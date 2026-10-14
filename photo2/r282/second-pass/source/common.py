"""Shared schema, exact native supports and provenance. No phase-specific inference."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageCms

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('R282_OUTPUT', ROOT/'photo2/r282/results'))
PHOTO = ROOT/'beads-photo-2.jpg'
REQUIRED = ('record_id', 'phase_origin', 'importance', 'phase1_reliability',
            'phase2_identity_reliability', 'visibility', 'color', 'color_reliability',
            'measured_photo_location', 'measured_support', 'physical_model_index',
            'physical_model_confidence', 'notes')
COLORS = ('red', 'yellow', 'black')


def save(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, separators=(',', ':'), allow_nan=False)+'\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def read(path):
    path = Path(path); raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def photo():
    source = ImageOps.exif_transpose(Image.open(PHOTO))
    native = np.asarray(source.convert('RGB'))
    icc = source.info.get('icc_profile')
    if icc:
        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        converted = ImageCms.profileToProfile(source, profile, ImageCms.createProfile('sRGB'),
                      renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, outputMode='RGB')
    else:
        converted = source.convert('RGB')
    return native, np.asarray(converted), dict(photo_sha256=sha(PHOTO),
        icc_sha256=hashlib.sha256(icc).hexdigest() if icc else None,
        dimensions=list(source.size), convention='EXIF-transposed native pixel centers, x right/y down',
        appearance='ICC relative-colorimetric sRGB for measurements; original decoded RGB for review')


def runs(xy):
    xy = np.asarray(xy, int).reshape(-1, 2)
    if not len(xy): return []
    xy = np.unique(xy, axis=0); xy = xy[np.lexsort((xy[:, 0], xy[:, 1]))]
    result = []; x0 = last = int(xy[0, 0]); row = int(xy[0, 1])
    for x, y in xy[1:]:
        if y != row or x != last+1:
            result.append([row, x0, last]); row, x0 = int(y), int(x)
        last = int(x)
    result.append([row, x0, last]); return result


def pixels(region):
    return np.array([(x, y) for y, a, b in (region or {}).get('runs', []) for x in range(a, b+1)], int).reshape(-1, 2)


def support(xy):
    xy = np.asarray(xy, int).reshape(-1, 2)
    if not len(xy): return None
    return dict(runs=runs(xy), pixel_count=len(xy), centroid=xy.mean(0).tolist(),
                kind='measured interior; not full-body silhouette')


def record(identifier, phase):
    return dict(record_id=identifier, phase_origin=[phase], importance='high' if phase == 'phase1' else 'medium',
        phase1_reliability=0., phase2_identity_reliability=0., physical_identity_reliability=0.,
        visibility=None, visibility_kind='unmeasured', color='unknown', color_reliability=0.,
        measured_photo_location=None, measured_support=None, physical_model_index=None,
        physical_model_confidence=0., notes=[], evidence_links=[], phase_history=[phase])


def validate(record):
    assert all(k in record for k in REQUIRED), record.get('record_id')
    assert record['color'] in (*COLORS, 'unknown')
    assert set(record['phase_origin']) <= {'phase1', 'phase2', 'phase3'}
    for key in ('phase1_reliability', 'phase2_identity_reliability', 'color_reliability', 'physical_model_confidence'):
        assert 0 <= record[key] <= 1, (key, record['record_id'])
    if record['visibility'] is not None: assert 0 <= record['visibility'] <= 1
    if record['measured_support']:
        xy = pixels(record['measured_support'])
        assert len(xy) == record['measured_support']['pixel_count']
        np.testing.assert_allclose(xy.mean(0), record['measured_photo_location'], atol=1e-12)
    if record['phase_origin'] == ['phase1']:
        assert record['physical_model_index'] is None and record['phase2_identity_reliability'] == 0


def circular_distance(a, b):
    return np.abs((np.asarray(a)-b+180) % 360-180)
