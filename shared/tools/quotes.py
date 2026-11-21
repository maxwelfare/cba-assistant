"""tools/quotes.py: check quoted passages against stored source texts (notes/briefs/shared_quote_checker.md).

    .venv/bin/python -m tools.quotes text TEXT QUOTE [QUOTE ...]
    .venv/bin/python -m tools.quotes refs REFS SOURCES

Standard library only and importing no `tools` module, so a project may also load this file by its path
(`importlib.util.spec_from_file_location`). `normalise` and `quote_in` are the cost-benefit engine's
(`cost_benefit_engine/quotes.py`): `normalise` moved here unchanged in behaviour, and `quote_in` with the
number-boundary rule of rule 1 added. The public names are `normalise`, `plain_forms`, `quote_in`, `quote_in_forms`
and `main`; a name with a leading underscore may change without notice.

1. `normalise` and `quote_in` keep the engine's names and signatures. `normalise`: NFKC, except that a character of
   Unicode category No (superscripts, subscripts, vulgar fractions, circled digits) and the superscript and subscript
   plus and minus signs (U+207A, U+207B, U+208A, U+208B) are left as they are, so `10⁻⁶` never becomes `10-6` nor
   `10²` become `102`; every dash and minus
   sign (U+2010 to U+2015, U+2212) made a hyphen-minus and curly single and double quote marks made straight; a run of soft
   hyphens (U+00AD) removed unless it stands between two digits; a hyphen at a line end joined when the characters
   before the hyphen and after the white space are both letters, and otherwise kept with the line break and the white
   space about it removed, so no rule deletes a character between two digits or joins two digit runs; white space
   runs collapsed to one space. Case, letters, digits and word order stay exact. `quote_in`: `...` (or
   `[...]`) splits the quote into parts found in order, each after the end of the one before; spaces beside the
   scripts of `_UNRELIABLE_SPACING` removed; a quote with no part is not found. It is case-sensitive and strips no tag.
   The text is made plain two ways, as the engine's project ruled on 2026-11-16, since a hyphen at a line end may
   break a word or a compound: joined, as `normalise` makes it; and kept, the same but with each such hyphen between
   letters kept and the line break and the white space about it removed. Where the two are equal the text has one plain form. A quote
   is found when every part is found in the joined form, or every part in the kept form; the quote itself is made
   plain by `normalise`. `plain_forms(text)` returns the text's plain forms, joined first, then kept, as one element
   when the two are equal; `quote_in_forms(quote, forms)` is `quote_in` given forms already made, and
   `quote_in(quote, text)` is `quote_in_forms(quote, plain_forms(text))`. A caller that checks many quotes against
   one text makes its forms once with `plain_forms`, not a cache of `normalise`, which loses the kept form.
   `quote_in` adds the number-boundary rule the engine's project ruled on 2026-11-16: an occurrence H[i:j] of a part
   is inside a number when its first character is a digit and H[i-1] is a digit, "." or ","; or when its last
   character is a digit and H[j] is a digit, or is "." or "," with a digit at H[j+1]. A digit is a character for which
   `str.isdecimal()` is true; a position outside H is not a digit. Such an occurrence is passed over and the search
   goes on from i+1, so each part, elided or not, is found at its first occurrence, at or after the end of the part
   before, that is not inside a number.
2. `text` checks each QUOTE, in order, against the file TEXT. `refs` checks every passage of REFS, an index or a
   fragment: its top-level tables but `update`, then its `[update.<key>]` tables, each in file order. A `quote` string
   is split on " | "; each piece holding more than white space is a passage, printed as it stands. A passage is
   checked against the `.txt` files of `SOURCES/<key>/`, `text.txt` first and the rest by name, and is found when
   `quote_in` finds it in any one of them. Tables without `quote`, and values not tables, are passed over. `--` goes
   before a QUOTE that begins with "-".
   An entry whose source text is stored under another key (a page reprinted verbatim in a volume stored under its own
   key) names that key in an optional field, `text_under = "<other key>"`; its passages are then checked against
   `SOURCES/<other key>/*.txt` in place of its own, by the same rules. The field names a key, a folder directly under
   SOURCES, never a file: a value that is empty, `.`, or holds `/` or `..` is not followed, and only `.txt` files are
   read, so a hand transcription kept as `.md` stays unread (standards/process/peer_review.md 2.1).
   An entry merged into another, `merge_into = "<other key>"` with no `text_under`, is checked as if `text_under`
   named the key its merge chain ends at: the chain is followed through the tables of REFS, top-level and update,
   until a key with no `merge_into` or a key not in REFS. A chain that comes back to a key it passed is a refusal
   naming every key of the cycle (rule 6). Its lines name the field as `merge_into` where rule 4 says `text_under`.
3. Each text file is read as UTF-8 and made plain once per run, in both forms of rule 1, however many passages it meets. In `refs` mode the
   files of a key are read when its first passage is checked.
4. Output, on standard output. A passage is found exactly when every part, the quote split at `...` (or `[...]`) and
   each part stripped of spaces at its ends, is found in order in one raw text file, by rule 1's search with its
   number-boundary rule, with nothing made plain but every white space run (what `str.split()` splits on) collapsed to
   one space in quote and text; it prints nothing. A passage found only by `quote_in` prints
   `found (normalised): Q` (text) or `KEY: found (normalised): Q` (refs), so the loosening is visible. A passage found
   by neither but by the relaxed rule (roadmap R10 2.1) prints `found (relaxed): Q` (text) or `KEY: found (relaxed): Q`
   (refs). The relaxed rule makes the passage plain by `normalise`, drops its last character when that is one of
   `. , ; : ! ?` (not the last dot of `...`), and takes its first character in either case when that is a letter; it
   is then split and searched as `quote_in` does, in each plain form of the text, and again with every space removed
   from parts and plain forms alike except a space between two letters (`_LETTER`) or between two digits
   (`str.isdecimal`).
   One not found prints `not found: Q` (text) or
   `KEY: not found: Q` (refs), then, indented two spaces, `nearest: P` (text) or `nearest in FILE: P` (refs; `nearest in OTHER/FILE: P` for an entry with
   `text_under = "OTHER"`), with
   ` (part I of N)` when the quote has N > 1 parts and P is for part I, or `nearest: none`. In `refs` mode a passage
   whose stripped text begins with "(" and ends with the ")" that closes it, or that holds "not opened" or "search
   summary" in any case, prints `KEY: not a quote: Q` before anything is read for it (roadmap R10 7.2). A passage whose
   key folder is missing prints `KEY: no stored copy: Q`, and one whose folder holds no `.txt` file
   `KEY: stored, no text: Q` (R10 6.3), each followed on the same line, for an entry with `text_under`, by
   ` (text_under OTHER has no stored copy)`, ` (text_under OTHER has no stored text)` or ` (text_under OTHER is not a
   key)`, the last counted as no stored copy. The last line is `checked N: F found, G found (normalised), R found
   (relaxed), M not found, D not a quote, C no stored copy, K stored, no text`, F counting exact finds only. Q and P
   are written as `json.dumps(s, ensure_ascii=False)`.
5. The nearest passage. The part is the quote's first part at which the search in order fails; H is the text made
   plain. The part's words are split at spaces; k = min(3, its number of words); each run of k consecutive words is
   a seed. Each occurrence of a seed in H, at offset s, votes for the start max(0, s - o), o the seed's offset in the
   part. Among the starts with most votes, the one whose window H[start : start + len(part)] has the highest
   `difflib.SequenceMatcher(None, window, part, autojunk=False).ratio()` wins, the earlier start on a tie. P is that
   window widened to whole words: its start moved back to just after the last space at or before its first
   character, its end forward to just before the first space at or after its last character (H's ends if none).
   With no part, or no seed in H, P is none. Each plain form of each file (rule 1) gives its own failing part and
   window; the highest ratio wins, the earlier on a tie, and forms giving none are skipped. Within each file the
   joined form comes before the kept form, and files keep the order of rule 2. The file is named, not the form. This is approximate string
   matching by filtering (Navarro 2001, recalled, not opened): word q-gram counting verified by Ratcliff and Obershelp's gestalt matching.
6. Exit 0 when every passage is found, exactly, normalised or relaxed; 1 when any is not found, not a quote, or has no
   stored copy or no text; 2 on a refusal (TEXT or REFS missing
   or not UTF-8, REFS not TOML, SOURCES not a folder, a `quote`, `text_under` or `merge_into` not a string, a
   `merge_into` cycle, a `.txt` under SOURCES not UTF-8), which
   prints its reason, naming the file or key, on standard error, and no count line. REFS is read and every quote
   and `text_under` checked to be a string before anything is printed.
"""

from __future__ import annotations

import argparse
import difflib
import io
import json
import re
import sys
import tomllib
import unicodedata
from collections import Counter
from pathlib import Path
from typing import cast

_PLAIN = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    **{chr(c): "-" for c in range(0x2010, 0x2016)}, "\u2212": "-",
})
_LETTER = r"[^\W\d_]"
_SOFT_HYPHENS = re.compile(r"(?<!\d)\u00ad+|\u00ad+(?![\u00ad\d])")
_LETTER_BREAK = re.compile(rf"(?<={_LETTER})-[ \t]*\r?\n\s*(?={_LETTER})")
_OTHER_BREAK = re.compile(r"-[ \t]*\r?\n\s*")

# Scripts whose word spacing is unreliable in stored text: Han, Hangul, kana and CJK punctuation. A script that writes
# digits in its own block (Thai, Lao, Khmer, Myanmar) waits for a source and a test, since adding one needs a rule for
# its digits.
_UNRELIABLE_SPACING = (
    (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0x20000, 0x3FFFF),
    (0x1100, 0x11FF), (0x3130, 0x318F), (0xA960, 0xA97F), (0xAC00, 0xD7FF),
    (0x3040, 0x30FF), (0x31F0, 0x31FF),
    (0x3001, 0x303F),
)
_LISTED = "".join(f"{chr(first)}-{chr(last)}" for first, last in _UNRELIABLE_SPACING)
_UNRELIABLE_SPACE = re.compile(f"(?<=[{_LISTED}]) | (?=[{_LISTED}])")

# Rule 4's relaxed tier (roadmap R10 2.1): a space stays only between two letters or between two digits.
_LOOSE_SPACE = re.compile(rf"(?<={_LETTER}) (?={_LETTER})|(?<=\d) (?=\d)|( )")

# Rule 1: characters NFKC would turn into plain digits or signs, so a changed number would match; left as they are.
_NUMBER_FORMS = re.compile("([" + "".join(
    re.escape(c) for c in map(chr, range(0x110000))
    if unicodedata.category(c) == "No" and unicodedata.normalize("NFKC", c) != c
) + "\u207a\u207b\u208a\u208b]+)")


def _nfkc(s: str) -> str:
    """Rule 1: NFKC on everything but `_NUMBER_FORMS`."""
    pieces = _NUMBER_FORMS.split(s)
    return "".join(p if i % 2 else unicodedata.normalize("NFKC", p) for i, p in enumerate(pieces))


def normalise(s: str) -> str:
    """Rule 1: NFKC; dashes and curly quotes made plain; soft hyphens and line-end hyphens between letters removed."""
    return _normal(s, "")


def _normal(s: str, hyphen: str) -> str:
    """`normalise`, with each hyphen at a line end between letters, and the white space about it, replaced by
    `hyphen`; any other hyphen at a line end is kept and the white space about it removed."""
    s = _SOFT_HYPHENS.sub("", _nfkc(s).translate(_PLAIN))
    s = _OTHER_BREAK.sub("-", _LETTER_BREAK.sub(hyphen, s))
    return " ".join(s.split())


def plain_forms(text: str) -> list[str]:
    """Rule 1: the text's plain forms, joined then kept, one when they are equal."""
    joined, kept = (_UNRELIABLE_SPACE.sub("", _normal(text, h)) for h in ("", "-"))
    return [joined] if joined == kept else [joined, kept]


def _raw_parts(quote: str) -> list[str]:
    """Rule 4: the quote's parts with nothing made plain but white space runs collapsed."""
    return [p for p in (p.strip(" ") for p in " ".join(quote.split()).replace("[...]", "...").split("...")) if p]


def _parts(quote: str) -> list[str]:
    parts = [_UNRELIABLE_SPACE.sub("", p.strip(" ")) for p in normalise(quote).replace("[...]", "...").split("...")]
    return [p for p in parts if p]


def _relaxed_variants(passage: str) -> list[list[str]]:
    """Rule 4's relaxed tier: the passage made plain by `normalise`, its one final mark of `.,;:!?` dropped (not the
    last dot of an ellipsis), its first character in either case when a letter, then split as `_parts` splits."""
    s = normalise(passage).strip(" ")
    if s[-1:] in tuple(".,;:!?") and not s.endswith("..."):
        s = s[:-1]
    firsts = {s[:1], s[:1].lower(), s[:1].upper()} if s[:1].isalpha() else {s[:1]}
    out: list[list[str]] = []
    for first in sorted(firsts):
        parts = [_UNRELIABLE_SPACE.sub("", p.strip(" ")) for p in (first + s[1:]).replace("[...]", "...").split("...")]
        out.append([p for p in parts if p])
    return out


def _loose(s: str) -> str:
    """Rule 4's relaxed tier: every space removed but one between two letters or between two digits."""
    return _LOOSE_SPACE.sub(lambda m: "" if m.group(1) else m.group(0), s)


def _failing(parts: list[str], hay: str) -> int | None:
    """The index of the first part the search in order fails to find, or None when every part is found."""
    at = 0
    for i, part in enumerate(parts):
        found = hay.find(part, at)
        while found >= 0 and _inside_number(hay, found, found + len(part)):
            found = hay.find(part, found + 1)
        if found < 0:
            return i
        at = found + len(part)
    return None


def _digit(hay: str, k: int) -> bool:
    """Rule 1: a decimal digit, or a character of category No or a sign of `_NUMBER_FORMS` (as `²`, `½`, `⁻`), which
    rule 1 leaves unnormalised and which is part of the number it stands in."""
    return 0 <= k < len(hay) and (
        hay[k].isdecimal() or unicodedata.category(hay[k]) == "No" or hay[k] in "\u207a\u207b\u208a\u208b")


def _inside_number(hay: str, i: int, j: int) -> bool:
    """Rule 1: whether the match hay[i:j] begins or ends inside a number."""
    if _digit(hay, i) and (_digit(hay, i - 1) or (i > 0 and hay[i - 1] in ".,")):
        return True
    return _digit(hay, j - 1) and (_digit(hay, j) or (j < len(hay) and hay[j] in ".," and _digit(hay, j + 1)))


def quote_in(quote: str, text: str) -> bool:
    """Whether the quote occurs in the text, compared as follows.

    Both are normalised, and `...` (or `[...]`) splits the quote into parts found in order. In each part and in the
    text, every space with a character of `_UNRELIABLE_SPACING` immediately before or after it is removed; every other
    space stays, so text with none of those scripts is compared with its spaces, and ASCII digits are never joined.
    An occurrence that begins or ends inside a number is passed over (rule 1). The quote is found when every part is
    found in one plain form of the text, joined or kept (rule 1).
    """
    return quote_in_forms(quote, plain_forms(text))


def quote_in_forms(quote: str, forms: list[str]) -> bool:
    """`quote_in`, given the text's plain forms already made by `plain_forms` (rule 1)."""
    parts = _parts(quote)
    return bool(parts) and any(_failing(parts, hay) is None for hay in forms)


def _nearest(part: str, hay: str) -> tuple[float, str] | None:
    """Rule 5: the ratio of the chosen window before widening, and the window widened to whole words."""
    words = part.split(" ")
    k = min(3, len(words))
    offsets: list[int] = []
    o = 0
    for w in words:
        offsets.append(o)
        o += len(w) + 1
    votes: Counter[int] = Counter()
    for i in range(len(words) - k + 1):
        seed = " ".join(words[i:i + k])
        s = hay.find(seed)
        while s >= 0:
            votes[max(0, s - offsets[i])] += 1
            s = hay.find(seed, s + 1)
    if not votes:
        return None
    most = max(votes.values())
    best: tuple[float, int] | None = None
    for start in sorted(t for t, v in votes.items() if v == most):
        ratio = difflib.SequenceMatcher(None, hay[start:start + len(part)], part, autojunk=False).ratio()
        if best is None or ratio > best[0]:
            best = (ratio, start)
    assert best is not None
    ratio, start = best
    end = min(start + len(part), len(hay))
    left = hay.rfind(" ", 0, start + 1) + 1
    right = hay.find(" ", end - 1)
    return ratio, hay[left:right if right >= 0 else len(hay)]


class _Refusal(Exception):
    pass


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise _Refusal(f"{path}: not UTF-8") from None
    except OSError as e:
        raise _Refusal(f"{path}: cannot be read ({e.strerror or e})") from None


def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _check(passage: str, raws: list[str], hays: list[tuple[str, str]], loose: list[str], key: str | None) -> int:
    """Print the lines of one passage checked against raw texts, named plain texts and their `_loose` forms; 0 when
    found exactly, 1 when found normalised, 2 when found relaxed, 3 when not found."""
    raw_parts = _raw_parts(passage)
    if raw_parts and any(_failing(raw_parts, raw) is None for raw in raws):
        return 0
    parts = _parts(passage)
    failing = [_failing(parts, hay) for _, hay in hays]
    if parts and None in failing:
        print(f"{key}: found (normalised): {_q(passage)}" if key is not None else f"found (normalised): {_q(passage)}")
        return 1
    variants = _relaxed_variants(passage)
    if any(v and _failing(v, hay) is None for v in variants for _, hay in hays) or any(
            v and _failing([_loose(p) for p in v], hay) is None for v in variants for hay in loose):
        print(f"{key}: found (relaxed): {_q(passage)}" if key is not None else f"found (relaxed): {_q(passage)}")
        return 2
    best: tuple[float, str, str, int] | None = None
    for (name, hay), i in zip(hays, failing):
        near = _nearest(parts[i], hay) if parts and i is not None else None
        if near is not None and (best is None or near[0] > best[0]):
            best = (near[0], name, near[1], i if i is not None else 0)
    print(f"{key}: not found: {_q(passage)}" if key is not None else f"not found: {_q(passage)}")
    if best is None:
        print("  nearest: none")
    else:
        _, name, window, i = best
        where = f"nearest in {name}" if key is not None else "nearest"
        suffix = f" (part {i + 1} of {len(parts)})" if len(parts) > 1 else ""
        print(f"  {where}: {_q(window)}{suffix}")
    return 3


def _not_a_quote(passage: str) -> bool:
    """Rule 4: a passage wholly in parentheses, or naming "not opened" or "search summary" in any case."""
    s = passage.strip()
    low = s.casefold()
    if "not opened" in low or "search summary" in low:
        return True
    depth = 0
    for i, c in enumerate(s if s.startswith("(") else ""):
        depth += (c == "(") - (c == ")")
        if depth == 0:
            return i == len(s) - 1
    return False


def _merged(tables: list[tuple[str, object]], refs: Path) -> dict[str, str]:
    """Rule 2: each key with `merge_into` mapped to the key its chain ends at; a cycle is a refusal naming its keys."""
    into: dict[str, str] = {}
    for key, table in tables:
        if isinstance(table, dict):
            target = cast(dict[str, object], table).get("merge_into")
            if target is not None and not isinstance(target, str):
                raise _Refusal(f"{refs}: the merge_into of {key} is not a string")
            if target is not None:
                into[key] = target
    end: dict[str, str] = {}
    for key in into:
        chain = [key]
        while chain[-1] in into:
            nxt = into[chain[-1]]
            if nxt in chain:
                cycle = chain[chain.index(nxt):]
                raise _Refusal(f"{refs}: merge_into cycle: {' -> '.join(cycle + [nxt])}")
            chain.append(nxt)
        end[key] = chain[-1]
    return end


def _passages(refs: Path) -> list[tuple[str, str, str | None, str]]:
    """Every (key, passage, other key, field naming it) of REFS in rule 2's order, every quote, text_under and
    merge_into checked to be a string, and every merge chain resolved, first."""
    try:
        data = tomllib.loads(_read(refs))
    except tomllib.TOMLDecodeError as e:
        raise _Refusal(f"{refs}: not TOML ({e})") from None
    update = data.get("update")
    tables = [(k, v) for k, v in data.items() if k != "update"]
    if isinstance(update, dict):
        tables += list(cast(dict[str, object], update).items())
    merged = _merged(cast(list[tuple[str, object]], tables), refs)
    out: list[tuple[str, str, str | None, str]] = []
    for key, table in tables:
        if not isinstance(table, dict) or "quote" not in table:
            continue
        quote = cast(dict[str, object], table)["quote"]
        under = cast(dict[str, object], table).get("text_under")
        if not isinstance(quote, str):
            raise _Refusal(f"{refs}: the quote of {key} is not a string")
        if under is not None and not isinstance(under, str):
            raise _Refusal(f"{refs}: the text_under of {key} is not a string")
        field = "text_under"
        if under is None and key in merged:
            under, field = merged[key], "merge_into"
        out += [(key, p, under, field) for p in quote.split(" | ") if p.strip()]
    return out


def _run(args: argparse.Namespace) -> int:
    # found, found (normalised), found (relaxed), not found, not a quote, no stored copy, stored, no text
    counts = [0] * 7
    if args.mode == "text":
        raw = _read(Path(args.text))
        hays = [("", hay) for hay in plain_forms(raw)]
        raw = " ".join(raw.split())
        for quote in cast(list[str], args.quotes):
            counts[_check(quote, [raw], hays, [_loose(h) for _, h in hays], None)] += 1
    else:
        passages = _passages(Path(args.refs))
        sources = Path(args.sources)
        if not sources.is_dir():
            raise _Refusal(f"{sources}: not a folder")
        plain: dict[Path, tuple[str, list[str], list[str]]] = {}
        for key, passage, under, field in passages:
            if _not_a_quote(passage):
                print(f"{key}: not a quote: {_q(passage)}")
                counts[4] += 1
                continue
            is_key = under is None or (under not in ("", ".") and "/" not in under and ".." not in under)
            folder = sources / (key if under is None else under)
            files = sorted((f for f in folder.glob("*.txt") if f.is_file()),
                           key=lambda f: (f.name != "text.txt", f.name)) if is_key else []
            if not files:
                stored = is_key and folder.is_dir()
                tier = "stored, no text" if stored else "no stored copy"
                state = "has no stored text" if stored else "has no stored copy" if is_key else "is not a key"
                why = "" if under is None else f" ({field} {_q(under)} {state})"
                print(f"{key}: {tier}: {_q(passage)}{why}")
                counts[6 if stored else 5] += 1
                continue
            for f in files:
                if f not in plain:
                    raw = _read(f)
                    forms = plain_forms(raw)
                    plain[f] = (" ".join(raw.split()), forms, [_loose(h) for h in forms])
            prefix = "" if under is None else f"{under}/"
            hays = [(prefix + f.name, hay) for f in files for hay in plain[f][1]]
            loose = [h for f in files for h in plain[f][2]]
            counts[_check(passage, [plain[f][0] for f in files], hays, loose, key)] += 1
    print(f"checked {sum(counts)}: {counts[0]} found, {counts[1]} found (normalised), {counts[2]} found (relaxed), "
          f"{counts[3]} not found, {counts[4]} not a quote, {counts[5]} no stored copy, {counts[6]} stored, no text")
    return 0 if sum(counts[:3]) == sum(counts) else 1


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")
    quiet = "A passage found exactly prints nothing; the last line counts every passage checked, so read it."
    parser = argparse.ArgumentParser(prog="tools.quotes",
                                     description=f"Check quoted passages against stored texts. {quiet}")
    sub = parser.add_subparsers(dest="mode", required=True)
    text = sub.add_parser("text", help="check each QUOTE against the file TEXT", description=quiet)
    text.add_argument("text", metavar="TEXT")
    text.add_argument("quotes", metavar="QUOTE", nargs="+")
    refs = sub.add_parser("refs", help="check every passage of REFS against SOURCES/<key>/*.txt", description=quiet)
    refs.add_argument("refs", metavar="REFS")
    refs.add_argument("sources", metavar="SOURCES")
    try:
        return _run(parser.parse_args(argv))
    except _Refusal as e:
        sys.stdout.flush()
        print(f"tools.quotes: refused: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
