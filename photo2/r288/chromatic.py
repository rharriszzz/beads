"""Diagnostic H: locally learned diffuse chromaticity, not a physical body model.

Tests whether N11-like upper color drift supports exclusion. Failure to fit a
single local color distribution is uncertainty, not proof of a different bead.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.color import hsv2rgb
from photo2.r285.methods import component
PARAMETERS=dict(core_radius=8,minimum_samples=12,diffuse_upper_quantile=.7,
 covariance_ridge=.0002,mahalanobis_limit=9.,highlight_saturation=.65)

def restrict(f,owned):
    seed=f['seed'];pg=f['pigment'];raw=f['lum'];hs=f['hsv'];empty=np.zeros_like(owned)
    if seed is None:return empty,dict(reason='no-supported-cue')
    yy,xx=np.indices(owned.shape);near=(xx-seed[0])**2+(yy-seed[1])**2<=64;core=near&pg&(hs[:,:,1]>.5)
    if core.any():core &= raw<=np.quantile(raw[core],.7)
    a=hsv2rgb(hs);lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);ch=lin[:,:,:2]/np.maximum(lin.sum(2,keepdims=True),1e-8);samples=ch[core]
    if len(samples)<12:return empty,dict(reason='insufficient-local-diffuse-color',samples=len(samples))
    mean=np.median(samples,axis=0);delta=samples-mean;cov=(delta.T@delta)/len(samples)+.0002*np.eye(2);diff=ch-mean;cost=np.einsum('...i,ij,...j->...',diff,np.linalg.inv(cov),diff);material=pg&(cost<=9.);highlight=(hs[:,:,1]<.65)&(raw>f['meta']['diffuse_Y'])&(ndi.distance_transform_edt(~material)<=3);mask=component(owned&(material|highlight),seed)
    y,x=np.where(owned&~mask);return mask,dict(samples=len(samples),mean_chromaticity=mean.tolist(),covariance=cov.tolist(),removed_pixels=np.c_[x,y].tolist(),removed=int((owned&~mask).sum()),model='single local diffuse chromaticity ellipsoid; engineering distance, not calibrated probability',uncertainty='illumination or hue variation within one bead can violate this model')
