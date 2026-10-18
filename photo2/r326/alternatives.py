"""Explicit counterfactual complete-path witnesses; primary inference unchanged.
Anchor-conditioned paths do not cover marginal alternatives at other positions.
Force a selected marginal state, recover its exact cyclic full-path witness, then
retain a compatible whole-hypothesis subset that includes the forced state.
"""
import json,copy,time
from pathlib import Path
from collections import Counter
import numpy as np
from photo2.r325.global_solver import solve,objective,overlap
from photo2.r325.graph import infer_graph
from photo2.r325.tracker import preprocess
from photo2.r326.compatibility import compatible_subset
from photo2.r326.runner import key
from photo2.r323.tracker import save
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def main():
    start=time.perf_counter();g=json.load(open(OUT/'full/graph.json'));ws=g['windows'];sol=g['global_solution'];proposals=[]
    for i,w in enumerate(ws):
        best=sol['choices'][i]
        for h in sol['selected'][i]:
            if h==best:continue
            _,shift,common,agree=overlap(w['hypotheses'][best],w['hypotheses'][h]);proposals.append(dict(window=i,hypothesis=h,disagree=common-agree,gap=sol['max_marginal_gaps'][i][h]))
    selected=[]
    for p in sorted(proposals,key=lambda p:(-p['disagree'],p['gap'],p['window'],p['hypothesis'])):
        if any(abs(p['window']-x['window'])<5 for x in selected):continue
        selected.append(p)
        if len(selected)>=8:break
    data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));witnesses=[]
    for p in selected:
        wi,hi=p['window'],p['hypothesis'];scores=[h['score'] for h in ws[wi]['hypotheses']]
        for k,h in enumerate(ws[wi]['hypotheses']):
            if k!=hi:h['score']-=1000000
        alt=solve(ws)
        for h,s in zip(ws[wi]['hypotheses'],scores):h['score']=s
        assert alt['choices'][wi]==hi;actual=objective(ws,alt['choices']);gap=sol['score']-actual;assert abs(gap-p['gap'])<1e-7
        # Force retention only in the whole-window subset selection. This changes
        # the subset feasibility witness, never the primary or cyclic objective.
        h=ws[wi]['hypotheses'][hi];photo=h['photo_score'];h['photo_score']=100000000.
        sels,audit=compatible_subset(ws,alt,g['stations_px'],g['period_px']);h['photo_score']=photo
        assert sels[wi]==[hi]
        _,graph,_,_=infer_graph(g['observations'],ws,sels,data,g['stations_px'],g['period_px']);assert not graph['conflicts']
        witnesses.append(dict(request=p,cyclic_objective=actual,cyclic_gap=gap,choices=alt['choices'],selected_window_states=sels,compatibility=audit,edges=[list(key(e)) for e in graph['edges']],policy='A globally compatible partial whole-hypothesis configuration extending a near-optimal complete cyclic path, with explicit window abstentions. Not independent photographic truth.'))
    primary={key(e) for e in g['graph']['edges']};altkeys={tuple(k) for w in witnesses for k in w['edges']};marginal=g['support_classes']['marginal_only_unwitnessed'];unwitnessed=[e for e in marginal if key(e) not in altkeys]
    report=dict(witnesses=witnesses,primary_edges=len(primary),compatible_alternative_only=[list(k) for k in sorted(altkeys-primary)],marginal_only_unwitnessed=unwitnessed,covered_previous_marginal_only=len(marginal)-len(unwitnessed),seconds=time.perf_counter()-start,policy='Witness sampling, not enumeration of every global alternative. Unwitnessed does not mean impossible. Primary selections and all reported evaluation results unchanged.')
    save(OUT/'alternatives.json',report)
    model=json.load(open(OUT/'full/model-input.json'));model['alternative_assignments']=report;model['confidence']={o['id']:dict(native_support='observed native pixels; distinct body provisional' if o.get('provisional') else 'original independently measured support',lattice='strict context-screened conditional component relation' if o['component'] is not None else 'unresolved for fixed model use',calibrated_probability=None) for o in model['observations']};model['neighbor_interpretations']=dict(F0=dict(A=7,B=6),F1=dict(A=6,B=7),difference=dict(A=1,B=-1),reversal='negate every increment');model['global_winding_certified']=False;model['total_bead_count']=None;model['provenance_note']='Strict constraints copied exactly from frozen full/model-input.json; bounded full-path witnesses added afterward without changing primary inference.';save(OUT/'model-input.json',model)
    print(dict(witnesses=len(witnesses),alternate_edges=len(altkeys-primary),marginal_unwitnessed=len(unwitnessed),seconds=report['seconds']))
if __name__=='__main__':main()
