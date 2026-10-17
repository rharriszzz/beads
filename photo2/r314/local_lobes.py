"""Retain every distinct sampled local maximum, including faint secondary lobes.

Connected half-local-maximum supports may overlap or merge. Those relationships
are recorded, never converted to distinct beads or unique physical specular lobes.
"""
import numpy as np
from scipy import ndimage as ndi

def maxima(xy,intensity,step=1.,floor=1e-4):
    xy=np.asarray(xy,float).reshape(-1,2);v=np.asarray(intensity,float)
    if not len(v):return []
    lo=xy.min(0);ij=np.rint((xy-lo)/step).astype(int);shape=tuple((ij.max(0)+1)[::-1]);field=np.zeros(shape);field[ij[:,1],ij[:,0]]=v
    ismax=(field>=ndi.maximum_filter(field,3,mode='constant'))&(field>=floor);labels,n=ndi.label(ismax,np.ones((3,3),bool));out=[]
    for k in range(1,n+1):
        yy,xx=np.where(labels==k);peak=float(field[yy[0],xx[0]]);patches=[]
        for frac in [.4,.5,.6]:
            cc,_=ndi.label(field>=max(floor,frac*peak),np.ones((3,3),bool));mask=cc==cc[yy[0],xx[0]];py,px=np.where(mask);w=field[py,px];pts=lo+np.c_[px,py]*step;other=np.unique(labels[mask]);other=other[other>0]
            patches.append(dict(fraction=frac,pixels=pts.tolist(),centroid=pts.mean(0).tolist(),weighted_centroid=np.average(pts,axis=0,weights=w).tolist(),contains_local_maxima=other.tolist(),merged_peak_support=len(other)>1))
        out.append(dict(local_maximum=k,peak=(lo+np.array([xx[0],yy[0]])*step).tolist(),peak_ties=(lo+np.c_[xx,yy]*step).tolist(),intensity=peak,relative_to_global=float(peak/v.max()),patches=patches))
    return out
