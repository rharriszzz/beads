#!/usr/bin/env python3
"""Estimate photo-2 shadow uncertainty and constrain shadowed edges by clear width.

Original curves remain inputs; outputs are provisional image-space corrections.
No bead order, camera calibration, physical width, or source patterns are used.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter1d, map_coordinates
from scipy.optimize import least_squares
from skimage.color import rgb2hsv

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = dict(samples=600, tangent_sigma_samples=2., clear_ratio=.85,
                  deep_shadow_ratio=.80, paper_hue=.90, paper_hue_radius=.10,
                  near_offsets=[8,16,24], reference_offsets=[70,90,110],
                  tangent_offsets=[-10,-5,0,5,10], paper_near_fraction=.8,
                  paper_reference_fraction=.9, huber_scale_px=4.,
                  residual_quantiles=[.1,.9], blend_sigma_samples=2.,
                  shadow_scan_step_px=4, shadow_scan_limit_px=180,
                  shadow_reference_offsets=[190,210,230], shadow_recovery_ratio=.90,
                  shadow_recovery_samples=3, zone_bridge_samples=2,
                  zone_min_strong_samples=5)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def cross(a,b):
    return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def resample(points, count):
    points=np.asarray(points,float)
    if not np.isfinite(points).all() or not np.array_equal(points[0],points[-1]):
        raise ValueError('Expected finite closed input curve')
    s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    if np.any(np.diff(s)<=0):
        raise ValueError('Repeated adjacent points')
    distance=np.linspace(0,s[-1],count,endpoint=False)
    xy=np.column_stack([np.interp(distance,s,points[:,j]) for j in range(2)])
    smooth=gaussian_filter1d(xy,PARAMETERS['tangent_sigma_samples'],axis=0,mode='wrap')
    tangent=np.roll(smooth,-1,axis=0)-np.roll(smooth,1,axis=0)
    tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    normal=np.column_stack([-tangent[:,1],tangent[:,0]])
    return xy,normal,distance,float(s[-1])


def normal_hits(xy, normal, curve):
    """Nearest line/segment intersection; sign is retained for both edges."""
    curve=np.asarray(curve,float);a=curve[:-1];v=np.diff(curve,axis=0)
    den=cross(normal[:,None,:],v[None,:,:]);delta=a[None,:,:]-xy[:,None,:]
    with np.errstate(divide='ignore',invalid='ignore'):
        t=cross(delta,v[None,:,:])/den;u=cross(delta,normal[:,None,:])/den
    valid=(np.abs(den)>1e-8)&(u>=0)&(u<=1)
    t[~valid]=np.inf
    index=np.argmin(np.abs(t),axis=1)
    return t[np.arange(len(xy)),index]


def sample_strip(hsv, edge, direction, tangent, offsets):
    points=(edge[:,None,None,:]+direction[:,None,None,:]*np.asarray(offsets)[None,:,None,None]
            +tangent[:,None,None,:]*np.asarray(PARAMETERS['tangent_offsets'])[None,None,:,None])
    values=np.stack([map_coordinates(hsv[...,j],points.reshape(-1,2).T[::-1],
                     order=1,mode='constant',cval=np.nan) for j in range(3)],axis=1)
    values=values.reshape(len(edge),len(offsets),-1,3)
    hue=np.abs(values[...,0]-PARAMETERS['paper_hue'])
    paper=(np.minimum(hue,1-hue)<PARAMETERS['paper_hue_radius'])&(values[...,1]>.2)&(values[...,2]>.15)
    return values,paper


def edge_quality(hsv, edge, direction, tangent):
    near,npaper=sample_strip(hsv,edge,direction,tangent,PARAMETERS['near_offsets'])
    far,fpaper=sample_strip(hsv,edge,direction,tangent,PARAMETERS['reference_offsets'])
    ratio=np.nanmedian(near[...,2],axis=(1,2))/np.nanmedian(far[...,2],axis=(1,2))
    valid=np.isfinite(near).all(axis=(1,2,3))&np.isfinite(far).all(axis=(1,2,3))
    paper_ok=(npaper.mean(axis=(1,2))>=PARAMETERS['paper_near_fraction'])&(fpaper.mean(axis=(1,2))>=PARAMETERS['paper_reference_fraction'])&valid
    return dict(ratio=ratio,paper_ok=paper_ok,near_paper_fraction=npaper.mean(axis=(1,2)),
                reference_paper_fraction=fpaper.mean(axis=(1,2)))


def fit_width(y, width, reliable, height):
    y=np.asarray(y);width=np.asarray(width);reliable=np.asarray(reliable,bool)
    if reliable.sum()<12 or np.ptp(y[reliable])<height*.5:
        raise ValueError('Insufficient clear width samples or vertical coverage')
    X=np.column_stack([np.ones(len(y)),(y-height/2)/(height/2)])
    initial=[float(np.median(width[reliable])),.01]
    fun=lambda p:(X@p-width)[reliable]
    free=least_squares(fun,initial,loss='soft_l1',f_scale=PARAMETERS['huber_scale_px'])
    monotone=least_squares(fun,initial,bounds=([1,0],[1000,500]),loss='soft_l1',f_scale=PARAMETERS['huber_scale_px'])
    expected=X@monotone.x
    residual=(width-expected)[reliable]
    band=np.quantile(residual,PARAMETERS['residual_quantiles'])
    return expected,dict(model='affine width versus image y; nonnegative slope; robust soft_l1',
                         coefficients=monotone.x.tolist(),free_coefficients=free.x.tolist(),
                         top_bottom_width_px=[float(monotone.x[0]-monotone.x[1]),float(monotone.x.sum())],
                         reliable_samples=int(reliable.sum()),reliable_y_range=[float(y[reliable].min()),float(y[reliable].max())],
                         residual_band_px=band.tolist(),median_absolute_residual_px=float(np.median(np.abs(residual))),
                         empirical_band_note='10th–90th percentile calibration residuals; not a statistical confidence interval')


def constrain(xy, inner, outer, width, expected, upper_residual, inner_clear, outer_clear, inner_shadow, outer_shadow):
    """One clear edge is fixed. Blend toward predicted width only at excess widths."""
    proposed=width-expected
    threshold=max(float(upper_residual),1.)
    allowed_inner=outer_clear&~inner_clear&inner_shadow
    allowed_outer=inner_clear&~outer_clear&outer_shadow
    strength=np.clip((proposed-threshold)/threshold,0,1)
    moved={'inner':inner.copy(),'outer':outer.copy()};center=xy.copy();weights=np.zeros(len(xy))
    unit=(inner-outer)/width[:,None]
    for name,allowed,anchor,target in [('inner',allowed_inner,outer,outer+unit*expected[:,None]),
                                       ('outer',allowed_outer,inner,inner-unit*expected[:,None])]:
        gain=np.clip(gaussian_filter1d(np.where(allowed,strength,0.),PARAMETERS['blend_sigma_samples'],mode='wrap'),0,1)
        gain=np.where(allowed& (proposed>0),gain,0.)
        moved[name]+=gain[:,None]*(target-moved[name])
        center+=gain[:,None]*((anchor+target)/2-xy)
        weights+=gain
    strong=(allowed_inner|allowed_outer)&(proposed>threshold)
    return moved['inner'],moved['outer'],center,weights,strong,allowed_inner,allowed_outer


def shadow_extent(hsv, edge, direction, tangent):
    offsets=np.arange(4,PARAMETERS['shadow_scan_limit_px']+1,PARAMETERS['shadow_scan_step_px'])
    scan,paper=sample_strip(hsv,edge,direction,tangent,offsets)
    far,far_paper=sample_strip(hsv,edge,direction,tangent,PARAMETERS['shadow_reference_offsets'])
    ref=np.ma.median(np.ma.masked_invalid(far[...,2]),axis=(1,2)).filled(np.nan)
    value=np.ma.median(np.ma.masked_invalid(scan[...,2]),axis=2).filled(np.nan)
    ratio=value/ref[:,None];valid_ref=far_paper.mean(axis=(1,2))>=.9
    recovered=(ratio>=PARAMETERS['shadow_recovery_ratio'])&(paper.mean(axis=2)>=.8)
    result=[]
    for i in range(len(edge)):
        if not valid_ref[i] or not np.isfinite(ratio[i]).all():
            result.append(dict(extent_px=None,censored=False,reason='reference_or_scan_unreliable'));continue
        found=next((j for j in range(len(offsets)-2) if recovered[i,j:j+3].all()),None)
        result.append(dict(extent_px=int(offsets[found]) if found is not None else int(offsets[-1]),
                           censored=found is None,reason='brightness_recovery_proxy'))
    return result


def zones(strong, xy, width, expected, band, inner_side, shift, shadow):
    """Group short gaps for reporting only; does not alter corrections."""
    n=len(strong);joined=strong.copy()
    for start in np.flatnonzero(strong&~np.roll(strong,-1)):
        for gap in range(1,PARAMETERS['zone_bridge_samples']+1):
            end=(start+gap+1)%n
            if strong[end]:
                joined[(start+np.arange(1,gap+1))%n]=True;break
    starts=np.flatnonzero(joined&~np.roll(joined,1));groups=[]
    for start in starts:
        ids=[int(start)];j=(start+1)%n
        while joined[j] and j!=start:
            ids.append(int(j));j=(j+1)%n
        chosen=[j for j in ids if strong[j]]
        if len(chosen)<PARAMETERS['zone_min_strong_samples']:continue
        side='inner' if np.mean(inner_side[chosen])>=.5 else 'outer'
        excess=width[chosen]-expected[chosen]
        ext=[shadow[side][j]['extent_px'] for j in chosen if shadow[side][j]['extent_px'] is not None]
        groups.append(dict(sample_ids=ids,strong_sample_ids=chosen,side=side,
                           center_xy=np.mean(xy[chosen],axis=0).tolist(),
                           bbox_xyxy=[float(xy[chosen,0].min()),float(xy[chosen,1].min()),float(xy[chosen,0].max()),float(xy[chosen,1].max())],
                           median_observed_width_px=float(np.median(width[chosen])),
                           median_expected_width_px=float(np.median(expected[chosen])),
                           median_edge_excess_px=float(np.median(excess)),
                           empirical_edge_excess_range_px=[float(np.median(excess)-band[1]),float(np.median(excess)-band[0])],
                           median_applied_center_shift_px=float(np.median(shift[chosen])),
                           max_applied_center_shift_px=float(np.max(shift[chosen])),
                           median_shadow_extent_outside_saved_edge_px=float(np.median(ext)) if ext else None,
                           shadow_extent_censored_samples=sum(shadow[side][j]['censored'] for j in chosen)))
    groups.sort(key=lambda g:(-len(g['strong_sample_ids']),g['center_xy'][0]))
    for i,g in enumerate(groups,1):g['zone']=i
    return groups


def closed(points):
    return np.vstack([points,points[0]]).tolist()


def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)


def draw_outputs(output, rgb, xy, corrected, inner, outer, new_inner, new_outer, strong, groups):
    def path(draw,points,color,width):draw.line([tuple(p) for p in np.vstack([points,points[0]])],fill=color,width=width,joint='curve')
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im);path(d,corrected,'black',10);path(d,corrected,'cyan',6)
    im.save(output/'centerline-corrected.png');im.thumbnail((1000,1253));im.save(output/'centerline-corrected-preview.png')
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im);path(d,xy,'yellow',4);path(d,corrected,'cyan',4)
    for i in np.flatnonzero(strong):
        for a,b in [(inner[i],new_inner[i]),(outer[i],new_outer[i])]:
            if np.linalg.norm(a-b)>.5:d.line([tuple(a),tuple(b)],fill='#ff4040',width=9)
    for g in groups:
        x,y=g['center_xy'];d.ellipse((x-19,y-19,x+19,y+19),fill='white',outline='black',width=2);d.text((x-10,y-14),str(g['zone']),font=font(24),fill='black')
    im.thumbnail((1000,1253));im.save(output/'shadow-overview.png')
    for name,box in [('left-comparison',(80,650,550,1500)),
                     ('lower-loop-comparison',(800,2320,1250,2920)),
                     ('bottom-reference',(1300,2870,1700,3150))]:
        w,h=box[2]-box[0],box[3]-box[1];panels=[]
        for mode in ['Photo','Original','Width-constrained']:
            im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
            if mode!='Photo':
                path(d,outer if mode=='Original' else new_outer,'lime',3)
                path(d,inner if mode=='Original' else new_inner,'orange' if mode=='Original' else 'lime',3)
                path(d,xy if mode=='Original' else corrected,'cyan',4)
            crop=im.crop(box);panel=Image.new('RGB',(w,h+50),'white');panel.paste(crop,(0,45));pd=ImageDraw.Draw(panel);pd.text((12,10),mode,font=font(22),fill='black');panels.append(panel)
        canvas=Image.new('RGB',(3*w,h+50),'white')
        for j,p in enumerate(panels):canvas.paste(p,(w*j,0))
        canvas.save(output/(name+'.png'))


def review_page(output, groups):
    parts=['<!doctype html><meta charset="utf-8"><title>Shadow and width review</title>',
           '<style>body{font:17px system-ui;max-width:1450px;margin:2em auto;padding:0 1em}img,svg{max-width:100%;height:auto}table{border-collapse:collapse}td,th{padding:.5em;border:1px solid #ccc}</style>',
           '<h1>Photo 2: shadow and width review</h1><p>Provisional corrections from the clearer edge. Full-image coordinates and widths use original 2540×3182 pixels. Cyan: centerline; green: edges; orange: original inner edge. The overview uses yellow for the old centerline and red for estimated edge movements.</p>']
    for name,title in [('left-comparison','Left bend'),('lower-loop-comparison','Lower loop, left side'),('bottom-reference','Bottom reference: some edge-quality checks fail'),('shadow-overview','Other candidate regions')]:
        encoded=base64.b64encode((output/(name+'.png')).read_bytes()).decode()
        parts.append(f'<h2>{title}</h2><img src="data:image/png;base64,{encoded}" alt="{title}">')
    parts.append('<h2>Width measurements</h2>'+ (output/'width-profile.svg').read_text())
    parts.append('<p>The green band shows the 10th–90th percentile calibration residuals, not a confidence interval. A shadow beyond the saved edge is different from an error in the saved edge.</p><table><tr><th>Zone</th><th>Edge</th><th>Estimated excess width</th><th>Empirical range</th><th>Center movement</th><th>Shadow beyond saved edge</th></tr>')
    for g in groups:
        lo,hi=g['empirical_edge_excess_range_px'];shade=g['median_shadow_extent_outside_saved_edge_px'];shade='unavailable' if shade is None else f'{shade:.0f} px'
        parts.append(f'<tr><td>{g["zone"]}</td><td>{g["side"]}</td><td>{g["median_edge_excess_px"]:.1f} px</td><td>{lo:.1f}–{hi:.1f} px</td><td>{g["median_applied_center_shift_px"]:.1f} px</td><td>{shade}</td></tr>')
    parts.append('</table><p>These are estimates conditional on the width model and edge-quality rules. Original input curves have not been replaced.</p>')
    (output/'review.html').write_text('\n'.join(parts))


def profile_svg(output, s, width, expected, band, both, length):
    W,H=1200,410;left,top,pw,ph=65,65,1090,280;low,high=70,130
    fx=lambda v:left+pw*v/length
    fy=lambda v:top+ph*(high-v)/(high-low)
    pts=lambda values:' '.join(f'{fx(x):.2f},{fy(y):.2f}' for x,y in zip(s,values))
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="14">',
           '<text x="65" y="25">Width around the necklace: gray measured; green model; blue both edges clear</text>',
           '<text x="65" y="46">Green band: calibration residual 10th–90th percentiles, not a confidence interval</text>']
    for tick in range(70,131,10):parts.append(f'<path d="M{left},{fy(tick)}h{pw}" stroke="#ddd"/><text x="20" y="{fy(tick)+5}">{tick}</text>')
    upper=np.column_stack([s,expected+band[1]]);lower=np.column_stack([s[::-1],(expected+band[0])[::-1]])
    polygon=' '.join(f'{fx(x):.2f},{fy(y):.2f}' for x,y in np.vstack([upper,lower]))
    parts.append(f'<polygon points="{polygon}" fill="#d7f0df"/><polyline points="{pts(width)}" fill="none" stroke="#888" stroke-width="1.5"/><polyline points="{pts(expected)}" fill="none" stroke="#138844" stroke-width="2"/>')
    for x,y in zip(s[both],width[both]):parts.append(f'<circle cx="{fx(x)}" cy="{fy(y)}" r="2.5" fill="#2454b8"/>')
    for tick in range(0,int(length)+1,1000):parts.append(f'<text x="{fx(tick)-12}" y="370">{tick}</text>')
    parts.append('<text x="430" y="400">Distance along saved centerline (image pixels)</text></g></svg>')
    (output/'width-profile.svg').write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/width-correction')
    parser.add_argument('--review-bundle',type=Path,help='Save curated question illustrations for committing (R065)')
    args=parser.parse_args();output=args.output;output.mkdir(parents=True,exist_ok=True)
    sources=[ROOT/'photo2/width_correction.py',ROOT/'photo2/boundary-splines-source.json',ROOT/'photo2/centerline.json',ROOT/'beads-photo-2.jpg',ROOT/'photo2/test_width_correction.py']
    original=json.loads(sources[1].read_text());center=json.loads(sources[2].read_text())
    if digest(sources[1])!=center['source_sha256'] or digest(sources[3])!=center['image_sha256']:raise ValueError('Bound source mismatch')
    rgb=np.array(Image.open(sources[3]).convert('RGB'));hsv=rgb2hsv(rgb)
    xy,n,s,length=resample(original['centerline_spline'],PARAMETERS['samples']);tangent=np.column_stack([n[:,1],-n[:,0]])
    hits={k:normal_hits(xy,n,original[k+'_spline']) for k in ['inner','outer']}
    if not np.isfinite(np.r_[hits['inner'],hits['outer']]).all() or not (hits['inner']*hits['outer']<0).all():raise ValueError('Cross sections do not straddle the centerline')
    edges={k:xy+n*hits[k][:,None] for k in hits};width=np.abs(hits['outer']-hits['inner'])
    quality={k:edge_quality(hsv,edges[k],n*np.sign(hits[k])[:,None],tangent) for k in hits}
    clear={k:(quality[k]['ratio']>=PARAMETERS['clear_ratio'])&quality[k]['paper_ok'] for k in hits}
    shadow={k:(quality[k]['ratio']<PARAMETERS['deep_shadow_ratio'])&quality[k]['paper_ok'] for k in hits};both=clear['inner']&clear['outer']
    expected,fit=fit_width(xy[:,1],width,both,rgb.shape[0]);band=np.array(fit['residual_band_px'])
    ni,no,nc,gain,strong,ai,ao=constrain(xy,edges['inner'],edges['outer'],width,expected,band[1],clear['inner'],clear['outer'],shadow['inner'],shadow['outer'])
    extent={k:shadow_extent(hsv,edges[k],n*np.sign(hits[k])[:,None],tangent) for k in hits}
    shift=np.linalg.norm(nc-xy,axis=1);groups=zones(strong,xy,width,expected,band,ai,shift,extent)
    sensitivity=[]
    for cutoff in [.80,.85,.90]:
        trusted={k:(quality[k]['ratio']>=cutoff)&quality[k]['paper_ok'] for k in hits};b=trusted['inner']&trusted['outer'];e,f=fit_width(xy[:,1],width,b,rgb.shape[0]);sens=constrain(xy,edges['inner'],edges['outer'],width,e,f['residual_band_px'][1],trusted['inner'],trusted['outer'],shadow['inner'],shadow['outer'])
        sensitivity.append(dict(clear_ratio=cutoff,fit=f,strong_samples=int(sens[4].sum()),left_median_shift_px=float(np.median(np.linalg.norm(sens[2]-xy,axis=1)[xy[:,0]<400]))))
    holdout=[]
    for block in range(8):
        hold=(s>=length*block/8)&(s<length*(block+1)/8)&both;train=both&~hold
        if not hold.any():continue
        try:
            e,f=fit_width(xy[:,1],width,train,rgb.shape[0])
        except ValueError as error:
            holdout.append(dict(arc_block=block,training_count=int(train.sum()),held_count=int(hold.sum()),unavailable=str(error)))
            continue
        err=width[hold]-e[hold]
        holdout.append(dict(arc_block=block,training_count=int(train.sum()),held_count=int(hold.sum()),mae_px=float(np.mean(np.abs(err))),median_error_px=float(np.median(err))))
    rows=[]
    for j in range(len(xy)):
        rows.append(dict(sample=j,s_px=float(s[j]),center_xy=xy[j].tolist(),inner_xy=edges['inner'][j].tolist(),outer_xy=edges['outer'][j].tolist(),observed_width_px=float(width[j]),expected_width_px=float(expected[j]),expected_width_band_px=[float(expected[j]+v) for v in band],
                         inner_clear=bool(clear['inner'][j]),outer_clear=bool(clear['outer'][j]),inner_brightness_ratio=float(quality['inner']['ratio'][j]),outer_brightness_ratio=float(quality['outer']['ratio'][j]),
                         strong_shadow_width_excess=bool(strong[j]),blend_weight=float(gain[j]),corrected_center_xy=nc[j].tolist(),center_shift_px=float(shift[j]),corrected_inner_xy=ni[j].tolist(),corrected_outer_xy=no[j].tolist(),shadow_extent={k:extent[k][j] for k in hits}))
    write_json(output/'measurements.json',rows)
    write_json(output/'corrected-curves.json',dict(image_sha256=center['image_sha256'],image_size=center['image_size'],source_centerline_sha256=digest(sources[2]),status='provisional width-constrained candidate, not adopted source geometry',points=closed(nc),inner_spline=closed(ni),outer_spline=closed(no)))
    draw_outputs(output,rgb,xy,nc,edges['inner'],edges['outer'],ni,no,strong,groups);profile_svg(output,s,width,expected,band,both,length)
    review_page(output,groups)
    report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,sources={str(p.relative_to(ROOT)):digest(p) for p in sources},fit=fit,sensitivity=sensitivity,spatial_holdout=holdout,zones=groups,
                summary=dict(sample_count=len(xy),arc_length_px=length,both_clear=int(both.sum()),one_clear=int((clear['inner']^clear['outer']).sum()),neither_clear=int((~clear['inner']&~clear['outer']).sum()),strong_samples=int(strong.sum()),strong_arc_fraction=float(strong.mean()),applied_samples=int((gain>1e-3).sum()),max_center_shift_px=float(shift.max()),left_sample_count=int((xy[:,0]<400).sum()),left_median_observed_width_px=float(np.median(width[xy[:,0]<400])),left_median_center_shift_px=float(np.median(shift[xy[:,0]<400]))),
                limitations=['Quality selection is heuristic; no manually measured true edges supplied.', 'Residual band describes clear-sample variability, not a calibrated confidence interval.', 'Brightness-recovery extent measures a shadow proxy beyond the saved edge, not true boundary error.', 'Only one clear edge plus a dark opposite side and excess width supports correction; neither-clear regions remain unchanged.', 'Nonnegative vertical slope is a hypothesis constrained by data, not measured camera tilt.', 'New curves are a candidate; original inputs and forward-model defaults remain unchanged.'])
    report['artifacts']={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file() and p.name!='report.json'}
    write_json(output/'report.json',report)
    if args.review_bundle:
        bundle=args.review_bundle;bundle.mkdir(parents=True,exist_ok=True)
        names=['left-comparison.png','lower-loop-comparison.png','bottom-reference.png','shadow-overview.png','width-profile.svg']
        for name in names:shutil.copyfile(output/name,bundle/name)
        html=(output/'review.html').read_text()
        for name in names:
            if name.endswith('.png'):
                encoded=base64.b64encode((output/name).read_bytes()).decode()
                html=html.replace('data:image/png;base64,'+encoded,name)
        (bundle/'review.html').write_text(html)
        write_json(bundle/'manifest.json',dict(command=report['command'],sources=report['sources'],
                    report_sha256=digest(output/'report.json'),summary=report['summary'],fit=fit,
                    artifacts={name:digest(bundle/name) for name in names+['review.html']}))
    print(json.dumps(dict(summary=report['summary'],fit=fit,zones=[{k:v for k,v in z.items() if k not in ['sample_ids','strong_sample_ids']} for z in groups]),indent=2))


if __name__=='__main__':main()
