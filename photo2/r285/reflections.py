"""Reflection-only R1/R2/R4 comparison, old controls preserved and two new anchors."""
import copy
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from PIL import Image
from photo2.r282.common import ROOT,read,save,photo,pixels,support,record,validate
from photo2.r282.phase1 import image_features
from photo2.r284b.methods import reflection,metrics
from photo2.r284b.run import mask_of
from photo2.r284.assess import TARGETS
from .select import OUT,bank
from .review import REVIEW,plt

def main():
    native,rgb,_=photo();f=image_features(rgb);rows=[copy.deepcopy(o) for o in bank() if o['color']=='black'];baseline=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];rr={r['record_id']:r for r in baseline}
    for q in read(OUT/'selection.json')['confirmation']:
        if q['color']!='black':continue
        x,y=q['seed'];origin=np.array([x,y])-24;sl=np.s_[y-24:y+25,x-24:x+25];lum=f['lum'][sl];hs=f['hsv'][sl];initial=mask_of(rr[q['id']]['measured_support'],origin);domain=((hs[:,:,1]<.65)|(hs[:,:,1]*hs[:,:,2]<.12))&~f['paper'][sl];variants={}
        for m in ('R1','R2','R4'):
            mask,c,meta=reflection(lum,domain,initial,variant=m);yy,xx=np.where(mask);met=metrics(mask,c,lum,initial,[24,24]);meta['perturbations']=[]
            for sigma,delta in ((.5,-.02),(.8,.02)):
                pm,pc,_=reflection(lum,domain,initial,variant=m,sigma=sigma,level_delta=delta);meta['perturbations'].append(dict(sigma=sigma,level_delta=delta,mask_iou=float((mask&pm).sum()/max(1,(mask|pm).sum())),contour_mean_distance=float(cKDTree(c).query(pc)[0].mean()) if len(c) and len(pc) else None))
            variants[m]=dict(measured_support=support(np.c_[xx,yy]+origin),subpixel_contour=(c+origin).tolist(),metrics=met,method_evidence=meta,peak_location=(np.array(meta['peak'])+origin).tolist(),measured_photo_location=(np.array(met['centroid'])+origin).tolist() if met['centroid'] else None,support_type='specular-reflection region',physical_body_center=None,physical_body_centerline_crossing=None,phase_of_origin='phase1',importance='high',physical_identity_reliability=0,photographic_reliability='unrated',color_reliability='unrated',visibility='unresolved',evidence_links=['beads-photo-2.jpg','photo2/r285/results/selection.json'])
        for m,v in variants.items():
            base=record(q['id']+':'+m,'phase1');base.update(v);base['visibility']=None;base['visibility_notes']='unresolved';base['phase1_reliability']=0.;base['color_reliability']=0.;base['color_reliability_kind']='unrated image-only assignment';base['photographic_reliability']=dict(classification='unrated',calibrated_probability=None);base['status']='experimental-unresolved';base['seed']=q['seed'];base['color']='black';base['method']=m
            if base['measured_support']:base['measured_support']['kind']='specular-reflection region'
            validate(base);variants[m]=base
        rows.append(dict(id=q['id'],seed=q['seed'],origin=origin.tolist(),color='black',source_status=q['source_status'],native_Y=lum.tolist(),variants=variants))
    for o in rows:
        for m in ('R1','R2','R4'):
            v=o['variants'][m];c=np.array(v['subpixel_contour']).reshape(-1,2)-o['origin'];field=ndi.gaussian_filter(np.array(o['native_Y']),.65);level=v['method_evidence']['level']
            v['isophote_mean_absolute_Y_residual']=float(np.abs(ndi.map_coordinates(field,c[:,::-1].T,order=1)-level).mean()) if len(c) else None
    summary={}
    for m in ('R1','R2','R4'):
        vs=[o['variants'][m] for o in rows];summary[m]=dict(features=len(vs),nonempty=sum(v['metrics']['area']>0 for v in vs),median_turn_energy=float(np.median([v['metrics']['turn_energy'] for v in vs if v['metrics']['turn_energy'] is not None])),median_centroid_shift=float(np.median([v['metrics']['centroid_shift'] for v in vs if v['metrics']['centroid_shift'] is not None])),mean_boundary_gradient=float(np.mean([v['metrics']['boundary_gradient'] for v in vs if v['metrics']['boundary_gradient'] is not None])),brighter_neighbor_flags=sum(v['method_evidence']['brighter_neighbor_in_support'] for v in vs),median_perturbation_iou=float(np.median([p['mask_iou'] for v in vs for p in v['method_evidence']['perturbations']])))
    selected=[]
    for name,xy in TARGETS['duplicate'][:2]:selected.append((name,min(rows,key=lambda o:np.linalg.norm(np.array(o['seed'])-xy))))
    old=[o for o in rows if o['id'].startswith('auto-weak:')];selected.append(('weak-reference',min(old,key=lambda o:o['variants']['R1']['method_evidence']['peak_Y'])))
    selected.extend((f'black-confirmation-{i+1}',o) for i,o in enumerate(rows[-2:]))
    for name,o in selected:
        origin=np.array(o['origin']);x,y=origin;im=native[y:y+49,x:x+49];lum=np.array(o['native_Y']);Image.fromarray(im).save(REVIEW/(name+'-native.png'));fig,axs=plt.subplots(3,4,figsize=(12,8))
        axs[0,0].imshow(im,interpolation='nearest');axs[0,0].set_title('Raw photo enlarged');axs[1,0].imshow(lum,cmap='magma',interpolation='nearest');axs[1,0].set_title('Native linear luminance');axs[2,0].axis('off');axs[2,0].text(0,.8,'Black measurements = reflections\nWhite +: photographic centroid\nGreen dot: native peak\nNo body or ownership inference.',fontsize=10)
        for col,m in enumerate(('R1','R2','R4'),1):
            r=o['variants'][m];c=np.array(r['subpixel_contour']).reshape(-1,2)-origin;mask=mask_of(r['measured_support'],origin);pk=np.array(r['peak_location'])-origin
            for row in (0,1):
                ax=axs[row,col];ax.imshow(im,interpolation='nearest')
                if row==1:
                    rgba=np.zeros((49,49,4));rgba[mask]=[0,1,1,.5];ax.imshow(rgba,interpolation='nearest')
                if len(c):ax.plot(c[:,0],c[:,1],color='cyan',lw=1)
                if r['measured_photo_location']:ax.plot(*(np.array(r['measured_photo_location'])-origin),'+',color='white')
                ax.plot(*pk,'.',color='lime');ax.set_title(m+(' smooth isophote' if row==0 else f" exact support: {mask.sum()}px"))
            px,py=pk.astype(int);ax=axs[2,col];ax.plot(lum[py,:],label='native horizontal');ax.plot(lum[:,px],label='native vertical');ax.axhline(r['method_evidence']['level'],ls='--',color='orange',label='smooth isophote');ax.legend(fontsize=6);ax.set_title(f"turn {r['metrics']['turn_energy'] or 0:.3f}; shift {r['metrics']['centroid_shift'] or 0:.2f}px")
        for ax in axs[:2].flat:ax.set_xticks([]);ax.set_yticks([]);ax.set_xlim(-.5,48.5);ax.set_ylim(48.5,-.5)
        fig.suptitle(name+' — R2 experimental default; retain R4 when neighboring highlights compete');fig.tight_layout();fig.savefig(REVIEW/(name+'.png'),dpi=130);plt.close(fig)
    save(OUT/'reflections.json.gz',dict(observations=rows,summary=summary,selected=[dict(name=n,id=o['id']) for n,o in selected],default='R2; R4 alternative for competing features; never silently assign physical ownership',confirmation_ids=[o['id'] for o in rows[-2:]]));save(OUT/'reflection-summary.json',summary)
if __name__=='__main__':main()
