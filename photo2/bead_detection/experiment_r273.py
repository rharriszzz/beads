"""Recompute the baseline from pixels, then compare scoped R273 alternatives."""
from pathlib import Path
from dataclasses import replace
import json,gzip,time,hashlib,csv
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from .brightness_r270 import color_managed_photo
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine,Parameters
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/review/r273'
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def lines(name,rows):
    with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
        for r in rows:f.write((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode())
def main():
    OUT.mkdir(exist_ok=True);start=time.time();protected=[p for folder in ('r272','r272-coverage') for p in (ROOT/'photo2/review'/folder).rglob('*') if p.is_file()]+[ROOT/'photo2/COVERAGE_R272.md',ROOT/'photo2/TRUSTED_INVENTORY_R272.md']
    save('preserved-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected});native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,profile=color_managed_photo();base,_,_,baseline_summary,_=baseline(native,srgb);previous=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text());assert base==previous['beads'];print('exact baseline',len(base),flush=True)
    variants={'connected':Parameters(method='connected'),'star-color':Parameters(method='star-color'),'star-valley':Parameters()};summaries={}
    for name,p in variants.items():
        t=time.time();beads,records,edges,summary=refine(native,srgb,base,p);summary['seconds']=time.time()-t;summaries[name]=summary;lines(name+'-candidates.jsonl.gz',records);save(name+'-black-pairs.json',edges);print(name,summary,flush=True)
        if name=='star-valley':
            uncertain=[dict(id=r['id'],anchor=r['anchor'],color=r['color'],reasons=r['reasons'],explanations=r['explanations']) for r in records if not r['accepted']];data=dict(schema='r273-interior-inventory-v1',source_image_sha256=previous['source_image_sha256'],image=previous['image'],coordinate_convention=previous['coordinate_convention'],id_convention='Preserved automatic R272 location IDs; sequential inventory numbers are not physical-string indices.',beads=beads,uncertain=uncertain);save('inventory.json',data);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'))+';\n')
            with (OUT/'inventory.csv').open('w',newline='') as f:
                fields=['id','inventory_number','color','x','y','luminance','patch_pixels','patch_centroid','region_pixels','region_centroid'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
                for b in beads:w.writerow(dict(id=b['id'],inventory_number=b['inventory_number'],color=b['color'],x=b['brightest']['x'],y=b['brightest']['y'],luminance=b['brightest']['luminance'],patch_pixels=b['bright_patch']['pixel_count'],patch_centroid=json.dumps(b['bright_patch']['centroid']),region_pixels=b['region']['pixel_count'],region_centroid=json.dumps(b['region']['centroid'])))
    # Ownership-only controls keep original small black masks exactly unchanged.
    from .interiors_r273 import black_ownership
    from copy import deepcopy
    controls={}
    for radius in (8,12,16):
        for rule in ('winner','margin','defer'):
            rows=deepcopy([r for r in base if r['color']=='black']);edges=black_ownership(rows,native,srgb,replace(Parameters(),black_radius=radius,black_rule=rule));controls[f'{rule}-{radius}']=dict(accepted=sum(r['accepted'] for r in rows),reasons=dict(Counter(k for r in rows for k in r['reasons'])));lines(f'black-{rule}-{radius}.jsonl.gz',rows)
    save('black-controls.json',controls);save('summary.json',dict(variants=summaries,black_controls=controls,baseline_exact=True,baseline_count=len(base),elapsed_seconds=time.time()-start));print('complete',time.time()-start,flush=True)
if __name__=='__main__':main()
