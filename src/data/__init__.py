"""Public market data entry points."""

from src.binance_public_hosts import (
    BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES,
    BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES,
)
from src.data.binance import (
    BinanceSpotPublicClient,
    build_closed_kline_stream_url,
    build_universe_snapshot,
    parse_book_ticker_payload,
    parse_depth_snapshot_payload,
    parse_exchange_info_symbol_filters,
    parse_rest_kline_rows,
    parse_runtime_closed_kline_message,
    symbol_from_binance_native,
)
from src.data.quality import inspect_candle_quality, require_closed_candles, timeframe_delta
from src.data.smoke import (
    PublicDataSmokeResult,
    PublicDataSmokeStatus,
    dns_resolves,
    first_passing_public_rest_base_url,
    run_public_rest_smoke,
    smoke_public_rest_base_url,
)
from src.data.types import (
    BookTickerSnapshot,
    CandleIssueCode,
    CandleQualityIssue,
    CandleQualityReport,
    DepthLevel,
    DepthSnapshot,
    MarketDataError,
    MarketDataValidationError,
    SymbolFilters,
    UniverseSnapshot,
)

__all__ = [
    "BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES",
    "BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES",
    "BinanceSpotPublicClient",
    "BookTickerSnapshot",
    "CandleIssueCode",
    "CandleQualityIssue",
    "CandleQualityReport",
    "DepthLevel",
    "DepthSnapshot",
    "MarketDataError",
    "MarketDataValidationError",
    "PublicDataSmokeResult",
    "PublicDataSmokeStatus",
    "SymbolFilters",
    "UniverseSnapshot",
    "build_closed_kline_stream_url",
    "build_universe_snapshot",
    "dns_resolves",
    "first_passing_public_rest_base_url",
    "inspect_candle_quality",
    "parse_book_ticker_payload",
    "parse_depth_snapshot_payload",
    "parse_exchange_info_symbol_filters",
    "parse_rest_kline_rows",
    "parse_runtime_closed_kline_message",
    "require_closed_candles",
    "run_public_rest_smoke",
    "smoke_public_rest_base_url",
    "symbol_from_binance_native",
    "timeframe_delta",
]
