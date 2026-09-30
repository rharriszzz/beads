"""Independent source-macro/POV trigonometry check of the curved ray model."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from check_placement import source_parts,run_pov,vec,ROOT,sha
from local_surface_fit import frame,RADIUS
from curved_surface_fit import ROW,INDICES,PRINCIPAL,trace


def render(p,hand,crop,out,stem,focal=None):
    out.mkdir(parents=True,exist_ok=True)
    x0,y0,x1,y1=crop;w=int(round(x1-x0));h=int(round(y1-y0))
    r,d,eye=frame(p[:7]); mid=np.array([x0+(w-1)/2,y0+(h-1)/2])
    if focal is None:
        base=r*(mid[0]-p[0])/p[2]+d*(mid[1]-p[1])/p[2]
        camera=f'orthographic location {vec(base+100*eye)} direction {vec(-eye)} right {vec(r*w/p[2])} up {vec(-d*h/p[2])}'
    else:
        loc=(PRINCIPAL[0]-p[0])/p[2]*r+(PRINCIPAL[1]-p[1])/p[2]*d+focal/p[2]*eye
        direction=-eye+(mid[0]-PRINCIPAL[0])/focal*r+(mid[1]-PRINCIPAL[1])/focal*d
        camera=f'location {vec(loc)} direction {vec(direction)} right {vec(r*w/focal)} up {vec(-d*h/focal)}'
    _,_,macro=source_parts()
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
        f'camera {{{camera}}}\n#declare bead_radius={RADIUS:.16g};\n'
        '#declare hole_size_per_bead_size=.14;\n'+macro+
        f'\n#declare Row={ROW:.16g}; #declare Q={p[8]:.16g}; #declare K={p[7]:.16g};\n')
    parts=[]
    for label,index in enumerate(INDICES,1):
        parts.append(f'#declare S={int(index)}*Row/Q; #declare A=K*S;\n'
            f'#declare Phi=({p[6]:.16g}+{hand}*360*{int(index)}/Q)*pi/180;\n'
            '#if (abs(K)<1e-12) #declare C=<S,0,0>;\n'
            '#else #declare C=<sin(A)/K,(1-cos(A))/K,0>; #end\n'
            '#declare N=<-sin(A),cos(A),0>;\n'
            'object {bead(material {texture {pigment {rgb <'+str(label)+'/255,0,0>} '
            'finish {ambient 0 emission 1 diffuse 0}}},.8,.7,1) '
            'rotate z*(A*180/pi-90) translate C+4*sin(Phi)*N+<0,0,4*cos(Phi)>}\n')
    scene=out/(stem+'.pov');scene.write_text(header+''.join(parts))
    png,command=run_pov(scene,w,h)
    im=np.asarray(Image.open(png))[:,:,0];labels=np.full(im.shape,-999,int)
    yes=im>0;labels[yes]=INDICES[im[yes]-1]
    return labels,dict(scene_sha256=sha(scene),png_sha256=sha(png),command=command)


def parity(p,hand,crop,out,stem,focal=None):
    actual,provenance=render(p,hand,crop,out,stem,focal)
    x0,y0,x1,y1=map(int,crop);yy,xx=np.mgrid[y0:y1,x0:x1]
    xy=np.column_stack((xx.ravel(),yy.ravel()))
    pred,_,unfinished,_=trace(p,xy,hand,focal=focal)
    wrong=int(np.sum(pred.reshape(actual.shape)!=actual))
    result=dict(parameters=list(p),hand=hand,focal=focal,crop=list(crop),
                mismatches=wrong,pixels=actual.size,mismatch_fraction=wrong/actual.size,
                unfinished_ray_pairs=unfinished,**provenance)
    assert result['mismatch_fraction']<.001,result
    return result,actual


if __name__=='__main__':
    cases=[]
    from curved_surface_fit import NOMINAL_FOCAL
    for i,(hand,k,focal) in enumerate([(1,.018,None),(-1,-.018,None),(1,.018,NOMINAL_FOCAL)]):
        p=[1345,285,8,-8,60,15,10,k,6.5]
        result,_=parity(p,hand,[1170,220,1500,365],ROOT/'photo2/output/r156/parity',f'check-{i}',focal)
        cases.append(result)
    report=dict(cases=cases,source_sha256=sha(ROOT/'beads.pov'),
                kernel_sha256=sha(ROOT/'photo2/curved_surface_fit.py'),checker_sha256=sha(Path(__file__)))
    out=ROOT/'photo2/review/r156';out.mkdir(parents=True,exist_ok=True)
    (out/'parity.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
