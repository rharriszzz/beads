"""Freeze geography using photographic evidence only, before numerical fitting."""
import subprocess
import numpy as np
from photo2.r293.geometry import Reference
from photo2.r297.common import ROOT, read, save, sha, utc

BASE=ROOT/'photo2/r301'

def freeze():
    target=BASE/'evidence/frozen.json.gz'
    if target.exists():
        return read(target)
    ref=Reference();old=read(ROOT/'photo2/r299/evidence/measurements.json.gz')
    rows=old['observations'];xy=np.array([r.get('centroid') or r['historical_peak'] for r in rows])
    proj=ref.project(xy);arc=proj['arc'];candidates=[]
    for s in np.arange(60,ref.length-60,12):
        ix=np.flatnonzero(ref.arc_distance(arc,s)<52)
        strong=[i for i in ix if rows[i]['eligible']];black=sum(rows[i]['color']=='black' for i in strong)
        c=np.array([np.interp(s,ref.arc,ref.points[:,j]) for j in range(2)])
        t=np.array([np.interp(s+5,ref.arc,ref.points[:,j])-np.interp(s-5,ref.arc,ref.points[:,j]) for j in range(2)]);t/=np.linalg.norm(t)
        candidates.append(dict(station=float(s),center=c.tolist(),tangent=t.tolist(),ids=ix.tolist(),strong=len(strong),black=black,score=len(strong)+2*black+.15*len(ix)))
    chosen=[]
    for _ in range(3):
        eligible=[c for c in candidates if all(ref.arc_distance(c['station'],d['station'])>ref.length/6 for d in chosen)]
        c=max(eligible,key=lambda c:c['score']+sum(3*(1-abs(np.dot(c['tangent'],d['tangent']))) for d in chosen))
        chosen.append(c)
    separators=read(ROOT/'photo2/r298/evidence/separators.json')['records']
    dims=read(ROOT/'photo2/r298/evidence/measurements.json')
    raw=np.load(ROOT/'photo2/r296/evidence/cues.npz');sections=[]
    for k,c in enumerate(chosen):
        obs=[]
        for rank,i in enumerate(sorted(c['ids'],key=lambda i:arc[i])):
            r=dict(rows[i]);r.update(weight=1. if r['eligible'] else .2,split='withheld' if rank%4==1 else 'train',point=xy[i].tolist(),station=float(arc[i]))
            obs.append(r)
        center=np.array(c['center']);t=np.array(c['tangent']);n=np.array([-t[1],t[0]])
        def inside(q,pad=0):
            a=np.asarray(q)-center;return (abs(a@t)<=52+pad)&(abs(a@n)<=70+pad)
        mask=inside(raw['xy']);ix=np.flatnonzero(mask)[::3]
        cues={key:raw[key][ix].tolist() for key in ['xy','color','paper','lum']}
        seps=[r for r in separators if inside(np.array(r['xy'])[48],20)]
        profiles=[r for r in dims['envelope'] if r['eligible'] and inside(r['point'],20)]
        bead_dims=[r for r in dims['beads'] if inside(r['point'],30)]
        sections.append(dict(id=f'S{k+1}',**c,observations=obs,cues=cues,separators=seps,profiles=profiles,bead_dimensions=bead_dims))
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    protected={p:sha(ROOT/p) for p in paths if p and (p.startswith('photo2/') or p=='beads.pov' or p=='beads-photo-2.jpg')}
    for p in (ROOT/'photo2').glob('r*/feedback/**/*'):
        if p.is_file():protected[str(p.relative_to(ROOT))]=sha(p)
    save(BASE/'evidence/preservation.json.gz',protected)
    d=dict(utc=utc(),photo_sha256=sha(ROOT/'beads-photo-2.jpg'),sources={p:sha(ROOT/p) for p in ['photo2/r299/evidence/measurements.json.gz','photo2/r299/evidence/visual-screen.json','photo2/r298/evidence/measurements.json','photo2/r298/evidence/separators.json','photo2/r296/evidence/cues.npz']},sections=sections,all_original_observations=rows,historical_r257=old['historical_r257'],selection_candidates=candidates,protocol='104px photographic arc windows, approximately 26 positions at historical 4px spacing (not inferred count); 25 core + 16 guards per side initially. Rank eligible specularity and black evidence, enforce >1/6 circuit separation, reward different tangent. All local observations retained, weak .2 weight; every fourth station-ordered observation withheld. No physical owners or fit residuals used. Earlier evidence is retrospective. Core/guard predictions may exchange geographic roles; all predictions in frozen image window scored.')
    save(target,d);return d

if __name__=='__main__':
    d=freeze()
    for s in d['sections']:print(s['id'],s['center'],len(s['observations']),s['strong'],s['black'])
