"""Retain the strongest sampled compatible configuration under one fixed objective.
The cyclic-regret decomposition proposes configurations. It must not cause a
reversible incumbent to be discarded merely because an expanded bank changes its
regret weights. This final comparison has no label, count or pattern inputs.
"""
import time,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r325.global_solver import overlap
from photo2.r325.graph import infer_graph
from photo2.r325.tracker import preprocess
from .compatibility import relations,cycle_audit
from .runner import ROOT,OUT,OLD,read,save,change_ledger
PILOT=ROOT/'photo2/r327/development/cycle-prefix-run'
def working_objective(ws,sels):
    hs=[w['hypotheses'][s[0]] if s else dict(score=0.,assignments={}) for w,s in zip(ws,sels)];n=len(hs);unary=sum(h['score'] for h in hs);pairs=0.;triples=0.
    for i in range(n):
        x=overlap(hs[i],hs[(i+1)%n]);z=overlap(hs[i],hs[(i+2)%n]);y=overlap(hs[(i+1)%n],hs[(i+2)%n]);pairs+=x[0]+z[0]
        if all(v[1] is not None for v in (x,y,z)):triples-=2.5*min(sum(abs(x[1][q]+y[1][q]-z[1][q]) for q in (0,1)),4)
    return dict(total=unary+pairs+triples,photo_unaries=unary,overlap_pairs=pairs,translation_triples=triples)
def main():
    start=time.perf_counter();g=read(OUT/'graph.json.gz');ws=g['windows'];old=read(OLD/'graph.json');archive=ROOT/'photo2/r327/development/continuation-final';archive.mkdir(parents=True,exist_ok=True)
    for name in ['graph.json.gz','scientific-seal.json','performance.json']:shutil.copy2(OUT/name,archive/name)
    states=[('R326',old['selected_window_states'])]
    for folder in (PILOT,OUT):
        for p in sorted(folder.glob('iteration-*.json.gz'),key=lambda p:int(p.name.split('-')[1].split('.')[0])):states.append((str(p.relative_to(ROOT)),read(p)['selected_window_states']))
    records=[];best=None
    for label,sels in states:
        choices=[s[0] if s else None for s in sels];active,conflicts,ll=relations(ws,choices,g['stations_px'],g['period_px']);bad,audit=cycle_audit(set(active),ll);assert not conflicts and not bad
        score=working_objective(ws,sels);records.append(dict(configuration=label,score=score,selected_windows=len(active),holonomies=audit['possible_holonomies']))
        if best is None or score['total']>best[0]+1e-9:best=(score['total'],label,sels,audit)
    _,label,sels,audit=best;data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));nodes,graph,tracks,_=infer_graph(g['observations'],ws,sels,data,g['stations_px'],g['period_px']);assert not graph['conflicts']
    for n in nodes:n['status']='working indexed support' if n['component'] is not None else 'unindexed observed support'
    for e in graph['edges']:e['status']='working provisional link';e['independently_established']=False
    before=g.copy();g.update(intersections=nodes,graph=graph,tracks=tracks,selected_window_states=sels,compatibility=dict(selected_windows=[i for i,s in enumerate(sels) if s],abstained_windows=[i for i,s in enumerate(sels) if not s],cycle_audit=audit,policy='Best explicitly sampled compatible configuration under fixed unnormalized photographic+cyclic-factor objective; no exact full-bank optimum claim'),incumbent_selection=dict(source=label,objective=working_objective(ws,sels),configurations_tested=len(records)))
    save(OUT/'working-selection.json',dict(selected=label,records=records,policy='Null window has zero unary and empty assignments. Scores use the same final bank, native unaries and R325 overlap/triple factors; no varying regret weights, graph connectivity reward or count prior. Every saved witness and original R326 compete. This is best among sampled configurations, not exhaustive MAP.'))
    save(OUT/'incumbent-changes.json.gz',change_ledger(before,g,ws));save(OUT/'graph.json.gz',g);save(OUT/'final-changes.json.gz',change_ledger(old,g,ws));perf=read(OUT/'performance.json');perf.update(incumbent_selection_seconds=time.perf_counter()-start,refinement_plus_incumbent_seconds=perf['refinement_seconds']+time.perf_counter()-start);save(OUT/'performance.json',perf)
    seal={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'photo2/r327').glob('*.py'))};seal['graph_sha256']=hashlib.sha256((OUT/'graph.json.gz').read_bytes()).hexdigest();save(OUT/'scientific-seal.json',seal);print('WORKING',label,working_objective(ws,sels),'links',len(graph['edges']),'H',audit['possible_holonomies'],flush=True)
if __name__=='__main__':main()
