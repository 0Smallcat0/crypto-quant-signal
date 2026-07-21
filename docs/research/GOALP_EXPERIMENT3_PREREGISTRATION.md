# Goal P experiment 3 pre-registration — cross-sectional momentum family

Status: **FROZEN on commit**. Written 2026-07-21, before any engine work or
backtest run. Hypothesis, grid, selection rule, and success criteria may not
change once the first family member runs. A failed family is a registered
negative. Registered BEFORE reading any new results (last result read-out
was experiment 2 on 2026-07-18; the goalpost-drift guard is satisfied).

## Hypothesis

Cross-sectional (relative) momentum — long the strongest K of 13 large-cap
USDT pairs, rebalanced on a fixed cadence — carries positive risk-adjusted
returns beyond BTC/ETH time-series trend, per the external evidence review
(`docs/research/EXTERNAL_EVIDENCE_2026-07.md`) and the classic
Liu–Tsyvinski–Wu cross-crypto-momentum literature. The 13-symbol universe
and its survivorship-bias discount are documented in
`docs/research/UNIVERSE_EXPANSION.md`.

## Strategy definition (mechanical)

- Universe: the 13 qualified symbols (BTC, ETH, BNB, LTC, ADA, XRP, XLM,
  TRX, LINK, DOGE, SOL, AVAX, DOT — USDT pairs), pre-holdout data only
  (`data/candles_preholdout/`).
- Ranking pool on each rebalance day: symbols with ≥ lookback days of
  history by that day. Pool smaller than 4 → hold cash entirely.
- Signal: total return over the trailing `lookback` days.
- Portfolio: equal weight 1/K in the top-K ranked symbols; spot long only,
  remainder (if any) in cash. No leverage, no shorts (product law).
- Absolute filter (grid arm): when ON, a top-K symbol with lookback return
  ≤ 0 is replaced by cash (dual-momentum). All-negative tape → 100% cash.
- Execution: decisions on the daily close, executable from the next bar,
  same cost assumptions as every registered trial (fee 10 bps + modeled
  slippage; turnover pays for itself).
- Backtest window: identical to the registry window (returns
  2018-03-05 → 2025-07-01) so the strict-alignment gate report can include
  the family without exceptions.

## Family grid (16 configurations, all registered)

- K ∈ {2, 3}
- lookback ∈ {90, 180} days
- rebalance ∈ {weekly, monthly}
- absolute_filter ∈ {on, off}

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 37)

1. Winner DSR > 0.9273 (trial 7, the current all-time best) in the same
   report — the family must beat the record holder after paying its own
   deflation.
2. Winner max drawdown ≤ 51.93% (trial 4's MDD — no worse than the live
   baseline).
3. Winner annualized turnover ≤ 53.1 (3 × trial 4's 17.69 — cross-sectional
   rebalancing is naturally busier; beyond 3× the cost model dominates).

Anything less on any criterion → the family is a registered negative.
Informative non-gating read-outs: filter-on vs filter-off, weekly vs
monthly, K=2 vs K=3 direction, and correlation of the winner's daily
returns with trial 4 (diversification value).

## Engine prerequisite (work item, not a degree of freedom)

The current engine decides per-symbol independently; ranking needs one
cross-symbol allocation step. The allocator must be a new research-only
path (`cross_sectional_momentum` strategy name in BacktestParameters),
leaving the live daily_trend_ensemble contract untouched. Implementation
and tests land BEFORE the first family run; the run happens on a clean
committed tree (commit-first rule).

## Honesty clauses

- Registry N grows to ≥ 37; every DSR in the report pays the larger
  deflation. If that sinks the family, the verdict stands.
- Survivorship bias: in-sample numbers on a 2026-selected universe are
  upper bounds. The October holdout CANNOT be spent on this family (its
  nominations are fixed in `docs/contracts/PRE_HOLDOUT_PROTOCOL.md`); a
  passing winner becomes a candidate for the NEXT holdout cycle and its own
  paper-trading qualification. No shortcut exists.
- The autonomous research loop may EXECUTE this pre-registration but may
  not EDIT it. Editing after the first run voids the family.
