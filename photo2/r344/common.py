"""Fixed historical inputs and transparent color-authority strata."""
import copy
import csv
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np

OUT = Path(os.environ.get('R344_RUN_ROOT', ROOT / 'photo2/r344'))
OUT.mkdir(parents=True, exist_ok=True)
BASE = '6fa108f7c378bdecf55fcaad8fc99387869f8188'
COLORS = ['red', 'yellow', 'black']  # Historical tie order, unchanged.
LETTERS = {'red': 'R', 'yellow': 'Y', 'black': 'B'}
CORRECTIONS = ['NEW-1519-2976', 'R332-R-0125-0118']


def read(path):
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as f:
        return json.load(f)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, allow_nan=False, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x.item()) + '\n'
    if path.suffix == '.gz':
        path.write_bytes(gzip.compress(text.encode(), mtime=0))
    else:
        path.write_text(text)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_graph(path):
    g = read(path)
    return g, {r['id']: r for r in g['observations']}, {r['id']: r['ab'] for r in g['coordinates']}


def index(ab, hand='A'):
    a, b = ab
    return (7*a + 6*b) % 2704 if hand == 'A' else (6*a + 7*b) % 2691


def authority(o, ledger):
    if o not in ledger:
        return 'native_software_label'
    source = ledger[o]['source']
    if 'accepted' in source:
        return 'illustration_label_approval'
    return 'explicit_individual_pigment'


def frozen_inputs():
    return read(ROOT/'photo2/r343/pattern-analysis.json')['blocks']
