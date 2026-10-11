"""Supplementary count admissibility, residue coverage and exact-control figures."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r254-mpl')
import csv,json,argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from pattern_r254 import OUT,diagnostic
from evidence_r254 import COL
import global_fit_r253 as old

def run(out):
    summary=list(csv.DictReader((out/'comparison.csv').open()));points=[]
    for n in range(2670,2701):
        for P in range(1,400):
            if n%P==0 and P%13:points.append((n,P))
    fig,ax=plt.subplots(figsize=(14,5));ax.scatter(*np.array(points).T,s=18,c='navy');ax.set(xticks=range(2670,2701),xlabel='Total bead count N',ylabel='Admissible template period P',title='A2: exact arithmetic filter — only divisors P<400, excluding P divisible by13');ax.tick_params(axis='x',rotation=90);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'A2-divisibility.png',dpi=170);plt.close(fig)
    mids=json.loads((out/'display-selection.json').read_text())['display'];fig,axs=plt.subplots(len(mids),1,figsize=(14,2.8*len(mids)),squeeze=False)
    for ax,mid in zip(axs[:,0],mids):
        s=next(s for s in summary if s['model_id']==mid);P=int(s['P_all']);rr=json.loads((out/f'{mid}-assignments.json').read_text());a=np.zeros((13,P),int)
        for r in rr:a[r['k']%13,r['k']%P]+=1
        ax.imshow(a,aspect='auto',origin='lower',vmin=0,vmax=3,cmap='Blues');ax.set(title=f'{mid}: P={P}; observed residue coverage (white=none); gcd(P,13)=1',ylabel='k mod13',xlabel='k modP');ax.set_yticks([0,6,12])
    fig.tight_layout();fig.savefig(out/'B2-residue-visibility.png',dpi=160);plt.close(fig)
    palette=['red','yellow','black','red','black','yellow','yellow'];rows=[dict(k=k,color=palette[k%7],observation_id=f'control-{k}') for k in range(35) if palette[k%7]!='black'];d=diagnostic(rows[:20],7,35)
    fig,axs=plt.subplots(3,1,figsize=(12,5));templates=[''.join(c[0].upper() for c in palette),d['template'],''.join(d['template'][k%7] for k in range(28,35))]
    for ax,text,title in zip(axs,templates,['H: known source P7, N35 (black is known only to this synthetic source)','Observed red/yellow constraints: withheld black positions stay ?','Independent next-repeat predictions: R/Y agree; ? remains unpredicted']):
        ax.imshow(np.array([to_rgb(COL[c]) for c in text])[None,:,:],aspect='auto');ax.set_xticks(range(7));ax.set_yticks([]);ax.set_title(title,fontsize=11)
        for i,c in enumerate(text):ax.text(i,0,c,ha='center',va='center',color='white' if c=='B' else 'black')
    fig.tight_layout();fig.savefig(out/'H-known-pattern-control.png',dpi=170);plt.close(fig)
    old.save(out/'known-pattern-control.json',dict(N=35,P=7,source_template=templates[0],training_observations=rows[:20],inferred_template=d['template'],heldout_observations=rows[20:],heldout_correct=sum(d['template'][r['k']%7]==r['color'][0].upper() for r in rows[20:])))
    # Raw and marked distributed stars: four widely separated training sectors.
    from PIL import Image
    from camera_r254 import Model,rays
    photo=Image.open(old.ROOT/'beads-photo-2.jpg').convert('RGB');mid=mids[0];m=json.loads((out/f'{mid}-camera.json').read_text());rows=json.loads((out/f'{mid}-assignments.json').read_text());model=Model(m['n'],m['h'],m['p'],m['focal'],m.get('turn_delta',0));geom=model.geometry(np.arange(m['n']))
    fig,axs=plt.subplots(4,2,figsize=(13,13));sectors=[1,9,17,25]
    for axes,sector in zip(axs,sectors):
        rr=[r for r in rows if r['sector']==sector and r['observation_id'] in m['stars']]
        if not rr:continue
        seed=rr[0];cx,cy=seed['x'],seed['y'];box=(int(cx)-125,int(cy)-120,int(cx)+125,int(cy)+120);extent=(box[0],box[2],box[3],box[1])
        for ax in axes:ax.imshow(photo.crop(box),extent=extent);ax.set(xlim=(box[0],box[2]),ylim=(box[3],box[1]))
        axes[0].set_title(f'Raw sector{sector}',fontsize=10);axes[1].set_title('Reserved conditional identities; green owns point, magenta fails',fontsize=9)
        xx,yy=np.meshgrid(np.arange(box[0],box[2],2),np.arange(box[1],box[3],2));own,_,un=rays(model,np.c_[xx.ravel(),yy.ravel()],geom);own=own.reshape(xx.shape)
        for r in rr:
            mask=(own==r['generator_index']).astype(float)
            if mask.any():axes[1].contour(xx,yy,mask,levels=[.5],colors='cyan',linewidths=.6)
            axes[1].plot(r['x'],r['y'],'+',color='lime' if r['owns_representative'] else 'magenta',ms=9);axes[1].text(r['x']+5,r['y']-5,f"{r['observation_id']}\nk={r['k']}",fontsize=7,color='white',bbox=dict(facecolor='black',alpha=.5,pad=.4))
    fig.suptitle(f'D2: geographically distributed identity checks, {mid}\nThese stars are conditional R253 identities, not newly maker-verified neighbor facts',fontsize=11);fig.tight_layout(rect=[0,0,1,.97]);fig.savefig(out/'D2-distributed-stars.png',dpi=160);plt.close(fig)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();run(a.output)
