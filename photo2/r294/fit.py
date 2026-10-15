"""Shared-pose initial fit and a diagnosed, regularized revision.

Only frozen training observations are read by the objective. The proxy is an
initializer; final ranking uses literal annular first-hit support, with unmatched
legacy observations and separate many-patch unresolved physical ownership.
"""
import argparse
from copy import deepcopy
import numpy as np
from scipy.optimize import linear_sum_assignment
from photo2.r282.phase1 import image_features
from photo2.r293.geometry import Reference
from .common import *
from .geometry import Chain,nominal

def sample(region,n):
    xy=pixels(region)
    return xy[np.linspace(0,len(xy)-1,min(n,len(xy))).astype(int)]

class Objective:
    def __init__(self,inputs,split='train',revised=False):
        self.inputs=inputs;self.revised=revised
        self.rows=[r for r in inputs['records'] if r['fit_eligible'] and r['split']==split]
        self.old=[r for r in inputs['legacy_colored'] if r['fit_eligible'] and r['split']==split and r['source']['record_id']!=inputs['anchor']['record_id']]
        self.groups=[sample(r['source']['native_bright_patch'],8) for r in self.rows]
        self.legacy=[sample(r['source']['measured_support'],20) for r in self.old]
        self.anchor=sample(inputs['anchor']['measured_support'],48)
        self.xy=np.concatenate(self.groups+self.legacy+[self.anchor]);self.sizes=[len(g) for g in self.groups+self.legacy+[self.anchor]]
        self.centroids=np.array([r['source']['measured_photo_location'] for r in self.old])
        self.calls=0
        if revised:
            _,rgb,_=photo();f=image_features(rgb)
            ref=Reference();aa=np.arange(-60,751,5);j=np.searchsorted(ref.arc,(inputs['arc0']+inputs['direction']*aa)%ref.length)-1
            tangent=ref.delta[j]/ref.lengths[j,None];normal=np.c_[-tangent[:,1],tangent[:,0]]
            line=np.c_[*[np.interp((inputs['arc0']+inputs['direction']*aa)%ref.length,ref.arc,ref.points[:,k]) for k in range(2)]]
            pts=line[:,None,:]+np.arange(-55,56,5)[None,:,None]*normal[:,None,:]
            train=(np.floor((aa+60)/120).astype(int)%4!=2) if split=='train' else (np.floor((aa+60)/120).astype(int)%4==2)
            self.paper_xy=pts[train].reshape(-1,2)
            ix=np.rint(self.paper_xy).astype(int);self.paper=f['paper'][ix[:,1],ix[:,0]]

    def proxy(self,p):
        s=Chain(p,self.inputs);visible=s.g['radial']@s.eye>-.1
        pc=s.pc[visible];cost=np.linalg.norm(self.centroids[:,None,:]-pc[None,:,:],axis=2)
        cost=np.minimum(cost,18)**2
        a,b=linear_sum_assignment(np.c_[cost,np.full((len(cost),len(cost)),18**2)])
        v=float(cost[a[b<len(pc)],b[b<len(pc)]].sum()+18**2*np.sum(b>=len(pc)))/max(len(cost),1)
        anchor=s.pc[s.indices==0][0]
        return v+.6*np.sum((anchor-self.inputs['anchor']['measured_photo_location'])**2)

    def assess(self,p,details=False):
        self.calls+=1;s=Chain(p,self.inputs);d=s.trace(self.xy);owner=d['owner'];offset=0;hist=[]
        for size in self.sizes:
            ids,co=np.unique(owner[offset:offset+size],return_counts=True)
            hist.append({int(k):float(v/size) for k,v in zip(ids,co) if k>=0});offset+=size
        patch=np.array([max(h.values(),default=0.) for h in hist[:len(self.groups)]])
        hh=hist[len(self.groups):-1];matrix=np.zeros((len(hh),s.n))
        for i,h in enumerate(hh):
            for k,v in h.items():matrix[i,k]=v
        # A match must explain >=30% sampled support or remain unmatched.
        aa,bb=linear_sum_assignment(np.c_[1-matrix,np.full((len(hh),len(hh)),.7)])
        fraction=np.zeros(len(hh));mapping=np.full(len(hh),-999,int)
        good=bb<s.n;fraction[aa[good]]=matrix[aa[good],bb[good]];mapping[aa[good]]=s.indices[bb[good]]
        z=int(np.flatnonzero(s.indices==0)[0]);anchor=hist[-1].get(z,0.)
        paper=0.
        if self.revised:
            o=s.trace(self.paper_xy)['owner'];ok=o>=0
            paper=float(self.paper[ok].mean()) if ok.any() else 1.
        reg=.3*np.mean(np.asarray(p['strain'])**2)+.001*np.mean(np.asarray(p['bend'])**2)
        score=.42*float(patch.mean())+.42*float(fraction.mean())+.16*anchor-.22*paper-reg
        if anchor<.7:score-=.6*(.7-anchor)
        result=dict(score=score,patch_containment=float(patch.mean()),legacy_one_to_one_containment=float(fraction.mean()),
            anchor_containment=anchor,predicted_paper_fraction=paper,regularization=reg)
        if details:result.update(patch_fractions=patch.tolist(),legacy_fractions=fraction.tolist(),legacy_mapping=mapping.tolist())
        return result

def valid(p):
    return (6.5<=p['scale']<=11.5 and 1.10<=p['pitch']<=1.65 and 55<=p['elevation']<=90
        and abs(p['phase'])<=.85 and abs(p['s0'])<=18
        and max(abs(np.array(p['strain'])))<=.12 and max(abs(np.array(p['bend'])))<=8)

def refine(obj,start,revised=False):
    p=deepcopy(start);initial=obj.assess(p);best=initial['score'];history=[]
    keys=[('scale',.22),('pitch',.025),('elevation',4.),('phase',.08),('s0',1.5)]
    if revised:keys+=[(f'strain{j}',.025) for j in range(5)]+[(f'bend{j}',1.5) for j in range(5)]
    for step in (1.,.5,.25):
        for iteration in range(2):
            changed=False
            for key,delta in keys:
                options=[]
                for sign in (-1,1):
                    q=deepcopy(p)
                    if key.startswith('strain'):q['strain'][int(key[-1])]+=sign*delta*step
                    elif key.startswith('bend'):q['bend'][int(key[-1])]+=sign*delta*step
                    else:q[key]+=sign*delta*step
                    if valid(q):options.append((obj.assess(q)['score'],q))
                if options:
                    v,q=max(options,key=lambda o:o[0])
                    if v>best+1e-10:p=q;best=v;changed=True
            history.append(dict(step=step,iteration=iteration,parameters=deepcopy(p),metrics=obj.assess(p)))
            if not changed:break
    return dict(parameters=p,train=obj.assess(p,True),initial=initial,history=history)

def initial(inputs):
    obj=Objective(inputs);coarse=[]
    for hand in (-1,1):
        for scale in (7.2,8.3,9.4,10.5):
            for pitch in (1.12,1.26,1.40,1.54):
                for elevation in (60.,75.,90.):
                    for phase in (-.35,0.,.35):
                        p=nominal(hand);p.update(scale=scale,pitch=pitch,elevation=elevation,phase=phase)
                        coarse.append(dict(parameters=p,proxy_mse=obj.proxy(p)))
        print('coarse hand',hand,flush=True)
    candidates=[]
    for hand in (-1,1):
        pool=sorted([r for r in coarse if r['parameters']['hand']==hand],key=lambda r:r['proxy_mse'])
        short=pool[:6]
        # Preserve spacing aliases instead of allowing one proxy basin to monopolize starts.
        for pitch in (1.12,1.26,1.40,1.54):
            r=next(r for r in pool if r['parameters']['pitch']==pitch)
            if r not in short:short.append(r)
        for i,r in enumerate(short):
            q=refine(obj,r['parameters']);q['proxy_start']=r;candidates.append(q)
            print('initial',hand,i,{k:round(v,3) for k,v in q['train'].items() if isinstance(v,float)},flush=True)
    selected=max(candidates,key=lambda r:r['train']['score'])
    save(OUT/'initial.json',dict(selected=selected,candidates=candidates,coarse=coarse,
        training_only=True,input_sha256=sha(EVIDENCE/'inputs.json.gz'),source_hashes=source_hashes()))
    print('selected initial',selected['parameters'],selected['train']['score'],flush=True)

def revised(inputs):
    assert (BASE/'checkpoints/initial-diagnosis.json').exists(),'Diagnose before revising'
    previous=read(OUT/'initial.json');obj=Objective(inputs,revised=True);candidates=[]
    for hand in (-1,1):
        pool=sorted([r for r in previous['candidates'] if r['parameters']['hand']==hand],key=lambda r:r['train']['score'],reverse=True)[:2]
        for r in pool:
            q=refine(obj,r['parameters'],True);q['initial_parameters']=r['parameters'];candidates.append(q)
            print('revised',hand,q['parameters'],q['train']['score'],flush=True)
    unconstrained=max(candidates,key=lambda r:r['train']['score'])
    for r in candidates:r['contact']=Chain(r['parameters'],inputs).certify()
    feasible=[r for r in candidates if r['contact']['certified']]
    assert feasible, 'No revised candidate passes physical nonintersection'
    selected=max(feasible,key=lambda r:r['train']['score'])
    save(OUT/'revised.json',dict(selected=selected,candidates=candidates,training_only=True,
        input_sha256=sha(EVIDENCE/'inputs.json.gz'),source_hashes=source_hashes(),
        unconstrained_winner=unconstrained,
        selection_rule='Highest training score among candidates with analytic nonintersection certificates; failures retained. Added after first unconstrained result failed physical audit, with no parameter refitting.',
        diagnosis_sha256=sha(BASE/'checkpoints/initial-diagnosis.json')))

def physical_selection(inputs):
    # Deterministic post-fit feasibility audit. It does not read held-out outcomes.
    raw=read(BASE/'checkpoints/unconstrained-revision/revised.json')
    raw['unconstrained_winner']=deepcopy(raw['selected'])
    for r in raw['candidates']:r['contact']=Chain(r['parameters'],inputs).certify()
    feasible=[r for r in raw['candidates'] if r['contact']['certified']]
    assert feasible
    raw['selected']=max(feasible,key=lambda r:r['train']['score'])
    raw['selection_rule']='Highest training score with a nonintersection certificate; no parameter refit. Unconstrained first result and exposed evaluation retained in checkpoints/unconstrained-revision.'
    raw['source_hashes']=source_hashes()
    save(OUT/'revised.json',raw)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['initial','revised','physical-selection']);a=p.parse_args()
    inputs=read(EVIDENCE/'inputs.json.gz');{'initial':initial,'revised':revised,'physical-selection':physical_selection}[a.stage](inputs)
if __name__=='__main__':main()
