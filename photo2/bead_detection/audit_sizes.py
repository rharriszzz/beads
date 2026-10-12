"""Read saved area records across the workspace, distinguishing provenance later."""
import csv
import gzip
import json
import os
from pathlib import Path
from .tunable_detect import ROOT,save

FIELDS={'area','area_px','area_px2','area_pixels','pixel_count','pixels','n_pixels','mask_pixels',
        'visible_area','visible_area_px2','isolated_area','isolated_area_px2','unobstructed_area',
        'unobstructed_area_px2','projected_area','projected_area_px2','visible_px2','isolated_px2'}
SKIP={'pixel_runs','plateau_runs','patch_runs','contours','accepted','stops','retreat_floor_dn',
      'perimeter_runs','points','vertices','samples','rgb','hsv','image','mask','labels'}


def main():
    out=ROOT/'photo2/review/r263';records=[];scanned=[];errors=[];omitted=[]
    for directory,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in {'.git','.venv','node_modules','traces','__pycache__','.pytest_cache'}]
        for name in files:
            path=Path(directory)/name;rel=str(path.relative_to(ROOT))
            if name in {'size-audit.json','manifest.json'}:continue
            if not name.endswith(('.json','.json.gz','.csv','.csv.gz')):continue
            if path.stat().st_size>180_000_000:
                omitted.append(dict(file=rel,reason='over180MB; listed for explicit inspection'));continue
            maxima={}
            def put(field,value,context):
                try:value=float(value)
                except (TypeError,ValueError):return
                if value<=0:return
                if field not in maxima or value>maxima[field]['value']:
                    maxima[field]=dict(file=rel,field=field,value=value,context=context)
            def walk(obj,route='',parent=None):
                if isinstance(obj,dict):
                    context={k:obj[k] for k in ('id','region_id','observation_id','bead_id','bead_index','k','status','kind','label','centroid','center','location','source','image_path') if k in obj and not isinstance(obj[k],dict)}
                    if not context:context=parent or {}
                    for k,v in obj.items():
                        if k in SKIP:continue
                        if k in FIELDS:
                            if isinstance(v,(int,float)):put(k,v,dict(context,route=route))
                            elif isinstance(v,dict) and 'max' in v:put(k+'.max',v['max'],dict(context,route=route))
                            elif isinstance(v,list) and v and all(isinstance(n,(int,float)) for n in v):put(k+'[]',max(v),dict(context,route=route))
                        if isinstance(v,dict):walk(v,route+'/'+k,context)
                        elif isinstance(v,list) and v and isinstance(v[0],dict):
                            for i,item in enumerate(v):walk(item,route+'/'+k+'/'+str(i),context)
                elif isinstance(obj,list):
                    for i,item in enumerate(obj):
                        if isinstance(item,dict):walk(item,route+'/'+str(i),parent)
            try:
                opener=gzip.open if name.endswith('.gz') else open
                with opener(path,'rt') as f:
                    if '.csv' in name:
                        reader=csv.DictReader(f);fields=FIELDS&set(reader.fieldnames or [])
                        if fields:
                            for row in reader:
                                context={k:v for k,v in row.items() if k in ('id','region_id','bead_id','bead_index','k','status','kind','label','x','y','centroid_x','centroid_y')}
                                for field in fields:put(field,row[field],context)
                    else:walk(json.load(f))
                scanned.append(rel);records.extend(maxima.values())
            except (ValueError,OSError,UnicodeError) as e:errors.append(dict(file=rel,error=str(e)))
    records.sort(key=lambda r:-r['value'])
    save(out/'size-audit.json',dict(scanned_files=len(scanned),files=scanned,errors=errors,omitted=omitted,
        exclusions='Environment/git/node_modules caches and per-pixel growth traces; these are not per-bead area catalogs. Raster images were not automatically segmented anew.',
        note='Large values may be aggregate areas, multi-bead components, simulated areas or failed proposals; not automatically individual bead measurements.',maxima=records))
    print(json.dumps(dict(scanned_files=len(scanned),errors=errors,omitted=omitted,largest=records[:30]),indent=2))

if __name__=='__main__':main()
