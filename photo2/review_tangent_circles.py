"""Curate R175 forward geometry and R177's isolated five-percent count change."""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from tangent_circles import ROOT, sha, plt
from matplotlib.path import Path as Polygon


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    first = ROOT / 'photo2/output/r175'
    changed = ROOT / 'photo2/output/r177'
    before, after = first / 'fit', changed / 'count-plus-5-percent'
    original, revised = read(before / 'report.json'), read(after / 'report.json')
    model = read(first / 'model/report.json')
    checks = [read(first / 'fit-check/report.json'), read(changed / 'count-check/report.json')]
    for report in [model, original, revised]:
        for path, digest in report['source_sha256'].items():
            assert sha(ROOT / path) == digest, path
    for report in checks:
        assert report['kernel_sha256'] == sha(ROOT / 'photo2/tangent_circles.py')
        assert report['check']['independent_same_ray_check']['mismatches'] == 0
    assert revised['parameters']['nbeads'] == round(original['parameters']['nbeads'] * 1.05)
    for key, value in original['parameters'].items():
        if key != 'nbeads':
            assert revised['parameters'][key] == value, key

    r175, r177 = ROOT / 'photo2/review/r175', ROOT / 'photo2/review/r177'
    r175.mkdir(parents=True, exist_ok=True)
    r177.mkdir(parents=True, exist_ok=True)
    files = [(first / 'model/model-only.png', r175 / 'model-only.png'),
             (before / 'bracelet-overlay.png', r175 / 'bracelet-overlay.png'),
             (before / 'patch-overlay.png', r175 / 'patch-overlay.png'),
             (after / 'bracelet-overlay.png', r177 / 'bracelet-overlay.png'),
             (after / 'patch-overlay.png', r177 / 'patch-overlay.png')]
    for source, target in files:
        shutil.copyfile(source, target)
    write(r175 / 'parameters.json', read(before / 'parameters.json'))
    write(r177 / 'parameters.json', read(after / 'parameters.json'))
    write(r175 / 'fit-candidates.json', original['candidates'])

    raw = ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB')
    crop = (900, 155, 1650, 455)
    fig, axes = plt.subplots(3, 1, figsize=(15, 14), constrained_layout=True)
    for ax, image, title in zip(axes,
            [raw, Image.open(before / 'bracelet-overlay.png'), Image.open(after / 'bracelet-overlay.png')],
            ['Raw photo: wider upper arc', 'Before: 2,698 beads',
             'After: 2,833 beads (+5.004%); same phase and spline position']):
        ax.imshow(image.crop(crop))
        ax.set_title(title)
        ax.axis('off')
    fig.savefig(r177 / 'spacing-comparison.png', dpi=160)
    plt.close(fig)
    for directory in [before, after]:
        assert Image.open(directory / 'bracelet-overlay.png').size == raw.size == (2540, 3182)

    best = {}
    for candidate in original['candidates']:
        key = f"{candidate['family']}/{candidate['parameters']['hand']:+d}"
        best.setdefault(key, candidate)
    cores = read(ROOT / 'photo2/review/r157/report.json')['results']
    evaluation = {}
    for name, report in [('initial_fit', original), ('count_adjustment', revised)]:
        evaluation[name] = []
        for point in report['overlay']['local_checks']:
            number = point['maker_number']
            core = next((core for core in cores if core['number'] == number), None)
            if core is not None:
                evaluation[name].append(dict(maker_number=number,
                    predicted_outward_inside_confirmed_core=bool(Polygon(np.array(core['loop_xy'])).contains_point(point['outward_xy'])),
                    used_for_initial_fit=number in [8, 11, 20]))
    summary = dict(requests=['R175', 'R176', 'R177', 'R178'],
        curator_sha256=sha(Path(__file__)), source_sha256=original['source_sha256'],
        historical_spline=read(ROOT / 'photo2/spline-seed-r175.json') | {'points': '303 points preserved in tracked spline-seed-r175.json'},
        historical_count=read(ROOT / 'photo2/count-seed-r175.json'),
        model_only=model, original_fit=dict(parameters=original['parameters'],
            selected=original['selected'], best_by_chart_and_hand=best,
            candidate_count=len(original['candidates']), overlay=original['overlay'],
            candidate_file='photo2/review/r175/fit-candidates.json'),
        count_adjustment=dict(parameters=revised['parameters'], nrows=revised['nrows'],
            exact_beads_per_row=revised['exact_beads_per_row'],
            count_percent=100*(2833/2698-1), original_scale=original['scale_pixels_per_unit'],
            revised_scale=revised['scale_pixels_per_unit'], overlay=revised['overlay'],
            refitted=False, unchanged=['spline', 'phase', 'origin_fraction', 'elevation', 'roll', 'hand', 'physical_bead_dimensions'],
            projected_scale_ratio=revised['scale_pixels_per_unit']/original['scale_pixels_per_unit']),
        independent_checks=checks, positive_core_checks_after_selection=evaluation,
        exposure=dict(first_owner_must_be_self=True, front_depth_tolerance_model_units=.002,
            sdf_march_tolerance_model_units=1e-5, max_iterations=600, facing_dot_margin=.12,
            unfinished_rays_excluded=True, all_beads_including_hidden_occluders=True),
        meanings=dict(plane_normal='geometry.npz radial; normal is the planar left normal',
            center='Minor-radial outer-wall midpoint, not visible-area centroid or specular reflection',
            indices='Forward generator indices/competing diagnostic chart; not recovered full-string photo labels',
            visibility='Visibility in each provisional model, not established physical exposure in the photo'),
        held_group_excluded_from_fit_and_ranking=[22,23,24,25],
        question=dict(id='Q177.1', status='pending', file='photo2/TANGENT_CIRCLES.md',
            text='In the wider upper-arc comparison, does the spacing of the cyan circles look closer to the photographed bead spacing after increasing the count to 2,833?'),
        reproduction_commands=[
            '.venv/bin/python photo2/tangent_circles.py --stage model --output photo2/output/r175/model',
            '.venv/bin/python photo2/tangent_circles.py --stage fit --output photo2/output/r175/fit',
            '.venv/bin/python photo2/check_tangent_circles.py',
            '.venv/bin/python photo2/tangent_circles.py --stage overlay --parameters photo2/output/r175/fit/parameters.json --nbeads 2833 --output photo2/output/r177/count-plus-5-percent',
            '.venv/bin/python photo2/check_tangent_circles.py --parameters photo2/output/r177/count-plus-5-percent/parameters.json --output photo2/output/r177/count-check',
            '.venv/bin/python photo2/review_tangent_circles.py'],
        artifact_sha256={str(path.relative_to(ROOT)): sha(path) for path in [
            *(target for _, target in files), r177 / 'spacing-comparison.png',
            r175 / 'parameters.json', r177 / 'parameters.json', r175 / 'fit-candidates.json']})
    write(r175 / 'summary.json', summary)
    print(json.dumps(dict(current_nbeads=2833, visible_anchors=revised['overlay']['visible_anchors'],
                         positive_core_checks=evaluation), indent=2))


if __name__ == '__main__':
    main()
