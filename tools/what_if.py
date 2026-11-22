"""tools/what_if.py — what a change of a case's inputs does to its totals, as a lead, never a result of record
(roadmap item 2.60).

    .venv/bin/python tools/what_if.py cases/<case> --set "NAME=LOW,MIDDLE,HIGH" [--set ...] [--skip LABEL ...] [--keep]

It makes a scratch copy of the repository at HEAD (`git worktree add --detach`, under the system temporary folder,
with the repository's .venv linked in), and there, in every .toml file under the case folder, gives each table block
whose `name` is exactly NAME, or whose header `[...NAME]` ends in it, the new `low`, `middle` and `high`, editing those
lines only, so the rest of each file stays byte for byte. A block so named that has no `low`, `middle` or `high` line
of its own (a model input whose values sit in other keys or in sub-blocks such as `[[input.method]]`) is refused,
naming NAME and its file, since a change there would report a change and move nothing; a factor of an [[effect]] row
is exempt, as it may state only `name` and take its values from a `[factors.NAME]` entry. It then runs the case's steps, stated in `cases/<case>/rerun.toml`:

    totals = "results/estimate_total.json"      # path under the case folder
    [[step]]
    label = "totals"
    command = "tools/estimate_total.py --quiet cases/<case>/estimates.toml"   # run as PYTHONPATH=. .venv/bin/python <command>

and prints, for each option of the totals file (the form tools/estimate_total.py writes), the expected total before
(as committed at HEAD), after, and their difference, in millions, then the share of draws above zero before and after.
Before and after print at the one count of significant figures, two or more, that tells every option's before and after
apart; the difference prints to two.
The scratch copy is removed afterwards, on failure too, unless --keep. Nothing in the caller's tree changes.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # this tree's engine, whatever the venv points at

from cost_benefit_engine.documents import percent, separating_figures, significant  # noqa: E402

HEADER = re.compile(r"\s*\[")
TABLE = re.compile(r"\s*\[([^\[\]]+)\]\s*(#.*)?$")  # a single-bracket header, [a.b]
NAME = re.compile(r'\s*name\s*=\s*"([^"]*)"')
END = re.compile(r"(\s*(low|middle|high)\s*=\s*)([^\s#]+)(.*)", re.DOTALL)


class Refusal(Exception):
    """A refusal: its message is the one line printed."""


def parse_set(text: str) -> tuple[str, tuple[str, str, str]]:
    """NAME=LOW,MIDDLE,HIGH, the three numbers kept as written and checked LOW <= MIDDLE <= HIGH."""
    name, eq, rest = text.partition("=")
    ends = [e.strip() for e in rest.split(",")]
    try:
        low, middle, high = (float(e) for e in ends)
    except ValueError:
        raise Refusal(f"--set {text!r}: give NAME=LOW,MIDDLE,HIGH with three numbers") from None
    if not eq or not name.strip():
        raise Refusal(f"--set {text!r}: give NAME=LOW,MIDDLE,HIGH")
    if not low <= middle <= high:
        raise Refusal(f"--set {text!r}: LOW <= MIDDLE <= HIGH does not hold")
    return name.strip(), (ends[0], ends[1], ends[2])


def blocks(lines: list[str]) -> list[tuple[str | None, list[int]]]:
    """Each table block of a file: its name (its first `name` line, else the last key of a [a.b] header; None if
    neither) and its line indices, the header's first."""
    out: list[tuple[str | None, str | None, list[int]]] = [(None, None, [])]  # header key, name line, lines
    for i, line in enumerate(lines):
        if HEADER.match(line):
            t = TABLE.match(line)
            out.append((t[1].split(".")[-1].strip().strip('"') if t else None, None, []))
        key, name, idx = out[-1]
        m = NAME.match(line)
        out[-1] = (key, m[1] if m and name is None else name, [*idx, i])
    return [(name or key, idx) for key, name, idx in out]


def apply(case: Path, name: str, ends: tuple[str, str, str]) -> tuple[int, int, set[str]]:
    """Set NAME's ends in every .toml under the case; return its blocks and files changed, and every name seen. A block
    named NAME with no end of its own, other than an [[effect]] row's factor, is refused."""
    n_blocks, n_files, names = 0, 0, set[str]()
    new: dict[str, str] = dict(zip(("low", "middle", "high"), ends))
    for path in sorted(case.rglob("*.toml")):
        lines = path.read_text().splitlines(keepends=True)
        hit = 0
        for block_name, idx in blocks(lines):
            if block_name is None:
                continue
            names.add(block_name)
            if block_name != name:
                continue
            found = [(i, m) for i in idx if (m := END.fullmatch(lines[i]))]
            if not found:
                if lines[idx[0]].strip().startswith("[[effect"):
                    continue
                raise Refusal(f"--set {name}: its block in {path.relative_to(case)} has no low, middle or high line of"
                              " its own (a model input whose values sit in other keys or sub-blocks); what_if cannot"
                              " change it, so edit it by hand")
            hit += 1
            for i, m in found:
                lines[i] = m[1] + new[m[2]] + m[4]
        if hit:
            path.write_text("".join(lines))
            n_blocks, n_files = n_blocks + hit, n_files + 1
    return n_blocks, n_files, names


def options(path: Path) -> dict[str, dict[str, Any]]:
    """Each option's total from a totals file; a table with no option gives one, `total`."""
    data: dict[str, Any] = json.loads(path.read_text())
    parts: dict[str, Any] = data.get("options") or {"total": data}
    return {key: part["total"] for key, part in parts.items()}


def git(cwd: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise Refusal(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def run(scratch: Path, case: Path, sets: list[tuple[str, tuple[str, str, str]]], skip: set[str]) -> None:
    rerun_path = case / "rerun.toml"
    if not rerun_path.exists():
        raise Refusal(f"{rerun_path.relative_to(scratch)} is not committed: add it, with `totals` and a [[step]] for each step")
    rerun = tomllib.loads(rerun_path.read_text())
    if "totals" not in rerun:
        raise Refusal(f"{rerun_path.relative_to(scratch)}: add `totals`, the totals file's path under the case folder")
    steps: list[dict[str, str]] = rerun.get("step", [])
    if not steps:
        raise Refusal(f"{rerun_path.relative_to(scratch)}: add a [[step]] with `label` and `command` for each step")
    totals = case / rerun["totals"]
    if not totals.exists():
        raise Refusal(f"{totals.relative_to(scratch)} is not committed at HEAD: commit the case's totals first")
    before = options(totals)
    for name, ends in sets:
        n_blocks, n_files, names = apply(case, name, ends)
        if not n_blocks:
            close = difflib.get_close_matches(name, sorted(names), n=3)
            raise Refusal(f"no block named {name!r} in the case; closest: {', '.join(close) or 'none close'}")
        print(f"set {name}: {n_blocks} blocks in {n_files} files")
    env = {**os.environ, "PYTHONPATH": "."}
    for step in steps:
        if step["label"] in skip:
            print(f"step {step['label']}: skipped")
            continue
        start = time.monotonic()
        r = subprocess.run([str(scratch / ".venv" / "bin" / "python"), *shlex.split(step["command"])], cwd=scratch,
                           env=env, capture_output=True, text=True)
        print(f"step {step['label']}: {time.monotonic() - start:.1f} s")
        if r.returncode:
            tail = (r.stdout + r.stderr).splitlines()[-20:]
            raise Refusal(f"step {step['label']} failed (exit {r.returncode}); its last lines:\n" + "\n".join(tail))
    after = options(totals)
    n = separating_figures([t["expected"] / 1e6 for t in (*before.values(), *after.values())])
    rows = [["(millions)", "before", "after", "change", "share of draws above zero, before -> after"]]
    for key, b in before.items():
        a = after[key]
        chance = ""
        if "chance_positive" in b and "chance_positive" in a:
            pair = (b["chance_positive"], a["chance_positive"])
            m = separating_figures(pair, show=percent)
            chance = f"{percent(pair[0], m)} -> {percent(pair[1], m)}"
        rows.append([key, significant(b["expected"] / 1e6, n), significant(a["expected"] / 1e6, n),
                     significant((a["expected"] - b["expected"]) / 1e6), chance])
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    for r in rows:
        print(" ".join([r[0].ljust(widths[0]), *(c.rjust(w) for c, w in zip(r[1:4], widths[1:]))]) + f"  {r[4]}".rstrip())


def main() -> int:
    p = argparse.ArgumentParser(description="What a change of a case's inputs does to its totals (a lead, never of record).")
    p.add_argument("case", type=Path)
    p.add_argument("--set", action="append", required=True, dest="sets", metavar="NAME=LOW,MIDDLE,HIGH")
    p.add_argument("--skip", action="append", default=[], metavar="LABEL")
    p.add_argument("--keep", action="store_true")
    a = p.parse_args()
    try:
        sets = [parse_set(s) for s in a.sets]
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
        rel = a.case.resolve().relative_to(root)
    except (Refusal, ValueError) as e:
        print(e, file=sys.stderr)
        return 1
    scratch = Path(tempfile.mkdtemp(prefix="what_if_"))  # git worktree add fills an empty folder
    try:
        git(root, "worktree", "add", "--detach", "-q", str(scratch), "HEAD")
        (scratch / ".venv").symlink_to(root / ".venv")
        run(scratch, scratch / rel, sets, set(a.skip))
        return 0
    except Refusal as e:
        print(e, file=sys.stderr)
        return 1
    finally:
        if a.keep:
            print(f"scratch copy kept at {scratch}")
        else:
            subprocess.run(["git", "worktree", "remove", "--force", str(scratch)], cwd=root, capture_output=True)
            if scratch.exists() and not any(scratch.iterdir()):
                scratch.rmdir()  # git worktree add failed and left the empty folder


if __name__ == "__main__":
    sys.exit(main())
