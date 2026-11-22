"""The small helpers every case's model and run wrote for itself: required inputs, the method pick, run basics, provenance.

`need` and `pick_method` read a model's inputs and refuse a missing one where it enters (core rule 3). `pick_method`
is how a mixture of independent methods is evaluated: each draw takes one method's value whole, never an average of
them (the owner's rule 9). `provenance` is the block a run writes to say what it read and in what state.
"""

from __future__ import annotations

import dataclasses
import hashlib
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from cost_benefit_engine.outputs import Arr, summary

_ENGINE = Path(__file__).resolve().parent


class CheckFailed(Exception):
    """A check of the run failed: the run stops and writes nothing."""


def f64(a: Any) -> Arr:
    return np.asarray(a, dtype=np.float64)


def _present(inputs: Mapping[str, Any], name: str) -> Any:
    if name not in inputs:
        raise KeyError(f"the model needs the input {name!r}, which the inputs do not hold")
    return inputs[name]


def need(inputs: Mapping[str, Any], name: str) -> Arr:
    """An input's draws as floats, in any number of dimensions; a missing input raises a KeyError naming it."""
    return f64(_present(inputs, name))


def pick_method(inputs: Mapping[str, Any], name: str, by_method: Mapping[str, Any]) -> Arr:
    """Each draw's value from the array of its own outcome of the categorical input `name`.

    `by_method` maps outcome to an array whose first axis is the draws; a 2-D array is draws by years. A row is one
    array's row, whole. An outcome with no entry, or arrays that do not match the draws or one another, are refused
    with a ValueError; an entry no draw picks is allowed and is not read.
    """
    outcomes = np.asarray(_present(inputs, name)).astype(str)
    unknown = sorted(set(outcomes.ravel().tolist()) - set(by_method))
    if unknown:
        raise ValueError(f"{name}: outcomes {unknown} have no entry in by_method")
    used, which = np.unique(outcomes, return_inverse=True)
    stacked = np.stack([f64(by_method[m]) for m in used.tolist()])
    if stacked.shape[1:2] != outcomes.shape:
        raise ValueError(f"{name}: by_method arrays have shape {stacked.shape[1:]}, the input's draws {outcomes.shape}")
    return stacked[which, np.arange(outcomes.size)]


def summary_dict(values: Any) -> dict[str, Any]:
    """`outputs.summary` of `values`, as a plain dict for a results file."""
    return dataclasses.asdict(summary(values))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    # --literal-pathspecs: a file named with * or : is that file, not a pattern.
    done = subprocess.run(["git", "--literal-pathspecs", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return done.stdout.strip()


def provenance(command: str, root: Path, files: Sequence[Path], include_engine: bool = True) -> dict[str, Any]:
    """What this run reads and in what state; call it when the run starts, not after.

    `command` is recorded as given and `commit` is the full HEAD of `root`. `files_read` maps each path, relative to
    `root`, to its SHA-256, for every file in `files` and, with `include_engine`, every `*.py` directly in the folder
    this module is in, which is the engine this run really imports. `working_tree` says whether `git status` shows
    any of those files uncommitted, an untracked one included. A file outside `root`, judged on its resolved path, is
    a ValueError, the engine's included: the engine is never left out of the record silently.
    """
    base = root.resolve()
    read = [*files, *(sorted(_ENGINE.glob("*.py")) if include_engine else [])]
    files_read = {p.resolve().relative_to(base).as_posix(): sha256(p) for p in read}
    # With no paths at all, `git status --` would report on the whole repository, not on the files read.
    dirty = bool(files_read) and _git(base, "status", "--porcelain", "--", *files_read) != ""
    return {
        "command": command,
        "commit": _git(base, "rev-parse", "HEAD"),
        "working_tree": "with uncommitted changes to the files it reads" if dirty else "clean in every file it reads",
        "files_read": files_read,
        "date": time.strftime("%Y-%m-%d %H:%M %Z"),
    }
