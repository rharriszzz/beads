"""A pure phase/registration example, selected using recorded development data."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from photo2.r305.forward import segments
from .model import scene

def run(out=ROOT/'photo2/r311/results/campaign'):
    out=Path(out);rows=[read(p) for p in (out/'trials').glob('*.gz')]
    base=next(r for r in rows if r['family']=='R306-2405' and r['kind']=='start')
    reference=base['first_errors'][0]['modal_fraction']
    pool=[r for r in rows if r['family']=='R306-2405' and r['feasible'] and r['kind']=='map' and r.get('pair')==['phase','s0'] and r['global_score']<=1.15*base['global_score'] and r['first_errors'][0]['modal_fraction']>=reference-.05]
    if not pool:return
    chosen=min(pool,key=lambda r:r['target_loss']);data,m,obs=load()
    crop=[1425,211,1675,341];photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');raw=photo.crop(crop)
    panels=[raw.copy()];titles=['Original photograph; unchanged pixels']
    # A one-pixel native context prevents the crop perimeter from becoming a
    # fictitious closed body edge. Drawing clips only the already computed edges.
    yy,xx=np.mgrid[crop[1]-1:crop[3]+1,crop[0]-1:crop[2]+1];xy=np.c_[xx.ravel(),yy.ravel()]
    for row,title in [(base,'R306 primary: native visible boundaries'),(chosen,f"Phase / registration trial {chosen['id']}")]:
        s=scene(row['parameters'],data,row['implementation']);tr=s.trace(xy);owners=tr['owner'].reshape(xx.shape);unknown=tr['unknown'].reshape(xx.shape)
        panel=raw.copy();draw=ImageDraw.Draw(panel)
        for j in np.unique(owners[owners>=0]):
            for a,b,c,d in segments((owners==j)&~unknown,crop[0]-1,crop[1]-1):draw.line((a-crop[0],b-crop[1],c-crop[0],d-crop[1]),fill='#00edff',width=1)
        panels.append(panel);titles.append(title)
    canvas=Image.new('RGB',(3*250,185),'#14222c');draw=ImageDraw.Draw(canvas)
    for i,(panel,title) in enumerate(zip(panels,titles)):
        canvas.paste(panel,(i*250,25));draw.text((i*250+5,6),title,fill='white')
    gain=100*(chosen['global_score']/base['global_score']-1)
    draw.text((5,161),f'Pure two-global change; full-necklace development score {gain:+.1f}% (positive = worse). No adoption.',fill='white')
    target=ROOT/'photo2/r311/evidence/phase-registration-example.png';canvas.resize((1500,370),Image.Resampling.NEAREST).save(target)
    raw.save(target.with_name('phase-registration-raw.png'))
    save(target.with_suffix('.json'),dict(baseline_trial=base['id'],after_trial=chosen['id'],crop=crop,
         whole_scene_occlusion=True,only_changed=['phase','s0'],before={k:base['parameters'][k] for k in ['phase','s0']},after={k:chosen['parameters'][k] for k in ['phase','s0']},
         global_score_before=base['global_score'],global_score_after=chosen['global_score'],before_targets=base['first_errors'],after_targets=chosen['first_errors'],
         trial_sha256=sha(out/'trials'/f"{chosen['id']:06d}.json.gz"),raw_exact=True,native_one_pixel_border_context=True,
         display_correction='An initial illustration incorrectly closed bodies at the crop perimeter. One-pixel context removes those cut edges; the earlier PNG is retained. Native coverage, trial vectors and all full-model science are unchanged.',
         policy='Development-selected illustrative pair, not finalist selection or a global photographic improvement. All N bodies render the crop.'))
    print('phase/registration figure trial',chosen['id'])
if __name__=='__main__':run()
