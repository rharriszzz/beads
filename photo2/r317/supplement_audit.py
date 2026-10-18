"""Audit sealed R317 radial-orientation evidence without generating new trials.

Only reads saved parameters, metrics and exported frames. No placement, renderer,
contact search or optimization is invoked. Historical cant is inward-positive;
the supplement reports outward-positive beta = -cant.
"""
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path(__file__).with_name('results')
OUT = RESULTS / 'supplement-audit'
SPLITS = ['development', 'comparison', 'buffer']
CORES = ['C-1477-0290', 'R282-1459-0316', 'R282-1536-0239',
         'R282-1537-0308', 'C-1497-0271', 'C-1559-0252']


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def beta(p, k):
    result = np.full(len(k), -p.get('radial_cant', 0.), dtype=float)
    width = p.get('orientation_halfwidth', 18)
    centers = p.get('compact_centers', [-13, 0, 13])
    for center, value in zip(centers, p.get('compact_cant', [])):
        result -= value * np.maximum(0, 1 - ((k-center)/width)**2)**3
    return result


def brief(row):
    out = {k: row[k] for k in ['id', 'classification', 'feasible']}
    if row['feasible']:
        early = {r['id']: r for r in row['early']}
        out['coverage_percent'] = {k: 100*early[k]['best_visible'] for k in CORES}
        out['next_negative_visible_percent'] = {
            str(i): 100*early[CORES[1]]['visible'].get(str(i), 0.)
            for i in [-14, -15]}
        out['evidence'] = {k: row[k] for k in SPLITS}
        out['brackets'] = row['brackets']
        out['physical'] = row['physical']
    return out


def main():
    paths = sorted((RESULTS / 'trials').glob('*.json.gz'))
    rows = [read(p) for p in paths]
    assert len(rows) == 1797
    shared = []
    for row in rows:
        if row['stage'] != 'D-shared-radial-cant':
            continue
        p = dict(row['parameters'])
        cant = p.pop('radial_cant')
        parents = [r for r in rows if r['parameters'] == p]
        assert len(parents) == 1
        assert not any(p.get('compact_cant', []))
        shared.append(dict(parent=brief(parents[0]), trial=brief(row),
                           beta_degrees=-cant,
                           changed_parameter_keys=['radial_cant'],
                           all_other_parameters_exact=True))
    assert len(shared) == 12
    baseline_controls = sorted([r for r in shared if r['parent']['id'] == 3],
                               key=lambda r: r['beta_degrees'])
    assert [r['beta_degrees'] for r in baseline_controls] == [-10, -5, 5, 10]
    models = []
    exports = sorted(RESULTS.glob('*-model.json.gz'))
    for path in exports:
        row = read(path)
        p = row['parameters']
        if p.get('trajectory_mix', 0.) != 0:
            models.append(dict(name=row['name'], excluded=True,
                               reason='Historical trajectory_mix baseline outside the R316 alpha/beta family'))
            continue
        frames = row['positions']['frames']
        axis = np.array(frames['surface_tangent'])
        other = np.array(frames['surface_normal'])
        third = np.array(frames['surface_binormal'])
        # R306 stores (axis, r cross axis, r) before cant. Invert the stated
        # rotation to check internal consistency of the saved body frame.
        k = np.array(row['positions']['indices'])
        b = np.radians(beta(p, k))[:, None]
        a0 = np.cos(b)*axis - np.sin(b)*third
        radial = np.sin(b)*axis + np.cos(b)*third
        np.testing.assert_allclose(np.cross(radial, a0), other, atol=2e-12)
        np.testing.assert_allclose(np.sum(axis*radial, axis=1),
                                   np.sin(b[:, 0]), atol=2e-12)
        frame = np.stack([axis, other, third], axis=1)
        np.testing.assert_allclose(frame @ np.swapaxes(frame, 1, 2),
                                   np.tile(np.eye(3), (len(k), 1, 1)), atol=2e-12)
        np.testing.assert_allclose(np.linalg.det(frame), 1., atol=2e-12)
        # These are algebraic frame consistency checks, NOT an independent
        # reconstruction of r from centers. Existing verification separately
        # replays R316 placement and checks that physical radial is unchanged.
        selected = (k >= -100) & (k <= 99)
        assert k[selected].tolist() == list(range(-100, 100))
        values = np.degrees(b[:, 0])
        models.append(dict(name=row['name'], bodies=len(k),
                           beta_range_degrees=[float(values.min()), float(values.max())],
                           target_beta_degrees=values[selected].tolist(),
                           target_indices=k[selected].tolist(),
                           maximum_radial_component=float(np.abs(np.sin(b)).max()),
                           saved_frames_orthonormal=True))
    dependencies = paths + exports + [Path(__file__), RESULTS/'attribution.json',
                                     RESULTS/'verification.json', RESULTS/'delivery.json']
    doc = dict(policy='Archive-only audit; no new scientific evaluations or optimization.',
               original_deadline_utc=read(RESULTS/'delivery.json')['deadline_utc'],
               sign='beta = -radial_cant - sum(compact_cant * compact_basis); outward positive',
               shared_controls=shared, models=models,
               missing=['shared +/-20 and +/-30 degree controls',
                        'isolated outlines and occluder ledgers for shared controls',
                        'fixed-baseline paper-plane clearances for shared controls',
                        'phase-locked and curvature-dependent beta comparisons',
                        'controlled shared-versus-smooth comparison with other parameters frozen'],
               source_sha256={str(p.relative_to(ROOT)): sha(p) for p in dependencies})
    OUT.mkdir(exist_ok=True)
    (OUT/'audit.json').write_text(json.dumps(doc, indent=2, sort_keys=True)+'\n')
    def table_row(angle, r):
        cover = r['coverage_percent']
        next15 = r['next_negative_visible_percent']['-15']
        return '| '+ ' | '.join([str(angle), str(r['id'])] +
                                [f'{cover[k]:.2f}' for k in CORES] + [f'{next15:.2f}'])+' |'
    ordered = [(r['beta_degrees'], r['trial']) for r in baseline_controls]
    ordered.append((0, brief(rows[3])))
    ordered.sort()
    text = ['# Saved orientation-only R316 controls', '',
            'Percent visible single-body core coverage; all controls certified full-chain separation.',
            'Next −15 is a separate nominated body, never combined with the modal next-negative fraction.', '',
            '| beta ° | trial | first negative | next negative | +8 | +12 | reference | C-1559 | next −15 |',
            '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    text += [table_row(a, r) for a, r in ordered]
    text += ['', '| beta ° | geography | paper % | seam conflicts % | bracket p95 px | worst-core p95 px |',
             '|---:|---|---:|---:|---:|---:|']
    for a, r in ordered:
        for split in SPLITS:
            v = r['evidence'][split]['vector']
            text.append(f"| {a} | {split} | {v['paper']:.3f} | {v['seam']:.3f} | {r['brackets'][split]['p95']:.3f} | {v['worst']:.3f} |")
    text += ['', 'Generated only from sealed trial files. Full 40-core metrics and the other two',
             'fixed-parent control families are retained in audit.json. No new contact or ray evaluation.', '']
    (OUT/'tables.md').write_text('\n'.join(text))
    print(json.dumps(dict(shared_controls=len(shared), models=len(models),
                          trials_unchanged=all(sha(p) == doc['source_sha256'][str(p.relative_to(ROOT))]
                                               for p in paths), output=str(OUT))))


if __name__ == '__main__':
    main()
