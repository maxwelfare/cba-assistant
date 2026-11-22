"""Quotes checked against a stored text: the shared quote checker, `shared/tools/quotes.py`, loaded by its path.

The checker lives in the shared folder (its header states the rules: the text's two plain forms, the number boundary,
`...` as text left out); this module only finds it, in the copy's `shared/` folder or in the shared folder beside the
project, and hands on its functions: `normalise` and `quote_in`, and `forms` and `found_in`, the shared file's
`plain_forms` and `quote_in_forms`, for a caller checking many quotes against one text made plain once.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

_ROOT = Path(__file__).resolve().parent.parent
_PATH = next((f / "tools" / "quotes.py" for f in (_ROOT / "shared", _ROOT.parent / "shared")
              if (f / "tools" / "quotes.py").is_file()), None)
_SPEC = importlib.util.spec_from_file_location("shared_tools_quotes", _PATH) if _PATH else None
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("the shared quote checker, shared/tools/quotes.py, is not in this repository or beside it")
_shared = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _shared
_SPEC.loader.exec_module(_shared)

normalise = cast(Callable[[str], str], _shared.normalise)
quote_in = cast(Callable[[str, str], bool], _shared.quote_in)
forms = cast(Callable[[str], list[str]], _shared.plain_forms)
found_in = cast(Callable[[str, list[str]], bool], _shared.quote_in_forms)
