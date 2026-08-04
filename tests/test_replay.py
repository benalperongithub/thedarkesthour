from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.replay import net_r_after_costs, replay_fixed_rr
from darkest_hour.signals import LONG, SHORT


def _bars(rows: list[tuple[float, float, float]]) -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=len(rows), freq="5min", tz="UTC")
    return pd.DataFrame(rows, columns=["high", "low", "close"], index=index)


def test_long_tp_is_two_r_and_starts_after_entry_bar() -> None:
    bars = _bars([(100, 100, 100), (105, 99, 101)])
    result = replay_fixed_rr(bars, 0, LONG, stop_pct=0.02)
    assert result.exit_reason == "TP_SINGLE_EXCHANGE"
    assert result.bars_held == 1
    assert np.isclose(result.gross_r, 2.0)


def test_short_stop_is_minus_one_r() -> None:
    bars = _bars([(100, 100, 100), (103, 99, 101)])
    result = replay_fixed_rr(bars, 0, SHORT, stop_pct=0.02)
    assert result.exit_reason == "SL_SINGLE_EXCHANGE"
    assert np.isclose(result.gross_r, -1.0)


def test_intrabar_tie_is_conservatively_a_loss() -> None:
    bars = _bars([(100, 100, 100), (105, 97, 100)])
    result = replay_fixed_rr(bars, 0, LONG, stop_pct=0.02)
    assert result.exit_reason == "SL_SINGLE_EXCHANGE"


def test_time_stop_precedes_touch_on_terminal_bar() -> None:
    bars = _bars([(100, 100, 100), (101, 99, 100), (105, 99, 101)])
    result = replay_fixed_rr(
        bars, 0, LONG, stop_pct=0.02, time_stop_bars=2
    )
    assert result.exit_reason == "TIME_STOP"
    assert result.bars_held == 2
    assert result.exit_price == 101


def test_costs_reduce_gross_r() -> None:
    entry = pd.Timestamp("2025-01-01", tz="UTC")
    exit_ = entry + pd.Timedelta(hours=8)
    net_r = net_r_after_costs(0.04, 0.02, entry, exit_)
    assert 1.9 < net_r < 2.0
