"""Summarize completed trials, with native masks and explicit duplicate evidence."""
import csv
import gzip
import itertools
import json
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .tunable_detect import ROOT, save, sha


def points(r):
    return {(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)}


def main():
    out=ROOT/'photo2/review/r263';s=json.loads((out/'search.json').read_text())
    trials=s['trials']
    if (out/'sensitivity.json').exists():trials+=json.loads((out/'sensitivity.json').read_text())['trials']
    if (out/'adaptive.json').exists():trials+=json.loads((out/'adaptive.json').read_text())['trials']
    base=json.loads((ROOT/'photo2/output/detection-r262/regions.json').read_text())
    baseline={r['id']:r for r in base['regions']};comparisons=[]
    for t in trials:
        path=ROOT/t['work'];d=json.loads((path/'regions.json').read_text());regions=d['regions']
        memberships={};intersections=Counter()
        for r in regions:
            for xy in points(r):
                for other in memberships.get(xy,[]):intersections[tuple(sorted([r['id'],other]))]+=1
                memberships.setdefault(xy,[]).append(r['id'])
        byid={r['id']:r for r in regions};pairs=[]
        for (a,b),n in intersections.items():
            pa,pb=byid[a]['pixel_count'],byid[b]['pixel_count']
            pairs.append(dict(a=a,b=b,intersection=n,iou=n/(pa+pb-n),fraction_of_smaller=n/min(pa,pb)))
        pairs.sort(key=lambda r:-r['iou'])
        save(out/(t['name']+'-overlaps.json'),pairs)
        common=set(baseline)&set(byid)
        shifts=[dict(id=k,shift_px=float(np.linalg.norm(np.array(byid[k]['centroid'])-baseline[k]['centroid'])),
                     pixels_before=baseline[k]['pixel_count'],pixels_after=byid[k]['pixel_count']) for k in common]
        shifts.sort(key=lambda r:(-r['shift_px'],r['id']))
        item=dict(trial=t['name'],regions=len(regions),same_id_regions=len(common),
             lost_ids=sorted(set(baseline)-set(byid)),added_ids=sorted(set(byid)-set(baseline)),
             dark_enclosed=t['summary']['dark_enclosed'],overlapping_regions=t['summary']['overlapping_regions'],
             pair_iou_over_half=sum(p['iou']>.5 for p in pairs),overlap_pairs=len(pairs),
             median_centroid_change_px=float(np.median([r['shift_px'] for r in shifts])) if shifts else None,
             largest_centroid_changes=shifts[:10])
        comparisons.append(item)
    save(out/'native-comparisons.json',comparisons)
    # Count profiles: all points are exact threshold evaluations, not interpolation.
    rows=list(csv.DictReader((out/'parameter-grid.csv').open()))
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for names,ax in [(('p10-b0','p20-b0','p40-b0','p80-b0'),axes[0]),(('p40-b0','p40-b1','p40-b2','p40-b4'),axes[1])]:
        for name in names:
            rr=[r for r in rows if r['trial']==name]
            if rr:ax.step([int(r['minimum_peak_dn']) for r in rr],[int(r['regions']) for r in rr],where='post',label=name)
        ax.axhspan(1500,1650,color='gray',alpha=.2,label='Provisional count target')
        ax.set(xlabel='Minimum peak brightness (0–255)',ylabel='Retained regions, NOT verified beads');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'count-profiles.png',dpi=160);plt.close(fig)
    # Native comparison of the motivating pair and automatically selected worst shift.
    available={t['name']:t for t in trials};names=[n for n in ('p10-b0','p40-b0','p40-b1','p40-b2','p40-b4') if n in available]
    datasets={n:json.loads((ROOT/available[n]['work']/'regions.json').read_text()) for n in names}
    cases=[('pair-32240-32353',(450,640,515,701))]
    high=next((c for name in ('p40-b4','p40-b2','p40-b1') for c in comparisons if c['trial']==name),None)
    if high and high['largest_centroid_changes']:
        r=baseline[high['largest_centroid_changes'][0]['id']];x,y=r['bright_patch']['peak']
        cases.append(('largest-centroid-change',(x-35,y-35,x+36,y+36)))
    # Prior failure coordinates enter ONLY post-search evaluation, never detection.
    oldpath=ROOT/'photo2/review/r260/regions.json.gz'
    if oldpath.exists():
        with gzip.open(oldpath,'rt') as f:old=json.load(f)
        for rid in ('R01307','R00956','R01284'):
            r=next((r for r in old['regions'] if r['id']==rid),None)
            if r:
                x,y=map(round,r['centroid']);cases.append((rid,(x-40,y-40,x+41,y+41)))
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    for label,box in cases:
        x0,y0,x1,y1=box;x0=max(0,x0);y0=max(0,y0);x1=min(rgb.shape[1],x1);y1=min(rgb.shape[0],y1)
        fig,axes=plt.subplots(1,len(names)+1,figsize=(3.5*(len(names)+1),3.8))
        for ax in axes:ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest');ax.set_xlim(x0-.5,x1-.5);ax.set_ylim(y1-.5,y0-.5)
        axes[0].set_title('Original native pixels')
        native={}
        for ax,name in zip(axes[1:],names):
            membership={};count=0
            for r in datasets[name]['regions']:
                subset={p for p in points(r) if x0<=p[0]<x1 and y0<=p[1]<y1}
                if not subset:continue
                count+=1
                for xy in subset:membership.setdefault(xy,[]).append(r['id'])
                for curve in r['contours']:
                    arr=np.array(curve);ax.plot(arr[:,0],arr[:,1],color='cyan',lw=.7)
                ax.plot(*r['centroid'],'+',color='white',ms=4)
            native[name]=membership;ax.set_title(name+'; '+str(count)+' intersecting supports')
        fig.tight_layout();fig.savefig(out/(label+'-native.png'),dpi=170);plt.close(fig)
        with (out/(label+'-native.csv')).open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(['x','y','r','g','b','value_dn']+names)
            for y in range(y0,y1):
                for x in range(x0,x1):writer.writerow([x,y,*map(int,rgb[y,x]),int(rgb[y,x].max())]+[';'.join(native[n].get((x,y),[])) for n in names])
    save(out/'manifest.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'manifest.json'})
    print(json.dumps([dict(trial=c['trial'],regions=c['regions'],dark=c['dark_enclosed'],overlap_half=c['pair_iou_over_half']) for c in comparisons],indent=2))

if __name__=='__main__':main()
