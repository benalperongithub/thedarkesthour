# TDH V5 — Nested Direction and Managed-Exit Tournament

V4's frozen cross-sectional momentum book failed. Its long side lost money,
while its short side was weakly positive. That observation is design input,
not permission to relabel a retrospective short-only book as validation.

V5 freezes a nested quarterly procedure before inspecting any managed-exit
results. It reuses V4's causal entry candidates and chooses both direction mode
and exit policy using only trades that would have been fully known before each
outer quarter.

## Frozen candidates

Direction modes: `BOTH`, `LONG_ONLY`, `SHORT_ONLY`.

Exit policies:

1. fixed 2R target, 1R stop, 48-hour time stop;
2. fixed 2R target, 1R stop, 24-hour time stop;
3. move the stop to break-even one bar after +1R, retain 2R target;
4. after +1R, trail one R behind the best completed-bar price, 3R cap;
5. take 50% at +1R, move the remainder to break-even on the next bar, and
   target 3R on the runner.

Stop changes become active on the following bar. The original/active stop wins
every ambiguous OHLC bar. Partial exits are charged the full-position funding
duration through final exit, which is conservative.

## Nested selection

- Design history begins 2023-01-01.
- Outer tests are 2024Q1 through 2025Q1.
- Before each outer quarter, the last 48 hours are purged.
- Each of the 15 direction/exit combinations is replayed as a one-position
  historical book using only the remaining past.
- A combination needs at least 60 training trades.
- Selection score is mean net R minus one standard error. Ties are broken by
  profit factor, sample size, policy name and direction name.
- The selected combination is then used for that outer quarter only. Combined
  outer trades preserve one global position across quarter boundaries.

All V4 cost, liquidity, weekday and execution assumptions remain unchanged.
No result from an outer quarter may change a later score except after its exit
is in the past.

## Acceptance gate

The combined outer book passes only if all conditions hold after costs:

1. at least 150 trades;
2. win rate at least 50%;
3. profit factor at least 1.50;
4. positive total R;
5. maximum drawdown no greater than 10R; and
6. at least 60% of active outer quarters have positive total R.

This is still historical design evidence. A pass justifies forward paper
trading, never immediate live capital.
