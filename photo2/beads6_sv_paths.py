#!/usr/bin/env python3
"""R087: frozen JPEG-only interior paths, with S/V and placement controls."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import scipy
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'photo2/beads6-sv-paths-r087.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sv(rgb):
    """Encoded RGB 0–255 -> descriptive S 0–1, V 0–255 (no linearization)."""
    value = np.max(rgb, axis=-1)
    saturation = np.divide(value - np.min(rgb, axis=-1), value,
                           out=np.zeros_like(value, dtype=float), where=value != 0)
    return saturation, value


def sample_path(rgb, ends, offsets, step):
    ends = np.asarray(ends, dtype=float)
    delta = ends[1] - ends[0]
    length = float(np.linalg.norm(delta))
    if length <= 0 or step <= 0:
        raise ValueError('Path length and sample step must be positive')
    axis = delta / length
    normal = np.array([-axis[1], axis[0]])
    # Include both endpoints exactly; actual spacing is <= requested step.
    distance = np.linspace(0, length, int(np.ceil(length / step)) + 1)
    xy = (ends[0] + distance[None, :, None] * axis
          + np.asarray(offsets)[:, None, None] * normal)
    if (xy[..., 0].min() < 0 or xy[..., 1].min() < 0
            or xy[..., 0].max() > rgb.shape[1]-1 or xy[..., 1].max() > rgb.shape[0]-1):
        raise ValueError('Path corridor outside image')
    pixels = np.stack([ndi.map_coordinates(rgb[..., k].astype(float),
                       [xy[..., 1], xy[..., 0]], order=1, mode='nearest')
                       for k in range(3)], axis=-1)
    return distance, xy, pixels


def metrics(distance, rgb, window):
    saturation, value = sv(rgb)
    left, right = distance <= window, distance >= distance[-1] - window
    inner = (distance > window) & (distance < distance[-1] - window)
    if not inner.any():
        raise ValueError('Path too short for endpoint windows')
    sl, sr = float(np.median(saturation[left])), float(np.median(saturation[right]))
    vl, vr = float(np.median(value[left])), float(np.median(value[right]))
    ids = np.flatnonzero(inner)
    trough = ids[np.argmin(value[inner])]
    return dict(s_start=sl, s_end=sr, s_delta=sr-sl,
                s_range=float(np.ptp(saturation)), v_start=vl, v_end=vr,
                v_dip=float(min(vl,vr)-value[trough]),
                v_dip_distance_px=float(distance[trough]),
                v_peak=float(value[inner].max()-max(vl,vr)),
                trough_at_search_edge=bool(trough in (ids[0],ids[-1])))


def draw_path(ax, path, color='yellow'):
    ends = np.array(path['ends'], dtype=float)
    delta = ends[1]-ends[0]
    normal = np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
    for shift in [-2, 2]:
        line = ends + shift*normal
        ax.plot(*line.T, color=color, lw=.6, alpha=.7, linestyle=':')
    ax.plot(*ends.T, color=color, lw=.9)
    ax.plot(*ends[0], 'o', ms=3, color=color)
    ax.plot(*ends[1], 's', ms=3, color=color)
    ax.annotate(path['id'], ends[0], xytext=(-9,-10), textcoords='offset points',
                color='white', weight='bold', fontsize=10,
                bbox=dict(facecolor='black',alpha=.65,edgecolor='none',pad=1))


def explanation_card(rgb, path, output):
    """Keep unmarked context, endpoint hypotheses and measurement route distinct."""
    ends = np.array(path['ends'])
    center = ends.mean(axis=0)
    radius = max(19, np.ptp(ends,axis=0).max()/2+12)
    fig,axes = plt.subplots(1,3,figsize=(13,4.8))
    for col,ax in enumerate(axes):
        ax.imshow(rgb.astype('uint8'),interpolation='nearest')
        ax.set(xlim=(center[0]-radius,center[0]+radius),
               ylim=(center[1]+radius,center[1]-radius),
               title=['1. Raw JPEG: judge the visible faces','2. Proposed interior points P and Q','3. Sample on the straight line P to Q'][col])
        if col:
            if col==2:
                ax.plot(*ends.T,color='yellow',lw=1)
            for point,label,color,marker in zip(ends,['P','Q'],['cyan','orange'],['o','s']):
                ax.plot(*point,marker,ms=9,mfc='none',mec=color,mew=1.5)
                ax.annotate(label,point,xytext=(7,-12),textcoords='offset points',
                            color=color,weight='bold',fontsize=12,
                            bbox=dict(facecolor='black',alpha=.6,edgecolor='none',pad=1))
    fig.suptitle(f"{path['id']}: {path['name']} — a measurement path, not a bead outline",fontsize=14)
    fig.text(.5,.03,f"P = {path['ends'][0]}   Q = {path['ends'][1]} in original JPEG pixels. Endpoint identities are visual hypotheses.",ha='center')
    fig.tight_layout(rect=(0,.13,1,.92))
    fig.savefig(output,dpi=150)
    plt.close(fig)


def journey_card(rgb, path, cfg, output):
    """Link sampled colors and extrema back to their locations in the JPEG."""
    d,xy,pixels = sample_path(rgb,path['ends'],[0],cfg['sample_step_px'])
    s,v = sv(pixels[0])
    highlight = path['id']=='H'
    middle = int(np.argmin(s if highlight else v))
    stop_ids = [0,middle,len(d)-1]
    notes = {
        'A': 'Cyan becomes darker and then brighter again. This supports a candidate seam; shading can also make a valley.',
        'B': 'Between the revised interiors, brightness falls and recovers while saturation changes little. Body identities remain hypotheses.',
        'H': 'Red becomes almost white at the highlight and returns to red. A large saturation change occurs inside one apparent face.',
        'K': 'The darkest point is very near P. P was placed in the shadow stripe: this is a failed interior-to-interior comparison.'}
    fig = plt.figure(figsize=(12,7))
    grid = fig.add_gridspec(3,2,height_ratios=[1,1,.35],width_ratios=[1,1.6])
    ax = fig.add_subplot(grid[:2,0])
    ax.imshow(rgb.astype('uint8'),interpolation='nearest')
    points = xy[0]
    center = points.mean(axis=0)
    radius = max(16,np.ptp(points,axis=0).max()/2+8)
    ax.set(xlim=(center[0]-radius,center[0]+radius),ylim=(center[1]+radius,center[1]-radius),title='Where the three stops lie')
    ax.plot(*points.T,color='yellow',lw=1)
    colors = ['cyan','magenta','orange']
    for n,(idx,color) in enumerate(zip(stop_ids,colors),1):
        ax.plot(*points[idx],'o',ms=7,mfc='none',mec=color,mew=1.5)
        ax.annotate(str(n),points[idx],xytext=(6,-14 if n!=2 else 10),textcoords='offset points',color=color,weight='bold',bbox=dict(facecolor='black',alpha=.65,pad=1,edgecolor='none'))
    for row,values,title,limits in [(0,v,'Brightness V (0–255)',(0,260)),(1,s,'Saturation S (0–1)',(-.02,1.02))]:
        ax = fig.add_subplot(grid[row,1])
        ax.plot(d,values,color='black')
        for n,(idx,color) in enumerate(zip(stop_ids,colors),1):
            ax.axvline(d[idx],color=color,ls=':',lw=1)
            ax.plot(d[idx],values[idx],'o',color=color,mec='black',ms=5)
            ax.annotate(str(n),(d[idx],values[idx]),xytext=(3,7),textcoords='offset points')
        ax.set(xlim=(0,d[-1]),ylim=limits,ylabel=title,xlabel='distance from P (px)')
        ax.grid(alpha=.15)
    ax = fig.add_subplot(grid[2,:])
    # Color strip retains actual encoded sample RGB; interpolation adds no image detail.
    ax.imshow(np.clip(pixels[0][None,:,:]/255,0,1),aspect='auto',interpolation='nearest',extent=(0,d[-1],0,1))
    ax.set(yticks=[],xlabel='P → Q: the sampled colors in travel order (enlarged, not new resolution)')
    for n,(idx,color) in enumerate(zip(stop_ids,colors),1):
        ax.axvline(d[idx],color=color,lw=1.5)
        ax.text(d[idx],1.12,str(n),ha='center',weight='bold')
    middle_label = 'lowest saturation' if highlight else 'lowest brightness'
    measurements = '   |   '.join(f'{n}: S={s[idx]:.2f}, V={v[idx]:.0f}' for n,idx in enumerate(stop_ids,1))
    fig.suptitle(f"{path['id']}: What changes along this path?\n1 = P; 2 = {middle_label} on the full path; 3 = Q",fontsize=14)
    fig.text(.5,.06,notes[path['id']],ha='center',fontsize=10)
    fig.text(.5,.025,measurements+'   (raw, offset 0)',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.09,1,.90))
    fig.savefig(output,dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(CONFIG.read_text())
    baseline_path = ROOT/'photo2/review/r078/report.json'
    baseline = json.loads(baseline_path.read_text())
    for path, expected in baseline['sources'].items():
        assert digest(ROOT/path) == expected, path
    inventory_path = ROOT/'photo2/review/r078/inventory.json'
    assert digest(inventory_path) == baseline['artifacts']['inventory.json']
    inventory = json.loads(inventory_path.read_text())
    assert len(inventory['active_observations']) == 310
    assert all(r['bead_index'] is None for r in inventory['active_observations'])
    rgb = np.asarray(Image.open(ROOT/cfg['image']).convert('RGB')).astype(float)
    smoothed = {s: ndi.gaussian_filter(rgb, (s,s,0),mode='reflect') if s else rgb
                for s in cfg['sigmas_px']}
    args.output.mkdir(parents=True,exist_ok=True)
    fig, axes = plt.subplots(2,3,figsize=(15,9))
    for col,panel in enumerate(cfg['panels']):
        x0,y0,x1,y1 = panel['box']
        for row in range(2):
            ax = axes[row,col]
            ax.imshow(rgb.astype('uint8'),interpolation='nearest')
            ax.set(xlim=(x0,x1),ylim=(y1,y0),title=panel['name'] + (' / paths' if row else ' / raw'))
            if row:
                for path in cfg['paths']:
                    if path['panel']==col:
                        draw_path(ax,path)
                t = np.array(panel['tangent_xy'])
                ax.annotate('',xy=t[1],xytext=t[0],arrowprops=dict(arrowstyle='->',color='lime',lw=2))
    fig.suptitle('beads6: JPEG-selected paths / circle start, square end / dotted ±2 px\nGreen arrows: qualitative planar section directions, not bead-chain directions')
    fig.tight_layout()
    fig.savefig(args.output/'paths.png',dpi=140)
    plt.close(fig)
    summaries, samples = [], []
    for start in range(0,len(cfg['paths']),5):
        count = min(5,len(cfg['paths'])-start)
        fig, axes = plt.subplots(count,3,figsize=(14,2.8*count+1),squeeze=False)
        for row,path in enumerate(cfg['paths'][start:start+5]):
            ends = np.array(path['ends'])
            ax = axes[row,0]
            ax.imshow(rgb.astype('uint8'),interpolation='nearest')
            ax.set(xlim=(ends[:,0].min()-6,ends[:,0].max()+6),
                   ylim=(ends[:,1].max()+6,ends[:,1].min()-6),title=f"{path['id']}: {path['name']}")
            draw_path(ax,path)
            path_metrics = []
            for sigma in cfg['sigmas_px']:
                distance, xy, pixels = sample_path(smoothed[sigma],path['ends'],cfg['offsets_px'],cfg['sample_step_px'])
                saturation,value = sv(pixels)
                nominal = cfg['offsets_px'].index(0)
                for col,values,label in [(1,value,'V (0–255)'),(2,saturation,'S (0–1)')]:
                    ax = axes[row,col]
                    if sigma==0:
                        ax.fill_between(distance,values.min(axis=0),values.max(axis=0),color='gray',alpha=.25,label='raw ±2 px range')
                    ax.plot(distance,values[nominal],label=f'offset 0, sigma {sigma:g}',lw=1)
                    ax.set(xlabel='distance from circle start (px)',ylabel=label)
                for offset,points,trace in zip(cfg['offsets_px'],xy,pixels):
                    m = metrics(distance,trace,cfg['endpoint_window_px'])
                    path_metrics.append(dict(sigma_px=sigma,offset_px=offset,**m))
                    sat,val = sv(trace)
                    for d,point,pixel,s,v in zip(distance,points,trace,sat,val):
                        samples.append([path['id'],sigma,offset,d,*point,*pixel,s,v])
            for col in [1,2]:
                ax = axes[row,col]
                ax.axvspan(0,cfg['endpoint_window_px'],color='blue',alpha=.04)
                ax.axvspan(distance[-1]-cfg['endpoint_window_px'],distance[-1],color='blue',alpha=.04)
                ax.grid(alpha=.2)
                ax.legend(fontsize=6)
            axes[row,1].set_ylim(0,260)
            axes[row,2].set_ylim(-.02,1.02)
            summaries.append(dict(**path,length_px=float(distance[-1]),measurements=path_metrics))
        fig.suptitle('S/V on the same full path: encoded RGB, bilinear sampling, RGB smoothing\nBands show translation sensitivity; controls are visual single-body hypotheses')
        fig.tight_layout(rect=(0,0,1,.96))
        fig.savefig(args.output/f'profiles-{start//5+1}.png',dpi=130)
        plt.close(fig)
    for path in cfg['paths']:
        if path['id'] in ['A','B','H','K']:
            explanation_card(rgb,path,args.output/f"explain-{path['id']}.png")
            journey_card(rgb,path,cfg,args.output/f"journey-{path['id']}.png")
    with (args.output/'profiles.csv').open('w',newline='') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(['path','sigma_px','offset_px','distance_px','x','y','red','green','blue','saturation','value'])
        writer.writerows(samples)
    (args.output/'measurements.json').write_text(json.dumps(dict(paths=summaries,limitations=cfg['limitations']),indent=2)+'\n')
    (args.output/'review.html').write_text('''<!doctype html><meta charset="utf-8"><title>beads6 S/V paths — R087</title>
<style>body{font:17px system-ui;max-width:1500px;margin:2em auto;padding:0 1em}img{max-width:100%}</style>
<h1>Interior paths and shading controls</h1><p>JPEG-selected hypotheses; inventory remains 310. Circle starts and square ends. Dotted lines are ±2-pixel translations. No chain directions or source indices assigned.</p>
<p><a href="../../BEADS6_SV_PATHS.md">Assessment and reproduction</a> · <a href="../../BEADS6_SV_QUESTIONS.md">Two illustrated questions</a></p>
<h2>Start with the explained pictures</h2><p>Raw pixels, proposed endpoints, then the straight sampling line. These are hypotheses, not recovered outlines. K is a rejected placement, not a valid interior-to-interior test.</p>
<img src="explain-A.png" alt="144 side seam: raw JPEG, proposed interiors, sampling connection">
<img src="journey-A.png" alt="Along A: darker cyan then brighter cyan, candidate seam with shading ambiguity">
<img src="explain-K.png" alt="Failed initial placement near 189: P starts in a shadow stripe">
<img src="journey-K.png" alt="Along rejected K: darkest point near P reveals poor endpoint placement">
<img src="explain-B.png" alt="Revised 189 path between broader central and right interiors">
<img src="journey-B.png" alt="Along revised B: brightness dip and recovery, small saturation change">
<img src="explain-H.png" alt="Within one red face: highlight control, not a boundary">
<img src="journey-H.png" alt="Along H: red to white highlight to red within one apparent face">
<h2>Technical overview and profiles</h2>
<img src="paths.png" alt="Raw and annotated sections, eleven paths and planar tangent estimates">
<img src="profiles-1.png" alt="Paths A to E, same-path saturation and value">
<img src="profiles-2.png" alt="Paths F to J, seams versus highlight and shading controls">
<img src="profiles-3.png" alt="Rejected path K: starts in the shadow stripe">
<p><a href="profiles.csv">All RGB/S/V samples</a> · <a href="measurements.json">Descriptive measurements</a> · <a href="report.json">Hashes and parameters</a></p>
''')
    source_paths = set(baseline['sources']) | {
        str(CONFIG.relative_to(ROOT)), 'photo2/beads6_sv_paths.py',
        'photo2/verify_beads6_sv_paths.py',
        'photo2/test_beads6_sv_paths.py','photo2/review/r078/inventory.json',
        'photo2/review/r078/report.json'}
    sources = {p:digest(ROOT/p) for p in sorted(source_paths)}
    artifacts = ['paths.png','profiles-1.png','profiles-2.png','profiles-3.png',
                 'explain-A.png','explain-B.png','explain-H.png','explain-K.png',
                 'journey-A.png','journey-B.png','journey-H.png','journey-K.png',
                 'profiles.csv','measurements.json','review.html']
    report = dict(command=[sys.executable,*sys.argv],parameters=cfg,sources=sources,
                  artifacts={p:digest(args.output/p) for p in artifacts},
                  environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                  checks=dict(baseline_sources_verified=True,inventory_hash_verified=True,active_count=310,
                              active_chain_indices_null=True,path_count=len(summaries),trace_count=len(summaries)*15,sample_rows=len(samples)),
                  encoding='Pillow RGB decode; stored 0–255 channels, no linearization; smooth RGB before bilinear sampling before S/V',
                  metric_definition='Endpoint medians within 2 px; dip = lower endpoint V median minus inner minimum. Peak = inner maximum minus higher endpoint V median. Inner excludes endpoint windows. S delta = end minus start median. Descriptive, not acceptance thresholds.')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    for p in summaries:
        raw = [m for m in p['measurements'] if m['sigma_px']==0]
        nominal = next(m for m in raw if m['offset_px']==0)
        print(p['id'],p['name'],'dip',round(nominal['v_dip'],2),'range',
              [round(min(m['v_dip'] for m in raw),2),round(max(m['v_dip'] for m in raw),2)],
              'S delta',round(nominal['s_delta'],3),'S range',round(nominal['s_range'],3))
    print(report['checks'])


if __name__=='__main__':
    main()
