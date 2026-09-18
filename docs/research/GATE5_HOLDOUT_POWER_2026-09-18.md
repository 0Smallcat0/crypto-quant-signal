# Gate 5 — what can the October holdout spend actually decide?

Date: 2026-09-18 (iteration 63) · Backtest series only · Zero registry
cost (no trial registered, no backtest run, no gate report regenerated) ·
**The holdout was not read, not fetched, and not touched; `spent` is still
`false`.** Every number below comes from `docs/reports/research/` and
`data/candles_preholdout/` — pre-holdout artifacts, all ending 2025-07-01.

## Why this document exists

`AUTONOMOUS_RESEARCH_LOOP.md` lists three states that could unblock this
program. Iterations 25 and 59-62 characterised the first one (forward
validation) until nothing was left unmeasured: all three tests of the
2026-10-22 read are mechanism checks, and none can speak to the edge.

The second lever has never been characterised at all:

> 2. The October holdout spend, per `PRE_HOLDOUT_PROTOCOL.md`,
>    operator-run.

`HOLDOUT_INTEGRITY_2026-07-28.md` checked that the holdout is **clean** —
no trial crossed the boundary, the trim is mechanical, `spent` is `false`.
Nobody ever checked whether it is **decisive.** Cleanliness and power are
different properties, and a holdout can be perfectly sealed and still
unable to settle the question it is reserved for.

This document measures the power. It returns **one referent defect, one
near-coin-flip, and one bar that cannot fire** — the same three-part shape
the forward read returned, reached independently.

---

## 0. Sources verified before anything was computed

| Trial | Registry `annualized_sharpe` | Reproduced | Registry `max_drawdown_fraction` | Reproduced | Registry `final_equity` | Reproduced |
|---|---:|---:|---:|---:|---:|---:|
| 4 | 1.022989 | **1.0230** | 0.519332 | **51.9332%** | 14221.28 | **14.2213x** |
| 7 | 1.127022 | **1.1270** | 0.473748 | **47.3748%** | 9280.36 | **9.2804x** |
| 118 | 1.241113 | **1.2411** | 0.332402 | **33.2402%** | 16898.58 | **16.8986x** |

Drawdown and terminal equity reproduce exactly; Sharpe reproduces once the
registry's sample (n−1) variance convention is used, which is what the
table above does.

The benchmark series used in §3 is reconstructed from
`data/candles_preholdout/` as a **no-rebalance 50/50 BTC/ETH hold** over
2018-03-04..2025-07-01. Provenance is not asserted, it is checked: that
construction terminates at **5.9764x**, matching the registry's recorded
`benchmark_final_equity` of 5976.443218 on all three trials **to four
decimal places**. A daily-rebalanced 50/50 does not match it (6.2597x), so
the no-rebalance series is the registry's benchmark and the rebalanced one
is not used anywhere below.

Holdout geometry, from `docs/reports/research/holdout_lock.json` metadata
only (`holdout_start` 2025-07-02, `spent: false`):

| Horizon | Days | What it is |
|---|---:|---|
| **L = 366** | 2025-07-02 .. 2026-07-02 | the holdout that exists in the archive today (`data/candles/` ends 2026-07-02) |
| **L = 478** | 2025-07-02 .. 2026-10-22 | the holdout if the operator re-ingests before spending on the read date |

---

## 1. DEFECT: N1 stopped naming what it named, and nobody noticed

`PRE_HOLDOUT_PROTOCOL.md` §2 fixes two nominations, sealed 2026-07-19
(commit `970f1e5`) and never editable again:

> - **N1 — the live contract**: `daily_trend_ensemble`, no overlay. The
>   Goal O subject.
> - **N2 — the experiment-2 winner**: vol overlay `target 0.30 / window
>   20d / monthly` on the unchanged ladder (**trial 7's exact
>   configuration**).

N2 names a trial id. **N1 names a role**, and on 2026-07-31 — twelve days
after the seal — commit `2423bf6` "Switch the live signal to trial 118"
moved that role to a different strategy.
`configs/runtime/paper_runtime.yaml` says so in its own comment:

> Switched 2026-07-31 from daily_trend_ensemble (trial 4) to trial 118.

So on the read date the sealed phrase "the live contract,
`daily_trend_ensemble`, no overlay" points at two different objects and
they are not the same strategy: trial 4 is the lookback ladder, trial 118
is `donchian_breakout_ensemble` with an ATR-channel exit.

**The sealed text settles its own ambiguity, on internal evidence.** The
pass bar is stated as *"annualized Sharpe ≥ 0.5 (half the pre-holdout
level — decay tolerance chosen blind)"*. Half of trial 4's 1.0230 is
**0.5115**. Half of trial 118's 1.2411 would be **0.6206**. The bar the
author wrote is 0.5, so **N1 as sealed is trial 4's configuration**, and
that reading is fixed by arithmetic inside the frozen document rather than
by anyone's recollection.

That resolves what N1 means and creates the problem:

- **Reading A (correct, per the arithmetic above).** The single-use spend
  evaluates a configuration that **has not been live since 2026-07-31**
  and that the program itself replaced. Its §2 consequence — "N1 passes →
  Goal O proceeds to its report with gate 6's paper evidence" — refers to
  a Goal O subject that no longer exists, and gate 6's clock for what *is*
  live has never started (iteration 57: the runtime's last `cycle` is
  2026-07-31, **day 49** today).
- **Reading B (substitute trial 118).** Then the nomination moved after
  the seal, toward a configuration chosen on backtest results produced
  after it — the switch commit quotes those results in the config file. §2
  forbids exactly this in substance: *"No third configuration may be added
  regardless of any future backtest result."*

Neither act was improper on its own. The protocol binds nominations, not
the runtime, and the switch is operator-attributed — iteration 40 recorded
the commit on 2026-08-03 and checked its effect on the shadow tracks. What
went unrecorded for **49 days** is the interaction: an indexical
nomination silently re-pointed. It is on the record now, seven weeks
before the read date, rather than on the day of the spend where it would
look like an excuse.

---

## 2. The Sharpe half is close to a coin flip, in both directions

§2's first pass bar is a **point estimate** — holdout-segment annualized
Sharpe ≥ 0.5 — with no confidence requirement attached. At a 366-day
horizon that estimate carries the standard error the program has already
adopted for the forward read (Bailey & López de Prado, the same
distributional machinery as gate 4's DSR; the method reproduces the
pre-registration's published SE column to three digits at L=182 and L=365
and to 0.3% at L=90, so it is the same machinery and not a new one).

At **L = 366**:

| Nomination | pre-holdout SR | SE(SR) | P(pass \| the edge is fully intact) | P(**pass** \| the edge is **completely dead**, true SR = 0) |
|---|---:|---:|---:|---:|
| **N1-A** trial 4 (sealed) | 1.0230 | 1.0034 | 0.6989 → **fails 30.1% of the time** | **0.3091** |
| N2 trial 7 | 1.1270 | 1.0030 | 0.7341 → fails 26.6% | 0.3091 |
| N1-B trial 118 (live now) | 1.2411 | 1.0012 | 0.7704 → fails 23.0% | 0.3088 |

A strategy whose edge has entirely evaporated **passes gate 5 roughly
three times in ten.** A strategy whose edge is perfectly intact **fails
roughly three times in ten.** This is a single-use, irreversible test
whose FAIL consequence is that "the strategy family returns to research"
and whose PASS consequence is that Goal O proceeds to its report.

The empirical cross-check agrees with the analytic figure. Over all
366-day windows of the 2676-day pre-holdout history, N1-A clears 0.5 in
**68.07%** of them against the analytic 69.89%; N2 in 72.26%, N1-B in
71.31%. These windows overlap heavily — 2311 of them contain only
**7.31** non-overlapping equivalents — so they describe what the series
actually did and the analytic column carries the probability claim. They
agree, which is the point of computing both.

---

## 3. The bar does not separate the strategy from doing nothing

The sharper question is not "does a dead strategy pass" but "does the bar
distinguish the strategy from the alternative the operator already has".
Same windows, same bar, the registry's own benchmark:

| Series | pass rate, L=366 | pass rate, L=478 |
|---|---:|---:|
| **registry benchmark — 50/50 BTC/ETH, held** | **0.6815** | **0.6712** |
| N1-A trial 4 (sealed) | 0.6807 (**−0.08pp**) | 0.7485 (+7.73pp) |
| N2 trial 7 | 0.7226 (+4.11pp) | 0.7767 (+10.55pp) |
| N1-B trial 118 | 0.7131 (+3.16pp) | 0.7731 (+10.19pp) |

**At the horizon the holdout actually has today, the sealed nomination
clears gate 5's bar slightly less often than simply holding BTC and ETH.**
Stated without spin in both directions: the gap is horizon-dependent and
reverses to +7.7pp if the operator re-ingests to 478 days before spending,
and a Sharpe bar applied to two series of different volatility is not a
like-for-like tournament. What survives both caveats is the magnitude: a
bar that a passive hold clears in roughly **two of every three** year-long
windows is not a bar that identifies skill. It is a bar that mostly
detects whether the year was good for crypto.

---

## 4. The drawdown half cannot fire — the same defect as forward Test 2

§2's second bar is *holdout-segment max drawdown ≤ pre-holdout max
drawdown + 10pp*. Iteration 62 found the forward read's Test 2 compares a
full-sample maximum against a 90-day one; gate 5 does the same thing with
a 2676-day maximum against a 366-day one, and then adds 10 percentage
points of further slack.

| Nomination | bar | worst 366-day drawdown in the **whole** pre-holdout history | bar ÷ worst-ever | in-sample windows breaching |
|---|---:|---:|---:|---:|
| N1-A trial 4 | 61.9332% | 48.3826% | **1.2801x** | **0 / 2311** |
| N2 trial 7 | 57.3748% | 42.1087% | **1.3625x** | **0 / 2311** |
| N1-B trial 118 | 43.2402% | 30.3857% | **1.4230x** | **0 / 2311** |

The zero is structural, not luck: a sub-window's running peak resets at
its first bar and is never above the full series' running peak at the same
date, so a sub-window's drawdown can never exceed the full-sample maximum
it is being compared against — before the +10pp is even added. The holdout
is genuinely out-of-sample so the bar is not *impossible* there, but the
in-sample statement is exact: **in the entire recorded history of all
three nominations, no 366-day stretch ever came within 12.85 percentage
points of its own bar** — the gaps are 13.5506 pp (trial 4), 15.2661 pp
(trial 7) and 12.8545 pp (trial 118).

As in iteration 62, the bar is not unreachable in principle. The
registry's own benchmark — the thing an operator holds if the strategy is
abandoned — has a worst 366-day drawdown of **81.2218%**, above every bar
in the table. What the drawdown half detects is therefore **the exit
mechanism failing**, not the edge decaying. It sits beside forward Test 1
and Test 2, and this is now the third pre-declared drawdown bar in this
program measured to have that property.

---

## 5. The gate's own bar needs 6x to 10x more holdout than will ever exist

The cleanest way to state §2 is to ask the program's own question of it.
MinTRL is the minimum track length at which an observed Sharpe is
distinguishable from a benchmark SR*. The forward read set SR* = 0 and got
706 days. Gate 5 sets **SR\* = 0.5**, which needs strictly more data:

| Nomination | MinTRL vs SR\*=0.5, 90% | date the holdout reaches it | MinTRL 95% | date |
|---|---:|---|---:|---|
| **N1-A trial 4 (sealed)** | **2207.8 d** | **2031-07-19** | **3636.3 d** | **2035-06-16** |
| N2 trial 7 | 1534.8 d | 2029-09-14 | 2527.7 d | 2032-06-03 |
| N1-B trial 118 | 1095.1 d | 2028-07-01 | 1803.4 d | 2030-06-09 |

Against the 366 days the holdout has today, the sealed nomination is short
by a factor of **6.0x** at 90% confidence and **9.9x** at 95%. Even the
best-case substitution needs until **2028-07-01** — one day later than the
forward track's own 2028-06-29 MinTRL date, reached by a completely
independent route.

An external check, found in this iteration's step-2 search and recorded in
`RESEARCH_LOG.md`: an August 2026 paper (arXiv 2608.23808) applies the
identical Bailey–López de Prado MinTRL formula as one of four validation
gates and reports that in its synthetic validation, at **252 bars (~1
year)** of history, **zero** strategies earned its robustness seal —
including genuine ones — rising to 17% at five years and 73% at twenty.
Independent construction, same conclusion about what one year of data can
carry.

---

## 6. What this closes

**Lever 2 of the three is now characterised, and it is not a verdict
machine.** Combining §§1-5:

- The October holdout **cannot confirm** the edge: its bar needs 6-10x
  more data than the window will ever hold, and a dead strategy clears
  that bar ~31% of the time.
- It **cannot refute** the edge: an intact strategy fails ~30% of the
  time, and the drawdown half has never come within 12.85pp of firing in
  2676 days of history.
- It **cannot identify skill**: at 366 days a passive BTC/ETH hold clears
  the same bar at essentially the same rate.
- And it **cannot cleanly name its own subject** until the operator
  resolves what N1 points at, with both readings carrying a cost.

Route closed, stated as a rule for future iterations: **no proposal may
treat the October holdout spend as evidence that decides whether the edge
works.** It remains a legitimate single-use out-of-sample *read* — the
numbers it produces are honest and unseen — but its pass/fail verdict is
close to a coin flip and must never be reported as a gate the program
"passed" or "failed" in the discriminating sense.

This is the same finding the forward read produced, now reached from the
other lever. Of the three unblocking states named in the contract, **two
have now been measured and neither decides anything**; the third is an
operator override of P3 that the program's own PBO measurement says would
produce an untrustworthy winner.

---

## 7. Options, none of them taken

Nothing here was repaired. `PRE_HOLDOUT_PROTOCOL.md` is frozen and was not
edited; the pass bars are unchanged; no nomination was substituted.

**(A) Resolve N1 to trial 4 and spend as sealed.** Honest to the frozen
document and costs nothing procedurally. The cost is that the single
irreversible spend is consumed on a configuration that has not been live
for seven weeks, and its PASS branch routes to a Goal O report whose
subject no longer exists.

**(B) Resolve N1 to trial 118 and record the substitution openly**, with
the §2 conflict stated in the spend document rather than discovered later.
Costs the protocol's central guarantee — the nomination would have been
chosen after seeing post-seal backtest results — and trial 118 is
specifically the trial whose gate-4 pass is one-trial fragile (iterations
26 and 55). The mitigation, which is real but partial: 0.5 is *not* half
of trial 118's Sharpe, so the bar was demonstrably not fitted to it.

**(C) Do not spend in October.** The holdout keeps accumulating and
`spent` stays `false`. Under the sealed nomination it reaches 90%
confidence in **2031** — beyond any horizon this program has planned for —
but under trial 118 it reaches it on **2028-07-01**, which is the same
date the forward track independently arrives at. The cost is that the one
reserved piece of clean evidence stays unread for at least two more years,
and §2's decay-tolerance bar would have to be re-derived for whatever is
live then, which cannot be done blind any more.

This is the **fifth** operator choice now due before 2026-10-22, joining
the cost omission (iteration 59), the archive-vs-reconstruct choice and
the replay-depth specification (iteration 61), and Test 2's framing
(iteration 62).

---

## Method note — exactly reproducible, no new script

The one-script budget is unspent; the measurement is inline and reruns
verbatim from this note. Inputs: `docs/reports/research/trial_returns/trial-{4,7,118}.json`
(2676 daily returns each, 2018-03-05..2025-07-01),
`docs/reports/research/trial_registry.jsonl`,
`data/candles_preholdout/{BTC,ETH}USDT_1d.jsonl`, and `holdout_lock.json`'s
metadata only.

- **Sharpe**: `mean/std * sqrt(365)` with the sample (n−1) std, matching
  the registry convention verified in §0.
- **SE of the Sharpe estimate at length L**: `sqrt((1 − g3·SR +
  (g4−1)/4·SR²)/(L−1)) · sqrt(365)` with per-period SR and the series' own
  skew `g3` and raw kurtosis `g4`.
- **P(pass)**: `1 − Φ((0.5 − SR_true)/SE)`, with SR_true set to the
  pre-holdout Sharpe for the intact case and to 0 for the dead case.
- **MinTRL**: `1 + (1 − g3·SR + (g4−1)/4·SR²)·(Φ⁻¹(c)/(SR − SR*))²` with
  per-period SR and SR* = 0.5/sqrt(365).
- **Rolling windows**: every contiguous L-length slice of the return
  series (2311 at L=366, 2199 at L=478); drawdown computed with the peak
  reset at each window's first bar.
- **Benchmark**: units bought at the first common date and held, per §0.

## What this iteration did not do

The holdout was not read, fetched, or unsealed; `spent` remains `false`
and no candle at or after `holdout_start` was opened. No gate rule was
modified, no frozen pre-registration or contract clause edited, no
registry row or return series touched, no trial registered, no backtest
run, no gate report regenerated, no shadow file written to or read for a
metric, no forward number computed or cited, no file under
`configs/runtime/`, `src/` or `scripts/` changed, and no prior result
document or log entry rewritten.
