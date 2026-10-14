"""Evaluate saved masks and native signal before introducing replacement methods."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r284b-mpl')
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import disk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r282.common import ROOT,read,save,photo,pixels
from photo2.r282.phase1 import image_features,attempts,component
from photo2.r284.assess import TARGETS

OUT=ROOT/'photo2/r284b/results'

def main():
    OUT.mkdir(parents=True,exist_ok=True);native,rgb,_=photo();f=image_features(rgb);results=[]
    for name,targets in TARGETS.items():
        case=read(ROOT/'photo2/r284/results'/f'{name}.json.gz')
        for label,xy in targets:
            r=min(case['methods']['A']['records'],key=lambda a:np.linalg.norm(np.array(a['seed'])-xy));x,y=map(int,r['seed']);origin=np.array([x-24,y-24]);sl=np.s_[y-24:y+25,x-24:x+25]
            p=pixels(r['measured_support'])-origin;m=np.zeros((49,49),bool);m[p[:,1],p[:,0]]=True
            base=next(a for a in attempts(f,[x,y]) if a['method']=='C');p0=pixels(base['region'])-origin;b=np.zeros_like(m);b[p0[:,1],p0[:,0]]=True
            dt=ndi.distance_transform_edt(b);radius=int(np.clip(round(dt.max()*.45),2,4));opened=component(ndi.binary_opening(b,structure=disk(radius)),[24,24]);restored=ndi.binary_dilation(opened)&b&~opened
            lum=f['lum'][sl];smooth=ndi.gaussian_filter(lum,.7);gx,gy=np.gradient(smooth)
            # Generic quadrant diagnostics are evaluation summaries, not cutting rules.
            yy,xx=np.indices(m.shape);quadrant=m&(xx<24)&(yy>24);qvals=lum[quadrant]
            center=np.mean(np.c_[xx[m],yy[m]],axis=0);core=np.mean(np.c_[xx[opened],yy[opened]],axis=0) if opened.any() else center
            item=dict(case=name,feature=label,seed=[x,y],A_area=int(m.sum()),pre_A_area=int(b.sum()),opening_radius=radius,
                maximum_thickness_radius=float(dt.max()),opened_area=int(opened.sum()),restored_pixels=int(restored.sum()),
                opening_centroid_shift=float(np.linalg.norm(center-core)),
                lower_left_pixels=int(quadrant.sum()),lower_left_Y_quantiles=np.quantile(qvals,[.1,.5,.9]).tolist() if len(qvals) else [],
                mask_Y_quantiles=np.quantile(lum[m],[.1,.5,.9]).tolist() if m.any() else [],
                centerline_interpretation=r['centerline'])
            results.append(item)
            fig,axs=plt.subplots(2,3,figsize=(12,8));axs[0,0].imshow(native[sl],interpolation='nearest');axs[0,0].contour(m,levels=[.5],colors=['cyan'],linewidths=.8);axs[0,0].plot(24,24,'x',color='orange');axs[0,0].set_title('Native photo + original A mask / cue')
            axs[0,1].imshow(dt,cmap='viridis');axs[0,1].contour(m,levels=[.5],colors=['white'],linewidths=.6);axs[0,1].set_title(f'Pre-A thickness; opening radius {radius}')
            rgbmask=np.zeros((49,49,3));rgbmask[opened]=[0,.7,.7];rgbmask[restored]=[1,.5,0];axs[0,2].imshow(rgbmask);axs[0,2].set_title('Opened core cyan; restored rim orange')
            axs[1,0].imshow(lum,cmap='magma');axs[1,0].contour(m,levels=[.5],colors=['cyan'],linewidths=.7);axs[1,0].set_title('Native linear Y, same mask')
            axs[1,1].imshow(np.hypot(gx,gy),cmap='gray');axs[1,1].contour(m,levels=[.5],colors=['cyan'],linewidths=.7);axs[1,1].set_title('Gradient of Y (sigma 0.7 native px)')
            for angle,lab in [(0,'horizontal'),(np.pi/2,'vertical'),(3*np.pi/4,'lower-left diagonal')]:
                t=np.arange(-20,21);px=np.rint(24+t*np.cos(angle)).astype(int);py=np.rint(24+t*np.sin(angle)).astype(int);axs[1,2].plot(t,lum[py,px],label=lab)
            axs[1,2].legend(fontsize=8);axs[1,2].set_xlabel('native px from cue');axs[1,2].set_ylabel('linear Y');axs[1,2].set_title('Native profiles; not fitted bead outlines')
            fig.suptitle(name+' / '+label);fig.tight_layout();fig.savefig(OUT/(name+'-'+label+'-diagnosis.png'),dpi=130);plt.close(fig)
    save(OUT/'diagnosis.json',results)
    print([{k:r[k] for k in ('feature','A_area','pre_A_area','opening_radius','maximum_thickness_radius','restored_pixels','opening_centroid_shift')} for r in results])

if __name__=='__main__':main()
