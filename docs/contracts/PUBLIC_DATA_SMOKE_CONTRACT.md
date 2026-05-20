# Public Data Smoke Contract

Status: active Core MVP support contract

Manual live public-data smoke is not part of baseline CI.

Baseline CI remains:

```bash
pytest -m "not network" tests -q
```

If local DNS cannot resolve Binance public market-data hosts, record the live
smoke result as:

```text
DNS_BLOCKED_BY_ENVIRONMENT
```

Do not record that state as:

```text
strategy failed
runtime failed
Binance adapter failed
MVP baseline failed
```

The implementation can still be code complete when:

- offline contract tests pass
- recorded fixture tests pass
- mock public endpoint tests pass
- replay-driven paper runtime smoke passes
- no private API path exists
- no real order path exists

Release certification cannot start until at least one official Binance public
market-data host is reachable from the runtime environment.

Preferred REST candidate order:

```text
https://data-api.binance.vision
https://api.binance.com
https://api-gcp.binance.com
https://api1.binance.com
https://api2.binance.com
https://api3.binance.com
https://api4.binance.com
```

Preferred combined WebSocket stream candidate order:

```text
wss://data-stream.binance.vision/stream
wss://stream.binance.com:443/stream
wss://stream.binance.com:9443/stream
```

Smoke status labels:

```text
PASS
DNS_BLOCKED
TCP_BLOCKED
TLS_OR_PROXY_BLOCKED
HTTP_BLOCKED
RATE_LIMITED
REGION_OR_WAF_BLOCKED
API_ERROR
```
