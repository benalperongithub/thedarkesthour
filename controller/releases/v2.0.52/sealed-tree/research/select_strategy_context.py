#!/usr/bin/env python3
"""Select a small, deterministic TDH strategy context from the full registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ATLAS = ROOT / "references" / "evidence-atlas.json"
DEFAULT_QUEUE = ROOT / "references" / "experiment-queue.jsonl"
PRIORITY_SCORE = {
    "critical": 30,
    "high": 22,
    "medium": 12,
    "low": 2,
    "reject_or_control": -35,
    "reject": -60,
}
DIAGNOSIS_HINTS = {
    "PAYOFF_FAMILY_CEILING": {"trend": 20, "factor": 14, "mean_reversion": 8, "risk_overlay": 5},
    "SIGNAL_PRECISION_CEILING": {"trend": 16, "derivatives_flow": 14, "risk_overlay": 12, "microstructure": 6},
    "RISK_REGIME_FAILURE": {"risk_overlay": 28, "trend": 8, "mean_reversion": 5},
    "NO_INCREMENTAL_FAMILY_EDGE": {"trend": 12, "factor": 12, "stat_arb": 10, "risk_overlay": 6},
    "FRAGILE_REGIME_FIT": {"risk_overlay": 25, "trend": 8, "mean_reversion": 8},
    "NO_PROGRESS": {"trend": 10, "factor": 8, "stat_arb": 6, "risk_overlay": 6},
}
MULTI_TIMEFRAME_DEFAULTS = {
    # These two registered OHLCV overlays have horizon parameters rather than
    # an explicit candle timeframe. Bind them deterministically for execution.
    "VOL_MANAGED_MOM": "1d",
    "VOL_REGIME_GATE": "1h",
}


class SelectionError(ValueError):
    pass


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_csv(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SelectionError(f"cannot read {path}: {exc}") from exc


def load_negative_memory(path: Path | None) -> dict[str, set[str]]:
    result = {"experiment_ids": set(), "family_ids": set(), "config_hashes": set()}
    if path is None:
        return result
    raw = load_json(path)
    records = raw if isinstance(raw, list) else raw.get("negative_memory", []) if isinstance(raw, dict) else []
    if not isinstance(records, list):
        raise SelectionError("negative memory must be an array or contain negative_memory array")
    for record in records:
        if not isinstance(record, dict):
            continue
        for source, target in (
            ("experiment_id", "experiment_ids"),
            ("family_id", "family_ids"),
            ("strategy_config_sha256", "config_hashes"),
        ):
            value = record.get(source)
            if isinstance(value, str) and value:
                result[target].add(value)
        if record.get("exhausted") is True and isinstance(record.get("family_id"), str):
            result["family_ids"].add(record["family_id"])
    return result


def normalize_token(value: str) -> str:
    return value.strip().casefold().replace("-", "_")


def data_item_satisfied(required: str, available: set[str], supported_timeframes: set[str]) -> bool:
    item = normalize_token(required)
    normalized_available = {normalize_token(value) for value in available}
    if item.endswith("_optional") or item.endswith("/optional"):
        return True
    if item in normalized_available:
        return True
    if "ohlcv" in normalized_available:
        if item == "ohlcv" or item == "intraday_ohlcv":
            return True
        if item == "daily_ohlcv" and "1d" in supported_timeframes:
            return True
    if "ohlcv_1m" in normalized_available and item in {"ohlcv", "intraday_ohlcv", "1m_or_tick"}:
        return True
    if "/" in item:
        alternatives = {part.strip() for part in item.split("/") if part.strip()}
        if alternatives & normalized_available:
            return True
    return False


def required_data_satisfied(required: Iterable[str], available: set[str], supported_timeframes: set[str]) -> bool:
    return all(data_item_satisfied(item, available, supported_timeframes) for item in required)


def effective_timeframe(experiment: dict[str, Any]) -> str:
    value = experiment.get("timeframe")
    if value == "multi":
        param_value = experiment.get("params", {}).get("timeframe")
        if isinstance(param_value, str):
            return param_value
        family_default = MULTI_TIMEFRAME_DEFAULTS.get(str(experiment.get("family_id")))
        if family_default:
            return family_default
    return value if isinstance(value, str) else ""


def timeframe_satisfied(experiment: dict[str, Any], supported: set[str]) -> bool:
    timeframe = effective_timeframe(experiment)
    return timeframe in supported or (timeframe == "multi" and "multi" in supported)


def compact_family(family: dict[str, Any], selection_score: int) -> dict[str, Any]:
    keys = (
        "family_id",
        "name",
        "bucket",
        "evidence_score",
        "confidence_tier",
        "research_priority",
        "required_data",
        "thesis",
        "main_failure_modes",
        "source_keys",
    )
    return {**{key: family.get(key) for key in keys}, "selection_score": selection_score}


def compact_seed(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "experiment_id",
        "family_id",
        "timeframe",
        "universe",
        "params",
        "required_data",
    )
    compact = {
        **{key: row.get(key) for key in keys},
        # The full repeated list lives in the registry; one stable identifier
        # avoids paying for the same validation prose once per seed.
        "validation_profile": "TDH_ROBUST_V1",
    }
    effective = effective_timeframe(row)
    if compact.get("timeframe") == "multi" and effective != "multi":
        compact["registry_timeframe"] = "multi"
        compact["timeframe"] = effective
    return compact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--diagnosis", default="NO_PROGRESS", choices=sorted(DIAGNOSIS_HINTS))
    parser.add_argument("--available-data", default="OHLCV")
    parser.add_argument("--supported-timeframes", default="5m,15m,1h,4h,6h,12h,1d")
    parser.add_argument("--previous-family")
    parser.add_argument("--negative-memory", type=Path)
    parser.add_argument("--family-limit", type=int, default=6)
    parser.add_argument("--seed-limit", type=int, default=16)
    parser.add_argument("--allow-control-families", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        if not 3 <= args.family_limit <= 8:
            raise SelectionError("family-limit must be between 3 and 8")
        if not 1 <= args.seed_limit <= 20:
            raise SelectionError("seed-limit must be between 1 and 20")
        atlas = load_json(args.atlas)
        if not isinstance(atlas, dict) or not isinstance(atlas.get("families"), list):
            raise SelectionError("invalid atlas")
        available_data = parse_csv(args.available_data)
        supported_timeframes = parse_csv(args.supported_timeframes)
        negative = load_negative_memory(args.negative_memory)
        hint_scores = DIAGNOSIS_HINTS[args.diagnosis]

        eligible_families: list[tuple[int, dict[str, Any]]] = []
        blocked_families: dict[str, str] = {}
        for family in atlas["families"]:
            family_id = family.get("family_id")
            priority = family.get("research_priority")
            if not isinstance(family_id, str):
                continue
            if priority in {"reject", "reject_or_control"} and not args.allow_control_families:
                blocked_families[family_id] = "CONTROL_OR_REJECT_ONLY"
                continue
            if family_id in negative["family_ids"]:
                blocked_families[family_id] = "NEGATIVE_MEMORY_EXHAUSTED"
                continue
            required = family.get("required_data", [])
            if not required_data_satisfied(required, available_data, supported_timeframes):
                blocked_families[family_id] = "BLOCKED_BY_DATA"
                continue
            score = int(family.get("evidence_score", 0)) + PRIORITY_SCORE.get(str(priority), 0)
            score += hint_scores.get(str(family.get("bucket")), 0)
            if args.previous_family and family_id == args.previous_family:
                score -= 45 if args.diagnosis in {"PAYOFF_FAMILY_CEILING", "NO_INCREMENTAL_FAMILY_EDGE"} else 15
            eligible_families.append((score, family))

        eligible_families.sort(key=lambda item: (-item[0], -int(item[1].get("evidence_score", 0)), str(item[1].get("family_id"))))
        selected_pairs = eligible_families[: args.family_limit]
        selected_ids = {family["family_id"] for _, family in selected_pairs}
        if not selected_ids:
            raise SelectionError("no eligible strategy families for the declared data")

        seeds: list[tuple[int, dict[str, Any]]] = []
        blocked_experiments = {"BLOCKED_BY_DATA": 0, "BLOCKED_BY_TIMEFRAME": 0, "NEGATIVE_MEMORY": 0, "UNSELECTED_FAMILY": 0}
        with args.queue.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                family_id = row.get("family_id")
                if family_id not in selected_ids:
                    blocked_experiments["UNSELECTED_FAMILY"] += 1
                    continue
                if row.get("experiment_id") in negative["experiment_ids"]:
                    blocked_experiments["NEGATIVE_MEMORY"] += 1
                    continue
                if not required_data_satisfied(row.get("required_data", []), available_data, supported_timeframes):
                    blocked_experiments["BLOCKED_BY_DATA"] += 1
                    continue
                if not timeframe_satisfied(row, supported_timeframes):
                    blocked_experiments["BLOCKED_BY_TIMEFRAME"] += 1
                    continue
                family_score = next(score for score, family in selected_pairs if family["family_id"] == family_id)
                digest = int(canonical_hash(row)[:8], 16)
                # Stable diversity tie-breaker prevents file ordering from becoming research policy.
                seeds.append((family_score * 10_000 - digest % 10_000, row))

        seeds.sort(key=lambda item: (-item[0], str(item[1].get("experiment_id"))))
        chosen_seeds: list[dict[str, Any]] = []
        per_family: dict[str, int] = {}
        # First pass: represent each selected family when it has an eligible seed.
        for _, row in seeds:
            family_id = row["family_id"]
            if per_family.get(family_id, 0) == 0:
                chosen_seeds.append(compact_seed(row))
                per_family[family_id] = 1
                if len(chosen_seeds) >= args.seed_limit:
                    break
        # Second pass: fill the remaining budget, capped to avoid one-family domination.
        if len(chosen_seeds) < args.seed_limit:
            chosen_ids = {row["experiment_id"] for row in chosen_seeds}
            cap = max(2, (args.seed_limit + len(selected_ids) - 1) // len(selected_ids) + 1)
            for _, row in seeds:
                if row["experiment_id"] in chosen_ids:
                    continue
                family_id = row["family_id"]
                if per_family.get(family_id, 0) >= cap:
                    continue
                chosen_seeds.append(compact_seed(row))
                chosen_ids.add(row["experiment_id"])
                per_family[family_id] = per_family.get(family_id, 0) + 1
                if len(chosen_seeds) >= args.seed_limit:
                    break

        packet = {
            "selection_version": "tdh-context-v1",
            "diagnosis": args.diagnosis,
            "constraints": {
                "available_data": sorted(available_data),
                "supported_timeframes": sorted(supported_timeframes),
                "previous_family": args.previous_family,
                "offline_only": True,
                "s1_only": True,
            },
            "family_cards": [compact_family(family, score) for score, family in selected_pairs],
            "experiment_seeds": chosen_seeds,
            "blocked_family_counts": {
                reason: sum(1 for value in blocked_families.values() if value == reason)
                for reason in sorted(set(blocked_families.values()))
            },
            "blocked_experiment_counts": blocked_experiments,
            "negative_memory_counts": {key: len(value) for key, value in negative.items()},
        }
        packet["context_sha256"] = canonical_hash(packet)
        encoded = json.dumps(packet, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError, json.JSONDecodeError, SelectionError) as exc:
        print(f"CONTEXT_SELECTION_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
