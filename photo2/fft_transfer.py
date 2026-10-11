"""R249: development-only freeze followed by unchanged six-site transfer."""
import argparse,itertools,json,datetime
import numpy as np
from photo2.fft_spectrum_led import (ROOT,read,save,sha,image_rgb,products,extract,
    reciprocal_alternatives,wrap)

BUNDLE=ROOT/'photo2/review/r249'
SOURCE=ROOT/'photo2/review/r248/sampling.json'
VARIANTS=[dict(name='primary',sigma=30,central=2.),dict(name='width20',sigma=20,central=2.),
          dict(name='width40',sigma=40,central=2.),dict(name='central15',sigma=30,central=1.5),
          dict(name='central25',sigma=30,central=2.5)]
RULES=dict(shortlist=4,alternatives=8,min_angle_separation=25.,weak_peak_ratio=.10,
           closure_resolution_multiplier=float(np.sqrt(3)),match_resolution_limit=2.,
           stability_required=3,stability_total=4,
           uncertainty='Window blur scales, not statistical confidence intervals; camera/tangent/assignment uncertainty additional.')


def vector(p):
    t=np.radians(p['relative_angle']);return p['frequency']*np.array([np.cos(t),np.sin(t)])


def match_triplets(left,right):
    """All axial one-to-one matches within two combined resolution scales."""
    if len(left)!=3 or len(right)!=3:return []
    matches=[]
    for perm in itertools.permutations(right):
        ds=[min(np.linalg.norm(vector(a)-vector(b)),np.linalg.norm(vector(a)+vector(b)))/np.hypot(a['frequency_resolution'],b['frequency_resolution']) for a,b in zip(left,perm)]
        if max(ds)<=RULES['match_resolution_limit']:
            matches.append(dict(right_candidates=[p['candidate'] for p in perm],distances=ds,rms=float(np.sqrt(np.mean(np.square(ds))))))
    return sorted(matches,key=lambda q:q['rms'])


def qualify(r):
    """Retain every signed-closure-compatible trio within brightest four.

    Do not manufacture a trio or replace a weak/clipped member from ranks5–8.
    Multiple bases of the same three pairs are not independent solutions.
    """
    alts=reciprocal_alternatives(r['peaks'][:4],r['n'],r['frequency_resolution'],r['tangent_deg'])
    triples={tuple(sorted(a['basis_candidates']+[a['third_candidate']])) for a in alts};out=[]
    for ids in sorted(triples):
        ps=[r['peaks'][i-1] for i in ids]
        sep=min(abs(float(wrap(a['relative_angle']-b['relative_angle']))) for a,b in itertools.combinations(ps,2))
        reasons=[]
        if sep<RULES['min_angle_separation']:reasons.append('directions too close')
        if any(p['boundary_clipped'] for p in ps):reasons.append('central-cut lobe overlap')
        if any(p['weak'] for p in ps):reasons.append('weak member')
        out.append(dict(candidates=list(ids),supported=not reasons,limitations=reasons,min_separation=sep,
                        best_closure=min(a['resolution_ratio'] for a in alts if tuple(sorted(a['basis_candidates']+[a['third_candidate']]))==ids)))
    return out,alts


def measure(rgb,q,ch,v):
    sigma=v['sigma'];delta=1/(2*np.pi*sigma);low=v['central']*delta
    base=dict(window=q['id'],source_site=q['source_site'],channel=ch,variant=v['name'],sigma=sigma,central=v['central'],s=q['s'],xy=q['xy'],tangent_deg=q['tangent_deg'])
    try:a=products(rgb,q,sigma,ch)
    except ValueError as e:return dict(base,failure=str(e),peaks=[],trios=[])
    r=extract(a,low,np.sqrt(.5),q['tangent_deg']);c=a['n']//2
    for p in r['peaks']:
        dx,dy=p['offset'];p['peak_bin_power']=float(abs(a['f'][c-dy,c+dx])**2)
    r['peaks'].sort(key=lambda p:p['peak_bin_power'],reverse=True)
    strongest=r['peaks'][0]['peak_bin_power'] if r['peaks'] else 1.
    for i,p in enumerate(r['peaks']):
        p.update(candidate=i+1,relative_brightness=p['peak_bin_power']/strongest,weak=p['peak_bin_power']/strongest<RULES['weak_peak_ratio'],shortlisted=i<4,physical_assignment='unassigned')
    result=dict(base,n=a['n'],**r);result['trios'],result['reciprocal_alternatives']=qualify(result)
    return result


def develop():
    BUNDLE.mkdir(parents=True,exist_ok=True)
    if (BUNDLE/'freeze.json').exists():raise RuntimeError('Already frozen; development cannot be overwritten')
    cfg=read(SOURCE);rgb=image_rgb(ROOT/cfg['image']);assert sha(ROOT/cfg['image'])==cfg['image_sha256']
    records=[measure(rgb,q,ch,v) for q in cfg['development'] for v in VARIANTS for ch in ('V','Y')]
    save(BUNDLE/'development.json',records)
    for r in records:
        if r['variant']=='primary':print(r['window'],r['channel'],[(t['candidates'],t['limitations']) for t in r['trios']],flush=True)


def freeze():
    if (BUNDLE/'freeze.json').exists():raise RuntimeError('Refuse to replace frozen procedure')
    cfg=read(SOURCE);dev=read(BUNDLE/'development.json');assert {r['window'] for r in dev}=={'D1','D2','D3'}
    refs=[]
    for r in dev:
        if r['variant']!='primary':continue
        for t in r['trios']:
            if t['supported']:refs.append(dict(window=r['window'],channel=r['channel'],candidates=t['candidates'],peaks=[r['peaks'][i-1] for i in t['candidates']]))
    files=[__file__,ROOT/'photo2/fft_spectrum_led.py',ROOT/'photo2/fft_explorer_core.py',ROOT/'photo2/fft_helicity.py',SOURCE,BUNDLE/'development.json']
    save(BUNDLE/'freeze.json',dict(request='R249',status='PROVISIONAL, frozen before six-site extraction; no maker confirmation of numeric choices',
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_commit='175b190059a63915e212a43d7b020348fb9bbe43',
        variants=VARIANTS,rules=RULES,image=cfg['image'],image_sha256=cfg['image_sha256'],sites=cfg['transfer'],references=refs,
        parameters='Circular native Gaussian support5sigma; V/Y matched; no mean removal, normalization, upper rejection or local retuning. Lower=central/(2*pi*sigma).',
        width_reason='Sigma30 balances the broad merged sigma20 features and added sigma40/55 substructure in D1–D3. Sigma20/40 are checks, never replacement winners.',
        central_reason='Two Gaussian Fourier amplitude-width scales remove DC core conservatively, near development .010–.015 at sigma30. Keep bright side lobes; residual central skirts remain possible. No new automatic central-component segmentation.',
        decision='Spectral support needs a distinct, nonweak, unclipped closure-compatible trio in brightest4. Retain all competing trios and ranks5–8, but do not rescue shortlist failures. Similarity to primary development trios is a separate descriptive test, never an extraction filter.',
        stability='For each primary supported trio require matching supported trios in at least3/4 fixed sensitivity settings for stable spectral support. Channels remain separate. Many-to-many matches retained.',
        visual='After extraction, inspect raw/weighted crops and every shortlisted pair inverse; state reflection/color/outline confounds separately. Numerical closure alone never establishes physical1/6/7.',
        limitation='Prior photograph and sites studied historically. Reserved for this frozen procedure, not untouched blind data. Tangent correction removes image roll, not camera projection.',
        source_hashes={str(__import__('pathlib').Path(p).relative_to(ROOT)):sha(p) for p in files}))
    print('Frozen',sha(BUNDLE/'freeze.json'),'development reference trios',len(refs),flush=True)


def verify_freeze():
    cfg=read(BUNDLE/'freeze.json');assert cfg['variants']==VARIANTS and cfg['rules']==RULES
    for p,h in cfg['source_hashes'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/cfg['image'])==cfg['image_sha256'];return cfg


def evaluate():
    cfg=verify_freeze();rgb=image_rgb(ROOT/cfg['image']);records=[]
    # Freeze and all its extraction-source hashes checked BEFORE any transfer crop.
    for q in cfg['sites']:
        for v in cfg['variants']:
            for ch in ('V','Y'):records.append(measure(rgb,q,ch,v))
        print('Measured',q['id'],flush=True)
    save(BUNDLE/'transfer.json',dict(freeze_sha256=sha(BUNDLE/'freeze.json'),records=records))
    summaries=[]
    for r in records:
        if r['variant']!='primary':continue
        cases=[]
        for t in r['trios']:
            if not t['supported']:continue
            ps=[r['peaks'][i-1] for i in t['candidates']];refs=[];sensitivity=[]
            for ref in cfg['references']:
                m=match_triplets(ps,ref['peaks'])
                if m:refs.append(dict(window=ref['window'],channel=ref['channel'],matches=m))
            for v in cfg['variants'][1:]:
                rr=next(x for x in records if (x['window'],x['channel'],x['variant'])==(r['window'],r['channel'],v['name']));matches=[]
                for tt in rr['trios']:
                    if tt['supported']:
                        m=match_triplets(ps,[rr['peaks'][i-1] for i in tt['candidates']])
                        if m:matches.append(dict(candidates=tt['candidates'],matches=m))
                sensitivity.append(dict(variant=v['name'],matches=matches))
            count=sum(bool(x['matches']) for x in sensitivity)
            cases.append(dict(candidates=t['candidates'],development_matches=refs,sensitivity=sensitivity,stable_count=count,stable=count>=RULES['stability_required']))
        summaries.append(dict(window=r['window'],channel=r['channel'],trios=cases,
            status='stable spectral trio' if any(t['stable'] for t in cases) else 'fragile spectral trio' if cases else 'no supported primary trio',
            development_match=any(t['development_matches'] for t in cases)))
    save(BUNDLE/'assessment.json',summaries)
    print([(r['window'],r['channel'],r['status'],r['development_match']) for r in summaries])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['develop','freeze','evaluate']);args=p.parse_args();globals()[args.stage]()
