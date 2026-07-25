# Goal P experiment 10 — result: first family to pass its own criteria; trial 118 clears the deflation bar by 0.0005

Executed: 2026-07-25 · Trials: **118-125** (registry N: 117 → 125)
Pre-registration: `docs/research/GOALP_EXPERIMENT10_PREREGISTRATION.md`
(unmodified)
Gate report: `docs/reports/research/gate_report_2026-07-25.json` (N=125)

## Family table (8 configs; trial 88's entries, ATR channel exit)

| Trial | ATR window | ATR multiple | Sharpe | MDD | Turnover | Equity |
|---:|---:|---:|---:|---:|---:|---:|
| **118** | **14** | **2** | **1.2411** | **33.24%** | **11.10** | **16,899** |
| 119 | 14 | 3 | 1.0902 | 47.69% | 7.27 | 15,674 |
| 120 | 14 | 4 | 1.0297 | 56.41% | 4.55 | 16,983 |
| 121 | 14 | 6 | 0.8552 | 60.31% | 1.75 | 9,657 |
| 122 | 28 | 2 | 1.1525 | 31.56% | 11.84 | 12,407 |
| 123 | 28 | 3 | 1.1811 | 38.63% | 7.49 | 19,254 |
| 124 | 28 | 4 | 0.9638 | 59.68% | 4.38 | 12,238 |
| 125 | 28 | 6 | 0.9052 | 64.18% | 1.64 | 11,995 |
| — | **trial 88 (mid-channel exit)** | — | **1.1821** | **33.05%** | 13.92 | 14,231 |

Winner by the pre-declared rule: **trial 118 — ATR window 14, multiple 2**.

## Verdict against the frozen criteria — ALL THREE PASS

1. **Winner DSR ≥ 0.95: PASS — 0.950514** at full N=125 deflation.
2. **Winner MDD ≤ 51.93%: PASS — 33.24%**, inside by 18.7pp.
3. **Winner turnover ≤ 53.1: PASS — 11.10**, and lower than trial 88's.

**This is the first family in ten to pass its own pre-registered
criteria.** Trial 118 is the first trial in the registry's history to
clear the gate-4 deflation bar while ALSO being risk-compliant (trials 29
and 37 clear DSR at 75.1% and 67.5% drawdown, which fails the risk bar by
23pp and 16pp; they qualify nothing).

## Read this pass honestly

- **The margin is 0.0005.** Treat trial 118 as sitting AT the bar, not
  above it. Any number that close is inside the noise of the deflation
  estimate, and the honest statement is "it reached the bar", not "it
  beat the bar".
- **The winner is at a grid endpoint.** ATR multiple 2 is the tightest
  arm tested; the pre-registration declared in advance that an endpoint
  winner is weaker evidence because the grid did not bracket the
  mechanism. A tighter multiple might score higher — and testing it
  requires a NEW pre-registration and its own N cost. Extending this grid
  post hoc is forbidden and is not being done.
- **The dial is otherwise well-behaved and monotone**: looser stops trade
  less (turnover 11.8 → 1.6) and lose more (MDD 31.6% → 64.2%,
  Sharpe 1.15 → 0.91). The mechanism is real and directional, not noise:
  giving a trend a *volatility-proportional* floor works, but only when
  the floor is tight.
- **Gate 3 is unchanged and still fails**: candidates-PBO 0.8451,
  all-columns 0.6967, against a 0.05 bar. The loop's stop condition
  (DSR ≥ 0.95 AND PBO ≤ 0.05) is NOT met, so the search does not halt on
  this result. A single trial clearing gate 4 does not qualify the
  project's six-gate sign-off.
- **N-arithmetic consequence, stated plainly**: at a 0.0005 margin, one
  more 8-arm family raises the deflation bar enough to push trial 118
  back under it on mechanics alone. Verdicts are rendered at the report a
  pre-registration names (this one: N=125) and are not retroactively
  voided — but any future report will likely show trial 118 below 0.95.
  That is expected arithmetic, not new evidence against the strategy, and
  it must be stated wherever trial 118's DSR is quoted later.

## Zero-cost diagnostics on trial 118 (no registry cost)

Run before this document from the already-registered return series:

- **Stationary bootstrap** (2000 resamples, mean block 20d): 90% CI
  **[0.6100, 1.8641]**, **P(Sharpe ≤ 0) = 0.0000**, P(Sharpe ≤ 1) = 0.280.
  Strictly better than trial 88's [0.5586, 1.8031] / 0.317.
- **Subperiods**: 2018-2020 1.61, 2021 1.61, **2022 −0.94** (trial 88:
  −1.17), 2023 1.62 (trial 88: 1.26), 2024-2025H1 0.96 (trial 88: 1.06).
  Still a losing bear year, at 24.4% drawdown.
- **Rolling 365d Sharpe**: 26 windows, min −0.98, median 1.27, 4 negative
  (15.4%) — same negative share as trial 88 at a higher median.
- **Tail dependence**: dropping the best 5 days of 2676 takes Sharpe
  1.241 → 1.069; the best 20 takes it to 0.636. Slightly less
  tail-dependent than trial 88 but the convexity is inherent to trend
  following and any live execution must accept it.
- **Versus trial 88**: correlation 0.9375; every blend (25/50/75%) is
  worse than pure trial 118 on Sharpe at equal drawdown. Trial 118
  dominates trial 88 on Sharpe, terminal wealth (15.90× vs 13.23×),
  turnover, 2022 behaviour, and bootstrap floor, at the same drawdown.

## Required next step, per this family's own honesty clause

Trial 118 does **not** inherit trial 88's robustness battery. Before it
may be nominated for anything it needs its own: parameter neighbourhood
(ATR window and multiple perturbations), cost stress at 2× and 3×, all
arms bound never-nominatable. That battery raises N and will move DSR
values in the next report — see the arithmetic note above.

Its forward-only shadow track started 2026-07-24 and runs daily beside
trial 88's, which is the only clean out-of-sample evidence either
candidate can accumulate before the October holdout (whose nominations
are fixed and cannot include either).

## Provenance

All 8 trials on clean tree `33f55e8` (commit-first rule). Registry rows
carry `dc_atr_window` / `dc_atr_multiple` machine-readable.

---

## Addendum 2026-07-26 — cross-market evidence against this family's key choice

Recorded after the fact and appended rather than rewritten; the verdict
above stands exactly as rendered at N=125.

Trial 118's configuration was run **unchanged** on Taiwan's 0050 ETF
(adjusted, 2004-04-15 → 2025-07-02, 21 years) in the sibling repository,
under its own frozen pre-registration forbidding any re-tuning
(`D:\TW-Stock-Trading\docs\research\CROSSMARKET_DONCHIAN_RESULT.md`).

| | Sharpe | MDD | 100k becomes |
|---|---:|---:|---:|
| trial 118 config | **−0.3055** | 40.48% | 66,330 |
| buy-and-hold 0050 | 0.7159 | 55.75% | 787,034 |
| trial 88 config (context) | 0.4262 | 30.85% | 215,032 |

**It did not transfer.** The decisive detail is the mechanism: the
primary and context arms differ only in the exit rule, and that single
swap is worth **+0.06 Sharpe in crypto but −0.73 in Taiwan**. The
2×ATR exit — the choice that made trial 118 this program's best
candidate — is the worst of the two in the other market.

Consequence for how trial 118 must be described from now on: its crypto
numbers, robustness battery, and gate-4 pass all stand, but any claim
that it captures a market-independent trend-following effect is refuted.
The parameter that distinguishes it encodes a property of crypto. This is
the same conclusion the 2026-07-26 PBO diagnostic reached statistically,
now measured directly across markets — which is stronger evidence than
resampling one market ever produces.
