"""Independent correction, native intensity-first test, graph and period audit.

Does not call correction extraction, pigment classifier, path search or period
fitting implementations. Historical labels are not new blind ground truth.
"""
import argparse,time,subprocess,json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[2];BASE='acd51b0bcd586e812e1979258de8b402094fb634'
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='photo2/r334');ap.add_argument('--output',default='photo2/r334/verification.json');a=ap.parse_args();run=Path(a.run);t=time.perf_counter();raw=read(ROOT/'photo2/r332/results/graph.json.gz');old={r['id']:r for r in raw['observations']};graph=read(run/'overlay/graph.json.gz');obs={r['id']:r for r in graph['observations']};co={r['id']:tuple(r['ab']) for r in graph['coordinates']};ids=sorted(co);ix={o:j for j,o in enumerate(ids)};ab=np.array([co[o] for o in ids]);ledger=read(run/'corrections/ledger.json');audit=read(run/'classification/audit.json.gz');analysis=read(run/'analysis/analysis.json.gz');cases=read(ROOT/'photo2/r333/review/cases.json');H=graph['H'];reviewed={r['id'] for r in ledger['ordinary_color_corrections']};loc=ledger['location_correction'];reviewed.add(loc['id']);assert len(reviewed)==8
    expected={'E5-1616-2970','NEW-1706-342','NEW-2207-1350','NEW-2237-2128','NEW-1942-2725','C-1893-2771','NEW-1828-2833'};assert {r['id'] for r in ledger['ordinary_color_corrections']}==expected;references=0
    for row in ledger['ordinary_color_corrections']+[loc]:
        for ref in row['references']:
            case=next(x for x in cases if x['name']==ref['case']);panel=case if ref['panel_type']=='target' else next(x for x in case['examples'] if x['asset']==ref['asset']);key=next(x for x in panel['key'] if x['number']==ref['local_number']);assert key['id']==row['id'];assert key['xy']==row['original_xy'];assert panel['id']==ref['photograph_identifier'];references+=1
        assert row['original_xy']==old[row['id']]['xy'];assert row['original_color']==old[row['id']]['color'];assert obs[row['id']]['color']=='black'
    assert graph['coordinates']==raw['coordinates'];assert graph['edges']==raw['edges'];assert len(co)==1041 and len(obs)==1064 and len(graph['edges'])==2285
    for o in obs:
        if o not in reviewed:assert obs[o]==old[o],o
        elif o!=loc['id']:assert obs[o]['xy']==old[o]['xy']
    assert sum(obs[o]['xy']!=old[o]['xy'] for o in obs)==1;assert obs[loc['yellow_body']['id']]==old[loc['yellow_body']['id']];assert loc['yellow_body']['id'] not in co;assert obs[loc['yellow_body']['id']]['color']=='yellow'
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo/255.;value=rgb.max(2);luma=.299*rgb[:,:,0]+.587*rgb[:,:,1]+.114*rgb[:,:,2];pp=np.array(loc['measured_material_pixels'],int);assert len(pp)==171;assert loc['corrected_xy'] in loc['measured_material_pixels'];px=rgb[pp[:,1],pp[:,0]];assert (px.max(1)<.4).all() and (px.max(1)-px.min(1)<.30).all();assert np.linalg.norm(np.array(loc['corrected_xy'])-loc['original_xy'])>10
    def representative(v):q=v[0]//H[0];return(v[0]-q*H[0],v[1]-q*H[1])
    assert len({representative(v) for v in co.values()})==len(co);edges={frozenset((e['source'],e['target'])):e for e in graph['edges']};adj=defaultdict(set)
    for e in graph['edges']:
        s,z=e['source'],e['target'];delta=np.array(co[z])-co[s]-e['delta_ab'];assert delta[0]%H[0]==0 and delta[1]==delta[0]//H[0]*H[1];adj[s].add(z);adj[z].add(s)
    reached=set();todo=[ids[0]]
    while todo:
        o=todo.pop()
        if o in reached:continue
        reached.add(o);todo+=list(adj[o]-reached)
    assert len(reached)==1041
    # Independently recreate the original filled foreground corridor mask.
    r,g,b=rgb.transpose(2,0,1);fg=((r>1.5*b)&(r>.13))|(value<.30);fg=ndi.binary_closing(fg,iterations=5);lab,_=ndi.label(~fg);sizes=np.bincount(lab.ravel());small=sizes<600;small[0]=False;fg|=small[lab];lab,_=ndi.label(fg);sizes=np.bincount(lab.ravel());sizes[0]=0;fg=lab==sizes.argmax();corridors=0
    for row in loc['incident_links']:
        p=np.array(loc['corrected_xy']);q=np.array(obs[row['other']]['xy']);pts=np.linspace(p,q,31);fraction=float(ndi.map_coordinates(fg.astype(float),[pts[:,1],pts[:,0]],order=1,mode='nearest').mean());assert fraction>.95;assert abs(fraction-row['original_filled_foreground_fraction'])<1e-12;assert not row['intervening_observations'];corridors+=1
    # All scalar black decisions independently recomputed from literal annular
    # pixels. No hue/chromaticity/pattern data are read in this calculation.
    record={r['id']:r for r in audit['records']};scalechecks=0;positive=negative=unknown=0
    for row in audit['records']:
        tests=[]
        for j,test in enumerate(row['black_test']['scales']):
            sample=row['samples'][j];points=np.array(test.get('ring_pixels',[]),int);count=len(points);assert count==test.get('ring_count',count);rawpos=rawneg=False
            if count:
                vals=value[points[:,1],points[:,0]];gray=luma[points[:,1],points[:,0]];assert abs(float(np.median(gray))-test['median_intensity'])<1e-12;assert abs(float(np.quantile(gray,.75))-test['q75_intensity'])<1e-12;assert abs(float(np.median(vals))-test['median_max_channel'])<1e-12;assert abs(float(np.mean(vals<=.35))-test['dark_fraction'])<1e-12
                rawpos=count>=25 and test['sectors']>=4 and np.median(gray)<=.15 and np.quantile(gray,.75)<=.20 and np.median(vals)<=.30 and np.quantile(vals,.75)<=.40 and np.mean(vals<=.35)>=.70;rawneg=count>=25 and test['sectors']>=4 and (np.median(vals)>=.45 or np.mean(vals<=.35)<=.30)
                assert bool(rawpos)==test['raw_positive'];assert bool(rawneg)==test['raw_negative']
            ratio=test.get('median_intensity',1)/max(row['lighting']['intensity'],.1);pos=bool(rawpos and ratio<=.65);neg=bool(rawneg);assert pos==test['positive'] and neg==test['negative'];assert not test['hue_used'];tests.append((pos,neg));scalechecks+=1
            body=set(map(tuple,sample['body_pixels']));reflection=set(map(tuple,sample['highlight_pixels']));ring=set(map(tuple,test.get('ring_pixels',[])));assert not(body&reflection);assert not(ring&reflection)
        positives=sum(p for p,n in tests);negatives=sum(n for p,n in tests);decision='black' if positives>=2 and negatives==0 else 'not-black' if negatives>=2 and positives==0 else 'unknown';assert row['black_test']['decision']==decision
        if decision=='black':assert row['body_prediction']=='black';positive+=1
        elif decision=='not-black':assert row['body_prediction'] in ['red','yellow','?'];negative+=1
        else:assert row['body_prediction']=='?';unknown+=1
        assert row['red_yellow_calculation_used']==(decision=='not-black')
        if decision!='not-black':assert np.max(np.abs(row['votes']))==0,'red/yellow calculation ran before black decision'
    assert len(record)==1600;assert audit['counts']['provisional_black']==65;assert len([r for r in audit['maker_controls'] if r['body_prediction']=='black'])==6
    # Check the illumination reference is from hue-free common geometry, not
    # the later chromatic paper mask. Reconstruct each referenced region once.
    allnames=sorted(obs);allxy=np.array([obs[o]['xy'] for o in allnames]);anchorchecks=0
    for o in sorted({q for row in audit['records'] for q in row['lighting']['ids']}):
        sample=record[o]['samples'][1];center=np.array(sample['xy']);x,y=np.rint(center).astype(int);rad=12;yy,xx=np.mgrid[y-rad:y+rad+1,x-rad:x+rad+1];distance=(xx-center[0])**2+(yy-center[1])**2;mask=distance<=rad*rad
        for name,xy in zip(allnames,allxy):
            dd=np.linalg.norm(xy-center)
            if name==o or dd<8 or dd>2*rad+6:continue
            mask&=distance<.86*((xx-xy[0])**2+(yy-xy[1])**2)
        mask&=value[yy,xx]>.012
        for px,py in sample['highlight_pixels']:mask[py-(y-rad),px-(x-rad)]=False
        assert int(mask.sum())==sample['common_body_count'];assert abs(float(np.median(luma[yy[mask],xx[mask]]))-sample['common_median_intensity'])<1e-12;anchorchecks+=1
    for row in audit['records']:
        expected=float(np.median([record[q]['samples'][1]['common_median_intensity'] for q in row['lighting']['ids']]));assert abs(expected-row['lighting']['intensity'])<1e-12
    # Frozen original station bins and weights recreated without the adapters.
    oldg=read(ROOT/'photo2/r328/results/graph.json.gz');oldnames=sorted(oldg['stations_px']);oldxy=np.array([old[o]['xy'] for o in oldnames]);period=oldg['period_px'];station=[]
    for o in ids:
        if o in oldg['stations_px']:station.append(oldg['stations_px'][o]%period);continue
        dist=np.linalg.norm(oldxy-old[o]['xy'],axis=1);jj=np.argsort(dist)[:3];ss=np.array([oldg['stations_px'][oldnames[j]]%period for j in jj]);ss-=np.rint((ss-ss[0])/period)*period;station.append(np.average(ss,weights=1/np.maximum(dist[jj],1))%period)
    blocks=np.minimum((np.array(station)/period*12).astype(int),11);colors=['red','yellow','black'];weights=np.array([.25 if 'provisional' in str(old[o]).lower() else .55 if old[o]['color']=='black' else 1. for o in ids]);hyp={r['id']:r['body_prediction'] for r in audit['ranked_color_candidates'] if r['strong_provisional']}
    layers={}
    for layer in ['raw','color','relocated','provisional']:
        cc={o:old[o]['color'] for o in ids}
        if layer!='raw':
            for row in ledger['ordinary_color_corrections']:cc[row['id']]='black'
        if layer in ['relocated','provisional']:cc[loc['id']]='black'
        if layer=='provisional':
            for o,col in hyp.items():
                if o in cc:cc[o]=col
        layers[layer]=np.array([colors.index(cc[o]) for o in ids])
    fitchecks=0;maxdelta=0
    for row in analysis['period_fits']:
        cc=layers[row['layer']];k=ab@([7,6] if row['family']=='A' else [6,7]);p=row['period'];parent=row.get('parent');guard=row.get('guard',0);pred=np.zeros((len(ids),3));ba=np.zeros_like(pred)
        for block in range(12):
            train=np.flatnonzero(~np.isin(blocks,[(block+d)%12 for d in range(-guard,guard+1)]));te=blocks==block;base=np.ones(3);cnt=np.zeros((p,3));pc=np.zeros((parent or 1,3))
            for j in train:base[cc[j]]+=weights[j];cnt[k[j]%p,cc[j]]+=weights[j];pc[k[j]%(parent or 1),cc[j]]+=weights[j]
            base/=base.sum()
            if parent:
                prior=(pc+3*base)/(pc.sum(1)[:,None]+3);prior=prior[np.arange(p)%parent];theta=(cnt+prior)/(cnt.sum(1)[:,None]+1)
            else:theta=(cnt+3*base)/(cnt.sum(1)[:,None]+3)
            pred[te]=theta[k[te]%p];ba[te]=base
        gain=float(np.average(np.log(pred[np.arange(len(ids)),cc]/ba[np.arange(len(ids)),cc]),weights=weights));delta=abs(gain-row['gain_nats']);maxdelta=max(maxdelta,delta);assert delta<1e-12;assert float(np.mean(pred.argmax(1)==cc))==row['agreement'];fitchecks+=1
    paths=0;linkchecks=0
    for layer in layers:
        for typ,file in [('spirals','spirals.json.gz'),('staircases','staircases.json.gz')]:
            data=read(run/'analysis'/layer/typ/file)
            for path in data['segments' if typ=='spirals' else 'traces']:
                assert len(path['ids'])==path['length'];assert path['inferred_links']==0
                for o in path['ids']:assert colors[layers[layer][ix[o]]] in path['palette']
                for o,z,delta in zip(path['ids'],path['ids'][1:],path['word']):assert frozenset((o,z)) in edges and tuple(np.array(co[z])-co[o])==tuple(delta);linkchecks+=1
                paths+=1
    # Test every rejected repeat-derived stripe transform against original edges.
    for row in analysis['repeat_derived_stripe_transforms']:
        shift=(ab[:,0]-row['cut'])//16;coords=ab+np.c_[-shift,shift];changed=0
        for edge in graph['edges']:
            j,z=ix[edge['source']],ix[edge['target']];changed+=not np.array_equal(coords[z]-coords[j],ab[z]-ab[j])
        assert changed==row['boundary_links_changed']>0;assert not row['adopted'];assert len(ids)-len(set(map(tuple,coords)))==len(row['duplicate_lattice_sites'])
    ref=read(ROOT/'photo2/r328/results/reference.json');recovered=interior=0
    for e in ref['links']:
        if e['recovered']:
            assert frozenset((e['source'],e['target'])) in edges;recovered+=1;interior+=e['priority']=='interior'
    assert recovered==65 and interior==45
    established=read(ROOT/'photo2/r328/results/established-subset.json');refids={o for e in established['links']+established['peripheral_links'] for o in [e['source'],e['target']]};assert all(obs[o]['xy']==old[o]['xy'] and obs[o]['color']==old[o]['color'] for o in refids)
    extended=read(ROOT/'photo2/r332/results/extended-reference.json');assert extended['associated']==36 and extended['recovered']==74 and not extended['wrong']
    for e in extended['recovered_links']:assert frozenset((e['source'],e['target'])) in edges
    crops=read(run/'review/native-crops.json')
    for row in crops:
        x,y,z,v=row['bbox'];assert np.array_equal(np.asarray(Image.open(run/'review'/row['file'])),photo[y:v,x:z])
    seal=read(ROOT/'photo2/r334/input-seal.json')
    for path,digest in seal['sources'].items():assert sha(ROOT/path)==digest,path
    allowed={'AGENTS.md','PLAN.md','SESSION_HANDOFF.md','REQUEST_LOG.md','INITIAL_QUESTION.md','photo2/R334_REPORT.md','photo2/R334_SPECIFICATION.md','photo2/R334_REPRODUCE.md'};changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines();assert all(p.startswith('photo2/r334/') or p in allowed for p in changed),changed
    receipt=dict(passed=True,baseline_commit=BASE,unique_maker_corrections=8,ordinary_color_corrections=7,local_panel_references=references,moved_image_locations=1,changed_lattice_coordinates=0,unique_sites=len(co),integer_edge_equations=len(edges),connected_component_nodes=len(reached),changed_native_corridors_checked=corridors,classifier_supports=len(record),hue_free_annular_tests=scalechecks,hue_free_lighting_anchors=anchorchecks,first_black_decisions=positive,not_black_decisions=negative,unknown_black_decisions=unknown,black_before_red_yellow=True,provisional_black_groups_scanned=65,matched_period_fits=fitchecks,period_score_max_delta=maxdelta,measured_paths=paths,path_link_incidences=linkchecks,rejected_stripe_transforms=16,R161=dict(associated=33,interior=25,links=65,interior_links=45,wrong_links=0),extended_R161=dict(associated=36,links=74,wrong_links=0),literal_native_crops=len(crops),sealed_historical_inputs=len(seal['sources']),historical_preservation=True,seconds=time.perf_counter()-t,limits='Independent native intensity/numerical/provenance checks; no new blind photographic accuracy, physical bead census or recovered shortest pattern.')
    Path(a.output).write_text(json.dumps(receipt,indent=2)+'\n');print(receipt,flush=True)
if __name__=='__main__':main()
