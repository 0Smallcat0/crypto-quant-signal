"""Validation helpers for public candle streams."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from src.data.types import (
    CandleIssueCode,
    CandleQualityIssue,
    CandleQualityReport,
    MarketDataValidationError,
)
from src.domain import Candle, Timeframe

_TIMEFRAME_DELTAS = {
    "15m": timedelta(minutes=15),
    "1d": timedelta(days=1),
}


def timeframe_delta(timeframe: Timeframe) -> timedelta:
    """Return the expected candle spacing for a supported MVP timeframe."""

    try:
        return _TIMEFRAME_DELTAS[timeframe.value]
    except KeyError as exc:
        msg = f"unsupported timeframe for data quality checks: {timeframe.value}"
        raise MarketDataValidationError(msg) from exc


def require_closed_candles(candles: Iterable[Candle]) -> tuple[Candle, ...]:
    """Return candles only when every item is closed; otherwise raise a hard block."""

    candle_tuple = tuple(candles)
    open_candles = [candle for candle in candle_tuple if not candle.is_closed]
    if open_candles:
        first = open_candles[0]
        msg = (
            "OPEN_CANDLE: candle is not safe for strategy input "
            f"({first.symbol.value} {first.timeframe.value} {first.open_time.isoformat()})"
        )
        raise MarketDataValidationError(msg)
    return candle_tuple


def inspect_candle_quality(
    candles: Iterable[Candle],
    *,
    timeframe: Timeframe,
    observed_at: datetime,
    stale_after: timedelta,
) -> CandleQualityReport:
    """Detect visible open-candle, duplicate, gap, and stale-data issues."""

    _require_utc("observed_at", observed_at)
    if stale_after <= timedelta(0):
        msg = "stale_after must be positive"
        raise MarketDataValidationError(msg)

    candle_tuple = tuple(candles)
    expected_delta = timeframe_delta(timeframe)
    issues: list[CandleQualityIssue] = []

    for candle in candle_tuple:
        if not candle.is_closed:
            issues.append(
                CandleQualityIssue(
                    code=CandleIssueCode.OPEN_CANDLE,
                    symbol=candle.symbol.value,
                    timeframe=candle.timeframe.value,
                    open_time=candle.open_time,
                    detail="still-open candle must not enter strategy input",
                )
            )

    candles_by_key: dict[tuple[str, str], list[Candle]] = defaultdict(list)
    for candle in candle_tuple:
        candles_by_key[(candle.symbol.value, candle.timeframe.value)].append(candle)

    for (symbol, candle_timeframe), grouped_candles in candles_by_key.items():
        sorted_candles = sorted(grouped_candles, key=lambda candle: candle.open_time)
        seen_open_times: set[datetime] = set()
        unique_closed_opens: list[datetime] = []
        closed_candles: list[Candle] = []
        for candle in sorted_candles:
            if candle.open_time in seen_open_times:
                issues.append(
                    CandleQualityIssue(
                        code=CandleIssueCode.DUPLICATE,
                        symbol=symbol,
                        timeframe=candle_timeframe,
                        open_time=candle.open_time,
                        detail="duplicate candle open time",
                    )
                )
                continue
            seen_open_times.add(candle.open_time)
            if candle.is_closed:
                unique_closed_opens.append(candle.open_time)
                closed_candles.append(candle)

        for previous_open, next_open in zip(unique_closed_opens, unique_closed_opens[1:]):
            expected_next_open = previous_open + expected_delta
            if next_open > expected_next_open:
                issues.append(
                    CandleQualityIssue(
                        code=CandleIssueCode.GAP,
                        symbol=symbol,
                        timeframe=candle_timeframe,
                        expected_open_time=expected_next_open,
                        actual_open_time=next_open,
                        detail="missing candle interval",
                    )
                )

        if closed_candles:
            latest_candle = max(closed_candles, key=lambda candle: candle.close_time)
            latest_closed_boundary = latest_candle.open_time + expected_delta
            if observed_at - latest_closed_boundary > stale_after:
                issues.append(
                    CandleQualityIssue(
                        code=CandleIssueCode.STALE,
                        symbol=latest_candle.symbol.value,
                        timeframe=latest_candle.timeframe.value,
                        open_time=latest_candle.open_time,
                        detail="latest closed candle is older than stale threshold",
                    )
                )

    return CandleQualityReport(issues=tuple(issues))


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise MarketDataValidationError(msg)
