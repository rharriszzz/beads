"""R249 reporting only; never changes frozen extraction or thresholds."""
import csv,itertools
import numpy as np
from photo2.fft_transfer import BUNDLE,verify_freeze,read,save,sha,ROOT,products,image_rgb,match_triplets
from photo2.fft_spectrum_led import spectrum,filter_fft,inverse_pairs,COLORS
from photo2.fft_spectrum_led_evidence import card,photo_view,write_csv
import matplotlib.pyplot as plt


def main():
    cfg=verify_freeze();data=read(BUNDLE/'transfer.json');assert data['freeze_sha256']==sha(BUNDLE/'freeze.json')
    records=data['records'];assessment=read(BUNDLE/'assessment.json');rgb=image_rgb(ROOT/cfg['image'])
    fig,axes=plt.subplots(2,3,figsize=(14,11),layout='constrained')
    for ax,q in zip(axes.ravel(),cfg['sites']):
        a=products(rgb,q,30,'V');photo_view(ax,a,a['patch']);c=a['n']//2;t=np.array(q['tangent']);ax.plot([c-50*t[0],c+50*t[0]],[c-50*t[1],c+50*t[1]],c='cyan',lw=1)
        ax.set_title(f"{q['id']} ({q['source_site']}), tangent {q['tangent_deg']:.1f}°\nNative raw crop ±60px; cyan centerline tangent")
    fig.suptitle('All six reserved sites, unchanged centers; primary circular σ30 native pixels');fig.savefig(BUNDLE/'raw-sites.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,9),layout='constrained');ax.imshow(rgb)
    for q in cfg['sites']:
        x,y=q['xy'];ax.plot(x,y,'o',c='cyan');ax.text(x+15,y,q['id'],c='white',bbox=dict(facecolor='black',alpha=.6,pad=1))
    ax.set_title('R249: six previously reserved locations');fig.savefig(BUNDLE/'locations.png',dpi=130);plt.close(fig)
    for q in cfg['sites']:
        fig,axes=plt.subplots(2,4,figsize=(16,9),layout='constrained')
        for row,ch in enumerate(('V','Y')):
            r=next(r for r in records if (r['window'],r['channel'],r['variant'])==(q['id'],ch,'primary'));a=products(rgb,q,30,ch)
            st=next(x for x in assessment if (x['window'],x['channel'])==(q['id'],ch))
            card(q,a,r,ch,BUNDLE/f'{q["id"]}-{ch}-individual.png')
            photo_view(axes[row,0],a,a['patch']);axes[row,0].set_title(ch+': raw ±60 native pixels')
            photo_view(axes[row,1],a,a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title(ch+' × circular Gaussian')
            spectrum(axes[row,2],a,r['low'],r['high'],lim=.10,marks=r['peaks'][:4]);axes[row,2].set_title('Brightest4, central cut only\n'+st['status'],fontsize=10)
            inv=inverse_pairs(filter_fft(a,r['low'],r['high']),r['peaks'][:4],lobes=True,resolution=1.25*a['n']*r['frequency_resolution']);m=max(float(abs(inv).max()),1e-12)
            photo_view(axes[row,3],a,inv,cmap='RdBu_r',vmin=-m,vmax=m);axes[row,3].set_title(f'All4 lobe neighborhoods: inverse\nSeparate signed scale ±{m:.3f}')
        fig.suptitle(q['id']+': identical native support, σ30 and lower0.01061, no upper cut\nFFT scale fixed −60..−20dB. Numerical support is not a verified physical-family assignment.');fig.savefig(BUNDLE/f'{q["id"]}-comparison.png',dpi=140);plt.close(fig)
        fig,axes=plt.subplots(2,5,figsize=(19,8),layout='constrained')
        for col,v in enumerate(cfg['variants']):
            for row,ch in enumerate(('V','Y')):
                r=next(r for r in records if (r['window'],r['channel'],r['variant'])==(q['id'],ch,v['name']));a=products(rgb,q,v['sigma'],ch)
                spectrum(axes[row,col],a,r['low'],r['high'],lim=.10,marks=r['peaks'][:4]);ids=[t['candidates'] for t in r['trios'] if t['supported']]
                axes[row,col].set_title(f"{ch} {v['name']}, σ{v['sigma']}\nlow{r['low']:.4f}; trios {ids}",fontsize=9)
        fig.suptitle(q['id']+': all predetermined checks, same contrast/frequency axes\nPrimary stays primary; no successful diagnostic setting substitutes for a failure.');fig.savefig(BUNDLE/f'{q["id"]}-sensitivity.png',dpi=125);plt.close(fig)
        print('Evidence',q['id'],flush=True)
    rows=[]
    for r in records:
        for p in r['peaks']:
            rows.append(dict(window=r['window'],channel=r['channel'],variant=r['variant'],s=r['s'],sigma=r['sigma'],lower=r['low'],rank=p['candidate'],shortlisted=p['shortlisted'],frequency=p['frequency'],wavelength=p['wavelength'],reciprocal_angle=p['angle'],relative_angle=p['relative_angle'],spatial_band_relative=p['row_angle_relative'],angle_resolution=p['angle_uncertainty'],frequency_resolution=p['frequency_resolution'],peak_power=p['peak_bin_power'],relative_brightness=p['relative_brightness'],prominence=p['prominence'],weak=p['weak'],clipped=p['boundary_clipped'],physical_assignment='unassigned'))
    write_csv(BUNDLE/'peaks.csv',rows)
    fig,axes=plt.subplots(2,2,figsize=(14,10),sharex=True,layout='constrained')
    colors=plt.get_cmap('tab10')
    for r in records:
        if r['variant']!='primary':continue
        row=0 if r['channel']=='V' else 1;color=colors(int(r['window'][1:])-1)
        for p in r['peaks'][:4]:
            axes[row,0].errorbar(r['s'],p['relative_angle'],yerr=p['angle_uncertainty'],fmt='x' if p['weak'] or p['boundary_clipped'] else 'o',c=color,ms=5,alpha=.8)
            axes[row,1].errorbar(r['s'],p['frequency'],yerr=p['frequency_resolution'],fmt='x' if p['weak'] or p['boundary_clipped'] else 'o',c=color,ms=5,alpha=.8)
        axes[row,0].text(r['s'],100,r['window'],ha='center',c=color,fontsize=9)
    for row,ch in enumerate(('V','Y')):
        axes[row,0].set_ylim(-110,115);axes[row,0].set_ylabel(ch+' reciprocal angle − tangent (°)')
        axes[row,1].set_ylabel(ch+' frequency (cycles/native pixel)');axes[row,1].set_ylim(0,.11)
    for ax in axes.ravel():ax.grid(alpha=.2);ax.set_xlabel('Centerline arc distance (native pixels)')
    fig.suptitle('All four primary candidates at each site; no forced tracks\nBars = window blur scales, not confidence intervals; × weak or central-clipped. Frequency is rotationally invariant.');fig.savefig(BUNDLE/'directions-frequency.png',dpi=140);plt.close(fig)
    # Both channels in a single tangent-aligned reciprocal frame, with dev references.
    fig,axes=plt.subplots(2,3,figsize=(14,10),layout='constrained')
    for ax,q in zip(axes.ravel(),cfg['sites']):
        for ref in cfg['references']:
            for p in ref['peaks']:
                t=np.radians(p['relative_angle']);k=p['frequency']*np.array([np.cos(t),np.sin(t)])
                ax.plot([k[0],-k[0]],[k[1],-k[1]],'.',c='.75',ms=5)
        for ch,color,marker in [('V','#e65c00','o'),('Y','#0055cc','x')]:
            r=next(r for r in records if (r['window'],r['channel'],r['variant'])==(q['id'],ch,'primary'))
            for i,p in enumerate(r['peaks'][:4]):
                t=np.radians(p['relative_angle']);k=p['frequency']*np.array([np.cos(t),np.sin(t)])
                ax.plot([k[0],-k[0]],[k[1],-k[1]],marker,c=color,ms=6,mfc='none',label=ch if i==0 else None)
                ax.text(*k,str(i+1),color=color,fontsize=8)
        ax.set_aspect('equal');ax.set_xlim(-.1,.1);ax.set_ylim(-.1,.1);ax.grid(alpha=.2);ax.legend();ax.set_title(q['id']);ax.set_xlabel('Along tangent frequency');ax.set_ylabel('Perpendicular frequency')
    fig.suptitle('Measured reciprocal vectors rotated by local tangent only\nOrange V / blue Y; gray = four frozen development-reference trios. No scaling, shear or camera fitting.');fig.savefig(BUNDLE/'tangent-frame.png',dpi=140);plt.close(fig)


if __name__=='__main__':main()
