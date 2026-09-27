"""R099: local paper/necklace transition review; no recovered silhouette."""
import argparse
import csv
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import gaussian_filter

from background_probe import ROOT, digest

SIGMAS = (48., 24., 12., 6.)
HALF = 144  # Fixed FFT grid: avoid changing frequency bins with window sigma.
PATHS = [
    dict(id='T1', title='Right section: yellow bead toward shadowed paper',
         start=[2200,1170], direction=[1,0], reason='P moved onto the visible yellow face; Q lies beyond the dark shadow.'),
    dict(id='T2', title='Inner bend: yellow bead toward shadowed paper',
         start=[1780,1702], direction=[1,0], reason='P moved off an internal dark seam onto a yellow face; Q is outward on paper.'),
    dict(id='T3', title='Upper section: dark bead toward paper below',
         start=[1410,275], direction=[0,1], reason='P samples the dark bead region near a glint; its exact interior status remains provisional. Q is on paper below.'),
]
PAPER = [(1100+dx,950+dy) for dx in (-24,0,24) for dy in (-24,0,24)] + [
    (450+dx,2350+dy) for dx in (-24,0,24) for dy in (-24,0,24)]
DISTANCES = np.arange(0,193,4)


class Probe:
    def __init__(self, sigma):
        y,x = np.mgrid[-HALF:HALF+1,-HALF:HALF+1]
        self.w = np.exp(-(x*x+y*y)/(2*sigma*sigma))
        self.w2 = self.w**2
        self.a = np.stack([np.ones_like(x),x/sigma,y/sigma],-1)
        a = self.a.reshape(-1,3)
        self.project = np.linalg.solve(a.T@(self.w.ravel()[:,None]*a),a.T*self.w.ravel())
        f = np.fft.fftfreq(len(x))
        self.freq = np.hypot(f[:,None],f[None,:])
        self.norm = self.w.size*self.w2.sum()

    def measure(self, patch, spatial=None):
        raw = abs(np.fft.fft2(patch*self.w))**2
        residual = patch-self.a@(self.project@patch.ravel())
        power = abs(np.fft.fft2(residual*self.w))**2
        result = {'raw_total_power':float(raw.sum()/self.norm),
                  'residual_total_power':float(power.sum()/self.norm)}
        for name, mask in [('dc',self.freq>0),('64',self.freq>=1/64),('32',self.freq>=1/32)]:
            raw_kept = float(raw[mask].sum()/self.norm)
            kept = float(power[mask].sum()/self.norm)
            result['raw_rms_'+name] = np.sqrt(raw_kept)
            result['raw_fraction_'+name] = raw_kept/result['raw_total_power'] if result['raw_total_power']>1e-20 else 0.
            result['detrended_rms_'+name] = np.sqrt(kept)
            result['detrended_fraction_'+name] = kept/result['residual_total_power'] if result['residual_total_power']>1e-20 else 0.
        if spatial is not None:
            result['spatial_rms'] = float(np.sqrt(np.sum(self.w2*spatial**2)/self.w2.sum()))
        return {k:float(v) for k,v in result.items()}


def crop(a,x,y):
    p = a[y-HALF:y+HALF+1,x-HALF:x+HALF+1]
    assert p.shape==(2*HALF+1,2*HALF+1), (x,y,p.shape)
    return p


def controls(probes):
    y,x=np.mgrid[-HALF:HALF+1,-HALF:HALF+1]
    result=[]
    for sigma,p in probes.items():
        flat=p.measure(np.full(x.shape,.5))
        ramp=p.measure(.5+.0005*x+.0003*y)
        wave=p.measure(.5+.1*np.sin(2*np.pi*x/16))
        dim=p.measure(.25+.05*np.sin(2*np.pi*x/16))
        assert flat['residual_total_power']<1e-20
        assert ramp['residual_total_power']<1e-20
        assert abs(dim['detrended_rms_64']/wave['detrended_rms_64']-.5)<1e-10
        assert abs(dim['raw_fraction_64']-wave['raw_fraction_64'])<1e-12
        expected=np.sum((.5*p.w)**2)/p.w2.sum()
        assert abs(flat['raw_total_power']-expected)<1e-12
        result.append(dict(sigma=sigma,constant_raw_dc_fraction=flat['raw_fraction_dc'],
                           constant_raw_64_rms=flat['raw_rms_64'],
                           constant_detrended_64_rms=flat['detrended_rms_64']))
    assert crossing(np.r_[np.full(10,4.),np.ones(39)],2.)==38.
    assert crossing(np.ones(49),2.) is None
    assert crossing(np.full(49,4.),2.) is None
    return result


def crossing(values, threshold):
    above=np.asarray(values)>threshold
    if not above[0] or above[-1] or not above.any():
        return None
    last=int(np.flatnonzero(above)[-1])
    return float((DISTANCES[last]+DISTANCES[last+1])/2)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r099')
    args=parser.parse_args(); out=args.output; out.mkdir(parents=True,exist_ok=True)
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    rgb=np.asarray(im)/255.; gray=rgb@np.array([.299,.587,.114])
    spatial=gray-gaussian_filter(gray,4,mode='reflect')
    probes={s:Probe(s) for s in SIGMAS}; synthetic=controls(probes)
    rows=[]
    for s,p in probes.items():
        for i,(x,y) in enumerate(PAPER):
            rows.append(dict(group='paper',id=str(i),distance=-1,x=x,y=y,sigma=s,
                             **p.measure(crop(gray,x,y),crop(spatial,x,y))))
        for path in PATHS:
            for distance in DISTANCES:
                x,y=np.array(path['start'])+distance*np.array(path['direction'])
                rows.append(dict(group='path',id=path['id'],distance=int(distance),x=int(x),y=int(y),sigma=s,
                                 **p.measure(crop(gray,x,y),crop(spatial,x,y))))
    with (out/'samples.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    metrics=('detrended_rms_64','detrended_rms_32','spatial_rms')
    references={s:{m:max(r[m] for r in rows if r['group']=='paper' and r['sigma']==s) for m in metrics} for s in SIGMAS}
    candidates=[]
    for path in PATHS:
        for s in SIGMAS:
            selected=[r for r in rows if r['id']==path['id'] and r['group']=='path' and r['sigma']==s]
            for m in metrics:
                for margin in (1.5,2.,3.):
                    threshold=margin*references[s][m]
                    candidates.append(dict(id=path['id'],sigma=s,metric=m,margin=margin,threshold=threshold,
                                           distance=crossing([r[m] for r in selected],threshold)))
    summary={}
    for path in PATHS:
        cs=[c for c in candidates if c['id']==path['id'] and c['sigma']<=24]
        valid=[c['distance'] for c in cs if c['distance'] is not None]
        summary[path['id']]=dict(score_crossing_spread=[min(valid),max(valid)] if valid else None,
                                valid=len(valid),unresolved=len(cs)-len(valid))
        start=np.array(path['start']); end=start+192*np.array(path['direction']); mid=(start+end)/2
        fig=plt.figure(figsize=(12,11)); gs=fig.add_gridspec(4,3,height_ratios=[1.5,.22,1,1])
        for k,title in enumerate(('Raw context','Proposed P and Q only','Sampling route: distance from P')):
            ax=fig.add_subplot(gs[0,k]); ax.imshow(im)
            ax.set_xlim(mid[0]-170,mid[0]+170); ax.set_ylim(mid[1]+170,mid[1]-170)
            ax.set_title(title,fontsize=11); ax.set_axis_off()
            if k:
                for name,point in [('P',start),('Q',end)]:
                    ax.plot(*point,'o',mfc='none',mec='white',ms=7)
                    ax.annotate(name,point,xytext=(7,7),textcoords='offset points',color='white',weight='bold')
            if k==2:
                ax.plot([start[0],end[0]],[start[1],end[1]],color='cyan',lw=1)
                for t in (48,96,144):
                    point=start+t*np.array(path['direction']); ax.plot(*point,'+',color='white')
                    ax.annotate(str(t),point,xytext=(5,7),textcoords='offset points',color='white',fontsize=8)
                ax.add_patch(Circle(mid,24,fill=False,color='yellow',lw=1))
        ax=fig.add_subplot(gs[1,:]); xy=start[None,:]+DISTANCES[:,None]*np.array(path['direction'])[None,:]
        strip=rgb[xy[:,1],xy[:,0]][None,:,:]
        ax.imshow(strip,extent=(0,192,0,1),aspect='auto'); ax.set_yticks([])
        ax.set_title('Sampled pixel colors in travel order P → Q; yellow circle above = sigma 24 px',fontsize=10)
        colors=plt.get_cmap('tab10').colors
        for panel,m in [(2,'detrended_rms_64'),(3,'spatial_rms')]:
            ax=fig.add_subplot(gs[panel,:])
            for i,s in enumerate(SIGMAS):
                selected=[r for r in rows if r['id']==path['id'] and r['group']=='path' and r['sigma']==s]
                ax.plot(DISTANCES,[r[m]/references[s][m] for r in selected],color=colors[i],label=f'sigma {s:g}')
            for margin in (1.5,2,3):ax.axhline(margin,color='gray',lw=.6,ls='--')
            span=summary[path['id']]['score_crossing_spread']
            if span:ax.axvspan(*span,color='gray',alpha=.15,label='score-crossing spread; NOT a verified edge')
            ax.set_ylabel('RMS / maximum paper-control RMS')
            ax.set_title('Detrended FFT: frequencies ≥ 1/64 cycles/pixel' if panel==2 else 'Spatial texture: grayscale minus sigma-4 Gaussian blur')
            ax.set_xlim(0,192); ax.legend(fontsize=8,ncol=3); ax.set_xlabel('Distance from P (original-photo pixels)')
        fig.suptitle(path['id']+': '+path['title']+'\n'+path['reason'],fontsize=11)
        fig.tight_layout(rect=(0,0,1,.94)); fig.savefig(out/(path['id']+'.png'),dpi=135); plt.close(fig)

    fig,axes=plt.subplots(3,3,figsize=(11,11))
    for row,path in enumerate(PATHS):
        start=np.array(path['start']); direction=np.array(path['direction'])
        end=start+192*direction; mid=(start+end)/2
        for col,title in enumerate(('Raw photograph','Route P to Q; distances in pixels','Score-crossing spread ONLY')):
            ax=axes[row,col]; ax.imshow(im)
            ax.set_xlim(mid[0]-140,mid[0]+140); ax.set_ylim(mid[1]+140,mid[1]-140)
            ax.set_axis_off(); ax.set_title(path['id']+': '+title,fontsize=9)
            if col==1:
                ax.plot([start[0],end[0]],[start[1],end[1]],color='cyan',lw=1)
                for t in (0,48,96,144,192):
                    pt=start+t*direction; ax.plot(*pt,'+',color='white')
                    ax.annotate({0:'P (0)',192:'Q (192)'}.get(t,str(t)),pt,
                                xytext=(-4 if t==192 else 4,-15 if t==192 else 7),ha='right' if t==192 else 'left',
                                textcoords='offset points',color='white',fontsize=8)
            if col==2:
                lo,hi=summary[path['id']]['score_crossing_spread']; normal=np.array([-direction[1],direction[0]])
                a,b=start+lo*direction,start+hi*direction
                ax.add_patch(Polygon([a-14*normal,a+14*normal,b+14*normal,b-14*normal],closed=True,facecolor='cyan',edgecolor='cyan',alpha=.4))
                ax.text(.02,.02,f'{lo:g}–{hi:g} px from P; not a confidence interval',transform=ax.transAxes,fontsize=8,color='white',bbox=dict(facecolor='black',alpha=.6))
    fig.suptitle('Where competing scores cross their thresholds\nCyan boxes show method disagreement, not recovered bead edges',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.95)); fig.savefig(out/'edge-review.png',dpi=145); plt.close(fig)

    fig,axes=plt.subplots(2,3,figsize=(12,7))
    p=probes[24.]; f=np.fft.fftshift(p.freq)
    for ax,(name,mask) in zip(axes[0],[('Remove DC only',f>0),('Exclude radius 1/64',f>=1/64),('Exclude radius 1/32',f>=1/32)]):
        ax.imshow(mask,origin='lower',extent=(-.5,.5,-.5,.5),cmap='gray',vmin=0,vmax=1)
        ax.set_xlim(-.08,.08); ax.set_ylim(-.08,.08); ax.set_title(name+'\nblack excluded; white retained')
        ax.set_xlabel('cycles / original pixel')
    for ax,path in zip(axes[1],PATHS):
        selected=[r for r in rows if r['group']=='path' and r['id']==path['id'] and r['sigma']==24]
        for m,label in [('raw_fraction_dc','DC only / raw power'),('raw_fraction_64','high band / raw power'),('detrended_fraction_64','high band / detrended power')]:
            ax.plot(DISTANCES,[r[m] for r in selected],label=label)
        ax.set_title(path['id']+': fractions, sigma 24'); ax.set_ylim(0,1.05); ax.set_xlabel('Distance from P (pixels)'); ax.legend(fontsize=7)
    fig.suptitle('Frequency exclusion and power denominators must be explicit'); fig.tight_layout()
    fig.savefig(out/'filters-and-fractions.png',dpi=135); plt.close(fig)
    report=dict(source_sha256=digest(ROOT/'beads-photo-2.jpg'),script_sha256=digest(__file__),
                helper_sha256=digest(ROOT/'photo2/background_probe.py'),sigmas=SIGMAS,half_support=HALF,
                paths=PATHS,paper_centers=PAPER,distances=DISTANCES.tolist(),
                rejected_initial_starts={'T1':[2180,1170],'T2':[1760,1690]},
                rejected_reason='Initial preview put P near an internal seam; moved onto visible yellow face before measurements.',
                channel='JPEG grayscale .299R+.587G+.114B',spatial_blur_sigma=4,
                threshold_margins=[1.5,2,3],threshold_reference='max of 18 overlapping paper-control windows, per sigma and metric',
                edge_padding='none for FFT patches; global spatial Gaussian uses reflect at distant photo edge',
                synthetic=synthetic,checks=['constant and ramp removed','amplitude scaling','fraction scaling invariance','Parseval normalization','known crossing and unresolved endpoint controls'],
                samples=len(rows),references=references,candidates=candidates,summary=summary,
                versions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),
                artifacts={p.name:digest(p) for p in sorted(out.iterdir()) if p.suffix in ('.png','.csv')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(samples=len(rows),summary=summary,synthetic=synthetic),indent=2))


if __name__=='__main__':main()
