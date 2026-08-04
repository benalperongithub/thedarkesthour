from __future__ import annotations

import numpy as np
import pandas as pd

from darkest_hour.tp_ranking import fit_tp_ranker
from scripts.run_tp_union_ranker import _union_frames


def _frame(family: str, reasons: list[str]) -> pd.DataFrame:
    rows = len(reasons)
    rng = np.random.default_rng(20260805)
    entry = pd.date_range("2023-01-01", periods=rows, freq="6h", tz="UTC")
    return pd.DataFrame(
        {
            "symbol": "AAA",
            "family": family,
            "entry_time": entry,
            "exit_time": entry + pd.Timedelta(hours=2),
            "direction": np.where(np.arange(rows) % 2, "Long", "Short"),
            "stop_pct": 0.02,
            "net_R": np.where(np.asarray(reasons) == "TP_SINGLE_EXCHANGE", 2.0, -1.0),
            "exit_reason": reasons,
            "bars_held": 24,
            "adx_excess": rng.normal(size=rows),
            "log_volume_excess": rng.normal(size=rows),
            "trend_signed_atr": rng.normal(size=rows),
            "breakout_signed_atr": rng.normal(size=rows),
            "impulse_signed_atr": rng.normal(size=rows),
            "compression_strength": rng.normal(size=rows),
            "log_daily_quote_volume": rng.normal(18.0, 1.0, size=rows),
            "daily_quote_volume": rng.lognormal(18.0, 1.0, size=rows),
            "raw_strength": rng.normal(size=rows),
        }
    )


def test_union_deduplicates_same_trade_and_preserves_confluence() -> None:
    reasons = ["TP_SINGLE_EXCHANGE", "SL_SINGLE_EXCHANGE"]
    left = _frame("trend_pullback", reasons)
    right = left.copy()
    right["family"] = "compression_breakout"
    union = _union_frames([left, right])
    assert len(union) == len(left)
    assert (union["family_count"] == 2).all()
    assert (union["family_trend_pullback"] == 1).all()
    assert (union["family_compression_breakout"] == 1).all()


def test_tp_ranker_predicts_finite_probability() -> None:
    reasons = ["TP_SINGLE_EXCHANGE", "SL_SINGLE_EXCHANGE"] * 100
    union = _union_frames([_frame("compression_breakout", reasons)])
    model = fit_tp_ranker(union)
    probability = model.predict_proba(union.iloc[:10])
    assert np.isfinite(probability).all()
    assert ((probability > 0.0) & (probability < 1.0)).all()
