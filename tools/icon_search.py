"""Find Tabler icons by word, for a heading's `{icon=NAME}` (tools/typeset.py, Icons).

Run from the repository root:

    .venv/bin/python tools/icon_search.py WORD [WORD ...]

It prints up to 20 icons of `tools/typeset_layout/assets/tabler-icons/icons.json` whose name, category or tags
contain every word, ignoring case: one per line, the name first, then the category and the tags. Icons whose name
holds every word come first, then by name.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

INDEX = Path(__file__).resolve().parent / "typeset_layout" / "assets" / "tabler-icons" / "icons.json"
LIMIT = 20


def search(words: list[str]) -> list[str]:
    """The lines for the icons that match every word, at most LIMIT."""
    index = cast(dict[str, dict[str, object]], json.loads(INDEX.read_text()))
    wanted = [w.lower() for w in words]
    found: list[tuple[bool, str, str]] = []
    for name, icon in index.items():
        category = str(icon.get("category", ""))
        tags = [str(t) for t in cast(list[object], icon.get("tags", []))]
        fields = [name.lower(), category.lower(), *(t.lower() for t in tags)]
        if all(any(w in f for f in fields) for w in wanted):
            in_name = all(w in name.lower() for w in wanted)
            found.append((not in_name, name, f"{name}  [{category}]  {', '.join(tags)}"))
    return [line for _, _, line in sorted(found)[:LIMIT]]


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: tools/icon_search.py WORD [WORD ...]", file=sys.stderr)
        return 2
    for line in search(argv):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
