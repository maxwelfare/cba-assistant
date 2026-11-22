# CBA 301: Practical Advice, its rules, and the literature behind them

Source: Richard Bruns, "CBA 301: Practical Advice", EA Forum, 7 February 2025, https://forum.effectivealtruism.org/posts/wsHnorrCFNffNJQmS/cba-301-practical-advice. Imported 2026-10-29 at his request [the owner's message of 2026-10-29]. The summary and the project implications are this session's reading. The literature section was compiled by a research agent (Claude Sonnet) from abstracts, publisher pages and the papers it could open; books were checked for existence only, and each entry says what was and was not read.

## Summary

A cost-benefit analysis is a public communication tool, built to help a decision-maker avoid surprises. Work in distributions from the first day; build the smallest concrete case first (one person, one event) and iterate; keep every number visible, cited and checkable, which for most audiences means a Google Sheet; cover every effect roughly before any effect rigorously; get real-world costs, mostly people's time, from the people who bear them; combine competing methods as a credence-weighted mixture, never an average; and stop refining when the next refinement is worth less to the client than it costs.

## The rules, the literature, and what each means here

Verdicts are the literature agent's, from the section below. "Here" is what the rule asks of this project's tools.

1. **A point estimate is always wrong.** Every input a distribution, every output an interval, from day one. Literature: strong (ISPOR-SMDM Task Force-6, Briggs et al. 2012; Doubilet et al. 1985; OMB A-4, 2003, the version in force after Executive Order 14192). The mean of a function is not the function of means (Jensen), so summaries are expected values from the draws. Here: the engine refuses a case run on point values except as a labelled example.
2. **Transparency; use Google Sheets.** Anyone numerate can check the work; no number hard-coded in a formula; every step labelled; every number cited with a link. Literature: transparency strong (Task Force-7, Eddy et al. 2012); the medium contested: spreadsheet errors are "common and non-trivial", and one inspector finds half or fewer of them (Panko 2000). Here: the sheet stays the face a client audits (roadmap item 3), and the Python twin with its row-by-row check is the second instrument that catches the errors Panko documents; case code holds no bare number, and a test refuses one.
3. **One individual, one event.** Estimate the smallest concrete unit, then aggregate through explicit, labelled stages. Literature: partial. Decomposition improves estimates of extreme and uncertain quantities and can worsen others (MacGregor and Armstrong 1994). Here: the case format has unit values and aggregation stages as separate, named steps, and the report leads with a per-unit result.
4. **Minimum viable analysis, then iterate.** A one-day version first, then narrow the intervals. Literature: supports (Phillips 1984, requisite models: "form and content ... sufficient to solve a particular problem"). Here: a case can run on wide judgement ranges from its first hour; each input records whether it is judgement, bounded by a reference class, or sourced.
5. **Deliver what the decision-maker needs; stop at the margin.** Refine until the value of the next refinement falls below its cost. Literature: strong (Claxton 1999; Felli and Hazen 1998, expected value of perfect information). Here: the engine reports the expected value of perfect information for each input or group, which is the stopping rule.
6. **Ruthlessly simplify the literature.** Take a wide interval and move on unless the input drives the result. Literature: supports (value-of-information logic; Saltelli et al. 2008, factor prioritisation). Here: research agents work the inputs in order of their share of output variance and of information value, never in order of appearance.
7. **Long-form NPV, and review every step.** Discount year by year until the arithmetic is intuitive; nest NPVs carefully (person, programme year, programme, research share); walk a second person through each step. Literature: review supported and sharpened (Panko 2000: single inspectors catch about half; group inspection about 80%); no study tests the by-hand method itself. Here: the engine's flows are per year, the report shows the year-by-year table, and the case's math gets more than one independent reader.
8. **Breadth beats rigour.** List every way the world changes from the baseline, bound each with napkin math, then research those whose intervals reach the largest values. Literature: the research-what-matters half is supported (value of information; Bojke et al. 2009 on omitted events as structural uncertainty); no source for napkin bounding as a stage. Here: a case's first version lists every effect with a rough interval before any is refined.
9. **Multiple specifications, combined as a mixture.** Report several methods; each Monte Carlo draw picks one by credence weight; never average their results. Literature: strong for structural uncertainty and model averaging (Bojke et al. 2009); the pooling literature agrees that no single combination rule is best everywhere (Clemen and Winkler 1999); no paper names the per-draw procedure, which is the linear opinion pool. Here: already in the engine's design (roadmap item 2).
10. **Become or hire a journalist.** Real costs come from key informants who do the work; bound their figure with a frictionless engineering estimate. Literature: the claim that ex-ante cost estimates run high is contested: total costs were overestimated in 14 of 28 rules but unit costs as often under as over (Harrington, Morgenstern and Nelson 2000); "a slight tendency to overestimate both costs and benefits" (Morgenstern 2018); the ratio exceeding one need not show bias (Simpson 2014). Here: an informant's figure enters as a source with the informant's role and stake recorded; the bias adjustment is a judgement, marked as one.
11. **Time costs usually dominate.** Elicit hours per task, then value them. Literature: "sometimes larger than direct medical costs" (Russell 2009), not "usually"; unpaid time is commonly valued at about half the after-tax wage (Whittington and Cook 2019), paid time at wage plus overhead (HHS ASPE 2017, multiplier not yet read). Here: the case format has a time-cost stream, and the valuation rule for each kind of time lives in `jurisdiction_guidance/` with its source.
12. **Analyses are worthless, analysing is everything.** Decision-makers want side effects, who is harmed and how hard they will fight. Literature: partial (OMB A-4 on who bears costs; Hahn and Tetlock 2008: "the relationship between analysis and policy decisions is tenuous"). Here: the report has a section on side effects, who bears costs, and who will resist.
13. **Ask for help.** Present the work to experienced practitioners. Literature: face validity by experts is part of model validation (Eddy et al. 2012); no empirical test of the practice. Here: a review by outside experts is a step before delivery.

Communicating intervals does not cost much trust: "only a small decrease in trust in numbers and trustworthiness of the source, and mostly for verbal uncertainty communication" (van der Bles et al. 2020, PNAS).

## Points from the post's comments

1. E[1/cost] differs from 1/E[cost] unless cost is nearly certain (Vasco Grilo); the mean of the draws handles it.
2. For some decisions the expected value is the output that matters; value of information, acceptability curves or the probability of a wrong decision can say more than an interval (Derek). The owner's reply: typical policy audiences collapse an expected value into a certain point, so show the interval.
3. froolow's review of GiveWell's model: models built by bright non-modellers tend toward cramped architecture, which is technical debt; uncertainty analysis is the largest omission in EA cost-effectiveness models.

---

## Literature, as verified

Method. Bibliographic data were checked against Crossref (all DOIs resolve to the stated title/venue/pages). Abstracts were taken from PubMed (E-utilities), Crossref, or the publisher/repository page. "Verbatim" = copied from an abstract or the paper text retrieved in this session. Where I could not retrieve primary text, the entry says so. Books were checked for existence (publisher, year, ISBN or DOI) and a catalogue/publisher description only; no page numbers are given and none should be cited without opening the book.

Verdict scale: supports / partly supports / contradicts.

---

### Rule 1. A point estimate is always wrong (distributions in, intervals out; Jensen)

1. Briggs AH, Weinstein MC, Fenwick EAL, Karnon J, Sculpher MJ, Paltiel AD (2012). Model parameter estimation and uncertainty: a report of the ISPOR-SMDM Modeling Good Research Practices Task Force-6. Value in Health 15(6):835-842. doi:10.1016/j.jval.2012.04.014 (also Med Decis Making 32(5):722-732). Verdict: SUPPORTS (strong; replaces the book-length Briggs-Claxton-Sculpher as the checkable source).
   "From a policy perspective, the value of a model-based analysis lies not simply in its ability to generate a precise point estimate for a specific outcome but also in the systematic examination and responsible reporting of uncertainty surrounding this outcome and the ultimate decision being addressed." (abstract, PubMed 22999133)

2. Doubilet P, Begg CB, Weinstein MC, Braun P, McNeil BJ (1985). Probabilistic sensitivity analysis using Monte Carlo simulation: a practical approach. Medical Decision Making 5(2):157-177. doi:10.1177/0272989X8500500205. Verdict: SUPPORTS (original method: every input a distribution, simulate).
   "The uncertainty in each probability and utility is assumed to possess a probability distribution." (abstract, PubMed 3831638)

3. OMB Circular A-4, Regulatory Analysis (17 Sept 2003). https://obamawhitehouse.archives.gov/omb/circulars_a004_a-4/ Verdict: SUPPORTS on uncertainty; PARTLY on Jensen (it asks for expected values, which is the Jensen-correct summary, not the mode of average inputs).
   "For major rules involving annual economic effects of $1 billion or more, you should present a formal quantitative analysis" [of uncertainties]; "These 'best estimates' are usually the average or the expected value of benefits and costs."; "combined in Monte Carlo simulations to derive a probability distribution of benefits and costs." (section Treatment of Uncertainty; fetched via page text, short quotes).
   STATUS (checked 2026-10-29): the 2023 revision (9 Nov 2023) was ordered revoked by Executive Order 14192 (31 Jan 2025): "The Director shall revoke OMB Circular No. A-4 of November 9, 2023 (Regulatory Analysis) ... and shall reinstate the prior version of Circular A-4, issued on September 17, 2003" (Presidential Documents, govinfo DCPD-202500205, section b). The whitehouse.gov circulars page lists only A-4 dated 09/17/2003. So cite the 2003 version. I could not retrieve the 2023 text, so I make no claim about what it said on probabilistic analysis.

Also kept, not independently verified beyond existence:
- Savage SL (2009). The Flaw of Averages: Why We Underestimate Risk in the Face of Uncertainty. Wiley. ISBN 978-0-471-38197-6. Verdict: SUPPORTS (popular book; publisher blurb: plans based on average assumptions are wrong "on average"). Cite as the name for the idea, not as evidence. Existence/ISBN confirmed (Open Library, library catalogues); blurb wording from a search summary, not read on the Wiley page.
- Briggs A, Claxton K, Sculpher M (2006). Decision Modelling for Health Economic Evaluation. Oxford University Press. doi:10.1093/oso/9780198526629.001.0001; ISBN 9780198526629. Verdict: SUPPORTS (standard text on probabilistic sensitivity analysis); content not read; prefer the Task Force-6 report above for a quotable sentence.
- Morgan MG, Henrion M (1990). Uncertainty: A Guide to Dealing with Uncertainty in Quantitative Risk and Policy Analysis. Cambridge University Press. doi:10.1017/CBO9780511840609; ISBN 978-0-521-36542-0. Verdict: SUPPORTS; contents list includes propagation of uncertainty and a final chapter "The value of knowing how little you know" (catalogue TOC). Not read.

4. Claxton K (2008). Exploring uncertainty in cost-effectiveness analysis. PharmacoEconomics 26(9):781-798. doi:10.2165/00019053-200826090-00008. Verdict: SUPPORTS (weakly quotable: abstract poses questions rather than asserting).
   "...should probabilistic sensitivity analysis continue to be recommended as a means to characterize parameter uncertainty..." (abstract, PubMed 18767898). Do not quote as a conclusion; it is a question the paper then answers in the text I did not read.

5. Jensen's inequality specifically: Simpson RD (2014/2015). Do regulators overestimate the costs of regulation? Journal of Benefit-Cost Analysis 5(2):315-332. doi:10.1515/jbca-2014-0027. Verdict: SUPPORTS the Jensen point in a CBA setting (see also rule 10, where it cuts against the "upward bias" claim).
   "Moreover, Jensen's inequality implies that the expected ratio of ex ante to ex post compliance costs would be greater than one." (abstract, Crossref)

### Rule 2. Transparency (shareable model, no hard-coded numbers, labelled steps, cited inputs)

1. Eddy DM, Hollingworth W, Caro JJ, Tsevat J, McDonald KM, Wong JB (2012). Model transparency and validation: a report of the ISPOR-SMDM Modeling Good Research Practices Task Force-7. Value in Health 15(6):843-850. doi:10.1016/j.jval.2012.04.012 (also Med Decis Making 32(5):733-743). Verdict: SUPPORTS (strong).
   "Technical documentation, written in sufficient detail to enable a reader with necessary expertise to evaluate the model and potentially reproduce it, should be made available openly or under agreements that protect intellectual property, at the discretion of the modelers." (abstract, PubMed 22999134)
2. Panko RR. What we know about spreadsheet errors. Journal of End User Computing 10(2):15-21 (1998). Existence per Panko's own note on a later version (not retrieved here). The text I did retrieve and quote is the extended version: Panko RR (2000). Spreadsheet errors: what we know. What we think we can do. Proc. EuSpRIG 2000; arXiv:0802.3457. Verdict: partly contradicts the choice of tool, supports the need for checks.
   "Fifteen years of research studies have concluded unanimously that spreadsheet errors are both common and non-trivial." (abstract) Also: field audits "found errors in 24% of the 367 spreadsheets audited" (text, section on Table 1). Note the popular "88%" figure is not in this paper's text; do not attribute it to it.
3. Counter-evidence on spreadsheets as the transparency medium: the same Panko paper and Herndon T, Ash M, Pollin R (2014). Does high public debt consistently stifle economic growth? A critique of Reinhart and Rogoff. Cambridge Journal of Economics 38(2):257-279. doi:10.1093/cje/bet075 (famous published result affected by a spreadsheet range error; I confirmed the citation and that it is a critique, but did not read the text, so the "spreadsheet error" detail is from general knowledge, not verified here). Also exists: Powell SG, Baker KR, Lawson B (2008). A critical review of the literature on spreadsheet errors. Decision Support Systems 46(1):128-138. doi:10.1016/j.dss.2008.06.001 (abstract not retrievable).

### Rule 3. One individual, one event; decompose before aggregating

1. MacGregor DG, Armstrong JS (1994). Judgmental decomposition: when does it work? International Journal of Forecasting 10(4):495-506. doi:10.1016/0169-2070(94)90018-3. Verdict: PARTLY SUPPORTS (this is the better and more honest source than the 1988 paper, because it states the limit).
   "As hypothesized, decomposition improved accuracy when the problem involved the estimation of extreme and uncertain values. Otherwise, decomposition often produced less accurate predictions." (abstract, from the authors' posted PDF at Wharton)
2. MacGregor DG, Lichtenstein S, Slovic P (1988). Structuring knowledge retrieval: an analysis of decomposed quantitative judgments. Organizational Behavior and Human Decision Processes 42(3):303-323. doi:10.1016/0749-5978(88)90003-9. Verdict: SUPPORTS, but I could not retrieve its abstract (ScienceDirect 403; Crossref, Semantic Scholar and RePEc have none). MacGregor & Armstrong (1994, introduction) describe it with Armstrong, Denniston & Gordon (1975) as having concluded "that decomposition would be especially effective for problems involving uncertain values" (retrieved text; sentence is cut off after "uncertain valu..." in my extract, so the wording is approximate). Cite only for existence and via the 1994 paper.
3. Armstrong JS, Denniston WB, Gordon MM (1975). The use of the decomposition principle in making judgments. Organizational Behavior and Human Performance 14(2):257-263. doi:10.1016/0030-5073(75)90028-8. Existence confirmed; abstract not read.
   Limit to state in onboarding: decomposition helps for extreme/uncertain quantities, not for quantities people already estimate well.

### Rule 4. Minimum viable analysis, then iterate

1. Phillips LD (1984). A theory of requisite decision models. Acta Psychologica 56(1-3):29-48. doi:10.1016/0001-6918(84)90005-2. Verdict: SUPPORTS (the model is grown iteratively until it is sufficient, not built to completion).
   "A requisite decision model is defined as a model whose form and content are sufficient to solve a particular problem." (abstract, LSE Research Online eprint 27250). The abstract also says the model is built interactively with the problem owners and is requisite once sensitivity analyses stop producing new intuitions (paraphrased by the retrieval tool; not copied verbatim).
2. Hubbard DW (2014, 3rd ed.). How to Measure Anything. Wiley. 1st ed. doi:10.1002/9781118983836 (2010). Verdict: PARTLY SUPPORTS (practitioner book; I saw only secondary summaries of its iterate-until-value-of-information-is-zero procedure; do not quote).

### Rule 5. Deliver what the decision-maker needs; stop when the marginal value of refinement < cost

1. Claxton K (1999). The irrelevance of inference: a decision-making approach to the stochastic evaluation of health care technologies. Journal of Health Economics 18(3):341-364. doi:10.1016/S0167-6296(98)00039-3. Verdict: SUPPORTS (strong; and it also supports using expected, not point-of-average, net benefit).
   "The distribution of net benefit is only relevant to deciding whether more information is required." and "This framework can distinguish ... deciding which alternatives should be chosen, given existing information, from the question of whether more information should be acquired." (abstract, PubMed 10537899)
2. Felli JC, Hazen GB (1998). Sensitivity analysis and the expected value of perfect information. Medical Decision Making 18(1):95-109. doi:10.1177/0272989X9801800117 (errata: 2001; 2003 23(1):97). Verdict: SUPPORTS.
   "EVPI, on the other hand, incorporates both the probability of a decision change and the marginal benefit of such a change into a single measure, and therefore provides a superior picture of problem sensitivity." (abstract, PubMed 9456214)
3. van der Bles AM, van der Linden S, Freeman ALJ, Mitchell J, Galvao AB, Zaval L, Spiegelhalter DJ (2019). Communicating uncertainty about facts, numbers and science. Royal Society Open Science 6(5):181870. doi:10.1098/rsos.181870 (author list beyond the first five from memory; check before citing). Verdict: partly supports (about presenting uncertainty to audiences; fits rule 1 and 12 more than 5).
   "While there is some evidence that communicating epistemic uncertainty does not necessarily affect audiences negatively, impact can vary between individuals and communication formats." (abstract, Crossref)

### Rule 6. Ruthlessly simplify the literature; wide interval unless a key driver

1. Felli & Hazen (1998), Claxton (1999) as above, plus Phillips (1984). Verdict: SUPPORTS the logic (research only where it can change the decision or the value of the output).
2. Briggs et al. 2012 (Task Force-6) abstract: "Expected value of perfect information is argued to be the most appropriate presentational technique, alongside cost-effectiveness acceptability curves, for representing decision uncertainty from probabilistic analysis." (PubMed 22999133). Verdict: SUPPORTS.
3. Saltelli A, Ratto M, Andres T, Campolongo F, Cariboni J, Gatelli D, Saisana M, Tarantola S (2008). Global Sensitivity Analysis: The Primer. Wiley. doi:10.1002/9780470725184. Verdict: SUPPORTS (the book names a "Factor Prioritization" setting, TOC 1.2.9, and asks which uncertain input "is more important in determining the uncertainty in the output"; wording from a search summary of the preface, not the book; not quoted verbatim).

### Rule 7. Long-form NPV by hand and independent review of every step

1. Panko (2000), EuSpRIG; arXiv:0802.3457 (see rule 2). Verdict: SUPPORTS review, and sharpens it: ONE reviewer is not enough.
   "individual code inspectors find only half or fewer of all errors, so group code inspection is necessary. Overall, group code inspection is an unpleasant medicine yet the only medicine that has been experimentally tested to date and found to be fairly effective, catching about 80% of all errors." (section on testing/code inspection). Also: "Teams of three or more are likely to be necessary."
   Implication for the rule: "a second person" is better than none but the evidence says it catches roughly half.
2. Hannay JE, Dybå T, Arisholm E, Sjøberg DIK (2009). The effectiveness of pair programming: a meta-analysis. Information and Software Technology 51(7):1110-1122. doi:10.1016/j.infsof.2009.02.001. Verdict: PARTLY SUPPORTS (pair programming is a different practice from independent review; effects are small).
   "a small significant positive overall effect of pair programming on quality", "a medium significant positive overall effect on duration", "a medium significant negative overall effect on effort" (abstract as quoted from the Durham EBSE bibliography page; the Elsevier page would not load). So pairing improves quality only slightly and costs effort; weak support for "every step". Suggest dropping it or citing it as a caution.
3. Doing the calculation by hand year by year: no study found testing this specifically. Treat as practitioner advice.

### Rule 8. Breadth beats rigour: list all changes from baseline, bound each, then research the largest

1. Felli & Hazen (1998), Saltelli et al. (2008), Claxton (1999): value-of-information and factor prioritisation logic (see rules 5, 6). Verdict: SUPPORTS the "research the ones that matter" half only.
2. Hubbard (2014): secondary summaries say it advises measuring only variables with high information value, and notes that analysts commonly spend effort on the wrong variables. Verdict: PARTLY SUPPORTS; unverified against the book.
3. Bojke et al. (2009) (rule 9) lists "inclusion of relevant events" and "inclusion of relevant comparators" as sources of structural uncertainty, which supports listing every channel: "Only parameterizing the uncertainty directly in the model can inform the decision to conduct further research to resolve this source of uncertainty." (abstract, PubMed 19508655).
   No source found for "napkin math bounds" as a method (Fermi estimation) in CBA specifically.

### Rule 9. Multiple specifications combined as a mixture drawn by credence

1. Bojke L, Claxton K, Sculpher M, Palmer S (2009). Characterizing structural uncertainty in decision analytic models: a review and application of methods. Value in Health 12(5):739-749. doi:10.1111/j.1524-4733.2008.00502.x. Verdict: SUPPORTS (strong).
   "Two methods to explicitly characterize such uncertainties were identified: model selection and model averaging." and "It is therefore important, for decision-making purposes, to incorporate such uncertainties into the modeling process." (abstract, PubMed 19508655)
2. Clemen RT, Winkler RL (1999). Combining probability distributions from experts in risk analysis. Risk Analysis 19(2):187-203. doi:10.1111/j.1539-6924.1999.tb00399.x. Verdict: PARTLY SUPPORTS (about combining experts' distributions, which is the linear opinion pool = mixture; the abstract does not name the linear pool, and it says no combination method is best everywhere).
   "no single process is best in all circumstances." (abstract, Crossref)
3. Simonsohn U, Simmons JP, Nelson LD (2020). Specification curve analysis. Nature Human Behaviour 4(11):1208-1214. doi:10.1038/s41562-020-0912-z. Verdict: SUPPORTS reporting all defensible specifications; it does NOT propose a credence-weighted mixture (it does joint inference across specifications).
   "Empirical results hinge on analytical decisions that are defensible, arbitrary and motivated." (abstract, PubMed 32719546)
   Alternative with similar scope: Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W (2016). Increasing transparency through a multiverse analysis. Perspectives on Psychological Science 11(5):702-712. doi:10.1177/1745691616658637.
4. Leamer EE (1983). Let's take the con out of econometrics. American Economic Review 73(1):31-43. Verdict: PARTLY SUPPORTS (argues for reporting sensitivity to specification; the abstract could not be retrieved, so the characterisation rests on secondary descriptions, e.g. Angrist & Pischke 2010 as quoted by a search summary). Citation details (73(1), 31-43) were confirmed from secondary pages, not from a DOI lookup (the DOI I tried did not resolve in Crossref).
   Not found: any paper that prescribes "draw one method per Monte Carlo iteration by credence weight" under that name. It is the standard linear opinion pool/model averaging; cite Bojke (averaging) plus Clemen & Winkler (pooling). The statement "never average point results" is the mixture-versus-mean distinction, which follows from the same Jensen logic as rule 1.

### Rule 10. Key informants for real-world cost; ex-ante cost estimates exceed ex-post; bound with a frictionless engineering estimate

1. Marshall MN (1996). The key informant technique. Family Practice 13(1):92-97. doi:10.1093/fampra/13.1.92. Verdict: PARTLY SUPPORTS (describes the method for health research; says nothing about costs).
   "This article considers the role of the key informant technique as a qualitative research method and examines the potential contribution of the approach to health care research." (abstract, PubMed 8671109)
2. Harrington W, Morgenstern RD, Nelson P (2000). On the accuracy of regulatory cost estimates. Journal of Policy Analysis and Management 19(2):297-322. doi:10.1002/(SICI)1520-6688(200021)19:2<297::AID-PAM7>3.0.CO;2-X. Verdict: PARTLY SUPPORTS (total costs usually overestimated; unit costs not).
   "the costs of regulations tend to be overestimated" [for total costs; true for 14 of the 28 rules, ex ante too low for 3]; "unit cost estimates are often accurate, and even when they are not, overestimation ... occurs about as often as underestimation" (abstract, as retrieved from the RePEc listing; quotes are short fragments, the rest paraphrased). The authors attribute the gap to errors in the quantity (effect of the rule), which is relevant to the rule's "bound with an engineering estimate".
3. Morgenstern RD (2018). Retrospective analysis of U.S. federal environmental regulation. Journal of Benefit-Cost Analysis 9(2):285-304. doi:10.1017/bca.2017.17. Verdict: PARTLY SUPPORTS, weaker than the rule.
   "the results suggest a slight tendency to overestimate both costs and benefits (or effectiveness) of regulation." (abstract, Crossref)
4. Fraas A, Kopits E, Wolverton A (2023). A review of retrospective cost analyses. Review of Environmental Economics and Policy 17(1):22-42. doi:10.1086/723595. Verdict: PARTLY SUPPORTS. Abstract not retrieved verbatim; a search summary says the main causes of ex ante/ex post gaps are inaccurate baseline assumptions and too little allowance for technological innovation. Do not quote.
COUNTER-EVIDENCE (rule 10):
- Simpson RD (2014/2015), JBCA 5(2):315-332, doi:10.1515/jbca-2014-0027. Verdict: CONTRADICTS the "ex-ante exceeds ex-post is a bias" reading. "I argue that neither the greater frequency of overestimates nor the fact that the average ratio of ex ante to ex post cost estimates is greater than one necessarily demonstrates that ex ante estimates are biased." and "I propose a regression-based test of the bias of ex ante compliance cost estimates, and cannot reject the hypothesis that estimates are unbiased." (abstract, Crossref). He adds that failing to reject with noisy data is not strong evidence either way.
- Kopits E et al. (2014), JBCA 5(2):173-193, doi:10.1515/jbca-2014-0024: a framework paper, no verdict on bias ("to see if judgments can be made about why and how ex ante and ex post estimates differ").
No source found for the "frictionless engineering estimate" bound. Treat as the author's own heuristic.

### Rule 11. Time costs dominate health-policy social cost; elicit time per task x wage plus overhead

1. Russell LB (2009). Completing costs: patients' time. Medical Care 47(7 Suppl 1):S89-S93. doi:10.1097/MLR.0b013e31819bc077. Verdict: SUPPORTS (strong for "can dominate"; says "sometimes", not "usually").
   "Studies of cancer care, smoking cessation, and diabetes self-management show that it can be a large part of an intervention's costs, sometimes larger than direct medical costs" and "Ignoring patients' time underestimates disease burden and biases cost-effectiveness results toward interventions that use more time." (abstract, PubMed 19536025)
2. Yabroff KR, Davis WW, Lamont EB, et al. (2007). Patient time costs associated with cancer care. Journal of the National Cancer Institute 99(1):14-23. doi:10.1093/jnci/djk001. Verdict: SUPPORTS the method.
   "For each service category, time estimates were combined with service frequency and an hourly value of patient time." (abstract, PubMed 17202109)
3. Whittington D, Cook J (2019; online Dec 2018). Valuing changes in time use in low- and middle-income countries. Journal of Benefit-Cost Analysis 10(S1):51-72. doi:10.1017/bca.2018.21. Verdict: PARTLY SUPPORTS; NOTE the title differs from the candidate list (the candidate said "valuing time use"). It reviews the valuation of unpaid time, not wage plus overhead.
   "...find support for a commonly used benchmark of 50% of after-tax wages for time changes in activities in the informal sector..." (abstract, Crossref). So "wage" is not the universal answer; unpaid time is valued at a fraction.
4. HHS ASPE (2017). Valuing time in U.S. Department of Health and Human Services regulatory impact analyses: conceptual framework and best practices. https://aspe.hhs.gov/reports/valuing-time-us-department-health-human-services-regulatory-impact-analyses-conceptual-framework . Verdict: PARTLY SUPPORTS; official guidance. Verbatim: "we focus largely on valuing time used for administrative and other activities." and that indirect costs include "overhead costs such as space rental and utilities." I did not retrieve its specific rule on wage-plus-overhead multipliers; open it before citing a multiplier.
5. OMB Circular A-4 (2003): the retrieved page text has no discussion of the opportunity cost of time (searched in the first 100,000 characters of the page; the rest was read only for the uncertainty section). Do not cite A-4 for rule 11.

### Rule 12. The analysing matters more than the number: side effects, who is harmed, resistance

1. OMB Circular A-4 (2003), distribution section. Verdict: SUPPORTS who-bears-the-cost.
   "Those who bear the costs of a regulation and those who enjoy its benefits often are not the same people." (A-4, distributional effects section)
2. Hahn RW, Tetlock PC (2008). Has economic analysis improved regulatory decisions? Journal of Economic Perspectives 22(1):67-84. doi:10.1257/jep.22.1.67. Verdict: PARTLY SUPPORTS (shows analysis often does not drive decisions, so the rule's "decision-makers want other things" has some backing; it does not say the process matters more than the number).
   "...the quality of analysis in the U.S. and European Union frequently fails to meet widely accepted guidelines. Furthermore, the relationship between analysis and policy decisions is tenuous." (abstract, Crossref)
3. Sunstein CR (2018). The Cost-Benefit Revolution. MIT Press. doi:10.7551/mitpress/11571.001.0001; ISBN 9780262038140. Verdict: WEAK. Publisher blurb (secondary) says officials often lack information on costs and benefits and that the book covers how to gather it; I found no passage on the process mattering more than the number or on resistance. Not recommended for rule 12.
4. Boardman AE, Greenberg DH, Vining AR, Weimer DL (2018). Cost-Benefit Analysis: Concepts and Practice, 5th ed. Cambridge University Press. doi:10.1017/9781108235594; ISBN 9781108401296 (paperback). Verdict: SUPPORTS for sensitivity analysis/Monte Carlo and stakeholder analysis in general, based on the publisher description only; I could not see the table of contents, so no chapter citations. Check before citing.

### Rule 13. Ask experienced practitioners

1. Eddy et al. (2012) as above. Verdict: SUPPORTS: validation includes "face validity (wherein experts evaluate model structure, data sources, assumptions, and results)". (abstract, PubMed 22999134)
2. Phillips (1984): requisite models are built in consultation between problem owners and specialists (abstract, paraphrased).
3. Panko (2000): independent inspection by several people (rule 7) is the one tested error-reduction method.
No dedicated study of "present to practitioners" as a technique was found.

### Rule 1/5 (communication): van der Bles et al. (2020)

van der Bles AM, van der Linden S, Freeman ALJ, Spiegelhalter DJ (2020). The effects of communicating uncertainty on public trust in facts and numbers. PNAS 117(14):7672-7683. doi:10.1073/pnas.1913678117. Verdict: SUPPORTS reporting intervals (counter to the fear that it costs credibility).
"...we observed only a small decrease in trust in numbers and trustworthiness of the source, and mostly for verbal uncertainty communication." (abstract, Crossref). Use this instead of the 2019 paper when the claim is about trust. Note the preprint (PsyArXiv 10.31234/osf.io/vbtg3) is the same work; cite the PNAS version.

---

### Rejected or demoted candidates

- Sunstein (2018) for rule 12: no verified passage fits; demoted to "weak". Hahn & Tetlock (2008) and A-4 used instead.
- Hannay et al. (2009) for rule 7: it is about pair programming (joint authorship), shows only a small quality effect and a medium effort cost. Kept only as a caution. Panko (2000) is the better source.
- Leamer (1983) as a basis for the mixture method in rule 9: argues for specification sensitivity, not for credence-weighted mixtures. Kept as background only; abstract not retrieved.
- Simonsohn et al. (2020) for rule 9: shows many specifications and joint inference, not a mixture. Partial.
- Marshall (1996) for rule 10: a general qualitative-methods paper; no content on cost estimation. Weak.
- Claxton (2008) as a quotable support for rule 1: abstract only poses questions. Use Briggs et al. (2012) Task Force-6 for the quote.
- OMB A-4 2023 revision: ordered revoked by EO 14192; 2003 text is posted. I could not retrieve the 2023 text, so it is not cited.
- Panko 1998 JEUC: text not retrieved; the 2000 EuSpRIG paper (arXiv:0802.3457) was read and is cited. The widely quoted "88% of spreadsheets" is not in that paper.
- Whittington & Cook: the title in the candidate list was loose; the correct title is above, and it supports 50% of wage for unpaid time, not "wage plus overhead".
- Jensen/"E[1/cost] != 1/E[cost]": no source in the CBA literature phrased this way was found other than Simpson (2014) (ratio of ex ante to ex post) and general mathematics. Cite the inequality itself to a statistics text.

### Gaps (no good source found)

- Rule 7: that doing NPV "by hand year by year" reduces errors.
- Rule 8: napkin-math bounding as a stage before research.
- Rule 10: frictionless engineering estimate as a bound.
- Rule 11: "usually dominate" (Russell says "sometimes"), and wage-plus-overhead multiplier (HHS report not fully read).
- Rule 13: no empirical test.

### Not verified by me

Savage (2009), Briggs et al. (2006), Morgan & Henrion (1990), Saltelli et al. (2008), Boardman et al. (2018), Sunstein (2018), Hubbard (2014): existence and publisher data confirmed, content not read. MacGregor, Lichtenstein & Slovic (1988), Phillips (1984) and Leamer (1983): abstract not retrievable from the publisher; Phillips from LSE repository (paraphrase plus one verbatim sentence), Leamer from secondary sources.
