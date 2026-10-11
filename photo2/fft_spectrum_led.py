"""R248 development-only spectrum-led FFT replay; no helicity scorer or transfer.

Numerical masks/channels/FFT/peak finder come from pinned fft-image-explorer.
Selection decisions are explicit reviewed JSON, not an automatic three-peak rule.
"""
from __future__ import annotations
import argparse,csv,itertools,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-fft-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from photo2 import fft_explorer_core as core
from photo2.fft_helicity import ROOT,read,save,sha,image_rgb,inverse_pairs,wrap
BUNDLE=ROOT/'photo2/review/r248';OUT=ROOT/'photo2/output/r248'
WIDTHS=(20,30,40,55)
COLORS=['#00ffff','#ff9900','#44dd55','#ff55ff','#ffff22','#aaaaff','#ffffff','#ff7777']
LOW_STEPS=[0,.005,.010,.015,.020,.025,.030,.040]
HIGH_STEPS=[float(np.sqrt(.5)),.25,.15,.10,.08,.06,.05,.04,.03]


def prepare():
    BUNDLE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    if (BUNDLE/'sampling.json').exists():raise ValueError('Selection already saved; do not overwrite')
    old=read(ROOT/'photo2/review/r244/protocol.json');lookup={q['id']:q for q in old['sites']}
    sources=[('S1','Nearly straight, conspicuous yellow/black rows; native full support available.'),('S4','Straight section with prominent red bodies, some yellow and black; different orientation.'),('C6','Gently curved mixed-color section; more turning without the sharp concavity.')]
    dev=[]
    for i,(key,why) in enumerate(sources):
        q=dict(lookup[key]);q.update(id=f'D{i+1}',source_site=key,split='development',reason=why)
        q['sample_xy']=np.round(q['xy']).astype(int).tolist();dev.append(q)
    transfer=[]
    for i,key in enumerate(['S2','S3','S6','C1','C2','C5']):
        q=dict(lookup[key]);q.update(id=f'T{i+1}',source_site=key,split='reserved; do not compute');transfer.append(q)
    cfg=dict(request='R248',image=old['image'],image_sha256=old['image_sha256'],base_commit='1a42697c8b9b2a72ce320168ad9125d780a4a872',source_sampling_sha256=sha(ROOT/'photo2/review/r244/protocol.json'),development=dev,transfer=transfer,widths=list(WIDTHS),
             selection='Raw R244 crop overview and geometry only for this selection. Prior photo studied; not blind data. No new spectra before this file.',
             gaussian='Original native RGB, integer-centered circle, support radius=5sigma, source softness0.2. No rotation/resampling, mean removal, normalization, or width adaptation.',
             channels=dict(V='max(R,G,B)',Y='.299R+.587G+.114B'),
             display=dict(normalization='abs(F)/sum(G), amplitude in original channel units; dB=20log10. Display only, no image normalization.',full_db=[-80,0],detail_db=[-60,-20],detail_cycles_per_pixel=.12,weights_and_channels=[0,1]),
             replay=dict(lower_steps=LOW_STEPS,upper_steps=HIGH_STEPS,selection='Human visual decisions stored separately; these grids are a bounded exploration, not a bead-scale band. Refinements must be recorded.',budget='One common lower sweep, one upper sweep after a saved lower decision, optional one recorded refinement per case; paired V/Y same budget.'),
             candidates=dict(max_display_pairs=8,prominence_min=3.,separation_resolution=1.5,resolution='1/(2*pi*sigma) cycles/pixel',origin='excluded',cutoff_created_maxima='reject unless a local maximum in the original unfiltered spectrum',boundary='flag lobe clipping rather than declaring narrow bands precise'),
             stop='Development review only. No transfer computation, no selection freeze, no helicity scores.')
    rgb=image_rgb(ROOT/cfg['image'])
    for q in dev:
        x,y=q['sample_xy'];half=5*max(WIDTHS)
        assert half<=x<rgb.shape[1]-half and half<=y<rgb.shape[0]-half
    save(BUNDLE/'sampling.json',cfg)
    fig,ax=plt.subplots(figsize=(8,10),layout='constrained');ax.imshow(rgb)
    for q in dev+transfer:
        x,y=q['xy'];color='cyan' if q['split']=='development' else 'orange'
        ax.text(x+12,y,q['id']+' ('+q['source_site']+')',color=color,bbox=dict(facecolor='black',alpha=.6,pad=1));ax.plot(x,y,'o',c=color,ms=4)
    ax.set_title('D1–D3: development; T1–T6: predeclared, not evaluated\nAll locations reused as raw/geometry references, not selected by new spectra')
    fig.savefig(BUNDLE/'locations.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,6),layout='constrained')
    for ax,q in zip(axes,dev):
        x,y=q['sample_xy'];t=np.array(q['tangent']);ax.imshow(rgb);ax.plot([x-110*t[0],x+110*t[0]],[y-110*t[1],y+110*t[1]],c='cyan',lw=.8)
        for radius,c in [(20,'white'),(55,'yellow')]:ax.add_patch(Circle((x,y),radius,fill=False,color=c,lw=1))
        ax.set_xlim(x-140,x+140);ax.set_ylim(y+140,y-140);ax.set_title(f"{q['id']} from {q['source_site']}; tangent {q['tangent_deg']:.1f}°\nWhite sigma20, yellow sigma55; circles are not boundaries")
    fig.savefig(BUNDLE/'raw-crops.png',dpi=135);plt.close(fig)


def sample(rgb,q,sigma):
    x,y=np.round(q.get('sample_xy',q['xy'])).astype(int);h=int(5*sigma)
    if x-h<0 or y-h<0 or x+h>=rgb.shape[1] or y+h>=rgb.shape[0]:raise ValueError('Full five-sigma native crop unavailable')
    patch=rgb[y-h:y+h+1,x-h:x+h+1];g=core.make_mask(patch.shape[:2],'Ellipse/circle','Gaussian',h,h,10*sigma,10*sigma,0,.2)
    return patch,g,[int(x-h),int(y-h)]


def products(rgb,q,sigma,ch):
    patch,g,origin=sample(rgb,q,sigma);x=core.make_channel_bank(patch).arrays['HSV V' if ch=='V' else 'Y luminance']
    result=core.compute_fft_products(x,g,False,square_fft=False)
    f=result[6].astype(complex)
    assert f.shape==x.shape,'Source changed crop; native inverse overlay must be updated'
    n=len(f);c=n//2;yy,xx=np.mgrid[:n,:n];fx=(xx-c)/n;fy=(c-yy)/n
    return dict(patch=patch,g=g,x=x,f=f,rad=np.hypot(fx,fy),fx=fx,fy=fy,n=n,origin=origin,metadata=result[7],sigma=sigma)


def filter_fft(a,low,high):
    """Exact source radial-mask semantics on cached source complex FFT (tested)."""
    f=a['f'].copy()
    if low>0:f*=a['rad']>low
    if high>0:f*=a['rad']<=high
    return f


def db(a,f=None):
    return 20*np.log10(np.maximum(abs(a['f'] if f is None else f)/float(a['g'].sum()),1e-12))


def spectrum(ax,a,low=0,high=np.sqrt(.5),lim=.12,marks=None,full=False):
    f=filter_fft(a,low,high);ax.imshow(db(a,f),cmap='magma',origin='upper',extent=[-.5,.5,-.5,.5],vmin=-80 if full else -60,vmax=0 if full else -20)
    ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim)
    ticks=np.linspace(-lim,lim,5);labels=[f'{t:.3g}' for t in ticks]
    ax.set_xticks(ticks,labels);ax.set_yticks(ticks,labels);ax.tick_params(labelsize=7)
    if low>0:ax.add_patch(Circle((0,0),low,fill=False,color='cyan',lw=.7))
    if high<lim*1.5:ax.add_patch(Circle((0,0),high,fill=False,color='lime',lw=.7))
    for p in marks or []:
        k=np.array(p['offset'])/a['n'];color=COLORS[(p['candidate']-1)%len(COLORS)]
        for sign in (-1,1):ax.plot(*(k*sign),'o',mfc='none',mec=color,ms=7,mew=1)
        ax.text(*(k+.002),str(p['candidate']),c='white',fontsize=8,bbox=dict(facecolor='black',alpha=.5,pad=.2,edgecolor='none'))
    return f


def extract(a,low,high,tangent=0):
    f=filter_fft(a,low,high);n=a['n'];c=n//2;yy,xx=np.mgrid[:n,:n];power=abs(f)**2;raw=abs(a['f'])**2;res=n/(2*np.pi*a['sigma']);peaks=[];rejected=[]
    proposals=core.find_top_fft_peaks(np.log1p(abs(f)),top_k=80,min_distance=max(1,int(np.ceil(1.5*res))))
    used=[]
    for p in proposals:
        dx,dy=int(p['x']),int(p['y']);r=float(np.hypot(dx,dy));freq=r/n
        if r==0 or not low<freq<high:continue
        if any(min(np.hypot(dx-x,dy-y),np.hypot(dx+x,dy+y))<1.5*res for x,y in used):continue
        iy,ix=c-dy,c+dx;local=raw[max(0,iy-1):iy+2,max(0,ix-1):ix+2]
        if raw[iy,ix]<local.max()*(1-1e-12):
            rejected.append(dict(offset=[dx,dy],frequency=freq,reason='cutoff-created maximum, absent in unfiltered 3x3 neighborhood'));continue
        dist=np.minimum(np.hypot(xx-c-dx,c-yy-dy),np.hypot(xx-c+dx,c-yy+dy));ann=(dist>2*res)&(dist<4*res)&(power>0)
        prom=float(power[iy,ix]/max(float(np.median(power[ann])) if ann.any() else 0,1e-12))
        if prom<3:
            rejected.append(dict(offset=[dx,dy],frequency=freq,prominence=prom,reason='prominence below3'));continue
        support=(dist<=1.25*res)&(power>0);pairpower=float(power[support].sum());angle=float(wrap(np.degrees(np.arctan2(dy,dx))))
        peaks.append(dict(candidate=len(peaks)+1,offset=[dx,dy],frequency=freq,wavelength=1/freq,radius_bins=r,angle=angle,relative_angle=float(wrap(angle-tangent)),row_angle_relative=float(wrap(angle+90-tangent)),angle_uncertainty=float(np.degrees(np.arctan2(res,r))),frequency_resolution=res/n,prominence=prom,pair_power=pairpower,band_fraction=pairpower/max(float(power.sum()),1e-12),boundary_clipped=bool(min(freq-low,high-freq)<1.25*res/n),legacy_log_power_sum=p['log_power_sum']))
        used.append((dx,dy))
        if len(peaks)==8:break
    return dict(peaks=peaks,rejected=rejected,total_band_power=float(power.sum()),low=low,high=high,low_explorer_percent=100*np.sqrt(2)*low,high_explorer_percent=100*np.sqrt(2)*high,frequency_resolution=res/n)


def initial():
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image']);assert sha(ROOT/cfg['image'])==cfg['image_sha256'];summary=[]
    for q in cfg['development']:
        fig,axes=plt.subplots(4,5,figsize=(19,14),layout='constrained')
        for row,sigma in enumerate(WIDTHS):
            av=products(rgb,q,sigma,'V');ay=products(rgb,q,sigma,'Y');a=av;h=len(a['x'])//2
            axes[row,0].imshow(a['patch']);axes[row,0].set_xlim(h-3*sigma,h+3*sigma);axes[row,0].set_ylim(h+3*sigma,h-3*sigma);axes[row,0].set_title(f'{q["id"]} sigma{sigma}: raw ±3sigma')
            axes[row,1].imshow(a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title('V × circular Gaussian')
            for col,ch,aa in [(2,'V',av),(3,'Y',ay)]:
                spectrum(axes[row,col],aa);axes[row,col].set_title(ch+' unfiltered detail; fixed −60..−20dB')
                r=extract(aa,0,np.sqrt(.5),q['tangent_deg']);summary.append(dict(window=q['id'],sigma=sigma,channel=ch,**r))
            for ch,aa,color in [('V',av,'#cc4422'),('Y',ay,'#2255aa')]:
                bins=np.floor(aa['rad']*aa['n']).astype(int);sums=np.bincount(bins.ravel(),weights=(abs(aa['f'])**2).ravel());count=np.bincount(bins.ravel());rr=np.arange(len(sums))/aa['n'];mean=sums/np.maximum(count,1)/(float(aa['g'].sum())**2)
                axes[row,4].plot(rr,10*np.log10(np.maximum(mean,1e-24)),label=ch,c=color)
            axes[row,4].set_xlim(0,.12);axes[row,4].set_ylim(-90,0);axes[row,4].legend();axes[row,4].set_title('Mean power per frequency ring; no band selection');axes[row,4].grid(alpha=.2)
        fig.suptitle(q['id']+' unfiltered starting evidence; fixed physical frequency axes across widths and channels\nMean-per-ring profile is supporting evidence, not the three-direction detector. DC remains present.');fig.savefig(BUNDLE/(q['id']+'-starting.png'),dpi=120);plt.close(fig)
        for sigma in WIDTHS:
            fig,axes=plt.subplots(2,len(LOW_STEPS),figsize=(23,6),layout='constrained')
            for row,ch in enumerate(('V','Y')):
                a=products(rgb,q,sigma,ch)
                for col,low in enumerate(LOW_STEPS):
                    spectrum(axes[row,col],a,low,lim=.08);axes[row,col].set_title(f'{ch} lower={low:.3f}');axes[row,col].tick_params(labelsize=6)
            fig.suptitle(f'{q["id"]} sigma{sigma}: increase lower cutoff; upper remains unrestricted\nFixed −60..−20dB scale and ±0.08 cycles/pixel view. Cyan circles mark excluded centers, not detections.')
            fig.savefig(BUNDLE/f'{q["id"]}-s{sigma}-lower.png',dpi=110);plt.close(fig)
        print('Initial',q['id'],flush=True)
    save(OUT/'unfiltered-candidates.json',summary)


def upper():
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image'])
    decisions=read(BUNDLE/'lower-decisions.json')['rows'];trace=[]
    for q in cfg['development']:
        for sigma in WIDTHS:
            fig,axes=plt.subplots(2,len(HIGH_STEPS),figsize=(25,6),layout='constrained')
            for row,ch in enumerate(('V','Y')):
                a=products(rgb,q,sigma,ch);d=next(d for d in decisions if (d['window'],d['sigma'],d['channel'])==(q['id'],sigma,ch));low=d['low']
                for col,high in enumerate(HIGH_STEPS):
                    ax=axes[row,col]
                    if high<=low:ax.text(.1,.5,'Empty band');ax.set_axis_off();continue
                    spectrum(ax,a,low,high,lim=.12);ax.set_title(f'{ch}: {low:.3f} < f ≤ {high:.3f}');ax.tick_params(labelsize=6)
                    trace.append(dict(window=q['id'],sigma=sigma,channel=ch,**extract(a,low,high,q['tangent_deg'])))
            fig.suptitle(f'{q["id"]} sigma{sigma}: decrease upper cutoff after recorded lower decision\nSame fixed −60..−20dB and ±0.12 cycles/pixel. Removing outer coefficients cannot sharpen retained peaks.')
            fig.savefig(BUNDLE/f'{q["id"]}-s{sigma}-upper.png',dpi=110);plt.close(fig)
        print('Upper',q['id'],flush=True)
    save(OUT/'upper-candidates.json',trace)


def reciprocal_alternatives(peaks,n,resolution,tangent=0):
    """All nondegenerate signed-sum alternatives; necessary, not sufficient evidence.

    Resolution is a window-blur scale, NOT a statistical standard error.
    B columns are reciprocal vectors; direct columns A satisfy B.T @ A = I.
    No lattice primitive-cell, nearest-neighbor or physical-family claim follows.
    """
    alternatives=[]
    for triple in itertools.combinations(peaks,3):
        for third in range(3):
            a,b=[p for i,p in enumerate(triple) if i!=third];c=triple[third]
            ka,kb,kc=[np.array(p['offset'])/n for p in (a,b,c)]
            for sb,sc in itertools.product((-1,1),repeat=2):
                B=np.column_stack([ka,sb*kb])
                if abs(np.linalg.det(B))<.25*np.linalg.norm(ka)*np.linalg.norm(kb):continue
                err=float(np.linalg.norm(ka+sb*kb-sc*kc));scaled=err/(np.sqrt(3)*resolution)
                if scaled>1:continue
                A=np.linalg.inv(B).T
                alternatives.append(dict(basis_candidates=[a['candidate'],b['candidate']],basis_signs=[1,sb],third_candidate=c['candidate'],third_sign=sc,closure_error=err,resolution_ratio=scaled,direct_columns=A.T.tolist(),direct_lengths=np.linalg.norm(A,axis=0).tolist(),direct_angles_relative=[float(wrap(np.degrees(np.arctan2(v[1],v[0]))-tangent)) for v in A.T],any_clipped=any(p['boundary_clipped'] for p in triple)))
    return sorted(alternatives,key=lambda q:q['resolution_ratio'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','initial','upper']);args=p.parse_args();globals()[args.stage]()
