"""Independent native pixels, graph arithmetic, regression and preservation.

Does not call the completion model or use motif/renderer predictions.
"""
import argparse,time,subprocess
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from .common import ROOT,BASE,read,save,sha,STEPS

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='photo2/r332/results');ap.add_argument('--output',default='photo2/r332/verification.json');args=ap.parse_args();start=time.perf_counter();r=read(Path(args.run)/'graph.json.gz');g=read(ROOT/'photo2/r328/results/graph.json.gz');state=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'][0];H=tuple(state['H']);raw={}
    for c in state['coords']:
        v=tuple(c['ab'][d]-c['turn']*H[d] for d in range(2));o=c['observation']
        if o in raw:assert raw[o]==v
        raw[o]=v
    origin=raw['C-1302-0316'];base={o:tuple(v[d]-origin[d] for d in range(2)) for o,v in raw.items()};co={x['id']:tuple(x['ab']) for x in r['coordinates']};obs={x['id']:x for x in r['observations']};old={x['id']:x for x in g['observations']}
    assert all(obs[o]==row for o,row in old.items());assert all(co[o]==ab for o,ab in base.items());assert tuple(r['H'])==H
    def occupancy(v):
        turn=v[0]//H[0];return v[0]-turn*H[0],v[1]-turn*H[1]
    assert len({occupancy(v) for v in co.values()})==len(co)
    ek=lambda e:tuple(sorted((e['source'],e['target'])));edges={ek(e):e for e in r['edges']};assert len(edges)==len(r['edges'])
    for e in g['graph']['edges']:
        now=edges[ek(e)];assert all(now[k]==v for k,v in e.items())
    adjacency=defaultdict(set);equations=0
    for e in r['edges']:
        a,z=e['source'],e['target'];assert a in co and z in co;d=np.array(co[z])-co[a]-e['delta_ab'];assert d[0]%H[0]==0 and d[1]==d[0]//H[0]*H[1];assert tuple(e['delta_ab']) in STEPS;adjacency[a].add(z);adjacency[z].add(a);equations+=1
    reached=set();todo=[next(iter(base))]
    while todo:
        o=todo.pop()
        if o in reached:continue
        reached.add(o);todo+=list(adjacency[o]-reached)
    assert reached==co.keys()
    # Independently re-evaluate final native corridor sampling, including every
    # original and new recorded observation as a potential intervening support.
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo.astype(float)/255.;rr,gg,bb=rgb.transpose(2,0,1);v=rgb.max(2)
    fg=((rr>1.5*bb)&(rr>.13))|(v<.30);fg=ndi.binary_closing(fg,iterations=5);lab,_=ndi.label(~fg);sizes=np.bincount(lab.ravel());small=sizes<600;small[0]=False;fg|=small[lab];lab,_=ndi.label(fg);sizes=np.bincount(lab.ravel());sizes[0]=0;fg=(lab==sizes.argmax()).astype(float)
    names=sorted(obs);xy=np.array([obs[o]['xy'] for o in names]);tree=cKDTree(xy);native_edges=0
    for e in r['edges']:
        a,z=e['source'],e['target'];p,q=np.array(obs[a]['xy']),np.array(obs[z]['xy']);d=q-p;length2=float(d@d);interveners=[]
        for i in tree.query_ball_point((p+q)/2,np.sqrt(length2)/2+7):
            o=names[i]
            if o in [a,z]:continue
            rel=xy[i]-p;t=float(rel@d/length2)
            if .2<t<.8 and np.linalg.norm(rel-t*d)<7:interveners.append(o)
        points=np.linspace(p,q,31);fraction=float(ndi.map_coordinates(fg,[points[:,1],points[:,0]],order=1,mode='nearest').mean())
        assert not interveners,(a,z,interveners);assert fraction>.95,(a,z,fraction)
        if e.get('origin')=='R332':assert abs(fraction-e['foreground_fraction'])<1e-7
        native_edges+=1
    additions=r['accepted_additions'];pixels_checked=0;newids=set();knownids=set();newpixel_rows=[]
    for a in additions:
        o=a['id'];assert tuple(a['cell'])==co[o];native=a['native'];pp=np.array(native['pixels_xy'],int);assert len(pp)==native['pixel_count'];assert len(set(map(tuple,pp)))==len(pp);assert min(np.ptp(pp,axis=0))>=4;assert len(pp)>= (35 if a['color']=='black' else 25)
        vals=rgb[pp[:,1],pp[:,0]];red,green,blue=vals.T;maximum=vals.max(1)
        col=a['color'];mask=(red>1.8*green)&(red>2.5*blue)&(red>.16) if col=='red' else (green>.35*red)&(green>1.8*blue)&(red>.9*green)&(red>.16) if col=='yellow' else (maximum<.36)&(maximum-vals.min(1)<.13)&(maximum>.012)
        assert mask.all(),o;pixels_checked+=len(pp)
        families=set();neighbors=list(adjacency[o])
        for z in neighbors:families.add(edges[tuple(sorted((o,z)))]['family'])
        assert len(families)>=2;assert any(z in adjacency[q] for j,q in enumerate(neighbors) for z in neighbors[j+1:])
        if a['known']:assert o in old;knownids.add(o)
        else:
            assert o not in old;newids.add(o);assert native['appearance']['stable'] and native['appearance']['minimum_vote']>=.6
            nearest=min(np.linalg.norm(np.array(obs[o]['xy'])-np.array(other['xy'])) for name,other in obs.items() if name!=o);assert nearest>=13-1e-10
        newpixel_rows.append(dict(id=o,pixels=len(pp),color=col,body_only=a['body_only']))
        # Independently reconstruct the target-excluded local regression. The
        # exact anchor list is frozen, so later additions cannot improve its fit.
        anchors=a['anchor_ids'];assert o not in anchors;root=np.array(co[anchors[0]]);aa=np.array([co[q] for q in anchors]);hh=np.array(H);aa-=np.rint((aa-root)@hh/(hh@hh)).astype(int)[:,None]*hh
        u=(aa-root)/3.;X=np.column_stack((np.ones(len(u)),u[:,0],u[:,1],u[:,0]**2,u[:,0]*u[:,1],u[:,1]**2));target=np.array(a['xy']);positions=np.array([obs[q]['xy'] for q in anchors]);weights=np.exp(-np.sum((positions-target)**2,axis=1)/10000)
        for iteration in range(3):
            lhs=np.einsum('ij,i,ik->jk',X,weights,X)+np.diag([0,0,0,.35,.35,.35]);rhs=np.einsum('ij,i,ik->jk',X,weights,positions);coeff=np.linalg.lstsq(lhs,rhs,rcond=None)[0];residual=np.linalg.norm(X@coeff-positions,axis=1);weights*=np.minimum(1,6/np.maximum(residual,1e-6))
        uu=(np.array(a['cell'])-root)/3.;pred=np.array([1,*uu,uu[0]**2,uu[0]*uu[1],uu[1]**2])@coeff
        assert np.max(abs(pred-a['prediction']))<1e-8,o;assert abs(np.linalg.norm(pred-target)-a['error'])<1e-8
        assert a['error']<=(8 if col=='black' else 6.5) and a['site_margin']>=5
    summary=r['summary'];assert summary['indexed']==len(co);assert summary['recorded_accepted']==len(obs);assert len(newids)==summary['new_observations'];assert len(knownids)==summary['newly_indexed_known'];assert summary['links']==len(edges);assert summary['new_colors']==dict(Counter(obs[o]['color'] for o in newids))
    # Independently audit conservative fresh-detection accounting against the
    # retained cached support pixels, not merely a newly chosen representative.
    source_run=Path(read(Path(args.run)/'provenance.json')['source_run']);pool=read(source_run/'candidate-pool.json.gz');pooltree=cKDTree([p['xy'] for p in pool]);fresh=0
    for a in additions:
        if a['known']:continue
        distance,_=pooltree.query(a['xy']);has_overlap=False
        if a['body_only']:
            material=set(map(tuple,a['native']['pixels_xy']))
            for j in pooltree.query_ball_point(a['xy'],35):
                old_support={(x,y) for y,lo,hi in pool[j].get('source_support',[]) for x in range(lo,hi+1)}
                if material&old_support:has_overlap=True
        expected=bool(a['body_only'] and distance>=8 and not has_overlap);assert expected==a['genuine_new_native_extraction'];fresh+=expected
    assert fresh==summary['newly_measured_native']==4
    assert all(p['id'] not in co for p in r['provisional_observations']);assert all(p['id'] not in obs and p['id'] not in co for p in r['predictions'])
    # Literal original crops, independent from the image-generating program.
    crops=read(ROOT/'photo2/r332/review/native-crops.json')
    for row in crops:
        box=row['bbox'];crop=np.asarray(Image.open(ROOT/'photo2/r332/review'/row['file']));assert np.array_equal(crop,photo[box[1]:box[3],box[0]:box[2]])
    # Retrospective R161 mapping is frozen; none of its recovered edges/directions
    # can disappear. This is regression evidence, not a new blind score.
    reference=read(ROOT/'photo2/r328/results/reference.json');recovered=interior=0
    for link in reference['links']:
        if not link['recovered']:continue
        a,z=link['source'],link['target'];e=edges[tuple(sorted((a,z)))];delta=np.array(e['delta_ab'])*(1 if e['source']==a else -1);assert np.array_equal(delta,link['delta_ab']);recovered+=1;interior+=link['priority']=='interior'
    assert recovered==65 and interior==45
    # Independent expected labels exposed in R161 are also compared with every
    # accepted edge whose two endpoints have frozen reference associations.
    makercoords={};adj=defaultdict(list)
    for link in reference['links']:
        a,z=link['maker_source'],link['maker_target'];d=np.array(link['delta_ab']);adj[a].append((z,d));adj[z].append((a,-d))
    makercoords[1]=np.zeros(2,int);todo=[1]
    while todo:
        a=todo.pop()
        for z,d in adj[a]:
            if z not in makercoords:makercoords[z]=makercoords[a]+d;todo.append(z)
            else:assert np.array_equal(makercoords[z],makercoords[a]+d)
    mapping={}
    for link in reference['links']:
        for field,makerfield in [('source','maker_source'),('target','maker_target')]:
            if link[field]:mapping[link[field]]=link[makerfield]
    wrong=[]
    for e in r['edges']:
        a,z=mapping.get(e['source']),mapping.get(e['target'])
        if a is not None and z is not None and not np.array_equal(makercoords[z]-makercoords[a],e['delta_ab']):wrong.append(e)
    assert not wrong
    extended=read(Path(args.run)/'extended-reference.json');assert sha(Path(args.run)/'graph.json.gz')==extended['graph_sha256'];assert extended['associated']==36 and extended['recovered']==74 and not extended['wrong']
    newref=0
    for row in extended['recovered_links']:
        e=edges[tuple(sorted((row['source'],row['target'])))];d=np.array(e['delta_ab'])*(1 if e['source']==row['source'] else -1);assert np.array_equal(d,row['delta_ab']);newref+=not row['recovered']
    assert newref==9
    extended_mapping={row['node']:row['maker'] for row in extended['matches'] if row['status']=='unambiguous proximity association'}
    for e in r['edges']:
        a,z=extended_mapping.get(e['source']),extended_mapping.get(e['target'])
        if a is not None and z is not None:assert np.array_equal(makercoords[z]-makercoords[a],e['delta_ab'])
    # No historical source or result can change. Only R332 and project handoffs
    # are authorized writes, even after scoped commits.
    changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines();allowed={'AGENTS.md','PLAN.md','SESSION_HANDOFF.md','REQUEST_LOG.md','INITIAL_QUESTION.md','photo2/R332_REPORT.md','photo2/R332_SPECIFICATION.md','photo2/R332_REPRODUCE.md'}
    assert all(p.startswith('photo2/r332/') or p in allowed for p in changed),changed
    seal=read(ROOT/'photo2/r332/audit/input-seal.json')
    for file,digest in seal['sources'].items():assert sha(ROOT/file)==digest,file
    receipt=dict(passed=True,baseline_commit=BASE,baseline_coordinates_preserved=len(base),baseline_observations_preserved=len(old),baseline_links_preserved=len(g['graph']['edges']),
        indexed=len(co),connected_component_nodes=len(reached),unique_quotient_occupancy=len(co),integer_edge_equations=equations,native_corridors_checked=native_edges,
        additions_checked=len(additions),new_material_pixels=pixels_checked,per_addition_native_pixels=newpixel_rows,new_observations=len(newids),newly_indexed_known=len(knownids),
        exact_original_crops=len(crops),R161=dict(indexed_associations=33,interior_associations=25,recovered_links=recovered,interior_links=interior,wrong_edges=0,frozen_associations=True),
        R161_extended=dict(associated=36,recovered_links=74,new_associations=3,new_recovered_links=9,wrong_edges=0,post_freeze=True,already_exposed=True),
        historical_sources_preserved=True,seconds=time.perf_counter()-start,
        limitations='Numerics and original-pixel support independently checked. New physical bead identities/links are working photographic hypotheses awaiting user review; no new blind photographic truth or all-physical-bead denominator.')
    save(args.output,receipt);print({k:v for k,v in receipt.items() if k!='per_addition_native_pixels'},flush=True)

if __name__=='__main__':main()
