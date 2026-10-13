"""Compress R266 trace containers without changing any native trace payload."""
import gzip,hashlib,json,shutil,tarfile
from pathlib import Path
from .experiment_r266 import OUT,WORK,save


def main():
    records=json.loads((OUT/'trace-packaging.json').read_text())['archives'] if (OUT/'trace-packaging.json').exists() else []
    for root in (OUT,WORK):
        for csv in root.glob('*/coordinates.csv'):
            csv.write_text(csv.read_text()) # Normalize CSV line endings only.
    for path in sorted(OUT.glob('*/traces.tar')):
        out=path.with_suffix('.tar.gz')
        with path.open('rb') as source,gzip.GzipFile(filename=str(out),mode='wb',mtime=0,compresslevel=6) as dest:shutil.copyfileobj(source,dest)
        # Verify the decoded complete tar before removing the redundant generated tar.
        original=hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(out,'rb') as f:decoded=hashlib.sha256(f.read()).hexdigest()
        assert original==decoded
        records.append(dict(path=str(out.relative_to(OUT)),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),uncompressed_tar_sha256=original,bytes=out.stat().st_size))
        path.unlink()
    save(OUT/'trace-packaging.json',dict(verified_lossless=True,archives=records))
    print('Compressed',len(records),'trace archives')
if __name__=='__main__':main()
