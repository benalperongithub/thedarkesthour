from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.tp_ranking import TP_FEATURES, fit_tp_ranker
from scripts.run_causal_scanner import _metrics
from scripts.run_walkforward_ranker import (
    _book_row,
    _fold_starts,
    _select,
    _training_slice,
)


FAMILIES = (
    "trend_pullback",
    "compression_breakout",
    "impulse_continuation",
)
KEYS = ("symbol", "entry_time", "direction", "stop_pct")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Causal TP-probability ranker over the deduplicated TDH family union."
    )
    parser.add_argument("--tapes", nargs="+", required=True)
    parser.add_argument("--train-start", required=True)
    parser.add_argument("--score-start", required=True)
    parser.add_argument("--end", required=True, help="Exclusive UTC end")
    parser.add_argument("--alpha", type=float, default=10.0)
    parser.add_argument("--min-train", type=int, default=750)
    parser.add_argument("--min-probability", type=float, default=0.50)
    parser.add_argument("--simulations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260805)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def _union_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    if not frames:
        raise ValueError("at least one tape is required")
    combined = pd.concat(frames, ignore_index=True)
    combined["entry_time"] = pd.to_datetime(combined["entry_time"], utc=True)
    combined["exit_time"] = pd.to_datetime(combined["exit_time"], utc=True)
    combined["net_R"] = pd.to_numeric(combined["net_R"], errors="raise")
    combined["stop_pct"] = pd.to_numeric(combined["stop_pct"], errors="raise")
    unknown = set(combined["family"].astype(str)).difference(FAMILIES)
    if unknown:
        raise ValueError(f"unknown families in tapes: {sorted(unknown)}")

    grouped = combined.groupby(list(KEYS), sort=False, dropna=False)
    for column in ("exit_time", "exit_reason", "bars_held"):
        if int(grouped[column].nunique(dropna=False).max()) > 1:
            raise ValueError(f"family outcome mismatch in {column}")
    spread = grouped["net_R"].agg(lambda values: values.max() - values.min())
    if float(spread.max()) > 1e-8:
        raise ValueError("family outcome mismatch in net_R")

    base = combined.sort_values([*KEYS, "family"], kind="stable").drop_duplicates(
        list(KEYS), keep="first"
    )
    flags = (
        combined.assign(_present=1)
        .pivot_table(
            index=list(KEYS),
            columns="family",
            values="_present",
            aggfunc="max",
            fill_value=0,
        )
        .reset_index()
    )
    flags.columns.name = None
    for family in FAMILIES:
        if family not in flags:
            flags[family] = 0
        flags.rename(columns={family: f"family_{family}"}, inplace=True)
    family_columns = [f"family_{family}" for family in FAMILIES]
    flags["family_count"] = flags[family_columns].sum(axis=1)
    union = base.drop(columns=["family"]).merge(
        flags,
        on=list(KEYS),
        how="inner",
        validate="one_to_one",
    )
    return union.sort_values(["entry_time", "symbol"], kind="stable").reset_index(
        drop=True
    )


def main() -> None:
    args = _parse_args()
    if not 0.0 < args.min_probability < 1.0:
        raise ValueError("min-probability must lie in (0, 1)")
    if args.min_train < 100:
        raise ValueError("min-train must be at least 100")
    if args.simulations < 1:
        raise ValueError("simulations must be positive")
    train_start = pd.to_datetime(args.train_start, utc=True)
    score_start = pd.to_datetime(args.score_start, utc=True)
    end = pd.to_datetime(args.end, utc=True)
    if not train_start < score_start < end:
        raise ValueError("require train-start < score-start < end")

    frames = []
    for path_text in args.tapes:
        path = Path(path_text)
        frame = pd.read_csv(path)
        frame = frame[
            frame["resolved"].astype(str).str.lower().isin({"true", "1"})
        ].copy()
        frames.append(frame)
    union = _union_frames(frames)
    union = union[
        union["entry_time"].ge(train_start)
        & union["entry_time"].lt(end)
        & union["exit_time"].lt(end)
    ].copy()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    union.to_csv(output_root / "v3_union_statefree.csv", index=False)

    scored_parts: list[pd.DataFrame] = []
    fit_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    starts = _fold_starts(score_start, end)
    for fold_number, fold_start in enumerate(starts):
        fold_end = min(fold_start + pd.DateOffset(months=3), end)
        train = _training_slice(union, fold_start)
        test = union[
            union["entry_time"].ge(fold_start)
            & union["entry_time"].lt(fold_end)
        ].copy()
        if len(train) < args.min_train:
            raise SystemExit(
                f"fold {fold_start.date()} has {len(train)} training rows; "
                f"minimum is {args.min_train}"
            )
        if test.empty:
            continue
        model = fit_tp_ranker(train, alpha=args.alpha)
        test["predicted_tp_probability"] = model.predict_proba(test)
        test["outer_fold"] = fold_number
        test["fit_cutoff"] = fold_start
        scored_parts.append(test)
        fit_rows.append(
            {
                "outer_fold": fold_number,
                "fold_start": fold_start,
                "fold_end": fold_end,
                "train_rows": len(train),
                "train_last_exit": train["exit_time"].max(),
                "test_rows": len(test),
                "train_TP_pct": 100.0
                * float(train["exit_reason"].eq("TP_SINGLE_EXCHANGE").mean()),
                "score_mean": float(test["predicted_tp_probability"].mean()),
                "score_max": float(test["predicted_tp_probability"].max()),
                "p50_candidates": int(
                    (test["predicted_tp_probability"] >= args.min_probability).sum()
                ),
            }
        )
        for name, value in zip(
            ("intercept", *TP_FEATURES),
            model.coefficients,
        ):
            coefficient_rows.append(
                {
                    "outer_fold": fold_number,
                    "fold_start": fold_start,
                    "feature": name,
                    "coefficient": float(value),
                }
            )

    if not scored_parts:
        raise SystemExit("no outer-fold candidates were scored")
    scored = pd.concat(scored_parts, ignore_index=True).sort_values(
        ["entry_time", "symbol"], kind="stable"
    )
    scored.to_csv(output_root / "v3_walkforward_scored.csv", index=False)
    books = {
        "TP_LOGIT_P50_PRIMARY": _select(
            scored,
            "predicted_tp_probability",
            minimum=args.min_probability,
        ),
        "TP_LOGIT_ALL_DIAGNOSTIC": _select(scored, "predicted_tp_probability"),
        "MAX_LIQUIDITY_DIAGNOSTIC": _select(scored, "daily_quote_volume"),
    }
    weekdays = len(
        pd.bdate_range(score_start.date(), (end - pd.Timedelta(days=1)).date())
    )
    years = (end - score_start).total_seconds() / (365.25 * 86_400.0)
    audit_rows = [
        _book_row(label, book, weekdays, len(starts), years)
        for label, book in books.items()
    ]

    primary_eligible = scored[
        scored["predicted_tp_probability"] >= args.min_probability
    ]
    random_total = np.empty(args.simulations)
    random_dd = np.empty(args.simulations)
    for simulation in range(args.simulations):
        rng = np.random.default_rng(args.seed + simulation)
        random_book = _select(
            primary_eligible,
            "predicted_tp_probability",
            rng=rng,
        )
        metrics = _metrics(random_book, weekdays)
        random_total[simulation] = metrics["total_R"]
        random_dd[simulation] = metrics["DD_R"]
    primary_total = float(audit_rows[0]["total_R"])
    audit_rows[0].update(
        {
            "random_total_R_p05": float(np.quantile(random_total, 0.05)),
            "random_total_R_median": float(np.median(random_total)),
            "random_total_R_p95": float(np.quantile(random_total, 0.95)),
            "random_DD_R_median": float(np.median(random_dd)),
            "ranker_minus_random_median_R": float(
                primary_total - np.median(random_total)
            ),
            "p_random_ge_ranker": float((random_total >= primary_total).mean()),
        }
    )

    for label, book in books.items():
        book.to_csv(output_root / f"{label.lower()}_selected.csv", index=False)
    audit = pd.DataFrame(audit_rows)
    audit.to_csv(output_root / "v3_selector_audit.csv", index=False)
    pd.DataFrame(fit_rows).to_csv(output_root / "v3_fit_audit.csv", index=False)
    pd.DataFrame(coefficient_rows).to_csv(
        output_root / "v3_coefficient_audit.csv", index=False
    )

    fold_rows: list[dict[str, object]] = []
    fold_periods = {
        int(row["outer_fold"]): (
            pd.Timestamp(row["fold_start"]),
            pd.Timestamp(row["fold_end"]),
        )
        for row in fit_rows
    }
    for label, book in books.items():
        for fold, sub in book.groupby("outer_fold", sort=True):
            fold_start, fold_end = fold_periods[int(fold)]
            fold_weekdays = len(
                pd.bdate_range(
                    fold_start.date(),
                    (fold_end - pd.Timedelta(days=1)).date(),
                )
            )
            fold_rows.append(
                {
                    "selector": label,
                    "outer_fold": fold,
                    **_metrics(sub, max(1, fold_weekdays)),
                }
            )
    pd.DataFrame(fold_rows).to_csv(output_root / "v3_fold_audit.csv", index=False)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 340)
    pd.set_option("display.float_format", lambda value: f"{value:.4f}")
    print("TDH V3 CAUSAL TP UNION RANKER")
    print("Union rows:", len(union), "from raw family rows:", sum(map(len, frames)))
    print("Every training label exited before its quarterly fit cutoff.")
    print("\nFIT AUDIT")
    print(pd.DataFrame(fit_rows).to_string(index=False))
    print("\nSELECTOR AUDIT")
    print(audit.to_string(index=False))
    print("\nWROTE", output_root)


if __name__ == "__main__":
    main()
