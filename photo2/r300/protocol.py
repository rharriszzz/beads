"""Record preservation and diagnostic choices before computing R300 outcomes."""
import subprocess
from photo2.r297.common import ROOT, save, sha, utc
BASE=ROOT/'photo2/r300'
if __name__=='__main__':
    target=BASE/'evidence/start.json'
    if target.exists(): raise SystemExit('Already frozen')
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    excluded={'AGENTS.md','SESSION_HANDOFF.md','PLAN.md','REQUEST_LOG.md'}
    paths={ROOT/n for n in names if n and n not in excluded and not n.startswith(('photo2/r300/','photo2/review/r300/','photo2/R300_'))}
    paths|={p for p in (ROOT/'photo2').glob('**/feedback/**/*') if p.is_file()}
    save(BASE/'evidence/preservation.json.gz',{str(p.relative_to(ROOT)):sha(p) for p in sorted(paths) if p.is_file()})
    save(target,dict(utc=utc(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),method='All 19 frozen R299 native exports; predicted minus observed. Common R282 photographic reference arc from R296 anchor in increasing-index direction. No owner or light changes. 16 equal arc bins, leave-bin-out slope sensitivity, sector bootstrap and cyclic-origin sensitivity; both peaks and centroids. Actual family index seams separately at 3%, 6%, 10% windows. Local signed displacement / centerline pitch is an index-equivalent diagnostic, never an observed integer error. Increment sums telescope; do not sum location residuals as count error. No absolute accuracy gate.',decision='Diagnose first. No fitting unless convincing progressive drift suggests a shared physical correction. All geography retrospective.'))
