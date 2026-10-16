"""Bounded structural fits with separate dimensional residuals and contact gates."""
from copy import deepcopy
from time import monotonic
import argparse
import numpy as np
from scipy.optimize import least_squares
from .geometry import Chain,Baseline,outlines,envelope,bead_extents,contact,R
from photo2.r297.common import ROOT,read,save,sha,load_evidence
BASE=ROOT/'photo2/r298'

def measurements():
    m=read(BASE/'evidence/measurements.json');reject=read(BASE/'evidence/visual-screen.json')['excluded']
    for r in m['envelope']:r['fit_eligible']=r['eligible'] and r['id'] not in reject
    return m

def prediction(p,data,m,baseline=False):
    scene=(Baseline if baseline else Chain)(p,data);poly=outlines(scene)
    return scene,poly,bead_extents(scene,m['beads'],poly),envelope(scene,m['envelope'],poly)

def metrics(pred,m,split):
    bd,en=pred;bi=[i for i,r in enumerate(m['beads']) if r['split']==split];ei=[i for i,r in enumerate(m['envelope']) if r['fit_eligible'] and r['split']==split]
    br=np.array([r['extent_px'] for r in m['beads']])-bd;er=np.array([r['bounds'] for r in m['envelope']])-en
    return dict(bead_axial_mae=float(np.mean(abs(br[bi,0]))),bead_face_mae=float(np.mean(abs(br[bi,1]))),edge_mae=float(np.mean(abs(er[ei]))),width_mae=float(np.mean(abs(np.diff(er[ei],axis=1)))),edge_common_mode_mae=float(np.mean(abs(er[ei].mean(1)))),width_bias=float(np.mean(np.diff(er[ei],axis=1))),bead_count=len(bi),profiles=len(ei))

def fit(base,data,m,mode,max_nfev=24,physical=False):
    keys={'dimensions':['scale','axial'],'shape':['scale','axial','elevation','roll'],'axis':[], 'joint':['scale','axial','minor','elevation','perspective','roll']}[mode]
    bounds=dict(roll=(-90.,90.),scale=(7.,10.5),axial=(.50,1.15),minor=(3.5,5.8),elevation=(48.,89.),perspective=(0,.0012))
    p0=deepcopy(base);p0.setdefault('roll',0.);p0.setdefault('axis_nodes',[0.]*16)
    axis=mode in ('axis','joint');v0=[p0[k] for k in keys]+(p0['axis_nodes'] if axis else [])
    lower=[bounds[k][0] for k in keys]+([-45.]*16 if axis else []);upper=[bounds[k][1] for k in keys]+([45.]*16 if axis else [])
    bi=[i for i,r in enumerate(m['beads']) if r['split']=='development'];ei=[i for i,r in enumerate(m['envelope']) if r['fit_eligible'] and r['split']=='development']
    targetb=np.array([r['extent_px'] for r in m['beads']]);targete=np.array([r['bounds'] for r in m['envelope']]);unc=np.maximum(4,np.array([r['uncertainty_px'] for r in m['envelope']]))
    history=[];best=[np.inf,None]
    def unpack(v):
        p=deepcopy(p0)
        for k,x in zip(keys,v):p[k]=float(x)
        if axis:p['axis_nodes']=v[len(keys):].tolist()
        return p
    def fun(v):
        p=unpack(v);s,poly,bd,en=prediction(p,data,m)
        residual=[((bd[bi]-targetb[bi])/3).ravel()/np.sqrt(len(bi))]
        if mode not in ('shape','dimensions'):
            residual.append(((en[ei]-targete[ei])/unc[ei]).ravel()/np.sqrt(len(ei)))
            nodes=np.array(p['axis_nodes']);residual.append((np.roll(nodes,1)-2*nodes+np.roll(nodes,-1))/18/np.sqrt(len(nodes)))
        if physical:
            cert=s.certify(iterations=35)
            gaps=sorted(w['gap_units'] for w in cert['witnesses'])[:12]
            residual.append(np.maximum(0,.012-np.array(gaps))*50/np.sqrt(12))
        r=np.concatenate(residual);score=float(r@r)
        history.append(dict(parameters=p,loss=score))
        if score<best[0]:best[:]=[score,p]
        return r
    start=monotonic();opt=least_squares(fun,v0,bounds=(lower,upper),max_nfev=max_nfev,diff_step=1e-3,ftol=1e-5,xtol=1e-5,gtol=1e-5,x_scale='jac')
    p=unpack(opt.x);s,poly,bd,en=prediction(p,data,m);cert=contact(s)
    return dict(mode=mode,parameters=p,loss=float(opt.fun@opt.fun),elapsed=monotonic()-start,nfev=opt.nfev,evaluations=len(history),history=history,physical=cert,metrics={split:metrics((bd,en),m,split) for split in ['development','comparison']},beads=bd.tolist(),envelope=en.tolist(),solver_message=opt.message)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['controls','joint'],default='controls');args=ap.parse_args();data,_=load_evidence();m=measurements();results=[]
    if args.stage=='controls':
        p=read(ROOT/'photo2/r297/results/pilot/exports/model-767.json.gz')['parameters']
        scene,poly,bd,en=prediction(p,data,m,True)
        save(BASE/'results/baseline.json',dict(parameters=p,beads=bd.tolist(),envelope=en.tolist(),metrics={s:metrics((bd,en),m,s) for s in ['development','comparison']}))
        for key,delta in [('axial',-.1),('minor',.4),('scale',.5),('elevation',10),('yaw',10),('perspective',.0004),('count',101)]:
            q=deepcopy(p);q[key]+=delta
            if key=='count':q['winding']=round(q['count']/q['turn'])
            sc,pp,b,e=prediction(q,data,m);cert=contact(sc)
            results.append(dict(parameter=key,delta=delta,parameters=q,beads=b.tolist(),envelope=e.tolist(),physical=cert,metrics={s:metrics((b,e),m,s) for s in ['development','comparison']}));print(key,results[-1]['metrics']['development'],cert['state'],flush=True)
        save(BASE/'results/sensitivities.json.gz',results)
        for mode in ['shape','axis']:
            r=fit(p,data,m,mode);save(BASE/f'results/control-{mode}.json.gz',r);print(mode,r['parameters']['axial'],r['parameters']['scale'],r['metrics'],r['physical']['state'],flush=True)
    else:
        for ident in [767,694,121,631]:
            p=read(ROOT/f'photo2/r297/results/pilot/exports/model-{ident}.json.gz')['parameters']
            # Common measured shape start, retaining hand/topology/count and nuisance fields.
            shape=read(BASE/'results/control-shape.json.gz')['parameters']
            for k in ['axial','scale','elevation']:p[k]=shape[k]
            r=fit(p,data,m,'joint',max_nfev=28);r['family_source']=ident;save(BASE/f'results/joint-{ident}.json.gz',r)
            print(ident,{k:r['parameters'][k] for k in ['axial','scale','minor','elevation','perspective']},r['metrics'],r['physical']['state'],flush=True)
if __name__=='__main__':main()
