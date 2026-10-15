"""Offline, native-pixel failure atlas. Measurements and predictions stay separate."""
import csv
import json
import shutil
import numpy as np
from scipy.spatial import cKDTree
from .common import *
from .geometry import Chain,FIELD_SIZE,reference


def section(station,length):return int(station/length*FIELD_SIZE)%FIELD_SIZE


def photo_disagreements(scene,data,splits):
    raw=np.load(EVIDENCE/'cues.npz');keep=np.isin(raw['split'],splits)
    xy=raw['xy'];owner=scene.trace(xy[keep])['owner']
    owners=np.full(len(xy),-2,int);owners[keep]=owner
    sections=(raw['station']/data['length']*FIELD_SIZE).astype(int)%FIELD_SIZE
    a,b=raw['pairs'].T;valid=keep[a]&keep[b];a=a[valid];b=b[valid]
    edges=raw['edge'][valid];lum=raw['mid_lum'][valid]
    boundary=(owners[a]!=owners[b])&((owners[a]>=0)|(owners[b]>=0))
    continuous=(raw['color'][a]>0)&(raw['color'][a]==raw['color'][b])&(lum>.065)&(edges<.6)
    paper=keep&(owners>=0)&raw['paper'];colored=keep&(raw['color']>0)
    counts=np.zeros((scene.n,3));vis=keep&(owners>=0);np.add.at(counts,(owners[vis],raw['color'][vis]),1)
    mixed=(counts[:,1]>=3)&(counts[:,2]>=3)
    conflict=vis.copy();conflict[vis]=mixed[owners[vis]]&(raw['color'][vis]>0)
    events=[]
    for kind,ids in [('paper-occupation',np.flatnonzero(paper)),('red-yellow-conflict',np.flatnonzero(conflict)),('uncovered-colored-material',np.flatnonzero(colored&(owners<0)))]:
        for i in ids:events.append(dict(mechanism=kind,point=xy[i].tolist(),section=int(sections[i]),model_index=int(scene.indices[owners[i]]) if owners[i]>=0 else None,
            measured=dict(color=int(raw['color'][i]),paper_proxy=bool(raw['paper'][i]),luminance=float(raw['lum'][i])),uncertainty='Photometric proxy; no physical identity or empty-space truth'))
    for j in np.flatnonzero(boundary&continuous):
        events.append(dict(mechanism='coherent-material-cut',point=((xy[a[j]]+xy[b[j]])/2).tolist(),section=int(sections[a[j]]),
            measured=dict(endpoints=[xy[a[j]].tolist(),xy[b[j]].tolist()],edge=float(edges[j]),mid_luminance=float(lum[j]),color=int(raw['color'][a[j]])),
            predicted_indices=[int(scene.indices[owners[i]]) if owners[i]>=0 else None for i in [a[j],b[j]]],uncertainty='Color/brightness continuity can cross a real boundary; inspect original pixels'))
    summary=[]
    for j in range(FIELD_SIZE):
        mask=keep&(sections==j);v=mask&(owners>=0);c=colored&(sections==j);pairs=sections[a]==j
        summary.append(dict(section=j,photo_samples=int(mask.sum()),paper_samples=int((paper&mask).sum()),predicted_visible_samples=int(v.sum()),
            colored_samples=int(c.sum()),uncovered_colored_samples=int((c&(owners<0)).sum()),conflicting_color_samples=int((conflict&mask).sum()),
            continuous_pairs=int((continuous&pairs).sum()),cut_pairs=int((boundary&continuous&pairs).sum())))
    return dict(events=events,sections=summary)


def build(out,data,evaluations,positions):
    out=Path(out);review=out/'review';export=out/'exports';best=evaluations[0]
    oldroot=ROOT/'photo2/r296/results/pilot'
    old=read(oldroot/'exports/evaluation-188.json.gz');oldmap={r['id']:r for r in old['observations']}
    prior=read(ROOT/'photo2/r295/results/R295-evaluation.json');priormap={r['id']:r for r in prior['observations']}
    measurements={r['id']:r for r in data['rows']}
    models=[dict(id=str(e['id']),image=f'model-{e["id"]}.png',parameters=e['parameters'],closure=e['closure'],visibility=e['visibility'],
        minimum_contact_margin=e['contact']['minimum_gap_units']) for e in evaluations]
    shutil.copyfile(oldroot/'review/model-188.png',review/'r296.png')
    shutil.copyfile(ROOT/'photo2/review/r295/R295-whole.png',review/'r295.png')
    models.extend([dict(id='R296',image='r296.png',parameters=old['parameters'],closure=old['closure'],visibility=old['visibility'],minimum_contact_margin=old['contact']['minimum_gap_units']),
                   dict(id='R295 local',image='r295.png',parameters=prior['parameters'])])
    records=[];sections=[];per_model=[];circuits={}
    for e,pos in zip(evaluations,positions):
        scene=Chain(e['parameters'],data);splits=list(e['summary']);photo=photo_disagreements(scene,data,splits)
        save(export/f'disagreements-{e["id"]}.json.gz',photo)
        by={r['index']:r for r in pos};obsmap={r['id']:r for r in e['observations']}
        stations=(data['direction']*(reference().project(scene.project(scene.line))['arc']-data['arc0']))%data['length']
        site_sections=(stations/data['length']*FIELD_SIZE).astype(int)%FIELD_SIZE
        circuit=circuit_summary(scene,e,data,splits);circuits[str(e['id'])]=circuit
        save(export/f'circuit-{e["id"]}.json',circuit)
        for j in range(FIELD_SIZE):
            obs=[r for r in e['observations'] if section(measurements[r['id']]['station'],data['length'])==j and r['kind']=='region']
            common=[r for r in obs if r['id'] in oldmap]
            sites=[r for r,k in zip(pos,site_sections) if k==j]
            per_model.append(dict(model=e['id'],section=j,modeled_sites=len(sites),supported_sites=sum(r['compatible_support'] for r in sites),low_visibility_sites=sum(r['visible_fraction']<.1 for r in sites),n=len(obs),mean=float(np.mean([r['containment'] for r in obs])) if obs else None,
                compatible=sum(r['compatible'] for r in obs),r296_common_n=len(common),
                r296_common_delta=float(np.mean([r['containment']-oldmap[r['id']]['containment'] for r in common])) if common else None,**{k:v for k,v in photo['sections'][j].items() if k!='section'}))
        if e is not best:continue
        eventtree=cKDTree([v['point'] for v in photo['events']]) if photo['events'] else None
        for r in e['observations']:
            source=measurements[r['id']];previous=oldmap.get(r['id']);local=priormap.get(r['id']);flags=[]
            if r['containment']<.5:flags.append('poor-material-fit')
            if not r['compatible']:flags.append('uncertain-correspondence')
            if r['unmatched_fraction']>.2:flags.append('uncovered-support')
            if len(r['alternatives'])>1 and r['alternatives'][1]['fraction']>.2:flags.append('split-visible-material')
            isolated=r.get('isolated_candidates',[])
            occluded=[a for a in isolated if a['fraction']>.5 and a['fraction']-a['visible_fraction']>.25]
            if occluded:flags.append('occlusion-competition')
            if previous and r['containment']-previous['containment']<-.1:flags.append('R296-regression')
            if local and r['containment']-local['containment']<-.1:flags.append('R295-regression')
            family=[]
            for other in evaluations:
                q=next((q for q in other['observations'] if q['id']==r['id']),None)
                if q:family.append(dict(model=other['id'],index=q['index'],containment=q['containment'],alternatives=q['alternatives']))
            if family and np.ptp([a['containment'] for a in family])>.2:flags.append('family-disagreement')
            near_events=[photo['events'][i] for i in eventtree.query_ball_point(r['point'],25)] if eventtree else []
            flags.extend(sorted({v['mechanism'] for v in near_events}))
            linked=by.get(r['index']);nearest=scene.tree.query(source['point'],k=4)[1]
            if linked and r['index']!=int(scene.indices[nearest[0]]):flags.append('nonnearest-surface-assignment')
            records.append(dict(id=r['id'],kind=r['kind'],point=r['point'],section=section(source['station'],data['length']),mechanisms=flags,
                measurement=dict(color=source['color'],reflection=source['reflection'],support=source['pixels'],provenance=source['provenance'],trust=source['trust'],split=r['split']),
                prediction=dict(index=r['index'],containment=r['containment'],compatible=r['compatible'],alternatives=r['alternatives'],
                    isolated_candidates=isolated,visibility=r.get('modeled_visibility'),nearest_projected_centers=[int(scene.indices[i]) for i in nearest],
                    unknown_pixels=r['unknown_pixels'],physical_identity_verified=False),
                nearby_photographic_diagnostics=near_events,comparisons=dict(r296=previous,r295=local,families=family),
                uncertainty='Automatic support may be incomplete/merged. Nonnearest ownership can be correct under occlusion. No independent owner or occlusion truth.'))
        # Use geography rather than same-number indices to compare different counts.
        regionorder=sorted([r for r in e['observations'] if r['kind']=='region' and r['index'] is not None],key=lambda r:measurements[r['id']]['station'])
        changes=[]
        for a,b in zip(regionorder,regionorder[1:]+regionorder[:1]):
            ka,kb=a['index'],b['index'];delta=(kb-ka+scene.n/2)%scene.n-scene.n/2
            gap=(measurements[b['id']]['station']-measurements[a['id']]['station'])%data['length']
            if gap<100 and (delta< -7 or delta>gap/data['length']*scene.n+12):
                changes.append(dict(ids=[a['id'],b['id']],points=[a['point'],b['point']],station_gap=gap,index_step=float(delta),
                    mechanism='possible-index-discontinuity',uncertainty='Nearby different helix surfaces need not be successive beads; diagnostic only'))
        save(export/'index-continuity.json',dict(pairs=changes,closure=scene.closure()))
        witnesses=sorted(e['contact']['witnesses'],key=lambda r:r['gap_units'])
        near=[]
        for w in witnesses[:100]:
            a,b=w['pair'];near.append(dict(indices=[int(scene.indices[a]),int(scene.indices[b])],gap_units=w['gap_units'],point=((scene.pc[a]+scene.pc[b])/2).tolist(),normal=w['normal']))
        save(export/'near-contacts.json',dict(witnesses=near,limits='Positive separating-plane lower bound, not the exact closest surface distance. Nonpositive certificate is inconclusive until volume witness.'))
        eps=.01;k=np.array([scene.start-eps,scene.start+eps,scene.start+scene.n-eps,scene.start+scene.n+eps])
        line,g,phase=scene.placement(k)
        seam=dict(scene.closure(),endpoints_photo=scene.pc[[0,-1]].tolist(),
            station_steps=np.diff(scene.station_px).tolist(),phase_steps=np.diff(scene.phase).tolist(),
            seam_spacing_derivative_difference=float(abs(np.linalg.norm(line[1]-line[0])-np.linalg.norm(line[3]-line[2]))/(2*eps)),
            physical_cross_seam_pairs=[dict(indices=[int(scene.indices[a]) for a in w['pair']],gap_units=w['gap_units']) for w in e['contact']['witnesses'] if abs(w['pair'][1]-w['pair'][0])>scene.n/2],
            gap_policy='Open chains have no last-to-first adjacency; nonintersection is still checked across all spatially near endpoints.',
            evidence='Endpoint and phase closure are conditional geometry. Image-reference periodicity is not evidence of a physical join.')
        save(export/'circuit.json',seam)
    for j in range(FIELD_SIZE):
        group=[r for r in records if r['section']==j and r['kind']=='region']
        row=next(r for r in per_model if r['model']==best['id'] and r['section']==j)
        center=np.mean([r['point'] for r in group],axis=0).tolist() if group else [0,0]
        sections.append(dict(**row,point=center,worst=[r['id'] for r in sorted(group,key=lambda r:r['prediction']['containment'])[:5]],
            label=f'Section {j:02d}: stations {j*data["length"]/32:.0f}–{(j+1)*data["length"]/32:.0f}px'))
    with (export/'regions.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(per_model[0]));writer.writeheader();writer.writerows(per_model)
    save(export/'sections.json',per_model)
    atlas=dict(models=models,sections=sections,records=records,near_contacts=near,index_discontinuities=changes,circuit=seam,
        circuits=circuits,photo=data['photo'],limits='All R296 reserved outcomes retrospective; validation selects models. Containment is not physical ownership. No new independent evidence.')
    save(export/'failure-atlas.json.gz',atlas)
    payload=json.dumps(atlas,separators=(',',':')).replace('</','<\\/')
    template=(BASE/'debugger.html').read_text()
    (review/'debug.html').write_text(template.replace('__DATA__',payload))
    path=review/'index.html';text=path.read_text();text=text.replace('<h1>', '<p><a href="debug.html">Open clickable full-circuit debugger: all sections, raw pixels, R295/R296, alternatives and failures</a></p><h1>',1);path.write_text(text)
    print('Offline failure atlas:',len(records),'observations;',len(sections),'sections',flush=True)


def circuit_summary(scene,e,data,splits):
    """Continuity is model mathematics; gap evidence is kept explicitly separate."""
    n=scene.n;eps=.001;boundaries=np.linspace(scene.start,scene.start+n,33)
    probes=[]
    for k in boundaries:
        line,g,phase=scene.placement(np.array([k-eps,k,k+eps]))
        probes.append(dict(index=float(k),axis_left_step=float(np.linalg.norm(line[1]-line[0])/eps),axis_right_step=float(np.linalg.norm(line[2]-line[1])/eps),phase_left_step=float((phase[1]-phase[0])/eps),phase_right_step=float((phase[2]-phase[1])/eps)))
    line,g,phase=scene.placement(np.array([scene.start,scene.start+n]));axis=scene.project(line)
    raw=np.load(EVIDENCE/'cues.npz');mid=axis.mean(0)
    nearby=np.isin(raw['split'],splits)&(np.linalg.norm(raw['xy']-mid,axis=1)<35)
    xy=raw['xy'][nearby];owner=scene.trace(xy)['owner'];color=raw['color'][nearby];paper=raw['paper'][nearby]
    witnesses=[w for w in e['contact']['witnesses'] if abs(w['pair'][1]-w['pair'][0])>n/2]
    return dict(scene.closure(),seam_fraction=scene.p.get('seam_fraction',-.5),endpoints_photo=scene.pc[[0,-1]].tolist(),axis_endpoints_photo=axis.tolist(),
        minimum_station_increment=float(np.min(np.diff(scene.station_px))),maximum_station_increment=float(np.max(np.diff(scene.station_px))),
        index_count=len(set(scene.indices.tolist())),section_boundary_probes=probes,
        cross_cut_contacts=[dict(indices=[int(scene.indices[j]) for j in w['pair']],gap_units=w['gap_units']) for w in witnesses],
        measured_seam_neighborhood=dict(radius_px=35,samples=len(xy),colored=int((color>0).sum()),paper_proxy=int(paper.sum()),
            colored_without_predicted_material=int(((color>0)&(owner<0)).sum()),predicted_material_on_paper=int((paper&(owner>=0)).sum())),
        physical_gap='Open endpoints have no connecting edge; their annular surfaces and all other neighbors are separately nonintersection-tested.' if not scene.closed else 'Periodic phase and frame; closing physical packing checked across the cut.',
        limits='Seam neighborhood is measured photometric proxy, not proof of closure or a gap. No independent occlusion labels. Station continuity is conditional model geometry.')
