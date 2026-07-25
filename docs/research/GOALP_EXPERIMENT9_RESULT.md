# Goal P experiment 9 — result: the SSRN sizing half does not transfer; ninth negative

Executed: 2026-07-25 · Trials: **110-117** (registry N: 109 → 117)
Pre-registration: `docs/research/GOALP_EXPERIMENT9_PREREGISTRATION.md`
(unmodified)
Gate report: `docs/reports/research/gate_report_2026-07-25.json` (N=125 —
the pre-registration specifies N ≥ 117, and the report was taken after
experiment 10 also ran, which is the more conservative reading).

## Family table (8 configs; trial 88's signal, inverse-vol sizing)

| Trial | Vol lookback | Target vol | Name cap | Sharpe | MDD | Turnover | Equity |
|---:|---:|---|---:|---:|---:|---:|---:|
| 110 | 20 | none | 0.50 | 1.1271 | 34.09% | 15.02 | 11,870 |
| 111 | 20 | none | 0.30 | 1.1277 | 40.26% | 9.62 | 10,518 |
| **112** | **20** | **0.25** | **0.50** | **1.1409** | **37.92%** | **10.42** | **7,413** |
| 113 | 20 | 0.25 | 0.30 | 1.1050 | 37.00% | 9.41 | 6,555 |
| 114 | 60 | none | 0.50 | 1.1303 | 34.23% | 14.23 | 12,216 |
| 115 | 60 | none | 0.30 | 1.1292 | 40.77% | 9.25 | 10,628 |
| 116 | 60 | 0.25 | 0.50 | 1.1025 | 39.18% | 7.88 | 6,639 |
| 117 | 60 | 0.25 | 0.30 | 1.0790 | 40.21% | 7.69 | 6,386 |
| — | **trial 88 (equal weight)** | — | — | **1.1821** | **33.05%** | 13.92 | **14,231** |

Winner by the pre-declared rule: **trial 112**.

## Verdict against the frozen criteria

1. **Winner DSR ≥ 0.95: FAIL — 0.915330** at N=125 deflation.
2. Winner MDD ≤ 51.93%: PASS — 37.92%.
3. Winner turnover ≤ 53.1: PASS — 10.42.

**Registered negative — the ninth.**

## The finding: sizing subtracts on an unleverable book, on a second signal

Every one of the eight arms scores BELOW the equal-weighted trial 88 on
Sharpe (1.079–1.141 vs 1.1821), on drawdown (34–41% vs 33.05%), and on
terminal wealth (6,386–12,216 vs 14,231). The target-vol arms are the
worst on wealth: 7,413 and below, roughly half of equal weighting.

This is the same mechanism experiments 2 and 4 found on the cs-momentum
signal, now confirmed on the Donchian signal: **a volatility target on a
spot long-only book can only de-risk.** The source paper reaches its
target by levering up in calm regimes as well as cutting in violent ones;
this product cannot lever, so it keeps the cut and forfeits the
compensation. Three families, two signal spaces, one conclusion —
volatility-based position sizing is closed for this product.

The pure vol-parity arms (target `none`) came closest to equal weighting
(1.1271–1.1303), which isolates the damage to the TARGETING step, not to
the parity step. Recorded for completeness: parity alone is roughly
neutral-to-slightly-negative here; targeting is what costs.

## Also recorded

- The declared faithfulness limit held: with per-name weights capped at
  their risk budget, parity could only de-risk within budgets. A book
  that could over-weight across names might behave differently, but that
  book is not product-legal here (spot, long-only, budgets sum to ≤ max
  gross), so the question is moot for this project.
- Registry rows 110-117 carry the full `dc_*` parameter set
  machine-readable.

## Provenance

All 8 trials on clean tree `880a545` (commit-first rule). The allocation
engine landed with 10 tests including a bit-for-bit parity test proving
`dc_alloc_model="equal"` reproduces the experiment-7/8 behaviour exactly,
and a test asserting the allocator and the experiment-2/4 overlay share
one volatility formula.
