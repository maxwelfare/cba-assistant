"""A Monte Carlo sheet on the owner's older layout, read from its .xlsx export, written as a `sheet_script` data file.

    python -m tools.sheet_import import EXPORT.xlsx --out DIR
    python -m tools.sheet_import replay DATA.toml EXPORT.xlsx

`import` writes DIR/sheet.toml, DIR/crosswalk.tsv (one line an old column: `Tab!LETTER`, its name, the new tab, id
and letter, the letter `sheet_script.load` gives the written file, as its generated columns.tsv shows it) and
DIR/import_report.md (every value it inlined, every pick, pooled range, lookup and dropped tab, and every placeholder
name and guide placeholder, for the audit). It reads each column's header rows and its first draw row only, the row under
column A's "Graph" where column A reads 1: the rows below hold the same formula pasted down.

A model tab is a tab whose column A holds "Graph" and then 1. Its columns with a formula in the first draw row are
its data columns; any other column is a spacer, and a spacer's row-1 title names the run of columns after it (the
run before the first spacer takes the tab's name; a tab with no spacer has no groups). A data column is:

1. an input, where the formula is the template's generator (`sheet_script.GENERATOR`) over the column's own header
   cells: its kind and parameters are read from the cells its LET binds (dist, sd, lo, hi, peak, alpha, beta) and the
   mean cell it cites;
2. a pick, where a calculation draws the template's hash (a LET binding, or MAP over INDEX/MATCH of a block of
   columns by a row of cumulative shares): it becomes a uniform input (min 0, max 1) just left of it and an IF chain
   over it. Shares computed from a weights row labelled "Credence" in column A become `[[tab.method]]` credences,
   one group a method column; any other shares are inlined as numbers;
3. a calculation, translated from Sheets' syntax: ranges over the draw rows become the row's cell (`Tab!id`, aligned
   by draw number across tabs whose first draw rows differ), column A the draw's number (`draw`), a header cell its
   cached number, LET inlined; IF, EXP and PV pass through, and any other function is refused, naming the cell.

The first tab, the old Readme, becomes the guide (`kind = "guide"`, named Guide), with `interval = 0.9`, so that rows
12 and 14 show the 5th and 95th percentiles as the old rows did; the importer refuses a workbook whose first tab has
formulas or columns, since moving a tab moves its draws. From the Readme, read cell by cell in row order: a cell that
links (its text ends in an address, or the export's hyperlink names one) is a `references` entry, labelled by its own
text or by the text before it in its row; a "Name: description" text whose name is a tab of the new workbook is that
tab's `tabs` entry; the first paragraph before the "Notes" label is `what`; the paragraphs of the "Notes" block are
`notes` rows without a title (a paragraph stands in the label's column); the old section labels (Overview, Guides and
References, Notes, Tabs) are dropped, since the guide writes its own headings; and any other text goes to `notes` marked "[AUTHOR: review]". A field with no source
(`start_here`, `worked_example`, `details`, a tab without a description, and `what` where there is no paragraph) gets an
`[AUTHOR: ...]` placeholder saying what it needs; the import report lists each. Any other tab without formulas becomes
a text tab (a formula among them is dropped and reported), its formatting kept as `Importer.text` says: headings,
subheads, links and column widths. On any tab but a model tab, a =HYPERLINK("address","text") of two texts is read as
the cell's text with its link, as a link the export's hyperlink relation names.
Results and Report Ready Tables, and any other tab with formulas, become tables (`kind = "table"`): a reference to a
column's AVERAGE or 5th or 95th PERCENTILE header cell becomes `Tab!id.mean`, `.low` or `.high`; a range over the
draw rows `Tab!first:last`; one draw row `INDEX(Tab!id, n)`; the owner's interval text LET `INTERVAL(m, low, high)`;
an INDEX/MATCH lookup of a column by its row-1 name is resolved to the cell it finds, or the text "#N/A" where it
finds none. Correlation becomes a `kind = "sensitivity"` tab whose outputs are the net of each pair of columns its
HSTACK names (a column of the same tab computing one less the other), or the pair itself where no such column
exists. Report Ready Charts is dropped. A name or title over `sheet_script`'s limits is written as a placeholder
within them, the full text first in the column's note (or in the report). The importer never guesses: a cell it
cannot translate is refused, naming it (exit 2).

`replay` checks a data file against the export it came from, using Google's own cached values: each input's draws
recomputed with `sampling.sheet_uniforms` at the old tab's place, the old column and the old first draw row; each
calculation evaluated on the export's cached draws of the columns it cites (a pick on its uniform recomputed the
same way), so a fault shows in its own column; each table cell computed from the cached draws and cells. Everything
is compared with the cached value under `sheet_script`'s agreement rule (1e-7 of the column's largest value, a text
exactly). It prints each disagreement, naming the old tab and column or cell, and exits 0 when all agree, 1 on a
disagreement and 2 on a fault.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import numpy as np

from cost_benefit_engine.sampling import sheet_uniforms
from tools import sheet_script as ss
from tools.sheet_script import DRAW, Bin, Call, Cred, Fault, Floats, Neg, Node, Num, Pool, Ref, Span, Stat

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
Value = float | str | None  # a cached value: a number, a text (an error begins with "#"), or None for a blank cell
SECTION_LABELS = {"overview", "guides and references", "references", "notes", "tabs"}  # an old Readme's labels; "notes" and "tabs" open their blocks
AUTHOR_REVIEW = "[AUTHOR: review]"  # Readme text the importer could not place, written to notes
PLACEHOLDERS = {
    "worked_example": "[AUTHOR: the name of the tab whose draw 1 the reader follows across, the worked example]",
    "what": "[AUTHOR: one or two sentences saying what this sheet is, for whom, and what its totals cover]",
    "start_here": "[AUTHOR: two or three questions for the reader, each naming the tab and columns that answer it]",
    "tab": "[AUTHOR: one or two sentences saying what this tab holds]",
    "details": "[AUTHOR: a sentence naming the document of details and caveats, then its address]",
}
ROLES = {"Readme": "text", "Results": "table", "Report Ready Tables": "table", "Correlation": "sensitivity", "Report Ready Charts": "drop"}
SENSITIVITY_TAB = "Sensitivity"
LITERAL_LINK = re.compile(r'\s*HYPERLINK\(\s*"((?:[^"]|"")*)"\s*(?:,\s*"((?:[^"]|"")*)"\s*)?\)\s*', re.I)  # =HYPERLINK("address","text")
DRAWS = ss.DRAWS


# Reading the export ------------------------------------------------------------------------------------------------


@dataclass
class Sheet:
    name: str
    position: int  # SHEET() of the old workbook
    cells: dict[tuple[int, int], tuple[str | None, Value]]  # (row, column) -> (formula without "=", cached value)
    links: dict[tuple[int, int], str] = field(default_factory=lambda: dict[tuple[int, int], str]())  # a cell's hyperlink address
    looks: dict[tuple[int, int], tuple[float, bool]] = field(default_factory=lambda: dict[tuple[int, int], tuple[float, bool]]())  # a cell's font size and bold
    widths: dict[int, int] = field(default_factory=lambda: dict[int, int]())  # a column's width in px, where the export gives one
    merges: list[str] = field(default_factory=lambda: list[str]())  # the export's merged blocks ("B5:C5")

    def formula(self, r: int, c: int) -> str | None:
        return self.cells.get((r, c), (None, None))[0]

    def value(self, r: int, c: int) -> Value:
        return self.cells.get((r, c), (None, None))[1]


REF_TEXT = re.compile(r"(\"(?:[^\"]|\"\")*\"|'(?:[^']|'')+')|(?<![A-Za-z0-9_.$])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![A-Za-z0-9_(])")


def shift(text: str, dr: int, dc: int) -> str:
    """A shared formula's master text moved dr rows and dc columns, its relative references with it."""

    def one(m: re.Match[str]) -> str:
        if m.group(1):
            return m.group(1)
        col = m.group(3) if m.group(2) else ss.letter(ss.colnum(m.group(3)) + dc)
        row = m.group(5) if m.group(4) else str(int(m.group(5)) + dr)
        return f"{m.group(2)}{col}{m.group(4)}{row}"

    return REF_TEXT.sub(one, text)


def read(path: Path) -> list[Sheet]:
    """Every tab of an .xlsx export, in order, with each cell's formula (shared formulas expanded) and cached value."""
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        raise Fault(f"{path}: not an .xlsx file: {e}") from None
    names = z.namelist()
    shared = [] if "xl/sharedStrings.xml" not in names else [
        "".join(t.text or "" for t in si.iter(M + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si")]
    rels = {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    fonts: list[tuple[float, bool]] = []  # size, bold
    xfs: list[int] = []  # a cell style's font
    if "xl/styles.xml" in names:
        st = ET.fromstring(z.read("xl/styles.xml"))
        for f in st.iterfind(f"{M}fonts/{M}font"):
            sz, b = f.find(M + "sz"), f.find(M + "b")
            fonts.append((float(sz.get("val") or 10) if sz is not None else 10.0, b is not None and b.get("val") not in ("0", "false")))
        xfs = [int(x.get("fontId") or 0) for x in st.iterfind(f"{M}cellXfs/{M}xf")]
    sheets: list[Sheet] = []
    for position, sh in enumerate(ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"), start=1):
        target = rels[sh.get(R + "id")].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        cells: dict[tuple[int, int], tuple[str | None, Value]] = {}
        masters: dict[str, tuple[str, int, int]] = {}
        links: dict[tuple[int, int], str] = {}
        looks: dict[tuple[int, int], tuple[float, bool]] = {}
        widths: dict[int, int] = {}
        merges: list[str] = []
        folder, _, base = target.rpartition("/")
        rels_path = f"{folder}/_rels/{base}.rels"
        targets = {} if rels_path not in names else {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read(rels_path))}
        with z.open(target) as fh:
            for _, el in ET.iterparse(fh):
                if el.tag == M + "hyperlink":
                    m = re.fullmatch(r"([A-Z]+)(\d+)", el.get("ref") or "")
                    url = targets.get(el.get(R + "id"), "")
                    if m and url.startswith(("http://", "https://")):
                        links[(int(m.group(2)), ss.colnum(m.group(1)))] = url + (f"#{el.get('location')}" if el.get("location") else "")
                    continue
                if el.tag == M + "col" and el.get("width"):  # an xlsx width unit is 7 of Google's px
                    for c in range(int(el.get("min") or 1), int(el.get("max") or 0) + 1):
                        widths[c] = round(float(el.get("width") or 0) * 7)
                    continue
                if el.tag == M + "mergeCell":
                    merges.append(el.get("ref") or "")
                    continue
                if el.tag != M + "c":
                    continue
                m = re.fullmatch(r"([A-Z]+)(\d+)", el.get("r") or "")
                if not m:
                    continue
                r, c = int(m.group(2)), ss.colnum(m.group(1))
                f, v, kind = el.find(M + "f"), el.find(M + "v"), el.get("t")
                formula: str | None = None
                if f is not None:
                    formula = f.text or ""
                    if f.get("t") == "shared" and f.get("si") is not None:
                        si = cast(str, f.get("si"))
                        if formula:
                            masters[si] = (formula, r, c)
                        elif si in masters:
                            text, mr, mc = masters[si]
                            formula = shift(text, r - mr, c - mc)
                value: Value = None
                if kind == "inlineStr":
                    value = "".join(x.text or "" for x in el.iter(M + "t"))
                elif v is not None and v.text is not None:
                    value = shared[int(v.text)] if kind == "s" else v.text if kind in ("str", "e") else \
                        float(int(v.text)) if kind == "b" else float(v.text)
                if formula is not None or value is not None:
                    cells[(r, c)] = (formula, value)
                    style = int(el.get("s") or 0)
                    if style < len(xfs) and xfs[style] < len(fonts):
                        looks[(r, c)] = fonts[xfs[style]]
                el.clear()
        sheets.append(Sheet(sh.get("name") or "", position, cells, links, looks, widths, merges))
    return sheets


# Sheets' formulas, parsed ------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class XNum:
    v: float


@dataclass(frozen=True)
class XStr:
    s: str


@dataclass(frozen=True)
class XRef:
    sheet: str | None
    c1: int
    r1: int
    c2: int
    r2: int
    text: str  # as written, without the sheet


@dataclass(frozen=True)
class XName:
    n: str


@dataclass(frozen=True)
class XCall:
    fn: str  # upper case, without _xlfn.
    args: tuple[X, ...]


@dataclass(frozen=True)
class XBin:
    op: str
    a: X
    b: X


@dataclass(frozen=True)
class XNeg:
    x: X


X = XNum | XStr | XRef | XName | XCall | XBin | XNeg

XTOKEN = re.compile(
    r"\s*(?:(\"(?:[^\"]|\"\")*\")"
    r"|((?:(?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_.]*)!)?\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)(?![A-Za-z0-9_(])"
    r"|(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)"
    r"|([A-Za-z_][A-Za-z0-9_.]*)"
    r"|(<=|>=|<>|[-+*/^&=<>(),]))"
)
XCOMPARE = ("<=", ">=", "<>", "<", ">", "=")


def xref(text: str) -> XRef:
    sheet, _, cells = text.rpartition("!")
    if sheet.startswith("'"):
        sheet = sheet[1:-1].replace("''", "'")
    a, _, b = cells.partition(":")
    ma = cast(re.Match[str], re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", a))
    mb = cast(re.Match[str], re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", b or a))
    return XRef(sheet or None, ss.colnum(ma.group(1)), int(ma.group(2)), ss.colnum(mb.group(1)), int(mb.group(2)), cells)


def xparse(text: str, where: str) -> X:
    """A Sheets formula's tree: comparison below &, below + -, below * /, below ^ (left to right), below a sign."""
    tokens: list[tuple[str, str]] = []
    pos = 0
    while text[pos:].strip():
        m = XTOKEN.match(text, pos)
        if not m:
            raise Fault(f"{where}: unreadable formula at {text[pos:].strip()[:20]!r}")
        kind = ("str", "ref", "num", "name", "op")[cast(int, m.lastindex) - 1]
        tokens.append((kind, m.group(cast(int, m.lastindex))))
        pos = m.end()
    tokens.append(("end", ""))
    i = 0

    def is_op(*ops: str) -> bool:
        return tokens[i][0] == "op" and tokens[i][1] in ops

    def take(want: str | None = None) -> tuple[str, str]:
        nonlocal i
        if want is not None and tokens[i][1] != want:
            raise Fault(f"{where}: formula expects {want!r} where it has {tokens[i][1] or 'its end'!r}")
        i += 1
        return tokens[i - 1]

    def binary(level: int) -> X:
        ops = (XCOMPARE, ("&",), ("+", "-"), ("*", "/"), ("^",))[level]
        node = binary(level + 1) if level < 4 else unary()
        while is_op(*ops):
            op = take()[1]
            node = XBin(op, node, binary(level + 1) if level < 4 else unary())
            if op == "^" and is_op("^"):
                raise Fault(f"{where}: a^b^c without brackets is read differently by different programs; refused")
        return node

    def unary() -> X:
        if is_op("-"):
            take()
            return XNeg(unary())
        if is_op("+"):
            take()
            return unary()
        return atom()

    def atom() -> X:
        kind, value = take()
        if kind == "num":
            return XNum(float(value))
        if kind == "str":
            return XStr(value[1:-1].replace('""', '"'))
        if kind == "ref":
            return xref(value)
        if kind == "op" and value == "(":
            node = binary(0)
            take(")")
            return node
        if kind == "name" and is_op("("):
            take("(")
            args: list[X] = []
            if not is_op(")"):
                args.append(binary(0))
                while is_op(","):
                    take()
                    args.append(binary(0))
            take(")")
            fn = value.upper()
            return XCall(fn[len("_XLFN."):] if fn.startswith("_XLFN.") else fn, tuple(args))
        if kind == "name":
            return XName(value.upper() if value.upper() in ("TRUE", "FALSE") else value)
        raise Fault(f"{where}: formula has {value or 'its end'!r} where a value belongs")

    node = binary(0)
    take("")
    return node


def inline_let(node: X, env: dict[str, X] | None = None) -> X:
    """The tree with every LET's names replaced by their values."""
    env = env or {}
    match node:
        case XName(n) if n in env:
            return env[n]
        case XCall("LET", args):
            if len(args) < 3 or len(args) % 2 == 0:
                raise Fault(f"LET with {len(args)} arguments")
            inner = dict(env)
            for k in range(0, len(args) - 1, 2):
                name = args[k]
                if not isinstance(name, XName):
                    raise Fault(f"LET binds {name}, not a name")
                inner[name.n] = inline_let(args[k + 1], inner)
            return inline_let(args[-1], inner)
        case XCall(fn, args):
            return XCall(fn, tuple(inline_let(a, env) for a in args))
        case XBin(op, a, b):
            return XBin(op, inline_let(a, env), inline_let(b, env))
        case XNeg(x):
            return XNeg(inline_let(x, env))
        case _:
            return node


def number(v: float) -> Node:
    """A cached number as a formula writes it."""
    text = str(int(v)) if v.is_integer() and abs(v) < 1e15 else repr(abs(v))
    node = Num(text.lstrip("-"))
    return Neg(node) if v < 0 else node


# The old workbook, analysed ----------------------------------------------------------------------------------------


@dataclass
class Col:
    tab: str
    col: int  # the old column
    kind: str  # an input's kind, "calc" or "pick"
    id: str = ""
    name: str = ""
    citation: str = ""
    note: str = ""
    group: str | None = None
    params: dict[str, float] = field(default_factory=lambda: dict[str, float]())
    formula: Node | None = None
    uniform: str = ""  # a pick's uniform column's id
    methods: list[tuple[int, str, float]] = field(default_factory=lambda: list[tuple[int, str, float]]())  # a pick's: column, id, credence


@dataclass
class ModelTab:
    sheet: Sheet
    first: int
    cols: list[Col]
    methods: list[tuple[str, str, float]] = field(default_factory=lambda: list[tuple[str, str, float]]())  # id, group, credence
    about: str = ""
    taken: set[str] = field(default_factory=lambda: set[str]())  # the ids of its columns and methods


@dataclass
class Plan:
    order: list[tuple[str, str]]  # (role, old tab name) in the workbook's order, dropped tabs left out
    model: dict[str, ModelTab]
    tables: dict[str, dict[tuple[int, int], str | float | Node]]
    texts: dict[str, tuple[list[list[str]], list[int]]]  # a text tab's rows (with the marks `# ` and `## `) and widths in px
    outputs: list[tuple[str, str]]
    report: dict[str, list[str]]
    guide: dict[str, object]  # the guide's fields, from the old Readme


HASH = "MOD(SIN(ROW($A{f}:$A{l})*12.9898+COLUMN()*78.233+SHEET()*37.719)*43758.5453,1)"
GENERATOR = (
    "LET(u," + HASH + ",dist,{dist},sd,{sd},lo,{lo},hi,{hi},peak,{peak},alpha,{alpha},beta,{beta},"
    'IF(dist="beta",lo+(hi-lo)*_xlfn.BETA.INV(u,alpha,beta),IF(dist="constant",{m}+0*u,IF(dist="lognormal",EXP(NORMINV(u,LN({m}^2/SQRT({m}^2+sd^2)),SQRT(LN(1+sd^2/{m}^2)))),'
    'IF(dist="normal",NORMINV(u,{m},sd),IF(dist="power law",lo*(1-u)^(-1/(alpha-1)),IF(dist="triangular",IF(u<=(peak-lo)/(hi-lo),lo+SQRT(u*(hi-lo)*(peak-lo)),hi-SQRT((1-u)*(hi-lo)*(hi-peak))),'
    'IF(dist="uniform",lo+u*(hi-lo),""))))))))'
)
BINDINGS = re.compile(r"dist,(\$?[A-Z]+\$?\d+),sd,(\$?[A-Z]+\$?\d+),lo,(\$?[A-Z]+\$?\d+),hi,(\$?[A-Z]+\$?\d+),peak,(\$?[A-Z]+\$?\d+),"
                      r"alpha,(\$?[A-Z]+\$?\d+),beta,(\$?[A-Z]+\$?\d+),.*?IF\(dist=\"constant\",(\$?[A-Z]+\$?\d+)\+0\*u")


def squeeze(text: str) -> str:
    """A formula without the spaces and line breaks outside its texts."""
    return re.sub(r"(\"(?:[^\"]|\"\")*\")|\s+", lambda m: m.group(1) or "", text)


def text_of(v: Value) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() and abs(v) < 1e15 else repr(v)
    return str(v)


def slug(name: str, letter: str) -> str:
    words = re.findall(r"[a-z0-9]+", name.lower())
    out = ""
    for w in words:
        if len(out) + len(w) + (1 if out else 0) > 40:
            break
        out += ("_" if out else "") + w
    if not out or not out[0].isalpha():
        out = f"col_{letter.lower()}" + ("_" + out if out else "")
    return out[:48]


def unique(base: str, taken: set[str]) -> str:
    out, k = base, 2
    while out in taken or out in ("u", DRAW):
        out, k = f"{base}_{k}", k + 1
    taken.add(out)
    return out


class Importer:
    def __init__(self, sheets: list[Sheet]) -> None:
        self.sheets = {s.name: s for s in sheets}
        self.workbook = sheets
        self.report: dict[str, list[str]] = {}
        self.model: dict[str, ModelTab] = {}
        self.ids: dict[tuple[str, int], str] = {}  # (old tab, old column) -> new id of a data column

    def note(self, section: str, line: str) -> None:
        self.report.setdefault(section, []).append(line)

    def where(self, tab: str, c: int, r: int) -> str:
        return f"{ss.sheet_name(tab)}!{ss.letter(c)}{r}"

    # model tabs ------------------------------------------------------------------------------------------------

    def first_row(self, s: Sheet) -> int | None:
        graph = sorted(r for (r, c), (_, v) in s.cells.items() if c == 1 and v == "Graph")
        if not graph:
            return None
        ones = [r for (r, c), (_, v) in s.cells.items() if c == 1 and r > graph[0] and v == 1.0]
        return min(ones) if ones else None

    def plan(self) -> Plan:
        order: list[tuple[str, str]] = []
        for s in self.workbook:
            first = self.first_row(s)
            if first is None:  # a link written as =HYPERLINK("address","text") is the cell's text and its link, as an inserted one is
                for (r, c), (f, _) in list(s.cells.items()):
                    m = LITERAL_LINK.fullmatch(f or "")
                    if m:
                        url = m.group(1).replace('""', '"')
                        s.cells[(r, c)] = (None, (m.group(2) or "").replace('""', '"') or url)
                        s.links[(r, c)] = url
            role = ROLES.get(s.name) or ("model" if first is not None else
                                         "table" if any(f is not None for f, _ in s.cells.values()) else "text")
            if role == "model" and first is not None:
                self.model[s.name] = ModelTab(s, first, [])
            if role == "drop":
                self.note("Dropped tabs", f"{s.name}: not imported (chart data; each column's rows 12 to 14 and its histogram replace it)")
            else:
                order.append((role, s.name))
        if not order or order[0][0] != "text":
            raise Fault(f"{order[0][1] if order else 'the workbook'}: the first tab becomes the guide, so it is a Readme without "
                        "formulas; this one has formulas or columns, and moving a tab moves its draws")
        order[0] = ("guide", order[0][1])
        for mt in self.model.values():
            self.columns(mt)
        for mt in self.model.values():
            self.headers(mt)
        for mt in self.model.values():
            self.formulas(mt)
            self.groups(mt)
        tables: dict[str, dict[tuple[int, int], str | float | Node]] = {}
        texts: dict[str, tuple[list[list[str]], list[int]]] = {}
        outputs: list[tuple[str, str]] = []
        for role, name in order:
            if role == "table":
                tables[name] = self.table(self.sheets[name])
            elif role == "text":
                texts[name] = self.text(self.sheets[name])
            elif role == "sensitivity":
                outputs = self.outputs(self.sheets[name])
        if sum(1 for role, _ in order if role == "sensitivity") > 1:
            raise Fault("more than one tab to replace by the sensitivity tab")
        names = {name.casefold(): SENSITIVITY_TAB if role == "sensitivity" else name for role, name in order[1:]
                 if role != "sensitivity" or outputs}
        guide = self.guide(self.sheets[order[0][1]], names)
        return Plan(order, self.model, tables, texts, outputs, self.report, guide)

    def data_columns(self, mt: ModelTab) -> list[int]:
        return sorted(c for (r, c), (f, _) in mt.sheet.cells.items() if r == mt.first and c > 1 and f)

    def columns(self, mt: ModelTab) -> None:
        """Each data column's kind, and its input parameters; ids are given in headers()."""
        s, first = mt.sheet, mt.first
        last = first + DRAWS - 1
        for c in self.data_columns(mt):
            f = cast(str, s.formula(first, c))
            where = self.where(s.name, c, first)
            if "BETA.INV" in f:
                mt.cols.append(self.generator(mt, c, f, where, last))
            elif "12.9898" in f:
                mt.cols.append(Col(s.name, c, "pick"))
            else:
                mt.cols.append(Col(s.name, c, "calc"))

    def generator(self, mt: ModelTab, c: int, f: str, where: str, last: int) -> Col:
        s = mt.sheet
        m = BINDINGS.search(squeeze(f))
        if not m:
            raise Fault(f"{where}: a generator whose LET bindings are not the template's")
        refs = dict(zip(("dist", "sd", "lo", "hi", "peak", "alpha", "beta", "m"), m.groups()))
        if squeeze(f) != squeeze(GENERATOR.format(f=mt.first, l=last, **refs)):
            raise Fault(f"{where}: the formula is not the template's generator over its own header cells")
        cells = {k: xref(v) for k, v in refs.items()}
        if any(x.c1 != c or x.r1 >= mt.first for x in cells.values()):
            raise Fault(f"{where}: the generator reads cells outside its own column's header")
        kind = s.value(cells["dist"].r1, c)
        if not isinstance(kind, str) or kind not in ss.REQUIRED:
            raise Fault(f"{where}: kind {kind!r} (cell {ss.letter(c)}{cells['dist'].r1}) is none of the template's seven")
        col = Col(s.name, c, kind)
        for p in sorted(ss.REQUIRED[kind], key=ss.PARAM_ROW.__getitem__):
            ref = cells["m" if p == "mean" else p]
            v = s.value(ref.r1, c)
            if not isinstance(v, float):
                raise Fault(f"{where}: {p} (cell {ss.letter(c)}{ref.r1}) holds {v!r}, not a number")
            if s.formula(ref.r1, c):
                self.note("Parameters taken from a formula's cached value", f"{self.where(s.name, c, ref.r1)} ({p}) = {v!r}: `={s.formula(ref.r1, c)}`")
            col.params[p] = v
        return col

    def headers(self, mt: ModelTab) -> None:
        """Names, ids, citations, notes and groups; a pick's uniform column and a tab's methods."""
        s, first = mt.sheet, mt.first
        about = text_of(s.value(1, 1)).strip()
        mt.about = about if about and not ss.too_long(about, ss.TITLE_CHARS) else s.name
        if mt.about != about:
            self.note("Placeholder names", f"{s.name}!A1 (the tab's about) written as {mt.about!r}; the original: {about!r}")
        labels = {r: text_of(s.value(r, 1)).strip().lower() for r in range(2, first)}
        cite_rows = [r for r, lab in labels.items() if lab.startswith("citation")]
        note_rows = cite_rows[1:] + [r for r, lab in labels.items() if lab.startswith("plain language")]
        taken = mt.taken
        for col in mt.cols:
            letter = ss.letter(col.col)
            name = text_of(s.value(1, col.col)).strip()
            texts: list[str] = []
            for r in cite_rows[:1] + sorted(note_rows):
                if s.formula(r, col.col) is not None:
                    self.note("Header formulas dropped", f"{self.where(s.name, col.col, r)}: `={s.formula(r, col.col)}`")
                    continue
                t = text_of(s.value(r, col.col)).strip()
                if t:
                    texts.append(t)
            if col.kind in ss.REQUIRED and cite_rows and texts and s.formula(cite_rows[0], col.col) is None and text_of(s.value(cite_rows[0], col.col)).strip():
                col.citation, notes = texts[0], texts[1:]
            else:
                notes = texts
            col.id = unique(slug(name, letter), taken)
            if not name:
                name = f"Unnamed {letter}"
                self.note("Placeholder names", f"{s.name}!{letter}: no name; written as {name!r}")
            elif ss.too_long(name, ss.NAME_CHARS):
                notes = [f"Full name: {name}"] + notes
                self.note("Placeholder names", f"{s.name}!{letter}: name written as \"Name {letter} (see note)\"; the original: {name!r}")
                name = f"Name {letter} (see note)"
            col.name = name
            col.note = "\n\n".join(notes)
            self.ids[(s.name, col.col)] = col.id
        for col in [c for c in mt.cols if c.kind == "pick"]:
            col.uniform = unique(col.id + "_draw", taken)

    def groups(self, mt: ModelTab) -> None:
        """Runs of data columns between spacers, each a group named by the title of the spacer before it (the first
        run, the tab's name); a pick's method columns a group each, "<group> method k"."""
        s = mt.sheet
        data = [c.col for c in mt.cols]
        if data == list(range(2, 2 + len(data))):
            return  # no spacer: no groups
        runs: list[list[int]] = []
        for c in data:
            if runs and runs[-1][-1] == c - 1:
                runs[-1].append(c)
            else:
                runs.append([c])
        used: set[str] = set()
        by_col = {c.col: c for c in mt.cols}
        for k, run in enumerate(runs):
            title, c = "", run[0] - 1
            while c > 1 and c not in by_col and not title:
                title = text_of(s.value(1, c)).strip()
                c -= 1
            if title:
                self.note("Spacer columns", f"{s.name}!{ss.letter(c + 1)}: a spacer; its title {title!r} names the group from {ss.letter(run[0])}")
            group = title or (s.name if k == 0 else "")
            if not group or ss.too_long(group, ss.NAME_CHARS):
                group = f"Group {ss.letter(run[0])}"
                if title:
                    self.note("Placeholder names", f"{s.name}: the group from {ss.letter(run[0])} written as {group!r}; its title: {title!r}")
            base, n = group, 2
            while group in used:
                group, n = f"{base} {n}", n + 1
            used.add(group)
            for c in run:
                by_col[c].group = group
        for col in mt.cols:
            for k, (c, mid, credence) in enumerate(col.methods, start=1):
                g = cast(str, by_col[c].group)
                name = f"{g} method {k}"
                if ss.too_long(name, ss.NAME_CHARS):
                    name = f"Group {ss.letter(c)} method {k}"
                by_col[c].group = name
                mt.methods.append((mid, name, credence))
        seen: list[str | None] = []
        for c in mt.cols:
            if not seen or seen[-1] != c.group:
                if c.group in seen:
                    raise Fault(f"{s.name}: a pick's method columns do not stand at the start of their run of columns")
                seen.append(c.group)

    # formulas ----------------------------------------------------------------------------------------------------

    def formulas(self, mt: ModelTab) -> None:
        s = mt.sheet
        for col in mt.cols:
            if col.kind in ss.REQUIRED:
                continue
            where = self.where(s.name, col.col, mt.first)
            tree = xparse(cast(str, s.formula(mt.first, col.col)), where)
            col.formula = self.column_node(mt, col, tree, {}, where)
            if col.kind == "pick":
                self.note("Picks", f"{where}: a pick; its random number is the new uniform column {col.uniform} just left of it, and it reads `{ss.source(col.formula, s.name)}`")

    def column_node(self, mt: ModelTab, col: Col, node: X, env: dict[str, Node], where: str) -> Node:
        here = mt.sheet.name

        def go(n: X) -> Node:
            return self.column_node(mt, col, n, env, where)

        match node:
            case XNum(v):
                return number(v)
            case XName(n) if n in env:
                return env[n]
            case XRef():
                return self.draw_ref(mt, node, where)
            case XNeg(x):
                return Neg(go(x))
            case XBin(op, a, b) if op in ss.LEVEL:
                return Bin(op, go(a), go(b))
            case XCall("LET", args):
                inner = dict(env)
                if len(args) < 3 or len(args) % 2 == 0:
                    raise Fault(f"{where}: LET with {len(args)} arguments")
                for k in range(0, len(args) - 1, 2):
                    name, value = args[k], args[k + 1]
                    if not isinstance(name, XName):
                        raise Fault(f"{where}: LET binds {name}")
                    if value == xparse(HASH.format(f=mt.first, l=mt.first + DRAWS - 1), where):
                        if col.kind != "pick":
                            raise Fault(f"{where}: a hash outside a pick")
                        inner[name.n] = Ref(here, col.uniform)
                    else:
                        inner[name.n] = self.column_node(mt, col, value, inner, where)
                return self.column_node(mt, col, args[-1], inner, where)
            case XCall("MAP", args):
                return self.map_pick(mt, col, args, env, where)
            case XCall(fn, args) if fn in ("IF", "EXP", "PV") and len(args) == ss.FUNCTIONS[fn]:
                return Call(fn, tuple(go(a) for a in args))
            case XCall(fn, args):
                raise Fault(f"{where}: function {fn} with {len(args)} arguments is outside what the importer translates (IF, EXP, PV, LET and the pick forms)")
            case _:
                raise Fault(f"{where}: {node} has no place in a column's formula")

    def draw_ref(self, mt: ModelTab, ref: XRef, where: str) -> Node:
        """A reference in a column's formula: a column's draw row, column A's draw number, or a header cell's number."""
        tab = ref.sheet or mt.sheet.name
        if tab not in self.model:
            raise Fault(f"{where}: cites {tab}!{ref.text}, which is no model tab")
        other = self.model[tab]
        if ref.r1 == other.first:
            if ref.c1 != ref.c2:
                raise Fault(f"{where}: cites {tab}!{ref.text}, a block of columns, where one column's draws belong")
            if ref.c1 == 1:
                return Ref(tab, DRAW)
            if (tab, ref.c1) not in self.ids:
                raise Fault(f"{where}: cites {tab}!{ref.text}, a column without a formula in its first draw row")
            return Ref(tab, self.ids[(tab, ref.c1)])
        if ref.r1 < other.first and (ref.r1, ref.c1) == (ref.r2, ref.c2):
            v = other.sheet.value(ref.r1, ref.c1)
            if v is None:
                v = 0.0
                self.note("Header cells inlined", f"{where}: {tab}!{ref.text} is blank, read as 0 (as Sheets reads it)")
            elif not isinstance(v, float):
                raise Fault(f"{where}: cites {tab}!{ref.text}, which holds {v!r}, not a number")
            else:
                self.note("Header cells inlined", f"{where}: {tab}!{ref.text} inlined as {v!r}")
            return number(v)
        raise Fault(f"{where}: cites {tab}!{ref.text}, neither the first draw row nor one header cell")

    def map_pick(self, mt: ModelTab, col: Col, args: tuple[X, ...], env: dict[str, Node], where: str) -> Node:
        """MAP(SEQUENCE(ROWS(r),1), u, LAMBDA(i, x, INDEX(block, i, MATCH(TRUE, x<=shares, 0)))) as an IF chain."""
        s = mt.sheet
        shape = f"{where}: MAP is translated only in the pick form MAP(SEQUENCE(ROWS(...),1),u,LAMBDA(i,x,INDEX(block,i,MATCH(TRUE,x<=shares,0))))"
        if len(args) != 3 or not (isinstance(args[0], XCall) and args[0].fn == "SEQUENCE") or not isinstance(args[1], XName):
            raise Fault(shape)
        lam = args[2]
        if not (isinstance(lam, XCall) and lam.fn == "LAMBDA" and len(lam.args) == 3):
            raise Fault(shape)
        i, x, body = lam.args
        if not (isinstance(i, XName) and isinstance(x, XName) and isinstance(body, XCall) and body.fn == "INDEX" and len(body.args) == 3):
            raise Fault(shape)
        block, i2, match = body.args
        if not (isinstance(block, XRef) and i2 == i and isinstance(match, XCall) and match.fn == "MATCH" and len(match.args) == 3
                and match.args[0] == XName("TRUE") and match.args[2] == XNum(0.0)):
            raise Fault(shape)
        test = match.args[1]
        if not (isinstance(test, XBin) and test.op == "<=" and test.a == x and isinstance(test.b, XRef)):
            raise Fault(shape)
        shares = test.b
        if args[1].n not in env:
            raise Fault(f"{where}: MAP over {args[1].n}, which is not the pick's random number")
        u = env[args[1].n]
        if block.sheet not in (None, s.name) or block.r1 != mt.first or shares.sheet not in (None, s.name) or shares.r1 != shares.r2 \
                or (block.c1, block.c2) != (shares.c1, shares.c2) or shares.r1 >= mt.first:
            raise Fault(f"{where}: the block {block.text} and the shares {shares.text} are not the pick's own columns and header row")
        cols = list(range(block.c1, block.c2 + 1))
        values = [s.value(shares.r1, c) for c in cols]
        if not all(isinstance(v, float) for v in values) or cast(float, values[-1]) != 1.0 or \
                any(cast(float, a) > cast(float, b) for a, b in zip(values, values[1:])):
            raise Fault(f"{where}: the shares {shares.text} are not rising numbers ending at 1: {values}")
        branches = [Ref(s.name, self.ids[(s.name, c)]) if (s.name, c) in self.ids else None for c in cols]
        if any(b is None for b in branches):
            raise Fault(f"{where}: the block {block.text} holds a column without a formula in its first draw row")
        weights = self.credences(mt, shares, cols, cast(list[float], values), where)
        if weights is not None:
            col.methods = [(c, unique(f"method_{ss.letter(c).lower()}", mt.taken), w) for c, w in zip(cols, weights)]
            creds: list[Node] = [Cred(mid, w) for _, mid, w in col.methods]
            total = creds[0]
            for cr in creds[1:]:
                total = Bin("+", total, cr)
            thresholds: list[Node] = []
            running = creds[0]
            for k in range(len(cols) - 1):
                if k:
                    running = Bin("+", running, creds[k])
                thresholds.append(Bin("/", running, total))
            self.note("Picks", f"{where}: the shares {shares.text} are the cumulative shares of the credences above them, written as [[tab.method]] entries")
        else:
            thresholds = [number(cast(float, v)) for v in values[:-1]]
            self.note("Header cells inlined", f"{where}: the shares {shares.text} inlined as {values[:-1]}")
        node = cast(Node, branches[-1])
        for t, b in zip(reversed(thresholds), reversed(branches[:-1])):
            node = Call("IF", (Bin("<=", u, t), cast(Node, b), node))
        return node

    def credences(self, mt: ModelTab, shares: XRef, cols: list[int], values: list[float], where: str) -> list[float] | None:
        """The weights behind cumulative shares sum($C6:C6)/sum($C6:$J6), where their row is labelled Credence."""
        s = mt.sheet
        f = s.formula(shares.r1, cols[0])
        if not f:
            return None
        m = re.fullmatch(r"(?i)sum\(\$?[A-Z]+\$?(\d+):\$?[A-Z]+\$?\d+\)/sum\(\$?[A-Z]+\$?\d+:\$?[A-Z]+\$?\d+\)", squeeze(f))
        if not m or text_of(s.value(int(m.group(1)), 1)).strip().lower() != "credence":
            return None
        row = int(m.group(1))
        weights = [s.value(row, c) for c in cols]
        if not all(isinstance(w, float) and w > 0 for w in weights):
            raise Fault(f"{where}: the credences of row {row} are not all numbers above 0: {weights}")
        w = np.asarray(weights, dtype=np.float64)
        if not np.allclose(np.cumsum(w) / w.sum(), values, rtol=0, atol=1e-9):
            raise Fault(f"{where}: the shares {shares.text} are not the cumulative shares of the credences in row {row}")
        return [float(x) for x in w]

    # tables ------------------------------------------------------------------------------------------------------

    def table(self, s: Sheet) -> dict[tuple[int, int], str | float | Node]:
        cells: dict[tuple[int, int], str | float | Node] = {}
        for (r, c), (f, v) in sorted(s.cells.items()):
            where = self.where(s.name, c, r)
            if f is not None:
                node = self.table_x(s.name, inline_let(xparse(f, where)), where, set())
                if isinstance(node, str):
                    cells[(r, c)] = node
                elif node is None:
                    self.note("Blank references", f"{where}: `={f}` cites a blank cell; written as an empty cell")
                else:
                    cells[(r, c)] = node
            elif isinstance(v, float):
                cells[(r, c)] = v
            elif isinstance(v, str) and v:
                if v.startswith("="):
                    raise Fault(f"{where}: a text beginning with '=', which Google would read as a formula")
                url = s.links.get((r, c))
                cells[(r, c)] = v if url is None or v == url else f"{v} {url}"  # a text ending in an address is written as a link
        return cells

    def table_x(self, home: str, node: X, where: str, seen: set[tuple[str, int, int]]) -> Node | str | None:
        """A table's formula, its unqualified references to tab home; None for a reference to a blank cell, a text
        for a lookup that finds nothing."""

        def go(n: X) -> Node:
            v = self.table_x(home, n, where, seen)
            if v is None:
                self.note("Blank references", f"{where}: a blank cell read as 0 (as Sheets reads it)")
                return Num("0")
            if isinstance(v, str):
                raise Fault(f"{where}: a text {v!r} inside a calculation")
            return v

        match node:
            case XNum(v):
                return number(v)
            case XRef():
                return self.table_ref(home, node, where, seen)
            case XNeg(x):
                return Neg(go(x))
            case XBin("&", _, _):
                return self.interval(home, node, where, seen)
            case XBin(op, a, b) if op in ss.LEVEL:
                return Bin(op, go(a), go(b))
            case XCall("INDEX", (XRef() as values, XCall("MATCH", (key, XRef() as names, XNum(0.0))))):
                return self.lookup(home, values, key, names, where, seen)
            case XCall(fn, args) if fn in ("SUM", "ABS", "AVERAGE", "PERCENTILE"):
                return Call(fn, tuple(self.pooled(home, a, where) if k == 0 and fn in ("AVERAGE", "PERCENTILE") else
                                      self.span(home, a, where) if fn == "SUM" and isinstance(a, XRef) and (a.r1, a.c1) != (a.r2, a.c2) else go(a)
                                      for k, a in enumerate(args)))
            case XCall(fn, args):
                raise Fault(f"{where}: function {fn} is outside what a table translates (SUM, ABS, AVERAGE, PERCENTILE, the interval text and lookups)")
            case _:
                raise Fault(f"{where}: {node} has no place in a table's formula")

    def span(self, home: str, ref: XRef, where: str) -> Node:
        if (ref.sheet or home) != home or home in self.model:
            raise Fault(f"{where}: SUM over {ref.text}, which is not a block of the table's own cells")
        a, _, b = ref.text.partition(":")
        return Span(ss.cell_ref(a), ss.cell_ref(b))

    def pooled(self, home: str, ref: X, where: str) -> Node:
        """A range over the draw rows of a run of adjacent data columns."""
        if not isinstance(ref, XRef) or (ref.sheet or home) not in self.model:
            raise Fault(f"{where}: AVERAGE or PERCENTILE of {ref}, which is not a range of a model tab's draws")
        tab = ref.sheet or home
        mt = self.model[tab]
        last = mt.first + DRAWS - 1
        if ref.r1 != mt.first or ref.r2 < last:
            raise Fault(f"{where}: {tab}!{ref.text} does not cover the draw rows {mt.first} to {last}")
        cols = list(range(ref.c1, ref.c2 + 1))
        if any((tab, c) not in self.ids for c in cols):
            raise Fault(f"{where}: {tab}!{ref.text} holds a column without a formula in its first draw row")
        extra = [(r, c) for (r, c) in mt.sheet.cells if c in cols and last < r <= ref.r2 and mt.sheet.value(r, c) is not None]
        if extra:
            raise Fault(f"{where}: {tab}!{ref.text} holds values below the draws, at {ss.letter(extra[0][1])}{extra[0][0]}")
        ids = tuple(self.ids[(tab, c)] for c in cols)
        order = [i for x in mt.cols for i in ([x.uniform] if x.uniform else []) + [x.id]]  # the new tab's ids
        if order[order.index(ids[0]):order.index(ids[-1]) + 1] != list(ids):
            raise Fault(f"{where}: {tab}!{ref.text} would pool other columns in the new tab")
        if len(cols) > 1:
            self.note("Pooled ranges", f"{where}: {tab}!{ref.text}, the draws of {len(cols)} columns pooled")
        return Pool(tab, ids)

    def table_ref(self, home: str, ref: XRef, where: str, seen: set[tuple[str, int, int]]) -> Node | str | None:
        tab = ref.sheet or home
        single = (ref.r1, ref.c1) == (ref.r2, ref.c2)
        if tab == home and home not in self.model:
            if not single:
                raise Fault(f"{where}: the block {ref.text} belongs inside SUM")
            return ss.cell_ref(ref.text)
        if tab not in self.model:
            raise Fault(f"{where}: cites {tab}!{ref.text}, which is neither the table's own cell nor a model tab's")
        mt = self.model[tab]
        if not single:
            raise Fault(f"{where}: cites the block {tab}!{ref.text} outside AVERAGE or PERCENTILE")
        if mt.first <= ref.r1 < mt.first + DRAWS:
            if (tab, ref.c1) not in self.ids:
                raise Fault(f"{where}: cites {tab}!{ref.text}, a draw of a column without a formula in its first draw row")
            n = ref.r1 - mt.first + 1
            self.note("Single draws", f"{where}: cites {tab}!{ref.text}, the column's draw {n} alone, written INDEX({ss.sheet_name(tab)}!{self.ids[(tab, ref.c1)]}, {n})")
            return Call("INDEX", (Pool(tab, (self.ids[(tab, ref.c1)],)), Num(str(n))))
        if ref.r1 >= mt.first:
            raise Fault(f"{where}: cites {tab}!{ref.text}, below the draws")
        return self.header(tab, ref.c1, ref.r1, where, seen)

    def header(self, tab: str, c: int, r: int, where: str, seen: set[tuple[str, int, int]]) -> Node | str | None:
        """A model tab's header cell in a table: a column's mean or percentile, an interval text, or a number."""
        mt = self.model[tab]
        f, v = mt.sheet.formula(r, c), mt.sheet.value(r, c)
        cell = f"{tab}!{ss.letter(c)}{r}"
        if f is None:
            if v is None:
                return None
            if isinstance(v, float):
                self.note("Header cells inlined", f"{where}: {cell} inlined as {v!r}")
                return number(v)
            raise Fault(f"{where}: cites {cell}, a text {v!r}")
        if (tab, c, r) in seen:
            raise Fault(f"{where}: {cell} cites itself")
        tree = inline_let(xparse(f, cell))
        draws = XRef(None, c, mt.first, c, mt.first + DRAWS - 1, "")
        stat = None
        if isinstance(tree, XCall) and tree.args and isinstance(tree.args[0], XRef) and (tree.args[0].sheet or tab) == tab \
                and (tree.args[0].c1, tree.args[0].r1, tree.args[0].c2, tree.args[0].r2) == (draws.c1, draws.r1, draws.c2, draws.r2):
            if tree.fn == "AVERAGE" and len(tree.args) == 1:
                stat = "mean"
            elif tree.fn == "PERCENTILE" and len(tree.args) == 2 and tree.args[1] in (XNum(0.05), XNum(0.95)):
                stat = "low" if tree.args[1] == XNum(0.05) else "high"
        if stat is not None:
            if (tab, c) not in self.ids:
                raise Fault(f"{where}: {cell} summarises a column without a formula in its first draw row")
            return Stat(tab, self.ids[(tab, c)], stat)
        return self.table_x(tab, tree, f"{where} (through {cell})", seen | {(tab, c, r)})

    def lookup(self, home: str, values: XRef, key: X, names: XRef, where: str, seen: set[tuple[str, int, int]]) -> Node | str | None:
        """INDEX(Tab!row a, MATCH(key, Tab!row b, 0)), resolved now to the cell it finds."""
        tab = values.sheet or home
        if tab not in self.model or (names.sheet or home) != tab or values.r1 != values.r2 or names.r1 != names.r2 \
                or (values.c1, values.c2) != (names.c1, names.c2):
            raise Fault(f"{where}: a lookup other than INDEX(Tab!row, MATCH(key, Tab!row of the same columns, 0))")
        if not (isinstance(key, XRef) and (key.sheet or home) == home and home not in self.model and (key.r1, key.c1) == (key.r2, key.c2)):
            raise Fault(f"{where}: a lookup whose key is not one of the table's own cells")
        table = self.sheets[home]
        if table.formula(key.r1, key.c1) is not None:
            raise Fault(f"{where}: a lookup whose key {key.text} is a formula; the importer resolves only a typed key")
        want = text_of(table.value(key.r1, key.c1)).strip().casefold()
        sheet = self.model[tab].sheet
        found = next((c for c in range(names.c1, names.c2 + 1) if want and text_of(sheet.value(names.r1, c)).strip().casefold() == want), None)
        if found is None:
            self.note("Lookups", f"{where}: no column of {tab} row {names.r1} is named {want!r}; written as the text #N/A, as Sheets shows it")
            return "#N/A"
        self.note("Lookups", f"{where}: resolved to {tab}!{ss.letter(found)}{values.r1}, the column named {want!r}")
        return self.header(tab, found, values.r1, where, seen)

    def interval(self, home: str, node: X, where: str, seen: set[tuple[str, int, int]]) -> Node:
        """The owner's interval text, round(m,p)&" ["&round(lo,p)&", "&round(hi,p)&"]", p = 1-FLOOR(LOG10(ABS(m)),1)."""
        parts: list[X] = []

        def flat(n: X) -> None:
            if isinstance(n, XBin) and n.op == "&":
                flat(n.a)
                flat(n.b)
            else:
                parts.append(n)

        flat(node)
        shape = f"{where}: a text formula other than the interval text round(m,p)&\" [\"&round(low,p)&\", \"&round(high,p)&\"]\""
        if len(parts) != 6 or parts[1] != XStr(" [") or parts[3] != XStr(", ") or parts[5] != XStr("]"):
            raise Fault(shape)
        three: list[X] = []
        for p in (parts[0], parts[2], parts[4]):
            if not (isinstance(p, XCall) and p.fn == "ROUND" and len(p.args) == 2):
                raise Fault(shape)
            three.append(p.args[0])
        precision = XBin("-", XNum(1.0), XCall("FLOOR", (XCall("LOG10", (XCall("ABS", (three[0],)),)), XNum(1.0))))
        if any(cast(XCall, p).args[1] != precision for p in (parts[0], parts[2], parts[4])):
            raise Fault(shape)
        args: list[Node] = []
        for x in three:
            v = self.table_x(home, x, where, seen)
            if v is None or isinstance(v, str):
                raise Fault(f"{where}: the interval text reads a blank or a text")
            args.append(v)
        return Call("INTERVAL", tuple(args))

    # text tabs and the sensitivity tab -------------------------------------------------------------------------

    def text(self, s: Sheet) -> tuple[list[list[str]], list[int]]:
        """A text tab's rows and column widths, its formatting kept in the form sheet_script writes: a bold text larger
        than the tab's body size (its most common text size) is a heading (`# `, Arial 16 bold), a bold one at or below
        it a subhead (`## `, Arial 10 bold), any plain text body (Arial 10, wrapped), whatever its size, escaped with a
        backslash where it begins as a mark would ("\\# of households", `sheet_script.marked`); a link the text
        followed by its address (a HYPERLINK formula); the export's widths in px, a column it leaves unsized Google's
        100 px. A merge is not kept (the owner, 2026-11-20: "widen the column
        if you can, merging causes all kinds of mess"); its text stays in its first cell."""
        rows: dict[int, dict[int, str]] = {}
        sizes = Counter(s.looks[k][0] for k, (f, v) in s.cells.items() if f is None and k in s.looks and text_of(v))
        body = sizes.most_common(1)[0][0] if sizes else 0.0  # the tab's body size: its most common text size
        for (r, c), (f, v) in s.cells.items():
            if f is not None:
                self.note("Text tabs", f"{self.where(s.name, c, r)}: the formula `={f[:120]}` dropped")
                continue
            t = text_of(v)
            if t:
                if t.startswith("=") or ss.PLACEHOLDER.search(t) or t == ss.SETTING:
                    raise Fault(f"{self.where(s.name, c, r)}: a text {t[:40]!r} that sheet_script would read as a formula or placeholder")
                url = s.links.get((r, c))
                t = t if url is None or t == url else f"{t} {url}"
                size, bold = s.looks.get((r, c), (body, False))
                plain = "\\" + t if ss.marked(t) != ("", t) else t  # a plain text that would read as a mark ("# of households") keeps its words
                rows.setdefault(r, {})[c] = plain if not bold else ("# " if size > body else "## ") + t
        for ref in s.merges:
            self.note("Text tabs", f"{s.name}!{ref}: merged in the export; not merged here (widen, never merge), its text in its first cell")
        if not rows:
            return [[""]], []
        last = max(max(cs) for cs in rows.values())
        widths = [s.widths.get(c, ss.TABLE_PX) for c in range(1, last + 1)] if any(c <= last for c in s.widths) else []
        return [[rows.get(r, {}).get(c, "") for c in range(1, max(rows.get(r, {0: ""})) + 1)] for r in range(1, max(rows) + 1)], widths

    def guide(self, s: Sheet, names: dict[str, str]) -> dict[str, object]:
        """The guide's fields from the old Readme (the module's header gives the rules); names maps each tab of the new
        workbook but the guide, by its old name folded to lower case, to its new name."""
        texts: dict[int, list[tuple[int, str]]] = {}
        for (r, c), (f, v) in sorted(s.cells.items()):
            if f is not None:
                self.note("Guide", f"{self.where(s.name, c, r)}: the formula `={f[:120]}` dropped")
            elif text_of(v).strip():
                texts.setdefault(r, []).append((c, text_of(v).strip()))
        references: list[list[str]] = []
        described: dict[str, str] = {}
        notes: list[list[str]] = []
        what: str | None = None
        section = ""
        notes_col = 0  # the Notes label's column: the block's paragraphs stand under it
        for r, row in sorted(texts.items()):
            used: set[int] = set()
            for k, (c, t) in enumerate(row):
                url = s.links.get((r, c))
                shown, tail = ss.link(t)
                if url is not None and shown != url:
                    references.append([t, url])
                elif url is not None or tail is not None:
                    before = [j for j in range(k) if j not in used and row[j][1].casefold().rstrip(":") not in SECTION_LABELS]
                    label = "" if shown != (tail or url) else row[before[-1]][1] if before else ""
                    used.update(before[-1:] if label else [])
                    references.append([label, t if tail is not None else cast(str, url)])
                else:
                    continue
                used.add(k)
            for k, (c, t) in enumerate(row):
                m = re.fullmatch(r"([^:]{1,60}?)\s*:\s+(.+)", t, re.S)
                where = self.where(s.name, c, r)
                if k in used:
                    continue
                if t.casefold().rstrip(":") in SECTION_LABELS:
                    section = t.casefold().rstrip(":") if t.casefold().rstrip(":") in ("notes", "tabs") else section
                    notes_col = c if t.casefold().rstrip(":") == "notes" else notes_col
                    self.note("Guide", f"{where}: the label {t!r} dropped; the guide writes its own headings")
                elif m and m.group(1).casefold() in names and names[m.group(1).casefold()] not in described:
                    described[names[m.group(1).casefold()]] = m.group(2)
                elif section == "notes" and c == notes_col:
                    notes.append(["", t])
                elif what is None and not section:
                    what = t
                else:
                    notes.append(["", f"{AUTHOR_REVIEW} {t}"])
                    self.note("Guide", f"{where}: unmapped, written to notes as {AUTHOR_REVIEW}: {t[:80]!r}")
        fields: dict[str, object] = {"interval": 0.9}
        for key, text in (("worked_example", None), ("what", what), ("start_here", None)):
            fields[key] = text if text is not None else PLACEHOLDERS[key]
        fields["notes"] = notes
        tabs = [[n, described.get(n, PLACEHOLDERS["tab"])] for n in names.values()]
        fields["tabs"] = tabs
        fields["references"] = references
        fields["details"] = PLACEHOLDERS["details"]
        for key, v in fields.items():
            if isinstance(v, str) and v.startswith(ss.AUTHOR):
                self.note("Guide", f"{key}: no source in the Readme; written as the placeholder {v!r}")
        for n, d in tabs:
            if d.startswith(ss.AUTHOR):
                self.note("Guide", f"tabs, {n}: no description in the Readme; written as the placeholder {d!r}")
        return fields

    def outputs(self, s: Sheet) -> list[tuple[str, str]]:
        """The net of each pair of columns the tab's HSTACK names, or the pair itself where no column computes it."""
        for (r, c), (f, _) in sorted(s.cells.items()):
            if f and squeeze(f).upper().startswith("HSTACK("):
                tree = xparse(f, self.where(s.name, c, r))
                if not isinstance(tree, XCall) or not all(isinstance(a, XRef) for a in tree.args):
                    raise Fault(f"{self.where(s.name, c, r)}: an HSTACK of other than columns")
                cols: list[tuple[str, str]] = []
                for a in cast(tuple[XRef, ...], tree.args):
                    tab = a.sheet or s.name
                    if tab not in self.model or a.r1 != self.model[tab].first or a.c1 != a.c2 or (tab, a.c1) not in self.ids:
                        raise Fault(f"{self.where(s.name, c, r)}: HSTACK names {tab}!{a.text}, not a model column's draws")
                    cols.append((tab, self.ids[(tab, a.c1)]))
                out: list[tuple[str, str]] = []
                pairs = [cols[k:k + 2] for k in range(0, len(cols), 2)]
                for pair in pairs:
                    net = None
                    if len(pair) == 2 and pair[0][0] == pair[1][0]:
                        (t, a), (_, b) = pair
                        for col in self.model[t].cols:
                            if col.formula in (Bin("-", Ref(t, b), Ref(t, a)), Bin("-", Ref(t, a), Ref(t, b))):
                                net = (t, col.id)
                                break
                    out += [net] if net else pair
                    self.note("Sensitivity outputs", f"{s.name}: {' and '.join(f'{t}!{i}' for t, i in pair)}: " +
                              (f"the net {net[0]}!{net[1]}" if net else "no column computes their net; both are outputs"))
                self.note("Dropped tabs", f"{s.name}: replaced by the tab {SENSITIVITY_TAB}, each input's tornado ends for each output")
                return out
        raise Fault(f"{s.name}: no HSTACK naming the outputs")


# Writing the data file ---------------------------------------------------------------------------------------------


def toml_value(v: str | float | int) -> str:
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if not math.isfinite(v):
        raise Fault(f"a number {v!r} the data file cannot hold")
    return str(int(v)) if float(v).is_integer() and abs(v) < 1e15 else repr(float(v))


def write_data(plan: Plan) -> str:
    out: list[str] = ["# Imported by tools/sheet_import.py; see import_report.md beside it.", ""]
    for role, name in plan.order:
        if role == "guide":
            out += ["[[tab]]", f"name = {toml_value(ss.GUIDE)}", 'kind = "guide"']
            for key, v in plan.guide.items():
                if isinstance(v, list):
                    rows = cast(list[list[str]], v)
                    out += [f"{key} = ["] + ["  [" + ", ".join(toml_value(x) for x in row) + "]," for row in rows] + ["]"]
                else:
                    out.append(f"{key} = {toml_value(cast(str | float, v))}")
            out.append("")
        elif role == "model":
            mt = plan.model[name]
            out += ["[[tab]]", f"name = {toml_value(name)}", f"about = {toml_value(mt.about)}", ""]
            for col in mt.cols:
                if col.kind == "pick":
                    out += ["[[tab.column]]", f"id = {toml_value(col.uniform)}", 'name = "Random number of the pick"', 'kind = "uniform"',
                            f"citation = {toml_value('The random number the pick to its right reads: uniform from 0 to 1.')}",
                            "lo = 0", "hi = 1"] + ([f"group = {toml_value(col.group)}"] if col.group else []) + [""]
                out += ["[[tab.column]]", f"id = {toml_value(col.id)}", f"name = {toml_value(col.name)}",
                        f"kind = {toml_value('calc' if col.kind == 'pick' else col.kind)}"]
                if col.kind in ss.REQUIRED:
                    out.append(f"citation = {toml_value(col.citation)}")
                    out += [f"{k} = {toml_value(v)}" for k, v in col.params.items()]
                else:
                    out.append(f"formula = {toml_value(ss.source(cast(Node, col.formula), name))}")
                if col.note:
                    out.append(f"note = {toml_value(col.note)}")
                if col.group:
                    out.append(f"group = {toml_value(col.group)}")
                out.append("")
            for mid, group, credence in mt.methods:
                out += ["[[tab.method]]", f"id = {toml_value(mid)}", f"group = {toml_value(group)}", f"credence = {toml_value(credence)}", ""]
        elif role == "text":
            rows, widths = plan.texts[name]
            out += ["[[tab]]", f"name = {toml_value(name)}", 'kind = "text"'] + ([f"widths = {widths}"] if widths else [])
            out.append("rows = [")
            out += ["  [" + ", ".join(toml_value(v) for v in (row or [""])) + "]," for row in rows]
            out += ["]", ""]
        elif role == "table":
            cells = plan.tables[name]
            out += ["[[tab]]", f"name = {toml_value(name)}", 'kind = "table"', "rows = ["]
            last_row = max((r for r, _ in cells), default=1)
            for r in range(1, last_row + 1):
                width = max((c for rr, c in cells if rr == r), default=0)
                row: list[str] = []
                for c in range(1, width + 1):
                    v = cells.get((r, c), "")
                    row.append(toml_value(v) if isinstance(v, (str, int, float)) else toml_value("=" + ss.source(v, name)))
                out.append("  [" + ", ".join(row) + "],")
            out += ["]", ""]
        elif role == "sensitivity":
            if not plan.outputs:
                continue
            if SENSITIVITY_TAB in (n for _, n in plan.order):
                raise Fault(f"a tab is already named {SENSITIVITY_TAB}")
            out += ["[[tab]]", f"name = {toml_value(SENSITIVITY_TAB)}", 'kind = "sensitivity"',
                    "outputs = [" + ", ".join(toml_value(f"{ss.sheet_name(t)}!{i}") for t, i in plan.outputs) + "]", ""]
    return "\n".join(out)


def run_import(export: Path, out: Path) -> None:
    importer = Importer(read(export))
    plan = importer.plan()
    out.mkdir(parents=True, exist_ok=True)
    data = out / "sheet.toml"
    data.write_text(write_data(plan))
    tabs = ss.load(data)  # the written file must load: every formula parses, every name fits
    letters = {(t.name, c.id): c.letter for t in tabs for c in t.columns}
    lines = ["old\tname\tnew tab\tnew id\tnew letter"]
    for name, mt in plan.model.items():
        for col in mt.cols:
            old = " ".join(text_of(mt.sheet.value(1, col.col)).split())
            lines.append(f"{name}!{ss.letter(col.col)}\t{old}\t{name}\t{col.id}\t{letters[(name, col.id)]}")
    (out / "crosswalk.tsv").write_text("\n".join(lines) + "\n")
    report = [f"# Import report: {export.name}", "",
              "What the importer inlined, translated, resolved or dropped, for the audit. Each line names the old cell.", ""]
    for section, items in plan.report.items():
        report += [f"## {section}", "", *(f"- {x}" for x in items), ""]
    (out / "import_report.md").write_text("\n".join(report))
    print(f"wrote {data}, {out / 'crosswalk.tsv'} and {out / 'import_report.md'}")


# replay ------------------------------------------------------------------------------------------------------------


def cached_draws(mt: ModelTab, c: int) -> Floats:
    vals = [mt.sheet.value(r, c) for r in range(mt.first, mt.first + DRAWS)]
    return np.array([v if isinstance(v, float) else np.nan for v in vals], dtype=np.float64)


def run_replay(data: Path, export: Path) -> int:
    importer = Importer(read(export))
    plan = importer.plan()
    tabs = ss.load(data)
    _, pct = ss.bounds(tabs)
    found_cols = {(t.name, c.id): c for t in tabs for c in t.columns}
    values: dict[tuple[str, str], Floats] = {}
    for name, mt in plan.model.items():
        for col in mt.cols:
            if (name, col.id) not in found_cols:
                raise Fault(f"{data}: no column {name}!{col.id}, which {name}!{ss.letter(col.col)} became")
            values[(name, col.id)] = cached_draws(mt, col.col)
            if col.uniform:
                values[(name, col.uniform)] = sheet_uniforms(mt.sheet.position, col.col, DRAWS, mt.first)
    lines: list[str] = []
    with np.errstate(all="ignore"):
        for name, mt in plan.model.items():
            for col in mt.cols:
                new = found_cols[(name, col.id)]
                expected = values[(name, col.id)]
                if new.formula is None:
                    params = {k: float(v) for k, v in new.params.items()}
                    got = ss.draw(new.kind, params, sheet_uniforms(mt.sheet.position, col.col, DRAWS, mt.first))
                else:
                    got = ss.evaluate(new.formula, values)
                lines += disagreements(name, col.col, col.id, mt.first, expected, got)
        for t in tabs:
            if t.kind != "table":
                continue
            if t.name not in importer.sheets:
                raise Fault(f"{data}: table {t.name} is no tab of the export")
            old = importer.sheets[t.name]

            def cell(r: int, c: int, old: Sheet = old) -> ss.Scalar:
                return old.value(r, c)

            for (r, c), v in t.cells.items():
                if isinstance(v, (str, int, float)):
                    continue
                got_v, scale = ss.scalar(v, lambda tab, cid: values[(tab, cid)], cell, pct, old_interval_text)
                want = old.value(r, c)
                if not agree(want, got_v, scale):
                    lines.append(f"{ss.sheet_name(t.name)}!{ss.letter(c)}{r}: expected {want!r}, found {got_v!r}")
    for line in lines:
        print(line)
    print(f"{'FAIL' if lines else 'pass'}: {len(lines)} disagreement line(s)")
    return 1 if lines else 0


def old_interval_text(mean: float, low: float, high: float) -> str:
    """The interval text an older-layout sheet caches: the three rounded to the decimals that give the mean two
    significant figures, joined as Sheets writes numbers. Every export this module reads computes it so, since `interval`
    translates no other text formula; a generated sheet writes `sheet_script.interval_text`."""
    if not (math.isfinite(mean) and math.isfinite(low) and math.isfinite(high)) or mean == 0:
        return "#NUM!"
    places = 1 - math.floor(math.log10(abs(mean)))

    def text(x: float) -> str:
        q = ss.rounded(x, places)
        return "0" if q == 0 else format(q.normalize(), "f")

    return f"{text(mean)} [{text(low)}, {text(high)}]"


def agree(want: ss.Scalar, got: ss.Scalar, scale: float) -> bool:
    if isinstance(want, float) and isinstance(got, float):
        return abs(want - got) <= ss.TOL * max(abs(want), abs(got), scale) or (math.isnan(want) and math.isnan(got))
    return want == got


def disagreements(tab: str, c: int, cid: str, first: int, expected: Floats, got: Floats) -> list[str]:
    finite = np.isfinite(expected)
    m = float(np.max(np.abs(expected[finite]))) if finite.any() else 0.0
    ok = (~finite & ~np.isfinite(got)) | (np.abs(expected - got) <= ss.TOL * np.maximum(np.maximum(np.abs(expected), np.abs(got)), m))
    bad = np.flatnonzero(~ok)
    if not bad.size:
        return []
    name, letter = ss.sheet_name(tab), ss.letter(c)
    return [f"{name}!{letter}{first + int(k)}: expected {float(expected[k])!r}, found {float(got[k])!r}" for k in bad[:3]] + \
        [f"{name} column {letter} ({cid}): {bad.size} of {DRAWS} draws disagree"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("import", help="write sheet.toml, crosswalk.tsv and import_report.md from an older-layout export")
    i.add_argument("export", type=Path)
    i.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("replay", help="check a data file against the export's cached values")
    r.add_argument("data", type=Path)
    r.add_argument("export", type=Path)
    a = p.parse_args(argv)
    try:
        if a.cmd == "import":
            run_import(a.export, a.out)
            return 0
        return run_replay(a.data, a.export)
    except Fault as e:
        print(f"refused: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
