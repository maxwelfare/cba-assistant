"""Typeset a case's documents as PDFs (roadmap R10, R14), and measure a PDF's pages (notes/pdf_layout_review.md).

Run from the repository root:

    .venv/bin/python tools/typeset.py [--language <tag>] [--notice TEXT] cases/<case>
    .venv/bin/python tools/typeset.py --measure <pdf> [<pdf> ...] [--sheets <folder>]

Each `<case>/documents/*.md` except `*_template.md`, each `documents/verse/*.md` and each audience edition's document
is rendered by the shared renderer (the shared folder's tools/render.py, R67, on the pinned Quarto that its
tools/quarto_setup.py installs) through Typst, the shared base format and, over it, the house format,
`tools/house_format/`, the case layer, in a temporary folder that is removed afterwards: the prepared text, copies of
its images and the stamp in a metadata file. The renderer refuses a document, and no PDF is written, for a reference
or internal link with no target, an image whose path is absolute, holds `..` or names no file, a word outside the
text block or over another, a table too wide for the page, a character no font draws, a font not installed or a
layout Typst did not settle, each fault printed as an error line (its docstring). Its PDF is written
to `<case>/documents/drafts/<identifier>.pdf`, the identifier the case's short name, the document's name and the
draft's version (`demo_1page_v2.0`, tools/document_names.py, which keeps the case's log `<case>/versions.toml`), and
the same bytes beside the source with its stem (the paper with the summary in front, below, only in drafts/). Before
any build it prints the version, pending or committed, and the hash of the inputs; it refuses the case, with one line
and no PDF, when the log refuses or two documents share a name. With `--language` ko, ja or zh the documents are set
in that language's layout (below); with `en` or no `--language` the English layout. Any other tag is refused: no
layout has been built for it.

Per document it prints the page count and the renderer's report: a line `<stem>: N pages, N contents entries, N
links`, the `##` and `###` headings where the layout sets a contents list and the PDF's link annotations, and a
warning for each table body cell that holds prose. It exits 1 if a document has an error, or if the case has no
document. The layout review (the shared agents/pdf-layout.md, review-only) reads the
PDFs; a fault it finds in the layout is fixed here or in the house format, never in a PDF.

The values below were matched, at R14's steps 5 to 9, to the LaTeX route this script had before (deleted at step 10;
its files are in git, `git show 88c49d4:tools/typeset_layout/<file>`), and the comments that name summary.tex,
document.tex, verse.tex, document-cjk.tex, summary-cjk.tex or a typeset-*.sty file name the setting matched.

Title and properties. Every PDF's Title names its document among the case's others (title()): the case's short title,
the words of its CASE.md's first `#` heading before their first colon (its short name where it has none), the
document's kind ("One-page summary", "Policy paper", "Technical appendix", "Technical note", else the file's stem) and
the draft's version, as "Example title: One-page summary v1.0"; the joined file's kind is "Policy
paper with summary", passed to the renderer as `short-title` and `kind`. The PDF asks a viewer to show the Title
rather than the file name (DisplayDocTitle, PDF/UA-1 7.1; the renderer sets it). The PDF's language is named (`en-US`,
or the `--language` tag) and it is tagged, as Typst writes every PDF.

Contents and bookmarks. Each `##` and `###` heading is a bookmark, the `###` ones under their `##`, and every document
but the executive summary and verse has a contents list of those headings, under "Contents" before its first `##`
heading, each line a link to its heading with its page number (Typst's outline, the base format's contents.lua).

Cross-references (roadmap item 2.69): Quarto's labels. A heading `## 4 Results {#sec-results}`, a figure `![Its
caption.](figures/x.png){#fig-x}`, and a table by the caption line straight after it, `: Its caption. {#tbl-x}`;
prose refers to each as `@sec-results`, `@fig-x` or `@tbl-x`. Each reference is a link to its target, printed
"Section 4" for a heading that opens with its number and the heading's words for one that does not, and "Figure N"
or "Table N" for the labelled figures and tables in order, whose captions get the same "Figure N." or "Table N." in
front (the renderer's crossrefs()). A reference, or an internal link `[...](#name)`, whose label no attribute in the
document carries is an error naming it, and the document gets no PDF.

Icons. A heading may end in Pandoc's attribute syntax naming a Tabler icon, `## 3 Effects on health {icon=heart}`;
the icon prints before the heading's words in its colour and size (on the policy paper's title, large on the cover),
and is left out of the contents list and the bookmarks (heading_icons() and the house format's icons.lua). A name not in
`tools/typeset_layout/assets/tabler-icons/icons.json` stops the build with an error naming it; `tools/icon_search.py
WORD ...` finds names. The CJK layouts draw no icons. The stored fonts, Lato and the Tabler icons in
`tools/typeset_layout/assets/` (its README), are linked into the build's format folder and named in `font-paths`, so
the route takes no Lato from the system.

Boxes. A document marks a box with a fenced div, Pandoc's syntax: a line `::: key-findings`, the box's blocks,
and a line `:::`. Three kinds are set, each a shaded box with a coloured rule (the house format's boxes.lua and
house-callout):

    ::: key-findings      the answer and its range, at the top of the summary or the paper
    ::: callout           what a reader must not miss: a caveat, what is left out, the action wanted
    ::: worked-example    the one unit rebuilt to the headline
    ::: credit            no box: the tool's credit line, in small grey type (the project's CLAUDE.md)

The box's title is its first words in bold ("**Key findings.**"), less a final period. Any other kind is refused.
`::: {.callout}` is read the same. A blank line is put before and after each fence line, since without one a list's
last item would swallow the closing `:::`.

Audience editions (notes/audience_layer.md). Each `<case>/documents/audience/<key>/*.md` except `*_template.md`
and `crosswalk.md` is built as the document of its name is, its PDF beside it, with the colours and the heading
font of the profile `audiences/<key>.toml`: the colour tokens of its `[design.color]` by role (accent,
accent_caveat, caveat_ground, panel, neutral, rule, ink, ink_second) and `[design.font.heading]` (lato, pagella,
termes or schola), written as the brand in the document's front matter (brand_json()), which the boxes, the credit,
the notice, the headings and the cover read. A token left out keeps the base value, and no other document gets one. The
profile's `[design.icons] cover`, a Tabler name or a word (the first name `tools/icon_search.py` lists for it), is
drawn on the policy paper's cover as a title's `{icon=NAME}` is, unless the title names an icon itself.
`[design.imagery]` is guidance in words that no tool reads; `[design.charts]` is the figures' rc overlay
(tools/figures.py), read here only to refuse a key that is not a matplotlib rc name. The build of such a document is
refused, with an error line, for a missing profile, an unknown token or key, a cover word no icon matches, or a
contrast under 4.5 to 1 between the accent and white or between the ink and a box's ground, the error naming the
pair and both colours.

Notice. Every page of every document, the policy paper's cover included, carries its stamp in small grey sans type
(TeX Gyre Heros) centred in the top margin (roadmap item 2.47, 2.66), in white on the cover's band: `--notice TEXT` if
given, the document's identifier and the draft's date, joined by " | " ("Draft for comment | demo_1page_v2.0 | 13
November 2026"). It is passed in the metadata, its punctuation escaped so that it prints as typed (notice.lua).

The layouts. The paper, the appendix and every other document are set in TeX Gyre Pagella at 11 pt on a text block
6 in wide, the top margin 0.75 in and the bottom 1 in, about 85 characters a line (QUARTO_DOCUMENT). The policy paper
in the English layout opens on a cover page of its own, drawn by the house format's house-cover: the blue band with
the notice in white, the title's icon or the profile's cover icon from the stored Tabler font, the title, the
dateline and a `::: credit` block if one directly follows the dateline at the page's foot (cover_typst()); the body
starts on page 2. Every other document keeps its title at the head of its first page. In the English layout the
title and headings of every document but verse are set in Lato bold, or the audience profile's heading font, the
fourth to sixth levels in its italic (heading_typst()); a font the document names that is not installed is an error
naming it, since Typst would set another in its place. A display equation labelled `$$ ... $$ {#eq-name}` is
numbered (1), (2), ... at its right; one too wide is broken and set smaller, or refused (the base format). Tables
are the base format's: a column whose body cells are all numbers right-aligned; set at 9/11 of the body's size (0.85
in the summary), rows spaced as LaTeX's \\arraystretch of 1.15 (HOUSE_METADATA's `table-stretch`), columns sized by
tabulary's rule with no column narrower than its longest word; one whose longest words do not fit the line runs into
the side margins, never nearer the page's edge than the renderer's trim-safe distance, then is set smaller, then gets
a landscape page, and past that is refused, naming it. No character hangs past the line's end (the house format's
header), as on the LaTeX route.

The executive summary is set in TeX Gyre Heros, in two columns on half-inch margins with no page number, its title,
its dateline (as split_head() takes it) and a key-findings box straight after them across both at the top of the
page (columns.lua), its body type the largest of 10.5, 10 and 9.5 pt at which it fits one page, rendered at each in
turn and the size used printed; one that does not fit at 9.5 pt is an error, naming its page count and the words
that run onto page 2, and no PDF is written: it is too long, a fault of content for its author. Its columns are
0.25 in apart, its title 19 pt and its dateline 8 pt in ink_second, the float of its head 0.7 of a line above the
columns, with a 0.6 pt rule under its title and dateline; every box has 4 pt above and below its title and its body
(the house format's header). It has no contents list. Its columns are then
balanced: rendered again in columns as short as hold the body (the format's house-balance), with more slack
(QUARTO_BALANCE) where the page would overrun, until the page holds the body and its columns, measured in the PDF,
end within two lines of each other (QUARTO_LEVEL); the report says with how much slack and how far apart they end,
or that they could not be balanced and how far apart they end unbalanced.

Verse documents, `documents/verse/*.md`, are set with the title and headings in Lato bold and the verse in two
columns, those of a run's last page balanced (QUARTO_VERSE and the format's verse.lua). With `--language` ko, ja or
zh the documents are set on A4 with `lang` and its region, Latin in the English faces and the rest in the Noto CJK
fonts, Japanese with JLREQ's quarter em between kana or kanji and Latin, Korean breaking only between words,
headings in the sans faces and a document's title centred (cjk_typst()); no joined file is made.

The paper with the summary in front. When `<case>/documents/` holds both `executive_summary.md` and
`policy_paper.md`, in the English layout, one more PDF is written to `drafts/`, its short name `paper_with_summary`
(`demo_paper_with_summary_v2.0`): the summary's page, bookmarked "Summary", then the paper with no cover, its title at
the head of page 2, then the contents list and the body. It is made in one Typst run of the paper, its first page the
summary built again with an empty notice and drawn whole as that page's background, under a hidden heading "Summary"
that is its bookmark, beside the paper's sections, so the paper's links and bookmarks hold and the joined file's own
notice is drawn once on every page. The page is marked as drawn from a checked PDF (the base format's doc-placed), so
the renderer does not hold the summary's words to the paper's text block.

With --measure it builds nothing: for each PDF it prints the page count, the side margins (the median over pages
of the distance from each edge to the nearest word), the median characters in a full line of text, the median
share of the page inside the text's bounding box, and the share of quarter-inch squares with no dark pixel
(median, range, and the emptiest pages), the measures of notes/pdf_layout_review.md 1. With --sheets it writes
a thumbnail sheet of each PDF's pages, `<stem>_pages.png`, into that folder, to look at all the pages at once.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, cast

import document_names
import figures
import icon_search

# The stored fonts, Lato and the Tabler icons (their README), and the house format, the case layer's Typst and filters.
ASSETS = Path(__file__).resolve().parent / "typeset_layout" / "assets"
ICONS = ASSETS / "tabler-icons" / "icons.json"
HOUSE_FORMAT = Path(__file__).resolve().parent / "house_format"
# The shared renderer (R67), run with this project's Python, and its base format, under which the house format sets
# the case layer: in the shared folder beside this project, or in shared/ inside a public copy, as
# cost_benefit_engine/shared.py finds it.
ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared" if (ROOT / "shared").is_dir() else ROOT.parent / "shared"
RENDER = SHARED / "tools" / "render.py"
BASE_FORMAT = SHARED / "tools" / "render_format" / "_extensions" / "doc"
# What the house format adds to every render's metadata: its Typst, after the base format's header; its filters, the
# summary's head and columns, the boxes and the verse before Quarto reads the document, the heading icons after
# Quarto's own filters, and the page notice at post-render, after the brand's colours are declared; the stored fonts.
# Each path is the build's, where the renderer links the format folder build() makes in as `_extensions`.
HOUSE_METADATA: dict[str, object] = {
    "include-in-header": [{"file": "_extensions/house/header.typ"}],
    "filters": [*({"path": f"_extensions/house/{name}.lua", "at": "pre-ast"} for name in ("columns", "boxes", "verse")),
                {"path": "_extensions/house/icons.lua", "at": "post-quarto"},
                {"path": "_extensions/house/notice.lua", "at": "post-render"}],
    "font-paths": ["_extensions/fonts"],
    # Table rows spaced as typeset-common.sty spaced them, LaTeX's \arraystretch at 1.15 (the shared base format)
    "table-stretch": 1.15}
# The summary's page in front of the joined file, as it is named in the format folder.
FRONT = "front.pdf"
# Each language's Noto CJK region (the fonts' names); Typst's region, for its line-breaking rules, is QUARTO_REGION.
CJK = {"ko": "KR", "ja": "JP", "zh": "SC"}


def is_summary(md: Path) -> bool:
    return md.name == "executive_summary.md" and md.parent.name != "verse"


def is_cover(md: Path, language: str) -> bool:
    """Whether the document opens on a cover page: the policy paper, in the English layout (document.tex sets the
    cover when its head file exists)."""
    return md.name == "policy_paper.md" and md.parent.name != "verse" and language not in CJK


# An audience edition's theme (notes/audience_layer.md 3.4). A profile, `audiences/<key>.toml`, overrides the house
# format's colours by role (THEME_COLOURS, the names its brand palette takes), may name a heading font (a TeX Gyre
# family, which replaces Lato) and a cover icon; its imagery and chart tables carry only the keys below. The body type
# does not change.
AUDIENCES = figures.AUDIENCES
PROVENANCE = ("basis", "evidence")
IMAGERY = ("photograph", "cover")
THEME_COLOURS = ("accent", "accent_caveat", "caveat_ground", "panel", "neutral", "rule", "ink", "ink_second")
THEME_FONTS = {"lato": None, "pagella": "TeX Gyre Pagella", "termes": "TeX Gyre Termes", "schola": "TeX Gyre Schola"}


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


def brand_json(md: Path) -> str:
    """The brand of a document of an audience edition (layout migration step 7), which build() writes as its front
    matter's `brand`: the profile's colours as the brand's palette, `#RRGGBB` by the role names of THEME_COLOURS,
    which the house format's boxes and credit read (its header, house-callout), and its heading font, where it is not
    the base Lato, as the brand's heading family, which Quarto sets on every heading. Written as JSON on one line,
    which YAML reads. The empty string for any other document and for a profile that sets neither. Raises ValueError
    as theme() does: the same checks, the contrast check among them, hold on this route."""
    if not profile_design(md):
        return ""
    colours, heading = theme(md)
    brand: dict[str, object] = {}
    if colours:
        brand["color"] = {"palette": {name: f"#{value}" for name, value in colours.items()}}
    font = THEME_FONTS[heading]
    if font:
        brand["typography"] = {"headings": {"family": font}}
    return json.dumps(brand) if brand else ""


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


# The short name of the policy paper with the executive summary as its first page (the module's docstring).
JOINED = "paper_with_summary"
# The kind of each document, for its PDF's Title (title()); a document not named here takes its file's stem.
KINDS = {"executive_summary": "One-page summary", "policy_paper": "Policy paper", "technical_appendix": "Technical appendix",
         "technical_note": "Technical note"}
# The executive summary on the Quarto route, as summary.tex sets it: TeX Gyre Heros at its own size, two columns on
# half-inch margins, no page number, lines about 1.25 em apart (Typst's leading of 0.65 em times 0.9, with the face's cap height, measured 1.24 em), its
# tables in \footnotesize, 0.85 of the body's size, no contents list, its body the largest of QUARTO_SIZES at which it
# fits one page (the module's docstring); its columns 0.25 in apart (columnsep), its title at 19 pt on 22 pt and
# its dateline at 8 pt on 10 pt (\fontsize; columns.lua).
QUARTO_SUMMARY: dict[str, object] = {"mainfont": "TeX Gyre Heros", "columns": 2, "margin": {"x": "0.5in", "y": "0.5in"}, "page-numbering": False, "linestretch": 0.9,
                  "table-size": 0.85, "contents": False, "gutter": "0.25in", "head-title": "19pt 22pt",
                  "head-dateline": "8pt 10pt"}
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
QUARTO_CJK_SUMMARY: dict[str, object] = {"papersize": "a4", "linestretch": 1.32, "head-title": "19pt 25pt",
                                          "head-dateline": "8pt 12pt"}
QUARTO_REGION = {"ko": "KR", "ja": "JP", "zh": "CN"}
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
    region = CJK[language]
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


def icon_code(name: str) -> str:
    """The code point of a Tabler icon's outline glyph in hexadecimal, `edbe`. Raises ValueError for a name not in the
    index."""
    icon = json.loads(ICONS.read_text()).get(name, {}).get("styles", {}).get("outline")
    if icon is None:
        raise ValueError(f"no Tabler icon {name!r} (tools/icon_search.py finds names)")
    return str(icon["unicode"])


def icon_glyph(name: str) -> str:
    """The Typst string of a Tabler icon's outline glyph, `"\\u{edbe}"`. Raises ValueError as icon_code() does."""
    return '"\\u{' + icon_code(name) + '}"'


# A heading that names an icon among its attributes, `## 3 Effects {icon=heart}`: its hashes and the name.
ICON_HEADING = re.compile(r"^(#{1,6}) (?=.*\{[^}]*\bicon=([\w-]+)[^}]*\}\s*$)")


def heading_icons(text: str, title: bool) -> str:
    """The prepared text with each heading's `{icon=NAME}` given its glyph, `{icon=NAME icon-glyph=CODE}`, which the
    house format's icons.lua draws before the heading's words with house-icon, as typeset-common.sty's
    \\typesetheadicon drew it; the title's too where `title` is true (not on the policy paper's cover, which
    cover_typst() draws large). The filter draws it after the shared renderer has resolved the cross-references, so a
    reference to the heading prints its number or words alone. Raises ValueError for a name not in the Tabler
    index."""
    lines = text.split("\n")
    fenced = False
    for i, line in enumerate(lines):
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        found = None if fenced else ICON_HEADING.match(line)
        if found and (title or found.group(1) != "#"):
            head, attributes = line.rsplit("{", 1)
            lines[i] = f"{head}{{{attributes.rstrip().removesuffix('}')} icon-glyph={icon_code(found.group(2))}}}"
    return "\n".join(lines)



def heading_family(md: Path) -> str:
    """The family of the title and headings in the English layout: Lato, or the audience profile's heading font.
    Raises ValueError for a profile theme() refuses."""
    return THEME_FONTS[theme(md)[1] if profile_design(md) else "lato"] or "Lato"


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


def title(case: Path, md: Path, short: str, version: str) -> dict[str, object]:
    """The metadata that makes the PDF's Title name a case's document among the case's others, "short title: kind"
    (the shared renderer's `short-title` and `kind`): the case's short title, the words of the first `#` heading of
    its CASE.md before their first colon (its short name, `short`, where it has none); the document's kind (KINDS,
    else the file's stem with spaces for underscores), "in verse" for a verse document and the profile's key for an
    audience edition's, then the version: "Example title: One-page summary v1.0"."""
    index = case / "CASE.md"
    heading = next((line[2:] for line in index.read_text().splitlines() if line.startswith("# ")), "") \
        if index.is_file() else ""
    name = heading.split(":", 1)[0].strip() or short
    kind = KINDS.get(md.stem.removesuffix("_verse"), md.stem.replace("_", " "))
    if md.parent.name == "verse":
        kind += ", in verse"
    elif md.parent.parent.name == "audience":
        kind += f", {md.parent.name} edition"
    return {"short-title": name, "kind": f"{kind} {version}"}


def build(md: Path, language: str, stamp: str, target: Path, front: Path | None = None,
          titled: dict[str, object] | None = None) -> bool:
    """Render one document with the shared renderer and the house format, in `language`, its page stamp `stamp`, to
    `target`, its PDF's Title from `titled` (title(); the first heading's words where none); print its report; return
    whether it rendered. The policy paper in the English layout opens on its cover (cover_typst()); with `front`, a
    one-page PDF, it opens instead on that page, drawn whole as the page's background under the page notice and
    bookmarked "Summary", and has no cover (the paper with the summary in front, the module's docstring)."""
    errors: list[str] = []
    verse = md.parent.name == "verse"
    with tempfile.TemporaryDirectory(prefix="typeset-") as tmp:
        work = Path(tmp)
        try:
            brand = brand_json(md)
            icon = cover_icon(md) if is_cover(md, language) else ""
            text = prepare(with_cover_icon(md.read_text(), icon))
            if language not in CJK:  # the CJK layouts draw no icons
                text = heading_icons(text, title=not is_cover(md, language) or front is not None)
            if front is not None:
                # The notice is drawn with the page, its baseline 0.3 in from the top as on the LaTeX route, since
                # the paper's header would fall in the summary's narrower top margin, on its title. The bookmark
                # "Summary" is a level-2 heading's, so that the paper's sections, whose title is no bookmark, stand
                # beside it, as on the LaTeX route. The page is marked doc-placed, so that the shared renderer, which
                # checked the summary's page when it rendered it, does not hold its words to the paper's text block.
                text = typst_block(
                    f'#page(numbering: none, header: none, background: {{ image("_extensions/{FRONT}", page: 1, '
                    'width: 100%, height: 100%); if house-notice != none { place(top + center, dy: 0.3in, '
                    'text(font: "TeX Gyre Heros", size: 8pt, top-edge: "baseline", bottom-edge: "baseline", '
                    'fill: brand-color.at("ink_second", default: rgb("#52514E")), house-notice)) } })[#[#show heading: '
                    'none; #heading(level: 2, outlined: false, bookmarked: true)[Summary]]; #doc-placed]') + text
            elif is_cover(md, language):
                text = cover_typst(md, text)
            if language in CJK:
                text = cjk_typst(md, language) + text
            elif not verse:  # a verse document's title and headings are verse.lua's
                text = heading_typst(md) + text
        except ValueError as refusal:
            print(f"{md.stem}: error: {refusal}\n{md.stem}: no PDF written")
            return False
        # The prepared text, its brand in its front matter (where Quarto reads a brand given in the document), beside
        # copies of its images; the shared renderer refuses an image whose path is absolute, holds `..` or names no file.
        source = work / "document" / md.name
        source.parent.mkdir()
        source.write_text(f"---\nbrand: {brand}\n---\n\n{text}" if brand else text)
        for found in IMAGE.finditer(text):
            path = Path(found.group(2))
            if not path.is_absolute() and ".." not in path.parts and (md.parent / path).is_file():
                (source.parent / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(md.parent / path, source.parent / path)
        # The format folder the renderer links in as the build's _extensions: the shared base format, the house
        # format, the stored fonts (Lato and the Tabler icons, so the route needs no system font the public copy
        # lacks; Quarto reads a font path relative to the document's folder) and the summary's page for `front`.
        extensions = work / "format" / "_extensions"
        extensions.mkdir(parents=True)
        for name, origin in (("doc", BASE_FORMAT), ("house", HOUSE_FORMAT / "_extensions" / "house"), ("fonts", ASSETS)):
            (extensions / name).symlink_to(origin)
        if front is not None:
            shutil.copyfile(front, extensions / FRONT)
        notice = re.sub(r"([!-/:-@\[-`{-~])", r"\\\1", stamp)
        pdf = work / f"{md.stem}.pdf"
        report = ""

        def render(metadata: dict[str, object]) -> int:
            """Render with `metadata`, setting `errors` and `report`; the PDF's page count, 0 where it was refused."""
            nonlocal errors, report
            (work / "metadata.json").write_text(json.dumps(HOUSE_METADATA | {"notice": notice} | metadata))
            run = subprocess.run([sys.executable, str(RENDER), str(source), "--out", str(pdf), "--metadata",
                                  str(work / "metadata.json"), "--format-dir", str(work / "format"), "--notice", stamp],
                                 capture_output=True, text=True, errors="replace")
            lines = (run.stdout + run.stderr).splitlines()
            if run.returncode != 0 or not pdf.is_file():
                errors = [line.removeprefix("refused: ") for line in lines if line.startswith("refused: ")] \
                    or lines[-20:] or [f"the shared renderer exited {run.returncode}"]
                return 0
            errors = []
            report = "\n".join(line.replace(str(pdf), md.stem) for line in lines)
            found = re.search(r": (\d+) pages?,", report)
            return int(found.group(1)) if found else 0

        layout = QUARTO_VERSE if verse else QUARTO_SUMMARY if is_summary(md) else QUARTO_DOCUMENT
        if language in CJK:  # its fonts are cjk_typst()'s, so no main font is named here
            layout = {key: value for key, value in layout.items() if key != "mainfont"} | {
                "lang": language, "region": QUARTO_REGION[language]} | (
                QUARTO_CJK_SUMMARY if is_summary(md) else QUARTO_CJK_DOCUMENT)
        layout = layout | (titled or {})
        pages, size = 0, ""
        metadata: dict[str, object] = {}
        for size in QUARTO_SIZES if is_summary(md) else ("",):
            metadata = layout | ({"fontsize": f"{size}pt"} if size else {})
            pages = render(metadata)
            if errors or pages <= 1:
                break
        if size and not errors and pages > 1:
            over = subprocess.run(["pdftotext", "-f", "2", "-l", "2", str(pdf), "-"], capture_output=True, text=True,
                                  check=True, errors="replace").stdout.replace(stamp, "", 1).split()
            errors = [f"the summary does not fit one page at {size} pt, the smallest body size: it runs to {pages} pages, "
                      f"page 2 holding {len(over)} words from \"{' '.join(over[:12])}\"; it is too long, a fault of "
                      "content for its author"]
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
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, target)
            body = f", body {size} pt" if size else ""
            print(f"{md.stem}: {pages} page{'' if pages == 1 else 's'}{body}{balanced}, {target}")
            print(report)
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
    # What the build reads: the sources, the images they reference, the audience profiles, this script, the house
    # format, the stored fonts, the naming module, and the shared renderer and its base format.
    inputs = set(documents) | {Path(__file__).resolve(), HOUSE_FORMAT, ASSETS, Path(document_names.__file__).resolve(),
                               RENDER, BASE_FORMAT.parent.parent}
    for md in documents:
        inputs |= {(md.parent / m.group(2)).resolve() for m in IMAGE.finditer(md.read_text())}
        if md.parent.parent.name == "audience":
            inputs.add(AUDIENCES / f"{md.parent.name}.toml")
    arguments = f"language={args.language}\nnotice={args.notice or ''}\n"
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
        results.append(build(md, args.language, stamp, target, titled=title(case, md, draft.short, draft.version)))
        if results[-1]:
            shutil.copyfile(target, md.with_suffix(".pdf"))
    if joined:
        # The paper with the summary as its first page, in one run of the paper, so that its links and bookmarks hold:
        # the summary is built again with an empty notice, and the joined file's own notice is drawn over every page.
        identifier = document_names.identifier(draft, JOINED)
        with tempfile.TemporaryDirectory(prefix="typeset-front-") as tmp:
            front = Path(tmp) / "front.pdf"
            results.append(build(summary, args.language, "", front) and build(
                paper, args.language, document_names.stamp(identifier, draft.date, args.notice),
                drafts / f"{identifier}.pdf", front, titled=title(case, paper, draft.short, draft.version) | {
                    "kind": f"Policy paper with summary {draft.version}"}))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
