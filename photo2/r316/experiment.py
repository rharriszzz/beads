"""Deterministic staged shared-profile/orientation then coherent-placement controls.

No random population and no old scalar merit. Fixed individual core, paper, seam,
finite bracket and worst-region metrics are retained. Diagnostic ranking selects
controls only; absolute readiness and physical certification decide eligibility.
"""
import time
from copy import deepcopy
from collections import Counter
import numpy as np
from photo2.r297.common import ROOT,read,save,digest
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r314.diagnostics import EARLY
from photo2.r315.model import refined_trace,subset
from photo2.r315.diagnose import brackets
from photo2.r315.measurement import measure_readiness
from photo2.r307.fast import grid
from .model import Chain
OUT=ROOT/'photo2/r316/results'


def early(s,e,tr):
    rows=[]
    for c in e.doc['regions']:
        if c['id'] not in EARLY:continue
        ix=np.flatnonzero(e.m['core'].ravel()==c['label']);xy=e.xy[ix];cs=[]
        for j in s.tree.query_ball_point(c['point'],s.query_radius+20):
            it=refined_trace(subset(s,[j]),xy);mask=it['owner']>=0
            if not mask.any():continue
            vis=tr['owner'][ix]==j;ids,num=np.unique(tr['owner'][ix][mask&~vis],return_counts=True)
            cs.append(dict(index=int(s.indices[j]),isolated_fraction=float(mask.mean()),visible_fraction=float(vis.mean()),occluders=[dict(index=int(s.indices[k]) if k>=0 else None,pixels=int(n)) for k,n in zip(ids,num)]))
        cs.sort(key=lambda r:-r['isolated_fraction']);rows.append(dict(id=c['id'],pixels=len(ix),candidates=cs,best_isolated=cs[0]['isolated_fraction'] if cs else 0,best_visible=max([z['visible_fraction'] for z in cs],default=0)))
    return rows


def evaluate(p,data,e):
    t=time.perf_counter();s=Chain(p,data);geom=time.perf_counter()-t;cert=contacts(s,seconds=.35);row=dict(parameters=p,physical=cert,feasible=cert['certified'],classification=cert['classification'],geometry_seconds=geom)
    if not row['feasible']:return row,s,None
    t=time.perf_counter();tr=refined_trace(s,e.xy);row['render_seconds']=time.perf_counter()-t;t=time.perf_counter()
    for part,k in enumerate(['development','comparison','buffer']):row[k]=e.measure(tr['owner'],tr['unknown'],s.indices,part,True)
    bs=brackets(e,tr);row['brackets']=dict(count=len(bs),missing=sum(not b['found'] for b in bs),p95=float(np.percentile([b['displacement'] for b in bs if b['found']],95)),maximum=max(b['displacement'] for b in bs if b['found']))
    row['early']=early(s,e,tr);row['scoring_and_diagnostics_seconds']=time.perf_counter()-t;row['compact_rates']=s.compact_rate_bounds
    return row,s,tr


def vector(r):
    if not r['feasible']:return None
    v=r['development']['vector'];w=r['comparison']['vector']
    return np.array([1-min(z['best_isolated'] for z in r['early']),1-min(z['best_visible'] for z in r['early']),v['paper'],w['paper'],v['seam'],w['seam'],r['brackets']['p95'],v['worst'],w['worst'],v['omission'],w['omission']])


def rank(r):
    z=vector(r)
    return (1e6,) if z is None else tuple(sorted(z/np.array([.2,.2,.5,.5,10,10,3,3,3,5,5]),reverse=True))


def main():
    began=time.monotonic();data=load()[0];e=engine();rows=[];seen=set();parents={};seeds={}
    def trial(p,label,parent):
        if time.monotonic()-began>300:return None
        h=digest(p)
        if h in seen:return None
        seen.add(h);t=time.monotonic()
        try:r,s,tr=evaluate(p,data,e)
        except ValueError as ex:r=dict(parameters=p,feasible=False,classification='exploratory-bound',reason=str(ex))
        r.update(id=len(rows),parent=parent,intervention=label,seconds=time.monotonic()-t)
        if 'physical' in r:r['physical'].pop('witnesses',None)
        rows.append(r);save(OUT/'trials'/f'{r["id"]:04d}.json.gz',r)
        print(r['id'],parent,label,r['classification'],rank(r)[:2],flush=True);return r
    for name,path in [('R306','photo2/r315/results/baseline-model.json.gz'),('focused3','photo2/r314/results/models/R313-focused-3.json.gz'),('narrow','photo2/r315/results/narrow-model.json.gz')]:
        p=read(ROOT/path)['parameters'];parents[name]=p;seeds[name]=trial(p,'unchanged-parent',name)
        # Dimensions and shared orientation, without registration/phase confounding.
        for rad,thick,tilt in [(r,a,t) for r in [.94,1.,1.06] for a in [.85,1.,1.15] for t in [-8.,0.,8.]]:
            q=deepcopy(p);q['radius']*=rad;q['axial']*=thick;q['tilt']+=tilt;trial(q,f'shared-dimensions-orientation:{rad},{thick},{tilt}',name)
        for edge,face in [(.20,.55),(.344,.8),(.5,1.)]:
            for tilt in [-8.,0.,8.]:
                q=deepcopy(p);q.update(exterior=True,edge=edge,face=face,bore=.14);q['tilt']+=tilt;trial(q,f'exterior-orientation:{edge},{face},{tilt}',name)
    # Choose one constrained diagnostic lead per family; freeze its shape in stage 2.
    stage2={name:min([r for r in rows if r['parent']==name and r['feasible']],key=rank) for name in parents}
    for name,lead in stage2.items():
        p=deepcopy(lead['parameters']);p.setdefault('compact_centers',[-13,0,13]);p.setdefault('phase_halfwidth',18);p.setdefault('spacing_halfwidth',35);p.setdefault('compact_phase_rate_limit',.05)
        for field,amps in [('compact_phase',[-.16,.16]),('compact_spacing',[-.008,.008]),('compact_tilt',[-8.,8.])]:
            for i in range(3):
                for amp in amps:
                    q=deepcopy(p);q[field]=list(q.get(field,[0,0,0]));q[field][i]+=amp;trial(q,f'coherent-{field}:{i},{amp}',name)
        for key,amps in [('minor',[-.25,.25]),('translation_x',[-3.,3.]),('translation_y',[-3.,3.])]:
            for amp in amps:
                q=deepcopy(p)
                if key.startswith('translation'):
                    q['translation']=list(q.get('translation',[0,0]));q['translation'][0 if key.endswith('x') else 1]+=amp
                else:q[key]+=amp
                trial(q,f'placement-control:{key},{amp}',name)
        # Deliberate joint follow-up combines separately tested local phase/station/orientation.
        local=[r for r in rows if r['parent']==name and r['feasible'] and r['intervention'].startswith('coherent-')]
        q=deepcopy(p)
        for field in ['compact_phase','compact_spacing','compact_tilt']:
            candidates=[r for r in local if field in r['intervention']];winner=min(candidates,key=rank) if candidates else None
            if winner and rank(winner)<rank(lead):q[field]=winner['parameters'][field]
        trial(q,'joint-separated-block-winners',name)
    feasible=[r for r in rows if r['feasible']];pareto=[]
    for r in feasible:
        v=vector(r)
        if not any(np.all(vector(o)<=v+1e-10) and np.any(vector(o)<v-1e-10) for o in feasible):pareto.append(r['id'])
    best=min(feasible,key=rank);chosen=[('R306',seeds['R306']),('focused3',seeds['focused3']),('narrow',seeds['narrow']),('joint-best',best)]
    exports=[]
    for name,row in chosen:
        r,s,tr=evaluate(row['parameters'],data,e);r.update(name=name,trial=row['id'],cohort=list(range(-100,100)),positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist()))
        r['readiness']={k:measure_readiness(e,tr,r[k],i) for i,k in enumerate(['development','comparison','buffer'])};ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);full=refined_trace(s,xy);assert len(ix)==200
        r['target']=dict(bodies=200,full_bodies=s.n,rays=len(xy),unknown=int(full['unknown'].sum()),visible_counts=[dict(index=int(s.indices[j]),pixels=int(np.sum(full['owner']==j))) for j in ix]);save(OUT/f'{name}-model.json.gz',r);np.savez_compressed(OUT/f'{name}-raster.npz',owner=tr['owner'],unknown=tr['unknown']);np.savez_compressed(OUT/f'{name}-target.npz',xy=xy,owner=full['owner'],unknown=full['unknown']);save(OUT/f'{name}-brackets.json.gz',brackets(e,tr));exports.append(dict(name=name,trial=row['id'],parameters=r['parameters'],readiness=r['readiness'],target=r['target']))
    save(OUT/'experiment.json',dict(seconds=time.monotonic()-began,trials=len(rows),classifications=dict(Counter(r['classification'] for r in rows)),pareto=pareto,pareto_dimensions=['early isolated deficit','early visible deficit','development paper','comparison paper','development seam','comparison seam','all bracket p95','development worst','comparison worst','development omission','comparison omission'],selected=exports,best=best['id'],stage2_seeds={k:v['id'] for k,v in stage2.items()},adopted=False,policy='Deterministic blocks, fixed global phase and old low-frequency basis. No optical fitting. Bounds are exploratory, not measured material strain. Full necklace certification and exact rendering; no hybrid proposal speedup claim.'))
if __name__=='__main__':main()
