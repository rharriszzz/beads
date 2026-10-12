"""Reproducible diagnostic comparison; frozen IDs are review samples, never priors."""
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from dataclasses import replace
from unittest.mock import patch
from .detect import ROOT,Parameters,radial_boundary


def main():
    out=ROOT/'photo2/review/r260';out.mkdir(parents=True,exist_ok=True)
    old=json.load(gzip.open(ROOT/'photo2/review/r259/regions.json.gz','rt'))
    new=json.loads((ROOT/'photo2/output/detection-r259/regions.json').read_text())
    a={r['id']:r for r in old['regions']+old['rejected']};b={r['id']:r for r in new['regions']+new['rejected']}
    old_ids={r['id'] for r in old['regions']};new_ids={r['id'] for r in new['regions']}
    common=old_ids&new_ids
    shifts=sorted([(float(np.linalg.norm(np.array(b[i]['centroid'])-a[i]['centroid'])),i) for i in common],reverse=True)
    changes=[dict(id=i,old_area=a[i]['pixel_count'],new_area=b[i]['pixel_count'],centroid_shift_px=s,
                  old_centroid=a[i]['centroid'],new_centroid=b[i]['centroid'],old_kind=a[i]['kind'],new_kind=b[i]['kind']) for s,i in shifts]
    spatial=[]
    for y in range(4):
        for x in range(4):
            opts=[r for r in old['regions'] if int(r['centroid'][0]/old['width']*4)==x and int(r['centroid'][1]/old['height']*4)==y]
            if opts:spatial.append(min(opts,key=lambda r:np.linalg.norm(np.array(r['centroid'])-[(x+.5)*old['width']/4,(y+.5)*old['height']/4]))['id'])
    groups=dict(largest=[r['id'] for r in sorted(old['regions'],key=lambda r:-r['pixel_count'])[:12]],
                smallest=[r['id'] for r in sorted(old['regions'],key=lambda r:r['pixel_count'])[:12]],
                recovered=sorted(new_ids-old_ids),largest_shifts=[i for _,i in shifts[:12]],spatial=spatial,
                coordinate_edge_cases=[r['id'] for r in new['regions'] if not r['centroid_inside_region']])
    image=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB')
    for name,ids in groups.items():
        # Raw / before / after, six rows per page. Region centroid is marked alone.
        for start in range(0,len(ids),6):
            page=ids[start:start+6];sheet=Image.new('RGB',(900,232*len(page)),'#17212c');draw=ImageDraw.Draw(sheet)
            for row,id in enumerate(page):
                x,y=a[id]['initial_center'];box=(x-50,y-46,x+50,y+46)
                for col,r in enumerate([None,a[id],b[id]]):
                    crop=image.crop(box);dr=ImageDraw.Draw(crop)
                    if r:
                        for c in r['contours']:dr.line([(xx-box[0],yy-box[1]) for xx,yy in c],fill='cyan',width=1)
                        cx,cy=r['centroid'];cx-=box[0];cy-=box[1]
                        dr.line([(cx-2,cy),(cx+2,cy)],fill='white');dr.line([(cx,cy-2),(cx,cy+2)],fill='white')
                    sheet.paste(crop.resize((280,184)),(col*300,row*232+44))
                    title=f'{id} raw' if r is None else f'{"Before" if col==1 else "After"}: {r["status"]}, {r["pixel_count"]} px'
                    draw.text((col*300+4,row*232+3),title,fill='white')
                    if r:draw.text((col*300+4,row*232+19),r['kind'],fill='white')
            sheet.save(out/f'{name}-{start//6+1}.png')
    summary=dict(old_generation=old['generation_id'],new_generation=new['generation_id'],
                 gained=sorted(new_ids-old_ids),lost=sorted(old_ids-new_ids),samples=groups,
                 common_centroid_shift_px=dict(median=float(np.median([s for s,_ in shifts])),p90=float(np.percentile([s for s,_ in shifts],90)),max=shifts[0][0]),changes=changes)
    (out/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
    rgb=np.asarray(image);value=ndi.gaussian_filter(rgb.max(axis=2).astype(np.float32)/255,1.15)
    chroma=rgb/np.maximum(rgb.max(axis=2,keepdims=True),1)
    paper=np.linalg.norm(chroma-old['background']['chromaticity'],axis=2)<old['background']['tolerance']
    diagnostic_ids=['R01307','R01441','R01284','R00956','R00460','R00913']
    sheet=Image.new('RGB',(1120,228*len(diagnostic_ids)),'#17212c');draw=ImageDraw.Draw(sheet);sensitivity=[]
    original_gaussian=ndi.gaussian_filter1d;original_median=ndi.median_filter
    for row,id in enumerate(diagnostic_ids):
        x,y=a[id]['initial_center'];box=(x-52,y-48,x+52,y+48)
        for col,rise in enumerate([None,.045,.025,.015]):
            crop=image.crop(box);dr=ImageDraw.Draw(crop)
            if rise:
                params=replace(Parameters(),rise=rise)
                edge,outer,closure,profiles,radii=radial_boundary(value,[x,y],params,paper)
                # Diagnostic ablation only: disable angular filters, retain radial smoothing.
                with patch.object(ndi,'gaussian_filter1d',side_effect=lambda z,*args,**kw:np.asarray(z) if kw.get('mode')=='wrap' else original_gaussian(z,*args,**kw)),patch.object(ndi,'median_filter',side_effect=lambda z,*args,**kw:np.asarray(z) if kw.get('mode')=='wrap' else original_median(z,*args,**kw)):
                    raw_radii=radial_boundary(value,[x,y],params,paper)[-1]
                dr.line([(xx-box[0],yy-box[1]) for xx,yy in edge],fill='cyan',width=1)
                sensitivity.append(dict(id=id,rise=rise,mean_radius=float(radii.mean()),max_radius=float(radii.max()),angular_smoothing_outward_max_px=float(np.max(radii-raw_radii))))
            sheet.paste(crop.resize((260,192)),(col*280,row*228+25));draw.text((col*280+3,row*228+4),id+(' raw' if rise is None else f' rise {rise}'),fill='white')
    sheet.save(out/'rise-comparison.png');(out/'sensitivity.json').write_text(json.dumps(sensitivity,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['samples','changes']},indent=2))


if __name__=='__main__':main()
