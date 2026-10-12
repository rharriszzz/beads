"""Saved synthetic and native photo evidence. Historical IDs are diagnostics only."""
import argparse
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from .pixel_detect import ROOT, detect, save, sha
from .test_pixels import fixtures, audit_trace

OUT=ROOT/'photo2/review/r261'


def synthetic():
    OUT.mkdir(parents=True,exist_ok=True);report={}
    for name,rgb in fixtures().items():
        data,labels,owners=detect(rgb);ac=st=0
        for r in data['regions']+data['rejected']:
            a,s=audit_trace(r,owners);ac+=a;st+=s
        report[name]=dict(raw_maxima=len(data['maxima']),meaningful=sum(m['meaningful'] for m in data['maxima']),
                         regions=len(data['regions']),accepted_pixels=ac,stopped_edges=st,contracts='passed')
        with gzip.GzipFile(filename=str(OUT/f'synthetic-{name}.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(data,separators=(',',':')).encode())
        raw=Image.fromarray(rgb);mark=raw.copy();d=ImageDraw.Draw(mark)
        for r in data['regions']:
            for c in r['contours']:d.line([tuple(p) for p in c],fill='cyan',width=1)
            cx,cy=r['centroid'];d.line((cx-1,cy,cx+1,cy),fill='white');d.line((cx,cy-1,cx,cy+1),fill='white')
        # Integer nearest-neighbor magnification preserves every source pixel.
        canvas=Image.new('RGB',(raw.width*10,raw.height*5+30),'#17202a')
        canvas.paste(raw.resize((raw.width*5,raw.height*5),Image.Resampling.NEAREST),(0,30))
        canvas.paste(mark.resize((raw.width*5,raw.height*5),Image.Resampling.NEAREST),(raw.width*5,30))
        ImageDraw.Draw(canvas).text((5,8),name+' | raw native pixels (5x) / cyan retained supports',fill='white');canvas.save(OUT/f'synthetic-{name}.png')
    save(OUT/'synthetic-validation.json',report);print(json.dumps(report,indent=2))


def compare():
    work=ROOT/'photo2/output/detection-r261';new=json.loads((work/'regions.json').read_text())
    with gzip.open(ROOT/'photo2/review/r260/regions.json.gz','rt') as f:old=json.load(f)
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));image=Image.fromarray(rgb)
    previous={r['id']:r for r in old['regions']};newrows=new['regions']+new['rejected']
    details=[]
    for rid in ['R01307','R00956','R01284']:
        r=previous[rid];x0,y0,x1,y1=r['bbox'];box=(max(0,x0-18),max(0,y0-18),min(image.width,x1+18),min(image.height,y1+18))
        matches=[q for q in newrows if any(box[1]<=m[0]<box[3] and m[2]>=box[0] and m[1]<box[2] for m in q['pixel_runs'])]
        matches.sort(key=lambda q:np.linalg.norm(np.array(q['centroid'])-r['centroid']))
        raw=image.crop(box);scale=5;panels=[raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST) for _ in range(3)]
        def mark(panel,rows):
            d=ImageDraw.Draw(panel)
            for q in rows:
                for c in q['contours']:d.line([((a-box[0]+.5)*scale,(b-box[1]+.5)*scale) for a,b in c],fill='cyan',width=2)
                cx,cy=q['centroid'];cx=(cx-box[0]+.5)*scale;cy=(cy-box[1]+.5)*scale;d.line((cx-4,cy,cx+4,cy),fill='white',width=2);d.line((cx,cy-4,cx,cy+4),fill='white',width=2)
        mark(panels[1],[r]);mark(panels[2],[q for q in matches if q['status']=='retained'])
        scale=5;canvas=Image.new('RGB',(raw.width*scale*3,raw.height*scale+48),'#17202a');d=ImageDraw.Draw(canvas)
        for i,(panel,title) in enumerate(zip(panels,['Original pixels','R260 '+rid,'R261 separate pixel supports'])):
            canvas.paste(panel,(i*raw.width*scale,48));d.text((i*raw.width*scale+5,6),title,fill='white')
        d.text((5,27),f'Native crop x={box[0]}..{box[2]-1}, y={box[1]}..{box[3]-1}; 5x nearest; white = area centroid',fill='white');canvas.save(OUT/f'{rid}-native-comparison.png')
        # Every native pixel in the crop: raw RGB/HSV, old membership, new label,
        # acceptance predecessor/order and stop reasons in separate full traces.
        labels=np.load(work/'labels.npz')['labels'];oldmask=np.zeros(labels.shape,bool)
        for y,a,b in r['pixel_runs']:oldmask[y,a:b+1]=True
        from matplotlib.colors import rgb_to_hsv
        hsv=rgb_to_hsv(rgb[box[1]:box[3],box[0]:box[2]].astype(float)/255)
        with gzip.open(OUT/f'{rid}-native-pixels.csv.gz','wt') as f:
            f.write('x,y,R,G,B,H_deg,S,V,R260_member,R261_owner\n')
            for y in range(box[1],box[3]):
                for x in range(box[0],box[2]):
                    hh,ss,vv=hsv[y-box[1],x-box[0]]
                    f.write(f'{x},{y},{rgb[y,x,0]},{rgb[y,x,1]},{rgb[y,x,2]},{hh*360:.9f},{ss:.9f},{vv:.9f},{int(oldmask[y,x])},{labels[y,x]}\n')
        details.append(dict(r260_id=rid,crop=list(box),r260_pixels=r['pixel_count'],r260_centroid=r['centroid'],
            candidates=[dict(id=q['id'],status=q['status'],pixels=q['pixel_count'],centroid=q['centroid'],location=q['location'],
                             shared_native_pixels=sum(int(oldmask[y,a:b+1].sum()) for y,a,b in q['pixel_runs']),
                             centroid_distance=float(np.linalg.norm(np.array(q['centroid'])-r['centroid']))) for q in matches]))
    save(OUT/'r260-comparisons.json',dict(old_generation=old['generation_id'],new_generation=new['generation_id'],comparisons=details))
    print(json.dumps(details,indent=2))


def valley_proof():
    from dataclasses import replace
    from matplotlib.colors import rgb_to_hsv
    from .pixel_detect import grow, Parameters
    v=np.array([[100,95,90,85,80,75,70],[95,50,50,50,50,50,65],
                [90,50,60,60,60,50,60],[85,50,55,50,55,50,55],
                [80,75,70,65,60,55,50]],np.uint8)
    hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
    _,trace=grow(v,hsv,np.ones_like(v),1,(0,0),replace(Parameters(),dark_dn=0,retreat_dn=0,retreat_fraction=0))
    accepted={(a[0],a[1]):i for i,a in enumerate(trace['accepted'])}
    assert (3,2) not in accepted
    im=Image.new('RGB',(910,590),'#17202a');d=ImageDraw.Draw(im)
    d.text((12,10),'Alternate-route stress test: every cell is ONE native pixel (8 neighbors)',fill='white')
    d.text((12,30),'Cell labels: brightness DN / acceptance order. Orange: locked, never accepted.',fill='white')
    for y,row in enumerate(v):
        for x,value in enumerate(row):
            left,top=15+x*125,60+y*90;idx=accepted.get((x,y))
            d.rectangle((left,top,left+115,top+80),fill='#20454b' if idx is not None else '#563c20',outline='#69dce6' if idx is not None else '#ffaa33')
            d.text((left+12,top+14),f'({x}, {y}) V={value}',fill='white')
            d.text((left+12,top+40),f'order {idx}' if idx is not None else 'LOCKED',fill='white')
    d.text((15,525),'Central V=60 island is rejected from V=55 and V=50 approaches, despite the outer detour.',fill='white')
    d.text((15,548),'Single catchment in this stress test: the no-rise/irreversible-lock safeguards alone prevent entry.',fill='white')
    im.save(OUT/'valley-proof.png');save(OUT/'valley-proof.json',dict(values=v.tolist(),trace=trace))


def archive():
    import shutil, tarfile
    work=ROOT/'photo2/output/detection-r261'
    for name in ['labels.npz','coordinates.csv','rank-size.csv','size-distribution.png','summary.json']:
        shutil.copy2(work/name,OUT/name)
        if name.endswith('.csv'):(OUT/name).write_text((OUT/name).read_text())
    with gzip.GzipFile(filename=str(OUT/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((work/'regions.json').read_bytes())
    # Each member is already compressed, so tar adds no second compression cost.
    with tarfile.open(OUT/'growth-traces.tar','w') as tar:
        for path in sorted((work/'traces').glob('*.gz')):
            info=tar.gettarinfo(str(path),arcname='traces/'+path.name)
            info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
            with path.open('rb') as f:tar.addfile(info,f)
    manifest={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('manifest.json','README.md')}
    save(OUT/'manifest.json',manifest)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['synthetic','compare','archive','valley']);a=ap.parse_args();{'synthetic':synthetic,'compare':compare,'archive':archive,'valley':valley_proof}[a.mode]()
