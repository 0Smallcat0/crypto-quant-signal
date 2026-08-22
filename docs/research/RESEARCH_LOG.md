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

## 2026-07-28 (iteration 27)

- **Lopez de Prado, methods for the effective number of independent
  trials** — `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`,
  `risklab.ai/research/backtesting/testing_set_overfitting`,
  `paperswithbacktest.com/course/deflated-sharpe-ratio`. Claim: three
  named techniques cluster correlated strategies to recover K
  independent trials — **ONC (optimal number of clusters)**,
  **hierarchical clustering** (a conservative lower bound for N), and
  **spectral methods** on the correlation matrix eigenvalue
  distribution. The full procedure does not stop at a smaller N: it
  forms inverse-variance-weighted aggregate returns per cluster,
  computes an aggregate Sharpe for each of the K independent trials, and
  takes **the variance across those K Sharpes**. Testable-here:
  **yes in principle, deliberately NOT run.** Both gate-4 inputs would
  change and the variance across K cluster aggregates can be larger or
  smaller than across 133 individual trials, so the net effect on trial
  118's 0.950140 is unknown — and choosing among three methods after
  seeing that margin is exactly the post-hoc move that would void the
  answer. Recorded in `GATE4_FRAGILITY_2026-07-28.md` as an
  operator-declares-first item.
- **Consequence found in our own frozen contract, not in the
  literature:** `VALIDATION_GATE_CONTRACT.md` gate 1 line 44 already
  mandates correlation-adjusted `effective_N` with the method recorded,
  and line 75 lists `effective_N` as a gate-4 input. The implementation
  passes the raw count (`run_gate_report.py:190`). This corrects
  iteration 26's claim that adopting effective-N would be a rule change
  — it is the frozen rule; the raw count is a conservative deviation
  from it.

## 2026-07-28 (iteration 28)

- **Benchmark appropriateness criteria** —
  `auroratrainingadvantage.com/finance/investment-management/performance-measurement-benchmarks/`,
  `m1.com/blog/benchmarks-why-choosing-the-right-one-matters/`,
  `assetvantage.com/blogs/portfolio-comparison-against-benchmark/`.
  Claim: a valid benchmark must be measurable, investable,
  **appropriate** (aligned with the portfolio's actual investment
  universe, strategy and constraints), reflective of current investment
  opinion, and **specified in advance**. A frequent error is choosing a
  benchmark by convenience rather than appropriateness — the cited
  example is judging a US large-cap portfolio against a global index.
  Outperformance against a mismatched benchmark reflects universe
  differences, not skill. Testable-here: **yes, and it convicts this
  program's own headline sentence.** Trial 88 trades BTC/ETH; the
  13-coin equal-weight benchmark is neither appropriate to its universe
  nor specified in advance for it. Corrected in
  `VS_BUY_AND_HOLD_2026-07-26.md` and in the contract standing answer.
- **Survivorship, look-ahead and data-snooping from narrow universes** —
  `arxiv.org/html/2505.07750v1` ("The Pitfalls of Benchmarking in
  Algorithm Selection"). Claim: short horizons and narrow universes
  produce survivorship, look-ahead and data-snooping bias that undermine
  claimed improvements. Testable-here: **already recorded** — the
  13-coin universe came from a 2026 eligibility screen, so its 13.53x is
  survivorship-flattered; that caveat now travels with the corrected
  opportunity comparison rather than being a footnote.

## 2026-07-28 (iteration 29)

- **Constant-mix vs buy-and-hold, and where volatility drag comes from** —
  `aqr.com/-/media/AQR/Documents/Whitepapers/AQR_Portfolio-Rebalancing_Common-Misconceptions.pdf`,
  `returnstacked.com/the-rebalance-drag-myth-in-leveraged-etfs-what-advisors-need-to-know/`,
  `en.wikipedia.org/wiki/Rebalancing_investments`,
  `caia.org/sites/default/files/dynamic_strategies_for_asset_allocation.pdf`.
  Claim: constant-mix is a **concave** strategy that outperforms in
  oscillating markets and underperforms buy-and-hold in trending ones;
  the drag itself "arises from the interplay of volatility and
  compounding, not from rebalancing", and rebalancing changes expected
  growth only through its effect on portfolio variance. Testable-here:
  **yes, and used to audit our own headline metric.** The
  exposure-matched twin in `analyze_timing_value.py:139` is a
  continuously-rebalanced constant mix. This window trended (benchmark
  6.0510x), so the literature predicts the constant-mix twin should lose
  to an un-rebalanced fraction twin — measured, it is the other way by
  4.1% (3.03x against 2.9121x), which makes the twin actually used the
  **more conservative** of the two. Either way the edge is 4.71 or 4.90,
  so the headline is not a rebalancing artefact.
- **Consequence recorded in `TIMING_VALUE_2026-07-27.md`** as a closed
  route, together with a second refuted attack: per-symbol mean weights
  read from the trial-88 report are BTC 0.2006 / ETH 0.1780, a 53/47
  split against an equal-weight 50/50 benchmark, so the edge is not
  BTC-over-ETH selection.

## 2026-07-28 (iteration 30)

- **Implementation shortfall and why delay is directional for breakout
  systems** — `cube.exchange/what-is/implementation-shortfall`,
  `quantitativebrokers.com/blog/a-brief-history-of-implementation-shortfall`,
  `ryanoconnellfinance.com/implementation-shortfall/`,
  `markets4you.com/en/blog/market-analysis/how-to-measure-slippage-spread-and-market-impact-before-they-erode-a-winning-strategy/`.
  Claim: implementation shortfall is the gap between the **decision
  price** and the realised execution price, covering market impact plus
  delay cost. It is called out as "particularly dangerous for breakout
  traders and momentum systems", because a breakout entry is identified
  at a level and by the time the order reaches the market liquidity has
  shifted and the fill lands worse. The urgency dilemma: trading fast
  costs impact, trading slow costs delay. Testable-here: **partially,
  and it convicts an unmodelled assumption.** Trial 88 is a Donchian
  breakout whose backtest fills at the next bar's open, which in 24/7
  crypto equals the decision-bar close — i.e. **zero assumed latency**.
  Live lag is ~5 min (paper runtime) to ~20 min (shadow recorder), across
  which BTC's expected absolute move is **16.0 / 32.0 bps** against a
  modelled 5 bps slippage. The adverse *fraction* is not measurable from
  daily candles, so no cost figure is claimed — but the literature says
  the sign is against a breakout system rather than neutral. Recorded in
  `GATE6_BASELINE_2026-07-25.md`.

## 2026-07-28 (iteration 31)

- **Bitcoin intraday volatility and volume seasonality** —
  `sciencedirect.com/science/article/pii/S1059056024006506` ("Intraday
  and daily dynamics of cryptocurrency"),
  `researchgate.net/publication/334727071` ("Time-of-Day Periodicities of
  Trading Volume and Volatility in Bitcoin Exchange"),
  `quantpedia.com/strategies/intraday-seasonality-in-bitcoin`,
  `blog.paperswithbacktest.com/p/bitcoin-never-sleeps-exploiting-seasonality`.
  Claim: crypto volume and volatility are **not uniform across the day**
  — they peak during the LSE/NYSE overlap (**14:00-16:00 UTC**) and
  decline after **20:00 UTC**; the 21:00-23:00 UTC window carries the
  highest average returns. Testable-here: **yes, and it corrects our own
  previous estimate.** Iteration 30 scaled the execution-delay dispersion
  from daily sigma by sqrt(t), implicitly assuming uniform intraday
  volatility. The execution window is **00:00-00:20 UTC**, which this
  literature places in the **quiet** part of the day, so the 16 bps and
  32 bps figures are **overestimates** rather than neutral scalings.
  Recorded in `GATE6_BASELINE_2026-07-25.md`.

## 2026-07-28 (iteration 32)

- **Adaptive data analysis and indirect holdout contamination** —
  `research.google/blog/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis/`,
  `mlbenchmarks.org/04-holdout-method.html`,
  `arxiv.org/pdf/1905.12580` ("Model Similarity Mitigates Test Set
  Overuse"). Claim: the holdout's statistical guarantee assumes the k
  models were chosen **independently** of the test data; in practice
  analysts choose guided by earlier results, and "the moment a scientist
  considers a prior result on a benchmark dataset, the new model now has
  some formal dependency on the test data that invalidates the classical
  theory." The failure mode is **adaptivity** — a feedback loop between
  analyst and data — not only direct fitting. Testable-here: **yes, and
  it names a channel this program had not recorded.** No trial read the
  holdout (verified: all 133 have `data_end` 2025-07-01), but
  `analyze_whipsaw` defaults to the full series and its documented run
  spanned 2024-01 to 2026-06, crossing `holdout_start`; its verdict set
  research priority. Recorded in `HOLDOUT_INTEGRITY_2026-07-28.md` as a
  caveat that must travel with the October result rather than be
  discovered after it.

## 2026-07-28 (iteration 33)

- **Programmatic holdout enforcement — search largely unproductive, recorded
  as such.** Queried for guard-rail patterns that prevent accidental test-set
  access in data pipelines. Results were dominated by LLM guardrail tooling
  (`invariantlabs.ai/blog/guardrails`, `budecosystem.com/llm-guardrails-...`,
  AWS Control Tower) rather than ML data governance. The one on-topic hit,
  `mlbenchmarks.org/pdf/04-holdout-method.pdf`, restates that in theory a
  test set is used once and in practice that is "only sometimes the case",
  and that repeated exposure degrades the generalisation estimate.
  Testable-here: **no established pattern to copy.** Recorded so that the
  engine-level holdout guard (operator decision 2 in
  `HOLDOUT_INTEGRITY_2026-07-28.md`) is known to be a from-scratch design
  rather than an adoption. Reporting the empty result rather than padding it.

## 2026-07-28 (iteration 34)

- **Framework-level enforcement of train/test boundaries** —
  `medium.com/balaena-quant-insights/train-test-split-cross-validation-and-walk-forward-testing-for-on-chain-factors-b5fcf01572e2`,
  `insightbig.com/post/traditional-backtesting-is-outdated-use-cpcv-instead`,
  `research.mental-momentum.ai/r/backtesting-frameworks-llm-trading-bias-l1dnl5`,
  `quantstrategy.io/blog/backtesting-ai-powered-trading-systems-ensuring-robustness/`.
  Claim: leakage prevention should be enforced **at the framework level**,
  "at the architectural level rather than relying on manual
  implementation"; chronological forward-chaining splits ensure the model
  never observes future data; **purging** removes observations adjacent to
  the split boundary. Testable-here: **yes, and it vindicates the codebase
  against our own iteration-32 claim.** `run_registered_backtest` trims
  every non-spend run to `close_time < holdout_start` before the engine
  sees a candle — architectural enforcement, exactly the recommended
  pattern. Purging is not applicable here: this is a chronological
  walk-forward boundary, not a cross-validation split, and the
  qualification run deliberately keeps pre-holdout history so indicators
  with up to 110-day lookbacks are computable at the holdout's first day.
  CPCV purging is already used separately in gate 3.

## 2026-07-28 (iteration 35)

- **Stopping rules for a research programme — search largely off-target,
  recorded as such.** Queried for when to stop a quantitative research
  programme on diminishing returns. Results were dominated by stop-loss
  literature (`sciencedirect.com/science/article/abs/pii/S138641811300030X`,
  `arxiv.org/pdf/1609.00869`), which answers a different question. The one
  on-point line, from
  `kevinrodonnell.com/leveraging-quantitative-market-research-to-avoid-diminishing-returns-in-product-development/`,
  is generic: diminishing returns arrive when further effort yields smaller
  increments of value and additional investment no longer justifies the
  gains. Testable-here: **no external stopping rule found to adopt**, so
  the convergence judgement in this iteration rests on the loop's own
  Step 0 criterion rather than borrowed authority. Second consecutive
  search returning little of substance; recorded rather than padded.

## 2026-07-28 (iteration 36, P1 maintenance)

- `papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565` — Han, Kang, Ryu,
  "Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market:
  A Comprehensive Analysis under Realistic Assumptions". Claim: momentum
  effects in crypto shrink materially once realistic trading assumptions
  (costs, borrowing constraints, execution frictions) are applied.
  Testable-here: **not actionable this iteration** — the queue is P1-only
  (route declared converged iteration 35). Filed for the next family
  window if the operator ever opens P3; would inform any experiment 9
  successor about cost sensitivity, not the existing frozen 133.
- `papers.ssrn.com/sol3/papers.cfm?abstract_id=4825389` — Huang,
  Sangiorgi, Urquhart, "Cryptocurrency Volume-Weighted Time Series
  Momentum". Claim: volume-weighted TSMOM in crypto shows significant
  positive returns using volume-weighted market returns. Testable-here:
  **no** — introduces a volume-weighting parameter that would be a new
  single-market family (P3-refused). Recorded so the same idea is not
  re-searched next iteration.
- Third pass on "trend/momentum in crypto forward-validated 2026" and
  "MinTRL small-sample corrections". Returned only Bailey/Lopez de Prado
  restatements already codified in the standing answer (MinTRL on trial
  88 is 706 days at 95% one-sided vs SR* = 0 = 2028-06-29, per iteration
  25). Testable-here: **already implemented**; nothing new to lift.
- **Meta-observation, recorded rather than acted on.** Three consecutive
  external-research passes have returned no directly-actionable finding
  under this repo's P1-only constraint. Same diminishing-returns pattern
  iteration 35 noted internally. Not a reason to stop Step 2 (which is
  contract-mandated), but another signal that the binding constraint is
  now forward rows, not literature.

## 2026-07-30 (iteration 38, P1 maintenance)

- `arxiv.org/abs/2602.11708` — "Systematic Trend-Following with Adaptive
  Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency
  Markets", claim: 36-month OOS on 150+ crypto pairs yields SR 2.41,
  max DD 12.7%, Calmar 3.18 via an adaptive weighting scheme.
  Testable-here: **no** — 150+ pairs is a universe expansion plus an
  adaptive allocator, i.e. simultaneously a new symbol set and a new
  parameter family. P3 refuses it, and PBO 0.7411 across four existing
  architectures says the winner of such a search would not be trustworthy
  regardless. Filed for provenance so this SR-2.41 headline is not
  chased again next iteration.
- `en.wikipedia.org/wiki/Deflated_Sharpe_ratio` + `quanterlab.com/articles/foundations-dsr`
  — DSR restatement, "DSR > 0.95 = real edge after search". No content
  beyond Bailey/Lopez de Prado 2014 already codified in the gate
  contract; specifically nothing on the fragility question raised in
  iteration 26 ("DSR pass is a property of a stopped search, not of a
  trial"). Testable-here: **already implemented**.
- Third pass on "forward validation of crypto trend rules under realistic
  costs 2026". Returned aggregator/practitioner posts (Coin Bureau,
  Vantixs, Medium/Coinmonks) and the older arXiv 2009.12155 already
  known. No new peer-reviewed finding that would displace the standing
  answer's MinTRL = 706 days on trial 88. Fourth consecutive iteration
  in which external literature returns nothing directly actionable under
  the P1-only queue — recording, not stopping.

## 2026-07-29 — new route opened: on-chain data

- **Coin Metrics community API** (`community-api.coinmetrics.io/v4/`) —
  **verified keyless by direct query**, no account, no bot wall. Daily
  BTC and ETH metrics covering the full backtest window: network activity
  (`AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`, `TxTfrCnt`), exchange
  flows (`FlowInExNtv`, `FlowOutExNtv`, `SplyExNtv`), miner/issuance
  (`FeeTotNtv`, `IssTotNtv`, `HashRate`), valuation (`CapMVRVCur`). BTC
  from 2009-2011, ETH from 2015. Testable-here: **yes — this is the first
  genuinely non-price information source available to the programme.**
- **Constraint discovered before any design, not after:**
  `AssetEODCompletionTime` shows each day's metrics finalize **~3.1 h
  after the UTC day closes** (BTC 3.18 h, ETH 3.02 h). The engine decides
  and fills at 00:00 UTC, so using day D's on-chain data for a day-D
  decision would be **look-ahead**. Every on-chain input must be lagged
  one full day, or execution moved past 04:00 UTC.
- **The programme's dual-source gate does not transfer.** Against
  `api.blockchain.info/charts/n-unique-addresses` (free, keyless, BTC
  only) over 1337 overlapping days: level ratio median **1.391** (range
  1.141-2.548) but daily-change correlation **+0.8729**. On-chain metrics
  are provider-specific constructions, so validation must move to change
  correlation plus recorded definitions. ETH would be single-source, and
  exchange flows cannot be cross-validated at all — every provider uses
  its own private exchange-address labelling.
- Full inventory: `ONCHAIN_SOURCE_INVENTORY_2026-07-29.md`. No strategy,
  no pre-registration, no trial, no ingestion script yet.

## 2026-07-31 (iteration 39, P1 maintenance)

- `deepbluealpha.io/research/bitcoin-bottom-signals-2026-on-chain`,
  `zipmex.com/blog/how-to-use-on-chain-analytics-for-crypto-trading/`,
  `theledgermind.com/on-chain-metrics-bitcoin/`,
  `axeladlerjr.com/charts/bitcoin-exchange-netflow/` — practitioner
  exchange-netflow narratives: negative netflow = accumulation,
  positive = distribution; divergence-based interpretation. Cited
  headline stat: ~48,500 BTC net outflow in the 30 days ending early
  April 2026, single-day 32,000 BTC withdrawal 2026-03-07.
  Testable-here: **partially.** The metric class (`FlowInExNtv`,
  `FlowOutExNtv`, `SplyExNtv`) is in the on-chain inventory as
  genuinely non-price and single-source-only (cannot cross-validate,
  every provider uses private exchange labelling). Any hypothesis
  lock the operator issues on netflow must specify (a) which side,
  (b) which threshold, (c) how to trade the signal (long-only spot,
  no shorting), (d) the D-1 lag rule. No peer-reviewed backtest with
  realistic two-sided costs found; practitioner sources are all
  narrative.
- `mdpi.com/2227-9091/14/3/51` — "Enhancing Bitcoin Trading Signal
  Prediction in Crisis Periods Using an Improved Machine Learning
  Approach" (Risks 2026, vol. 14 iss. 3). Uses ML on crisis-period
  features to predict entry/exit. Testable-here: **no** — an ML
  approach is a parameter family expansion (P3 refuses), the paper's
  own scope-of-validity is crisis periods (a regime-selected sample,
  not out-of-sample), and no realistic two-sided cost audit is
  reported. Adds nothing directly usable.
- `arxiv.org/pdf/2606.00071` — "Bitcoin Price Prediction: Peer-
  Reviewed Evidence and Social Media Discourse" (June 2026 arXiv).
  Cited multi-regime finding: no model survives across multiple
  regimes; independent replications with different model families
  are needed. Testable-here: **no**, but useful as external
  corroboration of the standing answer's PBO/multi-family findings.
- `coinbureau.com/guides/how-to-backtest-your-crypto-trading-strategy`,
  `theledgermind.com/bitcoin-mvrv-ratio-analysis/`,
  `tradingview.com/script/czUjU1Zi-Crypto-MVRV-ZScore-Strategy-PresentTrading/`
  — MVRV Z-score backtest guides. One useful negative line from the
  Coin Bureau piece: "MVRV has only been tested across three bear
  markets, and neither MVRV nor other popular indicators has survived
  a rigorous backtest across all historical cycles as a reliable
  standalone signal." Testable-here: **partial** — MVRV
  (`CapMVRVCur`) is in the on-chain inventory but flagged as
  partly-price-derived (price sits in the numerator of market cap
  over realized cap), so any use of it must be labelled accordingly.
  No independent peer-reviewed OOS backtest found.
- **Meta-observation.** Fifth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint.
  Consistent with iterations 35/37/38's same observation. The binding
  constraint remains forward rows plus operator hypothesis authority,
  not literature.

## 2026-08-03 — iteration 40 (P1 maintenance pass)

- `arxiv.org/pdf/2209.05559` — "Deep Reinforcement Learning for
  Cryptocurrency Trading: Practical Approach to Address Backtest
  Overfitting" (10-coin test, 2022-05-01..2022-06-27 cohort spanning
  two crashes). Reported finding: less-overfit DRL agents (measured
  by their PBO-like discipline) delivered HIGHER out-of-sample return
  than more-overfit peers. Testable-here: **no** — a DRL policy is a
  parameter-family expansion and P3 refuses. Value is corroborative:
  an independent methodology confirms the standing answer's PBO
  framework as OOS-predictive rather than a formality.
- `arxiv.org/pdf/2411.06327` — "Return and Volatility Forecasting
  Using On-Chain Flows in Cryptocurrency Markets". Reported finding:
  USDT flowing INTO exchanges positively predicts BTC and ETH returns
  at multiple horizons, and negatively predicts ETH volatility at
  multiple horizons and BTC volatility at 6h. Practitioner
  corroboration: ~48,500 BTC net outflow across major exchanges in
  the 30 days ending early April 2026 (single-day 32,000 BTC
  withdrawal on 2026-03-07). Testable-here: **partially, and only
  after operator hypothesis lock.** The metric class (`FlowInExNtv`,
  `FlowOutExNtv`) is already in the on-chain inventory as genuinely
  non-price and single-source-only; the literature adds a directional
  prior (INflow positively predicts return — counterintuitive vs the
  retail "coins leave exchanges = bullish" narrative) but does not
  fix N-budget, threshold, or cost-audit path. P3-blocked pending
  operator scope.
- `portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-*` and
  `stratbase.ai/en/blog/walk-forward-analysis-guide` — MinTRL and
  walk-forward canonical references. Two lines relevant to the
  standing answer: (i) MinTRL is defined against a specific null
  Sharpe and confidence — the 706-day figure for trial 88 at SR* = 0,
  95% one-sided is the textbook computation, not a bespoke bar;
  (ii) Quantpedia-cited OOS gap across published strategies is ~33%
  mean / ~44% median Sharpe degradation, corroborating the standing
  answer's caveat that the 5.4% margin over the naive benchmark is
  not enough. Neither line changes the standing answer; both belong
  on file so a future audit sees the numbers are aligned with
  external norms.
- **Meta-observation.** Sixth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint.
  Consistent with iterations 35/37/38/39. Item (ii) is the first
  literature-side entry with a genuine testable prior for the
  on-chain route (directional exchange-flow) — recording it here so
  that when the operator issues a hypothesis lock, the pre-reg has an
  external reference rather than being invented from scratch.

## 2026-08-03 — iteration 41 (P1 maintenance, TW ingest root cause)

- arXiv **2602.11708**, "Systematic Trend-Following with Adaptive
  Portfolio Construction: Enhancing Risk-Adjusted Alpha in
  Cryptocurrency Markets" (AdaptiveTrend). Claim: rule-based
  trend-following on crypto **perpetual futures**, 150+ pairs,
  36-month out-of-sample window 2022-2024, annualized Sharpe 2.41,
  max drawdown -12.7%, Calmar 3.18, beating TSMOM and equal-weight
  buy-and-hold; robustness section covers parameter sensitivity,
  transaction costs and regime decomposition. Testable-here:
  **no.** Product law binds this project to spot, long-only, daily,
  two-sided costs; perpetual futures bring leverage, shorting and
  funding-rate carry, none of which this engine models or is
  permitted to trade. Recorded because a 2.41 headline on a market
  this project cannot access is exactly the kind of number that
  invites goalpost drift — it is not comparable to trial 88's 1.1823
  and must never be cited as evidence about this program.
- arXiv **2510.23150** / SSRN 5665752, Etienne, Ohana, Benhamou et al.,
  "Revisiting the Structure of Trend Premia: When Diversification
  Hides Redundancy". Claim: equal-weighting trend horizons assumes
  every asset benefits equally from every horizon, which is
  empirically suboptimal; the medium-term (~125-day) horizon "adds
  little distinct information" and overlaps its neighbours; a
  **barbell** of short- plus long-term horizons captures most of the
  performance, and dropping the mid horizon modestly **lifts** Sharpe
  and improves drawdown. Testable-here: **mechanically yes, and
  refused.** This project's ensemble is a four-window equal-weight
  Donchian at windows 10/20/55/110 — close to the structure the paper
  says carries redundancy, and "drop 55" is a one-line arm. It is
  refused on two independent grounds: (a) queue **P3** bars new
  single-market parameter families, and this is a wrapper re-sweep of
  the kind `N_ARITHMETIC_2026-07-23.md` already ruled out; (b)
  `GATE4_FRAGILITY_2026-07-28.md` measured that a 134th trial
  preserves trial 118's DSR pass only if its Sharpe lands inside
  **[0.709, 1.180]**, so an arm that *worked* as the paper predicts
  would land above that band and **destroy the only gate-4 pass the
  program has**. Filed as a named, deliberately-unrun hypothesis so a
  future audit sees the refusal was priced, not overlooked.
- arXiv **2603.20319** / SSRN 6443898, Yin, Miki, Lesnichenko, Gural,
  "Implementation Risk in Portfolio Backtesting: A Previously
  Unquantified Source of Error" (2026-03-19). Claim: the same logical
  strategy run through five independent open-source engines diverges
  purely from implementation; 15 strategies x 30 stratified buckets
  (180 S&P 500 names) x 4 cost regimes. Key result: **at zero cost
  all five engines agreed exactly (max divergence 0.000%)**, isolating
  **transaction-cost implementation** as the sole source of
  disagreement; the authors propose engine sensitivity, an
  implementation-uncertainty interval, a divergence amplification
  factor and a conclusion stability index, and conclude multi-engine
  comparison is the most effective diagnostic. Testable-here:
  **no under P1**, but it names an uncertainty this program has never
  measured. Every headline number here (14.26x, Sharpe 1.1823/1.2413,
  the 4.70x twin edge) comes from **one** engine, and this is a
  cost-intensive daily strategy with two-sided costs — the exact
  regime where the paper finds divergence is material. Honest status:
  a **known-unquantified** error source, added to the caveat list.
  It cannot manufacture an edge, only widen the interval around one,
  so it does not change the standing answer's direction.
- `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`, Bailey & López de
  Prado (SSRN 2460551), and secondary explainers. Claim: DSR adjusts
  the rejection threshold by trial count, skew and kurtosis; "the
  more configurations you tried, the higher the bar the winner has to
  clear", and the expected maximum Sharpe across many zero-edge
  trials is well above zero. Testable-here: **already applied.**
  Recorded as external corroboration that iteration 26's finding is
  **DSR working as designed, not a defect of this implementation** —
  a pass that survives only while the search is stopped is the
  textbook property of the statistic. Removes any temptation to treat
  the one-trial margin (0.950140 at N=133, 0.949969 at N=134) as an
  artefact to be engineered around.
- **Meta-observation.** Seventh consecutive external-research pass
  with no *actionable* finding under P1-only — but the first in that
  run to change the **caveat list** rather than only corroborate it:
  2603.20319 adds single-engine implementation risk as a named
  unquantified error source, and 2510.23150 supplies a concrete,
  priced-and-refused hypothesis (drop the mid horizon) rather than
  the usual "no directly testable rule". Both are facts about
  measurement quality; neither is evidence of an edge.

## 2026-08-15 — iteration 42 (P1 maintenance after an 11-night loop outage)

- arXiv **2607.19453**, Ayoub Jadouli, "Predictive Extrema,
  Unprofitable Policies: An AI-Assisted Audit of Candle-Based Binance
  Spot Timing Models" (submitted 2026-07-21). Claim: machine-learning
  models that predict price extrema on **Binance Spot**, daily and
  4-hour candles, **long-only**, produce **no** profitable policy once
  costs are charged — "every operational decision remains NO_TRADE" at
  **31 bps per completed cycle** (21 bps stress threshold). Recorded
  numbers: a ten-pair daily selector lost **6.72% over 19 cycles**
  (3 wins, 16 losses); a local-minimum policy returned **-1.79%**
  against an **11.11 bps** gross advantage; a local-maximum policy
  underperformed holding by **2.80%** despite a **12.21 bps**
  theoretical edge; a Gurgul-inspired model lost **44.30%** over seven
  cycles against **-41.20%** for buy-and-hold. Classification quality
  was good and useless at once — ROC AUC **0.874-0.896** with average
  precision only **0.116-0.134**. Testable-here: **not as a strategy**
  (different signal family, and P3 bars new single-market families),
  but it is the **closest external match to this project's own product
  law** yet found — same exchange, same spot venue, same long-only
  daily bar, same two-sided cost discipline — and it is a registered
  negative. Its value here is as a base rate: an independent,
  cost-honest audit of daily Binance spot timing found nothing, which
  is the prior against which this program's single gate-4 pass should
  be read. Numbers verified at arxiv.org/abs/2607.19453.
- **"Order flow and cryptocurrency returns"**, Journal of Empirical
  Finance, ScienceDirect **S1386418126000029** (online 2026-01);
  working-paper version presented at EFMA 2025. Claim: exchange
  **order flow** has economically valuable **out-of-sample**
  predictive power for crypto returns, with non-linear ML conditioned
  on order flow beating both fundamentals-conditioned ML and leading
  ML benchmarks without it; a one-standard-deviation rise in lagged
  world order flow is associated with **+0.2% daily** and **+0.9%
  weekly** returns, and the authors state the result survives
  short-selling constraints and high transaction costs — the two
  restrictions that usually kill a crypto result under this project's
  product law. Testable-here: **not yet, and not without an operator
  hypothesis lock.** It is adjacent to, but not the same as, the open
  on-chain route: this is *exchange* order flow (trades and book), not
  *on-chain* exchange netflow, and conflating the two would repeat the
  pooling error of 2026-07-26 and 2026-07-28. The data is not
  ingested here. Filed as the strongest external support so far for
  the flow family being worth an eventual hypothesis lock, **and** as
  a reminder that the lock must name which flow. **Source-access
  caveat, recorded deliberately:** the publisher page returned HTTP
  403 and the EFMA working-paper PDF failed TLS verification, so the
  numbers above come from the publisher-side abstract summary and are
  **not** verified against the paper itself. They must not be quoted
  in a result document until someone reads the PDF.
- **E-values / anytime-valid sequential inference** (Ramdas and Wang,
  *Hypothesis Testing with E-values*; Johari et al., arXiv 1512.04922
  "Always Valid Inference"; group-sequential comparisons from
  practitioner sources). Claim: e-values and always-valid p-values
  control Type I error **at any data-dependent stopping time**, so a
  monitor may look at an accumulating record continuously without
  inflating alpha. Testable-here: **relevant, and refused as a way to
  read the forward tracks early.** This is the obvious next idea once
  a 706-day MinTRL is on the books (iteration 25), so it is priced
  here before anyone proposes it: anytime-validity buys *permission to
  look*, not *evidence*. It does not reduce the data needed to
  separate SR = 1.1823 from SR = 0; against a fixed-sample test at the
  same date it is strictly **less** powerful, because the flexibility
  is paid for in power. Adopting it would move the honest verdict date
  **later than 2028-06-29, not earlier**. What it could legitimately
  buy is the right to monitor the three shadow tracks continuously
  without the alpha-spending problem that
  `FORWARD_TRACK_READ_PREREGISTRATION.md` currently solves by freezing
  the read to four rows — a governance simplification, not a
  scientific shortcut, and one that would itself have to be
  pre-registered before any row is read under it.
- **Meta-observation.** Eighth consecutive external-research pass with
  no actionable finding under P1-only. This one is the first to supply
  an external **base rate** (2607.19453: an independent cost-honest
  audit of daily long-only Binance spot timing found nothing
  tradeable) rather than only method caveats, and the first to
  pre-refuse a shortcut around the 2028 verdict date. Neither is
  evidence of an edge; both narrow what a future iteration may claim.

## 2026-08-16 — iteration 43 (P1 maintenance, shadow-task scheduling defect)

- **"Do trend following strategies work in Chinese futures markets?"**
  (Li, Zhang and Zhou, *Journal of Futures Markets* 37(12), 2017,
  pp. 1226-1254; abstract read at RePEc, ideas.repec.org). Claim:
  trend-following technical trading rules "yield better performance
  than the buy and hold strategy on both individual contracts and
  sorted portfolios", and the outperformance is "robust to transaction
  costs, data frequency, sub-prime crisis, shorting constraint,
  delayed execution, liquidity and parameters". The authors themselves
  add that "the profitability of the trend following strategy may be
  subject to data snooping bias". Testable-here: **no, and it is the
  wrong market anyway** — Chinese commodity *futures*, which the
  product law excludes (spot only, long-only, no leverage). Filed for
  one reason: it is the closest external analogue to this project's
  own P2 gate, which requires a candidate sleeve to beat buy-and-hold
  **in its own market**. A 2017 futures result cannot license a spot
  sleeve, and the paper's own data-snooping caveat is the same defect
  PBO 0.7411 measures here.
- **Bitcoin volatility-regime claim — checked and NOT verified.** A
  search summary attributed to State Street Global Advisors the figures
  "daily standard deviation roughly halving from approximately 5.3% in
  2021 to about 2.1% in 2024-2025". The SSGA source
  (ssga.com, *Bitcoin volatility and liquidity: key trends for
  investors*, published 2026-02-03) was fetched and **contains no such
  numbers**: it reports two-year rolling windows of weekly returns and
  states only, qualitatively, that "BTC volatility has evolved since
  its inception and has been trending downward over time". The S&P
  Global piece that may carry the figures returned HTTP 403.
  **Therefore the 5.3%/2.1% pair must not be quoted anywhere in this
  project.** Recorded because the underlying question is real and
  directly relevant: this program's entire measured edge comes from
  2018-2025, and a Donchian breakout rule's value depends on the
  volatility and trend-persistence regime it is run in. Testable-here:
  **yes in principle** (the repo holds the daily candles), but not run
  — under the Step 0 hard limits a realized-volatility-by-era chart
  would be a diagnostic that does not change the standing answer or
  close a route. It is filed as a candidate for the first iteration
  that has a decision attached to it, e.g. an operator question about
  whether the 2018-2025 measurement should be re-weighted.
- **AdaptiveTrend (arXiv 2602.11708) re-encountered, not re-filed.**
  It surfaced again as the top result for crypto time-series momentum
  net of costs. Already recorded under iteration 41; the H6
  (six-hourly) rebalance at the core of its Sharpe 2.41 is outside the
  product law's daily frequency, so nothing changes. Noted only so a
  future reader does not count it twice.
- **Practitioner claim that daily rebalancing is cost-dominated.**
  Several 2026 practitioner sources assert weekly or threshold-based
  rebalancing beats daily for long-only crypto books because daily
  turnover costs exceed the benefit. Testable-here: **already
  answered internally and in the opposite direction for this rule** —
  the Donchian ensemble is not a daily *rebalance*, it is a daily
  *decision* that changes exposure only on channel events, and the
  measured execution-latency and cost work (about -6.4 bps round trip,
  bounded above by ~17 bps) is inside tested headroom. Filed as a
  reminder that "daily" in practitioner writing usually means daily
  turnover, which this book does not do. No action.
- **Meta-observation.** Ninth consecutive external-research pass with
  no actionable finding under P1-only. The one genuinely new thing this
  pass produced is negative and about method: a widely-repeated
  Bitcoin volatility statistic failed source verification, and is now
  banned from this project's documents rather than absorbed into them.

## 2026-08-19 — iteration 44 (P1 maintenance, two missed slots explained)

- **Gueta Quant, "Gueta Research #001", pre-registered funnel of 13
  simple strategies on EURUSD daily, 2020-01..2025-12 (in-sample
  2020-2023, out-of-sample 2024-2025).** Headline: **13 -> 0**. Eight
  passed gate 1 (OOS return > 0 and Sharpe > 0 at 2 pips), seven passed
  gate 2 (walk-forward cumulative return > 0), and **zero** passed gate
  3 (Deflated Sharpe Ratio >= 0.95) or gate 4 (PBO). Their PBO came out
  at 0.5639 via CSCV with 16 blocks and 12,870 combinations, family
  N=14. Their **Breakout Channel** arm returned +1.52% OOS and +16.05%
  walk-forward and still scored **DSR 0.062**. Testable-here: **no** —
  EURUSD spot FX is outside this project's product law. Filed anyway
  because it is the closest external analogue yet found to this
  program's own apparatus: an independent group, pre-registering, using
  the **same two deciding gates at the same DSR >= 0.95 threshold**, on
  a different market, rejected every candidate. That is independent
  corroboration of iteration 27's finding that gates 3 and 4 reject
  nearly everything, and it makes this project's single pass — trial
  118 at DSR 0.950140, a margin of exactly one trial (iteration 26) —
  look more like a property of a stopped search than less. It does not
  change the standing answer; it hardens one clause of it.
- **Momentum-decay literature, second look, still not actionable.**
  Several 2025-2026 sources (a comparative time-series vs
  cross-sectional momentum study in crypto; Grayscale's 2026 digital
  asset outlook; Springer's *Cryptocurrency momentum has (not) its
  moments*) converge on a qualitative claim: time-series and
  cross-sectional crypto momentum have **compressed toward similar,
  modest positive returns** as the market institutionalized post-2021,
  with BTC/ETH trading more as macro-sensitive instruments than as
  reflexive crypto assets. Testable-here: **yes in principle** — it is
  the same regime question raised in iteration 43 by the failed State
  Street volatility claim, and it bears directly on whether a
  2018-2025 measurement transfers. Still **not run**, for the same
  Step 0 reason: an era-split of the backtest is a diagnostic with no
  decision attached to it, and P3 forbids the family re-run that would
  give it teeth. Recorded now as the **second independent arrival** at
  the same question; a third should be treated as a signal that the
  operator ought to be asked whether to attach a decision to it.
- **Minimum-track-record-length sources re-checked; iteration 25's
  arithmetic stands.** Bailey and Lopez de Prado's DSR/PSR framework —
  and the Portfolio Optimizer write-ups of MinTRL — restate that the
  required track length "can substantially exceed typical evaluation
  windows", which is exactly the 706-day (2028-06-29) figure this
  project computed for trial 88. Also encountered: a practitioner rule
  that a forward test "is statistically valid when it reaches at least
  100 trades with no rule changes". **Not adopted.** A trade count is
  not a substitute for MinTRL — it ignores Sharpe, skew and kurtosis,
  all three of which drive this book's 706 days (SR 1.1823, skew
  +0.227, kurtosis 12.775) — and adopting a laxer forward-read rule
  after freezing a stricter one is precisely the goalpost move
  `FORWARD_TRACK_READ_PREREGISTRATION.md` exists to prevent. Logged so
  that a future iteration meeting the 100-trade rule cannot mistake it
  for permission to read return early.
- **arXiv 2512.22476 (AutoQuant) surfaced, not filed.** Auto-tuning
  under execution constraints for crypto **perpetual futures** — out of
  product law (spot, long-only), same disposal as AdaptiveTrend.
- **Meta-observation.** Tenth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint. Unlike
  the previous nine, this one produced a result that touches an
  existing conclusion: the Gueta funnel is the first outside evidence
  about how the DSR-plus-PBO pair behaves when someone else runs it
  honestly, and it points the same way this program's own gate-4
  fragility measurement does.

## 2026-08-21 — iteration 45 (P1 maintenance, backtest-to-live transfer measured by outsiders)

- **Liu (2026), "Evaluating Structured Strategy Backtests: Peer
  Benchmarks, Regime Timing, and Live Performance", arXiv 2604.18821,
  20 Apr 2026 — the largest measurement yet of the exact transfer this
  program cannot make.** 1,726 commercially distributed structured
  strategies from ten global institutions, 2009-2025, each with a
  marketed pro-forma record and a subsequent live record. Verified by
  extracting the PDF text, not from the search summary. Numbers: mean
  volatility-adjusted return over the twelve months **before** launch
  is 4.1% p.a. against **1.0%** live, a decay of −3.1pp (p<0.01); at
  six months 3.6% against 1.5%, −2.1pp (p<0.01). The regression of
  live on pro-forma performance gives **β̂ = 0.137 (R² = 0.148,
  N = 1694)** in raw returns, but **0.025 (R² = 0.032)** once the
  dependent variable is Jensen α against an external Bloomberg index
  and **0.034 (R² = 0.054)** against a leave-one-out peer average —
  reductions of about **81% and 75%**. Median live underperformance is
  0.8pp p.a. against LOO peers and 3.0pp against the external index at
  twelve months, with **59% of strategies negative** on both. The
  authors' reading: marketed backtests "predominantly reflect the
  common factor regime present before launch rather than strategy-
  specific skill", and the discount should grow when launch follows an
  extreme factor run. **Testable-here: no** — it is not a strategy
  hypothesis and nothing here can be traded. It is evidence, and it
  bears on two clauses this program already holds: that a backtest
  must be judged against a benchmark (which is why
  `VS_BUY_AND_HOLD_2026-07-26.md` exists), and that raw pro-forma
  numbers such as 14.26x carry far less information about live
  behaviour than their size suggests. **No goalpost moves from this**:
  the forward read rule stays exactly as frozen in
  `FORWARD_TRACK_READ_PREREGISTRATION.md`, and Liu's regime-timing
  finding is recorded as a prior, not as a reason to run an
  era-extremity diagnostic on the 2026-07-24 launch date.
- **Mroziewicz and Ślepaczuk (2026), arXiv 2602.10785, 11 Feb 2026 —
  an independent walk-forward crypto study whose own headline table
  loses to buy-and-hold.** University of Warsaw; **spot** BTC, ETH and
  BNB; EMA-crossover, long-short, intraday bars (1 to 60 minutes);
  0.1% per transaction with sensitivity from 0.05% to 0.50%; training
  2018-02-08..2019-09-01, unseen out-of-sample 2019-11-07..2021-08-22;
  81 training/testing window pairs optimized by walk-forward, with the
  top two carried to a single unseen evaluation. Unseen-period Sharpe,
  strategy against buy-and-hold: BTC **1.1064 vs 1.1281**, ETH
  **1.3371 vs 1.5365**, BNB **1.1982 vs 1.4644** — the benchmark wins
  all three, despite annualized returns of 90.91%, 137.27% and 140.30%
  that look spectacular in isolation. The paper's own sentence,
  verbatim: **"No strategy surpassed the respective asset's
  Buy-and-Hold performance in terms of Sharpe ratio."** **Testable-
  here: no** — long-short and intraday both fall outside product law
  (spot, long-only, daily), so no trial follows. Filed because it is
  an independent, published, walk-forward-validated instance of the
  failure mode this program measured for Taiwan and gold: an optimized
  trend rule that produces large absolute returns and still loses to
  simply holding the asset.
- **Wiecki, Campbell, Lent and Stauth (Quantopian), "All that glitters
  is not gold", SSRN 2745220 — what survives a backtest is drawdown
  character, not Sharpe.** 888 US-equities algorithms with at least six
  months of out-of-sample performance. Verified from the PDF: the
  abstract states Sharpe ratio and similar metrics "offer little value
  in predicting out of sample performance (**R² < 0.025**)", with the
  in-sample/out-of-sample Sharpe correlation at **Pearson R² = 0.02**,
  while **annual volatility reaches R² = 0.67 and maximum drawdown
  R² = 0.34**; a non-linear model on the full feature set gets to
  R² = 0.17 on hold-out data. **Testable-here: no** (equities, and the
  finding is about metrics, not a rule). Recorded because it puts a
  number on which half of this program's own result should be expected
  to travel: **drawdown character is among the most persistent
  properties of a backtest and Sharpe rank is nearly the least.** The
  precise claim is that an algorithm's own drawdown level persists
  in-sample to out-of-sample — **not** that a drawdown advantage over a
  benchmark persists, which is a different quantity and is not what
  Wiecki measured. Under that limit it supports the clause of the
  standing answer that treats the 33.05%-against-80.99% drawdown result
  as the more durable half, and it argues against leaning on the 5.4%
  return margin.
- **ETF- and on-chain-flow commentary surveyed, nothing adoptable.**
  The 2026 market-commentary corpus (Amberdata, VanEck and similar)
  offers claims of the form "five or more consecutive ETF inflow days
  marked durable bottoms in 2026". No sample definition, no
  out-of-sample split, no cost treatment, and no paper behind it. The
  on-chain route opened in iteration 39 remains open and unadvanced;
  it still awaits an operator hypothesis lock, and this class of claim
  is not one a hypothesis could honestly be locked from.
- **arXiv 2602.11708 (AdaptiveTrend) resurfaced and stays disposed.**
  Same paper already refused in an earlier pass: 6-hour bars,
  long-short, asymmetric 70/30 allocation. Re-encountering a disposed
  source is not new evidence, and it is logged only so a later
  iteration does not count it twice.
- **Meta-observation.** Eleventh consecutive external-research pass
  with nothing directly actionable under the P1-only constraint. Like
  iteration 44's, this one still touched existing conclusions rather
  than adding routes: three independent sources — 1,726 institutional
  strategies, 888 retail algorithms, and one walk-forward crypto study
  — all say the same thing from different directions, that the part of
  a backtest that survives contact with live markets is small and is
  not the part that looks best on the page. **None of these is the
  third arrival at the momentum-regime-decay question** flagged in
  iteration 44; that trigger concerns crypto momentum compressing
  post-2021 and remains at two arrivals. Conflating the two questions
  would be exactly the loose bookkeeping the trigger exists to prevent.

## 2026-08-22 — iteration 46 web pass (P1-only; horizon redundancy inside a trend ensemble)

- **arXiv 2607.19497 (Sepp and Lucic, 21 Jul 2026), "The Science and
  Practice of Trend-Following Systems" — a closed-form theory of what a
  trend system earns, and one sentence that touches this program.**
  Verified by fetching the abstract page. The paper classifies trend
  systems into European, American and time-series-momentum types and
  derives, for the European class, an exact relationship between P&L,
  autocorrelation and drift in volatility-normalized returns; in the
  frequency domain the expected return is a Poisson-kernel reading of
  the return spectrum, so that **"trend-following alpha is excess
  spectral mass at low frequencies"** and the system profits at zero
  drift when the kernel-weighted spectral mass exceeds one. It also
  derives a closed-form Sharpe ratio, a **net** Sharpe and a
  **cost-optimal span** under trading costs, and shows the positive
  skewness of aggregated trend returns is **structural**, positive at
  every horizon and peaking near half the filter span. Empirically it
  reports that **"all TF systems are strongly correlated"** on liquid
  contracts. **Testable-here: no, and deliberately not.** The
  cost-optimal-span formula is a design rule, and using it to pick or
  re-pick a lookback would be a new single-market parameter family,
  which P3 refuses. Two things it does do without any run: it gives a
  structural explanation for the **+0.227 skew** already measured on
  trial 88's return series (a property, not a result), and its
  strong-correlation finding is about systems on a shared contract set,
  which is a **different quantity** from this program's cross-market
  sleeve correlation of −0.0041 — the two must not be conflated.
- **arXiv 2510.23150v2 (Etienne, Ohana, Benhamou, Guez, Setrouk,
  Jacquot, 28 Oct 2025), "Revisiting the Structure of Trend Premia:
  When Diversification Hides Redundancy" — layering horizons can hide
  redundancy rather than add diversification.** Universe 20 liquid
  futures across commodities, equities, rates and FX; horizons 20, 60,
  125, 250, 500 trading days; sample 2013-2025 with the formal backtest
  2015-2025; Bayesian reallocation across horizons on rolling 8-year
  training windows. Numbers below were read twice from the paper's own
  tables. Standalone Sharpe (Table 6): **20d 0.20, 60d 0.21, 125d 0.21,
  250d 0.42, 500d 0.47, all-horizons baseline 0.36**. Pairwise
  correlations (Table 5): **20d-60d 83%, 20d-125d 59%, 20d-250d 59%,
  20d-500d 44%, 60d-125d 81%, 60d-250d 60%, 60d-500d 44%, 125d-250d
  84%, 125d-500d 67%, 250d-500d 90%**. The claim is that the medium
  band adds little once short and long are included, and that optimal
  weight goes barbell rather than ladder. **A number was retracted
  during verification:** the first read reported "excluding 125d lifts
  Sharpe from 0.36 to about 0.40"; the second, targeted read found no
  such figure in the document, so it is **not recorded** and must not
  be cited later. **Testable-here: mechanically yes, and refused.**
  This program's ensemble votes over windows **10/20/55/110**, so a
  leave-one-window-out ablation is the direct analogue — but it is an
  arm of the experiment-7 family, and P3 forbids new single-market
  parameter families. Iteration 26's arithmetic makes the refusal
  sharper rather than merely procedural: a 134th trial preserves trial
  118's gate-4 pass only if its Sharpe lands in **[0.709, 1.180]**, and
  an ablation arm that behaved like the existing ensemble (trial 88 at
  1.1823, trial 118 at 1.2413) would land at or above the top edge and
  destroy the pass. Recorded as evidence, not as a route.
- **Amberdata "2026 Outlook: The End of the Four-Year Cycle" (Michael
  Marshall, 20 Jan 2026) — search summary refused after source check.**
  A search result attributed to this piece a claim that Bitcoin's
  30-day realized volatility sits at 20-30% and that the ETF-flow
  regime is eroding trend-strategy efficacy. Fetching the page found
  **no realized-volatility figure, no dated measurement and no
  statement about momentum or trend-strategy performance** — the
  nearest text is the qualitative "Volatility compresses. Interest
  fades. Then something changes." The numbers are therefore not
  recorded, and this is **not** an arrival at the momentum-regime-decay
  question, which stays at **two**. Logged as a worked example of the
  iteration-43 lesson: a search summary is not a source.
- **arXiv 2602.11708 (AdaptiveTrend) re-encountered a third time and
  stays disposed.** 150+ pairs, 6-hour bars, long-short with asymmetric
  70/30 allocation, 2022-2024, reported Sharpe 2.41 and max drawdown
  −12.7%. Outside product law on two counts. Logged only so repeated
  encounters are never counted as accumulating evidence.
- **Meta-observation — twelfth consecutive pass with nothing actionable
  under P1-only, and a new question opened at two arrivals.** Both new
  sources point at the same unexamined place, from opposite directions:
  Sepp and Lucic say trend systems are strongly correlated with one
  another, and Etienne et al. say adjacent horizons inside one ensemble
  can be near-duplicates carrying real cost. Applied here the question
  is whether **10/20/55/110 is four bets or effectively two**. It is
  tracked at **two arrivals**, on the same bookkeeping rule as the
  momentum-regime-decay question — a third independent arrival triggers
  asking the operator whether to attach a decision to it, and until
  then nothing runs. The two questions are distinct and must not be
  pooled to reach a threshold faster.
