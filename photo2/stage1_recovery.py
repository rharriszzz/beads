"""R238 bounded supplement. Detector never reads references or adjudications.

Locations are colored samples or reflections, never inferred bead centers.
Frozen baseline proposals are retained verbatim. All merge/reject traces survive.
"""
from __future__ import annotations
import argparse
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-r238-mpl")
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from matplotlib.colors import rgb_to_hsv
from photo2.stage1_pilot import ROOT, read, save, sha, contains

BUNDLE = ROOT/'photo2/review/r238'
RULES = dict(color_radius_d=.32, color_min_area_d2=.10, color_inset_d=.09,
             color_value_q90=.50, color_hue_tolerance=18., color_sat_fraction=1.0,
             reflection_small_sigma=.70, reflection_large_sigma_d=.30,
             reflection_response=.045, reflection_peak_value=.28,
             reflection_peak_sat=.48, dark_value=.40, dark_fraction=.18,
             dark_sector_fraction=.55, ring_inner_d=.12, ring_outer_d=.32,
             reflection_merge_d=.32, old_snap_d=.14,
             basin_sigma_d=.10, basin_peak_spacing_d=.45, color_close_pixels=2)


def prepare():
    """Archive automatic candidates/trace in fixed halos, with no reference labels."""
    from photo2.stage1_pilot import assemble_candidates
    import copy
    protocol=read(ROOT/'photo2/review/r235/protocol.json')
    pp=copy.deepcopy(protocol)
    for s in pp['sections']:
        a,b,c,d=s['box']; s['box']=[a-30,b-30,c+30,d+30]
    baseline=assemble_candidates(pp)
    pool=read(ROOT/'photo2/output/r231/profile-pool.json')
    profiles=np.load(ROOT/'photo2/output/r231/profiles.npz')
    old=read(ROOT/'photo2/output/r238/old-detector.json')
    params=read(ROOT/'photo2/review/r231/points.json')['parameters']
    params['saturation_floor']=old['parameters']['saturation_floor']
    result=dict(parameters=params, detector_parameters=old['parameters'], sections=[],
                image_sha256=protocol['image_sha256'], sources={})
    for s,halo in zip(protocol['sections'],pp['sections']):
        colors=[]
        selected={tuple(p['xy']) for p in baseline['sections'][s['id']] if p['color']!='black'}
        for i,p in enumerate(pool):
            if contains(halo['box'],p['xy']) and tuple(p['xy']) not in selected:
                colors.append(dict(p, source_id=f'pool:{i}', old_reason='spacing' if profiles['accepted'][i] else 'profile',
                                   old_valid_cuts=int(profiles['valid'][i].sum()),
                                   old_color_cuts=int((profiles['color_fraction'][i]>=.75).sum())))
        black=[]
        for stage in ['points','excluded','reflection_rejections']:
            for i,p in enumerate(old[stage]):
                if stage!='reflection_rejections' and p['kind']!='dark-reflection':continue
                if contains(halo['box'],p['source_xy']):
                    black.append(dict(xy=p['source_xy'],color='black',source_id=f'{stage}:{i}',
                                      old_reason=p.get('reason','passed detector; downstream R192 or baseline')))
        result['sections'].append(dict(id=s['id'],box=s['box'],halo=halo['box'],
                                      baseline=baseline['sections'][s['id']],colored_pool=colors,black_pool=black))
    for name in ['beads-photo-2.jpg','photo2/output/r231/profile-pool.json','photo2/output/r231/profiles.npz',
                 'photo2/auto_label_beads.py','photo2/output/r238/old-detector.json',
                 'photo2/review/r231/points.json','photo2/review/r192/candidates.json']:
        result['sources'][name]=sha(ROOT/name)
    save(BUNDLE/'inputs.json',result)


def local_fields(rgb, params, rules):
    hsv=rgb_to_hsv(rgb.astype(np.float32)/255); v=hsv[...,2];d=params['native_diameter']
    masks={}; depths={}
    for mode,hue in enumerate(params['hue_modes_degrees'],1):
        q90=params['learned_family_parameters'][str(mode)]['diffuse_q90']
        mask=(abs((hsv[...,0]*360-hue+180)%360-180)<rules['color_hue_tolerance'])
        mask&=(hsv[...,1]>params['saturation_floor']*rules['color_sat_fraction'])&(v>rules['color_value_q90']*q90)
        masks[mode]=mask;depths[mode]=ndi.distance_transform_edt(mask)
    response=ndi.gaussian_filter(v,rules['reflection_small_sigma'])-ndi.gaussian_filter(v,rules['reflection_large_sigma_d']*d)
    return hsv,masks,depths,response


def detect_section(rgb, section, params, rules=RULES, native=True):
    """Only image, learned appearance, automatic pools and box; no truth inputs."""
    x0,y0,x1,y1=section['halo'];patch=rgb[y0:y1,x0:x1]
    hsv,masks,depths,response=local_fields(patch,params,rules)
    v=hsv[...,2];d=params['native_diameter']; yy,xx=np.indices(v.shape)
    offset=np.array([x0,y0]); traces=[]; additions=[]
    names={i:min({'red':0,'yellow':45},key=lambda n:abs((h-{'red':0,'yellow':45}[n]+180)%360-180)) for i,h in enumerate(params['hue_modes_degrees'],1)}
    bases=section['baseline']
    def reject(p,reason):p['decision']=reason;traces.append(p)
    colored=[]
    for p0 in section['colored_pool']:
        p=dict(p0,color=names[p0['mode']],arm='rejected'); xy=np.array(p['xy'])-offset;x,y=xy.astype(int)
        disk=(xx-x)**2+(yy-y)**2<=(rules['color_radius_d']*d)**2
        p['support_pixels']=int((masks[p['mode']]&disk).sum());p['inset']=float(depths[p['mode']][y,x]);p['value']=float(v[y,x])
        if p['support_pixels']<rules['color_min_area_d2']*d*d or p['inset']<rules['color_inset_d']*d:
            reject(p,'insufficient coherent colored patch');continue
        p['score']=p['value']*min(p['inset'],.2*d);colored.append(p)
    basins={};enclosed=np.zeros(v.shape,bool)
    for mode,mask in masks.items():
        smooth=ndi.gaussian_filter(v,rules['basin_sigma_d']*d)
        peaks=peak_local_max(smooth,min_distance=max(2,round(rules['basin_peak_spacing_d']*d)),labels=mask,exclude_border=False)
        markers=np.zeros(v.shape,int)
        for i,(y,x) in enumerate(peaks,1):markers[y,x]=i
        basins[mode]=watershed(-smooth,markers,mask=mask)
        enclosed|=ndi.binary_fill_holes(ndi.binary_closing(mask,iterations=rules['color_close_pixels']))
    def basin_at(p,mode):
        x,y=np.rint(np.array(p['xy'])-offset).astype(int)
        label=int(basins[mode][y,x])
        if not label:
            radius=rules['old_snap_d']*d
            nearby=(xx-x)**2+(yy-y)**2<=radius**2
            distances=np.where(nearby&(basins[mode]>0),(xx-x)**2+(yy-y)**2,np.inf)
            if np.isfinite(distances).any():
                iy,ix=np.unravel_index(distances.argmin(),v.shape);label=int(basins[mode][iy,ix])
        return label
    for p in sorted(colored,key=lambda p:(-p['score'],p['source_id'])):
        basin=basin_at(p,p['mode']);p['basin']=basin
        match=next((q for q in bases+additions if q['color']==p['color'] and basin and basin_at(q,p['mode'])==basin),None)
        if match:
            p['merged_into']=match['source_id'];reject(p,'same colored brightness basin; identity not proven');continue
        if not basin:reject(p,'no supported brightness basin');continue
        p['decision']='accepted';traces.append(p);additions.append(p)
    # Existing coarse candidates refined only inside a fixed small neighborhood.
    existing=[]
    for p0 in section['black_pool']:
        p=dict(p0,arm='rejected');xy=np.array(p['xy'])-offset;x,y=np.rint(xy).astype(int)
        disk=(xx-x)**2+(yy-y)**2<=(rules['old_snap_d']*d)**2
        iy,ix=np.unravel_index(np.where(disk,response,-np.inf).argmax(),v.shape)
        p['original_xy']=p['xy'];p['xy']=[int(ix+x0),int(iy+y0)];existing.append(p)
    pools=[existing]
    if native:
        peaks=peak_local_max(response,min_distance=2,threshold_abs=rules['reflection_response'],exclude_border=2)
        pools.append([dict(xy=[int(x+x0),int(y+y0)],color='black',source_id=f'native:{x+x0}:{y+y0}',old_reason='new native search',arm='native') for y,x in peaks])
    for pool in pools:
        for p in sorted(pool,key=lambda p:(-float(response[p['xy'][1]-y0,p['xy'][0]-x0]),p['source_id'])):
            x,y=np.asarray(p['xy'])-offset;rr=np.hypot(xx-x,yy-y)
            ring=(rr>rules['ring_inner_d']*d)&(rr<=rules['ring_outer_d']*d)
            dark=v<rules['dark_value']; angles=np.arctan2(yy-y,xx-x)
            sectors=[ring&(angles>=a)&(angles<a+np.pi/2) for a in [-np.pi,-np.pi/2,0,np.pi/2]]
            fractions=[float(dark[z].mean()) if z.any() else 0. for z in sectors]
            p.update(response=float(response[y,x]),value=float(v[y,x]),saturation=float(hsv[y,x,1]),
                     dark_fraction=float(dark[ring].mean()),max_dark_sector=max(fractions))
            if p['response']<rules['reflection_response'] or p['value']<rules['reflection_peak_value'] or p['saturation']>rules['reflection_peak_sat']:
                reject(p,'not a compact bright low-chroma reflection');continue
            if enclosed[y,x]:
                reject(p,'reflection enclosed by colored support');continue
            if p['dark_fraction']<rules['dark_fraction'] or p['max_dark_sector']<rules['dark_sector_fraction']:
                reject(p,'insufficient directional dark support');continue
            nearby=[q for q in bases+additions if q['color']=='black' and np.linalg.norm(np.array(q['xy'])-p['xy'])<rules['reflection_merge_d']*d]
            if nearby:p['merged_into']=nearby[0]['source_id'];reject(p,'near existing reflection; identity not proven');continue
            p['decision']='accepted';traces.append(p);additions.append(p)
    for i,p in enumerate(additions,1):p['candidate_id']=f"{section['id']}-A{i:02d}"
    return dict(section=section['id'],box=section['box'],halo=section['halo'],baseline=bases,additions=additions,traces=traces)


def render(rgb,result,out):
    box=result['halo'];crop=Image.fromarray(rgb).crop(box);scale=4
    raw=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST)
    marked=raw.copy();draw=ImageDraw.Draw(marked);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    for p in result['baseline']+result['additions']:
        x,y=(np.array(p['xy'])-box[:2])*scale
        col='#00e5ff' if p in result['baseline'] else '#ffe030' if p['arm']=='rejected' else '#55ff66'
        draw.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
        if 'arm' in p:
            label=p['candidate_id'].split('-')[1];draw.text((x+6,y-14),label,fill=col,font=font,stroke_width=2,stroke_fill='black')
    canvas=Image.new('RGB',(raw.width*2,raw.height+45),'white');canvas.paste(raw,(0,45));canvas.paste(marked,(raw.width,45))
    ImageDraw.Draw(canvas).text((8,8),f"{result['section']} raw | cyan baseline; yellow recovered pool; green native. Proposals, not centers.",fill='black',font=font)
    canvas.save(out)


def run(split,output):
    inputs=read(BUNDLE/'inputs.json');image=ROOT/'beads-photo-2.jpg'
    if sha(image)!=inputs['image_sha256']:raise ValueError('Changed image')
    rgb=np.asarray(Image.open(image).convert('RGB'));out=Path(output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for s in inputs['sections']:
        if (s['id'].startswith('D')) != (split=='development'):continue
        r=detect_section(rgb,s,inputs['parameters']);results.append(r);render(rgb,r,out/f"{s['id']}-comparison.png")
        print(s['id'],[(p['candidate_id'],p['color'],p['xy'],p['arm']) for p in r['additions']])
    save(out/'candidates.json',dict(split=split,rules=RULES,script_sha256=sha(Path(__file__)),inputs_sha256=sha(BUNDLE/'inputs.json'),results=results))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','development','transfer']);ap.add_argument('--output')
    args=ap.parse_args()
    if args.command=='prepare':prepare()
    else:run(args.command,args.output or BUNDLE/args.command)
