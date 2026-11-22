"""The arithmetic of cost_benefit_engine/distributions.py, each kind once, against a reference outside the code.

1. The seven template kinds: each inverse distribution function in closed form, written out here.
2. The metalog: Keelin, T. W. (2016), "The Metalog Distributions", Decision Analysis 13(4):243-277, by the page
   numbers of the author's manuscript: the basis, equation (6), page 16; the bounded forms, equations (11) to (14),
   pages 24 and 25; the three-term closed form, Proposition 1, equations (18) and (19), page 37; the three-term
   feasibility bound, Proposition 2, equation (20), page 39 (k0 = 1.66711).
3. SciPy kinds, the empirical kind and the mixture's bracket rule: closed forms and hand calculations.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy import stats

from cost_benefit_engine.distributions import choose, component, metalog_coefficients, quantile

REL = 1e-12
META_REL = 1e-10
BELOW_ONE = math.nextafter(1.0, 0.0)

Spec = dict[str, Any]


def arr(*values: float) -> NDArray[np.float64]:
    return np.array(values, dtype=np.float64)


def close(got: NDArray[np.float64], want: NDArray[np.float64], rel: float) -> None:
    """Every element within rel of its expected value, relative to that value (all non-zero)."""
    assert got.shape == want.shape
    assert np.all(want != 0.0), "a relative tolerance needs non-zero expected values"
    err = np.abs(got / want - 1.0)
    assert float(np.max(err)) <= rel, (got, want, err)


# ---------------------------------------------------------------- 1. the template kinds, in closed form


def test_template_kinds_in_closed_form() -> None:
    u = arr(0.025, 0.3, 0.7, 0.975)

    close(quantile({"distribution": "constant", "mean": 4.2}, u), np.full(4, 4.2), REL)
    close(quantile({"distribution": "uniform", "min": 1.3, "max": 1.6}, u), 1.3 + 0.3 * u, REL)

    nd = NormalDist(10.0, 2.0)
    close(quantile({"distribution": "normal", "mean": 10, "sd": 2}, u), np.array([nd.inv_cdf(float(x)) for x in u]), REL)

    # A lognormal stated by its own mean and standard deviation (3 and 2): the normal underneath has
    # mu = ln(mean^2 / sqrt(mean^2 + sd^2)) and sigma^2 = ln(1 + sd^2 / mean^2).
    log_nd = NormalDist(math.log(9.0 / math.sqrt(13.0)), math.sqrt(math.log(1.0 + 4.0 / 9.0)))
    close(quantile({"distribution": "lognormal", "mean": 3, "sd": 2}, u), np.array([math.exp(log_nd.inv_cdf(float(x))) for x in u]), REL)

    lo, alpha = 2.0, 3.0
    close(
        quantile({"distribution": "power law", "min": lo, "alpha": alpha}, u),
        np.array([lo * (1 - float(x)) ** (-1 / (alpha - 1)) for x in u]),
        REL,
    )


def test_template_beta_scales_from_min_to_max() -> None:
    """min + (max - min) * the standard beta's quantile, with min not 0, so that min + max * quantile fails."""
    lo, hi, a, b = 2.0, 12.0, 2.0, 3.0
    u = arr(0.05, 0.3, 0.5, 0.8, 0.95)
    want = np.array([lo + (hi - lo) * float(stats.beta.ppf(float(x), a, b)) for x in u])
    close(quantile({"distribution": "beta", "min": lo, "max": hi, "alpha": a, "beta": b}, u), want, REL)


def test_template_triangular_both_sides_of_mode() -> None:
    lo, peak, hi = 1.0, 3.0, 7.0
    u = arr(0.05, 0.33, 0.34, 0.9)
    assert u[1] < (peak - lo) / (hi - lo) < u[2]

    def tri(x: float) -> float:
        if x <= (peak - lo) / (hi - lo):
            return lo + math.sqrt(x * (hi - lo) * (peak - lo))
        return hi - math.sqrt((1 - x) * (hi - lo) * (hi - peak))

    close(
        quantile({"distribution": "triangular", "min": lo, "mode": peak, "max": hi}, u),
        np.array([tri(float(x)) for x in u]),
        REL,
    )


# ---------------------------------------------------------------- 2. metalog, against Keelin 2016


def basis(y: NDArray[np.float64], n: int) -> NDArray[np.float64]:
    """Keelin 2016, equation (6), page 16: columns 1 to n in the paper's order."""
    big_l = np.log(y / (1 - y))
    c = y - 0.5
    cols: list[NDArray[np.float64]] = [np.ones_like(y), big_l, c * big_l, c]
    for k in range(5, n + 1):
        cols.append(c ** ((k - 1) // 2) if k % 2 == 1 else c ** (k // 2 - 1) * big_l)
    return np.stack(cols[:n], axis=1)


def spt_closed_form(alpha: float, low: float, mid: float, high: float) -> NDArray[np.float64]:
    """Proposition 1, equations (18)-(19), page 37."""
    ln_odds = math.log((1 - alpha) / alpha)
    r = (mid - low) / (high - low)
    return arr(
        mid,
        (high - low) / (2 * ln_odds),
        (1 - 2 * r) * (high - low) / ((1 - 2 * alpha) * ln_odds),
    )


def expit(z: NDArray[np.float64]) -> NDArray[np.float64]:
    return 1.0 / (1.0 + np.exp(-z))


def to_z(x: NDArray[np.float64], b: dict[str, float]) -> NDArray[np.float64]:
    """Keelin 2016, pages 24-25: the transform of x for each bounded form."""
    if "lower_bound" in b and "upper_bound" in b:
        return np.log((x - b["lower_bound"]) / (b["upper_bound"] - x))
    if "lower_bound" in b:
        return np.log(x - b["lower_bound"])
    if "upper_bound" in b:
        return -np.log(b["upper_bound"] - x)
    return x


def from_z(z: NDArray[np.float64], b: dict[str, float]) -> NDArray[np.float64]:
    """The inverse: equations (11) and (14) and the nlog form on page 24."""
    if "lower_bound" in b and "upper_bound" in b:
        return b["lower_bound"] + (b["upper_bound"] - b["lower_bound"]) * expit(z)
    if "lower_bound" in b:
        return b["lower_bound"] + np.exp(z)
    if "upper_bound" in b:
        return b["upper_bound"] - np.exp(-z)
    return z


# (bounds, alpha, x triplet), one per bounded form; every triplet is skewed in z, so a3 is not zero.
SPT_CASES: list[tuple[dict[str, float], float, tuple[float, float, float]]] = [
    ({}, 0.1, (2.0, 5.0, 12.0)),
    ({"lower_bound": 0.0}, 0.1, (1.0, 3.0, 10.0)),
    ({"upper_bound": 20.0}, 0.1, (5.0, 12.0, 16.0)),
    ({"lower_bound": 0.0, "upper_bound": 1.0}, 0.05, (0.05, 0.2, 0.6)),
]


@pytest.mark.parametrize(("bounds", "alpha", "x"), SPT_CASES, ids=["unbounded", "lower", "upper", "both"])
def test_metalog_three_term_closed_form(bounds: dict[str, float], alpha: float, x: tuple[float, float, float]) -> None:
    """A three-term fit to a symmetric percentile triplet equals Keelin's closed form, in each bounded form."""
    p = arr(alpha, 0.5, 1 - alpha)
    xs = np.array(x, dtype=np.float64)
    z = to_z(xs, bounds)
    want = spt_closed_form(alpha, float(z[0]), float(z[1]), float(z[2]))
    assert abs(float(z[0] + z[2] - 2 * z[1])) > 1e-3  # skewed: a3 is not zero
    spec: Spec = {"distribution": "metalog", "probabilities": [float(a) for a in p], "values": [float(b) for b in xs], **bounds}
    close(metalog_coefficients(spec), want, META_REL)
    close(quantile(spec, p), xs, META_REL)
    u = arr(0.01, 0.2, 0.37, 0.8, 0.99)
    close(quantile(spec, u), from_z(basis(u, 3) @ want, bounds), META_REL)


def test_metalog_recovers_known_coefficients() -> None:
    """Six terms: exact data from known coefficients on the paper's basis, as many pairs as terms and more (least squares)."""
    coef = arr(10.0, 2.0, 0.5, -1.0, 0.8, 0.3)
    n = coef.size
    p = np.linspace(0.05, 0.95, n)
    xs = basis(p, n) @ coef
    assert np.all(np.diff(xs) > 0)
    spec: Spec = {"distribution": "metalog", "probabilities": [float(s) for s in p], "values": [float(t) for t in xs]}
    close(metalog_coefficients(spec), coef, META_REL)
    u = arr(0.003, 0.15, 0.42, 0.66, 0.97)
    close(quantile(spec, u), basis(u, n) @ coef, META_REL)
    p9 = arr(0.02, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 0.98)
    x9 = basis(p9, n) @ coef
    spec9: Spec = {"distribution": "metalog", "probabilities": [float(s) for s in p9], "values": [float(t) for t in x9], "number_of_terms": n}
    close(metalog_coefficients(spec9), coef, META_REL)


def test_metalog_feasibility() -> None:
    """A quantile function that is not increasing is refused.

    Three terms, Proposition 2 (eq. 20, page 39): at alpha = 0.1 the bound on r is 0.166578; a triplet with
    r = 0.1675 is feasible, r = 0.1655 and its mirror r = 0.8345 are refused. Five terms, coefficients
    (0, 1, 0, 0, -12): dQ/dy = 1/(y(1-y)) - 24(y - 0.5), negative at y = 0.8 (6.25 - 7.2), while the pairs at
    0.05, 0.3, 0.5, 0.6, 0.7 increase.
    """
    k = 0.5 * (1 - 1.66711 * (0.5 - 0.1))
    assert abs(k - 0.166578) < 1e-9

    def triplet(r: float) -> Spec:
        return {"distribution": "metalog", "probabilities": [0.1, 0.5, 0.9], "values": [0.0, 1000.0 * r, 1000.0]}

    assert metalog_coefficients(triplet(0.1675)).shape == (3,)
    assert metalog_coefficients(triplet(0.8325)).shape == (3,)
    for r in (0.1655, 0.8345):
        with pytest.raises(ValueError):
            quantile(triplet(r), arr(0.5))

    p = arr(0.05, 0.3, 0.5, 0.6, 0.7)
    xs = basis(p, 5) @ arr(0.0, 1.0, 0.0, 0.0, -12.0)
    assert np.all(np.diff(xs) > 0)
    assert 1 / (0.8 * 0.2) - 24 * (0.8 - 0.5) < 0
    with pytest.raises(ValueError):
        quantile({"distribution": "metalog", "probabilities": [float(s) for s in p], "values": [float(t) for t in xs]}, arr(0.5))


# ---------------------------------------------------------------- 3. SciPy, empirical, mixture and choice


def test_scipy_closed_forms() -> None:
    """scipy.<name> is that distribution's quantile function, against closed forms and a hand-summed distribution function."""
    u = arr(1e-10, 0.3, 0.5, 0.9, 1 - 1e-10)
    expo = -np.log1p(-u)  # the same function as -ln(1 - u)
    close(quantile({"distribution": "scipy.expon"}, u), expo, REL)
    close(quantile({"distribution": "scipy.expon", "loc": 2.0, "scale": 3.0}, u), 2.0 + 3.0 * expo, REL)
    close(quantile({"distribution": "scipy.weibull_min", "c": 2.0, "scale": 1.5}, u), 1.5 * np.sqrt(expo), REL)

    # Poisson mu = 2: the quantile is the smallest k with P(X <= k) >= u.
    cdf = np.cumsum([math.exp(-2.0) * 2.0**k / math.factorial(k) for k in range(30)])
    uq = arr(0.1, 0.5, 0.95)
    want = np.array([float(np.argmax(cdf >= x)) for x in uq])
    assert list(want) == [0.0, 2.0, 5.0]
    assert list(quantile({"distribution": "scipy.poisson", "mu": 2.0}, uq)) == list(want)
    assert list(quantile({"distribution": "scipy.poisson", "mu": 2.0, "loc": 10}, uq)) == list(want + 10.0)


def test_empirical() -> None:
    """numpy's inverted_cdf by hand on (3, 1, 2, 5): sorted 1, 2, 3, 5 with F = 0.25, 0.5, 0.75, 1, the smallest value with F >= u."""
    u = arr(0.1, 0.25, 0.26, 0.5, 0.74, 0.99)
    close(quantile({"distribution": "empirical", "pool": [3.0, 1.0, 2.0, 5.0]}, u), arr(1, 1, 2, 2, 3, 5), REL)


UNIT = {"distribution": "uniform", "min": 0.0, "max": 1.0}
THIRDS: Spec = {
    "distribution": "mixture",
    "components": [{**UNIT, "weight": 0.25}, {**UNIT, "weight": 0.5}, {**UNIT, "weight": 0.25}],
}


def test_mixture_bracket_by_hand() -> None:
    """Cumulative weights (0.25, 0.75, 1), lower edges (0, 0.25, 0.75), each exact in binary.

    The draw of a uniform(0, 1) component is the rescaled u itself.
    u = 0.1  -> component 0, (0.1 - 0) / 0.25 = 0.4
    u = 0.25 -> component 0 (an edge belongs to the component below it), 1.0, clipped to the float below 1
    u = 0.5  -> component 1, (0.5 - 0.25) / 0.5 = 0.5
    u = 0.75 -> component 1, 1.0, clipped
    u = 0.8  -> component 2, (0.8 - 0.75) / 0.25 = 0.2
    u = 0.9  -> component 2, 0.6
    """
    u = arr(0.1, 0.25, 0.5, 0.75, 0.8, 0.9)
    got = quantile(THIRDS, u)
    assert got[1] == BELOW_ONE and got[3] == BELOW_ONE
    keep = np.array([0, 2, 4, 5])
    close(got[keep], arr(0.4, 0.5, 0.2, 0.6), REL)
    assert component(THIRDS, u).tolist() == [0, 0, 1, 1, 2, 2]

    outcomes = {"A": 0.25, "B": 0.5, "C": 0.25}
    assert choose({"distribution": "categorical", "outcomes": outcomes}, u).tolist() == ["A", "A", "B", "B", "C", "C"]
