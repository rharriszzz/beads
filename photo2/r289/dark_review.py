from .common import *
from .calibrate import eligible,predict

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=read(OUT/'associations.json.gz');models=read(OUT/'calibration-frozen.json')['models'];chosen=[]
    for col in ('red','yellow'):
        rr=eligible(rows,'R275',col,'evaluation');constant=models[f'R275/{col}/constant_weighted'];dark=models[f'R275/{col}/darkness']
        def gain(r):return np.linalg.norm(predict(r,'constant_weighted',constant)-r['centroid'])-np.linalg.norm(predict(r,'darkness',dark)-r['centroid'])
        r=(max if col=='red' else min)(rr,key=gain);chosen.append(dict(color=col,id=r['id'],gain_px=float(gain(r)),landmark=r['landmark']['id']))
        fig,axs=plt.subplots(1,2,figsize=(9,3),layout='constrained')
        for ax,p in zip(axs,r['landmark']['dark']['profiles']):
            for s in p['sides']:
                t=np.arange(21)*s['sign'];ax.plot(t,s['median'],label='left/up' if s['sign']<0 else 'right/down')
                if s['edge'] is not None:ax.axvline(s['edge']*s['sign'],color='black',ls='--',alpha=.5)
            ax.set(xlabel='Native offset from maximum (px)',ylabel='Median linear Y over five tracks',title='Horizontal' if p['axis']==0 else 'Vertical');ax.legend(fontsize=8);ax.grid(alpha=.2)
        fig.suptitle(f"{col} / {r['id']}: dark refinement improvement {gain(r):+.2f}px (negative = worse)")
        fig.savefig(REVIEW/('dark-'+col+'.png'),dpi=140);plt.close(fig)
    save(OUT/'dark-review.json',chosen)
if __name__=='__main__':main()
