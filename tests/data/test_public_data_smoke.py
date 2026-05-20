from __future__ import annotations

import httpx

from src.data import (
    PublicDataSmokeStatus,
    first_passing_public_rest_base_url,
    smoke_public_rest_base_url,
)


def test_public_rest_smoke_marks_dns_block_as_environment_blocker() -> None:
    result = smoke_public_rest_base_url(
        "https://data-api.binance.vision",
        dns_resolver=lambda host: False,
    )

    assert result.host == "data-api.binance.vision"
    assert result.status is PublicDataSmokeStatus.DNS_BLOCKED
    assert result.classification == "ENVIRONMENT_BLOCKER"
    assert result.baseline_impact == "none"
    assert result.release_certification_impact == "cannot_start"


def test_public_rest_smoke_passes_against_mock_public_ping() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v3/ping"
        assert "authorization" not in request.headers
        return httpx.Response(200, json={})

    client = httpx.Client(
        base_url="https://data-api.binance.vision",
        transport=httpx.MockTransport(handler),
    )
    result = smoke_public_rest_base_url(
        "https://data-api.binance.vision",
        dns_resolver=lambda host: True,
        http_client=client,
    )

    assert result.status is PublicDataSmokeStatus.PASS
    assert result.classification == "OK"
    assert result.baseline_impact == "none"


def test_public_rest_smoke_classifies_rate_limit_and_region_blocks() -> None:
    rate_limited_client = httpx.Client(
        base_url="https://data-api.binance.vision",
        transport=httpx.MockTransport(lambda request: httpx.Response(429)),
    )
    region_blocked_client = httpx.Client(
        base_url="https://data-api.binance.vision",
        transport=httpx.MockTransport(lambda request: httpx.Response(451)),
    )

    rate_limited = smoke_public_rest_base_url(
        "https://data-api.binance.vision",
        dns_resolver=lambda host: True,
        http_client=rate_limited_client,
    )
    region_blocked = smoke_public_rest_base_url(
        "https://data-api.binance.vision",
        dns_resolver=lambda host: True,
        http_client=region_blocked_client,
    )

    assert rate_limited.status is PublicDataSmokeStatus.RATE_LIMITED
    assert region_blocked.status is PublicDataSmokeStatus.REGION_OR_WAF_BLOCKED


def test_first_passing_public_rest_base_url_uses_candidate_order() -> None:
    blocked = smoke_public_rest_base_url(
        "https://api.binance.com",
        dns_resolver=lambda host: False,
    )
    passed = smoke_public_rest_base_url(
        "https://data-api.binance.vision",
        dns_resolver=lambda host: True,
        http_client=httpx.Client(
            base_url="https://data-api.binance.vision",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={})),
        ),
    )

    assert first_passing_public_rest_base_url((blocked, passed)) == (
        "https://data-api.binance.vision"
    )
