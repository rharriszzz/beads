"""Read-only reuse of measured coordinates, supports, and uncertainty."""
import numpy as np
from photo2.r297.common import ROOT, read, save, sha, load_evidence
from photo2.r297.geometry import reference
from photo2.r298.calibrate import measurements

SOURCES = ['beads-photo-2.jpg', 'photo2/r282/results/centerline.json',
 'photo2/r296/evidence/inputs.json.gz', 'photo2/r296/evidence/cues.npz',
 'photo2/r298/evidence/measurements.json', 'photo2/r298/evidence/visual-screen.json',
 'photo2/r298/evidence/separators.json', 'photo2/r299/evidence/measurements.json.gz',
 'photo2/r299/evidence/visual-screen.json', 'photo2/r305/evidence/observations.json',
 'photo2/r305/results/starting-red-diagnosis.json', 'photo2/r305/results/B15-contour-diagnosis.json']

def load():
    data, frozen = load_evidence(); ref = reference()
    old = read(ROOT/'photo2/r299/evidence/measurements.json.gz')
    ambiguous = read(ROOT/'photo2/r299/evidence/visual-screen.json')['ambiguous']
    rows = []
    for r in old['observations']:
        point = r.get('centroid') or r['historical_peak']; pr = ref.project([point])
        arc = float(pr['arc'][0]); section = int(((arc-data['arc0'])*data['direction'])%ref.length/ref.length*32)%32
        rows.append(dict(id=r['id'], point=point, strong=bool(r['eligible'] and r['id'] not in ambiguous),
                         color=r['color'], uncertainty_px=r.get('uncertainty_px', 3.), arc=arc, section=section,
                         split='comparison' if section%4==3 else 'development', source=r['source'],
                         optical_status=r.get('specular_status'), selected_R299=r['selected'], aliases=[]))
    # Keep R257-only evidence and all aliases without double-counting nearby peaks.
    for r in old['historical_r257']:
        d=np.linalg.norm(np.array([o['point'] for o in rows])-r['xy'],axis=1); j=int(d.argmin())
        if d[j]<4:
            rows[j]['aliases'].append(dict(id=r['id'],point=r['xy'],source='R257',distance_px=float(d[j])))
        else:
            a=float(ref.project([r['xy']])['arc'][0]); section=int(((a-data['arc0'])*data['direction'])%ref.length/ref.length*32)%32
            rows.append(dict(id=r['id'],point=r['xy'],strong=False,color='black',uncertainty_px=r.get('uncertainty_px',4.),
                             arc=a,section=section,split='comparison' if section%4==3 else 'development',source='R257',
                             optical_status='historical uncertain candidate',selected_R299=False,aliases=[]))
    rows.sort(key=lambda r:(r['arc'],r['id']))
    return data, measurements(), rows

def freeze(out):
    data, m, obs = load()
    doc=dict(sources={p:sha(ROOT/p) for p in SOURCES}, observations=obs,
             policy='Original coordinates and uncertainty. No Phase 1 rerun. Strong localized reflections enter fitting; weak/diffuse observations stay in exports. Region/patch, contour, material and reflection blocks are dependent and not independent pixels.',
             held_out='Material/reflections: original-reference geographic sections 3 modulo 4; contours/envelopes: frozen R298 comparison partition. All are retrospective. No comparison outcome enters search or final ranking.')
    save(out/'evidence.json.gz',doc)
    return data,m,obs,doc['sources']
