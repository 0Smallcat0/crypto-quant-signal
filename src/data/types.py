"""Public market data contracts for the Core MVP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from src.domain import Symbol


class MarketDataError(ValueError):
    """Raised when public market data cannot be parsed or fetched safely."""


class MarketDataValidationError(MarketDataError):
    """Raised when market data is not safe for downstream strategy input."""


class CandleIssueCode(Enum):
    """Visible candle quality issue codes."""

    OPEN_CANDLE = "OPEN_CANDLE"
    GAP = "GAP"
    DUPLICATE = "DUPLICATE"
    STALE = "STALE"


@dataclass(frozen=True, slots=True)
class CandleQualityIssue:
    """One visible issue found in a candle sequence."""

    code: CandleIssueCode
    symbol: str
    timeframe: str
    open_time: datetime | None = None
    expected_open_time: datetime | None = None
    actual_open_time: datetime | None = None
    detail: str = ""


@dataclass(frozen=True, slots=True)
class CandleQualityReport:
    """Candle quality report consumed by later feature/risk/runtime gates."""

    issues: tuple[CandleQualityIssue, ...]

    @property
    def is_usable_for_strategy(self) -> bool:
        return not self.issues


@dataclass(frozen=True, slots=True)
class SymbolFilters:
    """Public Binance Spot filter values needed by later sizing and risk checks."""

    symbol: Symbol
    status: str
    is_spot_trading_allowed: bool
    price_tick_size: Decimal | None
    quantity_step_size: Decimal | None
    min_quantity: Decimal | None
    min_notional: Decimal | None
    raw_filter_types: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UniverseSelectionRules:
    """Public-data eligibility floors for the Core MVP universe."""

    quote_asset: str = "USDT"
    min_closed_15m_candles: int = 96
    min_recent_quote_volume: Decimal = Decimal("100000")

    def __post_init__(self) -> None:
        if not self.quote_asset.strip():
            msg = "quote_asset must not be empty"
            raise MarketDataValidationError(msg)
        if self.min_closed_15m_candles <= 0:
            msg = "min_closed_15m_candles must be positive"
            raise MarketDataValidationError(msg)
        _require_positive_decimal("min_recent_quote_volume", self.min_recent_quote_volume)


@dataclass(frozen=True, slots=True)
class UniverseEligibilityMetrics:
    """Closed-candle public metrics used to admit symbols into the MVP universe."""

    symbol: Symbol
    closed_15m_candle_count: int
    recent_quote_volume: Decimal

    def __post_init__(self) -> None:
        if self.closed_15m_candle_count < 0:
            msg = "closed_15m_candle_count must not be negative"
            raise MarketDataValidationError(msg)
        _require_non_negative_decimal("recent_quote_volume", self.recent_quote_volume)


@dataclass(frozen=True, slots=True)
class BookTickerSnapshot:
    """Best public bid/ask snapshot for one Binance Spot symbol."""

    symbol: Symbol
    bid_price: Decimal
    bid_quantity: Decimal
    ask_price: Decimal
    ask_quantity: Decimal
    captured_at: datetime

    def __post_init__(self) -> None:
        _require_positive_decimal("bid_price", self.bid_price)
        _require_positive_decimal("ask_price", self.ask_price)
        _require_non_negative_decimal("bid_quantity", self.bid_quantity)
        _require_non_negative_decimal("ask_quantity", self.ask_quantity)
        _require_utc("captured_at", self.captured_at)
        if self.ask_price < self.bid_price:
            msg = "ask_price must not be below bid_price"
            raise MarketDataValidationError(msg)


@dataclass(frozen=True, slots=True)
class DepthLevel:
    """One public order-book price level."""

    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        _require_positive_decimal("price", self.price)
        _require_non_negative_decimal("quantity", self.quantity)


@dataclass(frozen=True, slots=True)
class DepthSnapshot:
    """Public order-book depth snapshot for future paper cost modeling."""

    symbol: Symbol
    last_update_id: int
    bids: tuple[DepthLevel, ...]
    asks: tuple[DepthLevel, ...]
    captured_at: datetime

    def __post_init__(self) -> None:
        if self.last_update_id < 0:
            msg = "last_update_id must not be negative"
            raise MarketDataValidationError(msg)
        if not self.bids or not self.asks:
            msg = "depth snapshot must include bids and asks"
            raise MarketDataValidationError(msg)
        if any(not isinstance(level, DepthLevel) for level in (*self.bids, *self.asks)):
            msg = "depth levels must be DepthLevel values"
            raise MarketDataValidationError(msg)
        _require_utc("captured_at", self.captured_at)


@dataclass(frozen=True, slots=True)
class UniverseSnapshot:
    """Point-in-time public-data universe snapshot."""

    symbols: tuple[Symbol, ...]
    created_at: datetime
    source: str

    def __post_init__(self) -> None:
        _require_utc("created_at", self.created_at)
        if not self.source.strip():
            msg = "source must not be empty"
            raise MarketDataValidationError(msg)


def _require_positive_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal):
        msg = f"{name} must be Decimal"
        raise MarketDataValidationError(msg)
    if value <= Decimal("0"):
        msg = f"{name} must be positive"
        raise MarketDataValidationError(msg)


def _require_non_negative_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal):
        msg = f"{name} must be Decimal"
        raise MarketDataValidationError(msg)
    if value < Decimal("0"):
        msg = f"{name} must not be negative"
        raise MarketDataValidationError(msg)


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise MarketDataValidationError(msg)
