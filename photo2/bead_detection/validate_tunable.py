"""Audit every exported R263 native pixel and frontier against the source photo."""
import argparse
import gzip
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .tunable_detect import ROOT, N8, save, sha, Parameters
from .test_tuning import audit

def audit_trace(r, budget):
    t=r["trace"];audit(t,budget)
    points={(a[0],a[1]) for a in t["accepted"] if a[7]}
    expected={(x,y) for y,a,b in r["pixel_runs"] for x in range(a,b+1)}
    assert points==expected and len(points)==r["pixel_count"]
    assert np.allclose(np.mean(list(points),axis=0),r["centroid"],rtol=0,atol=1e-12)
    assert tuple(r["location"]) in points
    for c in r["contours"]:assert c[0]==c[-1]
    return len(t["accepted"]),len(t["stops"])


def validate(work, output):
    data=json.loads((work/'regions.json').read_text());arrays=np.load(work/'labels.npz');labels=arrays['labels'];coverage=arrays['membership_count'];assert 'catchments' not in arrays.files
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    hsv=rgb_to_hsv(rgb.astype(float)/255);value=rgb.max(axis=2)
    assert data['image_sha256']==sha(ROOT/'beads-photo-2.jpg')
    assert data['detector_sha256']==sha(Path(__file__).with_name('tunable_detect.py'))
    reconstructed=np.zeros(labels.shape,np.int32);recount=np.zeros(labels.shape,np.uint32);counts=dict(regions=0,rejected_grown=0,accepted_pixels=0,stop_edges=0,dark_enclosures=0,retreated_pixels=0)
    reasons={};all_records=data['regions']+data['rejected'];p=Parameters(**data['parameters'])
    for r in all_records:
        with gzip.open(work/r['trace_file'],'rt') as f:trace=json.load(f)
        r['trace']=trace;a,s=audit_trace(r,p.rise_budget_dn);counts['accepted_pixels']+=a;counts['stop_edges']+=s
        assert r['growth_pixel_count']==a and r['stop_count']==s
        for row in trace['accepted']+trace['stops']:
            x,y=row[:2];assert row[3]==int(value[y,x]);assert np.allclose(row[4:7],hsv[y,x]*[360,1,1],rtol=0,atol=1e-12)
        for row in trace['stops']:
            assert row[7]!='competing-maximum-catchment'
            reasons[row[7]]=reasons.get(row[7],0)+1
        # All eight neighbors: every nonaccepted frontier edge must have a stop
        # record, or target a pixel queued by a different adjacent predecessor.
        aset={(a[0],a[1]) for a in trace['accepted']};stop_edges={(s[2],s[0],s[1]) for s in trace['stops']}
        for i,a in enumerate(trace['accepted']):
            for dy,dx in N8:
                x,y=a[0]+dx,a[1]+dy
                if 0<=x<labels.shape[1] and 0<=y<labels.shape[0] and (x,y) not in aset:
                    assert (i,x,y) in stop_edges, (r['id'],i,x,y)
            threshold=trace['retreat_floor_dn'][i]+max(p.retreat_dn,p.retreat_fraction*(trace['accepted'][0][3]-trace['retreat_floor_dn'][i]))
            expected=a[3]==trace['accepted'][0][3] or (a[3]>threshold and trace['accepted'][a[2]][7])
            assert a[7]==expected
        counts['retreated_pixels']+=sum(not a[7] for a in trace['accepted'])
        x0,y0,x1,y1=r['bbox'];mask=np.zeros((y1-y0,x1-x0),bool)
        for y,a,b in r['pixel_runs']:mask[y-y0,a-x0:b-x0+1]=True
        assert ndi.label(mask,structure=np.ones((3,3)))[1]==1
        if r['status']=='retained':
            counts['regions']+=1
            for y,a,b in r['pixel_runs']:
                target=reconstructed[y,a:b+1];count=recount[y,a:b+1]
                target[count==0]=int(r['id'][1:]);target[count>0]=-1;count+=1
        else:counts['rejected_grown']+=1
        dark=r['dark_enclosure']
        if dark:
            counts['dark_enclosures']+=1
            boundary=np.zeros(labels.shape,bool)
            for y,a,b in dark['perimeter_runs']:boundary[y,a:b+1]=True
            assert np.all(value[boundary]<=p.dark_dn)
            # An independent 4-connected exterior flood cannot reach the seed
            # without crossing the saved 8-connected dark shell (digital duality).
            exterior=ndi.binary_propagation(np.pad(np.ones((1,labels.shape[1]),bool),((0,labels.shape[0]-1),(0,0))),mask=~boundary)
            x,y=r['bright_patch']['peak'];assert not exterior[y,x]
            assert dark['perimeter_max_dn']==int(value[boundary].max())
    assert np.array_equal(reconstructed,labels)
    assert np.array_equal(recount,coverage)
    for r in data['regions']:
        assert r['overlap_pixel_count']==sum(int(np.count_nonzero(coverage[y,a:b+1]>1)) for y,a,b in r['pixel_runs'])
    maxima=data['maxima'];assert len({m['id'] for m in maxima})==len(maxima)
    assert sum(m['meaningful'] and m['value_dn']>=p.minimum_peak_dn for m in maxima)==len(all_records)
    assert sum(m['status']=='retained' for m in maxima)==len(data['regions'])
    result=dict(generation_id=data['generation_id'],source_sha256=data['image_sha256'],contracts='passed',**counts,stop_reasons=reasons,
                overlap_pixels=int(np.count_nonzero(coverage>1)),maxima_accounted=len(maxima),low_prominence_preserved=sum(not m['meaningful'] for m in maxima),
                check_notes=['Native RGB/HSV for every accepted and stopped pixel','All predecessor edges adjacent; rises bounded by the running minimum plus budget','Irreversible destination locks; no accumulating uphill budget','All eight frontier neighbors examined','Exact retreat, mask, centroid, supported coordinate and explicit overlapping memberships','Independent dark-enclosure exterior flood','All raw maximum candidates accounted'])
    save(output,result);print(json.dumps(result,indent=2))

def isolation(work, output):
    import shutil, subprocess, sys, tempfile
    with tempfile.TemporaryDirectory(prefix='beads-r262-isolation-') as temp:
        root=Path(temp);code=root/'package'/'detector';code.mkdir(parents=True)
        shutil.copy2(Path(__file__).with_name('tunable_detect.py'),code/'tunable_detect.py')
        shutil.copy2(ROOT/'beads-photo-2.jpg',root/'photo.jpg')
        params=json.loads((work/'regions.json').read_text())['parameters']
        flags=[v for k,value in params.items() for v in ('--'+k.replace('_','-'),str(value))]
        subprocess.run([sys.executable,str(code/'tunable_detect.py'),'--image',str(root/'photo.jpg'),'--output',str(root/'result')]+flags,cwd=root,check=True,stdout=subprocess.DEVNULL)
        assert sha(root/'result/regions.json')==sha(work/'regions.json')
        a=np.load(root/'result/labels.npz');b=np.load(work/'labels.npz')
        for key in a.files:assert np.array_equal(a[key],b[key])
        traces=sorted((work/'traces').glob('*.gz'))
        for trace in traces:assert sha(trace)==sha(root/'result/traces'/trace.name)
        save(output,dict(generation_id=json.loads((work/'regions.json').read_text())['generation_id'],isolated_inputs=['tunable_detect.py','photo.jpg'],regions_json_sha256=sha(work/'regions.json'),exact_label_and_membership_arrays=True,byte_identical_traces=len(traces),status='passed'))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'photo2/output/detection-r263');ap.add_argument('--output',type=Path,default=ROOT/'photo2/review/r263/full-validation.json');ap.add_argument('--isolation',action='store_true');a=ap.parse_args();validate(a.work,a.output)
    if a.isolation:isolation(a.work,a.output.with_name('isolation.json'))
