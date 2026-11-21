"""Upgrades this copy of the tool to the published version, keeping the user's own files.

Run as `python3 tools/upgrade.py [--from URL] [--yes]` from the repository root, standard library and git only.
It fetches branch `main` of the published repository (or of URL), writes every fetched file that is not one of the
user's, deletes every tracked file that is neither the user's nor in the fetched tree, and commits the result as
one commit, so `git revert` undoes it. The user's files are `cases/` (except `cases/README.md`), `user.md` and
`organizations/`; it never writes or deletes one. It refuses on a working tree that is not clean, and refuses a
deletion unless `--yes` is given. On any refusal or failure it prints one sentence and exits 1.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

REPOSITORY = "maxwelfare/cba-assistant"
PUBLISHED_URL = f"https://github.com/{REPOSITORY}.git"


class Refusal(Exception):
    """A refusal or failure, carrying the sentence shown to the user."""


def git(*args: str, stdin: str | None = None) -> str:
    """Runs git with pathspecs taken literally, returning its output; raises Refusal on failure."""
    result = subprocess.run(
        ["git", "--literal-pathspecs", *args], input=stdin, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Refusal(f"git {args[0]} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def is_users(path: str) -> bool:
    """Whether a path is one of the user's own files."""
    return (path.startswith("cases/") and path != "cases/README.md") or path == "user.md" or path.startswith(
        "organizations/"
    )


def paths(output: str) -> list[str]:
    """The paths in NUL-separated git output."""
    return [p for p in output.split("\0") if p]


def upgrade(source: str, yes: bool) -> None:
    if git("status", "--porcelain"):
        raise Refusal("The working tree has uncommitted changes; commit or discard them, then run the upgrade again.")
    git("fetch", "--quiet", "--no-tags", source, "main")
    fetched = paths(git("ls-tree", "-r", "-z", "--name-only", "FETCH_HEAD"))
    version = git("show", "FETCH_HEAD:VERSION").strip()
    to_write = [p for p in fetched if not is_users(p)]
    fetched_set = set(fetched)
    to_delete = [p for p in paths(git("ls-files", "-z")) if not is_users(p) and p not in fetched_set]
    if to_delete:
        print("The upgrade deletes these tracked files, which the published version does not carry:")
        for p in to_delete:
            print(f"  {p}")
        if not yes:
            raise Refusal("Nothing was changed; run again with --yes to delete them and upgrade.")
    try:
        if to_write:
            git("checkout", "FETCH_HEAD", "--pathspec-from-file=-", "--pathspec-file-nul", stdin="\0".join(to_write))
        if to_delete:
            git("rm", "-q", "--pathspec-from-file=-", "--pathspec-file-nul", stdin="\0".join(to_delete))
        if not git("status", "--porcelain"):
            print(f"This copy already matches version {version}; nothing was changed.")
            return
        git("commit", "-q", "-m", f"Upgrade the tool to version {version}")
    except Refusal:
        git("reset", "-q", "--hard", "HEAD")
        raise
    print(git("diff", "--stat", "HEAD~1", "HEAD"), end="")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade this copy of the tool to the published version.")
    parser.add_argument("--from", dest="source", default=PUBLISHED_URL, help="repository to upgrade from")
    parser.add_argument("--yes", action="store_true", help="allow deleting tracked files the new version drops")
    args = parser.parse_args()
    try:
        upgrade(str(args.source), bool(args.yes))
    except Refusal as refusal:
        print(refusal, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
