from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.momentum import (
    MomentumConfig,
    apply_single_position,
    compute_momentum_features,
    decision_mask,
    select_momentum_symbol,
)
from darkest_hour.signals import LONG, SHORT


def test_features_do_not_read_future_rows() -> None:
    index = pd.date_range("2025-01-01", periods=12, freq="5min", tz="UTC")
    bars = pd.DataFrame(
        {"close": np.arange(100.0, 112.0), "volume": 10.0}, index=index
    )
    cfg = MomentumConfig(
        bars_24h=2,
        bars_7d=4,
        bars_30d=6,
        liquidity_bars=2,
        min_universe=2,
    )
    before = compute_momentum_features(bars, cfg)
    changed = bars.copy()
    changed.loc[index[-1], "close"] = 9_999.0
    after = compute_momentum_features(changed, cfg)
    pd.testing.assert_series_equal(before.loc[index[-2]], after.loc[index[-2]])


def test_decision_calendar_is_six_hour_weekday_only() -> None:
    index = pd.date_range("2025-01-03", periods=72 * 4, freq="5min", tz="UTC")
    selected = index[decision_mask(index, MomentumConfig(min_universe=2))]
    assert list(selected.hour) == [0, 6, 12, 18]
    assert set(selected.dayofweek) == {4}


def _snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["AAA", "BBB", "CCC"],
            "return_24h": [0.01, 0.03, -0.04],
            "return_7d": [0.02, 0.04, -0.05],
            "return_30d": [0.03, 0.05, -0.06],
            "daily_quote_volume": [20e6, 30e6, 40e6],
        }
    )


def test_selector_uses_btc_regime_and_strongest_aligned_coin() -> None:
    cfg = MomentumConfig(min_universe=2)
    long = select_momentum_symbol(
        _snapshot(), pd.Series({"return_7d": 0.1, "return_30d": 0.2}), cfg
    )
    short = select_momentum_symbol(
        _snapshot(), pd.Series({"return_7d": -0.1, "return_30d": -0.2}), cfg
    )
    assert long is not None and (long.symbol, long.direction) == ("BBB", LONG)
    assert short is not None and (short.symbol, short.direction) == ("CCC", SHORT)


def test_mixed_btc_regime_stays_flat() -> None:
    choice = select_momentum_symbol(
        _snapshot(),
        pd.Series({"return_7d": 0.1, "return_30d": -0.2}),
        MomentumConfig(min_universe=2),
    )
    assert choice is None


def test_single_position_removes_overlapping_candidates() -> None:
    times = pd.to_datetime(
        ["2025-01-01 00:05", "2025-01-01 06:05", "2025-01-01 12:05"],
        utc=True,
    )
    candidates = pd.DataFrame(
        {
            "symbol": ["AAA", "BBB", "CCC"],
            "entry_time": times,
            "exit_time": [times[1] + pd.Timedelta(hours=1), times[2], times[2]],
            "resolved": [True, True, True],
        }
    )
    selected = apply_single_position(candidates)
    assert selected["symbol"].tolist() == ["AAA", "CCC"]
