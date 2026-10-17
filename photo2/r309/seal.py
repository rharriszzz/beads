"""Read-only scientific integrity checks and additive final source snapshot."""
from pathlib import Path
import subprocess
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import SOURCES
from .search import sources

def seal():
    base=ROOT/'photo2/r309';out=base/'results/campaign'
    checkpoint=read(out/'checkpoint.json')
    assert checkpoint['sealed']
    assert checkpoint['sources']==sources()
    assert checkpoint['evidence']=={p:sha(ROOT/p) for p in SOURCES}
    protected=read(base/'evidence/preservation.json.gz');head=read(base/'evidence/start.json')['head'];additive=[]
    for p,h in protected.items():
        if sha(ROOT/p)!=h:
            assert p in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md'],p
            old=subprocess.check_output(['git','show',head+':'+p]);assert old in (ROOT/p).read_bytes(),p
            additive.append(p)
    preservation=dict(passed=True,files=len(protected),byte_identical=len(protected)-len(additive),additive_handoffs=additive,historical_science_changed=[],start_head=head)
    save(out/'preservation-final.json',preservation)
    src=set(base.glob('*.py'))|{ROOT/'photo2/phase2_competing_fit.py',ROOT/'photo2/review/r309/serve.py',ROOT/'photo2/review/r309/launch.sh'}|{ROOT/p for p in sources()}
    manifest={}
    for p in sorted(src):
        rel=str(p.relative_to(ROOT));dst=base/'evidence/final-source'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes());assert sha(dst)==sha(p);manifest[rel]=sha(p)
    save(base/'evidence/final-source-manifest.json',manifest)
    exports={str(p.relative_to(out)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted((out/'exports').rglob('*')) if p.is_file()}
    save(out/'export-manifest.json',exports)
    summary=read(out/'analysis-summary.json')
    for rel in summary['links'].values():assert (out/rel).exists(),rel
    for name in ['verification','boundary-verification','browser-check']:assert read(out/f'{name}.json')['passed']
    result=dict(passed=True,recorded_utc=utc(),preservation=preservation,source_files=len(manifest),exports=len(exports),fit_source_and_evidence_unchanged=True,summary_links_exist=True)
    save(out/'final-integrity.json',result);return result
if __name__=='__main__':print(seal())
