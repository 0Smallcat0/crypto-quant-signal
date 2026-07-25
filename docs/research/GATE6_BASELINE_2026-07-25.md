# Gate-6 baseline refresh + holdout spend rehearsal note — 2026-07-25

Iteration-12 gate-6 evidence work (autonomous research loop). No code
paths were touched; this document is a post-hoc analysis of the
existing `data/runtime/events.jsonl` stream plus an
operator-facing rehearsal of `PRE_HOLDOUT_PROTOCOL.md`. Iron rules
1 and 2 of `docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md` were
honored — runtime code untouched, holdout unread.

## 1. Baseline refresh (extends iteration-11 snapshot)

Iteration 11 (2026-07-24) recorded 42 `exec_quote` events over
21 trading days × 2 symbols. Today, +2 days accumulated:

| Symbol   | N (quotes) | Days | First → Last            | Median spread (bps) | Max spread (bps) | Round-trip est (bps) |
|----------|-----------:|-----:|-------------------------|--------------------:|-----------------:|---------------------:|
| BTCUSDT  | 22         | 22   | 2026-07-03 → 2026-07-24 | 0.0000              | 0.0000           | 20.00                |
| ETHUSDT  | 22         | 22   | 2026-07-03 → 2026-07-24 | 0.0500              | 0.0600           | 20.10                |

Round-trip estimate = `2 × median_spread_bps + 2 × fee_bps`
(fee = 10 bps per side, matching `configs/costs/`). Gate-6 cap is
37.5–45 bps (`VALIDATION_GATE_CONTRACT.md §6`, `1.5 × 25–30 bps`).
**Verdict unchanged from iteration 11: cost model comfortably inside
the calibration bar on the two live symbols so far.** Neither
symbol's spread widened; sample is still well short of the 90-day
window §6 asks for.

## 2. New — decision→capture drift statistic (queued gate-6 stat)

Iteration 11 flagged decision→capture drift as the queued
measurement gap. It can be computed today from the already-recorded
event schema (`close_time` = bar-close boundary at
23:59:59.999 UTC; `captured_at` = quote-fetch timestamp), no
runtime edit required.

Per-quote drift over the 44-event sample (identical distribution for
both symbols — capture is symbol-agnostic within one cycle run):

| Statistic        | Value (seconds) | Value (human)   |
|------------------|----------------:|-----------------|
| Median           | 308.4           | ~5m 08s         |
| Mean             | 4099.7          | ~68m 20s        |
| Min              | 306.5           | ~5m 07s         |
| Max              | 71273.9         | ~19h 47m        |

**Observation.** The mode is `~5 minutes` — the daily cycle fires at
08:05 Taipei = 00:05 UTC. Two outliers pull the mean:
2026-07-06 (drift ~3.4 h) and 2026-07-11 (drift ~19.8 h), both
recoveries from a missed cycle in the daily-run scheduler. Runtime
already handles this correctly — the quote is still recorded, and
the daily cycle catches up — but the drift metric captures the
asymmetry: **the tail is bounded by "roughly one day" because the
cycle re-fires the next morning at latest.** Two catch-ups out of 22
runs (9%) is inside the noise the runbook already tolerates.

**Slippage implication.** At the median drift of 5 min, price drift
between bar close and quote capture is limited by BTC/ETH intraday
vol at that horizon — roughly 5-10 bps for the majors — well below
the 25-30 bps cost model's headroom. At the 19h tail, the assumption
breaks; but such captures already trigger a next-day cycle correction
(same-day fill uses the fresh quote, not the stale one). No
recalibration required at this sample size; **re-check at N ≥ 60
quotes.**

## 3. Operator-facing holdout spend rehearsal (2026-10)

Purpose: walk the exact command sequence for the single-use holdout
spend defined in `docs/contracts/PRE_HOLDOUT_PROTOCOL.md`, so the
operator (only party authorized to invoke `--spend-holdout`) has a
one-page reference in October. **No commands in this document may
be run before the paper period completes and the operator signs
off — this is documentation, not a runbook execution.**

### 3.1. Prerequisites (checked before nomination)

- [ ] Paper period ≥ 3 calendar months completed
      (`docs/reports/` records ledger reconciliation + no critical
      crashes since 2026-07-03 → 2026-10-03 window at earliest).
- [ ] Gate-6 baseline table (§1 above) refreshed with ≥ 60
      quote days; round-trip cost still ≤ 45 bps.
- [ ] `docs/reports/research/holdout_lock.json` still shows
      `spent=false` (never touched by any research iteration).
- [ ] Registry `N` frozen for the spend window
      (no families run between nomination and spend).

### 3.2. The two nominations (fixed 2026-07-19, immutable)

- **N1**: `daily_trend_ensemble` no overlay — the live-contract Goal
  O subject.
- **N2**: vol overlay `target=0.30 / window=20d / rebalance=monthly`
  on the unchanged ladder (trial 7's exact configuration).

No third nomination is legal, regardless of any 2026-07-25 finding
(trial 88 / trial 118 / anything else). Adding a third would
require accumulating a NEW holdout window and starting the clock
over.

### 3.3. Command sequence (single session, no re-runs)

The two read-outs share ONE unsealing event. Order matters — N1
first, then N2, no interpretation between them.

```bash
# 1. Verify holdout still sealed (must print spent=false)
python -m src.backtest.runner --check-holdout-lock

# 2. Spend event — N1 first, note references the protocol file
python -m src.backtest.runner \
    --config configs/strategies/daily_trend_ensemble.yaml \
    --spend-holdout --i-understand-single-use \
    --operator-note "N1 per PRE_HOLDOUT_PROTOCOL.md §2 (2026-10 spend)"

# 3. Spend event — N2, SAME session, no re-interpretation
python -m src.backtest.runner \
    --config configs/strategies/daily_trend_ensemble_vol_overlay_t030_w20_monthly.yaml \
    --spend-holdout --i-understand-single-use \
    --operator-note "N2 per PRE_HOLDOUT_PROTOCOL.md §2 (2026-10 spend)"

# 4. Publish gate report over the now-spent state
python -m src.backtest.gate_report --output docs/reports/GATE6_SPEND_2026-10.md
```

Exact CLI flag names above match the current `src/backtest/runner.py`
surface as of 2026-07-25 by contract intent, not verified today —
the operator MUST re-run `python -m src.backtest.runner --help`
before the October session and confirm each flag exists verbatim.
Config filename for N2 to be confirmed against `configs/strategies/`
before spend day; if the exact filename differs, the operator
adjusts the config path verbatim — no parameter tweaks in the
command line, only pointing at the pre-registered config file.

### 3.4. Pre-declared pass bars (from `PRE_HOLDOUT_PROTOCOL.md §2`)

For each nomination, both must hold on the holdout segment:

- Annualized Sharpe ≥ 0.5.
- Max drawdown ≤ pre-holdout MDD + 10pp.

### 3.5. Consequence table (immutable, from §2)

| Nomination | PASS                                  | FAIL                              |
|------------|---------------------------------------|-----------------------------------|
| N1         | Goal O proceeds to report with gate-6 | Strategy family returns to research; FAIL report is the product |
| N2         | Pre-registered candidate for NEXT contract (starts own paper qual) | No effect on N1 verdict          |

**N2 passing does NOT promote it to qualified** — it has no paper
period yet. N2 is a research read-out, not a shortcut around gate 6.

### 3.6. What the rehearsal explicitly forbids

- Peeking at the holdout in any form before the spend session.
- Re-running the spend "with fixed parameters" if either
  nomination fails — the failure IS the result.
- Adding a third nomination after seeing either N1 or N2's number.
- Editing `PRE_HOLDOUT_PROTOCOL.md` after 2026-07-25 (only typo
  fixes are legal, per that file's opening paragraph).

## 4. What this document is NOT

- Not a pre-registration. No trial IDs are reserved. No new families
  are announced.
- Not a runtime change. `src/runtime/quotes.py` untouched — the
  drift statistic in §2 is a post-hoc query over already-recorded
  events, not a new runtime emission.
- Not a research verdict. The standing decision from LOOP_LOG.md
  (2026-07-25 late — "no new families") is unchanged.

Next iteration continues Q4 work per contract: shadow-track health
check, incremental gate-6 sample growth, holdout untouched until
the operator signs the October spend off in a separate session.
