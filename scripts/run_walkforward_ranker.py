from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from darkest_hour.ranking import fit_logistic_ranker
from scripts.run_causal_scanner import _metrics, _profit_factor


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quarterly causal logistic coin ranker with one global position."
    )
    parser.add_argument("--tape", required=True)
    parser.add_argument("--train-start", required=True)
    parser.add_argument("--score-start", required=True)
    parser.add_argument("--end", required=True, help="Exclusive UTC end")
    parser.add_argument("--alpha", type=float, default=10.0)
    parser.add_argument("--prior-strength", type=float, default=20.0)
    parser.add_argument("--min-train", type=int, default=750)
    parser.add_argument("--min-probability", type=float, default=0.50)
    parser.add_argument("--simulations", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260805)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def _select(
    frame: pd.DataFrame,
    score_column: str,
    *,
    minimum: float | None = None,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    eligible = frame
    if minimum is not None:
        eligible = eligible[eligible[score_column] >= minimum]
    selected: list[pd.Series] = []
    blocked_until: pd.Timestamp | None = None
    for entry_time, group in eligible.groupby("entry_time", sort=True):
        entry_time = pd.Timestamp(entry_time)
        if blocked_until is not None and entry_time <= blocked_until:
            continue
        if rng is None:
            row = group.sort_values(
                [score_column, "symbol"],
                ascending=[False, True],
                kind="stable",
            ).iloc[0]
        else:
            row = group.iloc[int(rng.integers(0, len(group)))]
        selected.append(row)
        blocked_until = pd.Timestamp(row["exit_time"])
    if not selected:
        return pd.DataFrame(columns=frame.columns)
    return pd.DataFrame(selected).reset_index(drop=True)


def _fold_starts(start: pd.Timestamp, end: pd.Timestamp) -> list[pd.Timestamp]:
    starts = list(pd.date_range(start, end, freq="QS", inclusive="left"))
    if not starts or starts[0] != start:
        starts.insert(0, start)
    return [pd.Timestamp(value) for value in starts if value < end]


def _training_slice(frame: pd.DataFrame, fit_cutoff: pd.Timestamp) -> pd.DataFrame:
    """Return only labels that were observable strictly before model fit."""
    return frame[frame["exit_time"].lt(fit_cutoff)].copy()


def _book_row(
    label: str,
    frame: pd.DataFrame,
    weekdays: int,
    fold_count: int,
    years: float,
) -> dict[str, object]:
    metrics = _metrics(frame, weekdays)
    direction = frame["direction"].astype(str).str.lower()
    values = pd.to_numeric(frame["net_R"], errors="raise")
    long_r = values[direction.eq("long")].to_numpy(dtype=float)
    short_r = values[direction.eq("short")].to_numpy(dtype=float)
    winners = values[values > 0.0]
    losers = values[values < 0.0]
    realized_rr = (
        float(winners.mean() / -losers.mean())
        if len(winners) and len(losers)
        else float("nan")
    )
    fold_totals = frame.groupby("outer_fold", sort=True)["net_R"].sum()
    positive_folds = int((fold_totals > 0.0).sum())
    positive_trade_r = values.clip(lower=0.0)
    positive_total = float(positive_trade_r.sum())
    long_positive = float(positive_trade_r[direction.eq("long")].sum())
    short_positive = float(positive_trade_r[direction.eq("short")].sum())
    direction_positive_share = (
        max(long_positive, short_positive) / positive_total
        if positive_total > 0.0
        else float("nan")
    )
    symbol_net = frame.assign(_net_R=values).groupby("symbol")["_net_R"].sum()
    positive_symbol_net = symbol_net[symbol_net > 0.0].sort_values(ascending=False)
    top5_positive_symbol_share = (
        float(positive_symbol_net.head(5).sum() / positive_symbol_net.sum())
        if len(positive_symbol_net)
        else float("nan")
    )
    annual_r = metrics["total_R"] / years
    monthly_r = annual_r / 12.0
    safe_risk = 2_000.0 / metrics["DD_R"] if metrics["DD_R"] > 0.0 else 0.0
    return {
        "selector": label,
        **metrics,
        "realized_RR": realized_rr,
        "ret_DD": (
            metrics["total_R"] / metrics["DD_R"]
            if metrics["DD_R"] > 0.0
            else float("nan")
        ),
        "long_n": len(long_r),
        "long_R": float(long_r.sum()),
        "long_PF": _profit_factor(long_r) if len(long_r) else float("nan"),
        "short_n": len(short_r),
        "short_R": float(short_r.sum()),
        "short_PF": _profit_factor(short_r) if len(short_r) else float("nan"),
        "positive_folds": positive_folds,
        "active_folds": int(fold_totals.size),
        "all_outer_folds": fold_count,
        "worst_fold_R": float(fold_totals.min()) if len(fold_totals) else 0.0,
        "max_direction_positive_share_pct": 100.0 * direction_positive_share,
        "top5_positive_symbol_share_pct": 100.0 * top5_positive_symbol_share,
        "annual_R": annual_r,
        "monthly_R": monthly_r,
        "DD_USD_at_R200": 200.0 * metrics["DD_R"],
        "monthly_USD_at_R200": 200.0 * monthly_r,
        "safe_risk_for_USD2000_DD": safe_risk,
        "monthly_USD_at_safe_risk": safe_risk * monthly_r,
    }


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

    frame = pd.read_csv(args.tape)
    frame["entry_time"] = pd.to_datetime(frame["entry_time"], utc=True)
    frame["exit_time"] = pd.to_datetime(frame["exit_time"], utc=True)
    frame = frame[
        frame["resolved"].astype(str).str.lower().isin({"true", "1"})
        & frame["entry_time"].ge(train_start)
        & frame["entry_time"].lt(end)
        & frame["exit_time"].lt(end)
    ].copy()
    frame = frame.sort_values(["entry_time", "symbol"], kind="stable")

    scored_parts: list[pd.DataFrame] = []
    fit_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    starts = _fold_starts(score_start, end)
    for fold_number, fold_start in enumerate(starts):
        fold_end = min(fold_start + pd.DateOffset(months=3), end)
        # This is the central leakage guard: even an earlier entry is unknown
        # if its trade has not EXITED before the model's fit timestamp.
        train = _training_slice(frame, fold_start)
        test = frame[
            frame["entry_time"].ge(fold_start)
            & frame["entry_time"].lt(fold_end)
        ].copy()
        if len(train) < args.min_train:
            raise SystemExit(
                f"fold {fold_start.date()} has only {len(train)} training rows; "
                f"minimum is {args.min_train}"
            )
        if test.empty:
            continue
        model = fit_logistic_ranker(
            train,
            alpha=args.alpha,
            prior_strength=args.prior_strength,
        )
        test["predicted_win_probability"] = model.predict_proba(test)
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
                "train_WR_pct": 100.0 * float((train["net_R"] > 0.0).mean()),
                "score_mean": float(test["predicted_win_probability"].mean()),
                "score_max": float(test["predicted_win_probability"].max()),
                "p50_candidates": int(
                    (test["predicted_win_probability"] >= args.min_probability).sum()
                ),
            }
        )
        for name, value in zip(
            ("intercept", *model.feature_names),
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
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    stem = Path(args.tape).name.removesuffix("_statefree.csv")
    score_path = output_root / f"{stem}_walkforward_scored.csv"
    scored.to_csv(score_path, index=False)

    books = {
        "LOGIT_P50_PRIMARY": _select(
            scored,
            "predicted_win_probability",
            minimum=args.min_probability,
        ),
        "LOGIT_ALL_DIAGNOSTIC": _select(scored, "predicted_win_probability"),
        "MAX_LIQUIDITY_V1_BASELINE": _select(scored, "daily_quote_volume"),
        "RAW_STRENGTH_DIAGNOSTIC": _select(scored, "raw_strength"),
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
        scored["predicted_win_probability"] >= args.min_probability
    ]
    random_total = np.empty(args.simulations)
    random_dd = np.empty(args.simulations)
    for simulation in range(args.simulations):
        rng = np.random.default_rng(args.seed + simulation)
        random_book = _select(
            primary_eligible,
            "predicted_win_probability",
            rng=rng,
        )
        random_metrics = _metrics(random_book, weekdays)
        random_total[simulation] = random_metrics["total_R"]
        random_dd[simulation] = random_metrics["DD_R"]

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
        book.to_csv(output_root / f"{stem}_{label.lower()}_selected.csv", index=False)
    audit = pd.DataFrame(audit_rows)
    audit.to_csv(output_root / f"{stem}_selector_audit.csv", index=False)
    pd.DataFrame(fit_rows).to_csv(
        output_root / f"{stem}_fit_audit.csv", index=False
    )
    pd.DataFrame(coefficient_rows).to_csv(
        output_root / f"{stem}_coefficient_audit.csv", index=False
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
            row = _metrics(sub, max(1, fold_weekdays))
            fold_rows.append({"selector": label, "outer_fold": fold, **row})
    pd.DataFrame(fold_rows).to_csv(
        output_root / f"{stem}_fold_audit.csv", index=False
    )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 320)
    pd.set_option("display.float_format", lambda value: f"{value:.4f}")
    print("TDH CAUSAL QUARTERLY COIN RANKER")
    print("Central guard: every training label exited before its fold fit cutoff.")
    print("\nFIT AUDIT")
    print(pd.DataFrame(fit_rows).to_string(index=False))
    print("\nSELECTOR AUDIT")
    print(audit.to_string(index=False))
    print("\nWROTE", output_root)


if __name__ == "__main__":
    main()
