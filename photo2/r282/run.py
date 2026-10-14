"""One-way integrated entry point. Every phase runs before any repair iteration."""
from datetime import datetime,timezone
from . import phase1,phase2,phase3
from .common import OUT,save,sha,ROOT


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'pipeline-complete.json').exists(),'Preserve each completed run; use a new R282_OUTPUT for another pass'
    started=datetime.now(timezone.utc).isoformat()
    phase1.main();phase2.main();phase3.main()
    save(OUT/'pipeline-complete.json',dict(started=started,finished=datetime.now(timezone.utc).isoformat(),
         phases=['phase1','phase2','phase3'],source_hashes={p.name:sha(p) for p in (ROOT/'photo2/r282').glob('*.py')},
         phase1_sha256=sha(OUT/'phase1.json.gz'),phase2_sha256=sha(OUT/'phase2.json'),phase3_sha256=sha(OUT/'phase3.json'),
         note='All phases executed before post-run repair decisions. Scientific acceptance is separate from execution.'))


if __name__=='__main__':main()
