#!/usr/bin/env python3
"""Apply R069: ignore slivers; compare each visible area with nearby bead bodies."""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import copy
import html
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import blind_generated as bg

ROOT=Path(__file__).resolve().parents[1]
PARAMETERS=dict(neighbor_count=8,neighbor_radius_px=45.,minimum_neighbors=4,
                minimum_area_ratio=.5,large_area_warning_ratio=2.,
                edge_radius_multiplier=1.,silhouette_closing_radius=2,
                silhouette_hole_limit_px=128,explicit_excluded_ids=[211])


def silhouette_distance(support):
    radius=PARAMETERS['silhouette_closing_radius']
    y,x=np.mgrid[-radius:radius+1,-radius:radius+1]
    mask=ndi.binary_closing(support,structure=x*x+y*y<=radius*radius)
    labels,_=ndi.label(~mask);sizes=np.bincount(labels.ravel());fill=sizes<=PARAMETERS['silhouette_hole_limit_px']
    fill[np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]])]=False
    mask|=fill[labels]
    return ndi.distance_transform_edt(mask)


def select_records(records,distance,params=None):
    p=PARAMETERS if params is None else params
    # Freeze reference bodies before selection: no iterative shrinkage/cascade.
    reference=[r for r in records if r['status']=='reviewed_body' and r['region_pixels']>0 and r['id'] not in p['explicit_excluded_ids']]
    ref_xy=np.array([r['marker_xy'] for r in reference],float).reshape(-1,2)
    ref_ids=np.array([r['id'] for r in reference],int)
    ref_areas=np.array([r['region_pixels'] for r in reference],float)
    active=[];excluded=[]
    for original in records:
        row=copy.deepcopy(original);x,y=row['marker_xy'];reasons=[];warnings=[]
        d=np.linalg.norm(ref_xy-np.array([x,y]),axis=1)
        candidates=np.flatnonzero((ref_ids!=row['id'])&(d<=p['neighbor_radius_px']))
        order=np.lexsort((ref_ids[candidates],d[candidates]));chosen=candidates[order[:p['neighbor_count']]]
        sufficient=len(chosen)>=p['minimum_neighbors']
        median=float(np.median(ref_areas[chosen])) if sufficient else None
        ratio=row['region_pixels']/median if median else None
        edge_distance=float(distance[y,x]);near=bool(edge_distance<=p['edge_radius_multiplier']*np.sqrt(median/np.pi)) if median else None
        if row['status']!='reviewed_body':reasons.append('sliver_or_fragment_ignored_by_user')
        if row['id'] in p['explicit_excluded_ids']:reasons.append('explicit_user_exclusion')
        if row['region_pixels']<=0:reasons.append('no_visible_region')
        if ratio is not None and ratio<p['minimum_area_ratio']:
            reasons.append('small_local_area_near_edge' if near else 'small_local_area')
        if ratio is not None and ratio>p['large_area_warning_ratio']:warnings.append('large_local_area_possible_merge')
        if not sufficient:warnings.append('insufficient_local_reference')
        row['selection']=dict(active=not reasons,reasons=reasons,warnings=warnings,
                              local_reference_ids=ref_ids[chosen].tolist(),local_median_area_px=median,
                              area_ratio=ratio,silhouette_distance_px=edge_distance,near_edge=near)
        (excluded if reasons else active).append(row)
    return active,excluded


def filter_labels(labels,active):
    return np.where(np.isin(labels,[r['id'] for r in active]),labels,0).astype(np.int32)


def overview(rgb,active,path):
    image=Image.fromarray(rgb).resize((1600,1200));d=ImageDraw.Draw(image)
    for row in active:
        x,y=np.array(row['marker_xy'])*2
        d.ellipse((x-4,y-4,x+4,y+4),outline='black',width=3)
        d.ellipse((x-3,y-3,x+3,y+3),outline='cyan',width=2)
    image.save(path)


def area_sheet(rgb,rows,path):
    w,h=220,210;image=Image.new('RGB',(w*5,h*((len(rows)+4)//5)),'white');d=ImageDraw.Draw(image)
    source=Image.fromarray(rgb)
    for i,row in enumerate(rows):
        x,y=row['marker_xy'];left=(i%5)*w;top=(i//5)*h;s=row['selection']
        d.text((left+4,top+3),f"{row['id']}: {'keep' if s['active'] else 'exclude'}",font=bg.font(16),fill='black')
        image.paste(source.crop((x-18,y-18,x+19,y+19)).resize((148,148)),(left+32,top+27))
        d.ellipse((left+100,top+95,left+108,top+103),outline='cyan' if s['active'] else 'orange',width=2)
        d.text((left+4,top+178),f"{row['region_pixels']} px / local {s['local_median_area_px']:.0f}",font=bg.font(14),fill='black')
        d.text((left+4,top+194),f"ratio {s['area_ratio']:.2f}; edge {s['silhouette_distance_px']:.1f}px",font=bg.font(13),fill='black')
    image.save(path)


def gallery(path,image_path,active,excluded,summary):
    encoded=base64.b64encode(image_path.read_bytes()).decode()
    parts=['<!doctype html><meta charset="utf-8"><title>Active bead inventory</title>',
           '<style>body{font:17px system-ui;max-width:1200px;margin:2em auto;padding:0 1em}svg,img{max-width:100%;height:auto}.mark{fill:transparent;stroke-width:1}.active{stroke:cyan}.excluded{stroke:orange;display:none}.id{font-size:7px;fill:white;paint-order:stroke;stroke:black;stroke-width:1px}</style>',
           '<h1>beads1.jpg: active bodies, slivers ignored</h1>',
           f'<p>{len(active)} active body observations. {summary["known_fragments_ignored"]} known fragments and {summary["additional_small_bodies_excluded"]} small body candidates excluded. 211 remains excluded. These are selected observations, not the total number of beads.</p>',
           '<p>Cyan: active. Excluded observations are hidden by default. The local-area rule is a heuristic; it can exclude genuinely visible partial beads. It does not diagnose the lighting.</p>',
           '<label><input type="checkbox" onchange="document.querySelectorAll(\'.excluded\').forEach(x=>x.style.display=this.checked?\'inline\':\'none\')"> Show excluded records for audit</label>',
           f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
    for kind,rows in [('active',active),('excluded',excluded)]:
        for r in rows:
            x,y=r['marker_xy'];s=r['selection'];ratio='unavailable' if s['area_ratio'] is None else f'{s["area_ratio"]:.2f}'
            title=f'ID {r["id"]}: {r["color"]}; {r["region_pixels"]} pixels; local ratio {ratio}; '+(', '.join(s['reasons']) or 'active')
            parts.append(f'<circle class="mark {kind}" cx="{x}" cy="{y}" r="3"><title>{html.escape(title)}</title></circle>')
    parts.append('</svg><h2>Small-area exclusions and retained 217</h2><img src="area-review.png" alt="Local area comparisons"><p>Neighborhoods use up to eight original reviewed body candidates within45px. Below half their median area is excluded; above twice it would be flagged for review. Known slivers are excluded regardless of size. Ordinary-sized edge beads remain eligible. Excluded pixels stay unassigned rather than being absorbed by neighbors.</p>')
    path.write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-review',type=Path,default=ROOT/'photo2/review/r068')
    parser.add_argument('--source-output',type=Path,default=ROOT/'photo2/output/inventory-r068-final')
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True)
    args=parser.parse_args();args.source_review=args.source_review.resolve();args.source_output=args.source_output.resolve()
    args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    source_report=args.source_review/'report.json';report=json.loads(source_report.read_text())
    source_inventory=args.source_review/'inventory.json'
    if bg.digest(source_inventory)!=report['artifacts']['inventory.json']:raise ValueError('Source inventory hash mismatch')
    for name in ['labels.npy','color-support.npy']:
        if bg.digest(args.source_output/name)!=report['bulk_artifacts'][name]:raise ValueError('Source map hash mismatch: '+name)
    image_path=ROOT/'beads1.jpg'
    if bg.digest(image_path)!=report['sources']['beads1.jpg']:raise ValueError('Source photo hash mismatch')
    inventory=json.loads(source_inventory.read_text());labels=np.load(args.source_output/'labels.npy');support=np.load(args.source_output/'color-support.npy')>0
    active,excluded=select_records(inventory['observations'],silhouette_distance(support))
    active_labels=filter_labels(labels,active)
    small=[r for r in excluded if r['status']=='reviewed_body']
    summary=dict(source_observations=len(inventory['observations']),active_count=len(active),active_colors=dict(Counter(r['color'] for r in active)),
                 excluded_observations=len(excluded),known_fragments_ignored=sum(r['status']!='reviewed_body' for r in excluded),
                 additional_small_bodies_excluded=len(small),small_ids=[r['id'] for r in small],
                 small_near_edge=sum(r['selection']['near_edge'] is True for r in small),
                 active_near_edge=sum(r['selection']['near_edge'] is True for r in active),
                 active_warning_ids=[r['id'] for r in active if r['selection']['warnings']],
                 ignored_region_pixels=int(((labels>0)&(active_labels==0)).sum()),
                 active_region_pixels=int((active_labels>0).sum()),explicit_211_excluded=211 not in [r['id'] for r in active])
    result=dict(summary=summary,policy='R069: ignore all slivers; 211 explicitly excluded; local area comparability',
                active_observations=active,excluded_observations=excluded,previously_removed=inventory['removed'],
                limitations=['Area ratios depend on provisional region masks.', 'Excluded partial beads remain missing observations, never renumbered chain indices.', 'Lighting cause is the maker hypothesis, not verified here.'])
    np.save(args.output/'active-labels.npy',active_labels)
    bg.write_json(args.review_bundle/'inventory.json',result)
    rgb=np.asarray(Image.open(image_path).convert('RGB'))
    overview(rgb,active,args.review_bundle/'active-overview.png')
    controls=[r for r in active if r['id']==217]
    area_sheet(rgb,small+controls,args.review_bundle/'area-review.png')
    gallery(args.review_bundle/'review.html',image_path,active,excluded,summary)
    sources=[Path(__file__).resolve(),ROOT/'photo2/test_inventory_selection.py',ROOT/'photo2/blind_generated.py',source_report,source_inventory,image_path]
    out_report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,summary=summary,
                    sources={str(p.relative_to(ROOT)):bg.digest(p) for p in sources},
                    source_bulk_hashes=report['bulk_artifacts'],
                    artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},
                    bulk_artifacts={'active-labels.npy':bg.digest(args.output/'active-labels.npy')})
    bg.write_json(args.review_bundle/'report.json',out_report);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
