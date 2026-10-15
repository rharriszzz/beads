"""Independent feature coverage, photometric priority and frozen novel targets."""
import hashlib,subprocess,time
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.color import rgb2hsv
from photo2.bead_detection.brightness_r270 import linearize
from .common import *
from .geometry import Reference

POLICY=dict(point_reach=26,nearby_reach=40,broad_window=11,median_Y=.025,contrast_Y=.03,core_resolution_pixels=3,station_spacing=24,new_vs_exposed_distance=45,new_target_separation=24,development=24,reserved=24)

def main():
    if (EVIDENCE/'collection.json').exists():raise RuntimeError('Population already frozen')
    native,rgb,meta=photo();reference=Reference();features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']];lum=linearize(rgb.astype(float)/255)@np.array([.2126,.7152,.0722]);median=ndi.median_filter(lum,size=11);hsv=rgb2hsv(rgb/255);projected=reference.project([q['point'] for q in features]);rows=[]
    for i,f in enumerate(features):
        x,y=f['point'];patch=pixels(f);core_sat=hsv[patch[:,1],patch[:,0],1];neutral_fraction=float(np.mean(core_sat<.25));lit=bool(median[y,x]>=.025 and f['contrast']>=.03 and f['area']>=3);distance=float(projected['distance'][i]);signed=float(projected['signed'][i]);arc=float(projected['arc'][i])
        priority='High: well-observed centerline context' if distance<=26 and lit else 'Central measurement uncertainty' if distance<=26 else 'Nearby well-observed context' if distance<=40 and lit else 'Deferred weak peripheral context' if not lit else 'Clear outside-band context: secondary'
        rows.append(dict(feature_id=f['id'],feature=f,point=f['point'],patch_location=f['weighted'],context_color=f['color'],neutral_patch_fraction=neutral_fraction,reflection_like_patch=neutral_fraction>=.5,photo_metrics=dict(median11_Y=float(median[y,x]),contrast_Y=f['contrast'],patch_pixels=f['area'],threshold_sensitivity_px=f['threshold_sensitivity_px']),well_observed_proxy=lit,priority=priority,centerline=dict(distance=distance,signed_offset=signed,side='positive' if signed>0 else 'negative',arc_px=arc,arc_fraction=arc/reference.length),photograph_border_distance=float(min(x,y,rgb.shape[1]-1-x,rgb.shape[0]-1-y)),arrangement_exterior='Not inferred from signed side or photograph-border proximity',physical_identity=None))
    old=read(ROOT/'photo2/r292/evidence/collection.json')['cases'];exposed=[c['feature']['point'] for c in old];pool=[r for r in rows if r['well_observed_proxy'] and r['centerline']['distance']<=26 and min(np.linalg.norm(np.array(r['point'])-p) for p in exposed)>=45]
    # Spatial strata are a sampling design, never a bead quota or inventory rule.
    selected=[];used=[];unfilled=[]
    for round_index in range(4):
        for sector in range(12):
            candidates=[r for r in pool if int(min(r['centerline']['arc_fraction']*12,11))==sector and all(np.linalg.norm(np.array(r['point'])-p)>=24 for p in used)]
            if not candidates:unfilled.append(dict(round=round_index,sector=sector));continue
            counts={color:sum(r['context_color']==color for r in selected) for color in ('red','yellow','unknown')};color_order=sorted(counts,key=lambda color:(counts[color],color));available=[color for color in color_order if any(r['context_color']==color for r in candidates)];color=available[0]
            side_counts={s:sum(r['centerline']['side']==s for r in selected) for s in ('negative','positive')};sides=sorted(side_counts,key=lambda s:(side_counts[s],s));side=next((s for s in sides if any(r['context_color']==color and r['centerline']['side']==s for r in candidates)),sides[0]);candidates=[r for r in candidates if r['context_color']==color and r['centerline']['side']==side]
            r=min(candidates,key=lambda r:hashlib.sha256(('R293-representative:'+r['feature_id']).encode()).hexdigest());selected.append(r);used.append(r['point']);pool.remove(r)
    # Alternate hash-ranked targets across stages; exact split fixed before outcomes.
    ordered=sorted(selected,key=lambda r:hashlib.sha256(('R293-split:'+r['feature_id']).encode()).hexdigest());cases=[]
    for i,r in enumerate(ordered):
        split='development' if i%2==0 else 'reserved';cases.append(dict(case_id='central-'+r['feature_id'][2:],feature=r['feature'],split=split,selection_anchor=r['point'],categories=['well-observed','centerline-relevant',r['context_color']+'-context',r['centerline']['side']+'-side'],priority_evidence={k:r[k] for k in ('centerline','photo_metrics','reflection_like_patch')},selection_source='R293 frozen representative feature population;12 arc sampling strata x4 passes, context/side diversity, SHA ranking;45px from all77 old targets,24px between selected features. Not physical bead identities or quotas.'))
    historical={p:sha(ROOT/p) for p in subprocess.check_output(['git','ls-files','photo2'],text=True).splitlines() if not p.startswith(('photo2/r293/','photo2/review/r293/','photo2/R293'))};feedback={str(p.relative_to(ROOT)):sha(p) for stage in ('r290','r291','r292') for p in (ROOT/'photo2'/stage/'feedback').rglob('*') if p.is_file()}
    save(EVIDENCE/'historical-hashes.json.gz',historical);save(EVIDENCE/'feedback-hashes.json',feedback)
    save(OUT/'feature-population.json.gz',dict(photo=meta,policy=POLICY,reference_source='photo2/review/r255/spline-samples.csv',reference_sha256=sha(ROOT/'photo2/review/r255/spline-samples.csv'),centerline_length_px=reference.length,records=rows,interpretation='Independent bright features, not bead counts. Context color is unchanged R289 metadata; neutral/reflection-like patches do not certify black physical owners. Photometric proxies are not correctness.'))
    save(EVIDENCE/'collection.json',dict(schema='R293-centerline-population-v1',frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),photo=meta,policy=POLICY,cases=cases,unfilled_sampling_slots=unfilled,source_hashes={p:sha(ROOT/p) for p in ('photo2/r293/population.py','photo2/r293/geometry.py','photo2/R293_SPECIFICATION.md','photo2/r289/results/photo-landmarks.json.gz','photo2/r282/results/centerline.json')},population_sha256=sha(OUT/'feature-population.json.gz'),detector_policy='Unchanged frozen R292. New reserved outcomes remain unopened until post-development method freeze; no major detector revision planned without clear central evidence. Old cases all exposed.'))
    print('Frozen',len(rows),'independent features;',len(cases),'new cases:',sum(c['split']=='development' for c in cases),'development,',sum(c['split']=='reserved' for c in cases),'reserved;',len(unfilled),'unfilled sample slots')
if __name__=='__main__':main()
