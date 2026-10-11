"""Photo-only reflection evidence and matched global lighting experiments (R257)."""
from __future__ import annotations
import argparse, json, csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import label, gaussian_filter, binary_dilation
from scipy.optimize import least_squares
from .generate import ROOT,sha,save
from .surface import Scene,unit,moments,shade,highlight,directions

OUT=ROOT/'photo2/review/r257'

def photo():return np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
def linear(rgb):
    a=np.asarray(rgb)/255.;return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)

def observations(inventory,rgb):
    result=[];white=linear(rgb).min(axis=2)
    for r in inventory['observations']:
        if r['evidence_class']!='black-candidate':continue
        x,y=int(r['x']),int(r['y']);a=white[y-12:y+13,x-12:x+13];base=float(np.percentile(a,30));peak=float(a[12,12]);threshold=base+.5*(peak-base)
        lab,_=label(a>threshold);mask=lab==lab[12,12]
        if not lab[12,12]:mask[:]=False
        yy,xx=np.where(mask);xy=np.c_[xx+x-12,yy+y-12];w=a[mask]-base;m=moments(xy,w)
        reliable=bool(m and 3<=len(xy)<=90 and r['dark_annulus_fraction']>=.55 and r['reflection_contrast']>=.35 and not np.any((xx==0)|(xx==24)|(yy==0)|(yy==24)))
        sector=int((np.arctan2(y-1590.5,x-1269.5)%(2*np.pi))/(2*np.pi)*8)
        result.append(dict(id=r['id'],seed_xy=[x,y],xy=m['centroid'] if m else [x,y],shape=m,area_px2=len(xy),patch=xy.tolist(),
                           intensity=w.tolist(),dark_surround=r['dark_annulus_fraction'],contrast=r['reflection_contrast'],
                           reliable_candidate=reliable,sector=sector,split='test' if sector in [1,4,6] else 'train',
                           evidence='Connected half-contrast neutral brightness on dark surround; unconfirmed specular candidate; no bead IDs used',
                           uncertainty_px=1.5 if reliable else 3.))
    return result


def shadow_observations(rgb,scene):
    """Paper chromaticity learned from border, local upper-envelope illumination.

    Excludes chromatic/dark bodies; residual darkness remains a candidate shadow,
    never ownership evidence. Border-derived color is input-specific, not magenta.
    """
    small=linear(rgb[::8,::8]);lum=small@np.array([.2126,.7152,.0722]);ch=small/np.maximum(small.sum(2,keepdims=True),1e-8)
    border=np.concatenate([ch[:12].reshape(-1,3),ch[-12:].reshape(-1,3),ch[:,:12].reshape(-1,3),ch[:,-12:].reshape(-1,3)])
    ref=np.median(border,axis=0);dist=np.linalg.norm(ch-ref,axis=2);paper=(dist<.055)&(lum>.035)
    # Weighted local average followed by broad upper envelope limits bead leakage.
    from scipy.ndimage import maximum_filter
    bg=gaussian_filter(np.where(paper,lum,0),8)/np.maximum(gaussian_filter(paper.astype(float),8),1e-5)
    bg=maximum_filter(bg,size=19);deficit=np.clip(1-lum/np.maximum(bg,1e-5),0,1)
    y,x=np.indices(lum.shape);xy=np.c_[x.ravel()*8,y.ravel()*8]
    from scipy.spatial import cKDTree
    near=cKDTree(scene.pc).query(xy)[0].reshape(lum.shape)
    eligible=paper&(near>25)&(near<95)
    yy,xx=np.where(eligible);pts=np.c_[xx*8,yy*8];values=deficit[eligible]
    # Space out fitting samples; retain both shadow and lit paper controls.
    take=np.arange(0,len(pts),max(1,len(pts)//1600));pts=pts[take];values=values[take]
    sector=((np.arctan2(pts[:,1]-1590.5,pts[:,0]-1269.5)%(2*np.pi))/(2*np.pi)*8).astype(int)
    return dict(xy=pts.tolist(),deficit=values.tolist(),split=['test' if s in [1,4,6] else 'train' for s in sector],
                paper_chromaticity=ref.tolist(),source='photo-only chromaticity + broad local illumination deficit; model only restricts diagnostic distance band',
                uncertainty='Texture, JPEG/color processing and broad paper variation confound shadow deficit; low weight, not certified masks',grid_px=8)


def light_from(p,kind):
    az,el,rough=p[:3];a,e=np.radians([az,el]);d=[np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)]
    return dict(id=kind,direction=d,azimuth_deg=float(az),elevation_deg=float(el),roughness_deg=float(rough),
                width_deg=float(p[3]) if len(p)>3 else 0.,height_deg=float(p[4]) if len(p)>4 else 0.,rotation_deg=float(p[5]) if len(p)>5 else 0.,
                ambient=.2,specular_strength=1.,diffuse_reflectance=dict(black=.025,red=.2,yellow=.5,paper=.6),
                material_status='Shared relative lobe; ambient/diffuse values are display nuisance assumptions, not recovered albedos',
                source_model='distant rectangular uniform-radiance source (angular dimensions); distance/physical size unidentifiable')


def datasets(scene,obs):
    data=[];used=set()
    # Highest reliability first; one independent photographic feature per owner.
    for o in sorted(obs,key=lambda r:-r['contrast']*r['dark_surround']):
        hit=scene.camera(np.array([o['xy']]))
        owner=int(hit['owner'][0]);o['owner']=owner;o['legacy_k']=(owner-scene.config['origin'])%scene.config['n'] if owner>=0 else None
        if not o['reliable_candidate'] or owner<0 or owner in used:continue
        grid=scene.grid(scene.box([owner]),1);mask=grid['owner']==owner
        if mask.sum()<20:continue
        owned=scene.camera(np.asarray(o['patch']))['owner'];support=float(np.mean(owned==owner));o['patch_owner_fraction']=support
        if support<.8:continue
        d={k:v[mask] for k,v in grid.items()};d['observation']=o;data.append(d);used.add(owner)
    return data


def fit_model(scene,data,kind,shadow_evidence):
    training=[d for d in data if d['observation']['split']=='train']
    lengths=np.array([len(d['xy']) for d in training]);offsets=np.r_[0,np.cumsum(lengths)]
    combined={k:np.concatenate([d[k] for d in training]) for k in ['xy','owner','points','normal','viewer','unknown']}
    train_shadow=np.array(shadow_evidence['split'])=='train'
    paper=plane_points(scene,np.array(shadow_evidence['xy'])[train_shadow]);deficit=np.array(shadow_evidence['deficit'])[train_shadow]
    # Equal observation weights; do not fit per-bead gains, positions or lights.
    def residual(p):
        light=light_from(p,kind);out=[];allvals=shade(scene,combined,light,shadows=True,order=3)['specular']
        for i,d in enumerate(training):
            vals=allvals[offsets[i]:offsets[i+1]];vals=np.where(vals>=.5*vals.max(),vals,0)+1e-20;pred=moments(d['xy'],vals)
            if pred is None:pred=moments(d['xy'],np.ones(len(vals)))
            o=d['observation'];target=o['shape']
            out.extend((np.array(pred['centroid'])-o['xy'])/3)
            out.extend((np.sqrt(np.maximum(np.linalg.eigvalsh(pred['covariance']),0))-np.array([target['sigma_minor'],target['sigma_major']]))/4)
            # Covariance cross term constrains orientation without angle singularity.
            out.append((pred['covariance'][0][1]-target['covariance'][0][1])/25)
        # Paper deficits provide a low-weight independent directional constraint.
        pred=np.zeros(len(paper))
        for direction,w in directions(light):pred+=w*scene.blocked(paper+[0,0,.001],direction)[0]
        A=np.c_[np.ones(len(pred)),pred];coef=np.linalg.lstsq(A,deficit,rcond=None)[0];coef[1]=max(0,coef[1])
        out.extend((A@coef-deficit)*2*np.sqrt(len(training)/len(paper)))
        return np.array(out)
    starts=[]
    for az in ([-150,-60,30,120] if kind=='directional' else [-165,15]):
        p=[az,60,7]+([18,30,0] if kind!='directional' else [])
        lo=[-360,8,2]+([2,2,-180] if len(p)>3 else []);hi=[360,89,22]+([65,65,180] if len(p)>3 else [])
        if kind=='rectangle-smooth':lo[2]=9;hi[2]=15;p[2]=10
        if kind=='rectangle-sharp':lo[2]=2;hi[2]=5;p[2]=4
        fit=least_squares(residual,p,bounds=(lo,hi),loss='soft_l1',f_scale=2,max_nfev=32 if kind=='directional' else 16,diff_step=3e-3)
        starts.append((float(np.mean(residual(fit.x)**2)),fit.x))
        print(kind,'start',az,'nfev',fit.nfev,'score',starts[-1][0],flush=True)
    score,p=min(starts,key=lambda x:x[0]);light=light_from(p,kind);light['fit_proxy_mse']=score;light['free_parameters']=len(p);light['fit_quadrature_order']=3;light['validation_quadrature_order']=9;light['optimizer_nfev_limit']=32 if kind=='directional' else 16
    return light


def evaluate(scene,data,light):
    rows=[]
    for d in data:
        o=d['observation'];sh=shade(scene,d,light);h=highlight(d['xy'],sh['specular']);row=dict(observation_id=o['id'],owner=o['owner'],legacy_k=o['legacy_k'],split=o['split'],observed=o['xy'],observed_shape=o['shape'],predicted=h,
                    uncertainty_px=o['uncertainty_px'],cast_shadow_fraction=float(np.mean(sh['cast_shadow'])),unfinished_shadow_pairs=sh['unfinished_shadow_pairs'])
        row['error_px']=float(np.linalg.norm(np.array(h['centroid'])-o['xy'])) if h else None
        if h:
            row['size_error_px']=float(np.hypot(h['sigma_major']-o['shape']['sigma_major'],h['sigma_minor']-o['shape']['sigma_minor']))
            row['orientation_error_deg']=float(abs((h['orientation_deg']-o['shape']['orientation_deg']+90)%180-90))
            row['observed_intensity']=float(sum(o['intensity']));row['predicted_intensity']=h['weight']
        rows.append(row)
    metrics={}
    for split in ['train','test']:
        rr=[r for r in rows if r['split']==split];errors=[r['error_px'] for r in rr if r['error_px'] is not None]
        metrics[split]=dict(n=len(rr),predicted=len(errors),median_px=float(np.median(errors)),rms_px=float(np.sqrt(np.mean(np.array(errors)**2))),p90_px=float(np.percentile(errors,90)),within_3px=sum(e<=3 for e in errors))
    return rows,metrics


def plane_points(scene,xy):
    xy=np.asarray(xy);v=scene.model.view.directions(xy);base=scene.model.view.base(xy)
    return base+(scene.plane_z-base[:,2,None])/v[:,2,None]*v


def evaluate_shadows(scene,evidence,light):
    xy=np.array(evidence['xy']);p=plane_points(scene,xy);prediction=np.zeros(len(xy));un=0
    for d,w in directions(light,9):
        b,u=scene.blocked(p+[0,0,.001],d);prediction+=b*w;un+=u
    observed=np.array(evidence['deficit']);train=np.array(evidence['split'])=='train'
    # Two shared paper nuisance terms; no local shadow labels fitted.
    A=np.c_[np.ones(len(prediction)),prediction];coeff=np.linalg.lstsq(A[train],observed[train],rcond=None)[0];coeff[1]=max(0,coeff[1])
    metrics={}
    for split,mask in [('train',train),('test',~train)]:
        metrics[split]=dict(n=int(mask.sum()),rmse=float(np.sqrt(np.mean((A[mask]@coeff-observed[mask])**2))),
                           null_rmse=float(np.sqrt(np.mean((observed[mask]-observed[train].mean())**2))))
    return dict(predicted=prediction.tolist(),paper_offset=float(coeff[0]),shadow_strength=float(coeff[1]),metrics=metrics,unfinished_pairs=un)


def run(out=OUT):
    out.mkdir(parents=True,exist_ok=True);rgb=photo();inv=json.loads((ROOT/'photo2/output/debugger/generated/observations.json').read_text());obs=observations(inv,rgb)
    scene=Scene('N2696_h+1_f0');evidence=shadow_observations(rgb,scene);data=datasets(scene,obs)
    print('Observations',len(obs),'eligible matches',len(data),'test',sum(d['observation']['split']=='test' for d in data),flush=True)
    save(out/'observations.json',dict(image_sha256=sha(ROOT/'beads-photo-2.jpg'),observations=obs,shadows=evidence))
    lights=[]
    for kind in ['directional','rectangle-sharp','rectangle-smooth']:
        print('Fitting',kind,flush=True);light=fit_model(scene,data,kind,evidence);print('Evaluating',light,flush=True)
        rows,metrics=evaluate(scene,data,light);sh=evaluate_shadows(scene,evidence,light)
        light.update(metrics=metrics,shadow_metrics=sh['metrics'],status='conditional diagnostic fit; not validated illumination')
        save(out/f'{kind}-predictions.json',rows);save(out/f'{kind}-shadows.json',sh);lights.append(light);print(kind,metrics,sh['metrics'],flush=True)
    # Penalize complexity, use TRAIN only to nominate; heldout never selects params.
    nominated=min(lights,key=lambda l:l['metrics']['train']['rms_px']+l['free_parameters']*.15+2*l['shadow_metrics']['train']['rmse'])
    doc=dict(schema=1,model_id=scene.mid,model_version=scene.version,image_sha256=sha(ROOT/'beads-photo-2.jpg'),selected=nominated['id'],lights=lights,
             geometry_frozen=True,plane_z=scene.plane_z,split='Entire image-angle sectors 1,4,6 of 8 withheld before fitting',
             limitations=['Geometry-conditioned matches, not verified bead indices','Source angular extent and roughness coupled','No radiometric camera calibration','Paper shadows are weak ambiguous evidence','No per-bead lights or material fitting'],
             hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).with_name('surface.py'),ROOT/'beads.pov',ROOT/'beads-photo-2.jpg',ROOT/'photo2/output/debugger/generated/observations.json']})
    save(out/'lighting.json',doc)
    with (out/'reflection-errors.csv').open('w') as f:
        writer=csv.DictWriter(f,lineterminator='\n',fieldnames=['light','observation_id','legacy_k','split','observed_x','observed_y','predicted_x','predicted_y','error_px','size_error_px','orientation_error_deg']);writer.writeheader()
        for light in lights:
            for r in json.loads((out/f'{light["id"]}-predictions.json').read_text()):
                h=r['predicted'];writer.writerow(dict(light=light['id'],**{k:r.get(k) for k in ['observation_id','legacy_k','split','error_px','size_error_px','orientation_error_deg']},observed_x=r['observed'][0],observed_y=r['observed'][1],predicted_x=h['centroid'][0] if h else None,predicted_y=h['centroid'][1] if h else None))
    print('Nominated',doc['selected'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();run(a.output)
