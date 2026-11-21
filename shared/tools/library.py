"""tools/library.py — the libraries of sources a seat searches before the web (CORE 2.2).

The owner, 2026-10-31 (an earlier session): "should we take the thing from perpetuity where we build an
archive of useful references and always search our own knowledge library before the web? You are searching something
that's been mentioned or referenced many times already"; and, choosing it: "Keep a shared index for anything like a
harness or process rule, and each project keeps its own refs."

THE LIBRARIES. The shared index, library/refs.toml in this folder, holds the literature behind harness and process
rules. Each project keeps its own: the files its .claude/library.json lists ({"files": [pattern, ...]}, relative to
the project's root), or by default research/refs.toml and every sources.toml below the root. An entry is a TOML table
with a `citation` (other fields as the file has them: link or url, quote, status, cited_in, licence), or a row of a
Markdown table, a line that starts with "|", so an index kept as a Markdown table is read as it stands.
A source stored in sources/<key>/ beside a TOML index (CORE 2.2) is named with its entry, and its text extracts,
the sources/<key>/*.txt beside any index searched, are searched too, keys without an entry included.

    .venv/bin/python -m tools.library search [--project DIR] WORDS...   print the entries that match

THE MATCH. A query's words are those of three letters or more, and every number, with common words dropped and
accents folded. An entry matches when it holds at least half the query's words, and at least two when the query has
two or more, so a one-word query matches what holds that word; a query with no such word is refused (exit 2). At most five entries are shown, those holding the most words first; a refusal, and
a search that matches nothing, are said on stderr. A line of a stored extract matches by the same rule, each query
word looked up in the folded text as a whole word rather than the text split into its word set, since a project's
extracts run to a gigabyte and splitting them took seconds a search; after the
entries, under a heading of its own, come the five keys with the best-matching lines, each with at most five of its
lines, stripped and cut to 300 characters around the first query word.

A seat runs it by CORE 2.2's instruction, never by a hook: a hook that showed the matches before every web search
or fetch was built and removed before it was applied (the owner, 2026-10-31: "I don't like adding hooks to every
action. why did you do that? Why not just use instructions? it's not a huge deal to repeat searches"; the shared
memory per-message-hooks-are-a-last-resort).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

SHARED = Path(__file__).resolve().parent.parent / "library" / "refs.toml"
DEFAULT_FILES = ["research/refs.toml", "**/sources.toml"]
SKIP = {".git", ".venv", "venv", "node_modules", "archive", "__pycache__", "scratch", "scratchpad"}
STOP = frozenset(
    "the and for with from that this what which into about over under than then also are was were has have had not "
    "but its their there these those his her our your you they them how why who when where does did can could would "
    "should may might will per via versus www http https html pdf org com".split())
WORD = re.compile(r"[a-z0-9]+")
SHOWN = 5
WIDTH = 300


@dataclass(frozen=True)
class Entry:
    where: str
    text: str
    words: frozenset[str]


def words(text: str) -> frozenset[str]:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return frozenset(w for w in WORD.findall(plain) if w not in STOP and (len(w) >= 3 or w.isdigit()))


def _need(q: frozenset[str]) -> int:
    """The number of query words an entry or a line must hold: half, and at least two, but never more than q has."""
    return min(len(q), max(2, math.ceil(len(q) / 2)))


def _fold(text: str) -> str:
    """The text lower-cased with accents folded, as `words` reads it; ASCII text skips the slow fold."""
    if text.isascii():
        return text.lower()
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def _whole(word: str, folded: str) -> bool:
    """Whether the folded text holds the word as a whole run of `WORD`, as `words` would split it out. A plain find
    with the boundaries checked by hand, since a regex with a lookbehind scans a large text many times slower."""
    at = folded.find(word)
    while at >= 0:
        end = at + len(word)
        if (at == 0 or not folded[at - 1].isalnum()) and (end == len(folded) or not folded[end].isalnum()):
            return True
        at = folded.find(word, at + 1)
    return False


def _held(q: frozenset[str], folded: str) -> int:
    """How many of the query words the folded text holds."""
    return sum(1 for w in q if _whole(w, folded))


def _make(where: str, text: str) -> Entry:
    return Entry(where, text, words(text))


def _toml_entries(path: Path, label: str) -> list[Entry]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    found: list[Entry] = []

    def walk(table: dict[str, Any], key: str) -> None:
        if isinstance(table.get("citation"), str):
            parts = [f"{key}: {table['citation']}"]
            parts += [f"{k}: {v}" for k, v in table.items() if k != "citation" and isinstance(v, (str, list))]
            stored = path.parent / "sources" / key.rsplit(".", 1)[-1]
            if stored.is_dir():
                parts.append(f"stored: {stored}")
            found.append(_make(f"{label} [{key}]", "; ".join(str(p) for p in parts)))
            return
        for k, v in table.items():
            if isinstance(v, dict):
                walk(cast(dict[str, Any], v), f"{key}.{k}" if key else k)

    walk(data, "")
    return found


def _markdown_entries(path: Path, label: str) -> list[Entry]:
    rows: list[Entry] = []
    for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        if line.startswith("|") and not re.fullmatch(r"[|\s:-]+", line):
            rows.append(_make(f"{label}:{n}", line.strip()))
    return rows


def _files(root: Path) -> list[Path]:
    config = root / ".claude" / "library.json"
    patterns: list[str] = DEFAULT_FILES
    if config.is_file():
        patterns = [str(p) for p in json.loads(config.read_text()).get("files", [])]
    out: list[Path] = []
    for pattern in patterns:
        if pattern.startswith("**/"):
            name = pattern[3:]
            for d, dirs, files in os.walk(root):
                dirs[:] = sorted(x for x in dirs if x not in SKIP)
                if name in files:
                    out.append(Path(d) / name)
        else:
            out += sorted(root.glob(pattern))
    return [p for p in dict.fromkeys(out) if p.is_file()]


def entries(project: Path | None, shared: Path | None = None) -> list[Entry]:
    """Every entry of the shared index and of the project's own files, the shared first."""
    found: list[Entry] = []
    for path, label in _index_paths(project, shared):
        try:
            found += _toml_entries(path, label) if path.suffix == ".toml" else _markdown_entries(path, label)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
            print(f"library: {path} skipped: {e}", file=sys.stderr)
    return found


def _index_paths(project: Path | None, shared: Path | None = None) -> list[tuple[Path, str]]:
    shared = shared or SHARED
    paths = [(shared, str(shared))] if shared.is_file() else []
    if project is not None:
        paths += [(p, str(p.relative_to(project))) for p in _files(project)]
    return paths


def _cut(line: str, q: frozenset[str], room: int) -> str:
    if len(line) <= room:
        return line
    low = line.lower()
    at = min((i for i in (low.find(w) for w in q) if i >= 0), default=0)
    start = max(0, min(at - room // 3, len(line) - room))
    return line[start:start + room]


def text_hits(query: str, project: Path | None, shared: Path | None = None) -> list[str]:
    """Lines of the stored text extracts beside every index searched, by key, the best-matching keys first."""
    q = words(query)
    need = _need(q)
    keys: list[tuple[int, int, list[str]]] = []
    seen: set[Path] = set()
    for path, label in _index_paths(project, shared):
        store = path.parent / "sources"
        if store in seen or not store.is_dir():
            continue
        seen.add(store)
        prefix = str(Path(label).parent / "sources")
        for key_dir in sorted(d for d in store.iterdir() if d.is_dir()):
            best, lines = 0, cast(list[str], [])
            for txt in sorted(key_dir.glob("*.txt")):
                try:
                    body = txt.read_text(errors="replace")
                except OSError as e:
                    print(f"library: {txt} skipped: {e}", file=sys.stderr)
                    continue
                if _held(q, _fold(body)) < need:
                    continue
                for n, raw in enumerate(body.splitlines(), 1):
                    hit = _held(q, _fold(raw))
                    if hit < need:
                        continue
                    best = max(best, hit)
                    if len(lines) < SHOWN:
                        head = f"{prefix}/{key_dir.name}/{txt.name}:{n}: "
                        lines.append(head + _cut(raw.strip(), q, WIDTH - len(head)))
            if lines:
                keys.append((best, len(keys), lines))
    return [ln for _, _, lines in sorted(keys, key=lambda x: (-x[0], x[1]))[:SHOWN] for ln in lines]


def search(query: str, found: list[Entry]) -> list[Entry]:
    q = words(query)
    need = _need(q)
    scored = [(len(q & e.words), i, e) for i, e in enumerate(found)]
    return [x[2] for x in sorted((x for x in scored if x[0] >= need), key=lambda x: (-x[0], x[1]))][:SHOWN]


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    find = sub.add_parser("search")
    find.add_argument("--project", type=Path, default=Path.cwd())
    find.add_argument("words", nargs="+")
    a = p.parse_args(argv)
    query = " ".join(cast(list[str], a.words))
    if not words(query):
        print("library: not searched: a query needs a word of three letters or more, or a number, besides common "
              "words; add an author, a year or a title word", file=sys.stderr)
        return 2
    project = cast(Path, a.project).resolve()
    hits = search(query, entries(project))
    for e in hits:
        print(f"{e.where}: {e.text}")
    texts = text_hits(query, project)
    if texts:
        print("-- in stored text extracts --")
        print("\n".join(texts))
    if not hits and not texts:
        print("library: no entry matches", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
