from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


FILE_PATTERN = re.compile(r"(.+)_sl(\d{2})_trades\.csv")


def _profit_factor(values: pd.Series) -> float:
    pnl = pd.to_numeric(values, errors="raise").to_numpy(dtype=float)
    gains = pnl[pnl > 0.0].sum()
    losses = -pnl[pnl < 0.0].sum()
    return float(gains / losses) if losses > 0.0 else float("inf")


def _realized_rr(values: pd.Series) -> float:
    pnl = pd.to_numeric(values, errors="raise")
    winners = pnl[pnl > 0.0]
    losers = pnl[pnl < 0.0]
    if winners.empty or losers.empty:
        return float("nan")
    return float(winners.mean() / -losers.mean())


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit and compare a TDH family/stop screening tournament."
    )
    parser.add_argument(
        "--root",
        default="results/v1_mini_q1_2025",
        help="Directory containing matching *_summary.csv and *_trades.csv files.",
    )
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-03-31")
    parser.add_argument("--notional", type=float, default=1000.0)
    parser.add_argument("--expected-variants", type=int, default=12)
    parser.add_argument("--expected-symbols", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    root = Path(args.root)
    trade_files = sorted(root.glob("*_trades.csv"))
    summary_files = sorted(root.glob("*_summary.csv"))
    weekdays = len(pd.bdate_range(args.start, args.end))

    if len(trade_files) != args.expected_variants:
        raise AssertionError(
            f"expected {args.expected_variants} trade files, found {len(trade_files)}"
        )
    if len(summary_files) != args.expected_variants:
        raise AssertionError(
            f"expected {args.expected_variants} summary files, found {len(summary_files)}"
        )
    if args.notional <= 0.0:
        raise ValueError("notional must be positive")

    rows: list[dict[str, object]] = []

    for trade_path in trade_files:
        match = FILE_PATTERN.fullmatch(trade_path.name)
        if match is None:
            raise AssertionError(f"unexpected trade filename: {trade_path.name}")

        family = match.group(1)
        stop = int(match.group(2)) / 100.0
        label = f"{family}_sl{int(round(stop * 100)):02d}"
        summary_path = root / f"{label}_summary.csv"
        if not summary_path.exists():
            raise AssertionError(f"missing summary: {summary_path}")

        trades = pd.read_csv(trade_path)
        summary = pd.read_csv(summary_path)
        summary = summary[summary["status"].eq("ok")].copy()

        if len(summary) != args.expected_symbols:
            raise AssertionError(
                f"{label}: expected {args.expected_symbols} symbols, got {len(summary)}"
            )
        if len(trades) != int(summary["trades"].sum()):
            raise AssertionError(f"{label}: summary/trade row mismatch")

        trades["entry_time"] = pd.to_datetime(
            trades["entry_time"], utc=True, errors="raise"
        )
        pnl = pd.to_numeric(trades["net_pnl"], errors="raise")
        entry = pd.to_numeric(trades["entry_price"], errors="raise")
        sl = pd.to_numeric(trades["sl_price"], errors="raise")
        stop_error = float((((entry - sl).abs() / entry) - stop).abs().max())
        duplicates = int(
            trades.duplicated(["symbol", "entry_time", "direction"]).sum()
        )
        weekend_entries = int((trades["entry_time"].dt.dayofweek >= 5).sum())

        summary_net = float(pd.to_numeric(summary["net_pnl_usd"]).sum())
        trade_net = float(pnl.sum())
        pnl_difference = summary_net - trade_net
        # Summary rows are rounded to cents independently. Allow slightly more
        # than one cent per symbol while requiring the full-precision trade log
        # to remain the source of truth for every metric below.
        rounding_tolerance = 0.011 * len(summary)

        if duplicates:
            raise AssertionError(f"{label}: duplicate trade keys={duplicates}")
        if weekend_entries:
            raise AssertionError(f"{label}: weekend entries={weekend_entries}")
        if stop_error >= 1e-10:
            raise AssertionError(f"{label}: reporting stop error={stop_error}")
        if abs(pnl_difference) > rounding_tolerance:
            raise AssertionError(
                f"{label}: summary/trade PnL difference={pnl_difference:.6f}"
            )

        risk_usd = args.notional * stop
        trade_r = pnl / risk_usd
        long_mask = trades["direction"].astype(str).str.lower().eq("long")
        short_mask = trades["direction"].astype(str).str.lower().eq("short")
        symbol_r = (
            trades.assign(_R=trade_r).groupby("symbol", sort=False)["_R"].sum()
        )
        positive_symbol_r = symbol_r[symbol_r > 0.0].sort_values(ascending=False)
        top2_positive_share = (
            float(100.0 * positive_symbol_r.head(2).sum() / positive_symbol_r.sum())
            if not positive_symbol_r.empty
            else float("nan")
        )

        rows.append(
            {
                "label": label,
                "family": family,
                "stop_pct": stop,
                "n": len(trades),
                "raw_per_weekday": len(trades) / weekdays,
                "WR_pct": 100.0 * float((pnl > 0.0).mean()),
                "PF": _profit_factor(pnl),
                "realized_RR": _realized_rr(pnl),
                "mean_R": float(trade_r.mean()),
                "total_R": float(trade_r.sum()),
                "profitable_symbols": int((symbol_r > 0.0).sum()),
                "PF_gt_1_symbols": int(
                    (pd.to_numeric(summary["profit_factor"]) > 1.0).sum()
                ),
                "long_n": int(long_mask.sum()),
                "long_PF": _profit_factor(pnl[long_mask]),
                "long_R": float(trade_r[long_mask].sum()),
                "short_n": int(short_mask.sum()),
                "short_PF": _profit_factor(pnl[short_mask]),
                "short_R": float(trade_r[short_mask].sum()),
                "top2_positive_share_pct": top2_positive_share,
                "pnl_rounding_difference": pnl_difference,
                "max_stop_error": stop_error,
            }
        )

    result = pd.DataFrame(rows).sort_values(
        ["mean_R", "PF", "n"], ascending=False
    ).reset_index(drop=True)
    result["both_directions_positive"] = (
        result["long_R"].gt(0.0) & result["short_R"].gt(0.0)
    )

    robustness = (
        result.groupby("family", as_index=False)
        .agg(
            variants=("label", "size"),
            profitable_stops=("total_R", lambda x: int((x > 0.0).sum())),
            min_PF=("PF", "min"),
            median_PF=("PF", "median"),
            median_mean_R=("mean_R", "median"),
            worst_mean_R=("mean_R", "min"),
            both_sides_stops=("both_directions_positive", "sum"),
            min_profitable_symbols=("profitable_symbols", "min"),
        )
        .sort_values(["worst_mean_R", "median_mean_R"], ascending=False)
        .reset_index(drop=True)
    )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 260)
    pd.set_option("display.float_format", lambda value: f"{value:.4f}")

    display_columns = [
        "label",
        "n",
        "raw_per_weekday",
        "WR_pct",
        "PF",
        "realized_RR",
        "mean_R",
        "total_R",
        "profitable_symbols",
        "long_PF",
        "long_R",
        "short_PF",
        "short_R",
        "both_directions_positive",
        "top2_positive_share_pct",
    ]
    print("TDH MINI TOURNAMENT — R-NORMALIZED RAW BOOKS")
    print(result[display_columns].to_string(index=False))
    print("\nFAMILY ROBUSTNESS ACROSS ALL THREE STOPS")
    print(robustness.to_string(index=False))

    result_path = root / "mini_tournament_audit.csv"
    robustness_path = root / "mini_family_robustness.csv"
    result.to_csv(result_path, index=False)
    robustness.to_csv(robustness_path, index=False)
    print(f"\nWROTE {result_path}")
    print(f"WROTE {robustness_path}")
    print("MINI TOURNAMENT INTEGRITY ACCEPTED")


if __name__ == "__main__":
    main()
