import gzip,json,hashlib,os
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASE='8c8ecab00f726c2010c2571e9ada953a60e878dc'
def artifact(path=''):return Path(os.environ.get('R336_RUN_ROOT',ROOT/'photo2/r336'))/path
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    def cast(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        if isinstance(x,set):return sorted(x)
        raise TypeError(type(x).__name__)
    with (gzip.open(p,'wt') if str(p).endswith('.gz') else open(p,'w')) as f:json.dump(value,f,default=cast,allow_nan=False,indent=None if str(p).endswith('.gz') else 2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rep(ab,H=(214,201)):
    a,b=map(int,ab);q=a//H[0];return a-q*H[0],b-q*H[1]
