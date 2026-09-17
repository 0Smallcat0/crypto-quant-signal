# Forward-track Test 2 — what can a drawdown breach actually detect?

Date: 2026-09-17 (iteration 62) · Backtest series only · Zero registry
cost (no trial registered, no backtest run, no gate report regenerated) ·
**No forward metric computed and none cited.** Every number below comes
from `docs/reports/research/trial_returns/` and `data/candles/`, both
backtest artifacts.

## Why this document exists

`FORWARD_TRACK_READ_PREREGISTRATION.md` fixes three tests. Two of them
have now been audited and the rule's own text audits the third:

| Test | What it can settle on 2026-10-22 | Established by |
|---|---|---|
| 1 — implementation agreement | harness check; cannot see cost, cannot see a signal-math error, cannot be run against an archived input | iterations 59, 61 |
| 2 — drawdown breach | **never measured** | — |
| 3 — return | nothing: the rule itself computes SE 2.016 and a 95% interval of [-2.77, +5.13] | the rule, 2026-07-28 |

The rule characterised Test 3's power in detail and **never characterised
Test 2's.** What it says instead is:

> If forward drawdown **exceeds the backtest maximum** at any read date,
> that is recorded as evidence **against** the strategy generalizing, and
> it counts at any N — a tail breach does not need MinTRL, because the
> claim being refuted is about the tail, not the mean.

"Counts at any N" is a statement about **admissibility**. It has been
sitting next to a paragraph that carefully quantifies Test 3's
**power**, and nothing anywhere states Test 2's. This document measures
it. The answer is one **PASS** and one **defect of framing**, and it
closes the last unmeasured part of the October read.

---

## 0. The bar, verified at source before anything was computed

| Trial | Registry `max_drawdown_fraction` | Reproduced from the return series | Registry `final_equity` | Reproduced |
|---|---|---|---|---|
| 88 | 0.3304782446654657897565823246 | **33.0478%** | 14231.46886767244 | **14.2315x** |
| 118 | 0.3324023474578522547374688075 | **33.2402%** | 16898.57716383774 | **16.8986x** |

Both series are n = **2676** daily returns, 2018-03-05..2025-07-01 —
the same files and the same n the read rule used for its MinTRL
arithmetic. The reproduction is exact to the printed precision, so the
series below is the series the bar was computed from.

---

## 1. PASS: Test 2's in-sample false-positive rate is exactly zero — and
## it is zero **by construction**, which is not the same as being safe

The bar is the **maximum of the same series** the forward track is a
continuation of. For any window `[i, i+L)` the running peak resets at the
window's first bar, while the full-sample running peak at the same instant
also includes everything before `i` and is therefore never smaller. So
every within-window drawdown is bounded above by the full-sample drawdown
at the same instant, hence

    max over windows of (within-window MDD)  <=  full-sample MDD

**for every L, with no exception and no statistics.** Measured, to check
the argument against the data rather than assert it:

| Trial | L | worst window MDD | bar | excess | naive count `> bar` | count `> bar + 1e-12` |
|---|---:|---:|---:|---:|---:|---:|
| 88 | 90 | 26.2856% | 33.0478% | -6.762 pp | 0 | **0** |
| 88 | 365 | 30.9439% | 33.0478% | -2.104 pp | 0 | **0** |
| 88 | 706 | 33.0478% | 33.0478% | +7.216e-14 pp | 78 | **0** |
| 88 | 1000 | 33.0478% | 33.0478% | +8.327e-14 pp | 141 | **0** |
| 88 | 1338 | 33.0478% | 33.0478% | +8.327e-14 pp | 194 | **0** |
| 118 | 90 | 23.4776% | 33.2402% | -9.763 pp | 0 | **0** |
| 118 | 706 | 33.2402% | 33.2402% | +1.221e-13 pp | 91 | **0** |
| 118 | 1338 | 33.2402% | 33.2402% | +1.221e-13 pp | 280 | **0** |

The long-window "breaches" are **floating-point artifacts** of order
1e-13 pp — windows that contain the full drawdown episode and reproduce
it to within one ulp. A first pass of this analysis used a naive `> bar`
comparison and reported "P(breach) 3.96% at L=706, first reachable at
L=423"; **those numbers are wrong and appear nowhere else in this
document.** They were caught because two independent implementations
(direct equity multiplication and log-cumsum) disagreed on them while
agreeing on everything else, which is the only reason the check was run.

**This is a genuine PASS.** A refutation test that cannot fire on
in-sample-consistent behaviour has a zero false-positive rate, and if it
ever does fire the signal is unambiguous. But zero here is a property of
comparing a series against its own maximum, not evidence that the bar was
well chosen — which is what section 2 is about.

---

## 2. DEFECT of framing: at 90 days the bar is 1.26x deeper than the
## worst thing the strategy has ever done

Maxima grow with the window. The bar is a maximum over **2676** days; on
2026-10-22 it will be applied to a maximum over **90**. The distribution
of within-window drawdown at each of the rule's four read dates, over the
strategy's own history:

### Trial 88 — bar 33.0478%

| Read date | L | windows | median | p95 | worst ever | bar − worst | bar / worst |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-10-22 | 90 | 2587 | 11.0101% | 21.9404% | **26.2856%** | **6.7622 pp** | **1.2573x** |
| 2027-01-24 | 184 | 2493 | 18.0216% | 26.2856% | 26.2856% | 6.7622 pp | 1.2573x |
| 2027-07-24 | 365 | 2312 | 22.1275% | 28.6741% | 30.9439% | 2.1039 pp | 1.0680x |
| 2028-06-29 | 706 | 1971 | 25.7087% | 33.0478% | 33.0478% | 0.0000 pp | 1.0000x |

### Trial 118 — bar 33.2402%

| Read date | L | windows | median | p95 | worst ever | bar − worst | bar / worst |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-10-22 | 90 | 2587 | 11.6201% | 21.1636% | **23.4776%** | **9.7627 pp** | **1.4158x** |
| 2027-01-24 | 184 | 2493 | 18.4368% | 23.6845% | 27.0914% | 6.1489 pp | 1.2270x |
| 2027-07-24 | 365 | 2312 | 23.0563% | 27.6674% | 30.3857% | 2.8545 pp | 1.0939x |
| 2028-06-29 | 706 | 1971 | 26.0888% | 33.2402% | 33.2402% | 0.0000 pp | 1.0000x |

Read the 2026-10-22 row plainly: **for Test 2 to fire in October, the
forward 90 days must be 26% worse than the worst 90 days of 2018-2025
(trial 88), or 42% worse (trial 118).** The worst 90 days of 2018-2025
includes the March 2020 collapse and the 2022 bear. The horizon at which
the bar stops being an over-reach is **706 days** — the MinTRL date,
arrived at independently, which is a coincidence worth noticing rather
than a design.

Externally corroborated for direction only: a practitioner treatment of
max drawdown resamples paths at the **original length** explicitly
"since max drawdown grows mechanically with the window" (Quantreo,
logged in `RESEARCH_LOG.md` under iteration 62). The magnitudes above are
this program's own; nothing quantitative is borrowed.

---

## 3. How much degradation Test 2 actually needs at 90 days

Two crude alternative models, deliberately opposite in shape, applied to
every one of the 2587 90-day windows. Model A scales severity in log
space, `log(1+r') = k*log(1+r)` — a well-defined transform that can never
drive equity negative, unlike a linear scaling of `r` which produces
returns below -100% and silently poisons the comparison with NaN. Model B
subtracts a constant daily bleed, `r' = r − δ`.

| Trial | Firing probability at L=90 | Model A: severity multiple k | Model B: extra bleed δ |
|---|---|---:|---:|
| 88 | any window at all (P>0) | 1.3155x | 0.1314 pp/day (**-38.12%/yr**) |
| 88 | P >= 5% | 1.6197x | 0.2575 pp/day (**-60.98%/yr**) |
| 88 | P >= 50% | 3.4393x | 0.4136 pp/day (**-77.97%/yr**) |
| 118 | any window at all (P>0) | 1.5101x | 0.1802 pp/day (**-48.22%/yr**) |
| 118 | P >= 5% | 1.6992x | 0.2596 pp/day (**-61.27%/yr**) |
| 118 | P >= 50% | 3.2711x | 0.4173 pp/day (**-78.27%/yr**) |

Analytic cross-check, independent of both models and of the data: the
gentlest **uniform** path that breaches is a loss of
`1 − (1−0.330478)^(1/90)` = **0.4448%/day, every day, for 90 consecutive
days** — an annualized **-80.35%** (trial 118: 0.4480%/day, **-80.58%**).
It lands on Model B's 50% row, as it should.

The two models disagree on shape and agree on magnitude: **Test 2 at 90
days is a detector for the strategy bleeding somewhere around -60% to
-80% per year.** That is not edge decay. A strategy whose edge had
vanished entirely and now simply held BTC/ETH through a bad quarter would
**not** trip it.

---

## 4. What Test 2 is therefore testing

The bar is not unreachable in principle. Over the identical window, a
50/50 daily-rebalanced BTC/ETH benchmark's worst drawdown inside a
**90-day** window is **65.9505%** — twice the bar — rising to 73.7503% at
184 days and 82.9121% at 365. (Provenance check on the series: a
no-rebalance 50/50 hold over the same dates reconstructs to 6.0283x at
81.0519% against the 6.05x / 80.99% recorded in
`VS_BUY_AND_HOLD_2026-07-26.md` — a sub-1% difference from the window's
first day, close enough to confirm the series is the right one and not
close enough to restate a recorded number.)

So the market crosses the bar routinely in 90 days and the strategy never
did. The difference is the exit rule. **Test 2 fires only if the exit
mechanism stops working** — it is a second mechanism check, not an edge
check, and it sits beside Test 1 rather than beside Test 3.

Combined with what was already established, the 2026-10-22 read is now
fully characterised:

| Test | Verdict it can return in October | Kind |
|---|---|---|
| 1 | exposure path reproduces, or halt | mechanism |
| 2 | exit rule did not catastrophically fail | mechanism |
| 3 | forbidden from confirming; refutation half is swamped by SE 2.016 | none |

**Not one of the three can say anything about whether the edge works.**
This was already true of Tests 1 and 3 and is now measured for Test 2.
**Route closed: no proposal may claim the October read produces evidence
about the edge, in any form.**

Interaction with the cost omission (iteration 59), stated for
completeness: the forward series charges no fee or slippage, so its
drawdown is understated and Test 2 is pushed **further** from firing —
the same one-signed direction. Iteration 59 measured that effect as
immaterial at the current level and it stays immaterial here, since the
gap being discussed is 6.76 pp.

---

## 5. Options, none of them taken

Nothing frozen was edited and nothing is proposed as a rule change.

**Option A — accept and re-scope.** Record that Test 2 at 90 days is a
mechanism-failure check and read a non-breach as what the rule already
declares it to be: uninformative. Costs nothing, changes no frozen text,
and is what this document accomplishes by existing. It leaves the rule's
"counts at any N" wording in place, where it will keep inviting a
non-breach to be read as reassurance.

**Option B — declare a length-matched bar, in a new document, before the
read.** The measured p95 of the 90-day distribution is **21.9404%**
(trial 88) and **21.1636%** (trial 118); a bar there has a 5% in-sample
false-positive rate instead of 0%. Honest cost, stated plainly: this is a
new metric chosen **after 54 forward rows exist**, which is weaker than a
pre-data choice even though it is 35 days before the read and even though
the frozen rule's prohibition is specifically on introducing metrics *at
read time*. Mitigating and verifiable: the forward drawdown recorded so
far (iteration 59, 3.4094%) is far below every candidate bar, so the
choice cannot currently be fitted to the data. The frozen rule would not
be edited — Test 2 stays exactly as written and the new bar is a second,
separately registered test that must report its own result whether it
fires or not.

**Option C — do nothing.** The October read reports "Test 2: no breach".
The cost is the one iteration 27 named: a defect that is recorded but not
acted on propagates as a qualifier-free sentence. "The forward track did
not breach its drawdown bar" is true, uninformative, and reads as
reassurance.

**The operator must choose, and before 2026-10-22 (35 days).** This is
the fourth choice now due before that date, alongside the cost omission
(iteration 59), the archive-vs-reconstruct choice and the replay-depth
specification (iteration 61).

---

## Method note — exactly reproducible, no new script

No script was added; the contract's one-script-per-iteration budget is
unspent. Run from the repo root.

```python
import json
import numpy as np

def load(tid):
    d = json.load(open(f'docs/reports/research/trial_returns/trial-{tid:06d}.json'))
    return np.array([float(x) for x in d['daily_returns']], dtype=float)

def wmdd(r, L):
    """Max drawdown inside every length-L window, peak reset at the window's
    first bar — the analogue of a forward track that starts fresh at 1000."""
    out = np.empty(len(r) - L + 1)
    for i in range(len(r) - L + 1):
        eq = peak = 1.0
        m = 0.0
        for x in r[i:i + L]:
            eq *= (1.0 + x)
            if eq > peak:
                peak = eq
            d = 1.0 - eq / peak
            if d > m:
                m = d
        out[i] = m
    return out

BARS = {88: 0.3304782446654657897565823246,   # registry max_drawdown_fraction
        118: 0.3324023474578522547374688075}

for tid, bar in BARS.items():
    r = load(tid)
    for L in (90, 184, 365, 706):               # the rule's four read dates
        v = wmdd(r, L)
        print(tid, L, len(v),
              np.percentile(v, 50), np.percentile(v, 95), v.max(),
              int((v > bar + 1e-12).sum()))     # the 1e-12 is load-bearing
```

Section 3's two degradation models replace `r` with `np.expm1(k *
np.log1p(r))` (Model A) and `r - delta` (Model B), bisecting on `k` and
`delta` to the stated firing probabilities; 44 bisection steps, bracket
`k` in [1, 12] and `delta` in [0, 0.05]. Section 4's benchmark is
`0.5 * BTC daily return + 0.5 * ETH daily return` from
`data/candles/{BTCUSDT,ETHUSDT}_1d.jsonl`, restricted to the trial
series' own `first_return_date`..`last_return_date`, 2675 returns.

Nothing here spends the holdout, touches `configs/runtime/`, reads a
shadow file, registers a trial, edits a frozen document, or moves a read
date.
