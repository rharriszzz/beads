"""Diagnostic omission of one failed cheap gate; never feeds inventory acceptance."""
from collections import Counter
import gzip,json,copy
import numpy as np
from PIL import Image,ImageOps
from scipy.spatial import cKDTree
from matplotlib.colors import rgb_to_hsv
from .experiment_r272 import ROOT,OUT,save,lines
from .brightness_r270 import color_managed_photo,linearize,SCALE,sums,Search
from .climb_r268 import background
from .search_r269 import Policy
from .inventory_r272 import features,build_region

CHEAP={'background-nearby','insufficient-light','uneven-light','small-bright-patch','window-dilution','weak-local-contrast','flat-maximum'}
def main():
    locations=[json.loads(s) for s in gzip.open(OUT/'location-candidates.jsonl.gz','rt')];data=json.load(open(OUT/'inventory.json'));summary=json.load(open(OUT/'summary.json'));palette=summary['palette']
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();native_hsv,paper,_=background(native);hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);q=np.rint(255*lum*SCALE).astype(np.int64);ss={n:sums(q,n) for n in (5,7,9)}
    tree=cKDTree([[r['x'],r['y']] for r in locations]);records=[];owners={(x,y):b['id'] for b in data['beads'] for y,a,z in b['region']['runs'] for x in range(a,z+1)}
    cohort=[r for r in locations if len(r['reasons'])==1 and r['reasons'][0] in CHEAP]
    for row in cohort:
        x,y=row['x'],row['y'];cut=np.s_[y-21:y+22,x-21:x+22];ends=[];remaining=[];graph=None
        if paper[y,x]:remaining.append('center-is-background-or-uncertain')
        for n in (5,7,9):
            g=Search(q[cut],native_hsv[cut],paper[cut],ss[n][cut],n,(21,21),'Y')
            if n==7:graph=g
            for radius in (10,16):
                for raw,mean in ((12,2),(24,2),(24,6)):
                    result=g.search(radius,Policy(raw,mean));endpoint=(g.xy[result['end']]+[x-21,y-21]).tolist();ends.append(endpoint)
                    if n==7 and radius==16 and raw==24 and mean==2:primary=endpoint
        endpoints=np.array(ends);spread=float(np.sqrt(((endpoints[:,None]-endpoints[None,:])**2).sum(axis=2)).max())
        if spread>3:remaining.append('unstable-location')
        if primary!=[x,y]:remaining.append('better-nearby-peak')
        if any(locations[j]['trusted'] for j in tree.query_ball_point([x,y],6)):remaining.append('nearby-location-conflict')
        caps,_=graph.widest(16,Policy(256,256),'mean');rivals=[]
        for j in tree.query_ball_point([x,y],16):
            r=locations[j];dist=np.hypot(r['x']-x,r['y']-y)
            if dist<4 or r['background_code'] or r['mean_y']<.9*row['mean_y']:continue
            ix=graph.index((r['x']-x+21,r['y']-y+21));saddle=float(caps[ix]/255)
            if saddle>=.75*min(row['mean_y'],r['mean_y']):rivals.append(r['id'])
        if rivals:remaining.append('competing-highlights')
        f=features(hsv,lum,paper,x,y);region=build_region(row,native,srgb,hsv,lum,paper,palette,f,locations);remaining.extend(region['reasons'])
        overlaps=sorted({owners[x,y] for y,a,b in region.get('region',{}).get('runs',[]) for x in range(a,b+1) if (x,y) in owners})
        if overlaps:remaining.append('ownership-overlap-with-inventory')
        records.append(dict(candidate_id=row['id'],anchor=[x,y],sole_cheap_failure=row['reasons'][0],original=row,endpoint_spread=spread,primary_endpoint=primary,rivals=rivals,other_failures=sorted(set(remaining)),overlaps=overlaps,provisional_region=region,passes_remaining_checks=not remaining,diagnostic_only=True))
    # Audit joint eligibility of the counterfactual cohort too; no forced ownership.
    eligible=[i for i,r in enumerate(records) if r['passes_remaining_checks']]
    if eligible:
        near=cKDTree([records[i]['anchor'] for i in eligible]).query_pairs(6)
        for a,b in near:
            for i in (eligible[a],eligible[b]):
                records[i]['passes_remaining_checks']=False
                if 'nearby-diagnostic-location-conflict' not in records[i]['other_failures']:records[i]['other_failures'].append('nearby-diagnostic-location-conflict')
    owner={};conflicts=set()
    for i,r in enumerate(records):
        if not r['passes_remaining_checks']:continue
        for y,a,b in r['provisional_region']['region']['runs']:
            for x in range(a,b+1):
                if (x,y) in owner:conflicts.update([i,owner[x,y]])
                else:owner[x,y]=i
    for i in conflicts:records[i]['passes_remaining_checks']=False;records[i]['other_failures'].append('ownership-overlap-with-other-diagnostic')
    lines('single-gate-diagnostics.jsonl.gz',records)
    counts=Counter(k for r in locations for k in r['reasons']);sole=Counter(r['sole_cheap_failure'] for r in records);otherwise=Counter(r['sole_cheap_failure'] for r in records if r['passes_remaining_checks'])
    region_records=[json.loads(s) for s in gzip.open(OUT/'region-candidates.jsonl.gz','rt')];region_counts=Counter(k for r in region_records for k in r['reasons']);region_sole=Counter(r['reasons'][0] for r in region_records if len(r['reasons'])==1)
    save('requirement-failures.json',dict(total_location_candidates=len(locations),location_failures=dict(counts),sole_cheap_failures=dict(sole),passes_remaining_detailed_checks=dict(otherwise),audited_single_failure_candidates=len(records),region_failures=dict(region_counts),sole_recorded_region_failures=dict(region_sole),caveat='Counts overlap. Image-edge cases lack other measurements. Sole cheap failures receive detailed path/color/region/overlap checks, with the failed screening gate omitted only for diagnosis. All remain excluded. Later region checks require a known color; unmeasurable later checks are not assumed passed.'))
    print((OUT/'requirement-failures.json').read_text())
if __name__=='__main__':main()
