"""Select one globally uniform reviewed alternative; preserve every other trial."""
import sys,json,gzip,csv
from .experiment_r273 import ROOT,OUT,save
from .expansion_r273 import VARIANTS
from .interiors_r273 import Parameters
from dataclasses import asdict

def main(name):
 p=VARIANTS.get(name,Parameters());rows=[json.loads(l) for l in gzip.open(OUT/(name+'-candidates.jsonl.gz'),'rt')];beads=[{k:v for k,v in r.items() if k!='direction_stops'} for r in rows if r['accepted']];old=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text());uncertain=[dict(id=r['id'],anchor=r['anchor'],color=r['color'],reasons=r['reasons'],explanations=r['explanations']) for r in rows if not r['accepted']]
 data=dict(schema='r273-interior-inventory-v1',source_image_sha256=old['source_image_sha256'],image=old['image'],coordinate_convention=old['coordinate_convention'],id_convention='Preserved automatic R272 location IDs; sequential inventory numbers are not physical-string indices.',beads=beads,uncertain=uncertain)
 save('selection.json',dict(method=name,parameters=asdict(p)));save('inventory.json',data);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'))+';\n')
 with (OUT/'inventory.csv').open('w',newline='') as f:
  fields=['id','inventory_number','color','x','y','luminance','patch_pixels','patch_centroid','region_pixels','region_centroid'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
  for b in beads:w.writerow(dict(id=b['id'],inventory_number=b['inventory_number'],color=b['color'],x=b['brightest']['x'],y=b['brightest']['y'],luminance=b['brightest']['luminance'],patch_pixels=b['bright_patch']['pixel_count'],patch_centroid=json.dumps(b['bright_patch']['centroid']),region_pixels=b['region']['pixel_count'],region_centroid=json.dumps(b['region']['centroid'])))
 with (OUT/'paired-regions.csv').open('w',newline='') as f:
  fields=['id','color','accepted','old_pixels','new_pixels','ratio','reasons'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();lookup={r['id']:r for r in old['beads']}
  for r in rows:
   a=lookup[r['id']]['region']['pixel_count'];b=r.get('region',{}).get('pixel_count',0);w.writerow(dict(id=r['id'],color=r['color'],accepted=r['accepted'],old_pixels=a,new_pixels=b,ratio=b/a,reasons='; '.join(r['explanations'])))
 print(name,len(beads))
if __name__=='__main__':main(sys.argv[1])
