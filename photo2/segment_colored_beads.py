"""R215: image-only broad colored-body regions and separate reflection pixels.

No saved labels, adjacency series, center spline or placement model is read.
Pixel masks are proposals; a retained fraction of a candidate is not true recall.
"""
import argparse
import json
import os
import uuid
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-segmentation-mpl')

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from scipy.spatial import cKDTree
from matplotlib.colors import rgb_to_hsv
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.measure import regionprops
from skimage.morphology import skeletonize
from skimage.segmentation import watershed, find_boundaries

import auto_label_beads as auto
from bead_evidence_inventory import encode_pixels, hue_distance


def resize_mask(mask, shape):
    return np.asarray(Image.fromarray(mask).resize((shape[1], shape[0]), Image.Resampling.NEAREST), bool)


def appearance_context(image, max_dimension=1600):
    """Learn paper/color/scale without requiring a closed strip axis.

    The older point detector's appearance initialization is reused explicitly,
    but pixel segmentation must not depend on successful curve/graph tracing.
    No skeleton path or geometric bead placement is computed.
    """
    height,width=image.shape[:2]; factor=min(1.,max_dimension/max(height,width))
    nw,nh=round(width*factor),round(height*factor)
    rgb=np.asarray(Image.fromarray(image).resize((nw,nh),Image.Resampling.LANCZOS),np.float32)/255
    hsv=rgb_to_hsv(rgb); hue=hsv[...,0]*360; sat=hsv[...,1]; value=hsv[...,2]
    scale=np.asarray([nw/width,nh/height])
    border=np.zeros((nh,nw),bool); margin=max(1,int(min(nh,nw)*.025))
    border[:margin]=True; border[-margin:]=True; border[:,:margin]=True; border[:,-margin:]=True
    chrom=rgb[...,:2]/np.maximum(rgb.sum(axis=2,keepdims=True),.01)
    bg=np.median(chrom[border],axis=0); mad=np.median(abs(chrom[border]-bg),axis=0)*1.4826
    score=np.sqrt(np.sum(((chrom-bg)/np.maximum(mad,.003))**2,axis=2))
    border_tail=float(np.quantile(score[border],.999))
    threshold=max(min(border_tail,50.),float(threshold_otsu(np.minimum(score,50))))
    background_value=float(np.median(value[border]))
    foreground=(score>threshold)|(value<background_value*.15)
    sigma=max(1.,max(nh,nw)/520)
    foreground=auto.small_components(foreground,max(4,int(sigma*sigma)))
    band=ndi.gaussian_filter(foreground.astype(float),sigma)>.2
    band=auto.fill_small_holes(band,int((sigma*10)**2))
    band=auto.small_components(band,int((sigma*10)**2))
    labels,_=ndi.label(band); sizes=np.bincount(labels.ravel()); sizes[0]=0
    if not sizes.max():
        raise ValueError('No supported image search band')
    band=labels==sizes.argmax()
    useful=foreground&band&(value>np.quantile(value[foreground],.4))&(sat>np.quantile(sat[foreground],.25))
    hist,_=np.histogram(hue[useful],bins=360,range=(0,360),weights=(value*sat)[useful])
    hist=ndi.gaussian_filter1d(hist,3,mode='wrap')
    peaks,_=find_peaks(np.r_[hist[-30:],hist,hist[:30]],distance=18,prominence=hist.max()*.08)
    modes=[int(p-30) for p in sorted((p for p in peaks if 30<=p<390),key=lambda p:hist[p-30],reverse=True)]
    if not modes:
        raise ValueError('No supported image-derived chromatic family')
    smin=max(.2,float(np.quantile(sat[foreground],.18)*.75))
    local_value=ndi.gaussian_filter(value,4)
    masks=[]
    for mode in modes:
        mask=foreground&band&(hue_distance(hue,mode)<15)&(sat>smin)
        mask&=(value>background_value*.15)&(value>local_value*.5)
        masks.append(auto.small_components(mask,15))
    props=[p for mask in masks for p in regionprops(ndi.label(mask)[0]) if 20<=p.area<2000 and p.axis_minor_length>3]
    distance=ndi.distance_transform_edt(band); skeleton=skeletonize(band)
    halfwidth=float(np.median(distance[skeleton])); internal=float(np.median([p.axis_minor_length for p in props])) if props else halfwidth*.56
    diameter=max(internal,halfwidth*.56)
    points=[]
    for mode,mask in enumerate(masks,1):
        smooth=ndi.gaussian_filter(ndi.distance_transform_edt(mask),diameter/12)
        locations=peak_local_max(smooth,min_distance=max(2,int(diameter*.55)),
            threshold_abs=max(1.5,diameter*.13),labels=mask)
        markers=np.zeros(mask.shape,np.int32)
        for ident,(y,x) in enumerate(locations,1): markers[y,x]=ident
        regions=watershed(-smooth,markers,mask=mask)
        for region in regionprops(regions):
            if region.area<diameter**2*.10 or region.axis_minor_length<diameter*.35: continue
            y,x=locations[region.label-1]
            core=region.coords[smooth[region.coords[:,0],region.coords[:,1]]>smooth[y,x]*.5]
            yy,xx=np.average(core,axis=0,weights=smooth[core[:,0],core[:,1]]**2)
            same=[p for p in points if p['appearance_mode']==mode and np.linalg.norm((np.asarray(p['source_xy'])+.5)*scale-.5-[xx,yy])<diameter*.5]
            if any(auto.line_evidence(rgb,[xx,yy],(np.asarray(p['source_xy'])+.5)*scale-.5,modes[mode-1])[0]>.85 for p in same): continue
            points.append(dict(source_xy=((np.asarray([xx,yy])+.5)/scale-.5).tolist(),
                               kind='chromatic',appearance_mode=mode))
    response=ndi.gaussian_filter(value,max(.65,min(1.5,diameter*.08)))-ndi.gaussian_filter(value,diameter*.4)
    noise=float(np.median(abs(response[border]-np.median(response[border])))*1.4826)
    parameters=dict(analysis_size=[nw,nh],scale_xy=scale.tolist(),background_chromaticity=bg.tolist(),background_mad=mad.tolist(),
        background_value=background_value,foreground_threshold=threshold,border_fraction=.025,
        border_score_tail_999=border_tail,border_tail_clipped=bool(border_tail>50),
        hue_modes_degrees=modes,saturation_floor=smin,reflection_response_floor=max(.015,4*noise),
        apparent_internal_width=internal,apparent_diameter=diameter,band_halfwidth=halfwidth,
        role='Image-derived appearance/search band; no closed centerline or adjacency prerequisite')
    return dict(parameters=parameters,band=band,scale=scale,diameter=diameter,points=points)


def reflection_regions(hsv, band, diameter, border, floor):
    """Bright compact excess with neutralizing color change or a dark surround.

    Hue is never used for the reflection itself. A reflection position is not a
    body center; association to a body is a separate, tentative operation.
    """
    sat, value = hsv[..., 1], hsv[..., 2]
    response = ndi.gaussian_filter(value, .8)-ndi.gaussian_filter(value, .35*diameter)
    noise = float(np.median(abs(response[border]-np.median(response[border])))*1.4826)
    small_sat = ndi.gaussian_filter(sat, .8)
    broad_sat = ndi.gaussian_filter(sat, .25*diameter)
    score = np.maximum(response, 0)*(1+2*np.maximum(broad_sat-small_sat, 0))
    clearance = ndi.distance_transform_edt(band)
    peaks = peak_local_max(score, min_distance=max(2, int(.12*diameter)),
        threshold_abs=max(floor, 5*noise), labels=band & (clearance > .4*diameter))
    labels = np.zeros(band.shape, np.int32); rows = []
    for y, x in peaks:
        radius = max(4, int(np.ceil(.35*diameter)))
        x0, x1 = max(0, x-radius), min(band.shape[1], x+radius+1)
        y0, y1 = max(0, y-radius), min(band.shape[0], y+radius+1)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        rr = np.hypot(xx-x, yy-y)
        local_v = value[y0:y1, x0:x1]; local_s = sat[y0:y1, x0:x1]
        ring = (rr > .18*diameter) & (rr < .32*diameter)
        if not ring.any():
            continue
        baseline = float(np.median(local_v[ring])); ring_s = float(np.median(local_s[ring]))
        near = rr <= max(2., .12*diameter)
        qy, qx = np.unravel_index(np.where(near, local_v, -1).argmax(), near.shape)
        peak = float(local_v[qy, qx]); peak_s = float(local_s[qy, qx])
        if peak-baseline < max(.10, 5*noise):
            continue
        if not (ring_s-peak_s > .10 or (peak_s < .30 and baseline < .45)):
            continue
        component, _ = ndi.label((rr < .28*diameter) & (local_v >= baseline+.60*(peak-baseline)))
        mask = component == component[qy, qx]
        if not component[qy, qx] or mask.sum() < 2 or mask.sum() > .20*diameter**2:
            continue
        current = labels[y0:y1, x0:x1]
        if np.any(current[mask]):
            continue
        weights = np.maximum(local_v[mask]-baseline, 0)**2
        xy = np.average(np.column_stack((xx[mask], yy[mask])), axis=0, weights=weights)
        ident = len(rows)+1; current[mask] = ident
        alternatives = []
        for level in [.55, .65]:
            cc, _ = ndi.label((rr < .28*diameter) & (local_v >= baseline+level*(peak-baseline)))
            mm = cc == cc[qy, qx]
            alternatives.append(np.average(np.column_stack((xx[mm], yy[mm])), axis=0,
                weights=np.maximum(local_v[mm]-baseline, 0)**2).tolist())
        rows.append(dict(reflection_number=ident, xy=xy.tolist(), peak_value=peak, surround_value=baseline,
            peak_saturation=peak_s, surround_saturation=ring_s, pixels=int(mask.sum()),
            pixel_runs=encode_pixels(mask, [x0, y0]), threshold_alternative_xy=alternatives,
            threshold_position_sensitivity_pixels=float(np.max(np.linalg.norm(np.asarray(alternatives)-xy, axis=1))),
            owner_region=None, role='Specular-appearance proposal, not bead center/boundary', status='unreviewed'))
    return labels, rows, dict(response_floor=max(floor, 5*noise), background_response_noise=noise,
                              minimum_peak_surround_difference=max(.10, 5*noise))


def segment(image, digest, use_dark_valleys=True, target_candidate_fraction=.90, context=None):
    if not .5 <= target_candidate_fraction <= .95:
        raise ValueError('Candidate fraction must be between .5 and .95')
    image = np.asarray(image, np.uint8)
    detected = appearance_context(image) if context is None else context
    diameter = float(detected['diameter']/np.sqrt(np.prod(detected['scale'])))
    hsv = rgb_to_hsv(image.astype(np.float32)/255)
    hue, sat, value = hsv[..., 0]*360, hsv[..., 1], hsv[..., 2]
    band = resize_mask(detected['band'], value.shape)
    clearance = ndi.distance_transform_edt(band)
    border = np.zeros(value.shape, bool)
    margin = max(1, int(min(value.shape)*detected['parameters']['border_fraction']))
    border[:margin] = True; border[-margin:] = True; border[:, :margin] = True; border[:, -margin:] = True
    modes = np.asarray(detected['parameters']['hue_modes_degrees'], float)
    differences = np.asarray([hue_distance(hue, mode) for mode in modes], np.float32)
    family = differences.argmin(axis=0)+1
    error = differences.min(axis=0)
    bg_hue = float(np.degrees(np.angle(np.mean(np.exp(1j*np.deg2rad(hue[border]))))) % 360)
    rgb = image.astype(np.float32)/255
    chrom = rgb[..., :2]/np.maximum(rgb.sum(axis=2, keepdims=True), .01)
    bg = np.asarray(detected['parameters']['background_chromaticity'])
    mad = np.maximum(detected['parameters']['background_mad'], .003)
    foreground_score = np.sqrt(np.sum(((chrom-bg)/mad)**2, axis=2))
    local_v = ndi.gaussian_filter(value, .35*diameter)
    domain = band & (error < 25) & (sat > detected['parameters']['saturation_floor']*.45)
    domain &= (foreground_score > detected['parameters']['foreground_threshold']*.60)
    # Background and a bead family can share hue (e.g. amber on brown paper).
    # Their learned chromaticity distributions still differ; hue alone must
    # not erase that entire family. Retain bg hue only as a diagnostic.
    domain &= value > local_v*.25
    domain = auto.small_components(domain, max(8, int(.03*diameter**2)))
    reflections, reflection_rows, reflection_params = reflection_regions(hsv, band, diameter, border,
        detected['parameters']['reflection_response_floor'])
    # Only a bright component supported by a predominantly chromatic immediate
    # surround joins a colored domain. Never fill arbitrary enclosed holes.
    attached_reflections = []
    for reflection in reflection_rows:
        runs = reflection['pixel_runs']; xs = [r[1] for r in runs]+[r[2] for r in runs]; ys = [r[0] for r in runs]
        pad = max(2, int(.12*diameter))
        x0, x1 = max(0, min(xs)-pad), min(value.shape[1], max(xs)+pad+1)
        y0, y1 = max(0, min(ys)-pad), min(value.shape[0], max(ys)+pad+1)
        mask = reflections[y0:y1, x0:x1] == reflection['reflection_number']
        surround = ndi.binary_dilation(mask, iterations=pad) & ~mask
        supported = domain[y0:y1, x0:x1][surround]
        if len(supported) and supported.mean() >= .65:
            counts = np.bincount(family[y0:y1, x0:x1][surround & domain[y0:y1, x0:x1]], minlength=len(modes)+1)
            mode = int(counts.argmax())
            if counts[mode]/counts.sum() >= .8:
                domain[y0:y1, x0:x1][mask] = True
                family[y0:y1, x0:x1][mask] = mode
                attached_reflections.append(reflection['reflection_number'])
    points = [dict(xy=p['source_xy'], appearance_mode=p['appearance_mode'], source='automatic color-distance peak')
              for p in detected['points'] if p['kind'] == 'chromatic']
    # Add supported native-scale cores not covered by coarse-scale seeds.
    for mode in range(1, len(modes)+1):
        strong = domain & (family == mode) & (error < 16) & (value > local_v*.75)
        distance = ndi.gaussian_filter(ndi.distance_transform_edt(strong), .8)
        peaks = peak_local_max(distance, min_distance=max(3, int(.40*diameter)),
            threshold_abs=max(2., .08*diameter), labels=strong)
        existing = [p['xy'] for p in points if p['appearance_mode'] == mode]
        tree = cKDTree(existing) if existing else None
        for y, x in peaks:
            if clearance[y, x] < .15*diameter or (tree is not None and tree.query([x, y])[0] < .40*diameter):
                continue
            points.append(dict(xy=[int(x), int(y)], appearance_mode=mode, source='additional native color core'))
    points.sort(key=lambda p: (p['xy'][1], p['xy'][0], p['appearance_mode']))
    markers = np.zeros(value.shape, np.int32); valid_points = []; excluded = []
    for point in points:
        x, y = np.rint(point['xy']).astype(int)
        if not domain[y, x] or family[y, x] != point['appearance_mode']:
            radius = max(2, int(np.ceil(.18*diameter)))
            y0, y1 = max(0, y-radius), min(value.shape[0], y+radius+1)
            x0, x1 = max(0, x-radius), min(value.shape[1], x+radius+1)
            yy, xx = np.mgrid[y0:y1, x0:x1]
            compatible = domain[y0:y1, x0:x1] & (family[y0:y1, x0:x1] == point['appearance_mode'])
            distances = np.where(compatible, np.hypot(xx-point['xy'][0], yy-point['xy'][1]), np.inf)
            if distances.min() > .18*diameter:
                excluded.append(dict(point, reason='No compatible nearby seed pixel in broad domain'))
                continue
            j, i = np.unravel_index(distances.argmin(), distances.shape)
            point = dict(point, original_automatic_xy=point['xy'], xy=[int(xx[j,i]),int(yy[j,i])])
            x, y = point['xy']
        if markers[y,x]:
            excluded.append(dict(point, reason='Duplicate seed pixel')); continue
        if clearance[y, x] < .15*diameter:
            excluded.append(dict(point, reason='Too close to approximate search-band edge'))
            continue
        valid_points.append(point); markers[y, x] = len(valid_points)
    candidate = np.zeros(value.shape, np.int32)
    # Remove compact specular brightness from the boundary elevation only.
    # Reflection pixels and raw RGB remain separately available, unchanged.
    median_value = ndi.median_filter(value, size=max(3, int(.20*diameter)//2*2+1))
    diffuse_value = np.where(reflections > 0, median_value, value)
    smooth_v = ndi.gaussian_filter(diffuse_value, max(.65, .025*diameter))
    local_diffuse = ndi.gaussian_filter(diffuse_value, .40*diameter)
    valley = np.maximum(0, 1-smooth_v/np.maximum(local_diffuse, .02))
    for mode in range(1, len(modes)+1):
        mask = domain & (family == mode)
        local_markers = np.where(mask, markers, 0)
        if not local_markers.any():
            continue
        if use_dark_valleys:
            elevation = valley + .15*error/25
        else:
            elevation = -ndi.distance_transform_edt(mask)/diameter
        part = watershed(elevation, local_markers, mask=mask, watershed_line=True)
        candidate[part > 0] = part[part > 0]
    retained = np.zeros(value.shape, np.int32); rows = []
    slices = ndi.find_objects(candidate, max_label=len(valid_points))
    minimum_inset = max(.5, .018*diameter)
    for ident, point in enumerate(valid_points, 1):
        sl = slices[ident-1]
        if sl is None:
            continue
        mask = candidate[sl] == ident
        if mask.sum() < .10*diameter**2:
            excluded.append(dict(point, reason='Small/sliver candidate', candidate_pixels=int(mask.sum())))
            candidate[sl][mask] = 0
            continue
        original_mask = mask.copy()
        vv = diffuse_value[sl][mask]
        floor = .32*float(np.quantile(vv, .90))
        if use_dark_valleys:
            mask &= diffuse_value[sl] >= floor
        yy, xx = np.mgrid[sl[0], sl[1]]
        mask &= np.hypot(xx-point['xy'][0], yy-point['xy'][1]) <= .85*diameter
        connected, _ = ndi.label(mask)
        seed_x, seed_y = np.rint(point['xy']).astype(int)
        local_seed = (seed_y-sl[0].start, seed_x-sl[1].start)
        connected_id = connected[local_seed]
        if not connected_id:
            excluded.append(dict(point, reason='Seed unsupported after diffuse/radius guard'))
            candidate[sl][original_mask] = 0
            continue
        mask = connected == connected_id
        candidate[sl][original_mask & ~mask] = 0
        distance = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
        # Integer-distance ties otherwise discard a whole one-pixel ring,
        # often 20–30% of a small visible face. Rank tied rim pixels by their
        # diffuse brightness and dark-valley evidence instead. This is a
        # candidate retention preference, never a measurement of photo recall.
        confidence = distance+.25*diffuse_value[sl]/max(float(np.quantile(vv,.90)),.02)-.25*valley[sl]
        threshold = float(np.quantile(confidence[mask], 1-target_candidate_fraction))
        core = mask & (distance >= minimum_inset) & (confidence >= threshold)
        _, component_count = ndi.label(core)
        if not core.any():
            excluded.append(dict(point, reason='No inset core')); candidate[sl][mask] = 0; continue
        retained[sl][core] = ident
        y0, x0 = sl[0].start, sl[1].start
        coordinates = np.argwhere(core)[:, ::-1]+[x0, y0]
        perimeter = find_boundaries(mask, mode='inner')
        local_valley = valley[sl][perimeter]
        ridged = float(np.mean(local_valley > .18)) if len(local_valley) else 0.
        rows.append(dict(region_number=ident,
            observation_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f'{digest}:broad-region:{point["xy"]}')),
            seed_xy=point['xy'], seed_source=point['source'], appearance_mode=point['appearance_mode'],
            learned_hue_degrees=float(modes[point['appearance_mode']-1]),
            display_color='red' if hue_distance(modes[point['appearance_mode']-1], 0) < 20 else
                          'yellow' if hue_distance(modes[point['appearance_mode']-1], 45) < 25 else 'learned color family',
            candidate_pixels=int(mask.sum()), retained_pixels=int(core.sum()),
            retained_fraction_of_candidate=float(core.sum()/mask.sum()),
            raw_watershed_pixels=int(original_mask.sum()), seed_retained=bool(core[local_seed]),
            confidence_threshold=threshold, minimum_inset_pixels=minimum_inset,
            retained_components=int(component_count),
            candidate_dark_floor=floor if use_dark_valleys else None,
            candidate_dark_perimeter_fraction=ridged, retained_centroid_xy=coordinates.mean(axis=0).tolist(),
            bounding_box=[x0, y0, sl[1].stop, sl[0].stop],
            boundary_status='dark/color-supported proposal; exact photo boundary unverified',
            bead_index=None, reflection_numbers=[],
            status='unreviewed broad-region proposal; no one-region-per-bead guarantee'))
    row_by_id = {r['region_number']: r for r in rows}
    for reflection in reflection_rows:
        counts = {}
        for y, lo, hi in reflection['pixel_runs']:
            for owner in candidate[y, lo:hi+1]:
                if owner in row_by_id:
                    counts[int(owner)] = counts.get(int(owner), 0)+1
        if counts:
            owner = max(counts, key=counts.get)
            if counts[owner]/reflection['pixels'] >= .8:
                reflection['owner_region'] = owner
                reflection['association_status'] = 'Tentative candidate-mask ownership, not maker confirmation'
                row_by_id[owner]['reflection_numbers'].append(reflection['reflection_number'])
    boundary_band = (candidate > 0) & (retained == 0)
    report = dict(request='R215', image_sha256=digest, source_size=list(image.shape[1::-1]),
        coordinate_system='EXIF-oriented native pixel centers; x right, y down; H degrees circular; S/V 0–1',
        parameters=dict(detector=detected['parameters'], native_diameter=diameter, method='dark-valley watershed' if use_dark_valleys else 'color-distance watershed',
            palette_halfwidth_degrees=25, minimum_background_score_fraction=.60,
            maximum_automatic_seed_shift_diameters=.18,
            native_core_peak_spacing_diameters=.40, native_core_minimum_radius_diameters=.08,
            seed_band_clearance_diameters=.15,
            diffuse_floor_fraction=.32, maximum_seed_radius_diameters=.85, minimum_inset_pixels=minimum_inset,
            target_retained_fraction_of_candidate=target_candidate_fraction, reflection=reflection_params),
        learned_background_hue_degrees=bg_hue, records=rows, reflections=reflection_rows,
        excluded=excluded, attached_colored_reflection_numbers=attached_reflections,
        counts=dict(regions=len(rows), candidate_pixels=int((candidate > 0).sum()),
            retained_pixels=int((retained > 0).sum()), boundary_band_pixels=int(boundary_band.sum()),
            reflections=len(reflection_rows), associated_colored_reflections=sum(r['owner_region'] is not None for r in reflection_rows),
            broad_color_domain_pixels=int(domain.sum()), unassigned_domain_pixels=int((domain & (candidate == 0)).sum())),
        target_actual_visible_pixel_coverage=[.70, .90], actual_photo_visible_pixel_coverage=None,
        manual_labels_used=False, adjacency_computed=False, model_or_saved_spline_used=False,
        fit_performed=False, status='Proposal basis pending pixel-coverage/ownership review')
    arrays = dict(candidate=candidate, retained=retained, boundary_band=boundary_band,
                  diffuse_retained=np.where(reflections > 0, 0, retained),
                  reflections=reflections, domain=domain, valley=valley.astype(np.float32), family=family.astype(np.uint8))
    return report, arrays


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=auto.ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/output/r215')
    parser.add_argument('--candidate-fraction', type=float, default=.90)
    args = parser.parse_args()
    image = np.asarray(ImageOps.exif_transpose(Image.open(args.image)).convert('RGB'))
    report, arrays = segment(image, auto.sha(args.image), target_candidate_fraction=args.candidate_fraction)
    args.output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output/'pixel-masks.npz', **arrays)
    (args.output/'segmentation.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(report['counts']), flush=True)


if __name__ == '__main__':
    main()
