"""Brightness mechanism controls, including preserved narrow-bridge failure."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r288-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r285.mechanisms import field
from photo2.r286.methods import watershed_support
from .methods import positive_watershed
from .methods_v1 import positive_watershed as first
from .common import *

def main():
    rows=[];fig,axs=plt.subplots(3,4,figsize=(12,8))
    for i,(name,level) in enumerate([('deep-seam',.025),('shallow-shading',.24),('narrow-bright',.29),('identical-deep-texture',.025)]):
        lum,dm=field(level);f=dict(smooth=lum,pigment=dm,domain=dm,paper=~dm,seed=[24,32]);m,mi,_=watershed_support(lum,dm,dm,~dm,[24,32],False);v,vi=first(f);w,wi=positive_watershed(f);variants={}
        for method,mask,info in [('M',m,mi),('W-v1',v,vi),('W',w,wi)]:
            y,x=np.where(mask);variants[method]=dict(support=support(np.c_[x,y]),right_feature_retained=bool(mask[32,46]),area=int(mask.sum()),evidence=info)
        rows.append(dict(name=name,level=level,variants=variants))
        if i<3:
            axs[i,0].imshow(lum,cmap='magma');axs[i,0].set_title(name)
            for ax,(method,mask) in zip(axs[i,1:],[('M',m),('W-v1',v),('W',w)]):
                ax.imshow(lum,cmap='magma');ax.contour(mask,levels=[.5],colors=['cyan']);ax.set_title(method+' / right '+str(bool(mask[32,46])))
    for ax in axs.flat:ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle('Mathematical controls: first corridor rule split valid narrow material; failure retained');fig.tight_layout();fig.savefig(REVIEW/'mechanisms.png',dpi=130);plt.close(fig)
    save(OUT/'mechanisms.json',dict(fields=rows,limits='Mathematical fields, not physical renders or real precision. Identical deep seam/texture cannot yield different ownership without additional evidence.'))
    print([(q['name'],{m:r['right_feature_retained'] for m,r in q['variants'].items()}) for q in rows])
if __name__=='__main__':main()
