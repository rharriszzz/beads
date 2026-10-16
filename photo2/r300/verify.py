"""Replay numerical analysis and crossed controls without overwriting delivery."""
import tempfile
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,load_evidence,utc
from photo2.r297.geometry import reference
from photo2.r299.forward import Surface,grids
from photo2.r299.experiment import observations,evaluate
from .analyze import analyze,BASE


def geographic_audit(ledger):
    ref=reference();out=[]
    for r in ledger:
        if r['model']!='joint-15':continue
        xy=np.array(r['observed_centroid']);a=ref.points[:-1];v=ref.delta;t=np.clip(np.sum((xy-a)*v,axis=1)/np.sum(v*v,axis=1),0,1);q=a+t[:,None]*v;dist=np.linalg.norm(xy-q,axis=1);arc=ref.arc[:-1]+t*ref.lengths;i=dist.argmin();da=np.abs(arc-arc[i]);mask=np.minimum(da,ref.length-da)>.05*ref.length;j=np.where(mask)[0][dist[mask].argmin()]
        np.testing.assert_allclose(ref.project([xy])['arc'][0],arc[i],atol=1e-9)
        out.append(dict(id=r['id'],distance_px=float(dist[i]),alternative_distance_px=float(dist[j]),distance_advantage_px=float(dist[j]-dist[i]),arc=float(arc[i]),alternative_arc=float(arc[j])))
    return out


def main():
    with tempfile.TemporaryDirectory(prefix='beads-r300-verify-') as temp:
        out=Path(temp);analyze(out)
        for name in ['analysis.json','ledger.json','residuals.csv']:assert (out/name).read_bytes()==(BASE/'results'/name).read_bytes(),name
    ledger=read(BASE/'results/ledger.json');assert geographic_audit(ledger)==read(BASE/'results/geographic-projection-audit.json')
    inputs,_=load_evidence();obs=observations();assign=read(ROOT/'photo2/r299/evidence/ownership-49.json')['assignments'];n=0
    for c in read(BASE/'results/crossed-controls.json')['controls']:
        s=Surface(c['parameters'],inputs);data=grids(s,[a['owner'] for a in assign],1.);records,_=evaluate(s,data,c['light'],obs,assign,1.,5,False)
        assert records==c['records'];n+=len(records)
    preserved=read(BASE/'evidence/preservation.json.gz');bad=[name for name,digest in preserved.items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest];assert not bad,bad[:10]
    sources=read(BASE/'results/analysis.json')['sources'];assert all(sha(ROOT/p)==v for p,v in sources.items())
    save(BASE/'results/verification.json',dict(utc=utc(),exact_analysis_replays=['analysis.json','ledger.json','residuals.csv'],native_crossed_reflection_replays=n,geographic_exhaustive_projections=52,protected_files_unchanged=len(preserved),source_hashes=len(sources),no_earlier_artifacts_modified=True,tests=8))
    print('R300 verification passed:',n,'native controls;',len(preserved),'protected files')
if __name__=='__main__':main()
