# TDH agent contract

## Mission

Maximize information gained per offline backtest. Do not maximize trial count
or isolated PnL.

## Invariants

- Never perform or prepare live or paper trading.
- Never access an exchange or private API.
- Never request, read, write, or expose credentials.
- Never use S6.
- Keep S2-S4 closed until all S1 gates pass.
- Require a registered family and bounded parameter schema.
- Require exactly one primary causal change per experiment.
- Run candidate, baseline, and negative control on identical immutable data,
  costs, and chronological partitions.
- Preserve raw evidence while passing only compact deterministic context to
  models.
- Fail closed on unknown families, unsupported data, malformed proposals,
  integrity errors, and arbitrary executable code.

## Ownership

- Frontier Scout writes only untrusted inbox proposals.
- Codex writes causal proposals.
- Claude writes adversarial critiques.
- Evaluator writes immutable measurements.
- Controller alone writes canonical state, registry promotion, negative memory,
  experiment ledger entries, and stage transitions.
