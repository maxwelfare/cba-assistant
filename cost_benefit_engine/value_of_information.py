"""Expected value of perfect and of partial perfect information, and one input's main effect at a quantile (`end`),
from Monte Carlo draws.

`net_benefits` is always a float array of draws by options. Only the columns given are compared: where doing nothing is
an option, it is a column of zeros.

One statistic serves every value here: with g the net benefit of each option as known in each draw,
mean(max over options of g) - max over options of mean(g). `evpi` takes g to be the net benefits themselves. `evppi`
takes g to be the conditional mean of net benefit on one input, estimated from the draws as Strong and Oakley (2013,
Medical Decision Making 33(6):755-766) and Strong, Oakley and Brennan (2014, Medical Decision Making 34(3):311-326) do,
by one of two fits:

1. "bins": the mean within equal-count bins over the ranks of a numeric key, or within each distinct value of a string
   or boolean key.
2. "spline": least squares on 1, u, u^2, u^3 and (u-k)^3 for u > k, at the knots in `SPLINE_KNOTS`.

Both place a numeric key at u = (average rank - 0.5) / n, so equal values share a position, and so a bin. A tied block
that crosses a bin edge goes wholly to the bin holding the block's middle, and two distinct values can share a bin only
if together they hold under 2 / bins of the draws, so a key with few values keeps them apart however uneven their
shares.

An estimated conditional mean follows the noise in the draws, so `evppi` is biased upward in a finite sample.
`noise_floor` gauges that bias: the largest `evppi` over random permutations of the key, which break any real relation
between key and net benefit.

`main_effect` reads the "bins" fit of one output as a variance: Var(E[output | key]) / Var(output), the input's
main-effect (first-order) index, biased upward by the same noise.

`end` gives one end of an input's tornado bar: the main effect E[output | key = x] (Oakley and O'Hagan 2004, J. R.
Stat. Soc. B 66(3):751-769), every other input drawn as it was, at x the key's p quantile. It equals the one-way bar
that holds the other inputs at their means only where, for each x, the output is multilinear in the other inputs and
they are independent of the key and of each other (Rothery et al. 2020). It is the intercept of a local linear fit (Fan
and Gijbels 1996) over the draws within `half` of p in rank on either side, with the intercept's heteroskedasticity-
consistent (HC0) standard error (White 1980), which is calibrated at the returned x, not at the true quantile.

Every refusal is a ValueError naming what it refuses.
"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

Floats = NDArray[np.float64]

SPLINE_KNOTS = (0.2, 0.4, 0.6, 0.8)
BINS = 50  # the default bins of the "bins" fit


def _value(known: Floats) -> float:
    """The statistic: `known` is draws by options."""
    return float(known.max(axis=1).mean() - known.mean(axis=0).max())


def _positions(key: NDArray[Any]) -> Floats:
    """Each draw's position in (0, 1) by the rank of its key; equal values share a position."""
    if key.dtype.kind not in "iuf":
        raise ValueError(f"a key of dtype {key.dtype} has no ranks")
    if np.isnan(key).any():
        raise ValueError("the key holds NaN")
    return (_ranks(key) - 0.5) / key.size


def _ranks(key: NDArray[Any]) -> Floats:
    """The average ranks of `key`, 1 to n, as `scipy.stats.rankdata` gives them (each exact, a whole or half number),
    from one unstable sort: each tied block of the sorted key takes its first index plus (its size + 1) / 2. Every rank
    in the "bins" fit passes through this, so it is the one cost per key (roadmap R15)."""
    order = np.argsort(key)
    ordered = key[order]
    start = np.flatnonzero(np.concatenate(([True], ordered[1:] != ordered[:-1])))
    size = np.diff(np.append(start, key.size))
    ranks = np.empty(key.size)
    ranks[order] = np.repeat(start + (size + 1) / 2, size)
    return ranks


def bin_codes(key: NDArray[Any], bins: int = BINS) -> NDArray[np.intp]:
    """Each draw's bin in the "bins" fit: for a numeric key floor((average rank - 0.5) / n * bins), else the index of
    its distinct value. A caller that groups draws as `evppi` does calls this, never a copy of it."""
    if key.dtype.kind in "iuf":
        return np.floor(_positions(key) * bins).astype(np.intp)
    return np.unique(key, return_inverse=True)[1].astype(np.intp)


def _bin_means(net_benefits: Floats, key: NDArray[Any], bins: int) -> Floats:
    codes = bin_codes(key, bins)
    counts = np.bincount(codes)
    means: list[Floats] = [np.bincount(codes, weights=option)[codes] / counts[codes] for option in net_benefits.T]
    return np.column_stack(means)


def binned_value(sums: Floats, n: int) -> float:
    """The statistic of the "bins" fit from `sums`, bins by options, each option's net benefit summed over a bin's
    draws (n draws in all): with every draw given its bin's mean, mean(max) is the sum over bins of the largest sum,
    over n, and max(mean) the largest column total over n. An empty bin adds nothing to either. Both totals come from one
    reduction, so where one option leads in every bin they are the same sum in the same order and the value is 0."""
    totals = np.column_stack([sums, sums.max(axis=1)]).sum(axis=0)
    return float((totals[-1] - totals[:-1].max()) / n)


def _spline_means(net_benefits: Floats, key: NDArray[Any]) -> Floats:
    u = _positions(key)
    basis = np.column_stack([np.ones(u.size), u, u**2, u**3, *[np.clip(u - k, 0.0, None) ** 3 for k in SPLINE_KNOTS]])
    return basis @ np.linalg.lstsq(basis, net_benefits, rcond=None)[0]


def evpi(net_benefits: Floats) -> float:
    """The expected value of perfect information: what it is worth to know every uncertainty before choosing."""
    return _value(net_benefits)


def evppi(net_benefits: Floats, key: NDArray[Any], fit: str = "bins", bins: int = BINS) -> float:
    """The expected value of partial perfect information on `key`, one input's draws. `bins` is ignored unless the fit
    is "bins" and the key numeric."""
    if fit == "bins":
        codes = bin_codes(key, bins)
        sums: list[Floats] = [np.bincount(codes, weights=option) for option in net_benefits.T]
        return binned_value(np.column_stack(sums), key.size)
    if fit == "spline":
        return _value(_spline_means(net_benefits, key))
    raise ValueError(f"unknown fit {fit!r}")


def main_effect(output: Floats, key: NDArray[Any], bins: int = BINS) -> float:
    """One input's main-effect (first-order) index, Var(E[output | key]) / Var(output), E[output | key] by the "bins" fit
    of `evppi` (Saltelli et al. 2008; Oakley and O'Hagan 2004, 2.5.2); refused where the output does not vary."""
    var = float(np.var(output))
    if not var > 0:
        raise ValueError("the output does not vary, so it has no main effect to share")
    return float(np.var(_bin_means(np.asarray(output, dtype=np.float64)[:, None], key, bins)[:, 0])) / var


def noise_floor(
    net_benefits: Floats,
    key: NDArray[Any],
    rng: np.random.Generator,
    permutations: int = 20,
    fit: str = "bins",
    bins: int = BINS,
) -> float:
    """The largest `evppi` over `permutations` random permutations of `key`, each drawn from `rng`."""
    return max(evppi(net_benefits, rng.permutation(key), fit, bins) for _ in range(permutations))


def end(output: Floats, key: Floats, p: float, half: float = 0.025) -> tuple[float, float, float]:
    """(x, E[output | key = x], its standard error), x being the key's p quantile.

    The window is the draws whose key lies between the key's quantiles at max(p - half, 0) and min(p + half, 1),
    inclusive. Where the key takes more than one value there, the end is the intercept of least squares of output on
    [1, key - x] over the window, with its HC0 standard error; where it takes one value, the window's mean of output and
    that mean's standard error."""
    y, k = np.asarray(output, dtype=np.float64), np.asarray(key, dtype=np.float64)
    if y.shape != k.shape or y.ndim != 1:
        raise ValueError(f"output of shape {y.shape} and key of shape {k.shape} are not one column of equal length")
    if not (np.isfinite(y).all() and np.isfinite(k).all()):
        raise ValueError("output or key holds a value that is not finite")
    if not 0 < p < 1:
        raise ValueError(f"p must lie in (0, 1), got {p!r}")
    if not 0 < half < 0.5:
        raise ValueError(f"half must lie in (0, 0.5), got {half!r}")
    x = float(np.quantile(k, p))
    lo, hi = np.quantile(k, max(p - half, 0.0)), np.quantile(k, min(p + half, 1.0))
    inside = (k >= lo) & (k <= hi)
    yw, kw = y[inside], k[inside] - x
    if yw.size < 3:
        raise ValueError(f"the window at p={p} with half={half} holds {yw.size} draws, fewer than 3")
    if kw.min() == kw.max():
        return x, float(yw.mean()), float(yw.std(ddof=1) / np.sqrt(yw.size))
    design = np.column_stack([np.ones(yw.size), kw])
    beta = np.linalg.lstsq(design, yw, rcond=None)[0]
    resid = yw - design @ beta
    bread = np.linalg.inv(design.T @ design)
    cov = bread @ ((design * resid[:, None] ** 2).T @ design) @ bread
    return x, float(beta[0]), float(np.sqrt(cov[0, 0]))
