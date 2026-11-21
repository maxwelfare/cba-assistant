"""tools/figures.py: the scientific figures of a case, drawn from the numbers its tools write.

    .venv/bin/python tools/figures.py tornado SENSITIVITY.json OUT [--labels LABELS.json] [--top N] [--xlabel TEXT]
        [--scale X] [--audience KEY]

`tornado` draws the JSON that tools/sensitivity.py writes: one horizontal bar per input above its noise line, for at
most the `top` inputs of largest key (the larger of |r| and |rank r|), drawn in order of span, the longest at the top.
Where no input passes the line it draws no bars and says so in the figure, so a paper's build goes on. Each bar runs
from Y's mean to the input's low end in the cycle's first color and to its high end in the second, the shorter drawn
over the longer; each end carries a whisker of +-1.96 standard errors. LABELS is a JSON object from input name to label; an unlabeled input shows its name. Values are divided by
`scale`. OUT's suffix sets the format (.svg, .pdf, .png).

`seats_flowchart` draws the seats of a case in the order of notes/fast_estimate.md 1.3, one box per numbered item
that runs a seat, each labelled with its item number and the agent types it dispatches (SEATS below). The function
reads 1.3 each time and refuses to draw when the two disagree: an item SEATS lacks or has that 1.3 no longer runs, or an
agent type 1.3 names in backticks that its box does not carry. `only` draws a subset; `case` draws the stages that ran,
those the case's seats record `<case>/results/seats.json` lists (written by tools/seats_record.py).

    .venv/bin/python tools/figures.py seats OUT [--only 1.3.1 1.3.2 ... | --case CASE_DIR]

Every figure is drawn within `matplotlib.style.context` of tools/house.mplstyle, which sets the whole look; no code
here sets a color, font, size of type or margin, and the caller's settings are untouched. A tornado drawn for an
audience edition, `audience=KEY` (`--audience KEY`), has the rc of the profile `audiences/<key>.toml` `[design.charts]`
laid over the house style (notes/audience_layer.md 3.4): each key but `basis` and `evidence` a matplotlib rc name, its
value in style-file syntax or a TOML number or boolean. A key that is not an rc name, or a value its validator
refuses, raises ValueError naming it before anything is drawn.
"""

# matplotlib's stubs leave **kwargs untyped, so each plotting method is "partially unknown" under strict mode.
# pyright: reportUnknownMemberType=false

from __future__ import annotations

import argparse
import json
import re
import textwrap
import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

import matplotlib
import matplotlib.style
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
AUDIENCES = ROOT / "audiences"
SEAT_ORDER = ROOT / "notes" / "fast_estimate.md"
STYLE = Path(__file__).resolve().with_name("house.mplstyle")
WRAP = 40
LOW_LABEL = "input at its low end (5th percentile, or the lower of two values)"
HIGH_LABEL = "input at its high end (95th percentile, or the higher of two values)"
ERROR_LABEL = "Monte Carlo error of the end (±1.96 standard errors)"


def chart_rc(charts: dict[str, Any]) -> dict[str, Any]:
    """The rc overlay of a profile's `[design.charts]` table, each value validated as matplotlib validates a style
    file's. Raises ValueError naming every key that is not an rc name and every value its validator refuses."""
    rc = cast("dict[str, Any]", matplotlib.RcParams())  # an RcParams validates each value as it is set
    faults: list[str] = []
    for key, value in charts.items():
        if key in ("basis", "evidence"):
            continue
        try:
            rc[key] = value
        except KeyError:
            faults.append(f"design.charts.{key}: not a matplotlib rc name")
        except ValueError as refusal:
            faults.append(f"design.charts.{key} = {value!r}: {refusal}")
            continue
        if key == "axes.prop_cycle" and len(rc[key].by_key().get("color", [])) < 2:
            faults.append(f"design.charts.{key}: needs a color key with at least two colors")
    if faults:
        raise ValueError("; ".join(faults))
    return dict(rc)


def style(audience: str | None) -> list[str | dict[str, Any]]:
    """The house style, with the chart rc of the profile `audiences/<audience>.toml` over it where one is named."""
    if audience is None:
        return [str(STYLE)]
    profile = AUDIENCES / f"{audience}.toml"
    if not profile.exists():
        raise ValueError(f"no audience profile {profile}")
    design: dict[str, Any] = tomllib.loads(profile.read_text()).get("design", {})
    try:
        return [str(STYLE), chart_rc(design.get("charts", {}))]
    except ValueError as refusal:
        raise ValueError(f"{profile}: {refusal}") from None


def tornado(
    numbers: dict[str, Any],
    path: Path | str,
    *,
    labels: dict[str, str] | None = None,
    top: int = 15,
    xlabel: str = "",
    scale: float = 1.0,
    audience: str | None = None,
) -> Figure:
    """The tornado of `numbers` (sensitivity.py's OUT, as json.load returns it), saved to `path`, in the house style
    with the chart rc of the profile `audience` over it where one is named."""
    if top < 1:
        raise ValueError(f"top must be at least 1, got {top}")
    if not scale > 0:
        raise ValueError(f"scale must be positive, got {scale}")
    names = labels or {}
    chosen: list[dict[str, Any]] = [e for e in numbers["inputs"] if e["above_line"]][:top]
    entries = sorted(chosen, key=lambda e: (-e["span"], e["name"]))  # chosen by key, drawn by span
    n = len(entries)
    mean = numbers["mean"] / scale
    ticks: list[str] = []
    for e in entries:
        name: str = e["name"]
        ticks.append(textwrap.fill(names.get(name, name) + (" (two values)" if e["two_valued"] else ""), WRAP))
    rows = np.arange(n, 0, -1, dtype=np.float64) - 1  # the longest span at the top
    with matplotlib.style.context(style(audience)):
        rc = matplotlib.rcParams
        low_color, high_color = rc["axes.prop_cycle"].by_key()["color"][:2]
        ink = rc["text.color"]
        line_in = float(rc["font.size"]) * 1.5 / 72  # one line of type, in inches
        lines = sum(t.count("\n") + 1 for t in ticks)
        fig = Figure(figsize=(rc["figure.figsize"][0], line_in * (lines + 0.8 * n + 8)))
        ax = fig.add_subplot()
        ax.yaxis.grid(False)  # the grid on the value axis only
        if not entries:
            ax.set_axis_off()
            ax.text(0.5, 0.5, textwrap.fill(
                f"No input of the {numbers['inputs_read']} in the table passes the noise line,"
                f" 4/sqrt(n), at {numbers['draws']:,} draws.", WRAP * 2),
                ha="center", va="center", transform=ax.transAxes)
            fig.savefig(path)
            return fig
        for row, e in zip(rows, entries):
            sides = [(e["at_low"] / scale, low_color), (e["at_high"] / scale, high_color)]
            sides.sort(key=lambda s: -abs(s[0] - mean))  # the longer first, so the shorter is drawn over it
            for at, color in sides:
                ax.barh(row, at - mean, left=mean, color=color)
        at = np.array([[e["at_low"], e["at_high"]] for e in entries]) / scale
        se = np.array([[e["se_low"], e["se_high"]] for e in entries]) / scale
        ax.errorbar(at.ravel(), np.repeat(rows, 2), xerr=1.96 * se.ravel(), fmt="none", ecolor=ink, elinewidth=0.8)
        ax.axvline(mean, color=ink, linewidth=0.8)
        left, right = ax.get_xlim()
        if left <= 0 <= right:
            ax.axvline(0, color=ink, linewidth=0.8, linestyle=":")
        ax.set_xlim(left, right)
        ax.set_yticks(rows, ticks)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel(xlabel)
        handles = [
            Patch(facecolor=low_color, label=LOW_LABEL),
            Patch(facecolor=high_color, label=HIGH_LABEL),
            Line2D([], [], color=ink, linewidth=0.8, label=ERROR_LABEL),
        ]
        fig.legend(
            handles=handles, loc="outside lower center", ncols=1,
            title=f"The {n} inputs most correlated with the result, of the {numbers['inputs_read']} in the table;"
            f" {numbers['above_line']} pass the noise line",
        )
        fig.savefig(path)
    return fig


# Each item of notes/fast_estimate.md 1.3 that runs a seat: its number, what it does in a few words, and the agent
# types it dispatches, as the files in .claude/agents/ and the shared agents/ name them. seats_flowchart checks this
# against 1.3 at every call.
SEATS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("1.3.1", "the fast draft, from the requirements conversation's lists and estimates",
     ("case-author", "effects-lister", "fermi-estimator")),
    ("1.3.2", "three reviewers comment, each blind to the others",
     ("referee", "audit-referee", "documents-referee")),
    ("1.3.3", "one decision letter, naming the effects that get a model", ("editor",)),
    ("1.3.4", "the same author models those effects and revises to milestone 1", ("case-author",)),
    ("1.3.4.1", "before any model, each decision of method that can move the result, one referee each",
     ("case-author", "referee")),
    ("1.3.4.2", "the author answers them, builds the models and drafts an outline", ("case-author",)),
    ("1.3.4.3", "the purpose check of results and outline; the author fixes and writes the appendix",
     ("referee", "case-author")),
    ("1.3.5", "milestone 1's own round: the economics and audit referees on the appendix, its results placeholders",
     ("referee", "audit-referee")),
    ("1.3.6", "the editor rules on milestone 1; the author fixes and the editor checks", ("editor", "case-author")),
    ("1.3.7", "milestone 2: results filled, paper and summary; the documents referee reruns and checks; a ruling",
     ("case-author", "worked-example", "documents-referee", "editor", "facts-researcher")),
    ("1.3.8", "where the user asks: peer review packages for human peer reviewers", ("case-author",)),
    ("1.3.9", "the layout review of the built documents", ("pdf-layout",)),
    ("1.3.10", "where the requirements name a reader: an audience edition, reviewed and laid out",
     ("audience-translator", "pdf-layout")),
)
ITEM = re.compile(r"^(1\.3\.\d+(?:\.\d+)?) (.*)$", re.MULTILINE)


def check_seats(source: Path) -> None:
    """Refuse when SEATS and 1.3 of `source` disagree on the items or on the agent types an item names."""
    items = dict(ITEM.findall(source.read_text()))
    known = {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")} | {a for _, _, ags in SEATS for a in ags}
    for shared in (ROOT.parent / "shared" / "agents", ROOT / "shared" / "agents"):
        known |= {p.stem for p in shared.glob("*.md")}
    listed = {n: set(ags) for n, _, ags in SEATS}
    faults = [f"{n}: in {source.name} 1.3 but not in SEATS" for n in items if n not in listed]
    faults += [f"{n}: in SEATS but not a seat of {source.name} 1.3" for n in listed if n not in items]
    for n, text in items.items():
        named = set(re.findall(r"`([\w-]+)`", text)) & known
        faults += [f"{n}: 1.3 names `{a}`, its box does not" for a in sorted(named - listed.get(n, set()))]
    order = [n for n in items if n in listed]
    seats = [n for n, _, _ in SEATS if n in items]
    for a, b in zip(seats, order):
        if a != b:
            faults.append(f"{a}: SEATS lists it where {source.name} 1.3 has {b}")
            break
    if faults:
        raise ValueError("SEATS in tools/figures.py no longer mirrors 1.3:\n" + "\n".join(faults))


def seats_flowchart(
    path: Path | str, *, only: Iterable[str] | None = None, source: Path | str = SEAT_ORDER,
    case: Path | str | None = None,
) -> Figure:
    """The seats of 1.3 in order, one box each, saved to `path`; `only` keeps the items it names, and `case` the stages
    its seats record lists (those that ran). Naming both is refused."""
    check_seats(Path(source))
    if case is not None:
        if only is not None:
            raise ValueError("name the stages by only or by case, not both")
        record: Any = json.loads((Path(case) / "results" / "seats.json").read_text(encoding="utf-8"))
        only = [str(s["stage"]) for s in cast("list[dict[str, Any]]", record["stages"])]
    keep = set(only) if only is not None else {n for n, _, _ in SEATS}
    unknown = keep - {n for n, _, _ in SEATS}
    if unknown:
        raise ValueError(f"not seats of 1.3: {sorted(unknown)}")
    seats = [s for s in SEATS if s[0] in keep]
    if not seats:
        raise ValueError("no seat to draw")
    with matplotlib.style.context(str(STYLE)):
        rc = matplotlib.rcParams
        ink = rc["text.color"]
        edge = rc["axes.prop_cycle"].by_key()["color"][0]
        line_in = float(rc["font.size"]) * 1.5 / 72  # one line of type, in inches
        labels: list[tuple[str, int]] = []
        for number, does, agents in seats:
            depth = number.count(".") - 2  # 0 for 1.3.4, 1 for 1.3.4.1
            body = textwrap.fill(f"{number}  {does}", 72 - 6 * depth)
            who = textwrap.fill("seats: " + ", ".join(agents), 72 - 6 * depth, break_on_hyphens=False)
            labels.append((body + "\n" + who, depth))
        gap = 1.6  # lines between boxes, for the arrow
        heights = [t.count("\n") + 1 + gap for t, _ in labels]
        total = sum(heights)
        fig = Figure(figsize=(rc["figure.figsize"][0], line_in * (total + 1)))
        ax = fig.add_subplot()
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(-total, 0)
        tops: list[tuple[float, float, float]] = []  # each box's top, bottom and left, in lines from the top
        y = 0.0
        for (text, depth), h in zip(labels, heights):
            left = 0.02 + 0.08 * depth
            ax.text(left, -y - gap / 2, text, va="top", ha="left",
                    bbox={"boxstyle": "round,pad=0.4", "facecolor": "none", "edgecolor": edge})
            tops.append((-y - gap / 2, -y - h + gap / 2, left))
            y += h
        for (_, bottom, left), (top, _, left_next) in zip(tops, tops[1:]):
            x = max(left, left_next) + 0.03  # under both boxes where one is indented
            ax.annotate("", xy=(x, top + 0.25), xytext=(x, bottom - 0.25),
                        arrowprops={"arrowstyle": "->", "color": ink, "linewidth": 0.8})
        fig.savefig(path)
    return fig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The scientific figures of a case.")
    sub = parser.add_subparsers(dest="figure", required=True)
    t = sub.add_parser("tornado", help="each input's tornado bar, from tools/sensitivity.py's JSON")
    t.add_argument("sensitivity")
    t.add_argument("out")
    t.add_argument("--labels")
    t.add_argument("--top", type=int, default=15)
    t.add_argument("--xlabel", default="")
    t.add_argument("--scale", type=float, default=1.0)
    t.add_argument("--audience", help="the key of the audience profile whose [design.charts] rc is laid over the house style")
    f = sub.add_parser("seats", help="the flowchart of the seats of notes/fast_estimate.md 1.3")
    f.add_argument("out")
    f.add_argument("--only", nargs="+")
    f.add_argument("--case", help="the case folder whose results/seats.json lists the stages that ran")
    args = parser.parse_args(argv)
    if args.figure == "seats":
        seats_flowchart(args.out, only=args.only, case=args.case)
        print(Path(args.out).resolve())
        return 0
    numbers: dict[str, Any] = json.loads(Path(args.sensitivity).read_text())
    labels: dict[str, str] | None = json.loads(Path(args.labels).read_text()) if args.labels else None
    tornado(numbers, args.out, labels=labels, top=args.top, xlabel=args.xlabel, scale=args.scale,
            audience=args.audience)
    print(Path(args.out).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
