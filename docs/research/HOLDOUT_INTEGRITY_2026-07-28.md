# Holdout integrity — verified clean at the trial level, with one live hazard

Date: 2026-07-28 (iteration 32) · Registry N=133 · Zero registry cost
(inspection only; no backtest, no trial registered, holdout not read).

## Why this exists

The October holdout is the one piece of clean evidence this program has
deliberately reserved. Everything else is in-sample, and forward
validation cannot return a return-based verdict before **2028-06-29**
(`FORWARD_TRACK_READ_PREREGISTRATION.md`). If the holdout were already
contaminated it would be worthless **before** being spent, and nobody had
ever checked. This checks it.

## Verification: clean at the trial level

| Source | rows | first | last |
|---|---:|---|---|
| `data/candles/BTCUSDT_1d.jsonl` (full) | 3242 | 2017-08-17 | **2026-07-02** |
| `data/candles_preholdout/BTCUSDT_1d.jsonl` | 2876 | 2017-08-17 | **2025-07-01** |

`docs/reports/research/holdout_lock.json`:

```json
{"holdout_start": "2025-07-02T23:59:59.999000+00:00",
 "locked_at": "2026-07-03T02:44:47.633808+00:00",
 "spent": false, "spent_at": null}
```

The truncated series ends exactly one day before `holdout_start`. The
decisive test is not what the scripts intend but what the registry
records:

**All 133 registered trials have `data_end` = 2025-07-01. Zero cross the
boundary.**

Roughly **366 days** of holdout (2025-07-02 .. 2026-07-02) exist to be
spent, matching gate 5's "~12 months", and `spent` is still `false`.
**Gate 5 is intact as written: no trial has read the holdout.**

## The hazard: the lock is convention, not mechanism

Every path that can register a trial defaults to the safe directory:

| Default `--candles-dir` | Scripts |
|---|---|
| `data/candles_preholdout` (safe) | `run_alloc_family`, `run_atr_family`, `run_combo_family`, `run_cs_family`, `run_donchian13_family`, `run_donchian_family`, `run_gate_family`, `run_robustness_trial88`, `run_robustness_trial118`, `run_trendfactor_family` — **all ten** |
| `data/candles` (**full, includes holdout**) | `analyze_symbol_dispersion.py:30`, `analyze_whipsaw.py:129` |

The design is coherent — the lock protects **trials** — but nothing
*prevents* `--candles-dir data/candles` being passed to a family runner.
The guarantee rests on ten defaults staying correct, not on the engine
refusing to read past `holdout_start`.

## Soft contamination, recorded before the holdout is spent

`analyze_whipsaw` defaults to the full series, and
`WHIPSAW_DIAGNOSTIC.md:84` documents its run over candles spanning
**2024-01 to 2026-06** — a window that crosses `holdout_start`. That
diagnostic's verdict placed the hysteresis experiment first in Goal P.

**This is not a gate-5 violation.** Gate 5 says the holdout is "never
read by any trial", and no trial read it — verified above. But the
adaptive-data-analysis literature is explicit that the relevant
dependency is not only through fitted models: *the moment a researcher
considers a result computed on the reserved data, the subsequent work
acquires a formal dependency on it that classical validity theory does
not cover.* Repeated or indirect use creates a feedback loop between
analyst and data.

**Magnitude, stated honestly and not minimised away:** the whipsaw
statistic is **signal churn frequency**, not strategy P&L. It cannot
reveal whether trial 88 or 118 made money after 2025-07-01, so it cannot
have tuned the strategies toward the holdout's returns. What it could
have done is nudge **research priority** — which it did. That is a weak
channel, but it is a real one, and it must be on the record **before**
October rather than discovered afterwards, when it would look like an
excuse.

## What the operator should decide

1. **Whether the October result carries this caveat.** The recommendation
   is yes, stated in the result document itself: one diagnostic read a
   window crossing the boundary and its verdict set priority.
2. **Whether to make the lock mechanical.** The cheap version is for the
   backtest engine to refuse candles with `open_time >= holdout_start`
   unless an explicit `--spend-holdout` flag is present, so the guarantee
   stops depending on ten argparse defaults. This is a code change to a
   path the loop must not alter unilaterally.
3. **Whether to repoint the two diagnostics** at
   `data/candles_preholdout` by default. Zero cost, removes the channel
   entirely for future work.

## What does not change

- No gate rule modified; `PRE_HOLDOUT_PROTOCOL.md` is frozen and was not
  edited.
- The holdout was **not read** by this iteration — only `holdout_lock.json`
  metadata, row counts, and date boundaries were inspected.
- Nominations stay fixed; `spent` stays `false`.
- No trial registered, no backtest run, no `configs/runtime/` touched.
