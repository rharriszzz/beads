"""Read-only native audits of immutable incumbents during the fitting campaign."""
from pathlib import Path
import time
from photo2.r297.common import read,save
from .evidence import load
from .geometry import Chain,contact
from .objective import Objective,predict,contour_samples
from .export import native_envelope,native_assess

def audit(out):
    out=Path(out);state=read(out/'checkpoint.json');path=out/'native-progress.json.gz'
    progress=read(path) if path.exists() else []
    ident=state['pool'][0]
    if any(r['id']==ident for r in progress):return progress[-1]
    data,m,obs=load();obj=Objective(data,m,obs);obj.contour_samples=contour_samples([m['beads'][i] for i in obj.bi],1.)
    row=read(out/'candidates'/f'{ident:06d}.json.gz');s=Chain(row['parameters'],data);t=time.monotonic()
    cert=contact(s,exact=True);assert cert['certified']
    pred,meta=predict(s,1.,obj.obs);en=native_envelope(s,m);result=native_assess(s,obj,pred,en)
    record=dict(id=ident,search_elapsed_seconds=state['elapsed_seconds'],proposals=state['next_id'],search_loss=row['train']['loss'],
                native=result,numerics=meta,seconds=time.monotonic()-t,comparison_evidence_used=False)
    progress.append(record);save(path,progress)
    print(ident,'search',row['train']['loss'],'native',result['loss'],'audit seconds',record['seconds'],flush=True)
    return record

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);audit(ap.parse_args().output)
