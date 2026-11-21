"""tools/hwp2txt.py: the text of an HWP 5.0 file, with Python's standard library only.

    <project>/.venv/bin/python -I shared/tools/hwp2txt.py original.hwp text.txt

or, from code run in the shared folder, `from tools.hwp2txt import hwp_text` (the file's bytes in, its text out), or
`hwp_streams` (the file's bytes in, its compound-file streams out, once its HWP 5.0 FileHeader is found).

WHY. HWP is the format of Hancom's word processor, in which Korean public bodies publish much of their guidance.
Some guidelines are published only as HWP 5.0:
LibreOffice cannot load them, and the established reader, pyhwp's hwp5txt (recalled), needs a package install,
which a sandbox may refuse, so this reader uses the standard library only. A reader that drops line breaks and the
two special spaces joins numbers (a table's two values read "3.01342.3266"). This one keeps them, and refuses the
cases a lenient reader passes over in silence.

WHAT IT READS, by Hancom's HWP 5.0 file format (revision 1.3, 2018) and Microsoft's [MS-CFB], both recalled, not
opened: the OLE compound file's streams; the FileHeader's flags; each BodyText/Section stream, raw-deflated when
the compressed flag is set; and, in its record stream, every paragraph-text record (tag 67), as UTF-16LE. Each
paragraph is one line, and a table's or text box's paragraphs follow in record order, a cell to a line, so a
table's layout is lost. Control codes 1 to 9, 11, 12 and 14 to 23 take eight code units: 9 is a tab, and the rest
mark an object, field or note and are skipped whole. Of the one-unit codes, 10 (line break) is a newline, 24 a
hyphen, 30 and 31 (non-breaking and fixed-width space) a space. An equation's script and a picture give no text.

REFUSES, on stderr with exit 2, writing nothing (CORE rule 3): a file that is not a compound file (an .hwpx is a
zip of XML, and HWP 3.0 is another format), a compound file with no HWP header, a document that is
password-protected, distribution-only or DRM-protected (its text is encrypted), one with no paragraph text, and a
damaged file, or one this reader cannot follow: any other error in reading it is named in the refusal.

CHECKED, 2026-11-10, on the two HWP files the cost-benefit project stores (`research/sources/` keys
molit_2026_transport_appraisal and hira_2021_pharmacoeconomic): the start of each output agrees, ignoring
whitespace and cell brackets, with all of the file's PrvText stream (616 and 728 characters), the preview Hancom's
own program wrote, which also renders code 31 as a space. Nothing runs this tool unasked, so it is no control
(CORE rule 10).
"""

import argparse
import struct
import sys
import zlib
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import NamedTuple

CFB_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")
CHAIN_END = 0xFFFFFFFA  # a sector id at or above this ends a chain or marks a special sector
NO_ENTRY = 0xFFFFFFFF
PARA_TEXT = 67  # HWPTAG_BEGIN (16) + 51
WIDE_CONTROLS = frozenset((*range(1, 10), 11, 12, *range(14, 24)))  # eight UTF-16 code units each
CONTROL_TEXT = {9: "\t", 10: "\n", 24: "-", 30: " ", 31: " "}
ENCRYPTED_FLAGS = {0x2: "password-protected", 0x4: "a distribution document", 0x10: "DRM-protected"}


class NotReadable(Exception):
    """The file is not an HWP 5.0 document this reader can take text from."""


class Entry(NamedTuple):
    name: str
    kind: int  # 1 storage, 2 stream, 5 root
    left: int
    right: int
    child: int
    start: int
    size: int


def compound_streams(data: bytes) -> dict[str, bytes]:
    """Every stream of an OLE compound file, by its path, such as 'BodyText/Section0'."""
    if data[:8] != CFB_MAGIC:
        raise NotReadable("not an OLE compound file, so not HWP 5.0 (.hwpx is a zip of XML; HWP 3.0 is another format)")
    sector_size = 1 << struct.unpack_from("<H", data, 0x1E)[0]
    mini_size = 1 << struct.unpack_from("<H", data, 0x20)[0]
    (first_directory,) = struct.unpack_from("<I", data, 0x30)
    cutoff, first_minifat, minifat_sectors, first_difat, difat_sectors = struct.unpack_from("<5I", data, 0x38)
    per_sector = sector_size // 4

    def sector(i: int) -> bytes:
        return data[(i + 1) * sector_size : (i + 2) * sector_size]

    def chain(start: int, table: Sequence[int]) -> list[int]:
        ids: list[int] = []
        while start < CHAIN_END:
            if start >= len(table) or len(ids) > len(table):
                raise NotReadable("a broken sector chain in the compound file")
            ids.append(start)
            start = table[start]
        return ids

    difat: list[int] = list(struct.unpack_from("<109I", data, 0x4C))
    at = first_difat
    for _ in range(difat_sectors):
        ids: tuple[int, ...] = struct.unpack(f"<{per_sector}I", sector(at))
        difat += ids[:-1]
        at = ids[-1]
    fat: list[int] = []
    for i in difat:
        if i < CHAIN_END:
            fat += struct.unpack(f"<{per_sector}I", sector(i))

    def big_stream(start: int) -> bytes:
        return b"".join(sector(i) for i in chain(start, fat))

    directory = big_stream(first_directory)
    entries: list[Entry] = []
    for at in range(0, len(directory) - 127, 128):
        e = directory[at : at + 128]
        (name_length,) = struct.unpack_from("<H", e, 64)
        left, right, child = struct.unpack_from("<3I", e, 68)
        (start,) = struct.unpack_from("<I", e, 116)
        (size,) = struct.unpack_from("<Q", e, 120)
        if sector_size == 512:  # version 3: the size's high half may hold junk
            size &= 0xFFFFFFFF
        name = e[: max(name_length - 2, 0)].decode("utf-16le", "replace")
        entries.append(Entry(name, e[66], left, right, child, start, size))
    root = entries[0]
    ministream = big_stream(root.start)[: root.size]
    minifat_bytes = big_stream(first_minifat) if minifat_sectors else b""
    minifat: tuple[int, ...] = struct.unpack(f"<{len(minifat_bytes) // 4}I", minifat_bytes)

    def stream(e: Entry) -> bytes:
        if e.size < cutoff:
            return b"".join(ministream[i * mini_size : (i + 1) * mini_size] for i in chain(e.start, minifat))[: e.size]
        return big_stream(e.start)[: e.size]

    found: dict[str, Entry] = {}

    def walk(i: int, parent: str) -> None:
        if i == NO_ENTRY:
            return
        e = entries[i]
        walk(e.left, parent)
        if e.kind == 2:
            found[parent + e.name] = e
        elif e.kind == 1:
            walk(e.child, f"{parent}{e.name}/")
        walk(e.right, parent)

    walk(root.child, "")
    return {path: stream(e) for path, e in found.items()}


def records(raw: bytes, tag: int) -> Iterator[bytes]:
    """The bodies of the records with this tag in an HWP record stream."""
    at = 0
    while at + 4 <= len(raw):
        (head,) = struct.unpack_from("<I", raw, at)
        at += 4
        size = head >> 20
        if size == 0xFFF:
            (size,) = struct.unpack_from("<I", raw, at)
            at += 4
        if head & 0x3FF == tag:
            yield raw[at : at + size]
        at += size


def paragraph(body: bytes) -> str:
    """One paragraph-text record as text."""
    out = bytearray()
    at = 0
    while at + 2 <= len(body):
        (code,) = struct.unpack_from("<H", body, at)
        if code >= 32:
            out += body[at : at + 2]
            at += 2
        else:
            out += CONTROL_TEXT.get(code, "").encode("utf-16le")
            at += 16 if code in WIDE_CONTROLS else 2
    return out.decode("utf-16le", "replace")


def _unreadable(e: Exception) -> NotReadable:
    return NotReadable(f"a damaged file, or one this reader cannot follow: {type(e).__name__}: {e}")


def hwp_streams(data: bytes) -> dict[str, bytes]:
    """The streams of an HWP 5.0 compound file, by path; raises only NotReadable."""
    try:
        streams = compound_streams(data)
    except NotReadable:
        raise
    except Exception as e:
        raise _unreadable(e) from e
    header = streams.get("FileHeader", b"")
    if not header.startswith(b"HWP Document File") or len(header) < 40:
        raise NotReadable("a compound file with no HWP 5.0 FileHeader")
    return streams


def hwp_text(data: bytes) -> str:
    """The paragraph text of an HWP 5.0 document, one line per paragraph; raises only NotReadable."""
    streams = hwp_streams(data)
    try:
        return _text(streams)
    except NotReadable:
        raise
    except Exception as e:
        raise _unreadable(e) from e


def _text(streams: dict[str, bytes]) -> str:
    (flags,) = struct.unpack_from("<I", streams["FileHeader"], 36)
    encrypted = [why for bit, why in ENCRYPTED_FLAGS.items() if flags & bit]
    if encrypted:
        raise NotReadable(f"the document is {' and '.join(encrypted)}, so its text is encrypted")
    prefix = "BodyText/Section"
    sections = sorted((p for p in streams if p.startswith(prefix)), key=lambda p: int(p.removeprefix(prefix)))
    paragraphs: list[str] = []
    for path in sections:
        raw = zlib.decompress(streams[path], -15) if flags & 1 else streams[path]
        paragraphs += [paragraph(body) for body in records(raw, PARA_TEXT)]
    if not any(p.strip() for p in paragraphs):
        raise NotReadable("no paragraph text in its BodyText sections")
    return "\n".join(paragraphs) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hwp2txt.py",
        description="Write the text of an HWP 5.0 file as UTF-8, a line per paragraph (the file's header says more).",
    )
    parser.add_argument("hwp", type=Path, help="the .hwp file to read")
    parser.add_argument("txt", type=Path, help="the text file to write")
    args = parser.parse_args(argv)
    source: Path = args.hwp
    target: Path = args.txt
    try:
        text = hwp_text(source.read_bytes())
    except NotReadable as e:
        print(f"hwp2txt: {source}: {e}; nothing written", file=sys.stderr)
        return 2
    target.write_text(text, encoding="utf-8")
    print(f"{target}: {len(text)} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
