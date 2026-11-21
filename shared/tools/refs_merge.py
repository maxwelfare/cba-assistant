"""tools/refs_merge.py — merge one research seat's refs fragment into a refs index (notes/briefs/refs_merge.md).

Research seats write the sources they cite as a TOML fragment beside their findings; this tool merges it into an index
(a project's research/refs.toml, a case's sources.toml, the shared library/refs.toml), so no merge is hand-written.

    .venv/bin/python -m tools.refs_merge FRAGMENT INDEX [--write]

THE FRAGMENT holds top-level `[<key>]` tables, each a new entry with a `citation` string, and `[update.<key>]`
tables, each an update of an entry the index holds. Keys and field names are bare TOML keys (letters, digits, `_`,
`-`); each field is a string, a list of strings or an integer. Anything else is refused.

THE UPDATE RULE. An update is judged against the index as it stood before the fragment, field by field:
1. a field the entry lacks, or holds as an empty string, is added (after the entry's last field line) or set;
2. a list gains the items it lacks, in order;
3. `quote` gains each passage of the offered value, split on " | ", that the held quote does not already contain;
4. `status` gains the offered reading whole, unless the held status already contains the whole of it, never split,
   since "; " stands inside one reading: a status is a dated log, never replaced, and its last reading is the
   current one;
5. any other held field is kept if equal and refused if not, as is a value whose type differs from the held one: a
   correction is made by hand, after a person reads it.

THE SEPARATORS. This tool joins passages of a quote, and readings of a status, by " | ", as wave 1's merge joined
them (ieq-modeling research/refs.toml). Held statuses also join readings by "; ", written by hand, and "; " stands
inside one reading as well, so the tool never splits on "; ".

THE INDEX must hold only blank lines, comments from their first character, `[<key>]` headers, and `name = value`
fields that tomllib reads alone as a string, a list of strings or an integer: one line, or a multi-line string
(opening with three double or three single quotes) running to the first line at which it reads; one out of that
form is refused whole.
It is read line by line, not written back from tomllib, so that lines outside updated entries, comments included,
stay as and where they are; inside one, only changed or added fields' lines differ, and an added field goes after the
last line of the entry's last field. A replaced multi-line field is written on one line. New entries go
last, after a blank line, a comment `# Added <date> from <fragment path relative to the index's folder>.` and a blank
line, one blank line between them. A value is written as json.dumps(s, ensure_ascii=False), U+007F as \\u007f.

It writes only with --write, and only when nothing is refused and tomllib reads the new text as the index's data with
the fragment applied. A refusal names each refused table and why, with the held and offered value in full, writes
nothing and exits 1, with or without --write. Otherwise it prints each change (the key, the field and only what is
added) and each new entry's key, and exits 0.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tomllib
from datetime import date
from pathlib import Path
from typing import cast

type Value = str | int | list[str]
type Entry = dict[str, Value]

BARE = re.compile(r"[A-Za-z0-9_-]+")
HEADER = re.compile(r"\[([A-Za-z0-9_-]+)\]")
SEP = " | "


class Refused(Exception):
    """A refusal; its message is printed and the run exits 1."""


def show(v: object) -> str:
    return json.dumps(v, ensure_ascii=False)


def as_value(v: object) -> Value | None:
    """The value as a field's type, or None when it is none of them (a boolean is not an integer)."""
    if isinstance(v, str):
        return v
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    if isinstance(v, list):
        items = cast(list[object], v)
        strings = [i for i in items if isinstance(i, str)]
        if len(strings) == len(items):
            return strings
    return None


def toml_value(v: Value) -> str:
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False).replace("\x7f", "\\u007f")
    if isinstance(v, int):
        return str(v)
    return "[" + ", ".join(toml_value(s) for s in v) + "]"


def field_line(name: str, v: Value) -> str:
    return f"{name} = {toml_value(v)}"


def kind(v: Value) -> str:
    return "string" if isinstance(v, str) else "integer" if isinstance(v, int) else "list"


def read_alone(text: str) -> dict[str, object]:
    """The text read as TOML, or empty when it is not TOML."""
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return {}


class Index:
    """An index's lines, with each entry's field lines located."""

    def __init__(self, text: str) -> None:
        self.lines = text.split("\n")
        self.data: dict[str, Entry] = {}
        self.field_at: dict[str, dict[str, tuple[int, int]]] = {}  # each field's lines, start to end exclusive
        self.last_field: dict[str, int] = {}
        bad: list[str] = []
        key: str | None = None
        n = 0
        while n < len(self.lines):
            start, line = n, self.lines[n]
            n += 1
            if not line.strip() or line.startswith("#"):
                continue
            header = HEADER.fullmatch(line)
            if header:
                head: str = header.group(1)
                if head == "update" or head in self.data:
                    bad.append(f"line {start + 1}: header [{head}] is 'update' or repeated")
                self.data[head] = {}
                self.field_at[head] = {}
                self.last_field[head] = start
                key = head
                continue
            name, _, rest = line.partition("=")
            name = name.strip()
            read = read_alone(line)
            if not read and rest.strip()[:3] in ('"""', "'''"):
                # A multi-line string: the field runs to the first line at which its text reads as TOML.
                while not read and n < len(self.lines):
                    n += 1
                    read = read_alone("\n".join(self.lines[start:n]))
                if not read:
                    n = start + 1
            value = as_value(read[name]) if len(read) == 1 and name in read else None
            if key is None or value is None or name in self.data[key]:
                bad.append(f"line {start + 1}: field {name} is not a line, or a multi-line string, read alone as "
                           f"a string, a list of strings or an integer, inside an entry: {line}")
                continue
            self.data[key][name] = value
            self.field_at[key][name] = (start, n)
            self.last_field[key] = n - 1
        if bad:
            raise Refused("index out of form, refused whole:\n  " + "\n  ".join(bad))


def check_fields(label: str, table: dict[str, object]) -> Entry:
    entry: Entry = {}
    why: list[str] = []
    for name, raw in table.items():
        value = as_value(raw)
        if not BARE.fullmatch(name):
            why.append(f"field name {show(name)} is not a bare key")
        elif value is None:
            what = "a table" if isinstance(raw, dict) else f"{type(raw).__name__} {raw!r}"
            why.append(f"field {name} is {what}, not a string, a list of strings or an integer")
        else:
            entry[name] = value
    if why:
        raise Refused(f"{label}: " + "; ".join(why))
    return entry


def read_fragment(data: dict[str, object], errors: list[str]) -> tuple[dict[str, Entry], dict[str, Entry]]:
    """The fragment's new entries and updates; each refused table's reason goes into errors."""
    new: dict[str, Entry] = {}
    updates: dict[str, Entry] = {}
    for key, raw in data.items():
        if key == "update" and isinstance(raw, dict):
            for ukey, uraw in cast(dict[str, object], raw).items():
                label = f"[update.{ukey}]"
                if not isinstance(uraw, dict):
                    errors.append(f"update.{ukey} ({show(ukey)} under [update]): a {type(uraw).__name__} value, "
                                  f"not a table; refused, with offered {show(uraw)}")
                    continue
                try:
                    if not BARE.fullmatch(ukey):
                        raise Refused(f"{label}: key {show(ukey)} is not a bare key")
                    updates[ukey] = check_fields(label, cast(dict[str, object], uraw))
                except Refused as e:
                    errors.append(str(e))
            continue
        if not isinstance(raw, dict):
            errors.append(f"{key} ({show(key)} at top level): a {type(raw).__name__} value, not a table; refused, "
                          f"with offered {show(raw)}")
            continue
        try:
            if not BARE.fullmatch(key):
                raise Refused(f"[{key}]: key {show(key)} is not a bare key")
            entry = check_fields(f"[{key}]", cast(dict[str, object], raw))
            if not isinstance(entry.get("citation"), str):
                raise Refused(f"[{key}]: a new entry with no citation string")
            new[key] = entry
        except Refused as e:
            errors.append(str(e))
    return new, updates


def merge_field(name: str, held: Value | None, offered: Value) -> tuple[Value | None, str]:
    """The field's new value (None when unchanged) and what it adds; Refused when the offer cannot merge."""
    if held is None or (held == "" and isinstance(offered, str)):
        return offered, f"new field: {show(offered)}"
    if kind(held) != kind(offered):
        raise Refused(f"field {name}: held {kind(held)} {show(held)}, offered {kind(offered)} {show(offered)}")
    if isinstance(held, list) and isinstance(offered, list):
        added = [i for n, i in enumerate(offered) if i not in held and i not in offered[:n]]
        return (held + added, "+ " + ", ".join(show(i) for i in added)) if added else (None, "")
    if isinstance(held, str) and isinstance(offered, str) and name in ("quote", "status"):
        parts = offered.split(SEP) if name == "quote" else [offered]
        value = held
        added: list[str] = []
        for part in parts:
            if part not in value:
                value += SEP + part
                added.append(part)
        return (value, "+ " + " | ".join(added)) if added else (None, "")
    if held == offered:
        return None, ""
    raise Refused(f"field {name}: held {show(held)}, offered {show(offered)}; a held field is never replaced")


def merge(fragment: Path, index_path: Path, today: str) -> tuple[str, list[str]]:
    """The new index text and the report of changes; Refused with every reason when any table is refused."""
    text = index_path.read_text(encoding="utf-8")
    index = Index(text)
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise Refused(f"index {index_path} is not TOML: {e}") from None
    try:
        fdata = cast(dict[str, object], tomllib.loads(fragment.read_text(encoding="utf-8")))
    except tomllib.TOMLDecodeError as e:
        raise Refused(f"fragment {fragment} is not TOML: {e}") from None
    errors: list[str] = []
    new, updates = read_fragment(fdata, errors)
    for key in new:
        if key in index.data:
            errors.append(f"[{key}]: a new entry whose key the index holds; held {show(index.data[key])}, "
                          f"offered {show(new[key])}")
    replace: dict[int, str] = {}
    drop: set[int] = set()
    insert: dict[int, list[str]] = {}
    report: list[str] = []
    expected = copy.deepcopy(index.data)
    for key, fields in updates.items():
        if key not in index.data:
            errors.append(f"[update.{key}]: the index holds no entry {key} (an entry this fragment adds is not "
                          f"updated by it)")
            continue
        held = index.data[key]
        for name, offered in fields.items():
            try:
                value, added = merge_field(name, held.get(name), offered)
            except Refused as e:
                errors.append(f"[update.{key}]: {e}")
                continue
            if value is None:
                continue
            expected[key][name] = value
            report.append(f"{key}.{name}: {added}")
            if name in index.field_at[key]:
                first, end = index.field_at[key][name]
                replace[first] = field_line(name, value)
                drop.update(range(first + 1, end))
            else:
                insert.setdefault(index.last_field[key], []).append(field_line(name, value))
    if errors:
        raise Refused("\n".join(errors))
    lines: list[str] = []
    for n, line in enumerate(index.lines):
        if n not in drop:
            lines.append(replace.get(n, line))
        lines.extend(insert.get(n, []))
    if new:
        while lines and not lines[-1].strip():
            lines.pop()
        where = Path(os.path.relpath(fragment.resolve(), index_path.resolve().parent)).as_posix()
        lines += ["", f"# Added {today} from {where}."]
        for key, entry in new.items():
            lines += ["", f"[{key}]"] + [field_line(n, v) for n, v in entry.items()]
            expected[key] = entry
            report.append(f"{key}: new entry")
        lines.append("")
    out = "\n".join(lines)
    got = cast(dict[str, dict[str, object]], tomllib.loads(out))
    wrong = [f"{k}.{f}" for k in expected.keys() | got.keys()
             for f in expected.get(k, {}).keys() | got.get(k, {}).keys()
             if expected.get(k, {}).get(f) != got.get(k, {}).get(f)]
    if wrong:
        raise Refused("the written text does not read back as the index with the fragment applied, at "
                      + ", ".join(sorted(wrong)))
    return out, report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="tools.refs_merge", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fragment", type=Path)
    parser.add_argument("index", type=Path)
    parser.add_argument("--write", action="store_true", help="write the merged index (default: a dry run)")
    args = parser.parse_args(argv)
    fragment = cast(Path, args.fragment)
    index = cast(Path, args.index)
    try:
        out, report = merge(fragment, index, date.today().isoformat())
    except (Refused, OSError, UnicodeDecodeError) as e:
        print(f"REFUSED, nothing written:\n{e}", file=sys.stderr)
        return 1
    if not report:
        print(f"{fragment} changes nothing in {index}; the file is untouched.")
        return 0
    print("\n".join(report))
    if cast(bool, args.write):
        index.write_text(out, encoding="utf-8")
        print(f"written: {index}")
    else:
        print("dry run: nothing written; --write applies it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
