# Goal P experiment 4 — result: the overlay cannot buy back the drawdown; family FAILS

Executed: 2026-07-21 · Trials: **38-53** (registry N: 37 → 53)
Pre-registration: `docs/research/GOALP_EXPERIMENT4_PREREGISTRATION.md`
(unmodified; drift-guard override recorded there)
Gate report: `docs/reports/research/gate_report_2026-07-21.json`
(regenerated at N=53, 2676 obs)

## Family table (16 configs; cs base fixed at K=2/180d/monthly/filter-on)

| Trial | Target | Window | Scaler cadence | Sharpe | MDD | Turnover | Final equity |
|---:|---:|---:|---|---:|---:|---:|---:|
| 38 | 30% | 20 | daily | 0.7693 | 44.34% | 5.29 | 5,953 |
| 39 | 30% | 20 | monthly | 0.8686 | 45.23% | 3.10 | 8,269 |
| 40 | 30% | 60 | daily | 0.7950 | 39.12% | 2.81 | 5,141 |
| 41 | 30% | 60 | monthly | 0.8338 | 39.24% | 2.36 | 6,281 |
| 42 | 50% | 20 | daily | 0.7612 | 58.43% | 6.56 | 6,774 |
| 43 | 50% | 20 | monthly | 0.9773 | 54.60% | 4.11 | 16,738 |
| 44 | 50% | 60 | daily | 0.8612 | 58.51% | 4.37 | 10,614 |
| 45 | 50% | 60 | monthly | 0.8554 | 56.11% | 3.53 | 10,465 |
| 46 | 70% | 20 | daily | 0.6684 | 62.56% | 6.21 | 4,930 |
| **47** | **70%** | **20** | **monthly** | **1.0338** | **63.76%** | **4.49** | **25,790** |
| 48 | 70% | 60 | daily | 0.9464 | 66.30% | 4.76 | 17,453 |
| 49 | 70% | 60 | monthly | 0.9289 | 68.99% | 4.01 | 16,857 |
| 50 | 90% | 20 | daily | 0.6620 | 68.25% | 5.54 | 4,916 |
| 51 | 90% | 20 | monthly | 0.9991 | 71.20% | 4.24 | 24,410 |
| 52 | 90% | 60 | daily | 0.9019 | 72.70% | 4.59 | 15,396 |
| 53 | 90% | 60 | monthly | 0.9038 | 73.06% | 4.10 | 15,631 |

Winner by the pre-declared rule (highest Sharpe): **trial 47 — target 70%,
window 20d, monthly scaler**.

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR ≥ 0.95: FAIL — 0.811394** at N=53 deflation. Sharpe 1.03
   is simply not enough signal for a 53-trial search history.
2. **Winner MDD ≤ 51.93%: FAIL — 63.76%**, missed by 11.83pp.
3. Winner turnover ≤ 53.1: PASS — 4.49.

**The family is a registered negative under its own pre-registration** —
the project's fourth. Stop condition remains unmet (candidates-PBO 0.6364,
all-columns 0.5871).

## The structural finding (why this negative is informative)

The grid swept the entire risk dial, and the two criteria never overlap:

- Every MDD-compliant arm (the 30% targets: 39-45% MDD) has Sharpe ≤ 0.87
  — DSR ≤ 0.68 at N=53. Dead on criterion 1.
- Every Sharpe-competitive arm (≥ 1.0) carries MDD ≥ 63.8%. Dead on
  criterion 2.
- The gap at its narrowest (trial 43: 0.977 Sharpe / 54.6% MDD) still
  fails both bars.

Mechanism, consistent with the Springer FMPM 2025 warning already in
RESEARCH_LOG: cs-momentum profits concentrate in high-volatility regimes.
A vol-target overlay de-risks EXACTLY when the strategy earns, so cutting
tail risk cuts the earning engine roughly one-for-one. Volatility is the
wrong conditioning variable for this signal — the overlay cannot tell a
profitable vol regime from a destructive one.

This kills the "wrap it in vol control" hypothesis cleanly and points the
search at DIRECTIONAL regime conditioning instead (e.g. a BTC 200-day-SMA
gate: flat when the tape is structurally bearish, full cs book otherwise)
— which the loop's iteration-3 web pass independently surfaced as the
practitioner-standard next lever (RESEARCH_LOG 2026-07-21 entries).
That is experiment-5 material, to be pre-registered in a LATER sitting
(the drift guard returns to normal after today's recorded override).

## Also recorded

- **Trial 29 at N=53: DSR rose to 0.976471** (from 0.9621 at N=37) —
  deflation non-monotonicity, third occurrence: sixteen similar-Sharpe
  overlay columns REDUCED cross-trial variance (3.64e-4 → 2.64e-4) faster
  than N raised the expected-max bar. Recorded as mechanics, not as a new
  qualification: trial 29 remains the winner of a FAILED family, nothing
  more, and gates 3/5/6 still stand between any backtest number and money.
- Trial 47's final equity (25,790) is the highest in the registry —
  informative for the terminal-wealth ledger, worthless as qualification
  (its 63.76% MDD is the reason followers wouldn't be there to collect).
- Registry rows 38-53 serialize the full cs_* + vol_* parameter set
  (the forward-fix landed before this family ran); they enter the
  candidates matrix as sixteen distinct columns, unlike rows 22-37.

## Provenance

All 16 trials ran on clean tree `1345492` (commit-first rule). Registry
rows, durable return series, the regenerated N=53 report, and this
document are committed together.
