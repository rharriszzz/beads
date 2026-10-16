"""Native evaluation after the fit seal; baseline and alternatives use same pixels."""
import time
from copy import deepcopy
import numpy as np
from .evidence import BASE,ROOT,read,save,sha,utc
from .model import Local,predict,NAMES,BOUNDS
from .objective import evaluate,assignment,secondary
from photo2.r299.forward import Surface,shade,highlight
from photo2.r298.geometry import outlines
from photo2.r297.common import load_evidence

def stats(records,section,scale):
    t=np.array(section['tangent']);n=np.array([-t[1],t[0]]);finite=[r for r in records if r['error'] is not None];e=np.array([r['error'] for r in finite]);v=np.array([r['residual'] for r in finite]).reshape(-1,2);station=(np.array([r['observed'] for r in finite]).reshape(-1,2)-section['center'])@t
    full=np.sort([r['error'] if r['error'] is not None else np.inf for r in records]);quant=lambda q:float(full[min(len(full)-1,int(np.ceil(q*len(full)))-1)]) if len(full) and np.isfinite(full[min(len(full)-1,int(np.ceil(q*len(full)))-1)]) else None
    slope=np.polyfit(station,v@t,1)[0] if len(e)>2 and np.ptp(station)>1 else None
    return dict(n=len(records),matched=len(e),unmatched=len(records)-len(e),median_including_unmatched=quant(.5),p90_including_unmatched=quant(.9),null_quantile_means_unmatched_infinite=True,finite_rms=float(np.sqrt(np.mean(e**2))) if len(e) else None,finite_median=float(np.median(e)) if len(e) else None,finite_p90=float(np.quantile(e,.9)) if len(e) else None,signed_tangent_mean=float(np.mean(v@t)) if len(e) else None,signed_normal_mean=float(np.mean(v@n)) if len(e) else None,tangent_slope_per100px=float(slope*100) if slope is not None else None,rms_in_face_diameters=float(np.sqrt(np.mean(e**2))/(2*scale)) if len(e) else None,face_diameter_px=2*scale,missing_penalty_rms=float(np.sqrt(np.mean([r['error']**2 if r['error'] is not None else 400 for r in records]))) if records else None)

def baseline(s,ident):
    inputs,_=load_evidence()
    if ident=='R299':d=read(ROOT/'photo2/r299/results/joint-history.json.gz')[15];p=d['parameters'];light=d['fit']['light']
    else:
        d=read(ROOT/f'photo2/r299/results/fixed-{0 if ident=="R297" else 49}-directional.json.gz');p=d['parameters'];light=d['fit']['light']
    scene=Surface(p,inputs);c=np.array(s['center']);t=np.array(s['tangent']);n=np.array([-t[1],t[0]]);extent=s.get('halfspan',52)+24
    corners=c+np.array([a*t+b*n for a in [-extent,extent] for b in [-91,91]]);lo=np.floor(corners.min(0));hi=np.ceil(corners.max(0));yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.c_[xx.ravel(),yy.ravel()];tr=scene.camera(xy);sh=shade(scene,tr,light);pred=[]
    for k in np.unique(tr['owner']):
        if k<0:continue
        mask=tr['owner']==k;h=highlight(xy[mask],sh['intensity'][mask])
        if h:pred.append(dict(owner=int(k),index=int(scene.indices[k]),point=h['centroid'],peak=h['peak'],strength=h['peak_intensity']))
    train=assignment(pred,[r for r in s['observations'] if r['split']=='train'],s);held=assignment(pred,[r for r in s['observations'] if r['split']=='withheld'],s,blocked=train['used'])
    scene.polygons=lambda:outlines(scene);sec=secondary(scene,s,2);poly=outlines(scene);keep=np.linalg.norm(scene.pc-c,axis=1)<180
    return dict(feasible=True,parameters=p,hand=p['hand'],train=train,withheld=held,predictions=pred,secondary=sec,loss=train['loss']+sec['loss'],polygons=poly[keep].tolist(),indices=scene.indices[keep].tolist(),centers=scene.centers[keep].tolist(),projected_centers=scene.pc[keep].tolist(),baseline=True,reference_face_diameter=2*scene.radius*scene.scale,physical_scope='Unchanged historical complete-chain certificate; new local matching does not recover physical identities.')

def main():
    seal=read(BASE/'results/fit-freeze.json');sections=read(BASE/'evidence/frozen.json.gz')['sections'];manifest=[];t0=time.monotonic()
    for s in sections:
        group=[r for r in read(BASE/'results/refined-manifest.json.gz') if r['section']==s['id']]
        for r in group:
            result=evaluate(r['best']['parameters'],s,r['hand'],2,True)
            manifest.append(dict(name=r['name'],section=s['id'],kind='independent',result=result))
        for r in read(BASE/'results/joint-manifest.json.gz'):
            j=sections.index(s);v=r['best']['parameters'];p=np.r_[v[:12],v[12+j*6:18+j*6]];result=evaluate(p,s,r['hand'],2,True)
            manifest.append(dict(name=f'joint-h{r["hand"]}-{s["id"]}',section=s['id'],kind='joint',result=result))
        for ident in ['R297','R298','R299']:
            manifest.append(dict(name=f'{ident}-{s["id"]}',section=s['id'],kind='baseline',result=baseline(s,ident)))
    for r in manifest:
        result=r['result'];s=next(s for s in sections if s['id']==r['section'])
        if not result['feasible']:continue
        records=result['train']['records']+result['withheld']['records'];scale=result.get('reference_face_diameter',2*result['parameters']['scale'])/2
        result['summary']={g:stats([z for z in records if g=='all' or z['split']==g or z['color']==g],s,scale) for g in ['all','train','withheld','red','yellow','black']}
        # Quantify simple center matching separately from physically predicted highlights.
        centers={int(i):np.array(p) for i,p in zip(result['indices'],result['projected_centers'])}
        for z in records:
            z['center_error_same_assignment']=float(np.linalg.norm(centers[z['index']]-z['observed'])) if z['index'] in centers else None
        save(BASE/f'results/native-{r["name"]}.json.gz',r)
    save(BASE/'results/native-manifest.json.gz',manifest)
    save(BASE/'results/native-complete.json',dict(utc=utc(),seconds=time.monotonic()-t0,seal_sha256=sha(BASE/'results/fit-freeze.json'),models=len(manifest)))
    print('Native export complete',len(manifest),flush=True)

if __name__=='__main__':main()
