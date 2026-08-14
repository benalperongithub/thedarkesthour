from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTROLLER=ROOT/'strategy_lab_controller.py'

def load_controller():
    s=importlib.util.spec_from_file_location('tdh_v241_test',CONTROLLER)
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

def review():
    return {'contract_version':'2.0.2','research_round':1,'policy':{'research_mode':'offline','trading_actions':False,'exchange_api_access':False},'hard_targets':{'net_win_rate_min':.5,'realized_reward_risk_min':2.0,'max_drawdown_pct_max':10.0,'baseline_and_negative_control_must_be_beaten':True},'round_roles':{'mode':'DUAL_POST_S1','controller_owns_promotion':True},'evidence_sha256':'e'*64,'raw_evidence_location':'hash-bound file retained on VPS'}

def packet():
    pos={'memory_version':'tdh-positive-pnl-prompt-v1','verified_current_positive_count':7,'legacy_positive_quarantined_count':27,'top_verified_current_positives':[{'positive_class':'PROMISING_POSITIVE','experiment_id':'P','family':'TSMOM_RETURN_SIGN','symbol':'DOGEUSDT','timeframe':'4h','strategy_config_sha256':'a'*16,'metrics':{'net_pnl':1000,'net_return_pct':5,'trade_count':338,'net_win_rate':.45,'realized_payoff_ratio':1.35,'max_drawdown_pct':7.5,'expectancy_r':.065,'profit_factor':1.23,'weekday_trades':1.25},'controller_verdict':'FAIL'}],'interpretation_contract':{'positive_pnl_is_hypothesis_memory_not_promotion':True,'s1_gate_remains_authoritative':True,'legacy_positive_metrics_are_not_model_financial_evidence':True,'prefer_mechanism_contrasts_over_micro_tuning':True}}
    prior={'source_run_id':'old','source_round':1,'codex_findings':[{'severity':'HIGH','claim':'C'*1200}],'claude_findings':[{'severity':'HIGH','claim':'D'*1200}],'controller_synthesis':{'s1_pass_ids':[],'consensus_ids':[],'next_selection_rule':'N'*1200},'scalping_exploration':{'status':'ACTIVE_EXECUTABLE_5M_15M','one_minute_status':'BLOCKED_NOT_REGISTERED_OR_EXECUTABLE'},'verified_s1':[{'candidate_id':'old','controller_verdict':'FAIL','family':'VOL_REGIME_GATE','experiment_id':'X','timeframe':'1h','metrics':{'expectancy_r':-.06,'profit_factor':.83,'net_win_rate':.41,'realized_payoff_ratio':1.06}}]}
    candidates=[]; evidence=[]
    for i in range(4):
        fam='MK_C_STR_LIQ_IMB' if i<2 else 'MK_A_LIQ_IMB'; cid=f'c{i}'
        cfg={'control_mode':'PERFORMANCE','experiment_id':'MK-C-5M-BASE' if i<2 else 'MK-A-5M-BASE','family':fam,'params':{'profile':'BASE','timeframe':'5m'},'symbol':['SOLUSDT','BTCUSDT','SOLUSDT','ETHUSDT'][i],'timeframe':'5m'}
        candidates.append({'candidate_id':cid,'hypothesis_id':f'h{i}','family':fam,'config':cfg,'primary_change':{'atomic_bundle':True,'component':'strategy_family','from':'VOLUME_TSMOM','to':fam,'rationale':'R'*600},'falsification':'F'*600})
        gates={k:True for k in ('no_leakage','data_integrity','accounting_reconciled','execution_model_compliant','single_position_compliant','costs_included','funding_included','deterministic_rerun')}; gates.update({'baseline_beaten':False,'negative_control_beaten':i<2,'mk_B0_random_timing_control':False,'mk_B1_fvg_only_control':True,'mk_full_pack_s1_eligible':False,'mk_implementation':'MK_CORE_ABC_5M_CAUSAL_V1','mk_min_trades_300':i>=2})
        evidence.append({'candidate_id':cid,'controller_verdict':'FAIL','metrics':{'expectancy_r':-.25,'profit_factor':.66,'net_win_rate':.32,'realized_payoff_ratio':1.35,'max_drawdown_pct':6,'trade_count':230+i*250,'weekday_trades':.8},'gates':gates,'observations':['NEGATIVE_EXPECTANCY'],'delta_vs_baseline':{},'delta_vs_negative_control':{}})
    return {'contract_version':'2.0.2','research_round':1,'verdict':'CONTINUE','candidates':candidates,'s1_evidence':evidence,'controller_batch':{'mode':'DUAL_AGENT_POST_S1_COMPACT','candidate_count':4,'full_s1_result_count':6,'selection_uses_llm':False,'full_raw_evidence_remains_on_vps':True,'positive_pnl_memory':pos,'prior_shared_research_context':prior},'audit_instruction':'A'*1000}

class Tests(unittest.TestCase):
    def test_precheck_headroom_and_preservation(self):
        m=load_controller(); raw=packet(); before=m._json_chars({'review_context':review(),'analysis_packet':raw}); self.assertGreater(before,10000)
        compact,report=m.compact_post_s1_precheck_packet(raw); after=m._json_chars({'review_context':review(),'analysis_packet':compact}); self.assertLessEqual(after,10000); self.assertIn(report['compaction_level'],(1,2)); self.assertTrue(report['limits_unchanged'])
        self.assertEqual(compact['candidates'][0]['config'],raw['candidates'][0]['config']); self.assertEqual(compact['s1_evidence'][0]['metrics'],raw['s1_evidence'][0]['metrics']); g=compact['s1_evidence'][0]['gates']; self.assertFalse(g['baseline_beaten']); self.assertFalse(g['mk_B0_random_timing_control']); self.assertFalse(g['mk_full_pack_s1_eligible'])
        self.assertEqual(compact['controller_batch']['positive_pnl_memory']['memory_version'],'tdh-positive-pnl-prompt-v1')
    def test_both_final_paths_and_limits(self):
        m=load_controller(); compact,r1=m.compact_post_s1_precheck_packet(packet()); again,r2=m.compact_post_s1_precheck_packet(packet()); self.assertEqual(compact,again); self.assertEqual(r1,r2)
        for kind in ('claude_post_s1','codex_post_s1'):
            _,p,rep=m._compact_prompt_inputs(kind,review(),compact); self.assertIsNotNone(p); self.assertLessEqual(rep['final_input_chars'],12000)
        self.assertEqual(m.POST_S1_PRECHECK_HARD_LIMIT,10000); self.assertEqual(m.PROMPT_TARGET_MAX_CHARS,12000); self.assertEqual(m.PROMPT_HARD_CEILING_CHARS,16000); self.assertIs(m.authoritative_s1_hard_target_pass,m.v224.authoritative_s1_hard_target_pass)

if __name__=='__main__': unittest.main()
