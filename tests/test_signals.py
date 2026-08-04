from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from darkest_hour.signals import (
    FAMILIES,
    NEUTRAL,
    SignalConfig,
    build_candidate_frame,
    build_entry_tokens,
)


def bars(n: int = 1600) -> pd.DataFrame:
    rng = np.random.default_rng(20260804)
    index = pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC")
    returns = rng.normal(0.00005, 0.003, n)
    close = 100.0 * np.exp(np.cumsum(returns))
    spread = rng.uniform(0.0005, 0.006, n) * close
    return pd.DataFrame(
        {
            "open": np.r_[close[0], close[:-1]],
            "high": close + spread,
            "low": close - spread,
            "close": close,
            "volume": rng.lognormal(8.0, 0.8, n),
        },
        index=index,
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_prefix_invariance_proves_no_future_rows_are_read(family: str) -> None:
    data = bars()
    cfg = SignalConfig(family=family)
    full = build_entry_tokens(data, cfg)
    cut = 1200
    prefix = build_entry_tokens(data.iloc[:cut], cfg)
    pd.testing.assert_series_equal(full.iloc[:cut], prefix)


@pytest.mark.parametrize("family", FAMILIES)
def test_output_is_aligned_and_first_token_is_neutral(family: str) -> None:
    data = bars()
    output = build_entry_tokens(data, SignalConfig(family=family))
    assert output.index.equals(data.index)
    assert output.iloc[0] == NEUTRAL
    assert set(output.dropna().unique()).issubset({"Long", "Short", "Neutral"})


def test_unknown_family_is_rejected() -> None:
    with pytest.raises(ValueError, match="family must be one of"):
        SignalConfig(family="historically_best_magic")


@pytest.mark.parametrize("family", FAMILIES)
def test_candidate_features_are_prefix_invariant(family: str) -> None:
    data = bars()
    cfg = SignalConfig(family=family)
    full = build_candidate_frame(data, cfg)
    cut = 1200
    prefix = build_candidate_frame(data.iloc[:cut], cfg)
    pd.testing.assert_frame_equal(full.iloc[:cut], prefix)


def test_daily_quote_volume_uses_only_completed_bars() -> None:
    data = bars()
    output = build_candidate_frame(data, SignalConfig())
    first_eligible_row = 288
    expected = (data["volume"] * data["close"]).iloc[:288].sum()

    assert np.isclose(
        output["daily_quote_volume"].iloc[first_eligible_row],
        expected,
    )
