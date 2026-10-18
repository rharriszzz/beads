"""Exact restricted-frequency peak search; unchanged FFT and spectral objective.
The original routine zeroes all frequencies outside a small positive-x annulus,
then searches a million-element array. Search the identical nonzero rectangle
plus a >min_distance zero halo, preserving full-array peak coordinates/order.
"""
import numpy as np
from skimage.feature import peak_local_max
from photo2.r322.tracker import CONFIG

def directions(data):
    n=CONFIG['fft_size'];f=np.fft.fftshift(np.fft.fft2(data['z']*data['weight'],s=(n,n)))
    # The nonzero spectral disk radius is strictly less than .060*n.
    radius=int(np.ceil(.060*n));halo=8;mid=n//2
    y0=mid-radius-halo;y1=mid+radius+halo+1;x0=mid-halo;x1=mid+radius+halo+1
    fy,fx=np.meshgrid((np.arange(y0,y1)-mid)/n,(np.arange(x0,x1)-mid)/n,indexing='ij');rad=np.hypot(fx,fy)
    p=abs(f[y0:y1,x0:x1])**2;masked=p*((rad>.018)&(rad<.060)&(fx>0))
    loc=peak_local_max(masked,min_distance=6,num_peaks=24)
    ks=np.array([[fx[y,x],fy[y,x]] for y,x in loc]);powers=np.array([p[y,x] for y,x in loc])
    coords=np.argwhere(data['fg'])[:,::-1];_,vec=np.linalg.eigh(np.cov(coords.T));t=vec[:,-1];t*=np.sign(t[0]);normal=np.array([-t[1],t[0]])
    angles=np.degrees(np.arctan2(ks@normal,ks@t));triples=[]
    for i in range(len(ks)):
        for j in range(len(ks)):
            if not(-80<angles[i]<-25 and 25<angles[j]<80):continue
            for l in range(len(ks)):
                err=float(np.linalg.norm(ks[i]+ks[j]-ks[l]))
                if abs(angles[l])>=25 or err>=.008:continue
                score=float((powers[i]*powers[j]*powers[l])**(1/3)*np.exp(-.5*(err/CONFIG['spectral_closure_sigma'])**2))
                triples.append(dict(peaks=[i,j,l],score=score,closure_error=err))
    triples.sort(key=lambda a:-a['score'])
    if not triples:raise ValueError('No reciprocal triangle; abstain')
    selected=ks[triples[0]['peaks'][:2]]
    peaks=[dict(id=i,frequency_xy=k.tolist(),power=float(powers[i]),angle_relative_strip=float(angles[i])) for i,k in enumerate(ks)]
    return selected,dict(strip_tangent=t.tolist(),peaks=peaks,triangles=triples,selected=selected.tolist(),warning='Spectral normal directions, not point-to-point bead directions. All competing triples retained.')
