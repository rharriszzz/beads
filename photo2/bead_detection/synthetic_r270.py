"""Paired score validation, adding color-varying highlights to preserved stress scenes."""
from collections import Counter,defaultdict
import csv,gzip,json,time
import numpy as np
from matplotlib.colors import hsv_to_rgb
from scipy import ndimage as ndi
from skimage.morphology import local_maxima
from .audit_r267 import ROOT,save,csvsave
from .climb_r268 import background
from .search_r269 import POLICIES
from .synthetic_r268 import start_points
from .brightness_r270 import MEASURES,SCALE,Climber,Search,quantized,scores,linearize,encode
from .experiment_r270 import OUT,deadline
from .experiment_r269 import RADII,writegz

def colored_scenes():
    y,x=np.mgrid[:71,:91]
    for palette in range(4):
      for gap in (-2,0,4):
        sep=24+gap;centers=[(43-sep//2,35),(43+sep//2,35)]
        hs=[(.12,.83),(.12 if palette==0 else .02 if palette==1 else .58 if palette==2 else .0,.83)]
        if palette==2:hs[0]=(.67,.88)
        if palette==3:hs[0]=(.02,.85);hs[1]=(.10,.8)
        bg=hsv_to_rgb(np.array([.87,.35,.79]));lin=np.broadcast_to(linearize(bg),(71,91,3)).copy();lin*=1-.36*np.exp(-((x-45)**2+(y-42)**2)/400)[:,:,None];truth=np.zeros((71,91),np.int16)
        for body,((cx,cy),(h,s)) in enumerate(zip(centers,hs),1):
            rr=((x-cx)/12)**2+((y-cy)/14)**2;mask=rr<=1
            diffuse=linearize(hsv_to_rgb(np.array([h,s,.9])));shading=(.62-.36*np.minimum(rr,1))*(1-.10*(x-cx)/12)
            highlight=.42*np.exp(-((x-cx+4)**2+(y-cy+2)**2)/13)+.18*np.exp(-((x-cx-3)**2+(y-cy-2)**2)/6)
            # Linear-light white specular contribution over colored diffuse body.
            bodyrgb=np.clip(diffuse*shading[:,:,None]+highlight[:,:,None],0,1)
            lin[mask]=bodyrgb[mask];truth[mask]=body
        rgb=np.rint(encode(lin)*255).clip(0,255).astype(np.uint8)
        yield f'colored-highlight-{palette}-gap{gap}',rgb,truth

def representatives(q):
    mask=local_maxima(q,connectivity=2,allow_borders=True);labels,_=ndi.label(mask,np.ones((3,3)));points=[]
    for label,sl in enumerate(ndi.find_objects(labels),1):
        if sl is None:continue
        yy,xx=np.where(labels[sl]==label);dist=(xx-xx.mean())**2+(yy-yy.mean())**2;k=np.argmin(dist);a=int(xx[k]+sl[1].start);b=int(yy[k]+sl[0].start)
        if 4<=a<q.shape[1]-4 and 4<=b<q.shape[0]-4:points.append((a,b))
    return points,mask

def main():
    started=time.time();old=np.load(ROOT/'photo2/review/r268/synthetic-inputs.npz');oldtruth=np.load(ROOT/'photo2/review/r268/synthetic-truth.npz');scenes=[(name,old[name],oldtruth[name]) for name in old.files]+list(colored_scenes())
    frames={name:im for name,im,t in scenes};truths={name:t for name,im,t in scenes};np.savez_compressed(OUT/'synthetic-inputs.npz',**frames);np.savez_compressed(OUT/'synthetic-truth.npz',**truths)
    inventories=[];rows=[];counts=Counter();failures={};baseline={}
    for r in csv.DictReader(open(ROOT/'photo2/review/r269/synthetic-results.csv')):baseline[r['scene'],int(r['window']),int(r['radius']),r['policy']]=r
    with gzip.GzipFile(filename=str(OUT/'synthetic-climbs.jsonl.gz'),mode='wb',mtime=0) as cf,gzip.GzipFile(filename=str(OUT/'synthetic-searches.jsonl.gz'),mode='wb',mtime=0) as sf:
      for index,(name,rgb,truth) in enumerate(scenes):
        deadline();hsv,paper,_=background(rgb);qs=quantized(rgb);native={};maxmasks={};origins=defaultdict(list)
        for m in MEASURES:
            pts,mask=representatives(qs[m]);native[m]=pts;maxmasks[m+'_raw']=mask
            for xy in pts:origins[xy].append(m)
        points=sorted(origins,key=lambda p:(p[1],p[0]));eligible=[p for p in points if paper[p[1],p[0]]==0];vpoints=set(start_points(rgb.max(axis=2)))
        inventories.append(dict(scene=name,points=[dict(x=x,y=y,sources=origins[x,y],eligible=bool(paper[y,x]==0),background_code=int(paper[y,x]),truth=int(truth[y,x]),legacy_v=(x,y) in vpoints) for x,y in points],native_maximum_pixel_counts={m:int(mask.sum()) for m,mask in maxmasks.items()}))
        # Save complete raw and mean maximum masks; representatives do not discard
        # plateau pixels from the numerical record.
        fields=dict(rgb=rgb,background=paper)
        for m in MEASURES:
            fields['q_'+m]=qs[m];fields[m+'_raw_maxima']=maxmasks[m+'_raw']
            for n in (5,7,9):
                c=Climber(qs[m],hsv,paper,n,m);fields[f'sum_{m}_{n}']=c.sumq;fields[f'{m}_mean{n}_maxima']=local_maxima(c.sumq,connectivity=2,allow_borders=False)
        np.savez_compressed(OUT/'synthetic-fields'/f'{name}.npz',**fields)
        vcache={};groups=defaultdict(list)
        for m in MEASURES:
          for n in (5,7,9):
            c=Climber(qs[m],hsv,paper,n,m)
            for si,xy in enumerate(eligible):
                t=c.climb(xy,True);u=c.climb(xy,False);legacy=xy in vpoints
                for mode,prefix in [('guarded12',t),('unguarded',u)]:
                    counts['climb_moves']+=c.audit(prefix,mode=='guarded12');counts['climbs']+=1
                    writegz(cf,dict(scene=name,measure=m,window=n,start_index=si,start=list(xy),mode=mode,legacy_v=legacy,truth_start=int(truth[xy[1],xy[0]]),trace=prefix))
                if (xy,n) not in vcache:vcache[xy,n]=Climber(qs['V'],hsv,paper,n,'V').climb(xy,True)
                vt=vcache[xy,n];g=Search(qs[m],hsv,paper,c.sumq,n,t['endpoint'],m,t['steps'][-1]['running_peak']);common=Search(qs[m],hsv,paper,c.sumq,n,vt['endpoint'],m,v_reference=vt['steps'][-1]['running_peak'],fixed_v=True)
                body=int(truth[xy[1],xy[0]])
                for radius in RADII:
                  for pname,policy,graph in [(p,pv,g) for p,pv in POLICIES.items()]+[('common-V-raw24-mean2',POLICIES['raw24-mean2'],common)]:
                    r=graph.search(radius,policy);path=graph.path(r['pred'],r['end']);counts['search_moves']+=graph.audit_path(path,radius,policy);counts['searches']+=1;ex,ey=graph.xy[r['end']];endbody=int(truth[ey,ex]);cross=body>0 and endbody not in (0,body);bg=body>0 and endbody==0
                    pathcross=body>0 and any(truth[p['y'],p['x']] not in (0,body) for p in path);prefixcross=body>0 and any(truth[p['y'],p['x']] not in (0,body) for p in t['steps'])
                    rawfloor,meanfloor=graph.floors(policy);record=dict(scene=name,measure=m,window=n,radius=radius,policy=pname,start_index=si,start=list(xy),legacy_v=legacy,anchor=list(graph.anchor),endpoint=[int(ex),int(ey)],raw_reference=graph.reference_raw,v_reference=graph.v_reference,raw_floor=rawfloor,mean_floor=meanfloor,anchor_mean=graph.reference_mean,end_mean=float(graph.mean[r['end']]),truth_start=body,truth_end=endbody,endpoint_cross=bool(cross),path_cross=bool(pathcross),prefix_cross=bool(prefixcross),background_exit=bool(bg),path=path,reachable_pixels=len(r['order']))
                    writegz(sf,record);groups[m,n,radius,pname].append(record)
                    if radius==16 and n==7 and body and (cross or bg):
                        kind='invisible-boundary' if name.startswith('no-visible') and cross else 'cross-body' if cross else 'background'
                        key=m+'-'+pname+'-'+kind
                        if key not in failures:failures[key]=dict(record,prefix=t,blocked_frontier=r['frontier'])
        for (m,n,radius,pname),rs in groups.items():
            def totals(rr):
                endpoint_groups=defaultdict(set)
                for r in rr:endpoint_groups[tuple(r['endpoint'])].add(r['truth_start'])
                return dict(starts=len(rr),body_starts=sum(r['truth_start']>0 for r in rr),cross_body=sum(r['endpoint_cross'] for r in rr),path_cross=sum(r['path_cross'] for r in rr),prefix_cross=sum(r['prefix_cross'] for r in rr),background_exits=sum(r['background_exit'] for r in rr),background_to_body=sum(r['truth_start']==0 and r['truth_end']>0 for r in rr),mixed_endpoint_groups=sum(len(s-{0})>1 for s in endpoint_groups.values()))
            a=totals(rs);paired=totals([r for r in rs if r['legacy_v']]);row=dict(scene=name,measure=m,window=n,radius=radius,policy=pname,**a,**{'paired_v_'+k:v for k,v in paired.items()});rows.append(row)
            if m=='V' and name in old.files and pname in POLICIES:
                ref=baseline[name,n,radius,pname]
                for k,oldk in [('body_starts','eligible_body_starts'),('cross_body','endpoint_cross'),('path_cross','path_cross'),('background_exits','body_to_background'),('mixed_endpoint_groups','mixed_endpoint_groups')]:assert paired[k]==int(ref[oldk]),(name,n,radius,pname,k,paired[k],ref[oldk])
                counts['baseline_synthetic_groups_exact']+=1
        if (index+1)%20==0:print('scenes',index+1,'searches',counts['searches'],'elapsed',round(time.time()-started),flush=True)
    csvsave(OUT/'synthetic-results.csv',rows);save(OUT/'synthetic-starts.json',inventories);save(OUT/'synthetic-failures.json',failures)
    summaries={}
    for cat in ('stress','no-visible-interface','colored-highlight'):
      for m in MEASURES:
       for n in (5,7,9):
        for radius in RADII:
         for pname in list(POLICIES)+['common-V-raw24-mean2']:
            rr=[r for r in rows if r['scene'].startswith(cat) and r['measure']==m and r['window']==n and r['radius']==radius and r['policy']==pname]
            summaries[f'{cat}-{m}-{n}-r{radius}-{pname}']={k:sum(r[k] for r in rr) for k in rows[0] if k not in ('scene','measure','window','radius','policy')}
    save(OUT/'synthetic-summary.json',dict(scenes=len(scenes),counts=dict(counts),elapsed_seconds=time.time()-started,results=summaries));print('complete',dict(counts),flush=True)
if __name__=='__main__':
    (OUT/'synthetic-fields').mkdir(exist_ok=True)
    main()
