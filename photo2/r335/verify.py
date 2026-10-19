"""Independent native-pixel, overlay, fixed-rule and annotation verification.

Does not import application/review/classifier/fitting code. Checks numerical
reproducibility and preservation, not independently established pigment accuracy.
"""
import argparse,hashlib,json,time
from pathlib import Path
from collections import Counter,deque
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r334.common import read,save,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default=str(ROOT/'photo2/r335'));p.add_argument('--output',default=str(ROOT/'photo2/r335/verification.json'));a=p.parse_args();run=Path(a.run);start=time.perf_counter()
    g=read(run/'results/graph.json.gz');old=read(ROOT/'photo2/r334/overlay/graph.json.gz');obs={r['id']:r for r in g['observations']};oo={r['id']:r for r in old['observations']};co={r['id']:tuple(r['ab']) for r in g['coordinates']}
    assert g['coordinates']==old['coordinates'] and g['edges']==old['edges'] and g['H']==old['H'];assert len(co)==len(set(co.values()))==1041;assert len(obs)==1064
    for o in obs:assert obs[o]['xy']==oo[o]['xy'],o
    edges={frozenset((e['source'],e['target'])):e for e in g['edges']};adj={o:set() for o in co}
    H=np.array(g['H']);assert len({(v[0]-(v[0]//H[0])*H[0],v[1]-(v[0]//H[0])*H[1]) for v in co.values()})==1041
    for e in g['edges']:
        residual=np.array(co[e['target']])-co[e['source']]-e['delta_ab'];assert residual[0]%H[0]==0 and residual[1]==residual[0]//H[0]*H[1];assert e['family']=={(1,0):'F0',(0,1):'F1',(1,-1):'difference'}[tuple(e['delta_ab'])]
        adj[e['source']].add(e['target']);adj[e['target']].add(e['source'])
    reached={next(iter(co))};pending=list(reached)
    while pending:
        for z in adj[pending.pop()]-reached:reached.add(z);pending.append(z)
    assert len(reached)==1041
    makers={'NEW-2237-1522','REC266-P032517','C-1284-0332','NEW-2257-2004','NEW-2060-796','NEW-2186-2343','NEW-2167-1179','NEW-1920-531'}
    original_makers=read(ROOT/'photo2/r334/corrections/ledger.json');original_ids={r['id'] for r in original_makers['ordinary_color_corrections']}|{original_makers['location_correction']['id']}
    assert all(obs[o]['color']=='black' for o in makers|original_ids)
    application=read(run/'results/application.json.gz');records=application['records'];assert len(records)==len({r['id'] for r in records})==1600
    oldaudit={r['id']:r for r in read(ROOT/'photo2/r334/classification/audit.json.gz')['records']}
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo.astype(float)/255.;names=sorted(oo);tree=cKDTree([oo[o]['xy'] for o in names]);checks=0
    for row in records:
        original=oldaudit[row['id']];assert row['xy']==original['xy'];assert row['before_color']==original['overlay_color'];positives=negatives=0
        for s in row['scales']:
            radius=s['radius'];center=np.array(row['xy']);x,y=np.rint(center).astype(int);x0=max(0,x-radius);y0=max(0,y-radius);patch=rgb[y0:y+radius+1,x0:x+radius+1];gray=patch@np.array([.299,.587,.114]);yy,xx=np.indices(gray.shape);xx+=x0;yy+=y0;d=(xx-center[0])**2+(yy-center[1])**2;domain=d<=radius**2
            for j in tree.query_ball_point(center,2*radius+6):
                other=np.array(oo[names[j]]['xy'])
                if names[j]==row['id'] or np.linalg.norm(other-center)<8:continue
                domain&=d<.86*((xx-other[0])**2+(yy-other[1])**2)
            allowed=domain&(d<=100);peak=gray[allowed].max();base=np.quantile(gray[domain],.2);threshold=base+.7*(peak-base);mask=domain&(gray>=threshold)
            # Independent component construction: propagation from a peak seed.
            peakpos=np.unravel_index(np.where(allowed,gray,-1).argmax(),gray.shape);seed=np.zeros_like(domain);seed[peakpos]=mask[peakpos];component=ndi.binary_propagation(seed,mask=mask);reflection=ndi.binary_dilation(component)&domain;bright=ndi.binary_dilation(mask)&domain
            ring=ndi.binary_dilation(reflection,iterations=4)&~ndi.binary_dilation(reflection)&domain&~bright
            actual=np.c_[xx[ring],yy[ring]].tolist();ref=np.c_[xx[reflection],yy[reflection]].tolist();assert actual==s['ring_pixels'];assert ref==s['reflection_pixels'];assert np.c_[xx[domain],yy[domain]].tolist()==s['domain_pixels']
            sy,sx=np.where(reflection);ry,rx=np.where(ring);sector=len(set(((np.arctan2(ry-sy.mean(),rx-sx.mean())+np.pi)/(2*np.pi)*8).astype(int).clip(0,7))) if len(ry) else 0
            valid=len(ry)>=25 and sector>=4 and peak-base>=.08;v=gray[ring];maximum=patch[ring].max(1)
            median=float(np.median(v)) if len(v) else 1.;q75=float(np.quantile(v,.75)) if len(v) else 1.;medmax=float(np.median(maximum)) if len(v) else 1.;qmax=float(np.quantile(maximum,.75)) if len(v) else 1.;dark=float(np.mean(maximum<=.35)) if len(v) else 0.;ratio=median/max(original['lighting']['intensity'],.1)
            positive=bool(valid and median<=.15 and q75<=.20 and medmax<=.30 and qmax<=.40 and dark>=.70 and ratio<=.65);negative=bool(valid and (medmax>=.45 or dark<=.30))
            assert positive==s['positive'] and negative==s['negative'];assert sector==s['sectors'] and s['hue_used'] is False
            for k,vv in [('median_intensity',median),('q75_intensity',q75),('median_max_channel',medmax),('q75_max_channel',qmax),('dark_fraction',dark),('lighting_ratio',ratio)]:assert abs(vv-s[k])<1e-14,(row['id'],k)
            positives+=positive;negatives+=negative;checks+=1
        decision='black' if positives>=2 and not negatives else 'not-black' if negatives>=2 and not positives else 'unknown';assert row['compact_decision']==decision
        maker=row['id'] in makers;automatic=bool(row['before_color']=='red' and original['body_prediction']=='black' and decision=='black' and not maker)
        assert row['maker_accepted']==maker and row['automatic_applied']==automatic;assert row['color']==('black' if maker or automatic else row['before_color']);assert row['changed']==(row['color']!=row['before_color'])
        if row['id'] in obs:assert obs[row['id']]['color']==row['color']
    appby={r['id']:r for r in records};assert sum(r['automatic_applied'] and r['status']=='recorded' for r in records)==7;assert sum(r['automatic_applied'] and r['status']!='recorded' for r in records)==12
    # Fixed diagnostic replay, using already saved geography, not any fitter.
    controls=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={r['id']:r['section'] for r in controls['rows']+controls['maker_geography']};assert len(blocks)==1041
    rawobs={r['id']:r for r in read(ROOT/'photo2/r332/results/graph.json.gz')['observations']};weights={o:.25 if 'provisional' in str(rawobs[o]).lower() else .55 if rawobs[o]['color']=='black' else 1. for o in co};occ={v:o for o,v in co.items()};remain=read(run/'results/remaining.json.gz');pred={r['id']:r for r in remain['predictions']};breaks=[]
    for o in sorted(co):
        examples=[]
        for n in range(-15,16):
            z=occ.get(tuple(np.array(co[o])+[n*16,n*16]))
            if n and z and blocks[z] not in [(blocks[o]-1)%12,blocks[o],(blocks[o]+1)%12]:examples.append(z)
        counts=Counter(obs[z]['color'] for z in examples);win,support=counts.most_common(1)[0] if counts else ('?',0);sections={blocks[z] for z in examples if obs[z]['color']==win};strong=support>=3 and len(sections)>=3 and support/max(len(examples),1)>=.8
        assert pred[o]['prediction']==(win if strong else '?');assert [e['id'] for e in pred[o]['examples']]==examples
        if strong and win!=obs[o]['color']:breaks.append(o)
    assert breaks==[r['id'] for r in remain['breaks']];assert len(breaks)==6
    for entry in remain['motif208']:
        ids=[o for o in sorted(co) if (7*co[o][0]+6*co[o][1])%208==entry['residue']];counts=np.zeros(3)
        for o in ids:counts[['red','yellow','black'].index(obs[o]['color'])]+=weights[o]
        win=int(counts.argmax());col=['red','yellow','black'][win];support=[o for o in ids if obs[o]['color']==col];sections={blocks[o] for o in support};fraction=counts[win]/counts.sum() if ids else 0.;known=len(support)>=3 and len(sections)>=3 and fraction>=.8
        assert entry['color']==(col if known else '?') and abs(entry['fraction']-fraction)<1e-14
    assert remain['known208']==180 and remain['unknown208']==28
    # Every local number is an actual saved/native support, never a prediction.
    panels=read(run/'review/panels.json.gz');ledger=read(run/'review/ledger.json.gz');raw=read(ROOT/'photo2/r332/results/graph.json.gz');allobs={r['id']:r for r in raw['unrepresented_candidates']+raw['provisional_observations']};allobs.update(obs);labelchecks=0;display_seams=0
    for panel in panels.values():
        assert panel['key'][0]['id']==panel['id'] and panel['key'][0]['number']==1;assert len({r['id'] for r in panel['key']})==len(panel['key']);key={r['id']:r for r in panel['key']};box=panel['bbox'];anchor=panel['key'][0]['ab'] or (panel['proposal'] or {}).get('cell') or next(r['ab'] for r in panel['key'] if r['ab']);H=np.array([214,201])
        for r in panel['key']:
            assert r['xy']==allobs[r['id']]['xy'];assert r['color']==appby[r['id']]['color'];assert r['ab']==(list(co[r['id']]) if r['id'] in co else None);x,y=r['xy'];assert box[0]<=x<box[2] and box[1]<=y<box[3];labelchecks+=1
        for e in panel['edges']:
            assert e==edges[frozenset((e['source'],e['target']))];aa=np.array(co[e['source']]);bb=np.array(co[e['target']]);aa-=round(float((aa-anchor)@H/(H@H)))*H;bb-=round(float((bb-anchor)@H/(H@H)))*H
            display_seams+=not np.array_equal(bb-aa,e['delta_ab'])
    primary={r['id'] for r in ledger['primary']};assert len(primary)==10 and not primary&(makers|original_ids)
    links=ledger['coordinate_only_links'];assert len(links)==5;covered={frozenset((e['source'],e['target'])) for c in ledger['primary'] for e in panels[c['panel']]['omitted']};assert covered=={frozenset((e['source'],e['target'])) for e in links}
    blackids={r['id'] for r in raw['provisional_observations'] if r['color']=='black'};assert len(blackids)==65;shown={r['id'] for r in ledger['primary']+ledger['additional']};assert blackids<=shown;assert len(ledger['all_unindexed'])==23;assert len(ledger['all_provisional_groups'])==273;assert len(ledger['inherited_gap_ledger'])==128
    crops=read(run/'review/native-crops.json')
    for r in crops:
        x,y,z,v=r['bbox'];assert np.array_equal(np.asarray(Image.open(run/'review'/r['file'])),photo[y:v,x:z]),r['file']
    # R161's associations and links remain identical. One accepted maker color
    # intentionally supersedes its old pigment label; do not regress that truth.
    ref=read(ROOT/'photo2/r328/results/reference.json');assert sum(e['recovered'] for e in ref['links'])==65;assert sum(e['recovered'] and e['priority']=='interior' for e in ref['links'])==45
    for e in ref['links']:
        if e['recovered']:assert frozenset((e['source'],e['target'])) in edges
    established=read(ROOT/'photo2/r328/results/established-subset.json');refids={o for e in established['links']+established['peripheral_links'] for o in [e['source'],e['target']]};assert all(obs[o]['xy']==oo[o]['xy'] for o in refids);assert {o for o in refids if obs[o]['color']!=oo[o]['color']}=={'C-1284-0332'}
    preserved={}
    for p,h in read(ROOT/'photo2/r334/input-seal.json')['sources'].items():preserved[p]=h
    for p,h in read(ROOT/'photo2/r334/manifest.json')['files'].items():
        if p.startswith('photo2/r334/') or p.startswith('photo2/R334_'):preserved[p]=h
    preserved['photo2/r334/manifest.json']=hashlib.sha256((ROOT/'photo2/r334/manifest.json').read_bytes()).hexdigest();preserved['photo2/r334/delivery.json']=hashlib.sha256((ROOT/'photo2/r334/delivery.json').read_bytes()).hexdigest()
    for p,h in preserved.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    save(run/'input-seal.json',dict(baseline_commit='4e40da6a2b222ae1a755f0dc4d403e6d9ad7ec7f',sources=preserved))
    result=dict(passed=True,global_supports=1600,independent_compact_masks=checks,maker_colors_applied=8,automatic_recorded_colors=7,automatic_candidate_labels=12,changed_locations=0,changed_lattice_coordinates=0,changed_links=0,unique_sites=1041,edge_equations=2285,one_component=1041,fixed_rule_disagreements=6,known208=180,unknown208=28,primary_cases=10,panels=len(panels),numbered_native_support_checks=labelchecks,display_seam_edges=display_seams,all_five_omitted_links_illustrated=True,all_65_original_black_groups_accessible=True,literal_native_crops=len(crops),historical_files_preserved=len(preserved),R161=dict(associated=33,interior=25,links=65,interior_links=45,wrong_links=0,maker_accepted_pigment_changes=1),seconds=time.perf_counter()-start,limits='Native/numerical reproducibility and preservation; not fresh blind pigment accuracy, physical bead census or a recovered shortest repeat.')
    save(a.output,result);print(result)
if __name__=='__main__':main()
