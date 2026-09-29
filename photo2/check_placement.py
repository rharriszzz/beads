"""R117: independent POV-Ray parity and rendered-marker projection checks.

All marker correspondences are explicitly supplied calibration, not detections
of physical bead centers in the photo. The photo panel only selects a pilot set.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from PIL import Image, ImageOps

from bead_placement import Rope, Camera, fit_similarity, apply_similarity

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vec(values):
    return '<'+','.join(format(float(x), '.16g') for x in values)+'>'


def run_pov(scene, width, height):
    png = scene.with_suffix('.png')
    command = ['povray', '+I'+str(scene.resolve()), '+O'+str(png.resolve()),
               f'+W{width}', f'+H{height}', '+FN', '-D', '-A', '+WT2', 'File_Gamma=1']
    p = subprocess.run(command, capture_output=True, text=True)
    scene.with_suffix('.log').write_text(p.stdout+p.stderr)
    p.check_returncode()
    return png, command


def source_parts():
    source = (ROOT/'beads.pov').read_text()
    parameters = source[source.index('#declare nrows ='):source.index('/* bead_major -')]
    placement = source[source.index('  #declare chain_angle ='):source.index('  object{ beads[color_pattern')]
    macro = source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
    return parameters, placement, macro


def parity(out):
    parameters, placement, _ = source_parts()
    cases = []
    for number, (n, clock, hand) in enumerate([(672,0.,1),(672,.125,1),(676,0.,1),
                                              (731,.72,1),(676,.125,-1)]):
        rope = Rope(n, rclock=clock, helicity=hand)
        formula = placement
        if hand == -1:
            formula = formula.replace('360*(bead_index/exact_beads_per_row', '-360*(bead_index/exact_beads_per_row')
        csvpath = out/f'parity-{number}.csv'
        scene = out/f'parity-{number}.pov'
        scene.write_text('#version 3.7;\n'+f'#declare nbeads={n};\n#declare beads_per_row=6.5;\n'
            +f'#declare rclock={clock};\n'+parameters
            +f'#fopen Result "{csvpath.resolve()}" write\n#declare bead_index=0;\n'
            +'#while (bead_index<nbeads)\n'+formula
            +'#write(Result, bead_index, ",", vstr(3,t1+t2+<0,0,chain_minor+2*bead_radius>,",",0,12), ",", str(chain_angle,0,12), "\\n")\n'
            +'#declare bead_index=bead_index+1;\n#end\n#fclose Result\n'
            +'camera {location <0,0,-10> look_at 0}\nsphere {0,1 pigment {rgb 0}}\n')
        _, command = run_pov(scene,1,1)
        actual = np.loadtxt(csvpath,delimiter=',')
        xyz, angle = rope.place(actual[:,0])
        position_error = np.linalg.norm(xyz-actual[:,1:4],axis=1)
        rotation_error = abs(angle-actual[:,4])
        assert position_error.max()<1e-8 and rotation_error.max()<1e-8
        cases.append(dict(parameters=asdict(rope),nrows=rope.nrows,exact_beads_per_row=rope.exact_beads_per_row,
            bead_radius=rope.bead_radius,chain_major=rope.chain_major,compared=n,
            max_position_error=float(position_error.max()),max_rotation_error_deg=float(rotation_error.max()),
            scene_sha256=sha(scene),command=command))
    return cases


def projection(out):
    rope = Rope(676)
    camera = Camera((60,-160,120),(45,4,8),800,600,angle=12)
    indices = np.array([0,1,6,7,13,14,20])
    xyz, angle = rope.place(indices)
    predicted, depth = camera.project(xyz)
    parameters, placement, macro = source_parts()
    header = ('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
       +f'camera {{ location {vec(camera.location)} look_at {vec(camera.look_at)} '
       +f'right x*{camera.width/camera.height} angle {camera.angle} }}\n'
       +'#declare nbeads=676;\n#declare beads_per_row=6.5;\n#declare rclock=0;\n'+parameters)
    scene = out/'markers.pov'
    # Position markers with the independently executed original POV expressions.
    body = ''
    for label, index in enumerate(indices,1):
        body += f'#declare bead_index={index};\n'+placement
        body += ('sphere {t1+t2+<0,0,chain_minor+2*bead_radius>, .16 '
                 +f'pigment {{rgb <{label}/255,0,0>}} finish {{ambient 0 emission 1 diffuse 0}}}}\n')
    scene.write_text(header+body)
    markerpng, command = run_pov(scene,camera.width,camera.height)
    labels = np.asarray(Image.open(markerpng))[:,:,0]
    measured=[]; areas=[]
    for label in range(1,len(indices)+1):
        yy,xx = np.where(labels==label)
        assert len(xx)>0, f'marker {label} missing'
        measured.append([float(xx.mean()),float(yy.mean())]); areas.append(len(xx))
    measured=np.array(measured)
    errors=np.linalg.norm(predicted-measured,axis=1)
    assert errors.max()<.8, errors
    # Calibration pairs are supplied. Holdout marker IDs are not fit inputs.
    train=np.array([0,2,4]); hold=np.array([1,3,5,6])
    fit=fit_similarity(predicted[train],measured[train])
    fitted=apply_similarity(predicted,fit)
    held_errors=np.linalg.norm(fitted[hold]-measured[hold],axis=1)
    assert held_errors.max()<1., held_errors
    wrong=fit_similarity(predicted[train],measured[train[::-1]])
    wrong_errors=np.linalg.norm(apply_similarity(predicted[hold],wrong)-measured[hold],axis=1)
    assert np.mean(wrong_errors)>5., wrong_errors
    # Separate appearance illustration; marker-centroid observations are NOT
    # replaced with visible-body centroids or used as a photo inverse test.
    beauty = out/'model-appearance.pov'
    objects=''
    for index in range(-20,41):
        objects+=f'#declare bead_index={index % rope.nbeads};\n'+placement
        pigment=['<.75,.03,.02>','<.8,.55,.04>','<.015,.015,.015>'][(index//3)%3]
        objects+=('object {bead(material {texture {pigment {rgb '+pigment+'} '
                  'finish {ambient .08 diffuse .75 phong 1.2}}},.8,.7,1) '
                  'rotate <0,0,chain_angle> translate t1+t2+<0,0,chain_minor+2*bead_radius>}\n')
    beauty.write_text(header+'#declare hole_size_per_bead_size=.14;\n'+macro
        +'light_source {<-20,-80,100> rgb 1.4}\nplane {z,0 pigment {rgb <.55,.45,.35>}}\n'+objects)
    # Appearance uses display encoding; geometry/marker pass above uses gamma=1.
    cmd=['povray','+I'+str(beauty.resolve()),'+O'+str(beauty.with_suffix('.png').resolve()),
         '+W800','+H600','+FN','-D','-A','+WT2','File_Gamma=2.2']
    p=subprocess.run(cmd,capture_output=True,text=True)
    beauty.with_suffix('.log').write_text(p.stdout+p.stderr);p.check_returncode()
    im=Image.open(beauty.with_suffix('.png'))
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    axes[0].imshow(im);axes[0].set_title('POV-Ray bead geometry\nCrosses are projected physical centers, possibly occluded')
    axes[0].scatter(predicted[:,0],predicted[:,1],marker='+',color='cyan')
    for i,xy in zip(indices,predicted):axes[0].text(*xy,str(i),color='cyan',fontsize=9)
    axes[1].scatter(measured[:,0],measured[:,1],facecolors='none',edgecolors='black',s=65,label='Rendered marker centroid')
    axes[1].scatter(predicted[:,0],predicted[:,1],marker='+',color='red',label='Python projection')
    for i,xy in zip(indices,measured):axes[1].text(xy[0]+4,xy[1],str(i))
    axes[1].set_aspect('equal');axes[1].invert_yaxis();axes[1].legend(fontsize=8)
    axes[1].set_title('Independent coordinate calibration\nKnown marker IDs, not photo bead detections')
    for ax in axes:ax.set_xlabel('image x (px)');ax.set_ylabel('image y (px)')
    fig.savefig(out/'projection-check.png',dpi=150);plt.close(fig)
    return dict(rope=asdict(rope),camera=asdict(camera),indices=indices.tolist(),
        projected_xy=predicted.tolist(),marker_centroids=measured.tolist(),marker_areas=areas,
        projection_errors_px=errors.tolist(),supplied_training_indices=indices[train].tolist(),
        withheld_indices=indices[hold].tolist(),registration=fit,
        holdout_errors_px=held_errors.tolist(),wrong_pairing_holdout_errors_px=wrong_errors.tolist(),
        assistance='Known 3-D model/camera and marker correspondences; no inverse bead detection or unknown-camera fitting.',
        marker_scene_sha256=sha(scene),appearance_scene_sha256=sha(beauty),
        marker_image_sha256=sha(markerpng),appearance_image_sha256=sha(beauty.with_suffix('.png')),
        marker_command=command,appearance_command=cmd)


def photo_panel(out):
    cfgpath=ROOT/'photo2/local-pilot-r114.json'
    cfg=json.loads(cfgpath.read_text());imagepath=ROOT/cfg['image']
    im=ImageOps.exif_transpose(Image.open(imagepath)).convert('RGB')
    selected=['B','C','E','F','G','H','J']
    fig,axes=plt.subplots(1,2,figsize=(10,6),layout='constrained')
    x0,y0,x1,y1=cfg['crop']
    for ax in axes:
        ax.imshow(im);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw photo patch')
    axes[1].set_title('Seven proposed body observations\nDots reuse interior samples; NOT physical centers')
    for o in cfg['observations']:
        if o['id'] not in selected:continue
        x,y=o['xy'];axes[1].add_patch(Circle((x,y),3,fill=False,edgecolor='cyan'))
        axes[1].text(x+4,y-3,o['id'],color='white',weight='bold',bbox=dict(facecolor='black',alpha=.5,pad=1))
    fig.savefig(out/'seven-body-patch.png',dpi=160);plt.close(fig)
    return dict(observation_ids=selected,photo_sha256=sha(imagepath),source_config_sha256=sha(cfgpath),
        observations=[o for o in cfg['observations'] if o['id'] in selected],
        deferred=['A','D','I','K','L'],
        status='Assistant-selected body proposals; no new coordinates, physical centers or indices. '
               'I is substantial but closer to the lower edge, so held out of this core set. '
               'Maker R115 confirms D separate from B; other labels remain proposals.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'photo2/output/r117')
    args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    report=dict(source_scene_sha256=sha(ROOT/'beads.pov'),
        placement_python_sha256=sha(ROOT/'photo2/bead_placement.py'),
        checker_sha256=sha(Path(__file__)),parity=parity(out),projection=projection(out),photo=photo_panel(out))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(compared_positions=sum(r['compared'] for r in report['parity']),
        max_position_error=max(r['max_position_error'] for r in report['parity']),
        max_projection_error_px=max(report['projection']['projection_errors_px']),
        max_holdout_error_px=max(report['projection']['holdout_errors_px']),
        wrong_pairing_mean_error_px=float(np.mean(report['projection']['wrong_pairing_holdout_errors_px']))),indent=2))


if __name__=='__main__':main()
