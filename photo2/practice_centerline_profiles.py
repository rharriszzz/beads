"""R203: assisted 1D HSV practice on the existing centerline, without a fit.

Marker/spline references select diagnostic paths, not automatic runtime priors.
Brightness extrema, hue drift and dark/glint features are hypotheses only.
"""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-profile-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from matplotlib.transforms import Affine2D
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from scipy.interpolate import splprep, splev
from scipy.signal import find_peaks
from scipy.spatial import cKDTree

import auto_label_beads as auto
from label_beads import atomic_json


def sample_path(rgb, xy):
    """Bilinear encoded RGB first, HSV conversion second; no hue interpolation."""
    samples = np.column_stack([ndi.map_coordinates(rgb[:, :, k], [xy[:, 1], xy[:, 0]],
        order=1, mode='nearest') for k in range(3)])
    return samples, rgb_to_hsv(samples)


def periodic_route(points, step=1.):
    curve = np.asarray(points, float)
    if np.linalg.norm(curve[0]-curve[-1]) < 1e-6:
        curve = curve[:-1]
    curve = np.vstack([curve, curve[0]])
    tck, _ = splprep(curve.T, s=len(curve)*2**2, per=True, k=3)
    dense = np.array(splev(np.linspace(0, 1, 16385), tck)).T
    arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))]
    stations = np.arange(0, arc[-1], step)
    xy = np.column_stack([np.interp(stations, arc, dense[:, a]) for a in [0, 1]])
    tangent = np.roll(xy, -1, axis=0)-np.roll(xy, 1, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    return stations, xy, np.column_stack([-tangent[:, 1], tangent[:, 0]])


def extrema(values, diameter):
    smooth = ndi.gaussian_filter1d(values, max(.6, diameter*.06), mode='wrap')
    residual = values-smooth
    noise = float(np.median(abs(residual-np.median(residual)))*1.4826)
    prominence = max(.03, noise*3)
    bright, _ = find_peaks(smooth, prominence=prominence, distance=max(2, round(diameter*.15)))
    dark, _ = find_peaks(-smooth, prominence=prominence, distance=max(2, round(diameter*.15)))
    return smooth, bright, dark, dict(sigma_pixels=max(.6, diameter*.06), prominence=prominence,
        median_residual_mad=noise, role='Brightness landmarks, not certified seams or one peak per bead')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/review/r203')
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    photo = auto.ROOT/'beads-photo-2.jpg'
    seed_path = auto.ROOT/'photo2/spline-seed-r175.json'
    center_path = auto.ROOT/'photo2/review/r200/centers.json'
    image = ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    rgb = np.asarray(image, dtype=float)/255
    detected = auto.detect(np.asarray(image))
    diameter = detected['diameter']/np.sqrt(np.prod(detected['scale']))
    modes = detected['parameters']['hue_modes_degrees']
    stations, xy, normal = periodic_route(json.loads(seed_path.read_text())['points'])
    offsets = [-diameter*.20, 0., diameter*.20]
    routes = []
    for offset in offsets:
        coords = xy+offset*normal
        color, hsv = sample_path(rgb, coords)
        smooth, bright, dark, params = extrema(hsv[:, 2], diameter)
        routes.append(dict(offset=float(offset), xy=coords, rgb=color, hsv=hsv, smooth=smooth,
                           bright=bright, dark=dark, parameters=params))
    # Full whole-loop raw samples are reproducible routine output, not a new
    # outline or centerline. Preserve exact coordinates and sample units.
    routine = auto.ROOT/'photo2/output/r203'; routine.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(routine/'profiles.npz', stations=stations, center_xy=xy,
        offsets=offsets, rgb=np.array([r['rgb'] for r in routes]), hsv=np.array([r['hsv'] for r in routes]))
    marks = json.loads(center_path.read_text())['points']
    sections = []
    for name, number in [('top', 4), ('right', 25), ('inward-bend', 34)]:
        mark = next(p for p in marks if p['number']==number)
        middle = cKDTree(xy).query([mark['x'], mark['y']])[1]
        indices = (np.arange(middle-140, middle+141) % len(stations)).astype(int)
        distance = np.arange(-140, 141)
        points = xy[indices]
        direction = points[-1]-points[0]
        angle = -float(np.arctan2(direction[1], direction[0]))
        display_transform = Affine2D().rotate_around(*xy[middle], angle)
        display_points = display_transform.transform(points)
        lo, hi = display_points.min(axis=0)-45, display_points.max(axis=0)+45
        fig = plt.figure(figsize=(13, 10), layout='constrained')
        axes = fig.subplot_mosaic([['raw', 'path'], ['strip', 'strip'], ['value', 'value'],
                                  ['sat', 'sat'], ['hue', 'hue']], height_ratios=[2.5, .45, 1.5, 1., 1.5])
        for key in ['raw', 'path']:
            ax = axes[key]; ax.imshow(image, transform=display_transform+ax.transData)
            ax.set_xlim(lo[0], hi[0]); ax.set_ylim(hi[1], lo[1]); ax.axis('off')
        for route, color in zip(routes, ['#20a060', 'cyan', '#f29922']):
            coords = display_transform.transform(route['xy'][indices])
            axes['path'].plot(*coords.T, color=color, lw=.8)
            label = f"offset {route['offset']:+.1f}px"
            axes['value'].plot(distance, route['hsv'][indices, 2], color=color, lw=1, label=label)
            axes['sat'].plot(distance, route['hsv'][indices, 1], color=color, lw=.8)
        main = routes[1]
        axes['raw'].set_title('Raw photo, rotated for path alignment')
        axes['path'].set_title('Cyan spline, ±5.4px alternatives; ticks in pixels')
        for distance_tick in [-140, -100, -50, 0, 50, 100, 140]:
            p = display_points[distance_tick+140]
            axes['path'].plot(*p, '.', color='white', ms=3)
            axes['path'].text(p[0], p[1]+18, str(distance_tick), fontsize=7,
                color='white', ha='center', bbox=dict(facecolor='black', alpha=.6, pad=1))
        question_points = []
        if name == 'right':
            for letter, location in [('P', -110), ('S', 0), ('Q', 20), ('R', 109)]:
                k = location+140; p = display_points[k]
                for key in ['raw', 'path']:
                    axes[key].annotate(letter, p, xytext=(p[0], p[1]-30), color='white',
                        fontsize=11, ha='center', bbox=dict(facecolor='black', alpha=.8, pad=2),
                        arrowprops=dict(arrowstyle='->', color='cyan', lw=.8))
                for key in ['value', 'sat', 'hue']:
                    axes[key].axvline(location, color='#506070', lw=.6, ls=':')
                question_points.append(dict(label=letter, distance_pixels=location,
                    xy=points[k].tolist(), rgb=main['rgb'][indices[k]].tolist(), hsv=main['hsv'][indices[k]].tolist()))
        axes['strip'].imshow(main['rgb'][indices][None, :, :], extent=[-140, 140, 0, 1], aspect='auto')
        axes['strip'].set_yticks([]); axes['strip'].set_title('Encoded RGB sampled on cyan path')
        for kind, symbol, color in [('bright', '^', '#bb0077'), ('dark', 'v', '#222222')]:
            selected = [i for i, index in enumerate(indices) if index in set(main[kind])]
            axes['value'].scatter(distance[selected], main['hsv'][indices[selected], 2], marker=symbol,
                color=color, s=20, zorder=4, label=kind+' landmark')
        hue = (main['hsv'][indices, 0]*360+180) % 360-180
        axes['hue'].scatter(distance, hue, c=main['rgb'][indices], s=8)
        for mode in modes:
            axes['hue'].axhline((mode+180)%360-180, color='gray', lw=.6, ls='--')
        axes['value'].set_ylabel('V (0–1)'); axes['sat'].set_ylabel('S (0–1)')
        axes['hue'].set_ylabel('H (degrees, wrapped)')
        axes['hue'].set_ylim(-90, 60)
        axes['hue'].set_title('Hue unreliable on neutral/dark features; clipped display range, full values saved')
        axes['value'].legend(ncol=5, fontsize=8, loc='upper right')
        for key in ['value', 'sat', 'hue']:
            axes[key].set_xlim(-140, 140); axes[key].grid(alpha=.2)
        axes['hue'].set_xlabel('Distance along base spline (native photo pixels); zero beside saved center '+str(number))
        fig.suptitle(name+': 1D practice, not bead boundaries or fitted geometry')
        fig.savefig(args.output/(name+'.png'), dpi=130); plt.close(fig)
        sections.append(dict(name=name, reference_maker_center=number,
            display_rotation_degrees=float(np.degrees(angle)), question_points=question_points,
            sample_indices=indices.tolist(), coordinates=points.tolist(), rgb=main['rgb'][indices].tolist(),
            hsv=main['hsv'][indices].tolist(), bright_landmark_indices=[int(i) for i in indices if i in set(main['bright'])],
            dark_landmark_indices=[int(i) for i in indices if i in set(main['dark'])]))
    report = dict(request='R203', role='Assisted 1D practice; old spline and maker marks select routes/sections only',
        coordinates='EXIF-oriented pixels, x right/y down; bilinear encoded RGB then HSV',
        sample_step_pixels=1, circumference_image_pixels=float(stations[-1]+1), samples_per_route=len(stations),
        learned_hue_modes_degrees=modes, offsets_pixels=offsets, smoothing=routes[1]['parameters'],
        sections=sections, labels_inferred=False, geometry_changed=False,
        limitations=['One path crosses a succession of surface pieces, not necessarily bead centers.',
            'Low V can be black, seam or shade; bright low-S spots can be glints on any color.',
            'A hue drift alone is not a certified edge; nearby offset paths test sensitivity.',
            'No peaks are assigned full-string indices or exact ownership.'])
    atomic_json(args.output/'report.json', report)
    sources = ['beads-photo-2.jpg', 'photo2/practice_centerline_profiles.py', 'photo2/spline-seed-r175.json',
        'photo2/review/r200/centers.json', 'photo2/auto_label_beads.py']
    # Curator answer records share this folder but are not generator outputs.
    generated = ['report.json']+[section['name']+'.png' for section in sections]
    atomic_json(args.output/'summary.json', dict(source_sha256={p:auto.sha(auto.ROOT/p) for p in sources},
        curated_sha256={name:auto.sha(args.output/name) for name in sorted(generated)},
        reproduction='.venv/bin/python photo2/practice_centerline_profiles.py', geometry_changed=False))
    print(json.dumps(dict(sections=[s['name'] for s in sections], samples=len(stations), offsets=offsets)))


if __name__ == '__main__':
    main()
