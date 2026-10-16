"""Evaluation-only complete guard views for truncation-sensitive source models.

No optimizer, selection or budget extension. Original sealed predictions remain.
"""
import json
import time
import numpy as np
from .core import *
from .export import surface
from photo2.r301.export import stats

def main():
    began=time.monotonic();ss=read(BASE/'evidence/sections.json.gz');seal=read(BASE/'results/fit-freeze.json');models=read(BASE/'results/native-manifest.json.gz')
    affected=read(BASE/'results/post-seal-guard-review.json')['affected'];audit=[]
    for name in affected:
        r=next(r for r in seal['selected'] if r['name']==name);s=next(s for s in ss if s['id']==r['section']);c=Scene(r['parameters'],s,r['hand'],r['mode'],guards=96)
        original=read(BASE/f'results/native-{name}.json.gz')['result'];d=deepcopy(original);pred,raster=old.native(c,s)
        d['train']=assignment(pred,[z for z in s['observations'] if z['split']=='train'],s)
        d['withheld']=assignment(pred,[z for z in s['observations'] if z['split']=='withheld'],s,blocked=d['train']['used'])
        z=d['secondary']=structure(c,s,raster);d['withheld_material']=structure(c,s,held=True)
        d['contact']=c.certify(iterations=100,witnesses=True);d['predictions']=pred;d['polygons']=c.polygons().tolist();d['indices']=c.indices.tolist();d['centers']=c.centers.tolist();d['projected_centers']=c.pc.tolist();d['local_positions']=z['local_positions']
        d['flags']=flags(d);d['geometrically_accepted']=False;d['guard_extension']=dict(guards_each_side=96,positions=c.n,physical=d['contact'],scope='post-seal diagnostic only; not fitted')
        dd=np.array(z['extents'])-np.array([q['extent_px'] for q in s['bead_dimensions']]) if s['bead_dimensions'] else np.array([])
        ee=np.array(z['envelope_bounds'])-np.array([q['bounds'] for q in s['profiles']]) if s['profiles'] else np.array([])
        penalty=(float(np.mean(dd*dd)) if dd.size else 0)+(float(np.mean(ee*ee)) if ee.size else 0)+(.5*float(np.mean(np.minimum(z['boundary_distances'],20.)**2)) if z['boundary_distances'] else 0)+100*(z['paper']+z['material_missing'])
        barrier=4000*(max(0,z['paper']-.10)**2+max(0,z['material_missing']-.23)**2)+4*max(0,z['dimension_mae']-3)**2+4*max(0,z['edge_mae']-4)**2
        d['reflection_loss']=d['train']['loss'];d['structural_loss']=penalty+barrier;d['loss']=d['reflection_loss']+d['structural_loss']
        records=d['train']['records']+d['withheld']['records'];d['summary']={g:stats([q for q in records if g=='all' or q['split']==g or q['color']==g],s,c.scale) for g in ['all','train','withheld','red','yellow','black']}
        outname='guard217-'+name;d['surface_image']=surface(c,s,outname);d['evaluation_flags']=['Evaluation-only217-position extension; original153-position fit was truncation-sensitive; not a refitted or selected model']
        d['post_seal_guard_audit']['scope']='217-position audit of the sealed153-position parameters; no further convergence claim'
        d['diagnostic']={k:v for k,v in raster.items() if k not in ['xy','owner','shape']}
        m=dict(name=outname,section=s['id'],kind='R303-guard-audit',stage='post-seal evaluation',result=d);models.append(m);save(BASE/f'results/native-{outname}.json.gz',m)
        audit.append(dict(name=name,positions=c.n,local_positions=d['local_positions'],loss=d['loss'],train_rms=d['summary']['train']['finite_rms'],held_rms=d['summary']['withheld']['finite_rms'],secondary=z,held=d['withheld_material'],flags=d['flags'],contact_certified=d['contact']['certified']))
    save(BASE/'results/native-manifest.json.gz',models)
    (ROOT/'photo2/review/r303/data.js').write_text('const DATA='+json.dumps(dict(sections=ss,models=models),separators=(',',':'))+';\n')
    save(BASE/'results/extended-audit.json',dict(utc=utc(),seconds=time.monotonic()-began,optimization=False,selected=False,models=audit))
    for r in audit:print(r['name'],r['local_positions'],r['train_rms'],r['held_rms'],r['flags'])

if __name__=='__main__':main()
