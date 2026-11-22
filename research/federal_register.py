"""Federal Register client: find documents through the API and store them in a case (roadmap 2.12).

Run by path as a command:
    python research/federal_register.py search --log PATH [--agency SLUG]... [--type RULE|PRORULE|NOTICE|PRESDOCU]...
        [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--docket ID] [--limit N] [TERM]
    python research/federal_register.py search --govinfo --log PATH [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--limit N] TERM
    python research/federal_register.py store --into cases/<case>/sources/<key> DOCUMENT_NUMBER
    python research/federal_register.py store --into cases/<case>/sources/<key> --citation VOLUME FIRST_PAGE LAST_PAGE

`search` prints one JSON object per document, in the API's order, and appends one row to the log in
bibliography.py's form. Like bibliography's searches it refuses a result shorter than the reported count, and it
refuses a count of 10,000 or more, the API's cap on the count it reports, so the seat splits the search by date.

`search --govinfo` runs TERM, in govinfo's query syntax, on the full text of govinfo's FR collection, which holds every
issue from volume 1 (1936). It needs the user's api.data.gov key, DATA_GOV_API_KEY, read by the shared registry
(bibliography._held) and sent in a header, never in a URL. A hit in volume 58 (1993) or older is a whole issue:
it gives the volume and date, and the page for `store --citation` is read in the issue. A later hit is one document,
with the document number `store` takes. A quoted phrase finds no hit in the older issues (probe of 2026-11-17).

`store` writes the PDF and its `text.txt` (pdftotext) into the folder and prints the sources.toml entry. Volume 59
(1994) and older exist only as whole issues on govinfo; `--citation` fetches the issue through the link service,
cuts the pages whose first line carries the printed page numbers, and keeps only the cut.

Every request goes through bibliography._get (host ledger, retries, pacing, User-Agent). An answer that is a block
page instead of JSON or a PDF closes the host in the ledger. On any site's refusal the command exits 2 and prints
the URL to open in a browser and the path to save the file as; once that file exists the same command uses it.
"""

# pyright: reportPrivateUsage=false
# The brief (2.1.2, 2.1.5, 2.1.6) has this client use bibliography's _get, _close, _complete and _next_log_id unchanged;
# giving them public names is a separate change to bibliography.py (brief 6.1).

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Sequence
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, cast

if __package__ in (None, ""):  # run by path: make the project's root importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research import bibliography  # noqa: E402

API = "https://www.federalregister.gov/api/v1"
LINK = "https://www.govinfo.gov/link/fr"
GOVINFO_SEARCH = "https://api.govinfo.gov/search"  # POST only (research/sources/govinfo_api/README.md)
GOVINFO_KEY = "DATA_GOV_API_KEY"  # the shared registry's row gpo_govinfo
GOVINFO_PAGE = 100  # its cap is 1000, but one 1000-hit answer (about 1 MB) arrived cut off on 2026-11-17
# Neither host publishes a rate (research/sources/federal_register_api_v1/api_headers.txt shows no rate-limit header);
# 1 second is Crossref's public pool, the slowest pace this project keeps.
bibliography.MIN_INTERVAL["www.federalregister.gov"] = 1.0
bibliography.MIN_INTERVAL["www.govinfo.gov"] = 1.0
bibliography.MIN_INTERVAL["api.govinfo.gov"] = 1.0  # well inside its published 40 a second (govinfo_api/README.md)

FIELDS = ("document_number", "citation", "title", "type", "agency_names", "publication_date", "volume",
          "start_page", "end_page", "docket_ids", "regulation_id_numbers", "pdf_url", "html_url")
PER_PAGE = 1000  # the API's maximum (research/sources/federal_register_api_v1/text.txt:16)
COUNT_CAP = 10000  # the API reports at most this count (probe_large.json)
LAST_DIGITIZED_VOLUME = 59  # volume 59 (1994) and older exist only as whole issues (govinfo help_fr_text.txt)
LICENCE = "US government work (17 U.S.C. 105)"
FIRST_VOLUME_YEAR = 1935  # volume 1 is 1936 and each year since is one volume, so a year's volume is year - 1935


class Refused(RuntimeError):
    """A site refused an automated fetch: the user opens `url` in a browser and saves the file as `save_as`."""

    def __init__(self, reason: str, url: str, save_as: Path | None, note: str = "") -> None:
        super().__init__(reason)
        self.url = url
        self.save_as = save_as
        self.note = note


class Stop(RuntimeError):
    """A refusal that is not a site's: an incomplete search, a capped count, a page not found, a wrong volume."""


def _fetch(url: str, save_as: Path | None, data: bytes | None = None) -> bytes:
    try:
        return bibliography._get(url, data)
    except bibliography.HostClosed as err:
        raise Refused(str(err), url, save_as) from err
    except bibliography.RequestFailed as err:
        if err.status == 403 and save_as is not None:
            raise Refused(str(err), url, save_as) from err
        raise


def _close(url: str, what: str, save_as: Path | None) -> Refused:
    host = urllib.parse.urlsplit(url).netloc.lower()
    bibliography._close(host, 302, None, url)
    return Refused(f"{url} answered with something other than {what}, a refusal of automated access; "
                   f"{host} is closed for 24 hours", url, save_as)


def _api_json(url: str) -> dict[str, Any]:
    body = _fetch(url, None)
    try:
        answer = json.loads(body)
    except ValueError:
        answer = None
    if not isinstance(answer, dict):
        raise _close(url, "JSON", None)
    return cast(dict[str, Any], answer)


def _pdf(url: str, save_as: Path, note: str = "") -> bytes:
    """The PDF the user saved at `save_as`, else the one `url` answers (never written here)."""
    if save_as.exists():
        body = save_as.read_bytes()
        if not body.startswith(b"%PDF-"):
            raise Stop(f"{save_as} is not a PDF; save the file {url} serves there again")
        return body
    try:
        body = _fetch(url, save_as)
    except Refused as err:
        err.note = note
        raise
    if not body.startswith(b"%PDF-"):
        err = _close(url, "a PDF", save_as)
        err.note = note
        raise err
    return body


# ---------------------------------------------------------------- search


def search(log: Path, term: str | None, agencies: Sequence[str], types: Sequence[str], date_from: str | None,
           date_to: str | None, docket: str | None, limit: int | None) -> list[dict[str, Any]]:
    last = bibliography.last_search_date()
    if last and (not date_to or date_to > last):
        date_to = last
    filters: dict[str, Any] = {}
    if agencies:
        filters["conditions[agencies][]"] = list(agencies)
    if types:
        filters["conditions[type][]"] = list(types)
    if date_from:
        filters["conditions[publication_date][gte]"] = date_from
    if date_to:
        filters["conditions[publication_date][lte]"] = date_to
    if docket:
        filters["conditions[docket_id]"] = docket
    params = {**({"conditions[term]": term} if term else {}), **filters, "per_page": str(PER_PAGE),
              "fields[]": list(FIELDS)}
    first = f"{API}/documents.json?{urllib.parse.urlencode(params, doseq=True)}"
    row_id = bibliography._next_log_id(log)
    stamp = datetime.now(timezone.utc).isoformat()

    url: str | None = first
    hits = 0
    docs: list[dict[str, Any]] = []
    while url:
        page = _api_json(url)
        hits = int(page.get("count") or 0)
        if hits >= COUNT_CAP:
            raise Stop(f"the API reported {hits} documents for {first}, its cap, so the true count is unknown; "
                       "split the search by publication date (--from, --to) until each part reports fewer")
        docs += cast(list[dict[str, Any]], page.get("results") or [])
        if len(docs) >= min(hits, limit if limit is not None else hits):
            break
        url = cast(str | None, page.get("next_page_url"))
    if limit is not None:
        docs = docs[:limit]
    try:
        bibliography._complete("federal_register", first, hits, len(docs), limit if limit is not None else hits)
    except bibliography.IncompleteSearch as err:
        raise Stop(str(err)) from err

    row = {"id": row_id, "time": stamp, "database": "federal_register", "query": term or "", "filters": filters,
           "hits": hits, "returned": len(docs), "url": first}
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return docs


_plain_request = bibliography._request


def _request(url: str, data: bytes | None, host: str) -> urllib.request.Request:
    """bibliography's request, and to govinfo's API the user's key in a header a redirect does not carry on."""
    req = _plain_request(url, data, host)
    if host == "api.govinfo.gov":
        req.add_unredirected_header("X-Api-Key", bibliography._held(GOVINFO_KEY))
        req.add_header("Content-Type", "application/json")
    return req


bibliography._request = _request  # bibliography._get sends through it, with the host ledger, pacing and retries


def search_govinfo(log: Path, term: str, date_from: str | None, date_to: str | None,
                   limit: int | None) -> list[dict[str, Any]]:
    if not bibliography._held(GOVINFO_KEY):
        raise Stop(f"govinfo's search needs an api.data.gov key and none is held: set {GOVINFO_KEY} or put the key "
                   f"in ~/.local/share/research-keys/{GOVINFO_KEY} (https://www.govinfo.gov/api-signup)")
    last = bibliography.last_search_date()
    if last and (not date_to or date_to > last):
        date_to = last
    query = f"({term}) collection:(FR)"
    if date_from or date_to:
        query += f" publishdate:range({date_from or ''},{date_to or ''})"
    row_id = bibliography._next_log_id(log)
    stamp = datetime.now(timezone.utc).isoformat()

    hits = 0
    docs: list[dict[str, Any]] = []
    mark: str | None = "*"
    while mark:
        body = {"query": query, "pageSize": GOVINFO_PAGE, "offsetMark": mark,
                "sorts": [{"field": "publishdate", "sortOrder": "ASC"}]}
        try:
            answer = json.loads(_fetch(GOVINFO_SEARCH, None, json.dumps(body).encode()))
        except ValueError:
            answer = None
        if not isinstance(answer, dict):
            raise _close(GOVINFO_SEARCH, "JSON", None)
        page = cast(dict[str, Any], answer)
        hits = int(page.get("count") or 0)
        results = cast(list[dict[str, Any]], page.get("results") or [])
        for r in results:
            issued = str(r["dateIssued"])
            docs.append({"volume": date.fromisoformat(issued).year - FIRST_VOLUME_YEAR, "publication_date": issued,
                         "title": r.get("title"), "package_id": r.get("packageId"),
                         "document_number": r.get("granuleId")})
        if not results or len(docs) >= min(hits, limit if limit is not None else hits):
            break
        mark = cast(str | None, page.get("offsetMark"))
    if limit is not None:
        docs = docs[:limit]
    try:
        bibliography._complete("govinfo_fr", f"{GOVINFO_SEARCH} {query}", hits, len(docs),
                               limit if limit is not None else hits)
    except bibliography.IncompleteSearch as err:
        raise Stop(str(err)) from err

    row = {"id": row_id, "time": stamp, "database": "govinfo_fr", "query": term, "filters": {"from": date_from, "to": date_to},
           "hits": hits, "returned": len(docs), "url": f"{GOVINFO_SEARCH} {query}"}
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return docs


# ---------------------------------------------------------------- store


def _entry(key: str, citation: str, url: str) -> str:
    name = key if re.fullmatch(r"[A-Za-z0-9_-]+", key) else json.dumps(key, ensure_ascii=False)
    lines = [f"[{name}]"] + [f"{k} = {json.dumps(v, ensure_ascii=False)}"
                             for k, v in (("citation", citation), ("licence", LICENCE), ("url", url))]
    return "\n".join(lines) + "\n"


def _pdftotext(pdf: Path, out: Path, *options: str) -> None:
    subprocess.run(["pdftotext", *options, str(pdf), str(out)], check=True)


def store_document(into: Path, number: str) -> str:
    doc = _api_json(f"{API}/documents/{urllib.parse.quote(number)}.json?"
                    + urllib.parse.urlencode({"fields[]": list(FIELDS)}, doseq=True))
    volume, start, end = doc.get("volume"), doc.get("start_page"), doc.get("end_page")
    pdf_url = cast(str | None, doc.get("pdf_url"))
    if not pdf_url:
        raise Stop(f"document {number} has no pdf_url; store it by its printed citation instead: "
                   f"store --into {into} --citation {volume} {start} {end}")
    target = into / f"{number}.pdf"
    body = _pdf(pdf_url, target)
    into.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(body)
    _pdftotext(target, into / "text.txt")

    published = date.fromisoformat(str(doc["publication_date"]))
    agencies = ", ".join(cast(list[str], doc.get("agency_names") or []))
    pages = f"{start}" if start == end else f"{start}-{end}"
    dockets = cast(list[str], doc.get("docket_ids") or [])
    citation = (f"{agencies} ({published.year}). {str(doc['title']).rstrip('.')}. Federal Register {volume}:{pages}, "
                f"{published.day} {published:%B} {published.year}"
                + (f", Docket {', '.join(dockets)}" if dockets else "") + f". Document {number}.")
    return _entry(into.name, citation, pdf_url)


def _first_lines(pdf: Path) -> list[str]:
    """The first non-blank `pdftotext -layout` line of each page, in page order ('' for a blank page)."""
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return [next((line.strip() for line in page.splitlines() if line.strip()), "") for page in text.split("\f")]


def _find(lines: Sequence[str], printed: int, after: int = 0) -> int | None:
    """The 1-based PDF page, at or after `after`, whose first line starts or ends with the token `printed`."""
    for index in range(after, len(lines)):
        tokens = lines[index].split()
        if tokens and str(printed) in (tokens[0], tokens[-1]):
            return index + 1
    return None


def store_citation(into: Path, volume: int, first: int, last: int) -> str:
    if volume > LAST_DIGITIZED_VOLUME:
        raise Stop(f"volume {volume} is in the API (volume 60, 1995, and later); find it with search and store it "
                   "by its document number")
    link = f"{LINK}/{volume}/{first}"
    saved = into / "issue.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        issue = saved if saved.exists() else work / "issue.pdf"
        body = _pdf(link, saved, note=f"{saved} is removed once the pages are cut from it")
        if issue != saved:
            issue.write_bytes(body)
        lines = _first_lines(issue)
        start = _find(lines, first)
        end = _find(lines, last, start - 1) if start is not None else None
        if start is None or end is None:
            raise Stop(f"the issue {link} serves has no page whose first line begins or ends with printed page "
                       f"{first if start is None else last} (asked for pages {first} to {last})")
        subprocess.run(["pdfseparate", "-f", str(start), "-l", str(end), str(issue), str(work / "page-%d.pdf")],
                       check=True)
        into.mkdir(parents=True, exist_ok=True)
        cut = into / f"FR-{volume}-{first}.pdf"
        subprocess.run(["pdfunite", *(str(work / f"page-{n}.pdf") for n in range(start, end + 1)), str(cut)],
                       check=True)
    _pdftotext(cut, into / "text.txt")
    if saved.exists():
        saved.unlink()
    pages = f"{first}" if first == last else f"{first}-{last}"
    citation = (f"Federal Register {volume}:{pages}. Printed pages {pages} cut from the whole issue the link serves "
                f"(its PDF pages {start}-{end}); the agency, title and date are read from the pages.")
    return _entry(into.name, citation, link)


# ---------------------------------------------------------------- the interface


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="federal_register.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("--log", required=True, type=Path)
    s.add_argument("--govinfo", action="store_true", help="full-text search of every issue on govinfo (needs TERM)")
    s.add_argument("--agency", action="append", default=[])
    s.add_argument("--type", action="append", default=[], choices=["RULE", "PRORULE", "NOTICE", "PRESDOCU"])
    s.add_argument("--from", dest="date_from")
    s.add_argument("--to", dest="date_to")
    s.add_argument("--docket")
    s.add_argument("--limit", type=int)
    s.add_argument("term", nargs="?")
    t = sub.add_parser("store")
    t.add_argument("--into", required=True, type=Path)
    t.add_argument("--citation", nargs=3, type=int, metavar=("VOLUME", "FIRST_PAGE", "LAST_PAGE"))
    t.add_argument("document_number", nargs="?")
    args = parser.parse_args(list(argv))

    try:
        if args.command == "search" and args.govinfo:
            term = cast(str | None, args.term)
            if not term or args.agency or args.type or args.docket:
                parser.error("search --govinfo takes TERM and no --agency, --type or --docket")
            for doc in search_govinfo(cast(Path, args.log), term, cast(str | None, args.date_from),
                                      cast(str | None, args.date_to), cast(int | None, args.limit)):
                print(json.dumps(doc, ensure_ascii=False))
            return 0
        if args.command == "search":
            for doc in search(cast(Path, args.log), cast(str | None, args.term), cast(list[str], args.agency),
                              cast(list[str], args.type), cast(str | None, args.date_from),
                              cast(str | None, args.date_to), cast(str | None, args.docket),
                              cast(int | None, args.limit)):
                print(json.dumps(doc, ensure_ascii=False))
            return 0
        into = cast(Path, args.into)
        citation = cast(list[int] | None, args.citation)
        number = cast(str | None, args.document_number)
        if (citation is None) == (number is None):
            parser.error("store takes either DOCUMENT_NUMBER or --citation VOLUME FIRST_PAGE LAST_PAGE")
        print(store_citation(into, *citation) if citation is not None else store_document(into, cast(str, number)),
              end="")
        return 0
    except Refused as err:
        print(f"refused: {err}", file=sys.stderr)
        if err.save_as is not None:
            print(f"Open this link in a browser:\n  {err.url}\nSave the file as:\n  {err.save_as}\n"
                  "then run the same command again." + (f" {err.note}." if err.note else ""), file=sys.stderr)
        else:
            print(f"Nothing can be stored without this answer; the user may open {err.url} in a browser.",
                  file=sys.stderr)
        return 2
    except Stop as err:
        print(f"refused: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
