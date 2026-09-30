"""R175: minor-outward points and tangent-plane circles on a planar spline rope.

Forward geometry uses the beads.pov rounded annulus, then explicit model exposure
tests. Small photo registration is diagnostic and manually assisted; fitted
interior points are not measured physical centers or outward anchors.
"""
import argparse,json,os
from pathlib import Path
from dataclasses import dataclass
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-tangent-mpl')
import numpy as np
from scipy.interpolate import splprep,splev
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
from PIL import Image,ImageOps,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as Polygon
from bead_placement import Rope
from local_surface_fit import frame
from curved_surface_fit import sdf
from check_placement import source_parts,run_pov,vec,sha

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'photo2/spline-seed-r175.json'
RADIUS=Rope(2698).bead_radius
ROW=.65*2*RADIUS*1.05


@dataclass
class View:
    elevation: float=80.
    roll: float=0.
    tx: float=1269.5
    ty: float=1590.5
    scale: float=1.

    def basis(self):return frame([self.tx,self.ty,self.scale,self.roll,self.elevation,0.,0.])

    def project(self,xyz):
        r,d,eye=self.basis()
        return np.column_stack((np.asarray(xyz)@r,np.asarray(xyz)@d))*self.scale+[self.tx,self.ty]

    def base(self,xy):
        r,d,eye=self.basis();xy=np.asarray(xy)
        return (xy[:,0,None]-self.tx)/self.scale*r+(xy[:,1,None]-self.ty)/self.scale*d


class SplineRope:
    """One planar periodic spline; arc spacing/closure follow the literal source.

    The inverse camera maps the image seed to the paper plane. Derive scale so
    its model arc length equals ROW*nrows; N remains a configurable hypothesis.
    """
    def __init__(self,points,view,nbeads=2698,hand=1,phase=0.,origin_fraction=0.,smoothing=2.):
        self.source=Rope(nbeads,helicity=hand);self.view=view;self.phase=phase;self.origin=origin_fraction
        points=np.asarray(points,float)
        if len(points)<4 or not np.isfinite(points).all():raise ValueError('At least four finite spline points required')
        if not 1<=view.elevation<=89.9:raise ValueError('Elevation must be between1 and89.9 degrees')
        if np.linalg.norm(points[0]-points[-1])<1e-6:points=points[:-1]
        area=np.sum(points[:,0]*np.roll(points[:,1],-1)-points[:,1]*np.roll(points[:,0],-1))
        if area<0:points=points[::-1]
        points=np.vstack((points,points[0]))
        self.tck,_=splprep(points.T,s=len(points)*smoothing**2,per=True,k=3)
        u=np.linspace(0,1,8193)
        image=np.array(splev(u,self.tck)).T
        r,d,eye=view.basis();matrix=np.array([r[:2],d[:2]])
        self.inverse=np.linalg.inv(matrix)
        plane=(image-[view.tx,view.ty])@self.inverse.T
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
        self.unscaled_length=arc[-1];view.scale=arc[-1]/(ROW*self.source.nrows)
        self.arc_fraction=arc/arc[-1];self.u_table=u
        self.length=ROW*self.source.nrows
        self.seed_image_curve=image

    def geometry(self,indices):
        indices=np.atleast_1d(indices).astype(float)
        fraction=(indices/self.source.nbeads+self.origin)%1.
        u=np.interp(fraction,self.arc_fraction,self.u_table)
        image=np.array(splev(u,self.tck)).T
        plane=(image-[self.view.tx,self.view.ty])@self.inverse.T/self.view.scale
        line=np.column_stack((plane,np.zeros(len(indices))))
        deriv=np.array(splev(u,self.tck,der=1)).T@self.inverse.T
        tangent=np.column_stack((deriv/np.linalg.norm(deriv,axis=1)[:,None],np.zeros(len(indices))))
        normal=np.column_stack((-tangent[:,1],tangent[:,0],np.zeros(len(indices))))
        angle=np.radians(self.phase+self.source.helicity*360*self.source.nrows*indices/self.source.nbeads)
        radial=np.sin(angle)[:,None]*normal;radial[:,2]=np.cos(angle)
        centers=line+4*radial;outer=line+(4+RADIUS)*radial
        return dict(indices=indices.astype(int),line=line,tangent=tangent,normal=normal,
                    radial=radial,centers=centers,outward=outer)

    def nearest_fraction(self,xy):
        k=int(np.argmin(np.linalg.norm(self.seed_image_curve-np.asarray(xy),axis=1)))
        return float(self.arc_fraction[k])


def tangent_circles(geometry,radius=.18*RADIUS,samples=48):
    if radius<=0 or samples<8:raise ValueError('Positive circle radius and at least8 samples required')
    a=geometry['tangent'];normal=geometry['radial'];b=np.cross(normal,a)
    angle=np.linspace(0,2*np.pi,samples+1)
    circles=geometry['outward'][:,None,:]+radius*(np.cos(angle)[None,:,None]*a[:,None,:]+np.sin(angle)[None,:,None]*b[:,None,:])
    plane_offset=np.sum(normal*geometry['outward'],axis=1)
    return circles,plane_offset


def first_hits(model,xy,geometry=None,eps=1e-5):
    """Orthographic exact annulus ray marching, including all hidden occluders.

    Screen-space conservative sphere culling avoids allocating a full N-by-N
    array. Nonconverged ray pairs remain explicit and never verify exposure.
    """
    if geometry is None:geometry=model.geometry(np.arange(model.source.nbeads))
    centers=geometry['centers'];t=geometry['tangent'];n=geometry['normal'];view=model.view
    xy=np.asarray(xy,float);base=view.base(xy);eye=view.basis()[2]
    bound=RADIUS*np.sqrt(1+.7**2);tree=cKDTree(view.project(centers))
    candidates=tree.query_ball_point(xy,bound*view.scale+1e-5)
    a=np.repeat(np.arange(len(xy)),[len(v) for v in candidates]);b=np.array([j for v in candidates for j in v],int)
    best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);uncertain=np.zeros(len(xy),int)
    if not len(a):return owner,best,uncertain
    delta=base[a]-centers[b];middle=-delta@eye
    perp2=np.sum(delta*delta,axis=1)-middle**2
    keep=perp2<bound**2;a=a[keep];b=b[keep];delta=delta[keep];middle=middle[keep];perp2=perp2[keep]
    half=np.sqrt(np.maximum(0,bound**2-perp2));depth=middle+half;end=middle-half
    local=np.column_stack((np.sum(delta*t[b],axis=1),np.sum(delta*n[b],axis=1),delta[:,2]))
    direction=np.column_stack((t[b]@eye,n[b]@eye,np.full(len(b),eye[2])))
    alive=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
    for _ in range(600):
        active=np.flatnonzero(alive)
        if not len(active):break
        distance=sdf(local[active]+depth[active,None]*direction[active])
        reached=distance<eps;hit[active[reached]]=True;alive[active[reached]]=False
        moving=active[~reached];depth[moving]-=np.maximum(distance[~reached],eps)
        alive[moving[depth[moving]<end[moving]]]=False
    np.add.at(uncertain,a[alive],1);np.maximum.at(best,a[hit],depth[hit])
    front=hit&(depth>=best[a]-eps/2);owner[a[front]]=geometry['indices'][b[front]]
    return owner,best,uncertain


def visible_anchors(model,geometry=None,facing_margin=.12):
    if geometry is None:geometry=model.geometry(np.arange(model.source.nbeads))
    xy=model.view.project(geometry['outward']);owner,front,unfinished=first_hits(model,xy,geometry)
    depth=geometry['outward']@model.view.basis()[2]
    gap=front-depth;facing=geometry['radial']@model.view.basis()[2]
    exposed=(owner==geometry['indices'])&(np.abs(gap)<.002)&(unfinished==0)&(facing>facing_margin)
    return dict(xy=xy,exposed=exposed,first_owner=owner,front_minus_anchor=gap,
                facing=facing,unfinished_pairs_per_ray=unfinished)


def load_model(config,parameters):
    path=Path(config['spline']);path=path if path.is_absolute() else ROOT/path
    seed=json.loads(path.read_text())
    view=View(elevation=parameters['elevation'],roll=parameters.get('roll',0.))
    return SplineRope(seed['points'],view,parameters['nbeads'],parameters['hand'],parameters['phase'],
                      parameters['origin_fraction'],seed['smoothing_rms_target_pixels'])


def draw_circles(ax,model,geometry,visibility,circle_radius,transform=None):
    curves,_=tangent_circles(geometry,circle_radius)
    for i in np.flatnonzero(visibility['exposed']):
        xy=model.view.project(curves[i])
        if transform is not None:xy=(xy+.5)*transform-.5
        ax.plot(xy[:,0],xy[:,1],color='cyan',lw=.75)


def render_model(model,out,size=(1000,1253),name='unmatched',circle_radius=.18*RADIUS):
    parameters,_,macro=source_parts();geometry=model.geometry(np.arange(model.source.nbeads))
    width,height=size;r,d,eye=model.view.basis();source_size=np.array([2540,3182])
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'+
        'camera {orthographic location '+vec(eye*10000)+' direction '+vec(-eye)+
        ' right '+vec(r*source_size[0]/model.view.scale)+' up '+vec(-d*source_size[1]/model.view.scale)+'}\n')
    body=(f'#declare nbeads={model.source.nbeads};\n#declare beads_per_row=6.5;\n'+parameters+
          '#declare hole_size_per_bead_size=.14;\n'+macro)
    objects=''
    for i,(center,tangent) in enumerate(zip(geometry['centers'],geometry['tangent'])):
        angle=np.degrees(np.arctan2(tangent[1],tangent[0]))-90
        objects+=f'object{{ bead(m,.8,.7,1) rotate z*{angle:.12g} translate {vec(center)} }}\n'
    scene=out/(name+'.pov')
    scene.write_text(header+body+'background{rgb 1}\n'+
        'light_source{'+vec(eye*1000+np.array([-300,-100,300]))+' rgb 1.5}\n'+
        '#declare m=material{texture{pigment{rgb<.45,.45,.45>} finish{ambient .2 diffuse .7 phong .4}}};\n'+objects)
    png,command=run_pov(scene,width,height)
    # Independent first-hit ownership checker on the same source macro.
    ids=''
    for i,(center,tangent) in enumerate(zip(geometry['centers'],geometry['tangent'])):
        angle=np.degrees(np.arctan2(tangent[1],tangent[0]))-90;code=i+1
        ids+=f'#declare m=material{{texture{{pigment{{rgb<{code%256}/255,{code//256}/255,0>}} finish{{ambient 0 emission 1 diffuse 0}}}}}};\n'
        ids+=f'object{{bead(m,.8,.7,1) rotate z*{angle:.12g} translate {vec(center)}}}\n'
    idscene=out/(name+'-ids.pov');idscene.write_text(header+body+ids)
    idpng,idcommand=run_pov(idscene,width,height)
    vis=visible_anchors(model,geometry);encoded=np.array(Image.open(idpng).convert('RGB')).astype(int)
    labels=encoded[:,:,0]+256*encoded[:,:,1]-1;factor=np.array(size)/source_size
    xy=(vis['xy']+.5)*factor-.5;rounded=np.round(xy).astype(int)
    inside=(rounded[:,0]>=0)&(rounded[:,0]<width)&(rounded[:,1]>=0)&(rounded[:,1]<height)
    use=vis['exposed']&inside;predicted=geometry['indices'][use];actual=labels[rounded[use,1],rounded[use,0]]
    agreement=int(np.sum(actual==predicted));total=int(use.sum())
    # Compare exactly the same pixel ray, separately from rounding an exposed
    # mathematical point onto a finite preview pixel near a bead edge.
    pixels=rounded[inside];source_xy=(pixels+.5)/factor-.5
    pixel_owner,_,pixel_unfinished=first_hits(model,source_xy,geometry)
    pixel_actual=labels[pixels[:,1],pixels[:,0]];verified=pixel_unfinished==0
    pixel_mismatch=int(np.sum((pixel_owner!=pixel_actual)&verified))
    assert pixel_mismatch<=max(1,int(verified.sum()*.001)),(pixel_mismatch,int(verified.sum()))
    fig,ax=plt.subplots(figsize=(8,10),constrained_layout=True);ax.imshow(Image.open(png))
    draw_circles(ax,model,geometry,vis,circle_radius,factor)
    ax.set_title('Unmatched spline model: exposed outward points and tangent circles');ax.axis('off')
    fig.savefig(out/'model-only.png',dpi=160);plt.close(fig)
    return dict(visible_anchors=int(vis['exposed'].sum()),unfinished_rays=int(np.sum(vis['unfinished_pairs_per_ray']>0)),
        independent_same_ray_check=dict(verified_rays=int(verified.sum()),mismatches=pixel_mismatch,
            unverified_rays=int((~verified).sum())),
        independent_pov_pixel_check=dict(agree=agreement,total=total,mismatch_indices=predicted[actual!=predicted].tolist(),
            interpretation='Rounded preview pixels can differ at grazing boundaries; point ray exposure is tested in continuous model coordinates.'),
        appearance_command=command,id_command=idcommand,appearance_scene_sha256=sha(scene),id_scene_sha256=sha(idscene))


def fit_patch(config):
    """Three manually established colored interiors, no black/held-group fitting.

    Centroids initialize proposals only. Keep every chart/hand candidate; final
    ranking uses outward-point distance to those positive interior polygons and
    exposure. No centroid is promoted to a measured outward point.
    """
    core_path=Path(config['cores']);core_path=core_path if core_path.is_absolute() else ROOT/core_path
    cores=json.loads(core_path.read_text());numbers=[8,11,20]
    polygons={n:np.array(next(v for v in cores['results'] if v['number']==n)['loop_xy']) for n in numbers}
    targets=np.array([polygons[n].mean(axis=0) for n in numbers]);candidates=[]
    mappings=json.loads((ROOT/'photo2/review/r160/report.json').read_text())['mappings']
    for family,hand in [('A',1),('A',-1),('B',1),('B',-1)]:
      if hand not in config.get('fit_hands',[-1,1]):continue
      indices=np.array([mappings[family][n-1] for n in numbers])
      for elevation in config.get('fit_elevations',[65.,80.,89.]):
        params=dict(config['parameters'],hand=hand,elevation=elevation,phase=0.)
        model=load_model(config,params);origin=model.nearest_fraction(targets[-1])
        span=45/model.unscaled_length
        for phase in np.arange(-180,180,45):
            def unpack(v):
                model.origin=float(v[0]);model.phase=float(v[1])
                return model.geometry(indices)
            fit=least_squares(lambda v:(model.view.project(unpack(v)['outward'])-targets).ravel(),
                [origin,float(phase)],bounds=([origin-span,phase-80],[origin+span,phase+80]),max_nfev=80)
            g=unpack(fit.x);xy=model.view.project(g['outward'])
            # Exact first-hit test against the complete spline, not only the fit beads.
            owner,front,unfinished=first_hits(model,xy)
            depth=g['outward']@model.view.basis()[2]
            exposed=(owner==indices%model.source.nbeads)&(np.abs(front-depth)<.002)&(unfinished==0)&(g['radial']@model.view.basis()[2]>.12)
            distances=[];inside=[]
            for n,q in zip(numbers,xy):
                poly=polygons[n];segments=np.roll(poly,-1,axis=0)-poly
                frac=np.clip(np.sum((q-poly)*segments,axis=1)/np.maximum(np.sum(segments**2,axis=1),1e-12),0,1)
                distance=np.min(np.linalg.norm(poly+frac[:,None]*segments-q,axis=1))
                yes=bool(Polygon(poly).contains_point(q));inside.append(yes);distances.append(0. if yes else float(distance))
            score=float(np.mean(np.square(distances)))+100*int(np.sum(~exposed))
            fitted=dict(params,phase=float(fit.x[1]),origin_fraction=float(fit.x[0]%1))
            candidates.append(dict(family=family,parameters=fitted,training_numbers=numbers,
                relative_indices=indices.tolist(),outward_xy=xy.tolist(),inside_confirmed_interiors=inside,
                exposed=exposed.tolist(),distance_to_confirmed_interiors=distances,score=score,
                centroid_proposal_rms=float(np.sqrt(np.mean(fit.fun**2))),converged=bool(fit.success)))
    candidates.sort(key=lambda v:(v['score'],v['centroid_proposal_rms']))
    return candidates,mappings


def overlays(config,model,out,family,mappings=None):
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    g=model.geometry(np.arange(model.source.nbeads));vis=visible_anchors(model,g)
    circles,offset=tangent_circles(g,config['circle_radius'])
    # Preserve full original resolution and pixel coordinates for later zooming.
    overlay=image.copy();draw=ImageDraw.Draw(overlay)
    for i in np.flatnonzero(vis['exposed']):
        xy=model.view.project(circles[i]);draw.line([tuple(v) for v in xy],fill=(0,255,255),width=1)
    overlay.save(out/'bracelet-overlay.png')
    fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    for ax,title in zip(axes,['Raw nearby colored beads','Cyan circles after three-interior registration']):
        ax.imshow(image);ax.set_xlim(1210,1450);ax.set_ylim(365,210);ax.axis('off');ax.set_title(title,fontsize=10)
    draw_circles(axes[1],model,g,vis,config['circle_radius'])
    doc=json.loads((ROOT/'photo2/manual-labels-r169.json').read_text())
    for n in (8,11,16,20):
        a=next(a for a in doc['annotations'] if a['number']==n)
        axes[0].text(a['x']+3,a['y']+4,str(n),color='white',fontsize=10,bbox=dict(facecolor='black',alpha=.6,pad=.2))
    checks=[]
    if mappings:
      for n in (8,11,14,16,17,20):
        index=int(mappings[family][n-1])%model.source.nbeads;xy=vis['xy'][index]
        checks.append(dict(maker_number=n,model_index=index,relative_index=mappings[family][n-1],outward_xy=xy.tolist(),exposed=bool(vis['exposed'][index])))
        if n in (8,11,16,20) and vis['exposed'][index]:
            axes[1].annotate(str(n),xy,xytext=(xy[0]+7,xy[1]-8),color='cyan',fontsize=10,
                bbox=dict(facecolor='black',alpha=.65,pad=.3),arrowprops=dict(arrowstyle='->',color='cyan',lw=.8))
    fig.savefig(out/'patch-overlay.png',dpi=180);plt.close(fig)
    np.savez_compressed(out/'geometry.npz',**g,circles=circles,tangent_plane_offset=offset,
                        projected_outward=vis['xy'],visible=vis['exposed'])
    return dict(visible_anchors=int(vis['exposed'].sum()),excluded_hidden_or_grazing=int((~vis['exposed']).sum()),
        unfinished_rays=int(np.sum(vis['unfinished_pairs_per_ray']>0)),local_checks=checks)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['model','fit','overlay'],default='model')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r175/model')
    parser.add_argument('--parameters',type=Path,help='Saved adjustable registration JSON for overlay stage')
    parser.add_argument('--nbeads',type=int);parser.add_argument('--hand',type=int,choices=[-1,1])
    parser.add_argument('--phase',type=float);parser.add_argument('--elevation',type=float)
    parser.add_argument('--circle-radius',type=float,help='Marker radius in beads.pov model units')
    parser.add_argument('--origin-shift-px',type=float,default=0.)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    cfg=dict(spline='photo2/spline-seed-r175.json',cores='photo2/review/r157/report.json',circle_radius=.18*RADIUS,
        parameters=dict(nbeads=2698,hand=1,elevation=80.,roll=0.,phase=0.,origin_fraction=0.))
    if args.parameters:cfg.update(json.loads(args.parameters.read_text()))
    for key in ['nbeads','hand','phase','elevation']:
        if getattr(args,key) is not None:cfg['parameters'][key]=getattr(args,key)
    if args.circle_radius is not None:cfg['circle_radius']=args.circle_radius
    if cfg['circle_radius']<=0:parser.error('--circle-radius must be positive')
    if args.elevation is not None:cfg['fit_elevations']=[args.elevation]
    if args.hand is not None:cfg['fit_hands']=[args.hand]
    model=load_model(cfg,cfg['parameters']);cfg['parameters']['origin_fraction']+=args.origin_shift_px/model.unscaled_length
    model=load_model(cfg,cfg['parameters'])
    report=dict(request='R175',stage=args.stage,parameters=cfg['parameters'],scale_pixels_per_unit=model.view.scale,
        nrows=model.source.nrows,exact_beads_per_row=model.source.exact_beads_per_row,
        model_arc_length=model.length,source_image_arc_seed_status='Historical approximate centerline; user-authorized diagnostic reuse',
        definition='Outer-wall midpoint at maximum minor-radial extent; tangent plane normal is minor radial vector',
        circle_radius_model_units=cfg['circle_radius'],facing_margin=.12,
        limits='Diagnostic geometry/registration, not recovered photo N, camera elevation, helicity or full-string correspondences',
        source_sha256={p:sha(ROOT/p) for p in ['beads-photo-2.jpg','beads.pov','photo2/tangent_circles.py','photo2/bead_placement.py',
            'photo2/curved_surface_fit.py','photo2/local_surface_fit.py','photo2/check_placement.py','photo2/spline-seed-r175.json','photo2/review/r157/report.json',
            'photo2/review/r160/report.json','photo2/manual-labels-r169.json']})
    if args.stage=='model':report['model_check']=render_model(model,args.output,circle_radius=cfg['circle_radius'])
    elif args.stage=='fit':
        candidates,mappings=fit_patch(cfg);best=candidates[0];cfg['parameters']=best['parameters'];cfg['family']=best['family']
        model=load_model(cfg,cfg['parameters']);report.update(parameters=cfg['parameters'],candidates=candidates,selected=best,
            scale_pixels_per_unit=model.view.scale,family=best['family'],training_numbers=[8,11,20],held_group_not_used=[22,23,24,25])
        report['overlay']=overlays(cfg,model,args.output,best['family'],mappings)
    else:
        mappings=json.loads((ROOT/'photo2/review/r160/report.json').read_text())['mappings']
        report['overlay']=overlays(cfg,model,args.output,cfg.get('family','A'),mappings)
    if args.stage=='model':
        g=model.geometry(np.arange(model.source.nbeads));vis=visible_anchors(model,g)
        circles,offset=tangent_circles(g,cfg['circle_radius'])
        np.savez_compressed(args.output/'geometry.npz',**g,circles=circles,tangent_plane_offset=offset,
                            projected_outward=vis['xy'],visible=vis['exposed'])
    (args.output/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    compact={k:report[k] for k in ['stage','parameters','scale_pixels_per_unit']}
    if 'model_check' in report:compact['model_check']={k:v for k,v in report['model_check'].items() if k in ['visible_anchors','unfinished_rays','independent_same_ray_check']}
    for key in ['overlay','selected']:
        if key in report:compact[key]=report[key]
    print(json.dumps(compact,indent=2),flush=True)


if __name__=='__main__':main()
