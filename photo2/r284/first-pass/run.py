"""Run only bounded photographic cases; no replacement whole-photo inventory."""
import argparse,copy
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from photo2.r282.common import ROOT,photo,read,save,sha,pixels,support
from photo2.r282.phase1 import image_features
from photo2.r283.coverage import relationships
from .methods import cues,infer,cut_features,PARAMETERS

OLD=ROOT/'photo2/r283/results'
OUT=ROOT/'photo2/r284/results'


def choose_cases(rows):
    by={r['record_id']:r for r in rows};coverage=read(OLD/'coverage.json');pairs=read(OLD/'ownership.json')['pairs']
    named=[('two-sided',coverage['flanking_pairs'][0]['ids'],'User: remove bottom cyan spike; include left red crossing and right yellow.'),
        ('duplicate',max((p for p in pairs if p['relation']=='shared-dark-envelope-alternative'),key=lambda p:p['broad_dark_envelope_overlap'])['ids'],'User: upper black reflection good, lower secondary. Compare the red right of upper black.'),
        ('abstention',max((p for p in pairs if p['relation']=='shared-material-conflict'),key=lambda p:p['shared_pixels'])['ids'],'User: magenta outline very wrong; redesign native support.')]
    cases=[]
    def add(name,ids,rule):
        center=np.mean([by[k]['measured_photo_location'] for k in ids],axis=0)
        cases.append(dict(name=name,center=center.tolist(),origin=np.rint(center-64).astype(int).tolist(),size=128,selection_ids=ids,selection_rule=rule))
    for n,ids,rule in named:add(n,ids,rule)
    def separated(center):return all(np.linalg.norm(np.array(center)-c['center'])>180 for c in cases)
    for color in ('red','yellow','black'):
        pool=[r for r in rows if r['status']=='high' and r['color']==color and r['centerline']['near'] and (color=='black' or r['centerline']['crosses']) and separated(r['measured_photo_location'])]
        chosen=max(pool,key=lambda r:(r['metrics']['solidity']*min(r['metrics']['area'],400),r['record_id']))
        add('auto-'+color,[chosen['record_id']],f'Highest solidity × min(area,400) R283 high {color} '+('near support' if color=='black' else 'crossing support')+'; >180px from earlier cases. This selects established cues, not blind recall ground truth.')
    flank=next(p for p in coverage['flanking_pairs'] if separated(np.mean([by[k]['measured_photo_location'] for k in p['ids']],axis=0)))
    add('auto-opposite',flank['ids'],'First saved R283 disjoint opposite-side near pair >180px from earlier cases, stable saved order.')
    high=[r for r in rows if r['status']=='high' and r['centerline']['near']]
    groups=[]
    for r in high:
        if not separated(r['measured_photo_location']):continue
        rr=[q for q in high if abs(q['centerline']['arc_px']-r['centerline']['arc_px'])<=16 and np.linalg.norm(np.array(q['measured_photo_location'])-r['measured_photo_location'])<65]
        if len(rr)==3:
            sides={q['centerline']['side'] for q in rr}
            groups.append((len(sides),sum(q['metrics']['area'] for q in rr),r['record_id'],rr))
    group=max(groups,key=lambda x:x[:3])[-1]
    add('auto-three',[r['record_id'] for r in group],'Exactly three R283 high support-near IDs within ±16px arc and 65px Euclidean; maximize side diversity, then support area; >180px from earlier cases. Three candidates, not verified bodies.')
    return cases


def shift_rows(rows,offset):
    out=copy.deepcopy(rows);offset=np.array(offset)
    for r in out:
        r['seed']=(np.array(r['seed'])+offset).tolist()
        for field in ('measured_support','reflection_support'):
            if field in r:r[field]=support(pixels(r[field])+offset)
        r['measured_photo_location']=r['measured_support']['centroid'] if r['measured_support'] else None
    return out


def in_case(r,case):
    p=np.array(r['measured_photo_location'] or r['seed'])-case['origin']
    return bool(np.all(p>=0) and np.all(p<case['size']))


def summary(rows,pairs):
    selected=[r for r in rows if r['status']=='high'];near=[r for r in selected if r['centerline']['near']]
    flanks=[];triples=[]
    for i,a in enumerate(near):
        for b in near[i+1:]:
            if abs(a['centerline']['arc_px']-b['centerline']['arc_px'])<=16 and {a['centerline']['side'],b['centerline']['side']}=={'negative','positive'}:
                flanks.append([a['record_id'],b['record_id']])
        at=[r['record_id'] for r in near if abs(r['centerline']['arc_px']-a['centerline']['arc_px'])<=16]
        if len(at)>=3:triples.append(sorted(at))
    return dict(status=dict(Counter(r['status'] for r in rows)),high_near=len(near),high_crossing=sum(r['centerline']['crosses'] for r in selected),
        high_by_color=dict(Counter(r['color'] for r in selected)),near_by_color=dict(Counter(r['color'] for r in near)),
        near_sides=dict(Counter(r['centerline']['side'] for r in near)),
        candidate_flanking_pairs=flanks,three_or_more_windows=[list(t) for t in sorted(set(map(tuple,triples)))],
        overlap_pairs=sum(p['kind']=='overlapping-support' for p in pairs),secondary_pairs=sum(p['kind']=='possible-secondary' for p in pairs),
        nonempty_components=dict(Counter(str(r['metrics']['components']) for r in rows if r['measured_support'])),
        high_mean_thin_fraction=float(np.mean([r['metrics'].get('thin_fraction',0) for r in selected])) if selected else None,
        high_mean_solidity=float(np.mean([r['metrics']['solidity'] for r in selected])) if selected else None,
        real_distinct_body_count=None,real_leaks=None,real_recall=None,
        warning='Counts of algorithmic candidate supports, not verified distinct real beads. Full silhouette crossing can be missed by interior-only crossing.')


def main(out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    native,rgb,meta=photo();features=image_features(rgb);baseline=read(OLD/'phase1.json.gz')['records'];curve=read(ROOT/'photo2/r282/results/centerline.json')['points']
    cases=choose_cases(baseline);save(out/'cases.json',cases)
    save(out/'method-freeze.json',dict(parameters=PARAMETERS,input_hashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads-photo-2.jpg',OLD/'phase1.json.gz',OLD/'coverage.json',OLD/'ownership.json',ROOT/'photo2/r282/results/centerline.json']},source_hashes={p.name:sha(p) for p in sorted(Path(__file__).parent.glob('*.py'))},photo=meta))
    allresults=[]
    for case in cases:
        origin=np.array(case['origin'])-48;f=cut_features(features,origin,[224,224])
        inherited=shift_rows([r for r in baseline if np.all(np.array(r['seed'])>=origin+24) and np.all(np.array(r['seed'])<origin+200)],-origin)
        bank,ledger=cues(f,inherited);save(out/(case['name']+'-cues.json'),dict(origin=origin.tolist(),bank=bank,ledger=ledger))
        result=dict(case=case,methods={},baseline=[r for r in baseline if in_case(r,case)])
        for m in 'ABC':
            localrows,pairs=infer(f,bank,m);globalrows=shift_rows(localrows,origin)
            # Fixed R283 support scale: a shrinking mask must not shrink its own near band.
            relationships(globalrows,curve)
            tree=cKDTree([r['measured_photo_location'] or r['seed'] for r in baseline])
            for r in globalrows:
                _,ix=tree.query(r['measured_photo_location'] or r['seed']);scale=baseline[ix]['centerline']['local_support_scale']
                rel=r['centerline'];rel['local_support_scale']=scale;rel['near']=rel['unsigned_support_distance'] is not None and rel['unsigned_support_distance']<=scale/2
                rel['nearness_rule']='min support distance <= half frozen nearest R283 local support scale; no centroid-only selection'
                rel['near_12px_sensitivity']=rel['unsigned_support_distance'] is not None and rel['unsigned_support_distance']<=12
            rows=[r for r in globalrows if in_case(r,case)];ids={r['record_id'] for r in rows};pairs=[p for p in pairs if any(k in ids for k in p['ids'])]
            result['methods'][m]=dict(records=rows,pairs=pairs,summary=summary(rows,pairs))
        save(out/(case['name']+'.json.gz'),result);allresults.append({m:result['methods'][m]['summary'] for m in 'ABC'})
        print(case['name'],{m:(result['methods'][m]['summary']['high_near'],result['methods'][m]['summary']['high_crossing']) for m in 'ABC'},flush=True)
    save(out/'summary.json',dict(cases=allresults,case_order=[c['name'] for c in cases],totals={m:{key:sum(r[m][key] for r in allresults) for key in ('high_near','high_crossing','overlap_pairs','secondary_pairs')} for m in 'ABC'},scope='Eight disjoint real crops, not a full replacement inventory. Review-selected set, no calibrated recall.'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUT);args=parser.parse_args();main(args.output)
