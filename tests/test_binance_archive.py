from __future__ import annotations

import hashlib
import io
import zipfile

import pytest

from darkest_hour.binance_archive import (
    ArchiveSpec,
    inspect_zip,
    month_range,
    normalize_funding,
    normalize_premium,
    parse_checksum,
    verify_sha256,
)


def _zip(member: str, content: bytes = b"1,2,3\n4,5,6\n") -> bytes:
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, content)
    return target.getvalue()


def test_official_archive_paths() -> None:
    funding = ArchiveSpec("BTCUSDT", "fundingRate", "2024-01")
    premium = ArchiveSpec("BTCUSDT", "premiumIndexKlines", "2024-01")
    assert funding.relative_path == (
        "fundingRate/BTCUSDT/BTCUSDT-fundingRate-2024-01.zip"
    )
    assert premium.relative_path == (
        "premiumIndexKlines/BTCUSDT/1h/BTCUSDT-1h-2024-01.zip"
    )
    assert funding.checksum_url.endswith(".zip.CHECKSUM")


def test_month_range_is_inclusive() -> None:
    assert month_range("2023-11", "2024-02") == [
        "2023-11",
        "2023-12",
        "2024-01",
        "2024-02",
    ]


def test_checksum_filename_and_digest_are_verified() -> None:
    payload = b"archive"
    digest = hashlib.sha256(payload).hexdigest()
    assert parse_checksum(f"{digest}  BTCUSDT.zip\n", "BTCUSDT.zip") == digest
    assert verify_sha256(payload, digest) == digest
    with pytest.raises(ValueError, match="filename mismatch"):
        parse_checksum(f"{digest}  ETHUSDT.zip\n", "BTCUSDT.zip")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_sha256(b"changed", digest)


def test_zip_inspection_reports_shape_without_extracting() -> None:
    result = inspect_zip(_zip("BTCUSDT.csv"))
    assert result["member"] == "BTCUSDT.csv"
    assert result["nonempty_lines"] == 2
    assert result["columns"] == 3
    assert result["has_header"] is False


def test_zip_rejects_path_traversal_and_multiple_members() -> None:
    with pytest.raises(ValueError, match="unsafe archive member"):
        inspect_zip(_zip("../escape.csv"))
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("one.csv", "1,2\n")
        archive.writestr("two.csv", "3,4\n")
    with pytest.raises(ValueError, match="expected one archive member"):
        inspect_zip(target.getvalue())


def test_funding_schema_normalizes_to_causal_timestamp() -> None:
    import pandas as pd

    raw = pd.DataFrame(
        {
            "calc_time": [1704067200000],
            "funding_interval_hours": [8],
            "last_funding_rate": ["0.00010000"],
        }
    )
    result = normalize_funding(raw)
    assert result["ts"].iloc[0] == pd.Timestamp("2024-01-01", tz="UTC")
    assert result["funding_rate"].iloc[0] == pytest.approx(0.0001)


def test_premium_becomes_available_after_close_millisecond() -> None:
    import pandas as pd

    raw = pd.DataFrame(
        {
            "open_time": [1704067200000],
            "open": ["0.001"],
            "high": ["0.002"],
            "low": ["-0.001"],
            "close": ["0.0005"],
            "close_time": [1704070799999],
            "count": [720],
        }
    )
    result = normalize_premium(raw)
    assert result["open_ts"].iloc[0] == pd.Timestamp("2024-01-01", tz="UTC")
    assert result["ts"].iloc[0] == pd.Timestamp("2024-01-01 01:00", tz="UTC")
