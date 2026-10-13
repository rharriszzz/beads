"""Recompute the uniform location algorithm, then build the R272 inventory."""
from pathlib import Path
from collections import Counter
import gzip,json,hashlib,time,csv
import numpy as np
from PIL import Image,ImageOps
from .trusted_r271 import detect
from .brightness_r270 import color_managed_photo
from .inventory_r272 import inventory
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/review/r272'
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def lines(name,rows):
    with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
        for r in rows:f.write((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(beads):
    rows=[]
    for b in beads:
        p=b['brightest'];a=b['region'];patch=b['bright_patch'];rows.append(dict(id=b['id'],inventory_number=b['inventory_number'],color=b['color'],brightest_x=p['x'],brightest_y=p['y'],luminance=p['luminance'],rgb_srgb=json.dumps(p['rgb_srgb']),hsv_srgb=json.dumps(p['hsv_srgb']),rgb_native=json.dumps(p['rgb_native']),hsv_native=json.dumps(p['hsv_native']),patch_x=patch['centroid'][0],patch_y=patch['centroid'][1],patch_pixels=patch['pixel_count'],area_pixels=a['pixel_count'],centroid_x=a['centroid'][0],centroid_y=a['centroid'][1]))
    with (OUT/'inventory.csv').open('w',newline='') as f:
        if rows:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
    OUT.mkdir(exist_ok=True);t=time.monotonic();old=[ROOT/'beads-photo-2.jpg']+[p for k in ('r270','r271') for p in (ROOT/'photo2/review'/k).rglob('*') if p.is_file()]+[p for p in (ROOT/'photo2/bead_detection').glob('*.py') if 'r272' not in p.name]
    save('input-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in old})
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();locations,traces,locsum,_,paper=detect(native,srgb,progress=lambda *a:print(*a,flush=True));lines('location-candidates.jsonl.gz',locations)
    beads,records,summary=inventory(native,srgb,locations,paper);lines('region-candidates.jsonl.gz',records)
    image_id=sha(ROOT/'beads-photo-2.jpg');data=dict(schema='r272-trusted-inventory-v1',source_image_sha256=image_id,image=dict(width=srgb.shape[1],height=srgb.shape[0],file='photo-srgb.png',profile=profile),coordinate_convention='native pixel centers use integer x,y; masks are inclusive [y,x_start,x_end] runs; counts/centroids are exact native mask measurements',id_convention='B-x-y is a source-image-scoped stable location ID; inventory_number is row-major accepted inventory order, never modeled string index',beads=beads)
    save('inventory.json',data);write_csv(beads);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'),allow_nan=False)+';\n');Image.fromarray(srgb).save(OUT/'photo-srgb.png')
    # Existing results are comparison only, after automatic detection has finished.
    previous=json.load(open(ROOT/'photo2/review/r271/trusted-locations.json'));assert {(r['x'],r['y']) for r in previous}=={(r['x'],r['y']) for r in locations if r['trusted']}
    summary.update(location_summary=locsum,source_image_sha256=image_id,old_proposals_exact=True,elapsed_seconds=time.monotonic()-t)
    grid=np.zeros((4,4),int)
    for r in beads:x,y=r['anchor'];grid[min(3,4*y//srgb.shape[0]),min(3,4*x//srgb.shape[1])]+=1
    summary['coverage_grid4x4']=grid.tolist();save('summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='location_summary'},indent=2),flush=True)
if __name__=='__main__':main()
