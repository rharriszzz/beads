"""Explicit second orientation freedom and constrained simultaneous recovery epoch."""
import time
from copy import deepcopy
from collections import Counter
import numpy as np
from photo2.r297.common import read,save,digest,utc
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r316.renderer import RayLayers
from . import search
from .search import OUT,merit,vals,vector
from .model import Chain

def rank(r,h='A'):
    if not r['feasible']:return (1e6,1e6)
    a=vals(r,h);targets=np.array([.88,.85,.80,.80,.80,.79]);z=list(np.maximum(0,targets-a)/.10)
    for key,paper,worst,omit,seam,br in [('development',.30,13.42,9.26,33.34,9.),('comparison',.97,10.77,9.38,26.87,14.3)]:
        v=r[key]['vector'];z.extend([max(0,v['paper']-paper)/.3,max(0,v['worst']-worst)/1.5,max(0,v['omission']-omit)/2,max(0,v['seam']-seam)/12,max(0,r['brackets'][key]['p95']-br)/2])
    reg=sum(np.mean(np.square(np.asarray(r['parameters'].get(k,[0]))/s)) for k,s in [('compact_phase',.4),('compact_spacing',.02),('compact_tilt',20),('compact_cant',12)])
    return (max(z),float(np.mean(np.square(z)))+.002*reg)

def admissible(r):
    if not r['feasible']:return False
    a=vals(r,'A');v=r['development']['vector'];w=r['comparison']['vector']
    return bool(np.all(a>=np.array([.80,.83,.7186440677966102,.75,.6325678496868476,.7657142857142857])) and v['paper']<=.5 and w['paper']<=1.07 and v['worst']<=14.42 and w['worst']<=11.77 and r['brackets']['development']['p95']<=10 and r['brackets']['comparison']['p95']<=15.3)

def main():
    began=time.monotonic();deadline=time.time()+390;data=load()[0];e=engine();search.Chain=Chain;rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];initial=len(rows);seen={digest(r['parameters']):r for r in rows};cache=RayLayers();rng=np.random.default_rng(1317)
    def trial(p,stage,h='A',local=True):
        if time.time()>deadline:raise TimeoutError
        key=digest(p)
        if key in seen:return seen[key]
        t=time.monotonic()
        try:r,s,tr=search.evaluate(p,data,e,cache if local else None)
        except ValueError as ex:r=dict(parameters=p,feasible=False,classification='exploration-bound',reason=str(ex))
        r.update(id=len(rows),stage=stage,hypothesis=h,seconds=time.monotonic()-t)
        if 'physical' in r:r['physical'].pop('witnesses',None)
        rows.append(r);seen[key]=r;save(OUT/'trials'/f'{r["id"]:05d}.json.gz',r)
        if len(rows)%10==0:print(r['id'],stage,h,r['classification'],rank(r,h),np.round(vals(r,h),3).tolist() if r['feasible'] else '',flush=True)
        return r
    feasible=[r for r in rows if r['feasible']];seeds=[min(feasible,key=rank),rows[3],min(feasible,key=lambda r:merit(r,'B'))]
    try:
        for h,seed in zip(['A','A','B'],seeds):
            options=[seed]
            for a in [-10.,-5.,5.,10.]:
                p=deepcopy(seed['parameters']);p['radial_cant']=a;options.append(trial(p,'D-shared-radial-cant',h,False))
            for i in range(3):
                for a in [-8.,8.]:
                    p=deepcopy(seed['parameters']);p['compact_cant']=[0]*len(p['compact_centers']);p['compact_cant'][i]=a;options.append(trial(p,'D-local-cant-sensitivity',h))
            cur=min(options,key=lambda r:rank(r,h));fields=[('compact_cant',i,4.) for i in range(3)]+[('compact_phase',i,.035) for i in range(3)]+[('compact_tilt',i,2.5) for i in range(3)]+[('compact_spacing',i,.003) for i in range(3)]
            for cycle in range(3):
                for field,i,step in fields:
                    opts=[cur]
                    for sign in [-1,1]:
                        p=deepcopy(cur['parameters']);p[field]=list(p.get(field,[0]*len(p['compact_centers'])));p[field][i]+=sign*step*.7**cycle;opts.append(trial(p,'D-joint-cant-placement',h))
                    cur=min(opts,key=lambda r:rank(r,h))
                for j in range(15):
                    p=deepcopy(cur['parameters'])
                    for field,i,step in fields:
                        p[field]=list(p.get(field,[0]*len(p['compact_centers'])));p[field][i]+=rng.normal()*step*.35
                    r=trial(p,'D-coupled-cant',h)
                    if rank(r,h)<rank(cur,h):cur=r
            # Registration/shared thickness interaction around the jointly optimized pose.
            for j in range(28):
                p=deepcopy(cur['parameters']);p['translation']=(np.array(p.get('translation',[0,0]))+rng.normal(size=2)*.5).tolist();p['axial']+=rng.normal()*.012;p['tilt']+=rng.normal()*1.3
                r=trial(p,'D-shared-joint',h,False)
                if rank(r,h)<rank(cur,h):cur=r
    except TimeoutError:print('REFINEMENT CUTOFF',flush=True)
    f=[r for r in rows if r['feasible']];adm=[r for r in f if admissible(r)];selected={'A':min(adm or f,key=rank)['id'],'B':min(f,key=lambda r:rank(r,'B'))['id'],'C':min(f,key=lambda r:merit(r,'C'))['id']}
    vv=np.array([vector(r) for r in f]);pareto=[r['id'] for i,r in enumerate(f) if not np.any(np.all(vv<=vv[i]+1e-12,axis=1)&np.any(vv<vv[i]-1e-12,axis=1))]
    save(OUT/'refinement.json',dict(seconds=time.monotonic()-began,initial_trials=initial,new_trials=len(rows)-initial,total_trials=len(rows),classifications=dict(Counter(r['classification'] for r in rows[initial:])),selected=selected,admissible=[r['id'] for r in adm],pareto=pareto,finished=utc(),policy='Added radial orientation freedom diagnosed as absent from R316. Fixed centers under cant-only interventions. Same rate bounds; 12deg cant and combined 3deg/address orientation derivative. A selected inside explicit preservation gates when nonempty. No adoption.'))
    print('DONE',len(rows),selected,'admissible',len(adm),flush=True)
if __name__=='__main__':main()
