# Robustness battery on trial 118 — pre-registration (NOT a search)

Status: **FROZEN on commit**. Written 2026-07-25 before any run, and
required by `docs/research/GOALP_EXPERIMENT10_RESULT.md`'s honesty clause
before trial 118 may be nominated for anything.

Subject: trial 118 — Donchian 10/20/55/110 entries, ATR channel exit
(window 14, multiple 2), no gate, equal weighting, BTC/ETH. Sharpe
1.2411, DSR 0.950514 at N=125, MDD 33.24%.

## Binding rule (identical to the trial-88 battery)

**No configuration run under this document may ever be nominated,
adopted, or reported as an improvement, however it scores.** These arms
exist to measure dispersion and to break the candidate, not to find a
better one. This is what lets battery A include an ATR multiple TIGHTER
than trial 118's: experiment 10's winner sat at a grid endpoint, and the
honest way to probe past an endpoint is with arms that cannot be adopted.

Cost-stress rows carry `cost_multiplier != 1` and are candidate-excluded
by PRE_HOLDOUT_PROTOCOL §1.

**Accepted cost, stated in advance**: these 8 rows take N from 125 to
133, which raises the deflation bar and will very likely put trial 118's
DSR below 0.95 in the next report. Experiment 10's verdict was rendered
at the report its pre-registration named (N=125) and is not retroactively
voided; but no future document may quote a post-battery DSR as if it
refuted that verdict, nor quote the N=125 pass without this note.
Knowing whether the candidate is fragile is worth more than protecting a
0.0005 margin that is inside the estimate's own noise.

## Battery A — parameter neighbourhood (6 runs)

| Arm | Change from trial 118 |
|---|---|
| A1 | ATR window 10 (−4) |
| A2 | ATR window 20 (+6) |
| A3 | ATR multiple 1.5 (tighter than the endpoint) |
| A4 | ATR multiple 2.5 |
| A5 | channel windows 8+16+44+88 (−20%) |
| A6 | channel windows 12+24+66+132 (+20%) |

**Pre-declared stability verdict (all must hold):**

1. All six arms annualized Sharpe ≥ 1.00.
2. All six arms MDD ≤ 51.93%.
3. Neighbourhood Sharpe spread (max − min) ≤ 0.35.

Any breach → trial 118 is recorded as parameter-fragile, and no future
pre-registration may nominate it without stating the fragility.

## Battery B — cost stress (2 runs)

Trial 118's exact configuration at `cost_multiplier` 2 and 3.

1. At 2× costs: Sharpe ≥ 1.00 and total return positive.
2. At 3× costs: Sharpe ≥ 0.80 and total return positive.

## Read-outs (non-gating, declared now)

- Whether trial 118 is the neighbourhood maximum (weaker evidence) or
  sits mid-pack (healthier), by the same standard applied to trial 88.
- What A3 says about the endpoint: if a tighter multiple scores higher,
  experiment 10's grid genuinely failed to bracket the mechanism, and
  that limitation is recorded permanently — it does not become a new
  candidate.

## Honesty clauses

- Nothing here touches the October holdout, its fixed nominations, or the
  live contract.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it.
