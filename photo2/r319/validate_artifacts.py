"""Independent exported-ledger invariants, original pixels and static links."""
import csv,re
from pathlib import Path
import numpy as np
from PIL import Image
from .common import *

def main():
    b=read(OUT/'baseline.json.gz');best=read(OUT/'best-full.json.gz');summary=read(OUT/'summary.json');ev=read(OUT/'evidence-policy.json');outlines=read(OUT/'per-body-outline-response.json.gz');count=0;differences=[]
    assert len(outlines['rows'])==summary['feasible']
    for r in outlines['rows']:
        assert len(r['bodies'])==22
        for z in r['bodies']:
            assert z['visible_pixels']<=z['isolated_pixels'];assert sum(v['pixels'] for v in z['occluders'])==z['occluded_pixels'];delta=z['isolated_pixels']-z['visible_pixels']-z['occluded_pixels']
            if delta:differences.append(dict(trial=r['trial'],index=z['index'],isolated_minus_visible_occluded=delta))
            assert delta>=0
            if r['trial']==0:assert z['symmetric_boundary_mean_px']==0 and z['visible_pixel_changes']==0
            count+=1
    x,y=ev['origin'];h,w=ev['shape'];im=np.array(Image.open(ROOT/'beads-photo-2.jpg'));raw=np.array(Image.open(OUT/'raw-photo.png'));np.testing.assert_array_equal(raw,im[y:y+h,x:x+w])
    page=(OUT/'index.html').read_text();links=re.findall(r'(?:href|src)="([^"]+)"',page)
    for link in links:assert (OUT/link).exists(),link
    # Recompute all CSV movements and error changes against explicit parent.
    trials={}
    def get(i):
        if i not in trials:trials[i]=read(OUT/'trials'/f'{i:05}.json.gz')
        return trials[i]
    csvchecks=0
    with (OUT/'all-reflection-responses.csv').open() as f:
        for r in csv.DictReader(f):
            p=get(int(r['parent_trial']));q=next(z for z in p['rows'] if z['id']==r['id']);assert abs(float(r['predicted_x'])-q['predicted'][0]-float(r['movement_x']))<1e-10;assert abs(float(r['error'])-q['error_px']-float(r['error_change']))<1e-10;csvchecks+=1
    # Human-scale ledger, fixed photographic region labels (no invented identities).
    lines=['# Most serious supported visible-geometry discrepancies','','Fractions are visible-owner coverage of frozen pigment cores; none is a complete outline.','', '| Photo core | Color | Baseline modal coverage | Final modal coverage | Final boundary-crossing fraction of eroded core | Final largest owners |','|---|---|---:|---:|---:|---|']
    before={r['id']:r for r in b['geometry']['cores']}
    for r in sorted(best['geometry']['cores'],key=lambda r:r['modal_fraction'])[:8]:
        owners=', '.join(f"{z['index']}: {100*z['fraction']:.1f}%" for z in r['owners'][:3]);lines.append(f"| {r['id']} | {r['color']} | {100*before[r['id']]['modal_fraction']:.1f}% | {100*r['modal_fraction']:.1f}% | {100*r['crossing_fraction']:.1f}% | {owners} |")
    lines+=['','The25% supported color-seam conflict fraction and7.2px exterior-bracket p95 remain unacceptable for an excellent reconstruction. No cross-color dual-core claim passes the conservative substantiality threshold in the baseline/final models. Same-color ambiguous separators remain unresolved; a zero dual count does not certify them.'];(OUT/'geometry-ledger.md').write_text('\n'.join(lines)+'\n')
    save(OUT/'artifact-validation.json',dict(passed=True,utc=utc(),body_outline_records=count,csv_response_checks=csvchecks,raw_rgb_exact=True,static_links=len(links),unresolved_isolated_visible_differences=differences))
    print('ARTIFACTS',count,csvchecks,'unresolved isolated',len(differences),flush=True)
if __name__=='__main__':main()
