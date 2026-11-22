"""A short, numbered name for every document a case builds (roadmap item 2.66), such as `bridge_1page_v2.4`.

A document's name is its case's short name, the document's name and the case's draft version:
`identifier(draft, document_name(case, md))`. Every page prints it through `stamp`. Both typesetters call this
module; it knows nothing of LaTeX or Quarto.

The case's log, `<case>/versions.toml`, holds two header keys and the drafts:

    short_name = "bridge"   # optional: lower case, one word or two joined by "-"
    design = 2                    # required: the case's design version (notes/case_pipeline.md 2.4.1)

    [[draft]]
    version = "v2.0"
    date = 2026-11-13
    inputs = "3f9a1c2e5b7d9a01"

Only the typesetter writes `[[draft]]` blocks. `inputs` is the hash of everything the build read (`draft`). The
newest block is pending while HEAD's copy of the log has no block of its version; every other block is committed
and is never rewritten. A changed build replaces a pending block, or adds one after a committed block, so a number
counts the drafts that enter version control. The next number is `v<design>.<m>`, `m` one more than the largest
minor of major `design` among the committed blocks and the tags `<case folder>/v<design>.*`, or 0. A build whose
hash equals a block's takes that block's version and date and writes nothing. With no `short_name` the case's
folder name is used, and a note says so.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import subprocess
import tempfile
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

# The one table of document names; a stem not in it is used as it stands.
SHORT_NAMES = {"executive_summary": "1page", "policy_paper": "paper", "technical_appendix": "appendix",
               "technical_note": "note"}
SEPARATOR = " | "
REPO = Path(__file__).resolve().parents[1]
SHORT_NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)?")
VERSION = re.compile(r"v(\d+)\.(\d+)")
HEADER_KEYS = ("short_name", "design")


class Refused(Exception):
    """A log the build cannot number by; its text is one line naming the file and the field."""


@dataclass(frozen=True)
class Draft:
    short: str
    version: str
    date: dt.date
    inputs: str
    pending: bool
    notes: tuple[str, ...]


def document_name(case: Path, md: Path) -> str:
    """The document's name: the table's name of its stem; under `documents/verse/` the stem less `_verse`, then
    `_verse`; under `documents/audience/<key>/`, then `_` and the profile's `short_name`, or `<key>`."""
    parts = md.relative_to(case / "documents").parts
    stem = md.stem.removesuffix("_verse") if parts[0] == "verse" else md.stem
    name = SHORT_NAMES.get(stem, stem)
    if parts[0] == "verse":
        return f"{name}_verse"
    if parts[0] == "audience" and len(parts) == 3:
        profile = REPO / "audiences" / f"{parts[1]}.toml"
        short: object = tomllib.loads(profile.read_text()).get("short_name", parts[1]) if profile.exists() else parts[1]
        if not isinstance(short, str):
            raise Refused(f"{profile}: short_name must be a string")
        return f"{name}_{short}"
    return name


def _label(path: Path, case: Path) -> str:
    for root in (case, REPO):
        if path.is_relative_to(root):
            return path.relative_to(root).as_posix()
    return str(path)


def _hash(case: Path, inputs: Sequence[Path], arguments: str) -> str:
    """Each input's files labelled by their paths, relative where they can be; the sorted lines
    `<label>\\0<SHA-256 of the bytes>\\n`, then `arguments`; the first 16 hex digits of their SHA-256."""
    lines: list[str] = []
    for item in (p.resolve() for p in inputs):
        for file in [item] if item.is_file() else (f for f in item.rglob("*") if f.is_file()):
            lines.append(f"{_label(file, case)}\0{hashlib.sha256(file.read_bytes()).hexdigest()}\n")
    return hashlib.sha256(("".join(sorted(lines)) + arguments).encode()).hexdigest()[:16]


def _git(case: Path, *args: str) -> str | None:
    run = subprocess.run(["git", *args], cwd=case, capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def _read(log: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """The log's header and blocks, or Refused naming the field that is wrong."""
    if not log.exists():
        raise Refused(f"{log}: missing; write the case's log with its design version (notes/case_pipeline.md 2.4.1)")
    try:
        data = tomllib.loads(log.read_text())
    except tomllib.TOMLDecodeError as error:
        raise Refused(f"{log}: not TOML: {' '.join(str(error).split())}") from None
    unknown = [key for key in data if key not in (*HEADER_KEYS, "draft")]
    if unknown:
        raise Refused(f"{log}: unknown key {', '.join(unknown)}; the header holds only short_name and design")
    design = data.get("design")
    if not isinstance(design, int) or isinstance(design, bool) or design < 0:
        raise Refused(f"{log}: no design: write the case's design version, notes/case_pipeline.md 2.4.1")
    short = data.get("short_name")
    if short is not None and not (isinstance(short, str) and SHORT_NAME.fullmatch(short)):
        raise Refused(f"{log}: short_name {short!r} is not lower case, one word or two joined by '-'")
    drafts = cast("list[dict[str, Any]]", data.get("draft", []))
    by_version: dict[str, dict[str, Any]] = {}
    by_inputs: dict[str, str] = {}
    for block in drafts:
        version, inputs = block.get("version"), block.get("inputs")
        if not (isinstance(version, str) and VERSION.fullmatch(version) and isinstance(inputs, str)
                and isinstance(block.get("date"), dt.date)):
            raise Refused(f"{log}: a [[draft]] block lacks a version vN.M, a date or inputs: {block!r}")
        if version in by_version:
            raise Refused(f"{log}: version {version} appears twice")
        if inputs in by_inputs:
            raise Refused(f"{log}: inputs {inputs} appears under both {by_inputs[inputs]} and {version}")
        by_version[version], by_inputs[inputs] = block, version
    return data, drafts


def _write(log: Path, text: str) -> None:
    """Write the log whole: to a temporary file beside it, then moved into place."""
    handle, temporary = tempfile.mkstemp(dir=log.parent, prefix=".versions-", suffix=".toml")
    with os.fdopen(handle, "w") as out:
        out.write(text)
    os.replace(temporary, log)


def draft(case: Path, inputs: Sequence[Path], arguments: str, today: dt.date | None = None) -> Draft:
    """The case's draft for a build of these inputs (files, or folders meaning every file under them) and these
    arguments: its short name, version, date and notes, the log updated as the module's docstring says."""
    case = case.resolve()
    log = case / "versions.toml"
    data, blocks = _read(log)
    design = cast(int, data["design"])
    notes: list[str] = []
    short = cast("str | None", data.get("short_name"))
    if short is None:
        short = case.name
        notes.append(f"{log}: no short_name, so the documents are named by the case folder, {short}")
    head = _git(case, "show", "HEAD:./versions.toml")
    head_blocks = cast("list[dict[str, Any]]", tomllib.loads(head).get("draft", []) if head else [])
    committed: set[str] = {str(b.get("version")) for b in head_blocks}
    digest = _hash(case, inputs, arguments)
    for block in blocks:
        if block["inputs"] == digest:
            return Draft(short, block["version"], block["date"], digest, block["version"] not in committed,
                         tuple(notes))
    tags = (_git(case, "tag", "-l", f"{case.name}/v{design}.*") or "").split()
    numbers = [*(b["version"] for b in blocks if b["version"] in committed), *(t.split("/")[-1] for t in tags)]
    minors = [int(m.group(2)) for v in numbers if (m := VERSION.fullmatch(v)) and int(m.group(1)) == design]
    version = f"v{design}.{max(minors) + 1 if minors else 0}"
    date = today or dt.datetime.now(dt.timezone.utc).date()
    text = log.read_text()
    if blocks and blocks[-1]["version"] not in committed:
        starts = [m.start() for m in re.finditer(r"^\[\[draft\]\]", text, re.M)]
        text = text[:starts[-1]]
        text = text[:-1] if text.endswith("\n\n") else text
    text = (text if text.endswith("\n") or not text else text + "\n") + \
        f'\n[[draft]]\nversion = "{version}"\ndate = {date.isoformat()}\ninputs = "{digest}"\n'
    _write(log, text)
    return Draft(short, version, date, digest, True, tuple(notes))


def identifier(draft: Draft, document: str) -> str:
    return f"{draft.short}_{document}_{draft.version}"


def stamp(identifier: str, date: dt.date, notice: str | None) -> str:
    """The line every page prints: the notice if given, the identifier and the date, as "13 November 2026"."""
    day = f"{date.day} {date.strftime('%B')} {date.year}"
    return SEPARATOR.join([*([notice] if notice else []), identifier, day])
