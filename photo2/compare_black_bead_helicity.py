#!/usr/bin/env python3
"""Compare both helicities using existing renders only, with colocated examples."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from black_bead_walk import ROOT, digest, font


def main():
    review=ROOT/'photo2/review/r084'
    output=ROOT/'photo2/output/black-bead-walk'
    summaries=[json.loads((review/sub/'angles-report.json').read_text()) for sub in ('','opposite')]
    rows=[]
    shapes=Image.new('RGB',(1200,8*220+65),'white')
    sd=ImageDraw.Draw(shapes)
    sd.text((12,10),'Colocated bead close-ups: +1 | −1 | pigment response overlap',font=font(23),fill='black')
    sd.text((12,38),'Overlap black; +1 only cyan; −1 only orange. Threshold 10/255, not an exact silhouette.',font=font(17),fill='black')
    overview=Image.new('RGB',(1200,8*285+55),'white')
    draw=ImageDraw.Draw(overview)
    draw.text((12,12),'Same black-bead position: helicity +1 versus −1',font=font(26),fill='black')
    html=['<!doctype html><meta charset="utf-8"><title>Black bead: opposite helicities</title>',
          '<style>body{font:18px system-ui;max-width:1250px;margin:2em auto}img{max-width:100%;height:auto}</style>',
          '<h1>One black bead: eight locations, both helicities</h1>',
          '<p>416 existing POV-Ray renders: 26 consecutive indices × eight locations × two helicities. '
          'Camera, light, material and bead geometry stay fixed. No extra comparison renders.</p>',
          '<p>The static examples use indices divisible by 13: the black bead has the same 3D '
          'position and orientation in both scenes. Neighbor winding is reversed, revealing changes '
          'to overlap and exposed edges. In the animations, the index matches, but most black-bead '
          'positions differ because the minor-circle phase reverses.</p>',
          '<p><a href="helicity-overview.png"><img src="helicity-overview.png"></a></p>',
          '<p><a href="angles.html">All +1 frames</a> · <a href="opposite/angles.html">All −1 frames</a></p>']
    for plus,minus in zip(summaries[0]['locations'],summaries[1]['locations']):
        assert plus['start']==minus['start']
        reports=[json.loads((review/sub/r['report']).read_text()) for sub,r in zip(('','opposite'),(plus,minus))]
        assert [r['helicity'] for r in reports]==[1,-1]
        boxes=[r['crop'] for r in reports]
        box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
        selected=((plus['start']+12)//13)*13
        assert selected<=plus['stop'] and selected%13==0
        crop_w,crop_h=box[2]-box[0],box[3]-box[1]
        scale=min(2.0,460/crop_w,225/crop_h)
        size=(round(crop_w*scale),round(crop_h*scale))
        y=55+plus['location']*285
        draw.text((12,y+8),f"{plus['nominal_angle']}° region\nIndex {selected}",font=font(20),fill='black')
        paths=[]
        for side,sub in enumerate(('','opposite')):
            scratch=output/sub
            if plus['location']:
                scratch=scratch/f"angle-{plus['nominal_angle']:03d}"
            paths.append(scratch)
            image=Image.open(scratch/f'black-{selected:03d}.png').convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST)
            x=220+side*490
            overview.paste(image,(x,y+35))
            draw.text((x,y+8),'Helicity +1' if side==0 else 'Helicity −1',font=font(19),fill='black')
        masks=[]
        targets=[]
        for scratch in paths:
            arrays=[np.asarray(Image.open(scratch/f'black-{i:03d}.png').convert('RGB')) for i in range(plus['start'],plus['stop']+1)]
            reference=np.maximum.reduce(arrays).astype(np.int16)
            target=arrays[selected-plus['start']]
            targets.append(target)
            masks.append((reference-target.astype(np.int16)).max(axis=2)>10)
        union=masks[0]|masks[1]
        yy,xx=np.nonzero(union)
        tight=(max(0,int(xx.min())-9),max(0,int(yy.min())-9),min(1200,int(xx.max())+10),min(900,int(yy.max())+10))
        overlap=np.full_like(targets[0],255)
        overlap[masks[0]&masks[1]]=[30,30,30]
        overlap[masks[0]&~masks[1]]=[0,180,215]
        overlap[masks[1]&~masks[0]]=[240,140,0]
        for col,array in enumerate(targets+[overlap]):
            crop=Image.fromarray(array).crop(tight)
            crop=crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST)
            crop.thumbnail((340,175),Image.Resampling.NEAREST)
            shapes.paste(crop,(160+col*345,65+plus['location']*220+28))
        sd.text((10,65+plus['location']*220+35),f"{plus['nominal_angle']}°\nIndex {selected}",font=font(18),fill='black')
        for col,label in enumerate(('Helicity +1','Helicity −1','Response overlap')):
            sd.text((160+col*345,65+plus['location']*220+3),label,font=font(18),fill='black')
        frames=[]
        for index in range(plus['start'],plus['stop']+1):
            frame=Image.new('RGB',(2*size[0]+12,size[1]+50),'white')
            fd=ImageDraw.Draw(frame)
            for side,scratch in enumerate(paths):
                crop=Image.open(scratch/f'black-{index:03d}.png').convert('RGB').crop(box).resize(size,Image.Resampling.NEAREST)
                x=side*(size[0]+12)
                frame.paste(crop,(x,50))
                fd.text((x+4,4),f"Index {index} · helicity {'+1' if side==0 else '−1'}",font=font(17),fill='black')
            frames.append(frame)
        name=f"paired-{plus['nominal_angle']:03d}.gif"
        frames[0].save(review/name,save_all=True,append_images=frames[1:],duration=650,loop=0,disposal=2)
        html.append(f"<h2>{plus['nominal_angle']}° region: indices {plus['start']}–{plus['stop']}</h2><img src=\"{name}\">")
        rows.append(dict(location=plus['location'],nominal_angle=plus['nominal_angle'],
                         colocated_index=selected,major_angle=360*selected/676,
                         crop=box,display_size=size,animation=name,
                         response_intersection_pixels=int((masks[0]&masks[1]).sum()),
                         response_union_pixels=int(union.sum()),
                         response_iou=float((masks[0]&masks[1]).sum()/union.sum()),
                         response_pixels_at_colocated_index=[r['frames'][selected-plus['start']]['response_pixels'] for r in reports]))
    overview.save(review/'helicity-overview.png')
    shapes.save(review/'helicity-shapes.png')
    html.insert(6,'<p><a href="helicity-shapes.png"><img src="helicity-shapes.png"></a></p>')
    (review/'helicity.html').write_text('\n'.join(html))
    report=dict(render_count=416,extra_comparison_renders=0,locations=rows,
                sources={str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
                inputs={name:digest(review/name) for name in ('angles-report.json','opposite/angles-report.json')},
                artifacts={name:digest(review/name) for name in ['helicity-overview.png','helicity-shapes.png','helicity.html']+[r['animation'] for r in rows]})
    (review/'helicity-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(rows,indent=2))


if __name__=='__main__':
    main()
