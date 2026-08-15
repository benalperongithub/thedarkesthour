#!/usr/bin/env python3
"""Offline RSI-gated reversion adapter overlay for TDH v2.0.61."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.60/adapter/tdh_strategy_lab_research_adapter.py'
)
spec = importlib.util.spec_from_file_location('tdh_adapter_v260_for_v261', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.60 research adapter')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

RELEASE_ROOT = Path(__file__).resolve().parents[1]
KERNEL_PATH = RELEASE_ROOT / 'research' / 'research_kernel.py'
kspec = importlib.util.spec_from_file_location(
    'tdh_kernel_v261_adapter', KERNEL_PATH
)
if kspec is None or kspec.loader is None:
    raise RuntimeError('cannot load v2.0.61 research kernel')
kernel = importlib.util.module_from_spec(kspec)
sys.modules[kspec.name] = kernel
kspec.loader.exec_module(kernel)


def _export_base_namespace(module: Any) -> None:
    namespace = globals()
    for export_name in tuple(dir(module)):
        if not export_name.startswith('__'):
            namespace[export_name] = getattr(module, export_name)


_export_base_namespace(base)
del _export_base_namespace


V261_FAMILY = 'RSI_GATED_REVERSION'
V261_IMPLEMENTATION = 'RSI14_25_75_ADX14_LE20_ATR1_RR2_CLOSED_BAR_V1'
V261_RISK_FRACTION = 0.01
_BASE_SIGNAL = base.v221.strategy_signal
_BASE_SIMULATE = base.v221.simulate
_BASE_AGGREGATE = base.v221.aggregate_folds
_BASE_FINALIZE = base.v221.finalize_comparisons
_ORIGINAL_METRICS = base._ORIGINAL_METRICS_FROM_TRADES
_ORIGINAL_AGGREGATE = base._ORIGINAL_AGGREGATE_FOLDS


def _wilder(values: pd.Series, period: int) -> pd.Series:
    return values.ewm(
        alpha=1.0 / period,
        adjust=False,
        min_periods=period,
    ).mean()


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    average_gain = _wilder(gain, period)
    average_loss = _wilder(loss, period)
    ratio = average_gain / average_loss.replace(0.0, np.nan)
    result = 100.0 - (100.0 / (1.0 + ratio))
    result = result.where(average_loss != 0.0, 100.0)
    result = result.where(average_gain != 0.0, 0.0)
    return result


def _adx(frame: pd.DataFrame, period: int) -> pd.Series:
    high = frame['high'].astype(float)
    low = frame['low'].astype(float)
    close = frame['close'].astype(float)
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0.0), 0.0)
    minus_dm = down.where((down > up) & (down > 0.0), 0.0)
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = _wilder(true_range, period).replace(0.0, np.nan)
    plus_di = 100.0 * _wilder(plus_dm, period) / atr
    minus_di = 100.0 * _wilder(minus_dm, period) / atr
    denominator = (plus_di + minus_di).replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / denominator
    return _wilder(dx, period)


def strategy_signal(
    frame: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.Series, pd.Series, dict[str, Any]]:
    if config.get('family') != V261_FAMILY:
        return _BASE_SIGNAL(frame, config)

    params = config['params']
    close = frame['close'].astype(float)
    rsi = _rsi(close, int(params['rsi_period']))
    adx = _adx(frame, int(params['adx_period']))
    raw = pd.Series(0.0, index=frame.index)
    raw = raw.mask(rsi <= float(params['long_threshold']), 1.0)
    raw = raw.mask(rsi >= float(params['short_threshold']), -1.0)
    gated = raw.where(adx <= float(params['adx_max']), 0.0).fillna(0.0)

    mode = config['control_mode']
    if mode == 'BASELINE':
        signal = raw.fillna(0.0)
    elif mode == 'NEGATIVE_CONTROL':
        signal = -gated
    elif mode == 'PERFORMANCE':
        signal = gated
    else:
        raise AdapterError('v2.0.61 unknown control mode')

    hold = pd.Series(
        int(params['max_holding_bars']), index=frame.index, dtype=int
    )
    meta = {
        'v261_family': True,
        'v261_implementation': V261_IMPLEMENTATION,
        'feature_timing': 'closed_bar_only',
        'entry_timing': 'next_bar_open',
        'atr_period': int(params['atr_period']),
        'atr_stop_x': float(params['stop_atr']),
        'target_r_multiple': float(params['target_r_multiple']),
        'candidate_protocol': 'RSI_WITH_ADX_LOW_TREND_GATE',
        'baseline_protocol': 'SAME_RSI_WITHOUT_ADX_GATE',
        'negative_control_protocol': 'INVERTED_RSI_WITH_SAME_ADX_GATE',
    }
    return signal.astype(float), hold, meta


def _v261_metrics(
    trades: list[dict[str, Any]], start: Any, end: Any
) -> dict[str, Any]:
    value = dict(_ORIGINAL_METRICS(list(trades), start, end))
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    for item in trades:
        factor = 1.0 + float(item.get('pnl_r', 0.0)) * V261_RISK_FRACTION
        equity = max(0.0, equity * max(0.0, factor))
        peak = max(peak, equity)
        if peak > 0.0:
            max_drawdown = max(max_drawdown, (peak - equity) / peak)
    net_return = max(-100.0, (equity - 1.0) * 100.0)
    net_pnl = 20_000.0 * net_return / 100.0
    trade_count = int(value.get('trade_count', 0))
    value.update({
        'initial_capital': 20_000.0,
        'final_capital': max(0.0, 20_000.0 + net_pnl),
        'net_pnl': net_pnl,
        'pnl_per_trade': net_pnl / trade_count if trade_count else 0.0,
        'net_return_pct': net_return,
        'max_drawdown_pct': min(100.0, max_drawdown * 100.0),
        'accounting_currency': 'USD',
        'accounting_basis': base.RUNTIME_ACCOUNTING_BASIS,
        'reference_capital_reporting_only': True,
        'risk_fraction_current_equity': V261_RISK_FRACTION,
        'v261_family': True,
        'v261_implementation': V261_IMPLEMENTATION,
    })
    return value


def simulate(
    frame: pd.DataFrame,
    config: dict[str, Any],
    start: Any,
    end: Any,
    cost_multiplier: float = 1.0,
) -> dict[str, Any]:
    if config.get('family') != V261_FAMILY:
        return _BASE_SIMULATE(frame, config, start, end, cost_multiplier)

    signal, hold_bars, meta = strategy_signal(frame, config)
    atr_period = int(meta['atr_period'])
    atr = base.v221.true_range(frame).rolling(
        atr_period, min_periods=atr_period
    ).mean()
    index = frame.index
    start_pos = int(index.searchsorted(start, side='left'))
    end_pos = int(index.searchsorted(end, side='left'))
    trades: list[dict[str, Any]] = []
    position_end = start_pos

    for signal_pos in range(
        max(1, start_pos), min(end_pos - 1, len(frame) - 1)
    ):
        if signal_pos < position_end:
            continue
        direction = int(np.sign(float(signal.iloc[signal_pos])))
        if direction == 0:
            continue
        entry_pos = signal_pos + 1
        raw_entry = float(frame['open'].iloc[entry_pos])
        entry = raw_entry * (
            1.0 + direction * base.v221.SLIPPAGE_RATE * cost_multiplier
        )
        atr_value = float(atr.iloc[signal_pos])
        if not math.isfinite(atr_value):
            atr_value = raw_entry * base.v221.MIN_STOP_PCT
        stop_distance = max(
            raw_entry * base.v221.MIN_STOP_PCT,
            atr_value * float(meta['atr_stop_x']),
        )
        stop = entry - direction * stop_distance
        target = entry + direction * stop_distance * float(
            meta['target_r_multiple']
        )
        exit_pos = min(
            end_pos - 1,
            entry_pos + max(1, int(hold_bars.iloc[signal_pos])),
        )
        reason = 'TIME'
        raw_exit = float(frame['close'].iloc[exit_pos])
        for position in range(entry_pos, exit_pos + 1):
            high = float(frame['high'].iloc[position])
            low = float(frame['low'].iloc[position])
            hit_stop = low <= stop if direction > 0 else high >= stop
            hit_target = high >= target if direction > 0 else low <= target
            if hit_stop:
                raw_exit = stop
                exit_pos = position
                reason = 'BOTH_HIT_STOP_FIRST' if hit_target else 'STOP'
                break
            if hit_target:
                raw_exit = target
                exit_pos = position
                reason = 'TARGET'
                break
        exit_price = raw_exit * (
            1.0 - direction * base.v221.SLIPPAGE_RATE * cost_multiplier
        )
        days = (index[exit_pos] - index[entry_pos]).total_seconds() / 86400.0
        raw_r = direction * (exit_price - entry) / stop_distance
        fee_r = (
            (entry + exit_price)
            * base.v221.FEE_RATE
            * cost_multiplier
            / stop_distance
        )
        funding_r = (
            entry
            * base.v221.FUNDING_DAILY_RATE
            * days
            * cost_multiplier
            / stop_distance
        )
        trades.append({
            'entry_ts': index[entry_pos].isoformat(),
            'exit_ts': index[exit_pos].isoformat(),
            'direction': direction,
            'pnl_r': raw_r - fee_r - funding_r,
            'reason': reason,
            'bars_held': max(1, exit_pos - entry_pos + 1),
        })
        position_end = exit_pos + 1
    return _v261_metrics(trades, start, end)


def aggregate_folds(folds: list[dict[str, Any]]) -> dict[str, Any]:
    if not folds or not all(
        isinstance(item, dict)
        and isinstance(item.get('metrics'), dict)
        and item['metrics'].get('v261_family') is True
        for item in folds
    ):
        return _BASE_AGGREGATE(folds)
    value = dict(_ORIGINAL_AGGREGATE(folds))
    returns = [float(item['metrics'].get('net_return_pct', 0.0)) for item in folds]
    drawdowns = [
        float(item['metrics'].get('max_drawdown_pct', 0.0)) for item in folds
    ]
    net_return = max(-100.0, min(returns) if returns else 0.0)
    net_pnl = 20_000.0 * net_return / 100.0
    trade_count = int(value.get('trade_count', 0))
    value.update({
        'initial_capital': 20_000.0,
        'final_capital': max(0.0, 20_000.0 + net_pnl),
        'net_pnl': net_pnl,
        'pnl_per_trade': net_pnl / trade_count if trade_count else 0.0,
        'net_return_pct': net_return,
        'max_drawdown_pct': min(100.0, max(drawdowns) if drawdowns else 0.0),
        'accounting_currency': 'USD',
        'accounting_basis': base.RUNTIME_ACCOUNTING_BASIS,
        'reference_capital_reporting_only': True,
        'risk_fraction_current_equity': V261_RISK_FRACTION,
        'v261_family': True,
        'v261_implementation': V261_IMPLEMENTATION,
    })
    return value


def finalize_comparisons(results: list[dict[str, Any]], stage: str) -> None:
    _BASE_FINALIZE(results, stage)
    if stage != 'S1':
        return
    for row in results:
        metrics = row.get('metrics')
        if not isinstance(metrics, dict) or metrics.get('v261_family') is not True:
            continue
        gates = row.setdefault('gates', {})
        gates['v261_closed_bar_only'] = True
        gates['v261_next_bar_entry'] = True
        gates['v261_target_r_multiple_2'] = True
        gates['v261_candidate_baseline_negative_control_bound'] = True
        gates['v261_s1_only'] = True
        gates['v261_implementation'] = V261_IMPLEMENTATION


base.v221.validate_config = kernel.validate_config
base.v221.control_config = kernel.control_config
base.v221.canonical_hash = kernel.canonical_hash
base.v221.ResearchContractError = kernel.ResearchContractError
base.v221.strategy_signal = strategy_signal
base.v221.simulate = simulate
base.v221.aggregate_folds = aggregate_folds
base.v221.finalize_comparisons = finalize_comparisons

validate_config = kernel.validate_config
control_config = kernel.control_config
write_object = base.write_object
sha256_file = base.sha256_file
run_experiment = base.v221.run_experiment
validate_request = base.v221.validate_request


def main() -> int:
    return base.v221.main()


if __name__ == '__main__':
    raise SystemExit(main())
