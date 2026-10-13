"""R275: reference-only centerline band; no modeled bead identities or predictions."""
from pathlib import Path
import json,gzip,hashlib
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'photo2/review/r275'
# Existing unregistered image-traced midpoint curve; exclude later model shift.
REFERENCE=ROOT/'photo2/review/r255/spline-samples.csv'
BAND=12.; POINT_REACH=26.; SCAN_REACH=40.
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def load_rows(path):
 with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]
def write_rows(name,rows):
 with gzip.GzipFile(filename=str(OUT/name),mode='wb',mtime=0) as f:
  for r in rows:f.write((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode())
class Band:
 def __init__(self,points=None):
  if points is None:
   a=np.genfromtxt(REFERENCE,delimiter=',',names=True);points=np.c_[a['x'],a['y']]
  # Linear subdivision to <=0.25px makes distance error at most 0.125px.
  self.points=np.asarray(points);dense=[]
  for a,b in zip(self.points,np.roll(self.points,-1,axis=0)):
   n=max(1,int(np.ceil(np.linalg.norm(b-a)/.25)));dense.extend(a+(b-a)*np.arange(n)[:,None]/n)
  self.tree=cKDTree(dense)
 def distance(self,points):return self.tree.query(points)[0]
 def qualifies(self,point,region=None):
  d=float(self.distance(point));rd=None
  if region and region.get('runs'):
   pts=np.array([(x,y) for y,a,b in region['runs'] for x in range(a,b+1)]);rd=float(self.distance(pts).min())
  return dict(in_band=bool(d<=POINT_REACH or rd is not None and rd<=BAND),point_distance=d,region_distance=rd)
def main():
 OUT.mkdir(exist_ok=True);b=Band();old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());regions={r['id']:r for r in old['beads']};rows=[]
 for l in old['locations']:
  r=regions.get(l['id']);rows.append(dict(id=l['id'],color=l['color'],**b.qualifies([l['point']['x'],l['point']['y']],r['region'] if r else None)))
 save('baseline-band.json',rows);save('band.json',dict(reference=str(REFERENCE.relative_to(ROOT)),sha256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),band_half_width=BAND,point_reach=POINT_REACH,scan_reach=SCAN_REACH,maximum_distance_approximation_error=.125,rule='Point within 26px (12px band plus 14px visible-body reach), OR native interior intersects the 12px band. Scan all maxima within 40px, retain final members by same rule. No model registration, bead indices or predicted sites.'))
 print('baseline band',sum(r['in_band'] for r in rows),'of',len(rows))
if __name__=='__main__':main()
