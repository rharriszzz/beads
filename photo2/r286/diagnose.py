"""Reconstruct P5's original S graph and trace its actual permitting connections."""
import os,heapq
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r286-mpl')
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import h_maxima
from photo2.r282.common import circular_distance
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from photo2.r282.phase1 import image_features
from photo2.r285.methods import measurements,basins
from photo2.r285.run import local_mask
from .common import *

def widest_path(field,domain,a,b):
    """Maximum-minimum 4-neighbor route, saved to expose permissive detours."""
    a=tuple(a[::-1]);b=tuple(b[::-1]);best=np.full(field.shape,-np.inf);best[a]=field[a];queue=[(-best[a],a)];prev={}
    while queue:
        neg,p=heapq.heappop(queue)
        if -neg<best[p]:continue
        if p==b:break
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            q=(p[0]+dy,p[1]+dx)
            if min(q)<0 or q[0]>=len(field) or q[1]>=field.shape[1] or not domain[q]:continue
            value=min(best[p],field[q])
            if value>best[q]:best[q]=value;prev[q]=p;heapq.heappush(queue,(-value,q))
    if not np.isfinite(best[b]):return [],None
    route=[b]
    while route[-1]!=a:route.append(prev[route[-1]])
    return [[int(v) for v in p[::-1]] for p in route[::-1]],float(best[b])

def main():
    native,rgb,meta=photo();f=image_features(rgb);o=reviewed()[-1]['observation'];x,y=o['seed'];origin=np.array(o['origin']);sl=np.s_[y-48:y+49,x-48:x+49];lum=f['lum'][sl];hs=f['hsv'][sl];paper=f['paper'][sl]
    smooth,pigment,domain,seed,info=measurements(lum,hs,paper,f['palette'],f['background_hue'],o['color']);mask,labels,group,refs,edges,markers=basins(smooth,pigment,domain,seed)
    np.testing.assert_array_equal(mask,local_mask(o['variants']['S']['measured_support'],origin,mask.shape))
    relevant=[]
    for e in edges:
        if not any(k in group for k in e['markers']):continue
        p=np.array(e['boundary_pixels']);v=np.minimum(smooth[p[:,1],p[:,0]],smooth[p[:,3],p[:,2]]);a,b=np.array(e['peaks']);straight=np.linspace(a,b,max(2,int(np.linalg.norm(b-a)*4)));profile=ndi.map_coordinates(smooth,straight[:,::-1].T,order=1)
        route,minimum=widest_path(smooth,domain,a,b);e.update(boundary_Y_quantiles=np.quantile(v,[0,.1,.5,.9,1]).tolist(),fraction_below_old_limit=float((v<.65*min(e['diffuse_references'])).mean()),straight_route=straight.tolist(),straight_profile=profile.tolist(),straight_minimum=float(profile.min()),widest_path=route,widest_minimum=minimum);relevant.append(e)
    missing=[]
    raw_labels,n=ndi.label(h_maxima(np.log(smooth+.003),.20))
    for k in range(1,n+1):
        yy,xx=np.where(raw_labels==k);j=np.argmax(smooth[yy,xx]);px,py=int(xx[j]),int(yy[j])
        if domain[py,px] or smooth[py,px]<.5*info['diffuse_Y'] or paper[py,px]:continue
        yy2,xx2=np.indices(domain.shape);near=(xx2-px)**2+(yy2-py)**2<=9;valid=near&domain&mask
        if not valid.any() or pigment[near].mean()<.5:continue
        dy,dx=np.where(valid);q=np.argmin((dx-px)**2+(dy-py)**2);snapped=[int(dx[q]),int(dy[q])];route,minimum=widest_path(smooth,domain,seed,snapped)
        straight=np.linspace(seed,snapped,120);profile=ndi.map_coordinates(smooth,straight[:,::-1].T,order=1)
        missing.append(dict(peak=[px,py],native_Y=float(lum[py,px]),smooth_Y=float(smooth[py,px]),hue_deg=float(hs[py,px,0]*360),saturation=float(hs[py,px,1]),own_hue_distance=float(circular_distance(hs[py,px,0]*360,f['palette'][o['color']])),paper=bool(paper[py,px]),nearby_pigment_fraction=float(pigment[near].mean()),snapped=snapped,widest_path=route,widest_minimum=minimum,straight_route=straight.tolist(),straight_profile=profile.tolist(),straight_minimum=float(profile.min())))
    info['missing_markers']=missing
    info.update(source_seed=o['seed'],origin=origin.tolist(),palette=f['palette'],background_hue=f['background_hue'],merged_marker_ids=group,refs=refs,area=int(mask.sum()),relevant_edges=relevant,all_edges=edges,smoothing_native_difference=float(np.abs(lum-smooth).mean()),domain_area=int(domain.sum()),material_area=int(pigment.sum()),domain_contact=int((mask[[0,-1],:]).sum()+(mask[:,[0,-1]]).sum()),old_domain32_area=o['variants']['S']['method_evidence']['domain32_area'],old_domain_iou=o['variants']['S']['method_evidence']['domain_iou'])
    save(OUT/'P5-diagnosis.json',info);np.savez_compressed(OUT/'P5-fields.npz',native_Y=lum,smooth=smooth,pigment=pigment,eligible=domain,markers=markers,labels=labels,support=mask)
    im=native[y-48:y+49,x-48:x+49];Image.fromarray(im).save(REVIEW/'P5-diagnostic-native.png');fig,axs=plt.subplots(2,4,figsize=(15,8))
    axs[0,0].imshow(im);axs[0,0].plot(*seed,'x',color='cyan');axs[0,0].set_title('Original pixels / refined photographic cue')
    axs[0,1].imshow(lum,cmap='magma');axs[0,1].set_title('Native ICC linear luminance')
    axs[0,2].imshow(smooth,cmap='magma');axs[0,2].contour(pigment,levels=[.5],colors=['cyan'],linewidths=.5);axs[0,2].set_title('Smoothed field / yellow-material gate')
    axs[0,3].imshow(im);axs[0,3].imshow(np.ma.masked_where(~domain,domain),alpha=.35,cmap='winter');axs[0,3].set_title(f'Eligible intensity/material domain: {domain.sum()}px')
    axs[1,0].imshow(labels,cmap='tab20',interpolation='nearest');axs[1,0].set_title('Watershed regions BEFORE merging')
    for k in range(1,int(markers.max())+1):
        yy,xx=np.where(markers==k);axs[1,0].text(xx.mean(),yy.mean(),str(k),color='white',fontsize=9,ha='center',bbox=dict(facecolor='black',alpha=.6,pad=1))
    axs[1,1].imshow(im);axs[1,1].imshow(np.ma.masked_where(~mask,mask),cmap='cool',alpha=.5);axs[1,1].set_title('S group '+str(group)+f': {mask.sum()}px (one basin)')
    ax=axs[1,2];ax.imshow(im);ax.set_title('Missing markers / actual bright connections')
    for i,e in enumerate(missing):
        ax.plot(*e['peak'],'x',color='red');ax.text(*e['peak'],f" M{i+1}",color='white',fontsize=8);r=np.array(e['widest_path']);ax.plot(r[:,0],r[:,1],lw=1,label=f"M{i+1}: minY={e['widest_minimum']:.3f}")
    ax.legend(fontsize=6)
    ax=axs[1,3]
    for i,e in enumerate(missing):ax.plot(np.linspace(0,1,len(e['straight_profile'])),e['straight_profile'],label=f"cue to M{i+1}; min={e['straight_minimum']:.3f}")
    ax.axhline(info['level'],ls='--',label='Permissive intensity floor',color='black');ax.legend(fontsize=6);ax.set_title('Direct valleys below floor; detours survive');ax.set_xlabel('Fraction along straight route');ax.set_ylabel('Linear Y')
    for ax in axs.flat[:-1]:ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle('R286 P5 diagnosis — no new segmentation rule yet');fig.tight_layout();fig.savefig(REVIEW/'P5-root-cause.png',dpi=140);plt.close(fig)
    print({k:info[k] for k in ('source_seed','refined_seed','diffuse_Y','background_Y','noise_floor','level','merged_marker_ids','area','old_domain32_area','old_domain_iou')})
    print('missing', [{k:v for k,v in e.items() if 'path' not in k and 'profile' not in k and 'route' not in k} for e in missing])
    for e in relevant:print({k:e[k] for k in ('markers','peaks','diffuse_references','saddle_ratio','boundary_Y_quantiles','fraction_below_old_limit','separated','separate_after_merging','straight_minimum','widest_minimum')})
if __name__=='__main__':main()
