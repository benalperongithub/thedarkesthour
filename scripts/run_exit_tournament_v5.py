from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.exits import POLICIES, replay_exit_policy
from darkest_hour.momentum import apply_single_position
from darkest_hour.replay import net_r_after_costs
from darkest_hour.signals import LONG, SHORT


DIRECTION_MODES = ("BOTH", "LONG_ONLY", "SHORT_ONLY")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen TDH V5 nested direction/exit tournament."
    )
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--exchange", default="binance")
    parser.add_argument("--tf", default="5m")
    parser.add_argument("--train-start", default="2023-01-01")
    parser.add_argument("--score-start", default="2024-01-01")
    parser.add_argument("--end", default="2025-04-01")
    parser.add_argument("--stop", type=float, default=0.02)
    parser.add_argument("--round-trip-cost-bps", type=float, default=9.5)
    parser.add_argument("--funding-apr", type=float, default=0.1095)
    parser.add_argument("--min-train", type=int, default=60)
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


def profit_factor(values: np.ndarray) -> float:
    gains = float(values[values > 0.0].sum())
    losses = float(-values[values < 0.0].sum())
    return gains / losses if losses > 0.0 else float("inf")


def drawdown(values: np.ndarray) -> float:
    equity = np.r_[0.0, np.cumsum(values)]
    return float(np.max(np.maximum.accumulate(equity) - equity))


def filter_direction(frame: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode == "BOTH":
        return frame
    if mode == "LONG_ONLY":
        return frame[frame["direction"] == LONG]
    if mode == "SHORT_ONLY":
        return frame[frame["direction"] == SHORT]
    raise ValueError(mode)


def book_metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    ordered = frame.sort_values(["exit_time", "symbol"], kind="stable")
    values = ordered["net_R"].to_numpy(dtype=float)
    if not len(values):
        return {
            "n": 0,
            "WR_pct": float("nan"),
            "mean_R": float("nan"),
            "total_R": 0.0,
            "PF": float("nan"),
            "DD_R": 0.0,
            "LCB_mean_R": float("-inf"),
        }
    standard_error = (
        float(values.std(ddof=1) / np.sqrt(len(values))) if len(values) > 1 else 0.0
    )
    return {
        "n": len(values),
        "WR_pct": 100.0 * float((values > 0.0).mean()),
        "mean_R": float(values.mean()),
        "total_R": float(values.sum()),
        "PF": profit_factor(values),
        "DD_R": drawdown(values),
        "LCB_mean_R": float(values.mean() - standard_error),
    }


def replay_all_policies(
    args: argparse.Namespace,
    candidates: pd.DataFrame,
    root: Path,
    end: pd.Timestamp,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    grouped = candidates.groupby("symbol", sort=True)
    for number, (symbol, subset) in enumerate(grouped, start=1):
        bars = load_bars(root, args.exchange, str(symbol), args.tf)
        bars = bars[bars.index < end]
        for _, candidate in subset.iterrows():
            entry_pos = int(candidate["entry_pos"])
            entry_time = pd.Timestamp(candidate["entry_time"])
            if entry_pos >= len(bars) or pd.Timestamp(bars.index[entry_pos]) != entry_time:
                raise AssertionError(f"entry alignment changed for {symbol} {entry_time}")
            for policy in POLICIES:
                result = replay_exit_policy(
                    bars,
                    entry_pos,
                    str(candidate["direction"]),
                    args.stop,
                    policy,
                )
                record = candidate.to_dict()
                record.update(
                    {
                        "exit_policy": policy.name,
                        "exit_time": result.exit_time,
                        "exit_price": result.exit_price,
                        "exit_reason": result.exit_reason,
                        "bars_held": result.bars_held,
                        "gross_R": result.gross_r,
                        "partial_taken": result.partial_taken,
                        "resolved": result.resolved,
                        "net_R": (
                            net_r_after_costs(
                                result.gross_return,
                                args.stop,
                                entry_time,
                                result.exit_time,
                                args.round_trip_cost_bps,
                                args.funding_apr,
                            )
                            if result.resolved
                            else float("nan")
                        ),
                    }
                )
                records.append(record)
        print(f"[replay {number:02d}] {symbol}: entries={len(subset):,}", flush=True)
    return pd.DataFrame(records)


def select_for_fold(
    outcomes: pd.DataFrame,
    train_start: pd.Timestamp,
    fold_start: pd.Timestamp,
    min_train: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    # All policies close within 48 hours. Purging that entire interval makes
    # every retained training label available before fit time.
    entry_cutoff = fold_start - pd.Timedelta(hours=48)
    audit: list[dict[str, object]] = []
    for policy in (item.name for item in POLICIES):
        policy_rows = outcomes[
            (outcomes["exit_policy"] == policy)
            & (outcomes["entry_time"] >= train_start)
            & (outcomes["entry_time"] < entry_cutoff)
            & (outcomes["exit_time"] < fold_start)
            & outcomes["resolved"]
        ]
        for mode in DIRECTION_MODES:
            book = apply_single_position(filter_direction(policy_rows, mode))
            metrics = book_metrics(book)
            audit.append(
                {
                    "exit_policy": policy,
                    "direction_mode": mode,
                    "train_last_exit": (
                        book["exit_time"].max() if len(book) else pd.NaT
                    ),
                    **metrics,
                }
            )
    eligible = [row for row in audit if int(row["n"]) >= min_train]
    if not eligible:
        raise RuntimeError(f"no policy has {min_train} training trades at {fold_start}")
    eligible.sort(
        key=lambda row: (
            -float(row["LCB_mean_R"]),
            -float(row["PF"]),
            -int(row["n"]),
            str(row["exit_policy"]),
            str(row["direction_mode"]),
        )
    )
    return eligible[0], audit


def main() -> None:
    args = parse_args()
    if args.stop <= 0.0 or args.min_train <= 0:
        raise ValueError("stop and min-train must be positive")
    root = Path(args.data_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    train_start = pd.to_datetime(args.train_start, utc=True)
    score_start = pd.to_datetime(args.score_start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    if not train_start < score_start < end:
        raise ValueError("require train-start < score-start < end")

    candidates = pd.read_csv(args.candidates)
    required = {"symbol", "entry_time", "entry_pos", "direction"}
    missing = required.difference(candidates.columns)
    if missing:
        raise ValueError(f"candidate tape missing columns: {sorted(missing)}")
    candidates["entry_time"] = pd.to_datetime(candidates["entry_time"], utc=True)
    candidates = candidates[
        (candidates["entry_time"] >= train_start) & (candidates["entry_time"] < end)
    ].copy()

    print("TDH V5 NESTED DIRECTION / MANAGED-EXIT TOURNAMENT")
    print("candidate rows:", len(candidates))
    print("policies:", [policy.name for policy in POLICIES])
    print("direction modes:", DIRECTION_MODES)
    print("central guard: 48h purge and train_last_exit < fold_start")

    outcomes = replay_all_policies(args, candidates, root, end)
    outcomes["entry_time"] = pd.to_datetime(outcomes["entry_time"], utc=True)
    outcomes["exit_time"] = pd.to_datetime(outcomes["exit_time"], utc=True)

    fold_starts = pd.date_range(score_start, end, freq="QS", inclusive="left")
    fit_rows: list[dict[str, object]] = []
    all_score_rows: list[dict[str, object]] = []
    selected_candidates: list[pd.DataFrame] = []
    for outer_fold, fold_start in enumerate(fold_starts):
        fold_end = min(fold_start + pd.offsets.QuarterBegin(startingMonth=1), end)
        winner, audit = select_for_fold(
            outcomes, train_start, fold_start, args.min_train
        )
        for row in audit:
            all_score_rows.append(
                {"outer_fold": outer_fold, "fold_start": fold_start, **row}
            )
        fit_rows.append(
            {
                "outer_fold": outer_fold,
                "fold_start": fold_start,
                "fold_end": fold_end,
                "selected_policy": winner["exit_policy"],
                "selected_direction_mode": winner["direction_mode"],
                "train_n": winner["n"],
                "train_mean_R": winner["mean_R"],
                "train_PF": winner["PF"],
                "train_DD_R": winner["DD_R"],
                "train_LCB_mean_R": winner["LCB_mean_R"],
                "train_last_exit": winner["train_last_exit"],
            }
        )
        test = outcomes[
            (outcomes["exit_policy"] == winner["exit_policy"])
            & (outcomes["entry_time"] >= fold_start)
            & (outcomes["entry_time"] < fold_end)
            & outcomes["resolved"]
        ]
        test = filter_direction(test, str(winner["direction_mode"])).copy()
        test["outer_fold"] = outer_fold
        selected_candidates.append(test)

    fit_audit = pd.DataFrame(fit_rows)
    score_audit = pd.DataFrame(all_score_rows)
    outer_pool = pd.concat(selected_candidates, ignore_index=True)
    selected = apply_single_position(outer_pool)

    summary_rows = [{"label": "ALL", **book_metrics(selected)}]
    for direction, subset in selected.groupby("direction", sort=True):
        summary_rows.append(
            {"label": str(direction).upper(), **book_metrics(subset)}
        )
    summary = pd.DataFrame(summary_rows)

    fold_rows: list[dict[str, object]] = []
    for outer_fold, subset in selected.groupby("outer_fold", sort=True):
        row = {"outer_fold": int(outer_fold), **book_metrics(subset)}
        fold_rows.append(row)
    folds = pd.DataFrame(fold_rows)

    all_row = summary.iloc[0]
    active_folds = len(folds)
    positive_folds = int((folds["total_R"] > 0.0).sum())
    checks = {
        "trades_at_least_150": int(all_row["n"]) >= 150,
        "win_rate_at_least_50": float(all_row["WR_pct"]) >= 50.0,
        "profit_factor_at_least_1p50": float(all_row["PF"]) >= 1.50,
        "total_R_positive": float(all_row["total_R"]) > 0.0,
        "drawdown_at_most_10R": float(all_row["DD_R"]) <= 10.0,
        "positive_folds_at_least_60pct": (
            active_folds > 0 and positive_folds / active_folds >= 0.60
        ),
    }
    decision = pd.DataFrame(
        [{"check": check, "passed": passed} for check, passed in checks.items()]
    )

    outcomes.to_csv(output_root / "v5_all_policy_outcomes.csv", index=False)
    score_audit.to_csv(output_root / "v5_training_score_audit.csv", index=False)
    fit_audit.to_csv(output_root / "v5_fit_audit.csv", index=False)
    selected.to_csv(output_root / "v5_outer_selected_trades.csv", index=False)
    summary.to_csv(output_root / "v5_summary.csv", index=False)
    folds.to_csv(output_root / "v5_fold_audit.csv", index=False)
    decision.to_csv(output_root / "v5_decision.csv", index=False)

    print("\nFIT AUDIT")
    print(fit_audit.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nOUTER SUMMARY")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nOUTER FOLDS")
    print(folds.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nPRE-REGISTERED DECISION")
    print(decision.to_string(index=False))
    print("V5 VERDICT:", "PASS" if all(checks.values()) else "FAIL")
    print("WROTE", output_root)


if __name__ == "__main__":
    main()
