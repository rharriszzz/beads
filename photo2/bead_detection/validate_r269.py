"""Preservation, native-pixel replay, graph certificates and synthetic failure views."""
from dataclasses import replace
from collections import Counter
import csv,gzip,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from .audit_r267 import ROOT,save,photo
from .experiment_r269 import OUT,PRIOR,sha
from .search_r269 import Neighborhood,POLICIES,Policy
from .climb_r268 import background,score_sums,audit as prefix_audit,VARIANTS,Surface
from .synthetic_r268 import start_points
from .review_r269 import font,path_draw,BG,WHITE,CYAN,ORANGE

def local_path(path,origin):return [dict(p,x=p['x']-int(origin[0]),y=p['y']-int(origin[1])) for p in path]

def figure(key,r,images,truths):
    rgb=images[r['scene']];truth=truths[r['scene']];h,w=truth.shape;scale=6
    im=Image.new('RGB',(w*scale*3,h*scale+88),BG);d=ImageDraw.Draw(im)
    for col,title in enumerate(['Original synthetic image',f"mean{r['window']} / radius{r['radius']} / {r['policy']}",'Withheld identity truth']):
        base=rgb if col<2 else np.array([[35,40,50],[80,190,240],[255,180,70]],np.uint8)[truth]
        im.paste(Image.fromarray(base).resize((w*scale,h*scale),Image.Resampling.NEAREST),(col*w*scale,88));d.text((col*w*scale+9,9),title,fill=WHITE,font=font(15))
        if col==1:
            proj=lambda x,y:(col*w*scale+(x+.5)*scale,88+(y+.5)*scale)
            path_draw(im,proj,r['prefix']['steps'],ORANGE);path_draw(im,proj,r['path'],CYAN)
    d.text((10,39),f"{r['scene']} | truth body {r['truth_start']} -> {r['truth_end']} | yellow R268 / cyan broader path",fill=WHITE,font=font(16))
    d.text((10,63),'Truth evaluated afterwards; never used for foreground eligibility, search or ranking.',fill=WHITE,font=font(14))
    im.save(OUT/f'synthetic-{key}.png')

def main():
    for name,digest in json.load(open(OUT/'input-hashes.json')).items():assert sha(ROOT/name)==digest,name
    assert json.load(open(OUT/'starts.json'))==json.load(open(PRIOR/'starts.json'))
    rgb=photo();datasets={};allc=json.load(open(OUT/'all-competing-points.json'))
    for crop in allc:
        data=np.load(OUT/f'{crop}-score-images.npz');origin=data['origin'];x0,y0=origin;h,w=data['raw_v'].shape
        assert np.array_equal(data['rgb'],rgb[y0:y0+h,x0:x0+w]);assert np.array_equal(data['raw_v'],data['rgb'].max(axis=2))
        for n in (5,7,9):
            exact=score_sums(data['raw_v'],n);r=n//2
            np.testing.assert_array_equal(exact[r:-r,r:-r],data[f'sum{n}'][r:-r,r:-r])
        old={tuple((int(r['x']),int(r['y']))) for r in csv.DictReader(open(ROOT/f'photo2/review/r267/{crop}-all-maximum-pixels.csv'))}
        new={(c['x'],c['y']) for c in allc[crop] if 'original-raw-maximum' in c['types']};assert old==new
        datasets[crop]=data
        for c in allc[crop]:
            x,y=c['x']-x0,c['y']-y0;assert c['raw_v']==data['raw_v'][y,x]
            for n in (5,7,9):assert c[f'mean{n}']==data[f'sum{n}'][y,x]/n**2
    counts=Counter();current=None
    with gzip.open(OUT/'photo-search-traces.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);key=(r['crop'],r['window'],r['start_id']);data=datasets[r['crop']];origin=data['origin'];n=r['window'];policy=POLICIES[r['policy']]
        if key!=current:
            g=Neighborhood(data['raw_v'],data['hsv'],data['background_stop_codes'],data[f'sum{n}'],n,np.array(r['anchor'])-origin,reference_raw=r['raw_reference']);current=key
        path=local_path(r['path'],origin);counts['photo_moves']+=g.audit(path,r['radius'],policy);counts['photo_searches']+=1
        q=g.search(r['radius'],policy);assert (g.xy[q['end']]+origin).tolist()==r['endpoint'];assert r['end_mean']==g.mean[q['end']]
        assert [g.x0+int(origin[0]),g.y0+int(origin[1])]==r['graph_origin'];assert list(g.shape)==r['graph_shape']
        tree=r['reachable_tree'];assert len(tree)==len(q['order'])
        for (x,y,pred),i in zip(tree,q['order']):
            assert [x,y]==(g.xy[i]+origin).tolist() and pred==q['pred'][i];counts['reachable_tree_nodes']+=1
        assert len(r['blocked_frontier'])==len(q['frontier'])
        for a,b in zip(r['blocked_frontier'],q['frontier']):
            assert a['from_xy']==(np.array(b['from_xy'])+origin).tolist() and a['to_xy']==(np.array(b['to_xy'])+origin).tolist()
            assert a['reasons']==b['reasons'] and a['raw_capacity']==b['raw_capacity'] and a['mean_capacity']==b['mean_capacity'];counts['blocked_frontier_edges']+=1
    # Prove each claimed optimal bottleneck by exhibiting its route and checking
    # there is NO route at a strictly higher threshold (independent flood check).
    focus=json.load(open(OUT/'focus-results.json'));refs={(r['crop'],r['case'],r['window']):r for r in focus if r['policy']=='raw24-mean2'}
    with gzip.open(OUT/'focus-alternative-paths.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);d=datasets[r['crop']];o=d['origin'];ref=refs[r['crop'],r['case'],r['window']];n=r['window']
        g=Neighborhood(d['raw_v'],d['hsv'],d['background_stop_codes'],d[f'sum{n}'],n,np.array(ref['anchor'])-o,reference_raw=ref['raw_reference']);target=g.index((r['x']-o[0],r['y']-o[1]));policy=POLICIES['raw24-mean2']
        routes=[('widest_raw_with_color_only','best_raw_saddle','raw',Policy(256,256)),('widest_mean_with_raw_and_color','best_mean_saddle_given_raw_floor','mean',Policy(24,256)),('widest_raw_with_mean_and_color','best_raw_saddle_given_mean_floor','raw',Policy(256,2))]
        for pathkey,capkey,metric,p in routes:
            path=local_path(r[pathkey],o);cap=r[capkey];spatial,bits=g.edge_masks(16,p);keep=spatial&(bits==0)
            if cap<0:
                assert not path;assert not g.search(16,p)['reachable'][target]
            else:
                g.audit(path,16,p);assert path[-1]['x']==r['x']-o[0] and path[-1]['y']==r['y']-o[1]
                capacity=g.rawcap if metric=='raw' else g.meancap
                # Include source/target and both diagonal corners in bottleneck.
                edge_lookup={(int(a),int(b)):i for i,(a,b) in enumerate(zip(g.a,g.b))}
                vals=[g.v[g.start] if metric=='raw' else g.mean[g.start]]
                for a,b in zip(path,path[1:]):vals.append(capacity[edge_lookup[g.index((a['x'],a['y'])),g.index((b['x'],b['y']))]])
                assert min(vals)==cap
                keep &= capacity>cap
                if (g.v[g.start] if metric=='raw' else g.mean[g.start])>cap:
                    graph=csr_matrix((np.ones(int(keep.sum()),np.uint8),(g.a[keep],g.b[keep])),shape=(len(g.v),)*2)
                    seen=breadth_first_order(graph,g.start,directed=True,return_predecessors=False)
                    assert target not in seen
            counts['alternative_bottleneck_certificates']+=1
    print('photographic and alternative-path checks passed',dict(counts),flush=True)
    images=np.load(PRIOR/'synthetic-inputs.npz');truths=np.load(PRIOR/'synthetic-truth.npz');current=None;failures={};savedinv={r['scene']:r for r in json.load(open(OUT/'synthetic-starts.json'))}
    with gzip.open(OUT/'synthetic-search-traces.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);key=(r['scene'],r['window'],r['start_index']);n=r['window']
        if key!=current:
            if current is None or r['scene']!=current[0]:
                im=images[r['scene']];v=im.max(axis=2);hsv,paper,_=background(im);truth=truths[r['scene']];points=start_points(v);eligible=[p for p in points if paper[p[1],p[0]]==0]
                inv=savedinv[r['scene']]['raw_starts'];assert [(p['x'],p['y']) for p in inv]==points
                assert [(p['x'],p['y']) for p in inv if p['eligible']]==eligible
            s=score_sums(v,n);g=Neighborhood(v,hsv,paper,s,n,r['anchor'],reference_raw=r['raw_reference']);current=key
            assert list(eligible[r['start_index']])==r['original_start']
            for a in r['prefix']['steps']:assert int(s[a['y'],a['x']])==a['score_sum']
            fake=type('Fields',(),dict(value=v,hsv=hsv,paper=paper))();prefix_audit(fake,r['prefix'],VARIANTS['guarded12'])
        counts['synthetic_moves']+=g.audit(r['path'],r['radius'],POLICIES[r['policy']]);counts['synthetic_searches']+=1
        q=g.search(r['radius'],POLICIES[r['policy']]);assert g.xy[q['end']].tolist()==r['endpoint']
        x,y=r['original_start'];ex,ey=r['endpoint'];assert r['truth_start']==int(truth[y,x]) and r['truth_end']==int(truth[ey,ex])
        cross=r['truth_start']>0 and r['truth_end'] not in (0,r['truth_start']);bg=r['truth_start']>0 and r['truth_end']==0
        assert cross==r['endpoint_cross'] and bg==r['body_to_background']
        if r['window']==7 and r['radius']==16:
            label='unobservable' if r['scene'].startswith('no-visible') and cross else 'cross-body' if cross else 'background' if bg else None
            if label:
                k=label+'-'+r['policy']
                if k not in failures:failures[k]=dict(r,blocked_frontier=q['frontier'])
    save(OUT/'synthetic-failures.json',failures)
    for key in ('cross-body-radius-only','background-raw24-mean2','unobservable-raw24-mean2'):figure(key,failures[key],images,truths)
    tests=(OUT/'tests.log').read_text();assert 'Ran 13 tests' in tests and tests.rstrip().endswith('OK')
    save(OUT/'validation.json',dict(status='pass',tests=13,**counts,all_original_maxima_preserved=True,all_previous_input_hashes_unchanged=True,
          all_native_score_arrays_exact=True,all_selected_paths_and_reachable_trees_replayed=True,all_frontier_reasons_replayed=True,
          no_route_with_better_claimed_bottleneck=True,synthetic_truth_used_only_after_image_eligibility_and_search=True,production_detector_changed=False))
    readme=OUT/'README.md';text=readme.read_text();marker='\nSynthetic failure review:'
    if marker in text:text=text[:text.index(marker)]
    text+=marker+' [unrestricted cross-body](synthetic-cross-body-radius-only.png), [guarded background exit](synthetic-background-raw24-mean2.png), [unobservable boundary](synthetic-unobservable-raw24-mean2.png).\n';readme.write_text(text)
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='artifact-hashes.json')+sorted((ROOT/'photo2/bead_detection').glob('*r269.py'))
    report=ROOT/'photo2/BROADER_PEAK_SEARCH_R269.md'
    if report.exists():files.append(report)
    save(OUT/'artifact-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in files})
    print((OUT/'validation.json').read_text(),flush=True)
if __name__=='__main__':main()
