from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.ranking import fit_logistic_ranker
from scripts.run_walkforward_ranker import _select, _training_slice


def _training_frame(rows: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(20260805)
    entry = pd.date_range("2023-01-01", periods=rows, freq="6h", tz="UTC")
    direction = np.where(np.arange(rows) % 2, "Long", "Short")
    signal = rng.normal(size=rows)
    return pd.DataFrame(
        {
            "symbol": np.where(np.arange(rows) % 3, "AAA", "BBB"),
            "entry_time": entry,
            "exit_time": entry + pd.Timedelta(hours=2),
            "direction": direction,
            "net_R": np.where(signal > 0.0, 2.0, -1.0),
            "adx_excess": signal,
            "log_volume_excess": rng.normal(size=rows),
            "trend_signed_atr": rng.normal(size=rows),
            "breakout_signed_atr": rng.normal(size=rows),
            "compression_strength": rng.normal(size=rows),
            "log_daily_quote_volume": rng.normal(18.0, 1.0, size=rows),
        }
    )


def test_logistic_ranker_returns_finite_probabilities() -> None:
    frame = _training_frame()
    model = fit_logistic_ranker(frame)
    probability = model.predict_proba(frame.iloc[:10])
    assert np.isfinite(probability).all()
    assert ((probability > 0.0) & (probability < 1.0)).all()


def test_ranked_selector_abstains_and_keeps_one_global_position() -> None:
    frame = _training_frame(4)
    frame["predicted_win_probability"] = [0.49, 0.70, 0.90, 0.80]
    frame.loc[:, "entry_time"] = pd.to_datetime(
        ["2025-01-01 00:00", "2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 03:00"],
        utc=True,
    )
    frame.loc[:, "exit_time"] = pd.to_datetime(
        ["2025-01-01 01:00", "2025-01-01 02:00", "2025-01-01 02:00", "2025-01-01 04:00"],
        utc=True,
    )
    selected = _select(
        frame,
        "predicted_win_probability",
        minimum=0.50,
    )
    assert selected["predicted_win_probability"].tolist() == [0.70, 0.80]


def test_training_slice_uses_exit_time_not_entry_time() -> None:
    frame = _training_frame(3)
    cutoff = pd.Timestamp("2024-01-01", tz="UTC")
    frame.loc[:, "entry_time"] = pd.to_datetime(
        ["2023-12-01", "2023-12-15", "2024-01-02"], utc=True
    )
    frame.loc[:, "exit_time"] = pd.to_datetime(
        ["2023-12-02", "2024-01-02", "2024-01-03"], utc=True
    )
    train = _training_slice(frame, cutoff)
    assert len(train) == 1
    assert train["exit_time"].max() < cutoff
