"""Native score/guard verification, exact baseline replay, and synthetic witnesses."""
from collections import Counter
import csv,gzip,json,time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from PIL import Image,ImageDraw
from .audit_r267 import ROOT,photo,save
from .experiment_r269 import sha
from .experiment_r270 import OUT,PREV,deadline
from .brightness_r270 import MEASURES,SCALE,Climber,Search,quantized,paired_scores,maxima_inventory,color_managed_photo
from .search_r269 import POLICIES,Policy
from .review_r270 import panel,draw_path,join,font,WHITE,BG


def local(path,o):return [dict(p,x=p['x']-int(o[0]),y=p['y']-int(o[1])) for p in path]

def check_path(g,path,radius,policy,lookup):
    assert [path[0]['x'],path[0]['y']]==list(g.anchor);rf,mf=g.floors(policy)
    for p in path:
        i=g.index((p['x'],p['y']));assert i is not None and g.dist2[i]<=radius**2;assert p['sum_q']==int(g.sums[i]) and p['raw']==g.v[i] and p['mean']==g.mean[i]
    for a,b in zip(path,path[1:]):
        ia=g.index((a['x'],a['y']));ib=g.index((b['x'],b['y']));e=lookup[ia,ib]
        for i in (g.a[e],g.b[e],g.c[e],g.d[e]):assert g.dist2[i]<=radius**2 and g.sums[i]>=0
        assert not policy.color or g.colorbits[e]==0
        assert (g.vcap[e] if g.fixed_v else g.rawcap[e])>=rf-1e-9
        assert g.sumcap[e]>=mf*SCALE*g.side**2-.25
    return len(path)-1

def graph_from(data,record,synthetic=False):
    m=record['measure'];n=record['window'];o=np.zeros(2,int) if synthetic else data['origin'];anchor=(np.array(record['anchor'])-o).tolist();common=record['policy']=='common-V-raw24-mean2'
    ref=record['raw_reference'] if synthetic else record['anchor_raw'];vref=record['v_reference'] if synthetic else record['raw_floor']+24 if common else None
    g=Search(data['q_'+m],data['hsv'],data['background_stop_codes'],data[f'sum_{m}_{n}'],n,anchor,m,reference=ref,v_reference=vref,fixed_v=common)
    return g,{(int(a),int(b)):i for i,(a,b) in enumerate(zip(g.a,g.b))}

def failure_figure(key,r,images,truths):
    image=images[r['scene']];truth=truths[r['scene']];h,w=truth.shape;scale=6;im=Image.new('RGB',(w*scale*3,h*scale+82),BG);d=ImageDraw.Draw(im)
    for col,title in enumerate(['Original synthetic image',f"{r['measure']} mean{r['window']}, radius16, {r['policy']}",'Withheld identity truth']):
        base=image if col<2 else np.array([[35,40,50],[80,190,240],[255,180,70]],np.uint8)[truth];im.paste(Image.fromarray(base).resize((w*scale,h*scale),Image.Resampling.NEAREST),(col*w*scale,82));d.text((col*w*scale+8,8),title,fill=WHITE,font=font(13))
        if col==1:draw_path(im,lambda x,y:(col*w*scale+(x+.5)*scale,82+(y+.5)*scale),r['prefix']['steps']+r['path'][1:],'#00eaff')
    d.text((8,37),f"{r['scene']} | truth body {r['truth_start']} -> {r['truth_end']}; truth enters evaluation only",fill=WHITE,font=font(15));im.save(OUT/f'synthetic-{key}.png')

def main():
    started=time.time();deadline();counts=Counter();rgb=photo();srgb,profile=color_managed_photo()
    for name,digest in json.load(open(OUT/'input-hashes.json')).items():assert sha(ROOT/name)==digest,name
    save(OUT/'color-profile.json',profile)
    datasets={};cases=json.load(open(OUT/'legacy-starts.json'));candidate=json.load(open(OUT/'candidate-points.json'));oldrows={}
    for crop in cases:
        d=dict(np.load(OUT/f'{crop}-fields.npz'));datasets[crop]=d;o=d['origin'];ox,oy=o;h,w=d['rgb'].shape[:2]
        np.testing.assert_array_equal(d['rgb'],rgb[oy:oy+h,ox:ox+w]);np.testing.assert_array_equal(d['srgb'],srgb[oy:oy+h,ox:ox+w]);expected=quantized(d['rgb'],d['srgb']);float_scores=paired_scores(d['rgb'],d['srgb'])
        old=np.load(PREV/f'{crop}-score-images.npz');bx,by=old['origin'];bh,bw=old['raw_v'].shape
        np.testing.assert_array_equal(d['background_stop_codes'][by-oy:by-oy+bh,bx-ox:bx-ox+bw],old['background_stop_codes'])
        for m in MEASURES:
            np.testing.assert_array_equal(d['q_'+m],expected[m]);np.testing.assert_array_equal(d['raw_'+m],float_scores[m])
            for n in (5,7,9):
                c=Climber(d['q_'+m],d['hsv'],d['background_stop_codes'],n,m);np.testing.assert_array_equal(c.sumq,d[f'sum_{m}_{n}'])
            box=(np.array(cases[crop]['box'])-[ox,oy,ox,oy]).tolist()
            for kind,arr in [('raw',d['q_'+m])]+[(f'mean{n}',d[f'sum_{m}_{n}']) for n in (5,7,9)]:
                pts,_=maxima_inventory(arr,box);actual={(x+ox,y+oy) for x,y,_ in pts};saved={(p['x'],p['y']) for p in candidate[crop] if m+'-'+kind in p['types']};assert actual==saved;counts['maximum_pixels_preserved']+=len(saved)
        for r in csv.DictReader(open(ROOT/f'photo2/review/r267/{crop}-all-maximum-pixels.csv')):
            xy=int(r['x']),int(r['y']);p=next(p for p in candidate[crop] if (p['x'],p['y'])==xy);assert 'V-raw' in p['types']
            if not p['V_prominence_censored']:assert p['V_prominence']==int(r['prominence_dn']);counts['uncensored_v_prominences_exact']+=1
        oldrows[crop]={(r['start_id'],int(r['window']),int(r['radius']),r['policy']):r for r in csv.DictReader(open(PREV/f'{crop}-search-endpoints.csv'))}
    # Every strict prefix, including diagonal routes and its exact score sum.
    current=None
    with gzip.open(OUT/'photo-climbs.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);d=datasets[r['crop']];o=d['origin'];key=r['crop'],r['measure'],r['window']
        if key!=current:c=Climber(d['q_'+r['measure']],d['hsv'],d['background_stop_codes'],r['window'],r['measure']);current=key
        t=dict(r['trace'],start=(np.array(r['trace']['start'])-o).tolist(),endpoint=(np.array(r['trace']['endpoint'])-o).tolist(),steps=local(r['trace']['steps'],o))
        counts['photo_climb_moves']+=c.audit(t,r['mode']=='guarded12');counts['photo_climbs']+=1
    print('photo fields and climbs checked',dict(counts),flush=True)
    current=None;graphs={}
    with gzip.open(OUT/'photo-searches.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);d=datasets[r['crop']];o=d['origin'];key=r['crop'],r['measure'],r['window'],r['start_id']
        if key!=current:graphs={};current=key
        common=r['policy']=='common-V-raw24-mean2'
        if common not in graphs:graphs[common]=graph_from(d,r)
        g,lookup=graphs[common];policy=POLICIES['raw24-mean2' if common else r['policy']];path=local(r['path'],o)
        counts['photo_search_moves']+=check_path(g,path,r['radius'],policy,lookup);counts['photo_searches']+=1
        assert r['endpoint']==[path[-1]['x']+int(o[0]),path[-1]['y']+int(o[1])]
        if r['measure']=='V' and r['legacy'] and not common:
            old=oldrows[r['crop']][r['start_id'],r['window'],r['radius'],r['policy']];assert r['endpoint']==json.loads(old['endpoint']) and r['end_mean']==float(old['end_mean']);counts['baseline_searches_exact']+=1
        if 'reachable_tree' in r:
            q=g.search(r['radius'],policy);assert r['endpoint']==(g.xy[q['end']]+o).tolist();assert len(r['reachable_tree'])==len(q['order'])
            for saved,i in zip(r['reachable_tree'],q['order']):assert saved==[int(g.xy[i,0]+o[0]),int(g.xy[i,1]+o[1]),int(q['pred'][i])]
            assert len(r['blocked_frontier'])==len(q['frontier'])
            for a,b in zip(r['blocked_frontier'],q['frontier']):assert a['reasons']==b['reasons'] and a['from_xy']==(np.array(b['from_xy'])+o).tolist() and a['to_xy']==(np.array(b['to_xy'])+o).tolist()
            counts['named_search_graphs_replayed']+=1;counts['named_reachable_nodes']+=len(q['order']);counts['named_blocked_edges']+=len(q['frontier'])
    print('photo searches checked',dict(counts),flush=True);deadline()
    # Independent threshold flood certificates for the saved alternative bottlenecks.
    focus=json.load(open(OUT/'focus-results.json'));refs={(r['crop'],r['measure'],r['case'],r['window']):r for r in focus if r['policy']=='raw24-mean2'};current=None
    with gzip.open(OUT/'alternative-paths.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);key=r['crop'],r['measure'],r['case'],r['window'];d=datasets[r['crop']];o=d['origin'];ref=refs[key]
        if key!=current:g,lookup=graph_from(d,ref);current=key
        target=g.index((r['x']-o[0],r['y']-o[1]))
        for pk,ck,metric,policy in [('widest_raw','raw_saddle','raw',Policy(256,256)),('widest_mean','mean_saddle','mean',Policy(24,256))]:
            path=local(r[pk],o);cap=r[ck]
            if cap<0:assert not path;assert not g.search(16,policy)['reachable'][target]
            else:
                check_path(g,path,16,policy,lookup);values=[g.v[g.start] if metric=='raw' else g.mean[g.start]];capacity=g.rawcap if metric=='raw' else g.meancap
                for a,b in zip(path,path[1:]):values.append(capacity[lookup[g.index((a['x'],a['y'])),g.index((b['x'],b['y']))]])
                assert min(values)==cap
                spatial,bits=g.edge_masks(16,policy);keep=spatial&(bits==0)&(capacity>cap)
                if (g.v[g.start] if metric=='raw' else g.mean[g.start])>cap:
                    graph=csr_matrix((np.ones(int(keep.sum()),np.uint8),(g.a[keep],g.b[keep])),shape=(len(g.v),)*2);order=breadth_first_order(graph,g.start,directed=True,return_predecessors=False);assert target not in order
            counts['optimal_bottleneck_certificates']+=1
    print('alternative certificates checked',counts['optimal_bottleneck_certificates'],flush=True)
    # Validate synthetic prefixes, per-score maximum masks, eligibility and every path.
    images=np.load(OUT/'synthetic-inputs.npz');truths=np.load(OUT/'synthetic-truth.npz');current=None;scene=None;vprefix_cross={}
    from .climb_r268 import background
    with gzip.open(OUT/'synthetic-climbs.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);key=r['scene'],r['measure'],r['window']
        if key!=current:
            if r['scene']!=scene:
                im=images[r['scene']];hs,pp,_=background(im);fields=dict(np.load(OUT/'synthetic-fields'/f"{r['scene']}.npz"));expected=quantized(im)
                for m in MEASURES:
                    np.testing.assert_array_equal(fields['q_'+m],expected[m]);np.testing.assert_array_equal(fields['background'],pp)
                scene=r['scene'];truth=truths[scene]
            c=Climber(fields['q_'+r['measure']],hs,pp,r['window'],r['measure']);current=key
        counts['synthetic_climb_moves']+=c.audit(r['trace'],r['mode']=='guarded12');counts['synthetic_climbs']+=1
        if r['measure']=='V' and r['mode']=='guarded12':
            body=r['truth_start'];vprefix_cross[r['scene'],r['window'],r['start_index']]=body>0 and any(truth[p['y'],p['x']] not in (0,body) for p in r['trace']['steps'])
    print('synthetic climbs checked',dict(counts),flush=True);deadline();scene=None;current=None;graphs={}
    with gzip.open(OUT/'synthetic-searches.jsonl.gz','rt') as f:
      for line in f:
        r=json.loads(line);key=r['scene'],r['measure'],r['window'],r['start_index']
        if r['scene']!=scene:
            im=images[r['scene']];hs,pp,_=background(im);d=dict(np.load(OUT/'synthetic-fields'/f"{r['scene']}.npz"));d['hsv']=hs;d['background_stop_codes']=pp;truth=truths[r['scene']];scene=r['scene']
        if key!=current:graphs={};current=key
        common=r['policy']=='common-V-raw24-mean2'
        if common not in graphs:graphs[common]=graph_from(d,r,True)
        g,lookup=graphs[common];policy=POLICIES['raw24-mean2' if common else r['policy']]
        counts['synthetic_search_moves']+=check_path(g,r['path'],r['radius'],policy,lookup);counts['synthetic_searches']+=1
        x,y=r['start'];ex,ey=r['endpoint'];assert pp[y,x]==0;assert r['truth_start']==int(truth[y,x]) and r['truth_end']==int(truth[ey,ex])
        assert r['endpoint_cross']==(r['truth_start']>0 and r['truth_end'] not in (0,r['truth_start']))
        if common:assert r['prefix_cross']==vprefix_cross[r['scene'],r['window'],r['start_index']]
    failures=json.load(open(OUT/'synthetic-failures.json'))
    for m in MEASURES:
        for kind in ('background','invisible-boundary','cross-body'):
            key=m+'-raw24-mean2-'+kind
            if key in failures:failure_figure(key,failures[key],images,truths)
        key=m+'-radius-only-cross-body'
        if key in failures:failure_figure(key,failures[key],images,truths)
    # Colored-highlight photographic-style comparison with withheld truth.
    name='colored-highlight-1-gap0';rgb=images[name];truth=truths[name];hs,pp,_=background(rgb);q=quantized(rgb);chosen=[]
    inv=next(r for r in json.load(open(OUT/'synthetic-starts.json')) if r['scene']==name)
    for p in inv['points']:
        if p['eligible']:chosen.append((p['x'],p['y']))
    cells=[]
    for m in ('original',)+MEASURES:
        im,project=panel(rgb,[0,0,rgb.shape[1],rgb.shape[0]],5,66);dr=ImageDraw.Draw(im);dr.text((8,8),name+' | '+m,fill=WHITE,font=font(14))
        if m!='original':
            c=Climber(q[m],hs,pp,7,m)
            for xy in chosen:
                t=c.climb(xy);g=Search(q[m],hs,pp,c.sumq,7,t['endpoint'],m,t['steps'][-1]['running_peak']);rr=g.search(16,POLICIES['raw24-mean2']);draw_path(im,project,t['steps']+g.path(rr['pred'],rr['end'])[1:],'#00eaff')
        cells.append(im)
    join(cells,OUT/'synthetic-colored-highlight-comparison.png')
    tests=(OUT/'tests.log').read_text();assert 'Ran 18 tests' in tests and tests.rstrip().endswith('OK');deadline();budget=json.load(open(OUT/'budget.json'))
    save(OUT/'validation.json',dict(status='pass',tests=18,**counts,elapsed_validation_seconds=time.time()-started,shared_budget_elapsed_seconds=time.time()-budget['start_epoch'],compute_limit_seconds=1800,
        icc_conversion_verified=True,all_previous_input_hashes_unchanged=True,all_native_score_sums_exact=True,all_independent_maxima_preserved=True,all_selected_moves_and_guards_checked=True,
        all_named_graphs_and_frontiers_replayed=True,production_detector_changed=False))
    readme=OUT/'README.md';s=readme.read_text();marker='\nSynthetic review:'
    if marker in s:s=s[:s.index(marker)]
    s+=marker+' [colored highlights](synthetic-colored-highlight-comparison.png), [luminance background exit](synthetic-Y-raw24-mean2-background.png), [invisible boundary](synthetic-Y-raw24-mean2-invisible-boundary.png).\n';readme.write_text(s)
    print((OUT/'validation.json').read_text(),flush=True)
if __name__=='__main__':main()
