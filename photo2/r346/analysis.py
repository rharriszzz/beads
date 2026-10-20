"""Compare complete-necklace shadows only on visible paper."""
from .shadows import *
from PIL import ImageOps
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r346-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CROPS={
 'right-straight':(2150,2020,2540,2370),
 'right-middle':(2160,1490,2540,1850),
 'top':(970,215,1430,550),
 'bottom-bend':(1260,2820,1740,3182),
 'left-outer':(100,1240,570,1590),
 'inner-bend':(1390,1850,1850,2180),
 'inside-straight':(970,1400,1500,1740),
 'lower-left-bend':(780,2400,1250,2740),
}

def features(row,values,offset=0.):
    distance=np.array(row['distance']);values=np.array(values,dtype=float)
    values=1-(1-values)/(1+offset)
    valid=np.isfinite(values)&(distance>=row['paper_guard']);d=distance[valid];v=values[valid]
    if len(v)<15:return dict(valid=False)
    v=ndi.gaussian_filter1d(v,1.5);candidate=d<=100
    if candidate.sum()<3:return dict(valid=False)
    peak=float(v[candidate].max());index=int(np.argmax(np.where(candidate,v,-np.inf)))
    def trailing(level):
        for j in range(index+1,len(v)-4):
            if np.all(v[j:j+5]<=level):
                return float(np.interp(level,[v[j],v[j-1]],[d[j],d[j-1]]))
        return None
    extent5=trailing(.05) if peak>.05 else 0.;extent10=trailing(.1) if peak>.1 else 0.
    p90=trailing(.9*peak) if peak>.1 else None;p10=trailing(.1*peak) if peak>.1 else None
    near=v[(d>=12)&(d<=20)]
    return dict(valid=True,peak=peak,peak_distance=float(d[index]),extent_5percent_px=extent5,extent_10percent_px=extent10,extent10_censored=bool(peak>.1 and extent10 is None),extent_lower_bound_px=float(d[-1]) if peak>.1 and extent10 is None else None,penumbra_px=p10-p90 if p10 is not None and p90 is not None else None,darkness_12_20=float(np.median(near)) if len(near) else None)

def ratio_images(render_path,clear_path):
    a=linear(rgb(render_path));b=linear(rgb(clear_path))
    assert a.shape==b.shape
    return np.divide(a,b,out=np.ones_like(a),where=b>.001).astype(np.float32)

def illumination_metrics(clear_path):
    from scipy.spatial import cKDTree
    yy,xx=np.mgrid[6:H:24,6:W:24];xy=np.c_[xx.ravel(),yy.ravel()]
    curve=Model(read(ROOT/'photo2/r345/config.json')).image
    xy=xy[cKDTree(curve).query(xy)[0]>260]
    clear=linear(rgb(clear_path));sy,sx=clear.shape[0]/H,clear.shape[1]/W
    points=(xy+.5)*[sx,sy]-.5
    predicted=np.stack([sample(clear[:,:,c],points) for c in range(3)],axis=1);target=background_at(xy)
    relative=predicted/target-1;luma=np.array([.2126,.7152,.0722]);error=(predicted@luma)/(target@luma)-1
    return dict(points=len(xy),median_luminance_relative_error=float(np.median(error)),luminance_relative_rms=float(np.sqrt(np.mean(error**2))),median_rgb_relative_error=np.median(relative,axis=0).tolist(),reference='Smooth photographic background, evaluated only on far-from-necklace grid points; shader paper albedo unchanged.')

def absolute_metrics(ratio,profiles,guard_extra=0.):
    """Same native image coordinates for photo and render, outside BOTH bodies."""
    photo=linear(rgb(ROOT/'beads-photo-2.jpg'));sy,sx=ratio.shape[0]/H,ratio.shape[1]/W
    totals={split:[0.,0.,0] for split in ['fit','validation','all']};rgb_sums=np.zeros(3);rgb_count=0
    source_rgb=[];render_rgb=[];sample_rows=[]
    for r in profiles:
        if not r['eligible']:continue
        d=np.array(r['distance']);d=d[(d>=r['paper_guard']+guard_extra)&(d<=200)];q=np.array(r['point']);t=np.array(r['tangent']);n=np.array(r['outward']);xy=q+np.arange(-18,19,3)[:,None,None]*t+(r['edge_radius']+d)[None,:,None]*n
        outside=sample(paper_distance(),xy)>=4
        baseline=background_at(xy);observed=np.stack([sample(photo[:,:,c],xy) for c in range(3)],axis=-1)/baseline
        pred=np.stack([sample(ratio[:,:,c],(xy+.5)*[sx,sy]-.5) for c in range(3)],axis=-1)
        ok=outside&np.isfinite(observed).all(2)&np.isfinite(pred).all(2)
        weights=baseline*[.2126,.7152,.0722];weights/=weights.sum(2,keepdims=True)
        errors=np.sum(weights*(pred-observed),axis=2)[ok]
        for split in [r['split'],'all']:
            totals[split][0]+=float(np.sum(errors**2));totals[split][1]+=float(np.sum(abs(errors)));totals[split][2]+=len(errors)
        rgb_sums+=np.sum((pred[ok]-observed[ok])**2,axis=0);rgb_count+=int(ok.sum())
        if features(r,r['photo_deficit']).get('peak',0)>=.3:
            near=ok&(d[None,:]<=20)
            if near.any():source_rgb.extend((1-observed[near]).tolist());render_rgb.extend((1-pred[near]).tolist())
        sample_rows.append(dict(id=r['id'],pixels=int(ok.sum()),squared_error=float(np.sum(errors**2)),absolute_error=float(np.sum(abs(errors)))))
    result={split:dict(pixels=v[2],rms=float(np.sqrt(v[0]/v[2])),mae=v[1]/v[2]) for split,v in totals.items()}
    result.update(rgb_rms=np.sqrt(rgb_sums/rgb_count).tolist(),strong_paper_band_photo_rgb_deficit=np.median(source_rgb,axis=0).tolist(),strong_paper_band_render_rgb_deficit=np.median(render_rgb,axis=0).tolist(),guard_extra=guard_extra,regions=sample_rows)
    return result

def panels(images,titles,width=635):
    tiles=[]
    for im,title in zip(images,titles):
        im=im.convert('RGB');height=round(im.height*width/im.width);im=im.resize((width,height),Image.Resampling.LANCZOS);tile=Image.new('RGB',(width,height+40),'#faf7f2');tile.paste(im,(0,40));ImageDraw.Draw(tile).text((12,10),title,font=font(17),fill='#18212b');tiles.append(tile)
    out=Image.new('RGB',(width*len(tiles),max(t.height for t in tiles)),'#faf7f2')
    for i,tile in enumerate(tiles):out.paste(tile,(i*width,0))
    return out

def figures(destination,profiles,baseline,new,base_ratio,new_ratio):
    destination=Path(destination);photo=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');old=Image.open(BASE/'render.png').convert('RGB');fresh=Image.open(destination/'render.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    panels([photo,old,fresh],['Original photograph','R345 lighting','R346: one area key + shared fill']).save(destination/'comparison.jpg',quality=95)
    annotated=photo.copy();d=ImageDraw.Draw(annotated)
    for name,box in CROPS.items():
        d.rectangle(box,outline='white',width=3);d.text((box[0],box[1]-28),name,font=font(21),fill='white',stroke_width=2,stroke_fill='black')
        panels([im.crop(box) for im in [photo,old,fresh]],['Original: silhouette + cast shadow','R345','R346'],550).save(destination/('crop-'+name+'.jpg'),quality=95)
    annotated.resize((1016,1273),Image.Resampling.LANCZOS).save(destination/'crop-locations.jpg',quality=95)
    # Photo is estimated relative to a globally smooth paper reference. Its gray
    # exclusion is a conservative whole-tube band, not invented precise contours.
    yy,xx=np.mgrid[0:796,0:635];xy=np.stack([(xx+.5)*W/635-.5,(yy+.5)*H/796-.5],axis=-1)
    pp=linear(np.asarray(photo.resize((635,796),Image.Resampling.LANCZOS),float)/255);bg=background_at(xy);weights=bg*[.2126,.7152,.0722];weights/=weights.sum(2,keepdims=True);photoD=1-np.sum(weights*pp/bg,axis=2)
    from scipy.spatial import cKDTree
    curve=Model(read(ROOT/'photo2/r345/config.json')).image;tree=cKDTree(curve);distance,index=tree.query(xy.reshape(-1,2));delta=xy.reshape(-1,2)-curve[index];t=unit_local(np.gradient(curve,axis=0)[index]);normal=np.c_[-t[:,1],t[:,0]];signed=np.sum(delta*normal,axis=1)
    # Native arclength fractions interpolate the two conservatively excluded sides.
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];f=arc[index]/arc[-1];st=(np.arange(96)+.5)/96
    radii=[]
    for side in [-1,1]:
        rr=[r for r in profiles if r['side']==side];v=np.array([r['edge_radius']+r['paper_guard'] for r in rr]);radii.append(np.interp(f,np.r_[st[-1]-1,st,st[0]+1],np.r_[v[-1],v,v[0]]))
    exclude=(distance<np.where(signed<0,radii[0],radii[1])).reshape(796,635)
    arrays=[np.ma.array(photoD,mask=exclude)]
    outside=sample(paper_distance(),xy)>=4
    for field in [base_ratio,new_ratio]:
        sy,sx=field.shape[0]/H,field.shape[1]/W;small=np.stack([sample(field[:,:,c],(xy+.5)*[sx,sy]-.5) for c in range(3)],axis=-1);arrays.append(np.ma.array(1-np.sum(weights*small,axis=2),mask=~outside))
    cmap=plt.get_cmap('gray_r').copy();cmap.set_bad('#b4bac0')
    fig,axes=plt.subplots(1,3,figsize=(12,5.4));labels=['Photo / smooth paper estimate','R345: paper-only deficit','R346: paper-only deficit']
    for ax,a,title in zip(axes,arrays,labels):im=ax.imshow(a,cmap=cmap,vmin=0,vmax=.95);ax.set_title(title,fontsize=10);ax.axis('off')
    fig.colorbar(im,ax=axes,fraction=.022,pad=.01,label='Fractional linear-luminance loss');fig.savefig(destination/'shadow-fields.png',dpi=180,bbox_inches='tight');plt.close(fig)
    # Opposing sides at fixed geography, selected without inspecting bead colors.
    selected=[(5,-1),(18,1),(26,1),(36,1),(48,-1),(58,-1),(74,1),(85,-1)]
    fig,axes=plt.subplots(2,4,figsize=(15,6.3),sharex=True,sharey=True)
    for ax,(station,side) in zip(axes.ravel(),selected):
        j=next(i for i,r in enumerate(profiles) if r['station']==station and r['side']==side);r=profiles[j];x=np.array(r['distance']);p=np.array(r['photo_deficit'],float);use=x>=r['paper_guard']
        ax.axvspan(0,r['paper_guard'],color='#dddddd');ax.plot(x[use],p[use],color='black',lw=1.6,label='photo');ax.plot(x[use],baseline[j,use],color='#9c56b8',lw=1.3,label='R345');ax.plot(x[use],new[j,use],color='#05836d',lw=1.5,label='R346');ax.axhline(.10,color='#666666',lw=.7,ls='--');ax.set_title(r['id']+(' (edge uncertain: excluded)' if not r['eligible'] else ''),fontsize=10);ax.set_xlim(0,220);ax.set_ylim(-.12,1);ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8);fig.supxlabel('Native pixels outward from each image’s silhouette estimate (gray band excluded)');fig.supylabel('Paper luminance loss relative to unshadowed paper');fig.tight_layout();fig.savefig(destination/'shadow-profiles.png',dpi=180);plt.close(fig)

def unit_local(v):return v/np.linalg.norm(v,axis=-1,keepdims=True)

def analyze(destination):
    destination=Path(destination);profiles=read(OUT/'profiles.json.gz')['profiles']
    base_ratio=ratio_images(BASE/'render.png',destination/'R345-clear.png');new_ratio=ratio_images(destination/'render.png',destination/'clear.png')
    baseline=rendered_profiles(base_ratio,profiles);new=rendered_profiles(new_ratio,profiles)
    np.savez_compressed(destination/'rendered-profiles.npz',R345=baseline,R346=new)
    data=[]
    for i,row in enumerate(profiles):
        observed=features(row,row['photo_deficit']);old=features(row,baseline[i]);fresh=features(row,new[i]);minus=features(row,row['photo_deficit'],-.03);plus=features(row,row['photo_deficit'],.03)
        data.append(dict(id=row['id'],station=row['station'],point=row['point'],normal=row['outward'],eligible=row['eligible'],split=row['split'],edge_uncertainty=row['edge_uncertainty'],paper_guard=row['paper_guard'],photo=observed,R345=old,R346=fresh,background_minus3percent=minus,background_plus3percent=plus,strong_feature_quality=bool(row['eligible'] and observed.get('peak',0)>=.3 and observed.get('extent_10percent_px') is not None and observed.get('penumbra_px') is not None)))
    save(destination/'shadow-measurements.json',data)
    strong=[r for r in data if r['strong_feature_quality']]
    def summary(group):
        out={}
        for name in ['photo','R345','R346']:
            out[name]={}
            for metric in ['extent_10percent_px','extent_5percent_px','penumbra_px','darkness_12_20']:
                vals=[r[name].get(metric) for r in group if r[name].get(metric) is not None]
                out[name][metric]=dict(n=len(vals),median=float(np.median(vals)) if vals else None,p10=float(np.percentile(vals,10)) if vals else None,p90=float(np.percentile(vals,90)) if vals else None)
        return out
    results=dict(scope='Whole necklace, both sides: camera/2704 transforms/materials/pattern/helicity unchanged. All measurements outside conservative photo band and exact model silhouette. Normalized linear-light paper profiles, never bead color or bead-shadow labels.',eligible_contours=sum(r['eligible'] for r in profiles),total_contours=len(profiles),profile_scores=dict(R345=score(baseline,profiles,False),R346=score(new,profiles,False)),same_pixel_scores=dict(R345=absolute_metrics(base_ratio,profiles),R346=absolute_metrics(new_ratio,profiles)),same_pixel_guard_plus4=dict(R345=absolute_metrics(base_ratio,profiles,4),R346=absolute_metrics(new_ratio,profiles,4)),strong_feature_profiles=len(strong),paired_features=summary(strong),censored_photo_10percent=sum(r['eligible'] and r['photo'].get('extent10_censored',False) for r in data),feature_definition='Strong photographic peak>=30% and both trailing crossings observed; 10% absolute toe is primary; 5% toe is sensitive to background error. Penumbra is sustained90..10% falloff of observed whole-necklace shadow peak, not a single-bead PSF. Distances remain original-photo pixels.',background_sensitivity='Full per-profile features retained for background level +/-3%; these are nuisance sensitivity controls, not confidence intervals.')
    results['unshadowed_paper']=dict(R345=illumination_metrics(destination/'R345-clear.png'),R346=illumination_metrics(destination/'clear.png'))
    save(destination/'comparison-metrics.json',results)
    with (destination/'shadow-measurements.csv').open('w') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['id','eligible','split','x','y','normal_x','normal_y','image','peak_darkness','extent_10percent_px','extent_5percent_px','penumbra_px','darkness_12_20','extent10_censored'])
        for r in data:
            for name in ['photo','R345','R346']:
                m=r[name];writer.writerow([r['id'],r['eligible'],r['split'],*r['point'],*r['normal'],name,*[m.get(key) for key in ['peak','extent_10percent_px','extent_5percent_px','penumbra_px','darkness_12_20','extent10_censored']]])
    figures(destination,profiles,baseline,new,base_ratio,new_ratio)
    save(destination/'provenance.json',dict(source_commit=read(OUT/'measurement-freeze.json')['source_commit'],configuration=read(HERE/'config.json'),input_seal=read(OUT/'input-seal.json'),measurement_freeze=read(OUT/'measurement-freeze.json'),sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(HERE.glob('*.py'))},renderer='POV-Ray3.7.0.10.unofficial',observations_use_bead_colors=False,geometry_pattern_helicity_camera_materials_fixed=True))
    print(json.dumps(results,indent=2))
    return results
