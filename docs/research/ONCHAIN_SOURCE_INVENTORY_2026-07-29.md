# On-chain data source inventory

Date: 2026-07-29 · Zero registry cost (no backtest, no trial, no strategy,
no pre-registration). This document opens a route; it does not test one.

## Why this route

All 133 registered trials use **price only**, and their mean pairwise
correlation is 0.628 — one idea written 133 ways, not 133 ideas. A 134th
price-derived variant cannot raise Sharpe enough to matter: the forward
answer date scales as 1/Sharpe^2, so reaching a six-month verdict from
today's 1.18 would need **Sharpe 2.34**, which parameter search on daily
long-only spot will not deliver.

On-chain metrics are the one genuinely different information source that
fits the product law (public data, spot, long-only, daily, no keys, no
derivatives). This inventory establishes what is actually obtainable
before anything is designed.

## Primary source: Coin Metrics community API

`https://community-api.coinmetrics.io/v4/` — **keyless, verified**, no
account, no bot-detection wall.

Daily metrics on the community tier with history covering the full
backtest window, for **both BTC and ETH**:

| Group | Metrics | BTC from | ETH from |
|---|---|---|---|
| Network activity | `AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`, `TxTfrCnt` | 2009-01-03 | 2015-07-30 |
| Exchange flows | `FlowInExNtv`, `FlowOutExNtv`, `SplyExNtv` | 2011-04-24 | 2015-07-30 |
| Miner / issuance | `FeeTotNtv`, `IssTotNtv`, `HashRate` | 2009-01-09 | 2015-07-30 |
| Valuation | `CapMVRVCur` | 2010-07-18 | 2015-08-08 |

All run to 2026-07-29. ETH `HashRate` stops **2022-09-14** — the Merge.
That the data knows this is a useful sign it is real.

### Which of these are actually new information

The point of the route is a source that is not price. Several catalog
entries fail that test and **must be excluded**, or they smuggle price
back in:

- **Price-derived, excluded:** `PriceUSD`, `PriceBTC`, `CapMrktCurUSD`,
  `ROI30d`, `ROI1yr`, `volume_reported_spot_usd_1d`, `IssTotUSD`, and
  every `...USD` flow variant (`FlowInExUSD`, `FlowOutExUSD`,
  `SplyExUSD`) — USD denomination multiplies the native quantity by price.
- **Partly price-derived:** `CapMVRVCur` is market cap over realized cap,
  so price sits in its numerator. Usable, but not a clean independent
  signal, and it must be labelled as such wherever it appears.
- **Genuinely non-price:** `AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`,
  `TxTfrCnt`, `FeeTotNtv`, `IssTotNtv`, `HashRate`, **`FlowInExNtv`,
  `FlowOutExNtv`, `SplyExNtv`**.

The native-unit exchange-flow series are the most interesting: coins
moving onto exchanges is the classic supply-pressure proxy, and it is
information price does not contain.

## Hard constraint found: a ~3 hour data lag

`AssetEODCompletionTime` records when each day's metrics are finalized.
Measured over 2026-07-20..24:

| Asset | Mean lag after the UTC day closes | Range |
|---|---:|---|
| BTC | **3.18 h** | 2.02 - 3.86 h |
| ETH | **3.02 h** | 2.81 - 3.57 h |

**This is the trap that would have invalidated everything.** The engine
decides at the 00:00 UTC bar close and fills at that same instant
(verified look-ahead-free in `GATE6_BASELINE_2026-07-25.md`). On-chain
data for that day **does not exist yet at that moment.** Using day D's
on-chain values to trade at D's close is look-ahead, full stop.

Any design on this route must therefore either

1. **lag every on-chain input by one full day** — use day D-1's finalized
   metrics for the day-D decision — or
2. move execution to roughly **04:00 UTC or later**, which changes the
   live runtime's schedule and is an operator decision.

Option 1 costs nothing and stays inside the current product. It should be
the default, and it must be written into the pre-registration **before**
any run rather than discovered afterwards.

## The dual-source discipline does not transfer, and that matters

`scripts/ingest_public_ohlcv.py` and its Taiwan counterpart require two
independent sources to agree within tight bounds (>=99% of sessions
present, <=0.5% close gap). That works for prices because "BTC closed at
X" is unambiguous.

**It does not work for on-chain metrics.** Second source tested:
`api.blockchain.info/charts/n-unique-addresses` — free, keyless, BTC
only. Compared against Coin Metrics `AdrActCnt` over 2018-03-05 ..
2025-07-01, **1337 overlapping days**:

| Comparison | Result |
|---|---|
| Level ratio (CM / blockchain.com) | median **1.391**, range 1.141 - 2.548 |
| Correlation of **daily changes** | **+0.8729** |

Levels are 39% apart at the median and 155% apart at worst — the existing
gate would reject this instantly. But daily *changes* correlate at 0.87,
so both measure the same underlying phenomenon through different
definitions (what counts as "active", senders only versus senders and
receivers, dust filtering, and so on).

**On-chain metrics are provider-specific constructions, not
observations.** The honest adaptation, to be fixed in a pre-registration
before any run:

- validate on **change correlation** against a declared floor, not on
  level agreement;
- record the **exact metric definition and provider** with every series,
  since the number is meaningless without them;
- treat cross-provider level differences as expected, not as a fault.

## Coverage asymmetry, recorded in advance

blockchain.com covers **BTC only**; Etherscan requires an API key. So
under any dual-source rule **ETH on-chain would be single-source**. That
asymmetry must be declared now, not discovered when ETH results differ
from BTC results.

And the most interesting family — **exchange flows — cannot be
cross-validated at all**, because every provider derives it from its own
private exchange-address labelling. Two providers disagree by
construction. Any exchange-flow work is single-source Coin Metrics and
must say so.

## What this document deliberately does not do

No strategy, no hypothesis, no pre-registration, no trial, no backtest,
no change to `configs/runtime/`, no touching of the holdout. The next
step, if the operator proceeds, is a frozen pre-registration fixing the
metric set, the one-day lag, the cross-source rule, and the pass criteria
**before** any data is fitted.

## Cost of proceeding, stated plainly

Opening this route registers new trials, and trial 118's gate-4 pass
fails at N=134 (`GATE4_FRAGILITY_2026-07-28.md`). That pass is worth
little — it holds only for a search that has permanently stopped, and
gate 3 rejects every trial regardless — but the trade is real and should
be made knowingly rather than by accident.

## Method note

Every number here was produced by querying the live APIs, not from
recollection: the keyless access, the catalog coverage and start dates,
the completion-time lag, and the 1337-day two-source comparison. No data
was written to disk and no ingestion script was created.
