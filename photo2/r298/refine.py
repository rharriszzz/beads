"""At most 160 physically gated trials; dimensions dominate, no patch reward."""
from .calibrate import *
from .photometry import PhotoScore

def dimension_loss(bd,en,m):
    bi=[i for i,r in enumerate(m['beads']) if r['split']=='development'];ei=[i for i,r in enumerate(m['envelope']) if r['fit_eligible'] and r['split']=='development']
    b=np.array([r['extent_px'] for r in m['beads']]);e=np.array([r['bounds'] for r in m['envelope']])
    # Robust independent components: direct bead width/diameter, transverse width,
    # and common-mode edge residual (axis evidence through forward surfaces).
    br=bd-b;er=en-e
    return float(np.mean(np.minimum((br[bi]/3)**2,9)) + np.mean(np.minimum((np.diff(er[ei],axis=1)/6)**2,9)) + np.mean(np.minimum((np.mean(er[ei],axis=1)/4)**2,9)))

def main():
    data,_=load_evidence();m=measurements();obj=PhotoScore(data);history=[];selected=[];start=monotonic()
    def trial(p,name):
        scene,poly,bd,en=prediction(p,data,m);cert=contact(scene);row=dict(id=len(history),name=name,parameters=p,physical=cert,dimension_loss=dimension_loss(bd,en,m),metrics={s:metrics((bd,en),m,s) for s in ['development','comparison']},beads=bd.tolist(),envelope=en.tolist())
        if cert['certified']:
            photo=obj.assess(scene);row['photographic']=photo
            row['loss']=row['dimension_loss']+2*photo['paper_occupied']+photo['colored_missing']+photo['color_conflict']+.5*photo['separator_error_px']/6+.25*(1-photo['region_containment'])
        else:row['loss']=None
        history.append(row);save(BASE/'results/refinement-history.json.gz',history)
        print(row['id'],name,cert['state'],row['loss'],flush=True);return row
    baseline=read(BASE/'results/baseline.json')['parameters'];trial(baseline,'R297 baseline')
    for ident in [767,121,694,631]:
        p=read(BASE/f'results/roll-{ident}.json.gz')['parameters'];base=trial(p,f'roll-fit {ident}')
        if not base['physical']['certified']:
            # Find the nearest feasible axial limit, retaining every failed test.
            hi=p['axial'];lo=.55;q=deepcopy(p);q['axial']=lo;feasible=trial(q,f'axial-bracket {ident}')
            if not feasible['physical']['certified']:
                p=read(BASE/f'results/physical-{ident}.json.gz')['parameters'];p['axial']=min(p['axial'],.72);base=trial(p,f'no-roll fallback {ident}')
                if not base['physical']['certified']:raise RuntimeError('No certified family start')
            else:
                base=feasible
                for j in range(7):
                    q=deepcopy(p);q['axial']=(lo+hi)/2;r=trial(q,f'axial-feasibility {ident}/{j}')
                    if r['physical']['certified']:lo=q['axial'];base=r
                    else:hi=q['axial']
        # Shared nuisance terms only. Every body remains on the common physical helix.
        for key,steps in [('phase',[-.32,-.16,.16,.32]),('s0',[-3.,-1.5,1.5,3.]),('roll',[-4.,4.]),('axial',[-.025,.025]),('minor',[-.06,.06]),('scale',[-.08,.08])]:
            origin=deepcopy(base['parameters']);best=base
            for step in steps:
                q=deepcopy(origin);q[key]=q.get(key,0.)+step;r=trial(q,f'{ident} {key} {step:+g}')
                if r['loss'] is not None and r['loss']<best['loss']:best=r
            base=best
        # Controlled shared-axis amplitude tests expose dependence on the fitted axis.
        for factor in [0.,.5,1.25]:
            q=deepcopy(base['parameters']);q['axis_nodes']=(np.array(q['axis_nodes'])*factor).tolist();r=trial(q,f'{ident} axis amplitude {factor}')
            if r['loss'] is not None and r['loss']<base['loss']:base=r
        selected.append(base['id']);save(BASE/'results/refinement-progress.json',dict(selected=selected,trials=len(history),elapsed=monotonic()-start))
    assert len(history)<=160
    best=min(selected,key=lambda i:history[i]['loss']);save(BASE/'results/selection.json',dict(primary=best,families=selected,history='refinement-history.json.gz',elapsed=monotonic()-start,limits='Finite retrospective structural calibration; no count or hand proof. No further fitting after this selection.'))
if __name__=='__main__':main()
