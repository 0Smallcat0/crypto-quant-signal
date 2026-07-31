"""The live runtime must be able to run trial 118, not only the incumbent.

The Donchian ensemble existed in the backtest engine while
``src/runtime/engine.py`` hardcoded the daily trend ensemble, so the researched
strategy could never reach the signals a human acts on. These tests pin the
dispatch, the deeper warmup it needs, and the replay determinism that lets the
runtime carry window state without persisting it.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.domain import Candle, Symbol, Timeframe
from src.notify import CollectingNotificationChannel
from src.runtime import (
    WARMUP_INSUFFICIENT_HISTORY,
    JsonlEventStore,
    RuntimeParameters,
    SignalRuntime,
)
from src.runtime.types import DonchianRuntimeConfig

_BASE_OPEN_TIME = datetime(2025, 1, 1, 0, 0, tzinfo=UTC)
_FLAT_DAYS = 420


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _daily_candle(symbol: Symbol, index: int, close: Decimal) -> Candle:
    open_time = _BASE_OPEN_TIME + timedelta(days=index)
    return Candle(
        symbol=symbol,
        timeframe=Timeframe("1d"),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=close,
        high_price=close + Decimal("1"),
        low_price=max(close - Decimal("1"), Decimal("0.01")),
        close_price=close,
        volume=Decimal("1000"),
        is_closed=True,
    )


def _breakout_series(scale: Decimal, *, flat_days: int = _FLAT_DAYS) -> tuple[Decimal, ...]:
    """Flat for the whole warmup, then a run that clears every channel high."""

    prices = [Decimal("100") * scale] * flat_days
    prices.extend([(Decimal("120") + Decimal(step) * Decimal("5")) * scale for step in range(12)])
    return tuple(prices)


def _universe(*, flat_days: int = _FLAT_DAYS) -> dict[str, tuple[Candle, ...]]:
    return {
        "BTCUSDT": tuple(
            _daily_candle(_symbol("BTCUSDT", "BTC"), index, price)
            for index, price in enumerate(_breakout_series(Decimal("1"), flat_days=flat_days))
        ),
        "ETHUSDT": tuple(
            _daily_candle(_symbol("ETHUSDT", "ETH"), index, price)
            for index, price in enumerate(_breakout_series(Decimal("0.1"), flat_days=flat_days))
        ),
    }


def _parameters(*, strategy_name: str = "daily_trend_ensemble") -> RuntimeParameters:
    return RuntimeParameters(
        risk_budgets={"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")},
        initial_cash=Decimal("1000"),
        account_id="paper-main",
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("5"),
        quantity_step=Decimal("0.000001"),
        price_tick=Decimal("0.01"),
        min_notional_usdt=Decimal("10"),
        max_drawdown_fraction=Decimal("0.20"),
        daily_loss_pause_fraction=Decimal("0.05"),
        disaster_single_day_drop_fraction=Decimal("0.20"),
        stale_data_max_age_seconds=129600,
        idempotency_namespace="paper-runtime",
        strategy_name=strategy_name,
        donchian=DonchianRuntimeConfig(),
    )


def _runtime(store_path: Path, *, strategy_name: str) -> SignalRuntime:
    return SignalRuntime(
        parameters=_parameters(strategy_name=strategy_name),
        store=JsonlEventStore(store_path),
        channel=CollectingNotificationChannel(),
    )


def _signal_fractions(path: Path) -> list[str]:
    return [
        str(event.payload["exposure_fraction"])
        for event in JsonlEventStore(path).events_of_kind("signal")
    ]


def test_default_strategy_stays_the_incumbent(tmp_path: Path) -> None:
    """Adding the dispatch must not silently move anyone off daily trend."""

    assert _parameters().strategy_name == "daily_trend_ensemble"
    runtime = _runtime(tmp_path / "a.jsonl", strategy_name="daily_trend_ensemble")
    assert runtime.process_closed_candles(_universe()).processed is True


def test_donchian_runtime_emits_a_breakout_signal(tmp_path: Path) -> None:
    """Trial 118's strategy reaches the signal path the human acts on."""

    store_path = tmp_path / "b.jsonl"
    runtime = _runtime(store_path, strategy_name="donchian_breakout_ensemble")
    outcome = runtime.process_closed_candles(_universe())

    assert outcome.processed is True
    signals = [
        event
        for event in JsonlEventStore(store_path).events_of_kind("signal")
        if "BTCUSDT" in event.key
    ]
    assert signals, "donchian run produced no signal event"
    payload = signals[-1].payload
    assert Decimal(str(payload["exposure_fraction"])) > Decimal("0")
    reason_codes = payload["reason_codes"]
    assert isinstance(reason_codes, list)
    assert "DONCHIAN_ENSEMBLE" in reason_codes


def test_donchian_needs_more_history_than_daily_trend(tmp_path: Path) -> None:
    """240 closed candles satisfy the SMA warmup but not the Donchian replay.

    The replay must start far enough back that window state comes from real
    crossings rather than from where the slice happens to begin, so the deeper
    floor is a correctness requirement, not caution.
    """

    short = _universe(flat_days=240)
    assert all(len(candles) >= 200 for candles in short.values())

    incumbent = _runtime(tmp_path / "c.jsonl", strategy_name="daily_trend_ensemble")
    assert incumbent.process_closed_candles(short).processed is True

    donchian = _runtime(tmp_path / "d.jsonl", strategy_name="donchian_breakout_ensemble")
    skipped = donchian.process_closed_candles(short)
    assert skipped.processed is False
    assert skipped.reason == WARMUP_INSUFFICIENT_HISTORY


def test_donchian_decision_is_a_pure_function_of_price_history(tmp_path: Path) -> None:
    """Two fresh runtimes over identical candles must decide identically.

    The runtime deliberately does not persist window state; it replays. If that
    ever regressed to hidden state, a restart would change the signal, and this
    is what would catch it.
    """

    universe = _universe()
    first = _runtime(tmp_path / "g.jsonl", strategy_name="donchian_breakout_ensemble")
    second = _runtime(tmp_path / "h.jsonl", strategy_name="donchian_breakout_ensemble")
    first.process_closed_candles(universe)
    second.process_closed_candles(universe)

    assert _signal_fractions(tmp_path / "g.jsonl") == _signal_fractions(tmp_path / "h.jsonl")
    assert _signal_fractions(tmp_path / "g.jsonl")
