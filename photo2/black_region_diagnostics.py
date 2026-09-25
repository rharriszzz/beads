#!/usr/bin/env python3
"""R073: HSV line scans and neighbor-constrained projected outline diagnostics."""
from __future__ import annotations
import argparse
import base64
import csv
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'output/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from skimage.color import rgb2hsv
import blind_generated as bg

ROOT=Path(__file__).resolve().parents[1]
PARAMETERS=dict(sample_step_px=.25,line_extension_fraction=.25,strip_offsets_px=[-2,-1,0,1,2],
                hue_min_value=.08,hue_min_saturation=.15,peak_prominence_8bit=5,
                contour_value_thresholds_8bit=[20,40,60,90],exterior_step_px=.25)


def sample_rgb(rgb,xy):
    xy=np.asarray(xy,float)
    return np.stack([ndi.map_coordinates(rgb[...,c].astype(float),xy[...,::-1].reshape(-1,2).T,order=1,mode='nearest').reshape(xy.shape[:-1]) for c in range(3)],axis=-1)


def line_profile(rgb,a,b):
    a=np.asarray(a,float);b=np.asarray(b,float);delta=b-a;length=float(np.linalg.norm(delta))
    if length==0:raise ValueError('Line endpoints coincide')
    normal=np.array([-delta[1],delta[0]])/length
    ext=PARAMETERS['line_extension_fraction'];t=np.linspace(-ext,1+ext,int(np.ceil((1+2*ext)*length/PARAMETERS['sample_step_px']))+1)
    offsets=np.array(PARAMETERS['strip_offsets_px'])
    xy=a+t[:,None]*delta;strip=xy[None,:,:]+offsets[:,None,None]*normal
    values=sample_rgb(rgb,strip);hsv=rgb2hsv(values/255.)
    valid_hue=(hsv[...,2]>=PARAMETERS['hue_min_value'])&(hsv[...,1]>=PARAMETERS['hue_min_saturation'])
    raw=values[2];median_v=np.median(hsv[...,2],axis=0)*255
    # Locate glints as measurements only; no peak-to-bead conversion.
    peaks,properties=find_peaks(median_v,prominence=PARAMETERS['peak_prominence_8bit'])
    interior=(t>=.2)&(t<=.8)
    metrics=dict(length_px=length,centerline_dark_fraction_between_endpoints=float((raw[(t>=0)&(t<=1)].max(axis=1)<=2).mean()),
                 middle_strip_median_value_8bit=float(np.median(median_v[interior])),
                 middle_max_value_8bit=float(median_v[interior].max()),
                 valid_hue_fraction=float(valid_hue.mean()),
                 measured_peaks=[dict(t=float(t[i]),xy=xy[i].tolist(),value_8bit=float(median_v[i]),prominence_8bit=float(prom)) for i,prom in zip(peaks,properties['prominences'])])
    return dict(t=t,xy=xy,values=values,hsv=hsv,valid_hue=valid_hue,median_v=median_v,metrics=metrics)


def local_model(case,rows,labels,target):
    vectors=np.array([np.array(rows[b]['marker_xy'])-rows[a]['marker_xy'] for a,b in case['step_pairs']],float)
    step=np.median(vectors,axis=0)
    covariances=[]
    for i in case['reference_ids']:
        y,x=np.nonzero(labels==i);covariances.append(np.cov(np.column_stack([x,y]).T))
    covariance=np.median(covariances,axis=0);_,axes=np.linalg.eigh(covariance)
    long=axes[:,-1]
    if long[1]<0:long=-long
    short=np.array([-long[1],long[0]])
    measurements=[]
    for i in case['reference_ids']:
        y,x=np.nonzero(labels==i)
        if len(x)<4:raise ValueError('Insufficient reference mask')
        points=np.column_stack([x,y]);center=points.mean(axis=0)
        # An ellipse filled uniformly has variance radius^2 / 4.
        radii=[float(2*np.std((points-center)@axis)) for axis in [long,short]]
        measurements.append(dict(id=i,centroid_xy=center.tolist(),marker_offset_xy=(center-rows[i]['marker_xy']).tolist(),ellipse_proxy_radii_px=radii,mask_pixels=len(x)))
    offset=np.median([x['marker_offset_xy'] for x in measurements],axis=0)
    radii=np.median([x['ellipse_proxy_radii_px'] for x in measurements],axis=0)
    a=np.array(rows[target]['marker_xy'],float)+offset
    predictions=np.array(rows[case['prediction_anchor']]['marker_xy'],float)+vectors+offset
    b=np.median(predictions,axis=0)
    alternate=None
    if 'alternate_cross_pair' in case:
        x,y=case['alternate_cross_pair'];alternate=(a+np.array(rows[y]['marker_xy'])-rows[x]['marker_xy']).tolist()
    loo=[]
    for j,(start,end) in enumerate(case['step_pairs']):
        estimate=np.median(np.delete(vectors,j,axis=0),axis=0)
        predicted=np.array(rows[start]['marker_xy'])+estimate;observed=np.array(rows[end]['marker_xy'])
        loo.append(dict(start_id=start,held_out_end_id=end,predicted_xy=predicted.tolist(),observed_marker_xy=observed.tolist(),error_px=float(np.linalg.norm(predicted-observed))))
    anchor=case['validation_anchor'];training=[vectors[j] for j,pair in enumerate(case['step_pairs']) if target not in pair]
    heldout=np.array(rows[anchor]['marker_xy'])+np.median(training,axis=0)
    validation=dict(anchor_id=anchor,held_out_target_id=target,predicted_marker_xy=heldout.tolist(),observed_marker_xy=rows[target]['marker_xy'],error_px=float(np.linalg.norm(heldout-rows[target]['marker_xy'])),target_excluded_from_training=True,claim='marker-location validation only, not physical-center validation')
    return dict(pair_leave_one_out=loo,target_holdout=validation,a_xy=a.tolist(),b_xy=b.tolist(),alternate_b_xy=alternate,
                b_predictions_xy=predictions.tolist(),row_step_xy=step.tolist(),row_step_samples_xy=vectors.tolist(),
                long_axis=long.tolist(),short_axis=short.tolist(),radii_px=radii.tolist(),
                marker_to_mask_centroid_offset_xy=offset.tolist(),reference_measurements=measurements,
                status='hypothesis_only; mask-derived ellipse proxies, not calibrated physical centers')


def exterior_scan(rgb,case):
    c=case['exterior'];p=np.arange(c['span'][0],c['span'][1]+.01,.5);q=np.arange(c['depth'][0],c['depth'][1]+.01,PARAMETERS['exterior_step_px'])
    xy=np.array(c['origin'])+p[:,None,None]*np.array(c['along'])+q[None,:,None]*np.array(c['outward'])
    hsv=rgb2hsv(sample_rgb(rgb,xy)/255.);value=hsv[...,2]*255
    result={}
    for threshold in PARAMETERS['contour_value_thresholds_8bit']:
        # Exclude saturated red neighbors; very dark hue/saturation is unstable.
        dark=(value<threshold)&((hsv[...,1]<.35)|(value<=5))
        last=np.where(dark,np.arange(len(q)),-1).max(axis=1);valid=(last>=0)&(last<len(q)-1)
        edge=np.full(len(p),np.nan);edge[valid]=q[last[valid]]
        result[str(threshold)]=edge
    return p,result


def outline(ax,center,model,color,scale=1,linestyle='-'):
    direction=np.array(model['long_axis']);angle=np.degrees(np.arctan2(direction[1],direction[0]));r=model['radii_px']
    ax.add_patch(Ellipse(center,2*r[0]*scale,2*r[1],angle=angle,fill=False,color=color,lw=1.3,linestyle=linestyle))


def crop_axes(ax,rgb,box):
    ax.imshow(rgb);ax.set_xlim(box[0],box[2]);ax.set_ylim(box[3],box[1]);ax.set_aspect('equal');ax.set_xlabel('image x (pixels)');ax.set_ylabel('image y (pixels)')


def save_profiles(rgb,case,model,profiles,path):
    fig,axes=plt.subplots(3,2,figsize=(12,9),layout='constrained')
    for column,(name,profile) in enumerate(profiles.items()):
        a,b=(model['a_xy'],model['b_xy']) if name=='projected_centers' else case['glint_line_xy']
        crop_axes(axes[0,column],rgb,case['crop']);axes[0,column].plot([a[0],b[0]],[a[1],b[1]],'o-',color='cyan',lw=1)
        axes[0,column].text(*a,' A',color='cyan');axes[0,column].text(*b,' B',color='cyan')
        axes[0,column].set_title('Provisional projected-center line' if name=='projected_centers' else 'Separate highlight / dark-patch line')
        t=profile['t'];hsv=profile['hsv'];ax=axes[1,column]
        for values in hsv[...,2]:ax.plot(t,values*255,color='gray',alpha=.4,lw=.6)
        ax.plot(t,profile['median_v'],color='black',label='5-line median V');ax.plot(t,hsv[2,:,2]*255,color='tab:blue',lw=.8,label='centerline V')
        ax.set_ylabel('V, 0–255');ax.set_xlabel('fraction along A–B');ax.legend(fontsize=8);ax.grid(alpha=.2)
        ax=axes[2,column];ax.plot(t,hsv[2,:,1],color='tab:orange',label='centerline S')
        hue=np.where(profile['valid_hue'][2],hsv[2,:,0],np.nan);ax.plot(t,hue,'.',color='tab:purple',label='H only when V/S adequate',ms=3)
        ax.set_ylim(-.03,1.03);ax.set_ylabel('H/S, 0–1');ax.set_xlabel('fraction along A–B');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('HSV scans: gray traces are ±2 pixels; missing hue is uninformative, not zero hue',fontsize=12)
    fig.savefig(path,dpi=140);plt.close(fig)


def save_outlines(rgb,case,model,rows,target,p,edges,path):
    fig,axes=plt.subplots(2,2,figsize=(12,10),layout='constrained')
    crop_axes(axes[0,0],rgb,case['crop']);axes[0,0].set_title('Known nearby markers and predicted next slot')
    for i in set(case['reference_ids']+[x for pair in case['step_pairs'] for x in pair]+[target]):
        x,y=rows[i]['marker_xy'];axes[0,0].plot(x,y,'+',color='cyan',ms=6);axes[0,0].text(x+1,y,str(i),color='cyan',fontsize=7)
    preds=np.array(model['b_predictions_xy']);axes[0,0].plot(preds[:,0],preds[:,1],'x',color='orange',ms=7,label='B from individual neighbor steps')
    check=model['target_holdout'];predicted=check['predicted_marker_xy'];observed=check['observed_marker_xy']
    axes[0,0].plot([predicted[0],observed[0]],[predicted[1],observed[1]],'r:',lw=1.5)
    axes[0,0].plot(*predicted,'x',color='red',ms=8,label=f"Held-out marker prediction: {check['error_px']:.2f} px error")
    if model['alternate_b_xy'] is not None:axes[0,0].plot(*model['alternate_b_xy'],'+',color='magenta',ms=10,label='B from cross-row transfer')
    axes[0,0].legend(fontsize=7)
    crop_axes(axes[0,1],rgb,case['crop']);axes[0,1].set_title('Local ellipse proxies: neither outline is accepted geometry')
    for center,color,label in [(model['a_xy'],'cyan','A'),(model['b_xy'],'orange','B')]:
        outline(axes[0,1],center,model,color);outline(axes[0,1],center,model,color,.65,'--');axes[0,1].plot(*center,'+',color=color);axes[0,1].text(center[0]+1,center[1],label,color=color)
    axes[0,1].text(.02,.03,'Solid: neighbor-derived size; dashed: 0.65 axial scale\nDashed scale is a sensitivity probe, not measured foreshortening.',transform=axes[0,1].transAxes,fontsize=7,color='black',bbox=dict(facecolor='white',alpha=.8))
    crop_axes(axes[1,0],rgb,case['crop']);axes[1,0].set_title('Measured dark exterior, varied V cutoff')
    c=case['exterior']
    for k,(threshold,edge) in enumerate(edges.items()):
        pts=np.array(c['origin'])+p[:,None]*np.array(c['along'])+edge[:,None]*np.array(c['outward'])
        axes[1,0].plot(pts[:,0],pts[:,1],lw=1,label=f'V<{threshold}')
        axes[1,1].plot(p,edge,label=f'V<{threshold}',lw=1)
    axes[1,0].legend(fontsize=7);axes[1,1].legend(fontsize=8);axes[1,1].grid(alpha=.2)
    axes[1,1].set_xlabel('position along outline sweep (pixels)');axes[1,1].set_ylabel('outward dark extent (pixels)');axes[1,1].set_title('External contour slices; gaps have no valid crossing')
    fig.suptitle(f'Region {target}: local reconstruction hypothesis and observed outline',fontsize=13)
    fig.savefig(path,dpi=140);plt.close(fig)


def gallery(path,rgb,results):
    encoded=base64.b64encode((ROOT/'beads3.jpg').read_bytes()).decode();parts=['<!doctype html><meta charset="utf-8"><title>Black-region line and outline diagnostics</title>',
    '<style>body{font:17px system-ui;max-width:1300px;margin:2em auto;padding:1em}img{max-width:100%}svg{width:100%;max-height:650px;background:#eee}label{display:inline-block;margin:.5em}input{width:140px}</style>',
    '<h1>Regions 122 and 405: neighborhood geometry first</h1><p>R074: neighborhood geometry is primary; HSV is supporting evidence. Image-only hypotheses. Cyan A is based on an existing observation; orange B is a locally predicted slot. Ellipses are approximate projected outlines, not recovered bead geometry. No new bead is accepted here.</p>']
    for name,result in results.items():
        c=result['case'];m=result['model'];box=c['crop'];u=m['long_axis'];angle=np.degrees(np.arctan2(u[1],u[0]));a,b=m['radii_px'];cx,cy=m['b_xy']
        parts.append(f'<h2>Region {name}</h2><p>{c["note"]}</p><p>Predicting the existing target marker while withholding it: error {m['target_holdout']['error_px']:.2f} pixels. This tests marker placement, not recovered physical centers.</p><img src="{name}-outlines.png" alt="Neighbor model and contour slices for {name}"><img src="{name}-hsv.png" alt="HSV profiles for {name}">')
        parts.append(f'<h3>Move candidate B along its two projected axes</h3><p>This is an inspection control, not an optimization or a saved inventory edit. Cyan shows A; orange shows B.</p><div id="controls-{name}"><label>Long-axis shift <input class="long" type="range" min="-10" max="10" value="0" step=".25"></label><label>Short-axis shift <input class="short" type="range" min="-10" max="10" value="0" step=".25"></label><label>Axial scale <input class="scale" type="range" min=".5" max="1.3" value="1" step=".025"></label><output></output></div>')
        parts.append(f'<svg viewBox="{box[0]} {box[1]} {box[2]-box[0]} {box[3]-box[1]}"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/><ellipse cx="{m["a_xy"][0]}" cy="{m["a_xy"][1]}" rx="{a}" ry="{b}" transform="rotate({angle} {m["a_xy"][0]} {m["a_xy"][1]})" fill="none" stroke="cyan" stroke-width=".35"/><ellipse id="candidate-{name}" cx="{cx}" cy="{cy}" rx="{a}" ry="{b}" transform="rotate({angle} {cx} {cy})" fill="none" stroke="orange" stroke-width=".4"/></svg>')
        parts.append('<script>'+f'(()=>{{const c=document.getElementById("controls-{name}"),e=document.getElementById("candidate-{name}");function update(){{const l=+c.querySelector(".long").value,s=+c.querySelector(".short").value,k=+c.querySelector(".scale").value,x={cx}+l*{u[0]}-s*{u[1]},y={cy}+l*{u[1]}+s*{u[0]};e.setAttribute("cx",x);e.setAttribute("cy",y);e.setAttribute("rx",{a}*k);e.setAttribute("transform",`rotate({angle} ${{x}} ${{y}})`);c.querySelector("output").textContent=`long ${{l}} px; short ${{s}} px; scale ${{k}}`;}}c.addEventListener("input",update);update();}})();'+'</script>')
    parts.append('<p>Method, conclusions and limitations: <a href="../../BLACK_REGION_METHODS.md">BLACK_REGION_METHODS.md</a>. Numerical data and profiles are saved beside this page. Original R071 inventory remains unchanged.</p>');path.write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--review-bundle',type=Path,required=True);parser.add_argument('--source-output',type=Path,default=ROOT/'photo2/output/beads3-final');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);args.review_bundle.mkdir(parents=True,exist_ok=True)
    config_path=ROOT/'photo2/black-region-review-r073.json';config=json.loads(config_path.read_text());source=ROOT/config['source_review'];source_report=json.loads((source/'report.json').read_text());image_path=ROOT/config['image']
    for path,expected in [(image_path,source_report['sources']['beads3.jpg']),(source/'inventory.json',source_report['artifacts']['inventory.json']),(args.source_output/'labels.npy',source_report['bulk_artifacts']['labels.npy'])]:
        if bg.digest(path)!=expected:raise ValueError('Source binding mismatch: '+str(path))
    inventory=json.loads((source/'inventory.json').read_text());rows={r['id']:r for r in inventory['active_observations']+inventory['excluded_observations']};labels=np.load(args.source_output/'labels.npy');rgb=np.asarray(Image.open(image_path).convert('RGB'));results={};csv_rows=[]
    for name,case in config['cases'].items():
        model=local_model(case,rows,labels,int(name));profiles={kind:line_profile(rgb,*ends) for kind,ends in [('projected_centers',[model['a_xy'],model['b_xy']]),('highlight_or_dark_patch',case['glint_line_xy'])]}
        p,edges=exterior_scan(rgb,case)
        contour_values=np.array(list(edges.values()));valid=np.isfinite(contour_values).all(axis=0)
        spread=np.ptp(contour_values[:,valid],axis=0)
        sensitivity=dict(valid_slices=int(valid.sum()),total_slices=len(p),median_band_px=float(np.median(spread)) if len(spread) else None,max_band_px=float(spread.max()) if len(spread) else None,meaning='threshold sensitivity along sweep rays, not a calibrated shadow-width confidence interval')
        result=dict(case=case,model=model,profiles={k:v['metrics'] for k,v in profiles.items()},exterior=dict(sensitivity=sensitivity,along_px=p.tolist(),thresholds={k:[None if not np.isfinite(x) else float(x) for x in edge] for k,edge in edges.items()}))
        results[name]=result;save_profiles(rgb,case,model,profiles,args.review_bundle/f'{name}-hsv.png');save_outlines(rgb,case,model,rows,int(name),p,edges,args.review_bundle/f'{name}-outlines.png')
        for kind,profile in profiles.items():
            for i,t in enumerate(profile['t']):
                for j,offset in enumerate(PARAMETERS['strip_offsets_px']):
                    values=profile['values'][j,i];hsv=profile['hsv'][j,i];csv_rows.append([name,kind,float(t),offset,*profile['xy'][i].tolist(),*values.tolist(),*hsv.tolist(),bool(profile['valid_hue'][j,i])])
    with (args.review_bundle/'profiles.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['region','line','t','perpendicular_offset_px','centerline_x','centerline_y','r','g','b','h','s','v','hue_usable']);writer.writerows(csv_rows)
    bg.write_json(args.review_bundle/'diagnostics.json',dict(parameters=PARAMETERS,results=results,limitations=config['limitations'],inventory_changed=False))
    gallery(args.review_bundle/'review.html',rgb,results)
    source_paths=[Path(__file__).resolve(),config_path,source/'inventory.json',source/'report.json',image_path,ROOT/'photo2/requirements.txt',ROOT/'photo2/blind_generated.py']
    test=ROOT/'photo2/test_black_region_diagnostics.py'
    if test.exists():source_paths.append(test)
    report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,versions=dict(python=sys.version.split()[0],numpy=np.__version__,matplotlib=matplotlib.__version__),sources={str(p.relative_to(ROOT)):bg.digest(p) for p in source_paths},source_labels_sha256=bg.digest(args.source_output/'labels.npy'),artifacts={p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!='report.json'},inventory_changed=False)
    bg.write_json(args.review_bundle/'report.json',report)
    print(json.dumps({name:dict(model=r['model'],profiles=r['profiles']) for name,r in results.items()},indent=2))

if __name__=='__main__':main()
