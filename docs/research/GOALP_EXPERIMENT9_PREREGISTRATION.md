# Goal P experiment 9 pre-registration — SSRN-faithful sizing on the Donchian book

Status: **FROZEN on commit**. Written 2026-07-25, after the allocation
engine landed (commit 880a545, 376 tests green) and before any
experiment-9 run.

## Override recorded

Sixth operator override (「預算很充足，你可以一直跑」, after
「想盡辦法，做盡測試」). Every criterion below is the statutory bar
frozen long before today (0.95 DSR gate; trial 4's 51.93% MDD; 3×17.69
turnover). No number observed in experiments 3-8 or in the trial-88
robustness battery appears as a threshold.

## Hypothesis

Experiment 7 tested half of the SSRN result: the Donchian breakout
ensemble, equally weighted. It landed at DSR 0.9267 (now 0.9330), with
both risk bars passed and a clean robustness battery behind it.
Zarattini/Pagani/Barbon attribute their headline JOINTLY to the ensemble
AND to volatility-based position sizing; experiment 8 showed that adding
breadth without sizing subtracts. This family tests the untested half:
size the same book by inverse volatility, cap per name, and rescale
toward a portfolio volatility target.

## Strategy definition (mechanical)

- Signal, universe, costs, window: **identical to trial 88** — Donchian
  10/20/55/110, mid_channel exit, no regime gate, BTC/ETH pre-holdout,
  risk budgets 0.5/0.5, returns pinned to the registry window.
- Allocation (`dc_alloc_model = "inverse_vol"`), per decision day:
  1. target gross = Σ (signal fraction × budget) — the signal's own
     exposure level is preserved, never inflated.
  2. shares ∝ 1 / realized volatility over `dc_vol_lookback` days
     (`_annualized_realized_vol`, the project's single vol formula).
  3. per-name weight capped at min(`dc_name_cap`, risk budget).
  4. if `dc_target_vol` is set: scale the whole book by
     min(1, target / Σ wᵢσᵢ) — a correlation-1 portfolio vol estimate,
     conservative for crypto, where correlations spike inside exactly the
     drawdowns this scaling exists to contain.
  5. gross clamped to 1. Long-only, de-risk-only, no leverage.
- Any active name without a volatility estimate (warmup) → the whole day
  falls back to equal weighting, so two sizing models never mix on one
  day.

**Declared faithfulness limit**: the portfolio contract caps each name at
its risk budget and requires budgets to sum to ≤ max gross. Vol parity is
therefore expressible only as de-risking WITHIN budgets, never as the
cross-name over-weighting the source paper uses. This family tests the
long-only-product-legal version of the paper's mechanism, not the paper's
exact book, and no result here may be reported as replicating it.

## Family grid (8 configurations, all registered)

- `dc_vol_lookback` ∈ {20, 60}
- `dc_target_vol` ∈ {none (pure vol parity), 0.25 (annualized)}
- `dc_name_cap` ∈ {0.50 (equals the budget — non-binding), 0.30}

The 0.25 target follows the Bloomberg Cryptocurrency Vol Target Indices
band (10/15/25%) logged in RESEARCH_LOG; the 0.30 cap follows the
Alvarez-style per-name cap logged there. Both arms bind by construction,
per the experiment-6 degeneracy lesson.

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe.

## Success criteria (ALL required, same full-registry gate report, N ≥ 117)

1. **Winner DSR ≥ 0.95** at full deflation.
2. **Winner max drawdown ≤ 51.93%.**
3. **Winner annualized turnover ≤ 53.1.**

Anything less on any criterion → registered negative. Passing all three
does not trigger the loop's stop condition unless candidates-PBO ≤ 0.05
in the same report; October's holdout nominations remain fixed.

## Informative read-outs (non-gating, declared now)

- Winner versus trial 88 (Sharpe 1.1821 / MDD 33.05% / turnover 13.92) —
  does sizing add on top of the signal, as the paper's mechanism claims?
- Vol parity alone (target none) versus parity + targeting.
- Cap binding cost: 0.30 versus 0.50 arms.
- Turnover: sizing rebalances daily on vol drift, so this family should
  be the busiest yet — the turnover bar is the one that could bite.

## Honesty clauses

- Registry N grows to ≥ 117; every DSR pays the larger deflation. The
  2026-07-23 N-arithmetic authorised this family specifically because it
  tests an untested MECHANISM, not another wrapper sweep.
- If the winner beats trial 88 it does NOT inherit trial 88's robustness
  battery; it would need its own before any nomination.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.
