from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.audit_data_capabilities import parquet_sources, sampled_schema


def test_partitioned_sources_take_precedence(tmp_path: Path) -> None:
    root = tmp_path / "5m"
    partition = root / "year=2025" / "month=01"
    partition.mkdir(parents=True)
    pd.DataFrame({"ts": [1], "close": [2.0]}).to_parquet(
        partition / "part.parquet"
    )
    pd.DataFrame({"ignored": [1]}).to_parquet(root / "ohlcv.parquet")
    files = parquet_sources(root)
    assert files == [partition / "part.parquet"]
    assert sampled_schema(files) == ("close", "ts")


def test_schema_samples_first_and_last_partition(tmp_path: Path) -> None:
    first = tmp_path / "a.parquet"
    last = tmp_path / "z.parquet"
    pd.DataFrame({"ts": [1], "close": [2.0]}).to_parquet(first)
    pd.DataFrame({"ts": [2], "close": [3.0], "quote_volume": [4.0]}).to_parquet(
        last
    )
    assert sampled_schema([first, last]) == ("close", "quote_volume", "ts")
