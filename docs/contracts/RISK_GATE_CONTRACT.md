# Risk Gate Contract

Status: Core MVP Goal H contract

## Purpose

The risk gate is the only Core MVP component allowed to approve a virtual order intent before paper execution.

It evaluates caller-provided public-market, account, position, and risk-state facts. It does not fetch data, submit orders, mutate ledger state, or call any private API.

## Inputs

The risk gate accepts:

- an `OrderIntent`
- risk-local parameters
- risk-local public exchange filters
- current position for the symbol, if any
- virtual account snapshot
- latest public market-data timestamp
- decision timestamp
- earliest legal execution timestamp
- caller-owned drawdown, daily-loss, account-stop, and trailing-stop state

`src/risk` must not import `src.config`, `src.data`, `src.portfolio`, `src.execution`, `src.accounting`, `src.backtest`, `src.runtime`, `src.api`, `src.monitoring`, or `scripts`.

## Outputs

The risk gate returns a `RiskDecision` with one of:

- `APPROVED`
- `REJECTED`
- `PAUSED`
- `STOPPED`

Every non-approved decision must include at least one reason code.

Approved decisions include `RISK_APPROVED`.

## Required Checks

Goal H checks:

- no short exposure
- no negative quantity
- sell cannot exceed holdings
- stale-data rejection or pause
- no same-bar execution
- configured minimum notional
- exchange filter checks
- exchange minimum notional
- drawdown pause
- daily loss pause
- account stop
- trailing stop

Missing or incomplete exchange filters make a symbol untradable.

## Pause And Stop Rules

Pause conditions block new buys and other risk-increasing actions.

An otherwise valid risk-reducing sell may remain approved during stale-data, drawdown, daily-loss, or trailing-stop pauses.

Account stop is a full account halt. It blocks all virtual orders.

## Broker Boundary

Goal H makes the bypass contract explicit:

```text
The Goal I paper broker must accept only an APPROVED risk decision for the same OrderIntent before it can create or process a virtual order.
```

The domain `VirtualOrder` structure enforces this approved-risk-decision requirement, so broker code cannot construct a virtual order from a raw `OrderIntent` alone.

Goal I remains responsible for implementing and testing broker-level enforcement.

## Forbidden

This contract does not authorize:

- real orders
- private exchange API
- real account access
- live exchange kill switch
- VaR
- advanced portfolio risk model
- paper broker implementation
- accounting ledger implementation
