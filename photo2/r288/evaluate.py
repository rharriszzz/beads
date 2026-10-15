"""Photographic proxy metrics and coverage; no independent real identity truth."""
from collections import Counter
from itertools import combinations
from .common import *
from photo2.r287.evaluate import coverage as original_coverage

def as_cases(cases,method):
    # Use the original exact geometry/overlap accounting with selected hypotheses.
    obs=[dict(o,selector=dict(o['selector'])) for q in cases for o in q['observations']]
    for o in obs:
        choice=o['r287_selector'] if method=='R287' else o['selector']['selection'] if method=='selector' else dict(alternatives=[method])
        o['selector']=dict(selection=choice)
    return obs

def cover(cases,method):
    out=[]
    for q in cases:
        c=original_coverage(as_cases([q],method),'selector');out.append(dict(case=q['name'],**c))
    totals={k:sum(q[k] for q in out) for k in ('nonempty','near_robust','near_possible','crossing_robust','near_overlap_groups')}
    totals.update(overlap_pairs=sum(len(q['overlap_pairs']) for q in out),duplicates=sum(p['near_duplicate'] for q in out for p in q['overlap_pairs']),flanking_pairs=sum(len(q['flanking_pairs']) for q in out))
    return dict(total=totals,cases=out)

def summarize(cases):
    obs=[o for q in cases for o in q['observations']];out=dict(observations=len(obs),decisions=dict(Counter(o['selector']['status'] for o in obs)),selected_methods=dict(Counter(','.join(o['selector']['selection']['alternatives']) or 'abstain' for o in obs)),independent_J_inadequacy=sum(bool(o['selector']['selection']['J_inadequacy']) for o in obs),controls={},anchors=[])
    for m in ('J','M','B','E','W','H'):
        cc=[o['evidence']['candidates'][m] for o in obs];rows=[o['variants'][m] for o in obs];retained=0;total=0;shifts=[]
        for o in obs:
            p=set(map(tuple,pixels(o['variants'][m]['measured_support'])));pp=np.array(o['evidence']['diffuse_routes'].get('pixels',[]),int).reshape(-1,2)+o['origin'];wanted=set(map(tuple,pp));retained+=len(p&wanted);total+=len(wanted)
            a=o['variants'][m]['measured_photo_location'];b=o['variants']['M']['measured_photo_location']
            if a is not None and b is not None:shifts.append(float(np.linalg.norm(np.array(a)-b)))
        out['controls'][m]=dict(nonempty=sum(c['area']>0 for c in cc),within_cap=sum(12<=c['area']<=870 for c in cc),seam_conflicts=sum(c['coherent_seam_conflicts']>0 for c in cc),unstable=sum(c['stability']['minimum_iou']<.7 for c in cc),domain_sensitive=sum(c['stability']['domain_minimum_iou']<.9 for c in cc),window_contact=sum(bool(c['stability']['window_contact']) for c in cc),components_gt1=sum(c['components']>1 for c in cc),mean_minimum_iou=float(np.mean([c['stability']['minimum_iou'] for c in cc])),mean_centroid_shift_from_M=float(np.mean(shifts)) if shifts else None,old_direct_diffuse_retained=retained,old_direct_diffuse_total=total,families={family:sum(c['stability']['by_family'][family]['minimum_iou']<.7 for c in cc) for family in ('gain','contrast','sigma','background','seed','domain')})
    for q in cases:
        o=min(q['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-q['seed']));out['anchors'].append(dict(case=q['name'],id=o['id'],color=o['color'],decision=o['selector']['status'],alternatives=o['selector']['selection']['alternatives'],area={m:r['metrics']['area'] for m,r in o['variants'].items()},minimum_iou={m:o['evidence']['candidates'][m]['stability']['minimum_iou'] for m in o['variants']},J_inadequacy=o['selector']['selection']['J_inadequacy']))
    out['coverage']={m:cover(cases,m) for m in ('J','M','B','E','W','H','R287','selector')};return out

def main():
    result={stage:summarize(read(OUT/(stage+'.json.gz'))['cases']) for stage in ('development','confirmation') if (OUT/(stage+'.json.gz')).exists()}
    result.update(real_precision=None,real_recall=None,new_distinct_beads_certified=0,limits=['R287 direct diffuse routes are a fixed photographic proxy, not independent labeled true-body material.','All raw-method coverage includes defective proposals; selector excludes abstentions.','Both alternatives count once, robust geometry requires agreement.','No new cue discovery; different supports do not certify new distinct bodies.'])
    save(OUT/'evaluation.json',result)
    for stage in ('development','confirmation'):
        if stage in result:print(stage,result[stage]['decisions']);print([(q['case'],q['alternatives'],q['area']) for q in result[stage]['anchors']])
if __name__=='__main__':main()
