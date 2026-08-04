from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


BASE_FEATURES = (
    "adx_excess",
    "log_volume_excess",
    "trend_signed_atr",
    "breakout_signed_atr",
    "compression_strength",
    "log_daily_quote_volume",
    "is_long",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "symbol_win_prior",
)


@dataclass(frozen=True)
class LogisticRanker:
    feature_names: tuple[str, ...]
    medians: np.ndarray
    means: np.ndarray
    scales: np.ndarray
    coefficients: np.ndarray
    global_win_rate: float
    symbol_win_priors: dict[str, float]

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        features = _feature_frame(
            frame,
            self.symbol_win_priors,
            self.global_win_rate,
        ).loc[:, self.feature_names]
        matrix = features.to_numpy(dtype=float)
        matrix[~np.isfinite(matrix)] = np.nan
        matrix = np.where(np.isnan(matrix), self.medians, matrix)
        matrix = (matrix - self.means) / self.scales
        design = np.column_stack([np.ones(len(matrix)), matrix])
        return _sigmoid(design @ self.coefficients)


def _sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-values))


def _symbol_priors(
    frame: pd.DataFrame,
    target: np.ndarray,
    prior_strength: float,
) -> tuple[float, dict[str, float]]:
    global_rate = float(target.mean())
    work = pd.DataFrame(
        {
            "symbol": frame["symbol"].astype(str).to_numpy(),
            "win": target,
        }
    )
    grouped = work.groupby("symbol", sort=False)["win"].agg(["sum", "count"])
    prior = (
        grouped["sum"] + prior_strength * global_rate
    ) / (grouped["count"] + prior_strength)
    return global_rate, {str(key): float(value) for key, value in prior.items()}


def _leave_one_out_symbol_prior(
    frame: pd.DataFrame,
    target: np.ndarray,
    prior_strength: float,
) -> np.ndarray:
    work = pd.DataFrame(
        {
            "symbol": frame["symbol"].astype(str).to_numpy(),
            "win": target,
        },
        index=frame.index,
    )
    symbol_sum = work.groupby("symbol")["win"].transform("sum").to_numpy()
    symbol_count = work.groupby("symbol")["win"].transform("count").to_numpy()
    global_loo = (target.sum() - target) / max(len(target) - 1, 1)
    return (
        symbol_sum - target + prior_strength * global_loo
    ) / (symbol_count - 1.0 + prior_strength)


def _feature_frame(
    frame: pd.DataFrame,
    symbol_priors: dict[str, float],
    global_win_rate: float,
) -> pd.DataFrame:
    entry_time = pd.to_datetime(frame["entry_time"], utc=True, errors="raise")
    hour = entry_time.dt.hour + entry_time.dt.minute / 60.0
    dow = entry_time.dt.dayofweek.astype(float)
    output = pd.DataFrame(index=frame.index)
    for column in BASE_FEATURES[:6]:
        output[column] = pd.to_numeric(frame[column], errors="coerce")
    output["is_long"] = (
        frame["direction"].astype(str).str.lower().eq("long").astype(float)
    )
    output["hour_sin"] = np.sin(2.0 * np.pi * hour / 24.0)
    output["hour_cos"] = np.cos(2.0 * np.pi * hour / 24.0)
    output["dow_sin"] = np.sin(2.0 * np.pi * dow / 7.0)
    output["dow_cos"] = np.cos(2.0 * np.pi * dow / 7.0)
    output["symbol_win_prior"] = (
        frame["symbol"].astype(str).map(symbol_priors).fillna(global_win_rate)
    )
    return output


def fit_logistic_ranker(
    frame: pd.DataFrame,
    *,
    alpha: float = 10.0,
    prior_strength: float = 20.0,
    max_iterations: int = 100,
) -> LogisticRanker:
    if alpha < 0.0:
        raise ValueError("alpha cannot be negative")
    if prior_strength <= 0.0:
        raise ValueError("prior_strength must be positive")
    target = (pd.to_numeric(frame["net_R"], errors="raise") > 0.0).to_numpy(
        dtype=float
    )
    if len(target) < 2 or np.unique(target).size != 2:
        raise ValueError("training data must contain wins and losses")

    global_rate, symbol_priors = _symbol_priors(
        frame,
        target,
        prior_strength,
    )
    features = _feature_frame(frame, symbol_priors, global_rate).loc[
        :, BASE_FEATURES
    ]
    # Training rows must not receive a prior containing their own target. The
    # stored full-training prior is used only for genuinely later rows.
    features["symbol_win_prior"] = _leave_one_out_symbol_prior(
        frame,
        target,
        prior_strength,
    )
    matrix = features.to_numpy(dtype=float)
    matrix[~np.isfinite(matrix)] = np.nan
    medians = np.nanmedian(matrix, axis=0)
    medians = np.where(np.isfinite(medians), medians, 0.0)
    matrix = np.where(np.isnan(matrix), medians, matrix)
    means = matrix.mean(axis=0)
    scales = matrix.std(axis=0)
    scales = np.where(scales > 1e-12, scales, 1.0)
    matrix = (matrix - means) / scales
    design = np.column_stack([np.ones(len(matrix)), matrix])

    coefficients = np.zeros(design.shape[1], dtype=float)
    coefficients[0] = np.log(global_rate / (1.0 - global_rate))
    penalty = np.r_[0.0, np.full(matrix.shape[1], alpha)]

    for _ in range(max_iterations):
        probability = _sigmoid(design @ coefficients)
        weight = np.clip(probability * (1.0 - probability), 1e-8, None)
        gradient = design.T @ (probability - target) + penalty * coefficients
        hessian = (design.T * weight) @ design + np.diag(penalty + 1e-10)
        step = np.linalg.solve(hessian, gradient)
        coefficients -= step
        if float(np.max(np.abs(step))) < 1e-8:
            break

    return LogisticRanker(
        feature_names=BASE_FEATURES,
        medians=medians,
        means=means,
        scales=scales,
        coefficients=coefficients,
        global_win_rate=global_rate,
        symbol_win_priors=symbol_priors,
    )
