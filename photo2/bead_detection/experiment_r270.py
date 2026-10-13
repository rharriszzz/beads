"""R270 paired photograph experiment; preserved old starts plus all new maxima."""
from collections import Counter,defaultdict
import csv,gzip,json,time
import numpy as np
from .audit_r267 import ROOT,photo,save,csvsave
from .climb_r268 import background
from .search_r269 import POLICIES,Policy
from .experiment_r269 import FOCUS,RADII,writegz,sha,shift_path,shift_xy,direct_path,direct_failures
from .brightness_r270 import MEASURES,SCALE,Climber,Search,quantized,scores,maxima_inventory,prominences,neutral,paired_scores,color_managed_photo

OUT=ROOT/'photo2/review/r270';PREV=ROOT/'photo2/review/r269'

def deadline():
    b=json.load(open(OUT/'budget.json'));assert time.time()<b['deadline_epoch'],'R270 shared 30-minute compute bound reached'

def path_global(path,o):return shift_path(path,o)

def main():
    OUT.mkdir(exist_ok=True);start_time=time.time();
    if not (OUT/'budget.json').exists():save(OUT/'budget.json',dict(start_epoch=start_time,deadline_epoch=start_time+1800,limit_seconds=1800))
    deadline()
    # Hash old evidence BEFORE any experimental output is computed.
    protected=[ROOT/'beads-photo-2.jpg',ROOT/'photo2/BROADER_PEAK_SEARCH_R269.md']+[p for name in ('r267','r268','r269') for p in sorted((ROOT/'photo2/review'/name).rglob('*')) if p.is_file()]+[p for p in sorted((ROOT/'photo2/bead_detection').glob('*.py')) if 'r270' not in p.name]
    save(OUT/'input-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in protected})
    rgb=photo();srgb,profile=color_managed_photo();save(OUT/'color-profile.json',profile);hsv,paper,bg=background(rgb);cases=json.load(open(PREV/'starts.json'));save(OUT/'legacy-starts.json',cases)
    params=dict(measures=list(MEASURES),score_scale='V DN; 255*linear sRGB Y; 255*OKLab L; VS=(maxRGB+minRGB)/2=V(1-S/2)',
        srgb_assumption='Native V and experimental native V/S preserve the historical samples. Y/OKL use ICC-converted sRGB samples with proper linearization. Native-RGB-as-sRGB control survives separately. No scene-linear exposure or recovered illumination claim',
        quantization_scale=SCALE,max_raw_rounding_error=0.5/SCALE,averaging='Transform each native pixel FIRST, then arithmetic mean; do not transform mean RGB',
        windows=[5,7,9],radii=list(RADII),policies=list(POLICIES),climbing='R268 deterministic strict 8-neighbor ascent; no equal steps; converted running raw-score 12-DN-equivalent guard',
        thresholds='For score m: floor_m(ref,d)=g_m(max(0,g_m_inverse(ref)-d)); g_m is response to neutral sRGB gray. Raw budgets12/24, mean budgets2/6. Neutral equivalence does not prove equal colored-image barriers.',
        background=bg,color='Identical original HSV hue/saturation and background rules; HSV V in reliability tests is fixed color evidence, not the optimized brightness score',
        common_guard_control='Original V climb anchor and original V running-peak raw24 floor, converted mean2 floor; all radii. Separates score ranking from changed anchors/raw guards.',
        max_source='All regional plateau pixels intersecting each original crop, with 192-pixel context; independent raw and mean maxima for every score; no prominence gate',
        baseline='V legacy starts must exactly reproduce R268 guarded/unguarded paths and all R269 broad endpoints',sources=['https://www.w3.org/TR/WCAG21/relative-luminance.html','https://bottosson.github.io/posts/oklab/'])
    save(OUT/'parameters.json',params);save(OUT/'threshold-reference.json',[dict(measure=m,gray_dn=v,score=float(neutral(v,m)),floor12=float(neutral(max(0,v-12),m)),floor24=float(neutral(max(0,v-24),m)),floor2=float(neutral(max(0,v-2),m)),floor6=float(neutral(max(0,v-6),m))) for m in MEASURES for v in (32,64,128,192,240)])
    all_rows=[];candidate_sets={};inventories={};focus=[];decisions=[];alternatives=[];counts=Counter();baseline_rows={};summary={}
    with gzip.GzipFile(filename=str(OUT/'photo-climbs.jsonl.gz'),mode='wb',mtime=0) as cf,gzip.GzipFile(filename=str(OUT/'photo-searches.jsonl.gz'),mode='wb',mtime=0) as sf:
      for crop,case in cases.items():
        deadline();points=np.array([s['xy'] for s in case['starts']]);b=case['box'];x0=max(0,min(b[0],int(points[:,0].min()))-192);y0=max(0,min(b[1],int(points[:,1].min()))-192);x1=min(rgb.shape[1],max(b[2],int(points[:,0].max())+1)+192);y1=min(rgb.shape[0],max(b[3],int(points[:,1].max())+1)+192);o=np.array([x0,y0]);cut=np.s_[y0:y1,x0:x1];image=rgb[cut];standard=srgb[cut];hs=hsv[cut];pp=paper[cut];qs=quantized(image,standard);unrounded=paired_scores(image,standard);local_box=(np.array(b)-[x0,y0,x0,y0]).tolist()
        surfaces={m:{n:Climber(qs[m],hs,pp,n,m) for n in (5,7,9)} for m in MEASURES};fields={'origin':o,'rgb':image,'srgb':standard,'hsv':hs,'background_stop_codes':pp};types=defaultdict(list);raw_meta={};measure_starts={}
        for m in MEASURES:
            fields['raw_'+m]=unrounded[m];fields['q_'+m]=qs[m];raw,mask=maxima_inventory(qs[m],local_box);prom=prominences(qs[m],raw);raw_meta[m]={}
            for (x,y,label),pr in zip(raw,prom):
                xy=(x+x0,y+y0);types[xy].append(m+'-raw');raw_meta[m][xy]=dict(plateau=label,**pr)
            own=set((x+x0,y+y0) for x,y,_ in raw)
            for n,c in surfaces[m].items():
                fields[f'sum_{m}_{n}']=c.sumq;maxpts,_=maxima_inventory(c.sumq,local_box)
                for x,y,label in maxpts:types[x+x0,y+y0].append(f'{m}-mean{n}');own.add((x+x0,y+y0))
            starts=[dict(s) for s in case['starts']];oldxy={tuple(s['xy']) for s in starts}
            for i,xy in enumerate(sorted(own-oldxy,key=lambda p:(p[1],p[0])),1):starts.append(dict(id=f'{m}-N{i:04d}',xy=list(xy),origins=[dict(source='r270-'+m,role='independent-maximum',status='audit')]))
            measure_starts[m]=starts
        for s in case['starts']:types[tuple(s['xy'])].append('legacy-start')
        # Preserve all R269 competing points even when not maxima of a new measure.
        for r in csv.DictReader(open(PREV/f'{crop}-all-competing-points.csv')):types[int(r['x']),int(r['y'])].append('R269-competing-point')
        candidates=[]
        for i,(xy,tags) in enumerate(sorted(types.items(),key=lambda p:(p[0][1],p[0][0])),1):
            x,y=np.array(xy)-o;r=dict(id=f'C{i:04d}',number=i,x=int(xy[0]),y=int(xy[1]),types=sorted(tags),rgb=image[y,x].tolist(),h_deg=float(hs[y,x,0]*360),s=float(hs[y,x,1]),background_code=int(pp[y,x]))
            for m in MEASURES:
                r[m+'_raw']=float(unrounded[m][y,x]);r[m+'_prominence']=raw_meta[m].get(xy,{}).get('prominence',0.);r[m+'_prominence_censored']=raw_meta[m].get(xy,{}).get('prominence_censored',False)
                for n in (5,7,9):r[f'{m}_mean{n}']=float(surfaces[m][n].sumq[y,x]/(SCALE*n*n))
            candidates.append(r)
        candidate_sets[crop]=candidates;inventories[crop]=measure_starts;np.savez_compressed(OUT/f'{crop}-fields.npz',**fields);csvsave(OUT/f'{crop}-candidate-measurements.csv',candidates)
        oldclimbs=json.load(gzip.open(ROOT/f'photo2/review/r268/{crop}-traces.json.gz'));baseline_rows[crop]={(r['start_id'],int(r['window']),int(r['radius']),r['policy']):r for r in csv.DictReader(open(PREV/f'{crop}-search-endpoints.csv'))}
        named={}
        for label,pid in FOCUS[crop]:
            s=next(s for s in case['starts'] if any(z['id']==pid and z['role']=='seed' and z['source']=='straight-0-selected12' for z in s['origins']));named[s['id']]=(label,pid)
        vcache={};cropcounts=Counter()
        for m in MEASURES:
          for n in (5,7,9):
            c=surfaces[m][n]
            for s in measure_starts[m]:
                xy=(np.array(s['xy'])-o).tolist();legacy=s['id'].startswith('S');special=s['id'] in named
                guarded=c.climb(xy,True);unguarded=c.climb(xy,False)
                for mode,t in [('guarded12',guarded),('unguarded',unguarded)]:
                    counts['climb_moves']+=c.audit(t,mode=='guarded12');counts['climbs']+=1
                    writegz(cf,dict(crop=crop,measure=m,window=n,start_id=s['id'],legacy=legacy,mode=mode,trace=dict(t,start=s['xy'],endpoint=shift_xy(t['endpoint'],o),steps=path_global(t['steps'],o),blocked=[dict(z,from_xy=shift_xy(z['from_xy'],o),to_xy=shift_xy(z['to_xy'],o)) for z in t['blocked']])))
                    if m=='V' and legacy:
                        old=oldclimbs[str(n)][mode][s['id']];assert shift_xy(t['endpoint'],o)==old['endpoint'];assert [[z['x']+x0,z['y']+y0] for z in t['steps']]==[[z['x'],z['y']] for z in old['steps']];counts['baseline_climbs_exact']+=1
                assert all(17<=z['x']<image.shape[1]-17 and 17<=z['y']<image.shape[0]-17 for z in guarded['steps']),'Climb needs more context'
                g=Search(qs[m],hs,pp,c.sumq,n,guarded['endpoint'],m,guarded['steps'][-1]['running_peak'])
                key=tuple(xy),n
                if key not in vcache:vcache[key]=surfaces['V'][n].climb(xy,True)
                vt=vcache[key];common=Search(qs[m],hs,pp,c.sumq,n,vt['endpoint'],m,raw_v=qs['V']/SCALE,v_reference=vt['steps'][-1]['running_peak'],fixed_v=True)
                policies=[(k,p,g) for k,p in POLICIES.items()]+[('common-V-raw24-mean2',POLICIES['raw24-mean2'],common)]
                for radius in RADII:
                  for pname,policy,graph in policies:
                    r=graph.search(radius,policy);path=graph.path(r['pred'],r['end']);counts['search_moves']+=graph.audit_path(path,radius,policy);counts['searches']+=1;cropcounts[m]+=1
                    rawfloor,meanfloor=graph.floors(policy);row=dict(crop=crop,measure=m,window=n,start_id=s['id'],legacy=legacy,radius=radius,policy=pname,start=s['xy'],anchor=shift_xy(graph.anchor,o),endpoint=shift_xy(graph.xy[r['end']],o),anchor_raw=graph.reference_raw,raw_floor=rawfloor,mean_floor=meanfloor,anchor_mean=graph.reference_mean,end_mean=float(graph.mean[r['end']]),gain=float(graph.mean[r['end']]-graph.reference_mean),end_raw=float(graph.v[r['end']]),steps=len(path)-1,reachable_pixels=len(r['order']),start_background=r['start_blocked'],climb_stop=guarded['stop'])
                    all_rows.append(row);record=dict(**row,path=path_global(path,o),blocked_reason_counts=dict(Counter(z for e in r['frontier'] for z in e['reasons'])))
                    if special:
                        record['blocked_frontier']=[dict(e,from_xy=shift_xy(e['from_xy'],o),to_xy=shift_xy(e['to_xy'],o)) for e in r['frontier']]
                        record['reachable_tree']=[[int(graph.xy[i,0]+x0),int(graph.xy[i,1]+y0),int(r['pred'][i])] for i in r['order']];record['graph_origin']=[int(graph.x0+x0),int(graph.y0+y0)];record['graph_shape']=list(graph.shape)
                    writegz(sf,record)
                    if m=='V' and legacy and pname in POLICIES:
                        old=baseline_rows[crop][s['id'],n,radius,pname];assert row['endpoint']==json.loads(old['endpoint']) and row['end_mean']==float(old['end_mean']);counts['baseline_broad_exact']+=1
                    if special and radius==16:
                        label,pid=named[s['id']];focus.append(dict(**record,case=label,maximum_id=pid,climb=dict(guarded,steps=path_global(guarded['steps'],o),endpoint=shift_xy(guarded['endpoint'],o)),unguarded=dict(unguarded,steps=path_global(unguarded['steps'],o),endpoint=shift_xy(unguarded['endpoint'],o))))
                        if pname=='raw24-mean2':
                            capraw,predraw=graph.widest(radius,Policy(256,256),'raw');capmean,predmean=graph.widest(radius,policy,'mean')
                            for point in candidates:
                                idx=graph.index((point['x']-x0,point['y']-y0))
                                if idx is None or graph.dist2[idx]>radius**2:continue
                                reachable=bool(r['reachable'][idx])
                                reason='best-mean-proposal' if idx==r['end'] else 'reachable-lower-score-or-tie' if reachable else 'anchor-background' if r['start_blocked'] else 'color/background-barrier' if capraw[idx]<0 else 'raw-score-valley' if capraw[idx]<rawfloor-1e-9 else 'mean-score-valley'
                                d=dict(crop=crop,case=label,measure=m,window=n,start_id=s['id'],candidate_id=point['id'],x=point['x'],y=point['y'],reachable=reachable,reason=reason,score_raw=point[m+'_raw'],score_mean=point[f'{m}_mean{n}'],raw_saddle=float(capraw[idx]),mean_saddle=float(capmean[idx]),raw_floor=rawfloor,mean_floor=meanfloor)
                                decisions.append(d)
                                direct=direct_path(graph,idx)
                                # R269 direct_path uses the overridden floating-score path sampler.
                                alternatives.append(dict(**d,shortest=path_global(graph.path(r['pred'],idx) if reachable else [],o),widest_raw=path_global(graph.path(predraw,idx),o),widest_mean=path_global(graph.path(predmean,idx),o),direct=path_global(direct,o),direct_violations=[dict(e,from_xy=shift_xy(e['from_xy'],o),to_xy=shift_xy(e['to_xy'],o)) for e in direct_failures(graph,direct,radius,policy)]))
            deadline()
            print(crop,m,n,'starts',len(measure_starts[m]),'searches',counts['searches'],flush=True)
        summary[crop]=dict(legacy_starts=len(case['starts']),starts={m:len(s) for m,s in measure_starts.items()},candidate_pixels=len(candidates),searches=dict(cropcounts))
    save(OUT/'starts.json',inventories);save(OUT/'candidate-points.json',candidate_sets);save(OUT/'focus-results.json',focus);csvsave(OUT/'focus-candidate-decisions.csv',decisions)
    with gzip.GzipFile(filename=str(OUT/'alternative-paths.jsonl.gz'),mode='wb',mtime=0) as f:
        for r in alternatives:writegz(f,r)
    with gzip.open(OUT/'search-endpoints.csv.gz','wt') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(all_rows)
    save(OUT/'photo-summary.json',dict(cases=summary,counts=dict(counts),elapsed_seconds=time.time()-start_time));print('complete',dict(counts),flush=True)
if __name__=='__main__':main()
