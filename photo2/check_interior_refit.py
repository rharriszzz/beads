"""Independent ownership and whole-held-group isolation checks for R160."""
import json
from pathlib import Path
import numpy as np
from check_placement import ROOT,sha
from check_curved_patch import render
from curved_surface_fit import trace
from fit_curved_patch import load,setup,NUMBERS,HELD
from refit_interior_poses import training_data,residual
from score_interior_poses import photo_samples,synthetic_samples


def isolation(report,samples):
    xy,_=load();changed=xy.copy()
    changed[[n-1 for n in HELD]] += np.array([98765.,-65432.])
    counts=[]
    for family in ['A','B']:
        mapping=np.array(report['mappings'][family])
        old=setup(xy,mapping,NUMBERS);new=setup(changed,mapping,NUMBERS)
        assert all(np.array_equal(a,b) for a,b in zip(old,new))
        c=next(c for c in report['cases'] if c['case_index']==(4 if family=='A' else 7))
        for coarse in [False,True]:
            groups=training_data(xy,NUMBERS,samples,coarse)
            other=training_data(changed,NUMBERS,samples,coarse)
            for a,b in zip(groups,other):
                assert a['kind']==b['kind'] and a['weight']==b['weight']
                assert np.array_equal(a['xy'],b['xy'])
                assert np.array_equal(a['numbers'],b['numbers'])
                assert not set(a['numbers']).intersection(HELD)
            a=residual(c['parameters'],groups,mapping,c['hand'],c['focal'])
            b=residual(c['parameters'],other,mapping,c['hand'],c['focal'])
            assert np.array_equal(a,b)
            counts.append(dict(family=family,coarse=coarse,samples=len(a),
                changed_heldout_locations_leave_bounds_training_and_loss_identical=True))
    return counts


def main():
    out=ROOT/'photo2/review/r160'
    path=ROOT/'photo2/output/r160/full-refits.json'
    if not path.exists():path=out/'report.json'
    report=json.loads(path.read_text())
    assert len(report['cases'])==26,'Wait for the bounded refits to finish'
    loops=json.loads((ROOT/'photo2/review/r157/report.json').read_text())
    photo=photo_samples(loops)
    old=json.loads((ROOT/'photo2/review/r156/report.json').read_text())
    synth,truth=synthetic_samples(old,ROOT/'photo2/output/r160/checks/truth')
    checks=[];fractional=[];marks=[]
    # Training loss alone chooses the displayed start; held-out marks never rank.
    chosen=[]
    for index in [0,3,4,7,8,11,12,15]:
        choices=[c for c in report['cases'] if c['case_index']==index]
        chosen.append(min(choices,key=lambda c:(c['guide_loss'],c['start_rank'])))
    # Also verify both retained baseline A alternatives, without held-out selection.
    chosen.extend(next(c for c in report['cases'] if (c['case_index'],c['start_rank'])==(4,r)) for r in [1,2])
    for c in chosen:
        samples=photo if c['dataset']=='photo' else synth
        xy=np.concatenate([v['core'] for v in samples.values()]).astype(int)
        lo=xy.min(axis=0)-2;hi=xy.max(axis=0)+3
        crop=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])]
        key=f"{c['case_index']}-{c['start_rank']}"
        p=np.array(c['parameters']);mapping=report['mappings'][c['family']]
        labels,pr=render(p,c['hand'],crop,ROOT/'photo2/output/r160/checks',f'core-{key}',c['focal'])
        owner,_,unfinished,_=trace(p,xy,c['hand'],focal=c['focal'])
        pov=labels[xy[:,1]-crop[1],xy[:,0]-crop[0]]
        assert np.array_equal(owner,pov),(key,int(np.sum(owner!=pov)))
        beads=[]
        for n,s in samples.items():
            q=s['core'].astype(int);passed=int(np.sum(labels[q[:,1]-crop[1],q[:,0]-crop[0]]==mapping[n-1]))
            expected=next(b for b in c['after']['interiors']['beads'] if b['number']==n)['core']['passed']
            assert passed==expected,(key,n,passed,expected)
            beads.append(dict(number=n,total=len(q),passed=passed))
            # Exact noninteger rays, including a miss witness if this route has one.
            metric=next(b for b in c['after']['interiors']['beads'] if b['number']==n)['route']
            point=np.array(metric['missed_xy'][0]) if metric['missed_xy'] else s['route'][len(s['route'])//3]
            one,prov=render(p,c['hand'],[*point,*(point+1)],ROOT/'photo2/output/r160/checks',f'route-{key}-{n}',c['focal'])
            py,_,u,_=trace(p,point[None,:],c['hand'],focal=c['focal'])
            assert one[0,0]==py[0],(key,n,one[0,0],py[0])
            fractional.append(dict(case_index=c['case_index'],start_rank=c['start_rank'],number=n,
                point=point.tolist(),expected=mapping[n-1],python_owner=int(py[0]),pov_owner=int(one[0,0]),
                unfinished_ray_pairs=u,**prov))
        checks.append(dict(case_index=c['case_index'],start_rank=c['start_rank'],
            dataset=c['dataset'],pixels=len(xy),python_pov_disagreements=0,
            unfinished_ray_pairs=unfinished,beads=beads,**pr))
        points=load()[0] if c['dataset']=='photo' else np.array(old['synthetic_truth']['points'])
        numbers=NUMBERS if c['dataset']=='photo' else np.array(old['synthetic_truth']['numbers'])
        for n,point in zip(numbers,points):
            one,prov=render(p,c['hand'],[*point,*(point+1)],ROOT/'photo2/output/r160/checks',f'mark-{key}-{n}',c['focal'])
            py,_,u,_=trace(p,point[None,:],c['hand'],focal=c['focal'])
            assert one[0,0]==py[0],(key,int(n),one[0,0],py[0])
            marks.append(dict(case_index=c['case_index'],start_rank=c['start_rank'],number=int(n),
                role='held-out' if n in HELD else 'training',point=point.tolist(),expected=mapping[n-1],
                python_owner=int(py[0]),pov_owner=int(one[0,0]),unfinished_ray_pairs=u,**prov))
    result=dict(full_refits_sha256=sha(path),checker_sha256=sha(Path(__file__)),
        pov_checker_sha256=sha(ROOT/'photo2/check_curved_patch.py'),
        source_sha256=sha(ROOT/'beads.pov'),synthetic_truth=truth,
        heldout_isolation=isolation(report,photo),checks=checks,fractional_checks=fractional,mark_checks=marks,
        meaning='Independent model ownership and training isolation; no uniqueness, boundary, outward-anchor or automatic-detector validation')
    (out/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(render_checks=len(checks),core_pixels=sum(c['pixels'] for c in checks),
        disagreements=0,exact_fractional_checks=len(fractional),exact_mark_checks=len(marks),heldout_isolation=len(result['heldout_isolation'])),indent=2))


if __name__=='__main__':main()
