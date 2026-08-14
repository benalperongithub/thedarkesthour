from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = ROOT / 'strategy_lab_controller.py'


def load():
    spec = importlib.util.spec_from_file_location('tdh_v243_test', CTRL)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def context():
    return {
        'contract_version': '2.0.2',
        'targets': {
            'net_win_rate': 0.5,
            'realized_payoff_ratio': 2.0,
            'max_drawdown_pct': 10.0,
        },
        'novelty_frontier': [{
            'config': {
                'experiment_id': 'MK-C-5M-STRICT',
                'family': 'MK_C_STR_LIQ_IMB',
                'symbol': 'BTCUSDT',
                'timeframe': '5m',
                'params': {'profile': 'STRICT'},
                'control_mode': 'PERFORMANCE',
            }
        }],
        'registered_candidate_contract': {
            'instruction': 'choose exact frontier config',
            'controller_owned_fields': ['config', 'family'],
            'dual_lane_contract': {
                'scalping_exploration': {
                    'status': 'ACTIVE_EXECUTABLE_5M_15M',
                    'one_minute_status': 'BLOCKED_NOT_REGISTERED_OR_EXECUTABLE',
                    'target_fraction': 0.3,
                }
            },
        },
        'latest_s1_financial_evidence': {
            'source_run_id': 'run-old',
            'prior_dual_agent_synthesis': {'large': 'X' * 4000},
            'candidates': [{
                'candidate_id': 'c1',
                'controller_verdict': 'FAIL',
                'metrics': {
                    'expectancy_r': -0.2,
                    'profit_factor': 0.7,
                    'net_win_rate': 0.3,
                    'realized_payoff_ratio': 1.1,
                    'max_drawdown_pct': 12.0,
                    'trade_count': 150,
                },
                'gates': {
                    'baseline_beaten': False,
                    'negative_control_beaten': False,
                },
                'observations': ['NEGATIVE_EXPECTANCY', 'LOW_WIN_RATE'],
            }],
        },
        'research_program_memory': {
            'completed_rounds': 244,
            'evaluated_s1_candidates': 1164,
            'status_counts': {'FAIL': 1163, 'PASS': 1},
            'observation_counts': {
                'NEGATIVE_EXPECTANCY': 1000,
                'PAYOFF_BELOW_TARGET': 900,
                'WIN_RATE_BELOW_TARGET': 850,
            },
            'positive_pnl_memory': {'large': 'Y' * 3000},
            'unresolved_audit_findings': [{
                'severity': 'HIGH',
                'claim': 'model verdict contradicts controller evidence ' * 10,
            }],
        },
        'global_research_memory': {'candidate_count': 1339},
        'tdh_research_selection': {
            'registry_version': 'v1',
            'blocked_by_data_family_count': 37,
            'robust_state_sha256': 'a' * 64,
            'family_cards': [
                {'family_id': 'MK_C_STR_LIQ_IMB'},
                {'family_id': 'TSMOM_RETURN_SIGN'},
            ],
        },
    }


def rows():
    return [
        {
            'experiment_id': 'TDH-LIT-0301',
            'family': 'TSMOM_RETURN_SIGN',
            'symbol': 'SOLUSDT',
            'timeframe': '4h',
            'positive_class': 'PROMISING_POSITIVE',
            'accounting': 'COMPOUNDED',
            'controller_verdict': 'FAIL',
            'metrics': {
                'net_pnl': 581.98,
                'expectancy_r': 0.0277,
                'profit_factor': 1.11,
                'net_win_rate': 0.4779,
                'realized_payoff_ratio': 0.99,
                'max_drawdown_pct': 6.41,
                'trade_count': 453,
            },
        },
        {
            'experiment_id': 'TDH-LIT-0301',
            'family': 'TSMOM_RETURN_SIGN',
            'symbol': 'DOGEUSDT',
            'timeframe': '4h',
            'positive_class': 'PROMISING_POSITIVE',
            'accounting': 'COMPOUNDED',
            'controller_verdict': 'FAIL',
            'metrics': {
                'net_pnl': 224.29,
                'expectancy_r': 0.0121,
                'profit_factor': 1.05,
                'net_win_rate': 0.4261,
                'realized_payoff_ratio': 0.98,
                'max_drawdown_pct': 7.49,
                'trade_count': 455,
            },
        },
        {
            'experiment_id': 'TDH-LIT-0261',
            'family': 'TSMOM_RETURN_SIGN',
            'symbol': 'DOGEUSDT',
            'timeframe': '4h',
            'positive_class': 'LEGACY_POSITIVE_QUARANTINED',
            'accounting': 'LEGACY',
            'metrics': {'net_pnl': 1100.0, 'expectancy_r': 0.2, 'profit_factor': 1.5},
        },
    ]


class Tests(unittest.TestCase):
    def test_cross_coin_specialist_finds_same_config_on_two_coins(self):
        m = load()
        packet = m.build_specialist_context(context(), positive_rows=rows())
        cross = packet['workers']['cross_coin']
        top = cross['top_cross_coin_configs'][0]
        self.assertEqual(top['experiment_id'], 'TDH-LIT-0301')
        self.assertEqual(top['unique_coins'], 2)
        self.assertEqual(top['coins'], ['DOGEUSDT', 'SOLUSDT'])
        self.assertEqual(cross['current_positive_records'], 2)
        self.assertTrue(packet['contract']['deterministic_no_llm'])
        self.assertEqual(packet['contract']['extra_provider_tokens'], 0)
        self.assertLessEqual(m._json_chars(packet), m.SPECIALIST_TOTAL_MAX_CHARS)

    def test_specialized_prompt_boundary_preserves_authoritative_fields(self):
        m = load()
        raw = context()
        specialized, packet = m.specialize_proposal_context(raw, positive_rows=rows())
        self.assertEqual(specialized['novelty_frontier'], raw['novelty_frontier'])
        self.assertEqual(specialized['targets'], raw['targets'])
        self.assertEqual(
            specialized['registered_candidate_contract'],
            raw['registered_candidate_contract'],
        )
        self.assertEqual(
            specialized['latest_s1_financial_evidence']['prior_dual_agent_synthesis'],
            'delegated_to_specialist_context',
        )
        self.assertNotIn('positive_pnl_memory', specialized['research_program_memory'])
        self.assertIn('specialist_context', specialized)
        self.assertTrue(
            specialized['specialist_context_contract'][
                'v242_final_prompt_optimizer_still_authoritative'
            ]
        )
        self.assertLess(m._json_chars(specialized), m._json_chars(raw))
        self.assertLessEqual(m._json_chars(packet), m.SPECIALIST_TOTAL_MAX_CHARS)

    def test_limits_and_s1_identity_are_unchanged(self):
        m = load()
        self.assertEqual(m.PROMPT_TARGET_MAX_CHARS, 12000)
        self.assertEqual(m.POST_S1_PRECHECK_HARD_LIMIT, 10000)
        self.assertEqual(m.PROMPT_HARD_CEILING_CHARS, 16000)
        self.assertIs(
            m.authoritative_s1_hard_target_pass,
            m.v242.authoritative_s1_hard_target_pass,
        )


if __name__ == '__main__':
    unittest.main()
