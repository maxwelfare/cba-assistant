"""The arithmetic of cost_benefit_engine/run.py, each piece once, on a small case written here, against hand values.

1. Present values, net present value and the benefit-cost ratio of one option: the annuity factor
   (1 - (1 + r)^-T) / r, within 1e-12 of the draw's gross present value.
2. Two options against a base case that has flows of its own: each present value as the sum of flow times
   (1 + r)^-t written out here, each increment as the option's less the base case's, net present value as the
   benefits' increment less the costs', and the ratio undefined where the costs' increment is not positive.
3. Money: an input's draw times the ratio of two price index values written into the guidance editions below, times
   the drawn exchange rate; a mixture of two moneys by the bracket rule (the uniform number among the cumulative
   weights, rescaled within its share). A uniform input's draw is min + u * (max - min).
4. Money in another currency already at the price base year (the rate alone, no price step), and money on an input
   indexed by a table (each row's draws times the price ratio and that draw's rate).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from cost_benefit_engine import case as case_module
from cost_benefit_engine import run as run_module

Floats = NDArray[np.float64]
REL = 1e-12

# Index values off any round base, so an inverted or misread ratio cannot pass.
F_TLD_2020 = 100.4 / 81.3
F_OTD_2018 = 63.1 / 47.9

_INDEX = """\
publisher = "A statistics office"
document = "National accounts, annual"
url = "https://example.org/deflator.csv"
date_read = "2030-01-01"
quote = "Implicit price deflator, calendar year"
licence = "CC BY 4.0"
guidance_document = "Appraisal guide"
guidance_url = "https://example.org/guide"
guidance_quote = "Use the GDP deflator."
"""

TESTLAND = f"""\
jurisdiction = "Testland"
edition = "2030-01-01"

[discount_rate]
rates = [0.05, 0.03]
unit = "real rate per year"
document = "Testland Treasury, Appraisal guide"
url = "https://example.org/guide"
quote = "Use real discount rates of 5 and 3 per cent."
licence = "CC BY 4.0"

[price_index]
currency = "TLD"
series = "TLD GDP deflator"
{_INDEX}calendar_year = {{ 2018 = 77.7, 2020 = 81.3, 2030 = 100.4 }}
"""

OTHERLAND = f"""\
jurisdiction = "Otherland"
edition = "2031-06-30"

[price_index]
currency = "OTD"
series = "OTD GDP deflator"
{_INDEX}calendar_year = {{ 2018 = 47.9, 2030 = 63.1 }}
"""

CASE = """\
decision_question = "Should Testland do the thing?"
unit_of_analysis = "one thing"
options = ["status_quo", "do_it"]
base_case = "status_quo"
appraisal_first_year = 2030
appraisal_last_year = 2039
discount_base_year = 2030
price_base_year = 2030
currency = "TLD"
jurisdiction = "testland"
guidance_edition = "2030-01-01"
iterations = 64
random_seed = 11
sampling_method = "latin_hypercube"
authoritative_model = "python"

[other_guidance_editions]
otherland = "2031-06-30"

[streams.cost1]
kind = "cost"
label = "Cost of the thing"
borne_by = "the treasury"

[streams.benefit1]
kind = "benefit"
label = "Benefit of the thing"
received_by = "residents"

[intermediate_results.r1]
label = "Cost per unit of benefit"
unit = "ratio"
"""

_JUDGED = """\
evidence_type = "analyst_judgement"
judged_by = "a tester"
rationale = "a stated reason"
"""


def _uniform(name: str, lo: float, hi: float, unit: str = "per thing", extra: str = "") -> str:
    return f'[{name}]\nlabel = "A judged quantity"\nunit = "{unit}"\ndistribution = "uniform"\nmin = {lo}\nmax = {hi}\n{extra}{_JUDGED}\n'


INPUTS = (
    _uniform("cost", 100, 200)
    + _uniform("benefit", 10, 30)
    + _uniform("foreign_old", 10, 20, extra='currency = "OTD"\nprice_year = 2018\n')
    + _uniform("otd_to_tld", 1.5, 1.7, unit="exchange rate", extra='from_currency = "OTD"\nto_currency = "TLD"\nrate_year = 2030\n')
    + '[mix]\nlabel = "Competing studies"\nunit = "per thing"\ndistribution = "mixture"\n'
    + f"components = {{ comp_a = 0.4, comp_b = 0.6 }}\n{_JUDGED}\n"
    + _uniform("comp_a", 900, 1100, extra='currency = "TLD"\nprice_year = 2020\n')
    + _uniform("comp_b", 600, 800, extra='currency = "OTD"\nprice_year = 2018\n')
)
SEEN = ("cost", "benefit", "foreign_old", "otd_to_tld", "mix")  # the inputs a model sees: every one but a mixture's components

# A one-off cost in the first year and a level benefit in every later year for `do_it`; nothing for the base case.
BASE_MODEL = '''
import numpy as np

def model(inputs, appraisal_years, option):
    n = inputs["cost"].shape[0]
    t = appraisal_years.shape[0]
    cost = np.zeros((n, t))
    benefit = np.zeros((n, t))
    if option == "do_it":
        cost[:, 0] = inputs["cost"]
        benefit[:, 1:] = inputs["benefit"][:, None]
    return {"cost1": cost, "benefit1": benefit, "r1": inputs["cost"] / inputs["benefit"]}
'''

# Three options, the base case with flows of its own; it records what it was given.
THREE_MODEL = '''
import numpy as np

SEEN = []

def model(inputs, appraisal_years, option):
    n, t = inputs["cost"].shape[0], appraisal_years.shape[0]
    SEEN.append((option, {k: np.array(v, copy=True) for k, v in inputs.items()}))
    c, b = inputs["cost"], inputs["benefit"]
    cost = np.zeros((n, t))
    benefit = np.zeros((n, t))
    if option == "status_quo":
        cost[:, :] = (0.1 * c)[:, None]
        benefit[:, :] = (0.2 * b)[:, None]
    elif option == "opt_a":
        cost[:, 0] = c
        benefit[:, 1:] = b[:, None]
    else:
        cost[:, 0] = 2 * c
        cost[:, 5] = c
        benefit[:, 2:] = (1.5 * b)[:, None]
    return {"cost1": cost, "benefit1": benefit, "r1": c + b}
'''


def _load(root: Path, case_toml: str = CASE, model: str = BASE_MODEL, inputs: str = INPUTS, extra: dict[str, str] | None = None) -> Any:
    files = {
        "jurisdiction_guidance/testland/2030-01-01.toml": TESTLAND,
        "jurisdiction_guidance/otherland/2031-06-30.toml": OTHERLAND,
        "cases/demo/case.toml": case_toml,
        "cases/demo/inputs.toml": inputs,
        "cases/demo/sources.toml": "",
        "cases/demo/model.py": model,
        **(extra or {}),
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return case_module.load(root / "cases" / "demo", root / "jurisdiction_guidance")


def _rates(case: Any) -> dict[str, float]:
    """Each constant schedule's label and rate, read from the loaded case (written in the edition above)."""
    out: dict[str, float] = {}
    for s in case.real_discount_rates:
        assert len(s.rows) == 1 and s.rows[0][:2] == (1, None)
        out[s.label] = s.rows[0][2]
    assert sorted(out.values()) == [0.03, 0.05]
    return out


def _close(actual: Any, expected: Any, rel: float = REL) -> None:
    a = np.asarray(actual, dtype=np.float64)
    e = np.asarray(expected, dtype=np.float64)
    assert a.shape == e.shape, (a.shape, e.shape)
    assert np.all(np.abs(a - e) <= rel * np.maximum(np.abs(e), 1e-300)), np.max(np.abs(a - e) / np.abs(e))


def test_closed_form_constant_rates(tmp_path: Path) -> None:
    case = _load(tmp_path)
    r = run_module.run(case, run_module.model_from(case))
    T = 9  # benefits in years 1 to 9 after the 2030 base year; the cost in year 0
    for label, rate in _rates(case).items():
        annuity = (1 - (1 + rate) ** -T) / rate
        b, c = r.draws["benefit"], r.draws["cost"]
        gross = b * annuity + c
        npv = r.net_present_value[label]["do_it"]
        assert np.all(np.abs(npv - (b * annuity - c)) <= 1e-12 * gross)
        _close(r.benefit_cost_ratio[label]["do_it"], b * annuity / c)
        _close(r.present_values[label]["do_it"]["cost1"], c)
        _close(r.benefits_increment[label]["do_it"], b * annuity)
        _close(r.costs_increment[label]["do_it"], c)
    assert list(r.years) == list(range(2030, 2040))


def _pv(stream: Floats, rate: float) -> Floats:
    out = np.zeros(stream.shape[0])
    for t in range(stream.shape[1]):
        out = out + stream[:, t] * (1 + rate) ** -t
    return out


def test_two_options_against_a_base_case(tmp_path: Path) -> None:
    case = _load(tmp_path, CASE.replace('["status_quo", "do_it"]', '["status_quo", "opt_a", "opt_b"]'), THREE_MODEL)
    model = run_module.model_from(case)
    r = run_module.run(case, model)
    calls = cast(list[Any], model.__globals__["SEEN"])
    assert [x[0] for x in calls] == ["status_quo", "opt_a", "opt_b"]
    first = calls[0][1]
    for _, given in calls[1:]:  # every option is given the same draws
        assert set(given) == set(first) == set(SEEN)
        for k in first:
            assert np.array_equal(given[k], first[k]), k
    c, b = first["cost"], first["benefit"]
    n, t = c.shape[0], 10
    hand: dict[str, dict[str, Floats]] = {}
    for opt in ("status_quo", "opt_a", "opt_b"):
        cost, benefit = np.zeros((n, t)), np.zeros((n, t))
        if opt == "status_quo":
            cost[:, :], benefit[:, :] = (0.1 * c)[:, None], (0.2 * b)[:, None]
        elif opt == "opt_a":
            cost[:, 0], benefit[:, 1:] = c, b[:, None]
        else:
            cost[:, 0], cost[:, 5], benefit[:, 2:] = 2 * c, c, (1.5 * b)[:, None]
        hand[opt] = {"cost1": cost, "benefit1": benefit}
    for label, rate in _rates(case).items():
        pv = {o: {s: _pv(a, rate) for s, a in hand[o].items()} for o in hand}
        for o in hand:
            for s in pv[o]:
                _close(r.present_values[label][o][s], pv[o][s])
        assert "status_quo" not in r.net_present_value[label]
        for o in ("opt_a", "opt_b"):
            db = pv[o]["benefit1"] - pv["status_quo"]["benefit1"]
            dc = pv[o]["cost1"] - pv["status_quo"]["cost1"]
            gross = sum(np.abs(pv[x][s]) for x in (o, "status_quo") for s in ("cost1", "benefit1"))
            _close(r.benefits_increment[label][o], db, 1e-11)
            _close(r.costs_increment[label][o], dc, 1e-11)
            assert np.all(np.abs(r.net_present_value[label][o] - (db - dc)) <= 1e-12 * gross)
            ratio = r.benefit_cost_ratio[label][o]
            assert np.all(np.isnan(ratio[dc <= 0]))
            _close(ratio[dc > 0], (db / dc)[dc > 0], 1e-10)


def test_money_conversion(tmp_path: Path) -> None:
    case = _load(tmp_path)
    rng = np.random.default_rng(3)
    u = {name: rng.uniform(0.001, 0.999, size=200) for name in SEEN}  # uniforms this file draws itself
    r = run_module.evaluate(case, run_module.model_from(case), u)
    rate = 1.5 + u["otd_to_tld"] * 0.2
    assert np.array_equal(r.draws["otd_to_tld"], r.raw_draws["otd_to_tld"].own_units())  # a rate is never converted
    _close(r.draws["otd_to_tld"], rate)
    raw = 10 + u["foreign_old"] * 10
    _close(r.raw_draws["foreign_old"].own_units(), raw)
    _close(r.draws["foreign_old"], raw * F_OTD_2018 * rate)
    # The mixture in two moneys, by the bracket rule: weights 0.4 then 0.6.
    um = u["mix"]
    a = um <= 0.4
    expected = np.where(a, (900 + 200 * (um / 0.4)) * F_TLD_2020, (600 + 200 * ((um - 0.4) / 0.6)) * F_OTD_2018 * rate)
    _close(r.draws["mix"], expected)
    assert np.array_equal(r.picks["mix"], np.where(a, 0, 1))
    # An input with no money is untouched.
    _close(r.draws["cost"], 100 + 100 * u["cost"])


def test_money_at_the_base_year_and_on_an_indexed_input(tmp_path: Path) -> None:
    # `at_base` is in OTD at the price base year 2030, so its price factor is 1 and only the rate applies:
    # draw = (10 + 10 u) * rate. `by_region` is in OTD at 2018, indexed by a two-row table: row j's draw is
    # (lo_j + u_j (hi_j - lo_j)) * (63.1 / 47.9) * rate, the same rate draw for both rows of one iteration.
    inputs = (
        _uniform("cost", 100, 200)
        + _uniform("benefit", 10, 30)
        + _uniform("otd_to_tld", 1.5, 1.7, unit="exchange rate", extra='from_currency = "OTD"\nto_currency = "TLD"\nrate_year = 2030\n')
        + _uniform("at_base", 10, 20, extra='currency = "OTD"\nprice_year = 2030\n')
        + '[by_region]\nlabel = "A judged quantity by region"\nunit = "per thing"\ndistribution = "uniform"\n'
        + 'indexed_by = "regions"\nmin = { column = "lo" }\nmax = { column = "hi" }\n'
        + f'currency = "OTD"\nprice_year = 2018\n{_JUDGED}\n'
    )
    table = "region,lo,hi\nnorth,1,2\nsouth,30,50\n"
    case = _load(tmp_path, inputs=inputs, extra={"cases/demo/data/regions.csv": table})
    rng = np.random.default_rng(5)
    n = 200
    u: dict[str, Floats] = {name: rng.uniform(0.001, 0.999, size=n) for name in ("cost", "benefit", "otd_to_tld", "at_base")}
    u["by_region"] = rng.uniform(0.001, 0.999, size=(n, 2))
    r = run_module.evaluate(case, run_module.model_from(case), u)
    rate = 1.5 + u["otd_to_tld"] * 0.2
    _close(r.draws["at_base"], (10 + 10 * u["at_base"]) * rate)
    ub = u["by_region"]
    expected = np.column_stack([1 + ub[:, 0] * 1, 30 + ub[:, 1] * 20]) * F_OTD_2018 * rate[:, None]
    _close(r.draws["by_region"], expected)
