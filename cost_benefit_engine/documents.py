"""Filling a case's document templates from its results, and formatting the numbers they print.

`fill_template` runs a template's placeholders in one fixed order: tables, citations, numbers, the reference list; then
anything left is refused. Each format prints a proper minus sign (U+2212) and no sign on a printed zero. Only `raw`, which
is `:g` by definition, can show an exponent. Every refusal is a `FillError` naming what it refused.

The rule for a number shown to a reader: it is rounded once, where it is shown, to two significant figures (Ehrenberg
1977), a trailing zero kept ("0.50", "$1.0 billion"), since the last shown digit states the precision (OMB Circular A-4,
"Precision of Estimates"). What is stored keeps every digit, and every derived number is worked from what is stored. A
caller exempts a number by the format it names, never by its value: `int` for a count, `year` for a year, `cited` and
`money_cited` for a value as its source states it. Where two values must read as different, `separating_figures` gives
the figures that tell them apart.

A case's record of review (roadmap 2.48) is `<case>/review/points.toml`, an array of tables `[[point]]`, one per point
of review, each column with one writer: `id` (the reviewer's number prefixed by the stage that raised it, as fast-E19 or
m1r2-A3) and `point` (the point in a few words), from the reviewer's report, with `raised_by`; `ruling` and `state`
("open" or "closed"), the editor's, the ruling saying who closed the point and on what; `answer` (opening with accepted,
revised, declined or for the user) and `where` (the files and sections the change is in), the author's; and, for a point
the editor rules a limit, `limit` (its text, part of the ruling) and `size` (the name of the fact in results/facts.json
that sizes it, the author's), with `size_format` ("money", the default, "percent" or "count") saying how the size
prints. A limit no editor has ruled (one the purpose check or the author finds) is an open row the author adds, with
`raised_by` "purpose check" or "author" and its `limit` and `size`, until the editor rules on it. An open row needs `id`,
`point`, `raised_by` and `state`; a closed row needs `ruling`, `answer` and `where` besides; `limit` and `size` come
together or not at all, and `size_format` only with them. `review_tables` prints from it the comment resolution matrix
(every row), the appendix's record of points not taken as asked (each row open, a limit, or whose answer does not open
with "accepted"), the appendix's and the paper's lists of limits, each limit with its size at the case's display figures
as `money`, `percent` or `significant` (for "count") prints it, and the one sentence of review status the appendix's
declaration carries; `check_document` refuses a built document that does not carry the record's current limits or status.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from dataclasses import dataclass
from numbers import Real
from pathlib import Path
from typing import Any, cast

from cost_benefit_engine.distributions import fields

MINUS = "−"
SCALES = ((12, "trillion"), (9, "billion"), (6, "million"), (3, "thousand"))
SUMMARY_HEAD = "| | mean | 5th percentile | median | 95th percentile |\n|---|---|---|---|---|"

Format = Callable[[Any], str]
Table = Callable[[Mapping[str, Any]], str]
Book = Mapping[str, Mapping[str, Any]]

_TABLE = re.compile(r"\{\{TABLE ([^{}]+)\}\}")
_CITATION = re.compile(r"\{\{(SRC|CITE) ([^{}]+)\}\}")
_NUMBER = re.compile(r"\{\{([^{}|]+)\|([^{}|]*)\}\}")
_LEFTOVER = re.compile(r"\{\{[^{}]*\}\}|\{\{|\}\}")


class FillError(Exception):
    """A template, or a value it asks for, that cannot be filled."""


def lookup(data: object, path: str, separator: str = ".") -> object:
    """The value at `path`: per step, a key of a mapping or a whole-number index of a list."""
    current = data
    for step in path.split(separator):
        if isinstance(current, Mapping) and step in current:
            current = cast(Mapping[str, object], current)[step]
        elif isinstance(current, list) and step.isdecimal() and int(step) < len(cast(list[object], current)):
            current = cast(list[object], current)[int(step)]
        else:
            raise FillError(f"{path}: cannot read step {step!r}")
    return current


# ---------------------------------------------------------------- formats


def _is_number(x: object) -> bool:
    return not isinstance(x, bool) and isinstance(x, Real) and math.isfinite(float(x))


def _number(x: object) -> float:
    if not _is_number(x):
        raise FillError(f"not a number: {x!r}")
    return float(cast(float, x))


def _with_sign(value: float, body: str, plus: bool = False) -> str:
    """`body`, which prints the magnitude of `value`, with its sign; a body with no non-zero digit is a printed zero."""
    if not re.search("[1-9]", body):
        return body
    return MINUS + body if value < 0 else "+" + body if plus else body


def _rounded(size: float, figures: int | None) -> Decimal:
    """`size` rounded to `figures` significant figures (the float's binary value, ties to even), or with `None` the value
    as stored, with every figure it carries."""
    if figures is None:
        return Decimal(repr(size)).normalize()
    return Decimal(f"{size:.{figures - 1}e}")


def _plain(size: Decimal) -> str:
    """Plain decimal notation with thousands separators, every figure `size` carries kept; a zero is "0"."""
    return "0" if size == 0 else f"{size:,f}"


def money(x: float, figures: int | None = 2, words_from: float = 1e6) -> str:
    """Dollars, rounded to `figures` first and then scaled by the largest word not above the rounded size, once that size
    is at least `words_from`. `figures=None` prints the value as stored."""
    value = _number(x)
    size = _rounded(abs(value), figures)
    for power, word in SCALES:
        if size >= max(words_from, 10**power):
            return _with_sign(value, f"${_plain(size.scaleb(-power))} {word}")
    return _with_sign(value, f"${_plain(size)}")


def significant(x: float, figures: int | None = 2) -> str:
    """A number to `figures` significant figures, or with `None` as stored."""
    value = _number(x)
    return _with_sign(value, _plain(_rounded(abs(value), figures)))


def percent(x: float, figures: int = 2) -> str:
    """A proportion as a percentage to `figures` significant figures: 0.1234 is 12%. A share below one that would round
    to 100 prints "more than 99%" (at two figures), and one above one that rounds to exactly 100 "more than 100%"."""
    value = _number(x)
    size = _rounded(abs(value) * 100, figures)
    if size == 100 and 0 < value < 1:
        return f"more than {_plain(100 - Decimal(1).scaleb(2 - figures))}%"
    if size == 100 and value > 1:
        return "more than 100%"
    return _with_sign(value, f"{_plain(size)}%")


def _per_cent(x: float, decimals: int) -> str:
    """A proportion as a percentage at fixed decimals, in "per cent": 0.1234 at one decimal is 12.3 per cent."""
    value = _number(x)
    return _with_sign(value, f"{abs(value) * 100:.{decimals}f} per cent")


def percentage_points(x: float, figures: int = 2, signed: bool = False) -> str:
    """A difference of proportions in points, to `figures` significant figures, 0.0012 being 0.12 points: its magnitude
    only, unless `signed`."""
    value = _number(x)
    body = f"{_plain(_rounded(abs(value) * 100, figures))} percentage points"
    return _with_sign(value, body, plus=True) if signed else body


def separating_figures(values: Sequence[float], show: Callable[[float, int], str] = significant) -> int:
    """The least count of figures, from 2 to 6, at which the distinct `values` print as distinct strings through `show`
    (`significant`, `money` or `percent`); 6 if none does."""
    distinct = set(values)
    for figures in range(2, 6):
        if len({show(v, figures) for v in distinct}) == len(distinct):
            return figures
    return 6


def signed(x: float, decimals: int = 2) -> str:
    value = _number(x)
    return _with_sign(value, f"{abs(value):.{decimals}f}", plus=True)


def _whole(x: float) -> str:
    value = _number(x)
    return _with_sign(value, f"{abs(value):,.0f}")


def _year(x: float) -> str:
    value = _number(x)
    if not value.is_integer():
        raise FillError(f"not a whole year: {x!r}")
    return _with_sign(value, f"{abs(value):.0f}")


def _raw(x: float) -> str:
    value = _number(x)
    return _with_sign(value, f"{abs(value):g}")


FORMATS: dict[str, Format] = {
    "money": money,
    "sig": significant,
    "pct": percent,
    "pp": percentage_points,
    "int": _whole,
    "year": _year,
    "cited": lambda x: significant(x, None),
    "money_cited": lambda x: money(x, None),
    "signed2": lambda x: signed(x, 2),
    "pct0": lambda x: _per_cent(x, 0),
    "pct1": lambda x: _per_cent(x, 1),
    "pct2": lambda x: _per_cent(x, 2),
    "raw": _raw,
}


# ---------------------------------------------------------------- templates and references


def _entry(book: str, key: str, sources: Book, methods: Book) -> Mapping[str, Any]:
    """The cited entry; `book` is "SRC", which reads `sources`, or "CITE", which reads `methods`."""
    entry = {"SRC": sources, "CITE": methods}.get(book, {}).get(key)
    if entry is None or "citation" not in entry:
        raise FillError(f"{{{{{book} {key}}}}}: no entry with a citation")
    return entry


def _anchor(n: int) -> str:
    """The identifier of reference-list entry `n`, which a citation of it links to."""
    return f"reference-{n}"


def _doi_link(doi: str) -> str:
    """`doi:<doi>` as a link to https://doi.org/<doi>. The characters a DOI may hold that would end a Markdown link's
    address or change its meaning ("10.1000/S0000-0000(00)00000-0", a SICI DOI's "<" and ">") are percent-encoded in
    the address; the label shows the DOI as it is."""
    address = "".join(f"%{ord(c):02X}" if c in "()<>[]\\ %#?" else c for c in doi)
    return f"[doi:{doi}](https://doi.org/{address})"


def reference_list(order: Sequence[tuple[str, str]], sources: Book, methods: Book) -> str:
    """One numbered line per `(book, key)` of `order`: the citation up to " Stored:", in a span carrying the entry's
    identifier (`_anchor`), then its DOI as a link, or its URL or link, which the typesetter makes a link as it does
    every bare web address. The span holds the citation, since the LaTeX route's markdown package reads no empty span."""
    lines: list[str] = []
    for n, (book, key) in enumerate(order, 1):
        entry = _entry(book, key, sources, methods)
        doi, address = entry.get("doi"), entry.get("url") or entry.get("link")
        where = f" {_doi_link(str(doi))}" if doi else f" {address}" if address else ""
        lines.append(f"{n}. [{str(entry['citation']).split(' Stored:')[0]}]{{#{_anchor(n)}}}{where}")
    return "\n".join(lines)


def fill_template(template: str, results: Mapping[str, Any], *, sources: Book, methods: Book, tables: Mapping[str, Table],
                  formats: Mapping[str, Format] = FORMATS, separator: str = ".") -> str:
    """The template filled. Tables go first, so a citation in a table is numbered where the table stands. A citation is
    its number in brackets, a link to its entry in the reference list, in Pandoc's Markdown, which both typesetting
    routes read: `[[2]](#reference-2)`, and the entry `[Its citation.]{#reference-2}`."""
    numbers: dict[tuple[str, str], int] = {}

    def table(match: re.Match[str]) -> str:
        name = match[1]
        if name not in tables:
            raise FillError(f"{match[0]}: no such table")
        return tables[name](results)

    def citation(match: re.Match[str]) -> str:
        _entry(match[1], match[2], sources, methods)
        n = numbers.setdefault((match[1], match[2]), len(numbers) + 1)
        return f"[[{n}]](#{_anchor(n)})"

    def number(match: re.Match[str]) -> str:
        if match[2] not in formats:
            raise FillError(f"{match[0]}: no format {match[2]!r}")
        try:
            return formats[match[2]](lookup(results, match[1], separator))
        except FillError as err:
            raise FillError(f"{match[0]}: {err}") from err

    text = _CITATION.sub(citation, _TABLE.sub(table, template))
    text = _NUMBER.sub(number, text).replace("{{REFERENCES}}", reference_list(list(numbers), sources, methods))
    left = _LEFTOVER.findall(text)
    if left:
        raise FillError(f"placeholders left unfilled: {left}")
    return text


# ---------------------------------------------------------------- tables, lists and headers


def _need(owner: str, entry: Mapping[str, Any], key: str) -> Any:
    if key not in entry:
        raise FillError(f"{owner}: no {key}")
    return entry[key]


def _money_note(entry: Mapping[str, Any]) -> str:
    return f" ({entry['currency']} {entry['price_year']})" if "currency" in entry else ""


def _parameters(name: str, spec: Mapping[str, Any], kind: str) -> str:
    if kind == "categorical":
        return ", ".join(f"{k} {_raw(v)}" for k, v in _need(name, spec, "outcomes").items())
    if kind == "mixture":
        return ", ".join(f"`{k}` {_raw(v)}" for k, v in _need(name, spec, "components").items())
    try:
        required, optional = fields(kind)
    except ValueError as err:
        raise FillError(f"{name}: {err}") from err
    return ", ".join(f"{k} {_raw(v)}" for k, v in spec.items() if k in required | optional and _is_number(v))


def _evidence(name: str, spec: Mapping[str, Any], cite: Callable[[str], str]) -> str:
    kind = str(_need(name, spec, "evidence_type"))
    keys = [spec["source"]] if "source" in spec else spec.get("sources")
    if keys:
        return f"{kind} " + " ".join(cite(str(k)) for k in keys)
    return f"{kind} {spec['judged_by']}" if "judged_by" in spec else kind


def _guided_cells(name: str, spec: Mapping[str, Any], guidance: Mapping[str, Any]) -> tuple[str, str]:
    """The distribution the loader draws for an official_guidance input, and its evidence cell. The entry's value is money
    only where the entry declares a currency; otherwise (a rate, say) it prints bare."""
    entry = cast(Mapping[str, Any], lookup(guidance, str(_need(name, spec, "guidance")).partition(".")[2]))
    show: Format = FORMATS["money_cited"] if "currency" in entry else _raw
    kind, words, keys = ("triangular", "low, central and high", ("low", "value", "high")) if "low" in entry or "high" in entry else (
        "constant", "central", ("value",))
    values = ", ".join(show(_need(name, entry, k)) for k in keys)
    return kind, f"official_guidance: {_need(name, entry, 'document')}; {words} {values}{_money_note(entry)}"


def input_table(inputs: Mapping[str, Mapping[str, Any]], *, guidance: Mapping[str, Any], cite: Callable[[str], str]) -> str:
    """A markdown table of a case's `inputs.toml` entries, one row each."""
    lines = ["| input | unit | distribution | parameters | evidence |", "|---|---|---|---|---|"]
    for name, spec in inputs.items():
        if spec.get("evidence_type") == "official_guidance":
            kind, evidence = _guided_cells(name, spec, guidance)
            parameters = ""
        else:
            kind = str(_need(name, spec, "distribution"))
            parameters, evidence = _parameters(name, spec, kind), _evidence(name, spec, cite)
        lines.append(f"| `{name}` | {_need(name, spec, 'unit')}{_money_note(spec)} | {kind} | {parameters} | {evidence} |")
    return "\n".join(lines)


def prcc_list(prcc: Mapping[str, float], at_least: float = 0.1) -> str:
    """A numbered list, in the order given, of the coefficients whose unrounded magnitude is at least `at_least`."""
    kept = [(name, value) for name, value in prcc.items() if abs(_number(value)) >= at_least]
    return "\n".join(f"{n}. `{name}`: {signed(value)}" for n, (name, value) in enumerate(kept, 1))


def results_header(res: Mapping[str, Any]) -> str:
    """One sentence saying how the results file was made."""
    state = " with uncommitted changes" if "uncommitted" in str(res.get("working_tree")) else ""
    parts = [f"Computed by `{_need('results', res, 'command')}` at commit {str(_need('results', res, 'commit'))[:10]}{state}",
             f"{_whole(_need('results', res, 'iterations'))} iterations", f"random seed {_need('results', res, 'random_seed')}"]
    for key, words in (("sampling_method", "sampling method"), ("price_base_year", "prices of"), ("discount_base_year", "discounted to")):
        if res.get(key) is not None:
            parts.append(f"{words} {res[key]}")
    return ", ".join(parts) + "."


def summary_row(name: str, s: Mapping[str, Any], fmt: Format = money) -> str:
    return f"| {name} | " + " | ".join(fmt(_need(name, s, k)) for k in ("mean", "p5", "p50", "p95")) + " |"


# ---------------------------------------------------------------- display settings (roadmap 2.78.4)


@dataclass(frozen=True)
class Display:
    """A case's display settings: the significant figures its documents show, and the unit and period its results are
    stated in. Only `significant_figures` is used by `formats_for` and `compare`; `unit` and `period` are read and
    validated to record the case's settings for the documents script and the referee, and the compare command checks
    figures only."""
    significant_figures: int
    unit: str
    period: str


_TOML_BLOCK = re.compile(r"^```toml[ \t]*\n(.*?)^```", re.M | re.S)


def read_display(case: Path) -> Display:
    """The case's one `[display]` table, in a fenced ```toml block of `<case>/requirements.md`, or of
    `<case>/design.md` when requirements.md holds none. Its keys: significant_figures (a whole number of at least 1),
    unit and period (text). Refused where neither file holds one, where a file holds two, or where a key is missing,
    of the wrong type or unknown."""
    for name in ("requirements.md", "design.md"):
        path = case / name
        if not path.is_file():
            continue
        tables = [doc["display"] for block in _TOML_BLOCK.findall(path.read_text())
                  if "display" in (doc := tomllib.loads(block))]
        if len(tables) > 1:
            raise FillError(f"{path}: {len(tables)} [display] tables; a case has one")
        if tables:
            table = cast(dict[str, object], tables[0])
            if set(table) != {"significant_figures", "unit", "period"}:
                raise FillError(f"{path}: [display] holds significant_figures, unit and period, not {sorted(table)}")
            figures, unit, period = table["significant_figures"], table["unit"], table["period"]
            if isinstance(figures, bool) or not isinstance(figures, int) or figures < 1:
                raise FillError(f"{path}: [display] significant_figures must be a whole number of at least 1")
            if not isinstance(unit, str) or not isinstance(period, str):
                raise FillError(f"{path}: [display] unit and period must be text")
            return Display(figures, unit, period)
    raise FillError(f"{case}: no [display] table in a ```toml block of requirements.md or design.md")


def formats_for(display: Display) -> dict[str, Format]:
    """The engine's formats, with `money` and `sig` at the display's significant figures."""
    n = display.significant_figures
    return {**FORMATS, "money": lambda x: money(x, n), "sig": lambda x: significant(x, n)}


# ---------------------------------------------------------------- comparing a rebuild with its previous build

# A number as a document prints it: an optional minus, an optional dollar sign, digits (thousands separated by commas),
# an optional decimal part, then an optional percentage or scale word. It does not start inside a word, a path or a
# dotted number, nor end before a letter, a slash or a further decimal part.
_PRINTED = re.compile(
    r"(?<![\w./$])(?P<sign>[−-])?(?P<dollar>\$)?(?P<digits>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?![\w/]|[.,]\d)"
    r"(?P<tail>%| per ?cent\b| percentage points?\b| (?:thousand|million|billion|trillion)\b)?")
_SCALE = {f" {word}": 10.0**power for power, word in SCALES}


def _stored(case: Path) -> list[float]:
    """Every finite numeric leaf of every JSON file under a folder named `results` inside `case`."""
    def leaves(o: object) -> list[float]:
        if isinstance(o, dict):
            return [x for v in cast(dict[str, object], o).values() for x in leaves(v)]
        if isinstance(o, list):
            return [x for v in cast(list[object], o) for x in leaves(v)]
        return [float(cast(float, o))] if _is_number(o) else []
    files = sorted({f for folder in case.rglob("results") if folder.is_dir() for f in folder.rglob("*.json")})
    return [x for f in files for x in leaves(json.loads(f.read_text()))]


def _figures(digits: str) -> tuple[int, int]:
    """The fewest and the most significant figures a printed number may carry: a decimal shows each of its figures; a
    whole number's trailing zeros may or may not be figures ("320" is two or three)."""
    plain = digits.replace(",", "")
    if "." in plain:
        shown = len(plain.replace(".", "").lstrip("0")) or 1
        return shown, shown
    whole = plain.lstrip("0") or "0"
    return len(whole.rstrip("0")) or 1, len(whole)


class _Number:
    """A checked number as a line prints it: its text, its value, and the fewest and most significant figures it
    may carry, and whether it is a percentage or printed with a sign."""

    def __init__(self, m: re.Match[str]) -> None:
        tail, digits = m["tail"] or "", m["digits"]
        self.shown = m[0]
        self.signed = bool(m["sign"])
        self.percent = tail not in _SCALE and bool(tail)
        self.value = float(digits.replace(",", "")) * _SCALE.get(tail, 1.0) * (-1 if self.signed else 1)
        self.fewest, self.most = _figures(digits)

    def reads(self, c: float) -> bool:
        """Whether the stored value `c` (for a percentage, also `c` times 100), rounded to some count of figures the
        number may show, reads as it; a number printed with no sign is matched by its magnitude, since prose may
        state a cost as an amount ("the costs take off $210 million")."""
        for x in (c, 100 * c) if self.percent else (c,):
            for f in range(self.fewest, self.most + 1):
                target = f"{self.value:.{f - 1}e}"
                if f"{x:.{f - 1}e}" == target or (not self.signed and f"{-x:.{f - 1}e}" == target):
                    return True
        return False


def _numbers(line: str) -> list[_Number]:
    """The checked numbers of `line`: each carrying "$", a percentage, a decimal point or a scale word; a bare whole
    number (a count, a year, a section number) is not checked."""
    return [_Number(m) for m in _PRINTED.finditer(line) if m["dollar"] or m["tail"] or "." in m["digits"]]


def compare(case: Path, previous: Path) -> int:
    """Compares each `*.md` of the folder `previous` (the accepted build) with the file of its name in
    `<case>/documents/` (the rebuild), and prints, for each line of the rebuild that differs, `<file>:<line>`, followed
    for each wrong number by the number as printed and why.

    A rebuild on the direct route moves no number, so each checked number of a changed line (`_numbers`) is paired
    with the number that stood in its place in the accepted text: the number at the same position among the checked
    numbers of the lines it replaced, where those carry as many; otherwise an accepted number printed the same that
    the change removed from elsewhere in the file (a moved line). It is right when one stored value of the case's
    `results` folders reads as both it and its pair, and it shows no more figures than the case's `[display]` table
    allows: a rounding of the same value passes, and a number of another value, even one stored elsewhere in the case,
    fails. A number with no pair is wrong, since the direct route adds none. Lines the rebuild drops are printed by
    the rebuild's line where they stood. Returns 1 when a number is wrong or a rebuilt file is missing, else 0."""
    figures = read_display(case).significant_figures
    stored = _stored(case)
    failed = False
    olds = sorted(previous.glob("*.md"))
    if not olds:
        raise FillError(f"{previous}: no *.md files to compare")
    for old_path in olds:
        new_path = case / "documents" / old_path.name
        if not new_path.is_file():
            print(f"{old_path.name}: no rebuilt file at {new_path}")
            failed = True
            continue
        old, new = old_path.read_text().splitlines(), new_path.read_text().splitlines()
        pairs: dict[int, list[tuple[_Number, _Number | None]]] = {}
        loose_new: list[tuple[int, _Number]] = []
        loose_old: list[_Number] = []
        opcodes = [op for op in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes() if op[0] != "equal"]
        for _, i1, i2, j1, j2 in opcodes:
            was = [n for i in range(i1, i2) for n in _numbers(old[i])]
            now = [(j, n) for j in range(j1, j2) for n in _numbers(new[j])]
            if len(was) == len(now):
                for (j, n), o in zip(now, was):
                    pairs.setdefault(j, []).append((n, o))
            else:
                loose_new += now
                loose_old += was
        for j, n in loose_new:
            o = next((o for o in loose_old if o.shown == n.shown), None)
            if o is not None:
                loose_old.remove(o)
            pairs.setdefault(j, []).append((n, o))
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "delete":
                print(f"{old_path.name}:{j1 + 1} previous lines {i1 + 1} to {i2} removed")
            for j in range(j1, j2):
                wrong: list[tuple[str, str]] = []
                for n, o in pairs.get(j, []):
                    if n.fewest > figures:
                        wrong.append((n.shown, f"shows {n.fewest} significant figures; the display table allows {figures}"))
                    elif o is None:
                        wrong.append((n.shown, "no number stood in its place in the previous build"))
                    elif not any(n.reads(c) and o.reads(c) for c in stored):
                        wrong.append((n.shown, f"no stored value reads as both it and the previous build's {o.shown}"))
                print(f"{old_path.name}:{j + 1}" + "".join(f"\n    wrong number {shown}: {why}" for shown, why in wrong))
                failed = failed or bool(wrong)
    return 1 if failed else 0


# ---------------------------------------------------------------- the technical appendix's annexes (roadmap 2.36)

_MARKDOWN_SPECIAL = re.compile(r"([\\`*_\[\]<>|$#~^{}])")


def _md(text: object) -> str:
    """Text set literally in Markdown: every character Markdown or the layout's maths would read is escaped."""
    return _MARKDOWN_SPECIAL.sub(r"\\\1", " ".join(str(text).split()))


def _totals(results: Path) -> dict[str, Any]:
    """The total tool's results file, `<folder>/results/estimate_total.json`, refused where it is missing."""
    path = results / "results" / "estimate_total.json"
    if not path.is_file():
        raise FillError(f"{path}: no results of the total tool; run tools/estimate_total.py on the table first")
    return cast(dict[str, Any], json.loads(path.read_text()))


def annex_a(table: Path, figures: int = 2) -> str:
    """Annex A: every `[[effect]]` row of a table of estimates (notes/fast_estimate.md section 3) and every factor of
    it, as one Markdown table. A row's first line holds its name, kind, option, who bears it and, where stated, its own
    low, middle and high; each factor follows on a line of its own with its unit, low, middle, high, form, the mean of
    its draws and source, a factor named by a row and stated once in `[factors]` read from that entry, its form and mean
    from the total tool's `factors` in `results/estimate_total.json` beside the table (refused where it lacks the
    factor). A factor naming a distribution shows, from the same file, its family and each parameter in the form column
    and, as its low, middle and high, the 5th, 50th and 95th percentiles the total tool computed, labelled computed.
    Numbers are printed by `significant` at `figures`."""
    doc = tomllib.loads(table.read_text())
    entries = cast(dict[str, dict[str, Any]], doc.get("factors", {}))
    rows = cast(list[dict[str, Any]], doc.get("effect", []))
    drawn = cast(dict[str, dict[str, Any]], _totals(table.parent).get("factors", {}))

    def ends(d: Mapping[str, Any]) -> str:
        return " | ".join(significant(_number(d[k]), figures) if k in d else "" for k in ("low", "middle", "high"))

    lines = ["# Annex A. Every effect and factor", "",
             f"Each effect of the table of estimates (`{_md(table.name)}`, {len(rows)} rows), then each of its factors: "
             f"low, middle and high are the 5th, 50th and 95th percentiles, and the mean is the mean of the total tool's"
             f" draws, to {figures} significant figures.", "",
             "| Effect or factor | Unit | Low | Middle | High | Form | Mean | Source |", "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        about = "; ".join(_md(x) for x in (row.get("kind"), row.get("option") and f"option {row['option']}",
                                            row.get("who"), "weight " + significant(_number(row["weight"]), figures)
                                            if "weight" in row else None,
                                            row.get("model") and f"model output {row['model']}") if x)
        lines.append(f"| **{_md(row['name'])}** ({about}) | | {ends(row)} | | | |")
        for factor in cast(list[dict[str, Any]], row.get("factor", [])):
            f = {**entries.get(factor["name"], {}), **factor}
            if f["name"] not in drawn:
                raise FillError(f"factor {f['name']!r}: not in the total tool's results beside {table.name}; rerun it")
            d = drawn[f["name"]]
            source = f"one minus {f['complement_of']}" if "complement_of" in f else f.get("source", "")
            form, shown = str(d["form"]), f
            if "parameters" in d:  # a named distribution: its family and parameters, its percentiles computed
                given = ", ".join(f"{k} = {v}" for k, v in cast(dict[str, Any], d["parameters"]).items())
                form, shown = f"{f['distribution']} ({given}); low, middle and high computed", d
            lines.append(f"| {_md(f['name'])} | {_md(f.get('unit', ''))} | {ends(shown)} | {_md(form)} |"
                         f" {significant(_number(d['mean']), figures)} | {_md(source)} |")
    return "\n".join(lines) + "\n"


def method_annex(case: Path) -> str:
    """The method of the total tool as its run states it, the `method` of `<case>/results/estimate_total.json`: the run's
    draws, seed and sampling, each form, how means, shares of variance, dependence and sets are computed, and, where the
    run states them, its groups and weights, elasticity, leading total, discounting, public outlay and prices."""
    m = cast(dict[str, Any], _totals(case)["method"])
    forms = cast(dict[str, str], m["forms"])
    return "\n".join([
        f"The totals are computed by the total tool (`tools/estimate_total.py`) from {int(m['draws']):,} draws at seed"
        f" {int(m['seed'])}, sampling {_md(m['sampling'])}. Each factor's judged low, middle and high become a"
        " distribution by its form, or the factor names a distribution with its own parameters:", "",
        *(f"- **{_md(name)}.** {_md(text)}" for name, text in forms.items()), "",
        f"**Means.** {_md(m['mean'])}", "",
        f"**Shares of variance.** {_md(m['variance_share'])}", "",
        f"**Dependence.** {_md(m['dependence'])}", "",
        f"**Sets and the base.** {_md(m['sets'])}",
        *(f"\n**{title}.** {_md(m[key])}" for key, title in (
            ("groups", "Groups and weights"), ("elasticity", "Income elasticity"), ("lead", "The leading total"),
            ("discount", "Discounting"), ("outlay", "Public outlay and excess burden"), ("price_year", "Prices"))
          if key in m)]) + "\n"


def method_tables(case: Path) -> dict[str, Table]:
    """The tables `fill_template` prints for the appendix's method (author_upgrade.md, message A, 2), by name:
    `method_annex`, the total tool's method as the case's run states it."""
    return {"method_annex": lambda facts: method_annex(case)}


def annex_b(case: Path) -> str:
    """Annex B: the requirements and the list of review reports. The requirements are `<case>/requirements.md` from its
    first `##` heading on, each heading one level lower; the review is each report in `<case>/review/`, by file name,
    with its first heading."""
    text = (case / "requirements.md").read_text()
    start = re.search(r"^## ", text, re.M)
    if start is None:
        raise FillError(f"{case / 'requirements.md'}: no ## section")
    body = text[start.start():]
    body = re.sub(r"^```toml[ \t]*\n\s*\[display\][ \t]*\n.*?^```[ \t]*\n?", "", body, flags=re.M | re.S)
    body = re.sub(r"^(#{2,5}) ", r"#\1 ", body, flags=re.M)
    reports: list[str] = []
    for path in sorted(p for p in (case / "review").iterdir() if p.is_file()):
        title = re.search(r"^#+ (.+)$", path.read_text(errors="replace"), re.M) if path.suffix == ".md" else None
        reports.append(f"- `{path.name}`" + (f": {_md(title[1])}" if title else ""))
    return "\n".join(["# Annex B. The requirements and the review reports", "",
                      "## B.1 The requirements", "", "As confirmed in the case's `requirements.md`.", "",
                      body.strip("\n"), "", "## B.2 The review", "",
                      "Each report of the case's review, in its folder `review/`, by file name and title.", "",
                      *reports]) + "\n"


# ---------------------------------------------------------------- the record of review points (roadmap 2.48)

_OPEN_NEEDS = ("id", "point", "raised_by", "state")
_CLOSED_NEEDS = (*_OPEN_NEEDS, "ruling", "answer", "where")
_COLUMNS = frozenset((*_CLOSED_NEEDS, "limit", "size", "size_format"))
_SIZE_FORMATS = {"money": money, "percent": percent, "count": significant}


def read_points(case: Path) -> list[dict[str, str]]:
    """The rows of `<case>/review/points.toml` (the module's header defines it), each checked: a row missing a column
    its state needs, holding a column not defined, with `limit` and `size` apart, or with a `size_format` not defined or
    without a size is refused naming its id, as is an id used twice; a file with anything but `[[point]]` rows is
    refused."""
    path = case / "review" / "points.toml"
    if not path.is_file():
        raise FillError(f"{path}: no record of review")
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = doc.get("point", [])
    if set(doc) - {"point"} or not isinstance(rows, list) or not all(isinstance(r, dict) for r in cast(list[object], rows)):
        raise FillError(f"{path}: the record is an array of [[point]] tables and nothing else")
    rows = cast(list[dict[str, object]], rows)
    seen: set[str] = set()
    for n, row in enumerate(rows, 1):
        name = str(row.get("id", f"row {n}"))
        if row.get("state") not in ("open", "closed"):
            raise FillError(f"{path}: {name}: state must be \"open\" or \"closed\"")
        missing = [k for k in (_CLOSED_NEEDS if row["state"] == "closed" else _OPEN_NEEDS)
                   if not isinstance(row.get(k), str) or not str(row[k]).strip()]
        if missing:
            raise FillError(f"{path}: {name} ({row['state']}): no {', '.join(missing)}")
        unknown = sorted(set(row) - _COLUMNS)
        if unknown:
            raise FillError(f"{path}: {name}: columns not in the record: {unknown}")
        if not all(isinstance(v, str) for v in row.values()):
            raise FillError(f"{path}: {name}: every column is text")
        if ("limit" in row) != ("size" in row):
            raise FillError(f"{path}: {name}: a limit needs its size, and a size its limit")
        if "size_format" in row and (row["size_format"] not in _SIZE_FORMATS or "size" not in row):
            raise FillError(f"{path}: {name}: size_format is one of {sorted(_SIZE_FORMATS)}, beside a size")
        if name in seen:
            raise FillError(f"{path}: {name}: the id is used twice")
        seen.add(name)
    return cast(list[dict[str, str]], rows)


def _sizer(case: Path, rows: Sequence[Mapping[str, str]]) -> Callable[[Mapping[str, str], Mapping[str, Any]], str]:
    """Prints a limit row's size: its fact's value in the row's `size_format` at the case's display figures."""
    figures = read_display(case).significant_figures if any("limit" in r for r in rows) else 2

    def size(row: Mapping[str, str], facts: Mapping[str, Any]) -> str:
        fact = facts.get(row["size"])
        if not isinstance(fact, Mapping) or "value" not in fact:
            raise FillError(f"{row['id']}: size {row['size']!r} names no fact in results/facts.json")
        show = _SIZE_FORMATS[row.get("size_format", "money")]
        return _md(show(cast(Mapping[str, Any], fact)["value"], figures))
    return size


def _limit_lines(rows: Sequence[Mapping[str, str]], facts: Mapping[str, Any], size: Callable[..., str],
                 kind: str) -> list[tuple[str, str]]:
    """Each limit row's id and the line the appendix's (`kind` "appendix") or the paper's list prints for it."""
    limits = [r for r in rows if "limit" in r]
    if kind == "appendix":
        return [(r["id"], f"{n}. {_md(r['limit']).rstrip('.')}. Its size: {size(r, facts)} (review point {_md(r['id'])}).")
                for n, r in enumerate(limits, 1)]
    return [(r["id"], f"- {_md(r['limit']).rstrip('.')}. Its size: {size(r, facts)}.") for r in limits]


def _status(rows: Sequence[Mapping[str, str]]) -> str:
    def count(n: int, word: str) -> str:
        return f"{n} {word}" if n == 1 else f"{n} {word}s"
    closed = sum(r["state"] == "closed" for r in rows)
    return (f"The case's record of review holds {count(len(rows), 'point')}, {closed} closed and {len(rows) - closed} "
            f"open, {count(sum('limit' in r for r in rows), 'stated limit')} among them.")


def review_tables(case: Path) -> dict[str, Table]:
    """The tables `fill_template` prints from the case's record of review, by name: `review_matrix`, `review_record`,
    `limits_appendix`, `limits_paper` and `review_status` (the module's header says what each holds)."""
    rows = read_points(case)
    size = _sizer(case, rows)

    def table(kept: Sequence[Mapping[str, str]]) -> Table:
        def print_(facts: Mapping[str, Any]) -> str:
            lines = ["| Point | Raised by | The point | The editor's ruling | Answer | Where | Status | Limit, with its size |",
                     "|---|---|---|---|---|---|---|---|"]
            for r in kept:
                limit = f"{_md(r['limit'])}: {size(r, facts)}" if "limit" in r else ""
                cells = [_md(r.get(k, "")) for k in ("id", "raised_by", "point", "ruling", "answer", "where", "state")]
                lines.append("| " + " | ".join([*cells, limit]) + " |")
            return "\n".join(lines)
        return print_

    not_as_asked = [r for r in rows if r["state"] == "open" or "limit" in r
                    or not r["answer"].strip().lower().startswith("accepted")]
    return {
        "review_matrix": table(rows),
        "review_record": table(not_as_asked),
        "limits_appendix": lambda facts: "\n".join(line for _, line in _limit_lines(rows, facts, size, "appendix")),
        "limits_paper": lambda facts: "\n".join(line for _, line in _limit_lines(rows, facts, size, "paper")),
        "review_status": lambda facts: _status(rows),
        "requirements_record": lambda facts: requirements_record(case),
    }


def _requirements_text(case: Path) -> str:
    path = case / "requirements.md"
    if not path.is_file():
        raise FillError(f"{path}: no requirements file")
    return path.read_text(encoding="utf-8")


def _requirements_start(text: str) -> int | None:
    """Where the requirements of a requirements.md in scope-case's form (its SKILL.md 6.1) start: at a `## The
    requirements` heading where the file has one, else at its first line `<n>. ` outside a quotation, so that a numbered
    line inside the user's verbatim request, which comes before the requirements, is not taken for one. A line is
    inside a quotation when the double quotes before it, straight or curly, leave one open."""
    heading = re.search(r"^## The requirements[ \t]*$", text, re.M)
    if heading is not None:
        return heading.start()
    at, open_ = 0, False
    for line in text.splitlines(keepends=True):
        if not open_ and re.match(r"\d+\. ", line):
            return at
        straight = line.count('"')
        curly_open, curly_close = line.count("\u201c"), line.count("\u201d")
        if straight % 2:
            open_ = not open_
        if curly_open != curly_close:
            open_ = curly_open > curly_close
        at += len(line)
    return None


def requirements_record(case: Path) -> str:
    """The appendix's table of requirements (author_upgrade.md, message A, 2.1.2): each numbered requirement of
    `<case>/requirements.md` in scope-case's form (its SKILL.md 6.1), and the headings of the sections of
    `<case>/design.md` whose `Serves:` line names it, or "none" (every one where the case has no design.md). The
    requirements start where `_requirements_start` says; a requirement is a line `<n>. ` and the lines that follow it
    with no blank, heading, fence or sub-item (`<n>.<m> `) between, joined into one row. A section headed `## Open` holds
    no requirement and is not printed. A case with no requirements.md is refused."""
    path = case / "requirements.md"
    text = _requirements_text(case)
    start = _requirements_start(text)
    if start is None:
        raise FillError(f"{path}: no numbered requirement")
    serving: dict[str, list[str]] = {}
    design = case / "design.md"
    heading = ""
    for line in design.read_text(encoding="utf-8").splitlines() if design.is_file() else []:
        if found := re.match(r"#+ (.+)", line):
            heading = found[1].strip()
        elif found := re.match(r"Serves:(.*)", line):
            for n in (x.strip() for x in found[1].split(",")):
                serving.setdefault(n, []).append(heading)
    requirements: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    in_open = False
    for line in text[start:].splitlines():
        if line.startswith("## "):
            in_open = re.match(r"## Open\b", line) is not None
            current = None
        elif in_open:
            continue
        elif found := re.match(r"(\d+)\. (.+)$", line):
            current = [found[2].strip()]
            requirements.append((found[1], current))
        elif (current is not None and line.strip() and not line.startswith(("#", "```"))
              and not re.match(r"\d+\.\d", line)):
            current.append(line.strip())
        else:
            current = None
    lines = ["| Requirement | Sections of the design that serve it |", "|---|---|"]
    for n, words in requirements:
        lines.append(f"| {n}. {_md(' '.join(words))} | {'; '.join(_md(h) for h in serving.get(n, [])) or 'none'} |")
    return "\n".join(lines)



# ---------------------------------------------------------------- the appendix's section on the process (roadmap 2.48 C)

PROCESS_DESCRIPTION = (
    "The assistant that produced this analysis is a set of AI agents directed by one coordinating session. The "
    "coordinator gives each step to a separate agent, called a seat, with written instructions for that step, and "
    "keeps every file of the work under version control. The steps run in a fixed order, and a case stops after the "
    "step its level of rigor reaches.\n\n"
    "A requirements conversation with the user first settles the question, the options and the base case, whose gains "
    "and losses count, and the level of rigor; each requirement is read back to the user and kept only once they "
    "confirm it. The coordinating session then has agents that each list effects from one angle, without seeing "
    "one another's lists, and agents that estimate each effect as the product of a few uncertain factors, each with a "
    "low, a middle and a high value and a source or the word judgement, and it pools their lists. An author checks "
    "the pool and the estimates and fills the gaps. A tool draws every factor "
    "many times and adds the effects into a distribution of net benefits. Three reviewers, each blind to the others, "
    "read this fast draft: an economist; an auditor, who traces every number to its source and redoes the arithmetic; "
    "and a reader of the documents for faithfulness and plain language. An editor turns their reports into one "
    "decision letter, which names the effects worth a small model of their own.\n\n"
    "The same author then builds those models. Before it does, each choice of method that could move the result goes "
    "to a referee of its own, and before any document is written a referee reads the results and an outline against "
    "the tool's standing rules of method and the user's requirements. The author writes this appendix with every result "
    "left as an empty placeholder, and milestone 1, the method and this appendix, has its own round of review: the "
    "economist and the auditor read the appendix for its method before any result is written about, and an editor "
    "rules and checks the fixes. The run of record is then made from the accepted commit, its results fill the "
    "placeholders, and the author writes the paragraphs that describe them, a policy paper and a one-page summary. "
    "In the round of milestone 2, the results and the documents, a referee of the documents reruns the case from "
    "that commit, checks that the method that ran is the one accepted and that the results paragraphs, the paper and "
    "the summary say what the results say, and an editor rules and checks the fixes. Every point of review, with the "
    "author's answer and the editor's ruling, is kept in one "
    "record, from which this appendix prints its tables of review. A layout review reads the built documents before "
    "they go to the user. Where the user asks, the process also makes peer review packages for human peer reviewers and editions "
    "written for a named reader. The stages that ran for this case, with the agent type in each seat and the AI models "
    "that answered, are listed below, read from the session records of the run; a run is placed in a stage by the "
    "instructions it was given, and a run of one of the process's agent types that could not be placed is named after "
    "the table."
)
# The cut is the build's own judgement of the owner's "printed where short" (author_upgrade.md 2.1.4), with no source; a request longer than this is named by its path.
SHORT_REQUEST_WORDS = 400


def _stage_key(stage: str) -> tuple[int, ...]:
    return tuple(int(x) for x in stage.split("."))


def seats_table(case: Path) -> str:
    """The table of stages, seats and models of `<case>/results/seats.json` (tools/seats_record.py), in
    the order of notes/fast_estimate.md 1.3 whatever the record's order, each model as the transcript names it; then
    each run the record assigned to no stage whose agent type a stage dispatches (`stages_naming_seat`), with its models
    and its task's description, and one sentence counting the other runs it assigned to no stage."""
    path = case / "results" / "seats.json"
    if not path.is_file():
        raise FillError(f"{path}: no seats record; tools/seats_record.py writes it")
    record = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    stages = sorted(cast(list[dict[str, Any]], record.get("stages", [])), key=lambda st: _stage_key(str(st["stage"])))
    lines = ["| Stage | Seat (agent type) | Models |", "|---|---|---|"]
    for st in stages:
        for k, seat in enumerate(cast(list[dict[str, Any]], st["seats"])):
            stage = _md(st["stage"]) if k == 0 else ""
            models = ", ".join(_md(m) for m in cast(list[str], seat["models"]))
            lines.append(f"| {stage} | {_md(seat['seat'])} | {models} |")
    unplaced = cast(list[dict[str, Any]], record.get("unassigned", []))
    seated = [u for u in unplaced if u.get("stages_naming_seat")]
    if seated:
        lines += ["", "Runs of the process's agent types that the record places in no stage:", ""]
        lines += [f"- {_md(u['seat'])} ({', '.join(_md(m) for m in cast(list[str], u['models']))}): "
                  f"\u201c{_md(u['description'])}\u201d" for u in seated]
    others = len(unplaced) - len(seated)
    if others:
        lines += ["", f"A further {others} {'run' if others == 1 else 'runs'} of the case's sessions, of agent types "
                  f"no stage dispatches, {'is' if others == 1 else 'are'} assigned to no stage of the process; the record, "
                  "`results/seats.json`, names each with its agent type, models and task."]
    return "\n".join(lines)


def user_messages(case: Path) -> str:
    """The user's messages, verbatim, from `<case>/requirements.md` in scope-case's form: the text from its first line
    that says "verbatim" (a heading's section, or the request's paragraph and those after it) to the next `##` heading
    or the first requirement, set as a block quote where it holds at most SHORT_REQUEST_WORDS words, else named by the
    file's path and its length."""
    path = case / "requirements.md"
    text = _requirements_text(case)
    found = re.search(r"^.*\bverbatim\b.*$", text, re.M | re.I)
    if found is None:
        raise FillError(f"{path}: no line saying where the user's messages are given verbatim")
    begin = found.end() if found[0].startswith("#") else found.start()
    ends = [m.start() for m in re.finditer(r"^## ", text[begin:], re.M)][:1]
    start = _requirements_start(text[begin:])
    end = begin + min(ends + ([start] if start is not None else []) + [len(text) - begin])
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text[begin:end]) if p.strip()]
    count = sum(len(p.split()) for p in paragraphs)
    if count > SHORT_REQUEST_WORDS:
        return (f"The user's messages in the requirements conversation, verbatim, are in the case's "
                f"`requirements.md` ({count} words).")
    return "\n>\n".join("> " + _md(p) for p in paragraphs)


def editor_record(case: Path) -> str:
    """The editor's record and the rest of the review, by path: each file under `<case>/review/`, with its first heading
    where it is Markdown."""
    folder = case / "review"
    if not folder.is_dir():
        raise FillError(f"{folder}: no review folder")
    lines: list[str] = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        title = re.search(r"^#+ (.+)$", path.read_text(errors="replace"), re.M) if path.suffix == ".md" else None
        lines.append(f"- `{path.relative_to(case).as_posix()}`" + (f": {_md(title[1])}" if title else ""))
    return "\n".join(lines)


def process_tables(case: Path) -> dict[str, Table]:
    """The tables `fill_template` prints in the appendix's section on the assistant and the process
    (author_upgrade.md, message A, 2.1.4), by name: `process_description`, the one description of the process, the same
    for every case; `seats_table`; `user_messages`; and `editor_record`."""
    return {
        "process_description": lambda facts: PROCESS_DESCRIPTION,
        "seats_table": lambda facts: seats_table(case),
        "user_messages": lambda facts: user_messages(case),
        "editor_record": lambda facts: editor_record(case),
    }


def check_document(text: str, case: Path, facts: Mapping[str, Any], kind: str) -> None:
    """Refuses a built paper (`kind` "paper") or appendix ("appendix") that does not carry the record's current entry for
    each limit, its text and its size as printed now, naming the point; and an appendix that does not carry the current
    status sentence. Text a document holds beyond the record, such as a limit since deleted from it, is not seen."""
    if kind not in ("paper", "appendix"):
        raise FillError(f"kind {kind!r}: a paper or an appendix")
    rows = read_points(case)
    for point, line in _limit_lines(rows, facts, _sizer(case, rows), kind):
        if line not in text:
            raise FillError(f"{point}: the {kind} does not carry the record's limit as it now stands: {line}")
    if kind == "appendix" and _status(rows) not in text:
        raise FillError(f"the appendix does not carry the record's status sentence: {_status(rows)}")


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m cost_benefit_engine.documents")
    sub = parser.add_subparsers(dest="command", required=True)
    cmp = sub.add_parser("compare", help="compare a case's rebuilt documents with their previous build")
    cmp.add_argument("case", type=Path)
    cmp.add_argument("previous", type=Path, help="the folder holding the previous build's *.md files")
    args = parser.parse_args(argv)
    try:
        return compare(cast(Path, args.case), cast(Path, args.previous))
    except (FillError, tomllib.TOMLDecodeError, OSError) as err:
        print(f"refused: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
