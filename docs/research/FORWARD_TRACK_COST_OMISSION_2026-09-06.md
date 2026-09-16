# The forward tracks are costless — and the read rule's only full-power test cannot see it

Date: 2026-09-06 · Iteration 59 · Zero registry cost (no backtest run, no
trial registered, no gate report regenerated, no frozen file edited).

## Why this is a document and not a log line

It records a **forced operator choice with a deadline**, in the same shape
as `GATE4_FRAGILITY_2026-07-28.md`. The subject is
`FORWARD_TRACK_READ_PREREGISTRATION.md`, which is frozen under iron rule 3,
so — following the precedent set by `GATE3_CANDIDATE_COMPOSITION_2026-09-01.md`
— the finding lives here and **that file is left byte-for-byte unchanged.**

## What was measured

Every forward shadow row carries `close`, `exposure` and `equity`. That is
enough to reconstruct the recorder's arithmetic from the data alone,
without trusting any comment. Two candidate models were fitted to all 99
recorded transitions across the four tracks:

- **lag** — `equity(D)/equity(D-1) - 1 = sum_i w_i(D-1) * r_i(D)`, weights
  from the *previous* row. This is the no-look-ahead accounting.
- **same** — the identical expression with weights from row `D`. This is
  what a look-ahead defect would produce.

For the two-symbol crypto tracks, `w_i = exposure_i / 2`; the recorder
splits capital equally across symbols (`BUDGET`,
`scripts/shadow_signal.py:198`), so `exposure` is the fraction of that
symbol's own sleeve, not of the book. Neither model charges anything to
trade.

| Track | transitions | max abs(actual − **lag**) | max abs(actual − **same**) |
|---|---:|---:|---:|
| `shadow_trial88` | 42 | **8.140e-28** | 0.070368 |
| `shadow_trial118` | 42 | **8.973e-28** | 0.039635 |
| `shadow_tw0050` | 7 | exact (7/7 within 1e-12) | matches on 3/7 |
| `shadow_gld` | 8 | exact (8/8 within 1e-12) | matches on 4/8 |

`1e-28` is `Decimal` rounding noise at the recorder's own 40-digit
precision. The `same` model matches only on days when exposure did not
change, which is exactly what an unbiased recorder looks like.

## Two results, and they point in opposite directions

### PASS — there is no look-ahead, and this is now verified from the data

`scripts/shadow_signal.py:191` carries the comment *"Notional
mark-to-market: yesterday's exposure earns today's return."* Until today
that was a claim about the code. It is now a **measured property of the
recorded series**: the lagged model reproduces all 99 transitions to
rounding, and the same-day model fails on every turnover day. The forward
evidence stream does not peek. That is the single most important thing a
forward track has to get right, and it got it right.

### DEFECT — the equity path pays nothing to trade

The residual against the **costless** lag model is zero. Not small — zero.
There is no fee, no slippage, no spread, on any of the 11 turnover days in
`shadow_trial88`, the 5 in `shadow_trial118`, or any in the other two.
Confirmed at source: the block at `scripts/shadow_signal.py:191-202`
contains no cost term of any kind.

The backtest these tracks exist to validate does charge. Trial 88's and
trial 118's registry rows both record
`cost_assumptions = {fee_bps: 10, slippage_bps: 5, cost_multiplier: 1,
fill_rule: next_bar_open}` — **15 bps per fill**, applied in
`src/backtest/engine.py:457-465`.

### Magnitude, charged at the registry's own 15 bps

Turnover is `sum_i abs(w_i(D) − w_i(D−1))`, which already counts each side
separately, so total turnover × 15 bps is the correct uncharged amount.

| Track | turnover, 42 d | annualized | uncharged drag | recorded equity | cost-charged equity |
|---|---:|---:|---:|---:|---:|
| `shadow_trial88` | 2.0000 | 17.381 /yr | **2.607 %/yr** | 1098.783795 | 1095.535887 |
| `shadow_trial118` | 1.0000 | 8.690 /yr | **1.304 %/yr** | 1150.438199 | 1148.760415 |

Over 42 transitions the gap is **0.2965 %** (trial 88) and **0.1461 %**
(trial 118). Extrapolated at the same turnover to the read rule's own
dates: **4.981 %** of equity by trial 88's MinTRL date 2028-06-29, and
**2.289 %** by trial 118's 2028-04-28.

`shadow_tw0050` (turnover 1.0000 over 7 transitions) and `shadow_gld`
(1.2500 over 8) are constructed the same way. **No drag figure is given
for them**: Taiwan and US-ETF cost assumptions live in the other
repository's registry and were not verified here, and inventing a rate
would be exactly the kind of number iron rule 5 forbids.

## Why it matters: all three pre-registered tests are biased one way

The bias is **one-signed**. A costless path can only make the track look
better than the thing it is shadowing — never worse.

- **Test 1, implementation agreement — the primary test, and it is blind
  to this.** As written it *"compare[s] the recomputed exposure path
  against the recorded one, per symbol, per date"*. Exposure only. The
  exposure path is correct — this audit confirms it — so **Test 1 passes
  while the defect is present**, at 4 rows and at 4000. The rule's one
  full-power test cannot detect its own accounting gap.
- **Test 2, refutation by drawdown breach.** Fires only if forward
  drawdown exceeds 33.05 % (trial 88) / 33.24 % (trial 118). Costs deepen
  drawdown, so omitting them makes the one-sided refutation check *less*
  likely to fire. **Stated honestly, the effect is currently negligible**:
  forward max drawdown is **3.4094 %** recorded against **3.4456 %**
  cost-charged, i.e. 0.036 points on a 29.6-point gap. Trial 118's is
  3.7291 % either way. This is a structural objection, not a live one.
- **Test 3, return.** The forward Sharpe is inflated by **+0.0843**
  (trial 88) and **+0.0280** (trial 118) on the 42-day sample. More
  seriously, the 2028-06-29 date was derived from trial 88's
  **cost-inclusive** backtest SR of 1.1823, while the series that will be
  measured on that date is **cost-exclusive**. The MinTRL date and the
  quantity it licenses a verdict on are not the same quantity.

**Test 3 compliance, stated explicitly.** The forward Sharpe *levels* were
computed in the course of this audit and are **not cited here as support
for anything**, in either direction, and no document may so cite them
before 2028-06-29. Only the *difference* between two accounting treatments
of one path is used, because only the difference is the subject.

## Is running this audit early itself a rule breach?

Stated plainly so the operator can overrule. The read rule declares
*"Health checks … are unrestricted and are not reads"* and reserves Test 1
for implementation agreement. This is an implementation-correctness audit
of the recorder — Test 1's own category — and it changes **no read date,
introduces no benchmark, and draws no verdict about return.** But it is
also true that the rule's *"What may not be added"* clause forbids
introducing a metric at read time, and a cost-charged equity variant is a
variant. The distinction relied on is that **today is not a read date**
and no verdict is drawn. If the operator judges otherwise, the correct
remedy is to record that judgement, not to unwrite the measurement.

## The forced choice, and why the loop will not make it

Three options. Each has a cost, and **the loop takes none of them.**

1. **Repair `shadow_signal.py` to charge costs from tomorrow.** Creates a
   splice: one append-only series under two accounting regimes, with the
   join date chosen after seeing 43 rows. The read rule forbids
   back-filling, so the pre-repair rows cannot be made comparable.
2. **Declare a cost adjustment applied at read time.** Cleanest
   arithmetically, and forbidden as written — it is a post-hoc metric
   choice, which the rule's *"What may not be added"* clause exists to
   prevent. It needs an explicit operator amendment, made **before** the
   2026-10-22 read, not at it.
3. **Accept the bias and state it in every citation of the tracks.**
   Costs nothing, changes nothing, and requires that no document ever
   again describe these tracks as validating a cost-inclusive backtest
   without naming the 2.607 %/yr and 1.304 %/yr gaps.

Option 2 is the only one that makes the 2028 verdict answer the question
it was designed to answer, and it is the only one that must be decided
**in advance**. That is the deadline: an amendment written after
2026-10-22 is written with data in hand.

## What this does not do

No frozen rule edited, no read date moved, no verdict drawn about return,
no registry row or return series touched, no trial registered, no backtest
run, no gate report regenerated, no new script written, no shadow file
modified, no file under `configs/runtime/`, `src/runtime/` or `src/api/`
touched, holdout untouched. `scripts/shadow_signal.py` is **left exactly as
it is** — repairing it is option 1, and option 1 is the operator's call.

## Method

Read from `data/runtime/shadow_trial88.jsonl` (43 rows, 2026-07-24 to
2026-09-05, one missing date 2026-08-09 already on record),
`data/runtime/shadow_trial118.jsonl` (43),
`D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` (8) and
`shadow_gld.jsonl` (9); cost assumptions from
`docs/reports/research/trial_registry.jsonl` trials 88 and 118; cost
application verified in `src/backtest/engine.py:457-465`; recorder
arithmetic verified in `scripts/shadow_signal.py:191-202`. All arithmetic
in `Decimal`. Nothing was written to any of these files.

---

## Addendum 2026-09-16 (iteration 61) — a second decision falls due on the same date

This document asks the operator to choose, before **2026-10-22**, among
three ways of handling the cost omission. A separate audit run that day
found **two more choices with the same deadline**, on the same tracks and
the same Test 1:

1. **The tracks archive no input.** Shadow rows record `close` only, the
   local candle store ends **2026-07-02**, and the forward window opens
   **2026-07-24** — so a Test 1 replay must **re-fetch 112 bars per symbol**
   at read time, unanchored for the 21 warmup bars and for all
   open/high/low (which trial 118's ATR exit consumes). Archiving is
   forward-only and cannot be back-filled.
2. **The read rule states no replay depth.** A replay seeded at the 110-bar
   channel floor can disagree with a correct recorder by up to **96 bars**
   of state, and the rule's verdict for any mismatch is an unconditional
   *"halt and fix"*. Required depth **≥ 206 bars**; the recorder's own 400
   is safe.

The same audit **closed one route in this document's favour**: the
recorder's rolling 400-bar re-seed is harmless, with a measured **194-bar
margin** over **12 524 seed-runs**, so the exposure path this document
relies on is reproducible in principle. The defect is the input, not the
procedure.

Nothing in this document is retracted or amended. Full measurement:
`FORWARD_TRACK_REPLAYABILITY_2026-09-16.md`.
