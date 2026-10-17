"""Static scientific diagnostics, dense final measurement and performance ledger."""
from pathlib import Path
from copy import deepcopy
from collections import Counter,defaultdict
import csv,io,time,tarfile,gzip
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r295.geometry import AXES
from .objective import Engine,statistics,guard,violation
from .model import scene,geometry_key,coordinate,BOX
from .profiling import Timers

def source_bundle(directory,manifest):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode='w') as tar:
        for path in sorted(manifest):
            assert sha(ROOT/path)==manifest[path],path
            payload=(ROOT/path).read_bytes();info=tarfile.TarInfo(path);info.size=len(payload);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(payload))
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    (directory/'source.tar.gz').write_bytes(gzip.compress(raw.getvalue(),mtime=0))
    save(directory/'source-manifest.json',manifest)

def top_errors(rows,n=20):return sorted([r for r in rows if r['error_px'] is not None],key=lambda r:-r['error_px'])[:n]

def first_large(rows):
    results=[]
    for threshold in [5.,10.,15.,20.]:
        for direction in [-1,1]:
            rr=sorted([r for r in rows if r['index'] is not None and r['index']*direction>=0 and r['error_px'] is not None and r['error_px']>=threshold],key=lambda r:abs(r['index']))
            results.append(dict(threshold_px=threshold,direction=direction,first=rr[0] if rr else None,definition='First observed frozen conditional address exceeding threshold; unsampled physical addresses are unknown, and bead 0 has no independently verified reflection.'))
    return results

def regional(model,root):
    engine=Engine(model['stage'],dense=True)
    native=np.load(Path(root)/f'stage{model["stage"]}/exports/{model["name"]}-native.npz')
    own=native['guard_owner'][int(engine.bounds[-1]):int(engine.bounds[-1])+len(engine.cues['xy'])]
    un=native['guard_unknown'][int(engine.bounds[-1]):int(engine.bounds[-1])+len(engine.cues['xy'])]
    sections=(engine.cues['station']/engine.data['length']*32).astype(int)%32
    byid={r['id']:r for r in engine.regions};out=[]
    for sec in range(32):
        refs=[r for r in model['result']['reflections'] if r['section']==sec]
        support=[r for r in model['result']['safeguards']['supports'] if int(byid[r['id']]['station']/engine.data['length']*32)%32==sec]
        pp=(sections==sec)&engine.cues['paper'];cc=(sections==sec)&(engine.cues['color']>0)
        out.append(dict(section=sec,reflection=statistics(refs),ownership_percent=100*float(np.mean([r['modal_fraction'] for r in support])) if support else None,
            background_percent=100*float(np.mean((own[pp]>=0)|un[pp])) if pp.any() else None,
            omission_percent=100*float(np.mean(own[cc]<0)) if cc.any() else None))
    return out

def edges(xy,owner,unknown,allowed):
    # Complete selected-body boxes ensure each selected visible mask is complete.
    frame=np.full((3182,2540),-1,np.int16);unc=np.zeros(frame.shape,bool)
    ij=xy.astype(int);frame[ij[:,1],ij[:,0]]=owner;unc[ij[:,1],ij[:,0]]=unknown
    valid=np.isin(frame,np.array(allowed,int))&~unc
    edge=np.zeros(frame.shape,bool)
    edge[1:]|=frame[1:]!=frame[:-1];edge[:-1]|=frame[:-1]!=frame[1:]
    edge[:,1:]|=frame[:,1:]!=frame[:,:-1];edge[:,:-1]|=frame[:,:-1]!=frame[:,1:]
    edge&=valid
    from scipy.ndimage import binary_dilation
    edge&=~binary_dilation(unc)
    y,x=np.where(edge);return np.c_[x,y]

def export(root,stage,name,p,mapping,baseline=False):
    directory=Path(root)/f'stage{stage}';path=directory/'exports'/f'{name}.json.gz'
    if path.exists():return read(path)
    began=time.monotonic();engine=Engine(stage,dense=True);r=engine.evaluate(p,mapping,step=1.)
    assert r['feasible'],name
    timer=Timers();item,_=engine.geometry(p,timer);s=item['scene'];cert=s.certify(iterations=220,witnesses=True)
    owners=np.flatnonzero((s.indices>=-100)&(s.indices<=99)) if stage==1 else np.array(sorted({v-int(s.indices[0]) for v in mapping.values() if v is not None}),int)
    key=__import__('photo2.r297.common',fromlist=['digest']).digest(dict(owners=owners.tolist(),step=1.))
    xy,tr,_,_=item['camera'][key]
    edge=edges(xy,tr['owner'],tr['unknown'],owners)
    raster=directory/'exports'/f'{name}-native.npz';raster.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(raster,xy=xy,owner=tr['owner'],unknown=tr['unknown'],points=tr['points'],normals=tr['normal'],edge=edge,guard_xy=engine.xy,guard_owner=item['trace']['owner'],guard_unknown=item['trace']['unknown'])
    positions=[dict(index=int(k),center=s.centers[j].tolist(),projected_center=s.pc[j].tolist(),axis=s.line[j].tolist(),phase=float(s.phase[j]),frame={key:s.g[key][j].tolist() for key in AXES},stage1_cohort=bool(-100<=k<=99)) for j,k in enumerate(s.indices)]
    # Secondary native free-association control never changes fitting maps.
    pred,_=engine.optics(item,owners,1.,timer)
    from .objective import bottleneck
    free=engine.records(pred,bottleneck(engine.obs,pred))
    oldmap={r['id']:r['index'] for r in r['reflections']}
    changes=sum(oldmap[z['id']]!=z['index'] for z in free)
    uncertain=[o for o in engine.allobs if not o['strong'] and (stage==2 or engine.in_roi([o['point']])[0])]
    nearest=[]
    for o in uncertain:
        alt=sorted(pred,key=lambda z:np.linalg.norm(np.array(z['point'])-o['point']))
        nearest.append(dict(id=o['id'],observed=o['point'],nearest_conditional_index=alt[0]['index'] if alt else None,nearest_distance_px=float(np.linalg.norm(np.array(alt[0]['point'])-o['point'])) if alt else None,status='Weak/uncertain observation, nearest-only descriptive control; not fitted or verified identity'))
    result=dict(name=name,stage=stage,baseline=baseline,parameters=p,mapping=mapping,result=r,physical=cert,positions=positions,
                top20=top_errors(r['reflections']),missing=[z for z in r['reflections'] if z['error_px'] is None],first_large=first_large(r['reflections']),
                uncertain_observations=nearest,free_rematch_control=dict(metrics=statistics(free),reassigned=changes,rows=free,enters_primary_objective=False),
                initially_unambiguous_metrics=None,closure=s.closure(),seconds=time.monotonic()-began,raster_sha256=sha(raster))
    save(path,result);print('export stage',stage,name,r['metrics'],'seconds',round(result['seconds'],2),flush=True)
    return result

def draw_vectors(ax,photo,rows,edge=None,crop=None,title='',label=False):
    ax.imshow(photo)
    if edge is not None and len(edge):
        if crop:edge=edge[(edge[:,0]>=crop[0])&(edge[:,0]<=crop[1])&(edge[:,1]>=crop[2])&(edge[:,1]<=crop[3])]
        ax.scatter(edge[:,0],edge[:,1],s=.15,c='#00ffff',alpha=.55,rasterized=True)
    for i,r in enumerate(rows):
        x,y=r['observed']
        if r['predicted'] is None:ax.plot(x,y,'rx',ms=5);continue
        u,v=r['predicted'];uncertain=r['ambiguous'] or (r['alternatives'] and r['index']!=r['alternatives'][0]['index']);color='#ffba36' if uncertain else '#40ffff'
        ax.plot([x,u],[y,v],color=color,lw=.8);ax.plot(x,y,'o',mec='white',mfc='none',ms=3,mew=.7);ax.plot(u,v,'+',c=color,ms=4)
        if label:ax.text(x+3,y-3,str(i+1),color='white',fontsize=6,bbox=dict(facecolor='black',alpha=.6,pad=.5))
    if crop:ax.set_xlim(crop[:2]);ax.set_ylim(crop[3],crop[2])
    ax.set_title(title,fontsize=9);ax.set_aspect('equal');ax.axis('off')

def plots(directory,model,baseline):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    name=model['name'];stage=model['stage'];rows=model['result']['reflections'];before=baseline['result']['reflections']
    edge=np.load(directory.parent/'exports'/f'{name}-native.npz')['edge']
    bedge=np.load(directory.parent/'exports'/f'{baseline["name"]}-native.npz')['edge']
    crop=None
    if stage==1:
        pts=np.array([r['observed'] for r in rows]);lo=pts.min(0)-90;hi=pts.max(0)+90;crop=[lo[0],hi[0],lo[1],hi[1]]
    fig,axes=plt.subplots(2 if stage==1 else 1,1 if stage==1 else 2,figsize=(13,8) if stage==1 else (13,9),squeeze=False)
    axes=axes.ravel()
    bp=baseline['parameters']
    draw_vectors(axes[0],photo,before,bedge,crop,f'Before: N{bp["count"]}, hand {bp["hand"]:+d}, {bp["topology"]}; max {baseline["result"]["metrics"]["maximum_px"]:.2f}px')
    draw_vectors(axes[1],photo,rows,edge,crop,f'After: {name}; max {model["result"]["metrics"]["maximum_px"]:.2f}px; missing {model["result"]["metrics"]["missing"]}')
    for ax,doc in zip(axes[:2],[baseline,model]):
        zero=next(r for r in doc['positions'] if r['index']==0)['projected_center']
        ax.plot(*zero,marker='D',mfc='none',mec='#baff22',ms=7,mew=1.2)
        ax.text(zero[0]+7,zero[1]+15,'conditional bead 0 center',color='#baff22',fontsize=7,bbox=dict(facecolor='black',alpha=.5,pad=1))
    for ax in axes[2:]:ax.axis('off')
    fig.suptitle('Native visible boundaries and frozen reflection displacements. White circle: observed; plus: predicted; orange: ambiguous. All bodies occlude.',fontsize=10)
    fig.tight_layout();fig.savefig(directory/f'{name}-overlay.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(3,1,figsize=(12,9),sharex=True)
    for rr,label,color in [(before,'before','#888888'),(rows,'after','#0077b6')]:
        good=sorted([r for r in rr if r['error_px'] is not None and r['index'] is not None],key=lambda r:r['index'])
        for ax,key in zip(axes,['error_px','tangent_px','normal_px']):ax.scatter([r['index'] for r in good],[r[key] for r in good],s=12,label=label,color=color,alpha=.8)
    for ax,key in zip(axes,['Euclidean error (px)','Signed tangent (px)','Signed transverse (px)']):ax.set_ylabel(key);ax.axhline(0,color='k',lw=.5);ax.grid(alpha=.25)
    axes[0].axhline(10,color='#cc5555',ls='--',lw=.8,label='10px diagnostic threshold');axes[0].legend()
    axes[-1].set_xlabel('Frozen conditional physical bead address (identities unverified)');axes[0].set_title(name)
    fig.tight_layout();fig.savefig(directory/f'{name}-errors.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,direction in zip(axes,[-1,1]):
        for rr,label,col in [(before,'before','gray'),(rows,'after','#0077b6')]:
            good=sorted([r for r in rr if r['index'] is not None and r['index']*direction>=0 and r['error_px'] is not None],key=lambda r:abs(r['index']))
            xx=[abs(r['index']) for r in good];yy=[r['error_px'] for r in good]
            ax.scatter(xx,yy,s=15,label=label,color=col)
            if yy:ax.step(xx,np.maximum.accumulate(yy),where='post',color=col,lw=1)
        ax.set_title('From bead 0 toward '+('negative' if direction<0 else 'positive')+' addresses');ax.set_xlabel('Absolute conditional address');ax.set_ylabel('Error / observed cumulative maximum (px)');ax.axhline(10,color='#cc5555',ls='--',lw=.8);ax.grid(alpha=.2);ax.legend()
    fig.suptitle('First large observed errors; gaps between observations do not establish error-free physical beads',fontsize=10);fig.tight_layout();fig.savefig(directory/f'{name}-outward.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(5,4,figsize=(12,14));byid={r['id']:r for r in before}
    for ax,r in zip(axes.ravel(),model['top20']):
        x,y=r['observed'];draw_vectors(ax,photo,[r],edge,[x-40,x+40,y-40,y+40],f'{r["id"]}\ni={r["index"]}, {r["error_px"]:.2f}px')
        old=byid.get(r['id'])
        if old and old['predicted'] is not None:ax.plot([x,old['predicted'][0]],[y,old['predicted'][1]],'--',color='white',lw=.8)
    for ax in axes.ravel()[len(model['top20']):]:ax.axis('off')
    fig.suptitle('20 largest measured mismatches. Dashed white: before; colored: after. Missing lobes are listed separately.',fontsize=10)
    fig.tight_layout();fig.savefig(directory/f'{name}-top20.png',dpi=150);plt.close(fig)
    save(directory/f'{name}-top20.json',model['top20']);save(directory/f'{name}-missing.json',model['missing']);save(directory/f'{name}-first-large.json',model['first_large'])
    with (directory/f'{name}-reflections.csv').open('w',newline='') as f:
        cols=['id','index','error_px','dx_px','dy_px','tangent_px','normal_px','ambiguous','observed','predicted'];writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    if stage==1:
        physical=[r for r in model['positions'] if -100<=r['index']<=99];xyz=np.array([r['center'] for r in physical]);uv=np.array([r['projected_center'] for r in physical])
        raster=np.load(directory.parent/'exports'/f'{name}-native.npz');shown=set(raster['owner'][raster['owner']>=0].tolist());first=model['positions'][0]['index']
        visible=np.array([r['index']-first in shown for r in physical])
        fig=plt.figure(figsize=(13,5));a=fig.add_subplot(121,projection='3d');b=fig.add_subplot(122)
        a.plot(xyz[:,0],xyz[:,1],xyz[:,2],lw=.4,c='gray',alpha=.5);a.scatter(xyz[:,0],xyz[:,1],xyz[:,2],c=np.where(visible,'#0077b6','#aaaaaa'),s=8)
        a.set_xlabel('World x');a.set_ylabel('World y');a.set_zlabel('Height');a.set_title('All 200 consecutive physical centers; gray = no native visible pixel')
        b.imshow(photo);b.scatter(uv[:,0],uv[:,1],s=10,facecolors='none',edgecolors=np.where(visible,'#00ffff','#aaaaaa'),linewidths=.6)
        if crop:b.set_xlim(crop[:2]);b.set_ylim(crop[3],crop[2])
        for k,col in [(0,'#baff22'),(1,'#ffff00'),(6,'#ffffff'),(7,'#ff8800')]:
            p=physical[k+100];i=k+100;a.scatter(*xyz[i],s=35,c=col,edgecolors='k');a.text(*xyz[i],str(k));b.scatter(*uv[i],s=40,facecolors='none',edgecolors=col);b.text(uv[i,0]+4,uv[i,1]-4,str(k),color=col,fontsize=8)
            if k:b.plot([uv[100,0],uv[i,0]],[uv[100,1],uv[i,1]],c=col,lw=1)
        b.set_aspect('equal');b.axis('off');b.set_title('Conditional projected centers, including hidden bodies; offsets +1/+6/+7')
        fig.suptitle('Geometry diagnostic: these are model centers, not observed bead-center measurements',fontsize=10);fig.tight_layout();fig.savefig(directory/f'{name}-physical200.png',dpi=150);plt.close(fig)

def ledger(root,stage):
    directory=Path(root)/f'stage{stage}';rows=[read(p) for p in sorted((directory/'trials').glob('*.gz'))]
    if stage==2:rows += [read(p) for p in sorted((directory/'local/trials').glob('*.gz'))]
    totals=Counter();status=Counter();kinds=Counter();calibrations=0.;best={1.:None,2.:None};progress=[];cpu=0.
    local_control_cpu=0.
    if stage==2 and (directory/'local/summary.json').exists():
        extra_summary=read(directory/'local/summary.json')
        local_control_cpu=max(0.,extra_summary['cpu_seconds']-sum(r.get('cpu_seconds',0.) for r in rows if 'local_elapsed' in r))
    local_boundary_seen=False
    for row in rows:
        if 'local_elapsed' in row and not local_boundary_seen:
            cpu+=local_control_cpu;local_boundary_seen=True
        status[row['status']]+=1;kinds[row['kind']]+=1;cpu+=row.get('cpu_seconds',0.)
        if row.get('result'):
            for key,value in row['result']['profile']['exclusive_seconds'].items():totals[key]+=value
        if row.get('passes_safeguards'):
            value=row['objective_px'];step=row['step']
            if best[step] is None or value<best[step]:best[step]=value
        progress.append(dict(id=row['id'],elapsed=row['elapsed'],cpu_seconds=cpu,seconds=row['seconds'],kind=row['kind'],family=row['family'],status=row['status'],step=row['step'],objective_px=row.get('objective_px'),best_native_px=best[1.],best_coarse_px=best[2.],passes_safeguards=row.get('passes_safeguards'),rays=row.get('result',{}).get('numerics',{}).get('rays',0),geometry_reused=row.get('result',{}).get('geometry_reused',False),correspondence_epoch='full-chain' if 'local_elapsed' in row else 'stage1' if stage==1 else 'inherited-stage1'))
    for file in (directory/'calibration').glob('*.gz'):calibrations+=read(file)['result']['seconds']
    summary=read(directory/'summary.json')
    overhead=max(0,sum(r['seconds'] for r in rows)-sum(totals.values())-calibrations)
    extra=directory/'local/summary.json'
    if stage==2 and extra.exists():
        local=read(extra);summary.update(elapsed=summary['elapsed']+local['elapsed'],cpu_seconds=summary['cpu_seconds']+local['cpu_seconds'],evaluations=len(rows),peak_rss_mib=max(summary['peak_rss_mib'],local['peak_rss_mib']),statuses=dict(status),includes_contingent_native_simplex=True)
        totals['full_chain_correspondence_control_seconds']=local['calibration_control_seconds']
        summary['full_chain_correspondence_controls']=local['calibration_controls']
    totals['calibration_native_seconds']=calibrations;totals['other_trial_overhead_seconds']=overhead
    totals['checkpoint_loading_proposal_and_search_seconds']=max(0,summary['elapsed']-sum(r['seconds'] for r in rows)-totals['full_chain_correspondence_control_seconds'])
    native=[r for r in rows if r.get('passes_safeguards') and r['step']==1.]
    initial=native[0]['objective_px'] if native else None;gain=initial-best[1.] if native else None
    summary.update(subsystem_seconds=dict(totals),kinds=dict(kinds),progress=progress,per_evaluation_median_seconds=float(np.median([r['seconds'] for r in rows])),per_evaluation_p95_seconds=float(np.percentile([r['seconds'] for r in rows],95)),best_native_objective_px=best[1.],best_coarse_objective_px=best[2.],
        strict_running_best_improvements=max(0,sum(r.get('accepted_improvement',False) for r in rows)-sum(best[k] is not None for k in best)),
        initial_native_objective_px=initial,native_gain_px=gain,useful_native_gain_px_per_cpu_second=gain/summary['cpu_seconds'] if gain is not None else None)
    summary['camera_reused_evaluations']=sum(bool(r.get('result',{}).get('numerics',{}).get('camera_reused',False)) for r in rows)
    summary['correspondence_policy']='Owners frozen within each epoch. Stage 2 has an initial inherited-window epoch and a separate full-chain initialization control; compare models to their own same-map before values. Cross-epoch reductions are not necessarily geometry gains.'
    summary['contact_reused_evaluations']=sum(bool(r.get('result',{}).get('contact_reused',False)) for r in rows)
    summary['camera_rays_avoided_by_reuse']=sum(r.get('result',{}).get('numerics',{}).get('rays',0) for r in rows if r.get('result',{}).get('numerics',{}).get('camera_reused',False))
    save(directory/'performance-ledger.json',summary)
    if progress:
        with (directory/'performance-ledger.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(progress[0]),lineterminator='\n');w.writeheader();w.writerows(progress)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,xkey in zip(axes,['elapsed','cpu_seconds']):
        for step,col in [(1.,'#0077b6'),(2.,'#dd8800')]:
            rr=[p for p in progress if p['step']==step and p['best_native_px' if step==1 else 'best_coarse_px'] is not None]
            ax.step([r[xkey] for r in rr],[r['best_native_px' if step==1 else 'best_coarse_px'] for r in rr],where='post',c=col,label=f'{step:g}px lattice')
        ax.set_xlabel(xkey+' (seconds)');ax.set_ylabel('Best safeguarded penalized maximum (px)');ax.grid(alpha=.25);ax.legend()
        ax.set_ylim(0,min(100,max([r['best_native_px'] or 0 for r in progress]+[20])*1.1))
    fig.tight_layout();fig.savefig(directory/'plots/progress.png',dpi=150);plt.close(fig)
    # Actual attempts, certified candidates and numerical/resource gaps are distinct.
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    pairs=[('phase','s0'),('light_az','light_el'),('elevation','roll'),('minor','axial'),('scale','perspective'),('twist','gap_steps')]
    for ax,(a,b) in zip(axes.ravel(),pairs):
        for feasible,c,label in [(False,'#bbbbbb','rejected/uncertified'),(True,'#0077b6','certified')]:
            rr=[r for r in rows if r.get('feasible',False)==feasible]
            ax.scatter([coordinate(r['parameters'],a) for r in rr],[coordinate(r['parameters'],b) for r in rr],s=4,c=c,label=label,alpha=.5)
        ax.set_xlabel(a);ax.set_ylabel(b);ax.grid(alpha=.15)
    axes[0,0].legend(fontsize=7);fig.suptitle('Actual coupled attempts; union ranges and projections do not imply full joint coverage',fontsize=10);fig.tight_layout();fig.savefig(directory/'plots/coverage.png',dpi=150);plt.close(fig)
    coverage={}
    for k,box in BOX.items():
        values=[coordinate(r['parameters'],k) for r in rows];feasible=[coordinate(r['parameters'],k) for r in rows if r.get('feasible')]
        coverage[k]=dict(numerical_box=box,attempted=[min(values),max(values)] if values else None,certified=[min(feasible),max(feasible)] if feasible else None)
    save(directory/'coverage.json',dict(parameters=coverage,counts=sorted({r['parameters']['count'] for r in rows}),hands=sorted({r['parameters']['hand'] for r in rows}),topologies=sorted({r['parameters']['topology'] for r in rows}),kinds=dict(kinds),statuses=dict(status),joint_coverage_claim=False))
    return summary

def stage_diagnostics(root,stage):
    directory=Path(root)/f'stage{stage}';selected=directory/'final-selection.json'
    selection=read(selected if selected.exists() else directory/'selection.json');checkpoint=read(directory/'checkpoint.json');models=[];baseline_by_family={}
    full_chain=selection.get('correspondence_epoch')=='full-chain'
    calibration_directory=directory/'local/calibration' if full_chain else directory/'calibration'
    prefix='baseline-fullchain-' if full_chain else 'baseline-'
    (directory/'plots').mkdir(parents=True,exist_ok=True)
    def exterior_control(model):
        if model['result']['safeguards'].get('boundary_policy'):return model
        # Reuse every saved native ray; do not rerender or change fitted parameters.
        e=Engine(stage,dense=True);native=np.load(directory/'exports'/f'{model["name"]}-native.npz')
        np.testing.assert_array_equal(e.xy,native['guard_xy'])
        model['result']['search_epoch_safeguards']=deepcopy(model['result']['safeguards'])
        model['result']['safeguards']=e.safeguards(dict(owner=native['guard_owner'],unknown=native['guard_unknown']),scene(model['parameters'],e.data))
        model['postseal_boundary_control']='Stage 1 fitting included unannotated native hole edges. Exterior-only diagnostic uses the same saved rays; fitting/search records and primary reflection errors remain unchanged.'
        save(directory/'exports'/f'{model["name"]}.json.gz',model);return model
    common=None
    if stage==2:
        cal=read(calibration_directory/'R306-2405.json.gz')
        common=export(root,stage,prefix+'R306-2405',cal['parameters'],cal['result']['mapping'],True)
        common['family']='R306-2405';common['correspondence_epoch']='full-chain' if full_chain else 'inherited-stage1'
        save(directory/'exports'/f'{common["name"]}.json.gz',common)
        baseline_by_family['R306-2405']=common
    for row in selection['models']+selection.get('tradeoffs',[]):
        family=row['family'];basefile=calibration_directory/f'{family}.json.gz';cal=read(basefile);mapping=cal['result']['mapping']
        if family not in baseline_by_family:
            base=exterior_control(export(root,stage,prefix+family,cal['parameters'],mapping,True));base['family']=family;base['correspondence_epoch']='full-chain' if full_chain else 'inherited-stage1'
            save(directory/'exports'/f'{base["name"]}.json.gz',base);baseline_by_family[family]=base
        pp=row['parameters'];name=f'trial-{row["id"]:06d}-N{pp["count"]}-h{pp["hand"]}-{pp["topology"]}'
        model=exterior_control(export(root,stage,name,row['parameters'],mapping));model['family']=family;model['trial']=row['id'];model['correspondence_epoch']='full-chain' if full_chain else 'inherited-stage1'
        if full_chain and 'legacy_fixed_map_control' not in model:
            model['legacy_fixed_map_control']=Engine(2).evaluate(row['parameters'],checkpoint['mappings'][family],step=1.,monitor=False)
            model['mapping_control']=dict(changed_owners=cal['changed_owners'],old_baseline_metrics=cal['old_metrics'],full_chain_baseline_metrics=cal['result']['metrics'],assignment_only_change_is_not_fitting_gain=True)
        model['tradeoff_only']=not row.get('passes_safeguards',False)
        base=baseline_by_family[family]
        initial={r['id']:(not r['ambiguous'] and bool(r['alternatives']) and r['index']==r['alternatives'][0]['index']) for r in cal['result']['reflections']}
        model['initially_unambiguous_metrics']=statistics([r for r in model['result']['reflections'] if initial.get(r['id'],False)])
        model['initially_ambiguous_metrics']=statistics([r for r in model['result']['reflections'] if not initial.get(r['id'],False)])
        model['dense_passes_safeguards']=guard(model['result'],base['result']);model['dense_violation']=violation(model['result'],base['result'])
        if common is not None:
            model['dense_passes_family_safeguards']=model['dense_passes_safeguards']
            model['dense_passes_common_safeguards']=guard(model['result'],common['result'])
            model['dense_passes_safeguards'] &= model['dense_passes_common_safeguards']
            model['common_R306_metrics']=common['result']['metrics'];model['common_R306_safeguards']=common['result']['safeguards']
        model['before_metrics']=base['result']['metrics'];model['before_safeguards']=base['result']['safeguards']
        model['regional']=regional(model,root);model['before_regional']=regional(base,root)
        save(directory/'exports'/f'{name}.json.gz',model)
        plotfiles=[directory/'plots'/f'{name}-{suffix}.png' for suffix in ['overlay','errors','outward','top20']+(['physical200'] if stage==1 else [])]
        if not all(p.exists() for p in plotfiles):plots(directory/'plots',model,base)
        models.append(model)
        if (directory/'plots'/f'{name}-regional.png').exists():continue
        fig,axes=plt.subplots(2,2,figsize=(12,6))
        for ax,key,title in zip(axes.ravel(),['maximum_px','ownership_percent','background_percent','omission_percent'],['Reflection maximum (px)','Interior ownership (%)','Paper occupation (%)','Colored omission (%)']):
            for rr,label,color in [(model['before_regional'],'before','gray'),(model['regional'],'after','#0077b6')]:
                vals=[r['reflection'][key] if key=='maximum_px' else r[key] for r in rr]
                ax.plot(range(32),[v if v is not None else np.nan for v in vals],'.-',label=label,c=color,lw=1)
            ax.set_title(title);ax.set_xlabel('Fixed photographic region');ax.grid(alpha=.2);ax.legend(fontsize=7)
        fig.tight_layout();fig.savefig(directory/'plots'/f'{name}-regional.png',dpi=150);plt.close(fig)
    performance=ledger(root,stage)
    save(directory/'diagnostics.json',dict(sealed=True,stage=stage,models=[dict(name=m['name'],family=m['family'],trial=m['trial'],count=m['parameters']['count'],hand=m['parameters']['hand'],topology=m['parameters']['topology'],tradeoff_only=m.get('tradeoff_only',False),metrics=m['result']['metrics'],before=m['before_metrics'],safeguards={k:v for k,v in m['result']['safeguards'].items() if k not in ['supports','boundaries']},dense_passes_safeguards=m['dense_passes_safeguards'],initially_unambiguous_metrics=m['initially_unambiguous_metrics']) for m in models],performance={k:v for k,v in performance.items() if k!='progress'}))
    return models

def performance_summary(root):
    root=Path(root);old=read(root/'profiling/baseline.json');new=read(root/'profiling/minimax-preflight.json');rows=[]
    for stage in ['200','whole']:
        for finite in [False,True]:
            groups={label:[r for r in old['records'] if r['stage']==stage and r['finite']==finite and r['label']==label and r['repetition']>0] for label in ['baseline','optimized']}
            b=float(np.median([r['wall_seconds'] for r in groups['baseline']]));a=float(np.median([r['wall_seconds'] for r in groups['optimized']]))
            components={}
            for key in groups['baseline'][0]['profile']['exclusive_seconds']:
                bv=float(np.median([r['profile']['exclusive_seconds'].get(key,0) for r in groups['baseline']]));av=float(np.median([r['profile']['exclusive_seconds'].get(key,0) for r in groups['optimized']]))
                components[key]=dict(before_seconds=bv,after_seconds=av,speedup=bv/av if av else None)
            rows.append(dict(region=stage,finite_light=finite,before_seconds=b,after_seconds=a,speedup=b/a,components=components))
    cached=[]
    for stage in [1,2]:
        for finite in [False,True]:
            records=[r for r in new['records'] if r['stage']==stage and r['finite']==finite]
            cold=records[0]['seconds'];warm=float(np.median([r['seconds'] for r in records[1:]]))
            cached.append(dict(stage=stage,finite_light=finite,cold_native_seconds=cold,cached_native_seconds=warm,speedup=cold/warm,peak_rss_mib=max(r['profile']['peak_rss_mib'] for r in records)))
    result=dict(original_baseline=rows,minimax_cache=cached,original_complete_objective=[dict(label=r['label'],seconds=r['seconds']) for r in old['existing_full_objective']],
                accuracy=old['accuracy_checks']+new['accuracy_checks'],sampling_note='Initial timings were collected with the same statistical sampler enabled for both variants. Native audits and later minimax preflight are separately timed. Warm medians use two repetitions, not precise population estimates.')
    extra=root/'profiling/stage2-optimizations.json'
    if extra.exists():result['stage2_optimizations']=read(extra)
    save(root/'performance-comparison.json',result)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,series,keys in [(axes[0],rows,('before_seconds','after_seconds')),(axes[1],cached,('cold_native_seconds','cached_native_seconds'))]:
        x=np.arange(len(series));ax.bar(x-.18,[r[keys[0]] for r in series],.36,label=keys[0]);ax.bar(x+.18,[r[keys[1]] for r in series],.36,label=keys[1]);ax.set_yscale('log');ax.set_ylabel('Wall seconds (log scale)');ax.legend(fontsize=7)
        ax.set_xticks(x,[f'{r.get("region",r.get("stage"))}\n'+('finite' if r['finite_light'] else 'directional') for r in series])
    fig.tight_layout();fig.savefig(root/'performance-comparison.png',dpi=150);plt.close(fig)
    return result

def finalize(root):
    root=Path(root);models=[]
    for stage in [1,2]:models.extend(stage_diagnostics(root,stage))
    performance_summary(root)
    controls=[]
    for stage in [1,2]:
        model=min([m for m in models if m['stage']==stage and not m.get('tradeoff_only',False)],key=lambda m:m['result']['metrics']['objective_px'])
        e=Engine(stage,dense=True);fine=e.evaluate(model['parameters'],model['mapping'],step=.5,monitor=False)
        byid={r['id']:r for r in fine['reflections']};delta=[];presence=[]
        for row in model['result']['reflections']:
            rr=byid[row['id']]
            if (rr['predicted'] is None)!=(row['predicted'] is None):presence.append(row['id'])
            if rr['predicted'] is not None and row['predicted'] is not None:delta.append(float(np.linalg.norm(np.array(rr['predicted'])-row['predicted'])))
        controls.append(dict(stage=stage,model=model['name'],native_metrics=model['result']['metrics'],half_pixel_metrics=fine['metrics'],maximum_centroid_shift_px=max(delta,default=0.),lobe_presence_changes=presence,fine_result=fine,policy='Identical parameters and frozen owners, no new proposals or selection. Native 1px is the fitted definition; half-pixel sampling is a resolution sensitivity control, not independent physical truth.'))
    save(root/'numerical-resolution-controls.json.gz',controls)
    engine=Engine(2);save(root/'observation-catalog.json.gz',dict(observations=engine.allobs,stage1=engine.local,all_retained=True,strong=sum(o['strong'] for o in engine.allobs),physical_identities_verified=0))
    full_pool_control(root)
    import subprocess,sys
    subprocess.run([sys.executable,'-c','from pathlib import Path; import sys; from photo2.r312.verify import run; run(Path(sys.argv[1]))',str(root.resolve())],check=True)
    from .report import write
    write(root)
    return models

def full_pool_control(root):
    """Retrospective all-body optical control; never changes fitting or selection."""
    root=Path(root);path=root/'full-necklace-optical-pool-control.json.gz'
    if path.exists():return read(path)
    d=read(root/'stage2/diagnostics.json');best=min([m for m in d['models'] if not m['tradeoff_only']],key=lambda m:m['metrics']['objective_px'])
    chosen=[read(root/f'stage2/exports/{best["name"]}.json.gz')]
    prefix='baseline-fullchain-' if chosen[0].get('correspondence_epoch')=='full-chain' else 'baseline-'
    chosen.append(read(root/f'stage2/exports/{prefix}{chosen[0]["family"]}.json.gz'))
    result=[]
    from .objective import bottleneck
    from .verify import recompute
    for model in chosen:
        began=time.monotonic();e=Engine(2);timer=Timers();item,_=e.geometry(model['parameters'],timer);s=item['scene']
        pred,meta=e.optics(item,np.arange(s.n),1.,timer)
        rows=e.records(pred,model['mapping']);byid={r['id']:r for r in rows};delta=[]
        for r in model['result']['reflections']:
            rr=byid[r['id']];assert (r['predicted'] is None)==(rr['predicted'] is None)
            if rr['predicted'] is not None:delta.append(float(np.linalg.norm(np.array(r['predicted'])-rr['predicted'])))
        assert max(delta,default=0.)<1e-9
        free=e.records(pred,bottleneck(e.obs,pred));metrics=recompute(rows)
        for k,v in metrics.items():assert abs(v-model['result']['metrics'][k])<1e-8
        result.append(dict(name=model['name'],body_count=s.n,predicted_lobes=len(pred),rays=meta['rays'],seconds=time.monotonic()-began,profile=timer.result(),maximum_target_pool_centroid_difference_px=max(delta,default=0.),fixed_map_metrics=statistics(rows),full_pool_rows=rows,full_pool_free_rematch_control=dict(metrics=statistics(free),reassigned=sum(r['index']!=model['mapping'][r['id']] for r in free),enters_primary_objective=False),predictions=pred))
    receipt=dict(utc=utc(),passed=True,models=result,policy='All physical bodies produce native lobes; fixed-map positions exactly match target-body rendering. Full-pool alternatives and rematching are diagnostics only, never fitting gains. Other export alternative lists and weak nearest-only diagnostics use their rendered target-owner pool and can omit unrendered competitors.')
    save(path,receipt);return receipt
