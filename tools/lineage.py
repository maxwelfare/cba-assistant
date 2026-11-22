"""The lineage map of a case: which input, from which source, feeds which run's results.

Run from the repository root:

    .venv/bin/python -m tools.lineage cases/<case>

It writes `<case>/ro-crate-metadata.json`, an RO-Crate 1.2 (https://w3id.org/ro/crate/1.2) conforming to the Process
Run Crate profile 0.6 (https://w3id.org/ro/wfrun/process/0.6; Leo et al. 2024, PLOS ONE 19(9) e0309210), and
`<case>/results/lineage.md`, its companion for people (CHEERS 2022 item 22; AEA Data and Code Availability Standard
item 13). Each input of inputs.toml is a PropertyValue citing one entity per sources.toml key; each results/*.json is
one CreateAction whose `object` holds the declared inputs that run read (a read mixture brings its components). The
read set is the results file's `inputs_read` when it records one; otherwise it is measured by a short replay of the
case's model through the engine at the current commit, calling the engine as the run script does (`run(case,
model_for(reading))` for each of the script's `READINGS`, else `run(case, model)`), and both outputs say so.

The crate states the licence of the crate (that of inputs.toml) and of each file it lists, read from REUSE.toml at
the repository root (REUSE specification 3.3; the shared licensing standard, 3.4); a file no annotation matches is
listed as a gap.

It reads the case's TOML files itself rather than through the loader, so a case the loader refuses still gets its
map: this is a report and refuses nothing. The loader is needed only for a replay.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import shlex
import subprocess
import sys
import tomllib
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from cost_benefit_engine import distributions
from cost_benefit_engine.documents import signed

CRATE = "https://w3id.org/ro/crate/1.2"
PROFILE = "https://w3id.org/ro/wfrun/process/0.6"
CONTEXT = [f"{CRATE}/context", "https://w3id.org/ro/terms/workflow-run/context"]
# Draws for a replay: enough above the largest rank-correlation group for the correlation step, few enough to take
# seconds; the read set does not depend on the number of draws unless the model branches on the values drawn.
REPLAY_DRAWS = 100
GAP_HEADINGS = (
    "Inputs the model read that inputs.toml does not declare",
    "Inputs declared and never read",
    "Sources no input cites",
    "Sources with neither url nor DOI",
    "Inputs with no source (none of source, sources or guidance)",
)

# The full name of each licence REUSE.toml uses: the `name` field of the SPDX License List 3.29
# (https://spdx.org/licenses/licenses.json, read 2026-11-02); LicenseRef-third-party's is the project's own.
LICENCE_NAMES = {
    "CC0-1.0": "Creative Commons Zero v1.0 Universal",
    "CC-BY-4.0": "Creative Commons Attribution 4.0 International",
    "CC-BY-SA-4.0": "Creative Commons Attribution Share Alike 4.0 International",
    "MIT": "MIT License",
    "LicenseRef-third-party": "Third-party material, not licensed by the holder",
}

Doc = dict[str, Any]


@dataclass
class RunRecord:
    file: str  # results/<name>.json
    record: Doc
    script: str | None  # the run script's file name, from the record's command
    read: set[str] | None  # None when unknown
    iterated: bool
    how: str  # one sentence on where the read set comes from


def _toml(path: Path) -> Doc:
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _git(folder: Path, *args: str) -> str | None:
    done = subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def _root(case: Path) -> Path | None:
    top = _git(case, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else None


def _licences(case: Path, files: Sequence[str]) -> dict[str, str | None]:
    """Each file's SPDX-License-Identifier by REUSE.toml at the repository root (REUSE 3.3,
    https://reuse.software/spec-3.3/): a path pattern's `*` matches anything but `/`, `**` anything including `/`,
    `\\*` a literal asterisk; of the [[annotations]] tables that match a file, the last counts. None: no table matches
    (or no REUSE.toml)."""
    root = _root(case)
    tables = cast(list[Doc], _toml(root / "REUSE.toml").get("annotations", [])) if root is not None else []
    tokens = {"\\\\": re.escape("\\"), "\\*": re.escape("*"), "**": ".*", "*": "[^/]*"}
    patterns: list[tuple[list[re.Pattern[str]], str | None]] = []
    for t in tables:
        paths = cast(list[str], t["path"] if isinstance(t["path"], list) else [t["path"]])
        regexes = [re.compile("".join(tokens.get(x, re.escape(x)) for x in re.split(r"(\\\\|\\\*|\*\*|\*)", p))) for p in paths]
        patterns.append((regexes, cast(str | None, t.get("SPDX-License-Identifier"))))
    out: dict[str, str | None] = {}
    for f in files:
        path = case / f
        rel = path.relative_to(root).as_posix() if root is not None and path.is_relative_to(root) else None
        matched = [licence for regexes, licence in patterns if rel is not None and any(r.fullmatch(rel) for r in regexes)]
        out[f] = matched[-1] if matched else None
    return out


def _licence_entity(case: Path, licence: str) -> Doc:
    """A licence as RO-Crate 1.2 states one: an SPDX licence by its spdx.org URI, a LicenseRef by a local entity whose
    description is its text in LICENSES/."""
    name = LICENCE_NAMES.get(licence)
    if not licence.startswith("LicenseRef-"):
        entity: Doc = {"@id": f"https://spdx.org/licenses/{licence}", "@type": "CreativeWork", "name": name or licence, "identifier": licence}
        if name is None:
            entity["description"] = "Its full name is not in tools/lineage.py's LICENCE_NAMES; see the @id."
        return entity
    root = _root(case)
    text = root / "LICENSES" / f"{licence}.txt" if root is not None else None
    return {
        "@id": f"#{licence}", "@type": "CreativeWork", "name": name or licence,
        "description": text.read_text(encoding="utf-8") if text is not None and text.is_file() else f"LICENSES/{licence}.txt is missing.",
    }


def _files(case: Path, runs: Sequence[RunRecord]) -> list[str]:
    """The files the crate lists other than run scripts."""
    files = [f for f in ("case.toml", "inputs.toml", "sources.toml") if (case / f).is_file()]
    files += sorted(f"data/{p.name}" for p in (case / "data").glob("*.csv"))
    return files + [r.file for r in runs] + ["results/lineage.md"]


def _source_keys(case: Path, spec: Mapping[str, Any]) -> list[str]:
    """The sources.toml keys an input names: `source`, `sources`, or for an indexed input the distinct cells of the
    column `source = { column = ... }` names in data/<indexed_by>.csv."""
    out: list[str] = []
    source = spec.get("source")
    if isinstance(source, str):
        out.append(source)
    elif isinstance(source, dict):
        column = cast(str, cast(Doc, source)["column"])
        with (case / "data" / f"{spec['indexed_by']}.csv").open(newline="", encoding="utf-8") as f:
            out += [row[column] for row in csv.DictReader(f) if row[column]]
    out += cast(list[str], spec.get("sources", []))
    return list(dict.fromkeys(out))


def _with_components(read: set[str], declared: Mapping[str, Doc]) -> set[str]:
    """The read set with every component, at any depth, of each mixture read."""
    out = set(read)
    todo = [k for k in read if k in declared]
    while todo:
        for part in cast(Mapping[str, object], declared[todo.pop()].get("components", {})):
            if part not in out:
                out.add(part)
                if part in declared:
                    todo.append(part)
    return out


def _text(v: object) -> str:
    if isinstance(v, dict):
        d = cast(Doc, v)
        return f"column {d['column']}" if set(d) == {"column"} else ", ".join(f"{k} {_text(x)}" for k, x in d.items())
    if isinstance(v, list):
        return "[" + ", ".join(_text(x) for x in cast(list[object], v)) + "]"
    return str(v)


def _value(spec: Mapping[str, Any], edition: str) -> float | int | str:
    """The point value of a constant, else a short text of the distribution and its parameters."""
    kind = spec.get("distribution")
    if "guidance" in spec:
        return f"official guidance entry {spec['guidance']}, edition {edition}"
    if kind == "constant" and isinstance(spec.get("mean"), (int, float)) and not isinstance(spec.get("mean"), bool):
        return cast(float, spec["mean"])
    if not isinstance(kind, str):
        return "no distribution stated"
    try:
        required, optional = distributions.fields(kind)
        names = [k for k in spec if k in required | optional]
    except ValueError:
        names = []
    where = f" (rows of data/{spec['indexed_by']}.csv)" if "indexed_by" in spec else ""
    return f"{kind}{where}: " + "; ".join(f"{k} {_text(spec[k])}" for k in names) if names else kind + where


def _cell(text: object) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


# ---------------------------------------------------------------- the runs


def _script(command: str) -> str | None:
    """The run script's file name: the module after `-m`, or the first .py the command names."""
    tokens = shlex.split(command)
    if "-m" in tokens and tokens.index("-m") + 1 < len(tokens):
        return tokens[tokens.index("-m") + 1].rsplit(".", 1)[-1] + ".py"
    return next((Path(t).name for t in tokens if t.endswith(".py")), None)


def _replay(case: Path, script: str | None) -> tuple[set[str], bool]:
    from cost_benefit_engine.case import guidance_for, load
    from cost_benefit_engine.run import Model, model_from, run

    loaded = load(case, guidance_for(case))
    fn = model_from(loaded)
    module = sys.modules[fn.__module__]
    readings: Sequence[str] = ()
    if script is not None and (case / script).is_file():
        spec = importlib.util.spec_from_file_location(f"_lineage_{case.name}_{script[:-3]}", case / script)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            readings = cast(Sequence[str], getattr(mod, "READINGS", ()))
    model_for = getattr(module, "model_for", None)
    models = [cast(Model, model_for(r)) for r in readings] if readings and callable(model_for) else [fn]
    read: set[str] = set()
    iterated = False
    for m in models:
        r = run(loaded, m, iterations=REPLAY_DRAWS)
        read |= set(r.inputs_read)
        iterated |= r.inputs_iterated
    return read, iterated


def _runs(case: Path) -> list[RunRecord]:
    out: list[RunRecord] = []
    head = _git(case, "rev-parse", "HEAD")
    dirty = _git(case, "status", "--porcelain", "--untracked-files=no")
    for path in sorted((case / "results").glob("*.json")):
        record = cast(Doc, json.loads(path.read_text(encoding="utf-8")))
        script = _script(str(record.get("command", "")))
        file = f"results/{path.name}"
        if isinstance(record.get("inputs_read"), list):
            read = set(cast(list[str], record["inputs_read"]))
            iterated = bool(record.get("inputs_iterated", False))
            how = f"The read set is the one the run recorded (inputs_read in {file})."
        else:
            tree = "a clean working tree" if dirty == "" else "uncommitted changes in the working tree"
            try:
                read, iterated = _replay(case, script)
                how = (
                    f"The run did not record the inputs it read, so the read set was measured by a replay of the case's "
                    f"model through the engine ({REPLAY_DRAWS} draws) at commit {head} with {tree}, not recorded by the "
                    f"run; the code replayed may differ from the run's commit {record.get('commit')}."
                )
            except Exception as e:  # a report refuses nothing: the failure is stated in both outputs
                read, iterated = None, False
                how = f"The run did not record the inputs it read, and a replay at commit {head} failed ({_cell(e)}): the read set is unknown."
        if iterated:
            how += " The model iterated its inputs, so every input counts as read and the read set cannot tell which inputs matter."
        out.append(RunRecord(file, record, script, read, iterated, how))
    return out


# ---------------------------------------------------------------- the crate


def _crate(
    case: Path, declared: Mapping[str, Doc], sources: Mapping[str, Doc], runs: Sequence[RunRecord], edition: str,
    licences: Mapping[str, str | None],
) -> Doc:
    graph: list[Doc] = []
    files = _files(case, runs)

    source_ids: dict[str, str] = {}
    cited = {k for spec in declared.values() for k in _source_keys(case, spec)}
    for key in [*sources, *sorted(cited - set(sources))]:
        entry = sources.get(key, {})
        where = f"https://doi.org/{str(entry['doi']).removeprefix('https://doi.org/')}" if "doi" in entry else entry.get("url")
        sid = where if isinstance(where, str) and where not in source_ids.values() else f"#source-{key}"
        source_ids[key] = sid
        entity: Doc = {"@id": sid, "@type": "CreativeWork", "identifier": key}
        entity["name"] = entry.get("citation", key)
        if "citation" not in entry:
            entity["description"] = "sources.toml has no citation text for this key" if key in sources else "named by inputs.toml but not a key in sources.toml"
        if isinstance(where, str):
            entity["url"] = where
        graph.append(entity)

    values: list[Doc] = []
    for name, spec in declared.items():
        pv: Doc = {"@id": f"#input-{name}", "@type": "PropertyValue", "name": name, "value": _value(spec, edition)}
        pv["description"] = f"{spec.get('label', name)} (evidence type: {spec.get('evidence_type', 'not stated')})"
        if "unit" in spec:
            pv["unitText"] = spec["unit"]
        pv["citation"] = [{"@id": source_ids[k]} for k in _source_keys(case, spec)]
        values.append(pv)

    actions: list[Doc] = []
    scripts: dict[str, Doc] = {}
    for r in runs:
        rec = r.record
        if r.script is not None and r.script not in scripts:
            scripts[r.script] = {
                "@id": r.script, "@type": ["File", "SoftwareSourceCode"], "name": r.script, "programmingLanguage": "Python",
                **({} if (case / r.script).is_file() else {"description": "named by the results file's command; not present in the case folder"}),
            }
        instrument = r.script if r.script is not None else f"#command-{Path(r.file).stem}"
        if r.script is None:
            scripts[instrument] = {"@id": instrument, "@type": "SoftwareApplication", "name": str(rec.get("command", "no command recorded"))}
        read = set[str]() if r.read is None else _with_components(r.read, declared) & set(declared)
        action: Doc = {
            "@id": f"#run-{Path(r.file).stem}", "@type": "CreateAction",
            "name": f"Run of {r.script or 'an unnamed script'} that wrote {r.file}",
            "description": (
                f"Command {rec.get('command')}; commit {rec.get('commit')}, working tree {rec.get('working_tree')}; random seed "
                f"{rec.get('random_seed')}; {rec.get('iterations')} iterations; date recorded {rec.get('date')}. {r.how}"
            ),
            "instrument": {"@id": instrument},
            "object": [{"@id": f"#input-{k}"} for k in declared if k in read],
            "result": [{"@id": r.file}],
        }
        m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}(?::\d{2})?))?", str(rec.get("date", "")))
        if m:
            action["endTime"] = m[1] + (f"T{m[2]}" if m[2] else "")
        actions.append(action)

    root: Doc = {
        "@id": "./", "@type": "Dataset", "name": f"Lineage of the case {case.name}",
        "description": (
            f"The inputs of the case {case.name} (inputs.toml), each a PropertyValue citing its sources (sources.toml), and "
            "each run that wrote a results file, with the inputs it read as its object; Process Run Crate 0.6 allows "
            "PropertyValue in a CreateAction's object for values not stored as files. Written by tools/lineage.py."
        ),
        "datePublished": datetime.now().astimezone().isoformat(timespec="seconds"),
        "conformsTo": [{"@id": PROFILE}],
        "hasPart": [{"@id": f} for f in [*files, *(s for s in scripts if not s.startswith("#"))]],
        "mentions": [{"@id": a["@id"]} for a in actions],
    }
    descriptor: Doc = {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": {"@id": "./"}, "conformsTo": {"@id": CRATE}}
    profile: Doc = {"@id": PROFILE, "@type": "CreativeWork", "name": "Process Run Crate", "version": "0.6"}
    parts: list[Doc] = [{"@id": f, "@type": "File", "name": f} for f in files]
    licensed = {"./": licences.get("inputs.toml"), **{f: licences.get(f) for f in [*files, *scripts]}}
    kinds = {x: _licence_entity(case, x) for x in sorted({x for x in licensed.values() if x is not None})}
    for entity in [root, *parts, *scripts.values()]:
        if (licence := licensed.get(entity["@id"])) is not None:
            entity["license"] = {"@id": kinds[licence]["@id"]}
    return {"@context": CONTEXT, "@graph": [descriptor, root, profile, *parts, *scripts.values(), *actions, *values, *graph, *kinds.values()]}


# ---------------------------------------------------------------- the map for people


def _markdown(
    case: Path, declared: Mapping[str, Doc], sources: Mapping[str, Doc], runs: Sequence[RunRecord], edition: str,
    licences: Mapping[str, str | None],
) -> str:
    out = [f"# Lineage of the case {case.name}", ""]
    out.append(
        "Which input, from which source, feeds which run's results. Written by tools/lineage.py "
        f"({datetime.now().astimezone().isoformat(timespec='minutes')}); the same map, machine-readable, is "
        "ro-crate-metadata.json (RO-Crate 1.2, Process Run Crate 0.6). A report: it refuses nothing."
    )
    listed = {f: x for f, x in licences.items() if f != "inputs.toml" or (case / f).is_file()}
    none = "no licence (no REUSE.toml annotation matches)"
    counts = Counter(x or none for x in listed.values())
    out += ["", (
        f"Licence, by REUSE.toml: the crate's is that of inputs.toml, {licences.get('inputs.toml') or none}; its {len(listed)} "
        "files: " + "; ".join(f"{n} under {x}" for x, n in sorted(counts.items())) + "."
    )]
    out += ["", "## Runs", ""]
    if not runs:
        out.append("No results file, so no run: the inputs and sources alone.")
    for i, r in enumerate(runs, 1):
        rec = r.record
        out.append(f"{i}. {r.file}, written by {r.script or 'a script the command does not name'}.")
        out.append(f"   {i}.1. Command: {rec.get('command')}")
        out.append(f"   {i}.2. Commit {rec.get('commit')}; working tree: {rec.get('working_tree')}.")
        out.append(f"   {i}.3. Random seed {rec.get('random_seed')}; {rec.get('iterations')} iterations; date recorded {rec.get('date')}.")
        out.append(f"   {i}.4. {r.how}")
    out += ["", "## Inputs", ""]
    prcc = {r.file: cast(Mapping[str, object], r.record["prcc_headline"]) for r in runs if isinstance(r.record.get("prcc_headline"), dict)}
    head = ["Input", "Value or distribution", "Unit", "Sources"]
    head += [f"Read in {r.file}" for r in runs] + [f"PRCC with the headline, {f}" for f in prcc]
    out += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    reads = {r.file: None if r.read is None else _with_components(r.read, declared) for r in runs}
    for name, spec in declared.items():
        cited = "; ".join(f"{k}: {sources.get(k, {}).get('citation', 'no citation text')}" for k in _source_keys(case, spec))
        cells = [f"`{name}`", _value(spec, edition), spec.get("unit", ""), cited]
        cells += ["unknown" if (s := reads[r.file]) is None else ("yes" if name in s else "no") for r in runs]
        for p in prcc.values():
            v = p.get(name)
            cells.append(signed(v) if isinstance(v, float) else "")
        out.append("| " + " | ".join(_cell(c) for c in cells) + " |")

    known = [s for s in reads.values() if s is not None]
    read_any = set[str]().union(*known)
    cited_all = {k for spec in declared.values() for k in _source_keys(case, spec)}
    gaps = [
        sorted(read_any - set(declared)),
        sorted(set(declared) - read_any) if known else [],
        sorted(set(sources) - cited_all),
        sorted(k for k, e in sources.items() if "url" not in e and "doi" not in e),
        sorted(k for k, s in declared.items() if not ({"source", "sources", "guidance"} & set(s))),
    ]
    out += ["", "## Gaps", "", "Listed, never refused."]
    unlicensed = [f for f, x in listed.items() if x is None]
    out += ["", "Files the crate lists that no REUSE.toml annotation matches: " + (", ".join(f"`{f}`" for f in unlicensed) if unlicensed else "none.")]
    for heading, keys in zip(GAP_HEADINGS, gaps):
        out += ["", f"### {heading}", ""]
        if heading == GAP_HEADINGS[1] and not known:
            out.append("No run with a known read set.")
        elif heading == GAP_HEADINGS[1] and any(r.iterated for r in runs):
            out.append("A model iterated its inputs, so every input counts as read.")
        out.append(", ".join(f"`{k}`" for k in keys) if keys else "None.")
    return "\n".join(out) + "\n"


def main(argv: Sequence[str]) -> int:
    if len(argv) != 1:
        print("usage: .venv/bin/python -m tools.lineage <case folder>", file=sys.stderr)
        return 2
    case = Path(argv[0]).resolve()
    declared = {k: cast(Doc, v) for k, v in _toml(case / "inputs.toml").items() if isinstance(v, dict)}
    sources = {k: cast(Doc, v) for k, v in _toml(case / "sources.toml").items() if isinstance(v, dict)}
    edition = str(_toml(case / "case.toml").get("guidance_edition", "not stated in case.toml"))
    runs = _runs(case)
    licences = _licences(case, ["inputs.toml", *_files(case, runs), *(r.script for r in runs if r.script is not None)])
    (case / "results").mkdir(exist_ok=True)
    crate = _crate(case, declared, sources, runs, edition, licences)
    (case / "ro-crate-metadata.json").write_text(json.dumps(crate, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (case / "results" / "lineage.md").write_text(_markdown(case, declared, sources, runs, edition, licences), encoding="utf-8")
    print(f"wrote {case / 'ro-crate-metadata.json'} and {case / 'results' / 'lineage.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
