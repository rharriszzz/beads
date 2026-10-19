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
    wanted={o:tuple(int(x) for x in np.array(CO['early'][o])-CO['early'][anchor]) for o in targets}
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

def followup(out):
    from .pattern import dataset,probabilities,COLORS
    from .refine import save as safe_save
    from photo2.r329.photographic_diagnostics.check_growth import assess
    from photo2.r329.photographic_diagnostics.continuity import angle,angle_diff
    g,b,p,ss=inputs();_,_,cp=replay(b,p,ss[5]['path']); states=[cp[79]];trace=[]
    for wi in range(79,83):
        batch=[]
        for s in states:
            for pp in p['patches'][wi]:
                t,why=extend(s,pp,lifted(pp,b['windows'][wi]['arc_px'],b['stations_px'],b['period_px']))
                if t:batch.append(t)
        unique={}
        for t in sorted(batch,key=lambda s:-s['score']):
            key=tuple(sorted(t['coords'].items()))
            if key not in unique:unique[key]=t
            if len(unique)>=128:break
        states=list(unique.values());trace.append(dict(window=wi,states=len(states)))
    hsuccess=[]
    for s in states:
        if 'C-1144-2947' not in {o for o,t in s['coords']}:continue
        end,r,_=replay(b,p,ss[5]['path'],checkpoint=s,start=83)
        if end:hsuccess.append(dict(receipt=r,state=serialize(end)))
    safe_save(out/'h-bundle-repair.json.gz',dict(trace=trace,candidates=hsuccess))
    _,states,ids,obs,station,blocks,c,w=dataset();idx={o:i for i,o in enumerate(ids)};base=canonical(states['working']);names=sorted(base);ii=np.array([idx[o] for o in names]);k=np.array([base[o] for o in names])@[7,6]
    candidates=read(out.parent/'photography/g-replays.json.gz')[-1]['candidates'];evaluation=[]
    for cand in candidates:
        co=canonical(cand['state']);rows=[o for o in names if o in co];jj=np.array([names.index(o) for o in rows]);ka=np.array([co[o] for o in rows])@[7,6];kb=k[jj];gain=[];conflicts=[]
        for block in range(12):
            tr=blocks[ii]!=block;te=blocks[ii[jj]]==block;th,_=probabilities(k,c[ii],w[ii],208,tr)
            gain.extend((np.log(th[ka[te]%208,c[ii[jj[te]]]])-np.log(th[kb[te]%208,c[ii[jj[te]]]])).tolist())
            for j in np.flatnonzero(te):
                if ka[j]!=kb[j] and th[kb[j]%208,c[ii[jj[j]]]]>th[ka[j]%208,c[ii[jj[j]]]]+.2:
                    conflicts.append(dict(id=rows[j],working_index=int(kb[j]),candidate_index=int(ka[j]),color=COLORS[c[ii[jj[j]]]]))
        evaluation.append(dict(H=cand['state']['H'],last_replaced=cand['last_replaced'],score=cand['state']['score'],changed_observations=sum(co[o]!=base[o] for o in rows),mean_log_change=float(np.mean(gain)),new_conflicts=conflicts))
    safe_save(out/'g-pattern-check.json.gz',evaluation)
    # Generalize E's direction diagnostic to all alternative colored bridges.
    # Reference intervals must have the same primitive assignment in BOTH maps;
    # omit the target from all reference intervals. No black geometry is used.
    colored=[o for o in base if obs[o]['color']!='black' and measure(obs[o]) is not None]
    pts={o:measure(obs[o])[0] for o in colored};refs=[]
    for ia,a in enumerate(colored):
        for z in colored[ia+1:]:
            delta=np.array(base[z])-base[a];nz=np.flatnonzero(delta)
            if len(nz)!=1 or abs(delta[nz[0]])!=1:continue
            fam=int(nz[0]);v=(pts[z]-pts[a])/delta[fam];refs.append((a,z,fam,(pts[a]+pts[z])/2,v))
    checks=[];seen=set()
    for name,state in states.items():
        if name=='working':continue
        co=canonical(state)
        for ia,a in enumerate(colored):
            if a not in co:continue
            for z in colored[ia+1:]:
                if z not in co or np.linalg.norm(pts[z]-pts[a])>85:continue
                dp=np.array(base[z])-base[a];da=np.array(co[z])-co[a]
                if np.array_equal(dp,da) or max(abs(dp))>3 or max(abs(da))>3:continue
                key=(a,z,tuple(dp),tuple(da))
                if key in seen:continue
                seen.add(key);mid=(pts[a]+pts[z])/2;local=[r for r in refs if z not in r[:2] and all(o in co for o in r[:2]) and tuple(np.array(co[r[1]])-co[r[0]])==tuple(np.array(base[r[1]])-base[r[0]]) and np.linalg.norm(r[3]-mid)<150]
                if any(sum(r[2]==fam for r in local)<3 for fam in [0,1]):continue
                votes=[]
                for bw in [35,55,85]:
                    eligible=[]
                    for fam in [0,1]:
                        rr=[r for r in local if r[2]==fam];weights=np.array([np.exp(-.5*(np.linalg.norm(r[3]-mid)/bw)**2) for r in rr]);v=np.average([r[4] for r in rr],weights=weights,axis=0);ang=angle(v);spread=max(angle_diff(angle(r[4]),ang) for r in rr)
                        if angle_diff(angle(pts[z]-pts[a]),ang)<=spread:eligible.append(fam)
                    votes.append(eligible)
                fam=votes[0][0] if len(votes[0])==1 and all(v==votes[0] for v in votes) else None
                def matches(d):return bool(fam is not None and d[1-fam]==0 and d[fam]!=0)
                checks.append(dict(map=name,source=a,target=z,working_delta=dp.tolist(),alternative_delta=da.tolist(),family=fam,working_same_family=matches(dp),alternative_same_family=matches(da),references=[list(r[:3]) for r in local],votes=votes,scope='Baseline pigment extraction; three locality controls. Exploratory screen, not universal rejection rule.'))
    old=read(ROOT/'photo2/r329/photographic_diagnostics/continuity.json.gz')['cases']['E']
    regression={name:assess(old,CO[name]) for name in ['working','closest']}
    assert regression['working']['status']=='same_family' and regression['closest']['status']=='family_mismatch'
    safe_save(out/'e-regression-and-extension.json.gz',dict(regression=regression,automatic_bridge_checks=checks))
    print('FOLLOWUP',len(hsuccess),'H completions;',len(evaluation),'G checks;',len(checks),'colored bridges',flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--followup',action='store_true');args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter()
    if args.followup:followup(out);return
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
