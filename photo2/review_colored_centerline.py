"""Curated R187 raw comparisons and independent ownership checks, no curve fit.

Display crops and selected question markers never feed detector/side decisions.
Rendered body IDs and maker interior polygons are evaluator-only.
"""
import argparse,json,os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as Polygon
import numpy as np
from PIL import Image,ImageOps

import auto_label_beads as auto
from colored_centerline_evidence import colored_subset,rim_candidates
from label_beads import atomic_json,LabelStore


def compare(image,points,targets,path,chain=None):
    xy=np.array([points[i-1]['source_xy'] for i in targets])
    display=np.array(chain['source_xy']) if chain else xy
    lo=display.min(axis=0)-55;hi=display.max(axis=0)+55
    crop=[float(lo[0]),float(lo[1]),float(hi[0]),float(hi[1])]
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax in axes:
        ax.imshow(image);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(hi[1],lo[1]);ax.axis('off')
    for letter,number in zip('ABC',targets):
        p=points[number-1];x,y=p['source_xy']
        for ax in axes:
            ax.annotate(letter,(x,y),xytext=(x+10,y-18),color='white',fontsize=12,
                        bbox=dict(facecolor='black',alpha=.8,pad=1),arrowprops=dict(arrowstyle='->',color='cyan',lw=.8))
        axes[1].plot(x,y,'+',color='lime',ms=8)
        axes[1].text(x-10,y+14,f'C{number}',color='white',fontsize=9,
                     bbox=dict(facecolor='black',alpha=.65,pad=1))
    if chain:
        axes[1].plot(display[:,0],display[:,1],'--',lw=1,color='dodgerblue')
    axes[0].set_title('Raw photo; arrows identify question locations')
    axes[1].set_title('Interior proposals'+(' and tentative diagonal series' if chain else '; no bead outlines'))
    fig.savefig(path,dpi=170);plt.close(fig)
    return dict(crop=crop,markers={letter:dict(points[n-1]) for letter,n in zip('ABC',targets)},chain=chain)


def calibration():
    folder=auto.ROOT/'photo2/output/r167/calibration';pending=[]
    for hand,palette,offset in [(1,0,0),(-1,0,0),(1,1,2)]:
        name=f'hand{hand:+d}-palette{palette}-shift{offset}'
        appearance=folder/(name+'.png')
        result=auto.detect(np.array(Image.open(appearance).convert('RGB')))
        graph=auto.adjacency(result);points,colored=colored_subset(result,graph)
        rims=rim_candidates(points,len(result['axis']['xy']),result['diameter'])
        pending.append((name,appearance,folder/(name+'-ids.png'),points,colored,rims))
    # Every image-derived proposal is finished before reading any ground-truth ID.
    checks=[]
    for name,appearance,ids,points,graph,rims in pending:
        rgb=np.array(Image.open(ids).convert('RGB')).astype(int);labels=rgb[:,:,0]+256*rgb[:,:,1]-1
        body=[int(labels[tuple(np.round(p['source_xy']).astype(int)[::-1])]) for p in points]
        rimbody=[body[p['observation_number']-1] for p in rims]
        deltas=[min((body[e['start']]-body[e['end']])%312,(body[e['end']]-body[e['start']])%312)
                if body[e['start']]>=0 and body[e['end']]>=0 else None for e in graph['edges']]
        checks.append(dict(fixture=name,appearance_sha256=auto.sha(appearance),ids_sha256=auto.sha(ids),
                           colored_proposals=len(points),on_paper=body.count(-1),
                           on_black=sum(b>=0 and b%3==2 for b in body),duplicates=len(body)-len(set(body)),
                           rim_proposals=len(rims),rim_on_paper=rimbody.count(-1),
                           rim_on_black=sum(b>=0 and b%3==2 for b in rimbody),
                           colored_links=len(deltas),true_unsigned_neighbors=sum(d in [1,6,7] for d in deltas),
                           limit='On-body ownership, not verified physical edge exposure, diagonal signs or centerline accuracy.'))
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,default=auto.ROOT/'photo2/output/r187/colored')
    parser.add_argument('--output',type=Path,default=auto.ROOT/'photo2/review/r187')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    report=json.loads((args.run/'report.json').read_text());points=report['points']
    assert report['image_sha256']==auto.sha(auto.ROOT/'beads-photo-2.jpg')
    image=ImageOps.exif_transpose(Image.open(auto.ROOT/'beads-photo-2.jpg')).convert('RGB')
    paths=[c for c in report['diagonal_chains'] if 'observation_numbers' in c]
    d2=max((c for c in paths if c['direction']=='d2'),key=lambda c:len(c['observation_numbers']))
    ownership=compare(image,points,d2['observation_numbers'][-3:],args.output/'interior-question.png')
    short=dict(d2,observation_numbers=d2['observation_numbers'][:3],source_xy=d2['source_xy'][:3])
    diagonal=compare(image,points,short['observation_numbers'],args.output/'diagonal-question.png',chain=short)
    # Whole-photo context: old curve is display-only, never a proposal input.
    seed=json.loads((auto.ROOT/'photo2/spline-seed-r175.json').read_text())
    fig,ax=plt.subplots(figsize=(10,12),layout='constrained');ax.imshow(image)
    old=np.array(seed['points']);ax.plot(old[:,0],old[:,1],'--',color='cyan',lw=.7,label='Old centerline: comparison only')
    xy=np.array([p['source_xy'] for p in points]);ax.scatter(xy[:,0],xy[:,1],s=3,color='lime',label='Colored interior proposals')
    rim=np.array([p['source_xy'] for p in report['rim_candidates']]);ax.scatter(rim[:,0],rim[:,1],s=14,facecolors='none',edgecolors='orange',lw=.6,label='Provisional near-envelope interiors')
    ax.legend(fontsize=9);ax.axis('off');ax.set_title('Image-derived colored evidence; no replacement centerline yet')
    fig.savefig(args.output/'whole-context.png',dpi=150);plt.close(fig)
    # Existing confirmed colored interiors test ownership only after selection.
    cores=json.loads((auto.ROOT/'photo2/review/r157/report.json').read_text())
    confirmed={n:[p['observation_number'] for p in points if Polygon(next(c for c in cores['results'] if c['number']==n)['loop_xy']).contains_point(p['source_xy'])] for n in [8,11,20]}
    opened=LabelStore(auto.ROOT/'beads-photo-2.jpg',None,args.run/'annotations.json').read()
    assert len(opened['annotations'])==len(points) and len(opened['series'])==len(report['adjacency']['edges'])
    checks=calibration()
    answer_path=auto.ROOT/'photo2/colored-review-answers-r188.json'
    answers=json.loads(answer_path.read_text()) if answer_path.exists() else None
    diagonal_path=auto.ROOT/'photo2/diagonal-confirmed-r189.json'
    diagonal_answer=json.loads(diagonal_path.read_text()) if diagonal_path.exists() else None
    # Track proposal observations/settings, keeping the editable full export ignored.
    atomic_json(args.output/'evidence.json',report)
    sources=['beads-photo-2.jpg','photo2/auto_label_beads.py','photo2/colored_centerline_evidence.py',
             'photo2/review_colored_centerline.py','photo2/test_colored_centerline_evidence.py',
             'photo2/spline-seed-r175.json','photo2/review/r157/report.json']
    if answers:sources.append(str(answer_path.relative_to(auto.ROOT)))
    if diagonal_answer:sources.append(str(diagonal_path.relative_to(auto.ROOT)))
    atomic_json(args.output/'summary.json',dict(request='R187',inventory=dict(colored=len(points),rim_candidates=len(report['rim_candidates']),
        diagonal_chains=len(paths),tentative_links=len(report['adjacency']['edges'])),parameters=report['parameters'],
        interior_question=ownership,diagonal_question=diagonal,confirmed_colored_core_proposals=confirmed,
        checks=checks,label_store_loaded=dict(points=len(opened['annotations']),series=len(opened['series'])),
        maker_review=answers,
        confirmed_diagonal=diagonal_answer,
        visual_concerns=[dict(observation_number=587,status='Ownership unresolved; suspected shaded-paper proposal, not a verified anchor.'),
                         dict(maker_number=20,status='No proposal inside its confirmed red core; full body coverage unresolved.')],
        source_sha256={p:auto.sha(auto.ROOT/p) for p in sources},
        curated_sha256={p.name:auto.sha(p) for p in sorted(args.output.glob('*.png'))},
        evidence_sha256=auto.sha(args.output/'evidence.json'),
        reproduction=['.venv/bin/python photo2/colored_centerline_evidence.py --output photo2/output/r187/colored',
                      '.venv/bin/python photo2/review_colored_centerline.py'],
        status='Candidate evidence only. Neither old axis nor near-envelope colored interiors establish a replacement physical centerline.'))
    print(dict(confirmed_colored_core_proposals=confirmed,checks=checks))


if __name__=='__main__':main()
