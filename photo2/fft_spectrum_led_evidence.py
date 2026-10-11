"""Reproduce R248 development evidence from recorded visual decisions only."""
import csv
import itertools
import numpy as np
from photo2.fft_spectrum_led import (BUNDLE,OUT,ROOT,WIDTHS,COLORS,read,save,sha,image_rgb,
    products,filter_fft,spectrum,extract,inverse_pairs,reciprocal_alternatives,LOW_STEPS,HIGH_STEPS)
import matplotlib.pyplot as plt


def photo_view(ax,a,im,**kwargs):
    ax.imshow(im,**kwargs);c=a['n']//2;s=a['sigma']
    ax.set_xlim(c-2*s,c+2*s);ax.set_ylim(c+2*s,c-2*s);ax.tick_params(labelsize=6)


def card(q,a,r,ch,path):
    fig,axes=plt.subplots(4,4,figsize=(18,17),layout='constrained');f=filter_fft(a,r['low'],r['high'])
    photo_view(axes[0,0],a,a['patch']);axes[0,0].set_title('Raw native photograph (±2σ)')
    photo_view(axes[0,1],a,a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[0,1].set_title(ch+' × circular Gaussian (same crop)')
    spectrum(axes[0,2],a,lim=.5,full=True);axes[0,2].set_title('Unfiltered FULL FFT; −80..0 dB')
    spectrum(axes[0,3],a,lim=.10);axes[0,3].set_title('Unfiltered detail; −60..−20 dB')
    axes[1,0].imshow(a['g'],cmap='gray',vmin=0,vmax=1);axes[1,0].set_title('Circular Gaussian; full ±5σ support')
    spectrum(axes[1,1],a,r['low'],r['high'],lim=.10,marks=r['peaks']);axes[1,1].set_title('Filtered, up to 8 alternatives; same dB')
    recon=np.fft.ifft2(np.fft.ifftshift(f)).real;m=max(float(abs(recon).max()),1e-12)
    photo_view(axes[1,2],a,recon,cmap='RdBu_r',vmin=-m,vmax=m);axes[1,2].set_title(f'All retained band coefficients: inverse\nSymmetric ±{m:.3g}, signed channel units')
    axes[1,3].set_axis_off();axes[1,3].text(0,.97,
        f"{len(r['peaks'])} qualified alternatives; NOT physical labels\n"
        f"{sum(p['boundary_clipped'] for p in r['peaks'])} potentially clipped lobes\n"
        f"Resolution scale δf = {r['frequency_resolution']:.4f} cy/px\n"
        "Origin excluded; cutoff-created maxima rejected.\n\n"
        "Each lower panel: individual real inverse (left),\nraw photo with its positive crests (right).\n"
        "Two complex conjugate bins, original phase.\nSeparate symmetric display range per pair;\n"
        "brightness here does not compare strengths.\nNo dewindowing or bead-center inference.\n\n"
        "* = within 1.25δf of a cutoff.\n"
        "Angles are reciprocal, tangent-relative.\nSpatial bands are perpendicular to these vectors.\n"
        "Family 1/6/7 and helicity remain unassigned.",va='top',fontsize=10,linespacing=1.5)
    for ax,i in zip(axes[2:].ravel(),range(8)):
        ax.set_axis_off()
        if i>=len(r['peaks']):ax.text(.1,.5,'No additional qualified pair');continue
        p=r['peaks'][i];inv=inverse_pairs(f,[p]);amp=max(float(abs(inv).max()),1e-12)
        left=ax.inset_axes([0,.03,.48,.88]);right=ax.inset_axes([.51,.03,.48,.88])
        photo_view(left,a,inv,cmap='RdBu_r',vmin=-amp,vmax=amp);photo_view(right,a,a['patch'])
        right.contour(inv,levels=[.95*amp],colors=[COLORS[i]],linewidths=.7)
        ax.set_title(f"{i+1}{'*' if p['boundary_clipped'] else ''}: f={p['frequency']:.4f}, θrel={p['relative_angle']:.1f}°\n±{amp:.3g}; left inverse / right positive crests",fontsize=10,color='black')
    fig.suptitle(f"{q['id']} sigma {a['sigma']} native pixels — {ch}; {r['low']:.3f} < f ≤ {r['high']:.3f} cycles/pixel\nProvisional visual review band; all retained candidates shown, no selected three-family solution",fontsize=15)
    fig.savefig(path,dpi=120);plt.close(fig)


def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image']);assert sha(ROOT/cfg['image'])==cfg['image_sha256']
    decisions=read(BUNDLE/'band-decisions.json')['rows'];records=[];cross=[];trace=[];csvrows=[]
    for q in cfg['development']:
        fig,axes=plt.subplots(2,4,figsize=(16,9),layout='constrained')
        for col,sigma in enumerate(WIDTHS):
            ds=[d for d in decisions if d['window']==q['id'] and d['sigma']==sigma]
            for row,ch in enumerate(('V','Y')):
                a=products(rgb,q,sigma,ch);d=next(d for d in ds if d['channel']==ch)
                r=extract(a,d['low'],d['high'],q['tangent_deg'])
                alts=reciprocal_alternatives(r['peaks'],a['n'],r['frequency_resolution'],q['tangent_deg'])
                rec=dict(window=q['id'],s=q['s'],sigma=sigma,channel=ch,lower_ambiguous=d['ambiguous'],physical_assignment='unassigned',n=a['n'],**r,reciprocal_alternatives=alts)
                records.append(rec);card(q,a,r,ch,BUNDLE/f'{q["id"]}-s{sigma}-{ch}.png')
                spectrum(axes[row,col],a,d['low'],d['high'],lim=.10,marks=r['peaks'])
                axes[row,col].set_title(f"{ch} σ{sigma}: {d['low']:.3f}..{d['high']:.3f}\n{len(r['peaks'])} candidates; {sum(p['boundary_clipped'] for p in r['peaks'])} clipped")
                for p in r['peaks']:
                    csvrows.append(dict(window=q['id'],s=q['s'],sigma=sigma,channel=ch,low=r['low'],high=r['high'],candidate=p['candidate'],frequency=p['frequency'],radius_bins=p['radius_bins'],wavelength=p['wavelength'],reciprocal_angle=p['angle'],tangent_relative_angle=p['relative_angle'],spatial_band_relative_angle=p['row_angle_relative'],resolution_angle_scale=p['angle_uncertainty'],frequency_resolution=p['frequency_resolution'],prominence=p['prominence'],pair_power=p['pair_power'],band_fraction=p['band_fraction'],boundary_clipped=p['boundary_clipped'],physical_assignment='unassigned'))
                for bd in ds:
                    cr=extract(a,bd['low'],bd['high'],q['tangent_deg'])
                    cross.append(dict(window=q['id'],sigma=sigma,channel=ch,band_from=bd['channel'],**cr))
                # Preserve the full bounded search numerically, including failed/empty stages.
                states=[('lower',lo,np.sqrt(.5)) for lo in LOW_STEPS]+[('upper',d['low'],hi) for hi in HIGH_STEPS]
                for stage,lo,hi in states:
                    tr=extract(a,lo,hi,q['tangent_deg']) if hi>lo else dict(low=lo,high=hi,peaks=[],rejected=[],failure='empty band')
                    trace.append(dict(window=q['id'],sigma=sigma,channel=ch,stage=stage,**tr))
            print(q['id'],sigma,flush=True)
        fig.suptitle(q['id']+' width/channel comparison: identical physical axes and display scaling\nNumbers are per-panel candidate IDs, not tracked families. Full inverse cards linked in report.');fig.savefig(BUNDLE/f'{q["id"]}-comparison.png',dpi=130);plt.close(fig)
    save(BUNDLE/'measurements.json',records);save(BUNDLE/'cross-applied-bands.json',cross);save(BUNDLE/'search-trace.json',trace);write_csv(BUNDLE/'peaks.csv',csvrows)
    # Matched-band channel comparison where manual lower choices differ.
    differing=[(q,s) for q in cfg['development'] for s in WIDTHS if len({(d['low'],d['high']) for d in decisions if d['window']==q['id'] and d['sigma']==s})>1]
    fig,axes=plt.subplots(len(differing)*2,2,figsize=(10,5*len(differing)),layout='constrained')
    for i,(q,sigma) in enumerate(differing):
        ds=[d for d in decisions if d['window']==q['id'] and d['sigma']==sigma]
        for row,ch in enumerate(('V','Y')):
            a=products(rgb,q,sigma,ch)
            for col,bd in enumerate(ds):
                r=extract(a,bd['low'],bd['high'],q['tangent_deg']);ax=axes[2*i+row,col]
                spectrum(ax,a,bd['low'],bd['high'],lim=.10,marks=r['peaks']);ax.set_title(f"{q['id']} σ{sigma} {ch}; band from {bd['channel']}\n{bd['low']:.3f}..{bd['high']:.3f}, {len(r['peaks'])} candidates")
    fig.suptitle('Cross-applied bands: each column uses identical V/Y cutoffs\nSame fixed display scale; compare evidence, not candidate count alone');fig.savefig(BUNDLE/'cross-applied.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(2,4,figsize=(17,8),sharex=True,sharey=True,layout='constrained')
    for r in records:
        ax=axes[0 if r['channel']=='V' else 1,list(WIDTHS).index(r['sigma'])]
        for p in r['peaks']:
            ax.errorbar(r['s'],p['row_angle_relative'],yerr=p['angle_uncertainty'],fmt='x' if p['boundary_clipped'] else 'o',ms=4,c={'D1':'#118833','D2':'#dd5522','D3':'#4466bb'}[r['window']],alpha=.6)
        ax.set_title(f"{r['channel']} σ{r['sigma']}");ax.set_ylim(-110,110);ax.grid(alpha=.2)
    for ax in axes[-1]:ax.set_xlabel('Centerline arc distance (native pixels)')
    for ax in axes[:,0]:ax.set_ylabel('Spatial-band angle relative to tangent (°)')
    fig.suptitle('All candidate spatial-band directions at THREE development sites only\nBlue D3 / orange D2 / green D1; × cutoff-clipped. Bars = window-resolution scale, NOT confidence intervals.\nNo tracks or physical 1/6/7 assignments; these widely separated sites do not establish continuity.');fig.savefig(BUNDLE/'direction-candidates.png',dpi=130);plt.close(fig)


def focus():
    """Post-selection review illustrations; no changes to saved selections."""
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image']);records=read(BUNDLE/'measurements.json')
    fig,axes=plt.subplots(4,3,figsize=(13,16),layout='constrained')
    for group,(site,sigma,refch) in enumerate([('D1',30,'V'),('D2',20,'Y')]):
        q=next(q for q in cfg['development'] if q['id']==site)
        ref=next(r for r in records if (r['window'],r['sigma'],r['channel'])==(site,sigma,refch))
        for row,ch in enumerate(('V','Y')):
            a=products(rgb,q,sigma,ch);r=next(r for r in records if (r['window'],r['sigma'],r['channel'])==(site,sigma,ch));ax=axes[2*group+row]
            photo_view(ax[0],a,a['patch']);ax[0].set_title(f'{site} σ{sigma} {ch}: raw')
            # Hold reference band's exact bounds and coefficient coordinates in both channels.
            same=extract(a,ref['low'],ref['high'],q['tangent_deg'])
            spectrum(ax[1],a,ref['low'],ref['high'],lim=.09,marks=ref['peaks'][:3]);ax[1].set_title(f'Fixed {refch} band and proposed A/B/C bins\n{ref["low"]:.3f}..{ref["high"]:.3f}; labels 1/2/3 local only')
            inv=inverse_pairs(filter_fft(a,ref['low'],ref['high']),ref['peaks'][:3],lobes=True,resolution=1.25*a['n']/(2*np.pi*sigma));m=max(float(abs(inv).max()),1e-12)
            photo_view(ax[2],a,inv,cmap='RdBu_r',vmin=-m,vmax=m);ax[2].set_title(f'Three lobe neighborhoods, phase retained\nOwn display range ±{m:.3f}; no dewindowing')
    fig.suptitle('Examples for review: V candidate trio at D1, Y candidate trio at D2\nReference locations in the other channel are marked even when not qualified maxima there.\nThese are provisional reciprocal families A/B/C, not physical directions 1/6/7.');fig.savefig(BUNDLE/'channel-examples.png',dpi=130);plt.close(fig)

    # One explicit refinement per channel at the ambiguous D3/s20 case.
    refinement=read(BUNDLE/'refinement-decision.json');q=next(q for q in cfg['development'] if q['id']=='D3');rs=[]
    fig,axes=plt.subplots(2,4,figsize=(15,8),layout='constrained')
    for row,ch in enumerate(('V','Y')):
        a=products(rgb,q,20,ch)
        for col,lo in enumerate([refinement['alternative_low'],refinement['original_low']]):
            r=extract(a,lo,refinement['high'],q['tangent_deg']);rs.append(dict(channel=ch,**r))
            spectrum(axes[row,2*col],a,lo,refinement['high'],lim=.08,marks=r['peaks']);axes[row,2*col].set_title(f'{ch}: {lo:.3f}..{refinement["high"]:.3f}\n{len(r["peaks"])} candidates, {sum(p["boundary_clipped"] for p in r["peaks"])} clipped')
            inv=np.fft.ifft2(np.fft.ifftshift(filter_fft(a,lo,refinement['high']))).real;m=float(abs(inv).max());photo_view(axes[row,2*col+1],a,inv,cmap='RdBu_r',vmin=-m,vmax=m);axes[row,2*col+1].set_title(f'Whole-band inverse ±{m:.3f}')
            if col==0:card(q,a,r,ch,BUNDLE/f'D3-s20-{ch}-alternative.png')
    fig.suptitle('D3 σ20: maker says KEEP THE SIDE LOBES\nLeft: current provisional lower cutoff. Right: superseded whole-bright-feature removal.\nExact numeric cutoffs remain Codex choices; the selection procedure is not frozen.');fig.savefig(BUNDLE/'central-ambiguity.png',dpi=130);plt.close(fig);save(BUNDLE/'refinement-results.json',rs)


def shortlist():
    """Maker update: brightest 3–4 noncentral pairs without upper rejection."""
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image']);old=read(BUNDLE/'measurements.json');results=[];comparisons=[]
    def canonical(p):
        k=tuple(p['offset']);return min(k,tuple(-x for x in k))
    for q in cfg['development']:
        fig,axes=plt.subplots(2,4,figsize=(16,9),layout='constrained')
        for col,sigma in enumerate(WIDTHS):
            for row,ch in enumerate(('V','Y')):
                a=products(rgb,q,sigma,ch);prior=next(r for r in old if (r['window'],r['sigma'],r['channel'])==(q['id'],sigma,ch))
                r=extract(a,prior['low'],np.sqrt(.5),q['tangent_deg']);c=a['n']//2
                for p in r['peaks']:
                    dx,dy=p['offset'];p['peak_bin_power']=float(abs(a['f'][c-dy,c+dx])**2)
                r['peaks'].sort(key=lambda p:p['peak_bin_power'],reverse=True)
                for i,p in enumerate(r['peaks']):p['candidate']=i+1
                r['reciprocal_alternatives']=reciprocal_alternatives(r['peaks'],a['n'],r['frequency_resolution'],q['tangent_deg'])
                results.append(dict(window=q['id'],sigma=sigma,channel=ch,n=a['n'],s=q['s'],physical_assignment='unassigned',**r))
                first=r['peaks'][:4];was=prior['peaks'][:4];same3={canonical(p) for p in first[:3]}=={canonical(p) for p in was[:3]};same4={canonical(p) for p in first}=={canonical(p) for p in was}
                filename=f'{q["id"]}-s{sigma}-{ch}.png';mapping={p['candidate']:next((x['candidate'] for x in prior['peaks'] if canonical(p)==canonical(x)),None) for p in first}
                if any(v is None for v in mapping.values()):
                    filename=f'{q["id"]}-s{sigma}-{ch}-no-upper.png';card(q,a,dict(r,peaks=first),ch,BUNDLE/filename);mapping={p['candidate']:p['candidate'] for p in first}
                comparisons.append(dict(window=q['id'],sigma=sigma,channel=ch,band_count=len(prior['peaks']),no_upper_count=len(r['peaks']),same_top3=same3,same_top4=same4,shortlist_count=len(first),inverse_card=filename,inverse_candidate_mapping=mapping))
                spectrum(axes[row,col],a,r['low'],np.sqrt(.5),lim=.12,marks=first);axes[row,col].set_title(f"{ch} σ{sigma}, lower {r['low']:.3f}, no upper\nBrightest {len(first)}; top3 {'same' if same3 else 'DIFFER'} from annulus")
        fig.suptitle(q['id']+' — maker update: brightest 3 pairs plus fourth alternative; central exclusion only\nNo outer coefficients removed. Same fixed display scale; first4 are candidates, not four physical directions.');fig.savefig(BUNDLE/f'{q["id"]}-no-upper.png',dpi=130);plt.close(fig)
    save(BUNDLE/'no-upper-measurements.json',results);save(BUNDLE/'no-upper-comparison.json',comparisons)
    print('No upper: same top3',sum(r['same_top3'] for r in comparisons),'same top4',sum(r['same_top4'] for r in comparisons),'of',len(comparisons),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['main','focus','shortlist'],nargs='?',default='main');args=p.parse_args();globals()[args.stage]()
