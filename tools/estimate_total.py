"""tools/estimate_total.py — the total of a case's table of estimates.

    .venv/bin/python tools/estimate_total.py [--quiet] [--draws] [--out DIR] cases/<case>/estimates.toml

Reads the table of notes/fast_estimate.md section 3, prints a plain table to two significant
figures and writes the same numbers, every digit kept, to results/estimate_total.json beside the
table, or with --out to DIR/estimate_total.json (DIR created if missing, nothing written beside the table).
A refusal exits 1, names the factor or effect, and leaves no results file (The draws files, below). With --quiet it prints
the totals and, of the effects, only the ten of largest expected value and the ten of largest share
of variance; every other line, the section on effects that can go either way included, prints in quiet
mode too; the file is the same.

A chain's low and high are the least and greatest of the 2^k products formed by taking each of its k
factors at its low or its high, and its middle is the product of their middles, computed here; with
every factor positive these are the products of the lows and of the highs. A stated low, middle or
high is a check on the hand arithmetic and nothing else, set against the least corner, the product of
middles and the greatest corner: more than SLIP of that number's size from it, it is refused; more
than SAME, the number takes its place, and the run counts the blocks so restated. Where the number is
exactly zero only a stated zero passes. An effect may state none.

Method. Each factor is drawn from one standard normal Z per draw, in two halves joined at the middle,
s = s1 for Z < 0 and s = s2 for Z >= 0, so its low, middle and high are its 5th, 50th and 95th
percentiles for any skew (z95 = 1.6449). Its `form` is one of four:
  lognormal, a positive quantity: X = middle * exp(s Z), s1 = ln(middle/low)/z95, s2 = ln(high/middle)/z95:
    a two-piece lognormal joined at the median, half the mass on each side, its density stepping there; a departure from Wallis's
    two-piece form (2014), which joins the halves at the mode. The high is passed one draw in twenty and the tail runs
    on beyond it uncapped.
  normal, a quantity that can be negative: X = middle + s Z, s1 = (middle - low)/z95,
    s2 = (high - middle)/z95.
  logit-normal, a chance or a share: X = 1/(1 + e^-(L + s Z)), L = logit(middle), s1 = (L - logit low)/z95,
    s2 = (logit high - L)/z95.
  bernoulli, a fact that is so or not, drawn whole in two stages: in each draw its chance, a logit-normal from
    its low, middle and high on the factor's own stream, then the fact, 1 where a second uniform number of its
    own (the stream named by the factor's name followed by FACT, " (so or not)") is below that chance, and 0
    otherwise. It is never a default. Its low, middle and high still give a chain's corners and check a stated
    value, so for it they check the arithmetic only; the effect's range is its p05 and p95.
Every mean the tool reports is the mean of the draws, with its Monte Carlo standard error, the draws' standard
deviation over the square root of their number (`outputs.standard_error` of the engine); no mean is computed by
formula. The JSON's `factors` gives each factor drawn, a complement included, its form (a complement's that of the
factor it complements) and the mean and standard error of its draws; its `method` states in words how each form
turns three numbers into a distribution and what it implies beyond them, the draw count, seed and sampling, how
means, shares of variance, dependence and sets are computed, for `documents.method_tables` to print.
A named form always wins. With none, a factor of unit "probability", or of a share (unit "share" or beginning
"share "), is a logit-normal; any other factor is a lognormal where its low is above zero and a normal where it
is below. A chance (unit "probability") may name logit-normal or bernoulli only.

A named distribution. In place of low, middle, high and form, a factor (in a row or a [factors.<name>] entry) may
carry `distribution` and that family's fields, exactly as an engine input does (cases/README.md, "An input"; the
fields `distributions.fields` gives, an unknown one refused naming it, a missing required one refused): a quantity
whose shape has a source, such as a fat-tailed event size following a power law. It is drawn by the engine's
`distributions.quantile` on the factor's own stream, so a model input of the same name and specification has the same
draws, draw by draw. Its low, middle and high, wherever the tool uses or reports them (a chain's corners, the check of
a stated value, Annex A), are its 5th, 50th and 95th percentiles computed by that `quantile`; its form in the JSON is
the family's name, and the JSON's `factors` adds its `parameters` and computed `low`, `middle` and `high`. A family
whose mean is infinite or undefined is refused by the engine's own check, since no mean of draws estimates it. An
`empirical` reads its `data_file` relative to the table's folder, by the engine's reader, which refuses a file outside
that folder and a file that is not valid CSV (a blank line among them). A factor of unit "probability" naming a family
is refused, naming it, where that instance's support (`distributions.support`) is not within [0, 1], so neither it nor
its complement can draw outside [0, 1]: a beta or uniform with 0 <= min < max <= 1 passes, a lognormal or a normal never.
A factor stating both forms, or neither, is refused.
Where `inputs.toml` stands in the table's folder, a named-family factor sharing the name of one of its inputs (a
top-level table with a `distribution`) must state the same `distribution` and the same value of every field of that
family; one that differs is refused.

Keys. Top-level: effect, factors, lever, and the frame keys of "Who gains and pays, time and money" below. An [[effect]]
row: name, kind, who, group, start, years, factor, policy (or option), draws, weight, model, low, middle, high. A `bound`
key, an effect left outside the total, is refused: an effect no source reaches is estimated as a judged chance and size
and counted (.claude/agents/fermi-estimator.md, rule 9). A row's factor: name, unit, low, middle, high, form, source,
currency, price_year, complement_of. Any other key is refused, naming it, so a misspelt key never passes as absent.
Z is the inverse normal CDF of the factor's own stream of uniform numbers, `sampling.uniforms` of the
engine under the factor's name, so a factor's draws depend only on its name, the seed, the count and
the sampling method, and a model input of the same name run by the engine at the same seed, count
and method has the same uniform numbers, draw by draw: where the factor names the input's own distribution and
parameters, one quantity is drawn once and used in both.
A factor name is one quantity across the table: the same name with a different unit, low, middle,
high, `form`, `distribution` or field, or `complement_of`, as written, is refused.

Factors stated once. A table may hold top-level tables `[factors.<name>]`, each with unit, low, middle and high,
or unit and a `distribution` with its fields, and optionally form (with low, middle and high), source (a string that changes no number), currency and price_year; any other key is refused, and so is a top-level
`factors` that is not a table of tables. A row's factor
`{ name = "<name>" }` is that entry. A row's factor that also states unit, low, middle, high or form passes where each
equals the entry's and is refused where one differs or the entry has none; a complement whose name has an entry is
refused so. A complement whose base is in no row but has an entry draws that entry. A factor with no entry, no complement_of and no unit, low, middle and high is refused, naming it. An entry
no row uses is not drawn and changes nothing.

The complement. A factor stated with `name` and `complement_of` alone is 1 minus the named factor, a
chance (unit "probability" or form logit-normal), a whole-drawn fact included, draw by draw; its low, middle and
high, for the corners, are 1 minus the named factor's high, middle and low. A complement of a factor not in the
table, of one that is not a chance, of another complement, or with values stated is refused. A factor and its
complement may share a row: the row's draws are their product draw by draw.

The other refusals, each naming the factor: a low above the middle or a middle above the high; a low
equal to the middle with a different high, or a middle equal to the high with a different low (all
three equal is a fixed quantity and passes); a probability's middle above 1; a low of exactly 0 with
no form, on a factor that is not a chance or a share; a named lognormal with a low at or below 0; a normal whose
high is at or below 0; a logit-normal (or a chance or share with no form) whose low is at or below 0 or whose
high is at or above 1; a bernoulli whose unit is not "probability", or whose low is at or below 0 or high at or
above 1; an unknown form; a chance named lognormal or normal; an unknown key; a factor whose name is a bernoulli's name
followed by FACT, which would share that fact's second stream.

Rows of one effect name are chains; each draw picks one by weight (a numpy generator at the seed). Each
chain counts in its own row's direction, and an effect whose chains differ in kind reports kind "mixed",
each chain in the output carrying its own kind. An
effect's expected value is the mean of its draws, and the total's the mean of the total's draws, each with its
`standard_error`; its median, interval, chance of being positive (with `chance_positive_se`, the standard error of a
share of draws) and the variance shares (each effect's covariance with the total over the total's variance, an
allocation that sums to one; for an effect that shares no drawn quantity with another, its main-effect variance, the
value of perfect information under squared-error loss, Oakley and O'Hagan 2004, 2.5.2) come from the draws, as do each effect's median,
90 per cent interval (`p05`, `p95`), share of draws strictly above zero, mean on each side of zero (null where it has
none) with `mean_if_above_se` and `mean_if_below_se`, and `signed`, true where some draws are above zero and some below.
Each share's `variance_share_se` (null where the share is) is the standard deviation of the share over BATCHES (10)
non-overlapping batches of the draws over the square root of their number. Every total of effects (that of a table
with no policy, each option's, the leading set's, written as `leading_set`) writes and prints `shared_factors`: each
drawn quantity that two or more differently named effects of it rest on (a factor of a chain, the chance a complement
is one minus, a row's start or years with the drawn rate that discounts it, and, where the weighted total leads, the
incomes and elasticity of a group's weight), with its main-effect index Var(E[total | factor]) / Var(total) by the
engine's 50-bin fit (`value_of_information.main_effect`) and its batch `standard_error`. Every total of effects also
carries `comonotone`, the case in which every effect moves together: the 5th and 95th percentiles and chance positive of
the sum of each effect's sorted draws, whose percentiles are the sums of the effects' own; it is the widest spread
in the convex-order sense, not a bound on a percentile or on the chance positive, which other dependence can move
further; it is printed on a line of its own and cannot move the mean. An effect is flagged, with its tail share, where its expected value exceeds three
times its middle in size, unless zero lies inside its 90 per cent interval, where a ratio to a middle
that may be near zero means nothing; a signed effect's tail share is always given. The tail share is the sum of |value| over the draws whose |value| is above the 95th percentile
of |value|, over the sum of |value|. `removable_benefits` counts the effects of positive expected
value, largest first, removed while the total's expected value stays at or above zero, each effect's value taken as the
total leads (weighted where the weighted total leads); an effect's own figures are in dollars.

Policies and levers (roadmap R15). A row may carry `policy`, the name of the policy it belongs to, or a
list of two or more names, a joint row that counts only in a set holding every policy it names: an interaction between
policies is stated as data, a row of its own. A row with no policy counts in every set that holds a policy and never in
the base (the set of no policy), which is the world without action (OMB Circular A-4's baseline), so the base's net
benefits are zero in every draw and every set's are its change from the base; a cost every acting set bears is such a
row. A table with no policy anywhere is one total of every row, as above. A top-level `[lever]` maps a lever's name to the
list of its levels, each a policy some row names (`scale = ["small", "large"]`); a set holds at most one level of each
lever, and a policy in no lever is on or off on its own. Rows are chains of one effect where they share both name and
policy; a name with and without a policy is refused, since its rows would be counted twice. A set's outlay is the net cost
to the groups marked public, at the leading reading, below.
`option`, the older name, is a policy of one lever: a table of `option` rows is read as the lever `option` whose
levels are the option keys, and may not also use `policy` or `[lever]`.

Every factor is drawn once per draw for the whole table, and an effect name with several chains picks its chain on one
uniform number per draw whatever the set, so every set is evaluated on common draws and a difference between two sets
is the difference of the policies alone. Where the allowed sets number at most ALL_SETS (1,024: ten free policies, or
the product over levers of one more than their levels, times 2 for each free policy), every one is evaluated. Above
it: the base, every policy alone and every allowed pair; then the nested sets that add, best first, each policy whose own
rows (those of that policy alone, not joint and not of no policy) have positive expected value, skipping a second level
of a lever, so a cost that every acting set bears does not stop the search at the base; then from the best set
so far, the one change (adding a policy, its lever's level replaced, or removing one) that most raises the expected net
benefits, repeated until none does. That search finds the best set wherever policies only add, and may miss one whose
value lies in a combination of three or more policies of low value alone. The JSON reports `sets`, each evaluated set
once with its policies, outlay (with `outlay_standard_error`) and total; `enumeration`, how many sets are allowed and
evaluated; `added`, each policy's expected net benefits added to the base; `leading`, the evaluated set of highest
expected net benefits, and `removed`, each of its policies' expected net benefits lost by removing it;
`interactions[p][q]` = NB(p + q) - NB(p) - NB(q) + NB(base), both orders, for every pair that can share a set; and
`frontier`, the sets no other evaluated set beats on both counts (outlay at most and expected net benefits at least its
own, one strictly), by ascending outlay, each with its set's total's `standard_error`; Pareto dominance only, no
extended dominance. Each of `added`, `removed` and `interactions` is the mean of the per-draw difference on the common
draws, worked row by row (each row's draws times the net count of the sets it enters), so a difference no row enters,
such as the interaction of two policies with no joint row in a table whose every row has a policy, is exactly zero;
`added_se`, `removed_se` and `interactions_se`, of the same keys, are those differences' own standard errors.
`value_of_information`, written for every table of policies that is not one lever, and printed after the frontier,
holds, at the leading reading: `expected_loss`, the mean over draws of the highest net benefits of any evaluated set
in that draw minus the leading set's, the expected opportunity loss of choosing the leading set, equal over those sets
to the expected value of perfect information (Raiffa and Schlaifer 1961; Claxton 1999; Briggs, Claxton and Sculpher
2006, ch. 6), with `expected_loss_se`, that per-draw difference's standard error; `evppi`, for each uncertain quantity
(one whose draws vary) that a row of any evaluated set rests on, shared or not, keyed by its factor's name, the
engine's `evppi` (its default "bins" fit) over the evaluated sets' draws keyed by that quantity's draws, the value of
learning it before choosing a set, printed largest first, the ten largest with a count of the rest; and
`over_all_sets`, true where every allowed set was evaluated. Where the search ran, both are over the sets evaluated, so each is a lower bound on its value over
every allowed set measured against the leading set (another set can only raise a draw's or a bin's highest), and the
printed text says so.

A table of one lever (the `option` form, or policy rows all levels of one lever) also writes what it always did: each
level totalled apart, over its own effects and those with no policy, under `options`, with no total across levels; and
on the common draws how often each level's total is the highest (`highest`, a tie counting for each, with `highest_se`,
each share's standard error) and, for each ordered pair, how often the first's total is above the second's (`beats`).

A row with `draws` names a plain-text file of its model's draws, its path relative to the table's
folder, written by `sampling.write_draws`: a first line "# seed S iterations N sampling M", then one
value per line, as values in the row's direction: a positive value counts as the row's kind says, a
negative one the other way. Every file's header must agree, and the
whole table is then drawn at that seed, count and method, draw i of the effect being line i of its
file, with no resampling. A file with no header, a header unlike another file's, or a count of
values unlike its header's is refused. With no `draws` row the table is drawn at seed 20261110,
200,000 draws, by independent (monte_carlo) streams. The effect's expected value is the file's mean;
its factors are still checked, as the estimate the model replaced, and enter no total. A yes-or-no fact (form
bernoulli) the modelled effect depends on is two of the model's inputs, drawn on the table's random numbers as the
tool draws the fact: its chance, under the fact's name, with the factor's low, middle and high as its 5th, 50th and
95th percentiles; and the input named by the fact's name followed by FACT, kind uniform from 0 to 1; the model takes
the fact as yes in a draw where the second is below the first. A bernoulli factor, or its complement, on a `draws` row
is refused. A model input that its own model rank-correlates or draws as a mixture
of methods has its uniform numbers moved, so it is coupled to the table's factor less than fully.

Who gains and pays, time and money (the owner's rules 12 and 14 to 17, scope rule 1; the method audit's build 2).
  Groups. `[groups.<name>]` holds `income`, the name of a factor (a distribution with its source), and optionally
    `public = true`. Where the table names groups, every row names one by `group`, beside its free-text `who`. Where the
    rows fall in two or more groups, a dollar to group g weighs (y_ref / y_g)^e in each draw, y a group's income factor,
    `reference` the group whose money weighs 1 and `elasticity` the factor e, the income elasticity of the value of a
    statistical life, drawn once per draw for every group (Robinson, Hammitt and O'Keeffe 2019; Somanathan 2006). No
    elasticity is assumed: such a table without one is refused. A row whose chain holds a factor named in
    `common_values` (a value already at a common rate, such as the guidance's value of a statistical life) weighs 1
    (OMB Circular A-4, 2023, 10.e). The weighted total leads; `lead = "dollars"` sets the dollar total to lead instead,
    and a table whose rows sit in one group, or that names none, is unweighted and its dollar total leads. A transfer
    is two rows of the same named factors, which cancel draw by draw in dollars and count in the weighted total and
    in the account by group.
  Time. `year`, `currency`, `guidance = "<jurisdiction>/<edition>"` (jurisdiction_guidance/) and `discount_rate`, the
    name of the drawn discount rate's factor, come together. A row's `start` and `years` each name a factor: start
    alone is a one-off that many years after `year`; years alone a flat amount each year for that many years; both,
    a flat amount each year for `years` years after `start`; neither, a value now. Flows fall at the end of each year
    (OMB Circular A-94: the factor 1/(1 + i)^t), a fractional year interpolated linearly between whole ones. Each
    draw is discounted at its drawn rate, the leading reading, and again at every rate or schedule of the edition,
    each a reading on the same draws (`cost_benefit_engine.timeline.discount_factors`). A `draws` row in such a table
    names one file per reading, `draws = { "<reading's label>" = "<file>", ... }`, its model's present values at that
    reading; for the drawn reading the model discounts at the input named by `discount_rate`, drawn on the same
    random numbers. A table with none of the four keys is read as its rows state it, undiscounted, and refuses start
    and years.
  Public money. A set's outlay is minus the dollar total of the public groups' rows. `bar_group` names the group the
    same money would reach as cash (the owner's rule 16): the cash is worth, weighted, each public group's net cost
    times the bar group's weight less its own, and the JSON's `cash` gives it and the weighted total less it. `life_year`
    names the factor of a life-year's value in the reference group's money; each reading's `life_years` is the weighted
    total over its draw. A table whose weighted total leads and that names no `life_year` is refused, naming the key and
    what it is, the value of a statistical life-year; with bar_group set, a public group with no rows is refused by
    name. Where the edition has
    `[excess_burden]` (the United States: A-94's 0.25), its reading is the dollar total less that rate times the
    outlay, draw by draw; the weighted total takes none. Net benefits per public dollar is the leading total's
    expected value over the outlay's.
  Money. In a table with `year`, a money factor carries `currency`, the table's (another is refused until a case
    needs one), and `price_year`, and is multiplied once, wherever it is used, by the edition's `[price_index]` at
    `year` over its value at the factor's year; a unit that names a currency, money with one of the two keys, or a
    year the index lacks is refused (`cost_benefit_engine.case.unit_currency_matcher`). The index is read by the engine's
    reader (`case.price_index_years`), which refuses a year whose value is not a finite number above zero, naming it.
    Every row of factors in such a table is money: its chain holds exactly one factor with currency and price_year, and
    a chain with none or two is refused, naming the effect. The printed headings name the table's currency. A table with no `year`
    refuses the two keys. A chain's low, middle and high stay the estimator's hand arithmetic, unconverted and
    undiscounted; the flag's middle is converted and discounted at the middles.
The JSON's `readings` lists the leading reading first, then one per rate or schedule, each with `label`, `rate` (a flat
guidance rate, else null), `dollars` and `weighted` (null where unweighted); `lead`, `groups` (each group's `dollars`
and `weighted` at the leading reading), `outlay`, `excess_burden` (null where the edition has none) and
`per_public_dollar` (null where the outlay is zero) follow, of the whole table or of the leading set of policies. Each
set also carries its `per_public_dollar`. The effects and every total, set and draws file are at the leading reading,
and the sets are ranked on the leading total.

The draws files. With --draws (main's `draws=True`) the tool also writes each total's draws, the totals
from which it computes its summaries, to results/estimate_total_draws/<option key>.txt beside the JSON
(a table of one lever), <policies joined by +>.txt for each evaluated set (base.txt the base) of any other table of
policies, or total.txt for a table with no policy, each by `sampling.write_draws` at the run's seed, count and
method, the format a `draws` row reads. The flag changes nothing printed and nothing in the JSON. Each
run first removes any earlier JSON and draws folder, so the folder and the JSON come from one run and a refused table
leaves no results that no longer describe it. Under the flag a policy that is not one path component is refused, and so, where sets are written, is one holding +
or named base. Each set's draws are held until written, 1.6 MB a set at 200,000 draws.

"Its middle" for the flag is the weight-averaged middle of the effect's chains, each chain's middle carrying its sign.

Assembling a table (roadmap item 2.33), so that an author writes no code:

    .venv/bin/python tools/estimate_total.py assemble cases/<case>

reads cases/<case>/estimates/changes.toml, which the author writes, and writes cases/<case>/estimates.toml from the
estimators' files it lists. The changes file:

    files = ["scenarios.md", "programme.md"]   # the estimator files in estimates/, in table order

    [[change]]
    do = "replace"              # one value of a factor, in every file that states it
    factor = "<factor name>"
    key = "unit"                # unit, low, middle, high, form or source
    value = "probability"
    reason = "<why>"

    [[change]]
    do = "replace"              # one value of a row
    effect = "<effect name>"    # every row of that name ...
    file = "<file>.md"          # ... or, with file, only the rows from that file
    key = "weight"              # kind, who, group, start, years, weight, option, policy, low, middle or high
    value = 0.5
    reason = "<why>"

    [[change]]
    do = "drop"                 # remove the rows of an effect (optionally `file = ...` as above)
    effect = "<effect name>"
    reason = "<why>"

    [[change]]
    do = "merge"                # two effects become one: every row of A and B takes the name C
    effects = ["<A>", "<B>"]
    into = "<C>"
    reason = "<why>"

An estimator file's blocks are the lines inside its ```toml fences, read as one TOML document per file; a
`[factors.<name>]` entry in a file fills in that file's rows that give the factor by name alone. The rows follow the
order of `files`, and each file's its own order: that order decides which random number picks each effect's chain, so
a table built from the same files in the same order draws the same digits. The changes apply in order, then the table
is written. A factor that two or more files state is written once as `[factors.<name>]`, with its source where every
file gives the same one and otherwise on each row. A factor stated with a different unit, low, middle, high or form in
two places is refused, naming both files: an author resolves it with a `replace` of the factor, never by a silent pick.
Also refused, each naming what it refuses, and with no table written: a change without a `reason` or with a blank one;
a change naming an effect or factor no row states; an unknown `do` or key; a listed file that is missing or not TOML
inside its fences; and a file of estimates/ holding ```toml fences that `files` does not list, since its rows would
otherwise be left out unseen. A merge gives A and B half the weight each, shared among each one's own chains (of one
policy) by their weights, or equally where no chain of the effect states one; a chain that states none beside one that
does is refused, naming the effect and its file.

A case of packages that build on one another, each a table of its own (notes/briefs/author_fast.md 10.4), lists its
tables in the same changes.toml, and the command is the same:

    [[table]]
    path = "second_chain/estimates.toml"   # relative to the case folder; its folder is made if missing
    heading = "Second chain"                # the fences whose nearest Markdown heading above contains this text

A fence belongs to a table when the nearest heading line above it (a line beginning with `#`, outside any fence)
contains the table's `heading`, case as written. With any `[[table]]`, each table's `path` is written and no
cases/<case>/estimates.toml. Each table is assembled on its own, its rows in the order of `files` and each file's own
order; the check that a factor is stated alike, and the [factors] written once, hold within one table, so two packages
may state a factor differently. Every change applies in each table where it finds its effect or factor, and one that
finds nothing in any table is refused; so is a fence of a listed file that no table takes, naming the file. A refusal
writes no table at all. The assembled table is then read by this tool's total as any other table,
and its refusals (a `bound`, say, in a row the changes do not drop) are the total's.
"""
from __future__ import annotations

import itertools
import json
import math
import re
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Any, NoReturn, cast

import numpy as np
from numpy.typing import NDArray
from scipy.special import expit, ndtri

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # this tree's engine, whatever the venv points at

from cost_benefit_engine import distributions, sampling, value_of_information  # noqa: E402
from cost_benefit_engine.case import (CaseError, guidance_for, guidance_schedules, price_index_years,  # noqa: E402
                                      read_empirical, unit_currency_matcher)
from cost_benefit_engine.value_of_information import main_effect  # noqa: E402
from cost_benefit_engine.timeline import discount_factors  # noqa: E402
from cost_benefit_engine.outputs import standard_error  # noqa: E402
from cost_benefit_engine.documents import percent, separating_figures, significant  # noqa: E402

DRAWS, SEED, METHOD, TOP = 200_000, 20261110, "monte_carlo", 10
# SLIP: how far a stated low, middle or high may be from the product of its factors. The estimators
# multiply by hand and round to two figures (.claude/agents/fermi-estimator.md, How to think 5).
# One rounding to two figures moves a number by at most 5 per cent (10.5 written as 10 or 11), so 10 per
# cent holds a product rounded at its last step and once on the way. Hand rounding puts many stated
# values more than 1 per cent from the product and few beyond 5 per cent. A dropped factor, a wrong power of ten or a low put where a middle belongs moves the product by
# far more. A slip under 10 per cent passes unseen and costs nothing: the product is what the tool uses.
# A product rounded to one figure can be a third off (1.5 written as 2) and is refused.
# SAME: closer than this a stated value is the product written to five or more figures; it stands as
# written, so a table written from exact products reports what it always did, and its block does not
# count as restated.
SLIP, SAME = 0.10, 1e-4
ENDS = ("low", "middle", "high")
SHAPE = (*ENDS, "form")  # the judged form, stated in place of a named `distribution`
PERCENTILES = np.array([0.05, 0.5, 0.95])
# A mixture's quantile is not monotone in u (the engine picks its component by u's bracket), so its percentiles are read
# from its values at GRID, evenly spaced uniform numbers, each 1/100,000 of the mass: exact to that share of the mass.
GRID = (np.arange(100_000) + 0.5) / 100_000
NAMED = " (named distribution)"  # a named family's form in the JSON and the method, apart from the judged forms
MONEY = ("currency", "price_year")
ENTRY_KEYS = ("unit", *ENDS, "form", "source", *MONEY)
FACTOR_KEYS = ("name", *ENTRY_KEYS, "complement_of")
ROW_KEYS = ("name", "kind", "who", "group", "start", "years", "factor", "option", "policy", "draws", "weight", "model",
            *ENDS)
FRAME_KEYS = ("year", "currency", "guidance", "discount_rate", "elasticity", "reference", "common_values", "lead",
              "life_year", "bar_group", "groups")
TOP_KEYS = ("effect", "factors", "lever", *FRAME_KEYS)
# ALL_SETS: the most sets of policies evaluated one by one, every allowed set; above it the search of the header.
# Each set costs one sum of its effects' draws and four quantiles, about 20 ms at 200,000 draws and 50 effects, so
# 1,024 sets (ten free policies) take about 20 s, inside the minute a rerun should take (roadmap R15).
ALL_SETS = 1024
SHOWN = 10  # the quantities whose value of partial perfect information is printed, the largest
BATCHES = 10  # the batches of a share's or an index's standard error; a 10-batch error is itself uncertain by about 24%
HEADER = re.compile(r"# seed (\d+) iterations (\d+) sampling (\w+)")
Z95 = NormalDist().inv_cdf(0.95)
FACT = " (so or not)"  # a bernoulli's second stream is named by its name and this
Vec = NDArray[np.float64]


FORMS = ("lognormal", "normal", "logit-normal", "bernoulli")
CHANCE_FORMS = ("logit-normal", "bernoulli")  # the forms a chance may name
MSG = {
    "2.5.1": 'a low of 0 cannot be a percentile of a lognormal. If the effect may not happen, make that a chance factor'
             ' (rule 6.3); if the factor can be negative, name form = "normal", under which one draw in 20 falls below'
             ' your low',
    "2.5.2": "form lognormal needs a low above 0; a quantity that can be negative is form normal",
    "2.5.3": "its sign is certain: write it positive and let the row's kind give the direction",
    "2.5.5": "form logit-normal needs 0 < low and high < 1: for a high of 1 write 0.99, and if you mean anywhere"
             " between, 0.05 and 0.95",
    "2.5.6": "form must be lognormal, normal, logit-normal or bernoulli",
    "2.5.7": "half its draws would sit exactly at the middle: widen that end, or give all three one value for a fixed"
             " quantity",
    "2.5.9": "a chance is logit-normal or bernoulli: name no form, form logit-normal or form bernoulli",
    "2.5.11": 'form bernoulli is a chance that a thing is so: unit "probability", with 0 < low and high < 1',
}


def refuse(why: str) -> NoReturn:
    sys.exit(f"refused: {why}")


def logit(p: float) -> float:
    return math.log(p / (1 - p))


def sigmas(f: dict[str, Any]) -> tuple[float, float]:
    """s1 and s2 of a factor of resolved form: its two halves' spreads, each from the middle to an end over z95."""
    low, mid, high = f["low"], f["middle"], f["high"]
    if f["form"] == "lognormal":
        return math.log(mid / low) / Z95, math.log(high / mid) / Z95
    if f["form"] == "normal":
        return (mid - low) / Z95, (high - mid) / Z95
    return (logit(mid) - logit(low)) / Z95, (logit(high) - logit(mid)) / Z95


def spread(f: dict[str, Any], z: Vec) -> Vec:
    """The factor's value at each Z, by its form."""
    s1, s2 = sigmas(f)
    s = np.where(z < 0, s1, s2)
    if f["form"] == "normal":
        return f["middle"] + s * z
    if f["form"] in ("logit-normal", "bernoulli"):
        return np.asarray(expit(logit(f["middle"]) + s * z), dtype=np.float64)
    x: Vec = f["middle"] * np.exp(s * z)
    return x


def factor_draw(f: dict[str, Any], n: int, seed: int, method: str) -> Vec:
    """The factor's n draws on its own stream of uniform numbers, by its form or by the engine's quantile of the
    distribution it names; a bernoulli in two stages, its chance drawn on that stream, then 1 where a second uniform
    number, of the stream named by its name and FACT, is below that chance, and 0 elsewhere."""
    name = f["name"]
    u = sampling.uniforms([name], n, seed, method)[name]
    if "spec" in f:
        try:
            return distributions.quantile(f["spec"], u)
        except ValueError as e:
            refuse(f"factor {name!r}: {e}")
    x = spread(f, np.asarray(ndtri(u), dtype=np.float64))
    if f["form"] != "bernoulli":
        return x
    u = sampling.uniforms([name + FACT], n, seed, method)[name + FACT]
    return np.where(u < x, 1.0, 0.0)


def resolve_form(f: dict[str, Any]) -> str:
    """The form a factor takes (brief 2.3), refusing what its form cannot draw (2.5)."""
    name, low, mid, high = f["name"], f["low"], f["middle"], f["high"]
    chance = f["unit"] == "probability"
    share = f["unit"] == "share" or str(f["unit"]).startswith("share ")

    def no(why: str) -> NoReturn:
        refuse(f"factor {name!r}: {why}")
    if chance and mid > 1:
        no("a probability's middle is above 1")
    if not low <= mid <= high:
        no("its low, middle and high must be in that order, low <= middle <= high")
    if (low == mid) != (mid == high):
        no(MSG["2.5.7"])
    form: str | None = f.get("form")
    if form is None:
        if chance or share:
            form = "logit-normal"
        elif low == 0:
            no(MSG["2.5.1"])
        else:
            form = "lognormal" if low > 0 else "normal"
    elif form not in FORMS:
        no(MSG["2.5.6"])
    elif chance and form not in CHANCE_FORMS:
        no(MSG["2.5.9"])
    if form == "bernoulli" and not (chance and 0 < low <= high < 1):
        no(MSG["2.5.11"])
    if form == "lognormal" and low <= 0:
        no(MSG["2.5.2"])
    if form == "normal" and high <= 0:
        no(MSG["2.5.3"])
    if form == "logit-normal" and not 0 < low <= high < 1:
        no(MSG["2.5.5"])
    return form


def check_keys(where: str, f: dict[str, Any], known: tuple[str, ...]) -> None:
    """Refuse an unknown key, naming it. A factor naming a `distribution` takes that family's fields
    (`distributions.fields`, required and optional) in place of low, middle, high and form, and states every required
    one."""
    if "distribution" not in f:
        unknown(where, f, known)
        return
    if any(k in f for k in SHAPE):
        refuse(f"{where}: states both a `distribution` and low, middle, high or form; give one or the other")
    kind = f["distribution"]
    try:
        if not isinstance(kind, str):
            raise ValueError(f"distribution must be a string, got {kind!r}")
        required, optional = distributions.fields(kind)
    except ValueError as e:
        refuse(f"{where}: {e}")
    unknown(where, f, (*(k for k in known if k not in SHAPE), "distribution", *sorted(required | optional)))
    missing = sorted(required - set(f))
    if missing:
        refuse(f"{where}: distribution {kind!r} needs {', '.join(missing)}")


def complete(f: dict[str, Any]) -> bool:
    """A whole factor: a unit with low, middle and high, or with a `distribution`."""
    return "unit" in f and ("distribution" in f or all(k in f for k in ENDS))


def pooled(spec: dict[str, Any], folder: Path) -> dict[str, Any]:
    """A specification as the engine draws it: an `empirical`'s pool read from its data_file's column by the engine's
    reader (`case.read_empirical`), the path relative to the table's folder and refused outside it, as the engine's
    loader refuses one outside the case's; a mixture's components alike."""
    kind = spec.get("distribution")
    if kind == "mixture" and isinstance(spec.get("components"), list):
        parts = cast(list[Any], spec["components"])
        return {**spec, "components": [pooled(cast(dict[str, Any], c), folder) if isinstance(c, dict) else c for c in parts]}
    if kind != "empirical":
        return spec
    try:
        pool = read_empirical(folder, "empirical", spec.get("data_file"), spec.get("column"))
    except CaseError as e:
        refuse(str(e))
    return {**spec, "pool": pool}


def stated_once(f: dict[str, Any], entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """A row's factor with its [factors] entry filled in; refused where it names no entry and states no values, where it
    states a value that is not the entry's, or where the entry is not a whole factor."""
    fname = f["name"]
    entry = entries.get(fname)
    if entry is None:
        if "complement_of" not in f and not complete(f):
            refuse(f"factor {fname!r}: states neither a unit with low, middle and high nor a unit with a `distribution`"
                   f" and its fields, and has no [factors.{fname}] entry")
        return f
    if not complete(entry):
        refuse(f"factor {fname!r}: a [factors] entry holds a unit with low, middle and high (and may hold form), or a"
               " unit with a `distribution` and its fields; and may hold source")
    for k, v in f.items():
        if k not in ("name", "source") and entry.get(k) != v:
            refuse(f"factor {fname!r}: the row states {k} = {v!r}, but [factors.{fname}] has {entry.get(k)!r}")
    return {"name": fname, **{k: v for k, v in entry.items() if k != "source"}}


def corners(ends: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    """A chain's low, middle and high: the least and greatest of its 2^k corner products, and the product of middles."""
    prods = [math.prod(c) for c in itertools.product(*[(lo, hi) for lo, _, hi in ends])]
    return min(prods), math.prod(m for _, m, _ in ends), max(prods)


def read_draws(files: list[str], folder: Path) -> tuple[dict[str, Vec], tuple[int, int, str]]:
    """Each file's values, and the (seed, iterations, method) their headers agree on."""
    out: dict[str, Vec] = {}
    first: tuple[str, tuple[int, int, str]] | None = None
    for file in files:
        path = folder / file
        with path.open() as fh:
            m = HEADER.fullmatch(fh.readline().strip())
        if not m or m[3] not in sampling.SAMPLING_METHODS or int(m[2]) < 1:
            refuse(f"draws file {file}: line 1 must be '# seed S iterations N sampling M', M one of"
                   f" {sampling.SAMPLING_METHODS}, as sampling.write_draws writes it")
        head = (int(m[1]), int(m[2]), m[3])
        if first is None:
            first = (file, head)
        elif head != first[1]:
            refuse(f"draws files {first[0]} and {file}: headers disagree, {first[1]} and {head}")
        d = np.loadtxt(path, dtype=np.float64, ndmin=1)
        if d.size != head[1]:
            refuse(f"draws file {file}: {d.size} values but its header says {head[1]} iterations")
        out[file] = d
    return out, (first[1] if first else (SEED, DRAWS, METHOD))


def totaled(values: list[Vec], n: int) -> tuple[dict[str, Any], Vec]:
    """One total's expected value (the mean of its draws) with its standard error, median, 90 per cent interval and
    chance of being positive, and its draws; a total of no effect is zero in every draw."""
    total: Vec = np.sum(values, axis=0) if values else np.zeros(n)
    return {"expected": float(total.mean()), "standard_error": standard_error(total), "median": float(np.median(total)),
            "p05": float(np.quantile(total, 0.05)), "p95": float(np.quantile(total, 0.95)),
            "chance_positive": float(np.mean(total > 0)), "chance_positive_se": standard_error((total > 0).astype(np.float64))}, total


def batches(n: int) -> list[slice]:
    """BATCHES non-overlapping runs of the draws, of equal size, for a figure's Monte Carlo standard error (the EPA's
    "non-overlapping subsequences", 1997, principle 9); none where a batch would hold fewer than two draws."""
    m = n // BATCHES
    return [slice(b * m, (b + 1) * m) for b in range(BATCHES)] if m >= 2 else []


def batch_se(figures: list[float | None]) -> float | None:
    """The standard error of a figure from its value in each batch: their standard deviation over the square root of
    their number; None where a batch has none."""
    known = [x for x in figures if x is not None]
    return float(np.std(known, ddof=1)) / math.sqrt(len(known)) if known and len(known) == len(figures) else None


def share(v: Vec, total: Vec) -> float | None:
    """An effect's covariance with the total over the total's variance; None where the total does not vary."""
    var = float(total.var())
    return float(np.mean((v - v.mean()) * (total - total.mean())) / var) if var > 0 else None


def comonotone(values: list[Vec], n: int) -> dict[str, float]:
    """The total if every effect moved together: the sum of each effect's sorted draws, the most spread-out dependence
    of the effects' own distributions (Dhaene et al. 2002), whose quantiles are the sums of theirs."""
    together: Vec = np.sum([np.sort(v) for v in values], axis=0) if values else np.zeros(n)
    return {"p05": float(np.quantile(together, 0.05)), "p95": float(np.quantile(together, 0.95)),
            "chance_positive": float(np.mean(together > 0))}


def summary(effects: list[dict[str, Any]], values: list[Vec], n: int) -> tuple[dict[str, Any], Vec]:
    """One total: its effects, each with its share of the total's variance and that share's batch standard error, the
    bound if every effect moved together, and its draws."""
    head, total = totaled(values, n)
    head["comonotone"] = comonotone(values, n)
    shares = [share(v, total) for v in values]
    shares_se = [batch_se([share(v[b], total[b]) for b in batches(n)]) if s is not None else None
                 for v, s in zip(values, shares)]
    t_exp = head["expected"]
    benefits = sorted((m for m in (float(v.mean()) for v in values) if m > 0), reverse=True)  # as the total leads
    removable, left = 0, t_exp
    for b in benefits:
        if left - b < 0:
            break
        removable, left = removable + 1, left - b
    return {
        "effects": [{**e, "variance_share": s, "variance_share_se": se} for e, s, se in zip(effects, shares, shares_se)],
        "removable_benefits": removable,
        "total": head,
    }, total


def shared_index(total: Vec, key: Vec, n: int) -> dict[str, float | None]:
    """A factor's main-effect index on the total, Var(E[total | factor]) / Var(total) by the engine's 50-bin fit
    (`value_of_information.main_effect`), and its standard error from BATCHES batches; None where the total does not
    vary."""
    def index(s: slice) -> float | None:
        return main_effect(total[s], key[s]) if float(total[s].var()) > 0 else None
    return {"index": index(slice(None)), "standard_error": batch_se([index(b) for b in batches(n)])}


def show_shared(shared: dict[str, dict[str, float | None]]) -> None:
    """Print each shared factor's main-effect index with its standard error."""
    if not shared:
        return
    print(f"factors that two or more effects share: each one's main-effect index, Var(E[total | factor]) / Var(total)"
          f" by 50 bins, with its standard error from {BATCHES} batches:")
    for fname, x in shared.items():
        i, se = x["index"], x["standard_error"]
        print(f"  {fname}: " + ("n/a" if i is None else percent(i))
              + ("" if se is None else f" (standard error {percent(se)})"))


def pair(a: float, b: float) -> str:
    """A 5th-to-95th pair, each end at the figures that tell the two apart."""
    n = separating_figures((a, b))
    return f"{significant(a, n)} to {significant(b, n)}"


def columns(rows: list[list[str]], left: int) -> None:
    """Print rows in columns as wide as each column's longest string; the first `left` columns align left."""
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print("  ".join(c.ljust(w) if i < left else c.rjust(w) for i, (c, w) in enumerate(zip(r, widths))).rstrip())


def show(s: dict[str, Any], quiet: bool, lead: str, money: str, figures: tuple[int, int] = (2, 2)) -> None:
    """Print one total, its expected value and median at `figures`, the case in which every effect moves together, and
    each shared quantity's main-effect index. Quiet:
    of its effects, the TOP of largest expected value and the TOP of largest variance share. The effects are in `money`,
    unweighted; where the weighted total leads, the total, the shares of variance and the benefits removable are
    weighted, and a line says so."""
    effects: list[dict[str, Any]] = s["effects"]
    if quiet:
        def largest(key: str) -> list[int]:
            return sorted(range(len(effects)), key=lambda i: -abs(effects[i][key] or 0.0))[:TOP]
        effects = [effects[i] for i in sorted({*largest("expected"), *largest("variance_share")})]
    rows = [["effect", "kind", "low", "middle", "high", "weight", "expected", "std error", "median", "var share",
             "share se", "flag"]]
    for e in effects:
        share = "n/a" if e["variance_share"] is None else percent(e["variance_share"])
        share_se = "n/a" if e["variance_share_se"] is None else percent(e["variance_share_se"])
        flag = f"tail {percent(e['tail_share'])}" if e["flagged"] else ""
        for i, c in enumerate(e["chains"]):
            kind = c["kind"] if e["kind"] == "mixed" else (e["kind"] if i == 0 else "")  # a mixed effect's on each line
            n = separating_figures((c["low"], c["middle"], c["high"]))
            ends = [significant(c[k], n) for k in ("low", "middle", "high")]
            tail_cols = ([significant(e["expected"]), significant(e["standard_error"]), significant(e["median"]), share,
                          share_se, flag] if i == 0 else ["", "", "", "", "", ""])
            rows.append([e["name"] if i == 0 else "", kind, *ends, percent(c["weight"]), *tail_cols])
    columns(rows, 2)
    if len(effects) < len(s["effects"]):
        print(f"({len(effects)} of {len(s['effects'])} effects shown: the {TOP} of largest expected value and the {TOP}"
              " of largest share of variance)")
    signed = [e for e in s["effects"] if e["signed"]]
    if signed:
        print("effects that can go either way: chance above zero; mean if above; mean if below; 90% interval; tail share")
    for e in signed:
        print(f"  {e['name']}: {percent(e['share_above_zero'])}; {significant(e['mean_if_above'])};"
              f" {significant(e['mean_if_below'])}; {pair(e['p05'], e['p95'])}; {percent(e['tail_share'])}")
    t = s["total"]
    print(f"total: expected {significant(t['expected'], figures[0])} (standard error {significant(t['standard_error'])});"
          f" median {significant(t['median'], figures[1])};"
          f" 90% interval {pair(t['p05'], t['p95'])}; chance positive {percent(t['chance_positive'])}"
          f" (standard error {percent(t['chance_positive_se'])})")
    c = t["comonotone"]
    print(f"if every effect moved together (the widest spread, not a bound: other dependence can move a percentile or"
          f" the chance positive further; the mean is unchanged): 90% interval"
          f" {pair(c['p05'], c['p95'])}; chance positive {percent(c['chance_positive'])}")
    if lead == "weighted":
        print(f"effects above in {money}; the total, the shares of variance and the count below weighted")
    print(f"largest benefits removable before expected net benefits turn negative: {s['removable_benefits']}")
    show_shared(s["shared_factors"])


FAMILIES = {  # how the engine's `distributions.quantile` draws each named family, for the method block
    "beta": "min + (max − min) × the beta(alpha, beta) quantile of the uniform number.",
    "constant": "its mean in every draw.",
    "lognormal": "exp(μ + σ Z), with σ² = ln(1 + sd² / mean²) and μ = ln(mean² / √(mean² + sd²)), so its mean and"
                 " standard deviation are the stated ones.",
    "normal": "mean + sd × Z.",
    "power law": "min × (1 − u)^(−1 / (alpha − 1)), a Pareto whose tail index is alpha − 1 and whose mean is"
                 " min (alpha − 1) / (alpha − 2); an alpha at or below 2, whose mean is infinite, is refused, and the"
                 " tail is not capped.",
    "triangular": "the inverse of the triangular distribution function from min through mode to max.",
    "uniform": "min + u (max − min).",
    "metalog": "the metalog quantile function fitted to the stated probabilities and values (Keelin 2016).",
    "empirical": "the inverted-CDF quantile of the values in the data file's column.",
    "mixture": "one component picked in each draw by its weight, the uniform number rescaled within that component's"
               " share and drawn by the component's own family. Since its value is not monotone in u, its 5th, 50th"
               " and 95th percentiles are read from its values at 100,000 evenly spaced uniform numbers.",
}


def form_of(f: dict[str, Any]) -> str:
    """A factor's form as the JSON and the method name it: a judged form, or a named family marked NAMED."""
    return f["form"] + NAMED if "spec" in f else f["form"]


def family_text(kind: str) -> str:
    """How a factor naming the family `kind` is drawn, in words."""
    how = FAMILIES.get(kind) or (f"scipy.stats's {kind[len(distributions.SCIPY):]} inverse distribution function (ppf) at"
                                 " its stated shapes, loc and scale.")
    return (f"A factor naming this distribution with its own parameters, drawn by the engine's"
            " `distributions.quantile` on the factor's own uniform numbers u (Z the standard normal number at u), as a"
            f" model input of the same name and specification is drawn: {how} Its low, middle and high in the tables"
            " are its 5th, 50th and 95th percentiles, computed by that quantile function; a family whose mean is"
            " infinite or undefined is refused, since no mean of draws estimates it.")


def method_block(n: int, seed: int, method: str, families: set[str]) -> dict[str, Any]:
    """The method in words, for the appendix (`documents.method_tables`): each form and each named family the table uses,
    the run's settings, and how means, shares of variance, dependence and sets are computed."""
    z = f"{Z95:.4f}"
    return {
        "forms": {**{kind + NAMED: family_text(kind) for kind in sorted(families)},
            "lognormal": "A positive quantity, drawn as a two-piece lognormal joined at the median, half the mass on each"
                         " side. Its judged low, middle and high are its 5th, 50th and 95th percentiles: the value is"
                         f" middle × exp(s Z), Z a standard normal number, with s = ln(middle / low) / {z} below the"
                         f" middle and s = ln(high / middle) / {z} above it, so its density steps at the median. This"
                         " departs from Wallis's two-piece form (2014), which joins the halves at the mode. The high is"
                         " passed one draw in twenty, and the upper half's tail runs on beyond it without bound, so where"
                         " the high is a large multiple of the middle much of the mean comes from draws above the high;"
                         " no tail is capped.",
            "normal": "A quantity that can be negative. The value is middle + s Z, with s = (middle − low) / {z} below the"
                      " middle and s = (high − middle) / {z} above it; beyond the low and the high each half's thin normal"
                      " tail runs on without bound, one draw in twenty beyond each end.".format(z=z),
            "logit-normal": "A chance or a share, between 0 and 1. The value is 1 / (1 + exp(−(L + s Z))), L the logit of"
                            f" the middle, with s = (L − logit(low)) / {z} below the middle and s = (logit(high) − L) /"
                            f" {z} above it; it never reaches 0 or 1, and beyond the high its tail is pressed toward 1.",
            "bernoulli": "A fact that is so or not, drawn in two stages in every draw: first its chance, a logit-normal"
                         " from its judged low, middle and high, then the fact, 1 where a second uniform number of its own"
                         " is below that chance and 0 otherwise. Its share of yes draws estimates the mean of its chance."
                         " Every row and every set that names the fact, or its complement (one minus it), sees the same"
                         " draw.",
        },
        "draws": n, "seed": seed, "sampling": method,
        "mean": "Every expected value the tool reports (each effect, each set's total and outlay, each factor, each"
                " policy added to the base or removed from the leading set, each interaction) is the mean of its draws,"
                " with its Monte Carlo standard error, the standard deviation of the draws over the square root of their"
                " number; no mean is computed by formula. A difference between sets is the mean of the per-draw"
                " difference on the common draws, and its standard error is that difference's own. Medians, 90 per cent"
                " intervals and chances of being positive are read from the same draws.",
        "variance_share": "An effect's share of variance is the covariance of its draws with the total's draws over the"
                          " variance of the total's draws: an allocation of the total's variance among the effects that"
                          " sums to one and can be negative. For an effect that shares no drawn quantity with another,"
                          " this share is its main-effect variance, the value of perfect information under squared-error"
                          " loss (Oakley and O'Hagan 2004, 2.5.2); where effects share one, the share is an allocation,"
                          " and each quantity two or more effects rest on (a factor of their chains, the chance a"
                          " complement is one minus, a start or a number of years with the drawn rate that discounts it,"
                          " and, where the weighted total leads, a weight's incomes and elasticity) is ranked, beside each"
                          " total, by its own main-effect index,"
                          " Var(E[total | factor]) / Var(total), the mean of the total within 50 equal-count bins of the"
                          " factor's draws (Strong and Oakley 2013). Each share and each index carries its Monte Carlo"
                          f" standard error, the standard deviation of its values in {BATCHES} non-overlapping batches of"
                          f" the draws over the square root of {BATCHES}; under a heavy tail these errors are wide, and"
                          " nothing is smoothed.",
        "dependence": "Each factor name is one quantity, drawn once per draw on a stream of uniform numbers fixed by its"
                      " name and the seed, so every row and every set that names it sees the same value. Factors of"
                      " different names are drawn independently of each other, as are a fact's chance and its second"
                      " uniform number. The rival chains of one effect are picked by their weights on one uniform number"
                      " per effect and draw, the same in every set, and the picks of different effects are independent."
                      " A model's draws enter as its file gives them, draw by draw, coupled to a factor of the same name"
                      " only through the shared stream. Independence is thus assumed between differently named factors"
                      " and between rival chains. Beside each total is printed the case in which every effect moves"
                      " together (comonotone), its 90 per cent interval running from the sum of the effects' 5th"
                      " percentiles to the sum of their 95th, and its chance positive the share of positive sums of each"
                      " effect's sorted draws. It is the widest spread any dependence can give the total in the"
                      " convex-order sense, its variance and every stop-loss premium the largest (Dhaene et al. 2002),"
                      " but it is not a bound on a percentile or on the chance positive: other dependence can move"
                      " either further (Embrechts and Puccetti 2006). It cannot move the mean, which is the sum of the"
                      " effects' means under any dependence.",
        "sets": "A set is a choice of policies holding at most one level of each lever. Its net benefits in a draw are"
                " the sum of its policies' rows, of the joint rows whose every policy it holds and, where it holds any"
                " policy, of the rows with no policy. The base, the set of no policy, is the world without action: no"
                " row counts in it, so its net benefits are zero in every draw and every other set's are its change from"
                " the base. Every set is evaluated on the same draws.",
    }


def unknown(where: str, d: dict[str, Any], known: tuple[str, ...]) -> None:
    """Refuse a key of `d` not in `known`, naming it: a misspelt key would otherwise pass as absent."""
    for k in d:
        if k not in known:
            refuse(f"{where}: unknown key {k!r}; the keys are {', '.join(known)}")


Schedule = tuple[tuple[int, int | None, float], ...]


@dataclass(frozen=True)
class Reading:
    """One discounting of every row: at the drawn rate (`drawn`, the factor's name), at one rate or schedule of the pinned
    edition (`schedule`), or, in a table with no frame, none."""
    label: str
    rate: float | None
    schedule: Schedule | None
    drawn: str | None = None


@dataclass(frozen=True)
class Frame:
    """The table's year, currency and pinned edition, its readings, groups and weighting (the header's Who gains and pays,
    time and money)."""
    year: int | None
    currency: str | None
    guidance: str | None
    series: str
    index: dict[int, float]
    readings: list[Reading]
    burden: float | None
    groups: dict[str, dict[str, Any]]
    weighted: bool
    reference: str | None
    elasticity: str | None
    common: frozenset[str]
    lead: str
    life_year: str | None
    bar_group: str | None


def read_frame(doc: dict[str, Any], rows: list[dict[str, Any]], table: Path) -> Frame:
    """The frame keys of the table, refused where incomplete, of the wrong kind or naming what is not there."""
    named = [k for k in ("year", "currency", "guidance", "discount_rate") if k in doc]
    if named and len(named) < 4:
        refuse(f"{', '.join(named)}: a table that names any of year, currency, guidance and discount_rate names all four:"
               " the year money and discounting are brought to, its currency, the pinned edition"
               " (<jurisdiction>/<edition>) and the factor of the drawn discount rate")
    year: int | None = None
    currency: str | None = None
    guidance: str | None = None
    series, index, burden = "", cast(dict[int, float], {}), None
    readings = [Reading("as the rows state it, undiscounted", None, None)]
    if named:
        year, currency, guidance, rate = doc["year"], doc["currency"], doc["guidance"], doc["discount_rate"]
        if not isinstance(year, int) or isinstance(year, bool):
            refuse(f"year: {year!r} is not a calendar year")
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            refuse(f"currency: {currency!r} is not three upper-case letters, such as USD")
        if not isinstance(guidance, str) or not re.fullmatch(r"[a-z_]+/[0-9-]+", guidance):
            refuse(f"guidance: {guidance!r} is not <jurisdiction>/<edition>, such as united_states/2026-10-30")
        if not isinstance(rate, str):
            refuse("discount_rate: names the [factors] entry of the drawn discount rate")
        path = guidance_for(table.resolve().parent) / f"{guidance}.toml"
        if not path.is_file():
            refuse(f"guidance: no edition {path}")
        edition = tomllib.loads(path.read_text())
        pi: Any = edition.get("price_index")
        if not isinstance(pi, dict) or cast(dict[str, Any], pi).get("currency") != currency \
                or not isinstance(cast(dict[str, Any], pi).get("calendar_year"), dict):
            refuse(f"guidance {guidance}: its [price_index] is not in {currency}, or has no calendar_year")
        prices = cast(dict[str, object], pi)
        series = str(prices.get("series", ""))
        years, problem = price_index_years(prices)  # the engine's reader, so one reader refuses a bad index
        if problem is not None or years is None:
            refuse(f"guidance {guidance}: [price_index] calendar_year: {problem}")
        index = {y: v for y, v in years.items() if v is not None}
        if year not in index:
            refuse(f"year: {year} is not a year of {guidance}'s price index")
        entry: Any = edition.get("discount_rate")
        found = guidance_schedules(cast(dict[str, object], entry)) if isinstance(entry, dict) else "it has none"
        if isinstance(found, str):
            refuse(f"guidance {guidance}: discount_rate: {found}")
        readings = [Reading(f"drawn rate ({rate})", None, None, rate)]
        readings += [Reading(label, rows_[0][2] if len(rows_) == 1 and rows_[0][1] is None else None, tuple(rows_))
                     for label, rows_ in found]
        eb: Any = edition.get("excess_burden")
        burden = float(cast(dict[str, Any], eb)["value"]) if isinstance(eb, dict) and "value" in eb else None
    raw: Any = doc.get("groups", {})
    if not isinstance(raw, dict) or not all(isinstance(g, dict) for g in cast(dict[str, Any], raw).values()):
        refuse("groups: a top-level `groups` holds only tables, [groups.<name>]")
    groups = cast(dict[str, dict[str, Any]], raw)
    for gname, g in groups.items():
        unknown(f"[groups.{gname}]", g, ("income", "public"))
        if not isinstance(g.get("income"), str) or not isinstance(g.get("public", False), bool):
            refuse(f"[groups.{gname}]: income names the factor of the group's income, and public is true or false")
    for r in rows:
        if groups and r.get("group") not in groups:
            refuse(f"effect {r.get('name')!r}: group must name one of the table's groups ({', '.join(groups)})")
        if not groups and "group" in r:
            refuse(f"effect {r.get('name')!r}: group {r['group']!r} names no [groups] entry, and the table has none")
    weighted = len({r["group"] for r in rows}) >= 2 if groups else False
    reference, elasticity = doc.get("reference"), doc.get("elasticity")
    if weighted and not isinstance(elasticity, str):
        refuse("elasticity: rows fall in two or more groups, each of its own income, so the table names the factor of the income"
               " elasticity of the value of a statistical life; the tool assumes none")
    if reference is not None and reference not in groups or weighted and reference is None:
        refuse(f"reference: {reference!r} must name the group whose money weighs 1, one of the table's groups")
    common: Any = doc.get("common_values", [])
    if not isinstance(common, list) or not all(isinstance(c, str) for c in cast(list[Any], common)):
        refuse("common_values: a list of factor names")
    for k in ("life_year", "bar_group"):
        if k in doc and (not weighted or not isinstance(doc[k], str) or k == "bar_group" and doc[k] not in groups):
            refuse(f"{k}: {doc[k]!r}; in a table whose rows fall in two or more groups, life_year names the factor of the"
                   " value of a life-year in the reference group's money, and bar_group the group cash would go to")
    lead: Any = doc.get("lead", "weighted" if weighted else "dollars")
    if lead not in ("weighted", "dollars") or lead == "weighted" and not weighted:
        refuse(f"lead: {lead!r}; lead is dollars, or weighted where rows fall in two or more groups")
    if lead == "weighted" and "life_year" not in doc:
        refuse("life_year: the weighted total leads, so the table names life_year, the factor of the value of a statistical"
               " life-year in the reference group's money (from the pinned guidance where it gives one), which turns the"
               " weighted total into life-years (the owner's rule 15); or lead = \"dollars\" sets the dollar total to lead")
    for gname, g in groups.items() if "bar_group" in doc else ():
        if g.get("public") and not any(r.get("group") == gname for r in rows):
            refuse(f"[groups.{gname}]: a public group with no rows, while bar_group is set; the bar weighs each public"
                   " group's net cost, so give the group its rows or remove it")
    return Frame(year, currency, guidance, series, index, readings, burden, groups, weighted,
                 cast(str | None, reference), cast(str | None, elasticity), frozenset(cast(list[str], common)), lead,
                 doc.get("life_year"), doc.get("bar_group"))


def discounted(reading: Reading, start: Vec | None, years: Vec | None, rate: Vec | None,
               grid: tuple[Vec, Vec] | None) -> Vec | float:
    """A row's present value of 1 at this reading: a one-off `start` years out, 1 a year for `years` years after `start`
    (0 where none), or 1 now; flows at the end of each year, a fractional year interpolated linearly between whole ones.
    At the drawn rate, per draw: sum of v^t over t = 1..k is (1 - v^k) / r, v = 1 / (1 + r); at a guidance rate or
    schedule, the yearly factors of `timeline.discount_factors` (`grid`: those factors and their cumulative sums)."""
    if start is None and years is None:
        return 1.0
    s: Vec = start if start is not None else np.zeros(1)
    if rate is not None:
        v = 1 / (1 + rate)
        safe = np.where(rate == 0, 1.0, rate)

        def at(x: Vec) -> Vec:
            k = np.floor(x)
            return v ** k * (1 - (x - k) * (1 - v))

        def cum(x: Vec) -> Vec:
            k = np.floor(x)
            return np.where(rate == 0, k, (1 - v ** k) / safe) + (x - k) * v ** (k + 1)
    else:
        assert grid is not None
        d, c = grid
        t = np.arange(d.size, dtype=np.float64)

        def at(x: Vec) -> Vec:
            return np.interp(x, t, d)

        def cum(x: Vec) -> Vec:
            return np.interp(x, t, c)
    return at(s) if years is None else cum(s + years) - cum(s)

Key = str | tuple[str, ...] | None  # a row's policy: one name, the sorted names of a joint row, or none


def policy_of(r: dict[str, Any]) -> Any:
    """A row's policy as written: `policy`, or its synonym `option`."""
    return r.get("policy", r.get("option"))


def policy_key(r: dict[str, Any]) -> Key:
    """A row's policy as a key: a joint row's names sorted, so that their order as written changes nothing."""
    p = policy_of(r)
    return tuple(sorted(cast(list[str], p))) if isinstance(p, list) else cast(Key, p)


def inside(key: Key, s: frozenset[str]) -> bool:
    """Whether a row of this policy key counts in the set s: a row of no policy where s holds any policy (never in the
    base), a joint row where s holds every policy it names."""
    if key is None:
        return bool(s)
    return s.issuperset(key) if isinstance(key, tuple) else key in s


def read_policies(doc: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[dict[str, list[str]], list[str]]:
    """The table's levers (name: levels) and its policies in the order the rows first name them. A table of
    `option` rows is one lever, named option, of the option keys."""
    if any("option" in r for r in rows) and (any("policy" in r for r in rows) or "lever" in doc):
        refuse("option and policy: `option` is the older name of a policy of one lever; a table uses one form, so write"
               " every row's `policy` and list the options as a [lever]")
    for r in rows:
        p = r.get("policy")
        if p is not None and not (isinstance(p, str) and p) and not (
                isinstance(p, list) and len(cast(list[Any], p)) >= 2
                and all(isinstance(x, str) and x for x in cast(list[Any], p))
                and len(set(cast(list[str], p))) == len(cast(list[str], p))):
            refuse(f"effect {r.get('name')!r}: policy is a name, or a list of two or more different names for a row that"
                   " counts only where all of them are in force")
    policies: list[str] = list(dict.fromkeys(
        x for r in rows if policy_of(r) is not None
        for x in (cast(list[str], policy_of(r)) if isinstance(policy_of(r), list) else [policy_of(r)])))
    if any("option" in r for r in rows):
        return {"option": policies}, policies
    raw: Any = doc.get("lever", {})
    if not isinstance(raw, dict) or not all(isinstance(v, list) for v in cast(dict[str, Any], raw).values()):
        refuse("lever: a top-level [lever] maps each lever's name to the list of its levels, each a policy")
    levers = cast(dict[str, list[str]], raw)
    seen: dict[str, str] = {}
    for name, levels in levers.items():
        for level in levels:
            if level not in policies:
                refuse(f"lever {name!r}: level {level!r} is the policy of no row")
            if level in seen:
                refuse(f"lever {name!r}: level {level!r} is also a level of lever {seen[level]!r}; a policy is in one lever")
            seen[level] = name
    for r in rows:
        p = policy_of(r)
        if isinstance(p, list) and len({seen[x] for x in cast(list[str], p) if x in seen}) < len(
                [x for x in cast(list[str], p) if x in seen]):
            refuse(f"effect {r.get('name')!r}: a joint row names two levels of one lever, which no set holds together")
    return levers, policies


def policy_sets(effects: list[dict[str, Any]], ekeys: list[Key], values: list[Vec], public: list[Vec | None],
                policies: list[str], levers: dict[str, list[str]], n: int,
                keep: bool) -> tuple[dict[str, Any], dict[tuple[str, ...], Vec], Vec]:
    """The sets of policies evaluated on the table's draws, each effect's leading total in `values` and its public
    groups' dollars in `public`, and what is reported of them (the header's Policies); with keep, each set's draws too;
    and in each draw the highest net benefits of any set evaluated."""
    group = {p: ("lever", name) for name, levels in levers.items() for p in levels}
    group.update({p: ("policy", p) for p in policies if p not in group})
    rank = {p: i for i, p in enumerate(policies)}
    done: dict[frozenset[str], dict[str, Any]] = {}
    kept: dict[tuple[str, ...], Vec] = {}
    peak: Vec = np.full(n, -np.inf)

    def nb(s: frozenset[str]) -> float:
        """The set's expected net benefits, evaluating it, on the common draws, the first time it is asked for."""
        if s not in done:
            mine = [i for i, key in enumerate(ekeys) if inside(key, s)]
            total, draws = totaled([values[i] for i in mine], n)
            paid = [p for p in (public[i] for i in mine) if p is not None]
            spent: Vec = -np.sum(paid, axis=0) if paid else np.zeros(n)
            names = sorted(s, key=rank.__getitem__)
            outlay = float(spent.mean())
            done[s] = {"policies": names, "outlay": outlay, "outlay_standard_error": standard_error(spent),
                       "total": total, "per_public_dollar": total["expected"] / outlay if outlay else None}
            np.maximum(peak, draws, out=peak)
            if keep:
                kept[tuple(names)] = draws
        return done[s]["total"]["expected"]

    def contrast(weights: dict[frozenset[str], int]) -> tuple[float, float]:
        """The mean and standard error of the sum over sets of weight * NB(set), per draw on the common draws, worked
        row by row: each row's draws times the net count of the sets it enters, so a contrast no row enters is exactly
        zero."""
        d: Vec = np.zeros(n)
        for i, key in enumerate(ekeys):
            c = sum(w for s, w in weights.items() if inside(key, s))
            if c:
                d = d + c * values[i]
        return float(d.mean()), standard_error(d)

    def allowed(s: frozenset[str]) -> bool:
        return len({group[p] for p in s}) == len(s)

    base = frozenset[str]()
    dims = [[None, *levels] for levels in levers.values()] + [[None, p] for p in policies if group[p][0] == "policy"]
    count = math.prod(len(d) for d in dims)
    if count <= ALL_SETS:
        for choice in itertools.product(*dims):
            nb(frozenset(p for p in choice if p is not None))
    else:  # alone, in pairs, then led by the policies of high value alone, then improved one change at a time
        nb(base)
        for p in policies:
            nb(frozenset({p}))
        for p, q in itertools.combinations(policies, 2):
            if allowed(frozenset({p, q})):
                nb(frozenset({p, q}))
        own = {p: float(sum(values[i].mean() for i, key in enumerate(ekeys) if key == p)) for p in policies}
        s = base
        for p in sorted(policies, key=lambda p: -own[p]):
            if own[p] <= 0:
                break
            if all(group[q] != group[p] for q in s):
                s = s | {p}
                nb(s)
        s = max(done, key=nb)
        while True:
            moves = [s - {p} for p in s] + [frozenset(q for q in s if group[q] != group[p]) | {p}
                                              for p in policies if p not in s]
            best = max(moves, key=nb)
            if nb(best) <= nb(s):
                break
            s = best
    added = {p: contrast({frozenset({p}): 1, base: -1}) for p in policies}
    lead = max(list(done), key=nb)
    removed = {p: contrast({lead: 1, lead - {p}: -1}) for p in sorted(lead, key=rank.__getitem__)}
    for p in lead:
        nb(lead - {p})
    interactions: dict[str, dict[str, tuple[float, float]]] = {}
    for p, q in itertools.combinations(policies, 2):
        if group[p] != group[q]:
            nb(frozenset({p, q}))
            v = contrast({frozenset({p, q}): 1, frozenset({p}): -1, frozenset({q}): -1, base: 1})
            interactions.setdefault(p, {})[q] = interactions.setdefault(q, {})[p] = v
    frontier: list[dict[str, Any]] = []
    best_nb = -math.inf
    ordered = sorted(done.values(), key=lambda e: (e["outlay"], -e["total"]["expected"]))
    for _, same in itertools.groupby(ordered, key=lambda e: e["outlay"]):
        tied = list(same)
        top = tied[0]["total"]["expected"]
        if top > best_nb:
            frontier += [{"policies": e["policies"], "outlay": e["outlay"], "expected": top,
                          "standard_error": e["total"]["standard_error"]}
                         for e in tied if e["total"]["expected"] == top]
            best_nb = top
    return {"sets": list(done.values()), "enumeration": {"allowed": count, "evaluated": len(done), "all": count <= ALL_SETS},
            "added": {p: v for p, (v, _) in added.items()}, "added_se": {p: se for p, (_, se) in added.items()},
            "leading": done[lead]["policies"], "removed": {p: v for p, (v, _) in removed.items()},
            "removed_se": {p: se for p, (_, se) in removed.items()},
            "interactions": {p: {q: v for q, (v, _) in qs.items()} for p, qs in interactions.items()},
            "interactions_se": {p: {q: se for q, (_, se) in qs.items()} for p, qs in interactions.items()},
            "frontier": frontier}, kept, peak


def choice_value(sets: list[frozenset[str]], lead: Vec, peak: Vec, ekeys: list[Key], values: list[Vec],
                 uses: list[set[str]], drawn: dict[str, Vec], every: bool) -> dict[str, Any]:
    """The header's `value_of_information`: the expected loss of the leading set, whose draws are `lead`, against
    `peak`, each draw's best of `sets`; and the engine's `evppi` over `sets` for each quantity in `drawn` whose draws
    vary and that an effect of any of `sets` uses (`uses`, by effect). Each key is binned once, by the engine's own
    `bin_codes`, and its `evppi` is the engine's `binned_value` of every set's sums by bin, each set's sums being the
    sums of its effects' (`member` times the effects' sums by bin); the full matrix of up to ALL_SETS sets by the draws
    would not fit the run's time or memory."""
    loss = peak - lead
    member = np.array([[inside(k, s) for k in ekeys] for s in sets], dtype=np.float64)
    used = set[str]().union(*(uses[i] for i in np.flatnonzero(member.any(axis=0))))
    found: dict[str, float] = {}
    for q in sorted(used):
        key = drawn[q]
        if key.min() == key.max():
            continue
        codes = value_of_information.bin_codes(key)  # looked up at the call, so the engine's binning is the one used
        size = int(codes.max()) + 1
        by_bin = np.array([np.bincount(codes, weights=v, minlength=size) for v in values]).T @ member.T  # bins by sets
        found[q] = value_of_information.binned_value(by_bin, lead.size)
    return {"expected_loss": float(loss.mean()), "expected_loss_se": standard_error(loss), "evppi": found,
            "over_all_sets": every}


def show_choice(v: dict[str, Any], evaluated: int) -> None:
    """Print the expected loss of the leading set and each quantity's value of partial perfect information."""
    bound = "" if v["over_all_sets"] else f", over the {evaluated} sets evaluated, so a lower bound"
    print(f"expected loss of the leading set, E[max over sets of NB] - E[NB of the leading set]:"
          f" {significant(v['expected_loss'])} (std error {significant(v['expected_loss_se'])}){bound}")
    if v["evppi"]:
        print(f"value of partial perfect information over the choice of set, by {value_of_information.BINS} bins"
              f"{bound}:")
        order = sorted(v["evppi"].items(), key=lambda qe: -qe[1])
        columns([[f"  {q}", significant(e)] for q, e in order[:SHOWN]], 1)
        if len(order) > SHOWN:
            print(f"  ({len(order) - SHOWN} more, none larger, in the JSON)")


def show_sets(found: dict[str, Any], quiet: bool) -> None:
    """Print each policy added to the base and removed from the leading set, the largest interactions (in quiet mode
    the TOP of largest size), and the frontier of outlay against expected net benefits."""
    e = found["enumeration"]
    how = "every allowed set" if e["all"] else f"a search above {ALL_SETS} sets"
    print(f"\npolicies, on the same draws: {e['evaluated']} of {e['allowed']} allowed sets evaluated ({how})")
    removed, removed_se = found["removed"], found["removed_se"]
    rows = [["policy", "added to the base", "std error", "removed from the leading set", "std error"]]
    rows += [[p, significant(v), significant(found["added_se"][p]), *([significant(removed[p]),
              significant(removed_se[p])] if p in removed else ["", ""])] for p, v in found["added"].items()]
    columns(rows, 1)
    pairs = sorted(((p, q, v, found["interactions_se"][p][q]) for p, qs in found["interactions"].items()
                    for q, v in qs.items() if p < q), key=lambda x: -abs(x[2]))
    if pairs:
        shown = pairs[:TOP] if quiet else pairs
        print(f"interactions, NB(p + q) - NB(p) - NB(q) + NB(base), largest first ({len(shown)} of {len(pairs)} pairs),"
              " each with its standard error:")
        columns([[p, q, significant(v), significant(se)] for p, q, v, se in shown], 2)
    print("frontier of public outlay against expected net benefits, no set beating it on both:")
    columns([["set", "outlay", "expected", "std error"],
             *([" + ".join(f["policies"]) or "no policy", significant(f["outlay"]), significant(f["expected"]),
                significant(f["standard_error"])] for f in found["frontier"])], 1)


def show_headline(h: dict[str, Any], frame: Frame) -> None:
    """Print each reading's totals, the account by group, the outlay, the excess-burden reading and net benefits per
    public dollar."""
    def cells(t: dict[str, Any] | None) -> list[str]:
        return [] if t is None else [significant(t["expected"]), significant(t["standard_error"]), pair(t["p05"], t["p95"])]
    both = ["weighted", "std error", "90% interval"] if frame.weighted else []
    money = frame.currency or "as stated"
    print(f"\nthe leading total: {h['lead']}, at the reading {h['readings'][0]['label']}")
    life = ["life-years", "std error", "90% interval"] if frame.life_year else []
    columns([["reading", money, "std error", "90% interval", *both, *life],
             *([r["label"], *cells(r["dollars"]), *cells(r["weighted"]), *cells(r["life_years"])] for r in h["readings"])],
            1)
    if h["groups"]:
        print("who gains and who pays, at the leading reading:")
        columns([["group", money, "std error", "90% interval", *both],
                 *([g + (" (public)" if frame.groups[g].get("public") else ""), *cells(t["dollars"]), *cells(t["weighted"])]
                   for g, t in h["groups"].items())], 1)
    o, per = h["outlay"], h["per_public_dollar"]
    print(f"public outlay: {significant(o['expected'])} (standard error {significant(o['standard_error'])})"
          + ("" if per is None else f"; net benefits per public dollar {significant(per)}"))
    if h["cash"] is not None:
        c = h["cash"]
        print(f"the same outlay as cash to {c['group']}, weighted: {significant(c['weighted']['expected'])}; net benefits"
              f" above that cash: {significant(c['net_of_cash']['expected'])},"
              f" 90% interval {pair(c['net_of_cash']['p05'], c['net_of_cash']['p95'])}")
    if h["excess_burden"] is not None:
        e = h["excess_burden"]
        print(f"excess-burden reading ({percent(e['rate'])} of outlay, {frame.guidance}): {money} expected"
              f" {significant(e['dollars']['expected'])}, 90% interval {pair(e['dollars']['p05'], e['dollars']['p95'])}")


def frame_method(frame: Frame) -> dict[str, str]:
    """The groups and weights, the elasticity, the leading total, the discount readings, the outlay and excess-burden
    reading and the price year, in words as this run applied them, for `documents.method_annex`."""
    names = ", ".join(frame.groups)
    paying = [g for g, x in frame.groups.items() if x.get("public")]
    common = ", ".join(sorted(frame.common)) or "none listed"
    if frame.weighted:
        groups = (f"Each row names one of the groups {names}, each with a factor of its income. In each draw a dollar to"
                  f" group g weighs (y_ref / y_g)^e: y_g the draw of g's income, y_ref that of the reference group"
                  f" {frame.reference}, e the draw of the income elasticity of the value of a statistical life (the"
                  " transfer of Robinson, Hammitt and O'Keeffe 2019, with weights proportional to the reciprocal of each"
                  " person's value, Somanathan 2006). A row whose chain holds a value already at a common rate"
                  f" ({common}) weighs 1, so a life valued at one value of a statistical life is not weighted again (OMB"
                  " Circular A-4, 2023, 10.e). The account by group sums each group's rows in dollars and weighted; a"
                  " transfer, two rows of one factor, cancels in dollars draw by draw and counts weighted.")
    elif frame.groups:
        groups = f"Every row sits in one group of {names}, so no total is weighted; the account by group is in dollars."
    else:
        groups = "The table names no groups, so no total is weighted and there is no account by group."
    rates = ", ".join(r.label for r in frame.readings[1:])
    return {
        "groups": groups,
        "elasticity": f"The income elasticity is the factor {frame.elasticity}, drawn once per draw and used for every"
                      " group in that draw; the tool assumes no value of its own." if frame.weighted
                      else "Not used: no total is weighted.",
        "lead": (f"The weighted total leads, in dollars of the reference group {frame.reference} (the owner's rule 15);"
                 " the dollar total is shown beside it at every reading."
                 + (f" In life-years it is the weighted total over the draw of {frame.life_year}, the value of a life-year"
                    " in the reference group's money, one factor at every reading." if frame.life_year else "") if frame.lead == "weighted" else
                 "The dollar total leads, as the table's lead key sets; the weighted total is shown beside it."
                 if frame.weighted else "The dollar total leads, since no total is weighted."),
        "discount": (f"Money is discounted to {frame.year}. A row's start and years each name a factor drawn like any"
                     f" other: start alone is a one-off that many years after {frame.year}, years alone a flat amount"
                     " each year for that many years, both a flat amount each year for that many years after the start,"
                     " and a row with neither is a value now. Flows fall at the end of each year, at the factor"
                     " 1/(1 + i)^t of OMB Circular A-94, a fractional year interpolated linearly. The leading reading"
                     f" discounts each draw at its own draw of the rate {frame.readings[0].drawn}; each rate or schedule"
                     f" of the guidance edition {frame.guidance} ({rates}) is a reading of its own on the same draws."
                     if frame.year is not None else
                     "The table names no discount rate: each row is the present value its factors state, and the tool"
                     " discounts nothing."),
        "outlay": ((f"Public outlay is the net cost to the groups marked public ({', '.join(paying)}): minus their dollar"
                    " total at the leading reading. Net benefits per public dollar is the leading total's expected value"
                    " over the outlay's." if paying else
                    "No group is marked public, so the public outlay is zero and no net benefits per public dollar are"
                    " given.")
                   + (f" The excess-burden reading, the supplementary analysis of OMB Circular A-94 (1992) section 11 at"
                      f" the rate {frame.burden} of {frame.guidance}, is the dollar total less {frame.burden} times the"
                      " outlay, draw by draw; the weighted total takes no burden (Jacobs 2018, as cited in OMB Circular"
                      " A-4, 2023)." if frame.burden is not None else
                      " The guidance gives no excess burden, so no such reading is made.")
                   + (f" The bar (the owner's rule 16) is the same outlay paid as cash to {frame.bar_group}: in each draw"
                      " each public group's net cost times the bar group's weight less its own, so the net benefits above"
                      " that cash are the weighted total less it; in dollars cash is a transfer, worth nothing, and its"
                      " bar is the excess-burden reading." if frame.bar_group else "")),
        "price_year": (f"Money is in {frame.currency} of {frame.year}: each money factor is multiplied once, wherever it"
                       f" is used, by {frame.guidance}'s price index ({frame.series}) at {frame.year} over its value at"
                       " the factor's price year. A unit naming a currency, money in another currency and money without"
                       " a price year are refused." if frame.year is not None else
                       "The table names no year: money is taken in the units its rows state, and no price index is"
                       " applied."),
    }


def as_factor(f: dict[str, Any], folder: Path) -> dict[str, Any]:
    """A factor as drawn: its name, unit, ends and money keys, its form resolved; or, for one naming a `distribution`,
    the family as its form, its parameters, the specification the engine draws and, as its ends, the 5th, 50th and 95th
    percentiles the engine's quantile computes, refused where the engine refuses it (an infinite mean among them)."""
    kept = {k: f[k] for k in ("name", "unit", *MONEY) if k in f}
    if "distribution" not in f:
        return {**kept, **{k: f[k] for k in ENDS}, "form": resolve_form(f)}
    parameters = {k: v for k, v in f.items() if k not in ("name", "unit", "source", "distribution", *MONEY)}
    spec = pooled({"distribution": f["distribution"], **parameters}, folder)
    try:
        ends = (distributions.quantile(spec, PERCENTILES) if f["distribution"] != "mixture"
                else np.quantile(distributions.quantile(spec, GRID), PERCENTILES))
        low, middle, high = (float(x) for x in ends)
    except ValueError as e:
        refuse(f"factor {f['name']!r}: {e}")
    if f["unit"] == "probability":
        lo, hi = distributions.support(spec)
        if not 0.0 <= lo <= hi <= 1.0:
            refuse(f"factor {f['name']!r}: a probability's {f['distribution']} has support [{lo!r}, {hi!r}], not within"
                   " [0, 1], so it or its complement would draw outside [0, 1]; name a family bounded within it, such as"
                   " beta or uniform with 0 <= min < max <= 1")
    return {**kept, "low": low, "middle": middle, "high": high, "form": f["distribution"], "parameters": parameters,
            "spec": spec}


def agree_with_inputs(factors: dict[str, dict[str, Any]], path: Path) -> None:
    """Refuse a factor whose model input of the same name (a top-level table with a `distribution` in the inputs.toml
    beside the table) states another distribution or another value of a field of either's family, or that states no
    `distribution` at all: one name is one quantity. A yes-or-no fact (form bernoulli) is exempt, since its model input
    of its name is its chance, fitted to the factor's low, middle and high; a complement names no input."""
    if not path.exists():
        return
    try:
        given = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        refuse(f"{path}: {e}")
    for fname, f in factors.items():
        raw = given.get(fname)
        if "complement_of" in f or f.get("form") == "bernoulli" or not isinstance(raw, dict) or "distribution" not in raw:
            continue
        model_input = cast(dict[str, Any], raw)
        if "spec" not in f:
            refuse(f"factor {fname!r}: its model input of the same name in {path.name} states distribution"
                   f" {model_input['distribution']!r} and its fields, where the factor states low, middle and high;"
                   " a factor and a model input of one name are one quantity, so the factor states the input's"
                   " `distribution` and fields")
        mine = {"distribution": f["form"], **f["parameters"]}
        keys = {"distribution"}
        for kind in {f["form"], model_input["distribution"]}:
            try:
                required, optional = distributions.fields(str(kind))
            except ValueError:
                continue
            keys |= required | optional
        differ = [k for k in sorted(keys) if mine.get(k) != model_input.get(k)]
        if differ:
            refuse(f"factor {fname!r}: its model input of the same name in {path.name} states "
                   + ", ".join(f"{k} {model_input.get(k)!r} where the factor states {mine.get(k)!r}" for k in differ)
                   + "; a factor and a model input of one name are one quantity, stated alike")


def main(table: Path, quiet: bool = False, draws: bool = False, results: Path | None = None) -> None:
    results = results or table.parent / "results"
    (results / "estimate_total.json").unlink(missing_ok=True)  # the folder and the JSON come from one run
    shutil.rmtree(results / "estimate_total_draws", ignore_errors=True)
    doc = tomllib.loads(table.read_text())
    unknown("the table", doc, TOP_KEYS)
    raw: Any = doc.get("factors", {})
    if not isinstance(raw, dict) or not all(isinstance(e, dict) for e in cast(dict[str, Any], raw).values()):
        refuse("factors: a top-level `factors` holds only tables, [factors.<name>]")
    entries = cast(dict[str, dict[str, Any]], raw)
    for ename, entry in entries.items():
        check_keys(f"[factors.{ename}]", entry, ENTRY_KEYS)
    raw = doc.get("effect")
    if not isinstance(raw, list) or not all(isinstance(r, dict) for r in cast(list[Any], raw)):
        refuse("effect: the table needs [[effect]] rows")
    rows = cast(list[dict[str, Any]], raw)
    for r in rows:
        if "bound" in r:
            refuse(f"effect {r.get('name')!r}: a bound leaves an effect outside the total; estimate it as a judged chance"
                   " and a size whose high is its 95th percentile, labelled judgement (fermi-estimator rule 9)")
        unknown(f"effect {r.get('name')!r}", r, ROW_KEYS)
        for f in r.get("factor", []):
            check_keys(f"effect {r.get('name')!r}, factor {f.get('name')!r}", f, FACTOR_KEYS)
        if "factor" in r:
            r["factor"] = [stated_once(f, entries) for f in r["factor"]]
    factors: dict[str, dict[str, Any]] = {}  # each name's factor, its form resolved
    written: dict[str, dict[str, Any]] = {}  # each name's keys as written, one specification per name
    chains: dict[tuple[str, Key], list[dict[str, Any]]] = {}
    levers, policies = read_policies(doc, rows)
    for r in rows:
        name = r["name"]
        if r.get("kind") not in ("benefit", "cost"):
            refuse(f"effect {name!r}: kind must be benefit or cost")
        fs: list[dict[str, Any]] = r.get("factor", [])
        if not fs and "draws" not in r:
            refuse(f"effect {name!r}: no factors or draws")
        if len({f["name"] for f in fs}) < len(fs):
            refuse(f"effect {name!r}: a factor appears twice in one row")
        for f in fs:
            fname = f["name"]
            if "complement_of" in f:
                if any(k in f for k in ("unit", "distribution", *SHAPE)):
                    refuse(f"factor {fname!r}: a complement states only its name and complement_of, no unit, form or values")
                factors[fname] = {"name": fname, "unit": "probability", "complement_of": f["complement_of"]}
                of = f["complement_of"]
                if of not in factors and of in entries:  # a base in no row so far: its entry, drawn
                    factors[of] = as_factor(stated_once({"name": of}, entries), table.parent)
            else:
                factors[fname] = as_factor(f, table.parent)
            key = {k: v for k, v in f.items() if k not in ("name", "source")}
            if written.setdefault(fname, key) != key:
                refuse(f"factor {fname!r}: same name with different values")
        chains.setdefault((name, policy_key(r)), []).append(r)
    for r in rows:  # a modelled effect's factors are the estimate it replaced; a fact it depends on is its model's input
        for f in r.get("factor", []) if "draws" in r else ():
            of = factors.get(f.get("complement_of", f["name"]), {})
            if of.get("form") == "bernoulli":
                refuse(f"effect {r['name']!r}: a yes-or-no fact ({of['name']!r}) in a modelled effect is two of its"
                       f" model's inputs, not a factor of a row with draws: its chance, named {of['name']!r}, with the"
                       f" factor's low, middle and high as its 5th, 50th and 95th percentiles, and {of['name'] + FACT!r},"
                       " uniform from 0 to 1; the model takes the fact as yes in a draw where the second is below the first")
    frame = read_frame(doc, rows, table)
    readings = frame.readings

    def drawn_factor(fname: Any, what: str) -> str:
        """A factor a frame key or a row's start or years names, drawn from its entry where no row states it."""
        if not isinstance(fname, str) or fname not in factors and fname not in entries:
            refuse(f"{what} names {fname!r}, which is no factor of the table: state it as a [factors.<name>] entry")
        if fname not in factors:
            factors[fname] = as_factor(stated_once({"name": fname}, entries), table.parent)
        return fname

    rate = drawn_factor(readings[0].drawn, "discount_rate") if readings[0].drawn else None
    for r in rows:
        timed = [k for k in ("start", "years") if k in r]
        if timed and (rate is None or "draws" in r):
            refuse(f"effect {r['name']!r}: {' and '.join(timed)} need the table's year, currency, guidance and"
                   " discount_rate, and a row of draws is discounted by its model")
        for k in timed:
            drawn_factor(r[k], f"effect {r['name']!r}: {k}")
        if "draws" in r and not isinstance(r["draws"], str if rate is None else dict):
            refuse(f"effect {r['name']!r}: draws names one file, or, in a table with a discount_rate, one file per"
                   f" reading: draws = {{ {', '.join(repr(x.label) for x in readings)} = <file> }}")
        if rate is not None and "draws" in r and set(cast(dict[str, str], r["draws"])) != {x.label for x in readings}:
            refuse(f"effect {r['name']!r}: draws names a file for each reading, {', '.join(x.label for x in readings)}")
    for c in sorted(frame.common):
        if c not in factors and c not in entries:
            refuse(f"common_values names {c!r}, which is no factor of the table; a misspelt name would weight its rows twice")
    if frame.weighted:
        drawn_factor(frame.elasticity, "elasticity")
        if frame.life_year:
            drawn_factor(frame.life_year, "life_year")
        for gname in {r["group"] for r in rows} | {cast(str, frame.reference)} | ({frame.bar_group} if frame.bar_group else set[str]()):
            drawn_factor(frame.groups[gname]["income"], f"[groups.{gname}] income")
    agree_with_inputs(factors, table.parent / "inputs.toml")
    convert: dict[str, float] = {}  # each money factor's price ratio, the table's year over its own
    names_currency = unit_currency_matcher({frame.currency} if frame.currency else set())
    for fname, f in factors.items():
        money = [k for k in MONEY if k in f]
        if money and frame.year is None:
            refuse(f"factor {fname!r}: currency and price_year need the table's year, currency and guidance")
        if frame.year is None or "complement_of" in f:
            continue
        if names_currency(str(f["unit"])):
            refuse(f"factor {fname!r}: unit {f['unit']!r} names a currency; give it as currency and price_year")
        if money and len(money) < 2:
            refuse(f"factor {fname!r}: money carries both currency and price_year")
        if money and f["currency"] != frame.currency:
            refuse(f"factor {fname!r}: currency {f['currency']!r} is not the table's {frame.currency}; money in another"
                   " currency is not converted until a case needs it")
        if money and f["price_year"] not in frame.index:
            refuse(f"factor {fname!r}: price_year {f['price_year']!r} is not a year of {frame.guidance}'s price index")
        if money:
            convert[fname] = frame.index[frame.year] / frame.index[f["price_year"]]
    for r in rows if frame.currency else ():  # every effect of a table with a currency is money, converted exactly once
        priced = [f["name"] for f in r.get("factor", []) if f["name"] in convert]
        if r.get("factor") and len(priced) != 1:
            refuse(f"effect {r['name']!r}: in a table in {frame.currency} each chain holds exactly one factor with currency"
                   f" and price_year, its money, and this one holds {len(priced)}"
                   + (f" ({', '.join(priced)})" if priced else ""))
    one_lever = len(levers) == 1 and set(policies) == set(next(iter(levers.values())))
    keys: list[str] = next(iter(levers.values())) if one_lever else []
    for key in policies if draws else ():
        if str(key) in ("", ".", "..") or Path(str(key)).name != str(key) or not one_lever and ("+" in key or key == "base"):
            refuse(f"policy {key!r}: under --draws a policy names a file, so it must be one path component, and where"
                   " sets of policies are written, joined by +, neither hold + nor be named base")
    ends: dict[str, tuple[float, float, float]] = {}
    for fname, f in factors.items():
        if "complement_of" not in f:
            ends[fname] = (f["low"], f["middle"], f["high"])
    for fname, f in factors.items():
        if "complement_of" in f:
            of = factors.get(f["complement_of"])
            if of is None:
                refuse(f"factor {fname!r}: complement_of names {f['complement_of']!r}, which is not a factor of the table")
            if "complement_of" in of:
                refuse(f"factor {fname!r}: complement_of names {of['name']!r}, itself a complement; name the chance it complements")
            if of["unit"] != "probability" and of["form"] != "logit-normal":
                refuse(f"factor {fname!r}: complement_of names {of['name']!r}, which is neither unit probability nor"
                       " form logit-normal")
            ends[fname] = (1 - of["high"], 1 - of["middle"], 1 - of["low"])

    blocks = restated = 0
    for rs in chains.values():
        for r in rs:
            fs = r.get("factor", [])
            if not fs and any(end not in r for end in ENDS):
                refuse(f"effect {r['name']!r}: a row of draws with no factors needs its low, middle and high stated")
            gaps: list[float] = []
            for end, number in zip(ENDS, corners([ends[f["name"]] for f in fs])) if fs else ():
                given = r.get(end, number)
                gaps.append(abs(given - number) / abs(number) if number else 0.0 if given == 0 else math.inf)
                if gaps[-1] > SLIP:
                    refuse(f"effect {r['name']!r}: stated {end} {r[end]} but its factors give {number:.6g}")
                if end not in r or gaps[-1] > SAME:
                    r[end] = number
            blocks, restated = blocks + bool(fs), restated + (max(gaps, default=0.0) > SAME)
    for (name, option), rs in chains.items():
        if option is not None and (name, None) in chains:
            refuse(f"effect {name!r}: has rows with a policy and rows with none; a row with none is in every set")
        given_w = [r["weight"] for r in rs if "weight" in r]
        if given_w and (len(given_w) < len(rs) or min(given_w) < 0 or abs(sum(given_w) - 1) > 1e-9):
            refuse(f"effect {name!r}: chain weights must all be given, non-negative and sum to 1")
        for r in rs:
            r["weight"] = r.get("weight", 1 / len(rs))

    def files_of(r: dict[str, Any]) -> list[str]:
        return [r["draws"]] if isinstance(r["draws"], str) else list(cast(dict[str, str], r["draws"]).values())

    files = list(dict.fromkeys(f for rs in chains.values() for r in rs if "draws" in r for f in files_of(r)))
    model_draws, (seed, n, method) = read_draws(files, table.parent)
    for fname, f in factors.items():
        if f.get("form") == "bernoulli" and fname + FACT in factors:
            refuse(f"factor {fname + FACT!r}: its name is the bernoulli {fname!r}'s second stream; rename it")
    rng = np.random.default_rng(seed)
    drawn = {fname: factor_draw(f, n, seed, method) for fname, f in factors.items() if "complement_of" not in f}
    for fname, f in factors.items():  # each complement after the factor it names
        if "complement_of" in f:
            drawn[fname] = 1 - drawn[f["complement_of"]]
    for fname, ratio in convert.items():  # money to the table's year, once per factor wherever it is used
        drawn[fname] = drawn[fname] * ratio
    if rate is not None and np.any(drawn[rate] <= -1):
        refuse(f"factor {rate!r}: a discount rate draws at or below -1")
    timed = [r for r in rows if "start" in r or "years" in r]
    for fname in {r[k] for r in timed for k in ("start", "years") if k in r}:
        if np.any(drawn[fname] < 0):
            refuse(f"factor {fname!r}: a start or a number of years draws below zero; name a form that cannot")
    span = max((float(np.max(sum((drawn[r[k]] for k in ("start", "years") if k in r), np.zeros(n))))
                for r in timed), default=0.0)
    grids: dict[str, tuple[Vec, Vec]] = {}
    for rd in readings:
        if rd.schedule is not None and timed:
            try:
                d = discount_factors(rd.schedule, np.arange(cast(int, frame.year), cast(int, frame.year) + math.ceil(span) + 2),
                                     cast(int, frame.year))
            except ValueError as e:
                refuse(f"guidance {frame.guidance}: discount rate {rd.label}: {e}")
            grids[rd.label] = (d, np.concatenate(([0.0], np.cumsum(d[1:]))))

    def multiplier(r: dict[str, Any], rd: Reading, value: Any) -> Vec | float:
        """A row's discount at a reading, `value(name)` giving each timing factor and the rate: draws or middles."""
        return discounted(rd, value(r["start"]) if "start" in r else None, value(r["years"]) if "years" in r else None,
                          value(rd.drawn) if rd.drawn else None, grids.get(rd.label))

    weight: dict[str, Vec] = {}
    if frame.weighted:
        ref, eps = drawn[frame.groups[cast(str, frame.reference)]["income"]], drawn[cast(str, frame.elasticity)]
        weight = {g: (ref / drawn[x["income"]]) ** eps for g, x in frame.groups.items() if x["income"] in drawn}
    public = {g for g, x in frame.groups.items() if x.get("public")}
    sums: list[dict[tuple[Key, str | None, bool], Vec]] = [{} for _ in readings]  # (policy, group at lead, weighted)

    def gather(k: int, key: Key, group: str | None, weighted: bool, x: Vec) -> None:
        here = sums[k]
        here[(key, group, weighted)] = here[(key, group, weighted)] + x if (key, group, weighted) in here else x

    effects: list[dict[str, Any]] = []
    values: list[Vec] = []  # each effect's leading total at the leading reading
    paid: list[Vec | None] = []  # each effect's dollars to the public groups at the leading reading
    picks: dict[str, Vec] = {}  # one uniform number per effect name per draw picks its chain, under every option
    for (name, pkey), rs in chains.items():
        signs = [1.0 if r["kind"] == "benefit" else -1.0 for r in rs]  # each chain counts in its own row's direction
        base = [None if "draws" in r else np.prod([drawn[f["name"]] for f in r["factor"]], axis=0) for r in rs]
        weights = [float(r["weight"]) for r in rs]
        if name not in picks:
            picks[name] = rng.random(n)
        cdf = np.cumsum(weights)  # the arithmetic of numpy's Generator.choice, on a number kept by name
        pick = np.searchsorted(cdf / cdf[-1], picks[name], side="right")
        unweighted = [any(f["name"] in frame.common for f in r.get("factor", [])) for r in rs]

        def picked(k: int, weighted: bool) -> Vec:
            rd = readings[k]
            per = [sg * (model_draws[r["draws"] if isinstance(r["draws"], str) else r["draws"][rd.label]] if b is None
                         else b * multiplier(r, rd, drawn.__getitem__))
                   * (weight[r["group"]] if weighted and not common else 1.0)
                   for r, sg, b, common in zip(rs, signs, base, unweighted)]
            return np.stack(per)[pick, np.arange(n)]

        groups_of = [r.get("group") for r in rs]
        v = picked(0, False)
        for k in range(len(readings)):
            for weighted in (False, True) if frame.weighted else (False,):
                x = v if k == 0 and not weighted else picked(k, weighted)
                if k == 0 and weighted == (frame.lead == "weighted"):
                    values.append(x)
                for g in dict.fromkeys(groups_of) if k == 0 else [None]:
                    mask = np.isin(pick, [i for i, h in enumerate(groups_of) if h == g])
                    gather(k, pkey, g, weighted, x if k or mask.all() else np.where(mask, x, 0.0))
        mine = [i for i, g in enumerate(groups_of) if g in public]
        paid.append(np.where(np.isin(pick, mine), v, 0.0) if mine else None)
        expected = float(v.mean())

        def middle_of(f: Any) -> Any:
            return np.array([factors[f]["middle"] * convert.get(f, 1.0)])
        middle = sum(w * sg * r["middle"] * math.prod(convert.get(f["name"], 1.0) for f in r.get("factor", []))
                     * float(np.asarray(multiplier(r, readings[0], middle_of)).item(0))
                     for w, sg, r in zip(weights, signs, rs))
        kinds = {r["kind"] for r in rs}
        above, below = v[v > 0], v[v < 0]
        signed = bool(above.size and below.size)
        p05, p95 = float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95))
        crosses = p05 < 0 < p95  # zero inside the 90 per cent interval: a ratio to a middle that may be near zero means nothing
        flagged = not crosses and abs(expected) > 3 * abs(middle)
        tail = None
        if flagged or signed:
            mag = np.abs(v)
            tail = float(mag[mag > np.quantile(mag, 0.95)].sum() / mag.sum())
        effects.append({
            "name": name, "kind": kinds.pop() if len(kinds) == 1 else "mixed", "expected": expected,
            "standard_error": standard_error(v), "median": float(np.median(v)),
            "p05": p05, "p95": p95,
            "share_above_zero": above.size / n, "mean_if_above": float(above.mean()) if above.size else None,
            "mean_if_above_se": standard_error(above) if above.size > 1 else None,
            "mean_if_below": float(below.mean()) if below.size else None,
            "mean_if_below_se": standard_error(below) if below.size > 1 else None, "signed": signed,
            "flagged": flagged, "tail_share": tail,
            "chains": [{**{k: float(r[k]) for k in ("low", "middle", "high", "weight")}, "kind": r["kind"],
                        "group": r.get("group")} for r in rs],
        })

    ekeys = [key for _, key in chains]

    def quantities(r: dict[str, Any]) -> set[str]:
        """The drawn quantities a row's leading value rests on: its factors, the chance a complement is one minus, its
        start and years with the drawn rate that discounts them, and, where the weighted total leads, the incomes and
        elasticity of its group's weight (none in the reference group's, whose weight is 1 in every draw)."""
        if "draws" in r:
            return set()
        q = {factors[f["name"]].get("complement_of", f["name"]) for f in r["factor"]} | {f["name"] for f in r["factor"]}
        timing = {r[k] for k in ("start", "years") if k in r}
        q |= timing | ({readings[0].drawn} if timing and readings[0].drawn else set())
        g = r.get("group")
        if frame.lead == "weighted" and g is not None and g != frame.reference \
                and not any(f["name"] in frame.common for f in r["factor"]):
            q |= {frame.groups[g]["income"], frame.groups[cast(str, frame.reference)]["income"], cast(str, frame.elasticity)}
        return q

    uses = [set[str]().union(*(quantities(r) for r in rs)) for rs in chains.values()]

    def ranked(mine: list[int]) -> tuple[dict[str, Any], Vec]:
        """One total of the effects `mine`, with `shared_factors`: each drawn quantity that two or more differently named
        effects of it rest on, and its main-effect index on the total with the index's batch standard error."""
        s, total = summary([effects[i] for i in mine], [values[i] for i in mine], n)
        names: dict[str, set[str]] = {}
        for i in mine:
            for q in uses[i]:
                names.setdefault(q, set()).add(effects[i]["name"])
        s["shared_factors"] = {q: shared_index(total, drawn[q], n) for q in sorted(names) if len(names[q]) >= 2}
        return s, total

    def part(s: frozenset[str]) -> tuple[dict[str, Any], Vec]:
        """One set's total: the effects of its policies, its joint rows and those with no policy."""
        return ranked([i for i, key in enumerate(ekeys) if inside(key, s)])

    def headline(s: frozenset[str] | None) -> tuple[dict[str, Any], Vec]:
        """The readings, the account by group, the outlay and the excess-burden reading of the whole table (None) or
        of one set, and its leading total's draws."""
        def add(group: Any, weighted: bool, k: int = 0) -> Vec:
            xs = [x for (key, g, w), x in sums[k].items()
                  if w == weighted and (group is True or g == group) and (s is None or inside(key, s))]
            return np.sum(xs, axis=0) if xs else np.zeros(n)
        found: list[dict[str, Any]] = []
        for k, rd in enumerate(readings):
            found.append({"label": rd.label, "rate": rd.rate, "dollars": totaled([add(True, False, k)], n)[0],
                          "weighted": totaled([add(True, True, k)], n)[0] if frame.weighted else None,
                          "life_years": totaled([add(True, True, k) / drawn[frame.life_year]], n)[0]
                          if frame.life_year else None})
        dollars = add(True, False)
        lead = add(True, True) if frame.lead == "weighted" else dollars
        spent: Vec = -np.sum([add(g, False) for g in public], axis=0) if public else np.zeros(n)
        outlay = float(spent.mean())
        cash: Vec = np.zeros(n)  # the same outlay paid as cash to bar_group, weighted: each public group's net cost moved
        for g in public if frame.bar_group else ():
            cash = cash - add(g, False) * (weight[cast(str, frame.bar_group)] - weight[g])
        return {"lead": frame.lead, "readings": found,
                "groups": {g: {"dollars": totaled([add(g, False)], n)[0],
                               "weighted": totaled([add(g, True)], n)[0] if frame.weighted else None}
                           for g in frame.groups},
                "outlay": {"expected": outlay, "standard_error": standard_error(spent)},
                "excess_burden": None if frame.burden is None else
                {"rate": frame.burden, "dollars": totaled([dollars - frame.burden * spent], n)[0]},
                "per_public_dollar": float(lead.mean()) / outlay if outlay else None,
                "cash": None if frame.bar_group is None else {"group": frame.bar_group, **dict(zip(
                    ("weighted", "net_of_cash"), (totaled([x], n)[0] for x in (cash, add(True, True) - cash))))}}, lead

    out: dict[str, Any] = {"draws": n, "seed": seed, "sampling": method}
    money = frame.currency or "as stated"  # the unweighted figures' unit: the table's currency, or its rows' own units
    print(f"{n} draws, seed {seed}, sampling {method}")
    totals: dict[str, Vec] = {}
    leading: frozenset[str] | None = None
    if not policies:
        whole, _ = ranked(list(range(len(effects))))
        out.update(whole)
        show(whole, quiet, frame.lead, money)
    elif one_lever:
        parts = {key: part(frozenset({key})) for key in keys}
        totals = {key: total for key, (_, total) in parts.items()}
        peak: Vec = np.max(list(totals.values()), axis=0)
        out["options"] = {key: s for key, (s, _) in parts.items()}
        out["highest"] = {key: float(np.mean(total >= peak)) for key, total in totals.items()}
        out["highest_se"] = {key: standard_error((total >= peak).astype(np.float64)) for key, total in totals.items()}
        out["beats"] = {a: {b: float(np.mean(totals[a] > totals[b])) for b in keys if b != a} for a in keys}
        figures = (separating_figures([out["options"][key]["total"]["expected"] for key in keys]),
                   separating_figures([out["options"][key]["total"]["median"] for key in keys]))
        for key in keys:
            print(f"\noption {key}")
            show(out["options"][key], quiet, frame.lead, money, figures)
        print("\nacross options, on the same draws")
        print("share of draws in which each option's total is the highest: "
              + "; ".join(f"{key} {percent(share)}" for key, share in out["highest"].items()))
        print("share of draws in which the row's total is above the column's:")
        columns([["", *keys], *([a, *("-" if a == b else percent(out["beats"][a][b]) for b in keys)] for a in keys)], 1)
    if policies:
        found, kept, peak = policy_sets(effects, ekeys, values, paid, policies, levers, n, draws and not one_lever)
        out.update(found)
        if not one_lever:
            totals = {"+".join(s) or "base": total for s, total in kept.items()}
            print(f"\nthe leading set: {' + '.join(found['leading']) or 'no policy'}")
            out["leading_set"], lead_draws = part(frozenset(found["leading"]))
            show(out["leading_set"], quiet, frame.lead, money)
            out["value_of_information"] = choice_value(
                [frozenset(e["policies"]) for e in found["sets"]], lead_draws, peak, ekeys, values,
                uses, drawn, found["enumeration"]["all"])
        show_sets(found, quiet)
        if not one_lever:
            show_choice(out["value_of_information"], found["enumeration"]["evaluated"])
        leading = frozenset(found["leading"])
    top, lead_total = headline(leading)
    if not policies:
        totals = {"total": lead_total}
    out.update(top)
    show_headline(top, frame)
    out["restated"] = restated
    out["factors"] = {fname: {"form": form_of(factors[f.get("complement_of", fname)]), "mean": float(drawn[fname].mean()),
                              "standard_error": standard_error(drawn[fname]),
                              **({"parameters": f["parameters"], **{k: f[k] for k in ENDS}} if "spec" in f else {})}
                      for fname, f in factors.items()}
    families = {f["form"] for f in factors.values() if "spec" in f}
    out["method"] = method_block(n, seed, method, families) | frame_method(frame)
    print(f"blocks with a stated low, middle or high restated as the product of its factors: {restated} of {blocks}")
    results.mkdir(parents=True, exist_ok=True)
    (results / "estimate_total.json").write_text(json.dumps(out, indent=2) + "\n")
    if draws:
        (results / "estimate_total_draws").mkdir()
        for key, total in totals.items():
            sampling.write_draws(results / "estimate_total_draws" / f"{key}.txt", total, random_seed=seed, iterations=n,
                                 sampling_method=method)

CHANGE_KEYS = {"replace": ("do", "factor", "effect", "file", "key", "value", "reason"),
               "drop": ("do", "effect", "file", "reason"), "merge": ("do", "effects", "into", "reason")}
ROW_EDITS = ("kind", "who", "group", "start", "years", "weight", "option", "policy", *ENDS)
BARE = re.compile(r"[A-Za-z0-9_-]+")
Rows = list[tuple[str, dict[str, Any]]]  # (file, row), in table order


def toml_value(v: Any) -> str:
    """A value as TOML; a float by repr, which reads back to the same float."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)  # a JSON string is a TOML basic string; written as itself
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in cast(list[Any], v)) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{toml_key(k)} = {toml_value(x)}" for k, x in cast(dict[str, Any], v).items()) + "}"
    refuse(f"a value {v!r} of a type the assembler does not write")


def toml_key(k: str) -> str:
    return k if BARE.fullmatch(k) else json.dumps(k, ensure_ascii=False)


def fences(text: str) -> list[tuple[str, str]]:
    """Each ```toml fence's lines, with the nearest Markdown heading line above it (outside any fence)."""
    out: list[tuple[str, str]] = []
    heading, body, other = "", cast(list[str] | None, None), False
    for line in text.splitlines():
        if body is not None:
            if line.startswith("```"):
                out.append((heading, "\n".join(body)))
                body = None
            else:
                body.append(line)
        elif other:
            other = not line.startswith("```")
        elif line.startswith("```toml"):
            body = []
        elif line.startswith("```"):
            other = True
        elif line.startswith("#"):
            heading = line
    return out


def read_estimates(fname: str, blocks: list[str]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """A file's rows and its [factors] entries, from the TOML of the given fences, read as one document."""
    try:
        doc = tomllib.loads("\n".join(blocks))
    except tomllib.TOMLDecodeError as e:
        refuse(f"{fname}: the TOML inside its fences does not parse: {e}")
    unknown(fname, doc, ("effect", "factors", "lever"))  # the frame keys are the author's, in changes.toml
    return cast(list[dict[str, Any]], doc.get("effect", [])), cast(dict[str, dict[str, Any]], doc.get("factors", {}))


def apply_change(c: dict[str, Any], rows: Rows, what: str) -> tuple[Rows, set[str]]:
    """One change applied to one table's rows: the rows after it, and the names it found there."""
    do = c["do"]
    if do == "merge":
        pair_ = cast(list[str], c["effects"])
        found = {e for e in pair_ if any(r.get("name") == e for _, r in rows)}
        for e in found:
            mine = [(fname, r) for fname, r in rows if r.get("name") == e]
            for _, r in mine:
                group = [(fname, x) for fname, x in mine if policy_of(x) == policy_of(r)]
                if "weight" not in r:
                    stating = [fname for fname, x in group if "weight" in x]
                    if stating:
                        bare = next(fname for fname, x in group if x is r)
                        refuse(f"{what}: a chain of {e!r} in {bare} states no weight, but a chain of it in {stating[0]}"
                               " states one; give every chain of the effect its weight by a replace with `file`")
            for _, r in mine:
                group_n = sum(1 for _, x in mine if policy_of(x) == policy_of(r))
                r["weight"] = 0.5 * r.get("weight", 1 / group_n)
        for _, r in rows:
            if r.get("name") in pair_:
                r["name"] = c["into"]
        return rows, found
    if do == "replace" and "factor" in c:
        hits = [f for _, r in rows for f in r["factor"] if f.get("name") == c["factor"]]
        for f in hits:
            f[c["key"]] = c["value"]
        return rows, {c["factor"]} if hits else set()
    hit = [i for i, (fname, r) in enumerate(rows) if r.get("name") == c.get("effect") and c.get("file", fname) == fname]
    if do == "drop":
        rows = [x for i, x in enumerate(rows) if i not in hit]
    else:
        for i in hit:
            rows[i][1][c["key"]] = c["value"]
    return rows, {c["effect"]} if hit else set()


def table_text(rows: Rows, files: list[str], heading: str | None, frame: dict[str, Any],
               loose: dict[str, dict[str, Any]]) -> tuple[str, int]:
    """One table as TOML: changes.toml's frame keys, each factor stated in two or more files written once, and each
    [factors] entry no row states, such as a group's income; and how many factors were written once."""
    stated: dict[str, list[tuple[str, dict[str, Any]]]] = {}  # each factor name: (file, statement) wherever stated
    for fname, r in rows:
        for f in r["factor"]:
            if "complement_of" not in f and "name" in f:
                stated.setdefault(f["name"], []).append((fname, f))
    def spec(f: dict[str, Any]) -> dict[str, Any]:
        """What makes two statements of a factor one quantity: every key but its name and source, which changes no
        number (unit, low, middle, high, form, money, or a `distribution` and its fields)."""
        return {k: v for k, v in f.items() if k not in ("name", "source")}

    entries: dict[str, dict[str, Any]] = {}
    for name, where in stated.items():
        full = [(fname, f) for fname, f in where if spec(f)]  # a missing key is a difference
        for fname, f in full[1:]:
            a, b = spec(full[0][1]), spec(f)
            if a != b:
                diff = ", ".join(f"{k} {a.get(k)!r} against {b.get(k)!r}" for k in sorted(a.keys() | b.keys())
                                 if a.get(k) != b.get(k))
                refuse(f"factor {name!r} is stated differently in {full[0][0]} and {fname} ({diff}); make them one by a"
                       " replace of the factor in changes.toml, with its reason")
        if full and len({fname for fname, _ in where}) > 1:
            entry = spec(full[0][1])
            sources = {f.get("source") for _, f in full}
            if len(sources) == 1 and None not in sources:
                entry["source"] = sources.pop()
            entries[name] = entry
    for _, r in rows:
        r["factor"] = [f if f.get("name") not in entries else
                       {k: v for k, v in f.items() if k == "name" or k == "source" and k not in entries[f["name"]]}
                       for f in r["factor"]]
    under = "" if heading is None else f" under headings containing {heading!r}"
    out = ["# The table of estimates, assembled by tools/estimate_total.py assemble from estimates/changes.toml:",
           f"# the blocks of {', '.join(files)}{under}, with the changes listed there, each with its reason.", ""]
    out += [f"{k} = {toml_value(v)}" for k, v in frame.items() if k != "groups"]
    for name, g in cast(dict[str, dict[str, Any]], frame.get("groups", {})).items():
        out += ["", f"[groups.{toml_key(name)}]", *(f"{k} = {toml_value(v)}" for k, v in g.items())]
    out.append("")
    for name, entry in [*entries.items(), *((k, e) for k, e in loose.items() if k not in stated)]:
        out += [f"[factors.{toml_key(name)}]", *(f"{k} = {toml_value(v)}" for k, v in entry.items()), ""]
    for fname, r in rows:
        out += [f"# from estimates/{fname}", "[[effect]]"]
        out += [f"{toml_key(k)} = {toml_value(v)}" for k, v in r.items() if k != "factor"]
        if r["factor"]:
            out += ["factor = [", *(f"  {toml_value(f)}," for f in r["factor"]), "]"]
        out.append("")
    return "\n".join(out), len(entries)


def assemble(case: Path) -> None:
    folder = case / "estimates"
    try:
        spec = tomllib.loads((folder / "changes.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        refuse(f"{folder / 'changes.toml'}: {e}")
    unknown("changes.toml", spec, ("files", "change", "table", *FRAME_KEYS))
    files = cast(list[str], spec.get("files", []))
    if not files:
        refuse("changes.toml: `files` lists no estimator file")
    for p in sorted(folder.glob("*.md")):
        if p.name not in files and fences(p.read_text(encoding="utf-8")):
            refuse(f"{p.name} holds ```toml blocks but changes.toml's `files` does not list it")
    targets: list[tuple[Path, str | None]] = [(case / "estimates.toml", None)]
    if "table" in spec:
        targets = []
        for t in cast(list[dict[str, Any]], spec["table"]):
            unknown("changes.toml's [[table]]", t, ("path", "heading"))
            if not isinstance(t.get("path"), str) or not isinstance(t.get("heading"), str) or not t["heading"]:
                refuse(f"changes.toml's [[table]] {toml_value(t)}: a table names its `path` and `heading`")
            targets.append((case / cast(str, t["path"]), cast(str, t["heading"])))
        if not targets:
            refuse("changes.toml: `table` lists no table")
    blocks: dict[str, list[tuple[str, str]]] = {}
    for fname in files:
        if not (folder / fname).is_file():
            refuse(f"{fname}: listed in changes.toml's `files` but not in {folder}")
        blocks[fname] = fences((folder / fname).read_text(encoding="utf-8"))
        for heading, _ in blocks[fname]:
            if not any(h is None or h in heading for _, h in targets):
                refuse(f"{fname}: a ```toml block under the heading {heading!r} goes to no [[table]] of changes.toml")
    tables: list[Rows] = []
    looses: list[dict[str, dict[str, Any]]] = []  # each table's [factors] entries, by name, for those no row states
    for _, h in targets:
        rows: Rows = []
        loose: dict[str, dict[str, Any]] = {}
        for fname in files:
            file_rows, entries = read_estimates(fname, [b for hd, b in blocks[fname] if h is None or h in hd])
            for name, e in entries.items():
                if loose.setdefault(name, e) != e:
                    refuse(f"factor {name!r} is stated differently in two files' [factors] entries; make them one")
            for r in file_rows:
                r["factor"] = [{**entries[f["name"]], **f} if f.get("name") in entries else f
                               for f in r.get("factor", [])]
                rows.append((fname, r))
        tables.append(rows)
        looses.append(loose)

    for c in cast(list[dict[str, Any]], spec.get("change", [])):
        what = f"change {toml_value(c)}"
        do = c.get("do")
        if do not in CHANGE_KEYS:
            refuse(f"{what}: `do` must be replace, drop or merge")
        unknown(what, c, CHANGE_KEYS[do])
        if not str(c.get("reason", "")).strip():
            refuse(f"{what}: a change needs a reason")
        if do == "merge":
            if len(cast(list[str], c.get("effects", []))) != 2 or "into" not in c:
                refuse(f"{what}: a merge names two effects and `into`")
        elif do == "replace" and "factor" in c:
            if "effect" in c or "file" in c or c.get("key") not in ENTRY_KEYS or "value" not in c:
                refuse(f"{what}: a replace of a factor names `factor`, `key` ({', '.join(ENTRY_KEYS)}) and `value`")
        elif do == "replace" and (c.get("key") not in ROW_EDITS or "value" not in c):
            refuse(f"{what}: a replace of a row names `effect`, `key` ({', '.join(ROW_EDITS)}) and `value`")
        found: set[str] = set()
        per_table: list[set[str]] = []
        for i, rows in enumerate(tables):
            tables[i], here = apply_change(c, rows, what)
            found |= here
            per_table.append(here)
        if do == "replace" and "factor" in c:
            if not found:
                refuse(f"{what}: no row of any table states a factor {c['factor']!r}")
            continue
        for e in cast(list[str], c["effects"]) if do == "merge" else [c.get("effect")]:
            if e not in found:
                refuse(f"{what}: no row of any table is named {e!r}" + (f" in {c['file']}" if "file" in c else ""))
        if do == "merge" and not any(len(here) == 2 for here in per_table):
            where = "; ".join(f"{e!r} in {', '.join(str(t[0]) for t, here in zip(targets, per_table) if e in here)}"
                              for e in cast(list[str], c["effects"]))
            refuse(f"{what}: a merge needs both effects in one table, but they sit in different tables ({where})")

    frame = {k: spec[k] for k in FRAME_KEYS if k in spec}
    texts = [table_text(rows, files, h, frame, loose) for rows, (_, h), loose in zip(tables, targets, looses)]
    for (path, _), rows, (text, n) in zip(targets, tables, texts):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}: {len(rows)} rows, {n} factors stated once")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["assemble"]:
        if len(args) != 2:
            sys.exit("usage: estimate_total.py assemble cases/<case>")
        assemble(Path(args[1]))
        sys.exit(0)
    out_dir: Path | None = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            sys.exit("usage: estimate_total.py [--quiet] [--draws] [--out DIR] cases/<case>/estimates.toml")
        out_dir = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    paths = [a for a in args if a not in ("--quiet", "--draws")]
    if len(paths) != 1:
        sys.exit("usage: estimate_total.py [--quiet] [--draws] [--out DIR] cases/<case>/estimates.toml")
    main(Path(paths[0]), quiet="--quiet" in args, draws="--draws" in args, results=out_dir)
