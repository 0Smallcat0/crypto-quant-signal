"""Portfolio target contracts for the Core MVP."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from src.domain import Symbol


class PortfolioValidationError(ValueError):
    """Raised when portfolio target generation would break the Goal G contract."""


class PortfolioTargetParameterValues(Protocol):
    """Readable target constraints accepted by the portfolio target builder."""

    @property
    def max_active_positions(self) -> int: ...

    @property
    def max_symbol_weight(self) -> Decimal: ...

    @property
    def max_gross_exposure(self) -> Decimal: ...

    @property
    def cash_allowed(self) -> bool: ...

    @property
    def cooldown_enabled(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class PortfolioTargetParameters:
    """Long-only target constraints for converting rankings into weights."""

    max_active_positions: int = 3
    max_symbol_weight: Decimal = Decimal("0.35")
    max_gross_exposure: Decimal = Decimal("1.0")
    cash_allowed: bool = True
    cooldown_enabled: bool = True

    def __post_init__(self) -> None:
        if self.max_active_positions <= 0:
            msg = "max_active_positions must be positive"
            raise PortfolioValidationError(msg)
        _require_fraction("max_symbol_weight", self.max_symbol_weight)
        _require_fraction("max_gross_exposure", self.max_gross_exposure)
        if not self.cash_allowed:
            msg = "cash_allowed must stay enabled in Core MVP"
            raise PortfolioValidationError(msg)
        if not isinstance(self.cooldown_enabled, bool):
            msg = "cooldown_enabled must be bool"
            raise PortfolioValidationError(msg)


@dataclass(frozen=True, slots=True)
class PortfolioTarget:
    """Desired long-only portfolio weight for one symbol."""

    symbol: Symbol
    target_weight: Decimal
    source_score: Decimal
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_negative_fraction("target_weight", self.target_weight)
        _require_non_negative_fraction("source_score", self.source_score)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise PortfolioValidationError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise PortfolioValidationError(msg)


@dataclass(frozen=True, slots=True)
class PortfolioTargetSet:
    """Inspectable target weights plus residual cash."""

    targets: tuple[PortfolioTarget, ...]
    cash_weight: Decimal
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.targets, tuple):
            msg = "targets must be a tuple"
            raise PortfolioValidationError(msg)
        if any(not isinstance(target, PortfolioTarget) for target in self.targets):
            msg = "targets must contain PortfolioTarget values"
            raise PortfolioValidationError(msg)
        _require_non_negative_fraction("cash_weight", self.cash_weight)
        if self.gross_target_weight + self.cash_weight > Decimal("1"):
            msg = "target weights plus cash_weight must not exceed 1"
            raise PortfolioValidationError(msg)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise PortfolioValidationError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise PortfolioValidationError(msg)

    @property
    def gross_target_weight(self) -> Decimal:
        """Total non-cash target exposure."""

        return sum((target.target_weight for target in self.targets), Decimal("0"))


def _require_fraction(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise PortfolioValidationError(msg)
    if value <= Decimal("0") or value > Decimal("1"):
        msg = f"{name} must be greater than 0 and at most 1"
        raise PortfolioValidationError(msg)


def _require_non_negative_fraction(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise PortfolioValidationError(msg)
    if value < Decimal("0") or value > Decimal("1"):
        msg = f"{name} must be between 0 and 1"
        raise PortfolioValidationError(msg)
