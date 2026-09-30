"""Score frozen R156 poses on provisional R157 positive interiors only.

No refitting, silhouettes, negative/background labels or loop acceptance is
implied. Known synthetic ID interiors calibrate the ownership measurement.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as Polygon
from scipy.ndimage import distance_transform_edt
from curved_surface_fit import trace
from check_curved_patch import render
from check_placement import ROOT,sha

NUMBERS=[8,11,14,17,20]


def route_samples(loop,spacing=.5):
    """Equal arc-length samples, preserving fractional source coordinates."""
    loop=np.asarray(loop,float)
    if not np.allclose(loop[0],loop[-1]):raise ValueError('Interior route is not closed')
    lengths=np.linalg.norm(np.diff(loop,axis=0),axis=1)
    distance=np.r_[0,np.cumsum(lengths)]
    positions=np.arange(0,distance[-1],spacing)
    return np.column_stack([np.interp(positions,distance,loop[:,axis]) for axis in [0,1]])


def photo_samples(loop_report):
    samples={}
    for result in loop_report['results']:
        n=result['number'];loop=np.array(result['loop_xy'])
        lo=np.floor(loop.min(axis=0)).astype(int);hi=np.ceil(loop.max(axis=0)).astype(int)+1
        yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]]
        xy=np.column_stack((xx.ravel(),yy.ravel()))
        core=xy[Polygon(loop).contains_points(xy)]
        assert len(core)==result['enclosed_pixels'],(n,len(core),result['enclosed_pixels'])
        samples[n]=dict(core=core,route=route_samples(loop),loop=loop)
    assert sorted(samples)==NUMBERS
    return samples


def score(p,hand,focal,mapping,samples):
    beads=[]
    for n,sample in samples.items():
        metrics=dict(number=int(n),expected_relative_index=int(mapping[n-1]))
        for kind in ['core','route']:
            xy=sample[kind]
            owner,_,unfinished,_=trace(np.array(p),xy,hand,focal=focal)
            passed=owner==mapping[n-1]
            labels,counts=np.unique(owner[~passed],return_counts=True)
            metrics[kind]=dict(total=len(xy),passed=int(passed.sum()),fraction=float(passed.mean()),
                unfinished_ray_pairs=unfinished,
                other_owners={str(int(i)):int(c) for i,c in zip(labels,counts)},
                missed_xy=xy[~passed].tolist())
        beads.append(metrics)
    return dict(beads=beads,mean_core_fraction=float(np.mean([b['core']['fraction'] for b in beads])),
        mean_route_fraction=float(np.mean([b['route']['fraction'] for b in beads])),
        complete_cores=sum(b['core']['passed']==b['core']['total'] for b in beads),
        complete_routes=sum(b['route']['passed']==b['route']['total'] for b in beads))


def synthetic_samples(fits,out):
    truth=fits['synthetic_truth'];crop=truth['crop']
    labels,provenance=render(truth['parameters'],truth['hand'],crop,out,'synthetic-interiors')
    samples={};geometry=[]
    for n in NUMBERS:
        index=fits['mappings']['A'][n-1]
        mask=distance_transform_edt(labels==index)>=4
        y,x=np.where(mask);xy=np.column_stack((x+crop[0],y+crop[1]))
        assert len(xy)>0,n
        fig,ax=plt.subplots();routes=ax.contour(mask.astype(float),levels=[.5]).allsegs[0];plt.close(fig)
        loop=max(routes,key=len)+np.array(crop[:2])
        samples[n]=dict(core=xy,route=route_samples(loop),loop=loop)
        geometry.append(dict(number=n,core_pixels=len(xy),loop_xy=loop.tolist()))
    return samples,dict(assistance='Exact evaluator-only POV ID masks, inset 4 pixels; not an HSV detector',
        parameters=truth['parameters'],hand=truth['hand'],crop=crop,geometry=geometry,**provenance)


def plot(ax,rgb,sample,title,misses=None):
    center=np.mean(sample['loop'],axis=0);x,y=np.rint(center).astype(int)
    crop=[x-23,y-26,x+24,y+27];x0,y0,x1,y1=crop
    ax.imshow(rgb[y0:y1,x0:x1],extent=[x0-.5,x1-.5,y1-.5,y0-.5],interpolation='nearest')
    ax.set_xlim(x0,x1);ax.set_ylim(y1,y0);ax.set_title(title,fontsize=9)
    if misses is not None:
        loop=sample['loop'];ax.plot(loop[:,0],loop[:,1],color='lime',lw=1)
        core=np.array(misses['core']['missed_xy']);route=np.array(misses['route']['missed_xy'])
        if len(core):ax.scatter(core[:,0],core[:,1],s=4,color='orange',alpha=.7)
        if len(route):ax.scatter(route[:,0],route[:,1],s=9,marker='x',color='red',linewidths=.7)
    ax.set_xlabel('source x');ax.set_ylabel('source y')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r159')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    fit_path=ROOT/'photo2/review/r156/report.json';loop_path=ROOT/'photo2/review/r157/report.json'
    fits=json.loads(fit_path.read_text());loops=json.loads(loop_path.read_text())
    photo=photo_samples(loops)
    synthetic,provenance=synthetic_samples(fits,ROOT/'photo2/output/r159')
    cases=[]
    for case_index,c in enumerate(fits['cases']):
        for rank,r in enumerate(c['retained']):
            samples=photo if c['dataset']=='photo' else synthetic
            result=score(r['parameters'],c['hand'],c['focal'],fits['mappings'][c['family']],samples)
            result.update(case_index=case_index,retained_index=rank,dataset=c['dataset'],family=c['family'],
                hand=c['hand'],focal=c['focal'],q_fixed=c['q_fixed'],parameters=r['parameters'],
                old_training_pass=r['training_pass'],old_heldout_pass=r['heldout_pass'])
            cases.append(result)
    truth=score(fits['synthetic_truth']['parameters'],1,None,fits['mappings']['A'],synthetic)
    assert truth['complete_cores']==5 and truth['complete_routes']==5,truth
    report=dict(fit_sha256=sha(fit_path),loop_sha256=sha(loop_path),script_sha256=sha(Path(__file__)),
        kernel_sha256=sha(ROOT/'photo2/curved_surface_fit.py'),image_sha256=sha(ROOT/'beads-photo-2.jpg'),
        source_sha256=sha(ROOT/'beads.pov'),synthetic_checker_sha256=sha(ROOT/'photo2/check_curved_patch.py'),
        loop_acceptance='Q157.1 unanswered; conditional diagnostic only',
        procedure='Frozen poses; equal arc-length route spacing 0.5 pixels and every enclosed integer pixel; per-bead equal weight; no outside loss',
        observation_ids={str(r['number']):r['observation_id'] for r in loops['results']},
        photo_counts={str(n):dict(core=len(s['core']),route=len(s['route'])) for n,s in photo.items()},
        synthetic=provenance,synthetic_truth_score=truth,cases=cases)
    # Full routine ray samples remain reproducible but ignored. Track all
    # aggregate scores plus complete miss coordinates for the four raw reviews.
    detail=ROOT/'photo2/output/r159/full-scores.json'
    detail.write_text(json.dumps(report,indent=2)+'\n')
    curated=json.loads(json.dumps(report))
    for c in curated['cases']:
        if c['case_index'] in [4,7]:continue
        for bead in c['beads']:
            for kind in ['core','route']:
                missed=bead[kind].pop('missed_xy')
                bead[kind]['missed_count']=len(missed)
                bead[kind]['first_miss_xy']=missed[0] if missed else None
    curated['full_sample_details']=dict(path='photo2/output/r159/full-scores.json',sha256=sha(detail),
        reproduction='Run score_interior_poses.py; all omitted miss coordinates remain here.')
    (args.output/'report.json').write_text(json.dumps(curated,indent=2)+'\n')
    # Original candidate ranks are retained; no selection by held-out scores.
    chosen=[next(c for c in cases if c['case_index']==i and c['retained_index']==j)
            for i,j in [(4,0),(4,1),(4,2),(7,0)]]
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    fig,axs=plt.subplots(5,5,figsize=(14,13),constrained_layout=True)
    for row,n in enumerate(NUMBERS):
        plot(axs[row,0],rgb,photo[n],f'Raw bead {n}')
        for col,(name,c) in enumerate(zip(['A1','A2','A3','B1'],chosen),1):
            metric=next(b for b in c['beads'] if b['number']==n)
            plot(axs[row,col],rgb,photo[n],f'{name}: core {metric["core"]["passed"]}/{metric["core"]["total"]}',metric)
    fig.suptitle('Frozen-pose comparison on interior samples only; no bead boundary is drawn.\nGreen: same provisional loop. Orange: misowned core pixel. Red x: misowned line sample.',fontsize=11)
    fig.savefig(args.output/'interior-ownership.png',dpi=150);plt.close(fig)
    # Small review focuses on a numerical failure, without moving the loop.
    # Focus on the body where B's coverage exceeds even the best saved A pose
    # most. This selects only the question crop, never the loop or a fit.
    focus=max(NUMBERS,key=lambda n:next(b for b in chosen[-1]['beads'] if b['number']==n)['core']['fraction']-
        max(next(b for b in c['beads'] if b['number']==n)['core']['fraction'] for c in chosen[:-1]))
    fig,axs=plt.subplots(1,5,figsize=(14,3.5),constrained_layout=True)
    plot(axs[0],rgb,photo[focus],f'Raw bead {focus}')
    for ax,name,c in zip(axs[1:],['A1','A2','A3','B1'],chosen):
        metric=next(b for b in c['beads'] if b['number']==focus)
        plot(ax,rgb,photo[focus],f'{name}: interior coverage {metric["core"]["fraction"]:.0%}',metric)
    fig.suptitle(f'Q159.1: do the green loop and orange locations remain inside bead {focus}?\nOrange/red mean the model assigns another owner, not that the photo location is wrong.',fontsize=10)
    fig.savefig(args.output/'question.png',dpi=170);plt.close(fig)
    (args.output/'review-provenance.json').write_text(json.dumps(dict(report_sha256=sha(args.output/'report.json'),
        reviewer_sha256=sha(Path(__file__)),focus_number=focus,
        focus_rule='Maximum B versus best saved A per-body core-coverage gap; question selection only',
        displayed_case_ranks=[[4,0],[4,1],[4,2],[7,0]]),indent=2)+'\n')
    print(json.dumps([dict(dataset=c['dataset'],family=c['family'],hand=c['hand'],focal=c['focal'],
        q_fixed=c['q_fixed'],rank=c['retained_index'],core=c['mean_core_fraction'],route=c['mean_route_fraction'],
        complete_cores=c['complete_cores'],complete_routes=c['complete_routes']) for c in cases],indent=2))


if __name__=='__main__':main()
