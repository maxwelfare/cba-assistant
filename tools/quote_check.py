"""Check every quote of a facts record against the stored text of its source (notes/briefs/facts_record.md).

Run from the repository root:

    .venv/bin/python -m tools.quote_check cases/<case>/baseline/<record>.md [more records] [--sources DIR]

DIR is the folder of stored sources, `DIR/<key>/text.txt`; by default the `sources/` folder of the record's case,
beside its `baseline/`.

WHAT IT READS. The record's `## Facts` section, from its first fact to the next `## ` heading. A fact runs from one
numbered label (`1.2.`, `1.2.3.`) or heading to the next. Every string in straight double quotes inside a fact, outside
a code span, is a quote. Its source key is the first key in backticks (lower case, digits and underscores, with one
underscore at least) after it in the same fact, else the last one before it; its line is the first `line N` or
`lines N-M` after it in the same fact. The brief's template puts each quote where these rules cannot misread it.

WHAT IT CHECKS. The quote and the stored text are each made plain by the project's normaliser
(`cost_benefit_engine.quotes.normalise`: NFKC, curly quotes and dashes made straight, white space collapsed), the text
line by line so that every character keeps its line, counted at each newline as `grep -n` counts; so, unlike
`quote_in`, a word broken by a hyphen at a line's end stays broken. A `|` counts as a space on both sides, so a table
row whose cells stand on separate lines is quoted as `cell | cell`. `...` or `[...]` in a quote marks words left out,
and the parts are found in order (the owner's ruling). A quote not in `text.txt` is looked for in the folder's
other `.txt` files, such as a `layout.txt` made by `pdftotext -layout` for a table. A quote passes when it is found and
one place where it is found meets the line or lines cited.

OUTPUT. One line for each quote that does not pass, with its line in the record, then the counts; exit 1 when any
quote does not pass, 2 when a record has no `## Facts` section. It writes nothing.

DOCUMENTS MODE. `.venv/bin/python -m tools.quote_check documents CASE` checks every quotation in `CASE/documents/*.md`,
CASE a case folder or the name of one under `cases/`. A quotation is text in double quotation marks, straight or curly,
outside a code span and before the document's `## References`, with a citation in its sentence, or in its row of a
Markdown table, that resolves to a key of `CASE/sources.toml`: a key in backticks, or `[N]` (or `[N, M]`) whose entry N
of the `## References` list holds the key in backticks, the key's `doi`, or begins with the key's `citation` (its first
60 characters). The first marker after the quotation decides: an owner's words identifier (`OW-YYYY-MM-DD-HHMM`) or a
parenthesis opening "(the owner" or "(the user" skips it as owner's or user's words, and a resolving citation checks
it; when none follows, the nearest resolving citation before it in the sentence or row does, and with none the
quotation (a term, a scare quote) is skipped with no citation. A sentence ends at `.`, `!` or `?` before white space
and a capital or an opening mark, except `e.g.` or `et al.` before a parenthesis, or at the paragraph's end; a straight
quotation mark after a backslash is part of the quotation, without the backslash. Each checked quotation is looked for
in every `.txt` file of `sources/<key>/`, `text.txt` first, with the shared checker's `plain_forms` and `quote_in_forms`;
it is not stored when that folder has no `.txt` file. One line for each, `<doc>:<line>: found|not found|not stored:
`key` "<quotation>"`, the line where it opens, then one tally line per document counting every quotation, the skipped
ones by reason; exit 1 when any is not found or not stored. It writes nothing.

INDEX AND SAMPLE MODES. A record is every `*.md` of a case's `baseline/` folder but `README.md`; a fact is a unit of
its `## Facts` section, read as above, that holds at least one quote. `.venv/bin/python -m tools.quote_check index
BASELINE` prints a Markdown table `Record | Question | Facts`, a row per record in file-name order with its first `# `
line and its count of facts; the facts step saves it as `baseline/README.md`. `.venv/bin/python -m tools.quote_check
sample BASELINE --n N --seed S [--sources DIR]` draws min(N, its facts) distinct facts from each record, uniformly
without replacement by a generator seeded with S, and prints them as one JSON array: record, fact label, row, the
fact's text, and each quote with its key, cited lines, the stored `.txt` file whose cited lines hold it (`text.txt`
when none does) and those lines as written, for an independent reader to judge each sentence against the lines it
quotes. `file` and `stored` are null with no key, no cited line or no stored text. Both write nothing.
"""

from __future__ import annotations

import argparse
import bisect
import json
import random
import re
import sys
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from cost_benefit_engine.quotes import forms, found_in, normalise

FACT_START = re.compile(r"#{3,6} |\d+(?:\.\d+)*\. ")
CODE_SPAN = re.compile(r"`[^`\n]*`")
QUOTE = re.compile(r'"([^"\n]+)"')
KEY = re.compile(r"`([a-z0-9]+(?:_[a-z0-9]+)+)`")
LINE = re.compile(r"\blines? (\d+)(?:\s*[–-]\s*(\d+))?")
OUTCOMES = ("pass", "not found", "wrong line", "no line", "no key", "not stored")


@dataclass
class Text:
    """A stored text made plain, with the offset and the line number at which each non-empty line starts."""

    flat: str
    starts: list[int]
    numbers: list[int]

    def line_at(self, offset: int) -> int:
        return self.numbers[bisect.bisect_right(self.starts, offset) - 1]


@dataclass
class Quote:
    row: int
    text: str
    key: str | None
    cited: tuple[int, int] | None


def load(path: Path) -> Text:
    pieces: list[str] = []
    starts: list[int] = []
    numbers: list[int] = []
    at = 0
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
        plain = normalise(line.replace("|", " "))
        if plain:
            pieces.append(plain)
            starts.append(at)
            numbers.append(number)
            at += len(plain) + 1
    return Text(" ".join(pieces), starts, numbers)


def spans(quote: str, text: Text) -> list[tuple[int, int]]:
    """The first and last line of each place where the quote's parts are found in order."""
    parts = [p.strip() for p in normalise(quote.replace("|", " ")).replace("[...]", "...").split("...")]
    parts = [p for p in parts if p]
    found: list[tuple[int, int]] = []
    start = text.flat.find(parts[0]) if parts else -1
    while start >= 0:
        end = start + len(parts[0])
        for part in parts[1:]:
            at = text.flat.find(part, end)
            if at < 0:
                return found
            end = at + len(part)
        found.append((text.line_at(start), text.line_at(end - 1)))
        start = text.flat.find(parts[0], start + 1)
    return found


def read_units(record: Path) -> list[tuple[int, str]]:
    """Each unit of the record's `## Facts` section: the row of its first line and its lines joined."""
    lines = record.read_text(encoding="utf-8").split("\n")
    first = next((i for i, line in enumerate(lines) if line.strip() == "## Facts"), None)
    if first is None:
        raise SystemExit(f"{record}: no '## Facts' section")
    end = next((i for i in range(first + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    facts: list[tuple[int, str]] = []
    for i in range(first + 1, end):
        if FACT_START.match(lines[i]):
            facts.append((i + 1, lines[i]))
        elif facts:
            facts[-1] = (facts[-1][0], facts[-1][1] + "\n" + lines[i])
    return facts


def unit_quotes(row: int, fact: str) -> list[Quote]:
    found: list[Quote] = []
    masked = CODE_SPAN.sub(lambda m: " " * len(m.group()), fact)
    for m in QUOTE.finditer(masked):
        after = KEY.search(fact, m.end())
        before = [k.group(1) for k in KEY.finditer(fact, 0, m.start())]
        key = after.group(1) if after else (before[-1] if before else None)
        line = LINE.search(fact, m.end())
        cited = (int(line.group(1)), int(line.group(2) or line.group(1))) if line else None
        found.append(Quote(row + fact.count("\n", 0, m.start()), m.group(1), key, cited))
    return found


def read_quotes(record: Path) -> list[Quote]:
    return [q for row, fact in read_units(record) for q in unit_quotes(row, fact)]


def check(quote: Quote, sources: Path, cache: dict[Path, Text]) -> tuple[str, str]:
    """The outcome, and where the quote was found when that is not where it was cited."""
    if quote.key is None:
        return "no key", ""
    folder = sources / quote.key
    files = sorted(folder.glob("*.txt"), key=lambda p: (p.name != "text.txt", p.name))
    if not files:
        return "not stored", ""
    seen = ""
    for path in files:
        if path not in cache:
            cache[path] = load(path)
        found = spans(quote.text, cache[path])
        if not found:
            continue
        if quote.cited and any(s <= quote.cited[1] and quote.cited[0] <= e for s, e in found):
            return "pass", ""
        seen = seen or f"found in {path.name} at " + ", ".join(f"{s}-{e}" if e != s else str(s) for s, e in found[:3])
    if not seen:
        return "not found", ""
    return ("wrong line" if quote.cited else "no line"), seen


DOC_QUOTE = re.compile(r'(?<!\\)"((?:[^"\\]|\\.)+)"|“([^“”]+)”')
SENTENCE_END = re.compile(r"(?:[!?]|\.(?!(?<=\be\.g\.)\s+\()(?!(?<=\bet al\.)\s+\())[\"”’)\]]*(?=\s+[A-Z“\"(\[]|\s*$)")
MARKER = re.compile(r"`([^`\n]+)`|\[(\d+(?:\s*,\s*\d+)*)\]|(OW-\d{4}-\d{2}-\d{2}-\d{4})|(\(the (?:owner|user)\b)")
REFERENCE = re.compile(r"(\d+)\.\s+(.*)")
SKIPPED = ("skipped as owner's or user's words", "skipped with no citation")


def resolve_entry(entry: str, sources: dict[str, dict[str, str]]) -> str | None:
    """The key a `## References` entry names: by a key in backticks, the key's doi, or its citation's opening."""
    for m in re.finditer(r"`([^`\n]+)`", entry):
        if m.group(1) in sources:
            return m.group(1)
    lowered = entry.lower()
    for key, fields in sources.items():
        doi = fields.get("doi", "").strip().lower()
        if doi and doi in lowered:
            return key
    plain = normalise(entry)
    for key, fields in sources.items():
        citation = normalise(fields.get("citation", ""))
        if citation and plain.startswith(citation[:60]):
            return key
    return None


def document_quotes(doc: Path, sources: dict[str, dict[str, str]]) -> tuple[list[tuple[int, str, str]], Counter[str]]:
    """Each checked quotation of a document (its line, the quotation as written, its source key), and the skips."""
    lines = doc.read_text(encoding="utf-8").split("\n")
    refs_at = next((i for i, line in enumerate(lines) if line.strip() == "## References"), len(lines))
    references: dict[int, str | None] = {}
    for line in lines[refs_at + 1:]:
        if line.startswith("## "):
            break
        m = REFERENCE.match(line)
        if m:
            references[int(m.group(1))] = resolve_entry(m.group(2), sources)
    paragraphs: list[tuple[int, str]] = []
    for i, line in enumerate(lines[:refs_at]):
        if not line.strip():
            continue
        if i > 0 and lines[i - 1].strip() and paragraphs:
            paragraphs[-1] = (paragraphs[-1][0], paragraphs[-1][1] + "\n" + line)
        else:
            paragraphs.append((i + 1, line))

    def cited(m: re.Match[str]) -> str | None:
        if m.group(1) is not None:
            return m.group(1) if m.group(1) in sources else None
        return next((k for n in m.group(2).split(",") if (k := references.get(int(n)))), None)

    found: list[tuple[int, str, str]] = []
    skipped: Counter[str] = Counter()
    for row, para in paragraphs:
        masked = CODE_SPAN.sub(lambda m: " " * len(m.group()), para)
        quotes = list(DOC_QUOTE.finditer(masked))
        blank = list(masked)
        for q in quotes:
            blank[q.start() + 1:q.end() - 1] = "x" * (q.end() - q.start() - 2)
        bare = "".join(blank)
        ends = list(SENTENCE_END.finditer(bare))
        for q in quotes:
            first = para.rfind("\n", 0, q.start()) + 1
            last = para.find("\n", q.end())
            last = len(para) if last < 0 else last
            if para[first:last].lstrip().startswith("|"):  # a table row is its own scope
                start, stop = first, last
            else:
                start = max((e.end() for e in ends if e.end() <= q.start()), default=0)
                stop = min((e.start() for e in ends if e.start() >= q.end()), default=len(para))
            key: str | None = None
            for m in MARKER.finditer(para, q.end(), stop):
                if m.group(3) or m.group(4):
                    key = "owner"
                    break
                if key := cited(m):
                    break
            if key is None:  # no marker after decides: the nearest citation before, in the sentence or row
                key = next((k for m in reversed(list(MARKER.finditer(para, start, q.start())))
                            if m.group(3) is None and m.group(4) is None and (k := cited(m))), None)
            if key == "owner":
                skipped[SKIPPED[0]] += 1
            elif key is None:
                skipped[SKIPPED[1]] += 1
            else:
                text = q.group(1).replace('\\"', '"') if q.group(1) is not None else q.group(2)
                found.append((row + para.count("\n", 0, q.start()), text, key))
    return found, skipped


def documents(case: Path) -> int:
    if not case.is_dir() and (Path("cases") / case).is_dir():
        case = Path("cases") / case
    sources = cast(dict[str, dict[str, str]], tomllib.loads((case / "sources.toml").read_text(encoding="utf-8")))
    cache: dict[Path, list[str]] = {}
    failed = False
    for doc in sorted((case / "documents").glob("*.md")):
        checked, counts = document_quotes(doc, sources)
        for row, text, key in checked:
            files = sorted((case / "sources" / key).glob("*.txt"), key=lambda p: (p.name != "text.txt", p.name))
            for path in files:
                if path not in cache:
                    cache[path] = forms(path.read_text(encoding="utf-8", errors="replace"))
            outcome = ("not stored" if not files else
                       "found" if any(found_in(text, cache[path]) for path in files) else "not found")
            counts[outcome] += 1
            failed = failed or outcome != "found"
            print(f'{doc}:{row}: {outcome}: `{key}` "{" ".join(text.split())}"')
        tally = ", ".join(f"{counts[o]} {o}" for o in ("found", "not found", "not stored", *SKIPPED) if counts[o])
        print(f"{doc}: {sum(counts.values())} quotations: {tally or 'none'}")
    return 1 if failed else 0


HEADING_NUMBER = re.compile(r"#{3,6} (\d+(?:\.\d+)*)\.?(?:\s|$)")


def records(baseline: Path) -> list[Path]:
    return sorted(p for p in baseline.glob("*.md") if p.name != "README.md")


def facts(record: Path) -> list[tuple[int, str, list[Quote]]]:
    """Each unit of the record that holds a quote: its row, its text without trailing blank lines, its quotes."""
    found: list[tuple[int, str, list[Quote]]] = []
    for row, unit in read_units(record):
        quotes = unit_quotes(row, unit)
        if quotes:
            lines = unit.split("\n")
            while lines and not lines[-1].strip():
                lines.pop()
            found.append((row, "\n".join(lines), quotes))
    return found


def index(baseline: Path) -> int:
    print("| Record | Question | Facts |\n|---|---|---|")
    for record in records(baseline):
        title = next((line[2:].strip() for line in record.read_text(encoding="utf-8").split("\n")
                      if line.startswith("# ")), "")
        print(f"| `{record.name}` | {title.replace('|', chr(92) + '|')} | {len(facts(record))} |")
    return 0


def label(text: str) -> str:
    first = text.split("\n", 1)[0]
    heading = HEADING_NUMBER.match(first)
    if heading:
        return heading.group(1)
    if first.startswith("#"):
        return first.lstrip("#").strip()
    return first.split(" ", 1)[0].rstrip(".")


def stored(quote: Quote, sources: Path, cache: dict[Path, Text]) -> tuple[str | None, str | None]:
    """The stored file whose cited lines hold the quote (else the first, text.txt), and those lines as written."""
    if quote.key is None or quote.cited is None:
        return None, None
    files = sorted((sources / quote.key).glob("*.txt"), key=lambda p: (p.name != "text.txt", p.name))
    if not files:
        return None, None
    first, last = quote.cited
    chosen = files[0]
    for path in files:
        if path not in cache:
            cache[path] = load(path)
        if any(s <= last and first <= e for s, e in spans(quote.text, cache[path])):
            chosen = path
            break
    lines = chosen.read_text(encoding="utf-8", errors="replace").split("\n")
    return chosen.name, "\n".join(lines[first - 1:last])


def sample(baseline: Path, n: int, seed: int, sources: Path) -> int:
    rng = random.Random(seed)
    cache: dict[Path, Text] = {}
    drawn: list[dict[str, object]] = []
    for record in records(baseline):
        units = facts(record)
        for i in sorted(rng.sample(range(len(units)), min(n, len(units)))):
            row, text, quotes = units[i]
            items: list[dict[str, object]] = []
            for q in quotes:
                name, lines = stored(q, sources, cache)
                items.append({"quote": q.text, "key": q.key, "lines": list(q.cited) if q.cited else None,
                              "file": name, "stored": lines})
            drawn.append({"record": record.name, "fact": label(text), "row": row, "text": text, "quotes": items})
    print(json.dumps(drawn, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    if sys.argv[1:2] == ["index"]:
        if len(sys.argv) != 3:
            raise SystemExit("usage: python -m tools.quote_check index BASELINE")
        return index(Path(sys.argv[2]))
    if sys.argv[1:2] == ["sample"]:
        drawer = argparse.ArgumentParser(prog="python -m tools.quote_check sample")
        drawer.add_argument("baseline", type=Path)
        drawer.add_argument("--n", type=int, required=True)
        drawer.add_argument("--seed", type=int, required=True)
        drawer.add_argument("--sources", type=Path, help="the folder of stored sources (default: BASELINE/../sources)")
        a = drawer.parse_args(sys.argv[2:])
        baseline: Path = a.baseline
        folder: Path | None = a.sources
        return sample(baseline, cast(int, a.n), cast(int, a.seed), folder or baseline.resolve().parent / "sources")
    if sys.argv[1:2] == ["documents"]:
        if len(sys.argv) != 3:
            raise SystemExit("usage: python -m tools.quote_check documents CASE")
        return documents(Path(sys.argv[2]))
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("records", nargs="+", type=Path)
    parser.add_argument("--sources", type=Path, help="the folder of stored sources (default: the case's sources/)")
    args = parser.parse_args()
    records: list[Path] = args.records
    given: Path | None = args.sources
    cache: dict[Path, Text] = {}
    failed = False
    for record in records:
        sources = given or record.resolve().parent.parent / "sources"
        counts: Counter[str] = Counter()
        for quote in read_quotes(record):
            outcome, where = check(quote, sources, cache)
            counts[outcome] += 1
            if outcome != "pass":
                cited = "-" if quote.cited is None else "-".join(dict.fromkeys(map(str, quote.cited)))
                print(f'{record}:{quote.row}: {outcome}: `{quote.key}` line {cited} {where}: "{quote.text[:90]}"')
        total = sum(counts.values())
        failed = failed or counts["pass"] < total
        tally = ", ".join(f"{counts[o]} {o}" for o in OUTCOMES if counts[o])
        print(f"{record}: {total} quotes: {tally or 'none found'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
