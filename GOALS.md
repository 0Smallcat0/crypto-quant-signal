# GOALS.md

Version: `v0.8-readable-expandable`
Status: Core MVP work queue
Last updated: `2026-05-19`
Project: `Crypto Quant Paper Trading MVP v1.0`

---

## 0. Product Target

Build a crypto spot, long-only, public-data, 15-minute paper trading system.

MVP output:

```text
A 1000 USDT virtual account follows system-generated LONG/FLAT decisions.
The user can see virtual buys, virtual sells, positions, cash, PnL, rejected orders, and risk events.
```

MVP does not submit real exchange orders.

Plain language:

```text
先做一個會用真實公開行情、但只在虛擬帳戶買賣的系統。
不是先做實盤機器人，也不是先做研究平台。
```

---

## 1. Goal Structure

Goals are split into three groups.

### 1.1 Core MVP

Must be done first.

```text
A. Repository Foundation
B. Domain Types
C. Config System
D. Public Market Data
E. Feature Pipeline
F. First Strategy
G. Portfolio Targets
H. Risk Gate
I. Paper Broker + Accounting
J. Backtest
K. Paper Runtime
L. Read-Only Dashboard
M. Core MVP Complete
```

### 1.2 Post-MVP Validation

Useful after Core MVP works.

```text
N. Paper Runtime Stability Run
O. Research Lab
```

### 1.3 Future Extensions

Allowed later, not part of Core MVP.

```text
P. HMM / ML Regime Research
Q. Genetic Algorithm Parameter Research
R. Multi-Strategy Studio
S. Read-Only Real Account Reconciliation
T. Live Trading Contract
```

---

## 2. Global Rules

### 2.1 Allowed In Core MVP

- Public market data.
- Binance Spot public REST/WebSocket.
- Backtesting.
- Paper trading through virtual account ledger.
- Virtual orders.
- Virtual fills.
- Spot long-only portfolio logic.
- Read-only dashboard/API.

### 2.2 Forbidden In Core MVP

- Real order submission.
- Private exchange API.
- API keys.
- Real account balances.
- Margin.
- Leverage.
- Borrowing.
- Lending.
- Derivatives.
- Perpetual futures.
- Short selling.
- Negative position quantity.
- Selling more than current holdings.
- Using still-open candles for signal generation.
- Same-bar execution.

### 2.3 Baseline Verification

Before claiming Core MVP complete:

```bash
ruff check .
ruff format --check .
mypy --strict src/
lint-imports
pytest -m "not network" tests -q
```

Network tests are not part of unit tests or CI. Manual public-data smoke tests must be explicitly marked.

---

## Goal A: Repository Foundation

### Why

Create a clean project foundation that future work can build on without carrying over legacy code.

### Build

- Initialize git repository.
- Create `main` branch.
- Add `.gitignore`.
- Add Python 3.12 project config.
- Add package scaffold.
- Add test scaffold.
- Add config folders.
- Add contract folders.
- Add local database compose file.
- Add baseline tool configuration.

### Required Choices

```text
Python: >=3.12,<3.13
Environment: .venv
Install: pip install -e ".[dev]" -c requirements/constraints-dev.txt
Package manager: pip + pyproject.toml + constraints file
```

Allowed runtime dependencies:

```text
pydantic
pydantic-settings
PyYAML
httpx
websockets
SQLAlchemy
alembic
psycopg
pandas
numpy
pyarrow
fastapi
jinja2
uvicorn
```

Allowed dev dependencies:

```text
pytest
ruff
mypy
import-linter
pre-commit
types-PyYAML
pandas-stubs
```

Not part of Core MVP dependencies:

```text
ccxt
torch
hmmlearn
scikit-learn
ta-lib
optuna
tensorflow
xgboost
lightgbm
```

### Done When

- repo is initialized
- base files exist
- package imports
- tests can run
- verification commands are documented
- initial commit contains docs and scaffold
- no remote is configured
- no private API code exists

### Not Now

- no strategy implementation yet
- no real exchange API
- no research lab
- no live trading

---

## Goal B: Domain Types

### Why

Make illegal trading states hard or impossible to represent.

### Build

Domain objects for:

- symbol
- timeframe
- candle
- money
- price
- quantity
- signal
- position
- target position
- order intent
- virtual order
- virtual fill
- virtual account snapshot
- risk decision

### Done When

- `Signal` supports only `LONG` and `FLAT`
- `SHORT` cannot be represented
- position quantity cannot be negative
- target quantity cannot be negative
- sell cannot exceed current holding
- money, price, quantity, fee, and fill values use `Decimal`
- domain imports no business, runtime, database, script, or exchange modules

### Not Now

- no exchange API
- no strategy logic
- no account persistence

---

## Goal C: Config System

### Why

The system should be reproducible without editing code.

### Build

Typed configs for:

- data source
- strategy
- portfolio
- risk
- execution
- runtime
- storage
- API/dashboard

### Done When

- configs load through typed models
- default initial virtual cash is `1000 USDT`
- default timeframe is `15m`
- default mode is `paper`
- real trading flags are rejected
- private API flags are rejected
- short/margin/leverage flags are rejected
- each run can store a config snapshot

### Not Now

- no production secret management
- no live trading config
- no strategy optimization config

---

## Goal D: Public Market Data

### Why

The system needs trustworthy public market data before it can trade virtually.

### Build

- Binance Spot public historical candles.
- Binance Spot public runtime candle stream.
- Closed-candle detection.
- Candle validation.
- Gap detection.
- Duplicate detection.
- Stale data detection.
- Public symbol filters.
- Public book ticker / depth snapshot support for future cost modeling.
- Universe snapshot.

### MVP Default

```text
Primary data source: Binance Spot public REST/WebSocket
Internal symbol format: BTCUSDT
Display symbol format: BTC/USDT
Timezone: UTC aware datetimes
Universe: large, mature, liquid USDT spot pairs
```

Detailed universe rules belong in:

```text
docs/contracts/UNIVERSE_CONTRACT.md
```

### Done When

- historical closed 15m candles can be fetched or loaded
- runtime closed candle events can be detected
- still-open candles are blocked from strategy input
- gaps, duplicates, and stale data are visible
- symbol filters are stored or available
- universe snapshot can be created

### Not Now

- no private endpoints
- no API keys
- no CCXT dependency
- no multi-exchange adapter implementation

---

## Goal E: Feature Pipeline

### Why

Features turn candles into neutral information that strategies can use.

### Build

Initial feature groups:

- return / momentum
- trend
- recent high / breakout support
- volume ratio
- volatility
- BTC market condition

### Done When

- features use only closed candles
- feature snapshots include timestamp and source candle range
- feature code does not access account, portfolio, order, or broker state
- feature tests prove no future data is used

### Not Now

- no model training
- no HMM
- no neural network
- no strategy parameter search

---

## Goal F: First Strategy

### Why

Core MVP needs one strategy so the virtual account can make decisions.

### Build

First active strategy:

```text
Large Liquid Trend 15
大幣高流動性 15 分鐘趨勢策略
```

Plain behavior:

```text
Buy only large liquid coins that show clear strength.
Do not buy weak coins.
Do not buy just because a candle closed.
Exit when strength disappears or risk rules trigger.
```

Detailed formula belongs in:

```text
docs/contracts/STRATEGY_LARGE_LIQUID_TREND_15.md
```

### Done When

- strategy returns only `LONG` or `FLAT`
- strategy emits score and reason codes
- strategy output is deterministic for the same input
- strategy does not size positions
- strategy does not create orders
- strategy does not bypass risk
- strategy does not use private data

### Not Now

- no second active strategy
- no HMM
- no neural network
- no genetic optimizer
- no automatic parameter search

---

## Goal G: Portfolio Targets

### Why

Strategy says what looks attractive; portfolio decides how much to target.

### Build

- select candidates from strategy output
- build target weights
- cap single-symbol exposure
- allow cash
- reduce unnecessary churn

### MVP Default

```text
max_active_positions: 3
max_symbol_weight: 35%
max_gross_exposure: 100%
cash_allowed: true
cooldown_enabled: true
```

### Done When

- targets are never negative
- no short exposure is possible
- portfolio can hold cash
- portfolio does not create orders directly
- portfolio output can be inspected and tested

### Not Now

- no Black-Litterman
- no multi-strategy allocation
- no risk parity optimizer

---

## Goal H: Risk Gate

### Why

Risk gate prevents invalid or dangerous virtual actions before they reach the paper broker.

### Build

Checks for:

- no short exposure
- no negative quantity
- sell cannot exceed holdings
- no stale-data trading
- no same-bar execution
- minimum notional
- exchange filters
- drawdown pause
- daily loss pause
- account stop
- trailing stop

### Done When

- every rejection has a reason code
- risk gate can pause new buys while allowing risk-reducing sells
- risk gate cannot be bypassed by paper broker
- missing exchange filters make a symbol untradable
- tests prove invalid actions are rejected

### Not Now

- no advanced portfolio risk model
- no VaR engine
- no live exchange kill switch

---

## Goal I: Paper Broker And Accounting

### Why

The system must simulate buys and sells and maintain a trustworthy virtual account.

### Build

Paper broker:

- accepts only risk-approved virtual orders
- applies fee assumption
- applies slippage assumption
- validates exchange-like constraints
- records accepted orders, rejected orders, and fills

Accounting:

- cash
- positions
- realized PnL
- unrealized PnL
- equity
- drawdown
- append-only ledger

### Done When

- paper broker never calls private API
- paper broker never sends real orders
- fills update cash and positions correctly
- ledger explains every cash and position change
- fees and slippage are recorded
- negative cash and negative position are rejected

### Not Now

- no real broker
- no exchange signing
- no real account reconciliation

---

## Goal J: Backtest

### Why

Backtest lets the system replay historical data before running paper runtime.

### Build

- historical replay loop
- same strategy/portfolio/risk/execution/accounting logic where practical
- later-bar fill rule
- cost assumptions
- report output

### Done When

Backtest outputs:

- config snapshot
- signal log
- target log
- order log
- fill log
- equity curve
- drawdown curve
- metrics
- rejected-order report

Rules:

- no same-bar execution
- no still-open candle logic
- no hidden cost assumptions

### Not Now

- no full research lab
- no parameter optimizer
- no ML model training

---

## Goal K: Paper Runtime

### Why

Paper runtime is the online loop that runs the virtual account against public market data.

### Build

- load config
- connect public data
- wait for closed 15m candle
- compute features
- generate signals
- build targets
- run risk gate
- create virtual orders/fills
- update account
- persist events
- recover after restart

### Done When

- runtime can process recorded closed-candle replay
- runtime can process a manual public-data one-cycle smoke
- runtime does not require API keys
- runtime does not submit real orders
- runtime persists decisions and account events
- runtime does not duplicate orders after restart

### Not Now

- no 14-day certification requirement for Code Complete
- no live trading
- no private account sync

---

## Goal L: Read-Only Dashboard/API

### Why

The user needs to see what the system is doing and why.

### Build

Read-only views for:

- account equity
- USDT cash
- positions
- realized PnL
- unrealized PnL
- latest signals
- virtual orders
- virtual fills
- rejected orders
- risk status
- runtime health

MVP stack:

```text
FastAPI
Jinja2/static page
polling JSON endpoints
```

### Done When

- dashboard can show current account state
- dashboard can show why the system bought or sold
- dashboard can show why an order was rejected
- API cannot manually submit orders
- API cannot change risk limits
- API cannot access private exchange data

### Not Now

- no React/Next/Vue full SPA
- no manual trading controls
- no real order endpoint

---

## Goal M: Core MVP Complete

### Why

Separate implementation completion from later research and long-running certification.

### Done When

Core MVP is complete when:

1. baseline verification passes
2. public data can be ingested or replayed
3. one strategy can produce `LONG/FLAT` decisions
4. portfolio targets are produced
5. risk gate approves or rejects actions
6. paper broker creates virtual orders and fills
7. virtual account updates cash, positions, PnL, and equity
8. backtest runs end-to-end
9. runtime replay smoke passes
10. dashboard is accessible
11. rejected orders and risk events are visible
12. no private API path exists
13. no real order path exists

### Verification

```bash
ruff check .
ruff format --check .
mypy --strict src/
lint-imports
pytest -m "not network" tests -q
python -m scripts.run_backtest --config configs/runtime/paper_runtime.yaml
python -m scripts.run_paper_runtime --config configs/runtime/paper_runtime.yaml --replay-smoke
```

### Not Required For Core MVP Complete

- 14-day wall-clock paper runtime
- research lab
- walk-forward study
- Monte Carlo
- PBO/DSR diagnostics
- HMM
- neural network
- genetic algorithm
- multi-strategy studio
- live trading

---

## Goal N: Paper Runtime Stability Run

### Status

Post-MVP validation gate.

### Why

Prove the system can run continuously after Core MVP is built.

### Done When

A true wall-clock paper runtime run completes the chosen certification period and meets its contract.

Recommended future default:

```text
14 calendar days
0 real order attempts
0 private API usage
0 critical runtime crashes
ledger reconciliation passes
all fills have fee/slippage records
all rejects have reason codes
```

This goal is not required for Core MVP implementation completion.

---

## Goal O: Research Lab

### Status

Post-MVP extension.

### Why

Research should improve and reject parameters after the trading system already runs end-to-end.

### Build Later

Possible research features:

- bounded parameter search
- walk-forward validation
- holdout testing
- cost stress testing
- Monte Carlo robustness checks
- trial ledger
- research report

### Rules

- research must not auto-deploy results into runtime
- research must not hide failed trials
- research must not expand search space after seeing results without recording a new experiment

This goal is not required for Core MVP implementation completion.

---

## Future Goals

### Future Goal P: HMM / ML Regime Research

Research-only until a new contract authorizes runtime use.

### Future Goal Q: Genetic Algorithm Parameter Research

Allowed only after research logging and backtest reproducibility are reliable.

### Future Goal R: Multi-Strategy Studio

Allowed only after one strategy runs end-to-end in paper runtime.

### Future Goal S: Read-Only Real Account Reconciliation

Requires private API and therefore requires a new explicit contract.

### Future Goal T: Live Trading Contract

Not authorized by this MVP. Requires a separate written contract, safety review, and explicit human approval.

---

## Final Rule

```text
Core MVP should be small enough to finish.
Architecture should be open enough to extend.
Advanced features must be added by contract, not by quietly expanding scope.
```
