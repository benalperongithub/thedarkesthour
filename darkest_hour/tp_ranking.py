from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


TP_FEATURES = (
    "adx_excess",
    "log_volume_excess",
    "trend_signed_atr",
    "breakout_signed_atr",
    "impulse_signed_atr",
    "compression_strength",
    "log_daily_quote_volume",
    "is_long",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "family_trend_pullback",
    "family_compression_breakout",
    "family_impulse_continuation",
    "family_count",
)


def _sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-values))


def _feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    entry_time = pd.to_datetime(frame["entry_time"], utc=True, errors="raise")
    hour = entry_time.dt.hour + entry_time.dt.minute / 60.0
    dow = entry_time.dt.dayofweek.astype(float)
    output = pd.DataFrame(index=frame.index)
    for column in TP_FEATURES[:7]:
        output[column] = pd.to_numeric(frame[column], errors="coerce")
    output["is_long"] = (
        frame["direction"].astype(str).str.lower().eq("long").astype(float)
    )
    output["hour_sin"] = np.sin(2.0 * np.pi * hour / 24.0)
    output["hour_cos"] = np.cos(2.0 * np.pi * hour / 24.0)
    output["dow_sin"] = np.sin(2.0 * np.pi * dow / 7.0)
    output["dow_cos"] = np.cos(2.0 * np.pi * dow / 7.0)
    for column in TP_FEATURES[12:]:
        output[column] = pd.to_numeric(frame[column], errors="coerce")
    return output


@dataclass(frozen=True)
class TPLogisticRanker:
    medians: np.ndarray
    means: np.ndarray
    scales: np.ndarray
    coefficients: np.ndarray

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        matrix = _feature_frame(frame).loc[:, TP_FEATURES].to_numpy(dtype=float)
        matrix[~np.isfinite(matrix)] = np.nan
        matrix = np.where(np.isnan(matrix), self.medians, matrix)
        matrix = (matrix - self.means) / self.scales
        design = np.column_stack([np.ones(len(matrix)), matrix])
        return _sigmoid(design @ self.coefficients)


def fit_tp_ranker(
    frame: pd.DataFrame,
    *,
    alpha: float = 10.0,
    max_iterations: int = 100,
) -> TPLogisticRanker:
    if alpha < 0.0:
        raise ValueError("alpha cannot be negative")
    target = frame["exit_reason"].astype(str).eq("TP_SINGLE_EXCHANGE").to_numpy(
        dtype=float
    )
    if len(target) < 2 or np.unique(target).size != 2:
        raise ValueError("training data must contain TP and non-TP outcomes")

    matrix = _feature_frame(frame).loc[:, TP_FEATURES].to_numpy(dtype=float)
    matrix[~np.isfinite(matrix)] = np.nan
    medians = np.nanmedian(matrix, axis=0)
    medians = np.where(np.isfinite(medians), medians, 0.0)
    matrix = np.where(np.isnan(matrix), medians, matrix)
    means = matrix.mean(axis=0)
    scales = matrix.std(axis=0)
    scales = np.where(scales > 1e-12, scales, 1.0)
    matrix = (matrix - means) / scales
    design = np.column_stack([np.ones(len(matrix)), matrix])

    base_rate = float(target.mean())
    coefficients = np.zeros(design.shape[1], dtype=float)
    coefficients[0] = np.log(base_rate / (1.0 - base_rate))
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
    return TPLogisticRanker(
        medians=medians,
        means=means,
        scales=scales,
        coefficients=coefficients,
    )
