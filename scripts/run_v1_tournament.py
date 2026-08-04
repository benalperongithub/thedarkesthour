from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from darkest_hour.signals import FAMILIES


STOPS = (0.01, 0.02, 0.03)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the frozen TDH v1 family/stop tournament through Phoenix S1."
    )
    parser.add_argument("--phoenix-root", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--output-root", default="results/v1_tournament")
    parser.add_argument("--config", default="configs/tdh_v1_5m.yaml")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    phoenix_root = Path(args.phoenix_root).resolve()
    output_root = (repo_root / args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(repo_root), str(phoenix_root), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)

    manifest = []
    for family in FAMILIES:
        for stop in STOPS:
            label = f"{family}_sl{int(round(stop * 100)):02d}"
            summary = output_root / f"{label}_summary.csv"
            trades = output_root / f"{label}_trades.csv"
            command = [
                args.python,
                str(phoenix_root / "scripts/phx_symbol_sweep.py"),
                "--base-config",
                str((repo_root / args.config).resolve()),
                "--symbols",
                *args.symbols,
                "--set",
                f"strategy.tdh_family={family}",
                "--set",
                f"strategy.sl_pct={stop}",
                "--out",
                str(summary),
                "--trades-out",
                str(trades),
            ]
            print("\n===== TDH", label, "=====", flush=True)
            print(" ".join(command), flush=True)
            completed = subprocess.run(command, cwd=phoenix_root, env=env, check=False)
            manifest.append((label, completed.returncode, summary, trades))
            if completed.returncode != 0:
                raise SystemExit(f"{label} failed with exit code {completed.returncode}")

    manifest_path = output_root / "manifest.tsv"
    manifest_path.write_text(
        "label\texit_code\tsummary\ttrades\n"
        + "".join(
            f"{label}\t{code}\t{summary}\t{trades}\n"
            for label, code, summary, trades in manifest
        )
    )
    print("\nWROTE", manifest_path)


if __name__ == "__main__":
    main()

