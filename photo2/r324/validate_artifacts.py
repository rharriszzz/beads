"""Delivery artifact consistency; no science proposals or changes."""
import re,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from .coupled import ROOT,OUT,read,save

def main():
 html=(OUT/'index.html').read_text();links=re.findall(r'(?:href|src)="([^"]+)"',html)
 for link in links:assert (OUT/link).exists(),link
 raw=np.array(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'));assert np.array_equal(np.array(Image.open(OUT/'bridge-raw.png')),raw[180:410,1470:1840])
 fs=read(OUT/'fit-summary.json');es=read(OUT/'expand-summary.json');g=read(OUT/'graph.json');ns={n['id']:n for n in g['intersections']};seed=read(OUT/'R321-photo-sized-rescue-frozen.json.gz')['seed_options'][0]
 checked=0
 for folder in ['fit-trials','expand-trials']:
  for path in (OUT/folder).glob('*.gz'):
   r=read(path)
   for row in r.get('support',[]):
    n=ns[row['id']];assert n['xy'][0]<=1510;assert row['index']==seed['origin']+np.dot(n['relative_ab'],seed['weights']);checked+=1
 for p in ['verification.json','physical-verification.json','browser-check.json']:assert read(OUT/p)['passed']
 assert read(OUT/'preservation.json')['unchanged'];assert read(OUT/'performance-control.json')['exact_scientific_parity'];assert read(OUT/'optical-speed.json')['exact_owner_intensity_arrays']
 files=[p for p in (ROOT/'photo2/r324').glob('*.py')]+[ROOT/'photo2'/f'R324_{name}.md' for name in ['REPORT','REPRODUCE','SPECIFICATION']]
 save(OUT/'source-manifest.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
 save(OUT/'artifact-validation.json',dict(passed=True,local_links=len(links),figures=html.count('<figure>'),raw_bridge_exact=True,strict_correspondence_rows=checked,all_strict_fits_stop_at_x1510=True,photo_evaluation=read(OUT/'validation.json')['summary'],preserved_files=read(OUT/'preservation.json')['verified_files']))
 print('ARTIFACT PASS',len(links),checked)
if __name__=='__main__':main()
