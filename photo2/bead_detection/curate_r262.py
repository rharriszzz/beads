"""Only the R262 no-watershed change and its motivating pair; no other fixes."""
import gzip
import json
import shutil
import tarfile
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from .monotone_detect import ROOT,save,sha


def main():
    out=ROOT/'photo2/review/r262';out.mkdir(exist_ok=True)
    work=ROOT/'photo2/output/detection-r262';oldwork=ROOT/'photo2/output/detection-r261'
    before=json.loads((oldwork/'regions.json').read_text());after=json.loads((work/'regions.json').read_text())
    old={r['id']:r for r in before['regions']+before['rejected']};new={r['id']:r for r in after['regions']+after['rejected']}
    fields=['id','peak','value_dn','meaningful','plateau_runs']
    assert [{k:m[k] for k in fields} for m in before['maxima']]==[{k:m[k] for k in fields} for m in after['maxima']]
    assert before['parameters']==after['parameters']
    pairs=[]
    def points(r):return {(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)}
    for rid in ['P032240','P032353']:
        a,b=old[rid],new[rid]
        with gzip.open(oldwork/a['trace_file'],'rt') as f:ta=json.load(f)
        with gzip.open(work/b['trace_file'],'rt') as f:tb=json.load(f)
        amap={(q[0],q[1]):i for i,q in enumerate(tb['accepted'])};pa,pb=points(a),points(b)
        examples=[]
        for s in ta['stops']:
            if s[7]=='competing-maximum-catchment' and (s[0],s[1]) in amap:
                pred=ta['accepted'][s[2]];idx=amap[s[0],s[1]];now=tb['accepted'][idx]
                examples.append(dict(old_predecessor=pred[:4],old_stop=s,new_acceptance_index=idx,new_acceptance=now))
        pairs.append(dict(id=rid,old_pixels=a['pixel_count'],new_pixels=b['pixel_count'],old_growth=a['growth_pixel_count'],new_growth=b['growth_pixel_count'],
            old_centroid=a['centroid'],new_centroid=b['centroid'],new_location=b['location'],added_pixels=len(pb-pa),removed_pixels=len(pa-pb),
            old_stops=dict(Counter(s[7] for s in ta['stops'])),new_stops=dict(Counter(s[7] for s in tb['stops'])),formerly_blocked_now_accepted=examples))
    overlap=sorted(points(new['P032240']) & points(new['P032353']))
    save(out/'pair-comparison.json',dict(before_generation=before['generation_id'],after_generation=after['generation_id'],unchanged_maxima_and_parameters=True,
        pair=pairs,pair_overlap_pixels=len(overlap),pair_overlap_xy=overlap))
    rgb=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');box=(450,640,515,701);scale=7
    raw=rgb.crop(box).resize((455,427),Image.Resampling.NEAREST);im=Image.new('RGB',(1365,466),'#17202a');d=ImageDraw.Draw(im)
    for j,(label,records) in enumerate([('Original native pixels',None),('R261: ownership partition',old),('R262: independent pixel growth',new)]):
        im.paste(raw,(455*j,39));d.text((455*j+8,8),label,fill='white')
        if records:
            for rid,color in [('P032240','cyan'),('P032353','yellow')]:
                r=records[rid]
                for c in r['contours']:d.line([((x-box[0]+.5)*scale+455*j,(y-box[1]+.5)*scale+39) for x,y in c],fill=color,width=2)
                x,y=r['bright_patch']['peak'];x=(x-box[0]+.5)*scale+455*j;y=(y-box[1]+.5)*scale+39;d.line((x-5,y,x+5,y),fill=color,width=2);d.line((x,y-5,x,y+5),fill=color,width=2)
    d.text((8,24),'Cyan P032240 / yellow P032353; crosses = unchanged maxima; 7x nearest-neighbor photograph',fill='white');im.save(out/'pair-no-watershed.png')
    for name in ['labels.npz','coordinates.csv','rank-size.csv','size-distribution.png','summary.json']:
        shutil.copy2(work/name,out/name)
        if name.endswith('.csv'):(out/name).write_text((out/name).read_text())
    with gzip.GzipFile(filename=str(out/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((work/'regions.json').read_bytes())
    with tarfile.open(out/'growth-traces.tar','w') as tar:
        for path in sorted((work/'traces').glob('*.gz')):
            info=tar.gettarinfo(str(path),arcname='traces/'+path.name);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
            with path.open('rb') as f:tar.addfile(info,f)
    save(out/'manifest.json',{p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ('README.md','manifest.json')})
    print(json.dumps(dict(pair=[{k:v for k,v in q.items() if k!='formerly_blocked_now_accepted'} for q in pairs],overlap_pixels=len(overlap)),indent=2))

if __name__=='__main__':main()
