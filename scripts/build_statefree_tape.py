from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.replay import net_r_after_costs, replay_fixed_rr
from darkest_hour.signals import (
    FAMILIES,
    NEUTRAL,
    SignalConfig,
    build_candidate_frame,
)


FEATURE_COLUMNS = (
    "adx",
    "volume_ratio",
    "compression_rank",
    "trend_signed_atr",
    "impulse_signed_atr",
    "breakout_signed_atr",
    "adx_excess",
    "log_volume_excess",
    "compression_strength",
    "raw_strength",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build causally aligned, state-free TDH candidate/outcome tapes."
    )
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--exchange", default="binance")
    parser.add_argument("--tf", default="5m")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True, help="Exclusive UTC end timestamp")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument(
        "--families",
        nargs="+",
        default=[
            "trend_pullback",
            "compression_breakout",
            "impulse_continuation",
        ],
    )
    parser.add_argument("--stops", nargs="+", type=float, default=[0.01, 0.02, 0.03])
    parser.add_argument("--rr-ratio", type=float, default=2.0)
    parser.add_argument("--time-stop-bars", type=int, default=576)
    parser.add_argument("--round-trip-cost-bps", type=float, default=9.5)
    parser.add_argument("--funding-apr", type=float, default=0.1095)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def _load_bars(root: Path, exchange: str, symbol: str, tf: str) -> pd.DataFrame:
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


def _symbols(args: argparse.Namespace, root: Path) -> list[str]:
    if args.symbols:
        return sorted(set(args.symbols))
    exchange_root = root / args.exchange
    return sorted(path.name for path in exchange_root.iterdir() if path.is_dir())


def _validate_args(args: argparse.Namespace) -> None:
    unknown = set(args.families).difference(FAMILIES)
    if unknown:
        raise ValueError(f"unknown families: {sorted(unknown)}")
    if "failed_breakout" in args.families:
        raise ValueError("failed_breakout was eliminated by the frozen mini screen")
    if any(stop <= 0.0 for stop in args.stops):
        raise ValueError("all stops must be positive")
    if args.rr_ratio <= 0.0:
        raise ValueError("rr-ratio must be positive")


def main() -> None:
    args = _parse_args()
    _validate_args(args)
    root = Path(args.data_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    start = pd.to_datetime(args.start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    if end <= start:
        raise ValueError("end must be after start")

    symbols = _symbols(args, root)
    tapes: dict[str, list[dict[str, object]]] = defaultdict(list)

    print("TDH STATE-FREE TAPE BUILD")
    print("symbols:", len(symbols))
    print("families:", args.families)
    print("stops:", args.stops)
    print("candidate period:", start, "->", end, "(end exclusive)")

    for symbol_number, symbol in enumerate(symbols, start=1):
        try:
            all_bars = _load_bars(root, args.exchange, symbol, args.tf)
        except FileNotFoundError as exc:
            print(f"[{symbol_number:02d}/{len(symbols):02d}] {symbol}: SKIP {exc}")
            continue

        # The evaluation horizon is sealed at end. Signals may use all earlier
        # history for warm-up, but exits cannot read the next period.
        bars = all_bars[all_bars.index < end].copy()
        if bars.empty:
            print(f"[{symbol_number:02d}/{len(symbols):02d}] {symbol}: SKIP empty")
            continue

        symbol_counts: list[str] = []
        for family in args.families:
            cfg = SignalConfig(family=family)
            candidates = build_candidate_frame(bars, cfg)
            eligible = (
                candidates["direction"].ne(NEUTRAL)
                & candidates.index.to_series().ge(start)
                & candidates.index.to_series().lt(end)
            )
            positions = np.flatnonzero(eligible.to_numpy())
            symbol_counts.append(f"{family}={len(positions)}")

            for stop in args.stops:
                label = f"{family}_sl{int(round(stop * 100)):02d}"
                for entry_pos in positions:
                    row = candidates.iloc[entry_pos]
                    direction = str(row["direction"])
                    replay = replay_fixed_rr(
                        bars,
                        entry_pos=int(entry_pos),
                        direction=direction,
                        stop_pct=float(stop),
                        rr_ratio=args.rr_ratio,
                        time_stop_bars=args.time_stop_bars,
                        worst_case_intrabar=True,
                    )
                    entry_time = pd.Timestamp(bars.index[entry_pos])
                    net_r = (
                        net_r_after_costs(
                            replay.gross_return,
                            stop,
                            entry_time,
                            replay.exit_time,
                            args.round_trip_cost_bps,
                            args.funding_apr,
                        )
                        if replay.resolved
                        else float("nan")
                    )
                    record: dict[str, object] = {
                        "symbol": symbol,
                        "family": family,
                        "stop_pct": stop,
                        "entry_time": entry_time,
                        "exit_time": replay.exit_time,
                        "direction": direction,
                        "entry_price": float(row["entry_price"]),
                        "exit_price": replay.exit_price,
                        "tp_price": replay.tp_price,
                        "sl_price": replay.sl_price,
                        "exit_reason": replay.exit_reason,
                        "bars_held": replay.bars_held,
                        "gross_R": replay.gross_r,
                        "net_R": net_r,
                        "resolved": replay.resolved,
                    }
                    for feature in FEATURE_COLUMNS:
                        record[feature] = float(row[feature])
                    tapes[label].append(record)

        print(
            f"[{symbol_number:02d}/{len(symbols):02d}] {symbol}: "
            + " ".join(symbol_counts),
            flush=True,
        )

    if not tapes:
        raise SystemExit(
            "no state-free candidates were produced; verify data paths, dates, "
            "symbols and signal parameters"
        )

    manifest_rows = []
    for label, records in sorted(tapes.items()):
        frame = pd.DataFrame.from_records(records)
        frame = frame.sort_values(["entry_time", "symbol"], kind="stable")
        path = output_root / f"{label}_statefree.csv"
        frame.to_csv(path, index=False)
        manifest_rows.append(
            {
                "label": label,
                "rows": len(frame),
                "resolved": int(frame["resolved"].sum()),
                "symbols": int(frame["symbol"].nunique()),
                "path": str(path),
            }
        )
        print("WROTE", path, "rows=", len(frame))

    manifest = pd.DataFrame(manifest_rows)
    manifest_path = output_root / "manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    print("WROTE", manifest_path)


if __name__ == "__main__":
    main()
