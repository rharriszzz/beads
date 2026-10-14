"""Fresh post-recovery confirmation of the fixed material/combined comparison.

The scene family is copied from the original frozen generator; only the seed,
split name and scene count differ. No new tuning or photographic fitting.
"""
import argparse
from datetime import datetime, timezone

import numpy as np
from PIL import Image

from photo2.r280.synthetic import render
from photo2.r280.geometry import templates, certify
from photo2.r280.evaluate import truth_rows
from .common import OUT, ROOT, read, save, sha
from .geometry import counterfactual
from .synthetic import removed, projection_audit
from . import run, analyze

SEED = 281403
SCENES = 24


def freeze():
    assert not (OUT / 'confirmation').exists(), 'Freeze before generating any confirmation scene'
    path = OUT / 'confirmation-freeze.json'
    assert not path.exists(), 'Do not overwrite the confirmation freeze'
    save(path, dict(utc=datetime.now(timezone.utc).isoformat(), seed=SEED, scenes=SCENES,
                   rules=read(OUT / 'freeze.json')['rules'],
                   source_hashes={name: sha(ROOT / 'photo2/r281' / name) for name in
                                  ('confirmation.py', 'detector.py', 'geometry.py', 'run.py',
                                   'synthetic.py', 'evaluate.py', 'analyze.py')},
                   motivation='Material-only recovered 17/23 development and 42/59 original held-out targets; '
                              'combined recovered 16/23 and 38/59. Both had zero exact-position absent confirmations. '
                              'Original held-out outcomes were seen before this follow-up; these new scenes are independent.',
                   decision='Keep all old results. Compare the two fixed methods at 0/.05/.10D and 5/10deg roll, '
                            'plus every negative. Report paired disagreements, recall and false confirmations. '
                            'No threshold search or automatic production adoption. Wrong-neighbor/identity failures block growth.'))


def generate():
    frozen = read(OUT / 'confirmation-freeze.json')
    assert frozen['seed'] == SEED and frozen['scenes'] == SCENES
    for name, digest in frozen['source_hashes'].items():
        assert sha(ROOT / 'photo2/r281' / name) == digest, name
    rng = np.random.default_rng(SEED)
    records = []
    for s in range(SCENES):
        folder = OUT / 'confirmation' / f'scene-{s:02}'
        folder.mkdir(parents=True, exist_ok=True)
        p = dict(hand=(-1, 1)[s % 2], phase=float(rng.uniform(-np.pi, np.pi)),
                 pitch=(1.12, 1.20)[s // 2 % 2], inclination=float(rng.uniform(-30, 30)),
                 roll=float(rng.uniform(-55, 55)), scale=(8., 10.)[s % 2], translation=[159.5, 111.5],
                 light=[float(rng.uniform(-.8, .8)), float(rng.uniform(-.7, .7)), 1.],
                 light_power=float(rng.uniform(.9, 1.3)), specular=(.3, 1.2, .7)[s % 3],
                 roughness=(.035, .06)[s % 2], ambient=.12,
                 background=([.47, .31, .43], [.65, .63, .52], [.23, .29, .34], [.46, .38, .31])[s % 4])
        classes = rng.choice(3, 29, p=[.4, .4, .2])
        classes[11:14] = s % 2
        certificate = certify(p)
        assert certificate['certified']
        render(folder, p, classes)
        identity = render(folder, p, classes, True)
        owner = identity[:, :, 0].astype(np.int16) - 1
        np.savez_compressed(folder / 'truth.npz', owner=owner)
        predictions, audit = templates(p)
        check = projection_audit(audit['owner'], np.where(owner >= 0, owner - 14, -999), audit['unknown'])
        save(folder / 'geometry.json', dict(parameters=p, predictions=predictions))
        save(folder / 'truth.json', dict(seed=SEED, scene=s, classes=classes.tolist(),
                                         certificate=certificate, projection_check=check))
        _, tiers = truth_rows(folder)
        eligible = sorted([r for r in tiers if r['tier'] == 'easy' and abs(r['model_index']) <= 10],
                          key=lambda r: (-r['area'], r['model_index']))[:4]
        save(folder / 'evaluation-targets.json', dict(targets=eligible, available=len(eligible),
                                                     unavailable_slots=4-len(eligible), all_tiers=tiers))
        for row in eligible:
            k = row['model_index']
            absent = folder / f'absent-{k:+03}'
            removed(absent, folder, row['index'])
            hyp = counterfactual(p, k, (224, 320), audit['owner'], audit['unknown'])
            np.savez_compressed(folder / f'hyp-{k:+03}.npz', h1=hyp['h1'], h0=hyp['h0'], unknown=hyp['unknown'])
            save(folder / f'hyp-{k:+03}.json', {a: b for a, b in hyp.items() if a not in ('h1', 'h0', 'unknown')})
            absent_owner = np.asarray(Image.open(absent / 'identity.png'))[:, :, 0].astype(int) - 1
            check = projection_audit(hyp['h0'], np.where(absent_owner >= 0, absent_owner - 14, -999), hyp['unknown'])
            save(absent / 'projection-audit.json', check)
        records.append(dict(scene=s, targets=len(eligible), hand=p['hand']))
        print('confirmation', s, 'easy', len(eligible), flush=True)
    save(OUT / 'confirmation-generation.json', dict(seed=SEED, scenes=records,
                                                   targets=sum(r['targets'] for r in records)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'run'])
    args = parser.parse_args()
    if args.action == 'freeze':
        freeze()
    else:
        generate()
        run.main('confirmation', 'all')
        analyze.main('confirmation')
