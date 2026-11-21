"""Typeset a case's documents as PDFs (roadmap R10), and measure a PDF's pages (notes/pdf_layout_review.md).

Run from the repository root:

    .venv/bin/python tools/typeset.py [--quarto] [--language <tag>] [--notice TEXT] cases/<case>
    .venv/bin/python tools/typeset.py --measure <pdf> [<pdf> ...] [--sheets <folder>]

Each `<case>/documents/*.md` except `*_template.md` is built with `lualatex` and the `markdown` package, without
shell escape, in a temporary folder that is removed afterwards. Its PDF is written to
`<case>/documents/drafts/<identifier>.pdf`, the identifier the case's short name, the document's name and the draft's
version (`demo_1page_v2.0`, tools/document_names.py, which keeps the case's log `<case>/versions.toml`), and the same
bytes beside the source with its stem (the paper with the summary in front, below, only in drafts/). Before any
build it prints the version, pending or committed, and the hash of the inputs; it refuses the case, with one line
and no PDF, when the log refuses or two documents share a name.
The layout is LaTeX, in `tools/typeset_layout/`: `summary.tex` for `executive_summary.md`, `document.tex`
for every other document, both loading `typeset-common.sty`. With `--language` ko, ja or zh it uses
`summary-cjk.tex` and `document-cjk.tex`, which load `typeset-cjk.sty` (A4, Latin in Pagella, Heros and Latin
Modern Mono, every other character in the Noto CJK fonts); with `en` or no
`--language` the English layout: the text in T1 fonts, the title, headings and box titles in Lato and icons from
the Tabler icon font, both stored in `tools/typeset_layout/assets/` (its README). Any other tag is refused: no
layout has been built for it.

Per document it prints the page count (`pdfinfo`), every LaTeX error, every "Missing character" line (a character
the fonts lack, which lualatex drops with no error), every overfull box with its width and the text it holds, every
float too large for its page (reported among the overfull boxes, since it runs off the page's foot unboxed), and
every font substitution. It exits 1 if a document has an error or a missing character, or if the case has no
document; overfull boxes and the page count are for the layout reviewer (`.claude/agents/pdf-layout.md`).

The executive summary's title and the paragraph under it, its dateline (unless that paragraph opens in bold, as
"**The answer.**" would), are set across the page and the rest in two columns. Its body type is the largest of
11, 10.5, 10 and 9.5 pt at which it fits one page (copyfitting): it is built at each in turn, and the size used
is printed. A summary that does not fit at 9.5 pt is too long, a fault of content for its author.

The policy paper, `policy_paper.md`, opens on a cover page of its own (document.tex): its title, the dateline,
a `::: credit` block if one directly follows the dateline, and the title's icon drawn large, under a blue band.
The body starts on page 2. Every other document keeps its title at the head of its first page.

The paper with the summary in front. When `<case>/documents/` holds both `executive_summary.md` and
`policy_paper.md`, in the English layout, one more PDF is written to
`drafts/`, its short name `paper_with_summary` (`demo_paper_with_summary_v2.0`): the summary's page, bookmarked
"Summary", then the paper with no cover, its title at the head of page 2, then the contents list and the body. It
is made in one LuaLaTeX run of the paper, which places the summary built again with an empty notice as its first
page (document.tex, `typeset-front.pdf` in the build folder), so the paper's links and bookmarks hold and the
joined file's own notice is drawn once on every page. Joining finished PDFs broke the links or the file. With
`--quarto` the same is made in one Typst run of the paper, its first page the summary built again with an empty
notice and drawn whole as that page's background, under a hidden heading "Summary" that is its bookmark, beside
the paper's sections.

Contents, bookmarks and properties. Every PDF's Title is its first `#` heading's words and its language is named
(`en-US`, or the `--language` tag). In the English layout each `##` and `###` heading is a bookmark, the `###` ones
under their `##`, and every document set by document.tex has a contents list of those headings, under "Contents"
before its first `##` heading, each line a link to its heading with its page number; LaTeX is run again until the
list's page numbers settle. The Quarto route does the same with Typst's outline (house format, contents.lua).

Cross-references (roadmap item 2.69). Both routes read Quarto's labels: a heading `## 4 Results {#sec-results}`,
a figure `![Its caption.](figures/x.png){#fig-x}`, and a table by the caption line straight after it, `: Its
caption. {#tbl-x}`; prose refers to each as `@sec-results`, `@fig-x` or `@tbl-x`. Each reference is a link to its
target, printed "Section 4" for a heading that opens with its number and the heading's words for one that does not,
and "Figure N" or "Table N" for the labelled figures and tables in order, whose captions get the same "Figure N."
or "Table N." in front (crossrefs()). A reference, or an internal link `[...](#name)`, whose label no attribute
in the document carries is an error naming it, and the document gets no PDF. After each document built, the report
prints a line `<stem>: N contents entries, N bookmarks, N links`: the `##` and `###` headings where the layout sets
a contents list, the PDF's outline items, and its link annotations, the last two counted with MuPDF (`mutool`), or
said to be not counted where it is not installed.
The CJK layouts read no heading attributes, so a heading label there prints as typed.

Icons. A heading may end in Pandoc's attribute syntax naming a Tabler icon, `## 3 Effects on health {icon=heart}`;
the icon prints before the heading's text in its colour and size (on the policy paper's title, large on the
cover). A name not in `tools/typeset_layout/assets/tabler-icons/icons.json` stops the build with an error naming
it; `tools/icon_search.py WORD ...` finds names. The English layout reads every name from a file this script
writes from that index, `typeset-icons.tex`. The CJK layouts draw no icons.

Boxes. A document marks a box with a fenced div, Pandoc's syntax: a line `::: key-findings`, the box's blocks,
and a line `:::`. Three kinds are set, each a shaded box with a coloured rule down its left side:

    ::: key-findings      the answer and its range, at the top of the summary or the paper
    ::: callout           what a reader must not miss: a caveat, what is left out, the action wanted
    ::: worked-example    the one unit rebuilt to the headline
    ::: credit            no box: the tool's credit line, in small grey type (the project's CLAUDE.md)

The box's title is its first words in bold ("**Key findings.**"), set in Lato after a fixed icon: key-findings
`bulb`, callout `alert-triangle`, worked-example `calculator`; the credit has none. Any other kind is refused. `::: {.callout}`
is read the same. A blank line is put before and after each fence line, since without one a list's last item
would swallow the closing `:::`.

Audience editions (notes/audience_layer.md). Each `<case>/documents/audience/<key>/*.md` except `*_template.md`
and `crosswalk.md` is built as the document of its name is, its PDF beside it, with the colours and the heading
font of the profile `audiences/<key>.toml`: the colour tokens of its `[design.color]` by role (accent,
accent_caveat, caveat_ground, panel, neutral, rule, ink, ink_second) and `[design.font.heading]` (lato, pagella,
termes or schola), written to `typeset-theme.tex` in the build folder, which typeset-boxes.sty reads after its
own colours. A token left out keeps the base value, and no other document gets the file. The profile's
`[design.icons] cover`, a Tabler name or a word (the first name `tools/icon_search.py` lists for it), is drawn on the
policy paper's cover as a title's `{icon=NAME}` is, unless the title names an icon itself. `[design.imagery]` is
guidance in words that no tool reads; `[design.charts]` is the figures' rc overlay (tools/figures.py), read here
only to refuse a key that is not a matplotlib rc name. The build of such a document is refused, with an error line,
for a missing profile, an unknown token or key, a cover word no icon matches, or a contrast under 4.5 to 1 between
the accent and white or between the ink and a box's ground, the error naming the pair and both colours. With
`--quarto`, an audience edition's documents go through the Quarto route instead, its theme a `_brand.yml` written
from the same profile with the same checks (brand_yml()).

Notice. Every page of every document, the policy paper's cover included, carries its stamp in small grey sans
type centred in the top margin (roadmap item 2.47, 2.66), in white on the cover's band: `--notice TEXT` if given,
the document's identifier and the draft's date, joined by " | " ("Draft for comment | demo_1page_v2.0 | 13
November 2026"). The stamp is written, its LaTeX special characters escaped, to `typeset-notice.tex` in the build
folder, which typeset-boxes.sty reads; it is drawn over the page after the text is set, so the text block, the
margins and the summary's copyfit do not change.

Quarto (layout migration steps 4 to 9). With `--quarto`, every document, of whatever name, is rendered instead by the
pinned Quarto (tools/quarto_setup.py) through Typst and the house format,
`tools/house_format/`: the prepared text and copies of its images (a path that is absolute, holds `..` or names
no file is an error) in a temporary folder, the stamp passed in a metadata file. The policy paper in the English
layout opens on a cover page of its own as on the LaTeX route, drawn by the house format's house-cover: the blue
band with the notice in white, the title's icon or the profile's cover icon from the stored Tabler font, the title,
the dateline and a credit block at the page's foot, each line's baseline where TeX puts it (cover_typst()). The stored
fonts, Lato and the Tabler icons in `tools/typeset_layout/assets/`, are linked into the build folder and named in
`font-paths`, so the route takes no Lato from the system. Every other heading's `{icon=NAME}` is drawn before its words,
as on the LaTeX route, and left out of the contents list and the bookmarks (heading_icons()); no title is a bookmark.
The page notice is set in TeX Gyre Heros, the LaTeX route's sans. A display equation labelled `$$ ... $$ {#eq-name}` is numbered (1), (2), ...
at its right; one wider than the text block, less its number's room on each side, is broken into one line per part
at its top-level spaces of a quad or more and set in smaller type, down to 80%, until its widest line fits, its
number at full size; one that still does not fit is an error naming its label (the format's header). A table column whose body cells are all numbers is right-aligned (numbers.lua). A
table is set in LaTeX's footnotesize (9 pt on the 11 pt documents, 0.85 of the summary's body), its columns sized by tabulary's
rule with no column narrower than its longest word, a cell spanning rows counted in the columns it covers, so no word
in a cell is broken and the table keeps to the text width; one whose longest words do not fit is set in scriptsize,
8/9 of that, with narrower insets (the format's header). The paper and the appendix are set as document.tex sets them:
TeX Gyre Pagella at 11 pt on a text block 6 in wide, the top margin 0.75 in and the bottom 1 in, about 85 characters
a line (QUARTO_DOCUMENT). In the English layout the title and headings of every document but verse are set in Lato
bold, or the audience profile's heading font, the fourth to sixth levels in its italic, as typeset-common.sty sets them
(heading_typst()); a font the document names that is not installed is an error naming it, since Typst would set
another in its place. The executive summary is set in TeX Gyre Heros, as summary.tex sets it, in two columns on
half-inch margins with no page number, its title, its dateline (as split_head() takes it) and a key-findings box straight after them across both at
the top of the page (columns.lua), its body type the largest of 10.5, 10 and 9.5 pt at which it fits one page,
rendered at each in turn and the size used printed; one that does not fit at 9.5 pt is written at 9.5 pt on more
pages, a fault of content for its author. It has no contents list. Its columns are then balanced, as flushend balances them: rendered again in
columns as short as hold the body (the format's house-balance), with more slack (QUARTO_BALANCE) where the page would
overrun, until the page holds the body and its columns, measured in the PDF, end within two lines of each other
(QUARTO_LEVEL); the report says with how much slack and how far apart they end, or that they could not be balanced and
how far apart they end unbalanced. An audience edition's theme
(Audience editions, above) reaches the boxes and the credit through `_brand.yml`: each box's rule and icon and its
title band take the profile's roles as on the LaTeX route, its text the ink, the credit ink_second, the headings the
heading font, the cover the accent, ink and ink_second and the heading font. The summary's head has the 0.6 pt rule
under its title and dateline that summary.tex draws (columns.lua). Verse documents, `documents/verse/*.md`, go through
this route too, set as verse.tex sets them (QUARTO_VERSE and the format's verse.lua): the title and headings in Lato
bold, the verse in two columns, those of a run's last page balanced. With `--language` ko, ja or zh
the documents are set on A4 as document-cjk.tex and summary-cjk.tex set them, with `lang` and its region, Latin in the
English faces and the rest in the Noto CJK fonts, Japanese with JLREQ's quarter em between kana or kanji and Latin,
Korean breaking only between words, headings in the sans faces and a document's title centred (cjk_typst()). A
character no font draws (missing_glyphs()) is an error naming its code point and Unicode name, and the document gets
no PDF. The flag and the house format enter the inputs hash.

With --measure it builds nothing: for each PDF it prints the page count, the side margins (the median over pages
of the distance from each edge to the nearest word), the median characters in a full line of text, the median
share of the page inside the text's bounding box, and the share of quarter-inch squares with no dark pixel
(median, range, and the emptiest pages), the measures of notes/pdf_layout_review.md 1. With --sheets it writes
a thumbnail sheet of each PDF's pages, `<stem>_pages.png`, into that folder, to look at all the pages at once.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import tomllib
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, cast

import document_names
import figures
import icon_search
import quarto_setup

LAYOUT = Path(__file__).resolve().parent / "typeset_layout"
ICONS = LAYOUT / "assets" / "tabler-icons" / "icons.json"


def icon_table() -> str:
    """typeset-icons.tex: a line `\\typeset@deficon{NAME}{CODE}` for each icon of the Tabler index with an outline
    glyph, CODE its code point in hexadecimal, in capitals as TeX reads a hexadecimal number."""
    index = json.loads(ICONS.read_text())
    return "".join(rf"\typeset@deficon{{{name}}}{{{icon['styles']['outline']['unicode'].upper()}}}" + "\n"
                   for name, icon in index.items() if "outline" in icon["styles"])


# Each language's Noto CJK region, and the penalty on a line break between two characters: Korean breaks at the
# spaces between words (klreq 5.2) and only a run too long for a line between syllables; the others break anywhere.
CJK = {"ko": ("KR", 5000), "ja": ("JP", 0), "zh": ("SC", 0)}


def is_summary(md: Path) -> bool:
    return md.name == "executive_summary.md" and md.parent.name != "verse"


def is_cover(md: Path, language: str) -> bool:
    """Whether the document opens on a cover page: the policy paper, in the English layout (document.tex sets the
    cover when its head file exists)."""
    return md.name == "policy_paper.md" and md.parent.name != "verse" and language not in CJK


# The summary's body sizes in points, largest first, tried in turn until it fits one page (summary.tex).
SIZES = ("11", "10.5", "10", "9.5")


def layout_argument(md: Path, language: str, size: str | None = None) -> str:
    """What lualatex is given to run: the layout file, with the summary's body size and, for a CJK language, its
    two settings defined first."""
    name = "verse" if md.parent.name == "verse" else "summary" if is_summary(md) else "document"
    size_def = rf"\def\typesetsize{{{size}}}" if size else ""
    if language not in CJK:
        return size_def + rf"\input{{{name}.tex}}" if size_def else str(LAYOUT / f"{name}.tex")
    region, penalty = CJK[language]
    return (size_def + rf"\def\typesetlanguage{{{language}}}\def\typesetcjkregion{{{region}}}"
            rf"\def\typesetcjkpenalty{{{penalty}}}\input{{{name}-cjk.tex}}")

# An audience edition's theme (notes/audience_layer.md 3.4). A profile, `audiences/<key>.toml`, overrides colours of
# typeset-boxes.sty by role, may name a heading font (a TeX Gyre family of TeX Live and its bold face, which replace
# Lato and Lato Black) and a cover icon; its imagery and chart tables carry only the keys below. The body type does
# not change.
AUDIENCES = figures.AUDIENCES
PROVENANCE = ("basis", "evidence")
IMAGERY = ("photograph", "cover")
THEME_COLOURS = {"accent": "typesetblue", "accent_caveat": "typesetwarnline", "caveat_ground": "typesetwarn",
                 "panel": "typesetpanel", "neutral": "typesetgray", "rule": "typesetrule", "ink": "typesetink",
                 "ink_second": "typesetinksecond"}
THEME_FONTS = {"lato": None, "pagella": ("TeX Gyre Pagella", "texgyrepagella-bold.otf"),
               "termes": ("TeX Gyre Termes", "texgyretermes-bold.otf"),
               "schola": ("TeX Gyre Schola", "texgyreschola-bold.otf")}


def contrast(one: str, other: str) -> float:
    """The contrast ratio of two colours written RRGGBB, by relative luminance (WCAG 2.2)."""
    def luminance(colour: str) -> float:
        red, green, blue = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                            for c in (int(colour[i:i + 2], 16) / 255 for i in (0, 2, 4)))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue
    high, low = sorted((luminance(one), luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def profile_design(md: Path) -> dict[str, dict[str, Any]]:
    """The `[design]` table of the profile of an audience edition's document; an empty table for any other document.
    Raises ValueError for a missing profile."""
    if md.parent.parent.name != "audience":
        return {}
    profile = AUDIENCES / f"{md.parent.name}.toml"
    if not profile.exists():
        raise ValueError(f"no audience profile {profile}")
    return cast("dict[str, dict[str, Any]]", tomllib.loads(profile.read_text()).get("design", {}))


def cover_icon(md: Path) -> str:
    """The Tabler name of the profile's `[design.icons] cover`: the word itself where it is a name, else the first
    name icon_search lists for it; the empty string where the key is absent or empty. Raises ValueError for a word
    no icon matches."""
    word = str(profile_design(md).get("icons", {}).get("cover", "")).strip()
    if not word or word in json.loads(ICONS.read_text()):
        return word
    found = icon_search.search([word])
    if not found:
        raise ValueError(f"design.icons.cover = {word!r}: no Tabler icon matches it (tools/icon_search.py)")
    return found[0].split()[0]


def with_cover_icon(text: str, name: str) -> str:
    """The text with `icon=NAME` among its title's attributes, unless `name` is empty or the title names an icon."""
    def put(m: re.Match[str]) -> str:
        attributes = (m.group(2) or "{}")[1:-1].strip()
        if re.search(r"(^|\s)icon=", attributes):
            return m.group(0)
        return f"{m.group(1)} {{{(attributes + ' ') if attributes else ''}icon={name}}}"
    if not name:
        return text
    lines = text.split("\n")
    fenced = False
    for i, line in enumerate(lines):
        if re.match(r"\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if not fenced and (m := re.match(r"^(# .*?)[ \t]*(\{[^}]*\})?[ \t]*$", line)):
            lines[i] = put(m)
            break
    return "\n".join(lines)


def theme(md: Path) -> tuple[dict[str, str], str]:
    """An audience edition's theme, read from its profile and checked: its colours by role, each `RRGGBB` in capitals,
    and its heading font's key of THEME_FONTS (`lato`, the base, where it names none). Raises ValueError for a missing
    profile, a token or key this function does not know (a chart key that is not a matplotlib rc name among them), a
    cover word no icon matches, and an accent on white or the ink on a box's ground under 4.5 to 1, the least contrast
    for text (WCAG 2.2, 1.4.3), naming each such pair and its colours."""
    profile = AUDIENCES / f"{md.parent.name}.toml"
    tokens = profile_design(md)
    unknown = [f"design.{part}" for part in tokens if part not in ("color", "font", "icons", "imagery", "charts")]
    unknown += [f"design.icons.{key}" for key in tokens.get("icons", {}) if key not in ("cover", *PROVENANCE)]
    unknown += [f"design.imagery.{key}" for key in tokens.get("imagery", {}) if key not in (*IMAGERY, *PROVENANCE)]
    try:
        figures.chart_rc(tokens.get("charts", {}))
    except ValueError as refusal:
        unknown.append(str(refusal))
    try:
        cover_icon(md)
    except ValueError as refusal:
        unknown.append(str(refusal))
    colours: dict[str, str] = {}
    for name, token in tokens.get("color", {}).items():
        colours[name] = str(token.get("value", "")).lstrip("#").upper()
        if name not in THEME_COLOURS or not re.fullmatch(r"[0-9A-F]{6}", colours[name]):
            unknown.append(f"design.color.{name} = {token.get('value')!r}")
    fonts = tokens.get("font", {})
    heading = str(fonts.get("heading", {}).get("value", "lato"))
    unknown += [f"design.font.{name}" for name in fonts if name != "heading"]
    if heading not in THEME_FONTS:
        unknown.append(f"design.font.heading = {heading!r}")
    if unknown:
        raise ValueError(f"{profile}: unknown design token: {', '.join(unknown)}")
    pairs = [("accent", "FFFFFF"), ("panel", colours.get("ink", "0B0B0B")), ("caveat_ground", colours.get("ink", "0B0B0B"))]
    low = [f"{name} #{colours[name]} with #{other} is {contrast(colours[name], other):.2f}"
           for name, other in pairs if name in colours and contrast(colours[name], other) < 4.5]
    if low:
        raise ValueError(f"{profile}: contrast under 4.5 to 1: {'; '.join(low)}")
    return colours, heading


def theme_tex(md: Path, language: str) -> str:
    """typeset-theme.tex for a document of an audience edition, `documents/audience/<key>/<name>.md`: a
    `\\definecolor` line for each colour its profile overrides and, in the English layout, two lines for its heading
    font. The empty string for any other document and for a profile that overrides nothing; no file is then written.
    Raises ValueError as theme() does."""
    if not profile_design(md):
        return ""
    colours, heading = theme(md)
    lines = [rf"\definecolor{{{THEME_COLOURS[name]}}}{{HTML}}{{{value}}}" for name, value in colours.items()]
    font = THEME_FONTS[heading]
    if font and language not in CJK:
        lines += [rf"\renewfontfamily\typesetlato{{{font[0]}}}[Ligatures=TeX]",
                  rf"\renewfontface\typesetlatoblack{{{font[1]}}}"]
    return "".join(line + "\n" for line in lines)


def brand_yml(md: Path) -> str:
    """_brand.yml for a document of an audience edition on the Quarto route (layout migration step 7), in place of
    theme_tex(): the profile's colours as the brand's palette, `#RRGGBB` by the role names of THEME_COLOURS, which the
    house format's boxes and credit read (its header, house-callout), and its heading font, where it is not the base
    Lato, as the brand's heading family, which Quarto sets on every heading. Written as JSON, which YAML reads. The
    empty string for any other document and for a profile that sets neither. Raises ValueError as theme() does: the
    same checks, the contrast check among them, hold on this route."""
    if not profile_design(md):
        return ""
    colours, heading = theme(md)
    brand: dict[str, object] = {}
    if colours:
        brand["color"] = {"palette": {name: f"#{value}" for name, value in colours.items()}}
    font = THEME_FONTS[heading]
    if font:
        brand["typography"] = {"headings": {"family": font[0]}}
    return json.dumps(brand, indent=2) + "\n" if brand else ""


# What each LaTeX special character becomes in the notice, so that it prints as typed.
TEX_ESCAPES = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
               "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def notice_tex(notice: str) -> str:
    """typeset-notice.tex: `\\typesetnotice` defined as the notice, on one line, its special characters escaped."""
    escaped = re.sub(r"[\\{}&%$#_~^]", lambda m: TEX_ESCAPES[m.group(0)], " ".join(notice.split()))
    return rf"\def\typesetnotice{{{escaped}}}" + "\n"


# A decimal-numbered item, "2.3 Wages ...", or, with three or more levels, "2.3.1 mean ...".
ITEM = re.compile(r"^\d+(\.\d+)+ (?=[^a-z])|^\d+(\.\d+){2,} ")
# A number and its unit, which a line of text should not part ("$715" / "million", "68.7 per" / "cent").
UNIT = re.compile(r"(\d) (million|billion|trillion|per cent)\b")
# A straight quote that opens: at the start of a line or after a space, an opening mark or =, before a character or
# the line's end; any other " closes. A
# straight ' that opens becomes a left single quote; any other ' is already set as an apostrophe or closing quote.
OPENS = re.compile(r"(?:(?<=^)|(?<=[\s(\[{\u2014\u2013/*>=-]))(\"|')(?=\S|$)")
# A straight double quote that closes; one escaped with a backslash, `\"`, is a literal mark Markdown sets as typed.
CLOSES = re.compile(r'(?<!\\)"')
# A fenced div's fence, `::: callout`, `::: {.callout}` or the closing `:::`, and a bare word's class.
FENCE = re.compile(r"^:{3,}(\s.*)?$")
BARE_CLASS = re.compile(r"^(:{3,})\s*([A-Za-z][\w-]*)\s*$")
CREDIT = re.compile(r"^:{3,}\s*\{\.credit\}\s*$")  # a credit block's opening fence, as prepare() writes it
URL = re.compile(r"(?<!\]\()(?<!<)\bhttps?://[^\s<>()\[\]`]+")
# An image's line, `![Figure N. Its caption.](path)`, and its path, the last `](` on the line opening it.
IMAGE = re.compile(r"^(!\[.*\]\()([^)\s]+)", re.M)


def prepare(text: str) -> str:
    """The Markdown as the layout reads it. Outside fenced code, a line that is only an HTML comment (a case's
    `<!-- part: NAME -->` markers) is dropped, since the layout reads HTML as text; a decimal-numbered item that
    follows a line of text starts a paragraph of its own, as it would in a numbered document, where Markdown would
    join it to the line before; a bare web address outside code spans becomes an autolink, which the layout sets
    so that it breaks across lines without a hyphen; a number in a line of text is tied to its unit by no-break
    spaces; and straight quotes outside code are made typographic, opening or closing by what comes before them."""
    out: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced:
            if re.fullmatch(r"\s*<!--.*-->\s*", line):
                continue
            if FENCE.match(line):  # a box's fence stands between blank lines (Boxes, above)
                if out and out[-1].strip():
                    out.append("")
                out.extend([BARE_CLASS.sub(r"\1 {.\2}", line), ""])
                continue
            if ITEM.match(line) and out and out[-1].strip() and not out[-1].startswith(("|", "#")):
                out.append("")
            parts = line.split("`")
            for i in range(0, len(parts), 2):  # the even pieces lie outside code spans
                parts[i] = URL.sub(lambda m: (lambda u, tail: f"<{u}>{tail}")(
                    m.group(0).rstrip(".,;:'\""), m.group(0)[len(m.group(0).rstrip(".,;:'\"")):]), parts[i])
                parts[i] = OPENS.sub(lambda m: "\u201c" if m.group(1) == '"' else "\u2018",
                                     parts[i] if i == 0 else "\x00" + parts[i])[0 if i == 0 else 1:]
                parts[i] = CLOSES.sub("\u201d", parts[i])
                if not line.startswith("|"):  # in a table's narrow column a cell may need that break
                    parts[i] = UNIT.sub(lambda m: f"{m.group(1)}\u00a0{m.group(2).replace(' ', chr(0xA0))}", parts[i])
            line = "`".join(parts)
        out.append(line)
    return "\n".join(out) + "\n"


# Cross-references (the module's docstring): a label in an attribute, a reference in prose, any identifier an
# internal link may name, and such a link.
LABEL = r"((?:sec|fig|tbl)-[\w-]*\w)"
HEADING_LABEL = re.compile(r"^#{2,6} (.*?)\s*\{[^}]*#" + LABEL + r"[^}]*\}\s*$")
ATTRIBUTE_ID = r"\{(?:[^}]*\s)?#"  # an attribute's identifier, anywhere among its attributes (Pandoc's syntax)
FIGURE_LABEL = re.compile(r"^!\[(.*)\](\([^)\s]+\))" + ATTRIBUTE_ID + LABEL + r"[^}]*\}\s*$")
TABLE_LABEL = re.compile(r"^: (.*?)\s*" + ATTRIBUTE_ID + LABEL + r"[^}]*\}\s*$")
REFERENCE = re.compile(r"(?<![\w@\\])@" + LABEL)
IDENTIFIER = re.compile(ATTRIBUTE_ID + r"([^\s}]+)")
INTERNAL_LINK = re.compile(r"\]\(#([^)\s]+)\)")


def crossrefs(text: str, latex: bool) -> str:
    """The prepared Markdown with its cross-references resolved, for either route. A reference `@sec-x`, `@fig-x`
    or `@tbl-x` becomes a link to its label, printed "Section 3" for a heading that opens with its number
    ("## 3 Effects {#sec-x}") and the heading's words for one that does not, and "Figure N" or "Table N" by the
    order of the labelled figures and tables; each labelled caption gets its "Figure N. " or "Table N. " in front.
    A figure's or a table's label becomes a link target at its caption's start, a span round the caption, since
    Typst places a target on the float itself where the float was written rather than where it prints. On the
    LaTeX route a table's caption line, which follows the table in Quarto's syntax, becomes the paragraph before it,
    where the layout keeps a caption with its table; on the Quarto route, which keeps a table's caption only on a
    float labelled `tbl-`, the float is labelled `<label>-float` and the target in the caption is Typst's own. A
    heading keeps its attribute on both routes (on the LaTeX route typeset-links.sty makes it a target). Raises
    ValueError naming every reference, and every internal link `[...](#name)`, whose label no attribute carries."""
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
        elif table and latex:
            caption, label = table.groups()
            while out and not out[-1].strip():
                out.pop()
            start = len(out)
            while start and out[start - 1].startswith("|"):
                start -= 1
            out[start:start] = [f"[{names[label]}. {caption}]{{#{label}}}", ""]
            continue
        elif table:
            caption, label = table.groups()
            line = f": `#metadata(none)<{label}>`{{=typst}}{names[label]}. {caption} {{#{label}-float}}"
        out.append(line)
    if missing:
        raise ValueError("no label for " + ", ".join(dict.fromkeys(missing))
                         + ": a reference or a link names a target no heading, figure, table or span carries")
    return "\n".join(out) + "\n"


def split_head(text: str, credit: bool = False) -> tuple[str, str]:
    """The head, its title line and the dateline paragraph under it, and the rest. The dateline is the first
    paragraph after the title unless it opens in bold or is a heading, list, table, box, quotation or image. With
    `credit` (the policy paper's cover), a `::: credit` block directly after the dateline is part of the head."""
    lines = text.splitlines()
    title = next((n for n, line in enumerate(lines) if line.startswith("# ")), None)
    if title is None:
        return "", text
    end = title + 1
    while end < len(lines) and not lines[end].strip():
        end += 1
    if end < len(lines) and not re.match(r"(#|:::|\||!\[|\d+\. |[-*+] |>|\*\*)", lines[end]):
        while end < len(lines) and lines[end].strip():
            end += 1
    else:
        end = title + 1
    if credit:
        start = end
        while start < len(lines) and not lines[start].strip():
            start += 1
        if start < len(lines) and CREDIT.match(lines[start]):
            close = next((n for n in range(start + 1, len(lines)) if FENCE.match(lines[n])), None)
            if close is not None:
                end = close + 1
    return "\n".join(lines[:end]) + "\n", "\n".join(lines[end:]) + "\n"


# A table's caption, the line "Table 3. Its words." before it (a labelled one's in a span, crossrefs()), which the layout
# keeps with its table.
CAPTION = re.compile(r"^\[?Table \d+\. ")


def write_pieces(md: Path, work: Path) -> None:
    """For a verse document, split it into `piece<N>.md` files (a heading, a table with its caption or an image
    alone, verse between; a blank line stays with the piece it is in) and write `body.tex`, which reads each across
    the full width or in columns (verse.tex), since a figure cannot float inside the columns; a heading's piece, with
    any heading straight after it ("## 4 Results" and "### 4.1 ..."), asks for room below it, so that no heading is
    left at a page's foot."""
    pieces: list[tuple[bool, list[str]]] = []
    for line in md.read_text().splitlines():
        if pieces and not line.strip():
            wide = pieces[-1][0]
        else:
            wide = line.startswith(("#", "|", "![")) or CAPTION.match(line) is not None
        after_heading = bool(pieces) and all(not x.strip() or x.startswith("#") for x in pieces[-1][1])
        if not pieces or wide != pieces[-1][0] or (line.startswith("#") and not after_heading):
            pieces.append((wide, []))
        pieces[-1][1].append(line)
    body: list[str] = []
    for number, (wide, lines) in enumerate(p for p in pieces if any(line.strip() for line in p[1])):
        (work / f"piece{number}.md").write_text("\n".join(lines) + "\n")
        kind = "heading" if lines[0].startswith("#") else "wide" if wide else "verse"
        body.append(rf"\{kind}piece{{piece{number}.md}}")
    (work / "body.tex").write_text("\n".join(body) + "\n")


def build(md: Path, language: str, stamp: str, target: Path, front: Path | None = None) -> bool:
    """Typeset one document, its page stamp `stamp`, to `target`; print its report; return whether it built with no
    error or missing character. With `front`, a one-page PDF, that page is set first with no cover (document.tex)."""
    try:
        theme = theme_tex(md, language)
        icon = cover_icon(md) if is_cover(md, language) else ""
        text = crossrefs(prepare(with_cover_icon(md.read_text(), icon)), latex=True)
    except ValueError as refusal:
        print(f"{md.stem}: error: {refusal}\n{md.stem}: no PDF written")
        return False
    with tempfile.TemporaryDirectory(prefix="typeset-") as tmp:
        work = Path(tmp)
        # A document's images by their paths relative to its own folder, `![...](figures/x.png)` or, from
        # documents/verse/, `../figures/x.png`, made absolute, since lualatex runs in a temporary folder.
        text = IMAGE.sub(lambda m: f"{m.group(1)}{(md.parent / m.group(2)).resolve()}", text)
        cover = is_cover(md, language) and front is None
        if is_summary(md) or cover:
            head, text = split_head(text, credit=cover)
            if head.strip():
                (work / f"{md.stem}-head.md").write_text(head)
        if front is not None:
            shutil.copyfile(front, work / "typeset-front.pdf")
            (work / "typeset-front-title.md").write_text(next((f"{line}\n" for line in text.splitlines()
                                                                if line.startswith("# ")), ""))
        (work / "typeset-icons.tex").write_text(icon_table())
        if theme:
            (work / "typeset-theme.tex").write_text(theme)
        (work / "typeset-notice.tex").write_text(notice_tex(stamp))
        (work / md.name).write_text(text)
        if md.parent.name == "verse":
            write_pieces(work / md.name, work)
        env = dict(os.environ, TEXINPUTS=f"{LAYOUT}{os.pathsep}", max_print_line="100000")
        pdf = work / f"{md.stem}.pdf"
        pages, size = 0, ""
        errors: list[str] = []
        missing: list[str] = []
        overfull: list[str] = []
        fonts: list[str] = []
        toc = work / f"{md.stem}.toc"
        for size in SIZES if is_summary(md) else ("",):
            # A layout with a contents list (document.tex) writes it to the .toc file and reads it in the next run,
            # so LaTeX runs again until that file is unchanged: twice, or more where the list moves a heading.
            runs = 0
            while True:
                before = toc.read_bytes() if toc.exists() else None
                run = subprocess.run(
                    ["lualatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                     f"-jobname={md.stem}", layout_argument(md, language, size or None)],
                    cwd=work, env=env, capture_output=True, text=True, errors="replace",
                )
                runs += 1
                settled = run.returncode != 0 or not toc.exists() or toc.read_bytes() == before
                if settled or runs == 5:
                    break
            log_file = work / f"{md.stem}.log"
            log = log_file.read_text(errors="replace").splitlines() if log_file.exists() else []
            errors = [f"{line} {log[i + 1] if i + 1 < len(log) else ''}".rstrip()
                      for i, line in enumerate(log) if line.startswith("! ")]
            missing = [line for line in log if line.startswith("Missing character")]
            # A float taller than its page runs off the page's foot with no overfull box, so LaTeX's own warning
            # for it is reported beside them.
            overfull = [f"{line}  {log[i + 1].strip() if i + 1 < len(log) else ''}"
                        for i, line in enumerate(log) if line.startswith("Overfull")]
            overfull += [line for line in log if "Float too large for page" in line]
            fonts = [line for line in log if "Font shape" in line and "instead" in line]
            if run.returncode != 0 and not errors:
                errors = [f"lualatex exited {run.returncode}: {run.stdout[-2000:]}"]
            if not settled:
                errors.append("the contents list's page numbers still changed after 5 runs")
            if errors or missing or not pdf.exists():
                break
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
            found = re.search(r"^Pages:\s+(\d+)", info, re.M)
            pages = int(found.group(1)) if found else 0
            if pages <= 1:
                break
        if pdf.exists() and not errors and not missing:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, target)
            body = f", body {size} pt" if size else ""
            print(f"{md.stem}: {pages} page{'' if pages == 1 else 's'}{body}, {target}")
            listed = not is_summary(md) and md.parent.name != "verse" and language not in CJK
            print(navigation(md.stem, text if listed else "", pdf))
        else:
            print(f"{md.stem}: no PDF written")
    for kind, lines in (("error", errors), ("missing character", missing), ("overfull box", overfull),
                        ("font substitution", fonts)):
        for line in lines:
            print(f"{md.stem}: {kind}: {line}")
    return not errors and not missing


# The short name of the policy paper with the executive summary as its first page (the module's docstring).
JOINED = "paper_with_summary"
HOUSE_FORMAT = LAYOUT.parent / "house_format"
# The executive summary on the Quarto route, as summary.tex sets it: TeX Gyre Heros at its own size, two columns on
# half-inch margins, no page number, lines about 1.25 em apart (Typst's leading of 0.65 em times 0.9, with the face's cap height, measured 1.24 em), its
# tables in \footnotesize, 0.85 of the body's size, no contents list, its body the largest of QUARTO_SIZES at which it
# fits one page (the module's docstring, Quarto).
QUARTO_SUMMARY: dict[str, object] = {"mainfont": "TeX Gyre Heros", "columns": 2, "margin": {"x": "0.5in", "y": "0.5in"}, "page-numbering": False, "linestretch": 0.9,
                  "table-size": 0.85, "contents": False}
QUARTO_SIZES = ("10.5", "10", "9.5")
# The slack, in lines, beyond half the body's height at which the summary's columns are tried in turn until the page
# holds the whole body and its columns, measured in the PDF (column_gap()), end within QUARTO_LEVEL lines of each other
# (the house format's house-balance); a block that cannot break where the left column would end can keep every slack
# from doing so.
QUARTO_BALANCE = (0, 0.5, 1, 1.5, 2, 3, 4, 6, 8)
# How far apart, in lines, the summary's two columns may end and still be called balanced (the brief of R14's step 6
# queue: "the summary's two columns end within two lines of each other").
QUARTO_LEVEL = 2.0
# Every other document on the Quarto route as document.tex sets it: TeX Gyre Pagella at 11 pt (Typst's default size) on
# a text block 6 in wide, side margins of 1.25 in on US letter, the top margin 0.75 in and the bottom 1 in, its
# mathematics in Pagella's own math face, as pxfonts gives the LaTeX route a Palatino math: about 85 characters a line.
QUARTO_DOCUMENT: dict[str, object] = {"mainfont": "TeX Gyre Pagella", "mathfont": "TeX Gyre Pagella Math",
                                      "margin": {"x": "1.25in", "top": "0.75in", "bottom": "1in"}}
# A verse document on the Quarto route as verse.tex sets it: 11 pt Pagella on a text block 7 in wide, the top margin
# 1 in and the bottom 1.1 in, no contents list; the house format's verse.lua sets its two columns.
QUARTO_VERSE: dict[str, object] = {"mainfont": "TeX Gyre Pagella", "margin": {"x": "0.75in", "top": "1in", "bottom": "1.1in"},
                                   "verse": True, "contents": False}
# A Korean, Japanese or Chinese document on the Quarto route as document-cjk.tex and summary-cjk.tex set it: A4, the
# longer documents' text block 438 pt wide (40 characters of the 10.95 pt CJK type, JLREQ's limit) on the English
# layout's top and bottom margins, the summary on half-inch margins; `lang` and the Typst region of the language
# (QUARTO_REGION), which name its line-breaking rules and the PDF's /Lang; lines 1.6 em apart, typeset-cjk.sty's
# \linespread{1.29} (17.5 pt on the 10.95 pt type, measured), for which Typst's leading is 1.32 times its 0.65 em
# (15.2 pt apart at 1, measured on a Japanese fixture). Its fonts are set by cjk_typst().
QUARTO_CJK_DOCUMENT: dict[str, object] = {"papersize": "a4", "margin": {"x": f"{(595.276 - 438) / 2:.2f}pt", "top": "0.75in",
                                                                     "bottom": "1in"}, "linestretch": 1.32}
QUARTO_CJK_SUMMARY: dict[str, object] = {"papersize": "a4", "linestretch": 1.32}
QUARTO_REGION = {"ko": "KR", "ja": "JP", "zh": "CN"}
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def missing_glyphs(text: str, pdf: Path) -> list[str]:
    """Each character of the document's printed text that no font drew, as `U+1E4D0 NAG MUNDARI LETTER O`: a
    printable character outside ASCII that is absent from the PDF's text layer. The printed text is Pandoc's plain
    rendering of the Markdown `text`, so a character that never prints, in a link's target, an image's path, an
    attribute or an HTML comment, is not looked for. Typst sets a character no font has as the
    font's .notdef glyph, which carries no text, so the character is missing from the text layer (pdftotext); a
    character a fallback font draws is there. Both sides are compared in compatibility form (NFKC), since Typst sets
    a letter in an equation as its mathematical alphanumeric (beta as U+1D6FD) and a ligature stands for its
    letters."""
    layer = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True,
                           errors="replace").stdout
    drawn = set(unicodedata.normalize("NFKC", layer))
    printed = subprocess.run([str(quarto_setup.binary()), "pandoc", "--from", "markdown", "--to", "plain"],
                             input=text, capture_output=True, text=True, check=True).stdout
    return [f"U+{ord(c):04X} {unicodedata.name(c, 'with no Unicode name')}"
            for c in sorted(set(printed)) if ord(c) > 127 and unicodedata.category(c)[0] not in "ZCM"
            and not set(unicodedata.normalize("NFKC", c)) <= drawn]


# Counts a PDF's outline items, every level, and its link annotations, with MuPDF.
NAVIGATION_JS = """var doc = Document.openDocument(scriptArgs[0]);
function items(list) { var n = 0; for (var i = 0; i < list.length; i++) n += 1 + items(list[i].down || []); return n; }
var links = 0;
for (var i = 0; i < doc.countPages(); i++) links += doc.loadPage(i).getLinks().length;
print(items(doc.loadOutline() || []) + " " + links);
"""


def navigation(stem: str, text: str, pdf: Path) -> str:
    """The report's line of a built PDF's means of moving through it: its contents entries, the `##` and `###`
    headings of `text`, the prepared Markdown of a document whose layout sets a contents list (the empty string for
    one that sets none); its bookmarks, the PDF's outline items; and its links, every link annotation, internal or
    external, both counted with MuPDF, or said to be not counted where `mutool` is not installed."""
    fenced = False
    headings = 0
    for line in text.splitlines():
        fenced = fenced != line.startswith(("```", "~~~"))
        headings += not fenced and re.match(r"#{2,3} ", line) is not None
    if shutil.which("mutool") is None:
        return f"{stem}: {headings} contents entries; bookmarks and links not counted (MuPDF's mutool not installed)"
    with tempfile.TemporaryDirectory(prefix="typeset-links-") as tmp:
        script = Path(tmp) / "navigation.js"
        script.write_text(NAVIGATION_JS)
        run = subprocess.run(["mutool", "run", str(script), str(pdf)], capture_output=True, text=True, check=True)
    bookmarks, links = run.stdout.split()[-2:]
    return f"{stem}: {headings} contents entries, {bookmarks} bookmarks, {links} links"


def column_gap(pdf: Path) -> float:
    """How far apart, in lines, the two columns of a one-page summary end: the lowest line wholly left of the page's
    middle and the lowest wholly right of it (pdftotext's lines), the head across both columns being above them and
    crossing the middle, divided by the median step between the left column's successive lines. A column with no line
    is infinitely far from the other."""
    xhtml = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox-layout", str(pdf), "-"], capture_output=True,
                           text=True, check=True, errors="replace").stdout
    page = next(ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xhtml)).iter(f"{XHTML}page"))
    mid = float(page.get("width", "0")) / 2
    boxes = [tuple(float(line.get(k, "0")) for k in ("xMin", "yMin", "xMax", "yMax"))
             for line in page.iter(f"{XHTML}line")]
    left = sorted(b[1] for b in boxes if b[2] <= mid)
    right = [b[3] for b in boxes if b[0] >= mid]
    steps = [b - a for a, b in zip(left, left[1:]) if b - a > 2]
    if not right or not steps:
        return float("inf")
    left_foot = max(b[3] for b in boxes if b[2] <= mid)
    return abs(left_foot - max(right)) / statistics.median(steps)


def typst_block(code: str) -> str:
    """A raw Typst block in the Markdown, which the house format passes to Typst as written."""
    return f"```{{=typst}}\n{code}\n```\n\n"


def cjk_typst(md: Path, language: str) -> str:
    """The Typst rules that set a Korean, Japanese or Chinese document's type on the Quarto route, as typeset-cjk.sty
    sets it: Latin in the English faces (Pagella, the summary's Heros as summary-cjk.tex sets it) and every other
    character in the Noto CJK face of the language's region (CJK), serif or, in the summary, sans; code in Typst's own
    mono face with Noto Sans Mono CJK; emphasis in bold, since the CJK faces have no italic. Typst's quarter-em space
    between CJK and Latin (cjk-latin-spacing), JLREQ 3.2.6's, in Japanese only: Korean and Chinese are set solid
    against Latin. Korean breaks only at the spaces between words (klreq 5.2): each run of non-space characters that
    holds a Hangul syllable is a box no line breaks inside, where Typst would break between any two syllables.
    Headings and the title in the sans faces, Heros and Noto Sans CJK, as typeset-cjk.sty's \\sffamily sets them; the
    title of a document other than the summary centred, as document-cjk.tex sets it."""
    region = CJK[language][0]
    latin, face = ("TeX Gyre Heros", "Sans") if is_summary(md) else ("TeX Gyre Pagella", "Serif")
    rules = [f'#set text(font: ("{latin}", "Noto {face} CJK {region}"), '
             f'cjk-latin-spacing: {"auto" if language == "ja" else "none"})',
             f'#show raw: set text(font: ("DejaVu Sans Mono", "Noto Sans Mono CJK {region}"))',
             "#show emph: it => strong(it.body)",
             f'#show heading: set text(font: ("TeX Gyre Heros", "Noto Sans CJK {region}"))']
    if not is_summary(md):  # document-cjk.tex centres the title; summary-cjk.tex sets it flush left
        rules.append("#show heading.where(level: 1): set align(center)")
    if language == "ko":
        rules.append(r'#show regex("[^\s]*\p{Hangul}[^\s]*"): box')
    return typst_block("\n".join(rules))


def icon_glyph(name: str) -> str:
    """The Typst string of a Tabler icon's outline glyph, `"\\u{edbe}"`. Raises ValueError for a name not in the
    index."""
    icon = json.loads(ICONS.read_text()).get(name, {}).get("styles", {}).get("outline")
    if icon is None:
        raise ValueError(f"no Tabler icon {name!r} (tools/icon_search.py finds names)")
    return '"\\u{' + icon["unicode"] + '}"'


# A heading that names an icon among its attributes, `## 3 Effects {icon=heart}`: its hashes and the name.
ICON_HEADING = re.compile(r"^(#{1,6}) (?=.*\{[^}]*\bicon=([\w-]+)[^}]*\}\s*$)")


def heading_icons(text: str, title: bool) -> str:
    """The prepared text with each heading's `{icon=NAME}` drawn on the Quarto route, as typeset-common.sty's
    \\typesetheadicon draws it: a call of the house format's house-icon with the Tabler glyph, put before the heading's
    words; the title's too where `title` is true (not on the policy paper's cover, which cover_typst() draws large).
    Raises ValueError for a name not in the Tabler index."""
    lines = text.split("\n")
    fenced = False
    for i, line in enumerate(lines):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        found = None if fenced else ICON_HEADING.match(line)
        if found and (title or found.group(1) != "#"):
            lines[i] = f"{found.group(0)}`#house-icon({icon_glyph(found.group(2))})`{{=typst}}{line[found.end():]}"
    return "\n".join(lines)


def heading_family(md: Path) -> str:
    """The family of the title and headings in the English layout: Lato, or the audience profile's heading font, as
    theme_tex() replaces Lato on the LaTeX route. Raises ValueError for a profile theme() refuses."""
    font = THEME_FONTS[theme(md)[1] if profile_design(md) else "lato"]
    return font[0] if font else "Lato"


def heading_typst(md: Path) -> str:
    """The Typst rules that set the title and headings of a document in the English layout on the Quarto route, as
    typeset-common.sty's \\typesetheading and the layouts' \\typesettitle set them: in heading_family()'s bold, the
    fourth to sixth levels in its italic of the regular weight. Placed in the body, after the brand's heading rule in
    the header, which they agree with. Raises ValueError as heading_family() does."""
    lower = ", ".join(f"heading.where(level: {level})" for level in (4, 5, 6))
    return typst_block(f'#show heading: set text(font: "{heading_family(md)}", weight: "bold")\n'
                       f'#show selector.or({lower}): set text(weight: "regular", style: "italic")')


def cover_typst(md: Path, text: str) -> str:
    """The prepared text of the policy paper with its head, the title, the dateline and a credit block straight after
    it (split_head()), set on a cover page of its own by the house format's house-cover, as document.tex sets it: the
    title's icon (with_cover_icon() has put the profile's cover icon there where the title names none) drawn large
    above the title; the cover in Lato, or the audience profile's heading font; the credit, house-cover's second body,
    at the page's foot. Raises ValueError for an icon not in the Tabler index or a profile theme() refuses."""
    head, rest = split_head(text, credit=True)
    title = next((line for line in head.splitlines() if line.startswith("# ")), "")
    named = re.search(r"\{[^}]*\bicon=([\w-]+)[^}]*\}\s*$", title)
    lines = head.splitlines()
    credit = next((n for n, line in enumerate(lines) if CREDIT.match(line)), len(lines))
    opening = (f'#house-cover(brand-color, "{heading_family(md)}", '
               f'{icon_glyph(named.group(1)) if named else "none"}, house-notice)[')
    return (typst_block(opening) + "\n".join(lines[:credit]) + "\n\n" + typst_block("][")
            + "\n".join(lines[credit:]) + "\n\n" + typst_block("]") + rest)


def build_quarto(md: Path, language: str, stamp: str, target: Path, front: Path | None = None) -> bool:
    """Render one document through Quarto and the house format (--quarto), in `language`, its page stamp `stamp`, to
    `target`; print its report as build() does; return whether it rendered. The policy paper in the English layout
    opens on its cover (cover_typst()); with `front`, a one-page PDF, it opens instead on that page, drawn whole as the
    page's background under the page notice and bookmarked "Summary", and has no cover (the paper with the summary in
    front, the module's docstring)."""
    errors: list[str] = []
    verse = md.parent.name == "verse"
    with tempfile.TemporaryDirectory(prefix="typeset-quarto-") as tmp:
        work = Path(tmp)
        try:
            brand = brand_yml(md)
            icon = cover_icon(md) if is_cover(md, language) else ""
            text = crossrefs(prepare(with_cover_icon(md.read_text(), icon)), latex=False)
            if language not in CJK:  # the CJK layouts draw no icons
                text = heading_icons(text, title=not is_cover(md, language) or front is not None)
            if front is not None:
                shutil.copyfile(front, work / "typeset-front.pdf")
                # The notice is drawn with the page, its baseline 0.3 in from the top as on the LaTeX route, since
                # the paper's header would fall in the summary's narrower top margin, on its title. The bookmark
                # "Summary" is a level-2 heading's, so that the paper's sections, whose title is no bookmark, stand
                # beside it, as on the LaTeX route.
                text = typst_block(
                    '#page(numbering: none, header: none, background: { image("typeset-front.pdf", page: 1, width: 100%, '
                    'height: 100%); if house-notice != none { place(top + center, dy: 0.3in, text(font: "TeX Gyre Heros", size: 8pt, top-edge: '
                    '"baseline", bottom-edge: "baseline", fill: brand-color.at("ink_second", default: luma(35%)), '
                    'house-notice)) } })[#[#show heading: none; #heading(level: 2, outlined: false, bookmarked: true)'
                    '[Summary]]]') + text
            elif is_cover(md, language):
                text = cover_typst(md, text)
            if language in CJK:
                text = cjk_typst(md, language) + text
            elif not verse:  # a verse document's title and headings are verse.lua's
                text = heading_typst(md) + text
        except ValueError as refusal:
            print(f"{md.stem}: error: {refusal}\n{md.stem}: no PDF written")
            return False
        (work / md.name).write_text(text)
        if brand:
            (work / "_brand.yml").write_text(brand)
        for found in IMAGE.finditer(text):
            path = found.group(2)
            source = md.parent / path
            if Path(path).is_absolute() or ".." in Path(path).parts:
                errors.append(f"image {path}: an absolute path or one with '..' is not copied")
            elif not source.is_file():
                errors.append(f"image {path}: no such file {source}")
            else:
                (work / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, work / path)
        (work / "_extensions").symlink_to(HOUSE_FORMAT / "_extensions")
        # The stored fonts, Lato and the Tabler icons, so that the route needs no system font the public copy lacks
        # (Typst searches the folder and those under it). Quarto reads a font path relative to the document's folder,
        # and one that starts with "/" as relative to its project's, so the folder is linked in beside the document.
        (work / "fonts").symlink_to(LAYOUT / "assets")
        notice = re.sub(r"([!-/:-@\[-`{-~])", r"\\\1", stamp)
        pdf = work / f"{md.stem}.pdf"

        def render(metadata: dict[str, object]) -> int:
            """Render with `metadata`, setting `errors`; the PDF's page count, 0 where it failed."""
            nonlocal errors
            (work / "metadata.json").write_text(json.dumps({"notice": notice, "font-paths": ["fonts"]} | metadata))
            try:
                run = subprocess.run(
                    [str(quarto_setup.binary()), "render", md.name, "--to", "house-typst", "--metadata-file",
                     "metadata.json"], cwd=work, capture_output=True, text=True, errors="replace")
                output = [ANSI.sub("", line) for line in (run.stdout + run.stderr).splitlines()]
                if run.returncode != 0 or not pdf.exists():
                    errors = [line for line in output if line.startswith("ERROR")] or output[-20:]
                else:  # a font the document names that no installed font matches: Typst sets another in its place;
                    # a layout Typst did not settle in its five passes, whose pages may not be those its measures chose
                    errors = [line.strip() for line in output
                              if "unknown font family" in line or "did not converge" in line]
            except quarto_setup.Refusal as refusal:
                errors = [str(refusal)]
            if errors:
                return 0
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
            found_pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
            return int(found_pages.group(1)) if found_pages else 0

        layout = QUARTO_VERSE if verse else QUARTO_SUMMARY if is_summary(md) else QUARTO_DOCUMENT
        if language in CJK:  # its fonts are cjk_typst()'s, so no main font is named here
            layout = {key: value for key, value in layout.items() if key != "mainfont"} | {
                "lang": language, "region": QUARTO_REGION[language]} | (
                QUARTO_CJK_SUMMARY if is_summary(md) else QUARTO_CJK_DOCUMENT)
        pages, size = 0, ""
        metadata: dict[str, object] = {}
        for size in () if errors else QUARTO_SIZES if is_summary(md) else ("",):
            metadata = layout | ({"fontsize": f"{size}pt"} if size else {})
            pages = render(metadata)
            if errors or pages <= 1:
                break
        balanced = ""
        if size and not errors and pages == 1:
            for slack in QUARTO_BALANCE:
                if render(metadata | {"balance": slack}) == 1 and (gap := column_gap(pdf)) <= QUARTO_LEVEL:
                    balanced = f", columns balanced with {slack} lines' slack, ending {gap:.1f} lines apart"
                if balanced or errors:
                    break
            else:
                render(metadata)
                if not errors:
                    balanced = f", columns not balanced at any slack: they end {column_gap(pdf):.1f} lines apart"
        if not errors:
            errors = [f"missing glyph {glyph}: no font draws it, so it would print as a blank box"
                      for glyph in missing_glyphs(text, pdf)]
        if not errors:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, target)
            body = f", body {size} pt" if size else ""
            print(f"{md.stem}: {pages} page{'' if pages == 1 else 's'}{body}{balanced}, {target}")
            print(navigation(md.stem, "" if verse or is_summary(md) else text, pdf))
            return True
    for line in errors:
        print(f"{md.stem}: error: {line}")
    print(f"{md.stem}: no PDF written")
    return False


INCH = 72.0
XHTML = "{http://www.w3.org/1999/xhtml}"


def measure(pdf: Path, sheets: Path | None) -> str:
    """One line of measures of a PDF's pages (the module's docstring, --measure), and its thumbnail sheet."""
    from PIL import Image

    xhtml = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], capture_output=True, text=True,
                           check=True, errors="replace").stdout
    root = ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xhtml))  # control characters XML forbids
    lefts: list[float] = []
    rights: list[float] = []
    blocks: list[float] = []
    full: list[int] = []
    for page in root.iter(f"{XHTML}page"):
        width, height = float(page.get("width", "0")), float(page.get("height", "0"))
        # A full line is one, not a paragraph's last, at least 93 per cent as wide as the widest line of its block
        # (pdftotext's paragraph), in blocks of three lines or more: running text, not a table cell or a caption.
        for block in page.iter(f"{XHTML}block"):
            lines = [(float(line.get("xMax", "0")) - float(line.get("xMin", "0")),
                      " ".join(w.text or "" for w in line.iter(f"{XHTML}word"))) for line in block.iter(f"{XHTML}line")]
            if len(lines) >= 3:
                widest = max(w for w, _ in lines)
                full += [len(t) for w, t in lines[:-1] if w >= 0.93 * widest]
        boxes = [(float(w.get("xMin", "0")), float(w.get("yMin", "0")), float(w.get("xMax", "0")),
                  float(w.get("yMax", "0"))) for w in page.iter(f"{XHTML}word")]
        if len(boxes) < 20:  # a page of figure or title alone says nothing of the text's measure
            continue
        x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
        x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
        lefts.append(x0 / INCH)
        rights.append((width - x1) / INCH)
        blocks.append((x1 - x0) * (y1 - y0) / (width * height))
    with tempfile.TemporaryDirectory(prefix="measure-") as tmp:
        subprocess.run(["pdftoppm", "-r", "48", "-gray", "-png", str(pdf), f"{tmp}/p"], check=True)
        empty: list[float] = []
        for png in sorted(Path(tmp).glob("p-*.png")):
            with Image.open(png) as image:
                cols, rows = image.width // 12, image.height // 12  # quarter-inch squares at 48 dpi
                dark = image.convert("L").crop((0, 0, cols * 12, rows * 12)).point([255 if v < 160 else 0 for v in range(256)])
                inked = cols * rows - dark.resize((cols, rows), Image.Resampling.BOX).histogram()[0]
                empty.append(1 - inked / (cols * rows))
        if sheets is not None:
            subprocess.run(["pdftoppm", "-r", "30", "-png", str(pdf), f"{tmp}/t"], check=True)
            thumbs = [Image.open(t).convert("RGB") for t in sorted(Path(tmp).glob("t-*.png"))]
            across = min(8, len(thumbs))
            w, h = thumbs[0].size
            sheet = Image.new("RGB", (across * (w + 6) + 6, -(-len(thumbs) // across) * (h + 6) + 6), (128, 128, 128))
            for n, thumb in enumerate(thumbs):
                sheet.paste(thumb, (6 + n % across * (w + 6), 6 + n // across * (h + 6)))
            sheets.mkdir(parents=True, exist_ok=True)
            sheet.save(sheets / f"{pdf.stem}_pages.png")
    worst = sorted(range(len(empty)), key=lambda n: -empty[n])[:3]
    median = statistics.median
    text = (f"side margins {median(lefts):.2f} and {median(rights):.2f} in; full lines {median(full):.0f} characters "
            f"(median of {len(full)}); text block {median(blocks):.0%} of the page; " if lefts and full
            else "too few words to measure the text; ")
    return (f"{pdf}: {len(empty)} page{'' if len(empty) == 1 else 's'}; {text}empty quarter-inch squares "
            f"{median(empty):.0%} (range {min(empty):.0%} to {max(empty):.0%}; emptiest pages "
            + ", ".join(f"{n + 1} {empty[n]:.0%}" for n in worst) + ")")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Typeset a case's documents as PDFs, or measure PDFs' pages.")
    parser.add_argument("--language", default="en", choices=["en", *CJK], help="the documents' primary language tag")
    parser.add_argument("--measure", nargs="+", type=Path, metavar="PDF", help="measure these PDFs; build nothing")
    parser.add_argument("--sheets", type=Path, help="with --measure, the folder for each PDF's thumbnail sheet")
    parser.add_argument("--notice", metavar="TEXT", help="print TEXT in small type at the head of every page")
    parser.add_argument("--quarto", action="store_true", help="render every document through Quarto and the house "
                        "format (layout migration steps 4 to 9)")
    parser.add_argument("case", type=Path, nargs="?", help="the case folder")
    args = parser.parse_args(argv)
    if args.measure:
        for pdf in args.measure:
            print(measure(pdf, args.sheets))
        return 0
    if args.case is None:
        parser.error("name the case folder, or --measure a PDF")
    case: Path = args.case.resolve()
    documents = sorted(p for p in (case / "documents").glob("*.md") if not p.name.endswith("_template.md"))
    documents += sorted((case / "documents" / "verse").glob("*.md"))
    documents += sorted(p for p in (case / "documents" / "audience").glob("*/*.md")
                        if not p.name.endswith("_template.md") and p.name != "crosswalk.md")
    if not documents:
        print(f"{case}: no document to typeset in {case / 'documents'}", file=sys.stderr)
        return 1
    quarto: set[Path] = set(documents) if args.quarto else set()
    if shutil.which("lualatex") is None and len(quarto) < len(documents):
        print("No TeX installation was found (no lualatex on the path), so no PDF is made and the case's documents "
              "stay as Markdown with the same text. On a machine of one's own, a TeX Live installation with LuaLaTeX "
              "makes the PDFs. In a cloud session TeX cannot be installed, so do not try: tell the user the documents "
              "are delivered as Markdown.", file=sys.stderr)
        return 1
    try:
        names = {md: document_names.document_name(case, md) for md in documents}
    except document_names.Refused as refusal:
        print(refusal, file=sys.stderr)
        return 1
    summary, paper = case / "documents" / "executive_summary.md", case / "documents" / "policy_paper.md"
    joined = (summary, paper) if summary.exists() and paper.exists() and args.language not in CJK else None
    if joined:
        names[case / "documents" / f"{JOINED}.pdf"] = JOINED
    shared = {name: [md for md in names if names[md] == name] for name in set(names.values())}
    clashes = [f"{name}: {', '.join(str(md.relative_to(case)) for md in mds)}" for name, mds in shared.items()
               if len(mds) > 1]
    if clashes:
        print(f"{case}: documents share a name, so their PDFs would overwrite each other: {'; '.join(clashes)}",
              file=sys.stderr)
        return 1
    # What the build reads: the sources, the images they reference, the audience profiles, this script, the layout
    # and the naming module.
    inputs = set(documents) | {Path(__file__).resolve(), LAYOUT, Path(document_names.__file__).resolve()}
    for md in documents:
        inputs |= {(md.parent / m.group(2)).resolve() for m in IMAGE.finditer(md.read_text())}
        if md.parent.parent.name == "audience":
            inputs.add(AUDIENCES / f"{md.parent.name}.toml")
    arguments = f"language={args.language}\nnotice={args.notice or ''}\n"
    if args.quarto:  # the route enters the hash, so a Quarto draft never shares a LaTeX draft's number
        arguments += "route=quarto\n"
        inputs.add(HOUSE_FORMAT)
    try:
        draft = document_names.draft(case, sorted(p for p in inputs if p.exists()), arguments)
    except document_names.Refused as refusal:
        print(refusal, file=sys.stderr)
        return 1
    print(f"version {draft.version}, {'pending' if draft.pending else 'committed'}")
    print(f"inputs {draft.inputs}")
    for note in draft.notes:
        print(note)
    drafts = case / "documents" / "drafts"
    results: list[bool] = []
    for md in documents:
        identifier = document_names.identifier(draft, names[md])
        stamp = document_names.stamp(identifier, draft.date, args.notice)
        target = drafts / f"{identifier}.pdf"
        results.append(build_quarto(md, args.language, stamp, target) if md in quarto
                       else build(md, args.language, stamp, target))
        if results[-1]:
            shutil.copyfile(target, md.with_suffix(".pdf"))
    if joined:
        # The paper with the summary as its first page, in one run of the paper, so that its links and bookmarks hold:
        # the summary is built again with an empty notice, and the joined file's own notice is drawn over every page.
        identifier = document_names.identifier(draft, JOINED)
        typeset = build_quarto if paper in quarto else build
        with tempfile.TemporaryDirectory(prefix="typeset-front-") as tmp:
            front = Path(tmp) / "front.pdf"
            results.append(typeset(summary, args.language, "", front) and typeset(
                paper, args.language, document_names.stamp(identifier, draft.date, args.notice),
                drafts / f"{identifier}.pdf", front))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
