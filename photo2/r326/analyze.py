"""Post-freeze descriptive comparisons; never detector inputs."""
import json,copy
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from photo2.r323.tracker import save
from photo2.r325.consistency import synchronize
from photo2.r326.contexts import pair_evidence,edge_context
from photo2.r326.runner import key
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def read(p):return json.load(open(p))
def main():
    old=read(ROOT/'photo2/r325/results/graph.json');g=read(OUT/'full/graph.json');evidence=pair_evidence(read(OUT/'full/contexts.json'));model=read(OUT/'full/model-input.json');op={o['id']:o for o in g['observations']};oldkeys={key(e) for e in old['graph']['edges']};newkeys={key(e) for e in g['graph']['edges']};rows=[]
    for e in old['graph']['edges']:
        support=[];contradict=[]
        for wi,hi in enumerate(old['global_solution']['choices']):
            if hi is None:continue
            a=old['windows'][wi]['hypotheses'][hi]['assignments'];s,t=e['source'],e['target']
            if s in a and t in a:
                d=(np.array(a[t]['ab'])-a[s]['ab']).tolist()
                (support if d==e['delta_ab'] else contradict).append(dict(window=wi,hypothesis=hi,delta_ab=d))
        rows.append(dict(source=e['source'],target=e['target'],delta_ab=e['delta_ab'],selected_path_support=support,selected_path_contradictions=contradict,status='selected path conflict' if contradict else ('selected path support' if support else 'marginal-only support')))
    screens=[]
    for name,x in [('R325',old),('R326',g)]:
        statuses=Counter(edge_context(e,evidence)['status'] for e in x['graph']['edges']);es=[copy.deepcopy(e) for e in x['graph']['edges'] if edge_context(e,evidence)['status'] in ['consistent','untested'] and not any(op[o].get('provisional') for o in [e['source'],e['target']])];a,c,coords,comps,cl=synchronize(es,x['observations'],x['stations_px'],x['period_px']);screens.append(dict(name=name,context_statuses=dict(statuses),same_strict_screen_links=len(a),same_strict_screen_indexed=len(coords),same_strict_screen_components=len(comps)))
    coverage=[]
    for s in range(16):
        ids=[o['id'] for o in g['observations'] if min(15,int(g['stations_px'][o['id']]/g['period_px']*16))==s];oldindexed={n['id'] for n in old['intersections'] if n['component'] is not None};newindexed={n['id'] for n in g['intersections'] if n['component'] is not None};coverage.append(dict(section=s,observations=len(ids),R325_indexed=len(set(ids)&oldindexed),R326_indexed=len(set(ids)&newindexed),windows=sum(min(15,int(w['arc_px']/g['period_px']*16))==s for w in g['windows'])))
    report=dict(R325_selected_path_edge_status=dict(Counter(r['status'] for r in rows)),R325_selected_path_edge_audit=rows,edges_added=[list(k) for k in sorted(newkeys-oldkeys)],edges_removed=[list(k) for k in sorted(oldkeys-newkeys)],same_context_screens=screens,coverage=coverage,old_indexed_black=sum(n['component'] is not None and n['color']=='black' for n in old['intersections']),new_indexed_original_black=sum(n['component'] is not None and n['color']=='black' and not op[n['id']].get('provisional') for n in g['intersections']),default_model=dict(links=len(model['edges']),indexed=sum(o['component'] is not None for o in model['observations']),components=len(model['components']),unresolved=sum(o['component'] is None for o in model['observations'])),policy='Coverage, consistency and compatible representation are not independent photographic accuracy. Strict model screen excludes context ambiguity as well as contradiction; same-screen R325 control avoids attributing that policy change to inference.')
    save(OUT/'analysis.json',report)
    print({k:v for k,v in report.items() if k not in ['R325_selected_path_edge_audit','coverage','edges_added','edges_removed']});print('ADDED',len(newkeys-oldkeys),'REMOVED',len(oldkeys-newkeys))
if __name__=='__main__':main()
