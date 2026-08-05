from __future__ import annotations

import argparse
import json
import socket
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from darkest_hour.binance_archive import (
    ArchiveSpec,
    inspect_zip,
    month_range,
    parse_checksum,
    verify_sha256,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and verify a bounded Binance USD-M V7 data smoke."
    )
    symbols = parser.add_mutually_exclusive_group(required=True)
    symbols.add_argument("--symbols", nargs="+")
    symbols.add_argument(
        "--symbols-from-data-root",
        help="Directory whose immediate subdirectories are symbol names.",
    )
    parser.add_argument("--start-month", required=True)
    parser.add_argument("--end-month", required=True)
    parser.add_argument(
        "--data-types",
        nargs="+",
        default=["fundingRate", "premiumIndexKlines"],
        choices=["fundingRate", "premiumIndexKlines"],
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def fetch(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TheDarkestHourResearch/7.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def download_one(
    spec: ArchiveSpec,
    output_root: Path,
    timeout: float,
    dry_run: bool,
) -> dict[str, object]:
    base = {
        "symbol": spec.symbol,
        "data_type": spec.data_type,
        "interval": "" if spec.data_type == "fundingRate" else spec.interval,
        "month": spec.month,
        "url": spec.url,
    }
    if dry_run:
        return {**base, "status": "dry_run"}

    target = output_root / spec.relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        checksum_payload = fetch(spec.checksum_url, timeout)
        expected = parse_checksum(
            checksum_payload.decode("utf-8-sig"), spec.filename
        )
        payload = fetch(spec.url, timeout)
        actual = verify_sha256(payload, expected)
        inspection = inspect_zip(payload)
        # Atomic replacement prevents a killed download leaving a valid-looking
        # partial archive. Existing verified files are deliberately rechecked.
        temporary = target.with_suffix(target.suffix + ".partial")
        temporary.write_bytes(payload)
        temporary.replace(target)
        target.with_suffix(target.suffix + ".CHECKSUM").write_bytes(
            checksum_payload
        )
        return {
            **base,
            "status": "verified",
            "archive_path": str(target),
            "archive_bytes": len(payload),
            "sha256": actual,
            **inspection,
        }
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {**base, "status": "not_available", "error": "HTTP 404"}
        return {**base, "status": "error", "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        return {**base, "status": "error", "error": repr(exc)}
    except Exception as exc:  # Preserve a full manifest instead of hiding a file.
        return {**base, "status": "error", "error": repr(exc)}


def main() -> None:
    args = parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")
    if args.timeout <= 0.0:
        raise ValueError("timeout must be positive")
    if args.progress_every <= 0:
        raise ValueError("progress-every must be positive")
    if args.symbols:
        symbols = sorted({symbol.upper() for symbol in args.symbols})
    else:
        symbol_root = Path(args.symbols_from_data_root)
        if not symbol_root.is_dir():
            raise ValueError(f"symbol data root does not exist: {symbol_root}")
        symbols = sorted(
            path.name.upper() for path in symbol_root.iterdir() if path.is_dir()
        )
    months = month_range(args.start_month, args.end_month)
    specs = [
        ArchiveSpec(symbol, data_type, month, args.interval)
        for symbol in symbols
        for data_type in args.data_types
        for month in months
    ]
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    print("TDH V7 BINANCE BASIS/FUNDING DATA SMOKE")
    print("symbols:", symbols)
    print("months:", months[0], "->", months[-1], "inclusive")
    print("data types:", args.data_types)
    print("archives planned:", len(specs))
    print("dry run:", args.dry_run)

    rows: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                download_one,
                spec,
                output_root,
                args.timeout,
                args.dry_run,
            ): spec
            for spec in specs
        }
        for count, future in enumerate(as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            if len(specs) <= 50 or count % args.progress_every == 0 or count == len(specs):
                print(
                    f"[{count:04d}/{len(specs):04d}] {row['symbol']} "
                    f"{row['data_type']} {row['month']}: {row['status']}",
                    flush=True,
                )

    manifest = pd.DataFrame(rows).sort_values(
        ["symbol", "data_type", "month"], kind="stable"
    )
    manifest_path = output_root / "v7_download_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    counts = manifest["status"].value_counts().to_dict()
    summary = {
        "symbols": symbols,
        "months": months,
        "data_types": args.data_types,
        "interval": args.interval,
        "archives_planned": len(specs),
        "status_counts": counts,
    }
    (output_root / "v7_download_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("\nSTATUS")
    print(pd.Series(counts).to_string())
    verified = manifest[manifest["status"] == "verified"]
    if not verified.empty:
        columns = [
            "symbol",
            "data_type",
            "month",
            "archive_bytes",
            "member",
            "nonempty_lines",
            "columns",
            "has_header",
        ]
        print("\nVERIFIED SCHEMA AUDIT")
        print(verified[columns].to_string(index=False))
    errors = manifest[manifest["status"] == "error"]
    if args.dry_run:
        verdict = "DRY_RUN"
    else:
        verdict = "PASS" if errors.empty and not verified.empty else "FAIL"
    print("\nV7 DATA SMOKE VERDICT:", verdict)
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
