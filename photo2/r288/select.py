"""Photograph-only new regions frozen before selector outcomes."""
import hashlib
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from photo2.r282.phase1 import image_features
from .common import *

def main():
    _,rgb,meta=photo();f=image_features(rgb);rows=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);ct=cKDTree(curve)
    oldcenters=[q['center'] for q in read(ROOT/'photo2/r284b/results/cases.json')]+[q['seed'] for q in read(ROOT/'photo2/r285/results/selection.json')['confirmation']]+[q['seed'] for q in read(ROOT/'photo2/r286/results/selection.json')['confirmation']]+[q['seed'] for q in read(OLD/'selection.json')['confirmation']];selected=[];pool=[]
    for r in rows:
        if r['color'] not in ('red','yellow') or r['status']!='high' or not r['centerline']['near']:continue
        x,y=r['seed'];v=f['lum'][y-5:y+6,x-5:x+6];exposure=float(np.median(v))
        if exposure>.025 and all(np.linalg.norm(np.array(r['seed'])-p)>100 for p in oldcenters):pool.append(dict(r,exposure=exposure))
    def rank(r):return hashlib.sha256(('R288-confirmation:'+r['record_id']).encode()).hexdigest()
    def far(r):return all(np.linalg.norm(np.array(r['seed'])-q['seed'])>80 for q in selected)
    strata=[(color,'crossing') for _ in range(4) for color in ('red','yellow')]+[(color,'same-color') for _ in range(2) for color in ('red','yellow')]+[(color,'flanking') for color in ('red','yellow')]+[(color,'near') for color in ('red','yellow')]
    ledger=[]
    for color,kind in strata:
        eligible=[]
        for a in pool:
            if a['color']!=color or not far(a):continue
            if kind=='crossing' and not a['centerline']['crosses']:continue
            companions=[]
            if kind in ('same-color','flanking'):
                for b in rows:
                    d=np.linalg.norm(np.array(a['seed'])-b['seed'])
                    if b['color'] not in ('red','yellow') or not b['centerline']['near'] or not 12<=d<=42:continue
                    if kind=='same-color' and a['color']!=b['color']:continue
                    if kind=='flanking' and {a['centerline']['side'],b['centerline']['side']}!={'negative','positive'}:continue
                    companions.append(b['record_id'])
                if not companions:continue
            eligible.append((a,companions))
        if not eligible:
            ledger.append(dict(color=color,stratum=kind,reason='No remaining spatially independent eligible cue; no result-driven relaxation.'));continue
        a,companions=min(eligible,key=lambda x:rank(x[0]));neighbors=[dict(id=r['record_id'],seed=r['seed'],color=r['color'],source_status=r['status']) for r in rows if r['color'] in ('red','yellow') and np.linalg.norm(np.array(a['seed'])-r['seed'])<=36]
        selected.append(dict(name=f'Q{len(selected)+1:02}',id=a['record_id'],seed=a['seed'],color=color,stratum=kind,exposure=a['exposure'],companions=companions,observations=neighbors))
    assert 12<=len(selected)<=20,(len(selected),ledger)
    save(OUT/'selection.json',dict(confirmation=selected,development=[dict(name=q['name'],seed=q['seed'],ids=[o['id'] for o in q['observations']]) for q in development()],excluded_centers=oldcenters,minimum_old_center_distance=100,minimum_new_center_distance=80,selection_ledger=ledger,rule='Stable SHA256 R288-confirmation:ID within planned strata; old high/photo support-near, native11 medianY>.025; all nearby old colored cues within36px retained; no selector outputs used.',photo=meta,baseline_sha256=sha(ROOT/'photo2/r283/results/phase1.json.gz'),new_methods_evaluated=False))
    print('Selected',len(selected),'regions',sum(len(q['observations']) for q in selected),'cues',[(q['name'],q['color'],q['stratum']) for q in selected]);print('unfilled',ledger)
if __name__=='__main__':main()
