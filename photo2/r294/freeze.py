"""Freeze independent evidence and geographic split before geometric fitting."""
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from photo2.r293.geometry import Reference
from .common import *

def main():
    assert not (EVIDENCE/'inputs.json.gz').exists(), 'Do not replace the evidence freeze'
    paths = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    scientific = {p:sha(ROOT/p) for p in paths if p and (p.startswith('photo2/') or p=='beads-photo-2.jpg') and (ROOT/p).is_file()}
    feedback = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2').glob('r*/feedback/**/*')) if p.is_file()}
    save(EVIDENCE/'prior-science-hashes.json.gz', scientific)
    save(EVIDENCE/'live-feedback-hashes.json', feedback)
    ref=Reference(); native,_,meta=photo()
    old=read(ROOT/'photo2/r283/results/phase1.json.gz')['records']
    candidates=[]
    for r in old:
        if r['color'] not in ('red','yellow') or not r['measured_support']: continue
        q=ref.project(pixels(r['measured_support'])); p=r['measured_photo_location']
        if p[1]>360 or not (q['signed'].min()<0<q['signed'].max()): continue
        candidates.append(dict(record_id=r['record_id'],point=p,status=r['status'],
            color=r['color'],signed_extent=[float(q['signed'].min()),float(q['signed'].max())],
            area=r['measured_support']['pixel_count'],ownership_alternatives=r['ownership_alternatives']))
    candidates.sort(key=lambda c:c['point'][1])
    selected=next(c for c in candidates if c['status']=='high' and not c['ownership_alternatives'] and c['area']>=100)
    anchor=next(r for r in old if r['record_id']==selected['record_id'])
    arc0=float(ref.project([selected['point']])['arc'][0])
    # Direction follows the actual curve tangent, initially right, then down the bend.
    j=np.searchsorted(ref.arc,arc0); direction=1 if ref.delta[j,0]>0 else -1
    def along(p):
        a=ref.project([p])['arc'][0]
        return float(direction*((a-arc0+ref.length/2)%ref.length-ref.length/2))
    rows=read(ROOT/'photo2/r293/results/phase1-observations.json.gz')['records']
    selected_rows=[]
    for r in rows:
        s=along(r['representative_bright_patch_location'])
        if not (-160<=s<=1250):continue
        split='holdout' if int(np.floor((s+60)/120))%4==2 else 'train'
        fit_eligible=(-60<=s<=750 and r['centerline']['distance']<=48
            and r['native_bright_patch']['pixel_count']>=3 and r['intensity']['contrast_Y']>=.03)
        selected_rows.append(dict(source=r,along_px=s,split=split,fit_eligible=fit_eligible))
    legacy=[]
    for r in old:
        p=r['measured_photo_location']
        if not p or not r['measured_support'] or r['color']=='black':continue
        s=along(p)
        if -160<=s<=1250:legacy.append(dict(source=r,along_px=s,
            split='holdout' if int(np.floor((s+60)/120))%4==2 else 'train',
            fit_eligible=-60<=s<=750 and r['status']=='high'))
    completed=read(ROOT/'photo2/r293/evidence/completed-r293-review-analysis.json')
    reviews=[]
    for r in completed['records']:
        d=read(ROOT/r['candidate_path']);answer=r['payload']['answer']
        reviews.append(dict(case_id=r['case_id'],feature_id=r['feature_id'],answer=answer,
            source=r['candidate_path'],source_sha256=sha(ROOT/r['candidate_path']),
            along_px=along(r['feature_point']),
            accepted_candidate=d['A'] if answer=='A' else None,
            rejected_centroid_used=False))
    inputs=dict(photo=meta,source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        anchor=anchor,anchor_selection=selected,anchor_candidates=candidates,arc0=arc0,direction=direction,
        records=selected_rows,legacy_colored=legacy,completed_r293_reviews=reviews,
        sources={p:sha(ROOT/p) for p in ['photo2/r293/results/phase1-observations.json.gz',
            'photo2/r283/results/phase1.json.gz','photo2/r282/results/centerline.json',
            'photo2/r293/evidence/completed-r293-review-analysis.json']},
        fit_roi_along_px=[-60,750],geographic_holdout='120px blocks, floor((s+60)/120) mod4 ==2; all features in a block share split',
        uncertainty='Source threshold sensitivity measures patch stability only; physical center and ownership remain unknown.',
        scope='Original real photo only. No synthetic scenes, Phase1 edits, pattern inference or production adoption.')
    save(EVIDENCE/'inputs.json.gz',inputs)
    Image.fromarray(native[205:345,1400:1650]).save(EVIDENCE/'anchor-native.png')
    save(EVIDENCE/'freeze.json',dict(input_sha256=sha(EVIDENCE/'inputs.json.gz'),
        prior_science_files=len(scientific),live_feedback_files=len(feedback),
        fit_features=sum(r['fit_eligible'] for r in selected_rows),
        train=sum(r['fit_eligible'] and r['split']=='train' for r in selected_rows),
        holdout=sum(r['fit_eligible'] and r['split']=='holdout' for r in selected_rows),
        selection_uses_image_and_historical_evidence=True,heldout_is_not_a_new_blind_photo=True))
    print(read(EVIDENCE/'freeze.json'))

if __name__=='__main__':main()
