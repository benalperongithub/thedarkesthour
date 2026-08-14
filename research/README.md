# Research queues

## Queue layers

1. `frontier-inbox.jsonl`: untrusted data-only hypotheses from the Frontier
   Scout.
2. Source validation: confirms provenance and prevents unsupported claims.
3. Data eligibility: confirms the canonical dataset can execute the hypothesis.
4. Registry validation: assigns a registered family, bounded schema, baseline,
   negative control, and stable hashes.
5. `experiment-queue.jsonl`: controller-approved executable seeds.

The inbox is not an execution queue. Only controller-registered entries may
reach S1.

## Replenishment policy

- Trigger only below a configurable eligible-frontier low watermark.
- Generate a bounded batch.
- Deduplicate against the registry, experiment ledger, and negative memory.
- Prefer mechanism novelty and information gain over cosmetic parameter search.
- Cap provider tokens, pending inbox size, registrations per epoch, and
  backtests per family.
- Apply cooldown after repeated rejection or structural `NO_SIGNAL`.
