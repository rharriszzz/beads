"""Manual visible-part centers and provisional, distinct nearest-anchor scores.

Observation numbers are independent of model generator indices. The scoring
target is deliberately a proxy: visible-part center versus exposed outward point.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import threading

import numpy as np
from scipy.optimize import linear_sum_assignment
from label_beads import atomic_json

KIND = 'visible_part_center'


def validate_marks(points, size):
    if not isinstance(points, list) or len(points) > 200:
        raise ValueError('Supply at most 200 center marks.')
    clean, ids, numbers = [], set(), set()
    for point in points:
        if not isinstance(point, dict):
            raise ValueError('Each center must be an object.')
        identity, number = point.get('id'), point.get('number')
        if not isinstance(identity, str) or not 1 <= len(identity) <= 80 or identity in ids:
            raise ValueError('Center IDs must be unique nonempty strings.')
        if type(number) is not int or not 1 <= number <= 100000 or number in numbers:
            raise ValueError('Center numbers must be unique positive whole numbers.')
        xy = []
        for key, limit in zip(['x', 'y'], size):
            value = point.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or not 0 <= value < limit:
                raise ValueError('Center coordinates must be finite and inside the photo.')
            xy.append(float(value))
        clean.append(dict(id=identity, number=number, x=xy[0], y=xy[1]))
        ids.add(identity); numbers.add(number)
    return clean


class CenterStore:
    def __init__(self, path, source, forbidden=()):
        self.path = Path(path).resolve()
        self.source = deepcopy(source)
        self.lock = threading.Lock()
        self.score_path = self.path.with_name(self.path.stem + '-score.json')
        paths = {self.path, self.score_path,
                 self.path.with_name(self.path.stem + '.previous.json'),
                 self.score_path.with_name(self.score_path.stem + '.previous.json')}
        if self.path.suffix != '.json' or paths.intersection(Path(p).resolve() for p in forbidden):
            raise ValueError('Use a separate --centers .json path, distinct from choices and existing labels.')
        self.read()  # Reject unrelated files before any mutation.
        if self.score_path.exists():
            self.read_score()

    def read(self):
        if not self.path.exists():
            return dict(schema_version=1, kind=KIND, source=self.source, revision=0, points=[])
        doc = json.loads(self.path.read_text())
        if not isinstance(doc, dict) or doc.get('schema_version') != 1 or doc.get('kind') != KIND or doc.get('source') != self.source:
            raise ValueError('The centers file belongs to another document or photo; use another --centers path.')
        if type(doc.get('revision')) is not int or doc['revision'] < 1:
            raise ValueError('Invalid center-file revision.')
        validate_marks(doc.get('points'), self.source['oriented_size'])
        return doc

    def save(self, payload, configuration, guides):
        if not isinstance(payload, dict):
            raise ValueError('Supply center points and their current revision.')
        points = validate_marks(payload.get('points'), self.source['oriented_size'])
        with self.lock:
            previous = self.read()
            if type(payload.get('revision')) is not int or payload['revision'] != previous['revision']:
                raise ValueError('Centers changed in another window. Download your draft before reloading.')
            doc = dict(schema_version=1, kind=KIND, source=self.source,
                       revision=previous['revision']+1, points=points,
                       coordinates='EXIF-oriented original photo pixels; x right, y down',
                       uncertainty='Maker-selected visible-area centers; numeric uncertainty unspecified.',
                       saved_at=datetime.now(timezone.utc).isoformat(),
                       viewer_reference=dict(configuration=deepcopy(configuration), guides=guides),
                       status='Manual observations; no inferred bead_index or model correspondence.')
            if self.path.exists():
                backup = self.path.with_name(self.path.stem + '.previous.json')
                self.check_backup(backup, KIND)
                atomic_json(backup, previous)
            atomic_json(self.path, doc)
        return dict(path=str(self.path), document=doc)

    def read_score(self):
        doc = json.loads(self.score_path.read_text())
        if not isinstance(doc, dict) or doc.get('kind') != 'center_count_score' or doc.get('schema_version') != 1 or doc.get('source') != self.source:
            raise ValueError('The score path contains an unrelated file; use another --centers path.')
        return doc

    def save_score(self, doc):
        with self.lock:
            if self.score_path.exists():
                backup = self.score_path.with_name(self.score_path.stem + '.previous.json')
                self.check_backup(backup, 'center_count_score')
                atomic_json(backup, self.read_score())
            atomic_json(self.score_path, doc)

    def check_backup(self, path, kind):
        if path.exists():
            doc = json.loads(path.read_text())
            if not isinstance(doc, dict) or doc.get('kind') != kind or doc.get('source') != self.source:
                raise ValueError(f'Backup contains an unrelated document: {path}. Choose another --centers path.')


def match_centers(points, frame):
    """Minimum squared-distance injective assignment; no observed index claim."""
    if not points:
        raise ValueError('Mark at least one visible bead center first.')
    predictions = np.asarray(frame['circles'], dtype=float).reshape(-1, 6)[:, :2]
    if len(predictions) < len(points):
        raise ValueError('This count has fewer exposed predictions than marked centers.')
    observed = np.array([[p['x'], p['y']] for p in points])
    delta = observed[:, None, :] - predictions[None, :, :]
    cost = np.sum(delta*delta, axis=2)
    rows, columns = linear_sum_assignment(cost)
    squared = cost[rows, columns]
    return dict(count=frame['count'], hand=frame['hand'], sse=float(squared.sum()),
                rms_pixels=float(np.sqrt(squared.mean())),
                matches=[dict(observation_id=points[r]['id'], number=points[r]['number'],
                              predicted_xy=predictions[c].tolist(),
                              tentative_generator_index=frame['generator_indices'][c],
                              distance_pixels=float(np.sqrt(cost[r, c]))) for r, c in zip(rows, columns)])


def score_counts(document, counts, hand, frame_provider, progress=None):
    if len(document['points']) < 3:
        raise ValueError('Mark at least three beads; 10–20 around the bracelet is the intended sample.')
    rows = []
    for i, count in enumerate(counts):
        row = match_centers(document['points'], frame_provider(count, hand))
        rows.append(row)
        if progress:
            progress(i+1, len(counts))
    best = min(rows, key=lambda row: row['sse'])
    return dict(schema_version=1, kind='center_count_score', source=document['source'],
                centers=deepcopy(document), hand=hand, counts=counts,
                metric='Sum of squared 2D distances, source-photo pixels squared; distinct nearest exposed outward predictions.',
                settings='Phase, origin, camera, spline and physical sizes fixed to the selected hand seed. Count changes projected scale and closure.',
                limitations='Visible-area centers are proxies for outward points; nearest matches may change with count. A minimum does not verify N or helicity.',
                rows=[{k: v for k, v in row.items() if k != 'matches'} for row in rows],
                best=best, saved_at=datetime.now(timezone.utc).isoformat())
