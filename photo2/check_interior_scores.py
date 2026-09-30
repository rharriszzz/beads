"""Independent POV ownership checks at the positive photo interior pixels."""
import json
from pathlib import Path
import numpy as np
from check_placement import ROOT,sha
from check_curved_patch import render
from curved_surface_fit import trace
from score_interior_poses import photo_samples


def main():
    review=ROOT/'photo2/review/r159'
    report=json.loads((review/'report.json').read_text())
    loops=json.loads((ROOT/'photo2/review/r157/report.json').read_text())
    fits=json.loads((ROOT/'photo2/review/r156/report.json').read_text())
    samples=photo_samples(loops)
    xy=np.concatenate([v['core'] for v in samples.values()]).astype(int)
    lo=xy.min(axis=0)-2;hi=xy.max(axis=0)+3
    crop=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])]
    checks=[];witnesses=[]
    chosen=[(4,0),(4,1),(4,2),(7,0),(8,2),(11,0),(11,1),(12,1),(15,0)]
    for case_index,rank in chosen:
        c=next(v for v in report['cases'] if (v['case_index'],v['retained_index'])==(case_index,rank))
        p=np.array(c['parameters']);mapping=fits['mappings'][c['family']]
        actual,provenance=render(p,c['hand'],crop,ROOT/'photo2/output/r159/checks',
            f'core-{case_index}-{rank}',c['focal'])
        owner,_,unfinished,_=trace(p,xy,c['hand'],focal=c['focal'])
        pov=actual[xy[:,1]-crop[1],xy[:,0]-crop[0]]
        disagreement=int(np.sum(owner!=pov))
        assert disagreement==0,(case_index,rank,disagreement)
        beads=[]
        for n,sample in samples.items():
            q=sample['core'].astype(int)
            ids=actual[q[:,1]-crop[1],q[:,0]-crop[0]]
            passed=int(np.sum(ids==mapping[n-1]))
            old=next(b for b in c['beads'] if b['number']==n)['core']['passed']
            assert passed==old,(case_index,rank,n,passed,old)
            beads.append(dict(number=n,passed=passed,total=len(q)))
        checks.append(dict(case_index=case_index,retained_index=rank,pixels=len(xy),
            python_pov_disagreements=disagreement,unfinished_ray_pairs=unfinished,
            beads=beads,**provenance))
        if case_index==4:
            for metric in c['beads']:
                if not metric['route']['missed_xy']:continue
                point=np.array(metric['route']['missed_xy'][0]);n=metric['number']
                labels,pr=render(p,c['hand'],[*point,*(point+1)],ROOT/'photo2/output/r159/checks',
                    f'route-{rank}-{n}',c['focal'])
                python,_,u,_=trace(p,point[None,:],c['hand'],focal=c['focal'])
                assert labels[0,0]==python[0],(rank,n,labels[0,0],python[0])
                witnesses.append(dict(case_index=case_index,retained_index=rank,number=n,
                    point=point.tolist(),expected=mapping[n-1],python_owner=int(python[0]),
                    pov_owner=int(labels[0,0]),unfinished_ray_pairs=u,**pr))
    result=dict(score_report_sha256=sha(review/'report.json'),checker_sha256=sha(Path(__file__)),
        pov_checker_sha256=sha(ROOT/'photo2/check_curved_patch.py'),
        checks=checks,exact_fractional_miss_witnesses=witnesses,
        meaning='Verifies model ownership only; does not validate photo loops or accept a family')
    (review/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(core_render_checks=len(checks),pixels_per_check=len(xy),
        total_disagreements=sum(v['python_pov_disagreements'] for v in checks),
        exact_fractional_witnesses=len(witnesses)),indent=2))


if __name__=='__main__':main()
