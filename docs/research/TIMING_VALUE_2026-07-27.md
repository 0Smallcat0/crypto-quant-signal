# Does the timing rule do anything? Controlled for exposure, in three markets

Diagnostic, 2026-07-27. `scripts/analyze_timing_value.py` over four
already-registered reports. No backtest, no registry row, no holdout
contact.

## Why the previous comparison was not good enough

"Beat buy-and-hold" compares a partly-invested system against a
fully-invested benchmark. The verdict therefore depends on how strong that
market happened to be, not only on the system. Experiment 8 lost that test
purely because its universe rose 13.53× rather than 6.05×
(`REGISTRY_VS_BENCHMARK_2026-07-26.md`, retraction box).

**The control that removes the confound:** a passive twin holding the same
asset at the system's own **average gross exposure**, continuously. Same
time-in-market, no signal. If the system beats its twin, the timing
decisions added value; if not, the signal machinery is an expensive way to
be partially invested.

The twin pays **no trading costs**, though holding a constant exposure
requires daily rebalancing, while the system pays full costs. Every edge
below is therefore conservative for the system.

## Result

| Book | Avg exposure | System | Twin | **Edge** | Sys MDD | Twin MDD |
|---|---:|---:|---:|---:|---:|---:|
| crypto trial 88 (2 sym) | 0.379 | 14.26× | 3.03× | **4.70×** | 33.05% | 43.60% |
| crypto trial 94 (13 sym) | 0.301 | 9.39× | 3.39× | **2.77×** | 51.54% | 36.73% |
| taiwan trial 23 | 0.477 | 2.15× | 2.95× | **0.73×** | 30.85% | 30.96% |
| gold trial 24 | 0.419 | 2.44× | 2.44× | **1.00×** | 25.01% | 21.17% |

## What it says, market by market

**Crypto: the timing rule works, and it works in both universes.** 4.70×
the twin on BTC/ETH and 2.77× on the 13-symbol book. This is the first
measurement that survives the benchmark-strength confound, and it
**vindicates experiment 8**: that family did not fail. It beat its
exposure-matched twin by 2.77× and only lost the raw buy-and-hold test
because its market rose more.

Note the asymmetry, which is not in the system's favour: on BTC/ETH timing
improved return *and* drawdown (33.05% against 43.60%). On 13 symbols it
improved return but **worsened** drawdown (51.54% against 36.73%).

**Taiwan: timing destroyed value.** Edge 0.73×. Holding 47.7% of 0050
continuously would have returned 2.95× against the system's 2.15× — **at
the same drawdown** (30.96% against 30.85%). The signal is strictly
dominated: less return, no risk benefit.

**Gold: timing did exactly nothing.** Edge 1.00×, to two decimals. And the
twin's drawdown is *lower* (21.17% against 25.01%). Holding 41.9% of GLD
statically would have matched the return with a smaller worst loss. The
sleeve's entire signal machinery is overhead.

## The consequence for the three-sleeve combination

The combination is not "one rule working in three markets". Measured, it is:

- **one market where the timing rule genuinely works** (crypto), and
- **two legs equivalent to, or worse than, a static partial position**
  (gold 1.00×, Taiwan 0.73×).

That yields a directly testable prediction: replacing the gold and Taiwan
sleeves with static partial holdings — 41.9% GLD, 47.7% 0050 — should
produce the **same or better** three-sleeve result. If it does, the
diversification benefit recorded in `SLEEVE3_GOLD_RESULT.md` was never
about trend-following in those markets; it was about holding partially
uncorrelated assets, which needs no signal at all.

That test is the next thing worth running, and it is free.

## What this does not overturn

- Every measured number in every result document stands. This changes
  interpretation, not measurement.
- It does **not** rescue the program's return story: trial 88 still
  returned 14.26× against 13.53× for holding thirteen coins
  (`VS_BUY_AND_HOLD_2026-07-26.md`), and the three-sleeve book still made
  less money than holding its constituents.
- It does **not** make trial 88 safe. Selection provenance
  (`SELECTION_PROVENANCE_CORRECTION_2026-07-26.md`) and PBO 0.7411 are
  untouched.

## Limits

- **The twin holds the benchmark**, which for the single-asset sleeves
  (0050, GLD) is exact, and for the crypto books is the equal-weight
  universe rather than the specific names the system chose. Approximate
  there.
- **Average exposure is a single number** applied across the whole window;
  a system whose exposure varies with opportunity is not fully described by
  its mean.
- **The twin is cost-free and would need continuous rebalancing.** Charging
  it realistic costs would raise every edge, most relevantly gold's 1.00×
  and Taiwan's 0.73×.
- One window, one crypto cycle, and the same uncontrolled survivorship as
  everywhere else in this program.

## Reproduce

```
python -m scripts.analyze_timing_value
```

---

## Addendum, same day — the substitution test ran, and it refuted the prediction above

The section above predicted that replacing the gold and Taiwan sleeves with
static partial holdings "should produce the **same or better** three-sleeve
result". Measured, via `scripts/analyze_sleeve_combination.py`:

| Book (common window, ⅓ each, monthly) | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| Three sleeves, all systems | **1.4108** | **14.90%** | **3.94×** |
| Crypto system + Taiwan held at 0.477 + gold held at 0.419 | 1.3870 | 16.74% | 3.74× |

**Worse on all three measures.** The prediction was wrong.

And the test was biased *against* the signal: the static twins pay **no
trading costs**, while the sleeves pay full costs. The signal won anyway.

### Why both results are true at once

A sleeve can be worthless standalone and still contribute to a book. The
Taiwan sleeve returns 0.73× of a passive holding at the same average
exposure — but a passive holding is exposed *all the time*, whereas the
trend sleeve is **flat at moments uncorrelated with crypto's drawdowns**.
That is precisely the mechanism `CROSSMARKET_COMBINATION_RESULT.md` named:

> the benefit comes from a sleeve being IN CASH while another falls

Static exposure cannot do that, by construction. So the signal's value
outside crypto is **not** in its own return — it is in *when* it holds
nothing.

### The honest size of it

Small. Sharpe +1.7%, drawdown −11%, terminal wealth +5% against the static
substitute. Real, measured, cost-conservative — and not large enough to
justify the machinery on its own if a simpler decorrelated flat-sleeve rule
existed.

## Addendum, same day — is the crypto edge one effect or two crashes?

The whole-window edge (4.70×) could be an artifact of sitting out one or
two crashes. Split across the **four sub-periods already declared** in
`analyze_sleeve_combination.print_stress` — reused verbatim so the split
cannot be chosen to flatter:

**Trial 88 (BTC/ETH), average exposure 0.379**

| Window | n | System | Twin | Edge |
|---|---:|---:|---:|---:|
| 2020 covid crash | 61 | 1.049 | 0.923 | **1.14** |
| 2022 bear year | 365 | 0.801 | 0.702 | **1.14** |
| 2018-2019 | 666 | 1.542 | 0.806 | **1.91** |
| 2023-2025H1 | 913 | 2.045 | 1.855 | **1.10** |

**Positive in all four.** Bull, bear, crash and mixed. The edge is not a
single-episode artifact, which is the strongest statement this program has
been able to make about any of its findings.

**Trial 94 (13 symbols), average exposure 0.301**

| Window | n | System | Twin | Edge |
|---|---:|---:|---:|---:|
| 2020 covid crash | 61 | 0.923 | 0.941 | 0.98 |
| 2022 bear year | 365 | 0.706 | 0.789 | **0.90** |
| 2018-2019 | 666 | 1.117 | 0.923 | 1.21 |
| 2023-2025H1 | 913 | 1.936 | 1.503 | 1.29 |

**Fails in both bear windows.** The 13-symbol book's whole-window edge of
2.77× is regime-dependent in a way the 2-symbol book's is not — it earns in
rising markets and loses to a static position in falling ones, which is the
opposite of what a trend system is supposed to do.

### The gap in this test, stated plainly

The four windows total **2,005 of 2,676 days — 74.9%**. They do not tile the
window: roughly **671 days from 2020-04 to 2021-12 are excluded**, and that
is the largest bull run in the sample. Much of the whole-window compounding
lives there and is untested by this split, so the sub-period edges do not
multiply to 4.70×.

Extending the split to cover every day would mean choosing new window
boundaries after seeing results, which is exactly the move this program
refuses. The honest statement is: **positive in all four windows that were
declared in advance, with a quarter of the sample untested.**

## Addendum, same day — the edge belongs to the family, not to the pick

The remaining doubt about the only positive finding was selection: trial 88
is the **maximum** of its 8-member experiment-7 family, and this program's
own PBO is 0.7411. But the exposure-matched twin had only ever been run on
the winner. Run on all eight:

| Trial | Exposure | System | Twin | **Edge** |
|---|---:|---:|---:|---:|
| 86 | 0.396 | 12.23× | 3.15× | 3.88 |
| 87 | 0.317 | 10.92× | 2.62× | 4.17 |
| **88 (the pick)** | 0.379 | 14.26× | 3.03× | **4.70** |
| 89 | 0.310 | 10.71× | 2.58× | 4.15 |
| 90 | 0.403 | 12.31× | 3.20× | 3.84 |
| 91 | 0.349 | 11.77× | 2.83× | 4.16 |
| 92 | 0.374 | 12.25× | 3.00× | 4.08 |
| 93 | 0.337 | 10.87× | 2.75× | 3.95 |

**Eight of eight. Range 3.84 to 4.70, median 4.115.** The family *floor*
beats its twin by 3.84×.

Trial 88's selection premium over a randomly-drawn family member is
**4.70 / 4.115 = +14.2%**. Selection chose the edge's **size**, not its
**existence** — a materially different claim from the one this program had
been braced for.

Spot-checking regime robustness on two non-winners with the same
pre-declared windows: trial 86 scores 1.09 / 1.08 / 1.89 / 1.06 and trial 93
scores 1.06 / 1.37 / 1.71 / 1.03. **Both positive in all four**, like the
winner. The regime robustness is not unique to the selected member either.

### Why this does not dispose of PBO

The eight are **not eight independent tests.** They are a 2×2×2 grid
(window set × exit rule × regime gate) on the *same two assets* over the
*same window*. "Eight of eight" means **no parameter choice inside that grid
destroys the edge** — not that the edge survived eight separate
opportunities to fail.

PBO 0.7411 was measured across *distinct architectures* on Sharpe rankings,
a different question that remains unanswered by this. What changed is
narrower: for **this** claim — exposure-adjusted return on BTC/ETH — the
family is homogeneously positive, so the specific worry that the winner was
a lucky draw is not supported.

### Method note

The first run of this test reported exit code 255 while printing correct
numbers. Rerun bare it exits 0 — the 255 came from PowerShell's
`Select-Object -First` closing the pipe early, not from the script. The
numbers were only used after that check. This project has twice been bitten
by pipes masking exit codes.

### Route closed

**"Replace the non-crypto sleeves with static holdings" is closed: it is
worse.** The sleeves stay as systems. This also refines the standing answer
— *standalone* timing value and *portfolio* timing value are different
quantities, and this program had been conflating them.

---

## Addendum 2026-07-28 (iteration 29) — the twin metric was audited and survives; route closed

This metric was built on 2026-07-27 and became the program's headline
number within one iteration ("4.70x its exposure-matched passive twin").
A metric that replaces a discredited one deserves the same scrutiny that
discredited the old one. Two attacks were tried. **Both fail, and the
number is more robust than expected.**

### Attack 1 — does the twin eat volatility drag the system avoids?

`analyze_timing_value.py:139` builds the twin as `w * benchmark_return`
per period, compounded. That is a continuously-rebalanced constant-mix
position, and constant-mix carries a drag term the system does not.

**Refuted.** Scaling *arithmetic* returns by w < 1 gains convexity
relative to full exposure: `log(1 + w*r) > w * log(1 + r)` for both signs
of r, so partial exposure genuinely suffers less drag than the asset it
tracks. The twin is therefore a **harder** benchmark than "w times the
asset's log growth", not an easier one.

Quantified against the obvious alternative construction — buy `w` of the
asset once and never rebalance, rest in cash:

| Twin construction | Twin multiple | Measured edge |
|---|---:|---:|
| constant-mix, daily rebalanced (**as used**) | 3.03x | **4.71** |
| un-rebalanced fraction, cash remainder | 2.9121x | 4.90 |

The two constructions differ by **4.1%**, and the one actually used is
the **more conservative** of the pair. This is consistent with the
standard result that buy-and-hold beats constant-mix in trending markets
and loses in oscillating ones; this window trended (benchmark 6.0510x).
**The headline edge is not an artefact of the rebalancing convention.**

### Attack 2 — is the "timing" edge really asset selection between BTC and ETH?

The twin matches **time-in-market** but not **asset mix**. Over this
window BTC returned 9.86x against the equal-weight benchmark's 6.05x, so
a rule that simply favoured BTC would show up as "timing value" without
timing anything.

**Refuted, decisively.** Mean per-symbol target weight across all 2,677
decision days, read from `trial-000088/report.json` `targets[].target_weights`:

| Symbol | Mean weight | Days with weight > 0 | Share of exposure |
|---|---:|---:|---:|
| BTCUSDT | 0.2006 | 1776 / 2677 | 53.0% |
| ETHUSDT | 0.1780 | 1627 / 2677 | 47.0% |
| **total** | **0.3785** | | |

The total reproduces the recorded mean exposure of 0.379 exactly. The
split is **53/47 against an equal-weight benchmark's 50/50 — a three
percentage point tilt.** A 3pp tilt toward the better asset cannot
produce a 4.70x edge. The rule is not picking BTC over ETH; it is going
in and out.

### What this closes

**The exposure-matched twin survives audit on both the construction it
uses and the composition it ignores.** The 4.70x is a property of the
timing decisions, is conservative by 4% against the alternative twin, and
is not contaminated by asset selection. Do not re-open either question
without new evidence.

**Limits that remain, unchanged and still recorded:** the twin pays no
trading costs while the system pays full costs (conservative for the
system); the twin has no drawdown control (43.60% against the system's
33.05%); and none of this is forward evidence — the earliest date a
forward return verdict is statistically permitted is 2028-06-29
(`FORWARD_TRACK_READ_PREREGISTRATION.md`).
