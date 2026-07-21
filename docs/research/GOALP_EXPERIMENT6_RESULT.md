# Goal P experiment 6 — result: multi-horizon factor does not raise the ceiling; sixth negative closes the lineage

Executed: 2026-07-21 (report generated 16:00 UTC) · Trials: **70-85**
(registry N: 69 → 85)
Pre-registration: `docs/research/GOALP_EXPERIMENT6_PREREGISTRATION.md`
(unmodified; third same-sitting override recorded there)
Gate report: `docs/reports/research/gate_report_2026-07-21.json`
(regenerated at N=85, 2676 obs)

## Family table (16 configs; gate fixed at SMA200/btc/2%/daily)

| Trial | Horizons | K | Cadence | Filter | Sharpe | MDD | Turnover | Final equity |
|---:|---|---:|---|---|---:|---:|---:|---:|
| 70 | 28+56 | 2 | weekly | off | 0.8693 | 52.57% | 11.54 | 12,913 |
| 71 | 28+56 | 2 | weekly | on | 0.8887 | 54.32% | 11.94 | 14,067 |
| 72 | 28+56 | 2 | monthly | off | 0.8472 | 58.59% | 7.93 | 12,085 |
| 73 | 28+56 | 2 | monthly | on | 0.8112 | 58.59% | 7.60 | 10,286 |
| 74 | 28+56 | 3 | weekly | off | 0.8887 | 55.62% | 12.29 | 13,230 |
| 75 | 28+56 | 3 | weekly | on | 0.9716 | 53.25% | 11.55 | 18,188 |
| 76 | 28+56 | 3 | monthly | off | 0.9167 | **48.74%** | 8.33 | 13,355 |
| 77 | 28+56 | 3 | monthly | on | 0.8803 | 52.37% | 7.12 | 11,396 |
| **78** | **28+56+112+224** | **2** | **weekly** | **off** | **0.9855** | **53.49%** | **5.80** | **19,764** |
| **79** | **28+56+112+224** | **2** | **weekly** | **on** | **0.9855** | **53.49%** | **5.80** | **19,764** |
| 80 | 28+56+112+224 | 2 | monthly | off | 0.8513 | 55.42% | 4.38 | 11,346 |
| 81 | 28+56+112+224 | 2 | monthly | on | 0.8516 | 55.42% | 4.35 | 11,358 |
| 82 | 28+56+112+224 | 3 | weekly | off | 0.9236 | 51.84% | 6.54 | 13,057 |
| 83 | 28+56+112+224 | 3 | weekly | on | 0.9223 | 51.84% | 6.46 | 12,991 |
| 84 | 28+56+112+224 | 3 | monthly | off | 0.8589 | **49.40%** | 5.30 | 9,893 |
| 85 | 28+56+112+224 | 3 | monthly | on | 0.8576 | **49.67%** | 5.24 | 9,838 |

Winner by the pre-declared rule (highest Sharpe): **trials 78/79, an exact
tie** — the full blend at K=2/weekly produces identical books with the
filter on or off (the blended score never went negative on a selected
symbol, so the filter arm never triggered). The tie is between two
registry rows of ONE effective configuration; every verdict number below
is shared, so no tie-break rule is needed and none is invented post hoc.

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR ≥ 0.95: FAIL — 0.834456** at N=85 deflation.
2. **Winner MDD ≤ 51.93%: FAIL — 53.49%**, missed by 1.56pp (the
   narrowest miss of the lineage).
3. Winner turnover ≤ 53.1: PASS — 5.80.

**The family is a registered negative under its own pre-registration** —
the project's sixth. Stop condition remains unmet (candidates-PBO 0.8241,
all-columns 0.5533).

## The structural verdict: this lineage's ceiling is below the bar

- The JFQA multi-horizon claim did NOT replicate here: the short-pair
  arms (28+56) top out at Sharpe 0.97, and the best blend (0.986) is
  statistically indistinguishable from experiment 5's single-lookback
  gated arm (0.978). Changing the selection signal inside the cs-momentum
  family moved nothing.
- The feasible MDD region widened again — four arms now sit inside the
  statutory bar (trials 76, 84, 85 at 48.7-49.7%, plus exp-5's 62/64) —
  but the best in-bar Sharpe is 0.917 (DSR 0.778). The corner needs
  roughly Sharpe ≥ 1.3 at N=85 deflation; nothing in this lineage has
  come within 0.13 of that while respecting the drawdown bar.
- Across experiments 3→6 the winner's DSR reads 0.962 (ungated, 75% MDD),
  0.811, 0.911, 0.834 — the gate buys drawdown compliance by giving back
  exactly the Sharpe the deflation bar needs. **Conclusion: cross-
  sectional momentum on this 13-symbol universe, gated or overlaid in any
  of the 64 registered ways, cannot satisfy both statutory bars at once.
  The lineage is closed.** Further arms on this architecture would spend
  N without new information.

## Also recorded

- **Trial 29 at N=85: DSR 0.985589** — fourth consecutive rise
  (0.9621 → 0.9765 → 0.9802 → 0.9856) as 32 more similar-Sharpe columns
  compressed cross-trial variance to 1.85e-4. Same standing as before:
  winner of a failed family, only DSR-passing trial in the registry,
  untouchable by October's fixed nominations.
- Trial 37 reached DSR 0.9494 — a second trial now sits at the gate's
  threshold, both from the ungated cs family (the high-MDD side).
- Filter-arm degeneracy (78 = 79 bit-for-bit) is recorded as a grid
  design lesson: an arm whose trigger never fires burns a registry slot;
  future pre-registrations should pick arms that provably bind.

## What happens next (a genuine fork, queued for the loop)

Two honest directions remain, and they are DIFFERENT signal spaces, not
another wrap on this one:

1. **Donchian breakout ensemble** (Zarattini/Pagani/Barbon SSRN 2025,
   already in RESEARCH_LOG): daily tactical breakout with vol sizing on a
   BTC+altcoin universe — a different entry/exit logic whose published
   MDD profile fits the statutory bar. Engine cost: a breakout signal
   path (new, bounded).
2. **Accept the ceiling and consolidate**: stop spending N, let the
   October holdout adjudicate N1/N2 as sealed, and direct the loop's
   iterations at gate-6 evidence and the TW-version cross-audit backlog.

The next pre-registration (a later sitting unless the operator overrides
again) must pick ONE. The holdout stays sealed; October is unaffected.

## Provenance

All 16 trials ran on clean tree `a726b3a` (commit-first rule). Registry
rows carry cs_*, gate, and horizon parameters machine-readable. Registry,
return series, the N=85 report, and this document are committed together.
