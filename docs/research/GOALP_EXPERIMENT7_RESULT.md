# Goal P experiment 7 — result: Donchian clears the risk bars at a canter; deflation still holds the door

Executed: 2026-07-22 · Trials: **86-93** (registry N: 85 → 93)
Pre-registration: `docs/research/GOALP_EXPERIMENT7_PREREGISTRATION.md`
(unmodified; fourth same-sitting override recorded there)
Gate report: `docs/reports/research/gate_report_2026-07-22.json`
(N=93, 2676 obs)

## Family table (8 configs; BTC/ETH universe)

| Trial | Windows | Exit | Gate | Sharpe | MDD | Turnover | Final equity |
|---:|---|---|---|---:|---:|---:|---:|
| 86 | 10+20+55+110 | half_low | off | 1.0916 | 40.28% | 13.47 | 12,208 |
| 87 | 10+20+55+110 | half_low | on | 1.1221 | 34.98% | 10.52 | 10,904 |
| **88** | **10+20+55+110** | **mid_channel** | **off** | **1.1821** | **33.05%** | **13.92** | **14,231** |
| 89 | 10+20+55+110 | mid_channel | on | 1.1369 | 32.13% | 10.93 | 10,694 |
| 90 | 20+55+110+220 | half_low | off | 1.0667 | 47.55% | 5.89 | 12,297 |
| 91 | 20+55+110+220 | half_low | on | 1.0967 | 41.88% | 5.35 | 11,758 |
| 92 | 20+55+110+220 | mid_channel | off | 1.0936 | 47.63% | 6.58 | 12,243 |
| 93 | 20+55+110+220 | mid_channel | on | 1.0766 | 44.40% | 5.74 | 10,856 |

Winner by the pre-declared rule (highest Sharpe): **trial 88 — fast
windows, mid-channel exit, no gate**.

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR ≥ 0.95: FAIL — 0.926746** at N=93 deflation. Missed by
   0.0233 — the closest any family winner has come.
2. **Winner MDD ≤ 51.93%: PASS — 33.05%**, inside the bar by 18.9pp. The
   entire family passes this criterion (32.1%–47.6%); no cs arm ever did
   better than 48.7%.
3. Winner turnover ≤ 53.1: PASS — 13.92.

**The family is a registered negative under its own pre-registration** —
the seventh — but the first where BOTH risk criteria pass family-wide and
only the deflation bar holds. Stop condition remains far off
(candidates-PBO 0.8705).

## Why this negative changes the search's shape

- **The signal space matters more than the wrapper.** Six cs experiments
  never got a compliant-MDD arm above Sharpe 0.92; Donchian's WORST arm
  (1.067 / 47.6%) beats every MDD-compliant cs arm on both axes at once.
  Breakout entries with built-in exits do natively what gates and
  overlays tried to bolt on.
- **Against the incumbent on its home turf**: trial 88 vs trial 4
  (same BTC/ETH universe): Sharpe 1.182 vs 1.023, MDD 33.05% vs 51.93%,
  final equity 14,231 vs 14,221 — equal terminal wealth on a path with
  RESHAPED risk (a 33% worst valley instead of 52%). For a follower whose
  failure mode is drawdown abandonment, that is the difference between
  holding and quitting.
- **The gate read-out resolved as predicted**: on a signal that already
  exits on weakness, the external regime gate LOWERS Sharpe in 3 of 4
  pairings (it double-brakes) while buying only a few MDD points the
  family didn't need. The gate belongs to signals without exits — carry
  that lesson forward.
- **What stands between 0.927 and 0.95**: roughly Sharpe ≥ 1.24 at this
  N. The registered path there is breadth — the SSRN paper ran
  BTC+altcoins; our 13-symbol universe is qualified and waiting — but the
  ladder engine aligns decision days by intersection, so staggered
  listings need engine work first (recorded follow-up since the
  pre-registration). That is experiment-8 material: same signal, wider
  book, its own frozen criteria.

## Also recorded

- Trial 29 at N=93: DSR 0.985224 (plateau; still the registry's only
  gate-4 pass; still the winner of a failed family; October nominations
  unaffected).
- Trial 37 at 0.948455 — knocking on the bar from the ungated cs side.
- Candidates-PBO 0.8705: in-family winner-picking remains overfit,
  which keeps the fixed-nomination design load-bearing.
- Fast windows beat slow on Sharpe everywhere; mid-channel exit beats
  half-low on the fast set (looser trailing floor lets winners breathe).

## What happens next (sequential research, not a rescue)

Experiment-8 candidate, to be pre-registered in a LATER sitting unless
the operator overrides again: the Donchian ensemble on the 13-symbol
qualified universe, which requires the ladder engine to admit staggered
listings (per-symbol decision eligibility instead of intersection
alignment) — an engineering prerequisite with its own tests, then the
family. Statutory bars unchanged. The October holdout stays sealed and
its nominations fixed; nothing here touches it.

## Provenance

All 8 trials ran on clean tree `6c99598` (commit-first rule). Registry
rows carry dc_windows/dc_exit plus gate parameters machine-readable.
Registry, return series, the N=93 report, and this document are committed
together.
