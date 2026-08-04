# The Darkest Hour research charter — v1

## Objective

Find a Binance perpetual strategy that can scan a fixed, causally eligible
universe and operate one global position with a structural 2R target and 1R
stop. The stretch target is a net win rate of at least 50% and maximum portfolio
drawdown no greater than 10% on USD 20,000.

## Non-negotiable rules

1. Signals are computed on a completed bar and become executable no earlier
   than the following bar.
2. Symbols, strategy families, parameters and acceptance rules are fixed before
   aggregate results are inspected.
3. Training labels are available only after their exit timestamp.
4. The universe uses information available before each measured period; no
   present-day survivor list may be described as historical.
5. Results include Phoenix S1 fees and slippage, an enabled funding model and an
   additional execution-cost stress.
6. Simultaneous candidates are resolved by a pre-registered selector. The v1
   operational baseline is highest trailing liquidity, not the historically
   best symbol.
7. One global position is allowed. A position may not rotate or reopen on its
   exit bar.
8. End-of-data trades are right-censored and excluded from primary performance.
9. Every reported candidate must include long/short, symbol, quarter and regime
   concentration audits.
10. The already inspected 2023–2026 Binance history is development evidence,
    not a fresh final holdout.

## Primary acceptance gate

All conditions must pass on genuinely forward outer folds and later on a new
venue or forward paper period:

- structural RR exactly 2.0 and realized RR at least 1.80 after costs;
- win rate at least 50.0%;
- profit factor at least 1.50;
- positive total R in at least 70% of active outer folds;
- annual block-bootstrap p05 greater than zero;
- maximum drawdown at the frozen risk size no greater than USD 2,000;
- neither direction supplies more than 75% of total positive R;
- top five symbols supply no more than 40% of total positive R;
- performance remains positive with 10 bps extra round-trip cost;
- minimum 300 closed outer-test trades before a research pass is possible.

Failure is a valid result. Parameters are not retuned to make a failed primary
test pass.

## Frozen v1 tournament

All families run on 5-minute bars with 1h-equivalent trend context encoded by
causal moving averages. Stops are tested as separate, declared sensitivity
variants: 1%, 2% and 3%. The primary stop is 2%; RR is always 2.

The signal families and their default parameters live in
`darkest_hour/signals.py`. Changing a default creates a new charter version.

## Deployment boundary

This repository is research-only. A successful backtest does not authorize
live trading. Paper trading and live trading require separate explicit gates.

