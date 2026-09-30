"""R179: both saved three-core helicity fits at original and +5% counts."""
import argparse
import json
import shutil
from pathlib import Path

from tangent_circles import ROOT, load_model, overlays, render_model, sha, plt
from PIL import Image, ImageOps


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'photo2/output/r179')
    parser.add_argument('--review', type=Path, default=ROOT / 'photo2/review/r179')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.review.mkdir(parents=True, exist_ok=True)
    frozen = read(ROOT / 'photo2/review/r175/summary.json')
    for path, digest in frozen['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
    candidates = frozen['original_fit']['best_by_chart_and_hand']
    template = read(ROOT / 'photo2/review/r175/parameters.json')
    mappings = read(ROOT / 'photo2/review/r160/report.json')['mappings']
    raw = ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB')
    records = []
    for hand, family in [(1, 'A'), (-1, 'B')]:
        seed = candidates[f'{family}/{hand:+d}']
        assert all(seed['inside_confirmed_interiors']) and all(seed['exposed'])
        for count in [2698, 2833]:
            name = f"{'plus' if hand > 0 else 'minus'}-{count}"
            out, review = args.output / name, args.review / name
            out.mkdir(parents=True, exist_ok=True)
            review.mkdir(parents=True, exist_ok=True)
            config = dict(template, family=family,
                          parameters=dict(seed['parameters'], nbeads=count))
            model = load_model(config, config['parameters'])
            print(f'Generating {name}: whole photo, local crop, exposure check', flush=True)
            overlay = overlays(config, model, out, family, mappings)
            check = render_model(model, out, name=name, circle_radius=config['circle_radius'])
            assert check['independent_same_ray_check']['mismatches'] == 0
            assert Image.open(out / 'bracelet-overlay.png').size == (2540, 3182)
            if hand == -1:
                prior = ROOT / f"photo2/review/{'r175' if count == 2698 else 'r177'}"
                for filename in ['bracelet-overlay.png', 'patch-overlay.png']:
                    assert sha(out / filename) == sha(prior / filename), filename
                assert config == read(prior / 'parameters.json')
            write(out / 'parameters.json', config)
            write(out / 'report.json', dict(parameters=config, overlay=overlay, check=check))
            for filename in ['bracelet-overlay.png', 'patch-overlay.png', 'parameters.json']:
                shutil.copyfile(out / filename, review / filename)
            records.append(dict(name=name, hand=hand, count=count, family=family,
                config=config, original_core_fit=seed,
                projected_scale_pixels_per_unit=model.view.scale,
                overlay=overlay, independent_check=check,
                report_sha256=sha(out / 'report.json')))
            print(json.dumps(dict(name=name, visible_anchors=overlay['visible_anchors'],
                same_ray_check=check['independent_same_ray_check'])), flush=True)

    # Same frame, marker size, crop and panel arrangement for every comparison.
    for crop, filename, figsize in [(None, 'whole-comparison.png', (12, 16)),
                                   ((1210, 210, 1450, 365), 'patch-comparison.png', (14, 10))]:
        fig, axes = plt.subplots(2, 2, figsize=figsize, constrained_layout=True)
        for ax, record in zip(axes.flat, records):
            image = Image.open(args.review / record['name'] / 'bracelet-overlay.png')
            ax.imshow(image if crop is None else image.crop(crop))
            ax.set_title(f"Helicity {record['hand']:+d}; {record['count']:,} beads" +
                         (' (+5%)' if record['count'] == 2833 else ' (original)'))
            ax.axis('off')
        fig.savefig(args.review / filename, dpi=160)
        plt.close(fig)
    crop = (900, 155, 1650, 455)
    for hand in [1, -1]:
        name = 'plus' if hand > 0 else 'minus'
        fig, axes = plt.subplots(3, 1, figsize=(15, 14), constrained_layout=True)
        images = [raw] + [Image.open(args.review / f'{name}-{count}/bracelet-overlay.png')
                          for count in [2698, 2833]]
        titles = ['Raw photo: wider upper arc', f'Helicity {hand:+d}: 2,698 beads',
                  f'Helicity {hand:+d}: 2,833 beads (+5.004%); same phase and spline position']
        for ax, image, title in zip(axes, images, titles):
            ax.imshow(image.crop(crop)); ax.set_title(title); ax.axis('off')
        fig.savefig(args.review / f'{name}-spacing-comparison.png', dpi=160)
        plt.close(fig)
    summary = dict(request='R179', variants=records,
        source_sha256=frozen['source_sha256'] | {
            'photo2/compare_tangent_helicities.py': sha(Path(__file__)),
            'photo2/review/r175/summary.json': sha(ROOT / 'photo2/review/r175/summary.json'),
            'photo2/review/r175/parameters.json': sha(ROOT / 'photo2/review/r175/parameters.json')},
        method='Reuse each hand/chart original 8/11/20 core fit; change count only within that hand; no new fit.',
        identical_between_helicities=['spline', 'camera elevation/roll', 'physical bead dimensions',
                                      'circle radius', 'exposure rule', 'source photo', 'crops'],
        differing_registration_between_helicities=['saved phase', 'saved along-spline origin', 'diagnostic index chart'],
        helicity_sign='Positive advances increasing minor-circle phase along the clockwise image centerline; negative decreases it.',
        exposure_rule='Only self-first, depth-matching, finished, non-grazing minor-outward points are drawn; all beads remain occluders.',
        pending_review='Q177.1 remains pending; user still working, no new question required.',
        limits='Diagnostic forward hypotheses, not recovered photo helicity, N, camera or full bead correspondence.',
        reproduction_command='.venv/bin/python photo2/compare_tangent_helicities.py',
        artifact_sha256={str(path.relative_to(ROOT)): sha(path)
                         for path in sorted(args.review.rglob('*'))
                         if path.is_file() and path.name != 'summary.json'})
    write(args.review / 'summary.json', summary)
    print('Saved four whole-photo overlays, four raw/local overlays, two spacing comparisons and two four-way grids.', flush=True)


if __name__ == '__main__':
    main()
