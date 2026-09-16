# Forward-track replayability — can Test 1 actually be executed on 2026-10-22?

Date: 2026-09-16 (iteration 61) · Backtest-only, local history only · Zero
registry cost (no trial registered, no backtest run, no gate report
regenerated) · **No forward metric computed and none cited.**

## Why this document exists

`FORWARD_TRACK_READ_PREREGISTRATION.md` names **Test 1 — implementation
agreement** as the *primary* test and the **only one the 2026-10-22 read
can settle at full power**:

> Replay the strategy offline over the forward window and compare the
> recomputed exposure path against the recorded one, per symbol, per date.
> **Pass** = exact agreement on every recorded date. **Any mismatch =
> implementation defect. Halt and fix before any other reading of the
> track.**

Iteration 59 established what Test 1 **cannot see**: the exposure path is
correct while the equity path charges nothing to trade, so Test 1 passes
with the cost defect present. Nobody has asked the prior question —
**can Test 1 be run at all, and is it well defined?** Gate 6 was audited
that way in iterations 57-58 and turned out to be unexecutable. Test 1 is
36 days from its first read date. This is that audit.

Three questions, three separate answers: one **PASS**, one **missing
specification**, one **defect**.

---

## 1. PASS (measured, not assumed): the rolling re-seed is harmless

### The concern

The recorder and an offline replay are **different procedures**, and
Test 1 demands *exact* agreement between them.

`scripts/shadow_signal.py` fetches `FETCH_LIMIT = 400` daily candles on
every run (line 45) and `decide()` loops `for index in range(max(windows),
len(closed))` from `states = None` (lines 113-130). So each run seeds a
fresh **all-OFF** state at slice index `max(windows) = 110` and evolves it
for **290 bars** to reach today — and because the 400-bar window rolls, the
seed bar advances one day per run. An offline replay over the forward
window seeds **once**. If the ensemble's state has not forgotten its
initial condition within the burn-in, the two procedures can disagree for
reasons that are not implementation defects.

### The mechanism (why it converges at all)

For one window `w`, two runs differing only in seed date satisfy
**late ⊆ early**: a late-seeded run can never be ON while an early-seeded
run is OFF, because `OFF -> ON` (`close > max(prior w closes)`,
`donchian_breakout_ensemble.py:99`) depends only on current data, not on
prior state. The two re-converge on the first bar where either

- `close > max(prior w closes)` — both ON, or
- `close < exit_level` — both OFF.

Divergence therefore survives **only** while the close sits inside the band
`[exit_level, max(prior w closes)]`. Convergence is guaranteed and
absorbing; the horizon is not.

### The measurement

Local history only: `data/candles/BTCUSDT_1d.jsonl` and
`ETHUSDT_1d.jsonl`, n = 3242 each, 2017-08-17..2026-07-02. Ground truth =
one pass seeded once at index 110 and run to the end. For every legal seed
position `s` (3131 per symbol) a fresh all-OFF run is started at `s` and
the bars until its 4-tuple matches ground truth are counted — search
capped at 800. **12 524 seed-runs** (3131 x 2 symbols x 2 tracked configs):

| Symbol | Track | exit | max burn-in needed | p99 | p95 | median | mean | seeds > 290 | unconverged |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BTCUSDT | trial 88 | `mid_channel` | **96** (seed bar 2024-03-14) | 65 | 31 | 0 | 6.09 | **0** | 0 |
| BTCUSDT | trial 118 | `atr_channel` | **29** (seed bar 2025-01-22) | 18 | 10 | 0 | 2.01 | **0** | 0 |
| ETHUSDT | trial 88 | `mid_channel` | **68** (seed bar 2025-08-23) | 47 | 26 | 0 | 4.66 | **0** | 0 |
| ETHUSDT | trial 118 | `atr_channel` | **28** (seed bar 2020-04-30) | 18 | 11 | 0 | 2.05 | **0** | 0 |

**Worst case over all 12 524 runs: 96 bars, against the recorder's 290.
Margin 194 bars. Zero seeds needed more than 290; zero failed to converge
within 800.**

**Internal check the measurement passes.** On this data the `atr_channel`
exit level (`max(prior) - 2*ATR`) sits *above* the `mid_channel` level
(`(max+min)/2`), so its divergence band is narrower and it should converge
faster. Measured 29 / 28 against 96 / 68 — it does. The mechanism and the
numbers agree, which is weak evidence that neither is an artifact of the
other.

**Route closed:** the rolling re-seed is not a threat to Test 1, and no
future iteration should re-open it. **Stated at its true strength:** 96 is
an *empirical maximum over 2017-2026 history*, not a proved bound. The
convergence argument guarantees the horizon is finite, not that it is
under 96.

---

## 2. MISSING SPECIFICATION: the rule never states the replay depth

This is the consequence of §1, and it cuts the other way.

Test 1 says "replay the strategy offline" and **states no warmup depth**. A
replay seeded at the channel floor — 110 bars, the obvious choice — carries
**zero** state burn-in. The measurement above says it can then disagree with
the recorded path by up to 96 bars' worth of state, and the rule's verdict
for a disagreement is unconditional: *"Any mismatch = implementation defect.
Halt and fix before any other reading of the track."*

**So the rule as written can manufacture a false halt on a correct
recorder.** The repair is a specification, not a metric — it changes nothing
about *what* Test 1 measures, so it does not fall under the rule's
*"What may not be added"* clause on the same footing as a new metric:

> A Test 1 replay must carry at least **110 + 96 = 206 bars** of history
> before the first compared date. The recorder's own **400** is a safe
> choice and introduces no new number.

It is nonetheless an amendment to a frozen document, so it is the
operator's to make, and it must be made **before** 2026-10-22 rather than
at the read — a depth chosen after seeing a mismatch is a post-hoc choice.

---

## 3. DEFECT: Test 1 is not offline, and its input was never archived

The rule's word is **"offline"**. There is no offline input.

| Claim | Verified against |
|---|---|
| Local candle store ends at bar **2026-07-02** | `data/candles/BTCUSDT_1d.jsonl`, `ETHUSDT_1d.jsonl` (n=3242, last `open_time` 2026-07-02) |
| Forward window opens **2026-07-24** | first row of `data/runtime/shadow_trial88.jsonl` |
| Shadow rows record **`close` only** | row fields are exactly `close, config, date, equity, exposure, reason_codes, recorded_at, strategy` — no `open`/`high`/`low` |
| trial 118 needs high/low | `average_true_range()` uses `high_price`/`low_price` (`donchian_breakout_ensemble.py:29-42`), used by the `atr_channel` exit |
| Run logs archive no candles | `data/runtime/shadow_runs/` — 88 files, ~400 bytes each, stdout only |
| No archive anywhere | grep for a forward-window `open_time` across `data/` and `docs/` returns nothing |

### Consequence, in bars

Executing Test 1 on 2026-10-22 requires re-fetching, **per symbol**:

- **21 warmup bars** — 2026-07-03..2026-07-23, the gap between the local
  store and the forward window, and
- **91 forward bars** — 2026-07-24..2026-10-22,

= **112 daily bars per symbol** that exist in **no local file**. That fetch
is (a) conditional on Binance public REST being reachable that day —
`shadow_signal.fetch_candles()` already exits with *"no reachable public
REST base url; shadow track skipped"* when it is not — and (b)
**unverifiable against what the recorder actually saw**, because nothing
was archived at decision time.

### The partial anchor, stated in the direction that costs the argument

This is not a total loss of provenance. The recorded `close` per symbol per
date **is** a re-fetch anchor for the forward part: today a re-fetch can be
checked against **52 real recorded closes x 2 symbols** (≈90 by the read
date). It is **no anchor** for the 21 warmup bars, and **no anchor at all**
for open/high/low on any date — which is precisely the data trial 118's ATR
exit consumes. So Test 1's input is *partly* verifiable for one track and
*not* verifiable for the other.

### That this risk is real rather than theoretical

Logged the same day in `RESEARCH_LOG.md`: Concretum Group measured one
provider's re-download of an identical historical query returning
materially different bars (>350 of 390 one-minute bars flat on some
sessions, equity curve diverging under identical strategy logic), and
TS-Arena — a live forecast pre-registration platform — archives the exact
input snapshot every round on the stated grounds that re-fetching returns
updated or corrected values. Neither is crypto-daily and **neither
magnitude is carried here**; they establish direction only.

---

## 4. What the 2026-10-22 read can establish, now bounded on three sides

| Test 1 cannot detect | Established |
|---|---|
| A trading-cost error — it compares the exposure path, which is correct, while the equity path charges nothing | iteration 59, `FORWARD_TRACK_COST_OMISSION_2026-09-06.md` |
| A signal-math error — `scripts/shadow_signal.py:41`, `src/backtest/engine.py:57` and `src/runtime/engine.py:65` all import the **same** `evaluate_donchian_ensemble`, so any replay shares the implementation under test | this document, §3 |
| Anything about an archived input — there is none; the input is reconstructed 90 days after the decisions | this document, §3 |

**What remains, and it is not nothing.** Test 1 still detects a **harness**
defect — wrong slice, wrong lag, dropped symbol, corrupted append, silent
skip — and against a re-fetch anchored on ~90 recorded closes it is a real
check on the recorder's persistence path. It is a **narrower** test than
the rule's wording implies. The operator should see the narrowing before
2026-10-22, not discover it at the read.

---

## 5. What this document does NOT do

`FORWARD_TRACK_READ_PREREGISTRATION.md` is left **byte-for-byte
unchanged** — specifying the replay depth is an operator amendment, not a
loop action. `scripts/shadow_signal.py` is left **exactly as it is**, on
iteration 59's precedent: it is a live recording track. **No ingest was
run** — re-fetching into `data/candles` today would create an archive
stamped 2026-09-16 for decisions taken up to 54 days earlier, which is not
the missing provenance, and it would overwrite a shared research input. No
trial registered, no backtest run, no gate report regenerated, no forward
row read for a metric, no Sharpe/return/drawdown computed, holdout
untouched.

## 6. The operator choice, and why it has a clock

Archiving is **forward-only and cannot be back-filled**. Every day the
choice is deferred is one more day of provenance that can never be
recovered. Three options; (3) is independent of (1)/(2) and is needed
either way:

1. **Archive from a named date.** Write the fetched candle window (or its
   hash) alongside each shadow row from a date chosen in advance. Costs a
   change to the recorder — operator-only. Does not repair 2026-07-24
   onward.
2. **Accept reconstruction.** Record, before the read, that Test 1's input
   is re-fetched rather than archived, anchored on recorded closes for the
   forward part and unanchored for the 21 warmup bars and for all
   open/high/low. Cheapest; makes the limitation explicit instead of
   discovered.
3. **State the replay depth** in the read rule (>= 206 bars, or simply
   reuse the recorder's 400) so Test 1 cannot manufacture a false "halt and
   fix". **Needed under either of the above**, and it must be fixed
   *before* 2026-10-22.

Companion decision, same deadline, different subject:
`FORWARD_TRACK_COST_OMISSION_2026-09-06.md` section "three options".

---

## Method appendix (reproducible; no script added to `scripts/`)

Run from the repository root with `PYTHONPATH` set to it. Reads
`data/candles/` only; writes nothing.

```python
from decimal import Decimal
from src.data.files import read_candles_jsonl
from src.strategies import evaluate_donchian_ensemble

WINDOWS = (10, 20, 55, 110)
SEED_INDEX = max(WINDOWS)                     # shadow_signal.decide() loop floor
RECORDER_BURNIN = 400 - SEED_INDEX            # shadow_signal.FETCH_LIMIT - floor
TRACKS = (("trial88", "mid_channel", Decimal("3")),
          ("trial118", "atr_channel", Decimal("2")))
CAP = 800

def ground_truth(candles, exit_mode, atr_multiple):
    states, out = None, {}
    for i in range(SEED_INDEX, len(candles)):
        frac, _, states = evaluate_donchian_ensemble(
            candles, i, windows=WINDOWS, exit_mode=exit_mode,
            previous_states=states, atr_window=14, atr_multiple=atr_multiple)
        out[i] = (frac, states)
    return out

def convergence_lag(candles, gt, s, exit_mode, atr_multiple):
    states = None
    for i in range(s, min(len(candles), s + CAP + 1)):
        _, _, states = evaluate_donchian_ensemble(
            candles, i, windows=WINDOWS, exit_mode=exit_mode,
            previous_states=states, atr_window=14, atr_multiple=atr_multiple)
        if states == gt[i][1]:
            return i - s
    return None
```

Reported per symbol and track: `max`, p99, p95, median and mean of
`convergence_lag` over every seed `s` in
`range(SEED_INDEX, len(candles) - 1)`, the count exceeding
`RECORDER_BURNIN`, and the count not converging within `CAP`.

Slicing equivalence, checked before relying on it: the recorder passes a
400-bar slice, so `candles[index - window]` is slice-relative. At slice
index 110 with `window = 110` the lookback is positions 0..109 and the ATR
lookback is 96..110 — both inside the slice — so evaluating at absolute
index `a` of the full series and at the matching slice index reference the
identical bars. The seed **position** is therefore the only difference
between the two procedures, which is what is measured above.
