"""Native forward replay, immutable pixels, independent contacts, fit replay."""
import time
import numpy as np
from PIL import Image,ImageOps
from .common import *
from .experiment import *
from .export import runs
from .measure import measure
from photo2.r298.geometry import contact

def main():
    start=time.monotonic();protected=read(BASE/'evidence/preservation.json.gz');changed=[p for p,v in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=v];assert not changed,changed
    for p,h in read(BASE/'evidence/fit-freeze.json')['files'].items():assert sha(ROOT/p)==h,p
    old=read(BASE/'evidence/measurements.json.gz');again,_=measure();old.pop('utc');again.pop('utc');assert again==old
    rows=observations();inputs,_=load_evidence();checks=[];manifest=read(BASE/'results/export-manifest.json');native=np.array(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    for i,r in enumerate(rows):
        x,y=r['peak'];crop=np.array(Image.open(REVIEW/f'raw-{i:02}.png'));np.testing.assert_array_equal(crop,native[y-45:y+46,x-45:x+46])
    for name in manifest['models']:
        result=read(BASE/f'results/native-{name}.json.gz');s=Surface(result['parameters'],inputs);np.testing.assert_array_equal(s.pc,result['positions']);np.testing.assert_array_equal(s.centers,result['world_centers']);cert=contact(s,exact=True);assert cert==result['geometry']['physical']
        # Replay every assigned primary peak and centroid, including missing.
        assign=read(BASE/f"evidence/ownership-{result['baseline']}.json")['assignments'];owners=sorted(set(a['owner'] for a in assign)|set(b['owner'] for a in assign for b in a['alternatives']));data=grids(s,owners,1.);rr,diag=evaluate(s,data,result['light'],rows,assign,1.,5,True)
        for a,b in zip(rr,result['records']):
            assert a['predicted']==b['predicted'],(name,a['id']);assert a['exists']==b['exists'];assert a['peak_error_px']==b['peak_error_px'];assert a['centroid_error_px']==b['centroid_error_px']
        assert summary(rr)==result['summary'];assert diag==result['shadow']
        for k in set(a['owner'] for a in assign)-{-1}:assert runs(data['xy'][data['owner']==k])==result['visible_surfaces'][str(k)]
        checks.append(dict(model=name,positions=s.n,contact_pairs=cert['pairs'],reflection_replays=len(rr),native_visible_samples=len(data['xy'])))
    fixed=read(BASE/'results/fixed-49-directional.json.gz');s=Surface(fixed['parameters'],inputs);assign=read(BASE/'evidence/ownership-49.json')['assignments'];data=grids(s,[a['owner'] for a in assign],2.);fit=light_fit(s,data,rows,assign,'directional',budget=22);assert fit==fixed['fit']
    # Every geometric trial retains its exact physical certificate, including rejected trials.
    hist=read(BASE/'results/joint-history.json.gz')
    for r in hist:assert contact(Surface(r['parameters'],inputs))==r['geometry']['physical']
    save(BASE/'results/verification.json',dict(utc=utc(),protected_files=len(protected),changed=changed,measurements_replayed=len(again['observations']),raw_crops=len(rows),models=checks,full_light_fit_replay_evaluations=len(fit['history']),physical_trial_replays=len(hist),elapsed=time.monotonic()-start,environment=environment()))
    print('R299 preservation, native predictions, physical and deterministic fit replay passed',flush=True)
if __name__=='__main__':main()
