# The layout review of a case's PDF documents

Version 3, 2026-11-21 (version 2, 2026-11-10): version 1's checks (2026-10-31) merged with the checklist of `research/report_layout.md` section 5, wasted space first. The checklist of the `pdf-layout` agent (`.claude/agents/pdf-layout.md`), the twin of `notes/sheet_layout_review.md`. A bracket names the section of `research/report_layout.md` an item rests on, where its sources and measurements are.

The owner, 2026-11-10: "the margins are absurdly large ... Make a process to do better with pdf layout, with a reviewer prompted with patterns of good design, especially not wasting space."

The owner, 2026-11-21, on a sheet review, ruling for anything generated (his later words govern): "the process when finding a flaw in anything generated shuold always be to fix the generator, never hand edit one of its outputs". The reviewer therefore reports and edits nothing (6).

## 1 Wasted space

Measure first: `.venv/bin/python tools/typeset.py --measure <pdf> --sheets <folder>` prints each PDF's side margins, characters in a full line, text block's share of the page and share of empty quarter-inch squares, with its emptiest pages, and writes a thumbnail sheet of all its pages.

1.1 Margin and line together. One column: a full line of 75 to 90 characters, and side margins whatever that line leaves, at most 1.25 in on letter (IFS: 81 to 88 characters on 1.18 in; RFF's long paper, the one wider precedent, 1.75 in at 82 to 86) [3.1, 3.2, 3.4]. Two columns: 45 to 65 characters a line on sides of 0.5 to 0.75 in [2.8, 3.2]. Fault: sides over 1.0 in round a line under 75 characters, or any side over 1.25 in with nothing beside the text. A line over 90 characters in one column takes two columns or a side column, never wider margins [3.1.3].

1.2 Vertical waste. Fault: a page whose lower quarter is empty while the next opens with a heading, table or figure that could have started on it; a gap above or below a figure or table of more than about a line and a half; a page broken before each section. See it in the thumbnails and the emptiest pages. Fix in the generator's layout files (a finding for a build): float fractions, float spacing, where breaks may fall [3.3, 4.4]. Causes found so far: a float barrier at every heading level (now only at `##`); the summary's column balancer stretching the space round a figure to 26 pt (now rigid).

1.3 A figure the wrong size. A figure is set at the size it was drawn, shrunk to fit the line, never blown up. Fault: a five-bar chart on half a page, a table whose cells hold more white than data, or a figure drawn for another width, whose labels then fall below the floors of 4.6: a finding for the author, who redraws it [4.4].

1.4 Density. Empty quarter-inch squares: 39 to 45 per cent on a one-page summary, 45 to 58 per cent on a paper's text pages [3.2, 3.3]. A page over about 70 per cent that is not a document's last page or a full-page figure is looked at for 1.2.

1.5 Type and leading. Body 9.5 to 11 pt, leading 120 to 145 per cent; no double spacing [3.1.2].

## 2 Attention and hierarchy, every document

2.1 An entry point. Squint at page 1's thumbnail: the eye needs a first place to land, a key-findings box, another box or a side column [2.1, 2.4, 2.5, 4.2].

2.2 Hierarchy. At least three levels, each visibly different, and no more than five sizes: title, then dateline or subtitle, box, headings, body [4.1, 4.2].

2.3 A chart's title states its finding ("The labor force participation rate has declined for men"), its unit and period beneath; one that would read the same whichever way the data came out fails, a finding for the author [2.6].

2.4 Repetition and alignment. One style for each kind of element on every page; flip the thumbnails, and edges fall on a few vertical lines [4.1].

2.5 Proximity. More space above a heading than below it; a caption tight to its own figure; a box's title its first bold words [4.1].

## 3 The one-page summary

3.1 The answer, the headline and its range, within the body's first five lines [2.3].

3.2 At least one device: the key-findings box holding the headline, in bold where it is a number; a callout for what must not be missed; a figure where the page has room [2.4, 2.5, 2.8.1].

3.3 Between about 250 and 550 words on letter [2.8, 3.3].

3.4 One page, its foot not empty. The layout copyfits: the body is the largest of 11, 10.5, 10 and 9.5 pt at which the page fits, and the build prints which. A page that spills at 9.5 pt, or leaves more than about an inch empty at the foot of both columns at 11 pt, is a finding for the author: cut, or add a figure [2.8].

3.5 A compact head: title and dateline across the page, the first body line within about 1.5 in of the top (the briefs measured 1.36 to 1.41 in) [2.8].

## 4 The policy paper and the appendix

4.1 The answer first. The paper states the headline and its interval in its first lines, as text, and has no key-findings box, since the summary's page stands in front of it in the joined file (`notes/briefs/author_documents.md`, message A, 5); a key-findings box in the paper is a finding for the author. The appendix has key findings, or a summary that states them, in its first two pages [2.1, 2.2].

4.2 The worked example, the one unit rebuilt to the headline, in a box near the head. This item is the seat's reading of his words on how think tanks make policy reports, "with worked examples, callout boxes, etc." (the owner's message of 2026-11-10), not a measured norm [2.7]; the one-unit rebuild and its place near the head are the seat's.

4.3 Rhythm. A figure, table or box on most spreads; not every page half figure [2.8.3, 3.3].

4.4 No lonely figure page: a small chart alone on a page fails 1.2.

4.5 Boxes: at most two a page, each about 60 words or fewer (a judgement), each the key number, the action or the example [2.5]. Each explanatory box sits in the section whose table or claim it explains; one set ahead of that section, such as on the paper's second page, is a finding for the author, since moving it changes the order of paragraphs (6.3).

4.6 Legibility. Chart text no smaller than Urban's floors for PDFs: axis and data labels 8.5 pt, legends 9.5 pt, sources and notes 8 pt, and never smaller than the caption. Labels on the data rather than a legend; the unit stated once; one number format a chart; round ticks. A long label wraps at a phrase break, its secondary detail on the second line in the second ink; it is never rotated and never shrinks the data region (Storytelling with Data, 2020; the owner on two-line labels, the owner's message of 2026-10-31: "you could have made the labels take 2 lines and put the SCC under them"; the phrase-break wrap and the no-rotation rule are the seat's). Tables after Schwabish (2020), *Journal of Benefit-Cost Analysis* 11(2): 151 to 178, as in `notes/sheet_layout_review.md` 3.1 [2.6].

## 5 The build is correct

5.1 The page count the document's brief sets (the summary: one).

5.2 The build report of `tools/typeset.py`: no error, no missing character, no overfull box, no font substitution.

5.3 Nothing outside its place: no word past the margin or into the other column and no two words overlapping (word boxes from `pdftotext -bbox-layout`).

5.4 Paragraph shape: no paragraph parted after its first line, by a column or page break or by a change from full width to columns (the owner, 2026-11-13: "you don't chop up a paragraph after its first line"); no line of one short word ending a paragraph; no heading, and no line that introduces a list, at a column's foot; no more than two hyphenated lines running; no number parted from its unit.

5.5 The tops of side-by-side columns level; the same gap between sections everywhere.

5.6 A reader moves through the file by clicking. The owner, 2026-11-13: "make sure we do all the normal user friendliness things in the pdf: any reference to a table or figure or section is a clickable link to that part of the file, there's a clickable table of contents, every citation is also a clickable link instead of just an endnote, etc." These hold for every PDF a case builds; the typesetter makes them (`tools/typeset.py`; `tools/typeset_layout/typeset-links.sty`).

5.6.1 Contents. A document of more than about four pages opens with a contents list, every entry a link to its section. The one-page summary has none.

5.6.2 Bookmarks. The file carries an outline of its headings, so a reader's side panel lists the sections.

5.6.3 Cross-references. Every mention in the text of a section, table, figure, box or equation is a link to it, written in the source as a label and never as a typed number, so a number cannot go stale when a section moves.

5.6.4 Citations. Every citation in the text is a link to its entry in the reference list, and every entry's DOI or address is a live link to the source.

5.6.5 Addresses. Every web address or email address shown anywhere is a live link.

5.6.6 Metadata. The file's properties give its title, its authors and its language.

5.6.7 Appearance. A link is marked by color alone, with no box round it, in an ink dark enough to read when printed in gray.

5.6.8 Fault: a link whose target is missing, a typed "section 4" or "Table 2" with no link, a citation that is a bare number, a file with no outline. The build report counts contents entries, bookmarks, links within the file and links out of it, and the reviewer reads the counts.

## 6 What the reviewer reports, and to whom

6.1 The reviewer edits no file and no PDF. Each fault is a finding with its document, its page, the fault as the page shows it, the part of the generator that made it, and the fix there. The only write is the build that makes the PDF, the generator's normal run.

6.2 A fault in the layout files of `tools/typeset_layout/` (the templates `summary.tex`, `document.tex` and their CJK twins, float sizes and spacing, box styles and break rules) or in `tools/typeset.py` is a finding for a `build` of the generator. They serve every case, so the finding names the file and line, says what the fix does to other documents, and names one other case's documents to rebuild to see it.

6.3 A fault in the box marks of a case's `documents/*_template.md` (`::: key-findings`, `::: callout`, `::: worked-example` and the closing `:::`; `tools/typeset.py`'s help) is a finding for the case's author, with the line and the mark to put or take out.

6.4 The seat that dispatched the review sends the findings to a `build` of the generator or to the case's author, then builds the documents again by the normal route. A PDF already delivered that carries the fault stays as it is until that build.

6.5 A fault of content goes to the case's author as a finding, with its document, its page and its line in the Markdown: a summary too long or too short, the answer not first, a chart title that describes, a figure drawn for another width, a table too wide, an equation wider than the line.

## 7 How and when

7.1 Once a case's documents are final and built, before anyone sees them, and again after any later edit to a document: every edit is followed by a build and a look, since an edit can break a page in ways that show only in the render (8.1).

7.2 Measure (1); look at the thumbnail sheets; render every page at 110 dpi (`pdftoppm -r 110`), with 200 dpi crops for small text; check sections 1 to 5; report by 6. One round of looking, since nothing is fixed in it; a second build and look follows when the generator has been fixed and the dispatching seat asks.

7.3 On Sonnet, a seat other than the writer, who knows what the page means and so cannot see it as a reader does.

## 8 Weighing (CORE rule 10)

8.1 Caught: faults that show in the render and in none of the numbers, such as a second page, wrong legend swatches, a footer pushed off or a plot narrowed by its labels, each following an edit, and margins that waste the page; each, unchecked, can reach the owner.

8.2 Cost: the measures and the build report are free once written. A review is one Sonnet run of one or two rounds over a case's pages. A run over seven to nine pages has cost about $0.50 at the price table's rates (`shared/tools/token_prices.json`), in about 25 tool calls and three minutes; every page of a 25-page paper adds some 1,500 tokens an image, perhaps $0.50 more. That is against a fault that costs the owner a screenshot and a message, and a client a worse page.
