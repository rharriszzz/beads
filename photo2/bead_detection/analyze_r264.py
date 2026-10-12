"""Post-detection measurements and diagnostic crops; coordinates never enter growth."""
import csv
import gzip
import json
from collections import defaultdict
import numpy as np
from PIL import Image, ImageOps
from matplotlib.colors import rgb_to_hsv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .bounded_detect import ROOT, save, sha, measure
from .hue_r264 import HUES, WORK, OUT

CASES = [
    ('R00956', [2233,1863,2314,1944]),
    ('R01284', [944,2628,1025,2709]),
    ('pair', [445,635,520,706]),
    ('R01307', [1888,2699,1969,2780]),
    ('top-transition', [1210,235,1350,335]),
    ('inner-transition', [1510,1410,1650,1530]),
    ('largest-shift', [900,1535,970,1600]),
    ('paper-risk', [1975,2605,2045,2675]),
    ('yellow-shift', [1370,2000,1445,2060]),
]


def points(r):
    return {(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)}


def coordinate(rows):
    xy = np.array(rows, dtype=int)
    x0,y0 = xy.min(axis=0); x1,y1 = xy.max(axis=0)
    mask = np.zeros((y1-y0+1,x1-x0+1),bool)
    mask[xy[:,1]-y0,xy[:,0]-x0] = True
    return measure(mask,int(x0),int(y0))


def leaf_control(trace, p):
    """Diagnostic only: retain otherwise-pruned bright tree leaves if their
    parent survives and they exceed the parent's original retreat threshold.
    No new pixels, tree edges, ownership or detector decisions are introduced.
    This is a sensitivity control, NOT a proposed corrected retreat algorithm.
    """
    a=trace['accepted']; parents={r[2] for r in a if r[2]>=0}
    keep=[r[7] for r in a]; restored=[]; peak=a[0][3]
    dark_parents={s[2] for s in trace['stops'] if s[7]=='dark-frontier'}
    for i,r in enumerate(a):
        parent=r[2]
        if i in parents or r[7] or parent<0 or not a[parent][7] or i in dark_parents:
            continue
        low=trace['retreat_floor_dn'][parent]
        if r[3] > low+max(p['retreat_dn'],p['retreat_fraction']*(peak-low)):
            keep[i]=True;restored.append(i)
    return coordinate([r[:2] for i,r in enumerate(a) if keep[i]]), restored


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    hsv=rgb_to_hsv(rgb.astype(float)/255); hsv[:,:,0]*=360
    datasets={}; summaries=[]; leafrows=[]; pairs=[]
    for hue in HUES:
        ds=json.loads((WORK/str(hue)/'regions.json').read_text())
        ds.pop('maxima');datasets[hue]=ds
        rows=ds['regions']; members=defaultdict(list); sets={r['id']:points(r) for r in rows}
        for rid,ps in sets.items():
            for xy in ps:members[xy].append(rid)
        intersections=defaultdict(int)
        for ids in members.values():
            for i,a in enumerate(ids):
                for b in ids[i+1:]:intersections[tuple(sorted((a,b)))]+=1
        near=[]
        for (a,b),n in intersections.items():
            iou=n/len(sets[a]|sets[b]);smaller=n/min(len(sets[a]),len(sets[b]))
            pair=dict(hue=hue,a=a,b=b,intersection=n,iou=iou,smaller_fraction=smaller)
            pairs.append(pair)
            if iou>.5:near.append(pair)
        # Connected components quantify redundant support hypotheses, not beads.
        parent={r['id']:r['id'] for r in rows}
        def find(a):
            while parent[a]!=a:a=parent[a]
            return a
        for p in near:parent[find(p['a'])]=find(p['b'])
        groups=defaultdict(list)
        for rid in parent:groups[find(rid)].append(rid)
        groups=[v for v in groups.values() if len(v)>1]
        summary=json.loads((OUT/str(hue)/'summary.json').read_text())
        summary.update(high_iou_pairs=len(near),high_iou_regions=sum(map(len,groups)),
                       high_iou_components=len(groups),high_iou_excess=sum(len(v)-1 for v in groups))
        save(OUT/str(hue)/'overlap-groups.json',groups)
        leaf_h=[]
        for r in rows:
            with gzip.open(WORK/str(hue)/r['trace_file'],'rt') as f:t=json.load(f)
            control,restored=leaf_control(t,ds['parameters'])
            pre=coordinate([a[:2] for a in t['accepted']])
            row=dict(hue=hue,id=r['id'],location=r['location'],control_location=control['location'],
                     restored_leaves=len(restored),coordinate_shift=float(np.linalg.norm(np.array(control['location'])-r['location'])),
                     centroid_shift=float(np.linalg.norm(np.array(control['centroid'])-r['centroid'])),
                     pre_retreat_location=pre['location'],total_retreat_coordinate_shift=float(np.linalg.norm(np.array(pre['location'])-r['location'])))
            leaf_h.append(row)
        leafrows.extend(leaf_h)
        summary['leaf_control']=dict(affected_supports=sum(r['restored_leaves']>0 for r in leaf_h),
            changed_coordinates=sum(r['coordinate_shift']>0 for r in leaf_h),max_coordinate_shift=max(r['coordinate_shift'] for r in leaf_h),
            median_coordinate_shift=float(np.median([r['coordinate_shift'] for r in leaf_h])),
            max_centroid_shift=max(r['centroid_shift'] for r in leaf_h))
        summaries.append(summary)
    baseline={r['id']:r for r in datasets[10]['regions']}
    shifts=[]
    for hue in HUES:
        current={r['id']:r for r in datasets[hue]['regions']}
        for rid in sorted(baseline.keys() | current.keys()):
            a=baseline.get(rid); b=current.get(rid)
            shifts.append(dict(hue=hue,id=rid,status='common' if a and b else 'added' if b else 'lost',
                shift=float(np.linalg.norm(np.array(a['location'])-b['location'])) if a and b else None))
        vals=[r['shift'] for r in shifts if r['hue']==hue and r['shift'] is not None]
        s=next(s for s in summaries if s['parameters']['hue_stop_deg']==hue)
        s['coordinate_vs_10']=dict(common=len(vals),median=float(np.median(vals)),p90=float(np.percentile(vals,90)),max=max(vals),
                                  above_5=sum(v>5 for v in vals),added=len(current.keys()-baseline.keys()),lost=len(baseline.keys()-current.keys()))
    cases=[]
    for name,box in CASES:
        x0,y0,x1,y1=box
        local={}
        for hue,ds in datasets.items():
            local[hue]=[r for r in ds['regions'] if r['bbox'][0]<x1 and r['bbox'][2]>x0 and r['bbox'][1]<y1 and r['bbox'][3]>y0]
            for r in local[hue]:
                vals=np.array([hsv[y,x] for x,y in points(r)])
                anchor=hsv[r['location'][1],r['location'][0],0]
                delta=(vals[:,0]-anchor+180)%360-180
                r['hsv_diagnostic']=dict(at_location=hsv[r['location'][1],r['location'][0]].tolist(),
                    hue_relative_p10_p90=np.percentile(delta,[10,90]).tolist(),
                    saturation_p10_p90=np.percentile(vals[:,1],[10,90]).tolist(),value_p10_p90=np.percentile(vals[:,2],[10,90]).tolist())
        cases.append(dict(name=name,box=box,runs=local))
        fig,axes=plt.subplots(2,4,figsize=(16,8))
        for ax,label in zip(axes.flat,['Original',*HUES,'Coordinates / HSV']):
            if isinstance(label,str) and label!='Original':
                ax.axis('off');ax.text(.02,.98,'Cyan: retained support\nWhite +: supported coordinate\n\nAll panels: identical native crop\nNo interpolation or photo alteration\n\nHue in degrees; S/V in 0–1\nHover / select in simple viewer\nfor native HSV and coordinates\n\nSupports are not bead identities.',va='top',fontsize=12);continue
            ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest')
            if label!='Original':
                for r in local[label]:
                    for c in r['contours']:
                        c=np.array(c);ax.plot(c[:,0],c[:,1],color='cyan',lw=.65)
                    ax.plot(*r['location'],'+',color='white',ms=6)
            ax.set(xlim=(x0-.5,x1-.5),ylim=(y1-.5,y0-.5),title=name+' · '+(label if label=='Original' else str(label)+'°'))
            ax.tick_params(labelsize=8)
        fig.tight_layout();fig.savefig(OUT/(name+'.png'),dpi=130);plt.close(fig)
    save(OUT/'comparison.json',dict(source_sha256=sha(ROOT/'beads-photo-2.jpg'),hues=list(HUES),cases=cases))
    save(OUT/'metrics.json',summaries);save(OUT/'overlap-pairs.json',pairs)
    save(OUT/'coordinate-changes.json',shifts);save(OUT/'leaf-control.json',leafrows)
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
