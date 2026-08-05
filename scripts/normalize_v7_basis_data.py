from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from darkest_hour.binance_archive import (
    normalize_funding,
    normalize_premium,
    read_verified_archive,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize checksum-verified Binance V7 funding/premium archives."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(manifest_path)
    required = {"symbol", "data_type", "month", "status", "archive_path", "sha256"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"manifest missing columns: {sorted(missing)}")
    errors = manifest[manifest["status"] == "error"]
    if not errors.empty:
        raise RuntimeError(f"download manifest contains {len(errors)} errors")
    verified = manifest[manifest["status"] == "verified"].copy()
    if verified.empty:
        raise RuntimeError("download manifest contains no verified archives")

    print("TDH V7 VERIFIED ARCHIVE NORMALIZATION")
    print("verified archives:", len(verified))
    print("symbols:", verified["symbol"].nunique())

    audit_rows: list[dict[str, object]] = []
    grouped = verified.groupby(["symbol", "data_type"], sort=True)
    for number, ((symbol, data_type), group) in enumerate(grouped, 1):
        frames: list[pd.DataFrame] = []
        for _, row in group.sort_values("month", kind="stable").iterrows():
            raw = read_verified_archive(Path(row["archive_path"]), str(row["sha256"]))
            normalized = (
                normalize_funding(raw)
                if data_type == "fundingRate"
                else normalize_premium(raw)
            )
            frames.append(normalized)
        combined = pd.concat(frames, ignore_index=True)
        duplicate_rows = int(combined.duplicated("ts").sum())
        combined = (
            combined.drop_duplicates("ts", keep="last")
            .sort_values("ts", kind="stable")
            .reset_index(drop=True)
        )
        symbol_root = output_root / str(symbol)
        symbol_root.mkdir(parents=True, exist_ok=True)
        filename = (
            "funding_rate.parquet"
            if data_type == "fundingRate"
            else "premium_index_1h.parquet"
        )
        target = symbol_root / filename
        combined.to_parquet(target, index=False)
        if data_type == "fundingRate":
            gap_count = int(
                (
                    combined["ts"].diff().dt.total_seconds().div(3600)
                    > combined["funding_interval_hours"] + 1e-9
                ).sum()
            )
        else:
            gap_count = int((combined["ts"].diff() > pd.Timedelta(hours=1)).sum())
        audit_rows.append(
            {
                "symbol": symbol,
                "data_type": data_type,
                "archives": len(group),
                "rows": len(combined),
                "duplicate_rows_before_dedup": duplicate_rows,
                "gap_count": gap_count,
                "ts_min": combined["ts"].min(),
                "ts_max": combined["ts"].max(),
                "output_path": str(target),
            }
        )
        print(
            f"[{number:03d}/{len(grouped):03d}] {symbol} {data_type}: "
            f"archives={len(group)} rows={len(combined):,} gaps={gap_count}",
            flush=True,
        )

    audit = pd.DataFrame(audit_rows)
    audit_path = output_root / "v7_normalization_audit.csv"
    audit.to_csv(audit_path, index=False)
    pivot = audit.pivot(index="symbol", columns="data_type", values="rows")
    complete_symbols = int(pivot.dropna().shape[0])
    print("\nNORMALIZATION SUMMARY")
    print("symbols with both funding and premium:", complete_symbols)
    print("duplicate rows before dedup:", int(audit["duplicate_rows_before_dedup"].sum()))
    print("gaps reported:", int(audit["gap_count"].sum()))
    print("V7 NORMALIZATION VERDICT:", "PASS" if complete_symbols > 0 else "FAIL")
    print("WROTE", audit_path)


if __name__ == "__main__":
    main()
