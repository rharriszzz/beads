"""Post-reboot verification; does not change the frozen detector or predictions."""
import argparse
import hashlib
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from .common import OUT, ROOT, read, save, sha, mask_from_runs
from .detector import decide
from .geometry import trace
from .synthetic import projection_audit

BASE = 'f180991af5843362ebd948bcf9af4d2f6bf7219a'
DOCUMENTS = {'AGENTS.md', 'SESSION_HANDOFF.md', 'PLAN.md', 'REQUEST_LOG.md', 'METHODS.md'}


def historical_hashes():
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', BASE], cwd=ROOT)
    checked = {}
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        mode, kind, expected = meta.decode().split()
        name = name.decode()
        if name in DOCUMENTS:
            continue
        assert kind == 'blob' and mode in ('100644', '100755'), (name, mode)
        content = (ROOT / name).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        assert actual == expected, name
        checked[name] = expected
    return checked


def native_result(result, shape):
    previous = (-1, -1)
    encoded_count = 0
    for y, start, stop in result['support']:
        assert 0 <= y < shape[0] and 0 <= start <= stop < shape[1], result['id']
        assert y > previous[0] or (y == previous[0] and start > previous[1]), result['id']
        previous = (y, stop)
        encoded_count += stop - start + 1
    mask = mask_from_runs(result['support'], shape)
    count = int(mask.sum())
    assert count == encoded_count, result['id']
    assert count == result.get('support_pixels', result.get('positive_pixels')), result['id']
    assert result['physical_center'] is None
    if count:
        y, x = np.where(mask)
        np.testing.assert_allclose(result['location'], [x.mean(), y.mean()], rtol=0, atol=1e-12)
    else:
        assert result['location'] is None


def normalized(record, rules):
    # Development inference preceded calibration; compare both at the saved
    # operating point while retaining every original development record.
    return {**record, 'result': decide(record['result'], rules),
            'controls': {m: decide(r, rules, m) for m, r in record['controls'].items()}}


def main(replay=None):
    rules = read(OUT / 'freeze.json')['rules']
    historical = historical_hashes()
    result_count = 0
    query_count = 0
    scene_rows = []
    replay_queries = 0
    raster_replays = 0
    map_replays = 0
    ray_counts = dict(resolved=0, unknown=0, boundary_disagreements=0)
    splits = ['dev', 'heldout']
    if (OUT / 'confirmation-frozen-summary.json').exists():
        splits.append('confirmation')
    for split in splits:
        for folder in sorted((OUT / split).glob('scene-*')):
            records = read(folder / 'inference.json.gz')
            truth = read(folder / 'truth.json')
            targets = read(folder / 'evaluation-targets.json')['targets']
            assert len(records) == len(targets) * 15
            scene_rows.append(dict(split=split, scene=folder.name,
                                   hand=read(folder / 'geometry.json')['parameters']['hand'],
                                   targets=len(targets)))
            checks = [truth['projection_check']]
            for target in targets:
                k = target['model_index']
                maps = np.load(folder / f'hyp-{k:+03}.npz')
                identity = np.asarray(Image.open(folder / f'absent-{k:+03}' / 'identity.png'))[:, :, 0].astype(int) - 1
                expected = np.where(identity >= 0, identity - 14, -999)
                checks.append(projection_audit(maps['h0'], expected, maps['unknown']))
            for check in checks:
                for key in ray_counts:
                    # Before the recorded amendment, successful generation
                    # required zero mismatches and did not save this field.
                    ray_counts[key] += check.get(key, 0)
            for record in records:
                query_count += 1
                for result in [record['result'], record['baseline'], *record['controls'].values()]:
                    native_result(result, (224, 320))
                    result_count += 1
            if replay and (replay / split).exists():
                other = replay / folder.relative_to(OUT)
                repeat = read(other / 'inference.json.gz')
                assert [normalized(r, rules) for r in records] == [normalized(r, rules) for r in repeat], folder
                replay_queries += len(records)
                for path in sorted(folder.rglob('*.png')):
                    np.testing.assert_array_equal(np.asarray(Image.open(path)),
                                                  np.asarray(Image.open(replay / path.relative_to(OUT))))
                    raster_replays += 1
                for path in sorted(folder.glob('*.npz')):
                    with np.load(path) as a, np.load(replay / path.relative_to(OUT)) as b:
                        assert set(a.files) == set(b.files)
                        for key in a.files:
                            np.testing.assert_array_equal(a[key], b[key])
                    map_replays += 1
    real = OUT / 'real'
    anchors = read(real / 'anchors.json')
    original = ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB')
    x, y = anchors['origin']
    np.testing.assert_array_equal(np.asarray(original.crop((x, y, x + 220, y + 180))),
                                  np.asarray(Image.open(real / 'raw.png')))
    freeze = read(real / 'prediction-freeze.json')
    full_anchor_ownership = {}
    for model in freeze['models']:
        fractions = []
        for anchor, index in zip(anchors['anchors'], model['assignments']):
            owner, _, unknown = trace(model['parameters'], np.asarray(anchor['pixels']))
            fractions.append(dict(id=anchor['id'], pixels=len(owner),
                                  ownership_fraction=float(np.mean(owner == index)),
                                  unknown=int(unknown.sum())))
        full_anchor_ownership[model['id']] = fractions
    measurements = read(real / 'measurements.json')
    for row in measurements['rows']:
        for key in ('result', 'baseline'):
            native_result(row[key], (180, 220))
            result_count += 1
    real_replayed = False
    if replay:
        for name in ('anchors.json', 'prediction-freeze.json', 'measurements.json'):
            assert read(real / name) == read(replay / 'real' / name), name
        assert all(read(replay / 'replay-check.json').values())
        real_replayed = True
    save(OUT / 'recovery-audit.json', dict(
        base_commit=BASE, historical_file_count=len(historical), historical_git_blobs=historical,
        native_measurements=result_count, synthetic_queries=query_count,
        scenes=scene_rows, projection_audit=ray_counts,
        original_crop_exact=True, full_anchor_ownership=full_anchor_ownership,
        frozen_detector_sha256=sha(ROOT / 'photo2/r281/detector.py'),
        replay=dict(synthetic_queries=replay_queries, decoded_rasters=raster_replays,
                    array_files=map_replays, real_freezes_and_measurements=real_replayed,
                    note='Development decisions normalized to the frozen operating point; original records retained.')))
    print(dict(historical=len(historical), native_measurements=result_count,
               synthetic_queries=query_count, replay_queries=replay_queries,
               rasters=raster_replays, maps=map_replays, real_replayed=real_replayed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=Path)
    main(parser.parse_args().replay)
