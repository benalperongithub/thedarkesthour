from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prove Phoenix stateful trades are an exact subset of a TDH state-free tape."
    )
    parser.add_argument("--statefree", required=True)
    parser.add_argument("--phoenix-trades", required=True)
    parser.add_argument("--stop", type=float, required=True)
    parser.add_argument("--notional", type=float, default=1000.0)
    parser.add_argument("--pnl-tolerance", type=float, default=1e-8)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.stop <= 0.0 or args.notional <= 0.0:
        raise ValueError("stop and notional must be positive")

    tape = pd.read_csv(args.statefree)
    actual = pd.read_csv(args.phoenix_trades)
    for frame in (tape, actual):
        frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)

    tape = tape[tape["resolved"].astype(str).str.lower().isin({"true", "1"})]
    keys = ["symbol", "entry_time", "direction"]
    if tape.duplicated(keys).any():
        raise AssertionError("state-free tape contains duplicate trade keys")
    if actual.duplicated(keys).any():
        raise AssertionError("Phoenix log contains duplicate trade keys")

    merged = actual.merge(
        tape,
        on=keys,
        how="left",
        suffixes=("_phoenix", "_statefree"),
        indicator=True,
        validate="one_to_one",
    )
    missing = int(merged["_merge"].ne("both").sum())
    if missing:
        print(merged.loc[merged["_merge"].ne("both"), keys].head(20).to_string(index=False))
        raise AssertionError(f"Phoenix entries missing from state-free tape: {missing}")

    entry_error = (
        pd.to_numeric(merged["entry_price_phoenix"])
        - pd.to_numeric(merged["entry_price_statefree"])
    ).abs()
    stop_error = (
        pd.to_numeric(merged["sl_price_phoenix"])
        - pd.to_numeric(merged["sl_price_statefree"])
    ).abs()
    bars_mismatch = (
        pd.to_numeric(merged["bars_held_phoenix"])
        != pd.to_numeric(merged["bars_held_statefree"])
    )
    reason_mismatch = (
        merged["exit_reason_phoenix"].astype(str)
        != merged["exit_reason_statefree"].astype(str)
    )
    phoenix_r = pd.to_numeric(merged["net_pnl"]) / (args.notional * args.stop)
    pnl_error = (phoenix_r - pd.to_numeric(merged["net_R"])).abs()

    print("TDH PHOENIX / STATE-FREE PARITY")
    print("Phoenix trades:", len(actual))
    print("state-free resolved candidates:", len(tape))
    print("missing Phoenix entries:", missing)
    print("entry price max error:", float(entry_error.max()))
    print("stop price max error:", float(stop_error.max()))
    print("bars mismatches:", int(bars_mismatch.sum()))
    print("reason mismatches:", int(reason_mismatch.sum()))
    print("net R max error:", float(pnl_error.max()))

    assert float(entry_error.max()) < 1e-12
    assert float(stop_error.max()) < 1e-12
    assert not bars_mismatch.any()
    assert not reason_mismatch.any()
    assert float(pnl_error.max()) <= args.pnl_tolerance
    print("PHOENIX STATEFUL BOOK IS AN EXACT STATE-FREE SUBSET")


if __name__ == "__main__":
    main()
