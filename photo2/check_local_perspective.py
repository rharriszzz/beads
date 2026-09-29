"""R128 close-camera sensitivity; unknown intrinsics are diagnostic hypotheses."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares,minimize
from PIL import Image,ExifTags
from local_surface_fit import ROOT,IDS,INDICES,RADIUS,frame,centers,polygons,outward
from check_placement import source_parts,run_pov,vec,sha
from review_local_surface_fit import best_by_chart,measure

OUT=ROOT/'photo2/output/r126/perspective'


def project(p,xyz,focal,principal):
    r,d,eye=frame(p)
    numerator=p[2]*np.column_stack((xyz@r,xyz@d))+p[:2]-principal
    return principal+numerator/(1-p[2]*(xyz@eye)/focal)[:,None]


def anchors(p,indices,hand,focal,principal):
    c=centers(p,indices,hand);c[:,1:]*=(4+RADIUS)/4
    return project(p,c,focal,principal)


def trace(p,xy,hand,focal,principal,eps=1e-4):
    r,d,eye=frame(p)
    base=(xy[:,0,None]-p[0])/p[2]*r+(xy[:,1,None]-p[1])/p[2]*d
    rays=eye-(xy[:,0,None]-principal[0])/focal*r-(xy[:,1,None]-principal[1])/focal*d
    rays/=np.linalg.norm(rays,axis=1)[:,None]
    delta=base[:,None,:]-centers(p,INDICES,hand)[None,:,:]
    middle=-np.einsum('ijk,ik->ij',delta,rays)
    perp2=np.sum(delta*delta,axis=2)-middle*middle
    bound=RADIUS*np.sqrt(1+.7**2)
    a,b=np.where(perp2<bound**2)
    half=np.sqrt(np.maximum(0,bound**2-perp2[a,b]))
    depth=middle[a,b]+half;end=middle[a,b]-half
    localbase=delta[a,b];ray=rays[a]
    alive=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
    major=.57*RADIUS;minor=.43*RADIUS;rounding=.8*minor;extra=.2*minor;stretch=.7/.43
    for _ in range(400):
        active=np.flatnonzero(alive)
        if not len(active):break
        v=localbase[active]+depth[active,None]*ray[active]
        qr=np.abs(np.hypot(v[:,1],v[:,2])-major)-extra
        qa=np.abs(v[:,0])/stretch-extra
        sdf=np.hypot(np.maximum(qr,0),np.maximum(qa,0))+np.minimum(np.maximum(qr,qa),0)-rounding
        reached=sdf<eps;hit[active[reached]]=True;alive[active[reached]]=False
        moving=active[~reached];depth[moving]-=np.maximum(sdf[~reached],eps)
        alive[moving[depth[moving]<end[moving]]]=False
    best=np.full(len(xy),-np.inf);np.maximum.at(best,a[hit],depth[hit])
    labels=np.full(len(xy),-999,int);front=hit&(depth>=best[a]-eps/2)
    labels[a[front]]=INDICES[b[front]]
    return labels,int(alive.sum())


def render(p,hand,crop,focal,principal,out,stem):
    x0,y0,x1,y1=crop;w=x1-x0;h=y1-y0;r,d,eye=frame(p)
    camera=focal/p[2]*eye-(p[0]-principal[0])/p[2]*r-(p[1]-principal[1])/p[2]*d
    direction=-eye+(x0+(w-1)/2-principal[0])/focal*r+(y0+(h-1)/2-principal[1])/focal*d
    _,_,macro=source_parts()
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
        +f'camera {{perspective location {vec(camera)} direction {vec(direction)} '
        +f'right {vec(r*w/focal)} up {vec(-d*h/focal)} }}\n'
        +f'#declare bead_radius={RADIUS:.16g};\n#declare hole_size_per_bead_size=.14;\n'+macro)
    objects=[]
    for label,c in enumerate(centers(p,INDICES,hand),1):
        objects.append('object {bead(material {texture {pigment {rgb <'+str(label)+'/255,0,0>} '
          'finish {ambient 0 emission 1 diffuse 0}}},.8,.7,1) rotate z*90 '+f'translate {vec(c)}}}\n')
    scene=out/(stem+'.pov');scene.write_text(header+''.join(objects));png,command=run_pov(scene,w,h)
    red=np.asarray(Image.open(png))[:,:,0];labels=np.full(red.shape,-999,int);yes=red>0;labels[yes]=INDICES[red[yes]-1]
    return labels,dict(scene_sha256=sha(scene),png_sha256=sha(png),command=command)


def fit(f,cfg,focal,principal):
    p0=np.array(f['parameters']);free=np.array([0,1,2,3,5,6]);train=[k for k in IDS if k!=cfg['held_out']]
    idx=[f['mapping'][k] for k in train];target=outward(p0,idx,f['hand'])
    def unpack(v):
        p=p0.copy();p[free]=v;return p
    lo=p0-np.array([25,25,3,25,0,30,70]);hi=p0+np.array([25,25,3,25,0,30,70])
    coarse=least_squares(lambda v:(anchors(unpack(v),idx,f['hand'],focal,principal)-target).ravel(),p0[free],bounds=(lo[free],hi[free]),max_nfev=150)
    xy,shape,masks=polygons(cfg,spacing=2)
    def loss(v):
        labels,_=trace(unpack(v),xy,f['hand'],focal,principal)
        scores=measure(labels.reshape(shape),masks,f['mapping'],cfg['boundary_uncertainty_px']/2)
        return np.mean([scores[k]['region_loss'] for k in train])
    refined=minimize(loss,coarse.x,method='Powell',bounds=list(zip(lo[free],hi[free])),
                     options={'maxfev':550,'maxiter':20,'xtol':.01,'ftol':.001})
    # Same full-pixel final objective as the orthographic comparison.
    xy,shape,masks=polygons(cfg,spacing=1)
    def fine_loss(v):
        labels,_=trace(unpack(v),xy,f['hand'],focal,principal)
        scores=measure(labels.reshape(shape),masks,f['mapping'],cfg['boundary_uncertainty_px'])
        return np.mean([scores[k]['region_loss'] for k in train])
    widths=np.array([5,5,1,8,8,12])
    bounds=list(zip(np.maximum(lo[free],refined.x-widths),np.minimum(hi[free],refined.x+widths)))
    fine=minimize(fine_loss,refined.x,method='Powell',bounds=bounds,
                  options={'maxfev':650,'maxiter':20,'xtol':.005,'ftol':.0001})
    return unpack(fine.x),float(fine.fun),int(refined.nfev+fine.nfev),bool(fine.success)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    photo=Image.open(ROOT/cfg['image']);exif=photo.getexif();details={}
    allowed={'FocalLength','FocalLengthIn35mmFilm','DigitalZoomRatio','LensModel','SubjectDistance'}
    for key,value in exif.get_ifd(34665).items():
        name=ExifTags.TAGS.get(key,str(key))
        if name in allowed:details[name]=str(value)
    w,h=photo.size;principal=np.array([(w-1)/2,(h-1)/2])
    nominal=float(exif.get_ifd(34665)[41989])*np.hypot(w,h)/np.hypot(36,24)
    results=[];fits=best_by_chart(json.loads((ROOT/'photo2/output/r126/final/fits.json').read_text()))
    xy,shape,masks=polygons(cfg)
    for ratio in [.5,1.,2.]:
      for f in fits:
        focal=nominal*ratio;p,loss,neval,success=fit(f,cfg,focal,principal)
        labels,unfinished=trace(p,xy,f['hand'],focal,principal);labels=labels.reshape(shape)
        independent,provenance=render(p,f['hand'],cfg['crop'],focal,principal,OUT,f"{f['hypothesis']}-{ratio}")
        mismatch=int((labels!=independent).sum());assert mismatch/labels.size<.001,mismatch
        rows=measure(independent,masks,f['mapping'],cfg['boundary_uncertainty_px'])
        train=[k for k in IDS if k!=cfg['held_out']]
        result=dict(hypothesis=f['hypothesis'],hand=f['hand'],mapping=f['mapping'],focal_px=focal,
            focal_ratio=ratio,parameters=p.tolist(),training_mean_iou=float(np.mean([rows[k]['iou'] for k in train])),
            training_region_loss=float(np.mean([rows[k]['region_loss'] for k in train])),
            held_out_iou=rows[cfg['held_out']]['iou'],metrics=rows,ray_pov_mismatches=mismatch,
            ray_pairs_unfinished=unfinished,evaluations=neval,optimizer_success=success,render_provenance=provenance)
        results.append(result);print(json.dumps({k:result[k] for k in ['hypothesis','focal_ratio','training_region_loss','held_out_iou','optimizer_success']}),flush=True)
        report=dict(metadata=details,image_dimensions=[w,h],principal_xy=principal.tolist(),nominal_focal_px=nominal,
            assumptions='Principal point at image center; nominal focal converts 51mm equivalent using image and 35mm-frame diagonals. Crop/calibration unknown. 0.5x/1x/2x are sensitivity scenarios, not measured intrinsics. Distance is not recovered. Local camera/phase gauge is fixed as before.',
            results=results,code_sha256=sha(Path(__file__)),source_image_sha256=sha(ROOT/cfg['image']),
            config_sha256=sha(ROOT/'photo2/local-fit-r126.json'),orthographic_fits_sha256=sha(ROOT/'photo2/output/r126/final/fits.json'))
        (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
