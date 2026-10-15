"""Fixed supplementary diagnostics; no detector or calibration changes."""
from collections import Counter
from .calibrate import eligible,predict
from .common import *

def main():
    rows=read(OUT/'associations.json.gz');models=read(OUT/'calibration-frozen.json')['models'];det=read(OUT/'photo-landmarks.json.gz')['records'];good=[r for r in det if r['accepted']]
    pooled=models['R275/pooled/constant_patch'];scores={};coverage={};pairs=[]
    for ref in ('R275','J','W'):
        for col in ('red','yellow'):
            for qual in ('reliable','all'):
                rr=[r for r in rows if r['reference']==ref and r['color']==col and r['split']=='evaluation' and r['match_status']=='unique' and (r['reliable'] or qual=='all')]
                err=[np.linalg.norm(predict(r,'constant_patch',pooled)-r['centroid']) for r in rr]
                scores[f'{ref}/{col}/{qual}']=stats(err)
                if rr:coverage[f'{ref}/{col}/{qual}']=dict(training_radius90=pooled['training_radius90'],evaluation_coverage=float(np.mean(np.array(err)<=pooled['training_radius90'])),threshold_sensitivity=stats([r['landmark']['threshold_sensitivity_px'] for r in rr]),dark_axes=dict(Counter(r['landmark']['dark']['axes'] for r in rr)),color_agreement=float(np.mean([r['landmark']['color']==r['color'] for r in rr])))
    lookup={(r['reference'],r['id']):r for r in rows}
    for r in rows:
        if r['reference']!='J':continue
        w=lookup.get(('W',r['id']))
        if w:pairs.append(dict(id=r['id'],color=r['color'],case=r['case'],split=r['split'],both_reliable=r['reliable'] and w['reliable'],centroid_distance=float(np.linalg.norm(np.array(r['centroid'])-w['centroid']))))
    paired=[r for r in rows if r['reference']=='R275' and r['match_status']=='unique']
    independent_vs_old=dict(point_changed=sum(r['landmark']['point']!=r['old_point'] for r in paired),count=len(paired),patch_shift=stats([np.linalg.norm(np.array(r['landmark']['centroid'])-r['old_patch']) for r in paired]),peak_saturation=stats([r['landmark']['peak_saturation'] for r in paired],1.))
    save(OUT/'diagnostics.json',dict(pooled_patch=scores,uncertainty_coverage=coverage,J_W_disagreement=pairs,independent_vs_old=independent_vs_old,detector=dict(raw_maxima=len(det),accepted=len(good),nearby_alternative_events=sum(bool(r['nearby_alternatives']) for r in good),colors=dict(Counter(r['color'] for r in good)),rejection_reasons=dict(Counter(reason for r in det for reason in r['reasons']))),interpretation='Raw maxima / features are not beads. R275 calibration transfer to J/W is not refitted; diagnostic reference disagreement is not measured physical error.'))
    exports=[]
    for r in good:
        exports.append(dict(observation_id=r['id'],phase_origin='phase1',importance='high',visibility=None,color_reliability=None,measured_point=r['centroid'],absolute_local_maximum=r['point'],weighted_centroid=r['weighted'],bright_patch_runs=r['runs'],brightness=dict(peak_linear_Y=r['peak'],annulus_background_Y=r['background'],contrast_Y=r['contrast'],peak_saturation=r['peak_saturation']),feature_covariance=r['shape']['covariance'],feature_sigma_major=r['shape']['sigma_major'],feature_sigma_minor=r['shape']['sigma_minor'],feature_orientation_deg=r['shape']['orientation_deg'],threshold_sensitivity_px=r['threshold_sensitivity_px'],color_hypothesis=r['color'],color_evidence=r['color_evidence'],specularity=r['specularity'],possible_duplicates=r['nearby_alternatives'],physical_center=None,physical_identity=None,physical_identity_reliability=None,photographic_reliability='unrated automatic feature; ownership unresolved',optional_R275_interior_proxy=dict(point=(np.array(r['centroid'])+pooled['coef'][0]).tolist(),condition='Only under red/yellow-interior interpretation; never use for black-body center',offset=pooled['coef'][0],covariance=pooled['residual_covariance'],radius90_training_px=pooled['training_radius90'],limitation='Training residual radius for selected unique R275 references, not universal measurement precision or physical-center uncertainty')))
    save(OUT/'phase2-observations.json.gz',dict(schema_version='r289-experimental-landmark-1',records=exports,production_adopted=False,source_sha256=sha(OUT/'photo-landmarks.json.gz')))
    print('Pooled constant',pooled['coef'],scores['R275/red/reliable'],scores['R275/yellow/reliable'])
if __name__=='__main__':main()
