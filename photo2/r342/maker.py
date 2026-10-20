"""Four maker judgments applied without altering source identities or geometry."""
from common import *
def main():
 g,obs,co,rgb,auth=load();new=copy.deepcopy(g);rows={r['id']:r for r in new['observations']};changes=[]
 for o,c in MAKER.items():
  before=rows[o]['color'];rows[o].update(color=c,r342_before_color=before,r342_color_authority='Maker R342 own-photograph feature1',r342_color_independent_of_activity=True);changes.append(dict(id=o,before=before,color=c,xy=obs[o]['xy'],ab=co[o],source='Maker R342 response to R341 question',feature=1,pattern_used=False,activity='Retained in full recorded-color cohort. Optional edge/weak-source exclusions tested separately.'))
 new.update(schema='r342-maker-color-overlay-v1',previous_graph='photo2/r341/graph.json.gz',baseline_commit=BASE,indexed_colors=dict(Counter(rows[o]['color'] for o in co)))
 save(OUT/'maker-graph.json.gz',new);save(OUT/'maker-decisions.json',dict(changes=changes,authoritative_labels=auth,geometry_changes=0,identity_changes=0,links_changed=0,pattern_used=False))
 print('Maker changes',[(r['id'],r['before'],r['color']) for r in changes])
if __name__=='__main__':main()
