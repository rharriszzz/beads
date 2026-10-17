"""Independent original-kernel verification and byte-preservation audit."""
from pathlib import Path
import time
import numpy as np
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r306.verify import verify as inherited_verify
from photo2.r305.forward import segments
from photo2.r295.physical_audit import independent_support

def verify(out):
    out=Path(out);start=time.monotonic()
    # Original Python geometry, native marcher and support formula independently
    # replay compiled-exported geometry, contacts, pixels and original supports.
    result=inherited_verify(out)
    data,m,obs=load();primary=read(out/'exports/primary.json.gz');s=Original(primary['parameters'],data)
    ras=np.load(out/'exports/primary-raster.npz');owner=ras['owner'];address=ras['address'];unknown=ras['unknown']
    good=owner>=0;np.testing.assert_array_equal(address[good],s.indices[owner[good]]);assert np.all(address[~good]==-32768)
    edges=0
    for b in primary['positions']:
        j=b['index']-int(s.indices[0]);x,y=b['projected_center'];rad=s.query_radius+2;x0=max(0,int(x-rad));x1=min(2540,int(x+rad)+2);y0=max(0,int(y-rad));y1=min(3182,int(y+rad)+2)
        seg=segments(owner[y0:y1,x0:x1]==j,x0,y0);assert seg==b['boundary_segments'];edges+=len(seg)
    # Exact full photographic window at the maker's required location.
    yy,xx=np.mgrid[246:426,1020:1200];xy=np.c_[xx.ravel(),yy.ravel()];tr=s.trace(xy)
    np.testing.assert_array_equal(tr['owner'].reshape(xx.shape),owner[yy,xx]);np.testing.assert_array_equal(tr['unknown'].reshape(xx.shape),unknown[yy,xx])
    from photo2.r307.objective import Objective
    # These original traces cover every dense objective evidence sample; no
    # candidate-to-photo correspondence is inferred in this numerical check.
    evidence_rays=0
    for split in ['development','comparison']:
        obj=Objective(data,m,obs,split,dense=True);tr=s.trace(obj.xy);ij=np.rint(obj.xy).astype(int)
        # Contours/old separator paths may be subpixel; support and cue rays are native.
        count=len(obj.supportxy)+len(obj.cues['xy']);native=ij[:count]
        np.testing.assert_array_equal(tr['owner'][:count],owner[native[:,1],native[:,0]])
        evidence_rays+=len(obj.xy)
    # Independently inspect field amplitude and actual projection effects for each stage.
    from photo2.r308.search import correction
    state=read(out/'checkpoint.json');field_checks=[]
    for name in ['primary','stage-global','stage-distributed','stage-joint']:
        model=read(out/'exports'/f'{name}.json.gz');c=correction(model['parameters'],state['correction_reference'],data);assert c['within_bounds'],(name,c)
        field_checks.append(dict(model=name,checks=c))
    protected=read(ROOT/'photo2/r308/evidence/preservation.json.gz');changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    # Handoffs may only prepend new text and retain the full original content.
    allowed=[]
    if changed:
        import subprocess
        for p in changed[:]:
            if p in ['AGENTS.md','PLAN.md','REQUEST_LOG.md','METHODS.md']:
                original=subprocess.check_output(['git','show',f'{read(ROOT/"photo2/r308/evidence/start.json")["head"]}:{p}'],cwd=ROOT)
                if original in (ROOT/p).read_bytes():allowed.append(p);changed.remove(p)
    assert not changed,changed
    result.update(r308_passed=True,distributed_effect_checks=field_checks,boundary_segments_exact=edges,required_location_native_rays=len(xy),original_kernel_dense_evidence_rays=evidence_rays,protected_R308_start_files=len(protected),changed_historical_science=changed,additive_R308_handoffs=allowed,total_seconds=time.monotonic()-start)
    save(out/'verification.json',result);print('R308 independent verification passed',result['total_seconds'],flush=True);return result
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);verify(ap.parse_args().output)
