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

