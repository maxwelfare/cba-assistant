"""The SessionStart hook: greets a copy with no case yet, and says once a day when a newer version is published.

Run as `python3 tools/update_check.py` from the repository root, standard library only, so it runs before any
virtual environment exists. It compares `./VERSION` with the published one, at most once a day, and makes one line
for Claude when the published one is newer. In a copy whose cases/ holds no case folder yet it prints Claude Code's
hook JSON: the welcome line in `systemMessage`, shown to the user when the hook's stdin JSON gives "source" as
"startup" (or stdin is missing or unparsable), not on resume, clear or compact, and the update line, if any, in
`hookSpecificOutput.additionalContext`. Otherwise it prints the update line alone as plain text, or nothing. An error prints nothing of its own and the script always exits 0. The environment variable CBA_UPDATE_URL,
when set, replaces the published VERSION's address.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import cast

REPOSITORY = "maxwelfare/cba-assistant"
PUBLISHED_VERSION_URL = f"https://raw.githubusercontent.com/{REPOSITORY}/main/VERSION"
TIMEOUT_SECONDS = 3
STAMP = Path(".git") / "cba_update_check"
ONE_DAY_SECONDS = 24 * 60 * 60
WELCOME = (
    "Welcome to the maxwelfare.com CBA AI Assistant: tell it the policy, program or decision you want a "
    "cost-benefit analysis of, and it starts by asking about it."
)


def parse(text: str) -> tuple[str, int] | None:
    """A version as (ISO date, suffix), the suffix 0 when absent; None when the text is not a version."""
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})(?:\.(\d+))?", text.strip())
    if match is None:
        return None
    return match.group(1), int(match.group(2) or 0)


def has_no_case() -> bool:
    """True in a copy whose cases/ folder exists and holds no case folder (a directory not named with a dot)."""
    cases = Path("cases")
    return cases.is_dir() and not any(p.is_dir() and not p.name.startswith(".") for p in cases.iterdir())


def is_startup() -> bool:
    """True when the hook's stdin JSON gives "source" as "startup", or when stdin is missing or unparsable."""
    if sys.stdin is None or sys.stdin.isatty():
        return True
    try:
        data: object = json.loads(sys.stdin.read())
    except ValueError:
        return True
    if not isinstance(data, dict):
        return True
    return cast("dict[str, object]", data).get("source", "startup") == "startup"


def update_line() -> str | None:
    """The line telling Claude to offer an upgrade, when a daily check finds a newer published version."""
    local_path = Path("VERSION")
    if not local_path.is_file() or not STAMP.parent.is_dir():
        return None
    local_text = local_path.read_text().strip()
    local = parse(local_text)
    if local is None:
        return None
    if STAMP.exists() and time.time() - STAMP.stat().st_mtime < ONE_DAY_SECONDS:
        return None
    STAMP.touch()
    url = os.environ.get("CBA_UPDATE_URL") or PUBLISHED_VERSION_URL
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
        published_text = response.read(64).decode().strip()
    published = parse(published_text)
    if published is None or published <= local:
        return None
    return (
        f"A newer version of the tool is published ({published_text}; this copy is {local_text}): "
        "offer the user, once and in one sentence, to upgrade by running `python3 tools/upgrade.py`, "
        "which keeps their cases, user.md and organizations/."
    )


def main() -> None:
    try:
        update = update_line()
    except Exception:
        update = None
    try:
        welcome = has_no_case() and is_startup()
    except Exception:
        welcome = False
    if welcome:
        output: dict[str, object] = {"systemMessage": WELCOME}
        if update is not None:
            output["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": update}
        print(json.dumps(output))
    elif update is not None:
        print(update)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
