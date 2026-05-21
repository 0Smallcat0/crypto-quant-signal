"""Build long-only portfolio targets from strategy decisions."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Protocol, runtime_checkable

from src.domain import Signal, Symbol
from src.portfolio.types import (
    PortfolioTarget,
    PortfolioTargetParameters,
    PortfolioTargetParameterValues,
    PortfolioTargetSet,
    PortfolioValidationError,
)


@runtime_checkable
class StrategyDecisionLike(Protocol):
    """Strategy output fields needed by the portfolio target builder."""

    symbol: Symbol
    signal: Signal
    score: Decimal
    reason_codes: tuple[str, ...]


def build_portfolio_targets(
    decisions: Iterable[StrategyDecisionLike],
    *,
    parameters: PortfolioTargetParameterValues | None = None,
    previous_targets: Iterable[PortfolioTarget] | None = None,
) -> PortfolioTargetSet:
    """Convert ranked strategy decisions into capped long-only target weights."""

    decision_list = tuple(decisions)
    if not decision_list:
        msg = "strategy decisions must not be empty"
        raise PortfolioValidationError(msg)
    if any(not isinstance(decision, StrategyDecisionLike) for decision in decision_list):
        msg = "decisions must contain strategy decision values"
        raise PortfolioValidationError(msg)
    _require_unique_decision_symbols(decision_list)

    target_parameters = _portfolio_target_parameters_from(parameters)
    previous_target_list = _validated_previous_targets(previous_targets)
    long_candidates_by_symbol = {
        decision.symbol.value: decision
        for decision in decision_list
        if decision.signal is Signal.LONG
    }
    if not long_candidates_by_symbol:
        return PortfolioTargetSet(
            targets=(),
            cash_weight=Decimal("1"),
            reason_codes=("NO_LONG_CANDIDATES", "CASH_HELD"),
        )

    ranked_candidates = sorted(
        long_candidates_by_symbol.values(), key=lambda decision: decision.score, reverse=True
    )
    selected_candidates = _select_candidates(
        ranked_candidates=ranked_candidates,
        long_candidates_by_symbol=long_candidates_by_symbol,
        previous_targets=previous_target_list,
        parameters=target_parameters,
    )
    remaining_exposure = target_parameters.max_gross_exposure
    targets: list[PortfolioTarget] = []

    for decision, preferred_weight, selection_reason in selected_candidates:
        if remaining_exposure <= Decimal("0"):
            break
        target_weight = min(preferred_weight, remaining_exposure)
        targets.append(
            PortfolioTarget(
                symbol=decision.symbol,
                target_weight=target_weight,
                source_score=decision.score,
                reason_codes=decision.reason_codes + (selection_reason,),
            )
        )
        remaining_exposure -= target_weight

    gross_target_weight = sum((target.target_weight for target in targets), Decimal("0"))
    cash_weight = Decimal("1") - gross_target_weight
    reason_codes = ["TARGETS_BUILT"]
    if cash_weight > Decimal("0"):
        reason_codes.append("CASH_HELD")

    return PortfolioTargetSet(
        targets=tuple(targets),
        cash_weight=cash_weight,
        reason_codes=tuple(reason_codes),
    )


def _require_unique_decision_symbols(decisions: tuple[StrategyDecisionLike, ...]) -> None:
    seen_symbols: set[str] = set()
    for decision in decisions:
        symbol = decision.symbol.value
        if symbol in seen_symbols:
            msg = f"duplicate strategy decision symbol: {symbol}"
            raise PortfolioValidationError(msg)
        seen_symbols.add(symbol)


def _validated_previous_targets(
    previous_targets: Iterable[PortfolioTarget] | None,
) -> tuple[PortfolioTarget, ...]:
    if previous_targets is None:
        return ()
    target_list = tuple(previous_targets)
    if any(not isinstance(target, PortfolioTarget) for target in target_list):
        msg = "previous_targets must contain PortfolioTarget values"
        raise PortfolioValidationError(msg)

    seen_symbols: set[str] = set()
    for target in target_list:
        symbol = target.symbol.value
        if symbol in seen_symbols:
            msg = f"duplicate previous target symbol: {symbol}"
            raise PortfolioValidationError(msg)
        seen_symbols.add(symbol)
    return target_list


def _portfolio_target_parameters_from(
    parameters: PortfolioTargetParameterValues | None,
) -> PortfolioTargetParameters:
    if parameters is None:
        return PortfolioTargetParameters()
    return PortfolioTargetParameters(
        max_active_positions=parameters.max_active_positions,
        max_symbol_weight=parameters.max_symbol_weight,
        max_gross_exposure=parameters.max_gross_exposure,
        cash_allowed=parameters.cash_allowed,
        cooldown_enabled=parameters.cooldown_enabled,
    )


def _select_candidates(
    *,
    ranked_candidates: list[StrategyDecisionLike],
    long_candidates_by_symbol: dict[str, StrategyDecisionLike],
    previous_targets: tuple[PortfolioTarget, ...],
    parameters: PortfolioTargetParameters,
) -> list[tuple[StrategyDecisionLike, Decimal, str]]:
    selected: list[tuple[StrategyDecisionLike, Decimal, str]] = []
    selected_symbols: set[str] = set()

    if parameters.cooldown_enabled:
        for previous_target in previous_targets:
            decision = long_candidates_by_symbol.get(previous_target.symbol.value)
            if decision is None or previous_target.target_weight <= Decimal("0"):
                continue
            selected.append(
                (
                    decision,
                    min(previous_target.target_weight, parameters.max_symbol_weight),
                    "COOLDOWN_RETAINED_TARGET",
                )
            )
            selected_symbols.add(decision.symbol.value)
            if len(selected) >= parameters.max_active_positions:
                return selected

    for decision in ranked_candidates:
        if decision.symbol.value in selected_symbols:
            continue
        selected.append(
            (
                decision,
                parameters.max_symbol_weight,
                "PORTFOLIO_TARGET_SELECTED",
            )
        )
        selected_symbols.add(decision.symbol.value)
        if len(selected) >= parameters.max_active_positions:
            break

    return selected
