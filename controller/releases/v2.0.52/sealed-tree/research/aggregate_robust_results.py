#!/usr/bin/env python3
"""Aggregate TDH candidate results across chronological WFO/OOS windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


class AggregateError(ValueError):
    pass


METRIC_ALIASES = {
    "expectancy": ("expectancy", "expectancy_r", "net_expectancy", "net_expectancy_r"),
    "profit_factor": ("profit_factor", "pf"),
    "win_rate": ("win_rate", "wr", "net_win_rate"),
    "realized_rr": ("realized_rr", "realized_r_r", "rr", "reward_risk"),
    "max_drawdown_pct": ("max_drawdown_pct", "max_dd_pct", "max_dd", "drawdown_pct"),
    "net_pnl": ("net_pnl", "pnl", "net_profit", "return_pct"),
    "trade_count": ("trade_count", "trades", "n_trades"),
}


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def as_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise AggregateError(f"{label} must be a finite number")
    return float(value)


def find_metric(metrics: dict[str, Any], name: str, label: str) -> float:
    for alias in METRIC_ALIASES[name]:
        if alias in metrics:
            return as_number(metrics[alias], f"{label}.{alias}")
    raise AggregateError(f"{label}: missing {name}")


def as_rate(value: float) -> float:
    # Accept 0..1 or human percentages such as 52.3.
    return value / 100.0 if value > 1.0 else value


def as_drawdown_pct(value: float) -> float:
    value = abs(value)
    return value * 100.0 if value <= 1.0 else value


def gate_value(gates: dict[str, Any], *names: str) -> bool:
    for name in names:
        if name in gates:
            return gates[name] is True
    return False


def iter_records(path: Path) -> Iterable[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AggregateError(f"cannot read input: {exc}") from exc
    stripped = raw.lstrip()
    if stripped.startswith("["):
        try:
            rows = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AggregateError(f"invalid JSON: {exc}") from exc
        if not isinstance(rows, list):
            raise AggregateError("JSON input must be an array")
        for row in rows:
            if not isinstance(row, dict):
                raise AggregateError("each record must be an object")
            yield row
        return
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AggregateError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise AggregateError(f"line {line_number}: record must be an object")
        yield row


def normalize_record(row: dict[str, Any], index: int) -> dict[str, Any]:
    config_hash = row.get("strategy_config_sha256") or row.get("config_sha256") or row.get("candidate_hash")
    family_id = row.get("family_id") or row.get("strategy_family")
    window_id = row.get("window_id") or row.get("wfo_window") or row.get("period_id")
    if not isinstance(config_hash, str) or not config_hash:
        raise AggregateError(f"record {index}: strategy_config_sha256 missing")
    if not isinstance(family_id, str) or not family_id:
        raise AggregateError(f"record {index}: family_id missing")
    if not isinstance(window_id, (str, int)):
        raise AggregateError(f"record {index}: window_id missing")
    metrics = row.get("metrics")
    gates = row.get("gates", {})
    if not isinstance(metrics, dict):
        raise AggregateError(f"record {index}: metrics missing")
    if not isinstance(gates, dict):
        raise AggregateError(f"record {index}: gates must be an object")
    normalized = {
        "strategy_config_sha256": config_hash,
        "family_id": family_id,
        "experiment_id": row.get("experiment_id"),
        "window_id": str(window_id),
        "metrics": {
            "expectancy": find_metric(metrics, "expectancy", f"record {index}.metrics"),
            "profit_factor": find_metric(metrics, "profit_factor", f"record {index}.metrics"),
            "win_rate": as_rate(find_metric(metrics, "win_rate", f"record {index}.metrics")),
            "realized_rr": find_metric(metrics, "realized_rr", f"record {index}.metrics"),
            "max_drawdown_pct": as_drawdown_pct(find_metric(metrics, "max_drawdown_pct", f"record {index}.metrics")),
            "net_pnl": find_metric(metrics, "net_pnl", f"record {index}.metrics"),
            "trade_count": int(find_metric(metrics, "trade_count", f"record {index}.metrics")),
        },
        "gates": {
            "s1_pass": gate_value(gates, "s1_pass", "all_s1_gates_pass"),
            "baseline_beaten": gate_value(gates, "baseline_beaten"),
            "negative_control_beaten": gate_value(gates, "negative_control_beaten"),
        },
    }
    if normalized["metrics"]["trade_count"] < 0:
        raise AggregateError(f"record {index}: trade_count must not be negative")
    return normalized


def med(rows: list[dict[str, Any]], metric: str) -> float:
    return float(statistics.median(row["metrics"][metric] for row in rows))


def aggregate_group(
    rows: list[dict[str, Any]],
    target_wr: float,
    target_rr: float,
    target_dd: float,
) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: row["window_id"])
    config_hash = rows[0]["strategy_config_sha256"]
    family_id = rows[0]["family_id"]
    if len({row["family_id"] for row in rows}) != 1:
        raise AggregateError(f"config {config_hash}: family_id changes across windows")
    window_ids = [row["window_id"] for row in rows]
    if len(window_ids) != len(set(window_ids)):
        raise AggregateError(f"config {config_hash}: duplicate window_id")

    count = len(rows)
    positive_expectancy = [row["metrics"]["expectancy"] > 0 for row in rows]
    s1_passes = [row["gates"]["s1_pass"] for row in rows]
    baseline = [row["gates"]["baseline_beaten"] for row in rows]
    negative = [row["gates"]["negative_control_beaten"] for row in rows]
    target_hits = [
        row["metrics"]["expectancy"] > 0
        and row["metrics"]["profit_factor"] > 1.0
        and row["metrics"]["win_rate"] >= target_wr
        and row["metrics"]["realized_rr"] >= target_rr
        and row["metrics"]["max_drawdown_pct"] <= target_dd
        for row in rows
    ]
    median_metrics = {name: med(rows, name) for name in METRIC_ALIASES}
    worst_metrics = {
        "expectancy": min(row["metrics"]["expectancy"] for row in rows),
        "profit_factor": min(row["metrics"]["profit_factor"] for row in rows),
        "win_rate": min(row["metrics"]["win_rate"] for row in rows),
        "realized_rr": min(row["metrics"]["realized_rr"] for row in rows),
        "max_drawdown_pct": max(row["metrics"]["max_drawdown_pct"] for row in rows),
        "net_pnl": min(row["metrics"]["net_pnl"] for row in rows),
    }
    signs = [1 if value else -1 for value in positive_expectancy]
    sign_changes = sum(left != right for left, right in zip(signs, signs[1:]))
    breakeven_wr = 1.0 / (1.0 + median_metrics["realized_rr"]) if median_metrics["realized_rr"] > 0 else 1.0
    wr_margin = median_metrics["win_rate"] - breakeven_wr

    violations = {
        "nonpositive_worst_expectancy": worst_metrics["expectancy"] <= 0,
        "worst_pf_not_above_one": worst_metrics["profit_factor"] <= 1.0,
        "worst_wr_below_target": worst_metrics["win_rate"] < target_wr,
        "worst_rr_below_target": worst_metrics["realized_rr"] < target_rr,
        "worst_dd_above_target": worst_metrics["max_drawdown_pct"] > target_dd,
        "baseline_not_always_beaten": not all(baseline),
        "negative_control_not_always_beaten": not all(negative),
    }
    violation_count = sum(violations.values())
    all_s1 = all(s1_passes) and all(target_hits)
    all_controls_and_positive = all(baseline) and all(negative) and all(positive_expectancy)
    fragile = any(positive_expectancy) and not all(positive_expectancy)
    if all_s1 and all_controls_and_positive:
        status = "ROBUST"
    elif fragile or sign_changes > 0:
        status = "FRAGILE"
    elif violation_count <= 2 and worst_metrics["max_drawdown_pct"] <= target_dd * 2:
        status = "NEAR_MISS"
    else:
        status = "REJECTED"

    counterexample = min(
        rows,
        key=lambda row: (row["metrics"]["expectancy"], -row["metrics"]["max_drawdown_pct"], row["window_id"]),
    )
    ranking_key = [
        0 if status == "ROBUST" else 1,
        0 if all_controls_and_positive else 1,
        violation_count,
        -worst_metrics["expectancy"],
        worst_metrics["max_drawdown_pct"],
        -median_metrics["profit_factor"],
        -wr_margin,
        config_hash,
    ]
    return {
        "strategy_config_sha256": config_hash,
        "family_id": family_id,
        "experiment_id": rows[0].get("experiment_id"),
        "robust_status": status,
        "window_count": count,
        "total_trade_count": sum(row["metrics"]["trade_count"] for row in rows),
        "s1_pass_count": sum(s1_passes),
        "s1_pass_rate": sum(s1_passes) / count,
        "positive_expectancy_window_rate": sum(positive_expectancy) / count,
        "baseline_superiority_rate": sum(baseline) / count,
        "negative_control_superiority_rate": sum(negative) / count,
        "target_hit_rate": sum(target_hits) / count,
        "sign_change_count": sign_changes,
        "regime_fragile": fragile,
        "median_metrics": median_metrics,
        "worst_metrics": worst_metrics,
        "breakeven_win_rate": breakeven_wr,
        "median_win_rate_margin": wr_margin,
        "violations": violations,
        "violation_count": violation_count,
        "strongest_counterexample": {
            "window_id": counterexample["window_id"],
            "metrics": counterexample["metrics"],
            "gates": counterexample["gates"],
        },
        "ranking_key": ranking_key,
    }


def family_diagnostics(aggregates: list[dict[str, Any]], target_wr: float, target_rr: float, target_dd: float) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for aggregate in aggregates:
        groups[aggregate["family_id"]].append(aggregate)
    results: list[dict[str, Any]] = []
    for family_id, items in sorted(groups.items()):
        flags: list[str] = []
        rr_values = [item["median_metrics"]["realized_rr"] for item in items]
        wr_values = [item["median_metrics"]["win_rate"] for item in items]
        dd_values = [item["worst_metrics"]["max_drawdown_pct"] for item in items]
        control_values = [
            min(item["baseline_superiority_rate"], item["negative_control_superiority_rate"])
            for item in items
        ]
        if len(items) >= 8:
            if max(rr_values) < target_rr and max(rr_values) - min(rr_values) <= 0.10:
                flags.append("PAYOFF_FAMILY_CEILING")
            if max(wr_values) < target_wr - 0.05:
                flags.append("SIGNAL_PRECISION_CEILING")
            if statistics.median(dd_values) > target_dd * 2:
                flags.append("RISK_REGIME_FAILURE")
            if statistics.median(control_values) <= 0.10:
                flags.append("NO_INCREMENTAL_FAMILY_EDGE")
        results.append(
            {
                "family_id": family_id,
                "evaluated_config_count": len(items),
                "flags": flags,
                "median_of_worst_dd_pct": float(statistics.median(dd_values)),
                "best_median_win_rate": max(wr_values),
                "median_rr_range": [min(rr_values), max(rr_values)],
                "median_control_superiority": float(statistics.median(control_values)),
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--target-wr", type=float, default=0.50)
    parser.add_argument("--target-rr", type=float, default=2.0)
    parser.add_argument("--target-dd-pct", type=float, default=10.0)
    args = parser.parse_args()
    try:
        if not 0 < args.target_wr < 1:
            raise AggregateError("target-wr must be a 0..1 rate")
        if args.target_rr <= 0 or args.target_dd_pct <= 0:
            raise AggregateError("target RR and DD must be positive")
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        normalized_rows: list[dict[str, Any]] = []
        for index, row in enumerate(iter_records(args.input), start=1):
            normalized = normalize_record(row, index)
            normalized_rows.append(normalized)
            groups[normalized["strategy_config_sha256"]].append(normalized)
        if not normalized_rows:
            raise AggregateError("input contains no records")
        aggregates = [
            aggregate_group(rows, args.target_wr, args.target_rr, args.target_dd_pct)
            for _, rows in sorted(groups.items())
        ]
        aggregates.sort(key=lambda item: tuple(item["ranking_key"]))
        output = {
            "aggregation_version": "tdh-robust-v1",
            "targets": {"win_rate": args.target_wr, "realized_rr": args.target_rr, "max_drawdown_pct": args.target_dd_pct},
            "record_count": len(normalized_rows),
            "config_count": len(aggregates),
            "aggregates": aggregates,
            "family_diagnostics": family_diagnostics(aggregates, args.target_wr, args.target_rr, args.target_dd_pct),
            "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        }
        output["aggregate_sha256"] = canonical_hash(output)
        encoded = json.dumps(output, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (AggregateError, OSError) as exc:
        print(f"ROBUST_AGGREGATION_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
