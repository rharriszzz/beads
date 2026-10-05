"""R229: show the actual pre-growth seed pixels of the frozen photo run."""
import argparse
import base64
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from auto_label_beads import ROOT, sha


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def paint(image, points, box):
    x0,y0,x1,y1 = box
    rgb = image[y0:y1,x0:x1].copy()
    visible = []
    for point in points:
        x,y = point['marker_xy']
        if x0 <= x < x1 and y0 <= y < y1:
            rgb[y-y0,x-x0] = point['display_rgb']
            visible.append(point)
    return rgb,visible


def closeups(image, points, contexts, out):
    font = ImageFont.truetype('DejaVuSans.ttf',18)
    small = ImageFont.truetype('DejaVuSans.ttf',16)
    rows = []
    canvas = Image.new('RGB',(1120,1560),'white')
    draw = ImageDraw.Draw(canvas)
    for index,context in enumerate(contexts):
        box = context['box']; x0,y0,x1,y1 = box
        raw = Image.fromarray(image[y0:y1,x0:x1])
        colored,visible = paint(image,points,box)
        display_height=round(560*(y1-y0)/(x1-x0))
        # All location guides are drawn after pixel enlargement, not in masks.
        right = Image.fromarray(colored).resize((560,display_height),Image.Resampling.NEAREST)
        seed = next(p for p in points if p['seed_number']==context['focus_seed'])
        sx = (seed['marker_xy'][0]-x0+.5)*560/(x1-x0)
        sy = (seed['marker_xy'][1]-y0+.5)*display_height/(y1-y0)
        rd = ImageDraw.Draw(right)
        rd.ellipse((sx-6,sy-6,sx+6,sy+6),outline='white',width=1)
        rd.text((sx+11,sy-25),context['name'],font=font,fill='white',stroke_width=2,stroke_fill='black')
        y=index*505
        draw.text((8,y+5),f"{context['name']}: raw photo",font=font,fill='black')
        draw.text((568,y+5),f"Step 2 only: {len(visible)} seed pixels",font=font,fill='black')
        draw.text((568,y+31),f"Target seed {seed['seed_number']} at {tuple(seed['marker_xy'])}",font=small,fill='black')
        canvas.paste(raw.resize((560,display_height),Image.Resampling.NEAREST),(0,y+60))
        canvas.paste(right,(560,y+60))
        rows.append(dict(**context,visible_seeds=[p['seed_number'] for p in visible],
                         focus_marker_xy=seed['marker_xy']))
    draw.text((8,1527),'Cyan: new diffuse-core seeds. Orange: older fallback seeds. Each square is ONE native pixel; white rings/letters are guides.',font=small,fill='black')
    canvas.save(out/'closeups.png')
    return rows


def whole(image, points, out):
    height,width=image.shape[:2]
    factor=650/height; panel_width=round(width*factor)
    raw=Image.fromarray(image).resize((panel_width,650),Image.Resampling.LANCZOS)
    shown=raw.copy(); draw=ImageDraw.Draw(shown)
    for point in points:
        x,y=point['marker_xy']; x=(x+.5)*factor; y=(y+.5)*factor
        draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),outline=tuple(point['display_rgb']),width=1)
    result=Image.new('RGB',(panel_width*2,733),'white'); draw=ImageDraw.Draw(result)
    font=ImageFont.truetype('DejaVuSans.ttf',17)
    result.paste(raw,(0,45));result.paste(shown,(panel_width,45))
    draw.text((8,8),'Raw whole necklace',fill='black',font=font)
    draw.text((panel_width+8,8),'Step 2: seed locations only',fill='black',font=font)
    draw.text((8,705),'Rings enlarged for visibility. Every actual seed occupies one native pixel.',fill='black',font=font)
    result.save(out/'whole-seeds.png')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r229')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    prior_path=ROOT/'photo2/review/r224/summary.json'
    prior=json.loads(prior_path.read_text())
    for p,v in prior['source_sha256'].items():assert sha(ROOT/p)==v,p
    for p,v in prior['curated_sha256'].items():assert sha(ROOT/'photo2/review/r224'/p)==v,p
    trace=json.loads((ROOT/'photo2/review/r224/trace.json').read_text())
    capture=ROOT/'photo2/output/r224/watershed.npz'
    assert sha(capture)==trace['capture']['watershed_archive_sha256']
    markers=np.load(capture)['markers']
    r218_path=ROOT/'photo2/review/r218/regions.json'
    r218=json.loads(r218_path.read_text())
    seal=json.loads((ROOT/'photo2/review/r218/summary.json').read_text())
    assert sha(r218_path)==seal['curated_sha256']['regions.json']
    raw_points=[dict(xy=r['seed_xy'],source=r['seed_source'],appearance_mode=r['appearance_mode']) for r in r218['records']]
    raw_points += [{k:r[k] for k in ('xy','source','appearance_mode')} for r in r218['excluded_refinement']]
    raw_points.sort(key=lambda p:(p['xy'][1],p['xy'][0],p['appearance_mode']))
    assert len(raw_points)==np.count_nonzero(markers)==markers.max()
    points=[]
    for ident,p in enumerate(raw_points,1):
        x,y=map(round,p['xy']);assert markers[y,x]==ident
        legacy=p['source']=='Uncovered R215 automatic seed'
        points.append(dict(seed_number=ident,seed_xy=p['xy'],marker_xy=[x,y],source=p['source'],
                           appearance_mode=p['appearance_mode'],display_rgb=[255,150,25] if legacy else [0,225,255],
                           kind='fallback' if legacy else 'diffuse',selected_native_pixels=1,
                           status='Step 2 proposal; not confirmed bead identity or visible center'))
    photo=ROOT/'beads-photo-2.jpg'
    image=np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'))
    assert image.shape[:2]==markers.shape
    assert Image.open(photo).getexif().get(274,1)==1
    contexts=[dict(name=c['letter'],box=c['crop'],focus_seed=c['region_number']) for c in trace['cases']]
    rows=closeups(image,points,contexts,out)
    whole(image,points,out)
    width,height=image.shape[1],image.shape[0]
    data=dict(photo_sha256=sha(photo),native_size=[width,height],seeds=points,
              contexts=[dict(name='Whole necklace',box=[0,0,width,height],focus_seed=None)]+contexts,
              native_seed_pixels=len(points),diffuse_seeds=sum(p['kind']=='diffuse' for p in points),
              fallback_seeds=sum(p['kind']=='fallback' for p in points),
              source_markers_archive_sha256=sha(capture),stage=2)
    save(out/'seeds.json',data)
    save(out/'review-locations.json',dict(rows=rows,selection='Same prior automatic crops, used only for display after extraction'))
    rectangles=''.join(f'<rect x="{p["marker_xy"][0]}" y="{p["marker_xy"][1]}" width="1" height="1" fill="rgb({",".join(map(str,p["display_rgb"]))})" data-seed="{p["seed_number"]}"/>' for p in points)
    initial=contexts[0]['box'];x0,y0,x1,y1=initial
    template=(ROOT/'photo2/step2_seed_viewer.html').read_text()
    payload=json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    html=(template.replace('__PHOTO__',base64.b64encode(photo.read_bytes()).decode())
          .replace('__SEEDS__',rectangles).replace('__VIEWBOX__',' '.join(map(str,[x0,y0,x1-x0,y1-y0])))
          .replace('__DATA__',payload))
    (out/'index.html').write_text(html)
    alias=ROOT/'photo2/review/r224/step2.html'
    alias.write_text(html)
    # Native stage 2 output is a label at each single seed pixel, never a face mask.
    routine=ROOT/'photo2/output/r229';routine.mkdir(parents=True,exist_ok=True)
    Image.fromarray(markers.astype(np.uint16)).save(routine/'seed-labels.tiff')
    sources=['beads-photo-2.jpg','photo2/refine_colored_masks.py','photo2/segment_colored_beads.py',
             'photo2/review_step2_seeds.py','photo2/step2_seed_viewer.html','photo2/review/r218/regions.json']
    payloads=['seeds.json','review-locations.json','closeups.png','whole-seeds.png','index.html']
    save(out/'summary.json',dict(request='R229',source_sha256={p:sha(ROOT/p) for p in sources},
        curated_sha256={p:sha(out/p) for p in payloads},existing_server_alias=str(alias.relative_to(ROOT)),
        alias_sha256=sha(alias),prior_summary_sha256=sha(prior_path),native_seed_pixels=len(points),
        pre_growth_seed_map_exact=True,prior_review_payloads_unchanged=True,segmentation_changed=False,
        reconstruction_fit_performed=False,manual_bead_data_read=False,
        reproduction='.venv/bin/python photo2/review_step2_seeds.py'))
    print(json.dumps({k:data[k] for k in ('native_seed_pixels','diffuse_seeds','fallback_seeds')},indent=2))


if __name__=='__main__':main()
