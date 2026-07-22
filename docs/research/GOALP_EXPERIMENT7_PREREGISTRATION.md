# Goal P experiment 7 pre-registration — Donchian breakout ensemble (new signal space)

Status: **FROZEN on commit**. Written 2026-07-22, before any engine work or
run for this family. Hypothesis, grid, selection rule, and success criteria
may not change once the first member runs. A failed family is a registered
negative.

## Drift-guard override (recorded, not hidden)

Fourth same-sitting override, by operator order 「繼續找」 after the
experiment-6 result closed the cs-momentum lineage and posed the fork
(new signal space vs consolidate). Neutralized as before: **every success
criterion is the statutory bar frozen long before today** (absolute 0.95
DSR gate; trial 4's 51.93% MDD; 3×17.69 turnover). No number first
observed in experiments 3-6 appears as a threshold.

## Hypothesis

The cs-momentum lineage is closed (64 arms; the two statutory bars never
met in one configuration). The next EXTERNALLY-EVIDENCED signal space in
RESEARCH_LOG is the Donchian breakout ensemble (Zarattini/Pagani/Barbon,
SSRN 2025): daily channel-breakout entries with disciplined exits report
materially lower drawdowns than buy-and-hold on crypto while keeping
trend capture. Unlike a wrap on cs selection, this changes the SIGNAL:
per-symbol absolute breakouts with per-window exits — mechanically closer
to the live daily_trend_ensemble's 5-rung ladder, which a 4-window
ensemble maps onto exactly (0, ¼, ½, ¾, 1).

## Strategy definition (mechanical)

- Universe: **BTCUSDT + ETHUSDT** (pre-holdout files). The ladder engine
  aligns decision days across symbols by intersection; the 13-symbol
  universe would collapse the window to the youngest listing's warmup
  (≈2021+), breaking registry alignment. Widening the ladder engine to
  staggered listings is out of scope for this family and recorded as an
  engineering follow-up.
- Per symbol, per window w in the arm's window set:
  - OFF→ON: decision close strictly exceeds the max close of the prior w
    days (breakout).
  - ON→OFF (exit arm `half_low`): decision close falls below the min
    close of the prior ⌈w/2⌉ days.
  - ON→OFF (exit arm `mid_channel`): decision close falls below the
    midpoint of the prior w-day high-low close range.
  - State persists between decision days (state machine, no lookahead;
    all inputs are closes up to and including the decision close).
- Exposure fraction = (windows ON) / 4 — the standard 5-rung ladder;
  next-bar-open execution, identical costs, decision window pinned to the
  registry (2018-03-05 → 2025-07-01 returns).
- Regime-gate arm: when ON, the experiment-5 gate (SMA 200, btc basis,
  2% hysteresis, daily) multiplies the whole book by 0/1 — same state
  machine, applied to ladder decisions. When OFF, no gate.
- No vol overlay anywhere in this family.

## Family grid (8 configurations, all registered)

- window set ∈ { {10,20,55,110}, {20,55,110,220} }
- exit rule ∈ { half_low, mid_channel }
- regime gate ∈ { on, off }

Eight arms, chosen so every arm's trigger provably binds (the
experiment-6 filter-arm degeneracy lesson).

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 93)

1. **Winner DSR ≥ 0.95** at full deflation.
2. **Winner max drawdown ≤ 51.93%.**
3. **Winner annualized turnover ≤ 53.1.**

Anything less on any criterion → registered negative. Passing all three
does NOT trigger the loop's stop condition unless candidates-PBO ≤ 0.05
in the same report; October's holdout nominations remain fixed.

## Informative read-outs (non-gating, declared now)

- Fast (10-110) vs slow (20-220) window sets.
- Exit discipline: half-low trailing vs mid-channel.
- Gate marginal value on a signal that already exits on weakness (the
  breakout exit may make the gate redundant — worth knowing either way).
- Winner's correlation with trial 4 (the live ensemble) — same universe,
  different signal: the first true diversification read-out.
- Comparison to trial 4's own numbers (Sharpe 1.023, MDD 51.93%): does
  breakout logic beat the incumbent on ITS home turf?

## Engine prerequisite (work item, not a degree of freedom)

New strategy_name `donchian_breakout_ensemble` on the LADDER path (not
the cs path): an evaluate function over raw candles (windows + exit mode
+ per-window state), dispatched beside daily/confirmed trend; the ladder
path gains the regime-gate application (reusing the experiment-5 state
machine unchanged). Implementation and tests land before the first run;
runs happen on a clean committed tree.

## Honesty clauses

- Registry N grows to ≥ 93; every DSR pays the larger deflation.
- BTC/ETH-only scope is declared UP FRONT; a future 13-symbol ladder
  needs engine work and its own pre-registration — no post-hoc universe
  switching inside this family.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.
