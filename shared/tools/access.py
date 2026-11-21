"""tools/access.py: which of the registry's accesses this user holds, and the file each is read from.

The owner, 2026-11-16: "One registry, read by the tool. ... A status command prints which keys are set, never a value."

THE REGISTRY is library/access.toml in the folder above this file's own, found from this file's place, so a copy of
the two in another tree works as it stands. A row describes a service and is the same for every user; its `env_var` is
the one name of what a user holds for it.

WHERE A VALUE IS READ is stated once, in the env_var paragraph of the registry's header, and this tool does what it
says, reading the environment and the file at every call. One function returns a value, `value`, to the tool that
sends it (the polite fetch of tools/host_cooldown.py, by a row's key_host and its key_header or key_query); no other prints, raises,
returns or writes one, and the tool writes no file.

    .venv/bin/python -m tools.access status              # what is set or bad, the connectors, how many are not set
    .venv/bin/python -m tools.access status --all        # every variable
    .venv/bin/python -m tools.access status NAME ...     # these names (a variable or a row's id), in the order given
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import NamedTuple, cast

REGISTRY = Path(__file__).resolve().parent.parent / "library" / "access.toml"
KEY_DIR = Path(".local") / "share" / "research-keys"
REQUIRED = ("name", "credential", "env_var")
VAR = re.compile(r"[A-Z][A-Z0-9_]*\Z")
QUERY_NAME = re.compile(r"[A-Za-z0-9._~-]+\Z")   # RFC 3986 unreserved characters: a name sent without encoding
ASSIGNMENT = re.compile(r"""(export(\s|$)|["']?[A-Z0-9_]*_[A-Z0-9_]*["']?\s*[=:])""")
SET_NOTE = "set: a value is present. No request is made, so whether its service accepts it is not known."
Rows = dict[str, dict[str, str]]


class Refused(Exception):
    """The registry cannot be used as it stands; the message names the file, the row and the field."""


def rows(path: Path | None = None) -> Rows:
    """The registry's rows by id. Refuses a file or a row it cannot use rather than skip it."""
    path = path or REGISTRY
    try:
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise Refused(f"{path}: {e}") from e
    out: Rows = {}
    files: dict[str, tuple[str, str]] = {}
    keyed: dict[str, tuple[str, tuple[str, str, str]]] = {}
    for rid, row in loaded.items():
        if not isinstance(row, dict):
            raise Refused(f"{path}: {rid} is not a table")
        fields = cast(dict[str, object], row)
        missing = [k for k in REQUIRED if k not in fields]
        if missing:
            raise Refused(f"{path}: row {rid} has no {', '.join(missing)}")
        wrong = [k for k, v in fields.items() if not isinstance(v, str)]
        if wrong:
            raise Refused(f"{path}: row {rid}: {', '.join(wrong)} is not a string")
        r = cast(dict[str, str], row)
        var, kf = r["env_var"], r.get("key_file", "")
        if var and not VAR.match(var):
            raise Refused(f"{path}: row {rid}: env_var {var!r} is not capitals, digits and underscores")
        if kf and not var:
            raise Refused(f"{path}: row {rid} gives a key_file and no env_var")
        if kf and not kf.startswith("~/"):
            raise Refused(f"{path}: row {rid}: key_file {kf!r} does not start with ~/")
        if r["credential"] == "connector" and not r.get("tools"):
            raise Refused(f"{path}: row {rid} is a connector and gives no tools")
        host, header, query = r.get("key_host", ""), r.get("key_header", ""), r.get("key_query", "")
        if host or header or query:
            if not (host and bool(header) != bool(query) and var):
                raise Refused(f"{path}: row {rid} gives key_host, key_header or key_query without key_host, an env_var "
                              "and exactly one of key_header and key_query")
            if header and (header.count("{value}") != 1 or not header.isprintable()):
                raise Refused(f"{path}: row {rid}: key_header is not one line holding {{value}} once")
            if query and not QUERY_NAME.match(query):
                raise Refused(f"{path}: row {rid}: key_query {query!r} is not a bare parameter name")
            first, first_form = keyed.setdefault(host, (rid, (header, query, var)))
            if first_form != (header, query, var):
                raise Refused(f"{path}: rows {first} and {rid} give key_host {host} and differ on its key_header, "
                              "key_query or env_var")
        if var:
            first, first_kf = files.setdefault(var, (rid, kf))
            if first_kf != kf:
                raise Refused(f"{path}: rows {first} and {rid} give {var} and differ on its key_file")
        out[rid] = r
    return out


class Held(NamedTuple):
    var: str
    rows: tuple[str, ...]
    file: Path
    where: str  # "environment", "file", "bad" (the file is no value or cannot be read) or "" (not set)
    note: str   # why the file is bad, or that the environment overrides a file that holds a value


def _file_value(path: Path) -> tuple[str, str]:
    """(the value the user's file holds, "" when none; why it is no value). Only `value` passes the value on."""
    try:
        text = path.read_text(encoding="utf-8-sig")  # an editor's byte-order mark is no part of the value
    except FileNotFoundError:
        return "", ""
    except (OSError, UnicodeDecodeError) as e:
        return "", f"cannot be read ({type(e).__name__})"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        return "", f"holds {len(lines)} lines; the file holds the value alone"
    if not lines:
        return "", ""
    line = lines[0]
    if ASSIGNMENT.match(line):
        return "", "holds an assignment; the file holds the value alone"
    if len(line) > 1 and line[0] == line[-1] and line[0] in "\"'":
        return "", "is wrapped in quote marks; the file holds the value alone"
    return line, ""


def _file(reg: Rows, var: str) -> Path:
    """The user's file for `var`: the key_file of the rows that name it (rows refuses two that differ), else the default."""
    given = next((r.get("key_file", "") for r in reg.values() if r["env_var"] == var), "")
    return Path.home() / (given[2:] if given else KEY_DIR / var)


def value(var: str, reg: Rows | None = None) -> str:
    """The value this user holds for `var` by the registry's env_var rule, "" when none. The one function that returns
    a value, for a tool that sends it; `holdings` reads by the same rule."""
    return os.environ.get(var, "").strip() or _file_value(_file(reg if reg is not None else rows(), var))[0]


def _show(path: Path, home: Path) -> str:
    return f"~/{path.relative_to(home)}"   # every file is built under the home (key_file starts with ~/)


def holdings(reg: Rows) -> list[Held]:
    """One entry per variable the registry names, sorted by name: whether this user holds it, and from where."""
    home = Path.home()
    by_var: dict[str, list[str]] = {}
    for rid, r in reg.items():
        if r["env_var"]:
            by_var.setdefault(r["env_var"], []).append(rid)
    out: list[Held] = []
    for var, rids in sorted(by_var.items()):
        path = _file(reg, var)
        in_file, problem = _file_value(path)
        if os.environ.get(var, "").strip():
            where = "environment"
            note = f"and the file {_show(path, home)}, which the environment overrides" if in_file else ""
        elif in_file:
            where, note = "file", ""
        else:
            where, note = ("bad", problem) if problem else ("", "")
        out.append(Held(var, tuple(sorted(rids)), path, where, note))
    return out


def _var_line(reg: Rows, h: Held) -> str:
    names, where = ", ".join(h.rows), _show(h.file, Path.home())
    if h.where == "environment":
        return f"set      {h.var} (environment{', ' + h.note if h.note else ''}): {names}"
    if h.where == "file":
        return f"set      {h.var} (file {where}): {names}"
    if h.where == "bad":
        return f"bad      {h.var} (file {where}): {h.note}: {names}"
    signup = next((reg[r]["signup_url"] for r in h.rows if reg[r].get("signup_url")), "")
    return (f"not set  {h.var} (not in this session's environment; no value in {where}): {names}. If the user holds "
            f"it, it goes in {where} alone, read at every call." + (f" Sign up: {signup}" if signup else ""))


def _row_line(reg: Rows, rid: str) -> str:
    """The line for a row with no variable."""
    r = reg[rid]
    if r["credential"] == "connector":
        return f"connector {rid}: no command can see it; yours when your own tool list holds names that start {r['tools']}"
    if r["credential"] == "none":
        return f"none     {rid}: takes nothing from the user"
    how = r.get("how_to_get", "")
    return f"account  {rid}: {r['credential']}, which this command does not read." + (f" How to get it: {how}" if how else "")


def status(names: list[str], everything: bool) -> int:
    reg = rows()
    held = holdings(reg)
    lines: list[str] = []
    if names:
        for name in names:
            hit = [h for h in held if name == h.var or name in h.rows]
            if not hit and name not in reg:
                print(f"access: no row of the registry is named {name} or names it as its env_var")
                return 2
            line = _var_line(reg, hit[0]) if hit else _row_line(reg, name)
            if line not in lines:
                lines.append(line)
    else:
        shown = [h for h in held if everything or h.where]
        lines = [_var_line(reg, h) for h in shown]
        lines += [_row_line(reg, rid) for rid in sorted(reg) if reg[rid]["credential"] == "connector"]
        if rest := len(held) - len(shown):
            lines.append(f"{rest} more names are not set (no value in this session's environment or in their files): "
                         "`status --all` lists them, `status NAME` one.")
    if any(line.startswith("set ") for line in lines):
        lines.append(SET_NOTE)
    print("\n".join(lines))
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("names", nargs="*")
    s.add_argument("--all", action="store_true")
    a = p.parse_args(argv)
    try:
        return status(cast(list[str], a.names), bool(a.all))
    except Refused as e:
        print(f"access: the registry is refused: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
