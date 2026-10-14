"""Intensity mechanism controls, including an intentionally ambiguous counterexample.

These mathematical fields are not physical renderings. Fresh certified POV scenes
are evaluated separately. No control identities are supplied to the algorithms.
"""
import numpy as np
from photo2.r285.mechanisms import field
from .methods import watershed_support,ridge_barriers,path_support,marker_field
from .common import *

def main():
    rows=[]
    for name,level in [('deep-seam',.025),('shallow-shading',.24),('narrow-bright-continuation',.29),('ambiguous-deep-internal-texture',.025)]:
        lum,domain=field(level);variants={}
        for m in ('M','A','B','C'):
            if m in ('M','B'):mask,info,bar=watershed_support(lum,domain,domain,~domain,[24,32],m=='B')
            else:mask,blocked=path_support(lum,domain,[24,32],.3,ridge_barriers(lum,domain) if m=='A' else None);info=dict(blocked=blocked)
            y,x=np.where(mask);variants[m]=dict(support=support(np.c_[x,y]),right_feature_retained=bool(mask[32,46]),area=int(mask.sum()),evidence=info)
        rows.append(dict(name=name,bridge=level,native_Y=lum.tolist(),variants=variants))
    # A bright maximum whose one pixel fails pigment eligibility; valid local context.
    y,x=np.indices((31,31));lum=.01+.5*np.exp(-((x-15)**2+(y-15)**2)/30);domain=(x-15)**2+(y-15)**2<100;domain[15,15]=False;markers,target,ledger=marker_field(lum,domain,domain,np.zeros_like(domain),[14,15])
    save(OUT/'mechanisms.json',dict(fields=rows,excluded_peak_context=dict(ledger=ledger,target=target),limitations='Identical deep-seam/internal-texture pixels must yield identical proposals. Physical ownership cannot be recovered from these pixels alone. B false-splits the shallow .24 neck; retain this failure.'))
    from .review import plt,COLORS
    fig,axs=plt.subplots(3,5,figsize=(14,8))
    for i,q in enumerate(rows[:3]):
        field_=np.array(q['native_Y']);axs[i,0].imshow(field_,cmap='magma',vmin=0,vmax=.4);axs[i,0].set_title(q['name'])
        for j,m in enumerate(('M','A','B','C'),1):
            ax=axs[i,j];ax.imshow(field_,cmap='magma',vmin=0,vmax=.4);p=pixels(q['variants'][m]['support']);rgba=np.zeros((65,65,4));rgba[p[:,1],p[:,0]]=[0,1,1,.4];ax.imshow(rgba);ax.set_title(m+' / right retained '+str(q['variants'][m]['right_feature_retained']))
    for ax in axs.flat:ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle('Mathematical mechanism controls — B false-splits shallow shading; no retuning');fig.tight_layout();fig.savefig(REVIEW/'mechanisms.png',dpi=120);plt.close(fig)
if __name__=='__main__':main()
