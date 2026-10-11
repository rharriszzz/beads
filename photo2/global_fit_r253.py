"""R253 bounded, assisted global geometry experiment. No color sequence prior.

Broad matching uses ellipsoidal screen support, followed by exact rounded-annulus
first-hit audits. All saved assignments remain model-conditional, never photo truth.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys, time, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-r253-mpl")
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, linear_sum_assignment
from scipy.spatial import cKDTree
from scipy.interpolate import splev
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tangent_circles import SplineRope, View, RADIUS, ROW, first_hits
from visible_correspondence import rays
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'photo2/review/r253'
SEED = json.loads((ROOT/'photo2/spline-seed-r175.json').read_text())
ANCHOR = 'C252-A948'  # maker 20 = C; identity preserved by R252
NAMES = ['phase_rad','origin_beads','dx_px','dy_px','elevation_deg','roll_deg',
         'stretch_sin1','stretch_cos1','stretch_sin2','stretch_cos2',
         'twist_sin1_rad','twist_cos1_rad','twist_sin2_rad','twist_cos2_rad']
LOW = np.array([-20,-2,-15,-15,70,-180]+[-.005]*4+[-np.pi/60]*4)
HIGH = np.array([20,2,15,15,89.9,180]+[.005]*4+[np.pi/60]*4)


def save(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(x, indent=2, allow_nan=False)+'\n')


def table(path, rows):
    if not rows: return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n');w.writeheader();w.writerows(rows)


def data():
    rows=list(csv.DictReader((ROOT/'photo2/review/r252/accepted.csv').read_text().splitlines()))
    for r in rows:
        for key in ['x','y','arc_fraction']: r[key]=float(r[key])
        r['sector']=int(r['sector'])
        # Eight entire, separated sectors are never used by optimization.
        r['split']='test' if r['sector']%4==0 else 'train'
    return rows


def harmonics(t):
    a=2*np.pi*np.asarray(t)
    return np.array([np.sin(a),np.cos(a),np.sin(2*a),np.cos(2*a)]).T


def correction(t, p):
    a=2*np.pi*np.asarray(t)
    integ=np.array([-np.cos(a),np.sin(a),-np.cos(2*a)/2,np.sin(2*a)/2]).T/(2*np.pi)
    return integ@p[6:10], harmonics(t)@p[10:14]


class Model(SplineRope):
    def __init__(self, n, h, p):
        self.p=np.array(p,float)
        super().__init__(SEED['points'], View(elevation=p[4],roll=p[5]),n,h,
                         smoothing=SEED['smoothing_rms_target_pixels'])
        # Translation moves the predicted rope, not the image points.
        self.view.tx += p[2];self.view.ty += p[3]

    def geometry(self, indices):
        p=self.p;indices=np.atleast_1d(indices).astype(float);t=indices/self.source.nbeads
        ds,tw=correction(t,p)
        f=(t+p[1]/self.source.nbeads+ds)%1
        u=np.interp(f,self.arc_fraction,self.u_table)
        image=np.array(splev(u,self.tck)).T
        plane=(image-[1269.5,1590.5])@self.inverse.T/self.view.scale
        line=np.column_stack((plane,np.zeros(len(indices))))
        der=np.array(splev(u,self.tck,der=1)).T@self.inverse.T
        tangent=np.column_stack((der/np.linalg.norm(der,axis=1)[:,None],np.zeros(len(indices))))
        normal=np.column_stack((-tangent[:,1],tangent[:,0],np.zeros(len(indices))))
        angle=p[0]+self.source.helicity*2*np.pi*self.source.nrows*t+tw
        radial=np.sin(angle)[:,None]*normal;radial[:,2]=np.cos(angle)
        return dict(indices=indices.astype(int),line=line,tangent=tangent,normal=normal,
                    radial=radial,centers=line+4*radial,outward=line+(4+RADIUS)*radial,
                    fraction=f)


def weights(rows):
    sec=np.array([r['sector'] for r in rows]);return np.array([1/np.sum(sec==s) for s in sec])/len(set(sec))


def candidates(model, xy):
    g=model.geometry(np.arange(model.source.nbeads));pc=model.view.project(g['centers'])
    eye=model.view.basis()[2]
    # Back-half side faces remain candidates; final tracing handles actual occlusion.
    eligible=np.flatnonzero(g['radial']@eye > -.35)
    _, j=cKDTree(pc[eligible]).query(xy,k=12);ids=eligible[j]
    delta=xy[:,None,:]-pc[ids]
    r,d,_=model.view.basis()
    axis=np.stack((g['tangent']@r,g['tangent']@d),axis=1)[ids]
    # Projected covariance of radius R, axial half-height .7R ellipsoid.
    along=np.sum(delta*axis,axis=2)
    den=1-.51*np.sum(axis*axis,axis=2)
    q=(np.sum(delta*delta,axis=2)+.51/den*along*along)/(RADIUS*model.view.scale)**2
    return ids,q,g,pc


def assign(model, rows):
    xy=np.array([[r['x'],r['y']] for r in rows]);ids,q,g,pc=candidates(model,xy)
    # Ellipsoid membership plus weak center regularizer, dimensionless to avoid
    # awarding dense/small beads a raw-pixel nearest-center advantage.
    cost=np.maximum(np.sqrt(q)-.85,0)**2+.15*q
    unique=np.unique(ids);matrix=np.full((len(rows),len(unique)),1e5)
    matrix[np.arange(len(rows))[:,None],np.searchsorted(unique,ids)]=cost*weights(rows)[:,None]
    a,b=linear_sum_assignment(matrix)
    chosen=unique[b];loc=np.argmax(ids==chosen[:,None],axis=1)
    if not np.all(np.any(ids==chosen[:,None],axis=1)): raise RuntimeError('Candidate graph exhausted')
    return chosen,cost[np.arange(len(rows)),loc],ids,q,g,pc


def penalties(p):
    # Gaussian-style engineering regularizers, not calibrated probabilities.
    return np.r_[p[2:4]/30,p[6:10]/.015,p[10:14]/np.radians(20)]*.15


def fixed_residual(p,n,h,rows,ids):
    model=Model(n,h,p);g=model.geometry(ids);pc=model.view.project(g['centers'])
    xy=np.array([[r['x'],r['y']] for r in rows]);v=xy-pc
    r,d,eye=model.view.basis();axis=np.stack((g['tangent']@r,g['tangent']@d),axis=1)
    # Smooth vector transform for the projected ellipsoid quadratic form.
    aa=np.sum(axis*axis,axis=1);a=np.sum(v*axis,axis=1)
    factor=np.where(aa>1e-8,((1-.51*aa)**-.5-1)/np.maximum(aa,1e-8),0)
    v=(v+factor[:,None]*a[:,None]*axis)/(RADIUS*model.view.scale)
    q=np.linalg.norm(v,axis=1);w=np.sqrt(weights(rows))
    visible=np.maximum(-.35-g['radial']@eye,0)*2
    return np.r_[(v*w[:,None]*np.sqrt(.15)).ravel(),np.maximum(q-.85,0)*w,visible*w,penalties(p)]


def fit(n,h,start,rows,kind='rigid',budget=45):
    p=np.array(start,float); active=list(range(6))
    if kind in ('stretch','both'): active+=list(range(6,10))
    if kind in ('twist','both'): active+=list(range(10,14))
    costs=[];neval=0
    for _ in range(4):
        ids,*_=assign(Model(n,h,p),rows)
        def fun(x):
            pp=p.copy();pp[active]=x
            return fixed_residual(pp,n,h,rows,ids)
        res=least_squares(fun,p[active],bounds=(LOW[active],HIGH[active]),
                          max_nfev=budget,diff_step=1e-4,ftol=2e-5,xtol=2e-5,gtol=2e-5)
        p[active]=res.x;neval+=res.nfev
        _,c,*_=assign(Model(n,h,p),rows);costs.append(float(c@weights(rows)+np.sum(penalties(p)**2)))
    return dict(n=n,h=h,kind=kind,p=p.tolist(),train_score=costs[-1],iterations=costs,nfev=neval)


def fft_estimate(out):
    rows=list(csv.DictReader((ROOT/'photo2/review/r250/angle-range-observations.csv').open()))
    model=Model(2698,1,np.array([0,0,0,0,89,0]+[0]*8));length=float(np.linalg.norm(np.diff(model.seed_image_curve,axis=0),axis=1).sum())
    results=[];profiles=[]
    for channel in ['V','Y']:
        for narrow in [False,True]:
            rr=[r for r in rows if r['channel']==channel and int(r['range'])==3 and (not narrow or abs(float(r['angle'])-6)<8)]
            # Multiple peaks per window: weighted mean before interpolation, never
            # count overlapping windows as independent samples.
            grid=[];vals=[]
            for idx in sorted({int(r['index']) for r in rr}):
                rs=[r for r in rr if int(r['index'])==idx]
                w=np.array([float(r['weight']) for r in rs]);f=np.array([float(r['frequency'])*np.cos(np.radians(float(r['angle']))) for r in rs])
                grid.append(float(rs[0]['s']));vals.append(float(w@f/w.sum()))
            grid=np.array(grid);vals=np.array(vals)
            all_s=np.arange(2000)*length/2000
            interp=np.interp(all_s,grid,vals,period=length)
            turns=float(interp.mean()*length)
            # Spatial-block spread describes nonuniformity/systematics, not iid CI.
            blocks=[float(v.mean()*length*6.5) for v in np.array_split(interp,32)]
            results.append(dict(channel=channel,angle_filter='within8deg_of6' if narrow else 'R250_range3',observed_windows=len(grid),coverage=len(grid)/2000,turns=turns,n_at_6_5=6.5*turns,largest_interpolation_gap_px=float(np.diff(np.r_[grid,grid[0]+length]).max()),block_equivalent_n_p10_p90=np.percentile(blocks,[10,90]).tolist()))
            if not narrow:
                profiles.extend(dict(channel=channel,s=float(s),tangent_frequency=float(f),local_n_equivalent=float(6.5*length*f)) for s,f in zip(all_s,interp))
    save(out/'fft-count.json',dict(length_pixels=length,formula='turns=integral f(s)*cos(alpha(s)) ds; N=(N/T)*turns; conditional reciprocal-family identification',estimates=results))
    table(out/'fft-profile.csv',profiles)
    return results


def scan(out):
    rows=data();train=[r for r in rows if r['split']=='train'];table(out/'split.csv',rows)
    fft_estimate(out)
    results=[];start=time.time()
    for n in range(2000,3601):
        for h in [1,-1]:
            best=None
            for phase in np.arange(8)*2*np.pi/8:
                for shift in [-.25,.25]:
                    p=np.array([phase,shift,0,0,89,0]+[0]*8)
                    _,cost,*_=assign(Model(n,h,p),train)
                    score=float(cost@weights(train))
                    if best is None or score<best['train_score']: best=dict(n=n,h=h,p=p.tolist(),train_score=score)
            results.append(best)
        if n%100==0:
            print('scan',n,'elapsed',round(time.time()-start),flush=True)
            save(out/'scan.json',results)
    save(out/'scan.json',results)


def refine(out):
    rows=data();train=[r for r in rows if r['split']=='train'];scan=json.loads((out/'scan.json').read_text())
    # A common union of three separated minima per hand plus old hypotheses and
    # FFT vicinity. Same count set and budgets for both signs.
    counts={2698,2700,2833,2679}
    for h in [1,-1]:
        selected=[]
        for r in sorted((r for r in scan if r['h']==h),key=lambda r:r['train_score']):
            if all(abs(r['n']-n)>20 for n in selected): selected.append(r['n'])
            if len(selected)==3:break
        counts.update(selected)
    results=[]
    for n in sorted(counts):
        for h in [1,-1]:
            base=next(r for r in scan if r['n']==n and r['h']==h)['p'];trials=[]
            for el,roll in [(89,0),(80,0),(80,90)]:
                p=base.copy();p[4:6]=[el,roll]
                trials.append(fit(n,h,p,train))
            best=dict(min(trials,key=lambda x:x['train_score']));best['starts']=trials
            results.append(best); print('rigid',n,h,round(best['train_score'],4),flush=True)
            save(out/'rigid.json',results)
    # Refine neighboring integers around a matched common set of leading counts.
    promising=set()
    for h in [1,-1]:
        best=min((r for r in results if r['h']==h),key=lambda r:r['train_score']);promising.add(best['n'])
    for n in sorted({n+d for n in promising for d in [-3,-2,-1,1,2,3]}-counts):
        for h in [1,-1]:
            base=min((r for r in results if r['h']==h),key=lambda r:abs(r['n']-n))
            trials=[fit(n,h,base['p'],train),fit(n,h,next(r for r in scan if r['n']==n and r['h']==h)['p'],train)]
            best=dict(min(trials,key=lambda x:x['train_score']));best['starts']=trials
            results.append(best);print('neighbor',n,h,round(best['train_score'],4),flush=True)
            save(out/'rigid.json',results)
    leading={2698,2833}
    for h in [1,-1]:leading.add(min((r for r in results if r['h']==h),key=lambda r:r['train_score'])['n'])
    ablations=[]
    for n in sorted(leading):
        for h in [1,-1]:
            base=next(r for r in results if r['n']==n and r['h']==h)
            ablations.append({k:v for k,v in base.items() if k!='starts'})
            for kind in ['stretch','twist','both']:
                trial=fit(n,h,base['p'],train,kind,70);ablations.append(trial)
                print('deform',n,h,kind,round(trial['train_score'],4),flush=True)
            save(out/'ablations.json',ablations)


def exact_training_score(model, rows, groups):
    xy=np.array([[r['x'],r['y']] for r in rows]);ids,q,g,pc=candidates(model,xy)
    owner,_,unknown=rays(model,np.concatenate(groups),g)
    hist=[];cursor=0;dominant=[]
    for pts in groups:
        oo=owner[cursor:cursor+len(pts)];uu=unknown[cursor:cursor+len(pts)];cursor+=len(pts)
        v,c=np.unique(oo[(oo>=0)&(uu==0)],return_counts=True)
        hist.append({int(k):float(count/len(pts)) for k,count in zip(v,c)})
        dominant.append(int(v[np.argmax(c)]) if len(v) else -1)
    ids=np.column_stack((ids,np.where(np.array(dominant)>=0,dominant,ids[:,0])))
    delta=xy[:,None,:]-pc[ids];r,d,_=model.view.basis()
    axis=np.stack((g['tangent']@r,g['tangent']@d),axis=1)[ids];along=np.sum(delta*axis,axis=2)
    q=(np.sum(delta*delta,axis=2)+.51/(1-.51*np.sum(axis*axis,axis=2))*along*along)/(RADIUS*model.view.scale)**2
    support=np.array([[hist[i].get(int(k),0.) for k in ks] for i,ks in enumerate(ids)])
    cost=(1-support+.15*q)*weights(rows)[:,None]
    unique=np.unique(ids);matrix=np.full((len(rows),len(unique)),1e5)
    matrix[np.arange(len(rows))[:,None],np.searchsorted(unique,ids)]=cost
    a,b=linear_sum_assignment(matrix)
    return float(matrix[a,b].sum()+np.sum(penalties(model.p)**2))


def polish(out):
    rows=data();train=[r for r in rows if r['split']=='train'];groups,_=patch_points(train)
    # Deterministically spread up to9 samples across each saved positive patch.
    # All original pixels remain in the later independent full-patch audit.
    groups=[p[np.unique(np.linspace(0,len(p)-1,min(9,len(p))).astype(int))] for p in groups]
    trials=json.loads((out/'ablations.json').read_text());rigid=json.loads((out/'rigid.json').read_text())
    if not any(t['n']==2679 for t in trials):
        for h in [1,-1]:
            base=next(r for r in rigid if r['n']==2679 and r['h']==h)
            trials.append({k:v for k,v in base.items() if k!='starts'})
            for kind in ['stretch','twist','both']:trials.append(fit(2679,h,base['p'],train,kind,70))
    # Retain a close lower-count basin and low/high-count density controls.
    scan_rows=json.loads((out/'scan.json').read_text())
    for n in [2312,2529,3592]:
        for h in [1,-1]:
            matches=[r for r in rigid if r['n']==n and r['h']==h]
            if matches:base=matches[0]
            else:
                start=next(r['p'] for r in scan_rows if r['n']==n and r['h']==h);starts=[]
                for el,roll in [(89,0),(80,0),(80,90)]:
                    p=start.copy();p[4:6]=[el,roll];starts.append(fit(n,h,p,train))
                base=dict(min(starts,key=lambda r:r['train_score']));base['starts']=starts
                save(out/f'control-{n}-{h:+d}.json',base)
            trials.append({k:v for k,v in base.items() if k!='starts'})
    results=json.loads((out/'polished.json').read_text()) if (out/'polished.json').exists() else []
    for trial in trials:
        if any(r['n']==trial['n'] and r['h']==trial['h'] and r['kind']==trial['kind'] for r in results):continue
        p=np.array(trial['p']);n=trial['n'];h=trial['h'];trace=[]
        best=exact_training_score(Model(n,h,p),train,groups);trace.append(dict(score=best,p=p.tolist()))
        for scale in [1.,.5]:
            for dim,step in [(0,np.radians(8)),(1,.15),(2,1.5),(3,1.5)]:
                options=[(best,p.copy())]
                for sign in [-1,1]:
                    q=p.copy();q[dim]=np.clip(q[dim]+sign*scale*step,LOW[dim],HIGH[dim])
                    score=exact_training_score(Model(n,h,q),train,groups);options.append((score,q));trace.append(dict(score=score,p=q.tolist()))
                best,p=min(options,key=lambda x:x[0])
        result=dict(trial);result.update(p=p.tolist(),proxy_fit_p=trial['p'],proxy_train_score=trial['train_score'],train_score=best,surface_polish_trials=trace)
        results.append(result);save(out/'polished.json',results);print('surface polish',n,h,trial['kind'],round(trace[0]['score'],4),'->',round(best,4),flush=True)


def metrics(values):
    v=np.asarray(values,float)
    return dict(count=len(v),mean=float(v.mean()),sse=float(v@v),rms=float(np.sqrt(np.mean(v*v))),median=float(np.median(v)),p90=float(np.percentile(v,90)),max=float(v.max()))


def patch_points(rows):
    inv=json.loads((ROOT/'photo2/review/r252/inventory.json').read_text());sources={r['key']:r for r in inv['sources']}
    groups=[];provenance=[]
    for row in rows:
        pts=[[row['x'],row['y']]];key=None
        # Only existing small R201 positive interiors; other alias masks may
        # contain acknowledged same-color merges and are not promoted to truth.
        for k in row['source_keys'].split(';'):
            source=sources[k]
            if source['source_file']=='photo2/review/r201/interiors.json':
                runs=source['original'].get('region',{}).get('pixel_runs',[])
                pp=np.array([(x,y) for y,lo,hi in runs for x in range(lo,hi+1)],float)
                if len(pp):
                    pts=np.vstack((pts,pp));key=k;break
        groups.append(np.array(pts));provenance.append(key)
    return groups,provenance


def audit_one(trial,rows,groups):
    n,h,p=trial['n'],trial['h'],trial['p'];model=Model(n,h,p)
    # Geometry was fitted on training only. Exact first-hit positive-patch
    # ownership now reranks identity alternatives, with one-to-one constraints.
    # Holdout assignment reserves identities already used by training.
    train_idx=np.array([i for i,r in enumerate(rows) if r['split']=='train']);test_idx=np.array([i for i,r in enumerate(rows) if r['split']=='test'])
    xy=np.array([[r['x'],r['y']] for r in rows]);ids,q,g,pc=candidates(model,xy)
    proxy_ids=np.empty(len(rows),int)
    for subset in [train_idx,test_idx]:
        proxy_ids[subset]=assign(model,[rows[i] for i in subset])[0]
    own,_,unknown=rays(model,xy,g)
    allp=np.concatenate(groups);po,_,pu=rays(model,allp,g)
    cursor=0;hist=[];dominant=[]
    for pts in groups:
        oo=po[cursor:cursor+len(pts)];uu=pu[cursor:cursor+len(pts)];cursor+=len(pts)
        v,c=np.unique(oo[(oo>=0)&(uu==0)],return_counts=True)
        hist.append({int(k):float(count/len(pts)) for k,count in zip(v,c)})
        dominant.append(int(v[np.argmax(c)]) if len(v) else -1)
    # Add exact owners even when the screening exposure cutoff rejected them.
    ids=np.column_stack((ids,np.where(own>=0,own,ids[:,0]),np.where(np.array(dominant)>=0,dominant,ids[:,0])))
    delta=xy[:,None,:]-pc[ids];r,d,_=model.view.basis()
    axis=np.stack((g['tangent']@r,g['tangent']@d),axis=1)[ids]
    along=np.sum(delta*axis,axis=2)
    q=(np.sum(delta*delta,axis=2)+.51/(1-.51*np.sum(axis*axis,axis=2))*along*along)/(RADIUS*model.view.scale)**2
    support_matrix=np.array([[hist[i].get(int(k),0.) for k in ks] for i,ks in enumerate(ids)])
    cost=1-support_matrix+.15*q
    assigned=np.empty(len(rows),int);used=[]
    for subset in [train_idx,test_idx]:
        unique=np.setdiff1d(np.unique(ids[subset]),used);matrix=np.full((len(subset),len(unique)),1e5)
        w=weights([rows[i] for i in subset])
        for i,ri in enumerate(subset):
            for j,k in enumerate(ids[ri]):
                col=np.searchsorted(unique,k)
                if col<len(unique) and unique[col]==k:matrix[i,col]=min(matrix[i,col],cost[ri,j]*w[i])
        a,b=linear_sum_assignment(matrix);assigned[subset]=unique[b];used.extend(unique[b].tolist())
    support=[hist[i].get(int(k),0.) for i,k in enumerate(assigned)]
    # Direct distance to first-visible pixels of each assigned body at 2px grid.
    # Membership rays are exact; nonzero distances have <=sqrt(2)*2px sampling
    # scale, NOT a certified error bound at arbitrarily narrow visible slivers.
    offsets=np.arange(-40,41,2);dx,dy=np.meshgrid(offsets,offsets);off=np.c_[dx.ravel(),dy.ravel()]
    success=(own==assigned)&(unknown==0)
    missing=np.flatnonzero(~success);distances=np.zeros(len(rows));censored=np.zeros(len(rows),bool)
    if len(missing):
        probes=(xy[missing,None,:]+off).reshape(-1,2);oo,_,uu=rays(model,probes,g)
        oo=oo.reshape(len(missing),-1);uu=uu.reshape(len(missing),-1)
        dd=np.where((oo==assigned[missing,None])&(uu==0),np.linalg.norm(off,axis=1)[None,:],np.inf).min(axis=1)
        censored[missing]=~np.isfinite(dd);dd[~np.isfinite(dd)]=np.sqrt(2)*40;distances[missing]=dd
    center=np.linalg.norm(xy-pc[assigned],axis=1)
    anchor_idx=next(i for i,r in enumerate(rows) if r['observation_id']==ANCHOR);origin=int(assigned[anchor_idx])
    records=[]
    for i,row in enumerate(rows):
        alternatives=sorted({int(k):float(c) for c,k in zip(cost[i],ids[i])}.items(),key=lambda z:z[1])[:4]
        alternatives=[(c,k) for k,c in alternatives]
        # Conditional uniqueness requires ray ownership, >=95% patch support,
        # and >=0.15 normalized assignment margin. Cross-model stability separate.
        chosen_cost=next((float(c) for c,k in zip(cost[i],ids[i]) if k==assigned[i]),1e5)
        other=min(float(c) for c,k in zip(cost[i],ids[i]) if k!=assigned[i])
        records.append(dict(**row,generator_index=int(assigned[i]),k=int((assigned[i]-origin)%n),
            screening_generator_index=int(proxy_ids[i]),projected_center=pc[assigned[i]].tolist(),center_distance_px=float(center[i]),surface_distance_px=float(distances[i]),
            surface_distance_censored=bool(censored[i]),first_owner=int(own[i]),ownership=bool(success[i]),unfinished=int(unknown[i]),
            patch_support=support[i],patch_dominant=dominant[i],conditional_unique=bool(success[i] and support[i]>=.95 and other-chosen_cost>=.15),
            alternatives=[dict(generator_index=int(k),k=int((k-origin)%n),exact_audit_cost=float(c)) for c,k in alternatives]))
    t=np.linspace(0,1,4096,endpoint=False);stretch=harmonics(t)@np.array(p[6:10]);tw=harmonics(t)@np.array(p[10:14]);ds,_=correction(t,np.array(p))
    a=2*np.pi*t;der=np.array([2*np.pi*np.cos(a),-2*np.pi*np.sin(a),4*np.pi*np.cos(2*a),-4*np.pi*np.sin(2*a)]).T@np.array(p[10:14])
    summary=dict(**{k:v for k,v in trial.items() if k!='starts'},model_id=f'N{n}_h{h:+d}_{trial["kind"]}',turns=model.source.nrows,q=n/model.source.nrows,origin_generator_index=origin,anchor=ANCHOR,
        stretch_max=float(abs(stretch).max()),stretch_rms=float(np.sqrt(np.mean(stretch**2))),longitudinal_displacement_max_px=float(abs(ds).max()*model.unscaled_length),twist_max_deg=float(np.degrees(abs(tw).max())),twist_rms_deg=float(np.degrees(np.sqrt(np.mean(tw**2)))),turn_rate_relative_max=float(abs(der/(2*np.pi*model.source.nrows)).max()),physical_scale_px_per_unit=model.view.scale,
        visible_surface_distance_censored=int(censored.sum()),unfinished_rays=int((unknown>0).sum()))
    for split in ['train','test','all']:
        ix=np.array([i for i,r in enumerate(rows) if split=='all' or r['split']==split]);w=weights([rows[i] for i in ix])
        summary[split]=dict(center=metrics(center[ix]),surface=metrics(distances[ix]),ownership=float(success[ix].mean()),patch_support=float(np.mean(np.array(support)[ix])),conditional_unique=sum(records[i]['conditional_unique'] for i in ix),balanced_center_rms=float(np.sqrt(w@(center[ix]**2))),balanced_surface_rms=float(np.sqrt(w@(distances[ix]**2))),balanced_patch_support=float(w@np.array(support)[ix]))
    summary['by_color']={c:dict(center=metrics(center[[i for i,r in enumerate(rows) if r['color']==c]]),surface=metrics(distances[[i for i,r in enumerate(rows) if r['color']==c]]),ownership=float(success[[i for i,r in enumerate(rows) if r['color']==c]].mean())) for c in ['red','yellow']}
    summary['by_sector']={str(s):dict(center=metrics(center[[i for i,r in enumerate(rows) if r['sector']==s]]),surface=metrics(distances[[i for i,r in enumerate(rows) if r['sector']==s]]),ownership=float(success[[i for i,r in enumerate(rows) if r['sector']==s]].mean())) for s in range(1,33)}
    summary['worst']=sorted(records,key=lambda r:r['surface_distance_px'],reverse=True)[:10]
    return summary,records,model,g


def full_visibility(model,g,step=2):
    pc=model.view.project(g['centers']);bound=RADIUS*np.sqrt(1+.7**2)*model.view.scale
    # Complete global image grid in conservative projected bounding squares.
    mask=np.zeros((int(3250/step),int(2600/step)),bool)
    for x,y in pc:
        x0,x1=np.floor([(x-bound)/step,(x+bound)/step]).astype(int)
        y0,y1=np.floor([(y-bound)/step,(y+bound)/step]).astype(int)
        mask[max(y0,0):min(y1+2,len(mask)),max(x0,0):min(x1+2,mask.shape[1])]=True
    yy,xx=np.where(mask);xy=np.c_[xx,yy]*step;own,_,unknown=rays(model,xy,g)
    valid=(own>=0)&(unknown==0);n=model.source.nbeads
    area=np.bincount(own[valid],minlength=n)*step**2
    sums=np.array([np.bincount(own[valid],weights=xy[valid,j],minlength=n) for j in [0,1]]).T
    centroid=sums/np.maximum(area[:,None]/step**2,1)
    # Isolated area quadrature in each bead's complete bound, using identical
    # global pixel lattice and all actual rounded annular geometry.
    isolated=np.zeros(n);isolated_unknown=np.zeros(n)
    for chunk in np.array_split(np.arange(n),max(1,n//80)):
        for k in chunk:
            x,y=pc[k];lo=np.floor((pc[k]-bound)/step).astype(int);hi=np.ceil((pc[k]+bound)/step).astype(int)
            xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)*step,np.arange(lo[1],hi[1]+1)*step);pts=np.c_[xx.ravel(),yy.ravel()]
            gg={key:value[[k]] for key,value in g.items()};oo,_,uu=first_hits(model,pts,gg)
            isolated[k]=np.sum((oo==k)&(uu==0))*step**2
            isolated_unknown[k]=np.sum(uu>0)*step**2
    fraction=area/np.maximum(isolated,1)
    possible=cKDTree(xy[unknown>0]).query_ball_point(pc,bound,return_length=True)*step**2 if np.any(unknown>0) else np.zeros(n)
    return dict(area=area,isolated=isolated,fraction=fraction,centroid=centroid,uncertain_area_bound=possible,isolated_uncertain_area=isolated_unknown,fraction_lower=area/np.maximum(isolated+isolated_unknown,1),fraction_upper=np.minimum(1,(area+possible)/np.maximum(isolated,1)),uncertain_rays=int((unknown>0).sum()),sampled_rays=len(xy))


def audit(out):
    rows=data();groups,provenance=patch_points(rows);save(out/'patch-provenance.json',dict(zip([r['observation_id'] for r in rows],provenance)))
    trials=json.loads((out/'polished.json').read_text());summaries=[]
    for trial in trials:
        mid=f'N{trial["n"]}_h{trial["h"]:+d}_{trial["kind"]}'
        path=out/f'{mid}-metrics.json'
        if path.exists(): summaries.append(json.loads(path.read_text()));continue
        summary,records,model,g=audit_one(trial,rows,groups)
        save(path,summary);save(out/f'{mid}-assignments.json',records);summaries.append(summary)
        print('audit',mid,'test surface',round(summary['test']['surface']['rms'],2),'ownership',round(summary['test']['ownership'],3),flush=True)
    save(out/'models.json',summaries)
    # Nominate on training only; heldout remains a disclosed evaluation, never
    # used to select geometry. Include both best rigid and best corrected hand.
    selected=[]
    for h in [1,-1]:
        for corrected in [False,True]:
            pool=[r for r in summaries if r['h']==h and (r['kind']!='rigid' if corrected else r['kind']=='rigid')]
            selected.append(min(pool,key=lambda r:r['train_score']))
    for h in [1,-1]:
        fft_model=next(r for r in summaries if r['n']==2679 and r['h']==h and r['kind']=='rigid')
        if fft_model not in selected:selected.append(fft_model)
    save(out/'selected.json',[r['model_id'] for r in selected])
    for summary in selected:
        mid=summary['model_id'];model=Model(summary['n'],summary['h'],summary['p']);g=model.geometry(np.arange(summary['n']))
        records=json.loads((out/f'{mid}-assignments.json').read_text());visibility=full_visibility(model,g)
        pc=model.view.project(g['centers']);op=model.view.project(g['outward']);origin=summary['origin_generator_index'];pred=[]
        for j in range(summary['n']):
            k=(j-origin)%summary['n'];v=k//7;u=k-7*v;vb=k//6;ub=6*vb-k
            associated=[r for r in records if r['generator_index']==j]
            frac=visibility['fraction'][j];area=visibility['area'][j]
            pred.append(dict(model_id=mid,h=summary['h'],generator_index=j,k=k,reverse_k=(-k)%summary['n'],
                chart_A_u=u,chart_A_v=v,chart_B_u=ub,chart_B_v=vb,
                center_x=pc[j,0],center_y=pc[j,1],outward_x=op[j,0],outward_y=op[j,1],
                visible_x=visibility['centroid'][j,0] if area else None,visible_y=visibility['centroid'][j,1] if area else None,
                area_px2=int(area),isolated_area_px2=int(visibility['isolated'][j]),visible_fraction=float(frac),
                meaningfully_visible=bool(frac>=.10 and area>=24),geometrically_distinguishable=bool(frac>=.25 and area>=80),
                observation_id=';'.join(r['observation_id'] for r in associated),
                status='conditional_color_supported' if any(r['ownership'] and r['patch_support']>=.95 for r in associated) else ('unresolved_association' if associated else 'geometry_prediction'),
                observed_color=';'.join(r['color'] for r in associated if r['ownership'] and r['patch_support']>=.95),predicted_color='unknown'))
        table(out/f'{mid}-predictions.csv',pred)
        counts=dict(model_id=mid,n=summary['n'],meaningfully_visible=sum(r['meaningfully_visible'] for r in pred),geometrically_distinguishable=sum(r['geometrically_distinguishable'] for r in pred),any_sampled_surface=int((visibility['area']>0).sum()),uncertain_rays=visibility['uncertain_rays'],sampled_rays=visibility['sampled_rays'],threshold_sensitivity={str(f):int(((visibility['fraction']>=f)&(visibility['area']>=24)).sum()) for f in [.05,.1,.2,.25,.4]},criteria='meaningful >=10% isolated projected area AND >=24px2; distinguishable proxy >=25% AND >=80px2; actual photographic identifiability unmeasured')
        save(out/f'{mid}-visibility.json',counts);print('visible',counts,flush=True)
    figures(out)


def figures(out):
    rows=data();scan=json.loads((out/'scan.json').read_text());models=json.loads((out/'models.json').read_text());selected=json.loads((out/'selected.json').read_text())
    fig,ax=plt.subplots(figsize=(12,4))
    for h,c in [(1,'tab:blue'),(-1,'tab:orange')]:
        rr=[r for r in scan if r['h']==h];ax.plot([r['n'] for r in rr],[r['train_score'] for r in rr],lw=.6,label=f'h={h:+d}',color=c)
    ax.set(xlabel='Total physical beads N (every integer)',ylabel='Balanced dimensionless screening score');ax.legend();fig.tight_layout();fig.savefig(out/'count-scan.png',dpi=170);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(13,4))
    for h,c in [(1,'tab:blue'),(-1,'tab:orange')]:
        for kind,marker in [('rigid','o'),('stretch','s'),('twist','^'),('both','x')]:
            rr=[r for r in models if r['h']==h and r['kind']==kind]
            axs[0].scatter([r['n'] for r in rr],[r['train_score'] for r in rr],c=c,marker=marker,label=f'{h:+d} {kind}')
            axs[1].scatter([r['n'] for r in rr],[r['test']['balanced_surface_rms'] for r in rr],c=c,marker=marker)
    axs[0].set(xlabel='N',ylabel='Penalized training surface score');axs[0].legend(fontsize=7,ncol=2);axs[1].set(xlabel='N',ylabel='Heldout balanced visible-surface RMS (px)');fig.tight_layout();fig.savefig(out/'leading-models.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(3,1,figsize=(12,9));t=np.linspace(0,1,1000)
    for mid in selected:
        m=next(r for r in models if r['model_id']==mid);p=np.array(m['p']);rr=json.loads((out/f'{mid}-assignments.json').read_text())
        axs[0].plot([r['arc_fraction']*9235.586 for r in rr],[r['surface_distance_px'] for r in rr],'.',ms=2,label=mid)
        mm=Model(m['n'],m['h'],p);f=mm.geometry(t*m['n'])['fraction'];uu=np.interp(f,mm.arc_fraction,mm.u_table);image_arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(mm.seed_image_curve,axis=0),axis=1))];ss=np.interp(uu,mm.u_table,image_arc);order=np.argsort(ss)
        axs[1].plot(ss[order],(harmonics(t)@p[6:10]*100)[order],label=mid);axs[2].plot(ss[order],np.degrees(harmonics(t)@p[10:14])[order],label=mid)
    for ax,label in zip(axs,['Visible-surface residual (px)','Longitudinal spacing correction (%)','Extra winding phase (degrees)']):ax.set(xlabel='Image centerline arc length (pixels)',ylabel=label);ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(out/'residuals-corrections.png',dpi=170);plt.close(fig)
    image=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    overlay_images={}
    for mid in selected:
        pred=list(csv.DictReader((out/f'{mid}-predictions.csv').open()));rr=json.loads((out/f'{mid}-assignments.json').read_text());im=image.copy();draw=ImageDraw.Draw(im)
        for r in pred:
            if r['meaningfully_visible']=='True':
                x,y=float(r['visible_x']),float(r['visible_y']);draw.ellipse((x-3,y-3,x+3,y+3),outline=(0,235,255),width=1)
        for r in rr:
            x,y=r['x'],r['y'];color=(255,40,40) if r['color']=='red' else (255,235,20)
            draw.rectangle((x-2,y-2,x+2,y+2),fill=color)
            if r['surface_distance_px']>6:draw.line((x,y,*r['projected_center']),fill=(255,0,255),width=2)
        draw.rectangle((0,0,2540,35),fill=(0,0,0));draw.text((10,8),mid+' | cyan: predicted visible centroid; red/yellow: observed interiors; magenta: >6px surface mismatch',font=font,fill='white')
        im.save(out/f'{mid}-whole.png');overlay_images[mid]=im
    # Matched raw / both-hand crops at anchor and diverse image orientations.
    best=[next(mid for mid in selected if f'h{h:+d}' in mid and not mid.endswith('_rigid')) for h in [1,-1]]
    for name,box in [('anchor',(1220,190,1440,390)),('right',(2160,1510,2390,1750)),('bend',(1650,1540,1890,1800)),('left',(140,1000,410,1240)),('bottom-mismatch',(1320,2880,1590,3150))]:
        canvas=Image.new('RGB',((box[2]-box[0])*3,(box[3]-box[1])+35),'white');d=ImageDraw.Draw(canvas)
        for col,mid in enumerate(['raw']+best):
            crop=(image if mid=='raw' else overlay_images[mid]).crop(box);cd=ImageDraw.Draw(crop)
            if mid!='raw':
                rr=json.loads((out/f'{mid}-assignments.json').read_text())
                for r in rr:
                    if box[0]<r['x']<box[2] and box[1]<r['y']<box[3]:
                        nn=next(m['n'] for m in models if m['model_id']==mid)
                        kk=r['k'] if r['k']<=nn//2 else r['k']-nn
                        label='C:0' if r['observation_id']==ANCHOR else str(kk)
                        cd.text((r['x']-box[0]+4,r['y']-box[1]+3),label,font=font,fill='lime' if r['observation_id']==ANCHOR else 'white',stroke_width=1,stroke_fill='black')
            canvas.paste(crop,(col*crop.width,35));d.text((col*crop.width+4,8),mid,font=font,fill='black')
        canvas.resize((canvas.width*2,canvas.height*2)).save(out/f'crop-{name}.png')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['scan','refine','polish','audit','figures']);parser.add_argument('--output',type=Path,default=OUT);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    globals()[args.stage](args.output)

if __name__=='__main__': main()
