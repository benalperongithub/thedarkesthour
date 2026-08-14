#!/usr/bin/env python3
"""TDH Strategy Lab v2.0.3 Phoenix adapter extension.

This adapter reuses the immutable v2.0.2 Phoenix implementation and adds a narrow,
reviewable research surface:

* each candidate is bound to one registered symbol and one timeframe;
* candidate/baseline/negative-control share the exact same symbol/timeframe;
* independent experiments use at most two local worker processes;
* completed S1 controls may be reused inside the same run only when every protected
  identity hash and the exact strategy-config hash match.

No network, exchange, secret, Docker, service, deployment, or trading capability is
added. Structural R/R, costs, funding, capital, risk, WFO, seeds and Phoenix stage
semantics remain owned by the immutable v2.0.2 implementation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

BASE_PATH = Path(
    "/srv/tdh-collab/controller/strategy-lab-v2/v2.0.2/adapter/tdh_strategy_lab_phoenix_adapter.py"
)
if not BASE_PATH.is_file():
    raise RuntimeError(f"immutable v2.0.2 base adapter missing: {BASE_PATH}")
_spec = importlib.util.spec_from_file_location("tdh_strategy_lab_v202_adapter_base", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load immutable v2.0.2 base adapter")
base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = base
_spec.loader.exec_module(base)

CONTRACT_VERSION = base.CONTRACT_VERSION
AdapterError = base.AdapterError
_compute_status = base._compute_status
REGISTERED_FAMILY = base.REGISTERED_FAMILY
ALLOWED_TIMEFRAMES = set(base.ALLOWED_TIMEFRAMES)
MAX_OVERRIDES = base.MAX_OVERRIDES
REGISTERED_SYMBOLS = (
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
)
DEFAULT_LEGACY_SYMBOL = "BTCUSDT"
MAX_PARALLEL_WORKERS = 2
_BASE_VALIDATE = base.validate_candidate_config


def validate_candidate_config(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise AdapterError("config must be an object")
    keys = set(raw)
    if keys not in ({"family", "timeframe", "overrides"}, {"family", "symbol", "timeframe", "overrides"}):
        raise AdapterError("config must contain family, symbol, timeframe, and overrides")
    symbol = raw.get("symbol", DEFAULT_LEGACY_SYMBOL)
    if symbol not in REGISTERED_SYMBOLS:
        raise AdapterError("candidate symbol is not registered")
    legacy = {
        "family": raw.get("family"),
        "timeframe": raw.get("timeframe"),
        "overrides": raw.get("overrides"),
    }
    validated = _BASE_VALIDATE(legacy)
    return {
        "family": validated["family"],
        "symbol": symbol,
        "timeframe": validated["timeframe"],
        "overrides": validated["overrides"],
    }


# The immutable implementation calls this function through its own module globals.
base.validate_candidate_config = validate_candidate_config


def _hash_json(value: Any) -> str:
    return base._hash_json(value)


def _sha256(path: Path) -> str:
    return base._sha256(path)


def _json(path: Path) -> dict[str, Any]:
    return base._json(path)


def _write_json(path: Path, value: Any) -> None:
    base._write_json(path, value)


def _identity_compatible(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    fields = (
        "classification",
        "data_manifest_sha256",
        "execution_model_version",
        "experiment_plan_sha256",
        "partition_sha256",
        "phoenix_source_tree_sha256",
        "random_seed_manifest_sha256",
        "strategy_code_commit",
        "strategy_config_sha256",
        "wfo_plan_sha256",
    )
    return all(previous.get(field) == current.get(field) for field in fields)


def _normalized_experiment(entry: dict[str, Any]) -> dict[str, Any]:
    result = dict(entry)
    spec = dict(result.get("spec") or {})
    config = validate_candidate_config(spec.get("config"))
    spec["config"] = config
    result["spec"] = spec
    return result


def _validated_experiments(request: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    experiments = request.get("experiments")
    if not isinstance(experiments, list) or not experiments:
        raise AdapterError("request experiments are missing")
    plan = request.get("experiment_plan")
    if not isinstance(plan, dict) or plan.get("s1_trial_budget_per_candidate") != 3:
        raise AdapterError("request experiment plan is invalid")
    if not isinstance(plan.get("baseline"), dict) or plan["baseline"].get("overrides") != {}:
        raise AdapterError("request baseline plan is invalid")
    if not isinstance(plan.get("negative_control"), dict) or not isinstance(plan["negative_control"].get("overrides"), dict):
        raise AdapterError("request negative-control plan is invalid")

    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_trial_ids: set[str] = set()
    for raw_entry in experiments:
        if not isinstance(raw_entry, dict):
            raise AdapterError("experiment entry must be an object")
        entry = _normalized_experiment(raw_entry)
        experiment_id = str(entry.get("experiment_id", ""))
        candidate_id = str(entry.get("candidate_id", ""))
        classification = str(entry.get("classification", ""))
        identity = entry.get("identity")
        if not experiment_id or experiment_id in seen_ids or classification not in {"PERFORMANCE", "BASELINE", "NEGATIVE_CONTROL"}:
            raise AdapterError("experiment identity/classification is invalid")
        if not isinstance(identity, dict) or identity.get("experiment_id") != experiment_id or identity.get("candidate_id") != candidate_id or identity.get("classification") != classification:
            raise AdapterError("experiment wrapper identity drift")
        trial_id = str(identity.get("trial_id", ""))
        if not trial_id or trial_id in seen_trial_ids:
            raise AdapterError("experiment trial ID is missing or duplicated")
        seen_trial_ids.add(trial_id)
        config = entry["spec"]["config"]
        if identity.get("strategy_config_sha256") != _hash_json(config):
            raise AdapterError("experiment config hash drift")
        if identity.get("experiment_plan_sha256") != _hash_json(plan):
            raise AdapterError("experiment plan hash drift")
        if identity.get("wfo_plan_sha256") != _hash_json(plan.get("wfo")):
            raise AdapterError("WFO plan hash drift")
        if identity.get("partition_sha256") != _sha256(base.PARTITION):
            raise AdapterError("partition identity drift")
        if identity.get("data_manifest_sha256") != _sha256(base.DATA_MANIFEST):
            raise AdapterError("data manifest identity drift")
        if identity.get("random_seed_manifest_sha256") != _sha256(base.SEED_MANIFEST):
            raise AdapterError("seed manifest identity drift")
        seen_ids.add(experiment_id)
        group = grouped.setdefault(candidate_id, {})
        if classification in group:
            raise AdapterError("duplicate experiment classification for candidate")
        group[classification] = entry
        normalized.append(entry)

    expected_classes = {"PERFORMANCE", "BASELINE", "NEGATIVE_CONTROL"} if stage == "S1" else {"PERFORMANCE"}
    for candidate_id, group in grouped.items():
        if set(group) != expected_classes:
            raise AdapterError(f"incomplete experiment set for candidate: {candidate_id}")
        performance = group["PERFORMANCE"]["spec"]["config"]
        if stage == "S1":
            for classification, plan_key in (("BASELINE", "baseline"), ("NEGATIVE_CONTROL", "negative_control")):
                expected_config = {
                    "family": REGISTERED_FAMILY,
                    "symbol": performance["symbol"],
                    "timeframe": performance["timeframe"],
                    "overrides": plan[plan_key]["overrides"],
                }
                if group[classification]["spec"]["config"] != expected_config:
                    raise AdapterError(f"{classification} config drifted from frozen plan")
            fingerprints = {
                json.dumps(group[name]["spec"]["config"], sort_keys=True, separators=(",", ":"))
                for name in expected_classes
            }
            if len(fingerprints) != 3:
                raise AdapterError("candidate and control configs must be distinct")

    order = {"BASELINE": 0, "NEGATIVE_CONTROL": 1, "PERFORMANCE": 2}
    return sorted(normalized, key=lambda item: (str(item["candidate_id"]), order[str(item["classification"])]))


def _selected_files_for_config(manifest: dict[str, Any], config: dict[str, Any], dates: dict[str, str]) -> list[Path]:
    previous = base.VALIDATION_SYMBOLS
    try:
        base.VALIDATION_SYMBOLS = (config["symbol"],)
        return base._selected_data_files(manifest, config["timeframe"], dates)
    finally:
        base.VALIDATION_SYMBOLS = previous


def _job_payload(
    item: dict[str, Any],
    stage: str,
    output: Path,
    request_path: Path,
    dates: dict[str, str],
    data_files: list[Path],
    before_data: dict[str, str],
    comparisons: dict[str, dict[str, dict[str, float]]],
) -> tuple[dict[str, Any], str, str, str, dict[str, str], list[str], dict[str, str], dict[str, dict[str, dict[str, float]]]]:
    return (
        item,
        stage,
        str(output),
        str(request_path),
        dates,
        [str(p) for p in data_files],
        before_data,
        comparisons,
    )


def _run_one_job(payload: tuple[Any, ...]) -> dict[str, Any]:
    item, stage, output_raw, request_raw, dates, data_file_raw, before_data, comparisons = payload
    config = validate_candidate_config(item["spec"]["config"])
    base.VALIDATION_SYMBOLS = (config["symbol"],)
    return base._result_for_experiment(
        item,
        stage,
        Path(output_raw),
        Path(request_raw),
        dates,
        [Path(p) for p in data_file_raw],
        before_data,
        comparisons,
    )


def _run_jobs(payloads: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    if not payloads:
        return []
    if len(payloads) == 1:
        return [_run_one_job(payloads[0])]
    workers = min(MAX_PARALLEL_WORKERS, len(payloads))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_run_one_job, payloads))


def _find_cached_control(request_path: Path, item: dict[str, Any]) -> dict[str, Any] | None:
    if item.get("classification") not in {"BASELINE", "NEGATIVE_CONTROL"}:
        return None
    current_identity = item.get("identity") or {}
    run_root = request_path.parents[2]
    current_stage_dir = request_path.parent.resolve()
    for result_path in sorted(run_root.glob("round-*/s1/BACKTEST_RESULT.json")):
        if result_path.parent.resolve() == current_stage_dir:
            continue
        raw = _json(result_path)
        for previous in raw.get("experiment_results", []):
            if not isinstance(previous, dict):
                continue
            if previous.get("classification") != item.get("classification") or previous.get("status") != "COMPLETED":
                continue
            previous_identity = previous.get("identity") or {}
            if _identity_compatible(previous_identity, current_identity):
                return previous
    return None


def _cached_control_result(
    previous: dict[str, Any],
    item: dict[str, Any],
    stage: str,
    output: Path,
    request_path: Path,
    dates: dict[str, str],
    before_data: dict[str, str],
) -> dict[str, Any]:
    identity = item["identity"]
    experiment_id = str(identity["experiment_id"])
    candidate_id = str(identity["candidate_id"])
    classification = str(identity["classification"])
    config = validate_candidate_config(item["spec"]["config"])
    artifact = output.parent / "experiments" / experiment_id
    artifact.mkdir(parents=True, exist_ok=False)
    _write_json(artifact / "experiment_identity.json", identity)
    _write_json(artifact / "effective_config.json", {
        "experiment_id": experiment_id,
        "parent_candidate_id": candidate_id,
        "classification": classification,
        "registered_experiment_config": config,
        "validation_symbols": [config["symbol"]],
        "partition": dates,
        "initial_capital_usd": base.INITIAL_CAPITAL_USD,
        "fixed_risk_usd": base.FIXED_RISK_USD,
        "fixed_sl_pct": base.FIXED_SL_PCT,
        "fixed_notional_usd": base.FIXED_NOTIONAL_USD,
        "funding_apr_conservative": base.FUNDING_APR_CONSERVATIVE,
        "cache_hit": True,
    })
    _write_json(artifact / "cache_reference.json", {
        "source_experiment_id": previous.get("experiment_id"),
        "source_artifact_path": previous.get("artifact_path"),
        "source_identity_sha256": _hash_json(previous.get("identity")),
        "reason": "exact protected identity + strategy_config hash match within same run",
    })
    metrics = dict(previous.get("metrics") or {})
    gates = dict(previous.get("gates") or {})
    gates["data_integrity"] = bool(before_data)
    failure_reasons: list[str] = []
    status = "COMPLETED"
    _write_json(artifact / "stage_metrics.json", {
        "stage": stage,
        "status": status,
        "metrics": metrics,
        "gates": gates,
        "failure_reasons": failure_reasons,
        "cache_hit": True,
    })
    hashes = base._artifact_hashes(artifact)
    return {
        "candidate_id": candidate_id,
        "experiment_id": experiment_id,
        "classification": classification,
        "identity": identity,
        "status": status,
        "gates": gates,
        "metrics": metrics,
        "artifact_path": str(artifact),
        "artifact_hashes": hashes,
        "reproducibility_command": (
            f"/srv/tdh-research/phoenix-venv/bin/python {Path(__file__).resolve()} "
            f"--request {request_path} --output {output} --stage {stage}"
        ),
        "failure_reasons": failure_reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--stage", required=True, choices=("S1", "S2", "S3", "S4"))
    args = parser.parse_args()

    request = _json(args.request)
    if request.get("contract_version") != CONTRACT_VERSION or request.get("stage") != args.stage:
        raise AdapterError("request contract/stage mismatch")
    if request.get("data_class") != "DEVELOPMENT_VALIDATION_ONLY":
        raise AdapterError("adapter only accepts DEVELOPMENT_VALIDATION_ONLY")

    experiments = _validated_experiments(request, args.stage)
    partition = _json(base.PARTITION)
    dates = base._partition_dates(partition)
    manifest = _json(base.DATA_MANIFEST)

    files_by_experiment: dict[str, list[Path]] = {}
    before_by_experiment: dict[str, dict[str, str]] = {}
    for item in experiments:
        config = item["spec"]["config"]
        files = _selected_files_for_config(manifest, config, dates)
        files_by_experiment[item["experiment_id"]] = files
        before_by_experiment[item["experiment_id"]] = base._data_identity(files)

    results: list[dict[str, Any]] = []
    comparisons: dict[str, dict[str, dict[str, float]]] = {}

    if args.stage == "S1":
        controls = [x for x in experiments if x["classification"] in {"BASELINE", "NEGATIVE_CONTROL"}]
        uncached_payloads: list[tuple[Any, ...]] = []
        uncached_items: list[dict[str, Any]] = []
        for item in controls:
            previous = _find_cached_control(args.request, item)
            if previous is not None:
                result = _cached_control_result(
                    previous,
                    item,
                    args.stage,
                    args.output,
                    args.request,
                    dates,
                    before_by_experiment[item["experiment_id"]],
                )
                results.append(result)
                comparisons.setdefault(result["candidate_id"], {})[result["classification"]] = result["metrics"]
            else:
                uncached_items.append(item)
                uncached_payloads.append(_job_payload(
                    item,
                    args.stage,
                    args.output,
                    args.request,
                    dates,
                    files_by_experiment[item["experiment_id"]],
                    before_by_experiment[item["experiment_id"]],
                    {},
                ))
        for result in _run_jobs(uncached_payloads):
            results.append(result)
            if result["status"] == "COMPLETED":
                comparisons.setdefault(result["candidate_id"], {})[result["classification"]] = result["metrics"]

        performance = [x for x in experiments if x["classification"] == "PERFORMANCE"]
        payloads = [
            _job_payload(
                item,
                args.stage,
                args.output,
                args.request,
                dates,
                files_by_experiment[item["experiment_id"]],
                before_by_experiment[item["experiment_id"]],
                comparisons,
            )
            for item in performance
        ]
        results.extend(_run_jobs(payloads))
    else:
        payloads = [
            _job_payload(
                item,
                args.stage,
                args.output,
                args.request,
                dates,
                files_by_experiment[item["experiment_id"]],
                before_by_experiment[item["experiment_id"]],
                {},
            )
            for item in experiments
        ]
        results.extend(_run_jobs(payloads))

    order = {"BASELINE": 0, "NEGATIVE_CONTROL": 1, "PERFORMANCE": 2}
    results.sort(key=lambda item: (str(item["candidate_id"]), order.get(str(item["classification"]), 9)))
    _write_json(args.output, {
        "contract_version": CONTRACT_VERSION,
        "stage": args.stage,
        "adapter_feature_version": "2.0.3",
        "max_parallel_workers": MAX_PARALLEL_WORKERS,
        "experiment_results": results,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
