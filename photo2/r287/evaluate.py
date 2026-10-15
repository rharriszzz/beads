"""Decision/ownership/coverage accounting without calibrated real-photo truth."""
from collections import Counter
from itertools import combinations
from .common import *

def pset(r):return set(map(tuple,pixels(r['measured_support'])))
def coverage(obs,method):
    # A both decision remains an alternative set. A pair overlaps if any retained
    # interpretation overlaps; robust near/crossing requires every alternative.
    groups=[]
    for o in obs:
        names=[method] if method in ('J','M','B') else o['selector']['selection']['alternatives']
        rr=[o['variants'][m] for m in names];groups.append((names,rr))
    pairs=[];parent=list(range(len(obs)))
    def root(i):
        while parent[i]!=i:i=parent[i]
        return i
    for i,j in combinations(range(len(obs)),2):
        scores=[];intersections=[]
        for a in groups[i][1]:
            for b in groups[j][1]:
                pa,pb=pset(a),pset(b);scores.append(len(pa&pb)/max(1,len(pa|pb)));intersections.append(len(pa&pb))
        if scores and max(intersections)>0:pairs.append(dict(ids=[obs[i]['id'],obs[j]['id']],maximum_iou=max(scores),maximum_overlap=max(intersections),near_duplicate=max(scores)>=.5))
        if scores and max(scores)>=.5:parent[root(j)]=root(i)
    near=[i for i,(_,rr) in enumerate(groups) if rr and all(r['centerline']['near'] for r in rr)];possible=[i for i,(_,rr) in enumerate(groups) if rr and any(r['centerline']['near'] for r in rr)];cross=[i for i,(_,rr) in enumerate(groups) if rr and all(r['centerline']['crosses'] for r in rr)];flanking=[]
    for i,j in combinations(near,2):
        all_ok=True
        for a in groups[i][1]:
            for b in groups[j][1]:
                ca,cb=a['centerline'],b['centerline'];aa,ab=ca.get('arc_interval',[0,0]),cb.get('arc_interval',[0,0]);gap=max(aa[0],ab[0])-min(aa[1],ab[1]);pa,pb=pset(a),pset(b);overlap=len(pa&pb)/max(1,min(len(pa),len(pb)))
                all_ok &= {ca['side'],cb['side']}=={'negative','positive'} and gap<=12 and overlap<.2
        if all_ok:flanking.append([obs[i]['id'],obs[j]['id']])
    return dict(nonempty=sum(bool(rr) and all(r['measured_support'] for r in rr) for _,rr in groups),near_robust=len(near),near_possible=len(possible),crossing_robust=len(cross),near_overlap_groups=len({root(i) for i in near}),overlap_pairs=pairs,flanking_pairs=flanking)

def summarize(cases,anchors=False):
    obs=[min(q['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-q['seed'])) for q in cases] if anchors else [o for q in cases for o in q['observations']];out=dict(observations=len(obs),decisions=dict(Counter(o['selector']['status'] for o in obs)),by_color={color:dict(Counter(o['selector']['status'] for o in obs if o['color']==color)) for color in ('red','yellow')},mean_JM_iou=float(np.mean([o['evidence']['agreement_iou'] for o in obs])),low_agreement=sum(o['evidence']['agreement_iou']<.65 for o in obs),controls={},preferences=[])
    for m in ('J','M','B'):
        rr=[o['variants'][m] for o in obs];cc=[o['evidence']['candidates'][m] for o in obs];out['controls'][m]=dict(nonempty=sum(r['metrics']['area']>0 for r in rr),within_cap=sum(0<r['metrics']['area']<=870 for r in rr),seam_conflicts=sum(c['coherent_seam_conflicts']>0 for c in cc),unstable=sum(c['stability']['minimum_iou']<.7 for c in cc),domain_unstable=sum(c['stability']['domain_minimum_iou']<.9 for c in cc),mean_area=float(np.mean([c['area'] for c in cc])),mean_minimum_iou=float(np.mean([c['stability']['minimum_iou'] for c in cc])),families={family:dict(flagged=sum(c['stability']['by_family'][family]['minimum_iou']<.7 for c in cc),mean_minimum_iou=float(np.mean([c['stability']['by_family'][family]['minimum_iou'] for c in cc]))) for family in ('gain','contrast','sigma','background','seed','domain')})
    for o in obs:
        e=o['evidence'];out['preferences'].append(dict(id=o['id'],color=o['color'],decision=o['selector']['status'],reasons=o['selector']['selection'],JM_iou=e['agreement_iou'],diffuse_gain_pixels=e.get('diffuse_routes',{}).get('supported_pixels',0),diffuse_route_fraction=e.get('diffuse_routes',{}).get('supported_fraction',0),J_area=e['candidates']['J']['area'],M_area=e['candidates']['M']['area']))
    return out

def main():
    dev=read(OUT/'development.json.gz')['cases'];conf=read(OUT/'confirmation.json.gz')['cases'];v1=read(OUT/'development-v1.json.gz')['cases'];groups=[]
    for stage,cases in [('development',dev),('confirmation',conf)]:
        for q in cases:
            for m in ('J','M','B','selector'):groups.append(dict(stage=stage,case=q['name'],method=m,**coverage(q['observations'],m)))
    totals={m:{k:sum(q[k] for q in groups if q['stage']=='confirmation' and q['method']==m) for k in ('nonempty','near_robust','near_possible','crossing_robust','near_overlap_groups')} for m in ('J','M','B','selector')}
    for m in totals:
        qs=[q for q in groups if q['stage']=='confirmation' and q['method']==m];totals[m].update(overlap_pairs=sum(len(q['overlap_pairs']) for q in qs),near_duplicate_pairs=sum(p['near_duplicate'] for q in qs for p in q['overlap_pairs']),flanking_pairs=sum(len(q['flanking_pairs']) for q in qs))
    save(OUT/'evaluation.json',dict(development=summarize(dev),first_policy=summarize(v1),confirmation=summarize(conf),confirmation_anchors=summarize(conf,True),coverage=groups,confirmation_coverage=totals,physical_precision=None,physical_recall=None,new_distinct_bodies_certified=0,limits=['No new cue detector; J/M selection changes interiors, not certified physical inventory.','Both is two retained alternatives, never a union. Robust geometry requires both alternatives agree.','Overlap clusters can still include wrong or duplicate ownership; not bead counts.','Domain/brightness/smoothing tests keep HSV/paper/initial A fixed; conditional sensitivity only.']))
    print('anchors',summarize(conf,True)['decisions']);print('all',summarize(conf)['decisions']);print('coverage',totals)
if __name__=='__main__':main()
