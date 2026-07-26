# Cash-aware allocation — result: REGISTERED NEGATIVE

Executed 2026-07-26 · Pre-registration:
`docs/research/CASH_AWARE_ALLOCATION_PREREGISTRATION.md` (unmodified,
frozen at commit `111dedd`) · No backtest, no registry row.

## Result

Window 2018-03-06 → 2025-07-01, 2,675 days. At least one sleeve was long on
2,522 of them (94.3%).

| Book | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| 1/3 each, monthly (published) | **1.4108** | **14.90%** | 3.94× |
| Equal among active sleeves | 1.3027 | 23.49% | **4.39×** |

Mean book gross exposure rose from 0.3380 to **0.5557**, and never exceeded
1.0 on any day, so the rule stayed inside product law as designed.

Pre-declared criteria:

1. **Terminal multiple > 3.94×** — PASS (4.39×).
2. **Max drawdown < 19.73%** — **FAIL** (23.49%).
3. **Sharpe ≥ 1.3437** — **FAIL** (1.3027).

**VERDICT: REGISTERED NEGATIVE.**

## What it means, in the words the pre-registration used before seeing it

> If concentration raises the drawdown materially, that is the finding: the
> idle cash was buying something real.

It did, and it was. Deploying the idle two-thirds bought **+11% terminal
wealth for +58% drawdown** (14.90% → 23.49%) and a *lower* Sharpe. The book
also ends up worse than the two-sleeve book it was meant to improve, on both
risk measures, while barely beating the three-sleeve book on return.

The mechanism is legible: the rule concentrates hardest exactly when fewest
markets are trending, which is when a trend book is least likely to be
right. Equal weights are not leaving money on the table by accident — the
idle cash is what makes the drawdown small, and those are the same fact.

**And this is an upper bound.** Reallocation trading costs are not modeled
and daily reallocation is assumed; both favour the losing design. A costed
version can only be worse than these numbers.

## What survives

The published three-sleeve equal-weight book stands unchanged: Sharpe
1.4108, max drawdown 14.90%, 3.94×. Nothing here revises it.

What is now measured rather than assumed: the terminal-wealth cost of the
combination is **not** recoverable by reallocating idle capital under a
no-leverage constraint. Within product law (spot, long-only, unlevered), the
smoother path and the smaller multiple are the same fact. The remaining ways
to change that trade are outside product law (leverage) or outside this
design entirely (sleeves that are long more often, or that earn a yield
while flat).

That is worth knowing precisely because it closes a route rather than
opening one — with a mechanism attached rather than a shrug.

## Limits

- One window, one crypto cycle, three sleeves.
- No DSR, no gate verdict, no registry row; portfolio-level analysis of
  already-registered trials.
- FX still not modeled across three currencies.
- Never nominatable for the October holdout.

## Reproduce

```
python -m scripts.analyze_idle_capital
python -m scripts.run_cash_aware_allocation
```
