"""After-seal counterfactuals/ablations and retrospective evaluation."""
import copy,time
from collections import defaultdict,Counter
import numpy as np
from PIL import Image,ImageOps
from photo2.r325.tracker import preprocess
from photo2.r325.global_solver import solve,objective
from .compatibility import compatible_subset
from photo2.r325.graph import infer_graph
from photo2.r326.runner import key
from .continue_run import graph_for
from photo2.r326.evaluate import reference_audit
from .select_working import working_objective
from .runner import ROOT,OUT,OLD,read,save

def metrics(g,sels):
    vals=defaultdict(list)
    for wi,ss in enumerate(sels):
        for hi in ss:
            for r in g['windows'][wi]['hypotheses'][hi]['r327_evidence']['rows']:
                vals[r['observation']].append([np.mean(r['errors_px']),r['pixel_support'],r['utility']])
    return {o:np.median(v,axis=0).tolist() for o,v in vals.items()}

def main():
    started=time.perf_counter();g=read(OUT/'graph.json.gz');ws=g['windows'];obs=g['observations'];data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));base={key(e) for e in g['graph']['edges']};original=[[h['score'] for h in w['hypotheses']] for w in ws];controls=[]
    for mode in ['discovery_only','without_native_pixel','without_sequence']:
        t=time.perf_counter()
        for w in ws:
            for h in w['hypotheses']:
                e=h['r327_evidence']
                if mode=='discovery_only':h['score']=h['photo_score']
                elif mode=='without_native_pixel':h['score']-=.25*sum(r['pixel_support'] for r in e['rows'])
                else:h['score']-=.35*e['sequence']
        sol=solve(ws);doc=graph_for(g,ws,obs,data,sol);edges={key(e) for e in doc['graph']['edges']}
        controls.append(dict(mode=mode,seconds=time.perf_counter()-t,selected_window_states=doc['selected_window_states'],added_vs_primary=[list(k) for k in sorted(edges-base)],removed_vs_primary=[list(k) for k in sorted(base-edges)],compatibility=doc['compatibility']))
        for w,ss in zip(ws,original):
            for h,s in zip(w['hypotheses'],ss):h['score']=s
    save(OUT/'ablations.json.gz',controls)
    pairs=read(ROOT/'photo2/r326/results/closure-investigation.json')['old_four_pairs'];proposals={}
    for wi in range(65,94):
        w=ws[wi]
        for hi,h in enumerate(w['hypotheses']):
            rel=[]
            for p in pairs:
                a,b=p['source'],p['target'];aa=h['assignments']
                if a in aa and b in aa:rel.append((a,b,*(np.array(aa[b]['ab'])-aa[a]['ab'])))
            if not rel or hi in g['selected_window_states'][wi]:continue
            sig=tuple(rel);gap=g['global_solution']['max_marginal_gaps'][wi][hi]
            if sig not in proposals or gap<proposals[sig]['gap']:proposals[sig]=dict(window=wi,hypothesis=hi,gap=gap,relations=rel)
    candidates=sorted(proposals.values(),key=lambda p:p['gap'])[:8];alternatives=[];pm=metrics(g,g['selected_window_states'])
    for p in candidates:
        t=time.perf_counter();wi,hi=p['window'],p['hypothesis']
        for k,h in enumerate(ws[wi]['hypotheses']):
            if k!=hi:h['score']-=1e6
        sol=solve(ws)
        for w,ss in zip(ws,original):
            for h,s in zip(w['hypotheses'],ss):h['score']=s
        actual=objective(ws,sol['choices']);assert sol['choices'][wi]==hi
        h=ws[wi]['hypotheses'][hi];s=h['photo_score'];h['photo_score']=1e8;sels,audit=compatible_subset(ws,sol,g['stations_px'],g['period_px']);h['photo_score']=s;assert sels[wi]==[hi]
        nodes,graph,tracks,_=infer_graph(obs,ws,sels,data,g['stations_px'],g['period_px']);assert not graph['conflicts'];am=metrics(g,sels);common=sorted(pm.keys()&am.keys());changes=[]
        for o in common:
            if np.max(np.abs(np.array(pm[o])-am[o]))>.01:changes.append(dict(observation=o,primary_error_pixel_utility=pm[o],alternative_error_pixel_utility=am[o]))
        changes.sort(key=lambda r:-abs(r['alternative_error_pixel_utility'][0]-r['primary_error_pixel_utility'][0]));edges={key(e) for e in graph['edges']};hol=audit['cycle_audit']['possible_holonomies']
        alternatives.append(dict(working_objective=working_objective(ws,sels),primary_working_objective=working_objective(ws,g['selected_window_states']),request=p,seconds=time.perf_counter()-t,unforced_cyclic_score=actual,cyclic_gap=g['global_solution']['score']-actual,selected_window_states=sels,compatibility=audit,graph=graph,photographic_consequences=changes,common_supports=len(common),mean_error_primary=float(np.mean([pm[o][0] for o in common])),mean_error_alternative=float(np.mean([am[o][0] for o in common])),added_links=[list(k) for k in sorted(edges-base)],withdrawn_links=[list(k) for k in sorted(base-edges)],conditional_counts=[dict(H=h,A=7*h[0]+6*h[1],B=6*h[0]+7*h[1]) for h in hol]))
        print('ALTERNATIVE',p,'H',hol,'changed supports',len(changes),flush=True)
    save(OUT/'lower-bend-alternatives.json.gz',dict(primary_holonomies=g['compatibility']['cycle_audit']['possible_holonomies'],old_four_pairs=pairs,alternatives=alternatives,policy='Forced states are diagnostic reversible alternatives. Scores exclude forcing. Whole-window abstentions explicit. Photographic differences are conditional prediction errors, not independent labels. Counts never enter selection.'))
    reference=reference_audit(g);save(OUT/'reference.json',reference)
    # This is the actual independent historical label subset, not the old strict mask.
    links=[dict(source=r['automatic_source'],target=r['automatic_target'],direction=r['direction'],priority=r['priority'],maker_source=r['source'],maker_target=r['target']) for r in reference['links'] if r['recovered']]
    save(OUT/'established-subset.json',dict(links=[e for e in links if e['priority']=='interior'],edge_reference_links=[e for e in links if e['priority']!='interior'],reference='Historical R161 independently recorded links; associations conditional on fixed radius18/margin3',summary=reference['summary'],new_independently_established_links=0,policy='Independent reference support is distinct from algorithmic agreement. Prior development has seen this reference; this is not a new blind holdout. The R326 strict17 mask is not promoted to ground truth.'))
    save(OUT/'analysis-performance.json',dict(seconds=time.perf_counter()-started,alternatives=len(alternatives),reference_summary=reference['summary']))
    print('REFERENCE',reference['summary'],flush=True)
if __name__=='__main__':main()
