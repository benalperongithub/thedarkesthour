from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.momentum import (
    MOMENTUM_COLUMNS,
    MomentumConfig,
    apply_single_position,
    compute_momentum_features,
    decision_mask,
    select_momentum_symbol,
)
from darkest_hour.replay import net_r_after_costs, replay_fixed_rr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen TDH V4 cross-sectional momentum strategy."
    )
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--exchange", default="binance")
    parser.add_argument("--tf", default="5m")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2025-04-01")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument("--min-daily-quote-volume", type=float, default=10_000_000)
    parser.add_argument("--min-universe", type=int, default=20)
    parser.add_argument("--stop", type=float, default=0.02)
    parser.add_argument("--rr-ratio", type=float, default=2.0)
    parser.add_argument("--time-stop-bars", type=int, default=576)
    parser.add_argument("--round-trip-cost-bps", type=float, default=9.5)
    parser.add_argument("--funding-apr", type=float, default=0.1095)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def load_bars(root: Path, exchange: str, symbol: str, tf: str) -> pd.DataFrame:
    tf_root = root / exchange / symbol / tf
    parts = sorted(tf_root.glob("year=*/**/*.parquet"))
    if parts:
        frames = [
            pd.read_parquet(
                path,
                columns=["ts", "open", "high", "low", "close", "volume"],
            )
            for path in parts
        ]
        data = pd.concat(frames, ignore_index=True)
    else:
        monolith = tf_root / "ohlcv.parquet"
        if not monolith.exists():
            raise FileNotFoundError(f"no parquet bars under {tf_root}")
        data = pd.read_parquet(
            monolith,
            columns=["ts", "open", "high", "low", "close", "volume"],
        )
    data["ts"] = pd.to_datetime(data["ts"], utc=True, errors="raise")
    return (
        data.drop_duplicates("ts", keep="last")
        .sort_values("ts", kind="stable")
        .set_index("ts")
    )


def symbols_from_root(args: argparse.Namespace, root: Path) -> list[str]:
    if args.symbols:
        symbols = sorted(set(args.symbols))
    else:
        exchange_root = root / args.exchange
        symbols = sorted(path.name for path in exchange_root.iterdir() if path.is_dir())
    if "BTCUSDT" not in symbols:
        symbols.append("BTCUSDT")
        symbols.sort()
    return symbols


def profit_factor(values: np.ndarray) -> float:
    gains = float(values[values > 0.0].sum())
    losses = float(-values[values < 0.0].sum())
    return gains / losses if losses > 0.0 else float("inf")


def drawdown(values: np.ndarray) -> float:
    equity = np.r_[0.0, np.cumsum(values)]
    return float(np.max(np.maximum.accumulate(equity) - equity))


def metric_row(label: str, frame: pd.DataFrame, weekdays: int) -> dict[str, object]:
    ordered = frame.sort_values(["exit_time", "symbol"], kind="stable")
    values = ordered["net_R"].to_numpy(dtype=float)
    if not len(values):
        return {
            "label": label,
            "n": 0,
            "per_weekday": 0.0,
            "WR_pct": float("nan"),
            "mean_R": float("nan"),
            "total_R": 0.0,
            "PF": float("nan"),
            "DD_R": 0.0,
        }
    return {
        "label": label,
        "n": len(values),
        "per_weekday": len(values) / weekdays,
        "WR_pct": 100.0 * float((values > 0.0).mean()),
        "mean_R": float(values.mean()),
        "total_R": float(values.sum()),
        "PF": profit_factor(values),
        "DD_R": drawdown(values),
    }


def build_decision_tape(
    args: argparse.Namespace,
    cfg: MomentumConfig,
    root: Path,
    symbols: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for number, symbol in enumerate(symbols, start=1):
        try:
            bars = load_bars(root, args.exchange, symbol, args.tf)
        except FileNotFoundError as exc:
            print(f"[{number:02d}/{len(symbols):02d}] {symbol}: SKIP {exc}")
            continue
        bars = bars[bars.index < end]
        features = compute_momentum_features(bars, cfg)
        mask = (
            decision_mask(features.index, cfg)
            & features.index.to_series().ge(start).to_numpy()
            & features.index.to_series().lt(end).to_numpy()
        )
        positions = np.flatnonzero(mask)
        positions = positions[positions + 1 < len(bars)]
        if not len(positions):
            print(f"[{number:02d}/{len(symbols):02d}] {symbol}: decisions=0")
            continue

        sampled = features.iloc[positions].copy()
        sampled.insert(0, "decision_time", sampled.index)
        sampled.insert(0, "symbol", symbol)
        sampled["entry_pos"] = positions + 1
        sampled["entry_time"] = bars.index[positions + 1]
        sampled = sampled[sampled["entry_time"] < end]
        rows.append(sampled.reset_index(drop=True))
        print(
            f"[{number:02d}/{len(symbols):02d}] {symbol}: decisions={len(sampled):,}",
            flush=True,
        )
    if not rows:
        raise RuntimeError("no decision rows were built")
    return pd.concat(rows, ignore_index=True)


def choose_candidates(tape: pd.DataFrame, cfg: MomentumConfig) -> pd.DataFrame:
    choices: list[dict[str, object]] = []
    for decision_time, snapshot in tape.groupby("decision_time", sort=True):
        btc = snapshot[snapshot["symbol"] == "BTCUSDT"]
        if btc.empty:
            continue
        choice = select_momentum_symbol(snapshot, btc.iloc[-1], cfg)
        if choice is None:
            continue
        winner = snapshot[snapshot["symbol"] == choice.symbol].iloc[-1]
        row = winner.to_dict()
        row.update(
            {
                "direction": choice.direction,
                "momentum_score": choice.momentum_score,
                "eligible_symbols": choice.eligible_symbols,
            }
        )
        choices.append(row)
    if not choices:
        return pd.DataFrame()
    return pd.DataFrame(choices).sort_values("decision_time", kind="stable")


def replay_candidates(
    args: argparse.Namespace,
    root: Path,
    candidates: pd.DataFrame,
    end: pd.Timestamp,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for number, (symbol, subset) in enumerate(
        candidates.groupby("symbol", sort=True), start=1
    ):
        bars = load_bars(root, args.exchange, str(symbol), args.tf)
        bars = bars[bars.index < end]
        for _, candidate in subset.iterrows():
            entry_pos = int(candidate["entry_pos"])
            entry_time = pd.Timestamp(candidate["entry_time"])
            if entry_pos >= len(bars) or pd.Timestamp(bars.index[entry_pos]) != entry_time:
                raise AssertionError(f"entry alignment changed for {symbol} {entry_time}")
            replay = replay_fixed_rr(
                bars,
                entry_pos=entry_pos,
                direction=str(candidate["direction"]),
                stop_pct=args.stop,
                rr_ratio=args.rr_ratio,
                time_stop_bars=args.time_stop_bars,
                worst_case_intrabar=True,
            )
            record = candidate.to_dict()
            record.update(
                {
                    "entry_price": float(bars["close"].iloc[entry_pos]),
                    "exit_time": replay.exit_time,
                    "exit_price": replay.exit_price,
                    "tp_price": replay.tp_price,
                    "sl_price": replay.sl_price,
                    "exit_reason": replay.exit_reason,
                    "bars_held": replay.bars_held,
                    "gross_R": replay.gross_r,
                    "resolved": replay.resolved,
                    "net_R": (
                        net_r_after_costs(
                            replay.gross_return,
                            args.stop,
                            entry_time,
                            replay.exit_time,
                            args.round_trip_cost_bps,
                            args.funding_apr,
                        )
                        if replay.resolved
                        else float("nan")
                    ),
                }
            )
            records.append(record)
        print(
            f"[replay {number:02d}] {symbol}: candidates={len(subset):,}", flush=True
        )
    return pd.DataFrame(records)


def main() -> None:
    args = parse_args()
    if args.stop <= 0.0 or args.rr_ratio <= 0.0:
        raise ValueError("stop and rr-ratio must be positive")
    if args.time_stop_bars <= 0:
        raise ValueError("time-stop-bars must be positive")

    root = Path(args.data_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    start = pd.to_datetime(args.start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    if end <= start:
        raise ValueError("end must be after start")

    cfg = MomentumConfig(
        min_daily_quote_volume=args.min_daily_quote_volume,
        min_universe=args.min_universe,
    )
    symbols = symbols_from_root(args, root)
    print("TDH V4 FROZEN CROSS-SECTIONAL MOMENTUM")
    print("symbols:", len(symbols))
    print("period:", start, "->", end, "(end exclusive)")
    print("decision hours UTC:", cfg.decision_hours)
    print("stop / target:", args.stop, "/", args.stop * args.rr_ratio)

    decision_tape = build_decision_tape(args, cfg, root, symbols, start, end)
    candidates = choose_candidates(decision_tape, cfg)
    print("decision snapshots:", decision_tape["decision_time"].nunique())
    print("regime-aligned candidates:", len(candidates))
    if candidates.empty:
        raise RuntimeError("the frozen policy produced no candidates")

    outcomes = replay_candidates(args, root, candidates, end)
    selected = apply_single_position(outcomes)
    selected = selected[selected["resolved"]].copy()
    selected["entry_time"] = pd.to_datetime(selected["entry_time"], utc=True)
    selected["exit_time"] = pd.to_datetime(selected["exit_time"], utc=True)

    weekdays = len(
        pd.bdate_range(start.normalize(), end.normalize() - pd.Timedelta(days=1))
    )
    summary_rows = [metric_row("ALL", selected, weekdays)]
    for direction, subset in selected.groupby("direction", sort=True):
        summary_rows.append(metric_row(str(direction).upper(), subset, weekdays))
    summary = pd.DataFrame(summary_rows)

    quarter_rows: list[dict[str, object]] = []
    quarter_key = (
        selected["entry_time"].dt.year.astype(str)
        + "Q"
        + selected["entry_time"].dt.quarter.astype(str)
    )
    for quarter, subset in selected.groupby(quarter_key, sort=True):
        period = pd.Period(str(quarter), freq="Q")
        quarter_start = period.start_time
        quarter_end = period.end_time
        quarter_weekdays = len(pd.bdate_range(quarter_start, quarter_end))
        row = metric_row(str(quarter), subset, quarter_weekdays)
        row["quarter"] = quarter
        quarter_rows.append(row)
    quarters = pd.DataFrame(quarter_rows)

    all_row = summary.iloc[0]
    direction_totals = summary[summary["label"].isin(["LONG", "SHORT"])]
    active_quarters = len(quarters)
    positive_quarters = int((quarters["total_R"] > 0.0).sum())
    checks = {
        "trades_at_least_150": int(all_row["n"]) >= 150,
        "win_rate_at_least_50": float(all_row["WR_pct"]) >= 50.0,
        "profit_factor_at_least_1p50": float(all_row["PF"]) >= 1.50,
        "drawdown_at_most_10R": float(all_row["DD_R"]) <= 10.0,
        "both_directions_positive": (
            set(direction_totals["label"]) == {"LONG", "SHORT"}
            and bool((direction_totals["total_R"] > 0.0).all())
        ),
        "positive_quarters_at_least_60pct": (
            active_quarters > 0 and positive_quarters / active_quarters >= 0.60
        ),
    }
    decision = pd.DataFrame(
        [{"check": key, "passed": value} for key, value in checks.items()]
    )

    decision_tape.to_csv(output_root / "v4_decision_tape.csv", index=False)
    candidates.to_csv(output_root / "v4_regime_candidates.csv", index=False)
    outcomes.to_csv(output_root / "v4_candidate_outcomes.csv", index=False)
    selected.to_csv(output_root / "v4_selected_trades.csv", index=False)
    summary.to_csv(output_root / "v4_summary.csv", index=False)
    quarters.to_csv(output_root / "v4_quarters.csv", index=False)
    decision.to_csv(output_root / "v4_decision.csv", index=False)

    print("\nSUMMARY")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nQUARTERS")
    print(quarters.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nPRE-REGISTERED DECISION")
    print(decision.to_string(index=False))
    print("V4 VERDICT:", "PASS" if all(checks.values()) else "FAIL")
    print("WROTE", output_root)


if __name__ == "__main__":
    main()
