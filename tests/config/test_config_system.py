from __future__ import annotations

from copy import deepcopy
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


def test_default_config_model_has_core_mvp_defaults() -> None:
    config = AppConfig()

    assert config.account.initial_cash == Decimal("1000")
    assert config.account.quote_asset == "USDT"
    assert config.data_source.timeframe == "15m"
    assert config.data_source.rest_base_url_candidates == BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES
    assert (
        config.data_source.ws_stream_base_url_candidates
        == BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES
    )
    assert config.data_source.timeout_seconds == Decimal("10")
    assert config.runtime.mode == "paper"
    assert config.execution.mode == "paper"


def test_default_paper_runtime_config_loads_through_typed_model() -> None:
    config = load_config(DEFAULT_CONFIG_PATH)

    assert config.account.initial_cash == Decimal("1000")
    assert config.data_source.timeframe == "15m"
    assert config.runtime.mode == "paper"
    assert config.execution.fee_bps == Decimal("10")
    assert config.strategy.parameters.minimum_entry_score == Decimal("0.70")


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
