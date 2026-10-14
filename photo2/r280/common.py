from pathlib import Path
import hashlib,json,gzip
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'photo2/r280/results'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 raw=(json.dumps(data,indent=2,allow_nan=False)+'\n').encode()
 if path.suffix=='.gz':
  with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(raw)
 else:path.write_bytes(raw)
def read(path):
 path=Path(path)
 return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def runs(mask):
 result=[]
 for y,row in enumerate(mask):
  a=np.diff(np.r_[False,row,False].astype(int));result.extend([int(y),int(x),int(z-1)] for x,z in zip(np.where(a==1)[0],np.where(a==-1)[0]))
 return result
def mask_from_runs(rr,shape):
 m=np.zeros(shape,bool)
 for y,x,z in rr:m[y,x:z+1]=True
 return m
