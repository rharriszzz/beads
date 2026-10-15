"""Package automatic outcomes and prior human evidence without creating judgments."""
import shutil
import numpy as np
from scipy.spatial import cKDTree
from .common import *
from .separators import crossing

def region(candidate):return set(map(tuple,pixels(candidate['candidate_pixels'])))
def raster(candidate,box):
    lo=np.array(box[:2]);shape=np.array(box[2:])-lo;mask=np.zeros(shape[::-1],bool);q=pixels(candidate['candidate_pixels'])-lo;ok=(q[:,0]>=0)&(q[:,0]<shape[0])&(q[:,1]>=0)&(q[:,1]<shape[1]);q=q[ok];mask[q[:,1],q[:,0]]=True;return mask

def reference_metrics(new,old):
    a=region(new);b=region(old);add=a-b;lost=b-a
    distance=max([cKDTree(np.array(list(a))).query(np.array(list(b-a)))[0].max() if lost else 0,cKDTree(np.array(list(b))).query(np.array(list(a-b)))[0].max() if add else 0])
    iou=len(a&b)/max(len(a|b),1)
    return dict(iou=iou,exact=a==b,added_pixels=len(add),removed_pixels=len(lost),maximum_difference_distance_px=float(distance),materially_changed=bool(iou<.97 or distance>2))

def compare(r,old,label='A'):
    baseline=old[label];a=r['A'];oldmask=raster(baseline,r['box']);cross=crossing(oldmask,r['separator_arcs']);before=set(baseline['evidence']['T4']['other_features_inside']);after=set(a['evidence']['T4']['other_features_inside'])
    def points(c):return np.array([np.mean(q['endpoints'],axis=0) for q in c['segments'] if q['supported']]).reshape(-1,2)
    p,q=points(a),points(baseline)
    return dict(baseline_label=label,old_pixels=len(region(baseline)),new_pixels=len(region(a)),**reference_metrics(a,baseline),crossings_before=sum(c['straddled_samples'] for c in cross if c['enforced']),crossings_after=sum(c['straddled_samples'] for c in r['separator_comparison']['after'] if c['enforced']),routed_around_before=sum(c['routed_around_samples'] for c in cross if c['enforced']),routed_around_after=sum(c['routed_around_samples'] for c in r['separator_comparison']['after'] if c['enforced']),baseline_arc_measurements=cross,other_feature_inclusions_removed=sorted(before-after),other_feature_inclusions_added=sorted(after-before),new_supported_sides_away_from_old=int((cKDTree(q).query(p)[0]>1.5).sum()) if len(q) and len(p) else len(p),old_supported_sides_without_new_match=int((cKDTree(p).query(q)[0]>1.5).sum()) if len(q) and len(p) else len(q),old_min_IoU=min(baseline['evidence']['T8']['perturbation_IoU']),new_min_IoU=min(a['evidence']['T8']['perturbation_IoU']),interpretation='Masks and sampled crossings are diagnostics, not exact pixel truth. Multiple arcs can share samples. Other features do not certify other beads. Baseline is user-selected R291 A/B where reviewed and accepted, otherwise R291 A. Both banks inside despite excluded valley flags a possible route around an unresolved ending.')

def priority(rows):
    chosen=[];pool=list(rows)
    def take(reason,eligible,score,n):
        candidates=sorted([r for r in pool if eligible(r)],key=lambda r:(score(r),r['case_id']),reverse=True)
        for r in candidates:
            if n<=0:break
            if any(np.linalg.norm(np.array(r['feature']['point'])-q['point'])<12 for q in chosen):continue
            chosen.append(dict(case_id=r['case_id'],point=r['feature']['point'],reason=reason,score=float(score(r))));pool.remove(r);n-=1
    take('Previously wrong in a clear photograph: assess the traced separator and new contour',lambda r:r.get('r291_review',{}).get('answer')=='wrong-clear',lambda r:r['comparison']['crossings_before'],1)
    take('Accepted reference changed materially: check for lost target material or a new merger',lambda r:r.get('r291_review',{}).get('accepted') and r['r291_review']['materially_changed'],lambda r:1-r['r291_review']['iou'],3)
    take('Direct separator crossings repaired; check the actual arc and remaining ownership ambiguity',lambda r:(r.get('comparison') or {}).get('crossings_before',0)>(r.get('comparison') or {}).get('crossings_after',0) and not r.get('r291_review',{}).get('accepted'),lambda r:r['comparison']['crossings_before']-r['comparison']['crossings_after'],3)
    take('New frozen holdout: difficult separator or unstable evidence',lambda r:r['split']=='reserved',lambda r:r['A']['evidence']['T4'].get('remaining_separator_bank_connections',0)+1-min(r['A']['evidence']['T8']['perturbation_IoU']),3)
    take('New holdout reflection/poor illumination: inspect useful reflection and sensitivity separately from body extent',lambda r:r['split']=='reserved' and r['A']['evidence']['T8']['reflection_edge_ambiguous'],lambda r:1-min(r['A']['evidence']['T8']['perturbation_IoU']),1)
    take('Expanded existing merger: assess newly included material; growth is a review signal, not a correctness rule',lambda r:bool(r.get('comparison')) and r['comparison']['new_pixels']>1.05*r['comparison']['old_pixels'] and not r.get('r291_review',{}).get('accepted'),lambda r:r['comparison']['new_pixels']/max(r['comparison']['old_pixels'],1),1)
    take('Remaining merger/regression: both banks connect around an unresolved end, or new features enter',lambda r:not r.get('r291_review',{}).get('accepted') and bool(r.get('comparison')) and (r['comparison']['routed_around_after'] or r['comparison']['other_feature_inclusions_added']),lambda r:r['comparison']['routed_around_after']+len(r['comparison']['other_feature_inclusions_added']),2)
    return dict(cases=chosen,policy='At most1 previously wrong-clear,3 materially changed accepted,3 repaired crossing examples,3 difficult new holdouts,1 reflection holdout,1 expanded-merger diagnostic,2 remaining regressions;12px target spacing. No unchanged/immaterially changed accepted case is re-requested. Material change means mask IoU<.97 or added/removed native pixels >2px from the other mask; a review trigger, not a correctness criterion. Scores are diagnostic selection, not human judgments or an unbiased accuracy sample.')

def main():
    rows=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];human={q['case_id']:q for q in read(ROOT/'photo2/r291/evidence/completed-review-analysis.json')['cases']};manifest=[];comparisons={}
    for r in rows:
        name=r['case_id'];r['analysis_limit_reached']=r['search'][-1]['contact'];r['prior_user_evidence']=[]
        path=ROOT/f'photo2/review/r291/data/{name}.json'
        if path.exists():
            old=read(path);ref=human.get(name);label=ref['answer'] if ref and ref['answer'] in ('A','B') else 'A';r['baseline']=dict(algorithm=old['algorithm'],A=old[label],label=label);r['prior_user_evidence']=old['prior_user_evidence'];r['comparison']=compare(r,old,label);comparisons[name]=r['comparison']
            r['r291_review']=dict(answer=ref['answer'],accepted=ref['answer'] in ('A','B'),**reference_metrics(r['A'],old[label]),provenance='photo2/r291/evidence/completed-review-2026-10-15.jsonl.gz',candidate_digest=ref['candidate_digest']) if ref else None
        else:r['baseline']=None;r['comparison']=None;r['r291_review']=None
    # Normalize missing prior evidence for the selection predicates.
    for r in rows:
        if r['r291_review'] is None:r['r291_review']={}
    chosen=priority(rows);byid={c['case_id']:c for c in chosen['cases']};(REVIEW/'data').mkdir(parents=True,exist_ok=True);(REVIEW/'crops').mkdir(exist_ok=True)
    for r in rows:
        name=r['case_id'];r['priority']=byid.get(name);path=REVIEW/'data'/(name+'.json');save(path,r);shutil.copy2(OUT/'crops'/(name+'.png'),REVIEW/'crops'/(name+'.png'));ref=r['r291_review']
        manifest.append(dict(case_id=name,feature_id=r['feature']['id'],point=r['feature']['point'],split=r['split'],categories=r['categories'],status=r['A']['status'],alternative=bool(r['B']),candidate_digest=sha(path),priority_reason=r['priority']['reason'] if r['priority'] else None,r291_accepted=ref.get('accepted',False),r291_answer=ref.get('answer'),materially_changed=ref.get('materially_changed')))
    save(OUT/'comparison.json',comparisons);save(OUT/'start-here.json',chosen);save(REVIEW/'manifest.json',dict(schema='R292-review-v1',algorithm=rows[0]['algorithm'],photo=rows[0]['photo'],cases=manifest,start_here=[q['case_id'] for q in chosen['cases']],priority_policy=chosen['policy']))
    for src,dst in [('R292_REPORT.md','report.md'),('R292_REPRODUCE.md','reproduce.md')]:
        if (ROOT/'photo2'/src).exists():shutil.copy2(ROOT/'photo2'/src,REVIEW/dst)
    print('Packaged',len(rows),'cases;',len(chosen['cases']),'Start Here; no human answers created')
if __name__=='__main__':main()
