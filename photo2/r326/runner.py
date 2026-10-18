"""Practice/full iterative global reconstruction, with no label/model data reads."""
import argparse,copy,json,time,resource
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy.spatial import cKDTree
from photo2.r325 import tracker as baseline
from photo2.r325.global_solver import solve,overlap
from photo2.r325.graph import infer_graph
from photo2.r325.candidates import inputs,refine,to_world,signature
from photo2.r323.tracker import save
from .contexts import measure,rescore,augment_contexts,edge_context
from .compatibility import compatible_subset,reconsider
from .black import regions_and_provisionals
from .black_contexts import corroborate
ROOT=baseline.ROOT;OUT=ROOT/'photo2/r326/results'


def key(e):
    a,b=e['source'],e['target'];d=e['delta_ab'];return (a,b,*d) if a<b else (b,a,*[-x for x in d])


def graph_for(g,windows,obs,data,sol,reopt=True):
    selected,audit=(reconsider if reopt else compatible_subset)(windows,sol,g['stations_px'],g['period_px'])
    nodes,graph,tracks,_=infer_graph(obs,windows,selected,data,g['stations_px'],g['period_px'])
    # All accepted edges derive from this ONE compatible complete-state subset.
    assert not graph['conflicts']
    for e in graph['edges']:e['support_class']='selected compatible whole-hypothesis witness'
    return dict(intersections=nodes,graph=graph,tracks=tracks,selected_window_states=selected,compatibility=audit)


def summary(doc,obs,sol):
    return dict(observations=len(obs),provisional_observations=sum(o.get('provisional',False) for o in obs),hypotheses=sum(len(w['hypotheses']) for w in doc['windows']),indexed=sum(n['component'] is not None for n in doc['intersections']),indexed_black=sum(n['component'] is not None and n['color']=='black' for n in doc['intersections']),accepted_links=len(doc['graph']['edges']),unresolved_links=len(doc['graph']['unresolved_edges']),components=len(doc['graph']['components']),compatible_windows=len(doc['compatibility']['selected_windows']),abstained_windows=len(doc['compatibility']['abstained_windows']),closure_identified=doc['graph']['closure']['identified'])


def run(out=OUT,practice=False,cached=None,iterations=3):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);started=time.perf_counter();timings={}
    if cached:g=json.load(open(cached));timings['baseline_load']=time.perf_counter()-started
    else:g=baseline.run(out/'baseline');timings['fresh_R325_baseline_including_serialization']=time.perf_counter()-started
    black=json.load(open(Path(cached).parent/'colored-first.json' if cached else out/'baseline/colored-first.json'))
    pixels=json.load(open(Path(cached).parent/'observation-pixels.json' if cached else out/'baseline/observation-pixels.json'))
    g=copy.deepcopy(g)
    if practice:
        g['windows']=g['windows'][65:94];ids={o for w in g['windows'] for o in w['observation_ids']};g['observations']=[o for o in g['observations'] if o['id'] in ids];pixels=[p for p in pixels if p['id'] in ids]
        assert 100<=len(g['observations'])<=200
    windows=g['windows'];obs=g['observations'];cyclic=not practice
    t=time.perf_counter();data=baseline.preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));timings['refinement_preprocess']=time.perf_counter()-t
    baseline.base.CROP=(0,0,data['rgb'].shape[1],data['rgb'].shape[0]);baseline.joint.CROP=baseline.base.CROP
    sol=solve(windows,cyclic=cyclic);initial=graph_for(g,windows,obs,data,sol);initial['windows']=windows
    history=[dict(iteration=0,summary=summary(initial,obs,sol),global_solution=sol,compatibility=initial['compatibility'],changed_choices=[],new_contexts=0,candidate_additions=0,seconds=sol['seconds']+initial['compatibility']['seconds'])]
    save(out/'iteration-0.json',dict(**initial,global_solution=sol,observations=obs))
    doc=initial;contexts=[];cache=set();fit_cache={};previous=sol['choices'];stopped='bounded refinement iteration budget';black_report=None;provisional=[];evidence={}
    for iteration in range(1,iterations+1):
        epoch=time.perf_counter();stages={};t=time.perf_counter()
        affected=set(doc['compatibility']['abstained_windows'])
        for c in doc['compatibility'].get('pair_conflicts',[]):affected.update(c['windows'])
        affected.update(c['window'] for c in doc['compatibility'].get('changed_from_cyclic',[]))
        for i,ss in enumerate(sol['selected']):
            if len(ss)>1:affected.add(i)
        # Regions with context contradiction remain eligible even after a solver switch.
        for i,w in enumerate(windows):
            if w['hypotheses'] and w['hypotheses'][sol['choices'][i]].get('context_penalty',0)>.8:affected.add(i)
        # Broad scheduled coverage outside known failures, without reading R325 labels.
        if iteration==1:affected.update(range(0,len(windows),8))
        if iteration==2:affected.update(range(4,len(windows),8))
        # Neighborhood expansion propagates changes beyond the initial problem site.
        core=set(affected)
        for i in core:affected.update(j for j in (i-1,i+1) if 0<=j<len(windows))
        new=[]
        for i in sorted(core):
            w=windows[i]
            specs=[(160,0.),(240,0.)] if iteration==1 else ([(280,0.),(160,18.)] if iteration==2 else [(160,-18.)])
            for size,shift in specs:
                k=(w['id'],size,shift)
                if k in cache:continue
                c=measure(w,obs,data,size,shift);contexts.append(c);new.append(c['id']);cache.add(k)
        stages['photographic_disagreement_measurement']=time.perf_counter()-t;t=time.perf_counter()
        if iteration==1 and not practice:
            enriched_black,colored_contexts=corroborate(black,contexts,obs)
            provisional,new_pixels,black_report=regions_and_provisionals(enriched_black,obs,data,windows)
            black_report['fresh_colored_only_context_predictions']=colored_contexts
            obs+=provisional;pixels+=new_pixels
            guide=np.array([[r['x'],r['y']] for r in json.load(open(out/'baseline/guide.json' if not cached else Path(cached).parent/'guide.json'))['samples']]);tree=cKDTree(guide)
            for o in provisional:g['stations_px'][o['id']]=float(tree.query(o['xy'])[1])*g['period_px']/len(guide)
            for i,w in enumerate(windows):
                for o in provisional:
                    if max(abs((np.array(o['xy'])-w['center'])@np.array(w['frame'])))<92:w['observation_ids'].append(o['id']);affected.add(i)
            # Existing no-addition candidates stay. New candidates must refit and
            # explicitly assign a native provisional support to a unique cell.
            op={o['id']:o for o in obs}
            for i in sorted(affected):
                w=windows[i]
                if not any(o in w['observation_ids'] for o in [p['id'] for p in provisional]):continue
                ids,xy,sig,wt=inputs(w,op);extra=[];seen={signature(h) for h in w['hypotheses']}
                for h in list(w['hypotheses']):
                    hh=refine(xy,sig,wt,np.array(h['basis_local']),np.array(h['offset_local']),ids)
                    if hh and any(o['id'] in hh['assignments'] for o in provisional):
                        hh=to_world(hh,w);s=signature(hh)
                        if s not in seen:hh['proposal_source']='provisional native reflection refit';extra.append(hh);seen.add(s)
                w['hypotheses']+=extra[:4]
        stages['new_black_evidence_and_refits']=time.perf_counter()-t;t=time.perf_counter()
        additions=augment_contexts(windows,contexts,obs,affected,max_add=4 if iteration<3 else 2,fit_cache=fit_cache)
        stages['selective_candidate_generation']=time.perf_counter()-t;t=time.perf_counter()
        scoreledger,evidence=rescore(windows,contexts)
        # Sparse longer-range messages from last compatible state configuration.
        # These frozen-neighbor penalties are a surrogate, not exact loopy MAP.
        old_selected=doc['selected_window_states'];longledger=[]
        for i,w in enumerate(windows):
            for hi,h in enumerate(w['hypotheses']):
                losses=[]
                for j,z in enumerate(windows):
                    if min(abs(i-j),len(windows)-abs(i-j))<=2 or not old_selected[j]:continue
                    k=z['hypotheses'][old_selected[j][0]];_,shift,common,agree=overlap(h,k)
                    if common>=4:losses.append((common-agree)/common)
                penalty=2.*float(np.mean(losses)) if losses else 0.
                h['longrange_penalty']=penalty;h['score']-=penalty
                if penalty:longledger.append(dict(window=w['id'],hypothesis=hi,penalty=penalty))
        stages['context_and_longrange_feedback']=time.perf_counter()-t;t=time.perf_counter()
        sol=solve(windows,cyclic=cyclic);stages['global_cyclic_optimization']=time.perf_counter()-t;t=time.perf_counter()
        revised=graph_for(g,windows,obs,data,sol);stages['compatible_graph_and_integer_audit']=time.perf_counter()-t
        revised['windows']=windows
        # Same-bank causal control: remove ONLY changed-context unary evidence.
        # Preserve candidate additions and long-range messages, then reselect.
        t=time.perf_counter();saved_scores=[[h['score'] for h in w['hypotheses']] for w in windows]
        for w in windows:
            for h in w['hypotheses']:h['score']+=h.get('context_penalty',0.)
        counter_sol=solve(windows,cyclic=cyclic);counter=graph_for(g,windows,obs,data,counter_sol)
        for w,scores in zip(windows,saved_scores):
            for h,score in zip(w['hypotheses'],scores):h['score']=score
        counter_keys={key(e) for e in counter['graph']['edges']};actual_keys={key(e) for e in revised['graph']['edges']}
        context_causal=dict(control='same expanded candidates and longrange messages; changed-context unary penalties set to zero',choices=counter_sol['choices'],selected_window_states=counter['selected_window_states'],edges_added_by_context=[list(k) for k in sorted(actual_keys-counter_keys)],edges_removed_by_context=[list(k) for k in sorted(counter_keys-actual_keys)])
        stages['same_bank_context_ablation']=time.perf_counter()-t
        for e in revised['graph']['edges']+revised['graph']['unresolved_edges']:e['photographic_context']=edge_context(e,evidence)
        before={key(e):e for e in doc['graph']['edges']};after={key(e):e for e in revised['graph']['edges']}
        changed=[dict(window=windows[i]['id'],previous=a,current=b) for i,(a,b) in enumerate(zip(previous,sol['choices'])) if a!=b]
        entry=dict(context_causal_control=context_causal,iteration=iteration,summary=summary(revised,obs,sol),global_solution=sol,compatibility=revised['compatibility'],changed_choices=changed,new_contexts=len(new),context_ids=new,candidate_additions=sum(a['added'] for a in additions),candidate_generation=additions,context_penalties=scoreledger,longrange_penalties=longledger,added_edges=[list(k) for k in sorted(after.keys()-before.keys())],removed_edges=[list(k) for k in sorted(before.keys()-after.keys())],stages_seconds=stages,seconds=time.perf_counter()-epoch)
        history.append(entry);doc=revised;previous=sol['choices'];save(out/f'iteration-{iteration}.json',dict(**doc,global_solution=sol,observations=obs));print('ITERATION',iteration,entry['summary'],'changed',len(changed),'new contexts',len(new),'seconds',round(entry['seconds'],3),flush=True)
        if not changed and not new and not entry['candidate_additions']:stopped='objective stable with no new proposals in requested finite context schedule; evidence may remain ambiguous';break
    # Provisional-evidence ablation: keep original observations/candidates and mask
    # every state assigning a provisional site; no-addition alternatives survive.
    if provisional:
        t=time.perf_counter();prov_ids={o['id'] for o in provisional};saved=[[h['score'] for h in w['hypotheses']] for w in windows]
        for w in windows:
            for h in w['hypotheses']:
                if prov_ids & h['assignments'].keys():h['score']-=1000000.
        without_sol=solve(windows,cyclic=cyclic);without=graph_for(g,windows,obs,data,without_sol)
        for w,scores in zip(windows,saved):
            for h,score in zip(w['hypotheses'],scores):h['score']=score
        before={key(e) for e in without['graph']['edges']};after={key(e) for e in doc['graph']['edges']}
        black_report['no_provisional_state_ablation']=dict(selected_window_states=without['selected_window_states'],edges_added=[list(k) for k in sorted(after-before)],edges_removed=[list(k) for k in sorted(before-after)],selected_provisional_observations=sorted({o for i,sel in enumerate(doc['selected_window_states']) for hi in sel for o in windows[i]['hypotheses'][hi]['assignments'] if o in prov_ids}),seconds=time.perf_counter()-t)
    # Explicit alternative complete configurations. No pooling into primary graph.
    t=time.perf_counter();alternative_witnesses=[];alternative_edges=set()
    for rank,path in enumerate(sol['anchor_conditioned_paths'][1:4]):
        if path['score']<sol['score']-sol['allowance']-1e-9:continue
        altsol=dict(sol,choices=path['choices']);alt=graph_for(g,windows,obs,data,altsol,reopt=False)
        es=[list(key(e)) for e in alt['graph']['edges']];alternative_edges.update(map(tuple,es));alternative_witnesses.append(dict(rank=rank+1,score=path['score'],choices=path['choices'],selected_window_states=alt['selected_window_states'],compatibility=alt['compatibility'],edges=es))
    primary={key(e) for e in doc['graph']['edges']}
    # Marginal-union legacy graph is diagnostic only, never default correspondences.
    _,mg,_,_=infer_graph(obs,windows,sol['selected'],data,g['stations_px'],g['period_px'])
    marginal_only=[e for e in mg['edges'] if key(e) not in primary|alternative_edges]
    support=dict(alternative_witnesses=alternative_witnesses,compatible_alternative_only=[list(k) for k in sorted(alternative_edges-primary)],marginal_only_unwitnessed=marginal_only,policy='An unwitnessed marginal link is not proved impossible. Alternatives have explicit whole-hypothesis abstentions and are never unioned into the primary graph.')
    timings['alternative_witnesses']=time.perf_counter()-t
    doc.update(schema='r326-iterative-photographic-v1',summary=summary(doc,obs,sol),observations=obs,global_solution=sol,stations_px=g['stations_px'],period_px=g['period_px'],closure=doc['graph']['closure'],image_sha256=g['image_sha256'],source_sha256=baseline.joint.sha(__file__),iterations=history,stop_reason=stopped,contexts=len(contexts),provenance='Original RGB, original R275 appearance supports, photographic geography; no R161, model, count or pattern runtime inputs',support_classes=support,configuration=dict(iterations=iterations,cyclic=cyclic,context_penalty_max=4,longrange_penalty_max=2,retention='all historical candidates preserved; selective additions',practice=practice))
    # Default model constraints exclude contradictory OR ambiguous contexts and
    # provisional distinct-body identities. Untested constraints remain labeled.
    safe=[e for e in doc['graph']['edges'] if e.get('photographic_context',{}).get('status') not in ['contested','ambiguous']]
    prov_ids={o['id'] for o in provisional};safe=[e for e in safe if not ({e['source'],e['target']}&prov_ids)]
    from photo2.r325.consistency import synchronize
    accepted,conflicts,coords,components,closure=synchronize(copy.deepcopy(safe),obs,g['stations_px'],g['period_px'])
    modelnodes=[]
    for o in obs:
        n=dict(o,pixels_xy=next(p['pixels_xy'] for p in pixels if p['id']==o['id']),component=None,relative_ab=None,conditional_indices=None)
        if o['id'] in coords:
            ci,ab=coords[o['id']];a,b=map(int,ab);n.update(component=ci,relative_ab=[a,b],conditional_indices=dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b))
        modelnodes.append(n)
    save(out/'model-input.json',dict(schema='r326-conservative-model-input-v1',observations=modelnodes,edges=accepted,unresolved_edges=doc['graph']['unresolved_edges']+[e for e in doc['graph']['edges'] if key(e) not in {key(x) for x in safe}],components=components,closure=closure,candidate_graph='graph.json',alternative_assignments=support,policy='Conditional photographic constraints, component-local gauges; untested links explicitly labeled. No certified global lattice or count. Provisional native sites do not become fixed model correspondences.'))
    timings['refinement_iterations']=sum(h['seconds'] for h in history[1:]);timings['total_before_serialization']=time.perf_counter()-started
    doc['timings_seconds']=timings;doc['peak_rss_mb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    save(out/'graph.json',doc);save(out/'contexts.json',contexts);save(out/'observation-pixels.json',pixels);save(out/'black-evidence.json',black_report or dict(practice=True,provisional_count=0));save(out/'iterations.json',history)
    save(out/'performance.json',dict(stages=timings,total_including_serialization=time.perf_counter()-started,peak_rss_mb=doc['peak_rss_mb'],cached_baseline=bool(cached),stop_reason=stopped))
    print('FINAL',doc['summary'],'seconds',time.perf_counter()-started,flush=True);return doc

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=OUT);ap.add_argument('--practice',action='store_true');ap.add_argument('--cached');ap.add_argument('--iterations',type=int,default=3);a=ap.parse_args();run(a.output,a.practice,a.cached,a.iterations)
