"""A quote attributed to a source that the source does not contain is not found: cost_benefit_engine.quotes.quote_in,
which the case loader and research/records.py call, against a truth table written by hand. The parts either side of an
omission mark are each found, in order, each starting after the end of the one before; curly quotation marks, dashes
and a word hyphenated across a line end are compared as plain text."""

from __future__ import annotations

from cost_benefit_engine.quotes import quote_in

TEXT = "alpha beta gamma"
CASES: list[tuple[str, str, bool]] = [
    ("alpha beta", TEXT, True),
    ("alpha delta", TEXT, False),  # a word the text does not hold
    ("alpha gamma", TEXT, False),  # with no omission mark, one passage
    ("alpha ... gamma", TEXT, True),
    ("gamma ... alpha", TEXT, False),  # both parts occur, in the other order
    ("alpha [...] gamma", TEXT, True),
    ("alpha … gamma", TEXT, True),  # the one-character ellipsis
    ("... beta gamma", TEXT, True),  # an empty part dropped
    ("...", TEXT, False),  # no part remains
    (" [...] ", TEXT, False),
    ("abc ... bcd", "abcd", False),  # the second part must start after the end of the first
    ("ab ... cd", "abcd", True),
    ("“alpha” – beta", '"alpha" - beta', True),  # both made plain alike
    ("valuation", "valua-\ntion", True),
]


def test_quote_in_by_hand() -> None:
    for quote, text, found in CASES:
        assert quote_in(quote, text) is found, (quote, text)
