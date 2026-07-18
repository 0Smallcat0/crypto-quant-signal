# Goal P pre-registration — experiment 2: volatility-target overlay FAMILY

Date registered: 2026-07-18 (BEFORE any family backtest runs)
Basis: internal evidence (SSRN 3175538 via 07-02 report) + external check
(docs/research/EXTERNAL_EVIDENCE_2026-07.md §2) — the strongest available
hypothesis compatible with spot-long-only.
Method change vs experiment 1: ONE family, pre-registered in full, judged
family-wise — not one variant per week. This is the honest way to search
hard: every configuration is declared before any result exists, and the
winner's deflation pays for the whole family.

## Hypothesis

Scaling the ladder's exposure by a volatility target materially improves
deflation-adjusted risk-adjusted performance: vol-managed evidence across
asset classes shows left-tail reduction and Sharpe gains concentrated in
risk assets; crypto-specific 2024-25 results corroborate. The ladder decides
WHETHER to be long; the overlay decides HOW MUCH, shrinking exposure when
realized volatility is rich relative to target.

## Family definition (exact, 16 configurations)

Overlay: `final_fraction = ladder_fraction × min(1, target_vol / realized_vol)`
applied per symbol; realized vol = annualized std of daily log returns over
`vol_window`; scaling factor recomputed on the `rebalance` schedule and
held in between; final fraction is NOT re-quantized to the ladder rungs
(the overlay is a position-size modifier, not a signal change).

Grid (4 × 2 × 2 = 16):

- `target_vol` ∈ {30%, 50%, 70%, 90%} annualized
- `vol_window` ∈ {20, 60} trading days
- `rebalance` ∈ {daily, monthly (first decision day of each calendar month)}

Everything else identical to trial 4: universe BTC+ETH, pre-holdout window,
standard costs, production engine, next-bar-open fills.

## Registration accounting

All 16 configurations are registered trials (registry N: 5 → 21). No
configuration is hidden, ever. The in-family selection rule is pre-declared
(below), so the family counts as ONE hypothesis with a 16-way selection —
and the winner's DSR is deflated at the FULL registry count (N=21),
which over-penalizes if anything. Costs of honesty are accepted up front:
every future trial's deflation rises too.

## Family-wise success criteria (set before running)

Selection rule: the family winner is the configuration with the highest
annualized Sharpe over the full window (ties → lower turnover wins).

The family is a SUCCESS only if the winner satisfies ALL of:

1. Winner's DSR (at N=21, registry-wide variance) **> trial 4's DSR in the
   same N=21 report** — deflation-adjusted improvement after paying for the
   16-way search;
2. Winner's max drawdown ≤ trial 4's max drawdown − 5pp (the overlay's whole
   point is the left tail; a vol overlay that doesn't cut drawdown is
   noise);
3. Winner's annualized turnover ≤ 2× trial 4's (manual execution must stay
   feasible; a daily-churn overlay is unusable even if pretty).

Additional pre-declared read-outs (informative, not gating): monthly vs
daily rebalance comparison (compliance cost of frequency), and whether ANY
configuration beats trial 4's raw Sharpe (family-level signal existence).

If the family fails: registered negative, move to universe expansion track.
No grid extension to rescue it (a wider grid is a NEW pre-registration with
its own accounting).

## What this cannot do

- Touch the holdout or the live qualification run (config cannot express
  the overlay; backtest-only).
- Fix gate 3's matrix-composition question — it sharpens it: after this
  family, the registry will hold 21 columns of ONE strategy lineage. The
  gate contract MUST define candidate-vs-rerun matrix rules before any
  holdout access (recorded 2026-07-18 in experiment 1's result; still open).
