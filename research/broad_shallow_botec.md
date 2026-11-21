# Broad but shallow: Fermi estimates, effect inventories and simple models

Written 2026-11-10 for the redesign of how a case is built. The owner's words (2026-11-10): every analysis "should start with subagents listing all the good and bad effects of the policy. Then the author does a BOTEC fermi-style estimate for all of those ... No Python code is allowed to be written at this stage"; "simplicity does not mean leaving things out. I want a 'broad but shallow' approach"; the few effects then modelled get "maybe half a dozen inputs each, and math that could fit on one spreadsheet tab"; "complexity is slop".

How to read this note. A key in square brackets is the entry in `research/refs.toml` (or the shared `library/refs.toml`). A quote in quotation marks was read in the stored text at `research/sources/<key>/text.txt` and machine-checked against it; the page is the printed page of the source where the text shows one, else the section. A claim marked "recalled" comes from memory or from a summarising fetch and has no stored text; it must be checked before a brief rests on it. Where the note departs from the owner's words, section 5 says so.

## 1. Fermi estimation and its patterns of thought

### 1.1 What the sources are

1.1.1 Mahajan's two books teach the tools by name and by worked case. `Street-Fighting Mathematics` has the tools dimensions, easy cases, lumping, pictures, taking out the big part, and reasoning by analogy [mahajan_2010_street_fighting]. `The Art of Insight` has divide and conquer, abstraction, symmetry and conservation, proportional reasoning, dimensions, lumping, probabilistic reasoning, easy cases, and spring models [mahajan_2014_art_of_insight]. Both were read in the stored full text (the OCW file of the first is headed "draft text" but carries the 2010 MIT Press title page).

1.1.2 MacKay's `Sustainable Energy - without the hot air` is the exemplar of an entire policy field done by rough multiplied numbers, and it says so in its first chapter [mackay_2009_without_hot_air].

1.1.3 Tetlock and Gardner, `Superforecasting` (Crown 2015), chapter 5, is the source for "Fermi-izing" as a forecasting habit. No free copy exists; it is recalled, not read [tetlock_2015_superforecasting]. What is recalled: the authors name Enrico Fermi's school-of-hard-knocks questions (piano tuners in Chicago) and say the superforecasters break a question into sub-questions, separate what is known from what is not, and take the outside view (the base rate for the reference class) before the inside view.

### 1.2 The reasoning tools, one rule and one example each

Each line is a rule an agent can be told, with a case from the sources.

1.2.1 Divide and conquer. Replace one quantity you know badly by a product of quantities you know better. Example: the volume of a dollar bill is hard to guess, the width "probably lies between 10 and 20 centimeters—a range of only a factor of 2" against the volume range: "This range is wide, spanning a factor of 100", so estimate width, height and thickness (15 cm x 6 cm x 0.01 cm = 1 cm3) [mahajan_2014_art_of_insight, 1.1, p. 4]. The book calls this its first tool: "Break hard problems into manageable pieces" [mahajan_2014_art_of_insight, ch. 1 opening, p. 3].

1.2.2 Draw the tree. Write the decomposition as a tree so the structure is visible at a glance. Example: the capacity of a train line against a road. "The sequential presentation hides the structure ... A tree representation shows us the analysis in one glance" [mahajan_2014_art_of_insight, 1.3, pp. 7-8].

1.2.3 Estimate from the demand side as well as the supply side. Reach a quantity by a second route that uses unrelated knowledge. Example: Mahajan's section 1.4 estimates by what people use, not only by what is built (recalled from the section heading "Demand-side estimates"; the body was not quoted). The repository's own rule for independent methods is the same idea.

1.2.4 Use a second method on every important quantity. "Reliability, in short, comes from intelligent redundancy"; use several methods "as different from one another as possible--for example, by using unrelated background knowledge" [mahajan_2014_art_of_insight, 1.5, pp. 16-17]. "mindless redundancy offers little protection": a second pass by the same method repeats the same mistakes. This is the support in the literature for owner rule 9 in `notes/owner_cba_rules.md`.

1.2.5 Talk to your gut for a range, then check it. Give a lower and an upper end that would each be a mild surprise to find exceeded, and call it about a 2/3 interval. Mahajan's worked case: "My gut chose the range for which I would feel mild surprise, but not shock, to learn that the area lies outside it" [mahajan_2014_art_of_insight, 7.2.1, p. 239]. The "mugger" device is for courage: "I often imagine a mugger who holds a knife at my ribs, demanding, 'Your guess or your life!'" [mahajan_2014_art_of_insight, 1.1, p. 3].

1.2.6 Lumping. Replace a varied set by one typical member and multiply by the count. Example: "Taking Massachusetts as a typical state, the US population is roughly 50 × 6 million or 300 million" against a true 314 million [mahajan_2014_art_of_insight, 6.3.1]. In Mahajan's words, "Lumping helps us find, or create, a quantity that does not change" and so "We’ve lumped away all the change—throwing away information in exchange for insight" The cost to watch: the typical member must not be biased.

1.2.7 Round on a logarithmic scale. Round each number to one significant figure, or to a power of ten and a factor of 3, and do the sums in your head. "The antidote is to do the computations ourselves, but approximately--by placing quantities on a logarithmic scale and rounding them to the nearest convenient value" [mahajan_2014_art_of_insight, 6.2]. MacKay does the same by policy: "by rounding the numbers, we can make them easier to remember. Second, rounded numbers allow quick calculations" [mackay_2009_without_hot_air, ch. 1].

1.2.8 Taking out the big part. Find the largest effect first, get it roughly right, and refine afterwards. "First approximate and understand the most important effect--the big part--then refine your analysis and understanding" [mahajan_2010_street_fighting, ch. 5 opening]. In an uncertain product the big part is the factor with the widest range (see 1.5.3).

1.2.9 Easy cases. Check the estimate at limits where the answer is obvious. "A correct solution works in all cases, including the easy ones" [mahajan_2010_street_fighting, ch. 2 opening]. Example for a cost-benefit estimate: with zero uptake the benefit must be zero; with everyone treated it must equal the whole eligible pool's gain.

1.2.10 Dimensions. Every term added must have the same units, and every comparison must be of like with like. Mahajan's economic example: Nigeria's GDP "would be roughly $1 trillion per decade" or "$2 billion per week" depending on the unit of time, and "A valid economic argument cannot reach a conclusion that depends on the astronomical phenomenon chosen to measure time. The mistake lies in comparing incomparable quantities. Net worth is an amount" [mahajan_2010_street_fighting, 1.1]. For a case: a stock (a count of people) is never added to a flow (people per year), and a rate is never compared to a total.

1.2.11 Proportional reasoning. Look at ratios and at what stays constant. "When there is change, look for what does not change" and "Using intensive quantities for the independent variables usually leads to more insightful results than using extensive quantities does" [mahajan_2014_art_of_insight, ch. 4 opening]. Example: use cases per 1,000 people (intensive) rather than total cases (extensive) when carrying a rate from one country to another.

1.2.12 Symmetry and conservation. Find what cannot change and let it fix the answer. Example: the mouse-eaten chessboard, where the difference between empty black and white squares cannot change [mahajan_2014_art_of_insight, ch. 3, 3.1.2]. For an effect list: money paid is money received, so a transfer is a cost to one party and an equal gain to another; it nets to zero in the total and matters for who bears it.

1.2.13 Bound it from above and below. Estimate the most the quantity could be and the least, and use the bound when it settles the question. MacKay's method for biomass power: all uses pass "the first staging post", so "the power at the first staging post is an upper bound on the power available from all plant-based power solutions" [mackay_2009_without_hot_air, ch. 6, p. 38 ff.]. He also states the purpose: "quick rough estimates of the maximum plausible powers that each of these routes could deliver" and neglects costs on the first pass. An effect whose upper bound is far below the largest effect may be dropped with the bound written down.

1.2.14 Make everything a number, in a common unit. MacKay's chapter 1 headline is "Numbers, not adjectives", and every source of energy is turned into kilowatt-hours per day per person so they can be compared [mackay_2009_without_hot_air, ch. 1]. For a case: one currency or one health unit across all effects.

1.2.15 Use everyday knowledge before statistics. "I like to base my calculations on everyday knowledge rather than on trawling through impersonal national statistics ... I back up these everyday estimates with other peoples' calculations and with official statistics" [mackay_2009_without_hot_air, ch. 1]. The order is: guess first, then check against a stored source.

1.2.16 Reference class (outside view). Start from the base rate for comparable cases before the details of this one. The inside view is the trap: "Overly optimistic forecasts result from the adoption of an inside view of the problem, which anchors predictions on plans and scenarios" [kahneman_1993_timid, abstract]; the method is named by Flyvbjerg, "reference class forecasting ... basing forecasts on actual performance in a reference class of comparable projects" [flyvbjerg_2006_nobel, abstract]. Both were read as abstracts only. Tetlock and Gardner recommend the same order [tetlock_2015_superforecasting, recalled].

1.2.17 Keep the sum of the pieces honest. After the product, divide back: does the answer, per head, per year, per dollar, look sane? MacKay does it throughout: from 34 billion tons of CO2-equivalent a year and 6 billion people, "we can instantly note, without a calculator, that the average emissions per person are 5 or 6 tons" [mackay_2009_without_hot_air, ch. 1]. This is a sanity check by a ratio the reader already knows.

1.2.18 Say what the symbol claims. Mahajan marks accuracy with different equality signs: equal, approximately equal, proportional. An estimate carries "approximately" in its form [mahajan_2014_art_of_insight, 1.1, p. 5]. For agents: every line of a BOTEC says what it leaves out.

### 1.3 Why a product of rough factors is less wrong than it looks

1.3.1 The worry. If each of ten factors is uncertain by a factor of 2 either way, the naive range for the product is the widest possible. Mahajan: that a range spanning a factor of 4 for each of ten factors would give a product spanning 4^10, about a million: "That conclusion is terribly pessimistic. More likely, several of the ten estimates will be too large and several will be too small, allowing many errors to cancel" [mahajan_2014_art_of_insight, 7.2.2, p. 242]. His title for the section is "Plausible ranges: Why divide and conquer works" (7.2, pp. 239-244).

1.3.2 The remedy, in his words. Take each factor as log-normal: "on a logarithmic scale, the probability distribution is a normal distribution". "The midpoint is the geometric mean of the two endpoints, and the width is the square root of the ratio between the upper and lower endpoints" [mahajan_2014_art_of_insight, 7.2.2, p. 242]. Two reasons given: "our mental hardware compares quantities using ratio rather than absolute difference", and "normal distributions combine simply".

1.3.3 The rule for a product's range. "The midpoint of the plausible range for the area A is the product of the midpoint of the plausible ranges for h and w." Then, in decibels or any logarithmic unit, the half width of the product's range "is the Pythagorean sum of the individual half widths" [mahajan_2014_art_of_insight, 7.2.2, pp. 243-244]. In symbols: if the range of factor i is give-or-take a factor f_i, the product's range is give-or-take a factor F, with ln F = sqrt( (ln f_1)^2 + (ln f_2)^2 + ... ). The same holds for a quotient, since a divisor's log enters with a sign and squares to the same number. His check: heights give or take a factor of 1.2, widths 1.3, area 250,000 km2 give or take a factor of 1.37 (his text rounds this to 1.4) against 2.4 by multiplying the endpoints.

1.3.4 Conditions. The rule needs the factors to be independent and each range to have the same coverage (all 2/3 intervals, or all 90% intervals). Positive links between factors do not cancel: for perfectly correlated factors the logs add in a straight line (ln F = sum of ln f_i), which is the naive result. This last point is derived from the algebra of variances, not quoted. Mahajan's own caveat on the log-normal: "the tails of the normal distribution are too thin, reflecting an unrealistically high confidence that our estimate does not contain a huge error ... we will concern ourselves with the location and width of the central region" [mahajan_2014_art_of_insight, 7.2.2, p. 243]. Hubris in ranges is the main risk: people's stated intervals are usually too narrow (calibration research, for example Soll and Klayman 2004; recalled) [soll_2004_overconfidence].

1.3.5 Why the log-normal is not an arbitrary choice. Multiplicative causes give a log-normal by the same central-limit argument that additive causes give a normal. Limpert and Stahel: "Multiplicative causes are by far more important than additive ones, in general, and benefit from a multiplicative (or log-) normal approach"; the variation is written as the geometric mean times-divide s* (x/s*), with an interval from mean divided by s* to mean times s* containing "2/3 of the data" [limpert_2011_normal_problems, abstract and Methods]. The Dissolving-the-Fermi-paradox paper (Sandberg, Drexler and Ord 2018, recalled) applies the same point to a famous Fermi product, the Drake equation: point estimates of each factor hide a product distribution so wide that it is consistent with an empty galaxy [sandberg_2018_fermi_paradox].

### 1.4 How Squiggle and Guesstimate show a Fermi model with ranges

1.4.1 Squiggle (Quantified Uncertainty Research Institute) is "a minimalist programming language for probabilistic estimation ... meant for intuitively-driven quantitative estimation instead of data analysis or data-driven statistical techniques", and its opening example is the Fermi problem of the piano tuners of New York City [squiggle_docs, Introduction]. A range is written `to(low, high)`: "The 'to' function is a shorthand for lognormal({p5:min, p95:max}). It does not accept values of 0 or less, as those are not valid for lognormal distributions" [squiggle_docs, Dist API]. So a Squiggle range is a 90% interval of a log-normal, which is exactly the object in 1.3, with the 90% coverage in place of Mahajan's 2/3. The product of two such ranges is a sample-based multiplication.

1.4.2 Guesstimate (Ozzie Gooen, 2015) is a spreadsheet-like web app in which each cell holds a range and is multiplied through by Monte Carlo sampling. Its authors recommend the log-normal for positive quantities and the normal when the range includes zero or negatives. This is recalled from the Guesstimate blog posts "Lognormal > Normal" and "Guesstimate with Different Distributions" (the pages were behind a bot wall; only search summaries were seen) [gooen_2015_guesstimate].

1.4.3 What a hand BOTEC can borrow from both: write each range as a low-high pair at one stated coverage, treat it as log-normal, and show the product's range beside the product's median. The sampling is the part a human leaves out (section 1.5).

### 1.5 Can a person do the range arithmetic by hand?

1.5.1 Yes, for a product or quotient of a handful of factors, with one table of logs. Mahajan does it with decibels because a factor f is 10 log10 f decibels: "a factor of 3 is close to 5 decibels ... and a factor of 2 is almost exactly 3 decibels" [mahajan_2014_art_of_insight, 7.2.2, p. 243]. Then add the squares, take the square root, and convert back.

1.5.2 Worked example. Estimate the yearly benefit of a hypothetical programme as people reached, times the share who gain, times the value of a gain. Each factor is given as a median and a 90% interval written as "give or take a factor".

| Factor | Median | 90% interval | f (give or take) | ln f | (ln f)^2 |
|---|---|---|---|---|---|
| People reached | 25 million | 21 to 30 million | 1.2 | 0.182 | 0.033 |
| Share who gain | 4% | 2% to 8% | 2 | 0.693 | 0.480 |
| Value per gain | $3,000 | $1,000 to $9,000 | 3 | 1.099 | 1.207 |
| Sum of squares | | | | | 1.720 |

1.5.2.1 Median of the product: 25 million x 0.04 x $3,000 = $3.0 billion a year.
1.5.2.2 Spread: sqrt(1.720) = 1.31, and e^1.31 = 3.7. The 90% interval of the product is $3.0 billion divided and multiplied by 3.7: about $0.8 billion to $11 billion.
1.5.2.3 In decibels, by hand: 0.8, 3.0 and 4.8 dB; squares 0.6, 9.0 and 23.0, sum 32.7; square root 5.7 dB; 10 to the 0.57 is 3.7. The same answer, with a slide rule's effort.
1.5.2.4 The naive endpoint product gives 1.2 x 2 x 3 = 7.2, so $0.4 billion to $22 billion, an interval twice as wide on the log scale. The quadrature rule is what the claim that errors partly cancel in 1.3.1 amounts to in numbers.
1.5.2.5 Which factor matters. Shares of the log-variance are 2% (people), 28% (share), and 70% (value per gain). Narrowing the value per gain is worth far more than narrowing the first two: this is "taking out the big part" (1.2.8) applied to uncertainty, and it tells the agent where to spend a second method.
1.5.2.6 The mean differs from the median. For a log-normal with log standard deviation s, the mean is the median times e^(s^2/2). Here a 90% interval factor of 3.7 means s = 1.31/1.645 = 0.80, so the mean is $3.0 billion x 1.37, about $4.1 billion. A cost-benefit analysis reports expected values, so the BOTEC must show both median and mean. If the same three factors had been 2/3 intervals the spread would be the same but s = 1.31 and the mean would be 2.4 times the median, $7.1 billion: the coverage convention changes the mean, so every range states its coverage. All arithmetic in 1.5.2 was checked in Python by this note's author as arithmetic only; the BOTEC itself uses no code.

1.5.3 Limits of hand arithmetic. A sum or difference of uncertain terms is not handled by quadrature in logs; two terms can be added by adding the medians and combining absolute half-widths in quadrature (a normal approximation) if neither range is wide. When a term can be negative or a factor is a probability that can be near zero, a hand rule fails; those are the cases for the half-dozen-input model of section 3, with sampling. Correlation between factors (1.3.4) must be named by the author, and a safe default is to say which pairs move together and to treat them as one factor.

1.5.4 A product with a probability factor. An event with chance p and size X contributes p x X; give p as a range of odds (a factor on p/(1-p)) when it is far from 1/2. For a rare event the range on p usually dominates (Pindyck's catastrophe example in 3.4.2 is this form).

## 2. Listing all the effects before estimating any

### 2.1 What the literature asks for

2.1.1 Second Panel on Cost-Effectiveness in Health and Medicine (Sanders et al. 2016, JAMA 316:1093). The impact inventory is "a structured table that contains consequences (both inside and outside the formal health care sector), intended to clarify the scope and boundaries of the 2 reference case analyses" [sanders_2016_recommendations, abstract]. Its purpose: "to ensure that all consequences, including those outside the formal health care sector, are considered regularly and comprehensively, which has generally not been the case to date" [sanders_2016_recommendations, Recommendation 3]. The template's rows are sectors (formal health care, informal health care, labor-market productivity, consumption, social services, legal and criminal justice, education, housing, environment, other) crossed with the type of impact, a column for whether it is included, and a column for the source of evidence [sanders_2016_recommendations, Figure 1]. The panel then asks that the analyst "attempt to quantify and value nonhealth consequences in the impact inventory unless those consequences are likely to have a negligible effect on the result of the analysis" [sanders_2016_recommendations, Recommendation 3B]. That is the broad-but-shallow rule in a regulatory form: list everything, quantify everything not negligible.

2.1.2 Boardman, Greenberg, Vining and Weimer, `Cost-Benefit Analysis: Concepts and Practice` (5th ed. 2018): the standard nine-step list includes deciding whose benefits and costs have standing, then identifying the impact categories, cataloguing the impacts and choosing a measurement indicator for each, before predicting them quantitatively, monetising, discounting and summing [boardman_2018_cost]. Recalled, not opened (paywalled); the step wording and the numbering must be checked in the text before a brief cites them. The distinction it supports is: first decide who counts, then what happens to each of them.

2.1.3 HM Treasury Green Book (2026 edition; the 2022 edition is withdrawn, see the shared entry). Proportion: "Green Book guidance should be used proportionately. Business cases should contain sufficient detail to support sound decision making, but they should not take up more time and resources than is necessary" (1.8). On monetising: "It may be disproportionate to monetise or quantify every impact. Practitioners should focus on monetising those social costs and social benefits that are likely to be most decisive in distinguishing between options" (6.29). For what is left unmonetised: "Practitioners might estimate the monetary value that an unmonetisable benefit would need to be for the proposal's NPSV to be greater than zero. They should then explain whether this value is likely or unlikely, based on past evidence" (6.104), a switching value. [hm_treasury_2026_green_book]

2.1.4 What the three agree on: list widely, quantify in proportion, keep a record of what was listed and not quantified, and say how large an unquantified item would have to be to matter.

### 2.2 Methods that make a list complete

2.2.1 Independent brainstorming before pooling: the nominal group technique (Delbecq and Van de Ven 1971, "A group process model for problem identification and program planning", J. Applied Behavioral Science 7:466-492). Recalled [delbecq_1971_group_process]. The steps: each member writes ideas silently and alone, ideas are collected round by round without debate, the list is clarified, then members rank or vote. Adds: no member anchors the others, and the list is longer than a talking group's (Diehl and Stroebe 1987, stored in full by an earlier seat: "production blocking accounted for most of the productivity loss of real brainstorming groups" [diehl_1987_productivity], read from its entry). Costs: one run per member. For agents the cost is one subagent run each, whose cost is in dollars, not people's hours; the benefit holds only if the subagents are not given each other's output, and only if their prompts differ enough that they do not make the same list (different stakeholder or different time horizon per run, see 2.2.5).

2.2.2 The futures wheel (Glenn). "The Futures Wheel is a method for identifying and packaging primary, secondary, and tertiary consequences of trends, events, emerging issues, and future possible decisions" and is "a kind of structured brainstorming" in which the event is written in the middle, first-order impacts on spokes, and "the secondary impacts of each primary impact form a second ring of the wheel. This ripple effect continues until a useful picture of the implications of the event or trend is clear" [glenn_2009_futures_wheel, I and II]. The chapter dates the invention to 1971, with workshops from the early 1970s (the brief's "Glenn 1972" is not supported by the text read). Adds: second- and third-order effects, which a first-pass list misses, and feedback loops (the chapter says the higher-order consequences can show positive and negative loops). Costs: it grows without bound unless trimmed; the chapter itself gives a trimming rule, the "rule of unanimity" (an impact enters only if all agree it is plausible) and warns that the process "leads rapidly to unexpected consequences and, thus, requires a restriction on the group to prevent them from arriving at conclusions that are so speculative as to be of little worth." A cap of two rings, with each ring's items tested against the plausibility test, is the form to prompt.

2.2.3 The premortem (Klein 2007, "Performing a project premortem", Harvard Business Review 85(9):18-19). Imagine the policy has already failed, and each person writes why. Recalled [klein_2007_premortem]. Adds: bad effects and failure routes, which an ordinary list under-supplies because the planners are committed to success. The base of the claim, prospective hindsight, is from Mitchell, Russo and Pennington 1989 (recalled, not entered). Cost: one run in the opposite frame; little else. In the repository `standards/process/peer_review.md` already uses the idea; its status there is "recalled, not opened" too.

2.2.4 Stakeholder-by-stakeholder listing. For each party (those who pay, those who receive, those who administer, those who resist, third parties, future people, non-human life where it matters) ask what changes for them. Source: standing in Boardman et al. and the societal perspective in Sanders et al. ("counts all significant outcomes and costs that flow from it, regardless of who experiences the outcomes or bears the costs" [sanders_2016_recommendations, Reference Cases]). Adds: effects that fall on someone outside the analysis's default frame, and the owner's rule 12 (report who bears the costs and who will resist). Cost: a long list for a policy with many parties; control by naming at most a dozen parties.

2.2.5 Matching method to gap. A first-order list by sector (the Sanders template) finds the obvious; independent runs per stakeholder find the omitted party; the futures wheel finds the knock-on effects; the premortem finds the harms. None of them removes the need for a final pass that asks what in the list is double counted (an effect and its consequence both listed as benefits) and which items are transfers (1.2.12).

2.2.6 An item the list must record, from the sources: the sector, the sign, who is affected, a one-line mechanism, and the evidence behind it if any (the Sanders template's columns), plus whether it is estimated in this pass, bounded only, or deferred, with the reason. This is the "keep a record of what was listed and not quantified" in 2.1.4.

## 3. Simplicity in decision models

### 3.1 Requisite decision models

3.1.1 Phillips 1984, "A theory of requisite decision models", Acta Psychologica 56:29-48: a requisite model is one whose "form and content ... sufficient to solve a particular problem" (the sentence recorded in `research/refs.toml`, which says it was read in the LSE repository; the paper itself is not stored) [phillips_1984_theory]. The paper was not available in full. From recall: the model is built by iterating with the people who own the problem until the model produces no new insight, so the stopping rule is that further modelling no longer changes the decision-maker's thinking, and sensitivity analysis is how one tests that. This ties to Claxton's rule (3.4.3) that the model is enough when more information would not change the choice.

### 3.2 Morgan and Henrion's ten commandments

3.2.1 Chapter 3 of `Uncertainty` (Morgan and Henrion 1990), "An Overview of Quantitative Policy Analysis", develops "what we term 'ten commandments' for good policy analysis, one of which involves being explicit about uncertainties" [morgan_1990_uncertainty, chapter abstract on the publisher page]. The chapter text is paywalled and was not read. From recall, the list includes: do your homework with experts and the literature; let the problem drive the analysis; make the analysis as simple as possible, but not simpler; identify all significant assumptions; be explicit about uncertainties; perform systematic sensitivity and uncertainty analysis; iteratively refine the problem statement and the analysis; document clearly; and expose the work to peer review. The owner-specified "as simple as possible but no simpler" is confirmed by a second, stored source: the FAST Standard states its signatories' belief that "financial models must be as simple as possible, but no simpler" [fast_2019_standard, The FAST Philosophy, p. 6].

### 3.3 Saltelli and others: added complexity can raise uncertainty

3.3.1 Saltelli et al. 2020, "Five ways to ensure that models serve society: a manifesto", Nature 582:482-484. The page is a Nature comment whose body was not retrievable (publisher wall); the points below are from a summarising fetch of an excerpt page and are therefore recalled and must be checked: "Most modellers are aware that there is a tradeoff between the usefulness of a model and the breadth it tries to capture ... But many are seduced by the idea of adding complexity in an attempt to capture reality more accurately ... As modellers incorporate more phenomena, a model might fit better to the training data, but at a cost." Its remedy is global uncertainty and sensitivity analysis in which "all that is uncertain" varies at once, which "often reveals that the uncertainty in predictions is substantially larger than originally asserted" (the same unstored excerpt) [saltelli_2020_manifesto].

3.3.2 The empirical support for the point is Puy et al. 2022 in Science Advances: adding detail raises a model's effective dimensions "and the weight of high-order interactions", which makes its estimates fuzzier (abstract and press coverage only, recorded in the shared entry) [puy_2022_effective].

3.3.3 What this changes in the design: a rule that each extra input in the full model must earn its place by a sensitivity result, not by being true.

### 3.4 Pindyck: simple, transparent models fed by expert probabilities

3.4.1 Pindyck 2013, "Climate change policy: what do the models tell us?", Journal of Economic Literature 51(3):860-872: integrated assessment models have "crucial flaws that make them close to useless as tools for policy analysis ... IAM-based analyses of climate policy create a perception of knowledge and precision, but that perception is illusory and misleading." (text read in the NBER working-paper version, WP 19244) [pindyck_2013_climate_models, abstract].

3.4.2 Pindyck 2015, NBER WP 21097, "The use and misuse of models for climate policy". Against the answer that Monte Carlo over uncertain parameters cures the problem: "What can we learn from assigning arbitrary probability distributions to the parameters of an arbitrary function and running Monte Carlo simulations? Nothing" (p. 6). His alternative is a model with few inputs: "start with three or four potential catastrophic outcomes ... a 10%, 30%, or 50% drop in GDP ... Now attach probabilities to those outcomes, say .2, .1, and .05 ... Given these outcomes and probabilities, and given a discount rate, we can calculate the present value of the expected benefits from avoiding these outcomes ... A simple ratio then gives us an estimate of the SCC" (pp. 13-14), and: "In effect, we would use expert opinion to determine the inputs to a simple, transparent, and easy-to-understand model (and I stress the importance of easy-to-understand)" (p. 13), because "the calculations I have just described constitute a 'model,' but one that is exceedingly simple and straightforward, and involves no pretense that we know the damage function" (p. 14). He accepts the cost: it "might not inspire the kind of awe and sense of scientific legitimacy conveyed by a large-scale IAM, but that is exactly the point" (p. 15). [pindyck_2015_use_misuse]

3.4.3 What this means for the project's speculative cases. The shape he describes is the shape the owner asked for: a few outcomes, a probability and a size for each, a discount rate, one ratio. It differs from the owner's first rule in `notes/owner_cba_rules.md` (distributions in, intervals out) only in what he rejects: distributions on the parameters of a made-up functional form, not distributions on elicited outcomes. See section 5.

### 3.5 FAST: a standard for spreadsheets a person can audit

3.5.1 The FAST Standard (02c, July 2019, Creative Commons BY 4.0) states a philosophy that matches the owner's words: "Any model that is unnecessarily complicated is not good. Without simplicity supported by rigorous structure a financial model will be poorly suited to its sole purpose", and "A flexible model is not an all-singing, all-dancing template model with an option switch for every eventuality. Flexibility is born of simplicity" [fast_2019_standard, pp. 5-7].

3.5.2 Rules a reviewer can apply by looking. "Do not write a formula longer than your thumb" (FAST 3.03-01); "No formula should take more than 24 seconds to explain" (FAST 3.03-02); "Do not write multi-line formulas" (3.03-03); "Use a limited set of Excel functions" (3.03-04); use flags rather than nested IF (3.03-05). On precision: "Spurious precision is distracting, verging on dangerous, particularly when it is unbalanced ... An overly precise base case only serves to drown analytically more important scenario-based risk analysis" (p. 7, Appropriate). Structure: "Rigorous consistency in model layout and organisation is essential" and the sheets are separated into inputs, calculations and presentation (sections 2.04 to 2.05).

3.5.3 FAST's own limits: it governs spreadsheet design, not testing, version control or the management environment; it "presumes the reader has a good understanding of Excel" (p. 5-6). So it is a design test, not an error-catching test. This agrees with the owner's own position (2026-11-09) that the sheet is for auditability, not a redundant build.

### 3.6 Choosing which few effects deserve a full model

3.6.1 Rank by swing. A tornado diagram or swing ranking sets each input to its low and high value in turn, holding the rest at the base, and sorts inputs by the change in the result. Clemen's `Making Hard Decisions` (2nd ed. 1996, ch. 5 on sensitivity analysis) is the textbook source (recalled; no free copy) [clemen_1996_making_hard_decisions]. The hand version is exactly section 1.5.2.5: the factor with the largest share of log-variance is the big part.

3.6.2 Rank by value of information. The expected value of perfect information for an input is the expected gain from learning it before choosing; Claxton 1999 sets this as the rule for whether to collect more evidence in health-technology decisions [claxton_1999_irrelevance]. In the repository's cost-benefit frame, an effect needs a full model only if, were it known exactly, the choice or the funding level could change. A tornado is a first approximation to this, and it ignores the decision threshold; EVPI does not.

3.6.3 The cheap form of both on a BOTEC is the switching value (Green Book 6.102 to 6.104, quoted at 2.1.3): ask how large the effect would have to be to flip the choice, and whether the BOTEC's interval reaches that value. If the whole interval lies on one side with margin, no full model is warranted. If the interval straddles the switching value, the effect is a candidate.

3.6.4 Stopping, in the sources' words. The Green Book: effort "should correlate to its scale, cost, complexity and risk" (1.8). Phillips: the model is requisite when it is enough to solve the problem (3.1.1). Morgan and Henrion: make it "as simple as possible, but not simpler" (3.2.1).

## 4. What this asks of the agents

### 4.1 Patterns a Fermi-estimating agent should be prompted with

4.1.1 Write the estimate as a product of three to six factors, each a quantity a reader can check against a number they know, and draw it as a tree (1.2.1, 1.2.2). Mahajan's own worked cases have two to four factors; the ten-factor case in 1.3.1 is a worst case, not a target.

4.1.2 For every factor give a median and a low-high range at one stated coverage (90%, as Squiggle's `to` reads it), a one-line reason, and where it came from: a stored source, a reference class, or "guess" (1.2.5, 1.4.1; owner rule 3 of the harness core, a gap filled by inference is marked as one).

4.1.3 Round every number to one or two figures and do the arithmetic in the head, with no code (1.2.7, 1.5.1; the owner's instruction). If the sum cannot be done in the head it is not a BOTEC: split it or stop and say so (the owner's instruction).

4.1.4 Combine ranges by the quadrature rule: ln F is the square root of the sum of the squares of the ln of each factor's give-or-take (1.3.3, 1.5.2). Show the median, the interval, and the mean, with the mean taken as median times exp(s squared over 2) (1.5.2.6). State which factors are assumed independent (1.3.4).

4.1.5 Give the share of the log-variance each factor carries and name the big part; spend any second method on that factor (1.2.8, 1.5.2.5, 1.2.4).

4.1.6 Estimate each important factor a second way, from unrelated knowledge, before relying on it (1.2.3, 1.2.4). If two ways disagree by more than their ranges allow, say so and do not average.

4.1.7 Check at the easy cases and the bounds: what is the answer at zero uptake and at full uptake, and what is the largest the quantity could physically or economically be (1.2.9, 1.2.13).

4.1.8 Check dimensions and the stock-flow line: units on every factor, no total compared with a rate, no transfer counted as both a cost and a benefit (1.2.10, 1.2.12).

4.1.9 Start from the reference class: find the base rate for the nearest comparable programme before the details of this one, and let the range cover it (1.2.16).

4.1.10 Use intensive quantities (per person, per year, per dollar) when carrying a number from one setting to another (1.2.11).

4.1.11 Keep the factors few and every one visible: name what the estimate leaves out in one line (1.2.18, 3.5.2).

4.1.12 Warn the agent against overconfidence: a first-guess range is probably too narrow, so widen it until a surprise beyond either end would be real (1.3.4).

### 4.2 The method an effects-listing step should use

4.2.1 Run several subagents in parallel, each given the policy and one lens (a stakeholder group, a time horizon, or good effects versus bad), none shown the others' lists, then pool and remove duplicates (2.2.1, 2.2.4).

4.2.2 Give one subagent the premortem frame: the policy has failed, say why; and one the futures-wheel frame: first-order, then second-order consequences, capped at two rings with an implausibility test on each item (2.2.2, 2.2.3).

4.2.3 Record each item as a row of an impact inventory: sector, sign, who is affected, mechanism in one line, evidence if any, and status (estimated, bounded only, deferred with reason) (2.1.1, 2.2.6).

4.2.4 Put a final pass on the pooled list: merge an effect with its own consequence, mark transfers, mark each item's party, and add the parties that have no row (2.2.5, 2.1.2).

4.2.5 Everything on the list is estimated at BOTEC depth or bounded; an item is left out of the estimate only with a written bound showing it cannot be among the largest (2.1.1, 1.2.13, 2.1.3).

4.2.6 For each item left unquantified, record its switching value, the size at which it would change the headline (2.1.3, 3.6.3).

### 4.3 Simplicity tests a reviewer should apply

4.3.1 Does each modelled effect have no more than about half a dozen inputs, and does its arithmetic fit on one spreadsheet tab? Count the inputs and the formulas (the owner's test; FAST 3.03; Phillips 3.1.1).

4.3.2 Does the model earn each input by a swing or a value-of-information result, with the ranking shown? An input without one is a candidate for deletion (3.6.1, 3.6.2, 3.3.3; prompt a deletion first, harness core rule 11).

4.3.3 Is any formula longer than a thumb, explained in more than 24 seconds, nested in an IF chain, or reading its own output? Break it or remove it (3.5.2).

4.3.4 Is each probability or distribution an elicited statement about an outcome, rather than a distribution put on the parameters of an invented functional form? If the form is invented, replace it with a few outcomes and probabilities (3.4.2).

4.3.5 Was any input given more precision than its evidence allows, so that the base case looks firmer than the guess behind it? (3.5.2, "Spurious precision").

4.3.6 Could the headline be recomputed from a spreadsheet tab by a reader with no code? If it needs a library call, the model is not auditable in the owner's sense (3.5.1, and the owner's rule 2 in `notes/owner_cba_rules.md`).

4.3.7 Do the ranges combine as in 1.3.3, and is the mean shown beside the median with its coverage named? (1.5.2.6).

4.3.8 Does each effect on the inventory appear in the model or carry a written reason and a switching value? (4.2.5, 4.2.6).

4.3.9 Is the model's size, in inputs and tabs, within what the earlier, simpler version had, and is any growth justified by a result in the tornado? (3.3.1, 3.5.2).

## 5. Where this contradicts or qualifies the owner's words

5.1 "Math that could fit on one spreadsheet tab" is supported by FAST 3.03 and Pindyck's example, but Pindyck's own simplicity cuts against one of the owner's standing rules. Rule 1 of `notes/owner_cba_rules.md` says "distributions in, intervals and expected values out, from the first day." Pindyck 2015 (p. 6) argues that running Monte Carlo over arbitrary distributions on an arbitrary function "buys us nothing". The two agree if the distributions are elicited ranges on outcomes and inputs that have a meaning, not on a free parameter of a made-up form. The agent prompts in 4.1 and 4.3.4 are written for that reading, and Pindyck's catastrophe-table form (outcomes, probabilities, one ratio) is the model for the speculative cases.

5.2 "No Python code" is consistent with the Fermi literature, but the owner's "multiplying a few known or guessable values" covers only products and quotients. Sums, probabilities near zero or one, and correlated factors need either a rule stated in the prompt or the sampled model of section 3 (1.5.3).

5.3 The mean of a product of ranges is not the product of the means; by hand it is the median times exp(s squared over 2), and with wide factors it is large (a factor 1.4 for the example in 1.5.2.6 at 90% coverage, 2.4 at 2/3 coverage). A BOTEC that reports only the median understates the expected value that a cost-benefit analysis needs. The note asks the agent to show both.

5.4 "Glenn 1972" is not what the stored chapter says: it dates the futures wheel to 1971 (2.2.2).

5.5 Gut-estimated ranges are usually too narrow; the quadrature rule makes narrow ranges narrower still when many factors are combined. Agents should be told to widen first guesses and to check them with a second method (4.1.12, 4.1.6). The size of the effect in LLM agents is not in these sources.

5.6 The owner's wording "estimate all of those" for every effect is stricter than the sources: Sanders exempts effects "likely to have a negligible effect on the result", and the Green Book says it "may be disproportionate to monetise or quantify every impact". A bounded-only status (4.2.5) keeps the owner's breadth while honouring the sources.

5.7 Several sources behind sections 2 and 3 were not read in full text and are marked recalled: Tetlock and Gardner, Delbecq and Van de Ven, Klein, Boardman et al., Clemen, Morgan and Henrion chapter 3, Phillips (beyond the abstract), Saltelli et al. (excerpt only), Guesstimate, Soll and Klayman, Sandberg et al. A brief that rests on one should send a source-fetcher for it first.
