from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from darkest_hour.replay import FixedRRResult, replay_fixed_rr
from darkest_hour.signals import LONG, SHORT


@dataclass(frozen=True)
class ExitPolicy:
    name: str
    kind: str
    target_r: float
    time_stop_bars: int
    trigger_r: float | None = None
    trail_r: float | None = None
    partial_fraction: float | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"fixed", "breakeven", "trailing", "partial"}:
            raise ValueError(f"unknown exit kind: {self.kind}")
        if self.target_r <= 0.0 or self.time_stop_bars <= 0:
            raise ValueError("target and time stop must be positive")
        if self.kind != "fixed" and (self.trigger_r is None or self.trigger_r <= 0):
            raise ValueError("managed exits require a positive trigger")
        if self.kind == "trailing" and (self.trail_r is None or self.trail_r <= 0):
            raise ValueError("trailing exits require a positive trail distance")
        if self.kind == "partial" and not (
            self.partial_fraction is not None and 0 < self.partial_fraction < 1
        ):
            raise ValueError("partial exits require a fraction in (0, 1)")


POLICIES = (
    ExitPolicy("FIXED_2R_48H", "fixed", target_r=2.0, time_stop_bars=576),
    ExitPolicy("FIXED_2R_24H", "fixed", target_r=2.0, time_stop_bars=288),
    ExitPolicy(
        "BE1_2R_48H",
        "breakeven",
        target_r=2.0,
        trigger_r=1.0,
        time_stop_bars=576,
    ),
    ExitPolicy(
        "TRAIL1_3R_48H",
        "trailing",
        target_r=3.0,
        trigger_r=1.0,
        trail_r=1.0,
        time_stop_bars=576,
    ),
    ExitPolicy(
        "PARTIAL50_1R_3R_48H",
        "partial",
        target_r=3.0,
        trigger_r=1.0,
        partial_fraction=0.50,
        time_stop_bars=576,
    ),
)


@dataclass(frozen=True)
class ManagedExitResult:
    exit_pos: int
    exit_time: pd.Timestamp
    exit_price: float
    exit_reason: str
    bars_held: int
    gross_return: float
    gross_r: float
    resolved: bool
    partial_taken: bool


def policy_by_name(name: str) -> ExitPolicy:
    for policy in POLICIES:
        if policy.name == name:
            return policy
    raise KeyError(name)


def replay_exit_policy(
    bars: pd.DataFrame,
    entry_pos: int,
    direction: str,
    stop_pct: float,
    policy: ExitPolicy,
) -> ManagedExitResult:
    if policy.kind == "fixed":
        fixed = replay_fixed_rr(
            bars,
            entry_pos,
            direction,
            stop_pct,
            rr_ratio=policy.target_r,
            time_stop_bars=policy.time_stop_bars,
            worst_case_intrabar=True,
        )
        return _from_fixed(fixed)
    return _managed_replay(bars, entry_pos, direction, stop_pct, policy)


def _managed_replay(
    bars: pd.DataFrame,
    entry_pos: int,
    direction: str,
    stop_pct: float,
    policy: ExitPolicy,
) -> ManagedExitResult:
    if direction not in {LONG, SHORT}:
        raise ValueError(f"unknown direction: {direction!r}")
    if stop_pct <= 0.0:
        raise ValueError("stop_pct must be positive")
    if not 0 <= entry_pos < len(bars):
        raise IndexError("entry_pos outside bars")

    sign = 1.0 if direction == LONG else -1.0
    entry = float(bars["close"].iloc[entry_pos])
    initial_stop = entry * (1.0 - sign * stop_pct)
    target = entry * (1.0 + sign * policy.target_r * stop_pct)
    trigger = entry * (1.0 + sign * float(policy.trigger_r) * stop_pct)
    active_stop = initial_stop
    activated = False
    partial_taken = False
    best = entry

    for pos in range(entry_pos + 1, len(bars)):
        held = pos - entry_pos
        row = bars.iloc[pos]
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])

        if held >= policy.time_stop_bars:
            return _managed_result(
                bars,
                entry_pos,
                pos,
                entry,
                close,
                direction,
                stop_pct,
                "TIME_STOP",
                True,
                partial_taken,
                policy,
            )

        stop_touched = low <= active_stop if direction == LONG else high >= active_stop
        target_touched = low <= target if direction == SHORT else high >= target

        # The stop always wins an ambiguous bar. Stop changes and trailing
        # updates only become active on the next bar, avoiding intrabar path
        # assumptions that cannot be recovered from OHLC data.
        if stop_touched:
            return _managed_result(
                bars,
                entry_pos,
                pos,
                entry,
                active_stop,
                direction,
                stop_pct,
                "MANAGED_STOP",
                True,
                partial_taken,
                policy,
            )
        if target_touched:
            # Reaching a partial policy's final target necessarily crosses its
            # lower partial trigger first. With the original stop already
            # ruled out above, account for both fills even when they occur in
            # the same OHLC bar.
            if policy.kind == "partial" and not partial_taken:
                partial_taken = True
            return _managed_result(
                bars,
                entry_pos,
                pos,
                entry,
                target,
                direction,
                stop_pct,
                "MANAGED_TARGET",
                True,
                partial_taken,
                policy,
            )

        trigger_touched = low <= trigger if direction == SHORT else high >= trigger
        if trigger_touched and not activated:
            activated = True
            if policy.kind in {"breakeven", "partial"}:
                active_stop = entry
            if policy.kind == "partial":
                partial_taken = True

        if direction == LONG:
            best = max(best, high)
        else:
            best = min(best, low)
        if policy.kind == "trailing" and activated:
            distance = float(policy.trail_r) * stop_pct * entry
            proposed = best - distance if direction == LONG else best + distance
            active_stop = (
                max(entry, active_stop, proposed)
                if direction == LONG
                else min(entry, active_stop, proposed)
            )

    return _managed_result(
        bars,
        entry_pos,
        len(bars) - 1,
        entry,
        float(bars["close"].iloc[-1]),
        direction,
        stop_pct,
        "RIGHT_CENSORED",
        False,
        partial_taken,
        policy,
    )


def _managed_result(
    bars: pd.DataFrame,
    entry_pos: int,
    exit_pos: int,
    entry: float,
    exit_price: float,
    direction: str,
    stop_pct: float,
    reason: str,
    resolved: bool,
    partial_taken: bool,
    policy: ExitPolicy,
) -> ManagedExitResult:
    sign = 1.0 if direction == LONG else -1.0
    final_return = sign * (exit_price / entry - 1.0)
    if policy.kind == "partial" and partial_taken:
        fraction = float(policy.partial_fraction)
        trigger_return = float(policy.trigger_r) * stop_pct
        gross_return = fraction * trigger_return + (1.0 - fraction) * final_return
    else:
        gross_return = final_return
    return ManagedExitResult(
        exit_pos=exit_pos,
        exit_time=pd.Timestamp(bars.index[exit_pos]),
        exit_price=float(exit_price),
        exit_reason=reason,
        bars_held=int(exit_pos - entry_pos),
        gross_return=float(gross_return),
        gross_r=float(gross_return / stop_pct),
        resolved=resolved,
        partial_taken=partial_taken,
    )


def _from_fixed(result: FixedRRResult) -> ManagedExitResult:
    return ManagedExitResult(
        exit_pos=result.exit_pos,
        exit_time=result.exit_time,
        exit_price=result.exit_price,
        exit_reason=result.exit_reason,
        bars_held=result.bars_held,
        gross_return=result.gross_return,
        gross_r=result.gross_r,
        resolved=result.resolved,
        partial_taken=False,
    )
