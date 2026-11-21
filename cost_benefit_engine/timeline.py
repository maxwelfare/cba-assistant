"""The engine's timeline: a case's appraisal years, discount factors, present values and time shapes.

A schedule is a sequence of (first, last, rate) segments counted
in years after `discount_base_year` (year 0), the last segment's `last` None for "onward"; the
factor of year discount_base_year + t is the product over k = 1..t of 1 / (1 + rate_k), the
forward-rate reading the Green Book prescribes. Streams are float64 arrays of shape
(iterations, len(years)). Every refusal is a ValueError naming the argument; nothing defaults and
no flow is dropped silently.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

Floats = NDArray[np.float64]
Years = NDArray[np.integer[Any]]
Integer = int | np.integer[Any]
Amount = int | float | np.integer[Any] | np.floating[Any] | NDArray[np.integer[Any] | np.floating[Any]]
Segment = tuple[int, int | None, float]


def _integer(name: str, value: object) -> int:
    """A Python or numpy integer, never bool."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer (Python or numpy, not bool), got {value!r}")
    return int(cast(Integer, value))


def _positive(name: str, value: object) -> int:
    out = _integer(name, value)
    if out < 1:
        raise ValueError(f"{name} must be a positive integer, got {out}")
    return out


def _years(years: object) -> Years:
    """A non-empty 1-D integer array of ascending, contiguous years."""
    if not isinstance(years, np.ndarray):
        raise ValueError(f"years must be a numpy integer array, got {type(years).__name__}")
    arr = cast(NDArray[Any], years)
    if arr.ndim != 1 or arr.size == 0 or arr.dtype == np.bool_ or not np.issubdtype(arr.dtype, np.integer):
        raise ValueError(f"years must be a non-empty 1-D integer array, got dtype {arr.dtype}, shape {arr.shape}")
    if np.any(np.diff(arr) != 1):
        raise ValueError("years must be ascending and contiguous (each year one after the last)")
    return cast(Years, arr)


def _position(name: str, value: object, years: Years) -> int:
    """The column of an integer year among the appraisal years, refusing one outside them."""
    year = _integer(name, value)
    first = int(years[0])
    if not first <= year <= int(years[-1]):
        raise ValueError(f"{name} {year} is outside the appraisal years {first} to {int(years[-1])}")
    return year - first


def _amount(amount: object, n: int) -> Floats:
    """A finite real number or a 1-D integer or floating array of length n, as float64 of shape (n,)."""
    if isinstance(amount, np.ndarray):
        arr = cast(NDArray[Any], amount)
        if arr.ndim != 1 or arr.dtype == np.bool_ or not (
            np.issubdtype(arr.dtype, np.integer) or np.issubdtype(arr.dtype, np.floating)
        ):
            raise ValueError(f"amount must be 1-D of integer or floating dtype, got dtype {arr.dtype}, shape {arr.shape}")
        if arr.shape[0] != n:
            raise ValueError(f"amount has {arr.shape[0]} draws, but iterations is {n}")
        out = arr.astype(np.float64)  # always a copy
    elif isinstance(amount, (bool, np.bool_)) or not isinstance(amount, (int, float, np.integer, np.floating)):
        raise ValueError(f"amount must be a real number or a 1-D array, got {amount!r}")
    else:
        try:
            value = float(cast(float, amount))
        except OverflowError:
            raise ValueError(f"amount {amount!r} does not fit a float") from None
        out = np.full(n, value, dtype=np.float64)
    if not np.all(np.isfinite(out)):
        raise ValueError("amount must be finite (no NaN or infinity)")
    return out


def _stream(stream: object) -> Floats:
    """A 2-D, finite array of floating dtype."""
    if not isinstance(stream, np.ndarray):
        raise ValueError(f"stream must be a numpy array, got {type(stream).__name__}")
    arr = cast(NDArray[Any], stream)
    if arr.ndim != 2 or not np.issubdtype(arr.dtype, np.floating):
        raise ValueError(f"stream must be 2-D of floating dtype, got dtype {arr.dtype}, shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("stream must be finite (no NaN or infinity)")
    return cast(Floats, arr)


def appraisal_years(appraisal_first_year: int, appraisal_last_year: int) -> NDArray[np.int64]:
    """The case's years, appraisal_first_year to appraisal_last_year inclusive."""
    first = _integer("appraisal_first_year", appraisal_first_year)
    last = _integer("appraisal_last_year", appraisal_last_year)
    if first > last:
        raise ValueError(f"appraisal_first_year {first} is after appraisal_last_year {last}")
    return np.arange(first, last + 1, dtype=np.int64)


def _rates(schedule: Sequence[Segment]) -> tuple[list[tuple[int, int | None, float]], int | None]:
    """The schedule's segments, checked, and its last year (None when open-ended)."""
    rows = cast(object, schedule)
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence) or len(cast(Sequence[object], rows)) == 0:
        raise ValueError("schedule must be a non-empty sequence of (first, last, rate) segments")
    segments: list[tuple[int, int | None, float]] = []
    expected_first = 1
    for i, row in enumerate(cast(Sequence[object], schedule)):
        where = f"schedule segment {i} (counting from 0)"
        if isinstance(row, (str, bytes)) or not isinstance(row, Sequence) or len(cast(Sequence[object], row)) != 3:
            raise ValueError(f"{where} must be a (first, last, rate) row, got {row!r}")
        first_obj, last_obj, rate_obj = cast(Sequence[object], row)
        if isinstance(first_obj, (bool, np.bool_)) or not isinstance(first_obj, (int, np.integer)):
            raise ValueError(f"{where}: first must be an integer, got {first_obj!r}")
        first = int(cast(Integer, first_obj))
        is_final = i == len(schedule) - 1
        last: int | None
        if last_obj is None:
            if not is_final:
                raise ValueError(f"{where}: only the last segment may have last None (onward)")
            last = None
        elif isinstance(last_obj, (bool, np.bool_)) or not isinstance(last_obj, (int, np.integer)):
            raise ValueError(f"{where}: last must be an integer or None, got {last_obj!r}")
        else:
            last = int(cast(Integer, last_obj))
            if last < first:
                raise ValueError(f"{where}: last {last} is before first {first}")
        if first != expected_first:
            raise ValueError(
                f"{where}: first is {first} but must be {expected_first}"
                " (segments start at year 1 and leave no gap or overlap)"
            )
        if isinstance(rate_obj, (bool, np.bool_)) or not isinstance(rate_obj, (int, float, np.integer, np.floating)):
            raise ValueError(f"{where}: rate must be a real number, got {rate_obj!r}")
        rate = float(cast(float, rate_obj))
        if not math.isfinite(rate) or rate <= -1.0:
            raise ValueError(f"{where}: rate {rate} must be finite and above -1")
        segments.append((first, last, rate))
        if last is not None:
            expected_first = last + 1
    return segments, segments[-1][1]


def discount_factors(schedule: Sequence[Segment], years: NDArray[np.integer[Any]], discount_base_year: int) -> Floats:
    """One factor per year: the product over k = 1..t of 1 / (1 + rate_k), t = year - discount_base_year."""
    segments, horizon = _rates(schedule)
    base = _integer("discount_base_year", discount_base_year)
    cal = _years(years)
    t_first = int(cal[0]) - base
    t_last = int(cal[-1]) - base
    if t_first < 0:
        raise ValueError(f"years start at {int(cal[0])}, before discount_base_year {base}; the schedule gives no rate for the past")
    if horizon is not None and t_last > horizon:
        raise ValueError(f"years run to {int(cal[-1])}, year {t_last} after discount_base_year, past the schedule's last year {horizon}")
    rate = np.empty(t_last, dtype=np.float64)  # rate[k - 1] is the rate of year k
    for first, last, r in segments:
        stop = t_last if last is None else min(last, t_last)
        rate[first - 1 : stop] = r
    factors = np.concatenate(([1.0], np.cumprod(1.0 / (1.0 + rate))))
    return factors[t_first:].copy()


def present_value(stream: Floats, factors: Floats) -> Floats:
    """Per draw, the sum over years of the stream times the factors."""
    s = _stream(stream)
    given = cast(object, factors)
    if not isinstance(given, np.ndarray):
        raise ValueError(f"factors must be a numpy array, got {type(given).__name__}")
    f = cast(NDArray[Any], given)
    if f.ndim != 1 or not np.issubdtype(f.dtype, np.floating) or f.shape[0] != s.shape[1]:
        raise ValueError(
            f"factors must be 1-D floating with one per year of the stream ({s.shape[1]}), "
            f"got dtype {f.dtype}, shape {f.shape}"
        )
    if not np.all(np.isfinite(f)):
        raise ValueError("factors must be finite (no NaN or infinity)")
    return np.sum(s * f, axis=1, dtype=np.float64)


def one_off(amount: Amount, year: Integer, years: Years, *, iterations: Integer) -> Floats:
    """The amount in one year."""
    draws = _positive("iterations", iterations)
    a = _amount(amount, draws)
    cal = _years(years)
    out = np.zeros((draws, cal.shape[0]), dtype=np.float64)
    out[:, _position("year", year, cal)] = a
    return out


def annual(amount: Amount, first: Integer, last: Integer, years: Years, *, iterations: Integer) -> Floats:
    """The amount every year from first to last inclusive."""
    return every_n_years(amount, 1, first, last, years, iterations=iterations)


def every_n_years(
    amount: Amount, period: Integer, first: Integer, last: Integer, years: Years, *, iterations: Integer
) -> Floats:
    """The amount in years first, first + period, ... up to last inclusive: a replacement cycle."""
    draws = _positive("iterations", iterations)
    a = _amount(amount, draws)
    step = _positive("period", period)
    cal = _years(years)
    i = _position("first", first, cal)
    j = _position("last", last, cal)
    if i > j:
        raise ValueError(f"first {int(cal[i])} is after last {int(cal[j])}")
    out = np.zeros((draws, cal.shape[0]), dtype=np.float64)
    out[:, i : j + 1 : step] = a[:, None]
    return out


def linear_phase_in(
    amount: Amount, start: Integer, full: Integer, last: Integer, years: Years, *, iterations: Integer
) -> Floats:
    """Rising in equal steps from amount / (full - start + 1) in year start to amount in year full,
    then amount each year to last."""
    draws = _positive("iterations", iterations)
    a = _amount(amount, draws)
    cal = _years(years)
    i = _position("start", start, cal)
    j = _position("full", full, cal)
    k = _position("last", last, cal)
    if j < i:
        raise ValueError(f"full {int(cal[j])} is before start {int(cal[i])}")
    if k < j:
        raise ValueError(f"last {int(cal[k])} is before full {int(cal[j])}")
    steps = j - i + 1
    out = np.zeros((draws, cal.shape[0]), dtype=np.float64)
    out[:, i:j] = a[:, None] * np.arange(1, steps, dtype=np.float64) / steps
    out[:, j : k + 1] = a[:, None]
    return out


def bring_forward(stream: Floats, by: Integer, years: Years) -> Floats:
    """Every flow moved by years earlier (by > 0) or later (by < 0), the vacated years zero;
    refused when a non-zero flow would leave the appraisal years."""
    s = _stream(stream)
    k = _integer("by", by)
    cal = _years(years)
    width = cal.shape[0]
    if s.shape[1] != width:
        raise ValueError(f"stream has {s.shape[1]} years, but years has {width}")
    m = min(abs(k), width)
    leaving = s[:, :m] if k > 0 else s[:, width - m :]
    if np.any(leaving != 0):
        raise ValueError(f"bringing forward by {k} years would move a non-zero flow outside the appraisal years")
    out = np.zeros(s.shape, dtype=np.float64)
    if k >= 0:
        out[:, : width - m] = s[:, m:]
    else:
        out[:, m:] = s[:, : width - m]
    return out
