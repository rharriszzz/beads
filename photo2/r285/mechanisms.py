"""Controlled intensity mechanisms; identity assumptions are evaluation-only."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r282.common import save,support
from .methods import basins
from .select import OUT

def field(bridge):
    y,x=np.indices((65,65));left=(x-24)**2+(y-32)**2<=9**2;right=(x-46)**2+(y-32)**2<=9**2;neck=(x>=24)&(x<=46)&(abs(y-32)<=1);domain=left|right|neck
    lum=np.where(domain,.3,.003);lum[neck&~(left|right)]=bridge
    lum+=.08*np.exp(-((x-24)**2+(y-32)**2)/12)+.08*np.exp(-((x-46)**2+(y-32)**2)/12)
    return ndi.gaussian_filter(lum,.65),domain

def main():
    results=[]
    for name,bridge,interpretation in [('narrow-bright-continuation',.29,'One supported bright connection must not be pruned merely for width.'),('deep-dark-seam',.025,'Two bright regions with a deep connecting valley should separate.'),('shallow-shading',.24,'Weak brightness variation should not certify another body.'),('one-body-deep-texture-ambiguity',.025,'Identical pixels to seam but same-body interpretation: image-only rule cannot distinguish this unobservable ownership.')]:
        lum,domain=field(bridge);mask,labels,group,refs,edges,markers=basins(lum,domain,domain,[24,32]);yy,xx=np.where(mask)
        results.append(dict(name=name,bridge=bridge,interpretation=interpretation,right_feature_retained=bool(mask[32,46]),connected_components=int(ndi.label(mask)[1]),support=support(np.c_[xx,yy]),native_field=lum.tolist(),saddles=edges,merged=group))
    save(OUT/'mechanisms.json',results)
    print([(r['name'],r['right_feature_retained']) for r in results])
if __name__=='__main__':main()
