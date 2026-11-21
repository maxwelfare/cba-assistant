"""tools/source_store.py: stores one source in sources/<key>/ beside its index, as CORE 2.2 asks.

A seat that stores a source calls this command rather than writing its own: fetchers running at once that each
write their own storing script end with as many forms of source.json as scripts, and with folders left empty.

WHAT IT WRITES, in DIR/KEY/: original.<ext>, the bytes as they came; text.txt; and source.json with the fields of
the cost-benefit project's research/sources/page_2021_prisma (key, citation, doi, url, media_type, sha256, licence,
fetched, text_method) and `how`, the command that got the bytes. The index entry is the calling seat's to write.

WHERE THE BYTES COME FROM. By default the polite fetch of tools/host_cooldown.py, so a host closed on the ledger is
refused before anything is sent and a 429 closes exactly the host that sent it; with --from-file, a file already on
disk (a salvaged copy, one the owner saved), URL then being the address it came from.

THE TEXT, by the bytes' type: PDF by plain `pdftotext` (`-layout` mixes columns and splits sentences); HTML by the
standard library's parser, with script, style and noscript dropped and block ends kept as line breaks, in the
charset the page declares, its label read by the WHATWG Encoding Standard's table as a browser reads it (UTF-8
when it declares none or one not in the table); XML by its text content, block elements as line breaks, and, in
XML whose DOCTYPE names an external DTD, the HTML5 named entities (`&nbsp;`, `&frac13;`) resolved from Python's
html.entities.html5, the DTD not being read. Where expat cannot use the encoding the XML declaration names
(a multi-byte one such as EUC-KR or Shift_JIS, a name Python does not know, a UTF-16 label on an ASCII stream), the
label is read by the HTML Standard's "get an XML encoding" (whatwg_html_parsing, 13.2.3.2) and the Encoding
Standard's table, the bytes decoded by its codec, and the text_method says so. Where that gives no codec (no label
read, a label not in the table, one the table maps to its replacement encoding), the XML extract refuses, where the
HTML path reads UTF-8 and says so: a missing value refuses where it enters (CORE rule 3), and on non-ASCII text a
UTF-8 guess garbles it silently. HWP 5.0 by tools/hwp2txt.py, the file told by its bytes, whatever its address:
a compound file (the magic d0cf11e0a1b11ae1) holding "HWP Document File", the start of an HWP FileHeader, at an
offset that is a multiple of 64, where every stream of a compound file begins; no compound file is parsed to type
it. A DOC, XLS, PPT or .msg that embeds an HWP document or attachment, or holds that phrase at such an offset, is
typed HWP too: it is stored as original.hwp, the reader refuses it (a well-formed one with "NotReadable: a compound
file with no HWP 5.0 FileHeader"), and the command exits 2, so a seat that sees that refusal knows the type came
from the bytes and may be wrong. Plain text as it is. For any other type (DOCX, a spreadsheet), or where an extract
fails (an HWP file that reader refuses, XML nested too deep, any other error, which is printed), the original and
source.json are stored with text_method "none", no text.txt is left, and the command exits 2: the seat makes
text.txt from the original by another tool and writes in text_method how; on a fill's exit 2 (below) the seat
writes nothing in the record. An interrupt during the extract leaves the
same, and is raised again. A scanned PDF is stored at exit 0, since pdftotext succeeds on it, with a text.txt of form
feeds: the seat replaces text.txt by another tool and writes in text_method how.

IT REFUSES, before any request, a KEY whose folder holds any file but source.json alone (exit 1): the library comes
first, and a stored original is never overwritten.

A FOLDER THAT HOLDS ONLY ITS RECORD is filled, by the same command: the record governs, and the URL, --citation,
--doi and --licence given are not used. The record must be a JSON object in UTF-8 with a `sha256` of 64 lowercase hex
digits and a non-empty `url` or `address`, or it cannot be filled (exit 1, before any request). The bytes come from
the record's `url`, else its `address`, by the polite fetch, or from --from-file; their sha256 must be the record's,
they are typed by the record's address, extracted and judged for a wall as in any store. A fill writes its files in
its own DIR/.KEY.<random> and links them into DIR/KEY by os.link, which refuses an existing name. The record is never
written. The method the record names is the first string of text_method, text_command, text_made_by that is neither
empty nor "none", the store's word for no text.
  Exit 0: the store's extract is by the method the record names; original.<ext> and text.txt are linked in.
  Exit 2: the extract gave no text, or is by another method, or the record names none; original.<ext> alone is
linked in, and the seat makes text.txt by the method the record names and writes nothing in the record; where that
method cannot be run again, or the record names none, the seat reports it.
  Exit 1: bytes whose sha256 is not the record's, a wall, a record that cannot be filled, or a link that meets an
existing name (it removes what it linked and its folder and says so as a store does); nothing is stored and the
record is left as it was. Bytes that cannot be had end a fill as they end a store (exit 1, or 3 when the polite
fetch refused the URL or a redirect hop unsent). An error or interrupt before the first link removes its folder and is
raised.

Otherwise it writes the store in a folder of its own beside the key's,
DIR/.KEY.<random>, and publishes it as DIR/KEY by one rename, which replaces a missing or empty folder and fails
onto one holding files; a seat whose rename finds the key stored removes its own folder, says so with the sha256 of
the bytes it discards, and exits 1, so of two seats storing one KEY at once one store survives whole. When the bytes
cannot be had, or anything fails before the original is in place, it removes its own folder and nothing else (exit
1, or 3 when the polite fetch refused the URL or a redirect hop unsent). It does the same, exit 1, for a page a host serves in
place of a work: an extract of any type but PDF under WALL_MAX characters that holds a wall phrase, or an HTML
extract with fewer than WALL_MIN characters other than white space; it prints each reason, the extract it judged,
the URL and the route. Otherwise, once the original is in place, it publishes whatever the extract does. A publish
that fails for any other reason leaves its folder, prints its path, and raises the error. A kill leaves its
.KEY.<random> folder, which blocks nothing; git does not ignore it, so it shows as untracked and is never to be
committed. Anyone may remove it once no store of KEY is running, since removing one while its store runs makes that
store fail and, if the removal overlaps the publish, can delete files from the newly published key folder. Any other
extract under 500 characters is kept and said, since a wall the rules miss, a login page or an abstract is the usual
cause.

A SECOND COPY BESIDE A STORED ONE, by --beside TAG --why "...", for a stored copy found wrong (the wrong edition, a
text layer the quote checker cannot read). It cannot replace the held copy, since tools/quotes.py accepts a match in
any .txt of the folder and a quote may have come from it. It runs only on a folder holding an original (a file
original.<ext>); on any other, a missing or empty one or one holding its record alone, it refuses (exit 1) and says to
store without it. TAG is lower-case letters, digits and `_`, or it refuses (exit 1). It stores as a store does (the
polite fetch or --from-file, the typing, the extract, the wall judgement) in its own DIR/.KEY.<random>, under the
names original_TAG.<ext> and text_TAG.txt, so that its text_method names them; its source.json adds `supersedes`, the
held original's file name, and `why`. It then links the three into DIR/KEY, the record as source_TAG.json, by os.link,
which refuses an existing name. Every held file is left byte for byte. A link that meets an existing name (the TAG used before) removes what it
linked and its folder (exit 1), as does an interrupt during the extract, which is raised again. Exits 0, 1, 2 and 3
otherwise as a store's; at exit 2 no text_TAG.txt is linked.

    cd shared && ../.venv/bin/python -m tools.source_store KEY URL --to DIR --citation "..." \\
        [--doi DOI] [--licence "..."] [--from-file PATH] [--beside TAG --why "..."]
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import html.entities
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.parsers.expat import errors as expat_errors
from collections.abc import Callable
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import NamedTuple, cast
from urllib.parse import urlsplit

from tools import host_cooldown, hwp2txt

HWP_SIGNATURE = b"HWP Document File"   # an HWP 5.0 FileHeader stream begins with it (tools/hwp2txt.py)

Fetch = Callable[..., int]   # (url, out, by=...) -> exit code, as host_cooldown.fetch
SHORT = 500
# A wall is told by what it says to its visitor, never by a topic word. Counted by the shared coordinator on 2026-11-15
# over 5,728 extracts of four projects' sources (notes/briefs/source_store_walls.md, 3.3): under 2,000 characters the
# rows below stand in 22 extracts, each a wall, and in no real text; under 100 characters other than white space no
# extract is a work, the shortest real text being 130 characters of JSON. A false refusal is corrected here, in a row
# or a bound: there is no override.
WALL_MAX = 2000   # characters, counted as the stored-text count is; the phrase rule reads extracts shorter than this
WALL_MIN = 100    # characters other than white space; an HTML extract with fewer holds no text of a work
WALL_PHRASES = (   # folded as _fold folds, one row each
    "just a moment...",
    "enable javascript and cookies to continue",
    "checking your browser",
    "you don't have permission to access",
    "sorry, you have been blocked",
    "complete the captcha",
    "cookies must be enabled",
    "validating browser",
    "please enable js and disable any ad blocker",
    "verification required!",
    "incapsula incident id",
    "a required part of this site couldn't load",
)
HTML_SKIP = frozenset({"script", "style", "noscript", "template", "svg"})
HTML_BLOCK = frozenset({"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article",
                        "table", "ul", "ol", "dl", "dt", "dd", "blockquote", "pre", "header", "footer", "main",
                        "aside", "figure", "figcaption", "caption", "hr"})
XML_BLOCK = frozenset({"p", "para", "title", "article-title", "sec", "abstract", "caption", "label", "list-item", "li",
                       "tr", "td", "th", "ref", "fn", "fig", "table-wrap", "div", "head"})
# A JATS file names its DTD and uses its entities (&nbsp;, &frac13;); expat does not read an external DTD, so the
# HTML5 named character references stand in for the ISO 8879 sets the JATS DTDs declare.
XML_ENTITIES = {k.rstrip(";"): v for k, v in html.entities.html5.items()}


class _HtmlText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in HTML_SKIP:
            self.skip += 1
        elif tag in HTML_BLOCK:
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in HTML_SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in HTML_BLOCK:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def _tidy(text: str) -> str:
    lines = [re.sub(r"[ \t\r\f\v ]+", " ", line).strip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


# The Encoding Standard's label table (library/sources/whatwg_encoding, section 4.2): each encoding, the Python
# codec that decodes it, and its labels. GBK's decoder is gb18030's (section 10.1.1); Big5, Shift_JIS and EUC-KR
# take Python's big5hkscs, cp932 and cp949, which decode the Standard's tests where big5, shift_jis and euc_kr do
# not; UTF-16BE/LE read as UTF-8 and x-user-defined as windows-1252, as the HTML Standard's prescan sets them
# (whatwg_html_parsing, 13.2.3.2). The replacement encoding has no codec: such a page is read as UTF-8 and said.
ENCODINGS: tuple[tuple[str, str | None, str], ...] = (
    ("UTF-8", "utf-8", "unicode-1-1-utf-8 unicode11utf8 unicode20utf8 utf-8 utf8 x-unicode20utf8"),
    ("IBM866", "cp866", "866 cp866 csibm866 ibm866"),
    ("ISO-8859-2", "iso8859_2", "csisolatin2 iso-8859-2 iso-ir-101 iso8859-2 iso88592 iso_8859-2 iso_8859-2:1987 l2 "
                                "latin2"),
    ("ISO-8859-3", "iso8859_3", "csisolatin3 iso-8859-3 iso-ir-109 iso8859-3 iso88593 iso_8859-3 iso_8859-3:1988 l3 "
                                "latin3"),
    ("ISO-8859-4", "iso8859_4", "csisolatin4 iso-8859-4 iso-ir-110 iso8859-4 iso88594 iso_8859-4 iso_8859-4:1988 l4 "
                                "latin4"),
    ("ISO-8859-5", "iso8859_5", "csisolatincyrillic cyrillic iso-8859-5 iso-ir-144 iso8859-5 iso88595 iso_8859-5 "
                                "iso_8859-5:1988"),
    ("ISO-8859-6", "iso8859_6", "arabic asmo-708 csiso88596e csiso88596i csisolatinarabic ecma-114 iso-8859-6 "
                                "iso-8859-6-e iso-8859-6-i iso-ir-127 iso8859-6 iso88596 iso_8859-6 iso_8859-6:1987"),
    ("ISO-8859-7", "iso8859_7", "csisolatingreek ecma-118 elot_928 greek greek8 iso-8859-7 iso-ir-126 iso8859-7 "
                                "iso88597 iso_8859-7 iso_8859-7:1987 sun_eu_greek"),
    ("ISO-8859-8", "iso8859_8", "csiso88598e csisolatinhebrew hebrew iso-8859-8 iso-8859-8-e iso-ir-138 iso8859-8 "
                                "iso88598 iso_8859-8 iso_8859-8:1988 visual"),
    ("ISO-8859-8-I", "iso8859_8", "csiso88598i iso-8859-8-i logical"),
    ("ISO-8859-10", "iso8859_10", "csisolatin6 iso-8859-10 iso-ir-157 iso8859-10 iso885910 l6 latin6"),
    ("ISO-8859-13", "iso8859_13", "iso-8859-13 iso8859-13 iso885913"),
    ("ISO-8859-14", "iso8859_14", "iso-8859-14 iso8859-14 iso885914"),
    ("ISO-8859-15", "iso8859_15", "csisolatin9 iso-8859-15 iso8859-15 iso885915 iso_8859-15 l9"),
    ("ISO-8859-16", "iso8859_16", "iso-8859-16"),
    ("KOI8-R", "koi8_r", "cskoi8r koi koi8 koi8-r koi8_r"),
    ("KOI8-U", "koi8_u", "koi8-ru koi8-u"),
    ("macintosh", "mac_roman", "csmacintosh mac macintosh x-mac-roman"),
    ("windows-874", "cp874", "dos-874 iso-8859-11 iso8859-11 iso885911 tis-620 windows-874"),
    ("windows-1250", "cp1250", "cp1250 windows-1250 x-cp1250"),
    ("windows-1251", "cp1251", "cp1251 windows-1251 x-cp1251"),
    ("windows-1252", "cp1252", "ansi_x3.4-1968 ascii cp1252 cp819 csisolatin1 ibm819 iso-8859-1 iso-ir-100 "
                               "iso8859-1 iso88591 iso_8859-1 iso_8859-1:1987 l1 latin1 us-ascii windows-1252 "
                               "x-cp1252"),
    ("windows-1253", "cp1253", "cp1253 windows-1253 x-cp1253"),
    ("windows-1254", "cp1254", "cp1254 csisolatin5 iso-8859-9 iso-ir-148 iso8859-9 iso88599 iso_8859-9 "
                               "iso_8859-9:1989 l5 latin5 windows-1254 x-cp1254"),
    ("windows-1255", "cp1255", "cp1255 windows-1255 x-cp1255"),
    ("windows-1256", "cp1256", "cp1256 windows-1256 x-cp1256"),
    ("windows-1257", "cp1257", "cp1257 windows-1257 x-cp1257"),
    ("windows-1258", "cp1258", "cp1258 windows-1258 x-cp1258"),
    ("x-mac-cyrillic", "mac_cyrillic", "x-mac-cyrillic x-mac-ukrainian"),
    ("GBK", "gb18030", "chinese csgb2312 csiso58gb231280 gb2312 gb_2312 gb_2312-80 gbk iso-ir-58 x-gbk"),
    ("gb18030", "gb18030", "gb18030"),
    ("Big5", "big5hkscs", "big5 big5-hkscs cn-big5 csbig5 x-x-big5"),
    ("EUC-JP", "euc_jp", "cseucpkdfmtjapanese euc-jp x-euc-jp"),
    ("ISO-2022-JP", "iso2022_jp", "csiso2022jp iso-2022-jp"),
    ("Shift_JIS", "cp932", "csshiftjis ms932 ms_kanji shift-jis shift_jis sjis windows-31j x-sjis"),
    ("EUC-KR", "cp949", "cseuckr csksc56011987 euc-kr iso-ir-149 korean ks_c_5601-1987 ks_c_5601-1989 ksc5601 "
                        "ksc_5601 windows-949"),
    ("replacement", None, "csiso2022kr hz-gb-2312 iso-2022-cn iso-2022-cn-ext iso-2022-kr replacement"),
    ("UTF-16BE", "utf-8", "unicodefffe utf-16be"),
    ("UTF-16LE", "utf-8", "csunicode iso-10646-ucs-2 ucs-2 unicode unicodefeff utf-16 utf-16le"),
    ("x-user-defined", "cp1252", "x-user-defined"),
)
LABELS = {label: (name, codec) for name, codec, labels in ENCODINGS for label in labels.split()}


def _charset(data: bytes) -> tuple[str, str]:
    """The codec for the charset the page declares, and a clause saying how it was chosen."""
    m = re.search(rb"""charset\s*=\s*["']?[\t\n\f\r ]*([A-Za-z0-9_.:-]+)""", data[:4096], re.IGNORECASE)
    if not m:
        return "utf-8", "decoded as utf-8: the page declares no charset"
    label = m.group(1).decode("ascii")
    if label.lower() not in LABELS:
        return "utf-8", f'decoded as utf-8: the declared label "{label}" is not a label of the Encoding Standard'
    name, codec = LABELS[label.lower()]
    if codec is None:
        return "utf-8", (f'decoded as utf-8: the Encoding Standard maps the declared label "{label}" to its '
                         "replacement encoding")
    return codec, _decoded_as(codec, name, label)


# The HTML Standard reads these encodings as others (whatwg_html_parsing, 13.2.3.2), and LABELS gives that codec.
READ_AS = {"UTF-16BE": "UTF-8", "UTF-16LE": "UTF-8", "x-user-defined": "windows-1252"}


def _decoded_as(codec: str, name: str, label: str) -> str:
    if name in READ_AS:
        return (f'decoded as {codec}: the declared label "{label}" names {name}, which the HTML Standard reads as '
                f"{READ_AS[name]}")
    return (f"decoded as {codec}, the codec for {name}, the Encoding Standard's encoding for the declared label "
            f'"{label}"')


def html_text(data: bytes) -> str:
    parser = _HtmlText()
    parser.feed(data.decode(_charset(data)[0], errors="replace"))
    parser.close()
    return _tidy("".join(parser.parts))


def _xml(data: bytes | str) -> ET.Element:
    parser = ET.XMLParser()   # a fresh one each time: an XMLParser cannot parse again after close
    parser.entity.update(XML_ENTITIES)
    parser.feed(data)
    return parser.close()


# Expat's ways of refusing the encoding an XML declaration names: ValueError for a multi-byte one, LookupError for
# a name Python does not know, and these ParseError codes for one it knows but cannot apply (UTF-16 on ASCII bytes,
# EBCDIC).
XML_ENCODING_CODES = frozenset({expat_errors.codes[expat_errors.XML_ERROR_UNKNOWN_ENCODING],
                                expat_errors.codes[expat_errors.XML_ERROR_INCORRECT_ENCODING]})


def _encoding_refused(e: Exception) -> bool:
    return isinstance(e, (ValueError, LookupError)) or (isinstance(e, ET.ParseError) and e.code in XML_ENCODING_CODES)


def _xml_label(data: bytes) -> str | None:
    """The label an XML declaration names, by the HTML Standard's "get an XML encoding"; None for its failure."""
    end = data.find(b">")
    if not data.startswith(b"<?xml") or end < 0:
        return None
    i = data.find(b"encoding", 0, end)
    if i < 0:
        return None
    i += len(b"encoding")
    while i < len(data) and data[i] <= 0x20:
        i += 1
    if data[i:i + 1] != b"=":
        return None
    i += 1
    while i < len(data) and data[i] <= 0x20:
        i += 1
    quote = data[i:i + 1]
    if quote not in (b'"', b"'"):
        return None
    close = data.find(quote, i + 1)
    if close < 0 or any(b <= 0x20 for b in data[i + 1:close]):
        return None
    return data[i + 1:close].decode("latin-1")   # isomorphic decode


def _xml_declared(data: bytes) -> tuple[ET.Element, str]:
    """The parse of `data` decoded by the codec for its declared label, and a clause saying how; ValueError if none."""
    label = _xml_label(data)
    if label is None:
        raise ValueError('expat cannot use the declared encoding, and no label could be read from the XML '
                         'declaration by the HTML Standard\'s "get an XML encoding"')
    if label.lower() not in LABELS:
        raise ValueError(f'expat cannot use the declared label "{label}", and it is not a label of the Encoding '
                         "Standard")
    name, codec = LABELS[label.lower()]
    if codec is None:
        raise ValueError(f'the Encoding Standard maps the declared label "{label}" to its replacement encoding, '
                         "which decodes to no text")
    # A str is parsed as UTF-8 whatever its declaration names, so the declaration needs no edit.
    return _xml(data.decode(codec, errors="replace")), (
        f'{_decoded_as(codec, name, label)}, the label read by the HTML Standard\'s "get an XML encoding" since expat '
        "cannot use it")


def xml_text(data: bytes) -> tuple[str, str]:
    """The text of `data`, and a clause saying how it was decoded where expat could not use its declared encoding."""
    try:
        root, clause = _xml(data), ""
    except (ET.ParseError, ValueError, LookupError) as e:
        if not _encoding_refused(e):
            raise
        root, clause = _xml_declared(data)
    parts: list[str] = []

    def walk(e: ET.Element) -> None:
        parts.append(e.text or "")
        for child in e:
            walk(child)
            parts.append(child.tail or "")
        if e.tag.rsplit("}", 1)[-1] in XML_BLOCK:
            parts.append("\n")

    walk(root)
    return _tidy("".join(parts)), clause


def kind(data: bytes, url: str) -> tuple[str, str]:
    """The file extension and media type of `data`, from its bytes first and the address's suffix second."""
    head = data[:4096].lstrip().lower()
    if data.startswith(b"%PDF"):
        return "pdf", "application/pdf"
    if data.startswith(hwp2txt.CFB_MAGIC):   # every compound-file stream begins at a multiple of 64 ([MS-CFB] 2.2)
        at = data.find(HWP_SIGNATURE)
        while at != -1:
            if at % 64 == 0:
                return "hwp", "application/x-hwp"   # IANA registers none; freedesktop's name
            at = data.find(HWP_SIGNATURE, at + 1)
    if head.startswith(b"<!doctype html") or b"<html" in head:
        return "html", "text/html"
    if head.startswith(b"<"):
        try:
            _xml(data)
        except (ET.ParseError, ValueError, LookupError) as e:   # XML whose declared encoding expat refuses is XML
            if not _encoding_refused(e):
                return "html", "text/html"
        return "xml", "application/xml"
    suffix = PurePosixPath(urlsplit(url).path).suffix.lstrip(".").lower()
    guessed = mimetypes.guess_type("x." + suffix)[0] if suffix else None
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return suffix or "bin", guessed or "application/octet-stream"
    return suffix or "txt", guessed or "text/plain"


def extract(ext: str, data: bytes, original: Path, text: Path) -> str | None:
    """Write text.txt for a known type and return how it was made; None for a type it has no extractor for."""
    if ext == "pdf":
        try:
            done = subprocess.run(["pdftotext", str(original), str(text)], capture_output=True, text=True)
        except FileNotFoundError:
            return None
        return f"pdftotext {original.name} {text.name}" if done.returncode == 0 and text.exists() else None
    if ext == "hwp":
        text.write_text(hwp2txt.hwp_text(data), encoding="utf-8")
        return "tools/hwp2txt.py hwp_text: a line per paragraph"
    if ext == "xml":
        body, clause = xml_text(data)
        text.write_text(body, encoding="utf-8")
        return ("tools/source_store.py xml_text: the text content, block elements as line breaks, named entities "
                "not declared in the file resolved from Python's html.entities.html5 (the DTD is not read)"
                + (f"; {clause}" if clause else ""))
    if ext == "html":
        text.write_text(html_text(data), encoding="utf-8")
        return ("tools/source_store.py html_text: script, style and noscript dropped, block ends as line breaks, "
                + _charset(data)[1])
    try:
        text.write_text(_tidy(data.decode("utf-8")), encoding="utf-8")
    except UnicodeDecodeError:
        return None
    return "tools/source_store.py: the original decoded as UTF-8, white space tidied"


def _fold(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("\u2019", "'").replace("\u2026", "..."))


def wall_reasons(ext: str, text: str) -> list[str]:
    """Why `text`, the extract of an original of type `ext`, is a page served in place of a work; empty if it is not."""
    reasons: list[str] = []
    if ext != "pdf" and len(text) < WALL_MAX:
        folded = _fold(text)
        reasons += [f'a wall phrase: "{row}"' for row in WALL_PHRASES if row in folded]
    if ext == "html":
        solid = len(re.sub(r"\s", "", text))
        if solid < WALL_MIN:
            reasons.append(f"no text of a work: {solid} characters other than white space, under {WALL_MIN}")
    return reasons


def _utc(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _refuse(key: str, folder: Path) -> None:
    print(f"{key} is already stored in {folder}: the library comes first, and a stored original is never "
          "overwritten. Compare the bytes by hand if this copy differs, and report it.")


def _workdir(to: Path, key: str) -> Path:
    """A new folder of this seat's own beside the key's, made by a plain mkdir so it has a mkdir's mode."""
    while True:
        work = to / f".{key}.{secrets.token_hex(8)}"
        try:
            work.mkdir()
        except FileExistsError:
            continue
        return work


class Record(NamedTuple):
    """What a fill takes from a record alone in its folder."""
    sha256: str
    address: str          # its url, else its address
    method: str | None    # the first string of text_method, text_command, text_made_by that is neither "" nor "none"
    fetched: str | None   # its fetched_utc, else its fetched


def _record(path: Path) -> Record | str:
    """The record at `path` as a fill reads it, or why it cannot be filled."""
    try:
        obj: object = json.loads(path.read_bytes().decode("utf-8"))
    except ValueError as e:   # UnicodeDecodeError and JSONDecodeError both are
        return f"it is not JSON in UTF-8 ({e})"
    if not isinstance(obj, dict):
        return "it is not a JSON object"
    rec = cast(dict[str, object], obj)

    def first(*fields: str, empty: tuple[str, ...] = ("",)) -> str | None:
        return next((v for f in fields if isinstance(v := rec.get(f), str) and v not in empty), None)

    sha = rec.get("sha256")
    if not (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha)):
        return "it holds no sha256 of 64 lowercase hex digits, and nothing else shows the bytes are its work"
    address = first("url", "address")
    if address is None:
        return "it names neither a url nor an address to fetch its bytes from"
    method = first("text_method", "text_command", "text_made_by", empty=("", "none"))   # "none": the store's no text
    return Record(sha, address, method, first("fetched_utc", "fetched"))


def _short(chars: int) -> str:
    return (f"; under {SHORT} characters, so check it is the work and not a wall, a login page or an abstract"
            if chars < SHORT else "")


def store(key: str, url: str, to: Path, citation: str, *, doi: str | None = None, licence: str = "not stated",
          from_file: Path | None = None, fetch: Fetch = host_cooldown.fetch, beside: str | None = None,
          why: str = "") -> int:
    folder = to / key
    held = sorted(p.name for p in folder.iterdir()) if folder.exists() else []
    fill: Record | None = None
    supersedes: str | None = None
    if beside is not None:
        if not re.fullmatch(r"[a-z0-9_]+", beside):
            print(f"--beside {beside!r}: a TAG is lower-case letters, digits and _ only; nothing is stored.")
            return 1
        supersedes = next((n for n in held if n.startswith("original.")), None)
        if supersedes is None:
            print(f"{folder} holds no original to add a copy beside; store {key} without --beside.")
            return 1
    elif held == ["source.json"]:
        got = _record(folder / "source.json")
        if isinstance(got, str):
            print(f"{key}'s record in {folder} cannot be filled: {got}. Nothing is fetched and the record is left as "
                  "it was.")
            return 1
        fill = got
    elif held:
        _refuse(key, folder)
        return 1
    address = url if fill is None else fill.address   # where the bytes are fetched from, and what types them
    source = str(from_file) if fill is not None and from_file is not None else address   # named in what is printed
    to.mkdir(parents=True, exist_ok=True)
    work = _workdir(to, key)
    part = work / "original.part"
    try:
        if from_file is not None:
            shutil.copyfile(from_file, part)
            fetched = _utc(datetime.fromtimestamp(from_file.stat().st_mtime, timezone.utc))
            how = f"copied from {from_file} (fetched is the file's modification time)"
        else:
            code = fetch(address, part, by=f"source_store {key}")
            if code != 0:
                shutil.rmtree(work)
                return code
            fetched = _utc(datetime.now(timezone.utc))
            how = f"python tools/host_cooldown.py fetch {address}"
        data = part.read_bytes()
        if not data:
            shutil.rmtree(work)
            print(f"{source} gave no bytes; nothing is stored.")
            return 1
        digest = hashlib.sha256(data).hexdigest()
        if fill is not None and digest != fill.sha256:
            shutil.rmtree(work)
            dated = f" of {fill.fetched}" if fill.fetched else ""
            print(f"{source} gave bytes of sha256 {digest}, not the sha256 {fill.sha256} in {folder / 'source.json'}; "
                  f"nothing is stored and the record is left as it was. Store again by --from-file a copy holding "
                  f"the record's bytes (an archived copy of {fill.address}{dated}), or report both.")
            return 1
        ext, media = kind(data, address)
        tag = "" if beside is None else f"_{beside}"   # a beside store makes its files under their tagged names
        original = work / f"original{tag}.{ext}"
        meta = {"key": key, "citation": citation, "doi": doi, "url": url, "media_type": media, "sha256": digest,
                "licence": licence, "fetched": fetched, "text_method": "none", "how": how}
        if supersedes is not None:
            meta |= {"supersedes": supersedes, "why": why}
        record = work / "source.json"
        if fill is None:
            record.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        part.rename(original)
    except BaseException:
        shutil.rmtree(work, ignore_errors=True)
        raise
    # From here a store's original and its record are published whatever the extract does; an interrupt or any
    # other exception is raised again after the publish. A fill publishes nothing that is not as its record says.
    text = work / f"text{tag}.txt"
    method: str | None = None
    pending: BaseException | None = None
    try:
        try:
            method = extract(ext, data, original, text)
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
        if method is not None and fill is None:
            meta["text_method"] = method
            record.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    except BaseException as e:
        pending, method = e, None
    if fill is not None and pending is not None:
        shutil.rmtree(work, ignore_errors=True)
        raise pending
    if method is None:
        text.unlink(missing_ok=True)  # pdftotext can write part of text.txt and then fail
    elif pending is None:
        judged = text.read_text(encoding="utf-8")
        reasons = wall_reasons(ext, judged)
        if reasons:
            shutil.rmtree(work, ignore_errors=True)
            print(f"{source} gave a page in place of the work; nothing is stored.")
            for reason in reasons:
                print(f"  {reason}")
            print(f"The extract judged ({len(judged)} characters):\n{judged[:WALL_MAX]}")
            if fill is not None:
                print(f"{key}'s record is of this page: report it.")
            else:
                print("Store another copy by --from-file, or name the source for the owner's library browser. A wall "
                      "that is itself the evidence is quoted in its index entry's status. If this page is the work, "
                      "store nothing and report the reason above, so that the row or the floor is corrected.")
            return 1
    if fill is not None:
        return _fill(key, folder, work, original.name, digest, fill, method, source,
                     url if from_file is None and url != fill.address else None)
    if beside is not None:
        if pending is not None:
            shutil.rmtree(work, ignore_errors=True)
            raise pending
        names = [(original.name, original.name), ("source.json", f"source_{beside}.json")]
        names += [] if method is None else [(text.name, text.name)]
        if not _link(work, folder, names):
            print(f"{key} already holds a copy tagged {beside} in {folder}: nothing is stored; choose another TAG.")
            print(f"This copy, sha256 {digest}, is discarded; compare it with the sha256 in "
                  f"{folder / f'source_{beside}.json'}.")
            return 1
        print(f"stored beside {supersedes} in {folder}: " + ", ".join(new for _, new in names))
        if method is None:
            print(f"no text was made: make {folder / f'text_{beside}.txt'} from it by another tool and write how in "
                  f"source_{beside}.json's text_method.")
            return 2
        return 0
    try:
        os.rename(work, folder)
    except OSError as e:
        if e.errno not in (errno.ENOTEMPTY, errno.EEXIST):
            print(f"the publish of {work} as {folder} failed ({e}); the store is left in {work}.")
            raise
        shutil.rmtree(work, ignore_errors=True)
        _refuse(key, folder)
        _discarded(digest, folder)
        if pending is not None:
            raise pending
        return 1
    if pending is not None:
        raise pending
    stored = folder / original.name
    if method is None:
        print(f"stored {stored} ({media}) with no text: make {folder / 'text.txt'} from it by another tool and "
              "write how in source.json's text_method.")
        return 2
    chars = len((folder / "text.txt").read_text(encoding="utf-8"))
    print(f"stored {stored} and text.txt ({chars} characters){_short(chars)}")
    return 0


def _discarded(digest: str, folder: Path) -> None:
    print(f"This copy, sha256 {digest}, is discarded; compare it with the sha256 in {folder / 'source.json'}.")


def _link(work: Path, folder: Path, names: list[tuple[str, str]]) -> bool:
    """Link each (name in `work`, name in `folder`) by os.link and remove `work`; on a name already in `folder`, remove
    what was linked and `work` and return False. Any other failure leaves `work`, says so, and is raised."""
    linked: list[Path] = []
    try:
        for old, new in names:
            os.link(work / old, folder / new)
            linked.append(folder / new)
    except FileExistsError:
        for p in linked:
            p.unlink(missing_ok=True)
        shutil.rmtree(work, ignore_errors=True)
        return False
    except OSError as e:
        print(f"the publish of {work} into {folder} failed ({e}); the store is left in {work}.")
        raise
    shutil.rmtree(work)
    return True


def _fill(key: str, folder: Path, work: Path, name: str, digest: str, fill: Record, method: str | None, source: str,
          unused: str | None) -> int:
    """Publish `work`'s original `name` and text.txt into `folder`, which holds the record, where the record names the
    extract's method (exit 0); otherwise the original alone, the text left to the seat by the record's method (exit 2).
    `unused` is the URL given where a fetched fill did not use it."""
    alone = method is None or method != fill.method
    if not _link(work, folder, [(each, each) for each in ((name,) if alone else (name, "text.txt"))]):
        _refuse(key, folder)   # another seat's fill or store got there first
        _discarded(digest, folder)
        return 1
    not_used = f"; the URL given, {unused}, is not used" if unused else ""
    if alone:
        print(f"filled {key} in {folder} from {source}: {name} alone; the record is left as it was{not_used}.")
        named = f"names its text's method as {fill.method}" if fill.method else "names no method"
        made = (f"the store's extract of these bytes is by {method}" if method else
                f"the store's extract gave no text of {name}")
        route = ("make text.txt by the method the record names, and write nothing in the record; where that method "
                 "cannot be run again, report it" if fill.method else
                 "the record names no method, so no text it vouches for can be made: report it")
        print(f"{key}'s record {named}, and {made}: {route}.")
        return 2
    chars = len((folder / "text.txt").read_text(encoding="utf-8"))
    print(f"filled {key} in {folder} from {source}: {name} and text.txt ({chars} characters); the record is left as "
          f"it was{_short(chars)}{not_used}")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    p.add_argument("key")
    p.add_argument("url")
    p.add_argument("--to", type=Path, required=True, help="the sources/ folder beside the index")
    p.add_argument("--citation", required=True)
    p.add_argument("--doi")
    p.add_argument("--licence", default="not stated")
    p.add_argument("--from-file", type=Path)
    p.add_argument("--beside", metavar="TAG", help="add a second copy beside the held original, under this tag")
    p.add_argument("--why", help="with --beside: why the held copy is superseded")
    a = p.parse_args(argv)
    if (a.beside is None) != (a.why is None) or a.why == "":
        p.error("--beside and --why go together, and --why says why")
    return store(a.key, a.url, a.to, a.citation, doi=a.doi, licence=a.licence, from_file=a.from_file,
                 beside=a.beside, why=a.why or "")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
