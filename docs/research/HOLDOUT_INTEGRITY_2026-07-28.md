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

---

## Addendum 2026-07-28 (iteration 33) — one claim above corrected, and the channel closed

### Correction: only one of the two diagnostics was actually unsafe

The table above lists `analyze_symbol_dispersion.py:30` and
`analyze_whipsaw.py:129` together as reading the full series. **That
overstates it for the first script.**
`analyze_symbol_dispersion.py` carries its own date bound:

```python
_START = date(2018, 3, 6)
_END = date(2025, 7, 1)
...
parser.add_argument("--end", default=_END.isoformat())
```

Its default `--end` is **2025-07-01**, exactly the holdout boundary. It
reads from `data/candles` but truncates before `holdout_start`, so it was
**safe by default all along**. Only `analyze_whipsaw` was genuinely
unbounded — it has no date argument at all, so its `--candles-dir`
default was the whole exposure.

### The channel is now closed

`scripts/analyze_whipsaw.py` now defaults to `data/candles_preholdout`,
with the reason stated at the argument. `first_month` / `last_month` were
already in its JSON output, so any future run that widens the window with
an explicit `--candles-dir` still records what it saw.

Locked in by `tests/scripts/test_analyze_whipsaw.py::
test_default_candles_dir_is_the_preholdout_slice`, so the default cannot
regress silently. Full suite: **379 passed**; ruff, ruff format, mypy
--strict and lint-imports all exit 0.

This closes operator decision 3 from the section above. Decisions 1 (carry
the caveat into the October result) and 2 (make the lock mechanical in the
engine) remain open and remain the operator's.

**What is not undone:** the whipsaw verdict that set hysteresis first in
Goal P was formed on a window crossing the boundary. Fixing the default
prevents recurrence; it does not retract the history. That caveat still
travels to October.

### Note on the mechanical-lock recommendation

A literature search for programmatic holdout-enforcement patterns
returned little of substance — mostly LLM guardrail tooling, not ML data
governance. The one relevant confirmation is the benchmarks literature's
observation that in theory a test set is used once and in practice that
is "only sometimes the case". That is an argument for decision 2 rather
than against it, but no established pattern was found to copy, so the
engine-level guard would be designed from scratch.

---

## Addendum 2026-07-28 (iteration 34) — the central claim of this document was wrong

### The lock IS mechanical. "Convention, not mechanism" is retracted.

The section "The hazard: the lock is convention, not mechanism" argued the
guarantee "rests on ten defaults staying correct, not on the engine
refusing to read past `holdout_start`." **That is false, and it is
retracted here.**

`src/backtest/runner.py` is the single registered entry point every
family runner goes through, and it trims unconditionally:

```python
if spend_holdout_single_use:
    holdout = spend_holdout(holdout_path, spent_at=recorded_at)
    run_candles = dict(candles_by_symbol)
else:
    run_candles = {
        symbol_value: tuple(
            candle for candle in candles if candle.close_time < holdout.holdout_start
        )
        ...
    }
```

Its module docstring says so on line 1 — "holdout enforcement + trial
registry + report" — and the function docstring states "inputs are
trimmed to end before the holdout starts."

**Passing `--candles-dir data/candles` to a family runner would NOT leak
the holdout.** The runner discards every candle at or after
`holdout_start` before the engine sees it. The reason all 133 trials
carry `data_end` = 2025-07-01 is **this trim**, not ten argparse defaults
happening to be right.

This is the pattern the leakage literature recommends — enforcement "at
the framework level ... at the architectural level rather than relying on
manual implementation." The codebase already implements it.

**Operator decision 2 above ("make the lock mechanical") is therefore
VOID.** There is nothing to build; it exists.

### The spend path is covered, and spending before the run is deliberate

`spend_holdout`'s docstring states the design outright: "The spend is
recorded BEFORE the qualification run executes: if the run crashes, the
holdout stays spent (conservative by doctrine)." A suspected
irreversible-loss bug is an explicit, documented choice.

Six tests in `tests/backtest/test_validation_gate.py` cover the October
procedure:

| Test | Covers |
|---|---|
| `test_holdout_lock_is_single_use` | double-spend rejected, post-spend reads rejected |
| `test_registered_run_locks_holdout_trims_data_and_registers_trials` | **the trim itself** |
| `test_holdout_spend_run_is_single_use_and_marked_in_registry` | spend marked in the registry |
| `test_future_dated_candles_cannot_anchor_the_holdout` | a future candle cannot push `holdout_start` years out |
| `test_holdout_spend_registers_isolated_holdout_segment_metrics` | holdout-segment metrics are isolated |
| `test_holdout_segment_includes_the_boundary_day_move` | the boundary-day return is not dropped |

### What survives from this document

**Iteration 33's fix still stands and was the real hole.** Diagnostics
like `analyze_whipsaw` read candle files **directly** and never call
`run_registered_backtest`, so the trim never protected them. That was the
only genuine leak channel, and it is now closed at the source.

Corrected picture: **trials were mechanically safe all along; diagnostics
were not.** The soft-contamination history (the whipsaw verdict that set
hysteresis first in Goal P) is unaffected by this correction and still
travels to October.

### Note on how this document went wrong

Iteration 32 inferred a mechanism claim from **ten argparse defaults
without reading the runner they feed into.** That is asserting rather
than measuring — the exact failure this program has caught repeatedly in
its own record (the retracted 0.9+ correlation claim, the retracted
sleeve-count synthesis, the pooled-universe headline). Three of that
iteration's statements have now needed correction: the dispersion script
was already bounded, the lock was already mechanical, and operator
decision 2 was never needed.
