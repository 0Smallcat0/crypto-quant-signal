from __future__ import annotations

from dataclasses import fields
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Signal, Symbol
from src.portfolio import (
    PortfolioTarget,
    PortfolioTargetParameters,
    PortfolioValidationError,
    build_portfolio_targets,
)
from src.strategies import StrategyDecision


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _decision(
    value: str,
    base_asset: str,
    score: str,
    *,
    signal: Signal = Signal.LONG,
) -> StrategyDecision:
    generated_at = datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)
    return StrategyDecision(
        symbol=_symbol(value, base_asset),
        signal=signal,
        score=Decimal(score),
        reason_codes=("TEST_STRATEGY_REASON",),
        generated_at_bar_close=generated_at,
        executable_from_next_bar=generated_at + timedelta(milliseconds=1),
    )


def test_ranked_long_decisions_become_capped_target_weights() -> None:
    targets = build_portfolio_targets(
        (
            _decision("DOGEUSDT", "DOGE", "0.99", signal=Signal.FLAT),
            _decision("BTCUSDT", "BTC", "0.70"),
            _decision("ETHUSDT", "ETH", "0.95"),
            _decision("SOLUSDT", "SOL", "0.80"),
            _decision("ADAUSDT", "ADA", "0.60"),
        )
    )

    assert [
        (target.symbol.value, target.target_weight, target.source_score)
        for target in targets.targets
    ] == [
        ("ETHUSDT", Decimal("0.35"), Decimal("0.95")),
        ("SOLUSDT", Decimal("0.35"), Decimal("0.80")),
        ("BTCUSDT", Decimal("0.30"), Decimal("0.70")),
    ]
    assert targets.gross_target_weight == Decimal("1.00")
    assert targets.cash_weight == Decimal("0.00")
    assert "TARGETS_BUILT" in targets.reason_codes


def test_single_long_candidate_keeps_cash_instead_of_forcing_full_exposure() -> None:
    targets = build_portfolio_targets(
        (
            _decision("ETHUSDT", "ETH", "0.90"),
            _decision("SOLUSDT", "SOL", "0.20", signal=Signal.FLAT),
        )
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("ETHUSDT", Decimal("0.35")),
    ]
    assert targets.gross_target_weight == Decimal("0.35")
    assert targets.cash_weight == Decimal("0.65")
    assert "CASH_HELD" in targets.reason_codes


def test_all_flat_decisions_return_cash_only_targets() -> None:
    targets = build_portfolio_targets(
        (
            _decision("BTCUSDT", "BTC", "0.30", signal=Signal.FLAT),
            _decision("ETHUSDT", "ETH", "0.20", signal=Signal.FLAT),
        )
    )

    assert targets.targets == ()
    assert targets.gross_target_weight == Decimal("0")
    assert targets.cash_weight == Decimal("1")
    assert targets.reason_codes == ("NO_LONG_CANDIDATES", "CASH_HELD")


def test_custom_target_parameters_limit_active_positions_and_gross_exposure() -> None:
    targets = build_portfolio_targets(
        (
            _decision("BTCUSDT", "BTC", "0.90"),
            _decision("ETHUSDT", "ETH", "0.80"),
            _decision("SOLUSDT", "SOL", "0.70"),
        ),
        parameters=PortfolioTargetParameters(
            max_active_positions=2,
            max_symbol_weight=Decimal("0.20"),
            max_gross_exposure=Decimal("0.50"),
        ),
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("BTCUSDT", Decimal("0.20")),
        ("ETHUSDT", Decimal("0.20")),
    ]
    assert targets.gross_target_weight == Decimal("0.40")
    assert targets.cash_weight == Decimal("0.60")


def test_gross_exposure_can_truncate_the_last_selected_target() -> None:
    targets = build_portfolio_targets(
        (
            _decision("BTCUSDT", "BTC", "0.90"),
            _decision("ETHUSDT", "ETH", "0.80"),
            _decision("SOLUSDT", "SOL", "0.70"),
        ),
        parameters=PortfolioTargetParameters(max_gross_exposure=Decimal("0.50")),
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("BTCUSDT", Decimal("0.35")),
        ("ETHUSDT", Decimal("0.15")),
    ]
    assert targets.gross_target_weight == Decimal("0.50")
    assert targets.cash_weight == Decimal("0.50")


def test_duplicate_strategy_decisions_for_same_symbol_are_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="duplicate strategy decision symbol"):
        build_portfolio_targets(
            (
                _decision("BTCUSDT", "BTC", "0.90"),
                _decision("BTCUSDT", "BTC", "0.80"),
            )
        )


def test_cooldown_retains_previous_long_target_to_reduce_churn() -> None:
    previous_sol = PortfolioTarget(
        symbol=_symbol("SOLUSDT", "SOL"),
        target_weight=Decimal("0.35"),
        source_score=Decimal("0.70"),
        reason_codes=("PREVIOUS_TARGET",),
    )

    targets = build_portfolio_targets(
        (
            _decision("BTCUSDT", "BTC", "0.95"),
            _decision("ETHUSDT", "ETH", "0.90"),
            _decision("SOLUSDT", "SOL", "0.70"),
        ),
        parameters=PortfolioTargetParameters(max_active_positions=2),
        previous_targets=(previous_sol,),
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("SOLUSDT", Decimal("0.35")),
        ("BTCUSDT", Decimal("0.35")),
    ]
    assert "COOLDOWN_RETAINED_TARGET" in targets.targets[0].reason_codes


def test_disabled_cooldown_uses_fresh_score_ranking() -> None:
    previous_sol = PortfolioTarget(
        symbol=_symbol("SOLUSDT", "SOL"),
        target_weight=Decimal("0.35"),
        source_score=Decimal("0.70"),
        reason_codes=("PREVIOUS_TARGET",),
    )

    targets = build_portfolio_targets(
        (
            _decision("BTCUSDT", "BTC", "0.95"),
            _decision("ETHUSDT", "ETH", "0.90"),
            _decision("SOLUSDT", "SOL", "0.70"),
        ),
        parameters=PortfolioTargetParameters(max_active_positions=2, cooldown_enabled=False),
        previous_targets=(previous_sol,),
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("BTCUSDT", Decimal("0.35")),
        ("ETHUSDT", Decimal("0.35")),
    ]


def test_portfolio_target_outputs_do_not_create_orders() -> None:
    target_fields = {field.name for field in fields(PortfolioTarget)}

    assert target_fields == {"symbol", "target_weight", "source_score", "reason_codes"}
    assert {"side", "quantity", "order_id"}.isdisjoint(target_fields)


def test_invalid_portfolio_parameters_are_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="max_active_positions"):
        PortfolioTargetParameters(max_active_positions=0)

    with pytest.raises(PortfolioValidationError, match="max_symbol_weight"):
        PortfolioTargetParameters(max_symbol_weight=Decimal("1.01"))

    with pytest.raises(PortfolioValidationError, match="cash_allowed"):
        PortfolioTargetParameters(cash_allowed=False)


def test_negative_target_weight_is_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="target_weight"):
        PortfolioTarget(
            symbol=_symbol("BTCUSDT", "BTC"),
            target_weight=Decimal("-0.01"),
            source_score=Decimal("0.80"),
            reason_codes=("INVALID_TEST_TARGET",),
        )
