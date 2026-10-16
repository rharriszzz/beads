"""Scientific figures from the frozen-data analysis; no fitting."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read
from .analyze import PRINCIPAL,LABELS


def main(results,output):
    output.mkdir(parents=True,exist_ok=True);d=read(results/'analysis.json');ledger=read(results/'ledger.json')
    colors=['#167c80','#d06b21','#9b42a0','#658d22','#315ab7','#9c443a']
    fig,axes=plt.subplots(6,3,figsize=(15,18),sharex=True,constrained_layout=True)
    for j,(name,label) in enumerate(zip(PRINCIPAL,LABELS)):
        rows=[r for r in ledger if r['model']==name];m=d['models'][name];s=m['groups']['centroid']['trusted'];seam=m['seam']['centroid']['fraction']
        for c in range(3):
            ax=axes[j,c]
            for r in rows:
                if not r['exists']:ax.plot(r['fraction']*100,0,'rx',ms=9);continue
                val=r['centroid_tn'][c] if c<2 else r['centroid_diameters']
                if r['trusted']:ax.scatter(r['fraction']*100,val,s=26,marker='o',facecolor='none' if r['ownership_ambiguous'] else colors[j],edgecolor=colors[j],alpha=.8)
                else:ax.scatter(r['fraction']*100,val,s=34,marker='x',color=colors[j],alpha=.8)
            if c<2:
                ax.axhline(0,color='.6',lw=.8)
                for reg in s['regions']:
                    if reg['n']:ax.plot([(reg['sector']+.1)*100/16,(reg['sector']+.9)*100/16],[reg['mean_tn'][c]]*2,color='black',lw=2)
                ax.set_ylim(-30,30)
            else:ax.set_ylim(0,1.2)
            ax.axvline(seam*100,color='crimson',ls='--',lw=1);ax.set_xlim(0,100);ax.grid(alpha=.15)
            if j==0:ax.set_title(['Parallel residual (px)','Normal residual (px)','Magnitude / local face diameter'][c])
            if c==0:ax.set_ylabel(label)
            if j==5:ax.set_xlabel('Photographic circuit from bead-zero reference (%)')
    fig.suptitle('Saved centroid residuals: prediction minus observation\nFilled = stronger + unambiguous owner; open = stronger + ambiguous owner; × = mixture or red missing; bars = sector means; dashed = index seam',fontsize=12)
    fig.savefig(output/'circuit-residuals.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(3,2,figsize=(14,11),constrained_layout=True)
    for j,(name,label) in enumerate(zip(PRINCIPAL,LABELS)):
        ax=axes.flat[j];rows=sorted([r for r in ledger if r['model']==name and r['trusted'] and r['exists']],key=lambda r:r['fraction']);m=d['models'][name]
        x=np.array([r['fraction'] for r in rows]);eq=np.array([r['centroid_index_equivalent'] for r in rows]);ax.scatter(x*100,eq,c=colors[j],s=23,label='Local displacement / axis pitch')
        ax.plot(x*100,eq-eq[0],c=colors[j],alpha=.45,ls=':',label='Net from first observed point (telescoping)')
        ax.axvline(m['seam']['centroid']['fraction']*100,color='crimson',ls='--');ax.axhline(0,color='.6',lw=.8);ax.set_title(label);ax.set_xlabel('Circuit (%)');ax.set_ylabel('Conditional index-equivalent units');ax.set_xlim(0,100);ax.set_ylim(-12,12);ax.grid(alpha=.2)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle('Displacement is not physical index error; sparse local owners cannot detect whole-turn slips\nDotted line is a difference from one observation, not independent cumulative-drift evidence')
    fig.savefig(output/'index-diagnostics.png',dpi=140);plt.close(fig)
    fig,axes=plt.subplots(3,1,figsize=(13,10),sharex=True,constrained_layout=True)
    for j,(name,label) in enumerate(zip(PRINCIPAL[:3],LABELS[:3])):
        m=d['models'][name];rr=[q for q in m['profiles'] if q['eligible']];x=np.array([q['fraction'] for q in rr])*100
        axes[0].scatter(x,[q['width_error'] for q in rr],s=14,label=label,color=colors[j],alpha=.65)
        axes[1].scatter(x,[q['common_edge_error'] for q in rr],s=14,label=label,color=colors[j],alpha=.65)
        ss=m['groups']['centroid']['trusted']['ordered'];axes[2].plot(np.r_[0,np.array(ss['fraction'])*100],ss['cusum_mean_parallel'],label=label,color=colors[j])
    for ax in axes:ax.axhline(0,color='.5',lw=.8);ax.legend();ax.grid(alpha=.15);ax.set_xlim(0,100)
    axes[0].set_ylabel('Signed transverse width error (px)');axes[1].set_ylabel('Common edge residual (px)');axes[2].set_ylabel('Demeaned parallel CUSUM / n (px)');axes[2].set_xlabel('Circuit (%)')
    fig.suptitle('Independent native edges and regional reflection bias\nCUSUM displays runs of signed bias; it is not an accumulated positioning error')
    fig.savefig(output/'geometry-and-bias.png',dpi=140);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,9),constrained_layout=True)
    from PIL import Image,ImageOps
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg'))
    from photo2.r297.geometry import reference
    ref=reference();a=(d['anchor_arc']+np.arange(16)/16*ref.length*d['direction'])%ref.length
    xy=np.array([[np.interp(v,ref.arc,ref.points[:,j]) for j in range(2)] for v in a])
    axes[0].imshow(im);axes[0].plot(ref.points[:,0],ref.points[:,1],color='cyan',lw=.7)
    for i,point in enumerate(xy):axes[0].text(*point,str(i),color='white',fontsize=9,bbox=dict(facecolor='black',alpha=.65,pad=1))
    rows=[r for r in ledger if r['model']=='joint-15']
    for r in rows:axes[0].plot(*r['observed_centroid'],marker='o' if r['trusted'] else 'x',color='yellow',ms=3)
    for j,(name,label,c) in enumerate(zip(PRINCIPAL[:3],LABELS[:3],colors)):
        xy0=d['models'][name]['seam_xy'][0];axes[0].plot(*xy0,marker='s',color=c,ms=7);axes[0].annotate(label+' seam',xy0,xytext=(30,45-22*j),textcoords='offset points',fontsize=8,color=c,bbox=dict(facecolor='white',alpha=.9,pad=2),arrowprops=dict(arrowstyle='-',color=c,lw=.8))
    axes[0].set_title('Original photo, common bins and true model seams');axes[0].axis('off')
    for j,(name,label) in enumerate(zip(PRINCIPAL,LABELS)):
        rr=[r for r in ledger if r['model']==name]
        for r in rr:axes[1].scatter(r['fraction']*100,j,marker='|' if r['exists'] else 'x',color=colors[j] if r['trusted'] else '.7',s=100)
    axes[1].set_yticks(range(6),LABELS);axes[1].set_xlabel('Circuit (%)');axes[1].set_xlim(0,100);axes[1].set_title('Observation coverage; × = missing prediction');axes[1].grid(alpha=.2)
    fig.savefig(output/'coverage.png',dpi=140);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=ROOT/'photo2/r300/results');p.add_argument('--output',type=Path,default=ROOT/'photo2/review/r300');a=p.parse_args();main(a.results,a.output)
