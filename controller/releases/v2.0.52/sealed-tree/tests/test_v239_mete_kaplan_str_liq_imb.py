from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTROLLER=ROOT/'strategy_lab_controller.py'
ADAPTER=ROOT/'adapter'/'tdh_strategy_lab_research_adapter.py'
SEEDS=ROOT/'research'/'mete-kaplan-seeds-v1.jsonl'
SOURCE=ROOT/'research'/'TDH_Mete_Kaplan_STR_LIQ_IMB_Research_Pack_v1.md'
PHOENIX=Path('/srv/tdh-research/phoenix-venv/bin/python')


def load_controller():
    spec=importlib.util.spec_from_file_location('tdh_v239_mk_test',CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module


class V239MeteKaplanTests(unittest.TestCase):
    def test_registry_has_three_families_and_twelve_5m_seeds(self):
        m=load_controller(); families,experiments=m.kernel.registry()
        self.assertTrue(m.kernel.METE_EXECUTABLE_FAMILIES <= set(families))
        rows=[r for r in experiments.values() if r.get('family_id') in m.kernel.METE_EXECUTABLE_FAMILIES]
        self.assertEqual(len(rows),12)
        self.assertEqual({r['effective_timeframe'] for r in rows},{'5m'})
        self.assertEqual({r['family_id'] for r in rows},{'MK_A_LIQ_IMB','MK_B_STR_IMB','MK_C_STR_LIQ_IMB'})
        self.assertEqual({tuple(r['universe']) for r in rows},{('BTCUSDT','ETHUSDT','SOLUSDT')})
        self.assertEqual({r['params']['profile'] for r in rows},{'BASE','LOOSE','STRICT','CONFIRM'})

    def test_mete_status_is_explicit_about_blocked_layers(self):
        m=load_controller(); status=m.kernel.mete_registry_status()
        self.assertEqual(status['status'],'ACTIVE_EXECUTABLE_CORE_ABC_5M')
        self.assertEqual(status['executable_seed_count'],12)
        self.assertIn('1m',status['blocked'])
        self.assertIn('MK_D_MTF_BIAS',status['blocked'])
        self.assertIn('MK_F_MAGIC_ALIGNMENT',status['blocked'])

    def test_config_is_fail_closed_outside_registered_symbol_or_timeframe(self):
        m=load_controller(); _,experiments=m.kernel.registry(); row=experiments['MK-C-5M-BASE']
        config=m.kernel.performance_config(row,'BTCUSDT'); self.assertEqual(m.kernel.validate_config(config),config)
        bad=dict(config); bad['symbol']='DOGEUSDT'
        with self.assertRaises(m.kernel.ResearchContractError): m.kernel.validate_config(bad)
        bad=dict(config); bad['timeframe']='15m'
        with self.assertRaises(m.kernel.ResearchContractError): m.kernel.validate_config(bad)

    def test_source_manifest_binds_user_pack_sha(self):
        text=SOURCE.read_text(encoding='utf-8')
        self.assertIn('MK_STR_LIQ_IMB_v1',text)
        self.assertIn('a96aaea3fc5069b6da5e1b87071c7377723c303904e553a40b9cacc8f5d6bab8',text)
        self.assertIn('B0',text)
        self.assertIn('blocked',text.lower())

    def test_phoenix_adapter_causality_and_symmetry(self):
        script=r'''
import importlib.util,sys,numpy as np,pandas as pd
from pathlib import Path
p=Path(sys.argv[1]); spec=importlib.util.spec_from_file_location('mk_adapter_prop',p); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
rng=np.random.default_rng(73); n=900; idx=pd.date_range('2024-01-01',periods=n,freq='5min',tz='UTC'); ret=rng.normal(0,0.002,n); close=100*np.exp(np.cumsum(ret)); op=np.r_[close[0],close[:-1]]; span=np.maximum(0.05,np.abs(close-op)+rng.uniform(.03,.25,n)); hi=np.maximum(op,close)+span; lo=np.minimum(op,close)-span; vol=rng.uniform(100,1000,n); frame=pd.DataFrame({'open':op,'high':hi,'low':lo,'close':close,'volume':vol},index=idx)
_,ex=m.kernel.registry(); cfg=m.kernel.performance_config(ex['MK-C-5M-LOOSE'],'BTCUSDT'); s1=m.strategy_signal(frame,cfg)[0]
cut=600; changed=frame.copy(); changed.iloc[cut+1:,changed.columns.get_loc('open')]*=1.7; changed.iloc[cut+1:,changed.columns.get_loc('close')]*=1.7; changed.iloc[cut+1:,changed.columns.get_loc('high')]*=1.7; changed.iloc[cut+1:,changed.columns.get_loc('low')]*=1.7; s2=m.strategy_signal(changed,cfg)[0]; assert np.array_equal(s1.iloc[:cut+1].to_numpy(),s2.iloc[:cut+1].to_numpy())
M=1000.0; mirror=frame.copy(); mirror['open']=M-frame['open']; mirror['close']=M-frame['close']; mirror['high']=M-frame['low']; mirror['low']=M-frame['high']; sm=m.strategy_signal(mirror,cfg)[0]; assert np.array_equal(s1.to_numpy(),-sm.to_numpy())
print('MK_CAUSAL_SYMMETRY_OK',int((s1!=0).sum()))
'''
        done=subprocess.run([str(PHOENIX),'-c',script,str(ADAPTER)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120,check=False)
        self.assertEqual(done.returncode,0,done.stdout); self.assertIn('MK_CAUSAL_SYMMETRY_OK',done.stdout)

    def test_mete_accounting_uses_quarter_percent_current_equity(self):
        script=r'''
import importlib.util,sys,pandas as pd
from pathlib import Path
p=Path(sys.argv[1]); spec=importlib.util.spec_from_file_location('mk_adapter_metrics',p); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
start=pd.Timestamp('2024-01-01',tz='UTC'); end=pd.Timestamp('2024-04-01',tz='UTC'); metrics=m._mk_metrics([{'pnl_r':2.0},{'pnl_r':-1.0},{'pnl_r':2.0}],start,end)
assert metrics['risk_fraction_current_equity']==0.0025
assert metrics['mk_risk_per_trade_pct']==0.25
assert metrics['accounting_basis']==m.base.RUNTIME_ACCOUNTING_BASIS
assert metrics['final_capital']>=0 and 0<=metrics['max_drawdown_pct']<=100
print('MK_ACCOUNTING_OK')
'''
        done=subprocess.run([str(PHOENIX),'-c',script,str(ADAPTER)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120,check=False)
        self.assertEqual(done.returncode,0,done.stdout); self.assertIn('MK_ACCOUNTING_OK',done.stdout)

    def test_mk_phase1_cannot_promote_even_if_global_metrics_pass(self):
        m=load_controller(); passing={'trade_count':400,'net_win_rate':.55,'realized_payoff_ratio':2.2,'max_drawdown_pct':5.0,'expectancy_r':.2,'profit_factor':1.4,'weekday_trades':1.5,'simultaneous_positions_max':1}
        integrity={key:True for key in m.INTEGRITY_GATES}; integrity.update({'baseline_beaten':True,'negative_control_beaten':True,'mk_implementation':'MK_CORE_ABC_5M_CAUSAL_V1','mk_min_trades_300':True,'mk_full_pack_s1_eligible':False})
        folds=[{'metrics':dict(passing),'gates':{'baseline_beaten':True,'negative_control_beaten':True}} for _ in range(4)]
        result={'classification':'PERFORMANCE','metrics':passing,'gates':integrity,'fold_results':folds}
        self.assertEqual(m.authoritative_s1_verdict(result),'PASS')
        self.assertEqual(m.Controller.compute_gate_verdict(None,'S1',result),'FAIL')

    def test_authoritative_global_s1_identity_is_unchanged(self):
        m=load_controller(); self.assertIs(m.authoritative_s1_hard_target_pass,m.v224.authoritative_s1_hard_target_pass)

    def test_runtime_binding_points_to_local_release_adapter(self):
        m=load_controller(); task=json.loads((ROOT/'task.json').read_text(encoding='utf-8')); rebound=m.local_backtest_command(task['backtest_command'])
        self.assertEqual(rebound[1],m.LOCAL_ADAPTER)
        self.assertEqual(Path(m.LOCAL_ADAPTER).resolve(),ADAPTER.resolve())


if __name__=='__main__':
    unittest.main()
