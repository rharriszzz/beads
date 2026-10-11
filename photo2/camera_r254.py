"""Matched bounded pinhole fits with unchanged projected spline and identity charts.

Screening residual is an engineering guide, NOT calibrated surface likelihood.
All final ownership is rechecked against the literal rounded annulus.
"""
from __future__ import annotations
import argparse, csv, json, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.optimize import least_squares, linear_sum_assignment
from scipy.spatial import cKDTree
import global_fit_r253 as old
from curved_surface_fit import sdf
from pattern_r254 import OUT, OLD, diagnostic


class Camera(old.View):
    focal:float=0.
    def project(self,xyz):
        xyz=np.asarray(xyz);r,d,e=self.basis();den=1-self.scale*(xyz@e)/self.focal if self.focal else np.ones(len(xyz))
        return np.c_[xyz@r,xyz@d]*self.scale/den[:,None]+[self.tx,self.ty]
    def directions(self,xy):
        r,d,e=self.basis();v=np.broadcast_to(e,(len(xy),3)).copy()
        if self.focal:v-=((xy[:,0]-self.tx)[:,None]*r+(xy[:,1]-self.ty)[:,None]*d)/self.focal
        return v/np.linalg.norm(v,axis=1)[:,None]


class Model(old.Model):
    def __init__(self,n,h,p,focal=0.,turn_delta=0):
        super().__init__(n,h,p)
        v=self.view;self.view=Camera(v.elevation,v.roll,v.tx,v.ty,v.scale);self.view.focal=focal
        self.turns=self.source.nrows+turn_delta
        self.source=SimpleNamespace(nbeads=n,nrows=self.turns,helicity=h)
        r,d,e=self.view.basis();A=np.array([r[:2],d[:2]]);P=self.seed_image_curve-[1269.5,1590.5]
        mat=np.broadcast_to(A,(len(P),2,2)).copy()
        if focal:mat+=P[:,:,None]*e[None,None,:2]/focal
        plane=np.linalg.solve(mat,P[...,None])[...,0]
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
        self.view.scale=arc[-1]/(old.ROW*self.turns);self.unscaled_length=arc[-1]
        self.arc_fraction=arc/arc[-1];self.plane=plane/self.view.scale
        der=np.gradient(self.plane,axis=0);self.tangent=der/np.linalg.norm(der,axis=1)[:,None]
    def geometry(self,indices):
        ii=np.atleast_1d(indices).astype(float);t=ii/self.source.nbeads;ds,tw=old.correction(t,self.p)
        f=(t+self.p[1]/self.source.nbeads+ds)%1
        xy=np.c_[np.interp(f,self.arc_fraction,self.plane[:,0]),np.interp(f,self.arc_fraction,self.plane[:,1])]
        tt=np.c_[np.interp(f,self.arc_fraction,self.tangent[:,0]),np.interp(f,self.arc_fraction,self.tangent[:,1])]
        tt/=np.linalg.norm(tt,axis=1)[:,None];tangent=np.c_[tt,np.zeros(len(ii))];normal=np.c_[-tt[:,1],tt[:,0],np.zeros(len(ii))]
        angle=self.p[0]+self.source.helicity*2*np.pi*self.turns*t+tw
        radial=np.sin(angle)[:,None]*normal;radial[:,2]=np.cos(angle);line=np.c_[xy,np.zeros(len(ii))]
        return dict(indices=ii.astype(int),line=line,tangent=tangent,normal=normal,radial=radial,centers=line+4*radial,outward=line+(4+old.RADIUS)*radial,fraction=f)


def rays(model,xy,g=None):
    xy=np.asarray(xy,float)
    if len(xy)>4000:
        parts=[rays(model,xy[i:i+4000],g) for i in range(0,len(xy),4000)]
        return tuple(np.concatenate([p[j] for p in parts]) for j in range(3))
    if g is None:g=model.geometry(np.arange(model.source.nbeads))
    c=g['centers'];v=model.view;bound=old.RADIUS*np.sqrt(1+.7**2);pc=v.project(c)
    radius=bound*v.scale+1e-4
    if v.focal:
        den=1-v.scale*(c@v.basis()[2])/v.focal
        radius=bound*v.scale*(1+np.max(np.linalg.norm(pc-[v.tx,v.ty],axis=1))/v.focal)/(den.min()-bound*v.scale/v.focal)+1e-4
    nearby=cKDTree(pc).query_ball_point(xy,radius)
    a=np.repeat(np.arange(len(xy)),[len(x) for x in nearby]);b=np.array([k for x in nearby for k in x],int)
    best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),int)
    if not len(a):return owner,best,unknown
    base=v.base(xy);ray=v.directions(xy);delta=base[a]-c[b];u=ray[a];middle=-np.sum(delta*u,axis=1)
    perp=np.sum(delta**2,axis=1)-middle**2;keep=perp<bound**2
    a,b,delta,u,middle,perp=[x[keep] for x in (a,b,delta,u,middle,perp)]
    half=np.sqrt(np.maximum(bound**2-perp,0));depth=middle+half;end=middle-half
    local=np.c_[np.sum(delta*g['tangent'][b],axis=1),np.sum(delta*g['normal'][b],axis=1),delta[:,2]]
    direction=np.c_[np.sum(u*g['tangent'][b],axis=1),np.sum(u*g['normal'][b],axis=1),u[:,2]]
    alive=np.ones(len(a),bool);hit=np.zeros(len(a),bool);eps=1e-5
    for _ in range(600):
        ix=np.flatnonzero(alive)
        if not len(ix):break
        distance=sdf(local[ix]+depth[ix,None]*direction[ix]);yes=distance<eps
        hit[ix[yes]]=True;alive[ix[yes]]=False;moving=ix[~yes];depth[moving]-=np.maximum(distance[~yes],eps);alive[moving[depth[moving]<end[moving]]]=False
    np.add.at(unknown,a[alive],1);np.maximum.at(best,a[hit],depth[hit]);front=hit&(depth>=best[a]-eps/2);owner[a[front]]=g['indices'][b[front]]
    return owner,best,unknown


def maker_chart():
    rr=list(csv.DictReader((OLD/'maker-local-chart.csv').open()))
    for r in rr:
        for k in ['x','y']:r[k]=float(r[k])
        for k in ['maker_number','k_A','k_B']:r[k]=int(r[k])
    return rr


def stars(rows):
    result={}
    for sector in range(1,33):
        if sector%4==0:continue
        rr=[r for r in rows if r['sector']==sector and r['conditional_unique']]
        if not rr:continue
        seed=max(rr,key=lambda r:min(a['exact_audit_cost'] for a in r['alternatives'] if a['k']!=r['k']))
        near=sorted(rr,key=lambda r:(r['x']-seed['x'])**2+(r['y']-seed['y'])**2)[:3]
        for r in near:
            if np.hypot(r['x']-seed['x'],r['y']-seed['y'])<=90:result[r['observation_id']]=r['generator_index']
    return result


def fit(base,focal,rows,max_nfev=20,turn_delta=0):
    p=np.array(base['p']);p[0]-=base['h']*2*np.pi*turn_delta*base['origin_generator_index']/base['n'];train=[r for r in rows if r['split']=='train'];fixed=stars(rows);chart=maker_chart();family='A' if base['h']==1 else 'B';origin=base['origin_generator_index'];n=base['n'];h=base['h']
    # Withhold every fourth maker target (except the anchor); colors of spatial
    # test sectors never enter fitting. Graph holdout is relational, not a new photo.
    mc=[r for r in chart if r['maker_number']%4 or r['maker_number']==20]
    target=np.array([(origin+r['k_'+family])%n for r in mc]);xy=np.array([[r['x'],r['y']] for r in train]);mxy=np.array([[r['x'],r['y']] for r in mc])
    # Fixed R253 stars are conditional identity hypotheses, not new maker facts.
    active=np.arange(14);lo=old.LOW.copy();hi=old.HIGH.copy()
    # Keep geometry changes modest, while preserving existing bounded corrections.
    lo=np.maximum(lo,p-np.r_[.7,.8,5,5,8,35,[.0015]*4,[.04]*4]);hi=np.minimum(hi,p+np.r_[.7,.8,5,5,8,35,[.0015]*4,[.04]*4])
    p=np.clip(p,lo+1e-9,hi-1e-9);history=[]
    for iteration in range(2):
        model=Model(n,h,p,focal,turn_delta)
        options,q,gg,pc=old.candidates(model,xy)
        available=sorted(set(options.ravel())|set(fixed.values()));columns={k:j for j,k in enumerate(available)}
        matrix=np.full((len(train),len(available)),1e6);reserved=set(fixed.values());train_weights=old.weights(train)
        for i,r in enumerate(train):
            key=r['observation_id']
            if key in fixed:
                matrix[i,columns[fixed[key]]]=0.
            else:
                for k,qq in zip(options[i],q[i]):
                    if k not in reserved:matrix[i,columns[k]]=(max(np.sqrt(qq)-.85,0)**2+.15*qq)*train_weights[i]
        aa,bb=linear_sum_assignment(matrix)
        if np.any(matrix[aa,bb]>=1e6):raise RuntimeError('Identity constrained candidate graph exhausted')
        ids=np.array(available)[bb]
        def fun(pp):
            mm=Model(n,h,pp,focal,turn_delta);gg=mm.geometry(ids);pc=mm.view.project(gg['centers']);v=(xy-pc)/(old.RADIUS*mm.view.scale);w=np.sqrt(old.weights(train));q=np.linalg.norm(v,axis=1)
            mg=mm.geometry(target);mv=(mxy-mm.view.project(mg['centers']))/(old.RADIUS*mm.view.scale)
            # A separate chart term enforces local identity; the target is a
            # positive surface point, so weak center preference remains explicit.
            return np.r_[(v*w[:,None]*np.sqrt(.15)).ravel(),np.maximum(q-.85,0)*w,
                         .35*mv.ravel()/np.sqrt(len(mc)),old.penalties(pp)]
        res=least_squares(fun,p,bounds=(lo,hi),max_nfev=max_nfev,diff_step=1e-4,ftol=2e-4,xtol=2e-4,gtol=2e-4)
        p=res.x;history.append(dict(nfev=res.nfev,proxy_loss=float(res.fun@res.fun),status=int(res.status)))
    return dict(protocol_version=2,n=n,h=h,p=p.tolist(),focal=focal,turn_delta=turn_delta,base_model=base['model_id'],origin=origin,stars=fixed,iterations=history,chart_family=family)


def audit(trial,rows,groups):
    n=trial['n'];model=Model(n,trial['h'],trial['p'],trial['focal'],trial.get('turn_delta',0));g=model.geometry(np.arange(n));xy=np.array([[r['x'],r['y']] for r in rows]);ids,q,_,pc=old.candidates(model,xy)
    owner,_,un=rays(model,xy,g);po,_,pu=rays(model,np.concatenate(groups),g);hist=[];cursor=0
    for pts in groups:
        oo=po[cursor:cursor+len(pts)];uu=pu[cursor:cursor+len(pts)];cursor+=len(pts)
        vv,cc=np.unique(oo[(oo>=0)&(uu==0)],return_counts=True);hist.append({int(k):float(c/len(pts)) for k,c in zip(vv,cc)})
    opts=[]
    for i,r in enumerate(rows):
        choices=set(ids[i])|set(hist[i]);choices.add(int(owner[i])) if owner[i]>=0 else None
        if r['observation_id'] in trial['stars']:choices.add(trial['stars'][r['observation_id']])
        options=[]
        for k in choices:
            dist=float(np.linalg.norm(xy[i]-pc[k]));support=hist[i].get(int(k),0);cost=1-support+.15*(dist/(old.RADIUS*model.view.scale))**2
            options.append(dict(generator_index=int(k),k=int((k-trial['origin'])%n),exact_audit_cost=cost,patch_support=support,owns_representative=bool(k==owner[i] and un[i]==0)))
        opts.append(sorted(options,key=lambda a:a['exact_audit_cost']))
    chosen={};used=set()
    for split in ['train','test']:
        ii=[i for i,r in enumerate(rows) if r['split']==split];available=sorted(set(a['generator_index'] for i in ii for a in opts[i])-used);col={k:j for j,k in enumerate(available)};cost=np.full((len(ii),len(available)),1e6)
        for j,i in enumerate(ii):
            for a in opts[i]:
                k=a['generator_index']
                if k in col:
                    required=trial['stars'].get(rows[i]['observation_id'])
                    if required is not None and k!=required:continue
                    if required is None and k in trial['stars'].values():continue
                    cost[j,col[k]]=a['exact_audit_cost']
        aa,bb=linear_sum_assignment(cost)
        if np.any(cost[aa,bb]>=1e6):raise RuntimeError('Exact identity constrained candidate graph exhausted')
        for j,b in zip(aa,bb):chosen[ii[j]]=available[b];used.add(available[b])
    records=[]
    for i,r in enumerate(rows):
        a=next(a for a in opts[i] if a['generator_index']==chosen[i]);other=min(x['exact_audit_cost'] for x in opts[i] if x['generator_index']!=chosen[i])
        records.append(dict(**{k:r[k] for k in ['observation_id','x','y','color','sector','split']},**a,first_owner=int(owner[i]),unfinished=int(un[i]),alternatives=sorted({x['generator_index']:x for x in opts[i][:4]+[a]}.values(),key=lambda x:x['exact_audit_cost']),conditional_unique=bool(a['owns_representative'] and a['patch_support']>=.95 and other-a['exact_audit_cost']>=.15),old_k=r['k'],index_changed=a['k']!=r['k'],projected_center=pc[chosen[i]].tolist()))
    chart=maker_chart();mxy=np.array([[r['x'],r['y']] for r in chart]);mo,_,mu=rays(model,mxy,g);mt=np.array([(trial['origin']+r['k_'+trial['chart_family']])%n for r in chart]);success=(mo==mt)&(mu==0)
    metrics={}
    for split in ['train','test']:
        rr=[r for r in records if r['split']==split];ww=old.weights(rr)
        metrics[split]=dict(geometry_cost=float(ww@np.array([r['exact_audit_cost'] for r in rr])),ownership=sum(r['owns_representative'] for r in rr),patch_support=float(np.mean([r['patch_support'] for r in rr])),count=len(rr))
    anchor=next(r for r in records if r['observation_id']==old.ANCHOR)
    metrics.update(anchor_owned=bool(anchor['owns_representative'] and anchor['k']==0),chart_owned=int(success.sum()),chart_total=len(chart),chart_holdout_owned=int(sum(ok for r,ok in zip(chart,success) if not r['maker_number']%4 and r['maker_number']!=20)),chart_holdout_total=5,changed_indices=sum(r['index_changed'] for r in records),star_identity_retained=sum(r['generator_index']==trial['stars'][r['observation_id']] for r in records if r['observation_id'] in trial['stars']),star_total=len(trial['stars']),
                   chart_records=[dict(maker_number=r['maker_number'],target=int(k),owner=int(o),owned=bool(ok)) for r,k,o,ok in zip(chart,mt,mo,success)],
                   point_ownership_complete=all(r['owns_representative'] for r in records))
    return metrics,records


def run(out=OUT,budget=20):
    bases=json.loads((OLD/'models.json').read_text());results=[];summary=[];counts=[2312,2529,2670,2671,2679,2698,2833]
    for n in counts:
        for h in [1,-1]:
            # Matched rigid starts, both hands and all three cameras.
            base=next(b for b in bases if b['n']==n and b['h']==h and b['kind']=='rigid');rows=json.loads((OLD/f'{base["model_id"]}-assignments.json').read_text());groups,_=old.patch_points(rows)
            for focal in [0.,9598.350455236487,4799.175227618243]:
                mid=f'N{n}_h{h:+d}_f{round(focal)}';start=time.monotonic()
                if (out/f'{mid}-camera.json').exists() and json.loads((out/f'{mid}-camera.json').read_text()).get('protocol_version')==2:
                    trial=json.loads((out/f'{mid}-camera.json').read_text());metrics=trial['metrics'];metrics['chart_holdout_total']=5;records=json.loads((out/f'{mid}-assignments.json').read_text())
                else:
                    trial=fit(base,focal,rows,budget);metrics,records=audit(trial,rows,groups)
                trial.update(model_id=mid,metrics=metrics);old.save(out/f'{mid}-camera.json',trial);old.save(out/f'{mid}-assignments.json',records);results.append(trial)
                for subset in ['all','unique','train_unique']:
                    rr=[r for r in records if subset=='all' or r['conditional_unique'] and (subset!='train_unique' or r['split']=='train')]
                    dd=[diagnostic(rr,P,n) for P in range(1,400)];allowed=[d for d in dd if d['admissible_by_maker']];best=min(allowed,key=lambda d:(d['minimum_conflicting_assignments'],d['P']))
                    summary.append(dict(model_id=mid,subset=subset,count=len(rr),best_P=best['P'],min_conflicts=best['minimum_conflicting_assignments'],exact_periods=[d['P'] for d in dd if d['exact'] and d['admissible_by_maker']],admissible_periods=[d['P'] for d in allowed],period_conflicts=[d['minimum_conflicting_assignments'] for d in dd]))
                old.save(out/'camera-results.json',results);old.save(out/'camera-pattern-summary.json',summary)
                print(mid,'score',round(metrics['train']['geometry_cost'],4),'graph',metrics['chart_owned'],'anchor',metrics['anchor_owned'],'seconds',round(time.monotonic()-start),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ap.add_argument('--budget',type=int,default=20);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True);run(args.output,args.budget)
