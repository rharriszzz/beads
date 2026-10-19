"""Bounded photographic interventions, independent of any motif score."""
import argparse, copy, time
from collections import Counter
from pathlib import Path
import numpy as np
from photo2.r329.common import inputs,canonical,replay,serialize,save,read,ROOT,lifted,extend
from photo2.r329.photographic_diagnostics.explore import OBS, CO, ST, measure, fit

def normalize_path(state,n):
    by={r['window']:r for r in state['path'][:-1]}
    return [by[i] for i in range(n)]+[by[0]]

def bounded_g(bank,prep,primary,checkpoint,width):
    start=time.perf_counter();begin=10;end=35;states=[checkpoint[begin]];failures=Counter();success=[];trace=[]
    anchor='C-1608-0253'; targets=['NEW-1621-315','P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325']
    wanted={o:tuple(np.array(CO['early'][o])-CO['early'][anchor]) for o in targets}
    for wi in range(begin,end+1):
        batch=[];arc=bank['windows'][wi]['arc_px']
        for s in states:
            for p in prep['patches'][wi]:
                t,why=extend(s,p,lifted(p,arc,bank['stations_px'],bank['period_px']))
                if t is None:failures[why]+=1;continue
                coords={o:ab for (o,turn),ab in t['coords'].items()}
                if anchor in coords and any(o in coords and tuple(np.array(coords[o])-coords[anchor])!=ab for o,ab in wanted.items()):
                    failures['G colored alternative constraint']+=1;continue
                batch.append(t)
        unique={}
        future={o for pp in prep['patches'][wi+1:] for p in pp for o in p['assignments']}
        for t in sorted(batch,key=lambda s:-s['score']):
            key=tuple(sorted((k,v) for k,v in t['coords'].items() if k[0] in future))
            if key not in unique:unique[key]=t
            if len(unique)>=width:break
        states=list(unique.values()); completed=0
        # Try reconnecting to every remaining historical primary patch now.
        for s in states:
            present={o for o,t in s['coords']}
            if not set(targets)<=present:continue
            full,receipt,_=replay(bank,prep,primary['path'],checkpoint=s,start=wi+1)
            if full:
                completed+=1;success.append(dict(last_replaced=wi,receipt=receipt,state=serialize(full)))
        trace.append(dict(window=wi,retained=len(states),suffix_completions=completed,seconds=time.perf_counter()-start))
        if not states or time.perf_counter()-start>90:break
    # Save distinct complete coordinate maps; retaining all equivalent paths is
    # unnecessary, but counts and trace preserve the scope of the search.
    distinct={}
    for r in success:
        key=tuple(sorted(canonical(r['state']).items()))
        if key not in distinct:distinct[key]=r
    return dict(width=width,targets=targets,anchor=anchor,required_deltas=wanted,trace=trace,failures=dict(failures),completed_attempts=len(success),candidates=list(distinct.values()),seconds=time.perf_counter()-start)

def shared_fits(case,box,targets):
    alt={'G':'early','H':'lower'}[case]
    # Expand shared reference coverage; every target excluded together. Same
    # measurements and exact reference coordinate cohort in both candidates.
    variants=[]; inventory=[]
    for margin in [0,60,120]:
        shared=[o for o in OBS if OBS[o]['color']!='black' and o not in targets and o in CO['working'] and o in CO[alt] and CO['working'][o]==CO[alt][o] and box[0]-margin<OBS[o]['xy'][0]<box[2]+margin and box[1]-margin<OBS[o]['xy'][1]<box[3]+margin]
        stable=[o for o in shared if all(measure(OBS[o],r,t) is not None for r in [16,18,20] for t in [.95,1.,1.05])]
        inventory.append(dict(margin=margin,shared=shared,stable=stable))
        for radius,threshold in [(16,.95),(18,1.),(20,1.05)]:
            mm={o:measure(OBS[o],radius,threshold) for o in stable+targets};pts={o:m[0] for o,m in mm.items() if m is not None}
            for degree in [1,2]:
                for state in ['working',alt]:
                    test=[o for o in targets if o in CO[state] and o in pts]
                    pred=fit(CO[state],pts,stable,test,degree) if len(stable)>=3 else None
                    if pred is None:variants.append(dict(margin=margin,radius=radius,threshold=threshold,degree=degree,state=state,available=False));continue
                    errors=[]
                    for o in stable:
                        pp=fit(CO[state],pts,[x for x in stable if x!=o],[o],degree)
                        if pp is not None:errors.append(float(np.linalg.norm(pp[0]-pts[o])))
                    variants.append(dict(margin=margin,radius=radius,threshold=threshold,degree=degree,state=state,available=True,anchors=stable,control_errors=errors,targets={o:dict(prediction=pp.tolist(),observed=pts[o].tolist(),error=float(np.linalg.norm(pp-pts[o]))) for o,pp in zip(test,pred)}))
    return dict(inventory=inventory,variants=variants)

def model_controls():
    # Reuse actual all-body visibility raster. Registration is a rigid 2D
    # translation of that frozen raster, NOT a newly certified physical scene.
    m=np.load(ROOT/'photo2/r329/photographic_diagnostics/model-geometry.npz');owner=m['owner'].reshape(m['shape']);bbox=m['bbox'];step=float(m['step'])
    targets=[('C-1302-0316',-64),('C-1391-0312',-38),('C-1422-0264',-26)]
    rows=[]
    for oid,address in targets:
        px=measure(OBS[oid])[1];values=[]
        for delta in range(-7,8):
            js=np.flatnonzero(m['indices']==address+delta)
            if not len(js):continue
            j=int(js[0])
            for dx in range(-12,13,2):
                for dy in range(-12,13,2):
                    xx=np.rint((px[:,0]-dx-bbox[0])/step).astype(int);yy=np.rint((px[:,1]-dy-bbox[1])/step).astype(int)
                    valid=(xx>=0)&(xx<owner.shape[1])&(yy>=0)&(yy<owner.shape[0]);coverage=np.sum(owner[yy[valid],xx[valid]]==j)/len(px)
                    values.append(dict(address_delta=delta,dx=dx,dy=dy,coverage=float(coverage)))
        rows.append(dict(id=oid,address=address,pixels=px.tolist(),trials=values))
    configs=[(d,dx,dy) for d in range(-7,8) for dx in range(-12,13,2) for dy in range(-12,13,2)]
    by=[{(r['address_delta'],r['dx'],r['dy']):r['coverage'] for r in x['trials']} for x in rows]
    shared=[]
    for mode in ['registration','correspondence','joint']:
        options=[v for v in configs if (mode!='registration' or v[0]==0) and (mode!='correspondence' or v[1:]==(0,0))]
        # Reference only is fit; remaining two observations test transfer.
        best=max(options,key=lambda v:(by[0][v],-sum(abs(x) for x in v)))
        shared.append(dict(mode=mode,fit_observation=targets[0][0],configuration=best,coverages=[x[best] for x in by]))
    return dict(rows=rows,shared=shared,baseline=[x[(0,0,0)] for x in by],policy='Partial colored pigment coverage; finite-grid translation/correspondence controls. No black position evidence or new physical fit. Shared changes fitted at reference only; two other colored regions test transfer.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter()
    g,b,p,states=inputs();end,_,cp=replay(b,p,states[0]['path']);gtrials=[]
    for width in [32,128]:
        r=bounded_g(b,p,states[0],cp,width);gtrials.append(r);print('G',width,len(r['candidates']),r['seconds'],flush=True)
    save(out/'g-replays.json.gz',gtrials)
    # Exact difference ledger distinguishes successive shears from one offset.
    common=sorted(CO['working'].keys()&CO['early'].keys(),key=lambda o:b['stations_px'][o]);ledger=[]
    for o in common:
        a=np.array(CO['working'][o]);d=np.array(CO['early'][o])-a
        ledger.append(dict(id=o,xy=OBS[o]['xy'],station=b['stations_px'][o],working=a.tolist(),delta=d.tolist(),delta_A=int(d@[7,6]),delta_B=int(d@[6,7])))
    save(out/'g-differences.json.gz',ledger)
    # H missing observation: parent membership versus connected selected patch.
    omitted='C-1144-2947';members=[]
    for wi in range(75,87):
        for hi,h in enumerate(b['windows'][wi]['hypotheses']):
            if omitted in h['assignments']:
                members.append(dict(window=wi,hypothesis=hi,assignment=h['assignments'][omitted],patches=[j for j,pp in enumerate(p['patches'][wi]) if pp['hypothesis']==hi and omitted in pp['assignments']]))
    attempts=[]
    lower=states[5];_,_,cpl=replay(b,p,lower['path'])
    for wi in range(79,83):
        for pi,pp in enumerate(p['patches'][wi]):
            if omitted not in pp['assignments']:continue
            path=copy.deepcopy(lower['path']);path[wi]=dict(window=wi,patch=pi,hypothesis=pp['hypothesis'])
            s,r,_=replay(b,p,path,checkpoint=cpl[wi],start=wi)
            attempts.append(dict(window=wi,patch=pi,receipt=r,state=serialize(s) if s else None))
    fitG=shared_fits('G',[1525,220,1710,350],['P5-1645-0309','C-1669-0293','NEW-1697-280','E5-1671-0325'])
    fitH=shared_fits('H',[1050,2800,1230,2985],['C-1125-2900','C-1119-2879','C-1098-2901','NEW-1074-2896',omitted])
    save(out/'photography.json.gz',dict(G=fitG,H=dict(**fitH,omitted_membership=members,local_reinsertions=attempts,selected=[dict(window=wi,working=states[0]['path'][wi],lower=lower['path'][wi],lower_parent_has_omitted=omitted in b['windows'][wi]['hypotheses'][lower['path'][wi]['hypothesis']]['assignments'],lower_patch_omitted=p['patches'][wi][lower['path'][wi]['patch']]['parent_omitted']) for wi in range(79,83)]),F=model_controls(),seconds=time.perf_counter()-t))
    print('PHOTOGRAPHY DONE',time.perf_counter()-t,flush=True)

if __name__=='__main__':main()
