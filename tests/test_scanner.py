from __future__ import annotations

import pandas as pd

from scripts.run_causal_scanner import _groups, _select


def test_selector_takes_strongest_and_enforces_one_global_position() -> None:
    t0 = pd.Timestamp("2025-01-01 00:00", tz="UTC")
    t1 = t0 + pd.Timedelta(minutes=5)
    t2 = t0 + pd.Timedelta(minutes=10)
    t3 = t0 + pd.Timedelta(minutes=15)
    frame = pd.DataFrame(
        [
            {"entry_time": t0, "exit_time": t2, "symbol": "AAA", "raw_strength": 1.0},
            {"entry_time": t0, "exit_time": t1, "symbol": "BBB", "raw_strength": 2.0},
            {"entry_time": t1, "exit_time": t2, "symbol": "CCC", "raw_strength": 9.0},
            {"entry_time": t3, "exit_time": t3 + pd.Timedelta(minutes=5), "symbol": "DDD", "raw_strength": 1.0},
        ]
    )
    selected = _select(_groups(frame), rng=None)
    assert selected["symbol"].tolist() == ["BBB", "DDD"]
