"""Photo-only symmetric ownership audit. No geometry or pattern inputs."""
from collections import Counter
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r282.phase1 import image_features, attempts
from .common import OUT, OLD, photo, read, save, sha, pixels, record

RULES = dict(overlap_fraction=.12, equivalent_fraction=.85, minimum_shared=5,
             close_scale=.8, trough_ratio=.65, black_envelope_overlap=.25, black_separation_scale=1.5,
             weight_semantics='uncalibrated engineering weights; never probabilities')


def audit(rows, features, variants=None):
    rows=deepcopy(rows); pairs=[]; clouds=[pixels(r['measured_support']) for r in rows]
    sets=[set(map(tuple,p)) for p in clouds]
    centers=np.array([r['measured_photo_location'] or r['seed'] for r in rows]);broad={}
    for i,j in sorted(cKDTree(centers).query_pairs(48)):
        a,b=rows[i],rows[j];pa,pb=clouds[i],clouds[j]
        if min(len(pa),len(pb))<12:continue
        shared=len(sets[i]&sets[j]);overlap=shared/min(len(pa),len(pb))
        # Search only original native pixels on the straight centroid segment.
        d=float(np.linalg.norm(centers[i]-centers[j]));scale=2*np.sqrt(max(len(pa),len(pb))/np.pi)
        route=np.unique(np.rint(np.linspace(centers[i],centers[j],max(2,int(d*2)))).astype(int),axis=0)
        lum=features['mean5'][route[:,1],route[:,0]]
        trough=float(lum.min()/max(1e-8,min(lum[0],lum[-1])))
        equivalent=shared>=RULES['minimum_shared'] and shared/max(len(pa),len(pb))>=RULES['equivalent_fraction']
        conflict=shared>=RULES['minimum_shared'] and overlap>=RULES['overlap_fraction']
        close=d<RULES['close_scale']*scale and a['color']==b['color']
        # Absence of a dark separator alone is not a duplicate verdict.
        relation='equivalent-measurements' if equivalent else 'shared-material-conflict' if conflict else 'possible-secondary-feature' if close and trough>RULES['trough_ratio'] else 'separated-features' if close else None
        envelope_overlap=None
        if not conflict and a['color']==b['color']=='black' and d<RULES['black_separation_scale']*scale:
            for k in (i,j):
                if k not in broad:
                    alt=attempts(features,rows[k]['seed']);broad[k]=set(map(tuple,pixels(alt[0]['region']))) if alt else set()
            envelope_overlap=len(broad[i]&broad[j])/max(1,min(len(broad[i]),len(broad[j])))
            if envelope_overlap>=RULES['black_envelope_overlap']:
                relation='shared-dark-envelope-alternative'
        if relation is None:continue
        pairs.append(dict(ids=[a['record_id'],b['record_id']],relation=relation,
            shared_pixels=shared,overlap_smaller=overlap,overlap_larger=shared/max(len(pa),len(pb)),
            centroid_distance=d,support_scale=scale,trough_ratio=trough,
            broad_dark_envelope_overlap=envelope_overlap,
            distinct_identity_established=False))
    by={r['record_id']:r for r in rows}
    for r in rows:
        r['previous_status']=r['status'];r['importance']='high'
        r['ownership_alternatives']=[];r['likely_duplicate_group']=None
        r['reliability_semantics']=RULES['weight_semantics']
        r['color_reliability_kind']='photo material evidence; distinct identity not implied'
        r['physical_identity_reliability']=0.
        if variants and r['record_id'] in variants:
            v={a['method']:a for a in variants[r['record_id']]};p=pixels(v['B']['region']);q=pixels(r['measured_support'])
            r['yellow_B_sensitivity']=dict(centroid_shift=float(np.linalg.norm(p.mean(0)-q.mean(0))) if len(p) and len(q) else None,
                area_ratio=len(p)/max(1,len(q)),support=v['B']['region'],quality=v['B']['quality']) if r['color']=='yellow' else None
    # Equivalent masks are redundant measurements, not a claim about unseen body extent.
    equivalent_edges=[p for p in pairs if p['relation']=='equivalent-measurements']
    parent={r['record_id']:r['record_id'] for r in rows}
    def root(k):
        while parent[k]!=k:k=parent[k]
        return k
    for p in equivalent_edges:
        a,b=map(root,p['ids']);parent[max(a,b)]=min(a,b)
    groups={}
    for k in parent:groups.setdefault(root(k),[]).append(k)
    for group in groups.values():
        if len(group)<2:continue
        representative=min(group,key=lambda k:(by[k]['previous_status']!='high',-len(pixels(by[k]['measured_support'])),k))
        for k in group:
            by[k]['likely_duplicate_group']=sorted(group)
            if k!=representative:
                by[k]['status']=by[k]['reliability_class']='unresolved'
                by[k]['notes'].append('Redundant native measurement retained; representative '+representative+' is not a verified physical identity.')
    for p in pairs:
        if p['relation']=='separated-features':continue
        for k in p['ids']:
            r=by[k];r['ownership_alternatives'].append(p)
            if p['relation']!='equivalent-measurements' and r['status'] in ('high','medium'):
                r['status']=r['reliability_class']='unresolved'
                r['notes'].append('Symmetric ownership abstention: '+p['relation']+'.')
    weights={'high':.95,'medium':.6,'unresolved':.25,'rejected':0.}
    for r in rows:
        r['phase1_reliability']=weights[r['status']]
        r['photographic_reliability']=dict(classification=r['status'],calibrated_probability=None,
            reasons=r['notes'],distinct_body='unverified; no detected conflict' if r['status']=='high' else 'unresolved')
    return rows,pairs


def detect(rgb):
    """Fresh image-only proposals for synthetic evaluation; truth never enters."""
    f=image_features(rgb);m=f['mean5'];maxima=(m==ndi.maximum_filter(m,9))&(m>.035)&~f['paper']
    labels,n=ndi.label(maxima);starts=[]
    for k in range(1,n+1):
        yy,xx=np.where(labels==k);starts.append([int(xx[0]),int(yy[0])])
    rows=[]
    for x,y in starts:
        aa=attempts(f,[x,y]);
        if not aa:continue
        a=aa[2];r=record(f'P-{x:04}-{y:04}','phase1')
        r.update(seed=[x,y],color=a['color'],measured_support=a['region'],
            measured_photo_location=(a['region'] or {}).get('centroid'),status=a['quality'],
            reliability_class=a['quality'],phase1_reliability=a['reliability'],notes=a['reasons'],metrics=a['metrics'])
        rows.append(r)
    return rows,f


def main():
    _,rgb,_=photo();f=image_features(rgb);old=read(OLD/'phase1.json.gz')
    rows,pairs=audit(old['records'],f,read(OLD/'phase1-attempts.json.gz'))
    summary=dict(before=old['summary']['counts'],after=dict(Counter(r['status'] for r in rows)),
        by_color={c:dict(Counter(r['status'] for r in rows if r['color']==c)) for c in ('red','yellow','black','unknown')},
        pairs=dict(Counter(p['relation'] for p in pairs)),retained_records=len(rows),rules=RULES,
        scope='Audit of unchanged Attempt C measured interiors; no physical identity truth for photograph.')
    save(OUT/'ownership.json',dict(pairs=pairs,summary=summary))
    save(OUT/'phase1-owned.json.gz',dict(records=rows,summary=summary))
    save(OUT/'method-freeze.json',dict(rules=RULES,synthetic_seed=283501,source_sha256=sha(__file__),
         detector_sha256=sha(OLD.parent/'phase1.py'),baseline_sha256=sha(OLD/'phase1.json.gz')))
    print(summary,flush=True)

if __name__=='__main__':main()
