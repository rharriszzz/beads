"""R315 readiness uses independent evidence relevance, never unrelated raster rays."""
import numpy as np
from scipy import ndimage as ndi
from .diagnose import brackets

def measure_readiness(e,tr,metrics,split):
    m=e.m;valid=m['roi']&(m['split']==split)
    relevant=m['material']|m['paper']|(m['core']>0)|ndi.binary_dilation(m['seams'].any(0))
    for y,x,axis,sign,gap in m['external_brackets']:
        dy,dx=(0,sign) if axis==0 else (sign,0)
        for t in range(-3,int(gap)+4):
            yy,xx=int(y+t*dy),int(x+t*dx)
            if 0<=yy<e.shape[0] and 0<=xx<e.shape[1]:relevant[yy,xx]=True
    un=tr['unknown'].reshape(e.shape);bs=[b for b in brackets(e,tr) if b['split']==split];finite=[b['displacement'] for b in bs if b['found']];p95=float(np.percentile(finite,95)) if finite else None;missing=sum(not b['found'] for b in bs);v=metrics['vector'];fails=[]
    for key,val,limit in [('material',v['omission'],5),('paper',v['paper'],.5),('seam',v['seam'],10),('worst_core',v['worst'],3)]:
        if val>limit:fails.append(key)
    if any(c['modal_fraction']<.8 for c in metrics['cores']):fails.append('individual_core')
    if p95 is None or p95>3:fails.append('external_brackets')
    if missing:fails.append('missing_boundary')
    count=int((un&relevant&valid).sum())
    if count:fails.append('uncertainty_on_independent_evidence')
    return dict(ready=not fails,failures=fails,unknown_evidence_pixels=count,unknown_unrelated_roi_pixels=int((un&~relevant&valid).sum()),finite_external_p95=p95,missing_boundaries=missing,policy='Absolute engineering limits, no R306 owner protection. Harmless unrelated unknown rays are reported, not readiness failures. Contact certification and visual review remain additional necessary requirements.')
