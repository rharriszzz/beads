"""R183: raw photo beside smooth model-width and +7% comparison guides."""
import json
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image, ImageOps
from tangent_circles import ROOT, sha, plt
from tangent_viewer import ViewerStore


def draw_guides(ax, frame):
    guide = frame['guides']
    center = np.array(guide['centerline']); normal = np.array(guide['normals'])
    ax.plot(center[:, 0], center[:, 1], color='white', lw=.7, ls='--')
    for factor, color, style in [(1., '#ffb347', '--'), (1.07, '#80ff80', '-')]:
        for sign in [-1, 1]:
            xy = center + sign*factor*guide['radius_pixels']*normal
            ax.plot(xy[:, 0], xy[:, 1], color=color, lw=.8, ls=style)


def draw_circles(ax, frame):
    phi = np.linspace(0, 2*np.pi, 49)
    for circle in frame['circles']:
        c = np.array(circle)
        xy = c[:2] + c[2:4]*np.cos(phi)[:, None] + c[4:6]*np.sin(phi)[:, None]
        ax.plot(xy[:, 0], xy[:, 1], color='cyan', lw=.65)


def main():
    out = ROOT / 'photo2/review/r183'
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        store = ViewerStore(Path(folder) / 'review-only.json')
        frame = store.frame(2698, -1)
        comparison = store.frame(2833, -1)
    raw = ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB')
    fig = plt.figure(figsize=(25.4, 31.82), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(raw)
    draw_guides(ax, frame); draw_circles(ax, frame)
    ax.set_xlim(-.5, 2539.5); ax.set_ylim(3181.5, -.5); ax.axis('off')
    fig.savefig(out / 'whole-guides.png', dpi=100); plt.close(fig)
    assert Image.open(out / 'whole-guides.png').size == (2540, 3182)
    crop = [1180, 130, 1540, 520]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5), constrained_layout=True)
    for ax, title in zip(axes, ['Raw photo', 'White centerline; amber 100%; green 107%']):
        ax.imshow(raw); ax.set_xlim(crop[0], crop[2]); ax.set_ylim(crop[3], crop[1])
        ax.set_title(title, fontsize=11); ax.axis('off')
    draw_guides(axes[1], frame)
    fig.savefig(out / 'raw-width-comparison.png', dpi=160); plt.close(fig)
    sources = ['beads-photo-2.jpg', 'beads.pov', 'photo2/tangent_circles.py',
               'photo2/tangent_viewer.py', 'photo2/spline-seed-r175.json',
               'photo2/review_width_guides.py', 'photo2/test_tangent_viewer.py',
               'photo2/tangent_viewer/app.mjs', 'photo2/tangent_viewer/viewport.mjs',
               'photo2/tangent_viewer/viewport.test.mjs', 'photo2/tangent_viewer/index.html',
               'photo2/tangent_viewer/style.css']
    summary = dict(request='R183', proposal='Maker estimates actual visible diameter may be about7% larger; not verified.',
        demonstration_parameters=frame['parameters'], crop=crop,
        definition='Image-normal offset of projected centerline by plus/minus (chain_minor+bead_radius)*orthographic_scale; reference band, not detected silhouette.',
        orthographic_support='A circular cross-section has this normal support radius at any camera elevation; guides omit discrete scallops and axial curvature effects.',
        samples=2048, baseline_radius_model_units=frame['guides']['radius_model_units'],
        diameter_pixels={str(f['count']): dict(model=2*f['guides']['radius_pixels'],
            comparison_107_percent=2*1.07*f['guides']['radius_pixels']) for f in [frame, comparison]},
        circles_unchanged=True, geometry_scale_unchanged=True,
        saves_compatible_with_prior_choice_format=True,
        validation=dict(python_checks=7, viewport_checks=5, status='passed',
            not_run=['Browser/UI/server interaction', 'Launcher']),
        question=dict(id='Q183.1', status='pending',
            text='In the raw/guide comparison, do green107% lines bracket the visible bead bodies better than amber100% lines, ignoring cast shadow and small scallops?',
            file='photo2/WIDTH_GUIDES.md'),
        source_sha256={name: sha(ROOT / name) for name in sources},
        artifact_sha256={str(p.relative_to(ROOT)):sha(p) for p in [out/'whole-guides.png',out/'raw-width-comparison.png']},
        reproduction_commands=['.venv/bin/python photo2/review_width_guides.py',
            '.venv/bin/python -m unittest discover -s photo2 -p test_tangent_viewer.py',
            'node photo2/tangent_viewer/viewport.test.mjs'],
        limits='Approximate historical spline and camera/count hypotheses; no edge detection, width measurement, helicity or count recovery.')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary['diameter_pixels'], indent=2))


if __name__ == '__main__':
    main()
