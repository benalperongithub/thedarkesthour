from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.exits import ExitPolicy, replay_exit_policy
from darkest_hour.signals import LONG


def bars(rows: list[tuple[float, float, float]]) -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=len(rows), freq="5min", tz="UTC")
    return pd.DataFrame(rows, columns=["high", "low", "close"], index=index)


def test_breakeven_activates_on_following_bar() -> None:
    policy = ExitPolicy("BE", "breakeven", 2.0, 20, trigger_r=1.0)
    data = bars([(100, 100, 100), (103, 99, 102), (101, 99, 100)])
    result = replay_exit_policy(data, 0, LONG, 0.02, policy)
    assert result.exit_reason == "MANAGED_STOP"
    assert result.bars_held == 2
    assert np.isclose(result.gross_r, 0.0)


def test_ambiguous_activation_bar_keeps_original_stop() -> None:
    policy = ExitPolicy("BE", "breakeven", 2.0, 20, trigger_r=1.0)
    data = bars([(100, 100, 100), (103, 97, 100)])
    result = replay_exit_policy(data, 0, LONG, 0.02, policy)
    assert np.isclose(result.gross_r, -1.0)


def test_trailing_stop_uses_prior_bar_update() -> None:
    policy = ExitPolicy("TRAIL", "trailing", 3.0, 20, trigger_r=1.0, trail_r=1.0)
    data = bars([(100, 100, 100), (105, 99, 104), (104, 102, 103)])
    result = replay_exit_policy(data, 0, LONG, 0.02, policy)
    assert result.exit_reason == "MANAGED_STOP"
    assert np.isclose(result.exit_price, 103.0)
    assert np.isclose(result.gross_r, 1.5)


def test_partial_exit_weights_trigger_and_runner() -> None:
    policy = ExitPolicy(
        "PARTIAL", "partial", 3.0, 20, trigger_r=1.0, partial_fraction=0.5
    )
    data = bars([(100, 100, 100), (103, 99, 102), (106, 101, 106)])
    result = replay_exit_policy(data, 0, LONG, 0.02, policy)
    assert result.partial_taken
    assert result.exit_reason == "MANAGED_TARGET"
    assert np.isclose(result.gross_r, 2.0)


def test_partial_and_final_target_on_same_bar_are_both_accounted() -> None:
    policy = ExitPolicy(
        "PARTIAL", "partial", 3.0, 20, trigger_r=1.0, partial_fraction=0.5
    )
    data = bars([(100, 100, 100), (106, 99, 106)])
    result = replay_exit_policy(data, 0, LONG, 0.02, policy)
    assert result.partial_taken
    assert np.isclose(result.gross_r, 2.0)
