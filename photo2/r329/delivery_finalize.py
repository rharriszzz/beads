"""Presentation-only LF normalization; retain exact pre-normalization CSV bytes."""
import csv,gzip,io,json,hashlib
from pathlib import Path

def main():
 root=Path(__file__).resolve().parents[2];p=root/'photo2/r329/results/count-coverage.csv';raw=p.read_bytes();before=list(csv.DictReader(io.StringIO(raw.decode())))
 normalized=raw.replace(b'\r\n',b'\n');after=list(csv.DictReader(io.StringIO(normalized.decode())));assert before==after
 archive=root/'photo2/r329/development/count-coverage-original-crlf.csv.gz'
 if b'\r\n' in raw:
  if not archive.exists():
   with gzip.open(archive,'wb') as f:f.write(raw)
  p.write_bytes(normalized)
 receipt=dict(change='CSV CRLF to LF only; all 1601 count records exact',science_changed=False,rows=len(after),current_sha256=hashlib.sha256(normalized).hexdigest(),original_archive=str(archive.relative_to(root)))
 (root/'photo2/r329/results/presentation-correction.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
if __name__=='__main__':main()
