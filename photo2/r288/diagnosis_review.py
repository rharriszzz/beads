"""Original native pixels and the demonstrated two-pair merge discontinuity."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r288-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from PIL import Image
from photo2.r285.run import local_mask
from photo2.r284b.methods import contour
from .common import *

def main():
    native,rgb,_=photo();cases=read(OUT/'diagnosis.json.gz')['cases']
    for q in cases[:3]:
        x,y=q['origin'];im=native[y:y+97,x:x+97];Image.fromarray(im).save(REVIEW/(q['name']+'-native.png'));runs=q['runs'];base=runs[0];alt=next(r for r in runs if r['name']==('background-high' if q['name']=='N11' else 'background-low'));fig,axs=plt.subplots(2,3,figsize=(12,8))
        axs[0,0].imshow(im);axs[0,0].set_title('Original photograph')
        for ax,r in zip(axs[0,1:],(base,alt)):
            ax.imshow(im);mask=local_mask(r['support'],np.array(q['origin']),(97,97));c=contour(mask);ax.plot(c[:,0],c[:,1],color='cyan');ax.set_title(f"{r['name']}: {r['area']} pixels")
        for ax,r in zip(axs[1,:2],(base,alt)):
            e=r['evidence'];ax.imshow(im);origin=np.array(e['local_origin']);target=e['target_marker'];edge=next((a for a in e['interfaces'] if target in a['markers'] and a['maximum_ratio']<.4),None)
            for row in e['marker_ledger']:
                if row['placed'] is not None:
                    p=np.array(row['placed'])+origin;ax.plot(*p,'+',color='white' if row['label'] in e['group'] else 'yellow',ms=8)
            if edge:
                pts=np.array(edge['interface']).reshape(-1,2)+origin;ax.scatter(pts[:,0],pts[:,1],color='red',s=15);ax.set_title(f"{r['name']}: {len(edge['interface'])} interface pairs\nmax/reference={edge['maximum_ratio']:.3f}; merged={not edge['separate_after_merging']}",fontsize=9)
            else:ax.set_title(r['name']+': target disconnected from upper region',fontsize=9)
        ax=axs[1,2];ax.axis('off');ax.text(0,1,'White markers: target merged group\nYellow: other photographic markers\nRed: exact interface pixels\n\nOriginal rule:\nseparate only if pairs >= 3\nAND maximum ratio < 0.65\n\nA 2-pair dark interface is merged,\neven at ratio 0.17–0.24.\n\nThis changes ownership abruptly;\nit does not discredit stable\ndiffuse pixels inside the target.',va='top',fontsize=11)
        for ax in list(axs[0])+list(axs[1,:2]):ax.set_xlim(0,96);ax.set_ylim(96,0);ax.set_xticks([]);ax.set_yticks([])
        fig.suptitle(q['name']+' — original M, causal interface diagnostic');fig.tight_layout();fig.savefig(REVIEW/(q['name']+'-diagnosis.png'),dpi=130);plt.close(fig)
if __name__=='__main__':main()
