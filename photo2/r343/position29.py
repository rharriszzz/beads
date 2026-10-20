"""Five complete source/HSV/neighbor records; no majority-driven pigment edit."""
from common import *

def main():
 g,obs,co,rgb,auth,extra=load();cores={r['id']:r for r in read(OUT/'glass-regions.json')['records']};patches={r['id']:r for r in read(OUT/'sampling-comparison.json')['records']};H=np.array(g['H']);steps=[(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)];records=[]
 for o in P29:
  base=np.array(co[o]);links=[e for e in g['edges'] if o in [e['source'],e['target']]];allowed=None
  for e in links:
   z=e['target'] if e['source']==o else e['source'];a=np.array(co[z]);a-=round(((a-base)@H)/(H@H))*H;cells={tuple(a-np.array(d)) for d in steps};allowed=cells if allowed is None else allowed&cells
  names=[z for z in co if z!=o and np.linalg.norm(np.array(obs[z]['xy'])-obs[o]['xy'])<70];aa=np.array([co[z] for z in names]);aa-=np.rint(((aa-base)@H)/(H@H)).astype(int)[:,None]*H;X=np.c_[aa-base,np.ones(len(aa))];B=np.linalg.lstsq(X,[obs[z]['xy'] for z in names],rcond=None)[0];native_error=float(np.linalg.norm(B[2]-obs[o]['xy']));k=(7*base[0]+6*base[1])%2704;assert k%208==29
  records.append(dict(id=o,recorded_color=obs[o]['color'],xy=obs[o]['xy'],ab=co[o],index_A=int(k),occurrence=int(k//208),authority_category=authority(o,auth),explicit_individual_pigment=False,old_approval=auth.get(o),automatic_protection_retained=o=='NEW-1519-2976',native_core=cores[o],sampling=patches[o],accepted_incident_links=links,local_anchors=names,native_target_excluded_prediction=B[2].tolist(),native_target_excluded_error=native_error,same_neighbor_allowed_cells=[list(v) for v in sorted(allowed)],primitive_neighbor_unique=len(allowed)==1))
 ref=np.array(co[P29[0]]);translations=[]
 for r in records:
  d=np.array(r['ab'])-ref;assert d[0]==d[1] and d[0]%16==0;translations.append(dict(id=r['id'],relative_to=P29[0],delta_ab=d.tolist(),copies_of_16_16=int(d[0]//16)))
 save(OUT/'position29.json',dict(records=records,translations=translations,pigment_correction_adopted=False,metadata_only_target='NEW-1519-2976',current_label_protection_retained=True,photographic_conclusion='NEW1519 glass is orange/yellow-like in native pixels and joint HSV relative to inspected controls, independently of other residue29 labels. Its red remains unchanged and protected; general approval is retained. A new explicit individual pigment question is justified by R343 provenance clarification and current native samples.',lattice_conclusion='All five observations retain their accepted original sites and source identities. Same-neighbor primitive intersections/native fits do not support an isolated index repair. Larger coherent continuations not searched.',pattern_prediction_is_pigment_evidence=False))
 print('P29',[(r['id'],r['recorded_color'],r['occurrence'],r['authority_category'],r['native_target_excluded_error'],r['same_neighbor_allowed_cells']) for r in records])
if __name__=='__main__':main()
