"""Photo review only: exact native supports and independent diagnostic plots."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r286-mpl')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from photo2.r285.run import local_mask
from .common import *
COLORS=dict(J='lime',S='deepskyblue',M='orange',A='magenta',B='cyan',C='yellow')
LABELS=dict(J='Original J',S='Original S',M='M: marker repair',A='A: dark ridges',B='B: protected basins',C='C: direct valleys')

def panel(o,name,native):
    origin=np.array(o['origin']);x,y=origin;im=native[y:y+97,x:x+97];lum=np.array(o['native_Y']);methods=list(o['variants']);Image.fromarray(im).save(REVIEW/(name+'-native.png'));fig,axs=plt.subplots(3,7,figsize=(21,9))
    curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-origin;curve=curve[np.all((curve>=0)&(curve<97),axis=1)]
    for ax in axs[:2].flat:ax.imshow(im,interpolation='nearest');ax.set_xticks([]);ax.set_yticks([]);ax.set_xlim(-.5,96.5);ax.set_ylim(96.5,-.5)
    axs[0,0].set_title('Raw photo enlarged');axs[1,0].plot(48,48,'x',color='orange')
    if len(curve):axs[1,0].plot(curve[:,0],curve[:,1],color='white',lw=1)
    axs[1,0].set_title('Input cue / image centerline');axs[2,0].imshow(lum,cmap='magma');axs[2,0].axhline(48,color='white',lw=1);axs[2,0].axvline(48,color='cyan',lw=1);axs[2,0].set_title('Native Y / profile routes');axs[2,0].set_xticks([]);axs[2,0].set_yticks([])
    for col,m in enumerate(methods,1):
        r=o['variants'][m];mask=local_mask(r['measured_support'],origin,(97,97));c=np.array(r['subpixel_contour']).reshape(-1,2)-origin;bar=pixels(r['barrier_pixels'])-origin
        if len(c):axs[0,col].plot(c[:,0],c[:,1],color=COLORS[m],lw=.8)
        if r['measured_photo_location']:axs[0,col].plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white')
        axs[0,col].set_title(LABELS[m]+f"\n{mask.sum()}px / ΔS {r['metrics']['centroid_shift'] or 0:.2f}px",fontsize=10)
        rgba=np.zeros((97,97,4));rgba[mask]=[0,1,1,.45];axs[1,col].imshow(rgba,interpolation='nearest')
        if len(bar):axs[1,col].scatter(bar[:,0],bar[:,1],s=1,c='red',alpha=.65)
        axs[1,col].set_title('Exact native fill / red barrier\n'+r['centerline']['side']+f"; near={r['centerline']['near']}",fontsize=9)
        ax=axs[2,col];ax.plot(lum[48,:],label='horizontal');ax.plot(lum[:,48],label='vertical');level=r['method_evidence'].get('level')
        if level is not None:ax.axhline(level,ls='--',color='gray')
        ax.scatter(np.where(mask[48,:])[0],lum[48,mask[48,:]],s=3,c=COLORS[m]);ax.legend(fontsize=6);ax.set_title('Native brightness / selected pixels',fontsize=9)
    fig.suptitle(name+' — measured photographic centroids; masks are not full physical silhouettes');fig.tight_layout();fig.subplots_adjust(hspace=.35,top=.89);fig.savefig(REVIEW/(name+'-all.png'),dpi=125);plt.close(fig)
    fig,axs=plt.subplots(1,5,figsize=(15,3.5))
    for ax in axs:ax.imshow(im,interpolation='nearest');ax.set_xlim(12,84);ax.set_ylim(84,12);ax.set_xticks([]);ax.set_yticks([])
    axs[0].set_title('Original pixels enlarged')
    for ax,m in zip(axs[1:4],('J','S','B')):
        r=o['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
        if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=1)
        if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white')
        ax.set_title(LABELS[m]+f" / {r['metrics']['area']}px")
    s=local_mask(o['variants']['S']['measured_support'],origin,(97,97));b=local_mask(o['variants']['B']['measured_support'],origin,(97,97));rgba=np.zeros((97,97,4));rgba[s&~b]=[1,0,0,.65];rgba[b&~s]=[0,1,0,.65];axs[4].imshow(rgba,interpolation='nearest');axs[4].set_title('B vs S: red lost / green gained');fig.suptitle(name+' / '+o['color']);fig.tight_layout();fig.savefig(REVIEW/(name+'-choice.png'),dpi=135);plt.close(fig)

def main(stage='development'):
    native,_,_=photo();data=read(OUT/(stage+'.json.gz'))
    for case in data['cases']:
        o=min(case['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-case['seed']));panel(o,case['name'],native)
        if stage=='confirmation':
            origin=np.array(case['seed'])-80;x,y=origin;im=native[y:y+161,x:x+161];Image.fromarray(im).save(REVIEW/(case['name']+'-group-native.png'));fig,axs=plt.subplots(1,4,figsize=(14,4))
            for ax,m in zip(axs,('raw','J','S','B')):
                ax.imshow(im,interpolation='nearest');ax.set_xticks([]);ax.set_yticks([]);ax.set_xlim(0,160);ax.set_ylim(160,0);ax.set_title(m+' — all independent nearby cues')
                if m=='raw':continue
                cc=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-origin;cc=cc[np.all((cc>=0)&(cc<=160),axis=1)]
                if len(cc):ax.plot(cc[:,0],cc[:,1],color='white',lw=.8)
                for o in case['observations']:
                    r=o['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
                    if len(c):ax.plot(c[:,0],c[:,1],lw=.65,color=COLORS[m],alpha=.8)
                    if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white',ms=4)
            fig.suptitle(case['name']+' / '+case['stratum']+' — overlapping proposals remain uncertain');fig.tight_layout();fig.savefig(REVIEW/(case['name']+'-group.png'),dpi=135);plt.close(fig)
if __name__=='__main__':
    import sys
    main(sys.argv[1] if len(sys.argv)>1 else 'development')
