from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from darkest_hour.signals import LONG, SHORT


@dataclass(frozen=True)
class FixedRRResult:
    exit_pos: int
    exit_time: pd.Timestamp
    exit_price: float
    exit_reason: str
    bars_held: int
    tp_price: float
    sl_price: float
    gross_return: float
    gross_r: float
    resolved: bool


def fixed_rr_levels(
    entry_price: float,
    direction: str,
    stop_pct: float,
    rr_ratio: float,
) -> tuple[float, float]:
    if entry_price <= 0.0:
        raise ValueError("entry_price must be positive")
    if stop_pct <= 0.0:
        raise ValueError("stop_pct must be positive")
    if rr_ratio <= 0.0:
        raise ValueError("rr_ratio must be positive")
    if direction == LONG:
        return entry_price * (1.0 + rr_ratio * stop_pct), entry_price * (
            1.0 - stop_pct
        )
    if direction == SHORT:
        return entry_price * (1.0 - rr_ratio * stop_pct), entry_price * (
            1.0 + stop_pct
        )
    raise ValueError(f"unknown direction: {direction!r}")


def replay_fixed_rr(
    bars: pd.DataFrame,
    entry_pos: int,
    direction: str,
    stop_pct: float,
    rr_ratio: float = 2.0,
    time_stop_bars: int = 576,
    worst_case_intrabar: bool = True,
) -> FixedRRResult:
    """Replay Phoenix's fixed-R bar semantics from the bar after entry.

    The time stop is checked before TP/SL touches on its terminal bar to match
    the Phoenix builder frozen for TDH v1. An unresolved end-of-data position
    is returned as right-censored and must not be scored as a realized trade.
    """
    required = {"high", "low", "close"}
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {sorted(missing)}")
    if not 0 <= entry_pos < len(bars):
        raise IndexError("entry_pos outside bars")
    if time_stop_bars < 0:
        raise ValueError("time_stop_bars cannot be negative")

    entry_price = float(bars["close"].iloc[entry_pos])
    tp_price, sl_price = fixed_rr_levels(
        entry_price, direction, stop_pct, rr_ratio
    )

    for pos in range(entry_pos + 1, len(bars)):
        held = pos - entry_pos
        row = bars.iloc[pos]

        if time_stop_bars and held >= time_stop_bars:
            exit_price = float(row["close"])
            return _result(
                bars,
                entry_pos,
                pos,
                entry_price,
                exit_price,
                direction,
                stop_pct,
                tp_price,
                sl_price,
                "TIME_STOP",
                resolved=True,
            )

        high = float(row["high"])
        low = float(row["low"])
        if direction == LONG:
            tp_touched = high >= tp_price
            sl_touched = low <= sl_price
        elif direction == SHORT:
            tp_touched = low <= tp_price
            sl_touched = high >= sl_price
        else:
            raise ValueError(f"unknown direction: {direction!r}")

        if sl_touched and (worst_case_intrabar or not tp_touched):
            return _result(
                bars,
                entry_pos,
                pos,
                entry_price,
                sl_price,
                direction,
                stop_pct,
                tp_price,
                sl_price,
                "SL_SINGLE_EXCHANGE",
                resolved=True,
            )
        if tp_touched:
            return _result(
                bars,
                entry_pos,
                pos,
                entry_price,
                tp_price,
                direction,
                stop_pct,
                tp_price,
                sl_price,
                "TP_SINGLE_EXCHANGE",
                resolved=True,
            )

    return _result(
        bars,
        entry_pos,
        len(bars) - 1,
        entry_price,
        float(bars["close"].iloc[-1]),
        direction,
        stop_pct,
        tp_price,
        sl_price,
        "RIGHT_CENSORED",
        resolved=False,
    )


def net_r_after_costs(
    gross_return: float,
    stop_pct: float,
    entry_time: pd.Timestamp,
    exit_time: pd.Timestamp,
    round_trip_cost_bps: float = 9.5,
    funding_apr: float = 0.1095,
) -> float:
    if stop_pct <= 0.0:
        raise ValueError("stop_pct must be positive")
    duration_years = max(
        0.0,
        (pd.Timestamp(exit_time) - pd.Timestamp(entry_time)).total_seconds()
        / (365.0 * 86_400.0),
    )
    cost_return = round_trip_cost_bps / 10_000.0
    funding_return = funding_apr * duration_years
    return float((gross_return - cost_return - funding_return) / stop_pct)


def _result(
    bars: pd.DataFrame,
    entry_pos: int,
    exit_pos: int,
    entry_price: float,
    exit_price: float,
    direction: str,
    stop_pct: float,
    tp_price: float,
    sl_price: float,
    reason: str,
    resolved: bool,
) -> FixedRRResult:
    sign = 1.0 if direction == LONG else -1.0
    gross_return = sign * (exit_price / entry_price - 1.0)
    exit_time = pd.Timestamp(bars.index[exit_pos])
    return FixedRRResult(
        exit_pos=exit_pos,
        exit_time=exit_time,
        exit_price=float(exit_price),
        exit_reason=reason,
        bars_held=int(exit_pos - entry_pos),
        tp_price=float(tp_price),
        sl_price=float(sl_price),
        gross_return=float(gross_return),
        gross_r=float(gross_return / stop_pct),
        resolved=resolved,
    )
