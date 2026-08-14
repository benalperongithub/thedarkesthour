from __future__ import annotations

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"
TASK = ROOT / "task.json"
PHOENIX_PYTHON = Path("/srv/tdh-research/phoenix-venv/bin/python")


class V222AccountingTests(unittest.TestCase):
    def test_reference_capital_reporting_and_v221_metric_parity(self):
        script = textwrap.dedent(
            """
            import importlib.util
            import math
            import sys
            from pathlib import Path
            import pandas as pd

            adapter_path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location("tdh_v222_accounting_runtime", adapter_path)
            if spec is None or spec.loader is None:
                raise RuntimeError("adapter import failed")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            start = pd.Timestamp("2025-01-01", tz="UTC")
            end = pd.Timestamp("2025-01-31", tz="UTC")
            trades = [{"pnl_r": 2.0}, {"pnl_r": -1.0}]

            old = module._ORIGINAL_METRICS_FROM_TRADES(trades, start, end)
            new = module.metrics_from_trades(trades, start, end)

            untouched = (
                "trade_count", "net_win_rate", "realized_payoff_ratio",
                "max_drawdown_pct", "expectancy_r", "weekday_trades",
                "profit_factor", "simultaneous_positions_max", "net_return_pct",
            )
            for key in untouched:
                assert old[key] == new[key], (key, old[key], new[key])

            assert new["initial_capital"] == 20000.0
            assert math.isclose(new["net_return_pct"], 1.0, abs_tol=1e-12)
            assert math.isclose(new["net_pnl"], 200.0, abs_tol=1e-9)
            assert math.isclose(new["final_capital"], 20200.0, abs_tol=1e-9)
            assert math.isclose(new["pnl_per_trade"], 100.0, abs_tol=1e-9)
            assert new["accounting_currency"] == "USD"
            assert new["accounting_basis"] == "REFERENCE_CAPITAL_REPORTING_ONLY"
            assert new["reference_capital_reporting_only"] is True
            assert old["net_pnl"] == old["net_return_pct"]
            assert new["net_pnl"] != old["net_pnl"]
            assert module.hard_target_pass(old) == module.hard_target_pass(new)
            print("V222_ACCOUNTING_RUNTIME_OK")
            """
        )
        completed = subprocess.run(
            [str(PHOENIX_PYTHON), "-c", script, str(ADAPTER)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("V222_ACCOUNTING_RUNTIME_OK", completed.stdout)

    def test_source_marks_reference_capital_as_reporting_only(self):
        source = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("REFERENCE_INITIAL_CAPITAL_USD = 20_000.0", source)
        self.assertIn('ACCOUNTING_BASIS = "REFERENCE_CAPITAL_REPORTING_ONLY"', source)
        self.assertIn('"reference_capital_reporting_only": True', source)

    def test_task_keeps_sealed_v224_phoenix_evaluator_for_orchestration_only_v225(self):
        task = json.loads(TASK.read_text(encoding="utf-8"))
        command = task["backtest_command"]
        self.assertEqual(
            command[1],
            "/srv/tdh-collab/controller/strategy-lab-v2/v2.0.24/adapter/tdh_strategy_lab_research_adapter.py",
        )
        self.assertNotIn("/v2.0.20/adapter/", command[1])
        self.assertNotIn("/v2.0.21/adapter/", command[1])
        self.assertNotIn("/v2.0.22/adapter/", command[1])
        self.assertNotIn("/v2.0.23/adapter/", command[1])


if __name__ == "__main__":
    unittest.main()
