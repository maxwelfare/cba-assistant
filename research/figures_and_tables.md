# Figures and tables for a high-quality cost-benefit analysis

Research for the owner, 12 November 2026 (an earlier session, a research seat). He asked for "a research agent to look up what kinds of figures and tables should be included in high quality analyses of this type, and give me the list to review. Im sure theres more things we need that I forgot to specifically ask for", and then set the form the list should take: "this should probably be in table form instead of paragraph, with references to standards or best practice instead of explaining it from scratch. In general the papers should lean heavily on figures and graphs and proper scientific tables. They are accurate, efficient, and the mark of high quality, and we can produce them cheaply based on the code. Especially since we should do a lot of specification testing, options analysis, and other proper guides to uncertainty and details." He chose from it the same day, answering its card "yes to a" [the owner's message of 2026-11-12]: the tiers of part 3 as recommended, the process flowchart drawn as a figure (3.4.2), and the tornado in the paper with the value-of-information table in the appendix (3.4.1, option A). The instruction an author follows is the table in `notes/briefs/author_documents.md`, message A, 5.2, which places the independent-methods figure (row 29) in the appendix only, by the owner's later ruling [the owner's message of 2026-11-13]. The "Now" column and each entry's "Now" line describe the briefs and the cases in the tree on 12 November 2026.

How it was made. The guidance read is:

1. the official guides of the United States (Circular A-4 of 2003 and 2023, Circular A-94 of 1992, EPA's guidelines), the United Kingdom (the Green Book, the AQuA book, the Analysis Function's guidance on uncertainty, the statistics regulator's review), Canada (Treasury Board), Australia (Office of Impact Analysis) and the European Union (the Better Regulation toolbox, whose chapter 8 is stored in its 2025 edition under the key `ec_2023_better_regulation_toolbox`);
2. the reporting standards of health economics (CHEERS 2022 and its explanation, the Second Panel) and the reference case for benefit-cost analysis in global health (Robinson et al. 2019);
3. the ISPOR task forces on uncertainty and on value of information, and the sensitivity-analysis literature;
4. the literature on specification testing, on evidence synthesis (PRISMA, Cochrane) and on expert elicitation (IDEA);
5. three style guides (AEA, APA, Urban Institute) and three exemplars (Resources for the Future, Copenhagen Consensus, GiveWell).

Every quote comes from the stored text in `research/sources/<key>/`, or in the folder that key's `research/refs.toml` entry names. "Recalled" marks a claim from memory that has not been checked. The places are the source's own section, item or page numbers. The 2003 Circular A-4 is stored as a single HTML line, so its quote serves as its place. Circular A-4 of 2023 was rescinded in 2025 and the 2003 Circular is in force again; where both ask for an item, both are cited.

Terms used throughout. Expected net benefits (ENB) is the mean of net benefits over the Monte Carlo draws, the case's key result (memory `key-result-is-net-benefits`). A draw is one joint sample of every uncertain input. An input that "matters" is one whose range moves ENB far, by the measures of rows 6 to 9.

## 1. The list as one table

This table is the instruction an author would be handed. It has one row per figure or table, and each row points to the source that defines the item; the item is not described from scratch here.

1. The columns.
   1. When: the research seat's recommendation, argued in part 3. His choice replaces it.
   2. Where: summary (the one-page executive summary), paper (the policy paper), appendix (the technical appendix) or sheet (the audit spreadsheet).
   3. Defined by: a `research/refs.toml` key and the place in that source. "No standard defines it" is written where none does.
   4. Now: "required" (a brief already asks for it, at the file and line given in part 2), "in a case" (a case has it but no brief asks for it), or "new".
2. The rules for any table or chart are in part 4.
3. Part 5 says what the code already computes for each row.

| No. | Name in the field | Question it answers | When | Where | Defined by | Now |
|---:|---|---|---|---|---|---|
| | **What the answer is, and how sure** | | | | | |
| 1 | Summary boxes: headline tiles, key findings, worked example | What is the answer at a glance, and for one person? | Every case | summary, paper | `gaf_2018_communicating_quality` ("presented up front"); `omb_2023_circulara4` 15 (summary "preferably in an executive summary"); worked example: no standard defines it (the owner's rule 3) | required |
| 2 | Results table: ENB, median, 5th and 95th percentiles, share of draws above zero | What is the result per option at each discount rate? | Every case | paper, appendix | `omb_2023_circulara4` 11.a and 15.c; `omb_2003_circulara4`; `husereau_2022_cheers` item 23 | in a case |
| 3 | Interval chart (dot at the mean, line over the 90 per cent range) | How wide is the uncertainty, and does it cross zero? | Every case | summary, paper | `gaf_2018_communicating_quality` ("Illustrate ranges"); `vanderbles_2019_communicating` 4.1, Fig. 4 | required |
| 4 | Distribution of net benefits (density, violin or quantile dot plot) | What shape is the uncertainty: skewed, heavy-tailed, two-humped? | Every case | appendix; paper where the shape is skewed or two-humped | `omb_1992_circulara94` 9.a; `epa_2014_guidelines_economic_analyses` 11.1.4; `vanderbles_2019_communicating` Fig. 4; `ec_2023_better_regulation_toolbox` Tool #65, Box 2 | new |
| 5 | Acceptability curve, in CBA form: share of draws above zero against the bar or the discount rate | How sure is the conclusion across the bars a reader might hold? | Where the bar or the rate is disputed | appendix | `husereau_2022_cheers_ee` item 24; `fenwick_2020_value` (Reporting; Box 4 for choosing by the mean) | new |
| | **What drives it, and where research pays** | | | | | |
| 6 | Tornado diagram | Which inputs move the result furthest? | Every case | paper; appendix table of every input | `tbs_2025_cba_guide` 7.1; `husereau_2022_cheers_ee` items 20 and 24; limits: `saltelli_2019_why`, `ec_2023_better_regulation_toolbox` Tool #65 | required |
| 7 | Variance shares by effect | Which effects carry the uncertainty? | Every case | appendix | `oakley_2004_probabilistic` 2.2; `ec_2023_better_regulation_toolbox` Tool #65, Box 4 | in a case |
| 8 | Value of information: EVPI of the decision, EVPPI of each input that matters, with the noise floor | Which research could change the decision, and what is it worth? | Every case comparing options (table); figure where research could change the choice | appendix; paper figure as stated | `fenwick_2020_value` Box 5, good practice recommendations 5 to 9, and Reporting; `rothery_2020_value` Box 2, recommendations 4, 5 and 8; `briggs_2012_model` (abstract); `strong_2014_estimating` | new (the engine computes it) |
| 9 | Switching values (break-even values), with the switching ratio; two-way break-even chart where two inputs dominate | How far must an input move before the answer changes? | Every case; the two-way chart where two inputs carry most of the variance | appendix table; paper: marked on the tornado | `hm_treasury_2026_green_book` 6.102 to 6.104; `tbs_2025_cba_guide` 7.1; `omb_2023_circulara4` 7.iii and 11.a; `omb_2003_circulara4` ("switch points"); `robinson_2019_reference` 6(b) | new |
| | **What was counted, and what was left out** | | | | | |
| 10 | Impact inventory | Was every effect considered, and what became of each? | Every case | appendix | `sanders_2016_recommendations` (impact inventory; Figure 2); `epa_2014_guidelines_economic_analyses` Table 11.1 | in part |
| 11 | Table of effects not valued, ranked, with the value each would need to change the conclusion | What is missing, and could it matter? | Every case with an effect left unvalued or only bounded | paper, appendix | `omb_2023_circulara4` 7 (p. 46) and 7.iii; `omb_2003_circulara4` (threshold analysis; summary table); `hm_treasury_2026_green_book` 6.104; `robinson_2019_reference` 6(b) | callout required; table new |
| 12 | Accounting statement | What are the benefits, costs and transfers, valued and not? | Every case | paper (or summary); appendix in full | `omb_2023_circulara4` 15 (its template); `tbs_2025_cba_guide` 9.2; `epa_2014_guidelines_economic_analyses` Table 11.4; `ec_2023_better_regulation_toolbox` (Annex 3 summary table) | new |
| 13 | Results by effect or stream | Where does the value come from? | Every case | paper (figure), appendix (table) | `sanders_2016_recommendations` Figure 2 ("Disaggregated results"); `husereau_2022_cheers` item 23 | required (appendix); figure in a case |
| 14 | Reporting checklist (CHEERS 2022) | Is everything a referee expects reported, and where? | Every case at the Normal and Full levels | appendix | `husereau_2022_cheers` Box 1 and table 1; `sanders_2016_recommendations` Figure 2 | new |
| 15 | Assumptions and decisions logs | What was chosen, by whom, and what does it move? | Every case at the Normal and Full levels | appendix | `aqua_book_2025` (Assumptions log; Decisions log); `ipcc_2013_procedures` Annex 1, 5 | required |
| | **Who gains and who pays** | | | | | |
| 16 | Distribution by group and payer, the public purse among them | Who gains, who pays, and how many of each? | Every case | paper (small table), appendix | `omb_2023_circulara4` 7 and 10; `robinson_2019_reference` 5(b)(i); `hm_treasury_2026_green_book` 7.3 and Table 12; `tbs_2025_cba_guide` 9.2 | prose required; tables in a case |
| 17 | Equity impact plane, or results in life-years by income group | Does the policy trade efficiency against equity? | Where effects fall on people of different incomes (the owner's rules 14 and 15) | appendix | `husereau_2022_cheers_ee` item 19 | new |
| 18 | Map | Where do the effects fall? | Where effects differ by place | paper | `omb_2023_circulara4` 10 ("maps may help") | new |
| | **When costs and benefits fall** | | | | | |
| 19 | Streams by year, undiscounted | What falls in each year, before discounting? | Where the case has a time path | appendix, sheet | `omb_2023_circulara4` 15.b; `omb_2003_circulara4` ("separate schedules"); `omb_1992_circulara94` 5; `epa_2014_guidelines_economic_analyses` ch. 11; `robinson_2019_reference` 1(c)(i); `husereau_2022_cheers_ee` item 23 | new |
| 20 | Time profile: costs, benefits and cumulative net benefits by year, as a fan chart | When does the policy pay back, and how sure is the path? | Where costs and benefits fall in different years | paper | `oia_2023_cba_note` Step 9; `tbs_2025_cba_guide` Figure 2; `gaf_2018_communicating_quality` (fan chart) | new |
| 21 | Discount rate and horizon table | Does the answer hang on the rate or the horizon? | Every case | appendix; the paper's results table carries the rates | `husereau_2022_cheers_ee` item 24; `robinson_2019_reference` 1(c)(iii); exemplar `shawhan_2021_rff_wp2110` Table 2 | rates required; horizon new |
| | **How the model is built** | | | | | |
| 22 | Model diagram, or theory of change | What causes what, from the action to each valued outcome? | Every case | paper (the main chain); appendix (one per model) | `husereau_2022_cheers_ee` item 16; `sanders_2016_recommendations` Figure 2; `hm_treasury_2026_green_book` 4.9; `omb_2023_circulara4` p. 69 (decision trees) | new |
| 23 | Process flowchart of the assistant's stages | How was the analysis made, and by whom? | Every case at the Normal and Full levels | appendix | No standard defines it; the owner's request (the owner's message of 2026-11-10); form as `page_2021_prisma` item 16a | required as a table, "never a figure" |
| 24 | Validation table | Does the model reproduce what is known from outside it? | Where a model exists or earlier work is reconciled | appendix | `eddy_2012_model` (abstract); `sanders_2016_recommendations` Figure 2 ("Results of model validation") | reconciliation required; table new |
| | **Where the inputs come from, and how good the evidence is** | | | | | |
| 25 | Input table with ranges, sources and the kind of evidence | What is each number, and what rests on it? | Every case | appendix in full; sheet | `husereau_2022_cheers` item 22; `husereau_2022_cheers_ee` item 22; certainty: `schunemann_2024_cochrane_ch14` 14.1, `mastrandrea_2010_ipcc` table 1 | required; evidence-kind column new |
| 26 | PRISMA flow diagram | How were studies found and screened? | Where a systematic review set an input | appendix | `page_2021_prisma` item 16a | required in that brief |
| 27 | Forest plot | What do the studies say, one by one and pooled? | Where a meta-analysis set an input (the owner's rule 9) | appendix | `page_2021_prisma` items 19 and 20b | new |
| 28 | Summary of findings table, with certainty graded | How sure is each pooled estimate? | Where a systematic review set an input | appendix | `schunemann_2024_cochrane_ch14` 14.1 | new (that brief makes no rating) |
| 29 | Independent methods figure: each method's distribution and the mixture used | Do independent methods agree? | Where an input that matters has two or more methods (the owner's rule 9) | paper or appendix | No standard defines it as a figure; nearest: `bojke_2009_characterizing`, `steegen_2016_increasing` | in a case |
| 30 | Expert estimates figure: each expert's low, best and high, with the pooled estimate | What did the experts say, and how far apart are they? | Where an elicitation ran | appendix; paper where the input leads the tornado | `hemming_2018_practical` (Figure 3 step); `bojke_2021_reference` Principle 1; exemplar `shawhan_2021_rff_wp2110` Figures 2 to 7 | new |
| | **How the options compare** | | | | | |
| 31 | Options comparison table, with doing nothing and the best other use of the money among the rows | Which option is best, and against what? | Every case | paper, appendix | `hm_treasury_2026_green_book` 2.32 and Table 12; `omb_2023_circulara4` 6; `omb_1992_circulara94` 5; the owner's rule 16 | required where options exist; the do-nothing and cash rows new |
| 32 | Incremental table, with dominated options marked | Is each step up in scale worth its extra cost? | Where options are ordered by scale or stringency | appendix; paper where the choice is between them | `omb_2023_circulara4` 6; `epa_2014_guidelines_economic_analyses` ch. 11; `fenwick_2020_value` (acceptability frontier) | in part |
| 33 | Curve of ENB against a design number | What scale is best, and how flat is the top? | Where a design number is searched | paper, appendix | `omb_1992_circulara94` 5 ("different program scales"); the owner's ruling in `notes/briefs/author_upgrade.md`:23 | required |
| 34 | Pairwise share of draws (row option above column option) | How often does each option beat each other? | Where options are compared | appendix | `fenwick_2020_value` Box 4 (choose by the mean; the error probability) | in a case (the tool prints it) |
| 35 | League table against other programmes | How does this compare with other uses of public money? | Where the decision-maker chooses among programmes, or the bar is another programme | paper | No standard defines it; exemplars `lomborg_2023_halftime` Table 1, `givewell_2026_benchmark` | new |
| | **What would change the conclusion** | | | | | |
| 36 | Scenario table | What happens under coherent alternative futures? | Every case | paper, appendix | `hm_treasury_2026_green_book` 6.73; `omb_2023_circulara4` 11.a | in a case |
| 37 | Robustness table: the headline under each reasonable alternative to each method choice and value judgement, one at a time | Does any single choice of the analyst change the answer? | Every case | appendix (it fills the decisions log's "Moves" column) | `omb_2023_circulara4` 11.c; `omb_1992_circulara94` 9.c; `husereau_2022_cheers_ee` item 24; `aqua_book_2025` (Assumptions log) | "Moves" required, or marked "not sized" |
| 38 | Specification curve, or multiverse | Across every combination of reasonable choices, how often does the answer hold? | Where three or more choices each move the result | appendix; paper where the sign or the ranking changes across it | `simonsohn_2015_specification` Figure 2 (published 2020 as `simonsohn_2020_specification`); `steegen_2016_increasing` Figs. 1 and 2 | new |
| 39 | Results under each reasonable model structure, separately and averaged | Does the answer depend on how the model is built? | Where two model structures are both defensible | appendix | `bojke_2009_characterizing`; `tbs_2025_cba_guide` 7 (model uncertainty) | in part (the owner's rule 9) |
| 40 | Tail table: chance of large losses or gains, and the share of ENB from the top draws | Is the mean driven by rare outcomes? | Where the distribution is heavy-tailed | paper, appendix | `hm_treasury_2026_green_book` 6.72 | in a case |
| | **Not recommended (part 3.3)** | | | | | |
| 41 | Cost-benefit plane (each draw's cost against its benefit) | | Not recommended | | `husereau_2022_cheers_ee` item 23 | |
| 42 | Spider plot (partial sensitivity curves) | | Not recommended, except row 33 | | `oia_2023_cba_note` Step 8 | |
| 43 | Correlation rankings (PRCC) and total-order Sobol indices | | Not recommended in the documents | | `saltelli_2008_global` (recalled); engine `outputs.prcc` | |
| 44 | Extreme bounds | | Not recommended | | `leamer_1983_lets` (not read); against it: `omb_2023_circulara4` 11.a | |
| 45 | Convergence plot | | Not recommended; one sentence gives the Monte Carlo error | | No standard found | |

## 2. The entries

Each entry gives what the item adds that nothing else does, who asks for it (quoted, with the place), exemplars, objections and limits, what exists now, and its cost with the present tools. The number matches the row. "A case" is one of the cases in the tree on 12 November 2026, named by what its documents showed.

2.1 Summary boxes.

2.1.1 They put the answer before the reasoning. GAF: "Vital messages about quality – those that have a profound impact on what can be drawn from the numbers – should be presented up front". A-4 2023 asks for the accounting statement "preferably in an executive summary" (15).

2.1.2 Exemplar: RFF WP 21-10 opens with Figure ES1, the benefit-cost ratios.

2.1.3 Now: required (`notes/briefs/author_documents.md`:20 worked example, :24 key findings, :27 tiles; `.claude/agents/case-author.md`:49).

2.1.4 Cost: none new.

2.2 Results table.

2.2.1 It gives the exact numbers the chart only shows. A-4 2023: "provide some estimates of central tendency (e.g., mean or median) in addition to ranges, variances, specified low-end and high-end percentile estimates" (11.a). A-4 2003 asks for "expected-value estimates as well as distributions". CHEERS 2022 item 23: "Report the mean values for the main categories of costs and outcomes of interest".

2.2.2 Exemplar: RFF Table 2 (benefit-cost ratios at three horizons).

2.2.3 Now: in a case (one paper's table of the answer). The briefs ask for the mean with a 90 per cent interval in the text (`notes/briefs/author_fast.md`:24); no brief asks for the table.

2.2.4 Cost: a table written by script from the results.

2.3 Interval chart.

2.3.1 It shows width and sign at a glance. GAF: "Illustrate ranges and confidence intervals".

2.3.2 Limits: a bar with an error bar is read as if the values lie inside the bar ("within-the-bar" bias, `vanderbles_2019_communicating` 4.1, citing Correll and Gleicher), so a dot and a line is the right form, as now. Showing a best estimate changes how the range is read: "including a best estimate increases perceptions that the distribution is roughly normal" (`dieckmann_2015_home`, abstract). For a skewed result that is a reason for row 4.

2.3.3 Now: required (`notes/briefs/author_documents.md`:28); in both summaries of one case.

2.4 Distribution of net benefits.

2.4.1 The interval chart hides the shape: a heavy right tail, a mass at zero, two humps. Most of the owner's cases are speculative with heavy tails (`CLAUDE.md`, "How the owner does a cost-benefit analysis"). A-94: "Ideally, probability distributions of potential benefits, costs, and net benefits should be presented" (9.a). EPA: "Ideally, an economic analysis would present results in the form of probability distributions" (11.1.4). The EC toolbox shows a box plot of Monte Carlo results (Tool #65, Box 2).

2.4.2 Forms compared for lay readers in `vanderbles_2019_communicating` Fig. 4: error bar, diamond, violin, fan and density strip.

2.4.3 Exemplar: RFF Figure 8, box-and-whisker plots from the 5th to the 95th percentile.

2.4.4 Now: new. Cost: ten lines of matplotlib from the draws the total tool already holds.

2.5 Acceptability curve, in CBA form.

2.5.1 The curve shows how the chance of the right answer changes with the bar. In health economics the bar is the threshold per QALY. Here it is the bar of the owner's rule 16 (for instance a multiple of cash transfers, `givewell_2026_benchmark`) or the discount rate. CHEERS E&E: "cost-effectiveness plane scatter plots ... and accompanying cost-effectiveness acceptability curves should be used for probabilistic analysis, if appropriate" (item 24). Briggs et al.: "Expected value of perfect information is argued to be the most appropriate presentational technique, alongside cost-effectiveness acceptability curves, for representing decision uncertainty from probabilistic analysis" (abstract).

2.5.2 Limit: the option most often first is not always the one to choose. Fenwick et al.: "The cost-effective (optimal) treatment, based on current evidence, for a risk-neutral decision maker is that which generates the highest expected (mean) NHB", and in their example "The error probability associated with the decision is 60%" (Box 4). Any share-of-draws display (rows 5 and 34) needs the sentence that the choice goes by the mean.

2.5.3 Now: new. The tool prints the share above zero at the case's rates. Cost: a loop over the bar on the same draws.

2.6 Tornado diagram.

2.6.1 It shows the reader, in one picture, which few inputs drive the answer. Treasury Board: "The result of this approach is often represented using a tornado diagram. Of particular interest are the values of different variables at which the overall net benefit present value switches from positive to negative or vice versa" (7.1). CHEERS E&E: "For deterministic analyses, tornado diagrams are useful" (item 20); "Tornado diagrams should be used if deterministic analyses are performed" (item 24).

2.6.2 Limits from the literature.

2.6.2.1 Moving one input at a time misses interactions. Saltelli et al. call such analysis "perfunctory, unless the model is proven to be linear", and they find that "moving factors OAT in ten dimensions leaves over 99.75% of the input space unexplored" (`saltelli_2019_why`). The EC toolbox says the one-at-a-time approach "is commonly used as it requires less resources, but it can be inaccurate or insufficient" (Tool #65).

2.6.2.2 Bar length is not research value. Fenwick et al. write: "Note that the parameters with the highest EVPPI will not necessarily correspond to the parameters that are most uncertain". So row 8 is the measure for "where research pays".

2.6.3 The project's form is partly protected against 2.6.2.1. It fixes one input and draws every other as usual (`notes/briefs/author_documents.md`:34; one case's appendix). Each end of a bar is then E[NB | input at that value], so the bar is two points of the input's main effect, whose variance over the input's range is Oakley and O'Hagan's main effect index, var{E(Y | X_i)} / var(Y) (`oakley_2004_probabilistic` 2.2). It averages over the other inputs, which meets one of Saltelli's criteria for a global measure. It still misses an input that matters only jointly with another, and the estimates are products of factors, which do interact.

2.6.4 Now: required (`notes/briefs/author_documents.md`:34); in one case's paper, drawn by `tools/figures.py` `tornado`. That case's appendix says "No stored source on the technique is cited". `tbs_2025_cba_guide` 7.1 and `husereau_2022_cheers_ee` items 20 and 24 are such sources.

2.6.5 Cost: hand-run cases now; one tool change (roadmap R35).

2.7 Variance shares by effect.

2.7.1 They show which effects carry the spread of the total. EC toolbox: the "most influential input variable is the stock of flammable material, causing 38% of the variance in the cost" (Tool #65, Box 4). Oakley and O'Hagan show the variance-based ranking is the value of perfect information under squared-error loss (2.5.2; used by `notes/fast_estimate.md` 2.4).

2.7.2 Limit: the tool's share is a covariance share. It sums to one over effects and can be negative. It is not the main-effect index of a single input.

2.7.3 Now: printed by `tools/estimate_total.py`:136; in one case's appendix; no brief asks the documents to carry it.

2.8 Value of information.

2.8.1 It is the only item that answers the owner's question directly: what more research or an expert survey would be worth. Fenwick et al. recommend: "Estimates of population EVPPI should be compared with the expected costs of research on specific (groups of) parameters to determine whether research is potentially valuable" (recommendation 7). On reporting: "the results of VOI analyses should be presented graphically for a range of values of the cost-effectiveness threshold". Rothery et al.: "When reporting VOI results, clearly state all underlying assumptions" (Box 2, recommendation 8).

2.8.2 Limits.

2.8.2.1 EVPPI of single inputs does not add up to that of a group, so groups that research would measure together are computed together (Fenwick et al., Box 5).

2.8.2.2 Estimates are biased upward in a finite sample, which the engine's `noise_floor` gauges (Rothery et al., recommendations 4 and 5).

2.8.2.3 Where one option is ahead in nearly every draw, every value is near zero. That is a finding, said in one sentence: research cannot change the choice. One case's appendix does this, with an EVPI of $0.

2.8.3 Now: new as a display. The engine computes `evpi`, `evppi` and `noise_floor` (part 5). One case's appendix reports EVPI and partial values in text.

2.8.4 Cost: a table from existing functions once the per-factor draws are exposed (roadmap R35).

2.9 Switching values.

2.9.1 A switching value tells a reader with a different view of an input whether that view changes the answer. It is the form of sensitivity a reader can use without the model. The Green Book: "at a minimum, conduct sensitivity analysis and calculate switching values for the preferred option. These results should be included in the presentation" (6.102 to 6.104). Treasury Board: "A low switching ratio (switch value / expected value) suggests the project is very sensitive to that variable" (7.1). A-4 2003: sensitivity analysis can be used to find 'switch points', "critical parameter values". A-4 2023 asks for the values at which the "relative ranking of regulatory options changes" (11.c). It also gives the two-way form, a diagonal break-even curve dividing "a diagram with X and Y axes, or a table with X and Y rows and columns, into regions with positive and negative net benefits" (7.iii).

2.9.2 With draws, the switching value of an input is where E[NB | input] crosses zero or another option's line: the point where a tornado bar crosses. Where it lies outside the input's range, the table says so.

2.9.3 Now: new; one case's table of what would change the ranking is near it. Cost: a root-find along the same conditional means as row 6.

2.10 Impact inventory.

2.10.1 It shows a referee that nothing was silently dropped. The Second Panel: "The impact inventory should be completed and reported for all analyses" (`sanders_2016_recommendations`). EPA Table 11.1 is a benefits checklist.

2.10.2 Now: in part. The pooled list (`effects/pooled.md`) holds it, and the appendix's effects table holds the estimated ones (`notes/briefs/author_upgrade.md`:17). No document carries the whole inventory, with what became of each effect. Cost: a script over the pooled list.

2.11 Effects not valued, ranked, with a break-even value.

2.11.1 A-4 2023 asks for a "summary table that lists all the unquantified or non-monetized benefits and costs", rank-ordered and "placed prominently" (7, p. 46). It also asks: "How small could the value of the non-monetized benefits be ... (or before the most net-beneficial regulatory alternative changes)?" (7.iii). A-4 2003 has the same pair: a "threshold" analysis and "a summary table that lists all the unquantified benefits and costs". The Green Book gives the switching value of an unmonetisable benefit (6.104). Robinson et al. ask that nonquantified effects be listed and ranked, with a breakeven or bounding analysis (6(b)).

2.11.2 Now: the callout of effects left out is required (`notes/briefs/author_documents.md`:26); the ranked table and its break-even column are new. Cost: the break-even column is ENB at the decision margin, already computed.

2.12 Accounting statement.

2.12.1 It is the one table every regulator's reader expects. It has three categories, monetized, quantified but not monetized, and unquantified, with primary, low and high estimates and transfers kept apart (A-4 2023, section 15, with its template). Treasury Board's cost-benefit statement is the same by stakeholder and year (9.2). EPA Table 11.4 summarises benefits and costs. The EC requires an "obligatory summary table of the Annex 3".

2.12.2 Limit: it repeats rows 2 and 13 in another arrangement. The case for it is that readers in government look for it.

2.12.3 Now: new. Cost: a table from results already held.

2.13 Results by effect or stream.

2.13.1 Second Panel checklist: "Disaggregated results for important categories" (Figure 2). Exemplar: the Copenhagen Consensus reports cost, lives saved and benefit-cost ratio across 12 interventions (`lomborg_2023_halftime` Table 1).

2.13.2 Now: required in the appendix, as the effects table by script (`notes/briefs/author_upgrade.md`:17); the figure is in one case's paper.

2.14 Reporting checklist.

2.14.1 It is a table of the standard's items, each with the section that answers it or "not applicable". Journals that publish economic evaluations ask for it, and it is the mark of a complete report. CHEERS 2022 was "broadened to make CHEERS more widely applicable to cost-benefit/benefit-cost analysis" (Box 1). The Second Panel's Figure 2 is a reporting checklist.

2.14.2 Limit: many items assume health outcomes and will read "not applicable".

2.14.3 Now: new. Cost: a template filled once per case, about a page in the appendix.

2.15 Assumptions and decisions logs. Required (`notes/briefs/author_upgrade.md`:18 to :21). The AQuA book's assumptions log asks each assumption's analyst to "quantify its effect and reliability". Row 37 fills its "Moves" column.

2.16 Distribution by group and payer.

2.16.1 A-4 2023 asks for net benefits by subgroup (7, 10). Robinson et al. ask for "the expected number of individuals who accrue net costs and/or benefits" (5(b)(i)). The Green Book's appraisal summary table has columns for "public sector financial impact" and "distribution" (Table 12). The owner's rule 12: report who bears the costs and who will resist.

2.16.2 Now: prose is required (`notes/briefs/author_documents.md`:34). One case's paper has tables of outlays by payer and of what each group is asked to do.

2.16.3 Cost: a table, where the estimates carry who gains and who pays.

2.17 Equity impact plane. CHEERS E&E item 19 names the "equity-efficiency impact plane" for analyses of distribution. Here the natural form is the owner's rule 15: results in life-years by income group. New; worth its space only where incomes differ.

2.18 Map. A-4 2023: "maps may help" (10). New; only where effects differ by place.

2.19 Streams by year, undiscounted.

2.19.1 It lets a reader re-discount and check the arithmetic. It is asked for by more standards than any other table:

2.19.1.1 A-4 2023 15.b (undiscounted streams for each year, in a table separate from the accounting statement).

2.19.1.2 A-4 2003 ("separate schedules of the monetized benefits and costs").

2.19.1.3 A-94: "Key data and results, such as year-by-year estimates of benefits and costs, should be reported to promote independent analysis and review" (5).

2.19.1.4 EPA ch. 11 ("Separate time streams of benefits and costs should be reported").

2.19.1.5 Robinson: "The distribution of undiscounted costs and benefits over time should be reported" (1(c)(i)).

2.19.1.6 CHEERS E&E item 23 (discounted and undiscounted).

2.19.2 Limit: a fast estimate is a present value without a time path. There, one sentence says so.

2.19.3 Now: new. Cost: the engine's timeline functions write it where a model has a timeline (`cost_benefit_engine/README.md`).

2.20 Time profile. OIA: "Your conclusion should include the time profiles of costs, benefits and net benefits" (Step 9). Treasury Board, Figure 2: baseline against the regulatory scenario over time. GAF shows a fan chart as its example of a range over time. Exemplar: Copenhagen Figure 3, costs by year. New.

2.21 Discount rate and horizon. CHEERS E&E: "Authors should always report the impact of choice of discount rate and time horizon" (item 24). Robinson asks for a standardized sensitivity at 3 per cent and at twice the growth of GDP per capita (1(c)(iii)). Exemplar: RFF Table 2 at 10, 20 and 30-year horizons. The rates are required; a second horizon is new and costs one rerun.

2.22 Model diagram, or theory of change.

2.22.1 It gives the reader the causal story before the numbers. CHEERS E&E: "In most cases, a figure illustrating the model structure and patient flows through the model is recommended" (item 16). Second Panel checklist: "Diagram of event pathway or model". The Green Book's theory of change is "the logical chain of cause and effect", with "Figure 3 provides a graphical illustration" (4.9). A-4 2023: "Decision trees may be helpful visual devices" (p. 69).

2.22.2 Now: new. `notes/briefs/author_upgrade.md`:22 says `tools/typeset.py` "draws no diagram (its LaTeX layout loads no drawing package)", and so orders the process flowchart as a table, "never a figure". A diagram drawn as a PNG by graphviz (`/usr/bin/dot` is installed) or by matplotlib typesets as any other figure, so that reason does not hold. The owner asked for "a flowchart of the process used" (the owner's message of 2026-11-10).

2.22.3 Cost: a short dot file per case.

2.23 Process flowchart. No standard defines a flowchart of an analysis's own process. PRISMA's flow diagram (item 16a) is the nearest established form. Required as a table now (2.22.2); a figure if he chooses.

2.24 Validation table. The ISPOR task force on transparency and validation names "face validity (wherein experts evaluate model structure, data sources, assumptions, and results)" among the kinds of validation (`eddy_2012_model`, abstract). The Second Panel checklist asks for "Results of model validation". The house rule CORE 3.3 is that a result is checked against reality, not an earlier output. A table, one row per check with whether it passed, makes that visible. The reconciliation with earlier work is required (`notes/briefs/author_upgrade.md`:17); the table is new.

2.25 Input table.

2.25.1 CHEERS E&E: "Providing a table with all the input values and data sources used is critical to full reporting", with "a table with key parameters in the main body of the report with a supplementary table of the ranges and actual distributions" (item 22).

2.25.2 The evidence-kind column (measured data, one study, pooled studies, judgement) is the light form of the grading of Cochrane and IPCC (`schunemann_2024_cochrane_ch14`; `mastrandrea_2010_ipcc`). The tornado already marks judgements.

2.25.3 Now: required in the appendix (`notes/briefs/author_upgrade.md`:17; `cost_benefit_engine/documents.py`:234 `input_table`). In the paper the tornado's labels carry the key inputs, so no second table is proposed there.

2.26 PRISMA flow diagram. PRISMA 2020 item 16a: "ideally using a flow diagram". Required where a systematic input review runs (`notes/briefs/systematic_input_review.md`:130, "as a table and a Mermaid chart"; a Mermaid chart needs a renderer the typesetter lacks, while dot does not).

2.27 Forest plot. PRISMA 2020 item 19 asks for results of individual studies, "ideally using structured tables or plots", and item 20b for the summary estimate, its precision and heterogeneity. The owner's rule 9 orders a random-effects meta-analysis, reporting the prediction for a new setting, for a major input with enough studies. The forest plot with the prediction interval is that analysis's standard figure (recalled; the Cochrane chapter on meta-analysis is not stored). New.

2.28 Summary of findings. Cochrane: "'Summary of findings' tables include a row for each important outcome (up to a maximum of seven)", each graded for certainty (14.1). The systematic input review brief makes no grading and says so (`notes/briefs/systematic_input_review.md`:97). New; it applies only where such a review ran.

2.29 Independent methods figure. The owner's rule 9 uses every independent method, as a mixture or by overlap. A figure of each method's distribution and the mixture shows whether they agree. No standard defines it as a figure. The nearest are model averaging (`bojke_2009_characterizing`: "Two methods to explicitly characterize such uncertainties were identified: model selection and model averaging") and the multiverse (row 38). In a case.

2.30 Expert estimates figure. The IDEA protocol: "Create graphs for each question to display the estimates of each participant (labelled with their codename) and the group aggregate (Figure 3)" (`hemming_2018_practical`). Its purpose is feedback between rounds, and it is also how a reader sees the spread of judgement. Exemplar: RFF Figures 2 to 7, each expert's 10th, 50th and 90th percentiles with a fitted density. New; it applies where an elicitation ran (offered after the Normal level).

2.31 Options comparison table.

2.31.1 It is the decision itself in one table.

2.31.1.1 The Green Book's appraisal summary table has rows for business as usual, do minimum, preferred, more ambitious and less ambitious options (2.32, Table 12). It warns that the summary "helps to avoid the tendency to reduce appraisal results to a simple comparison of benefit-cost ratios" (9.3).

2.31.1.2 A-4 2023 asks for at least three options, at least one more ambitious and one costing less (6, pp. 21 to 22), and to "document all of the alternatives that were assessed in a list or table".

2.31.1.3 A-94 lists "(i) doing nothing" first among alternatives (5).

2.31.1.4 The owner's rule 16 sets the bar as the best other use of the same money, such as cash to the same people. That is a row of this table, not a footnote.

2.31.2 Now: the brief requires options "compared in one table" (`notes/briefs/author_upgrade.md`:23). Rows for doing nothing and for the best other use of the money are new.

2.32 Incremental table. A-4 2023 asks for "both total and incremental benefits and costs" between alternatives, against "the next less-stringent alternative" (6). EPA: "The incremental costs and non-monetary benefit yield of each option, in order of increasing stringency, should be reported". In health economics the same idea is the acceptability frontier and extended dominance (`fenwick_2020_value`). In part: one case's pairwise table.

2.33 Curve against a design number. A-94 asks for alternatives "examining different program scales" (5). The owner's ruling: "report the curve of expected net benefits against the value" (`notes/briefs/author_upgrade.md`:23). Required; in a case (`paper_search.png`).

2.34 Pairwise share of draws. It answers how often one option beats another, but needs the sentence of 2.5.2. Printed by the tool; in one case's appendix.

2.35 League table. It places the case among other uses of money, which the owner's rule 16 makes the real comparison. Exemplars: Copenhagen Consensus Table 1 (12 interventions by benefit-cost ratio); GiveWell's benchmark as multiples of cash, with a funding bar of 6 times the benchmark as of May 2026 (`givewell_2026_benchmark`). No standard defines it. New; it needs sourced figures for the other programmes.

2.36 Scenario table. The Green Book separates scenario analysis (6.73) from sensitivity analysis. A-4 2023 allows "varying a combination of variables simultaneously" (11.a). In a case (a table of what would change the ranking).

2.37 Robustness table.

2.37.1 It is the economist's standard robustness table: one row per method choice or value judgement, with the headline under each reasonable alternative. A-4 2023 asks that inputs a result depends on be made explicit with "sensitivity analyses using plausible alternatives" (11.c). A-94: "Major assumptions should be varied and net present value and other outcomes recomputed" (9.c).

2.37.2 Now: the decisions log's "Moves" column is required, filled from sensitivity results or marked "not sized" (`notes/briefs/author_upgrade.md`:19). The robustness table makes that mark rare.

2.37.3 Cost: one rerun per alternative on common draws.

2.38 Specification curve, or multiverse.

2.38.1 It shows every combination of reasonable choices at once, so a reader sees whether the answer holds across all of them rather than across the one the analyst picked.

2.38.1.1 Simonsohn, Simmons and Nelson: the descriptive curve serves two functions, displaying the range of estimates and identifying "analytic decisions that are most consequential". Their Figure 2 sorts the estimates in an upper panel, with a lower panel marking each one's choices.

2.38.1.2 Steegen et al.: "A multiverse analysis involves performing the analysis of interest across the whole set of data sets that arise from different reasonable choices".

2.38.2 Limits: the share of specifications with a positive result is not a probability, since the choices are not equally credible. Where they are weighted, the result is model averaging (row 39).

2.38.3 Now: new. Cost: a grid loop on common draws, the same machinery as row 33. The owner named specification testing in his message.

2.39 Model structure. Bojke et al. name "model selection and model averaging" (abstract). Treasury Board: results "should be evaluated for each alternative model separately and then compared" (7). In part: the owner's rule 9 mixes independent methods for an input, not whole structures.

2.40 Tail table. Green Book: "Confidence intervals and P90 values often do not adequately capture these risks" (6.72). In a case (an appendix's section on tails); the total tool flags effects with a large tail share.

2.41 Cost-benefit plane. CHEERS E&E calls the cost-effectiveness plane "a helpful aid to understanding the extent to which interventions are dominated or extendedly dominated" (item 23). In a CBA both axes are money and net benefits already says what the plane shows; dominance goes in row 32. Not worth its space.

2.42 Spider plot. OIA: "Partial sensitivity analysis: examines how net benefits change as one variable varies over a plausible range" (Step 8). The tornado and switching values say the same in less space, so it is not worth its space. The exception is the design curve of row 33, which is a spider plot of the one variable the decision sets.

2.43 PRCC rankings and total-order indices. The engine computes PRCC, and one case's appendix reports it. A third ranking measure beside the tornado and the variance shares costs attention and adds little. PRCC is unitless and measures monotone association, not how far an input moves ENB. Total-order Sobol indices capture interactions, the tornado's blind spot (2.6.2.1), but need a designed sample (Saltelli et al. 2008, recalled). They are worth adding only where a model's inputs interact strongly and the tornado and the variance shares disagree. Not in the documents.

2.44 Extreme bounds. Leamer 1983 (not read; the entry says its abstract was not retrieved). The specification curve shows every combination rather than only the extremes. A-4 2023: "Worst-case or bounding analyses do not adequately convey the complete probability distribution" (11.a). Not worth its space.

2.45 Convergence plot. One sentence giving the Monte Carlo standard error of ENB says what a running-mean plot shows. Not worth its space.

## 3. Recommendation, in three tiers

The recommendation is the research seat's. It weighs the owner's point that these items are cheap to make from the code, so their cost is mostly the reader's attention and the pages. "Broad but shallow" (`notes/briefs/simplicity.md`) limits what the model computes, not how much of what it already computes is shown. So the appendix carries every Tier 1 table, since its readers are experts who look things up. The paper carries the figures and small tables that answer a lay reader's main questions, about one per spread (`notes/briefs/author_documents.md`:34). The summary keeps what it has.

3.1 In every paper.

3.1.1 Already required: 1 summary boxes; 3 interval chart; 6 tornado diagram; 13 results by effect; 15 assumptions and decisions logs; 23 process flowchart (as a table now); 25 input table; 31 options comparison table.

3.1.2 New or only in a case:

3.1.2.1 2 results table (in a case).

3.1.2.2 4 distribution of net benefits (appendix; paper where skewed).

3.1.2.3 7 variance shares by effect (in a case).

3.1.2.4 8 value of information (appendix table).

3.1.2.5 9 switching values (appendix; marked on the tornado).

3.1.2.6 10 impact inventory.

3.1.2.7 11 effects not valued, ranked, with break-even values.

3.1.2.8 12 accounting statement.

3.1.2.9 14 reporting checklist (Normal and Full).

3.1.2.10 16 distribution by group and payer (in a case).

3.1.2.11 21 discount rate and horizon.

3.1.2.12 22 model diagram.

3.1.2.13 36 scenario table (in a case).

3.1.2.14 37 robustness table.

3.1.2.15 Rows for doing nothing and the best other use of the money in table 31.

3.1.3 In the paper this adds about six exhibits to the five figures and nine tables the fullest paper of that date had: the results table, effects not valued, the accounting statement, the distribution table, the model diagram and the scenario table. The rest goes in the appendix.

3.2 Where the case has the feature that calls for it.

3.2.1 5 acceptability curve: the bar or the rate is disputed.

3.2.2 8 value-of-information figure in the paper: research could change the choice.

3.2.3 9 two-way break-even chart: two inputs dominate.

3.2.4 17 equity plane: incomes differ.

3.2.5 18 map: effects differ by place.

3.2.6 19 streams by year: a time path exists.

3.2.7 20 time profile: costs and benefits fall in different years.

3.2.8 24 validation table: a model or earlier work exists.

3.2.9 26 PRISMA flow, 27 forest plot and 28 summary of findings: a systematic review or meta-analysis ran.

3.2.10 29 independent methods: two or more methods for an input that matters.

3.2.11 30 expert estimates: an elicitation ran.

3.2.12 32 incremental table: options ordered by scale.

3.2.13 33 design curve: a design number is searched.

3.2.14 34 pairwise shares: several options.

3.2.15 35 league table: a choice among programmes.

3.2.16 38 specification curve: three or more choices each move the result.

3.2.17 39 model structures: two defensible structures.

3.2.18 40 tail table: a heavy tail.

3.3 Not worth the space.

3.3.1 41 cost-benefit plane: both axes are money (2.41).

3.3.2 42 spider plot, except the design curve (2.42).

3.3.3 43 PRCC and total-order indices in the documents (2.43).

3.3.4 44 extreme bounds (2.44).

3.3.5 45 convergence plot (2.45).

3.3.6 Pie charts, 3-D effects and dual axes (part 4).

3.4 Points that are the owner's.

3.4.1 The tornado or value of information as the paper's figure of "where research pays". The tornado shows what moves the result. EVPPI shows what research is worth, and the literature prefers it for that question (2.6.2.2, 2.8.1). The options:

A. Keep the tornado in the paper and add the value-of-information table in the appendix. This is the seat's recommendation: lay readers read a tornado easily, and the appendix gives referees the measure the literature asks for.

B. Put a value-of-information bar chart in the paper beside the tornado.

C. Keep one figure, ordering or marking the tornado's bars by EVPPI.

3.4.2 Whether the process flowchart (row 23) becomes a figure. The brief's reason for a table (2.22.2) no longer holds.

3.4.3 Which items the summary carries. It keeps its tiles, interval chart and outcomes table. The accounting statement could replace the outcomes table where the reader is a regulator.

## 4. What makes a proper scientific table and a good chart

Each rule names its source. Where a rule is recalled, it says so.

4.1 Tables.

4.1.1 Horizontal rules only, no vertical lines, no shading. AEA: "Use only horizontal lines and additional blank space", "Do not use shading" (`aea_aer_style_guide`). APA: "Do not use vertical borders" (`owl_2026_apa_tables_figures`).

4.1.2 Every table numbered, with a title that says what it shows, every column headed, and the units in the head. AEA: "Do not abbreviate in column headings". APA: numbered tables with clear titles, and notes in three kinds, general, specific and probability.

4.1.3 Few columns. AEA asks for at most 9, with Panel A and Panel B for subsets.

4.1.4 Uncertainty in brackets beside or beneath the estimate, never stars. AEA: "Do not use asterisks to denote significance of estimation results". Standard errors in parentheses beneath the estimate is the economics convention (recalled; not in the stored guide). Here, the 90 per cent interval takes that place.

4.1.5 The source in a note under the table, last (AEA).

4.1.6 Numbers right-aligned on the decimal point, with one precision within a column, rounded to the digits that matter. Schwabish 2020 presents "10 guidelines for creating better, more effective tables" (abstract stored; the guidelines themselves recalled). Ehrenberg 1977 (recalled): round to two effective digits, order rows by size rather than alphabet, and put figures to be compared in columns. A-4 2023 asks for estimates that do not "create a false sense of precision", "including using appropriate significant figures" (15, "Precision of Estimates").

4.1.7 A table where exact values matter, a chart where a pattern does. Schwabish 2020: tables "are useful when you want to show the exact values of your data or estimates" (abstract).

4.2 Charts.

4.2.1 Every chart has a title, a source line and labels. Urban: "Urban charts require a title, source line, and axis or other labels". The title states the finding (Urban's active titles; `notes/briefs/author_documents.md`:34, "each chart's caption opening with its finding").

4.2.2 Label the data directly rather than through a legend (Urban: "directly label the data").

4.2.3 Bars start at zero (Urban: "should always start at zero"). For a range, use a dot and a line, not a bar with an error bar (the within-the-bar bias, 2.3.2).

4.2.4 No 3-D and no special effects (Urban: "Stay away from 3-D"; APA). No dual axes. Urban: "Charts that have two axes ... should be avoided".

4.2.5 Small multiples share their scales. Urban: each multiple should "use the same type of scales, which should start and end at the same values"; Tufte 2001, recalled.

4.2.6 Position along a common scale is read more accurately than length, angle, area or colour (Cleveland and McGill 1984, recalled). So use dot plots and bars rather than pies.

4.2.7 Colour by data type: categorical, sequential or diverging palettes (Urban). Colour that stays readable to colour-blind readers is recalled practice, not checked in the stored guide.

4.2.8 Ink on data, not on decoration (Tufte 2001, recalled).

4.3 Showing a range to a lay reader.

4.3.1 Put uncertainty up front, beside the numbers it qualifies (GAF: "Critical quality caveats or warnings should be included in the commentary besides the points that they relate to").

4.3.2 Show ranges graphically. GAF: "Illustrate ranges and confidence intervals"; fan charts are its example. The statistics regulator found uncertainty better shown in bulletins than in data tables, and "it can be particularly useful when producers show uncertainty in a graphical form" (`osr_2022_presenting_uncertainty`, landing-page summary).

4.3.3 Give a best estimate with the range, knowing that it pulls readers toward a symmetric reading (`dieckmann_2015_home`).

4.3.4 Graphics work differently for readers of different numeracy (`spiegelhalter_2011_visualizing`: "the effectiveness of some graphics clearly depends on the relative numeracy of an audience"). Verbal terms, where used, follow a calibrated scale (`mastrandrea_2010_ipcc` table 1).

4.3.5 Stating uncertainty costs little trust. Van der Bles et al. found "only a small decrease in trust in numbers and trustworthiness of the source, and mostly for verbal uncertainty communication" (`vanderbles_2020_effects`).

## 5. What the code already computes

5.1 `cost_benefit_engine/value_of_information.py`.

5.1.1 `evpi(net_benefits)` (:68): E[max over options] − max over options of E. `net_benefits` is draws by options, and doing nothing is a column of zeros.

5.1.2 `evppi(net_benefits, key, fit="bins"|"spline", bins=50)` (:73) replaces net benefits by their conditional mean on one input's draws, after Strong and Oakley (2013) and Strong, Oakley and Brennan (2014).

5.1.3 `noise_floor(net_benefits, key, rng, permutations=20, ...)` (:83) is the largest EVPPI over random permutations of the key, the upward bias to beat.

5.1.4 They feed row 8: a table, or a bar chart of EVPPI by input with the noise floor drawn as a line and EVPI as the ceiling.

5.1.5 The same conditional mean gives, at no extra cost, each input's main-effect variance share (var of E[NB | input] over var of NB, `oakley_2004_probabilistic` 2.2) for row 7 at the level of inputs. It also gives each input's switching value for row 9: where the fitted conditional mean crosses zero or another option's.

5.1.6 Limit: `evppi` takes one key, so EVPPI of a group of inputs (2.8.2.1) needs a fit on several keys. Strong, Oakley and Brennan's method allows that; the engine does not do it.

5.1.7 The functions are used in one case's own model run, not in `tools/estimate_total.py`.

5.2 `tools/estimate_total.py`.

5.2.1 It prints each effect's variance share (:136), the share of draws in which each option is highest, the pairwise shares and the removable benefits.

5.2.2 It holds every option's draws, so EVPI over options (row 8) and the acceptability curve (row 5) need no new draws.

5.2.3 It reports nothing per factor. The tornado, per-factor EVPPI and switching values all wait on that one change (roadmap R35), which should expose each factor's draws beside the totals.

5.3 Elsewhere.

5.3.1 `outputs.prcc` and `analysis.ranked_prcc` (row 43).

5.3.2 The timeline functions (rows 19 and 20).

5.3.3 `documents.input_table` (`cost_benefit_engine/documents.py`:234, row 25).

5.3.4 Matplotlib 3.11.2 in the venv, and `/usr/bin/dot` (row 22).

5.3.5 One case's own figures script had functions for tiles, intervals, groups, methods, search and tornado; `tools/figures.py` holds the tornado as the shared figure library's first function.

## 6. What could not be established, and sources not obtained

6.1 Not established.

6.1.1 No standard was found that defines a figure of independent methods (row 29), a league table (row 35), a process flowchart (row 23) or a convergence plot (row 45).

6.1.2 GiveWell's practice on showing uncertainty (25th and 75th percentiles; tornado charts in 2017) is known only from a search summary, since its page could not be fetched.

6.1.3 No praised US regulatory impact analysis was identified to serve as an exemplar of figures. The exemplars used are RFF, Copenhagen Consensus and GiveWell.

6.1.4 How the published specification curve paper (2020) differs from the stored 2015 working paper was not checked.

6.1.5 The OSR quote is from its landing page; the full report was not read.

6.2 Sources not obtained, with their addresses.

6.2.1 Briggs et al. 2012, full text: Value in Health returned 403, and the abstract is stored from Europe PMC (`briggs_2012_model`); the full text of its Medical Decision Making printing is stored as `briggs_2012_model_mdm`.

6.2.2 Schwabish 2014, "An economist's guide to visualizing data": https://www.aeaweb.org/articles/pdf/doi/10.1257/jep.28.1.209, 403 from the AEA.

6.2.3 Schwabish 2020, full text: paywalled; the abstract is stored (doi:10.1017/bca.2020.11).

6.2.4 GiveWell's page on uncertainty: https://www.givewell.org/node/3974, refused by its bot wall twice. It was not worked round.

6.2.5 The OSR full report: https://osr.statisticsauthority.gov.uk/wp-content/uploads/sites/3/2022/09/Approaches_to_presenting_uncertainty_in_the_statistical_system.pdf. Found, not fetched.

6.2.6 Cleveland and McGill 1984: doi:10.1080/01621459.1984.10478080, closed.

6.2.7 Ehrenberg 1977: doi:10.2307/2344922, closed.

6.2.8 Tufte, books.

6.2.9 Leamer 1983: JSTOR.

6.2.10 Eschenbach 1992 on spider plots: doi:10.1287/inte.22.6.40, closed.

6.2.11 Spiegelhalter et al. 2011: closed; the abstract is in refs.

6.2.12 Bojke et al. 2009: abstract only.

6.2.13 Fenwick, O'Brien and Briggs 2004 on acceptability curves: doi:10.1002/hec.903, closed.

6.2.14 Barton, Briggs and Fenwick 2008 on the acceptability frontier: not tried.

6.2.15 Howard 1988, Morgan and Henrion 1990, Clemen 1996 and Saltelli et al. 2008: books or closed.

6.2.16 Claxton 1999: no free copy, as its entry records.

6.2.17 CBO and ICER reports: not tried. CBO refused fetches in earlier sessions.

6.2.18 The Cochrane chapter on meta-analysis, for the forest plot: not tried.

6.2.19 Cited above with no stored full text: `bojke_2021_good` has no stored text and no title in its entry, and `bojke_2021_reference` holds the "Principle 1" row 30 cites; `strong_2014_estimating` has a bibliographic record only; `simonsohn_2020_specification` is stored as its abstract, and its working paper `simonsohn_2015_specification` in full; Robinson's reference case (`robinson_2019_reference`) is stored as its summary only, and the full report was not read.
