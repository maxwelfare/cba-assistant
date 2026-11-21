# The layout review of a case's Google Sheet

Version 2, 2026-11-21 (version 1, 2026-10-31). The owner asked for it: "design a UI subagent review of the sheet to look for and fix these kinds of things. Lookup best practice or scripts or libraries first, I cannot be the first one who wants to automate making a sheet look right". The same morning he set two of its rules: "make the font size at least 11, I look at this on a laptop" (superseded: Arial 10; his "a, my old order was confused", the owner's message of 2026-11-20, choosing the seat's Decision 19 option A: "Arial 10 in every cell of every tab, including headers, notes, tables and the Guide. Only a tab's title is set apart, by bold at a larger size") and "apply formatting where appropriate especially percentages and money figures". On 2026-11-21 he ruled what "fix" means, and his later words govern: "\"The layout look already fixed both by hand on the live sheet. \" this should not happen. the process when finding a flaw in anything generated shuold always be to fix the generator, never hand edit one of its outputs". The review reads the sheet and reports; the fix is made in the generator (`tools/sheet_script.py`, its layout files or the case's data file), and the sheet is written again by the normal route. A step of the sheet twin (`notes/case_pipeline.md` 3.2.3); the layout rules it checks are the sheet-twin protocol's 2.3.6.

## 1 Why

1.1 Without it, layout faults reach the owner, who finds them by eye: for example, columns too wide, or words broken across lines in a narrow column, which a rule that every text cell wraps can cause. Each costs him a look, a screenshot and a message.

1.2 Neither fault shows in the values the sheet-twin agent reads back, so its checks (protocol 2.4) cannot see them.

## 2 What exists

Searched 2026-10-31. Nothing lints or fixes the layout of a Google Sheet:

2.1 Spreadsheet Preflight, a Workspace add-on, checks sheets against rules it does not publish.

2.2 ExceLint (Barowy, Berger and Zorn, OOPSLA 2018) and Formula Foundry find formula errors, not layout.

2.3 The xlsx-verify skill renders an Excel file and lints it; it does not read Google Sheets.

2.4 The Sheets API resizes rows and columns to their content (`autoResizeDimensions`): a fix, not a check.

The standards exist and the checker does not, so the review applies the standards by rule, then by eye.

## 3 The standard

3.1 Schwabish, J. (2020), "Ten Guidelines for Better Tables", *Journal of Benefit-Cost Analysis* 11(2): 151–178, doi:10.1017/bca.2020.11, the field's own journal. The guidelines applied here: offset the heads from the body (1); right-align numbers and their heads (3); left-align text and its heads (4); show the precision the reader needs (5); guide the eye with space (6); put the unit in the head, not in every cell (7).

3.2 The modelling codes the protocol already cites (FAST; ICAEW) for one format per column and inputs styled apart from calculations.

3.3 The owner's rulings: Arial 10 in every cell, a tab's title alone bold and larger (his "a", the owner's message of 2026-11-20, choosing the seat's Decision 19 option A, which set both), while model and input tabs keep his template's widths and alignment (protocol 2.3.6; his words on alignment, the owner's message of 2026-11-16: "left justify the mins (7 and 13 on templater) right justify the maxes and center the means"; that the template's widths stay is the seat's reading, beside his the owner's message of 2026-11-20: "keep the columns narrower like before if possible"); narrow columns and text rows tall enough to read in place (his the owner's message of 2026-10-31: "The current draft has colums that are too wide, meaning more scrolling is needed, and the rows with text should be longer"); percentages and money formatted (the owner's message of 2026-10-31: "apply formatting where appropriate especially percentages and money figures"); the header rows of his own sheets (protocol 2.3.5).

## 4 The checks

Each is a rule over the grid's metadata (`spreadsheets.get` with grid data: effective format, width, height, wrapping, merges), then a look at the render.

4.1 Type: every cell Arial 10, a tab's title alone bold and larger. Model and input tabs keep the template's widths and alignment (mins left, means centred, maxes right); do not restyle them. Font colour marks a cell's kind (his "a", the owner's message of 2026-11-20, choosing the seat's Decision 23 option A: "Use the usual modelling convention: blue for a value someone may change, black for a formula, and green for a formula that reads another tab"): input blue for a value someone may change, black for a formula, green for another tab's cell carried over unchanged (a plain reference or a lookup returning one; a formula that computes is black whatever tab it reads; protocol 2.3.6), and every hyperlink on every tab the normal hyperlink blue, underlined (the owner, 2026-11-21, overruling the seat's earlier choice for links: "no everyone expects hyperlinks to be blue. Use normal hyperlink blue for them and a different blue for inputs, and make sure the explanation sheet has the convention, with examples"); the Guide carries a colour key with one row per kind: a sample in its colour, a plain sentence, and a real example cell of that kind from the sheet; his template's red and green text, which no file explained, is replaced by it. The seat's choices, not his: link blue #1155CC (Google's own link colour), underlined; input blue #0000FF, never underlined; green #008000; Results and Sensitivity otherwise black. The check reads each cell's effective font colour against its kind.

4.2 Formats by unit: a probability or share as a percentage; money with a dollar sign and thousands separators, its unit in the head; a year with no separator; a count with separators. Every number a reader sees (an input's parameters, rows 12 to 14, the draws, Results, Sensitivity and every table) shows two significant figures, by its number format, never by rounding a value; a large one shows in a scaled unit (thousand, million, billion, trillion) chosen from its column's or block's values and named in words in its column's name or its table's head, never by a letter in the cells (2,970,000,000 shows 3.0 under "(billion)", never 2.97; R57 round 5), on every tab, model tabs included (the owner, 2026-11-20 local, not yet in the register: "fix the geenrator so it lists numbers in million or billion or trillion when appropriate, this is bad and the earlier sheets we made did better", and of "2.97 billion": "no thats 3 sigfigs which I know Ive complained about before too and this forgot"). Kept exact: a year, a label, the draw numbers in column A. A whole number from 100 to 999 shows its three figures, since a format chooses decimals only (the seat's reading of his words, the owner's message of 2026-11-16: "sometimes this wont work because it only lets you choose decimals"). A column's unit is read from its head and from the Variables tab.

4.3 No word broken across lines: in a wrapped cell, the longest word is narrower than its column (estimated as characters × 0.55 × the size in pixels, plus 10 px of padding; the factor is checked against the render).

4.4 No paragraph in a narrow column: text that would wrap past about five lines in a column under 150 px gets its column widened (a text column up to 600 px), or moves to the tab's wide column; never a merge (the five lines, the 150 px and the 600 px are the seat's). The owner, the owner's message of 2026-11-20, replacing the merge rule: "the actual rule is to widen the column if you can, merging causes all kinds of mess".

4.5 Nothing hidden: no text clipped by a filled neighbour, no number shown as `###`. The one exception is a citation or note cut off at the foot of its fixed-height header row (4.7).

4.6 Alignment: numbers right, text left, each head aligned with its column.

4.7 Widths and heights as the protocol's 2.3.6 sets them. The header rows keep their fixed heights, at most about 420 px together, so that three draw rows show under them on a laptop screen (about 490 px of grid) without scrolling, and are never grown to fit their text; every other row is tall enough for its wrapped text.

4.8 Heads: row 1 frozen, and in the model tabs column A too; a sheet built on his template keeps the template's panes. Header text is not bold, so that more of it shows (4.7; `notes/sheet_twin_protocol.md` 2.3.6).

4.9 Table tabs: no error value (#N/A, #VALUE!, #REF!) in any cell, every number formatted (4.2), every interval text at two significant figures.

4.10 A column's note is true of what the column now holds: a note copied from an imported sheet that names another currency, unit or source than the column's is a fault of content, reported (register 4.2).

4.11 A sheet's headline compares its result with the bar of the best other use of the money, as the owner's original sheet compared its benefit-cost ratio with GiveWell's top charities (the owner, 2026-10-31: "the headline result should compare the benefit cost ratio to givewell top charities, like the original sheet did at the end"); the generalisation to the best other use of the money, and the reporting of a sheet without one, are the seat's (register 6.7).

4.12 In a client sheet converted to the template, a fact a statistics office publishes (a salary, a population, a price) is sourced, not judged (the owner, 2026-11-20: "why would you just make something up for basic facts like korean researcher salary instead of finding a source?"); a judged input whose fact is published is reported (register 6.6).

## 5 The render

5.1 The Drive connector exports the whole workbook as one PDF, laid out as Google draws it (`download_file_content` with `exportMimeType` `application/pdf`); `pdftoppm` turns its pages into images, and `pdftotext` finds the first page of each tab by the tab's title text. The export shows a fault of layout as a screenshot of the sheet does.

5.2 The reviewer looks at the first page of each tab against section 4, and at what no rule sees: a head that reads badly, a block that should be grouped, a chart cut off.

5.3 Render, look, render once more and look again: two renders at most. The reviewer writes nothing to the sheet; it reports what the renders show, as findings (6).

## 6 What it reports, and to whom

6.1 The reviewer reads the sheet and reports each fault as a finding. It never writes to the sheet: no `update_spreadsheet`, and no other route into it.

6.2 Each finding names the cells (tab and range), the fault as Google displays it, the part of the generator that made it (the script `tools/sheet_script.py`, its template or layout files, or the case's data file) and what the fix there would be.

6.3 The faults are of formats, fonts, widths, heights, wrapping, alignment, merges and frozen panes, which the generator sets. A fault of content (a wrong value, a display formula that prints the wrong thing) is a finding for the case's author, as before.

6.4 The seat that dispatched the review sends the findings to a `build` of the generator, or to the case's author for a data-file fault. It then regenerates and writes the sheet by the normal route (`notes/sheet_inplace_route.md` for a delivered sheet). A sheet already live that carries the fault stays as it is until that regeneration.

## 7 Who runs it, and when

7.1 After the sheet-twin's build and checks (protocol 2.4), before the owner sees the sheet.

7.2 A different seat from the builder, on Sonnet: the builder makes the faults, and the review must look at images and judge them.

7.4 Every upload or in-place write of a sheet ends with this look before anyone is told the sheet is ready (register 8.1); a fault it finds is reported (6) and goes to a build of the generator, which fixes it in the script or the data file and adds its test to the suite (register 8.2); the next regeneration carries the fix, and nothing is fixed live.

7.6 The note delivered beside a changed sheet lists what changed, briefly, and no results comparison (the owner, 2026-11-20: "the change document should just be about what actually changed, not a results comparison"; register 8.6).

7.3 The rules of section 4 become a script over the saved grid metadata once a trial run has shown which of them catch real faults; the script then runs inside the sheet-twin's build as well, so that most faults never reach the reviewer.

## 8 Weighing (CORE rule 10; the shared `standards/process/controls.md`)

8.1 What it catches, for the generator to fix: faults like those of 1.1, and the size and formats the owner asked for on 2026-10-31 (the owner's message of 2026-10-31: "make the font size at least 11, I look at this on a laptop" and "apply formatting where appropriate especially percentages and money figures"; the size is since superseded, 3.3).

8.2 What it costs: one Sonnet run reading the grid metadata and about fifteen page images a round, two rounds at most; the script, once written, costs nothing to run. Against that, each fault that reaches the owner costs him a look, a screenshot, a message and a rebuild round.

8.3 A trial run measures the cost and records which check found what; a check that finds nothing in three builds is weighed again.
