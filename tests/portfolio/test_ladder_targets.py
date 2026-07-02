from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

from src.domain import Symbol
from src.portfolio import (
    LadderPortfolioParameters,
    PortfolioValidationError,
    build_ladder_targets,
)


@dataclass(frozen=True, slots=True)
class _LadderDecision:
    symbol: Symbol
    exposure_fraction: Decimal
    reason_codes: tuple[str, ...]


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _decision(value: str, base_asset: str, fraction: str) -> _LadderDecision:
    return _LadderDecision(
        symbol=_symbol(value, base_asset),
        exposure_fraction=Decimal(fraction),
        reason_codes=("LADDER_TEST",),
    )


def _parameters() -> LadderPortfolioParameters:
    return LadderPortfolioParameters(
        risk_budgets={"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")}
    )


def test_targets_scale_exposure_fraction_by_risk_budget() -> None:
    targets = build_ladder_targets(
        (
            _decision("BTCUSDT", "BTC", "1"),
            _decision("ETHUSDT", "ETH", "0.5"),
        ),
        parameters=_parameters(),
    )

    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("BTCUSDT", Decimal("0.5")),
        ("ETHUSDT", Decimal("0.25")),
    ]
    assert targets.cash_weight == Decimal("0.25")
    assert "TARGETS_BUILT" in targets.reason_codes
    assert "CASH_HELD" in targets.reason_codes


def test_zero_fractions_hold_full_cash() -> None:
    targets = build_ladder_targets(
        (
            _decision("BTCUSDT", "BTC", "0"),
            _decision("ETHUSDT", "ETH", "0"),
        ),
        parameters=_parameters(),
    )

    assert targets.targets == ()
    assert targets.cash_weight == Decimal("1")
    assert "NO_LONG_EXPOSURE" in targets.reason_codes
    assert "CASH_HELD" in targets.reason_codes


def test_full_ladder_never_exceeds_gross_exposure_of_one() -> None:
    targets = build_ladder_targets(
        (
            _decision("BTCUSDT", "BTC", "1"),
            _decision("ETHUSDT", "ETH", "1"),
        ),
        parameters=_parameters(),
    )

    assert targets.gross_target_weight == Decimal("1.0")
    assert targets.cash_weight == Decimal("0.0")


def test_decision_reason_codes_propagate_into_targets() -> None:
    targets = build_ladder_targets(
        (_decision("BTCUSDT", "BTC", "0.25"), _decision("ETHUSDT", "ETH", "0")),
        parameters=_parameters(),
    )

    (btc_target,) = targets.targets
    assert "LADDER_TEST" in btc_target.reason_codes
    assert "LADDER_TARGET_BUILT" in btc_target.reason_codes
    assert btc_target.source_score == Decimal("0.25")


def test_symbol_without_risk_budget_is_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="SOLUSDT"):
        build_ladder_targets(
            (_decision("SOLUSDT", "SOL", "0.5"),),
            parameters=_parameters(),
        )


def test_duplicate_decision_symbols_are_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="duplicate"):
        build_ladder_targets(
            (
                _decision("BTCUSDT", "BTC", "0.5"),
                _decision("BTCUSDT", "BTC", "0.25"),
            ),
            parameters=_parameters(),
        )


def test_empty_decisions_are_rejected() -> None:
    with pytest.raises(PortfolioValidationError, match="empty"):
        build_ladder_targets((), parameters=_parameters())


@pytest.mark.parametrize(
    "risk_budgets",
    (
        {},
        {"BTC/USDT": Decimal("0.5")},
        {"BTCUSDT": Decimal("0")},
        {"BTCUSDT": Decimal("1.5")},
        {"BTCUSDT": Decimal("0.7"), "ETHUSDT": Decimal("0.4")},
    ),
)
def test_invalid_risk_budgets_are_rejected(risk_budgets: dict[str, Decimal]) -> None:
    with pytest.raises(PortfolioValidationError):
        LadderPortfolioParameters(risk_budgets=risk_budgets)


def test_risk_budgets_capped_by_max_gross_exposure() -> None:
    with pytest.raises(PortfolioValidationError, match="max_gross_exposure"):
        LadderPortfolioParameters(
            risk_budgets={"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")},
            max_gross_exposure=Decimal("0.8"),
        )
