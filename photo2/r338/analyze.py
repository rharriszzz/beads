"""Frozen additions -> strict208 comparisons; full/common/physical cohorts distinct."""
import argparse,time
from .common import *

def metrics(obs,co,names,blocks):
    names=sorted(names);aa=np.array([co[o] for o in names]);c=np.array([COLORS.index(obs[o]['color']) for o in names]);b=np.array([blocks[o] for o in names]);k=aa@[7,6]%2704;entries=motif(k%208,c,b,names,208);strict=''.join(e['color'][0].upper() if e['status']=='strong' else '?' for e in entries);scores=[]
    for kind,parent in [('flat',None),('hier104',k%104)]:
        geo,_,_=predict(k%208,c,b,parent=parent);occ,_,_=predict(k%208,c,b,parent=parent,occ=k//208);scores.append(dict(model=kind,geographic=geo,whole_occurrence=occ))
    return dict(n=len(names),strict_sequence=strict,supported=strict.count('?')*-1+208,conflicting=sum(e['status']=='conflict' for e in entries),insufficient=sum(e['status'] in ['observed','unknown'] for e in entries),entries=entries,scores=scores)

def run(out):
    started=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False);g,oldobs,oldco=baseline();new=read(artifact('results/graph.json.gz'));freeze=read(artifact('results/body-freeze.json'));assert freeze['expected_pattern_colors_used'] is False;obs={o['id']:o for o in new['observations']};co={r['id']:tuple(r['ab']) for r in new['coordinates']};control=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={r['id']:r['section'] for r in control['rows']+control['maker_geography']};oldnames=sorted(oldco);tree=cKDTree([oldobs[o]['xy'] for o in oldnames]);newids=sorted(set(co)-set(oldco))
    for o in newids:blocks[o]=blocks[oldnames[int(tree.query(obs[o]['xy'])[1])]]
    distance,variants=rope_clearance(photograph());physical=[];core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids'])
    for o in sorted(co):
        p=np.array(obs[o]['xy']);x,y=np.rint(p).astype(int);local=[e for e in g['edges'] if np.linalg.norm((np.array(oldobs[e['source']]['xy'])+oldobs[e['target']]['xy'])/2-p)<100];spacing=float(np.median([np.linalg.norm(np.array(oldobs[e['source']]['xy'])-oldobs[e['target']]['xy']) for e in local]));clear=float(distance[y,x]);physical.append(dict(id=o,clearance=clear,settings_clearance=[float(v[y,x]) for v in variants],common_support_spacing=spacing,physical_interior=clear>=max(18.,.65*spacing),graph710=o in core))
    physicalids={r['id'] for r in physical if r['physical_interior']};core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);cohorts={
        'R337_common_baseline':metrics(oldobs,oldco,oldco,blocks),
        'R338_common_1039':metrics(obs,co,oldco,blocks),
        'R338_expanded':metrics(obs,co,co,blocks),
        'frozen710_before':metrics(oldobs,oldco,core,blocks),
        'frozen710_after':metrics(obs,co,core,blocks),
        'physical_interior_common_before':metrics(oldobs,oldco,physicalids&set(oldco),blocks),
        'physical_interior_common_after':metrics(obs,co,physicalids&set(oldco),blocks),
        'physical_interior_expanded':metrics(obs,co,physicalids,blocks)}
    assert cohorts['R337_common_baseline']==cohorts['R338_common_1039'];assert cohorts['frozen710_before']==cohorts['frozen710_after'];before=cohorts['R337_common_baseline']['entries'];after=cohorts['R338_expanded']['entries'];transitions=[dict(residue=i,before_status=a['status'],after_status=z['status'],before_ids=a['ids'],after_ids=z['ids'],before_counts=a['counts'],after_counts=z['counts']) for i,(a,z) in enumerate(zip(before,after)) if a!=z]
    # Evaluate only AFTER freeze. Train on original observations from other
    # complete cyclic occurrences; the target's own occurrence is never used.
    validation=[];aa=np.array([oldco[o] for o in oldnames]);cc=np.array([COLORS.index(oldobs[o]['color']) for o in oldnames]);kk=aa@[7,6]%2704
    for o in newids:
        k=int(np.dot(co[o],[7,6]))%2704;q=k//208;mask=kk//208!=q;base=np.bincount(cc[mask],minlength=3)+1;base=base/base.sum();training=[oldnames[j] for j in np.flatnonzero(mask&(kk%208==k%208))];counts=np.bincount([COLORS.index(oldobs[z]['color']) for z in training],minlength=3);prob=(counts+3*base)/(counts.sum()+3);baseline_color=COLORS[int(base.argmax())];prediction=COLORS[int(prob.argmax())];validation.append(dict(id=o,color=obs[o]['color'],residue=k%208,occurrence=q,training_ids=training,training_occurrences=sorted({int((7*oldco[z][0]+6*oldco[z][1])%2704)//208 for z in training}),probabilities=dict(zip(COLORS,prob.tolist())),prediction=prediction,agrees=obs[o]['color']==prediction,baseline_prediction=baseline_color,scope='Newly indexed previously maker-confirmed body; not a fresh independently labeled discovery or calibrated accuracy denominator. No body/color decision used this prediction.'))
    p337=read(ROOT/'photo2/r337/results/pattern208.json');assert cohorts['R337_common_baseline']['strict_sequence']==p337['strict_sequence'];save(out/'analysis.json.gz',dict(cohorts=cohorts,transitions=transitions,physical_interior_records=physical,blocks=blocks,newly_indexed_validation=validation,body_freeze_sha256=sha(artifact('results/body-freeze.json')),policy='Strict conflicts cannot disappear by adding corroborating votes while old authoritative records are retained. No colors changed; no cohort-selection gain called recovered pattern truth. Physical interior uses native outline clearance with common all-color scale, not graph degree. N2704/L208/13 repeats remain conditional.',seconds=time.perf_counter()-started));summary={name:{k:v for k,v in r.items() if k not in ['entries','strict_sequence']} for name,r in cohorts.items()};save(out/'summary.json',dict(cohorts=summary,transitions=transitions,newly_indexed_validation=validation,positions_resolved=0,previously_insufficient_now_supported=0,previously_supported_retained=176,seconds=time.perf_counter()-started));print('ANALYZE',[(n,r['n'],r['supported'],r['conflicting'],r['insufficient']) for n,r in cohorts.items()],validation,time.perf_counter()-started)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
