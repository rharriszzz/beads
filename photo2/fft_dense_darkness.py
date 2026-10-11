"""Maker's black-bead discontinuity hypothesis: descriptive dark-proxy check.
No segmentation, bead labels, extraction changes or causal inference.
"""
import numpy as np
from scipy.stats import spearmanr
from photo2.fft_dense import *


def corr(a,b):
    return float(spearmanr(a,b).statistic) if np.std(a)>0 and np.std(b)>0 else None


def regress(y,X):
    X=np.column_stack([np.ones(len(y)),X]);beta=np.linalg.lstsq(X,y,rcond=None)[0];res=y-X@beta
    return res,float(1-np.sum(res**2)/np.sum((y-y.mean())**2))


def main():
    import matplotlib.pyplot as plt
    d=load_measurements(2000);length=d['length'];tracks=read(BUNDLE/'tracks.json');stats=[];rows=[]
    fig,axes=plt.subplots(2,3,figsize=(16,9),layout='constrained')
    for row,ch in enumerate(('V','Y')):
        rs=[r for r in d['records'] if r['channel']==ch];t=tracks[ch];inc={e['target'] for e in t['associations'] if e['accepted']};out={e['source'] for e in t['associations'] if e['accepted']}
        dark=np.array([r['dark_proxy'] for r in rs]);gradient=abs((np.roll(dark,-1)-np.roll(dark,1))/(2*length/2000))
        endpoints=np.array([sum(p['observation'] not in inc or p['observation'] not in out for p in r['peaks'][:4]) for r in rs]);ss=np.array([r['s'] for r in rs]);curvature=np.abs([r['curvature'] for r in rs]);unsupported=np.array([not any(tr['supported'] for tr in r['trios']) for r in rs])
        for width in (60,120,240):
            groups=(ss/width).astype(int);means=[]
            for k in np.unique(groups):
                m=groups==k;actual=min(width,length-k*width)
                r=dict(channel=ch,bin_width=width,s=float(ss[m].mean()),dark=float(dark[m].mean()),dark_gradient=float(gradient[m].mean()),curvature=float(curvature[m].mean()),endpoints_per100px=float(endpoints[m].sum()/actual*100),unsupported_fraction=float(unsupported[m].mean()));means.append(r);rows.append(r)
            x=np.array([r['dark'] for r in means]);g=np.array([r['dark_gradient'] for r in means]);k=np.array([r['curvature'] for r in means]);y=np.array([r['endpoints_per100px'] for r in means]);bad=np.array([r['unsupported_fraction'] for r in means])
            ry,r2k=regress(y,k[:,None]);rx,_=regress(x,k[:,None]);rg,_=regress(g,k[:,None]);_,r2full=regress(y,np.column_stack([k,x,g]))
            stats.append(dict(channel=ch,width=width,bins=len(means),dark_endpoint_rho=corr(x,y),dark_change_endpoint_rho=corr(g,y),curvature_endpoint_rho=corr(k,y),dark_endpoint_partial_after_curvature=corr(rx,ry),dark_change_endpoint_partial_after_curvature=corr(rg,ry),dark_unsupported_trio_rho=corr(x,bad),curvature_only_in_sample_R2=r2k,curvature_plus_dark_and_change_in_sample_R2=r2full))
            if width==120:
                for ax,xx,label in zip(axes[row],(x,g,k),('Gaussian dark fraction','Absolute dark-fraction gradient / pixel','Absolute curvature / pixel')):
                    ax.scatter(xx,y,c=k,cmap='viridis',s=24);ax.set_xlabel(label);ax.set_ylabel(ch+' top-four endpoints / 100px');ax.grid(alpha=.2);ax.set_title(f'Spearman rho = {corr(xx,y):+.2f}')
    fig.suptitle('Black/dark appearance hypothesis: observed association with tracking breaks\n120px bins; point color = curvature. V<0.2 is a dark-pixel proxy, not black-bead identity. No causal or majority attribution.')
    fig.savefig(BUNDLE/'darkness-discontinuities.png',dpi=140);plt.close(fig)
    save(BUNDLE/'darkness-analysis.json',dict(hypothesis='Maker proposes black-bead appearance differences explain most discontinuities.',proxy='Gaussian-weighted HSV V<0.2 fraction over full native crop. Black reflections may be bright; red shadows/background can be dark. This proxy cannot identify black-bead-specific causality.',outcome='Number of top-four measured candidates without accepted incoming or outgoing neighbor link; normalize by arc span. Tentative gaps do not suppress endpoints.',statistics='Descriptive Spearman and in-sample linear R2 on fixed arc bins. Partial Spearman computed on linear residuals after curvature. No independent-sample p-values; adjacent windows overlap.',results=stats));write_csv(BUNDLE/'darkness-bins.csv',rows)
    print(stats)


if __name__=='__main__':main()
