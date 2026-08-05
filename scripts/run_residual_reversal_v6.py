from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.reversal import (
    ReversalConfig,
    aggregate_completed_hours,
    compute_residual_features,
    fixed_horizon_single_position,
    select_reversal_pool,
    strongest_per_timestamp,
)
from darkest_hour.signals import LONG


HORIZONS = (1, 2, 4)
BAR_COLUMNS = [
    "ts",
    "open",
    "high",
    "low",
    "close",
    "quote_volume",
    "taker_buy_quote",
    "trades",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the pre-registered TDH V6 residual-reversal audit."
    )
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--exchange", default="binance")
    parser.add_argument("--tf", default="5m")
    parser.add_argument("--start", default="2023-03-01")
    parser.add_argument("--end", default="2025-04-01")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument("--min-daily-quote-volume", type=float, default=10_000_000)
    parser.add_argument("--min-universe", type=int, default=20)
    parser.add_argument("--round-trip-cost-bps", type=float, default=9.5)
    parser.add_argument("--funding-apr", type=float, default=0.1095)
    parser.add_argument("--simulations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260806)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def load_bars(root: Path, exchange: str, symbol: str, tf: str) -> pd.DataFrame:
    tf_root = root / exchange / symbol / tf
    parts = sorted(tf_root.glob("year=*/**/*.parquet"))
    if parts:
        frames = [pd.read_parquet(path, columns=BAR_COLUMNS) for path in parts]
        data = pd.concat(frames, ignore_index=True)
    else:
        monolith = tf_root / "ohlcv.parquet"
        if not monolith.exists():
            raise FileNotFoundError(f"no parquet bars under {tf_root}")
        data = pd.read_parquet(monolith, columns=BAR_COLUMNS)
    data["ts"] = pd.to_datetime(data["ts"], utc=True, errors="raise")
    numeric = [column for column in BAR_COLUMNS if column != "ts"]
    data[numeric] = data[numeric].apply(pd.to_numeric, errors="raise")
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


def build_feature_tape(
    args: argparse.Namespace,
    cfg: ReversalConfig,
    root: Path,
    symbols: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    btc_bars = load_bars(root, args.exchange, "BTCUSDT", args.tf)
    btc_bars = btc_bars[btc_bars.index < end]
    btc_hourly = aggregate_completed_hours(btc_bars, cfg)

    frames: list[pd.DataFrame] = []
    for number, symbol in enumerate(symbols, start=1):
        try:
            bars = load_bars(root, args.exchange, symbol, args.tf)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[{number:02d}/{len(symbols):02d}] {symbol}: SKIP {exc}")
            continue
        bars = bars[bars.index < end]
        hourly = aggregate_completed_hours(bars, cfg)
        features = compute_residual_features(hourly, btc_hourly, cfg)
        mask = (features.index >= start) & (features.index < end)
        if cfg.weekdays_only:
            mask &= features.index.dayofweek < 5
        sampled = features.loc[mask].copy()
        if sampled.empty:
            print(f"[{number:02d}/{len(symbols):02d}] {symbol}: feature_rows=0")
            continue
        sampled.insert(0, "decision_time", sampled.index)
        sampled.insert(0, "symbol", symbol)
        sampled["entry_pos"] = sampled["decision_pos"].astype(np.int64) + 1
        valid = sampled["entry_pos"] < len(bars)
        sampled = sampled.loc[valid].copy()
        sampled["entry_time"] = bars.index[
            sampled["entry_pos"].to_numpy(dtype=np.int64)
        ]
        sampled = sampled[sampled["entry_time"] < end]
        frames.append(sampled.reset_index(drop=True))
        print(
            f"[{number:02d}/{len(symbols):02d}] {symbol}: "
            f"feature_rows={len(sampled):,}",
            flush=True,
        )
    if not frames:
        raise RuntimeError("no causal feature rows were built")
    return pd.concat(frames, ignore_index=True)


def build_candidate_pool(
    feature_tape: pd.DataFrame,
    cfg: ReversalConfig,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for decision_time, snapshot in feature_tape.groupby("decision_time", sort=True):
        pool = select_reversal_pool(snapshot, cfg)
        if pool.empty:
            continue
        pool = pool.copy()
        pool["decision_time"] = pd.Timestamp(decision_time)
        frames.append(pool)
    if not frames:
        raise RuntimeError("the frozen reversal definition produced no candidates")
    return pd.concat(frames, ignore_index=True).sort_values(
        ["decision_time", "reversal_score", "symbol"],
        ascending=[True, False, True],
        kind="stable",
    )


def add_forward_outcomes(
    args: argparse.Namespace,
    root: Path,
    pool: pd.DataFrame,
    end: pd.Timestamp,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for number, (symbol, subset) in enumerate(pool.groupby("symbol", sort=True), 1):
        bars = load_bars(root, args.exchange, str(symbol), args.tf)
        bars = bars[bars.index < end]
        for _, candidate in subset.iterrows():
            entry_pos = int(candidate["entry_pos"])
            entry_time = pd.Timestamp(candidate["entry_time"])
            if entry_pos >= len(bars) or pd.Timestamp(bars.index[entry_pos]) != entry_time:
                raise AssertionError(f"entry alignment changed for {symbol} {entry_time}")
            entry_price = float(bars["close"].iloc[entry_pos])
            sign = 1.0 if str(candidate["direction"]) == LONG else -1.0
            record = candidate.to_dict()
            record["entry_price"] = entry_price
            for hours in HORIZONS:
                target_time = entry_time + pd.Timedelta(hours=hours)
                target_pos = int(bars.index.searchsorted(target_time, side="left"))
                exact = (
                    target_pos < len(bars)
                    and pd.Timestamp(bars.index[target_pos]) == target_time
                    and target_time < end
                )
                suffix = f"{hours}h"
                if not exact:
                    record[f"exit_time_{suffix}"] = pd.NaT
                    record[f"gross_return_{suffix}"] = np.nan
                    record[f"net_return_{suffix}"] = np.nan
                    record[f"net_bps_{suffix}"] = np.nan
                    continue
                exit_price = float(bars["close"].iloc[target_pos])
                gross_return = sign * (exit_price / entry_price - 1.0)
                funding = args.funding_apr * hours / (365.0 * 24.0)
                net_return = (
                    gross_return
                    - args.round_trip_cost_bps / 10_000.0
                    - funding
                )
                record[f"exit_time_{suffix}"] = target_time
                record[f"gross_return_{suffix}"] = gross_return
                record[f"net_return_{suffix}"] = net_return
                record[f"net_bps_{suffix}"] = 10_000.0 * net_return
            records.append(record)
        print(
            f"[outcome {number:02d}] {symbol}: candidates={len(subset):,}",
            flush=True,
        )
    result = pd.DataFrame(records)
    for column in ["decision_time", "entry_time", *[f"exit_time_{h}h" for h in HORIZONS]]:
        result[column] = pd.to_datetime(result[column], utc=True)
    return result


def profit_factor(values: np.ndarray) -> float:
    gains = float(values[values > 0.0].sum())
    losses = float(-values[values < 0.0].sum())
    return gains / losses if losses > 0.0 else float("inf")


def drawdown(values: np.ndarray) -> float:
    equity = np.r_[0.0, np.cumsum(values)]
    return float(np.max(np.maximum.accumulate(equity) - equity))


def metric_row(label: str, frame: pd.DataFrame, hours: int) -> dict[str, object]:
    values = frame[f"net_bps_{hours}h"].dropna().to_numpy(dtype=float)
    return {
        "label": label,
        "horizon_hours": hours,
        "n": len(values),
        "WR_pct": 100.0 * float((values > 0.0).mean()) if len(values) else np.nan,
        "mean_net_bps": float(values.mean()) if len(values) else np.nan,
        "total_net_bps": float(values.sum()),
        "PF": profit_factor(values) if len(values) else np.nan,
        "DD_bps": drawdown(values) if len(values) else 0.0,
    }


def random_benchmark(
    outcomes: pd.DataFrame,
    simulations: int,
    seed: int,
) -> pd.DataFrame:
    if simulations <= 0:
        return pd.DataFrame()
    eligible = outcomes.dropna(subset=["exit_time_4h", "net_bps_4h"]).copy()
    groups = [group for _, group in eligible.groupby("decision_time", sort=True)]
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for simulation in range(simulations):
        values: list[float] = []
        available_at: pd.Timestamp | None = None
        for group in groups:
            entry_time = pd.Timestamp(group["entry_time"].iloc[0])
            if available_at is not None and entry_time < available_at:
                continue
            row = group.iloc[int(rng.integers(0, len(group)))]
            values.append(float(row["net_bps_4h"]))
            available_at = pd.Timestamp(row["exit_time_4h"])
        array = np.asarray(values, dtype=float)
        rows.append(
            {
                "simulation": simulation,
                "n": len(array),
                "mean_net_bps": float(array.mean()) if len(array) else np.nan,
                "total_net_bps": float(array.sum()),
                "DD_bps": drawdown(array) if len(array) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    if args.round_trip_cost_bps < 0.0 or args.funding_apr < 0.0:
        raise ValueError("cost assumptions cannot be negative")
    start = pd.to_datetime(args.start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    if end <= start:
        raise ValueError("end must be after start")
    root = Path(args.data_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    symbols = symbols_from_root(args, root)
    cfg = ReversalConfig(
        min_daily_quote_volume=args.min_daily_quote_volume,
        min_universe=args.min_universe,
    )

    print("TDH V6 PRE-REGISTERED RESIDUAL-REVERSAL SIGNAL AUDIT")
    print("No stop, target, trailing stop, or exit family is tuned in this run.")
    print("symbols:", len(symbols))
    print("period:", start, "->", end, "(end exclusive)")
    print("round-trip cost bps:", args.round_trip_cost_bps)
    print("funding APR stress:", args.funding_apr)
    print("tail / z1 / z4:", cfg.tail_fraction, cfg.min_abs_z1, cfg.min_abs_z4)

    feature_tape = build_feature_tape(args, cfg, root, symbols, start, end)
    pool = build_candidate_pool(feature_tape, cfg)
    outcomes = add_forward_outcomes(args, root, pool, end)
    strongest = strongest_per_timestamp(outcomes)
    selected = fixed_horizon_single_position(strongest, "4h")

    summary = pd.DataFrame(
        [metric_row("STRONGEST_RESIDUAL_REVERSAL", selected, h) for h in HORIZONS]
    )
    quarter_key = (
        selected["entry_time"].dt.year.astype(str)
        + "Q"
        + selected["entry_time"].dt.quarter.astype(str)
    )
    quarter_rows: list[dict[str, object]] = []
    for quarter, subset in selected.groupby(quarter_key, sort=True):
        row = metric_row(str(quarter), subset, 4)
        row["quarter"] = quarter
        quarter_rows.append(row)
    quarters = pd.DataFrame(quarter_rows)
    random = random_benchmark(outcomes, args.simulations, args.seed)

    primary = summary[summary["horizon_hours"] == 4].iloc[0]
    active_quarters = len(quarters)
    positive_quarters = int((quarters["total_net_bps"] > 0.0).sum())
    random_median = float(random["total_net_bps"].median())
    p_random_ge = float(
        (random["total_net_bps"] >= float(primary["total_net_bps"])).mean()
    )
    checks = {
        "trades_at_least_300": int(primary["n"]) >= 300,
        "four_hour_mean_after_costs_positive": float(primary["mean_net_bps"]) > 0.0,
        "four_hour_win_rate_at_least_50": float(primary["WR_pct"]) >= 50.0,
        "positive_quarters_at_least_60pct": (
            active_quarters > 0 and positive_quarters / active_quarters >= 0.60
        ),
        "strongest_beats_random_median": (
            float(primary["total_net_bps"]) > random_median
        ),
        "random_ge_strongest_probability_at_most_10pct": p_random_ge <= 0.10,
    }
    decision = pd.DataFrame(
        [{"check": key, "passed": value} for key, value in checks.items()]
    )

    feature_audit = (
        feature_tape.groupby("symbol", sort=True)
        .agg(
            feature_rows=("decision_time", "size"),
            decision_min=("decision_time", "min"),
            decision_max=("decision_time", "max"),
            finite_z1=("residual_z1", "count"),
            finite_z4=("residual_z4", "count"),
        )
        .reset_index()
    )
    # The million-row feature matrix is deliberately not persisted. Candidate
    # rows retain every feature used by the selector, while this compact audit
    # proves coverage without consuming hundreds of megabytes of VPS disk.
    feature_audit.to_csv(output_root / "v6_feature_audit.csv", index=False)
    outcomes.to_csv(output_root / "v6_candidate_pool_outcomes.csv", index=False)
    selected.to_csv(output_root / "v6_selected_fixed4h.csv", index=False)
    summary.to_csv(output_root / "v6_horizon_summary.csv", index=False)
    quarters.to_csv(output_root / "v6_quarters.csv", index=False)
    random.to_csv(output_root / "v6_random_benchmark.csv", index=False)
    decision.to_csv(output_root / "v6_decision.csv", index=False)
    manifest = {
        "start": str(start),
        "end_exclusive": str(end),
        "symbols": len(symbols),
        "config": cfg.__dict__,
        "round_trip_cost_bps": args.round_trip_cost_bps,
        "funding_apr": args.funding_apr,
        "simulations": args.simulations,
        "seed": args.seed,
    }
    (output_root / "v6_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("\nHORIZON SUMMARY")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nQUARTERLY 4H RESULT")
    print(quarters.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nRANDOM QUALIFIED-CANDIDATE BENCHMARK")
    print("random total bps p05/median/p95:", *np.quantile(random["total_net_bps"], [0.05, 0.5, 0.95]))
    print("strongest minus random median bps:", float(primary["total_net_bps"]) - random_median)
    print("p(random >= strongest):", p_random_ge)
    print("\nPRE-REGISTERED DECISION")
    print(decision.to_string(index=False))
    print("V6 SIGNAL VERDICT:", "PASS" if all(checks.values()) else "FAIL")
    print("WROTE", output_root)


if __name__ == "__main__":
    main()
