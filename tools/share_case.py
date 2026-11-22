"""Share one case (roadmap 2.5): a new repository from the template holding the tool and that one case, and the
case taken out of the user's repository.

Run from the root of the user's repository:

    .venv/bin/python tools/share_case.py CASE --to OWNER/REPO [--template OWNER/REPO]
    .venv/bin/python tools/share_case.py CASE --dry-run --template PATH_OR_URL --to NEW_PATH

Steps, in order, each stopping the run on failure:

1. Refuse unless CASE names a folder directly under `cases/` committed at HEAD and none of its tracked files has an
   uncommitted change, so the state shared and the state removed are the same and nothing of the user's is lost; and
   refuse, naming each file, when a stored source whose `licence` (in its source.json or in the case's sources.toml,
   either one) forbids redistribution has any file besides its source.json and .gitignore tracked in git.
2. Make the repository. Real mode: `gh repo create OWNER/REPO --private --template TEMPLATE` (GitHub copies the
   template's files in one commit). Dry run: a bare repository at NEW_PATH holding the template's branch `main`.
3. Clone it into a temporary folder, add the case's files as committed at the user's HEAD (`git archive`, so files
   git ignores, such as licensed copies of sources, and untracked files never travel; every committed stored source
   travels whole, text and original: CLAUDE.md, "Where things live"), put the credit line in the first lines of
   README.md (`notes/what_a_case_delivers.md`), commit once and push `main`.
4. In the user's repository, delete the case's tracked files in one commit of their own. Untracked and ignored files
   in the folder stay on disk and are listed.

The case's version tags stay in the user's repository; versions made in the shared one follow
`notes/case_pipeline.md` 2.4.2.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import cast

CREDIT = "Produced with the help of the maxwelfare.com CBA AI Assistant."
TEMPLATE = "maxwelfare/cba-assistant"
# Wordings in a stored source's `licence` that say its copy may not leave this machine, as the project's records write
# them ("paywalled", "book; not free", "the publisher's subscription copy"). Plain "licensed" is not one: free records
# say "AMA-licensed CPT tables were not opened" and "data licensed Creative Commons".
NOT_REDISTRIBUTABLE = re.compile(r"local copy only|not for redistribution|library access|paywall|subscription|"
                                 r"\bnot free\b|no licen[cs]e permits redistribution", re.I)


class Refused(Exception):
    pass


def run(cmd: list[str], cwd: Path, data: bytes | None = None) -> bytes:
    done = subprocess.run(cmd, cwd=cwd, input=data, capture_output=True)
    if done.returncode != 0:
        raise Refused(f"{' '.join(cmd)} (in {cwd}) failed:\n{done.stderr.decode(errors='replace').strip()}")
    return done.stdout


def git(cwd: Path, *args: str) -> str:
    return run(["git", *args], cwd).decode()


def check_case(user: Path, case: str) -> str:
    """The case's folder as a path from the root; refuses a name that is not a folder directly under cases/ at HEAD,
    an uncommitted or changed case, and a licensed source whose copy git tracks."""
    folders = git(user, "ls-tree", "-d", "--name-only", "HEAD", "cases/").splitlines()
    folder = f"cases/{case}"
    if "/" in case or "\\" in case or ".." in case or folder not in folders:
        raise Refused(f"{case!r} is not the name of a case folder committed directly under cases/")
    changed = [line for line in git(user, "status", "--porcelain", "--", folder).splitlines()
               if not line.startswith("??")]
    if changed:
        raise Refused(f"{folder} has uncommitted changes; commit or discard them first:\n" + "\n".join(changed))
    tracked = git(user, "ls-tree", "-r", "--name-only", "HEAD", "--", folder).splitlines()
    licences: dict[str, list[str]] = {}  # source key -> its recorded licences
    if f"{folder}/sources.toml" in tracked:
        for key, entry in tomllib.loads(git(user, "show", f"HEAD:{folder}/sources.toml")).items():
            if isinstance(entry, dict):
                licences.setdefault(key, []).append(str(cast(dict[str, object], entry).get("licence") or ""))
    for record in (p for p in tracked if re.fullmatch(re.escape(folder) + r"/sources/[^/]+/source\.json", p)):
        licence = json.loads(git(user, "show", f"HEAD:{record}")).get("licence") or ""
        licences.setdefault(record.split("/")[-2], []).append(str(licence))
    licensed = [p for p in tracked if (parts := p[len(folder) + 1:].split("/"))[0] == "sources" and len(parts) > 2
                and parts[-1] not in ("source.json", ".gitignore")
                and any(NOT_REDISTRIBUTABLE.search(text) for text in licences.get(parts[1], []))]
    if licensed:
        raise Refused("these files of sources whose licence forbids redistribution are tracked in git; untrack them "
                      "(git rm --cached) and list them in .gitignore first:\n" + "\n".join(licensed))
    return folder


def add_credit(readme: Path) -> None:
    lines = readme.read_text(encoding="utf-8").splitlines(keepends=True) if readme.exists() else []
    if any(CREDIT in line for line in lines[:5]):
        return
    at = 1 if lines and lines[0].startswith("#") else 0
    lines[at:at] = ["\n", f"<sub>{CREDIT}</sub>\n"] if at else [f"<sub>{CREDIT}</sub>\n", "\n"]
    readme.write_text("".join(lines), encoding="utf-8")


def make_repository(dry_run: bool, template: str, to: str, work: Path) -> str:
    """Creates the empty-of-case shared repository; returns the address to clone and push to."""
    if dry_run:
        dest = Path(to).resolve()
        if dest.exists():
            raise Refused(f"{dest} exists already")
        git(work, "init", "-q", "--bare", "-b", "main", str(dest))
        seed = work / "seed"
        git(work, "clone", "-q", "--single-branch", "-b", "main", template, str(seed))
        git(seed, "push", "-q", str(dest), "main:main")
        return str(dest)
    run(["gh", "repo", "create", to, "--private", "--template", template], work)
    return f"https://github.com/{to}.git"


def clone_when_ready(address: str, into: Path, work: Path, tries: int = 10) -> None:
    """GitHub fills a repository made from a template a few seconds after creating it."""
    for attempt in range(tries):
        try:
            git(work, "clone", "-q", "-b", "main", address, str(into))
            return
        except Refused:
            if attempt == tries - 1:
                raise
            time.sleep(3)


def share(user: Path, case: str, template: str, to: str, dry_run: bool) -> None:
    folder = check_case(user, case)
    head = git(user, "rev-parse", "--short", "HEAD").strip()
    with tempfile.TemporaryDirectory(prefix="share_case_") as tmp:
        work = Path(tmp)
        address = make_repository(dry_run, template, to, work)
        clone = work / "shared"
        clone_when_ready(address, clone, work)
        if (clone / folder).exists():
            raise Refused(f"the template already holds {folder}")
        run(["tar", "-x", "-C", str(clone)], work, run(["git", "archive", "HEAD", "--", folder], user))
        add_credit(clone / "README.md")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "-m", f"Add case {case}, as committed at {head} of its source repository")
        git(clone, "push", "-q", "origin", "main:main")
    git(user, "rm", "-r", "-q", "--", folder)
    git(user, "commit", "-q", "-m", f"Remove case {case}: shared to {to}", "--", folder)
    left = sorted(p.relative_to(user).as_posix() for p in (user / folder).rglob("*") if p.is_file()) \
        if (user / folder).exists() else []

    print(f"Shared {folder} (as committed at {head}) to {to}, and removed it from this repository in one commit.")
    if left:
        print(f"Left on this machine, never shared (untracked or ignored by git): {', '.join(left)}")
    if dry_run:
        print("Dry run: no GitHub repository was made. In a real run, collaborators are invited on the new "
              "repository's page, Settings, Collaborators, Add people; or the session invites a GitHub username.")
    else:
        print(f"To invite collaborators: open https://github.com/{to}/settings/access and choose Add people, or "
              "give the session their GitHub usernames and it invites them. The repository is private.")
    print("The case's earlier version tags stay in this repository; tag new versions in the shared one "
          "(notes/case_pipeline.md 2.4.2).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("case", help="the case's folder name under cases/")
    parser.add_argument("--to", required=True, help="OWNER/REPO on GitHub; under --dry-run, a new local path")
    parser.add_argument("--template", default=TEMPLATE,
                        help=f"the template repository (default {TEMPLATE}); under --dry-run, a git path or URL")
    parser.add_argument("--dry-run", action="store_true", help="make a local bare repository and call no GitHub; the case is still removed from this "
                             "repository in a real commit, which a post-commit hook may push")
    args = parser.parse_args(argv)
    try:
        share(Path.cwd(), str(args.case), str(args.template), str(args.to), bool(args.dry_run))
    except Refused as e:
        print(f"share_case: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
