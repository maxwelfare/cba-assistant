# Research pipeline

Proposed 2026-10-29; revised the same day on the owner's rulings [the owner's message of 2026-10-29]: we run the whole literature review ourselves, teammates read the written review as journal referees, free models never see client material, and the pipeline is built alongside the engine in whatever order is cheapest in the long run. Built: search of OpenAlex, Crossref and PubMed with citation chasing (`bibliography.py`), the record table with its PRISMA counts, source storage and the quote check (`records.py`) and Cooke's classical model (`panel_scoring/classical.py`); not built: swarm screening, the PRISMA diagram and a panel runner. The evidence each choice rests on is in `research_pipeline_evidence.md`; the sources for the synthetic panel are cited in its section below.

## What it is for

The owner usually starts a case knowing the economics but not the field. The pipeline does three jobs for every case:

1. **Orientation:** bring him, in about an hour of reading, to where he can talk with the field's experts: what the field knows, how it is organised, its key quantities with their ranges, its live disputes and who holds each side, its vocabulary and its data sources.
2. **Input dossiers:** for each input of the case's model, the candidate values with their sources, quotes and uncertainty, combined into the input's distribution.
3. **Gaps:** what the literature cannot settle goes to a synthetic expert panel and, where it matters, to human experts.

The written review is a document a teammate reads as a journal referee would. Teammates' effort goes to getting expert interviews for what is not in the literature, not to searching or screening.

## How AI literature reviews fail, and the guard against each

1. **Invented sources.** Language models cite works that do not exist when they answer from memory (18% of GPT-4's citations in Walters and Wilder 2023; GPT-4o 78–90% in the OpenScholar evaluation). Guard: every source comes from a logged database query or a citation chase, resolves to a DOI or URL that was fetched, and every value carries a verbatim quote a machine checks against the stored text. A model may suggest search terms, never sources.
2. **Low recall.** Search through one database interface found under 20% of a review's relevant papers where expanding through bibliographies found over 80% (Sahu, Charlin and Pal 2026, preprint); in an audited complex review, 51% of sources came from citation chasing, 30% from the protocol's database searches and 24% from personal knowledge and contacts (Greenhalgh and Peacock 2005). Guard: broad keyword searches across several databases, then citation chasing backward and forward from what they find; recall is measured on a known-item set before screening ends; and the referee read is where a teammate's knowledge of a missing work comes in.
3. **Bias toward what is already famous.** Models over-cite highly cited papers, more than human authors do (Algaba et al. 2024, preprint). Guard: inclusion is decided by written criteria, never by a model's taste; the primer's reading list takes, from each cluster of the field, its best synthesis, its newest strong work and its strongest critique; and the citation counts of what was included are compared with those of all records screened.
4. **One-sided reading.** Guard: a separate search for critiques, null results and rival schools; the primer names each side with its best work.
5. **Unchecked screening.** A single model screening titles and abstracts reaches high sensitivity with low specificity (Tran et al. 2024: 94.6–99.8% sensitivity at 2.2–46.6% specificity on its sensitive rule). Guard: the Cochrane rapid-review pattern (Garritty et al. 2021): every record screened, at least a fifth screened twice, and every exclusion checked a second time. Here two Anthropic screeners screen every record, a third seat settles their disagreements, and an analyst audits a sample (`notes/briefs/systematic_input_review.md` 5.1 to 5.3 and 9.4).

## The process

An input's review is run and reported to PRISMA 2020 by the brief `notes/briefs/systematic_input_review.md`. Orientation is a scoping review (Arksey and O'Malley 2005: as comprehensive as practical, no quality appraisal), run with the same search and record tools; it ends in the primer and reading list, every claim quote-backed, read cold by a fresh agent for gaps and one-sidedness.

## Synthetic expert panel

For a quantity the literature cannot settle (for example, the probability that a contested event happens by a given year), a panel of AI consultants, each given a specialist's brief and the same evidence pack from the pipeline, estimates it [the owner's message of 2026-10-29]. It serves two purposes: a test of the model (an input where the panel and the humans disagree, and where the result is sensitive, is where to look first) and a sanity check on human elicitation.

1. **Protocol.** The IDEA steps (Hemming et al. 2018): each panellist estimates alone (lowest, highest and best value, and how confident it is that the truth lies between), sees the others' estimates and reasons without names, and revises; the estimates are pooled as a mixture. The panel's reasons are kept with its numbers.
2. **Diversity.** Panellists differ in role (for example: a scientist of the field, an economist, a practitioner, a forecaster) and in model family, since panellists from one model share its errors. Free models sit on a panel only when its brief and evidence are entirely published material.
3. **Calibration.** Before a panel's numbers are trusted, the same panel answers questions whose answers are known and that its models cannot have seen (resolved after their training cutoff), and is scored as in Cooke's classical model.
4. **Standing.** A panel's estimate is labelled synthetic wherever it appears; it is never presented as a human expert's. It enters a case as a check or as one specification among others, drawn by credence weight (CBA 301 rule 9), never as a silent replacement for human judgement.

Evidence: an ensemble of 12 language models forecasting 31 binary questions was statistically indistinguishable from a crowd of 925 human forecasters, showed human-like biases such as acquiescence, and improved when shown the human median (Schoenegger, Tuminauskaite, Park, Bastos and Tetlock 2024, *Science Advances* 10(45), doi:10.1126/sciadv.adp1528); a retrieval-based forecasting system came close to the crowd of competitive forecasters on questions published after its models' cutoff (Halawi, Zhang, Chen and Steinhardt 2024, NeurIPS, arXiv:2402.18563). Against it: language models asked to answer as personas reproduce survey averages but raise doubts about the quality, reliability and reproducibility of what they produce (Bisbee et al. 2024, *Political Analysis* 32:401–416, doi:10.1017/pan.2024.5). These were read from abstracts and search summaries, not full texts.

## Records

Everything stays in this project folder. An input's review (its protocol, search log, record table with each work, how it was found and each decision with its reason and seat, extractions and written review) lives in the case, `cases/<case>/reviews/<input>/`, and every source a case uses in the case's `sources/<key>/`, which goes with the case when it is shared (`CLAUDE.md`, "Where things live"); `research/<case>/` holds orientation and the panel runs, and `research/sources/` the project's methods literature. Free models never see client material [the owner's message of 2026-10-29].

The files that cite a source in `research/refs.toml` are found by searching the tree for its key: `git grep -l KEY`. The index keeps no list of them.

Each run reports: recall on the known items; screening agreement; quotes found and not found; sources that failed to resolve (zero is the only pass); the share of included works by route (database, citation chase, other); and the citation counts of included works against all records screened.

## Tools

New: a bibliographic client (OpenAlex first, with Crossref and PubMed; each query logged; references and citing works), an open-access lookup, the retraction check (Crossref), the known-item test, the screening swarm, the PRISMA flow-diagram generator, and the panel runner. From the shared folder: the polite downloader, the quote-checked extraction and the two-model free fan-out; and the pattern of one research agent per question.

## The test, written before the code

A blind rerun of finished, published analyses, the pipeline given only each one's question and list of inputs: for example, the mpox stockpile investment case (*The Lancet Global Health*, 2026, doi:10.1016/j.langlo.2026.104069) and the UK synthetic nucleic acid screening report (CLTR 2025, doi:10.71172/kyey-h0ya). Measured: the share of each analysis's load-bearing sources (those that set an input's value) the pipeline finds; whether each input's range covers the published value; zero unresolved sources and zero failed quotes; and, read by the owner, which works it found that the published analysis lacked. A human citation list is not a perfect answer key (Sahu et al. 2026), so each miss is read, not only counted. The test passes on two conditions: no unresolved source or failed quote, and no missed source that would have moved an input's distribution materially, which the reading of each miss decides. The recall of load-bearing sources is reported, not gated; 80% is a suggested reference point, the recall bibliography expansion reached in Sahu et al. 2026, not a ruled threshold [the owner's message of 2026-10-29]. Orientation is tested on a field the owner now knows: he reads the primer and reading list for one such field and says what a newcomer would still lack. The synthetic panel is tested on questions resolved after its models' training cutoffs, scored against the outcomes and against the human crowd's forecasts where those exist.
