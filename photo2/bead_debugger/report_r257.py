"""Finalize numeric audit tables without changing fitted parameters or identities."""
from pathlib import Path
import json,csv
import numpy as np
from PIL import Image,ImageDraw
from .generate import ROOT,save,sha
from .lighting import OUT,evaluate,datasets,photo
from .surface import Scene


def run():
    lights=json.loads((OUT/'lighting.json').read_text());observed=json.loads((OUT/'observations.json').read_text());summary=[]
    for light in lights['lights']:
        rows=json.loads((OUT/f'{light["id"]}-predictions.json').read_text());train=[r for r in rows if r['split']=='train' and r.get('predicted_intensity',0)>0]
        gain=float(np.exp(np.median([np.log(r['observed_intensity']/r['predicted_intensity']) for r in train])))
        photometry={}
        for split in ['train','test']:
            rr=[r for r in rows if r['split']==split and r.get('predicted_intensity',0)>0]
            errors=[np.log(max(r['predicted_intensity']*gain,1e-9)/max(r['observed_intensity'],1e-9)) for r in rr]
            photometry[split]=dict(n=len(rr),log_intensity_rmse=float(np.sqrt(np.mean(np.array(errors)**2))),median_size_error_px=float(np.median([r['size_error_px'] for r in rr])),median_orientation_error_deg=float(np.median([r['orientation_error_deg'] for r in rr])))
        light['brightness_validation']=dict(shared_training_gain=gain,metrics=photometry);light['status']='FAILED precise heldout localization; diagnostic configuration only'
        light['uncertainty']='No calibrated lamp position or size. Poor geometry-conditioned predictions; parameters at bounds and local optimizer budgets are not confidence intervals.'
        summary.append(dict(light=light['id'],direction=light['direction'],extent=[light['width_deg'],light['height_deg']],roughness_deg=light['roughness_deg'],train=light['metrics']['train'],test=light['metrics']['test'],paper=light['shadow_metrics'],photometry=photometry))
    save(OUT/'lighting.json',lights);save(OUT/'metrics.json',summary)
    # Exact same PRIMARY directional light comparison, with consistent final lobe threshold.
    alt=json.loads((OUT/'alternative-geometries.json').read_text());primary=next(l for l in lights['lights'] if l['id']=='directional')
    for row in alt:
        scene=Scene(row['model_id']);data=datasets(scene,json.loads(json.dumps(observed['observations'])))
        _,row['fixed_primary_light_metrics']=evaluate(scene,data,primary)
        rr,metrics=evaluate(scene,data,row['light']);row['refitted_metrics']=metrics
        row['refit_protocol_note']='Same 3-parameter directional family, 4 starts, max32 evaluations, half-peak moments and paper residual weights. Correspondence/eligibility changes with geometry, so counts and conditional selection differ.'
        save(OUT/f'{scene.mid}-directional-predictions.json',rr)
    save(OUT/'alternative-geometries.json',alt)
    # Raw + disjoint predicted and observed shadow channels for the two sections.
    for name in ['straight','bend']:
        path=OUT/f'{name}-detail.json'
        if not path.exists():continue
        d=json.loads(path.read_text());box=d['box'];raw=Image.fromarray(photo()).crop(box);scale=3;width=max(350,raw.width*scale);height=raw.height*scale+48
        sheet=Image.new('RGB',(width*3,height),'#14212c');dr=ImageDraw.Draw(sheet)
        for j,title in enumerate(['Original pixels','Modeled cast shadow (purple)','Observed paper darkness (orange)']):
            tile=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST);sheet.paste(tile,(j*width,48));dr.text((j*width+5,8),title,fill='white')
        dr=ImageDraw.Draw(sheet,'RGBA')
        for x,y,val in d['background_shadows']:
            if val>.05:
                xx=width+(x-box[0])*scale;yy=48+(y-box[1])*scale;dr.rectangle((xx,yy,xx+3*scale,yy+3*scale),fill=(150,90,240,int(170*val)))
        for x,y,val in d['observed_background_deficit']:
            xx=width*2+(x-box[0])*scale;yy=48+(y-box[1])*scale;dr.rectangle((xx,yy,xx+8*scale,yy+8*scale),fill=(255,130,40,int(200*val)))
        sheet.save(OUT/f'{name}-shadows.png')
    from .models import model_version,IDS
    geometry_sources={}
    for mid in IDS:geometry_sources.update(model_version(mid)[1])
    save(OUT/'provenance.json',dict(image_sha256=sha(ROOT/'beads-photo-2.jpg'),inputs={**geometry_sources,**{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads.pov',ROOT/'photo2/spline-seed-r175.json',*[ROOT/f'photo2/review/r254/{mid}-camera.json' for mid in ['N2696_h+1_f0','N2674_h+1_f0','N2681_h-1_f0']]]}},implementation={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/bead_debugger').rglob('*')) if p.is_file() and p.suffix in ['.py','.mjs','.html','.css']},
         artifacts={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ['provenance.json','README.md']},
         units='Original JPEG integer pixel centers; world dimensions in source bead units, not calibrated millimeters'))

if __name__=='__main__':run()
