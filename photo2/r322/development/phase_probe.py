import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r322-mpl')
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from skimage.measure import find_contours
from skimage.restoration import unwrap_phase
q=np.load('photo2/r322/development/preflight.npz');rgb=q['rgb'];fg=q['fg'];z=q['z'];h,w=z.shape
y,x=np.mgrid[:h,:w]
ks=[(.01953,-.02930),(.02637,.01953)]
fig,ax=plt.subplots(figsize=(14,10));ax.imshow(rgb,extent=(1180,1540,520,130));ax.set_xlim(1180,1540);ax.set_ylim(410,210)
phases=[]
for k,c in zip(ks,['cyan','lime']):
    carrier=k[0]*x+k[1]*y
    zz=z*fg*np.exp(-2j*np.pi*carrier)
    env=ndi.gaussian_filter(zz.real,35)+1j*ndi.gaussian_filter(zz.imag,35)
    phase=carrier+unwrap_phase(np.ma.array(np.angle(env),mask=~fg),rng=0).filled(np.nan)/(2*np.pi)
    phases.append(phase)
    phase[~ndi.binary_erosion(fg,iterations=6)]=np.nan
    cs=ax.contour(x+1180,y+130,phase,levels=np.arange(-20,30),colors=c,linewidths=.8)
    ax.clabel(cs,fontsize=7)
fig.savefig('photo2/r322/development/phase-probe.png',dpi=130,bbox_inches='tight')
np.savez_compressed('photo2/r322/development/phases.npz',phases=phases)
