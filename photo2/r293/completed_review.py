"""Archive and verify the completed R293 review; no inference or feedback writes.

Run without arguments to archive the local ledger and every immutable snapshot.
Run --check to reproduce the summary from the archive, without requiring live feedback.
"""
import argparse
import collections
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import tarfile

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / 'photo2/r293/feedback'
OUT = ROOT / 'photo2/r293/evidence'
REVIEW = ROOT / 'photo2/review/r293'
ARCHIVE = OUT / 'completed-r293-review.tar.gz'
LEDGER = OUT / 'completed-r293-review.jsonl.gz'
SUMMARY = OUT / 'completed-r293-review-analysis.json'
SOURCE_REVISION = '7e30d3a6e2bed1848ff84f7670a8e6b5901fdb1b'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def live_files():
    if not (LIVE / 'judgments.jsonl').is_file():
        raise FileNotFoundError('Completed R293 ledger unavailable: ' + str(LIVE))
    return {str(p.relative_to(LIVE)): p.read_bytes()
            for p in sorted(LIVE.rglob('*')) if p.is_file()}


def packed(files):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        for name, raw in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(raw))
    return gzip.compress(stream.getvalue(), mtime=0)


def unpacked(raw):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for member in tar:
            assert member.isfile() and member.name not in files
            files[member.name] = tar.extractfile(member).read()
    return files


def analyze(files):
    raw = files['judgments.jsonl']
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    assert events, 'No judgments in archive'
    manifest = json.loads((REVIEW / 'manifest.json').read_bytes())
    entries = {c['case_id']: c for c in manifest['cases']}
    native = ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB')
    image_hash = digest((ROOT / 'beads-photo-2.jpg').read_bytes())
    latest = {}
    snapshot_ids = set()
    ownership = {}
    for event in events:
        cid = event['case_id']
        previous = latest.get(cid)
        assert event['schema'] == 'R293-review-v1'
        assert event['revision'] == (previous['revision'] if previous else 0) + 1
        assert event['previous_payload'] == (previous['payload'] if previous else
                                             dict(answer=None, diagnostics=[], ownership={}))
        assert 0 <= event['logical_parent_revision'] < event['revision']
        sid = event['candidate_digest']
        snapshot_ids.add(sid)
        data = files[f'snapshots/{sid}/candidate.json']
        crop = files[f'snapshots/{sid}/crop.png']
        assert digest(data) == sid
        assert digest(crop) == event['crop_sha256']
        candidate = json.loads(data)
        assert candidate['case_id'] == cid
        assert event['image_sha256'] == candidate['photo']['photo_sha256'] == image_hash
        assert event['feature_id'] == candidate['feature']['id']
        assert event['feature_point'] == candidate['feature']['point']
        assert event['algorithm'] == candidate['algorithm']
        assert event['parameters'] == candidate['parameters']
        assert event['displayed_candidates'] == {k: candidate[k] for k in ('A', 'B')}
        assert event['displayed_separator_arcs'] == candidate['separator_arcs']
        for key in ('historical_reviews', 'measurement_question', 'position_measurements'):
            assert event[key] == candidate[key]
        assert data == (REVIEW / 'data' / (cid + '.json')).read_bytes()
        assert crop == (REVIEW / 'crops' / (cid + '.png')).read_bytes()
        assert entries[cid]['candidate_digest'] == sid
        decoded = Image.open(io.BytesIO(crop)).convert('RGB')
        expected = native.crop(candidate['box'])
        assert decoded.size == expected.size and decoded.tobytes() == expected.tobytes()
        for key, value in event['ownership_changes'].items():
            assert event['ownership_previous'][key] == ownership.get(key)
            if value is None:
                ownership.pop(key, None)
            else:
                ownership[key] = value
        latest[cid] = event
    records = []
    for cid, event in latest.items():
        candidate = json.loads(files[f"snapshots/{event['candidate_digest']}/candidate.json"])
        a = candidate['A']
        ev = a['evidence']
        assert set(ev) == {f'T{i}' for i in range(1, 9)}
        pos = candidate['position_measurements']
        record = {k: event[k] for k in ('case_id', 'feature_id', 'feature_point', 'revision',
                                       'candidate_digest', 'crop_sha256', 'payload', 'utc')}
        record.update(split=candidate['split'], box=candidate['box'],
                      priority_context=candidate['priority_context'],
                      position_measurements=pos, algorithm=event['algorithm'],
                      candidate_path=f'photo2/review/r293/data/{cid}.json',
                      crop_path=f'photo2/review/r293/crops/{cid}.png',
                      candidate_pixel_count=a['candidate_pixels']['pixel_count'],
                      evidence=ev, separator_comparison=candidate['separator_comparison'],
                      patch_to_candidate_centroid_px=math.dist(
                          pos['independent_bright_patch'], pos['candidate_visible_region_centroid']))
        records.append(record)
    artifacts = ['photo2/R293_REPORT.md', 'photo2/R293_PRIORITY_POLICY.md',
                 'photo2/R293_COVERAGE.md', 'photo2/r293/results/phase1-observations.json.gz',
                 'photo2/r293/results/coverage.json', 'photo2/review/r293/manifest.json',
                 'photo2/review/r293/index.html', 'photo2/review/r293/app.js', 'photo2/r293/serve.py']
    history_keys = ('case_id', 'revision', 'logical_parent_revision', 'action', 'utc',
                    'payload', 'previous_payload', 'ownership_changes', 'ownership_previous',
                    'candidate_digest')
    return dict(
        schema='R293-completed-review-analysis-v1', source_revision=SOURCE_REVISION,
        source='photo2/r293/feedback/judgments.jsonl', original_ledger_sha256=digest(raw),
        archive='photo2/r293/evidence/' + ARCHIVE.name, archive_sha256=digest(packed(files)),
        ledger_archive='photo2/r293/evidence/' + LEDGER.name,
        ledger_archive_sha256=digest(gzip.compress(raw, mtime=0)), image_sha256=image_hash,
        original_files={k: dict(bytes=len(v), sha256=digest(v)) for k, v in sorted(files.items())},
        tracked_source_artifacts={p: digest((ROOT / p).read_bytes()) for p in artifacts},
        events=len(events), reviewed_cases=len(latest), revisions_after_first=len(events)-len(latest),
        final_answers=dict(collections.Counter(e['payload']['answer'] for e in latest.values())),
        start_here_total=len(manifest['start_here']),
        start_here_reviewed=sum(cid in latest for cid in manifest['start_here']),
        other_cases_unreviewed_in_r293=len(entries)-len(latest),
        optional_diagnostic_events=sum(bool(e['payload']['diagnostics']) for e in events),
        final_ownership=ownership, history=[{k: e[k] for k in history_keys} for e in events],
        records=records, verification=dict(archive_byte_exact=True, original_image=True,
            immutable_snapshot_versions=len(snapshot_ids), native_crops=len(snapshot_ids),
            event_provenance_checks=len(events), tracked_candidate_crop_pairs=len(latest)),
        interpretation='Human visible-region judgments, not pixel truth, physical centers, '
            'explicit ownership answers or population accuracy. No diagnoses were supplied. '
            'All source events and snapshots are archived intact. No detector inputs changed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        files = unpacked(ARCHIVE.read_bytes())
        assert ARCHIVE.read_bytes() == packed(files)
        assert gzip.decompress(LEDGER.read_bytes()) == files['judgments.jsonl']
        summary = analyze(files)
        assert SUMMARY.read_bytes() == encoded(summary), 'Summary replay mismatch'
    else:
        files = live_files()
        summary = analyze(files)
        OUT.mkdir(parents=True, exist_ok=True)
        for path, raw in ((ARCHIVE, packed(files)), (LEDGER, gzip.compress(files['judgments.jsonl'], mtime=0)),
                          (SUMMARY, encoded(summary))):
            if path.exists() and path.read_bytes() != raw:
                raise FileExistsError('Preserve prior archive; use a new version: ' + str(path))
            path.write_bytes(raw)
        assert unpacked(ARCHIVE.read_bytes()) == files
        assert live_files() == files, 'Live review changed during archival'
    print(json.dumps(dict(events=summary['events'], cases=summary['reviewed_cases'],
                          answers=summary['final_answers'], files=len(files),
                          verification=summary['verification']), sort_keys=True))


if __name__ == '__main__':
    main()
