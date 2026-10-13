"""Bounded coverage runner; old evidence is comparison-only after detection."""
from pathlib import Path
import json,gzip,time,hashlib,csv
import numpy as np
from PIL import Image,ImageOps
from .coverage_r272 import detect
from .brightness_r270 import color_managed_photo
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/review/r272-coverage'
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def lines(name,rows):
    with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
        for r in rows:f.write((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode())
def check_budget():
    b=json.loads((OUT/'budget.json').read_text());assert time.time()<b['start']+b['seconds'],'Experiment budget exhausted'
def main():
    check_budget();t=time.monotonic();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();beads,records,traces,summary,masks=detect(native,srgb,progress=lambda *a:print(*a,flush=True));print('detected',summary['colors'],flush=True)
    lines('candidates.jsonl.gz',records);lines('search-traces.jsonl.gz',traces);np.savez_compressed(OUT/'all-maxima.npz',**masks)
    # Compact optional diagnostic layer excludes obvious paper/noise, which remain
    # fully present in candidates.jsonl.gz and all-maxima.npz.
    uncertain=[dict(id=r['id'],anchor=r['anchor'],color=r.get('color'),reasons=r['reasons'],explanations=r['explanations']) for r in records if not r['accepted'] and ('region' in r or 'primary_endpoint' in r)]
    data=dict(schema='r272-coverage-v1',source_image_sha256=hashlib.sha256((ROOT/'beads-photo-2.jpg').read_bytes()).hexdigest(),image=dict(width=srgb.shape[1],height=srgb.shape[0],file='../r272/photo-srgb.png',profile=profile),beads=beads,uncertain=uncertain,coordinate_convention='Native integer pixel centers, inclusive [y,x_first,x_last] mask runs; no modeled string index.',id_convention='C/K-native-anchor is stable for a source image, pathway and parameters; inventory number is sequential row-major accepted order.')
    save('inventory.json',data);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'),allow_nan=False)+';\n')
    with (OUT/'inventory.csv').open('w',newline='') as f:
        fields=['id','inventory_number','color','x','y','luminance','patch_pixels','patch_centroid','region_pixels','region_centroid'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
        for b in beads:w.writerow(dict(id=b['id'],inventory_number=b['inventory_number'],color=b['color'],x=b['brightest']['x'],y=b['brightest']['y'],luminance=b['brightest']['luminance'],patch_pixels=b['bright_patch']['pixel_count'],patch_centroid=json.dumps(b['bright_patch']['centroid']),region_pixels=b['region']['pixel_count'],region_centroid=json.dumps(b['region']['centroid'])))
    old=json.loads((ROOT/'photo2/review/r271/trusted-locations.json').read_text());xy=np.array([b['anchor'] for b in beads]);comparisons=[]
    for r in old:
        ds=np.linalg.norm(xy-[r['x'],r['y']],axis=1);j=int(np.argmin(ds));comparisons.append(dict(old_id=r['id'],old_coordinate=[r['x'],r['y']],nearest_new_id=beads[j]['id'],distance=float(ds[j])))
    save('r271-comparison.json',dict(old_count=len(old),within6=sum(r['distance']<=6 for r in comparisons),within12=sum(r['distance']<=12 for r in comparisons),note='Spatial correspondence only, not verified same physical identity.',rows=comparisons))
    summary['elapsed_seconds']=time.monotonic()-t;save('summary.json',summary);print(json.dumps(summary,indent=2),flush=True);check_budget()
if __name__=='__main__':main()
