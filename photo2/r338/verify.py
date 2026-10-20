"""Independent serialized-evidence checks; no admission or inference routine reused."""
import argparse,time,math
from scipy import ndimage as ndi
from .common import ROOT,read,save,sha,np,Counter,defaultdict,deque,Image,ImageOps
PALETTE=['red','yellow','black']
def rem(v,H):
    a,b=map(int,v);return a%H[0],b-(a//H[0])*H[1]
def independent_scores(names,obs,co,blocks,hier,occurrence):
    colors={o:obs[o]['color'] for o in names};index={o:(7*co[o][0]+6*co[o][1])%2704 for o in names};pred={};priors={}
    for fold in (range(13) if occurrence else range(12)):
        test=[o for o in names if (index[o]//208 if occurrence else blocks[o])==fold]
        train=[o for o in names if index[o]//208!=fold] if occurrence else [o for o in names if blocks[o] not in {(fold-1)%12,fold,(fold+1)%12}]
        base=Counter(colors[o] for o in train);prior=np.array([(base[c]+1)/(len(train)+3) for c in PALETTE]);counts=defaultdict(Counter);parent=defaultdict(Counter)
        for o in train:counts[index[o]%208][colors[o]]+=1;parent[index[o]%104][colors[o]]+=1
        for o in test:
            ct=counts[index[o]%208];vec=np.array([ct[c] for c in PALETTE]);pt=parent[index[o]%104];p=(np.array([pt[c] for c in PALETTE])+3*prior)/(sum(pt.values())+3)
            pred[o]=(vec+p)/(sum(ct.values())+1) if hier else (vec+3*prior)/(sum(ct.values())+3);priors[o]=prior
    gain=np.mean([math.log(pred[o][PALETTE.index(colors[o])]/priors[o][PALETTE.index(colors[o])]) for o in names]);agreement=np.mean([PALETTE[int(pred[o].argmax())]==colors[o] for o in names]);return float(gain),float(agreement)
def run(root):
    started=time.perf_counter();root=__import__('pathlib').Path(root);seal=read(root/'audit/input-seal.json');assert all(sha(ROOT/p)==h for p,h in seal.items());legacy=read(ROOT/'photo2/r338/legacy-cache-verification.json');assert legacy['passed'] and all(sha(ROOT/r['path'])==r['sha256'] for r in legacy['records']);g=read(ROOT/'photo2/r336/results/graph.json.gz');new=read(root/'results/graph.json.gz');obs={r['id']:r for r in new['observations']};oldobs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in new['coordinates']};oldco={r['id']:r['ab'] for r in g['coordinates']};H=new['H'];oid='R332-B-0098-0092'
    assert H==g['H']==[214,201];assert len(obs)==1058 and len(co)==1040 and len(new['edges'])==2287;assert {o for o in obs if o not in oldobs}=={oid};assert all(obs[o]==r for o,r in oldobs.items());assert all(co[o]==v for o,v in oldco.items());assert new['edges'][:2284]==g['edges'];assert new['indexed_colors']==dict(Counter(obs[o]['color'] for o in co))
    assert len({rem(v,H) for v in co.values()})==1040;assert len({(7*a+6*b)%2704 for a,b in co.values()})==1040;adj=defaultdict(set)
    for e in new['edges']:
        a,z=e['source'],e['target'];d=e['delta_ab'];assert tuple(d) in [(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)];assert rem([co[z][j]-co[a][j]-d[j] for j in range(2)],H)==(0,0);adj[a].add(z);adj[z].add(a)
    seen={next(iter(co))};queue=deque(seen)
    while queue:
        for z in adj[queue.popleft()]-seen:seen.add(z);queue.append(z)
    assert len(seen)==1040
    maker=next(r for r in read(ROOT/'photo2/r336/results/maker-decisions.json')['decisions'] if r['id']==oid);support=maker['accepted_association']['measured_support'];assert obs[oid]['xy']==support and co[oid]==[98,92];assert maker['not_alias_of']==obs[oid]['not_alias_of']=='D40-K-1036-2780';assert np.linalg.norm(np.array(support)-obs['D40-K-1036-2780']['xy'])>20;assert 'REC266-P134549' not in obs and obs[oid]['known_cache_aliases']==['REC266-P134549']
    audit=read(root/'audit/audit.json.gz');assert len(audit['rows'])==3993 and len(audit['ranked'])==5;assert all(not r.get('visible_body_established') for r in audit['rows']);fresh=[r for r in audit['rows'] if r['source_kind']=='unseeded-component'];photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));freshpixels=0
    for r in fresh:
        p=np.array(r['pixels_xy']);assert np.allclose(p.mean(0),r['xy'],rtol=0,atol=1e-12);assert 25<=len(p)<=900 and min(np.ptp(p,axis=0))>=4 and max(np.ptp(p,axis=0))<=48;rgb=photo[p[:,1],p[:,0]].astype(np.float32)/255;red,green,blue=rgb.T;val=rgb.max(1)
        valid=(red>1.8*green)&(red>2.5*blue)&(red>.16) if r['cue']=='red-cue' else (green>.35*red)&(green>1.8*blue)&(red>.9*green)&(red>.16) if r['cue']=='yellow-cue' else (val<.36)&(val-rgb.min(1)<.13)&(val>.012)
        assert valid.all();freshpixels+=len(p)
    quarantine=[r for r in audit['rows'] if r['status'] in ['maker-excluded','quarantined-excluded-identity-or-phantom-site-cue']];assert len(quarantine)==28;assert not any(o in obs for o in ['R332-B-0196-0183','R332-B-0138-0130','R338-N-1009-2826','REC266-P143676','REC266-P055677'])
    row=next(r for r in audit['rows'] if r['id']==oid);assert all(o in oldco for o in row['anchors']) and oid not in row['anchors'];aa=np.array([oldco[o] for o in row['anchors']]);rootcell=aa[0];aa-=np.rint((aa-rootcell)@H/(np.dot(H,H))).astype(int)[:,None]*H;u=(aa-rootcell)/3;X=np.c_[np.ones(len(u)),u,u[:,0]**2,u[:,0]*u[:,1],u[:,1]**2];xy=np.array([oldobs[o]['xy'] for o in row['anchors']]);wt=np.exp(-np.sum((xy-support)**2,axis=1)/10000)
    for _ in range(3):
        M=X.T@(wt[:,None]*X)+np.diag([0,0,0,.35,.35,.35]);beta=np.linalg.solve(M,X.T@(wt[:,None]*xy));res=np.linalg.norm(X@beta-xy,axis=1);wt*=np.minimum(1,6/np.maximum(res,1e-6))
    uv=(np.array(co[oid])-rootcell)/3;prediction=np.r_[1,uv,uv[0]**2,uv.prod(),uv[1]**2]@beta;assert np.allclose(prediction,row['prediction'],atol=1e-8);assert abs(np.linalg.norm(prediction-support)-row['error'])<1e-8
    links=read(root/'results/link-audit.json');assert len(links)==3;rawrgb=photo.astype(float)/255;red,green,blue=rawrgb.transpose(2,0,1);raw=((red>1.5*blue)&(red>.13))|(rawrgb.max(2)<.30);fractions=[]
    blockers={o:r for o,r in oldobs.items() if o in oldco or r.get('r336_roles',{}).get('link_obstruction')};blockers[oid]=obs[oid]
    for r in links:
        e=r['edge'];p=np.array(obs[e['source']]['xy']);q=np.array(obs[e['target']]['xy']);v=q-p;points=np.array([p+i/30*(q-p) for i in range(31)]);assert np.allclose(points,r['filled_corridor']['sample_xy']);fraction=float(ndi.map_coordinates(raw.astype(float),[points[:,1],points[:,0]],order=1,mode='nearest').mean());assert abs(fraction-r['raw_fraction'])<1e-12;blocked=[]
        for o,record in blockers.items():
            if o in [e['source'],e['target']]:continue
            w=np.array(record['xy'])-p;t=w@v/(v@v)
            if .2<t<.8 and np.linalg.norm(w-t*v)<7:blocked.append(o)
        assert blocked==[];lengths=[np.linalg.norm(np.array(obs[a]['xy'])-obs[z]['xy']) for a,z in r['reference_links']];ratio=np.linalg.norm(v)/np.median(lengths);assert abs(ratio-r['ratio'])<1e-12 and .65<=ratio<=1.45;fractions.append(fraction)
    measurement=read(root/'measurement/pigment.json.gz')['records'];assert len(measurement)==166;ringpixels=0
    for record in measurement:
        assert not record['hue_used_for_black'] and not record['body_identity_established_by_classifier']
        for mode in ['broad','compact']:
            for t in record[mode]:
                points=np.array(t['ring_pixels']);ringpixels+=len(points)
                if not len(points):continue
                rgb=rawrgb[points[:,1],points[:,0]];intensity=rgb@np.array([.299,.587,.114]);value=rgb.max(1)
                for key,val in [('median_intensity',np.median(intensity)),('q75_intensity',np.quantile(intensity,.75)),('median_max_channel',np.median(value)),('q75_max_channel',np.quantile(value,.75)),('dark_fraction',np.mean(value<=.35))]:assert abs(float(val)-t[key])<1e-12
        def dec(ts):return 'black' if sum(t['positive'] for t in ts)>=2 and not any(t['negative'] for t in ts) else 'not-black' if sum(t['negative'] for t in ts)>=2 and not any(t['positive'] for t in ts) else 'unknown'
        a,b=dec(record['broad']),dec(record['compact']);assert a==record['broad_decision'] and b==record['compact_decision'];assert record['black_first']==(a if a==b else 'unknown')
    assert next(r for r in measurement if r['id']==oid)['black_first']=='black';assert next(r for r in measurement if r['id']=='R338-N-1009-2826')['black_first']=='unknown'
    analysis=read(root/'analysis/analysis.json.gz');assert analysis['body_freeze_sha256']==sha(root/'results/body-freeze.json');blocks=analysis['blocks'];core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids']);physical={r['id'] for r in analysis['physical_interior_records'] if r['physical_interior']};assert len(core)==710 and len(physical)==450 and oid in physical and oid not in core
    for r in analysis['physical_interior_records']:assert r['physical_interior']==(min(r['settings_clearance'])>=max(18,.65*r['common_support_spacing']))
    cohorts={'R337_common_baseline':sorted(oldco),'R338_common_1039':sorted(oldco),'R338_expanded':sorted(co),'frozen710_before':sorted(core),'frozen710_after':sorted(core),'physical_interior_common_before':sorted(physical&set(oldco)),'physical_interior_common_after':sorted(physical&set(oldco)),'physical_interior_expanded':sorted(physical)};scorechecks=0
    for name,names in cohorts.items():
        result=analysis['cohorts'][name];assert result['n']==len(names);statuses=[]
        for residue in range(208):
            ids=[o for o in names if (7*co[o][0]+6*co[o][1])%208==residue];counts=Counter(obs[o]['color'] for o in ids);sections={blocks[o] for o in ids};status='conflict' if len(counts)>1 else 'strong' if len(ids)>=3 and len(sections)>=3 else 'observed' if ids else 'unknown';entry=result['entries'][residue];assert counts==entry['counts'] and ids==entry['ids'] and status==entry['status'];statuses.append(status)
        assert statuses.count('strong')==result['supported'] and statuses.count('conflict')==result['conflicting']
        for score in result['scores']:
            for kind,occur in [('geographic',False),('whole_occurrence',True)]:
                gain,agreement=independent_scores(names,obs,co,blocks,score['model']=='hier104',occur);assert abs(gain-score[kind]['gain_nats'])<1e-12 and abs(agreement-score[kind]['agreement'])<1e-12;scorechecks+=1
    assert analysis['cohorts']['R337_common_baseline']==analysis['cohorts']['R338_common_1039'];assert analysis['cohorts']['frozen710_before']==analysis['cohorts']['frozen710_after'];assert [(t['residue'],t['before_status'],t['after_status']) for t in analysis['transitions']]==[(198,'strong','strong')];v=analysis['newly_indexed_validation'][0];assert v['id']==oid and v['occurrence']==5 and v['training_occurrences']==[6,7,8];assert all(((7*oldco[o][0]+6*oldco[o][1])%2704)//208!=5 for o in v['training_ids']);assert v['prediction']==v['baseline_prediction']=='black' and v['agrees'];assert abs(v['probabilities']['black']-.6768041237113401)<1e-12
    panels=read(root/'review/panels.json');assert len(panels)==23;keycount=0
    for r in panels.values():
        assert r['key'][0]['number']==1 and r['key'][0]['id']==r['id'];assert [k['number'] for k in r['key']]==list(range(1,len(r['key'])+1));keys={k['id'] for k in r['key']}
        for k in r['key']:assert k['xy']==obs[k['id']]['xy'] and k['color']==obs[k['id']]['color'] and k['ab']==co[k['id']];keycount+=1
        assert r['edges']==[e for e in new['edges'] if e['source'] in keys and e['target'] in keys]
    crops=read(root/'review/native-crops.json')
    for r in crops:assert np.array_equal(np.asarray(Image.open(root/'review'/r['file'])),np.asarray(Image.fromarray(photo).crop(r['bbox'])))
    receipt=dict(passed=True,historical_hashes=len(seal),original_records_exact=1057,original_coordinates_exact=1039,original_links_exact=2284,all_primitive_equations=2287,unique_lattice_sites=1040,unique_A_mod2704=1040,components=1,candidate_source_rows=3993,unseeded_components=len(fresh),component_native_pixels=freshpixels,quarantined_source_cues=28,independent_local_regression=True,new_corridors=3,raw_corridor_fractions=fractions,pigment_targets=len(measurement),native_ring_pixels=ringpixels,cohorts=8,independent_predictor_checks=scorechecks,common_cohorts_identical=True,strict_supported=176,strict_conflicting=24,strict_insufficient=8,numbered_panels=len(panels),local_key_rows=keycount,literal_native_crops=len(crops),seconds=time.perf_counter()-started);save(root/'verification.json',receipt);print('PASS R338 independent',receipt)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);run(p.parse_args().root)
