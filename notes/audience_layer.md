# The audience layer: a design

Status: proposed on 2026-11-12 and revised the same day to a referee's review, cited below as V with its finding; that review is not in this copy. Built: the typesetter's theme (4.3). What is the owner's to settle is listed in section 10, each with the cautious default used until he rules. The owner's request (2026-11-11): "a translator subagent prompted with patterns of classical rhetoric, plain language, risk communication, active voice etc. to translate the default academic output of the main author into something better for policy stakeholders", with "a political audience dial ... while still being scrupulously honest in the facts and data. But it can and should change tone, emphasis on presentation, what parts get the most focus in callout boxes, etc. That feeds into the graphic layout, with advice on art and symbols and color patterns to match the audience." The evidence is `research/audience_layer.md` (cited below as R with its item).

## 1 What the layer is

1.1 The plain edition is the summary and the policy paper as the case's author writes them, for the case's reader in neutral words: `documents/executive_summary.md` and `documents/policy_paper.md`, filled from their templates. The author does not attempt the audience's voice, and does state the facts this reader will look for (section 9).

1.2 An audience edition is the same two documents re-voiced for one audience by the `audience-translator` seat: `documents/audience/<key>/executive_summary_template.md` and `policy_paper_template.md`, the filled `.md` of each, and `crosswalk.md`.

1.3 A profile is one data file, `audiences/<key>.toml`, that describes the audience. A new audience is one more profile, written when a case's requirements name a reader no profile describes, and before the author's documents read it (`notes/briefs/author_documents.md`, message A, 2), by a `facts-researcher` briefed by `notes/briefs/facts_record.md` with its 2.9 asked of the reader's office: it writes the profile in the form of section 3, each entry resting on the office's own dated documents, stored in `research/sources/<key>/` and keyed in `research/refs.toml`, or marked as judgment (3.3). No code, agent definition or brief names an audience. A profile describes an office and serves many cases: what one case asks an edition to attend to is in that case's `requirements.md`, which the translator reads and which wins over the profile.

1.4 The record is the plain edition and the technical appendix. An audience edition is checked against the plain edition, which milestone 2 has already checked against the appendix. The appendix is never re-voiced.

1.5 The one rule. An audience edition asserts nothing the plain edition does not assert, and leaves out nothing the plain edition says. It changes what the reader meets first and in what words. The rule is necessary and not enough: emphasis alone can mislead with every sentence true (V 1), so the reader's skim path is checked too (2.4, J5).

## 2 What is fixed and what the dial may change

2.1 Fixed in every edition.

2.1.1 Numbers. The translator re-voices the templates, so every number stays a placeholder that the case's script fills from the same facts file. In each document the placeholders are the plain template's: none new, and none used fewer times. No number is typed that the plain template does not type, in digits or in words.

2.1.2 Content. Every claim, cost, harm, caveat and limit of the plain edition is present in the same document. Nothing is dropped. What the plain edition puts in a `key-findings` or `callout` box stays in a box of that kind, and the key findings stay first, with the headline, its range and its cost.

2.1.3 Certainty. A hedge stays a hedge, an interval keeps both ends and what it covers, a judgement stays labelled a judgement, an association stays an association.

2.1.4 Equivalent frames. Each quantity keeps the frame the plain edition gives it: gain or loss, total or per unit, absolute or relative, its denominator, its horizon and its discount rate. Three reasons. A logically equivalent rewording moved 72 per cent to 22 per cent in the original experiment and still moves stated choices across many replications (R 4.2). The remedy the literature gives is to show both frames to every reader (R 2.1.3, 4.2.1), which is a rule for the plain edition's author, not a setting per audience. And a dial that picks the frame by audience is the "nontransparent framing" the literature names as the fault (R 2.4). No comparison or rescaling is added either. What this reader needs is asked of the author before the documents are written (section 9); a want found later is noted in the crosswalk for the author.

2.1.5 Figures and tables: the same data in each figure, drawn in the house chart style or, for a figure drawn with `audience=KEY`, in that profile's `[design.charts]` style (3.4.4); each table character for character.

2.1.6 The citations and the reference list, the dateline, the credit line, and the ranking of the options with what would change it.

2.2 What the dial may change.

2.2.1 Words: vocabulary, tone and sentence shape. A preferred term names the same thing, asserts nothing new, and has its ground stated in the profile: a dated document of the reader's own institution, a count from the sample, or judgement marked as such. Quotations, titles of sources and statutory names keep their own words.

2.2.2 Order of sections; in the summary, of paragraphs too. In the policy paper the paragraphs of a section keep their order, so that a dropped paragraph can be found by counting (V 4).

2.2.3 Emphasis: the title, headings and captions (no new claim in any); bold lead-ins; boxes added round material the case's requirements or the profile say this reader looks for, within the layout's limits; which already-cited source a sentence names first. An added box is `key-findings` when it holds a finding and `callout` only when it holds a cost, a caveat or a limit: the callout is the warning box, and a benefit set in it is overstated while the real caveats grow less distinct (V 5).

2.2.4 Connecting sentences, which tie a finding the plain edition states to a concern the profile lists, in the reader's words: "For the taxpayer, the question is what each dollar buys." Such a sentence carries no number, states no fact about the world, the reader or the reader's institution, and cites nothing. At most three in the summary and one per section of the paper, each listed in the crosswalk with the plain lines it leans on. This is emphasis framing (R 4.1.2).

2.2.5 The look: the design tokens of 3.4 and the cover's icon, which shows the subject and never a verdict.

2.3 The mechanical checks, each a one-line command in the review brief. A script for them waits until one run has shown the form holds (CORE 6.3).

M1. Each `{{...}}` placeholder of the plain template is used at least as often in the audience template, and no other is used; one used more often, as a headline repeated in an added box, is listed in the crosswalk. A plain set comparison is not enough, since it cannot see a number dropped from a sentence where the same placeholder also stands in a table.

M2. Every run of digits typed outside a placeholder in the audience template is in the plain template, or is listed in the crosswalk (the edition's own date). Number words ("half", "most", "double") in the audience template and not in the plain one are listed for the referee.

M3. The table lines of the two templates are identical; the image file names are the same.

M4. The audience summary's template opens with `key-findings`, as the plain summary's does, and each audience template has at least as many boxes of each kind as the plain one. The count of `callout` boxes rises only by boxes the crosswalk lists as a cost, a caveat or a limit.

M5. Counted from the plain side. In the paper, each section of the audience template has the plain section's blocks (paragraphs, lists, boxes, tables, figures), every one and in the plain order, plus the added boxes the crosswalk lists. In the summary, every block of the plain template has a row in the crosswalk. The referee reads the two side by side; sampling the translator's own crosswalk cannot find a paragraph that has no row.

M6. Each word of the profile's `instead_of` lists found in the audience template is listed with its line, for the referee to judge against the term's rule. Words within 15 per cent of the plain document's count; the summary on one page at 9.5 pt or more.

2.4 The judged checks, the referee's, row by row of the crosswalk: the same meaning and the same strength (J1); each connecting sentence asserts nothing (J2); each frame unchanged (J3); each term swap names the same thing (J4); the skim path (J5, below); no title, heading or caption claims more than its section, and the cover's icon shows the subject, not a verdict (J6); the edition sentence of 5.3 is true (J7).

J5, in the referee's words (V 1.4): "Read only what the profile's `reader.reads` names, in the order printed (for the summary: the title, the key findings and the boxes). From that alone a reader gets the same five answers as from the plain edition (the net benefit, its range, the cost, the main caveat, the option ranked first) and its largest cost. Any effect the edition leads with or boxes that is not the largest contributor to the result states its share of the total in the same box or paragraph, from the plain edition's placeholder. A headline number repeated in an added box carries its range and its cost each time."

## 3 The audience profile

3.1 One TOML file per audience in `audiences/`, read with Python's `tomllib`: the format the project's other hand-edited data uses. The three written are real files; `us_hhs_appointee_2026.toml` is the fullest example.

3.2 Its parts.

3.2.1 The head: `schema`, `key`, `label` (what the profile is, in full), `disclosure_label` and `edition_line` (how an edition names its reader, and the one sentence at its foot that says what it is, 5.3), `as_of`, `review_by`, `status` and `assumes` (what was assumed about the present, and what was not checked).

3.2.2 `[reader]`: who they are, what they decide, what they read.

3.2.3 `[[priority]]`, one per concern: its `name`, what findings to `connect` to it, and the reader's own document that states it, by `source` key, `date` and `quote`.

3.2.4 `[[term]]`, one per word choice: `prefer`, `instead_of`, a `rule` for its limits, and its evidence. An entry with `apply = false` is recorded and not used; its `awaiting` says whose ruling it waits for.

3.2.5 `[voice]`: `tone`, what to `lead` with in order, `emphasis_boxes`, `sources_named_first`, and `never`; its `basis` is judgement in all three profiles.

3.2.6 `[design]`: the tokens of 3.4: colours, the heading face, the cover icon, imagery in words and the chart style.

3.3 Every entry says what it rests on, in `basis`: `source` (the reader's own dated public document, quoted and machine-checked against the stored text), `study`, `sample` (the 22 reports looked at, R 5.5), `convention` or `judgement`. A stereotype is `judgement` and says so. Of the first profile's 24 entries marked with a basis, 14 rest on a source, 4 on the sample, 1 on a study and 5 on judgement in whole or part. A profile describes an office or a kind of reader, never a named person, and holds no clause its reader would resent on seeing the file.

3.4 Design tokens. The W3C Design Tokens format (R 5.7) gives the shape: a token is a value with a type and a description, and a theme is a set of overrides resolved over a base. Here the base stays where it is, in `tools/typeset_layout/typeset-boxes.sty` and `typeset-common.sty`, and a profile lists only what it overrides. Each token is a TOML table with `value`, `type`, `basis` and `evidence`. Plain keys are used, not the format's `$value`, because TOML reads `$` keys only in quotes; the conversion to the JSON form is mechanical if a second renderer ever needs it.

3.4.1 Colours, by role, with the LaTeX name each sets: `accent` (`typesetblue`: the cover band, the key-findings rule), `accent_caveat` (`typesetwarnline`: the callout rule), `caveat_ground` (`typesetwarn`), `panel` (`typesetpanel`), `neutral` (`typesetgray`), `rule` (`typesetrule`), `ink` and `ink_second`.

3.4.2 `font.heading`: `lato` (the base), `pagella`, `termes` or `schola`, the TeX Gyre families installed with TeX Live. The body type does not change.

3.4.3 `[design.icons] cover`: one Tabler name or a word, for which the typesetter takes the first name `tools/icon_search.py` lists. The typesetter draws it on the policy paper's cover as a title's `{icon=NAME}` is drawn, unless the title names an icon itself; absent, there is none. A word no icon matches stops the build.

3.4.4 `[design.imagery]`: `cover` and `photograph`, guidance in words; no tool reads it yet. `[design.charts]`: a matplotlib rc overlay on `tools/house.mplstyle`, each key but `basis` and `evidence` a quoted rc name (`"axes.prop_cycle" = "cycler('color', ['14315C', '898989'])"`), its value in style-file syntax or a TOML number or boolean; `tools/figures.py` lays it over the house style for a figure drawn with `audience=KEY`, and both it and the typesetter refuse a key that is not an rc name. Each of the three tables may carry `basis` and `evidence` (3.3); any other key is refused.

3.5 The first three profiles.

3.5.1 `us_hhs_appointee_2026`: a Republican political appointee at the Department of Health and Human Services. Ten priorities, each quoted from the administration's own documents of January 2025 to April 2026; navy accent, deep red caveat rule, cream panels, serif headings. Revised to V 3.

3.5.2 `us_democratic_health_staff_2026`: Democratic health-committee staff, or a Democratic administration's official. Six priorities from congressional Democrats' statements of 2025 and the White House documents of 2021. It overrides no token: the sample shows no left-leaning look the base theme lacks (R 5.6). Not for a delivered edition until the result of the election of 3 November 2026 is looked up (V 3.12).

3.5.3 `us_budget_examiner`: a career analyst at the Office of Management and Budget or the Congressional Budget Office. Six priorities from the standing rules of those two offices and of the Government Accountability Office; one muted blue, no icon. No case uses it yet.

## 4 Seats and order

4.1 The order, after milestone 2 is accepted and `pdf-layout` has finished with the plain edition, so that no fix is made twice:

4.1.1 `audience-translator` writes the audience templates and the crosswalk, runs the case's documents script and M1 to M6, builds the PDFs, looks at each page and commits its files. Its definition is `.claude/agents/audience-translator.md`.

4.1.2 One review round: a fresh `documents-referee` on faithfulness, the skim path and fit to the profile; a fresh `editor` rules; the translator, resumed, makes the fixes; the editor checks them. The brief is `notes/briefs/audience_review.md`. No new reviewing seat: the documents referee's charge is already faithfulness and plain language. The editor stays for the first two editions, since an error here puts a slanted document under the user's name; after that the round may run without it (V 10.2).

4.1.3 `pdf-layout` on the audience PDFs, by its own checklist. It edits nothing: its findings go to a `build` of the generator or, for a box mark or a fault of content, to the translator or the author; after the documents are built again, M1 to M4 are run again.

4.2 The fill. The case's documents script fills every `*_template.md` under `documents/`, at any depth, and writes each filled file beside its template. One sentence in `notes/briefs/author_upgrade.md`, message A, 2.3.2 says so.

4.3 The typesetter.

4.3.1 `tools/typeset_layout/typeset-boxes.sty`: one line before `\endinput`, `\InputIfFileExists{typeset-theme.tex}{}{}`.

4.3.2 `tools/typeset.py`: the document list adds `documents/audience/*/*.md`, less templates and `crosswalk.md`. A function `theme_tex(md, language)` returns nothing unless the document's grandparent folder is `audience`; then it reads `audiences/<folder name>.toml` and returns one `\definecolor` line per colour token and two font lines for a heading font. `build()` writes that text to `typeset-theme.tex` in its work folder. The folder's name carries the audience, so no flag is added.

4.3.3 It refuses a missing profile, an unknown token, and a contrast under 4.5 to 1 (R 5.7) between the accent and white or between a ground and the ink. Computed for the two profiles with colours: 12.9 and 8.7 for the accents on white. The base blue itself computes to 4.42 on white, a finding for the layout seat, not for this layer.

4.3.4 A case's plain summary and policy paper, built with the typesetter before and again after the change, are the same on every page, pixel for pixel at 60 dots an inch.

4.4 If time runs out, the case delivers the reviewed plain edition and says the audience edition is pending. An audience edition that has had no review is not delivered.

## 5 Limits, ethics and disclosure

5.1 What the evidence supports. Strong: the bottom line first, plain active sentences, every number with its range, one denominator, both frames (R 6.1); these belong in every edition. Weak: that matching a reader's values moves them (R 4.3.1 finds it entrenches more reliably than it persuades), and every claim about colour, typeface and imagery by political leaning (R 5.6: one looker, 22 documents). The layer may do nothing for the reader; the FDA's guide warns that tailoring made without a research base "is more likely to weaken the communication than improve it" (R 2.2). So the dial is kept light. The referee names further studies, of spin in abstracts and of framing and tailored briefs tested on officials (V 1.2, 6.5, 8.2); none is stored yet, so none is cited here.

5.2 Where tailoring ends. Tailoring changes what the reader notices first and the words it comes in. Misleading changes what the reader would believe about a fact or about the choice, or about what drives the result. Two tests. A reader who reads only what this reader reads gives the same five answers as a reader of the plain edition: the net benefit, its range, the cost, the main caveat, the option ranked first (J5). And the publicity test, an old one in ethics (the referee recalls Kant, Rawls, Bok, and Thaler and Sunstein; V 7.6, not stored): no reader would feel deceived on seeing the other editions, or the profile, side by side with theirs.

5.3 An edition says what it is, in one sentence at its foot, beside the credit line: the profile's `edition_line`, word for word (the translator's definition, "What you change", 6). Under its title it carries the plain edition's dateline and nothing more, and no line of it states the review either edition has had (the owner, 2026-11-13, of an audience summary: "why would you add more than the earlier plain version?"; "kill the line about no human"). For the first profile, the first sentence of the referee's draft (V 7.4): "This edition is written for officials of the present administration at the US Department of Health and Human Services." It names the office and not the party. The plain edition travels with every audience edition. Both are the cautious default until the owner rules (10.1).

5.4 Never, in any edition: a seal, flag, logo or another publisher's dress; a statement that the reader's institution supports, requires or endorses anything; a movement's or a campaign's slogan in the document's own voice; praise or blame of a person or a party; an invented quotation; a profile of a named person.

5.5 A profile dates. Each carries `as_of` and `review_by`, three months on for a political audience; the translator returns blocked on a profile past its date. The first profile's assumptions about the present administration rest partly on search summaries, and the department's own budget and strategy pages refused the fetch (R 7.2).

5.6 What this layer does not do: choose the frame of a number, add a comparison, change a figure, compute a quantity, or write for a reader the case's requirements do not name. A new derived quantity that a reader needs, such as net benefit per dollar of government outlay, is the author's to compute and the case's review to check (V 9.2).

## 6 How a first run is judged

A proposal awaiting the owner: how a test is scored is his to see before it is built. Nothing in 6.2 is run until he rules.

6.1 Every edition, with no ruling needed: M1 to M6 pass, and the referee and the editor find no stated falsehood and pass J5.

6.2 The proposal, from the FDA guide's test for a communication with no budget (V 8.4): the owner and one person who has worked in such an office each get the plain and the audience summary marked A and B, not told which is which. Each says of each how understandable it is, whether the amount of information is right, how balanced it is, whether they would recommend it and how to improve it, and which they would send up. It costs no tokens. It gives a preference from two readers, not an effect, and is reported as that.

6.3 Deleted on the referee's finding (V 8.3): the test that rendered one summary for all three profiles and had a fresh reader match editions to profiles. It would pass on one phrase and show only that words changed, at about $15 for editions no case asked for. Its useful part, the five answers, is J5.

## 7 The build, in order

7.1 The typesetter (4.3): done.

7.2 The seat's definition is `.claude/agents/audience-translator.md`, installed on 2026-11-12 under the owner's request of 2026-11-11 (the owner's message of 2026-11-11: "I want a translator subagent prompted with patterns of classical rhetoric, plain language, risk communication, active voice etc.") for a translator subagent.

7.3 The review's brief is `notes/briefs/audience_review.md`; `notes/briefs/author_upgrade.md`, message A, 2.3.2 carries the sentence of 4.2 and `notes/briefs/author_documents.md`, message A, 2 those of 9.3, and the seat's place in a case's order is `notes/fast_estimate.md` 1.3.10.

7.4 `audiences/` and its three profiles exist. `research/refs.toml` has the entries.

7.5 Cost of one audience edition at list prices, by arithmetic from the sizes of the documents and not measured: the translator about $4 to $6, the referee $1 to $2, the editor $2 to $4, `pdf-layout` $1 to $2; $8 to $14 in all, and about an hour.

## 8 Simpler choices rejected

8.1 The author writes for the audience directly. Rejected: there is then no neutral text to check the audience's against, a second audience means a second authoring, and the record itself would carry the dial.

8.2 Re-voicing the filled documents, as the verse does. Rejected: typed numbers go stale when a result changes, and "the same numbers" becomes a reading task where it can be a count.

8.3 A reader seat that plays the audience. Rejected: a model's guess at how an appointee reacts is a stereotype judging a stereotype. Fit to the profile is checked against the profile's own lists.

8.4 A separate theme file per audience beside the profile, or the token format's JSON. Rejected: two files to keep in step, for one renderer.

8.5 Leaving the look alone and changing only words. Not rejected on evidence: the sample supports little (5.1). It is kept because it costs one line of LaTeX and a short function, and a profile that overrides nothing, as the second does, is the null case.

## 9 What the plain edition must carry

9.1 The facts an audience's lead and boxes will need are in the plain edition, or they appear nowhere. The translator runs after the plain edition is accepted and may add no number, comparison or claim, so a want it finds then is too late for that edition (V 2).

9.2 The reader's decision sets the content of every edition: "A communication is adequate if it contains any information that might affect a significant fraction of users’ choices." (R 2.2). So what the reader will look for is settled before the documents are written, and stated in neutral words for every reader.

9.3 The route. The author's documents brief asks the author, where the case's requirements name the reader, to state what the requirements name as that reader's concerns, each quantity under its true name, and, where the coordinator names an audience profile, to read its `voice.lead` and `voice.emphasis_boxes` as a list of what the plain edition must state. The author takes the list from them and nothing of their voice.

9.4 Two things the plain edition states whenever an audience edition will follow, because J5 needs them: each group of effects' share of the total, and each cost under its true name. A cost to society and a government outlay are different numbers: a payment from one party to another is in part a transfer, and "Transfer payments are monetary payments from one group to another that do not affect total resources available to society." (`omb_2003_circulara4`, quoted and machine-checked in `audiences/us_budget_examiner.toml`). An edition that calls the first by the second's name changes a claim with no digit changed.

## 10 Points put to the owner

10.1 The edition sentence: its wording, and whether it names the office, the administration or the party (V 7, V 4.1). Decided 2026-11-14 by the seat, his to reverse: the first sentence of the referee's draft, which names the office and not the party (5.3).

10.2 Whether the plain edition travels with every audience edition. Decided 2026-11-14 by the seat, his to reverse: it does, so any reader can set the two side by side.

10.3 Whether his analysis writes "Department of War" (V 4.3). Decided 2026-11-14 by the seat, his to reverse: the term stays in the profile marked `apply = false`, and an edition uses the name the plain edition uses.

10.4 Whether an edition may carry a marked note quoting the reader's institution's own documents (V 6.3). Decided 2026-11-14 by the seat, his to reverse: none is added, and 2.2.4 stands as written, since an edition asserts nothing the plain edition does not.

10.5 How a first run is judged (6.2; V 4.2): his to see before it is used (roadmap R21).

10.6 Whether an edition may add examples. Under this design an edition chooses among the examples the plain edition holds and adds none (V 4.5). Decided 2026-11-14 by the seat, his to reverse: as designed.

10.7 His own read of the first profile: what it has wrong and what concern it lacks (V 3.10, V 4.6): his alone (roadmap R21).
