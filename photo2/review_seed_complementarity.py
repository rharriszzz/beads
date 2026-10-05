"""R232: inspect frozen seed proposals and spacing; do not run a detector.

Coordinates are diagnostic proposals, not physical bead identities. Crops and
the P/Q pair are presentation choices made after R231 extraction finished.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "photo2/review/r231"
SUMMARY_SHA = "fc37467fc50ffb4804768874d019265a8c1e453330bac5ec51dc63cf0c36a53b"
POINTS_SHA = "422858d7f4365cc415014b39c3001f091ca2d6099946bbbfc620c9062f517bfd"
QUESTION_SHA = "013a65a0fcd9fa98c6bec8bb5e93d4283e982af62eec072b4dbf630b09485ed2"
COLORS = {"M4": (0, 225, 255), "M1": (255, 165, 40), "M3": (40, 255, 120)}
QUESTION = (
    "Q232.1: In photo2/SEED_METHOD_REVIEW.md, the B close-up marks P "
    "(M1 brightness point) and Q (M4/M3 point). Are P and Q inside the "
    "same yellow bead, or two different yellow beads?"
)
ASYNC_QUESTION = (
    "Q232.1: In photo2/SEED_METHOD_REVIEW.md (also "
    "http://127.0.0.1:4001/seed-review.html), the final B close-up marks "
    "amber P and cyan Q on yellow. Are P and Q inside the same yellow bead, "
    "or two different yellow beads?"
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def check(path, expected):
    actual = sha(path)
    if actual != expected:
        raise ValueError(f"Frozen input changed: {path}")
    return actual


def visible(rows, box):
    x0, y0, x1, y1 = box
    return [p for p in rows if x0 <= p['xy'][0] < x1 and y0 <= p['xy'][1] < y1]


def panel(image, box, groups=(), labels=None):
    """One native pixel per point; resized rings/letters are guides only."""
    x0, y0, x1, y1 = box
    pixels = image[y0:y1, x0:x1].copy()
    shown = [(method, p) for method, rows in groups for p in visible(rows, box)]
    for method, p in shown:
        x, y = p['xy']
        pixels[y-y0, x-x0] = COLORS[method]
    scale = 4
    result = Image.fromarray(pixels).resize(
        ((x1-x0)*scale, (y1-y0)*scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype('DejaVuSans.ttf', 22)
    for method, p in shown:
        x, y = p['xy']
        sx, sy = (x-x0+.5)*scale, (y-y0+.5)*scale
        r = 6
        draw.ellipse((sx-r, sy-r, sx+r, sy+r), outline=COLORS[method], width=1)
        if labels and p['id'] in labels:
            draw.text((sx+11, sy-23), labels[p['id']], fill='white', font=font,
                      stroke_width=2, stroke_fill='black')
    return result


def contact(image, rows, case, out):
    box = case['box']
    local = case['methods']
    extras = {k: [p for p in local[k] if p['shown_as_possible_extra']]
              for k in ['M1', 'M3']}
    panels = [
        ('Raw photo', 'Same native crop in every panel', ()),
        ('M4 alone', f"{case['M4_points_in_crop']} cyan proposals",
         (('M4', rows['M4']),)),
        ('M4 + possible M1 additions', f"{len(extras['M1'])} amber points beyond 6.80 px",
         (('M4', rows['M4']), ('M1', extras['M1']))),
        ('M4 + possible M3 additions', f"{len(extras['M3'])} green points beyond 6.80 px",
         (('M4', rows['M4']), ('M3', extras['M3']))),
    ]
    width, height = (box[2]-box[0])*4, (box[3]-box[1])*4
    row_height = height + 60
    result = Image.new('RGB', (2*width, 2*row_height+65), 'white')
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype('DejaVuSans.ttf', 19)
    for i, (title, caption, groups) in enumerate(panels):
        x, y = (i % 2)*width, (i // 2)*row_height
        draw.text((x+8, y+4), title, fill='black', font=font)
        draw.text((x+8, y+30), caption, fill='#404854', font=font)
        result.paste(panel(image, box, groups), (x, y+60))
    draw.text((8, 2*row_height+4),
              'Cyan = frozen M4. Amber/green = another proposal, not a confirmed extra bead.',
              fill='black', font=font)
    draw.text((8, 2*row_height+32),
              '6.80 px only declutters the display. One native pixel per point; hollow rings are guides.',
              fill='black', font=font)
    result.save(out / f"supplements-{case['name'].lower()}.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'photo2/review/r232')
    parser.add_argument('--profiles', type=Path, default=ROOT / 'photo2/output/r231/profiles.npz')
    parser.add_argument('--pool', type=Path, default=ROOT / 'photo2/output/r231/profile-pool.json')
    args = parser.parse_args()
    inputs = {
        'photo2/review/r231/summary.json': check(FROZEN / 'summary.json', SUMMARY_SHA),
        'photo2/review/r231/points.json': check(FROZEN / 'points.json', POINTS_SHA),
        'photo2/seed-method-questions-r231.json': check(
            ROOT / 'photo2/seed-method-questions-r231.json', QUESTION_SHA),
    }
    summary = json.loads((FROZEN / 'summary.json').read_text())
    for relative, expected in summary['source_sha256'].items():
        inputs[relative] = check(ROOT / relative, expected)
    for relative, expected in summary['curated_sha256'].items():
        path = FROZEN / relative
        inputs[str(path.relative_to(ROOT))] = check(path, expected)
    for name, path in [('profile-pool.json', args.pool), ('profiles.npz', args.profiles)]:
        expected = summary['routine_sha256'][name]
        check(path, expected)
        inputs[str(path)] = expected

    data = json.loads((FROZEN / 'points.json').read_text())
    rows = {p['key']: p['points'] for p in data['methods']}
    pool = json.loads(args.pool.read_text())
    pool_index = {(p['xy'][0], p['xy'][1], p['mode']): i for i, p in enumerate(pool)}
    profiles = np.load(args.profiles)
    parameters = data['parameters']
    diameter = parameters['native_diameter']
    spacing = parameters['same_family_spacing']
    count = profiles['valid'].sum(axis=-1)
    assert np.array_equal(count, profiles['count'])
    passes = ((np.minimum(count[:, 0], count[:, 2]) >= 2)
              | (np.minimum(count[:, 1], count[:, 3]) >= 2))
    assert np.array_equal(passes, profiles['accepted'])
    selected = {(p['xy'][0], p['xy'][1], p['mode']) for p in rows['M4']}
    diagnostics = {}
    for method in ['M1', 'M3']:
        diagnostics[method] = []
        for p in rows[method]:
            x, y = p['xy']
            same = [q for q in rows['M4'] if q['mode'] == p['mode']]
            nearest = min(same, key=lambda q: np.linalg.norm(np.asarray(q['xy']) - [x, y]))
            distance = float(np.linalg.norm(np.asarray(nearest['xy']) - [x, y]))
            index = pool_index[x, y, p['mode']]
            if (x, y, p['mode']) in selected:
                state = 'selected_exact_point'
            elif not passes[index]:
                state = 'rejected_profile'
            else:
                state = 'suppressed_spacing'
                assert distance < spacing
                assert nearest['score'] >= float(profiles['score'][index])
            diagnostics[method].append(dict(
                id=p['id'], xy=p['xy'], mode=p['mode'], method=method,
                nearest_M4={'id': nearest['id'], 'xy': nearest['xy'], 'distance_pixels': distance},
                profile_index=index, valid_cuts_per_direction=count[index].tolist(),
                profile_score=float(profiles['score'][index]), M4_stage_outcome=state,
                shown_as_possible_extra=distance >= .25*diameter))

    contexts = json.loads((FROZEN / 'review-locations.json').read_text())['cases'][:2]
    cases = [dict(name=c['name'], box=c['box'],
                  M4_points_in_crop=len(visible(rows['M4'], c['box'])),
                  methods={k: visible(diagnostics[k], c['box']) for k in diagnostics})
             for c in contexts]
    sensitivity = []
    for name, methods in [('Whole photo', diagnostics)] + [(c['name'], c['methods']) for c in cases]:
        for method, points in methods.items():
            sensitivity.append(dict(context=name, method=method, total=len(points),
                farther_than=[dict(diameter_fraction=f, radius_pixels=f*diameter,
                    proposals=sum(p['nearest_M4']['distance_pixels'] >= f*diameter for p in points))
                    for f in [.25, .35, .50]]))

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    image = np.asarray(Image.open(ROOT / 'beads-photo-2.jpg').convert('RGB'))
    for case in cases:
        contact(image, rows, case, out)
    p = next(p for p in rows['M1'] if p['id'] == 'M1:53')
    q = next(p for p in rows['M4'] if p['id'] == 'M4:55')
    assert p['xy'] == [943, 388] and q['xy'] == [946, 377]
    assert any(t['xy'] == q['xy'] and t['mode'] == q['mode'] for t in rows['M3'])
    box = cases[1]['box']
    raw = panel(image, box)
    marked = panel(image, box, (('M1', [p]), ('M4', [q])), {p['id']: 'P', q['id']: 'Q'})
    pair = Image.new('RGB', (raw.width*2, raw.height+75), 'white')
    draw = ImageDraw.Draw(pair)
    font = ImageFont.truetype('DejaVuSans.ttf', 19)
    draw.text((8, 5), 'B: raw photo', font=font, fill='black')
    draw.text((raw.width+8, 5), 'P: M1 (amber). Q: M4/M3 (cyan).', font=font, fill='black')
    pair.paste(raw, (0, 40)); pair.paste(marked, (raw.width, 40))
    draw.text((8, raw.height+48), 'P and Q are 11.40 native pixels apart. Same bead or different beads?',
              font=font, fill='black')
    pair.save(out / 'pair-b.png')
    save(out / 'analysis.json', dict(request='R232', input_sha256=inputs,
        native_diameter=diameter, display_radius_pixels=.25*diameter,
        spacing_radius_pixels=spacing, source_M4_directions_degrees=[0, 45, 90, 135],
        display_rule='Show other-method points at least 0.25D from all same-family M4 points; whole-photo nearest search. Display decluttering only.',
        cases=cases, proximity_sensitivity=sensitivity,
        source_points_recomputed=False, physical_bead_aliases_resolved=False,
        profile_outcomes_verified=True))

    question_manifest = dict(request='R232', question=QUESTION, async_prompt=ASYNC_QUESTION, status='pending',
        review='photo2/SEED_METHOD_REVIEW.md', image='photo2/review/r232/pair-b.png',
        image_sha256=sha(out / 'pair-b.png'), photo_sha256=inputs['beads-photo-2.jpg'],
        points_sha256=POINTS_SHA, box=box, pair=[dict(letter='P', **p), dict(letter='Q', **q)],
        other_method_at_Q='M3:45', distance_pixels=float(np.linalg.norm(np.asarray(p['xy'])-q['xy'])),
        relation='Unresolved same-body relationship; no seed/mask/center confirmation implied.')
    save(out / 'question.json', question_manifest)

    images = []
    for title, name in [('A: M4 and possible supplements', 'supplements-a.png'),
                        ('B: M4 and possible supplements', 'supplements-b.png'),
                        ('Q232.1: shifted yellow points', 'pair-b.png')]:
        encoded = base64.b64encode((out / name).read_bytes()).decode()
        images.append(f'<h2>{title}</h2><div class="photo"><img alt="{title}" src="data:image/png;base64,{encoded}"></div>')
    html = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>R232 seed review</title><style>body{font:18px/1.5 sans-serif;margin:24px;max-width:1500px}'
        '.photo{overflow:auto}img{display:block;width:1440px;max-width:none}p{max-width:950px}</style>'
        '<h1>Seed review after your A/B assessment</h1>'
        '<p>M4 is the provisional starting point. M1 finds bright diffuse colored interiors; '
        'detected reflections are suppressed and excluded from its seed pixels.</p>'
        '<p>These three options compare M4 alone, M4 with M1 candidates, and M4 with M3 candidates. '
        'Cyan is frozen M4; amber is M1; green is M3. The 6.80 px rule only declutters the display; '
        'additional points can still belong to already represented beads. No detector was changed.</p>'
        '<p>' + QUESTION + '</p>' + ''.join(images) + '</html>\n')
    (out / 'index.html').write_text(html)
    alias = ROOT / 'photo2/review/r224/seed-review.html'
    canonical_output = out.resolve() == (ROOT / 'photo2/review/r232').resolve()
    if canonical_output:
        alias.write_text(html)
    save(out / 'summary.json', dict(request='R232', input_sha256=inputs,
        source_sha256={'photo2/review_seed_complementarity.py': sha(Path(__file__))},
        curated_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p)
                        for p in sorted(out.iterdir()) if p.is_file() and p.name not in ['summary.json', 'verification.json']},
        existing_server_alias='http://127.0.0.1:4001/seed-review.html' if canonical_output else None,
        alias_sha256=sha(alias) if canonical_output else None,
        detector_changed=False, frozen_R231_changed=False, new_bead_identity_claimed=False,
        reproduction='.venv/bin/python photo2/review_seed_complementarity.py'))
    print('R232: two supplement comparisons and one same-body question; no detector change.')


if __name__ == '__main__':
    main()
