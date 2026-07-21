# Goal P experiment 6 pre-registration — multi-horizon trend factor under the proven gate

Status: **FROZEN on commit**. Written 2026-07-21, before any engine work or
run for this family. Hypothesis, grid, selection rule, and success criteria
may not change once the first member runs. A failed family is a registered
negative.

## Drift-guard override (recorded, not hidden)

Third same-sitting override today; the operator answered the explicit
offer ("你說『直接寫』我就直接寫") with 「continue」. Neutralized
identically to experiments 4 and 5: **every success criterion below is the
statutory bar frozen before today** (absolute 0.95 DSR gate; trial 4's
51.93% MDD; 3×17.69 turnover). No number first observed today (the
experiment-5 table, trial 56's DSR, trial 62's MDD) appears as a
threshold. Architecture carry-over (the SMA-200/btc/daily/2% gate) is
sequential refinement, declared legitimate since experiment 2.

## Hypothesis

Experiment 5 proved the directional gate can hold cs drawdown inside the
statutory bar (51.83% at SMA 200) but the single-lookback 180d selection
signal is too weak to clear deflation once gated (Sharpe 0.98 → DSR 0.79).
The Cambridge JFQA 2024 trend-factor result (RESEARCH_LOG, iteration 1:
multi-horizon trends subsume single-lookback momentum; 4- and 8-week
horizons carry most OOS power) predicts a MULTI-HORIZON selection score
earns more Sharpe from the same universe. Combining that stronger signal
with the gate that already touches the MDD bar targets the still-open
statutory corner: DSR ≥ 0.95 AND MDD ≤ 51.93% in one configuration.

## Strategy definition (mechanical)

- Universe, costs, window, floor: unchanged — 13 pre-holdout symbols,
  decision floor 2018-03-05, identical cost assumptions, returns pinned to
  the registry window.
- Selection score: the equal-weight mean of trailing total returns over
  the arm's horizon set (no estimated weights — a fixed, mechanical
  blend). A symbol enters the ranking pool only when it has history for
  the LONGEST horizon in the set. Pool < 4 → cash.
- Selection: top-K by score, equal weight 1/K; absolute-filter arm
  replaces a selected symbol with cash when its SCORE ≤ 0. Spot long-only.
- Regime gate, FIXED for the whole family (experiment 5's MDD-bar
  configuration with the turnover-friendlier hysteresis arm):
  SMA window 200, basis btc, hysteresis 2%, gate cadence daily.
  Gated weight = weight × {0,1}; raw selection state never rewritten.
- No vol overlay (mutually exclusive by engine law since experiment 5).

## Family grid (16 configurations, all registered)

- horizon set ∈ { {28,56}, {28,56,112,224} } (short-pair vs full blend)
- K ∈ {2, 3}
- selection cadence ∈ {weekly, monthly}
- absolute filter ∈ {on, off}

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 85)

1. **Winner DSR ≥ 0.95** — statutory gate-4 bar at full N≥85 deflation.
2. **Winner max drawdown ≤ 51.93%** — trial 4's live baseline, unchanged.
3. **Winner annualized turnover ≤ 53.1** — unchanged.

Anything less on any criterion → registered negative. Passing all three
still does NOT trigger the loop's stop condition unless candidates-PBO
≤ 0.05 holds in the same report; October's holdout nominations remain
fixed regardless.

## Informative read-outs (non-gating, declared now)

- Short-pair vs full-blend horizon sets (the JFQA short-horizon claim,
  tested gated).
- Weekly vs monthly selection under a daily gate (short-horizon signals
  decay faster; weekly may finally earn its turnover — experiment 3's
  monthly verdict was for a 180d signal).
- Gate engagement overlap with experiment 5's arms (same gate, different
  signal: how much MDD protection is gate vs signal).
- Winner's daily-return correlation with trial 4 and with trial 56.

## Engine prerequisite (work item, not a degree of freedom)

`cs_horizon_days` parameter (tuple of ints; empty = single-lookback
current behavior). Score computation replaces the single-lookback pool
return when set; eligibility keys on the longest horizon. Registry
serialization carries the horizon set. Implementation and tests land
before the first family run; runs happen on a clean committed tree.

## Honesty clauses

- Registry N grows to ≥ 85; every DSR pays the larger deflation. If that
  sinks the family, the verdict stands.
- Universe survivorship bias carries over; the holdout remains the single
  arbiter; nothing here touches the October nominations.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.
