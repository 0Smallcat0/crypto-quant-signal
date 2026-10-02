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

---

## Addendum 2026-10-02 (iteration 73) — the anchor this document asserted is now measured: it holds exactly, it covers one track completely and the other only on close, and the re-fetch it depends on has one working host out of seven

Append-only. Nothing above this line is edited.
`FORWARD_TRACK_READ_PREREGISTRATION.md` remains **byte-for-byte unchanged**,
`scripts/shadow_signal.py` is unchanged, `data/candles/` was **not written**,
no exposure/drawdown/return/Sharpe was computed, no trial registered, no gate
report regenerated, holdout untouched.

### Why this was the thing to measure

Section 3 above asserts, in this document's own words:

> The recorded `close` per symbol per date **is** a re-fetch anchor for the
> forward part: today a re-fetch can be checked against **52 real recorded
> closes x 2 symbols** (~90 by the read date).

and section 5 states *"**No ingest was run**"*. So the sentence on which
operator option **2 — "Accept reconstruction … anchored on recorded closes for
the forward part"** rests has been, for 16 days, an **assertion that a check
would succeed**, never the check. Option 2 is the cheapest of the three and is
due before **2026-10-22**, now **20 days**. Section 3's own "risk is real
rather than theoretical" paragraph cites Concretum and TS-Arena for the
*direction* and says plainly that **neither magnitude is carried here** — so
this program had an outside reason to worry and no measurement of its own
provider. This addendum is that measurement.

Health checks are explicitly unrestricted by the frozen rule — *"Health checks
(does the file have a new row) are unrestricted and are not reads"*
(`FORWARD_TRACK_READ_PREREGISTRATION.md:78`). Comparing a recorded input
against its source computes no exposure, so it cannot produce Test 1's verdict
early; what is deliberately **not** done here is stated in the last section.

### Finding 1 — PASS, at full strength and in two shapes

Re-fetched **2026-10-02** through the recorder's own client and the recorder's
own base-url selector (`run_public_rest_smoke` ->
`first_passing_public_rest_base_url` -> `BinanceSpotPublicClient`), at the
recorder's own `FETCH_LIMIT = 400`:

| Quantity | Value |
|---|---:|
| Recorded rows per track, `2026-07-24..2026-10-01` | **69** |
| Independent recorded closes (2 symbols x 69 dates) | **138** |
| Compared cells (2 tracks x 69 dates x 2 symbols) | **276** |
| **String-exact agreement with the re-fetch** | **138 / 138** |
| Value mismatches | **0** |
| Recorded dates absent from the re-fetch | **0** |

Agreement is **string-exact to the last trailing zero** (e.g.
`84880.05000000`), not merely equal as decimals, so there is no formatting or
precision drift to reconcile.

**Request-shape control**, because the Concretum concern is about an *identical
historical query* returning different bars: the same comparison run with a
different request shape — `startTime`-paginated from 2026-07-23 via
`fetch_historical_candles_range` instead of a trailing `limit=400` — also
returns **138/138 string-exact, 0 mismatches**. The anchor does not depend on
how the window is asked for.

**Date alignment, which nothing before this had checked.** The comparison key
is the one `shadow_signal.append_day` writes — `closed[-1].open_time.date()`
for the date and `str(closed[-1].close_price)` for the value — so a
**one-day shift** in what the recorder calls "yesterday's close" would appear
here as 138 mismatches. It appears as zero. This matters because iteration 59's
verification was **internal**: it reproduced the equity path *from the recorded
closes*, which a mis-dated source would survive untouched. Finding 1 is the
first check in this program's record that can fail on a mis-dated input, and it
passes.

**Re-fetch depth, free and relevant to option 3.** The `limit=400` re-fetch
returned **399 closed candles, 2025-08-29..2026-10-01** — i.e. **329 bars
before the track start**, against the **21** warmup bars section 3 says Test 1
needs and the **>= 206** bars iteration 61 derived as the required replay
depth. The recorder's own 400 is sufficient on both counts, as section 3
already said; it is now confirmed against a live response rather than from the
constant.

**Coverage, and the one hole is the one already on record.** The exchange has
**70** closed candles in `2026-07-24..2026-10-01`; the track has **69** rows.
The single absent date is **2026-08-09** — iteration 72's lost row — and its
closes **are present in the re-fetch** (BTCUSDT `64901.59000000`, ETHUSDT
`1910.65000000`). So that loss is a lost **row**, not a lost **input**: the
input is recoverable, and the row is deliberately left absent because a
back-filled row is not forward evidence.

### Finding 2 — the anchor covers one track completely and the other only on close; section 3's "partly verifiable for one track" was too pessimistic for trial 88 and unquantified for trial 118

Section 3 says high/low is *"precisely the data trial 118's ATR exit
consumes"*. That is correct, and it has a consequence section 3 does not draw:
**trial 88 consumes none of it.** Read out of
`donchian_breakout_ensemble.py`, the `mid_channel` path reaches `close_price`
and nothing else (`:77` decision close, `:83` prior closes, `:94`/`:98` the
mid-channel exit level, `:101` the breakout test); `average_true_range`
(`:24-43`, the only reader of `high_price`/`low_price`) is reached **only**
from the `EXIT_ATR_CHANNEL` branch at `:88-96`, and that branch sits inside
`if was_on:`.

Counted from the **recorded reason codes** — ATR is consumed at date D for a
symbol iff at least one window was ON at D-1, which `WINDOWS_ON_k_OF_4`
records directly — with no call to `evaluate_donchian_ensemble`:

| | trial 88 (`mid_channel`) | trial 118 (`atr_channel`) |
|---|---:|---:|
| (date, symbol) cells reaching the ATR branch | **0 of 136** | **121 of 136 (88.97 %)** |
| In-window bars whose high/low Test 1 needs | **0** | **138 of 138** |
| Further pre-window bars needed, per symbol | **0** | **12** |
| Cells anchored by a recorded close | **138** | **138** |
| High/low cells carrying any recorded anchor | — | **0** |

**So Test 1's input over the forward window is 100 % anchored for trial 88 and
close-only for trial 118**, where the unanchored part is not a corner case:
the ATR branch is reached on **89 %** of decision cells, the high/low it needs
spans **every bar in the recorded window plus 12 more per symbol reaching back
into the unanchored 21-bar warmup gap**, and **not one** of those **162**
(symbol, date) bars has any recorded anchor at all.

Also measured, from the files alone and worth recording so it is not
re-derived: `exposure == WINDOWS_ON_k_OF_4 / 4` on **138 of 138** cells in
**both** tracks, exactly as `fraction = Decimal(on_count) / Decimal("4")`
(`:104`) requires, and the two tracks record **identical closes on 138/138
cells and identical dates on 69/69 rows** because both are served by one fetch
per run. Two consequences: the independent fact count above is **138, not
276**, and Test 1's recorded exposure column carries **no information beyond**
the recorded reason-code column.

### Finding 3 — DEFECT, new and not about Test 1: the re-fetch everything above depends on has one working host out of seven

Section 3 notes the fetch is *"conditional on Binance public REST being
reachable that day"* and stops there. Measured, **four independent probes** of
`paper_runtime.yaml`'s `rest_base_url_candidates` through this repository's own
preflight (`run_public_rest_smoke`):

| Probe | Pass | Failures |
|---|---:|---|
| 1 | **1 / 7** | 6 x `DNS resolution failed` |
| 2 | **1 / 7** | 6 x `ConnectTimeout` (TLS handshake) |
| 3 | **1 / 7** | 6 x `DNS resolution failed` |
| 4 | **1 / 7** | 5 x `ConnectTimeout`, 1 x `DNS resolution failed` |

The one that passes is **`https://data-api.binance.vision`** every time; the
six that fail are `api.binance.com`, `api-gcp`, `api1`, `api2`, `api3`,
`api4`, each classified by this repository's own preflight as
`ENVIRONMENT_BLOCKER`. The **verdict is stable at 1/7 and the mechanism is
not** — it moved between DNS failure and TLS timeout across probes taken
minutes apart — so no single mechanism may be claimed.
`developers.binance.com` also failed DNS from this host, which is why the
primary-source quotes in today's `RESEARCH_LOG.md` entry come from the GitHub
raw mirror.

Why this is a P1 finding and not a footnote:

1. **`fetch_candles` raises `SystemExit("no reachable public REST base url;
   shadow track skipped")` (`scripts/shadow_signal.py:79`) when none passes.**
   The daily track — *"the only unbiased evidence this program can still
   generate"* — therefore has a **single point of failure**, and the config's
   apparent 7-way redundancy contributes **zero** availability on this host.
2. **It is the reason iteration 72's repair is load-bearing.** Before
   2026-10-01 that `SystemExit` was swallowed by the wrapper and Task Scheduler
   recorded `LastTaskResult` 0. A single-host dependency plus a discarded exit
   code is exactly the pair that cost Friday 2026-07-31 on the weekly track.
3. **It bounds the October read.** Test 1's re-fetch of 112 bars per symbol is
   not merely *"conditional on Binance public REST being reachable"* — it is
   conditional on **one host** being reachable, and today's 138/138 agreement
   is single-sourced, so no independent-provider cross-check of the anchor is
   available from this machine.

Stated in the direction that costs the finding: `data-api.binance.vision` is
not a workaround. Binance's own `rest-api.md` says *"For APIs that only send
public market data, please use the base endpoint
**https://data-api.binance.vision**"*, and its klines maximum of **1000**
leaves the recorder's `FETCH_LIMIT = 400` well inside the documented ceiling.
The six blocked hosts are the **authenticated-trading** hosts this program is
forbidden to use anyway (product law, AGENTS.md section 2). The defect is not
that the working host is wrong; it is that **the list is one entry long in
practice and no document said so.**

### What this does and does not settle for the operator choice

- **Option 2 (accept reconstruction) is now evidence-backed rather than
  asserted** — for **trial 88 it is sound without qualification**, since its
  entire forward signal input is anchored and the anchor agrees exactly under
  two request shapes. For **trial 118 it remains a partial reconstruction**,
  and the size of the unanchored part is now a number: **162 bars of high/low,
  89 % of its decision cells, zero anchors.**
- **Option 3 (state the replay depth) is unaffected and still required.** The
  live response confirms a `limit=400` re-fetch reaches 329 bars before the
  window, comfortably above the **>= 206** derived in section 2.
- **Option 1 (archive from a named date) is now the only one that can close the
  trial-118 gap**, and archiving is still forward-only: 2026-07-24 onward
  cannot be repaired, and every further day deferred adds to the 162.
- **New, and not one of the three:** whether a second market-data provider
  should be configured so that the anchor and the October re-fetch are not
  single-sourced. This is a change to a file the live runtime reads, so it is
  **operator-only** and is **not** made here.

Scope limits, stated rather than buried. One re-fetch on one date establishes
agreement **on that date**; Binance's own documentation contains **no**
statement that historical klines are never revised, so this is an empirical
observation and not a vendor guarantee, and the Concretum/TS-Arena direction
recorded in section 3 is uncontradicted in principle. The 1-of-7 result is a
property of **this host on 2026-10-02** — an outside project records the same
block as deployment-dependent and varying between two machines of one project
(`itsafo/fintech-data-warehouse` #9) — not a property of Binance.

### What was deliberately not done

**Test 1 was not run.** No exposure was recomputed,
`evaluate_donchian_ensemble` was not called, and Finding 2's ATR-branch counts
come from the **recorded** reason codes rather than from a replay — precisely
so that the read is not moved earlier than 2026-10-22, which the frozen rule
forbids. The lost **2026-08-09** exposure is therefore still **not**
reconstructed even though its closes are now known to be re-fetchable, for the
same reason iteration 72 left it alone. Nothing was written to `data/candles/`,
which would have created an archive stamped 2026-10-02 for decisions taken up
to 70 days earlier and would have overwritten a shared research input the live
runtime reads.

### Method appendix (reproducible; no script added to `scripts/`)

Run from the repository root with `PYTHONPATH` set to it; writes nothing.

```python
import asyncio, json
from datetime import UTC, datetime
from pathlib import Path
from src.config import load_config
from src.data import (BinanceSpotPublicClient, first_passing_public_rest_base_url,
                      run_public_rest_smoke, symbol_from_binance_native)
from src.domain import Timeframe

SYMBOLS = ("BTCUSDT", "ETHUSDT")
config = load_config(Path("configs/runtime/paper_runtime.yaml"))
timeout = float(config.data_source.timeout_seconds)
results = run_public_rest_smoke(config.data_source.rest_base_url_candidates,
                                timeout_seconds=timeout)          # Finding 3
base = first_passing_public_rest_base_url(results)

async def closes():
    out = {}
    async with BinanceSpotPublicClient(rest_base_url=base, timeout_seconds=timeout) as c:
        for s in SYMBOLS:
            for k in await c.fetch_historical_candles(
                    symbol=symbol_from_binance_native(s), timeframe=Timeframe("1d"),
                    limit=400, received_at=datetime.now(UTC)):
                if k.is_closed:                   # the recorder's own key, verbatim:
                    out[(s, k.open_time.date().isoformat())] = str(k.close_price)
    return out                                    # str(closed[-1].close_price)

got = asyncio.run(closes())
for name in ("trial88", "trial118"):              # Finding 1
    rows = [json.loads(x) for x in Path(f"data/runtime/shadow_{name}.jsonl")
            .read_text(encoding="utf-8").splitlines() if x.strip()]
    cells = [(r["date"], s, str(r["close"][s])) for r in rows for s in SYMBOLS]
    print(name, len(cells), sum(got.get((s, d)) == v for d, s, v in cells))
```

Finding 2 needs no fetch: read `reason_codes[symbol]`, take `k` from
`WINDOWS_ON_k_OF_4`, and count dates where the **previous** row's `k >= 1`
(the `if was_on:` guard at `donchian_breakout_ensemble.py:84`); the high/low
bars needed are the 14 ending at each such date (`:31`,
`start = index - window + 1`).
