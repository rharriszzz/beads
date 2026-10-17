"""Original positive interiors: isolated overlap, visible overlap, neighbor masking."""
from copy import copy
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import pixels
from photo2.r307.fast import Chain as Fast

TARGETS = ['C-1497-0271', 'C-1477-0290', 'R282-1459-0316',
           'R282-1536-0239', 'R282-1537-0308', 'C-1608-0253']

class FirstErrors:
    def __init__(self, data):
        self.rows = [next(r for r in data['rows'] if r['id']==ident and r['kind']=='region') for ident in TARGETS]
        self.parts = [pixels(r['pixels']) for r in self.rows]
    def evaluate(self, s):
        out=[]
        for r, pts in zip(self.rows, self.parts):
            tr=s.trace(pts); own=tr['owner']; good=(own>=0)&~tr['unknown']
            js, counts=np.unique(own[good], return_counts=True)
            order=np.argsort(-counts); js=js[order]; counts=counts[order]
            # All projected bounding spheres that can cover ANY support pixel,
            # including candidates that are wholly hidden by neighbors.
            candidates=sorted({j for group in s.tree.query_ball_point(pts, s.query_radius) for j in group})
            alts=[]
            for j in candidates:
                single=copy(s); single.n=1; single.indices=s.indices[j:j+1]
                single.centers=s.centers[j:j+1]; single.pc=s.pc[j:j+1]
                single.g={key:v[j:j+1] for key,v in s.g.items()}; single.tree=cKDTree(single.pc)
                # Class methods ensure a historical instance's bound method cannot
                # accidentally trace the parent whole scene.
                hit=Fast.trace(single, pts); isolated=(hit['owner']>=0)&~hit['unknown']
                visible=good&(own==j)
                if isolated.any() or visible.any():
                    alts.append(dict(index=int(s.indices[j]), isolated_fraction=float(isolated.mean()),
                                     visible_fraction=float(visible.mean()),
                                     occluded_fraction=float((isolated&~visible).mean()),
                                     unknown_fraction=float(hit['unknown'].mean())))
            alts.sort(key=lambda a:-a['isolated_fraction'])
            out.append(dict(id=r['id'], point=r['point'], pixels=len(pts),
                            modal_fraction=float(counts[0]/len(pts)) if len(counts) else 0.,
                            modal_index=int(s.indices[js[0]]) if len(js) else None,
                            best_isolated_fraction=max([a['isolated_fraction'] for a in alts],default=0.),
                            union_fraction=float(good.mean()), unknown_fraction=float(tr['unknown'].mean()),
                            competing_owners=[dict(index=int(s.indices[j]),fraction=float(n/len(pts))) for j,n in zip(js[:6],counts[:6])],
                            isolated_candidates=alts, physical_identity_verified=False))
        return out
