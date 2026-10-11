"""Explicit post-hoc lower-dimensional control, kept separate from main holdout."""
import json
from .refit import OUT,BeadCurve,SurfaceLoss,fit,audit
from .generate import save

def run():
    c=json.loads((OUT/'initial.json').read_text());ev=json.loads((OUT/'origin-evidence.json').read_text());loss=SurfaceLoss(ev['box'],ev['observations']);rows=[]
    for label,active in [('C2',[0,1]),('C4',[0,1,2,3])]:
        fitted,log=fit(c,(c['origin']+2)/c['n'],loss,'C',400,active);fitted['id']='R258_origin_'+label;fitted['section']='origin';fitted['box']=ev['box'];save(OUT/(fitted['id']+'.json'),fitted)
        rows.append(dict(id=fitted['id'],**log,**audit(fitted,loss),protocol='Post-hoc compact control after observing primary holdout regression; not an untouched confirmatory test'))
    save(OUT/'compact-controls.json',rows)
    # main and alternative jobs may still own their index; final packaging merges.
    print([(r['id'],r['metrics']) for r in rows],flush=True)
if __name__=='__main__':run()
