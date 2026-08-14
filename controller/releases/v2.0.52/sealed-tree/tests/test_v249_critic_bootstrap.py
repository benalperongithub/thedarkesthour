from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = ROOT / 'strategy_lab_controller.py'

def load():
    spec = importlib.util.spec_from_file_location('tdh_v249_bootstrap_test', CTRL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class Tests(unittest.TestCase):
    def test_critic_bootstrap_uses_existing_config_object_not_config_path(self):
        source = CTRL.read_text(encoding='utf-8')
        self.assertNotIn('load_json(self.config_path)', source)
        self.assertIn("self.config.claude_user", source)
        self.assertIn("self.config.claude_bin", source)
        self.assertIn("self.config.worker_timeout_seconds", source)

    def test_evidence_only_and_usage_contracts_remain_enabled(self):
        m = load()
        c = m.runtime_binding_contract()
        self.assertTrue(c['evidence_only_critic'])
        self.assertTrue(c['failed_provider_usage_accounted'])
        self.assertTrue(c['critic_completed_required_for_cache'])
        self.assertFalse(c['trading_actions'])
        self.assertFalse(c['exchange_api_access'])
        self.assertIs(m.authoritative_s1_hard_target_pass, m.v224.authoritative_s1_hard_target_pass)

if __name__ == '__main__':
    unittest.main()
