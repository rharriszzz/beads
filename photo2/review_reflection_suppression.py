"""R169: compare deferred reflection suppression with the committed R167 baseline.

Display coordinates and maker cores are evaluator-only. Both detectors and their
graphs finish before reading any maker labels or confirmed-core coordinates.
The baseline module is the pinned, previously reviewed local Git source.
"""
import argparse,hashlib,json,os,subprocess,types
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as Polygon
from matplotlib.colors import rgb_to_hsv
from scipy import ndimage as ndi
import auto_label_beads as current
from review_auto_labels import graph_summary

ROOT=Path(__file__).resolve().parents[1]
BASELINE='3a74cdfefc401fe4d74b509152ce76268635cee0'


def before_result(image):
    source=subprocess.check_output(['git','show',BASELINE+':photo2/auto_label_beads.py'],cwd=ROOT)
    digest=hashlib.sha256(source).hexdigest()
    assert digest=='99af3a42cfcc6673934cf207623f46094167d763f69f564494d2ac0fc7843da1'
    module=types.ModuleType('r167_committed_detector')
    module.__file__=str(ROOT/'photo2/auto_label_beads.py')
    exec(compile(source,module.__file__+'@'+BASELINE,'exec'),module.__dict__)
    result=module.detect(image);graph=module.adjacency(result)
    return result,graph,digest


def point_key(point):return tuple(point['source_xy'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,default=ROOT/'photo2/output/r169/context-first')
    p.add_argument('--validation',type=Path,default=ROOT/'photo2/manual-labels-r169.json')
    p.add_argument('--calibration',type=Path,default=ROOT/'photo2/output/r169/calibration/report.json')
    p.add_argument('--output',type=Path,default=ROOT/'photo2/review/r169')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    before,graph,baseline_sha=before_result(np.array(image))
    after=json.loads((args.run/'report.json').read_text())
    assert after['script_sha256']==current.sha(ROOT/'photo2/auto_label_beads.py')
    assert after['image_sha256']==current.sha(ROOT/'beads-photo-2.jpg')
    # All detection/adjacency decisions have finished; only now load maker data.
    doc=json.loads(args.validation.read_text())
    evaluation=current.evaluate(before,graph,args.validation,after['image_sha256'])
    cores=json.loads((ROOT/'photo2/review/r157/report.json').read_text())
    core_ownership={str(b['number']):dict(
        before=[dict(source_xy=q['source_xy'],kind=q['kind']) for q in before['points'] if Polygon(b['loop_xy']).contains_point(q['source_xy'])],
        after=[dict(source_xy=q['source_xy'],kind=q['kind']) for q in after['observations'] if Polygon(b['loop_xy']).contains_point(q['source_xy'])]) for b in cores['results']}
    old_keys=set(map(point_key,before['points']));new_keys=set(map(point_key,after['observations']))
    added=[q for q in after['observations'] if point_key(q) not in old_keys]
    removed=[q for q in before['points'] if point_key(q) not in new_keys]
    matches={m['number']:m for m in after['manual_evaluation']['matches']}
    target=after['observations'][matches[10]['automatic_point']]
    target14=core_ownership['14']['after'][0]
    ann=json.loads((args.run/'annotations.json').read_text())
    targets={name:dict(**q,stable_id=next(a['id'] for a in ann['annotations'] if [a['x'],a['y']]==q['source_xy'])) for name,q in [('P',target),('R',target14)]}
    v=rgb_to_hsv(before['rgb'])[:,:,2];d=before['diameter']
    response=ndi.gaussian_filter(v,max(.65,min(1.5,d*.08)))-ndi.gaussian_filter(v,d*.40)
    xy=np.round((np.array(target14['source_xy'])+.5)*before['scale']-.5).astype(int)
    x,y=xy;radius=max(2,int(d*.4));yy,xx=np.mgrid[y-radius:y+radius+1,x-radius:x+radius+1]
    k=np.unravel_index(response[yy,xx].argmax(),yy.shape)
    competing_xy=((np.array([xx[k],yy[k]])+.5)/before['scale']-.5).tolist()
    suppression=dict(analysis_peak_xy=xy.tolist(),radius_analysis_pixels=radius,
        restored_response=float(response[y,x]),competing_response=float(response[yy[k],xx[k]]),
        competing_source_xy=competing_xy,
        meaning='A brighter colored-highlight flank enters the old pixel maximum filter; it is not a black-bead boundary.')
    fig,axes=plt.subplots(1,3,figsize=(12,5),constrained_layout=True)
    crop=(1240,245,1350,330)
    for ax,title in zip(axes,['Raw photo and maker numbers','Before: black reflection R missing','After: P and R restored']):
        ax.imshow(image);ax.set_xlim(crop[0],crop[2]);ax.set_ylim(crop[3],crop[1]);ax.axis('off');ax.set_title(title,fontsize=11)
        for number in [10,11,14,16,17]:
            a=next(a for a in doc['annotations'] if a['number']==number)
            ax.text(a['x']+3,a['y']+4,str(number),color='white',fontsize=9,bbox=dict(facecolor='black',alpha=.65,pad=.2))
    for ax,points in [(axes[1],before['points']),(axes[2],after['observations'])]:
        for q in points:
            x,y=q['source_xy']
            if crop[0]<x<crop[2] and crop[1]<y<crop[3]:ax.plot(x,y,'+',color='lime' if q['kind']=='chromatic' else 'cyan',ms=7)
    for name,q,offset in [('P',target,(-15,-18)),('R',target14,(16,-17))]:
        x,y=q['source_xy'];dx,dy=offset
        axes[2].annotate(name,(x,y),xytext=(x+dx,y+dy),color='cyan',fontsize=13,
            bbox=dict(facecolor='black',alpha=.75,pad=.4),arrowprops=dict(arrowstyle='->',color='cyan',lw=1.2))
    axes[1].annotate('colored flank',competing_xy,xytext=(competing_xy[0]-20,competing_xy[1]+30),
        color='orange',fontsize=8,arrowprops=dict(arrowstyle='->',color='orange'))
    fig.savefig(args.output/'recovered-black.png',dpi=170);plt.close(fig)
    # Compare the entire maker patch without assuming proximity proves identity.
    fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
    crop=(1130,160,1910,520)
    for ax,points,title in [(axes[0],before['points'],'Before: 58/76 nearby associations'),
        (axes[1],after['observations'],'After: 63/76 nearby associations')]:
        ax.imshow(image);ax.set_xlim(crop[0],crop[2]);ax.set_ylim(crop[3],crop[1]);ax.axis('off');ax.set_title(title)
        for q in points:
            x,y=q['source_xy']
            if crop[0]<x<crop[2] and crop[1]<y<crop[3]:ax.plot(x,y,'+',color='lime' if q['kind']=='chromatic' else 'cyan',ms=4)
    fig.savefig(args.output/'patch-comparison.png',dpi=160);plt.close(fig)
    calibration=json.loads(args.calibration.read_text())
    old_calibration=json.loads((ROOT/'photo2/review/r167/summary.json').read_text())['calibration']
    summary=dict(image_sha256=after['image_sha256'],baseline_commit=BASELINE,baseline_detector_sha256=baseline_sha,
        detector_sha256=after['script_sha256'],review_script_sha256=current.sha(Path(__file__)),
        calibration_script_sha256=calibration['script_sha256'],annotation_sha256=current.sha(args.validation),
        annotation_revision=doc['revision'],parameters=after['parameters'],before_inventory=dict(points=len(before['points']),links=len(graph['edges'])),
        after_inventory=after['inventory'],added_proposals=len(added),removed_proposals=len(removed),
        retained_source_positions=len(old_keys&new_keys),targets=targets,suppression=suppression,
        maker_confirmed_core_ownership=core_ownership,
        before_evaluation=evaluation,after_evaluation=after['manual_evaluation'],graph_after=graph_summary(after),
        calibration_before=old_calibration,
        calibration_after=[{k:v for k,v in q.items() if k not in ('point_body_ids','relations','eligible_missed')} for q in calibration['cases']],
        caveat='Proposals and proximity associations are not complete body identities, unit steps, physical centers, outward anchors or helicity.',
        curated_image_sha256={q.name:current.sha(q) for q in sorted(args.output.glob('*.png'))})
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(added=len(added),removed=len(removed),before_associated=evaluation['matched_within_gate'],
        after_associated=after['manual_evaluation']['matched_within_gate'],restored_core14=target14,
        targets={k:v['source_xy'] for k,v in targets.items()},graph_after=summary['graph_after']),indent=2))


if __name__=='__main__':main()
