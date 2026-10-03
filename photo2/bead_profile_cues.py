"""Local parallel RGB/HSV traces; feature hypotheses, never bead identities.

The image-derived strip axis supplies orientation only. An interior reference
is the origin, not a claimed bead center. No maker points or geometry are used.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from scipy.spatial import cKDTree

import auto_label_beads as auto
from practice_centerline_profiles import sample_path


def circular_mean(hue, weight):
    vector = np.sum(weight*np.exp(2j*np.pi*hue))
    total = float(np.sum(weight))
    if total <= 1e-12:
        return 0., 0.
    return float(np.angle(vector)), float(abs(vector)/total)


def trace_cues(hsv, diameter):
    """Measure V troughs, chroma-weighted hue changes and neutral bright peaks."""
    hsv = np.asarray(hsv, float)
    sigma = max(.6, diameter*.06)
    value = ndi.gaussian_filter1d(hsv[:, 2], sigma, mode='nearest')
    saturation = ndi.gaussian_filter1d(hsv[:, 1], sigma, mode='nearest')
    residual = hsv[:, 2]-value
    noise = float(np.median(abs(residual-np.median(residual)))*1.4826)
    minimum_distance = max(2, round(diameter*.15))
    prominence = max(.03, 3*noise)  # R203 generic landmark rule; not fitted to S/Q.
    troughs, trough_properties = find_peaks(-value, distance=minimum_distance, prominence=prominence)
    near, far = max(1, round(diameter*.12)), max(2, round(diameter*.35))
    hue_change = np.zeros(len(hsv)); hue_score = np.zeros(len(hsv))
    chroma = hsv[:, 1]*hsv[:, 2]
    for i in range(far, len(hsv)-far):
        left = slice(i-far, i-near+1); right = slice(i+near, i+far+1)
        a, ra = circular_mean(hsv[left, 0], chroma[left])
        b, rb = circular_mean(hsv[right, 0], chroma[right])
        delta = float(np.angle(np.exp(1j*(b-a))))
        hue_change[i] = np.degrees(delta)
        hue_score[i] = abs(delta)/np.pi*min(chroma[left].mean(), chroma[right].mean())*min(ra, rb)
    hue_peaks, _ = find_peaks(hue_score, distance=minimum_distance, prominence=.01)
    neutral_score = value*(1-saturation)
    neutral_peaks, _ = find_peaks(neutral_score, distance=minimum_distance, prominence=prominence)
    events = []
    for kind, indices in [('V trough', troughs), ('hue change', hue_peaks), ('neutral bright feature', neutral_peaks)]:
        for k, i in enumerate(indices):
            shoulder = np.r_[value[max(0,i-far):max(0,i-near)+1], value[i+near:min(len(value),i+far+1)]]
            background = float(np.median(shoulder)) if len(shoulder) else float(value[i])
            event = dict(kind=kind, sample_index=int(i), value=float(hsv[i, 2]), saturation=float(hsv[i, 1]),
                signed_hue_change_degrees=float(hue_change[i]), hue_score=float(hue_score[i]),
                neutral_score=float(neutral_score[i]), shoulder_value=background,
                brightness_contrast=float(value[i]-background), status='Feature hypothesis; ownership unresolved')
            if kind=='V trough':
                event['value_prominence'] = float(trough_properties['prominences'][k])
            events.append(event)
    return dict(events=sorted(events, key=lambda e:(e['sample_index'],e['kind'])),
        smooth_value=value.tolist(), smooth_saturation=saturation.tolist(),
        signed_hue_change_degrees=hue_change.tolist(), hue_score=hue_score.tolist(), neutral_score=neutral_score.tolist(),
        parameters=dict(sigma_pixels=sigma, value_prominence=prominence, residual_mad=noise,
            hue_score_prominence=.01, hue_side_window_pixels=[near,far], minimum_event_spacing_pixels=minimum_distance,
            hue_weight='HSV S*V (RGB chroma), multiplied by both circular resultants',
            hue_score='abs(circular hue difference)/pi * lesser mean side chroma * lesser side resultant',
            neutral_role='Bright low-S appearance on any body/background; not a black-bead classifier'))


def parallel_cues(rgb, coordinates, diameter, offsets, middle):
    """Input coordinates have shape (paths, stations, 2); no labels consulted."""
    paths = []
    for offset, xy in zip(offsets, coordinates):
        color, hsv = sample_path(rgb, np.asarray(xy))
        result = trace_cues(hsv, diameter)
        for e in result['events']:
            e.update(distance_pixels=e['sample_index']-middle, xy=np.asarray(xy[e['sample_index']]).tolist())
        paths.append(dict(offset_pixels=float(offset), coordinates=np.asarray(xy).tolist(),
            rgb=color.tolist(), hsv=hsv.tolist(), **result))
    base = next(p for p in paths if p['offset_pixels']==0)
    tolerance = diameter*.15
    for e in base['events']:
        matches = []
        peers = [r for r in base['events'] if r['kind']==e['kind']]
        for p in paths:
            candidates = [r for r in p['events'] if r['kind']==e['kind']]
            if not candidates: continue
            candidate = min(candidates,key=lambda r:abs(r['sample_index']-e['sample_index']))
            reverse = min(peers,key=lambda r:abs(r['sample_index']-candidate['sample_index']))
            if reverse is e and abs(candidate['sample_index']-e['sample_index'])<=tolerance:
                matches.append(dict(offset_pixels=p['offset_pixels'], sample_index=candidate['sample_index'],
                    distance_pixels=candidate['distance_pixels'], xy=candidate['xy']))
        e['parallel_matches'] = matches
        e['matched_paths'] = len(matches)
        e['persistence_role'] = 'Along-path proximity only; offset points may cross different bodies'
    return dict(paths=paths, base_path_index=paths.index(base), parallel_match_tolerance_pixels=tolerance,
        persistent_definition='Base event matches at least three of five paths within0.15 apparent diameters; not a seam certificate')


def local_profiles(image, inventory):
    """Annotate a frozen image-only interior set with image-derived local strips."""
    image = np.asarray(image, dtype=np.uint8)
    detector = auto.detect(image)
    axis = (np.asarray(detector['axis']['xy'])+.5)/detector['scale']-.5
    tangent = np.roll(axis,-1,axis=0)-np.roll(axis,1,axis=0)
    tangent /= np.linalg.norm(tangent,axis=1)[:,None]
    tree = cKDTree(axis)
    diameter = inventory['parameters']['inventory']['native_diameter']
    offsets = np.array([-.4,-.2,0.,.2,.4])*diameter
    half = round(diameter*2)
    distance = np.arange(-half,half+1)
    rgb = image.astype(float)/255
    rows = []
    for record in inventory['records']:
        if not record['selected']: continue
        origin = np.asarray(record['source_xy'])
        station = tree.query(origin)[1]; direction=tangent[station]
        normal = np.array([-direction[1],direction[0]])
        xy = origin+distance[None,:,None]*direction+offsets[:,None,None]*normal
        result=parallel_cues(rgb,xy,diameter,offsets,half)
        rows.append(dict(observation_number=record['observation_number'], observation_id=record['observation_id'],
            source_xy=record['source_xy'], appearance_mode=record['appearance_mode'], route_fraction=record['route_fraction'],
            tangent_xy=direction.tolist(), reference_role=record['role'], **result))
    return dict(records=rows, source_image_sha256=inventory['image_sha256'], native_diameter=diameter,
        offsets_pixels=offsets.tolist(), distance_pixels=distance.tolist(),
        route_role='Image-derived axis orientation; straight local parallel strips through existing interior references',
        automatic_body_labels_added=False, fitting_performed=False, selected_set_modified=False)
