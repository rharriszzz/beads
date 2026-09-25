#!/usr/bin/env python3
"""Image-only beads4 body/color review with R069 sliver selection."""
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
COLORS=['red','yellow','green','cyan','white']
PARAMETERS=dict(envelope_closing_radius=10,envelope_fill_holes_below=1500,
                minimum_chroma=20,minimum_saturation=.16,minimum_white_value=95,
                red_hue_max=.08,yellow_hue_max=.22,green_hue_max=.47,
                fill_color_highlight_holes_below=64,maximum_seed_snap_px=6.,
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
    h,s,v=np.moveaxis(rgb2hsv(rgb),-1,0)
    chroma=rgb.max(axis=2).astype(int)-rgb.min(axis=2).astype(int)
    core=(chroma>=PARAMETERS['minimum_chroma'])&(s>=PARAMETERS['minimum_saturation'])&envelope
    channels=np.zeros(envelope.shape,np.uint8)
    channels[envelope&(v*255>=PARAMETERS['minimum_white_value'])]=5
    channels[core]=4
    channels[core&(h<PARAMETERS['green_hue_max'])]=3
    channels[core&(h<PARAMETERS['yellow_hue_max'])]=2
    channels[core&((h<PARAMETERS['red_hue_max'])|(h>.94))]=1
    for color in range(1,5):
        components,_=ndi.label(channels!=color);sizes=np.bincount(components.ravel())
        fill=sizes<=PARAMETERS['fill_color_highlight_holes_below']
        fill[np.unique(np.r_[components[0],components[-1],components[:,0],components[:,-1]])]=False
        channels[fill[components]&envelope&(channels==5)]=color
    return core,channels>0,channels


def segment(rgb,channels,records):
    labels=np.zeros(channels.shape,np.int32)
    value=ndi.gaussian_filter(rgb.max(axis=2)/255.,1.)
    occupied=set()
    for index,color in enumerate(COLORS,1):
        support=channels==index
        if not support.any():continue
        distance,nearest=ndi.distance_transform_edt(~support,return_indices=True)
        markers=np.zeros(channels.shape,np.int32)
        for row in records:
            if row['color']!=color:continue
            x,y=row['marker_xy'];d=float(distance[y,x]);ny,nx=nearest[:,y,x]
            if d>PARAMETERS['maximum_seed_snap_px']:
                row['mask_status']='no_nearby_color_support';row['seed_xy']=None;continue
            if (int(nx),int(ny)) in occupied:
                row['mask_status']='coincident_seed_unresolved';row['seed_xy']=None;continue
            occupied.add((int(nx),int(ny)));markers[ny,nx]=row['id']
            row.update(seed_xy=[int(nx),int(ny)],seed_snap_px=d,mask_status='provisional_color_constrained_region')
        if markers.any():
            surface=-value
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
    boxes=[('Missing yellow 411', (250,75,298,120)),
           ('Missing cyan 412', (78,207,133,257)),
           ('Missing white 413/414, corrected 379', (379,427,489,492)),
           ('One white body: retain 363', (564,434,612,483))]
    before=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],status='reviewed_body') for r in old]
    image=Image.new('RGB',(1380,4*325),'white');draw=ImageDraw.Draw(image)
    for i,(title,box) in enumerate(boxes):
        draw.text((8,i*325+3),title,font=bg.font(18),fill='black')
        for j,(label,rows) in enumerate([('Raw JPEG',[]),('R059 candidates',before),('R076 active',active)]):
            draw.text((j*460+8,i*325+27),label,font=bg.font(16),fill='black')
            image.paste(b1.marker_map(rgb,rows,[],box,4),(j*460+8,i*325+53))
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
        if not np.all(channels[region]==COLORS.index(row['color'])+1):
            raise ValueError('Active region crosses palette classes')
        if int(region.sum())!=row['region_pixels'] or row['bead_index'] is not None:
            raise ValueError('Incorrect region area or invented chain index')
    expected=np.where(np.isin(labels,[r['id'] for r in active]),labels,0)
    if not np.array_equal(expected,active_labels):
        raise ValueError('Filtering reassigned pixels')
    if set(np.unique(active_labels))-{0}-{r['id'] for r in active}:
        raise ValueError('Unexpected active labels')
    return dict(unique_ids=True,removed_ids_absent=True,connected_nonempty_active=True,
                active_seeds_preserved=True,palette_pure=True,areas_match=True,
                no_filter_pixel_reassignment=True,chain_indices_null=True,
                max_seed_snap_px=max(r['seed_snap_px'] for r in active),
                minimum_local_references=min(len(r['selection']['local_reference_ids']) for r in active),
                detached_pixels_unassigned=sum(r['detached_pixels_left_unassigned'] for r in records))


def gallery(path,active,excluded,summary,boxes):
    encoded=base64.b64encode((ROOT/'beads4.jpg').read_bytes()).decode()
    parts=['<!doctype html><meta charset="utf-8"><title>beads4 active inventory</title>',
           '<style>body{font:17px system-ui;max-width:1300px;margin:2em auto;padding:0 1em}svg,img{max-width:100%;height:auto}.mark{fill:transparent;stroke-width:1}.active{stroke:cyan}.excluded{stroke:orange;display:none}.id{font-size:7px;fill:white;paint-order:stroke;stroke:black;stroke-width:1px}</style>',
           '<h1>beads4.jpg: active body observations</h1>',
           f'<p>{len(active)} selected observations; colors {html.escape(str(summary["active_colors"]))}. Slivers ignored. No complete bead count or recovered pattern is claimed. Observation IDs are not chain indices.</p>',
           '<label><input type="checkbox" onchange="document.querySelectorAll(\'.excluded\').forEach(x=>x.style.display=this.checked?\'inline\':\'none\')">Show excluded records</label> <label><input type="checkbox" onchange="document.querySelectorAll(\'.id\').forEach(x=>x.style.visibility=this.checked?\'visible\':\'hidden\')">Show IDs</label>',
           f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
    for kind,rows in [('active',active),('excluded',excluded)]:
        for r in rows:
            x,y=r['marker_xy'];s=r['selection'];title=f'{r["id"]}: {r["color"]}, {r["region_pixels"]} pixels; '+(', '.join(s['reasons']) or 'active')
            parts.append(f'<g class="{kind}"><circle class="mark" cx="{x}" cy="{y}" r="3"><title>{html.escape(title)}</title></circle><text class="id" style="visibility:hidden" x="{x+3}" y="{y-3}">{r["id"]}</text></g>')
    parts.append('</svg><h2>Corrections from JPEG review</h2><img src="corrections.png" alt="Raw, baseline and active observations"><h2>Local-area exclusions</h2><img src="area-review.png" alt="Small regions excluded by the unchanged area rule"><h2>Foreground and palette</h2><img src="envelope.png" alt="Cyan search envelope"><img src="palette.png" alt="Five provisional color classes"><h2>Provisional active regions</h2><p>Yellow: region boundaries. Excluded regions remain unassigned; same-color borders are approximate.</p><img src="regions.png" alt="Active region boundaries">')
    for name in boxes:parts.append(f'<h2>{name}</h2><img src="{name}-review.png" alt="Active bodies in {name}">')
    parts.append('<p>See <a href="../../BEADS4_INVENTORY.md">BEADS4_INVENTORY.md</a> for method and limitations. No new maker questions are needed for this step.</p>')
    path.write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    edits_path=ROOT/'photo2/beads4-review-r076.json';edits=json.loads(edits_path.read_text());image_path=ROOT/'beads4.jpg'
    if bg.digest(image_path)!=edits['image_sha256'] or bg.digest(ROOT/'photo2/blind_generated.py')!=edits['baseline_source_sha256']:raise ValueError('Review inputs changed')
    rgb=np.asarray(Image.open(image_path).convert('RGB'));old_labels,xy,old_mask,hsv=bg.detect(rgb)
    old=bg.observations(rgb,old_labels,xy,old_mask,hsv,4)
    removed={r['id'] for r in edits['removed']};fragments=set(edits['fragment_ids'])
    records=[dict(id=r['observation_id'],marker_xy=r['marker_xy'],color=edits['color_overrides'].get(str(r['observation_id']),r['color']),status='ignored_fragment' if r['observation_id'] in fragments else 'reviewed_body',bead_index=None,physical_center_known=False,provenance='R059 marker reviewed from beads4 JPEG in R076') for r in old if r['observation_id'] not in removed]
    for row in edits['added_bodies']:records.append(dict(id=row['id'],marker_xy=row['xy'],color=row['color'],status='reviewed_body',bead_index=None,physical_center_known=False,provenance='R076 manual visible body',note=row['note']))
    for row in records:
        row['marker_xy']=edits.get('marker_overrides',{}).get(str(row['id']),row['marker_xy'])
    envelope=envelope_mask(old_mask)
    core,mask,channels=color_support(rgb,envelope);labels=segment(rgb,channels,records)
    active,excluded=selection.select_records(records,selection.silhouette_distance(mask),SELECTION);active_labels=selection.filter_labels(labels,active)
    checks=validate_maps(records,active,excluded,labels,active_labels,channels,removed)
    unassigned,regions=b1.coverage(mask,labels)
    reviewed=np.zeros(mask.shape,bool)
    for x0,y0,x1,y1 in edits['boxes'].values():reviewed[y0:y1,x0:x1]=True
    summary=dict(baseline_candidates=len(old),removed_markers=len(removed),added_bodies=len(edits['added_bodies']),active_count=len(active),active_colors=dict(Counter(r['color'] for r in active)),excluded_count=len(excluded),known_fragments_ignored=sum(r['status']!='reviewed_body' for r in excluded),small_ids=[r['id'] for r in excluded if any('small_local_area' in reason for reason in r['selection']['reasons'])],active_warning_ids=[r['id'] for r in active if r['selection']['warnings']],support_pixels=int(mask.sum()),original_unassigned_pixels=int(unassigned.sum()),original_unassigned_regions=len(regions),active_pixels=int((active_labels>0).sum()),ignored_assigned_pixels=int(((labels>0)&(active_labels==0)).sum()),support_pixels_outside_review=int((mask&~reviewed).sum()),complete_visible_inventory_verified=False,pattern_status='not inferred')
    bg.write_json(args.review_bundle/'inventory.json',dict(summary=summary,active_observations=active,excluded_observations=excluded,removed=edits['removed'],unassigned_regions=regions,review_boxes=edits['boxes'],limitations=['Image-derived envelope includes uncertain neutral shadow boundaries.','Same-color watershed boundaries and white/shadow separation remain provisional.','Slivers ignored, not assigned identities.','Unknown chain indices and missing bodies retained.']))
    for name,array in [('envelope',envelope),('labels',labels),('active-labels',active_labels),('color-support',channels)]:np.save(args.output/f'{name}.npy',array)
    selection.overview(rgb,active,args.review_bundle/'active-overview.png')
    outline=rgb.copy();outline[find_boundaries(envelope,mode='inner')]=[0,255,255]
    Image.fromarray(outline).resize((1600,1200)).save(args.review_bundle/'envelope.png')
    for name,box in edits['boxes'].items():b1.marker_map(rgb,active,[],box,4).save(args.review_bundle/f'{name}-review.png')
    overlay=rgb.copy();overlay[find_boundaries(active_labels,mode='inner')]=[255,255,0]
    Image.fromarray(overlay).resize((1600,1200)).save(args.review_bundle/'regions.png')
    palette=np.array([[255,255,255],[220,30,30],[190,180,0],[20,190,30],[0,150,210],[175,175,175]],dtype=np.uint8)
    Image.fromarray(palette[channels]).resize((1600,1200)).save(args.review_bundle/'palette.png')
    correction_sheet(rgb,old,active,args.review_bundle/'corrections.png')
    selection.area_sheet(rgb,excluded,args.review_bundle/'area-review.png')
    gallery(args.review_bundle/'review.html',active,excluded,summary,edits['boxes'])
    sources=[Path(__file__).resolve(),ROOT/'photo2/blind_generated.py',ROOT/'photo2/beads1_inventory.py',ROOT/'photo2/inventory_selection.py',edits_path,image_path]
    test=ROOT/'photo2/test_beads4_inventory.py'
    if test.exists():sources.append(test)
    bg.write_json(args.review_bundle/'report.json',dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,selection_parameters=SELECTION,checks=checks,environment=dict(python=sys.version,numpy=np.__version__,scipy=bg.scipy.__version__,skimage=bg.skimage.__version__),sources={str(p.relative_to(ROOT)):bg.digest(p) for p in sources},summary=summary,artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},bulk_artifacts={p.name:bg.digest(p) for p in sorted(args.output.glob('*.npy'))}))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
