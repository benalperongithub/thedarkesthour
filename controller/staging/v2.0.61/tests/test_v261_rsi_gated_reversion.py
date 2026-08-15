from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'
ADAPTER = ROOT / 'adapter' / 'tdh_strategy_lab_research_adapter.py'


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'import failed: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONTROLLER_MODULE = load_module('tdh_v261_controller_test', CONTROLLER)
ADAPTER_MODULE = load_module('tdh_v261_adapter_test', ADAPTER)


def synthetic_frame(rows: int = 720) -> pd.DataFrame:
    index = pd.date_range('2025-01-01', periods=rows, freq='15min', tz='UTC')
    x = np.arange(rows, dtype=float)
    close = 100.0 + 2.2 * np.sin(x / 5.0) + 0.7 * np.sin(x / 17.0)
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) + 0.35
    low = np.minimum(open_, close) - 0.35
    volume = 1_000.0 + 80.0 * (1.0 + np.sin(x / 11.0))
    return pd.DataFrame(
        {
            'open': open_,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
        },
        index=index,
    )


class V261RsiGatedReversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = CONTROLLER_MODULE.kernel.registry()
        cls.experiment = experiments[
            CONTROLLER_MODULE.V261_PACKET_A_EXPERIMENT_ID
        ]
        cls.performance = CONTROLLER_MODULE.kernel.performance_config(
            cls.experiment, 'BTCUSDT'
        )

    def test_exact_packet_a_registry_and_unknown_family_fail_closed(self):
        status = CONTROLLER_MODULE.kernel.v261_registry_status()
        self.assertEqual(status['seed_count'], 1)
        self.assertTrue(status['family_registered'])
        self.assertTrue(status['candidate_baseline_negative_control_bound'])
        self.assertTrue(status['closed_bar_only'])
        self.assertFalse(status['trading_actions'])
        self.assertFalse(status['exchange_api_access'])

        drift = copy.deepcopy(self.performance)
        drift['params']['adx_max'] = 21
        with self.assertRaises(CONTROLLER_MODULE.kernel.ResearchContractError):
            CONTROLLER_MODULE.kernel.validate_config(drift)

        unknown = copy.deepcopy(self.performance)
        unknown['family'] = 'FREEFORM_LLM_FAMILY'
        with self.assertRaises(CONTROLLER_MODULE.kernel.ResearchContractError):
            CONTROLLER_MODULE.kernel.validate_config(unknown)

    def test_candidate_baseline_and_negative_control_are_bound(self):
        frame = synthetic_frame()
        candidate = CONTROLLER_MODULE.kernel.control_config(
            self.performance, 'PERFORMANCE'
        )
        baseline = CONTROLLER_MODULE.kernel.control_config(
            self.performance, 'BASELINE'
        )
        negative = CONTROLLER_MODULE.kernel.control_config(
            self.performance, 'NEGATIVE_CONTROL'
        )
        candidate_signal, _, meta = ADAPTER_MODULE.strategy_signal(
            frame, candidate
        )
        baseline_signal, _, _ = ADAPTER_MODULE.strategy_signal(frame, baseline)
        negative_signal, _, _ = ADAPTER_MODULE.strategy_signal(frame, negative)

        self.assertGreater(int((baseline_signal != 0.0).sum()), 0)
        self.assertTrue((negative_signal == -candidate_signal).all())
        self.assertTrue(
            ((candidate_signal == 0.0) | (candidate_signal == baseline_signal)).all()
        )
        self.assertEqual(meta['feature_timing'], 'closed_bar_only')
        self.assertEqual(meta['entry_timing'], 'next_bar_open')
        self.assertEqual(meta['target_r_multiple'], 2.0)

    def test_future_bars_do_not_change_closed_bar_backtest(self):
        frame = synthetic_frame()
        start = frame.index[120]
        end = frame.index[520]
        before = ADAPTER_MODULE.simulate(
            frame, self.performance, start, end, 1.0
        )
        changed = frame.copy()
        changed.loc[changed.index >= frame.index[560], ['open', 'high', 'low', 'close']] *= 5.0
        after = ADAPTER_MODULE.simulate(
            changed, self.performance, start, end, 1.0
        )
        self.assertEqual(before, after)
        self.assertTrue(before['v261_family'])
        self.assertEqual(before['risk_fraction_current_equity'], 0.01)

    def test_empty_frontier_admits_only_exact_reviewed_packet_a(self):
        context = {
            'contract_version': '2.0.2',
            'novelty_frontier': [],
            'latest_s1_financial_evidence': {},
            'negative_memory': [],
            'research_program_memory': {},
        }
        updated = CONTROLLER_MODULE._v261_packet_a_replenishment(
            context, 'codex'
        )
        self.assertEqual(len(updated['novelty_frontier']), 1)
        item = updated['novelty_frontier'][0]
        self.assertEqual(item['config'], self.performance)
        event = updated['v261_packet_a_replenishment']
        self.assertTrue(event['candidate_baseline_negative_control_required'])
        self.assertTrue(event['s1_only'])
        self.assertFalse(event['trading_actions'])
        self.assertFalse(event['exchange_api_access'])

        peer = CONTROLLER_MODULE._v261_packet_a_replenishment(
            context, 'claude'
        )
        self.assertEqual(peer, context)

    def test_runtime_contract_preserves_offline_fail_closed_boundary(self):
        contract = CONTROLLER_MODULE.runtime_binding_contract()
        self.assertTrue(contract['v261_only_reviewed_packet_a_is_auto_admitted'])
        self.assertTrue(contract['v261_candidate_baseline_negative_control_bound'])
        self.assertTrue(contract['v261_closed_bar_only'])
        self.assertTrue(contract['v261_s1_only'])
        self.assertTrue(contract['v260_spoofed_or_freeform_seed_transition_fails_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])

    def test_full_scout_inbox_skips_provider_and_accounts_rollover(self):
        original_here = CONTROLLER_MODULE.HERE
        original_capacity = CONTROLLER_MODULE.V254_SCOUT_INBOX_MAX_FILES
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                release = root / 'v2.0.61'
                release.mkdir()
                inbox = root / 'frontier-scout-inbox'
                inbox.mkdir()
                (inbox / 'TDH-SCOUT-000001-test.json').write_text(
                    '{}', encoding='utf-8'
                )
                CONTROLLER_MODULE.HERE = release
                CONTROLLER_MODULE.V254_SCOUT_INBOX_MAX_FILES = 1

                status = CONTROLLER_MODULE._v261_scout_inbox_status()
                self.assertEqual(status['inbox_count'], 1)
                self.assertFalse(status['provider_allowed'])
                self.assertTrue(status['checked_before_provider'])

                class Dummy:
                    _avu = {
                        'codex': {},
                        'claude': {'billable_tokens': 8348},
                    }

                dummy = Dummy()
                with self.assertRaisesRegex(
                    CONTROLLER_MODULE.LabError,
                    'capacity reached before provider',
                ):
                    CONTROLLER_MODULE.Controller._run_frontier_scout(
                        dummy,
                        root,
                        {},
                        {},
                        {},
                        'CACHE_HIT',
                    )
                self.assertFalse(
                    hasattr(dummy, '_v254_scout_attempted'),
                    'provider attempt marker must not be set when inbox is full',
                )

                round_dir = root / 'round-01'
                round_dir.mkdir()
                CONTROLLER_MODULE.Controller._v261_write_frontier_usage_accounting(
                    dummy, round_dir
                )
                accounting = json.loads(
                    (round_dir / 'TOKEN_ACCOUNTING_V245.json').read_text(
                        encoding='utf-8'
                    )
                )
                self.assertEqual(
                    accounting['subagent_usage']['claude']['billable_tokens'],
                    8348,
                )
                self.assertTrue(
                    accounting['v261_frontier_rollover_usage_accounted']
                )
        finally:
            CONTROLLER_MODULE.HERE = original_here
            CONTROLLER_MODULE.V254_SCOUT_INBOX_MAX_FILES = original_capacity


if __name__ == '__main__':
    unittest.main()
