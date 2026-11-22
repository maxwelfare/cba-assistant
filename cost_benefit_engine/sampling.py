"""The uniform numbers in (0, 1) every input's draws start from, before `distributions.quantile`.

`uniforms(names, iterations, random_seed, sampling_method, columns)` draws n = iterations of them,
stratified by Latin hypercube (`latin_hypercube`; McKay, Beckman and Conover 1979: each of the n
equal strata [k/n, (k+1)/n) holds exactly one value) or independently (`monte_carlo`).
The owner's Google Sheet template's own hash numbers (`sheet_random_numbers`), for a run that must
match the sheet, are the shared sheet package's `sheet_uniforms` (`cost_benefit_engine/shared.py`).
`correlate` reorders inputs' values to sourced rank correlations by Iman and Conover's method
(1982, Communications in Statistics - Simulation and Computation 11(3):311-334). Every refusal is a ValueError naming what it refuses.

The stream recipe, which is the project's reproducibility contract. Each input, and each column of
an input indexed over a table, has its own generator, so its numbers depend only on the seed, the
input's name and its row key, and adding, removing or reordering other inputs or rows moves nothing:

1. digest = SHA-256 of json.dumps([name, key]) (default arguments) encoded in UTF-8; key is None for
   an input with no table, the row key (a str or an int, never a bool) for a keyed table, and the
   int column index for a table given only by its row count. 0 and "0" are different keys.
2. words = [int.from_bytes(digest[4*i:4*i+4], "big") for i in range(8)].
3. rng = numpy.random.Generator(numpy.random.PCG64(numpy.random.SeedSequence([random_seed, *words]))).
   Python's `hash` changes between processes and is not used; numpy is pinned in the lock file.
4. latin_hypercube: perm = rng.permutation(n) first, then v = rng.random(n); each v[i] exactly 0 is
   replaced, in index order, by rng.random() drawn again until non-zero; value[i] =
   (perm[i] + v[i]) / n, moved with nextafter into stratum perm[i] if floor(value[i] * n) is not
   perm[i].
5. monte_carlo: rng.random(n), each value exactly 0 replaced in index order as in step 4.

A model's draws file, read by `tools/estimate_total.py`, is written by `write_draws`: line 1 is
"# seed S iterations N sampling M", the run's seed, iteration count and method, so the total tool can
draw its factors on these same streams; then one value per line, in draw order, at full precision.

Correlation. Each target is a Spearman rank correlation, converted to the normal-score correlation
2 sin(pi rho / 6) (Pearson 1907; Kruskal 1958). The inputs the correlations name are split into the
connected groups the entries link, and each group is rearranged on its own, its inputs in sorted-name
order, so other groups, entries and inputs never move it. Inside a group, a pair no entry names has
target 0; inputs in different groups are left independent. Each input's scores are the van der
Waerden scores of its incoming values, Phi^-1(rank / (n + 1)), so their order is the seeded order
already drawn and no generator is needed. With S the n by k scores, E their sample correlation with
Cholesky factor F, and C the converted target with Cholesky factor P, the new scores are
S F^-T P^T (Iman and Conover's correction for the scores' own sample correlation), and each input's
sorted values are laid out in the rank order of its new scores: values are reordered, never changed.
Inputs no correlation names are returned as copies, whatever their shape. Which inputs may take a
correlation at all is the case loader's to decide.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.special import ndtri

Floats = NDArray[np.float64]
Key = str | int | None
SAMPLING_METHODS = ("latin_hypercube", "monte_carlo")


def _is_int(x: object) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _rng(seed: int, name: str, key: Key) -> np.random.Generator:
    digest = hashlib.sha256(json.dumps([name, key]).encode("utf-8")).digest()
    words = [int.from_bytes(digest[4 * i : 4 * i + 4], "big") for i in range(8)]
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, *words])))


def _nonzero(rng: np.random.Generator, v: Floats) -> Floats:
    for i in np.flatnonzero(v == 0.0):
        while v[i] == 0.0:
            v[i] = rng.random()
    return v


def _stream(seed: int, name: str, key: Key, n: int, method: str) -> Floats:
    rng = _rng(seed, name, key)
    if method == "monte_carlo":
        return _nonzero(rng, rng.random(n))
    perm = rng.permutation(n)
    out = (perm + _nonzero(rng, rng.random(n))) / n
    for i in np.flatnonzero(np.floor(out * n) != perm):
        k = int(perm[i])
        while math.floor(out[i] * n) > k:
            out[i] = math.nextafter(out[i], -math.inf)
        while math.floor(out[i] * n) < k:
            out[i] = math.nextafter(out[i], math.inf)
    return out


def _row_keys(name: str, rows: object) -> list[Key]:
    if _is_int(rows):
        count = cast(int, rows)
        if count <= 0:
            raise ValueError(f"{name}: a row count must be a positive integer, got {count}")
        return list(range(count))
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise ValueError(f"{name}: columns takes a positive row count or a sequence of row keys, got {rows!r}")
    keys: list[Key] = []
    seen: set[str] = set()
    for item in cast(Sequence[object], rows):
        if not (isinstance(item, str) or _is_int(item)):
            raise ValueError(f"{name}: a row key must be a str or an int (not a bool), got {item!r}")
        key = cast(str | int, item)
        form = json.dumps(key)
        if form in seen:
            raise ValueError(f"{name}: row key {key!r} given twice")
        seen.add(form)
        keys.append(key)
    if not keys:
        raise ValueError(f"{name}: a keyed table needs at least one row key")
    return keys


def uniforms(
    names: Sequence[str],
    iterations: int,
    random_seed: int,
    sampling_method: str,
    columns: Mapping[str, int | Sequence[str | int]] | None = None,
) -> dict[str, Floats]:
    """iterations uniform numbers strictly inside (0, 1) per name; an iterations by rows array for a
    name in columns."""
    if not _is_int(iterations) or iterations <= 0:
        raise ValueError(f"iterations must be a positive integer, got {iterations!r}")
    if not _is_int(random_seed) or random_seed < 0:
        raise ValueError(f"random_seed must be a non-negative integer, got {random_seed!r}")
    if sampling_method not in SAMPLING_METHODS:
        raise ValueError(f"sampling_method must be one of {SAMPLING_METHODS}, got {sampling_method!r}")
    if len(set(names)) != len(names):
        twice = sorted({x for x in names if list(names).count(x) > 1})
        raise ValueError(f"names given twice: {twice}")
    tables = dict(columns or {})
    stray = sorted(set(tables) - set(names))
    if stray:
        raise ValueError(f"columns names inputs not among the names: {stray}")
    out: dict[str, Floats] = {}
    for name in names:
        if name in tables:
            keys = _row_keys(name, tables[name])
            out[name] = np.column_stack([_stream(random_seed, name, key, iterations, sampling_method) for key in keys])
        else:
            out[name] = _stream(random_seed, name, None, iterations, sampling_method)
    return out


def write_draws(path: Path | str, values: Sequence[float] | Floats, *, random_seed: int, iterations: int, sampling_method: str) -> None:
    """A model's draws file: the header line, then values[i] on line i + 2, each as its repr."""
    if sampling_method not in SAMPLING_METHODS:
        raise ValueError(f"sampling_method must be one of {SAMPLING_METHODS}, got {sampling_method!r}")
    for label, x, least in (("random_seed", random_seed, 0), ("iterations", iterations, 1)):
        if not _is_int(x) or x < least:
            raise ValueError(f"{label} must be an integer of at least {least}, got {x!r}")
    v = np.asarray(values, dtype=np.float64).ravel()
    if v.size != iterations:
        raise ValueError(f"{v.size} values for a run of {iterations} iterations")
    lines = [f"# seed {random_seed} iterations {iterations} sampling {sampling_method}", *(repr(float(x)) for x in v)]
    Path(path).write_text("\n".join(lines) + "\n")


def _groups(names: set[str], links: dict[frozenset[str], float]) -> list[list[str]]:
    neighbours: dict[str, set[str]] = {x: set() for x in names}
    for pair in links:
        a, b = sorted(pair)
        neighbours[a].add(b)
        neighbours[b].add(a)
    groups: list[list[str]] = []
    left = set(names)
    while left:
        stack = [min(left)]
        found: set[str] = set()
        while stack:
            x = stack.pop()
            if x not in found:
                found.add(x)
                stack.extend(neighbours[x] - found)
        left -= found
        groups.append(sorted(found))
    return groups


def _ranks(x: Floats) -> NDArray[np.int64]:
    r = np.empty(x.size, dtype=np.int64)
    r[np.argsort(x, kind="stable")] = np.arange(1, x.size + 1)
    return r


def _cholesky(m: Floats, refusal: str) -> Floats:
    try:
        return np.linalg.cholesky(m)
    except np.linalg.LinAlgError:
        raise ValueError(refusal) from None


def _rearrange(group: list[str], arrays: dict[str, Floats], links: dict[frozenset[str], float]) -> dict[str, Floats]:
    lengths = {x: arrays[x].size for x in group}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"correlated inputs' arrays differ in length: {lengths}")
    n, k = next(iter(lengths.values())), len(group)
    if n <= k:
        raise ValueError(f"group {group}: n = {n} must be larger than its number of inputs, {k}")
    target = np.eye(k)
    for i, a in enumerate(group):
        for j, b in enumerate(group):
            if i != j:
                rho = links.get(frozenset((a, b)), 0.0)
                target[i, j] = 2.0 * math.sin(math.pi * rho / 6.0)
    p = _cholesky(
        target,
        f"group {group}: the target correlation matrix (pairs no entry names at 0) is not positive "
        "definite; state the pair that is missing",
    )
    ranks = [_ranks(arrays[x]) for x in group]
    for i in range(k):
        for j in range(i + 1, k):
            if np.array_equal(ranks[i], ranks[j]) or np.array_equal(ranks[i], n + 1 - ranks[j]):
                raise ValueError(
                    f"group {group}: {group[i]} and {group[j]} have the same rank order (or its reverse), "
                    "so their scores' correlation matrix is singular"
                )
    scores = np.column_stack([ndtri(r / (n + 1.0)) for r in ranks])
    f = _cholesky(np.atleast_2d(np.corrcoef(scores, rowvar=False)), f"group {group}: the scores' correlation matrix is singular")
    new = scores @ np.linalg.inv(f).T @ p.T
    return {x: np.sort(arrays[x])[_ranks(new[:, i]) - 1] for i, x in enumerate(group)}


def correlate(u: Mapping[str, Floats], rank_correlations: Sequence[tuple[str, str, float]]) -> dict[str, Floats]:
    """New arrays: each correlated input's values reordered towards the targets, the rest copied."""
    links: dict[frozenset[str], float] = {}
    for a, b, rho in rank_correlations:
        for x in (a, b):
            if x not in u:
                raise ValueError(f"rank correlation ({a}, {b}): {x} is not an input drawn")
        if a == b:
            raise ValueError(f"rank correlation ({a}, {b}): {a} is given twice in one pair")
        if not -1.0 < rho < 1.0:
            raise ValueError(f"rank correlation ({a}, {b}): {rho} is not inside (-1, 1)")
        pair = frozenset((a, b))
        if pair in links:
            raise ValueError(f"rank correlation ({a}, {b}): the pair {a}, {b} is given twice")
        links[pair] = float(rho)
    out = {x: np.array(arr, dtype=np.float64, copy=True) for x, arr in u.items()}
    named = {x for pair in links for x in pair}
    for x in sorted(named):
        if out[x].ndim != 1:
            raise ValueError(f"{x}: a correlated input's array must be 1-D, got shape {out[x].shape}")
    for group in _groups(named, links):
        out.update(_rearrange(group, out, links))
    return out
