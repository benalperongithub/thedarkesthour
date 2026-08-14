#!/usr/bin/env python3
"""Fail-fast validation of the immutable TDH dataset contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_DATASET_FIELDS = {
    "dataset_id",
    "symbol",
    "base_timeframe",
    "path",
    "sha256",
    "row_count",
    "start_ts_utc",
    "end_ts_utc",
    "columns",
    "missing_bar_count",
    "duplicate_ts_count",
    "monotonic_ts",
    "source_version",
}


class PreflightError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--verify-files", action="store_true")
    parser.add_argument("--allowed-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        require(isinstance(manifest, dict), "manifest must be an object")
        require(manifest.get("contract_version") == "tdh-data-contract-v1", "unsupported contract_version")
        require(manifest.get("timezone") == "UTC", "timezone must be UTC")
        require(manifest.get("lookahead_policy") == "closed_bar_only", "lookahead_policy must be closed_bar_only")
        require(isinstance(manifest.get("adjustment_policy"), str) and manifest["adjustment_policy"], "adjustment_policy missing")
        datasets = manifest.get("datasets")
        require(isinstance(datasets, list) and datasets, "datasets must be a non-empty array")
        ids: set[str] = set()
        checked: list[dict[str, Any]] = []
        allowed_root = args.allowed_root.resolve() if args.allowed_root else None
        for index, dataset in enumerate(datasets, start=1):
            prefix = f"dataset[{index}]"
            require(isinstance(dataset, dict), f"{prefix} must be an object")
            missing = sorted(REQUIRED_DATASET_FIELDS - set(dataset))
            require(not missing, f"{prefix}: missing fields {missing}")
            dataset_id = dataset["dataset_id"]
            require(isinstance(dataset_id, str) and dataset_id, f"{prefix}: dataset_id missing")
            require(dataset_id not in ids, f"duplicate dataset_id: {dataset_id}")
            ids.add(dataset_id)
            require(isinstance(dataset["symbol"], str) and dataset["symbol"], f"{dataset_id}: symbol missing")
            require(dataset["base_timeframe"] in {"1m", "5m", "15m", "1h"}, f"{dataset_id}: unsupported base_timeframe")
            require(isinstance(dataset["row_count"], int) and dataset["row_count"] > 0, f"{dataset_id}: row_count invalid")
            require(dataset["missing_bar_count"] == 0, f"{dataset_id}: missing bars detected")
            require(dataset["duplicate_ts_count"] == 0, f"{dataset_id}: duplicate timestamps detected")
            require(dataset["monotonic_ts"] is True, f"{dataset_id}: timestamps are not monotonic")
            require(isinstance(dataset["sha256"], str) and SHA256_RE.fullmatch(dataset["sha256"]), f"{dataset_id}: sha256 invalid")
            columns = dataset["columns"]
            require(isinstance(columns, list), f"{dataset_id}: columns must be an array")
            require({"ts", "open", "high", "low", "close", "volume"} <= set(columns), f"{dataset_id}: OHLCV schema incomplete")
            require(str(dataset["start_ts_utc"]).endswith(("Z", "+00:00")), f"{dataset_id}: start timestamp not UTC")
            require(str(dataset["end_ts_utc"]).endswith(("Z", "+00:00")), f"{dataset_id}: end timestamp not UTC")
            file_path = Path(dataset["path"])
            if args.verify_files:
                resolved = file_path.resolve(strict=True)
                if allowed_root:
                    require(resolved == allowed_root or allowed_root in resolved.parents, f"{dataset_id}: path outside allowed root")
                require(sha256_file(resolved) == dataset["sha256"], f"{dataset_id}: file hash mismatch")
            checked.append({"dataset_id": dataset_id, "symbol": dataset["symbol"], "sha256": dataset["sha256"]})

        resampling = manifest.get("resampling", {})
        require(isinstance(resampling, dict), "resampling must be an object")
        if resampling:
            require(resampling.get("label") == "right", "resampling label must be right")
            require(resampling.get("closed") == "right", "resampling closed must be right")
            require(resampling.get("incomplete_bar_policy") == "drop", "incomplete resampled bars must be dropped")
            require(resampling.get("ohlcv_aggregation") == "first,max,min,last,sum", "unexpected OHLCV aggregation")

        result = {
            "status": "DATA_PREFLIGHT_OK",
            "dataset_count": len(checked),
            "datasets": checked,
            "manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
            "offline_only": True,
        }
        encoded = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError, json.JSONDecodeError, PreflightError) as exc:
        print(f"DATA_PREFLIGHT_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
