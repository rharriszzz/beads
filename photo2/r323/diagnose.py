"""Post-freeze explanatory evidence; maker numbers never enter tracking."""
import json,time
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r323.tracker import ROOT,save,utc
from photo2.r323.review import canvas,point,text,draw_graph,COLORS
OUT=ROOT/'photo2/r323/results'
def main():
    began=time.perf_counter();g=json.loads((OUT/'graph.json').read_text());v=json.loads((OUT/'validation.json').read_text());old=json.loads((ROOT/'photo2/r322/results/graph.json').read_text());ov=json.loads((ROOT/'photo2/r322/results/validation.json').read_text());controls=json.loads((OUT/'controls.json').read_text())
    op={o['id']:o for o in g['observations']};nodes={n['id']:n for n in g['intersections']};mapping={a['maker']:a['node'] for a in v['associations'] if a['status']=='unambiguous proximity association'}
    oldnodes={n['id']:n for n in old['intersections']};newedges={(e['source'],e['target']):e for e in g['graph']['edges']}
    cases=[]
    for a,b in [(2,3),(4,5),(4,3),(11,14),(14,16)]:
        s,t=mapping[a],mapping[b];records=[]
        for wi,w in enumerate(g['windows']):
            alternatives=[]
            for hi,h in enumerate(w['hypotheses']):
                p,q=h['assignments'].get(s),h['assignments'].get(t)
                if p and q:alternatives.append(dict(hypothesis=hi,selected=hi in g['selected_window_states'][wi],score=h['score'],
                    delta_ab=(np.array(q['ab'])-p['ab']).tolist(),residuals_px=[p['residual_px'],q['residual_px']],observations=len(h['assignments']),triangles=h['triangles']))
            if alternatives:records.append(dict(window=wi,crop=w['crop'],alternatives=alternatives))
        oldedge=next((e for e in ov['automatic_links'] if e['maker_source']==a and e['maker_target']==b),None)
        cases.append(dict(maker_pair=[a,b],observations=[s,t],original_support_xy=[op[s]['xy'],op[t]['xy']],
            R322_edge=oldedge,R323_edge=newedges.get((s,t)),propagated_delta=(np.array(nodes[t]['relative_ab'])-nodes[s]['relative_ab']).tolist(),local_window_evidence=records))
    residuals=[]
    for n in g['intersections']:
        if n['conditional_indices'] is None:continue
        residuals.append(n['representative_spread_px'])
    ranges={}
    for name in ('A','B'):
        vals=defaultdict(list)
        for n in nodes.values():
            if n['conditional_indices']:vals[n['conditional_indices'][name]].append(n['id'])
        lo,hi=min(vals),max(vals);ranges[name]=dict(minimum=lo,maximum=hi,distinct_indices=len(vals),missing_indices=sorted(set(range(lo,hi+1))-vals.keys()),
            same_index_distinct_observations=[dict(index=k,observations=x) for k,x in vals.items() if len(x)>1])
    transitions=[]
    for wi,hi in enumerate(g['joint_beam'][0]['choices']):
        if wi==0 or hi is None:continue
        prev=g['joint_beam'][0]['choices'][wi-1]
        if prev is None:continue
        from photo2.r323.tracker import overlap
        transitions.append(dict(windows=[wi-1,wi],**overlap(g['windows'][wi-1]['hypotheses'][prev],g['windows'][wi]['hypotheses'][hi])))
    suspect=[dict(source=e['source'],target=e['target'],xy=np.mean([op[e['source']]['xy'],op[e['target']]['xy']],axis=0).tolist(),reasons=e['reasons'],alternatives=e['alternatives']) for e in g['graph']['unresolved_edges']]
    # All observations, support pixels and color observations preserved; no color
    # repeat selected. The graph has no independent accuracy guarantee outside R161.
    report=dict(created_utc=utc(),specific_cases=cases,bead10=v['bead10'],index_ranges=ranges,overlap_transitions=transitions,
        changed_local_winners=[x for x in controls['joint_decisions'] if x['local_rank']!=0],
        suspected_row_switches=suspect,representative_spread_px=dict(median=float(np.median(residuals)),maximum=float(max(residuals))),
        counts=dict(consistent_overlap_transitions=sum(x['disagree']==0 for x in transitions),all_overlap_transitions=len(transitions),
            accepted_tracks_supported_in_multiple_windows=len(g['tracks']),joint_changed_local_winners=sum(x['local_rank']!=0 for x in controls['joint_decisions']),
            joint_changed_topology=sum(x['local_rank']!=0 and x['overlap_with_local_winner']['disagree']>0 for x in controls['joint_decisions']),
            unresolved_row_assignment_edges=sum('competing row assignment across joint hypotheses' in e['reasons'] for e in g['graph']['unresolved_edges']),
            confirmed_row_switch_errors_R161=sum(e['validation']=='disagrees with maker chart' for e in v['automatic_links']),
            accepted_edge_photographic_checks=len(g['graph']['edges']),rejected_edge_photographic_checks=len(g['graph']['unresolved_edges'])),
        causal_statement='R322 shared phase-contour identity and constructed cycles did not independently certify physical adjacency. R323 competing lattice states are ranked by multiple observed supports and their two-family relative coordinates across overlaps. This recovers the known failures without chart runtime input; a unique optical cause remains unestablished.',
        pattern='Deferred: only the 33 associated local identities have held-out validation; 11 row-ambiguous edges remain outside that patch. No repeat scan or color-based tracker repair.',
        frozen_models='Deferred: whole expanded-chain identity is not independently established. The improved local image graph is useful future correspondence evidence, not a demonstrated defect in R319/R321.',seconds=time.perf_counter()-began)
    save(OUT/'diagnosis.json',report)
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');crop=(1180,235,1350,365);s=5
    raw=canvas(im,crop,s);oldim=canvas(im,crop,s);d=ImageDraw.Draw(oldim)
    for track in old['tracks']:d.line([point(p,crop,s) for p in track['points']],fill=COLORS[track['family']],width=2)
    for e in ov['automatic_links']:
        if e['validation']=='disagrees with maker chart':d.line([point(oldnodes[e[k]]['xy'],crop,s) for k in ('source','target')],fill='#ff952b',width=4)
    new=draw_graph(im,g,crop,s,uncertain=True)
    manual=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text())['annotations']
    for panel in (raw,oldim,new):
        d=ImageDraw.Draw(panel)
        for m in manual:
            if m['number'] in [1,2,3,4,5,8,10,11,14,16]:text(d,point([m['x'],m['y']],crop,s),str(m['number']),size=21)
    result=Image.new('RGB',(raw.width*3,raw.height+90),'#181818')
    for i,(r,title) in enumerate([(raw,'Original photo — maker labels for evaluation'),(oldim,'R322 — orange wrong links'),(new,'R323 — frozen joint proposals')]):result.paste(r,(i*raw.width,90));text(ImageDraw.Draw(result),(i*raw.width+10,15),title,size=20)
    text(ImageDraw.Draw(result),(10,52),'Maker labels were added after the detector freeze; they do not enter automatic inference.',size=20)
    result.save(OUT/'failure-comparison.png')
    # All 40 associations on unaltered original pixels.
    crop=(1180,215,1540,385);s=5;panel=draw_graph(im,g,crop,s,uncertain=True);d=ImageDraw.Draw(panel)
    for m in manual:
        p=point([m['x'],m['y']],crop,s);text(d,p,str(m['number']),'white',18)
        if m['number'] in mapping:d.line([p,point(op[mapping[m['number']]]['xy'],crop,s)],fill='#ffffff',width=1)
    panel.save(OUT/'heldout-validation.png')
    print(json.dumps(report['counts'],indent=2))
if __name__=='__main__':main()
