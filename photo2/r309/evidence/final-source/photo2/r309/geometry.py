"""Whole-photo height laws; unchanged periodic axis and frozen local fields."""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r307.fast import Chain as Fast,kernel
from photo2.r306.geometry import Chain as Original,valid as original_valid
from photo2.r295.geometry import AXES,unit

class Chain(Fast):
    def placement(self,k):
        line,g,phase=super().placement(k)
        y=(self.project(line)[:,1]-1591.)/1591.
        angle=np.radians(self.p.get('tilt_y',0)*y+self.p.get('tilt_y2',0)*(y*y-1/3))
        a,b=g[AXES[0]],g[AXES[2]]
        g[AXES[0]]=np.cos(angle)[:,None]*a+np.sin(angle)[:,None]*b
        g[AXES[2]]=-np.sin(angle)[:,None]*a+np.cos(angle)[:,None]*b
        return line,g,phase
    def __init__(self,p,data,resolution=16385):
        super().__init__(p,data,resolution)
        y=(self.axis_xy[:,1]-1591.)/1591.
        self.height_minor_factor=1+p.get('minor_y',0)*y
        self.centers=self.line+p['minor']*self.height_minor_factor[:,None]*self.g['radial']
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
        if np.isfinite(self.distance):
            depth=self.centers@self.eye
            if np.max(depth+self.bound)>.85*self.distance:raise ValueError('Camera bound')
            self.query_radius=self.bound*self.scale*np.max((1+np.linalg.norm(self.centers,axis=1)/self.distance)/(1-(depth+self.bound)/self.distance)**2)
    def blocked(self,points,direction,max_distance=np.inf):
        if np.ndim(direction)!=2:return super().blocked(points,direction,max_distance)
        points=np.asarray(points);d=np.asarray(direction);blocked=np.zeros(len(points),bool);owner=np.full(len(points),-1,int);unknown=0
        for start in range(0,len(points),256):
            p=points[start:start+256];v=d[start:start+len(p)];limits=np.asarray(max_distance)[start:start+len(p)] if np.ndim(max_distance) else np.full(len(p),max_distance)
            delta=p[:,None,:]-self.centers[None];mid=-np.einsum('ijk,ik->ij',delta,v);perp=np.einsum('ijk,ijk->ij',delta,delta)-mid**2
            a,b=np.where((perp<self.bound**2)&(mid+self.bound>0)&(mid-self.bound<limits[:,None]));delta=delta[a,b];mid=mid[a,b];perp=perp[a,b]
            half=np.sqrt(np.maximum(self.bound**2-perp,0));t=np.maximum(0,mid-half);end=np.minimum(limits[a],mid+half);keep=end>=t;a,b,delta,t,end=[z[keep] for z in (a,b,delta,t,end)]
            if not len(a):continue
            axes=[self.g[key][b] for key in AXES];q=np.stack([np.sum(delta*z,axis=1) for z in axes],axis=1);vl=np.stack([np.sum(v[a]*z,axis=1) for z in axes],axis=1)
            depth,state=kernel(q,vl,t,end,self.dims,1);hit=state==1;active=state==2;unknown+=int(active.sum());blocked[start+a[hit|active]]=True
            first=np.full(len(p),np.inf);np.minimum.at(first,a[hit],depth[hit]);front=hit&(depth<=first[a]+1e-6);owner[start+a[front]]=b[front];owner[start+a[active]]=-2
        return blocked,owner,unknown

def valid(p):
    return original_valid(p) and abs(p.get('minor_y',0))<=.04 and abs(p.get('tilt_y',0))<=3 and abs(p.get('tilt_y2',0))<=3 and 0<=p.get('light_inverse',0)<=.003
