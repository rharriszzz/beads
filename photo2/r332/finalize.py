"""Global additive integrity screen, complete omission ledger and pure predictions.

This is not another growth/search. It can only withdraw a conflicting R332
addition, preserve its measured evidence provisionally, and enumerate omissions.
"""
import argparse,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from .common import *
from .recover import Completion

def novelty(accepted,pool):
    from scipy.spatial import cKDTree
    poolxy=np.array([p['xy'] for p in pool]);ptree=cKDTree(poolxy)
    for x in accepted:
        if x['known']:continue
        dist,idx=ptree.query(x['xy']);x['nearest_cached_candidate']=dict(id=pool[idx]['id'],distance=float(dist));intersections=[]
        if x['body_only']:
            measured=set(map(tuple,x['native']['pixels_xy']))
            for j in ptree.query_ball_point(x['xy'],35):
                other=pool[j]
                if not other.get('source_support'):continue
                cached={(xx,y) for y,a,z in other['source_support'] for xx in range(a,z+1)};n=len(measured&cached)
                if n:intersections.append(dict(id=other['id'],shared_native_pixels=n))
        x['overlapping_cached_supports']=intersections
        # Strict novelty accounting: even a small overlap is conservatively
        # classified as cache-related, not a new photographic detection claim.
        x['genuine_new_native_extraction']=bool(x['body_only'] and dist>=8 and not intersections)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();run=Path(args.run);r=read(run/'graph.json.gz');g,base,H=baseline();engine=Completion(g,base,H)
    engine.obs={o['id']:o for o in r['observations']};engine.co={x['id']:tuple(x['ab']) for x in r['coordinates']};engine.links={edgekey(e['source'],e['target']):e for e in r['edges']};engine.occupied={representative(v,H):o for o,v in engine.co.items()};engine.rebuild();baseline_ids={o['id'] for o in g['observations']};withdrawn=[]
    # Final all-observation corridor check catches interactions between additions
    # assessed simultaneously in an earlier batch.
    for key,e in list(engine.links.items()):
        if e['origin']=='baseline':continue
        ck=engine.link_check(e['source'],engine.obs[e['source']]['xy'],e['target'],engine.obs[e['target']]['xy'])
        if not ck['allowed']:
            withdrawn.append(dict(e,final_check=ck,status='withdrawn R332 edge'));del engine.links[key]
        else:e['final_native_check']=ck
    # Refuse a new assignment that loses its required multi-direction support.
    retracted=[]
    for iteration in range(8):
        incident=defaultdict(list)
        for e in engine.links.values():
            incident[e['source']].append(e);incident[e['target']].append(e)
        bad=[]
        for record in r['accepted_additions']:
            o=record['id']
            if o not in engine.co:continue
            ee=incident[o];families={e['family'] for e in ee};neighbors=[e['source'] if e['target']==o else e['target'] for e in ee]
            triangles=sum(edgekey(a,z) in engine.links for i,a in enumerate(neighbors) for z in neighbors[i+1:])
            color=record['color'];appearance=record['native']['appearance'];chosen=['red','yellow','black'].index(color)
            conflict=not record['known'] and (np.argmax(appearance['probabilities'])!=chosen)
            if len(families)<2 or triangles<1 or conflict:bad.append((o,'lost two-family/shared-neighbor support' if not conflict else 'cached color conflicts with appearance winner'))
        if not bad:break
        for o,why in bad:
            del engine.co[o];retracted.append(dict(id=o,reason=why));engine.obs[o]['r332_status']='provisional'
            for key,e in list(engine.links.items()):
                if o in key:withdrawn.append(dict(e,status='withdrawn with unsupported endpoint'));del engine.links[key]
    retracted_ids={x['id'] for x in retracted};accepted=[x for x in r['accepted_additions'] if x['id'] not in retracted_ids]
    engine.occupied={representative(v,H):o for o,v in engine.co.items()};engine.rebuild()
    original_provisional=r['provisional_observations']+[dict(x,status='provisional',reasons=x['reasons']+['final integrity retraction']) for x in r['accepted_additions'] if x['id'] in retracted_ids]
    provisional_groups=defaultdict(list);alias=[];uncertain=[]
    for p in original_provisional:
        if p['id'] in engine.co:continue
        if not p.get('cell'):continue
        key=representative(p['cell'],H);owner=engine.occupied.get(key);distance,idx=engine.alltree.query(p['xy']);nearest=engine.allnames[idx]
        if owner or (distance<13 and nearest!=p['id']):
            alias.append(dict(id=p['id'],owner=owner,nearest=nearest,distance=float(distance),reason='occupied coordinate or close recorded support; association unresolved, not a second accepted bead'));continue
        provisional_groups[key].append(p)
    provisional=[]
    for key,rows in provisional_groups.items():
        best=min(rows,key=lambda x:(len(x['reasons']),x.get('error',999),x['id']));provisional.append(dict(best,alternatives=[x['id'] for x in rows],candidate_group=list(key)))
    # Remaining cached supports: distinct unresolved native candidates shown in
    # the viewer, with ownership/duplicate screening separated from absence.
    unrepresented=[];seen=[]
    for p in sorted(r['remaining_candidates'],key=lambda p:(p.get('error',999),p['id'])):
        if p['id'] in engine.co or not p.get('native') or p['native']['pixel_count']<25:continue
        near,idx=engine.alltree.query(p['xy'])
        if near<13:continue
        if any(np.linalg.norm(np.array(p['xy'])-xy)<12 for xy in seen):continue
        if any(np.linalg.norm(np.array(p['xy'])-np.array(x['xy']))<12 for x in provisional):continue
        seen.append(np.array(p['xy']));unrepresented.append(p)
    predictions=[]
    for cell in engine.empty_sites():
        ns=engine.neighbors(cell);point=np.mean([engine.obs[o]['xy'] for o,d in ns],axis=0);model=engine.model(point)
        if not model:continue
        target=np.array(cell);target-=round(float((target-model['root'])@engine.H/(engine.H@engine.H)))*engine.H;pred=engine.predict(model,target)
        if np.any(pred<10) or pred[0]>2530 or pred[1]>3172 or engine.alltree.query(pred)[0]<14:continue
        if any(np.linalg.norm(pred-np.array(p['xy']))<13 for p in provisional):continue
        key=representative(target,H);ev=engine.evidence(pred);predictions.append(dict(id=f'PRED-{key[0]}-{key[1]}',cell=target.tolist(),prediction=pred.tolist(),
            neighbor_ids=[o for o,d in ns],native_pixel_count=ev['pixel_count'],foreground_fraction=ev['foreground_fraction'],status='purely predicted unverified site',
            reason='geometry predicts a vacancy, but no separate native observation is accepted; may be occluded or misprojected'))
    edge_candidates=[]
    for a,ab in engine.co.items():
        for d in STEPS:
            z=engine.occupied.get(representative(np.array(ab)+d,H))
            if not z or edgekey(a,z) in engine.links:continue
            ck=engine.link_check(a,engine.obs[a]['xy'],z,engine.obs[z]['xy']);edge_candidates.append(dict(source=a,target=z,delta_ab=d,family=FAMILY[d],
                status='native supported but not accepted' if ck['allowed'] else 'blocked or ambiguous',**ck))
    added=[e for e in engine.links.values() if e['origin']=='R332'];newids={x['id'] for x in accepted if not x['known']};knownids={x['id'] for x in accepted if x['known']}
    # A fresh native extraction can rediscover an older detector location. Count
    # that as cache recovery, not a wholly new photographic detection.
    pool=read(run/'candidate-pool.json.gz');novelty(accepted,pool)
    counts=dict(baseline_recorded=len(g['observations']),recorded_accepted=len(engine.obs),indexed=len(engine.co),
        newly_indexed_known=len(knownids),new_observations=len(newids),new_colors=dict(Counter(engine.obs[o]['color'] for o in newids)),
        newly_associated_cached=sum(not x['known'] and not x.get('genuine_new_native_extraction',False) for x in accepted),
        newly_measured_native=sum(x.get('genuine_new_native_extraction',False) for x in accepted),
        fresh_native_colors=dict(Counter(x['color'] for x in accepted if x.get('genuine_new_native_extraction',False))),
        native_body_black_without_highlight_gate=sum(x['body_only'] and x['color']=='black' for x in accepted),
        baseline_indexed_colors=dict(Counter(engine.obs[o]['color'] for o in base)),indexed_colors=dict(Counter(engine.obs[o]['color'] for o in engine.co)),
        links=len(engine.links),families=dict(Counter(e['family'] for e in engine.links.values())),unindexed=len(engine.obs)-len(engine.co),
        remaining_original_unindexed=len(baseline_ids-engine.co.keys()),provisional=len(provisional),
        additional_provisional_groups=sum(p['id'] not in engine.obs for p in provisional),known_unindexed_provisional_groups=sum(p['id'] in engine.obs for p in provisional),
        provisional_colors=dict(Counter(p['color'] for p in provisional)),
        unresolved_native_candidate_groups=len(unrepresented),pure_predictions=len(predictions),unresolved_links=len(edge_candidates),
        new_links_total=len(added),new_links_existing=sum(e['source'] in baseline_ids and e['target'] in baseline_ids for e in added),
        new_links_new_observations=sum(e['source'] in newids or e['target'] in newids for e in added),
        rejected_alias_proposals=len(alias),withdrawn_new_links=len(withdrawn),retracted_assignments=len(retracted))
    result=dict(r,observations=list(engine.obs.values()),coordinates=[dict(id=o,ab=v) for o,v in sorted(engine.co.items())],edges=list(engine.links.values()),
        accepted_additions=accepted,provisional_observations=provisional,unrepresented_candidates=unrepresented,predictions=predictions,
        link_candidates=edge_candidates,coordinate_only_edges=[dict(e,status='coordinate relation only') for e in edge_candidates],summary=counts,
        final_integrity=dict(withdrawn_edges=withdrawn,retracted_assignments=retracted,alias_candidates=alias,seconds=time.perf_counter()-start),
        feedback_scope='User positive R331 review applies to displayed labels/links only. No existing assignment was corrected or globally certified.')
    save(out/'graph.json.gz',result);save(out/'summary.json',counts);save(out/'omissions.json.gz',dict(original_unindexed=[engine.obs[o] for o in sorted(baseline_ids-engine.co.keys())],
        coordinate_neighbors_without_accepted_link=edge_candidates,provisional_native_candidates=provisional,unrepresented_native_candidates=unrepresented,
        pure_predictions=predictions,duplicate_or_association_candidates=alias,
        final_withdrawals=withdrawn,policy='Candidates are not counts of physical missing beads. Pure predictions have no measured observation location.'))
    save(out/'provenance.json',dict(source_run=str(run),source_graph_sha256=sha(run/'graph.json.gz'),seconds=time.perf_counter()-start));print('FINAL INTEGRITY',counts,flush=True)

if __name__=='__main__':main()
