"""R268 isolated strict ascent experiment; never imported by production detection.

Means are exact integer square sums divided by area. Equality never permits a
move. Plateaus are inspected only to distinguish a true regional maximum from
an endpoint with an uphill exit reachable only by forbidden equal-score steps.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass,asdict
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from . import annular_detect as old

N8=tuple((dx,dy) for dy in (-1,0,1) for dx in (-1,0,1) if dx or dy)

@dataclass(frozen=True)
class Guards:
    enabled: bool=True
    raw_valley_dn: int=12
    paper_uncertainty_stop: bool=True
    hue_step_deg: float=12.
    hue_from_start_deg: float=25.
    saturation_step: float=.22
    saturation_both_bright: bool=False
    reliable_saturation: float=.35
    reliable_value: float=.2
    reliable_chroma: float=.08

VARIANTS={'unguarded':Guards(enabled=False),'guarded6':Guards(raw_valley_dn=6),'guarded12':Guards(),'guarded24':Guards(raw_valley_dn=24),'confident-only12':Guards(paper_uncertainty_stop=False),'legacy-color12':Guards(saturation_both_bright=True)}

def score_sums(value,side):
    """Whole-image exact native sums; incomplete edge windows have sentinel -1."""
    r=side//2
    tmp=ndi.convolve1d(value.astype(np.int32),np.ones(side,dtype=np.int32),axis=0,mode='constant',cval=0)
    sums=ndi.convolve1d(tmp,np.ones(side,dtype=np.int32),axis=1,mode='constant',cval=0)
    sums[:r]=sums[-r:]=-1;sums[:,:r]=sums[:,-r:]=-1
    return sums

def background(rgb):
    hsv=rgb_to_hsv(rgb/255.);h,w=rgb.shape[:2];border=np.zeros((h,w),bool);margin=max(1,round(min(h,w)*.035));border[:margin]=border[-margin:]=True;border[:,:margin]=border[:,-margin:]=True
    model,paper,uncertain=old.background_maps(hsv,border)
    # Reuse BOTH the original confident map and R267's established smooth-context
    # paper uncertainty deferral. Keep their reasons distinct; no hue-only gate.
    value=rgb.max(axis=2);texture=ndi.maximum_filter(value,5).astype(float)-ndi.minimum_filter(value,5)
    smooth=uncertain & (texture<=max(18,model.get('texture_limit_dn',18)*1.5))
    counts=ndi.convolve1d(ndi.convolve1d(smooth.astype(np.int32),np.ones(25,np.int32),axis=0,mode='constant'),np.ones(25,np.int32),axis=1,mode='constant')
    nx=np.minimum(np.arange(w)+13,w)-np.maximum(np.arange(w)-12,0)
    ny=np.minimum(np.arange(h)+13,h)-np.maximum(np.arange(h)-12,0)
    context=uncertain & (counts>.08*ny[:,None]*nx[None,:])
    stops=np.where(paper,1,np.where(context,2,0)).astype(np.uint8)
    model['stop_map']=dict(confident_pixels=int(paper.sum()),context_uncertain_pixels=int((stops==2).sum()),context_half_window=12,smooth_factor=1.5,nearby_fraction=.08)
    return hsv,stops,model

def hue_distance(a,b):return abs((float(a)-float(b)+.5)%1-.5)*360

def edge_reasons(a,b,start_hsv,peak_raw,value,hsv,paper,g):
    if not g.enabled:return []
    x,y=a;xx,yy=b;q=hsv[y,x];t=hsv[yy,xx];reasons=[]
    if paper[yy,xx]==1:reasons.append('confident-background')
    elif paper[yy,xx]==2 and g.paper_uncertainty_stop:reasons.append('existing-paper-context-uncertainty')
    if int(value[yy,xx])<peak_raw-g.raw_valley_dn:reasons.append('raw-running-peak-valley')
    reliable=lambda z:z[1]>=g.reliable_saturation and z[2]>=g.reliable_value and z[1]*z[2]>=g.reliable_chroma
    if reliable(q) and reliable(t) and hue_distance(q[0],t[0])>g.hue_step_deg:reasons.append('abrupt-hue-boundary')
    if reliable(start_hsv) and reliable(t) and hue_distance(start_hsv[0],t[0])>g.hue_from_start_deg:reasons.append('start-relative-hue-boundary')
    color_value=min(q[2],t[2]) if g.saturation_both_bright else max(q[2],t[2])
    if color_value>=g.reliable_value and abs(q[1]-t[1])>g.saturation_step:reasons.append('abrupt-saturation-boundary')
    return reasons

class Surface:
    def __init__(self,value,hsv,paper,side):
        self.value=value;self.hsv=hsv;self.paper=paper;self.side=side;self.sums=score_sums(value,side);self.plateau_cache={};self.h,self.w=value.shape
    def valid(self,x,y):return 0<=x<self.w and 0<=y<self.h and self.sums[y,x]>=0
    def plateau(self,x,y):
        if (x,y) in self.plateau_cache:return self.plateau_cache[x,y]
        level=int(self.sums[y,x]);seen={(x,y)};queue=deque([(x,y)]);exits=set();touches=False
        while queue:
            a,b=queue.popleft()
            for dx,dy in N8:
                xx,yy=a+dx,b+dy
                if not self.valid(xx,yy):touches=True;continue
                s=int(self.sums[yy,xx])
                if s==level and (xx,yy) not in seen:seen.add((xx,yy));queue.append((xx,yy))
                elif s>level:exits.add((xx,yy))
        canonical=min(seen,key=lambda p:(p[1],p[0]))
        result=dict(id=f'{canonical[0]},{canonical[1]}',pixel_count=len(seen),canonical=list(canonical),higher_boundary_count=len(exits),touches_window_boundary=touches)
        for p in seen:self.plateau_cache[p]=result
        return result
    def climb(self,start,g=Guards()):
        x,y=map(int,start);start_hsv=self.hsv[y,x];peak=int(self.value[y,x]);steps=[];blocked=[]
        def sample():
            return dict(x=x,y=y,raw_v=int(self.value[y,x]),score_sum=int(self.sums[y,x]),score_dn=float(self.sums[y,x]/self.side**2),running_raw_peak=peak,h_deg=float(self.hsv[y,x,0]*360),s=float(self.hsv[y,x,1]))
        if not self.valid(x,y):return dict(start=list(start),endpoint=[x,y],steps=[sample()],stop='incomplete-image-window',blocked=[],plateau=None)
        if g.enabled and (self.paper[y,x]==1 or (self.paper[y,x]==2 and g.paper_uncertainty_stop)):
            reason='start-confident-background' if self.paper[y,x]==1 else 'start-existing-paper-context-uncertainty'
            return dict(start=list(start),endpoint=[x,y],steps=[sample()],stop=reason,blocked=[],plateau=None)
        while True:
            steps.append(sample());current=int(self.sums[y,x]);better=[];valid=[]
            for dx,dy in N8:
                xx,yy=x+dx,y+dy
                if self.valid(xx,yy) and int(self.sums[yy,xx])>current:better.append((xx,yy))
            for xx,yy in better:
                reasons=edge_reasons((x,y),(xx,yy),start_hsv,peak,self.value,self.hsv,self.paper,g)
                # No diagonal passage around a blocked native corner. Side pixels
                # are checked as barriers, not accepted as lower/equal-score moves.
                if g.enabled and xx!=x and yy!=y:
                    for sx,sy in ((xx,y),(x,yy)):
                        side=edge_reasons((x,y),(sx,sy),start_hsv,peak,self.value,self.hsv,self.paper,g)
                        side+=edge_reasons((sx,sy),(xx,yy),start_hsv,max(peak,int(self.value[sy,sx])),self.value,self.hsv,self.paper,g)
                        reasons += ['diagonal-corner:'+r for r in side]
                if reasons:blocked.append(dict(step=len(steps)-1,from_xy=[x,y],to_xy=[xx,yy],score_sum=int(self.sums[yy,xx]),score_dn=float(self.sums[yy,xx]/self.side**2),raw_v=int(self.value[yy,xx]),reasons=sorted(set(reasons))))
                else:valid.append((xx,yy))
            if valid:
                # Best admissible neighbor; exact ties resolved by y then x.
                x,y=min(valid,key=lambda p:(-int(self.sums[p[1],p[0]]),p[1],p[0]));peak=max(peak,int(self.value[y,x]));continue
            if better:stop='all-strictly-higher-neighbors-blocked'
            else:
                p=self.plateau(x,y)
                stop='equal-plateau-with-unreachable-uphill-exit' if p['higher_boundary_count'] else 'equal-plateau-regional-maximum' if p['pixel_count']>1 else 'strict-local-maximum'
                if p['touches_window_boundary']:stop+=';image-window-boundary'
            return dict(start=list(start),endpoint=[x,y],steps=steps,stop=stop,blocked=blocked,plateau=self.plateau(x,y))

def audit(surface,result,g):
    steps=result['steps'];assert steps[0]['x']==result['start'][0] and steps[0]['y']==result['start'][1]
    assert [steps[-1]['x'],steps[-1]['y']]==result['endpoint']
    for a,b in zip(steps,steps[1:]):
        assert max(abs(a['x']-b['x']),abs(a['y']-b['y']))==1
        assert b['score_sum']>a['score_sum']
        assert not edge_reasons((a['x'],a['y']),(b['x'],b['y']),surface.hsv[result['start'][1],result['start'][0]],a['running_raw_peak'],surface.value,surface.hsv,surface.paper,g)
        if g.enabled and a['x']!=b['x'] and a['y']!=b['y']:
            for sx,sy in ((a['x'],b['y']),(b['x'],a['y'])):
                q=surface.hsv[result['start'][1],result['start'][0]]
                assert not edge_reasons((a['x'],a['y']),(sx,sy),q,a['running_raw_peak'],surface.value,surface.hsv,surface.paper,g)
                assert not edge_reasons((sx,sy),(b['x'],b['y']),q,max(a['running_raw_peak'],int(surface.value[sy,sx])),surface.value,surface.hsv,surface.paper,g)
    assert len({(a['x'],a['y']) for a in steps})==len(steps)
    return len(steps)-1
