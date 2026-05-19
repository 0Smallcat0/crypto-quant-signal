# Crypto Quant Paper Trading Architecture

Version: `v0.8-readable-expandable`
Status: system foundation contract
Last updated: `2026-05-19`
Project: `Crypto Quant Paper Trading MVP v1.0`

---

## 0. Product In One Sentence

Build a crypto spot, long-only, 15-minute paper trading system where a `1000 USDT` virtual account follows system-generated decisions, records every virtual order/fill/PnL event, and shows the result in a read-only dashboard.

Plain language:

```text
The system watches the market every 15 minutes.
It uses real public market data.
It trades only inside a virtual account.
It can buy spot coins or hold USDT.
It never shorts, never uses leverage, and never sends real exchange orders in MVP v1.0.
```

---

## 1. How To Read This Document

This document is the system map, not a technical encyclopedia.

It defines:

- what the system is
- what the system must never do
- how the main modules connect
- what the MVP must build first
- where future features can be added

Detailed formulas, parameter ranges, database schemas, research diagnostics, and strategy experiments should live in separate files under:

```text
docs/contracts/
```

Do not put every future idea into this architecture file.

Plain language:

```text
主文件只講系統骨架。
細節合約放 docs/contracts/。
這樣文件好讀，但未來仍然能擴充。
```

---

## 2. Product Boundary

### 2.1 Core MVP Includes

MVP v1.0 must include:

- public market data
- 15-minute closed candle processing
- one active strategy
- virtual account starting with `1000 USDT`
- virtual buy/sell orders
- virtual fills
- cash, positions, realized PnL, unrealized PnL, fees, slippage, and equity tracking
- portfolio target generation
- pre-trade risk checks
- paper broker
- backtest engine
- paper runtime
- read-only dashboard/API
- audit trail for decisions, orders, fills, rejects, account changes, and risk events

### 2.2 Core MVP Does Not Include

MVP v1.0 must not include:

- real exchange order submission
- private exchange API
- real account balance reading
- API keys
- margin
- leverage
- borrowing
- lending
- derivatives
- perpetual futures
- short selling
- synthetic short exposure
- live trading
- canary trading
- production trading

### 2.3 Future But Not Core MVP

The architecture must leave room for these later, but they do not block Core MVP:

- research lab
- parameter search
- Monte Carlo robustness checks
- HMM regime filters
- neural network signals
- genetic algorithm optimizers
- multiple strategies
- multi-exchange data adapters
- read-only real account reconciliation
- live trading contract

Plain language:

```text
未來可以做，但第一版不要被它們拖住。
Core MVP 先讓一個虛擬帳戶能安全跑起來。
```

---

## 3. Hard Safety Rules

These are system rules, not strategy preferences.

| Rule | Meaning |
|---|---|
| Spot only | Trade only spot instruments. |
| Long/flat only | The system can hold coins or hold USDT. It cannot short. |
| No negative quantity | Positions and targets must never be below zero. |
| Sell only existing holdings | A sell can only reduce an existing long position. |
| Paper only | MVP orders are virtual ledger events, not exchange orders. |
| Public data only | MVP must not require API keys or private exchange endpoints. |
| Closed candle only | Strategy cannot use still-open candles. |
| Later execution | A signal from candle `t` can execute only after candle `t` closes. |
| Explicit costs | Paper fills must include fee and slippage assumptions. |
| Audit trail | Every decision and account change must be recorded. |

---

## 4. System Responsibility Split

The system must keep these responsibilities separate:

```text
Data          = gets and validates public market data
Features      = turns closed candles into useful numbers
Strategy      = says which symbols look attractive
Portfolio     = decides target weights
Risk          = decides whether an action is allowed
Paper broker  = simulates execution
Accounting    = records cash, positions, PnL, and equity
Runtime       = runs the loop online using public data
Backtest      = replays history using the same core logic
Dashboard     = shows what happened, read-only
```

Important rule:

```text
Strategy must not become the whole system.
```

Strategy must not:

- submit orders
- choose final order quantity
- bypass risk
- touch the virtual account ledger
- touch exchange clients directly
- read private account state

---

## 5. Main Pipeline

```text
Public market data
  -> Candle validation
  -> Closed 15m candle gate
  -> Universe selection
  -> Feature computation
  -> Strategy ranking
  -> Portfolio target generation
  -> Risk gate
  -> Paper broker
  -> Virtual fill model
  -> Virtual account ledger
  -> Dashboard/API
```

Backtest and runtime use the same logical pipeline.

| Mode | Data source | Clock | Fill rule |
|---|---|---|---|
| Backtest | historical public data | replay clock | simulated later-bar fill |
| Paper runtime | live public data | real clock | virtual fill from later public price |

---

## 6. MVP Default Choices

These are defaults, not permanent limitations.

| Area | MVP default | Future extension |
|---|---|---|
| Exchange data | Binance Spot public data | CCXT, other exchanges, paid data providers |
| Trading mode | Paper trading only | read-only account sync, live trading contract |
| Symbols | USDT spot pairs | other quote assets or exchanges by contract |
| Strategy | one active trend strategy | multiple strategy contracts |
| Portfolio | simple capped target weights | volatility weighting, risk parity, Black-Litterman |
| Storage | PostgreSQL-compatible runtime store, TimescaleDB recommended | alternative store adapter by contract |
| Dashboard | read-only FastAPI + simple web page | richer UI after MVP |
| Research | not required for Core MVP | research lab after system runs end-to-end |

Plain language:

```text
MVP 只實作一條預設路徑。
但架構不要寫死，未來可以替換資料源、策略、投組、儲存和 dashboard。
```

---

## 7. First Active Strategy

### 7.1 Strategy Role

The first active strategy should be:

```text
Large Liquid Trend 15
```

Chinese display name:

```text
大幣高流動性 15 分鐘趨勢策略
```

Technical note:

```text
This is a long-only time-series momentum style strategy.
The main docs call it a trend strategy to keep the system easy to understand.
Detailed formulas belong in docs/contracts/STRATEGY_LARGE_LIQUID_TREND_15.md.
```

Plain language:

```text
只買大型、高流動性、趨勢變強的幣。
市場不好時少買或不買。
不要因為每 15 分鐘有新 K 線就亂交易。
```

### 7.2 Strategy Output

The strategy outputs only:

```text
symbol
signal: LONG | FLAT
score
reason_codes
generated_at_bar_close
executable_from_next_bar
```

The strategy does not output:

- final order quantity
- final cash amount
- exchange order
- private API action

### 7.3 Strategy Expansion Rule

Only one strategy is active in Core MVP.

Future strategies are allowed, but each new strategy must have:

- its own strategy contract
- its own tests
- declared inputs and outputs
- clear stop rules
- no direct order submission
- no private API dependency

---

## 8. Data Source Contract

### 8.1 MVP Data Source

Primary MVP source:

```text
Binance Spot public REST + Binance Spot public WebSocket
```

Allowed public data:

- historical candles
- public kline streams
- exchange information
- symbol filters
- public ticker data
- public book ticker
- public depth snapshots

Forbidden in MVP:

- private REST endpoints
- private WebSocket streams
- real account endpoints
- real balance endpoints
- real order endpoints
- API key signing

### 8.2 Candle Rule

Every candle used by the system must carry:

```text
symbol
timeframe
open_time
close_time
open
high
low
close
volume
quote_volume
is_closed
source
received_at
```

Rules:

- features use only closed candles
- strategy uses only feature snapshots built from closed candles
- if candle closure is unclear, treat it as not usable
- all timestamps are UTC timezone-aware
- internal symbols use Binance format, such as `BTCUSDT`
- display symbols may use slash format, such as `BTC/USDT`

---

## 9. Universe Contract

Universe means the list of symbols that the strategy is allowed to consider.

MVP default:

```text
Use large, mature, liquid Binance Spot USDT pairs.
```

Main rules:

- symbol must be spot
- quote asset must be USDT
- symbol must be trading
- stablecoin pairs are excluded
- fiat proxy pairs are excluded
- leveraged tokens are excluded
- symbol must have enough closed 15m history
- symbol must have enough recent quote volume

The exact ranking rule belongs in:

```text
docs/contracts/UNIVERSE_CONTRACT.md
```

Plain language:

```text
策略可以很積極，但不要在冷門幣和奇怪交易對上冒險。
```

---

## 10. Storage Contract

The system needs storage so it can restart safely and explain what happened.

Runtime must persist:

- config snapshot
- universe snapshot
- candle events
- feature snapshots
- strategy signals
- portfolio targets
- risk decisions
- virtual orders
- virtual fills
- virtual account snapshots
- health events

MVP default:

```text
PostgreSQL-compatible runtime database.
TimescaleDB is recommended for local development and time-series data.
```

Rules:

- ledger-like tables must be append-only
- schema changes must be tracked
- runtime must not silently lose events
- SQLite may be used for unit tests or temporary fixtures, not as the formal runtime store unless a storage contract explicitly allows it

Plain language:

```text
系統重啟後不能忘記之前做過什麼。
每一筆虛擬訂單、成交、拒單和帳戶變化都要查得到。
```

---

## 11. Core Modules

### 11.1 `src/domain/`

Purpose:

```text
Define the shared language of the system.
```

Examples:

- symbol
- timeframe
- candle
- signal
- position
- order intent
- virtual order
- virtual fill
- account snapshot
- risk decision

Rules:

- `Signal` can only be `LONG` or `FLAT`
- money, price, quantity, fees, and fills use `Decimal`
- negative position is impossible
- sell-more-than-holding is invalid
- domain must not import data, strategy, risk, runtime, database, or scripts

### 11.2 `src/config/`

Purpose:

```text
Load and validate run settings.
```

Rules:

- configs are typed
- configs are reproducible
- configs must not contain secrets
- MVP configs must reject real trading, private API, shorting, margin, and leverage
- each run stores a config snapshot

### 11.3 `src/data/`

Purpose:

```text
Fetch, validate, store, and serve public market data.
```

Responsibilities:

- get historical candles
- listen for closed runtime candles
- detect gaps
- detect duplicates
- detect stale data
- fetch public symbol filters
- build universe snapshots
- expose clean data to features

### 11.4 `src/features/`

Purpose:

```text
Turn closed candles into neutral features.
```

Examples:

- returns
- trend
- recent high/low
- volume ratio
- volatility
- BTC market condition

Rules:

- features do not trade
- features do not size positions
- features do not read account state
- features must be point-in-time

### 11.5 `src/strategies/`

Purpose:

```text
Turn features into LONG/FLAT signals and rankings.
```

Rules:

- strategy returns signals and reason codes
- strategy does not create orders
- strategy does not size final quantity
- strategy does not bypass risk
- strategy parameters come from config or a strategy contract

### 11.6 `src/portfolio/`

Purpose:

```text
Turn ranked signals into target positions.
```

MVP default:

- hold up to a few strong candidates
- cap single-symbol exposure
- allow cash
- avoid unnecessary churn

Rules:

- no negative targets
- no short exposure
- no direct order submission

### 11.7 `src/risk/`

Purpose:

```text
Block invalid or dangerous virtual actions.
```

Risk checks include:

- no short exposure
- no negative quantity
- sell cannot exceed current holdings
- no trading on stale data
- no same-bar execution
- exchange filter checks
- minimum notional checks
- drawdown and pause checks
- trailing stop checks

Risk output:

```text
APPROVED | REJECTED | PAUSED | STOPPED
reason_codes
```

### 11.8 `src/execution/`

Purpose:

```text
Simulate order validation and fills.
```

Rules:

- paper broker accepts only risk-approved virtual orders
- paper broker never sends real orders
- paper broker applies fee and slippage assumptions
- every fill records cost information
- invalid orders are rejected with reason codes

### 11.9 `src/accounting/`

Purpose:

```text
Maintain the virtual account.
```

Tracks:

- cash
- positions
- average entry price
- realized PnL
- unrealized PnL
- fees
- equity
- drawdown
- ledger events

Rules:

- ledger is append-only
- every cash change must be explained
- every position change must be explained
- account cannot have negative cash or negative positions unless a future contract explicitly allows a different accounting mode; MVP does not

### 11.10 `src/backtest/`

Purpose:

```text
Replay historical public data using the same core logic as runtime.
```

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

- no same-bar fills
- include fee and slippage assumptions
- use the same strategy, portfolio, risk, execution, and accounting components as runtime where practical

### 11.11 `src/runtime/`

Purpose:

```text
Run the paper trading loop with public market data.
```

Runtime loop:

```text
load config
connect public data
wait for closed candle
compute features
generate signals
build targets
run risk gate
paper execute
update account
persist events
wait for next candle
```

Runtime must be:

- restartable
- idempotent
- auditable
- safe on stale data
- public-data only

### 11.12 `src/api/` and `src/monitoring/`

Purpose:

```text
Show what the system is doing.
```

MVP dashboard is read-only.

It should show:

- account
- cash
- positions
- PnL
- latest signals
- virtual orders
- virtual fills
- rejected orders
- risk status
- runtime health

It must not include:

- manual buy button
- manual sell button
- real order endpoint
- private API controls
- API key management

---

## 12. Repository Skeleton

```text
pyproject.toml
requirements/
  constraints-dev.txt
docker-compose.yml
.gitignore
README.md
AGENTS.md
GOALS.md
crypto_quant_architecture.md

src/
  domain/
  config/
  data/
  features/
  strategies/
  portfolio/
  risk/
  execution/
  accounting/
  backtest/
  runtime/
  monitoring/
  api/

configs/
  data/
  strategy/
  portfolio/
  risk/
  execution/
  runtime/
  storage/
  api/

docs/
  contracts/
  reports/

scripts/
  ingest_public_ohlcv.py
  run_backtest.py
  run_paper_runtime.py
  make_report.py

tests/
  domain/
  config/
  data/
  features/
  strategies/
  portfolio/
  risk/
  execution/
  accounting/
  backtest/
  runtime/
  api/
```

`src/research/` is intentionally not required for Core MVP. It can be added after Core MVP through a research contract.

---

## 13. Extension Points

Future features should be added through contracts, not by rewriting the system.

| Future feature | Add through |
|---|---|
| New strategy | `docs/contracts/STRATEGY_<NAME>.md` |
| New exchange/data source | `docs/contracts/DATA_ADAPTER_<NAME>.md` |
| Research lab | `docs/contracts/RESEARCH_LAB.md` |
| HMM or ML model | `docs/contracts/MODEL_<NAME>.md` |
| Multi-strategy allocation | `docs/contracts/MULTI_STRATEGY_PORTFOLIO.md` |
| Read-only real account sync | `docs/contracts/REAL_ACCOUNT_READONLY.md` |
| Live trading | `docs/contracts/LIVE_TRADING.md` |

Important:

```text
Future extension is allowed.
Unplanned scope expansion during Core MVP is not allowed.
```

---

## 14. MVP Completion Definition

Core MVP is complete when:

- public market data can be ingested or replayed
- closed 15m candles drive the system
- one strategy produces LONG/FLAT decisions
- portfolio targets are created
- risk gate approves or rejects actions
- paper broker creates virtual orders and fills
- virtual account updates cash, positions, PnL, and equity
- backtest runs end-to-end
- runtime smoke runs from recorded closed candles
- dashboard shows account, positions, signals, orders, fills, rejects, and health
- no real order path exists
- no private API path exists
- baseline tests pass

Release certification, long-running paper runtime, and research lab validation are later gates, not required for Core MVP implementation completion.

---

## 15. Design Principle

```text
Keep the architecture expandable.
Keep the main documents readable.
Keep Core MVP narrow.
Move advanced details into contracts.
Never weaken safety rules.
```
