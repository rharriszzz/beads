"""Independent data/asset audit of the presentation; never runs reconstruction."""
import gzip, hashlib, json, re
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent

def read(p):
    if str(p).endswith('.gz'):
        with gzip.open(p,'rt') as f:return json.load(f)
    return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coordinates(s):
    coords={}
    for r in s['coords']:
        xy=tuple(r['ab'][i]-r['turn']*s['H'][i] for i in range(2))
        if r['observation'] in coords:assert coords[r['observation']]==xy
        coords[r['observation']]=xy
    zero=coords['C-1302-0316']
    return {k:tuple(v[i]-zero[i] for i in range(2)) for k,v in coords.items()}
def slug(s):return re.sub(r'[^\w\- ]','',s.lower()).replace(' ','-')
def main():
    protected=read(HERE/'science-before.json')
    assert all(digest(ROOT/p)==h for p,h in protected.items())
    graph=read(ROOT/'photo2/r328/results/graph.json.gz');obs={o['id']:o for o in graph['observations']}
    states=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states']
    prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz')
    novel=read(ROOT/'photo2/r329/results/novel-windings.json.gz')
    states={'working':states[0],'closest':states[1],'lower':states[5],'early':next(a['state'] for a in novel['alternatives'] if a['state']['H']==[214,176])}
    allcoords={k:coordinates(s) for k,s in states.items()};edges={}
    for name,s in states.items():
        edges[name]=set()
        for path in s['path']:
            if path.get('skipped'):continue
            for a,b,d in prep['patches'][path['window']][path['patch']]['edges']:
                edges[name].add((a,b,tuple(d)))
                edges[name].add((b,a,tuple(-v for v in d)))
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    figures=read(HERE/'figure-data.json');labelcount=edgecount=0
    for fig in figures:
        assert Image.open(HERE/'images'/fig['figure']).size in [(1600,1120),(1800,1380)]
        if 'state' not in fig:continue
        co=allcoords[fig['state']];bbox=fig['crop_xyxy'];ids={r['id'] for r in fig['labels']}
        assert hashlib.sha256(photo.crop(bbox).tobytes()).hexdigest()==fig['raw_crop_rgb_sha256']
        for r in fig['labels']:
            assert r['xy']==obs[r['id']]['xy']
            x,y=r['xy'];assert bbox[0]<=x<bbox[2] and bbox[1]<=y<bbox[3]
            a,b=co[r['id']];assert r['relative_index']==(7*a+6*b if fig['family']=='A' else 6*a+7*b)
            labelcount+=1
        for e in fig['edges']:
            a,b=e['source'],e['target'];d=tuple(e['delta'])
            assert a in ids and b in ids
            assert tuple(co[b][j]-co[a][j] for j in range(2))==d
            assert (a,b,d) in edges[fig['state']]
            edgecount+=1
        # Each diagnostic has a connected three-feature sequence of EACH primitive.
        if not fig['figure'].startswith(('a-','b-')):
            for d in [(1,0),(0,1)]:
                ee=[(e['source'],e['target']) for e in fig['edges'] if tuple(e['delta'])==d]
                assert any(b==c for a,b in ee for c,z in ee),(fig['figure'],d)
    for a,b in [('g-early-working.png','g-early-alternative.png'),('h-lower-working.png','h-lower-alternative.png')]:
        fa=next(f for f in figures if f['figure']==a);fb=next(f for f in figures if f['figure']==b)
        assert fa['crop_xyxy']==fb['crop_xyxy']
        assert [(r['number'],r['id'],r['xy']) for r in fa['labels']]==[(r['number'],r['id'],r['xy']) for r in fb['labels']]
    # Independent model ownership check: the exact original three support pixels.
    import numpy as np
    model=next(f for f in figures if f.get('model'))['model']
    pos=read(ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz')['positions']
    raster=np.load(ROOT/model['raster'])
    owner={tuple(xy):int(o) for xy,o in zip(raster['xy'],raster['owner'])}
    pixels=next(o['pixels_xy'] for o in read(ROOT/'photo2/r324/results/observation-pixels.json') if o['id']=='K-1398-0248')
    assert pixels==model['support_pixels'] and len(pixels)==3
    saved_model=read(ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz')
    support=next(r for r in saved_model['support'] if r['id']=='K-1398-0248')
    assert support['pixels']==3 and support['unknown']==0
    assert support['owners']==[{'fraction':1.0,'index':-27}]
    assert support['modal_index']==-27 and support['modal_fraction']==1.0
    assert (raster['owner']==pos['indices'].index(-33)).any()
    assert (raster['owner']==pos['indices'].index(-27)).any()
    ledger=read(ROOT/'photo2/r329/results/frozen-ledger.json.gz')
    record=next(m for m in ledger['models'] if m['label']=='R321-geometry-best')['first_forward']
    first=record['first'];last=record['last_agreement']
    assert (first['id'],first['k'],first['model_address'],first['modal_address'])==('K-1398-0248',31,-33,-27)
    assert (last['id'],last['k'],last['model_address'],last['modal_address'])==('C-1391-0312',26,-38,-38)
    assert first['projected_center']==pos['projected'][pos['indices'].index(-33)]
    assert first['reflection_error_px'] is None
    assert -64+31==-33 and -64+26==-38
    # Verify exact original crops, no annotation or resampling.
    raw={'inward':(1638,1484,1800,1624),'reference':(1200,242,1360,355),'model':(1318,224,1468,338),'early':(1527,225,1698,342),'lower':(1090,2855,1220,2970)}
    for name,bbox in raw.items():assert Image.open(HERE/'images'/f'{name}-original.png').tobytes()==photo.crop(bbox).tobytes()
    # Local Markdown links, GitHub-style anchors, and named IDs are visible in figures.
    links=0;visible={r['id'] for f in figures for r in f.get('labels',[])}
    for md in [HERE/'READING_THE_PHOTOGRAPH.md',HERE.parent/'ILLUSTRATED_GUIDE.md']:
        s=md.read_text()
        for dest in re.findall(r'\]\(([^)]+)\)',s):
            if '://' in dest:continue
            filename,_,anchor=dest.partition('#');target=(md.parent/filename).resolve() if filename else md
            assert target.is_file() or target==HERE/'verification.json',dest
            if anchor:
                headings=[slug(h) for h in re.findall(r'^#+ (.+)$',target.read_text(),re.M)]
                assert anchor in headings,(dest,headings)
            links+=1
        mentioned=set(re.findall(r'\b(?:C|K|MAT25-K|E5|P5|RF70T-K|NEW)-\d{3,4}-\d{3,4}\b',s))
        assert mentioned<=visible,mentioned-visible
    source_names=['beads-photo-2.jpg','photo2/r328/results/graph.json.gz','photo2/r328/development/final256/search.json.gz','photo2/r328/development/final256/prepared.json.gz','photo2/r329/results/novel-windings.json.gz','photo2/r324/results/R321-geometry-best-frozen.json.gz','photo2/r324/results/R321-geometry-best-raster.npz','photo2/r324/results/observation-pixels.json','photo2/R329_REPORT.md']
    result={'passed':True,'protected_files_unchanged':len(protected),'annotated_figures':len(figures),'label_occurrences_checked':labelcount,'selected_edges_checked':edgecount,'exact_raw_crops':len(raw),'markdown_links_checked':links,'every_diagnostic_has_both_three_feature_primitive_sequences':True,'paired_early_lower_labels_fixed':True,'model_three_pixels_owner_address':-27,'source_sha256':{p:digest(ROOT/p) for p in source_names},'assets_sha256':{p.name:digest(p) for p in sorted((HERE/'images').glob('*.png'))},'scope':'Presentation audit only; no scientific inference or reconstruction was run.'}
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if not isinstance(v,dict)},indent=2))
if __name__=='__main__':main()
