from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"
CONTROLLER = ROOT / "strategy_lab_controller.py"
PHOENIX_PYTHON = Path("/srv/tdh-research/phoenix-venv/bin/python")


def run_phoenix(script: str) -> str:
    completed = subprocess.run(
        [str(PHOENIX_PYTHON), "-c", textwrap.dedent(script), str(ADAPTER)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout)
    return completed.stdout


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v235_controller_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V235EquityAccountingTests(unittest.TestCase):
    def test_high_frequency_loss_cannot_create_negative_capital_or_dd_above_100(self):
        output = run_phoenix(
            """
            import importlib.util, sys
            from pathlib import Path
            import pandas as pd

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location("v235_a", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            start = pd.Timestamp("2024-04-01", tz="UTC")
            end = pd.Timestamp("2024-07-01", tz="UTC")
            trades = [{"pnl_r": -0.20} for _ in range(6000)]
            legacy = module._ORIGINAL_METRICS_FROM_TRADES(trades, start, end)
            current = module._runtime_compounded_metrics_from_trades(trades, start, end)
            assert legacy["net_return_pct"] < -100.0
            assert legacy["max_drawdown_pct"] > 100.0
            assert current["final_capital"] >= 0.0
            assert current["net_return_pct"] >= -100.0
            assert 0.0 <= current["max_drawdown_pct"] <= 100.0
            assert current["accounting_basis"] == "CURRENT_EQUITY_COMPOUNDED_RISK_V1"
            assert current["risk_fraction_current_equity"] == 0.01
            assert current["legacy_additive_net_return_pct"] == legacy["net_return_pct"]
            assert current["legacy_additive_max_drawdown_pct"] == legacy["max_drawdown_pct"]
            print("V235_BOUNDED_EQUITY_OK")
            """
        )
        self.assertIn("V235_BOUNDED_EQUITY_OK", output)

    def test_compounding_changes_only_equity_fields_not_signal_statistics(self):
        output = run_phoenix(
            """
            import importlib.util, math, sys
            from pathlib import Path
            import pandas as pd

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location("v235_b", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            start = pd.Timestamp("2025-01-01", tz="UTC")
            end = pd.Timestamp("2025-04-01", tz="UTC")
            trades = ([{"pnl_r": 1.5} for _ in range(50)]
                      + [{"pnl_r": -0.8} for _ in range(70)]
                      + [{"pnl_r": 0.3} for _ in range(20)])
            legacy = module._ORIGINAL_METRICS_FROM_TRADES(trades, start, end)
            current = module._runtime_compounded_metrics_from_trades(trades, start, end)
            for key in ("trade_count", "net_win_rate", "realized_payoff_ratio",
                        "expectancy_r", "weekday_trades", "profit_factor",
                        "simultaneous_positions_max"):
                assert current[key] == legacy[key], (key, current[key], legacy[key])
            assert math.isfinite(current["final_capital"])
            assert current["final_capital"] >= 0.0
            assert current["max_drawdown_pct"] <= 100.0
            print("V235_SIGNAL_STATS_PRESERVED_OK")
            """
        )
        self.assertIn("V235_SIGNAL_STATS_PRESERVED_OK", output)

    def test_runtime_aggregate_financial_fields_remain_bounded(self):
        output = run_phoenix(
            """
            import importlib.util, sys
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location("v235_c", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            common = {
                "net_win_rate": 0.4, "realized_payoff_ratio": 1.0,
                "expectancy_r": -0.1, "weekday_trades": 2.0,
                "profit_factor": 0.8, "simultaneous_positions_max": 1,
            }
            folds = [
                {"metrics": {**common, "trade_count": 100,
                    "max_drawdown_pct": 99.9, "net_return_pct": -99.0,
                    "net_pnl": -19800.0, "legacy_additive_net_return_pct": -500.0,
                    "legacy_additive_max_drawdown_pct": 500.0, "account_ruined": False}},
                {"metrics": {**common, "trade_count": 110,
                    "max_drawdown_pct": 100.0, "net_return_pct": -100.0,
                    "net_pnl": -20000.0, "legacy_additive_net_return_pct": -900.0,
                    "legacy_additive_max_drawdown_pct": 900.0, "account_ruined": True}},
            ]
            value = module._runtime_compounded_aggregate_folds(folds)
            assert value["final_capital"] == 0.0
            assert value["net_pnl"] == -20000.0
            assert value["net_return_pct"] == -100.0
            assert value["max_drawdown_pct"] == 100.0
            assert value["account_ruined"] is True
            assert value["legacy_additive_net_return_pct"] == -900.0
            assert value["legacy_additive_max_drawdown_pct"] == 900.0
            print("V235_AGGREGATE_BOUNDED_OK")
            """
        )
        self.assertIn("V235_AGGREGATE_BOUNDED_OK", output)

    def test_authoritative_s1_gate_identity_remains_unchanged(self):
        module = load_controller()
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()
