"""Cheap final preservation, correspondence-control and artifact sealing audit."""
from pathlib import Path
import subprocess
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,utc
from .verify import recompute
from .delivery import source_bundle

def run():
    root=ROOT/'photo2/r312/results/campaign';receipt=read(root/'verification.json');assert receipt['passed']
    for control in read(root/'full-necklace-optical-pool-control.json.gz')['models']:
        model=read(root/f'stage2/exports/{control["name"]}.json.gz');byid={r['id']:r for r in control['full_pool_rows']}
        for k,v in recompute(control['full_pool_rows']).items():assert abs(v-model['result']['metrics'][k])<1e-8
        for r in model['result']['reflections']:
            q=byid[r['id']]['predicted']
            if r['predicted'] is None:assert q is None
            else:np.testing.assert_allclose(r['predicted'],q,atol=1e-9,rtol=0)
    protected=read(ROOT/'photo2/r312/evidence/preservation.json.gz');head=read(ROOT/'photo2/r312/evidence/start.json')['head'];additive=[]
    for path,digest in protected.items():
        if sha(ROOT/path)==digest:continue
        assert path in ['AGENTS.md','METHODS.md','PLAN.md','REQUEST_LOG.md','SESSION_HANDOFF.md','.gitignore'],path
        original=subprocess.check_output(['git','show',head+':'+path]);assert original in (ROOT/path).read_bytes(),path;additive.append(path)
    assert read(root/'static-review-check.json')['passed']
    for stage in [1,2]:assert read(root/f'stage{stage}/checkpoint.json')['sealed']
    assert read(root/'stage2/local/checkpoint.json')['sealed']
    paths=list((ROOT/'photo2/r312').glob('*.py'))+[ROOT/p for p in ['photo2/phase2_minimax.py','photo2/R312_REPORT.md','photo2/R312_REPRODUCE.md','photo2/R312_SPECIFICATION.md','AGENTS.md','METHODS.md','PLAN.md','REQUEST_LOG.md','SESSION_HANDOFF.md','.gitignore','photo2/r312/evidence/implementation-checks/primary-verifier-source.py']]
    source_bundle(ROOT/'photo2/r312/evidence/delivery-source',{str(p.relative_to(ROOT)):sha(p) for p in paths})
    files=list((ROOT/'photo2/r312').rglob('*'))+[ROOT/p for p in ['photo2/phase2_minimax.py','photo2/R312_REPORT.md','photo2/R312_REPRODUCE.md','photo2/R312_SPECIFICATION.md']]
    files=[p for p in files if p.is_file() and '__pycache__' not in p.parts and p.name not in ['.writer.lock','artifact-manifest.json.gz','final-checks.json','delivery.json']]
    manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)};save(root/'artifact-manifest.json.gz',manifest)
    result=dict(passed=True,utc=utc(),historical_files_checked=len(protected),additive_handoffs=additive,artifact_files=len(manifest),artifact_manifest_sha256=sha(root/'artifact-manifest.json.gz'),primary_verification_sha256=sha(root/'verification.json'),primary_verifier_source_epoch_sha256=sha(ROOT/'photo2/r312/evidence/implementation-checks/primary-verifier-source.py'),supplemental_full_pool_control_passed=True,photographic_identities_verified=0,policy='Primary fresh-process native replay source is preserved. The later full-pool diagnostic receives this separate fresh-process arithmetic/centroid audit. No new fitting or repeated native replay.')
    save(root/'final-checks.json',result);print(result,flush=True)

if __name__=='__main__':run()
