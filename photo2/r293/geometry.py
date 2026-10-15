"""Image-traced curve coordinates only; no physical reconstruction or bead stations."""
import numpy as np
from scipy.spatial import cKDTree
from .common import ROOT,read

class Reference:
    def __init__(self):
        d=read(ROOT/'photo2/r282/results/centerline.json');self.points=np.array(d['points']);self.delta=np.diff(self.points,axis=0);self.lengths=np.linalg.norm(self.delta,axis=1);self.arc=np.r_[0,np.cumsum(self.lengths)];self.length=float(self.arc[-1]);self.tree=cKDTree(self.points)
    def project(self,xy):
        xy=np.asarray(xy,float).reshape(-1,2);_,near=self.tree.query(xy,k=8);ix=np.unique(near) if len(xy)==0 else near
        candidates=np.concatenate([near,np.maximum(near-1,0)],axis=1);candidates=np.minimum(candidates,len(self.delta)-1);a=self.points[candidates];v=self.delta[candidates];t=np.clip(np.sum((xy[:,None,:]-a)*v,axis=2)/np.maximum(np.sum(v*v,axis=2),1e-12),0,1);q=a+t[:,:,None]*v;dist=np.linalg.norm(xy[:,None,:]-q,axis=2);best=dist.argmin(1);idx=np.arange(len(xy));j=candidates[idx,best];point=q[idx,best];tangent=self.delta[j]/np.maximum(self.lengths[j,None],1e-12);normal=np.c_[-tangent[:,1],tangent[:,0]];signed=np.sum((xy-point)*normal,axis=1);arc=self.arc[j]+t[idx,best]*self.lengths[j]
        return dict(distance=dist[idx,best],signed=signed,arc=arc,point=point)
    def station_points(self,spacing=24):
        arc=np.arange(0,self.length,spacing);j=np.minimum(np.searchsorted(self.arc,arc,side='right')-1,len(self.delta)-1);t=(arc-self.arc[j])/np.maximum(self.lengths[j],1e-12);return arc,self.points[j]+t[:,None]*self.delta[j]
    def arc_distance(self,a,b):
        d=np.abs(np.array(a)-np.array(b));return np.minimum(d,self.length-d)
