"""Additional evaluator-only distance/occlusion summaries. No inference updates."""
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from .run import OUT,read,save
from .evaluate import membership

def main():
    rows=[]
    for folder in sorted(OUT.glob('scene-*')):
        owner=np.load(OUT/'synthetic-scenes'/folder.name/'truth-membership.npy');obs=read(folder/'observations.json.gz');by={o['id']:o for o in obs};pix={}
        for k in np.unique(owner):
            if k<0:continue
            y,x=np.where(owner==k);pix[int(k)]=np.c_[x,y]
        for case in read(folder/'test1.json'):
            a=by[case['anchor']];ak,ap=membership(a,owner)
            for method,m in case['methods'].items():
                b=by[m['top']];bk,bp=membership(b,owner)
                if min(ap,bp)<.5 or ak==bk:continue
                true_gap=float(cKDTree(pix[ak]).query(pix[bk])[0].min());support=m['ranking'][0]['cues']['supported_surface_gap_px']
                rows.append(dict(scene=folder.name,anchor=a['id'],method=method,truth_surface_gap_px=true_gap,supported_gap_px=support,anchor_visible_area=len(pix[ak]),neighbor_visible_area=len(pix[bk])))
    loc=read(OUT/'localization-evaluation.json');bins={}
    for label,lo,hi in [('small_visible_support',0,300),('medium_visible_support',300,700),('large_visible_support',700,100000)]:
        rr=[r for r in loc if lo<=r['visible_area']<hi];bins[label]=dict(n=len(rr),median_error_px=float(np.median([r['error_px'] for r in rr])) if rr else None,coverage=float(np.mean([r['covered'] for r in rr])) if rr else None)
    save(OUT/'surface-distance-evaluation.json',rows);save(OUT/'visibility-sensitivity.json',bins)
    real=read(OUT/'real/test1.json');rp=read(OUT/'real/pairs.json.gz');conditional=[]
    for p in rp:conditional+=read(OUT/'real'/p['after_C'])['scores']
    save(OUT/'real-results.json',dict(anchors=len(real),decisions={m:dict(Counter(r['methods'][m]['status'] for r in real)) for m in 'ABC'},pairs=len(rp),C_hypotheses=len(conditional),C_conditional_pixel_matches=sum(r['match'] is not None for r in conditional),D_predictions=sum(len(p['before_D']) for p in rp),verified_real_neighbor_accuracy=None,physical_valid_models=0))
if __name__=='__main__':main()
