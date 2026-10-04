# Can the 2026-10-22 read actually be run? — iteration 74, 2026-10-04

Date: 2026-10-04 (iteration 74) · **No forward statistic computed and none
cited** · Zero registry cost (no trial registered, no backtest run, no gate
report regenerated, nothing frozen edited) · No new script — every number
below comes from a file listing, a `grep`, a registry row, or the recorded
JSON's own representation.

## Why this document exists

Five iterations have now audited the 2026-10-22 read, and all five asked the
same kind of question: *what can each test decide?*

| Test | What it can settle on 2026-10-22 | Established by |
|---|---|---|
| 1 — implementation agreement | harness check; blind to cost, blind to signal-math error, no archived input, needs >= 206 bars of replay depth | iterations 59, 61 |
| 2 — drawdown breach | detects the exit mechanism failing, not a dead edge; bar is 1.26x / 1.42x the worst 90 days on record | iteration 62 |
| 3 — return | nothing; 95% interval [-2.77, +5.13] at 90 days, MinTRL 2028-06-29 | iteration 25 |

Iteration 62 concluded that **"all three tests of the 2026-10-22 read are
now characterised."** That sentence is true of what the tests *detect* and it
is not the same claim as the read being *runnable*, and nobody had asked the
second question. Characterising a test's power presumes an executor who
performs it as written. This document asks who that is, what they run, and
what they must decide that the rule does not say.

The rule's own closing clause makes the question load-bearing rather than
pedantic:

> No metric, sub-period, symbol subset, or alternative benchmark may be
> introduced at read time.

Every gap below is a thing an executor must settle on the day. Under that
clause, settling it on the day is the one thing forbidden.

## 0. The rule does not name its own inputs

`FORWARD_TRACK_READ_PREREGISTRATION.md` is 154 lines. The only file paths it
names anywhere are the two **backtest** return series it used to compute
MinTRL — `trial_returns/trial-000088.json` and `trial-000118.json`, at its
lines 28-29 and 149-150. It names **no forward track file**, and it describes
its subject set once, at line 9:

> Since 2026-07-24 **three** forward shadow tracks have been recording.

**Four track files exist.** Measured today:

| File | Repo | Rows | Range | `source_trial` |
|---|---|---:|---|---:|
| `data/runtime/shadow_trial88.jsonl` | this | 71 | 2026-07-24..2026-10-03 | 88 |
| `data/runtime/shadow_trial118.jsonl` | this | 71 | 2026-07-24..2026-10-03 | 118 |
| `data/runtime/shadow_tw0050.jsonl` | `D:/TW-Stock-Trading` | 11 | 2026-07-24..2026-10-02 | 23 |
| `data/runtime/shadow_gld.jsonl` | `D:/TW-Stock-Trading` | 12 | 2026-07-23..2026-10-02 | 24 |

The contract's P1 names the three tracks by *job* — crypto daily, Taiwan
weekly, gold weekly — which is three. The rule's Test 2 names bars for
trials **88 and 118**, which is the crypto pair. The two enumerations do not
pick out the same set, and the rule never resolves it, so the read's subject
set is the first undeclared choice.

## 1. DEFECT, and it is the whole finding: there is no executor

Eighteen days before the read, **no code in either repository reads a shadow
track for comparison, and no document names who runs the read.**

Searched this repository for every reference to a shadow track path across
`*.py`, `*.ps1`, `*.cmd`, `*.toml` and `*.cfg`, excluding `docs/` and
`.venv/`. Two hits, both in the **writer**:

- `scripts/shadow_signal.py:58` and `:67` — the track table's own `path`
  entries.

That script's single read of the file is `load_track` (`:95-102`), and all
three consumers are bookkeeping, not comparison: `:187-188` is the idempotency
check that prints `already recorded through`, `:192` reads
`rows[-1]["equity"]` to carry equity forward, and `summarize` prints the same
field at `:141` for the `--summary` display. Nothing in it recomputes a
recorded exposure or compares two paths. The sibling repository has the
mirror of this and nothing else — `scripts/shadow_signal_tw.py:66,75`.

Test coverage of the recorder is **zero**. `tests/` contains no file
mentioning `shadow`, `forward_track` or `track`; `tests/scripts/` holds four
files — `test_analyze_whipsaw.py`, `test_log_fill.py`, `test_run_demo.py`,
`test_run_gate_report.py` — and none of them touches `shadow_signal.py`. The
suite that reports **383 passed** does not execute a single line of the
program's only unbiased evidence producer.

No scheduler hook exists either: no `*.ps1` or `*.cmd` under `scripts/`
mentions `10-22`, `October`, `read rule` or `forward read`. And the rule
assigns no owner — searched for `operator-run`, `who runs`, `executor`,
`responsible` and `owner` across its 154 lines: **zero hits**.

**Consequence.** The reader gets written on or after 2026-10-22, by whoever
opens the files, with the data visible on screen. That is precisely the
failure the rule's own line 15 names — *"whoever opens the file first will
pick the metric that looks best"* — relocated from the metric to the
procedure. The rule bought pre-commitment on dates and thresholds and spent
nothing on the comparison itself.

## 2. DEFECT: Test 2 has a bar for two tracks and none for the other two

Test 2's bar, as frozen:

> The backtest max drawdown is **33.05%** (trial 88) and **33.24%**
> (trial 118), recorded in the registry.

Verified at source first, per iron rule 5. `docs/reports/research/trial_registry.jsonl`,
133 rows, `metrics.max_drawdown_fraction`:

| Trial | Registry value | As % | Rule quotes | Slack |
|---:|---|---|---|---|
| 88 | `0.3304782446654657897565823246` | 33.04782446654657897565823246% | 33.05% | **+0.0021755 pp (looser)** |
| 118 | `0.3324023474578522547374688075` | 33.24023474578522547374688075% | 33.24% | **-0.0002347 pp (tighter)** |

Both quotes are correct to the precision given, and the two round in
**opposite directions** — a trial-88 forward drawdown in
(33.047824%, 33.05%] breaches the registry bar but not the quoted one, and a
trial-118 drawdown in (33.24%, 33.240235%] breaches the quoted bar but not
the registry one. Immaterial in magnitude; it is still a reading the
executor picks.

**The real gap is the two tracks with no bar at all.** The weekly rows
declare their own source: `shadow_tw0050.jsonl` carries
`"source_trial": 23` and `shadow_gld.jsonl` carries `"source_trial": 24`
(set at `shadow_signal_tw.py:67,76`). Those trials are in a **different
registry in a different repository** —
`D:/TW-Stock-Trading/docs/reports/research/trial_registry.jsonl`, 24 rows —
and their recorded maxima are:

| Trial | Universe | `max_drawdown_fraction` | As % | ann. Sharpe |
|---:|---|---|---|---:|
| 23 | `0050` | `0.3085102549397344468077160372` | 30.85102549397344468077160372% | 0.426168 |
| 24 | `GLD` | `0.2500876201575916653023598257` | 25.00876201575916653023598257% | 0.498551 |

**The rule cites neither number and never references that registry**, and no
file under `docs/` declares either as a Test-2 bar — searched for `30.85`,
`0.3085`, `25.00876`, `0.25008` and `25.01%`; every hit is an unrelated
substring inside a backtest `report.json`. So on 2026-10-22 the executor
either skips Test 2 on half the tracks or supplies a bar the operator never
declared. Unlike the rounding above, this is **the threshold itself
missing**, not a reading of one.

## 3. DEFECT, smaller: Test 1 is written for one row schema and there are two

Test 1 says *"compare the recomputed exposure path against the recorded one,
**per symbol, per date**."* The daily rows are keyed that way. The weekly
rows are not:

| Field | Daily (88/118) | Weekly (0050/GLD) |
|---|---|---|
| `close` | dict `{BTCUSDT: "...", ETHUSDT: "..."}` | scalar string `"112.80"` |
| `exposure` | dict per symbol | scalar string `"1"` |
| `reason_codes` | dict of lists per symbol | flat list |
| `symbol` | **absent** | present, e.g. `"0050"` |

A harness written against the daily shape does not read the weekly files at
all, and the rule gives no mapping. Mechanical to fix; it is listed because
it is a third thing decided on the day if it is not decided before.

## 4. PASS: "exact agreement" cannot manufacture a false halt from representation

Test 1's verdict for any mismatch is *"implementation defect. Halt and fix."*
Iteration 61 already found one way that can fire on a correct recorder
(replay depth; see section 6). A second way would be representation — a
replay that is right but formats its answer differently. It cannot happen
here.

Measured over **307** (track, date, symbol) exposure cells — all four files,
every row: 71x2 + 71x2 + 11 + 12 — exactly **five** distinct strings appear:

| Exposure string | Cells | Paired reason code |
|---|---:|---|
| `0` | 59 | `WINDOWS_ON_0_OF_4` |
| `0.25` | 28 | `WINDOWS_ON_1_OF_4` |
| `0.5` | 57 | `WINDOWS_ON_2_OF_4` |
| `0.75` | 62 | `WINDOWS_ON_3_OF_4` |
| `1` | 101 | `WINDOWS_ON_4_OF_4` |

The pairing is 1:1 on all 307 cells, with no exceptions in either direction.
And the five strings are exactly the five `str(Decimal(k)/Decimal("4"))`
yields for k = 0..4 — `'0'`, `'0.25'`, `'0.5'`, `'0.75'`, `'1'` — which is
the engine's own expression at `donchian_breakout_ensemble.py:104`
(`fraction = Decimal(on_count) / Decimal("4")`). All five are dyadic
rationals, so a string comparison, a `Decimal` comparison and even a `float`
comparison agree on every cell. **Three plausible implementations of "exact
agreement" give the same verdict.** This route to a false halt is closed.

Noted and not over-read: this is a PASS about *formatting*, and it is a
consequence of the quantity being a quarter. It says nothing about the
replay being right.

## 5. The read's own N is 89, not 90

Arithmetic, since the rule calls 2026-10-22 the "90 d" mark: 2026-07-24 plus
90 days **is** 2026-10-22, so the date is right. The track will hold **89**
rows, covering 2026-07-24..2026-10-21, because **2026-08-09** is permanently
absent (iteration 72). Today the file holds 71 rows across a 72-day span,
one missing. Not a new defect — a consequence of a recorded one — and it
matters only because an executor who asserts 90 and finds 89 has to decide
something on the day.

## 6. Carried from earlier iterations, not re-measured

- **Replay depth.** The rule states none; iteration 61 derived **>= 206**
  bars, against a recorder that re-seeds at index 110 of a rolling 400-bar
  window. A replay seeded at the channel floor can disagree by up to 96 bars
  of state, and the rule's verdict for any mismatch is *halt*.
  `FORWARD_TRACK_REPLAYABILITY_2026-09-16.md`.
- **Test 1's input for trial 118 is unanchored.** 162 (symbol, date) bars of
  high/low, zero anchors, covering 89% of its decision days; trial 88's
  input is 100% anchored and close-only. Iteration 73.
- **The re-fetch has one working host of seven**, and `fetch_candles` exits
  when none passes (`scripts/shadow_signal.py:79`). Iteration 73.
- **No cost is charged on any turnover day**, while the backtest the tracks
  validate charges 15 bps per fill. Iteration 59.

## 7. Outside calibration, and it runs against alarmism

This defect is the **modal** defect of pre-registration, not an unusual one.
Ofosu and Posner reviewed a representative sample of **195** pre-analysis
plans from the EGAP and AEA registries ("Pre-Analysis Plans: An Early
Stocktaking", *Perspectives on Politics* 21(1), March 2023, 174-190, DOI
10.1017/S1537592721000931). As printed:

> Sixty-eight percent of PAPs were judged to have spelled out the precise
> statistical model to be tested; 37% specified how they would estimate
> their standard errors.

> In 44% of PAPs, the number of pre-specified control variables was judged
> to be unclear, making it nearly impossible to compare what was
> pre-registered with what is ultimately presented in the resulting paper.

So **32%** of plans in that sample left the analysis procedure
underspecified, against **90%** that specified clear hypotheses and *"just
over half"* that met all four of the authors' completeness criteria. The
pattern is exactly this program's: the **thresholds** were fixed in advance
and the **procedure** was not. Recorded in the direction that costs the
finding — those authors' own verdict is that *"the glass is half full rather
than half empty"*, and this rule's hardest and most valuable commitment, the
2028 date and the two drawdown bars written at **4 rows**, is intact and
unedited.

**The exposure to drift is therefore bounded, and the bound has one hole.**
On the two crypto tracks an executor filling the gaps chooses *how to
compare*, not *what counts as a pass* — the bars and dates are frozen, so no
threshold can be tuned. On the two weekly tracks that bound does not hold,
because section 2 shows the threshold itself is absent.

## 8. Decision

**Route closed: no proposal may treat the 2026-10-22 read as
executable-as-frozen.** Any document or plan that assumes the read will run
as written must first point at a declaration covering the subject set, the
weekly Test-2 bars, the replay depth and the row-schema mapping.

**The loop declines to write the harness today**, and the reason is not
caution. A harness is the right artifact and the right time is now rather
than on the day — but a harness written against an incomplete rule *silently
fixes* the four undeclared choices in code, and then the code is what gets
cited as the rule. Picking the weekly tracks' drawdown bars is introducing a
metric the operator never declared, which the rule's closing clause forbids.
The implementation is mechanical **once** the specification is closed, and
not before.

This is the **twelfth** operator choice due, and it shares the 2026-10-22
date with items (g) and (i)-(k).

Separately and newly due: the **2026-10-03** deadline for the gate-6 choice
(item (m)) **passed yesterday with no declaration**.
`GATE6_BASELINE_2026-07-25.md:76-78`'s first prerequisite is still
`- [ ] Paper period >= 3 calendar months completed`, and its own window text
reads *"2026-07-03 -> 2026-10-03 window at earliest"*.

## 9. Operator options, none of them taken

**Option A — declare the four missing items before 2026-10-22, then let the
loop build the harness.** Costs one declaration. Needs: the subject set by
filename; the weekly tracks' Test-2 bars (30.85102549397344468077160372% and
25.00876201575916653023598257% are what their own registry records, or an
explicit exemption); the replay depth (**>= 206**; the recorder's own 400 is
safe and adds no new number); and the row-schema mapping. Preserves
everything the rule was written at 4 rows to buy.

**Option B — narrow the read by declaration to the two crypto tracks.**
Removes sections 0, 2 and 3 entirely and leaves only the replay depth, which
iteration 61 already derived. Cost: the weekly tracks then have **no read
rule at all**, and they are two of the three the contract's P1 protects.

**Option C — accept that the choices get made on the day.** Costs nothing
now. It also converts the read from a pre-registered test into an
exploratory one, and the honest consequence must then be written down: a
read whose procedure was chosen with the data visible cannot be cited as
pre-registered evidence, whatever it returns.

The loop takes none of these. Nothing was repaired, nothing frozen was
edited, and `FORWARD_TRACK_READ_PREREGISTRATION.md` is byte-for-byte
unchanged.

## Method note — exactly reproducible, no new script

Every number above is a file listing, a `grep`, a registry field, or a
property of the recorded JSON's representation. No measurement called
`evaluate_donchian_ensemble`, recomputed an exposure, or computed a forward
drawdown or forward Sharpe — the 2026-10-22 read was **not** moved earlier,
which the frozen rule forbids. The ten-script limit is untouched; the
measurements ran inline.

- Executor search: `grep -rn "shadow_trial88\|shadow_trial118\|shadow_tw0050\|shadow_gld\|shadow_.*\.jsonl"`
  over `--include=*.py --include=*.ps1 --include=*.cmd --include=*.toml --include=*.cfg`,
  excluding `./docs/` and `.venv/`.
- Test coverage: `grep -rln "shadow\|forward_track\|track" tests/` -> no output;
  `ls tests/scripts/`.
- Owner search: `grep -rn "operator-run\|who runs\|executor\|responsible\|owner"`
  over `docs/research/FORWARD_TRACK_READ_PREREGISTRATION.md`.
- Bars: `metrics.max_drawdown_fraction` from
  `docs/reports/research/trial_registry.jsonl` (133 rows) and
  `D:/TW-Stock-Trading/docs/reports/research/trial_registry.jsonl` (24 rows),
  read as strings and scaled with `Decimal`.
- Representation: every `exposure` / `WINDOWS_ON_k_OF_4` pair in all four
  track files, counted, against `str(Decimal(k)/Decimal("4"))` for k = 0..4.
- Row counts and dates: `wc -l` plus first/last `date` field per file.
