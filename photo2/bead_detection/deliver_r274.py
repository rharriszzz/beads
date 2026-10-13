"""Export separate location and interior statuses for the minimal viewer."""
import sys,json,csv
from .experiment_r274 import ROOT,OUT,save
from .review_r274 import load
from .hue_r274 import VARIANTS
from dataclasses import asdict

def main(name):
 rows=load(name);beads=[{k:v for k,v in r.items() if k not in ('direction_stops','r272_measurements','supported_region')} for r in rows if r['accepted']];locations=json.loads((OUT/(name+'-locations.json')).read_text());prior=json.loads((ROOT/'photo2/review/r273/inventory.json').read_text());data=dict(schema='r274-location-and-interior-v1',source_image_sha256=prior['source_image_sha256'],image=prior['image'],coordinate_convention=prior['coordinate_convention'],id_convention=prior['id_convention'],beads=beads,locations=locations,uncertain=[dict(id=r['id'],anchor=r['anchor'],color=r['color'],reasons=r['reasons'],explanations=r['explanations']) for r in rows if r['location_status']!='trusted'])
 save('selection.json',dict(method=name,parameters=asdict(VARIANTS[name])));save('inventory.json',data);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'))+';\n')
 with (OUT/'inventory.csv').open('w',newline='') as f:
  fields=['id','inventory_number','color','location_x','location_y','location_luminance','interior_status','interior_pixels','interior_centroid','interior_peak','reasons'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();lookup={r['id']:r for r in beads}
  for r in locations:
   b=lookup.get(r['id']);w.writerow(dict(id=r['id'],inventory_number=r['inventory_number'],color=r['color'],location_x=r['point']['x'],location_y=r['point']['y'],location_luminance=r['point']['luminance'],interior_status=r['interior_status'],interior_pixels=b['region']['pixel_count'] if b else '',interior_centroid=json.dumps(b['region']['centroid']) if b else '',interior_peak=json.dumps(b['brightest']) if b else '',reasons='; '.join(r['explanations'])))
 print(name,len(beads),'interiors',len(locations),'locations')
if __name__=='__main__':main(sys.argv[1])
