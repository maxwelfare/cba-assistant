"""Each input kind's inverse distribution function, and the parameter names each kind takes.

`quantile(spec, u)` turns one input's entry in a case's `inputs.toml` (a mapping holding `distribution`
and the kind's parameters; other keys are ignored) and uniform numbers strictly inside (0, 1) into that
input's draws. `choose` draws a `categorical`; `component` reports which top-level component of a
`mixture` each draw picked (a nested mixture's inner pick is not reported), and `pick` gives that index with
the uniform rescaled within the component's share; `metalog_coefficients`
gives a metalog's fitted a1 to an on the transformed scale; `support` the least and greatest value an input can
draw. `fields(distribution)` gives a kind's
required and optional parameter names, for the loader to refuse a missing or unknown one.

The kinds are those of cases/README.md ("An input"): the owner's template's seven, computed as his
template formula computes them; `scipy.<name>`; `metalog`
(Keelin 2016, "The Metalog Distributions", Decision Analysis 13(4):243-277); `empirical`; `mixture`;
`categorical`. Every refusal is a ValueError naming the kind and the field.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import cast

import numpy as np
import scipy.stats
from numpy.typing import NDArray
from scipy.special import expit
from scipy.stats import rv_continuous, rv_discrete

Floats = NDArray[np.float64]

# The template's seven, with the parameters each uses (its row names).
TEMPLATE: dict[str, frozenset[str]] = {
    "beta": frozenset({"min", "max", "alpha", "beta"}),
    "constant": frozenset({"mean"}),
    "lognormal": frozenset({"mean", "sd"}),
    "normal": frozenset({"mean", "sd"}),
    "power law": frozenset({"min", "alpha"}),
    "triangular": frozenset({"min", "mode", "max"}),
    "uniform": frozenset({"min", "max"}),
}
OTHER: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "metalog": (frozenset({"probabilities", "values"}), frozenset({"lower_bound", "upper_bound", "number_of_terms"})),
    "empirical": (frozenset({"data_file", "column"}), frozenset()),
    "mixture": (frozenset({"components"}), frozenset()),
    "categorical": (frozenset({"outcomes"}), frozenset()),
}
SCIPY = "scipy."
# Keelin 2016, Proposition 2 (eq. 20): a three-term metalog is feasible iff a2 > 0 and |a3|/a2 < this.
KEELIN_K0 = 1.66711
# The feasibility grid for four or more terms: logit(y) evenly spaced, y from 1e-12 to 1 - 1e-12.
GRID_EDGE = 1e-12
GRID_POINTS = 100_001
WEIGHT_SUM_TOL = 1e-9
TINY = math.nextafter(0.0, 1.0)
BELOW_ONE = math.nextafter(1.0, 0.0)


def _scipy_dist(distribution: str) -> rv_continuous | rv_discrete:
    obj: object = getattr(scipy.stats, distribution[len(SCIPY) :], None)
    if not isinstance(obj, (rv_continuous, rv_discrete)):
        raise ValueError(f"{distribution}: distribution names no univariate distribution in scipy.stats")
    return obj


def fields(distribution: str) -> tuple[frozenset[str], frozenset[str]]:
    """The required and the optional parameter names of a kind (`distribution` itself is in neither)."""
    if distribution in TEMPLATE:
        return TEMPLATE[distribution], frozenset()
    if distribution in OTHER:
        return OTHER[distribution]
    if distribution.startswith(SCIPY):
        obj = _scipy_dist(distribution)
        shapes = frozenset(s.strip() for s in (obj.shapes or "").split(",") if s.strip())
        optional = {"loc", "scale"} if isinstance(obj, rv_continuous) else {"loc"}
        return shapes, frozenset(optional)
    raise ValueError(f"unknown distribution {distribution!r}")


# ---------------------------------------------------------------- shared checks


def _real(kind: str, name: str, value: object) -> float:
    """A finite real number, never a bool."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{kind}: {name} must be a real number, got {value!r}")
    x = float(cast(float, value))
    if not math.isfinite(x):
        raise ValueError(f"{kind}: {name} must be finite, got {value!r}")
    return x


def _get(kind: str, spec: Mapping[str, object], name: str) -> object:
    if name not in spec:
        raise ValueError(f"{kind}: missing required field {name}")
    return spec[name]


def _check_u(kind: str, u: Floats) -> None:
    if u.ndim != 1:
        raise ValueError(f"{kind}: u must be one-dimensional")
    if not bool(np.all((u > 0.0) & (u < 1.0))):
        raise ValueError(f"{kind}: every u must lie strictly between 0 and 1 (NaN refused)")


def _kind(spec: Mapping[str, object]) -> str:
    distribution = spec.get("distribution")
    if not isinstance(distribution, str):
        raise ValueError(f"distribution must be a string, got {distribution!r}")
    fields(distribution)  # refuses an unknown kind
    return distribution


def _finite_mean(kind: str, spec: Mapping[str, object], finite: bool) -> None:
    """Refuse a distribution whose mean is infinite or undefined: a Monte Carlo mean of it is set by the seed
    and the draw count, not by the inputs (the referee's ruling on infinite means, 2026-11-17)."""
    if not finite:
        params = {k: v for k, v in spec.items() if k != "distribution"}
        raise ValueError(
            f"{kind}: its mean is infinite or undefined at {params!r}, so a Monte Carlo mean would depend on the seed; "
            "a heavy tail over a quantity with a physical limit is entered bounded, as kind scipy.truncpareto with "
            "b = alpha - 1, c = limit / min and scale = min, the limit's source named"
        )


def _brackets(kind: str, field: str, weights: Sequence[object], u: Floats) -> tuple[NDArray[np.int64], Floats]:
    """The bracket rule: index j with W[j-1] < u <= W[j] (W[-1] = 0), and u rescaled within it."""
    if len(weights) == 0:
        raise ValueError(f"{kind}: {field} must not be empty")
    w = np.array([_real(kind, field, x) for x in weights], dtype=np.float64)
    if not bool(np.all(w > 0.0)):
        raise ValueError(f"{kind}: every {field} weight must be positive")
    if abs(float(np.sum(w)) - 1.0) > WEIGHT_SUM_TOL:
        raise ValueError(f"{kind}: {field} weights must sum to 1 within {WEIGHT_SUM_TOL}, sum {float(np.sum(w))!r}")
    upper = np.cumsum(w)
    upper[-1] = 1.0
    lower = np.concatenate(([0.0], upper[:-1]))
    j = np.searchsorted(upper, u, side="left").astype(np.int64)
    rescaled = np.clip((u - lower[j]) / w[j], TINY, BELOW_ONE)
    return j, rescaled


# ---------------------------------------------------------------- the template's seven


def _template(kind: str, spec: Mapping[str, object], u: Floats) -> Floats:
    p = {name: _real(kind, name, _get(kind, spec, name)) for name in sorted(TEMPLATE[kind])}
    if "min" in p and "max" in p and not p["min"] < p["max"]:
        raise ValueError(f"{kind}: min ({p['min']!r}) must be below max ({p['max']!r})")
    if "sd" in p and not p["sd"] > 0.0:
        raise ValueError(f"{kind}: sd must be positive, got {p['sd']!r}")
    lo, hi = p.get("min", 0.0), p.get("max", 0.0)
    if kind == "beta":
        for name in ("alpha", "beta"):
            if not p[name] > 0.0:
                raise ValueError(f"beta: {name} must be positive, got {p[name]!r}")
        return lo + (hi - lo) * scipy.stats.beta.ppf(u, p["alpha"], p["beta"])
    if kind == "constant":
        return p["mean"] + 0.0 * u
    if kind == "lognormal":
        mean, sd = p["mean"], p["sd"]
        if not mean > 0.0:
            raise ValueError(f"lognormal: mean must be positive, got {mean!r}")
        mu = math.log(mean**2 / math.sqrt(mean**2 + sd**2))
        sigma = math.sqrt(math.log(1.0 + sd**2 / mean**2))
        return np.exp(scipy.stats.norm.ppf(u, mu, sigma))
    if kind == "normal":
        return scipy.stats.norm.ppf(u, p["mean"], p["sd"])
    if kind == "power law":
        if not lo > 0.0:
            raise ValueError(f"power law: min must be positive, got {lo!r}")
        _finite_mean(kind, spec, p["alpha"] > 2.0)  # mean min (alpha - 1) / (alpha - 2)
        with np.errstate(over="ignore"):
            return lo * (1.0 - u) ** (-1.0 / (p["alpha"] - 1.0))
    if kind == "triangular":
        peak = p["mode"]
        if not lo <= peak <= hi:
            raise ValueError(f"triangular: mode ({peak!r}) must lie in [min, max] = [{lo!r}, {hi!r}]")
        left = lo + np.sqrt(u * (hi - lo) * (peak - lo))
        right = hi - np.sqrt((1.0 - u) * (hi - lo) * (hi - peak))
        return np.where(u <= (peak - lo) / (hi - lo), left, right)
    # uniform
    return lo + u * (hi - lo)


# ---------------------------------------------------------------- scipy.<name>


def _scipy(kind: str, spec: Mapping[str, object], u: Floats) -> Floats:
    obj = _scipy_dist(kind)
    required, optional = fields(kind)
    shapes = [s.strip() for s in (obj.shapes or "").split(",") if s.strip()]
    args = [_real(kind, name, _get(kind, spec, name)) for name in shapes]
    named = {name: _real(kind, name, spec[name]) for name in sorted(optional) if name in spec}
    if "scale" in named and not named["scale"] > 0.0:
        raise ValueError(f"{kind}: scale must be positive, got {named['scale']!r}")
    low, high = obj.support(*args, **named)
    if math.isnan(float(low)) or math.isnan(float(high)):
        given = ", ".join(f"{n}={v!r}" for n, v in [*zip(shapes, args), *named.items()])
        raise ValueError(f"{kind}: the distribution rejects its parameters ({given}); its shapes are {sorted(required)}")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        _finite_mean(kind, spec, math.isfinite(float(obj.mean(*args, **named))))
        return np.asarray(obj.ppf(u, *args, **named), dtype=np.float64)


# ---------------------------------------------------------------- metalog


def _powers(n: int) -> list[tuple[int, bool]]:
    """Keelin 2016 eq. (6): term k is (y - 0.5)^m, times L = ln(y/(1-y)) when the flag is set."""
    terms = [(0, False), (0, True), (1, True), (1, False)]
    terms += [((k - 1) // 2, False) if k % 2 == 1 else (k // 2 - 1, True) for k in range(5, n + 1)]
    return terms[:n]


def _basis(y: Floats, n: int) -> Floats:
    big_l = np.log(y / (1.0 - y))
    c = y - 0.5
    return np.stack([c**m * big_l if logit else c**m for m, logit in _powers(n)], axis=1)


def _basis_slope(y: Floats, n: int) -> Floats:
    """d/dy of each basis term."""
    big_l = np.log(y / (1.0 - y))
    dl = 1.0 / (y * (1.0 - y))
    c = y - 0.5
    cols: list[Floats] = []
    for m, logit in _powers(n):
        dcm = m * c ** (m - 1) if m > 0 else np.zeros_like(y)
        cols.append(dcm * big_l + c**m * dl if logit else dcm)
    return np.stack(cols, axis=1)


def _metalog_bounds(spec: Mapping[str, object]) -> tuple[float | None, float | None]:
    lower = _real("metalog", "lower_bound", spec["lower_bound"]) if "lower_bound" in spec else None
    upper = _real("metalog", "upper_bound", spec["upper_bound"]) if "upper_bound" in spec else None
    return lower, upper


def metalog_coefficients(spec: Mapping[str, object]) -> Floats:
    """The fitted a1 to an on the transformed scale, in Keelin's basis order (eq. 6), by least
    squares (eq. 7); refused when the fitted quantile function is not strictly increasing."""
    kind = "metalog"
    lists: list[Sequence[object]] = []
    for name in ("probabilities", "values"):
        raw = _get(kind, spec, name)
        if not isinstance(raw, (list, tuple)):
            raise ValueError(f"{kind}: {name} must be a list of numbers")
        lists.append(cast(Sequence[object], raw))
    p_raw, x_raw = lists
    if len(p_raw) != len(x_raw):
        raise ValueError(
            f"{kind}: probabilities and values must be of equal length, got {len(p_raw)} probabilities "
            f"and {len(x_raw)} values"
        )
    points = len(p_raw)
    if points < 3:
        raise ValueError(f"{kind}: probabilities and values need at least 3 points, got {points}")
    p = np.array([_real(kind, "probabilities", v) for v in p_raw], dtype=np.float64)
    x = np.array([_real(kind, "values", v) for v in x_raw], dtype=np.float64)
    if not bool(np.all((p > 0.0) & (p < 1.0))) or not bool(np.all(np.diff(p) > 0.0)):
        raise ValueError(f"{kind}: probabilities must be strictly increasing inside (0, 1)")
    if not bool(np.all(np.diff(x) > 0.0)):
        raise ValueError(f"{kind}: values must be strictly increasing")
    n = points
    if "number_of_terms" in spec:
        t = spec["number_of_terms"]
        if isinstance(t, (bool, np.bool_)) or not isinstance(t, (int, np.integer)) or not 2 <= int(cast(int, t)) <= points:
            raise ValueError(f"{kind}: number_of_terms must be an integer from 2 to {points}, got {t!r}")
        n = int(cast(int, t))
    lower, upper = _metalog_bounds(spec)
    if lower is not None and not bool(np.all(x > lower)):
        raise ValueError(f"{kind}: every one of values must lie strictly above lower_bound ({lower!r})")
    if upper is not None and not bool(np.all(x < upper)):
        raise ValueError(f"{kind}: every one of values must lie strictly below upper_bound ({upper!r})")
    if lower is not None and upper is not None:
        z = np.log((x - lower) / (upper - x))
    elif lower is not None:
        z = np.log(x - lower)
    elif upper is not None:
        z = -np.log(upper - x)
    else:
        z = x
    a = np.linalg.lstsq(_basis(p, n), z)[0]
    if n == 2:
        feasible = a[1] > 0.0
    elif n == 3:
        feasible = a[1] > 0.0 and abs(a[2]) / a[1] < KEELIN_K0
    else:
        edge = math.log((1.0 - GRID_EDGE) / GRID_EDGE)
        y = expit(np.linspace(-edge, edge, GRID_POINTS))
        feasible = bool(np.all(_basis_slope(y, n) @ a > 0.0))
    if not feasible:
        raise ValueError(
            f"{kind}: the fit to probabilities and values is infeasible (its quantile function is not strictly increasing)"
        )
    return a


def _metalog(spec: Mapping[str, object], u: Floats) -> Floats:
    a = metalog_coefficients(spec)
    z = _basis(u, len(a)) @ a
    lower, upper = _metalog_bounds(spec)
    # A semi-bounded metalog's open tail goes as (1 - y)^-s (lower bound only) or y^-s (upper bound only), s the
    # sum of a_k (y - 1/2)^m over the terms carrying L, taken at that tail's end; its mean is finite iff s < 1.
    if (lower is None) != (upper is None):
        c = 0.5 if upper is None else -0.5
        s = sum(float(a[k]) * c**m for k, (m, logit) in enumerate(_powers(len(a))) if logit)
        _finite_mean("metalog", spec, s < 1.0)
    with np.errstate(over="ignore", invalid="ignore"):
        if lower is not None and upper is not None:
            return lower + (upper - lower) * expit(z)
        if lower is not None:
            return lower + np.exp(z)
        if upper is not None:
            return upper - np.exp(-z)
    return z


# ---------------------------------------------------------------- empirical, mixture, categorical


def _empirical(spec: Mapping[str, object], u: Floats) -> Floats:
    kind = "empirical"
    raw = _get(kind, spec, "pool")
    if isinstance(raw, np.ndarray):
        arr = cast(NDArray[np.generic], raw)
        if arr.dtype.kind not in "iuf" or arr.ndim != 1:
            raise ValueError(f"{kind}: pool must be a one-dimensional array of real numbers")
        values = arr.astype(np.float64)
        if not bool(np.all(np.isfinite(values))):
            raise ValueError(f"{kind}: pool must all be finite")
    elif isinstance(raw, (list, tuple)):
        values = np.array([_real(kind, "pool", v) for v in cast(Sequence[object], raw)], dtype=np.float64)
    else:
        raise ValueError(f"{kind}: pool must be a list or array of numbers")
    if values.size == 0:
        raise ValueError(f"{kind}: pool must not be empty")
    return np.quantile(values, u, method="inverted_cdf")


def pick(spec: Mapping[str, object], u: Floats) -> tuple[NDArray[np.int64], Floats]:
    """A `mixture`'s top-level component index for each draw, and the uniform rescaled within that
    component's share (the bracket rule): the one code path `quantile` draws a mixture by."""
    kind = _kind(spec)
    if kind != "mixture":
        raise ValueError(f"{kind}: pick applies to a mixture only")
    _check_u(kind, u)
    raw = _get(kind, spec, "components")
    if not isinstance(raw, (list, tuple)):
        raise ValueError(f"{kind}: components must be a list")
    weights: list[object] = []
    for i, part in enumerate(cast(Sequence[object], raw)):
        if not isinstance(part, Mapping):
            raise ValueError(f"{kind}: component {i} of components must be a mapping")
        entry = cast(Mapping[str, object], part)
        if entry.get("distribution") == "categorical":
            raise ValueError(f"{kind}: component {i} is a categorical, which has no quantile")
        if "weight" not in entry:
            raise ValueError(f"{kind}: component {i} has no weight")
        weights.append(entry["weight"])
    return _brackets(kind, "weight", weights, u)


def _mixture(spec: Mapping[str, object], u: Floats) -> tuple[Floats, NDArray[np.int64]]:
    j, rescaled = pick(spec, u)
    parts = cast(Sequence[Mapping[str, object]], spec["components"])  # checked by pick
    out = np.empty_like(u)
    for i, part in enumerate(parts):
        picked = j == i
        out[picked] = quantile(part, rescaled[picked])  # every component checked, picked or not
    return out, j


def quantile(spec: Mapping[str, object], u: Floats) -> Floats:
    """The draws of one numeric input at the uniform numbers u (a `categorical` is drawn by `choose`)."""
    kind = _kind(spec)
    _check_u(kind, u)
    if kind == "categorical":
        raise ValueError("categorical: a categorical has outcomes, not numbers; draw it with choose")
    if kind in TEMPLATE:
        draws = _template(kind, spec, u)
    elif kind.startswith(SCIPY):
        draws = _scipy(kind, spec, u)
    elif kind == "metalog":
        draws = _metalog(spec, u)
    elif kind == "empirical":
        draws = _empirical(spec, u)
    else:
        draws = _mixture(spec, u)[0]
    draws = np.asarray(draws, dtype=np.float64)
    if not bool(np.all(np.isfinite(draws))):
        params = {k: v for k, v in spec.items() if k != "distribution"}
        raise ValueError(f"{kind}: a draw is not finite at a legal u, with parameters {params!r}")
    return draws


def support(spec: Mapping[str, object]) -> tuple[float, float]:
    """The least and greatest value a numeric input can draw (infinite where unbounded): its family's support at its
    parameters, an `empirical`'s pool's least and greatest, a `mixture`'s across its components. For an entry
    `quantile` has accepted; a `categorical` is refused."""
    kind = _kind(spec)
    if kind in ("beta", "triangular", "uniform"):
        return _real(kind, "min", _get(kind, spec, "min")), _real(kind, "max", _get(kind, spec, "max"))
    if kind == "constant":
        mean = _real(kind, "mean", _get(kind, spec, "mean"))
        return mean, mean
    if kind == "lognormal":
        return 0.0, math.inf
    if kind == "normal":
        return -math.inf, math.inf
    if kind == "power law":
        return _real(kind, "min", _get(kind, spec, "min")), math.inf
    if kind.startswith(SCIPY):
        obj = _scipy_dist(kind)
        _, optional = fields(kind)
        shapes = [s.strip() for s in (obj.shapes or "").split(",") if s.strip()]
        args = [_real(kind, name, _get(kind, spec, name)) for name in shapes]
        named = {name: _real(kind, name, spec[name]) for name in sorted(optional) if name in spec}
        low, high = obj.support(*args, **named)
        return float(low), float(high)
    if kind == "metalog":
        lower, upper = _metalog_bounds(spec)
        return (-math.inf if lower is None else lower), (math.inf if upper is None else upper)
    if kind == "empirical":
        pool = np.asarray(_get(kind, spec, "pool"), dtype=np.float64)
        return float(pool.min()), float(pool.max())
    if kind == "mixture":
        ends = [support(cast(Mapping[str, object], part)) for part in cast(Sequence[object], _get(kind, spec, "components"))]
        return min(lo for lo, _ in ends), max(hi for _, hi in ends)
    raise ValueError(f"{kind}: a categorical has outcomes, not numbers, so no support")


def component(spec: Mapping[str, object], u: Floats) -> NDArray[np.int64]:
    """The index of the top-level component of a `mixture` each draw picked. A nested mixture's
    own inner pick is not reported."""
    kind = _kind(spec)
    if kind != "mixture":
        raise ValueError(f"{kind}: component applies to a mixture only")
    _check_u(kind, u)
    return _mixture(spec, u)[1]


def choose(spec: Mapping[str, object], u: Floats) -> NDArray[np.str_]:
    """The outcome of a `categorical` each draw picked, by the same bracket rule as a mixture."""
    kind = _kind(spec)
    if kind != "categorical":
        raise ValueError(f"{kind}: choose applies to a categorical only")
    _check_u(kind, u)
    raw = _get(kind, spec, "outcomes")
    if not isinstance(raw, Mapping) or len(cast(Mapping[object, object], raw)) == 0:
        raise ValueError(f"{kind}: outcomes must be a non-empty mapping of outcome to weight")
    outcomes = cast(Mapping[object, object], raw)
    labels = [str(label) for label in outcomes]
    j, _ = _brackets(kind, "outcomes", list(outcomes.values()), u)
    return np.array(labels, dtype=np.str_)[j]
