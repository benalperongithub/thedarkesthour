from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"
TASK = ROOT / "task.json"
PHOENIX_PYTHON = Path("/srv/tdh-research/phoenix-venv/bin/python")


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v234_scalping_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V234ScalpingFrontierTests(unittest.TestCase):
    def test_registry_extension_contains_eight_executable_scalping_seeds(self):
        module = load_controller()
        _, experiments = module.kernel.registry()
        scalping = [
            row for row in experiments.values()
            if str(row.get("experiment_id", "")).startswith("TDH-SCALP-")
        ]
        self.assertEqual(len(scalping), 8)
        self.assertEqual(
            {row["effective_timeframe"] for row in scalping}, {"5m", "15m"}
        )
        self.assertEqual(
            {row["family_id"] for row in scalping},
            {"FILTER_BREAKOUT", "SUPPORT_RES_BREAK", "MA_TREND", "VOLUME_TSMOM"},
        )
        for row in scalping:
            self.assertEqual(
                row["universe"],
                ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
            )
            config = module.kernel.performance_config(row, "BTCUSDT")
            self.assertEqual(config["timeframe"], row["effective_timeframe"])
            self.assertEqual(module.kernel.validate_config(config), config)

    def test_scalping_frontier_is_now_active_and_prioritized(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            frontier = module.build_scalping_frontier(Path(tmp), limit=2)
        self.assertEqual(len(frontier), 2)
        self.assertTrue(all(item["config"]["timeframe"] in {"5m", "15m"} for item in frontier))
        self.assertEqual(len({item["config"]["family"] for item in frontier}), 2)
        status = module.scalping_lane_status(frontier)
        self.assertEqual(status["status"], "ACTIVE_EXECUTABLE_5M_15M")
        self.assertEqual(status["eligible_frontier_configs"], 2)

    def test_task_disk_contract_stays_v224_but_runtime_command_binds_local_adapter(self):
        module = load_controller()
        task = json.loads(TASK.read_text(encoding="utf-8"))
        command = task["backtest_command"]
        self.assertEqual(command[1], module.SEALED_ADAPTER)
        rebound = module.local_backtest_command(command)
        self.assertEqual(rebound[0], module.PHOENIX_PYTHON)
        self.assertEqual(rebound[1], module.LOCAL_ADAPTER)
        self.assertEqual(rebound[2:], command[2:])

    def test_phoenix_interpreter_accepts_scalping_seed_through_local_adapter(self):
        script = r'''
import importlib.util, sys
from pathlib import Path
p = Path(sys.argv[1])
s = importlib.util.spec_from_file_location("tdh_v234_adapter_smoke", p)
m = importlib.util.module_from_spec(s)
sys.modules[s.name] = m
s.loader.exec_module(m)
_, experiments = m.kernel.registry()
row = experiments["TDH-SCALP-0001"]
config = m.kernel.performance_config(row, "BTCUSDT")
assert config["timeframe"] == "5m"
assert m.validate_config(config) == config
assert m.v221.validate_config(config) == config
assert m.v221.control_config(config, "BASELINE")["control_mode"] == "BASELINE"
print("V234_SCALPING_ADAPTER_OK")
'''
        completed = subprocess.run(
            [str(PHOENIX_PYTHON), "-c", script, str(ADAPTER)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("V234_SCALPING_ADAPTER_OK", completed.stdout)

    def test_authoritative_s1_gate_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()
