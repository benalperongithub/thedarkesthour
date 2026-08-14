#!/usr/bin/env python3
"""v2.0.39 registry-aware offline adapter with Mete Kaplan core A/B/C signals."""
from __future__ import annotations

# Immutable accounting contract inherited from sealed v2.0.38:
# REFERENCE_INITIAL_CAPITAL_USD = 20_000.0
# ACCOUNTING_BASIS = "REFERENCE_CAPITAL_REPORTING_ONLY"
# "reference_capital_reporting_only": True


import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

BASE = Path('/srv/tdh-collab/controller/strategy-lab-v2/v2.0.38/adapter/tdh_strategy_lab_research_adapter.py')
spec = importlib.util.spec_from_file_location('tdh_adapter_v238_mkbase', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.38 adapter')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

RELEASE_ROOT = Path(__file__).resolve().parents[1]
KERNEL_PATH = RELEASE_ROOT / 'research' / 'research_kernel.py'
kspec = importlib.util.spec_from_file_location('tdh_kernel_v239_adapter', KERNEL_PATH)
if kspec is None or kspec.loader is None:
    raise RuntimeError('cannot load v2.0.39 kernel')
kernel = importlib.util.module_from_spec(kspec)
sys.modules[kspec.name] = kernel
kspec.loader.exec_module(kernel)

for name in dir(base):
    if not name.startswith('__'):
        globals()[name] = getattr(base, name)

MK_FAMILIES = kernel.METE_EXECUTABLE_FAMILIES
MK_RISK_FRACTION = 0.0025
MK_MIN_TRADES = 300
MK_IMPLEMENTATION = 'MK_CORE_ABC_5M_CAUSAL_V1'

PROFILE = {
    'BASE': dict(k=3,bos=.05,disp=1.25,body=.65,loc=.80,sweep=.05,reclaim=1,fvg=.10,mid=True,expiry=24,confirm=False,hold=48,stop_x=2.0),
    'LOOSE': dict(k=2,bos=0.0,disp=1.00,body=.50,loc=.70,sweep=0.0,reclaim=0,fvg=.05,mid=False,expiry=12,confirm=False,hold=48,stop_x=2.0),
    'STRICT': dict(k=5,bos=.10,disp=1.50,body=.65,loc=.80,sweep=.10,reclaim=2,fvg=.20,mid=True,expiry=24,confirm=False,hold=48,stop_x=2.0),
    'CONFIRM': dict(k=3,bos=.05,disp=1.25,body=.65,loc=.80,sweep=.05,reclaim=1,fvg=.10,mid=True,expiry=24,confirm=True,hold=24,stop_x=2.0),
}

_BASE_SIGNAL = base.v221.strategy_signal
_BASE_SIMULATE = base.v221.simulate
_BASE_AGGREGATE = base.v221.aggregate_folds
_BASE_FINALIZE = base.v221.finalize_comparisons
_ORIGINAL_METRICS = base._ORIGINAL_METRICS_FROM_TRADES
_ORIGINAL_AGGREGATE = base._ORIGINAL_AGGREGATE_FOLDS
_CACHE: dict[tuple[int,str,str], tuple[pd.Series,pd.Series,pd.Series,dict[str,Any]]] = {}


def _profile(config: dict[str,Any]) -> dict[str,Any]:
    name = str(config.get('params',{}).get('profile',''))
    if name not in PROFILE:
        raise AdapterError('unknown Mete profile')
    return PROFILE[name]


def _pivot_levels(frame: pd.DataFrame, k: int) -> tuple[pd.Series,pd.Series]:
    high=frame['high']; low=frame['low']
    center_h=high.shift(k); center_l=low.shift(k)
    left_h=high.shift(k+1).rolling(k,min_periods=k).max(); right_h=high.rolling(k,min_periods=k).max()
    left_l=low.shift(k+1).rolling(k,min_periods=k).min(); right_l=low.rolling(k,min_periods=k).min()
    ch=(center_h>left_h)&(center_h>right_h); cl=(center_l<left_l)&(center_l<right_l)
    return center_h.where(ch).ffill().shift(1), center_l.where(cl).ffill().shift(1)


def _mk_arrays(frame: pd.DataFrame, config: dict[str,Any]):
    p=_profile(config); o=frame['open']; h=frame['high']; l=frame['low']; c=frame['close']
    atr=base.v221.true_range(frame).rolling(14,min_periods=14).mean().shift(1)
    last_h,last_l=_pivot_levels(frame,int(p['k']))
    rng=(h-l).replace(0,np.nan); body=(c-o).abs()/rng
    bull_loc=(c-l)/rng; bear_loc=(h-c)/rng
    tr=base.v221.true_range(frame); ratio=tr/atr.replace(0,np.nan)
    disp_up=(c>o)&(ratio>=p['disp'])&(body>=p['body'])&(bull_loc>=p['loc'])
    disp_dn=(c<o)&(ratio>=p['disp'])&(body>=p['body'])&(bear_loc>=p['loc'])
    bos_up=disp_up&(c>last_h+p['bos']*atr); bos_dn=disp_dn&(c<last_l-p['bos']*atr)
    bos_up=bos_up & ~bos_up.shift(1,fill_value=False); bos_dn=bos_dn & ~bos_dn.shift(1,fill_value=False)
    bull_gap=l-h.shift(2); bear_gap=l.shift(2)-h
    fvg_up=(bull_gap>=p['fvg']*atr)&(l>h.shift(2)); fvg_dn=(bear_gap>=p['fvg']*atr)&(h<l.shift(2))
    if p['mid']:
        fvg_up=fvg_up&disp_up.shift(1,fill_value=False); fvg_dn=fvg_dn&disp_dn.shift(1,fill_value=False)
    return p,atr,last_h,last_l,bos_up.fillna(False),bos_dn.fillna(False),fvg_up.fillna(False),fvg_dn.fillna(False)


def _mk_bundle(frame: pd.DataFrame, config: dict[str,Any]):
    key=(id(frame),str(config['family']),str(config['params']['profile']))
    cached=_CACHE.get(key)
    if cached is not None:
        return cached
    p,atr,last_h,last_l,bos_up,bos_dn,fvg_up,fvg_dn=_mk_arrays(frame,config)
    n=len(frame); o=frame['open'].to_numpy(float); h=frame['high'].to_numpy(float); l=frame['low'].to_numpy(float); c=frame['close'].to_numpy(float)
    av=atr.to_numpy(float); lh=last_h.to_numpy(float); ll=last_l.to_numpy(float)
    bu=bos_up.to_numpy(bool); bd=bos_dn.to_numpy(bool); fu=fvg_up.to_numpy(bool); fd=fvg_dn.to_numpy(bool)
    perf=np.zeros(n,float); fvg_only=np.zeros(n,float)
    last_sweep_up=-10**9; last_sweep_dn=-10**9; last_bos_up=-10**9; last_bos_dn=-10**9
    pen_up=None; pen_dn=None; active_up=None; active_dn=None; base_up=None; base_dn=None
    family=config['family']; seq_window=int(p['expiry'])

    def eligible(direction:int, i:int)->bool:
        if family=='MK_A_LIQ_IMB':
            s=last_sweep_up if direction>0 else last_sweep_dn
            return i-s <= min(seq_window, int(p['reclaim'])+6)
        if family=='MK_B_STR_IMB':
            b=last_bos_up if direction>0 else last_bos_dn
            return 0 <= i-b <= 1
        s=last_sweep_up if direction>0 else last_sweep_dn; b=last_bos_up if direction>0 else last_bos_dn
        return s<=b<=i and b-s<=3 and i-b<=1

    for i in range(20,n):
        if math.isfinite(av[i]):
            if math.isfinite(ll[i]) and l[i] <= ll[i]-p['sweep']*av[i]:
                pen_up=(i,ll[i])
            if math.isfinite(lh[i]) and h[i] >= lh[i]+p['sweep']*av[i]:
                pen_dn=(i,lh[i])
            if pen_up and i-pen_up[0] <= int(p['reclaim']) and c[i] >= pen_up[1]:
                last_sweep_up=i; pen_up=None
            elif pen_up and i-pen_up[0] > int(p['reclaim']):
                pen_up=None
            if pen_dn and i-pen_dn[0] <= int(p['reclaim']) and c[i] <= pen_dn[1]:
                last_sweep_dn=i; pen_dn=None
            elif pen_dn and i-pen_dn[0] > int(p['reclaim']):
                pen_dn=None
        if bu[i]: last_bos_up=i; active_dn=None
        if bd[i]: last_bos_dn=i; active_up=None

        for direction,active,name in ((1,active_up,'up'),(-1,active_dn,'dn')):
            if active is None: continue
            created,mid,expiry=active
            if i<=created or i>expiry:
                if name=='up': active_up=None
                else: active_dn=None
                continue
            touched=l[i] <= mid <= h[i]
            confirmed=(c[i]>o[i]) if direction>0 else (c[i]<o[i])
            if touched and (not p['confirm'] or confirmed):
                perf[i]=direction
                if name=='up': active_up=None
                else: active_dn=None

        for direction,active,name in ((1,base_up,'up'),(-1,base_dn,'dn')):
            if active is None: continue
            created,mid,expiry=active
            if i<=created or i>expiry:
                if name=='up': base_up=None
                else: base_dn=None
                continue
            touched=l[i] <= mid <= h[i]; confirmed=(c[i]>o[i]) if direction>0 else (c[i]<o[i])
            if touched and (not p['confirm'] or confirmed):
                fvg_only[i]=direction
                if name=='up': base_up=None
                else: base_dn=None

        if fu[i]:
            mid=(h[i-2]+l[i])/2.0; base_up=(i,mid,i+int(p['expiry']))
            if eligible(1,i): active_up=(i,mid,i+int(p['expiry']))
        if fd[i]:
            mid=(l[i-2]+h[i])/2.0; base_dn=(i,mid,i+int(p['expiry']))
            if eligible(-1,i): active_dn=(i,mid,i+int(p['expiry']))

    idx=frame.index; hold=pd.Series(int(p['hold']),index=idx,dtype=int)
    result=(pd.Series(perf,index=idx),pd.Series(fvg_only,index=idx),hold,{'atr_stop_x':float(p['stop_x']),'mk_implementation':MK_IMPLEMENTATION,'mk_control_baseline':'B1_FVG_ONLY','mk_negative_control':'N1_DIRECTION_INVERSION','mk_B0_status':'BLOCKED_PENDING_FOLD_LOCAL_RANDOMIZER'})
    _CACHE[key]=result
    return result


def strategy_signal(frame: pd.DataFrame, config: dict[str,Any]):
    if config.get('family') not in MK_FAMILIES:
        return _BASE_SIGNAL(frame,config)
    perf,b1,hold,meta=_mk_bundle(frame,config); mode=config['control_mode']
    signal = b1 if mode=='BASELINE' else (-perf if mode=='NEGATIVE_CONTROL' else perf)
    return signal.astype(float),hold.astype(int),dict(meta)


def _mk_metrics(trades,start,end):
    legacy=_ORIGINAL_METRICS(list(trades),start,end); equity=1.0; peak=1.0; maxdd=0.0
    for item in trades:
        factor=1.0+float(item.get('pnl_r',0.0))*MK_RISK_FRACTION
        equity=max(0.0,equity*max(0.0,factor)); peak=max(peak,equity); maxdd=max(maxdd,(peak-equity)/peak if peak>0 else 1.0)
    value=dict(legacy); ret=(equity-1.0)*100.0; count=int(value.get('trade_count',0)); pnl=20000.0*ret/100.0
    value.update({'initial_capital':20000.0,'final_capital':max(0.0,20000.0+pnl),'net_pnl':pnl,'pnl_per_trade':pnl/count if count else 0.0,'net_return_pct':max(-100.0,ret),'max_drawdown_pct':min(100.0,maxdd*100.0),'accounting_currency':'USD','accounting_basis':base.RUNTIME_ACCOUNTING_BASIS,'reference_capital_reporting_only':True,'risk_fraction_current_equity':MK_RISK_FRACTION,'mk_risk_per_trade_pct':0.25,'mk_family':True})
    return value


def simulate(frame,config,start,end,cost_multiplier=1.0):
    if config.get('family') not in MK_FAMILIES:
        return _BASE_SIMULATE(frame,config,start,end,cost_multiplier)
    signal,hold_bars,meta=strategy_signal(frame,config); atr=base.v221.true_range(frame).rolling(14).mean(); index=frame.index
    start_pos=int(index.searchsorted(start,side='left')); end_pos=int(index.searchsorted(end,side='left')); trades=[]; position_end=start_pos
    for sp in range(max(1,start_pos),min(end_pos-1,len(frame)-1)):
        if sp<position_end: continue
        direction=int(np.sign(float(signal.iloc[sp]))); 
        if direction==0: continue
        ep=sp+1; raw_entry=float(frame['open'].iloc[ep]); entry=raw_entry*(1.0+direction*base.v221.SLIPPAGE_RATE*cost_multiplier)
        av=float(atr.iloc[sp]) if math.isfinite(float(atr.iloc[sp])) else raw_entry*base.v221.MIN_STOP_PCT
        sd=max(raw_entry*base.v221.MIN_STOP_PCT,av*float(meta.get('atr_stop_x',2.0))); stop=entry-direction*sd; target=entry+direction*sd*2.0
        xp=min(end_pos-1,ep+max(1,int(hold_bars.iloc[sp]))); reason='TIME'; raw_exit=float(frame['close'].iloc[xp])
        for pos in range(ep,xp+1):
            hi=float(frame['high'].iloc[pos]); lo=float(frame['low'].iloc[pos]); hs=lo<=stop if direction>0 else hi>=stop; ht=hi>=target if direction>0 else lo<=target
            if hs: raw_exit=stop; xp=pos; reason='BOTH_HIT_STOP_FIRST' if ht else 'STOP'; break
            if ht: raw_exit=target; xp=pos; reason='TARGET'; break
        exit_price=raw_exit*(1.0-direction*base.v221.SLIPPAGE_RATE*cost_multiplier); days=(index[xp]-index[ep]).total_seconds()/86400.0
        raw_r=direction*(exit_price-entry)/sd; fee_r=(entry+exit_price)*base.v221.FEE_RATE*cost_multiplier/sd; funding_r=entry*base.v221.FUNDING_DAILY_RATE*days*cost_multiplier/sd
        trades.append({'entry_ts':index[ep].isoformat(),'exit_ts':index[xp].isoformat(),'direction':direction,'pnl_r':raw_r-fee_r-funding_r,'reason':reason,'bars_held':max(1,xp-ep+1)})
        position_end=xp+1
    return _mk_metrics(trades,start,end)


def aggregate_folds(folds):
    if not folds or not all(isinstance(x,dict) and isinstance(x.get('metrics'),dict) and x['metrics'].get('mk_family') for x in folds):
        return _BASE_AGGREGATE(folds)
    value=dict(_ORIGINAL_AGGREGATE(folds)); returns=[float(x['metrics'].get('net_return_pct',0.0)) for x in folds]; dds=[float(x['metrics'].get('max_drawdown_pct',0.0)) for x in folds]
    ret=min(returns) if returns else 0.0; pnl=20000.0*ret/100.0; count=int(value.get('trade_count',0))
    value.update({'initial_capital':20000.0,'final_capital':max(0.0,20000.0+pnl),'net_pnl':pnl,'pnl_per_trade':pnl/count if count else 0.0,'net_return_pct':max(-100.0,ret),'max_drawdown_pct':min(100.0,max(dds) if dds else 0.0),'accounting_currency':'USD','accounting_basis':base.RUNTIME_ACCOUNTING_BASIS,'reference_capital_reporting_only':True,'risk_fraction_current_equity':MK_RISK_FRACTION,'mk_risk_per_trade_pct':0.25,'mk_family':True})
    return value


def finalize_comparisons(results,stage):
    _BASE_FINALIZE(results,stage)
    if stage!='S1': return
    for row in results:
        if row.get('classification')!='PERFORMANCE': continue
        artifact=Path(str(row.get('artifact_path') or '')); cfg={}
        try:
            raw=json.loads((artifact/'effective_config.json').read_text(encoding='utf-8')); cfg=raw.get('registered_experiment_config') if isinstance(raw,dict) else {}
        except Exception: cfg={}
        if isinstance(cfg,dict) and cfg.get('family') in MK_FAMILIES:
            gates=row.setdefault('gates',{}); gates['mk_min_trades_300']=int(row.get('metrics',{}).get('trade_count',0))>=MK_MIN_TRADES; gates['mk_B1_fvg_only_control']=True; gates['mk_B0_random_timing_control']=False; gates['mk_full_pack_s1_eligible']=False; gates['mk_implementation']=MK_IMPLEMENTATION
            if row.get('status')=='PASS' or not gates['mk_min_trades_300']:
                row['status']='FAIL'; row['controller_verdict']='FAIL'; row['failure_reasons']=['MK pack phase-1 core is not full-S1 eligible; B0 and later confirmation gates remain pending']

base.v221.validate_config=kernel.validate_config
base.v221.control_config=kernel.control_config
base.v221.canonical_hash=kernel.canonical_hash
base.v221.ResearchContractError=kernel.ResearchContractError
base.v221.strategy_signal=strategy_signal
base.v221.simulate=simulate
base.v221.aggregate_folds=aggregate_folds
base.v221.finalize_comparisons=finalize_comparisons

validate_config=kernel.validate_config
control_config=kernel.control_config
write_object=base.write_object
sha256_file=base.sha256_file
run_experiment=base.v221.run_experiment
validate_request=base.v221.validate_request


def main():
    return base.v221.main()

if __name__=='__main__':
    raise SystemExit(main())
