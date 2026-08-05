from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


TARGET_COLUMNS = (
    "quote_volume",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "funding_rate",
    "fundingRate",
    "open_interest",
    "openInterest",
    "mark_price",
    "markPrice",
    "index_price",
    "indexPrice",
    "premium_index",
    "basis",
    "liquidation_volume",
)

AUXILIARY_TERMS = (
    "funding",
    "premium",
    "basis",
    "interest",
    "mark",
    "index",
    "liquidat",
    "aggtrade",
    "bookticker",
    "depth",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory causal features available in the local market-data tree."
    )
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--exchange", default="binance")
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def parquet_sources(tf_root: Path) -> list[Path]:
    parts = sorted(tf_root.glob("year=*/**/*.parquet"))
    if parts:
        return parts
    monolith = tf_root / "ohlcv.parquet"
    return [monolith] if monolith.exists() else []


def sampled_schema(files: list[Path]) -> tuple[str, ...]:
    samples = [files[0]] if len(files) == 1 else [files[0], files[-1]]
    columns: set[str] = set()
    for path in samples:
        columns.update(pq.ParquetFile(path).schema_arrow.names)
    return tuple(sorted(columns))


def main() -> None:
    args = parse_args()
    exchange_root = Path(args.data_root) / args.exchange
    if not exchange_root.is_dir():
        raise FileNotFoundError(exchange_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    dataset_rows: list[dict[str, object]] = []
    auxiliary_rows: list[dict[str, object]] = []
    coverage: Counter[tuple[str, str]] = Counter()
    tf_symbols: Counter[str] = Counter()

    symbols = sorted(path for path in exchange_root.iterdir() if path.is_dir())
    for number, symbol_root in enumerate(symbols, start=1):
        symbol = symbol_root.name
        found_tfs: list[str] = []
        for tf_root in sorted(path for path in symbol_root.iterdir() if path.is_dir()):
            files = parquet_sources(tf_root)
            if not files:
                continue
            columns = sampled_schema(files)
            tf = tf_root.name
            found_tfs.append(tf)
            tf_symbols[tf] += 1
            for column in columns:
                coverage[(tf, column)] += 1
            dataset_rows.append(
                {
                    "symbol": symbol,
                    "timeframe": tf,
                    "parquet_files": len(files),
                    "first_file": str(files[0]),
                    "last_file": str(files[-1]),
                    "columns": ",".join(columns),
                    **{
                        f"has_{column}": column in columns
                        for column in TARGET_COLUMNS
                    },
                }
            )

        for path in symbol_root.rglob("*"):
            if not path.is_file():
                continue
            lowered = path.name.lower()
            if any(term in lowered for term in AUXILIARY_TERMS):
                auxiliary_rows.append(
                    {
                        "symbol": symbol,
                        "path": str(path),
                        "size_bytes": path.stat().st_size,
                    }
                )
        print(
            f"[{number:02d}/{len(symbols):02d}] {symbol}: "
            f"timeframes={','.join(found_tfs) if found_tfs else 'NONE'}",
            flush=True,
        )

    datasets = pd.DataFrame(dataset_rows)
    coverage_rows = [
        {
            "timeframe": tf,
            "column": column,
            "symbols_with_column": count,
            "symbols_with_timeframe": tf_symbols[tf],
            "coverage_pct": 100.0 * count / tf_symbols[tf],
        }
        for (tf, column), count in sorted(coverage.items())
    ]
    coverage_frame = pd.DataFrame(coverage_rows)
    auxiliary = pd.DataFrame(
        auxiliary_rows,
        columns=["symbol", "path", "size_bytes"],
    )

    datasets.to_csv(output_root / "dataset_inventory.csv", index=False)
    coverage_frame.to_csv(output_root / "column_coverage.csv", index=False)
    auxiliary.to_csv(output_root / "auxiliary_files.csv", index=False)

    print("\nDATA CAPABILITY SUMMARY")
    print("symbols:", len(symbols))
    print("datasets:", len(datasets))
    print("timeframe coverage:", dict(sorted(tf_symbols.items())))
    print("\nTARGET COLUMN COVERAGE")
    target = coverage_frame[coverage_frame["column"].isin(TARGET_COLUMNS)]
    if target.empty:
        print("NONE")
    else:
        print(target.to_string(index=False, float_format=lambda value: f"{value:.1f}"))
    print("\nAUXILIARY FILES:", len(auxiliary))
    if len(auxiliary):
        print(auxiliary.head(50).to_string(index=False))
    print("\nWROTE", output_root)


if __name__ == "__main__":
    main()
