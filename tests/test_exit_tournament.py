from __future__ import annotations

import pandas as pd

from darkest_hour.exits import POLICIES
from darkest_hour.signals import LONG, SHORT
from scripts.run_exit_tournament_v5 import select_for_fold


def test_nested_selector_uses_only_pre_cutoff_labels_and_can_choose_short() -> None:
    rows = []
    start = pd.Timestamp("2023-01-01", tz="UTC")
    for policy in POLICIES:
        for number in range(140):
            entry = start + pd.Timedelta(days=2 * number)
            direction = LONG if number % 2 == 0 else SHORT
            if policy.name == "BE1_2R_48H" and direction == SHORT:
                net_r = 0.40
            else:
                net_r = -0.10
            rows.append(
                {
                    "symbol": f"S{number % 5}",
                    "entry_time": entry,
                    "exit_time": entry + pd.Timedelta(hours=12),
                    "direction": direction,
                    "exit_policy": policy.name,
                    "resolved": True,
                    "net_R": net_r,
                }
            )
    outcomes = pd.DataFrame(rows)
    winner, _ = select_for_fold(
        outcomes,
        train_start=start,
        fold_start=pd.Timestamp("2024-01-01", tz="UTC"),
        min_train=60,
    )
    assert winner["exit_policy"] == "BE1_2R_48H"
    assert winner["direction_mode"] == "SHORT_ONLY"
    assert pd.Timestamp(winner["train_last_exit"]) < pd.Timestamp(
        "2024-01-01", tz="UTC"
    )
