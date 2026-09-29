"""R118/R119 minor-outward versus nearest-camera surface visibility check.

The user clarified the minor-circle direction; no two-point threshold is assumed.
POV-Ray ray intersections and ID area are evaluators, not photo inference inputs.
"""
import argparse
from pathlib import Path
import json
import os
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import matplotlib
matplotlib.use('Agg')
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from bead_placement import Rope, Camera, bead_surface_samples, closest_camera_sample, minor_outward_point
from check_placement import ROOT, source_parts, run_pov, vec, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r118')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    rope=Rope(676);camera=Camera((60,-160,120),(45,4,8),800,600,angle=12)
    indices=list(range(-20,41))
    nearest=[];refined=[]
    for i in indices:
        nearest.append(closest_camera_sample(bead_surface_samples(rope,i),camera))
        refined.append(closest_camera_sample(bead_surface_samples(rope,i,64,512),camera))
    nearest=np.array(nearest);refined=np.array(refined)
    xy,_=camera.project(refined);coarse_xy,_=camera.project(nearest)
    outward=np.array([minor_outward_point(rope,i) for i in indices])
    outward_xy,_=camera.project(outward)
    torus_distance=np.hypot(np.hypot(outward[:,0],outward[:,1])-rope.chain_major,
                            outward[:,2]-rope.chain_minor-2*rope.bead_radius)
    assert np.max(abs(torus_distance-(rope.chain_minor+rope.bead_radius)))<1e-10
    parameters,placement,macro=source_parts()
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
        +f'camera {{location {vec(camera.location)} look_at {vec(camera.look_at)} '
        +'right x*4/3 angle 12}\n#declare nbeads=676;\n#declare beads_per_row=6.5;\n'
        +'#declare rclock=0;\n'+parameters+'#declare hole_size_per_bead_size=.14;\n'+macro)
    objects=[];individual=[]
    for label,index in enumerate(indices,1):
        prefix=f'#declare bead_index={index % rope.nbeads};\n'+placement
        obj=('object {bead(material {texture {pigment {rgb <'+str(label)+'/255,0,0>} '
             'finish {ambient 0 emission 1 diffuse 0}}},.8,.7,1) '
             'rotate <0,0,chain_angle> translate t1+t2+<0,0,chain_minor+2*bead_radius>}')
        objects.append(prefix+obj+'\n');individual.append((prefix,obj))
    raycsv=out/'ray-check.csv'
    scene=out/'visibility.pov'
    text=header+'#declare AllBeads=union {\n'+''.join(objects)+'}\nobject {AllBeads}\n'
    text+=f'#fopen Result "{raycsv.resolve()}" write\n'
    for points in [refined,outward]:
        for index,p,(prefix,obj) in zip(indices,points,individual):
            text+=prefix+'#declare Own='+obj+';\n'
            text+=f'#declare Eye={vec(camera.location)};\n#declare Target={vec(p)};\n'
            text+='#declare N=<0,0,0>;\n#declare H=trace(AllBeads,Eye,Target-Eye,N);\n'
            text+='#declare N2=<0,0,0>;\n#declare H2=trace(Own,Eye,Target-Eye,N2);\n'
            text+='#write(Result,'+str(index)+',",",str(vlength(Target-Eye),0,12),",",str(vlength(H-Eye),0,12),",",str(vlength(N),0,12),",",str(vlength(H2-Eye),0,12),",",str(vlength(N2),0,12),"\\n")\n'
    text+='#fclose Result\n';scene.write_text(text)
    png,command=run_pov(scene,800,600)
    rays=np.loadtxt(raycsv,delimiter=',');labels=np.asarray(Image.open(png))[:,:,0]
    # Evaluator-only denominators: exact same bead/view with neighbors removed.
    # Keep clipping explicit; this is not an image-side visibility classifier.
    def isolated(k):
        prefix,obj=individual[k];path=out/f'isolated-{k}.pov'
        path.write_text(header+prefix+obj+'\n')
        image,_=run_pov(path,800,600)
        mask=np.asarray(Image.open(image))[:,:,0]>0
        yy,xx=np.where(mask)
        clipped=bool(len(xx) and (xx.min()==0 or xx.max()==799 or yy.min()==0 or yy.max()==599))
        return int(mask.sum()),clipped
    with ThreadPoolExecutor(max_workers=2) as pool:
        isolated_results=list(pool.map(isolated,range(len(indices))))
    rows=[]
    for k,index in enumerate(indices):
        _,target,hit,normal,own,ownnormal=rays[k]
        own_error=abs(target-own)
        assert ownnormal>.9 and own_error<1e-4,(index,own_error,ownnormal)
        _,out_target,out_hit,out_normal,out_own,out_ownnormal=rays[k+len(indices)]
        assert out_ownnormal>.9
        out_exposed=out_normal>.9 and abs(out_target-out_hit)<1e-4
        area=int(np.sum(labels==k+1));point_visible=normal>.9 and abs(target-hit)<1e-4
        isolated_area,clipped=isolated_results[k]
        # Centrality in image: centroid displacement normal to projected local
        # centerline, divided by the reference torus envelope's projected halfwidth.
        _,degrees=rope.place(index);theta=np.radians(degrees)
        radial=np.array([np.cos(theta),np.sin(theta),0.]);tangent=np.array([-np.sin(theta),np.cos(theta),0.])
        axis=rope.chain_major*radial+np.array([0,0,rope.chain_minor+2*rope.bead_radius])
        axis_xy,_=camera.project(axis);tangent_xy,_=camera.project(axis+tangent)
        t=tangent_xy-axis_xy;n=np.array([-t[1],t[0]])/np.linalg.norm(t)
        a=np.linspace(0,2*np.pi,256,endpoint=False)
        envelope=axis+(rope.chain_minor+rope.bead_radius)*(np.cos(a)[:,None]*radial+np.sin(a)[:,None]*np.array([0,0,1]))
        env_xy,_=camera.project(envelope)
        yy,xx=np.where(labels==k+1)
        normal_offset=float((np.array([xx.mean(),yy.mean()])-axis_xy)@n) if area else None
        offsets=(env_xy-axis_xy)@n
        halfwidth=max(offsets) if normal_offset is not None and normal_offset>=0 else -min(offsets)
        centrality=abs(normal_offset)/halfwidth if area else None
        rows.append(dict(index=index,nearest_camera_point=refined[k].tolist(),projected_xy=xy[k].tolist(),
            coarse_to_fine_projected_shift_px=float(np.linalg.norm(xy[k]-coarse_xy[k])),
            own_surface_ray_error=float(own_error),occluder_depth_gap=float(target-hit),
            nearest_point_exposed=bool(point_visible),rendered_body_pixels=area,
            body_has_any_rendered_pixel=area>0,
            context_supported=indices[0]+13<=index<=indices[-1]-13,
            outward_point=outward[k].tolist(),
            outward_projected_xy=outward_xy[k].tolist(),outward_point_exposed=bool(out_exposed),
            outward_own_depth_gap=float(out_target-out_own),outward_all_depth_gap=float(out_target-out_hit),
            isolated_body_pixels=isolated_area,isolated_clipped=clipped,
            visible_fraction_of_isolated=float(area/isolated_area) if isolated_area else None,
            visible_centroid_normalized_offset=centrality))
    witnesses=[r for r in rows if r['body_has_any_rendered_pixel'] and not r['nearest_point_exposed']]
    outward_witnesses=[r for r in rows if r['body_has_any_rendered_pixel'] and not r['outward_point_exposed']]
    subsets=[]
    for fraction in [.25,.5,.75]:
        for band in [.4,.6]:
            eligible=[r for r in rows if r['context_supported'] and not r['isolated_clipped'] and r['visible_fraction_of_isolated'] is not None
                      and r['visible_fraction_of_isolated']>=fraction
                      and r['visible_centroid_normalized_offset'] is not None
                      and r['visible_centroid_normalized_offset']<=band]
            subsets.append(dict(min_visible_fraction=fraction,max_normalized_centerline_distance=band,
                eligible_indices=[r['index'] for r in eligible],
                hidden_outward_indices=[r['index'] for r in eligible if not r['outward_point_exposed']]))
    report=dict(parameters=dict(nbeads=676,indices=indices,roundedness=.8,height_ratio=.7,
            coarse_sampling=[32,256],fine_sampling=[64,512],ray_tolerance=1e-4,
            camera=camera.__dict__),source_scene_sha256=sha(ROOT/'beads.pov'),
            placement_python_sha256=sha(ROOT/'photo2/bead_placement.py'),checker_sha256=sha(Path(__file__)),
            generated_scene_sha256=sha(scene),id_image_sha256=sha(png),command=command,observations=rows,
            nearest_hidden_but_body_visible_indices=[r['index'] for r in witnesses],
            outward_hidden_but_body_visible_indices=[r['index'] for r in outward_witnesses],
            substantial_central_subsets=subsets,
            subset_caveat='Evaluator uses known rendered centerline/envelope and isolated masks. '
                          'Exclude 13 model indices at each finite segment end (two turns of context), '
                          'so open-end exposure does not masquerade as necklace visibility. '
                          'Thresholds .25/.5/.75 and .4/.6 are diagnostic, not maker-supplied or image-learned. '
                          'This one pose is not validation around the entire ring.',
            outward_definition='R119 minor-circle outward direction; exact midpoint of the outer bead wall, '
                               'on the reference torus with minor radius chain_minor+bead_radius.',
            note='Nearest camera point on individual bead; neighbor occlusion evaluated separately. '
                 'Any-pixel visibility includes slivers and image-boundary truncation. R120 substantial/central '
                 'subsets separately exclude clipped isolated silhouettes and stratify visible fraction/centrality. '
                 'No unspecified two-point distance/angle rule is implemented. '
                 'This checks the R119 claim that an outward torus point must be visible if its bead is visible.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    # Visualize body IDs with a deterministic varied palette, no visibility inference.
    rng=np.random.default_rng(118);palette=rng.uniform(.2,.95,(62,3));palette[0]=0
    rgb=palette[labels]
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    axes[0].imshow(rgb);axes[0].set_title('Evaluator ID view: one color per modeled bead\nColor here encodes identity, not pigment')
    axes[1].imshow(rgb)
    selected=[r for r in rows if 0<=r['index']<=20]
    for r in selected:
        x,y=r['projected_xy'];color='lime' if r['nearest_point_exposed'] else 'red'
        axes[1].plot(x,y,'+',color=color,ms=6)
        axes[1].text(x+4,y,r['index'],color='white',fontsize=7)
    axes[1].set_title('Nearest-camera surface points, indices 0–20\nGreen: exposed; red: blocked (point visibility only)')
    for ax in axes:ax.set_xlabel('image x (px)');ax.set_ylabel('image y (px)')
    fig.savefig(out/'nearest-camera-check.png',dpi=150);plt.close(fig)
    if outward_witnesses:
        # Largest visible area avoids presenting a tiny-sliver-only counterexample.
        witness=max((r for r in outward_witnesses if r['context_supported']),key=lambda r:r['rendered_body_pixels'])
        mask=labels==indices.index(witness['index'])+1
        yy,xx=np.where(mask);px,py=witness['outward_projected_xy']
        bounds=[min(xx.min(),px)-25,max(xx.max(),px)+25,
                min(yy.min(),py)-25,max(yy.max(),py)+25]
        beauty_path=ROOT/'photo2/output/r117/model-appearance.png'
        appearance=np.asarray(Image.open(beauty_path)) if beauty_path.exists() else rgb
        fig,axes=plt.subplots(1,2,figsize=(10,5),layout='constrained')
        axes[0].imshow(appearance);axes[1].imshow(rgb)
        for ax in axes:
            ax.contour(mask,levels=[.5],colors=['cyan'],linewidths=1)
            ax.plot(px,py,'o',mfc='none',mec='red',ms=10,mew=2)
            ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[3],bounds[2])
            ax.set_xlabel('image x (px)');ax.set_ylabel('image y (px)')
        axes[0].set_title(f"Visible part of modeled bead {witness['index']}\nCyan outline: {witness['rendered_body_pixels']} rendered pixels")
        axes[1].set_title('Red circle: its minor-outward torus point\nRay test: point hidden although part of bead is visible')
        fig.savefig(out/'outward-counterexample.png',dpi=170);plt.close(fig)
        report['illustrated_witness']=witness
        report['illustration_appearance_sha256']=sha(beauty_path) if beauty_path.exists() else None
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
    valid=[r for r in rows if r['context_supported'] and r['body_has_any_rendered_pixel'] and not r['isolated_clipped']]
    for exposed,color,label in [(True,'tab:blue','Outward point exposed'),(False,'tab:red','Outward point blocked')]:
        group=[r for r in valid if r['outward_point_exposed']==exposed]
        ax.scatter([r['visible_centroid_normalized_offset'] for r in group],
                   [r['visible_fraction_of_isolated'] for r in group],c=color,label=label)
    ax.axvline(.4,color='gray',ls='--');ax.axvline(.6,color='gray',ls=':')
    ax.axhline(.5,color='gray',ls='--');ax.set_xlabel('Visible centroid distance from centerline / envelope halfwidth')
    ax.set_ylabel('Visible pixels / isolated-bead pixels');ax.legend()
    ax.set_title('R120: separate central/substantial bodies from edge remnants\nKnown synthetic geometry; thresholds are diagnostic choices')
    fig.savefig(out/'central-visibility.png',dpi=160);plt.close(fig)
    print(json.dumps(dict(bodies=len(rows),visible_pixel_bodies=sum(r['body_has_any_rendered_pixel'] for r in rows),
        nearest_hidden_but_body_visible=report['nearest_hidden_but_body_visible_indices'],
        outward_hidden_but_body_visible=report['outward_hidden_but_body_visible_indices'],
        witness=report.get('illustrated_witness'),
        substantial_central_subsets=subsets,
        max_surface_error=max(r['own_surface_ray_error'] for r in rows),
        max_refinement_shift_px=max(r['coarse_to_fine_projected_shift_px'] for r in rows)),indent=2))


if __name__=='__main__':main()
