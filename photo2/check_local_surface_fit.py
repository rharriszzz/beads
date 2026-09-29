"""Independent POV-Ray checks for the local fitting renderer and inverse fit."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_placement import source_parts,run_pov,vec,ROOT,sha
from local_surface_fit import frame,centers,trace,polygons,RADIUS,INDICES,IDS


def render(p,hand,crop,out,stem):
    out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=crop;w=x1-x0;h=y1-y0
    r,d,eye=frame(p)
    base=r*(x0+(w-1)/2-p[0])/p[2]+d*(y0+(h-1)/2-p[1])/p[2]
    _,_,macro=source_parts()
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
        +f'camera {{orthographic location {vec(base+100*eye)} direction {vec(-eye)} '
        +f'right {vec(r*w/p[2])} up {vec(-d*h/p[2])} }}\n'
        +f'#declare bead_radius={RADIUS:.16g};\n#declare hole_size_per_bead_size=.14;\n'+macro)
    parts=[]
    for label,c in enumerate(centers(p,INDICES,hand),1):
        parts.append('object {bead(material {texture {pigment {rgb <'+str(label)+'/255,0,0>} '
          'finish {ambient 0 emission 1 diffuse 0}}},.8,.7,1) rotate z*90 '
          +f'translate {vec(c)}}}\n')
    scene=out/(stem+'.pov');scene.write_text(header+''.join(parts))
    png,command=run_pov(scene,w,h)
    im=np.asarray(Image.open(png))[:,:,0]
    labels=np.full(im.shape,-999,int)
    yes=im>0;labels[yes]=INDICES[im[yes]-1]
    return labels,dict(scene_sha256=sha(scene),png_sha256=sha(png),command=command)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r126/synthetic')
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text());crop=cfg['crop']
    xy,shape,_=polygons(cfg)
    cases=[]
    for n,(p,hand) in enumerate([([1348,289,8,-4,55,10,5],1),([1348,289,8,9,35,-15,45],-1)]):
        actual,provenance=render(p,hand,crop,out,f'parity-{n}')
        pred,depth,unfinished=trace(p,xy,hand);pred=pred.reshape(shape)
        mismatches=int(np.sum(pred!=actual))
        # Pixel ownership must agree independently, not just total bead area.
        cases.append(dict(parameters=p,hand=hand,mismatches=mismatches,pixels=actual.size,
            mismatch_fraction=mismatches/actual.size,unfinished_ray_pairs=unfinished,**provenance))
        assert mismatches/actual.size<.001,cases[-1]
        if n==0:
            obs={}
            for k,i in cfg['hypotheses']['H1'].items():
                mask=actual==i
                fig,ax=plt.subplots()
                contour=max(ax.contour(mask.astype(float),levels=[.5]).allsegs[0],key=len)
                plt.close(fig)
                obs[k]=(contour[::2]+np.array(crop[:2])).tolist()
            synthetic=dict(cfg,image=None,observations=obs,boundary_uncertainty_px=1.,
                assistance='Supplied exact visible-body regions from independent POV ID rendering, no image detector. Source indices/pose retained only in evaluator truth.',
                evaluator_truth=dict(parameters=p,hand=hand,mapping=cfg['hypotheses']['H1']))
            (out/'synthetic-config.json').write_text(json.dumps(synthetic,indent=2)+'\n')
    report=dict(source_scene_sha256=sha(ROOT/'beads.pov'),fitter_sha256=sha(ROOT/'photo2/local_surface_fit.py'),
        checker_sha256=sha(Path(__file__)),cases=cases)
    (out/'ray-parity.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
