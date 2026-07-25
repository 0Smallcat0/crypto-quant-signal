# Cross-market combination — pre-registration

Status: **FROZEN on commit**. Written 2026-07-26, before any daily-resolution
computation. The monthly exploratory numbers that motivated this are
disclosed below and are NOT criteria.

## Why

Every improvement this program has produced in 140 trials came from
choosing a parameter, and two independent measurements now say that
channel is unreliable: PBO 0.7411 across distinct architectures, and a
cross-market test in which the parameter that made trial 118 the best
crypto candidate (2×ATR exit) turned negative on Taiwan 0050.

One thing survived that test. The **mid-channel** Donchian rule — crypto
trial 88's exit, untuned — is positive in BOTH markets: Sharpe 1.1821 in
crypto (2018-2025 daily) and +0.4262 on 0050 across 21 years, where it
also cut drawdown from buy-and-hold's 55.75% to 30.85%.

A combination of the same rule run in two weakly-correlated markets
performs **no selection at all**: same rule, fixed weights, no parameter
chosen per market. That is structurally different from everything that
has failed here.

## Disclosed exploratory numbers (not criteria)

Monthly-resolution, overlapping window 2018-04 → 2025-07 (88 months):
monthly correlation 0.2921; crypto sleeve Sharpe 1.103 / MDD 26.6%;
TW sleeve 0.906 / 10.5%; 50/50 blend 1.219 / 13.0%. A 30/70 TW-heavy
blend scored higher (1.261) and is **excluded from this design** because
choosing it after seeing it is the selection channel this test exists to
avoid. Monthly MDD understates true drawdown; the criteria below are
evaluated at daily resolution for exactly that reason.

## The combination rule (fixed now)

- **Sleeves**: crypto trial 88 (Donchian 10/20/55/110, mid-channel exit,
  BTC/ETH) and TW trial 23 (identical rule, 0050 adjusted). Both are
  already-registered trials in their own repositories; neither is re-run
  or re-tuned.
- **Weights**: fixed **50/50**, rebalanced monthly. No other weighting is
  evaluated.
- **Alignment**: union of calendar dates over the overlapping window. The
  crypto sleeve returns on every day; the TW sleeve returns on Taiwan
  trading days and contributes exactly 0 on Taiwan holidays, which is
  what a held position in a closed market actually does.
- **Evaluation**: daily-resolution Sharpe and maximum drawdown on the
  combined series. Monthly figures may be reported alongside but are not
  the verdict.

## Success criteria (ALL required)

1. Combined Sharpe **strictly greater than both** sleeve Sharpes over the
   identical overlapping window.
2. Combined maximum drawdown **strictly lower than the crypto sleeve's**
   over that window.
3. Both sleeves individually **positive Sharpe** in the overlapping
   window — if either is negative there, the premise "the same rule works
   in both markets" is false and the combination is a rescue, not a
   finding.

Failing any → registered as a negative and reported as such in both
repositories.

## Declared limitations (stated before the result)

- **FX is not modeled.** The TW sleeve is TWD-denominated and the crypto
  sleeve USDT-denominated; a real investor holding both carries currency
  exposure this computation ignores. The result is a local-currency
  combination and may not be described as an achievable portfolio return.
- **The overlapping window flatters the TW sleeve**: 0050 rose strongly
  over 2018-2025, and the same rule scores only 0.4262 across the full 21
  years. Any claim about the combination is a claim about this window.
- **No new registry rows.** This is portfolio-level analysis of two
  already-registered trials; it performs no backtest and registers no
  trial, so it has no DSR of its own. The selection history it inherits
  is the crypto program's N=133 search plus one pre-registered TW
  validation, and that history is not diluted by combining.
- A pass here qualifies nothing. It becomes a candidate for forward
  shadow tracking, which is the only clean evidence either program can
  still accumulate.

## Honesty clause

Weights, sleeves, window, and criteria are fixed by this document. If the
result fails, no alternative weighting, sleeve, or window may be
substituted — the recorded outcome is the negative.
