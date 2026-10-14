"""Support-based two-sided accounting. Curve proximity never certifies a bead."""
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from .common import OUT,OLD,ROOT,read,save,sha,pixels


def relationships(rows,curve):
    curve=np.asarray(curve,float)
    if np.linalg.norm(curve[0]-curve[-1])<1e-6:curve=curve[:-1]
    delta=np.roll(curve,-1,axis=0)-curve
    segment=np.linalg.norm(delta,axis=1);arc=np.r_[0,np.cumsum(segment)];length=arc[-1]
    tangent=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0)
    tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9);normal=np.c_[-tangent[:,1],tangent[:,0]]
    tree=cKDTree(curve)
    centers=np.array([r['measured_photo_location'] or r['seed'] for r in rows]);ct=cKDTree(centers)
    sizes=np.array([2*np.sqrt(len(pixels(r['measured_support']))/np.pi) for r in rows])
    for i,r in enumerate(rows):
        p=pixels(r['measured_support']);_,j=tree.query(centers[i]);near=ct.query_ball_point(centers[i],100)
        pool=[sizes[k] for k in near if rows[k]['status']=='high' and sizes[k]>=8]
        scale=float(np.median(pool)) if pool else float(np.median(sizes[sizes>=8]))
        origin_s=arc[j]
        if len(p):
            dist,ix=tree.query(p);signed=np.sum((p-curve[ix])*normal[ix],axis=1)
            # Unwrap each support locally at the closed-curve seam.
            ss=(arc[ix]-origin_s+length/2)%length-length/2
            bounds=[float(signed.min()),float(signed.max())]
            crosses=bool(bounds[0]<=0<=bounds[1] and dist.min()<=1.)
            side='crossing' if crosses else 'changes-side' if bounds[0]<0<bounds[1] else 'positive' if np.median(signed)>=0 else 'negative'
            near_support=bool(dist.min()<=.5*scale)
            rel=dict(signed_extent=bounds,signed_median=float(np.median(signed)),unsigned_support_distance=float(dist.min()),
                arc_interval_relative=[float(ss.min()),float(ss.max())],crosses=crosses,side=side,near=near_support)
        else:rel=dict(signed_extent=None,signed_median=None,unsigned_support_distance=None,arc_interval_relative=None,crosses=False,side='no-support',near=False)
        rel.update(arc_px=float(origin_s),local_support_scale=scale,station=int(j),
            centroid26_diagnostic=bool(np.linalg.norm(centers[i]-curve[j])<=26),
            nearness_rule='minimum native support distance <= half local median equivalent interior diameter; crossing separately recorded',
            scale_limitation='Observed interior scale underestimates full bead extent; not calibrated physical diameter.')
        r['centerline']=rel;r['near_centerline']=rel['near']
    return curve,arc[:-1],length,normal


def main():
    p1=read(OUT/'phase1-owned.json.gz');rows=p1['records'];curve,arc,length,normal=relationships(rows,read(OLD/'centerline.json')['points'])
    pairs=read(OUT/'ownership.json')['pairs'];ambiguous={frozenset(p['ids']) for p in pairs if p['relation']!='separated-features'}
    flank=[]
    high=[r for r in rows if r['status']=='high' and r['centerline']['near']]
    for i,a in enumerate(high):
        ac=a['centerline']
        for b in high[i+1:]:
            bc=b['centerline'];d=abs((ac['arc_px']-bc['arc_px']+length/2)%length-length/2)
            if {ac['side'],bc['side']}!={'positive','negative'} or d>.65*min(ac['local_support_scale'],bc['local_support_scale']):continue
            if frozenset((a['record_id'],b['record_id'])) in ambiguous:continue
            flank.append(dict(ids=[a['record_id'],b['record_id']],arc_separation=d,
                interpretation='two disjoint photographic interiors on opposite sides; physical distinctness remains uncalibrated'))
    old_gaps=read(ROOT/'photo2/review/r282/phase1-gaps.json');gaps=[]
    for old in old_gaps:
        center=np.array(old['center']);j=int(np.argmin(np.linalg.norm(curve-center,axis=1)));near=[]
        for r in rows:
            c=r['centerline'];p=pixels(r['measured_support'])
            if not len(p):continue
            along=np.abs((c['arc_px']-arc[j]+length/2)%length-length/2)
            distance=float(np.linalg.norm(p-center,axis=1).min())
            if along<=c['local_support_scale']*1.5 and distance<=c['local_support_scale']*1.5:
                near.append(dict(id=r['record_id'],status=r['status'],side=c['side'],support_distance=distance,
                    local_scale=c['local_support_scale'],near=c['near'],centroid26=c['centroid26_diagnostic']))
        highnear=[r for r in near if r['status']=='high' and r['support_distance']<=.5*r['local_scale']]
        flanks=[p for p in flank if set(p['ids'])<={r['id'] for r in highnear}]
        unresolved=[r for r in near if r['status']=='unresolved' and r['near']]
        causes=[]
        if flanks:causes.append('The curve passes between two separate accepted interiors; neither centroid has to sit on the curve.')
        accepted=[r for r in near if r['status']=='high']
        nearest_support=min((r['support_distance'] for r in accepted),default=None)
        if nearest_support is not None and nearest_support<=26<old['nearest_high_distance']:
            causes.append(f'The old centroid distance exaggerates distance to measured material: the nearest accepted interior is {nearest_support:.1f} pixels away. This diagnostic improvement does not prove coverage at the station.')
        if unresolved:causes.append('Nearby photographic candidates remain unresolved; their material is retained and does not establish completeness.')
        if not highnear:causes.append('There is insufficient accepted photographic evidence at this station under the support-scale rule; this is not proof of a missing bead.')
        if highnear and not flanks and old['nearest_high_distance']<=26:causes.append('This was a sector maximum, not a threshold-exceeding gap; nearby measured interiors are present.')
        if highnear and not causes:causes.append('Nearby measured interiors explain proximity, but do not establish all nearby beads have been found.')
        # Curve sensitivity is a diagnostic, never a fitted replacement curve.
        scale=float(np.median([r['local_scale'] for r in near])) if near else 20.
        sensitivity=[]
        for sign in (-1,0,1):
            shifted=center+sign*.25*scale*normal[j]
            ds=[float(np.linalg.norm(pixels(r['measured_support'])-shifted,axis=1).min()) for r in rows if r['status']=='high' and r['measured_support']]
            sensitivity.append(dict(normal_shift=sign*.25*scale,nearest_high_support_distance=min(ds)))
        gaps.append(dict(**old,nearby=near,flanking_pairs=flanks,nearest_accepted_support_distance=nearest_support,explanations=causes,curve_sensitivity=sensitivity,
            curve_problem='No independently established centerline defect. A curve between bodies is allowed; normal-shift sensitivity retained.'))
    bins=[];step=float(np.median([r['centerline']['local_support_scale'] for r in high]))
    for start in np.arange(0,length,step):
        assigned=[r for r in rows if r['centerline']['near'] and start<=r['centerline']['arc_px']<start+step]
        bins.append(dict(start_arc=float(start),end_arc=float(min(length,start+step)),
            ids=[r['record_id'] for r in assigned],counts=dict(Counter(r['status'] for r in assigned)),
            high_sides=dict(Counter(r['centerline']['side'] for r in assigned if r['status']=='high')),
            completeness='unestablished'))
    summary=dict(near=dict(Counter(r['status'] for r in rows if r['centerline']['near'])),
        high_sides=dict(Counter(r['centerline']['side'] for r in high)),flanking_pairs=len(flank),
        high_distinct_candidate_ids=len(high),count_unit='each stable observation once; ambiguous groups retained, not a certified bead census',
        bins=len(bins),bins_without_high=sum(not b['counts'].get('high') for b in bins),
        completeness=False,station_coverage_percentage=None,
        old_eight_panels='One maximum per sector, not eight established gaps or missing beads.')
    save(OUT/'coverage.json',dict(summary=summary,flanking_pairs=flank,bins=bins,gaps=gaps))
    p1['summary'].update(coverage=summary);save(OUT/'phase1.json.gz',p1)
    save(OUT/'phase1-freeze.json',dict(phase1_sha256=sha(OUT/'phase1.json.gz'),coverage_sha256=sha(OUT/'coverage.json'),
        ownership_sha256=sha(OUT/'ownership.json'),note='Frozen before local model fitting; no geometry inputs.'))
    print(summary,flush=True)

if __name__=='__main__':main()
