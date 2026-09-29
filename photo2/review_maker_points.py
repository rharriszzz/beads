"""Show retained R149 starts, including a feasible B start missed by selection.

This is an evaluator/review view. It does not select or refit using G.
"""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fit_maker_points import ROOT, PATCH, grid
from local_surface_fit import trace
from check_local_surface_fit import render
from check_placement import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'photo2/review/r149/report.json')
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/r149')
    args = parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    report = json.loads(args.report.read_text())
    a = next(c for c in report['results']['photo'] if c['family']=='A' and c['hand']==1)
    b = next(c for c in report['results']['photo'] if c['family']=='B' and c['hand']==-1)
    for case in (a,b):
        case['mapping'] = {int(n):index for n,index in case['mapping'].items()}
    states = [(a,a['selected'],'A'), (b,b['seed_results'][0],'B1'), (b,b['seed_results'][1],'B2')]
    points = {int(n):xy for n,xy in report['photo_points'].items()}
    raw = ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    colors = plt.get_cmap('tab10')(np.arange(len(PATCH)))
    crop = a['crop']; x0,y0,x1,y1 = crop
    xy,shape = grid(crop,1)
    fig,axes = plt.subplots(1,4,figsize=(16,5.5),constrained_layout=True)
    for ax in axes:
        ax.imshow(raw); ax.set_xlim(x0,x1); ax.set_ylim(y1,y0)
        for n,color in zip(PATCH,colors):
            x,y=points[n]
            ax.scatter(x,y,c=[color],s=22,marker='x' if n==23 else 'o')
            ax.text(x+2,y-3,str(n)+(' G' if n==23 else ''),color='white',fontsize=9,
                    bbox=dict(facecolor='black',alpha=.65,pad=1))
        ax.set_xlabel('Source x (pixels)'); ax.set_ylabel('Source y (pixels)')
    axes[0].set_title('Raw photo + maker points\nC=20, B=22, G=23')
    for ax,(case,state,title) in zip(axes[1:],states):
        labels,_,_ = trace(state['parameters'],xy,case['hand'])
        labels=labels.reshape(shape)
        for n,color in zip(PATCH,colors):
            if (labels==case['mapping'][n]).any():
                ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==case['mapping'][n],
                           levels=[.5],colors=[color],linewidths=1.2,linestyles='--')
        ax.set_title(f"{title}: training {state['training_correct']}/6\n"
                     f"G {'passes' if state['ownership']['23']['correct'] else 'misses'}; dashed = proposal")
    fig.savefig(args.report.with_name('candidate-range.png'),dpi=160); plt.close(fig)
    # Separately validate the retained B2, since main renderer checks B1 only.
    actual, provenance = render(b['seed_results'][1]['parameters'],-1,crop,args.output,'photo-B-second-start')
    predicted,_,unfinished = trace(b['seed_results'][1]['parameters'],xy,-1)
    mismatch=int(np.sum(actual!=predicted.reshape(shape)))
    check=dict(mismatches=mismatch,pixels=actual.size,fraction=mismatch/actual.size,
               unfinished_ray_pairs=unfinished,**provenance)
    if check['fraction']>=.001: raise AssertionError(check)
    # Small question: C's proposed boundary, with raw crop kept beside all starts.
    qcrop=[int(points[20][0]-34),int(points[20][1]-35),
           int(points[20][0]+37),int(points[20][1]+39)]
    qxy,qshape=grid(qcrop,1);qx0,qy0,qx1,qy1=qcrop
    fig,axes=plt.subplots(1,4,figsize=(12,3.5),constrained_layout=True)
    for ax in axes:
        ax.imshow(raw);ax.set_xlim(qx0,qx1);ax.set_ylim(qy1,qy0)
        ax.scatter(*points[20],c='white',s=18)
        ax.text(points[20][0]+2,points[20][1]-3,'20 = C',color='white',fontsize=9,
                bbox=dict(facecolor='black',alpha=.65,pad=1))
    axes[0].set_title('Raw C neighborhood')
    for ax,(case,state,title) in zip(axes[1:],states):
        labels,_,_=trace(state['parameters'],qxy,case['hand'])
        mask=labels.reshape(qshape)==case['mapping'][20]
        ax.contour(np.arange(qx0,qx1),np.arange(qy0,qy1),mask,levels=[.5],colors=['cyan'],linestyles='--')
        ax.set_title(title+' — proposed C outline')
    fig.savefig(args.report.with_name('c-question.png'),dpi=180);plt.close(fig)
    result=dict(report_sha256=sha(args.report),reviewer_sha256=sha(Path(__file__)),
                B_second_start_independent_check=check,
                selection='Show training-selected A and both retained training-feasible B starts; no G-based refitting',
                figures={name:sha(args.report.with_name(name)) for name in ('candidate-range.png','c-question.png')})
    args.report.with_name('review-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
