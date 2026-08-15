from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError:
    np = None
    pd = None


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'
ADAPTER = ROOT / 'adapter' / 'tdh_strategy_lab_research_adapter.py'
SEEDS = ROOT / 'research' / 'v268-volume-tsmom-ablation-seeds-v1.jsonl'


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NUMERICAL_DEPS_AVAILABLE = np is not None and pd is not None


@unittest.skipUnless(
    NUMERICAL_DEPS_AVAILABLE,
    'v2.0.68 numerical integration tests require the Phoenix environment',
)
class V268VolumeTsmomAblationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = load(ADAPTER, 'tdh_v268_adapter_test')
        cls.kernel = cls.adapter.kernel
        cls.controller = load(CONTROLLER, 'tdh_v268_controller_test')

    def test_exact_three_hash_bound_registered_seeds(self):
        families, experiments = self.kernel.registry()
        self.assertIn('VOLUME_TSMOM', families)
        rows = [
            row for row in experiments.values()
            if row.get('registry_id') == self.kernel.V268_REGISTRY_VERSION
        ]
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row['effective_timeframe'] for row in rows},
            {'1h', '4h', '1d'},
        )
        for row in rows:
            self.assertEqual(
                row['universe'], ['BTCUSDT', 'XRPUSDT', 'SOLUSDT']
            )
            self.assertNotIn('DOGEUSDT', row['universe'])
            admission = row['controller_admission']
            self.assertEqual(
                admission['source_proposal_sha256'],
                self.kernel.V268_SOURCE_PROPOSAL_SHA256,
            )
            self.assertEqual(
                admission['source_decision_sha256'],
                self.kernel.V268_SOURCE_DECISION_SHA256,
            )
            self.assertFalse(admission['raw_proposal_executed'])
            self.assertTrue(admission['controller_only_promotion'])
            self.assertTrue(admission['s1_only'])

    def _config(self, mode: str = 'PERFORMANCE') -> dict:
        _, experiments = self.kernel.registry()
        row = experiments['TDH-SCOUT-000001-VTM-VOL80-NODOGE-1H']
        config = self.kernel.performance_config(row, 'BTCUSDT')
        if mode != 'PERFORMANCE':
            config = self.kernel.control_config(config, mode)
        return config

    @staticmethod
    def _frame(size: int = 420) -> pd.DataFrame:
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

    def test_candidate_baseline_and_causal_shuffle_are_distinct(self):
        frame = self._frame()
        candidate, hold, candidate_meta = self.adapter.strategy_signal(
            frame, self._config('PERFORMANCE')
        )
        baseline, _, _ = self.adapter.strategy_signal(
            frame, self._config('BASELINE')
        )
        negative, _, negative_meta = self.adapter.strategy_signal(
            frame, self._config('NEGATIVE_CONTROL')
        )
        expected = np.sign(frame['close'].pct_change(40)).fillna(0.0)
        pd.testing.assert_series_equal(baseline, expected.astype(float))
        self.assertFalse(candidate.equals(baseline))
        self.assertFalse(candidate.equals(negative))
        self.assertTrue((hold == 10).all())
        self.assertEqual(candidate_meta['entry_timing'], 'next_bar_open')
        self.assertFalse(negative_meta['volume_shuffle_uses_future_labels'])

    def test_negative_control_is_deterministic_and_prefix_invariant(self):
        frame = self._frame()
        config = self._config('NEGATIVE_CONTROL')
        first, _, _ = self.adapter.strategy_signal(frame, config)
        second, _, _ = self.adapter.strategy_signal(frame, config)
        pd.testing.assert_series_equal(first, second)
        prefix, _, _ = self.adapter.strategy_signal(frame.iloc[:300].copy(), config)
        pd.testing.assert_series_equal(first.iloc[:300], prefix)

    def test_low_trade_count_can_never_pass_s1(self):
        original_finalize = self.adapter._BASE_FINALIZE
        self.adapter._BASE_FINALIZE = lambda results, stage: None
        try:
            with tempfile.TemporaryDirectory() as directory:
                artifact = Path(directory)
                (artifact / 'effective_config.json').write_text(
                    json.dumps({
                        'registered_experiment_config': self._config()
                    }),
                    encoding='utf-8',
                )
                results = [{
                    'classification': 'PERFORMANCE',
                    'artifact_path': str(artifact),
                    'metrics': {'trade_count': 29},
                    'gates': {},
                    'status': 'PASS',
                    'failure_reasons': [],
                }]
                self.adapter.finalize_comparisons(results, 'S1')
                row = results[0]
                self.assertEqual(row['status'], 'FAIL')
                self.assertFalse(row['gates']['v268_min_trades_per_symbol_30'])
                self.assertIn('at least 30 trades', row['failure_reasons'][0])
        finally:
            self.adapter._BASE_FINALIZE = original_finalize

    def test_lifecycle_recognizes_exact_source_as_registered(self):
        original_here = self.controller.HERE
        try:
            with tempfile.TemporaryDirectory() as directory:
                release = Path(directory) / 'v2.0.68'
                research = release / 'research'
                research.mkdir(parents=True)
                (research / self.controller.V268_REVIEWED_SEEDS_FILENAME).write_text(
                    SEEDS.read_text(encoding='utf-8'), encoding='utf-8'
                )
                self.controller.HERE = release
                reviewed = self.controller._v265_reviewed_proposal_registry()
                self.assertEqual(
                    reviewed[self.controller.V268_SOURCE_PROPOSAL_SHA256],
                    tuple(sorted(self.kernel.V268_IDENTITIES)),
                )
        finally:
            self.controller.HERE = original_here

    def test_tampered_registry_source_hash_fails_closed(self):
        original_here = self.controller.HERE
        try:
            with tempfile.TemporaryDirectory() as directory:
                release = Path(directory) / 'v2.0.68'
                research = release / 'research'
                research.mkdir(parents=True)
                text = SEEDS.read_text(encoding='utf-8').replace(
                    self.controller.V268_SOURCE_PROPOSAL_SHA256, '0' * 64
                )
                (research / self.controller.V268_REVIEWED_SEEDS_FILENAME).write_text(
                    text, encoding='utf-8'
                )
                self.controller.HERE = release
                with self.assertRaisesRegex(
                    self.controller.LabError, 'registry contract drift'
                ):
                    self.controller._v265_reviewed_proposal_registry()
        finally:
            self.controller.HERE = original_here

    def test_runtime_contract_preserves_offline_s1_boundary(self):
        contract = self.controller.runtime_binding_contract()
        self.assertTrue(contract['v268_source_proposal_hash_bound'])
        self.assertTrue(contract['v268_source_decision_hash_bound'])
        self.assertTrue(
            contract['v268_candidate_baseline_negative_control_bound']
        )
        self.assertTrue(contract['v268_causal_volume_shuffle_only'])
        self.assertTrue(contract['v268_raw_proposal_never_executes'])
        self.assertTrue(contract['v268_s1_only'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()
