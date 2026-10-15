"""Alternating bounded integer ownership beam and contact-constrained geometry.

All patch measurements survive; the region graph adds soft neighbor/color/valley
consistency, not assumed ownership truth. Several regions may share an owner.
"""
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from .common import *
from .geometry import Chain
from .fit import Objective,refine

def beam_assign(scene,rows,assignments,edges,width=24):
    records=[r for r in assignments if r['kind']=='region'];source={r['id']:r for r in rows};beams=[(0.,[])];ordering=[]
    for i,r in enumerate(records):
        options={a['index']:a['fraction'] for a in r['alternatives']};k=r['index']
        if k is not None:
            for delta in (-7,-6,-1,0,1,6,7):options.setdefault(k+delta,0.)
        options={j:v for j,v in options.items() if -20<=j<=200};options[None]=.28
        new=[]
        for score,indices in beams:
            for j,value in options.items():
                penalty=0.
                if j is not None:
                    for n,other in enumerate(indices):
                        if other is None:continue
                        edge=edges.get(tuple(sorted((r['id'],records[n]['id']))))
                        if edge is None:continue
                        if j==other:penalty+=edge['separation_weight']
                        else:
                            pred=scene.pc[j-scene.indices[0]]-scene.pc[other-scene.indices[0]]
                            observed=np.array(source[r['id']]['point'])-source[records[n]['id']]['point']
                            if pred@observed<0:penalty+=.12
                new.append((score+min(value,.9)/.9-penalty,indices+[j]))
        beams=sorted(new,key=lambda x:-x[0])[:width]
    return dict(score=float(beams[0][0]/max(1,len(records))),ids=[r['id'] for r in records],alternatives=[dict(score=float(s),indices=ix) for s,ix in beams[:6]])

class JointObjective(Objective):
    def __init__(self):
        super().__init__(version=2);self.edges={};_,rgb,_=photo();a=rgb.astype(float)/255;lum=a@np.array([.2126,.7152,.0722]);regions=[r for r in self.rows if r['kind']=='region']
        for i,r in enumerate(regions):
            for q in regions[:i]:
                start=np.array(r['point']);end=np.array(q['point']);distance=np.linalg.norm(start-end)
                if distance>58:continue
                xy=start+np.linspace(0,1,31)[:,None]*(end-start);v=ndi.map_coordinates(lum,[xy[:,1],xy[:,0]],order=1)
                # An observed valley strengthens distinct-owner preference, but
                # remains a soft cue because internal shading also has valleys.
                valley=float(np.clip(1-np.min(v[5:-5])/max(.02,min(np.median(v[:5]),np.median(v[-5:]))),0,1))
                weight=.35*(r['color']!=q['color'])+.18*max(0,valley-.25)
                self.edges[tuple(sorted((r['id'],q['id'])))]=dict(separation_weight=weight,valley=valley,distance=distance)
    def assess(self,p,physical=True,details=False):
        result=super().assess(p,physical,True)
        if result['feasible']:
            assignment=beam_assign(Chain(p,self.inputs),self.rows,result['assignments'],self.edges)
            frac=[r['containment'] for r in result['assignments'] if r['kind']=='region'];old=float(np.mean(np.minimum(frac,.9)/.9))
            result['independent_photo_score']=result['score'];result['score']+=.28*(assignment['score']-old);result['joint_assignment']=assignment
            if not details:result.pop('assignments')
        return result

def main():
    obj=JointObjective();pool=read(OUT/'revision.json')['candidates'];starts=[max([r for r in pool if r['parameters']['hand']==h],key=lambda r:r['train']['score']) for h in (1,-1)];candidates=[]
    keys=[('s0',.8),('phase',.05),('axial',.02)]+[(f'phase_knots:{j}',.04) for j in range(5)]+[(f'strain:{j}',.008) for j in range(5)]+[(f'bend:{j}',.5) for j in range(5)]
    for r in starts:
        fit=refine(obj,r['parameters'],keys,steps=(1.,.5));fit['family']=r['family'];candidates.append(fit)
        print('joint hand',r['parameters']['hand'],fit['train']['score'],'photographic',fit['train']['independent_photo_score'],flush=True)
    save(OUT/'joint.json',dict(candidates=candidates,selected=max(candidates,key=lambda r:r['train']['score']),edges=[dict(ids=list(k),**v) for k,v in obj.edges.items()],source_hashes=source_hashes(),training_only=True))
if __name__=='__main__':main()
