"""Authoritative maker overlay and complete ranked classification exports."""
import argparse,time,csv
from collections import Counter
from pathlib import Path
from .common import *

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=reviewed_dataset('relocated');ledger=read(artifact('corrections/ledger.json'));audit=read(artifact('classification/audit.json.gz'));raw=read(ROOT/'photo2/r332/results/graph.json.gz');rawobs={r['id']:r for r in raw['observations']};changes={r['id']:r for r in ledger['ordinary_color_corrections']+[ledger['location_correction']]};adj=Counter(o for e in g['edges'] for o in [e['source'],e['target']]);rows=[]
    for o,r in obs.items():
        r=dict(r)
        if o in changes:r.update(review_authority='R334 maker photographic review',original_raw_color=rawobs[o]['color'],original_raw_xy=rawobs[o]['xy'],correction_mechanism=changes[o]['mechanism'])
        rows.append(r)
    overlay=dict(schema='r334-maker-reviewed-overlay-v1',baseline_commit=BASE,raw_input='photo2/r332/results/graph.json.gz',observations=rows,coordinates=g['coordinates'],edges=g['edges'],H=g['H'],reference=g['reference'],correction_ledger='photo2/r334/corrections/ledger.json',yellow_body_preserved=ledger['location_correction']['yellow_body'],indexed_colors=dict(Counter(obs[o]['color'] for o in ids)),policy='Seven ordinary colors and one distinct-body location/color association corrected by maker review. Every lattice coordinate and edge equation retained. Automatic suggestions are NOT observations in this authoritative overlay.')
    save(out/'graph.json.gz',overlay)
    ranked=[]
    for r in audit['ranked_color_candidates']:
        rr={k:v for k,v in r.items() if k!='samples'};rr['lattice_indexed']=r['id'] in co;rr['working_degree']=adj[r['id']];rr['triangulated_priority']=bool(r['body_prediction']=='black' and adj[r['id']]>=2 and r['R333_spatial_expectation']=='black');rr['rank_score']=r['rank_score']+.05*min(adj[r['id']],3)+.5*rr['triangulated_priority'];ranked.append(rr)
    ranked.sort(key=lambda r:(not r['triangulated_priority'],not r['strong_provisional'],-r['rank_score']));save(out/'ranked-suspects.json.gz',ranked)
    fields=['id','status','xy','original_raw_color','overlay_color','body_prediction','plurality','abstain','minimum_vote','lattice_indexed','working_degree','R333_spatial_expectation','triangulated_priority','strong_provisional','rank_score']
    with (out/'ranked-suspects.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(ranked)
    with (out/'complete-classification.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(audit['records'])
    refs=[]
    for r in ledger['ordinary_color_corrections']+[ledger['location_correction']]:
        for ref in r['references']:refs.append(dict(id=r['id'],mechanism=r['mechanism'],original_color=r['original_color'],corrected_color=r['corrected_color'],original_xy=r['original_xy'],corrected_xy=r['corrected_xy'],original_ab=r['original_ab'],**ref))
    with (out/'maker-corrections.csv').open('w',newline='') as f:
        fields=['photograph_identifier','panel_type','case','parent_target','local_number','id','original_color','corrected_color','original_xy','corrected_xy','original_ab','mechanism','asset'];wr=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');wr.writeheader();wr.writerows(refs)
    save(out/'summary.json',dict(indexed=len(ids),observations=len(obs),links=len(g['edges']),maker_corrections=8,ordinary_color_corrections=7,moved_image_locations=1,changed_lattice_coordinates=0,added_or_removed_links=0,indexed_colors=overlay['indexed_colors'],ranked_suspects=len(ranked),three_evidence_source_priority=sum(r['triangulated_priority'] for r in ranked),seconds=time.perf_counter()-t));print('EXPORTED',overlay['indexed_colors'],'priority',sum(r['triangulated_priority'] for r in ranked),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
