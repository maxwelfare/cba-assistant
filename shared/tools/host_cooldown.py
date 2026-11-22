"""tools/host_cooldown.py: after a server answers 429, nobody touches it for at least a day.

The owner, 2026-10-30 (an earlier session): "set up a hard rule that nobody ever
touches any server for any reason for at least a day after getting a 429 from it. or some other amount based on
best practices and how the system works".

THE PERIOD. Twenty-four hours from the refusal, or longer when the server's Retry-After asks for longer. The services
ask less of a well-behaved client: Crossref, "wait a short while and try your request again at a lower rate" (its REST
API access page, read 2026-10-30); OpenAlex, exponential backoff, its daily budget refilling at midnight UTC (its
error and authentication pages); NCBI, which may block an address that keeps breaking its three-a-second limit and
restores it only when the software registers its tool and email (E-utilities, NBK25497). The day is kept because the
429s on record came from seats running things again, not from one client's burst (notes/bad_calls/, cases 1 and 2):
a day takes the repeat off the table, covers OpenAlex's daily window, and costs no work that has to happen sooner.

WHAT CLOSES A HOST. An HTTP 429 from any host; a 403 from api.crossref.org or api.openalex.org, whose pages give 403
for a block (Crossref) or a rate limit (OpenAlex). A 403 elsewhere is an ordinary refusal and closes nothing.

THE LEDGER. One JSON object per line in ~/.cache/shared-tools/host_cooldowns.jsonl (HOST_COOLDOWN_LEDGER overrides):
{"host", "status", "at", "until", "by", "note"}, times ISO 8601 in UTC. Lines are only appended, save one case: at
the owner's word a host reopens early, its live line's `until` set to the time and his words and the old `until`
added to its note (an earlier session, 2026-11-08: "the key is saved. Now you can try the site
again"). A host is closed while any of its lines has `until` in the future. A project's own fetcher reads and writes
the file by this contract (the cost-benefit project's research/bibliography.py), so no project imports this folder.

ENFORCED THREE WAYS.
1. PreToolUse on Bash and WebFetch (`hook-pre`): a call that names a closed host in a URL (scheme://host) is denied,
   with the time the host opens. A bare host name is not a request and passes.
2. PostToolUse and PostToolUseFailure on WebFetch (`hook-post`): a WebFetch closes its one URL's host on the status
   its response reports (`code`), never on a number in the page it read, and tells the seat to stop. A Bash call
   passes: its output cannot say which host sent a status, or whether a server sent it at all rather than a page that
   documents one, so a seat that sees a refusal there closes the host by hand (`close`).
3. A fetcher in code checks the ledger before each request and closes the host on a 429 without retrying.

PRICE (CORE rule 10). The hook lines start Python only for a call whose text holds "://" (before, Bash and WebFetch)
or a WebFetch whose answer holds "429", "403" or "Too Many Requests" (after), about 50 ms each; every other call pays
a shell test or nothing. The check before a call also denies a command that only holds a closed host's URL as text,
such as a heredoc writing a test; write such a file with the Edit or Write tool, which the hook does not watch. A crash
of the tool lets the call through (Claude Code treats it as a non-blocking error) and is logged to
~/.cache/shared-tools/host_cooldown.log. Review 2026-12-01: every closure in the ledger is read for whether it was a
real refusal.

    .venv/bin/python -m tools.host_cooldown close HOST --status 429 --note "what was asked"
    .venv/bin/python -m tools.host_cooldown check HOST               # exit 1 while HOST is closed or stopped, 4 if unreadable
    .venv/bin/python -m tools.host_cooldown close HOST --status 403 --if-refusal   # writes only when the status closes

THE POLITE FETCH (`fetch URL --out PATH`, `fetch-status`). One URL per call, with a house User-Agent, a 2 MB/s cap and a 30 s timeout.
It follows redirects itself, one hop at a time (curl without -L, with --globoff so a URL is never a curl range):
a hop is the URL asked, then each URL the hop before redirected to. A redirect's body is removed; a chain stops,
exit 1 with nothing recorded, at an eleventh redirect, at one to an address that is not http(s) or names no host,
and at one to a URL already sent in the chain. Every URL it compares or records is in one form: the fragment
dropped, since a fragment is never sent (RFC 3986, 3.5), scheme and host in lower case (6.2.2.1), an empty path as
"/" (6.2.3); the TLS record alone keeps the URL asked as typed. Before each hop it refuses (exit 3) a host closed
on the ledger, a host this fetcher stopped in the last 24 hours, and a URL stopped in the last 24 hours, whether as
the URL asked or as the one that refused it; before the first hop, a URL whose TLS handshake failed (curl exit 35,
at any hop; one attempt). Exit 3 means the refused hop and every later one were not sent; an earlier hop may have
been, and PATH then holds no file. A refusal counts against the hop that drew it, its host and URL, with "Reached
from" the URL asked in each message. A 429, or a 403 from a host that closes on the ledger, stops that host at
once. Any other 403 stops only its URL, for every seat for 24 hours (the record's `refused_urls`, keyed by the URL
asked, with `host` and `final` the host and URL that refused); a 403 from the host on a second URL while an earlier
one's stop runs stops the host, its stop recording the number of distinct URLs that refused, since every fetch
leaves from one address (the owner's ruling, 2026-11-16, of Decision 4 of an earlier session on one refusal: "The host
recorded is the one that refused"). A hop refused unsent counts nothing. `check HOST` and `fetch-status` read the same two
records, the ledger and this fetch's: `check` answers for one host, exit 1 while the ledger closes it or this fetch
stops it (a stopped URL alone leaves its host open), else 0; `fetch-status` shows every stop: stopped hosts, stopped
URLs (`refused`), failed URLs and the hosts closed on the ledger, each closure with its `by` and `note`. `check`
only reads, with no lock and no write, so it answers on a cache folder it cannot write; it exits 4, printing why, when
either record exists but cannot be read or parsed (a ledger line that is valid JSON but not an object is skipped, as
for the hooks), and a missing record counts as
no stop. Requests to one host are spaced 3 s apart, 30 s for archive.org, which limits a whole address. Its record is ~/.cache/shared-tools/fetch_hosts.json (FETCH_HOSTS_RECORD
overrides), under a lock so concurrent seats in every project serialize; the 403 stop lives there, not on the
ledger, so the hooks do not deny a host for an ordinary refusal. Exit 0 on a 2xx saved to PATH, 1 on any other
failure, and PATH then holds no file this fetch wrote.

THE USER'S KEY. An https hop to a host that a row of the registry (library/access.toml) names as its key_host carries
the value the user holds for that row (tools/access.py, `value`): in the row's key_header, or, percent-encoded, as the
query parameter its key_query names, added to the hop's address unless the address already carries that parameter, in
which case it is sent as given. Curl reads the address and the header from a config on its standard input; where the
user holds none, the hop goes as any other. A header value that is not visible ASCII (white space or a control
character in it) raises before any request. The value is on no command line and in nothing the fetch prints, records
or saves, which name the address the caller gave and each redirect's: an answer whose body or redirect repeats it, as
given or encoded, ends the fetch, exit 1, the file removed, a status that stops a host still recorded.

    python shared/tools/host_cooldown.py fetch URL --out PATH
    python shared/tools/host_cooldown.py fetch-status    # stopped hosts, stopped URLs, failed URLs and hosts closed on the ledger
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Protocol, cast
from urllib.parse import parse_qsl, quote, unquote, unquote_plus, urldefrag, urlsplit, urlunsplit

CLOSED_FOR = timedelta(hours=24)
BLOCK_403 = frozenset({"api.crossref.org", "api.openalex.org"})
URL_HOST = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://(?:[^/\s'\"<>@]*@)?([A-Za-z0-9.-]+)")
# Only the forms an HTTP client prints: urllib's "HTTP Error 429", a status line "HTTP/1.1 429", a client's
# "HTTP 429:" (the cost-benefit project's RequestFailed), "429 Too Many Requests", and a status field. Prose that
# mentions a past refusal ("drew HTTP 429 from Crossref") does not match: two false alarms on 2026-10-30, when a
# seat printed a test's docstring and a build's welfare note.
STATUS = {
    code: re.compile(
        rf"HTTP Error {code}\b|HTTP/\d(?:\.\d)?\s+{code}\b|HTTP {code}:|\b{code}\s*[:\-]?\s*{phrase}"
        rf"|status(?:[_ ]?code|Code)?[\\\x22']*\s*[:=]?\s*{code}\b" + ("|(?-i:Too Many Requests)" if code == 429 else ""),
        re.IGNORECASE,
    )
    for code, phrase in ((429, "Too Many Requests"), (403, "Forbidden"))
}
RETRY_AFTER = re.compile(r"Retry-After\"?\s*[:=]\s*\"?(\d+)", re.IGNORECASE)


def ledger_path() -> Path:
    return Path(os.environ.get("HOST_COOLDOWN_LEDGER") or Path.home() / ".cache" / "shared-tools" / "host_cooldowns.jsonl")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


def _rows() -> list[dict[str, Any]]:
    path = ledger_path()
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded: object = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(cast(dict[str, Any], loaded))
    return rows


def closed(now: datetime | None = None) -> dict[str, dict[str, Any]]:
    """Each closed host's line with the latest `until`."""
    t = now or _now()
    out: dict[str, dict[str, Any]] = {}
    for row in _rows():
        until = datetime.fromisoformat(str(row["until"]))
        host = str(row["host"]).lower()
        if until > t and (host not in out or until > datetime.fromisoformat(str(out[host]["until"]))):
            out[host] = row
    return out


def retry_after_seconds(value: str | None, now: datetime | None = None) -> float | None:
    """A Retry-After value in seconds, from its delay-seconds or HTTP-date form (RFC 9110, 10.2.3); None if unreadable."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - (now or _now())).total_seconds())


def close(host: str, status: int, *, by: str, note: str = "", retry_after: str | None = None,
          now: datetime | None = None) -> datetime:
    """Close `host` for a day, or for its Retry-After if longer; returns when it opens."""
    t = now or _now()
    wait = retry_after_seconds(retry_after, t)
    until = t + max(CLOSED_FOR, timedelta(seconds=wait or 0))
    row = {"host": host.lower(), "status": status, "at": _iso(t), "until": _iso(until), "by": by, "note": note}
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return until


def closes(host: str, status: int) -> bool:
    """Whether `status` from `host` closes it on the ledger (WHAT CLOSES A HOST)."""
    return status == 429 or (status == 403 and host.lower() in BLOCK_403)


def hosts_in(text: str) -> list[str]:
    seen: list[str] = []
    for m in URL_HOST.finditer(text):
        host = m.group(1).lower().rstrip(".")
        if host and host not in seen:
            seen.append(host)
    return seen


def _call_text(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        ti = cast(dict[str, Any], tool_input)
        return " ".join(str(ti.get(k) or "") for k in ("command", "url"))
    return ""


def _result_text(payload: dict[str, Any]) -> str:
    return " ".join(json.dumps(v) for v in (payload.get("tool_response"), payload.get("error")) if v is not None)


def _who(payload: dict[str, Any]) -> str:
    agent = payload.get("agent_type") or payload.get("agent_id")
    session = str(payload.get("session_id") or "")[:8]
    return f"session {session}" + (f", agent {agent}" if agent else "")


def hook_pre(payload: dict[str, Any], now: datetime | None = None) -> dict[str, Any] | None:
    shut = closed(now)
    hit = [h for h in hosts_in(_call_text(payload)) if h in shut]
    if not hit:
        return None
    lines = [f"{h} refused with HTTP {shut[h]['status']} at {shut[h]['at']} and is closed until {shut[h]['until']} (UTC)"
             for h in hit]
    reason = ("; ".join(lines) + ". Nobody touches a server for a day after it refuses for load (the owner, 2026-10-30; "
              "shared/tools/host_cooldown.py). Do not retry it by another tool or URL; "
              "report what is waiting on it.")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def _webfetch_status(payload: dict[str, Any], result: str) -> int | None:
    """The status of WebFetch's one URL: the `code` its response reports, so a page that documents a 429 counts as the
    200 it came with; a failed call that carries no code is read from what came back."""
    response = payload.get("tool_response")
    code = str(cast(dict[str, Any], response).get("code")) if isinstance(response, dict) else ""
    if code.isdigit():
        return int(code)
    return next((c for c in (429, 403) if STATUS[c].search(result)), None)


def hook_post(payload: dict[str, Any], now: datetime | None = None) -> dict[str, Any] | None:
    """A WebFetch closes its one URL's host on a status that closes it; every other tool passes."""
    if payload.get("tool_name") != "WebFetch":
        return None
    result = _result_text(payload)
    url = _call_text(payload).strip()
    host = (urlsplit(url).hostname or "").lower()
    status = _webfetch_status(payload, result)
    if not host or status is None or not closes(host, status):
        return None
    m = RETRY_AFTER.search(result)
    until = close(host, status, by=_who(payload), note=f"WebFetch of {url} answered {status}",
                  retry_after=m.group(1) if m else None, now=now)
    text = (f"{host} answered HTTP {status} and is closed for every project until {_iso(until)} (UTC). Stop: do "
            "not run this again or reach the host another way; report it (the owner's rule, tools/host_cooldown.py).")
    event = str(payload.get("hook_event_name") or "PostToolUse")
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


USER_AGENT = "PoliteResearchFetch/1.0 (academic parameter-sourcing; one URL per call)"
STOP_STATUSES = (403, 429)
STOP_FOR_S = 24 * 3600.0
PAUSE_S = 3.0
ARCHIVE_PAUSE_S = 30.0
TLS_EXIT = 35
MAX_REDIRECTS = 10
VISIBLE_ASCII = re.compile(r"[\x21-\x7e]+\Z")


class Runner(Protocol):
    """(url to send, out[, a header line]) -> (curl exit, http status or 0, redirect URL or "")."""

    def __call__(self, url: str, out: Path, header: str = "", /) -> "tuple[int, int, str]": ...


def fetch_record() -> Path:
    return Path(os.environ.get("FETCH_HOSTS_RECORD") or Path.home() / ".cache" / "shared-tools" / "fetch_hosts.json")


def pause_for(host: str) -> float:
    return ARCHIVE_PAUSE_S if host == "archive.org" or host.endswith(".archive.org") else PAUSE_S


@contextmanager
def _locked(record: Path) -> Generator[dict[str, Any]]:
    record.parent.mkdir(parents=True, exist_ok=True)
    with open(record.with_suffix(".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data: dict[str, Any] = json.loads(record.read_text()) if record.exists() else {}
        for k in ("stopped", "refused_urls", "failed_urls", "last"):
            data.setdefault(k, {})
        yield data
        record.write_text(json.dumps(data, indent=1, sort_keys=True))


def _quoted(text: str) -> str:
    """`text` as a quoted value of a curl config file, whose escapes are \\\\, \\", \\n, \\r and \\t."""
    for raw, escaped in (("\\", "\\\\"), ('"', '\\"'), ("\n", "\\n"), ("\r", "\\r"), ("\t", "\\t")):
        text = text.replace(raw, escaped)
    return f'"{text}"'


def _curl(url: str, out: Path, header: str = "", /) -> "tuple[int, int, str]":
    """One request. The address and any header line go to curl as a config on its standard input (`-K -`), so a value
    either carries is on no command line."""
    config = f"url = {_quoted(url)}\n" + (f"header = {_quoted(header)}\n" if header else "")
    r = subprocess.run(["curl", "-sS", "--globoff", "-A", USER_AGENT, "--limit-rate", "2M", "--max-time", "30",
                        "-o", str(out), "-w", "%{http_code} %{redirect_url}", "-K", "-"],
                       input=config, capture_output=True, text=True)
    code, _, location = r.stdout.strip().partition(" ")
    return r.returncode, int(code) if code.isdigit() else 0, location


def url_key(url: str) -> str:
    """The form a URL is compared and recorded in: no fragment, which is never sent (RFC 3986, 3.5); scheme and host
    in lower case (6.2.2.1); an empty path as "/" (6.2.3); path and query as they came."""
    p = urlsplit(urldefrag(url).url)
    userinfo, at, hostport = p.netloc.rpartition("@")
    return p._replace(scheme=p.scheme.lower(), netloc=userinfo + at + hostport.lower(), path=p.path or "/").geturl()


def _keyed(hop: str) -> tuple[str, str, str]:
    """(the address to send, the header line to send or "", the user's value they carry or "") for a hop: the hop as
    given, with the row's key_header or with its key_query parameter added, the value percent-encoded, where the hop
    goes by https to a row's key_host and the user holds a value; a hop that already carries that parameter is sent as
    given. Raises for a header value that is not visible ASCII, naming the variable and nothing of the value."""
    p = urlsplit(hop)
    if p.scheme.lower() != "https":
        return hop, "", ""
    root = str(Path(__file__).resolve().parent.parent)   # imported here, not at the top: the hooks of every Bash call
    if root not in sys.path:                             # import this module, and the file run by its path has only
        sys.path.insert(0, root)                         # its own folder on the import path
    from tools import access
    reg = access.rows()
    row = next((r for r in reg.values() if r.get("key_host") == p.hostname), None)
    held = access.value(row["env_var"], reg) if row else ""
    if not row or not held:
        return hop, "", ""
    param = row.get("key_query", "")
    if param:
        if any(name == param for name, _ in parse_qsl(p.query, keep_blank_values=True)):
            return hop, "", ""
        pair = f"{param}={quote(held, safe='')}"
        return urlunsplit(p._replace(query=f"{p.query}&{pair}" if p.query else pair, fragment="")), "", held
    if not VISIBLE_ASCII.match(held):
        raise ValueError(f"the value held for {row['env_var']} has a character a header cannot carry (white space, a "
                         "control character or one outside ASCII); nothing was sent")
    return hop, row["key_header"].replace("{value}", held), held


def _repeats(text: str, value: str) -> bool:
    """Whether `text` holds `value` as given or percent-encoded in any way: the text is decoded and searched, so
    lower-case hex and a partly encoded value are caught as the fully encoded one is."""
    return value in text or value in unquote(text) or value in unquote_plus(text)


def _refused_403(data: dict[str, Any], host: str, now: float) -> int:
    """The distinct URLs (`final`, else the key) that `host` refused by a 403 whose stop is still running."""
    return len({r.get("final", u) for u, r in data["refused_urls"].items()
                if r["host"] == host and r["status"] == 403 and r["until"] > now})


def fetch(url: str, out: Path, *, by: str = "host_cooldown fetch", run: Runner = _curl,
          clock: Callable[[], float] = time.time, sleep: Callable[[float], None] = time.sleep) -> int:
    """One polite fetch of `url` to `out`, following redirects hop by hop (THE POLITE FETCH); returns the exit code.
    Every non-zero exit or raise after a hop was sent removes `out`, so a failed answer's body is never left as the
    source."""
    sent: list[str] = []   # the hops of this chain already sent, in compared form
    code = 1
    try:
        code = _fetch_chain(url, out, sent, by=by, run=run, clock=clock, sleep=sleep)
    finally:
        if code != 0 and sent:
            out.unlink(missing_ok=True)
    return code


def _fetch_chain(url: str, out: Path, sent: list[str], *, by: str, run: Runner,
                 clock: Callable[[], float], sleep: Callable[[float], None]) -> int:
    """The hops of `fetch`, each appended to `sent` as it goes out; returns the exit code and leaves `out` to it."""
    if not urlsplit(url).hostname:
        print(f"fetch: {url!r} names no host")
        return 1
    key = url_key(url)
    hop = url
    while True:
        hop_key = url_key(hop)
        host = urlsplit(hop_key).hostname or ""
        via = f" Reached from {key}." if hop_key != key else ""
        to_send, header, key_value = _keyed(hop)
        with _locked(fetch_record()) as data:
            now = clock()
            shut = closed(datetime.fromtimestamp(now, timezone.utc)).get(host)
            stop = data["stopped"].get(host)
            if shut:
                print(f"STOPPED: {host} is closed on the machine's host cooldown ledger until {shut['until']} "
                      f"({shut['status']} at {shut['at']}). Mark the source catalog-only and move on.{via}")
                return 3
            if stop and now < stop["until"]:
                print(f"STOPPED: {host} answered {stop['status']} to {stop['url']}; no request goes to it for another "
                      f"{(stop['until'] - now) / 3600:.1f} h. Mark the source catalog-only with that status and move "
                      f"on.{via}")
                return 3
            live = [r for u, r in data["refused_urls"].items()
                    if hop_key in (u, r.get("final", u)) and now < r["until"]]
            if live:
                refused = max(live, key=lambda r: float(r["until"]))
                final = refused.get("final", hop_key)
                print(f"STOPPED: {refused['host']} answered {refused['status']} to {final}; no request goes to that URL "
                      f"for another {(refused['until'] - now) / 3600:.1f} h. Take another route to this work."
                      + (f" Reached from {key}." if final != key else ""))
                return 3
            if not sent and url in data["failed_urls"]:
                print(f"STOPPED: {url} failed at the TLS handshake; one attempt is the rule. Mark it catalog-only.")
                return 3
            wait = data["last"].get(host, 0.0) + pause_for(host) - now
            if wait > 0:
                sleep(wait)
            data["last"][host] = clock()
        sent.append(hop_key)
        exit_code, status, location = run(to_send, out, header)
        repeated = bool(key_value) and (_repeats(location, key_value) or (
            out.is_file() and _repeats(out.read_bytes().decode("utf-8", "replace"), key_value)))
        if repeated:   # removed at once, not at the wrapper's exit, so a crash in the lock below leaves no key on disk
            out.unlink(missing_ok=True)
        with _locked(fetch_record()) as data:
            now = clock()
            if status in STOP_STATUSES:
                entry = {"status": status, "host": host, "final": hop_key, "at": now, "until": now + STOP_FOR_S}
                old = data["stopped"].get(host)
                if not closes(host, status):
                    data["refused_urls"][key] = entry
                    n = _refused_403(data, host, now)
                    if n < 2:
                        held = (old and now < old["until"]) or closed(datetime.fromtimestamp(now, timezone.utc)).get(host)
                        state = (f"{host} is already stopped" if held else "the host stays open. A second 403 on another "
                                 f"URL of {host} within the day stops the host")
                        print(f"fetch: {host} answered 403 to {hop_key}; that URL is stopped for every seat for 24 h and "
                              f"{state}. Take another route to this work; do not retry.{via}")
                        return 1
                    data["stopped"][host] = {"status": status, "url": hop_key, "urls": n,
                                             "until": max(now + STOP_FOR_S, old["until"] if old else 0.0)}
                    print(f"fetch: {host} answered 403 to {n} URLs within the day; it is stopped for every seat for "
                          f"24 h. Mark the source catalog-only with that status and move on; do not retry.{via}")
                    return 1
                # a 429, or a 403 from a host that closes on the ledger
                if via:
                    data["refused_urls"][key] = entry
                data["stopped"][host] = {"status": status, "url": hop_key,
                                         "until": max(now + STOP_FOR_S, old["until"] if old else 0.0)}
                note = f"{hop_key} (reached from {key})" if via else hop_key
                until = close(host, status, by=by, note=note, now=datetime.fromtimestamp(now, timezone.utc))
                print(f"fetch: {host} answered {status}; it is stopped for every seat for a day for every project (the "
                      f"host cooldown ledger, until {_iso(until)}). Mark the source catalog-only with that status and "
                      f"move on; do not retry.{via}")
                return 1
            if exit_code == TLS_EXIT:
                data["failed_urls"][url] = {"exit": exit_code, "at": now}
                print(f"fetch: TLS handshake failed for {url}; catalog-only, no retry.")
                return 1
        if repeated:   # an answer that repeats the key is not kept, and its redirect is not followed
            print(f"fetch: the answer to {hop_key} repeats the user's key; nothing is kept and nothing more is sent")
            return 1
        if not location:
            break
        out.unlink(missing_ok=True)   # the redirect's body is not the page
        target = urlsplit(location)
        if len(sent) > MAX_REDIRECTS:
            print(f"fetch: {url} redirected more than {MAX_REDIRECTS} times; nothing more is sent")
            return 1
        if target.scheme.lower() not in ("http", "https") or not target.hostname:
            print(f"fetch: {url} redirects to {location}, which is not an http address; nothing more is sent")
            return 1
        if url_key(location) in sent:
            print(f"fetch: {url} redirects in a loop at {url_key(location)}; nothing more is sent")
            return 1
        hop = location
    if exit_code != 0 or not 200 <= status < 300:
        print(f"fetch: {url} gave HTTP {status}, curl exit {exit_code}")
        return 1
    print(f"fetch: saved {url} to {out} (HTTP {status})")
    return 0


def fetch_status(now: float | None = None) -> int:
    t = time.time() if now is None else now
    with _locked(fetch_record()) as data:
        live = {h: s for h, s in data["stopped"].items() if s["until"] > t}
        for h, s in sorted(live.items()):
            on = f"{s['urls']} URLs, the last {s['url']}" if "urls" in s else s["url"]
            print(f"stopped {h}: {s['status']} on {on}, {(s['until'] - t) / 3600:.1f} h left")
        for u, r in sorted(data["refused_urls"].items()):
            if r["until"] > t:
                at = f" at {r['final']}" if r.get("final", u) != u else ""
                print(f"refused {u}: {r['status']} from {r['host']}{at}, {(r['until'] - t) / 3600:.1f} h left")
        for u, f in sorted(data["failed_urls"].items()):
            print(f"failed  {u}: curl exit {f['exit']}")
    for host, row in sorted(closed().items()):
        print(f"closed  {host}: HTTP {row['status']} on the ledger until {row['until']}, by {row['by']}: {row['note']}")
    return 0


def check(host: str, now: float | None = None) -> int:
    """Exit 1, naming HOST, while the ledger closes it or this fetch stops it; 0 when it is clear; 4 when either record
    exists but cannot be read. Reads only: no lock and no write, so a read-only cache folder answers as a writable one."""
    t = time.time() if now is None else now
    h = host.lower()
    record = fetch_record()
    try:
        data: object = json.loads(record.read_text()) if record.exists() else {}
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
        stop = cast(dict[str, Any], cast(dict[str, Any], data).get("stopped") or {}).get(h)
        said = (f"{host} stopped by the fetch (HTTP {stop['status']} on {stop['url']}) for another "
                f"{(stop['until'] - t) / 3600:.1f} h") if stop and stop["until"] > t else ""
    except Exception as e:  # any read failure is exit 4, never the stop code 1
        print(f"check: could not read the fetch record {record}: {e!r}", file=sys.stderr)
        return 4
    if said:
        print(said)
        return 1
    try:
        row = closed(datetime.fromtimestamp(t, timezone.utc)).get(h)
    except Exception as e:  # any read failure is exit 4, never the stop code 1
        print(f"check: could not read the host cooldown ledger {ledger_path()}: {e!r}", file=sys.stderr)
        return 4
    if row:
        print(f"{host} closed until {row['until']} (UTC)")
        return 1
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("close")
    c.add_argument("host")
    c.add_argument("--status", type=int, default=429)
    c.add_argument("--retry-after")
    c.add_argument("--note", default="")
    c.add_argument("--by", default="by hand")
    c.add_argument("--if-refusal", action="store_true", help="write only when the status closes the host")
    f = sub.add_parser("fetch")
    f.add_argument("url")
    f.add_argument("--out", type=Path, required=True)
    f.add_argument("--by", default="host_cooldown fetch")
    sub.add_parser("fetch-status")   # every stop: hosts and URLs this fetch stopped, failed URLs, ledger closures
    k_help = ("one host, from the same two records, read without writing: exit 0 clear, 1 while closed or stopped, "
              "4 when a record exists but cannot be read")
    k = sub.add_parser("check", help=k_help, description=k_help)
    k.add_argument("host")
    sub.add_parser("hook-pre")
    sub.add_parser("hook-post")
    a = p.parse_args(argv)
    if a.cmd == "fetch":
        return fetch(a.url, a.out, by=a.by)
    if a.cmd == "check":
        return check(a.host)
    if a.cmd == "fetch-status":
        return fetch_status()
    if a.cmd == "close":
        if a.if_refusal and not closes(a.host, a.status):
            print(f"{a.host}: HTTP {a.status} closes nothing on the ledger")
            return 0
        print(f"{a.host} closed until {_iso(close(a.host, a.status, by=a.by, note=a.note, retry_after=a.retry_after))} (UTC)")
        return 0
    loaded: object = json.loads(sys.stdin.read() or "{}")
    payload = cast(dict[str, Any], loaded) if isinstance(loaded, dict) else {}
    out = hook_pre(payload) if a.cmd == "hook-pre" else hook_post(payload)
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
