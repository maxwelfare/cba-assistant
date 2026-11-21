"""The record table and the source store (build plan item 10).

Record table: one JSON line per work in research/<case>/records.jsonl, holding the
work's bibliographic fields (a `bibliography.Record`), every `found_by`, every
decision about it and, when its full text could not be obtained, why. A row's id
is the id of the first Record that made it. The PRISMA 2020 counts (Page et al.
2021, BMJ 372:n71, flow diagram for new reviews) are derived from the rows and
the search log by `prisma`.

Source store: research/sources/<key>/ holds a source once for the whole project:
`original.<ext>` (the bytes as fetched), `source.json` (the record's fields, URL,
media type, SHA-256, licence, fetch time and, once text is stored, the method that
extracted it) and `text.txt`. `quote_found` checks a quote against the stored text.

Every write is a whole-file rewrite through a temporary file and a rename.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import tempfile
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from cost_benefit_engine.quotes import quote_in
from research.bibliography import Record, merge_into

SOURCES = Path(__file__).resolve().parent / "sources"
STAGES = ("screening", "eligibility")
DECISIONS = ("include", "exclude", "unsure")
CITATION_CHASING = ("references:", "citing:")
# The extension `original.<ext>` takes for each media type; an unlisted type is refused.
EXTENSIONS = {
    "application/pdf": "pdf",
    "application/xml": "xml",
    "text/xml": "xml",
    "text/html": "html",
    "text/plain": "txt",
}
_RECORD_FIELDS = tuple(f.name for f in dataclasses.fields(Record))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_atomic(path: Path, data: bytes) -> None:
    """Write `data` to a temporary file beside `path`, then rename it over `path`."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------- the record table


def _load(table: Path) -> list[dict[str, Any]]:
    if not table.exists():
        return []
    return [cast(dict[str, Any], json.loads(line)) for line in table.read_text(encoding="utf-8").splitlines() if line.strip()]


def _save(table: Path, rows: list[dict[str, Any]]) -> None:
    _write_atomic(table, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode())


def _record(row: dict[str, Any]) -> Record:
    """The row's Record. A field an older row lacks takes Record's default; one with no default is refused by Record."""
    fields: dict[str, Any] = {k: tuple(cast(list[str], row[k])) if isinstance(row[k], list) else row[k]
                              for k in _RECORD_FIELDS if k in row}
    return Record(**fields)


def _row(rows: list[dict[str, Any]], record_id: str) -> dict[str, Any]:
    for row in rows:
        if row["id"] == record_id:
            return row
    raise KeyError(f"no row with id {record_id!r}")


def add(table: Path | str, records: list[Record]) -> tuple[int, int]:
    """Add records, merging each into the row of the same work (bibliography.merge's rule); returns (new, merged)."""
    table = Path(table)
    rows = _load(table)
    works = [_record(r) for r in rows]
    new, merged = merge_into(works, records)
    for i, work in enumerate(works):
        fields = dataclasses.asdict(work)
        if i < len(rows):
            rows[i].update(fields)
        else:
            rows.append({**fields, "decisions": []})
    _save(table, rows)
    return new, merged


def decide(table: Path | str, record_id: str, stage: str, decision: str, reason: str, seat: str) -> None:
    """Append a decision with its reason, seat and UTC time; a row's status at a stage is its last decision there."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected one of {STAGES}")
    if decision not in DECISIONS:
        raise ValueError(f"unknown decision {decision!r}; expected one of {DECISIONS}")
    if not reason.strip():
        raise ValueError("every decision needs a reason")
    if not seat.strip():
        raise ValueError("every decision needs the seat that made it")
    table = Path(table)
    rows = _load(table)
    _row(rows, record_id)["decisions"].append(
        {"stage": stage, "decision": decision, "reason": reason, "seat": seat, "time": _now()}
    )
    _save(table, rows)


def mark_not_retrieved(table: Path | str, record_id: str, reason: str) -> None:
    """Record that the row's full text could not be obtained, and why."""
    if not reason.strip():
        raise ValueError("a report not retrieved needs a reason")
    table = Path(table)
    rows = _load(table)
    _row(rows, record_id)["not_retrieved"] = {"reason": reason, "time": _now()}
    _save(table, rows)


def _last(row: dict[str, Any], stage: str) -> dict[str, Any] | None:
    at_stage = [d for d in cast(list[dict[str, Any]], row["decisions"]) if d["stage"] == stage]
    return at_stage[-1] if at_stage else None


def prisma(table: Path | str, search_log: Path | str) -> dict[str, Any]:
    """The PRISMA 2020 flow counts for a new review, from the table's rows and the search log.

    Records identified per database are the records each search returned (not the database's
    hit count); citation-chased records are counted by their references:/citing: found_by and
    then deduplicated and screened with the rest. A last screening decision of "unsure" goes
    forward to retrieval.
    """
    rows = _load(Path(table))
    databases: Counter[str] = Counter()
    for line in Path(search_log).read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = cast(dict[str, Any], json.loads(line))
            databases[cast(str, entry["database"])] += int(entry["returned"])
    chased = sum(
        1 for row in rows for f in cast(list[str], row["found_by"]) if f.startswith(CITATION_CHASING)
    )
    screening = [d for d in (_last(r, "screening") for r in rows) if d is not None]
    eligibility = [d for d in (_last(r, "eligibility") for r in rows) if d is not None]
    return {
        "identified_databases": dict(databases),
        "identified_citation_chasing": chased,
        "duplicates_removed": sum(databases.values()) + chased - len(rows),
        "records_screened": len(screening),
        "records_excluded": sum(1 for d in screening if d["decision"] == "exclude"),
        "reports_sought": sum(1 for d in screening if d["decision"] in ("include", "unsure")),
        "reports_not_retrieved": sum(1 for r in rows if "not_retrieved" in r),
        "reports_assessed": len(eligibility),
        "reports_excluded": dict(Counter(cast(str, d["reason"]) for d in eligibility if d["decision"] == "exclude")),
        "included": sum(1 for d in eligibility if d["decision"] == "include"),
    }


# ---------------------------------------------------------------- the source store


def _key(record: Record) -> str:
    """One directory name per work: from the DOI (lower case), or the OpenAlex id when there is none."""
    if record.doi:
        return "doi-" + urllib.parse.quote(record.doi.strip().lower(), safe="")
    if record.database == "openalex":
        return "openalex-" + urllib.parse.quote(record.id.rstrip("/").rsplit("/", 1)[-1], safe="")
    raise ValueError(f"record {record.id!r} has neither a DOI nor an OpenAlex id to key the source store")


def _meta(folder: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((folder / "source.json").read_text(encoding="utf-8")))


def store(
    record: Record,
    content: bytes,
    url: str,
    media_type: str,
    licence: str | None,
    *,
    replace: bool = False,
    root: Path | str = SOURCES,
) -> str:
    """Store a fetched source once; returns its key. Different bytes under a stored key need replace=True."""
    ext = EXTENSIONS.get(media_type.split(";")[0].strip().lower())
    if ext is None:
        raise ValueError(f"no extension for media type {media_type!r}; known: {sorted(EXTENSIONS)}")
    key = _key(record)
    folder = Path(root) / key
    digest = hashlib.sha256(content).hexdigest()
    if (folder / "source.json").exists():
        stored = cast(str, _meta(folder)["sha256"])
        if stored == digest:
            return key
        if not replace:
            raise FileExistsError(
                f"source {key} is stored with SHA-256 {stored}; the new bytes have SHA-256 {digest}; "
                "pass replace=True to replace it"
            )
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / f"original.{ext}"
    _write_atomic(original, content)
    # On a replace, the old original and the text extracted from it go.
    for old in [*folder.glob("original.*"), folder / "text.txt"]:
        if old != original:
            old.unlink(missing_ok=True)
    meta = {
        **dataclasses.asdict(record),
        "url": url,
        "media_type": media_type,
        "sha256": digest,
        "licence": licence if licence is not None else "not stated",
        "fetched": _now(),
    }
    _write_atomic(folder / "source.json", json.dumps(meta, ensure_ascii=False, indent=2).encode())
    return key


def store_text(key: str, text: str, method: str, *, root: Path | str = SOURCES) -> None:
    """Store the text extracted from a stored original, verbatim, and the method that extracted it."""
    folder = Path(root) / key
    meta = _meta(folder)
    _write_atomic(folder / "text.txt", text.encode())
    _write_atomic(folder / "source.json", json.dumps({**meta, "text_method": method}, ensure_ascii=False,
                                                     indent=2).encode())


def quote_found(key: str, quote: str, *, root: Path | str = SOURCES) -> bool:
    """Whether the quote occurs in the stored text, by `quote_in` (parts either side of `...` in order); FileNotFoundError when no text is stored."""
    text = (Path(root) / key / "text.txt").read_bytes().decode()
    return quote_in(quote, text)
