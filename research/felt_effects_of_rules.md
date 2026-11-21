# Felt effects of rules: how to count the small, frequent experiences no market prices

A methods note written on 2026-11-14 for the owner's request of that day. It was revised the same day to answer a referee's report. Section 8 says how each of the referee's findings was answered. The table of section 6 is installed as `notes/felt_effects.toml`, and two seat definitions each gained a sentence or two (section 6.2).

His words, with typos corrected: "If there's a situation of possible systemic or implicit bias, you don't solve that by inserting verbiage about being unbiased. You do a process audit to see if certain voices are being systematically overlooked because the system does not understand them or think about them or know how to count them. Many people experience the effects of regulation in a way that might be classified as a microaggression. When they get in a weak shower, or have to flush a toilet twice, or their car engine stops at a light, they feel oppressed and annoyed. So we should always try to calculate the effects of these microaggressions. Calculate how many people will be affected, what percentage will feel the impacts in this way, and how often it happens. Do a lit search on the effects of microaggressions and try to calculate the microDALY cost of each one. Then this effect becomes part of the checklist applied to any policy that has these kinds of effects. And for fairness, do we have any reports of populations who feel actively happy when they encounter the effects of regulation? Maybe someone who feels a little sense of joy or pride at being in an advanced enlightened society when their car engine shuts off at a light? I've never seen anyone talking like this the way people complain about regulation but maybe it happens. And then brainstorm ways to honestly measure and quantify more voices and viewpoints, pro and con, in similar ways."

What the class is. A felt effect of a rule is a small, frequent change in everyday experience that the rule causes. No market prices it, so an analysis leaves it at zero. It can fall on either side.

1. Unpleasant members include irritation at a product that works worse (his weak shower, second flush and engine that stops at a light), the feeling of being overridden, and a hassle.
2. Pleasant members include enjoyment of what the rule changes (a smoke-free bar), relief, reassurance and pride.

His three examples stand for the class. Section 5 sorts the class into eight types.

Every number below is quoted from a source stored in `research/sources/<key>/text.txt`, cited by key and line, or is marked as an inference or a judgement. Works marked "recalled" were not opened and are cited from memory, with an entry in `research/refs.toml` saying so. Numbers are rounded to two significant figures, except in quotations.

## 1. The established techniques

1.1. The noise-annoyance burden of disease. This is the technique his calculation reaches for, and it is already in official use. WHO Europe counts the people highly annoyed by traffic noise and multiplies by a disability weight to get disability-adjusted life-years (DALYs). The count comes from an exposure–response curve or from a survey.

1.1.1. The curves pool the "raw data from a total of 54 studies" (`who_2011_noise_burden`, line 6213). A survey can stand in for the curve: one may "replace steps (a) and (b) by direct estimates of annoyance prevalence through an annoyance survey in the population concerned (outcome-based approach)" (`who_2011_noise_burden`, lines 6190-6192).

1.1.2. The weight is the weak part. "Given the limited number of studies on a DW for annoyance ... a tentative DW of 0.02 is proposed with a relatively large uncertainty interval" (`who_2011_noise_burden`, lines 6248-6251); the interval runs from 0.01 to 0.12. Only the highly annoyed are counted, because "only for rather severe annoyance may it be possible to gain consensus on a DW that can be meaningfully distinguished from zero" (`who_2011_noise_burden`, lines 6185-6187).

1.1.3. The UK government adopted the method for appraisal in 2014: "Value of annoyance = population exposed x proportion highly annoyed x disability weight x health value" (`defra_2014_noise_valuing_impacts`, line 762). Its reason: "Whilst annoyance is not a disease in itself, it does affect wellbeing" (`defra_2014_noise_valuing_impacts`, line 728).

1.1.4. The first weights measured in the general public came in 2024: "The disability weight for moderate and severe annoyance was 0.006 and 0.011, respectively" (`haagsma_2024_noise_disability_weights`, line 20). They come from 4,056 respondents in four countries (line 88).

1.2. Weight times duration. Global Burden of Disease (GBD) studies weight a short illness by its weight times its duration, as they do any health state.

1.2.1. The lowest weights the GBD measures are the precedent for a very mild state: "Across all states, estimated weights ranged from 0·003 (95% uncertainty interval 0·001–0·007) for mild distance vision impairment" upward (`salomon_2015_gbd_disability_weights`, lines 531-533). The answers "were insensitive to whether the comparisons were framed in terms of temporary or chronic outcomes" (line 27), where the temporary framing was a state lasting "1 week" (lines 390-391).

1.2.2. The multiplication is the standard of experienced utility: total experienced utility is the integral of moment-by-moment utility over time (Kahneman, Wakker and Sarin 1997, `kahneman_wakker_sarin_1997`, recalled).

1.2.3. What no study measures is the weight of one felt minute. A review of methods for valuing temporary health states found no gold standard (Wright et al. 2009, `wright_2009_temporary_health_states`; the abstract was read, not stored).

1.3. Experienced utility: the Day Reconstruction Method and experience sampling. These measure how people feel during each episode of their day, the thing his "how often" asks for.

1.3.1. "The Day Reconstruction Method (DRM) assesses how people spend their time and how they experience the various activities and settings of their lives, combining features of time-budget measurement and experience sampling" (`kahneman_2004_drm`, line 3, the abstract). It was validated against experience sampling in "909 employed women" (`kahneman_2004_drm`, line 3).

1.3.2. The U-index is the share of time a person spends in an unpleasant state (Kahneman and Krueger 2006, `kahneman_krueger_2006_measurement`, not stored).

1.3.3. The method gives no money value: "There is currently no recommended standard ... approach for monetising wellbeing changes based on eudemonic or affective measures" (`hm_treasury_2021_wellbeing_guidance`, lines 1550-1553).

1.4. Daily hassles and uplifts. Small, frequent irritations add up to measurable harm. "It was found that the Hassles Scale was a better predictor of concurrent and subsequent psychological symptoms than were the life events scores" (`kanner_1981_hassles`, line 3, the abstract). Uplifts were "related, although only modestly so, to positive and negative affect" (`kanner_1981_hassles`, line 3). The literature gives no weight per hassle and no money value.

1.5. Life satisfaction and the WELLBY. A WELLBY is a one-point change in life satisfaction, on a scale of 0 to 10, for one person for one year.

1.5.1. HM Treasury values "a one-point change in life satisfaction for one year" at "£13,000 [Low: £10,000, High £16,000]" in 2019 prices (`hm_treasury_2021_wellbeing_guidance`, lines 1572-1575). It ties the scale to health: "One QALY is then associated with a 7- point change in life satisfaction" (line 2885).

1.5.2. The scale suits a rule broad enough to move how people rate their whole lives, such as smoking bans (4.3.2). A weak shower will not show in a life rating.

1.6. Adaptation and reference points.

1.6.1. "research suggests that people do not adapt to the negative impact of noise (Weinstein, 1982), disagreeable job conditions, nor to the positive benefits of volunteering ... People tend to adapt little to situations that regularly draw their attention (Dolan, 2014)" (`hm_treasury_2021_wellbeing_guidance`, lines 470-473).

1.6.2. People "adapt to serious chronic health conditions" (`loewenstein_ubel_2008_hedonic_adaptation`, lines 22-26). That source concludes that "evaluations of welfare will inevitably have to be informed by a combination of both approaches", meaning both experienced well-being and people's judgements of a state (`loewenstein_ubel_2008_hedonic_adaptation`, lines 25-26).

1.6.3. People judge a change against what they are used to (reference-dependent preferences; Kőszegi and Rabin 2006, `koszegi_rabin_2006`, recalled). Someone who never had the stronger shower has a different reference point from someone who lost it. So the share who feel a rule's effect is measured among people living with the rule now (2.5).

1.7. Money per episode-day: the US precedent. EPA's benefit tool values a day of a mild symptom by stated willingness to pay, applied to counts of days. Its values are given "in 2015 $" (`benmap_ce_2017_appendices`, line 17551), and "All estimates are WTP to avoid one day of symptom" (line 17652). In the midrange column:

1.7.1. wheeze, $4.57 (lines 17635-17643);

1.7.2. headache, $18.14 (lines 17605-17613);

1.7.3. eye irritation, $28.50 (lines 17595-17603).

1.7.4. A minor restricted-activity day has a "distribution centered at $69.58" (`benmap_ce_2017_appendices`, line 17811). This is the nearest regulatory precedent for what this note does, and it is denominated in money per episode-day.

1.8. Willingness to pay of either sign, measured so that answering truthfully pays. Two field studies measure a policy instrument's felt effects on both sides by one method.

1.8.1. Allcott and Kessler elicited what households would pay to keep receiving home energy reports, with a price list that allowed negative values. "While most people like HERs, 35 percent have weakly negative WTP" (`allcott_kessler_2019_nudges`, line 143). Weakly negative includes zero, and "most of that group is close to indifferent: 56 percent of negative WTPs are between $0 and $-1" (`allcott_kessler_2019_nudges`, lines 1567-1569). The reports cost those who acted on them more than their bills show: "the remaining 49 percent represents net financial, time, comfort, and psychological costs" (`allcott_kessler_2019_nudges`, lines 154-156). Leaving such costs out means "traditional program evaluation approaches overstate welfare gains by a factor of five" (`allcott_kessler_2019_nudges`, line 42).

1.8.2. Butera, Metcalfe, Morrison and Taubinsky price pride and shame from public recognition. Their procedure "allowed participants to indicate a WTP for public recognition between -$8 and $8" (`butera_2022_shame_pride`, lines 557-559). Recognition paid off for high performers and cost low performers. The net was "negative-sum in the YMCA and BU samples, is approximately zero-sum in the Berkeley sample, and is positive-sum in the Prolific sample" (`butera_2022_shame_pride`, lines 241-243). This is the literature's direct answer to his question about pride.

1.9. Remedies: defensive spending as a bound. Where people can remedy a felt effect (remove a restrictor, press a button, buy a better product), what the remedy costs bounds the loss from above for those who know of it (averting expenditure; Courant and Porter 1981, `courant_porter_1981`, recalled).

1.9.1. A person who uses the remedy no longer feels the episodes. They bear the remedy's cost instead, and where the remedy undoes the rule, they also undo its benefit for themselves.

1.9.2. A person who knows of the remedy and keeps the rule's default reveals that the felt cost is below the remedy's cost.

1.9.3. Revealed preference measures decision utility, which 1.6 says may differ from experienced utility.

1.9.4. The dispute over efficiency standards turns on this split. Gayer and Viscusi argue that the agencies' gains rest "on the agencies' poorly-supported assumption that consumers and firms make irrational purchasing decisions" (`gayer_viscusi_2012_overriding`, line 189). Studies of appliance sales find that standards "have led to an increase in quality" (`houde_spurlock_2015_standards_quality`, lines 57-58). They also find that "prices declined while quality and consumer welfare increased, especially when standards become more stringent" (`brucal_roberts_2019_standards_hurt`, lines 46-47).

1.10. The value of time, with a weight for unpleasant time. US EPA values nonwork time at "after-tax wages" (`epa_2020_valuing_time_use`, line 147). UK transport appraisal weights waiting time at "1.5 – 2.5" times in-vehicle time (`dft_2024_tag_m3_2`, line 1396).

1.10.1. The weight multiplies the value of in-vehicle time, not the wage. US guidance values personal travel time at about half the wage (`dot_2016_value_of_travel_time`, recalled, not stored).

1.10.2. So the premium for a waiting minute, the part above a weight of 1, is about 0.25 to 0.75 of a wage (inference: 0.5 to 1.5 times 0.5). It is a measured price of an unpleasant minute.

1.11. Reactance and procedural utility. His word "oppressed" names a second feeling, distinct from irritation at performance.

1.11.1. "Reactance is an unpleasant motivational arousal that emerges when people experience a threat to or loss of their free behaviors" (`steindl_2015_reactance`, lines 50-54).

1.11.2. Procedural utility is the well-being people draw from how a decision is made, apart from its result (Frey, Benz and Stutzer 2004, `frey_benz_stutzer_2004_procedural_utility`, not stored).

1.11.3. No weight per episode exists. A laboratory study separates the value of holding a decision right from the value of its outcome (Bartling, Fehr and Herz 2014, `bartling_fehr_herz_2014`, recalled). The laboratory premium is relative to the value of the outcome at stake. So it is carried to a rule by judgement as a share of the T1 value for the same people, sharing T1's factors by name, never as a free-standing amount per person.

1.12. Administrative burden and sludge audits. Herd and Moynihan describe the psychological costs of dealing with the state (`herd_2018_administrative`, in the shared library, recalled). These costs are now measured by audit. Sludge audits "tackle these issues by systematically identifying and quantifying psychological, financial and temporal costs, as well as highlighting disparities in equitable and efficient access" (`oecd_2024_sludge_audits`, lines 212-214).

1.13. What the microaggressions literature can and cannot supply.

1.13.1. The term means identity-based slights: "brief and commonplace daily verbal, behavioral, or environmental indignities, whether intentional or unintentional, that communicate hostile, derogatory, or negative racial slights and insults toward people of color" (`sue_2007_microaggressions`, line 3).

1.13.2. A review of its five premises found "negligible support for all five suppositions" and recommends "abandonment of the term" (`lilienfeld_2017_microaggressions`, line 3).

1.13.3. It supplies the idea that small, repeated slights add up, and the practice of counting them by how often people report them. It cannot supply a weight per episode or any study of how products perform.

1.13.4. A weak shower carries no message about anyone's identity. The nearest thing among rules is a rule read as contempt for a group's way of life, which belongs to the type "being overridden" (section 5).

1.14. The technique that best fits his idea, and where it departs from his words. The best fit is the noise-annoyance burden (1.1), counted by episodes, weight times duration (1.2), and valued at the case's value of a life-year. Its chain is his own four factors (2.1). It departs from his words in five places:

1.14.1. The literature. Microaggressions research gives no weights. The hassles and noise-annoyance literatures carry his idea (1.13).

1.14.2. "How often". The noise method values a year of being highly annoyed and has no episodes. An episode's weight is not measured anywhere. It is bracketed by three sources (2.3).

1.14.3. "Oppressed and annoyed". These are two quantities: irritation at worse performance, and the feeling of being overridden (1.11). The second has no weight per episode. It is a bound, or a share of the first for the same people (1.11.3).

1.14.4. The scale. His "microDALY" counts a loss. The unit used here is the life-year as a welfare equivalence: money converts to life-years at the person's value of a life-year (`notes/owner_cba_rules.md`, rules 15 to 17). So a pleasant minute counts as fully as an unpleasant one (2.8).

1.14.5. The remedy. Where a cheap remedy exists, it caps the felt loss of those who know of it (1.9). Much of the irritation may already be in an analysis's willingness to pay for the lost performance (2.6).

1.15. The process audit. His first sentence describes an audit of the process, not a sentence telling seats to be fair. The established forms are the sludge audit (1.12) and social impact assessment (Vanclay 2003, `vanclay_2003_sia_principles`, not stored).

1.15.1. The audit reads finished cases' lists of effects and estimates against the types of section 5, one cell per case and type: does not apply, priced, listed but not priced, or missing. A missing cell is an effect no seat raised; a listed one with no price is one no seat could size. Section 6 makes the audit a standing check inside every case: a table and two seat sentences.

## 2. A calculation a person can audit by hand

2.1. The chain: the owner's four factors. For one felt effect in one year:

value = P × s × f × m × V / 1,000,000

2.1.1. The factors:

2.1.1.1. P is the people whose experience differs because of the rule: the people exposed times the rule's share in the change, judged as one number (the `fermi-estimator` rule 6.5).

2.1.1.2. s is the share of them who feel it.

2.1.1.3. f is the episodes a year for each person who feels it.

2.1.1.4. m is the micro-life-years an episode is worth.

2.1.1.5. V is the case's value of a life-year.

2.1.2. m is derived beside the chain: felt minutes in an episode × weight per felt minute × 1.901. The constant 1.901 is the micro-life-years in one minute (inference: 1,000,000 / 525,960).

2.1.3. The value is the difference in felt value between the world with the rule and the world without it, whichever world is the baseline. It may be of either sign.

2.1.4. This is the UK's noise formula (1.1.3), with the share and the year split into the owner's "how often".

2.2. The units. A micro-life-year is one millionth of a life-year, about 32 seconds. At the US guidance's "$611,000 as the central estimate of VSLY for analyses using a 3% discount rate" (HHS 2026, quoted in `research/guidance/2026-10-29_guidance_values.md`, line 27):

2.2.1. a micro-life-year is worth $0.61;

2.2.2. one weighted minute is worth $1.16 (inference: 611,000 / 525,960).

2.3. The weight per felt minute. This is one factor, the share of a full-health minute that a felt minute costs or adds. Three sources bracket it, and none measures it:

2.3.1. The floor: disability weights read per felt minute. These are 0.003 for the lowest GBD state (`salomon_2015_gbd_disability_weights`, lines 531-533), and 0.006 and 0.011 for moderate and severe annoyance (`haagsma_2024_noise_disability_weights`, line 20). WHO's 0.02 for being highly annoyed has an interval up to 0.12 (`who_2011_noise_burden`, lines 6248-6251).

2.3.2. The middle: symptom-day willingness to pay spread over 960 waking minutes (16 hours, a judgement). This gives 0.0041 for wheeze, 0.016 for headache, 0.026 for eye irritation and 0.062 for a minor restricted-activity day (inference: $4.57, $18.14, $28.50 and $69.58 ÷ 960 ÷ $1.16, from 1.7).

2.3.2.1. These figures assume the symptom is felt every waking minute. A symptom felt for a quarter of the day gives four times as much per felt minute.

2.3.2.2. They are in 2015 dollars against a value of a life-year of a later year. The price change is far inside the factor's range.

2.3.3. The high end: the waiting premium, 0.25 to 0.75 of a wage (1.10). At after-tax wages of $15 to $35 an hour (a judgement, to be read from the Bureau of Labor Statistics in a case), that is $0.063 to $0.44 a minute, or 0.054 to 0.38 of a full-health minute (inference). A bus stop is harsher than a bathroom, and the premium also prices uncertainty and exposure, so it sets only the high end.

2.3.4. The factor: low 0.005, middle 0.03, high 0.2, combined from the three by judgement. A pleasant felt minute of matching intensity takes the same weight with the opposite sign.

2.4. The remedy. Where a remedy exists, the effect splits in two, by whether those who feel it have a usable remedy: they know of it and can use it (1.9; the referee's finding 1 and round 2, R2.5). A renter cannot replace a fixture.

2.4.1. Those with no usable remedy: P × s × u × f × m × V / 1,000,000, where u is the share of those who feel it who have no usable remedy.

2.4.2. Those with a usable remedy: P × s × (1 − u) × their felt cost a person-year. Each of its low, middle and high is no more than the remedy's annual cost. The share (1 − u) is drawn as the complement of u (`complement_of`), never as a share of its own, so the two can never sum past s. Those who use the remedy bear its cost, and those who keep the default reveal a felt cost below it.

2.4.3. In 2.4.1, u and the felt cost move against each other: a person who loses much has reason to find the remedy. The low and high of their product are judged afresh, as one quantity (the `fermi-estimator` rule 6.5), never as the product of each one's ends.

2.4.4. Where the remedy undoes the rule (a restrictor removed, a button pressed), the share who use it lowers the rule's benefit stream, under the same factor name. A remedy that keeps the rule, such as a better compliant product, lowers nothing.

2.4.5. A gain is bounded the same way. Those who could have had the rule's result before it, and did not, gain at most what that would have cost them.

2.5. The share s: the order of evidence. The sources, best first:

2.5.1. A probability sample of current users, asked a balanced question that offers both directions. The survey is recorded with the surveyor's role and stake (the owner's rule 10). The standard form is the five-point annoyance question of ISO/TS 15666 (`iso_ts_15666`, recalled).

2.5.2. Measured behavior. Remedy sales, opt-out logs and switch-off rates give exactly the share who use a remedy, and only a floor on the share who feel the effect. Allcott and Kessler show how far apart the two can be. In a typical program, "around one percent of consumers dislike HERs enough to take the time to opt out" (`allcott_kessler_2019_nudges`, lines 740-741), yet 35 percent had weakly negative willingness to pay, most of them close to indifferent (1.8.1). The share who would pay anything to stop the reports was many times the share who opted out. Meters give the frequency f.

2.5.3. Judgement. Its low reaches the lowest share any source supports.

2.5.4. Complaints, reviews and officials' statements set intensity and a floor, never the share. Online ratings over-represent the extremes (Hu, Pavlou and Zhang 2009, `hu_pavlou_zhang_2009`, recalled).

2.5.5. What was found for the three examples:

2.5.5.1. An insurer's survey: "more than a quarter (27 per cent) of drivers whose car has auto start/stop admit to turning it off because they find it annoying" (`directline_2024_in_car_tech`, line 335). That share uses the remedy.

2.5.5.2. A water district's survey of 1,300 rebate customers, which offered both directions on a satisfaction scale. Its ratings by model ran from "an 8.37 out of 10" down to "a 5.91", and "67% of respondents said they had to double-flush once or more a month" (`mwdsc_1999_ulft_survey_supplyht`, line 128). The same survey was also read as "More than 60 percent responded that they either never double flush, or double flush once a month" (`ballanco_2000_pmmag_ulft`, lines 185-186).

2.5.5.3. Meters: flushes per person a day went from "5.17-fpcd" to "5.50-fpcd" with 1.6-gallon toilets (`koeller_2003_dual_flush`, lines 69-71).

2.5.5.4. A test of showerheads by a panel reports that "59 to 64% of same models received" a rating of not wanting to buy (`mowris_2010_showerhead_satisfaction`, lines 291-292). That is a panel rating models put in front of it, which gives intensity rather than the share of current users.

2.5.5.5. Not found: a rate at which flow restrictors are removed, sales of devices that defeat stop-start, and a balanced survey of current showerhead users.

2.6. What the chain may double count:

2.6.1. Willingness to pay for the lost attribute (a stronger shower, a surer flush). It is the same effect measured another way. The two are mixed under the owner's rule 9, never added.

2.6.2. The time an episode takes. Time is its own effect at a weight of 1. Only the premium above 1 is a source for the felt weight (2.3.3).

2.6.3. A stated willingness to pay to repeal the rule. It contains both performance and the feeling of being overridden.

2.6.4. Noise annoyance and house-price values of the same noise. These are one quantity: Defra leaves the house-price values aside for that reason (`defra_2014_noise_valuing_impacts`, line 721).

2.6.5. Reassurance about a health risk and the value of a statistical life, which already prices fear of the risk.

2.6.6. Remedy users, once they are counted at the remedy's cost.

2.6.7. Where an analysis assumed no loss of performance, as efficiency-standard analyses often do, the felt effect is the performance stream itself, added once.

2.7. The second method. A second chain is truly independent when it starts from different knowledge (the `fermi-estimator` rule 8). Options:

2.7.1. The attribute's market value: a price premium times the share who buy the product.

2.7.2. The attribute's stated value, from a choice experiment.

2.7.3. A count of remedy users.

2.7.4. For a voluntary program, non-resource costs as a share of private savings: 0.49 in one study (1.8.1).

2.7.5. How the methods combine. Two independent chains are mixed at equal weight. A bound truncates a chain; it is not mixed in. Sources for one factor merge into that factor. A time chain at the waiting weight shares people, frequency and minutes with the felt chain, so it is a source for the weight, not a second chain.

2.8. Gains and losses on one scale. On the life-year as a welfare equivalence, a pleasant felt minute of matching intensity counts as fully as an unpleasant one, and a willingness to pay for an amenity converts at V. A disability weight is one source for a felt minute's intensity; it is not the unit. Adopting a rule and repealing it then value the same felt difference with opposite signs, whichever world is the baseline. Section 3.4 is a worked gain.

## 3. Worked estimates

The form is the `fermi-estimator`'s. Each factor has a low, a middle and a high. A row's low is the product of the lows and its high the product of the highs, which is not a 90 percent interval.

3.0. The frame. The United States, one year, at V = $610,000, so a micro-life-year is worth $0.61 and a weighted minute $1.16. Only the felt effect is counted: time, water and fuel are other streams. These illustrate the method; they are no case's numbers. Every example uses the weight of 2.3.4: 0.005, 0.03 and 0.2.

3.1. A weak shower under a flow limit for showerheads.

| Factor | Low | Middle | High | Unit | Source |
|---|---|---|---|---|---|
| P, people whose shower is weaker because of the rule | 4.0e7 | 1.2e8 | 2.4e8 | people | People with a head at the limit, 2.0e8, 3.0e8 and 3.4e8 (the WaterSense statement's "220 million showerheads" with "approximately 10 percent" replaced each year, `epa_watersense_2010_showerhead_support`, line 65, put nearly every head under the 1994 limit, an inference; about 1.5 people a head, a judgement). The rule's share is 0.2, 0.4 and 0.7 (judgement: state codes, water bills and heads redesigned to feel stronger at the limit would leave many showers the same without it) |
| s, share who feel it | 0.050 | 0.20 | 0.50 | share | judgement; no balanced survey of current users found (2.5.5) |
| u, share of them with no usable remedy | 0.20 | 0.50 | 0.80 | share | judgement; no source found for the share who know a restrictor can come out or that stronger-feeling compliant heads are sold |
| f, showers a year | 200 | 300 | 365 | per person | judgement |
| m, micro-life-years a felt shower | 0.0095 | 0.17 | 3.0 | micro-life-years | 1, 3 and 8 felt minutes (judgement) × the weight × 1.901 |
| c, the remedy's annual cost | 0.10 | 1.0 | 5.0 | $ a person-year | judgement. Removing the restrictor takes 5 to 30 minutes at an after-tax wage, spread over the head's life of 5 to 15 years ($0.083 to $3.5). A better-designed compliant head costs "$30 retail" (`epa_watersense_2010_showerhead_support`, line 287) every ten years, shared by 1.5 to 2.5 people ($1.2 to $2) |

3.1.1. The felt cost per person-year, f × m × $0.61, is $1.2, $31 or $680.

3.1.2. Those with no usable remedy (2.4.1). Here u and the felt cost a person-year are judged as one quantity (2.4.3): $0.23, $16 or $40 for each person who feels it. The low is 0.20 × $1.2 and the middle 0.50 × $31. The high is a judgement: 0.80 × at most $50, since a person whose felt cost passes about $50 a year has reason to find a $30 head. The first revision's high, 0.80 × $680, multiplied two ends that move against each other. Middle: 1.2e8 × 0.20 × $16 = $380 million, about 630 life-years. Low: 4.0e7 × 0.050 × $0.23 = $0.46 million. High: 2.4e8 × 0.50 × $40 = $4.8 billion.

3.1.3. Those with a usable remedy (2.4.2). Their share is the complement of u: 0.20, 0.50 or 0.80, where the low takes u at its high. Each is valued at their felt cost a person-year, never above c: $0.10, $1.0 or $5.0. Middle: 1.2e8 × 0.20 × 0.50 × $1.0 = $12 million. Low: 4.0e7 × 0.050 × 0.20 × $0.10 = $0.040 million. High: 2.4e8 × 0.50 × 0.80 × $5.0 = $0.48 billion.

3.1.4. Remedy users who remove the restrictor lower the rule's water saving by their share. Those who buy a better compliant head lower nothing (2.4.4).

3.1.5. The total is $400 million a year, with a range of $0.50 million to $5.3 billion. One felt shower costs 0.17 micro-life-years, or $0.10.

3.1.6. The second method. No stored source gives the market or stated value of shower force, and no removal rate was found. The row therefore carries the cap and no second chain. A lead for a case, seen only in a search result: an incentivized survey of willingness to pay for low-flow and feedback showerheads (Tomberg 2024, `tomberg_2024_showerheads`, not opened).

3.1.7. The big part. The merged quantity of 3.1.2 is 170 times its low, and m is 320 times its low (the weight 40 times, the felt minutes 8 times). Depth goes first to the share with a usable remedy, which a survey can measure, and to the felt cost that would send a person to find one. The weight of a felt minute in the shower would need a new study.

3.1.8. The row leaves out water and energy saved, rinse time, and the feeling of being overridden.

3.2. A second flush under a flush limit for toilets.

| Factor | Low | Middle | High | Unit | Source |
|---|---|---|---|---|---|
| P, people whose toilet flushes worse because of the rule | 2.0e7 | 9.0e7 | 2.4e8 | people | People with a toilet at the limit, 2.0e8, 3.0e8 and 3.4e8 (as in 3.1). The rule's share is 0.1, 0.3 and 0.7 (judgement: a maker says there is "essentially no difference in the way current 1.6-gpf toilets flush compared to 3.5-gpf toilets", `mwdsc_1999_ulft_survey_supplyht`, line 132, a party with a stake; state codes came before the federal rule) |
| s, share who must flush twice at least sometimes | 0.20 | 0.40 | 0.67 | share | high, "67% of respondents said they had to double-flush once or more a month" (`mwdsc_1999_ulft_survey_supplyht`, line 128); middle, under 40 percent more than monthly (`ballanco_2000_pmmag_ulft`, lines 185-186); low, judgement, since later toilets flush better |
| u, share of them with no usable remedy | 0.25 | 0.35 | 0.45 | share | judgement: renters cannot replace a toilet, and about a third of US households rent (recalled, not stored); owners are taken to know a toilet can be replaced |
| f, second flushes a year | 12 | 50 | 180 | per person who feels it | low, once a month (the survey's threshold); high, Seattle's 0.33 more flushes a person-day (`koeller_2003_dual_flush`, lines 69-71) ÷ 0.67 (inference); middle, judgement |
| m, micro-life-years a second flush | 0.0024 | 0.029 | 0.76 | micro-life-years | 0.25, 0.5 and 2 felt minutes (judgement) × the weight × 1.901 |
| c, the remedy's annual cost: an early replacement with a better compliant toilet | 4 | 8 | 15 | $ a person-year | judgement: $250 to $600 installed, over 20 years, shared by 2 to 3 people. It keeps the rule's water saving |

3.2.1. The felt cost per person-year is $0.017, $0.87 or $84.

3.2.2. Renters, with no usable remedy. Here u and the felt cost are judged as one quantity, $0.0043, $0.30 or $38 for each person who feels it: the products of the two, since a renter's felt cost does not send them to a remedy they cannot use. Low: 2.0e7 × 0.20 × $0.0043 = $0.017 million. Middle: 9.0e7 × 0.40 × $0.30 = $11 million. High: 2.4e8 × 0.67 × $38 = $6.1 billion.

3.2.3. Owners, with a usable remedy. Their share is the complement of u: 0.55, 0.65 or 0.75. Their felt cost is capped at c: $0.017, $0.87 or $15. Low: 2.0e7 × 0.20 × 0.55 × $0.017 = $0.037 million. Middle: 9.0e7 × 0.40 × 0.65 × $0.87 = $20 million. High: 2.4e8 × 0.67 × 0.75 × $15 = $1.8 billion.

3.2.4. The total is $31 million a year, with a range of $0.055 million to $7.9 billion, or 51 life-years at the middle. One felt second flush costs 0.029 micro-life-years, or $0.017.

3.2.5. The time of the second flushes is its own effect at a weight of 1: 3.6e7 × 50 × 0.5 minutes × $0.42 a minute = $380 million at the middle (inference). It is about twelve times the felt effect.

3.2.6. The second method: no stored source. Price premia for toilets rated for flush performance would serve.

3.2.7. The row leaves out the water of the second flush, clogs, and the feeling of being overridden.

3.3. An engine that stops at a light (stop-start).

3.3.1. The rule is a credit, not a mandate: the agency ended "credits to automakers who install automatic start-stop ignition systems" (`ap_2026_epa_start_stop_credits`, line 123). The remedy is the off button. Everyone with the feature can see it (judgement), so no one is in the group with no usable remedy, and pressing it undoes the rule.

| Factor | Low | Middle | High | Unit | Source |
|---|---|---|---|---|---|
| P, drivers whose car stops its engine because of the credit | 2.4e7 | 7.2e7 | 1.4e8 | drivers | Drivers with the feature, 8.0e7, 1.2e8 and 1.6e8 ("About two-thirds of vehicles now have it", `ap_2026_epa_start_stop_credits`, line 135, × about 230 million drivers, a judgement, not stored). The credit's share is 0.3, 0.6 and 0.9 (judgement) |
| a, share who turn it off | 0.15 | 0.27 | 0.40 | share | middle, the insurer's 2025 survey of UK drivers (`directline_2024_in_car_tech`, line 335, a party with a stake); low and high, judgement |
| c, the cost of pressing the button | 0.20 | 14 | 44 | $ a driver-year | judgement: 1,000 or 1,500 trips × 2 or 3 seconds × $25 or $35 an hour. The low: a press made during other start-up actions displaces almost no time, and whether seconds are worth the full value of time is the question of small time savings in transport appraisal (Mackie, Jara-Díaz and Fowkes 2001, `mackie_2001_small_time_savings`, recalled) |
| k, share who keep it on and feel it | 0.050 | 0.15 | 0.30 | share | judgement; no source found. It shares P with a, and the two highs sum to 0.70 |
| f, stops a year | 1,000 | 2,500 | 5,000 | per driver | judgement |
| m, micro-life-years a felt stop | 0.00016 | 0.0038 | 0.095 | micro-life-years | 1, 4 or 15 felt seconds (judgement; the restart is "a split-second lag in acceleration", `ap_2026_epa_start_stop_credits`, line 135) × the weight × 1.901 |

3.3.2. Those who turn it off, middle: 7.2e7 × 0.27 × $14 = $270 million. Low: 2.4e7 × 0.15 × $0.20 = $0.72 million. High: 1.4e8 × 0.40 × $44 = $2.5 billion. The same share, 0.27 at the middle, lowers the credit's fuel saving.

3.3.3. Those who keep it on and feel it. Their felt cost per driver-year is $0.097, $5.8 or $290, capped at c: $0.097, $5.8 or $44. Middle: 7.2e7 × 0.15 × $5.8 = $63 million. Low: 2.4e7 × 0.050 × $0.097 = $0.12 million. High: 1.4e8 × 0.30 × $44 = $1.9 billion.

3.3.4. The total is $330 million a year, with a range of $0.84 million to $4.4 billion. Four fifths of the middle is the cost of pressing the button, and c, at 220 times its low, is the big part. Depth goes to the time a press really takes.

3.3.5. The second method: no stored source. A stated-preference study of the feature would serve.

3.3.6. The row leaves out fuel saved, the idling noise and fumes spared to people at the curb (type T8), and the feeling of being overridden.

3.4. A gain and a loss: going out after a smoke-free law (Nevada, after its 2006 law). Those who enjoy going out more and those who enjoy it less are two effects of opposite kind that both happen (the `fermi-estimator` rule 6.2). Each is capped at what its remedy costs (2.4.2, 2.4.5).

| Factor | Low | Middle | High | Unit | Source |
|---|---|---|---|---|---|
| P, adults who meet the law's result | 1.8e6 | 2.0e6 | 2.2e6 | adults | judgement, not stored; the survey sampled all adults, so P is all adults and the shares carry who goes out |
| s_w, share for whom going out became more enjoyable | 0.45 | 0.50 | 0.55 | share | "50% of respondents feel that going out has become more enjoyable" (`snhd_2008_clean_indoor_air_survey`, line 34); low and high, the sampling error of "A total of 400 adult telephone interviews" (line 24, inference). The surveyor is a health department, a party with a stake |
| s_l, share for whom it became less enjoyable | 0.080 | 0.11 | 0.14 | share | 11 percent (`snhd_2008_clean_indoor_air_survey`, lines 145-160); low and high, the sampling error (inference) |
| f, outings a year | 12 | 50 | 150 | per adult | judgement |
| m, micro-life-years an outing | 0.048 | 1.1 | 23 | micro-life-years | 5, 20 and 60 felt minutes of cleaner air (judgement) × the weight × 1.901 |
| c_w, the cost of a smoke-free outing before the law | 6 | 100 | 750 | $ a person-year | judgement: $0.50, $2 or $5 an outing for a less-preferred venue or a non-smoking section, × the outings. Where no smoke-free option existed, the cap does not apply |
| c_l, the cost of stepping outside to smoke | 15 | 210 | 1,700 | $ a person-year | judgement: 5, 10 or 20 minutes an outing at $0.25, $0.42 or $0.58 a minute, × the outings |

3.4.1. The felt value per person-year, f × m × $0.61, is $0.35, $35 or $2,100, for a pleasant outing or an unpleasant one of matching intensity (a judgement, 6.4.4).

3.4.2. The gain: those who enjoy it more, valued at no more than c_w: $0.35, $35 or $750. Middle: 2.0e6 × 0.50 × $35 = $35 million, or 57 life-years. Low: 1.8e6 × 0.45 × $0.35 = $0.28 million. High: 2.2e6 × 0.55 × $750 = $0.91 billion.

3.4.3. The loss: those who enjoy it less, mostly smokers, valued at no more than c_l: $0.35, $35 or $1,700. Middle: 2.0e6 × 0.11 × $35 = $7.7 million. Low: 1.8e6 × 0.080 × $0.35 = $0.050 million. High: 2.2e6 × 0.14 × $1,700 = $0.52 billion.

3.4.4. The net at the middle is $27 million a year. The total tool combines the two effects' ranges.

3.4.5. The second method: willingness to pay for smoke-free venues, stated or revealed by the choice of venue. No source is stored.

3.4.6. The rows leave out the health stream and relief from fear of the health risk, which belongs to the value of a statistical life (2.6.5).

3.5. What the four show. Each felt episode is worth thousandths of a micro-life-year to a few. Totals in the middle are tens to hundreds of millions of dollars a year, because the episodes are counted in billions. The two revisions changed the results as follows:

| Example | First draft | First revision | Now | What moved it |
|---|---|---|---|---|
| Weak shower | $380 million ($7.0 million to $21 billion) | $390 million ($0.50 million to $65 billion) | $400 million ($0.50 million to $5.3 billion) | the weight five times higher at the middle; only people whose shower the rule changed are counted; the remedy cap; then the share with no usable remedy and their felt cost judged together |
| Second flush | $57 million ($0.87 million to $11 billion) | $31 million ($0.070 million to $2.4 billion) | $31 million ($0.055 million to $7.9 billion) | the rule's share; then renters, who cannot replace a toilet, left uncapped |
| Engine stop | $35 million ($0.47 million to $3.6 billion) | $330 million ($7.7 million to $4.4 billion) | $330 million ($0.84 million to $4.4 billion) | those who turn it off counted at the button's cost; then that cost's low near zero |
| Smoke-free outing, Nevada | none | net $27 million ($0.19 million to $2.2 billion) | gain $35 million ($0.28 million to $0.91 billion); loss $7.7 million ($0.050 million to $0.52 billion); net middle $27 million | the gain counted on the same scale; then the gain and the loss as two effects, each capped by its remedy |

## 4. His fairness question: does anyone report feeling pleased when they meet a rule's effect?

4.1. The answer. Yes, where the rule's result is itself pleasant, and then more people may report a gain than a loss. After Nevada's smoke-free law, half of adults said going out had become more enjoyable and 11 percent said less (3.4). Pride is real and measured in money, of either sign, where an act is visible (1.8.2). No report was found of pride or joy at a rule whose effect is an inconvenience borne for a distant benefit, such as an engine stopping at a light or a low-flow fixture.

4.2. The search may be uneven. People volunteer complaints more than praise, and no survey found asked drivers whether they like the stop. So the lack of reports is weak evidence of no pride; a balanced question (2.5.1) is how a case would find out.

4.3. What was searched (2026-11-14, in general terms only): pride or joy at efficiency regulation, and warm glow; drivers who like stop-start; satisfaction with smoke-free laws; feeling good about low-flow fixtures; reassurance from food labels, seat-belt laws and smoke alarms; support for bag charges and congestion pricing before and after they started; the happiness studies of smoking bans and cigarette taxes; and conspicuous conservation.

4.4. What was found, strongest first:

4.4.1. Enjoyment of a smoke-free law (felt, both signs, one survey). By group, going out became more enjoyable for 58 percent of non-smokers and 19 percent of smokers, and less enjoyable for 4 and 40 percent (`snhd_2008_clean_indoor_air_survey`, lines 145-160).

4.4.2. Pride and shame in money (felt, both signs, field and online experiments). Public recognition gives image gains to high performers and losses to low performers (`butera_2022_shame_pride`, lines 241-243).

4.4.3. Life satisfaction and smoking bans (felt, measured, mixed). Across 40 European countries and regions, "smoking bans are not related to subjective well-being, but increase the life satisfaction of smokers who recently" tried to quit and failed (`odermatt_stutzer_2013_smoking_bans`, lines 62-64). The rise is "0.03 to 0.08 points" on a four-point scale (`odermatt_stutzer_2013_smoking_bans`, lines 921-923). For likely non-smokers, "a negative correlation between the introduction of a smoking ban and subjective well-being is measured" (`odermatt_stutzer_2013_smoking_bans`, lines 786-788). On taxes, "excise taxes make predicted smokers happier" (`gruber_mullainathan_2002_cigarette_taxes`, line 44). The later paper disagrees with that result (`odermatt_stutzer_2013_smoking_bans`, lines 176-178).

4.4.4. Warm glow (felt, correlational, about one's own choices). A meta-analysis finds pro-environmental behavior related to well-being, "(overall r = .243)", and most strongly "for warm glow (r = .408)" (`zawadzki_2020_pro_environmental_wellbeing`, lines 93-99). The glow attaches to a person's own choice (Andreoni 1990, `andreoni_1990_impure_altruism`, not stored).

4.4.5. A mandate may remove both the glow and the signal people pay for. The green image of a hybrid car is worth "between $430.45 and $1,291.34" to buyers in Washington and "between $1,402.84 and $4,208.53" in Colorado (`sexton_2011_conspicuous_conservation`, lines 968-972).

4.4.6. Support that grows once a rule is in force (attitude, not feeling). Stockholm's congestion charge had support that "had fallen to 36%" before the trial, then "increased to 52%" once it started, and reached "66% support" later (`borjesson_2012_stockholm_five_years`, lines 1168-1200). After England's bag charge: "All demographics increased their support for the policy in the 1-month period after the charge was introduced" (`thomas_2019_bag_charge`, line 252).

4.4.7. Stop-start. The only favorable report comes from a battery maker's focus groups held before people had used the feature: "Most of the respondents said they liked the idea of saving on fuel costs" (`cbs_2012_start_stop_acceptance`, line 268).

4.4.8. Reassurance from food labels, seat belts and smoke alarms. Polls show support for such rules but do not measure reassurance; no source found.

## 5. The eight types

The 18 voices of the first draft fold into eight types (the referee's finding 8). `notes/felt_effects.toml` holds one row for each, with its chain, weight, remedy, second method, overlaps and the evidence for its share. The list is open: a new type is a new row.

| Type | What it is | Side it can fall on | First draft's voices folded in |
|---|---|---|---|
| T1 worse performance, each use | irritation each time a product works worse because of the rule, or relief when it works better | either | users of a worse product; later buyers (a date, below) |
| T2 being overridden | displeasure at a lost choice, consent or control, apart from the product | against a rule that removes a choice; for its repeal | people overridden; renters; groups who read a rule as contempt |
| T3 enjoyment of the rule's result | pleasure, relief or reassurance from what the rule changes, and the dislike of those who preferred the old state | either | people who enjoy the result; people reassured |
| T4 relief from a commitment device | higher life satisfaction for people the rule helps keep a resolution | for the rule | the same |
| T5 lost warm glow or signal | pride of conserving by choice, or its signal, which a mandate makes common; dismay of those who value a repealed rule's goal | either | conservers; people who value the goal |
| T6 a lost function for disabled people | a substitute fails someone whose body needs the old product, or a rule restores a function | either | the same |
| T7 the burden of the rule's process | the psychological cost of paperwork, waiting or a procedure, apart from its time | either | people who handle paperwork; workers who enforce face to face |
| T8 neighbors' exposure | annoyance or lost sleep from noise, smell or light the rule adds or removes nearby | either | the same |

5.1. Three of the first draft's voices are modifiers of any row, not types:

5.1.1. Low income is the case's distributional weight, applied once.

5.1.2. Children and others who are not surveyed are measured by proxy reports.

5.1.3. Later buyers are the same row at a later date, after products change.

5.2. Two voices are ordinary streams the listers already find: symptoms from a mandated technology are a health stream, and a lost pastime is lost consumer surplus.

## 6. What was installed, and why

6.1. The table. `notes/felt_effects.toml` holds the eight rows of section 5 as data, each on one screen. This puts knowledge into data (CORE 6.1): a new type is one more row, and no seat gains a rule it must apply to everything.

6.2. Two seat definitions. Words were counted with `wc -w` on the files before and after.

6.2.1. `.claude/agents/effects-lister.md`, angle 3.1 (groups). For each group, the lister also asks how it experiences the policy day to day, pleasant and unpleasant. No angle of the lister asked how a person feels, so reassurance and relief went unraised (1.15).

6.2.2. `.claude/agents/fermi-estimator.md`, a new item 11. A felt effect is estimated by its type's chain in the table, with the row's remedy cap and second method. The estimator whose task includes the pooled list's first effect also checks the list against the table's types. Each type the list lacks gets a rough estimate, or a reason it does not apply, in one line covering all such types. That makes the check run once per case with no change to how estimators are dispatched.

6.3. Simpler choices rejected, and why:

6.3.1. A sentence in every brief asking seats to consider all voices fairly. This is the "verbiage" the owner rejects. Estimators would have no weight to apply and would still set the effects to zero.

6.3.2. A new seat, a felt-effects auditor. It adds another handoff to every case, for a check the estimator can do while it reads the table.

6.3.3. A fourth lister, or the eight types sent to the listers as angles. The groups angle already names each group, so one clause there is cheaper. Listers have no Read tool, and the estimator's check catches a type they miss.

6.3.4. Weights chosen afresh in each case. Cases would disagree on the same weight with no record of why.

6.3.5. One line for each absent type, as the first draft proposed. One line for all of them shows the same thing.

6.4. What a referee would attack now, first to last:

6.4.1. The weight per felt minute is still not measured. Three sources bracket it, and its middle of 0.03 is a judgement. A study of experience sampling or stated preference for one product would settle it for that product.

6.4.2. The share with a usable remedy, and the felt cost that would send a person to find one, decide the shower row. No source gives either.

6.4.3. The high of a row with no usable remedy is a merged judgement (2.4.3), such as $50 a person-year for the shower. A referee may ask what it rests on.

6.4.4. Matching intensity for pleasant and unpleasant minutes. For non-market goods, willingness to accept runs well above willingness to pay (Horowitz and McConnell 2002, `horowitz_mcconnell_2002`, recalled). So a gain and a loss of the same felt size may not carry the same weight.

6.4.5. Health weights for welfare: "annoyance is not a disease in itself" (`defra_2014_noise_valuing_impacts`, line 728). The weight factor now draws on willingness to pay as well.

6.4.6. Shares from parties with a stake: an insurer, a battery maker, a health department and a water district. Each is recorded with its role and stake.

6.4.7. The US precedent. The FDA counted consumers' lost pleasure as an offset in its tobacco analyses, and economists criticized it (Cutler, Jessup, Kenkel and Starr 2015, `cutler_2015_happiness_offset`, recalled). A US referee will ask how a felt-effects row differs from that offset. The answer: the offset subtracts the pleasure of an addictive good from a health gain, while T1 counts a felt change in a product's performance. Where a rule acts on an addictive good, the same critique applies.

6.4.8. The word. The public name of the stream is the owner's to choose from candidates: "felt effects", "everyday hassles and pleasures", or his "microaggressions".

## 7. Sources

7.1. Stored in `research/sources/<key>/`, each with an entry in `research/refs.toml`. Five of them are the abstract or a summary page only (marked):

7.1.1. Noise and disability weights: `who_2011_noise_burden`, `defra_2014_noise_valuing_impacts`, `haagsma_2024_noise_disability_weights`, `salomon_2015_gbd_disability_weights`, `benmap_ce_2017_appendices`.

7.1.2. Wellbeing, time and adaptation: `hm_treasury_2021_wellbeing_guidance`, `kahneman_2004_drm` (abstract), `kanner_1981_hassles` (abstract), `loewenstein_ubel_2008_hedonic_adaptation`, `epa_2020_valuing_time_use`, `dft_2024_tag_m3_2`.

7.1.3. Microaggressions, reactance and sludge: `sue_2007_microaggressions` (abstract), `lilienfeld_2017_microaggressions` (abstract), `steindl_2015_reactance`, `oecd_2024_sludge_audits`.

7.1.4. Willingness to pay of either sign: `allcott_kessler_2019_nudges`, `butera_2022_shame_pride` (both NBER working papers).

7.1.5. Efficiency standards: `gayer_viscusi_2012_overriding` (a summary page), `houde_spurlock_2015_standards_quality`, `brucal_roberts_2019_standards_hurt`.

7.1.6. Showers and toilets: `mwdsc_1999_ulft_survey_supplyht`, `ballanco_2000_pmmag_ulft`, `koeller_2003_dual_flush`, `nbs_1982_showerheads`, `mowris_2010_showerhead_satisfaction`, `epa_watersense_2010_showerhead_support`.

7.1.7. Stop-start: `directline_2024_in_car_tech`, `ap_2026_epa_start_stop_credits`, `cbs_2012_start_stop_acceptance`.

7.1.8. Positive effects: `snhd_2008_clean_indoor_air_survey`, `odermatt_stutzer_2013_smoking_bans`, `gruber_mullainathan_2002_cigarette_taxes`, `zawadzki_2020_pro_environmental_wellbeing`, `sexton_2011_conspicuous_conservation`, `thomas_2019_bag_charge`, `borjesson_2012_stockholm_five_years`.

7.1.9. Disability: `green_2023_disabled_short_straw`.

7.2. Cited but not stored, each with its reason in `research/refs.toml`:

7.2.1. Refused or closed when fetched: `kahneman_krueger_2006_measurement`, `frey_benz_stutzer_2004_procedural_utility`, `andreoni_1990_impure_altruism`, `vanclay_2003_sia_principles`, `wright_2009_temporary_health_states` (abstract read), `dot_2016_value_of_travel_time`.

7.2.2. Recalled: `herd_2018_administrative`, `kahneman_knetsch_1992_valuing`, `kahneman_wakker_sarin_1997`, `koszegi_rabin_2006`, `courant_porter_1981`, `bartling_fehr_herz_2014`, `iso_ts_15666`, `hu_pavlou_zhang_2009`, `horowitz_mcconnell_2002`, `cutler_2015_happiness_offset`.

7.2.3. Seen in a search result only: `tomberg_2024_showerheads`.

7.3. Not found at all:

7.3.1. a removal rate for flow restrictors;

7.3.2. sales of devices that defeat stop-start;

7.3.3. a balanced survey of current showerhead users;

7.3.4. a market or stated value of shower force or flush performance;

7.3.5. the share of people who know of a remedy.

## 8. The referee's findings, and how each was answered

8.1. Finding 1, the remedy is a cap. Accepted (2.4). One change: the rule's benefit falls only where the remedy undoes the rule. A better compliant product, such as a stronger-feeling head or a better toilet, keeps the water saving, so its users lower nothing.

8.2. Finding 2, two chains that are one. Accepted. The weight is one factor from three sources (2.3), and the waiting premium is applied to in-vehicle time (1.10). The truly independent second method is named for every type. For the three worked examples, no stored source supplies it, so each says so rather than present a chain made of judgement alone.

8.3. Finding 3, counting people whose product the rule changed. Accepted: P in every example.

8.4. Finding 4, one scale. Accepted (2.8, 3.4). The table has no "scale" field. Matching intensity across gains and losses is stated as a judgement a referee may attack (6.4.4).

8.5. Finding 5, the order of evidence for the share. Accepted with one change. The referee put measured behavior first. That holds for the share who use a remedy and for frequency. For the share who feel an effect, behavior gives only a floor. In Allcott and Kessler, the share who would pay anything to stop the reports was many times the 1 percent who opted out (2.5.2). So a balanced probability sample comes first.

8.6. Finding 6, "overridden" is a bound. Accepted, with one addition. A laboratory measure separates the value of a decision right from its outcome (1.11.3), so a case may price the row by a transfer marked as judgement instead of leaving it a bound. The round-2 condition is met: the transfer is a share of the T1 value for the same people, sharing T1's factors by name (1.11.3; the table's T2 row).

8.7. Finding 7, the owner's four factors. Accepted (2.1).

8.8. Finding 8, eight types. Accepted (section 5). The first draft's row for workers who enforce face to face, which the referee did not place, goes to T7.

8.9. Finding 9, an audit of the tool done once. Accepted, and made a standing check: one line per case for all the absent types, made by one estimator (6.2.2).

8.10. Finding 10, no stance in each case on summing tiny harms. Accepted and deleted. Summing small values is the convention of cost-benefit analysis, and a case's methods appendix states it once.

8.11. Not accepted: the referee's 5.6, which would send the types to the listers as angles. The reasons are in 6.3.3.

8.12. The referee's round 2, and how each point was answered:

8.12.1. R2.2.1, the Allcott and Kessler figure. Corrected in 1.8.1, 2.5.2 and 8.5: weakly negative includes zero, and most of that group is close to indifferent.

8.12.2. R2.2.3, being overridden as a share of T1. Done in 1.11.3, 1.14.3 and the table's T2 row.

8.12.3. R2.3.2, renters. In the toilet example, renters are the share with no usable remedy and stay uncapped. The high rises from $2.4 billion to $7.9 billion; the middle is unchanged.

8.12.4. R2.3.6 and R2.5, the remedy rule. It sits once in the table's header, in the referee's exact words, and T1's field lists its remedies only. The note's 2.4 states the same split.

8.12.5. R2.4.1, opposed extremes in the shower's high. The share with no usable remedy and their felt cost are judged together (2.4.3, 3.1.2). The high falls from $65 billion to $5.3 billion.

8.12.6. R2.4.2, two shares that split one share. The usable-remedy share is the complement of u (`complement_of`) in every example.

8.12.7. R2.4.3, gains need the same cap. Both sides of the smoke-free example are capped: the gain at what a smoke-free outing cost before the law, the loss at stepping outside (2.4.5, 3.4). They are now two effects of opposite kind rather than one net share.

8.12.8. R2.4.4, the button's cost. Its low is $0.20 a driver-year, and the row's depth goes there (3.3.4).

8.12.9. Not taken: none. One note on R2.4.4. The middle stays at two seconds a trip at the full value of time, as UK practice values small savings; only the low reaches near zero, as the referee asked.
