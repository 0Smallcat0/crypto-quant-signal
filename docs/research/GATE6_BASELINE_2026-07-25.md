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

---

## Addendum 2026-07-28 (iteration 30) — no look-ahead (verified), but execution latency is unmodelled and larger than the modelled slippage

Five audits had not touched the single most consequential correctness
question in any backtest. This one does, and splits into a clean
acquittal and a quantified gap.

### Look-ahead: ruled out, empirically

The engine is explicit — `src/backtest/engine.py` carries
`generated_at_bar_close`, `executable_from_next_bar`, and executes at
the **next** bar's `open_price` / `open_time`. Code intent is not proof,
so the chain was traced end to end on trial 88's first trade:

| Stage | Value |
|---|---|
| signal `as_of` | 2018-03-04T23:59:59.999Z |
| target `as_of` | 2018-03-04T23:59:59.999Z |
| order `accepted_at` | 2018-03-05T00:00:00Z |
| fill `filled_at` / price | 2018-03-05T00:00:00Z / **11520.76** |

Against the source candles (`data/candles/BTCUSDT_1d.jsonl`):

| Day | open | close |
|---|---:|---:|
| 2018-03-04 | 11464.47 | **11515.00** |
| 2018-03-05 | **11515.00** | 11454.00 |

`11515.00 x 1.0005 = 11520.7575`, matching the recorded fill of
**11520.76** to the cent — the next bar's open plus exactly the modelled
5 bps of slippage. **The decision uses no information after its own bar
close, and the fill is the first price available afterwards. There is no
look-ahead.** This had never been documented; it is now, and the route is
closed.

### The gap the acquittal exposes

Because crypto trades continuously, `open[t+1] == close[t]` — 11515.00
in both cells above. The one-bar execution lag therefore provides **no
price protection at all**: the system fills at exactly the price it
decided on, plus slippage. That is legitimate arithmetic, but it encodes
an assumption: **zero decision-to-execution latency.**

The live system is not instantaneous:

| Clock | Lag after 00:00 UTC bar close |
|---|---|
| paper runtime, 08:05 Taipei | **~5 min** (00:05 UTC) |
| shadow recorder, 08:20 Taipei | **~20 min** (00:20 UTC, confirmed: `recorded_at` 2026-07-28T00:20:07Z for `date` 2026-07-27) |

BTC daily sigma over the backtest window (2018-03-05..2025-07-01,
n=2675) is **3.4068%**. Scaling by sqrt(t):

| Horizon | sigma | E abs move | vs modelled 5 bps slippage |
|---|---:|---:|---:|
| 5 min (runtime lag) | 0.4015%/sqrt(4) = 0.2007% | **16.0 bps** | **3.2x** |
| 20 min (shadow lag) | 0.4015% | **32.0 bps** | **6.4x** |
| 60 min | 0.6954% | 55.5 bps | 11.1x |

**The price dispersion across the execution delay is three to six times
the slippage the backtest charges.**

### What this does and does not establish

**It is dispersion, not cost.** A delay is symmetric in expectation
*unless* the signal is correlated with the move that follows it. The
adverse fraction cannot be measured from daily candles, so no cost
number is claimed here.

**But the sign is not neutral for this strategy.** Trial 88 is a Donchian
breakout: it fires precisely when price has just broken a level, which is
the moment continuation is most likely. The transaction-cost literature
names this case directly — implementation shortfall is "particularly
dangerous for breakout traders and momentum systems", because the fill
arrives after liquidity has shifted at the level. For a breakout rule the
delay cost is plausibly **directional against the system**, not
zero-mean.

**And it may sit outside what was stress-tested.** The trial-118
robustness battery held at 3x costs (Sharpe 1.152), covering roughly
60 bps round-trip. If even half of the 5-minute dispersion is adverse,
that is ~8 bps one-way / 16 bps round-trip added on top — inside the
tested range. At the 20-minute shadow lag, half-adverse would be ~32 bps
round-trip added, pushing total cost toward the edge of it. **The honest
statement is that the cost model's headroom is smaller than the 3x
stress suggests, by an amount this program cannot currently measure.**

### This is exactly gate 6's job, and gate 6 has not run

The gate-6 contract requires measuring "notification->execution delay
(simulated or journaled)" and recalibrating if round-trip cost exceeds
1.5x the assumed 25-30 bps. The checklist item "Paper period >= 3
calendar months completed" remains **unchecked** (iteration 27). This
addendum converts a checklist line into a quantified reason to run it.

### Closing it requires an operator decision, not a loop action

Two routes, both touching things the loop must not change unilaterally:

1. **Ingest intraday candles** (1m or 5m) for BTC/ETH over the window and
   measure the actual signed drift from bar close to +5 min and +20 min,
   conditioned on a signal firing. This is a data-ingestion task and a
   real measurement, not a bound.
2. **Add a field to the shadow tracks** recording price at bar close and
   at execution time, converting the gap into journaled evidence. This
   modifies a track that is actively recording, so it is the operator's
   call; it also strengthens Test 1 of
   `FORWARD_TRACK_READ_PREREGISTRATION.md` rather than adding a read-time
   metric, so it does not violate that pre-registration if done **now**
   rather than at a read.

Nothing here changes a gate rule, a recorded number, or the live
contract.

## Addendum 2026-07-28 (iteration 31) — the delay-cost concern, measured and de-escalated

The addendum above said the adverse fraction of the execution delay
"cannot be measured from daily candles, so no cost number is claimed."
**That was too pessimistic, and is corrected here.** Daily candles carry
one usable signal: where the **open** sits inside that day's high-low
range. If price rose after the open, the open sits low in the range — and
a delayed BUY would have paid more.

### Measurement

All 669 trial-88 fills matched against their execution-day candle:

| Group | n | mean open-in-range | delta vs baseline | t | mean daily range | implied drift |
|---|---:|---:|---:|---:|---:|---:|
| BUY fill days | 331 | 0.4910 | **-0.0167** | **-0.99** | 5.27% | **-8.8 bps** |
| SELL fill days | 338 | 0.5038 | -0.0040 | -0.25 | 5.98% | -2.4 bps |
| all days (baseline) | 6484 | 0.5077 | — | — | — | — |

**BUY days do lean the adverse way** — the open sits 1.67 percentage
points lower in its range than a typical day, meaning price rose after
the open more often than usual, which is the predicted breakout
signature. **But it is not significant (t = -0.99).**

**SELL days lean the *favourable* way.** For a sell, an open low in the
range means price rose afterwards, so a delayed sell gets a **better**
price. The -0.0040 there is a +2.4 bps benefit, not a cost.

**Net point estimate across a round trip: about -6.4 bps**, against
10 bps of round-trip slippage already modelled and roughly 40 bps of
headroom demonstrated by the trial-118 battery holding at 3x cost
(60 bps round-trip against a 20 bps baseline). **The delay cost, taken at
face value, sits well inside what was already stress-tested.**

### Two corrections to the previous addendum's framing

**1. The sqrt(t) scaling was conservative, not neutral.** It assumed
volatility is uniform across the day. It is not: Bitcoin volume and
volatility peak during the LSE/NYSE overlap (**14:00-16:00 UTC**) and
decline after **20:00 UTC**. The execution window here is **00:00-00:20
UTC** — the quiet part of the crypto day. The true dispersion across that
specific window is therefore **below** the 32 bps the uniform scaling
produced, and the 16 bps five-minute figure is likewise an overestimate.

**2. "Unmeasurable" was wrong.** It was measurable, imperfectly, from
data already on disk, and the loop should have tried before declaring it
out of reach.

### What this does NOT establish

**Power is limited.** With sd 0.3070 and n=331, the 95% detectable
deviation for BUYs is 0.0331 in open-in-range units, i.e. about
**17.4 bps**. This test can rule out adverse drifts **larger than ~17
bps**; it cannot resolve anything smaller. The measured -8.8 bps is
exactly in that unresolvable band.

**The proxy is coarse.** Open-in-range describes the whole 24-hour bar,
not the first 5 to 20 minutes. It is evidence about direction, not a
substitute for intraday measurement.

### Net effect on the standing concern

Iteration 30 raised execution latency as a possible threat to the cost
model's headroom. Iteration 31 measures it and finds **the right sign on
buys, the opposite sign on sells, neither significant, a net point
estimate inside the tested headroom, and a dispersion estimate that was
itself overstated.** The concern is **narrowed to "under 17 bps and
probably much less", not closed.** Gate 6's journaled measurement remains
the way to close it properly, and gate 6 still has not run.

## Addendum 2026-09-04 (iteration 57) — the paper runtime stopped deciding on 2026-07-31, exits 0 every day, and gate 6's clock for the live strategy has never started

This addendum was reached through §2's own pre-registered trigger. §2
closed with "**re-check at N ≥ 60 quotes**", written on 2026-07-25 at
N=44. Sixty-four calendar days later the re-check was run, and the reason
the threshold had not been crossed turned out to be the finding.

### The measurement

Read-only pass over `data/runtime/events.jsonl` (257 events) and
`data/runtime/daily_cycle.log`. Nothing in `configs/runtime/`, the live
contract, the store, or any file the 08:05 runtime reads was modified;
iron rules 1 and 2 of `docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md` hold.

| Event kind | Count | Last occurrence |
|---|---:|---|
| `cycle` | 29 | close 2026-07-30, recorded 2026-07-31T00:05:02Z |
| `signal` | 58 | `signal:ETHUSDT:2026-07-30T23:59:59.999000+00:00` |
| `target` | 29 | close 2026-07-30 |
| `order` | 9 | — |
| `fill` | 9 | — |
| `exec_quote` | 56 | `trading_day` 2026-07-30 |
| `health` | 35 | bar close 2026-09-03 |

Everything recorded after `2026-07-31T00:05:03Z` is **34 `health` rows and
2 `exec_quote` rows, and nothing else** — no cycle, no signal, no target,
no order, no fill. All 35 health rows carry the same payload:
`WARMUP_INSUFFICIENT_HISTORY` on `["BTCUSDT", "ETHUSDT"]`, one per bar
close from 2026-07-30 to 2026-09-03, with 2026-08-09 absent (the
already-recorded machine-off hole). The most recent block of
`daily_cycle.log`, from the 2026-09-04 08:05:01 run, reads
`"processed": false`, `"reason": "WARMUP_INSUFFICIENT_HISTORY"`,
`"close_time": null`, `"equity": null`, `"exec_quotes": 0`.

The scheduled task disagrees: `CryptoQuantDailySignalCycle` reports
`State=Ready`, `LastRunTime=2026/9/4 08:05:01`, **`LastTaskResult=0`**.

### Root cause — an off-by-one that cannot be satisfied

- `scripts/run_paper_runtime.py:59` sets `_LIVE_FETCH_LIMIT = 400`, and
  `_fetch_latest_candles` calls `fetch_historical_candles(..., limit=400,
  closed_only=True)`. Binance's `limit` counts the in-progress bar, so
  `closed_only=True` drops it. Measured live today against
  `api.binance.com`: **399 closed candles** for BTCUSDT and for ETHUSDT,
  first close 2025-08-01, last close 2026-09-03.
- `src/runtime/engine.py:73` sets `DONCHIAN_WARMUP_CANDLES = 400`, and
  `engine.py:123` selects it whenever
  `strategy_name == "donchian_breakout_ensemble"`. The guard at
  `engine.py:191-193` skips the cycle when `len(candles) < 400`.
- **399 < 400, every day, permanently.** The condition has no path to
  clearing itself: the fetch will never return a 400th *closed* bar while
  the limit is 400.

The date matches the cause exactly. Commit `2423bf6` ("Switch the live
signal to trial 118", 2026-07-31 22:56:33 +0800) changed
`configs/runtime/paper_runtime.yaml` from `daily_trend_ensemble` to
`donchian_breakout_ensemble`. The previous strategy's floor is
`DAILY_TREND_WARMUP_CANDLES = max((20, 65, 150, 200)) = 200`, comfortably
under 399, which is why 29 cycles ran cleanly before that evening and none
after. The last signal ever emitted carries SMA reason codes
(`ABOVE_SMA_20`, `ABOVE_SMA_65`, `BELOW_SMA_150`, `BELOW_SMA_200`,
`LADDER_HOLD`) — it is a trial-4 signal, not a trial-118 one.

`scripts/shadow_signal.py:45` uses the same `FETCH_LIMIT = 400` but has no
warmup floor, which is why the three forward shadow tracks are unaffected
and still recording (41 rows, last 2026-09-03). The two paths were proved
decision-equivalent on 138 of 138 historical windows before the switch;
that equivalence test ran offline on stored history and therefore could
not see a defect that only exists in the live fetch depth.

### What this costs, stated plainly

1. **The trial-118 paper period has zero processed cycles.** Not 36 days
   of evidence — zero. The 29 cycles on record were produced by trial 4,
   and commit `2423bf6` itself says the scoreboard before 2026-07-31 "is
   not continuous with what follows".
2. **Gate 6 cannot be executed in October 2026.** Its requirement is a
   signal runtime running ≥ 3 calendar months. The clock for the live
   strategy has never started. Fixed on 2026-09-04, the earliest
   completion is **2026-12-04**; every day unfixed moves that date.
3. **`PRE_HOLDOUT_PROTOCOL.md` §3.1 has two prerequisites that are now
   unreachable on their stated schedule** — "Paper period ≥ 3 calendar
   months completed (… 2026-07-03 → 2026-10-03 window at earliest)" and
   "Gate-6 baseline table refreshed with ≥ 60 quote days". Quote days are
   frozen at 28 and quotes at 56. §2's own N ≥ 60 re-check cannot fire.
   The protocol is frozen until the spend and **was not edited**; this is
   a report that reality has moved away from it, not a change to it.
4. **The dead-man switch has been reporting success throughout.**
   `scripts/run_daily_cycle.cmd` pings `%HEALTHCHECK_PING_URL%` on the
   `CYCLE_EXIT==0` branch and `/fail` otherwise. `processed: false` still
   exits 0, so the success branch was taken on all 36 days; the
   "HEALTHCHECK_PING_URL not set" fallback note appears only twice in the
   whole log (lines 16 and 76), so the ping was configured and attempted.
   The monitor is measuring process exit, not output. The precise
   published description of this failure mode is recorded in
   `RESEARCH_LOG.md` under 2026-09-04.

### What the loop may not do about it

All three candidate repairs — raising `_LIVE_FETCH_LIMIT` above 400,
lowering `DONCHIAN_WARMUP_CANDLES`, or reverting the strategy name — land
in `scripts/run_paper_runtime.py`, `src/runtime/engine.py`, or
`configs/runtime/paper_runtime.yaml`. **All three are files the daily
08:05 runtime reads, so iron rule 1 forbids the loop from touching any of
them.** This addendum diagnoses and escalates; the repair is the
operator's, and it should be paired with an outcome check (does today's
run append a `cycle` event?) rather than an exit-code check, or the next
instance of this will also take 36 days to notice.

### Effect on the standing answer

No backtest number changes and no verdict is revised. One framework
clause sharpens: "gates 5 and 6 have never been executed" becomes **gate 6
cannot be executed in October 2026, and the evidence stream it depends on
has been dead since the day the live signal became the candidate the
program is about.**

---

## Addendum 2026-09-05 (iteration 58) — the failure was never silent; it announced itself correctly 36 times, and every surface that reads the announcement reports the opposite

The 2026-09-04 addendum above characterised the outage with a borrowed
phrase, "a silent failure wearing a green badge", and concluded that the
monitor "measures process exit, not output". The first half is wrong for
this repository, and wrong in the direction of worse. The runtime
diagnosed itself correctly, in machine-readable form, once per failing
cycle, for 36 consecutive cycles. What failed is every consumer of that
diagnosis.

### 1. The outage is self-reported, correctly coded, and dated

`data/runtime/events.jsonl` holds **36 events of kind `health`**, every
one with payload `{"code": "WARMUP_INSUFFICIENT_HISTORY", "symbols":
["BTCUSDT", "ETHUSDT"]}`, emitted at `src/runtime/engine.py:196-202` on
the same branch that returns the skip. Their coverage, by candle close:

- **2026-07-30** — the same close the last successful `cycle` event
  processed (`cycle:2026-07-30T23:59:59.999+00:00`, recorded
  2026-07-31T00:05:02Z). The health row is appended *after* it in file
  order, so a later run that evening re-processed the same close and
  failed. Commit `2423bf6` landed 2026-07-31 22:56:33 +0800.
- **2026-07-31 through 2026-09-04** — one row per close, 36 dates, with
  exactly **one missing: 2026-08-09**, the hole already on record.

36 = 1 + (36 − 1). The event stream is complete and it says, every day,
precisely what is wrong and for which symbols.

### 2. Three operator-facing surfaces read the store; none reports the outage

**`/api/health` (`src/api/app.py:183-190`)** returns `"status": "OK"`
unconditionally. Its `last_cycle_close` comes from
`latest_of_kind("cycle")` — the 2026-07-30 close, now 36 days stale — and
the handler contains no comparison of that timestamp against anything.
A stale value is returned next to a hardcoded OK.

**`/api/gate` (`src/api/app.py:160-181`)** computes
`paper_trading.days` as `(datetime.now(UTC) - cycles[0].recorded_at).days`
— wall clock since the **first cycle ever recorded**,
`2026-07-03T03:00:21.953997+00:00`, which is a trial-4 cycle. Today that
is **64**. In the same payload, `cycles` is **29** and has not moved
since 2026-07-31. One number advances with the calendar; the other is
frozen; the endpoint presents them as equals.

**`src/api/page.py`** renders the first and hides the second.
`renderObs` (lines 290-300) sets the pill to `觀察期 ${days}/${target} 天`
with `target = 90`. `renderGate` (lines 365-374) prints
`${days} / ${target} 天 paper` above a progress bar of width
`min(100, days/target*100)`. `paper.cycles` is rendered **only in the
`demo_replay` branch** (line 372); in live mode the one number that would
expose the outage is fetched from the API and then never displayed.
Today the dashboard reads **觀察期 64/90 天** with the bar **71.1%** full.

### 3. The dates this produces, and they land on the protocol's own date

From `paper_started = 2026-07-03T03:00:21.953997+00:00`:

| Event | Date | Candidate cycles behind it |
|---|---|---:|
| Progress bar reaches 100% (`days = 90`) | **2026-10-01** | 0 |
| `days = 92`, i.e. three calendar months | **2026-10-03T03:00:21Z** | 0 |

§3.1's first prerequisite above reads "Paper period ≥ 3 calendar months
completed (… since 2026-07-03 → 2026-10-03 window at earliest)". On that
exact date the dashboard will show a full bar and a 92-day count, beside
a threshold block printing `paper_trading_months_min: 3`
(`src/api/app.py:179`), for a strategy that has produced **zero** cycles.
The number the operator would consult to check gate 6 will assert gate 6
is ready.

### 4. The one health line that is displayed says the stop is temporary, and cites the wrong floor

`src/api/page.py:194` maps the code to `暖身中（歷史不足200日）`. Two
defects in one string:

- **暖身中** ("warming up") frames a permanent condition as transient.
  The live fetch returns 399 closed bars against a floor of 400, so no
  amount of waiting clears it.
- **200** is not the active floor. 200 is
  `DAILY_TREND_WARMUP_CANDLES = max((20, 65, 150, 200))`
  (`src/features/daily_trend.py:17`), the SMA path's floor. The Donchian
  path's floor is `DONCHIAN_WARMUP_CANDLES = 400`
  (`src/runtime/engine.py:73`), selected at `engine.py:123`. The label is
  a hardcoded string that did not follow the strategy switch of commit
  `2423bf6`.

An operator who scrolled to the health card on any of the 36 days would
have read that the system was warming up and needed 200 days of history.

### 5. What this changes

- **Correct statement of the defect**, replacing the 2026-09-04 wording:
  not a silent failure, but a **correctly-detected, correctly-emitted,
  correctly-coded failure rendered by three surfaces as normal progress**,
  one of which crosses the gate-6 bar on its own on 2026-10-01.
- **The 2026-09-04 remediation is right but under-specified.** It asks
  for "an outcome check (does today's run append a `cycle` event?)". That
  outcome signal already exists *and is already queried* —
  `src/api/app.py:148` reads `events_of_kind("health")` for `/api/risk`.
  What is missing is four consumer-side changes: a staleness comparison
  in `/api/health`, a `days` counter derived from candidate cycles rather
  than wall clock, `cycles` rendered in the live branch, and a label that
  does not say 暖身中.
- **Route closed: "the operator could have caught this by looking."** No.
  Looking on any of the 36 days would have shown an advancing
  observation-period bar, `status: "OK"`, and at worst a line reporting
  warm-up.

### 6. What the loop may not do about it

All four repairs land in `src/api/app.py` and `src/api/page.py`. These
are operator-facing product surfaces, not research artifacts, and the
2026-09-04 addendum's stance — diagnose and escalate, do not repair —
carries over unchanged. No file under `src/`, `scripts/`,
`configs/runtime/` or any scheduled task was touched by this iteration.

### 7. Effect on the standing answer

No backtest number changes and no verdict is revised. One clause
sharpens: gate 6 cannot be executed in October 2026, **and the surface
the operator would consult to check that will say it can.**

### 8. Minor correction recorded under iron rule 5

The 2026-09-04 `LOOP_LOG.md` entry attributes the two gate-6
prerequisites to "`PRE_HOLDOUT_PROTOCOL.md` section 3.1". That file has
three sections and no §3.1; the prerequisites are §3.1 of **this**
document. The 2026-09-04 addendum's own body cites it correctly; only the
log summary slipped. Per append-only science no prior entry was edited —
the correction lives here and in today's entry.
