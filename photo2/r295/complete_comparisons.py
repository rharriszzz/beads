"""Add the already-fitted hand+ export and exact historical assignment comparison.

No fitting or selection is performed after reserved evaluation. The first exporter
named a duplicate hand-minus candidate 'opposite' when the primary hand switched.
Preserve it in place and add the actual pre-frozen hand-plus candidate explicitly.
"""
import numpy as np
from .common import *
from .geometry import Chain
from .evaluate import evaluate,summary
from .physical_audit import audit
from .finalize import visibility,export
from photo2.r294.evaluate import legacy,summary as old_summary

def main():
    data=read(EVIDENCE/'inputs.json.gz');joint=read(OUT/'joint.json');candidate=next(r for r in joint['candidates'] if r['parameters']['hand']==1);p=candidate['parameters'];s=Chain(p,data['r294']);name='hand-plus'
    r=evaluate(p,data);r['physical_audit']=audit(p,data['r294']);native,_,_=photo();xy,owner,d=visibility(s,native.shape[:2]);np.savez_compressed(OUT/(name+'-visibility.npz'),xy=xy,owner=owner,unknown=d['unknown']);export(name,s,r,xy,owner,d,[])
    save(OUT/(name+'-evaluation.json'),r)
    correction=BASE/'checkpoints/export-label-correction.json' if OUT==BASE/'results' else OUT/'export-label-correction.json'
    save(correction,dict(reason='Joint winner changed from hand+ to hand-. Original opposite filename is therefore a duplicate hand-minus model, retained without alteration. Added hand-plus export from the existing pre-freeze joint candidate; no model parameters changed, no post-reserved tuning.',candidate_parameters=p,joint_sha256=sha(OUT/'joint.json'),primary_unchanged=True))
    historical={}
    for name in ('R294','local','global','geometry','R295','hand-plus','light'):
        p=read(OUT/(name+'-evaluation.json'))['parameters'];rows=legacy(Chain(p,data['r294']),data['r294']);historical[name]=dict(rows=rows,summary={split:old_summary([r for r in rows if r['split']==split]) for split in ('train','holdout')})
    baseline=read(ROOT/'photo2/r294/results/revised-evaluation.json')['summary']['holdout']['legacy'];assert historical['R294']['summary']['holdout']==baseline
    save(OUT/'historical-one-to-one.json',dict(models=historical,original_R294_assignment_rule_exact=True,limits='Historical one-to-one automatic-mask ownership is not truth. New many-to-one compatibility is reported separately.'))
    print('Complete hand-plus alternative and exact historical one-to-one comparison written')
if __name__=='__main__':main()
