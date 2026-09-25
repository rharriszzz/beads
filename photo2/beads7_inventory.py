#!/usr/bin/env python3
"""Image-only beads7 body/color review with R069 sliver selection."""
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
COLORS=['red','green','black','silver','white']
SUPPORT_CLASS={'red':1,'green':2,'black':3,'silver':4,'white':4}
PARAMETERS=dict(envelope_closing_radius=10,envelope_fill_holes_below=1500,
                minimum_red_dominance=25,minimum_green_dominance=20,minimum_saturation=.13,
                black_value_max=95,fill_color_highlight_holes_below=192,
                maximum_seed_snap_px=6.,black_seed_interior_radius=4,
                watershed_compactness=.03,maximum_assignment_distance_px=28.)
SELECTION={**selection.PARAMETERS,'explicit_excluded_ids':[]}


def envelope_mask(base):
    mask=ndi.binary_closing(base,structure=disk(PARAMETERS['envelope_closing_radius']))
    components,_=ndi.label(~mask);sizes=np.bincount(components.ravel())
    fill=sizes<=PARAMETERS['envelope_fill_holes_below']
    fill[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
    return mask|fill[components]


def color_support(rgb,envelope):
    from skimage.color import rgb2hsv
    _,s,v=np.moveaxis(rgb2hsv(rgb),-1,0)
    red=(rgb[:,:,0].astype(int)-np.maximum(rgb[:,:,1],rgb[:,:,2]).astype(int)>=PARAMETERS['minimum_red_dominance'])&(s>=PARAMETERS['minimum_saturation'])&envelope
    green=(rgb[:,:,1].astype(int)-np.maximum(rgb[:,:,0],rgb[:,:,2]).astype(int)>=PARAMETERS['minimum_green_dominance'])&(s>=PARAMETERS['minimum_saturation'])&envelope
    black=(v*255<PARAMETERS['black_value_max'])&~red&~green&envelope
    channels=np.zeros(envelope.shape,np.uint8);channels[envelope]=4
    channels[red]=1;channels[green]=2;channels[black]=3
    for index,core in ((1,red),(2,green),(3,black)):
        components,_=ndi.label(~core);sizes=np.bincount(components.ravel())
        fill=sizes<=PARAMETERS['fill_color_highlight_holes_below']
        fill[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
        # Repair only neutral glints; retain another observed chromatic core.
        channels[fill[components]&envelope&~red&~green]=index
    return red|green|black,envelope.copy(),channels


def restore_reviewed_glints(channels,disks):
    """Restore only annotated neutral highlight pixels, never colored cores/background."""
    result=channels.copy();yy,xx=np.indices(channels.shape)
    for patch in disks:
        x,y=patch['xy'];inside=(xx-x)**2+(yy-y)**2<=patch['radius']**2
        result[inside&(result==4)]=3
    return result


def segment(rgb,channels,records):
    labels=np.zeros(channels.shape,np.int32)
    value=ndi.gaussian_filter(rgb.max(axis=2)/255.,1.)
    occupied=set()
    for index in (1,2,3,4):
        support=channels==index
        if not support.any():continue
        distance,nearest=ndi.distance_transform_edt(~support,return_indices=True)
        interior=ndi.distance_transform_edt(support)
        markers=np.zeros(channels.shape,np.int32)
        for row in records:
            if SUPPORT_CLASS[row['color']]!=index:continue
            x,y=row['marker_xy'];d=float(distance[y,x]);ny,nx=nearest[:,y,x]
            if d>PARAMETERS['maximum_seed_snap_px']:
                row['mask_status']='no_nearby_color_support';row['seed_xy']=None;continue
            if index==3:
                radius=PARAMETERS['black_seed_interior_radius']
                ys,xs=np.nonzero(support[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1])
                ys+=max(0,y-radius);xs+=max(0,x-radius);offset=np.hypot(xs-x,ys-y);valid=offset<=radius
                if valid.any():
                    ys,xs,offset=ys[valid],xs[valid],offset[valid]
                    best=np.argmax(interior[ys,xs]-.5*offset);ny,nx=ys[best],xs[best];d=float(offset[best])
            if (int(nx),int(ny)) in occupied:
                row['mask_status']='coincident_seed_unresolved';row['seed_xy']=None;continue
            occupied.add((int(nx),int(ny)));markers[ny,nx]=row['id']
            row.update(seed_xy=[int(nx),int(ny)],seed_snap_px=d,mask_status='provisional_color_constrained_region')
        if markers.any():
            surface=np.zeros_like(value) if index==3 else -value
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
    boxes=[('Dark-body additions on left', (105,183,155,288)),
           ('Pale-body separation on right', (695,317,739,379)),
           ('Black seed and lower body', (514,102,556,154)),
           ('Black glint beside pale body', (248,385,300,427))]
    before=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],status='reviewed_body') for r in old]
    heights=[(box[3]-box[1])*4+60 for _,box in boxes]
    image=Image.new('RGB',(960,sum(heights)),'white');draw=ImageDraw.Draw(image);oy=0
    for (title,box),height in zip(boxes,heights):
        draw.text((8,oy+3),title,font=bg.font(18),fill='black')
        for j,(label,rows) in enumerate([('Raw JPEG',[]),('R059 candidates',before),('R079 active',active)]):
            draw.text((j*320+8,oy+27),label,font=bg.font(16),fill='black')
            image.paste(b1.marker_map(rgb,rows,[],box,4),(j*320+8,oy+53))
        oy+=height
    image.save(path)


def glint_sheet(rgb,channels,base_channels,records,path):
    image=Image.new('RGB',(990,540),'white');draw=ImageDraw.Draw(image)
    for i,obs_id in enumerate((94,315)):
        row=next(r for r in records if r['id']==obs_id);x,y=row['marker_xy']
        box=(x-22,y-18,x+23,y+19);oy=i*270
        draw.text((8,oy+4),f'{obs_id}: reviewed black glint; manual support remains provisional',font=bg.font(17),fill='black')
        before=rgb.copy();before[find_boundaries(base_channels==3,mode='inner')]=[255,0,255]
        after=rgb.copy();after[find_boundaries(channels==3,mode='inner')]=[255,0,255];after[channels!=base_channels]=[0,255,255]
        for j,(title,source) in enumerate([('Raw JPEG',rgb),('Automatic dark support',before),('Cyan: restored glint pixels',after)]):
            draw.text((j*330+8,oy+28),title,font=bg.font(16),fill='black')
            image.paste(b1.marker_map(source,[],[],box,5),(j*330+8,oy+52))
    image.save(path)


def warning_sheet(rgb,labels,active,path):
    rows=[r for r in active if r['selection']['warnings']]
    image=Image.new('RGB',(1080,max(1,len(rows))*345),'white');draw=ImageDraw.Draw(image)
    if not rows:draw.text((10,10),'No large-area or sparse-reference warnings',font=bg.font(18),fill='black')
    for i,row in enumerate(rows):
        x,y=row['marker_xy'];box=(x-27,y-24,x+28,y+25);oy=i*345
        draw.text((8,oy+4),f"{row['id']}: {row['region_pixels']} pixels; {row['selection']['area_ratio']:.3f} x local median; unresolved",font=bg.font(18),fill='black')
        outline=rgb.copy();outline[find_boundaries(labels==row['id'],mode='inner')]=[255,0,255]
        for j,(title,source,markers) in enumerate([('Raw JPEG',rgb,[]),('Active markers',rgb,active),('Provisional region',outline,[])]):
            draw.text((j*360+8,oy+29),title,font=bg.font(16),fill='black')
            image.paste(b1.marker_map(source,markers,[],box,5),(j*360+8,oy+52))
    image.save(path)


def validate_maps(records,active,excluded,labels,active_labels,channels,removed):
    ids=[r['id'] for r in records]
    if len(ids)!=len(set(ids)) or set(ids)&removed:
        raise ValueError('Duplicate IDs or removed observations present')
    for row in active:
        region=active_labels==row['id'];seed=row['seed_xy']
        if not region.any() or ndi.label(region)[1]!=1:
            raise ValueError('Empty or disconnected active region')
        if not seed or not region[seed[1],seed[0]]:
            raise ValueError('Active seed lost')
        if not np.all(channels[region]==SUPPORT_CLASS[row['color']]):
            raise ValueError('Active region crosses palette classes')
        if int(region.sum())!=row['region_pixels'] or row['bead_index'] is not None:
            raise ValueError('Incorrect region area or invented chain index')
    expected=np.where(np.isin(labels,[r['id'] for r in active]),labels,0)
    if not np.array_equal(expected,active_labels):
        raise ValueError('Filtering reassigned pixels')
    if set(np.unique(active_labels))-{0}-{r['id'] for r in active}:
        raise ValueError('Unexpected active labels')
    return dict(unique_ids=True,removed_ids_absent=True,connected_nonempty_active=True,
                active_seeds_preserved=True,support_class_pure=True,areas_match=True,
                no_filter_pixel_reassignment=True,chain_indices_null=True,
                max_seed_snap_px=max(r['seed_snap_px'] for r in active),
                minimum_local_references=min(len(r['selection']['local_reference_ids']) for r in active),
                detached_pixels_unassigned=sum(r['detached_pixels_left_unassigned'] for r in records))


def gallery(path,active,excluded,summary,boxes):
    encoded=base64.b64encode((ROOT/'beads7.jpg').read_bytes()).decode()
    parts=['<!doctype html><meta charset="utf-8"><title>beads7 active inventory</title>',
           '<style>body{font:17px system-ui;max-width:1300px;margin:2em auto;padding:0 1em}svg,img{max-width:100%;height:auto}.mark{fill:transparent;stroke-width:1}.active{stroke:cyan}.excluded{stroke:orange;display:none}.id{font-size:7px;fill:white;paint-order:stroke;stroke:black;stroke-width:1px}</style>',
           '<h1>beads7.jpg: active body observations</h1>',
           f'<p>{len(active)} selected observations; colors {html.escape(str(summary["active_colors"]))}. Slivers ignored. No complete bead count or recovered pattern is claimed. Observation IDs are not chain indices.</p>',
           '<label><input type="checkbox" onchange="document.querySelectorAll(\'.excluded\').forEach(x=>x.style.display=this.checked?\'inline\':\'none\')">Show excluded records</label> <label><input type="checkbox" onchange="document.querySelectorAll(\'.id\').forEach(x=>x.style.visibility=this.checked?\'visible\':\'hidden\')">Show IDs</label>',
           f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
    for kind,rows in [('active',active),('excluded',excluded)]:
        for r in rows:
            x,y=r['marker_xy'];s=r['selection'];title=f'{r["id"]}: {r["color"]}, {r["region_pixels"]} pixels; '+(', '.join(s['reasons']) or 'active')
            parts.append(f'<g class="{kind}"><circle class="mark" cx="{x}" cy="{y}" r="3"><title>{html.escape(title)}</title></circle><text class="id" style="visibility:hidden" x="{x+3}" y="{y-3}">{r["id"]}</text></g>')
    parts.append('</svg><h2>Unresolved region warnings</h2><img src="warnings.png" alt="Raw, numbered and outlined warning regions"><h2>Corrections from JPEG review</h2><img src="corrections.png" alt="Raw, baseline and active observations"><h2>Reviewed black glints</h2><img src="glints.png" alt="Raw and repaired black highlight support"><h2>Local-area exclusions</h2><img src="area-review.png" alt="Small regions excluded by the unchanged area rule"><h2>Foreground and palette</h2><img src="envelope.png" alt="Cyan search envelope"><img src="palette.png" alt="Red, green, black and shared pale-neutral support"><h2>Provisional active regions</h2><p>Yellow: region boundaries. Excluded regions remain unassigned; same-color borders are approximate.</p><img src="regions.png" alt="Active region boundaries">')
    for name in boxes:parts.append(f'<h2>{name}</h2><img src="{name}-review.png" alt="Active bodies in {name}">')
    parts.append('<p>See <a href="../../BEADS7_INVENTORY.md">BEADS7_INVENTORY.md</a> for method and limitations. No new maker questions are needed for this step.</p>')
    path.write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    edits_path=ROOT/'photo2/beads7-review-r079.json';edits=json.loads(edits_path.read_text());image_path=ROOT/'beads7.jpg'
    if bg.digest(image_path)!=edits['image_sha256'] or bg.digest(ROOT/'photo2/blind_generated.py')!=edits['baseline_source_sha256']:raise ValueError('Review inputs changed')
    rgb=np.asarray(Image.open(image_path).convert('RGB'));old_labels,xy,old_mask,hsv=bg.detect(rgb)
    old=bg.observations(rgb,old_labels,xy,old_mask,hsv,7)
    removed={r['id'] for r in edits['removed']};fragments=set(edits['fragment_ids'])
    records=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],color=edits['color_overrides'].get(str(r['observation_id']),r['color']),status='ignored_fragment' if r['observation_id'] in fragments else 'reviewed_body',bead_index=None,physical_center_known=False,provenance='R059 marker reviewed from beads7 JPEG in R079') for r in old if r['observation_id'] not in removed]
    for row in edits['added_bodies']:records.append(dict(id=row['id'],marker_xy=row['xy'],color=row['color'],status='reviewed_body',bead_index=None,physical_center_known=False,provenance='R079 manual visible body',note=row['note']))
    for row in records:
        row['marker_xy']=edits.get('marker_overrides',{}).get(str(row['id']),row['marker_xy'])
    envelope=envelope_mask(old_mask)
    core,mask,channels=color_support(rgb,envelope)
    channels=restore_reviewed_glints(channels,edits.get('black_glint_disks',[]))
    labels=segment(rgb,channels,records)
    active,excluded=selection.select_records(records,selection.silhouette_distance(mask),SELECTION);active_labels=selection.filter_labels(labels,active)
    checks=validate_maps(records,active,excluded,labels,active_labels,channels,removed)
    unassigned,regions=b1.coverage(mask,labels)
    reviewed=np.zeros(mask.shape,bool)
    for x0,y0,x1,y1 in edits['boxes'].values():reviewed[y0:y1,x0:x1]=True
    summary=dict(baseline_candidates=len(old),removed_markers=len(removed),added_bodies=len(edits['added_bodies']),active_count=len(active),active_colors=dict(Counter(r['color'] for r in active)),excluded_count=len(excluded),known_fragments_ignored=sum(r['status']!='reviewed_body' for r in excluded),small_ids=[r['id'] for r in excluded if any('small_local_area' in reason for reason in r['selection']['reasons'])],active_warning_ids=[r['id'] for r in active if r['selection']['warnings']],support_pixels=int(mask.sum()),original_unassigned_pixels=int(unassigned.sum()),original_unassigned_regions=len(regions),active_pixels=int((active_labels>0).sum()),ignored_assigned_pixels=int(((labels>0)&(active_labels==0)).sum()),support_pixels_outside_review=int((mask&~reviewed).sum()),complete_visible_inventory_verified=False,pattern_status='not inferred')
    bg.write_json(args.review_bundle/'inventory.json',dict(summary=summary,active_observations=active,excluded_observations=excluded,removed=edits['removed'],unassigned_regions=regions,review_boxes=edits['boxes'],limitations=['Image-derived envelope includes uncertain neutral/shadow boundaries.','Same-color watershed borders and body colors remain provisional.','Slivers ignored, not assigned identities; large-area warnings are unresolved.','Unknown chain indices and missing bodies retained.']))
    for name,array in [('envelope',envelope),('labels',labels),('active-labels',active_labels),('color-support',channels)]:np.save(args.output/f'{name}.npy',array)
    selection.overview(rgb,active,args.review_bundle/'active-overview.png')
    outline=rgb.copy();outline[find_boundaries(envelope,mode='inner')]=[0,255,255]
    Image.fromarray(outline).resize((1600,1200)).save(args.review_bundle/'envelope.png')
    for name,box in edits['boxes'].items():b1.marker_map(rgb,active,[],box,4).save(args.review_bundle/f'{name}-review.png')
    overlay=rgb.copy();overlay[find_boundaries(active_labels,mode='inner')]=[255,255,0]
    Image.fromarray(overlay).resize((1600,1200)).save(args.review_bundle/'regions.png')
    palette=np.array([[255,255,255],[220,20,20],[40,180,60],[30,30,30],[185,200,205]],dtype=np.uint8)
    Image.fromarray(palette[channels]).resize((1600,1200)).save(args.review_bundle/'palette.png')
    correction_sheet(rgb,old,active,args.review_bundle/'corrections.png')
    glint_sheet(rgb,channels,color_support(rgb,envelope)[2],records,args.review_bundle/'glints.png')
    selection.area_sheet(rgb,excluded,args.review_bundle/'area-review.png')
    warning_sheet(rgb,active_labels,active,args.review_bundle/'warnings.png')
    gallery(args.review_bundle/'review.html',active,excluded,summary,edits['boxes'])
    sources=[Path(__file__).resolve(),ROOT/'photo2/blind_generated.py',ROOT/'photo2/beads1_inventory.py',ROOT/'photo2/inventory_selection.py',edits_path,image_path]
    test=ROOT/'photo2/test_beads7_inventory.py'
    if test.exists():sources.append(test)
    bg.write_json(args.review_bundle/'report.json',dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,selection_parameters=SELECTION,checks=checks,environment=dict(python=sys.version,numpy=np.__version__,scipy=bg.scipy.__version__,skimage=bg.skimage.__version__),sources={str(p.relative_to(ROOT)):bg.digest(p) for p in sources},summary=summary,artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},bulk_artifacts={p.name:bg.digest(p) for p in sorted(args.output.glob('*.npy'))}))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
