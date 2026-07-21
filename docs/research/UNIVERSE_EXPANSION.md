# Universe expansion — 2 → 13 qualified symbols

Executed: 2026-07-21 · Task: open the cross-sectional hypothesis space
(the strongest externally-evidenced edge family still untested here, per
`docs/research/EXTERNAL_EVIDENCE_2026-07.md`), which is impossible on a
2-asset universe.

## Selection rule (mechanical, declared before fetching)

Binance Spot USDT pairs that (a) sit in the top ~15 of 2026-07 market cap
excluding stablecoins and (b) listed early enough to give ≥ 1000 pre-holdout
daily candles. Fetched via the existing public ingestion path
(`scripts/ingest_public_ohlcv.py`, data-api.binance.vision), full history
from listing, then sliced at the locked holdout boundary by
`scripts/slice_preholdout.py` (keeps candles that CLOSE before
`holdout_start`; the BTC/ETH re-slice reproduced the prior pre-holdout
files' exact row counts (2876) and last day (2025-07-01), matching the
registered trials' data_end — candle data lives outside git, so the check
is counts + boundaries + registry consistency, not a byte diff).

**Survivorship-bias declaration:** picking today's top-15 conditions on
having survived to 2026. A 2018 observer could not have known SOL would
survive and FTT would not. Cross-sectional results on this universe are
therefore upper bounds; any pre-registration built on it must state this,
and the discount is one more reason the single-use holdout — not the
in-sample family read-out — is the arbiter.

## Quality gate (2026-07-21, all 13 pre-holdout series)

Rule: ≥ 1000 pre-holdout days, zero GAP, zero DUPLICATE
(`inspect_candle_quality`, 1d spacing).

| Symbol | Pre-holdout days | First day | Gaps | Dups | Verdict |
|---|---:|---|---:|---:|---|
| BTCUSDT | 2876 | 2017-08-17 | 0 | 0 | PASS |
| ETHUSDT | 2876 | 2017-08-17 | 0 | 0 | PASS |
| BNBUSDT | 2795 | 2017-11-06 | 0 | 0 | PASS |
| LTCUSDT | 2758 | 2017-12-13 | 0 | 0 | PASS |
| ADAUSDT | 2633 | 2018-04-17 | 0 | 0 | PASS |
| XRPUSDT | 2616 | 2018-05-04 | 0 | 0 | PASS |
| XLMUSDT | 2589 | 2018-05-31 | 0 | 0 | PASS |
| TRXUSDT | 2578 | 2018-06-11 | 0 | 0 | PASS |
| LINKUSDT | 2359 | 2019-01-16 | 0 | 0 | PASS |
| DOGEUSDT | 2189 | 2019-07-05 | 0 | 0 | PASS |
| SOLUSDT | 1786 | 2020-08-11 | 0 | 0 | PASS |
| AVAXUSDT | 1744 | 2020-09-22 | 0 | 0 | PASS |
| DOTUSDT | 1779 | 2020-08-18 | 0 | 0 | PASS |

All candles close before 2025-07-02T00:00Z; the holdout year
(2025-07-02 → 2026-07-01) stays sealed for every symbol.

## Scope boundary

Research data only. The live paper contract (BTC/ETH
daily_trend_ensemble) is frozen through its observation window; nothing
here touches runtime configs. New symbols enter backtests exclusively via
`data/candles_preholdout/` until the October holdout spend.

## Next (queued for the autonomous research loop)

1. Cross-sectional momentum family pre-registration
   (`docs/research/GOALP_EXPERIMENT3_PREREGISTRATION.md`).
2. Engine work: a cross-sectional allocator path (current engine decides
   per-symbol independently; top-K ranking needs a cross-symbol step).
3. Family run + gate report at the new registry N.
