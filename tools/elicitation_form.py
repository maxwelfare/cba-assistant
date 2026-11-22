"""Write the Google Apps Script that makes a case's expert-survey form (notes/case_pipeline.md 6.3).

Run from the repository root:

    .venv/bin/python tools/elicitation_form.py <questions.toml>

It writes `form.gs` beside the question file and prints its path as the last line. It never calls Google or the
network. The user pastes `form.gs` into a new project at script.google.com and runs `createExpertForm`, which asks
only for permission to manage the user's forms, creates the form in the user's Google account and logs the form's
link to send and its edit link. Answers stay in the form; its Responses tab links them to a sheet when one is
wanted. Apps Script stops a run at 6 minutes, and a long form takes longer, so the script stops itself at 4.5 minutes and logs how
far it got; run again, it finds its form by the id kept in the project's script properties and adds the rest.
Every method the script calls is in Google's reference for the Forms service and the Properties service, under
the keys google_apps_script_forms and google_apps_script_properties of research/refs.toml, with the
quotas page that states the limit.

The question file (TOML; every key required, nothing defaults, no other key allowed):

    case = "cases/<case>"     # the case folder, from the repository root
    title = "..."             # the form's title
    introduction = "..."      # the text the expert reads first; the form's description
    fixture = false           # true: a build test's wording, marked so in the title and description
    strings_file = "..."      # every fixed sentence of the form; a path relative to this file (see below)

    [<input key>]             # one table per question, in the order asked; the name is an input of
                              # <case>/inputs.toml, whose `label` titles the question's page
    wording = "..."           # the question
    channel = "..."           # one plain sentence: what the number does in the analysis
    unit = "share"            # must equal the input's `unit` in inputs.toml
    unit_text = "share"       # the unit as the expert sees it, and the unit of the limits and the answers
    lower_limit = 0           # the quantity's logical range; lower below upper
    upper_limit = 1
    best_estimate = "median"  # "median" or "mean": what the best estimate is asked to be
    anchors = [               # from the literature; each source a table of <case>/sources.toml
      { text = "...", source = "<source key>" },
    ]

Each question gets a page holding the wording, the channel and the anchors, and the four answers of the IDEA
protocol (Hemming et al. 2018): lowest plausible value, highest plausible value and best estimate, each
validated as a number within the limits; confidence that the truth lies between the lowest and highest, 50 to 100
per cent; and the reasons. Before the pages the form asks the expert's code and two consents (to be named; to have
their answers published without their name). Every item is optional, so an expert leaves blank whatever lies
outside their expertise (the owner, 2026-11-10: "allow anyone to leave things blank if it's not their expertise");
a blank consent is read as No. Each answer item's
title ends in a bracketed tag, `[<input key>.lowest]`, `.highest]`, `.best]`, `.confidence]`, `.reasons]`, or
`[expert_code]`, `[consent_named]`, `[consent_publish_anonymous]`, from which the import recovers what it is.

The strings file holds every sentence the form fixes, so a form in another language needs only a translated copy
of `tools/elicitation_strings_en.toml`; every key of that file is required and no other is allowed. A string may
use only the placeholders it has there, which are among `{lo}`, `{hi}`, `{unit}`, `{key}` and `{best}`. The
bracketed tags stay in the code, since the import reads them.

A `unit_text` containing 만, 억 or 조 must also contain that word's factor as a whole number in digits (10,000;
100,000,000; 1,000,000,000,000; commas optional), so that an expert who thinks in that word cannot answer a value
10^4 to 10^12 too small and pass the limits. The limits are in the unit the expert answers in; the form converts
nothing.

A file that breaks any rule above is refused: exit 1, a message naming the question and the key, nothing written.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import tomllib
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
TOP = {"case": str, "title": str, "introduction": str, "fixture": bool, "strings_file": str}
QUESTION = {
    "wording": str,
    "channel": str,
    "unit": str,
    "unit_text": str,
    "lower_limit": float,
    "upper_limit": float,
    "best_estimate": str,
    "anchors": list,
}
BEST = ("median", "mean")
# Each key of the strings file, with the placeholders its string may use.
STRINGS: dict[str, tuple[str, ...]] = {
    "expert_code_title": (),
    "expert_code_help": (),
    "consent_named_title": (),
    "consent_named_help": (),
    "consent_publish_anonymous_title": (),
    "consent_publish_anonymous_help": (),
    "yes": (),
    "no": (),
    "channel": (),
    "literature": (),
    "source": ("key",),
    "range": ("unit", "lo", "hi"),
    "invalid": ("unit", "lo", "hi"),
    "lowest_title": (),
    "lowest_help": (),
    "highest_title": (),
    "highest_help": (),
    "best_title": (),
    "best_help": ("best",),
    "best_median": (),
    "best_mean": (),
    "confidence_title": (),
    "confidence_help": ("lo", "hi"),
    "confidence_invalid": ("lo", "hi"),
    "reasons_title": (),
    "reasons_help": (),
    "fixture_title": (),
    "fixture_note": (),
}
PLACEHOLDER = re.compile(r"\{([^{}]*)\}|[{}]")  # the second branch catches a stray brace, which no string may hold
MAGNITUDE = {"만": 10**4, "억": 10**8, "조": 10**12}  # as the digits a `unit_text` holding the word must show

Table = dict[str, Any]


class Refusal(Exception):
    pass


def load(path: Path, where: str) -> Table:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise Refusal(f"{where}: cannot read {path}: {e}") from e


def checked(table: Table, spec: dict[str, type], where: str) -> None:
    """Refuse a missing, extra or wrongly typed key. A number is an int or float, never a bool."""
    for key in table.keys() - spec.keys():
        raise Refusal(f"{where}: key '{key}' is not one the format allows")
    for key, kind in spec.items():
        if key not in table:
            raise Refusal(f"{where}: key '{key}' is missing")
        value = table[key]
        if kind is float:
            ok = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        else:
            ok = isinstance(value, kind)
        if not ok:
            raise Refusal(f"{where}: key '{key}' must be {kind.__name__}, not {value!r}")
        if isinstance(value, str) and not value.strip():
            raise Refusal(f"{where}: key '{key}' is empty")


def num(x: float) -> str:
    return repr(x)


def load_strings(path: Path) -> dict[str, str]:
    strings = load(path, "key 'strings_file'")
    checked(strings, dict.fromkeys(STRINGS, str), f"strings file {path}")
    for name, allowed in STRINGS.items():
        for m in PLACEHOLDER.finditer(strings[name]):
            if m.group(1) not in allowed:
                raise Refusal(f"strings file {path}: key '{name}' uses {m.group(0)!r}, in {strings[name]!r}; it may use "
                              f"only {', '.join('{' + a + '}' for a in allowed) or 'no placeholder'}")
    return strings


def fill(template: str, **values: str) -> str:
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def js_string(text: str) -> str:
    """A single-quoted JavaScript literal, ASCII for the reason given where `spec` is written."""
    return "'" + json.dumps(text)[1:-1].replace("'", "\\'") + "'"


def question_items(key: str, q: Table, label: str, s: dict[str, str]) -> list[Table]:
    """The page break and five answer items of one question."""
    lo, hi, unit = q["lower_limit"], q["upper_limit"], q["unit_text"]
    page = [q["wording"], f"{s['channel']} {q['channel']}"]
    anchors = cast(list[Table], q["anchors"])
    if anchors:
        page.append(s["literature"] + "\n" + "\n".join(
            f"{n}. {a['text']} {fill(s['source'], key=a['source'])}" for n, a in enumerate(anchors, 1)))
    rng = fill(s["range"], unit=unit, lo=num(lo), hi=num(hi))
    invalid = fill(s["invalid"], unit=unit, lo=num(lo), hi=num(hi))
    best = fill(s["best_help"], best=s[f"best_{q['best_estimate']}"])
    sure = {"lo": num(50), "hi": num(100)}
    return [
        {"kind": "page", "title": label, "help": "\n\n".join(page)},
        {"kind": "number", "title": f"{s['lowest_title']} [{key}.lowest]",
         "help": f"{rng} {s['lowest_help']}", "between": [lo, hi], "invalid": invalid},
        {"kind": "number", "title": f"{s['highest_title']} [{key}.highest]",
         "help": f"{rng} {s['highest_help']}", "between": [lo, hi], "invalid": invalid},
        {"kind": "number", "title": f"{s['best_title']} [{key}.best]",
         "help": f"{rng} {best}", "between": [lo, hi], "invalid": invalid},
        {"kind": "number", "title": f"{s['confidence_title']} [{key}.confidence]",
         "help": fill(s["confidence_help"], **sure), "between": [50, 100],
         "invalid": fill(s["confidence_invalid"], **sure)},
        {"kind": "paragraph", "title": f"{s['reasons_title']} [{key}.reasons]", "help": s["reasons_help"]},
    ]


def form_spec(path: Path) -> tuple[Table, dict[str, str]]:
    """The form's items and the strings file, whose choice labels the script writes as JavaScript."""
    doc = load(path, str(path))
    questions = {k: cast(Table, v) for k, v in doc.items() if isinstance(v, dict)}
    checked({k: v for k, v in doc.items() if k not in questions}, TOP, f"{path} (top level)")
    if not questions:
        raise Refusal(f"{path}: no question tables")
    case = ROOT / doc["case"]
    inputs = load(case / "inputs.toml", "key 'case'")
    sources = load(case / "sources.toml", "key 'case'")
    s = load_strings(path.parent / doc["strings_file"])
    items: list[Table] = [
        {"kind": "text", "title": f"{s['expert_code_title']} [expert_code]", "help": s["expert_code_help"]},
        {"kind": "choice", "title": f"{s['consent_named_title']} [consent_named]", "help": s["consent_named_help"]},
        {"kind": "choice", "title": f"{s['consent_publish_anonymous_title']} [consent_publish_anonymous]",
         "help": s["consent_publish_anonymous_help"]},
    ]
    for key, q in questions.items():
        where = f"question [{key}]"
        checked(q, QUESTION, where)
        if key not in inputs or not isinstance(inputs[key], dict):
            raise Refusal(f"{where}: '{key}' is not an input of {doc['case']}/inputs.toml")
        inp = cast(Table, inputs[key])
        if not isinstance(inp.get("label"), str) or not isinstance(inp.get("unit"), str):
            raise Refusal(f"{where}: the input in {doc['case']}/inputs.toml lacks a 'label' or 'unit'")
        if q["unit"] != inp["unit"]:
            raise Refusal(f"{where}: key 'unit' is {q['unit']!r}, but the input's unit is {inp['unit']!r}")
        runs = re.findall(r"\d+", q["unit_text"].replace(",", ""))
        for word, factor in MAGNITUDE.items():
            if word in q["unit_text"] and str(factor) not in runs:
                raise Refusal(f"{where}: key 'unit_text' ({q['unit_text']!r}) contains {word} but not its factor "
                              f"{factor:,} in digits")
        if not q["lower_limit"] < q["upper_limit"]:
            raise Refusal(f"{where}: key 'lower_limit' ({q['lower_limit']}) is not below 'upper_limit' "
                          f"({q['upper_limit']})")
        if q["best_estimate"] not in BEST:
            raise Refusal(f"{where}: key 'best_estimate' must be 'median' or 'mean', not {q['best_estimate']!r}")
        for n, anchor in enumerate(cast(list[Any], q["anchors"]), 1):
            if not isinstance(anchor, dict):
                raise Refusal(f"{where}: key 'anchors', item {n}, is not a table with 'text' and 'source'")
            anchor = cast(Table, anchor)
            checked(anchor, {"text": str, "source": str}, f"{where}, key 'anchors', item {n}")
            if not isinstance(sources.get(anchor["source"]), dict):
                raise Refusal(f"{where}, key 'anchors', item {n}: key 'source' {anchor['source']!r} is not a "
                              f"table of {doc['case']}/sources.toml")
        items += question_items(key, q, inp["label"], s)
    titles = [i["title"] for i in items if i["kind"] != "page"]
    for t in titles:
        if titles.count(t) > 1:
            raise Refusal(f"{path}: two items are titled {t!r}")
    fixture = doc["fixture"]
    return {
        "title": (s["fixture_title"] + " " + doc["title"]) if fixture else doc["title"],
        "description": (doc["introduction"] + "\n\n" + s["fixture_note"]) if fixture else doc["introduction"],
        "items": items,
    }, s


SCRIPT = """\
// Made by tools/elicitation_form.py from {source}; do not edit by hand, edit the question file and run it again.
// Make a new project at script.google.com, paste this whole file in place of its code, save, and run
// createExpertForm. It asks for permission to manage your forms, creates the form in your account and writes the
// form's links in the execution log. Every item is optional; answers stay in the form. A run stops before Apps
// Script's limit of 6 minutes and says so; run createExpertForm again and it adds the rest to the same form.

function createExpertForm() {{
  var spec = {spec};
  var started = Date.now();
  var store = PropertiesService.getScriptProperties();
  var key = 'form {fingerprint}';
  var form;
  if (store.getProperty(key)) {{
    form = FormApp.openById(store.getProperty(key));
  }} else {{
    form = FormApp.create(spec.title);
    form.setDescription(spec.description);
    store.setProperty(key, form.getId());
  }}
  Logger.log('Link to send to experts: ' + form.getPublishedUrl());
  Logger.log('Link to edit the form: ' + form.getEditUrl());
  var made = form.getItems();
  if (made.length > spec.items.length ||
      (made.length > 0 && made[made.length - 1].getTitle() !== spec.items[made.length - 1].title)) {{
    throw new Error('The form holds items this script did not make; nothing was added.');
  }}
  for (var n = made.length; n < spec.items.length; n++) {{
    if (Date.now() - started > 270000) {{
      Logger.log('Stopped before the time limit with ' + n + ' of ' + spec.items.length +
          ' items in the form. Run createExpertForm again to add the rest.');
      return;
    }}
    var it = spec.items[n];
    if (it.kind === 'page') {{
      form.addPageBreakItem().setTitle(it.title).setHelpText(it.help);
    }} else if (it.kind === 'choice') {{
      form.addMultipleChoiceItem().setTitle(it.title).setHelpText(it.help)
          .setChoiceValues([{yes}, {no}]);
    }} else if (it.kind === 'paragraph') {{
      form.addParagraphTextItem().setTitle(it.title).setHelpText(it.help);
    }} else {{
      var item = form.addTextItem().setTitle(it.title).setHelpText(it.help);
      if (it.kind === 'number') {{
        item.setValidation(FormApp.createTextValidation()
            .requireNumberBetween(it.between[0], it.between[1])
            .setHelpText(it.invalid)
            .build());
      }}
    }}
  }}
  Logger.log('Done: all ' + spec.items.length + ' items are in the form.');
}}
"""


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: .venv/bin/python tools/elicitation_form.py <questions.toml>", file=sys.stderr)
        return 1
    path = Path(argv[1])
    try:
        spec, strings = form_spec(path)
    except Refusal as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    out = path.parent / "form.gs"
    # ensure_ascii keeps U+2028 and U+2029, legal in JSON but not in older JavaScript strings, escaped.
    spec_json = json.dumps(spec, ensure_ascii=True, indent=2)
    # The script keeps the form's id under a key from the spec, so a changed question file makes a new form.
    fingerprint = hashlib.sha256(spec_json.encode()).hexdigest()[:16]
    text = SCRIPT.format(source=path.name, spec=spec_json.replace("\n", "\n  "), fingerprint=fingerprint,
                         yes=js_string(strings["yes"]), no=js_string(strings["no"]))
    out.write_text(text, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
