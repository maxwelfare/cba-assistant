"""The case loader: reads a case folder (cases/README.md) and returns the whole case, every input
resolved to what `distributions.quantile` needs, or refuses with every problem it found at once.

The owner's rule 2 and the format's central rule: every number visible, labelled and cited, and a
missing value or source refused where it enters, never defaulted. Each problem names where it is
(`<file>: <key path>`) and the field. The rules include one quote per source, named mixture components,
other jurisdictions' pinned editions, notes in data/, expert_judgement and the discount base year's limit;
every quote checked against its source's stored text in
sources/<key>/text.txt, and a guidance value with a low and a high drawn as the triangular (low, value, high);
and money declared by `currency` and `price_year`, exchange
rates by `from_currency`, `to_currency` and `rate_year`, no currency in a unit, each pinned edition's
`[price_index]`, and each money input's conversion to the case's currency and price base year resolved into
`Case.conversions`. `flat_rate(case, label)` reads the one rate of a flat schedule, for a case's run script.
"""

from __future__ import annotations

import csv
import datetime
import json
import math
import re
import shlex
import subprocess
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast, overload

import numpy as np
import scipy.stats
from scipy.stats import rv_continuous, rv_discrete

from cost_benefit_engine import distributions
from cost_benefit_engine.quotes import forms, found_in

GUIDANCE_FOLDER = "jurisdiction_guidance"
TOOL = Path(__file__).resolve().parents[1]  # the tool's repository: this module stays there under an editable install
CASE_KEYS = frozenset(
    {
        "decision_question", "unit_of_analysis", "options", "base_case", "appraisal_first_year",
        "appraisal_last_year", "discount_base_year", "price_base_year", "currency", "jurisdiction", "guidance_edition",
        "other_guidance_editions",
        "iterations", "random_seed", "sampling_method", "authoritative_model", "real_discount_rates",
        "real_discount_rates_source", "real_discount_rates_quote", "sheet", "streams", "intermediate_results",
    }
)
CASE_TEXT = ("decision_question", "unit_of_analysis", "jurisdiction", "guidance_edition")
CASE_YEARS = ("appraisal_first_year", "appraisal_last_year", "discount_base_year", "price_base_year")
SAMPLING_METHODS = ("latin_hypercube", "monte_carlo", "sheet_random_numbers")
SHEET_RANDOM_NUMBERS = "sheet_random_numbers"
AUTHORITATIVE_MODELS = ("sheet", "python")
SHEET_KEYS = frozenset({"id", "title", "tabs"})
STREAM_KEYS = frozenset({"kind", "label", "borne_by", "received_by", "status"})
STREAM_STATUSES = ("counted", "flagged", "zero")  # a missing status means counted
STREAM_PARTY = {"cost": "borne_by", "benefit": "received_by"}
RESULT_KEYS = frozenset({"label", "unit", "sheet"})
SOURCE_KEYS = frozenset({"citation", "licence", "url", "doi", "ref"})
SOURCE_EVIDENCE_TYPES = frozenset({"single_source", "several_sources", "meta_analysis", "reference_class"})
EVIDENCE_TYPE_KEYS: dict[str, frozenset[str]] = {
    **{t: frozenset({"source", "sources", "quote", "pinpoint"}) for t in SOURCE_EVIDENCE_TYPES},
    "analyst_judgement": frozenset({"judged_by", "rationale"}),
    "expert_judgement": frozenset({"judged_by", "role", "stake", "rationale", "method", "date", "judgement_record"}),
    "expert_elicitation": frozenset({"experts", "elicitation_record"}),
    "ai_expert_panel": frozenset({"panel_run_id"}),
    "external_model_output": frozenset({"file", "source", "sources"}),
    "official_guidance": frozenset({"guidance"}),
}
EXPERT_JUDGEMENT_TEXT = ("judged_by", "role", "stake", "rationale")
EXPERT_JUDGEMENT_METHODS = ("interview", "survey", "correspondence")
NOTE_SUFFIXES = (".md", ".txt")
ALL_EVIDENCE_TYPE_KEYS = frozenset(k for keys in EVIDENCE_TYPE_KEYS.values() for k in keys)
MONEY_KEYS = ("currency", "price_year")
RATE_KEYS = ("from_currency", "to_currency", "rate_year")
INPUT_CORE = frozenset(
    {"label", "unit", "evidence_type", "distribution", "sheet", "indexed_by", "derivation", "note", *MONEY_KEYS, *RATE_KEYS}
)
GUIDANCE_INPUT_KEYS = frozenset({"label", "unit", "evidence_type", "guidance", "sheet", "note", "derivation"})
COLUMN_TEXT_KEYS = frozenset({"source", "quote", "pinpoint"})
RANK_CORRELATION_KEYS = frozenset({"inputs", "coefficient", "evidence_type"})
UNCORRELATABLE = frozenset({"mixture", "categorical"})
ONWARDS = "onwards"
CURRENCY = re.compile(r"[A-Z]{3}")
YEAR_KEY = re.compile(r"[0-9]{4}")
FINANCIAL_YEAR_KEY = re.compile(r"([0-9]{4})-([0-9]{2})")
# Settled choice 4.1 of the money brief: the codes, signs and words by which a unit names a currency.
LISTED_CURRENCIES = ("AUD", "CAD", "CHF", "CNY", "EUR", "GBP", "HKD", "JPY", "NZD", "SGD", "USD")
# The ISO 4217 active list, Table A.1 (SIX, list-one.xml, edition 2026-09-17), copied from the check of the multilingual
# brief 2, which records that reading. Matched in upper case only: the list holds ALL, CUP, TOP, PEN, TRY and GEL.
ISO_4217_CODES = (
    "AED AFN ALL AMD AOA ARS AUD AWG AZN BAM BBD BDT BHD BIF BMD BND BOB BOV BRL BSD BTN BWP BYN BZD CAD CDF CHE CHF "
    "CHW CLF CLP CNY COP COU CRC CUP CVE CZK DJF DKK DOP DZD EGP ERN ETB EUR FJD FKP GBP GEL GHS GIP GMD GNF GTQ GYD "
    "HKD HNL HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD "
    "MAD MDL MGA MKD MMK MNT MOP MRU MUR MVR MWK MXN MXV MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN PGK PHP PKR PLN "
    "PYG QAR RON RSD RUB RWF SAR SBD SCR SDG SEK SGD SHP SLE SOS SRD SSP STN SVC SYP SZL THB TJS TMT TND TOP TRY TTD "
    "TWD TZS UAH UGX USD USN UYI UYU UYW UZS VED VES VND VUV WST XAD XAF XAG XAU XBA XBB XBC XBD XCD XCG XDR XOF XPD "
    "XPF XPT XSU XTS XUA XXX YER ZAR ZMW ZWG"
).split()
# The Unicode Currency Symbols block, which holds the won and euro signs, and the signs outside it.
CURRENCY_SIGNS = re.compile("[$¢£¥₠-⃏]")
CURRENCY_WORDS = (
    "dollar", "dollars", "euro", "euros", "sterling", "won", "yen", "yuan", "rupee", "rupees", "peso", "pesos", "franc",
    "francs", "krona", "kronor", "baht",
)
# Hangul and Han currency words. These syllables sit inside ordinary words (병원 hospital, 单元 a unit), so here a letter
# of any script bounds the word and a digit does not; magnitude numerals may be written directly before it (억원, 万円).
CURRENCY_WORDS_HANGUL_HAN = re.compile(r"(?<![^\W\d_])[십백천만억조十百千万萬億亿兆]*(?:원|엔|위안|円|元)(?![^\W\d_])")
PRICE_INDEX = "price_index"
PRICE_INDEX_TEXT = (
    "series", "publisher", "document", "url", "date_read", "quote", "licence", "guidance_document", "guidance_url",
    "guidance_quote",
)
SHEET_CELL = re.compile(r"^(.+)!([A-Z]+)$")
MIDDLE = np.array([0.5])


def _all_parameters() -> frozenset[str]:
    """Every parameter name of every kind: the template's, metalog, empirical, mixture, categorical,
    and each scipy.stats distribution's shapes with loc and scale."""
    names: set[str] = {"loc", "scale"}
    for keys in distributions.TEMPLATE.values():
        names |= keys
    for required, optional in distributions.OTHER.values():
        names |= required | optional
    for attr in dir(scipy.stats):
        obj: object = getattr(scipy.stats, attr)
        if isinstance(obj, (rv_continuous, rv_discrete)):
            names |= {s.strip() for s in (obj.shapes or "").split(",") if s.strip()}
    return frozenset(names)


ALL_PARAMETERS = _all_parameters()
# Keys reported as unknown on an input whose distribution or evidence type is missing or invalid (settled choice 23).
UNIVERSAL_INPUT_KEYS = INPUT_CORE | ALL_EVIDENCE_TYPE_KEYS | ALL_PARAMETERS | {"column", "data_file"}

Row = tuple[int, int | None, float]
# An input's money: its (currency, price_year), "none" when it carries neither key, "refused" when they are refused.
Money = tuple[str, int] | str
_Check = Callable[[str, Mapping[str, object]], None]
# A quote's place (where, field) and what is checked there: (the quote's name in the message, source key, quote).
_QuoteCheck = tuple[str, str, list[tuple[str, str, str]]]


# ---------------------------------------------------------------- the results


@dataclass(frozen=True)
class Problem:
    where: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.where} [{self.field}]: {self.message}"


class CaseError(Exception):
    """A case refused: `problems` holds every problem found, each once per (where, field)."""

    def __init__(self, problems: Sequence[Problem]) -> None:
        self.problems: tuple[Problem, ...] = tuple(problems)
        super().__init__("\n".join(str(p) for p in self.problems))


@dataclass(frozen=True)
class DiscountSchedule:
    """One discount rate as a schedule of (first year, last year or None for onwards, rate), years
    counted after `discount_base_year`, with the document, URL and quote it comes from."""

    label: str
    rows: tuple[Row, ...]
    document: str
    url: str | None
    quote: str


@dataclass(frozen=True)
class PriceStep:
    """The price step of a conversion: the `[price_index]` of the pinned edition `<jurisdiction>/<edition>.toml`
    (the jurisdiction's folder name and the edition's file stem), its values at the input's price year and at the
    case's price base year."""

    jurisdiction: str
    edition: str
    series: str
    from_year: int
    to_year: int
    from_value: float
    to_value: float


@dataclass(frozen=True)
class Conversion:
    """How one money input's value is brought to the case's money: multiplied by `price_factor` (to_value over
    from_value of `price_step`, 1.0 without one) in its own currency, then by the draw of `rate_input`, when it
    has one. `currency` and `price_year` are the input's own money (an official_guidance input's, its entry's)."""

    currency: str
    price_year: int
    price_factor: float
    price_step: PriceStep | None
    rate_input: str | None


@dataclass(frozen=True)
class Case:
    folder: Path
    frame: Mapping[str, object]
    real_discount_rates: tuple[DiscountSchedule, ...]
    streams: Mapping[str, Mapping[str, object]]
    intermediate_results: Mapping[str, Mapping[str, object]]
    inputs: Mapping[str, Mapping[str, object]]
    sources: Mapping[str, Mapping[str, object]]
    tables: Mapping[str, tuple[Mapping[str, str], ...]]
    rank_correlations: tuple[tuple[str, str, float], ...]
    sheet_columns: Mapping[str, tuple[int, int]]
    editions: Mapping[str, str]
    guidance_root: Path
    conversions: Mapping[str, Conversion]
    row_parameters: Mapping[str, tuple[str, ...]]  # an indexed input's parameter keys read from columns, in order written; none, no entry


@overload
def load(folder: Path | str, guidance_root: Path | str | None = None, *, case_toml_optional: Literal[False] = False) -> Case: ...
@overload
def load(folder: Path | str, guidance_root: Path | str | None = None, *, case_toml_optional: bool) -> Case | None: ...
def load(folder: Path | str, guidance_root: Path | str | None = None, *, case_toml_optional: bool = False) -> Case | None:
    """Read a case folder. `guidance_root` defaults to the nearest folder named jurisdiction_guidance
    found walking up from the case folder. Raises CaseError listing every problem found.
    With `case_toml_optional`, a missing case.toml is no error (stage 2, before stage 3 writes it): every
    check on inputs.toml and sources.toml still runs, those needing the frame are skipped, and the return
    is None, since there is no whole case to return."""
    root = Path(guidance_root).resolve() if guidance_root is not None else None
    return _Loader(Path(folder).resolve(), root).run(case_toml_optional)


def _nearest_guidance(folder: Path) -> Path | None:
    return next((p / GUIDANCE_FOLDER for p in (folder, *folder.parents) if (p / GUIDANCE_FOLDER).is_dir()), None)


def guidance_for(folder: Path) -> Path:
    """The guidance root a run or report passes to `load`: the nearest walking up from the resolved case folder, else
    the tool's, where a case in a workspace finds it. Where neither exists the loader refuses as for any missing root."""
    return _nearest_guidance(folder) or TOOL / GUIDANCE_FOLDER


def commit_of(folder: Path) -> str:
    """The commit of the git repository holding `folder`, for a run's record. Raises where there is none."""
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


def flat_rate(case: Case, label: str) -> float:
    """The one rate of the discount schedule labelled `label` in `case.real_discount_rates`, for a case's run
    script. Raises ValueError naming the label when no schedule has it, or when its rows hold more than one rate."""
    schedule = next((s for s in case.real_discount_rates if s.label == label), None)
    if schedule is None:
        raise ValueError(f"no discount schedule is labelled {label!r}")
    rates = {row[2] for row in schedule.rows}
    if len(rates) != 1:
        raise ValueError(f"discount schedule {label!r} is not flat: its rows hold the rates {sorted(rates)}")
    return float(rates.pop())


# ---------------------------------------------------------------- value helpers


def _table(x: object) -> dict[str, object] | None:
    return cast(dict[str, object], x) if isinstance(x, dict) else None


def _text(x: object) -> str | None:
    """A string non-empty after stripping whitespace."""
    return x if isinstance(x, str) and x.strip() else None


def _int(x: object) -> int | None:
    return x if isinstance(x, int) and not isinstance(x, bool) else None


def _real(x: object) -> float | None:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    value = float(x)
    return value if math.isfinite(value) else None


def _currency(x: object) -> str | None:
    """Settled choice 1.2 of the money brief: three upper-case ASCII letters."""
    return x if isinstance(x, str) and CURRENCY.fullmatch(x) else None


def _year(x: object) -> int | None:
    """A TOML integer from 1000 to 9999; a boolean is not one."""
    value = _int(x)
    return value if value is not None and 1000 <= value <= 9999 else None


def _names(x: object) -> list[str] | None:
    """A non-empty list of distinct non-empty strings."""
    if not isinstance(x, list):
        return None
    items = cast(list[object], x)
    texts = [_text(i) for i in items]
    out = [t for t in texts if t is not None]
    if not out or len(out) != len(items) or len(set(out)) != len(out):
        return None
    return out


def _column(x: object) -> str | None:
    """The column a `{ column = "<name>" }` value names, None if the table is not of that form."""
    t = _table(x)
    if t is None or set(t) != {"column"}:
        return None
    return _text(t["column"])


def _pct(rate: float) -> str:
    return format(rate * 100, "g") + "%"


def _missing_or(entry: Mapping[str, object], key: str, wanted: str) -> str:
    return "missing" if key not in entry else f"must be {wanted}, got {entry[key]!r}"


def _parameters(distribution: object) -> frozenset[str] | None:
    """Every parameter a kind requires; for scipy.<name>, loc and scale (loc alone, discrete) are
    required too (settled choice 10). None for an unknown kind."""
    if not isinstance(distribution, str):
        return None
    try:
        required, optional = distributions.fields(distribution)
    except ValueError:
        return None
    return required | optional if distribution.startswith(distributions.SCIPY) else required


def _optional(distribution: str) -> frozenset[str]:
    return frozenset() if distribution.startswith(distributions.SCIPY) else distributions.fields(distribution)[1]


def _schedule(item: object, rows_only: bool) -> tuple[list[Row], str] | str:
    """A constant rate or a list of [first, last or "onwards", rate] rows, with its label; or the
    reason it is refused."""
    if not rows_only and not isinstance(item, list):
        rate = _real(item)
        if rate is None:
            return f"{item!r} is neither a rate nor a list of [first, last, rate] rows"
        if not -1.0 < rate < 1.0:
            return f"rate {item!r} is not inside (-1, 1); probably written in percent"
        return [(1, None, rate)], _pct(rate)
    if not isinstance(item, list) or not item:
        return f"{item!r} is not a non-empty list of [first, last, rate] rows"
    rows: list[Row] = []
    for raw in cast(list[object], item):
        if not isinstance(raw, list) or len(cast(list[object], raw)) != 3:
            return f"row {raw!r} is not [first, last, rate]"
        first_raw, last_raw, rate_raw = cast(list[object], raw)
        first, rate = _int(first_raw), _real(rate_raw)
        last = None if last_raw == ONWARDS else _int(last_raw)
        if first is None or (last is None and last_raw != ONWARDS) or rate is None:
            return f"row {raw!r} is not [first year, last year or \"onwards\", rate]"
        if not -1.0 < rate < 1.0:
            return f"rate {rate_raw!r} in row {raw!r} is not inside (-1, 1); probably written in percent"
        rows.append((first, last, rate))
    label = "schedule " + ", ".join(f"{a}-{ONWARDS if b is None else b}: {_pct(r)}" for a, b, r in rows)
    return rows, label


def _coverage(rows: Sequence[Row], horizon: int | None) -> str | None:
    """Why the rows fail to cover years 1 to the horizon once each, or None."""
    expected = 1
    for i, (first, last, _) in enumerate(rows):
        if first != expected:
            return f"row {i + 1} starts at year {first}, not {expected}: a gap or an overlap"
        if last is None:
            return None if i == len(rows) - 1 else f"row {i + 1} runs onwards but is not the last row"
        if last < first:
            return f"row {i + 1} ends (year {last}) before it starts (year {first})"
        expected = last + 1
    if horizon is not None and expected - 1 < horizon:
        return f"covers years 1 to {expected - 1}, short of the case's {horizon} years after discount_base_year"
    return None


def guidance_schedules(entry: Mapping[str, object]) -> list[tuple[str, list[Row]]] | str:
    """Every rate or schedule of an edition's `[discount_rate]` (`central` with `sensitivity`, `rates` or `schedule`), each
    with its label, read as the loader reads them, for a reader with no case such as the total tool; or why it is
    refused."""
    forms = [k for k in ("central", "rates", "schedule") if k in entry]
    if len(forms) != 1:
        return f"give one of central, rates or schedule, not {forms}"
    items: list[tuple[object, bool, str]] = []
    if forms[0] == "central":
        sensitivity = entry.get("sensitivity")
        if not isinstance(sensitivity, list) or not sensitivity:
            return _missing_or(entry, "sensitivity", "a non-empty list of rates")
        items = [(entry["central"], False, " (central)")] + [(x, False, " (sensitivity)") for x in cast(list[object], sensitivity)]
    elif forms[0] == "rates":
        rates = entry["rates"]
        if not isinstance(rates, list) or not rates:
            return "rates must be a non-empty list of rates"
        items = [(x, False, "") for x in cast(list[object], rates)]
    else:
        items = [(entry["schedule"], True, "")]
    out: list[tuple[str, list[Row]]] = []
    for item, rows_only, suffix in items:
        parsed = _schedule(item, rows_only)
        reason = parsed if isinstance(parsed, str) else _coverage(parsed[0], None)
        if reason is not None:
            return reason
        assert not isinstance(parsed, str)
        out.append((parsed[1] + suffix, parsed[0]))
    return out


def price_index_years(pi: Mapping[str, object]) -> tuple[dict[int, float | None] | None, str | None]:
    """A `[price_index]`'s calendar_year: year strings to finite positive numbers, None for a bad value (None for the whole
    table where it is missing), and the problem naming each bad one, or None; read so by the loader and by a reader with
    no case, such as the total tool."""
    table = _table(pi.get("calendar_year"))
    if not table:
        return None, _missing_or(pi, "calendar_year", "a table of year to index value")
    years: dict[int, float | None] = {}
    bad: list[str] = []
    for key, raw in table.items():
        if not YEAR_KEY.fullmatch(key) or int(key) < 1000:
            bad.append(f"{key!r} is not a year")
            continue
        value = _real(raw)
        if value is None or value <= 0.0:
            bad.append(f"{key}: {raw!r} is not a finite number above zero")
        years[int(key)] = value if value is not None and value > 0.0 else None
    return years, "; ".join(bad) or None


def read_empirical(folder: Path, where: str, data_file: object, column: object) -> list[float]:
    """An `empirical` input's pool, its data_file a CSV inside `folder` read by the loader's own reader, for a reader with
    no case such as the total tool; raises CaseError with the loader's words (a file outside the folder, invalid CSV, a
    missing column, a value that is not a finite number)."""
    loader = _Loader(folder.resolve(), None)
    pool = loader.read_empirical(where, data_file, column)
    if pool is None:
        raise CaseError(list(loader.found.values()))
    return pool


def unit_currency_matcher(codes: set[str]) -> Callable[[str], bool]:
    """Settled choice 4.1: whether a unit names a currency, by a code or word not run into other letters (in any letter
    case the listed codes, those given and the words; in upper case the rest of ISO 4217), a sign, or a currency's word
    in Hangul or Han."""
    any_case = "|".join(re.escape(w) for w in sorted(set(LISTED_CURRENCIES) | codes) + list(CURRENCY_WORDS))
    latin = re.compile(r"(?<![A-Za-z])(?:(?i:" + any_case + r")|" + "|".join(ISO_4217_CODES) + r")(?![A-Za-z])")
    return lambda unit: bool(latin.search(unit) or CURRENCY_SIGNS.search(unit) or CURRENCY_WORDS_HANGUL_HAN.search(unit))


def _sheet_column(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - ord("A") + 1
    return n


# ---------------------------------------------------------------- the loader


@dataclass(frozen=True)
class _Index:
    """A pinned edition's `[price_index]` as read: its calendar-year values by year, None for a value refused
    under settled choice 6.1; `years` is None when the calendar_year table itself is refused."""

    jurisdiction: str
    edition: str
    series: str
    years: Mapping[int, float | None] | None


@dataclass
class _Mixture:
    """A mixture as the first pass leaves it: its components as written, whether its own entry's
    parameters read cleanly, and its resolved entry, which the second pass completes."""

    where: str
    raw: object
    dist_ok: bool
    resolved: dict[str, object]


class _Loader:
    def __init__(self, folder: Path, guidance_root: Path | None) -> None:
        self.folder = folder
        self.guidance_root = guidance_root
        self.root: Path | None = None
        self.editions: dict[str, str] = {}
        self.found: dict[tuple[str, str], Problem] = {}
        self.sources: dict[str, object] | None = None
        self.used: dict[str, None] = {}
        self.guidance: dict[str, object] | None = None
        self.guide_label = ""
        self.jurisdiction = ""
        self.horizon: int | None = None
        self.sampling_method: str | None = None
        self.tabs: list[str] | None = None
        self.csv_cache: dict[Path, tuple[list[str], list[list[str]]] | None] = {}
        self.named: set[Path] = set()
        self.tables: dict[str, tuple[Mapping[str, str], ...]] = {}
        self.sheet_columns: dict[str, tuple[int, int]] = {}
        self.input_distribution: dict[str, object] = {}
        self.input_indexed: set[str] = set()
        self.drawn: dict[str, bool] = {}  # a non-mixture input's u = 0.5 check ran and passed
        self.mixtures: dict[str, _Mixture] = {}
        self.named_by: dict[str, list[str]] = {}  # a component to the mixtures naming it
        self.resolved: dict[str, dict[str, object]] = {}
        self.quote_checks: list[_QuoteCheck] = []  # run once every source key has been checked
        self.texts: dict[str, str | None] = {}  # a source's stored text, None when it has none
        self.unreadable: set[str] = set()
        self.other_docs: list[tuple[str, str, dict[str, object] | None]] = []  # other pinned editions, in table order
        self.case_currency: str | None = None
        self.price_base_year: int | None = None
        self.guided: dict[str, tuple[str, Mapping[str, object]]] = {}  # official_guidance input to its entry's place
        self.mixture_tables: dict[str, dict[str, object]] = {}
        self.refused_components: set[tuple[str, str]] = set()
        self.row_parameters: dict[str, tuple[str, ...]] = {}

    def add(self, where: str, field: str, message: str) -> None:
        self.found.setdefault((where, field), Problem(where, field, message))

    def need_text(self, where: str, entry: Mapping[str, object], key: str) -> str | None:
        value = _text(entry.get(key))
        if value is None:
            self.add(where, key, _missing_or(entry, key, "a non-empty string"))
        return value

    def unknown(self, where: str, entry: Mapping[str, object], allowed: frozenset[str], prefix: str = "") -> None:
        for key in entry:
            if key not in allowed:
                self.add(where, prefix + key, f"{key!r} is not a key this entry may hold")

    def toml(self, rel: str, path: Path) -> dict[str, object] | None:
        try:
            with path.open("rb") as f:
                return cast(dict[str, object], tomllib.load(f))
        except FileNotFoundError:
            self.add(rel, "-", "file missing")
        except (tomllib.TOMLDecodeError, UnicodeDecodeError, OSError) as e:
            self.add(rel, "-", f"not valid TOML: {e}")
        return None

    def csv(self, where: str, path: Path) -> tuple[list[str], list[list[str]]] | None:
        if path in self.csv_cache:
            return self.csv_cache[path]
        parsed: tuple[list[str], list[list[str]]] | None = None
        try:
            with path.open(newline="", encoding="utf-8") as f:
                lines = list(csv.reader(f, strict=True))
        except (csv.Error, UnicodeDecodeError, OSError) as e:
            self.add(where, "-", f"not valid CSV: {e}")
        else:
            if not lines or not all(h.strip() for h in lines[0]) or len(set(lines[0])) != len(lines[0]):
                self.add(where, "-", "not valid CSV: the first line must name each column once")
            else:
                bad = [n for n, line in enumerate(lines[1:], 1) if len(line) != len(lines[0])]
                if bad:
                    self.add(where, "-", f"not valid CSV: data row {bad[0]} has not {len(lines[0])} cells")
                else:
                    parsed = (lines[0], lines[1:])
        self.csv_cache[path] = parsed
        return parsed

    def inside(self, where: str, field: str, rel: str) -> Path | None:
        """The file a `file` or `data_file` names, if it exists inside the case folder; it then counts as named."""
        path = (self.folder / rel).resolve()
        if not path.is_relative_to(self.folder) or not path.is_file():
            self.add(where, field, f"{rel!r} is not a file inside the case folder")
            return None
        self.named.add(path)
        return path

    def ref(self, where: str, field: str, key: str) -> bool:
        """A source key: refused when sources.toml (if read) lacks it; counted as used otherwise."""
        if self.sources is None:
            return False
        if key not in self.sources:
            self.add(where, field, f"{key!r} is not a key in sources.toml")
            return False
        self.used.setdefault(key, None)
        return True

    # ------------------------------------------------------------ run

    def run(self, case_toml_optional: bool) -> Case | None:
        absent = case_toml_optional and not (self.folder / "case.toml").exists()
        frame = None if absent else self.toml("case.toml", self.folder / "case.toml")
        inputs_doc = self.toml("inputs.toml", self.folder / "inputs.toml")
        self.sources = self.toml("sources.toml", self.folder / "sources.toml")
        streams: dict[str, Mapping[str, object]] = {}
        results: dict[str, Mapping[str, object]] = {}
        if frame is not None:
            self.open_guidance(frame)
            self.check_frame(frame)
            streams = self.check_named_tables(frame, "streams", self.check_stream, required=True)
            results = self.check_named_tables(frame, "intermediate_results", self.check_result, required=False)
        inputs: dict[str, Mapping[str, object]] = {}
        correlations: list[tuple[str, str, float]] = []
        if inputs_doc is not None:
            inputs = self.check_inputs(inputs_doc)
            if "rank_correlation" in inputs_doc:
                correlations = self.check_rank_correlations(inputs_doc["rank_correlation"], inputs_doc)
        conversions: dict[str, Conversion] = {}
        if inputs_doc is not None:
            conversions = self.check_money(inputs_doc)
        else:
            self.check_price_indices()  # each pinned [price_index] is checked whatever inputs.toml holds
        rates = self.check_discount(frame) if frame is not None else []
        sources = self.check_sources()
        if inputs_doc is not None:
            self.check_data_files()
        self.check_stored_quotes()
        if self.found:
            raise CaseError(list(self.found.values()))
        if absent:
            return None
        assert frame is not None and self.root is not None  # the case's own edition is read from the root
        return Case(
            folder=self.folder,
            frame=frame,
            real_discount_rates=tuple(rates),
            streams=streams,
            intermediate_results=results,
            inputs=inputs,
            sources=sources,
            tables=self.tables,
            rank_correlations=tuple(correlations),
            sheet_columns=self.sheet_columns,
            editions=self.editions,
            guidance_root=self.root,
            conversions=conversions,
            row_parameters={n: k for n, k in self.row_parameters.items() if n in inputs},
        )

    # ------------------------------------------------------------ case.toml

    def open_guidance(self, frame: Mapping[str, object]) -> None:
        root = self.guidance_root
        if root is None:
            root = _nearest_guidance(self.folder)
        self.root = root.resolve() if root is not None and root.is_dir() else None
        no_root = f"no {GUIDANCE_FOLDER} folder found walking up from the case"
        jurisdiction, edition = _text(frame.get("jurisdiction")), _text(frame.get("guidance_edition"))
        if "other_guidance_editions" in frame:
            self.open_other_editions(frame["other_guidance_editions"], jurisdiction, no_root)
        if jurisdiction is None or edition is None:
            return  # reported by check_frame
        root = self.root
        if root is None:
            self.add("case.toml", "guidance_edition", no_root)
            return
        if not (root / jurisdiction).is_dir():
            self.add("case.toml", "jurisdiction", f"no jurisdiction {jurisdiction!r} in {root}")
            return
        path = root / jurisdiction / f"{edition}.toml"
        if not path.is_file():
            self.add("case.toml", "guidance_edition", f"no edition {edition!r} of {jurisdiction!r} in {root}")
            return
        self.guide_label = f"{jurisdiction}/{edition}.toml"
        self.jurisdiction = jurisdiction
        self.editions[jurisdiction] = edition
        self.guidance = self.toml(self.guide_label, path)

    def open_other_editions(self, raw: object, own: str | None, no_root: str) -> None:
        """Settled choice 4: each other jurisdiction's pinned edition names a guidance file that parses."""
        w, key = "case.toml", "other_guidance_editions"
        table = _table(raw)
        if not table:
            self.add(w, key, "must be a non-empty table of jurisdiction to edition")
            return
        if self.root is None:
            self.add(w, key, no_root)
            return
        for jurisdiction, value in table.items():
            field = f"{key}.{jurisdiction}"
            edition = _text(value)
            if edition is None:
                self.add(w, field, f"the edition must be a non-empty string, got {value!r}")
                continue
            not_plain = [x for x in (jurisdiction, edition) if x in ("", ".", "..") or "/" in x or "\\" in x]
            if not_plain:
                self.add(w, field, f"{not_plain[0]!r} is not one plain path component")
            elif jurisdiction == own:
                self.add(w, field, f"{jurisdiction!r} is the case's own jurisdiction, pinned by guidance_edition")
            elif not (self.root / jurisdiction).is_dir():
                self.add(w, field, f"no jurisdiction {jurisdiction!r} in {self.root}")
            elif not (self.root / jurisdiction / f"{edition}.toml").is_file():
                self.add(w, field, f"no edition {edition!r} of {jurisdiction!r} in {self.root}")
            else:
                self.editions[jurisdiction] = edition
                doc = self.toml(f"{jurisdiction}/{edition}.toml", self.root / jurisdiction / f"{edition}.toml")
                self.other_docs.append((jurisdiction, edition, doc))

    def check_frame(self, frame: Mapping[str, object]) -> None:
        w = "case.toml"
        self.unknown(w, frame, CASE_KEYS)
        for key in CASE_TEXT:
            self.need_text(w, frame, key)
        options = _names(frame.get("options"))
        if options is None:
            self.add(w, "options", _missing_or(frame, "options", "a non-empty list of distinct names"))
        base_case = _text(frame.get("base_case"))
        if base_case is None:
            self.add(w, "base_case", _missing_or(frame, "base_case", "a non-empty string naming one of options"))
        elif options is not None and base_case not in options:
            self.add(w, "base_case", f"{base_case!r} is not one of options {options}")
        self.case_currency = _currency(frame.get("currency"))
        if self.case_currency is None:
            self.add(w, "currency", _missing_or(frame, "currency", "three upper-case letters, such as AUD"))
        years: dict[str, int] = {}
        for key in CASE_YEARS:
            value = _int(frame.get(key))
            if value is None:
                self.add(w, key, _missing_or(frame, key, "an integer year"))
            else:
                years[key] = value
        self.price_base_year = years.get("price_base_year")
        first, last = "appraisal_first_year", "appraisal_last_year"
        if first in years and last in years and years[first] > years[last]:
            self.add(w, first, f"{first} {years[first]} is after {last} {years[last]}")
        base = "discount_base_year"
        if first in years and base in years and years[first] < years[base]:
            self.add(
                w,
                first,
                f"{first} {years[first]} is before {base} {years[base]}: the engine has no discount rule yet for "
                f"flows before {base}, so an appraisal cannot start before it",
            )
        if last in years and "discount_base_year" in years:
            self.horizon = years[last] - years["discount_base_year"]
        iterations = _int(frame.get("iterations"))
        if iterations is None or iterations < 1:
            self.add(w, "iterations", _missing_or(frame, "iterations", "a positive integer"))
        random_seed = _int(frame.get("random_seed"))
        if random_seed is None or random_seed < 0:
            self.add(w, "random_seed", _missing_or(frame, "random_seed", "an integer, not negative"))
        sampling_method = frame.get("sampling_method")
        if sampling_method in SAMPLING_METHODS:
            self.sampling_method = cast(str, sampling_method)
        else:
            self.add(w, "sampling_method", _missing_or(frame, "sampling_method", f"one of {SAMPLING_METHODS}"))
        authoritative_model = frame.get("authoritative_model")
        if authoritative_model not in AUTHORITATIVE_MODELS:
            self.add(w, "authoritative_model", _missing_or(frame, "authoritative_model", f"one of {AUTHORITATIVE_MODELS}"))
        self.check_sheet(frame, authoritative_model == "sheet")

    def check_sheet(self, frame: Mapping[str, object], sheet_authoritative: bool) -> None:
        sheet_numbers = self.sampling_method == SHEET_RANDOM_NUMBERS
        if "sheet" not in frame:
            if sheet_authoritative or sheet_numbers:
                self.add(
                    "case.toml",
                    "sheet",
                    "a [sheet] table is required when authoritative_model is sheet or sampling_method is sheet_random_numbers",
                )
            return
        sheet = _table(frame["sheet"])
        if sheet is None:
            self.add("case.toml", "sheet", "must be a table")
            return
        w = "case.toml: sheet"
        self.unknown(w, sheet, SHEET_KEYS)
        if sheet_authoritative or "id" in sheet:
            self.need_text(w, sheet, "id")
        if "title" in sheet:
            self.need_text(w, sheet, "title")
        if sheet_numbers or "tabs" in sheet:
            self.tabs = _names(sheet.get("tabs"))
            if self.tabs is None:
                self.add(w, "tabs", _missing_or(sheet, "tabs", "a non-empty list of distinct tab names, in sheet order"))

    def check_named_tables(
        self, frame: Mapping[str, object], key: str, check: _Check, required: bool
    ) -> dict[str, Mapping[str, object]]:
        out: dict[str, Mapping[str, object]] = {}
        raw = frame.get(key)
        tables = _table(raw)
        if raw is None or (tables is not None and not tables):
            if required:
                self.add("case.toml", key, f"at least one of [{key}.<name>] is required")
            return out
        if tables is None:
            self.add("case.toml", key, f"must be tables [{key}.<name>]")
            return out
        for name, value in tables.items():
            where = f"case.toml: {key}.{name}"
            entry = _table(value)
            if entry is None:
                self.add(where, "-", "must be a table")
                continue
            check(where, entry)
            out[name] = entry
        return out

    def check_stream(self, where: str, entry: Mapping[str, object]) -> None:
        self.unknown(where, entry, STREAM_KEYS)
        self.need_text(where, entry, "label")
        if "status" in entry and entry["status"] not in STREAM_STATUSES:
            self.add(where, "status", f"status {entry['status']!r} is not counted, flagged or zero")
        kind = entry.get("kind")
        if not isinstance(kind, str) or kind not in STREAM_PARTY:
            self.add(where, "kind", _missing_or(entry, "kind", "cost or benefit"))
            return
        party = STREAM_PARTY[kind]
        self.need_text(where, entry, party)
        for other in STREAM_PARTY.values():
            if other != party and other in entry:
                self.add(where, other, f"{other} does not belong to a {kind}")

    def check_result(self, where: str, entry: Mapping[str, object]) -> None:
        self.unknown(where, entry, RESULT_KEYS)
        self.need_text(where, entry, "label")
        self.need_text(where, entry, "unit")
        if "sheet" in entry:
            self.need_text(where, entry, "sheet")

    # ------------------------------------------------------------ discount rates

    def check_discount(self, frame: Mapping[str, object]) -> list[DiscountSchedule]:
        w = "case.toml"
        if "real_discount_rates" in frame:
            return self.case_rates(frame)
        for key in ("real_discount_rates_source", "real_discount_rates_quote"):
            if key in frame:
                self.add(w, key, f"{key} is given without real_discount_rates")
        if self.guidance is None:
            return []  # the guidance's own problem is reported once
        if "discount_rate" not in self.guidance:
            self.add(
                w, "real_discount_rates", f"{self.guide_label} gives no discount rate and case.toml gives no real_discount_rates"
            )
            return []
        entry = _table(self.guidance["discount_rate"])
        gw = f"{self.guide_label}: discount_rate"
        if entry is None:
            self.add(gw, "-", "must be a table")
            return []
        return self.guidance_rates(gw, entry)

    def case_rates(self, frame: Mapping[str, object]) -> list[DiscountSchedule]:
        w = "case.toml"
        document, url = "", None
        key = self.need_text(w, frame, "real_discount_rates_source")
        key_ok = False
        if key is not None and self.ref(w, "real_discount_rates_source", key):
            key_ok = True
            source = _table(cast(dict[str, object], self.sources)[key]) or {}
            document = _text(source.get("citation")) or ""
            url = _text(source.get("url"))
        quote = self.need_text(w, frame, "real_discount_rates_quote") or ""
        if key_ok and quote:
            self.quote_checks.append((w, "real_discount_rates_quote", [("", cast(str, key), quote)]))
        items = frame["real_discount_rates"]
        if not isinstance(items, list) or not items:
            self.add(w, "real_discount_rates", "must be a non-empty list of rates or schedules")
            return []
        out: list[DiscountSchedule] = []
        for item in cast(list[object], items):
            parsed = _schedule(item, rows_only=False)
            reason = parsed if isinstance(parsed, str) else _coverage(parsed[0], self.horizon)
            if reason is not None:
                self.add(w, "real_discount_rates", reason)
                continue
            assert not isinstance(parsed, str)
            out.append(DiscountSchedule(parsed[1], tuple(parsed[0]), document, url, quote))
        return out

    def guidance_rates(self, gw: str, entry: Mapping[str, object]) -> list[DiscountSchedule]:
        self.check_guidance_entry("discount_rate", entry)
        document = _text(entry.get("document")) or ""
        url = _text(entry.get("url"))
        quote = _text(entry.get("quote")) or ""
        forms = [k for k in ("central", "rates", "schedule") if k in entry]
        if not forms:
            self.add(gw, "central", "the guidance's discount rate has no central, rates or schedule")
            return []
        if len(forms) > 1:
            self.add(gw, forms[1], f"give one of central, rates or schedule, not {forms}")
            return []
        form = forms[0]
        if form != "central" and "sensitivity" in entry:
            self.add(gw, "sensitivity", "sensitivity goes with a central rate only")
        # (key holding the rates, the item, label suffix, quote)
        items: list[tuple[str, object, str, str]] = []
        if form == "central":
            items.append(("central", entry["central"], " (central)", quote))
            sensitivity = entry.get("sensitivity")
            if not isinstance(sensitivity, list) or not sensitivity:
                self.add(gw, "sensitivity", _missing_or(entry, "sensitivity", "a non-empty list of rates"))
            else:
                q = _text(entry.get("quote_sensitivity")) or quote
                items += [("sensitivity", x, " (sensitivity)", q) for x in cast(list[object], sensitivity)]
        elif form == "rates":
            rates = entry["rates"]
            if not isinstance(rates, list) or not rates:
                self.add(gw, "rates", "must be a non-empty list of rates")
            else:
                items += [("rates", x, "", quote) for x in cast(list[object], rates)]
        else:
            items.append(("schedule", entry["schedule"], "", quote))
        out: list[DiscountSchedule] = []
        for key, item, suffix, q in items:
            parsed = _schedule(item, rows_only=key == "schedule")
            reason = parsed if isinstance(parsed, str) else _coverage(parsed[0], self.horizon)
            if reason is not None:
                self.add(gw, key, reason)
                continue
            assert not isinstance(parsed, str)
            out.append(DiscountSchedule(parsed[1] + suffix, tuple(parsed[0]), document, url, q))
        return out

    def check_guidance_entry(self, name: str, entry: Mapping[str, object]) -> None:
        """A guidance entry the case uses needs its document, quote and licence (choices 19, 24)."""
        for key in ("document", "quote", "licence"):
            if _text(entry.get(key)) is None:
                self.add(f"{self.guide_label}: {name}", key, _missing_or(entry, key, "a non-empty string"))

    # ------------------------------------------------------------ inputs.toml

    def check_inputs(self, doc: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
        out: dict[str, Mapping[str, object]] = {}
        for name, raw in doc.items():
            if name == "rank_correlation":
                continue
            where = f"inputs.toml: {name}"
            entry = _table(raw)
            if entry is None:
                self.add(where, "-", "an input must be a table")
                continue
            self.input_distribution[name] = entry.get("distribution")
            if "indexed_by" in entry:
                self.input_indexed.add(name)
            resolved = self.check_input(where, name, entry)
            if resolved is not None:
                out[name] = self.resolved[name] = resolved
        self.check_mixtures(doc)
        return out

    def check_mixtures(self, doc: Mapping[str, object]) -> None:
        """The loader revision's settled choice 3: a mixture's components are inputs named by name, checked
        once every input has been, then resolved and drawn inner mixtures first. A mixture is drawn only when
        its components and every component's own draw check passed; otherwise it adds no problem of its own."""
        inputs = {n for n, raw in doc.items() if n != "rank_correlation" and _table(raw) is not None}
        tables: dict[str, dict[str, object]] = {}
        for m, mix in self.mixtures.items():
            table = _table(mix.raw)
            if table is None or len(table) < 2:
                self.add(mix.where, "components", "must be a table of input name to weight, two or more")
            else:
                tables[m] = table
        for m, table in tables.items():
            for n in table:
                if n != m:  # a mixture naming itself is refused below, not counted as a second mixture
                    self.named_by.setdefault(n, []).append(m)
        refused: set[str] = set()
        for m, table in tables.items():
            where = self.mixtures[m].where
            unit = _text(cast(dict[str, object], doc[m]).get("unit"))
            for n, w in table.items():
                weight = _real(w)
                reason = None
                if n not in inputs:
                    reason = f"{n!r} is not an input"
                elif n == m:
                    reason = "a mixture may not name itself"
                elif self.input_distribution.get(n) == "categorical":
                    reason = f"{n!r} is a categorical, which has no quantile"
                elif n in self.input_indexed and self.input_distribution.get(n) != "mixture":
                    reason = f"{n!r} is indexed by a table, and a component has no per-row form"
                elif unit is not None and (u := _text(cast(dict[str, object], doc[n]).get("unit"))) is not None and u != unit:
                    reason = f"{n!r} is in {u!r}, the mixture in {unit!r}: the components are estimates of one quantity"
                elif len(self.named_by[n]) > 1:
                    reason = f"{n!r} is named by the mixtures {self.named_by[n]}; a component belongs to one mixture"
                elif weight is None or weight <= 0.0:
                    reason = f"the weight must be a finite number above zero, got {w!r}"
                if reason is not None:
                    self.add(where, f"components.{n}", reason)
                    self.refused_components.add((m, n))
                    refused.add(m)
        # A ring: a mixture reached again by following the mixtures it names (naming itself is not a ring).
        for m in tables:
            seen: set[str] = set()
            stack = [n for n in tables[m] if n in tables and n != m]
            while stack:
                n = stack.pop()
                if n not in seen:
                    seen.add(n)
                    stack += [k for k in tables[n] if k in tables and k != n]
            if m in seen:
                self.add(self.mixtures[m].where, "components", "the mixtures it names lead back to it: a ring of mixtures")
                refused.add(m)
        self.mixture_tables = tables
        settled: dict[str, bool] = {}

        def settle(m: str) -> bool:
            if m not in settled:
                settled[m] = False  # a mixture reached again while it is settled lies in a ring, refused above
                mix = self.mixtures[m]
                if m in tables and m not in refused and mix.dist_ok:
                    items: list[dict[str, object]] = []
                    ok = True
                    for n, w in tables[m].items():
                        drawn = settle(n) if n in self.mixtures else self.drawn.get(n, False)
                        entry = self.resolved.get(n)
                        ok = ok and drawn and entry is not None
                        if entry is not None:
                            items.append({**entry, "input": n, "weight": w})
                    if ok:
                        mix.resolved["components"] = items
                        settled[m] = self.draw_check(mix.where, mix.resolved, {})
            return settled[m]

        for m in self.mixtures:
            settle(m)

    def check_input(self, where: str, name: str, entry: Mapping[str, object]) -> dict[str, object] | None:
        self.need_text(where, entry, "label")
        self.need_text(where, entry, "unit")
        for key in ("sheet", "derivation", "note"):
            if key in entry:
                self.need_text(where, entry, key)
        if self.sampling_method == SHEET_RANDOM_NUMBERS:
            self.check_sheet_cell(where, name, entry)
        type_raw = entry.get("evidence_type")
        evidence_type = type_raw if isinstance(type_raw, str) and type_raw in EVIDENCE_TYPE_KEYS else None
        if evidence_type is None:
            self.add(where, "evidence_type", _missing_or(entry, "evidence_type", f"one of {sorted(EVIDENCE_TYPE_KEYS)}"))
        if evidence_type == "official_guidance":
            resolved = self.check_guidance_input(where, name, entry)
            if resolved is not None and resolved["distribution"] == "triangular":
                self.drawn[name] = self.draw_check(where, resolved, {})
            else:
                self.drawn[name] = resolved is not None and resolved["mean"] is not None
            return resolved

        dist_raw = entry.get("distribution")
        required = _parameters(dist_raw)
        if required is None and (evidence_type is not None or dist_raw is not None):
            self.add(where, "distribution", _missing_or(entry, "distribution", "a kind cases/README.md lists"))
        if required is None or evidence_type is None:
            allowed = UNIVERSAL_INPUT_KEYS
        else:
            allowed = INPUT_CORE | EVIDENCE_TYPE_KEYS[evidence_type] | required | _optional(cast(str, dist_raw))
        self.unknown(where, entry, allowed)
        dist_ok = required is not None
        for key in sorted(required or ()):
            if key not in entry:
                self.add(where, key, "missing")
                dist_ok = False
        resolved = dict(entry)

        # Values read from a table's columns.
        indexed_by = entry.get("indexed_by")
        columns: dict[str, str] = {}
        parameters = ALL_PARAMETERS if required is None else required | _optional(cast(str, dist_raw))
        column_keys = parameters | COLUMN_TEXT_KEYS
        for key, value in entry.items():
            # A categorical's outcomes and a mixture's components are inline tables of name to weight, not
            # column references.
            # Money and rate keys are one value for the whole input, refused as such by check_money.
            skip = key in MONEY_KEYS or key in RATE_KEYS
            if skip or _table(value) is None or (dist_raw, key) in (("categorical", "outcomes"), ("mixture", "components")):
                continue
            col = _column(value)
            if indexed_by is None:
                self.add(where, key, "a { column = ... } value needs indexed_by")
            elif col is None or key not in column_keys:
                self.add(where, key, "a table value must be { column = \"<name>\" } on a parameter, source, quote or pinpoint")
            else:
                columns[key] = col
                continue
            if key in (required or ()):
                dist_ok = False
        if indexed_by is not None:
            if dist_raw == "mixture":
                self.add(where, "indexed_by", "a mixture may not be indexed by a table: a named component has no per-row form")
                dist_ok = False
            dist_ok = self.check_indexed_by(where, entry, indexed_by, columns, resolved) and dist_ok
            read = tuple(k for k in columns if k not in COLUMN_TEXT_KEYS)
            if read:
                self.row_parameters[name] = read

        if evidence_type is not None:
            self.check_evidence_type(where, entry, evidence_type, columns)
        dist = cast(str, dist_raw)
        if required is not None and dist == "empirical" and "data_file" in entry and "column" in entry:
            pool = self.read_empirical(where, entry["data_file"], entry["column"])
            if pool is None:
                dist_ok = False
            else:
                resolved["pool"] = pool
        if required is not None and dist == "mixture":
            if "components" in entry:
                self.mixtures[name] = _Mixture(where, entry["components"], dist_ok, resolved)
            return resolved  # resolved and drawn in the second pass, check_mixtures
        self.drawn[name] = dist_ok and self.draw_check(where, resolved, columns)
        return resolved

    def check_sheet_cell(self, where: str, name: str, entry: Mapping[str, object]) -> None:
        cell = _text(entry.get("sheet"))
        if cell is None:
            self.add(where, "sheet", "every input needs its sheet column when sampling_method is sheet_random_numbers")
            return
        match = SHEET_CELL.match(cell)
        if match is None:
            self.add(where, "sheet", f"{cell!r} is not <Tab>!<column letters>")
            return
        if self.tabs is None:
            return  # [sheet] tabs is reported itself
        tab = match.group(1)
        if tab not in self.tabs:
            self.add(where, "sheet", f"tab {tab!r} is not in [sheet] tabs")
            return
        self.sheet_columns[name] = (self.tabs.index(tab) + 1, _sheet_column(match.group(2)))

    def check_evidence_type(
        self, where: str, entry: Mapping[str, object], evidence_type: str, columns: Mapping[str, str]
    ) -> None:
        if evidence_type in SOURCE_EVIDENCE_TYPES or evidence_type == "external_model_output":
            n = self.check_source_keys(where, entry, evidence_type, columns)
            if evidence_type in SOURCE_EVIDENCE_TYPES:
                self.check_quotes(where, entry, columns, n)
        if evidence_type in ("analyst_judgement", "expert_judgement"):
            for key in EXPERT_JUDGEMENT_TEXT if evidence_type == "expert_judgement" else ("judged_by", "rationale"):
                self.need_text(where, entry, key)
        if evidence_type == "expert_judgement":
            if entry.get("method") not in EXPERT_JUDGEMENT_METHODS:
                self.add(where, "method", _missing_or(entry, "method", f"one of {EXPERT_JUDGEMENT_METHODS}"))
            date = entry.get("date")
            if not isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
                self.add(where, "date", _missing_or(entry, "date", "a TOML local date, such as date = 2026-10-30"))
            rel = self.need_text(where, entry, "judgement_record")
            if rel is not None:
                self.inside(where, "judgement_record", rel)
        elif evidence_type == "expert_elicitation":
            experts = entry.get("experts")
            if _text(experts) is None and _names(experts) is None:
                self.add(where, "experts", _missing_or(entry, "experts", "a non-empty string or list of distinct names"))
            self.need_text(where, entry, "elicitation_record")
        elif evidence_type == "ai_expert_panel":
            self.need_text(where, entry, "panel_run_id")
        elif evidence_type == "external_model_output":
            rel = self.need_text(where, entry, "file")
            if rel is not None:
                self.inside(where, "file", rel)

    def check_source_keys(
        self, where: str, entry: Mapping[str, object], evidence_type: str, columns: Mapping[str, str]
    ) -> int | None:
        """`source` or `sources` (settled choices 1 and 2): the number of sources named, 1 for `source` (a key
        or a column), or None when either key is refused. Every key named is checked and counted as used."""
        if "source" not in entry and "sources" not in entry:
            self.add(where, "source", "missing")
            return None
        if "source" in entry and "sources" in entry:
            self.add(where, "sources", "give source or sources, not both")
            return None
        if "source" in entry:
            ok = "source" in columns  # a column's cells are checked with the table
            if not ok:
                key = self.need_text(where, entry, "source")
                ok = key is not None and self.ref(where, "source", key)
            if evidence_type == "several_sources":
                self.add(where, "source", "several_sources names two or more sources by sources, not one by source")
                return None
            return 1 if ok else None
        keys = _names(entry["sources"])
        if keys is None:
            self.add(where, "sources", "must be a non-empty list of distinct source keys")
            return None
        ok = all([self.ref(where, "sources", key) for key in keys])
        if evidence_type == "single_source":
            self.add(where, "sources", "single_source names its one source by source, not by sources")
            return None
        if evidence_type == "several_sources" and len(keys) < 2:
            self.add(where, "sources", f"several_sources names two or more sources, got {len(keys)}")
            return None
        return len(keys) if ok else None

    def check_quotes(self, where: str, entry: Mapping[str, object], columns: Mapping[str, str], n: int | None) -> None:
        """One quote per source (settled choice 1): with `source`, a string or a column; with `sources` naming
        n keys, a list of n non-empty strings in the order of the sources; `pinpoint`, optional, likewise.
        When the source keys are refused (n is None), only the quote's presence is checked. A quote that passes
        is checked against its source's stored text (the quotes brief's settled choice 1)."""
        if "quote" not in entry:
            self.add(where, "quote", "missing")
        if n is None:
            return
        with_list = "sources" in entry
        quote_ok = "quote" in entry
        for key in ("quote", "pinpoint"):
            if key not in entry:
                continue
            if not with_list:
                if key not in columns and _text(entry[key]) is None:
                    self.add(where, key, f"with source, the {key} of its 1 source: must be a non-empty string, got {entry[key]!r}")
                    quote_ok = quote_ok and key != "quote"
                continue
            wanted = f"with sources naming {n} keys, a list of {n} non-empty strings, one per source in their order"
            if key in columns:
                self.add(where, key, f"a table column holds one {key} per row, not one per source; {wanted}")
                quote_ok = quote_ok and key != "quote"
                continue
            value = entry[key]
            items = cast(list[object], value) if isinstance(value, list) else None
            if items is None or len(items) != n or any(_text(i) is None for i in items):
                self.add(where, key, f"must be {wanted}, got {value!r}")
                quote_ok = quote_ok and key != "quote"
        if quote_ok:
            self.plan_quotes(where, entry, columns)

    def plan_quotes(self, where: str, entry: Mapping[str, object], columns: Mapping[str, str]) -> None:
        """Settled choice 1.1 of the quotes brief: each quote that passed its form checks, against the stored
        text of its source, when that source's key passed its own checks; a table's rows each on their own."""
        quote = entry["quote"]
        if "sources" in entry:
            keys = cast(list[str], entry["sources"])
            pairs = zip(keys, cast(list[str], quote))
            self.quote_checks.append((where, "quote", [(f"quote {i}", k, q) for i, (k, q) in enumerate(pairs, 1)]))
            return
        source_col, quote_col = columns.get("source"), columns.get("quote")
        if source_col is None and quote_col is None:
            self.quote_checks.append((where, "quote", [("", cast(str, entry["source"]), cast(str, quote))]))
            return
        table = _text(entry.get("indexed_by"))
        rows = self.tables.get(table) if table is not None else None
        if rows is None:
            return  # the table's own problem is reported
        one_quote: list[tuple[str, str, str]] = []
        for row in rows:
            row_id = next(iter(row.values()))
            key = row.get(source_col) if source_col is not None else cast(str, entry["source"])
            if key is None or not key.strip() or self.sources is None or key not in self.sources:
                continue  # a missing column or a refused cell is reported with the table
            if quote_col is None:
                one_quote.append((f"row {row_id}", key, cast(str, quote)))
                continue
            cell = row.get(quote_col)
            if cell is not None and cell.strip():
                self.quote_checks.append((f"data/{table}.csv: {row_id}", quote_col, [("", key, cell)]))
        if one_quote:
            self.quote_checks.append((where, "quote", one_quote))

    def check_indexed_by(
        self,
        where: str,
        entry: Mapping[str, object],
        indexed_by: object,
        columns: Mapping[str, str],
        resolved: dict[str, object],
    ) -> bool:
        """Reads the table an input is indexed by and its columns into `resolved`; False when a
        parameter's values could not be read."""
        if self.sampling_method == SHEET_RANDOM_NUMBERS:
            self.add(
                where,
                "indexed_by",
                "an input indexed by a table has no sheet column per row, so sheet_random_numbers cannot draw it",
            )
        name = _text(indexed_by)
        if name is None:
            self.add(where, "indexed_by", _missing_or(entry, "indexed_by", "a table name"))
            return False
        rel = f"data/{name}.csv"
        path = (self.folder / rel).resolve()
        self.named.add(path)
        if not path.is_file():
            self.add(where, "indexed_by", f"no table {rel}")
            return False
        parsed = self.csv(rel, path)
        if parsed is None:
            return False
        header, lines = parsed
        if not lines:
            self.add(rel, "-", "the table has no data rows")
            return False
        ids = [line[0] for line in lines]
        ok = True
        for n, row_id in enumerate(ids, 1):
            if not row_id.strip():
                self.add(f"{rel}: row {n}", header[0], "blank row identifier")
                ok = False
            elif ids.count(row_id) > 1:
                self.add(f"{rel}: {row_id}", header[0], f"row identifier {row_id!r} is not distinct")
                ok = False
        if not ok:
            return False
        self.tables[name] = tuple(dict(zip(header, line)) for line in lines)
        resolved["rows"] = ids
        values_ok = True
        for key, col in columns.items():
            text_key = key in COLUMN_TEXT_KEYS
            if col not in header:
                self.add(rel, col, f"no column {col!r} in the table")
                values_ok = values_ok and text_key
                continue
            i = header.index(col)
            cells = [line[i] for line in lines]
            if text_key:
                for row_id, cell in zip(ids, cells):
                    if not cell.strip():
                        self.add(f"{rel}: {row_id}", col, f"blank {key}")
                    elif key == "source" and self.sources is not None and cell not in self.sources:
                        self.add(f"{rel}: {row_id}", col, f"{cell!r} is not a key in sources.toml")
                    elif key == "source":
                        self.ref(f"{rel}: {row_id}", col, cell)
                resolved[key] = cells
                continue
            numbers: list[float] = []
            for row_id, cell in zip(ids, cells):
                try:
                    number = float(cell)
                except ValueError:
                    number = math.nan
                if not math.isfinite(number):
                    self.add(f"{rel}: {row_id}", col, f"{cell!r} is not a finite number")
                    values_ok = False
                numbers.append(number)
            resolved[key] = numbers
        return values_ok

    def read_empirical(self, where: str, file_raw: object, column_raw: object) -> list[float] | None:
        rel, col = _text(file_raw), _text(column_raw)
        if rel is None:
            self.add(where, "data_file", "must be a non-empty path")
        if col is None:
            self.add(where, "column", "must be a non-empty column name")
        if rel is None or col is None:
            return None
        path = self.inside(where, "data_file", rel)
        if path is None:
            return None
        parsed = self.csv(rel, path)
        if parsed is None:
            return None
        header, lines = parsed
        if col not in header:
            self.add(rel, col, f"no column {col!r} in the file")
            return None
        i = header.index(col)
        values: list[float] = []
        ok = True
        for n, line in enumerate(lines, 1):
            try:
                number = float(line[i])
            except ValueError:
                number = math.nan
            if not math.isfinite(number):
                self.add(f"{rel}: row {n}", col, f"{line[i]!r} is not a finite number")
                ok = False
            values.append(number)
        return values if ok else None

    def draw_check(self, where: str, resolved: Mapping[str, object], columns: Mapping[str, str]) -> bool:
        """Settled choice 3: each resolved input drawn once at u = 0.5, once per row when indexed; True
        when every draw passed."""
        params = [k for k in columns if k not in COLUMN_TEXT_KEYS]
        rows = cast(Sequence[str], resolved.get("rows", ()))
        specs: list[Mapping[str, object]] = [resolved]
        if rows:
            specs = [{**resolved, **{k: cast(list[float], resolved[k])[i] for k in params}} for i in range(len(rows))]
        for spec in specs:
            try:
                if spec.get("distribution") == "categorical":
                    distributions.choose(spec, MIDDLE)
                else:
                    distributions.quantile(spec, MIDDLE)
            except ValueError as e:
                self.add(where, "distribution", str(e))
                return False
        return True

    def check_guidance_input(self, where: str, input_name: str, entry: Mapping[str, object]) -> dict[str, object] | None:
        self.unknown(where, entry, GUIDANCE_INPUT_KEYS)
        key = self.need_text(where, entry, "guidance")
        if key is None or self.guidance is None:
            return None
        jurisdiction, dot, name = key.partition(".")
        if not dot or jurisdiction != self.jurisdiction:
            self.add(where, "guidance", f"{key!r} is not <jurisdiction>.<entry> for the case's jurisdiction {self.jurisdiction!r}")
            return None
        g = _table(self.guidance.get(name))
        if g is None or "value" not in g:
            self.add(where, "guidance", f"{self.guide_label} has no entry {name!r} with a value")
            return None
        gw = f"{self.guide_label}: {name}"
        self.guided[input_name] = (gw, g)
        value = _real(g["value"])
        if value is None:
            self.add(gw, "value", f"must be a number, got {g['value']!r}")
        self.check_guidance_entry(name, g)
        unit, guide_unit = entry.get("unit"), _text(g.get("unit"))
        if guide_unit is None:
            self.add(gw, "unit", _missing_or(g, "unit", "a non-empty string"))
        elif _text(unit) is not None and unit != guide_unit:
            self.add(where, "unit", f"unit {unit!r} differs from the guidance entry {gw}'s unit {guide_unit!r}")
        cited = {"document": g.get("document"), "url": g.get("url"), "quote": g.get("quote")}
        if "low" not in g and "high" not in g:
            return {**entry, "distribution": "constant", "mean": value, **cited}
        bounds = self.guidance_range(gw, g, value)
        if value is None or bounds is None:
            return None  # the brief's settled choice 2.2: a refused range leaves its input unresolved
        return {**entry, "distribution": "triangular", "min": bounds[0], "mode": value, "max": bounds[1], **cited}

    def guidance_range(self, gw: str, g: Mapping[str, object], value: float | None) -> tuple[float, float] | None:
        """The brief's settled choice 2.1: a guidance value's low and high, drawn as the triangular (low, value,
        high); None when refused. With a value that is not a number, low below high is still checked."""
        bounds: dict[str, float] = {}
        for key, other in (("low", "high"), ("high", "low")):
            if key not in g:
                self.add(gw, key, f"missing: {other} is given, so {key} is needed too")
                continue
            number = _real(g[key])
            if number is None:
                self.add(gw, key, f"must be a finite number, got {g[key]!r}")
            else:
                bounds[key] = number
        if len(bounds) < 2:
            return None
        low, high = bounds["low"], bounds["high"]
        ok = True
        if value is not None and low > value:
            self.add(gw, "low", f"low {low!r} lies above value {value!r}")
            ok = False
        elif low == high or (value is None and low > high):  # with a value, low above high is one of the others
            self.add(gw, "low", f"low {low!r} must lie below high {high!r}")
            ok = False
        if value is not None and high < value:
            self.add(gw, "high", f"high {high!r} lies below value {value!r}")
            ok = False
        return (low, high) if ok else None

    def check_stored_quotes(self) -> None:
        """Settled choices 1.3 and 1.4 of the quotes brief: one problem per quote's place, naming each quote
        that has no stored text or is not found in it; a text that cannot be read is refused at the text. Each
        source with no stored text also gets one problem saying how to store it, so the seat stores it and loads
        again (`missing_text`)."""
        missing: list[str] = []
        plain: dict[str, list[str]] = {}  # each stored text made plain once, in its forms, however many quotes it meets
        for where, field, items in self.quote_checks:
            failing: list[str] = []
            for name, key, quote in items:
                text = self.stored_text(key)
                if key in self.unreadable:
                    continue
                path = f"sources/{key}/text.txt"
                if text is None:
                    failing.append(f"{name + ': ' if name else ''}no stored text at {path}")
                    if key not in missing:
                        missing.append(key)
                else:
                    if key not in plain:
                        plain[key] = forms(text)
                    if not found_in(quote, plain[key]):
                        failing.append(f"{name + ': ' if name else ''}{quote!r} not found in {path}")
            if failing:
                self.add(where, field, "; ".join(failing))
        for key in missing:
            hint = self.missing_text(key)
            if hint is not None:
                self.add(f"sources/{key}/text.txt", "-", f"no stored text: {hint}")

    def missing_text(self, key: str) -> str | None:
        """How to store a quoted source that has no text: its address from sources.toml and the shared source
        store's command, so the seat fetches it and loads again; None for a key that is no plain path component or
        not in sources.toml, which other checks refuse. A stored file is a cache filled from the original, so the
        message sends the seat online; the stop stays, since it is the check that each quoted line is in its
        source, and a source nobody can fetch still stops the case."""
        if key in ("", ".", "..") or "/" in key or "\\" in key or self.sources is None or key not in self.sources:
            return None
        folder = self.folder / "sources" / key
        held = sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []
        record: object = None
        if "source.json" in held:
            try:
                record = json.loads((folder / "source.json").read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, ValueError):
                pass  # an unreadable record is treated as no record
        if (r := _table(record)) is not None and r.get("text_method") == "none" and any(
                h.startswith("original.") for h in held):
            return ("its original is stored but no text was extracted from it: make text.txt from the original "
                    "with another tool, write how in source.json's text_method, and load again")
        entry = _table(self.sources[key]) or {}
        # a case's sources.toml names the address url, the methods index (research/refs.toml) names it link
        url, doi = _text(entry.get("url")) or _text(entry.get("link")), _text(entry.get("doi"))
        address = url or (f"https://doi.org/{doi}" if doi else None)
        shared = next((f for f in (TOOL / "shared", TOOL.parent / "shared")
                       if (f / "tools" / "source_store.py").is_file()), None)
        if shared is None:
            store = "the shared folder's source store, tools/source_store.py (the source-fetcher agent runs it)"
        else:
            python = next((p for p in (shared / ".venv" / "bin" / "python", TOOL / ".venv" / "bin" / "python")
                           if p.is_file()), Path("python3"))
            parts = [str(python), "-m", "tools.source_store", key, address or "URL", "--to",
                     str(self.folder.resolve() / "sources"), "--citation", _text(entry.get("citation")) or "CITATION"]
            for flag, value in (("--doi", doi), ("--licence", _text(entry.get("licence")))):
                if value is not None:
                    parts += [flag, value]
            store = f"`cd {shlex.quote(str(shared))} && {shlex.join(parts)}`"
        if held == ["source.json"]:
            return (f"sources/{key}/ holds only the record a public copy keeps of a text its licence bars it from "
                    f"carrying; the store fills it from the record's own address with {store}, and you load again: "
                    "exit 0 means it stored the original and the text; exit 2 means it stored the original alone, and "
                    "you make text.txt by the method source.json names; exit 1 (or 3, when the site refused the "
                    "fetch) means it stored nothing, and a source that cannot be fetched still stops the case")
        first = ""
        if held:
            first = f"look at sources/{key}/, which holds {', '.join(held)} but no text.txt and which the store refuses; then "
        if address is None:
            return (f"sources.toml gives it no url or doi: {first}find a free legal copy by its citation, add its url "
                    f"to sources.toml, store it with {store} (URL being that address) and load again; a source that "
                    "cannot be found still stops the case")
        return (f"{first}store it from its address in sources.toml, {address}, with {store}, and load again; a source "
                "that cannot be fetched from there or elsewhere still stops the case")

    def stored_text(self, key: str) -> str | None:
        """Settled choice 1.2 of the quotes brief: `sources/<key>/text.txt` read as UTF-8, only when the key is
        one plain path component and the resolved path is a regular file inside the case's sources/."""
        if key not in self.texts:
            self.texts[key] = None
            if key not in ("", ".", "..") and "/" not in key and "\\" not in key:
                store = self.folder / "sources"
                path: Path | None = None
                try:
                    path = (store / key / "text.txt").resolve()
                except OSError:
                    pass  # a path that cannot be resolved has no stored text
                if path is not None and path.is_relative_to(store) and path.is_file():
                    try:
                        self.texts[key] = path.read_bytes().decode("utf-8")
                    except (OSError, UnicodeDecodeError) as e:
                        self.unreadable.add(key)
                        self.add(f"sources/{key}/text.txt", "-", f"cannot be read as UTF-8 text: {e}")
        return self.texts[key]

    # ------------------------------------------------------------ money

    def check_money(self, doc: Mapping[str, object]) -> dict[str, Conversion]:
        """Settled choices 1 to 6 of the money brief and its four cascades: each input's money keys, each exchange-rate
        input, the money of each guidance entry an official_guidance input uses, no currency in a unit, each pinned
        edition's `[price_index]`, and the conversion of every money input whose money differs from the case's."""
        entries = {n: t for n, raw in doc.items() if n != "rank_correlation" and (t := _table(raw)) is not None}
        indices, index_currencies, blind = self.check_price_indices()
        pairs, rate_currencies, silenced, from_refused = self.check_rates(entries)
        names_currency = self.currency_matcher(index_currencies | rate_currencies)
        money: dict[str, Money] = {}
        entry_money: dict[str, Money] = {}
        for name, entry in entries.items():
            where = f"inputs.toml: {name}"
            if entry.get("evidence_type") == "official_guidance":
                if name not in self.guided:
                    continue  # its entry does not resolve, reported by check_guidance_input
                gw, g = self.guided[name]
                if gw not in entry_money:
                    entry_money[gw] = self.read_money(gw, g)
                    unit = _text(g.get("unit"))
                    if unit is not None and names_currency(unit):
                        self.add(gw, "unit", f"unit {unit!r} names a currency: give it as currency and price_year")
                money[name] = entry_money[gw]
                continue
            unit = _text(entry.get("unit"))
            is_rate = any(k in entry for k in RATE_KEYS)
            if unit is not None and names_currency(unit):
                hint = "from_currency and to_currency" if is_rate else "currency and price_year"
                self.add(where, "unit", f"unit {unit!r} names a currency: give it as {hint}")
            has_money = any(k in entry for k in MONEY_KEYS)
            distribution = entry.get("distribution")
            if is_rate:
                money[name] = "refused" if has_money else "none"  # refused by check_rates
            elif has_money and distribution in ("categorical", "mixture"):
                why = "a categorical is not an amount of money" if distribution == "categorical" else (
                    "a mixture carries no money keys: each component is converted by its own currency and price_year"
                )
                self.add(where, "currency", why)
                money[name] = "refused"
            elif distribution != "mixture":
                money[name] = self.read_money(where, entry)
        self.check_mixture_money(entries, money)
        if self.case_currency is None:
            return {}  # cascade 2: a refused case currency silences every conversion problem
        return self.conversions(money, indices, blind, pairs, silenced, from_refused)

    def read_money(self, where: str, entry: Mapping[str, object]) -> Money:
        """Settled choices 1.1, 1.2 and 3.1: `currency` and `price_year`, both or neither, each one value."""
        if not any(k in entry for k in MONEY_KEYS):
            return "none"
        currency, year = _currency(entry.get("currency")), _year(entry.get("price_year"))
        for key, value, other, wanted in (
            ("currency", currency, "price_year", "three upper-case letters, such as AUD, one for the whole input"),
            ("price_year", year, "currency", "a year, an integer from 1000 to 9999, one for the whole input"),
        ):
            if key not in entry:
                self.add(where, key, f"missing: {other} is given, so {key} is needed too")
            elif value is None:
                self.add(where, key, f"must be {wanted}, got {entry[key]!r}")
        return (currency, year) if currency is not None and year is not None else "refused"

    def check_rates(
        self, entries: Mapping[str, Mapping[str, object]]
    ) -> tuple[dict[tuple[str, str], str], set[str], set[str], bool]:
        """Settled choice 2: each exchange-rate input. Returns the first rate input for each (from, to) pair whose
        currencies are well formed (cascade 1: it serves even when its other keys are refused), every well-formed
        currency a rate names, the from_currency of each rate whose to_currency is refused or which is refused under
        2.2, and whether any rate's from_currency is missing or refused (the check's open choice 2)."""
        pairs: dict[tuple[str, str], str] = {}
        named: set[str] = set()
        silenced: set[str] = set()
        from_refused = False
        for name, entry in entries.items():
            if entry.get("evidence_type") == "official_guidance" or not any(k in entry for k in RATE_KEYS):
                continue
            where = f"inputs.toml: {name}"
            ends: dict[str, str | None] = {}
            for key in ("from_currency", "to_currency"):
                ends[key] = _currency(entry.get(key))
                if ends[key] is None:
                    self.add(where, key, _missing_or(entry, key, "three upper-case letters, such as USD"))
            frm, to = ends["from_currency"], ends["to_currency"]
            named |= {c for c in (frm, to) if c is not None}
            if frm is not None and frm == to:
                self.add(where, "to_currency", f"to_currency {to!r} is from_currency too: a rate converts between two currencies")
                to = None
            rate_year = _year(entry.get("rate_year"))
            if rate_year is None:
                self.add(where, "rate_year", _missing_or(entry, "rate_year", "a year, an integer from 1000 to 9999"))
            elif self.price_base_year is not None and rate_year != self.price_base_year:
                self.add(
                    where,
                    "rate_year",
                    f"rate_year {rate_year} is not price_base_year {self.price_base_year}: the rate converts money already "
                    "in the price base year's prices",
                )
            refused = False
            for key in MONEY_KEYS:
                if key in entry and not refused:
                    self.add(where, key, f"a rate is not an amount of one currency: {key} does not belong on it")
                    refused = True
            distribution = entry.get("distribution")
            reason = None
            if distribution in ("categorical", "mixture"):
                reason = f"a rate is drawn as one quantity, not as a {distribution} (not yet ruled)"
            elif "indexed_by" in entry:
                reason = "a rate is one value for the whole case, not indexed by a table (not yet ruled)"
            elif name in self.named_by:
                reason = f"a rate is not a component of a mixture ({', '.join(self.named_by[name])}; not yet ruled)"
            if reason is not None:
                self.add(where, "from_currency", reason)
                refused = True
            if frm is None:
                from_refused = True
            elif to is None or refused:
                silenced.add(frm)
            if frm is not None and to is not None:
                first = pairs.setdefault((frm, to), name)
                if first != name:
                    self.add(where, "to_currency", f"the rate from {frm} to {to} is given already by {first}")
        return pairs, named, silenced, from_refused

    def check_price_indices(self) -> tuple[dict[str, _Index], set[str], bool]:
        """Settled choice 6: each pinned edition's `[price_index]`, the case's own edition first. Returns the index
        serving each currency, every well-formed currency an index names, and whether an index may be unseen (a
        pinned edition not read, or an index whose currency is refused: cascade 3)."""
        editions: list[tuple[str, str, dict[str, object] | None]] = []
        own = self.editions.get(self.jurisdiction)
        if own is not None:
            editions.append((self.jurisdiction, own, self.guidance))
        editions += self.other_docs
        blind = self.guidance is None
        indices: dict[str, _Index] = {}
        named: set[str] = set()
        for jurisdiction, edition, doc in editions:
            if doc is None:
                blind = True
                continue
            if PRICE_INDEX not in doc:
                continue  # settled choice 6.3: refused through 5.4.1 when a conversion needs it
            where = f"{jurisdiction}/{edition}.toml: {PRICE_INDEX}"
            pi = _table(doc[PRICE_INDEX])
            if pi is None:
                self.add(where, "-", "must be a table")
                blind = True
                continue
            currency = _currency(pi.get("currency"))
            if currency is None:
                self.add(where, "currency", _missing_or(pi, "currency", "three upper-case letters, such as AUD"))
                blind = True
            for key in PRICE_INDEX_TEXT:
                self.need_text(where, pi, key)
            years = self.index_years(where, pi)
            self.check_research(where, pi, years)
            if currency is None:
                continue
            named.add(currency)
            if currency in indices:
                first = indices[currency]
                self.add(
                    "case.toml",
                    f"other_guidance_editions.{jurisdiction}",
                    f"{jurisdiction}/{edition}.toml's price index is in {currency}, which "
                    f"{first.jurisdiction}/{first.edition}.toml's serves already",
                )
                continue
            indices[currency] = _Index(jurisdiction, edition, _text(pi.get("series")) or "", years)
        return indices, named, blind

    def index_years(self, where: str, pi: Mapping[str, object]) -> dict[int, float | None] | None:
        """A `[price_index]`'s calendar_year, by `price_index_years`, its problem added."""
        years, problem = price_index_years(pi)
        if problem is not None:
            self.add(where, "calendar_year", problem)
        return years

    def check_research(self, where: str, pi: Mapping[str, object], years: Mapping[int, float | None] | None) -> None:
        """A `[price_index]` citing `research_file` (its path from the folder holding the guidance root, inside
        `research/price_indices/<date>/`) and `research_table` (the dotted key of that file's table of period to value)
        holds that table's calendar years and values, relative 1e-12, read on every load. A table of financial years
        ("2024-25") gives calendar year Y as the mean of (Y-1)-Y and Y-(Y+1), the editions' derivation (the owner's
        ruling of 2026-10-30 that every price year is a calendar year)."""
        if "research_file" not in pi and "research_table" not in pi:
            return
        rel, dotted = self.need_text(where, pi, "research_file"), self.need_text(where, pi, "research_table")
        if rel is None or dotted is None or self.root is None:
            return
        base = self.root.parent
        path = (base / rel).resolve()
        if not path.is_relative_to(base / "research" / "price_indices") or not path.is_file():
            self.add(where, "research_file", f"{rel}: no such file in {base / 'research' / 'price_indices'}")
            return
        table: object = self.toml(rel, path)
        for key in dotted.split("."):
            table = (_table(table) or {}).get(key)
        raw = _table(table)
        if not raw:
            self.add(where, "research_table", f"{rel} has no table {dotted!r}")
            return
        values = {k: _real(v) for k, v in raw.items()}
        research: dict[int, float | None] = {}
        if all(YEAR_KEY.fullmatch(k) for k in values):
            research = {int(k): v for k, v in values.items()}
        elif all((m := FINANCIAL_YEAR_KEY.fullmatch(k)) and int(m[2]) == (int(m[1]) + 1) % 100 for k in values):
            starts = {int(k[:4]): v for k, v in values.items()}
            for y in sorted(starts):
                first, second = starts[y], starts.get(y + 1)
                if y + 1 in starts:
                    research[y + 1] = (first + second) / 2 if first is not None and second is not None else None
        else:
            self.add(where, "research_table", f"{rel} [{dotted}]: keys are neither all calendar years nor all financial years")
            return
        if years is None:
            return  # the calendar_year table itself is refused by index_years
        off: list[str] = []
        for y in sorted(set(years) | set(research)):
            here, there = years.get(y), research.get(y)
            if y not in research or y not in years:
                off.append(f"{y} is {'only here' if y not in research else 'only there'}")
            elif here is not None and (there is None or not math.isclose(here, there, rel_tol=1e-12, abs_tol=0.0)):
                off.append(f"{y} is {here!r} here, {there!r} there")
        if off:
            self.add(where, "research_file", f"calendar_year does not match {rel} [{dotted}]: " + "; ".join(off))

    def currency_matcher(self, named: set[str]) -> Callable[[str], bool]:
        """Settled choice 4.1: whether a unit names a currency, by a code or word not run into other letters (in any
        letter case the listed codes, the case's, those an index or a rate names, and the words; in upper case the rest
        of ISO 4217), a sign, or a currency's word in Hangul or Han."""
        return unit_currency_matcher(named | ({self.case_currency} if self.case_currency is not None else set()))

    def check_mixture_money(self, entries: Mapping[str, Mapping[str, object]], money: Mapping[str, Money]) -> None:
        """Settled choice 1.3 with the check's open choice 1: a mixture's readable components are all money or none,
        each differing from the first readable one refused at its own currency. A component already refused at the
        mixture, not an input, unresolved, with refused money keys, or a mixture of mixed components is not read."""
        status: dict[str, bool | None] = {}

        def of(n: str) -> bool | None:
            m = money.get(n)
            if m == "refused" or n not in entries:
                return None
            if n not in self.mixtures:
                return None if m is None else m != "none"
            if n in status:
                return status[n]
            status[n] = None  # a ring is refused by check_mixtures
            readable: list[tuple[str, bool]] = []
            for c in self.mixture_tables.get(n, {}):
                s = of(c) if (n, c) not in self.refused_components else None
                if s is not None:
                    readable.append((c, s))
            if not readable:
                return None
            first, first_status = readable[0]
            mixed = False
            for c, s in readable[1:]:
                if s != first_status:
                    kind = "is not money" if first_status else "is money"
                    self.add(
                        f"inputs.toml: {c}",
                        "currency",
                        f"the components of the mixture {n} are all money or none, and {first}, its first, {kind}",
                    )
                    mixed = True
            status[n] = None if mixed else first_status
            return status[n]

        for m in self.mixtures:
            of(m)

    def conversions(
        self,
        money: Mapping[str, Money],
        indices: Mapping[str, _Index],
        blind: bool,
        pairs: Mapping[tuple[str, str], str],
        silenced: set[str],
        from_refused: bool,
    ) -> dict[str, Conversion]:
        """Settled choice 5: the price step in the input's own currency, then the rate step to the case's."""
        case_currency, base = cast(str, self.case_currency), self.price_base_year
        out: dict[str, Conversion] = {}
        for name, m in money.items():
            if isinstance(m, str) or m == (case_currency, base):
                continue
            where = f"inputs.toml: {name}"
            currency, year = m
            factor, step, ok = 1.0, None, base is not None  # cascade 2: no price step without the base year
            if base is not None and year != base:
                index = indices.get(currency)
                if index is None:
                    if not blind:
                        self.add(where, "price_year", f"no pinned edition's [{PRICE_INDEX}] is in {currency}")
                    ok = False
                elif index.years is not None:
                    absent = [y for y in (year, base) if y not in index.years]
                    if absent:
                        self.add(
                            where,
                            "price_year",
                            f"{index.jurisdiction}/{index.edition}.toml's [{PRICE_INDEX}] has no calendar_year "
                            f"{' or '.join(str(y) for y in absent)}",
                        )
                    ok = ok and not absent
                    old, new = index.years.get(year), index.years.get(base)
                    if old is not None and new is not None:
                        factor = new / old
                        step = PriceStep(index.jurisdiction, index.edition, index.series, year, base, old, new)
                    else:
                        ok = False
                else:
                    ok = False
            rate = None
            if currency != case_currency:
                rate = pairs.get((currency, case_currency))
                if rate is None:
                    if not from_refused and currency not in silenced:
                        self.add(where, "currency", f"no rate input from {currency} to {case_currency}")
                    ok = False
            if ok:
                out[name] = Conversion(currency, year, factor, step, rate)
        return out

    # ------------------------------------------------------------ rank correlations

    def check_rank_correlations(self, raw: object, doc: Mapping[str, object]) -> list[tuple[str, str, float]]:
        if not isinstance(raw, list):
            self.add(
                "inputs.toml",
                "rank_correlation",
                "must be [[rank_correlation]] entries; no input may be named rank_correlation",
            )
            return []
        out: list[tuple[str, str, float]] = []
        index: list[int] = []
        seen: set[frozenset[str]] = set()
        ok = True
        for i, item in enumerate(cast(list[object], raw)):
            where = f"inputs.toml: rank_correlation[{i}]"
            entry = _table(item)
            if entry is None:
                self.add(where, "-", "must be a table")
                ok = False
                continue
            type_raw = entry.get("evidence_type")
            evidence_type = (
                type_raw
                if isinstance(type_raw, str) and type_raw in EVIDENCE_TYPE_KEYS and type_raw != "official_guidance"
                else None
            )
            if evidence_type is None:
                self.add(
                    where,
                    "evidence_type",
                    _missing_or(entry, "evidence_type", "an evidence type as an input's, other than official_guidance"),
                )
            allowed = EVIDENCE_TYPE_KEYS[evidence_type] if evidence_type else ALL_EVIDENCE_TYPE_KEYS
            self.unknown(where, entry, RANK_CORRELATION_KEYS | allowed)
            if evidence_type is not None:
                self.check_evidence_type(where, entry, evidence_type, {})
            names = entry.get("inputs")
            pair = cast(list[object], names) if isinstance(names, list) else []
            reason = None
            if len(pair) != 2 or not all(isinstance(x, str) for x in pair):
                reason = _missing_or(entry, "inputs", "two input names")
            else:
                a, b = cast(str, pair[0]), cast(str, pair[1])
                for x in (a, b):
                    if x == "rank_correlation" or x not in doc:
                        reason = f"{x!r} is not an input"
                    elif self.input_distribution.get(x) in UNCORRELATABLE:
                        reason = f"{x!r} is a {self.input_distribution[x]}, whose pick does not rise with the uniform number"
                    elif x in self.input_indexed:
                        reason = f"{x!r} is indexed by a table"
                    elif x in self.named_by:
                        reason = f"{x!r} is a component of the mixture {', '.join(self.named_by[x])}, drawn only through it"
                if reason is None and a == b:
                    reason = f"{a!r} is paired with itself"
                if reason is None and frozenset((a, b)) in seen:
                    reason = f"the pair {a}, {b} is given twice"
                seen.add(frozenset((a, b)))
            if reason is not None:
                self.add(where, "inputs", reason)
                ok = False
            coefficient = _real(entry.get("coefficient"))
            if coefficient is None or not -1.0 < coefficient < 1.0:
                self.add(where, "coefficient", _missing_or(entry, "coefficient", "a number inside (-1, 1)"))
                ok = False
            if reason is None and coefficient is not None:
                out.append((cast(str, pair[0]), cast(str, pair[1]), coefficient))
                index.append(i)
        if ok:
            self.check_feasible(out, index)
        return out

    def check_feasible(self, pairs: Sequence[tuple[str, str, float]], index: Sequence[int]) -> None:
        """Settled choice 25: each connected group's target matrix, 2 sin(pi rho / 6) as sampling.py
        builds it, must factor by Cholesky."""
        group_of: dict[str, set[str]] = {}
        for a, b, _ in pairs:
            merged = group_of.get(a, {a}) | group_of.get(b, {b})
            for x in merged:
                group_of[x] = merged
        done: set[frozenset[str]] = set()
        for group in group_of.values():
            key = frozenset(group)
            if key in done:
                continue
            done.add(key)
            members = sorted(group)
            target = np.eye(len(members))
            mine = [(i, a, b, rho) for i, (a, b, rho) in zip(index, pairs) if a in group]
            for _, a, b, rho in mine:
                x, y = members.index(a), members.index(b)
                target[x, y] = target[y, x] = 2.0 * math.sin(math.pi * rho / 6.0)
            try:
                np.linalg.cholesky(target)
            except np.linalg.LinAlgError:
                for i, *_ in mine:
                    self.add(
                        f"inputs.toml: rank_correlation[{i}]",
                        "coefficient",
                        f"the rank correlations among {members} cannot hold together",
                    )

    # ------------------------------------------------------------ sources and data

    def check_sources(self) -> dict[str, Mapping[str, object]]:
        out: dict[str, Mapping[str, object]] = {}
        if self.sources is None:
            return out
        for key in self.used:
            where = f"sources.toml: {key}"
            entry = _table(self.sources[key])
            if entry is None:
                self.add(where, "citation", "a source must be a table with a citation and a licence")
                continue
            self.unknown(where, entry, SOURCE_KEYS)
            self.need_text(where, entry, "citation")
            self.need_text(where, entry, "licence")
            for optional in ("url", "doi"):
                if optional in entry:
                    self.need_text(where, entry, optional)
        for key, value in self.sources.items():
            entry = _table(value)
            if entry is not None:
                out[key] = entry
        return out

    def check_data_files(self) -> None:
        """Every file in data/ is named by an input's indexed_by or data_file, an external model output's file
        or an expert judgement's judgement_record, or is a note (a name ending in .md or .txt)."""
        data = self.folder / "data"
        if not data.is_dir():
            return
        for path in sorted(data.rglob("*")):
            if path.is_file() and path.resolve() not in self.named and not path.name.endswith(NOTE_SUFFIXES):
                self.add(path.relative_to(self.folder).as_posix(), "-", "no input names this file")

