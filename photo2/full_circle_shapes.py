#!/usr/bin/env python3
"""R085: a pose-organized atlas of all visible shapes in one known necklace."""
from __future__ import annotations

import argparse
import colorsys
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_erosion
from skimage.measure import find_contours

from black_bead_walk import NBEADS, SIZE, font
from legacy_visibility import decode, instrument_source, render, wrapper
from neighbor_audit import projected_centers
from practice_legacy import ROOT, digest

HERE=ROOT/'photo2'
OUT=HERE/'output/full-circle-shapes'
REVIEW=HERE/'review/r085'


def choose_index(major_angle, phase_column):
    # phase = 720*i/13 mod 360; inverse of 2 modulo 13 is 7.
    candidates=np.arange((7*phase_column)%13,NBEADS,13)
    distance=np.abs((360*candidates/NBEADS-major_angle+180)%360-180)
    return int(candidates[np.argmin(distance)])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analyze-only',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    REVIEW.mkdir(parents=True,exist_ok=True)
    instrument=OUT/'instrument.pov'
    scene=OUT/'wrapper.pov'
    table=OUT/'layout.csv'
    source=(ROOT/'beads.pov').read_text()
    # Case 1 ID instrumentation and case 3 beauty use identical body proportions.
    for color in ('White','Black'):
        assert f'bead(shiny_opaque({color}), 0.8, 0.7, 1.0)' in source
    content=instrument_source(source)
    wrapped='#declare Helicity=1;\n'+wrapper({'colors':[0]*NBEADS,'groups':1},instrument.name,table)
    commands=[]
    if not args.analyze_only:
        if (OUT/'ids.png').exists():
            raise FileExistsError('Use --analyze-only; the one diagnostic render already exists')
        instrument.write_text(content)
        scene.write_text(wrapped)
        render(OUT,'ids',scene,'0',commands,width=SIZE[0],height=SIZE[1])
        (OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert instrument.read_text()==content and scene.read_text()==wrapped
    commands=json.loads((OUT/'commands.json').read_text())
    labels=decode(np.asarray(Image.open(OUT/'ids.png').convert('RGB')),NBEADS)
    assert labels.shape==(SIZE[1],SIZE[0])
    layout=np.loadtxt(table,delimiter=',')
    assert layout.shape==(NBEADS,7) and np.array_equal(layout[:,0],np.arange(NBEADS))
    assert np.allclose(layout[:,2],360*np.arange(NBEADS)/NBEADS)
    assert np.allclose(layout[:,3],360*np.arange(NBEADS)/6.5)
    centers=projected_centers(layout,*SIZE)
    angles=np.deg2rad(layout[:,2])
    tangent=np.column_stack((-np.sin(angles),np.cos(angles),np.zeros(NBEADS)))
    a,b=layout.copy(),layout.copy()
    a[:,4:7]+=.01*tangent
    b[:,4:7]-=.01*tangent
    direction=projected_centers(a,*SIZE)-projected_centers(b,*SIZE)
    tangent_degrees=np.rad2deg(np.arctan2(direction[:,1],direction[:,0]))
    # Reuse appearance; these two nonoverlapping black positions cover one another.
    walk=HERE/'output/black-bead-walk'
    beauty=np.maximum(np.asarray(Image.open(walk/'black-000.png').convert('RGB')),
                      np.asarray(Image.open(walk/'black-001.png').convert('RGB')))
    Image.fromarray(beauty).save(REVIEW/'white-reference.png')
    palette=np.array([[255,255,255]]+[[round(v*255) for v in colorsys.hsv_to_rgb(((2*i)%13)/13,.65,.88)] for i in range(NBEADS)],dtype=np.uint8)
    colored=palette[labels]
    border=np.zeros(labels.shape,bool)
    records=[]
    for index in range(NBEADS):
        mask=labels==index+1
        y,x=np.nonzero(mask)
        border|=mask & ~binary_erosion(mask)
        if len(x):
            box=[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]
            local=mask[box[1]:box[3],box[0]:box[2]]
            contours=[np.round(c[:,::-1]+[box[0]-1,box[1]-1],2).tolist()
                      for c in find_contours(np.pad(local,1).astype(float),.5)]
        else:
            box=None;contours=[]
        records.append(dict(index=index,major_angle=float(layout[index,2]),
                            minor_phase=float(layout[index,3]%360),phase_column=(2*index)%13,
                            projected_center=centers[index].tolist(),tangent_degrees=float(tangent_degrees[index]),
                            pixels=len(x),bbox=box,contours=contours))
    colored[border]=[70,70,70]
    Image.fromarray(colored).save(REVIEW/'full-circle.png')
    overlay=beauty.copy();overlay[border]=[0,170,200]
    Image.fromarray(overlay).save(REVIEW/'outlines-on-white.png')
    # All 52 occurrences of each of the 13 cross-section phases, in chain order.
    heat=Image.new('RGB',(13*65+100,52*16+85),'white');hd=ImageDraw.Draw(heat)
    hd.text((8,8),'Visible area over the complete circle (all 676 indices)',font=font(21),fill='black')
    for phase in range(13):hd.text((100+65*phase,43),f'{360*phase/13:.0f}°',font=font(15),fill='black')
    for turn in range(52):
        hd.text((4,85+turn*16),f'{360*turn/52:.0f}°',font=font(11),fill='black')
        for phase in range(13):
            index=turn*13+(7*phase)%13
            value=min(1,records[index]['pixels']/1100)
            color=(round(255-220*value),round(255-100*value),round(255-75*value))
            hd.rectangle((100+65*phase,85+turn*16,163+65*phase,99+turn*16),fill=color)
    heat.save(REVIEW/'visibility-grid.png')
    selected=[]
    for normalize,name in ((False,'screen-shapes.png'),(True,'tangent-shapes.png')):
        tile=112
        atlas=Image.new('RGB',(13*tile+110,12*tile+90),'white');draw=ImageDraw.Draw(atlas)
        title='Projected visible shapes' if not normalize else 'Visible shapes rotated so local rope tangent points right'
        draw.text((10,8),title+' · fixed pixel scale',font=font(21),fill='black')
        draw.text((10,36),'Rows: major-circle position. Columns: minor-circle phase. Gray cells: zero visible pixels.',font=font(16),fill='black')
        for phase in range(13):draw.text((110+tile*phase,65),f'{360*phase/13:.0f}°',font=font(15),fill='black')
        for row,major in enumerate(range(0,360,30)):
            draw.text((5,90+row*tile+40),f'{major}°',font=font(20),fill='black')
            for phase in range(13):
                index=choose_index(major,phase)
                r=records[index]
                if not normalize:selected.append(dict(requested_major_angle=major,phase_column=phase,index=index,actual_major_angle=r['major_angle']))
                cx,cy=np.rint(r['projected_center']).astype(int)
                mask=Image.fromarray(np.uint8(labels==index+1)*255).crop((cx-30,cy-30,cx+30,cy+30))
                if normalize:mask=mask.rotate(r['tangent_degrees'],resample=Image.Resampling.NEAREST)
                shape=Image.new('RGB',mask.size,'white');shape.paste('#202020',(0,0),mask)
                shape=shape.resize((90,90),Image.Resampling.NEAREST)
                x,y=110+phase*tile,90+row*tile
                if r['pixels']==0:draw.rectangle((x,y,x+105,y+105),fill='#eeeeee')
                else:atlas.paste(shape,(x+6,y+19))
                draw.text((x+4,y+2),f"{index}: {r['pixels']}px",font=font(11),fill='black')
        atlas.save(REVIEW/name)
    # Validate against the previously rendered 208 black-bead appearances.
    comparisons=[];prior_sources={}
    summary_path=HERE/'review/r084/angles-report.json'
    summary=json.loads(summary_path.read_text());prior_sources[str(summary_path.relative_to(ROOT))]=digest(summary_path)
    for location in summary['locations']:
        report_path=summary_path.parent/location['report']
        assert digest(report_path)==location['report_sha256']
        report=json.loads(report_path.read_text())
        scratch=walk if location['location']==0 else walk/f"angle-{location['nominal_angle']:03d}"
        arrays=[]
        for frame in report['frames']:
            path=scratch/f"black-{frame['index']:03d}.png"
            assert digest(path)==frame['png_sha256']
            arrays.append(np.asarray(Image.open(path).convert('RGB')))
        reference=np.maximum.reduce(arrays).astype(np.int16)
        for frame,array in zip(report['frames'],arrays):
            response=(reference-array.astype(np.int16)).max(axis=2)>10
            mask=labels==frame['index']+1
            n,m=int(response.sum()),int(mask.sum())
            assert n==frame['response_pixels']['10']
            intersection=int((response&mask).sum())
            comparisons.append(dict(index=frame['index'],response_pixels=n,id_pixels=m,
                                    overlap=intersection,precision=intersection/n if n else None,
                                    recall=intersection/m if m else None,
                                    outside_one_pixel=int((response&~binary_dilation(mask)).sum())))
    metrics={}
    for key in ('precision','recall'):
        values=[r[key] for r in comparisons if r['response_pixels']>=100 and r['id_pixels']>=100]
        metrics[key+'_median']=float(np.median(values));metrics[key+'_minimum']=float(min(values))
    metrics['compared_substantial']=sum(r['response_pixels']>=100 and r['id_pixels']>=100 for r in comparisons)
    metrics['response_pixels']=sum(r['response_pixels'] for r in comparisons)
    metrics['response_outside_one_pixel']=sum(r['outside_one_pixel'] for r in comparisons)
    data=dict(size=SIZE,beads=records,atlas_selection=selected)
    (REVIEW/'shapes.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    html=(HERE/'full_circle_shapes.html').read_text().replace('__SHAPE_DATA__',json.dumps(data,separators=(',',':')))
    (REVIEW/'review.html').write_text(html)
    sources=[Path(__file__),HERE/'full_circle_shapes.html',ROOT/'beads.pov',ROOT/'bead-shape.inc',HERE/'legacy_visibility.py',HERE/'legacy-visibility-body.inc',HERE/'neighbor_audit.py',HERE/'practice_legacy.py',HERE/'black_bead_walk.py',HERE/'verify_full_circle_shapes.py',HERE/'check_full_circle_viewer.cjs']
    result=dict(render_count=1,helicity=1,nbeads=NBEADS,size=SIZE,clock=0,
                nonzero_shapes=sum(r['pixels']>0 for r in records),
                zero_pixel_indices=[r['index'] for r in records if not r['pixels']],
                total_visible_pixels=int((labels>0).sum()),commands=commands,
                sources={**{str(p.relative_to(ROOT)):digest(p) for p in sources},**prior_sources},
                raw_artifacts={str(p.relative_to(ROOT)):digest(p) for p in (OUT/'ids.png',table,instrument,scene,OUT/'ids.log')},
                artifacts={p.name:digest(p) for p in sorted(REVIEW.iterdir()) if p.name!='report.json'},
                response_comparison=comparisons,response_summary=metrics)
    assert sum(r['pixels'] for r in records)==result['total_visible_pixels']
    (REVIEW/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('nonzero_shapes','total_visible_pixels','response_summary')},indent=2))


if __name__=='__main__':main()
