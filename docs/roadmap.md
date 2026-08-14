# TDH implementation roadmap

This is the controller-first execution order. Later items must not bypass earlier
release, test, or safety gates.

## 1. Activate and verify v2.0.52

- Switch the supervisor unit from sealed v2.0.51 to sealed v2.0.52.
- Confirm the running command references v2.0.52.
- Verify offline policy, lane-local frontier exhaustion handling, bounded epoch
  rollover, and fail-closed unknown errors from runtime artifacts.

## 2. Establish the repository as the release source of truth

- Import the exact sealed v2.0.52 controller source, tests, contracts, adapter,
  and research registry with provenance hashes.
- Keep datasets, runtime logs, provider envelopes, credentials, and generated
  run artifacts off GitHub.
- Define staging, test, seal, preflight, activation, and rollback documentation.

## 3. Build v2.0.53 Frontier Scout

- Trigger only below an eligible-frontier low watermark.
- Let the scout write data-only hypotheses to an untrusted inbox.
- Validate source provenance, dataset eligibility, bounded parameters,
  look-ahead-safe timing, controls, duplicates, and negative memory.
- Auto-admit only seeds inside an already registered family's immutable bounds.
- Require adapter/schema/tests/controller registration for a genuinely new
  executable family.
- Cap provider tokens, inbox size, registrations per epoch, and family
  backtests.
- Preserve offline-only operation and controller-only promotion.

## 4. Validate and register the pending video strategy intake

Source:
`research/intake/pending/TDH_Video_Stratejileri_Research_Intake_2026-08-14.md`

- Treat video findings as research priors, not crypto-futures performance proof.
- Revalidate the document's historical VPS snapshot against canonical state.
- Start with the cheapest discriminating `RSI_GATED_REVERSION` Package A only
  after the family, adapter, baseline, negative control, and tests are
  registered.
- Consider `KELTNER_REVERSION` only after the required registration work.
- Consider `CROSS_SECTION_MOM` only after synchronized multi-asset data
  preflight.
- Do not open S2-S4 until every S1 hard gate passes.
