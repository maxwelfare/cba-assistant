"""What a reader of a run sees, computed from draws already made: plain arrays in, records out.

`summary(values)` gives a result's mean, its 5th, 50th and 95th percentiles and the shares of draws
above and below zero (the owner's rule 1: a point estimate is always wrong). `prcc(inputs, output)`
gives each input's partial rank correlation with the output (Marino, Hogue, Ray and Kirschner 2008,
Journal of Theoretical Biology 254:178-196), so research goes to the inputs that drive the result.
`convergence(values, checkpoints)` gives the running mean, its standard error and the share of the
sum carried by the largest 1% of draws, so a reader sees a mean held up by a few heavy-tailed draws.
`standard_error(values)` is the Monte Carlo standard error of a mean of draws, the one both
`convergence` and `tools/estimate_total.py` report.

Every refusal is a ValueError saying what it refuses.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.stats import rankdata

Arr = NDArray[np.float64]


@dataclass(frozen=True)
class Summary:
    """A result's distribution: NaN draws are counted in nan_count and left out of the rest."""

    mean: float
    p5: float
    p50: float
    p95: float
    share_positive: float  # share of the count strictly above zero
    share_negative: float  # share of the count strictly below zero
    count: int  # non-NaN values used
    nan_count: int


@dataclass(frozen=True)
class Checkpoint:
    """The first `iterations` values: their mean, its standard error and the largest 1%'s share of the sum."""

    iterations: int
    mean: float
    standard_error: float
    top_share: float


def _numeric(name: str, value: Any) -> NDArray[Any]:
    """The array, refused unless its dtype is an integer or a float (booleans and labels refused)."""
    arr = np.asarray(value)
    if arr.dtype.kind not in "iuf":
        raise ValueError(f"{name}: not numeric (dtype {arr.dtype}); a categorical input's outcomes have no rank correlation")
    return arr


def _vector(name: str, value: Any) -> Arr:
    arr = _numeric(name, value)
    if arr.ndim != 1:
        raise ValueError(f"{name}: must be a 1-D array, got {arr.ndim} dimensions")
    return arr.astype(np.float64)


def summary(values: Any) -> Summary:
    """Mean, percentiles and sign shares of a 1-D array, NaN entries counted and left out.

    Percentiles use numpy's default linear interpolation between order statistics at position
    p (n - 1) (Hyndman and Fan 1996, definition 7). An array with no non-NaN value is refused.
    """
    arr = _vector("values", values)
    nan = np.isnan(arr)
    kept = arr[~nan]
    if kept.size == 0:
        raise ValueError("values: no non-NaN value to summarise")
    p5, p50, p95 = (float(q) for q in np.percentile(kept, [5.0, 50.0, 95.0]))
    n = int(kept.size)
    return Summary(
        mean=float(np.mean(kept)),
        p5=p5,
        p50=p50,
        p95=p95,
        share_positive=int(np.count_nonzero(kept > 0.0)) / n,
        share_negative=int(np.count_nonzero(kept < 0.0)) / n,
        count=n,
        nan_count=int(np.count_nonzero(nan)),
    )


def _columns(inputs: Mapping[str, Any], n: int) -> list[tuple[str, Arr]]:
    """Each input as named 1-D columns; a 2-D input gives one column per index, named name[j]."""
    out: list[tuple[str, Arr]] = []
    for name, value in inputs.items():
        arr = _numeric(name, value).astype(np.float64)
        if arr.ndim == 1:
            cols = [(name, arr)]
        elif arr.ndim == 2:
            cols = [(f"{name}[{j}]", arr[:, j]) for j in range(arr.shape[1])]
        else:
            raise ValueError(f"{name}: must be 1-D or 2-D, got {arr.ndim} dimensions")
        if arr.shape[0] != n:
            raise ValueError(f"{name}: {arr.shape[0]} draws, the output has {n}")
        if bool(np.isnan(arr).any()):
            raise ValueError(f"{name}: contains NaN")
        out.extend(cols)
    return out


def prcc(inputs: Mapping[str, Any], output: Any) -> dict[str, float]:
    """Partial rank correlation of each input column with the output.

    Every input and the output are ranked (scipy's rankdata, ties given their average rank). For
    each input, the ranks of that input and of the output are each regressed, with an intercept, on
    the ranks of all the other non-constant inputs by least squares, and the coefficient is the
    correlation of the two residuals. A constant input is left out of every regression and returned
    as NaN. Refused: a non-numeric input (named), NaN anywhere, a constant output, lengths that
    differ, more than two dimensions, and fewer draws than input columns (constants included) plus 3.
    """
    y = _vector("output", output)
    n = int(y.size)
    if bool(np.isnan(y).any()):
        raise ValueError("output: contains NaN")
    columns = _columns(inputs, n)
    if n < len(columns) + 3:
        raise ValueError(f"{n} draws for {len(columns)} input columns; at least {len(columns) + 3} needed")
    if float(np.ptp(y)) == 0.0:
        raise ValueError("output: constant, so no input can correlate with it")
    ry = np.asarray(rankdata(y), dtype=np.float64)
    varying = [(name, np.asarray(rankdata(col), dtype=np.float64)) for name, col in columns if float(np.ptp(col)) > 0.0]
    result: dict[str, float] = {name: math.nan for name, _ in columns}
    ones = np.ones(n)
    for i, (name, rx) in enumerate(varying):
        design = np.column_stack([ones, *(r for j, (_, r) in enumerate(varying) if j != i)])
        ex = rx - design @ np.linalg.lstsq(design, rx, rcond=None)[0]
        ey = ry - design @ np.linalg.lstsq(design, ry, rcond=None)[0]
        result[name] = float(np.sum(ex * ey) / math.sqrt(float(np.sum(ex * ex)) * float(np.sum(ey * ey))))
    return result


def standard_error(values: Any) -> float:
    """The Monte Carlo standard error of the mean of a 1-D array of draws: their sample standard deviation (ddof = 1)
    over the square root of their count; zero for draws all equal."""
    arr = _vector("values", values)
    return float(np.std(arr, ddof=1)) / math.sqrt(arr.size)


def convergence(values: Any, checkpoints: Sequence[object]) -> list[Checkpoint]:
    """At each checkpoint, the mean of the first that-many values, its standard error and top share.

    The standard error is the sample standard deviation (ddof = 1) over the square root of the
    count. The top share is the signed sum of the k = max(1, floor(draws / 100)) values largest in
    absolute value over the signed sum of all of them. Checkpoints must be integers, strictly
    ascending, at least 2 and at most the number of values; NaN in values is refused, and so is a
    checkpoint whose values sum to zero, where the share has no meaning.
    """
    arr = _vector("values", values)
    if bool(np.isnan(arr).any()):
        raise ValueError("values: contains NaN")
    out: list[Checkpoint] = []
    previous = 1
    for c in checkpoints:
        if isinstance(c, bool) or not isinstance(c, (int, np.integer)):
            raise ValueError(f"checkpoint {c!r}: not an integer")
        draws = int(cast(int, c))
        if draws <= previous:
            raise ValueError(f"checkpoint {draws}: checkpoints must be at least 2 and strictly ascending")
        if draws > arr.size:
            raise ValueError(f"checkpoint {draws}: more than the {arr.size} values")
        previous = draws
        head = arr[:draws]
        total = float(np.sum(head))
        if total == 0.0:
            raise ValueError(f"checkpoint {draws}: the values sum to zero, so no share of the sum exists")
        k = max(1, draws // 100)
        top = head[np.argsort(np.abs(head), kind="stable")[-k:]]
        out.append(
            Checkpoint(
                iterations=draws,
                mean=float(np.mean(head)),
                standard_error=standard_error(head),
                top_share=float(np.sum(top)) / total,
            )
        )
    return out
