"""Independent maker mapping, mask/ownership, graph, cohort and crop checks."""
import argparse,time
from collections import Counter,defaultdict
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageOps
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(artifact('verification.json')));a=p.parse_args();start=time.perf_counter();r=artifact();old=read(ROOT/'photo2/r335/results/graph.json.gz');retained=read(r/'results/retained-graph.json.gz');g=read(r/'results/graph.json.gz');raw=read(ROOT/'photo2/r332/results/graph.json.gz');oo={x['id']:x for x in old['observations']};obs={x['id']:x for x in retained['observations']};active={x['id']:x for x in g['observations']};co={x['id']:tuple(x['ab']) for x in old['coordinates']};H=np.array(g['H']);ledger=read(r/'results/maker-decisions.json')['decisions'];panels=read(ROOT/'photo2/r335/review/panels.json.gz');cases=read(ROOT/'photo2/r335/review/ledger.json.gz')['primary'];excluded={x['id'] for x in ledger};assert len(excluded)==10
    for d in ledger:
        case=next(c for c in cases if c['id']==d['photograph']);key=next(k for k in panels[case['panel']]['key'] if k['number']==d['local_feature']);assert key['id']==d['id'];assert key['xy']==d['original_xy'];assert key['color']==d['original_color'];assert not any(d['roles'].values());assert d['id'] not in active
    assert obs['REC266-P146299']['color']=='yellow' and obs['NEW-1927-2829']['color']=='red';assert {o for o in obs if obs[o]['color']!=oo[o]['color']}=={'REC266-P146299','NEW-1927-2829'};assert all(obs[o]['xy']==oo[o]['xy'] for o in obs)
    for oid,ab in [('R332-B-0098-0092',[98,92]),('C-1979-2669',[71,66])]:
        d=next(x for x in ledger if x['id']==oid);assert d['accepted_association']['same_bead'] and d['accepted_association']['ab']==ab and d['association_identity_count']==1
    d=next(x for x in ledger if x['id']=='R332-B-0098-0092');assert d['not_alias_of']=='D40-K-1036-2780';assert 'D40-K-1036-2780' in active
    ac={x['id']:tuple(x['ab']) for x in g['coordinates']};assert len(active)==1057 and len(ac)==1039;assert len(set(rep(x) for x in ac.values()))==1039;assert all(ac[o]==co[o] for o in ac)
    oldedges={frozenset((e['source'],e['target'])):e for e in old['edges']};alledges={frozenset((e['source'],e['target'])):e for e in retained['edges']};edges={frozenset((e['source'],e['target'])):e for e in g['edges']};assert len(alledges)==2290 and len(edges)==2284;assert all(alledges[k]==v for k,v in oldedges.items());assert len(alledges.keys()-oldedges.keys())==5
    adj=defaultdict(set)
    for e in g['edges']:
        u,v=e['source'],e['target'];assert u in ac and v in ac;delta=np.array(ac[v])-ac[u]-e['delta_ab'];assert delta[0]%H[0]==0 and delta[1]==delta[0]//H[0]*H[1];adj[u].add(v);adj[v].add(u)
    seen={next(iter(ac))};todo=list(seen)
    while todo:
        for z in adj[todo.pop()]-seen:seen.add(z);todo.append(z)
    assert len(seen)==1039
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo.astype(np.float32)/255.;v=rgb.max(2);black=(v<.36)&(v-rgb.min(2)<.13)&(v>.012);investigation=read(r/'evidence/investigation.json.gz');nativechecks=0
    # Every recorded threshold pixel is re-read from native RGB. This verifies
    # location/measurement, NOT a glass ownership claim.
    source_records=raw['accepted_additions']+raw['provisional_observations']+raw['unrepresented_candidates']
    for row in source_records:
        if not row.get('native'):continue
        points=np.array(row['native']['pixels_xy']);px=rgb[points[:,1],points[:,0]];rr,gg,bb=px.T;mx=px.max(1);color=row['native']['color'];valid=(mx<.36)&(mx-px.min(1)<.13)&(mx>.012) if color=='black' else (rr>1.8*gg)&(rr>2.5*bb)&(rr>.16) if color=='red' else (gg>.35*rr)&(gg>1.8*bb)&(rr>.9*gg)&(rr>.16);assert valid.all();nativechecks+=1
    assert nativechecks==687
    for case in investigation['cases']:
        for key,query in [('initial',case['initial_prediction']),('resampled',case['recorded_support'])]:
            x,y=np.rint(query).astype(int);yy,xx=np.mgrid[y-12:y+13,x-12:x+13];domain=(xx-x)**2+(yy-y)**2<=144;mask=black[y-12:y+13,x-12:x+13]&domain;lab,n=ndi.label(mask,np.ones((3,3)));counts=np.bincount(lab.ravel());counts[0]=0;points=np.c_[xx[lab==counts.argmax()],yy[lab==counts.argmax()]];assert points.tolist()==case[key]['pixels_xy'];assert len(points)==case[key]['pixel_count'];assert not case[key]['visible_body_established'] and not case[key]['can_create_bead']
        assert np.allclose(case['initial']['centroid'],case['recorded_support'])
    assert [(c['initial']['pixel_count'],c['resampled']['pixel_count']) for c in investigation['cases']]==[(32,208),(143,246)]
    lighting=read(r/'results/lighting-observations.json');x0,y0,x1,y1=lighting['bbox'];assert np.array_equal(lighting['native_RGB'],photo[y0:y1,x0:x1]);assert lighting['id']=='E5-1499-3037' and not lighting['bead_identity'] and lighting['bead_center'] is None
    r334={x['id']:x for x in read(ROOT/'photo2/r334/classification/audit.json.gz')['records']};r335={x['id']:x for x in read(ROOT/'photo2/r335/results/application.json.gz')['records']}
    for item in read(r/'review/evidence-pixels.json.gz'):
        oid=item['id'];source=next(x for x in investigation['cases'] if x['id']==oid);assert item['layers'][0]['pixels_xy']==source['initial']['pixels_xy'];assert item['layers'][1]['pixels_xy']==source['resampled']['pixels_xy'];assert item['layers'][2]['pixels_xy']==r334[oid]['samples'][1]['black_test']['ring_pixels'];assert item['layers'][3]['pixels_xy']==r335[oid]['scales'][1]['ring_pixels']
        for layer,stat in [(item['layers'][2],r334[oid]['samples'][1]['black_test']),(item['layers'][3],r335[oid]['scales'][1])]:
            pts=np.array(layer['pixels_xy']);px=photo[pts[:,1],pts[:,0]].astype(float)/255;median=float(np.median(px@np.array([.299,.587,.114])));assert abs(median-stat['median_intensity'])<1e-14
    # Adversarial regression: even a large, perfectly dark threshold component
    # plus a predicted vacancy must not create another physical bead.
    from .evidence import native_response,can_admit_identity
    response=native_response(np.full((64,64,3),20,np.uint8),[32.,32.]);assert response['pixel_count']==441 and not can_admit_identity(response);assert not can_admit_identity(response,dict(authority='lattice prediction',separate_body=True));assert can_admit_identity(response,dict(authority='maker visible-body review',separate_body=True))
    # Original foreground/intervener gates, independently coded.
    rr,gg,bb=rgb.transpose(2,0,1);mask=((rr>1.5*bb)&(rr>.13))|(v<.30);fg=ndi.binary_closing(mask,iterations=5);lab,_=ndi.label(~fg);counts=np.bincount(lab.ravel());small=counts<600;small[0]=False;fg|=small[lab];lab,_=ndi.label(fg);counts=np.bincount(lab.ravel());counts[0]=0;fg=(lab==counts.argmax()).astype(float)
    audit=read(r/'results/link-audit.json')['links']
    for row in audit:
        e=row['edge'];u,z=e['source'],e['target'];p0=np.array(obs[u]['xy']);p1=np.array(obs[z]['xy']);d=p1-p0;length2=float(d@d)
        for which,ignored in [('before',set()),('after',excluded)]:
            blockers=[]
            for o,x in obs.items():
                if o in ignored|{u,z}:continue
                rel=np.array(x['xy'])-p0;t=float(rel@d/length2)
                if .2<t<.8 and np.linalg.norm(rel-t*d)<7:blockers.append(o)
            samples=np.linspace(p0,p1,31);fraction=float(ndi.map_coordinates(fg,[samples[:,1],samples[:,0]],order=1).mean());assert row[which]['intervening_observations']==sorted(blockers);assert abs(row[which]['foreground_fraction']-fraction)<1e-7
        assert len(row['before']['intervening_observations'])==1 and not row['after']['intervening_observations'];assert row['after']['allowed'] and row['geometry_plausible'] and row['accepted'];assert .65<=row['length_ratio']<=1.45;assert frozenset((u,z)) in edges
    # Independent matched-cohort recurrence and weighted consensus.
    ctrl=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={x['id']:x['section'] for x in ctrl['rows']+ctrl['maker_geography']};rawobs={x['id']:x for x in raw['observations']};weights={o:.25 if 'provisional' in str(rawobs[o]).lower() else .55 if rawobs[o]['color']=='black' else 1. for o in co};diagnostics=read(r/'analysis/diagnostics.json.gz');core=set(diagnostics['fixed_core_ids']);degree=Counter(o for e in old['edges'] for o in [e['source'],e['target']]);assert core=={o for o in ac if degree[o]>=4} and len(core)==710;pathchecks=0
    for name,stage in diagnostics['stages'].items():
        ids=set(co) if name in ['R335_all','maker_colors_same_1041'] else core if name.startswith('fixed_interior') else set(ac);oo2=oo if name in ['R335_all','common_active_before','fixed_interior_before'] else obs;occ={co[o]:o for o in ids};paircount=agreement=0;breaks=[]
        for o in sorted(ids):
            z=occ.get((co[o][0]+16,co[o][1]+16))
            if z:paircount+=1;agreement+=oo2[o]['color']==oo2[z]['color']
            examples=[occ.get((co[o][0]+16*n,co[o][1]+16*n)) for n in range(-15,16) if n];examples=[z for z in examples if z and blocks[z] not in [(blocks[o]-1)%12,blocks[o],(blocks[o]+1)%12]];counts=Counter(oo2[z]['color'] for z in examples);win,num=counts.most_common(1)[0] if counts else ('?',0);strong=num>=3 and len({blocks[z] for z in examples if oo2[z]['color']==win})>=3 and num/max(len(examples),1)>=.8
            if strong and win!=oo2[o]['color']:breaks.append(o)
        assert paircount==stage['recurrence_pairs'] and agreement==stage['recurrence_agree'];assert breaks==[x['id'] for x in stage['breaks']]
        for entry in stage['motif208']:
            jj=[o for o in ids if (7*co[o][0]+6*co[o][1])%208==entry['residue']];counts=Counter()
            for o in jj:counts[oo2[o]['color']]+=weights[o]
            win=counts.most_common(1)[0][0] if counts else '?';support=[o for o in jj if oo2[o]['color']==win];fraction=counts[win]/sum(counts.values()) if counts else 0.;known=len(support)>=3 and len({blocks[o] for o in support})>=3 and fraction>=.8;assert entry['color']==(win if known else '?')
        allowed=oldedges if name in ['R335_all','maker_colors_same_1041','common_active_before','fixed_interior_before'] else edges
        for path in stage['staircases']['traces']:
            assert all(o in ids and oo2[o]['color'] in path['palette'] for o in path['ids']);assert path['inferred_links']==0 and path['length']==len(path['ids'])
            for j,(u,z) in enumerate(zip(path['ids'],path['ids'][1:])):
                assert frozenset((u,z)) in allowed;runs=path['runs'][0];d=[(1,0)]*runs+[(0,1)]*runs;assert tuple(np.array(co[z])-co[u])==d[(path['step_phase']+j)%(2*runs)];pathchecks+=1
    assert diagnostics['stages']['fixed_interior_before']==diagnostics['stages']['fixed_interior_after']
    panel=read(r/'review/panels.json');case=read(r/'review/cases.json');assert len(case)==2;assert not {c['id'] for c in case}&excluded;keychecks=0
    for c in case:
        p0=panel[c['panel']];key=p0['key'];assert key[0]['id']==c['id'];assert np.array_equal(np.array(co[key[1]['id']])-co[key[0]['id']],[-1,-1]);assert frozenset((key[0]['id'],key[1]['id'])) not in edges
        for x in key:assert x['id'] in ac and x['color']==obs[x['id']]['color'] and x['xy']==obs[x['id']]['xy'];keychecks+=1
        for m in key[2:4]:assert m['id'] in adj[key[0]['id']]&adj[key[1]['id']]
    crops=read(r/'review/native-crops.json')
    for x in crops:
        a0,b0,c0,d0=x['bbox'];assert np.array_equal(np.asarray(Image.open(r/'review'/x['file'])),photo[b0:d0,a0:c0])
    ref=read(ROOT/'photo2/r328/results/reference.json');assert sum(x['recovered'] for x in ref['links'])==65
    for e in ref['links']:
        if e['recovered']:assert frozenset((e['source'],e['target'])) in edges
    preserved=dict(read(ROOT/'photo2/r335/input-seal.json')['sources'])
    for path,digest in read(ROOT/'photo2/r335/manifest.json')['files'].items():
        if path.startswith('photo2/'):preserved[path]=digest
    for path in ['photo2/r335/manifest.json','photo2/r335/delivery.json']:preserved[path]=sha(ROOT/path)
    for path,digest in preserved.items():assert sha(ROOT/path)==digest,path
    save(r/'input-seal.json',dict(baseline_commit=BASE,sources=preserved))
    receipt=dict(passed=True,maker_decisions=10,independently_reproduced_suspicious_pixel_sets=4,all_eight_displayed_sample_sets_checked=True,lighting_pixels_exact=True,body_ownership_contract_regressions=3,native_response_records_checked=nativechecks,added_links_checked=5,deactivated_incident_links=6,active_observations=1057,active_indexed=1039,active_links=2284,unique_quotient_sites=1039,component_nodes=len(seen),matched_diagnostic_cohorts=6,staircase_edge_checks=pathchecks,primary_questions=2,numbered_support_checks=keychecks,literal_native_crops=len(crops),sealed_historical_scientific_files=len(preserved),R161=dict(associations=33,interior=25,links=65,interior_links=45,wrong_links=0),seconds=time.perf_counter()-start,limits='Independent pixel/equation/provenance checks are not new blind body-identity accuracy, a physical bead census or recovery of the actual repeat.')
    save(a.output,receipt);print(receipt)
if __name__=='__main__':main()
