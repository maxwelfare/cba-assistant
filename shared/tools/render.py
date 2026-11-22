"""tools/render.py: the shared Markdown-to-PDF renderer every project uses (R67, notes/r67_shared_renderer.md 1).

    <venv python> shared/tools/render.py SRC.md [SRC.md ...] --out OUT.pdf
        [--to pdf|docx|html] [--notice TEXT] [--metadata FILE.json] [--format-dir DIR --format NAME]

or, as a function, `render(sources, out, ...)`, which returns a `Report` (pages, contents entries, links, warnings)
or raises `Refused`, one line per fault. On a refusal the command prints each fault and exits 1, and no file is
written at `--out`. Standard library only; the engine is the Quarto binary that `shared/tools/quarto_setup.py` installs
(Pandoc and Typst inside it, found by its `binary()`), read with poppler's `pdftotext` and MuPDF's `mutool`. Ported
from the cost-benefit project's Quarto route (tools/typeset.py crossrefs(), missing_glyphs() and build_quarto(), at
its commit edd0548).

1. Sources. Several are joined in order with a page break between them. An image's relative path is read from the
   folder of the source that names it.
2. Format. The base format is `shared/tools/render_format/_extensions/doc` (format `doc-typst`): the tabulary width rule
   for tables and their placement (into the margins, smaller, landscape), links, the contents list from the `##` and
   `###` headings, right-aligned number columns, table cells that open with Typst markup printed as written, and
   the fitting of wide equations; its body face is TeX Gyre Pagella (Debian's fonts-texgyre) at Quarto's 11 pt.
   `--format-dir DIR --format NAME` renders with a project's own extension in `DIR/_extensions` instead, which
   defines the base format's `doc-tables` (its header), since this tool calls it at the body's start.
3. Metadata. `--metadata` is a JSON file of Quarto metadata (Typst keys). The page is the metadata's `papersize`
   (the format's default, us-letter) and the text block is set by its `margin`, keys `x`, `y`, `top`, `bottom`,
   `left`, `right` or `rest`, each a length in pt, in, mm or cm; a side it leaves out (with no `rest`) is the
   default's, 1.2 in at the sides and 1 in at the top and bottom, which this tool passes to Quarto so that the page
   and the overflow check agree. The default is the seat's: shared agents/pdf-layout.md 1.1 asks a full line of 75
   to 90 characters (a range a seat derived from Butterick's Practical Typography); at 11 pt, Pagella's mean full
   line is 87.9 characters at 1.2 in and 91.7 at 1.1 in, where Typst's Libertinus Serif gave 93.5 at Quarto's 1.25 in
   (measured 2026-11-21), the margin the owner faulted on 2026-11-10 ("the margins are absurdly large").
   `table-size` is the share of the body's size tables are set at (9/11 by default), honoured as given wherever the
   table fits at it, below TABLE_FLOOR too; `table-stretch`, a number, spaces a table's rows as LaTeX's \\arraystretch
   of that value does (the cost-benefit project's 1.15), where Typst's 5 pt insets above and below are the default. `short-title` and `kind` (such as summary, paper or appendix) make the
   PDF's Title "short title: kind", and the PDF opens with its Title in the viewer's tab (DisplayDocTitle), so that
   two documents of one case differ there. A `bibliography` gets `link-citations: true` (Pandoc's). `--notice` is
   set at the head of every page.
4. Cross-references. `@sec-x`, `@fig-x` and `@tbl-x` become links printed "Section 3" (a heading that opens with its
   number) or the heading's words, and "Figure N" or "Table N"; a labelled caption gets "Figure N. " or "Table N. "
   in front. A span `[...]{#name}` is a link target (links.lua).

Refusals (design 1.4), each naming what fails:
1. a reference or an internal link `[...](#name)` whose label no attribute carries, and Quarto's "Unable to
   resolve crossref";
2. a table too wide for the page: one whose longest words do not fit the line runs into the side margins, up to
   TRIM_SAFE from the page's edge; then its type shrinks, down to TABLE_FLOOR; then it gets a landscape page, where
   the same order runs again; past that the format stops the build, naming the table. A display equation too wide
   at 80% size is refused too. TRIM_SAFE (36 pt, 0.5 in) is the seat's: wider than the band an office printer
   leaves unprinted at a sheet's edge (commonly about 1/6 in) and the 1/8 in a commercial printer's trim may wander,
   so a table's edge survives either (both figures the seat's recollection, from no stored source). TABLE_FLOOR
   (8 pt) is the seat's: the Urban Institute's least size for a chart's sources and notes in a PDF, the smallest
   text agents/pdf-layout.md 2.6 allows, and the format's old last step (8/9 of 9 pt). A table's header cells wrap
   rather than widen its columns; a table whose words fit the line by wrapping its cells is not too wide;
3. in a PDF, a word outside the text block, or two words whose boxes overlap by more than 0.5 pt both ways
   (`pdftotext -bbox`). Across, a word's whole box must lie within the block, with 1 pt slack; down, its middle
   must, since poppler's box runs from the font's full ascent while Typst sets lines from cap height to baseline, so
   a large title's box reaches above the top margin with no fault. The page number in the bottom margin (its
   number, "of" and the page count) and the notice's words in the top margin are left out. Two words both set in a
   math font are not tested for overlap, since Typst sets an equation's glyphs, a subscript tucked under an italic's
   overhang or a bracket against a \\Big bracket, by the font's own math metrics, which no layout fault moves; a
   math word is held to the block like any other, its middle allowed MATH_DROP below the bottom for a subscript. A
   table run into the margins (2) may reach the trim-safe edge across, its band down the page read from the marks
   the format leaves in the PDF (which this tool takes out). A page that carries the format's doc-placed mark, one
   drawn whole from a PDF this tool rendered and checked already (a project's summary set as the first page of its
   paper), is left out of this check;
4. a character no font draws, an unknown font family, and a layout Typst did not settle.

Warnings, in the report and printed by the command, never refused: a body cell outside a table's first column that
holds a letter and is no number (the format's numbers.lua), since a table's body holds numbers and its text goes in
the first column or a footnote (the owner, 2026-11-21: "The table shoudl just be nymbers, any text goes in the left
column or a footntote. this should be a general rule"; a warning rather than a refusal is the seat's choice, so no
project's documents stop building).

Facts of the pinned engines that a format for this tool must allow for (Typst 0.15.1 in Quarto 1.11.9; found while
building the cost-benefit project's house format, its welfare log at commit 8cb1cd7):
1. measure() of content that overflows the height given (columns, a fixed block) returns that height less a
   rounding error of about 1e-12 pt, and does not show the overflow. A fit test written `measured < height` passes
   falsely, so it needs a margin (0.01 pt serves), and a block of fixed height built on such a bisection drops the
   overflow silently: a layout that fixes heights this way is checked afterwards by its page count or by a count of
   the text drawn.
2. A PDF bookmark's text is the heading's plain text: a `box(text(...))` inside the heading is part of it, a
   `context` expression is not, so an icon or other decoration in a heading is drawn inside a context.
   heading(bookmarked: auto) follows `outlined`, so a heading that is a bookmark and no contents entry needs
   bookmarked: true.
3. Quarto joins a `font-paths` entry that starts with "/" to its project's folder, not the file system's root, so a
   font folder is linked beside the document and named by a relative path.
4. A show-set rule written as a raw Typst block at the top of the document's body wins over Quarto's brand rules and
   over a format's include-in-header, which come before the body.
5. Quarto applies one `--metadata-file` per render; everything goes in one file.
6. In a show rule on a table, every column size reads back as type 'relative', so a column given a width is told
   from an unsized one by `c != auto`. text(size: s, body) returns styled content whose child has lost the size, so
   a width is measured with the size given explicitly. h(0pt) is dropped, while h(0.01pt) makes a break point that
   puts no character in the text layer.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from quarto_setup import Refusal, binary

SHARED = Path(__file__).resolve().parents[1]
FORMAT_DIR = SHARED / "tools" / "render_format"
XHTML = "{http://www.w3.org/1999/xhtml}"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
SLACK, OVERLAP = 1.0, 0.5  # pt: design 1.4.4
DEFAULT_MARGIN = {"x": "1.2in", "y": "1in"}  # the seat's: a line of 75 to 90 characters in the format's face (item 3)
TABLE_SHARE = 9 / 11  # a table's type as a share of the body's: LaTeX's \footnotesize in its 11 pt class
TABLE_FLOOR = 8.0  # pt, the seat's: the least size a table is shrunk to (Refusals 2)
TRIM_SAFE = 36.0  # pt, the seat's: the least distance from the page's edge of a table run into the margins
WARNING = "doc-warning: "  # the start of a line the format's filters write for Report.warnings
UNITS = {"pt": 1.0, "in": 72.0, "mm": 72 / 25.4, "cm": 72 / 2.54}
EXTENSION = {"pdf": "pdf", "docx": "docx", "html": "html"}
PAGE_BREAK = "\n\n{{< pagebreak >}}\n\n"
SHOWN = 20  # faults of one kind printed in full; the rest are counted
GRID = 10.0  # pt: the squares math boxes are filed under, for overflow()
MATH_DROP = 3.0  # pt, the seat's: how far a math word's middle may sit below the block (a subscript's drop, about
# a quarter em at 11 pt, the order of an OpenType math font's SubscriptShiftDown; the seat's recollection)


class Refused(Exception):
    """A refusal; `faults` holds one line per fault."""

    def __init__(self, faults: list[str]) -> None:
        super().__init__("\n".join(faults))
        self.faults = faults


@dataclass(frozen=True)
class Report:
    pages: int  # 0 for docx and html
    contents: int  # contents entries: the `##` and `###` headings, where the format sets a list
    links: int  # link annotations in the PDF, internal and external; 0 for docx and html
    warnings: tuple[str, ...] = ()  # one line per prose cell in a table's body (Warnings, in the module's docstring)


# Cross-references: a label in an attribute, a reference in prose, any identifier an internal link may name, and
# such a link (the cost-benefit project's typeset.py).
LABEL = r"((?:sec|fig|tbl)-[\w-]*\w)"
HEADING_LABEL = re.compile(r"^#{2,6} (.*?)\s*\{[^}]*#" + LABEL + r"[^}]*\}\s*$")
ATTRIBUTE_ID = r"\{(?:[^}]*\s)?#"  # an attribute's identifier, anywhere among its attributes (Pandoc's syntax)
FIGURE_LABEL = re.compile(r"^!\[(.*)\](\([^)\s]+\))" + ATTRIBUTE_ID + LABEL + r"[^}]*\}\s*$")
TABLE_LABEL = re.compile(r"^: (.*?)\s*" + ATTRIBUTE_ID + LABEL + r"[^}]*\}\s*$")
REFERENCE = re.compile(r"(?<![\w@\\])@" + LABEL)
IDENTIFIER = re.compile(ATTRIBUTE_ID + r"([^\s}]+)")
INTERNAL_LINK = re.compile(r"\]\(#([^)\s]+)\)")
IMAGE = re.compile(r"^(!\[.*\]\()([^)\s]+)", re.M)


def crossrefs(text: str, typst: bool = True) -> str:
    """The Markdown with its cross-references resolved. A reference `@sec-x`, `@fig-x` or `@tbl-x` becomes a link to
    its label, printed "Section 3" for a heading that opens with its number ("## 3 Effects {#sec-x}") and the
    heading's words for one that does not, and "Figure N" or "Table N" by the order of the labelled figures and
    tables; each labelled caption gets its "Figure N. " or "Table N. " in front. A figure's label becomes a link
    target at its caption's start, a span round the caption, since Typst places a target on the float itself where
    the float was written rather than where it prints. A labelled table's float is labelled `<label>-float` and, in
    Typst, the target in its caption is Typst's own (`typst` false, for docx and html, leaves the table's label
    on its float). Raises Refused naming every reference, and every internal link `[...](#name)`, whose label no
    attribute carries."""
    lines = text.splitlines()
    names: dict[str, str] = {}
    identifiers: set[str] = set()
    counts = {"fig": 0, "tbl": 0}
    fenced = False
    for line in lines:
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        if fenced:
            continue
        identifiers |= set(IDENTIFIER.findall(line))
        heading = HEADING_LABEL.match(line)
        if heading:
            number = re.match(r"\d+(\.\d+)*(?= )", heading.group(1))
            names[heading.group(2)] = f"Section {number.group(0)}" if number else heading.group(1)
        for kind, word, pattern, group in (("fig", "Figure", FIGURE_LABEL, 3), ("tbl", "Table", TABLE_LABEL, 2)):
            found = pattern.match(line)
            if found:
                counts[kind] += 1
                names[found.group(group)] = f"{word} {counts[kind]}"
    out: list[str] = []
    missing: list[str] = []
    fenced = False
    for line in lines:
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        if fenced:
            out.append(line)
            continue
        parts = line.split("`")
        for i in range(0, len(parts), 2):  # the even pieces lie outside code spans
            missing += [f"@{m}" for m in REFERENCE.findall(parts[i]) if m not in names]
            missing += [f"#{m}" for m in INTERNAL_LINK.findall(parts[i]) if m not in identifiers]
            parts[i] = REFERENCE.sub(lambda m: f"[{names.get(m.group(1), '')}](#{m.group(1)})", parts[i])
        line = "`".join(parts)
        figure, table = FIGURE_LABEL.match(line), TABLE_LABEL.match(line)
        if figure:
            caption, path, label = figure.groups()
            line = f"![[{names[label]}. {caption}]{{#{label}}}]{path}"
        elif table and typst:
            caption, label = table.groups()
            line = f": `#metadata(none)<{label}>`{{=typst}}{names[label]}. {caption} {{#{label}-float}}"
        elif table:
            caption, label = table.groups()
            line = f": {names[label]}. {caption} {{#{label}}}"
        out.append(line)
    if missing:
        raise Refused(["no label for " + ", ".join(dict.fromkeys(missing))
                       + ": a reference or a link names a target no heading, figure, table or span carries"])
    return "\n".join(out) + "\n"


def length(value: object, key: str) -> float:
    """A Typst length given in the metadata, in pt."""
    found = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(pt|in|mm|cm)\s*", str(value))
    if not found:
        raise Refused([f"margin {key}: {value!r} is not a length in pt, in, mm or cm"])
    return float(found.group(1)) * UNITS[found.group(2)]


def margins(margin: object) -> tuple[float, float, float, float]:
    """The left, top, right and bottom margins, in pt, of Typst's `margin` dictionary (its keys' precedence:
    a side over its axis, `x` or `y`, over `rest`)."""
    if not isinstance(margin, dict):
        raise Refused([f"margin {margin!r}: give a dictionary of x, y, top, bottom, left, right or rest"])
    given = {str(k): v for k, v in cast(dict[object, object], margin).items()}
    unknown = sorted(set(given) - {"x", "y", "top", "bottom", "left", "right", "rest"})
    if unknown:
        raise Refused([f"margin keys {', '.join(unknown)}: the overflow check reads only x, y, top, bottom, left, "
                       "right and rest"])

    def side(name: str, axis: str) -> float:
        for key in (name, axis, "rest"):
            if key in given:
                return length(given[key], key)
        raise Refused([f"margin: no {name}, {axis} or rest given"])

    return side("left", "x"), side("top", "y"), side("right", "x"), side("bottom", "y")


Word = tuple[str, float, float, float, float]  # text, xMin, yMin, xMax, yMax in pt, y down


def word_boxes(pdf: Path) -> list[tuple[float, float, list[Word]]]:
    """Each page's width, height and word boxes, read by poppler's pdftotext -bbox."""
    out = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True, check=True,
                         errors="replace").stdout
    root = ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", out))
    return [(float(page.get("width", "0")), float(page.get("height", "0")),
             [((w.text or "").strip(), float(w.get("xMin", "0")), float(w.get("yMin", "0")),
               float(w.get("xMax", "0")), float(w.get("yMax", "0"))) for w in page.iter(f"{XHTML}word")])
            for page in root.iter(f"{XHTML}page")]


Box = tuple[float, float, float, float]  # xMin, yMin, xMax, yMax in pt, y down


def math_boxes(pdf: Path) -> list[list[Box]]:
    """Each page's boxes of the characters set in a math font (a family whose name holds "Math", as every OpenType
    math font's does: New Computer Modern Math, TeX Gyre Schola Math, STIX Two Math), read by MuPDF's stext."""
    out = subprocess.run(["mutool", "draw", "-F", "stext", "-o", "-", str(pdf)], capture_output=True, text=True,
                         check=True, errors="replace").stdout
    pages: list[list[Box]] = []
    for page in ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", out)).iter("page"):
        boxes: list[Box] = []
        for font in page.iter("font"):
            if "Math" in font.get("name", ""):
                for char in font.iter("char"):
                    q = [float(v) for v in char.get("quad", "").split()]
                    if len(q) == 8:
                        boxes.append((min(q[0::2]), min(q[1::2]), max(q[0::2]), max(q[1::2])))
        pages.append(boxes)
    return pages


def overflow(pdf: Path, block_margins: tuple[float, float, float, float], notice: str,
             wide: dict[int, list[tuple[float, float]]], placed: set[int]) -> list[str]:
    """Every word outside the text block and every pair of words that overlap (refusal 3 of the module's
    docstring), one line each, the first SHOWN of each kind in full and the rest counted. Two words both set in a
    math font are not tested against each other, a math word's middle may sit MATH_DROP below the block, and a word
    whose middle lies in one of a page's `wide` bands (from, to, in pt down the page; a table run into the margins)
    may reach the trim-safe edge across. A page in `placed`, drawn whole from a PDF this tool rendered and checked
    already, is left out."""
    left, top, right, bottom = block_margins
    pages = word_boxes(pdf)
    math = math_boxes(pdf)
    count = len(pages)
    notice_words = set(notice.split())
    outside: list[str] = []
    overlaps: list[str] = []
    for index, (width, height, words) in enumerate(pages):
        if index + 1 in placed:
            continue
        x0, y0, x1, y1 = left, top, width - right, height - bottom
        page_number = {str(index + 1), "of", str(count)}
        grid: dict[tuple[int, int], list[Box]] = {}  # the math boxes by the GRID-pt squares they reach
        for b in math[index] if index < len(math) else []:
            for gx in range(int((b[0] - OVERLAP) // GRID), int((b[2] + OVERLAP) // GRID) + 1):
                for gy in range(int((b[1] - OVERLAP) // GRID), int((b[3] + OVERLAP) // GRID) + 1):
                    grid.setdefault((gx, gy), []).append(b)

        def in_math(w: Word) -> bool:
            cx, cy = (w[1] + w[3]) / 2, (w[2] + w[4]) / 2
            return any(b[0] - OVERLAP <= cx <= b[2] + OVERLAP and b[1] - OVERLAP <= cy <= b[3] + OVERLAP
                       for b in grid.get((int(cx // GRID), int(cy // GRID)), []))

        body = [w for w in words if w[0]
                and not (w[2] >= y1 - SLACK and w[0] in page_number)
                and not (w[4] <= y0 + SLACK and w[0] in notice_words)]
        maths = {id(w) for w in body if in_math(w)}
        for w in body:
            middle = (w[2] + w[4]) / 2
            banded = any(start - SLACK <= middle <= end + SLACK for start, end in wide.get(index + 1, []))
            a0, a1 = (min(x0, TRIM_SAFE), max(x1, width - TRIM_SAFE)) if banded else (x0, x1)
            drop = MATH_DROP if id(w) in maths else 0.0
            if w[1] < a0 - SLACK or w[3] > a1 + SLACK or not y0 - SLACK <= middle <= y1 + SLACK + drop:
                outside.append(f"page {index + 1}: word {w[0]!r} at x {w[1]:.1f}-{w[3]:.1f}, y {w[2]:.1f}-{w[4]:.1f} pt "
                               f"lies outside the text block (x {a0:.1f}-{a1:.1f}, y {y0:.1f}-{y1:.1f} pt)")
        ordered = sorted(body, key=lambda w: w[1])
        for a, p in enumerate(ordered):  # a sweep across the page: only words starting before p ends can meet it
            for q in ordered[a + 1:]:
                if q[1] >= p[3] - OVERLAP:
                    break
                if id(p) in maths and id(q) in maths:
                    continue
                dx = min(p[3], q[3]) - max(p[1], q[1])
                dy = min(p[4], q[4]) - max(p[2], q[2])
                if dx > OVERLAP and dy > OVERLAP:
                    overlaps.append(f"page {index + 1}: words {p[0]!r} and {q[0]!r} overlap by {dx:.1f} x {dy:.1f} pt")
    faults: list[str] = []
    for found in (outside, overlaps):
        faults += found[:SHOWN] + ([f"... and {len(found) - SHOWN} more like it"] if len(found) > SHOWN else [])
    return faults


def missing_glyphs(text: str, pdf: Path, exe: Path) -> list[str]:
    """Each character of the document's printed text that no font drew, as `U+1E4D0 NAG MUNDARI LETTER O`: a
    printable character outside ASCII that is absent from the PDF's text layer. The printed text is Pandoc's plain
    rendering of the Markdown `text`, so a character that never prints (a link's target, an image's path, an
    attribute) is not looked for. Typst sets a character no font has as the font's .notdef glyph, which carries no
    text; a character a fallback font draws is there. Both sides are compared in compatibility form (NFKC), since
    Typst sets a letter in an equation as its mathematical alphanumeric and a ligature stands for its letters."""
    layer = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True,
                           errors="replace").stdout
    drawn = set(unicodedata.normalize("NFKC", layer))
    printed = subprocess.run([str(exe), "pandoc", "--from", "markdown", "--to", "plain"],
                             input=text, capture_output=True, text=True, check=True).stdout
    return [f"missing glyph U+{ord(c):04X} {unicodedata.name(c, 'with no Unicode name')}: no font draws it"
            for c in sorted(set(printed)) if ord(c) > 127 and unicodedata.category(c)[0] not in "ZCM"
            and not set(unicodedata.normalize("NFKC", c)) <= drawn]


LINKS_JS = """var doc = Document.openDocument(scriptArgs[0]);
var links = 0;
for (var i = 0; i < doc.countPages(); i++) links += doc.loadPage(i).getLinks().length;
print(doc.countPages() + " " + links);
"""


def pages_and_links(pdf: Path, work: Path) -> tuple[int, int]:
    """The PDF's page count and its link annotations, counted with MuPDF's `mutool run`."""
    script = work / "links.js"
    script.write_text(LINKS_JS)
    run = subprocess.run(["mutool", "run", str(script), str(pdf)], capture_output=True, text=True, check=True)
    pages, links = run.stdout.split()[-2:]
    return int(pages), int(links)


def contents_entries(text: str, metadata: dict[str, object]) -> int:
    """The `##` and `###` headings outside fenced code, where the format sets a contents list."""
    if metadata.get("contents") is False:
        return 0
    fenced, headings = False, 0
    for line in text.splitlines():
        fenced = fenced != line.startswith(("```", "~~~"))
        headings += not fenced and re.match(r"#{2,3} ", line) is not None
    return headings


def joined(sources: list[Path], work: Path) -> tuple[str, list[str]]:
    """The sources' text joined with page breaks, and the faults of the images they name, each copied into `work`
    from its source's folder."""
    texts: list[str] = []
    faults: list[str] = []
    for src in sources:
        text = src.read_text(encoding="utf-8")
        for found in IMAGE.finditer(text):
            path = found.group(2)
            origin = src.parent / path
            target = work / path
            if Path(path).is_absolute() or ".." in Path(path).parts or "://" in path:
                faults.append(f"{src}: image {path}: give a path inside the source's folder")
            elif not origin.is_file():
                faults.append(f"{src}: image {path}: no such file {origin}")
            elif target.exists() and target.read_bytes() != origin.read_bytes():
                faults.append(f"{src}: image {path}: another source names a different file by the same path")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origin, target)
        texts.append(text)
    return PAGE_BREAK.join(texts), faults


FINISH_JS = """var doc = Document.openDocument(scriptArgs[0]);
var root = doc.getTrailer().get("Root");
var names = root.get("Names");
var files = names ? names.get("EmbeddedFiles") : null;
var list = files ? files.get("Names") : null;
if (list) {
  for (var i = list.length - 2; i >= 0; i -= 2) {
    if (list.get(i).asString() == "doc-wide.json") {
      list.get(i + 1).get("EF").get("F").readStream().save(scriptArgs[2]);
      list.delete(i + 1);
      list.delete(i);
    }
  }
  if (list.length == 0) names.delete("EmbeddedFiles");
}
var prefs = root.get("ViewerPreferences");
if (!prefs) { prefs = doc.newDictionary(); root.put("ViewerPreferences", prefs); }
prefs.put("DisplayDocTitle", true);
doc.save(scriptArgs[1], "garbage");
"""


def finish(made: Path, work: Path) -> tuple[Path, dict[int, list[tuple[float, float]]], set[int]]:
    """The PDF with DisplayDocTitle true and the format's attachment doc-wide.json taken out, the bands down each
    page (from, to, in pt) of the tables that attachment marks as run into the margins, and the pages it marks as
    drawn whole from another PDF (the format's doc-placed), by MuPDF's `mutool run`."""
    script, marks, done = work / "finish.js", work / "doc-wide.json", work / "finished.pdf"
    script.write_text(FINISH_JS)
    subprocess.run(["mutool", "run", str(script), str(made), str(done), str(marks)], capture_output=True, text=True,
                   check=True)
    bands: dict[int, list[tuple[float, float]]] = {}
    rows = cast(list[list[object]], json.loads(marks.read_text())) if marks.is_file() else []
    placed = {int(cast(int, row[1])) for row in rows if row[0] == "placed"}
    rows = [row for row in rows if row[0] != "placed"]
    for start, end in zip(rows[0::2], rows[1::2]):  # in the document's order: start, end, start, end ...
        (p0, y0), (p1, y1) = (int(cast(int, start[1])), float(cast(float, start[2]))), \
            (int(cast(int, end[1])), float(cast(float, end[2])))
        for page in range(p0, p1 + 1):
            bands.setdefault(page, []).append((y0 if page == p0 else float("-inf"), y1 if page == p1 else float("inf")))
    return done, bands, placed


def render(sources: list[Path], out: Path, *, to: str = "pdf", notice: str = "",
           metadata: dict[str, object] | None = None, format_dir: Path | None = None,
           fmt: str = "doc-typst") -> Report:
    """Render `sources` to `out` (the module's docstring); raises Refused, and writes nothing at `out`, on any fault."""
    if to not in EXTENSION:
        raise Refused([f"--to {to}: give pdf, docx or html"])
    needed = ["pdftotext", "mutool"] if to == "pdf" else []
    absent = [tool for tool in needed if shutil.which(tool) is None]
    if absent:
        raise Refused([f"{tool} is not installed; the PDF's checks need it (poppler-utils, mupdf-tools)"
                       for tool in absent])
    try:
        exe = binary()
    except Refusal as e:
        raise Refused([str(e)]) from None
    meta: dict[str, object] = dict(metadata or {})
    tables = ""
    if to == "pdf":
        margin = meta.get("margin", {})
        if isinstance(margin, dict) and "rest" not in margin:  # a side the metadata leaves out is the default's
            meta["margin"] = DEFAULT_MARGIN | cast(dict[str, object], margin)
        block_margins = margins(meta["margin"])
        share = meta.get("table-size", TABLE_SHARE)
        if isinstance(share, bool) or not isinstance(share, int | float) or share <= 0:
            raise Refused([f"table-size {share!r}: give a share of the body's size, a number such as 0.75"])
        stretch = meta.get("table-stretch")
        if stretch is not None and (isinstance(stretch, bool) or not isinstance(stretch, int | float) or stretch <= 0):
            raise Refused([f"table-stretch {stretch!r}: give LaTeX's \\arraystretch, a number such as 1.15"])
        tables = (f"```{{=typst}}\n#doc-tables(share: {share}, floor: {TABLE_FLOOR}pt, trim: {TRIM_SAFE}pt, "
                  f"left: {block_margins[0]}pt, right: {block_margins[2]}pt, "
                  f"stretch: {'none' if stretch is None else stretch})\n```\n\n")
        if notice:
            # In the header, before the template's title block, so the notice heads its first page too
            quoted = notice.replace("\\", "\\\\").replace('"', '\\"')
            given = meta.get("include-in-header", [])  # Quarto adds these to the format's own
            meta["include-in-header"] = [*(cast(list[object], given) if isinstance(given, list) else [given]),
                                         {"text": f'#set page(header: align(center, text(size: 8pt, "{quoted}")))'}]
    else:
        block_margins = (0.0, 0.0, 0.0, 0.0)
    if "bibliography" in meta:
        meta.setdefault("link-citations", True)
    if to == "html":
        meta.setdefault("embed-resources", True)  # one file at `out`, its images inside it
    with tempfile.TemporaryDirectory(prefix="render-") as tmp:
        work = Path(tmp)
        text, faults = joined(sources, work)
        text = crossrefs(text, typst=to == "pdf")
        if faults:
            raise Refused(faults)
        (work / "document.md").write_text(tables + text, encoding="utf-8")
        (work / "metadata.json").write_text(json.dumps(meta))
        (work / "_extensions").symlink_to((format_dir or FORMAT_DIR).resolve() / "_extensions")
        target = fmt if to == "pdf" else to
        run = subprocess.run([str(exe), "render", "document.md", "--to", target, "--metadata-file", "metadata.json"],
                             cwd=work, capture_output=True, text=True, errors="replace")
        output = [ANSI.sub("", line).rstrip() for line in (run.stdout + run.stderr).splitlines()]
        made = work / f"document.{EXTENSION[to]}"
        if run.returncode != 0 or not made.is_file():
            # Typst's own message, once, where it gave one (a panic of the format's names the table or equation);
            # otherwise Quarto's error lines, or its last lines
            errors = [re.sub(r"^.*?error: ", "", line).strip() for line in output if "error: " in line]
            errors = errors or [line.strip() for line in output if line.lstrip().startswith("ERROR")]
            raise Refused(list(dict.fromkeys(errors)) or output[-20:] or [f"quarto exited {run.returncode}"])
        faults = [line.strip() for line in output if "Unable to resolve crossref" in line
                  or "unknown font family" in line or "did not converge" in line]
        warnings = tuple(dict.fromkeys(line.split(WARNING, 1)[1] for line in output if WARNING in line))
        pages = links = 0
        if to == "pdf":
            made, wide, placed = finish(made, work)
            faults += overflow(made, block_margins, notice, wide, placed) + missing_glyphs(text, made, exe)
            pages, links = pages_and_links(made, work)
        if faults:
            raise Refused(faults)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(made, out)
        return Report(pages, contents_entries(text, meta) if to == "pdf" else 0, links, warnings)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render Markdown to PDF, docx or html through the shared format.")
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--to", choices=sorted(EXTENSION), default="pdf")
    parser.add_argument("--notice", default="")
    parser.add_argument("--metadata", type=Path, help="a JSON file of Quarto metadata")
    parser.add_argument("--format-dir", type=Path, help="a folder holding a project's own _extensions")
    parser.add_argument("--format", default="doc-typst", help="the format's name, with --format-dir")
    args = parser.parse_args(argv)
    sources: list[Path] = args.sources
    out: Path = args.out
    metadata: dict[str, object] | None = None
    try:
        if args.metadata is not None:
            loaded: object = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise Refused([f"{args.metadata}: the metadata must be a JSON object"])
            metadata = {str(k): v for k, v in cast(dict[object, object], loaded).items()}
        report = render(sources, out, to=args.to, notice=args.notice, metadata=metadata,
                        format_dir=args.format_dir, fmt=args.format)
    except Refused as refusal:
        for fault in refusal.faults:
            print(f"refused: {fault}")
        print(f"no file written at {out}")
        return 1
    for warning in report.warnings:
        print(f"warning: {warning}")
    print(f"{out}: {report.pages} pages, {report.contents} contents entries, {report.links} links")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
