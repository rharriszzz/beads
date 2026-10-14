"""Run existing three-phase architecture with frozen R283 photographic evidence."""
from copy import deepcopy
import shutil
from photo2.r282 import phase2,phase3
from .common import OUT,OLD,read,save,sha,validate


def main():
    freeze=read(OUT/'phase1-freeze.json');assert sha(OUT/'phase1.json.gz')==freeze['phase1_sha256']
    target=OUT/'integrated';target.mkdir(parents=True,exist_ok=True)
    assert not (target/'complete.json').exists(),'Use a fresh output for replay'
    for name,source in [('phase1.json.gz',OUT),('centerline.json',OLD)]:shutil.copyfile(source/name,target/name)
    phase2.OUT=target;phase3.OUT=target
    result=phase2.main()
    # Preserve the unmodified global-fit export before explicit uncertainty capping.
    original=target/'uncapped';original.mkdir(exist_ok=True)
    for name in result['selected_ids']:
        path=target/(name+'-inventory.json.gz');shutil.copyfile(path,original/path.name);d=read(path)
        for r in d['records']:
            r['pre_R283_identity_weight']=r['phase2_identity_reliability']
            # Local correspondence is not established. This is a conservative
            # engineering ceiling, not a posterior probability or calibration.
            weight=min(.35,r['phase2_identity_reliability'])
            r.update(phase2_identity_reliability=weight,physical_identity_reliability=weight,physical_model_confidence=weight,
                identity_class='unresolved',reliability_semantics='uncalibrated engineering weights',
                ownership_alternatives_preserved_in='../../phase1.json.gz')
            r['notes'].append('R283: independent local identity remains unresolved; global model is a regression alternative, not adopted local improvement. Identity weight capped at .35.')
            validate(r)
        save(path,d)
    result['R283_local_adoption']=False
    result['R283_limit']='Global family rerun for full pipeline regression only; local experiments do not justify a unique correspondence or global-count constraint.'
    save(target/'phase2.json',result);p3=phase3.main()
    # Also run original weights as an explicitly labeled sensitivity control.
    for name in result['selected_ids']:
        d=read(original/(name+'-inventory.json.gz'))
        save(original/(name+'-patterns.json'),dict(weighted=phase3.search(d['records'],d['model']['n']),
            note='Uncapped engineering-weight sensitivity, not an accepted pattern.'))
    assert sha(OUT/'phase1.json.gz')==freeze['phase1_sha256']
    save(target/'complete.json',dict(phase1_sha256=sha(target/'phase1.json.gz'),phase2_sha256=sha(target/'phase2.json'),
        phase3_sha256=sha(target/'phase3.json'),local_prediction_sha256=sha(OUT/'local/prediction-freeze.json'),
        phases=['frozen independent photographic inventory','physical fits/visibility/photo colors','uncertainty-weighted patterns'],
        accepted_count=False,accepted_hand=False,accepted_pattern=False))

if __name__=='__main__':main()
