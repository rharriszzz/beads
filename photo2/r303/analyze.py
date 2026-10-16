"""Descriptive comparisons of sealed models; no post-comparison selection."""
import numpy as np
from .core import *

def main():
    rows=read(BASE/'results/analysis.json')['rows'];groups=[]
    for stage in ['transfer','joint']:
        for mode in MODES:
            for hand in [-1,1]:
                selected=[r for r in rows if r['mode']==mode and r['hand']==hand and (r['stage']==stage or (stage=='transfer' and r['stage']=='S1'))]
                complete=len(selected)==3 and all(not r.get('rejected') for r in selected)
                if not complete:groups.append(dict(stage=stage,mode=mode,hand=hand,complete=False));continue
                groups.append(dict(stage=stage,mode=mode,hand=hand,complete=True,c=selected[0]['c'],train_matched=sum(r['train_matched'] for r in selected),held_matched=sum(r['held_matched'] for r in selected),all_training_checks_pass=all(not r['flags'] for r in selected),train_rms=float(np.sqrt(np.mean([r['train_rms']**2 for r in selected]))),held_rms=float(np.sqrt(np.mean([r['held_rms']**2 for r in selected]))),mean_omission=float(np.mean([r['omission'] for r in selected])),mean_paper=float(np.mean([r['paper'] for r in selected])),mean_held_omission=float(np.mean([r['held_omission'] for r in selected])),mean_held_paper=float(np.mean([r['held_paper'] for r in selected])),flags={r['section']:r['flags'] for r in selected}))
    sensitivity={}
    for kind in ['starts','final']:
        path=BASE/f'results/sensitivity-{kind}.json.gz'
        if not path.exists():continue
        sensitivity[kind]=[]
        for name,r in read(path).items():
            J=np.array(r['jacobian'],float);finite=np.all(np.isfinite(J),axis=1);A=np.nan_to_num(J[finite]);norm=np.linalg.norm(A,axis=0);C=A.T@A/np.maximum(norm[:,None]*norm[None,:],1e-15)
            pairs=sorted([(abs(C[a,b]),a,b) for a in range(len(norm)) for b in range(a+1,len(norm))],reverse=True)[:5]
            names=[('c' if i==4 and 'independent' not in name else NAMES[i]) for i in r['active']]
            sensitivity[kind].append(dict(name=name,certified_base=r['base_physical']['certified'],finite_rows=r['finite_rows'],directions_above_scale=r['resolved_scale_directions'],singular_values=r['singular_values'],contour_owner_alternatives=sorted(set(tuple(x['contour_owners']) for x in r['perturbations'])),uncertified_perturbations=sum(not x['physical']['certified'] for x in r['perturbations']),coupled_pairs=[dict(a=names[a],b=names[b],cosine=float(C[a,b])) for _,a,b in pairs]))
    # Components are compared separately. A better reflection score is never a
    # Pareto geometric improvement if any available contradiction metric worsens.
    comparisons=[]
    metrics=['extent_mae','boundary_mae','envelope_mae','paper','omission','held_paper','held_omission','valley_mae']
    for r in rows:
        if r.get('rejected') or r['mode']=='independent':continue
        b=next((b for b in rows if b['stage']==r['stage'] and b['section']==r['section'] and b['hand']==r['hand'] and b['mode']=='independent'),None)
        if b is None or b.get('rejected'):continue
        delta={k:r[k]-b[k] for k in metrics if r.get(k) is not None and b.get(k) is not None}
        comparisons.append(dict(name=r['name'],baseline=b['name'],deltas=delta,no_worse_all_geometry=all(d<=1e-9 for d in delta.values()),reflection_train_delta=r['train_rms']-b['train_rms'],reflection_held_delta=r['held_rms']-b['held_rms']))
    save(BASE/'results/interpretation.json',dict(groups=groups,sensitivity=sensitivity,component_comparisons=comparisons,warning='Descriptive local sensitivities and retrospective comparisons; no calibrated rank, confidence interval or global optimization claim. Free c does not remove a parameter.'))
    for g in groups:print(g)

if __name__=='__main__':main()
