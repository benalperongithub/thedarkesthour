from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from darkest_hour.signals import LONG, SHORT


@dataclass(frozen=True)
class ReversalConfig:
    """Frozen V6 residual-reversal signal parameters."""

    bars_per_hour: int = 12
    beta_hours: int = 720
    beta_min_hours: int = 240
    scale_hours: int = 720
    scale_min_hours: int = 240
    liquidity_hours: int = 24
    volume_median_hours: int = 168
    min_daily_quote_volume: float = 10_000_000.0
    min_universe: int = 20
    tail_fraction: float = 0.10
    min_abs_z1: float = 1.0
    min_abs_z4: float = 0.5
    min_volume_shock: float = 1.0
    weekdays_only: bool = True

    def __post_init__(self) -> None:
        positive = (
            self.bars_per_hour,
            self.beta_hours,
            self.beta_min_hours,
            self.scale_hours,
            self.scale_min_hours,
            self.liquidity_hours,
            self.volume_median_hours,
        )
        if any(value <= 0 for value in positive):
            raise ValueError("rolling windows must be positive")
        if self.beta_min_hours > self.beta_hours:
            raise ValueError("beta minimum cannot exceed its window")
        if self.scale_min_hours > self.scale_hours:
            raise ValueError("scale minimum cannot exceed its window")
        if not 0.0 < self.tail_fraction < 0.5:
            raise ValueError("tail_fraction must lie in (0, 0.5)")
        if self.min_universe < 2:
            raise ValueError("min_universe must be at least two")


def aggregate_completed_hours(
    bars: pd.DataFrame,
    cfg: ReversalConfig,
) -> pd.DataFrame:
    """Aggregate complete UTC hours while preserving source-bar positions.

    The returned ``decision_time`` is the timestamp of the final 5-minute row
    in the hour. A runner must enter no earlier than ``decision_pos + 1``.
    This convention is causal whether the vendor labels bars by open or close.
    """
    required = {
        "open",
        "high",
        "low",
        "close",
        "quote_volume",
        "taker_buy_quote",
        "trades",
    }
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {sorted(missing)}")
    if not isinstance(bars.index, pd.DatetimeIndex):
        raise TypeError("bars must have a DatetimeIndex")
    if bars.index.tz is None:
        raise ValueError("bar timestamps must be timezone-aware")
    if not bars.index.is_monotonic_increasing or bars.index.has_duplicates:
        raise ValueError("bar timestamps must be sorted and unique")

    work = bars.loc[:, sorted(required)].copy()
    work["source_pos"] = np.arange(len(work), dtype=np.int64)
    work["source_ts"] = work.index
    work["hour"] = work.index.floor("h")
    grouped = work.groupby("hour", sort=True)
    hourly = grouped.agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        quote_volume=("quote_volume", "sum"),
        taker_buy_quote=("taker_buy_quote", "sum"),
        trades=("trades", "sum"),
        decision_time=("source_ts", "last"),
        decision_pos=("source_pos", "max"),
        first_time=("source_ts", "first"),
        bar_count=("source_ts", "size"),
    )
    expected_span = pd.Timedelta(minutes=5 * (cfg.bars_per_hour - 1))
    complete = (hourly["bar_count"] == cfg.bars_per_hour) & (
        hourly["decision_time"] - hourly["first_time"] == expected_span
    )
    hourly = hourly.loc[complete].copy()
    hourly.index = pd.DatetimeIndex(hourly["decision_time"], name="decision_time")
    return hourly.drop(columns=["first_time", "bar_count", "decision_time"])


def compute_residual_features(
    hourly: pd.DataFrame,
    btc_hourly: pd.DataFrame,
    cfg: ReversalConfig,
) -> pd.DataFrame:
    """Compute causal BTC-residual price and aggressive-flow features."""
    required = {"close", "quote_volume", "taker_buy_quote", "decision_pos"}
    for label, frame in (("coin", hourly), ("BTC", btc_hourly)):
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{label} hourly bars missing: {sorted(missing)}")

    close = pd.to_numeric(hourly["close"], errors="raise").astype(float)
    btc_close = pd.to_numeric(
        btc_hourly["close"].reindex(hourly.index), errors="coerce"
    ).astype(float)
    coin_r1 = close.pct_change(fill_method=None)
    btc_r1 = btc_close.pct_change(fill_method=None)
    coin_r4 = close.pct_change(4, fill_method=None)
    btc_r4 = btc_close.pct_change(4, fill_method=None)

    # Shift the beta by one completed hour. The shock being ranked therefore
    # cannot alter the hedge ratio used to classify itself.
    covariance = coin_r1.rolling(
        cfg.beta_hours, min_periods=cfg.beta_min_hours
    ).cov(btc_r1)
    variance = btc_r1.rolling(
        cfg.beta_hours, min_periods=cfg.beta_min_hours
    ).var()
    beta = (covariance / variance.replace(0.0, np.nan)).shift(1)
    residual_1h = coin_r1 - beta * btc_r1
    residual_4h = coin_r4 - beta * btc_r4
    scale_1h = residual_1h.rolling(
        cfg.scale_hours, min_periods=cfg.scale_min_hours
    ).std(ddof=0).shift(1)
    scale_4h = residual_4h.rolling(
        cfg.scale_hours, min_periods=cfg.scale_min_hours
    ).std(ddof=0).shift(1)

    quote_volume = pd.to_numeric(
        hourly["quote_volume"], errors="coerce"
    ).astype(float)
    taker_buy = pd.to_numeric(
        hourly["taker_buy_quote"], errors="coerce"
    ).astype(float)
    prior_volume_median = quote_volume.rolling(
        cfg.volume_median_hours,
        min_periods=min(
            cfg.volume_median_hours,
            max(24, cfg.volume_median_hours // 3),
        ),
    ).median().shift(1)

    result = pd.DataFrame(index=hourly.index)
    result["decision_pos"] = hourly["decision_pos"].astype(np.int64)
    result["beta_btc"] = beta
    result["residual_1h"] = residual_1h
    result["residual_4h"] = residual_4h
    result["residual_z1"] = residual_1h / scale_1h.replace(0.0, np.nan)
    result["residual_z4"] = residual_4h / scale_4h.replace(0.0, np.nan)
    result["taker_imbalance"] = 2.0 * taker_buy / quote_volume.replace(
        0.0, np.nan
    ) - 1.0
    result["volume_shock"] = quote_volume / prior_volume_median.replace(
        0.0, np.nan
    )
    # Liquidity excludes the current shock hour and is fully known beforehand.
    result["prior_24h_quote_volume"] = quote_volume.rolling(
        cfg.liquidity_hours, min_periods=cfg.liquidity_hours
    ).sum().shift(1)
    return result


def select_reversal_pool(
    snapshot: pd.DataFrame,
    cfg: ReversalConfig,
) -> pd.DataFrame:
    """Return the causal cross-sectional reversal candidates at one hour."""
    required = {
        "symbol",
        "residual_z1",
        "residual_z4",
        "taker_imbalance",
        "volume_shock",
        "prior_24h_quote_volume",
    }
    missing = required.difference(snapshot.columns)
    if missing:
        raise ValueError(f"snapshot missing columns: {sorted(missing)}")
    numeric = sorted(required - {"symbol"})
    frame = snapshot.dropna(subset=numeric).copy()
    # BTC is the hedge benchmark, not a coin residual candidate. Its true
    # self-residual is zero, but floating-point noise divided by a near-zero
    # rolling scale can otherwise manufacture an extreme z-score.
    frame = frame[frame["symbol"] != "BTCUSDT"]
    frame = frame[
        frame["prior_24h_quote_volume"] >= cfg.min_daily_quote_volume
    ]
    frame = frame.sort_values("symbol", kind="stable").drop_duplicates(
        "symbol", keep="last"
    )
    if len(frame) < cfg.min_universe:
        return frame.iloc[0:0].assign(direction=pd.Series(dtype=str))

    frame["residual_rank"] = frame["residual_z1"].rank(
        method="average", pct=True
    )
    long_mask = (
        (frame["residual_rank"] <= cfg.tail_fraction)
        & (frame["residual_z1"] <= -cfg.min_abs_z1)
        & (frame["residual_z4"] <= -cfg.min_abs_z4)
        & (frame["taker_imbalance"] < 0.0)
        & (frame["volume_shock"] >= cfg.min_volume_shock)
    )
    short_mask = (
        (frame["residual_rank"] >= 1.0 - cfg.tail_fraction)
        & (frame["residual_z1"] >= cfg.min_abs_z1)
        & (frame["residual_z4"] >= cfg.min_abs_z4)
        & (frame["taker_imbalance"] > 0.0)
        & (frame["volume_shock"] >= cfg.min_volume_shock)
    )
    pool = frame.loc[long_mask | short_mask].copy()
    if pool.empty:
        return pool.assign(direction=pd.Series(dtype=str))
    pool["direction"] = np.where(long_mask.loc[pool.index], LONG, SHORT)
    pool["reversal_score"] = (
        pool["residual_z1"].abs()
        + 0.5 * pool["residual_z4"].abs()
        + 0.5 * pool["taker_imbalance"].abs()
    )
    pool["eligible_symbols"] = len(frame)
    return pool.sort_values(
        ["reversal_score", "symbol"],
        ascending=[False, True],
        kind="stable",
    )


def strongest_per_timestamp(pool: pd.DataFrame) -> pd.DataFrame:
    required = {"decision_time", "reversal_score", "symbol"}
    missing = required.difference(pool.columns)
    if missing:
        raise ValueError(f"pool missing columns: {sorted(missing)}")
    if pool.empty:
        return pool.copy()
    ordered = pool.sort_values(
        ["decision_time", "reversal_score", "symbol"],
        ascending=[True, False, True],
        kind="stable",
    )
    return ordered.drop_duplicates("decision_time", keep="first").reset_index(
        drop=True
    )


def fixed_horizon_single_position(
    candidates: pd.DataFrame,
    horizon: str = "4h",
) -> pd.DataFrame:
    """Apply a one-global-position book using a fixed, outcome-blind horizon."""
    exit_column = f"exit_time_{horizon}"
    required = {"entry_time", exit_column, "symbol"}
    missing = required.difference(candidates.columns)
    if missing:
        raise ValueError(f"candidates missing columns: {sorted(missing)}")
    ordered = candidates.dropna(subset=[exit_column]).sort_values(
        ["entry_time", "symbol"], kind="stable"
    )
    chosen: list[int] = []
    available_at: pd.Timestamp | None = None
    for index, row in ordered.iterrows():
        entry_time = pd.Timestamp(row["entry_time"])
        if available_at is not None and entry_time < available_at:
            continue
        chosen.append(index)
        available_at = pd.Timestamp(row[exit_column])
    return ordered.loc[chosen].reset_index(drop=True)
