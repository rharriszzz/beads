"""Bounded direct native-pixel verification; no classifier regression suite."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageOps
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def main():
 d=json.loads((OUT/'measurements.json').read_text());photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');n=0
 assert hashlib.sha256((ROOT/'beads-photo-2.jpg').read_bytes()).hexdigest()==d['source_photo_sha256']
 for r in d['records']:
  x,y,u,v=r['patch_box'];a,b,c,e=r['absolute_material_box'];assert a<=x<u<=c and b<=y<v<=e and u-x==v-y==3
  vals=[[list(photo.getpixel((x+i,y+j))) for i in range(3)] for j in range(3)];assert vals==r['patch_RGB'];assert max(max(pixel) for row in vals for pixel in row)==r['score']
  assert Image.open(OUT/f'native-{r["number"]:02d}.png').tobytes()==photo.crop(r['bbox']).tobytes();n+=1
 assert n==48 and d['previous_threshold']==73.5 and not d['previous_threshold_errors']
 for color in ['black','red','yellow']:
  scores=[r['score'] for r in d['records'] if r['color']==color];assert [min(scores),max(scores)]==d['ranges'][color]
 q=json.loads((ROOT/'photo2/r340/quick-diagnostic/measurements.json').read_text());old={r['id'] for r in q['records']};new=[r for r in d['records'] if r['id'] not in old];assert len(new)==45
 receipt=dict(passed=True,native_patch_RGB_checks=n,literal_native_crops=n,fixed_threshold=73.5,fixed_threshold_errors=0,additional_to_quick_diagnostic=45,range_checks=3,region_coordinates='All selected patches entirely inside frozen manually approved glass rectangles',manual_ownership_limit='Ownership was visually inspected; not automatically proved by a darkness mask.',utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
