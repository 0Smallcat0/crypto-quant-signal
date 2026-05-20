from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from src.data import (
    BinanceSpotPublicClient,
    CandleIssueCode,
    MarketDataValidationError,
    build_closed_kline_stream_url,
    build_universe_snapshot,
    inspect_candle_quality,
    parse_book_ticker_payload,
    parse_depth_snapshot_payload,
    parse_exchange_info_symbol_filters,
    parse_rest_kline_rows,
    parse_runtime_closed_kline_message,
    require_closed_candles,
)
from src.domain import Candle, Symbol, Timeframe


def _ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _symbol() -> Symbol:
    return Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT")


def _eth_symbol() -> Symbol:
    return Symbol(value="ETHUSDT", base_asset="ETH", quote_asset="USDT")


def _timeframe() -> Timeframe:
    return Timeframe("15m")


def _rest_row(open_time: datetime, *, close: str = "50100.0") -> list[object]:
    close_time = open_time + timedelta(minutes=15) - timedelta(milliseconds=1)
    return [
        _ms(open_time),
        "50000.0",
        "50200.0",
        "49900.0",
        close,
        "12.5",
        _ms(close_time),
        "625000.0",
        200,
        "8.0",
        "400000.0",
        "0",
    ]


def _closed_candle(open_time: datetime, symbol: Symbol | None = None) -> Candle:
    (candle,) = parse_rest_kline_rows(
        [_rest_row(open_time)],
        symbol=symbol or _symbol(),
        timeframe=_timeframe(),
        received_at=open_time + timedelta(minutes=16),
    )
    return candle


def test_rest_klines_are_parsed_as_closed_utc_domain_candles() -> None:
    open_time = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)

    (candle,) = parse_rest_kline_rows(
        [_rest_row(open_time)],
        symbol=_symbol(),
        timeframe=_timeframe(),
        received_at=datetime(2026, 5, 20, 0, 16, tzinfo=UTC),
    )

    assert candle.symbol.value == "BTCUSDT"
    assert candle.timeframe.value == "15m"
    assert candle.open_time == open_time
    assert candle.close_time == datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)
    assert candle.close_price == Decimal("50100.0")
    assert candle.volume == Decimal("12.5")
    assert candle.is_closed is True


def test_still_open_rest_kline_is_visible_and_blocked_from_strategy_input() -> None:
    open_time = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)
    candle = parse_rest_kline_rows(
        [_rest_row(open_time)],
        symbol=_symbol(),
        timeframe=_timeframe(),
        received_at=datetime(2026, 5, 20, 0, 10, tzinfo=UTC),
    )[0]

    assert candle.is_closed is False
    with pytest.raises(MarketDataValidationError, match="OPEN_CANDLE"):
        require_closed_candles((candle,))


def test_runtime_kline_message_only_accepts_closed_events() -> None:
    payload = {
        "stream": "btcusdt@kline_15m",
        "data": {
            "e": "kline",
            "E": _ms(datetime(2026, 5, 20, 0, 15, tzinfo=UTC)),
            "s": "BTCUSDT",
            "k": {
                "t": _ms(datetime(2026, 5, 20, 0, 0, tzinfo=UTC)),
                "T": _ms(datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)),
                "s": "BTCUSDT",
                "i": "15m",
                "o": "50000.0",
                "h": "50200.0",
                "l": "49900.0",
                "c": "50100.0",
                "v": "12.5",
                "x": False,
                "q": "625000.0",
            },
        },
    }

    assert parse_runtime_closed_kline_message(json.dumps(payload)) is None

    payload["data"]["k"]["x"] = True
    candle = parse_runtime_closed_kline_message(json.dumps(payload))

    assert candle is not None
    assert candle.symbol == _symbol()
    assert candle.is_closed is True


def test_quality_report_marks_gaps_duplicates_open_candles_and_stale_data() -> None:
    first_open = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)
    candles = (
        _closed_candle(first_open),
        _closed_candle(first_open + timedelta(minutes=15)),
        _closed_candle(first_open + timedelta(minutes=15)),
        _closed_candle(first_open + timedelta(minutes=45)),
        Candle(
            symbol=_symbol(),
            timeframe=_timeframe(),
            open_time=first_open + timedelta(minutes=60),
            close_time=first_open + timedelta(minutes=75) - timedelta(milliseconds=1),
            open_price=Decimal("50000"),
            high_price=Decimal("50200"),
            low_price=Decimal("49900"),
            close_price=Decimal("50100"),
            volume=Decimal("1"),
            is_closed=False,
        ),
    )

    report = inspect_candle_quality(
        candles,
        timeframe=_timeframe(),
        observed_at=first_open + timedelta(minutes=90),
        stale_after=timedelta(minutes=5),
    )

    assert {issue.code for issue in report.issues} == {
        CandleIssueCode.DUPLICATE,
        CandleIssueCode.GAP,
        CandleIssueCode.OPEN_CANDLE,
        CandleIssueCode.STALE,
    }
    assert report.is_usable_for_strategy is False


def test_quality_report_marks_stale_data_per_symbol() -> None:
    first_open = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)
    candles = (
        _closed_candle(first_open + timedelta(minutes=75), _symbol()),
        _closed_candle(first_open, _eth_symbol()),
    )

    report = inspect_candle_quality(
        candles,
        timeframe=_timeframe(),
        observed_at=first_open + timedelta(minutes=95),
        stale_after=timedelta(minutes=5),
    )

    stale_symbols = tuple(
        issue.symbol for issue in report.issues if issue.code is CandleIssueCode.STALE
    )
    assert stale_symbols == ("ETHUSDT",)


def test_exchange_info_symbol_filters_and_universe_snapshot_are_created() -> None:
    payload = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "status": "TRADING",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "isSpotTradingAllowed": True,
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "tickSize": "0.01000000",
                        "minPrice": "0.01000000",
                        "maxPrice": "1000000.00000000",
                    },
                    {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00001000",
                        "maxQty": "9000.00000000",
                        "stepSize": "0.00001000",
                    },
                    {
                        "filterType": "MIN_NOTIONAL",
                        "minNotional": "10.00000000",
                    },
                ],
            },
            {
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "quoteAsset": "BTC",
                "isSpotTradingAllowed": True,
                "filters": [],
            },
            {
                "symbol": "OLDUSDT",
                "status": "HALT",
                "baseAsset": "OLD",
                "quoteAsset": "USDT",
                "isSpotTradingAllowed": True,
                "filters": [],
            },
        ]
    }

    filters = parse_exchange_info_symbol_filters(payload)
    btc_filters = filters[0]
    snapshot = build_universe_snapshot(
        filters,
        created_at=datetime(2026, 5, 20, 0, 0, tzinfo=UTC),
    )

    assert btc_filters.symbol == _symbol()
    assert btc_filters.price_tick_size == Decimal("0.01000000")
    assert btc_filters.quantity_step_size == Decimal("0.00001000")
    assert btc_filters.min_notional == Decimal("10.00000000")
    assert tuple(symbol.value for symbol in snapshot.symbols) == ("BTCUSDT",)


def test_book_ticker_and_depth_snapshot_payloads_are_parsed() -> None:
    captured_at = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)

    (ticker,) = parse_book_ticker_payload(
        {
            "symbol": "BTCUSDT",
            "bidPrice": "50000.00",
            "bidQty": "1.25",
            "askPrice": "50001.00",
            "askQty": "0.75",
        },
        captured_at=captured_at,
    )
    depth = parse_depth_snapshot_payload(
        {
            "lastUpdateId": 123456,
            "bids": [["50000.00", "1.25"]],
            "asks": [["50001.00", "0.75"]],
        },
        symbol=_symbol(),
        captured_at=captured_at,
    )

    assert ticker.symbol == _symbol()
    assert ticker.bid_price == Decimal("50000.00")
    assert ticker.ask_quantity == Decimal("0.75")
    assert ticker.captured_at == captured_at
    assert depth.symbol == _symbol()
    assert depth.last_update_id == 123456
    assert depth.bids[0].price == Decimal("50000.00")
    assert depth.asks[0].quantity == Decimal("0.75")
    assert depth.captured_at == captured_at


def test_client_uses_public_binance_endpoints_without_auth_headers() -> None:
    async def run_client() -> tuple[Candle, ...]:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v3/klines"
            assert request.url.params["symbol"] == "BTCUSDT"
            assert request.url.params["interval"] == "15m"
            assert "authorization" not in request.headers
            return httpx.Response(
                200,
                json=[_rest_row(datetime(2026, 5, 20, 0, 0, tzinfo=UTC))],
            )

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(
            base_url="https://api.binance.com",
            transport=transport,
        ) as http_client:
            client = BinanceSpotPublicClient(http_client=http_client)
            return await client.fetch_historical_candles(
                symbol=_symbol(),
                timeframe=_timeframe(),
                received_at=datetime(2026, 5, 20, 0, 16, tzinfo=UTC),
            )

    candles = asyncio.run(run_client())

    assert len(candles) == 1
    assert candles[0].is_closed is True


def test_client_fetches_public_book_ticker_and_depth_without_auth_headers() -> None:
    captured_at = datetime(2026, 5, 20, 0, 0, tzinfo=UTC)

    async def run_client() -> tuple[str, str, Decimal, Decimal]:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "authorization" not in request.headers
            if request.url.path == "/api/v3/ticker/bookTicker":
                assert json.loads(request.url.params["symbols"]) == ["BTCUSDT", "ETHUSDT"]
                return httpx.Response(
                    200,
                    json=[
                        {
                            "symbol": "BTCUSDT",
                            "bidPrice": "50000.00",
                            "bidQty": "1.25",
                            "askPrice": "50001.00",
                            "askQty": "0.75",
                        }
                    ],
                )
            if request.url.path == "/api/v3/depth":
                assert request.url.params["symbol"] == "BTCUSDT"
                assert request.url.params["limit"] == "5"
                return httpx.Response(
                    200,
                    json={
                        "lastUpdateId": 123456,
                        "bids": [["50000.00", "1.25"]],
                        "asks": [["50001.00", "0.75"]],
                    },
                )
            msg = f"unexpected public endpoint: {request.url.path}"
            raise AssertionError(msg)

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(
            base_url="https://api.binance.com",
            transport=transport,
        ) as http_client:
            client = BinanceSpotPublicClient(http_client=http_client)
            (ticker,) = await client.fetch_book_tickers(
                ("BTCUSDT", "ETHUSDT"),
                captured_at=captured_at,
            )
            depth = await client.fetch_depth_snapshot(
                symbol=_symbol(),
                limit=5,
                captured_at=captured_at,
            )
        return ticker.symbol.value, depth.symbol.value, ticker.bid_price, depth.asks[0].price

    ticker_symbol, depth_symbol, bid_price, ask_level_price = asyncio.run(run_client())

    assert ticker_symbol == "BTCUSDT"
    assert depth_symbol == "BTCUSDT"
    assert bid_price == Decimal("50000.00")
    assert ask_level_price == Decimal("50001.00")


def test_closed_kline_stream_url_uses_public_combined_stream_format() -> None:
    url = build_closed_kline_stream_url(("BTCUSDT", "ETHUSDT"), _timeframe())

    assert url == (
        "wss://data-stream.binance.vision/stream?streams=btcusdt@kline_15m/ethusdt@kline_15m"
    )
