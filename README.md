# Crypto Quant Paper Trading MVP

Clean rebuild for a crypto spot, long-only, public-data, 15-minute paper trading MVP.

The Core MVP starts with a `1000 USDT` virtual account and records virtual decisions,
orders, fills, positions, cash, PnL, rejected orders, and risk events. It must not submit
real exchange orders, read private account balances, require API keys, or add live trading
paths in MVP v1.0.

## Goal A Status

This repository currently contains the foundation scaffold only:

- Python 3.12 project configuration.
- Source, config, docs, scripts, and test directories.
- Local TimescaleDB/PostgreSQL-compatible Docker Compose file.
- Baseline lint, format, type, import-boundary, and test tooling.

No strategy, data fetching, execution, runtime loop, dashboard behavior, research lab, real
exchange API, or private API code is implemented in Goal A.

## Local Setup

Use Python 3.12 explicitly. On this machine, `python` may point at a newer interpreter.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]" -c requirements\constraints-dev.txt
```

## Verification

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy --strict src/
.\.venv\Scripts\lint-imports
.\.venv\Scripts\python.exe -m pytest -m "not network" tests -q
docker compose config
docker compose up -d --wait
docker compose down
git remote -v
```

`git remote -v` should print nothing for Goal A.

## Local Database

The local database service uses dummy development credentials only:

- Host port: `54320`
- Database: `crypto_quant`
- User: `crypto`
- Password: `crypto_dev_only`

These are local Docker credentials, not production secrets.

