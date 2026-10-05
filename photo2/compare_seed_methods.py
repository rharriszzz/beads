"""R231: compare four image-derived seed hypotheses, without region growth.

Frozen appearance is an input; review crops are chosen only after extraction.
No maker bead/adjacency data, centerline or simulated positions are consulted.
"""
import argparse
import base64
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-seed-methods-mpl')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from skimage.feature import peak_local_max
from skimage.morphology import h_maxima

from auto_label_beads import ROOT, sha
from bead_evidence_inventory import hue_distance

METHODS = {
    'old': ('Old seeds: rejected basis', 'Frozen R229 starting points, including fallback seeds.'),
    'M1': ('M1: brightness peaks', 'Color-normalized smoothing, prominent brightness hills, learned brightness floor; no distance multiplier or old fallback.'),
    'M2': ('M2: deeper color support', 'Maxima of distance to color support edge; require at least 0.18 apparent diameters of inset.'),
    'M3': ('M3: broad interior patches', 'Tighter hue and saturation plus diffuse brightness; require a 0.17-diameter-radius disk to pass those pixel tests.'),
    'M4': ('M4: nearby profile support', 'A colored bright middle and darker flanks on at least two of three nearby cuts in each of two perpendicular directions.')
}


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def suppress(points, diameter, spacing=.5):
    chosen=[]
    for p in sorted(points, key=lambda p:(-p['score'],p['xy'][1],p['xy'][0],p['mode'])):
        nearby=[q for q in chosen if q['mode']==p['mode']]
        if any(np.linalg.norm(np.asarray(q['xy'])-p['xy']) < spacing*diameter for q in nearby):
            continue
        chosen.append(p)
    return sorted(chosen,key=lambda p:(p['xy'][1],p['xy'][0],p['mode']))


def maxima_points(score, support, eligible, inset, minimum, mode, diameter, floor):
    peaks=h_maxima(score.astype(np.float32),max(.001,float(floor)))&support
    labels,_=ndi.label(peaks)
    points=[]; radius=max(1,round(.15*diameter))
    for label,sl in enumerate(ndi.find_objects(labels),1):
        if sl is None:continue
        yy,xx=np.nonzero(labels[sl]==label);yy+=sl[0].start;xx+=sl[1].start
        best=np.argmax(score[yy,xx]);y,x=int(yy[best]),int(xx[best])
        # A glint can help support a disk but is not chosen as a colored seed.
        if not eligible[y,x]:
            ys=slice(max(0,y-radius),min(score.shape[0],y+radius+1))
            xs=slice(max(0,x-radius),min(score.shape[1],x+radius+1))
            sy,sx=np.mgrid[ys,xs]
            ok=eligible[ys,xs]&support[ys,xs]&(np.hypot(sx-x,sy-y)<=radius)&(inset[ys,xs]>=minimum)
            if not ok.any():continue
            value=np.where(ok,score[ys,xs]-1e-5*np.hypot(sx-x,sy-y),-np.inf)
            j,i=np.unravel_index(value.argmax(),value.shape);y,x=int(sy[j,i]),int(sx[j,i])
        if inset[y,x]<minimum:continue
        points.append(dict(xy=[x,y],mode=mode,score=float(score[y,x]),support_inset=float(inset[y,x])))
    return points


def methods(image, report, arrays, baseline, patch_rule='strict'):
    """Input-only extraction; baseline positions are automatic proposals."""
    d=report['parameters']['native_diameter'];modes=report['parameters']['detector']['hue_modes_degrees']
    sat_floor=report['parameters']['detector']['saturation_floor']
    hsv=rgb_to_hsv(image.astype(np.float32)/255);v=hsv[...,2]
    median=ndi.median_filter(v,size=max(3,int(.20*d)//2*2+1))
    diffuse=np.where(arrays['reflections']>0,median,v).astype(np.float32)
    result={'old':[dict(xy=p['marker_xy'],mode=p['appearance_mode'],score=0.,source_seed=p['seed_number']) for p in baseline]}
    for key in ['M1','M2','M3']:result[key]=[]
    fields={};params={};sigma=max(.8,.07*d)
    for mode,hue in enumerate(modes,1):
        error=hue_distance(hsv[...,0]*360,hue)
        attached=(arrays['reflections']>0)&arrays['domain']&(arrays['family']==mode)
        support=arrays['domain']&(arrays['family']==mode)&((error<18)|attached)
        eligible=support&~(arrays['reflections']>0)&(error<18)
        depth=ndi.distance_transform_edt(support).astype(np.float32)
        weight=ndi.gaussian_filter(support.astype(np.float32),sigma)
        smooth=ndi.gaussian_filter(diffuse*support,sigma)/np.maximum(weight,1e-6)
        q35,q65,q90=np.quantile(diffuse[support],[.35,.65,.90]).tolist()
        qbright=max(q65,.5*q90)
        bright_score=np.where(support & (smooth>=qbright),smooth,0).astype(np.float32)
        result['M1']+=maxima_points(bright_score,support,eligible,depth,max(1.5,.06*d),mode,d,.08*q90)
        deep_score=np.where(support&(diffuse>=.45*q90),ndi.gaussian_filter(depth,.65),0).astype(np.float32)
        result['M2']+=maxima_points(deep_score,support,eligible,depth,.18*d,mode,d,max(.7,.03*d))
        tight_floor=max(q65,.60*q90) if patch_rule=='strict' else max(q35,.45*q90)
        tight=support&(((error<12)&(hsv[...,1]>=.70*sat_floor))|attached)&(diffuse>=tight_floor)
        tight_depth=ndi.distance_transform_edt(tight).astype(np.float32)
        patch_score=tight_depth*(.7+.3*np.clip(diffuse/max(q90,.02),0,1))
        result['M3']+=maxima_points(patch_score,tight,eligible,tight_depth,.17*d,mode,d,max(.7,.03*d))
        fields[mode]=dict(support=support,smooth=smooth,depth=depth,tight=tight,tight_depth=tight_depth)
        params[mode]=dict(learned_hue_degrees=hue,diffuse_q35=q35,diffuse_q65=q65,diffuse_q90=q90,
            M1_brightness_floor=qbright,M3_pixel_brightness_floor=tight_floor)
    for key in ['M1','M2','M3']:result[key]=suppress(result[key],d)
    candidates={}
    for key in ['old','M1','M2','M3']:
        for p in result[key]:candidates[(p['xy'][0],p['xy'][1],p['mode'])]=p
    pool=[dict(xy=[x,y],mode=m) for x,y,m in sorted(candidates,key=lambda p:(p[1],p[0],p[2]))]
    profile=profile_measurements(image,diffuse,pool,modes,d,sat_floor,params)
    result['M4']=suppress([dict(**p,score=float(profile['score'][i]),profile_index=i)
        for i,p in enumerate(pool) if profile['accepted'][i]],d)
    for key,rows in result.items():
        for i,p in enumerate(rows,1):p.update(id=f'{key}:{i}',method=key,status='Unreviewed colored interior proposal; no bead identity or center claim')
    parameters=dict(native_diameter=d,hue_modes_degrees=modes,learned_family_parameters=params,
        reflection_median_window=max(3,int(.20*d)//2*2+1),masked_gaussian_sigma=sigma,
        same_family_spacing=.5*d,nonreflection_seed_shift_radius=round(.15*d),
        M1=dict(hue_tolerance=18,minimum_inset=max(1.5,.06*d),prominence_fraction=.08),
        M2=dict(minimum_color_support_inset=.18*d,minimum_diffuse_fraction=.45),
        M3=dict(hue_tolerance=12,saturation_fraction_of_learned_floor=.70,patch_radius=.17*d,
            brightness_rule=patch_rule,brightness_quantile=.65 if patch_rule=='strict' else .35,
            minimum_diffuse_fraction=.60 if patch_rule=='strict' else .45),
        M4=dict(angles_degrees=[0,45,90,135],offsets_pixels=[-.10*d,0,.10*d],
            middle_halfwidth=.12*d,flank_distances=[.30*d,.65*d],minimum_color_fraction=.75,
            minimum_brightness_fraction=.5,minimum_drop_absolute=.04,minimum_drop_relative=.10,
            required_paths_per_direction=2,required_perpendicular_directions=2))
    return result,fields,profile,parameters


def profile_measurements(image,diffuse,pool,modes,d,sat_floor,params):
    offsets=np.array([-.1,0,.1],np.float32)*d
    along=np.arange(-round(.75*d),round(.75*d)+1,dtype=np.float32)
    angle=np.deg2rad([0,45,90,135]);direction=np.column_stack((np.cos(angle),np.sin(angle))).astype(np.float32)
    normal=np.column_stack((-direction[:,1],direction[:,0]))
    origins=np.asarray([p['xy'] for p in pool],np.float32)
    xy=origins[:,None,None,None,:]+direction[None,:,None,None,:]*along[None,None,None,:,None]+normal[None,:,None,None,:]*offsets[None,None,:,None,None]
    coordinates=[xy[...,1],xy[...,0]]
    colors=np.stack([ndi.map_coordinates(image[...,c].astype(np.float32)/255,coordinates,order=1,mode='nearest') for c in range(3)],axis=-1)
    hsv=rgb_to_hsv(colors)
    value=ndi.map_coordinates(diffuse,coordinates,order=1,mode='nearest')
    hue=np.array([modes[p['mode']-1] for p in pool])[:,None,None,None]
    error=abs((hsv[...,0]*360-hue+180)%360-180)
    compatible=(error<18)&(hsv[...,1]>.6*sat_floor)
    middle=abs(along)<=.12*d;left=(along<=-.30*d)&(along>=-.65*d);right=(along>=.30*d)&(along<=.65*d)
    center=np.median(value[...,middle],axis=-1)
    color_fraction=compatible[...,middle].mean(axis=-1)
    drop=np.minimum(center-np.quantile(value[...,left],.20,axis=-1),center-np.quantile(value[...,right],.20,axis=-1))
    floor=np.array([max(.5*params[p['mode']]['diffuse_q90'],params[p['mode']]['diffuse_q35']) for p in pool])[:,None,None]
    valid=(color_fraction>=.75)&(center>=floor)&(drop>=np.maximum(.04,.10*center))
    count=valid.sum(axis=-1)
    pairs=np.stack([np.minimum(count[:,0],count[:,2]),np.minimum(count[:,1],count[:,3])],axis=-1)
    accepted=(pairs>=2).any(axis=-1)
    per_direction=np.mean(np.where(valid,np.maximum(drop,0)*center,0),axis=-1)
    pair_score=np.stack([np.minimum(per_direction[:,0],per_direction[:,2]),np.minimum(per_direction[:,1],per_direction[:,3])],axis=-1)
    pair_score=np.where(pairs>=2,pair_score,0)
    return dict(pool=pool,xy=xy,rgb=colors,hsv=hsv,value=value,along=along,offsets=offsets,
        valid=valid,count=count,center=center,drop=drop,color_fraction=color_fraction,
        accepted=accepted,score=pair_score.max(axis=-1),best_pair=pair_score.argmax(axis=-1))


def contexts(rows,shape):
    # All diagnostic positions are selected after every method finishes.
    h,w=shape;old=json.loads((ROOT/'photo2/review/r229/review-locations.json').read_text())['rows']
    out=[]
    for case in old[:2]:
        x,y=case['focus_marker_xy'];out.append(dict(name=case['name'],center=[x,y],focus_old=case['focus_seed'],selection='Earlier automatic review context'))
    points=np.asarray([p['xy'] for p in rows['old']],float)
    center=(points.min(axis=0)+points.max(axis=0))/2
    theta=np.arctan2(points[:,1]-center[1],points[:,0]-center[0])
    radius=np.linalg.norm(points-center,axis=1)
    for name,angle in [('Right',0),('Lower right',np.pi/4),('Bottom',np.pi/2),('Lower left',3*np.pi/4),('Left',np.pi)]:
        delta=abs((theta-angle+np.pi)%(2*np.pi)-np.pi)
        group=np.where(delta<np.pi/8)[0]
        if not len(group):group=np.argsort(delta)[:20]
        target=np.median(radius[group]);score=delta[group]*3+abs(radius[group]-target)/max(target,1)
        chosen=points[group[np.argmin(score)]].astype(int).tolist()
        out.append(dict(name=name,center=chosen,focus_old=None,selection='Post-extraction old-proposal angle sector and median radius; not selected by new-method success'))
    for p in out:
        x,y=p['center'];p['box']=[max(0,x-90),max(0,y-70),min(w,x+90),min(h,y+70)]
        p['slug']=p['name'].lower().replace(' ','-')
    return out


def visible(rows,box):
    x0,y0,x1,y1=box
    return [p for p in rows if x0<=p['xy'][0]<x1 and y0<=p['xy'][1]<y1]


def panel(image,rows,box,width=540,patch_radius=None,focus=None):
    x0,y0,x1,y1=box;raw=image[y0:y1,x0:x1].copy()
    points=visible(rows,box)
    for p in points:
        x,y=p['xy'];raw[y-y0,x-x0]=[255,150,25] if p['method']=='old' else [0,225,255]
    height=round(width*(y1-y0)/(x1-x0));result=Image.fromarray(raw).resize((width,height),Image.Resampling.NEAREST)
    draw=ImageDraw.Draw(result);scale=width/(x1-x0)
    for p in points:
        x,y=p['xy'];sx=(x-x0+.5)*scale;sy=(y-y0+.5)*scale
        r=patch_radius*scale if patch_radius is not None else 4
        color=(40,255,120) if patch_radius is not None else (255,150,25) if p['method']=='old' else (0,225,255)
        draw.ellipse((sx-r,sy-r,sx+r,sy+r),outline=color,width=1)
        if focus and p['id']==focus:
            draw.text((sx+9,sy-25),'P',fill='white',font=ImageFont.truetype('DejaVuSans.ttf',19),stroke_fill='black',stroke_width=2)
    return result


def contact(image,rows,case,out):
    box=case['box'];height=round(540*(box[3]-box[1])/(box[2]-box[0]));rowheight=height+55
    result=Image.new('RGB',(1620,2*rowheight+35),'white');draw=ImageDraw.Draw(result)
    font=ImageFont.truetype('DejaVuSans.ttf',18)
    for i,key in enumerate(['raw','old','M1','M2','M3','M4']):
        x=(i%3)*540;y=(i//3)*rowheight
        pts=[] if key=='raw' else rows[key]
        title='Raw photo' if key=='raw' else METHODS[key][0]
        count='' if key=='raw' else f"{len(visible(pts,box))} seed proposals in this crop"
        draw.text((x+7,y+3),title,fill='black',font=font);draw.text((x+7,y+27),count,fill='#46505a',font=font)
        result.paste(panel(image,pts,box),(x,y+55))
    draw.text((7,2*rowheight+7),'One native pixel per point. Hollow rings are location guides. Counts are proposals, not bead counts.',fill='black',font=font)
    result.save(out/f"comparison-{case['slug']}.png")


def evidence(image,rows,fields,case,params,out):
    box=case['box'];x0,y0,x1,y1=box;sl=np.s_[y0:y1,x0:x1];width=540;height=round(width*(y1-y0)/(x1-x0))
    raw=image[sl];color=np.zeros_like(raw);bright=np.zeros_like(raw);deep=np.zeros_like(raw);tight=np.zeros_like(raw)
    for mode,f in fields.items():
        support=f['support'][sl];rgb=[255,210,25] if params['hue_modes_degrees'][mode-1]>15 and params['hue_modes_degrees'][mode-1]<100 else [230,50,65]
        color[support]=rgb
        b=np.clip(f['smooth'][sl],0,1);bright[support]=(np.stack([b,b,b],axis=-1)*255).astype(np.uint8)[support]
        d=np.clip(f['depth'][sl]/(.4*params['native_diameter']),0,1);deep[support]=(np.stack([d,d,d],axis=-1)*255).astype(np.uint8)[support]
        tight[f['tight'][sl]]=rgb
    p=min(visible(rows['M3'],box),key=lambda p:np.linalg.norm(np.asarray(p['xy'])-case['center']),default=None)
    patch=panel(image,rows['M3'],box,patch_radius=params['M3']['patch_radius'],focus=p['id'] if p else None)
    result=Image.new('RGB',(1620,2*(height+60)+40),'white');draw=ImageDraw.Draw(result);font=ImageFont.truetype('DejaVuSans.ttf',18)
    panels=[('Raw photo',raw),('Allowed color area: NOT bead ownership',color),('M1: normalized diffuse brightness',bright),
            ('M2: depth in allowed color area',deep),('M3: tighter bright/color pixels',tight),('M3: tested small disks and seeds',patch)]
    for i,(title,pixels) in enumerate(panels):
        x=i%3*540;y=i//3*(height+60);draw.text((x+7,y+5),title,fill='black',font=font)
        shown=pixels if isinstance(pixels,Image.Image) else Image.fromarray(pixels).resize((width,height),Image.Resampling.NEAREST)
        result.paste(shown,(x,y+60))
    draw.text((7,2*(height+60)+8),'Green circles enclose tested pixel disks, not bead outlines. P is a new proposal, not a confirmed interior.',fill='black',font=font)
    result.save(out/f"evidence-{case['slug']}.png")
    return None if p is None else dict(id=p['id'],xy=p['xy'],radius=params['M3']['patch_radius'],mode=p['mode'])


def profile_figure(image,profile,case,params,out):
    import os
    os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-seed-methods-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pool=profile['pool'];index=min(range(len(pool)),key=lambda i:np.linalg.norm(np.asarray(pool[i]['xy'])-case['center']))
    point=pool[index];angles=[0,2] if profile['best_pair'][index]==0 else [1,3]
    fig,axs=plt.subplots(2,3,figsize=(15,8),gridspec_kw={'width_ratios':[1.2,1,1]})
    x0,y0,x1,y1=case['box'];hue=params['hue_modes_degrees'][point['mode']-1]
    for row,direction in enumerate(angles):
        ax=axs[row,0];ax.imshow(image[y0:y1,x0:x1],extent=(x0,x1,y1,y0),interpolation='nearest')
        for j,c in enumerate(['#24b8ff','#21ef78','#ffa826']):
            xy=profile['xy'][index,direction,j];ax.plot(xy[:,0],xy[:,1],color=c,lw=.9)
        ax.scatter(*point['xy'],s=30,facecolors='none',edgecolors='white');ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
        ax.set_title(f"Raw photo: {45*direction}° cuts through {tuple(point['xy'])}");ax.set_axis_off()
        for j,c in enumerate(['#0089bd','#169a52','#d87700']):
            x=profile['along'];offset=profile['offsets'][j]
            axs[row,1].plot(x,profile['value'][index,direction,j],color=c,label=f'offset {offset:+.1f}px')
            delta=(profile['hsv'][index,direction,j,:,0]*360-hue+180)%360-180
            delta=np.where(profile['hsv'][index,direction,j,:,1]>.15,delta,np.nan)
            axs[row,2].plot(x,delta,color=c)
        for ax in axs[row,1:]:
            ax.axvspan(-.12*params['native_diameter'],.12*params['native_diameter'],color='#00cbd2',alpha=.15)
            for lo,hi in [(-.65,-.30),(.30,.65)]:ax.axvspan(lo*params['native_diameter'],hi*params['native_diameter'],color='gray',alpha=.12)
            ax.axvline(0,color='black',lw=.7);ax.grid(alpha=.2);ax.set_xlabel('Distance from proposed point (native pixels)')
        axs[row,1].set_ylim(0,1.05);axs[row,1].set_title('Diffuse V: middle versus darker flanks');axs[row,1].legend(fontsize=8)
        axs[row,2].axhline(18,color='gray',ls='--',lw=.8);axs[row,2].axhline(-18,color='gray',ls='--',lw=.8)
        axs[row,2].set_ylim(-100,100);axs[row,2].set_title(f'Hue relative to learned {hue}°; low-S omitted')
    fig.suptitle(f"{case['name']}: M4 profile evidence at a candidate; passes profile rule: {bool(profile['accepted'][index])}. Paths are not seams.")
    fig.tight_layout();fig.savefig(out/f"profiles-{case['slug']}.png",dpi=110);plt.close(fig)
    return dict(xy=point['xy'],mode=point['mode'],profile_index=index,passes=bool(profile['accepted'][index]),directions=angles)


def viewer(image_path,rows,cases,params,out,install_alias=True):
    data=dict(methods=[dict(key=k,title=t,description=s,points=rows[k]) for k,(t,s) in METHODS.items()],
        contexts=[dict(name='Whole necklace',box=[0,0,2540,3182])]+cases,parameters=params,default_method='M3',default_context=1)
    groups=[]
    for key,points in rows.items():
        rects=''.join(f'<rect x="{p["xy"][0]}" y="{p["xy"][1]}" width="1" height="1" data-point="{p["id"]}"/>' for p in points)
        groups.append(f'<g id="points-{key}" fill="{"rgb(255,150,25)" if key=="old" else "rgb(0,225,255)"}" style="display:{"inline" if key=="M3" else "none"}">{rects}</g>')
    x0,y0,x1,y1=cases[0]['box']
    template=(ROOT/'photo2/seed_methods_viewer.html').read_text()
    html=(template.replace('__PHOTO__',base64.b64encode(image_path.read_bytes()).decode())
        .replace('__GROUPS__',''.join(groups)).replace('__VIEWBOX__',f'{x0} {y0} {x1-x0} {y1-y0}')
        .replace('__DATA__',json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')))
    (out/'index.html').write_text(html)
    if install_alias:(ROOT/'photo2/review/r224/seed-methods.html').write_text(html)
    save(out/'points.json',data)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r231')
    parser.add_argument('--patch-rule',choices=['strict','loose'],default='strict');args=parser.parse_args()
    if args.patch_rule=='loose' and args.output==ROOT/'photo2/review/r231':parser.error('Use a separate --output for a loose-patch diagnostic')
    out=args.output;out.mkdir(parents=True,exist_ok=True);routine=ROOT/'photo2/output/r231'
    if args.patch_rule=='loose':routine=routine/'loose'
    routine.mkdir(parents=True,exist_ok=True)
    prior=json.loads((ROOT/'photo2/review/r229/summary.json').read_text())
    for p,v in prior['source_sha256'].items():assert sha(ROOT/p)==v,p
    for p,v in prior['curated_sha256'].items():assert sha(ROOT/'photo2/review/r229'/p)==v,p
    seal=json.loads((ROOT/'photo2/review/r218/summary.json').read_text());archive=ROOT/'photo2/output/r218/pixel-masks.npz'
    assert sha(archive)==seal['mask_archive_sha256']
    with np.load(archive) as z:arrays={k:z[k] for k in ['domain','family','reflections']}
    report=json.loads((ROOT/'photo2/review/r218/regions.json').read_text());baseline=json.loads((ROOT/'photo2/review/r229/seeds.json').read_text())['seeds']
    photo=ROOT/'beads-photo-2.jpg';image=np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert('RGB'))
    rows,fields,profile,params=methods(image,report,arrays,baseline,args.patch_rule)
    print(json.dumps({'counts':{k:len(v) for k,v in rows.items()},'phase':'image-only extraction complete'}),flush=True)
    cases=contexts(rows,image.shape[:2]);reviews=[]
    for case in cases:
        contact(image,rows,case,out)
        focus=evidence(image,rows,fields,case,params,out)
        profile_focus=profile_figure(image,profile,case,params,out) if case['name'] in ['A','B'] else None
        reviews.append(dict(**case,counts={k:len(visible(v,case['box'])) for k,v in rows.items()},patch_focus=focus,profile_focus=profile_focus))
    save(out/'review-locations.json',dict(cases=reviews,selection='Diagnostic crops selected after all whole-photo extraction; no runtime coordinate priors'))
    install_alias=args.patch_rule=='strict' and out.resolve()==(ROOT/'photo2/review/r231').resolve()
    viewer(photo,rows,cases,params,out,install_alias)
    np.savez_compressed(routine/'fields.npz',**{f'{m}_{k}':v for m,f in fields.items() for k,v in f.items()})
    np.savez_compressed(routine/'profiles.npz',**{k:v for k,v in profile.items() if isinstance(v,np.ndarray)})
    save(routine/'profile-pool.json',profile['pool'])
    sources=['beads-photo-2.jpg','photo2/compare_seed_methods.py','photo2/seed_methods_viewer.html','photo2/refine_colored_masks.py',
        'photo2/segment_colored_beads.py','photo2/review/r218/regions.json','photo2/review/r229/seeds.json','photo2/review/r229/review-locations.json']
    payloads=['points.json','review-locations.json','index.html']+[p.name for p in sorted(out.glob('*.png'))]
    save(out/'summary.json',dict(request='R231',counts={k:len(v) for k,v in rows.items()},parameters=params,
        source_sha256={p:sha(ROOT/p) for p in sources},curated_sha256={p:sha(out/p) for p in payloads},
        frozen_mask_archive_sha256=sha(archive),routine_sha256={p.name:sha(p) for p in sorted(routine.iterdir()) if p.is_file()},
        existing_server_alias='photo2/review/r224/seed-methods.html' if install_alias else None,
        alias_sha256=sha(ROOT/'photo2/review/r224/seed-methods.html') if install_alias else None,
        production_extractor_changed=False,production_method_selected=False,region_growth_performed=False,
        manual_bead_data_read=False,geometry_fit_performed=False,
        reproduction='.venv/bin/python photo2/compare_seed_methods.py'+(' --patch-rule loose --output photo2/output/r231/loose-review' if args.patch_rule=='loose' else '')))


if __name__=='__main__':main()
