"""Atomic run artifacts and reproducibility fingerprints."""
import gzip
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from photo2.r282.common import ROOT, read, sha, photo, pixels

BASE = ROOT / 'photo2/r296'
EVIDENCE = BASE / 'evidence'
SCHEMA = 1

def utc():
    return datetime.now(timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def save(path, value):
    """Atomic replace; deterministic gzip; fsync before publishing checkpoint."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    if path.suffix == '.gz':
        raw = gzip.compress(raw, mtime=0)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)

def fingerprints():
    modules = ['r296', 'r295', 'r294', 'r293', 'r282', 'r280', 'r279']
    paths = [p for module in modules for p in (ROOT / 'photo2' / module).glob('*.py')]
    paths += [ROOT / 'photo2/phase2_autofit.py', ROOT / 'photo2/bead_placement.py']
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}
