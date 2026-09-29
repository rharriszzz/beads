"""R114 assisted local evidence pilot; never an automatic bead detector.

Render appearance first; annotate it without opening evaluator ID images.
Analysis consumes only RGB and declared diagnostic anchors. Evaluation is separate.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from matplotlib.patches import Circle, Rectangle
import numpy as np
from PIL import Image, ImageOps
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def render(out):
    """Local straight planar-centerline counterpart, not a fit to the photo."""
    original = (ROOT / 'beads.pov').read_text()
    macro = original[original.index('#macro bead('):original.index('#macro shiny_opaque')]
    header = '''#version 3.7;
#ifndef (Truth) #declare Truth=0; #end
global_settings { assumed_gamma 1.0 }
camera { orthographic location <2,-25,29> look_at <2,0,7>
 right x*22 up z*13 }
light_source { <-10,-20,35> color rgb 1.3 }
background { color rgb 0 }
#if (Truth=0)
plane { z,0 pigment { color rgb <0.55,0.42,0.32> }
 finish { ambient 0.1 diffuse 0.85 } }
#end
#declare bead_radius=4*0.96*sin(pi/6.5);
#declare hole_size_per_bead_size=0.14;
'''
    scene = header + macro + '''
#declare Palette=array[3]{<0.04,0.28,0.65>,<0.8,0.52,0.07>,<0.012,0.012,0.012>};
#declare i=-26;
#while (i<=39)
 #declare p=mod(floor((i+260)/3),3);
 #if (Truth)
  #declare M=material { texture { pigment { color rgb <(i+27)/255,0,0> }
   finish { ambient 0 emission 1 diffuse 0 specular 0 phong 0 } } };
 #else
  #declare M=material { texture { pigment { color rgb Palette[p] }
   finish { ambient 0.08 diffuse 0.75 phong 1.2 phong_size 60 } } };
 #end
 object { bead(M,0.8,0.7,1.0) rotate z*-90
  translate <i*2.5/6.5,4*sin(i*2*pi/6.5),7+4*cos(i*2*pi/6.5)> }
 #declare i=i+1;
#end
'''
    scene_path = out / 'counterpart.pov'
    scene_path.write_text(scene)
    for truth in (0, 1):
        output = out / ('truth.png' if truth else 'appearance.png')
        cmd = ['povray', f'+I{scene_path.resolve()}', f'+O{output.resolve()}',
               '+W880', '+H520', '+FN', '-D', '-A', '+WT2',
               f'Declare=Truth={truth}', f'File_Gamma={1 if truth else 2.2}']
        result = subprocess.run(cmd, capture_output=True, text=True)
        (out / f'render-{truth}.log').write_text(result.stdout + result.stderr)
        result.check_returncode()
    (out / 'render-provenance.json').write_text(json.dumps(dict(
        scene_sha256=digest(scene_path), source_scene_sha256=digest(ROOT/'beads.pov'),
        appearance_sha256=digest(out/'appearance.png'), truth_sha256=digest(out/'truth.png'),
        note='Local straight section; original bead macro; no photo geometry fitting. '
        'Index/palette truth is evaluator-only. No AA, 880x520, 2 threads; '
        'File_Gamma=2.2 appearance, 1 truth. Bead centers progress +x, '
        'minor phase +i*2pi/6.5; centers are 3D around a planar straight axis.'), indent=2)+'\n')


def disk(rgb, xy, radius=3):
    x,y = xy
    yy,xx = np.mgrid[int(y)-radius:int(y)+radius+1,
                     int(x)-radius:int(x)+radius+1]
    keep = (xx-x)**2+(yy-y)**2 <= radius**2
    return rgb[yy[keep],xx[keep]]


def summary(pixels):
    hsv = rgb_to_hsv(pixels)
    chroma = np.ptp(pixels, axis=1)
    z = np.sum(chroma*np.exp(2j*np.pi*hsv[:,0]))
    # Descriptive image colors: no fitted pigment or color-name thresholds.
    return dict(rgb=np.median(pixels, axis=0).tolist(),
                hue_deg=float(np.angle(z)*180/np.pi % 360) if chroma.sum()>0 else None,
                hue_strength=float(abs(z)/chroma.sum()) if chroma.sum()>0 else 0,
                s=float(np.median(hsv[:,1])), v=float(np.median(hsv[:,2])),
                v10=float(np.quantile(hsv[:,2],.1)), v90=float(np.quantile(hsv[:,2],.9)))


def groups(features, threshold):
    labels = fcluster(linkage(features, method='complete'), threshold, criterion='distance')
    # Stable appearance IDs ordered by first observation, not a color name.
    remap = {v:i+1 for i,v in enumerate(dict.fromkeys(labels))}
    return [remap[v] for v in labels]


def infer_graph(nodes, edges):
    """Check each entire hypothesis, retaining contradictions and duplicate indices."""
    values = {nodes[0]:0}
    for _ in nodes:
        for u,v,d in edges:
            if u in values and v not in values: values[v]=values[u]+d
            if v in values and u not in values: values[u]=values[v]-d
    conflicts = [(u,v,d) for u,v,d in edges if u in values and v in values
                 and values[v]-values[u]!=d]
    duplicates = [(u,v) for j,u in enumerate(values) for v in list(values)[j+1:]
                  if values[u]==values[v]]
    return dict(indices=values, conflicts=conflicts, duplicates=duplicates,
                disconnected=[n for n in nodes if n not in values])


def analyze(cfgpath, out):
    cfg = json.loads(cfgpath.read_text())
    source = ROOT / cfg['image']
    im = ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    rgb = np.asarray(im)/255.
    obs = cfg['observations']; lookup = {o['id']:o for o in obs}
    graphs={name:infer_graph(cfg['graph_nodes'],edges) for name,edges in cfg['hypotheses'].items()}
    summaries = [summary(disk(rgb,o['xy'])) for o in obs]
    features = np.array([s['rgb'] for s in summaries])
    thresholds = [.12,.18,.24]
    palette = {str(t):groups(features,t) for t in thresholds}
    perturbed = []
    for shift in [(-2,0),(2,0),(0,-2),(0,2)]:
        shifted = np.array([summary(disk(rgb,np.array(o['xy'])+shift))['rgb'] for o in obs])
        # Compare to fixed, image-derived group medians. Fit/holdout separated below.
        prototypes = {p:np.median(features[np.array(palette['0.18'])==p],axis=0)
                      for p in set(palette['0.18'])}
        predicted=[min(prototypes,key=lambda p:np.linalg.norm(f-prototypes[p])) for f in shifted]
        perturbed.append(dict(shift=shift, nearest_groups=predicted))
    holdout=[]
    labels=np.array(palette['0.18'])
    for j,o in enumerate(obs):
        train=np.arange(len(obs))!=j
        prototypes={p:np.median(features[train & (labels==p)],axis=0)
                    for p in set(labels[train])}
        predicted=min(prototypes,key=lambda p:np.linalg.norm(features[j]-prototypes[p]))
        holdout.append(dict(id=o['id'],nearest_group=int(predicted),
                            same_group=bool(predicted==labels[j]),
                            group_has_other_samples=bool(sum(labels==labels[j])>1)))
    rows=[]
    for j,(o,s) in enumerate(zip(obs,summaries)):
        rows.append(dict(observation_id=o['id'],x=o['xy'][0],y=o['xy'][1],
            visibility=o['visibility'],body_status=o['body_status'],
            component='conditional_triangle' if o['id'] in cfg['graph_nodes'] else 'unresolved',
            component_index='',bead_index='',
            local_index_alternatives=';'.join(f"{name}:{g['indices'][o['id']]}" for name,g in graphs.items() if o['id'] in g['indices']),
            appearance_group=f"P{palette['0.18'][j]}",color_status='appearance_only',
            median_rgb=','.join(f'{v:.4f}' for v in s['rgb']),hue_deg=s['hue_deg'],
            hue_strength=s['hue_strength'],S=s['s'],V=s['v'],
            reason=o['reason']))
    write_csv(out/'observations.csv',rows)
    paths=[]; samples=[]
    for route in cfg['paths']:
        start=np.array(route.get('start',lookup[route['u']]['xy']),dtype=float)
        end=np.array(route.get('end',lookup[route['v']]['xy']),dtype=float)
        length=np.linalg.norm(end-start); normal=np.array([-(end-start)[1],(end-start)[0]])/length
        n=int(np.ceil(length))+1; t=np.linspace(0,1,n)
        offsets=[]
        for shift in (-2,0,2):
            xy=start[None,:]+t[:,None]*(end-start)[None,:]+shift*normal
            pixels=np.array([map_coordinates(rgb[:,:,c], [xy[:,1],xy[:,0]],order=1) for c in range(3)]).T
            hsv=rgb_to_hsv(pixels); interior=(t>=.2)&(t<=.8)
            k=np.where(interior)[0][np.argmin(hsv[interior,2])]
            offsets.append(dict(offset_px=shift,min_v=float(hsv[k,2]),min_t=float(t[k]),
                endpoint_v_min=float(min(hsv[0,2],hsv[-1,2])),
                dip=float(min(hsv[0,2],hsv[-1,2])-hsv[k,2])))
            if shift==0:
                for a,(p,h) in enumerate(zip(pixels,hsv)):
                    samples.append(dict(path=route['id'],distance_px=float(t[a]*length),
                        x=float(xy[a,0]),y=float(xy[a,1]),R=p[0],G=p[1],B=p[2],H=h[0]*360,S=h[1],V=h[2]))
        paths.append({**route,'start':start.tolist(),'end':end.tolist(),
                      'length_px':float(length),'offsets':offsets})
    write_csv(out/'path-samples.csv',samples)
    edge_rows=[]
    for name,edges in cfg['hypotheses'].items():
        for u,v,d in edges:
            a=np.array(lookup[u]['xy']);b=np.array(lookup[v]['xy']);delta=b-a
            edge_rows.append(dict(hypothesis=name,u=u,v=v,delta=d,
                length_px=float(np.linalg.norm(delta)),angle_image_deg=float(np.degrees(np.arctan2(delta[1],delta[0]))),
                status='conditional_unverified',reason='image adjacency; family/sign not calibrated'))
    write_csv(out/'edges.csv',edge_rows)
    checks = {}
    checks['contradiction_detected']=bool(infer_graph(['a','b','c'], [('a','b',1),('b','c',6),('a','c',6)])['conflicts'])
    checks['duplicate_detected']=bool(infer_graph(['a','b','c'], [('a','b',1),('a','c',1)])['duplicates'])
    checks['disconnected_retained']=infer_graph(['a','b'],[])['disconnected']==['b']
    checks['hue_wrap']=min(summary(np.array([[1,0,.02],[1,.02,0]]))['hue_deg'],
                           360-summary(np.array([[1,0,.02],[1,.02,0]]))['hue_deg'])<1e-6
    assert all(checks.values()), checks
    report=dict(config_sha256=digest(cfgpath),image_sha256=digest(source),script_sha256=digest(Path(__file__)),
        assistance=cfg['assistance'],parameters=dict(disk_radius_px=3,thresholds=thresholds,
            color_feature='median encoded RGB, complete linkage Euclidean distance',
            path='bilinear RGB at <=1 px spacing; HSV after interpolation; no smoothing',
            crop=cfg['crop'],coordinate='EXIF-transposed source pixel centers, x right, y down'),
        summaries=summaries,palette_groups=palette,anchor_perturbations=perturbed,
        leave_one_anchor_out_fixed_groups=holdout,paths=paths,graphs=graphs,checks=checks)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    # Raw context, anchors, and separate uncertainty panel.
    fig,axes=plt.subplots(1,3,figsize=(15,6),layout='constrained')
    x0,y0,x1,y1=cfg['crop']
    for ax in axes:
        ax.imshow(im);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0);ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw RGB: unchanged pixels')
    axes[1].set_title('Assisted interior disks, radius 3 px\nLabels are observation IDs, not string indices')
    axes[2].set_title('Candidate connections / unresolved bodies\nDashed lines are hypotheses, not outlines')
    for o in obs:
        x,y=o['xy'];color='#00ffff' if o['body_status']=='proposed' else '#ffae00'
        axes[1].add_patch(Circle((x,y),3,fill=False,edgecolor=color,lw=1))
        axes[1].text(x+3,y-3,o['id'],color='white',fontsize=9,weight='bold',bbox=dict(facecolor='black',alpha=.55,pad=1))
        if o['body_status']!='proposed':
            axes[2].add_patch(Circle((x,y),7,fill=False,edgecolor=color,ls='--'))
            axes[2].text(x+5,y,o['id'],color=color,fontsize=10)
    for p in paths:
        a,b=np.array(p['start']),np.array(p['end'])
        axes[2].plot([a[0],b[0]],[a[1],b[1]],'--',color='cyan',lw=1)
    fig.savefig(out/'inventory.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,5),layout='constrained')
    for ax in axes:
        ax.imshow(im);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
    axes[0].set_title('Raw context; no accepted outlines')
    for ax,(name,g) in zip(axes[1:],graphs.items()):
        ax.set_title(name+': conditional local indices\n'+', '.join(f'{k}={v}' for k,v in g['indices'].items()))
        for u,v,d in cfg['hypotheses'][name]:
            a,b=np.array(lookup[u]['xy']),np.array(lookup[v]['xy'])
            ax.plot([a[0],b[0]],[a[1],b[1]],'--',color='cyan')
            ax.text(*((a+b)/2),f'{d:+d}',color='yellow',fontsize=11)
        for k in cfg['graph_nodes']:
            ax.text(*lookup[k]['xy'],k,color='white',fontsize=12,weight='bold')
    fig.savefig(out/'graph-alternatives.png',dpi=150);plt.close(fig)
    if 'tangent' in cfg:
        a,b=np.array(cfg['tangent'][0]),np.array(cfg['tangent'][1])
        delta=b-a
        report['manual_tangent']=dict(endpoints=[a.tolist(),b.tolist()],
            angle_image_deg=float(np.degrees(np.arctan2(delta[1],delta[0]))),
            endpoint_y_perturbation_3px_angles=[float(np.degrees(np.arctan2(delta[1]+s,delta[0]))) for s in [-6,6]],
            status='visual large-scale direction only; not physical centerline or camera calibration')
        fig,axes=plt.subplots(1,2,figsize=(10,5),layout='constrained')
        axes[0].imshow(im);axes[0].add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor='cyan',lw=1))
        axes[0].axis('off');axes[0].set_title('Selected diagnostic patch in full photo')
        axes[1].imshow(im);axes[1].set_xlim(1260,1460);axes[1].set_ylim(365,210)
        axes[1].plot([a[0],b[0]],[a[1],b[1]],'--',color='cyan')
        axes[1].set_title('Manual large-scale tangent proposal\nDashed line is not a sampling route or fitted centerline')
        fig.savefig(out/'context.png',dpi=150);plt.close(fig)
    if 'question_pair' in cfg:
        u,v=cfg['question_pair'];a,b=np.array(lookup[u]['xy']),np.array(lookup[v]['xy']);mid=(a+b)/2
        fig,axes=plt.subplots(1,2,figsize=(9,5),layout='constrained')
        for ax in axes:
            ax.imshow(im);ax.set_xlim(mid[0]-40,mid[0]+40);ax.set_ylim(mid[1]+40,mid[1]-40)
            ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
        axes[0].set_title('Raw neighborhood')
        axes[1].set_title('Is D a separate bead from B?\nCircles mark samples, not bead outlines')
        for label,p in [(u,a),(v,b)]:
            axes[1].add_patch(Circle(p,3,fill=False,edgecolor='cyan',lw=1.5))
            axes[1].text(p[0]+4,p[1],label,color='white',weight='bold',fontsize=14)
        fig.savefig(out/'question.png',dpi=160);plt.close(fig)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    fig,axes=plt.subplots(len(paths),3,figsize=(13,3.2*len(paths)),squeeze=False,layout='constrained')
    for axs,p in zip(axes,paths):
        a,b=np.array(p['start']),np.array(p['end']);mid=(a+b)/2
        half=max(30,np.max(abs(b-a))/2+15)
        axs[0].imshow(im);axs[0].set_xlim(mid[0]-half,mid[0]+half);axs[0].set_ylim(mid[1]+half,mid[1]-half)
        axs[0].scatter([a[0],b[0]],[a[1],b[1]],facecolors='none',edgecolors='cyan',s=55)
        axs[0].text(a[0],a[1]-4,'P',color='cyan');axs[0].text(b[0],b[1]-4,'Q',color='cyan')
        axs[0].set_title(f"{p['id']}: interior endpoints first")
        axs[1].imshow(im);axs[1].set_xlim(mid[0]-half,mid[0]+half);axs[1].set_ylim(mid[1]+half,mid[1]-half)
        axs[1].plot([a[0],b[0]],[a[1],b[1]],color='cyan',lw=1)
        for t in [0,.25,.5,.75,1]:
            v=a+t*(b-a);axs[1].text(*v,str(int(t*100)),color='white',fontsize=8)
        axs[1].set_title('Straight sampling path; stops = percent')
        ss=[s for s in samples if s['path']==p['id']]
        for key,color in [('V','black'),('S','orange')]:
            axs[2].plot([s['distance_px'] for s in ss],[s[key] for s in ss],label=key,color=color)
        axs[2].set_ylim(0,1);axs[2].legend();axs[2].set_xlabel('distance P → Q (px)')
        axs[2].set_title(p['purpose'],fontsize=10)
    fig.savefig(out/'paths.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,4),layout='constrained')
    for j,(o,s) in enumerate(zip(obs,summaries)):
        ax.scatter(j,s['v'],c=[s['rgb']],s=250,edgecolors='black')
        ax.plot([j,j],[s['v10'],s['v90']],color='gray')
        ax.text(j,s['v90']+.04,f"P{palette['0.18'][j]}",ha='center')
    ax.set_xticks(range(len(obs)),[o['id'] for o in obs]);ax.set_ylim(0,1)
    ax.set_ylabel('Encoded HSV V (0–1)');ax.set_title('Interior colors: median RGB dots, 10–90% V bars\nAppearance groups at distance 0.18; these are not recovered pigments')
    fig.savefig(out/'palette.png',dpi=150);plt.close(fig)


def evaluate(cfgpath,out):
    """Only this stage reads identity truth; never feeds corrections into inference."""
    cfg=json.loads(cfgpath.read_text())
    truth=np.asarray(Image.open(out/'truth.png'))[:,:,0].astype(int)-27
    report=json.loads((out/'analysis/report.json').read_text())
    mapping={o['id']:int(truth[o['xy'][1],o['xy'][0]]) for o in cfg['observations']}
    rows=[]
    for o in cfg['observations']:
        i=mapping[o['id']];pixels=disk(truth[:,:,None],o['xy']).ravel()
        rows.append(dict(id=o['id'],truth_index=i,truth_palette=((i+260)//3)%3,
                         disk_purity=float(np.mean(pixels==i))))
    pair_checks={}
    for th,labels in report['palette_groups'].items():
        errors=[]
        for a in range(len(rows)):
            for b in range(a+1,len(rows)):
                if (labels[a]==labels[b])!=(rows[a]['truth_palette']==rows[b]['truth_palette']):
                    errors.append([rows[a]['id'],rows[b]['id']])
        pair_checks[th]=dict(errors=errors,pairs=len(rows)*(len(rows)-1)//2)
    edges=[]
    for name,es in cfg['hypotheses'].items():
        for u,v,d in es:
            edges.append(dict(hypothesis=name,u=u,v=v,proposed=d,actual=mapping[v]-mapping[u],
                              correct=d==mapping[v]-mapping[u]))
    alignment={}
    for name,g in report['graphs'].items():
        options=[]
        for sign in [-1,1]:
            origin=mapping[cfg['graph_nodes'][0]]
            errs={k:sign*v+origin-mapping[k] for k,v in g['indices'].items()}
            options.append(dict(sign=sign,origin=origin,errors=errs,
                                exact=sum(v==0 for v in errs.values())))
        alignment[name]=max(options,key=lambda x:x['exact'])
    result=dict(assistance='All observation anchors and proposed edges supplied manually from RGB. '
        'No automatic detection. Evaluator maps anchors to rendered IDs only after frozen RGB analysis.',
        observations=rows,unique_bodies=len(set(mapping.values())),signed_edges=edges,
        color_pair_checks=pair_checks,one_component_alignment=alignment,
        detection_coverage='not measured: assisted anchors, no reference-blind detector or complete inventory')
    (out/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['render','analyze','evaluate'])
    parser.add_argument('--config',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r114')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if args.mode=='render':render(args.output)
    elif args.mode=='analyze':analyze(args.config,args.output)
    else:evaluate(args.config,args.output)


if __name__=='__main__':main()
