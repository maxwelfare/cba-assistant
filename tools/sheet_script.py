"""A teaching sheet written as a data file: the whole sheet as one .xlsx, the same columns in Python, and the comparison.

    python -m tools.sheet_script generate DATA.toml --out DIR
    python -m tools.sheet_script compare DATA.toml EXPORT.xlsx [--tab NAME] [--every-draw]

`generate` writes DIR/sheet.xlsx, every tab in the file's order, which Google converts into a Google Sheet in one
upload, and prints one line, `sha256:<hex digest>:<absolute path>`, the reference the upload call takes. First it
reads the workbook back from its bytes and refuses it (exit 2, writing nothing, naming each tab and cell) where a text
runs past five lines in a column under 150 px (in a table, past two) or past its row's height, a cell is merged, a
font is other than Arial 10 but a bold title in its tab's title place, a font colour is not one of the four below or a
formula is input blue, a block's column of a table holds two number formats, a Sensitivity key lacks its IFERROR
guard, or an input's citation neither ends in an address nor begins with a mark of CITATION_MARKS ("Judge:",
"Unpublished:", "Judgment", "Convention", "No source:"; a uniform random number from 0 to 1 that a pick reads needs
none) (`layout_faults`). It also
writes DIR/columns.tsv, one line a column: tab, letter, id, name, and the low end of the interval the guide sets,
the mean and the high end, of its 1,000 draws, in the sheet's order (linear interpolation, as Google's PERCENTILE). A
column tab's header, one row one purpose:

    row 1        A: the tab's `about`          each column: its name
    row 2        A: Notes                      its note
    row 3        A: Source or formula          an input's citation; a calculation's draw formula as text
                                               without row numbers (REGEXREPLACE of FORMULATEXT)
    rows 4-11    A: Set: distribution ... beta an input's kind (with the dropdown of the seven kinds) and parameters
                                               (min, mode, max in rows 7 to 9), in yellow; a calculation's rows empty,
                                               in grey
    rows 12-14   A: Draws: low, mean, high     the low end of the interval of the column's draws, their mean and the
                                               high end, in blue
    row 15       A: Graph                      a histogram of the draws
    rows 16-1015 A: 1 to 1000                  the draws: one shared formula down the column, over its own row

Row 1 and column A are frozen. The look is the owner's Monte Carlo Template's, written as the tables under
`generate` (LOOK, HEIGHT, the widths): column A 120 px and the others 70 px wide; each header row its alignment and
height; every cell Arial 10, A1 bold at 11; light gray borders on every cell from row 3 down (row 4 down in column A); and twelve empty
spare columns after the last one, with a calculation's fills, for people to write in. A calculation column may carry
`result = true`: its name is bold. Font colour marks a cell's kind (the owner, Decision 23, 2026-11-20): on a column
tab a value a person may change (an input's kind and parameters, a credence) is input blue; on every tab a formula
that is another tab's cell carried over unchanged (=Globals!C13, or a lookup into another tab) green, and any other
formula black, whatever tab it reads (`formula_colour`; the percentile rows 12 and 14 among them);
every hyperlink on every tab link blue, underlined; every other cell black but the guide's text that is not a formula,
in his template's #222222 (`INK`), the guide's setting, in input blue,
and the guide's colour key, which shows each kind in its colour beside an example cell of this sheet
(`colour_key`). An input's citation that ends in an
address (`... sd=39". https://arxiv.org/pdf/1304.4476`) is written as a HYPERLINK formula: the citation's words show,
and a click opens the address; a guide's or text tab's cell is linked the same way. In their rows, a cell that starts with
`# ` is a heading (Arial 16 bold), one that starts with `## ` a subhead (Arial 10 bold, as his template's Readme sets
"Inputs" at A10); one that starts with a backslash is plain text, the backslash dropped ("\\# of households"); one whose whole text is wrapped in `**` is plain, since a text tab's only bold is its titles and
subheads; the marks are not written. The guide's text that is not a formula is #222222, his template's Readme ink.
Every text cell is top-aligned and wraps, except a heading or subhead, which runs on over the empty cells to its right, and a
link, which stays on one line (an xlsx cannot ask Google to clip it).
Every draw row holds its column's formula over the cells of its own row (`=B16*C16`,
then `=B17*C17`), with no array formula: a reader sees which cells feed a cell. `compare` recomputes every column and
checks the final estimate in an .xlsx export of the uploaded sheet: rows 12 to 14 (low, mean, high) of each column of
the last tab that has columns, or of the tab `--tab` names, against Python's percentiles and mean of the same column.
It prints one line a column and a final pass or fail line. A cell agrees within 1e-7 of the column's largest
value, as every number does in `--every-draw`: the sheet draws no random numbers of its own, since every input reads
`U_TEXT`, which Python reproduces exactly (`sampling.sheet_uniforms`), so Python and the sheet share their draws and
no Monte Carlo noise lies between them; a looser tolerance would pass a fault that moves a statistic a little.
`--every-draw` instead compares everything, to 1e-7: each tab's place and `about`, each column's name, note, row 3,
kind and parameters, each method's credence, rows 12 to 14, all 1,000 draws, each given cell of the guide and a text tab, and which
cells of row 4 carry the dropdown, printing each disagreement. Row 15 has no value in an export and is not compared.
Exit 0 when all agree, 1 on a disagreement, 2 on a fault in the data file.

The data file: `[[tab]]` entries in the sheet's order, each with `name`. The first is the guide, `name = "Guide"`
and `kind = "guide"`; `generate` refuses a file without one (exit 2). The generator writes the guide itself, in
columns of GUIDE_WIDTHS px: the credit line in B1, the template's instructions (How to Read the Sheet, Quick Start,
Inputs, Outputs and Intermediate Calculations, Combining Estimates for each tab with methods, Technical Details) from
the text held here (GUIDE_*), then "This sheet" and "The tabs, left to right" from the data file, and the template's
Useful References in columns C and D. The guide carries `interval`, a number between 0 and 1 such as 0.9, the share
of each column's draws its rows 12 and 14 enclose (at 0.9 the 5th and 95th percentiles), which the guide's yellow
cell beside How to Read holds, the one setting every tab reads; `worked_example`, the column tab whose draw 1 the
reader follows across; `what`, a line saying what the sheet is; `start_here`, two or three questions, each naming
where its answer is; `tabs`, a list of [tab name, description] pairs, one for every other tab and no other name;
and optionally `general_form`, `notes` (a list of [bold title, text] rows, the title may be empty; a note titled
with a heading of the template's instructions, such as "How to Read the Sheet", stands untitled at that section's
end), `references` (a
list of [label, link] pairs added to the template's), `details` (the row linking the reader's document; `generate`
warns where it is absent) and `fill_down_script = true` (the sheet carries `tools/sheet_fill_down.gs`). A text that
begins with `[AUTHOR:` is a placeholder: `generate` writes it and prints one warning line for each. How the sheet
works belongs in the guide, never in a column. `kind = "text"` takes a place, holds no columns and may carry `rows`,
a list of rows, each a list of strings from column A on, and `widths`, whole numbers of pixels above 0, one a column
from A (without it, A 575 px and B 150 px; later columns Google's default). A column tab has `about`,
one line (A1) of words of at most 45 characters with none over 11, and `[[tab.column]]` entries, lettered B, C, ... in order, each with `id`,
`name` (row 1), words of at most 40 characters with none over 11 (the limits of its cell), and `kind`, and optionally
`note` (row 2) and `format` for its rows 5 to 9, 12 to 14 and its draws. A `format` is one of four kinds of number,
`"number"` (without `format`), `"$"`, `"%"` or `"year"`, or else a literal Google number format such as `$#,##0.0`
(one holding 0, # or @), applied as written; any other `format` is refused. For a kind, the draws show two significant figures of the column's typical size,
the mean of its draws' absolute values, with thousands separators and the decimals that give that (at most
MAX_DECIMALS; a size that needs more shows in scientific form, 4.0E-05); `"$"` puts the
sign first (-$4.5); `"%"` works its decimals on the value times 100, and on 1 less the value between 0.5 and 1, so
that 0.996 shows 99.6%, never 100%; `"year"` is always a whole number with no separator. A "number" or "$" column
whose typical size is 1,000 or more shows in a scaled unit, by the format's trailing commas, chosen so its typical
size shows under 100, up to quadrillions (a larger size shows whole in quadrillions), and the cells carry no letter: the column's name names the unit shown, in words, rewriting the
unit its name, note or group gives in brackets ("(₩ Bil)", "(USD mil)", "(Mil)"; units where none) and the same unit in its
note, everything else kept, or gaining it in brackets where the name gives none (2,677,000 under "Korea Real GDP
(₩ Bil)" shows 2.7 under "Korea Real GDP (₩ quadrillion)"; 2,970,000,000 under "Orders" shows 3.0 under "Orders
(billion)") (`column_scale`, `column_label`); a unit its name gives in brackets is named in words even where nothing
is scaled ("(₩ 000)" reads "(₩ thousand)"), and Sensitivity's labels of the column follow its name. Each Set cell (rows 5 to 11) and each of rows 12 to 14
shows two significant figures of its own value, in its column's one unit, the unit its name gives (`set_format`). A column may carry `group = "<words>"`, at most 40 characters with no
word over 11; columns that follow one another with the same group are one block. On a tab where every column carries
one (a tab carries groups on all its columns or on none, and a group's columns are adjacent), each block has one label
column before it, holding only the group's words in row 1, bold on bright yellow, and its columns' name cells are
tinted, block by block, with TINTS in turn. A label column is a real sheet column, so the letters after it move; an
input's draws are seeded by its place among the data columns (COLUMN() less the label columns before it), so groups
change no number, and `compare` reads only the data columns. An input's kind is one of the template's seven, with `citation` (row 3)
and its parameters in rows 5 to 11; a calculation (`kind = "calc"`) has `formula`, an expression over its own tab's
ids, in any order, any other column tab's columns as `Tab!id` or `'Tab name'!id` (written `Tab!X16`, the same draw
row), `draw` (the draw's number, column A), numbers, + - * / ^, comparisons, brackets and the functions of FUNCTIONS
(PV is Sheets' PV(rate, nper, pmt), paid at each period's end); `compute` evaluates the columns of the whole file in
the order their formulas need, and refuses a cycle, naming its columns. No calculation draws a random
number: one that picks among columns (a mixture) reads a uniform input column of its own, min 0 and max 1, so the
generator's formula stands in input columns only. A tab with groups may carry methods, `[[tab.method]]` entries
with `id` (in the namespace of the tab's column ids), `group` (a group of the tab, one method a group) and
`credence`, a number above 0: the group's label column shows "Credence" in row 4 and the number in row 5, both in
yellow, and any formula of the tab cites it as CREDENCE(id) (written X$5). A column carries no credence. A column
of `kind = "read"` is refused: a formula cites the other tab's column itself. A tab of `kind = "table"` has `rows`,
cells from A1, each a text, a number or a formula (a text beginning with "="), written to the sheet as Sheets
formulas and computed here like a column; `compare --every-draw` checks each. A table's formula cites its own cells
(`$B5`, a block `K19:K23` inside SUM), a column's statistic `Tab!id.low`, `.mean` or `.high` (rows 12 to 14), and a
column's draws, or a run of adjacent columns' pooled (`Tab!first:last`), as the first argument of AVERAGE,
PERCENTILE(draws, share), INDEX(Tab!id, n) (draw n) or INTERVAL(Tab!id), the owner's text "mean [low, high]", each
of the three at two significant figures of its own value with thousands separators ("-23,000 [-130,000, 99,000]";
INTERVAL(mean, low, high) takes three values), with SUM, ABS and arithmetic. A table's number typed as a whole number, a label such as a year, shows as typed
("2027"); any other number takes the format kind of the columns its formula cites (directly, or through its own cells),
"number" where it cites none, columns of more than one kind, or divides by a quantity that cites a column (a ratio),
with the rule of a column's draws applied to the cell's own value, so the mean of a 0/1 column of format "%" shows as a
percentage; numbers one under another in a column, a block's column, share one format worked out on all their values,
a "%" with the decimals that show each share at two significant figures of its distance from 0% or 100%; numbers are right-aligned
with their heads, texts left-aligned and wrapped, and A1, the table's title, bold at 16 (an A1 that holds a title and a
paragraph, "Results: the ...", keeps the title, and the paragraph goes to A2, `title_note`). A run of money whose
columns name their currency and unit ("(₩ Mil)", "in ₩ million"; the "$" kind is dollars) shows two
significant figures in the unit that puts its largest value under 100, by the format's trailing commas, and its
head names the unit ("Mean, ₩ trillion"); so do Sensitivity's means and change columns. A table may carry `formats`, a
mapping from a cell or block ("D1:F1") to a kind or a literal format, which overrides that rule, and `widths` as a text
tab does. On a text or table tab without `widths`, a column (a table's 100 px, Google's) is widened to fit a text that
would wrap past five lines, to at most 600 px; on every tab without columns each row is as tall as its tallest text. A
text of at most 80 characters on a table or sensitivity tab, or in the guide's column A, that is another tab's name,
or begins with it and "," or ":" where the cells it heads read that tab, is written as a formula that shows the tab's
present name (`tab_named`), so it follows a renaming. A
tab of `kind = "sensitivity"` has `outputs`, a list of columns written `Tab!id`. Its inputs are the columns of every
input kind but constant. For each input and output: r = CORREL(output, input); rank r = CORREL of their ranks; the
key, MAX(ABS(r), ABS(rank r)), the owner's old Correlation tab's statistic; and the change, SLOPE(output, input) x
(the input's 95th percentile less its 5th), signed, in the output's format at the changes' own size. B1 holds the
tab's title and row 2 the noise line, 4/SQRT(COUNT(draws)); how the numbers are found is in the guide, under the
tab's own row of "The tabs, left to right"; then one block per output, side by side, its name, mean and interval, and ranks 1 to 15 by key
(LARGE, INDEX/MATCH, the first match on a tie), each a rank and six cells: input, tab, r, rank r, change, key, a key
below the line showing all seven blank; below the lists every input with each output's r, rank r, change and
key. At the right, each output's ranks, RANK.AVG ascending, one a draw row, then each input's ranks as static values,
the ranks of its random numbers, which equal its draws' ranks whatever its kind and parameters, since every kind's
draw rises with its random number. Each rank r cell checks COLUMN() and SHEET() of the input's first draw against
their values at generation, and shows "moved: regenerate" where a moved tab or column has changed the input's random
numbers, and that input's key is then blank (IFERROR), so the others still rank; a constant input shows blank. Every other number is a live formula, and `sensitivity_values` is the twin `compare` checks. In a tab's about, a
column's name, note and citation, a text tab's rows and the guide's texts, `{col:id}` (a column of the same tab) or
`{col:Tab name.id}` is replaced by that column's letter, a method's id by its label column's letter, and
`{row:Table:Tab!id}` by the first row of the table whose cells cite the column, so no data file types a row number. A
header note, written as an Excel cell comment that Google imports as the cell's note, goes on row 1 of its column: a
column's `header_note`, or a tab's `header_notes` (any tab), a mapping from a column letter ("A", a label column's)
or, on a column tab, a column's id to the note; a key the tab lacks, or two notes on one cell, is refused (exit 2),
and a file without notes writes no comments part. No text written to the sheet may begin with `=`, which
Google reads as a formula on upload. A formula is read with the usual precedence (^ binds right to left and tighter
than a leading minus) and written with the brackets Google Sheets needs to read it the same way.

A number agrees when |expected - found| <= 1e-7 * max(|expected|, |found|, m), m the largest |value| among the
column's expected draws: the export stores some values to nine significant figures, and a draw near zero would
otherwise fail on rounding noise.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import math
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from decimal import ROUND_HALF_UP, Decimal
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import cast
from xml.sax.saxutils import escape

import numpy as np
from numpy.typing import NDArray
from scipy import stats

from cost_benefit_engine.sampling import sheet_uniforms

Floats = NDArray[np.float64]
DRAWS = 1000
FIRST, LAST = 16, 1015
TOL = 1e-7

KIND_ROW = 4
PARAM_ROW = {"mean": 5, "sd": 6, "lo": 7, "peak": 8, "hi": 9, "alpha": 10, "beta": 11}  # in row order
LOW, MEAN, HIGH = 12, 13, 14  # the draws' rows: the low end of the interval, the mean, the high end
REQUIRED = {
    "beta": {"lo", "hi", "alpha", "beta"},
    "constant": {"mean"},
    "lognormal": {"mean", "sd"},
    "normal": {"mean", "sd"},
    "power law": {"lo", "alpha"},
    "triangular": {"lo", "hi", "peak"},
    "uniform": {"lo", "hi"},
}
FUNCTIONS = {"IF": 3, "MIN": 0, "MAX": 0, "EXP": 1, "LN": 1, "SQRT": 1, "ABS": 1, "COS": 1, "SIN": 1, "RADIANS": 1, "PV": 3}  # 0: one or more

U_TEXT = "MOD(SIN(ROW()*12.9898+COLUMN()*78.233+SHEET()*37.719)*43758.5453,1)"
GENERATOR = (  # the Monte Carlo Template's input formula as its column C holds it, one draw a row
    "=LET(u," + U_TEXT + f",dist,C${KIND_ROW}," + "".join(f" {k},C${r}," for k, r in PARAM_ROW.items()) +
    'IF(dist="beta",lo+(hi-lo)*BETA.INV(u,alpha,beta),IF(dist="constant",mean+0*u,IF(dist="lognormal",EXP(NORMINV(u,LN(mean^2/SQRT(mean^2+sd^2)),SQRT(LN(1+sd^2/mean^2)))),'
    'IF(dist="normal",NORMINV(u,mean,sd),IF(dist="power law",lo*(1-u)^(-1/(alpha-1)),IF(dist="triangular",IF(u<=(peak-lo)/(hi-lo),lo+SQRT(u*(hi-lo)*(peak-lo)),hi-SQRT((1-u)*(hi-lo)*(hi-peak))),'
    'IF(dist="uniform",lo+u*(hi-lo),""))))))))'
)


class Fault(Exception):
    """A fault in the data file: exit 2."""


# Formulas --------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Num:
    text: str


@dataclass(frozen=True)
class Ref:
    tab: str  # a column tab
    id: str  # a column id of it, or DRAW


@dataclass(frozen=True)
class Neg:
    x: Node


@dataclass(frozen=True)
class Bin:
    op: str
    a: Node
    b: Node


@dataclass(frozen=True)
class Call:
    fn: str
    args: tuple[Node, ...]


@dataclass(frozen=True)
class Cred:
    id: str
    value: float


@dataclass(frozen=True)
class Cell:  # a table's own cell, as written ($B$15)
    text: str
    row: int
    col: int


@dataclass(frozen=True)
class Span:  # a block of a table's own cells, for SUM
    first: Cell
    last: Cell


@dataclass(frozen=True)
class Stat:  # a column's statistic: rows LOW, MEAN or HIGH
    tab: str
    id: str
    which: str


@dataclass(frozen=True)
class Pool:  # the draws of a run of adjacent columns, pooled
    tab: str
    ids: tuple[str, ...]


Node = Num | Ref | Neg | Bin | Call | Cred | Cell | Span | Stat | Pool

DRAW = "draw"  # the draw's number, column A
STAT_ROW = {"low": 12, "mean": 13, "high": 14}  # LOW, MEAN, HIGH
TABLE_FUNCTIONS = {"SUM": 0, "ABS": 1, "AVERAGE": 1, "PERCENTILE": 2, "INTERVAL": 0, "INDEX": 2}  # 0: one or more
POOLED = ("AVERAGE", "PERCENTILE", "INTERVAL", "INDEX")  # the functions whose first argument may be a column's draws
TOKEN = re.compile(
    r"\s*(?:(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"
    r"|(?:'((?:[^']|'')+)'|([A-Za-z_][A-Za-z0-9_]*))!([a-z][a-z0-9_]*)(?::([a-z][a-z0-9_]*))?(?:\.(mean|low|high))?"
    r"|(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)(?![A-Za-z0-9_(])"
    r"|([A-Za-z_][A-Za-z0-9_]*)"
    r"|(<=|>=|<>|[-+*/^(),<>=]))"
)
COMPARE = ("<=", ">=", "<>", "<", ">", "=")


def cell_ref(text: str) -> Cell:
    m = cast(re.Match[str], re.fullmatch(r"\$?([A-Z]+)\$?(\d+)", text))
    return Cell(text, int(m.group(2)), colnum(m.group(1)))


def parse(text: str, here: str, ids: dict[str, list[str]], credences: dict[str, int | float], where: str,
          table: bool = False) -> Node:
    """The formula's tree. here is its tab, ids each column tab's column ids, credences the tab's methods'; a table's
    formula (table) cites its own cells and columns' statistics and draws, a column's formula the columns of any tab."""
    tokens: list[tuple[str, str, tuple[str | None, ...]]] = []
    pos = 0
    while text[pos:].strip():
        m = TOKEN.match(text, pos)
        if not m:
            raise Fault(f"{where}: formula has an unreadable character at {text[pos:].strip()[:10]!r}")
        kind = "num" if m.group(1) else "sheet" if m.group(4) else "cell" if m.group(7) else "name" if m.group(8) else "op"
        tokens.append((kind, m.group(0).strip(), m.groups()))
        pos = m.end()
    tokens.append(("end", "", ()))
    i = 0

    def take(want: str | None = None) -> tuple[str, str, tuple[str | None, ...]]:
        nonlocal i
        tok = tokens[i]
        if want is not None and tok[1] != want:
            raise Fault(f"{where}: formula expects {want!r} where it has {tok[1] or 'its end'!r}")
        i += 1
        return tok

    def is_op(value: str | tuple[str, ...]) -> bool:
        return tokens[i][0] == "op" and (tokens[i][1] == value if isinstance(value, str) else tokens[i][1] in value)

    def expr() -> Node:
        node = additive()
        while is_op(COMPARE):
            node = Bin(take()[1], node, additive())
        return node

    def additive() -> Node:
        node = term()
        while is_op(("+", "-")):
            node = Bin(take()[1], node, term())
        return node

    def term() -> Node:
        node = unary()
        while is_op(("*", "/")):
            node = Bin(take()[1], node, unary())
        return node

    def unary() -> Node:
        if is_op("-"):
            take()
            return Neg(unary())
        return power()

    def power() -> Node:
        node = atom()
        if is_op("^"):
            take()
            return Bin("^", node, unary())
        return node

    def sheet(groups: tuple[str | None, ...]) -> Node:
        quoted, bare, cid, last, stat = groups[1], groups[2], cast(str, groups[3]), groups[4], groups[5]
        tab = quoted.replace("''", "'") if quoted is not None else cast(str, bare)
        if tab not in ids:
            raise Fault(f"{where}: formula cites tab {tab!r}, which is no column tab of the file")
        for x in (cid, last):
            if x is not None and x not in ids[tab]:
                raise Fault(f"{where}: formula cites {tab}!{x}, which tab {tab!r} lacks")
        if not table:
            if last is not None or stat is not None:
                raise Fault(f"{where}: a column's formula cites another column as Tab!id, one draw a row")
            return Ref(tab, cid)
        if stat is not None:
            if last is not None:
                raise Fault(f"{where}: a statistic belongs to one column, not to {tab}!{cid}:{last}")
            return Stat(tab, cid, stat)
        a, b = ids[tab].index(cid), ids[tab].index(last if last is not None else cid)
        if b < a:
            raise Fault(f"{where}: {tab}!{cid}:{last} runs backwards")
        return Pool(tab, tuple(ids[tab][a:b + 1]))

    def atom() -> Node:
        kind, value, groups = take()
        if kind == "num":
            return Num(value)
        if kind == "op" and value == "(":
            node = expr()
            take(")")
            return node
        if kind == "sheet":
            return sheet(groups)
        if kind == "cell":
            if not table:
                raise Fault(f"{where}: formula cites the cell {value}; a column's formula cites column ids")
            first, _, last = value.partition(":")
            return Span(cell_ref(first), cell_ref(last)) if last else cell_ref(first)
        if kind == "name" and value == "CREDENCE" and is_op("(") and not table:
            take("(")
            ref = take()[1]
            take(")")
            if ref not in credences:
                raise Fault(f"{where}: CREDENCE({ref}) cites {ref}, which is no method of the tab; a credence belongs to a [[tab.method]]")
            return Cred(ref, float(credences[ref]))
        if kind == "name" and is_op("("):
            allowed = TABLE_FUNCTIONS if table else FUNCTIONS
            if value not in allowed:
                raise Fault(f"{where}: function {value} is outside the list {', '.join(allowed)}")
            take("(")
            args = [expr()]
            while is_op(","):
                take()
                args.append(expr())
            take(")")
            arity = allowed[value]
            if arity and len(args) != arity or value == "INTERVAL" and len(args) not in (1, 3):
                raise Fault(f"{where}: {value} takes {arity or 'one or three'} arguments, not {len(args)}")
            return Call(value, tuple(args))
        if kind == "name" and not table:
            if value == DRAW or value in ids[here]:
                return Ref(here, value)
            if value == "u":
                raise Fault(f"{where}: formula cites u; a calculation draws no random number: add a uniform input column, min 0 and max 1, and cite its id")
            raise Fault(f"{where}: formula cites {value}, which the tab lacks")
        if kind == "name":
            raise Fault(f"{where}: a table's formula cites {value}; it cites its own cells (B5), a column's statistic "
                        "(Tab!id.mean, .low, .high) or its draws (AVERAGE, PERCENTILE, INTERVAL of Tab!id)")
        raise Fault(f"{where}: formula has {value or 'its end'!r} where a value belongs")

    def placed(node: Node, fn: str = "", k: int = -1) -> None:
        """Refuse a column's draws or a block of cells outside the one argument that takes it (fn's k-th)."""
        if isinstance(node, Span) and fn != "SUM":
            raise Fault(f"{where}: a block of cells belongs inside SUM")
        if isinstance(node, Pool) and not (fn in POOLED and k == 0):
            raise Fault(f"{where}: {node.tab}!{node.ids[0]} is a column of draws; cite Tab!id.mean, .low or .high, or "
                        "pass it to AVERAGE, PERCENTILE, INTERVAL or INDEX")
        if isinstance(node, Pool) and fn in ("INTERVAL", "INDEX") and len(node.ids) > 1:
            raise Fault(f"{where}: {fn} takes one column, not a run")
        if isinstance(node, Neg):
            placed(node.x)
        elif isinstance(node, Bin):
            placed(node.a)
            placed(node.b)
        elif isinstance(node, Call):
            three = node.fn == "INTERVAL" and len(node.args) == 3
            if node.fn in POOLED and not three and not isinstance(node.args[0], Pool):
                raise Fault(f"{where}: {node.fn} takes a column's draws first, Tab!id or Tab!first:last")
            for k, a in enumerate(node.args):
                placed(a, "" if three else node.fn, k)

    node = expr()
    take("")
    placed(node)
    return node


def refs(node: Node) -> set[tuple[str, str]]:
    """The columns a formula cites, as (tab, id): a column's, or a table cell's through a statistic or draws."""
    match node:
        case Ref(tab, cid):
            return set() if cid == DRAW else {(tab, cid)}
        case Stat(tab, cid, _):
            return {(tab, cid)}
        case Pool(tab, run):
            return {(tab, cid) for cid in run}
        case Neg(x):
            return refs(x)
        case Bin(_, a, b):
            return refs(a) | refs(b)
        case Call(_, args):
            found: set[tuple[str, str]] = set()
            for a in args:
                found |= refs(a)
            return found
        case _:
            return set()


LEVEL = {"<=": 1, ">=": 1, "<>": 1, "<": 1, ">": 1, "=": 1, "+": 2, "-": 2, "*": 3, "/": 3, "^": 4}
Show = Callable[[Node], "str | None"]


def write(node: Node, show: Show) -> tuple[str, int]:
    """The formula's text and its binding level (5 a leading minus, 6 an atom), with the brackets both Sheets and
    `parse` need to read it the same way; show writes the atoms, and any node it takes over."""
    shown = show(node)
    if shown is not None:
        return shown, 6

    def wrap(n: Node, bracket: bool) -> str:
        text = write(n, show)[0]
        return f"({text})" if bracket else text

    match node:
        case Num(text):
            return text, 6
        case Neg(x):
            return "-" + wrap(x, write(x, show)[1] <= 5), 5
        case Bin(op, a, b):
            level = LEVEL[op]
            left = write(a, show)[1] < level or (op == "^" and (isinstance(a, Neg) or (isinstance(a, Bin) and a.op == "^")))
            right = write(b, show)[1] <= level or isinstance(b, Neg)
            return wrap(a, left) + op + wrap(b, right), level
        case Call(fn, args):
            return fn + "(" + ",".join(write(a, show)[0] for a in args) + ")", 6
        case _:
            raise Fault(f"no way to write {node}")


def source(node: Node, here: str) -> str:
    """The formula as a data file writes it, on tab here."""

    def show(n: Node) -> str | None:
        match n:
            case Ref(tab, cid):
                return cid if tab == here else f"{sheet_name(tab)}!{cid}"
            case Cred(cid, _):
                return f"CREDENCE({cid})"
            case Cell(text):
                return text
            case Span(a, b):
                return f"{a.text}:{b.text}"
            case Stat(tab, cid, which):
                return f"{sheet_name(tab)}!{cid}.{which}"
            case Pool(tab, run):
                return f"{sheet_name(tab)}!{run[0]}" + (f":{run[-1]}" if len(run) > 1 else "")
            case _:
                return None

    return write(node, show)[0]


def in_sheet(letters: dict[tuple[str, str], str], here: str) -> Show:
    """How the sheet writes the atoms of a formula on tab here: a column's own row, a statistic's row, a run's draws;
    INTERVAL as the owner's text formula, each of the three at two significant figures of its own value."""

    def sig2(x: str) -> str:  # the Sheets text of `sig2_text`: ROUND to two significant figures, TEXT with separators
        p = f"(1-FLOOR(LOG10(ABS({x})),1))"
        return f'IF({x}=0,"0",TEXT(ROUND({x},{p}),"#,##0"&IF({p}>0,"."&REPT("0",{p}),"")))'

    def show(n: Node) -> str | None:
        match n:
            case Ref(tab, cid):
                return f"A{FIRST}" if cid == DRAW else ("" if tab == here else sheet_name(tab) + "!") + f"{letters[(tab, cid)]}{FIRST}"
            case Cred(cid, _):
                return f"{letters[(here, cid)]}$5"
            case Cell(text):
                return text
            case Span(a, b):
                return f"{a.text}:{b.text}"
            case Stat(tab, cid, which):
                return f"{sheet_name(tab)}!{letters[(tab, cid)]}{STAT_ROW[which]}"
            case Pool(tab, run):
                return f"{sheet_name(tab)}!{letters[(tab, run[0])]}{FIRST}:{letters[(tab, run[-1])]}{LAST}"
            case Call("INTERVAL", args):
                three = [Stat(cast(Pool, args[0]).tab, cast(Pool, args[0]).ids[0], w) for w in ("mean", "low", "high")] if len(args) == 1 else list(args)
                m, lo, hi = (write(a, show)[0] for a in three)
                return f'LET(m,{m},lo,{lo},hi,{hi},{sig2("m")}&" ["&{sig2("lo")}&", "&{sig2("hi")}&"]")'
            case _:
                return None

    return show


def evaluate(node: Node, values: dict[tuple[str, str], Floats]) -> Floats:
    """A column's formula over the draws; values holds every column it cites, by (tab, id)."""

    def ev(n: Node) -> Floats:
        return evaluate(n, values)

    match node:
        case Num(text):
            return np.full(DRAWS, float(text))
        case Ref(tab, cid):
            return np.arange(1.0, DRAWS + 1) if cid == DRAW else values[(tab, cid)]
        case Cred(_, value):
            return np.full(DRAWS, value)
        case Neg(x):
            return -ev(x)
        case Bin(op, a, b):
            x, y = ev(a), ev(b)
            ops = {"+": np.add, "-": np.subtract, "*": np.multiply, "/": np.divide, "^": np.power, "<=": np.less_equal,
                   ">=": np.greater_equal, "<>": np.not_equal, "<": np.less, ">": np.greater, "=": np.equal}
            return np.asarray(ops[op](x, y), dtype=np.float64)
        case Call("IF", (c, a, b)):
            return np.where(ev(c) != 0, ev(a), ev(b))
        case Call(fn, args) if fn in ("MIN", "MAX"):
            stacked = np.vstack([ev(a) for a in args])
            return stacked.min(axis=0) if fn == "MIN" else stacked.max(axis=0)
        case Call("PV", (r, n, p)):  # Sheets' PV(rate, nper, pmt), with no future value, paid at the end of each period
            rate, nper, pmt = ev(r), ev(n), ev(p)
            growth = (1 + rate) ** nper
            return np.where(rate == 0, -pmt * nper, -pmt * (growth - 1) / np.where(rate == 0, 1.0, rate) / growth)
        case Call(fn, args):
            funcs = {"EXP": np.exp, "LN": np.log, "SQRT": np.sqrt, "ABS": np.abs, "COS": np.cos, "SIN": np.sin, "RADIANS": np.radians}
            return np.asarray(funcs[fn](ev(args[0])), dtype=np.float64)
        case _:
            raise Fault(f"a column's formula holds {node}, which belongs to a table")


Scalar = float | str | None  # a table cell's value: None a blank cell, a text beginning with "#" an error as Sheets shows it


def rounded(x: float, places: int) -> Decimal:
    """x rounded to places decimals (negative: to tens, hundreds), half away from zero, as ROUND does."""
    d = Decimal(repr(x))
    return d.quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP) if places >= 0 else d.scaleb(places).quantize(Decimal(1), ROUND_HALF_UP).scaleb(-places)


def sig2_text(x: float) -> str:
    """x at two significant figures of its own value, with thousands separators, as the sheet's TEXT writes it."""
    if x == 0:
        return "0"
    places = 1 - math.floor(math.log10(abs(x)))
    return f"{rounded(x, places):,.{max(0, places)}f}"


def interval_text(mean: float, low: float, high: float) -> str:
    """The owner's interval text, "mean [low, high]", each at two significant figures of its own value (`sig2_text`)."""
    if not (math.isfinite(mean) and math.isfinite(low) and math.isfinite(high)):
        return "#NUM!"
    return f"{sig2_text(mean)} [{sig2_text(low)}, {sig2_text(high)}]"


def scalar(node: Node, draws: Callable[[str, str], Floats], cell: Callable[[int, int], Scalar],
           pct: tuple[float, float], interval: Callable[[float, float, float], str] = interval_text) -> tuple[Scalar, float]:
    """A table cell's value as Sheets computes it, from the columns' draws and the table's cells, and the largest
    magnitude among its numbers, the scale its agreement is judged at; interval writes INTERVAL's text (an older
    sheet's rule, for `sheet_import replay`)."""
    scale = 0.0

    def number(v: Scalar) -> float | str:
        if v is None:
            return 0.0
        if isinstance(v, str):
            return v if v.startswith("#") else "#VALUE!"
        return v

    def seen(v: float) -> float:
        nonlocal scale
        if math.isfinite(v):
            scale = max(scale, abs(v))
        return v

    def pooled(n: Node) -> Floats:
        p = cast(Pool, n)
        return np.concatenate([draws(p.tab, x) for x in p.ids])

    def ev(n: Node) -> Scalar:
        match n:
            case Num(text):
                return seen(float(text))
            case Cell(_, r, c):
                v = cell(r, c)
                return seen(v) if isinstance(v, float) else v
            case Stat(tab, cid, which):
                d = draws(tab, cid)
                s = summary(d, pct)
                return seen(s[0] if which == "low" else s[1] if which == "mean" else s[2])
            case Neg(x):
                a = number(ev(x))
                return a if isinstance(a, str) else -a
            case Bin(op, a, b):
                x, y = number(ev(a)), number(ev(b))
                if isinstance(x, str) or isinstance(y, str):
                    return x if isinstance(x, str) else y
                if op == "/" and y == 0:
                    return "#DIV/0!"
                try:
                    if op in ("+", "-", "*", "/"):
                        v = x + y if op == "+" else x - y if op == "-" else x * y if op == "*" else x / y
                    elif op == "^":
                        v = math.pow(x, y)
                    else:
                        v = float({"<=": x <= y, ">=": x >= y, "<>": x != y, "<": x < y, ">": x > y, "=": x == y}[op])
                except (ValueError, OverflowError):
                    return "#NUM!"
                return seen(v)
            case Call("ABS", (x,)):
                a = number(ev(x))
                return a if isinstance(a, str) else abs(a)
            case Call("SUM", args):
                total = 0.0
                for a in args:
                    if isinstance(a, Span):
                        found = [cell(r, c) for r in range(a.first.row, a.last.row + 1) for c in range(a.first.col, a.last.col + 1)]
                        error = next((v for v in found if isinstance(v, str) and v.startswith("#")), None)
                        if error is not None:
                            return error
                        total += sum(seen(v) for v in found if isinstance(v, float))
                    else:
                        v = number(ev(a))
                        if isinstance(v, str):
                            return v
                        total += v
                return seen(total)
            case Call("AVERAGE", (p,)):
                return seen(float(np.mean(pooled(p))))
            case Call("PERCENTILE", (p, q)):
                share = number(ev(q))
                return share if isinstance(share, str) else seen(float(np.percentile(pooled(p), 100 * share)))
            case Call("INDEX", (p, k)):  # one draw of a column, the k-th
                pos = number(ev(k))
                d = pooled(p)
                return pos if isinstance(pos, str) else seen(float(d[int(pos) - 1])) if 1 <= int(pos) <= len(d) else "#REF!"
            case Call("INTERVAL", args):
                if len(args) == 1:
                    p = cast(Pool, args[0])
                    s = summary(draws(p.tab, p.ids[0]), pct)
                    three: list[float | str] = [s[1], s[0], s[2]]
                else:
                    three = [number(ev(a)) for a in args]
                error = next((v for v in three if isinstance(v, str)), None)
                return error if error is not None else interval(*(cast(float, v) for v in three))
            case _:
                raise Fault(f"a table's formula holds {n}, which belongs to a column's formula")

    value = ev(node)
    return value, scale


# The data file ---------------------------------------------------------------------------------------------------


@dataclass
class Column:
    id: str
    name: str
    kind: str
    letter: str
    citation: str
    params: dict[str, int | float]
    formula: Node | None
    note: str = ""
    format: str = "number"  # a kind of number (KINDS_OF_NUMBER) or a literal number format, for rows 5 to 9, 12 to 14 and the draws
    result: bool = False  # a calculation the tab hands onward: its name bold
    group: str | None = None  # the words of the block of adjacent columns it stands in
    header_note: str = ""  # the cell note of its name cell (row 1)


@dataclass
class Method:
    id: str
    group: str
    credence: int | float
    letter: str = ""  # its group's label column


@dataclass
class Tab:
    name: str
    position: int
    about: str | None  # None for a guide, text, table or sensitivity tab
    columns: list[Column]
    rows: list[list[str]] | None = None  # a guide's or a text tab's cells from A1
    interval: float | None = None  # the guide's: the share of the draws rows 12 and 14 enclose
    widths: tuple[int, ...] = ()  # a guide's, text tab's or table's column widths in px from A; empty for the defaults
    methods: list[Method] = field(default_factory=lambda: list[Method]())
    kind: str = ""  # "guide", "text", "table", "sensitivity", or "" for a column tab
    cells: dict[tuple[int, int], str | float | Node] = field(default_factory=lambda: dict[tuple[int, int], str | float | Node]())  # a table's
    formats: list[tuple[tuple[int, int, int, int], str]] = field(default_factory=lambda: list[tuple[tuple[int, int, int, int], str]]())  # a table's: (first row, first column, last row, last column), kind or format
    outputs: list[tuple[str, str]] = field(default_factory=lambda: list[tuple[str, str]]())  # a sensitivity tab's, as (tab, id)
    header_notes: dict[str, str] = field(default_factory=lambda: dict[str, str]())  # a column letter, or a column tab's column id, -> the note of its row-1 cell


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


def table(x: object, where: str) -> dict[str, object]:
    if not isinstance(x, dict):
        raise Fault(f"{where}: expected a table")
    return cast(dict[str, object], x)


def string(entry: dict[str, object], key: str, where: str) -> str:
    v = entry.get(key)
    if not isinstance(v, str):
        raise Fault(f"{where}: {key} is missing or not text")
    return v


def text_rows(x: object, where: str) -> list[list[str]]:
    if not isinstance(x, list) or not x:
        raise Fault(f"{where}: rows must be a non-empty list of rows")
    rows: list[list[str]] = []
    for i, row in enumerate(cast(list[object], x), start=1):
        if not isinstance(row, list) or not all(isinstance(v, str) for v in cast(list[object], row)):
            raise Fault(f"{where}: row {i} is not a list of text")
        rows.append(cast(list[str], row))
    if not max(len(r) for r in rows):
        raise Fault(f"{where}: rows hold no cells")
    return rows


def notes_table(x: object, name: str) -> dict[str, str]:
    """A tab's `header_notes`: each key, a column letter or a column id, with its note."""
    if not isinstance(x, dict) or not all(isinstance(v, str) for v in cast(dict[str, object], x).values()):
        raise Fault(f"{name}: header_notes is a mapping from a column letter (\"B\") or a column's id to its note's text")
    return cast(dict[str, str], x)


def header_cells(tab: Tab, have: set[int]) -> dict[int, str]:
    """Each column with a header note, by number, from its `header_note` and the tab's `header_notes`; have is the
    columns the tab writes. A key that is neither one of those letters nor one of the tab's column ids, or two notes on
    one cell, is a fault."""
    by_id = {c.id: colnum(c.letter) for c in tab.columns}
    out: dict[int, str] = {}
    keyed = [(colnum(c.letter), c.header_note, f"column {c.id}") for c in tab.columns if c.header_note]
    for key, note in tab.header_notes.items():
        n = by_id.get(key) or (colnum(key) if re.fullmatch(r"[A-Z]{1,3}", key) and colnum(key) in have else None)
        if n is None:
            raise Fault(f"{tab.name}: header_notes key {key!r} is neither a column letter the tab has nor one of its column ids")
        keyed.append((n, note, f"header_notes key {key!r}"))
    for n, note, source in keyed:
        if n in out:
            raise Fault(f"{tab.name}: two header notes on {letter(n)}1 ({source} and another)")
        out[n] = note
    return out


def comments_parts(notes: dict[int, str], sheet: int) -> tuple[str, str]:
    """One worksheet's comments part and its VML drawing: each note an Excel cell comment on row 1 of its column,
    which Google imports as a note on that cell."""
    comments = "".join(f'<comment ref="{letter(n)}1" authorId="0"><text><t xml:space="preserve">{escape(note)}</t></text></comment>'
                       for n, note in sorted(notes.items()))
    shapes = "".join(
        f'<v:shape id="_x0000_s{sheet * 1024 + k}" type="#_x0000_t202" style="position:absolute;margin-left:80pt;margin-top:2pt;'
        'width:160pt;height:80pt;z-index:1;visibility:hidden" fillcolor="#ffffe1" o:insetmode="auto"><v:fill color2="#ffffe1"/>'
        '<v:shadow color="black" obscured="t"/><v:path o:connecttype="none"/><v:textbox style="mso-direction-alt:auto"><div style="text-align:left"/></v:textbox>'
        f'<x:ClientData ObjectType="Note"><x:MoveWithCells/><x:SizeWithCells/><x:Anchor>{n}, 15, 0, 2, {n + 2}, 15, 4, 16</x:Anchor>'
        f'<x:AutoFill>False</x:AutoFill><x:Row>0</x:Row><x:Column>{n - 1}</x:Column></x:ClientData></v:shape>'
        for k, n in enumerate(sorted(notes), 1))
    vml = ('<xml xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">'
           f'<o:shapelayout v:ext="edit"><o:idmap v:ext="edit" data="{sheet}"/></o:shapelayout>'
           '<v:shapetype id="_x0000_t202" coordsize="21600,21600" o:spt="202" path="m,l,21600r21600,l21600,xe"><v:stroke joinstyle="miter"/>'
           '<v:path gradientshapeok="t" o:connecttype="rect"/></v:shapetype>' + shapes + "</xml>")
    return XML + f'<comments xmlns="{NS}"><authors><author></author></authors><commentList>{comments}</commentList></comments>', vml


def pixel_widths(t: dict[str, object], name: str) -> tuple[int, ...]:
    px = t.get("widths", [])
    if not isinstance(px, list) or not all(type(w) is int and w > 0 for w in cast(list[object], px)):
        raise Fault(f"{name}: widths is a list of whole numbers of pixels, each above 0, one a column from A")
    return tuple(cast(list[int], px))


def table_formats(t: dict[str, object], name: str) -> list[tuple[tuple[int, int, int, int], str]]:
    """A table's `formats`: each cell or block ("B5", "D1:F1") with its kind of number or literal format."""
    x = t.get("formats", {})
    if not isinstance(x, dict):
        raise Fault(f"{name}: formats is a mapping from a cell or block, such as \"D1:F1\", to a kind of number or a format")
    out: list[tuple[tuple[int, int, int, int], str]] = []
    for where, fmt in cast(dict[str, object], x).items():
        m = re.fullmatch(r"([A-Z]{1,3})(\d+)(?::([A-Z]{1,3})(\d+))?", where)
        if not m or not isinstance(fmt, str) or not fmt:
            raise Fault(f"{name}: formats {where!r} = {fmt!r} is not a cell or block (\"D1:F1\") with a kind of number or a format")
        r1, c1 = int(m.group(2)), colnum(m.group(1))
        r2, c2 = (int(m.group(4)), colnum(m.group(3))) if m.group(3) else (r1, c1)
        out.append(((min(r1, r2), min(c1, c2), max(r1, r2), max(c1, c2)), number_kind(fmt, f"{name}: formats {where!r}")))
    return out


def number_kind(fmt: str, where: str) -> str:
    """A format as given: one of KINDS_OF_NUMBER or a literal Google number format (holding 0, # or @); else a fault."""
    if fmt not in KINDS_OF_NUMBER and not re.search(r"[0#@]", fmt):
        raise Fault(f"{where}: format {fmt!r} is neither a kind of number (" + ", ".join(f'"{k}"' for k in KINDS_OF_NUMBER)
                    + ") nor a Google number format, which holds 0, # or @")
    return fmt


# The guide: the template's own rows, written by the generator ----------------------------------------------------

GUIDE = "Guide"
GUIDE_WIDTHS = (170, 600, 200, 320)  # px, columns A to D; a text column at most 600 px (notes/sheet_twin_protocol.md 2.3.6)
GUIDE_KEYS = {"name", "kind", "interval", "worked_example", "what", "start_here", "general_form", "notes", "tabs",
              "references", "details", "fill_down_script", "header_notes"}
AUTHOR = "[AUTHOR:"  # a placeholder text: written, and warned of at each generate
CREDIT = "Produced with the help of the maxwelfare.com CBA AI Assistant."
# His template's Readme sets "How to Read the Sheet" (A1), "Quick Start" (A7) and "Technical Details" (A29) as heads, Arial 16
# bold, and "Inputs" (A10), "Outputs and Intermediate Calculations" (A22) and "Combining Estimates" (A25) as subheads, Arial
# 10 bold #222222 (read 2026-11-21, R58); the guide writes them so, with `# ` and `## `.
GUIDE_SECTIONS = ("How to Read the Sheet", "Quick Start", "Inputs", "Outputs and Intermediate Calculations", "Technical Details")
GUIDE_READ = (
    "Each column is one quantity. Row 1 is its name, row 2 a note, and row 3 an input's source and the words that give "
    "its number, or a calculation's formula.",
    "Rows 4 to 11 are what you set: yellow on an input, its distribution in row 4 and its parameters below it, with "
    "min, mode and max in rows 7 to 9; grey and empty on a calculation. Rows 12 to 14 are the low end, the mean and "
    "the high end of the column's draws, and row 15 their graph. A bold name marks a result. Columns stand in "
    "categories, each opened by a narrow yellow column that names it.",
    "Numbers show two significant figures, in a unit named in words; the largest unit is quadrillion, and a value of "
    "100 to 999 quadrillion shows whole (2.7 under \"GDP (₩ quadrillion)\" is 2.7 quadrillion won, 2,700 trillion). "
    "Click a cell to see its whole value.",
)
GUIDE_KEY = {  # the colour key: each kind's sample, then what its example cell is and what the colour means
    "input": ("Input", "an input's parameter: blue text is a value you may change."),
    "formula": ("Formula", "a draw: black text is a formula that computes, whatever tab its cells sit on."),
    "cross": ("From another tab", "{what}: green text is another tab's cell, carried over unchanged."),
    "link": ("Link", "an input's source: blue underlined text is a link; click it to open the source."),
}
GUIDE_INTERVAL = ("The interval every tab shows, from its low end to its high end, encloses this share of each column's "
                  "draws: {share} runs from the {low} percentile to the {high}.")
GUIDE_DRAWS = ("From row 16 down, each row is one draw: an input draws a value from its distribution, and a calculation "
               "does math on cells of its own row.")
GUIDE_COPY = "Save a copy of this sheet by clicking 'File' -> 'Make a Copy'"
GUIDE_WORKED = 'Click on the "{tab}" tab, the worked example, and follow draw 1, row 16, from left to right.'
GUIDE_INPUTS = (
    "For an input, choose the distribution type from the dropdown in row 4, and enter the appropriate parameters in "
    "rows 5 through 11.",
    "In situations where you have a best guess and a high and low estimate, use the triangular distribution and enter "
    "the best guess in the 'mode' row.",
    "To see the results at one value of an input, such as a 2% discount rate, set that input to constant with that value.",
    "Then copy the table of results you need, and set the input back.",
    "To add an input, copy the whole column of another input into an empty column, then change its name, source and "
    "settings. The new column gets its own random numbers.",
)
GUIDE_KINDS = (
    ("beta", "inputs are min, max, and shape parameters alpha and beta. We used this when we knew a distribution would "
     "be bounded, but its shape is not likely to be uniform or triangular."),
    ("constant", "the mean value is the only input."),
    ("lognormal", "input mean and standard deviation (not the μ and σ parameters.)"),
    ("normal", "input mean and standard deviation"),
    ("power law", "input min (xmin) and alpha (typically 2 < alpha < 3)"),
    ("triangular", "input min, max, and mode (the peak or ‘most likely’ value)."),
    ("uniform", "input min and max."),
)
GUIDE_OUTPUTS = (
    "Each draw row holds the column's formula over cells of its own row: B16*C16 in row 16, B17*C17 in row 17, and so "
    "on. There are no array formulas.",
    "To change a formula, edit it in row 16, copy that cell, select the cells below it down to the last draw "
    "(Ctrl+Shift+Down) and paste.",
)
GUIDE_FILL_DOWN = " Or wait a few seconds for a script to do it for you."  # where the sheet carries tools/sheet_fill_down.gs
GUIDE_COMBINING = (
    "The 'combining estimates' columns of the {tab} tab are a tool for combining the estimates from multiple papers or "
    "sources into a single estimate. Each method is a category of its own, opened by a yellow label column that holds "
    "its name and its credence ({labels}). Enter the value, and a credence weighting of how trustworthy the source is "
    "(if in doubt, leave all credences at 1 to weight them equally). A random number column picks one method in each row.",
    "Have all calculations refer to individual rows of the combined estimate, {picks} of the {tab} tab.",
)
GUIDE_TECHNICAL = (
    "Random numbers come from a hash of the row, column, and tab position, so they stay the same every time the sheet "
    "opens and no two columns share them. Moving a tab to a new position changes its numbers.",
    "Some tabs read columns from other tabs, draw by draw. Keep all tabs the same number of rows.",
)
GUIDE_REFERENCES = (  # the template's Useful References, label and link, in columns C and D
    ("Practical Advice", "https://forum.effectivealtruism.org/posts/wsHnorrCFNffNJQmS/cba-301-practical-advice"),
    ("", "https://acotra.substack.com/p/the-art-of-the-epistemic-deal"),
    ("Example CBA", "Doi: 10.1136/bmjgh-2021-007168 https://gh.bmj.com/content/bmjgh/6/12/e007168.full.pdf"),
    ("DALY Weights", "https://www.who.int/docs/default-source/gho-documents/global-health-estimates/ghe2019_daly-methods.pdf#page=42"),
    ("US VSL/VQALY", "https://aspe.hhs.gov/sites/default/files/documents/cd2a1348ea0777b1aa918089e4965b8c/standard-ria-values.pdf"),
    ("Global VSL", "https://cdn.who.int/media/docs/default-source/bulletin/online-first/blt.25.294080.pdf"),
    ("Global Health", "https://content.sph.harvard.edu/wwwhsph/sites/2447/2019/05/BCA-Guidelines-May-2019.pdf"),
    ("", "https://researchonline.lshtm.ac.uk/id/eprint/4653001/1/vassall_etal_2018_reference_case_for_estimating_costs_global_health_services.pdf"),
    ("US Programs", "https://www.whitehouse.gov/wp-content/uploads/2023/11/CircularA-94.pdf"),
    ("", "https://www.air.org/sites/default/files/Standards-for-the-Economic-Evaluation-of-Educational-and-Social-Programs-CASP-May-2021.pdf"),
    ("", "https://aspe.hhs.gov/reports/guidelines-regulatory-impact-analysis"),
)


def pairs(g: dict[str, object], key: str) -> list[tuple[str, str]]:
    x = g.get(key, [])
    if not isinstance(x, list) or not all(isinstance(p, list) and len(cast(list[object], p)) == 2
                                          and all(isinstance(v, str) for v in cast(list[object], p)) for p in cast(list[object], x)):
        raise Fault(f"{GUIDE}: {key} is a list of pairs of texts, [\"...\", \"...\"]")
    return [(p[0], p[1]) for p in cast(list[list[str]], x)]


def ordinal(x: float) -> str:
    n = f"{round(x, 6):g}"
    return n + ("th" if n.endswith(("11", "12", "13")) or n[-1] not in "123" else {"1": "st", "2": "nd", "3": "rd"}[n[-1]])


def and_list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def colour_key(tabs: list[Tab]) -> list[list[str]]:
    """The guide's colour key: a row per kind of cell, its sample in the kind's colour (KEY_MARK) and a sentence that
    begins with an example from this sheet, Tab!B5: an input's parameter on Globals (or the first column tab), a
    draw that computes (one reading another tab where there is one), a cell that carries another tab's cell over
    unchanged (`formula_colour`: a draw where a column tab has one, else a table's plain reference such as Results'
    =Globals!C13, else a sensitivity tab's first mean, ='Option 1'!CT13, so the key keeps its green row whenever the
    sheet shows green), and a linked citation. A kind the sheet has no cell of is left out. The example is
    text: a link to a cell of another tab needs the tab's id in Google, which an uploaded file cannot know."""
    model = [t for t in tabs if t.about is not None]
    letters = {(t.name, x.id): x.letter for t in tabs for x in [*t.columns, *t.methods]}

    def cross(t: Tab, c: Column) -> bool:
        return c.formula is not None and formula_colour(draw_formula(c, letters, t.name), t.name) == GREEN

    def reads_other(t: Tab, c: Column) -> bool:
        return c.formula is not None and any(x != t.name for x, _ in refs(c.formula))

    inputs = [(t, c) for t in sorted(model, key=lambda t: t.name != "Globals") for c in t.columns if c.kind in REQUIRED]
    draws = [(t, c) for t in model for c in t.columns]
    found = {
        "input": next(((t, c, PARAM_ROW[next(k for k in PARAM_ROW if k in c.params)]) for t, c in inputs), None),
        "formula": next(((t, c, FIRST) for t, c in sorted(draws, key=lambda x: (x[1].formula is None, not reads_other(*x))) if not cross(t, c)), None),
        "cross": next(((t, c, FIRST) for t, c in draws if cross(t, c)), None),
        "link": next(((t, c, 3) for t, c in inputs if link(c.citation)[1] is not None), None),
    }
    cells = {kind: (t.name, f"{c.letter}{r}", "a draw") for kind, x in found.items() if x is not None for t, c, r in [x]}
    if "cross" not in cells:  # no column tab carries a cell over: a table's plain reference to another tab
        for t in (t for t in tabs if t.kind == "table"):
            carried = [(r, c) for (r, c), v in sorted(t.cells.items()) if not isinstance(v, (str, int, float))
                       and (m := CARRIED.fullmatch(write(v, in_sheet(letters, t.name))[0])) is not None
                       and (m.group(2) if m.group(1) is None else m.group(1).replace("''", "'")) != t.name]
            if carried:
                cells["cross"] = (t.name, f"{letter(carried[0][1])}{carried[0][0]}", "a result")
                break
    sens = next((t for t in tabs if t.kind == "sensitivity" and t.outputs), None)
    if "cross" not in cells and sens is not None:  # else a sensitivity tab's first mean, its first output's row 13 carried over
        cells["cross"] = (sens.name, f"{letter(4)}{SENS_STATS}", "a result")
    return [[f"{KEY_MARK}{kind}}}{GUIDE_KEY[kind][0]}", f"{name}!{cell}, {GUIDE_KEY[kind][1].format(what=what)}"]
            for kind in GUIDE_KEY if kind in cells for name, cell, what in [cells[kind]]]


def guide_rows(g: dict[str, object], tabs: list[Tab]) -> list[list[str]]:
    """The guide's rows from A1: the template's instructions, then the data file's own, beside the references."""
    def text(key: str, required: bool = True) -> str | None:
        if key not in g and not required:
            return None
        return string(g, key, GUIDE)

    share = cast(float, tabs[0].interval)
    worked = cast(str, text("worked_example"))
    if not worked.startswith(AUTHOR) and worked not in (t.name for t in tabs if t.about is not None):
        raise Fault(f"{GUIDE}: worked_example {worked!r} is no column tab of the file")
    fill = g.get("fill_down_script", False)
    if not isinstance(fill, bool):
        raise Fault(f"{GUIDE}: fill_down_script is true or false")
    notes = pairs(g, "notes")

    def under(heading: str) -> list[list[str]]:  # the notes titled with a template section's heading, at its end, untitled
        return [["", x] for title, x in notes if title == heading]

    described = pairs(g, "tabs")
    names = [t.name for t in tabs[1:]]
    given = [n for n, _ in described]
    if sorted(given) != sorted(names):
        raise Fault(f"{GUIDE}: tabs describes {sorted(set(given) - set(names)) or 'no unknown tab'} that the file lacks, "
                    f"misses {sorted(set(names) - set(given)) or 'no tab'}, or names a tab twice; one description a tab")
    body: list[list[str]] = [
        [f"# {GUIDE_SECTIONS[0]}"], *(["", x] for x in GUIDE_READ),
        [SETTING, GUIDE_INTERVAL.format(share=f"{round(share * 100, 6):g}%", low=ordinal((1 - share) * 50), high=ordinal((1 + share) * 50))],
        ["", GUIDE_DRAWS], *colour_key(tabs), *under(GUIDE_SECTIONS[0]),
        [f"# {GUIDE_SECTIONS[1]}"], ["", GUIDE_COPY], ["", worked if worked.startswith(AUTHOR) else GUIDE_WORKED.format(tab=worked)], *under(GUIDE_SECTIONS[1]),
        [f"## {GUIDE_SECTIONS[2]}"], *(["", x] for x in GUIDE_INPUTS), *([f"**{k}**", x] for k, x in GUIDE_KINDS), *under(GUIDE_SECTIONS[2]),
        [f"## {GUIDE_SECTIONS[3]}"], ["", GUIDE_OUTPUTS[0]], ["", GUIDE_OUTPUTS[1] + (GUIDE_FILL_DOWN if fill else "")],
        *under(GUIDE_SECTIONS[3]),
    ]
    for i, t in enumerate(t for t in tabs if t.methods):
        if i == 0:
            body.append(["## Combining Estimates"])
        labels = and_list([f"{{col:{t.name}.{m.id}}}" for m in t.methods])
        picks = [f"{{col:{t.name}.{c.id}}}" for c in t.columns if c.formula is not None and "CREDENCE(" in source(c.formula, t.name)]
        body.append(["", GUIDE_COMBINING[0].format(tab=t.name, labels=labels)])
        if picks:
            body.append(["", GUIDE_COMBINING[1].format(tab=t.name, picks=("column " if len(picks) == 1 else "columns ") + and_list(picks))])
    body += [[f"# {GUIDE_SECTIONS[4]}"], *(["", x] for x in GUIDE_TECHNICAL), *under(GUIDE_SECTIONS[4]), ["# This sheet"],
             ["**What this is**", cast(str, text("what"))], ["**Start here**", cast(str, text("start_here"))]]
    general = text("general_form", False)
    if general is not None:
        body.append(["**The general form**", general])
    body += [[f"**{title}**" if title else "", note] for title, note in notes if title not in GUIDE_SECTIONS]
    body.append(["# The tabs, left to right"])
    for t in tabs[1:]:
        body.append([f"**{t.name}**", dict(described)[t.name]])
        if t.kind == "sensitivity":  # how its numbers are found, beside its description rather than on the tab
            body += [["", x] for x in GUIDE_SENSITIVITY]
    details = text("details", False)
    if details is not None:
        body.append(["**Details and caveats**", details])
    known = {link(x)[1] for _, x in GUIDE_REFERENCES}
    refs = [["# Useful References"], *([a, b] for a, b in GUIDE_REFERENCES),
            *([a, b] for a, b in pairs(g, "references") if link(b)[1] is None or link(b)[1] not in known)]
    body += [[""]] * (len(refs) - 1 - len(body))
    rows = [["", CREDIT, *refs[0]]]
    for i, row in enumerate(body, start=1):
        rows.append(row + [""] * (2 - len(row)) + refs[i] if i < len(refs) else row)
    return rows


def load(path: Path) -> list[Tab]:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise Fault(f"{path}: not valid TOML: {e}") from None
    if set(raw) - {"tab"}:
        raise Fault(f"{path}: unknown keys {sorted(set(raw) - {'tab'})}")
    entries = raw.get("tab")
    if not isinstance(entries, list):
        raise Fault(f"{path}: no [[tab]] entries")
    tabs: list[Tab] = []
    guide: dict[str, object] = {}
    pending: list[tuple[Tab, dict[str, object], list[dict[str, object]]]] = []  # column tabs, built once every id is known
    tables: list[tuple[Tab, object]] = []
    sensitivity: list[tuple[Tab, object]] = []
    ids: dict[str, list[str]] = {}
    for position, e in enumerate(cast(list[object], entries), start=1):
        t = table(e, f"tab {position}")
        name = string(t, "name", f"tab {position}")
        if name in (x.name for x in tabs):
            raise Fault(f"{name}: a second tab of this name")
        if "group" in t:
            raise Fault(f"{name}: group {t['group']!r} belongs on a column of a column tab, not on a tab")
        kind = t.get("kind", None)
        if (kind == "guide") != (position == 1):
            raise Fault(f"{name}: the first tab, and only the first, is the guide: name = {GUIDE!r} and kind = \"guide\"")
        if kind == "guide":
            if name != GUIDE or set(t) - GUIDE_KEYS:
                raise Fault(f"{name}: the guide is named {GUIDE!r} and has no keys but {sorted(GUIDE_KEYS)}")
            share = t.get("interval")
            if isinstance(share, bool) or not isinstance(share, (int, float)) or not 0 < share < 1:
                raise Fault(f"{name}: interval is a number between 0 and 1, such as 0.9")
            tabs.append(Tab(name, position, None, [], None, float(share), GUIDE_WIDTHS, kind="guide"))
            guide = t
            continue
        if kind == "text":
            if set(t) - {"name", "kind", "rows", "widths", "header_notes"}:
                raise Fault(f"{name}: a text tab has unknown keys {sorted(set(t) - {'name', 'kind', 'rows', 'widths', 'header_notes'})}")
            tabs.append(Tab(name, position, None, [], text_rows(t["rows"], name) if "rows" in t else None, None,
                            pixel_widths(t, name), kind="text"))
            continue
        if kind in ("table", "sensitivity"):
            key = "rows" if kind == "table" else "outputs"
            optional = ({"formats", "widths"} if kind == "table" else set[str]()) | {"header_notes"}
            if not {"name", "kind", key} <= set(t) <= {"name", "kind", key} | optional:
                raise Fault(f"{name}: a {kind} tab has name, kind and {key}, and may have " + ("formats, widths and " if kind == "table" else "")
                            + f"header_notes, not {sorted(t)}")
            tabs.append(Tab(name, position, None, [], widths=pixel_widths(t, name), kind=kind, formats=table_formats(t, name)))
            (tables if kind == "table" else sensitivity).append((tabs[-1], t[key]))
            continue
        if kind is not None:
            raise Fault(f"{name}: unknown tab kind {kind!r}; a tab is a column tab or of kind guide, text, table or sensitivity")
        if "note" in t:
            raise Fault(f"{name}: a column tab has no note: the tab's explanation belongs in the guide, and one line of it in about")
        if set(t) - {"name", "about", "column", "method", "header_notes"}:
            raise Fault(f"{name}: unknown keys {sorted(set(t) - {'name', 'about', 'column', 'method', 'header_notes'})}")
        cols = t.get("column", [])
        if not isinstance(cols, list):
            raise Fault(f"{name}: column must be [[tab.column]] entries")
        raw_cols = [table(c, f"{name}: column {i + 1}") for i, c in enumerate(cast(list[object], cols))]
        ids[name] = []
        for i, c in enumerate(raw_cols):
            cid = c.get("id")
            if not isinstance(cid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", cid) or cid in ("u", DRAW):
                raise Fault(f"{name}: column {i + 1} ({letter(i + 2)}): id {cid!r} is not a lower-case identifier other than u and {DRAW}")
            if cid in ids[name]:
                raise Fault(f"{name}: column {cid}: duplicate id")
            ids[name].append(cid)
        about = string(t, "about", name)
        if "\n" in about:
            raise Fault(f"{name}: about is one line")
        tabs.append(Tab(name, position, about, []))
        pending.append((tabs[-1], t, raw_cols))
    for tab, t, raw_cols in pending:
        tab.methods = read_methods(tab.name, t.get("method", []), cast(list[object], ids[tab.name]))
        credences = {m.id: m.credence for m in tab.methods}
        for i, c in enumerate(raw_cols):
            tab.columns.append(column(c, i, tab.name, ids, credences))
            group = c.get("group")
            if group is not None and not isinstance(group, str):
                raise Fault(f"{tab.name}: column {tab.columns[-1].id}: group is not text")
            tab.columns[-1].group = group
        place_groups(tab.name, tab.columns)
        for m in tab.methods:
            first = next((c for c in tab.columns if c.group == m.group), None)
            if first is None:
                raise Fault(f"{tab.name}: method {m.id}: group {m.group!r} is no group of the tab's columns")
            m.letter = letter(colnum(first.letter) - 1)
    for tab, e in zip(tabs, cast(list[object], entries)):
        tab.header_notes = notes_table(table(e, tab.name).get("header_notes", {}), tab.name)
    if not guide:
        raise Fault(f"{path}: no guide: the first [[tab]] is name = {GUIDE!r}, kind = \"guide\"")
    for tab, x in tables:
        tab.cells = title_note(tab.name, table_cells(tab.name, x, ids))
    for tab, x in sensitivity:
        if not isinstance(x, list) or not x or not all(isinstance(o, str) for o in cast(list[object], x)):
            raise Fault(f"{tab.name}: outputs is a non-empty list of columns, each written Tab!id")
        for o in cast(list[str], x):
            node = parse(o, "", ids, {}, f"{tab.name}: output {o}")
            if not isinstance(node, Ref):
                raise Fault(f"{tab.name}: output {o!r} is not one column, written Tab!id")
            tab.outputs.append((node.tab, node.id))
    tabs[0].rows = guide_rows(guide, tabs)  # after the tables and outputs, whose cells the colour key may take its green example from
    resolve_letters(tabs)
    for t in tabs:
        if t.about is not None and too_long(t.about, TITLE_CHARS):
            raise Fault(f"{t.name}: about {t.about!r} is not words of at most {TITLE_CHARS} characters with none over {WORD_CHARS}, the limits of A1")
        for c in t.columns:
            if too_long(c.name, NAME_CHARS):
                raise Fault(f"{t.name}: column {c.id} ({c.letter}): name {c.name!r} is not words of at most {NAME_CHARS} characters "
                            f"with none over {WORD_CHARS}, the limits of a column name's cell")
    bounds(tabs)
    return tabs


def table_cells(tab: str, x: object, ids: dict[str, list[str]]) -> dict[tuple[int, int], str | float | Node]:
    """A table's cells by (row, column): a text, a number, or a formula (a text beginning with "=") read as a tree."""
    if not isinstance(x, list):
        raise Fault(f"{tab}: rows must be a list of rows")
    cells: dict[tuple[int, int], str | float | Node] = {}
    for r, row in enumerate(cast(list[object], x), start=1):
        if not isinstance(row, list):
            raise Fault(f"{tab}: row {r} is not a list of cells")
        for c, v in enumerate(cast(list[object], row), start=1):
            where = f"{tab}: {letter(c)}{r}"
            if isinstance(v, str) and v.startswith("="):
                cells[(r, c)] = parse(v[1:], tab, ids, {}, where, table=True)
            elif isinstance(v, str):
                if v:
                    cells[(r, c)] = v
            elif isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
                cells[(r, c)] = float(v)
            else:
                raise Fault(f"{where}: a cell is a text, a finite number or a formula, not {v!r}")
    return cells


def title_note(tab: str, cells: dict[tuple[int, int], str | float | Node]) -> dict[tuple[int, int], str | float | Node]:
    """A table whose A1 holds a title and a paragraph ("Results: the 10-year ...", the title at most TITLE_CHARS before
    the first ": " or ". ") keeps the title in A1, bold and larger, and the paragraph in A2, a note row of its own at
    Arial 10; the texts of column A under it move down a row each, into the first empty row, so no cell that holds a
    number or formula moves."""
    a1 = cells.get((1, 1))
    m = re.match(r"(.{1,%d}?)[:.] (.+)" % TITLE_CHARS, a1, re.S) if isinstance(a1, str) and len(a1) > TITLE_CHARS else None
    if m is None:
        return cells
    texts = 2
    while isinstance(cells.get((texts, 1)), str) and not any(c > 1 for r, c in cells if r == texts):
        texts += 1
    if (texts, 1) in cells or any(r == texts for r, _ in cells):
        raise Fault(f"{tab}: A1 holds a title and a paragraph, and the paragraph needs an empty row below the texts of "
                    f"column A under it, which row {texts} is not")
    out = dict(cells)
    for r in range(texts, 2, -1):
        out[(r, 1)] = out[(r - 1, 1)]
    note = m.group(2).strip()
    out[(1, 1)], out[(2, 1)] = m.group(1), note[0].upper() + note[1:]
    return out


NAME_CHARS, TITLE_CHARS, WORD_CHARS = 40, 45, 11  # a column name's cell (and a group's), A1, and a word on one line of either


def too_long(text: str, chars: int) -> bool:
    return len(text) > chars or any(len(w) > WORD_CHARS for w in text.split())


SETTING = "{interval}"


def bounds(tabs: list[Tab]) -> tuple[str, tuple[float, float]]:
    """The setting's cell as a formula cites it (Guide!$B$7), and the two percentiles rows LOW and HIGH show at its value."""
    holders = [t for t in tabs if t.interval is not None]
    if len(holders) != 1:
        raise Fault(f"the guide carries interval, the share of the draws every tab's rows {LOW} and {HIGH} enclose; {len(holders)} tabs do")
    t, share = holders[0], cast(float, holders[0].interval)
    cells = [(r, c) for r, row in enumerate(t.rows or [], start=1) for c, v in enumerate(row, start=1) if v == SETTING]
    if len(cells) != 1:
        raise Fault(f"{t.name}: exactly one cell of its rows is {SETTING}, the cell that holds the setting; {len(cells)} are")
    return f"{sheet_name(t.name)}!${letter(cells[0][1])}${cells[0][0]}", ((1 - share) / 2, (1 + share) / 2)


def read_methods(tab: str, x: object, column_ids: list[object]) -> list[Method]:
    """A column tab's [[tab.method]] entries, each checked but its group, which place_groups must first lay out."""
    if not isinstance(x, list):
        raise Fault(f"{tab}: method must be [[tab.method]] entries")
    methods: list[Method] = []
    for i, e in enumerate(cast(list[object], x), start=1):
        m = table(e, f"{tab}: method {i}")
        mid = m.get("id")
        if not isinstance(mid, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", mid) or mid == "u":
            raise Fault(f"{tab}: method {i}: id {mid!r} is not a lower-case identifier other than u")
        where = f"{tab}: method {mid}"
        if set(m) - {"id", "group", "credence"}:
            raise Fault(f"{where}: unknown keys {sorted(set(m) - {'id', 'group', 'credence'})}; a method has id, group and credence")
        if mid in (y.id for y in methods):
            raise Fault(f"{where}: a second method of this id")
        if mid in column_ids:
            raise Fault(f"{where}: id {mid} is also a column's id; methods and columns share one namespace")
        group = string(m, "group", where)
        if group in (y.group for y in methods):
            raise Fault(f"{where}: group {group!r} already carries a method; a label column holds one credence")
        credence = m.get("credence")
        if isinstance(credence, bool) or not isinstance(credence, (int, float)) or not (credence > 0 and math.isfinite(credence)):
            raise Fault(f"{where}: credence {credence!r} is not a finite number greater than 0")
        methods.append(Method(mid, group, credence))
    return methods


def column(c: dict[str, object], i: int, tab: str, ids: dict[str, list[str]], credences: dict[str, int | float]) -> Column:
    """One column, its id already checked; ids are every column tab's ids, credences the tab's methods'."""
    cid = cast(str, c["id"])
    where = f"{tab}: column {cid}"
    kind = string(c, "kind", where)
    name = string(c, "name", where)
    note = string(c, "note", where) if "note" in c else ""
    fmt = number_kind(string(c, "format", where), where) if "format" in c else "number"
    header_note = string(c, "header_note", where) if "header_note" in c else ""
    common = {"id", "name", "kind", "note", "format", "group", "header_note"}
    if "credence" in c:
        raise Fault(f"{where}: a column carries no credence; a credence now belongs to a [[tab.method]] with id, group and credence")
    if kind == "read":
        raise Fault(f"{where}: kind read is gone: cite the column itself, as Tab!id (Globals!discount_rate) or 'Tab name'!id, "
                    "in each formula that uses it")
    if "result" in c and kind != "calc":
        raise Fault(f"{where}: result marks a calculation, not a column of kind {kind}")
    if kind == "calc":
        if set(c) - common - {"formula", "result"}:
            raise Fault(f"{where}: unknown keys {sorted(set(c) - common - {'formula', 'result'})}")
        result = c.get("result", False)
        if not isinstance(result, bool):
            raise Fault(f"{where}: result is true or false")
        node = parse(string(c, "formula", where), tab, ids, credences, where)
        return Column(cid, name, kind, letter(i + 2), "", {}, node, note, fmt, result, header_note=header_note)
    if kind not in REQUIRED:
        raise Fault(f"{where}: unknown kind {kind!r}; one of calc, {', '.join(REQUIRED)}")
    keys = set(c) - common - {"citation"}
    if keys - set(PARAM_ROW):
        raise Fault(f"{where}: unknown keys {sorted(keys - set(PARAM_ROW))}")
    if keys - REQUIRED[kind]:
        raise Fault(f"{where}: parameters {sorted(keys - REQUIRED[kind])} do not belong to kind {kind}")
    if REQUIRED[kind] - keys:
        raise Fault(f"{where}: kind {kind} lacks parameters {sorted(REQUIRED[kind] - keys)}")
    params: dict[str, int | float] = {}
    for k in sorted(keys, key=PARAM_ROW.__getitem__):
        v = c[k]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise Fault(f"{where}: {k} is not a number")
        params[k] = v
    if kind == "power law" and not params["alpha"] > 2:  # mean lo (alpha - 1) / (alpha - 2), infinite at alpha <= 2
        raise Fault(f"{where}: alpha {params['alpha']!r} gives an infinite mean, so the draws' mean depends on the seed; alpha must be above 2")
    return Column(cid, name, kind, letter(i + 2), string(c, "citation", where), params, None, note, fmt, header_note=header_note)


def place_groups(tab: str, columns: list[Column]) -> None:
    """Refuse a tab's faulty groups, and move each column's letter past the label columns before it."""
    if all(c.group is None for c in columns):
        return
    bare = next((c for c in columns if c.group is None), None)
    if bare is not None:
        raise Fault(f"{tab}: column {bare.id} has no group while other columns of the tab have one; give every column a group or none")
    seen: list[str] = []
    for i, c in enumerate(columns):
        g = cast(str, c.group)
        if i == 0 or g != columns[i - 1].group:
            if g in seen:
                raise Fault(f"{tab}: group {g!r} stands on two separate runs of columns; a group's columns are adjacent")
            if not g.strip() or too_long(g, NAME_CHARS):
                raise Fault(f"{tab}: group {g!r} is not words of at most {NAME_CHARS} characters with none over {WORD_CHARS}, the limits of a column name's cell")
            seen.append(g)
        c.letter = letter(i + 2 + len(seen))


PLACEHOLDER = re.compile(r"\{col:([^{}]*)\}")
ROW_PLACEHOLDER = re.compile(r"\{row:([^{}:]*):([^{}]*)!([^{}!]*)\}")  # {row:Table:Tab!id}


def resolve_letters(tabs: list[Tab]) -> None:
    """Replace each {col:id} or {col:Tab name.id} in abouts, names, notes, citations and text rows by the column's
    letter, and each {row:Table:Tab!id} by the first row of that table whose cells cite the column, and refuse any of them that begins with "=" (Google reads such a text as a formula on upload)."""
    letters = {(t.name, x.id): x.letter for t in tabs for x in [*t.columns, *t.methods]}

    def sub(text: str, tab: str, where: str) -> str:
        def one(m: re.Match[str]) -> str:
            ref = m.group(1)
            key = (ref.rsplit(".", 1)[0], ref.rsplit(".", 1)[1]) if "." in ref else (tab, ref)
            if key not in letters:
                raise Fault(f"{where}: {m.group(0)} names no column of the file")
            return letters[key]

        def row(m: re.Match[str]) -> str:
            table = next((t for t in tabs if t.name == m.group(1) and t.kind == "table"), None)
            found = None if table is None else min((r for (r, _), v in table.cells.items()
                                                    if not isinstance(v, (str, int, float)) and (m.group(2), m.group(3)) in refs(v)), default=None)
            if found is None:
                raise Fault(f"{where}: {m.group(0)} names no row of a table that cites that column")
            return str(found)

        out = ROW_PLACEHOLDER.sub(row, PLACEHOLDER.sub(one, text))
        if out.startswith("=") or marked(out)[1].startswith("="):
            raise Fault(f"{where}: begins with '=', which Google reads as a formula on upload")
        return out

    for t in tabs:
        if t.about is not None:
            t.about = sub(t.about, t.name, f"{t.name}: about")
        if t.rows is not None:
            t.rows = [[sub(v, t.name, f"{t.name}: row {r}") for v in row] for r, row in enumerate(t.rows, start=1)]
        for c in t.columns:
            c.name = sub(c.name, t.name, f"{t.name}: column {c.id}: name")
            c.note = sub(c.note, t.name, f"{t.name}: column {c.id}: note")
            c.citation = sub(c.citation, t.name, f"{t.name}: column {c.id}: citation")


# Python's columns ------------------------------------------------------------------------------------------------


def draw(kind: str, p: dict[str, float], u: Floats) -> Floats:
    """The template's generator, kind by kind."""
    if kind == "beta":
        return p["lo"] + (p["hi"] - p["lo"]) * np.asarray(stats.beta.ppf(u, p["alpha"], p["beta"]), dtype=np.float64)
    if kind == "constant":
        return p["mean"] + 0 * u
    if kind == "lognormal":
        m, s = p["mean"], p["sd"]
        loc, scale = np.log(m**2 / np.sqrt(m**2 + s**2)), np.sqrt(np.log(1 + s**2 / m**2))
        return np.exp(np.asarray(stats.norm.ppf(u, loc, scale), dtype=np.float64))
    if kind == "normal":
        return np.asarray(stats.norm.ppf(u, p["mean"], p["sd"]), dtype=np.float64)
    if kind == "power law":
        return p["lo"] * (1 - u) ** (-1 / (p["alpha"] - 1))
    if kind == "triangular":
        lo, hi, peak = p["lo"], p["hi"], p["peak"]
        return np.where(u <= (peak - lo) / (hi - lo), lo + np.sqrt(u * (hi - lo) * (peak - lo)), hi - np.sqrt((1 - u) * (hi - lo) * (hi - peak)))
    return p["lo"] + u * (p["hi"] - p["lo"])  # uniform


def compute(tabs: list[Tab]) -> dict[str, dict[str, Floats]]:
    """Every column's draws, by tab and id in the file's order, each computed after the columns it cites, wherever they
    stand; a cycle is refused."""
    found = {(t.name, c.id): (t, i, c) for t in tabs for i, c in enumerate(t.columns)}
    try:
        order = list(TopologicalSorter({k: refs(c.formula) if c.formula else set() for k, (_, _, c) in found.items()}).static_order())
    except CycleError as e:
        cycle = cast(list[tuple[str, str]], e.args[1])
        raise Fault("a cycle of formulas: " + " -> ".join(f"{t}!{c}" for t, c in cycle)) from None
    values: dict[tuple[str, str], Floats] = {}
    with np.errstate(all="ignore"):
        for k in order:
            tab, i, c = found[k]
            if c.formula is None:
                values[k] = draw(c.kind, {x: float(v) for x, v in c.params.items()}, sheet_uniforms(tab.position, i + 2, DRAWS, FIRST))
            else:
                values[k] = evaluate(c.formula, values)
    return {t.name: {c.id: values[(t.name, c.id)] for c in t.columns} for t in tabs}


def table_values(tab: Tab, computed: dict[str, dict[str, Floats]], pct: tuple[float, float]) -> dict[tuple[int, int], tuple[Scalar, float]]:
    """Each cell of a table as the twin computes it, with its scale (`scalar`); a cycle among its cells is refused."""
    done: dict[tuple[int, int], tuple[Scalar, float]] = {}
    busy: set[tuple[int, int]] = set()

    def cell(r: int, c: int) -> Scalar:
        if (r, c) not in done:
            v = tab.cells.get((r, c))
            if (r, c) in busy:
                raise Fault(f"{tab.name}: {letter(c)}{r} cites itself through its cells")
            busy.add((r, c))
            done[(r, c)] = (v, abs(v) if isinstance(v, float) else 0.0) if v is None or isinstance(v, (str, int, float)) else \
                scalar(v, lambda t, x: computed[t][x], cell, pct)
            busy.discard((r, c))
        return done[(r, c)][0]

    for r, c in tab.cells:
        cell(r, c)
    return done


# generate --------------------------------------------------------------------------------------------------------

KINDS_LIST = sorted(REQUIRED)  # the template's dropdown, in its order
SET = {"mean": "Set: mean", "sd": "Set: std dev", "lo": "Set: min", "peak": "Set: mode", "hi": "Set: max", "alpha": "Set: alpha", "beta": "Set: beta"}
LABELS = {2: "Notes", 3: "Source or formula", KIND_ROW: "Set: distribution", **{PARAM_ROW[k]: v for k, v in SET.items()},
          MEAN: "Draws: mean", 15: "Graph"}
YELLOW, GREY, BLUE = "FFF2CC", "E8E8E8", "D9EBFF"
LINE = "CCCCCC"  # the borders, the gray of Sheets' own gridlines
# Font colour marks a cell's kind (the owner, Decision 23, 2026-11-20, and his words after it): a value a person may
# change, a formula that computes, another tab's cell carried over unchanged (`formula_colour`), a hyperlink. The values are the seat's choices, not his: input blue
# the usual banking-model blue, never underlined; link blue Google's own link colour, underlined, so the two differ in
# shade and underline; green the usual banking-model green; every other cell black.
BLACK, INPUT_BLUE, GREEN, LINK_BLUE = "000000", "0000FF", "008000", "1155CC"
# The guide's text: his Monte Carlo Template's Readme (1FNCjzT3fCH2J2XU_P-NsmGBJahm2rz6U58mxyScAWno) sets its body (Readme
# A2 to A5, A8, A9, A11) and its subheads (A10 "Inputs", A22, A25) in foreground 0.1333 in each channel, #222222, and its
# section heads (A1, A7) in black; read through the Sheets connector, 2026-11-21 (R58).
INK = "222222"
COLOURS = (BLACK, INPUT_BLUE, GREEN, LINK_BLUE, INK)
LABEL = "FFFF00"  # a label column's name cell
TINTS = ("F4CCCC", "FFF2CC", "D9EAD3", "CFE2F3", "D9D2E9", "FCE5CD")  # the name cells of a tab's blocks in turn: pale pink, yellow, green, blue, lavender, orange
FORMATTED = {5, 6, 7, 8, 9, LOW, MEAN, HIGH}  # with the draws, the rows a column's format applies to
SHAPE_ROWS = {PARAM_ROW["alpha"], PARAM_ROW["beta"]}  # a beta's shape parameters, shown at two significant figures in no kind's format


@dataclass(frozen=True)
class Label:
    """A text that names a tab, written as a formula that shows the tab's present name, with its text cached."""
    formula: str  # beginning with "="
    text: str


CellValue = str | int | float | Label | None  # a text beginning with "=" is a formula

# The look, in Google's pixels: an xlsx width unit opens at 7 px, and a point of row height at 4/3 px.
Font = tuple[str, int, bool, str]  # name, size, bold, colour (COLOURS; LINK_BLUE is underlined)
# Type: every cell Arial 10, a tab's title alone bold and larger (notes/sheet_twin_protocol.md 2.3.6; the owner, 2026-11-20)
FONT, SIZE, HEADING_SIZE, MODEL_TITLE_SIZE = "Arial", 10, 16, 11  # HEADING_SIZE: a guide's or text tab's heading, a table's or Sensitivity's title; MODEL_TITLE_SIZE: a column tab's A1
ARIAL10: Font = (FONT, SIZE, False, BLACK)
HEADING: Font = (FONT, HEADING_SIZE, True, BLACK)  # his template's Readme A1, A7, A29: Arial 16 bold, black
SUBHEAD: Font = (FONT, SIZE, True, BLACK)  # a text tab's subhead (`## `); the guide's in INK, as his template's Readme A10, A22, A25: Arial 10 bold
LINK_FONT: Font = (FONT, SIZE, False, LINK_BLUE)
INPUT_FONT: Font = (FONT, SIZE, False, INPUT_BLUE)
WIDTH_A, WIDTH, SPARE = 120, 70, 12  # px; SPARE empty columns after the last on every column tab
TEXT_WIDTHS = (575, 150)  # a text tab's columns A and B, before any is widened to fit its text
HEIGHT = {1: 69, 2: 56, 3: 54, **dict.fromkeys(range(4, 15), 19), 15: 67}  # px; every draw row 21. Row 1 holds five lines of a name, row 2 four of a note
DRAW_HEIGHT = 21
LOOK: dict[int, tuple[str | None, str, bool]] = {  # a column's rows: horizontal, vertical, wrap
    1: ("center", "top", True), 2: ("left", "top", True), 3: ("left", "top", True),
    4: ("center", "bottom", False), 5: ("center", "bottom", False),
    6: ("center", "bottom", False), PARAM_ROW["lo"]: ("left", "bottom", False),
    PARAM_ROW["peak"]: ("center", "bottom", False), PARAM_ROW["hi"]: ("right", "bottom", False),
    10: ("center", "bottom", False), 11: ("center", "bottom", False),
    LOW: ("left", "bottom", False), MEAN: ("center", "bottom", False),
    HIGH: ("right", "bottom", False), 15: (None, "top", False),
}
DRAW_LOOK: tuple[str | None, str, bool] = ("right", "bottom", False)
# The layout of every tab but a column tab's header, which `generate` checks before it writes anything
# (notes/sheet_twin_protocol.md 2.3.6; notes/sheet_layout_review.md 4.4 and 4.7):
CHAR_PX, CELL_PAD_PX = 6, 10  # px a character at Arial 10 (s x 6/10 at size s), and a cell's padding
LINE_PX, ROW_PAD_PX, MIN_ROW_PX = 15, 6, 21  # a row is lines x 15 + 6 px at Arial 10 (a line s x 4/3 at size s), at least 21
NARROW_PX, MAX_LINES = 150, 5  # no text runs past 5 lines in a column under 150 px (review 4.4): its column is widened
NARROW_LINES = 3  # in a table, a text of this many lines in a column under NARROW_PX widens it (protocol 2.3.6: never wrapped in a narrow column)
BOLD_PX = 1.1  # a bold character's width over a plain one's, for the lines a bold title wraps to (the seat's estimate)
TEXT_MAX_PX, TABLE_PX = 600, 100  # a text column is widened at most to 600 px (protocol 2.3.6); a table column opens at Google's 100
LABEL_CHARS = 80  # a text this short that begins with a tab's name is a label, which follows a rename; a longer one is prose
KINDS_OF_NUMBER = ("number", "$", "%", "year")
MAX_DECIMALS = 4  # the most decimals a kind's draws show
PCT_DECIMALS = 5  # the most a share near 100% shows before the keep rule adds one: "100.00000%" fills a 70 px column (WIDTH)


def number_format(sign: str, decimals: int) -> str:
    """A Google number format: the sign ("" or "$"), thousands separators and the decimals."""
    return sign + "#,##0" + ("." + "0" * decimals if decimals else "")


def draws_format(kind: str, d: Floats, keep: tuple[float, ...] = ()) -> str:
    """The format of a kind's rows 12 to 14 and draws, or of a table's number: two significant figures of the mean of
    the draws' absolute values, of the smaller of p and 1 - p for a "%" between 0 and 1 (so 0.996 shows 99.6%), and in
    scientific form where that needs more than MAX_DECIMALS decimals; with the decimals each value of keep (a column's
    low end, mean and high end) needs to keep its digits, a "%" strictly between 0 and 1 never 0% or 100% and any
    other number between 0.5 and 1 never 1."""
    if kind == "year":
        return "0"
    finite = np.abs(d[np.isfinite(d)])
    size = float(finite.mean()) if finite.size else 0.0
    sign, pct = ("$" if kind == "$" else ""), ("%" if kind == "%" else "")
    near_one = kind == "%" and 0.5 < size < 1
    x = float(f"{(1 - size if near_one else size) * (100 if pct else 1):.1e}")  # rounded first, so 9.96 counts as 10
    decimals = 0 if x <= 0 else max(0, 1 - math.floor(math.log10(x)))
    if near_one:  # 100.00000% is the widest a 70 px column holds
        decimals = min(decimals, PCT_DECIMALS)
    if decimals > MAX_DECIMALS and not near_one:
        return sign + "0.0E+00" + pct

    def lost(v: float) -> bool:  # v shows 0%, 100% or 1 at these decimals
        if pct:
            return 0 < v < 1 and rounded(v * 100, decimals) in (0, 100)
        return 0.5 < abs(v) < 1 and abs(rounded(v, decimals)) == 1

    while (not near_one or decimals <= PCT_DECIMALS) and any(lost(v) for v in keep if math.isfinite(v)):  # 99.999997% still fits
        decimals += 1
    return number_format(sign, decimals) + pct


def run_format(kind: str, d: Floats) -> str:
    """One format for a run of a table's or Sensitivity's numbers (a block's column), from all their values: a literal
    format as given; a "%" with the decimals that show each share strictly between 0 and 1 at two significant figures
    of its distance from 0% or 100% (45%, 6.6%, 99.6%), so the largest shows no more where the run's shares are of one
    size, and more where a value would show as 0% or 100% (0.9996 as 99.96%), at most MAX_DECIMALS; any other kind as
    `draws_format`, two significant figures at the run's typical size."""
    if kind not in KINDS_OF_NUMBER:
        return kind
    if kind != "%":
        return signed_zero(draws_format(kind, d), d)
    inner = d[np.isfinite(d) & (d > 0) & (d < 1)]
    far = 100 * np.minimum(inner, 1 - inner)  # each share's distance from 0% or 100%, in points
    places = 0 if not far.size else max(0, 1 - math.floor(math.log10(float(far.min()))))  # its smallest at two figures
    places = min(places, MAX_DECIMALS)
    inner = 100 * inner
    while places < MAX_DECIMALS and bool(((np.round(inner, places) <= 0) | (np.round(inner, places) >= 100)).any()):
        places += 1
    return signed_zero(number_format("", places) + "%", d)


STEP = re.compile(r"\$?#,##0(?:\.(0+))?(,*)(%?)")  # a format of `number_format`, scaled by commas or a percent


def signed_zero(fmt: str, d: Floats, prefix: str = "", suffix: str = "") -> str:
    """prefix + fmt + suffix, or where a negative value of d rounds to zero in fmt (Sheets shows -47,317 in
    "#,##0.0,," as "-0.0", seen live), a format of two sections: a value at or below minus half the format's step
    shows with its minus, and any other with none, so a tiny negative shows 0.0. A section with a condition carries
    no "-" of its own: Sheets shows a negative value's minus itself in a conditional section, so a written "-" showed
    -200,000 as "--0.2" on the live v2 ROK sheet (the layout look's reading of Google's displayed values, R53,
    2026-11-21; register row 2.2); without it the value shows "-0.2" and a tiny negative still shows 0.0."""
    whole = prefix + fmt + suffix
    m = STEP.fullmatch(fmt)
    if m is None:
        return whole
    half = Decimal(5).scaleb(-len(m.group(1) or "") - 1) * 1000 ** len(m.group(2)) / (100 if m.group(3) else 1)
    if not bool(((d > -float(half)) & (d < 0)).any()):
        return whole
    return f"[<=-{half.normalize():f}]{whole};{whole}"


UNIT_SIZE = {"000": 1e3, "thousand": 1e3, "mil": 1e6, "million": 1e6, "bil": 1e9, "billion": 1e9, "tril": 1e12, "trillion": 1e12,
             "quadrillion": 1e15}
UNIT_WORD = {1e3: "thousand", 1e6: "million", 1e9: "billion", 1e12: "trillion", 1e15: "quadrillion"}
TOP_UNIT = 1e15  # the largest unit is quadrillion: two significant figures beat a familiar unit (R57 round 7)
UNIT = re.compile(r"(?:\(|\bin\s+)([₩$€£¥])\s?(" + "|".join(UNIT_SIZE) + r")?s?(?=[\s),.;:]|$)", re.I)  # "(₩ Mil)", "in ₩ million"


def money_unit(c: Column) -> tuple[str, float] | None:
    """The currency a column's values are in and the size of its unit, as its name or else its note names them
    ("(₩ Mil)": ₩, 1e6; "in ₩ thousand"), or the "$" kind's dollars; None where neither names a currency."""
    for text in (c.name, c.note):
        m = UNIT.search(text)
        if m:
            return m.group(1), UNIT_SIZE[m.group(2).lower()] if m.group(2) else 1.0
    return ("$", 1.0) if c.format == "$" else None


def scaled_format(kind: str, unit: tuple[str, float], d: Floats, block: Floats | None = None) -> tuple[str, str] | None:
    """A money run's format and the unit its head names: the values (in unit) shown in the thousands, millions,
    billions, trillions or quadrillions of the currency that put the largest of block (the run's own values where none
    is given; a mean with its low and high ends share one) under 100, by the format's trailing commas, never by rounding a value,
    with the decimals that show the run's largest to two significant figures (`signed_zero` where a negative would
    show -0.0); None for a kind other than
    "number" or "$", or a unit that is no power of 1,000."""
    currency, size = unit
    steps = round(math.log10(size) / 3) if size > 0 else -1
    if kind not in ("number", "$") or steps < 0 or not math.isclose(size, 1000.0 ** steps):
        return None

    def largest_of(x: Floats) -> float:
        finite = np.abs(x[np.isfinite(x)])
        return float(finite.max()) if finite.size else 0.0

    top = largest_of(d if block is None else block)
    commas = 0
    while top / 1000 ** commas >= 99.5 and 1000.0 ** (steps + commas + 1) <= TOP_UNIT:  # 177 billion has three figures; 0.18 trillion two
        commas += 1
    shown = largest_of(d) / 1000 ** commas
    decimals = 0 if shown >= 9.95 or shown == 0 else 1 - math.floor(math.log10(shown))
    if decimals > MAX_DECIMALS:
        return None
    total = 1000.0 ** (steps + commas)
    fmt = number_format("$" if kind == "$" else "", decimals) + "," * commas
    return signed_zero(fmt, d), currency + (f" {UNIT_WORD[total]}" if total in UNIT_WORD else "")


PAREN = re.compile(r"\(([^()]*)\)")
SIZE_WORD = r"000|thousand|mil|million|bil|billion|tril|trillion|quadrillion"
NAMED = re.compile(r"(?<!\S)(?:(?P<cur>[₩$€£¥]|KRW|USD|EUR|GBP|JPY)\s?(?P<size>" + SIZE_WORD + r")?|(?P<bare>" + SIZE_WORD
                   + r"))s?(?=$|[\s,/])", re.I)  # inside brackets: "(₩ Bil)", "($000)", "(USD mil)", "(Mil)", "(₩/min)", "(2020 USD Bil)"


@dataclass(frozen=True)
class Named:
    """A unit a column's name or note gives in brackets: where it stands in the text, its currency as written (empty
    for a count) and its size."""
    start: int
    end: int
    currency: str
    size: float


def named_units(text: str) -> list[Named]:
    """Every unit text gives in brackets, in order, one a bracket."""
    out: list[Named] = []
    for p in PAREN.finditer(text):
        m = NAMED.search(p.group(1))
        if m is not None:
            word = m.group("size") or m.group("bare")
            out.append(Named(p.start(1) + m.start(), p.start(1) + m.end(), m.group("cur") or "", UNIT_SIZE[word.lower()] if word else 1.0))
    return out


@dataclass(frozen=True)
class Scale:
    """How a column tab's number or $ column shows its values: divided by 1,000 ** commas, after prefix (the "$"
    kind's sign); unit is the unit the values show in, in words ("₩ trillion", "million"), which the column's name
    gives (`column_label`), empty where the name needs no rewriting."""
    commas: int = 0
    prefix: str = ""
    unit: str = ""


def column_scale(c: Column, d: Floats, pct: tuple[float, float]) -> Scale:
    """The unit of a column tab's number or $ column (the owner, 2026-11-20: "lists numbers in million or billion or
    trillion when appropriate"): the unit its name, its note or its group's label gives in brackets ("(₩ Bil)", units where none),
    times the power of 1,000 that puts the largest number the column shows in one unit (the typical size of its draws,
    the mean of their absolute values; its low end, mean and high end at the percentiles pct; its parameters in rows 5
    to 9) under 100, so that each shows two significant figures with no rounding of a whole number, where that largest
    is 1,000 or more, to at most a quadrillion (a larger size shows whole in quadrillions). One unit for the whole column, so no cell reads in another. The cells carry no letter:
    the unit is named in words in the column's name (`column_label`), so 2,677,000 under "Korea Real GDP (₩ Bil)" shows
    2.7 under "Korea Real GDP (₩ quadrillion)", and 2,970,000,000 under "Orders" shows 3.0 under "Orders (billion)"."""
    sign = "$" if c.format == "$" else ""
    if c.format not in ("number", "$"):
        return Scale(0, sign)
    found = next((u[0] for u in (named_units(c.name), named_units(c.note), named_units(c.group or "")) if u), None)
    currency, size = (found.currency, found.size) if found is not None else ("", 1.0)
    finite = np.abs(d[np.isfinite(d)])
    shown = [float(finite.mean()) if finite.size else 0.0, *(abs(v) for v in summary(d, pct) if math.isfinite(v)),
             *(abs(float(v)) for k, v in c.params.items() if PARAM_ROW.get(k, 0) <= 9)]
    top = float(f"{max(shown):.1e}")  # rounded first, so 999.6 counts as 1,000
    commas = 0
    while top >= 1000 and top / 1000 ** commas >= 99.5 and size * 1000 ** (commas + 1) <= TOP_UNIT:
        commas += 1
    total = size * 1000 ** commas
    if total == 1:
        return Scale(0, sign)
    word = UNIT_WORD[total]
    return Scale(commas, sign, f"{currency} {word}" if currency else word)


def column_label(c: Column, d: Floats, pct: tuple[float, float]) -> tuple[str, str]:
    """A column's name and note as the sheet shows them: the unit its name gives rewritten to the unit its values show
    in, in words, with everything else kept ("Korea Real GDP (₩ Bil)" to "Korea Real GDP (₩ quadrillion)"), and the
    same unit in its note rewritten alike; a name that gives no unit gains it in brackets ("Orders (billion)"). A
    group's label, which may stand over columns shown in different units, is kept as the data file gives it."""
    unit = column_scale(c, d, pct).unit
    if not unit:
        return c.name, c.note
    names, notes = named_units(c.name), named_units(c.note)
    found = (names or notes or named_units(c.group or "") or [None])[0]

    def rewrite(text: str, at: list[Named]) -> str:
        for u in reversed(at):
            if found is not None and u.currency.lower() == found.currency.lower() and u.size == found.size:
                text = text[:u.start] + unit + text[u.end:]
        return text

    name = rewrite(c.name, names[:1]) if names else f"{c.name} ({unit})"
    return name, rewrite(c.note, notes)


def scaled_number(scale: Scale, d: Floats) -> str:
    """The format of a scaled column (`column_scale`) for the values d: two significant figures of their typical size
    in the unit, the sign before the number in every section (`signed_zero`)."""
    finite = np.abs(d[np.isfinite(d)])
    shown = float(f"{float(finite.mean()) / 1000 ** scale.commas if finite.size else 0.0:.1e}")
    decimals = 0 if shown <= 0 or shown >= 10 else min(MAX_DECIMALS, 1 - math.floor(math.log10(shown)))
    return signed_zero(number_format("", decimals) + "," * scale.commas, d, scale.prefix)


def model_format(c: Column, d: Floats, pct: tuple[float, float]) -> str:
    """The format of a kind's draws on a column tab: `draws_format`, in the column's scaled unit where it has one
    (`column_scale`); a tiny negative never shows -0 (`signed_zero`). Rows 12 to 14 take their own (`set_format`)."""
    scale = column_scale(c, d, pct)
    if scale.commas:
        return scaled_number(scale, d)
    fmt = draws_format(c.format, d)
    return fmt if c.format == "year" else signed_zero(fmt, d)


def set_format(c: Column, d: Floats, v: int | float, pct: tuple[float, float]) -> str:
    """The format of a kind's Set cell, or of its low, mean or high (rows 12 to 14): two significant figures of its
    own value, in its column's one unit (`column_scale`, from the column's draws d), which the name gives; a "%" near 0
    or 1 keeps its digits, as `draws_format`."""
    one = np.array([float(v)])
    scale = column_scale(c, d, pct)
    if scale.commas:
        return scaled_number(scale, one)
    return draws_format(c.format, one, (float(v),))


ADDRESS = re.compile(r"(?:(.*?)\s+)?(https?://\S+)", re.S)  # a text that ends in an address


@dataclass(frozen=True)
class Look:
    fill: str | None = None
    fmt: str | None = None
    font: Font = ARIAL10
    h: str | None = None
    v: str | None = None
    wrap: bool = False
    border: bool = False


def column_look(r: int, fill: str | None = None, fmt: str | None = None, colour: str = BLACK, bold: bool = False) -> Look:
    """A data column's cell in row r (a draw row past 15), bordered from row 3 down."""
    h, v, wrap = LOOK.get(r, DRAW_LOOK)
    return Look(fill, fmt, (FONT, SIZE, bold, colour), h, v, wrap, r >= 3)


def char_px(size: float, bold: bool = False) -> float:
    return CHAR_PX * size / SIZE * (BOLD_PX if bold else 1)


def lines_of(text: str, px: float, size: float, bold: bool = False) -> int:
    """The lines a text wraps to in a column px wide at a size, estimated from its characters."""
    return max(1, math.ceil(len(text) * char_px(size, bold) / max(px - CELL_PAD_PX, 1)))


def row_px(text: str, px: float, size: float, wrap: bool, bold: bool = False) -> float:
    """The height in px a row needs for a text: its lines (one if it does not wrap) x the line, plus the padding."""
    line = LINE_PX if size <= SIZE else size * 4 / 3
    return max(MIN_ROW_PX, (lines_of(text, px, size, bold) if wrap else 1) * line + ROW_PAD_PX)


CARRIED = re.compile(r"(?:'((?:[^']|'')+)'|([A-Za-z_][A-Za-z0-9_.]*))!\$?[A-Z]{1,3}\$?\d+")  # Tab!$C$13, 'A tab'!C13
LOOKUPS = ("INDEX(", "VLOOKUP(", "HLOOKUP(", "XLOOKUP(", "LOOKUP(")


def formula_colour(formula: str, here: str) -> str:
    """The font colour of a formula on tab here: GREEN where its value is another tab's cell carried over unchanged,
    a plain reference (=Globals!C13) or a lookup whose outermost call reads another tab; else BLACK, for a formula that
    computes whatever tab its arguments sit on (the owner, 2026-11-20: "the 5th and 95th percentile values should not
    be green just because the range choice came from another sheet"; the financial-modelling green for a link)."""
    f = formula.removeprefix("=")

    def other(m: re.Match[str]) -> bool:
        return (m.group(2) if m.group(1) is None else m.group(1).replace("''", "'")) != here

    m = CARRIED.fullmatch(f)
    if m is not None:
        return GREEN if other(m) else BLACK
    return GREEN if f.startswith(LOOKUPS) and any(other(x) for x in CARRIED.finditer(f)) else BLACK


KEY_MARK = "{colour:"  # a guide cell written in a kind's colour, "{colour:input}Input": the colour key's samples
KEY_COLOURS = {"input": INPUT_BLUE, "formula": BLACK, "cross": GREEN, "link": LINK_BLUE}


def marked(text: str) -> tuple[str, str]:
    """A text tab cell's mark ("heading", "subhead", "bold", a KEY_COLOURS kind or "") and its text without the mark.
    A text that begins with a backslash is plain, the backslash dropped, so "\\# of households" shows "# of households"."""
    if text.startswith("\\"):
        return "", text[1:]
    if text.startswith("# "):
        return "heading", text[2:]
    if text.startswith("## "):
        return "subhead", text[3:]
    if len(text) > 4 and text.startswith("**") and text.endswith("**"):
        return "bold", text[2:-2]
    m = re.match(re.escape(KEY_MARK) + r"(\w+)\}", text)
    if m and m.group(1) in KEY_COLOURS:
        return m.group(1), text[m.end():]
    return "", text


def link(text: str) -> tuple[str, str | None]:
    """The text a cell shows and the address it opens, if the text ends in one; a bare address shows itself."""
    m = ADDRESS.fullmatch(text)
    return (text, None) if m is None else (m.group(1) or m.group(2), m.group(2))


def linked(text: str) -> CellValue:
    """The cell for a text: a HYPERLINK formula where it ends in an address, its pieces kept under Excel's 255
    characters a string, else the text itself."""
    shown, url = link(text)
    if url is None:
        return text or None

    def quote(s: str) -> str:
        return '"' + s.replace('"', '""') + '"'

    return f"=HYPERLINK({quote(url)},{'&'.join(quote(shown[i:i + 120]) for i in range(0, len(shown), 120))})"


def quoted(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


def tab_named(tab: str, before: str = "", after: str = "") -> CellValue:
    """A label naming a tab (before, the tab's name, after) as a formula that follows the tab's renaming: CELL quotes
    every tab name, so its quotes are removed (tested in Google, 2026-11-20). A name holding an apostrophe would lose it
    there, and stays text."""
    if "'" in tab:
        return before + tab + after
    name = f'SUBSTITUTE(REGEXREPLACE(CELL("address",{sheet_name(tab)}!A1),"!.*$",""),"\'","")'
    return Label("=" + (quoted(before) + "&" if before else "") + name + ("&" + quoted(after) if after else ""), before + tab + after)


def labelled(text: str, tabs: list[str], cites: set[str] | frozenset[str] = frozenset()) -> CellValue:
    """A cell's text: a label of at most LABEL_CHARS that names a tab, as `tab_named`: the tab's name alone, or
    followed by "," or ":" where the cells the label heads (cites, the tabs their formulas read) read that tab, so a
    head such as "Cost: mean" over other tabs' columns stays text; else as `linked`."""
    if len(text) <= LABEL_CHARS and link(text)[1] is None:
        for t in sorted(tabs, key=len, reverse=True):
            if text == t or (text.startswith(t) and text[len(t)] in ",:" and t in cites):
                return tab_named(t, after=text[len(t):])
    return linked(text)


def shown_text(value: CellValue) -> str | None:
    """The text a cell shows where it is known before Google computes: a text, a label's, a link's words."""
    if isinstance(value, Label):
        return value.text
    if isinstance(value, str) and value.startswith("=HYPERLINK("):
        return "".join(x.replace('""', '"') for x in re.findall(r'"((?:[^"]|"")*)"', value)[1:])
    return value if isinstance(value, str) and not value.startswith("=") else None


def sheet_name(tab: str) -> str:
    """A tab's name as a formula cites it: bare where Sheets needs no quotes (Globals), quoted otherwise ('Side effects')."""
    bare = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tab) and not re.fullmatch(r"[A-Z]{1,3}\d+|R\d*C?\d*|C\d*|TRUE|FALSE", tab, re.I)
    return tab if bare else "'" + tab.replace("'", "''") + "'"


# The sensitivity tab: per output a ranked list, live, and below the lists every input ------------------------------

SENS_RANKS = 15
SENS_HEADER = ("Rank", "Input", "Tab", "r", "Rank r", "Change, 5th to 95th", "Key")  # a block's columns, then a gap
SENS_WIDTHS = (50, 220, 90, 80, 80, 110, 70, 20)  # px, a block's columns and its gap; a rank column wide enough for the line, 0.13; r and rank r wide enough for the heads above them (register 3.3)
SENS_LINE, SENS_NAME, SENS_STATS, SENS_TOP = 2, 4, 5, 7  # rows: the noise line; output's name; its mean and interval; rank 1
SENS_R = "[<=-0.005]0.00;0.00"  # r, rank r, the key and the line: two significant figures below 1 (register 2.2), and a
# tiny negative r shows 0.00, never "-0.00" (the guard of `signed_zero`)
SENS_MOVED = "moved: regenerate"
SENS_TITLE = "Which inputs move each result most (how each number is found: the Guide)"  # B1, the tab's title
SENS_LINE_TEXT = "Noise line: a key below it is likely chance, and its rank shows blank."  # B2, beside the line
GUIDE_SENSITIVITY = (  # the guide's rows under the sensitivity tab's own, in "The tabs, left to right"
    "Which inputs move each result most. r is the straight-line correlation of an input with the output across the "
    "draws; rank r correlates their ranks, so one huge draw cannot dominate it. Each output's inputs are ranked by the "
    "key, the larger of |r| and |rank r|. The change is the output's straight-line change as the input moves from its "
    "5th to its 95th percentile, SLOPE x (95th - 5th), in the output's units: its sign says which way the output moves. "
    "Computed live from the draws.",
    "Noise line, smaller r is likely chance: 4/SQRT(draws). It is family-wise: the chance that some input "
    "unconnected to the output crosses it by luck is a few per cent, more with many inputs or a fat-tailed output "
    "(about 2% to 11% in the cases measured). A rank whose key is below the line shows blank. Below the lists, every "
    "input, in the tabs' order.",
    "Rank r reads each input's ranks from the block at the right, written when the sheet was generated: they hold under "
    "any change to an input's distribution or parameters, since each input's draws rise with its random number. Moving "
    "a tab or inserting a column changes the random numbers, and rank r then shows \"" + SENS_MOVED + "\" in that "
    "input's row alone.",
)
SensCell = tuple[CellValue, Scalar, float, Look]  # the sheet's value or formula, the twin's value, its scale, its look


def correl(a: Floats, b: Floats) -> float | None:
    """CORREL as Sheets computes it; None where it errs (a non-finite value, or a constant range)."""
    if not (np.isfinite(a).all() and np.isfinite(b).all()) or np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def sensitivity_cells(tab: Tab, tabs: list[Tab], computed: dict[str, dict[str, Floats]], pct: tuple[float, float]) -> dict[tuple[int, int], SensCell]:
    """A sensitivity tab's cells: its title and the noise line, 4/SQRT(COUNT(draws)), in rows 1 and 2; one block per
    output, side by side, with the output's name, mean and interval, then ranks 1 to SENS_RANKS by the key, MAX(|r|,
    |rank r|) (LARGE, the first MATCH on a tie), a rank whose key is below the line blank, rank and key too; below them
    every input with each output's r, rank r, change and key. At the right, each output's ranks (RANK.AVG, ascending)
    and each input's ranks as static values, from its random numbers, which its draws rise with whatever its kind and
    parameters; each rank r is guarded by the input's column and tab position at generation, and a key whose rank r
    shows the guard is blank, so the other inputs still rank. A label naming a tab follows its renaming (`tab_named`)."""
    letters = {(t.name, c.id): c.letter for t in tabs for c in t.columns}
    columns = {(t.name, c.id): c for t in tabs for c in t.columns}
    inputs = [(t, i, c) for t in tabs for i, c in enumerate(t.columns) if c.kind in REQUIRED and c.kind != "constant"]
    named = {(t.name, c.id): column_label(c, computed[t.name][c.id], pct)[0] or c.id for t, _, c in inputs}  # as its column shows it
    first = SENS_TOP + SENS_RANKS + 3  # a blank row, a heading and a header row after the lists
    last = first + len(inputs) - 1
    helper = 1 + len(SENS_WIDTHS) * len(tab.outputs)  # the first of the output ranks' columns, then the inputs'
    out: dict[tuple[int, int], SensCell] = {}

    def text(r: int, c: int, s: str, wrap: bool = True, h: str = "left", value: CellValue = None) -> None:
        out[(r, c)] = (s if value is None else value, s, 0.0, Look(h=h, v="top", wrap=wrap))

    def number(r: int, c: int, formula: str, v: float | str | None, scale: float, fmt: str | None) -> None:
        out[(r, c)] = ("=" + formula, "" if v is None else v, scale, Look(fmt=fmt, h="right", v="top"))

    def draws(key: tuple[str, str]) -> str:
        x = letters[key]
        return f"{sheet_name(key[0])}!${x}${FIRST}:${x}${LAST}"

    def kind_of(key: tuple[str, str]) -> str:
        return columns[key].format

    def whole(col: int) -> str:
        return f"${letter(col)}${first}:${letter(col)}${last}"

    out[(1, 2)] = (SENS_TITLE, SENS_TITLE, 0.0, Look(font=HEADING, h="left", v="top"))
    text(SENS_LINE, 2, SENS_LINE_TEXT, wrap=False)
    y0 = computed[tab.outputs[0][0]][tab.outputs[0][1]]
    line = 4 / math.sqrt(int(np.isfinite(y0).sum()))
    line_ref = f"$A${SENS_LINE}"
    number(SENS_LINE, 1, f"4/SQRT(COUNT({draws(tab.outputs[0])}))", line, 1.0, SENS_R)
    text(first - 2, 2, "Every input", wrap=False)
    text(first - 1, 2, SENS_HEADER[1])
    text(first - 1, 3, SENS_HEADER[2])
    xs = [computed[t.name][c.id] for t, _, c in inputs]
    static: list[Floats] = []
    for k, (t, i, c) in enumerate(inputs):
        r, col = first + k, helper + len(tab.outputs) + k
        text(r, 2, named[(t.name, c.id)])
        text(r, 3, t.name, value=tab_named(t.name))
        ranks = np.asarray(stats.rankdata(sheet_uniforms(t.position, i + 2, DRAWS, FIRST)), dtype=np.float64)
        static.append(ranks)
        text(FIRST - 1, col, f"Ranks: {t.name}: {named[(t.name, c.id)]}", value=tab_named(t.name, "Ranks: ", f": {named[(t.name, c.id)]}"))
        for n in range(DRAWS):  # a loop over the draws to write each static cell; nothing is computed in it
            out[(FIRST + n, col)] = (float(ranks[n]), float(ranks[n]), float(DRAWS), Look())
    for j, o in enumerate(tab.outputs):
        b = 1 + len(SENS_WIDTHS) * j  # the block's rank column
        rc, rrc, chc, kc = b + 3, b + 4, b + 5, b + 6
        y = computed[o[0]][o[1]]
        finite_y = np.abs(y[np.isfinite(y)])
        scale = float(finite_y.max()) if finite_y.size else 0.0
        fmt = run_format(kind_of(o), y)
        low, mean, high = summary(y, pct)
        name = columns[o].name or o[1]
        unit = money_unit(columns[o])
        block = np.array([low, mean, high])
        three = scaled_format(kind_of(o), unit, block) if unit is not None else None
        if three is not None and unit is not None and (m := UNIT.search(name)) is not None:  # the title names the unit shown
            name = name[:m.start(1)] + three[1] + name[m.end():]
        text(SENS_NAME, b + 1, f"{o[0]}: {name}", value=tab_named(o[0], after=f": {name}"))
        for k, (label, row, v) in enumerate((("Mean", MEAN, mean), ("Low end", LOW, low), ("High end", HIGH, high))):
            own = scaled_format(kind_of(o), unit, np.array([v]), block) if three is not None and unit is not None else None  # three's unit, its own figures
            text(SENS_NAME, b + 3 + k, label if three is None else f"{label}, {three[1]}", h="right")
            number(SENS_STATS, b + 3 + k, f"{sheet_name(o[0])}!{letters[o]}{row}", v, scale, fmt if own is None else own[0])
        oc = helper + j  # the output's ranks, RANK.AVG ascending, one a draw row
        text(FIRST - 1, oc, f"Ranks: {o[0]}: {name}", value=tab_named(o[0], "Ranks: ", f": {name}"))
        ry = np.asarray(stats.rankdata(y), dtype=np.float64)
        x_o = letters[o]
        for n in range(DRAWS):  # a loop over the draws to write each RANK.AVG cell; its value is computed above, at once
            number(FIRST + n, oc, f"RANK.AVG({sheet_name(o[0])}!{x_o}{FIRST + n},{draws(o)},1)", float(ry[n]), float(DRAWS), None)
        out_ranks = f"${letter(oc)}${FIRST}:${letter(oc)}${LAST}"
        found_stats: list[tuple[float | None, float | None, float | None]] = []
        for x, sr in zip(xs, static):  # a loop over the inputs; each statistic is over all the draws at once
            rv = correl(x, y)
            rrv = None if rv is None else correl(sr, ry)
            change = None
            if rv is not None:
                dx, dy = x - x.mean(), y - y.mean()
                change = float((dx * dy).sum() / (dx * dx).sum()) * float(np.percentile(x, 95) - np.percentile(x, 5))
            found_stats.append((rv, rrv, change))
        keys = [None if rv is None or rrv is None else max(abs(rv), abs(rrv)) for rv, rrv, _ in found_stats]
        ranked = sorted((v for v in keys if v is not None), reverse=True)

        def change_format(changes: list[float | None]) -> tuple[str | None, str]:
            """One format for a list's change column, at the changes' own size, scaled to a unit its head names."""
            d = np.array([ch for ch in changes if ch is not None and math.isfinite(ch)], dtype=np.float64)
            got = scaled_format(kind_of(o), unit, d) if unit is not None and d.size else None
            if got is not None:
                return got[0], f"{SENS_HEADER[5]}, {got[1]}"
            return run_format(kind_of(o), d) if d.size else fmt, SENS_HEADER[5]

        ch_fmt, ch_head = change_format([ch for _, _, ch in found_stats])
        top_fmt, top_head = change_format([found_stats[keys.index(kv)][2] for kv in ranked[:SENS_RANKS] if kv >= line])
        for k, label in enumerate(SENS_HEADER):
            h = "center" if k == 0 else "right" if k >= 3 else "left"
            text(SENS_TOP - 1, b + k, top_head if k == 5 else label, h=h)
            if k >= 3:
                text(first - 1, b + k, ch_head if k == 5 else label, h=h)
        for k, ((t, _, c), (rv, rrv, change)) in enumerate(zip(inputs, found_stats)):
            r, xr, key = first + k, draws((t.name, c.id)), (t.name, c.id)
            first_draw = f"{sheet_name(t.name)}!${letters[key]}${FIRST}"
            sc = letter(helper + len(tab.outputs) + k)
            kv = keys[k]
            ref_r, ref_rr = f"{letter(rc)}{r}", f"{letter(rrc)}{r}"
            number(r, rc, f'IFERROR(CORREL({draws(o)},{xr}),"")', rv, 1.0, SENS_R)
            number(r, rrc, f"IF(AND(COLUMN({first_draw})={colnum(letters[key])},SHEET({first_draw})={t.position}),"
                   f'IF({ref_r}="","",CORREL(${sc}${FIRST}:${sc}${LAST},{out_ranks})),"{SENS_MOVED}")', rrv, 1.0, SENS_R)
            number(r, chc, f'IF({ref_r}="","",SLOPE({draws(o)},{xr})*(PERCENTILE({xr},0.95)-PERCENTILE({xr},0.05)))', change, scale, ch_fmt)
            number(r, kc, f'IF({ref_r}="","",IFERROR(MAX(ABS({ref_r}),ABS({ref_rr})),""))', kv, 1.0, SENS_R)
        for k in range(SENS_RANKS):
            r = SENS_TOP + k
            kref = f"${letter(kc)}{r}"
            kv = ranked[k] if k < len(ranked) else None
            shown = kv is not None and kv >= line
            out[(r, b)] = (f'=IF({kref}="","",{k + 1})', float(k + 1) if shown else "", 0.0, Look(h="center", v="top"))
            large = f"LARGE({whole(kc)},{k + 1})"
            number(r, kc, f'IF({k + 1}>COUNT({whole(kc)}),"",IF({large}<{line_ref},"",{large}))', kv if shown else None, 1.0, SENS_R)
            i = keys.index(kv) if shown else -1  # the first match, as MATCH finds it
            match = f"MATCH({kref},{whole(kc)},0)"

            def pick(col: int) -> str:
                return f'IF({kref}="","",INDEX({whole(col)},{match}))'

            t, _, c = inputs[i] if shown else (None, 0, None)
            for col, v in ((b + 1, None if c is None or t is None else named[(t.name, c.id)]), (b + 2, None if t is None else t.name)):
                out[(r, col)] = ("=" + pick(2 if col == b + 1 else 3), "" if v is None else v, 0.0, Look(font=ARIAL10, h="left", v="top", wrap=True))
            row_of = first + i
            for col, f in ((rc, SENS_R), (rrc, SENS_R), (chc, top_fmt)):
                v = out[(row_of, col)][1] if shown else None
                number(r, col, pick(col), v, scale if col == chc else 1.0, f)
    return out


def sensitivity_values(tab: Tab, tabs: list[Tab], computed: dict[str, dict[str, Floats]], pct: tuple[float, float]) -> dict[tuple[int, int], tuple[Scalar, float]]:
    """Each cell of a sensitivity tab as the twin computes it, with its scale, as `table_values` gives a table's."""
    return {k: (v[1], v[2]) for k, v in sensitivity_cells(tab, tabs, computed, pct).items()}


def draw_formula(c: Column, letters: dict[tuple[str, str], str], here: str, labels: int = 0) -> str:
    """The column's formula in its first draw row on tab here, without the leading "="; an input with label columns
    before it seeds its draws by its place among the data columns, COLUMN() less the labels, as Python does."""
    if c.formula is None:
        generator = GENERATOR[1:].replace("C$", f"{c.letter}$")
        return generator.replace("COLUMN()", f"(COLUMN()-{labels})") if labels else generator
    return write(c.formula, in_sheet(letters, here))[0]


def shown_formula(c: Column, letters: dict[tuple[str, str], str], here: str) -> str:
    """Row 3 of a calculation as Google shows it: the draw formula without its row numbers."""
    return re.sub(rf"([A-Z]+){FIRST}\b", r"\1", "=" + draw_formula(c, letters, here))


class Styles:
    """The workbook's cell styles, each a Look, numbered as first used."""

    def __init__(self) -> None:
        self.ids: dict[Look, int] = {Look(): 0}

    def __call__(self, look: Look) -> int:
        return self.ids.setdefault(look, len(self.ids))

    def xml(self) -> str:
        fills = list(dict.fromkeys(k.fill for k in self.ids if k.fill is not None))
        formats = list(dict.fromkeys(k.fmt for k in self.ids if k.fmt is not None))
        for f in formats:  # register 2.2: Sheets shows a negative's minus itself in a section with a condition (`signed_zero`)
            if any(re.match(r"\[[<>=]+-?[\d.]+\]", sec) and "-" in re.sub(r'"[^"]*"|\\.', "", sec[sec.index("]") + 1:])
                   for sec in f.split(";")):
                raise Fault(f"number format {f!r} writes a '-' in a section with a condition, where Sheets shows its own (\"--0.2\")")
        fonts = list(dict.fromkeys(k.font for k in self.ids))
        xfs = ""
        for k in self.ids:
            fill_id = 0 if k.fill is None else fills.index(k.fill) + 2
            fmt_id = 0 if k.fmt is None else formats.index(k.fmt) + 164
            align = "".join(f' {a}="{v}"' for a, v in (("horizontal", k.h), ("vertical", k.v), ("wrapText", "1" if k.wrap else None)) if v)
            xfs += (f'<xf numFmtId="{fmt_id}" fontId="{fonts.index(k.font)}" fillId="{fill_id}" borderId="{int(k.border)}" xfId="0"'
                    + ' applyFont="1"' + (' applyFill="1"' if k.fill else "") + (' applyNumberFormat="1"' if k.fmt else "")
                    + (' applyBorder="1"' if k.border else "")
                    + (f' applyAlignment="1"><alignment{align}/></xf>' if align else "/>"))
        side = "".join(f'<{s} style="thin"><color rgb="FF{LINE}"/></{s}>' for s in ("left", "right", "top", "bottom"))
        return (XML + f'<styleSheet xmlns="{NS}">'
                + (f'<numFmts count="{len(formats)}">' + "".join(f'<numFmt numFmtId="{164 + i}" formatCode="{escape(f, {chr(34): "&quot;"})}"/>'
                                                               for i, f in enumerate(formats)) + "</numFmts>" if formats else "")
                + f'<fonts count="{len(fonts)}">' + "".join(
                    "<font>" + ("<b/>" if bold else "") + ("<u/>" if colour == LINK_BLUE else "") + f'<sz val="{size}"/>'
                    + (f'<color rgb="FF{colour}"/>' if colour != BLACK else "")
                    + f'<name val="{name}"/></font>' for name, size, bold, colour in fonts) + "</fonts>"
                + f'<fills count="{len(fills) + 2}"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
                + "".join(f'<fill><patternFill patternType="solid"><fgColor rgb="FF{f}"/></patternFill></fill>' for f in fills) + "</fills>"
                + f'<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border>{side}<diagonal/></border></borders>'
                + '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                + f'<cellXfs count="{len(self.ids)}">{xfs}</cellXfs></styleSheet>')


XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def cell(r: int, c: int, value: CellValue, style: int) -> str:
    ref, s = f"{letter(c)}{r}", f' s="{style}"' if style else ""
    if value is None:
        return f'<c r="{ref}"{s}/>'
    if isinstance(value, Label):
        return f'<c r="{ref}"{s} t="str"><f>{escape(value.formula[1:])}</f><v>{escape(value.text)}</v></c>'
    if isinstance(value, str) and value.startswith("="):
        return f'<c r="{ref}"{s}><f>{escape(value[1:])}</f></c>'
    if isinstance(value, str):
        return f'<c r="{ref}"{s} t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>'
    return f'<c r="{ref}"{s}><v>{value!r}</v></c>'


def text_sheet(tab: Tab, styles: Styles, letters: dict[tuple[str, str], str], extra: dict[tuple[int, int], SensCell] | None,
               shown: tuple[dict[tuple[int, int], str | None], dict[tuple[int, int], str]] | None, tab_names: list[str]) -> tuple[str, dict[int, str]]:
    """The sheet XML of a guide, text, table or sensitivity tab. Its cells are Arial 10 and black, a title alone bold
    and larger (a guide's or text tab's heading, `# `, and a table's A1), a link in LINK_BLUE, underlined, another
    tab's cell carried over in GREEN (`formula_colour`), the guide's setting in INPUT_BLUE and the colour key's samples
    in their kind's colour. A text column the data file gives no
    width is widened to fit a text that would wrap past MAX_LINES (at most TEXT_MAX_PX), or in a table past
    NARROW_LINES in a column under NARROW_PX, never merged; every row is as tall as its tallest text (`row_px`). A head
    over a number is aligned as the number, to the right. A label naming a tab, in a table, a sensitivity tab or the
    guide's column A, follows the tab's renaming (`labelled`); every tab but this one, whose CELL("address") would name
    no tab. shown is a table's number formats and its heads that name a scaled unit (`table_shown`). It returns the
    XML and the tab's header notes by column (`header_cells`)."""
    names = [t for t in tab_names if t != tab.name]
    ink = INK if tab.kind == "guide" else BLACK  # the guide's text as his template's Readme (INK)
    fonts: dict[str, Font] = {"heading": HEADING, "subhead": (*SUBHEAD[:3], ink), "bold": (FONT, SIZE, False, ink), "": (FONT, SIZE, False, ink),
                              **{k: (FONT, SIZE, False, colour) for k, colour in KEY_COLOURS.items()}}

    def font_of(value: CellValue, font: Font) -> Font:
        return LINK_FONT if isinstance(value, str) and value.startswith("=HYPERLINK(") else font

    entries: dict[tuple[int, int], tuple[CellValue, Look]] = {}
    for r, row in enumerate(tab.rows or [], start=1):
        for c, v in enumerate(row, start=1):
            if v == SETTING and tab.interval is not None:
                entries[(r, c)] = (tab.interval, Look(YELLOW, "0%", INPUT_FONT))
            elif v:
                mark, text = marked(v)
                wrap = mark not in ("heading", "subhead") and link(text)[1] is None
                value = labelled(text, names) if tab.kind == "guide" and c == 1 and mark in ("", "bold") else linked(text)
                formula = isinstance(value, Label) or (isinstance(value, str) and value.startswith("="))
                font = (*fonts[mark][:3], BLACK) if formula else fonts[mark]  # a formula (a label) is black
                entries[(r, c)] = (value, Look(font=font_of(value, font), h="left", v="top", wrap=wrap))
    numbers, heads = shown or ({}, {})
    cites: dict[tuple[str, int], set[str]] = {}  # the tabs each row's and each column's formulas read, for its labels
    for (r, c), v in tab.cells.items():
        if not isinstance(v, (str, int, float)):
            for key in (("row", r), ("column", c)):
                cites.setdefault(key, set()).update(t for t, _ in refs(v))
    for (r, c), v in sorted(tab.cells.items()):
        if (r, c) in numbers:
            entries[(r, c)] = (v if isinstance(v, float) else "=" + write(cast(Node, v), in_sheet(letters, tab.name))[0],
                               Look(fmt=numbers[(r, c)], h="right"))
            continue
        if isinstance(v, str):
            value = labelled(heads.get((r, c), v), names, cites.get(("row", r), set()) | cites.get(("column", c), set()))
        else:
            value = v if isinstance(v, (int, float)) else "=" + write(v, in_sheet(letters, tab.name))[0]
        font = HEADING if (r, c) == (1, 1) and isinstance(v, str) else font_of(value, ARIAL10)
        entries[(r, c)] = (value, Look(font=font, h="right" if (r + 1, c) in numbers else "left", wrap=True))
    for key, (v, _, _, look) in (extra or {}).items():
        entries[key] = (v, look)
    for key, (value, look) in entries.items():  # another tab's cell carried over is green (`formula_colour`)
        if isinstance(value, str) and value.startswith("=") and look.font[3] == BLACK and formula_colour(value, tab.name) == GREEN:
            entries[key] = (value, replace(look, font=(*look.font[:3], GREEN)))
    px: list[float] = list(SENS_WIDTHS * len(tab.outputs) if tab.kind == "sensitivity" else tab.widths)
    if tab.kind in ("text", "table") and not tab.widths:  # widen a column, never merge (notes/sheet_layout_review.md 4.4)
        px = list(TEXT_WIDTHS if tab.kind == "text" else ())
        px += [TABLE_PX] * (max((c for _, c in entries), default=0) - len(px))
        for (_, c), (value, look) in entries.items():
            text = shown_text(value)
            lines = lines_of(text, px[c - 1], look.font[1], look.font[2]) if text else 0
            if lines > MAX_LINES or (tab.kind == "table" and look.wrap and px[c - 1] < NARROW_PX and lines >= NARROW_LINES):
                px[c - 1] = min(TEXT_MAX_PX, max(px[c - 1], len(cast(str, text)) * char_px(look.font[1], look.font[2]) + CELL_PAD_PX))
    height: dict[int, float] = {}
    for (r, c), (value, look) in entries.items():  # a loop over the written cells, a sensitivity tab's static rank cells among them
        text = shown_text(value)
        need = row_px(text or "", px[c - 1] if c <= len(px) else TABLE_PX, look.font[1], look.wrap and bool(text), look.font[2])
        height[r] = max(height.get(r, 0.0), need)
    rows: dict[int, list[str]] = {}
    for (r, c), (value, look) in sorted(entries.items()):
        rows.setdefault(r, []).append(cell(r, c, value, styles(look)))
    data = "".join(f'<row r="{r}" ht="{math.ceil(height[r]) * 0.75:g}" customHeight="1">' + "".join(cs) + "</row>" for r, cs in rows.items())
    widths = "".join(f'<col min="{i}" max="{i}" width="{w / 7:.2f}" customWidth="1"/>' for i, w in enumerate(px, 1))
    notes = header_cells(tab, set(range(1, max(len(px), max((c for _, c in entries), default=0)) + 1)))
    return XML + f'<worksheet xmlns="{NS}">' + (f"<cols>{widths}</cols>" if widths else "") + f"<sheetData>{data}</sheetData></worksheet>", notes


def worksheet(tab: Tab, styles: Styles, setting: str, values: dict[str, Floats], letters: dict[tuple[str, str], str],
              extra: dict[tuple[int, int], SensCell] | None = None, shown: tuple[dict[tuple[int, int], str | None], dict[tuple[int, int], str]] | None = None,
              *, tab_names: list[str], pct: tuple[float, float]) -> tuple[str, dict[int, str]]:
    """One tab's sheet XML; setting is the cell that holds the interval's share, as a formula cites it, values the
    tab's columns' draws in Python, which set a kind of number's format, letters every column's and method's by (tab,
    id), pct the interval's percentiles, extra a sensitivity tab's cells (`sensitivity_cells`), and shown a table's number format for each cell whose
    value is a number (`table_shown`). A tab without columns is `text_sheet`'s. It returns the XML and the tab's header
    notes by column (`header_cells`)."""
    if tab.about is None:
        return text_sheet(tab, styles, letters, extra, shown, tab_names)
    rows: dict[int, list[str]] = {}

    def put(r: int, c: int, value: CellValue, style: int = 0) -> None:
        rows.setdefault(r, []).append(cell(r, c, value, style))

    low, high = f"(1-{setting})/2", f"(1+{setting})/2"
    draws = '="Draws: "&ROUND({}*100,1)&"%"'
    column_a: dict[int, CellValue] = {**LABELS, 1: tab.about or None, LOW: draws.format(low), HIGH: draws.format(high)}
    for r in range(1, 16):
        fill = YELLOW if 4 <= r <= 11 else BLUE if LOW <= r <= HIGH else None
        font: Font = (FONT, MODEL_TITLE_SIZE, True, BLACK) if r == 1 else (FONT, SIZE, r != 2, BLACK)
        put(r, 1, column_a[r], styles(Look(fill, None, font, "left", LOOK[r][1], r <= 3, r >= 4)))
    for r in range(FIRST, LAST + 1):
        put(r, 1, r - FIRST + 1, styles(column_look(r)))
    blocks = 0
    have = {1}  # the columns written: A, the label columns and the data columns
    for i, c in enumerate(tab.columns):
        n, x, is_input = colnum(c.letter), c.letter, c.kind in REQUIRED
        kind = c.format in KINDS_OF_NUMBER
        fmt = model_format(c, values[c.id], pct) if kind else c.format
        if c.group is not None and (i == 0 or c.group != tab.columns[i - 1].group):  # a block's label column
            blocks += 1
            have.add(n - 1)
            put(1, n - 1, c.group, styles(column_look(1, LABEL, bold=True)))
            method = next((m for m in tab.methods if m.group == c.group), None)
            for r in range(3, LAST + 1):
                if method is not None and r == 4:
                    put(r, n - 1, "Credence", styles(column_look(r, YELLOW, bold=True)))
                elif method is not None and r == 5:
                    put(r, n - 1, method.credence, styles(column_look(r, YELLOW, colour=INPUT_BLUE)))
                else:
                    put(r, n - 1, None, styles(column_look(r)))
        have.add(n)
        tint = None if c.group is None else TINTS[(blocks - 1) % len(TINTS)]
        name, note = column_label(c, values[c.id], pct)
        put(1, n, name or None, styles(column_look(1, tint, bold=c.result)))
        put(2, n, note or None, styles(column_look(2)))
        row3 = linked(c.citation) if is_input else f'=REGEXREPLACE(FORMULATEXT({x}{FIRST}),"([A-Z]+){FIRST}\\b","$1")'
        put(3, n, row3, styles(column_look(3, colour=LINK_BLUE if isinstance(row3, str) and row3.startswith("=HYPERLINK(") else BLACK)))
        head: list[CellValue] = [c.kind, *(c.params.get(k) for k in PARAM_ROW)] if is_input else [None] * 8
        for r, v in enumerate(head, start=4):
            set_fmt = set_format(c, values[c.id], v, pct) if kind and isinstance(v, (int, float)) else fmt
            if r in SHAPE_ROWS and isinstance(v, (int, float)):  # alpha and beta: plain numbers, two significant figures
                set_fmt = draws_format("number", np.array([float(v)]), (float(v),))
            put(r, n, v, styles(column_look(r, YELLOW if is_input else GREY, set_fmt if r in FORMATTED | SHAPE_ROWS else None, INPUT_BLUE if is_input else BLACK)))
        stats = [set_format(c, values[c.id], v, pct) if kind else fmt for v in summary(values[c.id], pct)]  # each its own two figures
        put(LOW, n, f"=PERCENTILE({x}${FIRST}:{x}${LAST},{low})", styles(column_look(LOW, BLUE, stats[0])))
        put(MEAN, n, f"=AVERAGE({x}${FIRST}:{x}${LAST})", styles(column_look(MEAN, BLUE, stats[1])))
        put(HIGH, n, f"=PERCENTILE({x}${FIRST}:{x}${LAST},{high})", styles(column_look(HIGH, BLUE, stats[2])))
        span = f"{x}{FIRST}:{x}{LAST}"
        put(15, n, f'=LET(lo,MIN({span}),w,(MAX({span})-lo)/20,SPARKLINE(FREQUENCY({span},SEQUENCE(19,1,lo+w,w)),{{"charttype","column";"color","#4285F4"}}))',
            styles(column_look(15)))
        first = draw_formula(c, letters, tab.name, n - i - 2)
        s = f' s="{styles(column_look(FIRST, None, fmt, formula_colour(first, tab.name)))}"'
        rows.setdefault(FIRST, []).append(f'<c r="{x}{FIRST}"{s}><f t="shared" ref="{span}" si="{n}">{escape(first)}</f></c>')
        for r in range(FIRST + 1, LAST + 1):
            rows.setdefault(r, []).append(f'<c r="{x}{r}"{s}><f t="shared" si="{n}"/></c>')
    last = colnum(tab.columns[-1].letter) if tab.columns else 1
    for n in range(last + 1, last + SPARE + 1):  # empty, with a calculation's fills and the borders
        for r in range(3, LAST + 1):
            put(r, n, None, styles(column_look(r, GREY if 4 <= r <= 11 else BLUE if LOW <= r <= HIGH else None)))
    data = "".join(f'<row r="{r}" ht="{HEIGHT.get(r, DRAW_HEIGHT) * 0.75:g}" customHeight="1">' + "".join(cs) + "</row>"
                   for r, cs in sorted(rows.items()))
    inputs = " ".join(f"{c.letter}4" for c in tab.columns if c.kind in REQUIRED)
    kinds = escape('"' + ",".join(KINDS_LIST) + '"')
    validation = (f'<dataValidations count="1"><dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="{inputs}">'
                  f"<formula1>{kinds}</formula1></dataValidation></dataValidations>") if inputs else ""
    return (XML + f'<worksheet xmlns="{NS}"><sheetViews><sheetView workbookViewId="0"><pane xSplit="1" ySplit="1" topLeftCell="B2" '
            f'activePane="bottomRight" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="1" width="{WIDTH_A / 7:.2f}" customWidth="1"/>'
            + f'<col min="2" max="{last + SPARE}" width="{WIDTH / 7:.2f}" customWidth="1"/>'
            + f"</cols><sheetData>{data}</sheetData>{validation}</worksheet>"), header_cells(tab, have)


def cited(tab: Tab, key: tuple[int, int], columns: dict[tuple[str, str], Column], seen: set[tuple[int, int]]) -> tuple[set[str], bool]:
    """The formats of the columns a table cell's formula cites, directly or through the table's own cells, and whether
    it divides by a quantity that cites a column (a ratio)."""
    v = tab.cells.get(key)
    if key in seen or v is None or isinstance(v, (str, int, float)):
        return set(), False
    seen.add(key)

    def go(n: Node) -> tuple[set[str], bool]:
        match n:
            case Stat(t, cid, _):
                return {columns[(t, cid)].format}, False
            case Pool(t, run):
                return {columns[(t, x)].format for x in run}, False
            case Cell(_, r, c):
                return cited(tab, (r, c), columns, seen)
            case Span(a, b):
                parts = [cited(tab, (r, c), columns, seen) for r in range(a.row, b.row + 1) for c in range(a.col, b.col + 1)]
                return {f for x, _ in parts for f in x}, any(q for _, q in parts)
            case Neg(x):
                return go(x)
            case Bin(op, a, b):
                (fa, qa), (fb, qb) = go(a), go(b)
                return fa | fb, qa or qb or (op == "/" and bool(fb))
            case Call(_, args):
                parts = [go(x) for x in args]
                return {f for x, _ in parts for f in x}, any(q for _, q in parts)
            case _:
                return set(), False

    return go(v)


def cell_unit(v: str | float | Node | None, columns: dict[tuple[str, str], Column]) -> tuple[str, float] | None:
    """The money unit of a table cell that is a column's statistic, or one divided by a number (`money_unit`)."""
    match v:
        case Stat(t, cid, _):
            return money_unit(columns[(t, cid)])
        case Bin("/", a, Num(n)) if float(n) > 0:
            unit = cell_unit(a, columns)
            return None if unit is None else (unit[0], unit[1] * float(n))  # ₩ million / 1000 is ₩ billion
        case _:
            return None


def stat_of(v: str | float | Node | None) -> tuple[str, str] | None:
    """The column whose statistic a table cell shows, alone or divided by a number, or None."""
    match v:
        case Stat(t, cid, _):
            return t, cid
        case Bin("/", a, Num(_)):
            return stat_of(a)
        case _:
            return None


def table_shown(tab: Tab, computed: dict[tuple[int, int], tuple[Scalar, float]], columns: dict[tuple[str, str], Column]
                ) -> tuple[dict[tuple[int, int], str | None], dict[tuple[int, int], str]]:
    """Each number cell's format, None for Google's General, and each head renamed to name its run's scaled unit. A
    typed whole number without a `formats` entry, a label such as a year, shows as typed; any other takes its `formats`
    entry, else the one format kind of the columns it cites, unless it divides by one ("number" where it cites none,
    several or a ratio). Cells of one kind or format that stand one under another in a column, a block's column, share
    one format, worked out on all their values (`run_format`); a run of money in one unit (`cell_unit`) is shown in
    the unit that gives about two significant figures (`scaled_format`), named after the nearest text above it in the
    three rows over the run ("Mean, ₩ trillion"), never by rounding a value."""
    heads: dict[tuple[int, int], str] = {}
    out: dict[tuple[int, int], str | None] = {}
    kinds: dict[tuple[int, int], str] = {}
    for (r, c), (v, _) in computed.items():
        if not isinstance(v, float):
            continue
        fmt = next((f for (r1, c1, r2, c2), f in tab.formats if r1 <= r <= r2 and c1 <= c <= c2), None)
        typed = tab.cells.get((r, c))
        if fmt is None and isinstance(typed, float) and typed.is_integer():
            out[(r, c)] = None
            continue
        if fmt is None:
            cites, ratio = cited(tab, (r, c), columns, set())
            fmt = cites.pop() if len(cites) == 1 and not ratio else "number"
        kinds[(r, c)] = fmt
    runs: list[list[tuple[int, int]]] = []
    for key in sorted(kinds, key=lambda k: (k[1], k[0])):  # a loop over the cells by column, gathering the runs
        if runs and key[1] == runs[-1][-1][1] and key[0] == runs[-1][-1][0] + 1 and kinds[key] == kinds[runs[-1][-1]]:
            runs[-1].append(key)
        else:
            runs.append([key])

    def block_of(run: list[tuple[int, int]]) -> tuple[object, ...]:
        """The rows and the columns a run's cells take statistics of: a mean and its low and high ends share it."""
        stats = tuple(stat_of(tab.cells.get(k)) for k in run)
        return (run[0][0], len(run), stats) if all(stats) else (run[0], )

    blocks: dict[tuple[object, ...], list[float]] = {}
    for run in runs:
        blocks.setdefault(block_of(run), []).extend(cast(float, computed[k][0]) for k in run)
    for run in runs:
        d = np.array([cast(float, computed[k][0]) for k in run])
        fmt = run_format(kinds[run[0]], d)
        units = {cell_unit(tab.cells.get(k), columns) for k in run}
        unit = units.pop() if len(units) == 1 else None
        scaled = None if unit is None else scaled_format(kinds[run[0]], unit, d, np.array(blocks[block_of(run)]))
        r0, c = run[0]
        head = next(((r, c) for r in range(r0 - 1, max(r0 - 4, 0), -1) if isinstance(tab.cells.get((r, c)), str)), None)
        if scaled is not None and head is not None and head not in heads:
            fmt, named = scaled
            text = cast(str, tab.cells[head])
            heads[head] = text if named in text else f"{text}, {named}"
        out.update(dict.fromkeys(run, fmt))
    return out, heads


def workbook(tabs: list[Tab], values: dict[str, dict[str, Floats]]) -> bytes:
    """The whole sheet as .xlsx bytes, written with the standard library in the form an upload to Google keeps."""
    setting, _ = bounds(tabs)
    styles = Styles()
    letters = {(t.name, x.id): x.letter for t in tabs for x in [*t.columns, *t.methods]}
    _, pct = bounds(tabs)
    columns = {(t.name, c.id): c for t in tabs for c in t.columns}
    written = [worksheet(t, styles, setting, values[t.name], letters, sensitivity_cells(t, tabs, values, pct) if t.kind == "sensitivity" else None,
                         table_shown(t, table_values(t, values, pct), columns) if t.kind == "table" else None, tab_names=[x.name for x in tabs], pct=pct)
               for t in tabs]
    n = len(written)
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ct = "application/vnd.openxmlformats-officedocument.spreadsheetml"
    noted = {i: notes for i, (_, notes) in enumerate(written, 1) if notes}  # a tab without notes gets no comments part
    sheets = [xml if i not in noted else xml.replace(f'<worksheet xmlns="{NS}">', f'<worksheet xmlns="{NS}" xmlns:r="{rel}">', 1)
              .removesuffix("</worksheet>") + '<legacyDrawing r:id="rId1"/></worksheet>' for i, (xml, _) in enumerate(written, 1)]
    note_parts: dict[str, str] = {}
    for i, notes in noted.items():
        note_parts[f"xl/comments{i}.xml"], note_parts[f"xl/drawings/vmlDrawing{i}.vml"] = comments_parts(notes, i)
        note_parts[f"xl/worksheets/_rels/sheet{i}.xml.rels"] = (
            XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/vmlDrawing" Target="../drawings/vmlDrawing{i}.vml"/>'
            f'<Relationship Id="rId2" Type="{rel}/comments" Target="../comments{i}.xml"/></Relationships>')
    parts = {
        "[Content_Types].xml": XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + ('<Default Extension="vml" ContentType="application/vnd.openxmlformats-officedocument.vmlDrawing"/>' if noted else "")
        + f'<Override PartName="/xl/workbook.xml" ContentType="{ct}.sheet.main+xml"/>'
        f'<Override PartName="/xl/styles.xml" ContentType="{ct}.styles+xml"/>'
        + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="{ct}.worksheet+xml"/>' for i in range(1, n + 1))
        + "".join(f'<Override PartName="/xl/comments{i}.xml" ContentType="{ct}.comments+xml"/>' for i in noted) + "</Types>",
        "_rels/.rels": XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": XML + f'<workbook xmlns="{NS}" xmlns:r="{rel}"><sheets>'
        + "".join(f'<sheet name="{escape(t.name, {chr(34): "&quot;"})}" sheetId="{i}" r:id="rId{i}"/>' for i, t in enumerate(tabs, 1))
        + "</sheets></workbook>",
        "xl/_rels/workbook.xml.rels": XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(f'<Relationship Id="rId{i}" Type="{rel}/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
        + f'<Relationship Id="rId{n + 1}" Type="{rel}/styles" Target="styles.xml"/></Relationships>',
        "xl/styles.xml": styles.xml(),
        **{f"xl/worksheets/sheet{i}.xml": s for i, s in enumerate(sheets, 1)},
        **note_parts,
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in parts.items():  # a fixed date, so the same data file gives the same bytes and digest
            z.writestr(zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)), text, compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue()


SHOWN_FAULTS = 40  # the faults a refused generate prints, then their count
# The marks a citation with no address begins with (the coordinator's convention, 2026-11-20): a judged value naming
# its judge, a source with no public copy naming who holds it, and the three older marks.
CITATION_MARKS = ("Judge:", "Unpublished:", "Judgment", "Convention", "No source:")


def citation_faults(tabs: list[Tab]) -> list[str]:
    """Each input whose citation neither ends in an address nor begins with one of CITATION_MARKS, so every source is a
    link (the owner, 2026-11-20: "every source should be a hyperlink, like it is in my examples"); a uniform random
    number from 0 to 1 that a pick reads (`picked`: a formula comparing it, IF(u<=0.5,...)) needs no citation."""
    read = {key for t in tabs for c in t.columns if c.formula is not None for key in picked(c.formula)}
    return [f"{t.name} {c.letter}3 ({c.id}): its citation neither ends in an address nor begins with "
            + ", ".join(f'"{m}"' for m in CITATION_MARKS) + f": {c.citation[:80]!r}"
            for t in tabs for c in t.columns if c.kind in REQUIRED and link(c.citation)[1] is None
            and not c.citation.startswith(CITATION_MARKS)
            and not (c.kind == "uniform" and (c.params["lo"], c.params["hi"]) == (0, 1) and (t.name, c.id) in read)]


def picked(node: Node) -> set[tuple[str, str]]:
    """The columns a formula compares directly, as a pick compares its random number (u<=0.5)."""
    match node:
        case Bin(op, a, b):
            own = {(x.tab, x.id) for x in (a, b) if op in COMPARE and isinstance(x, Ref) and x.id != DRAW}
            return own | picked(a) | picked(b)
        case Neg(x):
            return picked(x)
        case Call(_, args):
            return {key for x in args for key in picked(x)}
        case _:
            return set()


def title_cells(tab: Tab | None) -> set[tuple[int, int]]:
    """Where a tab's kind puts its titles: a guide's or text tab's headings, Sensitivity's B1, else A1."""
    if tab is not None and tab.kind in ("guide", "text"):
        return {(r, c) for r, row in enumerate(tab.rows or [], start=1) for c, v in enumerate(row, start=1) if marked(v)[0] == "heading"}
    return {(1, 2)} if tab is not None and tab.kind == "sensitivity" else {(1, 1)}


def layout_faults(data: bytes, tabs: list[Tab]) -> list[str]:
    """The generate check: the faults of the workbook in data, read back from its bytes, each naming its tab and cell
    (notes/sheet_twin_protocol.md 2.3.6; notes/sheet_layout_review.md 4.4, 4.7): (a) a text past MAX_LINES lines in a
    column under NARROW_PX, or in a table past NARROW_LINES there, or in a row lower than its lines x LINE_PX +
    ROW_PAD_PX (at least MIN_ROW_PX), outside a column tab's fixed header rows; (b) a merge; (c) a font other than
    FONT, or a size other than SIZE but a bold title larger in its tab kind's title place (`title_cells`); (d) more than
    one number format in a run of formatted cells one under another in a column of a table or sensitivity tab, a
    block's column; (e) a font colour outside COLOURS, or INPUT_BLUE on a formula; (f) a Sensitivity key,
    MAX(ABS(r),ABS(rank r)), without its IFERROR guard; (g) an input's citation without an address or a mark
    (`citation_faults`). A text is an inline string or a formula's cached string."""
    z = zipfile.ZipFile(io.BytesIO(data))
    st = ET.fromstring(z.read("xl/styles.xml"))
    codes = {int(f.get("numFmtId") or 0): f.get("formatCode") or "" for f in st.iter(M + "numFmt")}
    fonts: list[tuple[str | None, float, bool, str]] = []
    for f in st.iter(M + "font"):
        name, sz, colour = f.find(M + "name"), f.find(M + "sz"), f.find(M + "color")
        rgb = BLACK if colour is None else (colour.get("rgb") or str(colour.attrib))[-6:].upper()
        fonts.append((None if name is None else name.get("val"), SIZE if sz is None else float(sz.get("val") or 0), f.find(M + "b") is not None, rgb))
    xfs: list[tuple[int, int, bool]] = []  # font, number format, wrap
    for x in st.iter(M + "cellXfs"):
        for xf in x.iter(M + "xf"):
            al = xf.find(M + "alignment")
            xfs.append((int(xf.get("fontId") or 0), int(xf.get("numFmtId") or 0), al is not None and al.get("wrapText") in ("1", "true")))
    rels = {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    by_name = {t.name: t for t in tabs}
    faults: list[str] = citation_faults(tabs)
    for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"):
        name = sh.get("name") or ""
        target = rels[sh.get(R + "id")].lstrip("/")
        raw = z.read(target if target.startswith("xl/") else "xl/" + target).decode()
        root = ET.fromstring(raw)
        tab = by_name.get(name)
        model = tab is not None and tab.about is not None
        blocks = tab is not None and tab.kind in ("table", "sensitivity")
        titles = title_cells(tab)
        cols = [(int(c.get("min") or 0), int(c.get("max") or 0), float(c.get("width") or 0) * 7) for c in root.iter(M + "col")]

        def width(col: int) -> float:
            return next((w for a, b, w in cols if a <= col <= b), float(TABLE_PX))

        def font_fault(ref: str, s: int, formula: bool) -> None:
            fname, size, bold, colour = fonts[xfs[s][0]]
            m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
            title = m is not None and (int(m.group(2)), colnum(m.group(1))) in titles
            if fname != FONT or not (size == SIZE or (title and bold and size > SIZE)):
                faults.append(f"{name} {ref}: font {fname} {size:g}{' bold' if bold else ''}; every cell {FONT} {SIZE}, a title alone bold and larger, in its tab's title place")
            if colour not in COLOURS:
                faults.append(f"{name} {ref}: font colour {colour}; a cell's colour marks its kind: " + ", ".join(COLOURS))
            elif colour == INPUT_BLUE and formula:
                faults.append(f"{name} {ref}: a formula in input blue {INPUT_BLUE}; a formula is black, or green where it carries another tab's cell over unchanged")

        faults += [f"{name} {mc.get('ref')}: merged cells; widen the column instead" for mc in root.iter(M + "mergeCell")]
        if model:  # a column tab's draw rows hold numbers alone, so only their styles are checked: once a style and kind, not once a cell
            draws = raw[raw.find(f'<row r="{FIRST}"'):] if f'<row r="{FIRST}"' in raw else ""
            for s, f in set(re.findall(r'<c r="[A-Z]+\d+"(?: s="(\d+)")?\s*(?:/>|>\s*(<f\b)?)', draws)):
                style = f' s="{s}"' if s else ""
                body = r">\s*<f\b" if f else r"(?:/>|>(?!\s*<f\b))"  # the first cell of this style and kind
                if (dm := re.search(rf'<c r="([A-Z]+\d+)"{style}\s*{body}', draws)) is not None:
                    font_fault(dm.group(1), int(s or 0), bool(f))
        formatted: dict[int, list[tuple[int, str]]] = {}  # a column's formatted cells: row, format
        for row in root.iter(M + "row"):  # a loop over written rows; a sensitivity tab's static rank cells are among them, nothing computed
            r = int(row.get("r") or 0)
            if model and r >= FIRST:
                continue
            ht = row.get("ht")
            got = None if ht is None else float(ht) * 4 / 3
            need, where = 0.0, ""
            for c in row.iter(M + "c"):
                ref = c.get("r") or ""
                col = colnum(re.sub(r"\d", "", ref))
                f = c.find(M + "f")
                font_fault(ref, int(c.get("s") or 0), f is not None)
                if tab is not None and tab.kind == "sensitivity" and f is not None and "MAX(ABS(" in (f.text or "") and "IFERROR(" not in (f.text or ""):
                    faults.append(f"{name} {ref}: the key MAX(ABS(r),ABS(rank r)) lacks its IFERROR guard, so one moved input's "
                                  f'"{SENS_MOVED}" would blank every rank')
                font, fmt_id, wrap = xfs[int(c.get("s") or 0)]
                _, size, bold, _ = fonts[font]
                if blocks and fmt_id:
                    formatted.setdefault(col, []).append((r, codes.get(fmt_id, f"built-in format {fmt_id}")))
                v = c.find(M + "v")
                text = "".join(x.text or "" for x in c.iter(M + "t")) if c.get("t") == "inlineStr" else \
                    (v.text or "") if c.get("t") == "str" and v is not None else None
                if not text or (model and r < FIRST):
                    continue
                px = width(col)
                lines = lines_of(text, px, size, bold)
                if px < NARROW_PX and lines > MAX_LINES:
                    faults.append(f"{name} {ref}: {lines} lines of text in a {px:.0f} px column; at most {MAX_LINES} under {NARROW_PX} px: widen it")
                elif tab is not None and tab.kind == "table" and wrap and px < NARROW_PX and lines >= NARROW_LINES:
                    faults.append(f"{name} {ref}: {lines} lines of text wrapped in a {px:.0f} px table column; a table column under {NARROW_PX} px holds under {NARROW_LINES}: widen it")
                h = row_px(text, px, size, wrap, bold)
                if h > need:
                    need, where = h, ref
            if where and (got is None or got < need - 0.5):
                faults.append(f"{name} {where}: row {r} is {'of no set height' if got is None else f'{got:.0f} px'}, its text needs {need:.0f} px")
        for col, cells in formatted.items():
            cells.sort()
            start = 0
            for k in range(1, len(cells) + 1):
                if k == len(cells) or cells[k][0] != cells[k - 1][0] + 1:
                    run = cells[start:k]
                    if len({f for _, f in run}) > 1:
                        x = letter(col)
                        faults.append(f"{name} {x}{run[0][0]}:{x}{run[-1][0]}: one block column holds several number formats: "
                                      + ", ".join(f"{x}{r} {f!r}" for r, f in run))
                    start = k
    return faults


def summary(d: Floats, pct: tuple[float, float]) -> list[float]:
    """The low percentile, the mean and the high percentile of a column's draws, as rows LOW, MEAN and HIGH compute them."""
    finite = bool(np.isfinite(d).all())  # correctly rounded where it can be, so a constant column's mean is the constant
    mean = math.fsum(d.tolist()) / len(d) if finite else float(np.mean(d))
    return [float(np.percentile(d, 100 * pct[0])), mean, float(np.percentile(d, 100 * pct[1]))]


def generate(tabs: list[Tab], out: Path) -> str:
    """Write DIR/sheet.xlsx and DIR/columns.tsv; return the upload reference, sha256:<digest>:<path>."""
    values = compute(tabs)
    data = workbook(tabs, values)
    faults = layout_faults(data, tabs)
    if faults:
        more = f"\nand {len(faults) - SHOWN_FAULTS} more" if len(faults) > SHOWN_FAULTS else ""
        raise Fault(f"the generate check finds {len(faults)} faults, so nothing is written:\n" + "\n".join(faults[:SHOWN_FAULTS]) + more)
    _, pct = bounds(tabs)
    lines = ["\t".join([t.name, c.letter, c.id, c.name, *(repr(s) for s in summary(d, pct))])
             for t in tabs for c, d in zip(t.columns, values[t.name].values())]
    out.mkdir(parents=True, exist_ok=True)
    path = (out / "sheet.xlsx").resolve()
    path.write_bytes(data)
    (out / "columns.tsv").write_text("".join(ln + "\n" for ln in lines))
    return f"sha256:{hashlib.sha256(data).hexdigest()}:{path}"


# compare ---------------------------------------------------------------------------------------------------------

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
Found = str | float  # a value of an export: a number or a text


Sheet = tuple[int, dict[tuple[int, int], Found], dict[tuple[int, int], str]]


def read_export(path: Path) -> dict[str, Sheet]:
    """Each sheet's place in the workbook, its cached values keyed (row, column), and each cell's list of allowed values."""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    shared = [] if "xl/sharedStrings.xml" not in names else [
        "".join(t.text or "" for t in si.iter(M + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si")
    ]
    rels = {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out: dict[str, Sheet] = {}
    for position, sh in enumerate(ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"), start=1):
        target = rels[sh.get(R + "id")].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        values: dict[tuple[int, int], Found] = {}
        lists: dict[tuple[int, int], str] = {}
        root = ET.fromstring(z.read(target))
        for dv in root.iter(M + "dataValidation"):
            if dv.get("type") != "list":
                continue
            allowed = dv.findtext(M + "formula1") or ""
            for part in (dv.get("sqref") or "").split():
                m = re.fullmatch(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?", part)
                if not m:
                    continue
                c1, r1 = colnum(m.group(1)), int(m.group(2))
                c2, r2 = (colnum(m.group(3)), int(m.group(4))) if m.group(3) else (c1, r1)
                if r1 <= 4 <= r2:  # the kinds' row is the only one compared
                    lists.update({(4, col): allowed for col in range(c1, c2 + 1)})
        for c in root.iter(M + "c"):
            m = re.fullmatch(r"([A-Z]+)(\d+)", c.get("r") or "")
            if not m:
                continue
            key = (int(m.group(2)), colnum(m.group(1)))
            v, ty = c.find(M + "v"), c.get("t")
            if ty == "inlineStr":
                values[key] = "".join(t.text or "" for t in c.iter(M + "t"))
            elif v is not None and v.text is not None:
                values[key] = shared[int(v.text)] if ty == "s" else v.text if ty in ("str", "e") else "TRUE" if ty == "b" and v.text == "1" else "FALSE" if ty == "b" else float(v.text)
        out[sh.get("name") or ""] = (position, values, lists)
    return out


def agree(want: Found, found: Found | None, scale: float) -> bool:
    if isinstance(want, str):
        return want == ("" if found is None else found)
    if not isinstance(found, float):
        return False
    return abs(want - found) <= TOL * max(abs(want), abs(found), scale)


def compare_tab(tab: Tab, tabs: list[Tab], everything: dict[str, dict[str, Floats]], pct: tuple[float, float], letters: dict[tuple[str, str], str],
                position: int, values: dict[tuple[int, int], Found], lists: dict[tuple[int, int], str]) -> list[str]:
    bad: list[str] = []
    computed = everything[tab.name]

    def check(r: int, col: int, want: Found, scale: float = 0.0) -> None:
        if not agree(want, values.get((r, col)), scale):
            bad.append(f"{tab.name} {letter(col)}{r}: expected {want!r}, found {values.get((r, col))!r}")

    kinds = '"' + ",".join(KINDS_LIST) + '"'
    inputs = {colnum(c.letter) for c in tab.columns if c.kind in REQUIRED}
    for col in sorted(inputs | {k[1] for k in lists if k[1] > 1} if tab.columns else ()):
        found = lists.get((4, col))
        if col in inputs and found != kinds:
            bad.append(f"{tab.name} {letter(col)}4: expected the dropdown of the seven kinds, found {'no dropdown' if found is None else found}")
        elif col not in inputs and found is not None:
            bad.append(f"{tab.name} {letter(col)}4: expected no dropdown, found {found}")
    if position != tab.position:
        bad.append(f"{tab.name}: tab position expected {tab.position}, found {position}")
    for r, row in enumerate(tab.rows or [], start=1):
        for col, want in enumerate(row, start=1):
            check(r, col, tab.interval if want == SETTING and tab.interval is not None else link(marked(want)[1])[0])
    if tab.about is not None:
        check(1, 1, tab.about)
    twin = sensitivity_values(tab, tabs, everything, pct) if tab.kind == "sensitivity" else table_values(tab, everything, pct)
    if tab.kind == "table":  # the heads that name a scaled unit
        twin.update({k: (v, 0.0) for k, v in table_shown(tab, twin, {(t.name, c.id): c for t in tabs for c in t.columns})[1].items()})
    for (r, col), (v, scale) in sorted(twin.items()):
        check(r, col, "" if v is None else v, scale)
    for m in tab.methods:
        check(4, colnum(m.letter), "Credence")
        check(5, colnum(m.letter), float(m.credence))
    for c, d in zip(tab.columns, computed.values()):
        col, x = colnum(c.letter), c.letter
        scale = float(np.nanmax(np.abs(d))) if np.isfinite(d).any() else 0.0
        if c.kind in REQUIRED:
            head: list[Found] = [link(c.citation)[0], c.kind, *(float(c.params[k]) if k in c.params else "" for k in PARAM_ROW)]
        else:
            head = [shown_formula(c, letters, tab.name), *[""] * 8]
        name, note = column_label(c, d, pct)
        for r, want in enumerate([name, note, *head, *summary(d, pct)], start=1):
            check(r, col, want, scale)
        wrong = [r for r in range(FIRST, LAST + 1) if not agree(float(d[r - FIRST]), values.get((r, col)), scale)]
        for r in wrong[:3]:
            bad.append(f"{tab.name} {x}{r}: expected {float(d[r - FIRST])!r}, found {values.get((r, col))!r}")
        if wrong:
            bad.append(f"{tab.name} column {x} ({c.id}): {len(wrong)} of {DRAWS} draws disagree")
    return bad


def compare(tabs: list[Tab], export: Path, only: str | None) -> list[str]:
    sheets = read_export(export)
    computed = compute(tabs)
    _, pct = bounds(tabs)
    letters = {(t.name, x.id): x.letter for t in tabs for x in [*t.columns, *t.methods]}
    if only is not None:
        chosen = [t for t in tabs if t.name == only]
        if not chosen:
            raise Fault(f"{only}: no tab of this name in the data file")
        if only not in sheets:
            return [f"{only}: in the data file, not in the export"]
        return compare_tab(chosen[0], tabs, computed, pct, letters, *sheets[only])
    bad = [f"{name}: in the export, not in the data file" for name in sheets if name not in (t.name for t in tabs)]
    for t in tabs:
        bad += compare_tab(t, tabs, computed, pct, letters, *sheets[t.name]) if t.name in sheets else [f"{t.name}: in the data file, not in the export"]
    return bad


def compare_final(tabs: list[Tab], export: Path, only: str | None) -> tuple[list[str], bool]:
    """Rows LOW to HIGH of each column of one tab (the last with columns, or `only`) against Python's statistics."""
    named = [t for t in tabs if t.name == only] if only is not None else [t for t in tabs if t.columns][-1:]
    if not named or not named[0].columns:
        raise Fault(f"{only}: no tab of this name with columns in the data file" if only else "no tab has columns")
    tab = named[0]
    sheets = read_export(export)
    if tab.name not in sheets:
        return [f"{tab.name}: in the data file, not in the export", "FAIL: the final estimate is not in the export"], False
    values = sheets[tab.name][1]
    _, pct = bounds(tabs)
    lines: list[str] = []
    failed = 0
    for c, d in zip(tab.columns, compute(tabs)[tab.name].values()):
        want = summary(d, pct)
        scale = float(np.nanmax(np.abs(d))) if np.isfinite(d).any() else 0.0
        found = [values.get((r, colnum(c.letter))) for r in (LOW, MEAN, HIGH)]
        ok = all(agree(w, f, scale) for w, f in zip(want, found))
        failed += not ok
        shown = ", ".join(f"{n} {w:.6g} found {'missing' if f is None else f if isinstance(f, str) else format(f, '.6g')}"
                          for n, w, f in zip(("low", "mean", "high"), want, found))
        lines.append(f"{'ok  ' if ok else 'FAIL'} {tab.name} {c.letter} ({c.id}): {shown}; tolerance {TOL * scale:.3g}")
    n = len(tab.columns)
    lines.append(f"pass: the final estimate of all {n} columns of {tab.name} agrees" if not failed
                 else f"FAIL: {failed} of {n} columns of {tab.name} disagree")
    return lines, not failed


def placeholders(x: object) -> list[str]:
    """Every text of the data file that begins with the AUTHOR mark."""
    if isinstance(x, str):
        return [x] if x.startswith(AUTHOR) else []
    if isinstance(x, dict):
        return [s for v in cast(dict[str, object], x).values() for s in placeholders(v)]
    if isinstance(x, list):
        return [s for v in cast(list[object], x) for s in placeholders(v)]
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.sheet_script", description=(__doc__ or "").split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate", help="write sheet.xlsx and columns.tsv, and print the upload reference")
    g.add_argument("data", type=Path)
    g.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("compare", help="compare the data file's columns with a sheet's .xlsx export")
    c.add_argument("data", type=Path)
    c.add_argument("export", type=Path)
    c.add_argument("--tab")
    c.add_argument("--every-draw", action="store_true", help="compare every cell and every draw of every tab, as exactly as floats allow")
    a = ap.parse_args(argv)
    try:
        tabs = load(cast(Path, a.data))
        if a.command == "generate":
            print(generate(tabs, cast(Path, a.out)))
            raw = tomllib.loads(cast(Path, a.data).read_text())
            for text in placeholders(raw):
                print(f"warning: an AUTHOR placeholder the data file must fill: {text[:120]}", file=sys.stderr)
            if "details" not in cast(list[dict[str, object]], raw["tab"])[0]:
                print("warning: the guide has no details, the row linking the reader's document", file=sys.stderr)
            return 0
        if a.every_draw:
            lines = compare(tabs, cast(Path, a.export), cast(str | None, a.tab))
            ok = not lines
        else:
            lines, ok = compare_final(tabs, cast(Path, a.export), cast(str | None, a.tab))
    except (Fault, OSError, zipfile.BadZipFile) as e:  # exit 1 means a disagreement, so no other failure may take it
        print(f"refused: {e}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
