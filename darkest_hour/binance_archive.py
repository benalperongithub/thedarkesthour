from __future__ import annotations

import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

import pandas as pd


BASE_URL = "https://data.binance.vision/data/futures/um/monthly"
SUPPORTED_TYPES = frozenset({"fundingRate", "premiumIndexKlines"})
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass(frozen=True)
class ArchiveSpec:
    symbol: str
    data_type: str
    month: str
    interval: str = "1h"

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Z0-9_]{3,30}", self.symbol):
            raise ValueError(f"invalid Binance symbol: {self.symbol!r}")
        if self.data_type not in SUPPORTED_TYPES:
            raise ValueError(f"unsupported data type: {self.data_type!r}")
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", self.month):
            raise ValueError(f"month must be YYYY-MM: {self.month!r}")
        if not re.fullmatch(r"\d+[mhdw]", self.interval):
            raise ValueError(f"invalid interval: {self.interval!r}")

    @property
    def filename(self) -> str:
        if self.data_type == "fundingRate":
            return f"{self.symbol}-fundingRate-{self.month}.zip"
        return f"{self.symbol}-{self.interval}-{self.month}.zip"

    @property
    def relative_path(self) -> str:
        if self.data_type == "fundingRate":
            return f"fundingRate/{self.symbol}/{self.filename}"
        return (
            f"premiumIndexKlines/{self.symbol}/{self.interval}/{self.filename}"
        )

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.relative_path}"

    @property
    def checksum_url(self) -> str:
        return f"{self.url}.CHECKSUM"


def month_range(start_month: str, end_month: str) -> list[str]:
    start = pd.Period(start_month, freq="M")
    end = pd.Period(end_month, freq="M")
    if end < start:
        raise ValueError("end month cannot precede start month")
    return [str(period) for period in pd.period_range(start, end, freq="M")]


def parse_checksum(text: str, expected_filename: str) -> str:
    parts = text.strip().split()
    if len(parts) < 2:
        raise ValueError("checksum file must contain digest and filename")
    digest = parts[0].lower()
    filename = parts[-1].lstrip("*")
    if not _SHA256.fullmatch(digest):
        raise ValueError("checksum digest is not SHA-256")
    if PurePosixPath(filename).name != expected_filename:
        raise ValueError(
            f"checksum filename mismatch: {filename!r} != {expected_filename!r}"
        )
    return digest


def verify_sha256(payload: bytes, expected_digest: str) -> str:
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_digest.lower():
        raise ValueError(f"SHA-256 mismatch: expected {expected_digest}, got {actual}")
    return actual


def inspect_zip(payload: bytes) -> dict[str, object]:
    """Inspect one Binance archive without extracting arbitrary paths."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        files = [info for info in archive.infolist() if not info.is_dir()]
        if len(files) != 1:
            raise ValueError(f"expected one archive member, found {len(files)}")
        info = files[0]
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
            raise ValueError(f"unsafe archive member: {info.filename!r}")
        if path.suffix.lower() != ".csv":
            raise ValueError(f"archive member is not CSV: {info.filename!r}")
        raw = archive.read(info)
    if not raw:
        raise ValueError("CSV member is empty")
    text = raw.decode("utf-8-sig")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("CSV member has no non-empty rows")
    first = lines[0].split(",")
    has_header = any(not _looks_numeric(value) for value in first)
    return {
        "member": info.filename,
        "member_bytes": len(raw),
        "nonempty_lines": len(lines),
        "columns": len(first),
        "has_header": has_header,
        "first_row": lines[0][:500],
        "last_row": lines[-1][:500],
    }


def _looks_numeric(value: str) -> bool:
    try:
        float(value.strip())
    except ValueError:
        return False
    return True
