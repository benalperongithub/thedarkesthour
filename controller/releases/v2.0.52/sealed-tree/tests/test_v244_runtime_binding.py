from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v244_runtime_binding_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def minimal_context():
    return {
        "contract_version": "2.0.2",
        "data_class": "DEVELOPMENT_VALIDATION_ONLY",
        "task_id": "tdh-strategy-lab-v2",
        "round_id": "TDH-R02",
        "research_round": 1,
        "trial_count": 0,
        "targets": {
            "net_win_rate": 0.50,
            "realized_payoff_ratio": 2.0,
            "max_drawdown_pct": 10.0,
        },
        "novelty_frontier": [{
            "config": {
                "control_mode": "PERFORMANCE",
                "experiment_id": "TDH-SCALP-0001",
                "family": "FILTER_BREAKOUT",
                "params": {"timeframe": "5m"},
                "symbol": "BTCUSDT",
                "timeframe": "5m",
            },
            "selected_approach": "CHANGE_STRATEGY_FAMILY",
        }],
        "latest_s1_financial_evidence": {
            "source_run_id": "prior-run",
            "candidates": [{
                "candidate_id": "prior-c1",
                "controller_verdict": "FAIL",
                "metrics": {
                    "expectancy_r": -0.20,
                    "profit_factor": 0.70,
                    "net_win_rate": 0.30,
                    "realized_payoff_ratio": 1.10,
                    "max_drawdown_pct": 8.0,
                },
                "gates": {
                    "baseline_beaten": False,
                    "negative_control_beaten": False,
                },
                "observations": ["NEGATIVE_EXPECTANCY"],
            }],
            "prior_dual_agent_synthesis": {
                "shared_research_context": {"source_run_id": "prior-run"}
            },
        },
        "research_program_memory": {
            "completed_rounds": 250,
            "evaluated_s1_candidates": 1200,
            "status_counts": {"PASS": 1, "FAIL": 1199},
            "observation_counts": {"NEGATIVE_EXPECTANCY": 1100},
            "unresolved_audit_findings": [],
        },
        "global_research_memory": {"candidate_count": 1400},
        "tdh_research_selection": {
            "registry_version": "tdh-registry-v1",
            "blocked_by_data_family_count": 37,
            "robust_state_sha256": "a" * 64,
            "family_cards": [{"family_id": "FILTER_BREAKOUT"}],
        },
        "registered_candidate_contract": {
            "instruction": "choose one supplied frontier seed",
            "promotion_contract": "controller only",
            "dual_lane_contract": {
                "actor": "codex",
                "historical_config_duplicate_forbidden": True,
                "same_epoch_distinct_family_required": True,
                "scalping_exploration": {
                    "status": "ACTIVE_EXECUTABLE_5M_15M",
                    "one_minute_status": "BLOCKED_NOT_REGISTERED_OR_EXECUTABLE",
                    "target_fraction": 0.30,
                },
            },
        },
        "previous_rounds": [],
    }


class V244RuntimeBindingTests(unittest.TestCase):
    def test_all_real_runtime_controller_refs_are_rebound(self):
        m = load_controller()
        contract = m.runtime_binding_contract()
        self.assertTrue(contract["all_controller_refs_bound"])
        self.assertEqual(contract["extra_provider_tokens"], 0)
        self.assertTrue(contract["specialists_are_deterministic_no_llm"])
        self.assertTrue(contract["v242_final_prompt_optimizer_inherited"])

        v240 = m.v243.v242.v240
        deep = (
            v240.v238.v237.v236.v235.v233.v232.v231.v230.v229.v228
            .v227.v226.v225.v220.v217
        )
        refs = [
            m.v243.Controller,
            m.v243.v242.Controller,
            v240.Controller,
            v240.v238.Controller,
            v240.v238.v237.Controller,
            deep.Controller,
            deep.v216.Controller,
        ]
        self.assertTrue(all(ref is m.Controller for ref in refs))

    def test_specialist_boundary_is_on_bound_controller_and_writes_artifact(self):
        m = load_controller()
        controller = object.__new__(m.Controller)
        self.assertTrue(hasattr(controller, "_spec"))

        with tempfile.TemporaryDirectory() as tmp:
            round_dir = Path(tmp)
            specialized = controller._spec(round_dir, "codex", minimal_context())
            artifact_path = round_dir / "CODEX_SPECIALIST_CONTEXT.json"
            self.assertTrue(artifact_path.is_file())
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertIn("specialist_context", specialized)
        self.assertEqual(artifact["extra_provider_tokens"], 0)
        self.assertTrue(artifact["no_llm_worker_invoked"])
        workers = artifact["specialist_context"]["workers"]
        self.assertEqual(
            set(workers),
            {"cross_coin", "s1_forensics", "positive_edge", "scalping_mtf", "memory_curator"},
        )

    def test_local_adapter_and_safety_contracts_remain_exact(self):
        m = load_controller()
        self.assertEqual(Path(m.LOCAL_ADAPTER).resolve(), ADAPTER.resolve())
        self.assertEqual(m.PROMPT_TARGET_MAX_CHARS, 12000)
        self.assertEqual(m.POST_S1_PRECHECK_HARD_LIMIT, 10000)
        self.assertEqual(m.PROMPT_HARD_CEILING_CHARS, 16000)
        self.assertIs(
            m.authoritative_s1_hard_target_pass,
            m.v224.authoritative_s1_hard_target_pass,
        )

    def test_main_fails_closed_on_binding_drift(self):
        m = load_controller()
        original = m.v243.v242.v240.Controller
        try:
            m.v243.v242.v240.Controller = object
            contract = m.runtime_binding_contract()
            self.assertFalse(contract["all_controller_refs_bound"])
        finally:
            m.v243.v242.v240.Controller = original


if __name__ == "__main__":
    unittest.main()
