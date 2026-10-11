"""R243 reports; consumes frozen experiment outputs without retuning extraction."""
from collections import defaultdict
import csv,json
import numpy as np
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-fft-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image,ExifTags
from photo2.fft_helicity import *


def best_at(r,hand,cam):
    return min((f for f in r['fits'] if f['hand']==hand and (f['elevation'],f['roll'])==tuple(cam)),key=lambda f:f['score'])

def direct_alternatives(rec,fit):
    """Invert observed reciprocal basis; retain +/- sign branches and closure error.

    Conditional family assignments, not new bead observations. The third pair
    checks b1-b2 coherence; opposite pair signs cannot be recovered from magnitudes.
    """
    match={m['family']:next(p for p in rec['peaks'] if p['candidate']==m['candidate']) for m in fit['matches'] if m['residual']<2}
    if not {1,6}.issubset(match):return []
    k6=np.array(match[6]['offset'],float)/rec['n']; k1=np.array(match[1]['offset'],float)/rec['n'];out=[]
    for sign in (-1,1):
        b=np.column_stack((k6,sign*k1))
        if abs(np.linalg.det(b))<1e-8:continue
        a=np.linalg.inv(b).T;vs=[a[:,0],a[:,1],a[:,0]+a[:,1]]
        angles=[float(wrap(np.degrees(np.arctan2(v[1],v[0]))-rec['tangent_deg'])) for v in vs]
        closure=None
        if 7 in match:
            k7=np.array(match[7]['offset'])/rec['n'];pred=k6-sign*k1
            closure=float(min(np.linalg.norm(pred-k7),np.linalg.norm(pred+k7))*rec['diameter'])
        out.append(dict(sign_branch=sign,angles=dict(zip(['1','6','7'],angles)),third_pair_closure_fd=closure))
    return out


def main():
    rows=read(OUT/'all-windows.json');trackdata=read(OUT/'tracking.json');cfg=read(BUNDLE/'sampling.json');controls=read(BUNDLE/'controls-results.json')
    prim=[r for r in rows if r['variant_name']=='primary'];camera_choices={};camera_scores={}
    cameras=[(el,az) for el in (45,65,85) for az in (0,45,90,135)]
    for ch in ('V','Y'):
      dev=[r for r in prim if r['channel']==ch and r['split']=='development']
      for hand in (-1,1):
        scores=[dict(camera=cam,score=float(np.mean([best_at(r,hand,cam)['score'] for r in dev]))) for cam in cameras]
        choice=min(scores,key=lambda x:x['score'])['camera'];camera_choices[f'{ch}/{hand}']=choice;camera_scores[f'{ch}/{hand}']=scores
    summary=[];assignments=[]
    for r in prim:
        ch=r['channel'];fits={h:best_at(r,h,camera_choices[f'{ch}/{h}']) for h in (-1,1)}
        delta=fits[-1]['score']-fits[1]['score']
        variants=[x for x in rows if x['window']==r['window'] and x['channel']==ch]
        gaps=[best_at(x,-1,camera_choices[f'{ch}/-1'])['score']-best_at(x,1,camera_choices[f'{ch}/1'])['score'] for x in variants]
        stable=[]
        for p in r['peaks']:
            found=0
            for x in variants[1:]:
                if any(abs(float(wrap(pp['relative_angle']-p['relative_angle'])))<=max(10,p['angle_uncertainty']*2) and abs(pp['fd']-p['fd'])<.2 for pp in x['peaks']):found+=1
            stable.append(dict(candidate=p['candidate'],fraction=found/max(1,len(variants)-1)))
        modelgap=[best_at(r,-1,cam)['score']-best_at(r,1,cam)['score'] for cam in cameras]
        s=dict(window=r['window'],channel=ch,split=r['split'],s=r['s'],candidate_count=len(r['peaks']),
            fits={str(h):fits[h] for h in (-1,1)},gap=float(delta),sensitivity_gap_range=[float(min(gaps)),float(max(gaps))],
            shared_camera_gap_range=[float(min(modelgap)),float(max(modelgap))],stable_peak_count=sum(x['fraction']>=.75 for x in stable),peak_stability=stable,
            all_three_under_both_hands=all(f['resolved']==3 for f in fits.values()),
            support='h+1' if min(gaps)>.5 else ('h-1' if max(gaps)<-.5 else 'ambiguous'))
        summary.append(s)
        assignments.append(dict(window=r['window'],channel=ch,
            hypotheses={str(h):dict(fit=fits[h],direct_angle_alternatives=direct_alternatives(r,fits[h])) for h in (-1,1)}))
    control_summary=[]
    for appearance in ('uniform','mixed'):
      for perspective in (False,True):
       for ch in ('V','Y'):
        rs=[r for r in controls if r['appearance']==appearance and r['perspective']==perspective and r['channel']==ch]
        gaps=np.array([r['fits'][0]['score']-r['fits'][1]['score'] for r in rs]);truth=np.array([r['truth'] for r in rs]);conf=abs(gaps)>.5
        control_summary.append(dict(appearance=appearance,perspective=perspective,channel=ch,count=len(rs),correct=int(np.sum(gaps*truth>0)),confident_count=int(conf.sum()),confident_wrong=int(np.sum((gaps*truth<0)&conf)),median_absolute_gap=float(np.median(abs(gaps)))))
    # Shared global-camera alternatives for whole reserved-set support; no local tilt fitting.
    aggregate={}
    for ch in ('V','Y'):
        rs=[r for r in prim if r['channel']==ch and r['split']=='reserved']
        gaps=[float(np.mean([best_at(r,-1,cam)['score']-best_at(r,1,cam)['score'] for r in rs])) for cam in cameras]
        ss=[s for s in summary if s['channel']==ch and s['split']=='reserved']
        aggregate[ch]=dict(reserved_primary_plus=sum(s['gap']>0 for s in ss),reserved_primary_minus=sum(s['gap']<0 for s in ss),
            robust_plus=sum(s['support']=='h+1' for s in ss),robust_minus=sum(s['support']=='h-1' for s in ss),
            shared_camera_mean_gaps=[dict(camera=cam,gap=g) for cam,g in zip(cameras,gaps)])
    tracking_summary={}
    for ch in ('V','Y'):
        rs=[r for r in trackdata['windows'] if r['channel']==ch];peaks=[p for r in rs for p in r['peaks']];lens=defaultdict(int)
        for p in peaks:lens[p['track']]+=1
        tracking_summary[ch]=dict(windows=len(rs),failed=sum('failure' in r for r in rs),candidates=len(peaks),tracks=len(lens),
            tracks_length_at_least5=sum(n>=5 for n in lens.values()),ambiguous_links=sum(p['track_ambiguous'] for p in peaks),
            median_track_length=float(np.median(list(lens.values()))),max_track_length=max(lens.values()))
    result=dict(verdict='Inconclusive: no unique photographic helicity established',parameters=PARAMS,camera_choices_from_development=camera_choices,
        camera_scores_from_development=camera_scores,windows=summary,reserved=aggregate,controls=control_summary,tracking=tracking_summary,
        gate='Fail: known-camera controls include wrong strong preferences; photograph support is sensitive to candidate/projection alternatives.',
        claims='No bead centers, full indices, camera calibration, recovered sequence or general automatic reconstruction.')
    save(BUNDLE/'summary.json',result);save(BUNDLE/'assignments.json',assignments)
    # Full candidate table includes every primary dense/review candidate and every sensitivity candidate.
    allrows=rows+trackdata['windows'];columns=['window','channel','split','variant','s','candidate','frequency','radius_bins','fd','angle','relative_angle','angle_uncertainty','frequency_uncertainty','pair_power','band_fraction','prominence','breadth_bins','track','assignment_minus','assignment_plus','failure']
    with (BUNDLE/'peaks.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n");writer.writeheader()
        for r in allrows:
            for p in r['peaks'] or [{}]:
                base={k:p.get(k,'') for k in columns};base.update({k:r.get(k,'') for k in ('window','channel','split','s','failure')});base['variant']=r.get('variant_name','primary')
                for h,label in [(-1,'assignment_minus'),(1,'assignment_plus')]:
                    base[label]='unassigned'
                    if r.get('fits') and p:
                        fit=best_at(r,h,camera_choices[f"{r['channel']}/{h}"])
                        hits=[str(m['family']) for m in fit['matches'] if m['candidate']==p['candidate'] and m['residual']<2]
                        if hits:base[label]='conditional '+','.join(hits)
                writer.writerow(base)
    # Raw reciprocal measurements, no track smoothing: user can see fragmentation.
    fig,axes=plt.subplots(2,1,figsize=(15,9),sharex=True,layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        rs=[r for r in trackdata['windows'] if r['channel']==ch]
        for r in rs:
            for p in r['peaks']:
                ax.scatter(r['s'],p['relative_angle'],s=10+25*p['band_fraction'],c=[plt.cm.tab20((p['track']%20)/20)],alpha=.7)
            if 'failure' in r:ax.axvline(r['s'],c='red',alpha=.12)
        ax.set_ylim(-90,90);ax.set_ylabel(ch+' reciprocal angle − tangent (°)');ax.grid(alpha=.2)
        for q in cfg['sites']:ax.axvline(q['s'],c='gray',alpha=.25);ax.text(q['s'],82,q['id'])
    axes[-1].set_xlabel('Distance along approximate centerline (native image pixels)');fig.suptitle('Unsmoothed FFT pair directions; colors cycle through short-gap track IDs\nRed strips: full Gaussian crop leaves image. Overlapping windows are correlated.');fig.savefig(BUNDLE/'directions-tracking.png',dpi=150);plt.close(fig)
    # Direct inferred alternatives are explicitly conditional on family association.
    fig,axes=plt.subplots(2,1,figsize=(14,8),sharex=True,layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        for a in assignments:
            if a['channel']!=ch:continue
            s=next(q['s'] for q in cfg['sites'] if q['id']==a['window'])
            for h,mark in [('-1','x'),('1','o')]:
                for branch in a['hypotheses'][h]['direct_angle_alternatives']:
                    for fam,color in zip(['1','6','7'],['#3366cc','#ee8822','#339955']):
                        ax.scatter(s,branch['angles'][fam],c=color,marker=mark,alpha=.65)
        ax.set_ylim(-90,90);ax.set_ylabel(ch+' inferred direct angle (°)');ax.grid(alpha=.2)
    axes[-1].set_xlabel('Image arc length (px)');fig.suptitle('Conditional direct-lattice angles from observed reciprocal basis inversion\nBlue=1, orange=6, green=7; × h−1 assignment, ○ h+1; retain both pair-sign branches');fig.savefig(BUNDLE/'direct-angle-alternatives.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(14,5),sharey=True,layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        ss=[s for s in summary if s['channel']==ch];x=np.arange(8)
        for i,s in enumerate(ss):
            low,high=s['sensitivity_gap_range'];ax.plot([i,i],[low,high],c='#555555',lw=2)
            lo,hi=s['shared_camera_gap_range'];ax.plot([i+.16,i+.16],[lo,hi],c='#aaaaaa',lw=5,alpha=.6)
            ax.plot(i,s['gap'],'o',c='#2176ae')
        ax.axhline(0,c='black',lw=1);ax.axhspan(-.5,.5,color='orange',alpha=.12);ax.set_xticks(x,[s['window'] for s in ss]);ax.set_title(ch+'; positive favors h+1');ax.grid(alpha=.2)
    axes[0].set_ylabel('Score(h−1) − score(h+1), smaller model score is better');fig.suptitle('Blue: primary; dark range: fixed sensitivity variants; pale range: shared camera alternatives\n±0.5 shaded is a practical margin, not a calibrated probability');fig.savefig(BUNDLE/'helicity-support.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for ch,color in [('V','#cc4422'),('Y','#2266aa')]:
        ss=[s for s in summary if s['channel']==ch];axes[0].plot(range(8),[s['stable_peak_count'] for s in ss],'o-',label=ch,c=color)
        cc=[s for s in control_summary if s['channel']==ch];axes[1].plot(range(4),[s['correct']/s['count'] for s in cc],'o-',label=ch,c=color)
    axes[0].set_xticks(range(8),[q['id'] for q in cfg['sites']]);axes[0].set_ylim(0,6.5);axes[0].set_title('Photo candidates present in ≥75% of perturbations');axes[0].set_ylabel('Stable pairs (not validated families)')
    axes[1].set_xticks(range(4),['uniform/ortho','uniform/persp','mixed/ortho','mixed/persp'],rotation=15);axes[1].set_ylim(.5,1);axes[1].set_title('Known-camera control hand preference');axes[1].set_ylabel('Correct fraction; correlated windows')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.savefig(BUNDLE/'channel-comparison.png',dpi=150);plt.close(fig)
    # Every extracted pair gets a phase-preserving reconstruction; a model-selected
    # combination is labeled separately from strongest-three illustrative panels.
    rgb=image_rgb(ROOT/cfg['image'])
    for q in cfg['sites']:
        fig,axes=plt.subplots(2,8,figsize=(20,6),layout='constrained')
        for row,ch in enumerate(('V','Y')):
            rec,a=analyze(rgb,q,ch);rr=next(r for r in prim if r['window']==q['id'] and r['channel']==ch)
            axes[row,0].imshow(a['patch']);axes[row,0].set_title(ch+' raw')
            for k in range(6):
                if k<len(rec['peaks']):
                    p=rec['peaks'][k];inv=inverse_pairs(a['f'],[p]);amp=max(abs(inv).max(),1e-12)
                    axes[row,k+1].imshow(inv,cmap='gray',vmin=-amp,vmax=amp);axes[row,k+1].set_title(f"pair{k+1}: {p['relative_angle']:.1f}°\nf={p['frequency']:.4f}")
            fit=best_at(rr,1,camera_choices[f'{ch}/1']);ids=[m['candidate'] for m in fit['matches'] if m['residual']<2]
            picks=[p for p in rec['peaks'] if p['candidate'] in ids];inv=inverse_pairs(a['f'],picks,True,rec['resolution_bins']*1.25);amp=max(abs(inv).max(),1e-12)
            axes[row,7].imshow(inv,cmap='gray',vmin=-amp,vmax=amp);axes[row,7].set_title('h+1 selected lobes\nconditional '+','.join(map(str,ids)))
            for ax in axes[row]:ax.axis('off')
        fig.suptitle(q['id']+' individual-pair contributions; relative reciprocal angles; full coefficients retain phase');fig.savefig(BUNDLE/(q['id']+'-pairs.png'),dpi=120);plt.close(fig)
    # Curated EXIF subset; do not serialize opaque maker-note bytes.
    exif=Image.open(ROOT/cfg['image']).getexif();tags={**dict(exif),**exif.get_ifd(34665)}
    wanted={'LensMake','LensModel','FocalLength','FocalLengthIn35mmFilm','DigitalZoomRatio','ExifImageWidth','ExifImageHeight','Orientation','ExposureTime','FNumber','ISOSpeedRatings','CompositeImage'}
    save(BUNDLE/'exif.json',{ExifTags.TAGS.get(k,str(k)):str(v) for k,v in tags.items() if ExifTags.TAGS.get(k,str(k)) in wanted})
    print(json.dumps(dict(reserved=aggregate,tracking=tracking_summary,controls=control_summary),indent=2))

def supplementary():
    rows=read(OUT/'all-windows.json');cfg=read(BUNDLE/'sampling.json');summary=read(BUNDLE/'summary.json')
    cameras=summary['camera_choices_from_development'];controls=read(BUNDLE/'controls-results.json');manifest=read(BUNDLE/'controls-manifest.json')
    # V/Y exemplars chosen on known-hand controls, with explicit selection rule.
    pairs=defaultdict(dict)
    for r in controls:pairs[r['window']][r['channel']]=r
    candidates=[]
    for key,rs in pairs.items():
        if set(rs)!={'V','Y'} or rs['V']['appearance']!='mixed':continue
        margins={ch:(r['fits'][0]['score']-r['fits'][1]['score'])*r['truth'] for ch,r in rs.items()}
        candidates.append((margins['V']-margins['Y'],key,margins))
    examples=[]
    for label,item in [('V-advantage',max(candidates)),('Y-advantage',min(candidates))]:
        difference,key,margins=item;r=pairs[key]['V'];case=next(c for c in manifest if c['id']==r['case']);q=next(q for q in case['sites'] if q['id']==key)
        rgb=image_rgb(ROOT/case['image']);result=[analyze(rgb,q,ch) for ch in ('V','Y')]
        card(q,result,BUNDLE/f'control-{label}.png');examples.append(dict(label=label,window=key,truth=r['truth'],true_hand_margins=margins,selection='largest difference of correct-hand signed margins among mixed-color controls; illustrative extremes, not independent validation'))
    save(BUNDLE/'channel-examples.json',examples)
    # Fixed-variant sensitivity table and heat map (no retuning).
    names=[name for name,_ in variants()];grid=[];labels=[]
    for ch in ('V','Y'):
      for q in cfg['sites']:
        vals=[]
        for name in names:
            r=next(r for r in rows if r['channel']==ch and r['window']==q['id'] and r['variant_name']==name)
            vals.append(best_at(r,-1,cameras[f'{ch}/-1'])['score']-best_at(r,1,cameras[f'{ch}/1'])['score'])
        grid.append(vals);labels.append(q['id']+'/'+ch)
    fig,ax=plt.subplots(figsize=(15,8),layout='constrained');lim=max(abs(np.array(grid)).max(),.5)
    im=ax.imshow(grid,cmap='coolwarm',vmin=-lim,vmax=lim,aspect='auto');ax.set_yticks(range(16),labels);ax.set_xticks(range(len(names)),names,rotation=45,ha='right')
    fig.colorbar(im,ax=ax,label='score(h−1) − score(h+1)');ax.set_title('Identical predeclared perturbations; red favors h+1, blue h−1\nDevelopment-selected camera for each hand/channel; no parameter sweep selection');fig.savefig(BUNDLE/'sensitivity.png',dpi=150);plt.close(fig)
    with (BUNDLE/'sensitivity.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['window/channel']+names);w.writerows([[lab]+vals for lab,vals in zip(labels,grid)])
    td=read(OUT/'tracking.json')
    with (BUNDLE/'tracks.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['channel','window','candidate','track','previous','gap','alternative_links'])
        for ch,links in td['links'].items():
            for x in links:w.writerow([ch]+[x[k] for k in ['window','candidate','track','previous','gap']]+[json.dumps(x['alternatives'])])
    # Measured scale probes shown with endpoints and local context.
    rgb=image_rgb(ROOT/cfg['image']);fig,axes=plt.subplots(2,4,figsize=(16,9),layout='constrained')
    for ax,q in zip(axes.flat,cfg['sites']):
        x,y=q['xy'];r=q['radius'];ax.imshow(rgb);ax.set_xlim(x-1.5*r,x+1.5*r);ax.set_ylim(y+1.5*r,y-1.5*r)
        a=np.array(q['diameter_probe']);b=np.array(q['boundary_guide_endpoints']);ax.plot(*a.T,'y.-',lw=2);ax.plot(*b.T,'c.-',lw=1)
        ax.set_title(f"{q['id']} d≈{q['diameter']:.0f}px (yellow); R≈{r:.0f}px (cyan)\nBroad scale guides; d uncertainty20%",fontsize=10)
    fig.suptitle('Raw scale estimates, set before FFTs; cyan boundary guides can include shadow bias\nYellow lines are approximate diameter rulers near beads, not bead-boundary measurements');fig.savefig(BUNDLE/'scale-evidence.png',dpi=150);plt.close(fig)
    # Source/crop curvature is an additional reported limitation, not fitted away.
    curvature=[]
    for q in cfg['sites']:
        near=min((r for r in td['windows'] if r['channel']=='V'),key=lambda r:abs(r['s']-q['s']))
        curvature.append(dict(window=q['id'],nearest_tracking_window=near['window'],tangent_range_within_sigma_deg=near['tangent_variation_sigma_deg']))
    save(BUNDLE/'curvature.json',curvature)

if __name__=='__main__':
    main()
    supplementary()
