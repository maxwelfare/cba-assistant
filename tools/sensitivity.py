"""tools/sensitivity.py: each input's tornado ends, from a table of draws (cost_benefit_engine/draws_table.py).

    .venv/bin/python tools/sensitivity.py TABLE OUT.json --output NAME [--minus NAME]

Y is the output NAME, less the output given by --minus. For each input it estimates the main effect E[Y | input = x],
every other input drawn as it was, at x the input's 5th and 95th percentiles, by `value_of_information.end`: a local
linear fit over the draws within 2.5 percentiles in rank on either side, with its HC0 standard error. That is the one-way
bar holding the other inputs at their means only where, for each x, Y is multilinear in the other inputs and they are
independent; the main effect needs no such condition. An input taking exactly two values in its column has as its ends
Y's mean at each value, with that mean's standard error, so a rare state is never hidden; a value held by fewer
than 3 draws is refused, as `end` refuses so small a window.

The tornado ranks the columns the table holds: an input its producer did not write has no bar, and nothing here can
tell that it is missing.

The ranking is the sheet's (the shared tools/sheets/script.py's Sensitivity tab, the owner's old Correlation tab), so the sheet and
the appendix rank alike: each input's key is the larger of |r|, the Pearson correlation of input and Y, and |rank r|, the
Spearman correlation (average ranks on ties); the noise line is 4/sqrt(draws), and an input is above it when its key is
at least the line, as the sheet shows a key. The chance that some input unconnected to Y passes the line by luck
depends on the number of inputs and on Y's tails, which widen the spread of Pearson's r: a shuffled-output test put it at
7.4% to 10.7% on one case's fat-tailed outputs (223 inputs, 1,000 draws) and 1.6% to 3.1% on another's. Pearson is
kept beside Spearman because it alone finds an input that acts through the tail. A constant input, or a constant Y, has
no correlation: its r and rank r are null and its key 0.

OUT holds draws, seed, sampling, output, minus (null where not given), mean (Y's mean), inputs_read (the count of input
columns), noise_line, above_line (the count of inputs above it) and inputs, one entry per input with name, r, rank_r,
key, above_line, x_low, x_high, at_low, at_high, se_low, se_high, span (the greatest less the least of mean, at_low and
at_high) and two_valued, in order of key, largest first, ties by name. It prints the draw count, the noise line, and the
inputs above it (at most ten) with r, rank r and their ends, each number to two significant figures and each pair of
ends at the figures that tell it apart, then the largest standard error of those inputs' ends as a share of their
largest span. A refusal exits 1 and writes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # this tree's engine, whatever the venv points at

from cost_benefit_engine.documents import percent, separating_figures, significant  # noqa: E402
from cost_benefit_engine.draws_table import Floats, read_table  # noqa: E402
from cost_benefit_engine.value_of_information import end  # noqa: E402

LOW, HIGH, TOP = 0.05, 0.95, 10


def _mean_and_se(y: Floats, name: str, value: float) -> tuple[float, float]:
    if y.size < 3:  # the rule `end` applies to its window (brief 2.3.3)
        raise ValueError(f"input {name!r} takes the value {value:g} in {y.size} draws; an end needs at least 3")
    return float(y.mean()), float(y.std(ddof=1) / np.sqrt(y.size))


def correlations(y: Floats, xs: Floats) -> Floats:
    """The Pearson correlation of y with each column of xs; NaN where y or the column is constant."""
    xc, yc = xs - xs.mean(axis=0), y - y.mean()
    scale = np.sqrt((xc**2).sum(axis=0) * (yc**2).sum())
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(scale > 0, (xc.T @ yc) / scale, np.nan)


def entry(name: str, y: Floats, key: Floats, mean: float) -> dict[str, Any]:
    """One input's ends and span."""
    values = np.unique(key)
    two_valued = values.size == 2
    if two_valued:
        x_low, x_high = float(values[0]), float(values[1])
        at_low, se_low = _mean_and_se(y[key == values[0]], name, x_low)
        at_high, se_high = _mean_and_se(y[key == values[1]], name, x_high)
    else:
        x_low, at_low, se_low = end(y, key, LOW)
        x_high, at_high, se_high = end(y, key, HIGH)
    trio = (mean, at_low, at_high)
    return {
        "name": name, "x_low": x_low, "x_high": x_high, "at_low": at_low, "at_high": at_high,
        "se_low": se_low, "se_high": se_high, "span": max(trio) - min(trio), "two_valued": two_valued,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    parser.add_argument("table")
    parser.add_argument("out")
    parser.add_argument("--output", required=True)
    parser.add_argument("--minus")
    args = parser.parse_args(argv)
    try:
        t = read_table(args.table)
        names = sorted(t.outputs)
        for given in (args.output, args.minus):
            if given is not None and given not in t.outputs:
                raise ValueError(f"no output {given!r}; the table's outputs are: {', '.join(names)}")
        if args.minus == args.output:
            raise ValueError(f"--minus {args.minus!r} is the --output itself")
        y = t.outputs[args.output] - (t.outputs[args.minus] if args.minus is not None else 0.0)
        mean = float(y.mean())
        names_in = list(t.inputs)
        xs = np.column_stack([t.inputs[k] for k in names_in]) if names_in else np.empty((y.size, 0))
        r = correlations(y, xs)
        rank_r = correlations(rankdata(y), rankdata(xs, axis=0))
        line = 4 / float(np.sqrt(t.iterations))
        entries: list[dict[str, Any]] = []
        for j, n in enumerate(names_in):
            defined = bool(np.isfinite(r[j]) and np.isfinite(rank_r[j]))
            key = max(abs(float(r[j])), abs(float(rank_r[j]))) if defined else 0.0
            entries.append({
                "name": n, "r": float(r[j]) if defined else None, "rank_r": float(rank_r[j]) if defined else None,
                "key": key, "above_line": key >= line, **entry(n, y, t.inputs[n], mean),
            })
        entries.sort(key=lambda e: (-e["key"], e["name"]))
    except (ValueError, OSError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    above = [e for e in entries if e["above_line"]]
    result = {
        "draws": t.iterations, "seed": t.random_seed, "sampling": t.sampling_method,
        "output": args.output, "minus": args.minus, "mean": mean, "inputs_read": len(t.inputs),
        "noise_line": line, "above_line": len(above), "inputs": entries,
    }
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    y_name = args.output + (f" - {args.minus}" if args.minus is not None else "")
    print(f"{t.iterations:,} draws; Y = {y_name}, mean {significant(mean)}; {len(t.inputs)} inputs")
    print(f"noise line 4/sqrt(n) = {significant(line)}; {len(above)} inputs above it"
          + (f", the first {TOP} by the larger of |r| and |rank r|:" if len(above) > TOP else ""))
    for e in above[:TOP]:
        flag = " (two values)" if e["two_valued"] else ""
        at, x = separating_figures((e["at_low"], e["at_high"])), separating_figures((e["x_low"], e["x_high"]))
        print(f"  r {significant(e['r'])}, rank r {significant(e['rank_r'])}  {e['name']}{flag}:"
              f" {significant(e['at_low'], at)} at {significant(e['x_low'], x)},"
              f" {significant(e['at_high'], at)} at {significant(e['x_high'], x)}")
    shown = above[:TOP]
    widest = max((e["span"] for e in shown), default=0.0)
    if widest > 0:
        worst = max(max(e["se_low"], e["se_high"]) for e in shown)
        print(f"largest standard error of these ends: {percent(worst / widest)} of the largest span")
    return 0


if __name__ == "__main__":
    sys.exit(main())
