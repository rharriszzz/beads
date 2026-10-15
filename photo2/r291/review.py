"""Package frozen proposals, R290 comparison and a transparent short playlist."""
import shutil
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from .common import *

def midpoint(segments,supported=True):
    return np.array([np.mean(s['endpoints'],axis=0) for s in segments if not supported or s['supported']],float).reshape(-1,2)

def compare(new,old):
    a=midpoint(new['A']['segments']);b=midpoint(old['A']['segments'])
    recovered=int(np.sum(cKDTree(b).query(a)[0]>1.5)) if len(a) and len(b) else len(a)
    lost=int(np.sum(cKDTree(a).query(b)[0]>1.5)) if len(a) and len(b) else len(b)
    before=set(old['A']['evidence']['T4']['other_features_inside']);after=set(new['A']['evidence']['T4']['other_features_inside'])
    oldpx=set(map(tuple,pixels(old['A']['candidate_pixels'])));newpx=set(map(tuple,pixels(new['A']['candidate_pixels'])))
    separators=[q for q in new['separators'] if q['supported']]
    return dict(old_pixels=len(oldpx),new_pixels=len(newpx),new_supported_sides_away_from_old=recovered,old_supported_sides_without_new_match=lost,
                side_matching_tolerance_px=1.5,old_supported_sides=len(b),new_supported_sides=len(a),other_feature_inclusions_removed=sorted(before-after),other_feature_inclusions_added=sorted(after-before),
                old_crossed_supported_separators=[q['feature_id'] for q in separators if tuple(q['point']) in oldpx],new_crossed_supported_separators=[q['feature_id'] for q in separators if tuple(q['point']) in newpx],
                old_min_IoU=min(old['A']['evidence']['T8']['perturbation_IoU']),new_min_IoU=min(new['A']['evidence']['T8']['perturbation_IoU']),
                interpretation='Location/support and feature-inclusion diagnostics only. Removed features are not verified neighboring beads; new/lost support is not improved/worse precision. R290 and R291 parameter/context stresses differ.')

def metrics(r):
    e=r['A']['evidence'];n=max(e['T7']['total_sides'],1);support=e['T7']['supported_fraction'];stability=min(e['T8']['perturbation_IoU']);agreement=e['T7']['mechanism_agreement_sides']/n
    alternate=1.
    if r['B']:
        a=set(map(tuple,pixels(r['A']['candidate_pixels'])));b=set(map(tuple,pixels(r['B']['candidate_pixels'])));alternate=len(a&b)/max(len(a|b),1)
    conflict=e['T2']['continuity_conflict_sides']/n
    unresolved_features=len(e['T4']['other_features_inside'])
    quality=support*stability*(.5+.5*agreement)*(0.3 if e['T8']['reflection_edge_ambiguous'] else 1.)*e['T3']['target_material']['continuation_exposure']/(1+unresolved_features)
    return dict(quality=quality,agreement=agreement,conflict=conflict,alternative_IoU=alternate,support=support,stability=stability,
                removed_cues=len(r.get('comparison',{}).get('other_feature_inclusions_removed',[])),dark_fraction=e['T1']['dark_supported_sides']/n)

def prioritize(records):
    chosen=[];ledger=[];pool=list(records)
    def add(reason,eligible,score):
        candidates=[r for r in pool if eligible(r) and all(np.linalg.norm(np.array(r['feature']['point'])-q['point'])>=12 for q in chosen)]
        if not candidates:ledger.append(dict(reason=reason,unfilled=True));return
        r=max(candidates,key=lambda r:(score(r),r['case_id']));value=float(score(r));chosen.append(dict(case_id=r['case_id'],point=r['feature']['point'],reason=reason,ranking_value=value,diagnostics=metrics(r)));pool.remove(r)
    for color in ('red','yellow',None):add('Likely useful contour: color-diverse high support, stability and agreement; human correctness unknown',lambda r:not r['A']['evidence']['T8']['reflection_edge_ambiguous'] and (color is None or r['feature'].get('color')==color),lambda r:metrics(r)['quality'])
    for _ in range(2):add('Complementary methods reinforce the same edge portions',lambda r:not r['A']['evidence']['T8']['reflection_edge_ambiguous'],lambda r:metrics(r)['agreement']*metrics(r)['stability']/(1+len(r['A']['evidence']['T4']['other_features_inside'])))
    for _ in range(2):add('Conflicting edge versus material evidence or a meaningfully different alternative',lambda r:bool(r['B']) or metrics(r)['conflict']>0,lambda r:metrics(r)['conflict']+1-metrics(r)['alternative_IoU'])
    for _ in range(2):add('Same-color neighbors: separator protection and old inclusion changes',lambda r:'touching-same-color' in r['categories'],lambda r:metrics(r)['removed_cues']+.1*r['A']['evidence']['T1']['protected_separators']+metrics(r)['quality'])
    add('Multiple highlights: common ownership is unresolved',lambda r:'multiple-highlights' in r['categories'] and len(r['A']['evidence']['T4']['other_features_inside'])>0,lambda r:metrics(r)['quality'])
    add('Difficult dark boundary: sustained separator evidence',lambda r:r['A']['evidence']['T1']['protected_separators']>0,lambda r:metrics(r)['dark_fraction']+metrics(r)['quality'])
    add('Possible occlusion or incomplete edges at junctions',lambda r:'occlusion' in r['categories'] or r['A']['evidence']['T6']['termination_sides']>0,lambda r:metrics(r)['quality']+r['A']['evidence']['T6']['junction_sides']/max(r['A']['evidence']['T7']['total_sides'],1))
    for fresh in (True,False):add('Poor illumination or reflection context; body extent remains uncertain',lambda r:r['A']['evidence']['T3']['target_material']['diffuse_Y']<.04 and (not fresh or (r['split']=='reserved' and r['feature'].get('color')=='unknown')),lambda r:1-metrics(r)['stability']+(.5 if r['split']=='reserved' else 0))
    return dict(cases=chosen,unfilled=ledger,ranking_source_sha256=sha(ROOT/'photo2/r291/review.py'),policy='Greedy quotas:3 likely useful (red/yellow/additional color strata),2 agreement,2 disagreement,2 same-color,1 multiple-highlight,1 dark-boundary,1 occlusion,2 low-diffuse examples (first a new unknown-context feature). Scores use frozen automatic evidence; >=12px between selected features. No manual correctness labels or machine-written human answers. Selection is for review, not an unbiased accuracy estimate.')

def main():
    rows=[r for stage in ('development','retrospective','reserved') for r in read(OUT/(stage+'.json.gz'))['records']]
    (REVIEW/'data').mkdir(parents=True,exist_ok=True);(REVIEW/'crops').mkdir(exist_ok=True)
    old_manifest={c['case_id']:c for c in read(ROOT/'photo2/review/r290/manifest.json')['cases']};comparison={}
    user=read(ROOT/'photo2/r290/evidence/user-judgments.json');facts=user['records'][0];manifest=[]
    for r in rows:
        name=r['case_id'];r['prior_user_evidence']=[];r['analysis_limit_reached']=bool(r['search'][-1]['contact'])
        if name in old_manifest:
            old=read(ROOT/'photo2/review/r290/data'/(name+'.json'));r['baseline']=dict(algorithm=old['algorithm'],A=old['A'])
            r['comparison']=compare(r,old);comparison[name]=r['comparison']
            if 'provenance_correction' in old:r['provenance_correction']=old['provenance_correction']
        else:r['baseline']=None
        if r['feature']['id']==facts['landmark_id']:
            r['prior_user_evidence'].append(dict(id=facts['id'],statement=facts['statement'],source=facts['source'],source_files=facts['source_files'],limits=facts['not_confirmed']))
        if name in ('R215-A','R215-B','R215-R'):
            previous=user['records'][1];r['prior_user_evidence'].append(dict(id=previous['id'],statement=previous['reflection']['confirmation'] if name.endswith('-R') else next(c['confirmation'] for c in previous['colored'] if c['letter']==name[-1]),source=previous['answers_source'],limits=previous['limits']))
    priority=prioritize(rows);reason_by_id={r['case_id']:r for r in priority['cases']}
    for r in rows:
        name=r['case_id'];r['priority']=reason_by_id.get(name);path=REVIEW/'data'/(name+'.json');save(path,r)
        shutil.copy2(OUT/'crops'/(name+'.png'),REVIEW/'crops'/(name+'.png'))
        manifest.append(dict(case_id=name,feature_id=r['feature']['id'],point=r['feature']['point'],split=r['split'],categories=r['categories'],status=r['A']['status'],alternative=bool(r['B']),candidate_digest=sha(path),priority_reason=r['priority']['reason'] if r['priority'] else None))
    save(OUT/'comparison.json',comparison);save(OUT/'start-here.json',priority)
    save(REVIEW/'manifest.json',dict(cases=manifest,start_here=[r['case_id'] for r in priority['cases']],priority_policy=priority['policy'],algorithm=rows[0]['algorithm'],photo=rows[0]['photo'],schema='R291-review-v1'))
    for src,dst in [('R291_REPORT.md','report.md'),('R291_REPRODUCE.md','reproduce.md')]:
        if (ROOT/'photo2'/src).exists():shutil.copy2(ROOT/'photo2'/src,REVIEW/dst)
    print('Packaged',len(rows),'cases;',len(priority['cases']),'Start Here;',sum(bool(r['B']) for r in rows),'alternatives; no human answers created')

if __name__=='__main__':main()
