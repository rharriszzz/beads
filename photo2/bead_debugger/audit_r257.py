"""Reproduce curated native crops, centroid tables and matched geometry checks."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .generate import ROOT,save,sha
from .surface import Scene,shade,highlight
from .detail import DetailService
from .lighting import OUT,photo,datasets,fit_model,evaluate,evaluate_shadows

FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)

def marked(rgb,d):
    box=d['box'];raw=Image.fromarray(rgb).crop(box);im=raw.convert('RGBA');overlay=Image.new('RGBA',im.size);dr=ImageDraw.Draw(overlay)
    def p(xy):return tuple(np.array(xy)-box[:2])
    selected=d['selected_generator_index']
    for x,y,k,*values in d['footprint']:
        if k==selected:dr.point(p([x,y]),fill=(66,190,240,100))
    im=Image.alpha_composite(im,overlay).convert('RGB');dr=ImageDraw.Draw(im)
    for b in d['beads']:
        x,y=p(b['center_xy']);dr.ellipse((x-3,y-3,x+3,y+3),outline='#50aaff',width=1);
        if b['generator_index']==selected:dr.text((x+5,y-14),str(b['legacy_k']),fill='#9bcaff',font=FONT,stroke_width=1,stroke_fill='#101010')
        x,y=p(b['outward']['xy']);col='#ffad66' if b['outward']['visible'] else '#777777';dr.line((x-3,y-3,x+3,y+3),fill=col);dr.line((x-3,y+3,x+3,y-3),fill=col)
        if b['centroid']:
            x,y=p(b['centroid']);dr.ellipse((x-2,y-2,x+2,y+2),fill='#65ff88')
        if b['highlight']:
            for hx,hy,intensity in b['highlight']['region']:
                if b['generator_index']==selected and intensity>.15:dr.point(p([hx,hy]),fill='#ff55d7')
            x,y=p(b['highlight']['centroid']);dr.line((x-4,y,x+4,y),fill='#ff55d7');dr.line((x,y-4,x,y+4),fill='#ff55d7')
    for o in d['observed_reflections']:
        x,y=p(o['xy']);dr.ellipse((x-4,y-4,x+4,y+4),outline='white')
    return raw,im


def curate(out=OUT):
    rgb=photo();service=DetailService(ROOT/'photo2/output/debugger');lights=service.lighting();scene=service.scene(lights['model_id']);origin=scene.config['origin'];n=scene.config['n']
    # Section geometry is used only to choose diagnostic views, never fit evidence.
    tangent=scene.g['tangent'];bend=np.linalg.norm(np.roll(tangent,8,axis=0)-np.roll(tangent,-8,axis=0),axis=1)
    available=np.flatnonzero((np.abs(np.arange(n)-origin)>250)&(scene.g['radial'][:,2]>.4))
    straight=int(available[np.argmin(bend[available])]);curved=int(available[np.argmax(bend[available])])
    sections=[('straight',straight),('bend',curved)];jobs=[(f'bead-{k}',(origin+k)%n) for k in range(8)]+sections
    records=[];centroids=[];panels=[]
    for name,gi in jobs:
        d=service.result(scene.mid,gi,lights['selected']);raw,im=marked(rgb,d)
        raw.save(out/f'{name}-raw.png');im.save(out/f'{name}-marked.png')
        zoom=3;panel=Image.new('RGB',(raw.width*zoom*2,raw.height*zoom+34),'#15202b');dr=ImageDraw.Draw(panel);dr.text((8,8),f'{name}: original native pixels (3x nearest) | footprint + modeled points; k={(gi-origin)%n}',font=FONT,fill='white');panel.paste(raw.resize((raw.width*zoom,raw.height*zoom),Image.Resampling.NEAREST),(0,34));panel.paste(im.resize((im.width*zoom,im.height*zoom),Image.Resampling.NEAREST),(raw.width*zoom,34));panel.save(out/f'{name}-comparison.png')
        save(out/f'{name}-detail.json',d);b=next(b for b in d['beads'] if b['generator_index']==gi)
        records.append(dict(name=name,generator_index=gi,k=(gi-origin)%n,curvature_proxy=float(bend[gi]),box=d['box'],bead=b))
        for row in d['beads']:
            for step,m in row['convergence'].items():centroids.append(dict(section=name,k=row['legacy_k'],generator_index=row['generator_index'],step=step,x=m['centroid'][0] if m['centroid'] else None,y=m['centroid'][1] if m['centroid'] else None,area_px2=m['area_px2'],delta_to_adaptive_px=m['distance_to_adaptive_px']))
        panels.append(panel);print(name,gi,'ready',flush=True)
    save(out/'sections.json',records)
    with (out/'centroid-convergence.csv').open('w') as f:
        w=csv.DictWriter(f,lineterminator='\n',fieldnames=list(centroids[0]));w.writeheader();w.writerows(centroids)
    # Whole-photo locator and evidence montage retain photographic source coordinates.
    locator=Image.fromarray(rgb).resize((635,796));dr=ImageDraw.Draw(locator)
    for r in records:
        if r['name'].startswith('bead-') and r['k']!=2:continue
        x0,y0,x1,y1=np.array(r['box'])/4;dr.rectangle((x0,y0,x1,y1),outline='white',width=2);dr.text((x0,y0-16),r['name'],fill='white',font=FONT)
    locator.save(out/'sections-locator.png')
    observations=json.loads((out/'observations.json').read_text())['observations'];rr=[o for o in observations if o.get('patch_owner_fraction',0)>=.8]
    sheet=Image.new('RGB',(8*128,int(np.ceil(len(rr)/8))*116),'#15202b');dr=ImageDraw.Draw(sheet)
    for i,o in enumerate(rr):
        x,y=np.round(o['xy']).astype(int);tile=Image.fromarray(rgb).crop((x-20,y-20,x+20,y+20)).resize((80,80),Image.Resampling.NEAREST);a=(i%8)*128;b=(i//8)*116;sheet.paste(tile,(a,b));dr.text((a,b+82),f'{x},{y} {o["split"]}',fill='white',font=FONT);dr.text((a,b+98),f'candidate {i+1}',fill='white',font=FONT)
    sheet.save(out/'reflection-evidence.png')
    q=dict(id='R257-Q1',image='bead-2-comparison.png',question='For bead 2, is the main problem the separate predicted patch beneath the red body, or a different location/index relationship?',status='optional; unanswered; not used to fit',answer=None)
    save(out/'questions.json',[q])
    # Angular quadrature uncertainty is tested at 3,5,9 nodes per side.
    from .lighting import datasets
    data=datasets(scene,observations);quad=[]
    for light in lights['lights']:
        for item in data[::8]:
            points={}
            for order in [3,5,9]:
                h=highlight(item['xy'],shade(scene,item,light,order=order)['specular']);points[str(order)]=h['centroid'] if h else None
            quad.append(dict(light=light['id'],observation=item['observation']['id'],centroids=points,
                             delta_3_9=float(np.linalg.norm(np.array(points['3'])-points['9'])) if points['3'] and points['9'] else None))
    save(out/'quadrature.json',quad)
    # Is a full 2x2 grid materially different from boundary-only supersampling?
    fine=[]
    for _,gi in jobs:
        d=service.result(scene.mid,gi,lights['selected']);b=next(b for b in d['beads'] if b['generator_index']==gi);box=scene.box([gi]);yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]];xy=np.c_[xx.ravel(),yy.ravel()];xy=(xy[:,None,:]+np.array([[-.25,-.25],[.25,-.25],[-.25,.25],[.25,.25]])).reshape(-1,2);hits=scene.camera(xy);keep=hits['owner']==gi
        from .surface import moments
        m=moments(xy[keep],np.ones(keep.sum()));fine.append(dict(generator_index=gi,full_2x2=m,delta_px=float(np.linalg.norm(np.array(m['centroid'])-b['centroid'])) if m and b['centroid'] else None))
    save(out/'supersampling.json',fine)


def alternatives(out=OUT):
    evidence=json.loads((out/'observations.json').read_text());lights=json.loads((out/'lighting.json').read_text());primary=next(l for l in lights['lights'] if l['id']=='directional');result=[]
    for mid in ['N2674_h+1_f0','N2681_h-1_f0']:
        scene=Scene(mid);obs=json.loads(json.dumps(evidence['observations']));data=datasets(scene,obs)
        same,metrics=evaluate(scene,data,primary);print(mid,'same illumination',metrics,flush=True)
        fit=fit_model(scene,data,'directional',evidence['shadows']);rows,newmetrics=evaluate(scene,data,fit);shadow=evaluate_shadows(scene,evidence['shadows'],fit)
        result.append(dict(model_id=mid,model_version=scene.version,light=fit,fixed_primary_light_metrics=metrics,refitted_metrics=newmetrics,shadows=shadow['metrics'],matched_observations=len(data),observations=obs))
        save(out/f'{mid}-directional-predictions.json',rows);print(mid,'refit',newmetrics,flush=True)
    save(out/'alternative-geometries.json',result)

def clean_panels(out=OUT):
    """One concept per panel; specifically replaces the rejected cluttered question."""
    from scipy.ndimage import binary_erosion
    d=json.loads((out/'bead-2-detail.json').read_text());b=next(b for b in d['beads'] if b['legacy_k']==2);box=d['box'];raw=Image.fromarray(photo()).crop(box);scale=4
    width=max(360,raw.width*scale);height=raw.height*scale+66
    def panel(title,point=None,outline=False,subtitle=''):
        tile=Image.new('RGB',(width,height),'#14212c');dr=ImageDraw.Draw(tile);dr.text((10,8),title,font=FONT,fill='white');dr.text((10,27),subtitle,font=FONT,fill='#c4d3de')
        image=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST);tile.paste(image,(0,58));dr=ImageDraw.Draw(tile)
        if outline:
            mask=np.zeros((raw.height,raw.width),bool)
            for x,y,k,*_ in d['footprint']:
                if k==d['selected_generator_index']:mask[y-box[1],x-box[0]]=True
            yy,xx=np.where(mask&~binary_erosion(mask))
            for x,y in zip(xx,yy):dr.rectangle((x*scale,y*scale+58,x*scale+scale-1,y*scale+58+scale-1),fill='#54e5fa')
        if point is not None:
            x=(point[0]-box[0])*scale;y=(point[1]-box[1])*scale+58;dr.ellipse((x-6,y-6,x+6,y+6),outline='#54e5fa',width=2)
        return tile
    first=panel('Original photograph',subtitle='No markers. Same pixels and crop in every panel.')
    second=panel('Only bead 2: predicted visible footprint',outline=True,subtitle='Cyan border = pixels the MODEL assigns to bead 2.')
    pair=Image.new('RGB',(width*2,height));pair.paste(first,(0,0));pair.paste(second,(width,0));pair.save(out/'bead-2-clean.png')
    panels=[first,second,panel('Physical center (3D center projected)',b['center_xy'],subtitle='A geometric reference; not necessarily a visible point.'),
            panel('Outermost minor-radial surface point',b['outward']['xy'],subtitle='Surface extremum; '+('visible' if b['outward']['visible'] else 'occluded')+' in this model.'),
            panel('Centroid of visible modeled pixel area',b['centroid'],subtitle='Average image location after first-hit occlusion.'),
            panel('Predicted reflection — uncertain lighting',b['highlight']['centroid'] if b['highlight'] else None,subtitle='Not an observed reflection.' if b['highlight'] else 'No supported predicted reflection for this bead.')]
    sheet=Image.new('RGB',(width*2,height*3));
    for i,p in enumerate(panels):sheet.paste(p,((i%2)*width,(i//2)*height))
    sheet.save(out/'bead-2-locations.png')
    save(out/'questions.json',[dict(id='R257-Q1',image='question-1-cluttered.png',question='Is the exposed patch beneath the red body the mismatch?',answer="The image was cluttered with markers that I don't understand.",interpretation='Presentation failure only; not confirmation of geometry, identity or mismatch.',replacement='bead-2-clean.png',status='Answered; no repeat question required for implementation')])


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--alternatives',action='store_true');a=ap.parse_args()

    if a.alternatives:alternatives()
    else:curate();clean_panels()
