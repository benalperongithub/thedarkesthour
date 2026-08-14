# TDH architecture

## Canonical flow

1. The controller loads immutable offline policy, data provenance, robust
   research memory, and the registered strategy universe.
2. The deterministic research kernel builds an eligible novelty frontier.
3. The Deep Researcher and Independent Critic produce bounded advisory
   evidence. Their output cannot promote or execute anything.
4. Codex proposes one causal registered change. Claude attacks the weakest
   evidence and, when possible, proposes a distinct registered family.
5. The controller validates schema, family registration, data eligibility,
   novelty, single-change discipline, and safety.
6. The evaluator runs candidate, baseline, and negative control using identical
   chronological S1 partitions, costs, and data.
7. Codex and Claude audit the measured S1 result.
8. The controller applies conjunctive hard gates and writes immutable evidence,
   positive/negative memory, and the experiment ledger.
9. Expected lane-local exhaustion is skipped without discarding the valid peer.
   Global frontier exhaustion rolls into a fresh bounded epoch.

## Continuous frontier replenishment

Frontier replenishment is separate from canonical execution:

```text
Approved public literature / bounded internal atlas
  -> Frontier Scout
  -> untrusted frontier inbox
  -> source, schema, data and duplicate validation
  -> controller-owned registered family/seed queue
  -> eligible novelty frontier
```

The scout cannot write executable strategy code or the canonical registry. A
proposal that lacks source provenance, compatible data, bounded parameters,
look-ahead-safe timing, baseline, negative control, or a falsification test
remains rejected or pending.

## Continuity behavior

- Empty peer lane: skip that provider call and preserve the valid peer.
- Empty global frontier: record a bounded `REVISE` outcome and roll the epoch.
- Low registered-queue watermark: request bounded scout replenishment.
- Unknown provider, data, integrity, or schema error: fail closed.
