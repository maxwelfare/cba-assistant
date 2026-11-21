"""Bibliographic client for the research pipeline's step 1, Identify (build plan item 1).

Every record comes from a database's answer: OpenAlex, Crossref or PubMed.
`search` logs each query with its time, filters and the database's own hit
count (one JSON line per search, for the PRISMA flow); `lookup` finds a work by
DOI; `references` and `citing` chase citations through OpenAlex; `merge`
joins duplicates by DOI, then by title and year.

Run by path as a command:
    python research/bibliography.py search --database D --log PATH [--limit N] [--from YEAR] [--to YEAR] [--language CODE] QUERY
    python research/bibliography.py lookup DOI
    python research/bibliography.py references DOI
    python research/bibliography.py citing DOI
Each prints one JSON object per record per line.

Politeness: at most 5 requests a second to OpenAlex, 1 to Crossref and 3 to
PubMed (the limits Crossref's public pool and NCBI set without a key); a 5xx is retried up to 3
times with backoff; the User-Agent names the project. The contact address the user holds as
RESEARCH_CONTACT_EMAIL, if any, is sent as OpenAlex's and Crossref's `mailto`. The OpenAlex API key
the user holds as OPENALEX_API_KEY, if any, goes with each OpenAlex request as an `Authorization: Bearer`
header and never in a URL (RFC 6750, 2.3), since OpenAlex has metered keyless use since 2026-02-13
(https://developers.openalex.org/api-reference/authentication). What the user holds is read by the
shared registry's own function (tools/access.py `value`, with library/access.toml beside it: the
environment variable, else the user's file), so this client and `tools.access status` cannot disagree.

After a refusal for load nobody touches the host for a day (the owner, 2026-10-30: "set up a hard
rule that nobody ever touches any server for any reason for at least a day after getting a 429 from
it"). A 429, or a 403 from Crossref or OpenAlex (a block or a rate limit by their pages), is never
retried: it closes the host for 24 hours, or for its Retry-After if longer, in the machine's ledger,
and every request first checks that ledger. The ledger, its rule and the code that reads and writes it are
the shared folder's tools/host_cooldown.py (whose header gives the period's sources), loaded by its path from
the copy's shared/ folder or the shared folder beside the project; this client keeps no ledger code of its own.

Completeness: a search, or a chase of references or citing works, that returns fewer records than
the database reported (up to the limit asked for) is refused with IncompleteSearch, never logged or
returned short, so a lost page cannot silently drop studies from a review (the owner, 2026-10-30:
this check in place of paging tests).
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, cast

USER_AGENT = (
    "automated-cost-benefit-analysis bibliographic client "
    "(https://github.com/maxwelfare/cba-assistant)"
)
OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
# Seconds between requests to one host: 5 a second for OpenAlex; 1 for Crossref, whose public
# pool answers list queries with x-rate-limit-limit: 1 per 1s (headers read 2026-10-29); 3 for
# NCBI without a key (https://www.ncbi.nlm.nih.gov/books/NBK25497/).
# OpenAlex: 0.5 s, against its 5 a second for a search with more than five boolean operators and a free key
# (https://developers.openalex.org/api/authentication/, read 2026-11-08, stored in
# research/sources/openalex_2026_authentication/).
MIN_INTERVAL = {"api.openalex.org": 0.5, "api.crossref.org": 1.0, "eutils.ncbi.nlm.nih.gov": 1 / 3}
# OpenAlex's budget, from the same page: a daily budget ($1 with a free key, a tenth of that without) reset at
# midnight UTC, and a new account's first $1 spent at no more than $0.10 every 5 minutes, a tenth of the day's
# budget. Any 429 closes the host for a day under the owner's rule, so the client keeps well inside both, reading
# each response's X-RateLimit-Limit, X-RateLimit-Remaining and X-RateLimit-Credits-Used headers: it spends at most
# 8 per cent of the daily budget in any 5 minutes, and stops when a fifth of the day's budget is left.
OPENALEX_PACE_WINDOW_S = 300.0
OPENALEX_PACE_SHARE = 0.08
OPENALEX_RESERVE_SHARE = 0.2
RETRIES = 3
OPENALEX_MAX = 10000  # numbered pages stop at the 10,000th result
PUBMED_MAX = 9999  # esearch returns at most the first 9,999 ids of a query

_last_request: dict[str, float] = {}


@dataclass(frozen=True, kw_only=True)
class Record:
    database: str
    id: str
    doi: str | None
    pmid: str | None
    title: str
    authors: tuple[str, ...]
    year: int | None
    venue: str | None
    abstract: str | None
    cited_by_count: int | None
    oa_url: str | None
    found_by: tuple[str, ...]
    language: str | None = None


class RequestFailed(RuntimeError):
    def __init__(self, url: str, status: int, reason: str) -> None:
        super().__init__(f"{url} answered HTTP {status}: {reason}")
        self.url = url
        self.status = status


class IncompleteSearch(RuntimeError):
    """A search that returned fewer records than the database reported, up to the limit asked for."""


def _complete(database: str, url: str, hits: int, got: int, limit: int) -> None:
    want = min(limit, hits)
    if got != want:
        raise IncompleteSearch(
            f"{database} reported {hits} hits for {url} but returned {got} records where {want} were asked for; "
            "a page was lost or the index changed during the search"
        )


class BudgetReserve(RuntimeError):
    """OpenAlex's remaining daily budget fell to the reserve; nothing more is sent before it resets at midnight UTC."""


@dataclass
class _OpenAlexBudget:
    limit: float | None = None
    remaining: float | None = None
    largest_cost: float = 0.0
    spent: list[tuple[float, float]] = dataclasses.field(default_factory=lambda: [])

    def before(self) -> None:
        if self.limit is None or self.remaining is None:
            return
        if self.remaining < OPENALEX_RESERVE_SHARE * self.limit:
            raise BudgetReserve(
                f"OpenAlex reports {self.remaining:g} of a daily budget of {self.limit:g} left, under the reserve of "
                f"{OPENALEX_RESERVE_SHARE:.0%}; resume after midnight UTC"
            )
        cap = OPENALEX_PACE_SHARE * self.limit
        while True:
            now = time.monotonic()
            self.spent = [(t, c) for t, c in self.spent if now - t < OPENALEX_PACE_WINDOW_S]
            if not self.spent or sum(c for _, c in self.spent) + self.largest_cost <= cap:
                return
            time.sleep(self.spent[0][0] + OPENALEX_PACE_WINDOW_S - now + 0.1)

    def after(self, headers: Any) -> None:
        def number(name: str) -> float | None:
            value = headers.get(name) if headers is not None else None
            try:
                return float(value) if value is not None else None
            except ValueError:
                return None

        limit, remaining, cost = (number(h) for h in ("X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Credits-Used"))
        if limit is not None and remaining is not None:
            self.limit, self.remaining = limit, remaining
        if cost is not None:
            self.spent.append((time.monotonic(), cost))
            self.largest_cost = max(self.largest_cost, cost)


openalex_budget = _OpenAlexBudget()


class HostClosed(RuntimeError):
    def __init__(self, host: str, until: datetime) -> None:
        super().__init__(f"{host} refused for load and is closed until {until.isoformat()} (UTC); nothing may query it before then")
        self.host = host
        self.until = until


# ---------------------------------------------------------------- the shared ledger of closed hosts


_ROOT = Path(__file__).resolve().parent.parent
_COOLDOWN_PATH = next((f / "tools" / "host_cooldown.py" for f in (_ROOT / "shared", _ROOT.parent / "shared")
                       if (f / "tools" / "host_cooldown.py").is_file()), None)
_COOLDOWN_SPEC = (importlib.util.spec_from_file_location("shared_tools_host_cooldown", _COOLDOWN_PATH)
                  if _COOLDOWN_PATH else None)
if _COOLDOWN_SPEC is None or _COOLDOWN_SPEC.loader is None:
    raise ImportError("the shared ledger of closed hosts, shared/tools/host_cooldown.py, is not in this repository "
                      "or beside it")
_cooldown = importlib.util.module_from_spec(_COOLDOWN_SPEC)
sys.modules[_COOLDOWN_SPEC.name] = _cooldown
_COOLDOWN_SPEC.loader.exec_module(_cooldown)
_closed = cast(Callable[[], dict[str, dict[str, Any]]], _cooldown.closed)
_closes = cast(Callable[[str, int], bool], _cooldown.closes)
_shared_close = cast(Callable[..., datetime], _cooldown.close)


def _closed_until(host: str) -> datetime | None:
    row = _closed().get(host)
    return datetime.fromisoformat(str(row["until"])) if row else None


def _close(host: str, status: int, retry_after: str | None, url: str) -> datetime:
    """Close `host` on the shared ledger (research/federal_register.py calls this too)."""
    return _shared_close(host, status, by="research/bibliography.py", note=url, retry_after=retry_after)


# ---------------------------------------------------------------- HTTP


_Rows = dict[str, dict[str, str]]
_registry: tuple[Callable[[str, _Rows], str], _Rows] | None = None


def _held(var: str) -> str:
    """What this user holds for `var`, "" when none: the environment variable, else the user's file, read at every
    call by the shared registry's own function (tools/access.py `value`), found in the copy's shared/ folder or in
    the shared folder beside the project. The registry is parsed once a process."""
    global _registry
    if _registry is None:
        path = next((f / "tools" / "access.py" for f in (_ROOT / "shared", _ROOT.parent / "shared")
                     if (f / "tools" / "access.py").is_file()), None)
        spec = importlib.util.spec_from_file_location("shared_tools_access", path) if path else None
        if spec is None or spec.loader is None:
            raise RuntimeError("the shared registry's tool, shared/tools/access.py, is not in this repository "
                               "or beside it; it says where a user's key and contact address are read")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _registry = (cast(Callable[[str, _Rows], str], module.value), cast(_Rows, module.rows()))
    value, reg = _registry
    return value(var, reg)


def _request(url: str, data: bytes | None, host: str) -> urllib.request.Request:
    """The request as sent: one to OpenAlex carries the user's API key, where they hold one, in a header that a
    redirect to another address does not carry on."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT})
    key = _held("OPENALEX_API_KEY") if host == "api.openalex.org" else ""
    if key:
        req.add_unredirected_header("Authorization", f"Bearer {key}")
    return req


def _get(url: str, data: bytes | None = None) -> bytes:
    """GET (or POST `data`) with the per-host interval and retries on 5xx; raises RequestFailed, or HostClosed
    when the host is in the ledger of closed hosts. A refusal for load closes the host and is never retried."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    for attempt in range(RETRIES + 1):
        until = _closed_until(host)
        if until is not None:
            raise HostClosed(host, until)
        if host == "api.openalex.org":
            openalex_budget.before()
        wait = _last_request.get(host, 0.0) + MIN_INTERVAL[host] - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request[host] = time.monotonic()
        req = _request(url, data, host)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if host == "api.openalex.org":
                    openalex_budget.after(resp.headers)
                return cast(bytes, resp.read())
        except urllib.error.HTTPError as err:
            if _closes(host, err.code):
                _close(host, err.code, err.headers.get("Retry-After") if err.headers else None, url)
                raise RequestFailed(url, err.code, str(err.reason)) from err
            if err.code >= 500 and attempt < RETRIES:
                time.sleep(2**attempt)
                continue
            raise RequestFailed(url, err.code, str(err.reason)) from err
    raise AssertionError("unreachable")


def _get_json(url: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(_get(url)))


def _url(base: str, params: dict[str, str]) -> str:
    mailto = _held("RESEARCH_CONTACT_EMAIL")
    if mailto and not base.startswith(EUTILS):
        params = {**params, "mailto": mailto}
    return f"{base}?{urllib.parse.urlencode(params)}" if params else base


def _bare_doi(doi: str) -> str:
    doi = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:"):
        if doi.startswith(prefix):
            return doi[len(prefix):]
    return doi


# ---------------------------------------------------------------- OpenAlex


def _openalex_record(w: dict[str, Any], found_by: tuple[str, ...]) -> Record:
    ids = cast(dict[str, Any], w.get("ids") or {})
    pmid = cast(str | None, ids.get("pmid"))
    loc = cast(dict[str, Any], w.get("primary_location") or {})
    source = cast(dict[str, Any], loc.get("source") or {})
    inverted = cast(dict[str, list[int]] | None, w.get("abstract_inverted_index"))
    abstract = None
    if inverted:
        placed = sorted((pos, word) for word, positions in inverted.items() for pos in positions)
        abstract = " ".join(word for _, word in placed)
    doi = cast(str | None, w.get("doi"))
    authorships = cast(list[dict[str, Any]], w.get("authorships") or [])
    return Record(
        database="openalex",
        id=cast(str, w["id"]),
        doi=_bare_doi(doi) if doi else None,
        pmid=pmid.rstrip("/").rsplit("/", 1)[-1] if pmid else None,
        title=cast(str | None, w.get("title")) or "",
        authors=tuple(cast(str, a["author"]["display_name"]) for a in authorships),
        year=cast(int | None, w.get("publication_year")),
        venue=cast(str | None, source.get("display_name")),
        abstract=abstract,
        cited_by_count=cast(int | None, w.get("cited_by_count")),
        oa_url=cast(str | None, cast(dict[str, Any], w.get("open_access") or {}).get("oa_url")),
        found_by=found_by,
        language=cast(str | None, w.get("language")),
    )


def last_search_date() -> str | None:
    """The last publication date a search may return, from the environment; unset, the default, means no limit.

    One place for it, so a seat need remember nothing: every search, reference list and citation chase goes through
    the three functions that read it. A malformed date is refused, since it would read as an absent literature.
    """
    last = os.environ.get("SEARCH_LAST_DATE")
    if not last:
        return None
    date.fromisoformat(last)
    return last


def _openalex_pages(params: dict[str, str], limit: int) -> tuple[str, int, list[dict[str, Any]]]:
    """Page OpenAlex works; returns the first URL, the reported count and up to `limit` works.

    Numbered pages, since OpenAlex refuses cursor paging without an API key; they reach the
    first 10,000 results only.
    """
    if limit > OPENALEX_MAX:
        raise ValueError(f"OpenAlex's numbered pages reach at most {OPENALEX_MAX} results; limit was {limit}")
    last = last_search_date()
    if last:  # a repeated OpenAlex filter is an AND, so a tighter year filter already there still holds
        params = {**params, "filter": ",".join(p for p in (params.get("filter"), f"to_publication_date:{last}") if p)}
    params = {**params, "per-page": str(min(limit, 100))}  # its per_page maximum (authentication page)
    first_url = ""
    count = 0
    works: list[dict[str, Any]] = []
    page_number = 1
    while len(works) < limit:
        url = _url(OPENALEX, {**params, "page": str(page_number)})
        page = _get_json(url)
        if not first_url:
            first_url, count = url, int(page["meta"]["count"])
        results = cast(list[dict[str, Any]], page["results"])
        works.extend(results)
        if not results or len(works) >= count:
            break
        page_number += 1
    _complete("OpenAlex", first_url, count, len(works[:limit]), limit)
    return first_url, count, works[:limit]


def _openalex_year_filter(year_from: int | None, year_to: int | None) -> str | None:
    if year_from is not None and year_to is not None:
        return f"publication_year:{year_from}-{year_to}"
    if year_from is not None:
        return f"publication_year:>{year_from - 1}"
    if year_to is not None:
        return f"publication_year:<{year_to + 1}"
    return None


# ---------------------------------------------------------------- Crossref


def _crossref_record(item: dict[str, Any], found_by: tuple[str, ...]) -> Record:
    doi = _bare_doi(cast(str, item["DOI"]))
    year = None
    for key in ("issued", "published", "published-print", "published-online"):
        parts = cast(list[list[int | None]], cast(dict[str, Any], item.get(key) or {}).get("date-parts") or [])
        if parts and parts[0] and parts[0][0] is not None:
            year = int(parts[0][0])
            break
    authors: list[str] = []
    for a in cast(list[dict[str, Any]], item.get("author") or []):
        name = " ".join(cast(str, a[k]) for k in ("given", "family") if a.get(k)) or cast(str, a.get("name") or "")
        if name:
            authors.append(name)
    titles = cast(list[str], item.get("title") or [])
    venues = cast(list[str], item.get("container-title") or [])
    return Record(
        database="crossref",
        id=doi,
        doi=doi,
        pmid=None,
        title=titles[0] if titles else "",
        authors=tuple(authors),
        year=year,
        venue=venues[0] if venues else None,
        abstract=cast(str | None, item.get("abstract")),
        cited_by_count=cast(int | None, item.get("is-referenced-by-count")),
        oa_url=None,
        found_by=found_by,
    )


def _crossref_held_to(params: dict[str, str], last: str) -> dict[str, str]:
    """Crossref reads a repeated filter as an OR, so one until-pub-date is kept: the earlier of the caller's and `last`."""
    parts = [p for p in params.get("filter", "").split(",") if p]
    if any(p.startswith("until-pub-date:") and p.split(":")[1][:4] < last[:4] for p in parts):
        return params
    return {**params, "filter": ",".join([*(p for p in parts if not p.startswith("until-pub-date:")), f"until-pub-date:{last}"])}


def _crossref_pages(params: dict[str, str], limit: int) -> tuple[str, int, list[dict[str, Any]]]:
    last = last_search_date()
    if last:
        params = _crossref_held_to(params, last)
    params = {**params, "rows": str(min(limit, 1000))}
    cursor = "*"
    first_url = ""
    count = 0
    items: list[dict[str, Any]] = []
    while len(items) < limit:
        url = _url(CROSSREF, {**params, "cursor": cursor})
        message = cast(dict[str, Any], _get_json(url)["message"])
        if not first_url:
            first_url, count = url, int(message["total-results"])
        page = cast(list[dict[str, Any]], message["items"])
        items.extend(page)
        cursor = cast(str | None, message.get("next-cursor"))
        if not page or not cursor:
            break
    _complete("Crossref", first_url, count, len(items[:limit]), limit)
    return first_url, count, items[:limit]


# ---------------------------------------------------------------- PubMed


def _text(el: ET.Element | None) -> str | None:
    if el is None:
        return None
    text = " ".join("".join(el.itertext()).split())
    return text or None


def _pubmed_record(article: ET.Element, found_by: tuple[str, ...]) -> Record:
    pmid = _text(article.find(".//PMID"))
    if pmid is None:
        raise ValueError("PubMed answered an article without a PMID")
    doi = _text(article.find(".//ArticleIdList/ArticleId[@IdType='doi']"))
    year_text = _text(article.find(".//PubDate/Year")) or _text(article.find(".//PubDate/MedlineDate")) or ""
    year_match = re.match(r"\d{4}", year_text)
    authors: list[str] = []
    for a in article.findall(".//AuthorList/Author"):
        name = _text(a.find("CollectiveName")) or " ".join(
            t for t in (_text(a.find("ForeName")), _text(a.find("LastName"))) if t
        )
        if name:
            authors.append(name)
    abstract = "\n".join(t for t in (_text(p) for p in article.findall(".//Abstract/AbstractText")) if t)
    return Record(
        database="pubmed",
        id=pmid,
        doi=_bare_doi(doi) if doi else None,
        pmid=pmid,
        title=_text(article.find(".//ArticleTitle")) or _text(article.find(".//BookTitle")) or "",
        authors=tuple(authors),
        year=int(year_match.group()) if year_match else None,
        venue=_text(article.find(".//Journal/Title")),
        abstract=abstract or None,
        cited_by_count=None,
        oa_url=None,
        found_by=found_by,
    )


def _pubmed_search(
    params: dict[str, str], limit: int, found_by: tuple[str, ...]
) -> tuple[str, int, list[Record]]:
    if limit > PUBMED_MAX:
        raise ValueError(f"PubMed's esearch returns at most {PUBMED_MAX} ids; limit was {limit}")
    last = last_search_date()
    if last and params.get("maxdate", "3000")[:4] >= last[:4]:  # PubMed takes maxdate only with mindate
        params = {**params, "datetype": "pdat", "mindate": params.get("mindate", "1"), "maxdate": last.replace("-", "/")}
    url = _url(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", **params, "retmax": str(limit), "retmode": "json"})
    result = cast(dict[str, Any], _get_json(url)["esearchresult"])
    ids = cast(list[str], result["idlist"])
    _complete("PubMed", url, int(result["count"]), len(ids), limit)
    records: list[Record] = []
    for start in range(0, len(ids), 200):
        batch = ids[start:start + 200]
        body = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}).encode()
        root = ET.fromstring(_get(f"{EUTILS}/efetch.fcgi", data=body))
        got = [_pubmed_record(a, found_by) for a in root if a.tag in ("PubmedArticle", "PubmedBookArticle")]
        if sorted(r.id for r in got) != sorted(batch):
            raise RuntimeError(f"PubMed efetch answered {len(got)} records for {len(batch)} ids")
        records.extend(got)
    return url, int(result["count"]), records


# ---------------------------------------------------------------- the interface


def _next_log_id(log: Path) -> int:
    if not log.exists():
        return 1
    ids = [int(json.loads(line)["id"]) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    return max(ids, default=0) + 1


def search(
    query: str,
    database: str,
    log: Path | str,
    *,
    limit: int = 200,
    year_from: int | None = None,
    year_to: int | None = None,
    language: str | None = None,
) -> list[Record]:
    """The database's own keyword search, paged to `limit`; appends one row to `log` on success.

    `language`, a two-letter code, restricts an OpenAlex search; Crossref and PubMed refuse it, and a code of any
    other form is refused, since a malformed filter would answer few or no hits that read as an absent literature.
    """
    if language and database in ("crossref", "pubmed"):
        raise ValueError(f"{database} does not support a language filter through this client; search without one")
    if language and database == "openalex" and not re.fullmatch(r"[A-Za-z]{2}", language):
        raise ValueError(f"language must be a two-letter code such as ko; it was {language!r}")
    log = Path(log)
    row_id = _next_log_id(log)
    found_by = (f"search:{row_id}",)
    stamp = datetime.now(timezone.utc).isoformat()
    filters: dict[str, str] = {}
    if database == "openalex":
        language_filter = f"language:{language.lower()}" if language else None
        parts = [p for p in (_openalex_year_filter(year_from, year_to), language_filter) if p]
        if parts:
            filters["filter"] = ",".join(parts)
        url, hits, works = _openalex_pages({"search": query, **filters}, limit)
        records = [_openalex_record(w, found_by) for w in works]
    elif database == "crossref":
        parts = [f"from-pub-date:{year_from}"] if year_from is not None else []
        parts += [f"until-pub-date:{year_to}"] if year_to is not None else []
        if parts:
            filters["filter"] = ",".join(parts)
        url, hits, items = _crossref_pages({"query": query, **filters}, limit)
        records = [_crossref_record(i, found_by) for i in items]
    elif database == "pubmed":
        if year_from is not None or year_to is not None:
            filters = {"datetype": "pdat", "mindate": str(year_from or 1), "maxdate": str(year_to or 3000)}
        url, hits, records = _pubmed_search({"term": query, **filters}, limit, found_by)
    else:
        raise ValueError(f"unknown database {database!r}; expected openalex, crossref or pubmed")
    last = last_search_date()
    row = {
        "id": row_id, "time": stamp, "database": database, "query": query,
        "filters": {**filters, "last_search_date": last} if last else filters,
        "hits": hits, "returned": len(records), "url": url,
    }
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return records


def lookup(doi: str) -> Record | None:
    """The work with this DOI: from OpenAlex, else Crossref, else None."""
    doi = _bare_doi(doi)
    quoted = urllib.parse.quote(doi, safe="/")
    try:
        return _openalex_record(_get_json(_url(f"{OPENALEX}/doi:{quoted}", {})), ("lookup",))
    except RequestFailed as err:
        if err.status != 404:
            raise
    try:
        message = cast(dict[str, Any], _get_json(_url(f"{CROSSREF}/{quoted}", {}))["message"])
    except RequestFailed as err:
        if err.status != 404:
            raise
        return None
    return _crossref_record(message, ("lookup",))


def _openalex_work_id(record: Record) -> str:
    """The OpenAlex W id of a record: its own id, or found through its DOI."""
    if record.database == "openalex":
        return record.id.rsplit("/", 1)[-1]
    if record.doi:
        found = lookup(record.doi)
        if found is not None and found.database == "openalex":
            return found.id.rsplit("/", 1)[-1]
    raise ValueError(f"no OpenAlex work for record {record.id!r} to chase citations from")


def references(record: Record, *, limit: int = 500) -> list[Record]:
    """The works the record cites, from OpenAlex."""
    _, _, works = _openalex_pages({"filter": f"cited_by:{_openalex_work_id(record)}"}, limit)
    return [_openalex_record(w, (f"references:{record.id}",)) for w in works]


def citing(record: Record, *, limit: int = 500) -> list[Record]:
    """The works citing the record, from OpenAlex."""
    _, _, works = _openalex_pages({"filter": f"cites:{_openalex_work_id(record)}"}, limit)
    return [_openalex_record(w, (f"citing:{record.id}",)) for w in works]


def _title_key(title: str) -> str:
    return " ".join(re.sub(r"[\W_]+", " ", title.lower()).split())


def _title_year(r: Record) -> tuple[str, int] | None:
    key = _title_key(r.title)
    return (key, r.year) if key and r.year is not None else None


def merge_into(merged: list[Record], records: Iterable[Record]) -> tuple[int, int]:
    """Merge `records` into `merged` in place; returns (records appended as new works, records merged).

    Two records are one work when both have DOIs and they match (case aside), or, where either
    lacks a DOI, when their normalised titles and years match; a record joins the first such
    work in `merged`, filling its empty fields and adding its found_by. Rows are found through
    an index on DOI and on title and year, not by comparing every pair.
    """
    by_doi: dict[str, set[int]] = {}
    by_title: dict[tuple[str, int], set[int]] = {}

    def index(i: int, r: Record) -> None:
        if r.doi:
            by_doi.setdefault(r.doi.lower(), set()).add(i)
        ty = _title_year(r)
        if ty is not None:
            by_title.setdefault(ty, set()).add(i)

    for i, m in enumerate(merged):
        index(i, m)
    new = joined = 0
    for r in records:
        ty = _title_year(r)
        same_title: set[int] = by_title.get(ty, set()) if ty is not None else set()
        if r.doi:
            candidates = by_doi.get(r.doi.lower(), set()) | {i for i in same_title if not merged[i].doi}
        else:
            candidates = same_title
        if candidates:
            i = min(candidates)
            m = merged[i]
            filled = {
                f.name: getattr(r, f.name)
                for f in dataclasses.fields(Record)
                if f.name != "found_by" and getattr(m, f.name) in (None, "", ())
            }
            found_by = m.found_by + tuple(x for x in r.found_by if x not in m.found_by)
            merged[i] = dataclasses.replace(m, **filled, found_by=found_by)
            index(i, merged[i])
            joined += 1
        else:
            merged.append(r)
            index(len(merged) - 1, r)
            new += 1
    return new, joined


def merge(records: Iterable[Record]) -> list[Record]:
    """Duplicates merged by DOI, or by title and year where either lacks a DOI; first-seen order."""
    merged: list[Record] = []
    merge_into(merged, records)
    return merged


# ---------------------------------------------------------------- the command


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("--database", required=True, choices=("openalex", "crossref", "pubmed"))
    s.add_argument("--log", required=True, type=Path)
    s.add_argument("--limit", type=int, default=200)
    s.add_argument("--from", dest="year_from", type=int)
    s.add_argument("--to", dest="year_to", type=int)
    s.add_argument("--language", help="two-letter code; OpenAlex only")
    s.add_argument("query")
    for name in ("lookup", "references", "citing"):
        sub.add_parser(name).add_argument("doi")
    args = parser.parse_args(argv)
    command = cast(str, args.command)
    if command == "search":
        out = search(
            cast(str, args.query), cast(str, args.database), cast(Path, args.log), limit=cast(int, args.limit),
            year_from=cast(int | None, args.year_from), year_to=cast(int | None, args.year_to),
            language=cast(str | None, args.language),
        )
    else:
        found = lookup(cast(str, args.doi))
        if found is None:
            print(f"no record for DOI {args.doi} in OpenAlex or Crossref", file=sys.stderr)
            return 1
        out = [found] if command == "lookup" else (references if command == "references" else citing)(found)
    for r in out:
        print(json.dumps(dataclasses.asdict(r), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
