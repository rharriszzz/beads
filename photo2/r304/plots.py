"""Export standalone scientific plots, alongside interactive sequence inspection."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r304-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .model import *

def main():
    for name in FAMILIES:
        d=read(BASE/f'results/{name}-correspondences.json');rr=[r for r in d['records'] if r['strong'] and r['index'] is not None];rolling=d['rolling'];m=read(BASE/f'results/{name}.json.gz');axis={b['index']:b['photo_arc'] for b in m['positions']}
        for coordinate,label in [('index','Conditional bead index from S1 registration'),('photo_arc','Photographic arc distance from S1 registration (px)')]:
            fig,axs=plt.subplots(4,1,figsize=(10,11),sharex=True,constrained_layout=True);x=[r[coordinate] for r in rr];rx=[r[coordinate] for r in rolling]
            axs[0].scatter(x,[r['error_px'] for r in rr],s=22,c=['#138474' if r['status']=='confident conditional' else '#d08228' for r in rr],label='Strong observations, conditional pairs')
            axs[0].plot(rx,[r['rms'] if r['n']>=3 else np.nan for r in rolling],color='#205b9c',label='50-position rolling RMS (≥3 pairs)');axs[0].plot(rx,[r['median'] if r['n']>=3 else np.nan for r in rolling],color='#861ea6',label='Rolling median');axs[0].set_ylabel('Position error (px)');axs[0].legend(fontsize=8)
            for field,color in [('tangent_px','#c15329'),('normal_px','#2483a7')]:axs[1].scatter(x,[r[field] for r in rr],s=12,color=color,alpha=.55,label=field.replace('_px',''));axs[1].plot(rx,[r[field.replace('_px','_mean')] if r['n']>=3 else np.nan for r in rolling],color=color)
            axs[1].axhline(0,color='gray',lw=.6);axs[1].set_ylabel('Signed residual (px)');axs[1].legend(fontsize=8)
            groups=d['groups'];gx=[(r['first']+r['last'])/2 if coordinate=='index' else (axis[r['first']]+axis[r['last']])/2 for r in groups]
            for key,color in [('strong_observations','#2483a7'),('unmatched_observations','#c15329'),('unmatched_predictions','#861ea6')]:axs[2].plot(gx,[r[key] for r in groups],'-o',ms=3,label=key.replace('_',' '),color=color)
            axs[2].set_ylabel('Count / 50 positions');axs[2].legend(fontsize=8)
            oc=d['ordinal_control'];axs[3].plot([r[coordinate] for r in oc],[r['error_px'] for r in oc],color='#777777',label='No-gap ordinal control (incomplete catalog)');axs[3].set_ylabel('No-gap error (px)');axs[3].legend(fontsize=8);axs[3].set_xlabel(label)
            for ax in axs:
                ax.grid(alpha=.2)
                for a,b,col in [(17,55,'#e0bd87'),(110,180,'#becfdd')]:
                    lo=a if coordinate=='index' else axis[a];hi=b if coordinate=='index' else axis[b];ax.axvspan(lo,hi,color=col,alpha=.25)
            fig.suptitle(f'{name} · continuous 350-position forward model\nOrange band: curve splice; blue: top into bend. Pairing gaps remain explicit.',fontsize=12)
            suffix='index' if coordinate=='index' else 'arc';fig.savefig(REVIEW/f'{name}-errors-{suffix}.png',dpi=140);fig.savefig(BASE/f'results/{name}-errors-{suffix}.svg');plt.close(fig)
            svg=BASE/f'results/{name}-errors-{suffix}.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
if __name__=='__main__':main()
