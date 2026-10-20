"""Apply exact own-photograph decisions before any classifier or pattern fit."""
import argparse
from .common import *
DECISIONS=[('NEW-2185-1265',1,'black'),('NEW-1221-2081',1,'black'),('NEW-1530-3049',1,'black'),('D40-K-2081-2611',1,'black'),('MAT25-K-2270-1942',1,'black'),('MAT25-K-2270-1942',12,'black')]
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);g,obs,co=baseline();panels=read(ROOT/'photo2/r338/review/panels.json');decisions=[];after=copy.deepcopy(g);newobs={r['id']:r for r in after['observations']}
 for photo,num,color in DECISIONS:
  key,p=next((key,p) for key,p in panels.items() if p['id']==photo);k=next(k for k in p['key'] if k['number']==num);oid=k['id'];assert k['xy']==obs[oid]['xy'] and k['ab']==co[oid] and k['color']==obs[oid]['color']
  if photo=='MAT25-K-2270-1942' and num==12:assert oid=='NEW-2259-1961'
  decisions.append(dict(photograph=photo,local_feature=num,panel=key,id=oid,original_color=obs[oid]['color'],color=color,xy=obs[oid]['xy'],ab=co[oid],changed=obs[oid]['color']!=color,source='R339 maker review of exact R338 photograph and immediately matched diagram/key',old_panel_sha256=sha(ROOT/'photo2/r338/review/panels.json')))
  newobs[oid].update(color=color,r339_color_authority='R339 maker own-panel review',r339_before_color=obs[oid]['color'])
 p=panels['completed-known-body'];assert p['id']=='R332-B-0098-0092';decisions.append(dict(photograph=p['id'],panel='completed-known-body',id=p['id'],local_feature=None,color='black',changed=False,source='R339 maker confirms completed body association, color and all displayed adjacency',xy=obs[p['id']]['xy'],ab=co[p['id']]))
 after['indexed_colors']=dict(Counter(newobs[o]['color'] for o in co));after.update(schema='r339-maker-color-overlay-v1',baseline_commit=BASE,previous_graph='photo2/r338/results/graph.json.gz');save(out/'graph.json.gz',after);save(out/'decisions.json',dict(decisions=decisions,ordinary_color_corrections=3,previously_black_confirmations=3,completed_association_confirmation=1,geometry_edits=0));save(out/'input-seal.json',seal_inputs());print('MAKER',[(r['id'],r['changed']) for r in decisions])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
