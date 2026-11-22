"""The arithmetic of cost_benefit_engine/timeline.py, each piece once, against a reference outside the code.

1. A constant rate: each factor is (1 + r) ** -t, and a level flow's present value is the annuity
   A (1 - (1 + r) ** -T) / r, at 7% over 15 years, within 1e-12 relative.
2. A declining schedule: the United Kingdom's, against the closed form 1.03 ** -min(t, 30) * 1.025 ** -(years 31 to
   75 reached) * 1.0225 ** -(years past 75) within 1e-12 relative, and against the printed table of HM Treasury,
   "Discounting: Green Book supplementary guidance", October 2026, Annex A "Discount factors", within 5e-5
   absolute, half a unit in the table's fourth decimal place. The table is the outside judge of how a declining
   schedule compounds (forward rates, the step-by-step product; its paragraph 3.9): Annex A prints 0.8626 (year
   5), 0.4120 (30), 0.4019 (31), 0.1356 (75), 0.1326 (76) and 0.0778 (100). Read from
   https://assets.publishing.service.gov.uk/media/6ae0b34016428df537606216/Green_Book_supplementary_guidance_-_discounting.pdf
   on 2026-10-30. The spot-rate reading would give 1.025 ** -31 = 0.4651 at year 31, which the tolerance refuses.
3. Each time shape against a stream written out here by hand; bring_forward's present-value identity
   PV(bring_forward(s, k)) = (1 + r) ** k PV(s) at a constant rate.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from cost_benefit_engine.timeline import (
    annual,
    appraisal_years,
    bring_forward,
    discount_factors,
    every_n_years,
    linear_phase_in,
    one_off,
    present_value,
)

D = 2026  # the year discounted to
UK: tuple[tuple[int, int | None, float], ...] = ((1, 30, 0.03), (31, 75, 0.025), (76, None, 0.0225))


def _years(first: int, last: int) -> NDArray[np.int64]:
    return np.arange(first, last + 1, dtype=np.int64)


def _uk_hand(t: int) -> float:
    """The Green Book factor of year t after discount_base_year, by closed form (forward rates)."""
    return 1.03 ** -min(t, 30) * 1.025 ** -max(0, min(t, 75) - 30) * 1.0225 ** -max(0, t - 75)


def _close(actual: NDArray[np.float64], expected: NDArray[np.float64], rel: float = 1e-12) -> None:
    assert actual.shape == expected.shape
    assert np.all(expected != 0), "a relative tolerance never meets an expected value of zero"
    assert np.all(np.abs(actual - expected) <= rel * np.abs(expected)), (actual, expected)


def test_constant_rate_factors_and_annuity() -> None:
    r = 0.07
    years = appraisal_years(D, D + 15)
    assert np.array_equal(years, np.arange(D, D + 16))
    f = discount_factors([(1, None, r)], years, D)
    _close(f, np.array([(1 + r) ** -t for t in range(16)]))
    amount = np.array([100.0, -250.5])
    pv = present_value(annual(amount, D + 1, D + 15, years, iterations=2), f)
    _close(pv, amount * (1 - (1 + r) ** -15) / r)


def test_uk_schedule_against_green_book_table() -> None:
    f = discount_factors(UK, _years(D, D + 100), D)
    _close(f, np.array([_uk_hand(t) for t in range(101)]))
    printed = {5: 0.8626, 30: 0.4120, 31: 0.4019, 75: 0.1356, 76: 0.1326, 100: 0.0778}
    for t, value in printed.items():
        assert abs(float(f[t]) - value) <= 5e-5, (t, float(f[t]), value)


def test_time_shapes_by_hand() -> None:
    """Per-draw amounts, a negative and a zero included."""
    years = _years(D, D + 7)  # columns 0..7
    a = np.array([10.0, -4.0, 0.0])
    col = a.reshape(3, 1)

    def blank() -> NDArray[np.float64]:
        return np.zeros((3, 8))

    def check(out: NDArray[Any], expected: NDArray[np.float64]) -> None:
        assert np.array_equal(out, expected), (out, expected)

    e = blank()
    e[:, 2] = a
    check(one_off(a, D + 2, years, iterations=3), e)

    e = blank()
    e[:, 1:5] = col
    check(annual(a, D + 1, D + 4, years, iterations=3), e)

    e = blank()
    e[:, [1, 4, 7]] = col
    check(every_n_years(a, 3, D + 1, D + 7, years, iterations=3), e)  # the last year included
    e = blank()
    e[:, [1, 4]] = col
    check(every_n_years(a, 3, D + 1, D + 6, years, iterations=3), e)

    e = blank()
    e[:, 2] = a / 3
    e[:, 3] = 2 * a / 3
    e[:, 4:7] = col
    assert np.allclose(linear_phase_in(a, D + 2, D + 4, D + 6, years, iterations=3), e, rtol=1e-15, atol=0.0)
    e = blank()
    e[:, 5:8] = col
    check(linear_phase_in(a, D + 5, D + 5, D + 7, years, iterations=3), e)


def test_shift_by_hand_and_present_value_identity() -> None:
    years = _years(D, D + 9)
    s = np.zeros((2, 10))
    s[:, 4:7] = [[3.0, 1.0, -2.0], [0.5, 0.0, 6.0]]
    for k in (2, -3, 4, 0):
        expected = np.zeros((2, 10))
        expected[:, 4 - k : 7 - k] = s[:, 4:7]
        assert np.array_equal(bring_forward(s, k, years), expected), k

    for r in (0.03, 0.07):
        f = discount_factors([(1, None, r)], years, D)
        flows = np.zeros((2, 10))
        flows[:, 3:9] = [[1.0, 2.0, 3.0, -1.0, 4.0, 5.0], [7.0, 0.0, 1.0, 1.0, 2.0, 9.0]]
        base = present_value(flows, f)
        for k in (3, 1, -1):
            _close(present_value(bring_forward(flows, k, years), f), (1 + r) ** k * base)
