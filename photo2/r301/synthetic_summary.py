"""Summarize the compact pre-photo recovery diagnostics without further fitting."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r301-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .model import Local,NAMES
from .evidence import BASE,read,save

def main():
    out=[];fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for row,folder in enumerate(['before-maker-count','interim-6000-minimum']):
        records=read(BASE/f'checkpoints/{folder}/results/synthetic-summary.json.gz')
        for col,r in enumerate(records):
            known=r['name'].endswith('known');section=read(BASE/f'checkpoints/{folder}/evidence/{r["name"]}.json');truth=np.array(r['truth']);fit=np.array(r['selected']['parameters']);final=r['final'];train=final['train']['records'];held=final['withheld']['records'];errors=[x['error'] for x in train if x['error'] is not None]
            out.append(dict(regime=folder,name=r['name'],known_correspondence=known,observations=len(section['observations']),training=len(train),training_matched=len(errors),training_finite_rms=float(np.sqrt(np.mean(np.array(errors)**2))),withheld=len(held),withheld_matched=sum(x['error'] is not None for x in held),truth=dict(zip(NAMES,truth.tolist())),recovered=dict(zip(NAMES,fit.tolist())),parameter_errors=dict(zip(NAMES,(fit-truth).tolist())),seconds=r['elapsed'],conclusion='Positional fit does not demonstrate full parameter recovery; compare each dimension explicitly.'))
            ax=axes[row,col];ss=Local(truth,section,-1);fs=Local(fit,section,-1)
            for scene,color,alpha in [(ss,'#009e73',.45),(fs,'#d55e00',.30)]:
                for p in scene.polygons():ax.plot(p[:,0]-1200,p[:,1]-1400,color=color,alpha=alpha,lw=.6)
            obs=np.array([x['point'] for x in section['observations']]);ax.scatter(obs[:,0]-1200,obs[:,1]-1400,color='black',s=10,label='Native target observations')
            for x in train+held:
                if x['predicted'] is not None:ax.plot([x['observed'][0]-1200,x['predicted'][0]-1200],[x['observed'][1]-1400,x['predicted'][1]-1400],color='#0072b2',lw=1)
            ax.set(xlim=(-90,90),ylim=(90,-90),aspect='equal',title=f'{"Thin" if row else "Historical aspect"} / {"known owners" if known else "uncertain owners"}\naxial {truth[0]:.3f} → {fit[0]:.3f}; train RMS {out[-1]["training_finite_rms"]:.1f}px',xlabel='Native pixel offset',ylabel='Native pixel offset')
    fig.suptitle('Synthetic recovery diagnostic: green truth, orange recovered surfaces, blue errors\nIndependent native-ray targets versus coarse surface-quadrature search; shared mathematical model')
    fig.savefig(BASE/'results/synthetic-recovery.png',dpi=140);plt.close(fig);save(BASE/'results/synthetic-analysis.json',out)

if __name__=='__main__':main()
