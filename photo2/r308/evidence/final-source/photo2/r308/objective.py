"""Grouped positive support, reverse contradictions, dense visible contours and optics.

Weights count regions/bodies, not correlated pixels. Automatic masks are positive
material, not certified individual beads. Fixed conditional owners define each
local numerical subproblem; alternative assignments remain explicit.
"""
import time
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import linear_sum_assignment
from scipy.ndimage import distance_transform_edt,binary_erosion,binary_dilation
from matplotlib.path import Path as Polygon
from photo2.r297.common import ROOT,read,pixels
from photo2.r297.geometry import reference
from photo2.r306.objective import match
from photo2.r307.fast import predict

def sample(xy,n):
    # Spatially spread deterministic sample, independent of the current model.
    if len(xy)<=n:return xy
    lo=xy.min(0);extent=np.maximum(1,xy.max(0)-lo);q=(xy-lo)/extent
    # Interleaved x/y rank avoids row-only thin slices.
    key=(q[:,0]*31).astype(int)*32+(q[:,1]*31).astype(int)
    order=np.lexsort((xy[:,0],xy[:,1],key))
    return xy[order[np.linspace(0,len(xy)-1,n).astype(int)]]

class Objective:
    def __init__(self,data,m,obs,split='development',dense=False):
        self.data=data;self.m=m;self.split=split;self.dense=dense
        self.obs=[r for r in obs if r['strong'] and r['split']==split]
        self.rows=[r for r in data['rows'] if r['kind']=='region' and not r['reflection'] and ((int(r['station']/data['length']*32)%4==3)==(split=='comparison'))]
        self.sections=np.array([int(r['station']/data['length']*32)%32 for r in self.rows])
        self.parts=[pixels(r['pixels']) if dense else sample(pixels(r['pixels']),256) for r in self.rows]
        self.bounds=np.r_[0,np.cumsum([len(x) for x in self.parts])];self.supportxy=np.concatenate(self.parts)
        self.confidence=[];self.policy=[]
        for r,pts in zip(self.rows,self.parts):
            # No model-derived single-bead labels. Acceptance is qualitative.
            compact=np.max(np.ptp(pixels(r['pixels']),axis=0))<=42 and r['pixels']['pixel_count']<=1000
            w=1. if r['accepted'] else .5 if compact else .12
            self.confidence.append(w);self.policy.append('qualitatively accepted' if r['accepted'] else 'compact automatic; uncertain owner' if compact else 'possible same-color merger; weak coherence')
        self.confidence=np.array(self.confidence)
        raw=np.load(ROOT/'photo2/r296/evidence/cues.npz');sec=(raw['station']/data['length']*32).astype(int)%32
        keep=((sec%4==3)==(split=='comparison'))
        if not dense:keep&=np.arange(len(sec))%2==0
        self.cues={k:raw[k][keep] for k in ['xy','color','paper']};self.cue_sections=sec[keep]
        self.separators=[r for r in read(ROOT/'photo2/r298/evidence/separators.json')['records'] if r['split']==split]
        self.contours=[]
        for r in m['beads']:
            if r['split']!=split:continue
            poly=np.asarray(r['polygon']);lo=np.floor(poly.min(0)-16).astype(int);hi=np.ceil(poly.max(0)+16).astype(int)
            step=1 if dense else 2;yy,xx=np.mgrid[lo[1]:hi[1]+1:step,lo[0]:hi[0]+1:step];xy=np.c_[xx.ravel(),yy.ravel()]
            inside=Polygon(poly).contains_points(xy,radius=.01).reshape(xx.shape)
            signed=(distance_transform_edt(~inside)-distance_transform_edt(inside))*step
            self.contours.append(dict(row=r,xy=xy,shape=xx.shape,inside=inside,signed=signed,step=step))
        self.envelopes=[r for r in m['envelope'] if r['fit_eligible'] and r['split']==split]
        # Three original transverse lanes preserve both sides; native final uses nine.
        self.envxy=np.concatenate([np.array(r['samples_xy']).reshape(9,191,2)[[2,4,6]].reshape(-1,2) for r in self.envelopes])
        self.xy=np.concatenate([self.supportxy,self.cues['xy']]+[np.array(r['xy']) for r in self.separators]+[r['xy'] for r in self.contours]+[self.envxy])
        self.obs_region=[]
        for o in self.obs:
            choices=[(cKDTree(pts).query(o['point'])[0],i) for i,(r,pts) in enumerate(zip(self.rows,self.parts)) if r['color']==o['color'] and np.linalg.norm(np.array(r['point'])-o['point'])<45]
            d,j=min(choices,default=(np.inf,-1));self.obs_region.append(j if d<=4 else -1)
        ref=reference();t=[]
        for o in self.obs:
            a=(o['arc']+np.array([-1,1]))%ref.length;v=np.array([[np.interp(u,ref.arc,ref.points[:,k]) for k in range(2)] for u in a]);v=v[1]-v[0];t.append(v/np.linalg.norm(v))
        self.tangents=np.array(t);self.last=None

    def evaluate(self,scene,anchors=None,step=2.,detail=False):
        began=time.monotonic();tr=scene.trace(self.xy);own=tr['owner'];unknown=tr['unknown'];n=len(self.rows)
        hist=np.zeros((n,scene.n));fractions=[];missing=[];alternatives=[]
        for i,(a,b) in enumerate(zip(self.bounds[:-1],self.bounds[1:])):
            o=own[a:b];ids,cnt=np.unique(o[o>=0],return_counts=True);hist[i,ids]=cnt/(b-a);fractions.append(hist[i].max());missing.append(np.mean(o<0))
            order=np.argsort(-cnt);alternatives.append([dict(index=int(scene.indices[ids[k]]),fraction=float(cnt[k]/(b-a))) for k in order[:6]])
        modal=hist.argmax(1);fixed=modal if anchors is None else np.array(anchors['regions'])-scene.indices[0]
        fixed=np.clip(fixed,0,scene.n-1);coverage=hist[np.arange(n),fixed];omission=np.array(missing)
        residual=[];labels=[];regions=[]
        def add(v,label,weight=1.):
            v=np.asarray(v).ravel()
            # Equal geographic influence within region and reflection blocks.
            sections=self.sections if label in ['coherence','positive_material','reverse_color'] else np.repeat([r['section'] for r in self.obs],2) if label=='reflection' else None
            if sections is not None:
                _,inverse,counts=np.unique(sections,return_inverse=True,return_counts=True)
                v=v*np.sqrt(len(v)/(len(counts)*counts[inverse]))
            residual.extend((v*np.sqrt(weight/max(1,len(v)))).tolist());labels.extend([label]*len(v))
        # Region-balanced coherence; real large misses retain linear influence.
        add(np.sqrt(self.confidence)*np.maximum(0,.92-coverage)/.25,'coherence',3.)
        add(np.sqrt(omission)/.4,'positive_material',2.)
        # Reverse evidence: bodies crossing red AND yellow support contradict known material.
        colors=np.array([r['color'] for r in self.rows]);red=hist[colors=='red'].sum(0);yellow=hist[colors=='yellow'].sum(0)
        opposite=np.where((colors=='red')[:,None],yellow,red)[np.arange(n),fixed]
        reverse=opposite/(red[fixed]+yellow[fixed]+1e-8)
        add(np.sqrt(reverse)/.3,'reverse_color',1.5)
        start=len(self.supportxy);c=self.cues;o=own[start:start+len(c['xy'])];cue_unknown=unknown[start:start+len(c['xy'])];start+=len(c['xy']);visible=o>=0;material=[]
        for j in range(32):
            keep=self.cue_sections==j;pp=keep&c['paper'];cc=keep&(c['color']>0)
            if not pp.any() and not cc.any():continue
            paper=float((visible[pp]|cue_unknown[pp]).mean()) if pp.any() else 0.;miss=float((~visible[cc]).mean()) if cc.any() else 0.
            material.append(dict(section=j,paper=paper,omission=miss));regions.append(j)
        add(np.sqrt([r['paper'] for r in material])/.25,'background',4.)
        add(np.sqrt([r['omission'] for r in material])/.4,'colored_omission',2.)
        sep=[]
        for r in self.separators:
            o=own[start:start+97];uncertain=unknown[start:start+97];start+=97;changes=np.flatnonzero((o[:-1]!=o[1:])&~uncertain[:-1]&~uncertain[1:])+.5
            e=float(min(abs(changes-r['valley_sample']))*r['representative_distance']/96) if len(changes) else 24.
            # A dark valley does not necessarily mean empty paper.
            sep.append(dict(id=r['id'],error=e,unknown_samples=int(uncertain.sum()),bank_same=bool(o[16]>=0 and o[16]==o[80])))
        add([r['error']/4 for r in sep],'separator',1.5)
        add([float(r['bank_same']) for r in sep],'separator_bank_merge',.5)
        contour=[];contourids=[]
        for i,cnt in enumerate(self.contours):
            o=own[start:start+len(cnt['xy'])];uncertain=unknown[start:start+len(cnt['xy'])].reshape(cnt['shape']);start+=len(cnt['xy']);inside=cnt['inside'];ids,c=np.unique(o[inside.ravel()&(o>=0)],return_counts=True)
            k=int(ids[c.argmax()]) if len(ids) else -1
            if anchors is not None:k=anchors['contours'][i]-int(scene.indices[0])
            mask=(o==k).reshape(cnt['shape']) if k>=0 else np.zeros(cnt['shape'],bool);contourids.append(int(scene.indices[k]) if k>=0 else int(scene.indices[0]))
            signed=cnt['signed'];edge=mask&~binary_erosion(mask)&~binary_dilation(uncertain);observed_edge=inside&~binary_erosion(inside)
            distance=distance_transform_edt(~edge)*cnt['step'] if edge.any() else np.full(mask.shape,40.)
            fwd=float(np.mean(np.maximum(0,distance[observed_edge]-3)))
            rev=float(np.mean(np.maximum(0,abs(signed[edge])-3))) if edge.any() else 30.
            inner=signed< -3;outside=signed>3
            miss=float(np.mean(~mask[inner])) if inner.any() else 0.;excess=float(np.sum(mask&outside)/max(1,inside.sum()))
            contour.append(dict(id=cnt['row']['id'],boundary_mae=fwd,reverse_boundary_mae=rev,inner_missing=miss,outside_fraction=excess,index=contourids[-1]))
        add([[r['boundary_mae']/3,r['reverse_boundary_mae']/3,np.sqrt(r['inner_missing'])/.5,np.sqrt(r['outside_fraction'])/.4] for r in contour],'visible_boundary',3.)
        eo=own[start:].reshape(len(self.envelopes),3,191);en=[]
        for r,lines in zip(self.envelopes,eo):
            bounds=[]
            for line in lines:
                hit=np.flatnonzero(line>=0);bounds.append([hit[0]-95,hit[-1]-95] if len(hit) else [0,0])
            en.append(np.median(bounds,axis=0))
        er=np.array(en)-np.array([r['bounds'] for r in self.envelopes]);unc=np.maximum(4,np.array([r['uncertainty_px'] for r in self.envelopes]))
        add(er/unc,'envelope',1.5)
        needed=None if anchors is None else sorted(set(k-int(scene.indices[0]) for k in anchors['reflections'].values() if k is not None))
        pred,meta=predict(scene,step,self.obs if needed is None else None,owners=needed)
        lookup={r['index']:r for r in pred};mapping=None
        if anchors is None:
            points=np.array([p['point'] for p in pred]);cost=np.sum((np.array([o['point'] for o in self.obs])[:,None]-points[None])**2,axis=2)
            for i,j in enumerate(self.obs_region):
                if j>=0:cost[i]+=144*(1-hist[j,[p['index']-int(scene.indices[0]) for p in pred]])
            ii,jj=linear_sum_assignment(np.c_[cost,np.full((len(self.obs),len(self.obs)),48.**2)])
            mapping={self.obs[i]['id']:(pred[j]['index'] if j<len(pred) else None) for i,j in zip(ii,jj)}
        else:mapping=anchors['reflections']
        errors=[];rv=[];records=[]
        for i,o in enumerate(self.obs):
            p=lookup.get(mapping.get(o['id']));d=np.array(p['point'])-o['point'] if p else np.array([48.,0.]);t=self.tangents[i]
            signed=[float(d@t),float(d@[-t[1],t[0]])];rv.append(np.array(signed)/6.);error=float(np.linalg.norm(d));errors.append(error)
            records.append(dict(id=o['id'],index=mapping.get(o['id']),error_px=error if p else None,observed=o['point'],predicted=p['point'] if p else None,section=o['section'],tangent_px=signed[0] if p else None,normal_px=signed[1] if p else None))
        rv=np.asarray(rv);rv=np.sign(rv)*np.sqrt(np.where(abs(rv)<=3,rv*rv,6*abs(rv)-9))
        add(rv,'reflection',3.)
        # Equal weak smoothness blocks; no independent bead motion.
        for key,scale in [('axis_nodes',10.),('local_phase',.4),('local_spacing',.02)]:
            v=np.asarray(scene.p.get(key,[0.]*32));add((np.roll(v,1)-2*v+np.roll(v,-1))/scale,'regularity',.03)
        v=np.array(residual);loss=float(v@v)
        result=dict(loss=loss,seconds=time.monotonic()-began,coherence=float(np.mean(coverage)),modal_coherence=float(np.mean(fractions)),omission=float(np.mean(omission)),reverse_conflict=float(np.mean(reverse)),paper=float(np.mean([r['paper'] for r in material])),colored_missing=float(np.mean([r['omission'] for r in material])),boundary=float(np.mean([r['boundary_mae'] for r in contour])),reverse_boundary=float(np.mean([r['reverse_boundary_mae'] for r in contour])),separator=float(np.mean([r['error'] for r in sep])),envelope_width=float(np.mean(abs(np.diff(er,axis=1)))),reflection_rms=float(np.sqrt(np.mean(np.square(errors)))),unmatched=sum(r['predicted'] is None for r in records),unknown=int(unknown.sum()),rays=len(own),blocks={k:float(np.sum(v[np.array(labels)==k]**2)) for k in set(labels)},material=material)
        anchors=dict(regions=scene.indices[fixed].tolist(),contours=contourids,reflections=mapping)
        if detail:
            result.update(supports=[dict(id=r['id'],point=r['point'],section=int(j),fraction=float(f),modal_fraction=float(mo),missing=float(mi),confidence=float(w),policy=pol,index=int(k),alternatives=al) for r,j,f,mo,mi,w,pol,k,al in zip(self.rows,self.sections,coverage,fractions,omission,self.confidence,self.policy,anchors['regions'],alternatives)],contours=contour,separators=sep,reflections=records,predictions=pred,numerics=meta)
        return v,result,anchors
