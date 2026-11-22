"""The draws of tools/estimate_total.py, the total of a case's table of estimates, against closed forms.

The tool reports the mean of its draws; a closed form enters here only as an independent check that each reported
mean lies within four Monte Carlo standard errors of the distribution's expectation (the owner, 2026-11-17: "The mean
of random draws is the only source of truth"). Every factor of the table below is a lognormal with high/middle =
middle/low = 2, so both its halves have s = ln 2 / z95, its mean is middle * exp(s^2 / 2) = middle * LIFT and its
second moment middle^2 * LIFT^4. A product of independent factors has the product of their moments, an effect of kind
cost counts negative, and an option's total is the sum of its effects. A factor's low, middle and high are its 5th,
50th and 95th percentiles, checked on the one-factor option within 1 per cent, about five standard errors of a
percentile of 200,000 draws.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from statistics import NormalDist

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "estimate_total.py"
N = 200_000  # the tool's draws when no draws file sets them
S = math.log(2) / NormalDist().inv_cdf(0.95)
LIFT = math.exp(S * S / 2)  # mean / middle of a lognormal with high/middle = middle/low = 2

# Three effects under two options; the factor "visits" is shared by alpha and beta.
TABLE = """\
[[effect]]
name = "alpha"
kind = "benefit"
option = "build"

[[effect.factor]]
name = "visits"
unit = "visits per year"
low = 5.0
middle = 10.0
high = 20.0

[[effect.factor]]
name = "value_per_visit"
unit = "dollars"
low = 1.5e8
middle = 3e8
high = 6e8

[[effect]]
name = "beta"
kind = "cost"
option = "build"

[[effect.factor]]
name = "visits"
unit = "visits per year"
low = 5.0
middle = 10.0
high = 20.0

[[effect.factor]]
name = "cost_per_visit"
unit = "dollars"
low = 5e7
middle = 1e8
high = 2e8

[[effect]]
name = "gamma"
kind = "benefit"
option = "wait"

[[effect.factor]]
name = "saving"
unit = "dollars"
low = 2e8
middle = 4e8
high = 8e8
"""


def test_expected_totals_and_percentiles_in_closed_form(tmp_path: Path) -> None:
    table = tmp_path / "estimates.toml"
    table.write_text(TABLE)
    done = subprocess.run([sys.executable, str(TOOL), "--quiet", str(table)], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    options = json.loads((tmp_path / "results" / "estimate_total.json").read_text())["options"]

    def near(got: float, mean: float, second: float) -> None:
        """got within four standard errors of the mean, the standard error sqrt((second - mean^2) / N)."""
        assert abs(got - mean) < 4 * math.sqrt((second - mean**2) / N), (got, mean)

    build = {e["name"]: e["expected"] for e in options["build"]["effects"]}
    near(build["alpha"], 10 * 3e8 * LIFT**2, (10 * 3e8) ** 2 * LIFT**8)
    near(build["beta"], -10 * 1e8 * LIFT**2, (10 * 1e8) ** 2 * LIFT**8)
    # visits times (value less cost): E[V^2] E[(A - C)^2], A and C independent
    near(options["build"]["total"]["expected"], 10 * LIFT * (3e8 - 1e8) * LIFT,
         100 * LIFT**4 * (9e16 * LIFT**4 - 2 * 3e8 * 1e8 * LIFT**2 + 1e16 * LIFT**4))

    wait = options["wait"]["total"]
    near(wait["expected"], 4e8 * LIFT, 16e16 * LIFT**4)
    assert (wait["p05"], wait["median"], wait["p95"]) == pytest.approx((2e8, 4e8, 8e8), rel=0.01)
