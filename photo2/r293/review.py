"""Prioritized new review; old judgments remain read-only evidence, never new answers."""
import shutil
from collections import Counter
import numpy as np
from .common import *
from .geometry import Reference

def history():
    records={}
    for experiment,path in [('R291',ROOT/'photo2/r291/evidence/completed-review-analysis.json'),('R292',EVIDENCE/'r292-review-analysis.json')]:
        d=read(path)
        for q in d.get('cases',d.get('records',[])):
            records.setdefault(q['feature_id'],[]).append(dict(experiment=experiment,case_id=q['case_id'],answer=q['answer'],candidate_digest=q['candidate_digest'],source=str(path.relative_to(ROOT))))
    return records

def prioritize(new,coverage):
    chosen=[];pool=list(new)
    def add(r,reason):
        if r not in pool:return
        if any(np.linalg.norm(np.array(r['feature']['point'])-q['point'])<12 for q in chosen):return
        chosen.append(dict(case_id=r['case_id'],point=r['feature']['point'],reason=reason));pool.remove(r)
    ids={r['feature']['id']:r for r in new}
    pairs=[p for p in coverage['opposite_side_pairs'] if p['dark_separator_supported'] and all(f in ids for f in p['feature_ids'])]
    if pairs:
        pair=max(pairs,key=lambda p:sum(len(ids[f]['A']['evidence']['T4']['other_features_inside']) for f in p['feature_ids']))
        for f in pair['feature_ids']:add(ids[f],'Well-illuminated opposite-side context: assess visible material and separation without assuming a bead quota')
    for color in ('red','yellow'):
        candidates=[r for r in pool if r['feature']['color']==color and not r['A']['evidence']['T8']['reflection_edge_ambiguous'] and r['A']['evidence']['T4']['other_features_inside']]
        if candidates:add(max(candidates,key=lambda r:len(r['A']['evidence']['T4']['other_features_inside'])),'Clear centerline-relevant candidate with other highlights inside: check material ownership; feature count is not bead count')
    for color in ('red','yellow'):
        candidates=[r for r in pool if r['feature']['color']==color and not r['A']['evidence']['T8']['reflection_edge_ambiguous'] and not r['A']['evidence']['T4']['other_features_inside'] and r['A']['evidence']['T3']['target_material']['continuation_exposure']>=.75 and r['A']['evidence']['T3']['target_material']['local_material_pixels']>=100]
        if candidates:add(max(candidates,key=lambda r:r['A']['evidence']['T7']['supported_fraction']*min(r['A']['evidence']['T8']['perturbation_IoU'])),'Clearly illuminated visible-material proposal: assess usefulness of its measured region, not a full physical silhouette')
    candidates=[r for r in pool if r['A']['evidence']['T8']['reflection_edge_ambiguous']]
    if candidates:add(max(candidates,key=lambda r:min(r['A']['evidence']['T8']['perturbation_IoU'])),'Independent reflection measurement: assess the illuminated reflection only; dark-body outline and physical center are unknown')
    candidates=[r for r in pool if r['split']=='reserved' and not r['A']['evidence']['T8']['reflection_edge_ambiguous']]
    if candidates:add(min(candidates,key=lambda r:r['priority_evidence']['centerline']['distance']),'Reserved well-observed central example: assess representative material/location for later conditional interpretation')
    return dict(cases=chosen[:8],policy='Up to2 supported opposite-side sampled features,2 possible ownership failures (red/yellow contexts),2 useful-looking colored supports,1 reflection measurement,1 reserved central example. Only frozen well-observed centerline targets; no old judgments or maximum-instability peripheral ranking. All assessments remain human. Selection is not an accuracy sample.')

def main():
    population={r['feature_id']:r for r in read(OUT/'feature-population.json.gz')['records']};prior=history();old=[r for stage in ('development','reserved') for r in read(ROOT/f'photo2/r292/results/{stage}.json.gz')['records']];new=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];coverage=read(OUT/'coverage.json');chosen=prioritize(new,coverage);byid={q['case_id']:q for q in chosen['cases']};rows=old+new;manifest=[]
    (REVIEW/'data').mkdir(exist_ok=True);(REVIEW/'crops').mkdir(exist_ok=True)
    for r in rows:
        name=r['case_id'];isnew=name.startswith('central-');r['historical_reviews']=prior.get(r['feature']['id'],[]);r['read_only_historical']=bool(r['historical_reviews']);r['priority_context']={k:v for k,v in population[r['feature']['id']].items() if k not in ('feature',)};r['priority']=byid.get(name);r['prior_user_evidence']=[];r['analysis_limit_reached']=r['search'][-1]['contact'];r['comparison']=None;r['baseline']=None;r['r291_review']={}
        if not isnew:
            previous=read(ROOT/f'photo2/review/r292/data/{name}.json');r['prior_user_evidence']=previous['prior_user_evidence'];r['baseline']=dict(A=previous['A'],algorithm=previous['algorithm'],label='A');r['split']='historical'
        r['measurement_question']='Assess the visible material or reflection region and representative photographic observation, not a complete physical silhouette.'
        r['position_measurements']=dict(independent_bright_patch=r['feature']['centroid'],weighted_patch_alternative=r['feature']['weighted'],location_selection='R289 recommended unweighted small-patch centroid; original weighted alternative retained',peak=r['feature']['point'],patch_threshold_sensitivity_px=r['feature']['threshold_sensitivity_px'],candidate_visible_region_centroid=r['A']['candidate_centroid'],candidate_centroid_status='Hypothesis unless independently accepted; not a physical center',physical_center=None,physical_identity=None)
        path=REVIEW/'data'/(name+'.json');save(path,r);src=(OUT if isnew else ROOT/'photo2/r292/results')/'crops'/(name+'.png');shutil.copy2(src,REVIEW/'crops'/(name+'.png'));h=r['historical_reviews'];manifest.append(dict(case_id=name,feature_id=r['feature']['id'],point=r['feature']['point'],split=r['split'],categories=r['categories'],status=r['A']['status'],alternative=bool(r['B']),candidate_digest=sha(path),priority_reason=r['priority']['reason'] if r['priority'] else None,historical_review=bool(h),historical_answer=h[-1]['answer'] if h else None,well_observed=r['priority_context']['well_observed_proxy'],centerline_distance=r['priority_context']['centerline']['distance']))
    save(OUT/'start-here.json',chosen);save(REVIEW/'manifest.json',dict(schema='R293-review-v1',cases=manifest,start_here=[q['case_id'] for q in chosen['cases']],priority_policy=chosen['policy'],algorithm=rows[0]['algorithm'],photo=rows[0]['photo']))
    for a,b in [('R293_REPORT.md','report.md'),('R293_REPRODUCE.md','reproduce.md')]:
        if (ROOT/'photo2'/a).exists():shutil.copy2(ROOT/'photo2'/a,REVIEW/b)
    print('Packaged',len(rows),'cases;',len(chosen['cases']),'new central questions;',sum(c['historical_review'] for c in manifest),'historical cases read-only')
if __name__=='__main__':main()
