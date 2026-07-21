# Goal P experiment 5 pre-registration — directional regime gate family

Status: **FROZEN on commit**. Written 2026-07-21, before any engine work or
run for this family. Hypothesis, grid, selection rule, and success criteria
may not change once the first member runs. A failed family is a registered
negative.

## Drift-guard override (recorded, not hidden)

Second same-sitting override today, again by explicit operator order:
「不用等明晚，直接接著寫實驗 5 的 pre-registration 然後跑」. Neutralized
the same way as experiment 4's: **every success criterion is the statutory
bar frozen before today** (absolute 0.95 DSR gate; trial 4's 51.93% MDD;
3×17.69 turnover). No number first observed today (experiment 4's table,
trial 29's N=53 DSR) appears as a threshold. Architecture choice is
sequential refinement, declared legitimate since experiment 2.

## Hypothesis

Experiment 4 established that VOLATILITY is the wrong conditioning
variable for cs momentum — profits concentrate in high-vol regimes, so a
vol target de-risks exactly when the strategy earns. The remaining
practitioner-standard lever (RESEARCH_LOG 2026-07-21: regime-filtered
momentum; 200-DMA regime marker corroboration) is DIRECTIONAL
conditioning: hold the cs book only when the tape is structurally bullish,
sit fully in cash when it is bearish. Direction, unlike volatility, does
not correlate one-for-one with the strategy's earning periods — 2021-style
bull volatility keeps the book on; 2022-style bear trends switch it off.

## Strategy definition (mechanical)

- Base selection: experiment 3's winning architecture, fixed — K=2,
  lookback 180d, monthly cadence, absolute filter ON, min pool 4,
  13-symbol pre-holdout universe, decision floor 2018-03-05, identical
  costs and window to every registered trial. No vol overlay (experiment 4
  closed that arm).
- Regime gate: a boolean per decision day multiplying the whole book (or a
  symbol's slot) by 0 or 1. Gate inputs use only closes up to and
  including the decision close (no lookahead).
  - SMA basis `btc`: gate compares BTCUSDT's close to BTCUSDT's
    `sma_window`-day simple moving average; one switch for the whole book
    (BTC as the market-regime proxy).
  - SMA basis `per_symbol`: each symbol is gated by its own SMA; a symbol
    with fewer than `sma_window` closes is gated OFF (no data → no
    position, the conservative side).
- Hysteresis (whipsaw guard): OFF→ON requires close > SMA × (1 + band);
  ON→OFF requires close < SMA × (1 − band). Band 0 degenerates to the
  plain crossover. Gate state machines are per basis symbol.
- Gate cadence: `daily` re-evaluates every decision day — the gate can
  pull the book to cash mid-month (the crash-exit case that monthly
  selection alone cannot express; execution-on-drift already lands these
  orders next bar). `monthly` evaluates only on selection rebalance days
  and freezes between them.
- Gated weight = cs weight × gate ∈ {0, weight}. Raw cs selection state
  is never rewritten (same doctrine as the overlay experiments).

## Family grid (16 configurations, all registered)

- sma_window ∈ {100, 200}
- basis ∈ {btc, per_symbol}
- hysteresis band ∈ {0, 0.02}
- gate cadence ∈ {daily, monthly}

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 69)

1. **Winner DSR ≥ 0.95** — the statutory gate-4 bar at full N≥69
   deflation.
2. **Winner max drawdown ≤ 51.93%** — trial 4's live-baseline MDD,
   unchanged anchor since experiment 2.
3. **Winner annualized turnover ≤ 53.1** — 3 × trial 4's 17.69, unchanged
   since experiment 3.

Anything less on any criterion → registered negative. Passing all three
still does NOT trigger the loop's stop condition unless candidates-PBO
≤ 0.05 holds in the same report; October's holdout nominations remain
untouched either way.

## Informative read-outs (non-gating, declared now)

- Gate engagement: fraction of decision days gated off, per arm; equity
  path through 2018, 2020-03, 2022, 2025-H1 stress windows.
- btc vs per_symbol basis (market proxy vs idiosyncratic gating).
- Hysteresis value: whipsaw count with and without the 2% band.
- Daily vs monthly gate cadence: does mid-month crash exit earn its extra
  turnover?
- Winner's daily-return correlation with trial 4 (diversification
  read-out, carried forward).

## Engine prerequisite (work item, not a degree of freedom)

New `cs_gate_*` parameters (validated in BacktestParameters) and a gate
evaluation step in the cs path, applied AFTER selection and INSTEAD OF the
vol overlay (both simultaneously is out of scope for this family).
Implementation and tests land before the first family run; runs happen on
a clean committed tree.

## Honesty clauses

- Registry N grows to ≥ 69; every DSR pays the larger deflation. If that
  sinks the family, the verdict stands.
- Universe survivorship bias carries over unchanged; the holdout remains
  the single arbiter.
- Gate rows carry full cs_* + gate parameters in machine-readable registry
  fields (the serialization fix predates this family).
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.
