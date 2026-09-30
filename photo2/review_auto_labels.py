"""Curate raw/point/link comparisons and calibration summaries for R167.

Chosen display crops are diagnostic only, never automatic detector inputs.
"""
import argparse,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image,ImageOps
from auto_label_beads import sha

ROOT=Path(__file__).resolve().parents[1]


def graph_summary(report):
    points=report['observations'];edges=report['adjacency']['edges']
    adj={i:set() for i in range(len(points))}
    for e in edges:adj[e['start']].add(e['end']);adj[e['end']].add(e['start'])
    remaining=set(adj);components=[]
    while remaining:
        reached={min(remaining)};todo=list(reached)
        for i in todo:
            for j in adj[i]:
                if j not in reached:reached.add(j);todo.append(j)
        remaining-=reached;components.append(len(reached))
    return dict(components=len(components),component_sizes=sorted(components,reverse=True),
        isolated_observations=sum(k==1 for k in components),
        ambiguous_direction_choices=len(report['adjacency']['ambiguous_choices']),
        possible_skipped_step_links=len(report['adjacency']['possible_gaps']))


def context(image,report,crop,out,links=False,manual=None):
    fig,axes=plt.subplots(1,2,figsize=(12,6),constrained_layout=True)
    for ax in axes:
        ax.imshow(image);ax.set_xlim(crop[0],crop[2]);ax.set_ylim(crop[3],crop[1]);ax.axis('off')
    pts=report['observations'];inside=set()
    for i,p in enumerate(pts):
        x,y=p['source_xy']
        if crop[0]<x<crop[2] and crop[1]<y<crop[3]:
            inside.add(i);axes[1].plot(x,y,'+',color='lime' if p['kind']=='chromatic' else 'cyan',ms=6)
            if manual is None and not links:
                offsets={448:(-45,30),449:(35,20),450:(-10,-30)}
                if i+1 in offsets:
                    dx,dy=offsets[i+1]
                    axes[1].annotate(str(i+1),(x,y),xytext=(x+dx,y+dy),color='white',fontsize=11,
                        bbox=dict(facecolor='black',alpha=.8,pad=1),arrowprops=dict(arrowstyle='->',color='white',lw=1))
                elif min(np.linalg.norm(np.array([x,y])-pts[n-1]['source_xy']) for n in offsets)>55:
                    axes[1].text(x+3,y+3,str(i+1),color='white',fontsize=7,bbox=dict(facecolor='black',alpha=.55,pad=.3))
    if links:
        colors={'d1':'white','d2':'dodgerblue','d3':'orange'}
        for e in report['adjacency']['edges']:
            if e['start'] not in inside or e['end'] not in inside:continue
            xy=np.array([pts[e['start']]['source_xy'],pts[e['end']]['source_xy']])
            axes[1].plot(xy[:,0],xy[:,1],color=colors[e['direction']],lw=.9,alpha=.8)
    if manual:
        associated={q['number'] for q in report['manual_evaluation']['matches'] if q['automatic_point'] is not None}
        for p in manual['annotations']:
            for ax in axes:
                ax.text(p['x']+2,p['y']+2,str(p['number']),color='white' if p['number'] in associated else 'orange',
                    fontsize=7,bbox=dict(facecolor='black',alpha=.5,pad=.2))
    axes[0].set_title('Raw photo'+(' with maker observation numbers' if manual else ''))
    axes[1].set_title('Tentative links: d1 white, d2 blue, d3 orange' if links else 'Automatic points; no boundaries')
    fig.savefig(out,dpi=160);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,default=ROOT/'photo2/output/r167/automatic')
    p.add_argument('--calibration',type=Path,default=ROOT/'photo2/output/r167/calibration')
    p.add_argument('--output',type=Path,default=ROOT/'photo2/review/r167');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    report=json.loads((args.run/'report.json').read_text())
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    manual=json.loads((ROOT/'photo2/manual-labels-r167.json').read_text())
    context(image,report,(900,2000,1320,2270),args.output/'body-question.png')
    context(image,report,(900,2000,1320,2270),args.output/'adjacency-context.png',links=True)
    context(image,report,(1130,160,1770,450),args.output/'manual-comparison.png',manual=manual)
    with Image.open(args.run/'overview.png') as im:im.save(args.output/'whole-photo.png')
    calibration=json.loads((args.calibration/'report.json').read_text())
    cases=[]
    for q in calibration['cases']:
        cases.append({k:v for k,v in q.items() if k not in ('point_body_ids','relations','eligible_missed')})
    evaluation={k:v for k,v in report['manual_evaluation'].items() if k not in ('matches','relations')}
    evaluation.update(associated_relations=sum(q['endpoints_associated'] for q in report['manual_evaluation']['relations']),
        unmatched_maker_numbers=[q['number'] for q in report['manual_evaluation']['matches'] if q['automatic_point'] is None])
    summary=dict(image_sha256=report['image_sha256'],detector_sha256=report['script_sha256'],
        calibration_sha256=calibration['script_sha256'],review_script_sha256=sha(Path(__file__)),
        parameters=report['parameters'],inventory=report['inventory'],graph=graph_summary(report),
        manual_evaluation=evaluation,calibration=cases,
        question_observations={str(n):dict(**report['observations'][n-1],stable_id=json.loads((args.run/'annotations.json').read_text())['annotations'][n-1]['id']) for n in (448,449,450)},
        caveat=report['caveat'])
    fig,axes=plt.subplots(1,3,figsize=(12,4),constrained_layout=True)
    for ax,q in zip(axes,calibration['cases']):
        name=f'hand{q["hand"]:+d}-palette{q["palette"]}-shift{q["offset"]}'
        ax.imshow(Image.open(args.calibration/(name+'.png')));ax.axis('off')
        ax.set_title(f'Known hand {q["hand"]:+d}\n{q.get("eligible_located",0)}/{q.get("eligible_visible",0)} eligible bodies located')
    fig.savefig(args.output/'known-examples.png',dpi=160);plt.close(fig)
    summary['curated_image_sha256']={p.name:sha(p) for p in sorted(args.output.glob('*.png'))}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(inventory=summary['inventory'],graph=summary['graph'],manual_evaluation=evaluation),indent=2))


if __name__=='__main__':main()
