#!/usr/bin/env python3
"""Reviewed image-only body observations and unresolved fragments for beads1.jpg."""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import html
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.segmentation import watershed, find_boundaries
import blind_generated as bg

ROOT=Path(__file__).resolve().parents[1]
PARAMETERS=dict(color_dominance=25,minimum_value=35,fill_highlight_holes_below=64,
                maximum_seed_snap_px=6.,watershed_compactness=.002,maximum_assignment_distance_px=28.,
                unresolved_component_min_pixels=6)
COLORS=['red','green','blue']


def color_support(rgb):
    ordered=np.sort(rgb.astype(float),axis=2)
    core=(ordered[:,:,2]-ordered[:,:,1]>PARAMETERS['color_dominance'])&(ordered[:,:,2]>=PARAMETERS['minimum_value'])
    mask=core.copy();components,_=ndi.label(~core);sizes=np.bincount(components.ravel())
    enclosed=sizes<=PARAMETERS['fill_highlight_holes_below']
    enclosed[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
    mask|=enclosed[components]
    channels=rgb.argmax(axis=2)+1
    if core.any():
        nearest=ndi.distance_transform_edt(~core,return_distances=False,return_indices=True)
        channels[mask&~core]=channels[tuple(nearest[:,mask&~core])]
    channels[~mask]=0
    return core,mask,channels


def segment(rgb,channels,records):
    labels=np.zeros(channels.shape,np.int32);value=ndi.gaussian_filter(rgb.max(axis=2)/255.,1.)
    occupied=set()
    for color_index,name in enumerate(COLORS,1):
        support=channels==color_index
        if not support.any():continue
        distance,nearest=ndi.distance_transform_edt(~support,return_indices=True)
        markers=np.zeros(channels.shape,np.int32)
        for row in records:
            if row['color']!=name:continue
            x,y=row['marker_xy'];d=float(distance[y,x]);ny,nx=nearest[:,y,x]
            if d>PARAMETERS['maximum_seed_snap_px']:
                row['mask_status']='no_nearby_color_support';row['seed_xy']=None;continue
            if (int(nx),int(ny)) in occupied:
                row['mask_status']='coincident_seed_unresolved';row['seed_xy']=None;continue
            occupied.add((int(nx),int(ny)));markers[ny,nx]=row['id']
            row['seed_xy']=[int(nx),int(ny)];row['seed_snap_px']=d;row['mask_status']='provisional_color_constrained_region'
        if markers.any():
            result=watershed(-value,markers,mask=support,compactness=PARAMETERS['watershed_compactness'])
            d=ndi.distance_transform_edt(markers==0)
            result[d>PARAMETERS['maximum_assignment_distance_px']]=0
            labels[result>0]=result[result>0]
    for row in records:
        ys,xs=np.nonzero(labels==row['id']);row['region_pixels']=int(len(xs))
        row['bbox_xyxy']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
    return labels


def coverage(mask,labels):
    unassigned=mask&(labels==0);components,n=ndi.label(unassigned);regions=[]
    for i,slices in enumerate(ndi.find_objects(components),1):
        if slices is None:continue
        sy,sx=slices;ys,xs=np.nonzero(components[sy,sx]==i)
        if len(xs)<PARAMETERS['unresolved_component_min_pixels']:continue
        regions.append(dict(id=f'U{len(regions)+1}',pixels=int(len(xs)),bbox_xyxy=[sx.start,sy.start,sx.stop,sy.stop],
                            marker_xy=[float(xs.mean()+sx.start),float(ys.mean()+sy.start)],status='unassigned_colored_region_not_a_bead_count'))
    return unassigned,regions


def marker_map(rgb,records,regions,box=None,scale=2):
    if box is None:box=(0,0,rgb.shape[1],rgb.shape[0])
    image=Image.fromarray(rgb).crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale))
    d=ImageDraw.Draw(image)
    for r in records:
        x,y=r['marker_xy']
        if not(box[0]<=x<box[2] and box[1]<=y<box[3]):continue
        px=(x-box[0])*scale;py=(y-box[1])*scale
        color='cyan' if r['status']=='reviewed_body' else '#ffb000'
        d.ellipse((px-5,py-5,px+5,py+5),outline='black',width=3)
        d.ellipse((px-4,py-4,px+4,py+4),outline=color,width=2)
        d.text((px+5,py-11),str(r['id']),font=bg.font(13),fill='white',stroke_width=2,stroke_fill='black')
    for r in regions:
        x,y=r['marker_xy']
        if box[0]<=x<box[2] and box[1]<=y<box[3]:
            px=(x-box[0])*scale;py=(y-box[1])*scale
            d.text((px,py),r['id'],font=bg.font(13),fill='#ff66ff',stroke_width=1,stroke_fill='black')
    return image


def gallery(path,rgb,records,regions,summary):
    encoded=base64.b64encode((ROOT/'beads1.jpg').read_bytes()).decode()
    parts=['<!doctype html><meta charset="utf-8"><title>beads1 visible inventory</title>',
           '<style>body{font:17px system-ui;max-width:1300px;margin:2em auto;padding:0 1em}svg,img{max-width:100%;height:auto}.body{stroke:#00ffff}.fragment{stroke:#ffb000}.mark{fill:transparent;stroke-width:1}.mark:hover{stroke:#fff;stroke-width:3}.id{font-size:7px;paint-order:stroke;stroke:black;stroke-width:1px;fill:white}button{margin:.4em}</style>',
           '<h1>beads1.jpg: reviewed visible observations</h1>',
           f'<p>{summary["reviewed_body_count"]} visually supported body observations; {summary["fragment_count"]} unresolved fragment observations; {summary["unassigned_regions"]} unassigned colored regions of at least 6 pixels. These are not a total bead count or recovered sequence. Masks are provisional.</p>',
           '<p>Hover markers for details. Cyan: supported body; orange: fragment whose separate identity is unresolved. IDs are observation IDs, not chain indices. Raw and full-image context are retained.</p>',
           '<label><input type="checkbox" checked onchange="document.querySelectorAll(\'.mark,.id\').forEach(x=>x.style.display=this.checked?\'\':\'none\')">Markers</label> <label><input type="checkbox" onchange="document.querySelectorAll(\'.id\').forEach(x=>x.style.visibility=this.checked?\'visible\':\'hidden\')">IDs</label>',
           f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
    for row in records:
        x,y=row['marker_xy'];kind='body' if row['status']=='reviewed_body' else 'fragment'
        title=f'{row["id"]}: {row["color"]}, {row["status"]}; {row["region_pixels"]} region pixels; mask {row["mask_status"]}'
        parts.append(f'<circle class="mark {kind}" cx="{x}" cy="{y}" r="3"><title>{html.escape(title)}</title></circle><text class="id" style="visibility:hidden" x="{x+3}" y="{y-3}">{row["id"]}</text>')
    for row in regions:
        x,y=row['marker_xy'];title=f'{row["id"]}: {row["pixels"]} unassigned colored pixels; not a bead count'
        parts.append(f'<circle class="mark" style="stroke:magenta" cx="{x}" cy="{y}" r="4"><title>{html.escape(title)}</title></circle>')
    parts.append('</svg><h2>Color-constrained regions</h2><p>Region boundaries can still disagree with bead outlines. Magenta marks unassigned colored pixels. Neutral cast shadow is outside this support.</p><img src="regions.png" alt="Provisional color constrained regions">')
    for name in ['T1','T2','T3','L','R','BL','BM','BR']:
        parts.append(f'<h2>{name}: reviewed crop</h2><img src="{name}-review.png" alt="Reviewed {name} crop">')
    parts.append('<h2>Slivers found in the coverage audit</h2><img src="slivers.png" alt="Eleven retained visible slivers"><p>Unresolved fragments can belong to bodies already represented. No independent bead count is assigned to them. See inventory.json for records and coverage regions, and the source annotation file for removals/additions.</p>')
    path.write_text('\n'.join(parts))


def draw_slivers(rgb,edits,path):
    chosen=[r for r in edits['added_fragments'] if 'coverage_region' in r]
    image=Image.new('RGB',(900,((len(chosen)+3)//4)*200),'white');draw=ImageDraw.Draw(image)
    source=Image.fromarray(rgb)
    for k,row in enumerate(chosen):
        x,y=row['xy'];box=(x-14,y-14,x+15,y+15);ox=(k%4)*225;oy=(k//4)*200
        image.paste(source.crop(box).resize((174,174)),(ox+20,oy+25))
        draw.text((ox+5,oy+4),f"{row['id']}: {row['color']} sliver",font=bg.font(15),fill='black')
        cx=ox+104;cy=oy+109;draw.ellipse((cx-6,cy-6,cx+6,cy+6),outline='#ffb000',width=2)
    image.save(path)


def draw_duplicate_review(rgb,old,records,path):
    box=(96,302,139,335);scale=6;w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale
    image=Image.new('RGB',(3*w,h+45),'white');draw=ImageDraw.Draw(image)
    for j,(title,rows) in enumerate([('Photo',[]),('Before: 211 + 217',[r for r in old if r['observation_id'] in [211,217]]),
                                   ('After: 217',[r for r in records if r['id']==217])]):
        image.paste(Image.fromarray(rgb).crop(box).resize((w,h)),(j*w,45))
        draw.text((j*w+5,12),title,font=bg.font(18),fill='black')
        for row in rows:
            x,y=row['marker_xy'];px=j*w+(x-box[0])*scale;py=45+(y-box[1])*scale
            draw.ellipse((px-5,py-5,px+5,py+5),outline='cyan',width=2)
            draw.text((px+7,py-7),str(row.get('id',row.get('observation_id'))),font=bg.font(16),fill='white',stroke_width=2,stroke_fill='black')
    image.save(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    edits_path=ROOT/'photo2/beads1-review-r068.json';edits=json.loads(edits_path.read_text())
    if bg.digest(ROOT/'beads1.jpg')!=edits['image_sha256'] or bg.digest(ROOT/'photo2/blind_generated.py')!=edits['baseline_source_sha256']:raise ValueError('Review inputs changed')
    rgb=np.asarray(Image.open(ROOT/'beads1.jpg').convert('RGB'))
    old_labels,xy,old_mask,hsv=bg.detect(rgb);old=bg.observations(rgb,old_labels,xy,old_mask,hsv,1)
    removed={r['id'] for r in edits['removed']};fragments=set(edits['fragment_ids']);records=[]
    for row in old:
        i=row['observation_id']
        if i in removed:continue
        records.append(dict(id=i,marker_xy=row['marker_xy'],color=row['color'],status='fragment_identity_unresolved' if i in fragments else 'reviewed_body',
                            provenance='R059 marker visually reviewed in R068',bead_index=None,physical_center_known=False))
    for row in edits['added_fragments']:
        records.append(dict(id=row['id'],marker_xy=row['xy'],color=row['color'],status=row['status'],note=row['note'],
                            provenance='R068 manual visible fragment',bead_index=None,physical_center_known=False))
    core,mask,channels=color_support(rgb);labels=segment(rgb,channels,records);unassigned,regions=coverage(mask,labels)
    for row in records:
        if row['status']!='reviewed_body':
            p=np.array(row['marker_xy'])
            row['nearby_body_ids_not_assignment']=[r['id'] for r in records if r['status']=='reviewed_body' and r['color']==row['color'] and np.linalg.norm(p-r['marker_xy'])<=20]
    reviewed=np.zeros(mask.shape,bool)
    for x0,y0,x1,y1 in edits['boxes'].values():reviewed[y0:y1,x0:x1]=True
    summary=dict(baseline_candidates=len(old),removed_markers=len(removed),reviewed_body_count=sum(r['status']=='reviewed_body' for r in records),
                 fragment_count=sum(r['status']!='reviewed_body' for r in records),added_fragments=len(edits['added_fragments']),
                 body_colors=dict(Counter(r['color'] for r in records if r['status']=='reviewed_body')),
                 fragment_colors=dict(Counter(r['color'] for r in records if r['status']!='reviewed_body')),
                 old_foreground_pixels=int(old_mask.sum()),color_support_pixels=int(mask.sum()),unassigned_color_pixels=int(unassigned.sum()),
                 unassigned_pixels_in_small_components=int(unassigned.sum()-sum(r['pixels'] for r in regions)),
                 unassigned_regions=len(regions),color_pixels_outside_review_boxes=int((mask&~reviewed).sum()),
                 records_without_region=sum(r['region_pixels']==0 for r in records),
                 complete_visible_bead_inventory_verified=False,pattern_status='not inferred')
    np.save(args.output/'labels.npy',labels);np.save(args.output/'color-support.npy',channels)
    inventory=dict(summary=summary,observations=records,removed=edits['removed'],unassigned_regions=regions,review_boxes=edits['boxes'],limitations=edits['limitations'])
    bg.write_json(args.review_bundle/'inventory.json',inventory)
    marker_map(rgb,records,regions).save(args.review_bundle/'overview.png')
    for name,box in edits['boxes'].items():marker_map(rgb,records,regions,box,4).save(args.review_bundle/f'{name}-review.png')
    draw_slivers(rgb,edits,args.review_bundle/'slivers.png')
    draw_duplicate_review(rgb,old,records,args.review_bundle/'duplicate-211-217.png')
    overlay=rgb.copy();overlay[find_boundaries(labels,mode='inner')]=[255,255,0];overlay[unassigned]=[255,0,255]
    Image.fromarray(overlay).resize((1600,1200)).save(args.review_bundle/'regions.png')
    gallery(args.review_bundle/'review.html',rgb,records,regions,summary)
    sources=[Path(__file__).resolve(),ROOT/'photo2/blind_generated.py',edits_path,ROOT/'beads1.jpg']
    test=ROOT/'photo2/test_beads1_inventory.py'
    if test.exists():sources.append(test)
    report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,sources={str(p.relative_to(ROOT)):bg.digest(p) for p in sources},summary=summary,
                artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},
                bulk_artifacts={p.name:bg.digest(p) for p in sorted(args.output.iterdir()) if p.suffix=='.npy'})
    bg.write_json(args.review_bundle/'report.json',report);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
