from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from darkest_hour.signals import LONG, SHORT


MOMENTUM_COLUMNS = ("return_24h", "return_7d", "return_30d")


@dataclass(frozen=True)
class MomentumConfig:
    """Frozen V4 cross-sectional momentum parameters for 5-minute bars."""

    bars_24h: int = 288
    bars_7d: int = 2_016
    bars_30d: int = 8_640
    liquidity_bars: int = 288
    decision_hours: tuple[int, ...] = (0, 6, 12, 18)
    min_daily_quote_volume: float = 10_000_000.0
    min_universe: int = 20
    weekdays_only: bool = True

    def __post_init__(self) -> None:
        horizons = (self.bars_24h, self.bars_7d, self.bars_30d)
        if any(value <= 0 for value in horizons):
            raise ValueError("momentum horizons must be positive")
        if tuple(sorted(horizons)) != horizons:
            raise ValueError("momentum horizons must be increasing")
        if self.liquidity_bars <= 0:
            raise ValueError("liquidity_bars must be positive")
        if not self.decision_hours:
            raise ValueError("at least one decision hour is required")
        if any(not 0 <= hour <= 23 for hour in self.decision_hours):
            raise ValueError("decision hours must lie in [0, 23]")
        if self.min_daily_quote_volume < 0.0:
            raise ValueError("minimum liquidity cannot be negative")
        if self.min_universe < 2:
            raise ValueError("minimum universe must be at least two")


@dataclass(frozen=True)
class MomentumChoice:
    symbol: str
    direction: str
    momentum_score: float
    eligible_symbols: int


def compute_momentum_features(
    bars: pd.DataFrame,
    cfg: MomentumConfig,
) -> pd.DataFrame:
    """Compute completed-bar momentum and trailing liquidity features.

    A row is knowable immediately after that row's close. The operational
    runner enters at the following 5-minute close, never on this feature row.
    """
    missing = {"close", "volume"}.difference(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {sorted(missing)}")
    if not isinstance(bars.index, pd.DatetimeIndex):
        raise TypeError("bars must have a DatetimeIndex")

    close = pd.to_numeric(bars["close"], errors="raise").astype(float)
    volume = pd.to_numeric(bars["volume"], errors="coerce").astype(float)
    result = pd.DataFrame(index=bars.index)
    result["return_24h"] = close / close.shift(cfg.bars_24h) - 1.0
    result["return_7d"] = close / close.shift(cfg.bars_7d) - 1.0
    result["return_30d"] = close / close.shift(cfg.bars_30d) - 1.0
    result["daily_quote_volume"] = (close * volume).rolling(
        cfg.liquidity_bars,
        min_periods=cfg.liquidity_bars,
    ).sum()
    return result


def decision_mask(index: pd.DatetimeIndex, cfg: MomentumConfig) -> np.ndarray:
    """Return the frozen V4 six-hour decision calendar."""
    if index.tz is None:
        raise ValueError("decision timestamps must be timezone-aware")
    mask = (index.minute == 0) & index.hour.isin(cfg.decision_hours)
    if cfg.weekdays_only:
        mask &= index.dayofweek < 5
    return np.asarray(mask, dtype=bool)


def select_momentum_symbol(
    snapshot: pd.DataFrame,
    btc_row: pd.Series,
    cfg: MomentumConfig,
) -> MomentumChoice | None:
    """Select one symbol using a BTC regime and robust cross-sectional ranks.

    The regime is long only when BTC's 7d and 30d returns are positive, short
    only when both are negative, and flat otherwise. A selected coin must agree
    with that direction at all three frozen horizons.
    """
    required = {"symbol", "daily_quote_volume", *MOMENTUM_COLUMNS}
    missing = required.difference(snapshot.columns)
    if missing:
        raise ValueError(f"snapshot missing columns: {sorted(missing)}")

    frame = snapshot.dropna(subset=list(required - {"symbol"})).copy()
    frame = frame[
        pd.to_numeric(frame["daily_quote_volume"], errors="coerce")
        >= cfg.min_daily_quote_volume
    ]
    frame = frame.sort_values("symbol", kind="stable").drop_duplicates(
        "symbol", keep="last"
    )
    if len(frame) < cfg.min_universe:
        return None

    btc_7d = float(btc_row["return_7d"])
    btc_30d = float(btc_row["return_30d"])
    if not np.isfinite(btc_7d) or not np.isfinite(btc_30d):
        return None
    if btc_7d > 0.0 and btc_30d > 0.0:
        direction = LONG
        aligned = np.logical_and.reduce(
            [frame[column].to_numpy(dtype=float) > 0.0 for column in MOMENTUM_COLUMNS]
        )
    elif btc_7d < 0.0 and btc_30d < 0.0:
        direction = SHORT
        aligned = np.logical_and.reduce(
            [frame[column].to_numpy(dtype=float) < 0.0 for column in MOMENTUM_COLUMNS]
        )
    else:
        return None

    # Percentile ranks keep a single high-volatility coin from dominating the
    # score while preserving cross-sectional ordering at every horizon.
    ranks = frame.loc[:, MOMENTUM_COLUMNS].rank(method="average", pct=True)
    frame["momentum_score"] = (2.0 * ranks - 1.0).mean(axis=1)
    candidates = frame.loc[aligned].copy()
    if candidates.empty:
        return None

    if direction == LONG:
        candidates = candidates.sort_values(
            ["momentum_score", "symbol"],
            ascending=[False, True],
            kind="stable",
        )
    else:
        candidates = candidates.sort_values(
            ["momentum_score", "symbol"],
            ascending=[True, True],
            kind="stable",
        )
    winner = candidates.iloc[0]
    return MomentumChoice(
        symbol=str(winner["symbol"]),
        direction=direction,
        momentum_score=float(winner["momentum_score"]),
        eligible_symbols=int(len(frame)),
    )


def apply_single_position(candidate_outcomes: pd.DataFrame) -> pd.DataFrame:
    """Keep the first candidate whose entry is not blocked by the open trade."""
    required = {"entry_time", "exit_time", "resolved"}
    missing = required.difference(candidate_outcomes.columns)
    if missing:
        raise ValueError(f"candidate outcomes missing columns: {sorted(missing)}")

    ordered = candidate_outcomes.sort_values(
        ["entry_time", "symbol"], kind="stable"
    ).reset_index(drop=True)
    chosen: list[int] = []
    available_at: pd.Timestamp | None = None
    for index, row in ordered.iterrows():
        if not bool(row["resolved"]):
            continue
        entry_time = pd.Timestamp(row["entry_time"])
        exit_time = pd.Timestamp(row["exit_time"])
        if available_at is not None and entry_time < available_at:
            continue
        chosen.append(index)
        available_at = exit_time
    return ordered.loc[chosen].reset_index(drop=True)
