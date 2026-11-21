"""The statistics of cost_benefit_engine/sampling.py, each once, against a reference outside the code.

1. Latin hypercube sampling: one value in each stratum [k/n, (k+1)/n), by counting (McKay, Beckman and Conover 1979).
2. Rank correlation: Iman and Conover (1982), Communications in Statistics - Simulation and Computation
   11(3):311-334. The targets are the stated Spearman values, measured here with scipy.stats.spearmanr on columns
   this file draws itself; the tolerance is 0.01. On this fixture a reference implementation of the method misses
   by at most 0.0023, and by 0.0205 without the rank-to-normal conversion 2 sin(pi rho / 6) or 0.0191 without the
   correction for the sample's own correlation, so an implementation missing either fails.
"""

from __future__ import annotations

import copy
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.stats import spearmanr

from cost_benefit_engine.sampling import correlate, uniforms

Arr = NDArray[np.float64]


def test_latin_hypercube_fills_every_stratum_once() -> None:
    n = 1000
    got = uniforms(["p", "q", "r"], n, 3, sampling_method="latin_hypercube", columns={"r": ["a", "b"]})
    for c in (got["p"], got["q"], got["r"][:, 0], got["r"][:, 1]):
        assert c.shape == (n,)
        assert np.all((c > 0.0) & (c < 1.0))
        np.testing.assert_array_equal(np.sort(np.floor(c * n)), np.arange(n, dtype=np.float64))


# The group a, b, c, d, e has three stated correlations and an explicit zero between d and e; its six unnamed pairs
# are tested against 0. The pair f, g is a group of its own.
N = 10_000
GROUP = ["a", "b", "c", "d", "e"]
ENTRIES: list[tuple[str, str, float]] = [("a", "b", 0.3), ("a", "c", 0.6), ("c", "d", -0.6), ("d", "e", 0.0)]
PAIR: list[tuple[str, str, float]] = [("f", "g", 0.9)]


def fixture_u() -> dict[str, Arr]:
    """Latin hypercube columns drawn here, independently of the module, in the order a..g, and one no correlation names."""
    rng = np.random.default_rng([2026, 0])
    u: dict[str, Arr] = {}
    for name in [*GROUP, "f", "g", "z"]:
        u[name] = (rng.permutation(N) + rng.random(N)) / N
        assert np.all(u[name] > 0.0)
    return u


def spearman(x: Arr, y: Arr) -> float:
    return float(cast(Any, spearmanr(x, y)).statistic)


def test_correlate_reaches_targets_and_leaves_values() -> None:
    u = fixture_u()
    before = copy.deepcopy(u)
    out = correlate(u, ENTRIES + PAIR)
    for a, b, rho in ENTRIES + PAIR:
        assert abs(spearman(out[a], out[b]) - rho) < 0.01, (a, b, rho)
    named = {frozenset((a, b)) for a, b, _ in ENTRIES}
    for i, a in enumerate(GROUP):
        for b in GROUP[i + 1 :]:
            if frozenset((a, b)) not in named:
                assert abs(spearman(out[a], out[b])) < 0.01, (a, b)
    for name, arr in u.items():
        np.testing.assert_array_equal(arr, before[name])  # the caller's arrays unchanged
        np.testing.assert_array_equal(np.sort(out[name]), np.sort(arr))  # each input keeps its own values
    np.testing.assert_array_equal(out["z"], u["z"])
