from __future__ import annotations

from datetime import date
from decimal import Decimal

from scripts.analyze_whipsaw import (
    month_end_closes,
    turning_point_months,
    yearly_counts,
)


def _monthly_series(closes: list[str], *, start_year: int = 2020) -> dict[tuple[int, int], Decimal]:
    series: dict[tuple[int, int], Decimal] = {}
    year, month = start_year, 1
    for close in closes:
        series[(year, month)] = Decimal(close)
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return series


def test_monotonic_trend_has_no_turning_points() -> None:
    closes = [str(100 + index) for index in range(30)]

    points = turning_point_months(_monthly_series(closes), fast_months=1)

    assert points == []


def test_single_down_month_inside_an_uptrend_is_one_turning_point() -> None:
    # 13 rising months, one pullback, then rising again: slow 12M momentum
    # stays positive throughout; only the pullback month disagrees.
    closes = [str(100 + index) for index in range(13)] + ["105", "120", "121"]

    points = turning_point_months(_monthly_series(closes), fast_months=1)

    assert points == [(2021, 2)]


def test_flat_fast_leg_is_not_a_turning_point() -> None:
    # Month 14 repeats month 13's close: fast momentum is exactly zero,
    # which is agreement (no sign flip), not a turning point.
    closes = [str(100 + index) for index in range(13)] + ["112"]

    points = turning_point_months(_monthly_series(closes), fast_months=1)

    assert points == []


def test_yearly_counts_group_by_calendar_year() -> None:
    assert yearly_counts([(2019, 1), (2019, 7), (2020, 2)]) == {2019: 2, 2020: 1}


def test_month_end_sampling_drops_the_trailing_partial_month() -> None:
    closes_by_day = {
        date(2026, 5, 30): Decimal("10"),
        date(2026, 5, 31): Decimal("11"),  # true month end
        date(2026, 6, 29): Decimal("12"),
        date(2026, 6, 30): Decimal("13"),  # true month end
        date(2026, 7, 2): Decimal("14"),  # partial month: must be dropped
    }

    monthly = month_end_closes(closes_by_day)

    assert monthly == {(2026, 5): Decimal("11"), (2026, 6): Decimal("13")}


def test_month_end_sampling_keeps_a_complete_final_month() -> None:
    closes_by_day = {
        date(2026, 5, 31): Decimal("11"),
        date(2026, 6, 30): Decimal("13"),
    }

    monthly = month_end_closes(closes_by_day)

    assert monthly == {(2026, 5): Decimal("11"), (2026, 6): Decimal("13")}
