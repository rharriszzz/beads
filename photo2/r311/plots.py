"""Sampled response maps: invalid, unevaluated and feasible cells stay distinct."""
from pathlib import Path
from collections import Counter
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from photo2.r297.common import ROOT,read,save,digest
from .model import PAIRS,BOUNDS,VARIABLES,starts,canonical

def run(out):
    out=Path(out);dest=ROOT/'photo2/review/r311';dest.mkdir(parents=True,exist_ok=True)
    rows=[read(p) for p in sorted((out/'trials').glob('*.gz'))]
    bykey={r['key']:r for r in rows}
    planned=read(out/'checkpoint.json')['plan'];seeds=starts()[:3];surfaces=[]
    for a,b in PAIRS:
        fig,axes=plt.subplots(3,3,figsize=(15,11),layout='constrained')
        for col,seed in enumerate(seeds):
            todo=[r for r in planned if r.get('pair')==[a,b] and r['family']==seed['name']]
            actual=[]
            for job in todo:
                key=digest(dict(implementation=seed['implementation'],parameters=canonical(job['parameters'])))
                if key in bykey:
                    actual.append(dict(bykey[key],cell=job['cell'],coordinates=job['coordinates']))
            bycell={tuple(r['cell']):r for r in actual};xx=sorted({r['coordinates'][0] for r in todo});yy=sorted({r['coordinates'][1] for r in todo})
            losses=np.full((len(yy),len(xx)),np.nan);target=losses.copy();coverage=losses.copy();minimum=[]
            for job in todo:
                i,j=job['cell'];r=bycell.get((i,j))
                if r and r['feasible']:
                    losses[j,i]=r['global_score'];target[j,i]=1-r['target_loss'];coverage[j,i]=1
                    # A sampled local minimum only if every in-grid neighboring
                    # cell has been evaluated; invalid neighbors do not bridge.
                    cells=[((i-1)%len(xx) if a=='phase' else i-1,j),((i+1)%len(xx) if a=='phase' else i+1,j),(i,j-1),(i,j+1)]
                    neighbors=[bycell.get((u,v)) for u,v in cells if 0<=u<len(xx) and 0<=v<len(yy)]
                    if neighbors and all(z is not None for z in neighbors) and all(not z['feasible'] or z['global_score']>=r['global_score'] for z in neighbors):minimum.append(r['id'])
                elif r and r['status']=='witnessed-penetration':coverage[j,i]=0
            for ri,(z,label) in enumerate([(losses,'Whole-circuit development score (lower)'),(target,'Mean first-error visible overlap (higher)'),(coverage,'Certified1 / witnessed penetration0; ? unresolved')]):
                ax=axes[ri,col];im=ax.pcolormesh(xx,yy,np.ma.masked_invalid(z),shading='nearest',cmap='viridis' if ri!=2 else 'coolwarm_r',vmin=0 if ri else None,vmax=1 if ri else None)
                invalid=[r for r in actual if r['status']=='witnessed-penetration']
                unresolved=[r for r in actual if r['status']=='unresolved-separation']
                other=[r for r in actual if not r['feasible'] and r not in invalid and r not in unresolved]
                if invalid:ax.scatter([r['coordinates'][0] for r in invalid],[r['coordinates'][1] for r in invalid],marker='x',c='red',s=18)
                if unresolved:ax.scatter([r['coordinates'][0] for r in unresolved],[r['coordinates'][1] for r in unresolved],marker='$?$',c='#db8700',s=60)
                if other:ax.scatter([r['coordinates'][0] for r in other],[r['coordinates'][1] for r in other],marker='D',c='#777777',s=20)
                ax.set(xlabel=a+(' (unwrapped rad)' if a=='phase' else ''),ylabel=b,title=seed['name']+'\n'+label)
                fig.colorbar(im,ax=ax,shrink=.75)
            unseen={(i,j) for (i,j),r in bycell.items() if r['feasible']};components=[]
            while unseen:
                start=unseen.pop();group=[start];stack=[start]
                while stack:
                    i,j=stack.pop()
                    for v in [((i-1)%len(xx) if a=='phase' else i-1,j),((i+1)%len(xx) if a=='phase' else i+1,j),(i,j-1),(i,j+1)]:
                        if v in unseen:unseen.remove(v);stack.append(v);group.append(v)
                components.append([list(x) for x in group])
            surfaces.append(dict(family=seed['name'],pair=[a,b],planned=len(todo),evaluated=len(actual),feasible=sum(r['feasible'] for r in actual),sampled_minima=minimum,observed_grid_feasible_components=components,
                                 policy='Sampled cells only. Missing cells can connect apparent components; even complete discrete grids do not exclude narrow feasible continuous paths. No smooth interpolant or untested area implied.'))
        fig.suptitle(f'{a} / {b}: direct proposals. Red × penetration; orange ? unresolved; grey ◇ numerical/bounds; blank untested. Other fields frozen.')
        fig.savefig(dest/f'response-{a}-{b}.png',dpi=150);plt.close(fig)
    save(out/'response-surfaces.json',surfaces)
    coverage=[]
    for family in [s['name'] for s in starts()]:
        rr=[r for r in rows if r['family']==family]
        for key,(lo,hi) in BOUNDS.items():
            allv=[r['parameters'][key] for r in rr];feas=[r['parameters'][key] for r in rr if r['feasible']]
            coverage.append(dict(family=family,parameter=key,exploration_box=[lo,hi],attempted_range=[min(allv),max(allv)],feasible_range=[min(feas),max(feas)] if feas else None,
                                 unique_attempted=len(set(allv)),unique_feasible=len(set(feas)),policy='Projected min/max and unique values, not uniform joint coverage.'))
    save(out/'coverage.json',dict(ranges=coverage,types=dict(Counter(r['kind'] for r in rows)),statuses=dict(Counter(r['status'] for r in rows)),surfaces=surfaces,
                                 missing_highlight_trials=sum(r.get('missing_highlights',0)>0 for r in rows),derivative_proposals=0,missing_highlight_basin_rejections=0))
    fig,axes=plt.subplots(1,3,figsize=(15,4),layout='constrained')
    for ax,seed in zip(axes,seeds):
        rr=[r for r in rows if r['family']==seed['name'] and r['feasible']]
        for kind,mark in [('start','*'),('map','o'),('sobol','s'),('refine','+')]:
            z=[r for r in rr if r['kind']==kind]
            ax.scatter([r['global_score'] for r in z],[1-r['target_loss'] for r in z],s=25 if kind!='start' else 120,marker=mark,label=kind,alpha=.65)
        ax.set(xlabel='Whole-circuit development score (lower)',ylabel='Mean visible overlap at two first errors',title=seed['name']);ax.legend();ax.grid(alpha=.2)
    fig.suptitle('Local/global tradeoff: every point is a certified complete necklace')
    fig.savefig(dest/'local-global-tradeoff.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for row,block in enumerate([['phase','s0','elevation','roll'],['elevation','minor','scale','axial']]):
        for col,seed in enumerate(seeds):
            ax=axes[row,col];rr=[r for r in rows if r['family']==seed['name'] and r['kind']=='sobol' and r['block']==block]
            good=[r for r in rr if r['feasible']];norm=Normalize(min([r['global_score'] for r in good],default=0),max([r['global_score'] for r in good],default=1));cmap=plt.get_cmap('viridis_r')
            for r in rr:
                values=[(r['parameters'][k]-BOUNDS[k][0])/(BOUNDS[k][1]-BOUNDS[k][0]) for k in block]
                ax.plot(range(4),values,color=cmap(norm(r['global_score'])) if r['feasible'] else '#bbbbbb',alpha=.7 if r['feasible'] else .25)
            ax.set(xticks=range(4),xticklabels=block,ylim=(0,1),title=f"{seed['name']}: {len(good)}/{len(rr)} feasible")
    fig.suptitle('Four-variable Sobol combinations; normalized finite box. Grey rejected; colors = whole score.')
    fig.savefig(dest/'multivariate.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for ri,block in enumerate([['phase','s0','elevation','roll'],['minor','scale','axial','tilt']]):
        for ci,seed in enumerate(seeds):
            ax=axes[ri,ci];rr=[r for r in rows if r['family']==seed['name'] and r['kind']=='basin-sobol' and r['block']==block]
            good=[r for r in rr if r['feasible']];norm=Normalize(min([r['global_score'] for r in good],default=0),max([r['global_score'] for r in good],default=1))
            for r in rr:
                values=[(r['parameters'][k]-BOUNDS[k][0])/(BOUNDS[k][1]-BOUNDS[k][0]) for k in block]
                ax.plot(range(4),values,color=plt.get_cmap('viridis_r')(norm(r['global_score'])) if r['feasible'] else '#bbbbbb',alpha=.7 if r['feasible'] else .25)
            ax.set(xticks=range(4),xticklabels=block,ylim=(0,1),title=f"{seed['name']}: {len(good)}/{len(rr)} basin samples feasible")
    fig.suptitle('Four-variable refinement around selected promising basins; grey rejected, color whole score. Empty panels: no qualifying basin.')
    fig.savefig(dest/'basin-multivariate.png',dpi=150);plt.close(fig)
    pred=[r for r in rows if r.get('predicted_improvement') is not None and r.get('measured_improvement') is not None]
    fig,ax=plt.subplots(figsize=(6,5),layout='constrained')
    if pred:ax.scatter([r['predicted_improvement'] for r in pred],[r['measured_improvement'] for r in pred],s=12)
    ax.axhline(0,color='grey');ax.axvline(0,color='grey');ax.set(xlabel='Nearest-neighbor forecast improvement',ylabel='Measured native improvement',title='Weak forecast diagnostic; no forecast gates feasibility')
    fig.savefig(dest/'predicted-measured.png',dpi=150);plt.close(fig)
    # All strong observations retain their geographic location and missingness.
    selected=read(out/'selection.json')['models'];fig,axes=plt.subplots(len(seeds),1,figsize=(13,9),layout='constrained')
    for ax,seed in zip(axes,seeds):
        for item in [r for r in selected if r['family']==seed['name']]:
            model=read(out/'exports'/f"{item['name']}.json.gz");rr=[r for r in model['correspondences']['records'] if r['strong']]
            ax.scatter([r['arc'] for r in rr if r['error_px'] is not None],[r['error_px']/36.87817782917155 for r in rr if r['error_px'] is not None],s=8,label=item['name'],alpha=.55)
            missing=[r for r in rr if r['error_px'] is None]
            if missing:ax.scatter([r['arc'] for r in missing],np.full(len(missing),1.5),marker='x',c='red')
        ax.set(xlabel='Unchanged photographic circuit arc (px)',ylabel='Strong reflection error /D',title=seed['name']);ax.legend(fontsize=7)
    fig.suptitle('Native full-export nearest correspondences; red × missing. Dense surface-compatible metrics reported separately.')
    fig.savefig(dest/'whole-circuit-reflections.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(3,3,figsize=(16,10),layout='constrained')
    for row,seed in enumerate(seeds):
        for item in [r for r in selected if r['family']==seed['name']]:
            metric=read(out/'metrics'/f"{item['name']}.json.gz")
            region=metric['regional'];values=[
                [r['ownership_percent'] for r in region],
                [100*r['material']['paper'] if r['material'] else None for r in region],
                [r['reflection']['rms_D'] for r in region]]
            for col,v in enumerate(values):axes[row,col].plot(range(32),[np.nan if z is None else z for z in v],marker='.',linewidth=1,label=item['name'])
        for col,label in enumerate(['Modal interior coverage%','Frozen paper-cue occupation%','Surface-compatible reflection RMS/D']):
            axes[row,col].set(xlabel='Unchanged geographic section',ylabel=label,title=seed['name']);axes[row,col].grid(alpha=.2);axes[row,col].legend(fontsize=6)
    fig.suptitle('Dense whole-circuit regional outcomes: both retrospective partitions; missing regional evidence remains blank')
    fig.savefig(dest/'regional-outcomes.png',dpi=150);plt.close(fig)
    # Machine-readable flat vector table for external audit.
    fields=['id','family','kind','status','seconds','global_score','target_loss','missing_highlights']+VARIABLES
    with (out/'trial-vectors.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader()
        for r in rows:writer.writerow({**{k:r.get(k) for k in fields if k not in VARIABLES},**{k:r['parameters'][k] for k in VARIABLES}})
    return surfaces
