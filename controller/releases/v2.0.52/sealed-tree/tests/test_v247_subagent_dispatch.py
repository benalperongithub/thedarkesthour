from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = ROOT / 'strategy_lab_controller.py'


def load():
    spec = importlib.util.spec_from_file_location('tdh_v247_dispatch_test', CTRL)
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def evidence():
    return {
        'version': 'tdh-avenox-isolated-evidence-v246',
        'cross_coin': [{
            'experiment_id': 'TDH-LIT-0464',
            'family': 'VOLUME_TSMOM',
            'coins': ['DOGEUSDT', 'XRPUSDT'],
            'unique_coins': 2,
            'avg_expectancy_r': 0.05,
        }],
        'positive_edge': [{
            'experiment_id': 'TDH-LIT-0464',
            'family': 'VOLUME_TSMOM',
            'symbol': 'XRPUSDT',
            'timeframe': '6h',
            'expectancy_r': 0.09,
            'profit_factor': 1.30,
        }],
        's1_forensics': {
            'dominant_failures': [
                ['PAYOFF_BELOW_TARGET', 100],
                ['WIN_RATE_BELOW_TARGET', 90],
            ],
            'latest_samples': [],
        },
        'frontier': [{
            'config': {
                'control_mode': 'PERFORMANCE',
                'experiment_id': 'TDH-LIT-0458',
                'family': 'MA_TREND',
                'params': {'fast': 20, 'slow': 200, 'timeframe': '4h'},
                'symbol': 'BTCUSDT',
                'timeframe': '4h',
            },
            'selected_approach': 'CHANGE_STRATEGY_FAMILY',
        }],
        'contract': {
            'advisory_only': True,
            'controller_only_promotion': True,
        },
    }


class Tests(unittest.TestCase):
    def test_v245_explicit_super_anchor_is_restored(self):
        m = load()
        self.assertIs(m.v245.Controller, m.V245_DISPATCH_ANCHOR)
        self.assertIs(m.V245_DISPATCH_ANCHOR, m.Controller.__mro__[2])
        self.assertIsNot(m.v245.Controller, m.Controller)

    def test_critic_and_main_claude_dispatch_skip_v245_method(self):
        m = load()
        obj = object.__new__(m.Controller)
        anchor = m.V245_DISPATCH_ANCHOR
        critic_target = super(anchor, obj).run_claude
        proposal_target = super(anchor, obj).run_claude_proposal
        researcher_target = super(anchor, obj).run_codex_audit
        self.assertIsNot(getattr(critic_target, '__func__', None), anchor.run_claude)
        self.assertIsNot(getattr(proposal_target, '__func__', None), anchor.run_claude_proposal)
        self.assertIsNot(getattr(researcher_target, '__func__', None), anchor.run_codex_audit)

    def test_runtime_refs_are_current_while_anchor_stays_original(self):
        m = load()
        c = m.runtime_binding_contract()
        self.assertTrue(c['all_controller_refs_bound'])
        self.assertTrue(c['v245_dispatch_anchor_preserved'])
        self.assertTrue(c['dispatch_anchor_is_mro_parent'])
        self.assertTrue(c['avenox_subagent_layer'])
        self.assertFalse(c['trading_actions'])
        self.assertFalse(c['exchange_api_access'])
        self.assertIs(m.authoritative_s1_hard_target_pass, m.v224.authoritative_s1_hard_target_pass)

    def test_subpacket_is_advisory_evidence_cluster_not_empty_candidate_audit(self):
        m = load()
        obj = object.__new__(m.Controller)
        packet = obj.subpacket(
            {'contract_version': '2.0.2', 'research_round': 1},
            evidence(),
            'AVENOX_DEEP_RESEARCH',
        )
        self.assertEqual(packet['candidates'][0]['candidate_id'], 'ADVISORY_EVIDENCE_CLUSTER')
        self.assertEqual(packet['controller_batch']['research_object']['object_type'], 'ADVISORY_EVIDENCE_CLUSTER')
        self.assertFalse(packet['controller_batch']['research_object']['promotion_eligible'])
        self.assertIn('NOT a proposal-validation', packet['audit_instruction'])
        self.assertIn('Keep approved_candidate_ids empty', packet['audit_instruction'])

    def test_v244_is_safe_main_entry_below_dispatch_anchor(self):
        source = CTRL.read_text(encoding='utf-8')
        self.assertIn('return v245.v244.main(argv)', source)
        self.assertIn('v245.Controller = V245_DISPATCH_ANCHOR', source)
        self.assertNotIn('subprocess.', source)
        self.assertNotIn('os.system', source)


if __name__ == '__main__':
    unittest.main()
