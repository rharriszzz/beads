#!/usr/bin/env python3
"""Image-only beads3 body/color review with R069 sliver selection."""
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
from skimage.morphology import disk
from skimage.segmentation import watershed, find_boundaries
import blind_generated as bg
import beads1_inventory as b1
import inventory_selection as selection

ROOT=Path(__file__).resolve().parents[1]
COLORS=['red','black','white']
PARAMETERS=dict(envelope_closing_radius=10,envelope_fill_holes_below=1500,red_dominance=40,red_minimum=45,black_value_max=95,
                fill_black_highlight_holes_below=64,maximum_seed_snap_px=6.,
                watershed_compactness=.03,black_seed_interior_radius=4,maximum_assignment_distance_px=28.)
SELECTION={**selection.PARAMETERS,'explicit_excluded_ids':[]}


def envelope_mask(base):
    mask=ndi.binary_closing(base,structure=disk(PARAMETERS['envelope_closing_radius']))
    components,_=ndi.label(~mask);sizes=np.bincount(components.ravel())
    fill=sizes<=PARAMETERS['envelope_fill_holes_below']
    fill[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
    return mask|fill[components]


def color_support(rgb,envelope):
    value=rgb.max(axis=2);red=(rgb[:,:,0].astype(int)-rgb[:,:,1:].max(axis=2).astype(int)>PARAMETERS['red_dominance'])&(rgb[:,:,0]>=PARAMETERS['red_minimum'])&envelope
    black=(value<PARAMETERS['black_value_max'])&~red&envelope
    # Small bright islands enclosed by dark bodies are glints, not white beads.
    components,_=ndi.label(~black);sizes=np.bincount(components.ravel())
    fill=sizes<=PARAMETERS['fill_black_highlight_holes_below']
    fill[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
    black|=fill[components]&envelope&~red
    channels=np.zeros(envelope.shape,np.uint8)
    channels[envelope]=3;channels[black]=2;channels[red]=1
    return envelope.copy(),envelope.copy(),channels


def segment(rgb,channels,records):
    labels=np.zeros(channels.shape,np.int32)
    value=ndi.gaussian_filter(rgb.max(axis=2)/255.,1.)
    occupied=set()
    for index,color in enumerate(COLORS,1):
        support=channels==index
        if not support.any():continue
        distance,nearest=ndi.distance_transform_edt(~support,return_indices=True)
        interior=ndi.distance_transform_edt(support)
        markers=np.zeros(channels.shape,np.int32)
        for row in records:
            if row['color']!=color:continue
            x,y=row['marker_xy'];d=float(distance[y,x]);ny,nx=nearest[:,y,x]
            if d>PARAMETERS['maximum_seed_snap_px']:
                row['mask_status']='no_nearby_color_support';row['seed_xy']=None;continue
            if (int(nx),int(ny)) in occupied:
                row['mask_status']='coincident_seed_unresolved';row['seed_xy']=None;continue
            if color=='black':
                radius=PARAMETERS['black_seed_interior_radius'];ys,xs=np.nonzero(support[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1])
                ys+=max(0,y-radius);xs+=max(0,x-radius);offset=np.hypot(xs-x,ys-y);valid=offset<=radius
                if valid.any():
                    ys,xs,offset=ys[valid],xs[valid],offset[valid]
                    best=np.argmax(interior[ys,xs]-.5*offset);ny,nx=ys[best],xs[best];d=float(offset[best])
                if (int(nx),int(ny)) in occupied:
                    row['mask_status']='coincident_interior_seed_unresolved';row['seed_xy']=None;continue
            occupied.add((int(nx),int(ny)));markers[ny,nx]=row['id']
            row.update(seed_xy=[int(nx),int(ny)],seed_snap_px=d,mask_status='provisional_color_constrained_region')
        if markers.any():
            surface=np.zeros_like(value) if color=='black' else -value
            result=watershed(surface,markers,mask=support,compactness=PARAMETERS['watershed_compactness'])
            result[ndi.distance_transform_edt(markers==0)>PARAMETERS['maximum_assignment_distance_px']]=0
            labels[result>0]=result[result>0]
    for row in records:
        components,_=ndi.label(labels==row['id']);seed=row.get('seed_xy')
        keep=components[seed[1],seed[0]] if seed else 0
        detached=(components>0)&(components!=keep);row['detached_pixels_left_unassigned']=int(detached.sum());labels[detached]=0
        ys,xs=np.nonzero(labels==row['id']);row['region_pixels']=len(xs)
        row['bbox_xyxy']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
    return labels


def correction_sheet(rgb,old,active,path):
    boxes=[('Neutral beads: left side',(70,195,128,244)),
           ('Black glints: top',(345,43,396,95)),
           ('White duplicate peaks',(595,135,650,185)),
           ('Neutral edge: bottom',(395,461,453,512))]
    before=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],status='reviewed_body') for r in old]
    image=Image.new('RGB',(960,4*255),'white');draw=ImageDraw.Draw(image)
    for i,(title,box) in enumerate(boxes):
        draw.text((8,i*255+3),title,font=bg.font(18),fill='black')
        for j,(label,rows) in enumerate([('Raw image',[]),('Initial candidates',before),('Active review',active)]):
            draw.text((j*320+8,i*255+26),label,font=bg.font(15),fill='black')
            crop=b1.marker_map(rgb,rows,[],box,4)
            image.paste(crop,(j*320+8,i*255+50))
    image.save(path)


def warning_sheet(rgb,labels,active,path,focus=False):
    warnings=[r for r in active if (r['selection']['warnings'] if focus else r['id'] in [36,122,176,405])]
    scale=6 if focus else 4;row_height=340 if focus else 260
    image=Image.new('RGB',(980,row_height*len(warnings)),'white');draw=ImageDraw.Draw(image)
    for i,row in enumerate(warnings):
        x,y=row['marker_xy'];box=(x-25,y-23,x+26,y+24);oy=i*row_height
        draw.text((8,oy+4),f"{row['id']}: {row['region_pixels']} px, {row['selection']['area_ratio']:.2f} x local median; {"warning remains" if row["selection"]["warnings"] else "warning cleared after review"}",font=bg.font(16),fill='black')
        overlay=rgb.copy();overlay[find_boundaries(labels==row['id'],mode='inner')]=[255,0,255]
        for j,(title,source,rows) in enumerate([('Raw',rgb,[]),('Active markers',rgb,active),('Selected region',overlay,[])]):
            draw.text((j*320+8,oy+27),title,font=bg.font(15),fill='black')
            image.paste(b1.marker_map(source,rows,[],box,scale),(j*320+8,oy+50))
    image.save(path)


def warning_locations(rgb,active,path):
    image=Image.fromarray(rgb).resize((1600,1200));draw=ImageDraw.Draw(image)
    for row in active:
        if not row['selection']['warnings']:continue
        x,y=np.asarray(row['marker_xy'])*2
        draw.ellipse((x-35,y-35,x+35,y+35),outline='magenta',width=4)
        draw.text((x+40,y-12),str(row['id']),font=bg.font(27),fill='magenta',stroke_width=2,stroke_fill='white')
    draw.rectangle((0,0,1600,42),fill='white');draw.text((12,7),'beads3.jpg: locations of uncertain black regions 122 and 405',font=bg.font(23),fill='black')
    image.save(path)


def gallery(path,active,excluded,summary,boxes):
    encoded=base64.b64encode((ROOT/'beads3.jpg').read_bytes()).decode()
    parts=['<!doctype html><meta charset="utf-8"><title>beads3 active inventory</title>',
           '<style>body{font:17px system-ui;max-width:1300px;margin:2em auto;padding:0 1em}svg,img{max-width:100%;height:auto}.mark{fill:transparent;stroke-width:1}.active{stroke:cyan}.excluded{stroke:orange;display:none}.id{font-size:7px;fill:white;paint-order:stroke;stroke:black;stroke-width:1px}</style>',
           '<h1>beads3.jpg: active body observations</h1>',
           f'<p>{len(active)} selected observations; colors {html.escape(str(summary["active_colors"]))}. Slivers ignored. No complete bead count or recovered pattern is claimed. Observation IDs are not chain indices.</p>',
           '<label><input type="checkbox" onchange="document.querySelectorAll(\'.excluded\').forEach(x=>x.style.display=this.checked?\'inline\':\'none\')">Show excluded records</label> <label><input type="checkbox" onchange="document.querySelectorAll(\'.id\').forEach(x=>x.style.visibility=this.checked?\'visible\':\'hidden\')">Show IDs</label>',
           f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
    for kind,rows in [('active',active),('excluded',excluded)]:
        for r in rows:
            x,y=r['marker_xy'];s=r['selection'];title=f'{r["id"]}: {r["color"]}, {r["region_pixels"]} pixels; '+(', '.join(s['reasons']) or 'active')
            parts.append(f'<g class="{kind}"><circle class="mark" cx="{x}" cy="{y}" r="3"><title>{html.escape(title)}</title></circle><text class="id" style="visibility:hidden" x="{x+3}" y="{y-3}">{r["id"]}</text></g>')
    parts.append('</svg><h2>Uncertain black regions: 122 and 405</h2><img src="black-region-locations.png" alt="Locations of black regions 122 and 405"><img src="black-regions.png" alt="Raw, numbered and outlined views of black regions 122 and 405"><h2>Large-area review</h2><p>Remaining warnings are retained observations with provisional regions, not proven merged beads. Sliver ownership is not requested.</p><img src="warnings.png" alt="Raw image and four uncertain large regions"><h2>Reviewed corrections</h2><img src="corrections.png" alt="Raw, initial and corrected body observations"><h2>Reviewed analysis envelope</h2><p>Cyan limits the neutral-body search; this is a provisional image-derived outline.</p><img src="envelope.png" alt="Reviewed foreground outline"><h2>Provisional active regions</h2><p>Yellow: region boundaries. Excluded regions remain unassigned; same-color borders are approximate.</p><img src="regions.png" alt="Active region boundaries">')
    for name in boxes:parts.append(f'<h2>{name}</h2><img src="{name}-review.png" alt="Active bodies in {name}">')
    parts.append('<p>See <a href="../../BEADS3_INVENTORY.md">BEADS3_INVENTORY.md</a> for method and limitations. No new maker questions are needed for this step.</p>')
    path.write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    edits_path=ROOT/'photo2/beads3-review-r071.json';edits=json.loads(edits_path.read_text());image_path=ROOT/'beads3.jpg'
    if bg.digest(image_path)!=edits['image_sha256'] or bg.digest(ROOT/'photo2/blind_generated.py')!=edits['baseline_source_sha256']:raise ValueError('Review inputs changed')
    rgb=np.asarray(Image.open(image_path).convert('RGB'));old_labels,xy,old_mask,hsv=bg.detect(rgb)
    old=bg.observations(rgb,old_labels,xy,old_mask,hsv,3)
    envelope=envelope_mask(old_mask);core,mask,channels=color_support(rgb,envelope)
    removed={r['id'] for r in edits['removed']};fragments=set(edits['fragment_ids'])
    records=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],color=edits['color_overrides'].get(str(r['observation_id']),('red' if r['color']=='red' else (COLORS[int(channels[r['marker_xy'][1],r['marker_xy'][0]])-1] if channels[r['marker_xy'][1],r['marker_xy'][0]] else 'unknown'))),status='ignored_fragment' if r['observation_id'] in fragments else 'reviewed_body',bead_index=None,physical_center_known=False,provenance='R059 marker reviewed from beads3 JPEG in R071') for r in old if r['observation_id'] not in removed]
    for row in edits['added_bodies']:records.append(dict(id=row['id'],marker_xy=row['xy'],color=row['color'],status='reviewed_body',bead_index=None,physical_center_known=False,provenance='R071 manual visible body',note=row['note']))
    for row in records:
        row['marker_xy']=edits.get('marker_overrides',{}).get(str(row['id']),row['marker_xy'])
    envelope=envelope_mask(old_mask)
    core,mask,channels=color_support(rgb,envelope);labels=segment(rgb,channels,records)
    active,excluded=selection.select_records(records,selection.silhouette_distance(mask),SELECTION);active_labels=selection.filter_labels(labels,active)
    unassigned,regions=b1.coverage(mask,labels)
    reviewed=np.zeros(mask.shape,bool)
    for x0,y0,x1,y1 in edits['boxes'].values():reviewed[y0:y1,x0:x1]=True
    summary=dict(baseline_candidates=len(old),removed_markers=len(removed),added_bodies=len(edits['added_bodies']),active_count=len(active),active_colors=dict(Counter(r['color'] for r in active)),excluded_count=len(excluded),known_fragments_ignored=sum(r['status']!='reviewed_body' for r in excluded),small_ids=[r['id'] for r in excluded if any('small_local_area' in reason for reason in r['selection']['reasons'])],active_warning_ids=[r['id'] for r in active if r['selection']['warnings']],support_pixels=int(mask.sum()),original_unassigned_pixels=int(unassigned.sum()),original_unassigned_regions=len(regions),active_pixels=int((active_labels>0).sum()),ignored_assigned_pixels=int(((labels>0)&(active_labels==0)).sum()),support_pixels_outside_review=int((mask&~reviewed).sum()),complete_visible_inventory_verified=False,pattern_status='not inferred')
    bg.write_json(args.review_bundle/'inventory.json',dict(summary=summary,active_observations=active,excluded_observations=excluded,removed=edits['removed'],unassigned_regions=regions,review_boxes=edits['boxes'],limitations=['Image-derived envelope includes uncertain neutral shadow boundaries.','Slivers ignored, not assigned identities.','Unknown chain indices and missing bodies retained.']))
    for name,array in [('envelope',envelope),('labels',labels),('active-labels',active_labels),('color-support',channels)]:np.save(args.output/f'{name}.npy',array)
    selection.overview(rgb,active,args.review_bundle/'active-overview.png')
    outline=rgb.copy();outline[find_boundaries(envelope,mode='inner')]=[0,255,255]
    Image.fromarray(outline).resize((1600,1200)).save(args.review_bundle/'envelope.png')
    for name,box in edits['boxes'].items():b1.marker_map(rgb,active,[],box,4).save(args.review_bundle/f'{name}-review.png')
    overlay=rgb.copy();overlay[find_boundaries(active_labels,mode='inner')]=[255,255,0]
    Image.fromarray(overlay).resize((1600,1200)).save(args.review_bundle/'regions.png')
    correction_sheet(rgb,old,active,args.review_bundle/'corrections.png')
    warning_sheet(rgb,active_labels,active,args.review_bundle/'warnings.png')
    warning_sheet(rgb,active_labels,active,args.review_bundle/'black-regions.png',focus=True)
    warning_locations(rgb,active,args.review_bundle/'black-region-locations.png')
    gallery(args.review_bundle/'review.html',active,excluded,summary,edits['boxes'])
    sources=[Path(__file__).resolve(),ROOT/'photo2/blind_generated.py',ROOT/'photo2/beads1_inventory.py',ROOT/'photo2/inventory_selection.py',edits_path,image_path]
    test=ROOT/'photo2/test_beads3_inventory.py'
    if test.exists():sources.append(test)
    bg.write_json(args.review_bundle/'report.json',dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,selection_parameters=SELECTION,sources={str(p.relative_to(ROOT)):bg.digest(p) for p in sources},summary=summary,artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},bulk_artifacts={p.name:bg.digest(p) for p in sorted(args.output.glob('*.npy'))}))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
