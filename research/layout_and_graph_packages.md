<!-- The report of the research agent of an earlier session, 2026-11-13 (roadmap item 2.61), stored word for word from its return. Its prototype (scripts, PDFs, page images, stored pages of each source) was in that session's scratchpad folder `layout_proto/`; the sources it lists in section 8 are stored under `research/sources/` when the first build of its section 4 lands. -->

# Report layout by established open-source packages: survey, prototype, plan

## 1. Summary

1. **Today.** `tools/typeset.py` (467 lines) runs LuaLaTeX (TeX Live 2023) through the `markdown` LaTeX package, over 732 lines of hand-written TeX in `tools/typeset_layout/`. The TeX covers page geometry, boxes, a table renderer, Unicode mapping and CJK. The case's `figures.py` (183 lines) styles each chart by hand.
2. **Recommended.** Quarto 1.11.9 (Posit, MIT) rendering to Typst 0.15.1; Quarto bundles Typst and pandoc. Charts by matplotlib with one built-in style sheet and constrained layout. Use plotnine once its install is allowed.
3. **What Typst does by default** that the TeX files do by hand:
   - table columns size to their content;
   - headings stay with their text;
   - widows and orphans are prevented;
   - tables and figures float to page tops and feet, numbered and captioned.

   Quarto adds boxes (callouts), cross-references and per-audience themes (`_brand.yml`).
4. **The prototype.** Its own configuration is 6 lines of Typst and a 4-line Lua filter.
   - The summary fits one page.
   - The two-column summary takes 2 more lines of Typst.
   - The paper through section 3 fills 6 pages, with Tables 1 and 2 and Figures 1 to 3.
   - Each document builds in 2 to 3 s.
5. **Cost to adopt.** A 138 MB download (420 MB unpacked), pinned, and about ten small builds (section 4).
6. **Risks.**
   - Wide appendix tables: Typst shares overflowing width equally, which squeezes the label column. A 40-line width filter brings the appendix back to today's 114 pages, but one word still spills into the next column.
   - Columns do not balance.
   - Boxes never break across pages.
   - Icons and CJK are untested.
7. **Sensitivity numbers.** No maintained Python package computes EVPPI; R's `voi` does. The project's `value_of_information.py` already implements the established method. On a toy, the same fit gave variance shares, EVPPI and tornado ends that match brute force, including for an input hidden inside model code.
8. **PDFs:**
   - tmp/scratchpad/layout_proto/quarto_typst/summary.pdf
   - tmp/scratchpad/layout_proto/quarto_typst_twocol/summary.pdf
   - tmp/scratchpad/layout_proto/quarto_typst/paper.pdf
   - tmp/scratchpad/layout_proto/quarto_typst_appendix_tabulary/appendix.pdf
   - runner-up: tmp/scratchpad/layout_proto/quarto_latex/paper.pdf
9. **Page images**, present and prototype: tmp/scratchpad/layout_proto/images/
   - Best to look at: `typst_summary_twocol.png`, `typst_paper_p1-6.png`, `present_summary.png`, `present_paper_p1-6.png`, `latex_paper_p1-6.png`.
   - Appendix: `typst_appendix_autowidth_p78_zoom.png` and `typst_appendix_tabulary_p66_zoom.png`.

## 2. Survey

Release data comes from the GitHub, PyPI, CTAN and CRAN APIs, read 2026-11-13; the JSON is in `sources/meta/`. Pages are stored in `sources/store/<key>/` (original, text.txt, source.json from the shared `shared/tools/source_store.py`), with their addresses in `scripts/sources.tsv`.

### 2.1 Typesetting systems

**1. Typst, used through Quarto here.**
- Maintainer and licence: Typst GmbH and community; Apache-2.0.
- Latest release: 0.15.1, 2026-07-17.
- Defaults:
  - Auto tracks fit their content and share the space fairly when they overflow.
  - Headings are sticky: "set on heading blocks to prevent orphaned headings".
  - "Text layout prevents widows and orphans by default".
  - `figure(placement: auto)` floats a figure.
  - `table.header` repeats on each page.
  - Justified text gets optimized line breaks.
  - Hyphenation happens only when text is justified.
  - Columns "will currently not balance".
- Reproducibility: one static binary (56 MB); `@preview` packages are cached by exact version.
- Speed: 3.3 s to compile the 132-page appendix.
- Migration used alone: an own template plus pandoc filters, about 40 lines.
- Sources: typst_docs_grid, block, text, figure, table, columns, par; typst_changelog_0_12.

**2. Quarto, format typst (recommended).**
- Maintainer and licence: Posit; MIT.
- Latest release: 1.11.9, 2026-10-30.
- What it adds to Typst:
  - numbered captions;
  - cross-references `{#tbl-}` and `{#fig-}`;
  - titled callouts, which never split;
  - `_brand.yml` themes;
  - Marginalia margin layouts.
- One flaw: pipe-table widths come from the dash counts, which gives equal widths. A 4-line filter restores auto widths.
- Reproducibility: bundles pandoc 3.10, Typst 0.15.1 and the Typst packages its templates import (fontawesome, marginalia), so a render needs no network.
- Speed: appendix 19.7 to 22.6 s; paper 2.6 to 3.0 s.
- Sources: quarto_typst, quarto_typst_custom, quarto_callouts, quarto_figures, quarto_tables, quarto_brand.

**3. Quarto, format pdf on LaTeX with KOMA (runner-up look).**
- Defaults with no table settings:
  - equal-width columns;
  - the summary's box table overflows its box;
  - longtable leaves one row of Table 1 alone on the next page;
  - the summary runs to 2 pages;
  - the worked example splits across pages.
- TeX Live 2023 here lacks fontawesome5, and the current CTAN copy fails on it, so a stub was used.
- Speed: 12.7 s for the 6-page paper.
- Sources: quarto_pdf_engine, quarto_pdf_basics.

**4. pandoc 3.14 (2026-11-12, GPL-2.0) with a LaTeX class and packages.** This is close to today's chain. Versions:
- tcolorbox 6.10.0 (2026-05-28)
- tabularray 2025C (2025-11-27)
- microtype 3.2d (2026-03-01)
- longtable 4.28 (2026-10-05)
- needspace 1.3f (2026-10-13)
- widows-and-orphans 1.0f (2023-04-02)
- tabulary 0.11 (2024-06-04)
- caption (2023-09-08)
- KOMA 3.49.3 (2026-10-19)
- memoir 3.8.4b (2025-11-04)

Each package fixes one fault once configured. None chooses column widths, which is why today's 322-line `typeset-common.sty` measures each table. widows-and-orphans only "Identif[ies]" widows and orphans. needspace inserts a "pagebreak if not enough space". Today's typesetter takes 18.6 s for 114 pages.

**5. Eisvogel 3.5.1 (2026-07-04, BSD-3), a pandoc LaTeX report template.** Not tested. It gives a report look but leaves the table-width problem.

**6. WeasyPrint 70.0 (2026-09-08, BSD-3).** Not tested.
- "The orphans and widows properties are supported."
- Column balancing "should be efficient with simple cases".
- It has no page floats, which rules it out for this paper.

**7. Paged.js 0.4.3 (2023-07-06, MIT).** Stale: no release in three years.

**8. Vivliostyle.js 2.46.0 (2026-11-03).** AGPL-3.0, and needs a browser.

### 2.2 Templates

1. Typst Universe lists 1,757 packages, and none is a think-tank or policy-brief template. The nearest are biz-report 0.3.1 ("business report with table styling ... infoboxes"), marginalia 0.3.1, tufte-memo 0.1.2 and booktabs 0.0.4.
2. I tried Quarto's margin layout with defaults only, and rejected it (`images/typst_paper_margincolumn_tried.png`):
   - 7 pages, with page 1 84% empty;
   - Table 1 squeezed;
   - the margin holds only captions.

   A CBO-style margin column of key numbers would be a house template to design.

### 2.3 What published briefs and reports share

The pages read:
- CBO Outlook 2025, pages 1 to 8, and CBO Transparency 2026, pages 1 to 4. Both were fetched from the Internet Archive, because cbo.gov returns 403.
- Pages the project measured earlier (`research/report_layout.md`): RFF issue brief 21-10 and its working paper, Hamilton/Brookings, IFS BN259, the Urban fact sheet, and the Resolution Foundation.
- RAND could not be read: 403, and the archive index was offline.

What they share:
1. The title is the largest type, set under a rule or band, and the verdict comes within five lines.
2. Briefs use 0.5 to 0.83 in sides with two columns or a side column, at 9.5 to 11 pt. RFF's long paper uses one column of 82 to 86 characters with 1.75 in sides.
3. What the reader must not miss is in a box or side column. IFS uses a key-findings box. CBO uses a right-hand column of key numbers in large type.
4. Figures are titled with the finding, labeled directly, and give the unit above the axis. Tables use few rules and right-aligned numbers.
5. CBO and the long RFF paper carry a running header or footer with the date, short title and page.

Sheet of these pages: `images/exemplars_cbo_rff_brookings_ifs_urban.png`.

## 3. Faults

Faults were found by reading the rendered pages and with `tools/typeset.py --measure`.

### 3.1 Measurements

| Document | Pages | Side margins | Full line | Empty squares |
|---|---|---|---|---|
| Present summary | 1 | 0.50/0.50 in | 50 chars | 35% |
| Typst summary, one column | 1 | 0.70/0.68 in | 125 chars | 41% |
| Typst summary, two columns | 1 | 0.60/0.57 in | 61 chars | 45% |
| LaTeX summary | 2 | 1.15/0.82 in | 90 chars | 67% |
| Present paper, pages 1 to 6 | 6 | 1.25/1.25 in | 89 chars | 55% |
| Typst paper, through section 3 | 6 | 1.25/1.23 in | 95 chars | 65% |
| LaTeX paper, through section 3 | 6 | 1.15/1.14 in | 90 chars | 68% |
| Present appendix | 114 | 1.25/1.25 in | 77 chars | 55% |
| Typst appendix, auto columns | 132 | | 91 chars | 64% |
| Typst appendix, tabulary rule | 114 | | 92 chars | 56% |

The Typst paper's pages 5 and 6 end short because the excerpt stops at section 3.

### 3.2 Fault list

Each fault is followed by what the Typst prototype does with it, then the LaTeX prototype.

**Summary**

- **S1.** The key-findings table is squeezed into one 3.6 in column, so labels wrap to two or three lines.
  - Typst: fixed. The box spans the page and every label sits on one line.
  - LaTeX: worse; the table overflows its box.
- **S2.** Numbers are left-aligned and there is no table caption.
  - Typst: numbers right-aligned through the `---:` markup, but not decimal-aligned.
- **S3.** A wall of 8 pt grey dateline lines, five of them in the HHS edition.
  - Typst: set at body size, two lines. The remaining length is content.
- **S4.** The columns are unbalanced.
  - Typst two-column: still unbalanced, because Typst does not balance columns yet ("planned for the future").
- **S5.** The tall shaded box fills the left column.
  - Typst: fixed with a parent-scoped float that spans both columns.
- **S6.** Justified narrow columns show loose spacing and hyphenation.
  - Typst two columns: 61-character lines, with optimized line breaks.
  - Typst one column: 125-character lines, over the checklist's 90.
- **S7.** Bold run-in lead-ins and run-in box titles.
  - Typst: box titles move into the callout's title bar. The lead-ins are content.
- **S8.** In the HHS edition a paragraph breaks at the column foot.
  - Typst prevents orphans by default; the HHS edition was not rendered.
- **S9.** The HHS edition mixes faces.
  - Typst: one family throughout. `_brand.yml` would set it per audience (not tried).
- **S10.** The summary has no figure.
  - Content. The two-column version has about 3 in free.

**Paper**

- **P1.** The cover is about 70% white, and the dateline is pushed to page 2.
  - Typst: fixed. No cover page; title, byline, dateline, credit and key findings are all on page 1.
- **P2.** Page 2 opens with process text, then the credit, then stacked boxes.
  - Typst: page 1 holds them in reading order.
- **P3.** The key-findings table is narrower than its box, with left-aligned numbers.
  - Typst: numbers right-aligned.
- **P4.** Headings are small (about 13 pt against an 11 pt body) and the icons are inconsistent.
  - Typst: title at 1.7 em. Icons are dropped, because Quarto ignores `{icon=...}`.
- **P5.** The page-3 table has no caption and its labels wrap.
  - Typst: "Table 1" with a caption, and the label column sized to content.
  - LaTeX: equal widths, so labels wrap.
- **P6.** About 1.2 in empty at the foot of page 3 and 1 in on page 4.
  - Typst: page 3 is full; about 0.8 in is left above Figure 1 on page 4.
  - LaTeX: one row of Table 1 is left alone on a page.
- **P7.** Tables and figures have no numbers.
  - Typst: numbered and cross-referenceable. Captions are centered "Figure 1:", which is a house setting.
- **P8.** The figure's grey ground and Lato labels clash with the Pagella body.
  - Typst: the new figures have a white ground. Their sans labels still differ from the body; one line in a style file would match them.
- **P9.** The worked-example box splits at the page foot.
  - Typst: fixed, because callouts never split.
  - LaTeX: it splits.
- **P10.** The page-6 label column wraps.
  - Typst: fixed, except "Best of the three, share of draws", which wraps once.
- **P11.** About 89 characters per line.
  - Typst: 95 characters, which is over 90. The fix is one line: wider sides or 11.5 pt type.
- **P12.** No running header with the title.
  - Typst: one line in the page header would add it.
- **P13.** "-0.83" is set with a hyphen.
  - A content fault; pandoc does not change it.

**Appendix**

- **A1.** Wide tables.
  - With auto columns, the equal shares squeeze the label column to about an inch, and the appendix grows to 132 pages.
  - `tabulary.lua` brings it to 114 pages and 56% empty, but a long word still spills into the next narrow column ("Judgement" into "Low, high").

## 4. Migration plan

Each step is one `build` run that can be checked on its own.

1. **Pin the tool.** A setup script fetches `quarto-1.11.9-linux-amd64.tar.gz` into a git-ignored folder and checks its SHA-256.
   - Check: a three-line `.qmd` with a table renders to one page, and `pdftotext` extracts its text.
2. **Add a house format folder.** It holds `_quarto.yml` with the 6 Typst lines (the notice passed in as a variable) and `autowidth.lua`.
   - Check: the `.typ` has `columns: N` and no percentages.
3. **Map the project's box names to callouts with a Lua filter** (about 15 lines; `scripts/prepare.py` `boxes()` is the same mapping in Python):
   - key-findings becomes a tip callout;
   - callout becomes a warning;
   - worked-example becomes a note;
   - credit becomes small grey type.

   Existing documents keep working.
   - Check: three titled callouts appear, and a words-in, words-out comparison passes.
4. **Route the paper and appendix through Quarto in `typeset.py`, behind a flag.** Keep `measure()`. Move the `align_numbers()` rule into the filter.
   - Check: the `notes/pdf_layout_review.md` checklist passes, and `--measure` is no worse than today.
5. **Wide tables.** Use `tabulary.lua` plus a per-column minimum width set by the longest word, as tabulary's `\tymin` does (about 10 more lines).
   - Check: 114 pages or fewer, and `pdftotext -bbox` finds no word box crossing a cell edge.
6. **Two-column summary.** A filter wraps the title and box in `#place(top, scope: "parent", float: true)` and sets `columns: 2`; `build.sh` step 3a makes these two edits by hand. Keep copyfit as a loop over fontsize 10.5, 10 and 9.5 pt.
   - Check: one page, with full lines of 90 characters or fewer.
7. **Audience themes.** A `_brand.yml` per audience profile replaces `theme_tex()`. Keep the WCAG contrast check as a test.
   - Check: the HHS edition renders in its colors and passes contrast.
8. **Figures.** One house `.mplstyle` file plus constrained layout; strip the per-figure styling from the case's `figures.py`.
   - Check: no overlaps, by eye on the page images.
9. **Icons, verse and CJK.**
   - Tabler icons through a Typst icon package or the font file.
   - The verse layout as a Typst template.
   - CJK with Noto CJK fonts and `lang`.
   - Check: against the existing outputs, page for page.
10. **Delete the LaTeX path.** Remove `tools/typeset_layout/` (732 TeX lines) and, from `typeset.py`, `prepare()`, `split_head()`, `notice_tex()`, `theme_tex()`, `icon_table()` and the LuaLaTeX log parsing. Do this after steps 4 to 9 pass.
    - Check: the full test suite and a rebuild of every case.

The smallest first step is 1 with 2: a pinned Quarto and the house format, run on one fixture, with nothing in a case changed.

## 5. Why this recommendation, and its risks

**Why.** It deletes code instead of adding it. The TeX files exist to do what Typst does by default. The prototype configuration is 13 YAML lines and a 4-line filter. Builds take seconds, so a fix can be tried and seen in one round.

**Runner-up: plain pandoc 3.14 plus Typst 0.15.1.** Two static binaries, 226 MB unpacked. It needs its own template and filters (about 40 lines). The house filters carry over if Quarto's size or release pace becomes a burden.

**Third: Quarto on LaTeX.** Its defaults left the most faults, and it needs the same width and float work done by hand.

**Risks.**
1. **Size and churn.** Quarto is 420 MB unpacked and releases about monthly, and Typst minor versions have changed template behavior. Pin both and upgrade on purpose.
2. **Wide tables (A1).** LaTeX has an established answer here (tabulary, tabularray's X columns); Typst has only its fair-share rule. `tabulary.lua` is hand-written.
3. **Unbalanced columns.**
4. **Callouts never split across pages.** A box taller than a page would need Quarto's callout partial overridden.
5. **Not tried:** icons, verse, CJK and `_brand.yml`.
6. **Text extraction.** Running `typst compile` directly on Quarto's `.typ` once gave a PDF with no extractable text. `quarto render` PDFs extract normally.
7. **Heavy callout title bands.** A CBO-style ruled box would need a house partial.

## 6. Graphs

### 6.1 What `figures.py` writes by hand (183 lines)

1. Lato font registration and color constants.
2. Interval rows drawn piece by piece, with labels in white boxes and annotations.
3. `MaxNLocator` ticks and a hand-written number formatter.
4. Margins set with `subplots_adjust`.
5. A groups chart, one `barh` panel per design, every label placed by hand.
6. A tornado built from AnnotationBbox and VPacker label blocks, row heights from line counts, and a hand-made legend.

### 6.2 Packages

1. **matplotlib** (tested): 3.11.2, 2026-09-11, PSF-based licence.
   - Built-in style sheets set the look in one line.
   - Constrained layout plus `legend(loc="outside ...")` places labels and legends.
   - `ax.ecdf`, `errorbar`, and `barh` with `bar_label`.
   - Already in the venv.
2. **plotnine**: 0.15.9, 2026-11-03, MIT, Hassan Kibirige. The ggplot2 grammar with one theme set once:
   - `geom_pointrange` for intervals;
   - `stat_ecdf` for cumulative curves;
   - `geom_col` for tornado and stacked charts;
   - facets.

   The pip install was refused, so it was not tested.
3. **seaborn**: 0.13.2, 2024-01-25, BSD-3. No release in about two years.
4. **Altair**: 6.3.0, 2026-09-15, BSD-3. Static export goes through vl-convert 1.9.0, which bundles a JavaScript engine.
5. **SciencePlots**: 2.2.2, 2026-06-23, MIT. Style sheets only.
6. **ArviZ**: 1.3.0, 2026-08-11, Apache-2.0. Forest and ECDF plots, through `from_dict`.
7. **SALib**: index bar plots only.
8. **great_tables**: 1.1.0, MIT. Tables, not charts.
9. **Lilaq 0.6.0 (MIT) and cetz-plot 0.1.4 (LGPL-3.0)**: plotting inside Typst, but young.
10. **Quarto figures**: captions and cross-references. Code cells would need a Jupyter kernel, so keep charts as scripts.

Sources: matplotlib_style_sheets, plotnine_home, seaborn_home, altair_saving, scienceplots_readme, arviz_home, salib_home, great_tables_home, lilaq_home, quarto_figures.

### 6.3 Recommendation and prototype

**Recommendation.** matplotlib with a built-in style sheet and constrained layout now, plotnine for new charts once installed, and one house `.mplstyle` file.

**Prototype.** `scripts/figures_proto.py` is 70 lines against 183, with no color constants, no hand-placed labels and no hand-set margins. It draws:
- an interval chart from the committed facts.json;
- a cumulative curve of each design's net benefits from 200,000 draws, made by `tools/estimate_total.py --draws` on a scratch copy of the case (25 s).

**Check of the draws.** Means are 4.80, 6.05 and 7.94 billion against the facts' analytic 4.83, 6.10 and 7.98 billion, a Monte Carlo difference. The 5th and 95th percentiles and the medians match closely.

Both charts are placed in the paper as Figures 1 and 2. Figure 3 is the case's own `paper_groups.png`, kept to show the clash of styles.

**Still written by hand:** reading the data, choosing what to plot, labels and captions. A house style file would make the chart font match the body.

## 7. Sensitivity numbers from the stored draws

The class is given-data global sensitivity analysis and value of information: everything is computed from the stored input draws and output draws, with no rerun.

### 7.1 Packages

1. **SALib 1.6.0** (Python, MIT, 2026-09-19).
   - Given-data methods: `delta`, `rbd_fast`, `pawn`, `hdmr`, `enhanced_hdmr`, `rsa`, `discrepancy`, each marked "Compatible with: all samplers". `sobol` and `shapley` need their own samplers.
   - What it gives: delta's S1 is the binned conditional mean; `rbd_fast` uses Plischke's EASI ordering; plus moment-independent delta and PAWN.
   - Limits: one output per call, no decision, so no EVPPI, and no tornado. Not installed.
2. **R voi 1.0.3** (GPL-3, 2024-09-16, Christopher Jackson).
   - EVPPI by "gam" (mgcv), "gp", "inla", "bart", "earth", "so" (Strong and Oakley 2013) and "sal" (Sadatsafavi 2013), with the decision built in. Also EVSI.
   - The reference implementation, but R is not installed here.
3. **R BCEA 2.4.83** (GPL-3, 2025-11-26, Gianluca Baio) and **R sensitivity 1.31.0** (GPL-2, 2026-02-27, Bertrand Iooss). Both need R.
4. **OpenTURNS 1.27** (LGPL, 2026-06-19). `RankSobolSensitivityAlgorithm` gives first-order indices only, "given some input / output samples". A heavy dependency for one estimator.
5. **SciPy `stats.chatterjeexi`** (in the venv, SciPy 1.18.1). A moment-independent ranking that needs no fit.
6. **statsmodels 0.15.0 GAMs and pygam 0.12.0.** Generic smoothers.
7. **scikit-learn and dowhy.** They answer different questions.
8. **voiage** (Python with a Rust core, Apache-2.0, 3 stars). Too young.

No maintained Python package computes EVPPI; a GitHub search for "evppi" finds 8 repositories, none with more than 3 stars.

### 7.2 What the project already has, and a check

**What exists.** `cost_benefit_engine/value_of_information.py` (92 lines) already implements Strong and Oakley 2013 and Strong, Oakley and Brennan 2014:
- a fit by bins or a cubic spline on the input's ranks;
- EVPPI from the fitted values;
- a permutation noise floor.

The same fit also gives:
- each input's main-effect variance share, var(E[Y given X]) / var(Y), which is what SALib's delta S1 computes;
- the tornado ends, by a local linear fit near the 5th and 95th percentiles. Reading the global spline at the ends was 19% off for a heavy-tailed input, so the toy does not use it.

**The toy.** `scripts/gsa_toy.py` takes 200,000 draws of four inputs, two options plus doing nothing. Input M enters only through a kink, as an input inside a case's model code would. It is compared with brute force: 200 values of each input, the rest redrawn 20,000 times. Output is in `scripts/gsa_toy_output.txt`.

| Input | Variance share | EVPPI | 5th-percentile end | 95th-percentile end | xi |
|---|---|---|---|---|---|
| A | 0.810 / 0.810 | 0.588 / 0.588 | −2.465 / −2.450 | 18.531 / 18.499 | 0.657 |
| P | 0.021 / 0.021 | 1.131 / 1.117 | 5.394 / 5.666 | 1.057 / 1.188 | 0.024 |
| M | 0.000 / 0.000 | 1.131 / 1.116 | 3.690 / 3.664 | 3.698 / 3.662 | 0.001 |
| C | 0.017 / 0.016 | 0.103 / 0.101 | 5.103 / 5.050 | 1.317 / 1.365 | 0.058 |

Each pair is given data / brute force.

**What it shows.**
- Variance shares match to 0.001.
- EVPPI is within 1.4%, biased upward as the method predicts.
- The tornado ends carry Monte Carlo error: P's low end is 0.27 off on a bar 4.5 long, about 6%. The ends must be stated with their error.
- About 0.5 s per input, so 333 inputs take about 3 minutes.
- M is found wherever its draws are the ones the model used. The product closed form would draw M's bar at 0, which is what stopped this morning's build.
- M's variance share is 0 for the option best on average, yet its EVPPI equals P's. So a tornado or variance shares of one option do not show which input matters for the choice. The established remedy is to show them for the difference between the two leading options (incremental net benefit), beside EVPPI.

### 7.3 Recommendation

1. Extend `value_of_information.py`, which is already reviewed, with two functions on the same fit: `main_effect_share` and `ends` (local linear, about 6 lines).
2. Feed it each input's draws, regenerated by the 3-line `factor_values` from the stopped brief (the author's archive, 2.2).
3. Report incremental net benefit beside each option's figures.
4. As an independent check, once installs are allowed, use SALib's delta S1 and PAWN. If R is installed, compare once with voi's "gam" EVPPI.
5. This holds only where a model input's draws are the ones the model used. The tool's docstring says same-named inputs share uniform numbers. A model that draws on its own stream must save those draws.

**What no package does**, so only this is written by hand:
1. Regenerate each input's draws from its name and the seed.
2. Compute tornado ends from given data.
3. Find switching values.
4. Compute EVPPI with the decision built in, in Python.
5. Draw the charts.

## 8. Sources to store in research/sources/ with refs.toml entries

The keys are as in `sources/store/`:
- **Typst:** typst_docs_table, grid, block, figure, text, columns, place, page, heading, par; typst_changelog_0_12.
- **Quarto:** quarto_typst, quarto_typst_custom, quarto_brand, quarto_callouts, quarto_pdf_engine, quarto_figures, quarto_tables, quarto_pdf_basics.
- **Other typesetting:** pandoc_manual, weasyprint_features, pagedjs_home (only 312 characters).
- **Charts:** matplotlib_style_sheets, seaborn_home, plotnine_home, altair_saving, scienceplots_readme, arviz_home, great_tables_home, lilaq_home.
- **Sensitivity:** salib_home, salib_160_delta, salib_160_rbd_fast, salib_160_pawn, salib_160_hdmr, voi_evppi_reference, openturns_rank_sobol, cran_sensitivity.
- **Exemplars:** cbo_2025_budget_outlook (46 pages) and cbo_2026_transparency (23 pages).

Release metadata is in `sources/meta/`. Strong and Oakley 2013 (`strong_oakley_2013_efficient`) is still unstored.

## 9. What could not be done

1. **plotnine and SALib were not installed.** The permission prompt refused the pip install, and I did not retry.
2. **No RAND pages.** rand.org returned 403, and the archive index was offline.
3. **Not tried:** `_brand.yml`, CJK, the Tabler icons (dropped in the prototype) and verse.
4. **The LaTeX branch needed a stub `fontawesome5.sty`.**
5. **The present typesetter was timed on a scratch copy of the appendix**, so that no tracked PDF was written.
6. **R is not installed**, so voi and BCEA were read, not run.
7. **The two-column summary's two edits were made by hand to Quarto's `.typ`.** The filter that would make them is step 6 of the plan, not built.
8. **REPORT.md was refused by the harness**, so this message is the report.
