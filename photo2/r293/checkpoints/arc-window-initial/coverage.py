"""Centerline-centered evidence accounting; none of these counts are bead counts."""
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from photo2.r291.evidence import measure,separators
from photo2.r292.review import region
from photo2.bead_detection.brightness_r270 import linearize
from .common import *
from .geometry import Reference

def main():
    native,rgb,meta=photo();ref=Reference();population=read(OUT/'feature-population.json.gz');features=population['records'];points=np.array([r['point'] for r in features]);tree=cKDTree(points);arc=np.array([r['centerline']['arc_px'] for r in features]);signed=np.array([r['centerline']['signed_offset'] for r in features]);distance=np.array([r['centerline']['distance'] for r in features]);lit=np.array([r['well_observed_proxy'] for r in features]);pairs=[]
    # Measure opposite-side local photographic separators without assigning identities.
    for i,j in sorted(tree.query_pairs(40)):
        a,b=features[i],features[j]
        if distance[i]>40 or distance[j]>40 or signed[i]*signed[j]>=0 or ref.arc_distance(arc[i],arc[j])>24:continue
        separation=float(np.linalg.norm(points[i]-points[j]));
        if separation<6:continue
        seed=np.array(a['point']);lo=np.maximum(seed-48,0);hi=np.minimum(seed+49,[rgb.shape[1],rgb.shape[0]]);m=measure(rgb[lo[1]:hi[1],lo[0]:hi[0]],seed-lo);peer=dict(id=b['feature_id'],point=b['point'],local_point=(points[j]-lo).tolist());s=separators(m,seed-lo,[peer]);q=s[0] if s else None
        # A corridor is context evidence, not a hard physical same/different label.
        pairs.append(dict(feature_ids=[a['feature_id'],b['feature_id']],points=[a['point'],b['point']],arc_midpoint=float((arc[i]+((arc[j]-arc[i]+ref.length/2)%ref.length-ref.length/2)/2)%ref.length),distance_px=separation,dark_separator_supported=bool(q and q['supported']),coherence=q['coherence'] if q else None,central_ratio=q['ratios'][2] if q else None,material_contexts=[a['context_color'],b['context_color']],physical_distinct_beads=None,ownership='Photographic separator supports two-surface interpretation' if q and q['supported'] else 'Multiple opposite-side observations; ownership/separation unresolved'))
    duplicates=[]
    for i,j in sorted(tree.query_pairs(12)):
        if distance[i]>40 and distance[j]>40:continue
        a,b=features[i],features[j];shared=len(set(map(tuple,pixels(a['feature'])))&set(map(tuple,pixels(b['feature']))));duplicates.append(dict(feature_ids=[a['feature_id'],b['feature_id']],distance_px=float(np.linalg.norm(points[i]-points[j])),shared_bright_patch_pixels=shared,same_physical_bead=None,interpretation='Nearby features or overlapping bright patches; do not count as distinct beads'))
    human=read(EVIDENCE/'r292-review-analysis.json')['records'];human_byid={r['feature_id']:r for r in human};station_arc,station_points=ref.station_points();lum=linearize(rgb.astype(float)/255)@np.array([.2126,.7152,.0722]);mean11=ndi.uniform_filter(lum,11);stations=[]
    for idx,(s,p) in enumerate(zip(station_arc,station_points)):
        near=np.flatnonzero((ref.arc_distance(arc,s)<=18)&(distance<=26));nearby=np.flatnonzero((ref.arc_distance(arc,s)<=18)&(distance<=40));good=[i for i in near if lit[i]];sides={side:[features[i]['feature_id'] for i in near if features[i]['centerline']['side']==side] for side in ('negative','positive')};supported=[q for q in pairs if q['dark_separator_supported'] and ref.arc_distance(q['arc_midpoint'],s)<=18];bad=[r['case_id'] for r in human if r['answer']=='wrong-clear' and ref.arc_distance(ref.project([r['point']])['arc'][0],s)<=18 and ref.project([r['point']])['distance'][0]<=40];x,y=np.rint(p).astype(int);state='Illuminated feature evidence present; completeness unverified' if good else 'Only weaker independent evidence nearby' if len(near) else 'No accepted R289 feature in station window';sample=float(mean11[y,x]);stations.append(dict(station_id=f'S{idx:03}',arc_px=float(s),point=p.tolist(),state=state,near_feature_ids=[features[i]['feature_id'] for i in near],nearby_feature_ids=[features[i]['feature_id'] for i in nearby],well_observed_features=len(good),context_counts=dict(Counter(features[i]['context_color'] for i in near)),reflection_like_patches=sum(features[i]['reflection_like_patch'] for i in near),signed_sides=sides,both_sides_observed=bool(all(sides.values())),supported_opposite_side_pairs=[q['feature_ids'] for q in supported],human_clear_failures=bad,local_mean11_Y=sample,lit_window_without_feature=bool(not len(near) and sample>=.025),physical_bead_count=None,completeness=None))
    # Cross-reference old measured locations as independent historical gap evidence,
    # never as verified identity or a mask to constrain new detection.
    legacy=read(ROOT/'photo2/review/r275/inventory.json')['locations'];legacy_points=np.array([[r['point']['x'],r['point']['y']] for r in legacy]);ld=ref.project(legacy_points)['distance'];nearest,ix=tree.query(legacy_points);legacy_gaps=[dict(location_id=r['id'],point=legacy_points[i].tolist(),color=r['color'],centerline_distance=float(ld[i]),nearest_R289_feature=features[int(ix[i])]['feature_id'],distance_to_feature=float(nearest[i]),interpretation='Historical image-derived location without close independent R289 feature; not ground truth or a new bead') for i,r in enumerate(legacy) if ld[i]<=26 and nearest[i]>8]
    save(OUT/'coverage.json',dict(photo=meta,reference=dict(source=population['reference_source'],sha256=population['reference_sha256'],points=ref.points.tolist(),length_px=ref.length,station_spacing=24,station_arc_half_window=18,point_reach=26,nearby_reach=40,role='Existing image-derived reference only; not physical indexing'),feature_count=len(features),priority_counts=dict(Counter(r['priority'] for r in features)),near26=int((distance<=26).sum()),near40=int((distance<=40).sum()),well_observed_near26=int(((distance<=26)&lit).sum()),reflection_like_near26=int(sum(r['reflection_like_patch'] and r['centerline']['distance']<=26 for r in features)),stations=stations,opposite_side_pairs=pairs,near_feature_ambiguities=duplicates,historical_location_gaps=legacy_gaps,summary=dict(stations=len(stations),illuminated_feature_stations=sum(bool(s['well_observed_features']) for s in stations),any_feature_stations=sum(bool(s['near_feature_ids']) for s in stations),both_side_stations=sum(s['both_sides_observed'] for s in stations),separator_supported_both_side_stations=sum(bool(s['supported_opposite_side_pairs']) for s in stations),lit_windows_without_feature=sum(s['lit_window_without_feature'] for s in stations),human_clear_failure_stations=sum(bool(s['human_clear_failures']) for s in stations),opposite_side_pairs=len(pairs),separator_supported_pairs=sum(q['dark_separator_supported'] for q in pairs),ambiguous_near_feature_pairs=len(duplicates),legacy_near_locations_without_close_feature=len(legacy_gaps)),limits='Counts are features/windows/pairs, never physical bead counts or proof of complete coverage. Signed sides are local curve orientation, not arrangement inside/outside. Neutral patches are possible reflections, not certified black bodies. Illumination alone does not establish a bead or clear outer edge.'))
    # Lightweight browser overview: full native photo and independent feature dots.
    from PIL import Image
    Image.fromarray(native).save(REVIEW/'original.png')
    save(REVIEW/'coverage.json',dict(read(OUT/'coverage.json'),features=[{k:r[k] for k in ('feature_id','point','context_color','reflection_like_patch','well_observed_proxy','priority','centerline','photograph_border_distance')} for r in features]))
    print('Coverage:',read(OUT/'coverage.json')['summary'])
if __name__=='__main__':main()
