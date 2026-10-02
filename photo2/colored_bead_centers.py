"""Image-only colored visible-part center estimates; no manual/model inputs.

Approximate colored support centroids, not physical centers or outward anchors.
Agreement under appearance perturbations is a quality diagnostic, not a proof.
Black beads are never proposed by this module.
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-auto-mpl')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.feature import peak_local_max
from skimage.measure import regionprops
from skimage.segmentation import watershed
from matplotlib.colors import rgb_to_hsv

import auto_label_beads as auto
from bead_evidence_inventory import encode_pixels, hue_distance

VARIANTS = [dict(name='reference', hue_width=24, saturation_factor=.70, value_factor=.45),
            dict(name='narrow', hue_width=20, saturation_factor=.80, value_factor=.52),
            dict(name='broad', hue_width=28, saturation_factor=.60, value_factor=.38)]


def segment_centers(hsv, foreground, band, band_distance, diameter, parameters, variant):
    """Separate colored regions using distance peaks; no same-hue bridge merge."""
    height, width = band.shape
    hue, saturation, value = hsv[:, :, 0]*360, hsv[:, :, 1], hsv[:, :, 2]
    local_value = ndi.gaussian_filter(value, diameter*.15)
    rows = []
    for mode_number, mode in enumerate(parameters['hue_modes_degrees'], 1):
        mask = foreground & band & (hue_distance(hue, mode) <= variant['hue_width'])
        mask &= saturation >= max(.15, parameters['saturation_floor']*variant['saturation_factor'])
        mask &= value >= np.maximum(parameters['background_value']*.12, local_value*variant['value_factor'])
        mask = auto.small_components(mask, max(12, int(diameter**2*.06)))
        distance = ndi.distance_transform_edt(mask)
        smooth = ndi.gaussian_filter(distance, max(.6, diameter/16))
        locations = peak_local_max(smooth, min_distance=max(3, int(diameter*.55)),
                                  threshold_abs=diameter*.12, labels=mask)
        markers = np.zeros(band.shape, np.int32)
        for number, (y, x) in enumerate(locations, 1):
            markers[y, x] = number
        regions = watershed(-smooth, markers, mask=mask)
        for prop in regionprops(regions):
            y, x = prop.centroid
            seed_y, seed_x = locations[prop.label-1]
            py, px = int(round(y)), int(round(x))
            clearance = float(band_distance[seed_y, seed_x])
            reasons = []
            if not .18*diameter**2 <= prop.area <= 1.05*diameter**2:
                reasons.append('colored area outside substantial single-body range')
            if prop.axis_minor_length < diameter*.35 or prop.axis_major_length > diameter*1.7:
                reasons.append('thin or oversized colored region')
            if clearance < diameter*.7:
                reasons.append('near approximate search-band edge')
            if regions[py, px] != prop.label or distance[py, px] < max(1.5, diameter*.06):
                reasons.append('centroid not safely inside its colored support')
            core = prop.coords[distance[prop.coords[:, 0], prop.coords[:, 1]] >= max(2., diameter*.10)]
            if len(core) < 12:
                reasons.append('insufficient colored interior support')
            core_center = core[:, ::-1].mean(axis=0) if len(core) else np.array([x, y])
            core_shift = float(np.linalg.norm(core_center-[x, y]))
            if core_shift > diameter*.12:
                reasons.append('full-support and interior centroids disagree')
            origin = np.array([prop.bbox[1], prop.bbox[0]])
            rows.append(dict(source_xy=[float(x), float(y)], seed_xy=[int(seed_x), int(seed_y)],
                appearance_mode=mode_number, support_area=int(prop.area),
                axis_minor_pixels=float(prop.axis_minor_length), axis_major_pixels=float(prop.axis_major_length),
                band_clearance_pixels=clearance, support_margin_pixels=float(distance[py, px]),
                interior_centroid_xy=core_center.tolist(), interior_centroid_shift_pixels=core_shift,
                support=dict(pixel_runs=encode_pixels(prop.image, origin), pixels=int(prop.area),
                    role='Appearance support estimate only, not a confirmed bead outline'),
                rejection_reasons=reasons))
    return rows


def stable_candidates(reference, alternatives, diameter):
    """Require mutual nearest same-mode counterparts in every alternative."""
    output = []
    for row in reference:
        current = dict(row)
        current['rejection_reasons'] = list(row['rejection_reasons'])
        matches = []
        peers = [r for r in reference if r['appearance_mode'] == row['appearance_mode']]
        for name, rows in alternatives:
            other = [r for r in rows if r['appearance_mode'] == row['appearance_mode']]
            if not other:
                current['rejection_reasons'].append(f'{name}: no matching colored region')
                continue
            distances = np.linalg.norm(np.array([r['source_xy'] for r in other])-row['source_xy'], axis=1)
            j = int(np.argmin(distances))
            chosen = other[j]
            back = np.linalg.norm(np.array([r['source_xy'] for r in peers])-chosen['source_xy'], axis=1)
            if peers[int(np.argmin(back))] is not row or distances[j] > diameter*.25:
                current['rejection_reasons'].append(f'{name}: region identity unstable under perturbation')
                continue
            shift = float(distances[j])
            area_ratio = chosen['support_area']/row['support_area']
            matches.append(dict(variant=name, xy=chosen['source_xy'], shift_pixels=shift, area_ratio=area_ratio))
            if shift > diameter*.08 or not .70 <= area_ratio <= 1.40:
                current['rejection_reasons'].append(f'{name}: appearance perturbation changes center/area too much')
            if chosen['rejection_reasons']:
                current['rejection_reasons'].append(f'{name}: alternative fails support-quality checks')
        current['alternatives'] = matches
        current['threshold_sensitivity_pixels'] = max([m['shift_pixels'] for m in matches], default=None)
        current['status'] = 'stable colored-center candidate' if not current['rejection_reasons'] else 'excluded or uncertain'
        output.append(current)
    return output


def balanced_subset(rows, bins=20, target=300, accepted_status='stable colored-center candidate', minimum_separation=0.):
    """Round-robin quality ranks across equal image-derived route arc bins."""
    groups = [[] for _ in range(bins)]
    for row in rows:
        if row['status'] == accepted_status:
            groups[min(int(row['route_fraction']*bins), bins-1)].append(row)
    for group in groups:
        group.sort(key=lambda r: (r['selection_cost'] if 'selection_cost' in r else
            r['threshold_sensitivity_pixels']+r['interior_centroid_shift_pixels'], r['observation_number']))
    selected = []
    chosen_xy = []
    rank = 0
    while len(selected) < target and any(len(g) > rank for g in groups):
        for group in groups:
            if len(group) > rank:
                row = group[rank]
                point = np.asarray(row['source_xy'])
                if minimum_separation and any(np.linalg.norm(point-other) < minimum_separation for other in chosen_xy):
                    continue
                selected.append(row['observation_number'])
                chosen_xy.append(point)
                if len(selected) == target:
                    break
        rank += 1
    return selected, [len(g) for g in groups]


def detect_colored_centers(image, target=300):
    """All decisions depend only on appearance and generic dimensional rules."""
    rgb = np.asarray(image, dtype=np.uint8)
    seed = auto.detect(rgb)
    size = rgb.shape[1::-1]
    parameters = seed['parameters']
    diameter = seed['diameter']/float(np.mean(seed['scale']))
    hsv = rgb_to_hsv(rgb.astype(np.float32)/255)
    band = np.asarray(Image.fromarray(seed['band']).resize(size, Image.Resampling.NEAREST), dtype=bool)
    # Recompute the learned background distance at native resolution.
    chromaticity = rgb[:, :, :2].astype(np.float32)/np.maximum(rgb.sum(axis=2, keepdims=True), 1)
    score = np.sqrt(np.sum(((chromaticity-parameters['background_chromaticity']) /
        np.maximum(parameters['background_mad'], .003))**2, axis=2))
    foreground = score > parameters['foreground_threshold']
    band_distance = ndi.distance_transform_edt(band)
    runs = [segment_centers(hsv, foreground, band, band_distance, diameter, parameters, v) for v in VARIANTS]
    rows = stable_candidates(runs[0], [(v['name'], r) for v, r in zip(VARIANTS[1:], runs[1:])], diameter)
    # Native coordinates -> detector coordinates use the same half-pixel rule.
    xy = (np.asarray([r['source_xy'] for r in rows])+.5)*seed['scale']-.5
    _, stations = cKDTree(seed['axis']['xy']).query(xy)
    route = seed['axis']['xy']
    arcs = np.r_[0., np.cumsum(np.linalg.norm(np.diff(np.vstack([route, route[:1]]), axis=0), axis=1))]
    for number, (row, station) in enumerate(zip(rows, stations), 1):
        row.update(observation_number=number, route_fraction=float(arcs[station]/arcs[-1]),
                   bead_index=None, role='Estimated visible colored-support centroid; not physical center/outward point')
    selected, available = balanced_subset(rows, target=target)
    for row in rows:
        row['selected'] = row['observation_number'] in selected
    return dict(records=rows, selected_numbers=selected, parameters=dict(detector=parameters,
        native_diameter=diameter, appearance_variants=VARIANTS, bins=20, target=target,
        centroid_sensitivity_limit_diameters=.08, edge_guard_diameters=.7),
        available_per_bin=available, selected_per_bin=np.histogram(
            [r['route_fraction'] for r in rows if r['selected']], bins=np.linspace(0, 1, 21))[0].tolist(),
        fit_performed=False, centerline_changed=False, black_beads_included=False)
