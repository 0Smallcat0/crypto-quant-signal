# Engineering decisions — and how to verify each one

The feature list says what this system does. This file records the decisions
that are invisible from the feature list: what problem each one solves, the
trade-off accepted, and **where in the repository you can verify the claim**.
Nothing here asks to be believed on faith — every item points at code, tests,
or a signed-off audit report.

---

## 1. Notifications are exactly-once across crashes and outages

**Problem.** The runtime may die at any instant — mid-cycle, mid-delivery,
mid-write. A duplicated "buy" push is a real-money hazard for the human
following it; a silently dropped one breaks the scoreboard's honesty.

**Decision.** Persist the notification event *before* any delivery attempt,
then deliver, then persist a `delivered:` marker. A delivery failure leaves
the marker absent, so the next cycle (or a same-day rerun) retries; a crash
after delivery but before the marker is the only at-least-once window, and it
is bounded to one message.

**Where to look.** `src/runtime/engine.py` (`_flush_undelivered`);
`tests/runtime/test_signal_runtime.py::test_restart_duplicates_no_orders_and_no_notifications`,
`::test_delivery_outage_never_corrupts_the_cycle_and_retries`.

## 2. Fill events double as crash checkpoints

**Problem.** The 2026-07-03 adversarial audit proved (with a crash probe)
that a mid-cycle crash after a paper fill lost the fill from the scoreboard:
restore used only end-of-cycle snapshots while order-key dedup skipped
re-execution — cash said 1000, control said ~0 cash and two positions.

**Decision.** Every fill event embeds a full account-state checkpoint.
Restore takes the newest cycle-**or**-fill checkpoint; an order without a
fill is skipped *without* being marked executed, so a fresh order retries on
the next cycle's idempotency key. Recovery re-converges bit-for-bit with an
uninterrupted run.

**Trade-off.** Redundant state in the log (each fill carries the account) in
exchange for a two-level recovery lattice with no reconciliation pass.

**Where to look.** `src/runtime/engine.py` (`_latest_checkpoint`);
`tests/runtime/test_signal_runtime.py::test_mid_cycle_crash_after_fill_loses_nothing`;
`docs/reports/SYSTEM_AUDIT_2026-07-03.md` finding 1.

## 3. The event store quarantines torn tails instead of dying — or guessing

**Problem.** Power loss mid-append leaves a half-written final line in a
JSONL log. Refusing to start is an outage; silently skipping bad lines is
corruption laundering.

**Decision.** A torn **final** line — the only artifact an interrupted append
can produce — is treated as never-persisted and preserved in a `.torn`
sidecar for forensics. Invalid JSON anywhere else fails loudly, because that
is not a crash artifact; it is corruption.

**Where to look.** `src/runtime/store.py` (`_quarantine_torn_tail`);
`tests/runtime/test_signal_runtime.py::test_torn_final_line_is_quarantined_not_fatal`.

## 4. Two independently written engines, reconciled to the last Decimal digit

**Problem.** A backtest engine that shares code with the live engine inherits
its bugs; one that diverges silently makes every backtest a lie about what
the runtime would have done.

**Decision.** The backtest engine (`src/backtest/`) and the signal runtime
(`src/runtime/`) are separate implementations of the same contract. Replaying
identical candles through both must produce **bit-identical** Decimal equity
— `14221.27753677073000` on the audited trial. The audit used this property
to catch real divergence bugs (boundary-day inclusion, cost accounting)
before the paper period started.

**Trade-off.** Two engines cost double maintenance; that is the price of
having an oracle for either one.

**Where to look.** `docs/reports/SYSTEM_AUDIT_2026-07-03.md`;
`python -m scripts.run_paper_runtime --replay-smoke --store <path>` vs
`python -m scripts.run_backtest`.

## 5. Overfitting statistics are a gate, not a chapter in a report

**Problem.** Every retail strategy repo has a beautiful in-sample equity
curve. Iterated out-of-sample testing is not out-of-sample; unregistered
trials make N a fiction and every Sharpe ratio inflated.

**Decision.** Qualification is six sequential gates: append-only trial
registry (unregistered backtests are void *by construction*), a 1,000-day
data floor, PBO ≤ 0.05 via CSCV (S=16, 12,870 splits), Deflated Sharpe ≥
0.95 adjusted for the true trial count, a single-use locked holdout
(spending it is irreversible), and ≥3 months of live paper with measured
costs. The gate machinery is extracted as a zero-dependency package
([trialgate](https://github.com/0Smallcat0/trialgate)), and it has one
registered FAIL on record — [our own Taiwan-market
adaptation](https://github.com/0Smallcat0/tw-stock-trading), killed by its
pre-registered stop rule.

**Where to look.** `src/backtest/`; `tests/backtest/test_validation_gate.py`
(holdout single-use is tested: the second unlock attempt fails);
`docs/reports/research/trial_registry.jsonl` (committed, append-only).

## 6. Illegal states are unrepresentable, and the boundaries are compiled in

**Problem.** "Be careful" does not survive contributors, refactors, or
2 a.m. fixes.

**Decision.** `Signal` has two members — `LONG` and `FLAT`; a short position
cannot be expressed, let alone taken. Money is `Decimal` end-to-end (no
float ever touches an account). Naive datetimes are rejected at the store
boundary. Config is frozen Pydantic with `extra="forbid"`, and safety flags
(`real_orders_enabled`, `private_api_enabled`, `leverage_enabled`, …) are
validators that **reject `True`** — enabling them is a code change, not a
config change. Thirteen import-linter contracts make the layering
(domain imports nothing; strategy cannot see execution; API is read-only
presentation) a CI-enforced property instead of a convention.

**Where to look.** `src/domain/`; `src/config/models.py`
(`_reject_enabled_flag`); `.importlinter`; CI runs `lint-imports` on every
push.

## 7. No lookahead — by construction at the data layer, and proven by tests

**Problem.** Most backtest edges are timestamp bugs.

**Decision.** Still-open candles are visible to monitoring but blocked from
strategy input at the data layer; a signal computed on candle *t* can only
fill at *t+1*'s open (the backtest engine and the runtime share this
next-bar-open rule); features at close *t* use only closes ≤ *t*; decisions
require a 200-close warmup. Each rule has a test whose failure mode is the
bug it guards against.

**Where to look.**
`tests/data/test_public_market_data.py::test_still_open_rest_kline_is_visible_and_blocked_from_strategy_input`;
`tests/backtest/test_backtest_engine.py` (fill lands exactly at next bar's
open); `tests/runtime/test_signal_runtime.py` (warmup, stale-data halt).

## 8. The product's shape follows behavioral evidence, not engagement

**Problem.** The dominant failure mode of a followable signal system is not
the signal — it is the follower. Dollar-weighted investor returns trail
time-weighted fund returns, and the gap is largest exactly where this system
lives: high volatility, manual execution.

**Decision.** Adversarially verified research (three-vote verification over
109 claims; 23 survived) drove product shape: **no leaderboard, no social
features, no one-click copy** (the literature shows these causally amplify
risk-taking); manual execution with at most one command per day; every push
message is self-sufficient (whole-portfolio target embedded, so a missed
message never requires history replay); a fixed drawdown-expectation anchor
appears once the scoreboard passes −20%; liveness monitoring is a dead-man
switch on an independent channel, so silence in the command channel keeps
meaning "do nothing today".

**Where to look.** `docs/research/SIGNAL_DESIGN_RESEARCH.md` (English
summary: `docs/research/SIGNAL_DESIGN_RESEARCH_EN.md`);
`docs/plans/PRODUCT_OPTIMIZATION_PLAN.md` (per-claim citations and rejected
alternatives); `src/notify/messages.py` and its tests.

## 9. The README quickstart is a CI contract

**Problem.** Quickstarts rot. A visitor whose first command fails does not
file an issue; they leave.

**Decision.** CI has a dedicated job that runs the README verbatim — bare
`pip install -e .` (no dev extras, no constraints, no Docker) and
`python -m scripts.run_demo --no-serve` — and asserts the deterministic
output: 713 cycles, 248 commands, final equity `1145.05288738567`. The demo
replays bundled **real** BTC/ETH candles that deliberately end inside a −27%
drawdown, and its dashboard labels itself an offline replay so replayed
cycles can never masquerade as live qualification days.

**Where to look.** `.github/workflows/ci.yml` (`quickstart-demo` job);
`demo/candles/README.md`; `tests/scripts/test_run_demo.py`.

---

## What this project deliberately is not

There is no path here to an execution product: real order submission,
private-API access, and key custody are **permanently excluded by product
definition** (`AGENTS.md` §13.4), and the config layer rejects the flags at
validation time. That is not a missing feature; it is the point. The
reusable assets are the verification methodology (packaged as
[trialgate](https://github.com/0Smallcat0/trialgate)), the audit trail, and
a runnable demonstration that honest infrastructure for a strategy is
buildable by one person — whether or not the strategy itself survives its
own gate in October 2026.
