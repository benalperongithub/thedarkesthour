# TDH V6 — Residual Reversal and Aggressive Flow

V1–V5 inspected event signals, causal rankers, cross-sectional momentum, and
managed exits. Those hypotheses are closed. V6 tests a different source of
edge: short-horizon reversal after a BTC-adjusted extreme move accompanied by
same-direction aggressive taker flow.

## Frozen signal

- Build completed UTC hourly bars only from twelve complete 5-minute rows.
- Enter no earlier than the next 5-minute row.
- Estimate each coin's BTC beta on the preceding 720 completed hours, with a
  240-hour minimum, and shift the beta one hour.
- Rank the current 1-hour residual cross-sectionally.
- Candidate tails are the bottom/top 10%, with absolute residual z-scores of
  at least 1.0 at 1 hour and 0.5 at 4 hours.
- The 4-hour residual and aggressive taker imbalance must agree with the shock.
- Current hourly quote volume must be at least its prior 7-day hourly median.
- Prior 24-hour quote volume must be at least $10 million.
- Trade the reversal: negative extreme is LONG, positive extreme is SHORT.
- Select the largest frozen composite score; allow one global position for a
  fixed four-hour observation horizon. Weekends are excluded.

## Primary test

The primary 4-hour forward return includes 9.5 bps round-trip friction plus a
10.95% APR holding-cost stress. V6 passes only if all checks pass:

1. at least 300 non-overlapping observations;
2. positive mean net 4-hour return;
3. at least 50% net winners;
4. positive total net return in at least 60% of active calendar quarters;
5. strongest-score selection beats the median random qualified candidate;
6. no more than 10% of random simulations equal or beat the strongest selector.

The 1-hour and 2-hour results are diagnostics. Stop, target, partial profit,
break-even, and trailing exits are deliberately absent. They may be researched
only if the V6 entry signal passes this charter.
