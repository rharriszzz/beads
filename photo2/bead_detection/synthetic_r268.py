"""Known synthetic validation; truth is evaluated after image-only climbing."""
from collections import Counter,defaultdict
import gzip,json
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import local_maxima,h_maxima
from matplotlib.colors import hsv_to_rgb
from PIL import Image,ImageDraw,ImageFont
from .climb_r268 import Surface,VARIANTS,background,audit
from .stress_r266 import stress_scenes
from .experiment_r268 import OUT,gzsave
from .audit_r267 import save,csvsave,FONT

def scenes():
    yield from stress_scenes()
    y,x=np.mgrid[:71,:91]
    for i in range(4):
        # Adversarial adjacent bodies with an intentionally uninformative internal
        # interface: known identity alone cannot make it observable in the image.
        hsv=np.full((71,91,3),[.86,.5,.82]);truth=np.zeros((71,91),np.int16)
        mask=(x>=12)&(x<=78)&(y>=15)&(y<=55)
        val=105+.85*(x-12)+60*np.exp(-((x-57)**2+(y-35)**2)/130)+3*np.sin(x*2+i)
        hsv[mask,0]=.12;hsv[mask,1]=.75;hsv[mask,2]=val[mask]/255
        truth[mask & (x<45)]=1;truth[mask & (x>=45)]=2
        yield f'no-visible-interface-{i}',np.round(hsv_to_rgb(hsv)*255).astype(np.uint8),truth,[[28,35],[61,35]],dict(adversarial_unobservable_identity=True,phase=i)

def start_points(value):
    mask=local_maxima(value,connectivity=2,allow_borders=True);labels,n=ndi.label(mask,np.ones((3,3)));points=[]
    for label,sl in enumerate(ndi.find_objects(labels),1):
        if sl is None:continue
        yy,xx=np.where(labels[sl]==label);k=np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2);x=int(xx[k]+sl[1].start);y=int(yy[k]+sl[0].start)
        if 4<=x<value.shape[1]-4 and 4<=y<value.shape[0]-4:points.append((x,y))
    return points

def figure(name,rgb,truth,points,results,variant="guarded12",window=7):
    scale=6;h,w=truth.shape;font=ImageFont.truetype(FONT,14);im=Image.new('RGB',(w*scale*3,h*scale+64),'#172028');d=ImageDraw.Draw(im)
    for j,title in enumerate(('Known rendering',f'{window}x{window} {variant} paths','Withheld identity truth')):
        base=rgb if j<2 else np.array([[35,40,50],[80,190,240],[255,180,70]],np.uint8)[truth]
        im.paste(Image.fromarray(base).resize((w*scale,h*scale),Image.Resampling.NEAREST),(j*w*scale,64));d.text((j*w*scale+8,8),title,fill='white',font=font)
        if j==1:
            for xy,t in zip(points,results):
                if not truth[xy[1],xy[0]]:continue
                ps=[(j*w*scale+(a['x']+.5)*scale,64+(a['y']+.5)*scale) for a in t['steps']]
                if len(ps)>1:d.line(ps,fill='#00ffff',width=1)
                ex,ey=ps[-1];d.ellipse((ex-2,ey-2,ex+2,ey+2),outline='#ffad32');sx,sy=ps[0];d.rectangle((sx-1,sy-1,sx+1,sy+1),outline='white')
    d.text((8,34),name+' | truth never enters climbing; white start, cyan path, orange end',fill='white',font=font);im.save(OUT/f'synthetic-{name}.png')

def main():
    rows=[];frames={};truths={};audited=0;scene_count=0
    with gzip.GzipFile(filename=str(OUT/'synthetic-traces.jsonl.gz'),mode='wb',mtime=0) as tracefile:
        for name,rgb,truth,centers,conditions in scenes():
            scene_count+=1;value=rgb.max(axis=2);hsv,paper,model=background(rgb);points=start_points(value);strong=h_maxima(value,12,footprint=np.ones((3,3)));frames[name]=rgb;truths[name]=truth
            for side in (5,7,9):
                surface=Surface(value,hsv,paper,side)
                for variant,g in VARIANTS.items():
                    results=[];groups=defaultdict(set);cross=0;background_exit=0;body_starts=0;blocked_body=0;unreached=set();start_error=[];end_error=[];gain=[];rawdrop=[];entered=0;cross_path=0;strong_counts=Counter()
                    for index,xy in enumerate(points):
                        t=surface.climb(xy,g);audited+=audit(surface,t,g);results.append(t);sx,sy=xy;ex,ey=t['endpoint'];body=int(truth[sy,sx]);endbody=int(truth[ey,ex])
                        groups[tuple(t['endpoint'])].add(body)
                        if body and strong[sy,sx]:
                            strong_counts['prominence12_body_starts']+=1
                            strong_counts['prominence12_cross_body_endpoints']+=int(endbody not in (0,body))
                            strong_counts['prominence12_body_to_background']+=int(endbody==0)
                        if body:
                            body_starts+=1;cross+=int(endbody not in (0,body));background_exit+=int(endbody==0);blocked_body+=int(t['stop'] in ('start-confident-background','start-existing-paper-context-uncertainty'))
                            cross_path+=int(any(truth[a['y'],a['x']] not in (0,body) for a in t['steps']))
                            start_error.append(float(np.linalg.norm(np.array(xy)-centers[body-1])));end_error.append(float(np.linalg.norm(np.array(t['endpoint'])-centers[body-1])));gain.append(t['steps'][-1]['score_dn']-t['steps'][0]['score_dn'])
                            rawdrop.append(max(a['running_raw_peak']-a['raw_v'] for a in t['steps']))
                        else:entered+=int(endbody>0)
                        tracefile.write((json.dumps(dict(scene=name,window=side,variant=variant,start_index=index,truth_start=body,truth_end=endbody,trace=t),separators=(',',':'))+'\n').encode())
                    row=dict(scene=name,conditions=conditions,window=side,variant=variant,raw_maximum_starts=len(points),body_starts=body_starts,cross_body_endpoints=cross,cross_body_paths=cross_path,body_to_background=background_exit,background_to_body=entered,false_background_starts=blocked_body,mixed_body_endpoint_groups=sum(len(s-{0})>1 for s in groups.values()),body_endpoints=len({tuple(t['endpoint']) for xy,t in zip(points,results) if truth[xy[1],xy[0]]}),mean_score_gain=float(np.mean(gain)) if gain else 0,mean_start_center_distance=float(np.mean(start_error)) if start_error else 0,mean_end_center_distance=float(np.mean(end_error)) if end_error else 0,max_raw_running_drop=max(rawdrop,default=0))
                    row.update({k:strong_counts[k] for k in ['prominence12_body_starts','prominence12_cross_body_endpoints','prominence12_body_to_background']});rows.append(row)
                    if side==7 and variant=='guarded12' and name in ('stress-000','stress-001','stress-002','stress-024','stress-066','no-visible-interface-0'):figure(name,rgb,truth,points,results)
            if scene_count%25==0:print('scenes',scene_count,flush=True)
    csvsave(OUT/'synthetic-results.csv',rows);np.savez_compressed(OUT/'synthetic-inputs.npz',**frames);np.savez_compressed(OUT/'synthetic-truth.npz',**truths)
    summary={}
    for category in ('stress','no-visible-interface'):
        for side in (5,7,9):
            for variant in VARIANTS:
                rs=[r for r in rows if r['scene'].startswith(category) and r['window']==side and r['variant']==variant]
                summary[f'{category}-{side}-{variant}']={k:sum(r[k] for r in rs) for k in ['raw_maximum_starts','body_starts','cross_body_endpoints','cross_body_paths','body_to_background','background_to_body','false_background_starts','mixed_body_endpoint_groups','prominence12_body_starts','prominence12_cross_body_endpoints','prominence12_body_to_background']}
    save(OUT/'synthetic-summary.json',dict(scenes=scene_count,audited_moves=audited,results=summary,interpretation='Repeated windows/variants reuse starts; never sum these as independent bodies. Center distances are descriptive, not a target or physical-center guarantee. The four continuous-interface examples intentionally lack visible identity boundaries.'))
    print('complete',scene_count,summary['stress-7-guarded12'],summary['no-visible-interface-7-guarded12'],flush=True)
if __name__=='__main__':main()
