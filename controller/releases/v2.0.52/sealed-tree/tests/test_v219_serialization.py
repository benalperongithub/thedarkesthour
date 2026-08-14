import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"
PHOENIX_PYTHON = Path("/srv/tdh-research/phoenix-venv/bin/python")


class V219SerializationTests(unittest.TestCase):
    def test_real_backtest_python_serializes_numpy_scalars(self):
        script = textwrap.dedent(
            """
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            import numpy as np
            import pandas as pd

            adapter_path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location(
                "tdh_v219_adapter_regression",
                adapter_path,
            )
            if spec is None or spec.loader is None:
                raise RuntimeError("adapter import failed")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "result.json"
                module.write_object(
                    output,
                    {
                        "numpy_bool": np.bool_(True),
                        "numpy_int": np.int64(7),
                        "numpy_float": np.float64(1.25),
                        "timestamp": pd.Timestamp("2026-08-12T00:00:00Z"),
                    },
                )
                value = json.loads(output.read_text(encoding="utf-8"))
                assert value["numpy_bool"] is True
                assert value["numpy_int"] == 7
                assert value["numpy_float"] == 1.25
                assert value["timestamp"] == "2026-08-12T00:00:00+00:00"

            failed_metrics = {
                "trade_count": 386,
                "net_win_rate": 0.373,
                "realized_payoff_ratio": 1.712,
                "max_drawdown_pct": 29.9,
                "expectancy_r": 0.011,
                "profit_factor": 1.018,
                "weekday_trades": 1.36,
            }
            assert module.hard_target_pass(failed_metrics) is False
            print("V219_RUNTIME_REGRESSION_OK")
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
        self.assertIn("V219_RUNTIME_REGRESSION_OK", completed.stdout)

    def test_offline_contract_remains_present(self):
        config = (ROOT / "config.json").read_text(encoding="utf-8")
        self.assertIn('"research_mode": "offline"', config)
        self.assertIn('"trading_actions": false', config)
        self.assertIn('"exchange_api_access": false', config)


if __name__ == "__main__":
    unittest.main()
