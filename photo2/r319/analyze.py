"""Compact all-observation ledgers and explicit failure attribution."""
import csv,json
from collections import Counter
import numpy as np
from .common import *

def main():
    rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];base=read(OUT/'baseline.json.gz');best=read(OUT/'best-full.json.gz');small=read(OUT/'best-small.json.gz');chosen=read(OUT/'small-selection.json')['chosen'];feasible=[r for r in rows if r.get('feasible') and not r.get('missing')];improved=[r for r in feasible if r['emax_px']<base['emax_px']-1e-6];rejected=[r for r in improved if not r.get('acceptance',{}).get('passed')];tested=[r for r in rows if 'predicted_errors' in r['meta']];ledger=[];motions=[];active_parent=base
    for r in rows:
        if r['stage'].endswith('-parent'):active_parent=r
        worst=max(r.get('rows',[]),key=lambda z:z['error_px'] or -1,default={});ledger.append(dict(trial=r['id'],stage=r['stage'],classification=r['classification'],emax=r.get('emax_px'),worst_index=worst.get('index'),accepted=r.get('acceptance',{}).get('passed'),absolute_clear=r.get('acceptance',{}).get('absolute_clear'),failure=r.get('reason') or ';'.join(r.get('acceptance',{}).get('failures',[])),seconds=r['elapsed']))
        if not r.get('feasible'):continue
        parent=rows[r['meta']['parent']] if 'parent' in r['meta'] else active_parent
        for a,b in zip(r['rows'],parent['rows']):
            if a['predicted'] is None:continue
            movement=np.array(a['predicted'])-b['predicted'];peak_delta=np.linalg.norm(np.array(a['predicted_lobe']['peak'])-b['predicted_lobe']['peak']);motions.append(dict(trial=r['id'],parent_trial=parent['id'],stage=r['stage'],id=a['id'],index=a['index'],observed_x=a['observed'][0],observed_y=a['observed'][1],predicted_x=a['predicted'][0],predicted_y=a['predicted'][1],movement_x=movement[0],movement_y=movement[1],error=a['error_px'],error_change=a['error_px']-b['error_px'],peak_shift=peak_delta,principal_area=a['predicted_lobe']['area'],secondary_components=len(a['predicted_lobe']['secondary_components']),large_peak_jump_diagnostic=peak_delta>5,predicted_error=r['meta'].get('predicted_errors',[None]*22)[r['rows'].index(a)]))
    for name,values in [('trial-ledger.csv',ledger),('all-reflection-responses.csv',motions)]:
        with (OUT/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(values[0]),lineterminator="\n");w.writeheader();w.writerows(values)
    a=read(OUT/'bilateral-sensitivity.json.gz');x=read(OUT/'wide-secant-minimax.json.gz');J=np.array(x['jacobian']);C=J.reshape(-1,J.shape[2]);norm=np.linalg.norm(C,axis=0);cos=C.T@C/np.outer(norm,norm);pairs=[]
    for i in range(len(norm)):
        for j in range(i+1,len(norm)):
            if abs(cos[i,j])>.97:pairs.append(dict(a=x['variables'][i]['key'],b=x['variables'][j]['key'],cosine=float(cos[i,j])))
    pairs.sort(key=lambda r:-abs(r['cosine']));res=positions(base)-np.array([r['observed'] for r in base['rows']]);slopes=np.einsum('ij,ijk->ik',res/np.linalg.norm(res,axis=1)[:,None],J);worst=[next(i for i,r in enumerate(base['rows']) if r['index']==idx) for idx in [58,65,38,33]]
    four=[dict(variable=v['key'],scale=v['scale'],error_slopes={str(base['rows'][i]['index']):float(slopes[i,j]) for i in worst}) for j,v in enumerate(x['variables'])]
    with (OUT/'worst-four-sensitivities.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['parameter','scale','58','65','38','33'])
        for r in four:w.writerow([str(r['variable']),r['scale'],*[r['error_slopes'][str(i)] for i in [58,65,38,33]]])
    # Scalar linear target feasibility records with actual outcomes, no certified
    # infeasibility claim inferred from numerical SLSQP status alone.
    steps=[]
    for r in tested:
        pred=np.array(r['meta']['predicted_errors']);sel=r['meta'].get('cohort',list(range(22)));actual=np.array([z['error_px'] for z in r.get('rows',[])],float)
        d=dict(trial=r['id'],stage=r['stage'],parent=r['meta']['parent'],predicted_max=float(pred[sel].max()),actual_max=float(actual[sel].max()) if len(actual)==22 and not r.get('missing') else None,classification=r['classification'],reason=r.get('reason'),acceptance=r.get('acceptance'),maximum_error_prediction_mismatch=float(abs(actual-pred).max()) if len(actual)==22 and not r.get('missing') else None)
        steps.append(d)
    save(OUT/'step-comparison.json',steps)
    # Frozen response columns, full residual projections, and numerical rank.
    U,S,V=np.linalg.svd(C,full_matrices=False);projections=[]
    for cutoff in [.1,.03,.01,.003]:
        mask=S>S[0]*cutoff;remaining=res.ravel()-U[:,mask]@(U[:,mask].T@res.ravel());projections.append(dict(relative_cutoff=cutoff,rank=int(mask.sum()),unexplained_residual_norm=float(np.linalg.norm(remaining)),per_observation_unexplained=remaining.reshape(22,2).tolist()))
    sensitivity=dict(count=len(a['records']),unavailable=sum(r['derivative'].startswith('unavailable') for r in a['records']),locally_negligible=sum(r.get('scaled_norm',0)<=.03 for r in a['records'] if 'scaled_norm' in r),smooth_active=sum(r.get('scaled_norm',0)>.03 and r.get('smooth',False) for r in a['records']),nonsmooth_active=sum(r.get('scaled_norm',0)>.03 and not r.get('smooth',False) for r in a['records']),policy='Smooth means relative bilateral and multiscale disagreements both <0.6 at quarter scale. This empirical screen is intentionally exposed; it is not proof of differentiability.')
    summary=dict(utc=utc(),trials=len(rows),feasible=len(feasible),classifications=dict(Counter(r['classification'] for r in rows)),baseline_max=base['emax_px'],best_full_max=best['emax_px'],best_full_trial=best['id'],best_small_trial=small['id'],small_baseline_max=max(base['rows'][i]['error_px'] for i in chosen['cohort']),small_best_max=max(small['rows'][i]['error_px'] for i in chosen['cohort']),small_full22_max=small['emax_px'],small_interval=[chosen['low'],chosen['high']],small_reflections=len(chosen['cohort']),improved_reflection_trials=len(improved),improved_but_geometry_rejected=len(rejected),rejection_reasons=dict(Counter(k for r in rejected for k in r['acceptance']['failures'])),sensitivity=sensitivity,correlated_pairs=pairs,svd_projections=projections,four_worst_slopes=four,physical_violations=dict(Counter(r['classification'] for r in tested)),no_local_optimum_certificate=True,median_feasible_seconds=float(np.median([r['elapsed'] for r in feasible])))
    save(OUT/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['correlated_pairs','svd_projections','four_worst_slopes']},indent=2),flush=True)
if __name__=='__main__':main()
