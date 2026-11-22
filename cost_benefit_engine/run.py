"""The run: a loaded case and its model turned into every draw's present values, net present value and
benefit-cost ratio for each option against the base case, at each discount rate.

`model_from(case)` loads the case's `model.py` afresh as a package
of its own; `run(case, model)` draws the case's uniform numbers (its `sampling_method`, then its rank
correlations) and hands them to `evaluate(case, model, uniforms)`, which does the rest: each input's draws (a
mixture through `distributions.pick`, each component by its own money), the money conversions of
`Case.conversions`, any held values of a scenario run, the model once per option on the same read-only draws,
the present values by `timeline`, the increments over the base case, and the accounting identity. Every
refusal is a `RunError` naming the input, option, key or schedule at fault; a `ValueError` from `distributions`,
`sampling` or `timeline` is raised again as one, chained. An exception raised by the model itself, at load or
inside a call, is the case's own: it propagates unchanged with a note naming the case folder or the option.

A model must be deterministic in its inputs: the run gives it no random numbers of its own, so its results
reproduce from the case's seed and every option sees the same numbers (a model's own randomness awaits the
owner's rule on where its random numbers come from). `model_from`, `run`, `evaluate`, `Run` and `RunError` are
the engine's; a case calls none of them. A case's run script may call `stream_increments`, each stream's increment.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import math
import sys
import types
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from cost_benefit_engine import distributions, sampling, shared, timeline
from cost_benefit_engine.case import RATE_KEYS, SHEET_RANDOM_NUMBERS, STREAM_STATUSES, Case, Conversion

Floats = NDArray[np.float64]
Model = Callable[[Mapping[str, NDArray[Any]], NDArray[np.int64], str], Mapping[str, object]]
BOUNDED_UNITS = ("probability", "share")  # cases/README.md item 4: a draw outside [0, 1] is reported
IDENTITY_TOLERANCE = 1e-9  # times max(G, 1), G the draw's gross present value (settled choice 9)
PACKAGE_PREFIX = "_cost_benefit_case_"


@dataclass(frozen=True, eq=False)
class Unconverted:
    """An input's draws in its own units: its own currency and price year for money, before `Case.conversions` (a rate's
    and a non-money input's draws alike). It has no arithmetic, so strict pyright refuses a sum or product of a bare
    `Unconverted` with the case's money (`Floats`); the run's conversion (`_Draws.convert`) is the typed way from it to
    the case's money. `own_units()` is the untyped way out: it returns the plain array, for a report or a check, and
    pyright does not refuse that array added to the case's money, so a call to it is where a mixed-unit sum would hide."""

    _values: NDArray[Any]

    def own_units(self) -> NDArray[Any]:
        return self._values


class RunError(Exception):
    """A run refused, naming the input, option, key or schedule at fault."""


@dataclass(frozen=True)
class Run:
    """Everything a run gives, every array read-only.

    `draws` holds each input the model sees as given to it, converted to the case's money; `raw_draws` the same
    before conversion, as `Unconverted` (a mixture's: its picked component's raw draw, which may mix currencies and price years
    draw by draw). An indexed input's array is iterations by rows, column j being row `rows[name][j]`. `picks`
    holds, for each mixture not held, the top-level component index each draw picked. `conversions` holds each
    conversion applied, by the input (or component) it converted. `held` holds a scenario run's inputs and their
    stated values; a held value is taken in its input's own money and converted as its draws would be, with no
    way yet to state other money; a held mixture (`held_mixtures`) is never converted, so where its components
    are money its value is in the case's currency and price base year. `held_partners` names, for each held
    input with a rank-correlation partner not held, those partners: the held value meets their unconditional
    draws, so the correlation is not respected. `bounds_reports` counts, for each probability or share input
    with any, the draws outside [0, 1]. `nan_ratio_counts[label][option]` counts the draws whose cost increment
    is not positive, where the benefit-cost ratio is NaN. `evidence_counts` counts every entry of `Case.inputs`
    (a mixture and each component alike) by evidence type. `inputs_read` holds, sorted, every key the model looked
    up in its inputs by `[]`, `get` or `in` for any option, a key absent from them included; `inputs_iterated` is
    True when the model iterated its inputs (`iter`, `keys`, `items`, `dict(...)`), and then every key counts as
    read.

    `present_values[label][option][stream]` covers every option, the base case included; the increments, net
    present value and benefit-cost ratio cover each option other than the base case.

    `stream_status` gives each stream's status from case.toml, a missing status reported as `counted` (the
    default, so a case written before statuses existed runs as it did). A `zero` stream's arrays in `streams`,
    and so its present values, are zero in every option, the base case included; the model's intermediate
    results are left as it returned them. A `flagged` stream is counted in every total;
    `net_present_value_without_flagged`, nested as `net_present_value`, is the same sum over the other streams,
    and equals `net_present_value` exactly when no stream is flagged.

    Memory: the streams take iterations x years x streams x options x 8 bytes, about 1.3 GB for 70 years,
    8 streams and 3 options at 100,000 iterations.

    For the summaries a referee will ask for: a per-draw benefit-cost ratio grows without bound as the cost
    increment nears zero, so its mean is unstable; a summary reports the ratio of the expected increments beside
    it, and ranks options against each other by net present value (Boardman et al., Cost-Benefit Analysis:
    Concepts and Practice).
    """

    iterations: int
    random_seed: int | None
    sampling_method: str | None
    draws: Mapping[str, NDArray[Any]]
    raw_draws: Mapping[str, Unconverted]
    rows: Mapping[str, tuple[str, ...]]
    picks: Mapping[str, NDArray[np.int64]]
    conversions: Mapping[str, Conversion]
    held: Mapping[str, object]
    held_mixtures: tuple[str, ...]
    held_partners: Mapping[str, tuple[str, ...]]
    bounds_reports: Mapping[str, int]
    nan_ratio_counts: Mapping[str, Mapping[str, int]]
    evidence_counts: Mapping[str, int]
    years: NDArray[np.int64]
    streams: Mapping[str, Mapping[str, Floats]]
    intermediate_results: Mapping[str, Mapping[str, Floats]]
    present_values: Mapping[str, Mapping[str, Mapping[str, Floats]]]
    benefits_increment: Mapping[str, Mapping[str, Floats]]
    costs_increment: Mapping[str, Mapping[str, Floats]]
    net_present_value: Mapping[str, Mapping[str, Floats]]
    net_present_value_without_flagged: Mapping[str, Mapping[str, Floats]]
    stream_status: Mapping[str, str]
    benefit_cost_ratio: Mapping[str, Mapping[str, Floats]]
    inputs_read: tuple[str, ...]
    inputs_iterated: bool


# ---------------------------------------------------------------- loading the model

_FOLDERS: dict[str, Path] = {}  # each loaded case package (and any package inside one) to its folder


class _FreshLoader(importlib.abc.Loader):
    """Executes a module from its source every time, never from cached bytecode, which is keyed on the
    source's size and time and so cannot tell two versions of a file apart."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> types.ModuleType | None:
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        code = compile(self.path.read_bytes(), str(self.path), "exec", dont_inherit=True)
        exec(code, module.__dict__)


class _CaseFinder(importlib.abc.MetaPathFinder):
    """Finds the modules and packages beside a case's model.py, for its relative imports."""

    def find_spec(
        self, fullname: str, path: Sequence[str] | None, target: types.ModuleType | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        parent, _, leaf = fullname.rpartition(".")
        folder = _FOLDERS.get(parent)
        if folder is None:
            return None
        module = folder / f"{leaf}.py"
        if module.is_file():
            return importlib.util.spec_from_file_location(fullname, module, loader=_FreshLoader(module))
        init = folder / leaf / "__init__.py"
        if init.is_file():
            _FOLDERS[fullname] = folder / leaf
            return importlib.util.spec_from_file_location(
                fullname, init, loader=_FreshLoader(init), submodule_search_locations=[str(folder / leaf)]
            )
        return None


def _purge(package: str) -> None:
    for name in [m for m in sys.modules if m == package or m.startswith(package + ".")]:
        del sys.modules[name]
    for name in [p for p in _FOLDERS if p == package or p.startswith(package + ".")]:
        del _FOLDERS[name]


def model_from(case: Case) -> Model:
    """The `model` function of the case's model.py, executed afresh with its sibling modules as a package named
    for the case folder's resolved path, so its relative imports resolve to its own folder; sys.path is not
    changed. The package stays registered until this case's next load."""
    folder = Path(case.folder).resolve()
    if not (folder / "model.py").is_file():
        raise RunError(f"case {folder}: no model.py in the case folder")
    package = PACKAGE_PREFIX + hashlib.sha256(str(folder).encode("utf-8")).hexdigest()
    _purge(package)
    if not any(isinstance(finder, _CaseFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, _CaseFinder())
    spec = importlib.machinery.ModuleSpec(package, None, is_package=True)
    spec.submodule_search_locations = [str(folder)]
    sys.modules[package] = importlib.util.module_from_spec(spec)
    _FOLDERS[package] = folder
    try:
        module = importlib.import_module(f"{package}.model")
    except BaseException as e:
        _purge(package)
        e.add_note(f"raised while loading the model of case {folder}: model.py (or a module it imports)")
        raise
    fn: object = getattr(module, "model", None)
    if not callable(fn):
        _purge(package)
        raise RunError(f"case {folder}: model.py defines no function model(inputs, appraisal_years, option)")
    return cast(Model, fn)


# ---------------------------------------------------------------- the case's shape


def _options(case: Case) -> tuple[list[str], str]:
    raw, base = case.frame.get("options"), case.frame.get("base_case")
    if not isinstance(raw, list) or not all(isinstance(o, str) for o in cast(list[object], raw)):
        raise RunError(f"options: must be a list of option names, got {raw!r}")
    options = cast(list[str], raw)
    if not isinstance(base, str) or base not in options:
        raise RunError(f"base_case: {base!r} is not one of the options {options}")
    if not [o for o in options if o != base]:
        raise RunError(f"options {options}: no option besides the base case {base!r}, so no increment to report")
    return options, base


def _components(spec: Mapping[str, object]) -> Iterator[str]:
    for part in cast(Sequence[Mapping[str, object]], spec.get("components", ())):
        yield str(part["input"])
        yield from _components(part)


def _seen(case: Case) -> list[str]:
    """The inputs the model sees: every input but a mixture's components, at any depth."""
    components = {c for spec in case.inputs.values() for c in _components(spec)}
    return [name for name in case.inputs if name not in components]


def _rows(case: Case, seen: Sequence[str]) -> dict[str, tuple[str, ...]]:
    return {x: tuple(cast(Sequence[str], case.inputs[x]["rows"])) for x in seen if "rows" in case.inputs[x]}


def _is_rate(spec: Mapping[str, object]) -> bool:
    return any(key in spec for key in RATE_KEYS)


def _real(value: object) -> bool:
    return (
        not isinstance(value, (bool, np.bool_))
        and isinstance(value, (int, float, np.integer, np.floating))
        and math.isfinite(float(cast(float, value)))
    )


# ---------------------------------------------------------------- run and evaluate


def run(
    case: Case,
    model: Model,
    *,
    iterations: int | None = None,
    random_seed: int | None = None,
    held: Mapping[str, object] | None = None,
) -> Run:
    """The case's uniform numbers, drawn by its sampling method and correlated by its rank correlations, then
    `evaluate`. `iterations` and `random_seed` override the case's own; `held` makes a scenario run."""
    _override("iterations", iterations, 1)
    _override("random_seed", random_seed, 0)
    _options(case)
    method = cast(str, case.frame.get("sampling_method"))
    n = cast(int, iterations if iterations is not None else case.frame.get("iterations"))
    seen = _seen(case)
    rows = _rows(case, seen)
    seed: int | None
    if method == SHEET_RANDOM_NUMBERS:
        problems: list[str] = []
        if random_seed is not None:
            problems.append("random_seed: the sheet's random numbers take no seed, so an override is refused")
        if case.rank_correlations:
            problems.append("rank correlations: the sheet's random numbers are not correlated, so a run with them would not match the sheet")
        for name in seen:
            if name in rows:
                problems.append(f"input {name!r}: indexed by a table, it has no sheet column per row")
            elif name not in case.sheet_columns:
                problems.append(f"input {name!r}: no sheet column to draw its sheet random numbers from")
        if problems:
            raise RunError("sheet_random_numbers: " + "; ".join(problems))
        u: dict[str, Floats] = {}
        sheet_uniforms: Callable[[int, int, int], Floats] = shared.sheets("script").sheet_uniforms
        for name in seen:
            try:
                u[name] = sheet_uniforms(*case.sheet_columns[name], n)
            except ValueError as e:
                raise RunError(f"input {name!r}: sheet random numbers: {e}") from e
        seed = None
    else:
        seed = cast(int, random_seed if random_seed is not None else case.frame.get("random_seed"))
        try:
            drawn = sampling.uniforms(seen, n, seed, sampling_method=method, columns={x: list(r) for x, r in rows.items()})
            u = sampling.correlate(drawn, case.rank_correlations)
        except ValueError as e:
            raise RunError(f"sampling the uniform numbers ({method}): {e}") from e
    return dataclasses.replace(evaluate(case, model, u, held=held), random_seed=seed, sampling_method=method)


def _override(label: str, value: object, least: int) -> None:
    if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < least):
        kind = "positive" if least else "non-negative"
        raise RunError(f"{label}: an override must be a {kind} integer, got {value!r}")


def evaluate(
    case: Case, model: Model, uniforms: Mapping[str, NDArray[Any]], *, held: Mapping[str, object] | None = None
) -> Run:
    """The run on uniform numbers the caller supplies: exactly the inputs the model sees, each of shape (n,) or,
    for an indexed input, (n, rows), with one n throughout, every value strictly between 0 and 1."""
    options, base = _options(case)
    seen = _seen(case)
    rows = _rows(case, seen)
    u, n = _checked_uniforms(case, uniforms, seen, rows)
    stated = _checked_held(case, seen, rows, held)
    years, factors = _discounting(case)
    kinds = _kinds(case)
    status = _status(case)
    draws = _Draws(case, seen, rows, u, stated, n)

    streams: dict[str, dict[str, Floats]] = {}
    results: dict[str, dict[str, Floats]] = {}
    record = _Reads()
    for option in options:
        given = _Recorded({k: _frozen(v) for k, v in draws.draws.items()}, record)
        try:
            returned = model(given, _frozen(years), option)
        except Exception as e:
            e.add_note(f"raised by the case's model for option {option!r}")
            raise
        received, results[option] = _received(case, option, returned, n, years.shape[0])
        streams[option] = {s: _frozen(np.zeros_like(a)) if status[s] == "zero" else a for s, a in received.items()}

    present: dict[str, dict[str, dict[str, Floats]]] = {}
    benefits: dict[str, dict[str, Floats]] = {}
    costs: dict[str, dict[str, Floats]] = {}
    npv: dict[str, dict[str, Floats]] = {}
    npv_unflagged: dict[str, dict[str, Floats]] = {}
    unflagged = {s: k for s, k in kinds.items() if status[s] != "flagged"}
    ratio: dict[str, dict[str, Floats]] = {}
    nan_counts: dict[str, dict[str, int]] = {}
    for label, f in factors.items():
        pv = {o: {s: _frozen(_pv(label, streams[o][s], f)) for s in kinds} for o in options}
        present[label] = pv
        benefits[label], costs[label], npv[label], ratio[label], nan_counts[label] = {}, {}, {}, {}, {}
        npv_unflagged[label] = {}

        def total(option: str, kind: str, among: Mapping[str, str] = kinds) -> Floats:
            out = np.zeros(n)
            for s, k in among.items():
                if k == kind:
                    out = out + pv[option][s]
            return out

        for o in options:
            if o == base:
                continue
            b = total(o, "benefit") - total(base, "benefit")
            c = total(o, "cost") - total(base, "cost")
            net = b - c
            positive = c > 0.0
            r = np.full(n, np.nan)
            np.divide(b, c, out=r, where=positive)
            _identity(label, o, base, streams, kinds, f, net)
            b_u = total(o, "benefit", unflagged) - total(base, "benefit", unflagged)
            net_u = b_u - (total(o, "cost", unflagged) - total(base, "cost", unflagged))
            _identity(label, o, base, streams, unflagged, f, net_u)
            npv_unflagged[label][o] = _frozen(net_u)
            benefits[label][o], costs[label][o], npv[label][o], ratio[label][o] = _frozen(b), _frozen(c), _frozen(net), _frozen(r)
            nan_counts[label][o] = int(n - np.count_nonzero(positive))

    evidence: dict[str, int] = {}
    for name, spec in case.inputs.items():
        kind = spec.get("evidence_type")
        if not isinstance(kind, str):
            raise RunError(f"input {name!r}: evidence_type is {kind!r}, not an evidence type")
        evidence[kind] = evidence.get(kind, 0) + 1
    partners: dict[str, tuple[str, ...]] = {}
    for name in stated:
        free = tuple(b if a == name else a for a, b, _ in case.rank_correlations if name in (a, b))
        free = tuple(p for p in free if p not in stated)
        if free:
            partners[name] = free
    bounds: dict[str, int] = {}
    for name in seen:
        values = draws.draws[name]
        if case.inputs[name].get("unit") in BOUNDED_UNITS and values.dtype.kind == "f":
            count = int(np.count_nonzero((values < 0.0) | (values > 1.0)))
            if count:
                bounds[name] = count

    return Run(
        iterations=n,
        random_seed=None,
        sampling_method=None,
        draws={k: _frozen(v) for k, v in draws.draws.items()},
        raw_draws={k: Unconverted(_frozen(v.own_units())) for k, v in draws.raw.items()},
        rows=rows,
        picks={k: _frozen(v) for k, v in draws.picks.items()},
        conversions=dict(draws.applied),
        held=stated,
        held_mixtures=tuple(x for x in stated if case.inputs[x].get("distribution") == "mixture"),
        held_partners=partners,
        bounds_reports=bounds,
        nan_ratio_counts=nan_counts,
        evidence_counts=evidence,
        years=_frozen(years),
        streams=streams,
        intermediate_results=results,
        present_values=present,
        benefits_increment=benefits,
        costs_increment=costs,
        net_present_value=npv,
        net_present_value_without_flagged=npv_unflagged,
        stream_status=status,
        benefit_cost_ratio=ratio,
        inputs_read=tuple(sorted(record.keys)),
        inputs_iterated=record.iterated,
    )


@dataclass
class _Reads:
    keys: set[str] = dataclasses.field(default_factory=lambda: set[str]())
    iterated: bool = False


class _Recorded(Mapping[str, NDArray[Any]]):
    """The draws as the model sees them: read-only (no assignment), each value as given, every key looked up noted
    in `record` (`get` and `in` look up through `[]`; iterating notes every key and the iteration)."""

    def __init__(self, data: dict[str, NDArray[Any]], record: _Reads) -> None:
        self._data = types.MappingProxyType(data)
        self._record = record

    def __getitem__(self, key: str) -> NDArray[Any]:
        self._record.keys.add(key)
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        self._record.iterated = True
        self._record.keys.update(self._data)
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


# ---------------------------------------------------------------- the checks on what comes in


def _frozen[T: np.generic](a: NDArray[T]) -> NDArray[T]:
    out = a.copy()
    out.flags.writeable = False
    return out


def _checked_uniforms(
    case: Case, uniforms: Mapping[str, NDArray[Any]], seen: Sequence[str], rows: Mapping[str, tuple[str, ...]]
) -> tuple[dict[str, Floats], int]:
    if not isinstance(cast(object, uniforms), Mapping):
        raise RunError(f"uniforms: must be a mapping of input name to uniform numbers, got {type(uniforms).__name__}")
    missing = [x for x in seen if x not in uniforms]
    if missing:
        raise RunError(f"uniforms: no uniform numbers for the inputs {missing}, which the model sees")
    stray = [x for x in uniforms if x not in seen]
    if stray:
        kind = {x: "a mixture's component, drawn through its mixture" if x in case.inputs else "not an input" for x in stray}
        raise RunError(f"uniforms: given for inputs the model does not see: {kind}")
    out: dict[str, Floats] = {}
    for name in seen:
        a = cast(object, uniforms[name])
        given = type(a).__name__
        if not isinstance(a, np.ndarray) or cast(NDArray[Any], a).dtype.kind != "f":
            raise RunError(f"uniforms for {name!r}: must be a numpy float array, got {given}")
        arr = cast(Floats, a)
        shape = "(n, %d)" % len(rows[name]) if name in rows else "(n,)"
        if arr.ndim != (2 if name in rows else 1) or (name in rows and arr.shape[1] != len(rows[name])):
            raise RunError(f"uniforms for {name!r}: shape {arr.shape}, expected {shape}")
        bad = int(np.count_nonzero(~((arr > 0.0) & (arr < 1.0))))
        if bad:
            raise RunError(f"uniforms for {name!r}: {bad} values not strictly between 0 and 1 (NaN included)")
        out[name] = arr.astype(np.float64, copy=True)
    lengths = {name: a.shape[0] for name, a in out.items()}
    if len(set(lengths.values())) != 1:
        raise RunError(f"uniforms: the inputs' numbers differ in length: {lengths}")
    n = next(iter(lengths.values()))
    if n == 0:
        raise RunError("uniforms: no draws (length 0)")
    return out, n


def _checked_held(
    case: Case, seen: Sequence[str], rows: Mapping[str, tuple[str, ...]], held: Mapping[str, object] | None
) -> dict[str, object]:
    """Settled choice 6.1: each held input's stated value, checked against its kind."""
    if held is None:
        return {}
    if not isinstance(cast(object, held), Mapping):
        raise RunError(f"held: must be a mapping of input name to its stated value, got {type(held).__name__}")
    out: dict[str, object] = {}
    for name, value in held.items():
        where = f"held input {name!r}"
        if name not in case.inputs:
            raise RunError(f"{where}: not an input of the case")
        if name not in seen:
            raise RunError(f"{where}: a mixture's component is drawn only through its mixture; hold the mixture")
        spec = case.inputs[name]
        if spec.get("distribution") == "categorical":
            outcomes = [str(o) for o in cast(Mapping[object, object], spec["outcomes"])]
            want = f"one of its outcomes {outcomes}"

            def fits(value: object) -> bool:
                return isinstance(value, str) and value in outcomes
        else:
            want = "a finite number"
            fits = _real
        if name in rows and isinstance(value, Mapping):
            per_row = cast(Mapping[object, object], value)
            missing = [r for r in rows[name] if r not in per_row]
            extra = [k for k in per_row if k not in rows[name]]
            if missing or extra:
                raise RunError(f"{where}: a value per row must name every row once; missing {missing}, unknown {extra}")
            bad = [r for r in rows[name] if not fits(per_row[r])]
            if bad:
                raise RunError(f"{where}: the value of rows {bad} is not {want}")
            out[name] = dict(per_row)
        elif fits(value):
            out[name] = value
        else:
            form = " (a single value for every row, or a mapping of every row identifier to one)" if name in rows else ""
            raise RunError(f"{where}: {value!r} is not {want}{form}")
    return out


def _discounting(case: Case) -> tuple[NDArray[np.int64], dict[str, Floats]]:
    labels = [s.label for s in case.real_discount_rates]
    twice = sorted({x for x in labels if labels.count(x) > 1})
    if twice:
        raise RunError(f"real discount rates: two schedules share the label {twice}")
    if not labels:
        raise RunError("real discount rates: the case has no discount schedule")
    frame = case.frame
    try:
        years = timeline.appraisal_years(
            cast(int, frame.get("appraisal_first_year")), cast(int, frame.get("appraisal_last_year"))
        )
    except ValueError as e:
        raise RunError(f"appraisal_first_year and appraisal_last_year: {e}") from e
    factors: dict[str, Floats] = {}
    for s in case.real_discount_rates:
        try:
            factors[s.label] = timeline.discount_factors(s.rows, years, cast(int, frame.get("discount_base_year")))
        except ValueError as e:
            raise RunError(f"discount schedule {s.label!r}: {e}") from e
    return years, factors


def _kinds(case: Case) -> dict[str, str]:
    kinds: dict[str, str] = {}
    for name, stream in case.streams.items():
        kind = stream.get("kind")
        if kind not in ("cost", "benefit"):
            raise RunError(f"stream {name!r}: kind {kind!r} is neither cost nor benefit")
        kinds[name] = cast(str, kind)
    return kinds


def _status(case: Case) -> dict[str, str]:
    """Each stream's status: counted, flagged or zero; a missing status means counted."""
    status: dict[str, str] = {}
    for name, stream in case.streams.items():
        value = stream.get("status", "counted")
        if value not in STREAM_STATUSES:
            raise RunError(f"stream {name!r}: status {value!r} is not counted, flagged or zero")
        status[name] = cast(str, value)
    return status


def _received(
    case: Case, option: str, returned: object, n: int, years: int
) -> tuple[dict[str, Floats], dict[str, Floats]]:
    """Settled choice 7: the model's return checked and copied, as received, into the run's own arrays."""
    if not isinstance(returned, Mapping):
        raise RunError(f"option {option!r}: the model returned {type(returned).__name__}, not a mapping")
    given = cast(Mapping[object, object], returned)
    declared: dict[str, tuple[int, ...]] = {s: (n, years) for s in case.streams}
    declared.update({r: (n,) for r in case.intermediate_results})
    problems = [f"{k!r} missing" for k in declared if k not in given]
    problems += [f"{k!r} is not a stream or intermediate result case.toml declares" for k in given if k not in declared]
    copies: dict[str, Floats] = {}
    for key, shape in declared.items():
        if key not in given:
            continue
        v = given[key]
        if not isinstance(v, np.ndarray):
            problems.append(f"{key!r} is not a numpy array (got {type(v).__name__})")
            continue
        if cast(NDArray[Any], v).dtype.kind != "f":
            problems.append(f"{key!r} is not a float array (got dtype {cast(NDArray[Any], v).dtype})")
            continue
        arr = cast(NDArray[np.floating[Any]], v)
        if arr.shape != shape:
            problems.append(f"{key!r} has shape {arr.shape}, expected {shape}")
            continue
        bad = int(np.count_nonzero(~np.isfinite(arr)))
        if bad:
            problems.append(f"{key!r} has {bad} entries not finite")
            continue
        copies[key] = _frozen(arr.astype(np.float64, copy=True))
    if problems:
        raise RunError(f"option {option!r}: the model's return is refused: " + "; ".join(problems))
    return {s: copies[s] for s in case.streams}, {r: copies[r] for r in case.intermediate_results}


# ---------------------------------------------------------------- draws and conversions


class _Draws:
    """Each input's draws: drawn (or held), the rate inputs checked, then converted (settled choices 2.4 to 6)."""

    def __init__(
        self,
        case: Case,
        seen: Sequence[str],
        rows: Mapping[str, tuple[str, ...]],
        u: Mapping[str, Floats],
        stated: Mapping[str, object],
        n: int,
    ) -> None:
        self.case = case
        self.raw: dict[str, Unconverted] = {}
        self.draws: dict[str, NDArray[Any]] = {}
        self.picks: dict[str, NDArray[np.int64]] = {}
        self.applied: dict[str, Conversion] = {}
        mixtures = [x for x in seen if case.inputs[x].get("distribution") == "mixture"]
        plain = [x for x in seen if x not in mixtures]
        for name in plain:
            spec = case.inputs[name]
            if name in stated:
                self.raw[name] = Unconverted(_held_array(spec, stated[name], n, rows.get(name)))
            else:
                self.raw[name] = Unconverted(self.plain(name, spec, u[name], rows.get(name)))
        for name in plain:
            if _is_rate(case.inputs[name]):
                count = int(np.count_nonzero(~(self.raw[name].own_units() > 0.0)))
                if count:
                    raise RunError(f"rate input {name!r}: {count} of {n} draws at or below zero")
        for name in plain:
            self.draws[name] = self.convert(name, self.raw[name])
        for name in mixtures:
            if name in stated:
                self.draws[name] = np.full(n, float(cast(float, stated[name])))
                self.raw[name] = Unconverted(self.draws[name])  # a held mixture is never converted
            else:
                at = np.arange(n)
                raw, self.draws[name], self.picks[name] = self.mixture(f"input {name!r}", case.inputs[name], u[name], at)
                self.raw[name] = Unconverted(raw)
        self.draws = {x: self.draws[x] for x in seen}
        self.raw = {x: self.raw[x] for x in seen}

    def plain(self, name: str, spec: Mapping[str, object], u: Floats, rows: tuple[str, ...] | None) -> NDArray[Any]:
        where = f"input {name!r}"
        if rows is None:
            return _drawn(where, spec, u)
        keys = self.case.row_parameters.get(name, ())
        columns: list[NDArray[Any]] = []
        for j, row in enumerate(rows):
            row_spec = {**spec, **{k: cast(Sequence[object], spec[k])[j] for k in keys}}
            columns.append(_drawn(f"{where}, row {row!r}", row_spec, u[:, j]))
        return np.column_stack(columns)

    def convert(self, name: str, unconverted: Unconverted, at: NDArray[np.intp] | None = None) -> NDArray[Any]:
        """The case's money: the input's own-unit draws times the price factor and, with a rate input, times its draws at
        the draws `at` (all when None). The typed way from `Unconverted` to the case's money; `own_units()` is the untyped one."""
        values = unconverted.own_units()
        conversion = self.case.conversions.get(name)
        if conversion is None:
            return values
        self.applied[name] = conversion
        out = values * conversion.price_factor
        if conversion.rate_input is not None:
            rate_draws = self.raw.get(conversion.rate_input)
            if rate_draws is None:
                raise RunError(f"input {name!r}: its rate input {conversion.rate_input!r} is not an input the model sees")
            rate = rate_draws.own_units() if at is None else rate_draws.own_units()[at]
            out = out * (rate[:, None] if out.ndim == 2 else rate)
        return out

    def mixture(
        self, where: str, spec: Mapping[str, object], u: Floats, at: NDArray[np.intp]
    ) -> tuple[Floats, Floats, NDArray[np.int64]]:
        """Each draw's picked component drawn at the rescaled uniform by its own spec and converted by its own
        money, a rate's draws taken at the same draws (`at`, their positions among all n); returns the raw
        draws, the converted draws and the top-level picks."""
        try:
            j, rescaled = distributions.pick(spec, u)
        except ValueError as e:
            raise RunError(f"{where}: {e}") from e
        raw = np.empty_like(u)
        converted = np.empty_like(u)
        for i, part in enumerate(cast(Sequence[Mapping[str, object]], spec["components"])):
            picked = j == i
            component = str(part["input"])
            label = f"{where}, component {component!r}"
            if part.get("distribution") == "mixture":
                r, c, _ = self.mixture(label, part, rescaled[picked], at[picked])
            else:
                r = _drawn(label, part, rescaled[picked])
                c = self.convert(component, Unconverted(r), at[picked])
            raw[picked] = r
            converted[picked] = c
        return raw, converted, j


def _drawn(where: str, spec: Mapping[str, object], u: Floats) -> NDArray[Any]:
    try:
        if spec.get("distribution") == "categorical":
            return distributions.choose(spec, u)
        return distributions.quantile(spec, u)
    except ValueError as e:
        raise RunError(f"{where}: {e}") from e


def _held_array(spec: Mapping[str, object], value: object, n: int, rows: tuple[str, ...] | None) -> NDArray[Any]:
    categorical = spec.get("distribution") == "categorical"

    def one(v: object) -> object:
        return str(v) if categorical else float(cast(float, v))

    if rows is None:
        return np.full(n, one(value))
    per_row = cast(Mapping[str, object], value) if isinstance(value, Mapping) else {r: value for r in rows}
    return np.tile(np.array([one(per_row[r]) for r in rows]), (n, 1))


# ---------------------------------------------------------------- present values and the identity


def _pv(label: str, stream: Floats, factors: Floats) -> Floats:
    try:
        return timeline.present_value(stream, factors)
    except ValueError as e:
        raise RunError(f"discount schedule {label!r}: {e}") from e


def _identity(
    label: str,
    option: str,
    base: str,
    streams: Mapping[str, Mapping[str, Floats]],
    kinds: Mapping[str, str],
    factors: Floats,
    net: Floats,
) -> None:
    """Settled choice 9: the net present value again, from the net flow summed year by year before discounting,
    within 1e-9 times max(G, 1), G the draw's gross present value."""
    sign = {"benefit": 1.0, "cost": -1.0}
    flow = np.zeros((net.shape[0], factors.shape[0]))
    gross = np.zeros(net.shape[0])
    for o, direction in ((option, 1.0), (base, -1.0)):
        for s, k in kinds.items():
            flow = flow + direction * sign[k] * streams[o][s]
            gross = gross + _pv(label, np.abs(streams[o][s]), factors)
    again = _pv(label, flow, factors)
    bad = int(np.count_nonzero(~(np.abs(again - net) <= IDENTITY_TOLERANCE * np.maximum(gross, 1.0))))
    if bad:
        raise RunError(
            f"discount schedule {label!r}, option {option!r}: the net present value fails the accounting identity on "
            f"{bad} draws, a fault in the run's own code"
        )


def stream_increments(r: Run, label: str, option: str, base: str) -> dict[str, Floats]:
    """For each stream of `r.stream_status`, its present value at discount schedule `label` in `option` less that in
    `base`, one value per draw. `base` may be any option of the run, not only the base case. Raises RunError naming
    the label, option or base that `r.present_values` lacks."""
    by_option = r.present_values.get(label)
    if by_option is None:
        raise RunError(f"the run has no discount schedule {label!r}")
    for role, name in (("option", option), ("base", base)):
        if name not in by_option:
            raise RunError(f"discount schedule {label!r}: the run has no {role} {name!r}")
    return {s: by_option[option][s] - by_option[base][s] for s in r.stream_status}
