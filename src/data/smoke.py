"""Manual public-market-data smoke preflight helpers."""

from __future__ import annotations

import socket
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

import httpx


class PublicDataSmokeStatus(Enum):
    """Manual live-smoke status, kept separate from baseline CI results."""

    PASS = "PASS"
    DNS_BLOCKED = "DNS_BLOCKED"
    TCP_BLOCKED = "TCP_BLOCKED"
    TLS_OR_PROXY_BLOCKED = "TLS_OR_PROXY_BLOCKED"
    HTTP_BLOCKED = "HTTP_BLOCKED"
    RATE_LIMITED = "RATE_LIMITED"
    REGION_OR_WAF_BLOCKED = "REGION_OR_WAF_BLOCKED"
    API_ERROR = "API_ERROR"


@dataclass(frozen=True, slots=True)
class PublicDataSmokeResult:
    """One base URL preflight result for manual public-data smoke runs."""

    base_url: str
    host: str
    status: PublicDataSmokeStatus
    detail: str
    classification: str
    baseline_impact: str
    release_certification_impact: str

    def as_dict(self) -> dict[str, str]:
        return {
            "base_url": self.base_url,
            "host": self.host,
            "status": self.status.value,
            "detail": self.detail,
            "classification": self.classification,
            "baseline_impact": self.baseline_impact,
            "release_certification_impact": self.release_certification_impact,
        }


def dns_resolves(host: str, *, port: int = 443) -> bool:
    """Return whether the current runtime can resolve a public-data host."""

    try:
        socket.getaddrinfo(host, port)
    except socket.gaierror:
        return False
    return True


def smoke_public_rest_base_url(
    base_url: str,
    *,
    dns_resolver: Callable[[str], bool] = dns_resolves,
    http_client: httpx.Client | None = None,
    timeout_seconds: float = 10.0,
) -> PublicDataSmokeResult:
    """Run DNS plus HTTPS ping preflight for one public REST base URL."""

    host = _host_from_base_url(base_url)
    if not dns_resolver(host):
        return _result(
            base_url,
            host,
            PublicDataSmokeStatus.DNS_BLOCKED,
            f"DNS resolution failed for {host}",
        )

    owns_client = http_client is None
    client = http_client or httpx.Client(base_url=base_url, timeout=timeout_seconds)
    try:
        response = client.get("/api/v3/ping")
        if response.status_code in {418, 429}:
            return _result(
                base_url,
                host,
                PublicDataSmokeStatus.RATE_LIMITED,
                f"HTTP {response.status_code}",
            )
        if response.status_code in {403, 451}:
            return _result(
                base_url,
                host,
                PublicDataSmokeStatus.REGION_OR_WAF_BLOCKED,
                f"HTTP {response.status_code}",
            )
        if response.status_code >= 400:
            return _result(
                base_url,
                host,
                PublicDataSmokeStatus.HTTP_BLOCKED,
                f"HTTP {response.status_code}",
            )
        return _result(base_url, host, PublicDataSmokeStatus.PASS, "ping passed")
    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        return _result(base_url, host, PublicDataSmokeStatus.TCP_BLOCKED, repr(exc))
    except (httpx.ProxyError, httpx.RemoteProtocolError, httpx.ReadTimeout) as exc:
        return _result(
            base_url,
            host,
            PublicDataSmokeStatus.TLS_OR_PROXY_BLOCKED,
            repr(exc),
        )
    except httpx.HTTPError as exc:
        return _result(base_url, host, PublicDataSmokeStatus.API_ERROR, repr(exc))
    finally:
        if owns_client:
            client.close()


def run_public_rest_smoke(
    base_urls: Iterable[str],
    *,
    timeout_seconds: float = 10.0,
) -> tuple[PublicDataSmokeResult, ...]:
    """Run manual-smoke preflight across public REST base URL candidates."""

    return tuple(
        smoke_public_rest_base_url(base_url, timeout_seconds=timeout_seconds)
        for base_url in base_urls
    )


def first_passing_public_rest_base_url(
    results: Iterable[PublicDataSmokeResult],
) -> str | None:
    """Return the first public REST base URL that passed preflight."""

    for result in results:
        if result.status is PublicDataSmokeStatus.PASS:
            return result.base_url
    return None


def _host_from_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or parsed.hostname is None:
        msg = "public REST base URL must be an https URL with a host"
        raise ValueError(msg)
    return parsed.hostname


def _result(
    base_url: str,
    host: str,
    status: PublicDataSmokeStatus,
    detail: str,
) -> PublicDataSmokeResult:
    if status is PublicDataSmokeStatus.PASS:
        return PublicDataSmokeResult(
            base_url=base_url,
            host=host,
            status=status,
            detail=detail,
            classification="OK",
            baseline_impact="none",
            release_certification_impact="none",
        )
    return PublicDataSmokeResult(
        base_url=base_url,
        host=host,
        status=status,
        detail=detail,
        classification="ENVIRONMENT_BLOCKER",
        baseline_impact="none",
        release_certification_impact="cannot_start",
    )
