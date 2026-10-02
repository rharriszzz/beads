"""R201/R202: image-only distributed conservative colored interior proposals.

Safe interiors are accepted task targets. No black proposals are selected.
Manual marks, saved splines, model coordinates and fixed color boxes are absent.
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-auto-mpl')
import uuid
import numpy as np
from scipy.spatial import cKDTree
from matplotlib.colors import rgb_to_hsv

import auto_label_beads as auto
from bead_evidence_inventory import inventory, hue_distance
from colored_bead_centers import balanced_subset


def detect_distributed_interiors(image, digest, target=300, brightness_quantile=.20, spacing_factor=1.25):
    if not 0 <= brightness_quantile <= .5 or not 0 <= spacing_factor <= 2:
        raise ValueError('Use brightness quantile 0–0.5 and spacing factor 0–2')
    data = inventory(image)
    detector = auto.detect(image)
    route = detector['axis']['xy']
    arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(np.vstack([route, route[:1]]), axis=0), axis=1))]
    tree = cKDTree(route)
    hsv = rgb_to_hsv(np.asarray(image, float)/255)
    modes = data['parameters']['detector']['hue_modes_degrees']
    records = []
    for original in data['records']:
        if original['kind'] != 'chromatic':
            continue
        row = dict(original)
        x, y = row['seed_xy']
        row['observation_id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{digest}:automatic:{x:.3f}:{y:.3f}'))
        row['bead_index'] = None
        row['safe_interior_status'] = 'excluded or uncertain'
        row['quality_reasons'] = []
        region = row.get('region')
        if row['status'] != 'region-proposal' or region is None:
            row['quality_reasons'].append(row.get('reason', 'No supported colored interior'))
            row['source_xy'] = list(row['seed_xy'])
        else:
            pixels = np.array([(x, y) for y, lo, hi in region['pixel_runs'] for x in range(lo, hi+1)])
            values = hsv[pixels[:, 1], pixels[:, 0]]
            # A small unweighted positive-patch centroid, not a full-face center.
            row['source_xy'] = pixels.mean(axis=0).tolist()
            parameters = row['parameters']
            hue_error = hue_distance(values[:, 0]*360, modes[row['appearance_mode']-1])
            strong = (hue_error <= 18) & (values[:, 1] >= parameters['saturation_floor']*1.05)
            strong &= values[:, 2] >= parameters['value_floor']*1.10
            fraction = float(strong.mean())
            row['appearance_stability'] = dict(stronger_support_fraction=fraction,
                median_hue_error_degrees=float(np.median(hue_error)),
                hue_error_p90_degrees=float(np.quantile(hue_error, .90)),
                median_saturation=float(np.median(values[:, 1])), median_value=float(np.median(values[:, 2])),
                rule='18 degree learned-mode tolerance, local S floor x1.05, local V floor x1.10')
            if fraction < .95:
                row['quality_reasons'].append('positive patch does not survive modest stricter appearance test')
            x, y = np.rint(row['source_xy']).astype(int)
            if not np.any(np.all(pixels == [x, y], axis=1)):
                row['quality_reasons'].append('positive-patch centroid falls outside positive pixels')
            if region['minimum_support_margin'] < 3 or region['pixels'] < 12:
                row['quality_reasons'].append('insufficient conservative interior support')
            if not row['quality_reasons']:
                row['safe_interior_status'] = 'supported colored-interior proposal'
            row['selection_cost'] = float(np.quantile(hue_error, .90)/18 +
                (1-fraction)*10 + 3/region['minimum_support_margin'])
        _, station = tree.query((np.array(row['source_xy'])+.5)*detector['scale']-.5)
        row['route_fraction'] = float(arc[station]/arc[-1])
        row['role'] = 'Positive-patch centroid and small interior loop; not full visible center or minor-outward point'
        row['confirmation'] = 'unreviewed automatic proposal; appearance clearance is not certified bead-seam clearance'
        # Generic selector accepts this quality field without treating original
        # inventory's region-proposal status as the later positional status.
        row['inventory_status'] = row['status']
        row['status'] = row['safe_interior_status']
        records.append(row)
    # Prefer the visibly bright colored parts. A low, uniform, same-hue patch
    # can be a shaded fragment/seam rather than a trustworthy substantial body.
    # Estimate this conservative sampling preference separately for each learned
    # appearance family; no fixed photo V cutoff or rendered truth is used.
    floors = {}
    for mode in range(1, len(modes)+1):
        candidates = [r for r in records if r['appearance_mode']==mode and
                      r['status']=='supported colored-interior proposal']
        if not candidates:
            continue
        floors[mode] = float(np.quantile([r['appearance_stability']['median_value'] for r in candidates], brightness_quantile))
        for row in candidates:
            if row['appearance_stability']['median_value'] < floors[mode]:
                row['status'] = 'excluded or uncertain'
                row['safe_interior_status'] = 'appearance-supported but excluded by conservative brightness preference'
                row['quality_reasons'].append('below learned-family brightness quantile; conservative subset preference')
    # Sparse positional sampling avoids selecting nearby alternate patches as
    # independent anchors. It does NOT merge them or prove same/different beads.
    separation = data['parameters']['native_diameter']*spacing_factor
    selected, available = balanced_subset(records, target=target,
        accepted_status='supported colored-interior proposal', minimum_separation=separation)
    for row in records:
        row['selected'] = row['observation_number'] in selected
    return dict(request='R201/R202', image_sha256=digest, source_size=list(np.asarray(image).shape[1::-1]),
        records=records, selected_numbers=selected, available_per_bin=available,
        selected_per_bin=np.histogram([r['route_fraction'] for r in records if r['selected']], bins=np.linspace(0, 1, 21))[0].tolist(),
        parameters=dict(inventory=data['parameters'], target=target, image_arc_bins=20,
            stronger_support_minimum_fraction=.95, point_role='Interior reference, not visible-part center',
            minimum_selected_spacing_pixels=separation, minimum_selected_spacing_diameters=spacing_factor,
            brightness_quantile=brightness_quantile,
            spacing_role='Sparse sample preference, not bead identity or an estimated bead count'),
        learned_family_value_floors=floors,
        excluded_black_records=sum(r['kind']!='chromatic' for r in data['records']),
        centerline_changed=False, fit_performed=False, black_beads_included=False,
        complete=False, coverage='Distributed colored-only subset; ambiguous and unselected colored observations retained')
