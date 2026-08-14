# TDH Mete Kaplan STR + LIQ + IMB — Sealed Intake Manifest

Registry ID: `MK_STR_LIQ_IMB_v1`
Parent family: `MK_STR_LIQ_IMB`
Source version: `1.0.0`
Source prepared: `2026-08-13`
Source attachment SHA-256: `a96aaea3fc5069b6da5e1b87071c7377723c303904e553a40b9cacc8f5d6bab8`
Source attachment size: `35399` bytes
Research mode: `offline`
Trading actions: `false`
Exchange API access: `false`

This sealed file is the executable-intake manifest for the user-supplied research pack `TDH_Mete_Kaplan_STR_LIQ_IMB_Research_Pack_v1.md`. The full source document remains the authoritative research specification; this manifest records exactly which portion is executable in TDH v2.0.39 and prevents unsupported sections from being silently treated as implemented.

## Source-derived family grammar

The source pack defines the core research question as incremental comparison of:

- `MK_A_LIQ_IMB`: liquidity sweep/reclaim + imbalance/FVG retest.
- `MK_B_STR_IMB`: strong structure/displacement break + imbalance/FVG retest.
- `MK_C_STR_LIQ_IMB`: sweep -> strong structure break -> fresh imbalance/FVG -> retest.

Positive PnL alone is not a pass. The source requires causal closed-bar features, controls, walk-forward robustness, costs and a minimum completed-trade gate of 300.

## v2.0.39 executable tranche

Executable:

- Families: `MK_A_LIQ_IMB`, `MK_B_STR_IMB`, `MK_C_STR_LIQ_IMB`
- Timeframe: `5m`
- Symbols: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`
- Profiles: `BASE`, `LOOSE`, `STRICT`, `CONFIRM`
- Total immutable seeds: `12`
- Confirmed pivots become usable only after the right-side confirmation delay.
- FVGs are defined only after the third candle closes; resulting signals cannot execute before a later bar.
- Same-bar unresolved stop/target ambiguity remains pessimistic in the inherited simulator.
- Mete-specific accounting uses current-equity compounding at the pack's primary `0.25%` risk fraction.
- `BASELINE` is currently the source pack's `B1` FVG-only comparator.
- `NEGATIVE_CONTROL` is currently direction inversion (`N1`) as a diagnostic.

## Explicitly blocked in v2.0.39

- `1m`: blocked because the current canonical executable registry is 5m-based.
- `B0` regime/session-matched fold-local randomized timing: pending implementation.
- `MK_D_MTF_BIAS`: pending true MTF implementation.
- `MK_E_SESSION`: pending core A/B/C evidence review.
- `MK_F_MAGIC_ALIGNMENT`: pending synchronized cross-asset execution/control implementation.
- `MK_G_BREAKER_RETEST`, `MK_H_RANGE_DEVIATION`, `MK_I_PO3_EXPANSION`, `MK_J_BPR_INDUCEMENT`: conditional S1B mechanisms, not rescue searches.
- EQH/EQL, PDH/PDL and session liquidity variants are not silently substituted for the initial executable SWING-level operationalization.
- Full pack S1 promotion remains blocked until missing controls/confirmation layers are implemented and passed.

## Gate contract

The global authoritative TDH S1 gate is unchanged. Mete candidates additionally require `trade_count >= 300`. v2.0.39 core results are research evidence only and cannot promote while `mk_full_pack_s1_eligible=false`.

## Provenance rule

Any later change to the source operationalization must create a new registry/version and new config hashes. The sealed source attachment hash above must never be replaced silently.
