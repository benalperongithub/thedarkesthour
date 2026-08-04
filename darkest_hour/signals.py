from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd


LONG = "Long"
SHORT = "Short"
NEUTRAL = "Neutral"

FAMILIES = (
    "trend_pullback",
    "compression_breakout",
    "failed_breakout",
    "impulse_continuation",
)


@dataclass(frozen=True)
class SignalConfig:
    """Frozen v1 signal parameters.

    Values may be overridden by a Phoenix YAML only as a declared experiment.
    Defaults are intentionally shared across families so a family comparison
    does not hide a large per-family optimisation grid.
    """

    family: str = "trend_pullback"
    ema_fast: int = 48
    ema_slow: int = 192
    atr_period: int = 50
    adx_period: int = 50
    adx_threshold: float = 20.0
    channel_bars: int = 48
    volume_window: int = 288
    volume_ratio_min: float = 1.20
    compression_window: int = 576
    compression_quantile: float = 0.25
    impulse_bars: int = 3
    impulse_atr: float = 1.25
    weekdays_only: bool = True

    def __post_init__(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"family must be one of {FAMILIES}, got {self.family!r}")
        for name in (
            "ema_fast",
            "ema_slow",
            "atr_period",
            "adx_period",
            "channel_bars",
            "volume_window",
            "compression_window",
            "impulse_bars",
        ):
            if int(getattr(self, name)) < 2:
                raise ValueError(f"{name} must be at least 2")
        if self.ema_fast >= self.ema_slow:
            raise ValueError("ema_fast must be smaller than ema_slow")
        if not 0.0 < self.compression_quantile < 1.0:
            raise ValueError("compression_quantile must lie in (0, 1)")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> "SignalConfig":
        fields = cls.__dataclass_fields__
        values = {
            name: raw[f"tdh_{name}"]
            for name in fields
            if f"tdh_{name}" in raw
        }
        return cls(**values)


def _required_columns(data: pd.DataFrame) -> None:
    missing = {"high", "low", "close", "volume"}.difference(data.columns)
    if missing:
        raise ValueError(f"OHLCV data missing columns: {sorted(missing)}")


def _wilder(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(
        alpha=1.0 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def compute_features(data: pd.DataFrame, cfg: SignalConfig) -> pd.DataFrame:
    """Compute completed-bar features without reading future rows."""
    _required_columns(data)
    high = pd.to_numeric(data["high"], errors="raise").astype(float)
    low = pd.to_numeric(data["low"], errors="raise").astype(float)
    close = pd.to_numeric(data["close"], errors="raise").astype(float)
    volume = pd.to_numeric(data["volume"], errors="coerce").astype(float)

    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = _wilder(true_range, cfg.atr_period)

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0.0), up_move, 0.0),
        index=data.index,
        dtype=float,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0.0), down_move, 0.0),
        index=data.index,
        dtype=float,
    )
    adx_atr = _wilder(true_range, cfg.adx_period).replace(0.0, np.nan)
    plus_di = 100.0 * _wilder(plus_dm, cfg.adx_period) / adx_atr
    minus_di = 100.0 * _wilder(minus_dm, cfg.adx_period) / adx_atr
    di_sum = (plus_di + minus_di).replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    adx = _wilder(dx, cfg.adx_period)

    ema_fast = close.ewm(span=cfg.ema_fast, adjust=False).mean()
    ema_slow = close.ewm(span=cfg.ema_slow, adjust=False).mean()
    channel_high = high.shift(1).rolling(cfg.channel_bars).max()
    channel_low = low.shift(1).rolling(cfg.channel_bars).min()

    volume_baseline = volume.shift(1).rolling(
        cfg.volume_window,
        min_periods=max(10, cfg.volume_window // 3),
    ).median()
    volume_ratio = volume / volume_baseline.replace(0.0, np.nan)

    bb_mean = close.rolling(20).mean()
    bb_std = close.rolling(20).std(ddof=0)
    bb_width = 4.0 * bb_std / bb_mean.replace(0.0, np.nan)
    # Compression must be known before the breakout bar itself.
    compression_rank = bb_width.shift(1).rolling(
        cfg.compression_window,
        min_periods=max(50, cfg.compression_window // 3),
    ).rank(pct=True)

    impulse_return = close.pct_change(cfg.impulse_bars)
    atr_fraction = atr / close.replace(0.0, np.nan)
    # Approximate rolling quote turnover from base volume * close. At entry
    # this feature is shifted one row by build_candidate_frame, so only bars
    # completed before the entry bar contribute to the operational liquidity
    # floor.
    daily_quote_volume = (volume * close).rolling(
        288,
        min_periods=288,
    ).sum()

    return pd.DataFrame(
        {
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "atr": atr,
            "atr_fraction": atr_fraction,
            "adx": adx,
            "plus_di": plus_di,
            "minus_di": minus_di,
            "channel_high": channel_high,
            "channel_low": channel_low,
            "volume_ratio": volume_ratio,
            "compression_rank": compression_rank,
            "impulse_return": impulse_return,
            "daily_quote_volume": daily_quote_volume,
        },
        index=data.index,
    )


def _weekday_mask(index: pd.Index, enabled: bool) -> pd.Series:
    if not enabled:
        return pd.Series(True, index=index)
    timestamp = pd.to_datetime(index, utc=True, errors="coerce")
    if timestamp.isna().all():
        raise ValueError("weekdays_only requires a datetime-like index")
    return pd.Series(timestamp.dayofweek < 5, index=index)


def raw_signal_sides(
    data: pd.DataFrame,
    features: pd.DataFrame,
    cfg: SignalConfig,
) -> tuple[pd.Series, pd.Series]:
    """Return long/short conditions decided at each completed bar."""
    close = pd.to_numeric(data["close"], errors="raise").astype(float)
    high = pd.to_numeric(data["high"], errors="raise").astype(float)
    low = pd.to_numeric(data["low"], errors="raise").astype(float)

    trend_long = (
        (features["ema_fast"] > features["ema_slow"])
        & (features["adx"] >= cfg.adx_threshold)
        & (features["plus_di"] > features["minus_di"])
    )
    trend_short = (
        (features["ema_fast"] < features["ema_slow"])
        & (features["adx"] >= cfg.adx_threshold)
        & (features["minus_di"] > features["plus_di"])
    )
    liquid_event = features["volume_ratio"] >= cfg.volume_ratio_min

    if cfg.family == "trend_pullback":
        long = (
            trend_long
            & (close > features["ema_fast"])
            & (close.shift(1) <= features["ema_fast"].shift(1))
            & (low <= features["ema_fast"])
            & liquid_event
        )
        short = (
            trend_short
            & (close < features["ema_fast"])
            & (close.shift(1) >= features["ema_fast"].shift(1))
            & (high >= features["ema_fast"])
            & liquid_event
        )
    elif cfg.family == "compression_breakout":
        compressed = features["compression_rank"] <= cfg.compression_quantile
        long = trend_long & compressed & (close > features["channel_high"]) & liquid_event
        short = trend_short & compressed & (close < features["channel_low"]) & liquid_event
    elif cfg.family == "failed_breakout":
        long = (
            trend_long
            & (low < features["channel_low"])
            & (close > features["channel_low"])
            & liquid_event
        )
        short = (
            trend_short
            & (high > features["channel_high"])
            & (close < features["channel_high"])
            & liquid_event
        )
    else:  # impulse_continuation
        threshold = cfg.impulse_atr * features["atr_fraction"]
        long = (
            trend_long
            & (features["impulse_return"] >= threshold)
            & (close > features["channel_high"])
            & liquid_event
        )
        short = (
            trend_short
            & (features["impulse_return"] <= -threshold)
            & (close < features["channel_low"])
            & liquid_event
        )

    weekday = _weekday_mask(data.index, cfg.weekdays_only)
    return (long & weekday).fillna(False), (short & weekday).fillna(False)


def build_entry_tokens(data: pd.DataFrame, cfg: SignalConfig) -> pd.Series:
    """Build the S1 token stream.

    A signal decided from completed bar i becomes executable at i+1. The
    Phoenix `edge_only` policy is responsible for suppressing repeated tokens;
    this function deliberately does not inspect position state.
    """
    features = compute_features(data, cfg)
    long, short = raw_signal_sides(data, features, cfg)
    raw = pd.Series(NEUTRAL, index=data.index, dtype="string")
    raw.loc[long & ~short] = LONG
    raw.loc[short & ~long] = SHORT
    return raw.shift(1).fillna(NEUTRAL).astype("string")


def build_candidate_frame(data: pd.DataFrame, cfg: SignalConfig) -> pd.DataFrame:
    """Return causally aligned entry features and a frozen strength score.

    A candidate at row ``i`` is decided from completed row ``i-1`` and enters
    at row ``i`` close, matching :func:`build_entry_tokens`. The score is an
    outcome-blind, dimensionless diagnostic used only to break simultaneous
    cross-symbol signals; it is not fitted on trade results.
    """
    features = compute_features(data, cfg)
    long, short = raw_signal_sides(data, features, cfg)
    raw = pd.Series(NEUTRAL, index=data.index, dtype="string")
    raw.loc[long & ~short] = LONG
    raw.loc[short & ~long] = SHORT
    direction = raw.shift(1).fillna(NEUTRAL).astype("string")

    aligned = features.shift(1).copy()
    decision_close = pd.to_numeric(data["close"], errors="raise").shift(1)
    sign = pd.Series(0.0, index=data.index)
    sign.loc[direction.eq(LONG)] = 1.0
    sign.loc[direction.eq(SHORT)] = -1.0

    atr = aligned["atr"].replace(0.0, np.nan)
    atr_fraction = aligned["atr_fraction"].replace(0.0, np.nan)
    aligned["trend_signed_atr"] = (
        sign * (aligned["ema_fast"] - aligned["ema_slow"]) / atr
    )
    aligned["impulse_signed_atr"] = (
        sign * aligned["impulse_return"] / atr_fraction
    )
    aligned["breakout_signed_atr"] = np.where(
        direction.eq(LONG),
        (decision_close - aligned["channel_high"]) / atr,
        np.where(
            direction.eq(SHORT),
            (aligned["channel_low"] - decision_close) / atr,
            np.nan,
        ),
    )
    aligned["adx_excess"] = (
        aligned["adx"] - cfg.adx_threshold
    ) / max(cfg.adx_threshold, 1.0)
    aligned["log_volume_excess"] = np.log(
        aligned["volume_ratio"].clip(lower=1e-12) / cfg.volume_ratio_min
    )
    aligned["compression_strength"] = (
        cfg.compression_quantile - aligned["compression_rank"]
    ) / cfg.compression_quantile
    aligned["log_daily_quote_volume"] = np.log(
        aligned["daily_quote_volume"].clip(lower=1.0)
    )

    common = (
        aligned["adx_excess"]
        + aligned["log_volume_excess"]
        + aligned["trend_signed_atr"].clip(lower=0.0)
    )
    if cfg.family == "trend_pullback":
        strength = common
    elif cfg.family == "compression_breakout":
        strength = (
            common
            + aligned["breakout_signed_atr"].clip(lower=0.0)
            + aligned["compression_strength"].clip(lower=0.0)
        )
    elif cfg.family == "failed_breakout":
        strength = common + (-aligned["breakout_signed_atr"]).clip(lower=0.0)
    else:
        strength = (
            common
            + aligned["breakout_signed_atr"].clip(lower=0.0)
            + aligned["impulse_signed_atr"].clip(lower=0.0)
        )

    aligned.insert(0, "direction", direction)
    aligned.insert(
        1,
        "entry_price",
        pd.to_numeric(data["close"], errors="raise").astype(float),
    )
    aligned["raw_strength"] = strength.where(direction.ne(NEUTRAL))
    return aligned
