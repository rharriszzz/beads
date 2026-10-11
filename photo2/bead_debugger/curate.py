"""Small reproducible evidence package for the working program, not a new audit."""
import json,collections,shutil,platform
from importlib.metadata import version
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .generate import ROOT,sha,save

def main():
    generated=ROOT/'photo2/output/debugger/generated';out=ROOT/'photo2/review/r256';out.mkdir(parents=True,exist_ok=True)
    inv=json.loads((generated/'observations.json').read_text());spl=json.loads((generated/'splines.json').read_text());ref=json.loads((ROOT/'photo2/review/r255/historical-splines.json').read_text())
    metrics={k:dict(shape=list(np.array(spl['raw'][k]).shape),maximum_absolute_coordinate_difference_px=float(np.max(np.abs(np.array(spl['raw'][k])-np.array(ref[k]))))) for k in ['inner_spline','outer_spline','inner_spline_control','outer_spline_control','centerline_spline']}
    from .models import model_version,IDS
    from tangent_circles import SplineRope,View
    seed=json.loads((ROOT/'photo2/spline-seed-r175.json').read_text());old=SplineRope(seed['points'],View(),smoothing=2)
    diff=np.array(spl['centerline'])-old.seed_image_curve[::4]
    metrics['periodic_centerline']=dict(maximum_absolute_coordinate_difference_px=float(abs(diff).max()),rms_euclidean_difference_px=float(np.sqrt(np.mean(np.sum(diff**2,axis=1)))),tolerance_px=.001)
    counts=collections.Counter(r['evidence_class'] for r in inv['observations'])
    doc=dict(request='R256',environment=dict(python=platform.python_version(),packages={name:version(name) for name in ['numpy','scipy','Pillow','matplotlib','playwright']}),generation=json.loads((generated/'manifest.json').read_text()),counts=dict(counts),palette=inv['palette']['groups'],spline_regression=metrics,
             legacy_models={mid:dict(version=model_version(mid)[0]) for mid in IDS},
             independent_fit='staged, not performed',precision_recall='not established; counts are proposals, not physical beads',
             tests=dict(python='10 tests',javascript='coordinate/navigation/triple/collision contracts',browser='see browser-verification.json'))
    save(out/'regeneration.json',doc)
    observations={r['id']:r for r in inv['observations']}
    # Select illustrative routes using new-image evidence only, no historical site coordinates.
    candidates=[p for p in inv['split_pairs'] if all(observations[id]['patch_area']>=35 for id in [p['a'],p['b']]) and 14<np.linalg.norm(np.diff(p['endpoints'],axis=0))<35]
    pairs=[min(candidates,key=lambda p:abs(p['valley_fraction']-.3)),min(candidates,key=lambda p:abs(p['valley_fraction']-.03))]
    photo=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);questions=[]
    for i,p in enumerate(pairs,1):
        c=np.mean(p['endpoints'],axis=0).astype(int);box=[int(c[0]-55),int(c[1]-45),int(c[0]+55),int(c[1]+45)];raw=photo.crop(box).resize((550,450),Image.Resampling.NEAREST)
        im=Image.new('RGB',(1100,510),'#14202c');im.paste(raw,(0,60));im.paste(raw,(550,60));d=ImageDraw.Draw(im);d.text((12,8),f'R256 Q{i}: raw / new detector interiors; measured valley {p["valley_fraction"]*100:.1f}%',font=font,fill='white');d.text((12,33),'Two separate visible colored bodies, one body, or cannot determine?',font=font,fill='white')
        for label,id in zip(['A','B'],[p['a'],p['b']]):
            r=observations[id];x=550+(r['x']-box[0])*5;y=60+(r['y']-box[1])*5;d.ellipse((x-9,y-9,x+9,y+9),outline='cyan',width=3);d.text((x+11,y-12),label,font=font,fill='white',stroke_width=2,stroke_fill='black')
        im.save(out/f'question-{i}.png',icc_profile=None)
        questions.append(dict(question=f'Q{i}',image=f'question-{i}.png',box=box,observation_ids=[p['a'],p['b']],valley_fraction=p['valley_fraction'],credible_split_evidence=p['credible_split_evidence'],answer=None))
    answers=json.loads((out/'answers.json').read_text()) if (out/'answers.json').exists() else []
    for question in questions:
        match=next((a for a in answers if a['observation_ids']==question['observation_ids']),None)
        if match:question['answer']=match['answer'];question['answer_source']='answers.json'
    save(out/'questions.json',questions)
    smoke=ROOT/'photo2/output/debugger/smoke'
    for src,dst in [('whole.png','viewer-whole.png'),('review.png','viewer-review.png'),('verification.json','browser-verification.json')]:
        if (smoke/src).exists():shutil.copy2(smoke/src,out/dst)
    save(out/'artifact-hashes.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ['.png','.json'] and p.name!='artifact-hashes.json'})
if __name__=='__main__':main()
