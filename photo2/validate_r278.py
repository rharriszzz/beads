"""Reproducible image-only controls and immutable-input audit."""
from __future__ import annotations
import argparse,copy,gzip,json,hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from .bead_detection.phase1_r278 import recover,confidence_gate,resolve,WholePhoto,OUT
from .bead_detection.coverage_r272 import detect
from .bead_detection.synthetic_r274 import scenes
from .bead_detection.evaluate_coverage_r272 import scenes as others,metric,add_metrics,finish
from .bead_debugger.generate import save,sha,ROOT


def synthetic():
    total={c:Counter() for c in ('black','red','yellow')};records=[]
    items=list(scenes())+[(n,r,t,c) for n,r,t,c,_ in others()]
    for name,rgb,truth,colors in items:
        base=detect(rgb)[0];old=dict(beads=[],locations=[])
        _,fs,proposals=recover(rgb,rgb,old,base)
        for r in proposals:confidence_gate(r)
        beads,loc,decisions=resolve(proposals,old,WholePhoto())
        m,associations=metric(beads,truth,colors);add_metrics(total,m)
        records.append(dict(scene=name,features=len(fs),accepted=len(beads),metrics=m,associations=associations,
                            failures=[dict(id=r['id'],reasons=r['reasons']) for r in decisions if not r['accepted']]))
        if len(records)%10==0:print('synthetic',len(records),flush=True)
    save(OUT/'synthetic-image.json',dict(scenes=len(records),metrics=finish(total),records=records,
              protocol='New recovery from empty trusted inventory. Palette learned from automatic original detector. Truth evaluates only; not a photographic completeness claim.'))
    print(finish(total),flush=True)


def preservation():
    source=json.loads((ROOT/'photo2/review/r275/inventory.json').read_text())
    with gzip.open(OUT/'phase1-inventory.json.gz','rt') as f:new=json.load(f)
    for key in ('locations','beads'):
        byid={r['id']:r for r in new[key]}
        assert all(r==byid[r['id']] for r in source[key]),key
    checks=json.loads((OUT/'preserved-input-hashes.json').read_text())
    changed=[p for p,h in checks.items() if sha(ROOT/p)!=h]
    assert changed==['photo2/bead_placement.py'],changed
    accepted=[r for r in new['beads'] if r['id'] not in {b['id'] for b in source['beads']}]
    assert all(r['region']['pixel_count']<=870 for r in accepted)
    save(OUT/'preservation.json',dict(unchanged_prior_locations=len(source['locations']),unchanged_prior_masks=len(source['beads']),
        prior_files=len(checks),unchanged_prior_files=len(checks)-len(changed),intentional_shared_code_changes=changed,
        reason='Explicit optional radius_convention; legacy default and numerical replay preserved.',
        source_sha256=sha(ROOT/'beads-photo-2.jpg'),phase1_sha256=sha(OUT/'phase1-inventory.json.gz')))


def native():
    from PIL import Image,ImageOps
    from .bead_detection.brightness_r270 import color_managed_photo,linearize
    from .reconstruct_r276 import pixels
    from .reproduce_r278 import EXPORTED
    source=json.loads((ROOT/'photo2/review/r275/inventory.json').read_text());old={b['id'] for b in source['beads']}
    with gzip.open(OUT/'phase1-inventory.json.gz','rt') as f:inv=json.load(f)
    rgb,_=color_managed_photo();raw=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);n=0
    for b in inv['beads']:
        if b['id'] in old:continue
        pp=pixels(b['region']['runs']);assert len(pp)==b['region']['pixel_count']<=870
        np.testing.assert_allclose(pp.mean(0),b['region']['centroid'],atol=1e-12)
        p=b['brightest'];x,y=p['x'],p['y'];assert any(np.all(pp==[x,y],axis=1))
        assert abs(lum[y,x]-p['luminance'])<1e-12
        assert abs(lum[pp[:,1],pp[:,0]].max()-p['luminance'])<1e-12
        assert raw[y,x].tolist()==p['rgb_native'];assert rgb[y,x].tolist()==p['rgb_srgb'];n+=1
    ledgers={}
    for name in EXPORTED:
        with gzip.open(OUT/(name+'-correspondence.json.gz'),'rt') as f:d=json.load(f)
        beads=d['beads'];count=len(beads);ids=[b['phase1_id'] for b in beads if b['phase1_id'] is not None]
        assert len(ids)==len(set(ids));assert len(d['observations'])==len(inv['locations'])
        for k,b in enumerate(beads):
            assert b['candidate_index']==k
            assert all(v==(k+int(delta))%count for delta,v in b['neighbors'].items())
        ledgers[name]=dict(beads=count,observations=len(d['observations']),one_to_one=True,modulo_neighbors=True)
    save(OUT/'native-validation.json',dict(new_interiors_checked=n,exact_peaks_rgb_centroids=True,ledgers=ledgers))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['synthetic','preservation','native']);a=p.parse_args()
    if a.stage=='synthetic':synthetic()
    elif a.stage=='native':native()
    else:preservation()
