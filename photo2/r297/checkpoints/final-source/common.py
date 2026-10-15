"""Atomic run artifacts and reproducibility fingerprints."""
import gzip
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from photo2.r282.common import ROOT, read, sha, photo, pixels

BASE = ROOT / 'photo2/r297'
EVIDENCE = ROOT / 'photo2/r296/evidence'
SCHEMA = 2

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
    modules = ['r297', 'r296', 'r295', 'r294', 'r293', 'r282', 'r280', 'r279']
    paths = [p for module in modules for p in (ROOT / 'photo2' / module).glob('*.py')]
    paths += [ROOT / 'photo2/phase2_autofit.py', ROOT / 'photo2/bead_placement.py', BASE/'debugger.html', BASE/'evidence/protocol.json', ROOT/'photo2/r295/results/R295-evaluation.json', ROOT/'photo2/r296/results/pilot/exports/evaluation-188.json.gz']
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}


def environment():
    import sys
    import numpy
    import scipy
    import PIL
    return dict(python=sys.version, numpy=numpy.__version__, scipy=scipy.__version__, pillow=PIL.__version__)


from contextlib import contextmanager

@contextmanager
def run_lock(directory):
    """One CLI writer per run; OS releases the advisory lock after a hard kill."""
    import fcntl
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    with (directory/'.writer.lock').open('a+') as stream:
        try:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f'Run directory is already in use: {directory}. Do not start a second writer.')
        try:
            stream.seek(0);stream.truncate();stream.write(str(os.getpid())+'\n');stream.flush()
            yield
        finally:
            fcntl.flock(stream,fcntl.LOCK_UN)


def load_evidence(expected=None):
    """Bind search and standalone review to the same unchanged photo measurements."""
    data=read(EVIDENCE/'inputs.json.gz');frozen=read(EVIDENCE/'freeze.json')
    for filename,key in [('inputs.json.gz','inputs_sha256'),('cues.npz','cues_sha256')]:
        if sha(EVIDENCE/filename)!=frozen[key]:raise ValueError('Frozen evidence changed: '+filename)
    for filename,value in data['sources'].items():
        if sha(ROOT/filename)!=value:raise ValueError('Input changed: '+filename)
    if expected is not None:
        if expected['evidence']!=frozen['inputs_sha256'] or expected['photographic_cues']!=frozen['cues_sha256']:
            raise ValueError('Checkpoint photographic evidence differs from current freeze')
    return data,frozen
