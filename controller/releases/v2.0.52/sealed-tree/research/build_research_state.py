#!/usr/bin/env python3
"""Build bounded deterministic RESEARCH_STATE and optional append-only ledger entry."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


class StateError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path | None, label: str, default: Any = None) -> Any:
    if path is None:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"cannot read {label}: {exc}") from exc


def compact_aggregate(item: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "strategy_config_sha256",
        "family_id",
        "experiment_id",
        "robust_status",
        "window_count",
        "total_trade_count",
        "s1_pass_rate",
        "positive_expectancy_window_rate",
        "baseline_superiority_rate",
        "negative_control_superiority_rate",
        "target_hit_rate",
        "median_metrics",
        "worst_metrics",
        "median_win_rate_margin",
        "violation_count",
        "strongest_counterexample",
    )
    return {key: item.get(key) for key in keys}


def select_contrasts(aggregates: list[dict[str, Any]]) -> dict[str, Any]:
    if not aggregates:
        return {}
    leader = aggregates[0]
    near_misses = [item for item in aggregates if item.get("robust_status") == "NEAR_MISS"]
    low_dd = min(aggregates, key=lambda item: (item.get("worst_metrics", {}).get("max_drawdown_pct", float("inf")), item.get("strategy_config_sha256", "")))
    counterexample = min(aggregates, key=lambda item: (item.get("worst_metrics", {}).get("expectancy", float("inf")), item.get("strategy_config_sha256", "")))
    output: dict[str, Any] = {"robust_leader": compact_aggregate(leader)}
    if near_misses:
        output["best_near_miss"] = compact_aggregate(near_misses[0])
    output["lowest_worst_dd"] = compact_aggregate(low_dd)
    output["strongest_counterexample"] = compact_aggregate(counterexample)
    return output


def negative_record(item: dict[str, Any]) -> dict[str, Any]:
    violations = sorted(key for key, value in item.get("violations", {}).items() if value)
    return {
        "strategy_config_sha256": item.get("strategy_config_sha256"),
        "family_id": item.get("family_id"),
        "experiment_id": item.get("experiment_id"),
        "robust_status": item.get("robust_status"),
        "violation_codes": violations,
        "worst_expectancy": item.get("worst_metrics", {}).get("expectancy"),
        "worst_drawdown_pct": item.get("worst_metrics", {}).get("max_drawdown_pct"),
    }


def merge_negative_memory(prior: Any, aggregates: list[dict[str, Any]], limit: int = 64) -> list[dict[str, Any]]:
    existing = prior.get("negative_memory", []) if isinstance(prior, dict) else []
    records = [record for record in existing if isinstance(record, dict)]
    records.extend(
        negative_record(item)
        for item in aggregates
        if item.get("robust_status") in {"FRAGILE", "REJECTED"}
    )
    dedup: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get("strategy_config_sha256") or record.get("proposal_fingerprint") or canonical_hash(record)
        dedup[str(key)] = record
    return [dedup[key] for key in sorted(dedup)][-limit:]


def ledger_entry(state: dict[str, Any]) -> dict[str, Any]:
    contrasts = state.get("robust_contrasts", {})
    leader = contrasts.get("robust_leader", {}) if isinstance(contrasts, dict) else {}
    return {
        "ledger_version": "tdh-experiment-ledger-v1",
        "epoch_id": state.get("epoch_id"),
        "round_id": state.get("round_id"),
        "stage": state.get("stage"),
        "baseline_identity": state.get("baseline_identity"),
        "hypothesis": state.get("active_hypothesis"),
        "primary_change": state.get("primary_change"),
        "data_contract_sha256": state.get("provenance", {}).get("data_contract_sha256"),
        "protocol_sha256": state.get("provenance", {}).get("aggregate_sha256"),
        "leader_result": leader,
        "family_diagnostics": state.get("family_diagnostics", []),
        "critique": state.get("last_critique"),
        "decision": "ACCEPTED" if leader.get("robust_status") == "ROBUST" else "REJECTED",
        "negative_memory_count": len(state.get("negative_memory", [])),
        "state_sha256": state.get("state_sha256"),
    }


def append_ledger(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(entry) + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o640)
    try:
        with os.fdopen(fd, "ab", closefd=False) as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        os.close(fd)


def enforce_budget(state: dict[str, Any], max_chars: int) -> int:
    def length() -> int:
        return len(canonical_bytes(state).decode("utf-8"))

    current = length()
    if current <= max_chars:
        return current
    memory = state.get("negative_memory")
    if isinstance(memory, list) and len(memory) > 32:
        state["negative_memory"] = memory[-32:]
        current = length()
    selection = state.get("strategy_context")
    if current > max_chars and isinstance(selection, dict):
        seeds = selection.get("experiment_seeds")
        if isinstance(seeds, list) and len(seeds) > 10:
            selection["experiment_seeds"] = seeds[:10]
        families = selection.get("family_cards")
        if isinstance(families, list) and len(families) > 3:
            selection["family_cards"] = families[:3]
        current = length()
    if current > max_chars:
        state["negative_memory"] = state.get("negative_memory", [])[-12:]
        current = length()
    if current > max_chars:
        raise StateError(f"RESEARCH_STATE exceeds character budget: {current} > {max_chars}")
    return current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("aggregate", type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--prior-state", type=Path)
    parser.add_argument("--data-contract", type=Path)
    parser.add_argument("--epoch-id", required=True)
    parser.add_argument("--round-id", required=True)
    parser.add_argument("--baseline-identity")
    parser.add_argument("--active-hypothesis")
    parser.add_argument("--primary-change")
    parser.add_argument("--last-critique")
    parser.add_argument("--max-chars", type=int, default=16000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    try:
        aggregate = load_json(args.aggregate, "aggregate")
        selection = load_json(args.selection, "selection", {})
        prior = load_json(args.prior_state, "prior state", {})
        data_contract = load_json(args.data_contract, "data contract", {})
        if not isinstance(aggregate, dict) or not isinstance(aggregate.get("aggregates"), list):
            raise StateError("aggregate file is invalid")
        if selection is not None and not isinstance(selection, dict):
            raise StateError("selection must be an object")
        aggregates = aggregate["aggregates"]
        state = {
            "research_state_version": "tdh-research-state-v1",
            "epoch_id": args.epoch_id,
            "round_id": args.round_id,
            "stage": "WFO_REVIEWED",
            "ownership": {
                "codex": ["hypothesis", "primary_change"],
                "claude": ["critique", "falsification"],
                "evaluator": ["metrics", "fold_results"],
                "controller": ["canonical_state", "promotion", "ledger"],
            },
            "policy": {
                "research_mode": "offline",
                "trading_actions": False,
                "exchange_api_access": False,
                "s1_only": True,
                "controller_only_promotion": True,
                "one_primary_change": True,
            },
            "goal_contract": {
                "net_win_rate_min": aggregate.get("targets", {}).get("win_rate", 0.50),
                "realized_rr_min": aggregate.get("targets", {}).get("realized_rr", 2.0),
                "worst_window_drawdown_pct_max": aggregate.get("targets", {}).get("max_drawdown_pct", 10.0),
                "all_windows_positive_expectancy": True,
                "baseline_and_negative_control_always_beaten": True,
            },
            "baseline_identity": args.baseline_identity,
            "active_hypothesis": args.active_hypothesis,
            "primary_change": args.primary_change,
            "last_critique": args.last_critique,
            "robust_contrasts": select_contrasts(aggregates),
            "family_diagnostics": aggregate.get("family_diagnostics", []),
            "strategy_context": selection or {},
            "negative_memory": merge_negative_memory(prior, aggregates),
            "data_preflight": data_contract,
            "provenance": {
                "aggregate_sha256": aggregate.get("aggregate_sha256") or canonical_hash(aggregate),
                "selection_sha256": selection.get("context_sha256") if isinstance(selection, dict) else None,
                "data_contract_sha256": canonical_hash(data_contract) if data_contract else None,
                "prior_state_sha256": prior.get("state_sha256") if isinstance(prior, dict) else None,
            },
        }
        enforce_budget(state, args.max_chars)
        # Stabilize size metadata using a fixed-width hash placeholder. The
        # final digest has the same width, so context_char_count is exact.
        state["context_char_count"] = 0
        state["estimated_context_tokens"] = 0
        state["state_sha256"] = "0" * 64
        for _ in range(5):
            char_count = len(canonical_bytes(state).decode("utf-8"))
            estimate = (char_count + 3) // 4
            if state["context_char_count"] == char_count and state["estimated_context_tokens"] == estimate:
                break
            state["context_char_count"] = char_count
            state["estimated_context_tokens"] = estimate
        if state["context_char_count"] > args.max_chars:
            raise StateError(
                f"RESEARCH_STATE exceeds character budget after metadata: "
                f"{state['context_char_count']} > {args.max_chars}"
            )
        del state["state_sha256"]
        state["state_sha256"] = canonical_hash(state)
        encoded = json.dumps(state, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        if args.ledger:
            append_ledger(args.ledger, ledger_entry(state))
        return 0
    except (OSError, StateError) as exc:
        print(f"RESEARCH_STATE_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
