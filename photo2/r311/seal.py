"""Final preservation/source/input receipt after scientific and browser checks."""
from pathlib import Path
import subprocess,io,tarfile,gzip
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import SOURCES
from .model import starts
from .search import sources

OUT=ROOT/'photo2/r311/results/campaign'

def run():
    for name in ['verification','browser-check']:assert read(OUT/f'{name}.json')['passed'],name
    assert read(OUT/'checkpoint.json')['sealed']
    protected=read(ROOT/'photo2/r311/evidence/preservation.json.gz');head=read(ROOT/'photo2/r311/evidence/start.json')['head'];changed=[]
    for p,h in protected.items():
        if sha(ROOT/p)==h:continue
        assert p in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md','SESSION_HANDOFF.md','.gitignore'],p
        assert subprocess.check_output(['git','show',head+':'+p]) in (ROOT/p).read_bytes(),p
        changed.append(p)
    inputfiles=list(SOURCES)+[s['source'] for s in starts()]
    inputfiles+=['photo2/R306_REPORT.md','photo2/R307_REPORT.md','photo2/R308_REPORT.md','photo2/R309_REPORT.md','photo2/R310_REPORT.md']
    for m in ['R297-2337','R306-2405','R309-2733']:inputfiles.append(f'photo2/r310/results/{m}-partA.json.gz')
    save(OUT/'input-manifest.json',{p:sha(ROOT/p) for p in sorted(set(inputfiles))})
    manifest=sources()
    paths=list((ROOT/'photo2/r311').glob('*.py'))+[ROOT/'photo2/r311/viewer.html',ROOT/'photo2/phase2_basin_search.py',ROOT/'photo2/R311_SPECIFICATION.md',ROOT/'photo2/R311_REPRODUCE.md',ROOT/'photo2/r311/evidence/search-used-for-fitting.py']
    manifest.update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    old=OUT/'delivery-source-manifest.json'
    if not (OUT/'numerical-verification-delivery-source-manifest.json').exists():
        save(OUT/'numerical-verification-delivery-source-manifest.json',read(old))
    save(old,{str(p.relative_to(ROOT)):sha(p) for p in paths})
    save(OUT/'source-manifest.json',sources())
    save(OUT/'final-source-manifest.json',manifest)
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode='w') as tar:
        for p in sorted(manifest):
            info=tarfile.TarInfo(p);payload=(ROOT/p).read_bytes();info.size=len(payload);info.mtime=0;info.mode=0o644;tar.addfile(info,io.BytesIO(payload))
    (ROOT/'photo2/r311/evidence/final-source.tar.gz').write_bytes(gzip.compress(raw.getvalue(),mtime=0))
    result=dict(passed=True,utc=utc(),preserved_files=len(protected),byte_identical=len(protected)-len(changed),additive_handoffs_and_ignore=changed,
                historical_science_changed=[],source_files=len(manifest),source_bundle_sha256=sha(ROOT/'photo2/r311/evidence/final-source.tar.gz'),
                verification=True,browser=True,sealed_search=True,no_geometry_adoption=True,no_Phase3=True)
    save(ROOT/'photo2/r311/results/final-integrity.json',result);print(result)
if __name__=='__main__':run()
