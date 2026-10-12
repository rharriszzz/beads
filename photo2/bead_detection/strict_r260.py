"""Strict monotonic-darkening comparison, not the production detector.

Every sampled next Value must be strictly LOWER, including at the first step.
Equality and arbitrarily small increases stop the ray. No angular smoothing,
minimum growth radius, skipped dips or intensity tolerance can extend a run.
"""
import gzip
import json
import csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from .detect import ROOT,sha,contours,runs,measurements
from matplotlib.colors import rgb_to_hsv

COLOR_PARAMETERS=dict(hue_shift_degrees=20.,min_saturation=.35,min_hue_value=.20,
                      min_chroma=.08,dark_value=.32,dark_drop=.14,
                      chroma_retained_fraction=.45,persistence=2)


def color_stop(hsv):
    """Find persistent relative hue drift or dark/low-chroma evidence.

    This is a stopping clue, never a black-material classification. Input is
    already truncated to the strictly descending Value prefix.
    """
    p=COLOR_PARAMETERS;anchor=None;pending=None;count=0;first=None
    for j,(h,s,v) in enumerate(hsv):
        chroma=s*v
        reliable=s>=p['min_saturation'] and v>=p['min_hue_value'] and chroma>=p['min_chroma']
        if reliable and anchor is None:anchor=j
        drift=0. if anchor is None else abs((h-hsv[anchor,0]+.5)%1-.5)*360
        reason=None
        if reliable and drift>=p['hue_shift_degrees']:reason='relative-hue-change'
        # No hue inference at low chroma. A reflection can have no chromatic
        # anchor; require darkness AND a substantial drop from its peak instead.
        dark=v<=p['dark_value'] and hsv[0,2]-v>=p['dark_drop']
        lost_color=anchor is None or chroma<=p['chroma_retained_fraction']*hsv[anchor,1]*hsv[anchor,2]
        if dark and lost_color:reason='dark-low-chroma-clue'
        if reason is None:pending=None;count=0;continue
        if reason==pending:count+=1
        else:pending=reason;count=1;first=j
        if count>=p['persistence']:
            return dict(index=first,confirmed_at=j,reason=reason,anchor_index=anchor,
                        hue_drift_degrees=float(drift),first_hsv=hsv[first].tolist(),
                        confirmation_hsv=hsv[j].tolist(),
                        anchor_hsv=None if anchor is None else hsv[anchor].tolist())
    return None


def retreat_mask(mask,value,thresholds,x,y,x0,y0):
    """Exclude off-ray dark pixels too; preserve only the seed-connected part."""
    yy,xx=np.indices(mask.shape)
    angle=np.mod(np.arctan2(yy+y0-y,xx+x0-x),2*np.pi)
    local_threshold=np.interp(angle,np.linspace(0,2*np.pi,len(thresholds)+1),[*thresholds,thresholds[0]])
    mask=mask & (value>local_threshold)
    mask[y-y0,x-x0]=True
    components,_=ndi.label(mask)
    mask=components==components[y-y0,x-x0]
    nonseed=mask.copy();nonseed[y-y0,x-x0]=False
    assert np.all(value[nonseed]>local_threshold[nonseed])
    return mask


def radial_mask(radii,x,y,x0,y0,shape):
    """Pointwise angular interpolation keeps shrinking rays strictly nested.

    Polygon filling has ambiguous repeated vertices when rays shrink to zero.
    A direct polar envelope has no zero-width polygon wedges or winding rules.
    """
    yy,xx=np.indices(shape);dx=xx+x0-x;dy=yy+y0-y
    angle=np.mod(np.arctan2(dy,dx),2*np.pi)
    local_radius=np.interp(angle,np.linspace(0,2*np.pi,len(radii)+1),[*radii,radii[0]])
    return np.hypot(dx,dy)<=local_radius


def strict_stop(profile, retreat):
    """Return last strictly descending sample and last retained brighter sample."""
    end=0
    for j in range(1,len(profile)):
        if profile[j]>=profile[j-1]:break
        end=j
    threshold=profile[end]+retreat*(profile[0]-profile[end])
    keep=end
    while keep>0 and profile[keep]<=threshold:keep-=1
    return end,keep,float(threshold)


def experiment(rgb,data,mode,retreat,color_guard=False):
    hsv=rgb_to_hsv(rgb.astype(np.float32)/255)
    sigma=0. if mode=='native' else data['parameters']['blur_sigma']
    value=hsv[:,:,2] if not sigma else ndi.gaussian_filter(hsv[:,:,2],sigma)
    # Interpolate color in RGB, avoiding a spurious hue discontinuity at 0/360.
    color=rgb.astype(np.float32)/255
    if sigma:color=ndi.gaussian_filter(color,(sigma,sigma,0))
    maxima={m['id']:m for m in data['maxima']};rows=[]
    angles=np.arange(64)*2*np.pi/64;rr=np.arange(43)
    stops=[];retained=[];contracts=0
    for original in sorted(data['regions']+data['rejected'],key=lambda r:r['id']):
        # A genuine maximum in the existing image-derived bright patch, in the
        # signal being tested. No historical positions or new manual seeds.
        pixels=set()
        for mid in original['maxima_ids']:
            for y,a,b in maxima[mid]['patch_runs']:
                pixels.update((x,y) for x in range(a,b+1))
        px,py=original['initial_center']
        x,y=min(pixels,key=lambda xy:(-float(value[xy[1],xy[0]]),(xy[0]-px)**2+(xy[1]-py)**2,xy[1],xy[0]))
        coords=[y+np.sin(angles)[:,None]*rr,x+np.cos(angles)[:,None]*rr]
        profiles=ndi.map_coordinates(value,coords,order=1,mode='nearest')
        colors=rgb_to_hsv(np.stack([ndi.map_coordinates(color[:,:,c],coords,order=1,mode='nearest') for c in range(3)],axis=-1))
        colors[:,:,2]=profiles  # Exactly the Value signal used by the strict test.
        end=[];keep=[];threshold=[];events=[];effective=[];unguarded_keep=[]
        for ray,profile in enumerate(profiles):
            e,k,t=strict_stop(profile,retreat)
            assert np.all(np.diff(profile[:e+1])<0)
            assert e==len(profile)-1 or profile[e+1]>=profile[e]
            assert k==0 or profile[k]>t
            assert e==0 or k<e
            unguarded_keep.append(k)
            event=color_stop(colors[ray,:e+1]) if color_guard else None
            g=e
            if event:
                g=max(0,event['index']-1)
                _,k,t=strict_stop(profile[:g+1],retreat)
                events.append(dict(ray=ray,**event))
            assert g<=e and (k==0 or profile[k]>t)
            end.append(e);effective.append(g);keep.append(k);threshold.append(t);contracts+=1
        radius=max(unguarded_keep)
        x0,y0=max(x-radius-1,0),max(y-radius-1,0)
        x1,y1=min(x+radius+2,rgb.shape[1]),min(y+radius+2,rgb.shape[0])
        x0,y0,x1,y1=map(int,[x0,y0,x1,y1])
        mask=radial_mask(keep,x,y,x0,y0,(y1-y0,x1-x0))
        mask[y-y0,x-x0]=True  # A zero-length strict run retains its seed only.
        mask=retreat_mask(mask,value[y0:y1,x0:x1],threshold,x,y,x0,y0)
        r=dict(id=original['id'],production_status=original['status'],seed=[x,y],
               original_seed=original['initial_center'],stop_radii=end,retained_radii=keep,
               effective_stop_radii=effective,color_events=events,
               retreat_value_thresholds=threshold,contours=contours(mask,x0,y0),pixel_runs=runs(mask,x0,y0))
        r.update(measurements(mask,hsv[y0:y1,x0:x1],x0,y0));rows.append(r)
        if original['status']=='retained':stops.extend(end);retained.extend(keep)
    accepted=[r for r in rows if r['production_status']=='retained']
    original_by_id={r['id']:r for r in data['regions']}
    shifts=[float(np.linalg.norm(np.array(r['location'])-original_by_id[r['id']]['location'])) for r in accepted]
    event_counts={reason:sum(e['reason']==reason for r in accepted for e in r['color_events']) for reason in ['relative-hue-change','dark-low-chroma-clue']}
    summary=dict(mode=mode,signal_sigma=sigma,retreat_fraction=retreat,color_guard=color_guard,candidates=len(rows),
                 ray_contracts=contracts,comparison_regions=len(accepted),
                 color_event_counts=event_counts,color_affected_regions=sum(bool(r['color_events']) for r in accepted),
                 pixel_count=dict(min=min(r['pixel_count'] for r in accepted),median=float(np.median([r['pixel_count'] for r in accepted])),max=max(r['pixel_count'] for r in accepted)),
                 seed_only_regions=sum(r['pixel_count']==1 for r in accepted),
                 below_18_pixels=sum(r['pixel_count']<18 for r in accepted),
                 median_stop_radius=float(np.median(stops)),median_retained_radius=float(np.median(retained)),
                 capped_rays=sum(e==42 for e in stops),duplicate_locations=len(accepted)-len({tuple(r['location']) for r in accepted}),
                 location_movement_px=dict(median=float(np.median(shifts)),p90=float(np.percentile(shifts,90)),max=max(shifts)))
    return dict(summary=summary,color_parameters=COLOR_PARAMETERS if color_guard else None,regions=rows)


def main():
    work=ROOT/'photo2/output/detection-r259';out=ROOT/'photo2/review/r260';out.mkdir(exist_ok=True)
    data=json.loads((work/'regions.json').read_text());rgb=np.asarray(Image.open(work/'photo.png'))
    results={}
    for mode in ['native','smoothed']:
        for retreat,guard in [(.14,False),(.30,False),(.30,True)]:
            key=f'{mode}-{int(retreat*100)}'+('-color' if guard else '')
            result=experiment(rgb,data,mode,retreat,guard)
            results[key]=result
            result['source_sha256']=data['image_sha256'];result['parent_generation']=data['generation_id']
            result['experiment_source_sha256']=sha(__file__)
            (out/f'strict-{key}.json.gz').write_bytes(gzip.compress(json.dumps(result,separators=(',',':'),allow_nan=False).encode(),mtime=0))
            with (out/f'strict-{key}-coordinates.csv').open('w') as f:
                writer=csv.writer(f,lineterminator='\n');writer.writerow(['id','production_status','x','y','centroid_x','centroid_y','pixel_count'])
                for r in result['regions']:writer.writerow([r['id'],r['production_status'],*r['location'],*r['centroid'],r['pixel_count']])
    summary={key:result['summary'] for key,result in results.items()}
    (out/'strict-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Same raw contexts as the coordinate review; only diagnostic selection is fixed.
    ids=['R01307','R01441','R00956','R01284','R00912','R01207','R00362','R00732']
    production={r['id']:r for r in data['regions']+data['rejected']}
    native={r['id']:r for r in results['native-30']['regions']}
    smooth={r['id']:r for r in results['smoothed-30']['regions']}
    guarded={r['id']:r for r in results['smoothed-30-color']['regions']}
    changed=sorted(data['regions'],key=lambda r:np.linalg.norm(np.array(smooth[r['id']]['location'])-guarded[r['id']]['location']),reverse=True)
    hue_ids=[r['id'] for r in changed if any(e['reason']=='relative-hue-change' for e in guarded[r['id']]['color_events'])][:4]
    dark_ids=[r['id'] for r in changed if r['id'] not in hue_ids and any(e['reason']=='dark-low-chroma-clue' for e in guarded[r['id']]['color_events'])][:4]
    (out/'strict-color-review-ids.json').write_text(json.dumps(dict(hue=hue_ids,dark_clue=dark_ids),indent=2)+'\n')
    image=Image.fromarray(rgb)
    for page in range(4):
        sheet=Image.new('RGB',(1120,244*4),'#17212c');draw=ImageDraw.Draw(sheet)
        selected=ids[page*4:page*4+4] if page<2 else hue_ids if page==2 else dark_ids
        for row,id in enumerate(selected):
            x,y=production[id]['initial_center'];box=(x-48,y-44,x+48,y+44)
            columns=[('Raw',None),('Current',production[id]),('Strict native /30%',native[id]),('Strict smoothed /30%',smooth[id])]
            if page>=2:columns=[('Raw',None),('Current',production[id]),('Strict smoothed /30%',smooth[id]),('Plus hue/dark guard',guarded[id])]
            for col,(label,r) in enumerate(columns):
                crop=image.crop(box);dr=ImageDraw.Draw(crop)
                if r:
                    for c in r['contours']:dr.line([(a-box[0],b-box[1]) for a,b in c],fill='cyan',width=1)
                    a,b=r['location'];a-=box[0];b-=box[1];dr.line([(a-2,b),(a+2,b)],fill='white');dr.line([(a,b-2),(a,b+2)],fill='white')
                sheet.paste(crop.resize((264,176)),(col*280,row*244+50))
                draw.text((col*280+3,row*244+3),f'{id} {label}',fill='white')
                if r:draw.text((col*280+3,row*244+20),f'{r["pixel_count"]} pixels; location {r["location"]}',fill='white')
        sheet.save(out/(f'strict-comparison-{page+1}.png' if page<2 else f'strict-color-comparison-{page-1}.png'))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
