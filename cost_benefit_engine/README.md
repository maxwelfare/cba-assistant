# Cost-benefit engine: the toolbox

This folder holds tools for building a cost-benefit model: input distributions, sampling, time shapes, discounting and summaries. Use a tool as it is by importing it, or copy it into your case and edit it there. Never edit the engine during a case: the change could alter the results of other cases that use it. Each tool is checked against independent anchors, such as closed forms and accounting identities, never against an earlier output of the same code.

Two modules are the general case runner (code that runs a whole case written as data): `case.py` and `run.py`. A case's own model does not call them. The other modules are tools a model may call.

1. Case runner (not for a model to call)
   1.1. `case.py`
      1.1.1. `load(folder, ...)`: reads a case folder, checks every file and returns a `Case`, or raises `CaseError` listing every problem. `case.py:207`
      1.1.2. `Case`: the loaded case, with its frame, inputs, sources, tables, streams and rank correlations. `case.py:186`
      1.1.3. `CaseError`: the refusal, holding every problem found. `case.py:137`
      1.1.4. `Problem`: one problem, saying where, which field and what is wrong. `case.py:128`
      1.1.5. `DiscountSchedule`: one discount rate as year ranges with a rate each, and its source. `case.py:146`
      1.1.6. `PriceStep`: the price-index step of a money conversion. `case.py:158`
      1.1.7. `Conversion`: how one money input is brought to the case's currency and price year. `case.py:173`
      1.1.8. `flat_rate(case, label)`: the one rate of a discount schedule, refusing an unknown label or a schedule with more than one rate; for a case's run script, checked against the closed-form discount and annuity factors when it landed, with no kept test. `case.py:217`
   1.2. `run.py`
      1.2.1. `run(case, model, ...)`: draws the inputs, runs the model once per option and returns a `Run`; options let you override iterations and seed or hold inputs at stated values; it refuses any draw on which net present value is not benefits less costs, so a case need not check that itself. `run.py:244`
      1.2.2. `evaluate(case, model, uniforms, ...)`: the same run on uniform numbers you supply. `run.py:298`
      1.2.3. `model_from(case)`: loads the case's `model.py` and returns its model function. `run.py:170`
      1.2.4. `Run`: every draw, present value, net present value and benefit-cost ratio per option and discount rate. `run.py:54`
      1.2.5. `RunError`: a refusal naming the input, option or key at fault. `run.py:49`
      1.2.6. `stream_increments(r, label, option, base)`: each stream's present value in one option less that in another, per draw, refusing a label, option or base the run lacks; for a case's run script, checked against the closed forms and the accounting identity when it landed, with no kept test. `run.py:762`
2. Tools a model may call
   2.1. `distributions.py`
      2.1.1. `quantile(spec, u)`: turns an input's entry (kind and parameters) and uniform numbers in (0, 1) into draws. `distributions.py:356`
      2.1.2. `choose(spec, u)`: draws the outcomes of a categorical input. `distributions.py:389`
      2.1.3. `component(spec, u)`: which top-level component of a mixture each draw picked. `distributions.py:379`
      2.1.4. `pick(spec, u)`: that component index, with the uniform rescaled within the component's share. `distributions.py:323`
      2.1.5. `metalog_coefficients(spec)`: the fitted coefficients of a metalog input. `distributions.py:227`
      2.1.6. `fields(distribution)`: the required and optional parameter names of a distribution kind. `distributions.py:65`
   2.2. `sampling.py`
      2.2.1. `uniforms(names, iterations, random_seed, sampling_method, ...)`: uniform numbers strictly inside (0, 1) for each name. `sampling.py:114`
      2.2.2. `correlate(u, rank_correlations)`: imposes stated rank correlations between named uniform columns. `sampling.py:223`
      2.2.3. `sheet_uniforms(tab_position, column, iterations, ...)`: the spreadsheet template's pseudo-random numbers, to match a sheet twin. `sampling.py:146`
   2.3. `timeline.py`
      2.3.1. `appraisal_years(first, last)`: the array of calendar years of the appraisal. `timeline.py:99`
      2.3.2. `discount_factors(schedule, years, base_year)`: one factor per year from a year-by-year rate schedule. `timeline.py:151`
      2.3.3. `present_value(stream, factors)`: discounts a draws-by-years stream to a present value per draw. `timeline.py:170`
      2.3.4. `one_off(amount, year, years, iterations=)`: an amount in one year. `timeline.py:187`
      2.3.5. `annual(amount, first, last, years, iterations=)`: the same amount every year from first to last. `timeline.py:197`
      2.3.6. `every_n_years(amount, period, first, last, years, iterations=)`: a replacement cycle. `timeline.py:202`
      2.3.7. `linear_phase_in(amount, start, full, last, years, iterations=)`: a flow rising in equal steps to its full amount. `timeline.py:219`
      2.3.8. `bring_forward(stream, by, years)`: shifts a stream earlier by a number of years. `timeline.py:241`
   2.4. `outputs.py`
      2.4.1. `summary(values)`: mean, 5th, 50th and 95th percentiles and sign shares of one result, NaN counted and left out. `outputs.py:66`
      2.4.2. `prcc(inputs, output)`: partial rank correlation of each input with an output, to rank what drives the result. `outputs.py:110`
      2.4.3. `convergence(values, checkpoints)`: mean, standard error and top-1% share at each checkpoint, to judge whether enough draws were run. `outputs.py:150`
      2.4.4. `standard_error(values)`: the Monte Carlo standard error of a mean of draws, the one `convergence` and `tools/estimate_total.py` report. `outputs.py:143`
      2.4.5. `Summary`: the result `summary` returns. `outputs.py:28`
      2.4.6. `Checkpoint`: one row of `convergence`. `outputs.py:42`
   2.5. `quotes.py`
      2.5.1. `normalise(text)`: plain-text form (Unicode, dashes, quotes, line-end hyphens, spaces) for comparing quotes. `quotes.py:20`
      2.5.2. `quote_in(quote, text)`: whether a quote occurs in a source text, `...` allowed between parts. `quotes.py:27`
   2.6. `basics.py`
      2.6.1. `CheckFailed`: A check of the run failed: the run stops and writes nothing. `basics.py:25`
      2.6.2. `f64(a)`: . `basics.py:29`
      2.6.3. `need(inputs, name)`: An input's draws as floats, in any number of dimensions; a missing input raises a KeyError naming it. `basics.py:39`
      2.6.4. `pick_method(inputs, name, by_method)`: Each draw's value from the array of its own outcome of the categorical input `name`. `basics.py:44`
      2.6.5. `summary_dict(values)`: `outputs.summary` of `values`, as a plain dict for a results file. `basics.py:62`
      2.6.6. `sha256(path)`: . `basics.py:67`
      2.6.7. `provenance(command, root, files, include_engine)`: What this run reads and in what state; call it when the run starts, not after. `basics.py:77`
   2.7. `analysis.py`
      2.7.1. `prcc_columns(draws, rows, inputs_read)`: Name to 1-D float array, ready for `outputs.prcc`, with every column that has no spread dropped. `analysis.py:46`
      2.7.2. `ranked_prcc(columns, output)`: `outputs.prcc(columns, output)` ordered by descending absolute value, any NaN last. `analysis.py:66`
      2.7.3. `per_event_breakdown(events, per_year, present_value)`: The factors of a stream's mean present value: events x value per event x time factor. `analysis.py:71`
   2.8. `value_of_information.py`
      2.8.1. `SPLINE_KNOTS`: a constant. `value_of_information.py:34`
      2.8.2. `evpi(net_benefits)`: The expected value of perfect information: what it is worth to know every uncertainty before choosing. `value_of_information.py:68`
      2.8.3. `evppi(net_benefits, key, fit, bins)`: The expected value of partial perfect information on `key`, one input's draws. `value_of_information.py:73`
      2.8.4. `noise_floor(net_benefits, key, rng, permutations, fit, bins)`: The largest `evppi` over `permutations` random permutations of `key`, each drawn from `rng`. `value_of_information.py:83`
      2.8.5. `end(output, key, p, half)`: one end of an input's tornado bar, as (x, value, standard error) with x the key's p quantile. The value estimates the input's main effect E[output | key = x], every other input drawn as it was (Oakley and O'Hagan 2004), by a local linear fit over the draws within `half` of p in rank on either side, with the intercept's HC0 standard error, calibrated at the returned x. It equals the one-way bar that holds the other inputs at their means only where, for each x, the output is multilinear in the other inputs and they are independent. Checked when it landed, with no kept test, against the closed forms of E[output | input = x] for six inputs at 200,000 draws (within 4 standard errors), the identity output = 3 + 2·key (exact to 1e-9), and the fit and HC0 sandwich written out by hand. `value_of_information.py:105`
   2.9. `documents.py`
      2.9.1. `MINUS`: a constant. `documents.py:26`
      2.9.2. `SCALES`: a constant. `documents.py:27`
      2.9.3. `SUMMARY_HEAD`: the header of the table `summary_row` fills. `documents.py:28`
      2.9.4. `FillError`: A template, or a value it asks for, that cannot be filled. `documents.py:40`
      2.9.5. `lookup(data, path, separator)`: The value at `path`: per step, a key of a mapping or a whole-number index of a list. `documents.py:44`
      2.9.6. `money(x, figures=2, words_from=1e6)`: Dollars, rounded to `figures` significant figures first, a trailing zero kept, and then scaled by the largest word not above the rounded size, once that size is at least `words_from`; `figures=None` prints the value as stored: 9.96e8 is $1.0 billion, and with `None` 87.45 is $87.45. `documents.py:90`
      2.9.7. `significant(x, figures=2)`: a number to `figures` significant figures, the float's binary value rounded with ties to even and a trailing zero kept, or with `None` the value as stored: 0.5 is 0.50, 9.96 is 10. `documents.py:101`
      2.9.8. `percent(x, figures=2)`: A proportion as a percentage to `figures` significant figures: 0.1234 is 12%. A share below one that rounds to 100 prints "more than 99%" (99.9 at three figures), and one above one that rounds to exactly 100 "more than 100%"; a negative x is a change, rounded plainly. `documents.py:107`
      2.9.9. `percentage_points(x, figures=2, signed=False)`: A difference of proportions in points, to `figures` significant figures, 0.0012 being 0.12 points: its magnitude only, unless `signed`. `documents.py:125`
      2.9.10. `signed(x, decimals)`: a coefficient at fixed decimals, with its sign. `documents.py:143`
      2.9.11. `FORMATS`: the named number formats a template may use, and the one place they are named. `documents.py:165`

      | format | what it shows | example |
      |---|---|---|
      | `money` | dollars to two figures, a scale word from a million | 9.96e8: $1.0 billion |
      | `sig` | a number to two figures | 0.5: 0.50 |
      | `pct` | a share to two figures; "more than 99%" just below 100%, "more than 100%" just above | 0.1234: 12% |
      | `pp` | a difference of shares in points, two figures | 0.1234: 12 percentage points |
      | `int` | a whole number, for a count | 4200: 4,200 |
      | `year` | a year, refusing a fraction | 2026: 2026 |
      | `cited` | a value as its source states it | 87.45: 87.45 |
      | `money_cited` | dollars as the source states them | 86300000.0: $86.3 million |
      | `signed2` | a coefficient, two decimals and its sign | 0.4567: +0.46 |
      | `pct0` to `pct2` | a share at 0, 1 or 2 decimals, in "per cent" | 0.1234, `pct1`: 12.3 per cent |
      | `raw` | Python's shortest form, for a distribution's parameters | 4.249e9: 4.249e+09 |

      2.9.12. `reference_list(order, sources, methods)`: One numbered line per `(book, key)` of `order`: the citation up to " Stored:", then its DOI, URL or link. `documents.py:193`
      2.9.13. `fill_template(template, results, sources, methods, tables, formats, separator)`: The template filled. `documents.py:204`
      2.9.14. `input_table(inputs, guidance, cite)`: A markdown table of a case's `inputs.toml` entries, one row each; an official-guidance money value prints as its source states it, `money(v, None)`. `documents.py:279`
      2.9.15. `prcc_list(prcc, at_least)`: A numbered list, in the order given, of the coefficients whose unrounded magnitude is at least `at_least`. `documents.py:293`
      2.9.16. `results_header(res)`: One sentence saying how the results file was made. `documents.py:299`
      2.9.17. `summary_row(name, s, fmt)`: one table row of mean, 5th percentile, median and 95th percentile, each rounded on its own at `fmt`'s default (`money`: two figures), so neighboring values can print alike; separating them is left to the review texts. `documents.py:310`
      2.9.18. `separating_figures(values, show=significant)`: the least count of figures, from 2 to 6, at which the distinct `values` print as distinct strings through `show` (`significant`, `money` or `percent`), or 6 if none does: 5120 and 5140 need 3. `documents.py:133`
      2.9.19. `read_display(case)`, `Display`, `formats_for(display)`: a case's one `[display]` table (`significant_figures`, `unit`, `period`), in a fenced ```toml block of its `requirements.md` or else `design.md`, and the engine's formats with `money` and `sig` at its figures. `documents.py:354`
      2.9.20. `compare(case, previous)`, run as `python -m cost_benefit_engine.documents compare <case> <previous>`: each line of the rebuilt `<case>/documents/*.md` that differs from the file of its name in the folder `previous`, by `<file>:<line>`, and each number on it that is not a rounding of the same stored value in the case's `results` folders as the number in its place in the previous build, has no such number, or shows more figures than the display table allows; exits 1 on a wrong number. `documents.py:450`
      2.9.21. `annex_a(table, figures=2)`, `annex_b(case)`: the technical appendix's annexes in Markdown, every effect and factor of a table of estimates, each factor with its form and the mean of its draws from the total tool's results beside the table, and the requirements with the list of review reports, for the case's documents script to append after the appendix's main text. `documents.py:547`
      2.9.22. `method_tables(case)`: `{{TABLE method_annex}}`, the total tool's method as the case's run states it in `results/estimate_total.json` (`method`): the draws, seed and sampling, each form, and how means, shares of variance, dependence and sets are computed; the appendix's method section prints it rather than paraphrasing it. `documents.py:600`
   2.10. `draws_table.py`: a table of draws, one uncompressed `.npz` holding the header line of `sampling.write_draws` and, draw by draw, every input a model drew and every output it computed. A table holds what its producer drew and nothing else: an input the producer did not write has no column, so no figure drawn from the table can show it.
      2.10.1. `write_table(path, inputs, outputs, random_seed=, iterations=, sampling_method=)`: writes the table, refusing a column of another length, a value that is not finite, an empty name, no outputs, and a field `write_draws` would refuse; checked when it landed, with no kept test, by a round trip that returned every column exactly. `draws_table.py:59`
      2.10.2. `read_table(path)`: the `DrawsTable`, refusing a missing or malformed header, any other key and a column of another length. `draws_table.py:82`
      2.10.3. `DrawsTable`: the table's `inputs` and `outputs` (name to float array), `random_seed`, `iterations` and `sampling_method`. `draws_table.py:29`
