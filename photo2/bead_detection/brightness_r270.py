"""Isolated R270 score definitions, neutral-gray conversions and path experiments."""
from collections import deque
from dataclasses import replace
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import local_maxima,max_tree
from .climb_r268 import N8,Guards,edge_reasons
from .search_r269 import Neighborhood,Policy

SCALE=10**9
MEASURES=('V','Y','OKL','VS')
M1=np.array([[.4122214708,.5363325363,.0514459929],[.2119034982,.6806995451,.1073969566],[.0883024619,.2817188376,.6299787005]])
LROW=np.array([.2104542553,.7936177850,-.0040720468])
WHITE_L=float(np.cbrt(M1.sum(axis=1))@LROW)

def linearize(c):
    c=np.asarray(c,dtype=np.float64)
    return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)

def encode(c):
    c=np.asarray(c,dtype=np.float64)
    return np.where(c<=.0031308,12.92*c,1.055*np.maximum(c,0)**(1/2.4)-.055)

def scores(rgb):
    c=np.asarray(rgb,dtype=np.float64)/255;v=c.max(axis=-1);minimum=c.min(axis=-1);lin=linearize(c)
    return {'V':255*v,'Y':255*(lin@np.array([.2126,.7152,.0722])),
            'OKL':255*(np.cbrt(lin@M1.T)@LROW),'VS':255*(v+minimum)/2}

def paired_scores(native,srgb=None):
    result=scores(native)
    if srgb is not None:
        standard=scores(srgb)
        for m in ('Y','OKL'):result[m]=standard[m]
    return result

def quantized(rgb,srgb=None):return {m:np.rint(a*SCALE).astype(np.int64) for m,a in paired_scores(rgb,srgb).items()}

def color_managed_photo():
    import io,hashlib
    from PIL import Image,ImageOps,ImageCms
    from .audit_r267 import ROOT
    source=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg'))
    icc=source.info.get('icc_profile')
    if icc:
        profile=ImageCms.ImageCmsProfile(io.BytesIO(icc));converted=ImageCms.profileToProfile(source,profile,ImageCms.createProfile('sRGB'),renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,outputMode='RGB')
        metadata=dict(input_profile=ImageCms.getProfileName(profile).strip(),profile_sha256=hashlib.sha256(icc).hexdigest(),intent='relative-colorimetric',output='8-bit sRGB RGB via Pillow ImageCms/LCMS',lcms_version=ImageCms.core.littlecms_version,pillow_version=__import__('PIL').__version__)
    else:converted=source.convert('RGB');metadata=dict(input_profile=None,assumption='untagged RGB treated as sRGB')
    return np.asarray(converted),metadata

def neutral(code,m):
    c=np.clip(np.asarray(code,dtype=float),0,255)/255
    if m in ('V','VS'):return c*255
    y=linearize(c)
    return y*255 if m=='Y' else np.cbrt(y)*255*WHITE_L

def gray_equivalent(value,m):
    z=np.clip(np.asarray(value,dtype=float)/(255*WHITE_L if m=='OKL' else 255),0,1)
    if m in ('V','VS'):return z*255
    return encode(z if m=='Y' else z**3)*255

def floor_for(reference,budget,m):
    if budget>=256:return -1.
    return float(neutral(gray_equivalent(reference,m)-budget,m))

def sums(q,n):
    kernel=np.ones(n,np.int64);out=ndi.convolve1d(ndi.convolve1d(q,kernel,axis=0,mode='constant'),kernel,axis=1,mode='constant');r=n//2
    out[:r]=out[-r:]=-1;out[:,:r]=out[:,-r:]=-1
    return out

class Search(Neighborhood):
    def __init__(self,q,hsv,paper,sumq,side,anchor,measure,reference=None,raw_v=None,v_reference=None,fixed_v=False):
        super().__init__(q/SCALE,hsv,paper,sumq,side,anchor,reference_raw=reference)
        self.measure=measure;self.mean=self.sums/(SCALE*side**2);self.meancap=self.sumcap/(SCALE*side**2);self.reference_mean=float(self.mean[self.start])
        self.fixed_v=fixed_v;self.v_reference=v_reference
        self.original_v=np.rint(self.hs[:,2]*255).astype(np.int16)
        self.vcap=np.minimum.reduce([self.original_v[z] for z in (self.a,self.b,self.c,self.d)])

    def floors(self,policy):return (self.v_reference-policy.raw_drop if self.fixed_v else floor_for(self.reference_raw,policy.raw_drop,self.measure),floor_for(self.reference_mean,policy.mean_drop,self.measure))

    def edge_masks(self,radius,policy):
        spatial=self.validedge.copy()
        for z in (self.a,self.b,self.c,self.d):spatial &= self.dist2[z]<=radius**2
        bits=self.colorbits.copy() if policy.color else np.zeros(len(self.a),np.uint8)
        rf,mf=self.floors(policy);raw=self.vcap if self.fixed_v else self.rawcap
        bits[raw<rf-1e-9]|=32
        bits[self.sumcap<mf*SCALE*self.side**2-.25]|=64
        return spatial,bits

    def path(self,pred,end):
        ids=[int(end)]
        while ids[-1]!=self.start:
            a=int(pred[ids[-1]])
            if a<0:return []
            ids.append(a);assert len(ids)<=len(self.v)
        return [dict(x=int(self.xy[i,0]),y=int(self.xy[i,1]),raw=float(self.v[i]),mean=float(self.mean[i]),sum_q=int(self.sums[i]),raw_v=int(self.original_v[i]),h_deg=float(self.hs[i,0]*360),s=float(self.hs[i,1])) for i in ids[::-1]]

    def audit_path(self,path,radius,policy):
        spatial,bits=self.edge_masks(radius,policy);keep=spatial&(bits==0);edges={(int(a),int(b)) for a,b in zip(self.a[keep],self.b[keep])}
        assert (path[0]['x'],path[0]['y'])==self.anchor
        for a,b in zip(path,path[1:]):assert (self.index((a['x'],a['y'])),self.index((b['x'],b['y']))) in edges
        return len(path)-1

class Climber:
    def __init__(self,q,hsv,paper,n,measure):
        self.q=q;self.raw=q/SCALE;self.hsv=hsv;self.paper=paper;self.n=n;self.measure=measure;self.sumq=sums(q,n);self.h,self.w=q.shape;self.v=np.rint(hsv[:,:,2]*255).astype(np.uint8)

    def color_edge(self,a,b,start):return edge_reasons(a,b,start,0,self.v,self.hsv,self.paper,Guards(raw_valley_dn=256))
    def climb(self,start,guarded=True):
        x,y=map(int,start);seed=self.hsv[y,x];peak=float(self.raw[y,x]);steps=[];blocked=[]
        def sample():return dict(x=x,y=y,raw=float(self.raw[y,x]),raw_v=int(self.v[y,x]),sum_q=int(self.sumq[y,x]),mean=float(self.sumq[y,x]/(SCALE*self.n**2)),running_peak=peak)
        if guarded and self.paper[y,x]:return dict(start=list(start),endpoint=[x,y],steps=[sample()],blocked=[],stop='start-background' if self.paper[y,x]==1 else 'start-context-uncertainty',plateau=None)
        while True:
            steps.append(sample());better=[];valid=[]
            for dx,dy in N8:
                xx,yy=x+dx,y+dy
                if not(0<=xx<self.w and 0<=yy<self.h) or self.sumq[yy,xx]<0:continue
                if self.sumq[yy,xx]>self.sumq[y,x]:better.append((xx,yy))
            for xx,yy in better:
                reasons=[]
                if guarded:
                    reasons=self.color_edge((x,y),(xx,yy),seed)
                    if self.raw[yy,xx]<floor_for(peak,12,self.measure)-1e-9:reasons.append('measure-running-peak-floor')
                    if xx!=x and yy!=y:
                        for sx,sy in ((xx,y),(x,yy)):
                            rs=self.color_edge((x,y),(sx,sy),seed)+self.color_edge((sx,sy),(xx,yy),seed)
                            if self.raw[sy,sx]<floor_for(peak,12,self.measure)-1e-9 or self.raw[yy,xx]<floor_for(max(peak,self.raw[sy,sx]),12,self.measure)-1e-9:rs.append('measure-running-peak-floor')
                            reasons+=['diagonal-corner:'+r for r in rs]
                if reasons:blocked.append(dict(step=len(steps)-1,from_xy=[x,y],to_xy=[xx,yy],raw=float(self.raw[yy,xx]),mean=float(self.sumq[yy,xx]/(SCALE*self.n**2)),reasons=sorted(set(reasons))))
                else:valid.append((xx,yy))
            if valid:x,y=min(valid,key=lambda p:(-int(self.sumq[p[1],p[0]]),p[1],p[0]));peak=max(peak,float(self.raw[y,x]));continue
            if better:stop='all-higher-neighbors-blocked';plateau=None
            else:
                level=self.sumq[y,x];seen={(x,y)};queue=deque(seen);higher=False;boundary=False
                while queue:
                    a,b=queue.popleft()
                    for dx,dy in N8:
                        xx,yy=a+dx,b+dy
                        if not(0<=xx<self.w and 0<=yy<self.h) or self.sumq[yy,xx]<0:boundary=True;continue
                        s=self.sumq[yy,xx]
                        if s>level:higher=True
                        elif s==level and (xx,yy) not in seen:seen.add((xx,yy));queue.append((xx,yy))
                plateau=dict(pixels=len(seen),higher_exit=higher,context_boundary=boundary,canonical=list(min(seen,key=lambda p:(p[1],p[0]))))
                stop='equal-plateau-with-uphill-exit' if higher else 'equal-plateau-regional-maximum' if len(seen)>1 else 'strict-local-maximum'
            return dict(start=list(start),endpoint=[x,y],steps=steps,blocked=blocked,stop=stop,plateau=plateau)

    def audit(self,t,guarded):
        assert t['steps'][0]['x']==t['start'][0] and t['steps'][0]['y']==t['start'][1]
        assert [t['steps'][-1]['x'],t['steps'][-1]['y']]==t['endpoint']
        seed=self.hsv[t['start'][1],t['start'][0]];peak=float(self.raw[t['start'][1],t['start'][0]])
        for p in t['steps']:
            x,y=p['x'],p['y'];peak=max(peak,float(self.raw[y,x]))
            assert p['sum_q']==int(self.sumq[y,x]) and p['raw']==self.raw[y,x] and p['running_peak']==peak
            assert p['mean']==self.sumq[y,x]/(SCALE*self.n**2)
        for a,b in zip(t['steps'],t['steps'][1:]):
            assert max(abs(a['x']-b['x']),abs(a['y']-b['y']))==1 and b['sum_q']>a['sum_q']
            if guarded:
                assert not self.color_edge((a['x'],a['y']),(b['x'],b['y']),seed)
                assert b['raw']>=floor_for(a['running_peak'],12,self.measure)-1e-9
                if a['x']!=b['x'] and a['y']!=b['y']:
                    for sx,sy in ((b['x'],a['y']),(a['x'],b['y'])):
                        assert not self.color_edge((a['x'],a['y']),(sx,sy),seed) and not self.color_edge((sx,sy),(b['x'],b['y']),seed)
                        assert self.raw[sy,sx]>=floor_for(a['running_peak'],12,self.measure)-1e-9
                        assert b['raw']>=floor_for(max(a['running_peak'],self.raw[sy,sx]),12,self.measure)-1e-9
        assert len({(p['x'],p['y']) for p in t['steps']})==len(t['steps'])
        return len(t['steps'])-1

def maxima_inventory(q,box):
    """All pixels in regional plateaus intersecting box, including crossing pixels."""
    mask=local_maxima(q,connectivity=2,allow_borders=True);labels,_=ndi.label(mask,np.ones((3,3)));x0,y0,x1,y1=box
    ids=np.unique(labels[y0:y1,x0:x1]);ids=ids[ids>0];yy,xx=np.where(np.isin(labels,ids))
    return [(int(x),int(y),int(labels[y,x])) for x,y in zip(xx,yy)],mask

def prominences(q,points):
    """Exact context prominence via max-tree; flag paths escaping the saved context."""
    parent,order=max_tree(q,connectivity=2);p=parent.ravel();a=q.ravel();top=a.copy();border=np.zeros(q.shape,bool);border[[0,-1],:]=True;border[:,[0,-1]]=True;border=border.ravel()
    for i in order[::-1]:
        j=p[i]
        if top[i]>top[j]:top[j]=top[i]
        border[j] |= border[i]
    result=[]
    for x,y,*_ in points:
        i=y*q.shape[1]+x;peak=int(a[i]);j=i;censored=False
        while top[j]<=peak:
            if border[j] or p[j]==j:censored=True;break
            j=p[j]
        result.append(dict(prominence=(peak-int(a[j]))/SCALE,saddle=int(a[j])/SCALE,prominence_censored=censored))
    return result
