"""R250 plots: measured points/accepted links, explicit gaps and model overlays."""
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from photo2.fft_dense import *
from photo2.fft_spectrum_led import spectrum,filter_fft,inverse_pairs
from photo2.fft_spectrum_led_evidence import photo_view

COLORS=['#277da8','#e76f51','#6a994e','#8b5fbf']


def main():
    data=load_measurements(2000);records=data['records'];length=data['length'];summary=read(BUNDLE/'summary.json');tracks=read(BUNDLE/'tracks.json');fits=read(BUNDLE/'angle-fits.json');cfg=verify_freeze();rgb=image_rgb(ROOT/cfg['image']);scanner=Scanner(rgb)
    obs={p['observation']:dict(p,s=r['s'],index=r['index']) for r in records for p in r['peaks']}
    # Full photograph, all sampled locations, and geometry context.
    sites=records[::2];fig,ax=plt.subplots(figsize=(9,11),layout='constrained');ax.imshow(rgb);sc=ax.scatter([r['x'] for r in sites],[r['y'] for r in sites],c=[r['s'] for r in sites],s=2,cmap='turbo');fig.colorbar(sc,ax=ax,label='Arc distance, native pixels');ax.set_title('2,000 equal-arc centers; spacing 4.62 native pixels\nColors show traversal, not inferred bead identity; sigma 30 everywhere');ax.plot(sites[0]['x'],sites[0]['y'],'wo',ms=9,mec='k');ax.text(sites[0]['x']+20,sites[0]['y'],'s = 0 / seam',color='white',bbox=dict(facecolor='black',alpha=.6));fig.savefig(BUNDLE/'centerline.png',dpi=140);plt.close(fig)
    for ch in ('V','Y'):
        rs=[r for r in records if r['channel']==ch];t=tracks[ch];top=[a['track'] for a in summary[ch]['top_tracks']];color={name:plt.get_cmap('tab20')(i) for i,name in enumerate(top)}
        fig,axes=plt.subplots(5,1,figsize=(18,15),sharex=True,layout='constrained');keys=['relative_angle','frequency','band_fraction']
        for ax,key in zip(axes,keys):
            gray=[];colored={name:[] for name in top}
            for e in t['associations']:
                if not e['accepted'] or e['wrap']:continue
                a,b=obs[e['source']],obs[e['target']]
                if key=='relative_angle' and abs(a[key]-b[key])>90:continue
                seg=[(a['s'],a[key]),(b['s'],b[key])];name=t['assignment'][e['source']]
                if name in color:colored[name].append(seg)
                else:gray.append(seg)
            ax.add_collection(LineCollection(gray,colors='.65',linewidths=.35,alpha=.25))
            for name,segs in colored.items():ax.add_collection(LineCollection(segs,colors=[color[name]],linewidths=1.2,label=name))
            # Isolated primary observations remain visible even without a link.
            pp=[p for r in rs for p in r['peaks'][:4]];ss=[r['s'] for r in rs for p in r['peaks'][:4]]
            ax.scatter(ss,[p[key] for p in pp],s=.6,c='.3',alpha=.15)
            ax.grid(alpha=.2)
        axes[0].set_ylim(-90,90);axes[0].set_ylabel('Reciprocal angle − tangent (°)');axes[0].legend(ncol=6,fontsize=8,loc='upper right')
        axes[1].set_ylim(0,.13);axes[1].set_ylabel('Frequency (cycles/native pixel)')
        axes[2].set_yscale('log');axes[2].set_ylim(.0001,1);axes[2].set_ylabel('Pair power / filtered total')
        for i,name in enumerate(top):
            ps=[obs[o] for g in t['tracks'] if g['track']==name for o in g['observations']]
            axes[3].scatter([p['s'] for p in ps],np.full(len(ps),i),c=[color[name]],s=3)
        axes[3].set_yticks(range(len(top)),top,fontsize=8);axes[3].set_ylabel('Persistent fragments\nblank = no assigned observation')
        axes[4].plot([r['s'] for r in rs],[r['curvature'] for r in rs],c='k',lw=.8);axes[4].set_ylabel('Signed curvature (1/pixel)');axes[4].set_xlabel('Arc length along closed centerline (native pixels)');axes[4].grid(alpha=.2);axes[4].set_xlim(0,length)
        fig.suptitle(ch+': measured axial peak tracks; colored = 12 longest prevalent fragments, gray = all others\nLinks connect measured neighbors only. No gap interpolation; same IDs may cross s=0. Track identity does not prove physical family.');fig.savefig(BUNDLE/f'{ch}-tracks.png',dpi=140);plt.close(fig)
    # Angle concentrations and the four requested constant least-squares fits.
    fig,axes=plt.subplots(2,1,figsize=(14,9),sharex=True,layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        hh=np.array(fits['histogram'][ch]);xx=np.array(fits['histogram']['centers']);ax.bar(xx,hh,width=1,color='.8',label='Qualified primary candidates')
        for b,f,c in zip(fits['ranges'],fits['channels'][ch],COLORS):
            sel=(xx>=b['low'])&(xx<b['high']);ax.bar(xx[sel],hh[sel],width=1,color=c,alpha=.7)
            mu=f['constant_angle'];ax.axvline(mu,color=c,lw=2,label=f"{mu:+.1f}°; RMS {f['rms_residual']:.1f}°")
        ax.set_ylabel(ch+' weighted observations');ax.legend(ncol=3,fontsize=9);ax.grid(alpha=.2)
    axes[-1].set_xlabel('Reciprocal angle relative to centerline tangent (degrees, axial modulo 180)');axes[-1].set_xlim(-90,90)
    fig.suptitle('Four prevalent angle ranges; least-squares constants fitted to unsmoothed observations\nEach window has equal total weight. Gray tails/minor modes remain unassigned; these are spectral categories, not four bead directions.');fig.savefig(BUNDLE/'angle-distribution.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(4,2,figsize=(17,13),sharex=True,layout='constrained');frequencyfig,faxes=plt.subplots(4,2,figsize=(17,12),sharex=True,layout='constrained')
    with (BUNDLE/'angle-range-observations.csv').open() as f:arows=list(csv.DictReader(f))
    grid=np.linspace(0,length,400)
    for j,ch in enumerate(('V','Y')):
        for k,b in enumerate(fits['ranges']):
            f=fits['channels'][ch][k];ps=[p for p in arows if p['channel']==ch and int(p['range'])==k+1];ss=[float(p['s']) for p in ps];aa=[float(p['angle']) for p in ps];ff=[float(p['frequency']) for p in ps];ax=axes[k,j]
            ax.scatter(ss,aa,s=3,color=COLORS[k],alpha=.45);ax.axhline(f['constant_angle'],color='k',lw=1.2,label='Constant LS fit')
            beta=f['harmonic_coefficients'];ax.plot(grid,beta[0]+beta[1]*np.sin(2*np.pi*grid/length)+beta[2]*np.cos(2*np.pi*grid/length),'--',c='k',lw=.8,label='Periodic LS alternative')
            ax.set_ylim(b['low'],b['high']);ax.set_title(f"{ch}: {f['constant_angle']:+.2f}° ± {f['rms_residual']:.2f}° RMS; coverage {100*f['window_coverage']:.1f}%",fontsize=10);ax.set_ylabel(f"Range {k+1}: angle (°)");ax.grid(alpha=.2)
            fax=faxes[k,j];fax.scatter(ss,ff,s=3,color=COLORS[k],alpha=.5);fax.set_ylim(.01,.10);fax.set_ylabel('Frequency (cycles/pixel)');fax.set_title(f'{ch}: angle range {b["low"]:+.1f}..{b["high"]:+.1f}°');fax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8);fig.suptitle('Observed angles and fitted constants in the four prevalent ranges\nDots are measurements; lines are explicitly fitted models. RMS includes real variation, bin quantization, appearance and assignment uncertainty.')
    frequencyfig.suptitle('Frequencies within the same four angular categories\nSimilar angle does not establish identical periodic structure; the −19° range contains multiple frequency bands.')
    for ax in list(axes[-1])+list(faxes[-1]):ax.set_xlabel('Centerline arc distance (native pixels)');ax.set_xlim(0,length)
    fig.savefig(BUNDLE/'four-angle-fits.png',dpi=140);plt.close(fig);frequencyfig.savefig(BUNDLE/'four-range-frequencies.png',dpi=140);plt.close(frequencyfig)
    # Event density and reciprocal support, aligned with curvature/appearance.
    fig,axes=plt.subplots(5,1,figsize=(17,12),sharex=True,layout='constrained');bins=np.arange(0,length+60,60)
    for ch,c in [('V','#e76f51'),('Y','#277da8')]:
        rs=[r for r in records if r['channel']==ch];t=tracks[ch];inc={e['target'] for e in t['associations'] if e['accepted']};out={e['source'] for e in t['associations'] if e['accepted']}
        ss=[r['s'] for r in rs for p in r['peaks'][:4] if p['observation'] not in inc or p['observation'] not in out]
        counts,_=np.histogram(ss,bins);axes[0].stairs(counts,bins,label=ch,color=c)
        supported=np.array([any(x['supported'] for x in r['trios']) for r in rs]);axes[1].scatter([r['s'] for r in rs],supported.astype(float)+(0 if ch=='V' else 1.2),s=2,color=c,label=ch)
        gap=[e for e in t['associations'] if e['kind']=='tentative_gap'];axes[2].scatter([obs[e['source']]['s'] for e in gap],[e['arc_gap'] for e in gap],s=8,marker='x',c=c,label=ch)
    axes[0].set_ylabel('Top-four fragment endpoints\nper 60px bin');axes[0].legend();axes[1].set_yticks([0,1,1.2,2.2],['V no','V yes','Y no','Y yes']);axes[1].set_ylabel('Supported reciprocal trio');axes[2].set_ylabel('Tentative reappearance\narc gap (pixels)');axes[2].legend()
    for key,c in [('red_proxy','red'),('yellow_proxy','#b59a00'),('dark_proxy','black'),('highlight_proxy','blue')]:axes[3].plot([r['s'] for r in sites],[r[key] for r in sites],label=key,color=c,lw=.8)
    axes[3].legend(ncol=4,fontsize=9);axes[3].set_ylabel('Weighted appearance fraction\nproxies, not bead inventories');axes[4].plot([r['s'] for r in sites],np.abs([r['curvature'] for r in sites]),c='k',lw=.8);axes[4].set_ylabel('|Curvature| (1/pixel)');axes[4].set_xlabel('Arc length (native pixels)')
    for ax in axes:ax.set_xlim(0,length);ax.grid(alpha=.2)
    fig.suptitle('Where association/reciprocal support fails and similar peaks reappear\nTentative gap proposals are not accepted identities. Appearance proxies include background and illumination; no causal attribution.')
    fig.savefig(BUNDLE/'events-context.png',dpi=140);plt.close(fig)
    # Traceable transition choices, chosen AFTER measurement for explanation only.
    choices=[]
    v=tracks['V'];y=tracks['Y']
    # Large changing angle within a persistent accepted branch, and Y frequency migration.
    choices.extend([dict(index=next(g for g in v['tracks'] if g['track']=='V0012')['observations'][len(next(g for g in v['tracks'] if g['track']=='V0012')['observations'])//2].split(':')[1],reason='V0012: accepted branch traverses substantially different angles'),dict(index=1650,reason='Y0002: inspect frequency/angle migration near the branch start')])
    # Strongest rank inversion preserved by the graph.
    ee=[e for e in y['associations'] if e['accepted'] and obs[e['source']]['candidate']==1 and obs[e['target']]['candidate']>=3]
    if ee:
        e=max(ee,key=lambda e:obs[e['target']]['candidate']);i=obs[e['source']]['index'];choices.append(dict(index=i,indices=[(i-1)%2000,i,obs[e['target']]['index']],reason='Y brightness rank changes while angle/frequency association persists',association=e))
    if v['ambiguous']:choices.append(dict(index=obs[v['ambiguous'][0]]['index'],reason='V competing adjacent association: identity left unresolved'))
    gg=[e for e in y['associations'] if e.get('unique_gap') and obs[e['source']]['candidate']<=4 and obs[e['target']]['candidate']<=4]
    if gg:
        e=min(gg,key=lambda e:e['cost']);choices.append(dict(index=obs[e['source']]['index'],reason='Y tentative reappearance after a measured gap',gap=e,indices=[obs[e['source']]['index'],(obs[e['source']]['index']+obs[e['target']]['index'])//2,obs[e['target']]['index']]))
    worst=max(sites,key=lambda r:abs(r['curvature']));choices.append(dict(index=worst['index'],reason='Largest absolute centerline curvature'))
    for ci,q in enumerate(choices):
        i=int(q['index']);q['index']=i;q['s']=sites[i]['s'];fig,axes=plt.subplots(3,6,figsize=(20,11),layout='constrained')
        for row,j in enumerate(q.get('indices',[(i-5)%2000,i,(i+5)%2000])):
            rr={r['channel']:r for r in records[2*j:2*j+2]};aa=scanner.products(sites[j]);a=aa['V'];photo_view(axes[row,0],a,a['patch']);axes[row,0].set_title(f"s={sites[j]['s']:.1f}, index{j}\nRaw ±60 pixels")
            photo_view(axes[row,1],a,a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title('V × circular Gaussian')
            for col,ch in [(2,'V'),(3,'Y')]:spectrum(axes[row,col],aa[ch],LOW,np.sqrt(.5),lim=.1,marks=rr[ch]['peaks'][:4]);axes[row,col].set_title(ch+' FFT; labels = brightness rank')
            for col,ch in [(4,'V'),(5,'Y')]:
                # Combined shortlisted coefficients; no inference of unmeasured bead positions.
                r=rr[ch];a=aa[ch];inv=inverse_pairs(filter_fft(a,LOW,np.sqrt(.5)),r['peaks'][:4],lobes=True,resolution=1.25*SIZE*DELTA);m=max(float(abs(inv).max()),1e-12);photo_view(axes[row,col],a,inv,cmap='RdBu_r',vmin=-m,vmax=m);axes[row,col].set_title(ch+' top-four inverse\nindependent signed contrast')
        fig.suptitle(f"Example {ci+1}: {q['reason']}\nActual measured centers (arc distances shown); no location or filter retuning. Rank labels are not track IDs.")
        fig.savefig(BUNDLE/f'transition-{ci+1}.png',dpi=120);plt.close(fig)
    save(BUNDLE/'examples.json',choices)
    print('Saved full-loop, track, four-range fit, event and transition figures',flush=True)


if __name__=='__main__':main()
