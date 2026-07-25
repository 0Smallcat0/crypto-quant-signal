# Goal P experiment 10 pre-registration — ATR-scaled exits on the Donchian book

Status: **FROZEN on commit**. Written 2026-07-25, after the ATR exit
engine landed (commit 33f55e8, 78 backtest tests green) and before any
experiment-10 run. Written in the same sitting as the experiment-9 RUNS
but before their gate report exists — no experiment-9 DSR number was
available to steer this grid, and none of its Sharpe/MDD numbers appear
below as a threshold.

## Override recorded

Same standing operator authorization as experiment 9 (「預算很充足，你可以
一直跑」). All criteria are the statutory bars frozen long before today.

## Hypothesis

Across nine families, exit discipline is the only lever that has moved
Donchian Sharpe materially: experiment 7's mid_channel beat half_low by
0.09 on identical entries. The remaining gap from trial 88 (1.1821) to
the deflation bar (~1.25 at this N) is 0.07. Poluri (SSRN 2025, logged in
RESEARCH_LOG) specifies ATR-scaled Donchian exits: the stop floats at a
volatility-proportional distance below the channel high, so a trend gets
more room precisely when the tape is noisy — which a fixed mid-channel
floor cannot express.

This is a MECHANISM test on the one lever with demonstrated sensitivity,
which is what the 2026-07-23 N-arithmetic authorises; it is not a wrapper
re-sweep.

## Strategy definition (mechanical)

- Signal, universe, costs, window, allocation: **identical to trial 88** —
  Donchian 10/20/55/110, no regime gate, equal weighting, BTC/ETH
  pre-holdout, budgets 0.5/0.5, returns pinned to the registry window.
- Exit (`dc_exit = "atr_channel"`), per window w, when that window is ON:
  exit level = max(prior w closes) − `dc_atr_multiple` × ATR(`dc_atr_window`),
  where ATR is the Wilder true range (prior-close based) averaged over the
  window. Exit when the decision close falls below that level.
- ATR warmup falls back to the mid-channel level — never to a guessed
  floor, and never to "stay in".
- Entries are unchanged: a close strictly above the prior w-day max close.

**Declared deviation**: the source spec trails from the entry price; this
implementation trails from the channel high, which is stateless and
therefore replay-deterministic under the project's engine contract. No
result here may be reported as replicating the paper.

## Family grid (8 configurations, all registered)

- `dc_atr_window` ∈ {14, 28}
- `dc_atr_multiple` ∈ {2, 3, 4, 6}

The multiple sweeps the whole room-to-breathe dial from tight (2 ATR) to
loose (6 ATR); every arm binds by construction.

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe.

## Success criteria (ALL required, same full-registry gate report, N ≥ 125)

1. **Winner DSR ≥ 0.95** at full deflation.
2. **Winner max drawdown ≤ 51.93%.**
3. **Winner annualized turnover ≤ 53.1.**

Anything less on any criterion → registered negative.

## Informative read-outs (non-gating, declared now)

- Winner versus trial 88 (Sharpe 1.1821 / MDD 33.05% / turnover 13.92).
- Shape of the multiple dial: is there an interior optimum, or is the
  best arm at an endpoint (an endpoint winner is weaker evidence — the
  grid did not bracket the mechanism).
- Turnover versus looseness: a wider stop should trade less.

## Honesty clauses

- Registry N grows to ≥ 125; every DSR pays the larger deflation.
- A winner here does NOT inherit trial 88's robustness battery; it would
  need its own before any nomination.
- The October holdout, its fixed nominations, and the live contract are
  untouched by any outcome.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it.
