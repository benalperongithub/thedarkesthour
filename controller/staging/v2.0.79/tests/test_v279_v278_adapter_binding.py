from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError:
    np = None
    pd = None


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'adapter' / 'tdh_strategy_lab_research_adapter.py'


def load_adapter():
    spec = importlib.util.spec_from_file_location(
        'tdh_v279_v278_adapter_binding_test', ADAPTER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('adapter import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NUMERICAL_DEPS_AVAILABLE = np is not None and pd is not None
MODULE = load_adapter() if NUMERICAL_DEPS_AVAILABLE else None


@unittest.skipUnless(
    NUMERICAL_DEPS_AVAILABLE,
    'v2.0.79 numerical integration tests require the Phoenix environment',
)
class V279V278AdapterBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.experiments = experiments

    @staticmethod
    def frame(size: int = 420) -> pd.DataFrame:
        index = pd.date_range('2025-01-01', periods=size, freq='h', tz='UTC')
        x = np.arange(size, dtype=float)
        close = 100.0 + x * 0.08 + np.sin(x / 8.0) * 3.0
        volume = 1000.0 + (x % 73.0) * 17.0
        volume[::19] *= 4.0
        return pd.DataFrame({
            'open': close - 0.1,
            'high': close + 0.8,
            'low': close - 0.8,
            'close': close,
            'volume': volume,
        }, index=index)

    def config(self, experiment_id: str, symbol: str, mode='PERFORMANCE'):
        config = MODULE.kernel.performance_config(
            self.experiments[experiment_id], symbol
        )
        if mode != 'PERFORMANCE':
            config = MODULE.kernel.control_config(config, mode)
        return MODULE.kernel.validate_config(config)

    def test_exact_v278_identity_set_is_bound(self):
        self.assertEqual(
            MODULE.V279_EXPERIMENT_IDS,
            frozenset(MODULE.kernel.V278_IDENTITIES),
        )
        self.assertEqual(MODULE.V279_FAMILY, 'VOLUME_TSMOM')
        self.assertEqual(len(MODULE.V279_EXPERIMENT_IDS), 3)

    def test_all_four_runtime_symbols_use_v278_signal_path(self):
        frame = self.frame()
        experiment_id = 'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1H'
        for symbol in ('BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT'):
            signal, hold, meta = MODULE.strategy_signal(
                frame, self.config(experiment_id, symbol)
            )
            self.assertEqual(len(signal), len(frame))
            self.assertTrue((hold == 10).all())
            self.assertTrue(meta['v279_v278_id_binding'])
            self.assertEqual(
                meta['v279_implementation'], MODULE.V279_IMPLEMENTATION
            )
            self.assertFalse(meta['volume_shuffle_uses_future_labels'])

    def test_candidate_baseline_and_negative_control_remain_distinct(self):
        frame = self.frame()
        experiment_id = 'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1H'
        candidate, _, _ = MODULE.strategy_signal(
            frame, self.config(experiment_id, 'BTCUSDT')
        )
        baseline, _, _ = MODULE.strategy_signal(
            frame, self.config(experiment_id, 'BTCUSDT', 'BASELINE')
        )
        negative, _, _ = MODULE.strategy_signal(
            frame, self.config(experiment_id, 'BTCUSDT', 'NEGATIVE_CONTROL')
        )
        expected = np.sign(frame['close'].pct_change(40)).fillna(0.0)
        pd.testing.assert_series_equal(baseline, expected.astype(float))
        self.assertFalse(candidate.equals(baseline))
        self.assertFalse(candidate.equals(negative))

    def test_negative_control_is_deterministic_and_prefix_invariant(self):
        frame = self.frame()
        experiment_id = 'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1H'
        config = self.config(experiment_id, 'BTCUSDT', 'NEGATIVE_CONTROL')
        first, _, _ = MODULE.strategy_signal(frame, config)
        second, _, _ = MODULE.strategy_signal(frame, config)
        pd.testing.assert_series_equal(first, second)
        prefix, _, _ = MODULE.strategy_signal(frame.iloc[:300].copy(), config)
        pd.testing.assert_series_equal(first.iloc[:300], prefix)

    def test_v268_identity_still_delegates_to_sealed_base(self):
        frame = self.frame()
        config = self.config(
            'TDH-SCOUT-000001-VTM-VOL80-NODOGE-1H', 'BTCUSDT'
        )
        _, _, meta = MODULE.strategy_signal(frame, config)
        self.assertTrue(meta['v268_family'])
        self.assertNotIn('v279_v278_id_binding', meta)

    def test_runtime_failure_reproduction_no_longer_uses_legacy_param_name(self):
        frame = self.frame()
        config = self.config(
            'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1H', 'ETHUSDT'
        )
        self.assertIn('volume_rank_lookback', config['params'])
        self.assertNotIn('volume_lookback', config['params'])
        signal, _, meta = MODULE.strategy_signal(frame, config)
        self.assertEqual(len(signal), len(frame))
        self.assertTrue(meta['v279_v278_id_binding'])

    def test_simulation_chain_uses_new_binding_instead_of_legacy_fallback(self):
        frame = self.frame()
        config = self.config(
            'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1H', 'BTCUSDT'
        )
        metrics = MODULE.simulate(
            frame, config, frame.index[100], frame.index[350], 1.0
        )
        self.assertIsInstance(metrics, dict)
        self.assertIn('trade_count', metrics)

    def test_offline_safety_and_s1_scope_are_unchanged(self):
        status = MODULE.kernel.v278_registry_status()
        self.assertTrue(status['controller_only_promotion'])
        self.assertTrue(status['s1_only'])
        self.assertFalse(status['raw_proposal_executed'])
        self.assertFalse(status['trading_actions'])
        self.assertFalse(status['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()
