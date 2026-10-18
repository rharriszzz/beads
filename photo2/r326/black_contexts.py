"""Fresh colored-only fits around native faint sites; black pixels never fit geometry."""
import copy
from collections import defaultdict
import numpy as np
from photo2.r325.batched_fit import fit_hypotheses
from photo2.r325.candidates import signature


def corroborate(black,contexts,obs):
    result=copy.deepcopy(black);op={o['id']:o for o in obs};faint=list({tuple(map(tuple,p['raw_support_pixels'])):p for p in black['predictions'] if 'raw_support_pixels' in p}.values());ledger=[]
    for c in contexts:
        near=[p for p in faint if np.linalg.norm(np.array(p['raw_centroid_xy'])-c['center'])<c['size']/2-12]
        if not near or not c.get('spectral'):continue
        ids=[o for o in c['observation_ids'] if op[o]['color'] in ['red','yellow']]
        if len(ids)<6:continue
        R=np.array(c['frame']);cen=np.array(c['center']);xy=(np.array([op[o]['xy'] for o in ids])-cen)@R;sig=np.full(len(ids),5.);wt=np.array([1 if op[o]['band_clearance_px']>=18 else .55 for o in ids]);bases=[];hs=[];rng=np.random.default_rng(32628+c['parent']+c['size'])
        for tri in c['spectral']['triangles']:
            B=np.linalg.inv(np.array([c['spectral']['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
            if any(np.linalg.norm(B-b)<4 for b in bases):continue
            bases.append(B);hs+=fit_hypotheses(xy,sig,wt,B,ids,rng)[0]
            if len(bases)>=3:break
        unique={}
        for h in sorted(hs,key=lambda h:-h['score']):
            s=signature(h)
            if s not in unique:unique[s]=h
        for rank,h in enumerate(list(unique.values())[:2]):
            B=np.array(h['basis']);offset=np.array(h['offset']);a=h['assignments'];cells={tuple(v['ab']):o for o,v in a.items()}
            for p in near:
                local=(np.array(p['raw_centroid_xy'])-cen)@R;cell=np.rint(np.linalg.solve(B,local-offset)).astype(int);pred=R@(B@cell+offset)+cen
                if tuple(cell) in cells or np.linalg.norm(pred-p['raw_centroid_xy'])>12:continue
                anchors=[o for q,o in cells.items() if tuple(np.array(q)-cell) in [(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)]]
                if len(anchors)<2 or np.linalg.matrix_rank(np.array([a[o]['ab'] for o in anchors])-cell)<2:continue
                record=copy.deepcopy(p);record.update(window=c['parent'],context=c['id'],colored_hypothesis=rank,colored_anchors=anchors,predicted_xy=pred.tolist(),cell_ab=cell.tolist(),colored_assignments={o:v['ab'] for o,v in a.items()},basis_local=B.tolist(),offset_local=offset.tolist(),context_frame=c['frame'],context_center=c['center'],evidence='native faint site corroborated by fresh colored-only changed-context fit')
                result['predictions'].append(record);ledger.append(record)
    return result,ledger
