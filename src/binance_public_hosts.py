"""Official Binance public market-data host defaults."""

BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES = (
    "https://data-api.binance.vision",
    "https://api.binance.com",
    "https://api-gcp.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api4.binance.com",
)

BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES = (
    "wss://data-stream.binance.vision/stream",
    "wss://stream.binance.com:443/stream",
    "wss://stream.binance.com:9443/stream",
)

BINANCE_REST_BASE_URL = BINANCE_PUBLIC_REST_BASE_URL_CANDIDATES[0]
BINANCE_WS_BASE_URL = BINANCE_PUBLIC_WS_STREAM_BASE_URL_CANDIDATES[0]
