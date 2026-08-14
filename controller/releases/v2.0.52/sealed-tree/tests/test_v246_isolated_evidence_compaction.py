from __future__ import annotations
import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def mod():
 s=importlib.util.spec_from_file_location('v246pure',ROOT/'strategy_lab_controller.py'); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

def n(x): return len(json.dumps(x,sort_keys=True,separators=(',',':')))

def data():
 p={'workers':{'cross_coin':{'top_cross_coin_configs':[{'experiment_id':'E1','family':'VOLUME_TSMOM','coins':['DOGEUSDT','XRPUSDT'],'unique_coins':2,'avg_expectancy_r':.05}]},'positive_edge':{'top_hypotheses':[{'experiment_id':'E2','family':'VOLUME_TSMOM','symbol':'DOGEUSDT','timeframe':'6h','expectancy_r':.11,'profit_factor':1.34}]},'s1_forensics':{'dominant_failures':[['PAYOFF_BELOW_TARGET',1600]],'latest_samples':[{'candidate_id':'c1','verdict':'FAIL','expectancy_r':-.12,'pf':.62,'wr':.3,'rr':1.04,'dd':5.9,'baseline':False,'negative':False,'obs':['NEGATIVE_EXPECTANCY']}]},'scalping_mtf':{'status':'ACTIVE_EXECUTABLE_5M_15M'},'memory_curator':{'audit':'X'*5000}}}
 row={'candidate_id':'c1','controller_verdict':'FAIL','strategy_config':{'experiment_id':'OLD','family':'SUPPORT_RES_BREAK','symbol':'BTCUSDT','timeframe':'1h','params':{'x':1},'control_mode':'PERFORMANCE'},'metrics':{'expectancy_r':-.12,'profit_factor':.62,'net_win_rate':.3,'realized_payoff_ratio':1.04,'max_drawdown_pct':5.9,'trade_count':120},'gates':{'baseline_beaten':False,'negative_control_beaten':False},'fold_results':['Y'*5000]}
 c={'latest_s1_financial_evidence':{'source_run_id':'prior','source_round':1,'source_stage':'S1','source_result_sha256':'a'*64,'candidates':[row]},'novelty_frontier':[{'config':{'experiment_id':'NEXT','family':'MA_TREND','symbol':'BTCUSDT','timeframe':'4h','params':{'fast':20},'control_mode':'PERFORMANCE'}}]}
 return c,p

class T(unittest.TestCase):
 def test_shrinks(self):
  m=mod(); c,p=data(); old={'specialists':p,'latest_s1':c['latest_s1_financial_evidence'],'frontier':c['novelty_frontier']}; self.assertGreater(n(old),7000); self.assertLessEqual(n(m.isolated(c,p)),5500)
 def test_raw_removed(self):
  m=mod(); c,p=data(); x=json.dumps(m.isolated(c,p)); self.assertNotIn('memory_curator',x); self.assertNotIn('fold_results',x)
 def test_contract(self):
  m=mod(); self.assertEqual(m.V246_ISOLATED_HARD_CEILING,7000); self.assertIs(m.authoritative_s1_hard_target_pass,m.v224.authoritative_s1_hard_target_pass)
if __name__=='__main__': unittest.main()
