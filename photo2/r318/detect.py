"""Photo-only bright-component selection; no predicted reflection is consulted."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import binary_closing, disk, remove_small_holes, remove_small_objects
from PIL import Image, ImageDraw
from photo2.r297.common import ROOT, read, save, sha

OUT=ROOT/'photo2/r318/results'

def linear(rgb):
    z=np.asarray(rgb,dtype=float)/255
    return np.where(z<=.04045,z/12.92,((z+.055)/1.055)**2.4)

def principal(xy, intensity, fraction=.5, floor=1e-4):
    """Brightest connected threshold component, with deterministic peak ties."""
    xy=np.asarray(xy);v=np.asarray(intensity)
    if not len(v) or v.max()<floor:return None
    lo=xy.min(0);ij=np.rint(xy-lo).astype(int);shape=tuple((ij.max(0)+1)[::-1])
    field=np.zeros(shape);field[ij[:,1],ij[:,0]]=v
    labels,n=ndi.label(field>=max(floor,fraction*v.max()),np.ones((3,3)))
    k=int(np.argmax(v));label=labels[ij[k,1],ij[k,0]]
    ix=np.flatnonzero(labels[ij[:,1],ij[:,0]]==label);pts=xy[ix];w=v[ix]
    ties=pts[w==w.max()];near=pts[w>=.98*w.max()]
    others=[]
    for j in range(1,n+1):
        if j==label:continue
        yy,xx=np.where(labels==j);peak=float(field[yy,xx].max())
        others.append(dict(peak_intensity=peak,relative_peak=peak/float(v.max()),pixels=len(xx)))
    return dict(point=np.average(pts,axis=0,weights=w).tolist(),centroid=pts.mean(0).tolist(),
                peak=ties[0].tolist(),ties=ties.tolist(),near_maximum=near.tolist(),
                peak_intensity=float(w.max()),area=len(ix),pixels=pts.tolist(),
                secondary_components=others,threshold_fraction=fraction)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    im=np.array(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'));rgb=im.astype(float)
    seed=(rgb[:,:,2]<.63*rgb[:,:,0])|(rgb.max(2)<75)
    mask=remove_small_objects(remove_small_holes(binary_closing(seed,disk(5)),area_threshold=800),min_size=3000)
    dist=ndi.distance_transform_edt(mask)
    white=linear(im).min(2);smooth=ndi.gaussian_filter(white,.65)
    contrast=smooth-ndi.gaussian_filter(white,5)
    maxima=(smooth==ndi.maximum_filter(smooth,size=9))&(smooth>.07)&(contrast>.025)&mask
    yy,xx=np.where(maxima);order=np.argsort(-smooth[yy,xx],kind='stable');points=[]
    for i in order:
        p=np.array([xx[i],yy[i]])
        if any(np.linalg.norm(p-q)<10 for q in points):continue
        points.append(p)
    points=sorted(points,key=lambda p:(p[1],p[0]));rows=[]
    for i,(x,y) in enumerate(points):
        x0=max(0,x-13);y0=max(0,y-13);crop=white[y0:y+14,x0:x+14]
        cy,cx=np.mgrid[y0:y0+crop.shape[0],x0:x0+crop.shape[1]];xy=np.c_[cx.ravel(),cy.ravel()]
        variants=[principal(xy,crop.ravel(),f) for f in [.4,.5,.6]];m=variants[1]
        # The localization window must retain the detected peak; a brighter
        # neighbor is a documented observation ambiguity, not a silent switch.
        peakdist=float(np.linalg.norm(np.array(m['peak'])-[x,y]))
        shifts={key:float(max(np.linalg.norm(np.array(z[key])-m[key]) for z in variants)) for key in ['point','centroid','peak']}
        near=np.array(m['near_maximum']);spread=float(np.max(np.linalg.norm(near-np.array(m['point']),axis=1)))
        uncertainty=max(.71,shifts['point'],min(spread,5.))
        pix=np.array(m['pixels']);clipped=bool(np.any((pix[:,0]==x0)|(pix[:,0]==x0+crop.shape[1]-1)|(pix[:,1]==y0)|(pix[:,1]==y0+crop.shape[0]-1)))
        around=rgb[max(0,y-8):y+9,max(0,x-8):x+9];med=np.median(around.reshape(-1,3),axis=0)
        color='black' if med.max()<90 else ('yellow' if med[1]>.5*med[0] and med[2]<.6*med[0] else 'red')
        reasons=[]
        if dist[y,x]<11:reasons.append('near_photo_rope_silhouette')
        if peakdist>7:reasons.append('competing_brighter_neighbor_in_window')
        if clipped:reasons.append('bright_component_reaches_localization_window')
        if shifts['point']>2:reasons.append('threshold_localization_unstable')
        if m['area']<2:reasons.append('single_pixel_unsupported_peak')
        if any(z['relative_peak']>.95 for z in m['secondary_components']):reasons.append('near_equal_disconnected_principal_lobes')
        rows.append(dict(id=f'auto-{i:04}',detected_peak=[int(x),int(y)],point=m['point'],
                         component=m,variants=variants,method_threshold_shift_px=shifts,
                         uncertainty_px=uncertainty,silhouette_distance_px=float(dist[y,x]),
                         color=color,color_status='automatic local pigment cue; not inferred pattern',
                         eligible=not reasons,exclusion_reasons=reasons,window=[int(x0),int(y0),crop.shape[1],crop.shape[0]],
                         saturated_rgb_pixels=int(np.any(im[y0:y+14,x0:x+14]>=254,axis=2).sum())))
    # Prior measured geography only; no optical prediction or residual is used.
    model=read(ROOT/'photo2/r317/results/joint-preserved-model.json.gz')
    indices=np.array(model['positions']['indices']);pc=np.array(model['positions']['projected'])
    tree=cKDTree(pc[(indices>=-100)&(indices<=99)])
    eligible=[r for r in rows if r['eligible'] and tree.query(r['point'])[0]<35]
    assert len(eligible)>=20, len(eligible)
    xy=np.array([r['point'] for r in eligible]);choices=[]
    for i,r in enumerate(eligible):
        distance=np.linalg.norm(xy-xy[i],axis=1);order=np.argsort(distance,kind='stable')[:22]
        radius=float(distance[order[-1]])
        choices.append((radius+4*np.mean([eligible[j]['uncertainty_px'] for j in order]),i,order,radius))
    _,i,order,radius=min(choices,key=lambda z:(z[0],z[1]));center=xy[i]
    picked={eligible[j]['id'] for j in order}
    for r in rows:
        r['in_initial_patch']=bool(np.linalg.norm(np.array(r['point'])-center)<=radius+1e-8)
        r['selected_photo_candidate']=r['id'] in picked
        if r['eligible'] and not r['selected_photo_candidate']:
            r['exclusion_reasons'].append('outside_frozen_stage1_candidate_patch')
    save(OUT/'observations.json.gz',dict(photo_sha256=sha(ROOT/'beads-photo-2.jpg'),observations=rows,
         patch_center=center.tolist(),patch_radius=radius,photo_candidate_ids=sorted(picked),
         localization='Intensity-weighted centroid of brightest connected half-maximum component of linear-light minimum RGB; no disconnected averaging',
         mask_policy='Photo-only blue/red ratio or dark material, radius5 closing, fill holes <800px; silhouette clearance>=11px',
         selection_policy='22 reliable interior candidates in most compact quality-adjusted neighborhood within inherited -100..99 geography; no optical predictions consulted'))
    np.savez_compressed(OUT/'photo-mask.npz',mask=mask)
    lo=np.floor(center-radius-35).astype(int);hi=np.ceil(center+radius+35).astype(int)
    crop=Image.fromarray(im).crop((*lo,*hi)).resize(tuple((hi-lo)*3))
    draw=ImageDraw.Draw(crop)
    for r in rows:
        if not r['in_initial_patch']:continue
        x,y=(np.array(r['point'])-lo)*3;col='cyan' if r['selected_photo_candidate'] else 'orange'
        draw.ellipse((x-6,y-6,x+6,y+6),outline=col,width=2);draw.text((x+7,y-6),r['id'][5:],fill=col)
    crop.save(OUT/'selection.png')
    print('candidates',len(rows),'eligible_local',len(eligible),'selected',len(picked),'center',center,'radius',radius,flush=True)

if __name__=='__main__':main()
