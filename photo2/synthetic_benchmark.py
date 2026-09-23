#!/usr/bin/env python3
"""POV-Ray occlusion benchmark, not a photo fit or continuous inverse solver."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
import platform
from pathlib import Path
import subprocess

import numpy as np
import scipy
from PIL import Image, ImageDraw, __version__ as pillow_version
from scipy.ndimage import distance_transform_edt
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist, pdist

from reconstruct import HERE, ROOT, digest

WIDTH, HEIGHT, SCALE = 160, 70, 3
ROI_X = 60
MIN_PIXELS = 12


@dataclass(frozen=True)
class Geometry:
    hand: int = 1
    pitch: float = 26.
    count: float = 6.5
    radius: float = 18.
    phase: float = .37
    bead_radius: float = 7.
    height_ratio: float = .65
    tilt_degrees: float = 20.
    twist: float = 0.  # radians per axial unit


def layout(g):
    spacing = g.pitch / g.count
    # Fixed axial padding excludes truncation effects from the central ROI.
    k = np.arange(int(np.floor(-100 / spacing)), int(np.ceil(100 / spacing))+1)
    x = k * spacing
    theta = g.hand * 2*np.pi*k/g.count + g.phase + g.twist*x
    positions = np.column_stack([x, g.radius*np.sin(theta), g.radius*np.cos(theta)])
    tilt = np.deg2rad(g.tilt_degrees)
    axes = np.column_stack([np.full(len(k), np.cos(tilt)),
                            np.sin(tilt)*np.cos(theta), -np.sin(tilt)*np.sin(theta)])
    # Map the macro's local y (hole axis) to axes with a proper rotation.
    bx = np.cross(axes, [0., 0., 1.])
    bx /= np.linalg.norm(bx, axis=1)[:, None]
    bz = np.cross(bx, axes)
    colors = (np.arange(1, len(k)+1)[:, None] * [73,151,199]) % 251 + 1
    return {'k':k, 'positions':positions, 'axes':axes, 'bx':bx, 'bz':bz,
            'colors':colors.astype(np.uint8), 'theta':theta}


def candidates(truth):
    new_count = 8.
    spacing = truth.pitch/truth.count
    gauge = replace(truth, count=new_count, pitch=spacing*new_count,
                    twist=truth.hand*2*np.pi*(1/truth.count-1/new_count)/spacing)
    return {
        'truth':truth,
        'opposite_hand':replace(truth, hand=-truth.hand),
        'depth_reflection':replace(truth, hand=-truth.hand, phase=np.pi-truth.phase,
                                   tilt_degrees=-truth.tilt_degrees),
        'gauge_equivalent':gauge,
        'double_density_stress':replace(truth, count=2*truth.count),
        'pitch_+10pct':replace(truth, pitch=1.1*truth.pitch),
        'count_7.5':replace(truth, count=7.5),
        'radius_+15pct':replace(truth, radius=1.15*truth.radius),
        'body_-20pct':replace(truth, bead_radius=.8*truth.bead_radius),
        'height_+25pct':replace(truth, height_ratio=1.25*truth.height_ratio),
        'tilt_zero':replace(truth, tilt_degrees=0.),
        'tilt_reversed':replace(truth, tilt_degrees=-truth.tilt_degrees),
    }


def write_include(directory, g, data):
    def vector(v):
        return '<'+','.join(f'{a:.14g}' for a in v)+'>'
    lines = [f'#declare ViewWidth={WIDTH};', f'#declare ViewHeight={HEIGHT};',
             f'#declare BeadCount={len(data["k"])};',
             f'#declare bead_radius={g.bead_radius};', '#declare hole_size_per_bead_size=0.3;',
             f'#declare HeightRatio={g.height_ratio};']
    for name, key, factor in [('Positions','positions',1), ('Axes','axes',1),
                              ('BasisX','bx',1), ('BasisZ','bz',1), ('IDColors','colors',1/255)]:
        lines.append(f'#declare {name}=array[BeadCount] {{'+
                     ','.join(vector(v*factor) for v in data[key])+'};')
    (directory/'patch-data.inc').write_text('\n'.join(lines)+'\n')


def render(directory, name, commands, only=-1, beauty=False):
    output = directory/f'{name}.png'
    command = ['povray', f'+I{HERE/"synthetic-patch.pov"}', f'+L{directory}',
               f'+L{ROOT}', f'+O{output}', f'+W{WIDTH*SCALE}', f'+H{HEIGHT*SCALE}',
               '+FN8', '-D', '-A', '-J', '+WT2', 'File_Gamma=1.0', 'Dither=Off',
               f'Declare=Only={only}', f'Declare=Beauty={int(beauty)}']
    with (directory/f'{name}.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    commands.append(command)
    return np.asarray(Image.open(output).convert('RGB'))


def decode(rgb, colors):
    def packed(a):
        a = a.astype(np.int64)
        return (a[..., 0]<<16) + (a[..., 1]<<8) + a[..., 2]
    pixels = packed(rgb)
    ids = np.zeros(pixels.shape, dtype=np.int32)
    known = pixels == 0
    for i, color in enumerate(packed(colors), 1):
        mask = pixels == color
        ids[mask] = i
        known |= mask
    if not known.all():
        raise ValueError(f'Non-ID colors in mask: {np.unique(pixels[~known])[:10]}')
    return ids


def roi():
    x = (np.arange(WIDTH*SCALE)+.5)/SCALE-WIDTH/2
    return np.broadcast_to(np.abs(x)[None, :] < ROI_X, (HEIGHT*SCALE, WIDTH*SCALE))


def boundaries(ids):
    """Foreground pixels touching another instance/background; no numeric ID scoring."""
    edge = np.zeros_like(ids, dtype=bool)
    change = ids[1:] != ids[:-1]
    edge[1:] |= change
    edge[:-1] |= change
    change = ids[:,1:] != ids[:,:-1]
    edge[:,1:] |= change
    edge[:,:-1] |= change
    return edge & (ids > 0)


def visible_centers(ids, data):
    counts = np.bincount(ids.ravel(), minlength=len(data['k'])+1)[1:]
    keep = (counts >= MIN_PIXELS) & (np.abs(data['positions'][:,0]) < ROI_X)
    ordinals = np.flatnonzero(keep)
    centroids = []
    for i in ordinals:
        row, col = np.nonzero(ids == i+1)
        centroids.append([(col.mean()+.5)/SCALE-WIDTH/2,
                          HEIGHT/2-(row.mean()+.5)/SCALE])
    return ordinals, data['positions'][keep,:2], np.array(centroids).reshape(-1,2), counts


def center_rmse(observed, predicted):
    if not len(observed):
        raise ValueError('No observed centers')
    if len(predicted) < len(observed):
        return None  # Infeasible; do not hide missing matches in a finite sentinel.
    costs = cdist(observed, predicted, 'sqeuclidean')
    rows, cols = linear_sum_assignment(costs)
    return float(np.sqrt(costs[rows, cols].mean()))


def outline_scores(observed, predicted):
    a, b = boundaries(observed) & roi(), boundaries(predicted) & roi()
    da, db = distance_transform_edt(~a)/SCALE, distance_transform_edt(~b)/SCALE
    ma, mb = (observed>0)&roi(), (predicted>0)&roi()
    return {'silhouette_iou':float((ma&mb).sum()/(ma|mb).sum()),
            'boundary_symmetric_mean':float((db[a].mean()+da[b].mean())/2)}, db


def summaries(values):
    feasible = [v for v in values if v is not None]
    return {'feasible_trials':len(feasible), 'trials':len(values),
            'median':float(np.median(feasible)) if feasible else None,
            'min':float(min(feasible)) if feasible else None,
            'max':float(max(feasible)) if feasible else None}


def score_trials(target, models, seed):
    rng = np.random.default_rng(seed)
    ordinals, centers, centroids, _ = visible_centers(target['ids'], target['data'])
    report = {}
    for missing in [0., .5, .75]:
        for noise in [0., .75, 2.]:
            n = max(3, round(len(centers)*(1-missing)))
            samples = [(np.sort(rng.choice(len(centers), n, replace=False)),
                        rng.normal(0, noise, (n,2))) for _ in range(24)]
            scores = {}
            for name, model in models.items():
                _, pc, pm, _ = visible_centers(model['ids'], model['data'])
                model_edges = boundaries(model['ids']) & roi()
                distance = distance_transform_edt(~model_edges)/SCALE
                oracle, centroid, incomplete_edges = [], [], []
                for chosen, perturb in samples:
                    oracle.append(center_rmse(centers[chosen]+perturb, pc))
                    centroid.append(center_rmse(centroids[chosen]+perturb, pm))
                    # Missing instances become unknown, NOT background. Only retain
                    # their pre-existing visible boundaries; never create new edges.
                    observed_edge = boundaries(target['ids']) & roi()
                    observed_edge &= np.isin(target['ids'], ordinals[chosen]+1)
                    incomplete_edges.append(float(distance[observed_edge].mean()))
                scores[name] = {'oracle_center_rmse':summaries(oracle),
                               'mask_centroid_rmse':summaries(centroid),
                               'partial_boundary_one_way_mean':summaries(incomplete_edges),
                               'oracle_trials':oracle}
            # Retain ties rather than declaring a unique winner at truth's inclusion.
            wins = {name:0 for name in models}
            for trial in range(24):
                feasible = {name:v['oracle_trials'][trial] for name,v in scores.items()
                            if v['oracle_trials'][trial] is not None}
                best = min(feasible.values())
                for name, value in feasible.items():
                    if value <= best+1e-9:
                        wins[name] += 1
            report[f'missing={missing:g},noise={noise:g}'] = {
                'labels_kept':n, 'noise_std_per_coordinate':noise,
                'selected_bead_ids':[[int(target['data']['k'][ordinals[i]]) for i in chosen]
                                     for chosen, _ in samples],
                'oracle_best_including_ties':wins, 'candidates':scores}
    return report


def diagnostic_panel(output, hand, models):
    names = ['truth', 'depth_reflection', 'double_density_stress', 'tilt_zero']
    canvas = Image.new('RGB', (WIDTH*SCALE*2, (HEIGHT*SCALE+24)*len(names)), 'white')
    draw = ImageDraw.Draw(canvas)
    for row, name in enumerate(names):
        y = row*(HEIGHT*SCALE+24)
        draw.text((5,y+4), f'hand {hand:+d} / {name}: instance mask | boundary mismatch', fill='black')
        directory = output/f'hand{hand:+d}'/name
        canvas.paste(Image.open(directory/'ids.png'), (0,y+24))
        a, b = boundaries(models['truth']['ids']), boundaries(models[name]['ids'])
        rgb = np.zeros((*a.shape,3),dtype=np.uint8)
        rgb[a] = [255,60,60]
        rgb[b] = [60,220,255]
        rgb[a&b] = [255,255,255]
        canvas.paste(Image.fromarray(rgb), (WIDTH*SCALE,y+24))
    canvas.save(output/f'hand{hand:+d}-comparison.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'output/synthetic-benchmark')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    commands = []
    report = {'environment':{'python':platform.python_version(), 'numpy':np.__version__,
                            'scipy':scipy.__version__, 'pillow':pillow_version},
              'settings':{'view_width':WIDTH, 'view_height':HEIGHT, 'pixels_per_unit':SCALE,
                          'roi_abs_x_lt':ROI_X, 'min_visible_pixels':MIN_PIXELS,
                          'trial_seed':815, 'trials_per_condition':24,
                          'hole_radius_ratio':.3, 'roundedness':.8},
              'protocol':{
                  'units':'Synthetic world units; 3 raster pixels per unit, not photo-calibrated.',
                  'centers':'One-to-one assignment of unordered sets; extra model sites unpenalized. Null means insufficient predicted sites.',
                  'noise':'Independent Gaussian perturbations of each observed center coordinate only; outlines stay exact.',
                  'partial_outlines':'Randomly retain original visible boundaries by instance. Missing instances are unknown, never background. One-way observed-to-model distance.',
                  'complete_outlines':'Mean of the two directional mean boundary distances; all visible interfaces and hole rims included. Silhouette IoU separately.',
                  'registration':'Fixed camera, axial origin, phase and size except each stated alternative; no fitted nuisance parameters.'},
              'sources':{str(p.relative_to(ROOT)):digest(p) for p in
                         [HERE/'synthetic_benchmark.py', HERE/'synthetic-patch.pov',
                          HERE/'test_synthetic_benchmark.py', HERE/'reconstruct.py', ROOT/'bead-shape.inc']},
              'limitations':['Discrete alternatives with fixed registration; no continuous recovery.',
                             'Perfect instrumented masks, not segmentation of shaded images.',
                             'Straight orthographic synthetic patches only; no photo inference.',
                             'Known projected centers are oracle observations; centroids are separate.',
                             'Dense stress geometry can intersect and is not a physical hypothesis.',
                             'Gauge-equivalent parameterizations must remain ambiguous.'], 'hands':{}}
    for hand in [-1,1]:
        models = {}
        for name, g in candidates(Geometry(hand=hand)).items():
            directory = output/f'hand{hand:+d}'/name
            directory.mkdir(parents=True, exist_ok=True)
            data = layout(g)
            write_include(directory, g, data)
            rgb = render(directory, 'ids', commands)
            ids = decode(rgb, data['colors'])
            models[name] = {'ids':ids, 'data':data, 'geometry':g}
            print(f'rendered hand={hand:+d} {name}', flush=True)
        target = models['truth']
        data, ids = target['data'], target['ids']
        directory = output/f'hand{hand:+d}'/'truth'
        render(directory, 'beauty', commands, beauty=True)
        ordinals, centers, centroids, counts = visible_centers(ids, data)
        # Isolated renders use identical camera/pixel grid, giving exact fractions.
        isolated_counts = np.zeros(len(data['k']), dtype=int)
        for i in np.flatnonzero(np.abs(data['positions'][:,0]) < ROI_X):
            isolated = decode(render(directory, f'isolated-{i:03d}', commands, only=int(i)), data['colors'])
            isolated_counts[i] = (isolated==i+1).sum()
            if np.any((ids==i+1) & (isolated!=i+1)):
                raise AssertionError('Visible body pixels must belong to its isolated mask')
        truth_records = []
        for i, k in enumerate(data['k']):
            isolated = int(isolated_counts[i])
            truth_records.append({'bead_id':int(k), 'mask_id':i+1,
                                  'center_xyz':data['positions'][i].tolist(),
                                  'hole_axis':data['axes'][i].tolist(),
                                  'visible_pixels':int(counts[i]), 'isolated_pixels':isolated or None,
                                  'visible_fraction':float(counts[i]/isolated) if isolated else None,
                                  'in_center_observations':bool(i in ordinals),
                                  'front_half':bool(np.cos(data['theta'][i])>=0)})
        result = {'truth':truth_records, 'candidates':{},
                  'visible_center_count':len(centers),
                  'centroid_to_true_center_rmse':float(np.sqrt(np.mean(np.sum((centroids-centers)**2,axis=1))))}
        gauge_equal = np.array_equal(ids, models['gauge_equivalent']['ids'])
        reflected_silhouette_equal = np.array_equal(ids>0, models['depth_reflection']['ids']>0)
        if not gauge_equal or not reflected_silhouette_equal:
            raise AssertionError('Expected exact image invariants failed')
        result['diagnostics'] = {
            'gauge_mask_identical':gauge_equal,
            'depth_reflected_silhouette_identical':reflected_silhouette_equal,
            'back_half_observed_centers':sum(not truth_records[i]['front_half'] for i in ordinals),
            'partially_occluded_roi_bodies':sum(0<b['visible_fraction']<1 for b in truth_records
                                              if b['visible_fraction'] is not None)}
        for name, model in models.items():
            scores, _ = outline_scores(ids, model['ids'])
            _, pc, _, _ = visible_centers(model['ids'], model['data'])
            g = model['geometry']
            # Conservative enclosing sphere includes simultaneous radial/axial extent.
            bound = g.bead_radius*np.sqrt(1+g.height_ratio**2)
            separation = float(pdist(model['data']['positions']).min())
            result['candidates'][name] = {
                'geometry':asdict(g), 'visible_center_count':len(pc),
                'oracle_center_rmse':center_rmse(centers, pc), **scores,
                'min_center_separation':separation, 'enclosing_sphere_diameter':2*bound,
                'nonintersection_certified_by_spheres':bool(separation>2*bound)}
        result['trials'] = score_trials(target, models, seed=815)
        diagnostic_panel(output, hand, models)
        report['hands'][str(hand)] = result
        print(f'hand={hand:+d}: {len(centers)} visible centers; benchmark scored', flush=True)
    (output/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    # Bind all generated images/data, including isolated visibility masks.
    report['artifacts'] = {str(p.relative_to(output)):digest(p)
                           for p in sorted(output.rglob('*')) if p.suffix in {'.png','.inc'}}
    report['renderer_version'] = subprocess.run(['povray','--version'], capture_output=True,
                                               text=True).stderr
    (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(output/'report.json')


if __name__ == '__main__':
    main()
