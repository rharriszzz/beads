"""Lossless compact transport of immutable proposal transactions.

Local per-candidate files remain in place. Git stores compressed JSONL chunks;
the entry point restores exact deterministic-gzip bytes when needed on a clone.
"""
from pathlib import Path
import gzip,json,os
from photo2.r297.common import read,save,sha

def pack(out,chunk_size=150):
    out=Path(out);paths=sorted((out/'candidates').glob('*.json.gz'));destination=out/'candidate-archive';destination.mkdir(exist_ok=True)
    chunks=[];count=0
    for first in range(0,len(paths),chunk_size):
        selected=paths[first:first+chunk_size];name=f'part-{first//chunk_size:04d}.jsonl.gz';path=destination/name;temp=path.with_suffix('.tmp')
        rows=[dict(name=p.name,sha256=sha(p),value=read(p)) for p in selected]
        payload=''.join(json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n' for r in rows).encode()
        with temp.open('wb') as f:f.write(gzip.compress(payload,mtime=0));f.flush();os.fsync(f.fileno())
        os.replace(temp,path);chunks.append(dict(name=name,sha256=sha(path),count=len(rows),first=selected[0].name,last=selected[-1].name));count+=len(rows)
    save(destination/'manifest.json',dict(count=count,chunks=chunks,format='Canonical JSON records plus original deterministic-gzip SHA256; no proposal or failed witness dropped.'))
    return dict(count=count,compressed_bytes=sum((destination/r['name']).stat().st_size for r in chunks),individual_bytes=sum(p.stat().st_size for p in paths))

def restore(out):
    out=Path(out);manifest=out/'candidate-archive/manifest.json'
    if not manifest.exists():return 0
    doc=read(manifest);n=0
    for part in doc['chunks']:
        target=out/'candidate-archive'/part['name']
        if sha(target)!=part['sha256']:raise ValueError('Proposal archive changed: '+str(target))
        with gzip.open(target,'rt') as f:
            for line in f:
                r=json.loads(line);path=out/'candidates'/r['name']
                if not path.exists():save(path,r['value']);n+=1
                if sha(path)!=r['sha256']:raise ValueError('Proposal byte replay mismatch: '+str(path))
    return n

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--restore',action='store_true');a=ap.parse_args();print(restore(a.output) if a.restore else pack(a.output))
