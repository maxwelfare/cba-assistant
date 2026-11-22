"""Write a delivered Google Sheet in place: the files a seat needs, from files. No Google access of its own.

The route these steps serve, and the connector calls between them, is the in-place route of `standards/presentation/sheets.md` (part 3).

    python -m tools.sheets.inplace diff SNAPSHOT.json GRID.json [GRID.json ...]
        People's edits since the last write: every entered value (value or formula) that differs from the
        snapshot, every tab added, deleted or renamed, and every change in a tab's row or column count (where
        the snapshot records the counts). A tab-separated table on stdout (tab, cell, was, now); exit 1 when
        there is any change, 0 when there is none, 2 when the input is refused.
    python -m tools.sheets.inplace plan OLD.xlsx NEW.xlsx --live META.json [--snapshot SNAPSHOT.json]
            [--rename OLD=NEW ...] [--copies COPIES.json] --old-columns OLD.tsv --new-columns NEW.tsv --out DIR
        DIR/plan.json names the tabs whose content differs between the deployed xlsx (OLD) and the new one
        (NEW), in NEW's order, and the tabs renamed (only as --rename states them), added and dropped. With
        --snapshot, OLD is refused unless its sha256 is the one the snapshot records. Where a tab is renamed or
        added and the live sheet does not yet show it, DIR/before_copies.json is the update_spreadsheet body to
        apply before the copies are made (it renames the live tab and adds an empty tab under the new name, so
        copied formulas that cite the new names resolve). With --copies ({tab: sheetId of its "Copy of" tab}),
        DIR/batch_1.json, batch_2.json, ... are the update_spreadsheet bodies that paste each copy onto its live
        tab, set widths, heights and frozen panes from NEW, set the tab order and delete the copies; applied in
        number order. Before its paste, each changed tab is restructured natively by column id, read from the
        generator's columns.tsv for each xlsx (--old-columns, --new-columns): the columns NEW drops are deleted,
        those it adds inserted and those that move moved, so the comments and links on a column travel with it.
        Its rows carry no ids, so the header rows (above the draw block, which starts at the row whose column A is
        the number 1, the first draw) are matched OLD to NEW by their column-A text, and a row NEW adds or drops
        there is inserted or deleted natively; plan refuses, naming the tab and the rows, where that match is not
        unique, and where the draw block's row count changes. The paste covers NEW's extent and every column of
        the deployed version wherever the moves pushed it, never a column of the team's own to its right.
    python -m tools.sheets.inplace snapshot GRID.json [GRID.json ...] --out SNAPSHOT.json [--xlsx NEW.xlsx]
        The snapshot of what the live sheet holds after a write, in the form diff reads.

GRID and META files are get_spreadsheet results as the connector saves them, {"content": <Spreadsheet>}; a grid
file holds the tabs and row ranges of one read, and several files may hold parts of one tab. A tab a file lists
with no grid data counts as present but unread, which diff refuses for a tab the snapshot holds.

Two traps of the Sheets API shape this. A read leaves trailing empty rows out of rowData and returns only the tabs in
the ranges asked for, so a read cannot by itself tell an unread tab or row from a deleted one: diff refuses a listed
but unread tab and counts a snapshot cell its reads do not cover as deleted, and a seat that shortens its reads sees
false alarms. And a tab's new name cannot be told from a drop plus an add by pairing names in order, which misreads
both shapes (a drop with an unrelated add read as a rename; renames with a drop read as drops and adds): diff follows
each tab by its sheetId, and plan takes a rename only as --rename states it. A plan change is checked on both shapes,
with xlsx variants made by editing only xl/workbook.xml (a worksheet left orphaned in the zip counts as a shared part
and marks every tab changed).
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
MAX_BATCH_BYTES = 30_000  # the R55 check's choice: under the 30 to 40 KB a clerk sent by hand in one write
ROW_PX_DEFAULT = 21       # the clerks' calibration (roadmap/R55.md, Used 3): a row the xlsx gives no height
COL_PX_DEFAULT = 100      # a column the xlsx gives no width: Google Sheets' default width (the R55 check 3 writer's choice)

Value = str | int | float | bool
Json = dict[str, Any]


class Refused(Exception):
    pass


def letters(col: int) -> str:
    s = ""
    while col:
        col, r = divmod(col - 1, 26)
        s = chr(65 + r) + s
    return s


def split_a1(ref: str) -> tuple[int, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not m:
        raise Refused(f"not a cell reference: {ref}")
    col = 0
    for ch in m.group(1):
        col = col * 26 + ord(ch) - 64
    return int(m.group(2)), col


def load_json(path: Path) -> Json:
    body = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(body, dict):
        raise Refused(f"{path}: not a JSON object")
    return cast(Json, body)


def spreadsheet(path: Path) -> Json:
    body = load_json(path)
    content = body.get("content", body)
    if not isinstance(content, dict) or "sheets" not in content:
        raise Refused(f"{path}: not a get_spreadsheet result (no content.sheets)")
    return cast(Json, content)


# ---------- grid reads ----------

def entered(cell: Json) -> Value | None:
    uev = cast(Json | None, cell.get("userEnteredValue"))
    if not uev:
        return None
    if "formulaValue" in uev:
        return str(uev["formulaValue"])
    if "stringValue" in uev:
        s = str(uev["stringValue"])
        return s if s != "" else None
    if "numberValue" in uev:
        n = float(uev["numberValue"])
        return int(n) if n.is_integer() else n
    if "boolValue" in uev:
        return bool(uev["boolValue"])
    raise Refused(f"an entered value of a kind this helper does not read: {uev}")


@dataclass
class Tab:
    title: str
    sheet_id: int
    index: int
    read: bool = False                                     # some file carried grid data for it
    first: int = 0                                         # rows read, 1-based (0: none)
    last: int = 0
    cells: dict[str, Value] = field(default_factory=lambda: {})
    rows12to14: dict[str, float] = field(default_factory=lambda: {})  # numbers read in rows 12 to 16; the snapshot keeps the tab's statistics rows (`stat_rows`)
    a_rows: set[int] = field(default_factory=lambda: set[int]())  # rows a read covered from column A
    size: tuple[int, int] | None = None                    # rowCount, columnCount of the grid, where given


def read_grids(paths: list[Path]) -> dict[int, Tab]:
    """Every tab the files list, by sheetId, with the entered values and the numbers of its statistics rows (rows 12 to
    14 in the template's layout, 14 to 16 on a tab with the inserted Credence rows: `stat_rows`) of its reads."""
    tabs: dict[int, Tab] = {}
    for path in paths:
        for sheet in cast(list[Json], spreadsheet(path)["sheets"]):
            props = cast(Json, sheet["properties"])
            sid = int(props["sheetId"])
            tab = tabs.setdefault(sid, Tab(str(props["title"]), sid, int(props.get("index", 0))))
            grid = cast(Json, props.get("gridProperties", {}))
            if "rowCount" in grid and "columnCount" in grid:
                size = (int(grid["rowCount"]), int(grid["columnCount"]))
                if tab.size is not None and tab.size != size:
                    raise Refused(f"tab {tab.title}: the reads disagree on its size ({tab.size}, {size}); "
                                  "someone changed it between reads, so read it again")
                tab.size = size
            for data in cast(list[Json], sheet.get("data", [])):
                r0 = int(data.get("startRow", 0))
                c0 = int(data.get("startColumn", 0))
                rows = cast(list[Json], data.get("rowData", []))
                tab.read = True
                if rows:
                    tab.first = r0 + 1 if tab.first == 0 else min(tab.first, r0 + 1)
                    tab.last = max(tab.last, r0 + len(rows))
                for i, row in enumerate(rows):
                    if c0 == 0:
                        tab.a_rows.add(r0 + i + 1)
                    for j, cell in enumerate(cast(list[Json], row.get("values", []))):
                        ref = f"{letters(c0 + j + 1)}{r0 + i + 1}"
                        v = entered(cell)
                        if v is not None:
                            tab.cells[ref] = v
                        eff = cast(Json, cell.get("effectiveValue") or {})
                        if 12 <= r0 + i + 1 <= 16 and "numberValue" in eff:
                            tab.rows12to14[ref] = cast(float, eff["numberValue"])
    return tabs


def stat_rows(tab: Tab) -> range:
    """A column tab's statistics rows, around the row whose column A reads "Draws: mean" (each tab its own). A tab with no
    such label (a text or table tab) keeps rows 12 to 14, but only where the reads covered column A in every row 12 to 16
    that holds a number: otherwise the label may sit in a row no read covered, and the tab is refused."""
    mean = next((int(ref[1:]) for ref, v in tab.cells.items() if re.fullmatch(r"A\d+", ref) and v == "Draws: mean"), None)
    if mean is not None:
        return range(mean - 1, mean + 2)
    unread = sorted({int(re.sub(r"^[A-Z]+", "", ref)) for ref in tab.rows12to14} - tab.a_rows)
    if unread:
        raise Refused(f"tab {tab.title}: no read covers column A in rows {unread}, so its statistics rows are unknown; read column A from row 1 to 16")
    return range(12, 15)


def same(a: Value | None, b: Value | None) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return a == b


def shown(v: Value | None) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    return repr(v) if isinstance(v, float) else str(v)


def a1_key(ref: str) -> tuple[int, int]:
    return split_a1(ref)


def diff(snapshot: Json, live: dict[int, Tab]) -> Iterator[tuple[str, str, str, str]]:
    """People's edits: entered values against the snapshot, and tabs added, deleted or renamed."""
    snap_tabs = cast(dict[str, Json], snapshot["tabs"])
    order = cast(list[str], snapshot.get("tab_order", list(snap_tabs)))
    known: set[int] = set()
    for name in order + [n for n in snap_tabs if n not in order]:
        st = snap_tabs[name]
        sid = int(st["sheetId"])
        known.add(sid)
        tab = live.get(sid)
        if tab is None:
            yield name, "", "tab", "deleted"
            continue
        if tab.title != name:
            yield name, "(tab name)", name, tab.title
        if not tab.read:
            raise Refused(f"tab {tab.title} is listed but not read, so edits in it would go unseen; read its rows")
        # A row or column inserted or deleted outside the rows read shows only in the grid's size.
        if tab.size is not None:
            for key, now in zip(("rowCount", "columnCount"), tab.size):
                if key in st and int(st[key]) != now:
                    yield tab.title, f"({key})", str(st[key]), str(now)
        was = cast(dict[str, Value], st.get("cells", {}))
        for ref in sorted(set(was) | set(tab.cells), key=a1_key):
            if not same(was.get(ref), tab.cells.get(ref)):
                yield tab.title, ref, shown(was.get(ref)), shown(tab.cells.get(ref))
    for tab in sorted(live.values(), key=lambda t: t.index):
        if tab.sheet_id not in known:
            yield tab.title, "", "", f"added tab, {len(tab.cells)} cells read"


def take_snapshot(live: dict[int, Tab], xlsx: Path | None, ids: tuple[str, str]) -> Json:
    tabs = sorted((t for t in live.values() if t.read), key=lambda t: t.index)
    out: Json = {"spreadsheetId": ids[0], "title": ids[1]}
    if xlsx is not None:
        out["source_xlsx_sha256"] = hashlib.sha256(xlsx.read_bytes()).hexdigest()
    out["taken"] = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out["tab_order"] = [t.title for t in tabs]
    out["tabs"] = {}
    for t in tabs:
        entry: Json = {"sheetId": t.sheet_id, "rows_read": f"{t.first}-{t.last}"}
        if t.size is not None:
            entry["rowCount"], entry["columnCount"] = t.size
        entry["cells"] = dict(sorted(t.cells.items(), key=lambda kv: a1_key(kv[0])))
        rows = stat_rows(t) if t.rows12to14 else range(0)
        entry["rows12to14_values"] = {ref: v for ref, v in t.rows12to14.items() if int(re.sub(r"^[A-Z]+", "", ref)) in rows}
        out["tabs"][t.title] = entry
    return out


# ---------- the generated xlsx ----------

def worksheets(path: Path) -> tuple[list[str], dict[str, bytes], bytes]:
    """Tab names in order, each tab's worksheet XML, and the bytes of the parts every tab shares (styles)."""
    z = zipfile.ZipFile(path)
    rels = {r.get("Id"): r.get("Target") or "" for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    names: list[str] = []
    raw: dict[str, bytes] = {}
    members: set[str] = set()
    for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"):
        target = rels[sh.get(RID)].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        name = sh.get("name") or ""
        names.append(name)
        raw[name] = z.read(target)
        members.add(target)
    # A part outside the worksheets that is not bookkeeping (styles, shared strings, theme) can change every tab's
    # look at once, so it is compared too.
    skip = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels", "[Content_Types].xml", "_rels/.rels"}
    shared = b"".join(n.encode() + b"\0" + z.read(n) for n in sorted(z.namelist())
                      if n not in members and n not in skip and not n.startswith("docProps/"))
    return names, raw, shared


@dataclass
class Shape:
    rows: int = 0
    cols: int = 0
    widths: dict[int, float] = field(default_factory=lambda: {})   # 1-based column: xlsx width
    heights: dict[int, float] = field(default_factory=lambda: {})  # 1-based row: points
    frozen: tuple[int, int] = (0, 0)                               # rows, columns


def shape(xml: bytes) -> Shape:
    s = Shape()
    root = ET.fromstring(xml)
    pane = root.find(f"{M}sheetViews/{M}sheetView/{M}pane")
    if pane is not None and pane.get("state") in ("frozen", "frozenSplit"):
        s.frozen = (int(float(pane.get("ySplit", "0"))), int(float(pane.get("xSplit", "0"))))
    for col in root.iter(M + "col"):
        w = col.get("width")
        if w is not None:
            for i in range(int(col.get("min", "0")), int(col.get("max", "0")) + 1):
                s.widths[i] = float(w)
    for row in root.iter(M + "row"):
        r = int(row.get("r", "0"))
        s.rows = max(s.rows, r)
        ht = row.get("ht")
        if ht is not None:
            s.heights[r] = float(ht)
        for c in row.iter(M + "c"):
            rr, cc = split_a1(c.get("r") or "")
            s.rows, s.cols = max(s.rows, rr), max(s.cols, cc)
    return s


def column_px(width: float) -> int:
    return round(7 * width - 1)  # the clerks' calibration (roadmap/R55.md, Used 3), the conversion Google gave on import


def row_px(points: float) -> int:
    return round(points * 4 / 3)  # the clerks' calibration (roadmap/R55.md, Used 3)


def runs(sizes: list[tuple[int, int]]) -> Iterator[tuple[int, int, int]]:
    """(start, end exclusive, px) for each run of adjacent 0-based indexes sharing one size."""
    start = prev = -2
    px = -1
    for i, p in sorted(sizes):
        if i == prev + 1 and p == px:
            prev = i
            continue
        if start >= 0:
            yield start, prev + 1, px
        start = prev = i
        px = p
    if start >= 0:
        yield start, prev + 1, px


def dimension_requests(sid: int, s: Shape) -> list[Json]:
    last = max([s.cols, *s.widths])
    cols = [(c - 1, column_px(s.widths[c]) if c in s.widths else COL_PX_DEFAULT) for c in range(1, last + 1)]
    rows = [(r - 1, row_px(s.heights[r]) if r in s.heights else ROW_PX_DEFAULT) for r in range(1, s.rows + 1)]
    out: list[Json] = []
    for dim, sizes in (("COLUMNS", cols), ("ROWS", rows)):
        for a, b, px in runs(sizes):
            out.append({"updateDimensionProperties": {
                "range": {"sheetId": sid, "dimension": dim, "startIndex": a, "endIndex": b},
                "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    out.append({"updateSheetProperties": {
        "properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": s.frozen[0], "frozenColumnCount": s.frozen[1]}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    return out


def grow(sid: int, grid: Json, rows: int, cols: int) -> list[Json]:
    """appendDimension where a tab's grid is smaller than the range pasted into or from it."""
    out: list[Json] = []
    for dim, have, need in (("ROWS", int(grid.get("rowCount", 0)), rows), ("COLUMNS", int(grid.get("columnCount", 0)), cols)):
        if have < need:
            out.append({"appendDimension": {"sheetId": sid, "dimension": dim, "length": need - have}})
    return out


@dataclass
class Plan:
    changed: list[str]
    renamed: dict[str, str]     # old name: new name
    added: list[str]
    dropped: list[str]


@dataclass
class Texts:
    heads: dict[int, set[str]] = field(default_factory=lambda: {})   # 0-based column: its texts in rows 1 to 3
    labels: list[str] = field(default_factory=lambda: [])            # the header rows' column-A text, row 1 first
    draws: int = 0                                                   # the draw block's rows


def header_texts(xlsx: Path) -> dict[str, Texts]:
    """Each tab's header texts, from the xlsx itself. The draw block is the rows from the first whose column A is
    the number 1 (the generator writes each draw's number there) to the last; the rows above it are the header,
    each labelled by its column-A text (a formula as =text), "" where empty."""
    z = zipfile.ZipFile(xlsx)
    strings = (["".join(t.text or "" for t in si.iter(M + "t"))
                for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(M + "si")]
               if "xl/sharedStrings.xml" in z.namelist() else [])
    _, raw, _ = worksheets(xlsx)
    out: dict[str, Texts] = {}
    for tab, xml in raw.items():
        t = out.setdefault(tab, Texts())
        col_a: dict[int, str] = {}
        first = last = 0
        for row in ET.fromstring(xml).iter(M + "row"):
            r = int(row.get("r", "0"))
            last = max(last, r)
            for c in row.iter(M + "c"):
                col = split_a1(c.get("r") or "")[1]
                if r > 3 and col > 1:
                    continue
                v, f = c.find(M + "v"), c.find(M + "f")
                text = ("".join(x.text or "" for x in c.iter(M + "t")) if c.get("t") == "inlineStr"
                        else strings[int(v.text or "0")] if c.get("t") == "s" and v is not None
                        else (v.text or "") if v is not None else "")
                if r <= 3:
                    t.heads.setdefault(col - 1, set()).add(text)
                if col == 1:
                    col_a[r] = "=" + (f.text or "") if f is not None else text
                    if not first and f is None and c.get("t") in (None, "n") and text == "1":
                        first = r
        head = first - 1 if first else last
        t.labels = [col_a.get(r, "") for r in range(1, head + 1)]
        t.draws = last - head
    return out


def match_rows(old: list[str], new: list[str], tab: str) -> list[tuple[int, int]]:
    """The pairs (old row, new row), 0-based, of the one longest order-keeping match of the labels. Refused where
    two such matches differ (a row added or dropped beside another of its label), or where a gap between matched
    rows holds a different number of unmatched rows on each side (which old row became which new one is unknown);
    a gap of equal sizes on both sides is the same rows relabelled, kept in place."""
    n, m = len(old), len(new)
    length = [[0] * (m + 1) for _ in range(n + 1)]
    ways = [[1] * (m + 1) for _ in range(n + 1)]   # distinct longest matches of the suffixes
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            best = max(length[i + 1][j], length[i][j + 1], length[i + 1][j + 1] + (old[i] == new[j]))
            length[i][j] = best
            w = ways[i + 1][j + 1] if old[i] == new[j] and best == length[i + 1][j + 1] + 1 else 0
            w += ways[i + 1][j] if length[i + 1][j] == best else 0
            w += ways[i][j + 1] if length[i][j + 1] == best else 0
            w -= ways[i + 1][j + 1] if length[i + 1][j + 1] == best else 0
            ways[i][j] = w
    pairs: list[tuple[int, int]] = []
    i = j = 0
    while i < n and j < m:
        if old[i] == new[j] and length[i][j] == length[i + 1][j + 1] + 1:
            pairs.append((i, j))
            i, j = i + 1, j + 1
        elif length[i + 1][j] == length[i][j]:
            i += 1
        else:
            j += 1
    unmatched = sorted({old[k] for k in range(n) if k not in {a for a, _ in pairs}}
                       | {new[k] for k in range(m) if k not in {b for _, b in pairs}})
    if ways[0][0] > 1:
        raise Refused(f"tab {tab}: its header rows cannot be matched old to new by their column-A text, since more "
                      f"than one match fits; the rows labelled {unmatched}")
    out: list[tuple[int, int]] = []
    pi = pj = 0
    for a, b in pairs + [(n, m)]:
        if a - pi != b - pj and a > pi and b > pj:
            raise Refused(f"tab {tab}: rows {pi + 1} to {a} of OLD's header become rows {pj + 1} to {b} of NEW's, "
                          f"{a - pi} against {b - pj}, so which became which is unknown; the rows labelled "
                          f"{sorted(set(old[pi:a]) | set(new[pj:b]))}")
        if a - pi == b - pj:
            out.extend((pi + k, pj + k) for k in range(a - pi))
        if a < n:
            out.append((a, b))
        pi, pj = a + 1, b + 1
    return out


def row_pairs(old: Texts, new: Texts, tab: str) -> list[tuple[int, int]]:
    """A column tab's header rows matched OLD to NEW, or refused (see match_rows); its draw block must keep its size."""
    if old.draws != new.draws:
        raise Refused(f"tab {tab}: its draw block has {old.draws} rows in OLD and {new.draws} in NEW; draw rows carry "
                      "no labels, so the helper moves none")
    if old.labels == new.labels:
        return [(k, k) for k in range(len(old.labels))]
    return match_rows(old.labels, new.labels, tab)


def restructure_rows(sid: int, old: Texts, new: Texts, count: int, tab: str) -> tuple[list[Json], int]:
    """The deleteDimension and insertDimension requests that turn the live tab's header rows (OLD's) into NEW's,
    and the row count after them. Top down: each request's index is where NEW has the row, since every row above
    it already stands as NEW has it."""
    pairs = row_pairs(old, new, tab)
    if old.labels == new.labels:
        return [], count
    if len(old.labels) > count:
        raise Refused(f"tab {tab}: the live tab has {count} rows, fewer than the deployed version's header; "
                      "someone deleted rows: read it again and run diff")
    reqs: list[Json] = []

    def dim(start: int, end: int) -> Json:
        return {"sheetId": sid, "dimension": "ROWS", "startIndex": start, "endIndex": end}

    pi = pj = 0
    for a, b in pairs + [(len(old.labels), len(new.labels))]:
        if a > pi:
            reqs.append({"deleteDimension": {"range": dim(pj, pj + a - pi)}})
        if b > pj:
            reqs.append({"insertDimension": {"range": dim(pj, b), "inheritFromBefore": pj > 0}})
        pi, pj = a + 1, b + 1
    print(f"note: tab {tab}: header rows deleted {[old.labels[k] for k in range(len(old.labels)) if k not in {a for a, _ in pairs}]}"
          f", inserted {[new.labels[k] for k in range(len(new.labels)) if k not in {b for _, b in pairs}]}", file=sys.stderr)
    return reqs, count + len(new.labels) - len(old.labels)


def read_columns(path: Path, xlsx: Path, texts: dict[str, Texts]) -> dict[str, dict[int, str]]:
    """The generator's columns.tsv for XLSX: {tab: {0-based column: id}}. A name may hold a newline the generator
    writes unquoted, so a record is the lines joined until it has its seven fields. Each record's name must be a
    header cell (rows 1 to 3) at its letter in XLSX, so a columns.tsv from another version is refused rather than
    read as this one's ids (the generator writes both from one run)."""
    heads = {tab: t.heads for tab, t in texts.items()}
    tabs = list(heads)
    out: dict[str, dict[int, str]] = {}
    held = ""
    for line in path.read_text(encoding="utf-8").split("\n"):
        held = line if not held else held + "\n" + line
        f = held.split("\t")
        if len(f) < 7:
            continue
        held = ""
        if len(f) > 7:
            raise Refused(f"{path}: a record with {len(f)} fields, 7 expected: {f[:4]}")
        tab, letter, cid, name = f[0], f[1], f[2], f[3]
        if tab not in tabs:
            raise Refused(f"{path}: tab {tab} is not a tab of its xlsx")
        if not cid:
            raise Refused(f"{path}: tab {tab} column {letter} has no id")
        cols = out.setdefault(tab, {})
        if cid in cols.values():
            raise Refused(f"{path}: tab {tab} repeats the id {cid}")
        col = split_a1(letter + "1")[1] - 1
        if name not in heads[tab].get(col, set()):
            raise Refused(f"{path}: tab {tab} column {letter} is {name!r}, which is no header of {xlsx} there: "
                          "give the columns.tsv written with that xlsx")
        if col in cols:
            raise Refused(f"{path}: tab {tab} repeats the column {letter}")
        cols[col] = cid
    if held.strip():
        raise Refused(f"{path}: the last record is cut short: {held[:80]!r}")
    return out


def restructure(sid: int, old: dict[int, str], new: dict[int, str], count: int, deployed: int, tab: str
                ) -> tuple[list[Json], int, int]:
    """The deleteDimension, moveDimension and insertDimension requests that turn the live tab's columns (OLD's ids
    at OLD's places, `count` columns, the first `deployed` of them OLD's) into NEW's, the column count after them,
    and the place after the last of OLD's columns, wherever they were pushed. Deletes go first, from the
    right, so no inserted column takes a deleted one's place (and its comments); then, left to right, each place
    of NEW gets its id moved in from the right, where it still is, or a new column inserted. A place NEW gives no
    id keeps the column already there unless that column is an id still to be placed, which a blank column
    inserted before it pushes on."""
    if old and max(old) >= count:
        raise Refused(f"tab {tab}: the live tab has {count} columns, fewer than the deployed version's ids need; "
                      "someone deleted columns: read it again and run diff")
    cur: list[str | None] = [old.get(i) for i in range(count)]
    ours = [i < deployed for i in range(count)]   # beside cur: the column is OLD's, not one of the team's own
    keep = set(new.values())
    reqs: list[Json] = []

    def dim(start: int, end: int) -> Json:
        return {"sheetId": sid, "dimension": "COLUMNS", "startIndex": start, "endIndex": end}

    gone = sorted((i for i, cid in old.items() if cid not in keep), reverse=True)
    for i in gone:
        reqs.append({"deleteDimension": {"range": dim(i, i + 1)}})
        del cur[i]
        del ours[i]
    if gone:
        print(f"note: tab {tab}: the new version drops the columns {[old[i] for i in sorted(gone)]}; they are "
              "deleted, with any comment on them", file=sys.stderr)
    placed = set(old.values()) & keep
    for j in range(max(new, default=-1) + 1):
        want = new.get(j)
        if j >= len(cur):
            reqs.append({"appendDimension": {"sheetId": sid, "dimension": "COLUMNS", "length": j + 1 - len(cur)}})
            cur.extend([None] * (j + 1 - len(cur)))
            ours.extend([False] * (j + 1 - len(ours)))
            continue   # a place past the live columns: no id of OLD can be needed there, since all sit left of it
        if want is None:
            if cur[j] is None and ours[j]:
                continue   # OLD's own id-less column stays; a team column here is never taken for it
        elif want in placed:
            i = cur.index(want)   # i >= j: every place left of j already holds what NEW puts there
            if i != j:
                reqs.append({"moveDimension": {"source": dim(i, i + 1), "destinationIndex": j}})
                cur.insert(j, cur.pop(i))
                ours.insert(j, ours.pop(i))
            continue
        reqs.append({"insertDimension": {"range": dim(j, j + 1), "inheritFromBefore": j > 0}})
        cur.insert(j, None)
        ours.insert(j, False)
    return reqs, len(cur), max((i + 1 for i, o in enumerate(ours) if o), default=0)


def compare_versions(old: Path, new: Path, renamed: dict[str, str]
                     ) -> tuple[Plan, list[str], dict[str, bytes], dict[str, bytes]]:
    """A rename is only what the seat states: a guessed pairing could paste one tab over another people link to."""
    old_names, old_raw, old_shared = worksheets(old)
    new_names, new_raw, new_shared = worksheets(new)
    for o, n in renamed.items():
        if o not in old_raw or o in new_raw or n not in new_raw or n in old_raw:
            raise Refused(f"rename {o}={n}: {o} must be a tab of OLD only and {n} a tab of NEW only")
    if len(set(renamed.values())) != len(renamed):
        raise Refused("two tabs renamed to one name")
    was = {new_name: old_name for old_name, new_name in renamed.items()}
    added = [n for n in new_names if n not in old_raw and n not in was]
    dropped = [n for n in old_names if n not in new_raw and n not in renamed]
    every = old_shared != new_shared
    changed = [n for n in new_names
               if n in added or every or old_raw[was.get(n, n)] != new_raw[n]]
    return Plan(changed, renamed, added, dropped), new_names, old_raw, new_raw


def requests_for(plan: Plan, new_names: list[str], old_raw: dict[str, bytes], new_raw: dict[str, bytes],
                 live: Json, copies: dict[str, int], old_cols: dict[str, dict[int, str]],
                 new_cols: dict[str, dict[int, str]], old_texts: dict[str, Texts], new_texts: dict[str, Texts]
                 ) -> list[Json]:
    sheets = {int(cast(Json, s["properties"])["sheetId"]): cast(Json, s["properties"])
              for s in cast(list[Json], live["sheets"])}
    by_title = {str(p["title"]): sid for sid, p in sheets.items()}
    was = {n: o for o, n in plan.renamed.items()}

    def live_id(name: str) -> int:
        for title in (name, was.get(name)):
            if title is not None and title in by_title:
                return by_title[title]
        raise Refused(f"the live sheet has no tab {name}" + (f" or {was[name]}" if name in was else "")
                      + "; apply before_copies.json before the copies are made")

    for name, sid in copies.items():
        if sid not in sheets:
            raise Refused(f"copy {sid} of {name} is not in the live tab list; read the list after copying "
                          "(a copy may have failed, or answered 'Internal error' after succeeding)")
    missing = [n for n in plan.changed if n not in copies]
    if missing:
        raise Refused(f"no copy given for the changed tabs {missing}")

    reqs: list[Json] = []
    for name in plan.changed:
        copy = copies[name]
        new = shape(new_raw[name])
        sid = live_id(name)   # an added tab is the empty tab before_copies.json made, pasted like any other
        old = Shape() if name in plan.added else shape(old_raw[was.get(name, name)])
        rows, cols = max(new.rows, old.rows), max(new.cols, old.cols)   # old surplus cells are pasted over with empties
        grid = dict(cast(Json, sheets[sid].get("gridProperties", {})))
        o_ids, n_ids = old_cols.get(was.get(name, name), {}), new_cols.get(name, {})
        if name not in plan.added and o_ids and n_ids:
            # The owner, 2026-11-21: "comments usually stay with cells?" They do under native column moves, not
            # under a paste, so each column, and each header row, is put where NEW has it before its content is
            # pasted.
            if "columnCount" not in grid or "rowCount" not in grid:
                raise Refused(f"the live tab list gives no row or column count for {name}")
            o_text, n_text = old_texts[was.get(name, name)], new_texts[name]
            moves, grid["rowCount"] = restructure_rows(sid, o_text, n_text, int(grid["rowCount"]), name)
            # Rows in OLD's extent follow the rows inserted or deleted above the draws.
            rows = max(new.rows, old.rows + len(n_text.labels) - len(o_text.labels))
            col_moves, grid["columnCount"], ends = restructure(sid, o_ids, n_ids, int(grid["columnCount"]),
                                                               old.cols, name)
            reqs.extend(moves + col_moves)
            cols = max(new.cols, ends)   # OLD's columns wherever pushed, never a team's column right of them
        reqs.extend(grow(copy, cast(Json, sheets[copy].get("gridProperties", {})), rows, cols))
        reqs.extend(grow(sid, grid, rows, cols))
        for kind in ("PASTE_NORMAL", "PASTE_DATA_VALIDATION"):
            reqs.append({"copyPaste": {
                "source": {"sheetId": copy, "startRowIndex": 0, "endRowIndex": rows, "startColumnIndex": 0, "endColumnIndex": cols},
                "destination": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": rows, "startColumnIndex": 0, "endColumnIndex": cols},
                "pasteType": kind, "pasteOrientation": "NORMAL"}})
        reqs.extend(dimension_requests(sid, new))
    ids = [live_id(n) for n in new_names]
    live_order = sorted(ids, key=lambda i: int(sheets[i].get("index", 0)) if i in sheets else 0)
    if live_order != ids:
        for i, sid in enumerate(ids):
            reqs.append({"updateSheetProperties": {"properties": {"sheetId": sid, "index": i}, "fields": "index"}})
    for copy in copies.values():
        reqs.append({"deleteSheet": {"sheetId": copy}})
    return reqs


def compact(body: Json) -> int:
    return len(json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def batches(reqs: list[Json], limit: int) -> list[Json]:
    """The requests in order, cut into bodies of at most `limit` bytes of compact JSON each."""
    out: list[list[Json]] = [[]]
    for r in reqs:
        if compact({"requests": [r]}) > limit:
            raise Refused(f"one request is over {limit} bytes: {json.dumps(r)[:200]}")
        if compact({"requests": out[-1] + [r]}) > limit:
            out.append([])
        out[-1].append(r)
    return [{"requests": b} for b in out if b]


def write_json(path: Path, body: object) -> None:
    path.write_text(json.dumps(body, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


# ---------- the commands ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.sheets.inplace", description=(__doc__ or "").split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    d = sub.add_parser("diff", help="people's edits since the last write; exit 1 when there is any")
    d.add_argument("snapshot", type=Path)
    d.add_argument("grids", type=Path, nargs="+")
    p = sub.add_parser("plan", help="the changed tabs, and the request batches that write them")
    p.add_argument("old", type=Path)
    p.add_argument("new", type=Path)
    p.add_argument("--live", type=Path, required=True)
    p.add_argument("--snapshot", type=Path, help="the last write's snapshot; OLD must be the xlsx it records")
    p.add_argument("--rename", action="append", default=[], metavar="OLD=NEW",
                   help="a tab NEW renames; repeat for each (a rename is never guessed)")
    p.add_argument("--copies", type=Path)
    p.add_argument("--old-columns", type=Path, required=True, help="the generator's columns.tsv for OLD")
    p.add_argument("--new-columns", type=Path, required=True, help="the generator's columns.tsv for NEW")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-bytes", type=int, default=MAX_BATCH_BYTES)
    s = sub.add_parser("snapshot", help="the snapshot of the live sheet after a write")
    s.add_argument("grids", type=Path, nargs="+")
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--xlsx", type=Path, help="the xlsx written, whose sha256 the snapshot records")
    a = ap.parse_args(argv)
    try:
        if a.command == "diff":
            snap = load_json(cast(Path, a.snapshot))
            changes = list(diff(snap, read_grids(cast(list[Path], a.grids))))
            w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
            w.writerow(["tab", "cell", "was", "now"])
            w.writerows(changes)
            return 1 if changes else 0
        if a.command == "snapshot":
            grids = cast(list[Path], a.grids)
            first = spreadsheet(grids[0])
            props = cast(Json, first.get("properties", {}))
            body = take_snapshot(read_grids(grids), cast(Path | None, a.xlsx),
                                 (str(first.get("spreadsheetId", "")), str(props.get("title", ""))))
            cast(Path, a.out).write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
            return 0
        old_xlsx = cast(Path, a.old)
        if a.snapshot is not None:
            recorded = load_json(cast(Path, a.snapshot)).get("source_xlsx_sha256")
            got = hashlib.sha256(old_xlsx.read_bytes()).hexdigest()
            if got != recorded:
                raise Refused(f"OLD {old_xlsx} has sha256 {got}, the snapshot records {recorded}: "
                              "OLD must be the xlsx the last write deployed")
        renamed: dict[str, str] = {}
        for r in cast(list[str], a.rename):
            o, eq, n = r.partition("=")
            if not eq or not o or not n or o in renamed:
                raise Refused(f"--rename {r}: give OLD=NEW, once per tab")
            renamed[o] = n
        plan, new_names, old_raw, new_raw = compare_versions(old_xlsx, cast(Path, a.new), renamed)
        old_texts, new_texts = header_texts(old_xlsx), header_texts(cast(Path, a.new))
        old_cols = read_columns(cast(Path, a.old_columns), old_xlsx, old_texts)
        new_cols = read_columns(cast(Path, a.new_columns), cast(Path, a.new), new_texts)
        out = cast(Path, a.out)
        out.mkdir(parents=True, exist_ok=True)
        for stale in list(out.glob("batch_*.json")) + [out / "before_copies.json"]:
            stale.unlink(missing_ok=True)
        live = spreadsheet(cast(Path, a.live))
        # Refused here too, before the seat makes any copy.
        was = {n: o for o, n in plan.renamed.items()}
        for name in plan.changed:
            o = was.get(name, name)
            if name not in plan.added and old_cols.get(o) and new_cols.get(name):
                row_pairs(old_texts[o], new_texts[name], name)
        write_json(out / "plan.json", {"changed": plan.changed, "renamed": plan.renamed, "added": plan.added,
                                       "dropped": plan.dropped})
        titles = {str(cast(Json, s["properties"])["title"]): int(cast(Json, s["properties"])["sheetId"])
                  for s in cast(list[Json], live["sheets"])}
        # Run before the copies, so a copied formula citing a renamed or added tab finds it; a second run, on the
        # tab list read after the copies, finds them done and writes nothing here.
        before: list[Json] = []
        for o, n in plan.renamed.items():
            if n in titles:
                continue
            if o not in titles:
                raise Refused(f"the live sheet has neither {o} nor {n}")
            before.append({"updateSheetProperties": {"properties": {"sheetId": titles[o], "title": n}, "fields": "title"}})
        before.extend({"addSheet": {"properties": {"title": n}}} for n in plan.added if n not in titles)
        if before:
            write_json(out / "before_copies.json", {"requests": before})
        if a.copies is not None:
            copies = {str(k): int(v) for k, v in load_json(cast(Path, a.copies)).items()}
            reqs = requests_for(plan, new_names, old_raw, new_raw, live, copies, old_cols, new_cols,
                                old_texts, new_texts)
            for i, body in enumerate(batches(reqs, cast(int, a.max_bytes)), start=1):
                write_json(out / f"batch_{i}.json", body)
        for name in plan.dropped:
            print(f"note: the new version drops tab {name}; the plan leaves the live tab for the seat to delete "
                  "(if it was renamed, run again with --rename)", file=sys.stderr)
        return 0
    except (Refused, OSError, KeyError, ValueError, zipfile.BadZipFile, ET.ParseError) as e:
        print(f"refused: {e!r}" if isinstance(e, KeyError) else f"refused: {e}", file=sys.stderr)
        return 2
    finally:
        sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(main())
