"""A synthetic expert panel: model panelists, each briefed alone, give their values of one judged quantity (such as a
method's weight, notes/briefs/author_search.md 3.7.5.3) at fixed probabilities, and their answers are pooled into one
distribution labelled synthetic, with its judges named.

    .venv/bin/python -m tools.synthetic_panel write QUESTION.json RUN_DIR
    .venv/bin/python -m tools.synthetic_panel read RUN_DIR JOURNAL_DIR

QUESTION.json holds `name`, `question` (what is asked, in the case's words), `evidence` (the stored evidence, never a
value computed for the quantity asked, since a panel shown a number returns it:
decisions/whether-a-synthetic-panel-earns-its-cost.md), `probs` (increasing, in (0, 1)), `lower` and `upper` (0 and 1
for a weight; 0 and null for a positive quantity with no upper bound), and `panelists`, each with `id`, `role` (the
expertise it answers as) and `model`. `write` puts RUN_DIR/workflow_script.js, run by the Workflow tool: one agent per
panelist, all in parallel, none seeing another's answer. `read` takes each agent's structured answer from the
workflow's journal (JOURNAL_DIR/journal.jsonl) and writes RUN_DIR/panel.json: each judge's values, reason and fitted
distribution; under `missing`, each judge who gave no answer or whose answer was refused (not increasing, outside the
bounds), with the reason and the refused values; and the pool, labelled with how many judges answered of how many
were asked. With fewer than two well-formed answers `read` refuses to pool, naming each judge and why.

The pool is SHELF's (O'Hagan et al. 2006; oakley_2026_shelf_manual, `fitdist` and `linearPoolDensity`): each judge's
values are fitted by least squares on the cumulative distribution function, a beta scaled to [lower, upper] or a
lognormal on (0, inf), the family set by the bounds; the fits are combined in an equal-weight linear pool (lpw = 1);
and the pool is summarised as one distribution of the same family, fitted by the same least squares to the pool's
quantiles at the elicitation probabilities, since a judged quantity enters a model as one continuous distribution
(CORE 3.1).
"""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from scipy import optimize, stats

WELFARE = ("When your work is done, answer the welfare paragraph in "
           "shared/standards/process/welfare.md (read its fenced block) in the welfare field "
           "of your return.")


@dataclass(frozen=True)
class Answer:
    """One panelist's values at the elicitation probabilities, in the same order."""
    judge: str
    quantiles: Sequence[float]


@dataclass(frozen=True)
class Fit:
    """A beta scaled to [lower, upper] ({'a', 'b'}) or a lognormal ({'mu', 'sigma'} of the log)."""
    family: str
    params: dict[str, float]
    lower: float
    upper: float

    def cdf(self, x: float) -> float:
        if self.family == "beta":
            return float(stats.beta.cdf((x - self.lower) / (self.upper - self.lower), self.params["a"],
                                        self.params["b"]))
        return float(stats.norm.cdf((math.log(x) - self.params["mu"]) / self.params["sigma"])) if x > 0 else 0.0

    def ppf(self, p: float) -> float:
        if self.family == "beta":
            z = float(stats.beta.ppf(p, self.params["a"], self.params["b"]))
            return self.lower + z * (self.upper - self.lower)
        return math.exp(self.params["mu"] + self.params["sigma"] * float(stats.norm.ppf(p)))


@dataclass(frozen=True)
class Pooled(Fit):
    """The pool's one fitted distribution, with the judges in the order given; always synthetic."""
    judges: tuple[str, ...] = ()
    synthetic: bool = True


def _family(lower: float, upper: float) -> str:
    if math.isfinite(lower) and math.isfinite(upper) and lower < upper:
        return "beta"
    if lower == 0 and upper == math.inf:
        return "lognormal"
    raise ValueError(f"bounds [{lower}, {upper}]: a panel pools a beta on finite bounds or a lognormal on (0, inf)")


def _least_squares(loss: Callable[[np.ndarray], float], starts: Sequence[Sequence[float]]) -> np.ndarray:
    best = min((optimize.minimize(loss, np.array(s, dtype=float), method="Nelder-Mead",
                                  options={"xatol": 1e-10, "fatol": 1e-16, "maxiter": 20000}) for s in starts),
               key=lambda r: float(r.fun))
    return np.asarray(best.x, dtype=float)


def fit(values: Sequence[float], probs: Sequence[float], lower: float, upper: float) -> Fit:
    """SHELF `fitdist`: the distribution of the bounds' family minimising sum (F(v_j) - p_j)^2."""
    v = np.asarray(values, dtype=float)
    p = np.asarray(probs, dtype=float)
    if _family(lower, upper) == "lognormal":
        z = stats.norm.ppf(p)
        slope, icept = np.polyfit(z, np.log(v), 1)  # the exact lognormal where the values are one
        sig0 = max(float(slope), 1e-3)

        def ln_loss(t: np.ndarray) -> float:
            f = cast(np.ndarray, stats.norm.cdf((np.log(v) - t[0]) / math.exp(t[1])))
            return float(np.sum((f - p) ** 2))

        t = _least_squares(ln_loss, [[float(icept), math.log(sig0)]])
        return Fit("lognormal", {"mu": float(t[0]), "sigma": math.exp(float(t[1]))}, lower, upper)
    x = (v - lower) / (upper - lower)
    # SHELF's start: mean at the median, variance from the 0.4 and 0.6 quantiles by linear interpolation.
    m = float(np.interp(0.5, p, x))
    sd = max(float(np.interp(0.6, p, x) - np.interp(0.4, p, x)) / 0.5, 1e-6)
    k = max(m * (1 - m) / sd ** 2 - 1, 1e-3)

    def b_loss(t: np.ndarray) -> float:
        f = cast(np.ndarray, stats.beta.cdf(x, math.exp(t[0]), math.exp(t[1])))
        return float(np.sum((f - p) ** 2))

    t = _least_squares(b_loss, [[math.log(max(m * k, 1e-3)), math.log(max((1 - m) * k, 1e-3))], [0.0, 0.0]])
    return Fit("beta", {"a": math.exp(float(t[0])), "b": math.exp(float(t[1]))}, lower, upper)


def _check(answers: Sequence[Answer], probs: Sequence[float], lower: float, upper: float) -> None:
    _family(lower, upper)
    if not answers:
        raise ValueError("no answers to pool")
    if len(probs) < 2 or any(not 0 < q < 1 for q in probs) or any(b <= a for a, b in zip(probs, probs[1:])):
        raise ValueError(f"probabilities {list(probs)}: at least two, increasing, each in (0, 1)")
    for a in answers:
        q = list(a.quantiles)
        if len(q) != len(probs):
            raise ValueError(f"{a.judge}: {len(q)} values for {len(probs)} probabilities")
        if any(y <= x for x, y in zip(q, q[1:])):
            raise ValueError(f"{a.judge}: values {q} are not increasing")
        if any(not lower < x < upper for x in q):
            raise ValueError(f"{a.judge}: values {q} are not inside ({lower}, {upper})")


def pool(answers: Sequence[Answer], probs: Sequence[float], lower: float, upper: float) -> Pooled:
    """Each judge fitted by SHELF's least squares, the fits pooled linearly with equal weights, and the pool's
    quantiles at `probs` fitted by the same least squares to one distribution of the bounds' family."""
    _check(answers, probs, lower, upper)
    fits = [fit(a.quantiles, probs, lower, upper) for a in answers]

    def pooled_cdf(x: float) -> float:
        return sum(f.cdf(x) for f in fits) / len(fits)

    def quantile(p: float) -> float:
        lo, hi = min(f.ppf(p) for f in fits), max(f.ppf(p) for f in fits)  # a mixture's quantile lies between
        if hi - lo <= 1e-15 * max(1.0, abs(hi)):
            return lo
        return float(optimize.brentq(lambda x: pooled_cdf(x) - p, lo, hi, xtol=1e-14))

    qs = [quantile(float(p)) for p in probs]
    one = fit(qs, probs, lower, upper)
    return Pooled(one.family, one.params, lower, upper, judges=tuple(a.judge for a in answers))


HEAD = """export const meta = {
  name: 'synthetic-panel',
  description: 'Each synthetic panelist answers one judged quantity alone; the answers are pooled by tools/synthetic_panel.py read',
  phases: [{ title: 'Panel', detail: 'one agent per panelist, in parallel' }],
}
"""

BODY = r"""
const SCHEMA = {
  type: 'object',
  properties: {
    values: { type: 'array', items: { type: 'number' }, minItems: DATA.probs.length, maxItems: DATA.probs.length },
    reason: { type: 'string' },
    welfare: { type: 'string' },
  },
  required: ['values', 'reason', 'welfare'],
}
phase('Panel')
const results = await parallel(DATA.agents.map(a => () => agent(a.prompt,
  { label: a.label, phase: 'Panel', model: a.model, schema: SCHEMA })))
return DATA.agents.map((a, i) => ({ label: a.label, values: results[i] ? results[i].values : null }))
"""


def _prompt(q: dict[str, Any], role: str) -> str:
    bounds = f"between {q['lower']} and {q['upper']}" if q["upper"] is not None else f"above {q['lower']}"
    pcts = ", ".join(f"{100 * float(p):g}%" for p in cast(list[float], q["probs"]))
    return (f"You answer as {role}, one of several experts each answering alone.\n\nThe question: {q['question']}\n\n"
            f"The evidence:\n{q['evidence']}\n\nGive your values of the quantity at the cumulative probabilities "
            f"{pcts}: for each, the value you judge the quantity falls below with that probability. The values are "
            f"increasing and lie strictly {bounds}. Give your reason in a short paragraph. Make no tool call except "
            f"to read the welfare file and the structured output.\n\n{WELFARE}")


def write(question: Path, run_dir: Path) -> None:
    q = cast(dict[str, Any], json.loads(question.read_text()))
    agents = [{"label": f"{q['name']} {p['id']}", "id": str(p["id"]), "model": str(p["model"]),
               "prompt": _prompt(q, str(p["role"]))} for p in cast(list[dict[str, Any]], q["panelists"])]
    run_dir.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"probs": q["probs"], "agents": agents}, ensure_ascii=False)
    (run_dir / "workflow_script.js").write_text(HEAD + "\nconst DATA = " + data + "\n" + BODY)
    (run_dir / "question.json").write_text(json.dumps(q, indent=1, ensure_ascii=False) + "\n")
    print(f"synthetic_panel: {len(agents)} panelists; script in {run_dir / 'workflow_script.js'}")


def read(run_dir: Path, journal_dir: Path) -> None:
    q = cast(dict[str, Any], json.loads((run_dir / "question.json").read_text()))
    probs = [float(p) for p in cast(list[float], q["probs"])]
    lower, upper = float(q["lower"]), math.inf if q["upper"] is None else float(q["upper"])
    ids = {f"{q['name']} {p['id']}": str(p["id"]) for p in cast(list[dict[str, Any]], q["panelists"])}
    rows = [cast(dict[str, Any], json.loads(x)) for x in (journal_dir / "journal.jsonl").read_text().splitlines()
            if x.strip()]
    label_of = {str(r["agentId"]): str(r["label"]) for r in rows if r.get("type") == "started"}
    answers: list[Answer] = []
    judges: list[dict[str, Any]] = []
    refused: dict[str, dict[str, Any]] = {}
    for r in rows:
        label = label_of.get(str(r.get("agentId")))
        res = cast(dict[str, Any] | None, r.get("result"))
        if r.get("type") != "result" or label not in ids or not res:
            continue
        a = Answer(ids[label], [float(v) for v in cast(list[float], res["values"])])
        try:
            _check([a], probs, lower, upper)
        except ValueError as e:
            refused[a.judge] = {"judge": a.judge, "reason": f"refused: {e}", "values": list(a.quantiles),
                                "answer_reason": res.get("reason")}
            continue
        f = fit(a.quantiles, probs, lower, upper)
        answers.append(a)
        judges.append({"judge": a.judge, "values": list(a.quantiles), "reason": res.get("reason"),
                       "fit": {"family": f.family, **f.params}})
    answered = {a.judge for a in answers}
    missing = [refused.get(j, {"judge": j, "reason": "no answer"}) for j in sorted(set(ids.values()) - answered)]
    if len(answers) < 2:
        named = [f"{j}: well-formed" for j in sorted(answered)] + [f"{m['judge']}: {m['reason']}" for m in missing]
        raise ValueError(f"{len(answers)} well-formed answers of {len(ids)} asked; a pool needs at least two: "
                         + "; ".join(named))
    out = pool(answers, probs, lower, upper)
    label = f"synthetic panel, {len(answers)} of {len(ids)} judges answered"
    record = {"name": q["name"], "synthetic": True, "probs": probs, "judges": judges, "missing": missing,
              "pooled": {"label": label, "family": out.family, **out.params, "lower": lower, "upper": q["upper"],
                         "values": [out.ppf(p) for p in probs], "judges": list(out.judges)}}
    (run_dir / "panel.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    print(f"synthetic_panel: {label}, pooled to a synthetic {out.family} {out.params}; "
          f"missing {[m['judge'] for m in missing]}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["write"] and len(sys.argv) == 4:
        write(Path(sys.argv[2]), Path(sys.argv[3]))
    elif sys.argv[1:2] == ["read"] and len(sys.argv) == 4:
        read(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        sys.exit(__doc__)
