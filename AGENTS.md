# AGENTS.md

Version: `v0.8-readable-expandable`
Status: agent and contributor operating contract
Last updated: `2026-05-19`
Project: `Crypto Quant Paper Trading MVP v1.0`

---

## 0. Purpose

This file tells AI agents, coding assistants, and contributors how to work in this repository.

The project is being rebuilt from zero as a paper trading MVP:

```text
1000 USDT virtual account
15-minute public market data
spot long-only decisions
virtual buy/sell orders
no real exchange orders
```

The goal is to build a system that can actively trade virtually while remaining safe, auditable, and expandable.

Plain language:

```text
不要把系統做成死路。
也不要把 MVP 做成研究平台或技術百科。
先完成可運行核心，再用合約擴充。
```

---

## 1. Golden Rule

```text
Keep Core MVP narrow.
Keep architecture expandable.
Keep documents readable.
Never weaken safety rules.
```

Agents must not add future features just because the architecture has a place for them.

If a feature is not in the current goal, leave an interface or note, but do not implement it.

---

## 2. Non-Negotiable Safety Rules

### 2.1 Secrets

Do not create, edit, print, log, commit, or expose:

- API keys
- secret keys
- private keys
- seed phrases
- passwords
- webhook tokens
- `.env` files

MVP v1.0 should not need secrets.

If secrets are introduced in a later non-MVP contract, they must be loaded only from environment variables or approved secret management.

### 2.2 Trading Scope

Allowed in MVP:

- spot crypto
- long exposure
- flat exposure
- public market data
- backtesting
- paper trading through virtual account ledger

Forbidden in MVP:

- margin
- leverage
- borrowing
- lending
- perpetual futures
- derivatives
- short exposure
- synthetic short exposure
- real order submission
- private exchange API
- real account balance access

### 2.3 Signal And Position Rules

- `Signal` may only be `LONG` or `FLAT`.
- Do not add `SHORT`.
- `Position.quantity` must never be negative.
- `TargetPosition.quantity` must never be negative.
- `SELL` can only reduce an existing long spot position.
- Selling more than the current long position is invalid.

### 2.4 Paper Trading Rule

Paper trading is allowed only as:

```text
virtual order
virtual fill
virtual account ledger
```

Paper trading must not:

- sign exchange requests
- send real orders
- read real balances
- use private API keys
- mutate a real exchange account

---

## 3. Current MVP Boundary

### 3.1 Build

```text
public market data
  -> closed 15m candle gate
  -> feature pipeline
  -> one active strategy
  -> portfolio targets
  -> risk gate
  -> paper broker
  -> virtual account
  -> read-only dashboard/API
```

### 3.2 Do Not Build In Core MVP

```text
real trading bot
private exchange client
live account manager
research lab as a blocker
multi-strategy production allocator
unbounded optimizer
HMM or neural network strategy
```

### 3.3 Initial Virtual Account

```text
initial_cash: 1000 USDT
mode: paper
real_orders: disabled
private_api: disabled
```

---

## 4. Plain-Language Design Rule

The system must follow this division of responsibility:

```text
strategy = decides what looks attractive
portfolio = decides how much to target
risk = decides whether the action is allowed
paper broker = simulates execution
accounting = records what happened
```

Do not let strategy become the whole system.

Strategy must not:

- submit orders
- decide final execution quantity
- bypass risk
- touch account ledger directly
- touch exchange clients directly

---

## 5. Architecture Rules

### 5.1 `src/domain/`

Domain is the shared type layer.

It must not import:

- business packages
- runtime
- backtest
- scripts
- exchange adapters
- database clients

### 5.2 Business Packages

Business packages include:

```text
src/data/
src/features/
src/strategies/
src/portfolio/
src/risk/
src/execution/
src/accounting/
src/monitoring/
```

A business package may import:

- `src.domain`
- itself
- approved third-party libraries

Business packages should not directly import unrelated business packages unless the architecture document explicitly allows it.

Composition belongs in:

```text
src/backtest/
src/runtime/
```

### 5.3 `scripts/`

Scripts must remain thin CLI wrappers.

Scripts may:

- parse command arguments
- load config
- call application entry points
- print summary output

Scripts must not contain:

- strategy logic
- sizing logic
- risk logic
- execution logic
- accounting logic
- exchange business logic

---

## 6. Data And Timing Rules

### 6.1 Candle Rules

- Use only closed candles for feature and signal generation.
- Still-open candles must not be used for strategy decisions.
- Store candle close status when available.
- If close status is unclear, infer conservatively.
- Runtime candle closure should come from Binance Spot public kline closure fields when available.

### 6.2 Symbol And Time Rules

- Internal symbols use Binance native format, for example `BTCUSDT`.
- Display symbols may use slash format, for example `BTC/USDT`.
- Store `base_asset` and `quote_asset` explicitly.
- All storage, config, report, API, and runtime timestamps must be UTC timezone-aware.
- Naive datetimes are forbidden.

### 6.3 Execution Timing

- A feature computed at candle close may use data available at that close.
- A signal produced from candle `t` can only execute after candle `t` has closed.
- Backtest must not fill on the same candle that created the signal.
- Runtime paper fills must use a later public market price.

### 6.4 Lookahead Prevention

Stop and report if code:

- uses future candles
- uses target returns as features
- uses future universe membership
- uses a candle before it is closed
- backfills missing data in a way that leaks future information
- treats any latest incomplete OHLCV candle as closed

---

## 7. Core MVP Strategy Rules

The first active strategy is a readable trend strategy:

```text
Large Liquid Trend 15
大幣高流動性 15 分鐘趨勢策略
```

It may also be described technically as a long-only time-series momentum style strategy, but avoid unnecessary jargon in the main documents.

Default behavior:

```text
Check every 15 minutes.
Trade only when the signal is strong enough.
Let strong positions run.
Exit weak positions.
Avoid flip-flopping.
```

Do not hard-code parameters in business logic. Use config or strategy contract values.

Do not add additional active strategy candidates unless a new goal and contract authorize them.

---

## 8. Cost And Execution Rules

Paper execution must include costs.

Minimum cost components:

```text
fee
slippage
rounding
```

If spread, impact, or latency are modeled, record them clearly and do not double count them.

Execution rounding rules:

```text
quantity must respect exchange-like step size
cash_after_order must never be negative
buy orders must reserve estimated fee and slippage cash
dust positions may exist but must never become negative
reject after rounding if minimum notional is not satisfied
```

---

## 9. Runtime Rules

Paper runtime must be:

- restartable
- idempotent
- auditable
- public-data only
- safe on stale data
- safe on duplicate events
- safe on partial failure

Runtime must persist:

- config snapshot
- universe snapshot
- candle events
- feature snapshots
- signals
- targets
- risk decisions
- virtual orders
- virtual fills
- account snapshots
- health events

Runtime must not:

- depend on private API
- need API keys
- submit real orders
- continue trading on stale data
- duplicate orders after restart

---

## 10. Storage Rules

Runtime needs a real event store so the system can restart and explain what happened.

MVP default:

```text
PostgreSQL-compatible runtime storage.
TimescaleDB is recommended for local development.
```

SQLite is allowed only for unit tests and temporary fixtures unless a new storage contract says otherwise.

Local development credentials in `docker-compose.yml` may be explicit dummy credentials, for example:

```text
POSTGRES_USER=crypto
POSTGRES_PASSWORD=crypto_dev_only
POSTGRES_DB=crypto_quant
```

These are local-development credentials, not production secrets.

---

## 11. Dashboard/API Rules

MVP API is read-only.

Allowed views:

- account
- positions
- signals
- virtual orders
- virtual fills
- rejected orders
- risk status
- runtime health
- data freshness

Forbidden endpoints/actions:

- manual buy
- manual sell
- real order submit
- API key management
- private exchange account access
- changing risk limits from public API

MVP dashboard should stay simple:

```text
FastAPI
Jinja2 or static HTML
browser polling JSON endpoints
```

Do not introduce a full frontend framework unless a later goal authorizes it.

---

## 12. Research Rules

Research is not a Core MVP blocker.

Allowed after Core MVP through a research contract:

- bounded parameter search
- walk-forward validation
- holdout testing
- cost stress testing
- Monte Carlo robustness checks
- trial ledger
- research report

Forbidden in Core MVP:

- full genetic algorithm optimizer
- HMM regime engine
- neural network strategy
- reinforcement learning
- unlimited parameter search
- multi-strategy auto-selection
- automatic runtime deployment from research winners

Anti-overfitting rule:

```text
Research exists to reject fragile parameters, not to find magical parameters.
```

---

## 13. Extension Rules

Future features are allowed only by explicit contract.

### 13.1 Adding A New Strategy

Requires:

- new strategy contract
- tests
- declared inputs
- declared outputs
- no direct orders
- no private API
- no risk bypass

### 13.2 Adding A New Data Source

Requires:

- data adapter contract
- public/private boundary declaration
- closed-candle proof
- timestamp rules
- tests

### 13.3 Adding Research Lab

Requires:

- research contract
- trial ledger rules
- reporting rules
- no automatic runtime deployment

### 13.4 Adding Live Trading

Requires:

- separate live trading contract
- explicit human approval
- secret handling plan
- order submission safety plan
- kill switch plan

Live trading is not authorized by MVP v1.0.

---

## 14. Testing And Verification

### 14.1 General Rule

Use tests to prove behavior. Do not rely on comments or assumptions.

Prefer narrow tests first, then broader tests.

### 14.2 Required Baseline Checks

Before claiming Core MVP complete:

```bash
ruff check .
ruff format --check .
mypy --strict src/
lint-imports
pytest -m "not network" tests -q
```

Unit tests and CI tests must not hit Binance or any external network.

Public-network smoke tests must be explicit manual checks marked with:

```text
pytest.mark.network
```

### 14.3 Required Test Themes

Always test:

- no `SHORT` signal
- no negative position
- no sell greater than current holdings
- no still-open candle signal
- no same-bar execution
- no order below minimum notional
- no order violating exchange filters
- no trading on stale data
- no duplicate order after runtime restart
- paper broker never calls private API
- virtual account ledger balances after fills

---

## 15. Git And Change Discipline

Goal A must initialize the repository:

```text
git init
create .gitignore
create main branch
create pyproject.toml
create requirements/constraints-dev.txt
create docker-compose.yml
create src/, tests/, configs/, docs/contracts/ scaffold
commit the base contract documents and scaffold as the initial commit
do not configure a remote
do not push
```

### 15.1 Keep Diffs Reviewable

Do not mix unrelated concerns in one commit.

Examples:

- Do not modify strategy and database schema in the same commit unless the goal requires it.
- Do not modify dashboard and execution logic in the same commit.
- Do not add a future research feature while working on Core MVP runtime.

### 15.2 Commit Message Format

Use decision-record style:

```text
<intent line>

Constraint: <constraint>
Rejected: <alternative> | <reason>
Confidence: <low|medium|high>
Scope-risk: <narrow|moderate|broad>
Directive: <future warning>
Tested: <verification run>
Not-tested: <known gaps>
```

Do not add `Co-authored-by: OmX` unless the human explicitly requests that convention.

---

## 16. Stop Conditions

Stop and report if a task requires:

- storing or exposing secrets
- enabling real order submission
- using private exchange API in MVP
- adding leverage, margin, derivatives, or short exposure
- weakening risk rules to make a bad action pass
- using still-open candles for signals
- hiding a failed verification result
- changing universe or cost assumptions after seeing results without recording a new contract
- adding research, ML, HMM, GA, or live trading during Core MVP without authorization

---

## 17. Final Instruction To Agents

```text
Build the Core MVP first.
Keep advanced paths possible.
Do not implement advanced paths early.
Make every action testable, explainable, and auditable.
```
