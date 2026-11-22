"""The stored suite of the sheet tools: one test for each row of the complaint register that marks a test.

Every sheet-generator build brief points at the register (`standards/presentation/sheets.md`, part 1), runs this whole
suite, and adds a register row and a test here for each new complaint of the owner's. The owner chose to keep a stored
suite (2026-11-20, his "a" to the seat's Decision 1, option A). Each test is named by its register row ("2.2 two
figures"), and runs on the synthetic data file beside it, `synthetic.toml`, made up so that each test has a case.

    .venv/bin/python -m tools.sheets.suite [--workers N] [--limit N]      (from the shared folder)
    .venv/bin/python -m tools.sheets.suite --write-base [REF]

About a minute on 2 workers (the default; one generate or import a worker). Exits 1 if any test fails, printing up to
--limit failures a test (default 12), the data file's faults apart from the generator's, and a last line naming the
failed tests by row; else exit 0 and a last line "PASS: N tests ran". Its generate runs inherit the environment,
PYTHONPATH included.

The interface it uses:
1. `python -m tools.sheets.script generate DATA --out DIR` writes DIR/sheet.xlsx; exit 0, or exit 2 on a fault in the
   data file (the generate check), naming the column's id in its output. `python -m tools.sheets.importer import`
   reads the text tabs of 1.5's export.
2. The base: `synthetic_base.xlsx` and `synthetic_base.json` beside this file, the generator's workbook and the twin's
   values (`load`, `compute`, `bounds`, `table_values`, `sensitivity_values`) on the synthetic file, written by
   `--write-base REF`, which runs the shared repository's own `shared/tools/sheets` at commit REF (default HEAD), extracted
   by `git archive`, never the working tree: the code under test is never used for an expected value. A build that
   changes the synthetic file rewrites the base from the commit before it, with the new file. The look constants of
   the code under test are read only to compare them with the snapshot of 3.8, and its Guide strings only to read
   their spelling (6.5). Generated xlsx files carry no cached values for column-tab draws, so every value a test
   needs comes from the base's JSON.
3. The data file, read with tomllib, for what a row asks of the data file itself (4.2, 4.4, 5.2, 5.3, 6.1 to 6.4). A
   data-file test that fails names a fault of the data file, which a build of the generator does not fix; the suite
   prints those apart, and fails on them too.

What it reads (the seat's notes for a later build). `Book.cells` holds every draw row (1,000 a column): a test that
walks cells uses `Book.view`, or a column's near0, dmin and dmax, rather than render every typed value. `Case.numbers`
collects rows 5 to 14 and the draws of every column tab and every number the twin gives a table or Sensitivity cell,
Sensitivity's r, rank r, key and noise line among them, which 2.2 tests at two figures; the run builder of 2.3's
`t_units_tables` skips r, rank r and key, which name no unit. 3.1 reads the widths, and 2.3 the unit of each column.

Layout. The template's column tab has the notes in row 2 and the first draw in row 16; a tab with a method of one column
has two rows inserted above the notes (Credence, Cumulative share), so its first draw is row 18, and every other tab keeps
the template's rows. The suite reads each tab's offset from the data file (`rows_offset`) when it reads a case, and sets
the row numbers to a tab's own (`on`) before it tests that tab. A label column stands before its block, but a pick's own
block's, which stands before the pick's set, and the blocks of one pick's set share a tint (`placed`). 4.16 (no cell has
two roles) builds each tab's role map and fails on a cell claimed twice or one a choice of the dropdown would write to that holds
anything else.

Readings this suite settles (each the seat's where the register does not say):
1. Kinds of formula, read from the xlsx: a plain reference is a formula that is one cell of another tab and nothing
   else (`=Globals!C13`, `='Option 1'!$DC$13`); a lookup is a formula whose outermost call is INDEX, VLOOKUP, HLOOKUP,
   XLOOKUP or LOOKUP and that reads another tab; a link is a HYPERLINK formula. A shared formula's cells take the kind
   of its first cell. Every plain reference is green #008000; a lookup may be green or black; a link is #1155CC and
   underlined; every other formula is black #000000. A cell with no formula is green only as the Guide colour key's
   green sample, and only where its row names a real link cell (a plain reference, green). (1.4)
2. Number formats must fit the grammar `render` reads: General, or up to three sections, each
   [condition][literals]{#,##0|0}[.0...][E+00][,...][%][literals], literals "$", "-", "(", ")", space, or quoted
   text. Sheets rounds half away from 0 and shows a negative number in a one-section format with a minus; in a format
   of two or three sections without conditions, the second shows a negative number's size and the third an exact 0
   (Google's rules: developers.google.com/sheets/api/guides/formats, support.google.com/docs/answer/56470);
   with conditions, the first section whose condition holds, else the section without one, and a negative number in
   a section with a condition shows Sheets' own minus, so a "-" written there doubles it (the layout look's reading
   of a live client sheet, 2026-11-21: "--0.2"; the rule is in the standard, register 2.2).
3. Significant figures (2.2): a shown number's figures run from its first nonzero digit to its format's step (150K
   has three, 3.0B two, 0.18 two); a "%" above 50% and a number between 0.5 and 1 count on their distance from 100% or
   1. A number passes at two or fewer. Excused: a year, a typed whole number of a table (a label), column A's draw
   numbers; a number that needs a further decimal to keep a value of its run off 0%, 100% or 1 (register 2.2's "keeps
   the digits", the generator's keep rule); and, on column tabs only, a whole number from 100 to 999 in an unscaled
   format (the standard's review 4.2, the seat's reading of the owner's "it only lets you choose decimals").
   The draws of a column share one format chosen at their typical size (the mean of their absolute values), so the
   draws are tested at that size; a draw of a fat tail far above it shows more figures in that one format.
4. Units (2.3): no number shows five digits or more before its decimal point (12,345), a year and a label excused;
   the top unit, trillion, has none above it, so a whole number of trillions may run past four digits (R63). No cell
   format on any tab scales a number (no trailing comma) or carries a scale letter or abbreviation (K, M, B, T, Q, mil,
   bil, bn, tn), and no cell names a unit past trillion. A column tab's money column shows its values in the unit its
   name gives in words in brackets (thousand, million, billion, trillion; no abbreviation), the number the cell holds
   and shows alike; the unit is the one that shows the column's typical value at two figures, "(₩ trillion)" over
   2.7, never 2,677 under "(₩ billion)" (the owner: "no thats 3 sigfigs which I know Ive complained about before
   too"), and its note's first money unit is the heading's (reading 11). A formula that reads a column of another
   unit carries the factor beside the reference, and its note names each factor in a "Conversions:" line, the
   column by its letter (Tab!letter on another tab): the generated sheet is read, and a variant of the data file
   with a calculation in a stated unit that multiplies a column of another unit by 1,000 is generated and read the
   same way. Any scaled number of 1,000 or more shows thousands separators. A Guide text shows no example of a number
   of 1,000 or more under a scaled unit (2,677 under "GDP (₩ billion)"). A head naming a money unit names the unit
   its run is shown in, and a mean and its interval share one (Results and Sensitivity). Google's number formats scale
   only by powers of 1,000 (the rule is in the standard, register 2.3).
5. Clipping (2.4): a shown number's width, 6 px a character and 10 px of padding at Arial 10, fits its column; tested
   on column tabs at a column's smallest and largest draw as well as its statistics and Set cells.
6. The seat's numbers, to be put to the owner as such: the data file's Guide text at most GUIDE_WORDS words (4.4,
   about four minutes' reading); a Guide column-A text at most GUIDE_A_CHARS characters (4.5, the limit of a tab's
   A1); the synthetic file's reader is American, so every text of its sheet is read for 6.5.
7. Heights (3.2): rows 1 to 15 equal the template's heights (HEIGHT, 455 px together since 2026-11-16, when the owner
   saw them and asked for row 3 a little taller); the register's "at most 420 px", a seat's estimate of what leaves
   three draw rows on his laptop, contradicts them and is not tested until he rules.
8. The greps of 1.4 and 8.5 read the live homes of the rules: the standard less its register (part 1, a record that
   quotes old rules), the agent files and the package's own files, this one aside.
9. Constants and cases (6.1, 6.3), from the rows' quoted words ("no constants anywhere for anything uncertain"; "do
   not have seperate columns for low middle and high anything. make discount rate and anything like that a
   distribution"). A constant passes where it is a convention (its citation begins "Convention", or names a
   definition or unit conversion) or a published value for a past period (its name or id gives a year no later than
   the dollar year its data file's Guide states, "2025 won", "a 2025 dollar", or FIXED_YEAR where it states none, so
   that one file gets one verdict in every calendar year; and its citation gives a source's address, as a 2020 census
   count); every other constant is a judged or forecast quantity and fails. FIXED_YEAR is 2025, so the synthetic file
   states 2024, and a test of `stated_year` can tell its read from the fallback. Columns of one tab whose names differ
   only by low, mid, middle, central or high fail, unless each is a constant marked "Convention", or a calculation
   reading such a constant, the sets read differing between them (a result at each of the guidance's discount
   rates). A discount rate passes as a distribution, or as a constant marked "Convention" (every rate the applicable
   guidance reports is shown). The test reruns both on a copy of the data file with its discount rates marked
   "Convention", which must pass, and with a future-year constant and a low and high pair of judged inputs added,
   which must fail.
10. Terminal numbers (2.2; the owner, 2026-11-21, R63: "its fine to round any terminal displayed value that nothing
   else uses as an input"). A cell whose formula is ROUNDED, LET(x,F,IF(ISNUMBER(x),IF(x=0,0,ROUND(x,1-FLOOR(LOG10(
   ABS(x)),1))),x)), is read as F, rounded, and shows the twin's value at two significant figures, half away from 0
   (`round2`); the zeros before its point hold places and are not counted. No formula cites a rounded cell, and every
   formula of its own in a number format that is neither a share nor a year, which no formula cites, is rounded
   (`read_cells`: every reference of every formula, a shared formula's taken down its range).
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import math
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]  # the shared folder
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.sheets import script as ss  # noqa: E402  the look constants (3.8) and the Guide's own strings (6.5)

PY = sys.executable
DATA = HERE / "synthetic.toml"
BASE_XLSX, BASE_JSON = HERE / "synthetic_base.xlsx", HERE / "synthetic_base.json"
LABEL = "synthetic"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
M = "{" + NS + "}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
BLACK, INPUT_BLUE, GREEN, LINK_BLUE, LABEL_FILL, LINE = "000000", "0000FF", "008000", "1155CC", "FFFF00", "CCCCCC"
KINDS7 = {"beta", "constant", "lognormal", "normal", "power law", "triangular", "uniform"}
FOUR = {"number", "$", "%", "year"}
# The row numbers below are set for the tab being tested by their setter (`on`), so the rule on redefining a constant is
# off for this file.
# pyright: reportConstantRedefinition=false
# The rows of a column tab, read from the data file by the rule of the docs (the suite's own reading, never the code under
# test's): the template's layout has the notes in row 2 and the first draw in row 16; a tab with a method of one column has
# two rows inserted above the notes, Credence (row 2) and Cumulative share (row 3) (`set_rows`, `on`).
INSERTED = 2
OFFS: dict[str, int] = {}  # each column tab's offset, by name (`rows_offset`), set when a case is read
OFF = 0
NOTE = CITE = KIND = P1 = P7 = SLO = SMEAN = SHI = GRAPH = FIRST = LAST = CRED = SHARE = 0


def set_rows(off: int) -> None:
    global OFF, NOTE, CITE, KIND, P1, P7, SLO, SMEAN, SHI, GRAPH, FIRST, LAST, CRED, SHARE
    OFF = off
    NOTE, CITE, KIND, P1, P7 = 2 + off, 3 + off, 4 + off, 5 + off, 11 + off
    SLO, SMEAN, SHI, GRAPH, FIRST, LAST = 12 + off, 13 + off, 14 + off, 15 + off, 16 + off, 1015 + off
    CRED, SHARE = (2, 3) if off else (0, 0)


def on(sheet: str) -> None:
    """Set the row numbers to the tab's own layout."""
    set_rows(OFFS.get(sheet, 0))


def tr(r: int) -> int:
    """A row of the template's layout, in the layout of the sheet being tested."""
    return r + OFF if r >= 2 else r


set_rows(0)
CHAR_PX, PAD_PX, TABLE_PX = 6, 10, 100
GUIDE_WORDS, GUIDE_A_CHARS = 1000, 45  # the seat's numbers (reading 6)
MARKS = ("Judge:", "Unpublished:", "Judgment", "Convention", "No source:")
KEY_SAMPLES = {"Input": INPUT_BLUE, "Formula": BLACK, "From another tab": GREEN, "Link": LINK_BLUE}
BRITISH = ("tonne", "programme", "colour", "centre", "modelling")
# 1.5: his Monte Carlo Template's Readme (1FNCjzT3fCH2J2XU_P-NsmGBJahm2rz6U58mxyScAWno), read 2026-11-21 (R58): heads Arial
# 16 bold (A1, A7, A29); subheads Arial 10 bold #222222 (A10, A22, A25); body Arial 10 #222222 (A2 to A5, A8, A9, A11).
TEMPLATE_HEADS = ("How to Read the Sheet", "Quick Start", "Technical Details")
TEMPLATE_SUBHEADS = ("Inputs", "Outputs and Intermediate Calculations", "Combining Estimates")
TEMPLATE_INK = "222222"
# 3.8: the look as the owner's template set it; a build changes it only where its brief names the change, editing this with it.
LOOK_SNAPSHOT: dict[str, object] = {
    "FONT": "Arial", "SIZE": 10, "WIDTH_A": 120, "WIDTH": 70, "SPARE": 12, "LINE": "CCCCCC",
    "HEIGHT": {1: 69, 2: 56, 3: 54, **dict.fromkeys(range(4, 15), 19), 15: 67},
    "LOOK": {1: ("center", "top", True), 2: ("left", "top", True), 3: ("left", "top", True), 4: ("left", "bottom", False),
             5: ("center", "bottom", False), 6: ("center", "bottom", False), 7: ("left", "bottom", False),
             8: ("center", "bottom", False), 9: ("right", "bottom", False), 10: ("center", "bottom", False),
             11: ("center", "bottom", False), 12: ("left", "bottom", False), 13: ("center", "bottom", False),
             14: ("right", "bottom", False), 15: (None, "top", False)},
    "COLOURS": ("000000", "0000FF", "008000", "1155CC", "222222"),  # 222222: the guide's text, his template's Readme ink (R58)
    "GUIDE_WIDTHS": (170, 600, 200, 320),
}
# 8.5: the superseded rules of the register's section 9, which no rule file states unless it marks them superseded
SUPERSEDED = ["at least 11", "merged across", "never scaled to thousands", "ARRAYFORMULA", "a formula that reads another tab",
              "a new file with a new link", r"in red\b"]
STANDARD = "standards/presentation/sheets.md"
RULE_FILES = [STANDARD, "agents/sheet-layout.md", "agents/sheet-twin.md", "tools/sheets/__init__.py", "tools/sheets/script.py",
              "tools/sheets/importer.py", "tools/sheets/inplace.py"]  # reading 8
OLD = [  # 1.4: the old green rule's phrasings (green for any formula reading another tab)
    r"green (text )?(is |for )?(a )?formulas? (on a model tab )?(that )?(reads?|reading) another tab",
    r"formulas? (that )?(reads?|reading) another tab,? (in )?green",
    r"green where it reads another tab",
    r"a formula, a formula reading another tab",
    r"green cross-tab formula",
]
# reading 10: a terminal cell's formula F as the generator wraps it, and a cell reference in a formula
ROUNDED = re.compile(r"LET\(x,(.*),IF\(ISNUMBER\(x\),IF\(x=0,0,ROUND\(x,1-FLOOR\(LOG10\(ABS\(x\)\),1\)\)\),x\)\)", re.S)
REF = re.compile(r"(?:(?P<tab>'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!|(?<![A-Za-z0-9_.$!']))(?P<cd1>\$?)(?P<c1>[A-Z]{1,3})(?P<rd1>\$?)(?P<r1>\d+)"
                 r"(?::(?P<cd2>\$?)(?P<c2>[A-Z]{1,3})(?P<rd2>\$?)(?P<r2>\d+))?(?![A-Za-z0-9_(])")
PLAIN = re.compile(r"((?:'(?:[^']|'')+')|[A-Za-z_][A-Za-z0-9_.]*)!\$?([A-Z]{1,3})\$?(\d+)")
LOOKUPS = ("INDEX(", "VLOOKUP(", "HLOOKUP(", "XLOOKUP(", "LOOKUP(")
UNIT = re.compile(r"(?<![\w])([₩$€£¥])\s?(thousand|million|billion|trillion|mil|bil|tril|000)?(?![\w#0])", re.I)
UNIT_SIZE = {None: 1.0, "thousand": 1e3, "000": 1e3, "million": 1e6, "mil": 1e6, "billion": 1e9, "bil": 1e9, "trillion": 1e12,
             "tril": 1e12}
ERRORS = {"#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NUM!", "#NAME?", "#ERROR!", "#NULL!"}
SENS_HEAD = ("Rank", "Input", "Tab", "r", "Rank r", "Change", "Key")
SCALE_WORDS = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}
WORD_OF = {v: k for k, v in SCALE_WORDS.items()}
TOP = 1e12  # the largest unit is trillion (reading 4, R63)
SCI_FROM = 10_000  # reading 11: a number that is not money and this large shows in scientific notation (the seat's threshold, R63)
CURRENCY = r"₩|\$|€|£|¥|USD|KRW|EUR|GBP|JPY"
SAME_CURRENCY = {"₩": "KRW", "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
HEAD_UNIT = re.compile(r"(?<![\w])(?:(?P<cur>" + CURRENCY + r")\s?(?P<size>000|thousand|mil|million|bil|billion|tril|trillion)?"
                       r"|(?P<bare>000|thousand|mil|million|bil|billion|tril|trillion))s?(?![\w])", re.I)  # in a heading's brackets
NOTE_MONEY = re.compile(r"(?<![\w])(?P<cur>" + CURRENCY + r")(?!\s?\d)\s?(?P<size>000|thousand|mil|million|bil|billion|tril|trillion)?s?(?![\w])", re.I)
FIXED_YEAR = 2025  # reading 9: the past-period year of a data file whose Guide states no dollar year
SRC_UNIT = re.compile(r"(?<!\S)(?:(?:[₩$€£¥]|KRW|USD|EUR|GBP|JPY)\s?(?P<size>000|thousand|mil|million|bil|billion|tril|trillion|quadrillion)?"
                      r"|(?P<bare>000|thousand|mil|million|bil|billion|tril|trillion|quadrillion))s?(?=$|[\s,/)])", re.I)  # "(₩ Bil)", "($000)", "(mil)", "(₩/min)"
SRC_SIZE = {"000": 1e3, "thousand": 1e3, "mil": 1e6, "million": 1e6, "bil": 1e9, "billion": 1e9, "tril": 1e12, "trillion": 1e12,
            "quadrillion": 1e15}
ABBREV = re.compile(r"(?<![A-Za-z])(mil|bil|tril|mn|bn|tn)(?![A-Za-z])|(?:^|[₩$€£¥\s])000(?!\d)", re.I)
FOUR_FIGURE_EXAMPLE = re.compile(r"(?<![\d,.])(\d{1,3}(?:,\d{3})+)(?![\d,]) under \"[^\"]*\((?:[^()]*\s)?(thousand|million|billion|trillion)\)", re.I)
SCALE_LETTER = re.compile(r"(?<![A-Za-z])(k|m|mm|b|bn|t|tn|q|mil|bil|tril)(?![A-Za-z])", re.I)
shown = {"limit": 12}  # failures printed a test (--limit)
failures: list[str] = []
ran: list[str] = []
counts: dict[str, int] = {}
DATA_TESTS = {"4.2 notes", "4.4 guide short", "5.2 no copies", "5.3 picks show the pick", "6.1 no constants for the uncertain",
              "6.2 one distribution", "6.3 no low, mid and high", "6.4 globals reused"}


def fail(name: str, why: str) -> None:
    counts[name] = counts.get(name, 0) + 1
    if counts[name] <= shown["limit"]:
        failures.append(f"FAIL {name}: {why}")
    elif counts[name] == shown["limit"] + 1:
        failures.append(f"FAIL {name}: (more)")


def test(name: str) -> str:
    if name not in ran:
        ran.append(name)
    return name


def letter(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def colnum(s: str) -> int:
    n = 0
    for ch in s:
        n = n * 26 + ord(ch) - 64
    return n


def unquote(tab: str) -> str:
    return tab[1:-1].replace("''", "'") if tab.startswith("'") else tab


def unit_of(text: str | None) -> tuple[str, float] | None:
    m = UNIT.search(text or "")
    return None if m is None else (m.group(1), UNIT_SIZE[(m.group(2) or "").lower() or None])


def bracket_unit(text: str) -> float | None:
    """The size of the first unit a text gives in brackets ("(₩ Bil)" 1e9, "($000)" 1e3, "(mil)" 1e6), or None."""
    for p in re.finditer(r"\(([^()]*)\)", text):
        m = SRC_UNIT.search(p.group(1))
        if m is not None:
            word = m.group("size") or m.group("bare")
            return SRC_SIZE[word.lower()] if word else 1.0
    return None


def source_size(col: dict[str, Any]) -> float:
    """The unit a data-file column's values are in: the first its name, note or group label gives in brackets (reading 4)."""
    for key in ("name", "note", "group"):
        size = bracket_unit(str(col.get(key) or ""))
        if size is not None:
            return size
    return 1.0


def money_of(m: re.Match[str] | None) -> tuple[str, float] | None:
    """A unit a match names, its currency normalised (₩ is KRW) and its size; None for none."""
    if m is None:
        return None
    cur = m.group("cur") or ""
    word = (m.groupdict().get("size") or m.groupdict().get("bare") or "").lower()
    return SAME_CURRENCY.get(cur, cur.upper()), SRC_SIZE[word] if word else 1.0


def head_unit(text: str) -> tuple[str, float] | None:
    """The unit a column's heading gives in its first brackets that name one (reading 11), currency empty for a count."""
    for p in re.finditer(r"\(([^()]*)\)", text):
        m = HEAD_UNIT.search(p.group(1))
        if m is not None:
            return money_of(m)
    return None


def shown_word(text: str) -> str | None:
    """The first scale word (thousand to trillion) a text gives in brackets."""
    for p in re.finditer(r"\(([^()]*)\)", text):
        m = re.search(r"(?<![A-Za-z])(" + "|".join(SCALE_WORDS) + r")(?![A-Za-z])", p.group(1), re.I)
        if m is not None:
            return m.group(1).lower()
    return None


def commas_of(fmt: str) -> int:
    """The trailing commas (each a division by 1,000) of a format's first numeric section; 0 for General or a percent."""
    for sec in sections(fmt):
        m = SECTION.fullmatch(COND.sub("", sec, count=1))
        if m is not None:
            return 0 if m.group("pct") else len(m.group("commas"))
    return 0


def literals(fmt: str) -> str:
    """A format's literal text: quoted strings, backslash-escaped characters and bare letters, less E+00 and General."""
    if fmt == "General":
        return ""
    body = re.sub(r"\[[^\]]*\]", " ", fmt)
    quoted = " ".join(re.findall(r'"([^"]*)"', body))
    body = re.sub(r'"[^"]*"', " ", body)
    escaped = " ".join(re.findall(r"\\(.)", body))
    body = re.sub(r"\\.", " ", body)
    body = re.sub(r"E[+-]0+", " ", body)
    return " ".join((quoted, escaped, " ".join(re.findall(r"[A-Za-z]+", body))))


# reading an .xlsx ----------------------------------------------------------------------------------------------------

@dataclass
class Cell:
    s: int
    f: str | None = None  # the formula; a shared formula's cells hold its first cell's text, with offset its row's distance
    text: str | None = None
    num: float | None = None
    offset: int = 0
    span: str | None = None  # a shared formula's first cell: the range it fills
    rounded: bool = False  # the formula is wrapped in ROUNDED, and f holds the formula inside it (reading 10)


@dataclass(frozen=True)
class FontOf:
    name: str
    size: float
    bold: bool
    under: bool
    colour: str


@dataclass(frozen=True)
class Xf:
    font: int
    fmt: int
    fill: int
    border: int
    h: str | None
    v: str | None
    wrap: bool


@dataclass
class Sheet:
    cells: dict[tuple[int, int], Cell] = field(default_factory=lambda: {})
    links: dict[int, list[str]] = field(default_factory=lambda: {})
    cols: list[tuple[int, int, float]] = field(default_factory=lambda: [])  # min, max, px
    heights: dict[int, float] = field(default_factory=lambda: {})  # px
    pane: tuple[str, str, str] | None = None  # xSplit, ySplit, state
    merges: int = 0
    validations: list[tuple[str, str]] = field(default_factory=lambda: [])  # sqref, formula1
    view: dict[tuple[int, int], Cell] = field(default_factory=lambda: {})  # cells, less draw rows that repeat row 16's style and kind
    notes: dict[str, str] = field(default_factory=lambda: {})  # a cell's address -> its note (an xlsx comment)

    def width(self, col: int, default: float) -> float:
        return next((w for a, b, w in self.cols if a <= col <= b), default)


def children(el: ET.Element | None) -> list[ET.Element]:
    return [] if el is None else list(el)


class Book:
    def __init__(self, path: Path) -> None:
        z = zipfile.ZipFile(path)
        rels = {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        self.order: list[str] = []
        self.sheets: dict[str, Sheet] = {}
        try:
            shared = ["".join(t.text or "" for t in si.iter(M + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si")]
        except KeyError:
            shared = []
        st = ET.fromstring(z.read("xl/styles.xml"))
        self.codes = {int(n.get("numFmtId") or 0): n.get("formatCode") or "" for n in st.iter(M + "numFmt")}
        self.fonts: list[FontOf] = []
        for f in children(st.find(M + "fonts")):
            sz, col, nm = f.find(M + "sz"), f.find(M + "color"), f.find(M + "name")
            rgb = BLACK if col is None or col.get("rgb") is None else (col.get("rgb") or "")[-6:].upper()
            self.fonts.append(FontOf("" if nm is None else nm.get("val") or "", 10.0 if sz is None else float(sz.get("val") or 10),
                                     f.find(M + "b") is not None, f.find(M + "u") is not None, rgb))
        self.fills: list[str | None] = []
        for fl in children(st.find(M + "fills")):
            fg = fl.find(f"{M}patternFill/{M}fgColor")
            self.fills.append(None if fg is None else (fg.get("rgb") or "")[-6:].upper())
        self.borders: list[set[str] | None] = []  # the colours of a border's four sides, or None where a side is missing
        for b in children(st.find(M + "borders")):
            sides = [b.find(M + s) for s in ("left", "right", "top", "bottom")]
            if any(s is None or s.get("style") is None for s in sides):
                self.borders.append(None)
            else:
                self.borders.append({(c.get("rgb") or "")[-6:].upper() if c is not None else "" for s in sides if s is not None for c in [s.find(M + "color")]})
        self.xf: list[Xf] = []
        for x in children(st.find(M + "cellXfs")):
            al = x.find(M + "alignment")
            self.xf.append(Xf(int(x.get("fontId") or 0), int(x.get("numFmtId") or 0), int(x.get("fillId") or 0), int(x.get("borderId") or 0),
                              None if al is None else al.get("horizontal"), None if al is None else al.get("vertical"),
                              al is not None and al.get("wrapText") in ("1", "true")))
        for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"):
            t = rels[sh.get(R + "id")].lstrip("/")
            name = sh.get("name") or ""
            self.order.append(name)
            part = t if t.startswith("xl/") else "xl/" + t
            self.sheets[name] = self.read_sheet(ET.fromstring(z.read(part)), shared)
            folder, base = part.rsplit("/", 1)
            try:
                links = ET.fromstring(z.read(f"{folder}/_rels/{base}.rels"))
            except KeyError:
                continue
            for rel in links:
                if (rel.get("Type") or "").endswith("/comments"):
                    target = (rel.get("Target") or "").lstrip("/")
                    target = target if target.startswith("xl/") else "xl/" + target.removeprefix("../")
                    for cm in ET.fromstring(z.read(target)).iter(M + "comment"):
                        self.sheets[name].notes[cm.get("ref") or ""] = "".join(x.text or "" for x in cm.iter(M + "t"))

    @staticmethod
    def read_sheet(root: ET.Element, shared: list[str]) -> Sheet:
        out = Sheet()
        masters: dict[str, tuple[str, int]] = {}
        pending: list[tuple[Cell, str, int]] = []
        for row in root.iter(M + "row"):
            ht = row.get("ht")
            if ht is not None:
                out.heights[int(row.get("r") or 0)] = float(ht) * 4 / 3
        for c in root.iter(M + "c"):
            m = re.fullmatch(r"([A-Z]+)(\d+)", c.get("r") or "")
            if not m:
                continue
            r, col = int(m.group(2)), colnum(m.group(1))
            f, v, t = c.find(M + "f"), c.find(M + "v"), c.get("t")
            d = Cell(int(c.get("s") or 0))
            if f is not None:
                if f.get("t") == "shared":
                    si = f.get("si") or ""
                    if f.text:
                        masters[si] = (f.text, r)
                        d.f, d.span = f.text, f.get("ref")
                    else:
                        pending.append((d, si, r))
                else:
                    d.f = f.text or ""
                    if (w := ROUNDED.fullmatch(d.f)) is not None:
                        d.f, d.rounded = w.group(1), True
                if t == "str" and v is not None:
                    d.text = v.text or ""
            elif t == "inlineStr":
                d.text = "".join(x.text or "" for x in c.iter(M + "t"))
            elif v is not None and v.text is not None:
                if t == "s":
                    d.text = shared[int(v.text)]
                elif t in ("str", "e"):
                    d.text = v.text
                else:
                    d.num = float(v.text)
            out.cells[(r, col)] = d
        for d, si, r in pending:
            if si in masters:
                d.f, d.offset = masters[si][0], r - masters[si][1]
        for h in root.iter(M + "hyperlink"):
            mm = re.fullmatch(r"([A-Z]+)(\d+)", (h.get("ref") or "").split(":")[0])
            if mm and h.get("location"):
                out.links.setdefault(int(mm.group(2)), []).append(h.get("location") or "")
        out.cols = [(int(c.get("min") or 0), int(c.get("max") or 0), float(c.get("width") or 0) * 7) for c in root.iter(M + "col")]
        pane = root.find(f"{M}sheetViews/{M}sheetView/{M}pane")
        if pane is not None:
            out.pane = (pane.get("xSplit") or "", pane.get("ySplit") or "", pane.get("state") or "")
        out.merges = sum(1 for _ in root.iter(M + "mergeCell"))
        out.validations = [(dv.get("sqref") or "", dv.findtext(M + "formula1") or "") for dv in root.iter(M + "dataValidation")]

        def repeats(r: int, c: int, d: Cell) -> bool:
            first = out.cells.get((FIRST, c))
            return r > FIRST and first is not None and d.s == first.s and d.f == first.f and d.text is None and first.text is None
        out.view = {key: d for key, d in out.cells.items() if not repeats(*key, d)}
        return out

    def cells(self, sheet: str) -> dict[tuple[int, int], Cell]:
        return self.sheets[sheet].cells if sheet in self.sheets else {}

    def view(self, sheet: str) -> dict[tuple[int, int], Cell]:
        """A sheet's cells but the draw rows that repeat row 16's style and formula: what a test of looks needs."""
        return self.sheets[sheet].view if sheet in self.sheets else {}

    def font(self, s: int) -> FontOf:
        return self.fonts[self.xf[s].font if s < len(self.xf) else 0]

    def style(self, s: int) -> Xf:
        return self.xf[s] if s < len(self.xf) else Xf(0, 0, 0, 0, None, None, False)

    def fill(self, s: int) -> str | None:
        i = self.style(s).fill
        return self.fills[i] if i < len(self.fills) else None

    def fmt(self, s: int) -> str:
        n = self.style(s).fmt
        return self.codes.get(n, {0: "General", 1: "0", 2: "0.00", 3: "#,##0", 4: "#,##0.00", 9: "0%", 10: "0.00%", 11: "0.00E+00"}.get(n, f"builtin {n}"))


def kind_of(formula: str, here: str) -> str:
    """plain, lookup, link, label or other (reading 1)."""
    if formula.startswith("HYPERLINK("):
        return "link"
    if 'CELL("address"' in formula:
        return "label"
    m = PLAIN.fullmatch(formula.strip())
    if m and unquote(m.group(1)) != here:
        return "plain"
    if formula.startswith(LOOKUPS) and any(unquote(x.group(1)) != here for x in PLAIN.finditer(formula)):
        return "lookup"
    return "other"


def read_cells(book: Book) -> dict[str, dict[int, list[tuple[int, int]]]]:
    """For each tab, each column's row spans that some formula of the workbook cites (reading 10): a reference with or
    without its tab, a range, and a shared formula's relative references taken down the range it fills; texts in
    quotes and function names are not references."""
    out: dict[str, dict[int, list[tuple[int, int]]]] = {}
    for here in book.order:
        for d in book.cells(here).values():
            if d.f is None or d.offset:
                continue
            down = across = 0
            if d.span and (m := re.fullmatch(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", d.span)):
                down, across = int(m.group(4)) - int(m.group(2)), colnum(m.group(3)) - colnum(m.group(1))
            for x in REF.finditer(re.sub(r'"(?:[^"]|"")*"', '""', d.f)):
                tab = here if x.group("tab") is None else unquote(x.group("tab"))
                c1, r1 = colnum(x.group("c1")), int(x.group("r1"))
                c2, r2 = (colnum(x.group("c2")), int(x.group("r2"))) if x.group("c2") else (c1, r1)
                single = x.group("c2") is None
                if not (x.group("rd1") == "$" and (single or x.group("rd2") == "$")):  # a relative row moves down the fill
                    r2 += down
                if not (x.group("cd1") == "$" and (single or x.group("cd2") == "$")):
                    c2 += across
                for c in range(min(c1, c2), max(c1, c2) + 1):
                    out.setdefault(tab, {}).setdefault(c, []).append((min(r1, r2), max(r1, r2)))
    return out


def reads(read: dict[str, dict[int, list[tuple[int, int]]]], sheet: str, r: int, c: int) -> bool:
    return any(a <= r <= b for a, b in read.get(sheet, {}).get(c, []))


def round2(v: float) -> float:
    """v as ROUNDED shows it: two significant figures, half away from zero (reading 10)."""
    return v if v == 0 or not math.isfinite(v) else float(half_up(v, 1 - math.floor(math.log10(abs(v)))))


def refs_in(text: str, tabs: list[str]) -> list[tuple[str, str]]:
    """The cells a text or formula names, Tab!A1 or 'Tab name'!$A$1, for the workbook's tab names (quoted or not)."""
    out: list[tuple[str, str]] = []
    for t in sorted(tabs, key=len, reverse=True):
        for m in re.finditer(rf"(?:'{re.escape(t.replace(chr(39), chr(39) * 2))}'|(?<![\w']){re.escape(t)})!\$?([A-Z]{{1,3}})\$?(\d+)", text):
            out.append((t, m.group(1) + m.group(2)))
    return out


# number formats ------------------------------------------------------------------------------------------------------

SECTION = re.compile(r'(?P<pre>(?:"[^"]*"|[$\-() ])*)(?P<int>#,##0|0)(?:\.(?P<dec>0+))?(?P<exp>E\+0+)?(?P<commas>,*)(?P<pct>%?)(?P<post>(?:"[^"]*"|[$\-() ])*)')
COND = re.compile(r"\[(<=|>=|<>|<|>|=)(-?\d+(?:\.\d+)?)\]")


def sections(fmt: str) -> list[str]:
    out: list[str] = []
    cur, q = "", False
    for ch in fmt:
        if ch == '"':
            q = not q
        if ch == ";" and not q:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + [cur]


def half_up(x: float, places: int) -> Decimal:
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)


def holds(op: str, v: float, x: float) -> bool:
    return {"<": v < x, "<=": v <= x, ">": v > x, ">=": v >= x, "=": v == x, "<>": v != x}[op]


@dataclass(frozen=True)
class Shown:
    text: str  # what Sheets shows; "?" first where a negative number shows without its sign
    shown: float  # the shown number in the format's displayed units (nan where its sign is lost)
    step: float  # the format's step in those units
    scale: float  # cell value = shown x scale
    scaled: bool  # the section divides by commas or names a unit by a letter


def render(fmt: str, v: float) -> Shown | None:
    """How Sheets shows v in fmt, or None for a format outside reading 2 (Google's custom number format rules,
    developers.google.com/sheets/api/guides/formats and support.google.com/docs/answer/56470)."""
    if fmt == "General":
        return Shown(str(int(v)) if v == int(v) else repr(v), v, 0.0, 1.0, False)
    parts = sections(fmt)
    if len(parts) > 3:
        return None
    conds = [COND.match(p) for p in parts]
    if any(c is not None for c in conds):
        pick = next((i for i, c in enumerate(conds) if c is not None and holds(c.group(1), v, float(c.group(2)))), None)
        if pick is None:
            pick = next((i for i, c in enumerate(conds) if c is None), len(parts) - 1)
        c = conds[pick]
        sec, x, auto = parts[pick][c.end():] if c is not None else parts[pick], v, c is not None and v < 0
    elif len(parts) == 1:
        sec, x, auto = parts[0], v, v < 0
    elif v < 0:
        sec, x, auto = parts[1], -v, False
    elif v == 0 and len(parts) == 3:
        sec, x, auto = parts[2], v, False
    else:
        sec, x, auto = parts[0], v, False
    if "[" in sec:
        return None
    m = SECTION.fullmatch(sec)
    if m is None:
        return None
    scale = 1000.0 ** len(m.group("commas")) / (100.0 if m.group("pct") else 1.0)
    y = abs(x) / scale
    d = len(m.group("dec") or "")
    if m.group("exp"):
        e = 0 if y == 0 else math.floor(math.log10(y))
        mant = half_up(y / 10 ** e, d) if y else Decimal(0)
        if abs(mant) >= 10:
            e, mant = e + 1, half_up(y / 10 ** (e + 1), d)
        body = f"{mant:.{d}f}E+{e:02d}" if e >= 0 else f"{mant:.{d}f}E-{-e:02d}"
        shown_abs, step = float(mant) * 10 ** e, 10.0 ** (e - d)
    else:
        q = half_up(y, d)
        body = f"{q:,.{d}f}" if m.group("int") == "#,##0" else f"{q:.{d}f}"
        shown_abs, step = float(q), 10.0 ** -d
    pre, post = m.group("pre").replace('"', ""), m.group("post").replace('"', "")
    text = ("-" if auto else "") + pre + body + ("%" if m.group("pct") else "") + post
    signed = auto or "-" in pre + post or "(" in pre
    scaled = bool(m.group("commas")) or bool(re.search(r"[A-Za-z]", post))
    if v < 0 and shown_abs != 0 and not signed:
        return Shown("?" + text, float("nan"), step, scale, scaled)
    return Shown(text, -shown_abs if v < 0 and signed else shown_abs, step, scale, scaled)


def unit2(x: float) -> float:
    return 10.0 ** (math.floor(math.log10(abs(x))) - 1)


def figures(got: Shown, pct: bool) -> int | None:
    """A shown number's significant figures (reading 3), or None where it shows 0, exactly 1 or 100%, or General."""
    if math.isnan(got.shown) or got.shown == 0 or got.step == 0:
        return None
    a = abs(got.shown)
    if pct and 50 < a < 100:
        a = 100 - a
    elif not pct and not got.scaled and 0.5 < a < 1:
        a = 1 - a
    if a <= 1e-12:
        return None
    return math.floor(math.log10(a) + 1e-9) - round(math.log10(got.step)) + 1


def fewer(fmt: str) -> str | None:
    """fmt with one decimal fewer in every section, or None where it has none."""
    out = re.sub(r"\.(0+)", lambda m: "." + m.group(1)[1:] if len(m.group(1)) > 1 else "", fmt)
    return None if out == fmt else out


def keeps(fmt: str, run: list[float]) -> bool:
    """Whether a decimal fewer would show a value of the run as 0%, 100% or 1 (the keep rule); never for a share format of more than one decimal."""
    if "%" in fmt and (m := re.search(r"\.(0+)", fmt)) is not None and len(m.group(1)) > 1:
        return False  # a share never shows more than one decimal of a percent (the coordinator's ruling, 2026-11-21)
    f2 = fewer(fmt)
    if f2 is None:
        return False
    for v in run:
        got = render(f2, v)
        if got is None or math.isnan(got.shown):
            continue
        if "%" in fmt and 0 < v < 1 and got.shown * got.scale in (0.0, 1.0):
            return True
        if "%" in fmt and 0 < v < 1 and abs(got.shown * got.scale - v) > 0.5 * unit2(min(v, 1 - v)) * (1 + 1e-9):
            return True  # a share of the run would show under two figures
        if "%" not in fmt and 0.5 < abs(v) < 1 and abs(got.shown * got.scale) == 1:
            return True
    return False


# the base: the generator's workbook and the twin's values at a commit ---------------------------------------------------------------------

HELPER = r'''
import json, sys
import numpy as np
from pathlib import Path
from tools.sheets import script as ss
data, out = Path(sys.argv[1]), Path(sys.argv[2])
tabs = ss.load(data)
ss.generate(tabs, out)
comp = ss.compute(tabs)
_, pct = ss.bounds(tabs)
res = {"tables": {}, "strings": {}, "columns": {}}
for t in tabs:
    vals = ss.table_values(t, comp, pct) if t.kind == "table" else ss.sensitivity_values(t, tabs, comp, pct) if t.kind == "sensitivity" else None
    if vals is not None:
        res["tables"][t.name] = [[r, c, v] for (r, c), (v, _) in vals.items() if isinstance(v, float)]
        res["strings"][t.name] = [[r, c, v] for (r, c), (v, _) in vals.items() if isinstance(v, str)]
    for c in t.columns:
        d = np.asarray(comp[t.name][c.id], dtype=np.float64)
        f = d[np.isfinite(d)]
        res["columns"].setdefault(t.name, {})[c.letter] = {"id": c.id, "name": c.name, "note": c.note, "format": c.format, "kind": c.kind,
            "stats": [float(np.percentile(d, 100 * pct[0])), float(np.mean(d)), float(np.percentile(d, 100 * pct[1]))],
            "typ": float(np.mean(np.abs(f))) if f.size else 0.0, "dmin": float(f.min()) if f.size else 0.0, "dmax": float(f.max()) if f.size else 0.0,
            "near0": ([float(f[f < 0].max())] if (f < 0).any() else []) + ([float(f[f > 0].min())] if (f > 0).any() else [])}
(out / "base.json").write_text(json.dumps(res))
'''


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def write_base(ref: str) -> int:
    """Write synthetic_base.xlsx and synthetic_base.json from the shared repository's tools/sheets at commit ref."""
    work = Path(tempfile.mkdtemp(prefix="sheet_suite_base_"))
    try:
        tar = subprocess.run(["git", "-C", str(ROOT), "archive", ref, "tools/sheets"], capture_output=True)
        if tar.returncode != 0:
            print(f"git archive {ref} tools/sheets: {tar.stderr.decode()[-400:]}")
            return 1
        with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as t:
            t.extractall(work, filter="data")
        (work / "base_helper.py").write_text(HELPER)
        p = run([PY, "base_helper.py", str(DATA), str(work / "out")], work)
        if p.returncode != 0:
            print(f"the base's tools at {ref} failed on {DATA.name}:\n{p.stdout[-800:]}{p.stderr[-1500:]}")
            return 1
        shutil.copyfile(work / "out" / "sheet.xlsx", BASE_XLSX)
        shutil.copyfile(work / "out" / "base.json", BASE_JSON)
        print(f"wrote {BASE_XLSX.name} and {BASE_JSON.name} from tools/sheets at {ref}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def probe_file(work: Path) -> Path:
    """The data file with a uniform(0, 1) input with no address or mark, read by `u * 2`, on Globals."""
    text = DATA.read_text()
    starts = [m.start() for m in re.finditer(r"(?m)^\[\[tab\]\]\s*$", text)]
    glob = next(i for i, s in enumerate(starts) if re.search(r'(?m)^name = "Globals"', text[s:starts[i + 1] if i + 1 < len(starts) else None]))
    cut = starts[glob + 1]
    block = text[starts[glob]:cut]
    group = 'group = "Probe"\n' if re.search(r"(?m)^group = ", block) else ""
    add = (f'[[tab.column]]\nid = "probe_u"\nname = "Probe number"\n{group}kind = "uniform"\nlo = 0\nhi = 1\n'
           f'citation = "the random number of a probe"\n\n'
           f'[[tab.column]]\nid = "probe_twice"\nname = "Probe twice"\n{group}kind = "calc"\nformula = "probe_u * 2"\n\n')
    p = work / "probe.toml"
    p.write_text(text[:cut] + add + text[cut:])
    return p


def variant_files(work: Path) -> dict[str, Path]:
    """Copies of the data file for the register's rules 2.3, 4.11, 4.12 and 5.4: one more backward reference (a calculation on Globals
    citing a column to its right) without the data file's waiver, and with it, a tab-level `header_notes`, and no `stage`."""
    text = DATA.read_text()
    starts = [m.start() for m in re.finditer(r"(?m)^\[\[tab\]\]\s*$", text)]
    glob = next(i for i, s in enumerate(starts) if re.search(r'(?m)^name = "Globals"', text[s:starts[i + 1] if i + 1 < len(starts) else None]))
    cut = starts[glob + 1]
    group = 'group = "Probe"\n' if re.search(r"(?m)^group = ", text[starts[glob]:cut]) else ""
    add = (f'[[tab.column]]\nid = "probe_back"\nname = "Probe back"\n{group}kind = "calc"\nformula = "probe_next * 2"\n\n'
           f'[[tab.column]]\nid = "probe_next"\nname = "Probe next"\n{group}kind = "uniform"\nlo = 0\nhi = 1\n'
           f'citation = "the random number of a probe https://example.org/probe"\n\n')
    back = text[:cut] + add + text[cut:]
    mil = (f'[[tab.column]]\nid = "probe_mil"\nname = "Probe million ($ Mil)"\n{group}kind = "calc"\nformula = "regional_output*1000"\n'
           f'format = "$"\nunit = "$ million"\n\n')
    out = {
        "factor": text[:cut] + mil + text[cut:],  # the author's own factor beside a column of another unit (R63)
        "flow": re.sub(r"(?m)^backward_references = .*\n", "", back),  # the data file itself carries the waiver, for its Benefits tab reading Costs
        "waiver": back,
        "notes": text.replace('\n[[tab]]\nname = "Benefits"', '\n[tab.header_notes]\nA = "a tab-level note"\n\n[[tab]]\nname = "Benefits"', 1),
        "nostage": text.replace('stage = "template"\n', "", 1),
        # a method's column set to a beta (the survey's triangular): its alpha and beta stand in rows 10 and 11, its credence does not
        "rowform": text.replace('kind = "triangular"\nlo = 0.05\npeak = 0.1\nhi = 0.2\n', 'kind = "beta"\nlo = 0.05\nhi = 0.2\nalpha = 2\nbeta = 5\n', 1),
    }
    paths: dict[str, Path] = {}
    for key, body in out.items():
        paths[key] = work / f"{key}.toml"
        paths[key].write_text(body)
    return paths


# one data file and its workbooks -------------------------------------------------------------------------------------

@dataclass
class Num:
    """A number a sheet shows a reader, with the value Sheets shows it from."""
    sheet: str
    r: int
    c: int
    v: float
    fmt: str
    what: str  # set, stat, typical, extreme or table
    run: list[float]  # the values that share its format (the keep rule)
    year: bool = False
    column_tab: bool = True
    literal: bool = False  # the data file gives the column a literal format, which the generator applies as written
    col: str = ""  # a column tab's column id
    unit: float = 1.0  # the unit the shown number is in: its column's source unit x 1,000 ** commas, or its head's unit
    rounded: bool = False  # its cell's formula rounds it to two figures (reading 10), and v is the value it shows

    def test(self, name: str) -> str:
        """The test a failure counts against: a literal format is the data file's fault."""
        return name + " [data file]" if self.literal else name

    @property
    def where(self) -> str:
        return f"{self.sheet} {letter(self.c)}{self.r}"


class Case:
    def __init__(self, label: str, path: Path, book: Book, old: Book, twin: dict[str, Any]) -> None:
        self.label, self.book, self.old, self.twin = label, book, old, twin
        self.tabs: list[dict[str, Any]] = tomllib.loads(path.read_text())["tab"]
        OFFS.clear()
        OFFS.update({str(t["name"]): rows_offset(t) for t in self.tabs if t.get("column")})
        set_rows(0)
        self.kinds: dict[str, str] = {str(t["name"]): str(t.get("kind", "columns")) for t in self.tabs}
        self.data: dict[str, dict[str, dict[str, Any]]] = {str(t["name"]): {str(c["id"]): c for c in t.get("column", [])} for t in self.tabs}
        self.factor: dict[tuple[str, int], float] = {}  # a column's twin value times this is the number its cells hold
        self.columns: dict[str, dict[str, dict[str, Any]]] = {}
        placed_at = {str(t["name"]): layout(t) for t in self.tabs if t.get("column")}
        for sheet, cols in twin["columns"].items():
            self.columns[sheet] = {}
            for col in cols.values():  # keyed by the letter the data file's layout gives (`placed`), not the twin's
                x = letter(placed_at[sheet][str(col["id"])])
                f = self.factor[(sheet, colnum(x))] = self.twin_factor(sheet, x, col)
                self.columns[sheet][x] = col if f == 1 else col | {
                    "stats": [v * f for v in col["stats"]], "typ": col["typ"] * f, "dmin": col["dmin"] * f, "dmax": col["dmax"] * f,
                    "near0": [v * f for v in col["near0"]]}
        self.tables: dict[str, list[tuple[int, int, float]]] = {sheet: [(r, c, v * self.table_factor(sheet, r, c)) for r, c, v in values]
                                                                for sheet, values in twin["tables"].items()}

    def twin_factor(self, sheet: str, x: str, col: dict[str, Any]) -> float:
        """How many of the book's unit one of the twin's makes, for a column (reading 11): the twin gives a column's
        values in the unit its name names in brackets, else its note's first money unit, else, for a number or $
        column, its group's; the book holds them in the unit its heading names. 1 for a column whose heading names
        no money unit, which is not money (its note may name the units of the columns its formula converts). The base's twin is in the data file's units; a twin of the code under test is in
        the book's, and its factor is 1."""
        group = str(self.data.get(sheet, {}).get(str(col["id"]), {}).get("group") or "") if col["format"] in ("number", "$") else ""
        twin = next((u for u in (head_unit(str(col["name"] or "")), money_of(NOTE_MONEY.search(str(col["note"] or ""))),
                                 head_unit(group)) if u is not None), ("USD", 1.0) if col["format"] == "$" else None)
        head = self.book.cells(sheet).get((1, colnum(x)))
        book = head_unit((head.text or "") if head is not None else "")
        if twin is None or not twin[0] or book is None or book[0] != twin[0]:
            return 1.0
        return twin[1] / book[1]

    def table_factor(self, sheet: str, r: int, c: int) -> float:
        """How many of the book's unit one of the twin's makes, for a table's or Sensitivity's cell: the unit its head
        names over its format's trailing commas, in the base's workbook (old) and in the book; 1 where they are one
        or where either head names none."""
        if self.old is self.book:
            return 1.0

        def size(book: Book) -> float | None:
            d = book.cells(sheet).get((r, c))
            unit = unit_of(heads_of_cached(book, sheet).get((r, c), (0, ""))[1])
            return None if unit is None else unit[1] / 1000.0 ** commas_of(book.fmt(d.s) if d is not None else "General")
        old, new = size(self.old), size(self.book)
        return 1.0 if old is None or new is None else old / new  # a rank under a column's name names no unit of its own

    def subheads(self, sheet: str) -> set[tuple[int, int]]:
        """Where a subhead stands (1.5): the Guide's cells showing his template's subheads, a text tab's `## ` cells."""
        if self.kinds.get(sheet) == "guide":
            return {key for key, d in self.book.cells(sheet).items() if d.text in TEMPLATE_SUBHEADS}
        none: list[list[str]] = []
        rows: list[list[str]] = next((t.get("rows", none) for t in self.tabs if t["name"] == sheet and self.kinds.get(sheet) == "text"), none)
        return {(r, c) for r, row in enumerate(rows, start=1) for c, v in enumerate(row, start=1) if v.startswith("## ")}

    def column_tabs(self) -> list[str]:
        return [s for s in self.book.order if self.kinds.get(s) == "columns"]

    def numbers(self) -> list[Num]:
        out: list[Num] = []
        for sheet in self.column_tabs():
            on(sheet)
            cells = self.book.cells(sheet)
            for x, col in self.columns.get(sheet, {}).items():
                n, year, lit = colnum(x), col["format"] == "year", col["format"] not in FOUR
                stats: list[float] = col["stats"]
                cid, head = str(col["id"]), cells.get((1, n))
                unit = head_unit((head.text or "") if head is not None else "")
                size = 1.0 if unit is None else unit[1]

                def at(fmt: str) -> float:  # the unit its heading names (reading 11); a scaled format fails 2.6 apart
                    return size * 1000.0 ** commas_of(fmt)
                for r in range(P1, P7 + 1):
                    d = cells.get((r, n))
                    if d is not None and d.num is not None:
                        f = self.book.fmt(d.s)
                        out.append(Num(sheet, r, n, d.num, f, "set", [d.num], year, literal=lit, col=cid, unit=at(f)))
                for r, v in zip((SLO, SMEAN, SHI), stats):
                    d = cells.get((r, n))
                    if d is not None and math.isfinite(v):
                        f, v = self.book.fmt(d.s), round2(v) if d.rounded else v
                        out.append(Num(sheet, r, n, v, f, "stat", [v], year, literal=lit, col=cid, unit=at(f), rounded=d.rounded))
                d = cells.get((FIRST, n))
                if d is not None:
                    fmt = self.book.fmt(d.s)
                    out.append(Num(sheet, FIRST, n, col["typ"], fmt, "typical", [*stats, col["typ"]], year, literal=lit, col=cid, unit=at(fmt)))
                    out += [Num(sheet, FIRST, n, col[k], fmt, "extreme", [col[k]], year, literal=lit, col=cid, unit=at(fmt))
                            for k in ("dmin", "dmax")]
        for sheet, values in self.tables.items():
            cells = self.book.cells(sheet)
            heads = heads_of(self.book, sheet)
            runs: dict[tuple[int, str, str], list[float]] = {}
            found: list[tuple[int, int, float, str, str]] = []
            rounded: set[tuple[int, int]] = set()
            for r, c, v in values:
                d = cells.get((r, c))
                if d is None or not math.isfinite(v) or (d.f is None and d.num is None):
                    continue
                if d.rounded:
                    v = round2(v)
                    rounded.add((r, c))
                fmt, head = self.book.fmt(d.s), heads.get((r, c), (0, ""))[1]
                if fmt == "General" and v == int(v):
                    continue  # a label, a year
                runs.setdefault((c, fmt, head), []).append(v)
                found.append((r, c, v, fmt, head))
            out += [Num(sheet, r, c, v, fmt, "table", runs[(c, fmt, head)], column_tab=False, unit=(unit_of(head) or ("", 1.0))[1],
                        rounded=(r, c) in rounded) for r, c, v, fmt, head in found]
        return out


HEADS: dict[tuple[int, str], dict[tuple[int, int], tuple[int, str]]] = {}


def heads_of_cached(book: Book, sheet: str) -> dict[tuple[int, int], tuple[int, str]]:
    """`heads_of`, worked out once a book and tab."""
    key = (id(book), sheet)
    if key not in HEADS:
        HEADS[key] = heads_of(book, sheet)
    return HEADS[key]


def heads_of(book: Book, sheet: str) -> dict[tuple[int, int], tuple[int, str]]:
    """For each cell, the nearest text above it in its column (its row, its text)."""
    cells = book.cells(sheet)
    out: dict[tuple[int, int], tuple[int, str]] = {}
    cols: dict[int, list[int]] = {}
    for r, c in cells:
        cols.setdefault(c, []).append(r)
    for c, rows in cols.items():
        last: tuple[int, str] | None = None
        for r in sorted(rows):
            d = cells[(r, c)]
            if d.text:
                last = (r, d.text)
            elif last is not None:
                out[(r, c)] = last
    return out


def title_place(kind: str | None, r: int, c: int) -> bool:
    """Where a tab's kind puts a title: a column tab's or table's A1, Sensitivity's B1, any heading of a guide or text tab."""
    if kind in ("guide", "text"):
        return True  # a heading, in column A or over the Useful References
    return (r, c) == ((1, 2) if kind == "sensitivity" else (1, 1))


def is_input(col: dict[str, Any]) -> bool:
    return str(col["kind"]) in KINDS7


SETTINGS = {"mean": 5, "sd": 6, "lo": 7, "peak": 8, "hi": 9, "alpha": 10, "beta": 11}  # an input's settings, by the row they stand in


def row_form(t: dict[str, Any]) -> set[str]:
    """The groups of a tab's methods in the row form, read from the data file by the rule of the docs: a method whose group is
    one column carries no label column, its credence in its own column in the inserted Credence row, its cumulative share in
    the row under it."""
    cols = list(t.get("column", []))
    return {str(m["group"]) for m in t.get("method", []) if sum(c.get("group") == m["group"] for c in cols) == 1}


def rows_offset(t: dict[str, Any]) -> int:
    """The rows a column tab has above the template's: INSERTED where it has a method of one column, else none (the owner,
    2026-11-21, R64: "we just pointed each one at teh first row and copied down")."""
    return INSERTED if row_form(t) else 0


def pick_sets(t: dict[str, Any]) -> list[tuple[set[str], set[str]]]:
    """Each pick's set, read from the data file by the rule of the docs, as the groups of its methods and the groups of its
    own columns: a pick column's formula cites CREDENCE(id) or CUMSHARE(id); its methods are those it cites and those whose
    columns it reads (a short pick's last method, its else, is cited by none); pick columns of the same methods are one set."""
    cols = list(t.get("column", []))
    group_of = {str(m["id"]): str(m["group"]) for m in t.get("method", [])}
    method_of = {g: m for m, g in group_of.items()}
    sets: dict[frozenset[str], set[str]] = {}
    for c in cols:
        f = str(c.get("formula", ""))
        cited = set(re.findall(r"\b(?:CUMSHARE|CREDENCE)\((\w+)\)", f))
        if not cited or c.get("group") is None:
            continue
        read = {method_of[str(x["group"])] for x in cols if str(x.get("group")) in method_of
                and re.search(rf"(?<![\w!']){re.escape(str(x['id']))}(?!\w)", f)}
        sets.setdefault(frozenset(cited | read), set()).add(str(c["group"]))
    return [({group_of[m] for m in ms} - own, own) for ms, own in sets.items()]


def placed(t: dict[str, Any]) -> tuple[dict[str, int], dict[str, int], dict[str, str]]:
    """The column number of each column id of a tab and of each group's label column, as the data file's groups lay them
    out, and the group whose tint each group takes: a label column just before each group but the ones in the row form,
    a pick's own group's (its title) just before the first column of its set, a method block's label column included;
    every group of one pick's set takes one tint (the owner, 2026-11-21, R64)."""
    cols = list(t.get("column", []))
    rowed = row_form(t)
    first: dict[str, int] = {}
    for i, c in enumerate(cols):
        if c.get("group") is not None:
            first.setdefault(str(c["group"]), i)
    anchor, turn = dict(first), {g: g for g in first}
    for methods, own in pick_sets(t):
        lead = min(methods | own, key=lambda g: first[g])
        anchor.update({g: first[lead] for g in own})
        turn.update({g: lead for g in methods | own})
    labelled = sorted((g for g in first if g not in rowed), key=lambda g: (anchor[g], anchor[g] == first[g]))
    columns: dict[str, int] = {}
    labels: dict[str, int] = {}
    n = 2
    for i, c in enumerate(cols):
        for g in (g for g in labelled if anchor[g] == i):
            labels[g] = n
            n += 1
        columns[str(c["id"])] = n
        n += 1
    return columns, labels, turn


def layout(t: dict[str, Any]) -> dict[str, int]:
    """The column number of each column id of a tab (`placed`)."""
    return placed(t)[0]


def clipped(k: Case, sheet: str, r: int, c: int) -> bool:
    """Whether the text of a header cell is wider than its column (it does not wrap, and its neighbour holds a value)."""
    d = k.book.cells(sheet).get((r, c))
    if d is None or not d.text or k.book.style(d.s).wrap:
        return False
    f = k.book.font(d.s)
    return len(d.text) * CHAR_PX * f.size / 10 * (1.1 if f.bold else 1) + PAD_PX > k.book.sheets[sheet].width(c, TABLE_PX) + 0.5


def picks(case: Case, sheet: str) -> dict[str, str]:
    """A tab's picks: each calculation that compares a uniform(0, 1) input of its tab, and that input's id."""
    cols = case.data.get(sheet, {})
    units = [i for i, c in cols.items() if c.get("kind") == "uniform" and (c.get("lo"), c.get("hi")) == (0, 1)]
    out: dict[str, str] = {}
    for i, c in cols.items():
        f = str(c.get("formula") or "")
        for u in units:
            if re.search(rf"(?<![\w!]){re.escape(u)}\s*(<=|>=|<|>)|(<=|>=|<|>)\s*{re.escape(u)}(?!\w)", f):
                out[i] = u
    return out


# 1 type and colour ---------------------------------------------------------------------------------------------------

def t_face(k: Case) -> None:
    name = test("1.1 one face and size")
    for sheet in k.book.order:
        on(sheet)
        kind = k.kinds.get(sheet)
        for (r, c), d in k.book.view(sheet).items():
            f = k.book.font(d.s)
            if f.name != "Arial":
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: font {f.name!r}, not Arial")
            elif f.size != 10 and not (f.bold and f.size > 10 and title_place(kind, r, c)):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: {f.size:g} pt{' bold' if f.bold else ''}; every cell 10 but a tab's title, bold and larger")


def t_bold(k: Case) -> None:
    name = test("1.2 bold only where it marks")
    for sheet in k.book.order:
        on(sheet)
        kind = k.kinds.get(sheet)
        cells = k.book.view(sheet)
        if kind == "columns":
            data = k.columns.get(sheet, {})
            for (r, c), d in cells.items():
                if r > CITE or c == 1 or not k.book.font(d.s).bold:
                    continue
                col = data.get(letter(c))
                label = col is None and k.book.fill(d.s) == LABEL_FILL
                result = col is not None and bool(k.data.get(sheet, {}).get(col["id"], {}).get("result", False))
                if r in range(2, CITE + 1) or not (label or result):
                    fail(name, f"{k.label} {sheet} {letter(c)}{r} is bold: on a column tab only a result's name and a category label are")
            for x, col in data.items():
                d = cells.get((1, colnum(x)))
                if k.data.get(sheet, {}).get(col["id"], {}).get("result", False) and (d is None or not k.book.font(d.s).bold):
                    fail(name, f"{k.label} {sheet} {x}1: a result's name is not bold")
        else:
            subheads = k.subheads(sheet)
            for (r, c), d in cells.items():
                f = k.book.font(d.s)
                if f.bold and (d.text or d.f) and not (f.size > 10 and title_place(kind, r, c)) and not (f.size == 10 and (r, c) in subheads):
                    fail(name, f"{k.label} {sheet} {letter(c)}{r}: bold at {f.size:g} pt; on a tab without columns only a title is bold and larger, or a subhead bold at 10 (1.5)")


def t_link_colours(k: Case) -> None:
    name = test("1.3 links and inputs in their blues")
    for sheet in k.book.order:
        on(sheet)
        cells = k.book.view(sheet)
        for (r, c), d in cells.items():
            if d.f is None:
                continue
            f = k.book.font(d.s)
            if kind_of(d.f, sheet) == "link" and (f.colour != LINK_BLUE or not f.under):
                fail(name, f"{k.label} {sheet} {letter(c)}{r} is a link, coloured {f.colour}{' underlined' if f.under else ''}, not {LINK_BLUE} underlined")
            if f.colour == INPUT_BLUE:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a formula in input blue")
        if k.kinds.get(sheet) == "columns":
            data = k.columns.get(sheet, {})
            for (r, c), d in cells.items():
                col = data.get(letter(c))
                credence = (col is None and r == P1 and d.num is not None and c > 1) or (col is not None and r == CRED and d.num is not None)
                if (credence or (col is not None and is_input(col) and KIND <= r <= P7)) and (d.text or d.num is not None):
                    f = k.book.font(d.s)
                    if f.colour != INPUT_BLUE or f.under:
                        fail(name, f"{k.label} {sheet} {letter(c)}{r}: a value a person sets, coloured {f.colour}{' underlined' if f.under else ''}, not input blue")
    seen: dict[str, str] = {}
    for (_, c), d in k.book.cells("Guide").items():
        if c == 1 and d.text in KEY_SAMPLES:
            seen[d.text] = k.book.font(d.s).colour
    green = any(k.book.font(d.s).colour == GREEN for sheet in k.book.order if sheet != "Guide" for d in k.book.view(sheet).values())
    for sample, colour in KEY_SAMPLES.items():
        if (colour != GREEN or green) and seen.get(sample) != colour:
            fail(name, f"{k.label} Guide: the colour key's sample {sample!r} is {seen.get(sample, 'missing')}, not {colour}")


def t_green(k: Case) -> None:
    name = test("1.4 green marks a carried value")
    book = k.book
    stats_rows = plains = cross_calcs = 0
    greens_static: list[tuple[int, int]] = []
    for sheet in book.order:
        on(sheet)
        col_tab = k.kinds.get(sheet) == "columns"
        for (r, c), d in book.view(sheet).items():
            f, colour, where = d.f, book.font(d.s).colour, f"{k.label} {sheet} {letter(c)}{r}"
            if f is not None:
                kd = kind_of(f, sheet)
                stats_rows += col_tab and r in (SLO, SHI)
                if kd == "plain":
                    plains += 1
                    if colour != GREEN:
                        fail(name, f"{where} ={f[:60]} is a plain reference to another tab, coloured {colour}, not green")
                elif kd == "lookup":
                    if colour not in (GREEN, BLACK):
                        fail(name, f"{where} is a lookup reading another tab, coloured {colour}")
                elif kd != "link":
                    cross_calcs += kd == "other" and any(unquote(x.group(1)) != sheet for x in PLAIN.finditer(f))
                    if colour != BLACK:
                        fail(name, f"{where} ={f[:70]} computes, coloured {colour}, not black")
            elif colour == GREEN:
                if sheet == "Guide":
                    greens_static.append((r, c))
                else:
                    fail(name, f"{where} holds no formula and is green")
    if stats_rows == 0 or cross_calcs == 0:
        fail(name, f"{k.label}: no formula in rows {SLO} and {SHI}, or none reading another tab: the test cannot see them")
    guide = book.cells("Guide")
    for r, c in greens_static:
        named: list[tuple[str, str]] = []
        for (r2, _), d in guide.items():
            if r2 == r:
                for src in ([d.f] if d.f and kind_of(d.f, "Guide") == "plain" else []) + ([d.text] if d.text and d.f is None else []):
                    named += refs_in(src, book.order)
        for loc in book.sheets["Guide"].links.get(r, []):
            named += refs_in(loc.lstrip("#"), book.order)
        good = False
        for tab, ref in named:
            mm = re.fullmatch(r"([A-Z]+)(\d+)", ref)
            target = book.cells(tab).get((int(mm.group(2)), colnum(mm.group(1)))) if mm else None
            if target is not None and target.f is not None and kind_of(target.f, tab) == "plain" and book.font(target.s).colour == GREEN:
                good = True
        if not good:
            fail(name, f"{k.label} Guide {letter(c)}{r} is green with no formula, and its row names no real link cell: {named or 'none'}")
    if plains and not any(book.font(d.s).colour == GREEN for d in guide.values()):
        fail(name, f"{k.label}: the workbook holds links to other tabs, but the Guide's colour key shows no green")
    for (r, c), d in guide.items():
        text = d.text or ""
        for p in OLD:
            if re.search(p, text, re.I):
                fail(name, f"{k.label} Guide {letter(c)}{r} states the old rule: {text[:120]!r}")
        if re.search(r"(black|formula)[^.]{0,60}\bits own tab", text, re.I):
            fail(name, f"{k.label} Guide {letter(c)}{r} restricts black to a formula of its own tab: {text[:120]!r}")


# 1.5's import: an export of a Readme and two text tabs, each with a bold 16 head, a bold 10 subhead, a paragraph, a link
# (an inserted link in one, a =HYPERLINK formula in the other) and its own widths, as Google writes them.
@dataclass(frozen=True)
class TextTab:
    cells: dict[str, tuple[str, int]]  # cell: text, style (0 a wrapped paragraph, 1 bold 16, 2 bold 10, 4 a plain 11 pt paragraph, body text all the same)
    link: tuple[str, str, str, bool] | None  # cell, text, address, written as =HYPERLINK
    widths: dict[int, int]  # px by column


TEXT_TABS: dict[str, TextTab] = {
    "Sources": TextTab({"A1": ("Where the numbers come from", 1), "A2": ("Checked sources", 2),
                        "B2": ("Each input was read against its source before the model used it, and the reading is kept with it.", 0)},
                       ("A3", "Statistics portal", "https://example.org/stats", False), {1: 400, 2: 220}),
    "Method": TextTab({"A1": ("How the model works", 1), "B1": ("In brief", 2),
                       "A2": ("Two estimates are pooled by credence, and each year's net benefit is discounted to the base year.", 0),
                       "A4": ("Written at 11 pt under the old size rule, it is a paragraph, not a heading.", 4)},
                      ("B3", "Method note", "https://example.org/method", True), {1: 310, 2: 260}),
}
TEXT_SHEETS = [("Readme", TextTab({"A1": ("Overview", 1), "A2": ("A test of the importer's text tabs.", 0)}, None, {})), *TEXT_TABS.items()]


def text_export(path: Path) -> None:
    fonts = '<font><sz val="10"/><name val="Arial"/></font><font><b/><sz val="16"/><name val="Arial"/></font>' \
            '<font><b/><sz val="10"/><name val="Arial"/></font><font><u/><sz val="10"/><color rgb="FF1155CC"/><name val="Arial"/></font>' \
            '<font><sz val="11"/><name val="Arial"/></font>'
    xfs = '<xf fontId="0"><alignment wrapText="1"/></xf><xf fontId="1"/><xf fontId="2"/><xf fontId="3"/><xf fontId="4"><alignment wrapText="1"/></xf>'  # style = font
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/styles.xml", f'<styleSheet xmlns="{NS}"><fonts>{fonts}</fonts><cellXfs>{xfs}</cellXfs></styleSheet>')
        z.writestr("xl/workbook.xml", f'<workbook xmlns="{NS}" xmlns:r="{R[1:-1]}"><sheets>'
                   + "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(TEXT_SHEETS, 1)) + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(TEXT_SHEETS) + 1)) + "</Relationships>")
        for i, (_, t) in enumerate(TEXT_SHEETS, 1):
            cells = [(ref, f'<c r="{ref}" s="{st}" t="inlineStr"><is><t>{text}</t></is></c>') for ref, (text, st) in t.cells.items()]
            extra = ""
            if t.link:
                ref, text, url, formula = t.link
                cells.append((ref, f'<c r="{ref}" s="3" t="str"><f>HYPERLINK("{url}","{text}")</f><v>{text}</v></c>' if formula
                              else f'<c r="{ref}" s="3" t="inlineStr"><is><t>{text}</t></is></c>'))
                if not formula:
                    extra = f'<hyperlinks><hyperlink ref="{ref}" r:id="rL"/></hyperlinks>'
                    z.writestr(f"xl/worksheets/_rels/sheet{i}.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                               f'<Relationship Id="rL" Target="{url}" TargetMode="External"/></Relationships>')
            rows: dict[int, list[tuple[int, str]]] = {}
            for ref, xml in cells:
                m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
                assert m
                rows.setdefault(int(m.group(2)), []).append((colnum(m.group(1)), xml))
            cols = "".join(f'<col min="{c}" max="{c}" width="{px / 7}"/>' for c, px in t.widths.items())
            z.writestr(f"xl/worksheets/sheet{i}.xml", f'<worksheet xmlns="{NS}" xmlns:r="{R[1:-1]}">' + (f"<cols>{cols}</cols>" if cols else "")
                       + "<sheetData>" + "".join(f'<row r="{r}">' + "".join(x for _, x in sorted(cs)) + "</row>" for r, cs in sorted(rows.items()))
                       + "</sheetData>" + extra + "</worksheet>")


def text_round_trip(work: Path) -> subprocess.CompletedProcess[str]:
    text_export(work / "text_export.xlsx")
    p = run([PY, "-m", "tools.sheets.importer", "import", str(work / "text_export.xlsx"), "--out", str(work / "text_import")], ROOT)
    if p.returncode != 0:
        return p
    return run([PY, "-m", "tools.sheets.script", "generate", str(work / "text_import" / "sheet.toml"), "--out", str(work / "text_gen")], ROOT)


SEAT_QUOTED = re.compile(r'"[^"]*" \[the seat\'s text; its green superseded by register 1\.4\]')  # a quoted superseded rule, marked so


def live_lines() -> list[tuple[str, int, str]]:
    """Each line of the rules' live homes (reading 8): RULE_FILES, less the standard's register (its part 1)."""
    out: list[tuple[str, int, str]] = []
    for rel in RULE_FILES:
        path = ROOT / rel
        if not path.exists():
            fail("8.5 superseded rules left out", f"{rel} is missing")
            continue
        register = False
        for n, line in enumerate(path.read_text().splitlines(), start=1):
            if rel == STANDARD and line.startswith("## Part "):
                register = line.startswith("## Part 1")
            if not register:
                out.append((rel, n, SEAT_QUOTED.sub("", line)))
    return out


def t_old_copies(lines: list[tuple[str, int, str]]) -> None:
    name = test("1.4 green marks a carried value")
    for rel, n, line in lines:
        for p in OLD:
            if re.search(p, line, re.I):
                fail(name, f"{rel}:{n} states the old green rule: {line[:200]}")


# 2 numbers -----------------------------------------------------------------------------------------------------------

def t_unit_formats(k: Case) -> None:
    name = test("2.1 every number its unit's format")
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for x, col in k.columns.get(sheet, {}).items():
            d = cells.get((SMEAN, colnum(x)))
            if d is None:
                continue
            fmt, kind = k.book.fmt(d.s), col["format"]
            if (kind == "%" and "%" not in fmt) or (kind == "$" and "$" not in fmt) or (kind == "year" and fmt != "0"):
                fail(name, f"{k.label} {sheet} {x}{SMEAN} ({col['id']}): format {kind!r} shown as {fmt!r}")
    for sheet, values in k.tables.items():
        on(sheet)
        cells = k.book.cells(sheet)
        heads = heads_of(k.book, sheet)
        for r, c, v in values:
            d = cells.get((r, c))
            if d is None or (d.f is None and d.num is None):
                continue
            fmt = k.book.fmt(d.s)
            general = fmt == "General" and len(f"{abs(v):.15g}".replace(".", "").strip("0")) > 2
            if general and not (d.f is None and v == int(v)) and not (d.f or "").startswith("RANK.AVG("):  # a label; a draw's rank
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: {v!r} is left at General with more than two significant figures")
            if re.search(r"\bratio\b", heads.get((r, c), (0, ""))[1], re.I) and "$" in fmt:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a ratio shown with '$' ({fmt!r})")


def t_figures(k: Case, numbers: list[Num]) -> None:
    name = test("2.2 two figures")
    for n in numbers:
        if n.what == "extreme" or n.year:
            continue
        got, nm = render(n.fmt, n.v), n.test(name)
        if got is None:
            fail(nm, f"{k.label} {n.where}: number format {n.fmt!r} is outside the grammar this suite reads")
            continue
        if math.isnan(got.shown):
            fail(nm, f"{k.label} {n.where}: {n.v!r} shows as {got.text[1:]!r}, a negative number without its sign")
            continue
        if n.v < 0 and not re.search(r"[1-9]", got.text) and re.search(r"[-(]", got.text):
            fail(nm, f"{k.label} {n.where}: {n.v!r} shows a minus with a zero, {got.text!r}")
        if n.what == "table" and "%" in n.fmt and 0 < n.v < 1 and (got.shown * got.scale in (0.0, 1.0)
                                                                 or abs(got.shown * got.scale - n.v) > 0.5 * unit2(min(n.v, 1 - n.v)) * (1 + 1e-9)):
            fail(nm, f"{k.label} {n.where}: {n.v!r} shows as {got.text!r}; a share keeps two figures of min(p, 1 - p), never 0% or 100%")
        if n.what == "table" and "%" in n.fmt and 0 < n.v < 1 and (m := re.search(r"\.(0+)", n.fmt)) is not None and len(m.group(1)) > 1:
            fail(nm, f"{k.label} {n.where}: {n.v!r} shows as {got.text!r}; a share never shows more than one decimal of a percent")
        if n.what == "table" and "%" not in n.fmt and n.v != 0 and abs(n.v) == max(abs(x) for x in n.run) \
                and abs(got.shown - n.v / got.scale) > 0.5 * unit2(n.v / got.scale) * (1 + 1e-9):
            fail(nm, f"{k.label} {n.where}: the run's largest, {n.v!r}, shows as {got.text!r}, under two significant figures")
        figs = figures(got, "%" in n.fmt)
        if figs is not None and n.rounded and got.step >= 1:  # a rounded value's zeros before its point hold places (reading 10)
            whole = round(abs(got.shown) / got.step)
            while figs > 1 and whole and whole % 10 == 0:
                whole, figs = whole // 10, figs - 1
        if figs is None or figs <= 2:
            continue
        if n.column_tab and not got.scaled and got.step >= 1 and 100 <= abs(got.shown) < SCI_FROM:
            continue  # a whole number from 100 to 9,999, unscaled, on a column tab (reading 3)
        if n.unit == TOP and got.step >= 1 and 99.5 <= abs(got.shown):
            continue  # a whole number of trillions of 100 or more: no unit above it (reading 4)
        if keeps(n.fmt, n.run):
            continue
        fail(nm, f"{k.label} {n.where} ({n.what}): {n.v:.6g} shows as {got.text!r} (format {n.fmt!r}), {figs} significant figures")
    read = read_cells(k.book)  # reading 10: a terminal number is rounded by its formula; a number a formula reads is not
    for sheet in k.book.order:
        on(sheet)
        for (r, c), d in k.book.cells(sheet).items():
            fmt = k.book.fmt(d.s)
            if d.rounded and reads(read, sheet, r, c):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: rounded to two figures by its formula, but a formula reads it")
            if d.f is None or d.text is not None or d.offset or d.span or fmt == "General" or "%" in fmt or fmt == "0":
                continue  # a number of its own formula, in a number format that is neither a share nor a year
            if not d.rounded and not reads(read, sheet, r, c):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a number no formula reads, not rounded to two figures by its formula")
    for sheet, strings in k.twin["strings"].items():
        on(sheet)
        for r, c, v in strings:
            m = re.fullmatch(r"(-?[\d,.]+) \[(-?[\d,.]+), (-?[\d,.]+)\]", str(v))
            if m is None:
                continue
            for part in m.groups():
                digits = part.replace(",", "").lstrip("-")
                body = digits.replace(".", "").lstrip("0") if "." in digits else digits.lstrip("0").rstrip("0")
                if len(body) > 2:
                    fail(name, f"{k.label} {sheet} {letter(c)}{r}: the interval text {v!r} shows {part} at {len(body)} figures")
    for sheet, cols in k.columns.items():  # values near 1 keep their digits (a "%" between 0 and 0.5 never 0%)
        cells = k.book.cells(sheet)
        for x, col in cols.items():
            if col["format"] not in FOUR:
                continue
            for r, v in zip((SLO, SMEAN, SHI), col["stats"]):
                d = cells.get((r, colnum(x)))
                fmt = "" if d is None else k.book.fmt(d.s)
                v = round2(v) if d is not None and d.rounded else v
                got = None if d is None or not math.isfinite(v) else render(fmt, v)
                if got is None or math.isnan(got.shown):
                    continue
                if (0.5 < abs(v) < 1 and abs(got.shown * got.scale) == 1) or ("%" in fmt and 0 < v < 0.5 and got.shown == 0):
                    fail(name, f"{k.label} {sheet} {x}{r} ({col['id']}): {v!r} shows as {got.text!r}; a value near 0 or 1 keeps its digits")


def t_one_minus(k: Case, numbers: list[Num]) -> None:
    """2.2, its instance of R53 (2026-11-21): every number a sheet shows carries one minus where its value is negative
    and shows a nonzero digit, and none where it shows only zeros (reading 2: a section with a condition shows Sheets'
    own minus, so a "-" written there doubles it, "--0.2"). The values: every typed number, every number the twin gives
    a cell, and each column's statistics, extremes and the draws nearest 0 on each side, which reach every section a
    column's draws can (a section is chosen by an interval of the value, and "-0" first shows nearest 0)."""
    name = test("2.2 one minus")
    for fmt in sorted(set(k.book.codes.values())):
        for sec in sections(fmt):
            c = COND.match(sec)
            if c is not None and "-" in re.sub(r'"[^"]*"|\\.', "", sec[c.end():]):
                fail(name, f"{k.label}: number format {fmt!r} writes a '-' in a section with a condition, where Sheets shows its own")
    values = list(numbers)
    for sheet in k.book.order:
        on(sheet)
        cells, cols = k.book.cells(sheet), k.columns.get(sheet, {})
        # A draw row that repeats row 16 shares its format, read above; a column's draws reach every section through near0
        for (r, c), d in k.book.view(sheet).items():
            col = cols.get(letter(c))
            if d.num is not None:
                values.append(Num(sheet, r, c, d.num, k.book.fmt(d.s), "typed", [], literal=col is not None and col["format"] not in FOUR,
                                  col="" if col is None else str(col["id"])))
        for x, col in cols.items():
            d = cells.get((FIRST, colnum(x)))
            if d is not None:
                values += [Num(sheet, FIRST, colnum(x), v, k.book.fmt(d.s), "draw", [], literal=col["format"] not in FOUR, col=str(col["id"]))
                           for v in col["near0"]]
    for n in values:
        got = render(n.fmt, n.v)
        if got is None:
            continue  # outside reading 2: 2.2 two figures fails it
        text = re.sub(r"E-\d+$", "", got.text)  # a small number's exponent
        want = 1 if n.v < 0 and re.search(r"[1-9]", text) else 0
        if text.startswith("?") or text.count("-") != want:
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): {n.v!r} shows as {text.lstrip('?')!r} in {n.fmt!r}; {want} minus expected")


def t_scaled(k: Case, numbers: list[Num]) -> None:
    name = test("2.3 large numbers in a reasonable unit")
    for n in numbers:
        if n.what == "extreme" or n.year:
            continue
        got = render(n.fmt, n.v)
        if got is None or math.isnan(got.shown):
            continue
        if abs(got.shown) >= 9999.5 and n.unit != TOP and "E" not in got.text:  # the top unit has none above it: its whole numbers may run past four digits (R63)
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): {n.v:.6g} shows as {got.text!r}, five digits or more; a larger unit shows it")
        if n.unit == TOP and abs(got.shown) >= 99.5 and got.step < 1:
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): {got.text!r} trillion shows decimals past two figures; 100 trillion or more shows whole")
        if (got.scaled or n.unit > 1) and abs(got.shown) >= 999.5 and "," not in got.text:
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): {got.text!r} in a unit of thousands or more shows no thousands separators")
        if n.unit > TOP:
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): shown in a unit of {n.unit:.0e}, past trillion")
    # no scale letter in any cell's format, and no unit past trillion named anywhere
    for sheet in k.book.order:
        on(sheet)
        seen: set[int] = set()
        for (r, c), d in k.book.view(sheet).items():
            text = " ".join(x for x in (d.text, d.f) if x)
            m = re.search(r"quadrillion|quintillion", text, re.I)
            if m:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: names a unit past trillion, {m.group(0)!r}: {text[:80]!r}")
            m = FOUR_FIGURE_EXAMPLE.search(d.text or "") if sheet == "Guide" else None
            if m:
                fail(name, f"{k.label} Guide {letter(c)}{r}: shows {m.group(1)} under a {m.group(2)} unit as an example, "
                     f"over two significant figures: {m.group(0)[:80]!r}")
            if (d.num is None and d.f is None) or d.s in seen:
                continue
            seen.add(d.s)
            fmt = k.book.fmt(d.s)
            hit = SCALE_LETTER.search(literals(fmt))
            if hit:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: its format {fmt!r} carries the scale letter {hit.group(0)!r}; the column's name gives the unit in words")
    # a column tab's money column: its heading names its unit in words, and its typical value is 1 to 9,999 there
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for x, col in k.columns.get(sheet, {}).items():
            head = cells.get((1, colnum(x)))
            shown_name = (head.text or "") if head is not None else ""
            if ABBREV.search(" ".join(p for p in re.findall(r"\(([^()]*)\)", shown_name))):
                fail(name, f"{k.label} {sheet} {x}1 ({col['id']}): its name {shown_name!r} gives its unit by an abbreviation, not in words")
            unit = head_unit(shown_name)
            if unit is None or not unit[0] or col["format"] not in ("number", "$"):
                continue
            typical = float(f"{abs(col['typ']):.1e}")
            if unit[1] < TOP and typical >= 9999.5:
                fail(name, f"{k.label} {sheet} {x} ({col['id']}): typical size {col['typ']:.3g} under {shown_name!r}; a larger unit shows it")
            if unit[1] > 1 and typical < 1:
                fail(name, f"{k.label} {sheet} {x} ({col['id']}): typical size {col['typ']:.3g} under {shown_name!r}; a smaller unit shows it")


def t_heading_note_units(k: Case) -> None:
    """2.5 (the owner, 2026-11-21, R63: "the existing sheet has different units in the title and notes"): a column whose
    heading names a money unit in brackets has a note whose first money unit is the same (reading 11)."""
    name = test("2.5 a heading's unit is its note's")
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for x, col in k.columns.get(sheet, {}).items():
            head, note = cells.get((1, colnum(x))), cells.get((NOTE, colnum(x)))
            heading = (head.text or "") if head is not None else ""
            hu = head_unit(heading)
            if hu is None or not hu[0]:
                continue
            nu = money_of(NOTE_MONEY.search((note.text or "") if note is not None else ""))
            if nu != hu:
                fail(name, f"{k.label} {sheet} {x} ({col['id']}): its heading {heading!r} names {hu}, its note's first money unit is {nu}")


CELL = r"(?:(?:'[^']+'|\w+)!)?\$?([A-Z]{1,3})\$?\d+"
FACTOR_AT = re.compile(rf"({CELL})[*/]1(?:000)+(?![\d.eE])|(?<![\w.$])1(?:000)+\*({CELL})")  # a reference with a power of 1,000 beside it


def t_conversions_named(k: Case, label: str = "") -> None:
    """2.3 (R63): every conversion factor a column's formula carries, a power of 1,000 beside a reference to a column,
    is named in that column's note, as "Conversions: N is ₩ trillion, x 1,000 to ₩ billion", the column by its letter
    (Tab!letter on another tab)."""
    name = test("2.3 every conversion factor named in its note")
    label = label or k.label
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for (r, c), f in cells.items():
            if r != FIRST or not f.f:
                continue
            x = letter(c)
            note = cells.get((NOTE, c))
            text = (note.text or "") if note is not None else ""
            said = text.split("Conversions:", 1)[1] if "Conversions:" in text else ""
            for m in FACTOR_AT.finditer(f.f):
                ref = m.group(1) or m.group(3)
                at = re.sub(r"\$?\d+$", "", ref.replace("$", "")).replace("'", "")
                if f"{at} is " not in said:
                    fail(name, f"{label} {sheet} {x}: its formula carries a factor beside {ref}, and its note does not name {at}: {text[:120]!r}")


def scales(fmt: str) -> str | None:
    """Why a number format shows a number other than the one its cell holds, or None (reading 11): a trailing comma, a
    scale letter or word."""
    if fmt in ("General", "@"):
        return None
    for sec in sections(fmt):
        body = re.sub(r'"[^"]*"|\\.|\[[^\]]*\]', "", sec)
        if re.search(r"[0#?](,+)(?![0#?,])", body):
            return "a trailing comma divides by 1,000"
    hit = SCALE_LETTER.search(literals(fmt))
    return None if hit is None else f"the scale letter {hit.group(0)!r}"


def t_no_scaling_format(k: Case) -> None:
    """2.6 (R63: "somehow through horrible black magic the displayed number is much less than the typed number"): no
    number format of the workbook scales the number it shows; a percent's sign declares its factor of 100."""
    name = test("2.6 no format scales a number")
    for fmt in sorted(set(k.book.codes.values())):
        why = scales(fmt)
        if why is not None:
            fail(name, f"{k.label}: number format {fmt!r}: {why}")


def t_typed_shown(k: Case) -> None:
    """2.7 (R63): an input cell a person types into (rows 4 to 11 of a column tab) shows the number typed: the number a
    reader takes from it (a percent read as a share, scientific notation as written) is the typed one, to the
    format's own rounding."""
    name = test("2.7 an input shows what was typed")
    for sheet in k.column_tabs():
        on(sheet)
        for (r, c), d in k.book.cells(sheet).items():
            if not KIND <= r <= P7 or d.num is None or d.f is not None:
                continue
            fmt = k.book.fmt(d.s)
            got = render(fmt, d.num)
            if got is None or math.isnan(got.shown):
                continue  # outside reading 2, or a lost sign: 2.2 fails it
            pct = 100.0 if "%" in fmt else 1.0
            read, half = got.shown / pct, 0.5 * got.step / pct
            if abs(read - d.num) > half * (1 + 1e-9) + 1e-12 * abs(d.num):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: typed {d.num!r}, shown as {got.text!r} by {fmt!r}")


def two_sci(fmt: str) -> bool:
    """Every section of fmt is scientific notation at two figures (0.0E+0)."""
    return all(re.fullmatch(r"[^0#?]*0\.0E\+0+[^0#?]*", re.sub(r'"[^"]*"|\\.|\[[^\]]*\]', "", sec)) for sec in sections(fmt) if sec)


def t_large_scientific(k: Case) -> None:
    """2.8 (the owner, 2026-11-21, R63: "anything not money that is a large number should default to scientific
    notation"): a number column of a column tab whose heading names no currency, and whose typical size is SCI_FROM or
    more, shows its draws and rows 12 to 14 in scientific notation at two figures, as does each typed number of that
    size in its rows 5 to 11. A literal format of the data file is its own and is left out: the rule sets a default."""
    name = test("2.8 a large number that is not money in scientific notation")
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for x, col in k.columns.get(sheet, {}).items():
            head = cells.get((1, colnum(x)))
            unit = head_unit((head.text or "") if head is not None else "")
            if col["format"] != "number" or (unit is not None and unit[0]):
                continue
            n = colnum(x)
            if abs(col["typ"]) >= SCI_FROM:
                for r in (SLO, SMEAN, SHI, FIRST):
                    d = cells.get((r, n))
                    if d is not None and not two_sci(k.book.fmt(d.s)):
                        fail(name, f"{k.label} {sheet} {x}{r} ({col['id']}): typical size {col['typ']:.3g}, not money, format {k.book.fmt(d.s)!r}")
                        break
            for r in range(P1, P7 + 1):
                d = cells.get((r, n))
                if d is not None and d.num is not None and d.f is None and abs(d.num) >= SCI_FROM and not two_sci(k.book.fmt(d.s)):
                    fail(name, f"{k.label} {sheet} {x}{r} ({col['id']}): {d.num!r}, not money, format {k.book.fmt(d.s)!r}")


def t_clipped(k: Case, numbers: list[Num]) -> None:
    name = test("2.4 no number clipped")
    for n in numbers:
        got = render(n.fmt, n.v)
        if got is None:
            continue
        sheet = k.book.sheets[n.sheet]
        px = sheet.width(n.c, TABLE_PX)
        need = len(got.text.lstrip("?")) * CHAR_PX + PAD_PX
        if need > px:
            fail(n.test(name), f"{k.label} {n.where} ({n.what}): {got.text!r} needs {need} px, its column is {px:.0f} px")


def t_units_tables(k: Case) -> None:
    """2.3 on Results and Sensitivity: a head names the unit its run is shown in; a mean and its ends share one."""
    name = test("2.3 large numbers in a reasonable unit")
    new, meta = k.book, k.columns
    for sheet in ("Results", "Sensitivity"):
        on(sheet)
        values: dict[tuple[int, int], float] = {(r, c): v for r, c, v in k.tables.get(sheet, []) if math.isfinite(v)}
        cells = new.cells(sheet)
        heads = heads_of(new, sheet)
        slopes = {c: d.f for (_, c), d in sorted(cells.items(), reverse=True) if d.f and "SLOPE(" in d.f}  # a column's first
        factored = re.compile(PLAIN.pattern + r"(?:([*/])(\d+(?:\.\d+)?))?")
        outputs = sorted((c, m) for (r, c), d in cells.items() if r <= 10 and d.f is not None
                         for m in [factored.fullmatch(d.f)] if m is not None and m.group(3) == str(13 + OFFS.get(unquote(m.group(1)), 0))) if sheet == "Sensitivity" else []

        def factor_of(op: str | None, n: str | None) -> float:
            """How many of the source's unit one of the cell's makes: a trailing /1000 makes it 1,000 (R63)."""
            return 1.0 if n is None else float(n) if op == "/" else 1 / float(n)

        def source_unit(key: tuple[int, int]) -> tuple[str, float] | None:
            f = cells[key].f or ""
            m = factored.fullmatch(f)
            div = 1.0 if m is None else factor_of(m.group(4), m.group(5))
            if m is None and sheet == "Sensitivity" and heads.get(key, (0, ""))[1].startswith("Change"):
                m = next((o for c, o in reversed(outputs) if c <= key[1]), None)
                slope = slopes.get(key[1], "")
                t = re.search(r"\)([*/])(\d+)\)$", slope)
                div = 1.0 if t is None else factor_of(t.group(1), t.group(2))
            if m is None:
                return None
            col = meta.get(unquote(m.group(1)), {}).get(m.group(2))
            if col is None:
                return None
            tab = new.cells(unquote(m.group(1)))
            heading, note = tab.get((1, colnum(m.group(2)))), tab.get((2 + OFFS.get(unquote(m.group(1)), 0), colnum(m.group(2))))  # the unit the book holds it in
            u = unit_of(heading.text if heading is not None else "") or unit_of(note.text if note is not None else "") \
                or (("$", 1.0) if col["format"] == "$" else None)
            return None if u is None else (u[0], u[1] * div)

        runs: list[tuple[int, str, list[tuple[int, float, str]]]] = []
        for (r, c), v in sorted(values.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            d = cells.get((r, c))
            if d is None or (d.f is None and d.num is None):
                continue
            fmt, head = new.fmt(d.s), heads.get((r, c), (0, ""))[1]
            if (fmt == "General" and v == int(v)) or head in ("r", "Rank r", "Key") or (sheet, r, c) == ("Sensitivity", 2, 1):
                continue
            if runs and runs[-1][0] == c and runs[-1][1] == fmt and runs[-1][2][-1][0] == r - 1 and runs[-1][2][-1][2] == head:
                runs[-1][2].append((r, v, head))
            else:
                runs.append((c, fmt, [(r, v, head)]))
        for c, fmt, run_cells in runs:
            head = run_cells[0][2]
            hu = unit_of(head)
            for r, v, _ in run_cells:
                got = render(fmt, v)
                if got is None or math.isnan(got.shown):
                    continue
                su = source_unit((r, c))
                where = f"{k.label} {sheet} {letter(c)}{r}"
                if hu is not None:
                    if su is None:
                        fail(name, f"{where}: its head {head!r} names {hu} but its source column names no money unit")
                        break
                    if su[0] != hu[0] or abs(got.shown * hu[1] - v * su[1]) > (0.5 * got.step * hu[1]) * (1 + 1e-9) + 1e-9 * abs(v * su[1]):
                        fail(name, f"{where}: {got.text!r} under {head!r} is {got.shown * hu[1]:.4g} {hu[0]}, but the value is {v * su[1]:.4g} {su[0]}")
                        break
                elif got.scaled and not re.search(r"[A-Za-z]", got.text):
                    fail(name, f"{where}: shown scaled by its format {fmt!r} under a head that names no unit, {head!r}")
                    break
        texts = {key: d.text for key, d in cells.items() if d.text}
        for (r, c), t in texts.items():
            if re.search(r"\bmean\b", t, re.I) and re.match(r"low end", texts.get((r, c + 1), ""), re.I) and re.match(r"high end", texts.get((r, c + 2), ""), re.I):
                if len({unit_of(texts[(r, c + j)]) for j in range(3)}) > 1:
                    fail(name, f"{k.label} {sheet} row {r}: a mean and its ends name different units: {[texts[(r, c + j)] for j in range(3)]}")
        if sheet == "Sensitivity":
            top = min((r for (r, _), t in texts.items() if t.startswith("Change")), default=0)
            for (r, c), t in texts.items():
                u = unit_of(t)
                if r >= top or u is None or re.match(r"(mean|low end|high end)\b", t, re.I):
                    continue
                means = sorted((cc - c, rr) for (rr, cc), tt in texts.items() if r <= rr <= r + 3 and c <= cc <= c + 8 and re.match(r"mean\b", tt, re.I))
                if means and unit_of(texts[(means[0][1], c + means[0][0])]) != u:
                    fail(name, f"{k.label} Sensitivity {letter(c)}{r}: {t[:70]!r} names {u}, but its block's mean head names another unit")


# 3 widths, heights and the grid --------------------------------------------------------------------------------------

def last_column(k: Case, sheet: str) -> int:
    return max((colnum(x) for x in k.columns.get(sheet, {})), default=1)


def t_widths(k: Case) -> None:
    name = test("3.1 narrow columns")
    for sheet in k.column_tabs():
        on(sheet)
        sh = k.book.sheets[sheet]
        for c in range(1, last_column(k, sheet) + 13):
            want = 120 if c == 1 else 70
            if abs(sh.width(c, 0) - want) > 0.5:
                fail(name, f"{k.label} {sheet} column {letter(c)} is {sh.width(c, 0):.0f} px, not {want}")


def t_heights(k: Case) -> None:
    name = test("3.2 header fits a laptop")
    for sheet in k.column_tabs():
        on(sheet)
        want = {1: 69, **dict.fromkeys(range(2, 2 + OFF), 19), NOTE: 56, CITE: 54, **dict.fromkeys(range(KIND, GRAPH), 19), GRAPH: 67}
        h = k.book.sheets[sheet].heights
        for r in range(1, LAST + 1):
            if abs(h.get(r, -1) - want.get(r, 21)) > 0.5:
                fail(name, f"{k.label} {sheet} row {r} is {h.get(r, -1):.0f} px, not {want.get(r, 21)}")


def lines(text: str, px: float, size: float, bold: bool) -> int:
    per = CHAR_PX * size / 10 * (1.1 if bold else 1)
    return max(1, math.ceil(len(text) * per / max(px - PAD_PX, 1)))


def t_text_fits(k: Case) -> None:
    name = test("3.3 text read in place")
    for sheet in k.book.order:
        on(sheet)
        sh, kind = k.book.sheets[sheet], k.kinds.get(sheet)
        cells = sh.view
        if sh.merges:
            fail(name, f"{k.label} {sheet}: {sh.merges} merged cells; widen the column instead")
        need: dict[int, float] = {}
        for (r, c), d in cells.items():
            if not d.text or (kind == "columns" and r < FIRST) or (d.f is not None and d.f.startswith("HYPERLINK(")):
                continue
            st, f = k.book.style(d.s), k.book.font(d.s)
            px = sh.width(c, TABLE_PX)
            n = lines(d.text, px, f.size, f.bold) if st.wrap else 1
            if st.wrap and px < 150 and (n > 5 or (kind == "table" and n > 2)):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: {n} lines in a {px:.0f} px column; widen it")
            longest = max((len(w) for w in d.text.split()), default=0)
            if st.wrap and longest * CHAR_PX * f.size / 10 * (1.1 if f.bold else 1) + PAD_PX > px + 0.5:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a word of {longest} characters is wider than its {px:.0f} px column")
            line = 15 if f.size <= 10 else f.size * 4 / 3
            need[r] = max(need.get(r, 0.0), max(21.0, n * line + 6))
        for r, px in need.items():
            if sh.heights.get(r, 0) < px - 0.5:
                fail(name, f"{k.label} {sheet} row {r} is {sh.heights.get(r, 0):.0f} px; its text needs {px:.0f}")


def t_spare(k: Case) -> None:
    name = test("3.4 twelve spare columns")
    for sheet in k.column_tabs():
        on(sheet)
        cells, last = k.book.view(sheet), last_column(k, sheet)
        for c in range(last + 1, last + 13):
            d = cells.get((CITE, c))
            if d is None or d.text or d.f or d.num is not None:
                fail(name, f"{k.label} {sheet} {letter(c)}{CITE}: a spare column after the last ({letter(last)}) is missing or not empty")
        if any(c > last + 12 for _, c in cells):
            fail(name, f"{k.label} {sheet}: cells past the twelve spare columns")


def t_borders(k: Case) -> None:
    name = test("3.5 light gray lines")
    for sheet in k.column_tabs():
        on(sheet)
        for (r, c), d in k.book.view(sheet).items():
            if (r < CITE and r not in (CRED, SHARE)) or (c == 1 and r < KIND and r not in (CRED, SHARE)):
                continue
            i = k.book.style(d.s).border
            sides = k.book.borders[i] if i < len(k.book.borders) else None
            if sides != {LINE}:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: borders {sides}, not all four #{LINE}")


def t_align(k: Case) -> None:
    name = test("3.6 min left, mean centred, max right")
    for sheet in k.column_tabs():
        on(sheet)
        want = {tr(4): "left", tr(7): "left", tr(8): "center", tr(9): "right", SLO: "left", SMEAN: "center", SHI: "right"}
        cells = k.book.cells(sheet)
        for x in k.columns.get(sheet, {}):
            for r, h in want.items():
                d = cells.get((r, colnum(x)))
                if d is not None and k.book.style(d.s).h != h:
                    fail(name, f"{k.label} {sheet} {x}{r}: aligned {k.book.style(d.s).h}, not {h}")
    for sheet in (s for s in k.twin["tables"] if k.kinds.get(s) == "table"):
        on(sheet)
        for (r, c), d in k.book.cells(sheet).items():
            h = k.book.style(d.s).h
            number = d.num is not None or (d.f is not None and d.text is None and not d.f.startswith("HYPERLINK("))
            if number and h != "right":
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a number aligned {h}, not right")
            elif d.text and d.f is None and h not in ("left", None) and not ((r + 1, c) in k.book.cells(sheet) and h == "right"):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a text aligned {h}, not left")


def t_frozen(k: Case) -> None:
    name = test("3.7 row 1 and column A frozen")
    for sheet in k.column_tabs():
        on(sheet)
        if k.book.sheets[sheet].pane != ("1", "1", "frozen"):
            fail(name, f"{k.label} {sheet}: pane {k.book.sheets[sheet].pane}, not row 1 and column A frozen")


def t_look_snapshot() -> None:
    name = test("3.8 the look stays put")
    for key, want in LOOK_SNAPSHOT.items():
        got: object = getattr(ss, key, None)
        if got != want:
            fail(name, f"tools/sheets/script.py {key} is {got!r}, not the template's {want!r}; change it only where a brief names it, with this snapshot")


# 4 header rows, the guide and labels ---------------------------------------------------------------------------------

def t_one_purpose(k: Case) -> None:
    name = test("4.1 one row one purpose")
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        a = {r: cells[(r, 1)] for r in range(1, GRAPH) if (r, 1) in cells}
        if len((a[1].text or "") if 1 in a else "") > 45:
            fail(name, f"{k.label} {sheet} A1 is over 45 characters")
        for r, t in ((tr(7), "Set: min"), (tr(8), "Set: mode"), (tr(9), "Set: max"), (SMEAN, "Draws: mean")):
            if r not in a or a[r].text != t:
                fail(name, f"{k.label} {sheet} A{r} is {None if r not in a else a[r].text!r}, not {t!r}")
        if SLO not in a or "(1-" not in (a[SLO].f or "") or SHI not in a or "(1+" not in (a[SHI].f or ""):
            fail(name, f"{k.label} {sheet} A{SLO} and A{SHI} do not name the low and high ends")
        for x, col in k.columns.get(sheet, {}).items():
            d = cells.get((CITE, colnum(x)))
            if is_input(col):
                if d is not None and d.f is None and "http" in (d.text or ""):
                    fail(name, f"{k.label} {sheet} {x}{CITE}: an input's citation holds an address as text, not a link")
            elif d is None or not (d.f or "").startswith("REGEXREPLACE(FORMULATEXT("):
                fail(name, f"{k.label} {sheet} {x}{CITE}: a calculation's source row is not its formula without row numbers")


def t_notes(k: Case) -> None:
    name = test("4.2 notes")
    for sheet, cols in k.data.items():
        on(sheet)
        cells = k.book.cells(sheet)
        letters = {col["id"]: x for x, col in k.columns.get(sheet, {}).items()}
        for i, c in cols.items():
            note, cname = str(c.get("note", "")), str(c.get("name", ""))
            if note.startswith(("=", "Read from")) or (note and note == cname):
                fail(name, f"{k.label} {sheet} {i}: a note that repeats or reads: {note[:60]!r}")
            named, said = unit_of(cname), re.search(r"\bin ([₩$€£¥]) ?(thousand|million|billion|trillion)\b", note)
            if named is not None and said is not None and (said.group(1), UNIT_SIZE[said.group(2)]) != named:
                fail(name, f"{k.label} {sheet} {i}: its name says {named}, its note 'in {said.group(1)} {said.group(2)}'")
            d = cells.get((SMEAN, colnum(letters[i]))) if i in letters else None
            if named is not None and named[1] != 1 and d is not None:
                got = render(k.book.fmt(d.s), 1.0)
                if got is not None and got.scaled and re.search(r"[₩$€£¥]", got.text):
                    fail(name, f"{k.label} {sheet} {letters[i]} ({i}): its name {cname!r} names a unit, and its format "
                         f"{k.book.fmt(d.s)!r} puts a currency before a scaled number, so the two name different units")


def t_csv_quoting(k: Case) -> None:
    """4.10: no cell's text and no note is a source's CSV quoting, a text that begins and ends with '"' and holds '""'."""
    name = test("4.10 no CSV quoting")
    quoted = re.compile(r'^".*"".*"$', re.S)
    for sheet in k.book.order:
        on(sheet)
        sh = k.book.sheets[sheet]
        texts = [(f"{letter(c)}{r}", d.text) for (r, c), d in sh.view.items() if d.text is not None]  # view keeps every text
        for where, text in texts + [(f"{ref}'s note", note) for ref, note in sh.notes.items()]:
            if quoted.match(text):
                fail(name, f"{k.label} {sheet} {where}: {text[:80]!r} carries a source's CSV quoting")


def t_citations(k: Case) -> None:
    name = test("4.3 every source a link")
    for sheet in k.column_tabs():
        on(sheet)
        cells, chosen = k.book.cells(sheet), set(picks(k, sheet).values())
        for x, col in k.columns.get(sheet, {}).items():
            if not is_input(col) or col["id"] in chosen:
                continue
            d = cells.get((CITE, colnum(x)))
            if d is None or not ((d.f or "").startswith("HYPERLINK(") or (d.text or "").startswith(MARKS)):
                fail(name, f"{k.label} {sheet} {x}{CITE} ({col['id']}): an input's citation neither a link nor marked")


def t_guide_short(k: Case) -> None:
    name = test("4.4 guide short")
    g = k.tabs[0]
    words = sum(len(str(g.get(key, "")).split()) for key in ("what", "start_here", "general_form", "details"))
    words += sum(len(str(b).split()) for key in ("notes", "tabs") for _, b in g.get(key, []))
    if words > GUIDE_WORDS:
        fail(name, f"{k.label}: the data file's Guide text is {words} words, over {GUIDE_WORDS} (the seat's number)")
    cells = k.book.cells("Guide")
    details = {r for (r, c), d in cells.items() if c == 1 and d.text == "Details and caveats"}
    for (r, c), d in cells.items():
        if c <= 2 and r not in details and ((d.f or "").startswith("HYPERLINK(") or "http" in (d.text or "")):
            fail(name, f"{k.label} Guide {letter(c)}{r}: an address in columns A and B outside the details row")
    rows = {d.text: r for (r, c), d in cells.items() if c == 1 and d.text}
    if not rows.get("How to Read the Sheet", 10 ** 6) < rows.get("This sheet", -1):
        fail(name, f"{k.label} Guide: the template's instructions do not come before the data file's text")


def t_guide_form(k: Case) -> None:
    name = test("4.5 a guide in the reference form")
    if k.book.order[0] != "Guide":
        fail(name, f"{k.label}: the first tab is {k.book.order[0]!r}, not Guide")
        return
    sh = k.book.sheets["Guide"]
    for c, want in enumerate((170, 600, 200, 320), start=1):
        if abs(sh.width(c, 0) - want) > 0.5:
            fail(name, f"{k.label} Guide column {letter(c)} is {sh.width(c, 0):.0f} px, not {want}")
    for (r, c), d in sh.cells.items():
        if c == 1 and len(d.text or "") > GUIDE_A_CHARS:
            fail(name, f"{k.label} Guide A{r}: {len(d.text or '')} characters in column A, over {GUIDE_A_CHARS}")
    described = [str(a) for a, _ in k.tabs[0].get("tabs", [])]
    if sorted(described) != sorted(k.book.order[1:]):
        fail(name, f"{k.label}: the Guide's tabs {described} are not every other tab once")
    # 1.5: the Guide's heads, subheads and body as his template's Readme sets them (TEMPLATE_*)
    cells = k.book.cells("Guide")
    rows = {d.text: r for (r, c), d in cells.items() if c == 1 and d.text}
    for (r, c), d in cells.items():
        f, where = k.book.font(d.s), f"{k.label} Guide {letter(c)}{r}"
        if d.text in TEMPLATE_HEADS and (f.name, f.size, f.bold) != ("Arial", 16, True):
            fail(name, f"{where} {d.text!r}: {f.name} {f.size:g}{' bold' if f.bold else ''}; the template's head is Arial 16 bold")
        if d.text in TEMPLATE_SUBHEADS and (f.name, f.size, f.bold, f.colour) != ("Arial", 10, True, TEMPLATE_INK):
            fail(name, f"{where} {d.text!r}: {f.name} {f.size:g}{' bold' if f.bold else ''} #{f.colour}; the template's subhead is Arial 10 bold #{TEMPLATE_INK}")
    if not ("How to Read the Sheet" in rows and "Technical Details" in rows and "Inputs" in rows):
        fail(name, f"{k.label} Guide: the template's head or subhead is missing")
        return
    filled = {r for (r, c), d in cells.items() if c == 1 and (d.text or d.f)}
    body = [(r, d) for (r, c), d in cells.items() if c == 2 and rows["How to Read the Sheet"] <= r < rows["Technical Details"]
            and r not in filled and d.text and d.f is None]
    if len(body) < 5:
        fail(name, f"{k.label} Guide: {len(body)} body texts found before Technical Details")
    for r, d in body:
        f = k.book.font(d.s)
        if (f.name, f.size, f.bold, f.colour) != ("Arial", 10, False, TEMPLATE_INK):
            fail(name, f"{k.label} Guide B{r}: {f.name} {f.size:g}{' bold' if f.bold else ''} #{f.colour}; the template's body is Arial 10 #{TEMPLATE_INK}")


def t_setting(k: Case) -> None:
    name = test("4.6 the interval is one Guide cell")
    reads: set[str] = set()
    for sheet in k.column_tabs():
        on(sheet)
        for (r, c), d in k.book.cells(sheet).items():
            if r in (SLO, SHI) and c > 1 and d.f is not None:
                found = refs_in(d.f, ["Guide"])
                if not found:
                    fail(name, f"{k.label} {sheet} {letter(c)}{r} does not read the Guide's setting")
                reads.update(ref for _, ref in found)
    if len(reads) != 1:
        fail(name, f"{k.label}: rows {SLO} and {SHI} read {sorted(reads)}, not one Guide cell")
    for i, c in k.data.get("Globals", {}).items():
        if re.search(r"interval|percentile", str(c.get("name", "")), re.I):
            fail(name, f"{k.label} Globals {i}: a column of how the sheet works")


def t_groups(k: Case) -> None:
    name = test("4.7 categories with label columns")
    for t in k.tabs:
        sheet = str(t["name"])
        on(sheet)
        cols = list(t.get("column", []))
        if not cols or "group" not in cols[0]:
            continue
        cells, (letters, labels, turn) = k.book.cells(sheet), placed(t)
        methods = {str(m["group"]) for m in t.get("method", [])}
        fills: dict[str, list[str | None]] = {}  # each tint's turn: the fills of its groups' name cells
        for i, c in enumerate(cols):
            g = str(c["group"])
            first = cells.get((1, letters[str(c["id"])]))
            fills.setdefault(turn[g], []).append(None if first is None else k.book.fill(first.s))
            if (i and c["group"] == cols[i - 1]["group"]) or g not in labels:  # the row form: no label column, the name cell is still tinted
                continue
            n = labels[g]
            head = cells.get((1, n))
            if head is None or head.text != c["group"] or not k.book.font(head.s).bold or k.book.fill(head.s) != LABEL_FILL:
                fail(name, f"{k.label} {sheet} {letter(n)}1: the label column of {c['group']!r} is not its words, bold on yellow")
            for (r, cc), d in cells.items():
                if cc != n or r == 1 or not (d.text or d.f or d.num is not None):
                    continue
                if not (c["group"] in methods and ((r, d.text) in ((KIND, "Credence"), (tr(6), "Cum. share")) or (r == P1 and d.num is not None)
                                                   or (r == tr(7) and d.f is not None))):
                    fail(name, f"{k.label} {sheet} {letter(n)}{r}: a label column holds {d.text or d.f or d.num!r}")
        tints: list[str | None] = []
        for g, got in fills.items():
            if len(set(got)) != 1:
                fail(name, f"{k.label} {sheet}: the name cells of one block or pick set are tinted {sorted(set(x or '' for x in got))}, not one tint")
            tints.append(got[0])
        for a, b in zip(tints, tints[1:]):
            if a is None or a == b:
                fail(name, f"{k.label} {sheet}: neighbouring blocks' name cells are not tinted apart ({a}, {b})")


def t_dropdown(k: Case) -> None:
    name = test("4.8 the dropdown on inputs only")
    for sheet in k.column_tabs():
        on(sheet)
        inputs = {f"{x}{KIND}" for x, col in k.columns.get(sheet, {}).items() if is_input(col)}
        got = k.book.sheets[sheet].validations
        cells = {ref for sq, _ in got for ref in sq.split()}
        if cells != inputs:
            fail(name, f"{k.label} {sheet}: the dropdown covers {sorted(cells ^ inputs)[:6]} wrongly")
        for _, f1 in got:
            if set(f1.strip('"').split(",")) != KINDS7:
                fail(name, f"{k.label} {sheet}: the dropdown lists {f1!r}, not the seven kinds")


def t_tab_labels(k: Case) -> None:
    name = test("4.9 tab names follow a rename")
    for sheet in k.book.order:
        on(sheet)
        kind = k.kinds.get(sheet)
        if kind not in ("table", "sensitivity", "guide"):
            continue
        others = [t for t in k.book.order if t != sheet]
        cells = k.book.cells(sheet)
        for (r, c), d in k.book.view(sheet).items():
            if kind == "guide" and c != 1:
                continue
            text = d.text or ""
            label = d.f is not None and 'CELL("address"' in d.f
            if d.f is None and text in others:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: {text!r} names a tab as text, not a formula that follows a rename")
            if label and not any(text == t or (text.startswith(t) and text[len(t):len(t) + 1] in (",", ":")) or text.startswith("Ranks: " + t) for t in others):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a tab-name formula over {text!r}, which names no tab")
            if label and kind == "table":
                t = next((t for t in sorted(others, key=len, reverse=True) if text.startswith(t) and text[len(t):len(t) + 1] in (",", ":")), None)
                below = [e.f or "" for (r2, c2), e in cells.items() if c2 == c and r2 > r]
                if t is not None and not any(unquote(m.group(1)) == t for f in below for m in PLAIN.finditer(f)):
                    fail(name, f"{k.label} {sheet} {letter(c)}{r}: {text!r} is a formula naming tab {t}, but nothing below reads {t}")


# 5 formulas ----------------------------------------------------------------------------------------------------------

def t_no_arrays(k: Case) -> None:
    name = test("5.1 plain formulas, no array")
    for sheet in k.book.order:
        on(sheet)
        for (r, c), d in k.book.view(sheet).items():
            if d.f is not None and "ARRAYFORMULA" in d.f.upper():
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: an array formula")
    for sheet in k.column_tabs():
        on(sheet)
        cells = k.book.cells(sheet)
        for x, col in k.columns.get(sheet, {}).items():
            d = cells.get((FIRST, colnum(x)))
            if col["kind"] == "calc" and (d is None or d.span != f"{x}{FIRST}:{x}{LAST}"):
                fail(name, f"{k.label} {sheet} {x}{FIRST}: not one shared formula down to row {LAST}")


def t_no_copies(k: Case) -> None:
    name = test("5.2 no copies")
    cited: dict[tuple[str, str], set[str]] = {}
    for t in k.tabs:
        for c in t.get("column", []):
            for m in re.finditer(r"(?:'((?:[^']|'')+)'|([A-Za-z_][\w.]*))!(\w+)", str(c.get("formula", ""))):
                cited.setdefault((m.group(1) or m.group(2) or "", m.group(3)), set()).add(str(t["name"]))
    for t in k.tabs:
        for c in t.get("column", []):
            if c.get("kind") == "read":
                fail(name, f"{k.label} {t['name']} {c['id']}: a column of kind read")
            m = re.fullmatch(r"\s*(?:'((?:[^']|'')+)'|([A-Za-z_][\w.]*))!\w+\s*", str(c.get("formula", "")))
            if m is not None and not cited.get((str(t["name"]), str(c["id"])), set()) - {str(t["name"])}:
                fail(name, f"{k.label} {t['name']} {c['id']} = {c['formula']}: a copy of another tab's column that only its own tab uses; cite it directly")


def t_picks(k: Case) -> None:
    name = test("5.3 picks show the pick")
    for t in k.tabs:
        sheet, cols = str(t["name"]), list(t.get("column", []))
        on(sheet)
        ids = [str(c["id"]) for c in cols]
        for c in cols:
            if c.get("kind") == "calc" and re.search(r"\b(SIN|RAND|RANDBETWEEN|RANDARRAY)\(|MOD\(\s*ROW", str(c.get("formula", ""))):
                fail(name, f"{k.label} {sheet} {c['id']}: a calculation draws a random number")
        chosen = picks(k, sheet)
        for pick, u in chosen.items():
            between = ids[ids.index(u) + 1:ids.index(pick)]
            if ids.index(u) > ids.index(pick) or any(chosen.get(x) != u for x in between):
                fail(name, f"{k.label} {sheet} {pick}: its random number {u} does not stand just left of it (or of the picks reading it)")
    # 5.5: a pick citing CUMSHARE(id) is a short formula over each method's cumulative share, X$7, and each share cell
    # is the sum of its pick's credences up to its own over all of them, rising along the pick.
    name = test("5.5 a pick reads cumulative shares")
    for t in k.tabs:
        sheet = str(t["name"])
        on(sheet)
        cells, letters = k.book.cells(sheet), layout(t)
        rowed = row_form(t)
        first = {str(m["id"]): letters[next(str(c["id"]) for c in t.get("column", []) if c.get("group") == m["group"])] for m in t.get("method", [])}
        label = {str(m["id"]): first[str(m["id"])] - (0 if m["group"] in rowed else 1) for m in t.get("method", [])}
        credence_row = {str(m["id"]): CRED if m["group"] in rowed else P1 for m in t.get("method", [])}
        in_row = {str(m["id"]): m["group"] in rowed for m in t.get("method", [])}
        share_row = {i: r + 1 if in_row[i] else tr(7) for i, r in credence_row.items()}
        for c in t.get("column", []):
            cited = re.findall(r"CUMSHARE\((\w+)\)", str(c.get("formula", "")))
            if not cited:
                continue
            f = cells.get((FIRST, letters[str(c["id"])]))
            text = "" if f is None or f.f is None else "=" + f.f
            read = sorted(set(re.findall(r"([A-Z]+)\$(\d+)", text)))
            if len(text) >= 200 or read != sorted((letter(label[m]), str(share_row[m])) for m in set(cited)):
                fail(name, f"{k.label} {sheet} {c['id']}: its draw formula is not a short pick over the share cells of {cited}: {text[:120]!r}")
            last = 0.0
            for m in cited:
                rc, rs = credence_row[m], share_row[m]
                share = cells.get((rs, label[m]))
                head = cells.get((rs, 1) if in_row[m] else (tr(6), label[m]))
                if head is None or head.text != ("Cumulative share" if in_row[m] else "Cum. share") or share is None or share.f is None:
                    fail(name, f"{k.label} {sheet} {letter(label[m])}{rs}: method {m} shows no cumulative share")
                    continue
                expr = re.sub(rf"\$?([A-Z]+)\${rc}", lambda x: repr(cells[(rc, colnum(x.group(1)))].num), share.f)
                if not re.fullmatch(r"[\d.+/()e-]+", expr):
                    fail(name, f"{k.label} {sheet} {letter(label[m])}{rs}: ={share.f} reads more than the credences of row {rc}")
                    continue
                value = float(eval(expr))
                if not last < value < 1:
                    fail(name, f"{k.label} {sheet} {letter(label[m])}{rs}: ={share.f} gives {value}, not between {last} and 1")
                last = value


def cited_methods(t: dict[str, Any]) -> set[str]:
    return {m for c in t.get("column", []) for m in re.findall(r"CUMSHARE\((\w+)\)", str(c.get("formula", "")))}


def t_credence_row(k: Case) -> None:
    """A tab whose methods are single columns has no credence column: each credence stands in its own column, in the Credence
    row inserted above the notes (row 2), and the share under it (row 3), on that tab alone; no input's settings row
    (kind, parameters) is ever one of them, so that a method column set to a beta keeps its credence."""
    name = test("4.13 a method of one column has its credence in a row")
    for t in k.tabs:
        sheet, cols = str(t["name"]), list(t.get("column", []))
        on(sheet)
        if not cols or not row_form(t):
            continue
        cells = k.book.cells(sheet)
        for r, want in ((CRED, "Credence"), (SHARE, "Cumulative share")):  # a tab with a one-column pick has the two rows, the labels in column A
            d = cells.get((r, 1))
            if (r == CRED or cited_methods(t)) and (d is None or d.text != want) and row_form(t):
                fail(name, f"{k.label} {sheet} A{r}: {d.text if d else None!r}, not the label {want!r}")
            if d is not None and clipped(k, sheet, r, 1):
                fail(name, f"{k.label} {sheet} A{r}: {d.text!r} is clipped at the column's width")
        rowed = row_form(t)
        ltr, labels, _ = placed(t)
        blocks = len({c["group"] for c in cols if c["group"] not in rowed})
        last = max((c for (r, c), d in cells.items() if r == 1 and d.text), default=0)
        if last != 1 + len(cols) + blocks:
            fail(name, f"{k.label} {sheet}: {last} columns in row 1, not {1 + len(cols) + blocks}: a data column each, a label column for each block, and no credence column")
        shared = cited_methods(t)
        for m in t["method"]:
            if m["group"] not in rowed:
                continue
            n = ltr[next(str(c["id"]) for c in cols if c["group"] == m["group"])]
            if n > 2 and n - 1 not in ltr.values() and n - 1 not in labels.values():
                fail(name, f"{k.label} {sheet} {letter(n - 1)}: a credence column stands before the single column of method {m['id']}")
            cred, share = cells.get((CRED, n)), cells.get((SHARE, n))
            if cred is None or cred.num != float(m["credence"]) or k.book.font(cred.s).colour != INPUT_BLUE:
                fail(name, f"{k.label} {sheet} {letter(n)}{CRED}: the credence of {m['id']} is not its number {m['credence']} in input blue")
            if m["id"] in shared and (share is None or share.f is None or set(re.findall(r"\$(\d+)", share.f)) != {str(CRED)}):
                fail(name, f"{k.label} {sheet} {letter(n)}{SHARE}: the cumulative share of {m['id']} is not a formula over row {CRED}")


def t_credence_separator(k: Case) -> None:
    """A method that is a block of columns keeps its label column: empty but for the method's name, its credence, and the
    labels; no label is clipped at the column's width."""
    name = test("4.14 a method of several columns has a label column")
    for t in k.tabs:
        sheet, cols = str(t["name"]), list(t.get("column", []))
        on(sheet)
        rowed = row_form(t)
        cells = k.book.cells(sheet)
        ltr = layout(t)
        shared = cited_methods(t)
        for m in t.get("method", []):
            if m["group"] in rowed:
                continue
            n = ltr[next(str(c["id"]) for c in cols if c["group"] == m["group"])] - 1
            want = [(KIND, "Credence")] + ([(tr(6), "Cum. share")] if m["id"] in shared else [])
            for r, text in want:
                d = cells.get((r, n))
                if d is None or d.text != text:
                    fail(name, f"{k.label} {sheet} {letter(n)}{r}: {d.text if d else None!r}, not {text!r}")
                elif clipped(k, sheet, r, n):
                    fail(name, f"{k.label} {sheet} {letter(n)}{r}: {text!r} is clipped at the column's width")
            d = cells.get((P1, n))
            if d is None or d.num != float(m["credence"]):
                fail(name, f"{k.label} {sheet} {letter(n)}{P1}: the credence of {m['id']} is not {m['credence']}")


def t_credence_guide(k: Case) -> None:
    """The Guide says, for a sheet with a pick over methods, what the credence and cumulative share rows are, and the label
    column of a block."""
    name = test("4.15 the Guide explains the credences")
    text = " ".join(d.text or "" for d in k.book.cells("Guide").values())
    for t in k.tabs:
        if not t.get("method") or not cited_methods(t):
            continue
        on(str(t["name"]))
        rowed = row_form(t)
        need = [("need not sum to 1", "that the weights need not sum to 1")]
        if rowed:
            need += [("labelled Credence", "the Credence row"), ("Cumulative share", "the cumulative-share row"), ("may be hidden", "that the row may be hidden")]
        if rowed:
            need += [(f"Credence (row {CRED})", f"the Credence row's number, {CRED}"), (f"Cumulative share (row {SHARE},", f"the cumulative-share row's number, {SHARE}")]
        if any(m["group"] not in rowed for m in t["method"]):
            need += [("label column", "the label column of a block"), ("Cum. share", "its Cum. share")]
        for phrase, what in need:
            if phrase not in text:
                fail(name, f"{k.label} Guide: nothing says {what} ({phrase!r}) for the {t['name']} tab")


KIND_PARAMS = {"beta": {"lo", "hi", "alpha", "beta"}, "constant": {"mean"}, "lognormal": {"mean", "sd"}, "normal": {"mean", "sd"},
               "power law": {"lo", "alpha"}, "triangular": {"lo", "hi", "peak"}, "uniform": {"lo", "hi"}}  # the template's seven kinds' parameters


def t_one_role(k: Case) -> None:
    """4.16 (the owner, 2026-11-21, of a credence the generator put in a beta's alpha row: "don't have a cell that goes to 2
    things like that"): no cell of a generated sheet has two roles. Each tab's role map is built from the data file and the
    layout: a column tab's heading, note, source, the settings rows of an input (every row any kind of its dropdown can
    write, not only the kind chosen), the statistics, the graph, the draws, the credence and cumulative share, a label
    column's cells, and a table's cells. A cell claimed by two roles fails; so does a cell some selectable choice would
    write to that holds anything but its own setting, and a cell holding something no role claims."""
    name = test("4.16 no cell has two roles")
    for t in k.tabs:
        sheet, cols = str(t["name"]), list(t.get("column", []))
        on(sheet)
        cells = k.book.cells(sheet)
        roles: dict[tuple[int, int], list[str]] = {}

        def claim(r: int, c: int, role: str, roles: dict[tuple[int, int], list[str]] = roles) -> None:
            roles.setdefault((r, c), []).append(role)
        if t.get("kind") == "table":
            for r, row in enumerate(t.get("rows", []), start=1):
                for c in range(1, len(row) + 1):
                    claim(r, c, "a table's cell")
            for (r, c), d in cells.items():  # column A's texts under a long title move down a row (`title_note`), so only the rest is read
                if c > 1 and (d.text or d.f or d.num is not None) and (r, c) not in roles:
                    fail(name, f"{k.label} {sheet} {letter(c)}{r}: holds {d.text or d.f or d.num!r}, which no role claims")
            continue
        if not cols:
            continue
        got = k.book.sheets[sheet].validations
        dropdown = {x for _, f1 in got for x in f1.strip('"').split(",")} or KINDS7
        selectable = {p for kind in dropdown for p in KIND_PARAMS.get(kind, set())}  # every setting a choice of the dropdown writes
        (ltr, labels, _), rowed = placed(t), row_form(t)
        for r in range(1, GRAPH + 1):
            claim(r, 1, "column A's label")
        for i, c in enumerate(cols):
            n = ltr[str(c["id"])]
            claim(1, n, "name")
            claim(NOTE, n, "note")
            claim(CITE, n, "source or formula")
            for r in range(KIND, P7 + 1):
                key = next((p for p, v in SETTINGS.items() if tr(v) == r), None)
                claim(r, n, "the distribution kind" if r == KIND else "a setting of the kind chosen" if is_input(c) and key in selectable else "an unused settings row")
            for r in (SLO, SMEAN, SHI):
                claim(r, n, "a statistic")
            claim(GRAPH, n, "the graph")
            if c.get("group") in rowed:
                claim(CRED, n, "the credence")
                claim(SHARE, n, "the cumulative share")
            if c.get("group") is not None and (i == 0 or c["group"] != cols[i - 1].get("group")) and c["group"] not in rowed:
                for r, role in ((1, "the group's name"), (KIND, "the label of the credence"), (P1, "the credence"), (tr(6), "the label of the share"), (tr(7), "the cumulative share")):
                    claim(r, labels[str(c["group"])], role)
        for (r, c), who in sorted(roles.items()):
            if len(who) > 1:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: claimed by {len(who)} roles ({', '.join(who)})")
        for i, c in enumerate(cols):
            if not is_input(c):
                continue
            n = ltr[str(c["id"])]
            for p, v in SETTINGS.items():  # a cell a choice of the dropdown would write: its own setting or empty, nothing else
                d = cells.get((tr(v), n))
                held = None if d is None else d.num if d.num is not None else (d.text or d.f)
                want = c.get(p) if p in KIND_PARAMS.get(str(c["kind"]), set()) else None
                scales = [1000.0 ** j for j in range(-4, 5)] if p in ("mean", "sd", "lo", "peak", "hi") else [1.0]  # the book's unit (reading 11)
                own = want is not None and isinstance(held, float) and any(abs(held - float(want) * f) <= 1e-9 * max(abs(held), 1.0) for f in scales)
                if held not in (None, "") and not own:
                    fail(name, f"{k.label} {sheet} {letter(n)}{tr(v)}: the {p} cell of {c['id']} (kind {c['kind']}; a choice of the dropdown writes it) holds {held!r}, not {want!r}")
        for (r, c), d in cells.items():
            if r < FIRST and (d.text or d.f or d.num is not None) and (r, c) not in roles and c <= max(ltr.values(), default=1):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: holds {d.text or d.f or d.num!r}, which no role claims")


# 6 model content -----------------------------------------------------------------------------------------------------

CONVENTION = re.compile(r"\bdefin|\bconver|\bunit\b", re.I)
CASE_WORD = re.compile(r"\b(low|mid|middle|central|high)\b", re.I)


def convention(c: dict[str, Any]) -> bool:
    return str(c.get("citation", "")).startswith("Convention")


def stated_year(tabs: list[dict[str, Any]]) -> int:
    """The dollar year the data file's Guide states ("2025 won", "a 2025 dollar"), else FIXED_YEAR (reading 9)."""
    for t in tabs:
        if t.get("kind") != "guide":
            continue
        m = re.search(r"(?<!\d)((?:19|20)\d\d) (?:US )?(?:dollars?|won|euros?)\b", json.dumps(t, ensure_ascii=False))
        if m:
            return int(m.group(1))
    return FIXED_YEAR


def constant_faults(tabs: list[dict[str, Any]], year: int) -> list[tuple[str, str, str]]:
    """6.1 (reading 9): each constant that is neither a convention nor a published value for a past period, as (tab, id, why)."""
    out: list[tuple[str, str, str]] = []
    for t in tabs:
        for c in t.get("column", []):
            if c.get("kind") != "constant":
                continue
            cite = str(c.get("citation", ""))
            if c.get("format") == "year":
                out.append((str(t["name"]), str(c["id"]), "a year as a constant (an anchor year)"))
            years = [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d\d)(?!\d)", f"{c.get('name', '')} {c.get('id', '')}")]
            past = bool(years) and max(years) <= year and "http" in cite
            if not (convention(c) or CONVENTION.search(cite) or past):
                out.append((str(t["name"]), str(c["id"]), "a constant that is no convention, definition or unit conversion, nor a "
                            f"published value for a past period: a judged or forecast quantity: {cite[:70]!r}"))
    return out


def case_faults(tabs: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    """6.3 (reading 9): low, mid and high copies of a quantity not set by a convention, and discount rates that are no
    distribution, as (tab, first id, why)."""
    conv = {(str(t["name"]), str(c["id"])) for t in tabs for c in t.get("column", []) if c.get("kind") == "constant" and convention(c)}
    out: list[tuple[str, str, str]] = []
    for t in tabs:
        tab, cols = str(t["name"]), list(t.get("column", []))
        ids = {str(c["id"]) for c in cols}

        def reads(c: dict[str, Any]) -> frozenset[tuple[str, str]]:
            if c.get("kind") == "constant":
                return frozenset({(tab, str(c["id"]))} & conv)
            f = str(c.get("formula", ""))
            got = {(m.group(1).replace("''", "'") if m.group(1) else m.group(2), m.group(3))
                   for m in re.finditer(r"(?:'((?:[^']|'')+)'|([A-Za-z_][\w.]*))!(\w+)", f)}
            got |= {(tab, w) for w in re.findall(r"(?<![\w!.'])([A-Za-z_]\w*)(?![\w(!])", f) if w in ids}
            return frozenset(got & conv) if c.get("kind") == "calc" else frozenset()

        groups: dict[str, list[dict[str, Any]]] = {}
        for c in cols:
            cname = str(c.get("name", ""))
            if CASE_WORD.search(cname):
                groups.setdefault(" ".join(CASE_WORD.sub(" ", cname).lower().split()), []).append(c)
        for members in groups.values():
            if len(members) < 2:
                continue
            sets = [reads(c) for c in members]
            if not (all(sets) and len(set(sets)) == len(sets)):
                out.append((tab, str(members[0]["id"]), f"low, mid and high copies of one quantity, not each set by a convention: "
                            f"{[str(c['id']) for c in members]}"))
        for c in cols:
            if re.search(r"discount rate", str(c.get("name", "")), re.I) and c.get("kind") in ("constant", "calc") \
                    and not (c.get("kind") == "constant" and convention(c)):
                out.append((tab, str(c["id"]), f"a discount rate that is no distribution ({c.get('kind')}) and not marked Convention"))
    return out


def t_constants(k: Case) -> None:
    name = test("6.1 no constants for the uncertain")
    year = stated_year(k.tabs)
    for tab, cid, why in constant_faults(k.tabs, year):
        fail(name, f"{k.label} {tab} {cid}: {why}")


def t_one_distribution(k: Case) -> None:
    name = test("6.2 one distribution")
    for t in k.tabs:
        sheet = str(t["name"])
        on(sheet)
        for pick in picks(k, sheet):
            if not t.get("method") or not re.search(r"\b(CREDENCE|CUMSHARE)\(", str(k.data[sheet][pick].get("formula", ""))):
                fail(name, f"{k.label} {sheet} {pick}: a per-draw pick among cases on a tab that declares no methods")


def t_no_low_high(k: Case) -> None:
    name = test("6.3 no low, mid and high")
    for tab, cid, why in case_faults(k.tabs):
        fail(name, f"{k.label} {tab} {cid}: {why}")
    # reading 9's probes. The data file with its discount-rate constants marked Convention: no fault of 6.1 or 6.3
    # left on them or on a column that reads them (the present values at each of the guidance's rates).
    year = stated_year(k.tabs)
    probe = copy.deepcopy(k.tabs)
    marked: set[str] = set()
    for t in probe:
        for c in t.get("column", []):
            if c.get("kind") == "constant" and re.search(r"discount rate", str(c.get("name", "")), re.I):
                c["citation"] = "Convention: " + str(c.get("citation", ""))
                marked.add(str(c["id"]))
    if len(marked) < 2:
        fail(name, f"probe: the data file has {len(marked)} discount-rate constants to mark Convention; the probe cannot see a convention")
    by_id = {(str(t["name"]), str(c["id"])): c for t in probe for c in t.get("column", [])}
    for tab, cid, why in case_faults(probe) + constant_faults(probe, year):
        ids = [cid, *re.findall(r"'(\w+)'", why)]
        if any(i in marked or re.search(rf"(?<![\w]){re.escape(m)}(?!\w)", str(by_id.get((tab, i), {}).get("formula", "")))
               for i in ids for m in marked):
            fail(name, f"probe: with the discount rates marked Convention, {tab} {cid} still fails: {why[:120]}")
    # A tab of planted columns: a future-year constant and a low and high pair of judged inputs fail; a past-year
    # published count and a low and high pair of results at two Convention rates pass.
    plant: list[dict[str, Any]] = [{"name": "Probe", "column": [
        {"id": "p_future", "name": f"Reagent price, {year + 9}", "kind": "constant", "citation": "A forecast https://example.org/f", "mean": 1},
        {"id": "p_past", "name": f"Population, {year}", "kind": "constant", "citation": "A census https://example.org/c", "mean": 1},
        {"id": "p_yield_low", "name": "Yield, low", "kind": "lognormal", "lo": 1, "hi": 2},
        {"id": "p_yield_high", "name": "Yield, high", "kind": "lognormal", "lo": 2, "hi": 3},
        {"id": "p_rate_a", "name": "Rate A", "kind": "constant", "citation": "Convention: guidance A", "mean": 0.03},
        {"id": "p_rate_b", "name": "Rate B", "kind": "constant", "citation": "Convention: guidance B", "mean": 0.07},
        {"id": "p_pv_low", "name": "PV, low rate", "kind": "calc", "formula": "p_past/(1+p_rate_a)"},
        {"id": "p_pv_high", "name": "PV, high rate", "kind": "calc", "formula": "p_past/(1+p_rate_b)"}]}]
    got = {cid for _, cid, _ in constant_faults(plant, year) + case_faults(plant)}
    for cid, should in (("p_future", True), ("p_past", False), ("p_yield_low", True), ("p_pv_low", False)):
        if (cid in got) != should:
            fail(name, f"probe: the planted {cid} {'passes' if should else 'fails'} 6.1 or 6.3; it should {'fail' if should else 'pass'}")


def t_globals(k: Case) -> None:
    name = test("6.4 globals reused")
    users: dict[str, set[str]] = {}
    for t in k.tabs:
        for c in t.get("column", []):
            for m in re.finditer(r"(?<![\w'])Globals!(\w+)", str(c.get("formula", ""))):
                users.setdefault(m.group(1), set()).add(str(t["name"]))
        rows: list[list[object]] = t.get("rows", []) if t.get("kind") == "table" else []
        for row in rows:
            for cell in row:
                for m in re.finditer(r"(?<![\w'])Globals!(\w+)", str(cell)):
                    users.setdefault(m.group(1), set()).add(str(t["name"]))
    glob = k.data.get("Globals", {})
    for _ in glob:  # a Globals column that feeds another Globals column serves that column's tabs too
        for i, c in glob.items():
            for j in re.findall(r"(?<![\w!])(\w+)", str(c.get("formula", ""))):
                if j in glob and j != i:
                    users.setdefault(j, set()).update(users.get(i, set()))
    for i, c in glob.items():
        if len(users.get(i, set()) - {"Globals"}) < 2 and not re.search(r"analysis year", str(c.get("note", "")), re.I):
            fail(name, f"{k.label} Globals {i}: used by {sorted(users.get(i, set()) - {'Globals'})}; Globals holds what two tabs use")


def t_spelling(k: Case) -> None:
    name = test("6.5 American spelling")
    own = [str(s) for s in (*ss.GUIDE_READ, *(b for _, b in ss.GUIDE_KEY.values()), ss.GUIDE_INTERVAL, ss.GUIDE_DRAWS,
                            *ss.GUIDE_INPUTS, *(b for _, b in ss.GUIDE_KINDS), *ss.GUIDE_OUTPUTS, *ss.GUIDE_COMBINING, *ss.GUIDE_TECHNICAL)]
    texts = [("the generator's Guide", s) for s in own]
    texts += [(sheet, d.text) for sheet in k.book.order for d in k.book.cells(sheet).values() if d.text]
    for where, text in texts:
        m = re.search(r"\b(" + "|".join(BRITISH) + r")\w*", text, re.I)
        if m:
            fail(name, f"{k.label} {where}: {m.group(0)!r} in {text[:80]!r}")


# 7 output tabs -------------------------------------------------------------------------------------------------------

def t_sensitivity(k: Case) -> None:
    name = test("7.1 sensitivity leads with a ranked list")
    for t in k.tabs:
        if t.get("kind") != "sensitivity":
            continue
        sheet = str(t["name"])
        on(sheet)
        cells = k.book.cells(sheet)
        values = {(r, c): v for r, c, v in k.twin["tables"].get(sheet, [])}
        heads = sorted((r, c) for (r, c), d in cells.items() if d.text == "Rank")
        if len(heads) != len(t.get("outputs", [])):
            fail(name, f"{k.label} {sheet}: {len(heads)} ranked lists for {len(t.get('outputs', []))} outputs")
        every = min((r for (r, _), d in cells.items() if d.text == "Every input"), default=0)
        for r0, b in heads:
            row = [(cells.get((r0, b + j)) or Cell(0)).text or "" for j in range(7)]
            if any(not x.startswith(h) for x, h in zip(row, SENS_HEAD)):
                fail(name, f"{k.label} {sheet} row {r0}: the list's heads are {row}")
            if not r0 + 15 < every:
                fail(name, f"{k.label} {sheet}: the ranked list does not stand above the full table")
            keys: list[float] = []
            for j in range(1, 16):
                r = r0 + j
                for cc in (b + 1, b + 2, b + 6):
                    d = cells.get((r, cc))
                    if d is None or d.f is None:
                        fail(name, f"{k.label} {sheet} {letter(cc)}{r}: rank {j} has no formula naming its input, tab and key")
                v = values.get((r, b + 6))
                if v is not None and math.isfinite(v):
                    keys.append(v)
            if keys != sorted(keys, reverse=True):
                fail(name, f"{k.label} {sheet} {letter(b + 6)}: the keys are not ordered: {[round(x, 3) for x in keys]}")
        for (r, c), d in cells.items():
            if d.f is not None and "MAX(ABS(" in d.f and "IFERROR(" not in d.f:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: a key without its IFERROR guard")


def t_no_errors(k: Case) -> None:
    name = test("7.2 tables finished, no error cells")
    for sheet, values in k.twin["tables"].items():
        on(sheet)
        for r, c, v in values:
            if not math.isfinite(v):
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: the twin computes {v}")
    for sheet, strings in k.twin["strings"].items():
        on(sheet)
        for r, c, v in strings:
            if str(v) in ERRORS:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: an error value {v!r}")
    for sheet in k.book.order:
        on(sheet)
        for (r, c), d in k.book.view(sheet).items():
            if (d.text or "") in ERRORS:
                fail(name, f"{k.label} {sheet} {letter(c)}{r}: an error value {d.text!r}")


# 8 process -----------------------------------------------------------------------------------------------------------

def t_superseded(lines: list[tuple[str, int, str]]) -> None:
    name = test("8.5 superseded rules left out")
    for rel, n, line in lines:
        for p in SUPERSEDED:
            if re.search(p, line, re.I) and not re.search(r"supersed|replac", line, re.I):
                fail(name, f"{rel}:{n} states the superseded {p!r} without marking it so")


# the values and the generate check -----------------------------------------------------------------------------------

def setting_cell(book: Book) -> tuple[str, float] | None:
    for (r, c), d in book.cells("Guide").items():
        if d.num is not None and book.font(d.s).colour == INPUT_BLUE:
            return f"{letter(c)}{r}", d.num
    return None


POWER = re.compile(r"[*/]1(?:000)+(?![\d.eE])|(?<![\w.$])1(?:000)+\*")  # a conversion factor, a power of 1,000 (R63)
BARE = re.compile(r"(?<![\w.])\(([\w!$'.]+)\)")  # a reference in brackets of its own


def unconverted(f: str) -> str:
    """A formula less its conversion factors (`*1000`, `/1000000`, `1000*`) and the brackets they leave round one reference."""
    while True:
        g = BARE.sub(r"\1", POWER.sub("", f))
        if g == f:
            return f
        f = g


DRAW_PATTERN = re.compile(r"\(\[A-Z\]\+\)(?:\d+|\(\?:\d+(?:\|\d+)*\))\\b")  # the draw rows a shown formula strips
ROW_AT = re.compile(r"\(ROW\(\)-(\d+)\)|ROW\(\)")
COLUMN_AT = re.compile(r"\(COLUMN\(\)-(\d+)\)|COLUMN\(\)")
COLUMN_IS = re.compile(r"(COLUMN\((?:(?:'(?:[^']|'')+'|[A-Za-z_][\w.]*)!)?\$?([A-Z]{1,3})\$?\d+\)=)(\d+)")  # a guard that a reference is its column
Shape = dict[str, tuple[int, int, int, dict[int, str]]]  # a tab's offset, its block's top row and left column, its columns' keys
RANKS = '"Ranks: "'  # the head of Sensitivity's ranks of the draws, the row above their first draw


def shape_of(book: Book, ids: dict[str, dict[int, str]]) -> Shape:
    """A workbook's layout, read from its own cells, so that two layouts of one data file can be compared: each column
    tab's offset (its Notes row less 2) and the key of each column (its data column's id, a label column's group, A);
    on another tab, the offset of its ranks of the draws (the row of their head less the template's 15), right of their
    first column."""
    out: Shape = {}
    for sheet in book.order:
        cells = book.cells(sheet)
        if sheet in ids:
            off = next((r - 2 for (r, c), d in cells.items() if c == 1 and d.text == "Notes"), 0)
            keys = {1: "A"} | {c: f"label {d.text}" for (r, c), d in cells.items() if r == 1 and c > 1 and c not in ids[sheet] and d.text}
            out[sheet] = (off, 2 + off, 1, keys | ids[sheet])
            continue
        heads = [(r, c) for (r, c), d in cells.items() if d.f is not None and d.f.startswith(RANKS)]
        if heads:
            top = min(r for r, _ in heads)
            out[sheet] = (top - 15, top, min(c for _, c in heads), {})
    return out


def place(shape: Shape, sheet: str, r: int, c: int) -> tuple[str, str]:
    """A cell's place in the template's layout: its column's key and its row, less the inserted rows above it."""
    if sheet not in shape:
        return letter(c), str(r)
    off, top, left, keys = shape[sheet]
    col = keys.get(c, letter(c))
    if c < left or r < top - off:
        return col, str(r)
    return col, f"inserted {r}" if r < top else str(r - off)


def placed_formula(f: str, shape: Shape, sheet: str, r: int, c: int) -> str:
    """A formula in the template's layout: each reference by its place, ROW() and COLUMN() by their values in its cell, a
    guard's column number that is its reference's by one word, and a shown formula's draw rows by one word; text in quotes
    is left as it is but that pattern."""
    def ref(m: re.Match[str]) -> str:
        tab = unquote(m.group("tab")) if m.group("tab") else sheet
        ends = [(m.group("cd1"), m.group("c1"), m.group("rd1"), m.group("r1"))]
        if m.group("c2"):
            ends.append((m.group("cd2"), m.group("c2"), m.group("rd2"), m.group("r2")))
        return ":".join(f"[{tab}|{cd}{col}|{rd}{row}]" for cd, x, rd, y in ends for col, row in [place(shape, tab, int(y), colnum(x))])
    parts = re.split(r'("(?:[^"]|"")*")', f)
    for i, p in enumerate(parts):
        if i % 2:
            parts[i] = DRAW_PATTERN.sub("([A-Z]+)DRAW\\\\b", p)
        else:
            p = ROW_AT.sub(lambda m: str(r - int(m.group(1) or 0)), p)
            p = COLUMN_AT.sub(lambda m: str(c - int(m.group(1) or 0)), p)
            p = COLUMN_IS.sub(lambda m: m.group(1) + ("ITS" if colnum(m.group(2)) == int(m.group(3)) else m.group(3)), p)
            parts[i] = REF.sub(ref, p)
    return "".join(parts)


def t_values(k: Case) -> None:
    """Formulas and numbers unchanged from the base's workbook (the interface, item 2), in one unit (reading 11, R63) and
    one layout (R64): a formula is compared less its conversion factors, and a column tab's typed number in units of its
    currency, each side in the unit its column's heading or the base's twin names (`Case.twin_factor`); each cell and
    reference by its place in the template's layout, read from each workbook's own cells and columns (`shape_of`), since
    a tab's inserted rows and a pick's title column move cells without changing them."""
    name = test("values unchanged")
    sb, sn = setting_cell(k.old), setting_cell(k.book)
    if sb is None or sn is None or sb[1] != sn[1]:
        fail(name, f"{k.label}: the Guide's interval setting: base {sb}, now {sn}")
        return
    old = shape_of(k.old, {s: {colnum(x): str(c["id"]) for x, c in cols.items()} for s, cols in k.twin["columns"].items()})
    new = shape_of(k.book, {s: {colnum(x): str(c["id"]) for x, c in cols.items()} for s, cols in k.columns.items()})

    def norm(f: str, at: str, shape: Shape, sheet: str, key: tuple[int, int]) -> str:
        m = re.fullmatch(r"([A-Z]+)(\d+)", at)
        f = unconverted(f if m is None else re.sub(rf"Guide!\$?{m.group(1)}\$?{m.group(2)}(?!\d)", "Guide!SETTING", f))
        return placed_formula(f, shape, sheet, *key)

    for sheet in k.old.order:
        if sheet == "Guide":
            continue
        if sheet not in k.book.sheets:
            fail(name, f"{k.label}: tab {sheet} is gone")
            continue
        now = {place(new, sheet, *key): (key, e) for key, e in k.book.cells(sheet).items()}
        for key, d in k.old.cells(sheet).items():
            where = f"{k.label} {sheet} {letter(key[1])}{key[0]}"
            if d.f is not None and kind_of(d.f, sheet) == "label":
                continue
            at = place(old, sheet, *key)
            at_new, e = now.get(at, (key, None))
            if d.f is not None:
                if e is None or e.f is None or norm(e.f, sn[0], new, sheet, at_new) != norm(d.f, sb[0], old, sheet, key) or e.offset != d.offset:
                    fail(name, f"{where}: the formula ={d.f[:80]} is now {('=' + e.f[:80]) if e is not None and e.f else 'no formula'}"
                         f"{f' at {letter(at_new[1])}{at_new[0]}' if e is not None and at_new != key else ''}")
            elif d.num is not None:
                f = k.factor.get((sheet, at_new[1]), 1.0) if at[1].isdigit() and 5 <= int(at[1]) <= 9 else 1.0  # mean to hi; alpha and beta are shapes
                if e is None or e.num is None or abs(e.num - d.num * f) > 1e-9 * abs(d.num * f):
                    fail(name, f"{where}: the number {d.num!r} (x {f:g} in the book's unit) is now {None if e is None else (e.num, e.text)}")


def t_flow(res: dict[str, subprocess.CompletedProcess[str]], work: Path) -> None:
    name = test("5.4 every formula flows left to right")
    r = res["flow"]
    if r.returncode != 2 or "cite against the flow" not in r.stderr or "probe_back" not in r.stderr or "to its right" not in r.stderr:
        fail(name, f"a calculation citing a column to its right gave exit {r.returncode}, not 2 with the breach listed: {r.stderr[-400:]!r}")
    if (work / "flow" / "sheet.xlsx").exists():
        fail(name, "a refused file wrote a sheet")
    w = res["waiver"]
    if w.returncode != 0 or "flow: " not in w.stderr or "probe_back" not in w.stderr:
        fail(name, f"the same file with backward_references gave exit {w.returncode}, not 0 with flow: warnings: {w.stderr[-400:]!r}")


def t_header_notes(res: dict[str, subprocess.CompletedProcess[str]]) -> None:
    name = test("4.11 a header note only on a column")
    r = res["notes"]
    if r.returncode != 2 or "header_notes" not in r.stderr:
        fail(name, f"a tab-level header_notes gave exit {r.returncode}, not 2 naming it: {r.stderr[-400:]!r}")


def t_stage(res: dict[str, subprocess.CompletedProcess[str]], work: Path) -> None:
    name = test("4.12 the copy line by stage")
    if res["new"].returncode != 0 or res["nostage"].returncode != 0:
        fail(name, "a file to read did not generate")
        return

    def copies(path: Path) -> int:
        return sum(1 for d in Book(path).cells("Guide").values() if d.text and d.text.startswith("Save a copy of this sheet"))

    for label, path, want in (("stage = template", work / "new" / "sheet.xlsx", 1), ("no stage", work / "nostage" / "sheet.xlsx", 0)):
        if copies(path) != want:
            fail(name, f"with {label} the Guide has {copies(path)} copy lines, not {want}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.sheets.suite", description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--workers", type=int, default=2, help="generate and import runs at once (default 2)")
    ap.add_argument("--limit", type=int, default=12, help="failures printed a test (default 12)")
    ap.add_argument("--write-base", nargs="?", const="HEAD", metavar="REF", help="write the base from tools/sheets at REF and stop")
    a = ap.parse_args(argv)
    if a.write_base is not None:
        return write_base(cast(str, a.write_base))
    shown["limit"] = cast(int, a.limit)
    if not BASE_XLSX.exists() or not BASE_JSON.exists():
        print(f"no base beside the suite ({BASE_XLSX.name}, {BASE_JSON.name}): run --write-base")
        return 1
    work = Path(tempfile.mkdtemp(prefix="sheet_suite_"))
    try:
        probe = probe_file(work)
        jobs = {
            "new": [PY, "-m", "tools.sheets.script", "generate", str(DATA), "--out", str(work / "new")],
            "probe": [PY, "-m", "tools.sheets.script", "generate", str(probe), "--out", str(work / "probe")],
            **{key: [PY, "-m", "tools.sheets.script", "generate", str(path), "--out", str(work / key)] for key, path in variant_files(work).items()},
        }
        with ThreadPoolExecutor(max(1, cast(int, a.workers))) as ex:  # each job one process; the environment is inherited
            futures = {key: ex.submit(run, args, ROOT) for key, args in jobs.items()}
            text_tabs = ex.submit(text_round_trip, work)
            res = {key: f.result() for key, f in futures.items()}
            text_res = text_tabs.result()
        name = test("1.5 text tabs keep their formatting")
        if text_res.returncode != 0:
            fail(name, f"import and generate of a sheet with two text tabs: exit {text_res.returncode}: {(text_res.stdout + text_res.stderr)[-600:]}")
        else:
            book = Book(work / "text_gen" / "sheet.xlsx")
            want = {0: (10, False), 1: (16, True), 2: (10, True), 4: (10, False)}
            for tab, t in TEXT_TABS.items():
                cells = book.cells(tab)
                if not cells:
                    fail(name, f"imported tab {tab}: missing")
                    continue
                sh = book.sheets[tab]
                for text, st in t.cells.values():
                    found = [d for d in cells.values() if d.text == text]
                    f = book.font(found[0].s) if found else None
                    if f is None or (f.size, f.bold) != want[st] or (st in (0, 4) and not book.style(found[0].s).wrap):
                        fail(name, f"{tab} {text[:30]!r}: {'missing' if f is None else f'{f.size:g} pt' + (' bold' if f.bold else '')}; the source's {want[st][0]} pt{' bold' if want[st][1] else ''}")
                if t.link is None:
                    continue
                _, text, url, _ = t.link
                links = [d for d in cells.values() if d.f and d.f.startswith("HYPERLINK(") and url in d.f and text in d.f]
                if not links or book.font(links[0].s).colour != LINK_BLUE or not book.font(links[0].s).under:
                    fail(name, f"{tab}: the source's link {text!r} to {url} is not a link-blue, underlined HYPERLINK")
                for c, px in t.widths.items():
                    if abs(sh.width(c, 0) - px) > 1:
                        fail(name, f"{tab} column {letter(c)}: {sh.width(c, 0):.0f} px, the source's {px}")
        name = test("generate passes")
        if res["new"].returncode != 0:
            fail(name, f"exit {res['new'].returncode}\n{res['new'].stdout[-800:]}{res['new'].stderr[-1500:]}")
        name = test("4.3 every source a link")
        out = res["probe"].stdout + res["probe"].stderr
        if res["probe"].returncode != 2 or "probe_u" not in out:
            fail(name, f"a uniform(0, 1) with no address or mark, read by probe_u * 2 (no pick), gave exit "
                 f"{res['probe'].returncode}, not 2 naming probe_u: {out[-400:]!r}")
        t_flow(res, work)
        t_header_notes(res)
        t_stage(res, work)
        if res["factor"].returncode != 0:
            fail(test("2.3 every conversion factor named in its note"), f"the variant with a factor of the author's: exit {res['factor'].returncode}: {res['factor'].stderr[-400:]}")
        else:
            t_conversions_named(Case("factor variant", work / "factor.toml", Book(work / "factor" / "sheet.xlsx"), Book(BASE_XLSX), json.loads(BASE_JSON.read_text())), "factor variant")
        if res["rowform"].returncode != 0:
            fail(test("4.13 a method of one column has its credence in a row"), f"the variant with a beta on a method column: exit {res['rowform'].returncode}: {res['rowform'].stderr[-400:]}")
        else:
            row = Case("row-form variant", work / "rowform.toml", Book(work / "rowform" / "sheet.xlsx"), Book(BASE_XLSX), json.loads(BASE_JSON.read_text()))
            if not row_form(next(t for t in row.tabs if t["name"] == "Benefits")):
                fail(test("4.13 a method of one column has its credence in a row"), "the variant's Benefits tab is not in the row form")
            for t in (t_credence_row, t_credence_separator, t_credence_guide, t_picks, t_groups, t_one_role):
                t(row)
        lines = live_lines()
        t_old_copies(lines)
        t_look_snapshot()
        t_superseded(lines)
        if res["new"].returncode == 0:
            k = Case(LABEL, DATA, Book(work / "new" / "sheet.xlsx"), Book(BASE_XLSX), json.loads(BASE_JSON.read_text()))
            numbers = k.numbers()
            for t in (t_face, t_bold, t_link_colours, t_green, t_unit_formats, t_widths, t_heights, t_text_fits, t_spare,
                      t_borders, t_align, t_frozen, t_one_purpose, t_notes, t_citations, t_guide_short, t_guide_form,
                      t_setting, t_groups, t_dropdown, t_tab_labels, t_no_arrays, t_no_copies, t_picks, t_constants,
                      t_one_distribution, t_no_low_high, t_globals, t_spelling, t_sensitivity, t_no_errors, t_values,
                      t_csv_quoting, t_units_tables, t_heading_note_units, t_no_scaling_format, t_typed_shown, t_large_scientific,
                      t_credence_row, t_credence_separator, t_credence_guide, t_one_role):
                t(k)
            t_conversions_named(k)
            t_figures(k, numbers)
            t_one_minus(k, numbers)
            t_scaled(k, numbers)
            t_clipped(k, numbers)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if failures:
        failed = list(dict.fromkeys(f.split(":")[0].removeprefix("FAIL ") for f in failures))
        own = [f for f in failures if f.split(":")[0].removeprefix("FAIL ") not in DATA_TESTS and "[data file]" not in f.split(":")[0]]
        data = [f for f in failures if f not in own]
        print("\n".join(own))
        if data:
            print("\nFaults of the data file (synthetic.toml's to fix; a generator build changes no model formula or input):")
            print("\n".join(data))
        print(f"FAIL: {len(failed)} of {len(ran)} tests failed: {', '.join(failed)}")
        return 1
    print(f"PASS: {len(ran)} tests ran")
    return 0


if __name__ == "__main__":
    sys.exit(main())
