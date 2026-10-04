"""R218: compare image-derived diffuse-core refinement with frozen R215 masks.

No manual marks, saved spline, adjacency or simulated photo positions are read.
Reflection masks are inherited unchanged; newly split bodies stay provisional.
"""
import argparse
import copy
import json
import os
import uuid
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-segmentation-mpl")
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from skimage.morphology import h_maxima
from skimage.segmentation import watershed
from segment_colored_beads import segment,appearance_context,resize_mask
from auto_label_beads import ROOT, sha
from bead_evidence_inventory import hue_distance


def diffuse_cores(image, report, arrays, prominence=.08, neutral_support=True):
    """Prominent diffuse cores, with color support rather than reflection peaks."""
    if not 0<prominence<=.5:raise ValueError('Diffuse prominence must be positive and at most .5')
    diameter=report['parameters']['native_diameter']
    hsv=rgb_to_hsv(image.astype(np.float32)/255)
    value=hsv[...,2]
    med=ndi.median_filter(value,size=max(3,int(.20*diameter)//2*2+1))
    diffuse=np.where(arrays['reflections']>0,med,value)
    smooth=ndi.gaussian_filter(diffuse,max(.8,.07*diameter))
    modes=report['parameters']['detector']['hue_modes_degrees']
    points=[]
    hue_error=np.min([hue_distance(hsv[...,0]*360,hue) for hue in modes],axis=0)
    for mode,hue in enumerate(modes,1):
        # Neutral reflections inherit the surrounding chromatic support already
        # established by R215. Applying raw highlight hue here would reopen
        # holes and manufacture extra distance peaks on one colored bead.
        support=arrays['domain']&(arrays['family']==mode)&((hue_distance(hsv[...,0]*360,hue)<18)|((arrays['reflections']>0)&neutral_support))
        distance=ndi.distance_transform_edt(support)
        quality=smooth*np.minimum(distance/max(1.,.10*diameter),1.)
        quality[~support]=0
        height=float(np.quantile(smooth[support],.90))*prominence
        peaks=h_maxima(quality,height)&support
        labels,n=ndi.label(peaks)
        for ident,sl in enumerate(ndi.find_objects(labels),1):
            if sl is None:continue
            yy,xx=np.nonzero(labels[sl]==ident); yy+=sl[0].start; xx+=sl[1].start
            best=np.argmax(quality[yy,xx]); y,x=int(yy[best]),int(xx[best])
            if distance[y,x]<max(1.5,.06*diameter):continue
            points.append(dict(xy=[x,y],appearance_mode=mode,quality=float(quality[y,x]),
                               source='image-derived prominent diffuse core'))
    return points,diffuse,smooth,hue_error


def refine(image,digest,method='reseed',prominence=.08,base=None,hue_weight=0.,neutral_support=True):
    if method not in ['supplement','reseed']:raise ValueError('Unknown refinement method')
    if not 0<=hue_weight<=.5:raise ValueError('Hue weight must be between 0 and .5')
    report,arrays=segment(image,digest) if base is None else base
    if report['image_sha256']!=digest:raise ValueError('Cached appearance source does not match image digest')
    diameter=report['parameters']['native_diameter']
    new_points,diffuse,smooth,hue_error=diffuse_cores(image,report,arrays,prominence,neutral_support)
    points=[dict(xy=row['seed_xy'],appearance_mode=row['appearance_mode'],source='R215 accepted automatic seed')
            for row in report['records']]
    added=[]
    if method=='reseed':
        points=[]
    for point in sorted(new_points,key=lambda p:p['quality'],reverse=True):
        existing=[p for p in points if p['appearance_mode']==point['appearance_mode']]
        nearest=min((np.linalg.norm(np.asarray(p['xy'])-point['xy']) for p in existing),default=np.inf)
        if nearest<.35*diameter:continue
        points.append(point); added.append(point)
    if method=='reseed':
        for row in report['records']:
            p=dict(xy=row['seed_xy'],appearance_mode=row['appearance_mode'],source='Uncovered R215 automatic seed')
            existing=[q for q in points if q['appearance_mode']==p['appearance_mode']]
            nearest=min((np.linalg.norm(np.asarray(q['xy'])-p['xy']) for q in existing),default=np.inf)
            if nearest>.65*diameter:points.append(p)
    points.sort(key=lambda p:(p['xy'][1],p['xy'][0],p['appearance_mode']))
    markers=np.zeros(arrays['domain'].shape,np.int32)
    for ident,point in enumerate(points,1):
        x,y=point['xy']; markers[round(y),round(x)]=ident
    candidate=np.zeros(markers.shape,np.int32)
    for mode,hue in enumerate(report['parameters']['detector']['hue_modes_degrees'],1):
        support=arrays['domain']&(arrays['family']==mode)
        part=watershed(arrays['valley']+hue_weight*hue_error/25,np.where(support,markers,0),mask=support,watershed_line=True)
        candidate[part>0]=part[part>0]
    retained=np.zeros(markers.shape,np.int32); records=[]; excluded=[]
    # Selection confidence is learned from this image, independent of manual
    # locations, source loop indices or any fitted spline. It is a proposal
    # subset only, not maker confirmation or a claim of complete coverage.
    context=appearance_context(image)
    clearance=ndi.distance_transform_edt(resize_mask(context['band'],markers.shape))
    brightness={mode:float(np.quantile([p['quality'] for p in new_points if p['appearance_mode']==mode],.90))
        for mode in range(1,len(report['parameters']['detector']['hue_modes_degrees'])+1)
        if any(p['appearance_mode']==mode for p in new_points)}
    central_candidates=np.zeros(markers.shape,np.int32)
    for ident,sl in enumerate(ndi.find_objects(candidate),1):
        if sl is None:continue
        point=points[ident-1]; mask=candidate[sl]==ident; original=mask.copy()
        if mask.sum()<.10*diameter**2:
            candidate[sl][mask]=0; excluded.append(dict(point,reason='Small/sliver refined candidate')); continue
        yy,xx=np.mgrid[sl[0],sl[1]]
        floor=.32*float(np.quantile(diffuse[sl][mask],.90))
        mask&=diffuse[sl]>=floor
        mask&=np.hypot(xx-point['xy'][0],yy-point['xy'][1])<=.85*diameter
        labels,_=ndi.label(mask); x,y=point['xy']; local=(round(y)-sl[0].start,round(x)-sl[1].start)
        if not labels[local]:
            candidate[sl][original]=0; excluded.append(dict(point,reason='Unsupported seed after diffuse/radius guards')); continue
        mask=labels==labels[local]; candidate[sl][original&~mask]=0
        distance=ndi.distance_transform_edt(np.pad(mask,1))[1:-1,1:-1]
        confidence=distance+.25*diffuse[sl]/max(floor/.32,.02)-.25*arrays['valley'][sl]
        core=mask&(distance>=max(.5,.018*diameter))&(confidence>=np.quantile(confidence[mask],.10))
        if not core.any():
            candidate[sl][mask]=0; excluded.append(dict(point,reason='No retained inset after refinement'));continue
        retained[sl][core]=ident
        y0,x0=sl[0].start,sl[1].start; coords=np.argwhere(core)[:,::-1]+[x0,y0]
        hue=report['parameters']['detector']['hue_modes_degrees'][point['appearance_mode']-1]
        core_brightness=float(smooth[round(y),round(x)])
        seed_clearance=float(clearance[round(y),round(x)]/diameter)
        confidence_reasons=[]
        if point['source']!='image-derived prominent diffuse core':confidence_reasons.append('No independent prominent diffuse core')
        if seed_clearance<.55:confidence_reasons.append('Seed close to approximate search-band edge')
        if core_brightness<.45*brightness.get(point['appearance_mode'],1.):confidence_reasons.append('Diffuse core weak relative to learned family')
        if not confidence_reasons:central_candidates[sl][core]=ident
        records.append(dict(region_number=ident,observation_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{digest}:R218:{point["xy"]}')),
            seed_xy=point['xy'],seed_source=point['source'],appearance_mode=point['appearance_mode'],learned_hue_degrees=hue,
            display_color='red' if hue_distance(hue,0)<20 else 'yellow' if hue_distance(hue,45)<25 else 'learned color family',
            candidate_pixels=int(mask.sum()),retained_pixels=int(core.sum()),retained_centroid_xy=coords.mean(axis=0).tolist(),
            retained_components=int(ndi.label(core)[1]),retained_fraction_of_candidate=float(core.sum()/mask.sum()),
            bounding_box=[x0,y0,sl[1].stop,sl[0].stop],
            seed_clearance_diameters=seed_clearance,seed_diffuse_brightness=core_brightness,
            central_candidate=not confidence_reasons,confidence_exclusions=confidence_reasons,reflection_numbers=[],
            bead_index=None,status='Unreviewed refined color region; no distinct bead guarantee'))
    result=copy.deepcopy(report); result['request']='R218'; result['records']=records
    result['excluded_refinement']=excluded; result['added_diffuse_cores']=added
    result['refinement_parameters']=dict(method=method,diffuse_prominence_fraction=prominence,minimum_core_spacing_diameters=.35,
        no_existing_seed_radius_diameters=.65,reflection_masks_unchanged=True,hue_error_weight=hue_weight,
        central_seed_clearance_diameters=.55,central_core_family_brightness_fraction=.45,
        learned_family_core_brightness_90=brightness,neutral_reflection_color_support=neutral_support)
    # Pixel masks are unchanged; body association must be recalculated separately.
    for row in result['reflections']:
        row['owner_region']=None; row.pop('association_status',None)
    row_by_id={r['region_number']:r for r in records}
    for reflection in result['reflections']:
        counts={}
        for y,lo,hi in reflection['pixel_runs']:
            owners,n=np.unique(candidate[y,lo:hi+1],return_counts=True)
            for owner,count in zip(owners,n):
                if owner in row_by_id:counts[int(owner)]=counts.get(int(owner),0)+int(count)
        if counts:
            owner=max(counts,key=counts.get)
            if counts[owner]/reflection['pixels']>=.8:
                reflection['owner_region']=owner
                reflection['association_status']='Tentative refined candidate-mask ownership'
                row_by_id[owner]['reflection_numbers'].append(reflection['reflection_number'])
    result['baseline_counts']=report['counts']
    result['counts']=dict(regions=len(records),candidate_pixels=int((candidate>0).sum()),retained_pixels=int((retained>0).sum()),
        boundary_band_pixels=int(((candidate>0)&(retained==0)).sum()),reflections=len(result['reflections']),
        associated_colored_reflections=sum(r['owner_region'] is not None for r in result['reflections']),
        central_candidate_regions=sum(r['central_candidate'] for r in records),central_candidate_pixels=int((central_candidates>0).sum()),
        broad_color_domain_pixels=int(arrays['domain'].sum()),
        unassigned_domain_pixels=int((arrays['domain']&(candidate==0)).sum()))
    refined=dict(arrays,candidate=candidate,retained=retained,boundary_band=(candidate>0)&(retained==0),
        diffuse_retained=np.where(arrays['reflections']>0,0,retained),central_candidates=central_candidates)
    return result,refined


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r218')
    parser.add_argument('--method',choices=['supplement','reseed'],default='reseed')
    parser.add_argument('--prominence',type=float,default=.08)
    parser.add_argument('--hue-weight',type=float,default=0.)
    parser.add_argument('--no-neutral-support',action='store_true',help='Diagnostic ablation: reopen hue holes at neutral reflections')
    args=parser.parse_args(); image=np.asarray(ImageOps.exif_transpose(Image.open(args.image)).convert('RGB'))
    report,arrays=refine(image,sha(args.image),args.method,args.prominence,hue_weight=args.hue_weight,neutral_support=not args.no_neutral_support)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'regions.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    np.savez_compressed(args.output/'pixel-masks.npz',**arrays)
    print(json.dumps(dict(counts=report['counts'],new_cores=len(report['added_diffuse_cores']))),flush=True)


if __name__=='__main__':main()
