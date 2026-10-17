"""Replay selected trials through R315 oracle and retain full-scene diagnostics."""
import time
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save,pixels,sha,utc
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import paper
from photo2.r314.correspondence import evaluate_fixed
from photo2.r315.model import refined_trace,subset
from photo2.r315.diagnose import contact_graph,brackets
from .model import Chain
from photo2.r316.renderer import RayLayers
from photo2.r316.experiment import early
from photo2.r316 import followup
from .search import OUT,PATHS,SPLITS,merit,vals
NAMES=['R306','focused3','narrow','R316','hypothesis-A','hypothesis-B','hypothesis-C','joint-preserved']

def groups(data,e):
    src={r['id']:r for r in data['rows'] if r['kind']=='region'};ids=[c['id'] for c in e.doc['regions']];parent=list(range(len(ids)))
    sets=[set(map(tuple,pixels(src[k]['pixels']))) for k in ids]
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    overlaps=[]
    for i in range(len(ids)):
        for j in range(i):
            n=len(sets[i]&sets[j])
            if n:parent[find(i)]=find(j);overlaps.append(dict(a=ids[i],b=ids[j],pixels=n))
    gs={}
    for i,k in enumerate(ids):gs.setdefault(find(i),[]).append(k)
    return dict(groups=list(gs.values()),original_count=len(ids),group_count=len(gs),overlaps=overlaps,policy='Connected overlap of original historical supports, before R313 overlap exclusion. Equal weight per group; means inside group. No claim groups are statistically independent.')

def main():
    start=time.monotonic();e=engine();data=load()[0];search=read(OUT/'polish.json') if (OUT/'polish.json').exists() else (read(OUT/'refinement.json') if (OUT/'refinement.json').exists() else read(OUT/'search.json'));followup.OUT=OUT
    # R316 export/measurement code reused with the declared R317 rigid orientation class.
    from photo2.r316 import experiment
    experiment.Chain=Chain
    selected={k:dict(id=k,parameters=read(ROOT/'photo2'/v)['parameters']) for k,v in PATHS.items()}
    for h,i in search['selected'].items():selected['hypothesis-'+h]=read(OUT/'trials'/f'{i:05d}.json.gz')
    selected['joint-preserved']=read(OUT/'trials'/f'{read(OUT/"review-selection.json")["selected"]:05d}.json.gz')
    gg=groups(data,e);save(OUT/'correlation-groups.json',gg)
    old=read(ROOT/'photo2/r314/results/geometry-diagnostics.json.gz');arcs={r['id']:r['arc'] for r in old['models'][0]['regions']};baseowners={c['id']:c['index'] for k in SPLITS for c in read(ROOT/'photo2/r316/results/joint-recovery-model.json.gz')[k]['cores']};all_diag=[];checks=[]
    for name in NAMES:
        seed=selected[name];seed['epoch']='R317-selected' if name.startswith('hypothesis') else 'inherited-baseline';r=followup.export(name,seed,data,e);s=Chain(r['parameters'],data);a=np.load(OUT/f'{name}-raster.npz');tt=np.load(OUT/f'{name}-target.npz');layer=RayLayers().trace(s,tt['xy']);np.testing.assert_array_equal(layer['owner'],tt['owner']);np.testing.assert_array_equal(layer['unknown'],tt['unknown']);checks.append(dict(name=name,target_rays=len(tt['xy']),layer_oracle_disagreements=0))
        cs={c['id']:c for k in SPLITS for c in r[k]['cores']};regions=[]
        for c in e.doc['regions']:
            ix=np.flatnonzero(e.m['core'].ravel()==c['label']);xy=e.xy[ix];own=a['owner'][ix];cand=[]
            for j in s.tree.query_ball_point(c['point'],s.query_radius+15):
                iso=refined_trace(subset(s,[j]),xy);mask=iso['owner']>=0
                if not mask.any():continue
                vis=own==j;ii,nn=np.unique(own[mask&~vis],return_counts=True)
                cand.append(dict(index=int(s.indices[j]),isolated=float(mask.mean()),visible=float(vis.mean()),occluders=[dict(index=int(s.indices[k]) if k>=0 else None,pixels=int(n)) for k,n in zip(ii,nn)]))
            cand.sort(key=lambda z:-z['isolated']);fixed=baseowners[c['id']];jj=np.flatnonzero(s.indices==fixed) if fixed is not None else [];rgn=dict(id=c['id'],point=c['point'],arc=arcs[c['id']],split=c['split'],color=c['color'],modal=cs[c['id']],candidates=cand,fixed_R316_index=fixed,fixed_R316_visible=float(np.mean(own==jj[0])) if len(jj) else 0.)
            regions.append(rgn)
        group_metrics={}
        for part,k in enumerate(SPLITS):
            use=[z for group in gg['groups'] if (z:=[cs[c]['modal_fraction'] for c in group if next(x for x in e.doc['regions'] if x['id']==c)['split']==part])]
            group_metrics[k]=dict(groups=len(use),mean_single_owner=float(np.mean([np.mean(z) for z in use])) if use else None,original_core_count=sum(len(z) for z in use))
        failures={}
        for threshold in [.6,.7,.8,.9]:
            dd={}
            for sign in [-1,1]:
                rr=sorted([z for z in regions if z['arc']*sign>0],key=lambda z:abs(z['arc']));bad=next((z for z in rr if z['modal']['modal_fraction']<threshold),None)
                dd[str(sign)]=dict(first_measured_failure={k:bad[k] for k in ['id','point','arc']}|dict(index=bad['modal']['index'],visible=bad['modal']['modal_fraction']) if bad else None,preceding_measured_passes=next((i for i,z in enumerate(rr) if z is bad),len(rr)),unmeasured_addresses='unknown')
            failures[str(threshold)]=dd
        pp=paper(s);jj=np.flatnonzero((s.indices>=-100)&(s.indices<=99));clear=s.centers[:,2]-s.support(np.tile([0.,0.,1.],(s.n,1)),s.g['surface_tangent'])-pp['plane_z'];bins=np.floor(s.indices[jj]/6.5).astype(int);lows=[float(clear[jj[bins==b]].min()) for b in np.unique(bins)];complete=[float(clear[jj[bins==b]].min()) for b in np.unique(bins) if np.sum(bins==b)>=6];pp['complete_target_turn_minima']=dict(values=complete,median=float(np.median(complete)),maximum=max(complete),definition='Bins with at least six target addresses; partial end bins excluded');pp['target_minor_turn_minima']=dict(values=lows,median=float(np.median(lows)),maximum=max(lows),includes_partial_end_bins=True);all_diag.append(dict(name=name,regions=regions,group_metrics=group_metrics,first_failure=failures,paper=pp))
        if name.startswith('hypothesis') or name in ['R316','joint-preserved']:save(OUT/f'{name}-contacts.json.gz',contact_graph(s))
        print('EXPORTED',name,flush=True)
    save(OUT/'diagnostics.json.gz',dict(models=all_diag,policy='Conditional indices and original photo arcs; no verified physical chain. Fixed-R316-owner coverage separates geometry from changed modal assignment. Unmeasured indices are unknown, not zero error.'))
    epoch=read(ROOT/'photo2/r314/results/bright-epoch.json.gz');bright=evaluate_fixed(epoch,[],geometry_passed=False);bright['inherited_epoch_sha']=sha(ROOT/'photo2/r314/results/bright-epoch.json.gz');bright['policy']='118 inherited local observations including black reflections, retained ambiguous. No physical spot assignments established; no optical fit or invented Emax.';save(OUT/'bright-readiness.json',bright)
    save(OUT/'export-checks.json',dict(passed=True,checks=checks,seconds=time.monotonic()-start,utc=utc()))
if __name__=='__main__':main()
