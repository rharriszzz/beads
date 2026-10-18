"""Read-only diagnostics, model-feedback proposals and conditional color constraints."""
from .coupled import *
from scipy.stats import linregress

def main():
 g=read(OUT/'graph.json');ns={n['id']:n for n in g['intersections']};obs={o['id']:o for o in g['observations']};guide=read(OUT/'guide.json');xy=np.array([[r['x'],r['y']] for r in guide['samples']]);tree=cKDTree(xy);length=guide['length_px'];nearest={o:int(tree.query(n['xy'])[1]) for o,n in ns.items()};coverage=[]
 for sec in range(16):
  nn=[n for n in ns.values() if nearest[n['id']]*16//len(xy)==sec];ee=[e for e in g['graph']['edges'] if nearest[e['source']]*16//len(xy)==sec];ww=[w for w in g['windows'] if int(w['arc_px']*16/length)==sec]
  coverage.append(dict(section=sec,arc_start=sec*length/16,arc_end=(sec+1)*length/16,observations=len(nn),indexed=sum(n['component'] is not None for n in nn),interior_indexed=sum(n['component'] is not None and n['region_priority']=='interior' for n in nn),edge_indexed=sum(n['component'] is not None and n['region_priority']=='edge' for n in nn),unresolved=sum(n['component'] is None for n in nn),accepted_links=len(ee),windows=len(ww),successful_windows=sum(bool(w['hypotheses']) for w in ww)))
 assert sum(s['observations'] for s in coverage)==len(ns)
 window_centers=np.array([w['center'] for w in g['windows']]);guide_dist=cKDTree(window_centers).query(xy)[0]
 breaks=[dict(previous=t['previous'],current=t['current'],xy=g['windows'][t['current']]['center'],arc=g['windows'][t['current']]['arc_px'],checks=t['checks']) for t in g['transitions'] if not t['translation_consistent']]
 models=[];feedback=[]
 for label in ['R319-best','R321-geometry-best','R321-photo-sized-rescue']:
  m=read(OUT/(label+'-frozen.json.gz'));ref=next(r for r in m['seed_origin_extension'] if r['id']=='C-1497-0271');rows=m['seed_origin_extension'];strict=[r for r in rows if r['xy'][0]<=1510 and r['modal_fraction']>=.6];sl=linregress([r['index'] for r in strict],[r['index_discrepancy'] for r in strict]);first={}
  for sign in [-1,1]:
   ordered=sorted([r for r in strict if sign*(r['index']-ref['index'])>0],key=lambda r:abs(r['index']-ref['index']));first[str(sign)]=next((r for r in ordered if r['index_discrepancy']!=0),None)
  counts={f:dict(Counter(e['status'] for e in m['edge_comparison'] if e['family']==f)) for f in ['F0','F1','difference']}
  sectiondrift=[];sr={r['id']:r for r in m['support']};N=len(m['positions']['indices']);indices=np.array(m['positions']['indices']);pcs=np.array(m['positions']['projected'])
  for c in m['components']:
   best=c['best'];rr=[]
   for oid,k in best['mapping'].items():
    r=sr[oid]
    if r['modal_fraction']<.6:continue
    d=r['modal_index']-k
    if m['topology']=='closed':d=int((d+N//2)%N-N//2)
    rr.append(dict(id=oid,index=k,discrepancy=d,xy=r['xy']))
   if len(rr)>=12:
    reg=linregress([r['index'] for r in rr],[r['discrepancy'] for r in rr]);sectiondrift.append(dict(component=c['component'],n=len(rr),slope_per_100_indices=reg.slope*100,r=float(reg.rvalue) if np.isfinite(reg.rvalue) else None,rows=rr))
  known_edges=[e for e in m['edge_comparison'] if e['status'] in ['agrees','disagrees']]
  curve=np.array([abs(guide['samples'][nearest[e['source']]]['curvature']) for e in known_edges]);bad=np.array([e['status']=='disagrees' for e in known_edges]);rho=spearmanr(curve,bad.astype(float));cuts=np.quantile(curve,[0,.25,.5,.75,1]);bins=[]
  for j in range(4):
   mask=(curve>=cuts[j])&(curve<cuts[j+1] if j<3 else curve<=cuts[j+1]);bins.append(dict(curvature_interval=cuts[j:j+2].tolist(),links=int(mask.sum()),wrong=int(bad[mask].sum()),wrong_fraction=float(bad[mask].mean())))
  models.append(dict(label=label,whole_photo_curvature_error_spearman=float(rho.statistic),whole_photo_curvature_bins=bins,seed_reference=ref,first_from_reference=first,strict_seed_extension_n=len(strict),strict_index_drift_per_100=sl.slope*100,strict_drift_r=float(sl.rvalue) if np.isfinite(sl.rvalue) else None,family_counts=counts,component_drifts=sectiondrift,curvature_test=m['curvature_index_error_spearman'],curvature_n=m['curvature_test_n']))
  for pair in read(OUT/'bridge.json')['summary']:
   a,b=[sr[o] for o in pair['pair']];delta=None if a['modal_index'] is None or b['modal_index'] is None else b['modal_index']-a['modal_index']
   if delta is not None and m['topology']=='closed':delta=int((delta+N//2)%N-N//2)
   feedback.append(dict(model=label,pair=pair['pair'],modal_physical_delta=delta,modal_fractions=[a['modal_fraction'],b['modal_fraction']],source='model-generated first-hit ownership hypothesis',photo_context_deltas=pair['credible_local_deltas'],independent_photo_result='ambiguous multiscale alternatives; no promotion',photo_context_was_selected_before_model_comparison=True))
 # Exact-repeat incompatibilities from the independently checked reference geography.
 cohort=[n for n in ns.values() if 1180<=n['xy'][0]<=1505 and 200<n['xy'][1]<390 and n['region_priority']=='interior' and n['component'] is not None];patterns=[]
 for name,weights in [('A',[7,6]),('B',[6,7]),('reverse_A',[-7,-6]),('reverse_B',[-6,-7])]:
  rows=[];kk=[int(np.dot(n['relative_ab'],weights)) for n in cohort]
  for period in range(1,201):
   compared=0;conflicts=[]
   for i,a in enumerate(cohort):
    for j,b in enumerate(cohort[:i]):
     if (kk[i]-kk[j])%period:continue
     compared+=1
     if a['color']!=b['color']:conflicts.append([a['id'],b['id']])
   rows.append(dict(period=period,compared_pairs=compared,color_conflicts=len(conflicts),first_conflict=conflicts[0] if conflicts else None,compatible_with_current_color_cues=not conflicts))
  patterns.append(dict(interpretation=name,observations=len(cohort),span=max(kk)-min(kk)+1,periods=rows))
 save(OUT/'pattern-constraints.json',dict(results=patterns,policy='Exploratory exact constraints on automatic color cues in reference geography only. Unknown and hidden slots retained; zero conflicts with zero comparisons is uninformative. No global repeat or N inferred; both reversals retained. Color uncertainty can invalidate exclusions.'))
 save(OUT/'analysis.json',dict(coverage_exclusive=coverage,chart_breaks=breaks,guide_length_px=length,guide_max_distance_to_processed_window_px=float(guide_dist.max()),guide_min_clearance_px=float(min(guide['centerline_clearance_px'])),guide_paper_fraction=float(np.mean(np.array(guide['centerline_clearance_px'])==0)),models=models,feedback=feedback,colors=dict(Counter(n['color'] for n in ns.values())),family_fragments=dict(Counter(t['family'] for t in g['tracks'])),seam=g['transitions'][0],limitations=['Original R250 spline length re-evaluated, not an independently calibrated centerline.','Modal predicted surface index is not physical truth.','Global family choice can differ by disconnected component; no whole-circuit orientation certified.','Main beam first-bridge acceptance is contested by additional context; no fitting correspondence beyond x1510.']))
 print('ANALYSIS',len(coverage),len(breaks),[(m['label'],m['strict_index_drift_per_100']) for m in models],flush=True)
if __name__=='__main__':main()
