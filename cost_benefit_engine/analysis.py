"""What a case's analysis computes beside its model, from draws already made.

`prcc_columns(draws, rows, inputs_read)` turns a run's draws into the one-dimensional columns that
`outputs.prcc` takes, and `ranked_prcc(columns, output)` orders its result by size.
`per_event_breakdown(events, per_year, present_value)` factors a stream's mean
present value into events, value per event and a time factor, each a ratio of means.

Every refusal is a KeyError or ValueError naming what it refuses.
"""

from __future__ import annotations

import math
from collections.abc import Collection, Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from cost_benefit_engine import outputs

Floats = NDArray[np.float64]


def _vectors(name: str, values: NDArray[Any], rows: Mapping[str, Sequence[str]]) -> list[tuple[str, NDArray[Any]]]:
    """One input's draws as (column name, one-dimensional draws); a 2-D input gives one per row."""
    if values.ndim == 1:
        return [(name, values)]
    if name not in rows:
        raise KeyError(f"{name}: a 2-D input needs its row labels in rows")
    labels = rows[name]
    if len(labels) != values.shape[1]:
        raise ValueError(f"{name}: {len(labels)} row labels for {values.shape[1]} columns of draws")
    return [(f"{name}[{label}]", values[:, j]) for j, label in enumerate(labels)]


def _floats(name: str, vector: NDArray[Any]) -> list[tuple[str, Floats]]:
    """A numeric vector as one float column; string draws as one indicator per outcome but the first sorted."""
    if vector.dtype.kind != "U":
        return [(name, vector.astype(np.float64))]
    outcomes = [str(outcome) for outcome in np.unique(vector)]
    return [(f"{name} = {outcome}", (vector == outcome).astype(np.float64)) for outcome in outcomes[1:]]


def prcc_columns(
    draws: Mapping[str, Any], rows: Mapping[str, Sequence[str]], inputs_read: Collection[str] | None = None
) -> dict[str, Floats]:
    """Name to 1-D float array, ready for `outputs.prcc`, with every column that has no spread dropped.

    A 1-D numeric input keeps its name; a 2-D input is one column per row, `name[row]`, from
    `rows[name]`; string draws are one indicator per outcome except the first in sorted order, `name =
    outcome`. With `inputs_read` given, only those inputs are kept. A column of NaN is kept, for
    `outputs.prcc` to refuse.
    """
    return {
        column: floats
        for name, values in draws.items()
        if inputs_read is None or name in inputs_read
        for vector_name, vector in _vectors(name, np.asarray(values), rows)
        for column, floats in _floats(vector_name, vector)
        if float(np.ptp(floats)) != 0.0
    }


def ranked_prcc(columns: Mapping[str, Any], output: Any) -> dict[str, float]:
    """`outputs.prcc(columns, output)` ordered by descending absolute value, any NaN last."""
    ranked = sorted(outputs.prcc(columns, output).items(), key=lambda item: (math.isnan(item[1]), -abs(item[1])))
    return dict(ranked)


def per_event_breakdown(events: Any, per_year: Any, present_value: Any) -> dict[str, float]:
    """The factors of a stream's mean present value: events x value per event x time factor.

    `value_per_event` is mean per_year over mean events; `time_factor` is mean present_value over mean
    per_year. A zero mean in either denominator is refused, naming it.
    """
    events_mean = float(np.mean(np.asarray(events, dtype=np.float64)))
    per_year_mean = float(np.mean(np.asarray(per_year, dtype=np.float64)))
    present_value_mean = float(np.mean(np.asarray(present_value, dtype=np.float64)))
    for name, mean in (("events", events_mean), ("per_year", per_year_mean)):
        if mean == 0.0:
            raise ValueError(f"{name}: its mean is zero, so a ratio over it has no value")
    return {
        "events_mean": events_mean,
        "value_per_event": per_year_mean / events_mean,
        "time_factor": present_value_mean / per_year_mean,
        "present_value_mean": present_value_mean,
    }
