"""R244 paired summaries. Fixed R243 camera choices; no new camera fitting."""
import csv,json
from collections import defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment
from photo2.fft_curvature import *
from photo2.fft_helicity_report import direct_alternatives

def stable_pairs(primary,variants):
    hits=defaultdict(int);ambiguous=0
    for r in variants:
        a=primary['peaks'];b=r['peaks'];cost=np.full((len(a),len(b)+len(a)),3.)
        for i,p in enumerate(a):
            for j,q in enumerate(b):
                da=abs(float(base.wrap(p['relative_angle']-q['relative_angle'])));df=abs(p['fd']-q['fd'])
                if da<=10 and df<=.2:cost[i,j]=np.hypot(da/10,df/.2)
            ambiguous+=int(np.sum(cost[i,:len(b)]<3)>1)
        ii,jj=linear_sum_assignment(cost)
        for i,j in zip(ii,jj):
            if j<len(b) and cost[i,j]<3:hits[a[i]['candidate']]+=1
    return [dict(candidate=p['candidate'],fraction=hits[p['candidate']]/max(len(variants),1)) for p in primary['peaks']],ambiguous

def main():
    cfg=read(BUNDLE/'protocol.json');rows=read(OUT/'photo-measurements.json');controls=read(OUT/'controls.json')
    cams=read(base.BUNDLE/'summary.json')['camera_choices_from_development'];prim=[r for r in rows if r['variant']=='primary'];summary=[];assign=[]
    for r in prim:
        variants=[x for x in rows if (x['window'],x['arm'],x['channel'])==(r['window'],r['arm'],r['channel'])]
        good=[x for x in variants if not x.get('failure')]
        if r.get('failure'):summary.append({k:r[k] for k in ('window','arm','channel','group','failure')});continue
        ch=r['channel'];fits={h:best_at(r,h,cams[f'{ch}/{h}']) for h in (-1,1)}
        gap=fits[-1]['score']-fits[1]['score']
        gaps=[best_at(x,-1,cams[f'{ch}/-1'])['score']-best_at(x,1,cams[f'{ch}/1'])['score'] for x in good]
        camera_gaps=[best_at(r,-1,(el,roll))['score']-best_at(r,1,(el,roll))['score'] for el in (45,65,85) for roll in (0,45,90,135)]
        stable,amb=stable_pairs(r,[x for x in variants if x['variant']!='primary'])
        support='ambiguous'
        if len(good)==len(variants):
            if min(gaps)>.5:support='h+1'
            elif max(gaps)<-.5:support='h-1'
        summary.append(dict(window=r['window'],arm=r['arm'],channel=ch,group=r['group'],s=r['s'],gap=gap,
                            sensitivity_gap_range=[min(gaps),max(gaps)],shared_camera_gap_range=[min(camera_gaps),max(camera_gaps)],
                            candidate_count=len(r['peaks']),stable_peak_count=sum(p['fraction']>=.75 for p in stable),peak_stability=stable,
                            ambiguous_stability_links=amb,failed_variants=len(variants)-len(good),support=support,fits={str(h):fits[h] for h in (-1,1)},geometry=r['geometry']))
        # New offsets are already in the tangent grid, so subtract zero here.
        local=dict(r,tangent_deg=0.)
        assign.append(dict(window=r['window'],arm=r['arm'],channel=ch,hypotheses={str(h):dict(fit=fits[h],direct_angle_alternatives=direct_alternatives(local,fits[h])) for h in (-1,1)}))
    photo_groups=[]
    for group in ('straight','curved'):
      for arm in ARMS:
       for ch in ('V','Y'):
        rs=[s for s in summary if (s['group'],s['arm'],s['channel'])==(group,arm,ch) and not s.get('failure')]
        photo_groups.append(dict(group=group,arm=arm,channel=ch,n=len(rs),primary_plus=sum(s['gap']>0 for s in rs),robust_plus=sum(s['support']=='h+1' for s in rs),robust_minus=sum(s['support']=='h-1' for s in rs),median_stable_pairs=float(np.median([s['stable_peak_count'] for s in rs])),median_gap=float(np.median([s['gap'] for s in rs])),three_resolved_both=sum(all(f['resolved']==3 for f in s['fits'].values()) for s in rs)))
    control_groups=[];control_windows=[]
    for r in controls:
        gap=r['fits'][0]['score']-r['fits'][1]['score'];truefit=next(f for f in r['fits'] if f['hand']==r['truth'])
        control_windows.append(dict(window=r['window'],case=r['case'],arm=r['arm'],channel=r['channel'],appearance=r['appearance'],perspective=r['perspective'],truth=r['truth'],gap=gap,signed_margin=gap*r['truth'],correct=gap*r['truth']>0,wrong_strong=gap*r['truth']<-.5,true_model_score=truefit['score'],true_model_resolved=truefit['resolved']))
    for arm in ['native',*ARMS]:
     for appearance in ('uniform','mixed'):
      for perspective in (False,True):
       for ch in ('V','Y'):
        ss=[s for s in control_windows if (s['arm'],s['appearance'],s['perspective'],s['channel'])==(arm,appearance,perspective,ch)]
        control_groups.append(dict(arm=arm,appearance=appearance,perspective=perspective,channel=ch,n=len(ss),correct=sum(s['correct'] for s in ss),wrong_strong=sum(s['wrong_strong'] for s in ss),median_true_score=float(np.median([s['true_model_score'] for s in ss])),three_resolved_true=sum(s['true_model_resolved']==3 for s in ss)))
    result=dict(verdict='Diagnostic method comparison, not a unique photographic helicity determination',camera_choices_reused=cams,
                windows=summary,photo_groups=photo_groups,control_groups=control_groups,
                failed_records=[{k:r[k] for k in ('window','arm','channel','variant','failure')} for r in rows if r.get('failure')],
                stability_rule='One-to-one across eight perturbations; fixed <=10deg and <=0.2 f*d gates; >=75% repeatable. Ambiguity retained; not truth.',
                dependence='Same photo and controls as R243, neighboring pixels/channels/variants correlated. Straight versus curved groups have appearance/orientation confounds. No confidence intervals from pseudo-independent windows.')
    save(BUNDLE/'summary.json',result);save(BUNDLE/'assignments.json',assign);save(BUNDLE/'control-windows.json',control_windows)
    cols=['window','group','arm','channel','variant','s','candidate','frequency','radius_bins','fd','relative_angle','angle','angle_uncertainty','frequency_uncertainty','pair_power','band_fraction','prominence','assignment_minus','assignment_plus','failure']
    with (BUNDLE/'peaks.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader()
        for r in rows:
            fits={h:best_at(r,h,cams[f"{r['channel']}/{h}"]) for h in (-1,1)} if 'fits' in r else {}
            for p in r['peaks'] or [{}]:
                row={k:p.get(k,'') for k in cols};row.update({k:r.get(k,'') for k in ('window','group','arm','channel','variant','s','failure')})
                if p:row['radius_bins']=float(np.linalg.norm(p['offset']))
                for h,col in [(-1,'assignment_minus'),(1,'assignment_plus')]:row[col]=','.join(str(m['family']) for m in fits.get(h,{}).get('matches',[]) if m['candidate']==p.get('candidate') and m['residual']<2) or 'unassigned'
                w.writerow(row)
    plots(cfg,prim,result,assign)
    print(json.dumps(dict(photo_groups=photo_groups,control_groups=control_groups,failures=len(result['failed_records'])),indent=2))


def plots(cfg,prim,result,assign):
    ss=result['windows'];fig,axes=plt.subplots(3,2,figsize=(16,12),sharey=True,layout='constrained')
    for row,arm in enumerate(ARMS):
      for col,ch in enumerate(('V','Y')):
        ax=axes[row,col]
        for i,q in enumerate(cfg['sites']):
            s=next(s for s in ss if (s['window'],s['arm'],s['channel'])==(q['id'],arm,ch))
            if s.get('failure'):continue
            ax.plot([i,i],s['sensitivity_gap_range'],c='#444444',lw=2)
            ax.plot([i+.14,i+.14],s['shared_camera_gap_range'],c='#cccccc',lw=3)
            ax.plot(i,s['gap'],'o',c='#1776b6' if q['group']=='straight' else '#ce7500')
        ax.set_xticks(range(12),[q['id'] for q in cfg['sites']]);ax.axhline(0,c='black',lw=1);ax.axhspan(-.5,.5,alpha=.12,color='orange');ax.grid(alpha=.15);ax.set_title(arm+' '+ch)
    fig.suptitle('Hand support: positive favors source h+1; dots primary, dark range 8 perturbations, pale range shared-camera alternatives\nCamera choices reused from R243, not refit. ±0.5 is an uncalibrated practical margin; no probability interpretation.')
    fig.savefig(BUNDLE/'helicity-support.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(3,2,figsize=(16,11),sharex=True,sharey=True,layout='constrained')
    for row,arm in enumerate(ARMS):
      for col,ch in enumerate(('V','Y')):
        ax=axes[row,col]
        for r in prim:
            if (r['arm'],r['channel'])!=(arm,ch) or r.get('failure'):continue
            for p in r['peaks']:ax.scatter(r['s'],p['relative_angle'],s=12+100*p['band_fraction'],c=COLORS[p['candidate']-1],alpha=.7)
        for q in cfg['sites']:ax.text(q['s'],82,q['id'],ha='center',fontsize=7)
        ax.set_ylim(-90,90);ax.set_title(arm+' '+ch);ax.grid(alpha=.2);ax.set_ylabel('Reciprocal angle − tangent (°)')
    for ax in axes[-1]:ax.set_xlabel('Approximate centerline arc length (native px)')
    fig.suptitle('All qualified primary pairs; color is local strength rank, not a physical-family identity\nSparse separated sites: no tracking or interpolation across unsampled gaps.')
    fig.savefig(BUNDLE/'directions.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(3,2,figsize=(16,11),sharex=True,sharey=True,layout='constrained')
    for a in assign:
        ax=axes[list(ARMS).index(a['arm']),('V','Y').index(a['channel'])];s=next(q['s'] for q in cfg['sites'] if q['id']==a['window'])
        for h,marker in [('-1','x'),('1','o')]:
            for b in a['hypotheses'][h]['direct_angle_alternatives']:
                for fam,color in zip(['1','6','7'],['#3366cc','#ee8822','#339955']):ax.scatter(s,b['angles'][fam],marker=marker,c=color,alpha=.65)
    for row,arm in enumerate(ARMS):
      for col,ch in enumerate(('V','Y')):
        ax=axes[row,col];ax.set_ylim(-90,90);ax.set_title(arm+' '+ch);ax.grid(alpha=.2);ax.set_ylabel('Conditional direct angle (°)')
    for ax in axes[-1]:ax.set_xlabel('Approximate centerline arc length (native px)')
    fig.suptitle('Reciprocal-basis inversion: both sign branches and hand-conditioned assignments retained\nBlue=1, orange=6, green=7; × h−1, ○ h+1. Not verified bead directions; C angles in straightened coordinates.')
    fig.savefig(BUNDLE/'direct-angle-alternatives.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    groups=result['control_groups']
    for ax,ch in zip(axes,('V','Y')):
        for arm,color in zip(['native',*ARMS],['#888888','#2255aa','#cc6600','#228844']):
            rs=[r for r in groups if r['arm']==arm and r['channel']==ch]
            ax.plot(range(4),[r['correct']/r['n'] for r in rs],'o-',label=arm,c=color)
            for i,r in enumerate(rs):ax.text(i,r['correct']/r['n']+.008,str(r['wrong_strong']),c=color,fontsize=8)
        ax.set_xticks(range(4),['uniform ortho','uniform persp','mixed ortho','mixed persp'],rotation=12);ax.set_ylim(.35,1.09);ax.set_title(ch);ax.set_ylabel('Correct known-hand fraction');ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Known-camera e65 render controls: 16 correlated windows per category\nNumbers show wrong preferences exceeding 0.5; same images/sites across methods. Native is R243 adapter.')
    fig.savefig(BUNDLE/'controls-comparison.png',dpi=140);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(14,5),sharey=True,layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        for arm,color in zip(ARMS,['#2255aa','#cc6600','#228844']):
            vals=[s for s in ss if s['arm']==arm and s['channel']==ch and not s.get('failure')]
            ax.scatter([s['geometry']['turn_rms_deg'] for s in vals],[s['stable_peak_count'] for s in vals],label=arm,c=color)
        ax.set_xlabel('Turning RMS within this arm’s Gaussian (°)');ax.set_title(ch);ax.legend();ax.grid(alpha=.2)
    axes[0].set_ylabel('Repeatable pairs (not physical family accuracy)');fig.suptitle('Repeatability under location, width and band perturbations; fixed angle/frequency gates\nLong-window RMS spans more rope, so horizontal positions differ for A versus B/C.')
    fig.savefig(BUNDLE/'repeatability-curvature.png',dpi=140);plt.close(fig)


if __name__=='__main__':main()
