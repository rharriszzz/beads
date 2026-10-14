"""Native masks and independent photographic diagnostics for the R285 review."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r285-mpl')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from photo2.r282.common import ROOT,read,photo,pixels
from .select import OUT
from .run import local_mask
REVIEW=ROOT/'photo2/review/r285'
COLORS=dict(A='cyan',J='lime',D='orange',S='deepskyblue',G='magenta',P='white')

def panel(o,name,caption=''):
    native,_,_=photo();origin=np.array(o['origin']);x,y=origin;im=native[y:y+97,x:x+97];methods=list(o['variants']);fig,axs=plt.subplots(2,len(methods)+1,figsize=(3*(len(methods)+1),6.5));lum=np.array(o['native_Y']);smooth=ndi.gaussian_filter(lum,.65)
    curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points'])-origin;curve=curve[np.all((curve>=0)&(curve<97),axis=1)]
    for ax in axs.flat:ax.set_xticks([]);ax.set_yticks([])
    axs[0,0].imshow(im,interpolation='nearest');axs[0,0].set_title('Unmodified enlarged photo')
    axs[1,0].imshow(im,interpolation='nearest');axs[1,0].plot(48,48,'x',color='orange')
    if len(curve):axs[1,0].plot(curve[:,0],curve[:,1],color='white',lw=1)
    axs[1,0].set_title('Seed / image-only centerline')
    for ax,m in zip(axs[0,1:],methods):
        r=o['variants'][m];mask=local_mask(r['measured_support'],origin,lum.shape);ax.imshow(im,interpolation='nearest');c=np.array(r['subpixel_contour']).reshape(-1,2)-origin
        if len(c):ax.plot(c[:,0],c[:,1],color=COLORS[m],lw=.9)
        loc=r['measured_photo_location']
        if loc:ax.plot(*(np.array(loc)-origin),'+',color='white')
        met=r['metrics'];info=r['method_evidence'];ax.set_title(f"{m}: {met['area']}px / shift {met['centroid_shift'] or 0:.1f}px\n"+('domain-sensitive' if info.get('domain_sensitive') else ''))
    for ax,m in zip(axs[1,1:],methods):
        r=o['variants'][m];mask=local_mask(r['measured_support'],origin,lum.shape);ax.imshow(im,interpolation='nearest');rgba=np.zeros((*mask.shape,4));rgba[mask]=[0,1,1,.5];ax.imshow(rgba,interpolation='nearest');ax.set_title('Exact native support')
    for ax in axs.flat:ax.set_xlim(-.5,96.5);ax.set_ylim(96.5,-.5)
    fig.suptitle(name+' / '+o['color']+' — '+caption);fig.tight_layout();fig.subplots_adjust(hspace=.25,top=.84,bottom=.03);fig.savefig(REVIEW/(name+'-methods.png'),dpi=120);plt.close(fig)
    fig,axs=plt.subplots(1,3,figsize=(12,3.5))
    axs[0].imshow(im,interpolation='nearest');axs[0].axhline(48,color='white');axs[0].axvline(48,color='yellow');axs[0].set_title('Native horizontal / vertical routes')
    for ax,signal,label in [(axs[1],lum[48,:],'Horizontal'),(axs[2],lum[:,48],'Vertical')]:
        ax.plot(np.arange(97)-48,signal,color='black',lw=1,label='Native ICC luminance')
        for i,m in enumerate(methods):
            mask=local_mask(o['variants'][m]['measured_support'],origin,lum.shape);included=mask[48,:] if label=='Horizontal' else mask[:,48];ax.scatter(np.where(included)[0]-48,np.full(included.sum(),-.012*(i+1)),s=4,color=COLORS[m],label=m)
        ax.set_title(label+' brightness and included pixels');ax.set_xlabel('Native pixels from cue');ax.grid(alpha=.2)
    axs[1].legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(REVIEW/(name+'-profiles.png'),dpi=120);plt.close(fig)

def main(stage='development'):
    REVIEW.mkdir(parents=True,exist_ok=True);data=read(OUT/(stage+'.json.gz'));obs={o['id']:o for o in data['observations']};selection=read(OUT/'selection.json')
    if stage=='development':entries=[(r['example'],r['observation_id'],r['category']) for r in selection['development']]
    else:entries=[(f'v{i+1:02}',o['id'],'frozen confirmation') for i,o in enumerate(data['observations'])]
    for name,id,caption in entries:panel(obs[id],name,caption)
if __name__=='__main__':
    import sys
    main(sys.argv[1] if len(sys.argv)>1 else 'development')
