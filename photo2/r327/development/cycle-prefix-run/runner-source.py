"""Budgeted adaptive inference using only archived image candidates and native RGB."""
import argparse,copy,gzip,json,time,hashlib,resource
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r325.tracker import preprocess
from photo2.r325.global_solver import solve
from photo2.r326.runner import graph_for,key
from photo2.r326.contexts import measure,augment_contexts
from photo2.r325.candidates import signature
from .evidence import maps,score_bank
ROOT=Path(__file__).resolve().parents[2];OLD=ROOT/'photo2/r326/results/full';OUT=ROOT/'photo2/r327/results'
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.gz':
        with gzip.open(p,'wt') as f:json.dump(d,f,separators=(',',':'),allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist())
    else:p.write_text(json.dumps(d,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist())+'\n')
def read(p):
    p=Path(p)
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return json.load(f)
def snapshot(doc,sol):
    return dict(selected_window_states=doc['selected_window_states'],compatibility=doc['compatibility'],graph=doc['graph'],global_solution=sol)
def change_ledger(before,after,windows):
    b={key(e):e for e in before['graph']['edges']};a={key(e):e for e in after['graph']['edges']};records=[]
    for action,keys in [('added',a.keys()-b.keys()),('withdrawn',b.keys()-a.keys())]:
        for k in sorted(keys):
            old=[];new=[]
            for dest,doc in [(old,before),(new,after)]:
                for wi,sels in enumerate(doc['selected_window_states']):
                    for hi in sels:
                        h=windows[wi]['hypotheses'][hi];aa=h['assignments']
                        if k[0] not in aa or k[1] not in aa:continue
                        rows=[r for r in h.get('r327_evidence',{}).get('rows',[]) if r['observation'] in k[:2]]
                        dest.append(dict(window=wi,hypothesis=hi,delta_ab=(np.array(aa[k[1]]['ab'])-aa[k[0]]['ab']).tolist(),target_predictions=rows))
            alternatives=[e for e in after['graph']['edges']+after['graph']['unresolved_edges'] if {e['source'],e['target']}==set(k[:2])]
            records.append(dict(action=action,edge=list(k),previous_witnesses=old,current_witnesses=new,current_pair_records=alternatives,reason='joint photographic objective and whole-hypothesis compatibility; inspect prediction rows for pixel evidence',established_photographic_contradiction=False,rollback_available=True))
    return records

def run(output=OUT,budget=600.,practice=False):
    start=time.perf_counter();out=Path(output);out.mkdir(parents=True,exist_ok=True)
    g=read(OLD/'graph.json');ws=g['windows'];obs=g['observations'];old=copy.deepcopy(snapshot(g,g['global_solution']))
    if practice:
        ws=ws[65:94];g['windows']=ws;ids={o for w in ws for o in w['observation_ids']};obs=[o for o in obs if o['id'] in ids];g['observations']=obs
        old['selected_window_states']=old['selected_window_states'][65:94];old['graph']['edges']=[e for e in old['graph']['edges'] if e['source'] in ids and e['target'] in ids]
    op={o['id']:o for o in obs};data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));fields=maps(data['rgb']);cache={};fit_cache={}
    nold=[len(w['hypotheses']) for w in ws];score_bank(ws,op,fields,cache);sol=solve(ws,cyclic=not practice);doc=graph_for(g,ws,obs,data,sol)
    initial=change_ledger(old,doc,ws);save(out/'initial-changes.json.gz',initial);save(out/'iteration-0.json.gz',snapshot(doc,sol))
    history=[dict(iteration=0,elapsed=time.perf_counter()-start,links=len(doc['graph']['edges']),indexed=sum(n['component'] is not None for n in doc['intersections']),changes=len(initial),holonomies=doc['compatibility']['cycle_audit']['possible_holonomies'])]
    contexts=[];seen=set();stable=0;last_seconds=0.;stop='emergency pass bound';pending=[]
    # New shifted and larger contexts; archived fits are not extra votes.
    specs=[(240,18.),(240,-18.),(280,18.),(280,-18.),(320,0.)]
    for iteration in range(1,21):
        elapsed=time.perf_counter()-start
        if elapsed+max(15.,1.3*last_seconds)>budget:stop='measured refinement budget; choices/candidates may remain unsettled';break
        t=time.perf_counter();priority=[]
        for wi,w in enumerate(ws):
            sels=doc['selected_window_states'][wi]
            uncertainty=10. if not sels else sum(1-r['utility'] for r in w['hypotheses'][sels[0]]['r327_evidence']['rows'])
            # Prioritize named photographic questions geometrically, never by labels.
            center=np.array(w['center']);focus=any(np.linalg.norm(center-c)<200 for c in ([1660,285],[1750,1625],[1485,3010],[290,1410]))
            for si,(size,shift) in enumerate(specs):
                if (w['id'],size,shift) not in seen:priority.append((-(uncertainty+4*focus)/(1+si),wi,size,shift));break
        priority.sort();pending=priority;batch=priority[:12]
        affected=set()
        for _,wi,size,shift in batch:
            c=measure(ws[wi],obs,data,size,shift,seed=327);contexts.append(c);seen.add((ws[wi]['id'],size,shift));affected.update(j for j in range(max(0,wi-2),min(len(ws),wi+3)))
        # Transport archived R326 contexts as well as new larger/shifted evidence.
        if iteration==1:
            inherited=read(OLD/'contexts.json');ids={w['id'] for w in ws};contexts=[c for c in inherited if c['parent'] in ids]+contexts
        additions=augment_contexts(ws,contexts,obs,affected,max_add=2,fit_cache=fit_cache)
        fresh=score_bank(ws,op,fields,cache);newsol=solve(ws,cyclic=not practice);newdoc=graph_for(g,ws,obs,data,newsol)
        changes=change_ledger(doc,newdoc,ws);choice_changes=sum(a!=b for a,b in zip(doc['selected_window_states'],newdoc['selected_window_states']));stable=stable+1 if not choice_changes else 0
        save(out/f'changes-{iteration}.json.gz',changes);save(out/f'iteration-{iteration}.json.gz',snapshot(newdoc,newsol))
        last_seconds=time.perf_counter()-t
        history.append(dict(iteration=iteration,seconds=last_seconds,elapsed=time.perf_counter()-start,new_contexts=len(batch),new_hypotheses=sum(a['added'] for a in additions),new_evidence_records=fresh,changed_windows=choice_changes,added_links=sum(r['action']=='added' for r in changes),withdrawn_links=sum(r['action']=='withdrawn' for r in changes),links=len(newdoc['graph']['edges']),indexed=sum(n['component'] is not None for n in newdoc['intersections']),components=len(newdoc['graph']['components']),holonomies=newdoc['compatibility']['cycle_audit']['possible_holonomies'],candidate_generation=additions))
        doc,sol=newdoc,newsol;save(out/'iterations.json',history);print(json.dumps({k:v for k,v in history[-1].items() if k!='candidate_generation'}),flush=True)
        if stable>=2 and not batch and not history[-1]['new_hypotheses']:stop='two stable passes after finite proposal exhaustion';break
    doc.update(windows=ws,observations=obs,global_solution=sol,stations_px=g['stations_px'],period_px=g['period_px'],image_sha256=g['image_sha256'],schema='r327-reversible-working-v1',iterations=history,stop_reason=stop,original_hypothesis_counts=nold,configuration=dict(budget_seconds=budget,cached_start=str(OLD.relative_to(ROOT)),practice=practice,photo_discovery_weight=.35,sequence_weight=.35,context_disagreement_penalty=0.,context_specs=specs),pending_contexts=len(pending),working_only=True)
    save(out/'graph.json.gz',doc);save(out/'contexts.json.gz',contexts);save(out/'final-changes.json.gz',change_ledger(old,doc,ws));save(out/'performance.json',dict(refinement_seconds=time.perf_counter()-start,budget_seconds=budget,stop_reason=stop,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,old_hypotheses=sum(nold),final_hypotheses=sum(len(w['hypotheses']) for w in ws)))
    seal={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'photo2/r327').glob('*.py'))};seal['graph_sha256']=hashlib.sha256((out/'graph.json.gz').read_bytes()).hexdigest();save(out/'scientific-seal.json',seal)
    print('FINAL',history[-1],'stop',stop,flush=True);return doc
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=OUT);p.add_argument('--budget',type=float,default=600.);p.add_argument('--practice',action='store_true');a=p.parse_args();run(a.output,a.budget,a.practice)
