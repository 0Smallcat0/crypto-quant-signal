# Bundled demo candles

Daily OHLCV for `BTCUSDT` and `ETHUSDT`, 2024-01-01 → 2026-06-30 (912 closed
candles each), captured from the Binance Spot **public** market-data API via
`scripts/ingest_public_ohlcv.py`. Same JSONL schema as `data/candles/`.

Purpose: let `python -m scripts.run_demo` replay the real engine completely
offline — no API keys, no network, no region restrictions. These files are a
frozen fixture; the live system never reads them.

Public factual market data, bundled solely for reproducibility of the demo.
