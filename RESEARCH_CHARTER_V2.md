# The Darkest Hour research charter — v2 causal ranker

## Why v2 exists

The v1 raw-strength selector did not beat random selection inside the eligible
universe. The best v1 design book (`compression_breakout`, 2% stop) had a
39.19% win rate, 22.10R drawdown and `p_random_ge_top=0.612`. It therefore
failed before internal validation.

## Frozen v2 primary experiment

- Signal family: `compression_breakout`.
- Stop: 2%; take profit: 4%; structural RR: 2.0.
- Liquidity: trailing completed-bar approximate quote volume >= USD 10 million.
- Model: L2 logistic win-probability ranker.
- L2 alpha: 10.0; symbol-prior strength: 20 trades.
- Features: the fixed tuple in `darkest_hour/ranking.py`.
- Fit schedule: quarterly expanding window.
- A training label is usable only when its exit is strictly before the fold's
  fit timestamp.
- Primary entry: highest predicted win probability among simultaneous signals,
  only when predicted probability is at least 0.50.
- Portfolio: one global position; no entry on the current position's exit bar.
- Primary design scoring window: 2024-01-01 through 2025-03-31. Data in 2023
  supplies the first training window.
- V1 maximum-liquidity, logit-without-abstention and raw-strength books are
  diagnostics, not alternative ways to declare the primary test a pass.

The acceptance gate remains the gate in `RESEARCH_CHARTER.md`. In particular,
the ranker needs at least 300 forward-selected trades, >=50% win rate, PF>=1.50,
positive R in >=70% of active folds and drawdown <=10R at USD 200/R.

## Honest evidence boundary

Binance history through 2026 has already been inspected in the wider Phoenix
research programme. No part of it is a genuinely fresh market holdout. A v2
historical pass would justify only a time-forward paper test or independent
venue test; it would not authorize live trading.
