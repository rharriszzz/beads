"""Lossless delivery compression; immutable scientific bytes remain recoverable."""
import gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def main():
    paths=list((ROOT/'photo2/r326/development').rglob('*.json'))
    # Primary graph/model/context remain plain JSON. Large per-pass snapshots and
    # duplicate R325 baseline graph are archives; the verifier transparently reads.
    paths+=list((OUT/'full').glob('iteration-*.json'))+list((OUT/'practice').glob('iteration-*.json'))
    paths+=[OUT/'full/baseline/graph.json']
    receipts=[]
    for p in paths:
        if not p.exists() or p.stat().st_size<100000:continue
        raw=p.read_bytes();dest=p.with_suffix(p.suffix+'.gz');compressed=gzip.compress(raw,compresslevel=6,mtime=0);dest.write_bytes(compressed);assert gzip.decompress(dest.read_bytes())==raw
        receipts.append(dict(original=str(p.relative_to(ROOT)),compressed=str(dest.relative_to(ROOT)),original_bytes=len(raw),compressed_bytes=len(compressed),sha256=hashlib.sha256(raw).hexdigest(),compressed_sha256=hashlib.sha256(compressed).hexdigest()));p.unlink()
    (OUT/'archive-compression.json').write_text(json.dumps(dict(lossless=True,files=receipts),indent=2)+'\n');print('compressed',len(receipts),'bytes',sum(r['original_bytes'] for r in receipts),'to',sum(r['compressed_bytes'] for r in receipts))
if __name__=='__main__':main()
