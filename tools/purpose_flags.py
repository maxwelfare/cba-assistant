"""The flags a script computes for a case's purpose check (notes/briefs/purpose_check.md, item 4).

    .venv/bin/python tools/purpose_flags.py CASE [--previous PREV]

CASE is a case folder. PREV is the previous version: a folder if one exists at that path, otherwise a git ref
of the repository at the working directory, the previous version being cases/<CASE's folder name> at that
ref. The command prints each flag on its own line, "<key>: <detail>", and exits 0 whether or not any fires.

1. model_size: with a previous version, either count larger than the previous one's (purpose_check 4.5, "no
   larger than the version before"). Inputs: distinct factor names in estimates.toml, plus top-level tables
   of model/inputs.toml and inputs.toml. Lines: non-blank lines of model/**/*.py, model.py and run.py.
2. no_tornado: documents/policy_paper.md exists and holds no Markdown image whose alt text or path names a
   tornado (purpose_check 4.4). Silent before the paper is written.
3. one_sign: (a) within one option, a benefit row and a cost row, neither with draws, with equal sets of
   factor names, so they cancel in every draw (a pair set to cancel); (b) with a previous version, an effect
   signed there under some option and unsigned in every entry it has now.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tarfile
import tempfile
import tomllib
from io import BytesIO
from pathlib import Path
from typing import Any

Flag = dict[str, str]

IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
READ = ("estimates.toml", "inputs.toml", "model.py", "run.py", "model/", "results/estimate_total.json",
        "documents/policy_paper.md")


def totals(res: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Each total of a results file by its option key ("" for a table with no option)."""
    return res["options"] if "options" in res else {"": res}


def results(case: Path) -> dict[str, Any]:
    """The case's main results table; a case without one is refused, since no flag could be read from it."""
    path = case / "results" / "estimate_total.json"
    if not path.is_file():
        raise SystemExit(f"purpose_flags: no {path}; run the case's estimate first, or name the folder that holds it")
    return json.loads(path.read_text())


def rows(case: Path) -> list[dict[str, Any]]:
    path = case / "estimates.toml"
    return tomllib.loads(path.read_text()).get("effect", []) if path.is_file() else []


def size(case: Path) -> tuple[int, int]:
    """The model's inputs and its non-blank lines of code."""
    names = {f["name"] for r in rows(case) for f in r.get("factor", [])}
    tables = sum(sum(isinstance(v, dict) for v in tomllib.loads(p.read_text()).values())
                 for p in (case / "model" / "inputs.toml", case / "inputs.toml") if p.is_file())
    code = [*(case / "model").rglob("*.py"), case / "model.py", case / "run.py"]
    lines = sum(sum(bool(s.strip()) for s in p.read_text().splitlines()) for p in code if p.is_file())
    return len(names) + tables, lines


def model_size(case: Path, previous: Path) -> list[Flag]:
    (i, n), (pi, pn) = size(case), size(previous)
    if i > pi or n > pn:
        return [{"flag": "model_size", "detail": f"inputs {pi} -> {i}, lines of code {pn} -> {n}"}]
    return []


def no_tornado(case: Path) -> list[Flag]:
    paper = case / "documents" / "policy_paper.md"
    if not paper.is_file():
        return []
    if any("tornado" in (alt + path).lower() for alt, path in IMAGE.findall(paper.read_text())):
        return []
    return [{"flag": "no_tornado", "detail": f"{paper} holds no tornado figure of the inputs that move the result"}]


def one_sign(case: Path, previous: Path | None) -> list[Flag]:
    out: list[Flag] = []
    plain = [r for r in rows(case) if "draws" not in r and r.get("factor")]
    for b in (r for r in plain if r.get("kind") == "benefit"):
        for c in (r for r in plain if r.get("kind") == "cost"):
            same_option = "option" not in b or "option" not in c or b["option"] == c["option"]
            if same_option and {f["name"] for f in b["factor"]} == {f["name"] for f in c["factor"]}:
                out.append({"flag": "one_sign", "detail": f"{b['name']!r} and {c['name']!r} have the same factors,"
                            " a pair set to cancel"})
    if previous:
        before, now = results(previous), results(case)
        def signs(res: dict[str, Any]) -> dict[str, list[bool]]:
            out: dict[str, list[bool]] = {}
            for t in totals(res).values():
                for e in t["effects"]:
                    out.setdefault(e["name"], []).append(bool(e["signed"]))
            return out
        was, cur = signs(before), signs(now)
        for name in sorted(n for n, s in was.items() if any(s) and cur.get(n) and not any(cur[n])):
            out.append({"flag": "one_sign", "detail": f"{name!r} took either sign in the previous version and one"
                        " sign now"})
    return out


def purpose_flags(case: Path, previous: Path | None = None) -> list[Flag]:
    return [*(model_size(case, previous) if previous else []), *no_tornado(case), *one_sign(case, previous)]


def at_ref(ref: str, name: str, into: Path) -> Path:
    """The files this tool reads of cases/<name> at a git ref, written under into."""
    folder = f"cases/{name}"
    listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "--", folder], check=True,
                            capture_output=True, text=True).stdout.split()
    wanted = [p for p in listed if any(p[len(folder) + 1:].startswith(r) for r in READ)]
    if wanted:
        blob = subprocess.run(["git", "archive", ref, "--", *wanted], check=True, capture_output=True).stdout
        with tarfile.open(fileobj=BytesIO(blob)) as tar:
            tar.extractall(into, filter="data")
    return into / folder


def main() -> None:
    ap = argparse.ArgumentParser(description="The flags a script computes for a case's purpose check.")
    ap.add_argument("case", type=Path)
    ap.add_argument("--previous")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        prev: Path | None = None
        if a.previous is not None:
            prev = Path(a.previous) if Path(a.previous).is_dir() else at_ref(a.previous, a.case.resolve().name, Path(tmp))
        for f in purpose_flags(a.case, prev):
            print(f"{f['flag']}: {f['detail']}")


if __name__ == "__main__":
    main()
