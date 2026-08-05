from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.reversal import (
    ReversalConfig,
    aggregate_completed_hours,
    compute_residual_features,
    fixed_horizon_single_position,
    select_reversal_pool,
    strongest_per_timestamp,
)
from darkest_hour.signals import LONG, SHORT


def _bars(periods: int = 36) -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=periods, freq="5min", tz="UTC")
    close = np.linspace(100.0, 103.0, periods)
    return pd.DataFrame(
        {
            "open": close - 0.1,
            "high": close + 0.2,
            "low": close - 0.2,
            "close": close,
            "quote_volume": 1000.0,
            "taker_buy_quote": 550.0,
            "trades": 10,
        },
        index=index,
    )


def test_hourly_aggregation_is_complete_and_points_to_next_bar() -> None:
    hourly = aggregate_completed_hours(_bars(), ReversalConfig())
    assert len(hourly) == 3
    assert hourly.index[0] == pd.Timestamp("2025-01-01 00:55", tz="UTC")
    assert hourly["decision_pos"].tolist() == [11, 23, 35]
    assert hourly["quote_volume"].tolist() == [12_000.0] * 3


def test_incomplete_hour_is_dropped() -> None:
    bars = _bars().drop(pd.Timestamp("2025-01-01 01:20", tz="UTC"))
    hourly = aggregate_completed_hours(bars, ReversalConfig())
    assert hourly.index.tolist() == [
        pd.Timestamp("2025-01-01 00:55", tz="UTC"),
        pd.Timestamp("2025-01-01 02:55", tz="UTC"),
    ]


def test_residual_features_do_not_read_future_hour() -> None:
    cfg = ReversalConfig(
        beta_hours=3,
        beta_min_hours=2,
        scale_hours=3,
        scale_min_hours=2,
        liquidity_hours=2,
        volume_median_hours=3,
    )
    coin = aggregate_completed_hours(_bars(12 * 12), cfg)
    btc = coin.copy()
    before = compute_residual_features(coin, btc, cfg)
    changed = coin.copy()
    changed.loc[changed.index[-1], "close"] *= 5.0
    after = compute_residual_features(changed, btc, cfg)
    pd.testing.assert_series_equal(before.iloc[-2], after.iloc[-2])


def test_selector_reverses_extreme_residual_and_flow() -> None:
    symbols = [f"C{i:02d}" for i in range(20)]
    frame = pd.DataFrame(
        {
            "symbol": symbols,
            "residual_z1": np.linspace(-3.0, 3.0, 20),
            "residual_z4": np.linspace(-2.0, 2.0, 20),
            "taker_imbalance": np.linspace(-0.4, 0.4, 20),
            "volume_shock": 1.5,
            "prior_24h_quote_volume": 20e6,
        }
    )
    pool = select_reversal_pool(frame, ReversalConfig(min_universe=20))
    directions = dict(zip(pool["symbol"], pool["direction"], strict=True))
    assert directions["C00"] == LONG
    assert directions["C19"] == SHORT


def test_selector_never_trades_btc_benchmark() -> None:
    symbols = ["BTCUSDT", *[f"C{i:02d}" for i in range(20)]]
    frame = pd.DataFrame(
        {
            "symbol": symbols,
            "residual_z1": [100.0, *np.linspace(-3.0, 3.0, 20)],
            "residual_z4": [100.0, *np.linspace(-2.0, 2.0, 20)],
            "taker_imbalance": [0.9, *np.linspace(-0.4, 0.4, 20)],
            "volume_shock": 1.5,
            "prior_24h_quote_volume": 20e6,
        }
    )
    pool = select_reversal_pool(frame, ReversalConfig(min_universe=20))
    assert "BTCUSDT" not in set(pool["symbol"])


def test_strongest_and_single_position_are_outcome_blind() -> None:
    times = pd.to_datetime(
        ["2025-01-01 00:00", "2025-01-01 00:00", "2025-01-01 01:00"],
        utc=True,
    )
    pool = pd.DataFrame(
        {
            "decision_time": times,
            "entry_time": times + pd.Timedelta(minutes=5),
            "exit_time_4h": times + pd.Timedelta(hours=4, minutes=5),
            "symbol": ["AAA", "BBB", "CCC"],
            "reversal_score": [2.0, 3.0, 4.0],
        }
    )
    strongest = strongest_per_timestamp(pool)
    assert strongest["symbol"].tolist() == ["BBB", "CCC"]
    selected = fixed_horizon_single_position(strongest)
    assert selected["symbol"].tolist() == ["BBB"]
