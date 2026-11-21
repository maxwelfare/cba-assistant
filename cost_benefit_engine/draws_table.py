"""A table of draws: every input a model drew and every output it computed, draw by draw, in one file.

The file is one uncompressed `.npz` written by `numpy.savez`. Its key `header` holds the line `sampling.write_draws`
writes first, "# seed S iterations N sampling M"; its keys `input/<name>` and `output/<name>` each hold `iterations`
float64 values in draw order, so draw i of every column is the same draw. A name is split from its prefix at the first
"/", so a name may itself hold "/".

A table holds what its producer drew and nothing else: an input the producer did not write has no column, and no
reader of the table can see it. The reader knows nothing of the producer. Every refusal is a ValueError naming the
column or field it refuses.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from cost_benefit_engine.sampling import SAMPLING_METHODS

Floats = NDArray[np.float64]

_HEADER = re.compile(r"# seed (\d+) iterations (\d+) sampling (\S+)")
_KINDS = ("input", "output")


@dataclass(frozen=True)
class DrawsTable:
    """The columns of a table of draws, each a float64 array of `iterations` values, and its header's fields."""

    inputs: dict[str, Floats]
    outputs: dict[str, Floats]
    random_seed: int
    iterations: int
    sampling_method: str


def _fields(random_seed: object, iterations: object, sampling_method: object) -> None:
    """The refusals of `sampling.write_draws` for the header's fields."""
    if sampling_method not in SAMPLING_METHODS:
        raise ValueError(f"sampling_method must be one of {SAMPLING_METHODS}, got {sampling_method!r}")
    for label, x, least in (("random_seed", random_seed, 0), ("iterations", iterations, 1)):
        if not isinstance(x, int) or isinstance(x, bool) or x < least:
            raise ValueError(f"{label} must be an integer of at least {least}, got {x!r}")


def _column(kind: str, name: str, values: object, iterations: int) -> Floats:
    if not name:
        raise ValueError(f"an {kind} has an empty name")
    col = np.asarray(values, dtype=np.float64)
    if col.ndim != 1 or col.size != iterations:
        raise ValueError(f"{kind} {name!r} has shape {col.shape}, not ({iterations},)")
    if not np.isfinite(col).all():
        raise ValueError(f"{kind} {name!r} holds a value that is not finite")
    return col


def write_table(
    path: Path | str,
    inputs: dict[str, Floats],
    outputs: dict[str, Floats],
    *,
    random_seed: int,
    iterations: int,
    sampling_method: str,
) -> None:
    """Write the table to `path`, refusing before anything is written."""
    _fields(random_seed, iterations, sampling_method)
    if not outputs:
        raise ValueError("a table needs at least one output")
    arrays: dict[str, Floats | NDArray[np.str_]] = {
        "header": np.array(f"# seed {random_seed} iterations {iterations} sampling {sampling_method}")
    }
    for kind, columns in zip(_KINDS, (inputs, outputs)):
        for name, values in columns.items():
            arrays[f"{kind}/{name}"] = _column(kind, name, values, iterations)
    with open(path, "wb") as f:  # a file object, so numpy adds no ".npz" to a path that lacks it
        np.savez(f, allow_pickle=False, **arrays)


def read_table(path: Path | str) -> DrawsTable:
    """The table at `path`, refusing a missing or malformed header, any other key, and a column of another length."""
    with np.load(path, allow_pickle=False) as z:
        if "header" not in z.files:
            raise ValueError(f"{path}: no header")
        header = z["header"]
        match = _HEADER.fullmatch(str(header.item())) if header.ndim == 0 and header.dtype.kind == "U" else None
        if match is None:
            raise ValueError(f"{path}: malformed header {header!r}")
        random_seed, iterations, sampling_method = int(match[1]), int(match[2]), match[3]
        _fields(random_seed, iterations, sampling_method)
        found: dict[str, dict[str, Floats]] = {kind: {} for kind in _KINDS}
        for key in z.files:
            if key == "header":
                continue
            kind, _, name = key.partition("/")
            if kind not in found:
                raise ValueError(f"{path}: key {key!r} is neither the header nor an input/ or output/ column")
            found[kind][name] = _column(kind, name, z[key], iterations)
    if not found["output"]:
        raise ValueError(f"{path}: no outputs")
    return DrawsTable(found["input"], found["output"], random_seed, iterations, sampling_method)
