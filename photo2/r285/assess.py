"""Descriptive photo diagnostics, never evaluation labels in inference."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r282.common import read,save,pixels,ROOT
from .select import OUT,bank
from .run import local_mask
PERIPHERAL={'e06','e09','e10','e11','e13','e14'}

def evaluate(obs):
    out={};details=[]
    for o in obs:
        lum=np.array(o['native_Y']);smooth=ndi.gaussian_filter(lum,.65);origin=np.array(o['origin']);vs={};edges=o['variants']['S']['method_evidence'].get('saddles',[])
        j=local_mask(o['variants']['J']['measured_support'],origin,lum.shape)
        for m,r in o['variants'].items():
            mask=local_mask(r['measured_support'],origin,lum.shape);inside=mask&~ndi.binary_erosion(mask);outside=ndi.binary_dilation(mask)&~mask
            contrast=float(smooth[inside].mean()-smooth[outside].mean()) if inside.any() and outside.any() else None
            # This is S's own proposed seam evidence, NOT independent true seams.
            crossings=0
            for edge in edges:
                if not edge['separate_after_merging']:continue
                a,b=edge['peaks'];crossings+=bool(mask[a[1],a[0]] and mask[b[1],b[0]])
            vs[m]=dict(**r['metrics'],boundary_inside_minus_outside_Y=contrast,saddle_conflict_proxy=crossings,
                lost_from_J=int((j&~mask).sum()),gained_from_J=int((mask&~j).sum()),lost_J_intensity=float(lum[j&~mask].sum()),
                gained_J_intensity=float(lum[mask&~j].sum()),centerline=r['centerline'],domain_sensitive=r['method_evidence'].get('domain_sensitive'),window_contact=r['method_evidence'].get('window_contact_pixels'))
        details.append(dict(id=o['id'],seed=o['seed'],source_status=o['source_status'],color=o['color'],variants=vs))
    for m in ('A','J','D','S','G'):
        rr=[o['variants'][m] for o in details];valid=[r for r in rr if 0<r['area']<=870]
        side={k:sum(r['centerline']['near'] and r['centerline']['side']==k for r in valid) for k in ('crossing','negative','positive')}
        flanks=[];multiple=[]
        for i,a in enumerate(details):
            ar=a['variants'][m]
            if not(0<ar['area']<=870 and ar['centerline']['near']):continue
            nearby=[]
            for b in details[i+1:]:
                br=b['variants'][m]
                if not(0<br['area']<=870 and br['centerline']['near']):continue
                if abs(ar['centerline']['arc_px']-br['centerline']['arc_px'])<=24:
                    nearby.append(b['id'])
                    if {ar['centerline']['side'],br['centerline']['side']}=={'negative','positive'}:flanks.append([a['id'],b['id']])
            if len(nearby)>=2:multiple.append([a['id'],*nearby])
        out[m]=dict(candidates=len(rr),within_cap=len(valid),median_gradient=float(np.median([r['boundary_gradient'] for r in valid])) if valid else None,
            median_boundary_contrast=float(np.median([r['boundary_inside_minus_outside_Y'] for r in valid])) if valid else None,
            median_shift=float(np.median([r['centroid_shift'] for r in valid if r['centroid_shift'] is not None])) if valid else None,
            saddle_conflict_proxy=sum(r['saddle_conflict_proxy'] for r in valid),connected=sum(r['components']==1 for r in valid),
            near_sides=side,flanking_pairs=flanks,three_or_more_station_groups=multiple,
            distinct_beads=None,real_leakage=None,real_false_split_rate=None)
    return dict(summary=out,observations=details)

def main():
    dev=read(OUT/'development.json.gz')['observations'];sel=read(OUT/'selection.json')['development'];ids={q['observation_id'] for q in sel if q['example'] not in PERIPHERAL};full=evaluate(dev)
    save(OUT/'diagnostics.json.gz',dict(all=full,old_high_source=evaluate([o for o in dev if o['source_status']=='high']),priority_review=evaluate([o for o in dev if o['id'] in ids]),confirmation=evaluate(read(OUT/'confirmation.json.gz')['observations']),peripheral_examples=sorted(PERIPHERAL),scope='Descriptive image evidence. High-source status is not truth; saddle conflicts reuse S evidence and are not independent leakage labels.'))
    save(OUT/'diagnostic-summary.json',dict(all=full['summary'],priority_review=evaluate([o for o in dev if o['id'] in ids])['summary'],confirmation=evaluate(read(OUT/'confirmation.json.gz')['observations'])['summary']))
    source={o['id']:o for o in bank()};save(OUT/'control-clipping.json',dict(A=sum(o['variants']['A']['method_evidence']['search_radius_contact_pixels']>0 for o in source.values() if o['color']!='black'),J=sum(o['variants']['J']['method_evidence']['search_radius_contact_pixels']>0 for o in source.values() if o['color']!='black'),scope='Old radius contact must NOT be confused with missing/new-window-contact=0 in the runner summary.'))
if __name__=='__main__':main()
