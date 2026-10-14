"""Evaluation-only reviewed features, shape changes and crop-wide diagnostics.

These locations point at user-reviewed features in saved crops. They are never
imported by methods.py or run.py. They are not pixel truth or runtime bead labels.
"""
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import disk
from photo2.r282.common import read,save,pixels
from photo2.r282.phase1 import shape_metrics
from .run import OUT,summary

# Evaluation coordinates read from the already requested review images.
TARGETS={
 'two-sided': [('bottom-cyan-spike',[1259,324]),('left-red-crossing',[1235,312]),('right-yellow',[1277,302])],
 'duplicate':[('upper-good-black',[517,1582]),('lower-secondary',[515,1594]),('red-right-of-upper-black',[541,1601])],
 'abstention':[('bad-magenta',[1364,2971])]}


def native_shape(region):
    p=pixels(region)
    if not len(p):return dict(area=0,thin_fraction=0.,compactness=0.,solidity=0.,components=0)
    p=p-p.min(0)+2;m=np.zeros((p[:,1].max()+3,p[:,0].max()+3),bool);m[p[:,1],p[:,0]]=True
    return dict(**shape_metrics(m),thin_fraction=float((m&~ndi.binary_opening(m,structure=disk(2))).sum()/len(p)))


def main():
    results={};totals={m:dict(high=0,near=0,crossing=0,flanking_pairs=0,three_windows=0,high_black=0,high_pixels=0,spike_flagged_high=0,disconnected_high=0) for m in ['R283','A','B','C']};aggregate={m:[] for m in totals};targets={}
    for case in read(OUT/'cases.json'):
        n=case['name'];r=read(OUT/(n+'.json.gz'));results[n]={}
        for m in totals:
            rows=r['baseline'] if m=='R283' else r['methods'][m]['records'];high=[a for a in rows if a['status']=='high'];near=[a for a in high if a['centerline']['near']]
            t=totals[m];t['high']+=len(high);t['near']+=len(near);t['crossing']+=sum(a['centerline']['crosses'] for a in high);t['high_black']+=sum(a['color']=='black' for a in high)
            shapes=[native_shape(a['measured_support']) for a in high];t['high_pixels']+=sum(a['area'] for a in shapes);t['spike_flagged_high']+=sum(a['thin_fraction']>.03 for a in shapes);t['disconnected_high']+=sum(a['components']!=1 for a in shapes)
            aggregate[m]+=high
            s=summary(rows,[]) if m=='R283' else r['methods'][m]['summary']
            t['flanking_pairs']+=len(s['candidate_flanking_pairs']);t['three_windows']+=len(s['three_or_more_windows'])
            results[n][m]=dict(high=len(high),near=len(near),crossing=sum(a['centerline']['crosses'] for a in high),by_color=dict(Counter(a['color'] for a in near)))
        if n in TARGETS:
            targets[n]=[]
            for label,xy in TARGETS[n]:
                entry=dict(feature=label,evaluation_location=xy,methods={})
                for m in totals:
                    rows=r['baseline'] if m=='R283' else r['methods'][m]['records'];a=min(rows,key=lambda a:np.linalg.norm(np.array(a['seed'])-xy));distance=float(np.linalg.norm(np.array(a['seed'])-xy))
                    if distance>6:entry['methods'][m]=dict(found=False,nearest_distance=distance);continue
                    entry['methods'][m]=dict(found=True,id=a['record_id'],seed=a['seed'],status=a['status'],color=a['color'],shape=native_shape(a['measured_support']),centerline=a['centerline'],secondary_of=a.get('secondary_of'),notes=a['notes'])
                    if m=='R283':original=set(map(tuple,pixels(a['measured_support'])))
                    else:
                        now=set(map(tuple,pixels(a['measured_support'])));entry['methods'][m].update(removed_original_pixels=len(original-now),added_pixels=len(now-original))
                targets[n].append(entry)
    for m,rows in aggregate.items():
        totals[m]['by_color']={c:dict(high=sum(a['color']==c for a in rows),near=sum(a['color']==c and a['centerline']['near'] for a in rows),crossing=sum(a['color']==c and a['centerline']['crosses'] for a in rows)) for c in ('red','yellow','black')}
        shapes=[native_shape(a['measured_support']) for a in rows];totals[m]['mean_thin_fraction']=float(np.mean([s['thin_fraction'] for s in shapes]));totals[m]['median_compactness']=float(np.median([s['compactness'] for s in shapes]));totals[m]['median_solidity']=float(np.median([s['solidity'] for s in shapes]))
    save(OUT/'evaluation.json',dict(scope='Eight reviewed crops; all totals are candidate observations. Reviewed point roles do not define pixel truth.',totals=totals,cases=results,reviewed_features=targets))
    print(totals)

if __name__=='__main__':main()
