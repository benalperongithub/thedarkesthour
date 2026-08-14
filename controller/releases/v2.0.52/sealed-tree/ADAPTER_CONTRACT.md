# TDH Phoenix adapter contract — v2.0.3 feature layer

Production adapter path:

`/srv/tdh-collab/controller/strategy-lab-v2/v2.0.3/adapter/tdh_strategy_lab_phoenix_adapter.py`

The v2.0.3 adapter is a narrow extension over the immutable reviewed v2.0.2 Phoenix adapter. It may not weaken or bypass any v2.0.2 execution, accounting, stage, data, seed, WFO, cost, funding, risk or safety rule.

## Required behavior

1. Accept only `--request`, `--output`, and `--stage S1|S2|S3|S4`.
2. Read only the declared `DEVELOPMENT_VALIDATION_ONLY` identity.
3. Use Phoenix as the canonical S1–S4 judge; narrative/fabricated metrics are invalid.
4. Echo candidate/trial identity exactly and preserve protected hashes.
5. Keep contract version `2.0.2`; `2.0.3` is the reviewed feature/release layer, not a relaxation of the canonical contract.
6. Accept only family `phoenix_single_exchange_rr2`.
7. Require exactly one pre-registered symbol per production candidate from:
   `BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT, LINKUSDT, AVAXUSDT`.
8. Permit only `5m|15m`; 1m remains disabled until a separate canonical 1m dataset identity is frozen.
9. Permit at most four existing registered signal/entry overrides. Structural R/R, stop/risk, costs, funding, data roots and partition remain adapter-owned.
10. Candidate, baseline and negative control must use the identical symbol and timeframe.
11. S1 must run candidate + frozen baseline + frozen negative control as distinct trial identities/config hashes/artifact trees. Only PERFORMANCE may promote.
12. The adapter may execute independent experiment jobs with at most two local worker processes. It may not enable network or arbitrary commands.
13. S1 BASELINE/NEGATIVE_CONTROL may be reused inside the same run only when classification and every protected identity/config hash match exactly. Cache hits must create a fresh current-trial artifact containing a cryptographic reference to the source result.
14. Deterministic rerun evidence remains mandatory where v2.0.2 requires it; cache never substitutes for a PERFORMANCE rerun.
15. Return `INVALID` for integrity, leakage, reconciliation, identity, config, artifact or single-position failures.
16. S3 remains bound to the frozen four-fold WFO plan; S4 remains bound to the root-owned seed manifest.
17. No exchange/private API/network/service/Docker/deploy/order capability is permitted.
18. No internal-sealed or true-forward access is permitted.

## Single-position interpretation

A v2.0.3 candidate is a **single-symbol strategy**. This deliberately avoids combining independent symbol backtests into a fictitious multi-symbol portfolio. The canonical `max_simultaneous_positions = 1` and portfolio drawdown are therefore measured on the exact pre-registered candidate symbol. Symbol selection is part of the config hash and cannot change after observing that candidate's result.

## Parallelism and cache

Parallelism is only a compute optimization. It may not alter trial order semantics, random seeds, configs, artifacts, metrics or promotion gates. Cache eligibility is equality-based, never similarity-based. A different symbol, timeframe, config hash, Phoenix tree, data manifest, partition, execution model, WFO plan or seed identity is a cache miss.
