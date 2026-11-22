"""The statistics of cost_benefit_engine/outputs.py, each once, against a reference outside the code.

1. The summary and the convergence table: hand arithmetic on small arrays, worked in the comments beside each
   figure, with percentiles by linear interpolation between order statistics at position p (n - 1) (numpy's
   default, Hyndman and Fan 1996 definition 7).
2. The partial rank correlation coefficient: its definition (Marino, Hogue, Ray and Kirschner 2008, J. Theor.
   Biol. 254:178-196), rebuilt below with scipy's rankdata and numpy's lstsq, within 1e-10; an input the output
   ignores falls inside the null band 3 / sqrt(2000).
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.stats import rankdata

from cost_benefit_engine.outputs import convergence, prcc, summary

Arr = NDArray[np.float64]


def test_summary_by_hand_with_nan() -> None:
    s = summary(np.array([3.0, -1.0, math.nan, 0.0, 7.0, 2.0]))
    # Non-NaN, sorted: -1, 0, 2, 3, 7; n = 5; sum 11.
    assert s.count == 5
    assert s.nan_count == 1
    assert s.mean == pytest.approx(2.2, abs=1e-12)
    # p5: position 0.05 * 4 = 0.2 -> -1 + 0.2 * (0 - (-1)) = -0.8
    assert s.p5 == pytest.approx(-0.8, abs=1e-12)
    # p50: position 2 -> 2
    assert s.p50 == pytest.approx(2.0, abs=1e-12)
    # p95: position 3.8 -> 3 + 0.8 * (7 - 3) = 6.2
    assert s.p95 == pytest.approx(6.2, abs=1e-12)
    # Above zero: 3, 7, 2 -> 3/5; below zero: -1 -> 1/5; the zero counts in neither.
    assert s.share_positive == pytest.approx(0.6, abs=1e-12)
    assert s.share_negative == pytest.approx(0.2, abs=1e-12)


def reference_prcc(columns: list[Arr], y: Arr) -> list[float]:
    """The definition, written here: rank, regress on the other ranks with an intercept, correlate."""
    ranks = [np.asarray(rankdata(c), dtype=np.float64) for c in columns]
    ry = np.asarray(rankdata(y), dtype=np.float64)
    n = y.size
    out: list[float] = []
    for i in range(len(ranks)):
        others = [ranks[j] for j in range(len(ranks)) if j != i]
        design = np.column_stack([np.ones(n), *others])
        bx = np.linalg.lstsq(design, ranks[i], rcond=None)[0]
        by = np.linalg.lstsq(design, ry, rcond=None)[0]
        ex = ranks[i] - design @ bx
        ey = ry - design @ by
        out.append(float(np.sum(ex * ey) / math.sqrt(float(np.sum(ex * ex)) * float(np.sum(ey * ey)))))
    return out


def test_prcc_matches_the_definition() -> None:
    n = 2000
    rng = np.random.default_rng(20261030)
    x1 = rng.normal(size=n)
    x2 = rng.uniform(size=n)
    x3 = rng.normal(size=n)
    # Rises with x1 (monotone, non-linear), falls with x2, ignores x3; noise keeps the coefficient below 1.
    y = np.exp(x1) - 3.0 * x2 + 0.5 * rng.normal(size=n)
    got = prcc({"first": x1, "second": x2, "third": x3}, y)
    want = reference_prcc([x1, x2, x3], y)
    assert set(got) == {"first", "second", "third"}
    for name, w in zip(["first", "second", "third"], want):
        assert abs(got[name] - w) <= 1e-10, name
    assert got["first"] > 0.0
    assert got["second"] < 0.0
    assert abs(got["third"]) <= 3.0 / math.sqrt(n)


def test_convergence_by_hand() -> None:
    got = convergence(np.array([1.0, 2.0, 3.0, 10.0]), [2, 4])
    assert [c.iterations for c in got] == [2, 4]
    # First 2: mean 1.5; sd = sqrt((0.25 + 0.25) / 1) = sqrt(0.5); se = sqrt(0.5) / sqrt(2) = 0.5;
    # k = 1, largest |value| is 2, share 2 / 3.
    assert got[0].mean == pytest.approx(1.5, abs=1e-12)
    assert got[0].standard_error == pytest.approx(0.5, abs=1e-12)
    assert got[0].top_share == pytest.approx(2.0 / 3.0, abs=1e-12)
    # All 4: mean 4; squared deviations 9 + 4 + 1 + 36 = 50; sd = sqrt(50 / 3); se = sd / 2;
    # largest |value| is 10, share 10 / 16.
    assert got[1].mean == pytest.approx(4.0, abs=1e-12)
    assert got[1].standard_error == pytest.approx(math.sqrt(50.0 / 3.0) / 2.0, abs=1e-12)
    assert got[1].top_share == pytest.approx(0.625, abs=1e-12)
    # By absolute value: -10, 1, 2, 3 sums to -4; the largest |value| is -10, share 2.5
    # (by signed value it would be 3, share -0.75).
    assert convergence(np.array([-10.0, 1.0, 2.0, 3.0]), [4])[0].top_share == pytest.approx(2.5, abs=1e-12)
    # k = floor(250 / 100) = 2 for 1..250: (250 + 249) / 31375 (ceil would take 3 values: 747 / 31375).
    v = np.arange(1.0, 251.0)
    assert convergence(v, [250])[0].top_share == pytest.approx(499.0 / 31375.0, abs=1e-12)
