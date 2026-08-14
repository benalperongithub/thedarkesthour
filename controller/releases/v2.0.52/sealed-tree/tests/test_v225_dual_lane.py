from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v225_dual_lane_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def candidate(actor: str, index: int, family: str, experiment: str, symbol: str = "BTCUSDT", timeframe: str = "1h"):
    return {
        "candidate_id": f"{actor}-r01-c{index:02d}",
        "config": {
            "family": family,
            "symbol": symbol,
            "timeframe": timeframe,
            "experiment_id": experiment,
            "params": {"x": index},
            "control_mode": "PERFORMANCE",
        },
    }


class V225DualLaneTests(unittest.TestCase):
    def test_distinct_family_merge_drops_peer_collision_and_exact_duplicate(self):
        module = load_controller()
        codex = {
            "contract_version": "2.0.2",
            "candidates": [candidate("codex", 1, "MA_TREND", "A")],
        }
        exact = candidate("claude", 1, "MA_TREND", "A")
        exact["config"] = dict(codex["candidates"][0]["config"])
        exact["candidate_id"] = "claude-r01-c01"
        same_family = candidate("claude", 2, "MA_TREND", "B", symbol="ETHUSDT")
        distinct = candidate("claude", 3, "FILTER_BREAKOUT", "C", symbol="ETHUSDT")
        claude = {
            "contract_version": "2.0.2",
            "candidates": [exact, same_family, distinct],
        }
        merged = module.distinct_family_merge(codex, claude, 1)
        self.assertEqual(len(merged["candidates"]), 2)
        self.assertEqual(
            {item["config"]["family"] for item in merged["candidates"]},
            {"MA_TREND", "FILTER_BREAKOUT"},
        )
        batch = merged["controller_batch"]
        self.assertEqual(batch["dropped_exact_config_duplicates"], 1)
        self.assertEqual(batch["dropped_same_family_peer_candidates"], 1)
        self.assertEqual(batch["codex_families"], ["MA_TREND"])
        self.assertEqual(batch["claude_families"], ["FILTER_BREAKOUT"])

    def test_peer_frontier_excludes_codex_family(self):
        module = load_controller()
        frontier = [
            {"config": {"family": "MA_TREND", "timeframe": "4h"}},
            {"config": {"family": "FILTER_BREAKOUT", "timeframe": "1h"}},
            {"config": {"family": "DONCHIAN_VOL", "timeframe": "6h"}},
        ]
        filtered = module.filter_frontier_for_peer(frontier, "MA_TREND")
        self.assertEqual(
            [item["config"]["family"] for item in filtered],
            ["FILTER_BREAKOUT", "DONCHIAN_VOL"],
        )

    def test_scalping_quota_is_fail_closed_until_executable_seeds_exist(self):
        module = load_controller()
        current = module.scalping_lane_status([
            {"config": {"family": "MA_TREND", "timeframe": "1h"}},
            {"config": {"family": "DONCHIAN_VOL", "timeframe": "6h"}},
        ])
        self.assertEqual(current["status"], "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS")
        self.assertEqual(current["eligible_frontier_configs"], 0)
        self.assertEqual(current["one_minute_status"], "BLOCKED_NOT_REGISTERED_OR_EXECUTABLE")

        future = module.scalping_lane_status([
            {"config": {"family": "FILTER_BREAKOUT", "timeframe": "5m"}},
            {"config": {"family": "MA_TREND", "timeframe": "15m"}},
        ])
        self.assertEqual(future["status"], "ACTIVE_EXECUTABLE_5M_15M")
        self.assertEqual(future["eligible_frontier_configs"], 2)
        self.assertEqual(future["eligible_families"], ["FILTER_BREAKOUT", "MA_TREND"])

    def test_shared_context_and_peer_findings_are_wired_into_both_prompt_paths(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        for marker in (
            "SHARED_RESEARCH_CONTEXT.json",
            "shared_research_context",
            "prior_shared_research_context",
            "codex_findings",
            "claude_findings",
            "same_epoch_distinct_family_required",
            "dropped_same_family_peer_candidates",
            "historical_config_duplicate_forbidden",
        ):
            self.assertIn(marker, source)

    def test_v224_s1_contract_remains_authoritative(self):
        module = load_controller()
        bad = {
            "trade_count": 17,
            "net_win_rate": 0.50,
            "realized_payoff_ratio": 1.935,
            "max_drawdown_pct": 2.0,
            "expectancy_r": 0.48,
            "weekday_trades": 0.015,
            "profit_factor": 1.95,
            "simultaneous_positions_max": 1,
        }
        self.assertFalse(module.authoritative_s1_hard_target_pass(bad))
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()
