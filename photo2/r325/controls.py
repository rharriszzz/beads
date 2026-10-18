"""Origin changes, open-ring ablation and baseline-bank controls, no maker reads."""
import json,time,copy
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from photo2.r324 import fast_tracker as old
from .global_solver import solve
from .graph import infer_graph
OUT=Path(__file__).parent/'results'

def main():
    g=json.load(open(OUT/'graph.json'));ws=g['windows'];baseline=g['global_solution'];rows=[]
    for shift in [37,93,151]:
        sol=solve(ws[shift:]+ws[:shift]);sel=sol['selected'][-shift:]+sol['selected'][:-shift]
        gaps=sol['max_marginal_gaps'][-shift:]+sol['max_marginal_gaps'][:-shift]
        delta=max(float(np.max(abs(np.array(a)-b))) for a,b in zip(gaps,baseline['max_marginal_gaps']))
        rows.append(dict(shift_windows=shift,score=sol['score'],score_delta=sol['score']-baseline['score'],same_selected=sel==baseline['selected'],maximum_marginal_gap_delta=delta,seconds=sol['seconds']))
    opened=solve(ws,cyclic=False);changed=[i for i,(a,b) in enumerate(zip(opened['choices'],baseline['choices'])) if a!=b];topology_changed=[]
    for i in changed:
        h,k=ws[i]['hypotheses'][opened['choices'][i]],ws[i]['hypotheses'][baseline['choices'][i]]
        from .candidates import signature
        if signature(h)!=signature(k):topology_changed.append(i)
    legacy=json.load(open('photo2/r324/results/graph.json'));small=copy.deepcopy(ws[65:94]);ids={o for w in small for o in w['observation_ids']};obs=[o for o in g['observations'] if o['id'] in ids]
    data=old.preprocess(ImageOps.exif_transpose(Image.open('beads-photo-2.jpg')).convert('RGB'))
    sol=solve(small,cyclic=False);start=time.perf_counter();ns,gg,_,_=infer_graph(obs,small,sol['selected'],data,g['stations_px'],g['period_px']);secs=time.perf_counter()-start+sol['seconds']
    practice=dict(observations=len(obs),indexed=sum(n['component'] is not None for n in ns),edges=len(gg['edges']),unresolved=len(gg['unresolved_edges']),components=len(gg['components']),cycle_conflicts=len(gg['conflicts']),inference_seconds=secs)
    before=solve(legacy['windows']);ns0,gg0,_,_=infer_graph(legacy['observations'],legacy['windows'],before['selected'],data,g['stations_px'],g['period_px'])
    noaug=dict(indexed=sum(n['component'] is not None for n in ns0),edges=len(gg0['edges']),unresolved=len(gg0['unresolved_edges']),components=len(gg0['components']),cycle_conflicts=len(gg0['conflicts']),seconds=before['seconds'])
    # An ablation, explicitly not the delivered mechanism: same old beam, no chart gate.
    oldselected=legacy['selected_window_states'];ns1,gg1,_,_=infer_graph(legacy['observations'],legacy['windows'],oldselected,data,g['stations_px'],g['period_px'])
    gate=dict(indexed=sum(n['component'] is not None for n in ns1),edges=len(gg1['edges']),unresolved=len(gg1['unresolved_edges']),components=len(gg1['components']),cycle_conflicts=len(gg1['conflicts']))
    report=dict(origin_controls=rows,open_versus_cyclic=dict(changed_best_states=changed,changed_topologies=topology_changed,open_choices=opened['choices'],open_selected=opened['selected'],cyclic_choices=baseline['choices']),practice_augmented=practice,cyclic_original_bank=noaug,remove_chart_gate_only=gate)
    old.save(OUT/'controls.json',report);print(report)
if __name__=='__main__':main()
