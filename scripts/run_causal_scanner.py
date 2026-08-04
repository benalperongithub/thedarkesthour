from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build one-global-position TDH books from state-free tapes."
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True, help="Exclusive UTC end timestamp")
    parser.add_argument("--simulations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260805)
    return parser.parse_args()


def _drawdown(values: np.ndarray) -> float:
    equity = np.r_[0.0, np.cumsum(values)]
    return float(np.max(np.maximum.accumulate(equity) - equity))


def _profit_factor(values: np.ndarray) -> float:
    gains = values[values > 0.0].sum()
    losses = -values[values < 0.0].sum()
    return float(gains / losses) if losses > 0.0 else float("inf")


def _groups(frame: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.DataFrame]]:
    return [
        (pd.Timestamp(timestamp), group.reset_index(drop=True))
        for timestamp, group in frame.groupby("entry_time", sort=True)
    ]


def _select(
    groups: list[tuple[pd.Timestamp, pd.DataFrame]],
    rng: np.random.Generator | None,
) -> pd.DataFrame:
    selected: list[pd.Series] = []
    blocked_until: pd.Timestamp | None = None

    for entry_time, group in groups:
        # Conservative same-bar rule: a position resolving at timestamp T does
        # not permit another entry at the close stamped T.
        if blocked_until is not None and entry_time <= blocked_until:
            continue
        if rng is None:
            row = group.sort_values(
                ["raw_strength", "symbol"],
                ascending=[False, True],
                kind="stable",
            ).iloc[0]
        else:
            row = group.iloc[int(rng.integers(0, len(group)))]
        selected.append(row)
        blocked_until = pd.Timestamp(row["exit_time"])

    if not selected:
        return pd.DataFrame(columns=groups[0][1].columns if groups else [])
    return pd.DataFrame(selected).reset_index(drop=True)


def _metrics(frame: pd.DataFrame, weekdays: int) -> dict[str, float]:
    if frame.empty:
        return {
            "n": 0,
            "per_weekday": 0.0,
            "WR_pct": float("nan"),
            "mean_R": float("nan"),
            "total_R": 0.0,
            "PF": float("nan"),
            "DD_R": 0.0,
        }
    r = pd.to_numeric(frame["net_R"], errors="raise").to_numpy(dtype=float)
    exit_order = np.argsort(frame["exit_time"].to_numpy(), kind="stable")
    return {
        "n": len(frame),
        "per_weekday": len(frame) / weekdays,
        "WR_pct": 100.0 * float((r > 0.0).mean()),
        "mean_R": float(r.mean()),
        "total_R": float(r.sum()),
        "PF": _profit_factor(r),
        "DD_R": _drawdown(r[exit_order]),
    }


def main() -> None:
    args = _parse_args()
    if args.simulations < 1:
        raise ValueError("simulations must be positive")
    root = Path(args.root)
    tape_paths = sorted(root.glob("*_statefree.csv"))
    if not tape_paths:
        raise SystemExit(f"no *_statefree.csv files found under {root}")
    start = pd.to_datetime(args.start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    weekdays = len(pd.bdate_range(start.date(), (end - pd.Timedelta(days=1)).date()))
    rows: list[dict[str, object]] = []

    for file_number, path in enumerate(tape_paths):
        label = path.name.removesuffix("_statefree.csv")
        frame = pd.read_csv(path)
        frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)
        frame["exit_time"] = pd.to_datetime(frame["exit_time"], utc=True)
        frame = frame[
            frame["resolved"].astype(str).str.lower().isin({"true", "1"})
            & frame["entry_time"].ge(start)
            & frame["entry_time"].lt(end)
            & frame["exit_time"].lt(end)
        ].copy()
        frame = frame[np.isfinite(pd.to_numeric(frame["raw_strength"]))]
        frame = frame.sort_values(["entry_time", "symbol"], kind="stable")
        grouped = _groups(frame)
        top = _select(grouped, rng=None)
        top_metrics = _metrics(top, weekdays)
        selected_path = root / f"{label}_top_strength_selected.csv"
        top.to_csv(selected_path, index=False)

        random_total = np.empty(args.simulations)
        random_dd = np.empty(args.simulations)
        random_n = np.empty(args.simulations)
        for simulation in range(args.simulations):
            rng = np.random.default_rng(args.seed + 10_000 * file_number + simulation)
            random_book = _select(grouped, rng=rng)
            random_metrics = _metrics(random_book, weekdays)
            random_total[simulation] = random_metrics["total_R"]
            random_dd[simulation] = random_metrics["DD_R"]
            random_n[simulation] = random_metrics["n"]

        top_total = float(top_metrics["total_R"])
        top_percentile = 100.0 * float((random_total < top_total).mean())
        direction = top["direction"].astype(str).str.lower() if len(top) else pd.Series(dtype=str)
        top_r = pd.to_numeric(top["net_R"], errors="raise") if len(top) else pd.Series(dtype=float)
        long_r = top_r[direction.eq("long")].to_numpy(dtype=float)
        short_r = top_r[direction.eq("short")].to_numpy(dtype=float)
        competing_timestamps = int(sum(len(group) > 1 for _, group in grouped))

        rows.append(
            {
                "label": label,
                "eligible_candidates": len(frame),
                "signal_timestamps": len(grouped),
                "competing_timestamps": competing_timestamps,
                **top_metrics,
                "ret_DD": (
                    top_metrics["total_R"] / top_metrics["DD_R"]
                    if top_metrics["DD_R"] > 0.0
                    else float("nan")
                ),
                "long_n": len(long_r),
                "long_R": float(long_r.sum()),
                "long_PF": _profit_factor(long_r) if len(long_r) else float("nan"),
                "short_n": len(short_r),
                "short_R": float(short_r.sum()),
                "short_PF": _profit_factor(short_r) if len(short_r) else float("nan"),
                "random_n_median": float(np.median(random_n)),
                "random_total_R_p05": float(np.quantile(random_total, 0.05)),
                "random_total_R_median": float(np.median(random_total)),
                "random_total_R_p95": float(np.quantile(random_total, 0.95)),
                "random_DD_R_median": float(np.median(random_dd)),
                "random_DD_R_p95": float(np.quantile(random_dd, 0.95)),
                "top_minus_random_median_R": float(
                    top_total - np.median(random_total)
                ),
                "top_percentile": top_percentile,
                "p_random_ge_top": float((random_total >= top_total).mean()),
            }
        )

    if not rows:
        raise SystemExit("no scanner rows were produced")

    result = pd.DataFrame(rows).sort_values(
        ["mean_R", "ret_DD"], ascending=False
    ).reset_index(drop=True)
    output = root / "causal_scanner_audit.csv"
    result.to_csv(output, index=False)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)
    pd.set_option("display.float_format", lambda value: f"{value:.4f}")
    print("TDH ONE-GLOBAL-POSITION CAUSAL SCANNER")
    print(result.to_string(index=False))
    print("\nWROTE", output)


if __name__ == "__main__":
    main()
