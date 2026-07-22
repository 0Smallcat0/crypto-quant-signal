# Goal P experiment 8 — result: breadth subtracts; the eighth negative closes the equal-weight route

Executed: 2026-07-22 · Trials: **94-101** (registry N: 93 → 101)
Pre-registration: `docs/research/GOALP_EXPERIMENT8_PREREGISTRATION.md`
(unmodified; fifth override recorded there)
Gate report: `docs/reports/research/gate_report_2026-07-22.json`
(regenerated at N=101, 2676 obs)

## Family table (8 configs; 13-symbol staggered universe, 1/13 budgets)

| Trial | Windows | Exit | Gate | Sharpe | MDD | Turnover | Final equity |
|---:|---|---|---|---:|---:|---:|---:|
| 94 | 10+20+55+110 | half_low | off | 0.9725 | 51.54% | 7.36 | 9,384 |
| 95 | 10+20+55+110 | half_low | on | 0.9549 | 45.29% | 5.97 | 7,017 |
| **96** | **10+20+55+110** | **mid_channel** | **off** | **1.0004** | **46.59%** | **7.56** | **8,074** |
| 97 | 10+20+55+110 | mid_channel | on | 0.9212 | 45.15% | 5.98 | 5,664 |
| 98 | 10+20+110+220 | half_low | off | 0.9205 | 51.30% | 6.79 | 8,759 |
| 99 | 10+20+110+220 | half_low | on | 0.9246 | 45.08% | 5.57 | 6,727 |
| 100 | 10+20+110+220 | mid_channel | off | 0.9457 | 46.38% | 7.01 | 7,650 |
| 101 | 10+20+110+220 | mid_channel | on | 0.9492 | 44.70% | 5.57 | 6,912 |

Winner by the pre-declared rule (highest Sharpe): **trial 96 — fast
windows, mid-channel exit, no gate** (the exact experiment-7 winner
architecture, widened).

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR ≥ 0.95: FAIL — 0.831704** at N=101 deflation.
2. **Winner MDD ≤ 51.93%: PASS — 46.59%** (family-wide pass again:
   44.7-51.5%).
3. Winner turnover ≤ 53.1: PASS — 7.56.

**The family is a registered negative under its own pre-registration** —
the eighth. Stop condition remains far off (candidates-PBO 0.8746).

## The hypothesis is falsified, cleanly

Breadth did not add Sharpe — it subtracted it, in all eight pairings:

- Winner vs winner: 13-symbol 1.0004 vs BTC/ETH 1.1821 (−0.18).
- Every experiment-8 arm trails its experiment-7 counterpart on Sharpe
  AND on final equity (8,074 vs 14,231 at 1,000 start).
- Mechanisms, visible in the data: (a) **cash drag by construction** —
  1/13 equal budgets leave 7+ slots idle for the first years while
  SOL/AVAX/DOT are unlisted, and the ladder cannot reallocate idle budget
  (the cs path could; the ladder path holds it in cash); (b) **altcoin
  breakout quality** — the added symbols contribute more failed breakouts
  than trends (the 2021-05-19 −29% book day hits all 13 legs at once,
  where the BTC/ETH book held 2 legs).
- The barbell window set (arxiv 2510.23150) also underperformed fast in
  3 of 4 pairings — the redundancy claim did not transfer to this
  signal/universe.
- The gate read-out flipped versus experiment 7: on the diversified book
  the gate now IMPROVES MDD meaningfully (51.5→45.3 on half_low arms)
  and is roughly Sharpe-neutral — the double-brake verdict was
  BTC/ETH-specific, as suspected. Recorded for future signal designs.

What was NOT tested here (and remains the only registered-evidence route
left in this lineage): the SSRN paper's **vol-based position sizing** —
their breadth came with inverse-vol weights, not equal budgets. That is a
different allocation model, a new family, and a new engine feature; it
goes to the hypothesis pool, not to an automatic next run.

## Also recorded

- **Trial 37 at N=101: DSR 0.953212 — the registry's SECOND gate-4
  pass**, purely from cross-trial variance compression (1.69e-4). Its
  standing does not change: it was not its family's winner (trial 29
  was), its family is a registered negative, and its 67.53% MDD fails the
  risk bar by 15.6pp. A trial that passes one gate while failing the
  drawdown bar qualifies nothing. Recorded as deflation mechanics,
  fourth-order: high-Sharpe high-MDD arms survive deflation best, which
  is exactly why the MDD criterion exists.
- Trial 29 at N=101: DSR 0.986952 (still the benchmark; still sealed off
  from October).
- Trial 88 at N=101: DSR 0.932985 — the BTC/ETH Donchian winner GAINED
  ground from variance compression (0.9267 → 0.9330) and remains the
  best risk-compliant trial in the registry.

## Where the search stands after eight families

108 configurations tested honestly across two signal spaces and four
wrapper levers. The risk-compliant frontier is now: **trial 88
(Sharpe 1.182 / DSR 0.933 / MDD 33.05%)** — 0.017 of DSR short of the
statutory corner at current N. Paths registered in the hypothesis pool:
vol-based sizing on the Donchian book (SSRN-faithful, needs an
allocation-model engine feature) and the multi-horizon barbell variants
already parked. Every new family raises N and the bar with it — the
next pre-registration should weigh that arithmetic explicitly.

## Provenance

All 8 trials ran on clean tree `5e2d50e` (commit-first rule); staggered
mode verified against the registry window before the family ran (2676
returns, 2018-03-05 → 2025-07-01). Registry, return series, the N=101
report, and this document are committed together.
