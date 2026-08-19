# Autonomous research loop — iteration log (append-only)

## 2026-07-21 — iteration 0 (sprint session, human-supervised)

- Universe expanded 2 → 13 qualified symbols; quality gate 13/13 PASS
  (`docs/research/UNIVERSE_EXPANSION.md`, commit 71063e7).
- Experiment 3 pre-registered and FROZEN: cross-sectional momentum,
  16 configs (commit 972c44d).
- Daily loop scheduled: task `CryptoResearchLoop`, 21:37 local,
  runs `scripts/run_research_loop.ps1`.
- **Next step (Q1): implement the `cross_sectional_momentum` engine path +
  tests. Nothing has run yet; registry N is still 21.**

## 2026-07-21 — iteration 1 (Q1, autonomous)

- Research log appended (4 dated lines): Springer FMPM 2025 XS-momentum
  fragility warning, Cambridge JFQA 2024 trend-factor result parked for a
  future family, Trakx practitioner cost-drag confirmation, ACFR AUT
  homogeneous-universe read-out — all mapped to the pre-registered grid
  arms in `docs/research/RESEARCH_LOG.md`.
- `BacktestParameters` extended with `cs_top_k`, `cs_lookback_days`,
  `cs_rebalance_cadence`, `cs_absolute_filter`, `cs_min_pool_size`
  (`src/backtest/types.py`). Strategy whitelist now allows
  `"cross_sectional_momentum"`; the vol overlay is refused for it because
  cross-sectional weights are already normalized.
- Engine dispatch added at the top of `run_backtest` in
  `src/backtest/engine.py`; ladder path untouched. New
  `_run_cross_sectional_backtest` implements the mechanical spec: union of
  candle dates, per-decision lookback ranking, top-K equal-weight snap,
  absolute-filter arm, cadence-driven weekly/monthly rebalance, next-bar-open
  execution reusing `_execute_ladder_change` for order plumbing.
- 12 new tests in `tests/backtest/test_cross_sectional_backtest.py` cover
  validation errors, cadence key semantics, top-K selection, absolute filter,
  min-pool-size gate, monthly cadence firing, hold-day fill absence, cost
  assumptions surfacing, and ladder-strategy non-regression.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check` PASS;
  `mypy --strict src/` PASS (57 files, 0 issues after installing missing
  `websockets` and `types-PyYAML` env deps that pre-dated this iteration);
  `lint-imports` 13/13 KEPT; `pytest -m "not network"` 349 passed in 109.57s.
- Registry N unchanged at 21. Family runs are Q2 work, deferred to a future
  iteration per the multi-session split allowed by the contract.
- **Next step (Q2): run the 16-config experiment-3 family through
  `run_registered_backtest`, register 16 new trials (N: 21 → 37), commit
  registry rows and per-trial return series.**

## 2026-07-21 — iteration 2 (Q2+Q3, operator-triggered "直接接著跑")

- Alignment bug caught BEFORE running: cs decision times started at the
  lookback floor, so 90d/180d arms would have produced misaligned return
  series and the gate report would abort. Fixed with
  `cs_decision_start` (engine floor + validation + 2 tests), pinning all
  family series to the registry window (2676 returns,
  2018-03-05 → 2025-07-01). Commit 6163655.
- Family ran clean (trials 22-37). Winner trial 29 (K=2/180d/monthly/
  filter-on): Sharpe 1.4109, **DSR 0.962102 — first ≥ 0.95 in project
  history** — but MDD 75.08% fails criterion 2 by 23.15pp.
  **Family = registered negative.** Full table + verdict in
  `docs/research/GOALP_EXPERIMENT3_RESULT.md`.
- Stop condition NOT met: candidates-PBO 0.5834 > 0.05 (and the cs family
  folds to one candidates column — defect documented in the result file;
  runner serialization forward-fixed).
- **Next step (Q4, NEXT session per drift guard): pre-register the
  risk-managed combination family (cs momentum signal × drawdown/vol
  overlay) targeting MDD without killing the deflation-surviving Sharpe.
  Also compute trial 29 × trial 4 return correlation (queued read-out).**

## 2026-07-21 — iteration 4 (experiment 4, operator-triggered same-sitting)

- Drift-guard override by explicit operator order, recorded in the
  pre-registration; thresholds all anchored to pre-today numbers.
- Engine: cs vol-overlay refusal lifted; `_cs_vol_scaled_weights` reuses
  `_vol_scaler` verbatim; execution now fires on any effective-vs-held
  drift (daily scaler resizes between monthly selections). Commit 7e50bc8.
- Family ran (trials 38-53, N: 37 → 53). Winner trial 47 (70%/20d/monthly):
  Sharpe 1.0338, DSR 0.8114, MDD 63.76% — **criteria 1 AND 2 fail; fourth
  registered negative.** Full table + structural finding in
  `docs/research/GOALP_EXPERIMENT4_RESULT.md`.
- Structural conclusion: the vol dial sweeps 39%→73% MDD and Sharpe never
  clears the deflation bar anywhere on the dial — volatility is the wrong
  conditioning variable for cs momentum (profits live IN high-vol regimes).
- Trial 29 at N=53: DSR 0.9765 (non-monotonic deflation, third case).
- Scheduled iteration 3 (21:37 headless) ran during this window and
  surfaced the regime-gate hypothesis (BTC 200d-SMA) in RESEARCH_LOG.
- **Next step (Q4, NEXT sitting, drift guard back in force): pre-register
  experiment 5 — directional regime gate (BTC close > 200d SMA) over the
  fixed cs architecture; grid over gate window/hysteresis arms; criteria
  anchored to the same statutory bars (DSR ≥ 0.95, MDD ≤ 51.93%,
  turnover ≤ 53.1).**

## 2026-07-21 — iteration 5 (experiment 5, operator-triggered same-sitting)

- Second recorded drift-guard override; thresholds statutory as before.
- Engine: cs_gate_* parameters + prefix-sum SMA state machine with
  hysteresis (btc-proxy or per-symbol basis, daily or monthly-frozen
  cadence), mutually exclusive with the vol overlay. Commit 273b9d7.
- Family ran (trials 54-69, N: 53 → 69). Winner trial 56 (SMA100/btc/2%/
  daily): Sharpe 1.1651, DSR 0.9115, MDD 58.47% — criteria 1 and 2 fail;
  **fifth registered negative.** Full table + frontier analysis in
  `docs/research/GOALP_EXPERIMENT5_RESULT.md`.
- Breakthrough inside the negative: trials 62/64 (SMA200/btc/daily) put
  cs MDD INSIDE the statutory bar for the first time (51.83% ≤ 51.93%) at
  Sharpe 0.978 — the feasible region exists; the statutory corner
  (both bars at once) is still open.
- Winner-gap trend exp 3→4→5: 75.08% → 63.76% → 58.47% MDD. Directional
  gating works where vol targeting failed. Monthly-frozen gates are
  disaster arms; daily gate + 2% hysteresis halves turnover and raises
  Sharpe. Trial 29 at N=69: DSR 0.9802 (fourth non-monotone rise).
- **Next step (Q4, NEXT sitting unless operator overrides): pre-register
  experiment 6 — multi-horizon trend-factor selection (Cambridge JFQA
  2024, already in RESEARCH_LOG) under the proven SMA200/btc/daily gate;
  or K/lookback variation under that gate. Statutory bars unchanged.**

## 2026-07-21/22 — iteration 6 (experiment 6, operator-triggered "continue")

- Third recorded drift-guard override; thresholds statutory as before.
- Engine: cs_horizon_days multi-horizon score (+ decision-floor semantics
  fix so short/long-horizon arms share the 2676-return window). Commit
  2e9142f.
- Family ran (trials 70-85, N: 69 → 85). Winner trials 78/79 (exact tie,
  filter arm never triggered — grid design lesson recorded): blend
  28+56+112+224, K=2, weekly. Sharpe 0.9855, DSR 0.8345, MDD 53.49% —
  criteria 1 and 2 fail; **sixth registered negative.** Full table in
  `docs/research/GOALP_EXPERIMENT6_RESULT.md`.
- **Lineage closed**: JFQA multi-horizon did not replicate (blend ≈
  exp-5's single lookback); four arms now inside the MDD bar but best
  in-bar Sharpe 0.917 vs the ~1.3 the N=85 deflation demands. 64
  registered cs-momentum arms cannot satisfy both statutory bars at once.
- Trial 29 at N=85: DSR 0.9856 (fourth consecutive non-monotone rise);
  trial 37 at 0.9494. PBO candidates 0.8241.
- **Next step (Q4, NEXT sitting unless operator overrides): pick the fork
  recorded in the result file — (1) Donchian breakout ensemble
  pre-registration (new signal space, SSRN 2025 in RESEARCH_LOG), or
  (2) consolidate: stop spending N, redirect iterations to gate-6
  evidence until the October holdout. One choice, pre-registered.**

## 2026-07-22 — iteration 7 (experiment 7, operator-triggered "繼續找")

- Fork resolved by operator order: new signal space. Fourth recorded
  override; thresholds statutory as always.
- Engine: donchian_breakout_ensemble strategy module on the ladder path
  (4-window state machines → 5-rung ladder), _SizedDecision gained
  generated_at_bar_close, ladder path gained the exp-5 regime gate.
  Commit f625d87.
- Family ran (trials 86-93, N: 85 → 93). Winner trial 88 (10+20+55+110/
  mid_channel/no gate): Sharpe 1.1821, **DSR 0.9267 — missed by 0.0233,
  the closest any winner has come** — MDD 33.05% and turnover both PASS.
  **Seventh registered negative, but the first with both risk bars passed
  family-wide.** Full table in `docs/research/GOALP_EXPERIMENT7_RESULT.md`.
- Signal space > wrapper: Donchian's WORST arm beats every MDD-compliant
  cs arm on both axes. Gate on a self-exiting signal double-brakes
  (lowers Sharpe in 3 of 4 pairings) — lesson recorded.
- vs incumbent trial 4 (same universe): equal terminal wealth, MDD
  33% vs 52%.
- Trial 29 at N=93: DSR 0.9852 (plateau). PBO candidates 0.8705.
- **Next step (Q4, NEXT sitting unless operator overrides): experiment 8
  — Donchian on the 13-symbol universe. Engineering prerequisite first:
  ladder engine must admit staggered listings (per-symbol decision
  eligibility instead of intersection alignment) with tests; then the
  family pre-registration. Statutory bars unchanged.**

## 2026-07-22 — iteration 9 (experiment 8, operator-triggered "continue")

- Fifth recorded override; thresholds statutory. Iteration-8 engine
  prerequisite verified green (66 tests) and its unpushed commit 7f8a0b7
  pushed first.
- Family ran (trials 94-101, N: 93 → 101) on the staggered 13-symbol
  universe, 1/13 budgets. Winner trial 96 (fast/mid_channel/no gate —
  exp-7 winner architecture widened): Sharpe 1.0004, DSR 0.8317,
  MDD 46.59% — criterion 1 fails; **eighth registered negative.**
- **Breadth hypothesis falsified in all eight pairings** (winner −0.18
  Sharpe vs trial 88): cash drag from idle pre-listing budgets + altcoin
  false breakouts. Barbell windows underperformed fast. Gate verdict
  FLIPPED on the diversified book (improves MDD, Sharpe-neutral) — the
  exp-7 double-brake was BTC/ETH-specific.
- Deflation mechanics: trial 37 became the registry's SECOND gate-4 pass
  (0.9532) on variance compression alone — MDD 67.5% keeps it
  disqualified; trial 88 GAINED to 0.9330 and remains the risk-compliant
  frontier (0.017 short). Trial 29: 0.9870.
- Hypothesis pool (not auto-run): SSRN-faithful vol-based sizing on the
  Donchian book (new allocation-model engine feature); barbell variants
  parked. Full table in `docs/research/GOALP_EXPERIMENT8_RESULT.md`.
- **Next step: NEXT sitting weighs the N-arithmetic explicitly before
  any ninth family (every family raises every trial's bar); October
  holdout untouched; gate-6 evidence accumulation continues in the
  background.**

## 2026-07-22 — iteration 8 (Q1 for experiment 8, autonomous)

- Research log appended (4 dated lines): arxiv 2510.23150 (2025-10-28)
  "medium-term horizon is redundant when short and long are present —
  barbell beats equal-weight" (parked as follow-up family, not this
  iteration); CoinAPI/Concretum/StratBase practitioner notes on survivor-
  ship bias and point-in-time universe construction (load-bearing for
  exp-8); Zarattini/Pagani/Barbon SSRN 2025 revisited (their headline
  rests on a survivorship-bias-free wide universe — universe size is
  central to the claim). All mapped to the exp-8 lineage.
- `BacktestParameters.allow_staggered_listings: bool = False` added
  (`src/backtest/types.py`) — additive optional field; every existing
  call site defaults to intersection mode, so the entire pre-exp-8
  registry (trials 1..93) is bit-for-bit reproducible.
- Engine gained `_ladder_decision_times(...)` (union or intersection),
  `_partial_execution_candles(...)` (per-symbol next-bar slice), and a
  staggered-mode branch in the main ladder loop (`src/backtest/engine.py`):
  active-symbol filter per decision day, subset ladder targets, per-symbol
  benchmark anchor (reuses `_cs_benchmark_equity`), padded ledger marks
  (reuses `_cs_equity_at_marked`). The cs path is untouched — it already
  uses the union-of-dates model natively.
- 3 new tests in `tests/backtest/test_backtest_engine.py`:
  (1) intersection mode STILL rejects a staggered universe (contract
      preserved for every pre-exp-8 family);
  (2) staggered mode: BTC lists day 0, ETH day 100; ETH's first signal is
      strictly later than BTC's, union has strictly more BTC decision days
      than ETH, both symbols fill from their respective listing days;
  (3) parity — turning the flag on with an aligned universe reproduces the
      intersection result bit-for-bit (metrics, trade count, signals).
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check` PASS
  (2 files reformatted, re-checked green); `mypy --strict src/` PASS
  (58 files, 0 issues); `lint-imports` 13/13 KEPT; `pytest -m "not network"`
  366 passed in 50.21s (was 349 at iteration 1 — deltas across intervening
  iterations plus the 3 new engine tests this iteration).
- Registry N unchanged at 93. Family run (Q2) and pre-registration (Q4)
  are deferred to the next iteration per the multi-session split the
  contract allows and the drift-guard scheduling.
- **Next step (Q4, NEXT sitting unless operator overrides): pre-register
  experiment 8 — Donchian breakout ensemble on the 13-symbol qualified
  universe with `allow_staggered_listings=True`, grid drawn from the
  exp-7 family (best fast/slow window pair × exit rule × gate off/on),
  criteria anchored to the same statutory bars (DSR ≥ 0.95,
  MDD ≤ 51.93%, turnover ≤ 53.1).**

## 2026-07-23 — iteration 10 (N-arithmetic weigh-in, autonomous)

- Research log appended (4 dated lines): Lopez de Prado/Fabozzi SSRN
  2026-03 on FDR-in-finance validates "every family raises the bar"
  arithmetic; Quanterlab DSR foundations for the √(2·ln N) growth law;
  Zarattini/Pagani/Barbon SSRN 2025 mechanism read — Donchian ensemble ×
  **vol-based position sizing** is the interlocking half we never tested;
  Poluri SSRN 2025 ATR-scaled Donchian as sibling spec for a
  vol-sized-Donchian family grid.
- N-arithmetic recorded in `docs/research/N_ARITHMETIC_2026-07-23.md`
  (numbers verified against gate_report_2026-07-22.json only):
  σ_effective back-solved from trial 88's DSR row = 1.4332; at N=101 the
  DSR ≥ 0.95 bar is SR_ann=**1.2465** and trial 88's gap is **+0.0644**;
  each 16-config family lifts the bar to SR_ann≈1.255 (N=117) and costs
  trial 88 ≈0.003 DSR on pure bar-rise mechanics; net observed exp-8 gain
  was +0.0063 DSR (+0.0088 raw compression, exp-8 winners clustered
  0.92–1.00 below trial 88's 1.18).
- Decision recorded (does NOT pre-register anything — drift guard):
  next iteration is authorized to pre-register the SSRN-faithful
  vol-sized Donchian family IF AND ONLY IF the engine work
  (allocation-model plumbing + tests) fits inside a single iteration;
  else consolidate to gate-6 evidence accumulation until the October
  holdout. Any wrapper re-sweep, barbell variant, or ATR-on-cs-momentum
  family is strictly negative EV under the arithmetic and is refused.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (111 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT; `python -m pytest -m "not network"` 366
  passed in 49.42s. Registry N unchanged at 101. Tree remained clean
  through the iteration (docs-only edits).
- Trial 88 standing unchanged: DSR 0.9330, MDD 33.05%, Sharpe 1.1821 —
  incumbent risk-compliant frontier. Trial 29 sealed off from October per
  holdout protocol; October holdout untouched.
- **Next step (Q1+Q4, NEXT sitting): scope the SSRN-faithful vol-sized
  Donchian allocation-model engine feature (target-vol weights over the
  Donchian ladder). If bounded to one session (spec + tests + green
  tree), land it and pre-register experiment 9 with a frozen grid
  (window sets × vol target × cap arm). If unbounded, log a
  consolidation switch: stop spending N, redirect subsequent iterations
  to gate-6 real-run-readiness work (`docs/runbooks/`, holdout lock
  hygiene, notifier drills) until 2026-10.**

## 2026-07-24 — iteration 11 (experiment-9 scoping, consolidation switch, autonomous)

- Research log appended (4 dated lines): Zarattini/Pagani/Barbon SSRN
  5209907 mechanism re-read on the Concretum Group companion page
  (Sharpe 1.58, alpha +14% vs BTC 2015-01→2025-03 attributed **jointly**
  to Donchian ensemble AND cross-asset vol-based sizing — not per-symbol
  overlay); Concretum "Position Sizing in Trend-Following" naming
  vol-targeting vs vol-parity vs pyramiding as three distinct
  allocation models; Alvarez Quant Trading inverse-vol formula with
  25%-per-name cap as the standard baseline; Bloomberg Cryptocurrency
  Vol Target Indices spec (2025-08-05) anchoring 10/15/25% target-vol
  values in institutional use.
- Iteration-10's gate honored: engine work scoped honestly BEFORE any
  code changes. Path A (reuse `_apply_vol_overlay` for Donchian by
  lifting the exp-7 refusal in `types.py:110-115`) is bounded to one
  iteration but is NOT SSRN-faithful (per-symbol overlay, not cross-
  asset inverse-vol) and is explicitly refused by the 2026-07-23
  N-arithmetic doc as a wrapper re-sweep. Path B (SSRN-faithful:
  new allocation-model dispatch, cross-asset weight normalization,
  cap arm, portfolio-vol rescale) requires new `BacktestParameters`
  fields, new `_dc_vol_target_weights(...)`, execution rewire skipping
  `build_ladder_targets`, staggered-mode interaction, ≥6-8 tests, plus
  runner + registry + pre-registration — honest estimate 2-3
  iterations, not one. Full scoping in
  `docs/research/EXPERIMENT9_SCOPING_2026-07-24.md`.
- **Verdict: UNBOUNDED**. Consolidation switch engaged per iteration-10
  contingency. No exp-9 pre-registration written. No family run.
  Registry N unchanged at 101. Trial 88 incumbent-frontier unchanged
  (DSR 0.9330, MDD 33.05%, Sharpe 1.1821). The SSRN vol-sized
  Donchian family is deferred until October holdout completes OR an
  explicit operator authorization overrides the consolidation.
- First gate-6 baseline recorded from the live `exec_quote` stream
  (`data/runtime/events.jsonl` 42 events, 2026-07-03 → 2026-07-23,
  21 days × 2 symbols): BTCUSDT median spread 0.00 bps, ETHUSDT
  median 0.05 bps; round-trip estimate `2 × spread_median + 2 × fee_bps`
  = 20.00 / 20.10 bps respectively vs the gate-6 cap of 37.5-45 bps
  (`VALIDATION_GATE_CONTRACT.md §6`). Cost model comfortably inside
  the calibration bar on the two live symbols so far; 90-day window
  and decision→capture drift stat remain queued. Baseline table in
  the scoping doc.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (111 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT (via `.venv/Scripts/lint-imports.exe` —
  `python -m lint_imports` is not the entry point on Windows; noted
  for future iterations); `python -m pytest -m "not network"` 366
  passed in 50.48s. Registry N unchanged at 101; tree docs-only.
- Holdout hygiene: `docs/reports/research/holdout_lock.json`
  `spent=false`, `holdout_start=2025-07-02T23:59:59.999000+00:00`,
  `locked_at=2026-07-03T02:44:47.633808+00:00` — sealed and untouched
  this iteration.
- **Next step: NEXT sitting continues consolidation work — likely
  targets are (a) adding a decision→capture drift stat to
  `src/runtime/quotes.py` outputs so gate-6 measurement covers
  slippage in addition to spread, (b) drafting an operator-facing
  holdout spend rehearsal note against `PRE_HOLDOUT_PROTOCOL.md`, or
  (c) auditing the daily-cycle runbook against the actual harden
  script output. Any exp-9 resumption requires an explicit operator
  override recorded per drift-guard protocol.**

## 2026-07-25 — operator sprint (robustness, exp 9, exp 10; consolidation lifted)

- Operator lifted the iteration-11 consolidation and granted an unbounded
  budget (「想盡辦法，做盡測試」/「預算很充足，你可以一直跑」).
- **Robustness battery on trial 88** (trials 102-109, never-nominatable):
  all eight pre-declared criteria PASS — six window perturbations hold
  Sharpe 1.123-1.211 / MDD 29.7-37.7% (spread 0.087 vs a 0.35 bar), cost
  stress 1.126 at 2x and 1.071 at 3x. Zero-cost diagnostics:
  P(Sharpe<=0)=0.0000, 2022 is a real losing year at 22.6% drawdown,
  correlation 0.927 with the live incumbent which it dominates on every
  axis. `docs/research/ROBUSTNESS_TRIAL88_RESULT.md`.
- **Shadow track** started (commit 58f7af6) and later doubled: trial 88
  and trial 118 each accumulate forward-only records daily at 08:20
  (task CryptoShadowTrial88). First rows 2026-07-24; the two configs
  already disagree materially, which is what a forward record is for.
- **Experiment 9** (trials 110-117, SSRN-faithful inverse-vol sizing):
  winner trial 112 DSR 0.9153 — **ninth negative**. All eight arms score
  below equal-weighted trial 88. Third family across two signal spaces to
  confirm that volatility targeting on an unleverable spot book can only
  de-risk. Sizing is closed.
- **Experiment 10** (trials 118-125, ATR-scaled channel exits):
  **first family in ten to pass all three of its own criteria.**
  Winner trial 118 (ATR 14 / multiple 2): Sharpe 1.2411,
  **DSR 0.950514 PASS**, MDD 33.24% PASS, turnover 11.10 PASS. It is the
  first risk-compliant trial ever to clear gate 4.
- Honest limits recorded in the result doc: the DSR margin is 0.0005 (at
  the bar, not above it); the winner sits at a grid endpoint; gate 3 PBO
  is 0.8451 so the loop stop condition is NOT met and the search does not
  halt; and one more 8-arm family would push trial 118 back under 0.95 on
  bar-rise mechanics alone.
- **Next step: robustness battery on trial 118 (its own, per experiment
  10's honesty clause) — parameter neighbourhood plus 2x/3x cost stress,
  all arms never-nominatable. After that, no new families without an
  explicit N-arithmetic weigh-in, because the margin cannot absorb one.**

## 2026-07-25 (late) — trial-118 battery + final N=133 report

- Battery (trials 126-133, never-nominatable): all eight criteria PASS.
  Perturbations Sharpe 1.081-1.230 / MDD 29.9-43.4% (spread 0.149);
  cost stress 1.197 at 2x and 1.152 at 3x — the project's strongest.
- **Endpoint doubt resolved**: arm A3 at ATR multiple 1.5 scores 1.114,
  below multiple 2's 1.241, so experiment 10's boundary winner is a
  genuine interior optimum after all.
- **Honest counterweight**: trial 118 IS its own neighbourhood maximum
  (trial 88 was not) — the weaker signature, recorded to travel with
  every future quote.
- **Advance prediction WRONG, corrected in the result doc**: DSR was
  predicted to fall under 0.95 at N=133; measured 0.950140, still
  passing, because the clustered battery arms compressed cross-trial
  variance as fast as the bar rose. Fifth measured case of non-monotone
  deflation.
- Final report N=133: gate 2 PASS; gate 3 candidates-PBO 0.6518 (down
  from 0.8451) and all-columns 0.7326 — still FAIL by an order of
  magnitude; gate 4 passing trials [29, 37, 118], of which only 118 is
  risk-compliant.
- **Standing decision: no new families.** The margin (0.0001 at N=133)
  cannot absorb one, and every closed lineage is documented. Loop work
  returns to: shadow-track health (trial 88 + trial 118, daily 08:20),
  gate-6 evidence, and the October holdout per PRE_HOLDOUT_PROTOCOL.

## 2026-07-25 — iteration 12 (gate-6 evidence + holdout rehearsal, autonomous)

- Research log appended (4 dated lines): Bybit Q1 2026 spot slippage
  publication (institutional 0.01-0.06 bps band on US$10k BTC orders —
  our recorded 0.00/0.05 bps sits inside the same order of magnitude);
  QuantMedia slippage/latency modeling reference (mid-quote fills
  overstate Sharpe by 0.5-1.0 vs a decision-to-fill model);
  Turbine blog on backtest/live divergence (reinforces
  no-new-families standing at margin 0.0001); VARRD one-shot OOS
  restatement (external anchor for the holdout rehearsal note).
- Standing decision honored: **no new families**, no new
  pre-registrations, no trial IDs reserved. Registry `N` unchanged
  at 133; trial 118 remains the sole risk-compliant gate-4 pass;
  trial 88 remains the incumbent-frontier shadow. Holdout untouched
  (`spent=false`, `locked_at=2026-07-03T02:44:47.633808+00:00`).
- Shadow-track health: `data/runtime/shadow_trial88.jsonl` and
  `data/runtime/shadow_trial118.jsonl` each hold 1 row, first record
  2026-07-24 (recorded 2026-07-25 morning by task
  CryptoShadowTrial88). Both healthy — new files, first row within
  contract 48h rule; next 48h check is 2026-07-27. No diagnosis or
  fix needed.
- Gate-6 evidence: refreshed baseline snapshot from
  `data/runtime/events.jsonl` (44 exec_quote events, +2 vs
  iteration 11's 42) into a new consolidated doc
  `docs/research/GATE6_BASELINE_2026-07-25.md`. Numbers unchanged
  from iteration 11: BTCUSDT median 0.00 bps, ETHUSDT median 0.05
  bps, both round-trip estimates 20.00 / 20.10 bps vs the 37.5-45
  bps cap. Sample still short of the 90-day §6 requirement.
- Iteration-11 queued gate-6 stat delivered: decision→capture drift
  computed post-hoc from already-recorded `close_time` and
  `captured_at` fields (no runtime change — iron rule 1 preserved).
  Median 308.4 s (~5m 08s, matches the 08:05 Taipei daily cycle);
  two catch-up outliers (2026-07-06 ~3.4 h, 2026-07-11 ~19.8 h)
  pulled the mean to 4099.7 s. Tail is bounded by the daily
  re-fire; asymmetry documented, no recalibration required at
  N=44; next re-check at N ≥ 60.
- Operator-facing holdout spend rehearsal note included in the
  same file — command sequence for the single-use spend, both
  pre-declared nominations (N1 daily_trend_ensemble no-overlay,
  N2 trial-7 overlay config), pass bars, consequence table, and
  the explicit forbid list (no third nomination, no re-runs, no
  post-hoc parameter tweaks). Doc-only; no CLI flag verified today
  (called out in the doc so the operator re-checks `--help` before
  the October session).
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (118 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT (via `.venv/Scripts/lint-imports.exe`);
  `python -m pytest -m "not network"` 378 passed in 50.00s. Tree
  docs-only (2 files); registry N unchanged at 133.
- **Next step: NEXT sitting continues consolidation work — likely
  targets are (a) 48h shadow-track diff read-out (trial 88 vs
  trial 118 exposure disagreement) once both files have ≥ 3 rows,
  (b) audit of `RUNBOOK_DAILY_CYCLE_RELIABILITY.md` against the
  observed 9% catch-up rate (2 late captures in 22 runs), or
  (c) survey of `configs/costs/` vs the refreshed baseline to
  confirm no calibration drift has crept in. No family resumption
  without an explicit operator override recorded per drift-guard
  protocol; October holdout untouched.**

## 2026-07-26 — PBO scope diagnostic (zero registry cost)

- Tested the one available excuse for gate 3's failure: that CSCV over
  ~100 near-duplicate columns measures unrankable twins rather than
  overfitting. Computed PBO over nine DISTINCT architectures (trials
  4, 7, 29, 56, 78, 88, 96, 112, 118).
- **Hypothesis refuted, in the worse direction**: distinct-family PBO is
  **0.7411**, higher than candidates (0.6518) and all-columns (0.7326).
  The gate-3 failure is not a column-composition artefact.
- Consequences recorded in
  `docs/research/PBO_SCOPE_DIAGNOSTIC_2026-07-26.md`: in-sample ranking
  of these strategies is worse than a coin flip out of sample; trial
  118's gate-4 pass does NOT imply it is the best of the nine; and since
  all nine share 0.9+ correlated long-only crypto trend beta, **gate 3
  may be unpassable for any strategy this product is legally allowed to
  run**. October's report should state that as a finding, not discover it.
- No rule changed, no verdict moved, no alternative representative set
  tried after seeing the number (that search is exactly what the gate
  exists to catch).
- Forward shadow tracks are now the highest-value evidence stream: if
  in-sample ranking is uninformative, only out-of-sample observation can
  discriminate.

## 2026-07-26 (later) — correlation retraction + combination pre-registered

- **Retraction**: the PBO diagnostic asserted the nine architectures
  correlate at 0.9+. Measured: mean 0.628, min 0.359, max 0.958. Reading
  2 of that document ("the constraint space is too narrow, gate 3 may be
  structurally unpassable") is RETRACTED in place — it rested on the
  wrong number. Reading 1 (selection does not generalize) stands.
- The measured correlations point the other way: at ~0.63, combining
  candidates buys real variance reduction, and a combination rule
  performs no selection at all — the textbook answer to a high PBO.
- Exploratory blends (zero registry cost, from existing return series):
  nine hand-picked architectures Sharpe 1.4533 / MDD 34.77% / 27.2x;
  **all 133 registered columns 1.2017 / 39.22%; all protocol candidates
  1.1147 / 44.96%.** The gap between 1.45 and 1.11-1.20 IS the hindsight
  premium, disclosed rather than banked.
- **Experiment 11 pre-registered** (`GOALP_EXPERIMENT11_PREREGISTRATION.md`):
  combination instead of selection, members fixed by a mechanical rule
  (trial 4 plus every family's own pre-declared winner, including the
  bad ones — trials 5 and 47 are restored), two weighting arms (equal,
  inverse-vol), weight optimization forbidden, statutory bars.
- Engine prerequisite declared: a real combination path that nets
  offsetting trades across sleeves. Return-series averaging is the
  conservative bound only, never the registered result.

## 2026-07-26 (cross-market) — trial 118 tested in Taiwan, unchanged: it did not transfer

- Ported the Donchian+ATR strategy into `D:\TW-Stock-Trading` (376 tests
  green, existing paths untouched) under a frozen pre-registration
  allowing ONE configuration and forbidding any tuning on TW data.
- 0050 adjusted, 2004-2025, TW cost model unchanged: trial 118's config
  scores **Sharpe -0.3055, MDD 40.48%, 100k TWD to 66,330** against
  buy-and-hold's 0.7159 / 55.75% / 787,034. **DID NOT TRANSFER.**
- Not a broken port: mean exposure 0.384 over 5,218 days, all five rungs
  used, 165 trades.
- Mechanism: the declared context arm (trial 88's mid-channel exit)
  scores +0.4262 on identical data. One parameter — the exit rule — is
  worth +0.06 Sharpe in crypto and -0.73 in Taiwan. The crypto-optimal
  exit is the Taiwan-worst exit.
- Consequence appended to the experiment-10 result (verdict unchanged):
  trial 118's distinguishing choice is crypto-specific. Direct
  cross-market confirmation of what PBO 0.7411 implied statistically.
- **Standing guidance for any future work: a candidate's standing in this
  program now requires cross-market evidence before it can be described
  as an edge rather than a fit.**

## 2026-07-26 (cross-market combination) — PASS

- Pre-registered before computing: same untuned mid-channel Donchian rule
  in crypto and on 0050, fixed 50/50 monthly rebalanced, daily
  resolution, criteria and limitations frozen (the higher-scoring 30/70
  blend seen in exploration was excluded by design).
- Result over 2018-03-06 → 2025-07-01: crypto sleeve Sharpe 1.1829 /
  MDD 33.05% / 14.26x; Taiwan sleeve 0.9816 / 14.83% / 2.02x;
  **50/50 combination 1.3437 / 19.73% / 6.00x**. Daily correlation
  **-0.0041** — effectively independent.
- All three pre-declared criteria PASS.
- **Why it matters**: it chooses nothing. Same rule both markets, weights
  fixed in advance, improvement from diversification arithmetic rather
  than from a fitted parameter — the one channel PBO 0.7411 and the
  trial-118 cross-market refutation do not indict.
- **What it costs**: terminal wealth 14.26x to 6.00x. Better path, less
  money, and product law forbids levering it back. That is a decision
  about what a person can hold, recorded as such.
- Limits declared in advance: FX unmodeled, the window flatters the
  Taiwan sleeve (0.98 here vs 0.43 over its full 21 years), no DSR, one
  correlation estimate, two sleeves only.
- **Next: forward tracking of the Taiwan sleeve so the combination can be
  observed as a book. Backtests cannot strengthen this; only unseen data
  can.**

## 2026-07-26 (documentation + a blocked forward track)

- README updated in both repositories with the honest search log: 133
  trials, ten registered negatives, the trial-118 cross-market
  refutation, and the combination result with its wealth cost stated.
- second_brain project note updated to the current state.
- **Blocked, filed rather than worked around**: the TW forward shadow
  track cannot start yet. `scripts.ingest_public_ohlcv` completed but
  wrote through 2026-07-03 while reporting 5,675 known days against
  5,661 written — roughly 14 sessions fetched and not persisted. The
  shadow script's staleness guard refused to record rather than repeat a
  22-day-old signal into a forward record, which is the correct
  behaviour. **Next concrete task: find why the writer stops short of
  TWSE's coverage, fix it, then start the TW track.** Until then the
  cross-market combination has forward evidence on the crypto sleeve
  only.

## 2026-07-26 (later) — sleeve 3: gold, built and run the same day

- **Data source found and gated.** Stooq is behind a JavaScript
  proof-of-work bot wall and was not worked around. Yahoo's chart
  endpoint plus FinMind's `USStockPrice` are two independent providers
  for GLD; both were fetched. `range=max` silently downsamples 1d to
  monthly (261 rows instead of 5,453), so an explicit epoch window is
  used. Ingestion gate: 5,452 bars 2004-11-18..2026-07-23, **both
  providers agreeing on every one of them**, worst close disagreement
  6e-8, zero bars where adjusted close differs from raw, no gap over 10
  days. Yahoo's 2026-07-24 row was holed and was dropped rather than
  patched — the reason two providers are fetched at all.
- **Pre-registration frozen before the run**
  (`SLEEVE3_GOLD_PREREGISTRATION.md`, TW repo) with GLD chosen a priori,
  SPY and TLT rejected in writing, four criteria, a cost model harsher
  than US retail, brakes set so they cannot bind, and a binding
  market-shopping guard.
- **Result: PASS on all four** (`SLEEVE3_GOLD_RESULT.md`). TW trial 24.
  Three sleeves, one third each, monthly rebalanced,
  2018-03-06..2025-07-01: Sharpe 1.3437 to **1.4108**, max drawdown
  19.73% to **14.90%**, correlations gold/crypto +0.0767 and
  gold/Taiwan +0.0331. Lower drawdown in all four sub-periods;
  covid-window Sharpe −3.11 to −0.02.
- **Recorded against it:** terminal wealth 6.00x to 3.94x; the gold
  sleeve loses to holding gold (2.44x vs 6.96x, at a lower Sharpe); and
  its correlation to crypto **rises** in crypto's worst 5% of days
  (+0.077 to +0.105), unlike Taiwan's. Gold is not a hedge; it is flat.
- **Registry defect found and fixed.** Every row was stamping the SMA
  ensemble's lookbacks regardless of what ran, so trials 23 and 24 are
  on record naming a strategy they did not execute. Rows are
  append-only; both stay wrong, the result document is the correction,
  and rows after `63e2996` describe their own run. A test now fails if a
  Donchian run stamps SMA lookbacks.
- **Both non-crypto sleeves now record forward.** `shadow_signal_tw` was
  generalized to a TRACKS tuple; first GLD row 2026-07-23, exposure 0.0.
- **Next: P1 is keeping all three tracks alive.** A fourth sleeve is
  permitted only under the market-shopping guard, and must be weighed
  against the measured cost — every sleeve so far bought a smaller
  drawdown with terminal wealth.

## 2026-07-26 (later still) — where the money goes, and a closed route

- **Diagnostic** (`analyze_idle_capital.py`, no registry cost): the
  three-sleeve book holds **66.2% cash on average**, mean gross exposure
  0.3380, while at least one sleeve is long on 87.4% of days. The
  terminal-wealth cost of combining is mostly idle capital, not the
  arithmetic of diversification.
- **Pre-registered and run the same sitting** (operator override
  recorded): equal share among the sleeves actually long, zero free
  parameters, gross provably never above 1.
- **REGISTERED NEGATIVE** (`CASH_AWARE_ALLOCATION_RESULT.md`).
  Deployment 0.3380 to 0.5557 and multiple 3.94x to 4.39x, but drawdown
  14.90% to **23.49%** and Sharpe 1.4108 to **1.3027**. Two of three
  criteria fail. The pre-registration had already written what this
  would mean: the idle cash was buying something real.
- **Route closed with a mechanism**: within product law (spot,
  long-only, unlevered) the smoother path and the smaller multiple are
  the same fact, and reallocating idle capital does not separate them.
  The rule concentrates hardest exactly when fewest markets trend. This
  is an upper bound — reallocation costs are unmodelled and would only
  make it worse.
- **Do not re-open this by adding a cap parameter or a tilt.** That is a
  parameter family on a portfolio rule, and P3 refuses those for the
  same reason it refuses them on signals.

## 2026-07-26 (last) — the comparison the program answers to, and a correction

- **Against buy-and-hold** (`VS_BUY_AND_HOLD_2026-07-26.md`). Every
  report already carried a `benchmark_equity` series and no document had
  ever read it. The trend rule beats holding the asset in **one of three
  markets**: crypto 14.26x vs 6.05x (and 33% drawdown vs 81%), but
  Taiwan 2.15x vs **7.75x** and gold 2.44x vs **6.99x** — gold loses on
  Sharpe too. The three-sleeve book: 3.94x vs **5.42x** for holding the
  same three assets equally, winning on drawdown (14.90% vs 40.59%) and
  Sharpe (1.41 vs 1.05). **It is a risk-preference result, not a return
  result**, and the README now says so.
- **Correction, same day**
  (`SELECTION_PROVENANCE_CORRECTION_2026-07-26.md`). Calling the sleeve
  rule "untuned" was false and I had written it hours earlier.
  Experiment 8's frozen pre-registration names {10,20,55,110} as
  experiment 7's winner (line 54), lists `mid_channel` as one of two
  exit arms (line 57), and declares the winner as highest full-window
  Sharpe (line 66). Two rounds of selection, both on crypto.
- **Precise survivor:** the *transfer* to Taiwan and gold was untuned and
  the *portfolio construction* chose nothing. The *signal rule* carries
  crypto's search history everywhere it goes. Frozen result docs were
  not edited; the README and today's diagnostic were corrected in place.
- **This is the third independent line** saying the crypto result does
  not generalize, alongside PBO 0.7411 and trial 118's cross-market
  refutation.
- **Queue tightened:** a fourth sleeve must now beat buy-and-hold in its
  own market on return or Sharpe **before** it can be proposed. Adding a
  leg that loses on both, purely for a portfolio-level Sharpe bump, is
  buying drawdown reduction that holding less would buy more cheaply.

## 2026-07-26 (final) — the winner is the maximum of its family

- **Registry-wide benchmark comparison**
  (`REGISTRY_VS_BENCHMARK_2026-07-26.md`). All 133 rows already carried
  `benchmark_final_equity`; nothing had ever read that column.
- ~~**Trial 88 ranks 1 of 16 in its own family.** Its system/benchmark
  ratio is 2.381; the family median is 1.242; the spread runs 2.381 down
  to 0.419; and 8 of 16 members lose to buy-and-hold outright. A coin
  flip decides whether a family member beats holding the asset.~~
  **Retracted same day — the 16 rows are two different universes.**
  Experiment 7 is BTC/ETH only (8 rows) and experiment 8 is the
  13-symbol book (8 rows), declared as a separate test in exp 7's own
  pre-registration. Pooling them averaged 100% and 0% into a fake 50%.
- **Corrected: trial 88 ranks 1 of 8, and all 8 beat buy-and-hold.**
  Family median 2.005, floor **1.789** — the worst member still beat
  holding by 79%. Selection premium is 2.381/2.005 = **+18.8%**, not the
  ~50% first claimed. Within BTC/ETH the effect is parameter-robust.
- **But experiment 8 — the same rule on 13 symbols — beat buy-and-hold
  in 0 of 8 configurations**, median ratio 0.543. The rule does not
  survive universe expansion inside its own asset class.
- **Distribution is bimodal, not random.** Families either win every arm
  (exp 1, 2, 7, 9, 10) or lose most (exp 3, 5, 6, 8). The overall 57.9%
  is the average of two modes and means little alone.
- **Across the whole search: 77/133 (57.9%) beat buy-and-hold**, median
  ratio 1.099. Regime gate 8/33 (median 0.697), cross-sectional
  momentum 3/16 (median 0.643) — both lose in about three quarters of
  their configurations.
- **The real finding is scope, not selection.** Every out-of-scope test
  lands below the exp-7 family's *worst* member (floor 1.789): the
  13-symbol crypto book 0.419-0.695, Taiwan 0.277, gold 0.349. So the
  supportable statement is **"the rule works on BTC/ETH in this window,
  robustly across 8 configurations, and has failed every extension
  tested — more crypto symbols, another equity market, another asset
  class."** Scope is testable going forward; a cherry-picking story is
  not what the data says.
- **Fourth independent line** saying the result does not generalize:
  PBO 0.7411, trial 118's cross-market refutation, losing to
  buy-and-hold in two of three markets, and now 0/8 on universe
  expansion.
- **Lesson recorded in the tool, not just the prose.** The grouping key
  now carries the experiment number so two universes can never be
  averaged together again. I made that mistake and published it before
  catching it the same day.
- **Correction duty executed**, not just declared: the word "untuned"
  removed from README and from the TW repo's `shadow_signal_tw.py`
  docstring. Frozen result documents keep their wording and are covered
  by the correction file.

## 2026-07-26 (iteration 13, autonomous) — tracks alive, external evidence recorded, no new writes

- **All three forward tracks alive.** Crypto
  `data/runtime/shadow_trial88.jsonl` last row date 2026-07-25 recorded
  2026-07-26T00:20:06Z (daily 08:20 local) with `WINDOWS_ON_0_OF_4` for
  BTCUSDT and `WINDOWS_ON_1_OF_4` for ETHUSDT, exposure 0/0.25 —
  ensemble ran, ETH held a single window's long. TW repo
  `shadow_tw0050.jsonl` last row 2026-07-24 recorded 2026-07-25T18:09Z,
  exposure 0.25; `shadow_gld.jsonl` last row 2026-07-23 recorded
  2026-07-25T20:19Z, exposure 0. Both are ahead of today's Saturday
  09:40 schedule tick; healthy, no fix needed.
- **Web research pass (five dated lines)** appended to `RESEARCH_LOG.md`
  under `## 2026-07-26 (iteration 13)`. Two of the five directly harden
  the sleeve programme:
  1. Man Group "Cash (Equities) Is King" — directional univariate
     sector trend keeps ~0.81 rolling-24m correlation to equity-index
     trend over 21 years; cross-sectional trend is the diversifier,
     not univariate. Reads onto our three univariate sleeves as a
     warning against assuming a fourth is independent.
  2. arXiv 2510.23150 "When Diversification Hides Redundancy" —
     principal-components decomposition of multi-market trend books
     shows effective-N materially below nominal N. Points at a
     read-only diagnostic on our recorded sleeve returns.
- **Queue action taken: none of P1/P2/P3 required a write this
  iteration.** P1 was verified alive (above). P2 needs a fourth sleeve's
  market pre-checked against buy-and-hold **before** pre-registration;
  the standing goalpost-drift guard says an iteration that reads
  results does not write the next pre-registration. P3 remains refused.
  No code, no configs, no new pre-registration touched.
- **Next-iteration candidate (recorded, not committed to)**: read-only
  PCA / effective-N diagnostic on the three-sleeve daily return series
  (crypto trial 88 curve, TW trial 23 curve, TW trial 24 curve) to put
  a number on the arXiv 2510.23150 claim as it applies to this book.
  Belongs alongside `analyze_idle_capital.py`, does not use holdout,
  does not add a family, does not require a pre-registration.
- **Verify (rule 7, bare)**: `ruff check` all-clear; `ruff format
  --check` 125 files already formatted; `lint-imports` 13 contracts
  kept / 0 broken; `mypy --strict src/` 58 files, no issues;
  `pytest -m "not network"` 378 passed. Tree left green.

## 2026-07-27 — iteration 14 (loop, self-paced)

- **P1 checked first: all three tracks healthy.** Crypto shadow last ran
  2026-07-26 08:20 (result 0), track at 2 rows through 2026-07-25. The
  one-day lag is by design, not a defect: the script records the last
  fully closed daily candle. Next fire 2026-07-27 08:20.
- **Resolved the exp-8 confound.** Yesterday's "0 of 8 beat buy-and-hold"
  could not distinguish a collapsing system from an enormous benchmark.
  Measured: exp 8's median arm returned 7.33x and its best 9.39x, while
  the 13-coin benchmark returned **13.53x** — 2.2x the BTC/ETH
  benchmark's 6.05x. The system made real money and still lost.
- **The comparison this program had never made.** Trial 88 returned
  **14.26x**; buying thirteen coins in March 2018 and never looking again
  returned **13.53x**. A 5.4% margin after 133 registered trials.
- **What the search actually bought: drawdown, not return.** 33.05%
  against 86.22%, Sharpe 1.1829 against 0.8469. An 86% drawdown is the
  difference between a position a person holds and one they capitulate
  out of. Same conclusion as the combination results, now measured
  against the strongest naive alternative rather than against other
  systems.
- **Mechanism, not cost drag.** Exp 8 traded 1,516 times against exp 7's
  396 while running *lower* turnover (6.38 against 8.55) — thirteen
  independently-exiting sleeves are rarely all invested at once, and
  buy-and-hold captures every altcoin's full run.
- **Limit recorded against the finding:** the 13-coin universe came from
  a 2026 eligibility screen, so **survivorship is uncontrolled** and the
  13.53x benchmark is flattered by coins that never died.
- Written into `VS_BUY_AND_HOLD_2026-07-26.md` as a dated addendum.
- **Next: P1 stays P1.** No new family. The open scope question is
  whether the BTC/ETH effect is a two-asset phenomenon or a
  large-cap-only one; a fourth sleeve must still clear the buy-and-hold
  gate before being proposed.

## 2026-07-27 — iteration 15 (loop, self-paced)

- Answered the scope question left open by iteration 14. New tool:
  `scripts/analyze_symbol_dispersion.py` (zero registry cost, reads local
  candles only).
- **Per-name buy-and-hold across the 13-coin universe is violently
  skewed**: mean 16.09x, median 3.21x. Top 1 name is 32.9% of summed
  return, top 2 is 54.2%, top 3 is **73.7%** (BNB 68.8x, SOL 44.5x, DOGE
  40.8x). Two names lost money outright. **Every name drew down at least
  76%.**
- **The skew story alone does not survive contact with the data.**
  BTC/ETH is MORE top-heavy by top-1 share (BTC 76.9% of that two-name
  sum vs 32.9%), and the rule won there. Concentration does not separate
  the cases.
- **What does: sleeve count.** On 2 names the rule returned 14.26x —
  more than either constituent's own buy-and-hold (9.86x, 2.96x). On 13
  names the best arm returned 9.39x, below the average constituent. The
  measured cause is already on record: independently-exiting sleeves idle
  their share of the book, and the three-sleeve combination sits in 66.2%
  cash (`CASH_AWARE_ALLOCATION_RESULT.md`). Thirteen idle far more.
- **One mechanism now explains three previously separate results**:
  exp 8's 0-of-8, the combination's 3.94x against 5.42x held, and the
  cash-aware refutation. The rule's advantage shrinks as the number of
  independently-exiting sleeves grows — every sleeve buys drawdown
  reduction with compounding. One trade, not three findings.
- **Testable consequence**: a fourth sleeve should cut return again and
  cut drawdown again, which makes the buy-and-hold gate already in the
  contract the binding question rather than a formality.
- Limits recorded: one window; survivorship uncontrolled (2026
  eligibility screen, dead coins absent, benchmarks flattered); and the
  cross-experiment causal claim is inference, since exp 7 and exp 8
  differ in more than sleeve count.
- Written into `REGISTRY_VS_BENCHMARK_2026-07-26.md` as a dated addendum.
- **Next: P1 unchanged.** No new family. If a fourth sleeve is ever
  proposed, this addendum is the prior it has to beat.

## 2026-07-27 — iteration 16 (loop, self-paced): iteration 15 retracted

- Iteration 15 labelled its own central claim "inference, not
  measurement". This iteration measured it. **It failed.**
- **Deployment, measured from `targets[].cash_weight`:** trial 88
  (2 symbols) mean gross **0.3785**; trial 94 (13 symbols) **0.3011**;
  trial 96 (13 symbols, mid-channel) **0.2631**. The gap is real but only
  ~20% relative — it cannot explain a 3.4x swing in benchmark-relative
  performance. **The sleeve-count synthesis is retracted.**
- **Backup hypothesis also refuted.** "Buy-and-hold wins by letting BNB
  and SOL drift to dominate while the ladder re-snaps to equal budgets"
  predicts drift >> rebalanced. Measured across all 13: drift **16.09x**,
  daily-rebalanced equal weight **17.51x**. A wash.
- **A bug was caught before publication.** The first rebalancing
  computation returned 176.27x against a constituent mean of 16.09x.
  Implausible on its face; the loop double-counted cash for unlisted
  names. Rewritten with a sanity check on the six full-history names
  (drift 14.46x, rebalanced 9.04x — sensible) before any number was used.
  **Not reported as a finding at any point.**
- **Corrected reading, simpler and less flattering to the analysis:**
  both books add real timing value over their own exposure. Trial 88
  turned a 6.05x benchmark into 14.26x at 37.9% average exposure; trial
  94 turned a 13.53x benchmark into 9.39x at 30.1%. **Experiment 8 did
  not collapse — its benchmark was 2.2x stronger**, and a
  benchmark-relative test penalises operating in a market that rose more.
- **Methodological consequence for the contract's buy-and-hold gate:** it
  remains the right test for "hold this instead of the asset?", but it is
  NOT a measure of strategy quality across markets. A sleeve can fail the
  gate purely because its market went up a lot. That distinction now
  belongs in any fourth-sleeve pre-registration.
- Second self-retraction in two days, both caught by my own follow-up
  measurement rather than by a reader.
- **Next: P1 unchanged.** No new family.

## 2026-07-27 — iteration 17 (loop, self-paced): the confound-free control

- Iteration 16 identified that "beat buy-and-hold" is confounded by how
  strong the benchmark was. This iteration built the control that removes
  it: `scripts/analyze_timing_value.py` compares each system against a
  **passive twin holding the same asset at the system's own average
  gross exposure** — same time in market, no signal. The twin pays no
  trading costs, so every edge is conservative for the system.

| Book | Expo | System | Twin | Edge | Sys MDD | Twin MDD |
|---|---:|---:|---:|---:|---:|---:|
| crypto t88 (2 sym) | 0.379 | 14.26x | 3.03x | **4.70** | 33.05% | 43.60% |
| crypto t94 (13 sym) | 0.301 | 9.39x | 3.39x | **2.77** | 51.54% | 36.73% |
| taiwan t23 | 0.477 | 2.15x | 2.95x | **0.73** | 30.85% | 30.96% |
| gold t24 | 0.419 | 2.44x | 2.44x | **1.00** | 25.01% | 21.17% |

- **Crypto timing works, in both universes.** 4.70x and 2.77x the twin.
  This **vindicates experiment 8**: it did not fail, it beat its
  exposure-matched twin and only lost the raw comparison because its
  market rose 2.2x more. Iteration 16's correction is confirmed by a
  proper control rather than by argument.
- **Asymmetry not in the system's favour**: on BTC/ETH timing improved
  return AND drawdown; on 13 symbols it improved return but **worsened**
  drawdown (51.54% against 36.73%).
- **Taiwan: timing destroyed value.** 0.73x, at the same drawdown.
  Strictly dominated by holding 47.7% of 0050 continuously.
- **Gold: timing did exactly nothing.** 1.00x, and the twin's drawdown is
  LOWER (21.17% against 25.01%). The sleeve's signal machinery is
  overhead.
- **Consequence for the combination:** it is not one rule working in
  three markets. It is one market where timing works plus two legs
  equivalent to or worse than static partial positions.
- **Free testable prediction, and it is the next step**: replace the gold
  and Taiwan sleeves with static 41.9% GLD and 47.7% 0050 holdings. If
  the three-sleeve result holds or improves, the diversification benefit
  was never about trend-following in those markets — it was about holding
  partially uncorrelated assets, which needs no signal.
- Written up in `TIMING_VALUE_2026-07-27.md`.
- **Next: run that substitution test.** P1 unchanged.

## 2026-07-27 — iteration 18 (loop, first under the step-0 convergence check)

- **Step 0 recorded.** Current answer: timing works in crypto only
  (4.70x/2.77x vs exposure-matched twin), nothing in Taiwan (0.73x) or
  gold (1.00x); best book 14.26x against 13.53x for holding thirteen
  coins, so the search bought drawdown not return; no forward evidence.
  This iteration moves: whether the non-crypto sleeves need their signal
  at all. Not sprawl: closes a route, no new script (extended
  `analyze_sleeve_combination`), no new document (addendum).
- **Prediction from iteration 17 was REFUTED by its own test.** It said
  substituting static holdings "should produce the same or better"
  three-sleeve result. Measured: Sharpe **1.3870 vs 1.4108**, drawdown
  **16.74% vs 14.90%**, multiple **3.74x vs 3.94x**. Worse on all three.
- **The test was biased against the signal and the signal still won**:
  static twins pay no trading costs, the sleeves pay full costs.
- **Both results are true at once.** A sleeve can be worthless standalone
  (Taiwan 0.73x) and still contribute to a book, because a static holding
  is exposed all the time while a trend sleeve is **flat at moments
  uncorrelated with crypto's drawdowns**. That is exactly the mechanism
  `CROSSMARKET_COMBINATION_RESULT.md` named. Static exposure cannot
  reproduce it by construction.
- **Honest size: small.** Sharpe +1.7%, drawdown -11%, wealth +5% against
  the static substitute.
- **Route closed**: "replace the non-crypto sleeves with static holdings"
  is worse; the sleeves stay as systems. Recorded in the contract's
  standing answer so it is not proposed again.
- **Standing answer restated (refined, not overturned):** timing value in
  crypto only, the search bought drawdown rather than return, nothing is
  forward-validated — **and standalone timing value is not the same
  quantity as portfolio timing value**, which this program had been
  conflating.

## 2026-07-27 — iteration 19 (loop, step-0 check passed)

- **Step 0.** Current answer unchanged going in. This iteration moves:
  whether the program's ONLY positive finding (crypto timing edge 4.70x)
  is a stable effect or an artifact of one or two crash episodes. Not
  sprawl: no new script (extended `analyze_timing_value`), no new
  document (addendum), and it attacks the central clause of the standing
  answer.
- **Split uses the four windows already declared** in
  `analyze_sleeve_combination.print_stress`, reused verbatim so the split
  could not be chosen after seeing results.
- **Trial 88 (BTC/ETH): edge > 1 in all four windows** — covid 1.14,
  2022 bear 1.14, 2018-2019 1.91, 2023-2025H1 1.10. Bull, bear, crash and
  mixed. **Not a single-episode artifact.** This is the strongest
  statement this program has made about any finding.
- **Trial 94 (13 symbols): fails both bear windows** — covid 0.98, 2022
  **0.90**, 2018-2019 1.21, 2023-2025H1 1.29. Its whole-window 2.77x is
  regime-dependent: it earns in rising markets and loses to a static
  position in falling ones, which is the opposite of what a trend system
  is for.
- **Gap stated plainly:** the four windows cover 2,005 of 2,676 days
  (74.9%). They do not tile the sample — roughly 671 days from 2020-04 to
  2021-12 are excluded, and that is the largest bull run in it. The
  sub-period edges therefore do not multiply to 4.70x. Extending the
  split would mean picking boundaries after seeing results, which this
  program refuses.
- **Standing answer restated, now with a robustness clause:** timing
  works in crypto only; on BTC/ETH that edge is **positive in all four
  pre-declared sub-periods**, on 13 symbols it is not; the search bought
  drawdown rather than return; standalone and portfolio timing value are
  different quantities; **nothing is forward-validated.**

## 2026-07-27 — iteration 20 (loop, step-0 check passed)

- **Step 0.** Moves the biggest remaining doubt about the only positive
  finding: trial 88 is the MAXIMUM of its 8-member family and PBO is
  0.7411, but the exposure-matched twin had only ever been run on the
  winner. Not sprawl: **zero code change** (`--report` already existed),
  no new script, no new document.
- **Eight of eight family members beat their exposure-matched twin.**
  Edges 3.88 / 4.17 / **4.70 (trial 88)** / 4.15 / 3.84 / 4.16 / 4.08 /
  3.95. Range 3.84-4.70, median **4.115**. The family FLOOR beats its
  twin by 3.84x.
- **Trial 88's selection premium is +14.2%** over a randomly-drawn family
  member. **Selection chose the edge's size, not its existence.**
- **Regime robustness is not unique to the winner either.** Non-winners
  86 and 93, same pre-declared windows: 1.09/1.08/1.89/1.06 and
  1.06/1.37/1.71/1.03 — both positive in all four.
- **Stated against the finding:** the eight are NOT eight independent
  tests. They are a 2x2x2 grid (window set x exit x gate) on the same two
  assets over the same window. "Eight of eight" means no parameter choice
  inside that grid destroys the edge, not that it survived eight separate
  chances to fail. **PBO 0.7411 was measured across distinct
  architectures on Sharpe rankings and remains unanswered.**
- **Method note:** the first run printed correct numbers while returning
  exit code 255. Rerun bare it exits 0 — PowerShell's `Select-Object
  -First` closed the pipe. Numbers were used only after that check. This
  project has been bitten twice by pipes masking exit codes.
- **Standing answer restated:** timing works in crypto only; on BTC/ETH
  the edge is positive in all four pre-declared sub-periods AND all eight
  family members, with a selection premium of only +14.2%; on 13 symbols
  it fails both bear windows; the search bought drawdown rather than
  return; standalone and portfolio timing value differ; **nothing is
  forward-validated and PBO remains unanswered.**

## 2026-07-27 — iteration 21 (loop, step-0 check passed)

- **Step 0.** PBO was the last analytically-addressable item in the
  standing answer. Not sprawl: zero code change (`--representatives`
  already takes an arbitrary trial list), no new script, no new document.
- **PBO per family, eight columns each** — it is NOT degenerate, it
  ranges over 15x:

| Family | PBO |
|---|---:|
| exp-7 donchian BTC/ETH | **0.7415** |
| exp-8 donchian-13 | 0.6830 |
| exp-3 cs-momentum | 0.2789 |
| exp-5 regime gate | **0.0482** |

- **It runs opposite to measured quality.** exp-7's eight members score
  3.84-4.70 against exposure-matched twins — all positive, tightly
  clustered. A four-member sample of exp-5 scores 3.70 / 5.96 / 2.31 /
  1.85 — also all positive, spread 3.2x.
- **Both families have a real edge in every member measured; their PBOs
  differ by 15x.** The separator is dispersion: near-identical members
  make the in-sample best a near coin flip out of sample (high PBO);
  dispersed members make ranking stable (low PBO).
- **So PBO answers "can I trust that I picked the best member?" and says
  nothing about whether the family has an edge.** Used as a gate on edge
  existence it penalises parameter-robust families and rewards
  parameter-sensitive ones. The weakest family by this program's own
  buy-and-hold table is the only one that would PASS gate 3.
- **Self-correction inside the iteration:** exp-5 was picked as a "known
  weak" control from its buy-and-hold ratio. On the exposure-matched
  metric it is not weak. That is the exact confound iteration 17
  identified, biting again in the same session. Recorded rather than
  quietly fixed.
- **Untested, stated:** only 4 of exp-5's 8 members measured on the twin
  metric; exp-3's twin edges not measured at all.
- **Standing answer restated, with PBO now interpreted rather than
  outstanding:** timing works in crypto only; the BTC/ETH edge is
  positive in all four pre-declared sub-periods and all eight family
  members with a +14.2% selection premium; the search bought drawdown
  rather than return; **PBO 0.7415 for that family reflects members being
  indistinguishable, not absence of edge**; **nothing is
  forward-validated**, which is now the only unresolved item.

## 2026-07-27 — iteration 22 (loop, step-0 check passed)

- **Step 0.** Iteration 21 published "PBO tracks dispersion, not edge" on
  only two families. This iteration measured the other two, which could
  have refuted it. Not sprawl: no new script, no new document, tests a
  claim published one iteration earlier.
- **All four families now measured on the same exposure-matched metric:**

| Family | PBO | Twin edges | Spread | Members with edge |
|---|---:|---|---:|---:|
| exp-7 donchian BTC/ETH | **0.7415** | 3.84-4.70 | 1.22x | **8/8** |
| exp-8 donchian-13 | **0.6830** | 2.33-2.92 | 1.25x | **8/8** |
| exp-3 cs-momentum | 0.2789 | 0.04-20.22 | **505x** | **2/8** |
| exp-5 regime gate | 0.0482 | 1.85-5.96 | 3.2x | 4/4 measured |

- **Grouping confirmed, ranking not.** Both tight families have high PBO
  (0.68, 0.74); both dispersed families have low PBO (0.05, 0.28). But
  exp-3 is 150x more dispersed than exp-5 and still scores higher PBO, so
  dispersion explains the split and not the order. n = 4.
- **Sharpest form of the finding:** the two families where EVERY measured
  member has a real exposure-adjusted edge are the two with the WORST
  PBO. The family where only 2 of 8 members have any edge scores BETTER
  than both. **Gate 3 would rank exp-3 as safer than exp-7.**
- **exp-8 clarification:** all 8 members are positive whole-window
  (2.33-2.92) even though iteration 19 found it fails both bear
  sub-windows. Both are true and neither was retracted.
- **My own bug, recorded:** the first exp-8 run exited 1 because a
  PowerShell format string emitted `trial-0000100` instead of
  `trial-000100`. Caught by the exit code, fixed, rerun to exit 0 before
  any number was used.
- **Standing answer unchanged.** Forward validation remains the only
  unresolved item, and it needs time rather than analysis.

## 2026-07-27 — iteration 23 (loop): analytical routes exhausted

- **Step 0 returned "nothing to do", and that is the finding.** Every
  remaining lever is structurally blocked: forward validation needs time,
  the October holdout is operator-only, a new parameter family is refused
  by P3, revising gate 3 after discovering it misranks would be changing
  the rules after seeing results, and further diagnostics would not move
  the standing answer.
- **P1 verified, all three tracks healthy:**
  - `CryptoShadowTrial88` last ran 2026-07-26 08:20:01 result 0, next
    2026-07-27 08:20. Track at 2 rows through 2026-07-25 (one-day lag by
    design — it records the last CLOSED daily candle).
  - `TwShadow0050` shows last=1999-11-30 result=267011, which is
    `SCHED_S_TASK_HAS_NOT_RUN`, not a failure: it was registered on a
    Sunday and its first Saturday is 2026-08-01. 0050 at 1 row, GLD at 1
    row, both written by the manual runs that created them.
  - `CryptoResearchLoop` last ran 2026-07-26 21:37:01 result 0.
- **Contract updated** with a "when the analytical routes are exhausted"
  section, so a fresh-context iteration does not restart the diagnostic
  treadmill. It names the three states that would unblock the work: ~90
  days of forward rows, the October holdout spend, or an operator
  override of P3.
- **Standing answer unchanged**, and this iteration deliberately did not
  try to change it.

## 2026-07-27 — iteration 24 (loop, exhausted state, P1 maintenance)

- **Step 0.** Current answer unchanged from iteration 23 (see standing
  answer). What this iteration moves: nothing analytical — it confirms
  the three forward tracks are still gaining rows and adds two dated
  research-log entries whose only purpose is a calendar anchor for when
  the shadow tracks can first speak. Why not sprawl: **zero new
  scripts, zero new research documents, zero new pre-registrations, and
  no attempt to invent an experiment.** The contract's "when the
  analytical routes are exhausted" clause governs, and its instruction
  is "do P1 maintenance, confirm the three tracks are gaining rows, and
  stop."
- **P1 status, all three tracks:**
  - `CryptoShadowTrial88` — last 2026-07-27 08:20:01 result 0, next
    2026-07-28 08:20. `shadow_trial88.jsonl` at **3 rows** (up from 2 at
    iteration 23), most recent row `date=2026-07-26 close BTC 65399.99
    ETH 1954.72 equity 1006.230318 exposure BTC 0 / ETH 0.5`. New row
    written 2026-07-27 00:20:06 UTC. Track is healthy.
  - `TwShadow0050` — last=1999-11-30 result=267011
    (`SCHED_S_TASK_HAS_NOT_RUN`, per iteration 23 analysis), next
    2026-08-01 09:40 (Saturday). `shadow_tw0050.jsonl` still at 1 row
    and `shadow_gld.jsonl` still at 1 row, both from the manual seeds.
    First scheduled fire has not arrived; nothing to fix.
  - `CryptoResearchLoop` — currently Running (this iteration), previous
    run 2026-07-27 21:37:01 result 0, next 2026-07-28 21:37. Healthy.
- **Web research (contract step 2).** Two dated entries appended to
  `RESEARCH_LOG.md`:
  1. Coin Bureau's 2-4 weeks paper-trading threshold — places a first
     honest read on the shadow tracks no earlier than 2026-08-07, real
     read closer to 2026-08-21.
  2. Multiple aggregator repostings of a 55-day Donchian mid-line
     filter raising BTC daily long-signal win rate ~50% to ~55% — a
     prior consistent with trial 88's mechanism, not testable-here as
     a new experiment (P3 refuses).
- **What was deliberately NOT done, and why:**
  - Did not run any `analyze_*` script — every one would only refine
    an existing document, and Step 0 forbids that.
  - Did not open a new pre-registration — no sleeve candidate has
    passed the P2 buy-and-hold pre-gate on paper, so a pre-reg would
    be premature and would cost an N.
  - Did not touch `configs/runtime/`, the trial registry, or any frozen
    pre-registration.
  - Did not attempt to move the standing answer — it can only be moved
    by data that does not exist yet (~90 days of forward rows, or the
    October holdout, or an operator override of P3).
- **Standing answer restated, unchanged:** timing works in crypto only;
  BTC/ETH edge positive in all four pre-declared sub-periods and all
  eight family members with +14.2% selection premium; PBO 0.7415 for
  that family reflects members being indistinguishable rather than
  absence of edge; on 13 symbols the same edge fails both bear windows;
  the search bought drawdown rather than return; **nothing is
  forward-validated**, and forward validation remains the only
  unresolved item — it needs time rather than analysis.

## 2026-07-28 — iteration 25 (loop, exhausted state broken by a correction)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 24. What this iteration moves: it closes a real hole —
  **the forward tracks were recording with no rule for how they would
  be read** — and, in writing that rule, it found and corrected a
  wrong number in the contract's own roadmap. Why not sprawl: **zero
  new scripts** (all computation done inline against durable return
  series), **one new document, which is a pre-registration and
  therefore records a decision**, and two in-place corrections rather
  than new documents.
- **The hole.** Every queue revision since 2026-07-24 says "keep the
  three forward tracks recording" and "forward evidence is the binding
  constraint". Searching `docs/research/*PRE*` and `docs/contracts/`
  found **no document stating how the tracks would be read**. Reading
  forward data without a pre-declared rule is the exact failure the six
  gates exist to prevent. Written today at **4 rows**, so the data
  cannot have shaped the rule; every day of delay would have made that
  less true.
- **The correction, which is the substantive finding.** The contract
  asserted ~90 days of forward rows would be "enough to say anything at
  all". Measured with MinTRL (Bailey & Lopez de Prado, the same
  machinery as the gate-4 DSR) on the shadowed trials' own durable
  return series:

  | Trial | n | SR_ann | skew | kurtosis | MinTRL 90% | MinTRL 95% |
  |---:|---:|---:|---:|---:|---:|---:|
  | 88 | 2676 | 1.1823 | +0.227 | 12.775 | 429 d (2027-09-26) | **706 d (2028-06-29)** |
  | 118 | 2676 | 1.2413 | +0.157 | 12.980 | 391 d (2027-08-19) | **644 d (2028-04-28)** |

  Forward Sharpe standard error: **N=90 -> 2.016 annualized, 95%
  interval [-2.77, +5.13]**; N=365 -> 1.001, [-0.78, +3.14]. At the
  90-day mark the track cannot distinguish Sharpe -2.7 from +5.1. The
  contract was wrong by roughly a factor of eight and is corrected in
  place.
- **Method self-correction inside the iteration.** The first pass
  annualized with 252 and produced 706 days = 2.80 years. Checking
  against the registry's own recorded `annualized_sharpe` of 1.182061
  showed the program annualizes with **365** (crypto trades every day):
  0.06188 * sqrt(365) = 1.1823, exact match. Redone; 706 days is
  **1.93 years**, not 2.80. The 252 numbers appear in no document.
- **The rule now frozen** (`FORWARD_TRACK_READ_PREREGISTRATION.md`):
  read dates 2026-10-22 / 2027-01-24 / 2027-07-24 / 2028-06-29, none
  movable earlier; **Test 1 implementation agreement** (deterministic,
  full power at any N, and the only thing the 90-day read can settle);
  **Test 2 drawdown breach** as one-sided refutation against the
  recorded 33.05% / 33.24% backtest maxima, with non-breach declared in
  advance as uninformative; **Test 3 return**, refutation permitted but
  **confirmation forbidden until 2028-06-29**. No metric may be added at
  read time.
- **P1 status, all tracks healthy:**
  - `CryptoShadowTrial88` — last 2026-07-28 08:20:01 result 0, next
    2026-07-29 08:20. `shadow_trial88.jsonl` **4 rows** (up from 3),
    latest `date=2026-07-27 close BTC 63755.86 ETH 1892.53 equity
    998.2269 exposure BTC 0 / ETH 0.25`. `shadow_trial118.jsonl` also
    4 rows, equity 1002.9011, exposure 0.5 / 0.5.
  - `TwShadow0050` — next 2026-08-01 09:40, first scheduled fire still
    ahead; `shadow_tw0050.jsonl` and `shadow_gld.jsonl` at 1 row each
    from the manual seeds, as expected. Nothing to fix.
  - `CryptoResearchLoop` — previous run 2026-07-27 21:37:01 result 0,
    next 2026-07-28 21:37. Healthy.
- **What this does NOT do:** no trial registered, no backtest run, no
  holdout touched, no `configs/runtime/` touched, no new family
  proposed, no frozen pre-registration edited, no recorded verdict
  changed.
- **Standing answer, updated:** timing works in crypto only; the BTC/ETH
  edge is positive in all four pre-declared sub-periods and all eight
  family members; the search bought drawdown rather than return;
  nothing is forward-validated — **and the date at which forward
  validation could first return a positive verdict is 2028-06-29, not
  October 2026.** The 2026-10-22 read tests implementation only. The
  operator's levers to move that date are: accept 90% confidence
  (2027-09-26), accept the October holdout as a different question, or
  override P3 to search for a higher-Sharpe design, since MinTRL falls
  with the square of the Sharpe.

## 2026-07-28 — iteration 26 (loop, gate-4 fragility measured)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 25. What this iteration moves: it audits the program's
  single claimed achievement — trial 118's gate-4 pass at DSR 0.950140,
  margin 0.00014 — and converts "thin margin" from an adjective into a
  count. Why not sprawl: **zero new scripts** (imported the program's
  own `deflated_sharpe_ratio` and `non_annualized_sharpe_variance`
  rather than reimplementing), one new document that records a forced
  operator decision and two closed routes, one in-place contract
  refinement.
- **Two dishonesty hypotheses tested FIRST, both refuted.** Neither
  finding was allowed to rest on the margin until the margin was shown
  to be honest.
  - **H1: unregistered arms inflate the true N.** Refuted. Registry by
    experiment: exp-1 1, exp-2..exp-6 16 each, exp-7..exp-10 8 each, 20
    unlabelled early rows = 133. `LOOP_LOG.md:126` says "64 **registered**
    cs-momentum arms" = exp-3..exp-6 at 16 apiece, exactly. Both
    robustness batteries are registered (trials 102-109, 126-133).
    Nothing evaluated is missing from the count.
  - **H2: the pass is an artefact of trial 118's own battery
    compressing cross-trial variance** — a live suspicion, since that
    was the stated reason a 2026-07-25 advance prediction failed.
    Refuted, and backwards: dropping trial 118's own battery gives
    **0.950514**, dropping both batteries gives **0.951257**, both
    higher than the recorded 0.950140. The N reduction outweighs the
    variance increase. **The pass is honest.**
- **The margin, counted:** N=133 -> 0.950140 PASS; **N=134 -> 0.949969
  FAIL**. Because a 134th row shifts the variance as well as the count,
  the real question is whether *any* 134th trial preserves the pass.
  Sweeping its Sharpe: the surviving window is **[0.709, 1.180]**.

  | 134th trial Sharpe | trial 118 DSR | |
  |---:|---:|---|
  | 0.00 | 0.940088 | FAIL |
  | 0.95 (registry mean 0.9444) | 0.950626 | PASS |
  | 1.1823 (trial 88's own) | 0.949988 | FAIL |
  | 1.2413 (trial 118's own) | 0.949630 | FAIL |
  | 2.00 | 0.937298 | FAIL |

  **Finding something as good as what the program already has would
  destroy the pass.** So would something notably worse. Only a mediocre
  134th trial preserves it.
- **This is not a DSR defect.** More search, and more spread among what
  was searched, legitimately raises the bar. The error was this
  program's: "trial 118 passes gate 4" has been quoted as a durable
  property of trial 118, when it is a property of **a search of 133
  configurations that has stopped**.
- **Consequence, and it is a forced choice for the operator.** The
  standing order is 「沒有找到 edge 不准停」. The standing decision since
  2026-07-25 is "no new families" because "the margin cannot absorb
  one." Those were treated as a pause; measured, they are **mutually
  exclusive**. Keep the pass => the crypto registry is frozen at 133 and
  the search is over, not paused. Keep searching => the pass is forfeit
  the moment anything interesting registers, and gate 4 returns to zero
  risk-compliant passers.
- **Counterweight recorded against our own finding** (contract step 2
  web research): the DSR literature's variable is the number of
  **independent** trials, and a raw backtest count overstates search
  breadth because variations are correlated. This program uses the raw
  count by deliberate choice (`run_gate_report.py:188`). Its rows are
  heavily correlated — mean pairwise 0.628, and 64 of 133 are one
  lineage — so a correlation-adjusted N would be below 133 and would
  give trial 118 more margin. **Recorded as a genuine counterweight and
  as a fix that is refused**: adopting it now is changing a gate input
  after seeing the answer it produces, the same move already refused
  over gate 3, and self-serving in a measurable direction.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no holdout touched, no `configs/runtime/` touched,
  trial 118's recorded pass at N=125 and N=133 not retracted — only
  qualified.
- **Standing answer restated, extended:** timing works in crypto only;
  the BTC/ETH edge is positive in all four pre-declared sub-periods and
  all eight family members; the search bought drawdown rather than
  return; nothing is forward-validated and the earliest possible
  forward verdict is **2028-06-29**; **and the single gate-4 pass holds
  only for a search that has stopped — under the frozen N convention
  the program cannot both keep searching in crypto and keep it.**

## 2026-07-28 — iteration 27 (loop, gate audit + same-day correction of iteration 26)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 26. What this iteration moves: it audits the phrase used in
  nearly every document this program has produced — "six-gate
  anti-overfitting framework" — by asking which gates have ever decided
  anything; and in doing so it found that **iteration 26's own reasoning
  was wrong** and corrected it the same day. Why not sprawl: **zero new
  scripts, zero new documents** — the findings are a dated addendum to
  `GATE4_FRAGILITY_2026-07-28.md` plus two in-place contract
  refinements.
- **Correction to iteration 26, in place.** Iteration 26 said adopting
  correlation-adjusted `effective_N` "would be changing a gate's input
  after seeing the answer it produces" and refused it on that basis.
  **Wrong.** `VALIDATION_GATE_CONTRACT.md` — frozen, written before any
  of these results — mandates it at gate 1 line 44: "`effective_N` for
  DSR should account for correlation between trials ... the method used
  must be recorded alongside the number", and line 75 lists `effective_N`
  as a gate-4 input. So `run_gate_report.py:190` passing
  `trial_count = len(trials)` is a **deviation from the contract**,
  conservative on the N axis, with no method recorded — which also means
  gate 1 is not currently fully satisfied.
- **What is actually post-hoc, and why it was still not computed.** Three
  standard methods exist (ONC, hierarchical, spectral). Proper compliance
  clusters trials into K groups, forms an aggregate Sharpe per cluster,
  and takes the variance across **those K Sharpes** — changing *both*
  gate-4 inputs. The variance across K aggregates can be larger or
  smaller than across 133 individual trials, so **the net effect on trial
  118 is unknown, not favourable.** Choosing a method after seeing the
  0.950140 margin is the move that would void the answer, so it was left
  for the operator to declare first. Meanwhile trial 118's pass stands as
  earned under a bar at least as strict as the contract requires.
- **Gate audit — which gates have ever decided a candidate:**

  | Gate | Ever decided a candidate? |
  |---|---|
  | 1 trial registry | No — precondition, and **not currently satisfied** (no `effective_N` method recorded) |
  | 2 data floor >= 1000 days | **No, and cannot** — all 133 trials share one 2676-day window, so `passes: true` by construction |
  | 3 PBO <= 0.05 | **Yes — rejects everything** (0.6518 candidates, 0.7326 all-columns) |
  | 4 DSR >= 0.95 | **Yes — one passer**, trial 118, on a one-trial margin |
  | 5 single-use holdout | No — never executed, nominations fixed |
  | 6 paper trading >= 3 months | No — `GATE6_BASELINE_2026-07-25.md` checkbox still unchecked |

- **The synthesis, which is the finding.** Gates 5 and 6 lying ahead is
  normal and not a defect. What matters is that the two gates which have
  actually exercised judgement over 133 trials **both have recorded
  defects**: gate 3 misranks (iteration 22 — it would call exp-3 with
  2/8 members having edge safer than exp-7 with 8/8), and gate 4 holds
  only for a stopped search (iteration 26). **No document may describe
  this program as having "survived six gates".** Nothing has: gate 3
  fails, and gates 5 and 6 have not been attempted.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, no holdout touched, no
  `configs/runtime/` touched. The contract deviation is **recorded, not
  fixed** — fixing it requires an operator-declared method.
- **Standing answer restated, extended:** timing works in crypto only;
  the BTC/ETH edge is positive in all four pre-declared sub-periods and
  all eight family members; the search bought drawdown rather than
  return; nothing is forward-validated and the earliest possible forward
  verdict is 2028-06-29; the single gate-4 pass holds only for a stopped
  search; **and the framework that produced all of this has exercised
  exactly two gates, both of which are known to be defective in recorded
  ways.**

## 2026-07-28 — iteration 28 (loop, the standing answer's headline sentence was pooling two universes)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 27. What this iteration moves: it audits the single sentence
  this program restates verbatim every iteration — its convergence
  anchor — and finds it compares experiment 7's result against
  experiment 8's benchmark. Why not sprawl: **zero new scripts, zero new
  documents**; a dated addendum to the existing result document plus two
  in-place contract corrections.
- **The defect.** The standing answer reads: "best book 14.26x against
  13.53x for holding thirteen coins, so the search bought drawdown (33%
  vs 86%), not return." **Trial 88 traded BTC and ETH only.** Verified
  against `VS_BUY_AND_HOLD_2026-07-26.md`:

  | Row | System | Benchmark | System MDD | Benchmark MDD |
  |---|---:|---:|---:|---:|
  | line 14 / 143 — **BTC/ETH buy-and-hold** (same universe) | 14.26x | **6.05x** | 33.05% | **80.99%** |
  | line 145 / 166 — **13-coin equal-weight** (cross universe) | 14.26x | 13.53x | 33.05% | 86.22% |

  The 13.53x / 86.22% pair belongs to experiment 8, whose best arm
  returned 9.39x against it. **This is the identical universe-pooling
  error caught and retracted on 2026-07-26**, when "8 of 16 beat
  buy-and-hold, a coin flip" turned out to be 8/8 and 0/8 once the
  experiment number entered the grouping key.
- **The source document contradicts itself and the standing answer
  inherited the wrong half.** `VS_BUY_AND_HOLD_2026-07-26.md` line 19
  states it correctly — "more than doubles buy-and-hold's return while
  cutting the drawdown from 81% to 33%" — and line 171 states the pooled
  version as a mechanism claim, "the system's product is not return."
- **Corrected, split by the question being asked:**
  - **Does the timing rule add value?** Same-universe only. It bought
    **both**: return **14.26x vs 6.05x (+136%)** and drawdown **33.05%
    vs 80.99%**. **"Not return" is false here**, and unnecessary — the
    exposure-matched twin already scores this sleeve 4.70x independently.
  - **Was 133 trials better than the dumbest alternative?**
    Cross-universe is legitimate for this and is the operator's money
    question: **14.26x vs 13.53x, a 5.4% margin**, at 33.05% vs 86.22%.
    Caveats stay attached — the 13-coin universe is
    survivorship-uncontrolled so 13.53x is flattered, and 5.4% is not a
    margin 133 trials can claim credit for. Even here "not return"
    overstates: **mostly drawdown plus a slim return margin**.
- **Web research (contract step 2)** supplied the standard this convicts
  the sentence against: a benchmark must be **appropriate to the
  portfolio's actual universe** and **specified in advance**. The 13-coin
  benchmark for a BTC/ETH strategy fails both.
- **Note on direction.** This correction makes the program look
  **better** than the record said, so it was held to the stricter
  standard: every number was read from the result document's own tables
  rather than from LOOP_LOG prose, and nothing is retracted — only the
  pairing is.
- **What this does NOT do:** no gate rule modified, no frozen
  pre-registration edited, no measured number changed or retracted, no
  trial registered, no backtest run, no holdout touched, no
  `configs/runtime/` touched.
- **Standing answer restated, corrected:** timing works in crypto only,
  and **in its own universe it bought both return and drawdown (14.26x
  vs 6.05x, 33.05% vs 80.99%)**; against the naive 13-coin alternative
  the margin is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails (exp-8 best arm 9.39x vs 13.53x); nothing is
  forward-validated and the earliest possible forward verdict is
  2028-06-29; the single gate-4 pass holds only for a stopped search;
  and the framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 29 (loop, audited the headline metric; it survives)

- **Step 0.** Current answer entering the iteration: as corrected in
  iteration 28. What this iteration moves: it closes two open attacks on
  the **exposure-matched twin**, the metric that replaced the discredited
  buy-and-hold comparison on 2026-07-27 and became the headline number
  ("4.70x") within a single iteration without ever being audited itself.
  Why not sprawl: **zero new scripts, zero new documents** — one dated
  addendum to the existing metric document.
- **Attack 1 — volatility drag.** The twin is built as `w *
  benchmark_return` compounded (`analyze_timing_value.py:139`), i.e. a
  continuously-rebalanced constant mix, which carries a drag the system
  does not. **Refuted.** `log(1 + w*r) > w * log(1 + r)` for both signs
  of r, so partial exposure suffers *less* drag than the asset it tracks
  — the twin is a harder benchmark, not an easier one. Quantified against
  the alternative construction (buy w once, never rebalance, cash
  remainder):

  | Twin construction | Twin multiple | Edge |
  |---|---:|---:|
  | constant-mix, daily rebalanced (**as used**) | 3.03x | **4.71** |
  | un-rebalanced fraction | 2.9121x | 4.90 |

  **4.1% apart, and the one in use is the more conservative.** The
  headline is not a rebalancing artefact.
- **Attack 2 — is it asset selection, not timing?** The twin matches
  time-in-market but not asset mix, and BTC returned 9.86x against the
  equal-weight benchmark's 6.05x, so a rule that merely favoured BTC
  would masquerade as timing value. **Refuted decisively.** Mean
  per-symbol target weight over all 2,677 decision days, from
  `trial-000088/report.json`: **BTC 0.2006, ETH 0.1780** — total 0.3785,
  reproducing the recorded mean exposure 0.379 exactly, and a **53/47
  split against a 50/50 benchmark**. A three percentage point tilt cannot
  produce a 4.70x edge.
- **Route closed.** The twin metric survives audit on both the
  construction it uses and the composition it ignores. Neither question
  may be re-opened without new evidence. Limits unchanged and still
  attached: the twin pays no trading costs while the system pays full
  ones; the twin has no drawdown control (43.60% against 33.05%); and
  none of it is forward evidence.
- **Honest note on iteration value.** This iteration produced no new
  claim — it removed two ways the existing claim could have been wrong.
  That is the intended outcome of an audit, and it is recorded as such
  rather than dressed up as a discovery.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` touched.
- **Standing answer restated, unchanged from iteration 28:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%), **now with the 4.70x twin edge
  audited and robust to +-4% on twin construction and to asset mix**;
  against the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated and the earliest permitted forward verdict is
  2028-06-29; the single gate-4 pass holds only for a stopped search; and
  the framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 30 (loop, look-ahead ruled out; execution latency found unmodelled)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 29. What this iteration moves: five audits had not touched
  the most consequential correctness question in any backtest —
  **look-ahead between signal and fill**. It closes that question and, in
  doing so, exposes a quantified assumption nobody had written down. Why
  not sprawl: **zero new scripts, zero new documents** — one dated
  addendum to the gate-6 document, which is where execution realism
  belongs.
- **Look-ahead: ruled out, and verified empirically rather than from
  code intent.** `src/backtest/engine.py` carries
  `generated_at_bar_close` and `executable_from_next_bar` and executes at
  the next bar's `open_price`. Traced end to end on trial 88's first
  trade: signal `as_of` 2018-03-04T23:59:59.999Z, order `accepted_at`
  2018-03-05T00:00:00Z, fill price **11520.76**. Source candles give
  2018-03-04 close **11515.00** and 2018-03-05 open **11515.00**, and
  `11515.00 x 1.0005 = 11520.7575` — the next bar's open plus exactly the
  modelled 5 bps. **The decision uses nothing after its own bar close.
  Route closed.**
- **The gap the acquittal exposes.** Because crypto is continuous,
  `open[t+1] == close[t]`, so the one-bar lag gives **no price
  protection** — the system fills at the price it decided on. That
  encodes **zero decision-to-execution latency**. The live system is not
  instantaneous: paper runtime 08:05 Taipei = **~5 min** after the 00:00
  UTC bar close; shadow recorder 08:20 Taipei = **~20 min** (confirmed
  from `recorded_at` 2026-07-28T00:20:07Z against `date` 2026-07-27).
- **Quantified.** BTC daily sigma over the backtest window
  (2018-03-05..2025-07-01, n=2675) is **3.4068%**. Scaled by sqrt(t):

  | Horizon | E abs move | vs modelled 5 bps |
  |---|---:|---:|
  | 5 min (runtime) | **16.0 bps** | **3.2x** |
  | 20 min (shadow) | **32.0 bps** | **6.4x** |
  | 60 min | 55.5 bps | 11.1x |

- **Stated honestly, with its limit.** This is **dispersion, not cost** —
  a delay is symmetric in expectation unless the signal correlates with
  the move that follows. The adverse fraction **cannot be measured from
  daily candles**, so no cost number is claimed. But trial 88 is a
  breakout rule, firing exactly when a level has just broken, and the
  transaction-cost literature names breakout and momentum systems as the
  case where delay cost is directional against you. The trial-118
  robustness battery held at 3x cost (~60 bps round-trip); a
  half-adverse 20-minute gap would add ~32 bps round-trip on top,
  pushing toward the edge of what was tested. **The cost model's headroom
  is smaller than the 3x stress suggests, by an amount this program
  cannot currently measure.**
- **This is gate 6's declared job and gate 6 has not run.** Its contract
  requires measuring "notification->execution delay (simulated or
  journaled)"; its "paper period >= 3 months" checkbox is still
  unchecked. This converts a checklist line into a quantified reason to
  run it.
- **Closing it is an operator decision, not a loop action.** Either
  ingest 1m/5m candles and measure the signed drift conditioned on a
  signal firing, or add a bar-close-price and execution-price field to
  the shadow tracks. The second touches a live recording track, so it is
  the operator's call — and if done **now** rather than at a read it
  strengthens Test 1 of `FORWARD_TRACK_READ_PREREGISTRATION.md` instead
  of adding a read-time metric.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` or shadow script touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown (14.26x vs 6.05x,
  33.05% vs 80.99%), with the 4.70x twin edge audited and robust;
  **the engine is free of look-ahead, verified to the cent**; but the
  backtest assumes zero execution latency while the live system runs 5 to
  20 minutes late, a window whose price dispersion is 3 to 6 times the
  modelled slippage and whose adverse component is unmeasured; against
  the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated before 2028-06-29; the single gate-4 pass holds only
  for a stopped search; and the framework has exercised exactly two
  gates, both defective.

## 2026-07-28 — iteration 31 (loop, measured the delay cost iteration 30 called unmeasurable)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 30. What this iteration moves: iteration 30 left the
  execution-latency question as a bound and declared the adverse
  component "unmeasurable from daily candles". **That was wrong**, and
  this iteration measures it. Why not sprawl: **zero new scripts, zero
  new documents** — one dated addendum to the same gate-6 document, using
  data already on disk.
- **The test.** Daily candles carry one usable signal about intraday
  direction: where the **open** sits inside that day's high-low range. If
  price rose after the open, the open sits low in the range, and a
  delayed BUY pays more. All 669 fills were matched to their
  execution-day candle:

  | Group | n | mean open-in-range | delta vs baseline | t | implied drift |
  |---|---:|---:|---:|---:|---:|
  | BUY fill days | 331 | 0.4910 | **-0.0167** | **-0.99** | **-8.8 bps** |
  | SELL fill days | 338 | 0.5038 | -0.0040 | -0.25 | -2.4 bps |
  | all days baseline | 6484 | 0.5077 | — | — | — |

- **Result: the predicted signature is there on buys, and it is not
  significant.** BUY-day opens sit 1.67pp lower in range than typical —
  the breakout continuation signature — at **t = -0.99**. And **SELL days
  lean the favourable way**: an open low in the range means a delayed
  sell gets a *better* price, worth +2.4 bps. **Net round-trip point
  estimate about -6.4 bps**, against 10 bps of modelled round-trip
  slippage and ~40 bps of headroom the trial-118 battery demonstrated at
  3x cost. **Inside what was already stress-tested.**
- **Second correction to iteration 30.** Its sqrt(t) scaling assumed
  uniform intraday volatility. Crypto volatility peaks at **14:00-16:00
  UTC** and declines after **20:00 UTC**; the execution window is
  **00:00-00:20 UTC**, the quiet part of the day. So the 16 bps and
  32 bps dispersion figures are **overestimates**, not neutral scalings.
- **What this does not establish, stated plainly.** With sd 0.3070 and
  n=331 the 95% detectable deviation for buys is **~17.4 bps**, so this
  rules out adverse drifts larger than that and **cannot resolve the
  measured -8.8 bps from zero**. And open-in-range describes a 24-hour
  bar, not the first 5-20 minutes — it is evidence about direction, not a
  substitute for intraday data. **The concern is narrowed to "under 17
  bps and probably much less", not closed.**
- **Method note against self-flattery.** This iteration's result makes
  the program look better than iteration 30 implied, so the limits above
  are stated in the same breath as the numbers, and the "narrowed, not
  closed" verdict is the one that goes into the standing answer.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` or shadow script touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown (14.26x vs 6.05x,
  33.05% vs 80.99%), with the 4.70x twin edge audited and robust; the
  engine is free of look-ahead, verified to the cent; **the execution-
  latency gap iteration 30 raised is now measured at about -6.4 bps
  round-trip point estimate, bounded above by ~17 bps, and inside the
  cost headroom already stress-tested** — narrowed, not closed, and gate
  6 remains the way to close it; against the naive 13-coin alternative
  the margin is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; nothing is forward-validated before 2028-06-29;
  the single gate-4 pass holds only for a stopped search; and the
  framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 32 (loop, holdout integrity verified; one hazard found)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 31. What this iteration moves: seven audits had not touched
  **gate 5**, and the October holdout is the one clean evidence this
  program has reserved. If it were already contaminated it would be
  worthless before being spent, and nobody had checked. Why not sprawl:
  **zero new scripts**; one new document, justified because it records a
  verification the operator needs before spending the holdout and has no
  existing home (`PRE_HOLDOUT_PROTOCOL.md` is frozen and was not edited).
- **Verified clean at the trial level.** `data/candles` runs to
  2026-07-02 (3242 rows); `data/candles_preholdout` stops at 2025-07-01
  (2876 rows), exactly one day before `holdout_start`
  2025-07-02T23:59:59.999Z. The decisive check is the registry, not
  script intent: **all 133 registered trials have `data_end` =
  2025-07-01, and zero cross the boundary.** About 366 days of holdout
  exist to spend and `spent` is still `false`. **Gate 5 is intact as
  written.**
- **Hazard: the lock is convention, not mechanism.** All ten
  trial-registering scripts (`run_alloc_family`, `run_atr_family`,
  `run_combo_family`, `run_cs_family`, `run_donchian13_family`,
  `run_donchian_family`, `run_gate_family`, `run_robustness_trial88`,
  `run_robustness_trial118`, `run_trendfactor_family`) default to
  `data/candles_preholdout` — but nothing *prevents* passing
  `--candles-dir data/candles`. The guarantee rests on ten argparse
  defaults staying correct, not on the engine refusing to read past
  `holdout_start`.
- **Soft contamination found and recorded before October, not after.**
  `analyze_symbol_dispersion.py:30` and `analyze_whipsaw.py:129` default
  to the **full** series, and `WHIPSAW_DIAGNOSTIC.md:84` documents a run
  over candles spanning 2024-01 to 2026-06 — crossing the boundary. That
  diagnostic's verdict placed the hysteresis experiment first in Goal P.
  **This is not a gate-5 violation** (gate 5 binds trials, and no trial
  read it), but the adaptive-data-analysis literature is explicit that a
  researcher merely *considering* a result computed on reserved data
  creates a formal dependency the classical theory does not cover.
- **Magnitude, not minimised.** The whipsaw statistic is signal churn
  frequency, **not** strategy P&L, so it cannot reveal whether trial 88
  or 118 made money after 2025-07-01 and cannot have tuned them toward
  holdout returns. What it could do — and did — is nudge **research
  priority**. Weak channel, real channel, and it belongs on the record
  now rather than surfacing after the October result, when it would read
  as an excuse.
- **Three operator decisions named:** carry this caveat into the October
  result document; optionally make the lock mechanical (engine refuses
  `open_time >= holdout_start` without an explicit `--spend-holdout`);
  and repoint the two diagnostics at `candles_preholdout` by default,
  which costs nothing and closes the channel for future work.
- **What this does NOT do:** the holdout was **not read** — only
  `holdout_lock.json` metadata, row counts and date boundaries were
  inspected. No gate rule modified, no frozen contract edited, no trial
  registered, no backtest run, nominations unchanged, `spent` still
  `false`, no `configs/runtime/` touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown; the 4.70x twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is measured at about -6.4 bps
  round-trip point estimate, bounded above by ~17 bps, inside tested
  headroom; **the October holdout is verified unread by any trial and
  still has ~366 days available, with one soft-contamination channel now
  on the record**; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails; nothing is forward-validated before 2028-06-29; the single
  gate-4 pass holds only for a stopped search; and the framework has
  exercised exactly two gates, both defective.

## 2026-07-28 — iteration 33 (loop, first code change in nine iterations: holdout channel closed)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 32. What this iteration moves: eight consecutive iterations
  produced observations. Iteration 32 found a live hazard and named three
  fixes, one of which is purely protective — and I filed it under
  "operator decides", which on re-reading was **over-cautious**. It
  touches no runtime, no engine, no contract, no registry, and can only
  *reduce* holdout exposure. Why not sprawl: **zero new scripts** — one
  default changed, one test added.
- **Correction to iteration 32, in place.** That entry listed
  `analyze_symbol_dispersion.py` and `analyze_whipsaw.py` together as
  reading the full series. **Wrong for the first.**
  `analyze_symbol_dispersion` defaults `--end` to `_END = date(2025, 7, 1)`
  — exactly the holdout boundary — so it reads `data/candles` but
  truncates before `holdout_start` and was **safe all along**. Only
  `analyze_whipsaw` was genuinely unbounded: it has no date argument, so
  its `--candles-dir` default was the entire exposure.
- **Fix.** `scripts/analyze_whipsaw.py` now defaults to
  `data/candles_preholdout`, with the reason written at the argument.
  `first_month`/`last_month` were already emitted, so a future run that
  widens the window explicitly still records what it read. Locked in by
  `tests/scripts/test_analyze_whipsaw.py::test_default_candles_dir_is_the_preholdout_slice`
  so it cannot regress silently.
- **Verification, run bare.** ruff check 0, ruff format --check 0
  (127 files), mypy --strict 0 (58 source files), lint-imports 0
  (13 contracts kept), **pytest -m "not network": 379 passed**. The
  trailing `PermissionError` in the pytest output is its own Windows
  temp-directory cleanup at interpreter exit, after the run completed —
  not a test failure.
- **What is not undone.** The whipsaw verdict that placed hysteresis
  first in Goal P was formed on a window crossing the boundary. Changing
  the default prevents recurrence; it does not retract history. **That
  caveat still travels to October.**
- **Operator decisions 1 and 2 remain open** — carry the caveat into the
  October result document, and optionally make the lock mechanical in the
  engine. A literature search for programmatic holdout-enforcement
  patterns returned little of substance (mostly LLM guardrail tooling),
  so decision 2 would be a from-scratch design rather than adopting a
  known pattern. Empty search result recorded rather than padded.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read,
  nominations unchanged, `spent` still `false`, no `configs/runtime/`
  and no family runner touched.
- **Standing answer restated, unchanged in substance from iteration 32:**
  timing works in crypto only and in its own universe bought both return
  and drawdown; the 4.70x twin edge is audited and robust; the engine is
  free of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip point estimate, bounded above by ~17 bps,
  inside tested headroom; the October holdout is verified unread by any
  trial with ~366 days available, **its one soft-contamination channel is
  now closed at the source though the historical caveat stands**; against
  the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated before 2028-06-29; the single gate-4 pass holds only
  for a stopped search; and the framework has exercised exactly two
  gates, both defective.

## 2026-07-28 — iteration 34 (loop, iteration 32's central claim retracted)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 33. What this iteration moves: nine audits asked whether the
  holdout is clean; none asked whether the code that **spends** it works.
  October is a one-shot irreversible operation that has never executed.
  Why not sprawl: **zero new scripts, zero new documents** — one dated
  addendum, and it is mostly a retraction of my own earlier work.
- **Hypothesis tested and refuted.** Suspected an irreversible-loss bug:
  if the lock is marked spent **before** the run, a crash burns the
  single-use holdout for nothing. It is not a bug — `spend_holdout`'s
  docstring states the design outright: "The spend is recorded BEFORE the
  qualification run executes: if the run crashes, the holdout stays spent
  (conservative by doctrine)." Deliberate and documented.
- **RETRACTION: iteration 32's central claim was wrong.** That entry said
  "the lock is convention, not mechanism ... the guarantee rests on ten
  defaults staying correct, not on the engine refusing to read past
  `holdout_start`." **False.** `src/backtest/runner.py` — the single
  registered entry point every family runner uses — trims
  unconditionally:

  ```python
  run_candles = {
      symbol_value: tuple(
          candle for candle in candles if candle.close_time < holdout.holdout_start
      )
  ```

  **Passing `--candles-dir data/candles` to a family runner would not
  leak the holdout.** The reason all 133 trials carry `data_end` =
  2025-07-01 is this trim, not luck with argparse. This is exactly the
  framework-level enforcement the leakage literature prescribes —
  "architectural level rather than relying on manual implementation".
  **Operator decision 2 from iteration 32 ("make the lock mechanical") is
  VOID: it already is.**
- **The October procedure is covered by six tests**, including the trim
  itself (`test_registered_run_locks_holdout_trims_data_and_registers_trials`),
  double-spend rejection, future-dated candles being unable to anchor
  `holdout_start` years ahead, isolated holdout-segment metrics, and the
  boundary-day move not being dropped.
- **What survives, and it matters.** Iteration 33's fix was the real
  hole: diagnostics like `analyze_whipsaw` read candle files **directly**
  and never call `run_registered_backtest`, so the trim never protected
  them. **Trials were mechanically safe all along; diagnostics were
  not.** The soft-contamination history — the whipsaw verdict that placed
  hysteresis first in Goal P — is untouched by this correction and still
  travels to October.
- **How iteration 32 went wrong, named plainly.** It inferred a mechanism
  claim from **ten argparse defaults without reading the runner they feed
  into**. That is asserting instead of measuring, the same failure this
  program has caught in itself before (the retracted 0.9+ correlation
  claim, the retracted sleeve-count synthesis, the pooled-universe
  headline). Three of iteration 32's statements have now needed
  correction across two iterations.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read,
  nominations unchanged, `spent` still `false`, no code changed this
  iteration.
- **Standing answer restated, one clause strengthened:** timing works in
  crypto only and in its own universe bought both return and drawdown;
  the 4.70x twin edge is audited and robust; the engine is free of
  look-ahead, verified to the cent; execution-latency cost is about
  -6.4 bps round-trip, bounded above by ~17 bps, inside tested headroom;
  **the October holdout is protected mechanically by the runner's trim,
  not by convention, and its spend path is covered by six tests** —
  ~366 days remain, `spent` is false, and the one real leak channel
  (diagnostics) was closed in iteration 33 though its historical caveat
  stands; against the naive 13-coin alternative the margin is only 5.4%
  and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 35 (loop, Taiwan verdict closed; audit route declared converged)

- **Step 0, with a warning raised rather than buried.** Two of the
  previous three iterations corrected **my own recent work** rather than
  finding anything new (32 was wrong, 34 retracted it). That is precisely
  the diminishing-returns signal Step 0 exists to detect. This iteration
  targets the last substantive standing-answer claim never checked at
  source, then reports honestly on whether the route should continue.
  Zero new scripts, zero new documents.
- **Hypothesis: the Taiwan verdict is a dividend artefact.** 0050 pays
  ~3-4% a year; over 2018-03 to 2025-07 that compounds ~30%, enough to
  overturn "timing adds none in Taiwan (0.73x)" if the system and its
  benchmark treated dividends differently.
- **Refuted structurally.** The Taiwan `src/backtest/engine.py` derives
  the benchmark from the same candles the system trades:
  `benchmark_open_prices = dict(open_prices)` taken from
  `execution_candles`, then
  `growth += budget * close_prices[s] / benchmark_open_prices[s]`.
  One series feeds both sides, so adjusted-versus-raw shifts them
  **together** and no relative distortion is possible. This iteration
  deliberately did **not** resolve which series is used, because the
  conclusion does not depend on it.
- **Any residual error is conservative.** The system is ~30% invested
  against a 100%-invested benchmark, so missing dividends would
  understate the **benchmark** more, making the Taiwan loss look
  *smaller* than truth. The recorded verdict is correct or too kind, not
  an artefact. **Route closed.**
- **P1 status: nothing due, nothing missing.** `shadow_trial88` 4 rows,
  `shadow_trial118` 4 rows, next fire 2026-07-29 08:20; `shadow_tw0050`
  and `shadow_gld` 1 row each, first scheduled fire 2026-08-01.
- **Convergence declaration: the audit route opened at iteration 25 is
  converged.**

  | Iteration | Outcome |
  |---:|---|
  | 25 | **Finding** — forward-validation timetable wrong by ~8x; MinTRL 2028-06-29 |
  | 26 | **Finding** — the gate-4 pass survives only a stopped search |
  | 27 | **Finding** — only 2 of 6 gates ever adjudicated, both defective |
  | 28 | **Finding** — the headline sentence pooled two universes |
  | 29 | Refuted two attacks; metric survived |
  | 30 | Acquittal on look-ahead, plus one new gap |
  | 31 | **Finding** — that gap measured and de-escalated |
  | 32 | **Partly wrong** |
  | 33 | Fix (the one real hole) |
  | 34 | **Retraction of 32** |
  | 35 | Refuted; route closed |

  The last genuinely new finding was iteration 31. Four of the last five
  iterations produced refutations, fixes, or corrections of my own work.
  By Step 0's own criterion the route is worked out.
- **What the loop should do next.** None of the three unblocking states is
  reachable by analysis: forward rows need time (2028-06-29 for a return
  verdict), the October holdout is operator-only, and P3 refuses new
  families. The remaining mode is **P1 maintenance** — confirm the four
  tracks gain rows, correct anything found wrong, and stop manufacturing
  work. Two operator items remain, both narrowed by iteration 34: carry
  the whipsaw soft-contamination caveat into the October result, and
  optionally repoint `analyze_symbol_dispersion` for tidiness (it is
  already date-bounded, so this is cosmetic, not protective).
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read, no code
  changed, nominations unchanged.
- **Standing answer restated, unchanged in substance:** timing works in
  crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is audited and
  robust; the engine is free of look-ahead, verified to the cent;
  execution-latency cost is about -6.4 bps round-trip, bounded above by
  ~17 bps, inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; **the Taiwan
  and gold negatives are robust to dividend treatment and if anything
  understated**; against the naive 13-coin alternative the margin is only
  5.4% and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 36 (loop, P1 maintenance only — first post-convergence iteration)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 35. What this iteration moves: **it advances nothing new by
  design.** Iteration 35 declared the audit route converged; the
  contract's own guidance (line 182) is "do P1 maintenance, confirm the
  three tracks are gaining rows, and stop. Do not manufacture a
  diagnostic in order to have something to commit." This iteration tests
  whether the loop will honour that instruction rather than drift back
  into diagnostic-generation. Zero new scripts, zero new documents, one
  dated addendum to `RESEARCH_LOG.md`.
- **P1 status — all four tracks green.** Verified by direct read of the
  jsonl files and today's shadow-run log:

  | Track | Rows | Last date | Next fire | Today's run |
  |---|---:|---|---|---|
  | `shadow_trial88` (crypto BTC/ETH, source trial 88) | 4 | 2026-07-27 | 2026-07-29 08:20 | exit=0 at 08:20:07+08 |
  | `shadow_trial118` (crypto BTC/ETH, source trial 118) | 4 | 2026-07-27 | 2026-07-29 08:20 | exit=0 at 08:20:07+08 |
  | `shadow_tw0050` (Taiwan 0050, source trial 23) | 1 | 2026-07-24 | 2026-08-01 09:40 (weekly Sat) | not scheduled today |
  | `shadow_gld` (US GLD, source trial 24) | 1 | 2026-07-23 | 2026-08-01 09:40 (weekly Sat) | not scheduled today |

  Nothing broken, nothing due. The two weekly tracks are three days from
  their first non-seed row; if that fire fails on Saturday it becomes
  P1 obligation of iteration 37 or 38.
- **Step 2 (web research) done and recorded** — three passes, two
  actionable-adjacent papers (Han/Kang/Ryu SSRN 4675565 on crypto
  momentum under realistic assumptions, Huang/Sangiorgi/Urquhart SSRN
  4825389 on volume-weighted TSMOM). Both are blocked by P3 (no new
  single-market families). Filed in `RESEARCH_LOG.md` so the same
  searches are not re-issued. Third consecutive iteration with no
  directly-actionable literature under the P1-only constraint.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract edited, no trial registered, no backtest run, holdout not
  read, `spent` still `false`, no code changed, no diagnostic script
  written, no research document created. Verification (rule 7) not run
  because no source file changed — consistent with iterations 34-35.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is audited and
  robust; the engine is free of look-ahead, verified to the cent;
  execution-latency cost is about -6.4 bps round-trip, bounded above by
  ~17 bps, inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; the Taiwan
  and gold negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin is only
  5.4% and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 37 (session loop, handoff verification and shutdown)

- **Purpose: verify the unattended mechanism, then hand off.** Iteration
  35 declared the audit route converged; iteration 36 (this session)
  deliberately committed nothing so the nightly headless run could own
  that number cleanly. This iteration checks whether it did.
- **Verified, end to end and correct.** `CryptoResearchLoop` fired
  2026-07-28 21:37:01, exit 0, finished 21:41:24 (~4 minutes),
  `docs/research/loop_runs/run_20260728_213701.log`. It:
  - numbered itself **iteration 36**, with no collision;
  - read the convergence declaration and did **P1 maintenance only**,
    recording the standing answer "unchanged in every clause";
  - performed contract step 2 independently, surfacing SSRN 4675565
    (crypto momentum under realistic assumptions) and SSRN 4825389
    (volume-weighted TSMOM), and **correctly judged both blocked by P3**;
  - named its own next P1 obligation — confirm the 2026-08-01 Saturday
    fire appends a second row to the TW and GLD tracks;
  - committed `de0cb9d` and pushed. `origin/main` and local are both at
    `de0cb9d`, 0 ahead / 0 behind.
- **Operator decision, 2026-07-28: the session loop is stopped.** The
  reason is not fatigue and not diminishing returns in the abstract — it
  is that the free nightly mechanism was demonstrated tonight to do the
  same job correctly, so a paid session loop iterating the same contract
  on a converged route is strictly redundant. Research does not stop; it
  moves to the leg that costs nothing.
- **What continues unattended:**
  - `CryptoResearchLoop` — daily 21:37, one contract iteration.
  - `CryptoShadowTrial88` — daily 08:20, writes `shadow_trial88.jsonl`
    and `shadow_trial118.jsonl` (4 rows each).
  - `TwShadow0050` — Saturdays 09:40, first fire **2026-08-01**; both
    `shadow_tw0050.jsonl` and `shadow_gld.jsonl` still at their 1-row
    manual seeds, which is expected, not a fault.
- **Open items that need the operator, not the loop:**
  1. Carry the whipsaw soft-contamination caveat into the October
     holdout result document (`HOLDOUT_INTEGRITY_2026-07-28.md`).
  2. If an earlier answer date than 2028-06-29 is wanted, the only lever
     is a P3 override toward a higher-Sharpe design — MinTRL falls with
     the square of the Sharpe. The cost is trial 118's gate-4 pass, which
     fails at N=134 (`GATE4_FRAGILITY_2026-07-28.md`).
  3. Optionally repoint `analyze_symbol_dispersion` at the pre-holdout
     slice. Cosmetic only — it is already date-bounded to 2025-07-01.
- **Standing answer at handoff, unchanged:** timing works in crypto only
  and in its own universe bought both return and drawdown (14.26x vs
  6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin edge is
  audited and robust to twin construction and asset mix; the engine is
  free of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside tested
  headroom; the October holdout is protected mechanically by the runner's
  trim, unread by all 133 trials, with ~366 days available and its spend
  path covered by six tests; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth fails;
  **nothing is forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**; the single gate-4 pass
  holds only for a stopped search; and the six-gate framework has
  exercised exactly two gates, both with recorded defects.

## 2026-07-30 — iteration 38 (nightly headless, P1 maintenance)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iteration 37 handoff: timing
     works in crypto only; in its own universe it bought both return
     (14.26x vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no forward-based
     return verdict is statistically permitted before **2028-06-29**;
     the single gate-4 pass on trial 118 holds only for a stopped
     search; the six-gate framework has exercised only gates 3 and 4,
     both with recorded defects; the audit route is declared
     converged (iteration 35).
  2. **What this iteration moves.** Confirms the three continuing
     unattended tracks (crypto x2, weekly TW+GLD) are still gaining
     rows on schedule, and records that yesterday's nightly loop
     (2026-07-29 21:37) crashed with an upstream API
     `ConnectionRefused` before it could number itself as an
     iteration. Names no new decision; closes no route.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable to "confirm rows"), no new document,
     no gate rerun, no trial registered. Under contract's
     analytical-routes-exhausted clause the correct behaviour is
     "do P1 maintenance, confirm three tracks are gaining rows,
     and stop" — this iteration does exactly that.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Last date | Next fire | Today |
  |---|---|---:|---|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 6 (5 real + seed) | 2026-07-29 | 2026-07-31 08:20 | wrote 2026-07-30 at 08:20:07+00 (equity 999.44) |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 6 (5 real + seed) | 2026-07-29 | 2026-07-31 08:20 | wrote 2026-07-30 at 08:20:07+00 (equity 1006.23) |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed) | 2026-07-26 | 2026-08-01 09:40 (Sat) | not scheduled today |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 1 (seed) | 2026-07-26 | 2026-08-01 09:40 (Sat) | not scheduled today |

  Nothing broken, nothing due. The two weekly tracks are still
  two days from their first non-seed row; if Saturday's fire
  misses, that becomes P1 obligation of iteration 39 or 40.
  Iteration 36's own next-P1 obligation ("confirm 2026-08-01
  Saturday fire appends a second row to TW and GLD") is carried
  forward unchanged.
- **Nightly loop failure recorded, not fixed here.** The
  `CryptoResearchLoop` scheduled task fired 2026-07-29 21:37:01,
  ran ~3 minutes, and exited 1 —
  `docs/research/loop_runs/run_20260729_213701.log` contains a
  single line: `API Error: Unable to connect to API
  (ConnectionRefused)`. No LOOP_LOG entry was written, no
  iteration was numbered, and no source file changed, so the
  research state is uncorrupted. This is a transient upstream
  outage (Claude API), not a repo defect; iteration 37 explicitly
  named this exact failure mode as an acceptable one because a
  missed nightly does not touch the frozen artefacts. Not
  escalating unless it recurs — a second consecutive miss would
  need operator attention on the scheduled task's Claude
  invocation.
- **Step 2 (web research) done and recorded.** Three passes,
  one new-looking finding (arXiv 2602.11708 — adaptive-allocator
  trend-following on 150+ crypto pairs, headline SR 2.41) which
  P3 refuses because it is a simultaneous universe-and-family
  expansion; two other passes returned DSR restatements and
  practitioner blog posts already known. Filed in
  `RESEARCH_LOG.md` under iteration 38. **Fourth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint — signal that the binding constraint is
  forward rows, not literature.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed, no
  diagnostic script written, no research document created,
  no pre-registration touched. Verification (rule 7) not run
  because no source file changed — consistent with iterations
  34-37.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought
  both return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%);
  the 4.70x twin edge is audited and robust; the engine is free
  of look-ahead, verified to the cent; execution-latency cost
  is about -6.4 bps round-trip, bounded above by ~17 bps,
  inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; the
  Taiwan and gold negatives are robust to dividend treatment
  and if anything understated; against the naive 13-coin
  alternative the margin is only 5.4% and that benchmark is
  survivorship-flattered; breadth still fails; **nothing is
  forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**; the single
  gate-4 pass holds only for a stopped search; and the
  framework has exercised exactly two gates, both defective.

## 2026-07-31 — iteration 39 (P1 maintenance, on-chain route awaits operator hypothesis lock)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iteration 38. Timing works
     in crypto only; own universe bought both return (14.26x vs
     6.05x) and drawdown (33.05% vs 80.99%); the 4.70x exposure-
     matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; audit route declared converged (iteration 35).
  2. **What this iteration moves.** Declares in one place what the
     unnumbered `ba0b99f` ("Open the on-chain route: source
     inventory, no strategy", 2026-07-30 22:39) opened but did not
     close: the on-chain route is now standing, no hypothesis lock
     exists, and the contract's own queue block ("Queue as of
     2026-07-26 (latest)") does not yet mention it. Records that
     iteration 39 will NOT write an on-chain pre-registration
     unilaterally — that is a substantive hypothesis choice and
     needs an operator order. Route remains open; next actionable
     step is operator-scoped, not Claude-scoped.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable), no new research document, no gate rerun,
     no trial registered, no edit to `AUTONOMOUS_RESEARCH_LOOP.md`
     or any frozen contract. The LOOP_LOG entry records a
     decision (defer the on-chain pre-reg to operator hypothesis
     order); under Step 0's document rule "no new research
     document unless it records a decision or a closed route", a
     LOOP_LOG entry that records a defer-decision is inside the
     rule, not outside it. Under contract's analytical-routes-
     exhausted clause the correct behaviour absent an operator
     order is P1 maintenance — this iteration does exactly that.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Dates covered | Today's fire |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 7 (6 real + seed) | 2026-07-24 .. 2026-07-30 | wrote 2026-07-30 row at 01:31:46 UTC = 09:31 local, equity 999.9328, exposure `{BTC: 0, ETH: 0.25}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 7 (6 real + seed) | 2026-07-24 .. 2026-07-30 | wrote 2026-07-30 row at 01:31:46 UTC = 09:31 local, equity 1010.3542, exposure `{BTC: 0.5, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed) | 2026-07-24 (seed) | not scheduled today; next fire 2026-08-01 09:40 Sat |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 1 (seed) | 2026-07-23 (seed) | not scheduled today; next fire 2026-08-01 09:40 Sat |

  Two accounting corrections to iteration 38's own numbers,
  read directly from the jsonl:

  - Iteration 38 said trial88 wrote a 2026-07-30 row at
    08:20:07+00 UTC with equity 999.44. The jsonl shows the
    999.4365 equity attaches to the row for **date 2026-07-29**
    written at UTC 2026-07-30 00:20:07; the row for **date
    2026-07-30** was written today at UTC 01:31:46 with equity
    999.9328. Same-shift, off-by-one date label in iteration 38.
  - Same off-by-one for trial118: 1006.226 is the 2026-07-29 row
    (not 2026-07-30 as iteration 38 said); the 2026-07-30 row
    was written today at UTC 01:31:46 with equity 1010.3542.

  Two schedule observations for the record, not acted on:

  - Today's crypto shadow fire ran at 09:31 local (01:31 UTC),
    not the previous 08:20 local (00:20 UTC) documented in six
    prior `shadow_runs/shadow_YYYYMMDD_082001.log` files. The
    schedule shifted between 2026-07-30 08:20 local and today.
    No `.log` from 08:20 today exists, so the earlier scheduled
    task either did not fire or was replaced. Either way the row
    was written before any decision would consume it. Not a
    defect; recording so a future missed fire is diagnosed
    correctly.
  - `shadow_tw0050` last row is dated 2026-07-24 (seed) and
    `shadow_gld` last row is dated 2026-07-23 (seed). Both are
    still at their iteration-38 state. Iteration 36's carried-
    forward obligation ("confirm 2026-08-01 Saturday fire
    appends a second row to TW and GLD") lands on iteration 40
    or 41 depending on when the nightly loop fires next.
- **On-chain route: standing but unadvanced today, and why.**
  `ONCHAIN_SOURCE_INVENTORY_2026-07-29.md` opened the route with
  four decisions locked before any fit: keyless Coin Metrics
  community API is the source; genuinely non-price metrics are
  the ten listed (`AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`,
  `TxTfrCnt`, `FeeTotNtv`, `IssTotNtv`, `HashRate`, `FlowInExNtv`,
  `FlowOutExNtv`, `SplyExNtv`); every on-chain input lags D-1
  because completion is 3.02-3.18 h after UTC day close;
  validation moves from level agreement (unusable, median ratio
  1.391) to daily-change correlation ≥ some floor (measured
  +0.8729 on `AdrActCnt` vs blockchain.com over 1337 days).
  What the inventory explicitly did not decide: which metric or
  metric-combination to test, in which direction, against what
  passing threshold, with what N-budget cost against the gate-4
  fragility (a 134th trial would break trial 118's DSR pass unless
  its Sharpe fell inside [0.709, 1.180], per
  `GATE4_FRAGILITY_2026-07-28.md`). Writing that pre-registration
  is a substantive hypothesis choice, and the standing goalpost-
  drift guard at contract line 344-347 restricts Claude from
  authoring a next pre-registration in an iteration that reads
  prior state absent explicit operator order in the same sitting.
  No such order exists in today's input. **Iteration 39 therefore
  does not touch the on-chain route.** Options for iteration 40+
  when the operator decides: (a) close by refusing to spend
  registry N; (b) issue a hypothesis-scope order (which metric,
  which direction, which pass criterion) and let a subsequent
  iteration write the pre-reg; (c) hand the pre-reg authorship
  to a human. All three are legitimate under the contract; the
  ambiguity is not.
- **Step 2 (web research) done and recorded.** Three passes:
  practitioner exchange-netflow narratives (accumulation vs
  distribution language, no peer-reviewed backtest with realistic
  costs); active-address predictive signal (one MDPI 2026 paper
  using ML crisis-period features — P3 refuses on parameter-
  family grounds); MVRV backtest search — TradingView scripts and
  Coin Bureau guide, one useful negative line ("neither MVRV nor
  other popular indicators has survived a rigorous backtest
  across all historical cycles as a reliable standalone signal")
  which corroborates the standing answer. Filed in
  `RESEARCH_LOG.md` under iteration 39. **Fifth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint. The web-research signal is consistent —
  the binding constraint is forward rows plus operator hypothesis
  authority, not literature.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed, no
  diagnostic script written, no research document created, no
  pre-registration touched, on-chain ingestion not started.
  Verification (rule 7) not run because no source file under
  version control changed except this log entry itself and
  `RESEARCH_LOG.md` — consistent with iterations 34-38.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought
  both return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%);
  the 4.70x twin edge is audited and robust; the engine is free
  of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside
  tested headroom; the October holdout is protected mechanically
  and its spend path is covered by six tests; the Taiwan and gold
  negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; **nothing is forward-validated and no
  return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped
  search; and the framework has exercised exactly two gates,
  both defective. New line, dated 2026-07-31: the on-chain route
  is opened but unadvanced — inventory locked, pre-registration
  awaits operator hypothesis order.

## 2026-08-03 — iteration 40 (P1 maintenance, TW shadow broken, two research-loop misses recorded)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-39. Timing works
     in crypto only; own universe bought both return (14.26x vs 6.05x)
     and drawdown (33.05% vs 80.99%); the 4.70x exposure-matched twin
     edge is audited and robust; no return-based forward verdict is
     statistically permitted before **2028-06-29**; trial 118's gate-4
     pass holds only for a stopped search; the six-gate framework has
     exercised only gates 3 and 4, both with recorded defects; audit
     route declared converged (iteration 35); on-chain route open but
     unadvanced pending operator hypothesis lock.
  2. **What this iteration moves.** Records four facts read directly
     from source files, none changing the standing answer: (a) the TW
     0050 shadow is BROKEN — still at 1 seed row from 2026-07-24
     because the Saturday 2026-08-01 09:40 fire hit a TWSE
     `STOCK_DAY` ingest error and never reached the 0050 append step;
     (b) the GLD shadow gained its first non-seed row (2026-07-31,
     close 371.54, exposure 0) on 2026-08-01 09:55 local — one branch
     of the Sat fire worked, the other did not; (c) the daily crypto
     shadow missed its 2026-08-02 08:20 fire, caught up today at
     00:53 local writing the 2026-08-01 row late — no dates dropped
     but the schedule is drifting; (d) the nightly research loop
     missed BOTH 2026-08-01 21:37 and 2026-08-02 21:37 firings —
     iteration 39 named a second consecutive miss as the point that
     needs operator attention, so this is now flagged. This iteration
     is 00:53 local, i.e. today's recovery firing.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable — the TW ingest bug lives in `D:/TW-Stock-Trading`,
     a separate repo, and this loop's iron rule 1 forbids touching
     the live runtime side); no new research document; no gate rerun;
     no trial registered; no edit to any frozen contract; the LOOP_LOG
     entry records observations and one P1 escalation
     (operator-attention flag on TW shadow + research-loop scheduler),
     which is inside Step 0's rule "no new document unless it records
     a decision or a closed route" because the escalation IS a
     decision — defer fix to operator since the fix lives outside
     this repo's boundary. Under contract's analytical-routes-
     exhausted clause the correct behaviour is P1 maintenance; that
     is exactly what this iteration does.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Dates covered | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 9 (8 real + seed) | 2026-07-24 .. 2026-08-01 | OK — today's 00:53 local fire wrote 2026-08-01 row late (recorded_at 2026-08-02T16:53:28+00:00), equity 996.30, exposure `{BTC: 0, ETH: 0}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 9 (8 real + seed) | 2026-07-24 .. 2026-08-01 | OK — same fire wrote 2026-08-01 row, equity 993.28, exposure `{BTC: 0, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed only) | 2026-07-24 (seed) | **BROKEN** — 2026-08-01 09:40 Sat fire failed at TWSE `STOCK_DAY` step; log at `tw_shadow_20260801_094000.log` shows `python.exe : backfill failed: STOCK_DAY returned stat = '...'` (Chinese error garbled by PowerShell encoding). Corporate-actions and calendar refreshed 19063 events, TWSE month sweep began but the 0050 append never ran. Next scheduled Sat 2026-08-08 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 2 (1 real + seed) | 2026-07-23 (seed), 2026-07-31 (real) | OK — 2026-08-01 09:55 local wrote 2026-07-31 row, close 371.54, exposure 0, `WINDOWS_ON_0_OF_4` |

  Iteration 39's carried obligation — "confirm 2026-08-01 Saturday
  fire appends a second row to TW and GLD" — is resolved as **half
  pass, half fail.** GLD passed. TW failed and needs operator repair
  in the sibling repo before the next Sat fire is meaningful.
- **Nightly research loop schedule state.** `docs/research/loop_runs/`
  is missing files for 2026-08-01 21:37 and 2026-08-02 21:37 —
  contiguous with `run_20260731_213701.log` (last successful) and
  `run_20260803_005325.log` (this iteration). Two consecutive misses
  crosses iteration 39's escalation threshold. This is a scheduler
  problem, not a Claude API outage: the 2026-07-29 miss (recorded in
  iteration 38) had a `ConnectionRefused` line inside its log file;
  the 08-01/08-02 slots produced no log file at all, meaning the
  scheduled task itself did not fire. Not fixing here — the task is
  registered under Windows Task Scheduler outside this repo's
  operational boundary (`data/runtime/shadow_runs/task_registered.txt`
  references it) and operator attention is the correct next step.
- **Runtime-side commits noted, not touched.** Commits `8d9ce67`
  (2026-07-31, "Wire the Donchian ensemble into the live runtime")
  and `2423bf6` (2026-07-31, "Switch the live signal to trial 118")
  landed on main between iteration 39 and today. Iron rule 1 forbids
  iterations from touching the live paper contract; these commits
  are operator-attributed and inside the runtime side, so they do
  not violate the rule. Recorded here so a future audit can see that
  the shadow tracks now read from a live runtime that itself has
  been switched to the trial-118 configuration (`atr_multiple: 2`,
  `exit: atr_channel`) — the shadow trial88 file continues to write
  its own trial-88 numbers (`atr_multiple: 3`, `exit: mid_channel`),
  so the two are still parallel unbiased signals as long as the
  daily shadow driver stays configured against both trials. Verified
  from the shadow rows above that both configs are being written
  side-by-side.
- **Step 2 (web research) done and recorded.** Three passes filed in
  `RESEARCH_LOG.md` under iteration 40: (i) arXiv 2209.05559 (crypto
  DRL overfitting, 2022 crash cohort) — corroborates PBO framework
  but adds no directly-testable rule; (ii) exchange-flow predictive
  research (arXiv 2411.06327 + practitioner data ~48,500 BTC net
  outflow in the 30 days ending early April 2026) — directly relevant
  to on-chain route but P3-blocked until operator locks a hypothesis
  (metric/direction/threshold); (iii) MinTRL and walk-forward
  literature — corroborates the 706-day MinTRL number on trial 88
  and Quantpedia's 33%/44% Sharpe degradation OOS finding, both
  already inside the standing answer's caveats. **Sixth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint. Consistent with iterations 35/37/38/39.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed in either
  repo, no diagnostic script written, no research document created,
  no pre-registration touched, on-chain ingestion not started, TW
  shadow bug not fixed (operator boundary). Verification (rule 7)
  not run because no source file under version control changed
  except this log entry and `RESEARCH_LOG.md` — consistent with
  iterations 34-39.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought both
  return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the
  4.70x twin edge is audited and robust; the engine is free of
  look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside
  tested headroom; the October holdout is protected mechanically
  and its spend path is covered by six tests; the Taiwan and gold
  negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; **nothing is forward-validated and no
  return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped
  search; and the framework has exercised exactly two gates, both
  defective. On-chain route open but unadvanced. New operator-
  attention items, dated 2026-08-03: (a) TW 0050 shadow ingest
  broken since 2026-08-01, needs operator repair in
  `D:/TW-Stock-Trading` before Sat 2026-08-08 fire; (b) nightly
  research loop scheduled task missed 2026-08-01 and 2026-08-02
  slots with no log emission, indicating Task Scheduler misfire
  rather than in-process outage.

## 2026-08-15 — iteration 42 (P1 maintenance after an 11-night loop outage; iteration 40's root cause corrected)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-40. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** It closes the question "why has
     this loop produced nothing since 2026-08-03?" with a root cause
     read from log files rather than inferred, and it **corrects
     iteration 40's answer to that same question**, which named the
     wrong cause. It also resolves iteration 40's open obligation on
     the Taiwan track, records a permanent hole in the crypto forward
     record with the arithmetic needed to bound its damage, and repairs
     two verification defects that made contract rule 7 unrunnable as
     written.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a scheduler-auth outage or to a jsonl gap). No new
     research document. No gate rerun, no trial registered, no
     pre-registration touched, no frozen contract edited. Two config
     lines changed in `pyproject.toml`, both purely to make the
     contract's own verification command execute; no source or research
     content altered. Under the analytical-routes-exhausted clause the
     prescribed behaviour is P1 maintenance, and every item here is P1.
- **Root cause of the outage, and a correction to iteration 40.** The
  nightly `CryptoResearchLoop` task (registered 2026-07-21, daily
  21:37) **did fire** on 2026-08-04, 08-05, 08-06, 08-07, 08-09, 08-11,
  08-12 (21:53), 08-13 and 08-14. Every one of those runs is a 480-byte
  log containing exactly one error and an exit code:

  ```
  Failed to authenticate. API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"OAuth access token has expired. Re-authenticate to continue."},"request_id":null}
  exit=1
  ```

  Four extra daytime retries (2026-08-11 09:48 and 15:19, 08-12 17:53,
  08-13 09:58) failed identically. The 2026-08-03 21:37 and 2026-08-08
  21:37 logs are 0 bytes; the 2026-08-10 21:37 slot produced no file at
  all. **Net: zero completed iterations from 2026-08-04 to 2026-08-14,
  eleven nights.** Iteration 40 recorded the cause as "Task Scheduler
  misfire rather than in-process outage". For the outage that followed
  **that is wrong** — the task fires reliably and the agent cannot
  authenticate. Corrected here per the standing correction duty. The
  2026-08-01 and 2026-08-02 slots remain fileless and therefore still
  unexplained; they are a separate, earlier symptom and are not
  evidence for the auth diagnosis.
- **Orphaned iteration 41, committed unedited.** `RESEARCH_LOG.md`
  carried an uncommitted `## 2026-08-03 — iteration 41` block (four
  sources: arXiv 2602.11708, arXiv 2510.23150, arXiv 2603.20319, and
  the DSR literature) with **no** LOOP_LOG entry and no commit. That
  iteration completed step 2 and died before step 5 — consistent with
  the 0-byte 2026-08-03 21:37 log. It is committed today exactly as
  written, keeps the number 41, and today's work is numbered 42, so the
  numbering stays auditable rather than being silently reused.
- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Dates covered | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 21 (20 real + seed) | 2026-07-24 .. 2026-08-14, **2026-08-09 missing** | OK — last row 2026-08-14 written 2026-08-15T00:20:05.804828+00:00, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 21 (20 real + seed) | 2026-07-24 .. 2026-08-14, **2026-08-09 missing** | OK — last row 2026-08-14 written 2026-08-15T00:20:05.836265+00:00, equity 994.7655928691401162549420727, exposure `{BTC: 0.25, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-07-24 (seed), 08-07, 08-11, 08-12, 08-14 | **REPAIRED** — last row 2026-08-14 written 2026-08-15T01:49:32.325851+00:00, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-07-23 (seed), 07-31, 08-07, 08-10, 08-11, 08-14 | OK — last row 2026-08-14 written 2026-08-15T01:49:32.462409+00:00, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 |

  Iteration 40's operator-attention item (a) — the Taiwan 0050 ingest
  broken since 2026-08-01 — is **resolved**. The Saturday fires of
  2026-08-08 and 2026-08-15 both appended (01:49 UTC = 09:49 local),
  and two extra runs on 08-11 and 08-12 added rows as well. **Forward
  evidence accumulated normally throughout the loop outage**: the
  shadow drivers are separate scheduled tasks and never depended on the
  research agent.
- **One permanently lost forward row, and what it cost.** No
  `shadow_20260810_0820*.log` exists, so the 2026-08-10 08:20 fire did
  not run and the **2026-08-09** row was never written; the next run
  (2026-08-11 09:48 local) wrote the 2026-08-10 row and did **not**
  backfill. The gap is left as-is: fabricating a row after the fact
  would corrupt an append-only forward record, which is the one clean
  evidence stream this project still has. Damage bounded by arithmetic
  on trial 118, the only track that was exposed. From the 2026-08-08
  row (equity 1002.9901337, BTC 64962.60, ETH 1916.74) to the
  2026-08-10 row (BTC 63970.01, ETH 1873.16): BTC -1.5279%, ETH
  -2.2737%; at the driver's per-symbol weighting (exposure divided by
  the two symbols) the two-day portfolio return is **-0.759406%**,
  predicting equity **995.373370** against **995.373372** recorded. So
  the driver compounds from the last recorded close and the missing day
  **did not distort the equity path**. What was lost is at most one
  exposure update dated 2026-08-09, and it is unrecoverable.
- **Verification (rule 7) run bare, and two defects repaired to make it
  runnable.** `ruff format --check` failed on
  `docs/research/VS_BUY_AND_HOLD_2026-07-26.md:271` because **ruff
  0.16.2 now formats Python blocks inside Markdown** and wanted to
  restyle a source excerpt quoted verbatim in a recorded result
  document. Editing that document to satisfy a formatter would violate
  iron rule 3, so `*.md` was added to `[tool.ruff] exclude` instead — a
  formatter must never rewrite append-only records. Separately,
  `pytest -m "not network"` failed collection in **36 modules** with
  `ModuleNotFoundError: No module named 'src'`, because bare `pytest`
  resolves to the system Python 3.12 on PATH, which has neither the
  editable install nor the repo root on `sys.path`; `pythonpath = ["."]`
  was added to `[tool.pytest.ini_options]` so the command in rule 7
  works as written under any interpreter. Results after both fixes, all
  run bare: `ruff check` **All checks passed!**; `ruff format --check`
  **128 files already formatted** (exactly the 128 tracked `.py`
  files); `mypy --strict src/` **Success: no issues found in 58 source
  files**; `lint-imports` **Contracts: 13 kept, 0 broken** over 81 files
  and 325 dependencies; `pytest -m "not network"` **383 passed** in
  125.10s. Tree green.
- **Step 2 (web research) done and recorded.** Three passes filed in
  `RESEARCH_LOG.md` under iteration 42: (i) arXiv **2607.19453**
  (Jadouli, 2026-07-21) — the closest external match to this project's
  product law yet found (Binance **spot**, daily and 4h candles,
  **long-only**, costs charged at 31 bps per cycle) and a registered
  **negative**: "every operational decision remains NO_TRADE", ten-pair
  daily selector -6.72% over 19 cycles, ROC AUC 0.874-0.896 against
  average precision 0.116-0.134. Recorded as an external base rate, not
  as a strategy; (ii) *Order flow and cryptocurrency returns* (J. Emp.
  Fin., S1386418126000029, 2026-01) — order flow claimed to have
  out-of-sample predictive power surviving short-sale constraints and
  high costs; adjacent to but **not** the same as the open on-chain
  route (exchange order flow, not on-chain netflow), and its numbers
  are **unverified at source** (publisher 403, working-paper PDF TLS
  failure) so they may not be quoted in a result document yet; (iii)
  e-values / anytime-valid inference — **pre-refused** as a route to
  reading the forward tracks before 2028-06-29, because
  anytime-validity buys permission to look, not evidence, and is
  strictly less powerful than the fixed-sample test at the same date.
  **Eighth consecutive iteration** with no directly-actionable
  literature under the P1-only constraint.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no runtime or `configs/runtime/` file touched, no shadow row
  fabricated or backfilled, on-chain ingestion not started.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-15: (a) **the
  nightly research loop cannot authenticate** — every scheduled run
  from 2026-08-04 to 2026-08-14 exited 1 on an expired OAuth token, and
  it will keep doing so until the credential is refreshed on the
  machine that runs the task; there is no in-repo fix; (b) the
  2026-08-10 08:20 crypto shadow fire never ran, costing the 2026-08-09
  row permanently — if that slot misses again the driver's scheduling
  needs operator inspection; (c) iteration 40's item (a), the Taiwan
  ingest break, is closed.

## 2026-08-16 — iteration 43 (P1: the shadow track's scheduling defect found, fixed, and one missed row recovered inside its 24h window)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-42. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** It closes iteration 42's open
     operator-attention item (b) — "the 2026-08-10 08:20 crypto shadow
     fire never ran; if that slot misses again the driver's scheduling
     needs operator inspection". It missed again on 2026-08-16. The
     cause is now identified from the task definition rather than
     inferred, **fixed at its source in this repo**, and the row that
     the miss would have destroyed was recovered before it became
     unrecoverable. Forward rows are the only evidence this program can
     still add, so a defect that silently deletes them is the highest
     P1 item there is.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a Task Scheduler settings defect). No new research
     document. No gate rerun, no trial registered, no backtest, no
     pre-registration or frozen contract touched. Two registration
     scripts changed, both to make an existing scheduled task actually
     fire. Under the analytical-routes-exhausted clause the prescribed
     behaviour is P1 maintenance; every item here is P1.
- **The miss, from the task itself.** Before any change,
  `Get-ScheduledTaskInfo CryptoShadowTrial88` reported `LastRunTime
  2026-08-15 08:20:01`, `LastTaskResult 0`, **`NumberOfMissedRuns 1`**
  and `NextRunTime 2026-08-17 08:20`. No `shadow_20260816_*.log` exists
  in `data/runtime/shadow_runs/`. So the 2026-08-16 08:20 slot was
  **dropped by the scheduler, not failed by the driver** — the same
  signature as 2026-08-10.
- **Root cause, and it was in this repo all along.**
  `scripts/register_shadow_task.ps1` built the task with a bare
  `New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit
  20m`. That cmdlet's **defaults** are `WakeToRun=$false`,
  `DisallowStartIfOnBatteries=$true`, `StopIfGoingOnBatteries=$true`,
  and the task was registered with a single daily trigger. Verified on
  the live task before the fix: `StartWhenAvailable True, WakeToRun
  False, DisallowStartIfOnBatteries True, StopIfGoingOnBatteries True,
  ExecutionTimeLimit PT20M, triggers 1`. This machine is a laptop
  (`Win32_Battery` reports device `L23M4PK4`, 76% charge), so any 08:20
  where the machine is asleep or on battery is dropped, and the
  `StartWhenAvailable` catch-up is itself blocked while on battery.
  **The live 08:05 runtime task hit exactly this failure on 2026-07-07
  and was fixed then** — `scripts/harden_daily_task.ps1` and
  `docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md`. Confirmed by comparison:
  `CryptoQuantDailySignalCycle` today has `WakeToRun True,
  DisallowStartIfOnBatteries False`, and it caught its own missed 08:05
  up at 12:32:04 on 2026-08-16, on the same machine, on the same
  morning the shadow task was dropped. The hardening was simply never
  applied to the two research-side tasks.
- **Evidence quality, stated honestly.** The mechanism above is read
  from task settings plus `System` power events (kernel power manager
  shutdown transitions at 00:20:06, 05:31:06 and 05:32:05 on 2026-08-16,
  then no system activity recorded until 12:30:17 — the 08:20 slot falls
  inside that gap). It is **not** read from a per-launch record, because
  `Microsoft-Windows-TaskScheduler/Operational` is **disabled** on this
  machine (`IsEnabled False`), so no "did not launch because ..." event
  exists for either miss. The settings defect is certain; which of
  asleep-versus-on-battery applied on a given morning is inference.
- **The row was recovered, and the recovery window is 24 hours.**
  `scripts/run_shadow_track.ps1` was run manually at 2026-08-16 21:42:04
  local (`shadow_20260816_214200.log`, `exit=0`) and appended the
  **2026-08-15** row to both tracks — 22 rows each now. It could do this
  only because `scripts/shadow_signal.py` appends the latest *closed*
  daily candle, and at 13:42 UTC on 08-16 that candle was still 08-15.
  Had the fix waited until after tomorrow's 08:20 fire, the 08-15 row
  would have been lost exactly the way the **2026-08-09** row was lost
  (iteration 42): the driver appends one day and never backfills.
  **A missed slot is therefore recoverable for about 24 hours and
  permanently lost after that** — worth knowing before the next miss.
- **The recovered row, verified against its source.** trial 88:
  `date 2026-08-15`, exposure `{BTCUSDT: 0, ETHUSDT: 0}`, equity
  `993.7564267590065144761572415` — unchanged, correctly, because the
  08-14 exposure was zero. trial 118: exposure `{BTCUSDT: 0.25,
  ETHUSDT: 0.5}`, closes `BTCUSDT 63086.01`, `ETHUSDT 1882.64`, equity
  `994.9074566318213201893273399`. Recomputed independently from the
  08-14 row (equity `994.7655928691401162549420727`, closes
  `63043.56` / `1882.20`) at the driver's per-symbol budget of 0.5:
  day return `0.000142610242752802864757661375`, predicted equity
  `994.9074566318213201893273399`, **difference 0E-25**. The equity
  path is intact across the miss.
- **Fix applied, and deliberately not applied uniformly.**
  `scripts/register_shadow_task.ps1` now registers the task with
  `-WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries`
  plus at-logon and on-unlock catch-up triggers (2-minute delay each),
  mirroring the runbook's three lines of defense. The unlock trigger is
  safe here **because the driver is idempotent** — `append_day` returns
  early when the last recorded date is already >= the latest closed
  candle — so an extra fire is a no-op. The script was re-run and the
  live task verified: `StartWhenAvailable True, WakeToRun True,
  DisallowStartIfOnBatteries False, StopIfGoingOnBatteries False,
  ExecutionTimeLimit PT20M, MultipleInstances IgnoreNew`, three triggers
  (daily 08:20, logon +2m, session-unlock +2m), `NextRunTime
  2026-08-17 08:20`. The OS-level gate `WakeToRun` depends on is already
  on from 2026-07-07: `powercfg` reports allow-wake-timers `0x00000001`
  on both AC and DC. **`RestartCount` was considered and refused** —
  `run_shadow_track.ps1` always exits 0 (it logs Python's exit code
  instead of propagating it), so a restart-on-failure setting could
  never fire.
- **`scripts/register_research_loop_task.ps1` carried the identical
  defect and is fixed the same way, minus the catch-up triggers.**
  `CryptoResearchLoop` also had `WakeToRun False,
  DisallowStartIfOnBatteries True, StopIfGoingOnBatteries True`. This is
  a **consistent explanation for the 2026-08-01 and 2026-08-02 fileless
  21:37 slots that iteration 42 left unexplained** — not a proven one,
  for the same reason as above (operational log disabled). Logon and
  unlock triggers were **not** added to this task: the shadow driver is
  idempotent but a research iteration is not — every fire writes a
  LOOP_LOG entry and consumes a working session, so unlock-triggered
  catch-up would manufacture duplicate iterations. One fire per day.
  The task's live settings are updated after this entry is committed,
  because the task is *currently running this iteration* and a
  definition rewrite mid-run risks killing it before step 5 completes —
  which is precisely how iteration 41 was orphaned.
- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 22 (21 real + seed) | 2026-08-15, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0}` | OK — 2026-08-09 still permanently missing (iteration 42) |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 22 (21 real + seed) | 2026-08-15, equity 994.9074566318213201893273399, exposure `{BTC: 0.25, ETH: 0.5}` | OK — same single 2026-08-09 hole |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-08-14, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 | OK — weekly; `TwShadow0050` next fire 2026-08-22 09:40, last result 0, missed 0 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-08-14, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 | OK — same weekly task |

- **Loop health.** `docs/research/loop_runs/run_20260815_213702.log` is
  3230 bytes (iteration 42, successful) and today's
  `run_20260816_213701.log` is this run. The OAuth expiry that killed
  eleven consecutive nights (2026-08-04 .. 2026-08-14, iteration 42) is
  resolved on the operator's side; this is the **second consecutive**
  successful scheduled fire.
- **Step 2 (web research) done and recorded.** Four passes filed in
  `RESEARCH_LOG.md` under iteration 43: (i) Li, Zhang and Zhou, *J.
  Futures Markets* 37(12) 2017 — trend rules beat buy-and-hold in
  Chinese commodity **futures**, robust to costs, with the authors'
  own data-snooping caveat; out of product law (futures), filed only as
  the closest external analogue to this project's own P2
  beat-buy-and-hold gate; (ii) **a widely-repeated Bitcoin volatility
  statistic that failed source verification** — "daily standard
  deviation ~5.3% in 2021 falling to ~2.1% in 2024-2025", attributed to
  State Street; the SSGA page (published 2026-02-03) was fetched and
  contains **no such numbers**, only a qualitative downward-trend claim
  on two-year rolling weekly returns, and the S&P Global piece returned
  HTTP 403. The pair is now **banned from this project's documents**.
  The underlying question — whether the 2018-2025 measurement came from
  a volatility regime that no longer exists — is real and testable here,
  and is deliberately **not** run, because under Step 0 it would be a
  diagnostic with no decision attached; (iii) arXiv 2602.11708 resurfaced
  and is **not** re-filed (already logged in iteration 41; its H6
  rebalance is outside the daily product law); (iv) practitioner claims
  that daily rebalancing is cost-dominated — inapplicable, since this
  book makes a daily *decision*, not a daily *rebalance*. **Ninth
  consecutive iteration** with no directly-actionable literature under
  the P1-only constraint.
- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed** in 50.05s.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no `configs/runtime/` or live-runtime file touched, **the live 08:05
  task's definition not touched** (iron rule 1 — only the two
  research-side tasks were changed), no shadow row fabricated, and the
  2026-08-09 hole left as a hole.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-16: (a)
  iteration 42's item (b) is **closed** — cause found, fixed in
  `scripts/register_shadow_task.ps1`, task re-registered, and the row
  it cost recovered; (b) iteration 42's item (a), the loop's OAuth
  expiry, is **closed** — two consecutive successful nightly fires;
  (c) **new, low priority:** `Microsoft-Windows-TaskScheduler/Operational`
  is disabled on this machine, which is why both shadow misses had to be
  diagnosed by inference; enabling it would make the next scheduling
  failure self-documenting.

## 2026-08-19 — iteration 44 (P1: both missed slots explained from evidence; the loop's own log made self-documenting)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-43. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** Two scheduled iterations, 2026-08-17
     and 2026-08-18, produced no LOOP_LOG entry and no commit. This
     iteration gives each a **verified cause** rather than a
     hypothesis, and then closes the class: the loop's own log now
     distinguishes "killed mid-run" from "never started" without
     forensic work, and the Task Scheduler Operational channel — open
     as operator-attention item (c) since iteration 43 — is enabled, so
     the next scheduling failure documents itself. Three consecutive
     iterations have now had to diagnose a miss by inference from
     indirect evidence; this one removes the need.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a logging or event-channel defect). No new
     research document. No gate rerun, no trial registered, no
     backtest, no pre-registration or frozen contract touched. One
     existing script gained a start marker and an append redirect; one
     OS event channel was enabled. Under the analytical-routes-
     exhausted clause the prescribed behaviour is P1 maintenance, and
     every item here is P1.

- **2026-08-17: refused at the door, not killed.**
  `docs/research/loop_runs/run_20260817_213701.log` is **218 bytes** and
  reads, in full, that the account had hit its weekly usage limit
  (resetting 8am Asia/Taipei), followed by `exit=1
  finished=2026-08-17T21:37:19.1612042+08:00`. The iteration therefore
  started at 21:37:01 and died **18 seconds later** on an account usage
  limit. This is operator-side and outside the loop's control; the same
  class as the eleven-night OAuth outage of iteration 42, but a
  different mechanism (quota, not authentication). No repo change can
  prevent it.

- **2026-08-18: a working iteration killed by an operator reboot.**
  `run_20260818_213702.log` is **0 bytes with no `exit=` line at all**,
  which under the old script means the redirect created the file and
  the process died before anything was flushed *and* before the
  trailing status line could be appended. The Windows **System** log
  supplies the mechanism directly:

  | Time | Event | Content |
  |---|---|---|
  | 2026-08-18 21:37:02 | (log file created) | iteration starts |
  | 2026-08-18 21:52:48 | `User32` **1074** | `StartMenuExperienceHost.exe (SMALLCAT)` initiated the **restart** of computer SMALLCAT **on behalf of user** `smallcat\Administrator`, reason `其他 (不在計劃之中)` |
  | 2026-08-18 21:52:57 | `Kernel-Power` **109** | kernel power manager initiated a shutdown transition |
  | 2026-08-18 21:53:09 | `Hyper-V-Hypervisor` **1** | hypervisor started (machine back up) |

  The iteration ran **15 minutes 46 seconds** and was then terminated
  by an operator-initiated restart from the Start menu. **This is the
  same failure mode that orphaned iteration 41**, and it is not a
  defect: the operator may reboot their own machine whenever they like.
  What was defective was that the evidence had to be reconstructed from
  a system log at all.

  **Two hypotheses were considered and are refuted, not merely
  unfavoured.** (i) *Scheduler settings*, the cause found in iteration
  43 for the shadow task — refuted by inspecting the live task, which
  already carries iteration 43's hardening: `WakeToRun True`,
  `StartWhenAvailable True`, `DisallowStartIfOnBatteries False`,
  `StopIfGoingOnBatteries False`. So iteration 43's fix **was**
  applied to the live `CryptoResearchLoop`, and it is not the
  explanation here. (ii) *`ExecutionTimeLimit` expiry* — the limit is
  `PT6H`, which from a 21:37 start expires at 03:37, long after the
  21:52 shutdown. Task state today: one daily trigger at 21:37,
  `RestartCount 0`, `NextRunTime 2026-08-20 21:37`,
  `NumberOfMissedRuns 0`.

- **Fix: the loop's log now says which of the two happened.**
  `scripts/run_research_loop.ps1` writes `started=<ISO-8601>` before
  invoking the agent and appends the agent's output with `*>>` instead
  of truncating with `*>`. From the next fire onward the three
  signatures are distinct and need no event log: a file with
  **neither** marker means the task never launched; **`started=` with
  no `exit=`** means an interrupted iteration; **both** means it ran to
  completion and the exit code says how it ended. The rewritten script
  was parse-checked (`PSParser.Tokenize`, zero errors) but deliberately
  **not** executed — running it would launch a second concurrent
  iteration on top of this one. It takes effect at the 2026-08-20
  21:37 fire.

- **Operator-attention item (c) from iteration 43 closed.**
  `Microsoft-Windows-TaskScheduler/Operational` was still
  `IsEnabled=False`, which is why the 2026-08-09, 2026-08-16 and
  2026-08-18 misses all had to be diagnosed indirectly. It is now
  **enabled** (`wevtutil sl ... /e:true`, exit 0; verified
  `IsEnabled=True`, `MaximumSizeInBytes=10485760`, `LogMode=Circular`).
  Circular at 10 MB, so it self-trims and cannot fill the disk. This is
  a diagnostic channel on the operator's machine, not a change to the
  trading system, and it is reversible with `/e:false`.

- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 25 (24 real + seed) | 2026-08-18, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0.25}`, closes 64725.42 / 1917.85 | OK — +3 rows since iteration 43 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 25 (24 real + seed) | 2026-08-18, equity 1002.796755227646803154754684, exposure `{BTC: 0.25, ETH: 0.5}` | OK — +3 rows since iteration 43 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-08-14, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 | OK — weekly; next fire 2026-08-22 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-08-14, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-18 with **exactly one
  date gap, 2026-08-08 to 2026-08-10** — the permanently lost
  2026-08-09 row from iteration 42. No new holes opened during the two
  missed research iterations, which is the point: the shadow driver and
  the research loop are separate tasks, and the research loop failing
  does not cost forward rows. `TwShadow0050` last result 0, missed 0.

- **Iteration 43's catch-up trigger observed working, and harmless.**
  `CryptoShadowTrial88` shows `LastRunTime 2026-08-19 15:58:13` with
  result 0 — that is the session-unlock trigger added in iteration 43,
  not the 08:20 daily fire. It wrote nothing, exactly as designed: the
  2026-08-18 row was already recorded at `2026-08-19T00:20:05Z` by the
  daily fire, and `append_day` returns early when the last recorded
  date is already current. The idempotence argument used to justify
  that trigger now has a live confirmation.

- **Step 2 (web research) done and recorded.** Five items filed in
  `RESEARCH_LOG.md` under iteration 44. The one that matters: **Gueta
  Quant's pre-registered funnel of 13 simple strategies on EURUSD
  daily (2020-2025, OOS 2024-2025) returned 13 to 0** — 8 passed their
  gate 1, 7 their gate 2, and **zero** passed either DSR >= 0.95 or
  PBO, with their Breakout Channel arm scoring **DSR 0.062** despite
  +1.52% OOS and +16.05% walk-forward return; their PBO was 0.5639
  (CSCV, 16 blocks, 12,870 combinations, family N=14). Source-verified
  by fetching the page, per the iteration-43 lesson. Out of product law
  (FX, not spot crypto), so **not testable here** and no trial follows
  from it — but it is the first outside evidence about how this
  project's own two deciding gates behave in independent hands, and it
  points the same way iteration 26's fragility measurement does. Also
  filed: a second independent arrival at the momentum-regime-decay
  question (flagged — a third should trigger asking the operator
  whether to attach a decision to it); a practitioner "100 trades makes
  a forward test valid" rule **explicitly refused** as a goalpost move
  against `FORWARD_TRACK_READ_PREREGISTRATION.md`; and arXiv 2512.22476
  (AutoQuant) disposed of as perpetual futures. Tenth consecutive pass
  with nothing directly actionable under P1-only.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed**, 1 warning, in 102.52s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false` (`holdout_lock.json` verified), no research document created,
  no diagnostic script written, no `configs/runtime/` or live-runtime
  file touched, the live 08:05 task's definition not touched, no shadow
  row fabricated, and the 2026-08-09 hole left as a hole. The Gueta
  result was **not** used to adjust any gate threshold or to reinterpret
  trial 118's DSR — reading someone else's failure as license to move
  one's own bar is the error this program most needs to avoid.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-19: (a)
  iteration 43's item (c) is **closed** — the Task Scheduler
  Operational channel is enabled; (b) **new, informational only:** the
  2026-08-17 slot was lost to a weekly account usage limit, which no
  repo change can prevent — if nightly iterations matter more than
  other usage, the operator controls that trade-off, not the loop;
  (c) **new, informational only:** the 2026-08-18 slot was lost to an
  operator-initiated restart 15m46s into the run. Reboots are the
  operator's prerogative; noted only so the two blank logs are not
  mistaken for a recurring defect.
