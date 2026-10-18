"""Continue the preserved diagnostic bank with minimal cycle witnesses."""
import time,hashlib,resource,argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r325.tracker import preprocess
from photo2.r325.global_solver import solve
from photo2.r325.graph import infer_graph
from photo2.r326.contexts import measure,augment_contexts
from photo2.r325.candidates import signature
from .compatibility import reconsider
from .evidence import maps,score_bank
from .runner import ROOT,OUT,OLD,read,save,snapshot,change_ledger
PILOT=ROOT/'photo2/r327/development/cycle-prefix-run'
def graph_for(g,ws,obs,data,sol):
    sels,audit=reconsider(ws,sol,g['stations_px'],g['period_px']);nodes,graph,tracks,_=infer_graph(obs,ws,sels,data,g['stations_px'],g['period_px']);assert not graph['conflicts']
    return dict(intersections=nodes,graph=graph,tracks=tracks,selected_window_states=sels,compatibility=audit)
def main(output=OUT,pilot=PILOT,total_budget=600.):
    OUT=Path(output);PILOT=Path(pilot);OUT.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();g=read(PILOT/'graph.json.gz');prior=read(PILOT/'performance.json');budget=max(0.,total_budget-prior['refinement_seconds']);ws=g['windows'];obs=g['observations'];op={o['id']:o for o in obs};data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));fields=maps(data['rgb']);cache={signature(h):h['r327_evidence'] for w in ws for h in w['hypotheses']};fit_cache={};contexts=read(PILOT/'contexts.json.gz');seen={(c['parent'],c['size'],c['shift']) for c in contexts};specs=g['configuration']['context_specs'];history=g['iterations'];old=read(OLD/'graph.json');score_bank(ws,op,fields,cache);sol=solve(ws);doc=graph_for(g,ws,obs,data,sol)
    i=history[-1]['iteration']+1;history.append(dict(iteration=i,stage='minimal cycle witness correction on same bank',seconds=time.perf_counter()-start,elapsed=prior['refinement_seconds']+time.perf_counter()-start,links=len(doc['graph']['edges']),indexed=sum(n['component'] is not None for n in doc['intersections']),components=len(doc['graph']['components']),changed_windows=sum(a!=b for a,b in zip(doc['selected_window_states'],g['selected_window_states'])),holonomies=doc['compatibility']['cycle_audit']['possible_holonomies']))
    save(OUT/f'iteration-{i}.json.gz',snapshot(doc,sol));save(OUT/f'changes-{i}.json.gz',change_ledger(g,doc,ws));last=time.perf_counter()-start;stable=0;pending=[];stop='measured cumulative 600-second refinement budget'
    for iteration in range(i+1,101):
        if time.perf_counter()-start+max(20.,1.3*last)>budget:break
        t=time.perf_counter();priority=[]
        for wi,w in enumerate(ws):
            sels=doc['selected_window_states'][wi];uncertainty=10. if not sels else sum(1-r['utility'] for r in w['hypotheses'][sels[0]]['r327_evidence']['rows']);center=np.array(w['center']);focus=any(np.linalg.norm(center-c)<200 for c in ([1660,285],[1750,1625],[1485,3010],[290,1410]))
            for si,(size,shift) in enumerate(specs):
                if (w['id'],size,shift) not in seen:priority.append((-(uncertainty+4*focus)/(1+si),wi,size,shift));break
        priority.sort();pending=priority;batch=priority[:12];affected=set()
        for _,wi,size,shift in batch:
            contexts.append(measure(ws[wi],obs,data,size,shift,seed=327));seen.add((ws[wi]['id'],size,shift));affected.update(j for j in range(max(0,wi-2),min(len(ws),wi+3)))
        adds=augment_contexts(ws,contexts,obs,affected,max_add=2,fit_cache=fit_cache);fresh=score_bank(ws,op,fields,cache);ss=solve(ws);dd=graph_for(g,ws,obs,data,ss);changes=change_ledger(doc,dd,ws);changed=sum(a!=b for a,b in zip(doc['selected_window_states'],dd['selected_window_states']));stable=stable+1 if not changed else 0;save(OUT/f'changes-{iteration}.json.gz',changes);save(OUT/f'iteration-{iteration}.json.gz',snapshot(dd,ss));last=time.perf_counter()-t
        row=dict(iteration=iteration,seconds=last,elapsed=prior['refinement_seconds']+time.perf_counter()-start,new_contexts=len(batch),new_hypotheses=sum(a['added'] for a in adds),new_evidence_records=fresh,changed_windows=changed,added_links=sum(r['action']=='added' for r in changes),withdrawn_links=sum(r['action']=='withdrawn' for r in changes),links=len(dd['graph']['edges']),indexed=sum(n['component'] is not None for n in dd['intersections']),components=len(dd['graph']['components']),holonomies=dd['compatibility']['cycle_audit']['possible_holonomies']);history.append(row);save(OUT/'iterations.json',history);print(row,flush=True);doc,sol=dd,ss
        if stable>=2 and not batch and not row['new_hypotheses']:stop='two stable passes after finite proposal exhaustion';break
    doc.update(windows=ws,observations=obs,global_solution=sol,stations_px=g['stations_px'],period_px=g['period_px'],image_sha256=g['image_sha256'],schema='r327-reversible-working-v1',iterations=history,stop_reason=stop,original_hypothesis_counts=g['original_hypothesis_counts'],configuration=dict(g['configuration'],cycle_cut='minimal conflicting cycle rather than shared root path; 24-cut cap'),pending_contexts=len(pending),working_only=True)
    save(OUT/'graph.json.gz',doc);save(OUT/'contexts.json.gz',contexts);save(OUT/'final-changes.json.gz',change_ledger(old,doc,ws));save(OUT/'performance.json',dict(refinement_seconds=prior['refinement_seconds']+time.perf_counter()-start,initial_diagnostic_seconds=prior['refinement_seconds'],continuation_seconds=time.perf_counter()-start,budget_seconds=total_budget,stop_reason=stop,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,old_hypotheses=sum(g['original_hypothesis_counts']),final_hypotheses=sum(len(w['hypotheses']) for w in ws),pending_contexts=len(pending)))
    seal={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'photo2/r327').glob('*.py'))};seal['graph_sha256']=hashlib.sha256((OUT/'graph.json.gz').read_bytes()).hexdigest();save(OUT/'scientific-seal.json',seal);print('FINAL',history[-1],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=OUT);p.add_argument('--pilot',default=PILOT);p.add_argument('--total-budget',type=float,default=600.);a=p.parse_args();main(a.output,a.pilot,a.total_budget)
