# How think tanks lay out reports and one-page briefs, and what a layout reviewer can check

Research note, 2026-11-10, for the PDF-layout process the owner asked for ("the margins are absurdly large ... Make a process to do better with pdf layout, with a reviewer prompted with patterns of good design, especially not wasting space"). It does not look at the project's own documents or typesetter. Sources are in `research/sources/<key>/` and indexed in `research/refs.toml`. A quote in double marks was machine-checked against the stored `text.txt` and is followed by [key, place]. A source marked "recalled" was not read this session and has no quote. Page measurements were made from the stored PDFs with `pdftotext -bbox` (word bounding boxes) and by counting the quarter-inch squares of a 48 dpi render that hold any dark pixel; neither pdfplumber nor PyMuPDF is installed in the project venv. Type sizes are estimates from word-box height and line step, not read from the font files.

## 1. How the work is done

1.1 What was found and what was not. Think tanks publish style guides for charts and job advertisements for their staff; they do not publish a production workflow. The Urban Institute's chart guide, one Urban post, one job advertisement and Young and Quinn's guide give the roles. Nothing was found on the production steps at RFF, Brookings, IFS or the Resolution Foundation. The sites of RAND and the Congressional Budget Office refused the fetch (HTTP 403 to a polite request), so nothing from them is stored and nothing from them is used below.

1.2 The roles at the Urban Institute.

1.2.1 A design and communications team sits beside the researchers. Schwabish's Urban Wire post: "we have built out a strong, flexible digital team who work alongside writers, editors, and media relations teams to share Urban’s research." [schwabish_2015_unicorn, para. 2]. It gives the scale: about 350 researchers and analysts, and a team grown "in design, programming, data visualization, communications, and dissemination" [same, para. 6]. The post is on PolicyViz, Schwabish's site; its text names no author, so the attribution to Schwabish is inferred.

1.2.2 A data-visualisation designer works under the Office of Communications. The 2018 advertisement asks the designer to "Collaborate with researchers and communications staff (designers, developers, writers, and editors) on the conception and design of interactive data visualizations." and to "Create and refine static data visualizations for a range of publications based on our comprehensive communications standards." [onthinktanks_urban_designer_2018, responsibilities]. Charts are made by a specialist to a house standard, not by the author.

1.2.3 The house standard is a template system. Urban's Data Visualization Style Guide says its guidelines reduce "the burden of design and color decisions on individual researchers and analysts" [urban_graphics_styleguide, introduction]. It fixes one typeface: "Urban uses the Lato font for all our products, including the website, PDF publications, and presentations." [urban_graphics_styleguide, Typography]. Of the publication templates: "Urban Microsoft Word templates have built-in formatting to ensure correct placement of figures." [urban_graphics_styleguide, Inserting Figures into Urban Word Templates] and "Urban Word templates have built-in styles that apply proper line spacing, paragraph indents, and heading hierarchy without relying on manual formatting." [urban_graphics_styleguide, Accessibility]. Authors write into a template whose styles fix spacing and hierarchy; the template, not the author, owns the layout.

1.3 The roles and steps in a policy paper's publishing, from Young and Quinn (2002).

1.3.1 The people: "typically involves a number of individuals, e.g., editor, copyeditors, proof-readers, reviewers, and of course, the writer." [young_2002_writing, 6.3, p. 94]. Reviewers judge content; the proof-reader judges language, style and tone (same place, paraphrase). "Editing is a process of negotiation." [same].

1.3.2 Layout is a separate trade. The guide's imprint reads "Design & Layout by Createch Ltd." [young_2002_writing, imprint], and the acknowledgements thank a person "for the design and layout of this book" [same]. The guide says little about page layout itself; it tells writers to follow the publisher's: "Many publishers assist writers in the process of targeting their writing to their requirements by producing guidelines." [young_2002_writing, 6.1, p. 86].

1.3.3 The steps the sources give: planning against the publisher's guidelines; a full draft; internal feedback; submission to the editor; review and copy-editing; then production. Layout in the publisher's template, proofs and press are the usual order and are recalled, not stated by these sources.

1.4 What follows for this project. A think tank's page looks professional because of three things the sources show: a fixed template with named styles, a person whose job is the look, and an editor who reads against house rules. A reviewer agent stands in for the second and third; the first is the typesetter's stylesheet, which this note does not examine.

## 2. The anatomy that calls attention to what matters

2.1 The key-findings list at the top. IFS Briefing Note BN259 opens with a short executive summary and a list headed "Key findings", each item a full sentence whose first clause is the claim: "Taxes in the UK are high by historical standards." [ifs_2019_adam_bn259, p. 3]. The Hamilton Project (Brookings) puts three bulleted takeaways on page 1: "Among the key takeaways of the analysis are:" [hamilton_2016_bauer_head_start, p. 1]. Urban's SNAP brief is built as four key findings, each with a heading that is itself the finding: "SNAP IS A VERY EFFECTIVE TOOL FOR REDUCING FOOD INSECURITY" [urban_2023_waxman_snap, p. 1].

2.2 The summary that stands alone. "The abstract or executive summary should be much more than just a cut and paste from your completed policy paper." [young_2002_writing, 5.4, p. 35]. The Resolution Foundation's 30-page report gives its executive summary a full page (page 3) in larger type than most briefs (about 13.5 pt on 18 pt leading, measured) [resolution_2025_spending_review, p. 3].

2.3 The inverted pyramid. The answer first, then support in decreasing importance, is the newspaper form; Minto's Pyramid Principle is its business-writing twin. Both are recalled. RFF's issue brief does it: the first column of page 1 states the verdict ("likely to greatly exceed the costs"; about $30 billion per technology; about 7 times) before section 1, "Context" [shawhan_2021_rff_issue_brief, p. 1].

2.4 The side column of key points. Urban's two-page "Understanding Synthetic Data" sets a narrow left column of four short summary statements beside the main text, separated by rules, with key terms in colour; the first begins "Synthetic data replace actual records" [urban_2023_pickens_synthetic, p. 1]. A reader who reads only the left column gets the argument. The main column carries run-in headings such as "WHY SYNTHETIC DATA?" [same].

2.5 The callout box and the action box. Urban's one-page fact sheet puts a solid blue box in the right column listing the eleven occupations covered, and a grey box with the one action wanted ("Access the National Occupational Frameworks at ...") [urban_2023_fact_sheet_nof, p. 1]. Boxes hold what a reader needs to act on or look up, not paragraphs of argument.

2.6 Chart titles that state the finding. Urban: "Try to explain the chart in a few words and draw conclusions where possible." [urban_graphics_styleguide, Titles]. Its example turns "Labor Force Participation Rate, Men and Women, 1950–2024" into "The Labor Force Participation Rate Has Declined for Men and Increased for Women." [same]; and "Annotation is one of the most important ways to improve your data communication efforts." [same, Annotation]. RFF's own brief does not follow this: its figure titles are descriptive ("Figure 2. Estimated Average Cost Reductions in 2035 Due to 10-Year RD&D Funding") and the finding is in the text beside the chart ("Figures 2 and 3 provide a few key takeaways:") [shawhan_2021_rff_issue_brief, p. 3]. The named model is good on layout, not on this point.

2.7 Pull quotes, the worked example and summary tables. No stored brief uses a pull quote, so none is measured. The worked example (one unit, then the multiplication to the headline) was not found as a named device in any stored brief; RFF's brief opens with the verdict and the per-technology average, which is the informal version. Summary tables are Schwabish (2020, `schwabish_2020_tables`, recalled) and not checked here.

2.8 Three real short briefs, as the page is drawn. Letter paper, 8.5 by 11 in. "Empty squares" means quarter-inch squares with no dark pixel; they include margins, gaps between paragraphs and white inside tables, so they overstate pure margin. Text/box/image shares are by eye.

2.8.1 Urban Institute fact sheet, "National Occupational Frameworks", page 1 of 2 [urban_2023_fact_sheet_nof]. Top: logo, a bold 26 pt title and an italic blue subtitle that states the purpose, with a small product image at right. Then two short opening paragraphs full width. Then two blue small-caps headings phrased as the reader's questions ("What are the benefits of using the frameworks?"), each over three or four bullets whose first words are bold. Lower right: a solid blue box listing the occupations covered. Lower left: a grey box with the one action. A footer rule carries the address. Measured: 260 words; side margins 0.50 and 0.56 in; text block 67 percent of the page; 39 percent of squares empty. By eye: text about 45 percent of the page, boxes about 12 percent, image about 4 percent, the rest white.

2.8.2 Urban Institute, "Understanding Synthetic Data", page 1 of 2 [urban_2023_pickens_synthetic]. Logo, 20 pt title, italic subtitle, authors. Below, a two-column grid: a narrow left column (about 1.8 in) of four summary paragraphs with rules between, and a main column of about 4.8 in. Measured: 468 words; side margins 0.60 in; text block 61 percent; 40 percent of squares empty. Nearly all of the page is text; the left column is the only device and it carries the summary.

2.8.3 RFF issue brief 21-10, page 1 of 5 [shawhan_2021_rff_issue_brief]. A pale blue banner across the top holds the logo, a 20 pt title (the page's largest type) and the byline. Below, two columns: left an unheaded summary of five short paragraphs, right the numbered heading "1. Context" and its text. A footnote rule at the foot. Page 3 is about 40 percent figure: a bar chart in the left column and a full-width box-and-whisker chart with a legend. Measured: 467 words; side margins 0.75 in; line about 54 characters; 51 percent of squares empty (the banner is pale, so it counts as empty); top offset to the first body line 1.37 in.

2.8.4 Reading across the three. Each puts the title in the page's largest type, states the purpose or verdict within the first five lines, and uses a second column or a box for what the reader must not miss. Words on page 1: 260, 468, 467. None runs a single measure from edge to edge.

2.9 Two longer-report pages. IFS BN259 page 3 (executive summary with key findings): 413 words, side margins 1.18 in on A4, body block 50 percent of the page [ifs_2019_adam_bn259]. Resolution Foundation page 3: 477 words at about 13.5 pt on A4, side margins 0.83 in, body block 64 percent [resolution_2025_spending_review].

## 3. Page geometry and typography that do not waste space

3.1 What the rules say.

3.1.1 Line length. "Aim for an average line length of 45–90 characters, including spaces." [butterick_line_length]. Bringhurst gives about 45 to 75 characters with 66 ideal; recalled, not read.

3.1.2 Size and leading. "In print, the optimal point size for body text is 10–12 point." [butterick_point_size]. "For most text, the optimal line spacing is between 120% and 145% of the point size." [butterick_line_spacing].

3.1.3 Butterick argues for large margins, because they set the line length. "At 12 point, left and right page margins of 1.5–2.0″ will usually give you a comfortable line length." [butterick_page_margins]; "The smaller the point size, the larger the page margins will need to be, and vice versa." [same]. That is the opposite of the owner's complaint. The resolution is in the same page: "To fit more text on the page, reduce the top and bottom margins." [same], and "do any of those magazines run text in a single block on the page with one-inch margins? No—never. They use multiple-column layouts or find other ways to divide the page." [same]. A wide margin is harmless only when it is the price of a good line length; it is waste when the line is already short, or when the page is a single narrow column with nothing beside it. At 10 pt, a line of about 85 characters needs sides of about 1.0 to 1.25 in on letter, not 1.75 in. Two columns allow 0.6 to 0.75 in.

3.1.4 Columns and the margin column. Tufte sets text in a main column beside a wide margin column for notes, small figures and captions; recalled, not read (`tufte_2001_visual_display`). Urban's sidebar (2.4) is a working example with a narrow margin.

3.2 What the stored documents do (measured). Eleven documents or briefs, 15 pages in the density count, so the figures are ranges, not norms. Line length is the median number of characters per full text line from word boxes, merged across columns where there are two. Squares as in 2.8.

3.2.1 RFF issue brief 21-10 (letter): sides 0.75 in; two columns, about 54 characters per line; about 10 pt on 14 pt leading (140 percent, estimated); 45 to 55 percent of squares empty [shawhan_2021_rff_issue_brief].

3.2.2 RFF working paper 21-10, the long document of the same study (letter, 38 pp.): sides 1.75 in on text pages (the two margins are 41 percent of the page width); a single column about 5 in wide, 82 to 86 characters per line; about 10 pt on 13 pt leading (130 percent, estimated); the text block is 42 to 48 percent of the page on full text pages; 58 percent of squares empty on page 7, 66 percent on page 2. Pages that carry a wide table or figure (page 11) use 0.89 in sides [shawhan_2021_rff_wp2110]. So the owner's named model is generous in margins in its long report and tight in its brief. Which one he has in mind is not said in his words; both are measured so the reviewer's benchmark can be set against either.

3.2.3 Urban Institute (letter): sides 0.50 to 0.75 in; a single column of about 100 characters (SNAP brief, above Butterick's 90) or a two-column grid (synthetic-data brief); about 9.5 to 10 pt on 14 to 15 pt leading; 39 to 56 percent of squares empty [urban_2023_waxman_snap; urban_2023_fact_sheet_nof; urban_2023_pickens_synthetic].

3.2.4 Hamilton Project (letter): sides 1.0 in on page 1, 0.5 in on text pages; about 100 characters per line on text pages; about 10.5 pt on 14 pt leading; 46 to 50 percent of squares empty [hamilton_2016_bauer_head_start].

3.2.5 IFS BN259 (A4): sides 1.18 in (14 percent of the width each); 81 to 88 characters; body block 50 to 58 percent; 54 to 56 percent of squares empty [ifs_2019_adam_bn259].

3.2.6 Resolution Foundation Spending Review (A4): sides 0.83 in; about 87 characters; about 13.5 pt on 18 pt leading (133 percent); body block 59 to 64 percent; 39 percent of squares empty on page 3 [resolution_2025_spending_review].

3.2.7 Young and Quinn's book: a small trim (6.5 by 9.4 in); 43 percent of squares empty on page 50 [young_2002_writing].

3.3 What the numbers say. Side margins of 0.5 to 0.83 in, with the line held readable by two columns or a sidebar, are the brief norm in this sample; 1.18 in appears at IFS on A4; 1.75 in appears only in RFF's long working paper. Across all pages measured, 39 to 58 percent of the squares are empty; the one-page fact sheets sit at 39 to 43 percent. Letter pages carry 260 (a fact sheet's front page with a large header) to about 540 words. The gap between a good page and a wasteful one is therefore not mainly the side margin; it is whether the width left inside the margin is used (two columns, a sidebar, a box) and whether the vertical gaps (above headings, around figures, at the page foot) are bounded.

3.4 A starting range for the reviewer (derived from 3.1 and 3.2; the owner's to rule on). Letter or A4; type 9.5 to 11 pt; leading 120 to 145 percent; side margins 0.6 to 1.0 in; top and bottom margins 0.7 to 1.0 in; one column only if the line then stays at 90 characters or fewer, otherwise two columns or a 1.8 to 2.0 in side column; a bottom margin a little larger than the top ("try making the bottom margin about a 0.25″ larger than the top margin" [butterick_page_margins]).

## 4. Design principles a reviewer can apply to a rendered page

4.1 The four principles. Robin Williams, The Non-Designer's Design Book: contrast (make different things clearly different), repetition (repeat fonts, colours and rules), alignment (every item lines up with something else) and proximity (items that belong together sit together, and separate items are separated). Recalled, not read (`williams_2015_nondesigners`).

4.2 Visual hierarchy. Urban: "Good chart typography creates a hierarchy among elements and guides the reader through the visual." [urban_graphics_styleguide, Typography]. In the briefs of section 2 the eye's order is: title, subtitle or verdict, key box, section headings, body. Butterick on emphasis: step sizes up in small, few increments [butterick_point_size, "Point size as emphasis"; paraphrase].

4.3 Common faults of amateur layouts, drawn from sections 2 and 3 and from Butterick's summary [butterick_key_rules]: one long single column from margin to margin (6.5 in on letter paper, a typewriter habit); body in 12 pt at single or double spacing; headings the same size as the body or differing only by bold; no element that says which sentence matters; chart titles that describe rather than conclude; large gaps above and below figures and before headings, or a half-empty page before each section; tables whose cells hold more white than data; text and boxes that touch; defaults throughout (font, margins).

4.4 Waste has three kinds, each visible: margin waste (a narrow text strip with nothing beside it), vertical waste (gaps around floats, headings and page breaks) and content waste (a figure or table drawn larger than its information needs). Section 3.2.2 shows RFF's long paper has the first kind; a reviewer should treat it as a trade against line length, not an automatic fault.

## 5. A checklist for a layout reviewer

The reviewer looks at each page image, then at all pages as thumbnails. Each item names the fault, how to see it, the fix and its source in sections 1 to 4. Values are starting ranges from the sample in section 3; the owner or the reviewer may tighten them. Wasted space comes first.

5.1 Both documents: wasted space.

5.1.1 Margin waste. Fault: side margins above 1.0 in with a single column and nothing beside the text. See it: a thin text strip on a white page; side margin over about 12 percent of the page width each side. Fix: sides 0.6 to 1.0 in, and two columns or a side column to hold the line at 90 characters or fewer. Source: 3.1.3, 3.2, 3.3.

5.1.2 Short line with a large margin. Fault: both at once. See it: fewer than 45 characters per line, or a text block under 55 percent of the page area. Fix: widen the block until the line is 55 to 90 characters. Source: 3.1.1, 3.2.

5.1.3 Overlong line. Fault: more than 90 characters per line on a single wide column. See it: count one full line. Fix: two columns or a margin column; do not widen the margin just to cut the line. Source: 3.1.1, 3.2.3.

5.1.4 Vertical waste. Fault: a page whose lower third is empty because the next block would not fit, or a gap after a figure. See it: in thumbnails, white below the last block while the next page starts with a heading or float. Fix: let text flow, reorder, or shrink the float; no forced page break before each section. Source: 3.3, 4.4.

5.1.5 Float larger than its content. Fault: a five-bar chart on half a page, a table with wide empty cells. Fix: size to the information. Source: 4.4, 2.6.

5.1.6 Overall density. Fault: too many empty squares. See it: count quarter-inch squares with no ink (a tool can do it). Benchmark: 39 to 45 percent empty for a one-page summary, 45 to 58 percent for a policy-paper text page. Fix: whichever of 5.1.1 to 5.1.5 applies. Source: 3.2, 3.3.

5.1.7 Type size and leading. Fault: body type over 11.5 pt, or leading over 145 percent, or double spacing. See it: loose lines; baseline step over 1.45 times the type size. Fix: 9.5 to 11 pt on 120 to 145 percent. Source: 3.1.2, 3.2.

5.2 Both documents: attention and hierarchy.

5.2.1 No entry point. Fault: nothing tells the reader what matters. See it: squint at the thumbnail; if the eye has no first place to land, it fails. Fix: a key-findings list, a box or a sidebar on page 1. Source: 2.1, 2.4, 2.5, 4.2.

5.2.2 Flat hierarchy. Fault: title, headings and body look alike. See it: fewer than three distinct levels, or a heading no larger or bolder than the body. Fix: fixed levels, each visibly different (contrast), no more than four or five sizes. Source: 4.1, 4.2.

5.2.3 Descriptive chart titles. Fault: the title names the data, not the finding. See it: if the title would stay the same whichever way the data came out, it fails. Fix: "The ... has ..." with unit and period in a subtitle. Source: 2.6.

5.2.4 Repetition and alignment. Fault: boxes, headings and captions styled differently from page to page, or off the grid. See it: flip the thumbnails; edges should fall on a few vertical lines. Fix: one style per element, drawn to the grid. Source: 4.1.

5.2.5 Proximity. Fault: a caption nearer the next figure than its own, a heading nearer the paragraph above than below. Fix: more space above a heading than below; caption tight to its figure. Source: 4.1.

5.3 The one-page summary.

5.3.1 No answer in the first five lines. See it: read them. Fix: the headline result and its range at the top, as in RFF's brief. Source: 2.3, 2.8.3.

5.3.2 A wall of text. Fault: no box, no side column, no bold lead-ins. See it: count the devices. Fix: at least one box or side column holding the number or the action to take away. Source: 2.4, 2.5, 2.8.1.

5.3.3 Wrong amount on the page. Fault: under about 250 or over about 550 words on letter paper. See it: count. Fix: cut or add to the benchmark (260 on Urban's fact sheet front page, about 470 on the others). Source: 2.8, 3.3.

5.3.4 Spills or ends half empty. Fault: not one page, or a large gap at the foot. Fix: adjust content and box sizes, not margins alone. Source: 5.1.4.

5.3.5 Header eats the page. Fault: logo, title and byline over a quarter of the height. See it: top offset to the first body line (the samples measured 1.36 to 1.41 in of 11). Fix: a compact header. Source: 2.8.1 to 2.8.3.

5.4 The policy paper.

5.4.1 No key findings or summary up front. See it: pages 1 to 3. Fix: a summary with key findings in the first two pages. Source: 2.1, 2.2.

5.4.2 A worked example absent or buried. Fault: the headline cannot be rebuilt from its parts. Fix: the example at the head, in a box or lead-in so it stands apart. Source: 2.7 (not seen as a device in the stored briefs; this item rests on the owner's own request, not on a sampled norm).

5.4.3 Page rhythm. Fault: pages that are all running text, or every page half figure. See it: thumbnails; aim for a float, box or table on most spreads. Fix: break long text with a box, table or figure, one box per spread. Source: 2.8.3, 3.3.

5.4.4 Lonely figure pages. Fault: a single small chart alone on a page. Fix: float beside text or in the margin column. Source: 3.1.4, 4.4.

5.4.5 Callouts misused. Fault: more than two boxes on a page, or a box with more than about 60 words (the 60 is a judgement, not sampled). Fix: boxes only for the key number, the action or the example. Source: 2.5.

5.4.6 Legibility. Fault: low-contrast colour, chart text smaller than body, a legend instead of direct labels. See it: view at 100 percent. Fix: direct labels, a title, a source line and labelled axes, as Urban requires: "avoid using legends and instead directly label the data on the graph." [urban_graphics_styleguide, chart rules]. Source: 2.6.

## 6. Works not obtained

6.1 RAND research briefs and style manual, and CBO "At a Glance" pages: the sites refused a polite request (HTTP 403); none is stored.

6.2 Not read this session (recalled): Schwabish, Elevate the Debate (2020) and Better Data Visualizations (2021); Williams, The Non-Designer's Design Book; Tufte, The Visual Display of Quantitative Information and Beautiful Evidence; Bringhurst, The Elements of Typographic Style. No free copy is stored for any.

6.3 No one-page document from RFF was found; its issue brief is five pages and its working paper 38. The one-page brief stored is page 1 of Urban's two-page fact sheet; Urban's synthetic-data note is two pages, and the Hamilton paper (eight pages) is stored for its first page only.
