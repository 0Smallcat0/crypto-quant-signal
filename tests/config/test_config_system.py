from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.binance_public_hosts import (
    BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES,
    BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES,
)
from src.config import AppConfig, config_snapshot, load_config, write_config_snapshot
from src.domain import Candle, Signal, Symbol, Timeframe
from src.features import FeatureSnapshot, FeatureSourceRange, build_feature_snapshots
from src.portfolio import build_portfolio_targets
from src.strategies import StrategyDecision, evaluate_large_liquid_trend_15

DEFAULT_CONFIG_PATH = Path("configs/runtime/paper_runtime.yaml")


def _base_config_data() -> dict[str, object]:
    return AppConfig().model_dump(mode="json")


def _with_nested_value(path: tuple[str, ...], value: object) -> dict[str, object]:
    updated = deepcopy(_base_config_data())
    cursor = updated
    for key in path[:-1]:
        next_value = cursor[key]
        assert isinstance(next_value, dict)
        cursor = next_value
    cursor[path[-1]] = value
    return updated


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _timeframe() -> Timeframe:
    return Timeframe("15m")


def _closed_candle(
    symbol: Symbol,
    index: int,
    *,
    close: str,
    volume: str = "10",
) -> Candle:
    open_time = datetime(2026, 5, 20, 0, 0, tzinfo=UTC) + timedelta(minutes=15 * index)
    close_price = Decimal(close)
    return Candle(
        symbol=symbol,
        timeframe=_timeframe(),
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15) - timedelta(milliseconds=1),
        open_price=close_price,
        high_price=close_price + Decimal("2"),
        low_price=close_price - Decimal("2"),
        close_price=close_price,
        volume=Decimal(volume),
        is_closed=True,
    )


def _strategy_snapshot(symbol: Symbol) -> FeatureSnapshot:
    as_of = datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)
    return FeatureSnapshot(
        symbol=symbol,
        timeframe=_timeframe(),
        as_of=as_of,
        source_ranges=(
            FeatureSourceRange(
                symbol=symbol,
                timeframe=_timeframe(),
                start_open_time=as_of - timedelta(minutes=15) + timedelta(milliseconds=1),
                end_close_time=as_of,
            ),
        ),
        values={
            "momentum_return": Decimal("0.01"),
            "trend_distance": Decimal("0.01"),
            "recent_high_distance": Decimal("0.01"),
            "volume_ratio": Decimal("0.5"),
            "btc_momentum_return": Decimal("-0.01"),
            "btc_trend_distance": Decimal("-0.01"),
        },
    )


def _portfolio_decision(value: str, base_asset: str, score: str) -> StrategyDecision:
    generated_at = datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)
    return StrategyDecision(
        symbol=_symbol(value, base_asset),
        signal=Signal.LONG,
        score=Decimal(score),
        reason_codes=("CONFIG_INTEGRATION_TEST",),
        generated_at_bar_close=generated_at,
        executable_from_next_bar=generated_at + timedelta(milliseconds=1),
    )


def test_default_config_model_has_core_mvp_defaults() -> None:
    config = AppConfig()

    assert config.account.initial_cash == Decimal("1000")
    assert config.account.quote_asset == "USDT"
    assert config.data_source.timeframe == "1d"
    assert config.data_source.rest_base_url_candidates == BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES
    assert (
        config.data_source.ws_stream_base_url_candidates
        == BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES
    )
    assert config.data_source.timeout_seconds == Decimal("10")
    assert config.strategy.name == "daily_trend_ensemble"
    assert config.portfolio.risk_budgets == {
        "BTCUSDT": Decimal("0.5"),
        "ETHUSDT": Decimal("0.5"),
    }
    assert "SOLUSDT" not in config.portfolio.risk_budgets
    assert config.risk.disaster_single_day_drop_fraction == Decimal("0.20")
    assert config.risk.stale_data_max_age_seconds == 129600
    assert config.runtime.mode == "paper"
    assert config.runtime.decision_timeframe == "1d"
    assert config.execution.mode == "paper"


def test_default_paper_runtime_config_loads_through_typed_model() -> None:
    config = load_config(DEFAULT_CONFIG_PATH)

    assert config.account.initial_cash == Decimal("1000")
    assert config.data_source.timeframe == "1d"
    assert config.strategy.name == "daily_trend_ensemble"
    assert config.portfolio.risk_budgets == {
        "BTCUSDT": Decimal("0.5"),
        "ETHUSDT": Decimal("0.5"),
    }
    assert config.runtime.mode == "paper"
    assert config.runtime.decision_timeframe == "1d"
    assert config.execution.fee_bps == Decimal("10")
    assert config.strategy.parameters.minimum_entry_score == Decimal("0.70")


@pytest.mark.parametrize(
    "risk_budgets",
    (
        {},
        {"BTCUSDT": "0.7", "ETHUSDT": "0.4"},
        {"BTC/USDT": "0.5"},
        {"BTCUSDT": "0"},
        {"BTCUSDT": "1.5"},
    ),
)
def test_invalid_risk_budgets_are_rejected(risk_budgets: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(_with_nested_value(("portfolio", "risk_budgets"), risk_budgets))


def test_notification_defaults_are_log_channel() -> None:
    config = AppConfig()

    assert config.notifications.enabled is True
    assert config.notifications.channel == "log"
    assert config.notifications.webhook_url == ""
    assert config.notifications.follow_principal_usdt == Decimal("1000")


def test_discord_channel_carries_no_secret_in_config() -> None:
    config = AppConfig.model_validate(_with_nested_value(("notifications", "channel"), "discord"))

    # The discord channel is valid with no webhook_url; credentials load from env.
    assert config.notifications.channel == "discord"
    assert config.notifications.webhook_url == ""


@pytest.mark.parametrize(
    ("channel", "webhook_url"),
    (
        ("webhook", ""),
        ("webhook", "http://insecure.example/hook"),
        ("log", "https://hook.example/x"),
        ("discord", "https://hook.example/x"),
    ),
)
def test_invalid_notification_configs_are_rejected(channel: str, webhook_url: str) -> None:
    data = _base_config_data()
    data["notifications"] = {"enabled": True, "channel": channel, "webhook_url": webhook_url}

    with pytest.raises(ValidationError):
        AppConfig.model_validate(data)


def test_negative_follow_principal_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(
            _with_nested_value(("notifications", "follow_principal_usdt"), "0")
        )


def test_config_file_values_override_model_defaults(tmp_path: Path) -> None:
    data = _base_config_data()
    strategy = data["strategy"]
    risk = data["risk"]
    execution = data["execution"]
    runtime = data["runtime"]
    assert isinstance(strategy, dict)
    assert isinstance(risk, dict)
    assert isinstance(execution, dict)
    assert isinstance(runtime, dict)
    strategy_parameters = strategy["parameters"]
    assert isinstance(strategy_parameters, dict)

    strategy_parameters["minimum_entry_score"] = "0.80"
    risk["min_notional_usdt"] = "25"
    execution["fee_bps"] = "7.5"
    runtime["idempotency_key_namespace"] = "paper-runtime-test"

    config_path = tmp_path / "paper_runtime.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    config = load_config(config_path)

    assert config.strategy.parameters.minimum_entry_score == Decimal("0.80")
    assert config.risk.min_notional_usdt == Decimal("25")
    assert config.execution.fee_bps == Decimal("7.5")
    assert config.runtime.idempotency_key_namespace == "paper-runtime-test"


def test_loaded_config_values_drive_goal_e_f_g_parameters(tmp_path: Path) -> None:
    data = _base_config_data()
    strategy = data["strategy"]
    portfolio = data["portfolio"]
    assert isinstance(strategy, dict)
    assert isinstance(portfolio, dict)
    strategy_parameters = strategy["parameters"]
    assert isinstance(strategy_parameters, dict)

    strategy_parameters.update(
        {
            "momentum_lookback_candles": 1,
            "trend_lookback_candles": 2,
            "breakout_lookback_candles": 2,
            "volume_lookback_candles": 2,
            "volatility_lookback_candles": 2,
            "minimum_entry_score": "0.80",
            "exit_score": "0.20",
        }
    )
    portfolio.update(
        {
            "max_active_positions": 1,
            "max_symbol_weight": "0.20",
            "max_gross_exposure": "0.50",
        }
    )
    config_path = tmp_path / "paper_runtime.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    config = load_config(config_path)
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")
    feature_snapshots = build_feature_snapshots(
        (
            _closed_candle(eth, 0, close="100", volume="10"),
            _closed_candle(eth, 1, close="100", volume="20"),
            _closed_candle(eth, 2, close="120", volume="60"),
        ),
        btc_candles=(
            _closed_candle(btc, 0, close="200"),
            _closed_candle(btc, 1, close="200"),
            _closed_candle(btc, 2, close="220"),
        ),
        config=config.strategy.parameters,
    )
    assert len(feature_snapshots) == 1
    assert feature_snapshots[0].values["momentum_return"] == Decimal("0.2")

    strategy_decision = evaluate_large_liquid_trend_15(
        _strategy_snapshot(eth),
        parameters=config.strategy.parameters,
    )
    assert strategy_decision.score == Decimal("0.70")
    assert strategy_decision.signal is Signal.FLAT

    targets = build_portfolio_targets(
        (
            _portfolio_decision("BTCUSDT", "BTC", "0.90"),
            _portfolio_decision("ETHUSDT", "ETH", "0.80"),
        ),
        parameters=config.portfolio,
    )
    assert [(target.symbol.value, target.target_weight) for target in targets.targets] == [
        ("BTCUSDT", Decimal("0.20")),
    ]
    assert targets.cash_weight == Decimal("0.80")


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("runtime", "mode"), "live"),
        (("runtime", "real_trading_enabled"), True),
        (("runtime", "private_api_enabled"), True),
        (("execution", "real_orders_enabled"), True),
        (("execution", "private_api_enabled"), True),
        (("data_source", "private_api_enabled"), True),
        (("data_source", "api_key_required"), True),
    ),
)
def test_real_trading_and_private_api_flags_are_rejected(
    path: tuple[str, ...], value: object
) -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(_with_nested_value(path, value))


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("strategy", "allow_short"), True),
        (("portfolio", "allow_short"), True),
        (("risk", "short_exposure_enabled"), True),
        (("risk", "margin_enabled"), True),
        (("risk", "leverage_enabled"), True),
        (("execution", "margin_enabled"), True),
        (("execution", "leverage_enabled"), True),
    ),
)
def test_short_margin_and_leverage_flags_are_rejected(path: tuple[str, ...], value: object) -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(_with_nested_value(path, value))


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("api_dashboard", "read_only"), False),
        (("api_dashboard", "manual_orders_enabled"), True),
        (("api_dashboard", "risk_limit_mutation_enabled"), True),
        (("api_dashboard", "private_account_access_enabled"), True),
    ),
)
def test_api_dashboard_mutation_and_private_account_flags_are_rejected(
    path: tuple[str, ...], value: object
) -> None:
    with pytest.raises(ValidationError):
        AppConfig.model_validate(_with_nested_value(path, value))


def test_unknown_config_fields_are_rejected() -> None:
    data = _base_config_data()
    data["live_trading"] = {"enabled": True}

    with pytest.raises(ValidationError):
        AppConfig.model_validate(data)


def test_config_snapshot_is_json_serializable_and_writeable(tmp_path: Path) -> None:
    config = load_config(DEFAULT_CONFIG_PATH)
    snapshot = config_snapshot(config)

    assert snapshot["version"] == "1"
    assert snapshot["account"] == {
        "account_id": "paper-main",
        "initial_cash": "1000",
        "quote_asset": "USDT",
    }

    snapshot_path = write_config_snapshot(config, tmp_path / "config_snapshot.json")
    assert snapshot_path.read_text(encoding="utf-8").endswith("\n")
    assert '"mode": "paper"' in snapshot_path.read_text(encoding="utf-8")
