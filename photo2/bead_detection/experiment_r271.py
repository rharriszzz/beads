"""Run R271 automatically on the photograph; review boxes enter only rendering."""
from pathlib import Path
import csv,gzip,hashlib,json,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .trusted_r271 import detect,Criteria
from .brightness_r270 import color_managed_photo

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/review/r271'
def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def jsonlines(name,rows):
    with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
        for row in rows:f.write((json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True);start=time.monotonic()
    old=[ROOT/'beads-photo-2.jpg']+list((ROOT/'photo2/review/r270').rglob('*'))+list((ROOT/'photo2/bead_detection').glob('*.py'))
    save('input-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in old if p.is_file() and 'r271' not in p.name})
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();save('color-profile.json',profile)
    save('parameters.json',dict(criteria=__import__('dataclasses').asdict(Criteria()),input='photograph and fixed parameters only; no previous detections or reviewed coordinates',proposal='all native-resolution mean7 luminance regional maxima; retain all plateau pixels',guards='unchanged R270 native-HSV/background/color and diagonal-corner guards; neutral-gray-equivalent raw12/24 mean2/6',search_windows=[5,7,9],search_radii=[10,16],acceptance='AND of all criteria; no quotas, no count optimization, no forced locations',brightness='ICC-managed linear sRGB relative luminance',illumination='measured image brightness proxy; cannot separate material reflectance from illumination'))
    rows,traces,summary,mask,paper=detect(native,srgb,progress=lambda *a:print(*a,flush=True))
    jsonlines('all-candidates.jsonl.gz',rows);jsonlines('search-traces.jsonl.gz',traces);save('trusted-locations.json',[dict(id=r['id'],x=r['x'],y=r['y']) for r in rows if r['trusted']])
    np.savez_compressed(OUT/'candidate-and-background-maps.npz',mean7_maxima=mask,background=paper)
    columns=['id','x','y','trusted','mean_y','raw_y','mean5_y','mean9_y','lit_fraction','core_pixels','window_ratio','local_contrast','plateau_diameter','background_pixels','search_checked','endpoint_spread','reasons','explanations']
    with gzip.open(OUT/'candidate-measurements.csv.gz','wt') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(row[k]) if isinstance(row.get(k),list) else row.get(k,'') for k in columns})
    trusted=[r for r in rows if r['trusted']];h,w=paper.shape
    # Fixed full-frame grid: diagnostic distribution only, never a selection quota.
    grid=np.zeros((4,4),int)
    for r in trusted:grid[min(3,r['y']*4//h),min(3,r['x']*4//w)]+=1
    summary.update(elapsed_seconds=time.monotonic()-start,image_shape=[h,w],coverage_grid4x4=grid.tolist(),occupied_full_frame_cells=int((grid>0).sum()))
    save('summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('background_model','conflicts')},indent=2),flush=True)
if __name__=='__main__':main()
