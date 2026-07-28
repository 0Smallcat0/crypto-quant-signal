# External research log (append-only)

Per `docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md` step 2: every iteration
appends 3–5 dated lines — source, claim, testable-here yes/no. Seeded from
`docs/research/EXTERNAL_EVIDENCE_2026-07.md` (2026-07 review): vol-managed
momentum strongest (tested, exp 2); carry dead and product-excluded;
cross-sectional momentum untested here → experiment 3.

## 2026-07-21 — iteration 1 web pass (experiment-3 engine work)

- 2026-07-21 — Springer FMPM 2025 ("Cryptocurrency momentum has (not) its
  moments", link.springer.com/article/10.1007/s11408-025-00474-9): claims
  crypto XS-momentum profits concentrate in high-volatility regimes and are
  fragile to costs; long-short Sharpe > 1 in-sample. Testable-here: **no**
  (long-short excluded by product law), but the fragility warning maps onto
  our absolute-filter arm and cost-sensitivity read-out.
- 2026-07-21 — Cambridge JFQA 2024 ("A Trend Factor for the Cross Section of
  Cryptocurrency Returns"): trend factor from multiple horizons subsumes
  single-lookback XS-momentum; 4-week and 8-week short-horizon trends carry
  most of the OOS explanatory power. Testable-here: **yes as a follow-up
  family** (would need multi-horizon signal engine — parked for post-exp-3
  RESEARCH_LOG hypothesis pool, not this iteration).
- 2026-07-21 — Trakx practitioner note (trakx.io/resources/insights/
  momentum-trading-in-cryptocurrencies-guide): large-cap crypto momentum
  usually rebalanced monthly, 50–200% annual turnover typical; weekly on a
  small universe magnifies cost drag. Testable-here: **yes** — the family's
  weekly-vs-monthly arm directly measures this, and our ≤ 53.1 turnover cap
  in the pre-registration lines up with the practitioner range.
- 2026-07-21 — ACFR AUT working paper ("Time-Series and Cross-Sectional
  Momentum in the Cryptocurrency Market"): TS and XS momentum are correlated
  but XS wins when the universe is homogeneous large-cap USDT pairs.
  Testable-here: **yes indirectly** — winner's return correlation with
  trial 4 (TS ensemble) is already the pre-declared diversification
  read-out; nothing new to add to the grid.

## 2026-07-21 — iteration 3 web pass (experiment-4 result read-out)

- 2026-07-21 — Ali Azary Medium 2025-04 ("Regime-filtered risk-adjusted
  momentum strategy with inverse-volatility weighting") aliazary.medium.com/
  regime-filtered-risk-adjusted-momentum-strategy-with-inverse-volatility-
  weighting-12-to-655-b145d64d8cf9: combines (a) market-regime filter that
  gates trading to bullish trend, (b) risk-adjusted momentum selection,
  (c) inverse-volatility weights, (d) trailing stop-loss for tail control.
  Testable-here: **yes** — item (a) is the natural next lever to try after
  exp-4 confirmed vol-target overlay alone cannot compress MDD without
  destroying Sharpe. Candidate as experiment-5 pre-registration:
  BTC-200d-SMA regime gate applied to trial 29's architecture.
- 2026-07-21 — glassnode / bitcoinmagazinepro dashboards on 200-DMA regime
  use: 200-day SMA is the most commonly cited macro-regime marker; positions
  entered only above 200-DMA "reduce exposure to prolonged bear markets"
  (search corroboration, not a formal paper). Testable-here: **yes as gate,
  not as signal** — implementation is one boolean per decision day
  (BTC close_t > SMA200_t on the decision bar), which fits the cs decision
  cadence and reuses candle data already loaded.
- 2026-07-21 — Zarattini/Pagani/Barbon SSRN 2025 ("Catching Crypto Trends:
  A Tactical Approach for Bitcoin and Altcoins", papers.ssrn.com/sol3/
  Delivery.cfm/5209907.pdf): daily-rebalanced Donchian breakout ensemble
  with vol-based position sizing on a BTC+altcoin universe reports
  material MDD reduction vs. buy-and-hold. Testable-here: **partially** —
  Donchian is a different SIGNAL, not a wrap on the cs book; parked as an
  alternative architecture for a later family, not the immediate next step.
- 2026-07-21 — arxiv 2601.05716 ("When the Rules Change: Adaptive Signal
  Extraction via Kalman Filtering and Markov-Switching Regimes"): argues
  crypto strategies must be regime-adaptive because parameter stability
  breaks across cycles. Testable-here: **not directly this project**
  (Markov-switching classifier is an engine-scale addition; premature
  before we have exhausted the simpler regime-gate hypothesis).

## 2026-07-22 — iteration 8 web pass (experiment-8 engineering prerequisite)

- 2026-07-22 — arxiv 2510.23150 ("Revisiting the Structure of Trend Premia:
  When Diversification Hides Redundancy", 2025-10-28): dynamic per-asset
  weighting across trend horizons via Bayesian optimization; medium-term
  band (~125d) contributes little incremental performance or diversification
  once short and long are included; a barbell of short+long trends beats
  equal-weight three-band on Sharpe and drawdown while retaining benchmark
  correlation. Testable-here: **yes as a follow-up family** — our Donchian
  ensemble already spans 10/20/55/110 (short + medium) and 20/55/110/220
  (medium + long); a barbell arm (e.g. 10+20+110+220) is a natural addition
  once the wider universe is running. Not this iteration's scope.
- 2026-07-22 — CoinAPI + Concretum practitioner notes on survivorship bias
  (coinapi.io/blog/how-to-eliminate-survivorship-bias-in-crypto-backtesting,
  concretumgroup.com/building-a-survivorship-bias-free-crypto-dataset-with-
  coinmarketcap-api/): point-in-time universe construction (include symbols
  as of the historical decision date, not the terminal snapshot) is the
  standard fix; naive "all symbols traded today" datasets inflate returns
  200–400% in crypto. Testable-here: **yes and load-bearing for exp-8** —
  UNIVERSE_EXPANSION.md already qualifies 13 symbols with staggered listing
  dates; the engine change this iteration is the mechanical prerequisite so
  each symbol participates only from its own listing day onward (no
  look-back through the pre-listing window into future returns).
- 2026-07-22 — StratBase.ai note on delisting exposure: even a qualified
  universe carries survivorship risk if the strategy silently averages over
  the intersection of dates instead of using per-symbol eligibility.
  Testable-here: **directly** — this is what the ladder-path change fixes;
  the cross-sectional path already uses the union-of-dates model.
- 2026-07-22 — Zarattini/Pagani/Barbon SSRN 2025 revisited: the paper's
  headline result rests on a survivorship-bias-free dataset covering all
  cryptocurrencies traded since 2015 (per the SSRN abstract) — the SIZE of
  the universe is central to their claim, not incidental. Testable-here:
  **yes** — our 13-symbol qualified universe is the largest exp-8 can start
  with under gate 1, and per the pre-registration will be the test corpus.

## 2026-07-23 — iteration 10 web pass (N-arithmetic weigh-in)

- 2026-07-23 — Lopez de Prado & Fabozzi SSRN 2026-03 ("The False Discovery
  Rate in Finance: Identification Failure and Search-Adjusted Estimation",
  dx.doi.org/10.2139/ssrn.6450418): argues that in strategy search, FDR
  control (not FWER/DSR alone) is the correct target once the search
  budget grows large, because DSR is a per-test null-rejection rate that
  gets more punishing with N regardless of independence structure.
  Testable-here: **partially** — our current stop condition is DSR ≥ 0.95
  AND candidates-PBO ≤ 0.05; PBO is already an FDR-adjacent measure. Load-
  bearing for THIS iteration: it validates the "every family raises every
  trial's bar" arithmetic — spending N without expected-Sharpe headroom is
  strictly negative EV under both frameworks.
- 2026-07-23 — Quanterlab foundations note on DSR (quanterlab.com/articles/
  foundations-dsr): E[max SR|null] grows as √(2·ln N) times cross-trial
  Sharpe std; for our N=101→117 step that's a ~1.5% expected-max lift
  which raises the pass bar by ~0.007 annualized Sharpe. Testable-here:
  **yes** — plugged into the arithmetic doc this iteration.
- 2026-07-23 — Zarattini/Pagani/Barbon SSRN 2025 headline mechanism
  (papers.ssrn.com/sol3/Delivery.cfm/5209907.pdf): the paper combines a
  Donchian breakout ENSEMBLE with a **volatility-based position sizing**
  step (inverse-vol / target-vol weights) — the two ingredients are
  interlocking, not additive. Testable-here: **yes** — our exp-7/exp-8 ran
  the ensemble on equal budgets; the vol-sizing arm is the untested half of
  the paper's claim and remains the only registered-evidence route left in
  the Donchian lineage. Queued to Q4 (next iteration under drift guard).
- 2026-07-23 — Poluri SSRN 2025 ("Evaluating the Performance of a Donchian
  Channel Breakout Strategy with ATR-Based Risk Management",
  papers.ssrn.com/sol3/papers.cfm?abstract_id=6272239): ATR-scaled sizing
  on Donchian entries on BTC daily materially reduces drawdown vs
  fixed-size; the mechanism is roughly "smaller risk when the channel
  itself is wide". Testable-here: **yes** as a sibling / spec of the
  SSRN-2025 vol-sizing arm — if we add a vol-sized Donchian family,
  ATR-based and realized-vol-based both belong in the same pre-registered
  grid so the family is pre-registered before it runs.

## 2026-07-24 — iteration 11 web pass (experiment-9 scoping, gate-6 pivot)

- 2026-07-24 — Zarattini/Pagani/Barbon SSRN 5209907 revisited on the
  concretumgroup.com companion page ("Catching Crypto Trends"): the
  paper's headline (Sharpe 1.58, CAGR 30%, alpha +14% vs BTC over
  Jan-2015–Mar-2025 on a survivorship-free top-20 rotational book) is
  **jointly** attributed to the Donchian ensemble AND cross-asset
  volatility-based position sizing — the mechanism is inverse-vol
  weighting scaled to a portfolio vol target, NOT per-symbol vol
  overlay. Testable-here: **yes, but the engine feature is a genuinely
  new allocation model** — cross-asset weight normalization and cap
  arm — not a reuse of the per-symbol `_apply_vol_overlay` we already
  have. Load-bearing for the exp-9 scoping verdict this iteration.
- 2026-07-24 — Concretum Group "Position Sizing in Trend-Following:
  Comparing Volatility Targeting, Volatility Parity, and Pyramiding"
  (concretumgroup.com/position-sizing-in-trend-following-...): three
  named methods differ in whether normalization is per-symbol vs
  cross-asset and whether pyramiding is allowed; the trend-following
  results the paper cites (60% monthly hit rate, healthy Sharpe over
  1980–2024) use vol-targeting = cross-asset scale-to-portfolio-vol,
  which matches SSRN 5209907's arm. Testable-here: **yes** — if
  experiment 9 lands, the grid must pre-register vol-parity vs
  vol-targeting explicitly (they are distinct research questions).
- 2026-07-24 — Alvarez Quant Trading "Inverse Volatility Position
  Sizing" (alvarezquanttrading.com/blog/inverse-volatility-position-
  sizing/): concrete formula = per-asset weight ∝ 1/σ_i normalized so
  ∑w = 1; cap arm typically 25% per asset. Testable-here: **yes**;
  the SSRN top-20 book keeps ~5% per name under this rule, but our
  13-symbol universe needs a cap in {1/N, 0.25, 0.50} to stop BTC
  from dominating when altcoin vols spike. Belongs in the exp-9 grid.
- 2026-07-24 — Bloomberg "Cryptocurrency Volatility Target Indices"
  spec (assets.bbhub.io/professional/sites/10/Bloomberg-Vol-Target-
  Specs_Crypto.pdf, 2025-08-05): institutional cash-vs-crypto vol
  target indices; the mechanism scales to underlying-only for
  long-only mandates, matching our product law. Testable-here:
  **not directly** — index construction rules add rebalance bands and
  fee accruals we would not want to import — but the vol targets in
  common use (10% / 15% / 25%) anchor a reasonable grid range for
  our exp-9 target-vol arm.

## 2026-07-25 — iteration 12 web pass (gate-6 evidence + holdout hygiene)

- 2026-07-25 — Bybit Q1 2026 spot execution analysis via TradingView
  news feed (tradingview.com/news/chainwire:ee08acbdf094b:0-...):
  reference-order US$10k BTC spot slippage measured 0.01 bps on Bybit
  vs 0.02–0.06 bps on peer venues, with the RPI mechanism accounting
  for the improvement. Testable-here: **yes as a sanity anchor** —
  our current gate-6 baseline of median 0.00 bps BTCUSDT / 0.05 bps
  ETHUSDT (`data/runtime/events.jsonl`) is inside the same
  order-of-magnitude band as an institutional publication, i.e. our
  spread capture is not obviously miscalibrated; nothing to add to
  a family grid, everything to add to the gate-6 rehearsal note.
- 2026-07-25 — QuantMedia "Slippage and Latency Modeling: Realistic
  Backtesting in Python" (quantmedia.io/paper-slippage-latency-
  modeling.html): backtest engines that use mid-quote fills overstate
  Sharpe by 0.5–1.0 versus a decision-to-fill model that includes
  spread crossing + market-impact (square-root law) + stochastic drift
  during the latency window. Testable-here: **yes, defensively** —
  the specific number our `configs/costs/` cost model already books
  (~20 bps round-trip vs a 37.5–45 bps gate-6 cap) implicitly assumes
  the drift term is small; already-recorded `exec_quote` events make
  the arithmetic a query away, not a new family. Belongs in gate-6,
  not in trials.
- 2026-07-25 — Turbine blog "Why Your Backtest Said +20% But Live
  Trading Lost Money" (turbinefi.com/blog/why-backtests-lie-prediction-
  market-overfitting-2026): argues live-vs-backtest divergence on
  paper-trading books is dominated by (a) stale-side fills the backtest
  assumes are mid, and (b) selection bias from picking the "best"
  backtest out of many. Testable-here: **yes and both are already
  gated** — (a) is what decision→capture drift in the runtime quote
  stream is for (queued gate-6 work), (b) is exactly what the DSR
  deflation + PBO framework corrects for. Reinforces the
  no-new-families standing decision at margin 0.0001.
- 2026-07-25 — VARRD "Out-of-Sample Testing in Trading — The Sacred
  One-Shot" (varrd.com/guides/out-of-sample-testing.html): explicit
  restatement of the one-shot protocol — a holdout that gets peeked
  at, tweaked against, or re-tested is not a holdout. Testable-here:
  **yes, procedurally** — matches `PRE_HOLDOUT_PROTOCOL.md` exactly;
  useful as an external anchor for the operator-facing holdout
  rehearsal note this iteration produces (nomination → freeze →
  single `--spend-holdout` run → publish, no re-runs, no
  post-hoc grid searches).

## 2026-07-26 (iteration 13) — sleeve-independence external evidence

- 2026-07-26 — Man Group "A Trend Following Deep Dive: Cash (Equities)
  Is King" (man.com/insights/trend-following-cash-is-king): directional,
  time-series sector trend following retains a rolling-24-month
  correlation of ~0.81 to equity-index trend over a 21-year sample.
  Cross-sectional sector trend delivers the diversification; univariate
  sector trend does not. Testable-here: **yes, defensively** — our
  crypto/Taiwan/gold sleeves are univariate trend on three markets,
  which this paper says will remain highly correlated in the tails; a
  fourth univariate sleeve is not safely assumed to be independent.
  Reinforces the P2 buy-and-hold gate before any fourth sleeve.
- 2026-07-26 — arXiv 2510.23150 "Revisiting the Structure of Trend
  Premia: When Diversification Hides Redundancy": principal-components
  decomposition of multi-market trend books shows the effective number
  of independent bets is materially lower than the number of sleeves;
  most of the risk sits on a small set of common factors. Testable-here:
  **yes, as a read-only diagnostic on the three-sleeve book** — compute
  PCA on the daily sleeve returns already recorded and report
  effective-N vs nominal N=3. Belongs in a diagnostic doc, not a new
  family.
- 2026-07-26 — Man Group "A Trend Following Deep Dive: The Dynamics of
  Dispersion" (man.com/insights/deep-dive-trend-following): 2020-2025
  window, {20d, 60d, 125d, 250d, 500d} CTA horizons — only 20d and 500d
  reached ~160 cumulative index; 60d and 125d stalled at ~120; the gap
  widened after 2022 dispersion regime. Testable-here: **yes,
  interpretively** — our Donchian ensemble is {10, 20, 55, 110} bars
  daily, straddling the underperforming 60/125-day middle. Not
  actionable as a new family (P3 refuses), but useful when the operator
  weighs a fourth sleeve at a very different horizon.
- 2026-07-26 — QuantInsti "Donchian Channels: How to Turn a Simple Idea
  Into Working Strategies" (blog.quantinsti.com/donchian-channel-
  strategy/): explicit finding that a Donchian rule tuned on one date
  range typically degrades on the next, and that the in-sample /
  out-of-sample gap is a stronger robustness signal than any single
  backtest number. Testable-here: **yes as prior anchor** — matches our
  own PBO 0.7411 and trial 118's cross-market refutation; useful to
  cite when the operator asks whether the crypto search history really
  contaminates the Taiwan/gold transfer (it does; this is an
  independent voice saying so).
- 2026-07-26 — etfdb "Alternatives ETFs Punching Above Their Weight in
  2026" (etfdb.com/equity-etf-content-hub/alternatives-etfs-punch-
  above-weight/): DBMF and CTA managed-futures ETFs took large 2026
  inflows as bond-heavy allocators diversified. Testable-here: **no,
  directly** — those are levered multi-asset futures books, not a
  spot/long-only sleeve within product law. Useful only as a market
  context note: institutional demand for trend diversification is not
  evidence that a univariate long-only spot trend rule generalizes to
  a new market, which is what our P2 gate exists to check.
- 2026-07-27 — Coin Bureau "How to Backtest a Crypto Strategy in 2026"
  (coinbureau.com/guides/how-to-backtest-your-crypto-trading-strategy):
  claim that **2-4 weeks of paper/shadow trading** is a typical
  practitioner threshold to separate a backtest survivor from live
  failure, and that walk-forward re-optimisation should not be
  substituted for it. Testable-here: **no, directly** — three shadow
  tracks began 2026-07-24 and are ~3 days in; the claim places a first
  honest read no earlier than 2026-08-07 and a real read closer to
  2026-08-21. Useful as a **calendar anchor** for when to stop asking
  "does the shadow track say anything yet" (answer: not before ~Aug 21).
- 2026-07-27 — QuantInsti/Altrady/LuxAlgo/PyQuantLab Donchian repostings
  (quantzee.com/crypto-trading-indicators; altrady.com/blog/crypto-
  trading-strategies/donchian-channel-strategy; luxalgo.com/blog/
  donchian-channels-breakout-and-trend-following-strategy):
  consistently reported that a 55-day Donchian mid-line trend filter
  raises BTC daily long-signal win rate from ~50% to ~55%, and that
  mid-channel exits systematically outperform reversal-band exits for
  capital preservation across BTC, gold, and equity indices.
  Testable-here: **partially, as a prior** — trial 88 already uses
  mid_channel exit and windows straddling 55, so the reported filter
  uplift matches its mechanism claim. Not a new experiment (would need
  a new family, which P3 refuses), but supports the standing answer's
  mechanism claim that the crypto edge is real even if it does not
  generalize to Taiwan or gold.


## 2026-07-28 (iteration 25)

- **Bailey & López de Prado, Minimum Track Record Length (MinTRL)** —
  via `portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-bias-
  adjustment-confidence-intervals-hypothesis-testing-and-minimum-track-
  record-length/`, `papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643`
  ("The Sharpe Ratio Efficient Frontier"), and the CRAN
  `PerformanceAnalytics::MinTrackRecord` reference
  (`rdrr.io/cran/PerformanceAnalytics/man/MinTrackRecord.html`).
  Claim: the track length needed to reject "measured Sharpe is below a
  threshold" at a given confidence, explicitly incorporating skewness,
  kurtosis and sample length. Same authors and same distributional
  machinery as the Deflated Sharpe Ratio already used in gate 4.
  Testable-here: **yes, and tested this iteration.** Applied to trial
  88's own return series (n=2676, SR_ann 1.1823, skew +0.227, kurtosis
  12.775): **MinTRL = 706 days = 2028-06-29** at 95% one-sided against
  SR* = 0; 429 days (2027-09-26) at 90%. Trial 118: 644 / 391 days.
- **Consequence, recorded as a correction rather than a finding:** the
  loop contract's stated unblock condition ("~90 days of forward rows
  ... enough to say anything at all") is wrong by roughly 8x. At 90
  forward days the annualized Sharpe standard error is 2.016, a 95%
  interval of [-2.77, +5.13]. Corrected in place in
  `AUTONOMOUS_RESEARCH_LOOP.md` the same day, per the standing
  correction duty.
- **Sources consulted and rejected as not testable-here:**
  `arxiv.org/pdf/2605.17628` (quantum-annealer portfolio optimization —
  no bearing on a long-only daily spot rule),
  `en.wikipedia.org/wiki/Deflated_Sharpe_ratio` (already implemented in
  gate 4; nothing new).

## 2026-07-28 (iteration 26)

- **Bailey & Lopez de Prado, Deflated Sharpe Ratio — the "number of
  trials" variable** — `papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551`,
  `davidhbailey.com/dhbpapers/deflated-sharpe.pdf`,
  `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`. Claim: DSR integrates
  five inputs — track length, skewness, kurtosis, the variance across
  the Sharpe ratios of all trials, and **the number of INDEPENDENT
  trials**. The standard caution is that a raw backtest count
  **overstates** search breadth, because optimizers run highly
  correlated variations of one core strategy; determining the true
  independent count requires precise recording of all historical
  backtests. Testable-here: **yes, and used this iteration as a
  counterweight against our own finding.** This program uses the raw
  registry count by deliberate choice (`run_gate_report.py:188`,
  "Conservative: raw registry count, no correlation shrinkage"). Its 133
  rows are heavily correlated — mean pairwise 0.628 across nine distinct
  architectures, and 64 of 133 are one cs-momentum lineage — so a
  correlation-adjusted N would be materially below 133 and would give
  trial 118 more margin than the one-trial figure measured today.
  Recorded in `GATE4_FRAGILITY_2026-07-28.md` as a real counterweight
  **and** as a fix that is refused, because adopting it now would be
  changing a gate input after seeing the answer it produces — the same
  move already refused over gate 3.
- **Consulted, not usable here:** `arxiv.org/pdf/2603.20319`
  ("Implementation Risk in Portfolio Backtesting") — quantifies error
  from implementation choices rather than selection bias; relevant to
  Test 1 of the forward-track read rule but not to the trial count.
