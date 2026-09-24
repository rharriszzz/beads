#!/usr/bin/env python3
"""Compare direct paper-transition evidence with provisional width-only edges.

Frozen visual annotations are read only after all candidate optimizations.
"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates, gaussian_filter1d
from scipy.optimize import minimize
import transect_review as tr
import width_correction as wc

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = dict(search_radius_px=24, grid_step_px=1, paper_offsets_px=[35,45,55],
                  tangent_offsets_px=[-4,0,4], transition_offsets_px=[3,5,7],
                  chromaticity_scale_floor=.025, brightness_weight=.25,
                  image_weight=4., width_sigma_px=8., clear_position_sigma_px=8.,
                  other_position_sigma_px=20., second_difference_sigma_px=6.,
                  cost_smoothing_grid_sigma=1., interpolation='C1 cubic Hermite', optimizer_maxiter=400)


def sample_rgb(rgb, points):
    points = np.asarray(points)
    values = np.stack([map_coordinates(rgb[..., c].astype(float), points.reshape(-1,2).T[::-1],
                                      order=1, mode='constant', cval=np.nan) for c in range(3)], axis=1)
    return values.reshape(points.shape[:-1]+(3,))/255


def chromaticity(rgb):
    return rgb[..., [0,2]]/np.maximum(rgb.sum(axis=-1, keepdims=True), 1e-6)


def transition_scores(rgb, xy, n, tangent, original, base):
    delta = np.arange(-PARAMETERS['search_radius_px'], PARAMETERS['search_radius_px']+1., PARAMETERS['grid_step_px'])
    grid = base[:,:,None]+delta
    score = np.zeros_like(grid); diagnostics = []
    tang = np.array(PARAMETERS['tangent_offsets_px'])
    for side, sign in enumerate([-1,1]):
        offsets = original[:,side,None]+sign*np.array(PARAMETERS['paper_offsets_px'])
        p = xy[:,None,None,:]+offsets[:,:,None,None]*n[:,None,None,:]+tang[None,None,:,None]*tangent[:,None,None,:]
        paper = sample_rgb(rgb,p)
        chrom = chromaticity(paper)
        ref = np.nanmedian(chrom, axis=(1,2))
        scale = np.maximum(1.4826*np.nanmedian(np.abs(chrom-ref[:,None,None,:]),axis=(1,2)), PARAMETERS['chromaticity_scale_floor'])
        brightness = np.nanmedian(paper.max(axis=-1),axis=(1,2))
        # Magenta paper support, broad enough to include a dark cast shadow.
        valid = np.isfinite(paper).all(axis=(1,2,3)) & (ref[:,0]>.35) & (ref[:,1]>.28) & (brightness>.08)
        values = []
        for direction in [-1,1]:
            u = grid[:,side,:,None]+direction*sign*np.array(PARAMETERS['transition_offsets_px'])[None,None,:]
            p = xy[:,None,None,None,:]+u[:,:,:,None,None]*n[:,None,None,None,:]+tang[None,None,None,:,None]*tangent[:,None,None,None,:]
            rgb_values = sample_rgb(rgb,p)
            z = (chromaticity(rgb_values)-ref[:,None,None,None,:])/scale[:,None,None,None,:]
            probability = np.exp(-.5*np.sum(z*z,axis=-1))
            values.append((np.mean(probability,axis=(2,3)),np.mean(rgb_values.max(axis=-1),axis=(2,3))))
        contrast = values[1][0]-values[0][0]
        brightness_contrast = np.clip((values[1][1]-values[0][1])/np.maximum(brightness[:,None],.08),-1,1)
        raw = contrast+PARAMETERS['brightness_weight']*brightness_contrast
        valid &= np.isfinite(raw).all(axis=1)
        score[:,side] = gaussian_filter1d(np.where(valid[:,None],raw,0.),PARAMETERS['cost_smoothing_grid_sigma'],axis=1)
        diagnostics.append(dict(valid=valid.tolist(),reference_chromaticity=ref.tolist(),reference_scale=scale.tolist(),
                                max_score=score[:,side].max(axis=1).tolist()))
    return grid,score,diagnostics


def interpolate(grid, values, x):
    """C1 cubic profile and exact derivative; smooth forces at grid knots."""
    step = grid[0,0,1]-grid[0,0,0]
    position = (x-grid[:,:,0])/step
    j = np.clip(np.floor(position).astype(int),0,grid.shape[2]-2)
    f = np.clip(position-j,0,1)
    a = np.take_along_axis(values,j[:,:,None],axis=2)[:,:,0]
    b = np.take_along_axis(values,(j+1)[:,:,None],axis=2)[:,:,0]
    slopes = np.gradient(values,step,axis=2)
    m0 = np.take_along_axis(slopes,j[:,:,None],axis=2)[:,:,0]*step
    m1 = np.take_along_axis(slopes,(j+1)[:,:,None],axis=2)[:,:,0]*step
    value=(2*f**3-3*f**2+1)*a+(f**3-2*f**2+f)*m0+(-2*f**3+3*f**2)*b+(f**3-f**2)*m1
    derivative=((6*f*f-6*f)*a+(3*f*f-4*f+1)*m0+(-6*f*f+6*f)*b+(3*f*f-2*f)*m1)/step
    return value,derivative


def objective(flat, grid, score, base, expected, position_sigma, width_sigma, image_weight):
    x = flat.reshape(base.shape)
    evidence, slope = interpolate(grid,score,x)
    displacement = x-base
    width_error = x[:,1]-x[:,0]-expected
    curvature = np.roll(displacement,1,axis=0)-2*displacement+np.roll(displacement,-1,axis=0)
    smooth_var = PARAMETERS['second_difference_sigma_px']**2
    value = (.5*np.sum((displacement/position_sigma)**2)+.5*np.sum((width_error/width_sigma)**2)
             +.5*np.sum(curvature**2)/smooth_var-image_weight*evidence.sum())
    grad = displacement/position_sigma**2
    grad[:,0] -= width_error/width_sigma**2;grad[:,1] += width_error/width_sigma**2
    grad += (np.roll(curvature,1,axis=0)-2*curvature+np.roll(curvature,-1,axis=0))/smooth_var
    grad -= image_weight*slope
    return float(value),grad.ravel()


def optimize(grid, score, base, expected, clear, width_sigma=8., image_weight=4.):
    sigma = np.where(clear,PARAMETERS['clear_position_sigma_px'],PARAMETERS['other_position_sigma_px'])
    # Broad physical feasibility: keep the outer offset negative and inner positive.
    lower = grid[:,:,0].copy();upper=grid[:,:,-1].copy()
    upper[:,0]=np.minimum(upper[:,0],-5);lower[:,1]=np.maximum(lower[:,1],5)
    bounds = list(zip(lower.ravel(),upper.ravel()))
    result = minimize(objective,base.ravel(),args=(grid,score,base,expected,sigma,width_sigma,image_weight),
                      jac=True,bounds=bounds,method='L-BFGS-B',
                      options=dict(maxiter=PARAMETERS['optimizer_maxiter'],ftol=1e-10,gtol=1e-5,maxls=40))
    x=result.x.reshape(base.shape)
    return x,dict(success=bool(result.success),message=str(result.message),iterations=int(result.nit),
                  objective=float(result.fun),width_sigma_px=width_sigma,image_weight=image_weight,
                  min_width_px=float(np.min(x[:,1]-x[:,0])),max_width_px=float(np.max(x[:,1]-x[:,0])),
                  max_edge_displacement_from_width_only_px=float(np.max(np.abs(x-base))),
                  search_bound_hits=int(((np.abs(x-lower)<.05)|(np.abs(x-upper)<.05)).sum()))


def evaluate(xy,original,baseline,baseline_centers,candidates):
    # Evaluation labels never enter transition extraction or optimization.
    annotations=json.loads((ROOT/'photo2/transect-annotations-r066.json').read_text())
    if annotations['photo_sha256']!=wc.digest(ROOT/'beads-photo-2.jpg'):raise ValueError('Annotation/photo mismatch')
    records=[];summary={}
    methods={'original':original,'width_only':baseline,**candidates}
    for label,location,target in tr.TARGETS:
        j=int(np.argmin(np.linalg.norm(xy-np.array(target),axis=1)))
        review=annotations['transects'][label]
        record=dict(id=label,location=location,sample=j,center_xy=xy[j].tolist(),review=review,methods={})
        midpoint=[(review['inner_interval_px'][k]+review['outer_interval_px'][k])/2 for k in [0,1]]
        for method,offsets in methods.items():
            out,inside=offsets[j];center=(out+inside)/2
            if method=='original':center=0.
            elif method=='width_only':center=float(baseline_centers[j])
            distances=[tr.interval_distance(out,review['outer_interval_px']),tr.interval_distance(inside,review['inner_interval_px'])]
            record['methods'][method]=dict(outer=float(out),inner=float(inside),center=float(center),
                                          edge_distances_outside_px=distances,center_distance_outside_px=tr.interval_distance(center,midpoint))
        records.append(record)
    for method in methods:
        errors=np.array([r['methods'][method]['edge_distances_outside_px'] for r in records]).ravel()
        centers=np.array([r['methods'][method]['center_distance_outside_px'] for r in records])
        summary[method]=dict(edges_inside=int((errors==0).sum()),edges_within_2px=int((errors<=2).sum()),
                             mean_edge_distance_outside_px=float(errors.mean()),max_edge_distance_outside_px=float(errors.max()),
                             centers_inside=int((centers==0).sum()))
    return records,summary


def illustrate(output,rgb,xy,n,tangent,base,candidate,baseline_centers,records,grid,score):
    output.mkdir(parents=True,exist_ok=True)
    for start in range(0,len(records),4):
        chosen=records[start:start+4]
        items=[dict(id=r['id'],location=r['location'],center_xy=r['center_xy'],
                    direction=n[r['sample']],tangent=tangent[r['sample']]) for r in chosen]
        image=tr.draw_sheet(items,rgb);draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,804,60),fill='white')
        draw.text((15,8),'Cyan: width-only; green: image-guided; white: visual interval.',font=wc.font(18),fill='black')
        draw.text((15,33),'Outer side left, inner side right. Read at the horizontal side ticks.',font=wc.font(17),fill='black')
        for row,r in enumerate(chosen):
            top=120+row*335
            for side in ['outer','inner']:
                for off in r['review'][side+'_interval_px']:
                    x=402+4*off;draw.line((x,top+93,x,top+131),fill='white',width=2)
                for method,color in [('width_only','cyan'),('image_guided','lime')]:
                    x=402+4*r['methods'][method][side]
                    draw.line((x,top+80,x,top+144),fill='black',width=5)
                    draw.line((x,top+80,x,top+144),fill=color,width=2)
        image.save(output/f'comparison-{start//4+1}.png')
    overview=Image.fromarray(rgb);draw=ImageDraw.Draw(overview)
    for offsets,color in [(baseline_centers,'cyan'),(candidate.mean(axis=1),'lime')]:
        points=wc.closed(xy+n*offsets[:,None]);draw.line([tuple(p) for p in points],fill='black',width=7)
        draw.line([tuple(p) for p in points],fill=color,width=3)
    for r in records:
        j=r['sample'];x,y=xy[j]+115*n[j]
        draw.ellipse((x-24,y-24,x+24,y+24),fill='white',outline='black',width=2)
        draw.text((x-12,y-18),r['id'],font=wc.font(29),fill='black')
    overview.thumbnail((800,1100));overview.save(output/'center-comparison.png')
    selected=[r for r in records if r['id'] in ['C','E','G','H']]
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="850" viewBox="0 0 1100 850"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="14">',
           '<text x="20" y="25">Transition score: blue. Gray: assistant interval. Cyan: width-only. Green: image-guided.</text>']
    for row,r in enumerate(selected):
        j=r['sample']
        for side,name in enumerate(['outer','inner']):
            left=60+side*540;top=70+row*195;lo,hi=((-85,-15) if side==0 else (5,75))
            fx=lambda u:left+450*(u-lo)/(hi-lo)
            fy=lambda v:top+130*(1.2-v)/1.6
            a,b=r['review'][name+'_interval_px']
            parts.append(f'<rect x="{fx(a):.2f}" y="{top}" width="{fx(b)-fx(a):.2f}" height="130" fill="#ddd"/><text x="{left}" y="{top-13}">{r["id"]} {name}</text>')
            for tick in range(lo+5,hi,10):
                parts.append(f'<text x="{fx(tick)-10:.2f}" y="{top+150}">{tick}</text>')
            for tick in [0,.5,1.]:parts.append(f'<path d="M{left},{fy(tick):.2f}h450" stroke="#eee"/><text x="{left-33}" y="{fy(tick)+4:.2f}">{tick}</text>')
            pts=' '.join(f'{fx(u):.2f},{fy(v):.2f}' for u,v in zip(grid[j,side],score[j,side]) if lo<=u<=hi)
            parts.append(f'<polyline points="{pts}" fill="none" stroke="#2454b8" stroke-width="2"/>')
            for method,color in [('width_only','#00aabb'),('image_guided','#00aa00')]:
                x=fx(r['methods'][method][name]);parts.append(f'<path d="M{x:.2f},{top}v130" stroke="{color}" stroke-width="2"/>')
    parts.append('<text x="340" y="838">Normal offset in original image pixels</text></g></svg>')
    (output/'transition-profiles.svg').write_text('\n'.join(parts))


def review_html(output,summary,records):
    parts=['<!doctype html><meta charset="utf-8"><title>Image-edge comparison</title>',
           '<style>body{font:17px system-ui;max-width:1100px;margin:2em auto;padding:0 1em}img{max-width:100%;height:auto}td,th{border:1px solid #ccc;padding:.4em}table{border-collapse:collapse}</style>',
           '<h1>Direct image-edge test: retain the width-only candidate</h1>',
           '<p>The tested image-guided method is worse on the frozen assistant review intervals. It has not replaced any source geometry. These intervals are subjective visual estimates, not human ground truth.</p>',
           '<p>Cyan: width-only. Green: experimental image-guided. White brackets: visual intervals at the side ticks. Normal offsets are original-photo pixels. The full-image view compares centerlines.</p>',
           '<table><tr><th>Method</th><th>Edges inside /24</th><th>Within 2px /24</th><th>Mean distance outside</th><th>Maximum</th></tr>']
    for name,s in summary.items():parts.append(f'<tr><td>{html.escape(name)}</td><td>{s["edges_inside"]}</td><td>{s["edges_within_2px"]}</td><td>{s["mean_edge_distance_outside_px"]:.2f}</td><td>{s["max_edge_distance_outside_px"]:.2f}</td></tr>')
    parts.append('</table><p>Changing width scales does not rescue the image cue. The no-image ablation is a different soft-geometry fit; its mixed scores are not a reason to adopt it from these twelve observations.</p><img src="center-comparison.png" alt="Width-only and experimental centerlines">')
    for i in range(1,4):parts.append(f'<h2>Transects {"ABCD EFGH IJKL".split()[i-1]}</h2><img src="comparison-{i}.png" alt="Boundary comparison group {i}">')
    parts.append('<h2>Why the image cue can fail</h2><p>The outward color transition is not always the bead silhouette: blur, local bead scallops and colored shadow can create displaced peaks. G is the largest reviewed regression; H improves. C/E were preselected residual concerns. The graphs show the evidence actually used, not a true-edge probability.</p><img src="transition-profiles.svg" alt="Transition evidence at C E G H">')
    (output/'review.html').write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--review-bundle',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    rgb,xy,n,tangent,edges,baseline,clear,fit=tr.geometry()
    original=np.column_stack([np.sum((edges[k]-xy)*n,axis=1) for k in ['outer','inner']])
    base=np.column_stack([np.sum((baseline[k]-xy)*n,axis=1) for k in ['outer','inner']])
    baseline_centers=np.sum((baseline['center']-xy)*n,axis=1)
    clear_array=np.column_stack([clear[k] for k in ['outer','inner']])
    expected=fit['coefficients'][0]+fit['coefficients'][1]*(xy[:,1]-rgb.shape[0]/2)/(rgb.shape[0]/2)
    grid,score,diagnostics=transition_scores(rgb,xy,n,tangent,original,base)
    candidates={};optimizers={}
    for name,sigma,weight in [('image_guided',8.,4.),('width_sigma_6',6.,4.),('width_sigma_12',12.,4.),('no_image',8.,0.)]:
        candidates[name],optimizers[name]=optimize(grid,score,base,expected,clear_array,sigma,weight)
    records,summary=evaluate(xy,original,base,baseline_centers,candidates)
    wc.write_json(args.output/'curves.json',dict(status='experimental, not adopted',
                  candidates={name:dict(outer=wc.closed(xy+n*x[:,0,None]),inner=wc.closed(xy+n*x[:,1,None]),
                                        center=wc.closed(xy+n*x.mean(axis=1)[:,None])) for name,x in candidates.items()}))
    np.savez_compressed(args.output/'profiles.npz',grid=grid,score=score,xy=xy,n=n,base=base,original=original,**candidates)
    sources=[Path(__file__).resolve(),ROOT/'photo2/transect_review.py',ROOT/'photo2/width_correction.py',
             ROOT/'photo2/boundary-splines-source.json',ROOT/'photo2/centerline.json',ROOT/'beads-photo-2.jpg',ROOT/'photo2/transect-annotations-r066.json',ROOT/'photo2/test_image_edges.py']
    report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,sources={str(p.relative_to(ROOT)):wc.digest(p) for p in sources},
                fit=fit,optimizers=optimizers,summary=summary,transects=records,edge_diagnostics=diagnostics)
    report['artifacts']={name:wc.digest(args.output/name) for name in ['curves.json','profiles.npz']}
    wc.write_json(args.output/'report.json',report)
    if args.review_bundle:
        illustrate(args.review_bundle,rgb,xy,n,tangent,base,candidates['image_guided'],baseline_centers,records,grid,score)
        review_html(args.review_bundle,summary,records)
        review={k:v for k,v in report.items() if k not in ['edge_diagnostics','artifacts']}
        review['full_report_sha256']=wc.digest(args.output/'report.json')
        review['artifacts']={p.name:wc.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.suffix in ['.png','.svg','.html']}
        wc.write_json(args.review_bundle/'report.json',review)
    print(json.dumps(dict(optimizers=optimizers,summary=summary),indent=2))

if __name__=='__main__':main()
