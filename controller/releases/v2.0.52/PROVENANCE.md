# TDH controller v2.0.52 provenance

This directory is an immutable repository snapshot of the TDH v2.0.52 controller release entry point and its v2.0.52 frontier-continuity regression test.

## Safety contract

- System type: research and backtest only
- Research mode: offline
- Trading actions: disabled
- Exchange API access: disabled
- Promotion authority: controller only
- S2–S4 remain closed until all S1 gates pass

## Build and validation evidence

- Staged from sealed v2.0.51
- v2.0.52 marker: `tdh-avenox-frontier-continuity-v252`
- Static validation covered peer-frontier exhaustion lane skip, eligible-frontier exhaustion epoch rollover, and fail-closed unknown errors
- Regression suite at seal time: 153 passed
- Release preflight: `PREFLIGHT_OK`
- Activated on 2026-08-14 UTC through `strategy-lab-supervisor-v2.1.service`

## Runtime evidence

- First v2.0.52 run: `tdh-strategy-lab-v2-20260814T154129Z`
- The run reached S1 `BACKTESTING`
- It completed and was accounted as epoch 1012
- Automatic next run: `tdh-strategy-lab-v2-20260814T154426Z`
- `continuous_research_epochs=true`
- `no_progress_run_streak=0`
- Runtime safety flags remained `research_mode=offline`, `trading_actions=false`, and `exchange_api_access=false`

## Integrity

Repository snapshot hashes are recorded in `SOURCE_SHA256SUMS`.

This initial snapshot contains the release entry controller and the v2.0.52-specific regression test. Import of the remaining sealed release dependency tree, contracts, adapters, registry, and authoritative sealed `SHA256SUMS` remains tracked by GitHub Issue #2.
