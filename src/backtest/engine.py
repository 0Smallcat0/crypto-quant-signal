"""Daily replay engine reusing the runtime strategy/portfolio/risk/execution path."""

from __future__ import annotations

import math
import statistics
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

from src.accounting import AccountState, VirtualAccountLedger
from src.backtest.types import (
    BacktestError,
    BacktestMetrics,
    BacktestParameters,
    BacktestReport,
    EquityPoint,
    SignalLogEntry,
    TargetLogEntry,
)
from src.domain import (
    Candle,
    OrderIntent,
    OrderSide,
    Position,
    RiskDecisionStatus,
    Symbol,
    VirtualAccountSnapshot,
    VirtualFill,
    VirtualOrder,
)
from src.execution import (
    BrokerAccountView,
    PaperBroker,
    PaperBrokerParameters,
    PaperMarketPrice,
)
from src.features import FeatureSnapshot, build_daily_trend_snapshots
from src.portfolio import LadderPortfolioParameters, build_ladder_targets
from src.risk import (
    EXCHANGE_MIN_NOTIONAL_NOT_MET,
    MIN_NOTIONAL_NOT_MET,
    RiskEvent,
    RiskExchangeFilters,
    RiskGateContext,
    RiskGateParameters,
    RiskState,
    detect_single_day_disaster,
    evaluate_order_intent,
)
from src.strategies import (
    ConfirmationState,
    DailyTrendEnsembleDecision,
    evaluate_confirmed_trend_ensemble,
    evaluate_daily_trend_ensemble,
)

_BPS = Decimal("10000")
_DAYS_PER_YEAR = 365
ZERO_QUANTITY_AFTER_ROUNDING = "ZERO_QUANTITY_AFTER_ROUNDING"

# Hard rejections that would repeat identically every day if retried; the
# executed fraction is marked as reached so the (recorded) rejection stays a
# single auditable event instead of daily spam.
_NON_RETRIABLE_REJECTION_CODES = frozenset(
    {MIN_NOTIONAL_NOT_MET, EXCHANGE_MIN_NOTIONAL_NOT_MET, ZERO_QUANTITY_AFTER_ROUNDING}
)


def run_backtest(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    *,
    parameters: BacktestParameters,
) -> BacktestReport:
    """Replay daily candles through the full decision-to-accounting path."""

    if parameters.strategy_name == "cross_sectional_momentum":
        return _run_cross_sectional_backtest(candles_by_symbol, parameters=parameters)
    _require_symbols_match_budgets(candles_by_symbol, parameters)
    snapshots_by_symbol = {
        symbol_value: build_daily_trend_snapshots(candles)
        for symbol_value, candles in candles_by_symbol.items()
    }
    decision_times = _aligned_decision_times(snapshots_by_symbol)
    if not decision_times:
        msg = "no decision days after the warmup floor; provide more history"
        raise BacktestError(msg)

    candle_lookup = {
        symbol_value: {candle.close_time: index for index, candle in enumerate(candles)}
        for symbol_value, candles in candles_by_symbol.items()
    }
    symbols = {
        symbol_value: candles[0].symbol for symbol_value, candles in candles_by_symbol.items()
    }
    snapshot_lookup = {
        symbol_value: {snapshot.as_of: snapshot for snapshot in snapshots}
        for symbol_value, snapshots in snapshots_by_symbol.items()
    }

    first_decision_time = decision_times[0]
    ledger = VirtualAccountLedger.open(
        account_id=parameters.account_id,
        initial_cash=parameters.initial_cash,
        opened_at=first_decision_time,
    )
    broker = PaperBroker(
        PaperBrokerParameters(
            fee_bps=parameters.effective_fee_bps,
            slippage_bps=parameters.effective_slippage_bps,
            quantity_step=parameters.quantity_step,
            price_tick=parameters.price_tick,
            min_notional=parameters.min_notional_usdt,
        )
    )
    gate_parameters = RiskGateParameters(
        min_notional_usdt=parameters.min_notional_usdt,
        stale_data_max_age_seconds=parameters.stale_data_max_age_seconds,
        max_drawdown_fraction=parameters.max_drawdown_fraction,
        daily_loss_pause_fraction=parameters.daily_loss_pause_fraction,
    )
    ladder_parameters = LadderPortfolioParameters(risk_budgets=parameters.risk_budgets)

    previous_decision_fraction: dict[str, Decimal] = dict.fromkeys(symbols, Decimal("0"))
    executed_fraction: dict[str, Decimal] = dict.fromkeys(symbols, Decimal("0"))
    signals: list[SignalLogEntry] = []
    targets: list[TargetLogEntry] = []
    risk_rejections: list[tuple[str, datetime, tuple[str, ...]]] = []
    risk_events: list[RiskEvent] = []
    equity_curve: list[EquityPoint] = []
    order_sequence = 0
    start_of_day_equity = parameters.initial_cash
    benchmark_open_prices: dict[str, Decimal] | None = None

    confirmation_states: dict[str, ConfirmationState] = {}
    vol_scaler_cache: dict[str, tuple[tuple[int, int], Decimal]] = {}
    for decision_time in decision_times:
        decisions: dict[str, DailyTrendEnsembleDecision | _SizedDecision] = {}
        for symbol_value in sorted(symbols):
            snapshot = snapshot_lookup[symbol_value][decision_time]
            if parameters.strategy_name == "confirmed_trend_ensemble":
                decision, confirmation_states[symbol_value] = evaluate_confirmed_trend_ensemble(
                    snapshot,
                    previous_fraction=previous_decision_fraction[symbol_value],
                    state=confirmation_states.get(symbol_value),
                    confirm_days=parameters.confirm_days,
                )
            else:
                decision = evaluate_daily_trend_ensemble(
                    snapshot,
                    previous_fraction=previous_decision_fraction[symbol_value],
                )
            decisions[symbol_value] = decision
            previous_decision_fraction[symbol_value] = decision.exposure_fraction
            signals.append(
                SignalLogEntry(
                    symbol=symbol_value,
                    as_of=decision.generated_at_bar_close,
                    exposure_fraction=decision.exposure_fraction,
                    reason_codes=decision.reason_codes,
                )
            )
            risk_event = _disaster_event_for(
                candles_by_symbol[symbol_value],
                candle_lookup[symbol_value][decision_time],
                symbols[symbol_value],
                parameters.disaster_single_day_drop_fraction,
            )
            if risk_event is not None:
                risk_events.append(risk_event)

        if parameters.vol_target_annualized is not None:
            decisions = _apply_vol_overlay(
                decisions,
                parameters=parameters,
                candles_by_symbol=candles_by_symbol,
                candle_lookup=candle_lookup,
                decision_time=decision_time,
                scaler_cache=vol_scaler_cache,
            )

        target_set = build_ladder_targets(
            tuple(decisions[symbol_value] for symbol_value in sorted(symbols)),
            parameters=ladder_parameters,
        )
        targets.append(
            TargetLogEntry(
                as_of=decision_time,
                target_weights=tuple(
                    (target.symbol.value, target.target_weight) for target in target_set.targets
                ),
                cash_weight=target_set.cash_weight,
                reason_codes=target_set.reason_codes,
            )
        )

        execution_candles = _execution_candles(candles_by_symbol, candle_lookup, decision_time)
        if execution_candles is None:
            # Final decision day: signal recorded, nothing left to execute on.
            continue

        open_prices = {
            symbol_value: candle.open_price for symbol_value, candle in execution_candles.items()
        }
        if benchmark_open_prices is None:
            benchmark_open_prices = dict(open_prices)
        execution_time = next(iter(execution_candles.values())).open_time
        equity_at_open = _equity_at(ledger, open_prices)

        ordered_symbols = sorted(
            symbols,
            key=lambda value: (
                decisions[value].exposure_fraction >= executed_fraction[value],
                value,
            ),
        )
        for symbol_value in ordered_symbols:
            sized_decision = decisions[symbol_value]
            desired_fraction = sized_decision.exposure_fraction
            if desired_fraction == executed_fraction[symbol_value]:
                continue
            order_sequence += 1
            outcome = _execute_ladder_change(
                ledger=ledger,
                broker=broker,
                gate_parameters=gate_parameters,
                parameters=parameters,
                symbol=symbols[symbol_value],
                decision=sized_decision,
                desired_fraction=desired_fraction,
                current_fraction=executed_fraction[symbol_value],
                budget=parameters.risk_budgets[symbol_value],
                equity_at_open=equity_at_open,
                open_prices=open_prices,
                symbols=symbols,
                execution_time=execution_time,
                order_id=f"bt-{order_sequence:06d}-{symbol_value}",
                start_of_day_equity=start_of_day_equity,
            )
            if outcome.achieved is not None:
                executed_fraction[symbol_value] = outcome.achieved
            else:
                if not outcome.broker_recorded:
                    # Broker rejections already live in broker.rejected_orders;
                    # recording them here too would double-count the metric.
                    risk_rejections.append((symbol_value, execution_time, outcome.reason_codes))
                if _NON_RETRIABLE_REJECTION_CODES.intersection(outcome.reason_codes):
                    executed_fraction[symbol_value] = desired_fraction

        close_prices = {
            symbol_value: candle.close_price for symbol_value, candle in execution_candles.items()
        }
        close_time = next(iter(execution_candles.values())).close_time
        close_snapshot = ledger.snapshot(
            mark_prices=_mark_prices(close_prices, symbols),
            captured_at=close_time,
        )
        benchmark_equity = _benchmark_equity(parameters, benchmark_open_prices, close_prices)
        equity_curve.append(
            EquityPoint(
                close_time=close_time,
                equity=close_snapshot.equity,
                drawdown=ledger.state.drawdown,
                benchmark_equity=benchmark_equity,
            )
        )
        start_of_day_equity = close_snapshot.equity

    metrics = _metrics(
        equity_curve,
        parameters=parameters,
        fills=broker.fills,
        rejected_count=len(broker.rejected_orders) + len(risk_rejections),
    )
    return BacktestReport(
        data_start=decision_times[0],
        data_end=decision_times[-1],
        decision_days=len(decision_times),
        signals=tuple(signals),
        targets=tuple(targets),
        accepted_orders=broker.accepted_orders,
        fills=broker.fills,
        rejected_orders=broker.rejected_orders,
        risk_rejections=tuple(risk_rejections),
        risk_events=tuple(risk_events),
        equity_curve=tuple(equity_curve),
        metrics=metrics,
        cost_assumptions={
            "fee_bps": str(parameters.effective_fee_bps),
            "slippage_bps": str(parameters.effective_slippage_bps),
            "cost_multiplier": str(parameters.cost_multiplier),
            "fill_rule": "next_bar_open",
        },
    )


@dataclass(frozen=True, slots=True)
class _LadderOutcome:
    """Result of one ladder-change attempt: achieved fraction or rejection."""

    achieved: Decimal | None
    reason_codes: tuple[str, ...] = ()
    broker_recorded: bool = False


def _execute_ladder_change(
    *,
    ledger: VirtualAccountLedger,
    broker: PaperBroker,
    gate_parameters: RiskGateParameters,
    parameters: BacktestParameters,
    symbol: Symbol,
    decision: DailyTrendEnsembleDecision | _SizedDecision,
    desired_fraction: Decimal,
    current_fraction: Decimal,
    budget: Decimal,
    equity_at_open: Decimal,
    open_prices: Mapping[str, Decimal],
    symbols: Mapping[str, Symbol],
    execution_time: datetime,
    order_id: str,
    start_of_day_equity: Decimal,
) -> _LadderOutcome:
    """Build, gate, and execute one ladder-change order."""

    reference_price = open_prices[symbol.value]
    state = ledger.state
    current_position = _domain_position(state, symbol)
    delta_fraction = desired_fraction - current_fraction
    # The ladder step's cash claim; costs live INSIDE it so simultaneous
    # full-budget buys cannot starve whichever symbol trades last.
    intended_notional = abs(delta_fraction) * budget * equity_at_open

    if delta_fraction < Decimal("0"):
        side = OrderSide.SELL
        held_quantity = current_position.quantity if current_position is not None else Decimal("0")
        if desired_fraction == Decimal("0"):
            quantity = held_quantity
        else:
            quantity = min(
                _round_down(intended_notional / reference_price, parameters.quantity_step),
                held_quantity,
            )
    else:
        side = OrderSide.BUY
        # Mirror the broker's cost math exactly (slippage then tick round-up,
        # fee on the gross fill notional) so an affordable-sized buy can never
        # bounce off the broker's cash check by a rounding hair.
        fee_rate = parameters.effective_fee_bps / _BPS
        cost_rate = (
            Decimal("1") + (parameters.effective_fee_bps + parameters.effective_slippage_bps) / _BPS
        )
        estimated_fill_price = _round_up(
            reference_price * (Decimal("1") + parameters.effective_slippage_bps / _BPS),
            parameters.price_tick,
        )
        target_quantity = _round_down(
            intended_notional / cost_rate / reference_price, parameters.quantity_step
        )
        affordable_quantity = _round_down(
            state.cash / (estimated_fill_price * (Decimal("1") + fee_rate)),
            parameters.quantity_step,
        )
        quantity = min(target_quantity, affordable_quantity)

    if quantity <= Decimal("0"):
        ledger.record_rejected_order(
            order_id=None,
            symbol=symbol,
            occurred_at=execution_time,
            reason_codes=(ZERO_QUANTITY_AFTER_ROUNDING,),
        )
        return _LadderOutcome(achieved=None, reason_codes=(ZERO_QUANTITY_AFTER_ROUNDING,))

    intent = OrderIntent(
        symbol=symbol,
        side=side,
        quantity=quantity,
        created_at=execution_time,
    )
    account_snapshot = VirtualAccountSnapshot(
        account_id=state.account_id,
        cash=state.cash,
        equity=equity_at_open,
        positions=_domain_positions(state),
        captured_at=execution_time,
    )
    context = RiskGateContext(
        current_position=current_position,
        account_snapshot=account_snapshot,
        reference_price=reference_price,
        latest_market_data_at=execution_time,
        decision_time=execution_time,
        earliest_execution_time=decision.executable_from_next_bar,
        exchange_filters=RiskExchangeFilters(
            symbol=symbol,
            status="TRADING",
            is_spot_trading_allowed=True,
            price_tick_size=parameters.price_tick,
            quantity_step_size=parameters.quantity_step,
            min_quantity=parameters.quantity_step,
            min_notional=parameters.min_notional_usdt,
        ),
        risk_state=RiskState(
            peak_equity=ledger.state.peak_equity,
            start_of_day_equity=start_of_day_equity,
        ),
    )
    risk_decision = evaluate_order_intent(intent, context=context, parameters=gate_parameters)
    if risk_decision.status is not RiskDecisionStatus.APPROVED:
        ledger.record_rejected_order(
            order_id=order_id,
            symbol=symbol,
            occurred_at=execution_time,
            reason_codes=risk_decision.reason_codes,
        )
        return _LadderOutcome(achieved=None, reason_codes=risk_decision.reason_codes)

    order = VirtualOrder(
        order_id=order_id,
        intent=intent,
        risk_decision=risk_decision,
        approved_at=execution_time,
    )
    result = broker.submit_order(
        order,
        market_price=PaperMarketPrice(
            symbol=symbol, price=reference_price, observed_at=execution_time
        ),
        account_view=BrokerAccountView(cash=state.cash, positions=_domain_positions(state)),
        submitted_at=execution_time,
    )
    if result.fill is None:
        rejected = result.rejected_order
        reason_codes = rejected.reason_codes if rejected is not None else ("BROKER_REJECTED",)
        ledger.record_rejected_order(
            order_id=order_id,
            symbol=symbol,
            occurred_at=execution_time,
            reason_codes=reason_codes,
        )
        return _LadderOutcome(achieved=None, reason_codes=reason_codes, broker_recorded=True)

    ledger.apply_fill(result.fill, mark_prices=_mark_prices(open_prices, symbols))
    # A cash-capped fill must not masquerade as the full ladder step: track
    # the fraction actually achieved so the shortfall retries next cycle.
    actual_cost = result.fill.quantity * result.fill.price + result.fill.fee
    if intended_notional > Decimal("0") and actual_cost < intended_notional * Decimal("0.99"):
        achieved = current_fraction + delta_fraction * actual_cost / intended_notional
    else:
        achieved = desired_fraction
    return _LadderOutcome(achieved=achieved)


def _require_symbols_match_budgets(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    parameters: BacktestParameters,
) -> None:
    candle_symbols = set(candles_by_symbol)
    budget_symbols = set(parameters.risk_budgets)
    if candle_symbols != budget_symbols:
        msg = (
            "candles must cover exactly the budgeted decision universe; "
            f"candles={sorted(candle_symbols)} budgets={sorted(budget_symbols)}"
        )
        raise BacktestError(msg)


def _aligned_decision_times(
    snapshots_by_symbol: Mapping[str, tuple[FeatureSnapshot, ...]],
) -> tuple[datetime, ...]:
    time_sets = {
        symbol_value: {snapshot.as_of for snapshot in snapshots}
        for symbol_value, snapshots in snapshots_by_symbol.items()
    }
    reference: set[datetime] | None = None
    for symbol_value, times in time_sets.items():
        if reference is None:
            reference = times
            continue
        if times != reference:
            missing = sorted(reference.symmetric_difference(times))[:5]
            msg = (
                "decision days must align across all budgeted symbols; "
                f"first mismatches near {symbol_value}: "
                f"{[value.isoformat() for value in missing]}"
            )
            raise BacktestError(msg)
    return tuple(sorted(reference or ()))


@dataclass(frozen=True, slots=True)
class _SizedDecision:
    """Vol-overlay-sized view of a ladder decision.

    The strategy contract pins DailyTrendEnsembleDecision to the five ladder
    rungs; the overlay is a position-size modifier, so its output is
    deliberately a DIFFERENT type carrying only what the target builder and
    execution path consume. The rung-typed decision never leaves the grid.
    """

    symbol: Symbol
    exposure_fraction: Decimal
    reason_codes: tuple[str, ...]
    executable_from_next_bar: datetime


def _apply_vol_overlay(
    decisions: dict[str, DailyTrendEnsembleDecision | _SizedDecision],
    *,
    parameters: BacktestParameters,
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    candle_lookup: Mapping[str, Mapping[datetime, int]],
    decision_time: datetime,
    scaler_cache: dict[str, tuple[tuple[int, int], Decimal]],
) -> dict[str, DailyTrendEnsembleDecision | _SizedDecision]:
    """Experiment-2 sizing overlay: scale ladder fractions toward a vol target.

    Uses only closes up to and including the decision close (no lookahead).
    Monthly rebalance freezes each symbol's scaler at its first decision day
    of the calendar month; daily recomputes every decision. The ladder state
    carried into tomorrow's strategy call keeps the RAW fraction — the
    overlay resizes positions, it never rewrites the signal.
    """

    target = parameters.vol_target_annualized
    if target is None:  # pragma: no cover - guarded by the caller
        return decisions
    sized: dict[str, DailyTrendEnsembleDecision | _SizedDecision] = {}
    month_key = (decision_time.year, decision_time.month)
    for symbol_value, decision in decisions.items():
        if parameters.vol_rebalance == "monthly":
            cached = scaler_cache.get(symbol_value)
            if cached is not None and cached[0] == month_key:
                scaler = cached[1]
            else:
                scaler = _vol_scaler(
                    candles_by_symbol[symbol_value],
                    candle_lookup[symbol_value][decision_time],
                    vol_window=parameters.vol_window_days,
                    target=target,
                )
                scaler_cache[symbol_value] = (month_key, scaler)
        else:
            scaler = _vol_scaler(
                candles_by_symbol[symbol_value],
                candle_lookup[symbol_value][decision_time],
                vol_window=parameters.vol_window_days,
                target=target,
            )
        if scaler >= Decimal("1"):
            sized[symbol_value] = decision
            continue
        sized[symbol_value] = _SizedDecision(
            symbol=decision.symbol,
            exposure_fraction=decision.exposure_fraction * scaler,
            reason_codes=(*decision.reason_codes, f"VOL_SCALED_{scaler}"),
            executable_from_next_bar=decision.executable_from_next_bar,
        )
    return sized


def _vol_scaler(
    candles: tuple[Candle, ...],
    end_index: int,
    *,
    vol_window: int,
    target: Decimal,
) -> Decimal:
    """min(1, target / realized annualized vol) over closes ending at the decision.

    Warmup (fewer than vol_window prior closes) and degenerate series return 1
    — no scaling rather than a guessed one.
    """

    start = end_index - vol_window
    if start < 0:
        return Decimal("1")
    closes = [candles[index].close_price for index in range(start, end_index + 1)]
    returns = [
        math.log(float(closes[index + 1]) / float(closes[index]))
        for index in range(len(closes) - 1)
        if closes[index] > 0 and closes[index + 1] > 0
    ]
    if len(returns) < 2:
        return Decimal("1")
    realized = statistics.stdev(returns) * math.sqrt(365.0)
    if realized <= 0.0:
        return Decimal("1")
    return Decimal(str(round(min(1.0, float(target) / realized), 6)))


def _run_cross_sectional_backtest(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    *,
    parameters: BacktestParameters,
) -> BacktestReport:
    """Cross-sectional momentum: rank on trailing lookback, hold top-K equal weight.

    Pre-registered in docs/research/GOALP_EXPERIMENT3_PREREGISTRATION.md.
    Universe symbols may have staggered listings; the pre-registration
    explicitly allows the ranking pool to shrink below the full universe on
    early days, so this path uses the UNION of candle dates rather than the
    intersection required by the ladder engine. Signals log every symbol on
    every decision day (target weight + reason codes) so the audit trail is
    identical in shape to the ladder path.
    """

    _require_symbols_match_budgets(candles_by_symbol, parameters)
    symbols = {
        symbol_value: candles[0].symbol for symbol_value, candles in candles_by_symbol.items()
    }
    candle_lookup: dict[str, dict[datetime, int]] = {
        symbol_value: {candle.close_time: index for index, candle in enumerate(candles)}
        for symbol_value, candles in candles_by_symbol.items()
    }

    all_close_times = sorted(
        {candle.close_time for candles in candles_by_symbol.values() for candle in candles}
    )
    if not all_close_times:
        msg = "no candles provided"
        raise BacktestError(msg)

    lookback = parameters.cs_lookback_days

    def _has_lookback(symbol_value: str, close_time: datetime) -> bool:
        index = candle_lookup[symbol_value].get(close_time)
        return index is not None and index >= lookback

    decision_floor: date | None = (
        date.fromisoformat(parameters.cs_decision_start)
        if parameters.cs_decision_start is not None
        else None
    )
    decision_times = tuple(
        close_time
        for close_time in all_close_times
        if (decision_floor is None or close_time.date() >= decision_floor)
        and any(_has_lookback(symbol_value, close_time) for symbol_value in symbols)
    )
    if not decision_times:
        msg = "no cross-sectional decision days after the lookback floor; provide more history"
        raise BacktestError(msg)

    first_decision_time = decision_times[0]
    ledger = VirtualAccountLedger.open(
        account_id=parameters.account_id,
        initial_cash=parameters.initial_cash,
        opened_at=first_decision_time,
    )
    broker = PaperBroker(
        PaperBrokerParameters(
            fee_bps=parameters.effective_fee_bps,
            slippage_bps=parameters.effective_slippage_bps,
            quantity_step=parameters.quantity_step,
            price_tick=parameters.price_tick,
            min_notional=parameters.min_notional_usdt,
        )
    )
    gate_parameters = RiskGateParameters(
        min_notional_usdt=parameters.min_notional_usdt,
        stale_data_max_age_seconds=parameters.stale_data_max_age_seconds,
        max_drawdown_fraction=parameters.max_drawdown_fraction,
        daily_loss_pause_fraction=parameters.daily_loss_pause_fraction,
    )

    target_weights: dict[str, Decimal] = dict.fromkeys(symbols, Decimal("0"))
    executed_fraction: dict[str, Decimal] = dict.fromkeys(symbols, Decimal("0"))
    signals: list[SignalLogEntry] = []
    targets: list[TargetLogEntry] = []
    risk_rejections: list[tuple[str, datetime, tuple[str, ...]]] = []
    risk_events: list[RiskEvent] = []
    equity_curve: list[EquityPoint] = []
    order_sequence = 0
    start_of_day_equity = parameters.initial_cash
    # Benchmark = equal-weight buy-and-hold anchored per-symbol on first
    # executable open; late-listed symbols contribute cash until they anchor,
    # so the benchmark starts at initial_cash and grows only as the universe
    # actually comes online.
    benchmark_anchor: dict[str, Decimal] = {}
    last_close_by_symbol: dict[str, Decimal] = {}
    last_rebalance_key: object | None = None

    for decision_time in decision_times:
        for symbol_value, lookup in candle_lookup.items():
            index = lookup.get(decision_time)
            if index is not None:
                last_close_by_symbol[symbol_value] = candles_by_symbol[symbol_value][
                    index
                ].close_price

        cadence_key = _cs_cadence_key(decision_time, parameters.cs_rebalance_cadence)
        is_rebalance = cadence_key != last_rebalance_key

        if is_rebalance:
            pool_returns: dict[str, Decimal] = {}
            for symbol_value in sorted(symbols):
                index = candle_lookup[symbol_value].get(decision_time)
                if index is None or index < lookback:
                    continue
                start_close = candles_by_symbol[symbol_value][index - lookback].close_price
                end_close = candles_by_symbol[symbol_value][index].close_price
                if start_close <= Decimal("0"):
                    continue
                pool_returns[symbol_value] = end_close / start_close - Decimal("1")

            new_weights: dict[str, Decimal] = dict.fromkeys(symbols, Decimal("0"))
            if len(pool_returns) < parameters.cs_min_pool_size:
                reason_codes: tuple[str, ...] = (
                    "CS_REBALANCE",
                    f"POOL_TOO_SMALL_{len(pool_returns)}_LT_{parameters.cs_min_pool_size}",
                )
            else:
                ranked = sorted(pool_returns.items(), key=lambda pair: (-pair[1], pair[0]))
                top = ranked[: parameters.cs_top_k]
                selected: list[str] = []
                for symbol_value, momentum in top:
                    if parameters.cs_absolute_filter and momentum <= Decimal("0"):
                        continue
                    selected.append(symbol_value)
                per_slot = Decimal("1") / Decimal(parameters.cs_top_k)
                for symbol_value in selected:
                    new_weights[symbol_value] = per_slot
                reason_codes = (
                    "CS_REBALANCE",
                    f"POOL_{len(pool_returns)}",
                    f"SELECTED_{len(selected)}",
                )
            target_weights = new_weights
            last_rebalance_key = cadence_key
        else:
            reason_codes = ("CS_HOLD",)

        for symbol_value in sorted(symbols):
            signals.append(
                SignalLogEntry(
                    symbol=symbol_value,
                    as_of=decision_time,
                    exposure_fraction=target_weights[symbol_value],
                    reason_codes=reason_codes,
                )
            )

        active_weights = tuple(
            (symbol_value, target_weights[symbol_value])
            for symbol_value in sorted(symbols)
            if target_weights[symbol_value] > Decimal("0")
        )
        gross = sum((weight for _, weight in active_weights), Decimal("0"))
        targets.append(
            TargetLogEntry(
                as_of=decision_time,
                target_weights=active_weights,
                cash_weight=Decimal("1") - gross,
                reason_codes=reason_codes,
            )
        )

        for symbol_value in sorted(symbols):
            index = candle_lookup[symbol_value].get(decision_time)
            if index is None:
                continue
            event = _disaster_event_for(
                candles_by_symbol[symbol_value],
                index,
                symbols[symbol_value],
                parameters.disaster_single_day_drop_fraction,
            )
            if event is not None:
                risk_events.append(event)

        if is_rebalance:
            execution_candles: dict[str, Candle] = {}
            for symbol_value in sorted(symbols):
                index = candle_lookup[symbol_value].get(decision_time)
                if index is None:
                    continue
                next_index = index + 1
                if next_index < len(candles_by_symbol[symbol_value]):
                    execution_candles[symbol_value] = candles_by_symbol[symbol_value][next_index]

            if execution_candles:
                open_prices: dict[str, Decimal] = {
                    symbol_value: candle.open_price
                    for symbol_value, candle in execution_candles.items()
                }
                for symbol_value, price in open_prices.items():
                    benchmark_anchor.setdefault(symbol_value, price)
                # Pad with last-known close for any symbol we hold that lacks
                # today's open — ledger.apply_fill demands a mark for every
                # held position and can't tolerate a gap.
                padded_open_prices = dict(open_prices)
                for symbol_value in symbols:
                    if (
                        symbol_value not in padded_open_prices
                        and symbol_value in last_close_by_symbol
                    ):
                        padded_open_prices[symbol_value] = last_close_by_symbol[symbol_value]
                execution_time = next(iter(execution_candles.values())).open_time
                equity_at_open = _cs_equity_at_marked(ledger, padded_open_prices, symbols)

                ordered_symbols = sorted(
                    execution_candles,
                    key=lambda value: (
                        target_weights[value] >= executed_fraction[value],
                        value,
                    ),
                )
                for symbol_value in ordered_symbols:
                    desired_fraction = target_weights[symbol_value]
                    if desired_fraction == executed_fraction[symbol_value]:
                        continue
                    order_sequence += 1
                    sized = _SizedDecision(
                        symbol=symbols[symbol_value],
                        exposure_fraction=desired_fraction,
                        reason_codes=reason_codes,
                        executable_from_next_bar=execution_time,
                    )
                    outcome = _execute_ladder_change(
                        ledger=ledger,
                        broker=broker,
                        gate_parameters=gate_parameters,
                        parameters=parameters,
                        symbol=symbols[symbol_value],
                        decision=sized,
                        desired_fraction=desired_fraction,
                        current_fraction=executed_fraction[symbol_value],
                        budget=Decimal("1"),
                        equity_at_open=equity_at_open,
                        open_prices=padded_open_prices,
                        symbols=symbols,
                        execution_time=execution_time,
                        order_id=f"cs-{order_sequence:06d}-{symbol_value}",
                        start_of_day_equity=start_of_day_equity,
                    )
                    if outcome.achieved is not None:
                        executed_fraction[symbol_value] = outcome.achieved
                    else:
                        if not outcome.broker_recorded:
                            risk_rejections.append(
                                (symbol_value, execution_time, outcome.reason_codes)
                            )
                        if _NON_RETRIABLE_REJECTION_CODES.intersection(outcome.reason_codes):
                            executed_fraction[symbol_value] = desired_fraction

        close_marks = {
            symbols[symbol_value]: price for symbol_value, price in last_close_by_symbol.items()
        }
        close_snapshot = ledger.snapshot(mark_prices=close_marks, captured_at=decision_time)
        benchmark_equity = _cs_benchmark_equity(parameters, benchmark_anchor, last_close_by_symbol)
        equity_curve.append(
            EquityPoint(
                close_time=decision_time,
                equity=close_snapshot.equity,
                drawdown=ledger.state.drawdown,
                benchmark_equity=benchmark_equity,
            )
        )
        start_of_day_equity = close_snapshot.equity

    metrics = _metrics(
        equity_curve,
        parameters=parameters,
        fills=broker.fills,
        rejected_count=len(broker.rejected_orders) + len(risk_rejections),
    )
    return BacktestReport(
        data_start=decision_times[0],
        data_end=decision_times[-1],
        decision_days=len(decision_times),
        signals=tuple(signals),
        targets=tuple(targets),
        accepted_orders=broker.accepted_orders,
        fills=broker.fills,
        rejected_orders=broker.rejected_orders,
        risk_rejections=tuple(risk_rejections),
        risk_events=tuple(risk_events),
        equity_curve=tuple(equity_curve),
        metrics=metrics,
        cost_assumptions={
            "fee_bps": str(parameters.effective_fee_bps),
            "slippage_bps": str(parameters.effective_slippage_bps),
            "cost_multiplier": str(parameters.cost_multiplier),
            "fill_rule": "next_bar_open",
            "cs_top_k": str(parameters.cs_top_k),
            "cs_lookback_days": str(parameters.cs_lookback_days),
            "cs_rebalance_cadence": parameters.cs_rebalance_cadence,
            "cs_absolute_filter": str(parameters.cs_absolute_filter),
            "cs_min_pool_size": str(parameters.cs_min_pool_size),
        },
    )


def _cs_cadence_key(close_time: datetime, cadence: str) -> object:
    """A key that changes when a new rebalance window opens.

    Weekly: ISO year+week; monthly: calendar year+month. The first decision
    always fires because ``last_rebalance_key`` starts as None.
    """

    if cadence == "weekly":
        iso = close_time.isocalendar()
        return ("week", iso.year, iso.week)
    if cadence == "monthly":
        return ("month", close_time.year, close_time.month)
    msg = f"unknown cs_rebalance_cadence: {cadence}"
    raise BacktestError(msg)


def _cs_equity_at_marked(
    ledger: VirtualAccountLedger,
    prices: Mapping[str, Decimal],
    symbols: Mapping[str, Symbol],
) -> Decimal:
    """Sum cash + position marks using a symbol-value-keyed price map."""

    equity = ledger.state.cash
    for position in ledger.state.positions:
        for symbol_value, symbol in symbols.items():
            if symbol == position.symbol:
                equity += position.quantity * prices[symbol_value]
                break
    return equity


def _cs_benchmark_equity(
    parameters: BacktestParameters,
    anchors: Mapping[str, Decimal],
    last_close: Mapping[str, Decimal],
) -> Decimal:
    """Equal-weight buy-and-hold benchmark anchored per-symbol on first entry.

    Weight per universe slot = 1 / universe_size. Symbols not yet anchored
    contribute their slot as cash (no growth), so the benchmark starts at
    ``initial_cash`` and rises as the universe legs come online.
    """

    universe_size = len(parameters.risk_budgets)
    if universe_size == 0 or not anchors:
        return parameters.initial_cash
    slot = Decimal("1") / Decimal(universe_size)
    growth = Decimal("0")
    invested = Decimal("0")
    for symbol_value, anchor in anchors.items():
        end_price = last_close.get(symbol_value)
        if end_price is None or anchor <= Decimal("0"):
            continue
        growth += slot * end_price / anchor
        invested += slot
    cash_share = Decimal("1") - invested
    return parameters.initial_cash * (growth + cash_share)


def _execution_candles(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    candle_lookup: Mapping[str, Mapping[datetime, int]],
    decision_time: datetime,
) -> dict[str, Candle] | None:
    execution_candles: dict[str, Candle] = {}
    for symbol_value, candles in candles_by_symbol.items():
        index = candle_lookup[symbol_value][decision_time]
        next_index = index + 1
        if next_index >= len(candles):
            return None
        execution_candles[symbol_value] = candles[next_index]
    return execution_candles


def _disaster_event_for(
    candles: tuple[Candle, ...],
    close_index: int,
    symbol: Symbol,
    threshold_fraction: Decimal,
) -> RiskEvent | None:
    if close_index == 0:
        return None
    previous = candles[close_index - 1]
    current = candles[close_index]
    return detect_single_day_disaster(
        symbol=symbol,
        previous_close=previous.close_price,
        current_close=current.close_price,
        occurred_at=current.close_time,
        threshold_fraction=threshold_fraction,
    )


def _domain_positions(state: AccountState) -> tuple[Position, ...]:
    return tuple(
        Position(
            symbol=position.symbol,
            quantity=position.quantity,
            average_entry_price=position.average_entry_price,
        )
        for position in state.positions
    )


def _domain_position(state: AccountState, symbol: Symbol) -> Position | None:
    for position in _domain_positions(state):
        if position.symbol == symbol:
            return position
    return None


def _equity_at(ledger: VirtualAccountLedger, prices: Mapping[str, Decimal]) -> Decimal:
    equity = ledger.state.cash
    for position in ledger.state.positions:
        equity += position.quantity * prices[position.symbol.value]
    return equity


def _mark_prices(
    prices: Mapping[str, Decimal], symbols: Mapping[str, Symbol]
) -> dict[Symbol, Decimal]:
    return {symbols[symbol_value]: price for symbol_value, price in prices.items()}


def _benchmark_equity(
    parameters: BacktestParameters,
    benchmark_open_prices: Mapping[str, Decimal],
    close_prices: Mapping[str, Decimal],
) -> Decimal:
    invested_fraction = Decimal("0")
    growth = Decimal("0")
    for symbol_value, budget in parameters.risk_budgets.items():
        invested_fraction += budget
        growth += budget * close_prices[symbol_value] / benchmark_open_prices[symbol_value]
    cash_fraction = Decimal("1") - invested_fraction
    return parameters.initial_cash * (growth + cash_fraction)


def _round_down(value: Decimal, step: Decimal) -> Decimal:
    units = (value / step).to_integral_value(rounding=ROUND_FLOOR)
    return units * step


def _round_up(value: Decimal, step: Decimal) -> Decimal:
    units = (value / step).to_integral_value(rounding=ROUND_CEILING)
    return units * step


def _metrics(
    equity_curve: list[EquityPoint],
    *,
    parameters: BacktestParameters,
    fills: tuple[VirtualFill, ...],
    rejected_count: int,
) -> BacktestMetrics:
    final_equity = equity_curve[-1].equity if equity_curve else parameters.initial_cash
    benchmark_final = equity_curve[-1].benchmark_equity if equity_curve else parameters.initial_cash
    total_return = final_equity / parameters.initial_cash - Decimal("1")

    daily_returns: list[float] = []
    previous_equity = parameters.initial_cash
    for point in equity_curve:
        if previous_equity > Decimal("0"):
            daily_returns.append(float(point.equity / previous_equity) - 1.0)
        previous_equity = point.equity

    annualized_sharpe = Decimal("0")
    if len(daily_returns) >= 2:
        mean_return = statistics.fmean(daily_returns)
        stdev_return = statistics.stdev(daily_returns)
        if stdev_return > 0.0:
            annualized_sharpe = Decimal(
                str(round(mean_return / stdev_return * math.sqrt(_DAYS_PER_YEAR), 6))
            )

    max_drawdown = Decimal("0")
    peak = parameters.initial_cash
    for point in equity_curve:
        peak = max(peak, point.equity)
        if peak > Decimal("0"):
            max_drawdown = max(max_drawdown, (peak - point.equity) / peak)

    total_fees = Decimal("0")
    total_slippage = Decimal("0")
    total_traded_notional = Decimal("0")
    for fill in fills:
        total_fees += fill.fee
        total_slippage += fill.slippage
        total_traded_notional += fill.quantity * fill.price

    annualized_turnover = Decimal("0")
    if equity_curve:
        mean_equity = sum((point.equity for point in equity_curve), Decimal("0")) / Decimal(
            len(equity_curve)
        )
        years = Decimal(len(equity_curve)) / Decimal(_DAYS_PER_YEAR)
        if mean_equity > Decimal("0") and years > Decimal("0"):
            annualized_turnover = total_traded_notional / mean_equity / years

    return BacktestMetrics(
        final_equity=final_equity,
        total_return_fraction=total_return,
        annualized_sharpe=annualized_sharpe,
        max_drawdown_fraction=max_drawdown,
        trade_count=len(fills),
        rejected_count=rejected_count,
        total_fees=total_fees,
        total_slippage=total_slippage,
        total_traded_notional=total_traded_notional,
        annualized_turnover=annualized_turnover,
        benchmark_final_equity=benchmark_final,
        observation_days=len(equity_curve),
    )
