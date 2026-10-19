import json,gzip,hashlib
from pathlib import Path
import numpy as np
from photo2.r329.common import canonical

ROOT=Path(__file__).resolve().parents[2]
BASE='4b6c9a293ca18e912748f6ff1bfa2628519fd7c9'
STEPS=((1,0),(0,1),(1,-1))
DIRECTIONS=STEPS+tuple((-a,-b) for a,b in STEPS)
FAMILY={(1,0):'F0',(0,1):'F1',(1,-1):'difference'}
REGIONS=[('G',[1510,205,1750,375]),('upper-F',[1200,195,1515,390]),
    ('upper-bend',[1760,390,2100,710]),('inward',[1640,1485,1810,1645]),
    ('lower-H',[1035,2785,1260,3010]),('lower-bridge',[1230,2860,1650,3160]),
    ('black-left',[175,1295,430,1545]),('black-outer',[2180,1720,2380,2120]),
    ('lower-left',[800,2440,1100,2760]),('black-dim-left',[220,740,485,1085]),
    ('new-black-body',[1240,1410,1450,1625])]
def read(path):
    with (gzip.open(path,'rt') if str(path).endswith('.gz') else open(path)) as f:return json.load(f)
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    def scalar(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        if isinstance(v,set):return sorted(v)
        raise TypeError(type(v).__name__)
    data=json.loads(json.dumps(obj,default=scalar,allow_nan=False))
    with (gzip.open(path,'wt') if str(path).endswith('.gz') else open(path,'w')) as f:json.dump(data,f,indent=None if str(path).endswith('.gz') else 2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def baseline():
    g=read(ROOT/'photo2/r328/results/graph.json.gz');state=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'][0]
    return g,canonical(state),tuple(state['H'])
def inside(xy,box):return box[0]<=xy[0]<box[2] and box[1]<=xy[1]<box[3]
def edgekey(a,z):return tuple(sorted((a,z)))
def representative(ab,H):
    # Keep original winding quotient; physical occupancy is modulo H only.
    a,b=map(int,ab);turn=a//H[0];return a-turn*H[0],b-turn*H[1]
