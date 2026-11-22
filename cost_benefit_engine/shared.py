"""The shared folder, found in one place for the project, and the shared sheet package loaded from it.

`SHARED` is `shared/` inside a public copy of this project (tools/release_check.py), else the shared folder beside the
project. A command line runs a shared tool from it, with this project's Python: `[sys.executable, "-m",
"tools.sheets.script", ...]` with `cwd=SHARED`, as the copy runs `tools.source_store` (tools/release_claude.md item 4).

`sheets(name)` returns a module of the shared sheet package, `tools.sheets.<name>` (script, importer, inplace), in this
process. This project's `tools` folder and the shared folder's `tools` package share a name, and putting the shared
folder on sys.path would hide the project's own tools, so the package is registered by its path as `tools.sheets` and
its modules import as usual beneath it. The commit's type check reads this tree alone, so a module comes back typed
Any; a caller binds the names it uses with their types where it can.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared" if (ROOT / "shared").is_dir() else ROOT.parent / "shared"


def sheets(name: str) -> Any:
    """The shared module tools/sheets/<name>.py, loaded once."""
    if "tools.sheets" not in sys.modules:
        init = SHARED / "tools" / "sheets" / "__init__.py"
        spec = importlib.util.spec_from_file_location("tools.sheets", init, submodule_search_locations=[str(init.parent)])
        if not init.is_file() or spec is None or spec.loader is None:
            raise ImportError(f"the shared sheet package, {init}, is not in this repository or beside it")
        package = importlib.util.module_from_spec(spec)
        sys.modules["tools.sheets"] = package
        spec.loader.exec_module(package)
    return importlib.import_module(f"tools.sheets.{name}")
