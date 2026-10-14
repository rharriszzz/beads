"""Replay every fresh-scene inference from saved pixels/geometry, without rendering."""
import shutil

from .common import OUT, ROOT, read, save, sha
from . import run


def main():
    original = ROOT / 'photo2/r281/results'
    assert OUT.resolve() != original.resolve(), 'Use R281_OUTPUT for a new replay directory'
    assert not OUT.exists() or not any(OUT.iterdir()), 'Replay directory must be empty'
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original / 'freeze.json', OUT / 'freeze.json')
    shutil.copytree(original / 'confirmation', OUT / 'confirmation',
                    ignore=shutil.ignore_patterns('inference.json.gz'))
    run.main('confirmation', 'all')
    count = 0
    for folder in sorted((original / 'confirmation').glob('scene-*')):
        expected = read(folder / 'inference.json.gz')
        actual = read(OUT / 'confirmation' / folder.name / 'inference.json.gz')
        assert actual == expected, folder.name
        count += len(actual)
    save(original / 'confirmation-replay-check.json', dict(
        scenes=24, queries=count, method_outputs=count * 4, exact=True,
        detector_sha256=sha(ROOT / 'photo2/r281/detector.py'),
        freeze_sha256=sha(original / 'confirmation-freeze.json'),
        note='All method outputs and hypotheses compared exactly; reuses saved photographic/identity '
             'rasters and geometry. This check does not independently rerender the confirmation scenes.'))
    print('Exact fresh-scene query replays:', count)


if __name__ == '__main__':
    main()
