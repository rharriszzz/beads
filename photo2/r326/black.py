"""Provisional native reflection observations and shared projected-region evidence.
Colored pigment extents are visible-region proxies, never complete bead contours.
The same local ellipse and orientation rule applies to all colors. Reflection
location is uncertain within that region; it is not a measured physical center.
"""
from collections import defaultdict
import numpy as np
from scipy import ndimage as ndi
from photo2.r322 import tracker as base


def regions_and_provisionals(black,obs,data,windows):
    op={o['id']:o for o in obs};rgb=data['rgb'];records=[];groups=[];ellipses={}
    for p in black['predictions']:
        if 'raw_support_pixels' not in p:continue
        point=np.array(p['raw_centroid_xy']);target=None
        for group in groups:
            if np.linalg.norm(point-np.array(group[0]['raw_centroid_xy']))<12:target=group;break
        if target is None:groups.append([p])
        else:target.append(p)
    provisional=[];pixels=[]
    for gi,rows in enumerate(groups):
        # Union raw support, recompute centroid on original linear white values.
        xy=np.array(sorted({tuple(x) for p in rows for x in p['raw_support_pixels']}));v=rgb[xy[:,1],xy[:,0]].min(1);v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);point=np.average(xy,axis=0,weights=v)
        nearest=min(obs,key=lambda o:np.linalg.norm(np.array(o['xy'])-point));distance=float(np.linalg.norm(np.array(nearest['xy'])-point));anchors=sorted({o for p in rows for o in p['colored_anchors']});winids=sorted({p['window'] for p in rows})
        shapes=[]
        for oid in anchors:
            o=op[oid];x,y=np.rint(o['xy']).astype(int);rad=19;x0=max(0,x-rad);y0=max(0,y-rad);patch=rgb[y0:y+rad+1,x0:x+rad+1];yy,xx=np.indices(patch.shape[:2]);mask=(patch[:,:,0]>1.5*patch[:,:,2])&(patch[:,:,0]>.16)
            # Local visible pigment only, with a fixed common radius cap.
            mask&=(xx+x0-x)**2+(yy+y0-y)**2<=rad**2
            lab,n=ndi.label(mask);cy,cx=y-y0,x-x0;k=lab[cy,cx]
            if not k:continue
            py,px=np.where(lab==k)
            if len(px)<20:continue
            pts=np.column_stack([px+x0,py+y0]);cov=np.cov(pts.T);shapes.append(cov)
        cov=np.median(np.array(shapes),axis=0) if shapes else np.eye(2)*49
        ev,E=np.linalg.eigh(cov);ev=np.clip(ev,16,100);cov=(E*ev)@E.T
        ellipse=dict(center_proxy_xy=np.mean([p['predicted_xy'] for p in rows],axis=0).tolist(),covariance_px2=cov.tolist(),radii_2sigma_px=(2*np.sqrt(ev)).tolist(),axes=E.tolist(),colored_anchors=anchors,measured_colored_regions=len(shapes),
            meaning='Approximate partially visible pigment-region envelope transported to a same-shape bead; not measured full outline or center. Per-region covariance accommodates projection/orientation.',center_uncertainty_px=8,occlusion='Partial visible support allowed; darkness alone is not evidence')
        center=np.array(ellipse['center_proxy_xy']);mahal=float((point-center)@np.linalg.inv(cov+np.eye(2)*64)@(point-center));supported=distance>=12 and len(anchors)>=3 and len(winids)>=2 and mahal<=4 and len(xy)>=2
        oid=f'PROV326-{int(round(point[0]))}-{int(round(point[1]))}'
        record=dict(id=oid,xy=point.tolist(),native_pixels_xy=xy.tolist(),windows=winids,colored_anchors=anchors,nearest_existing=nearest['id'],nearest_distance_px=distance,ellipse=ellipse,mahalanobis_with_center_uncertainty=mahal,
            admitted=supported,independent_detection=False,body_identity_confirmed=False,competing_explanations=['faint reflection of a separate black bead','secondary reflection on an already observed bead','local glare or non-bead highlight'],
            status='provisional native reflection and neighboring-geometry hypothesis' if supported else 'unconfirmed native site; insufficient distinct neighboring context',source_predictions=[dict(window=p['window'],cell_ab=p['cell_ab'],predicted_xy=p['predicted_xy']) for p in rows])
        records.append(record)
        if supported:
            provisional.append(dict(id=oid,kind='geometry-triggered provisional native reflection',color='black',xy=point.tolist(),allowance_px=18,area=len(xy),source_pixel_count=len(xy),pixel_support=oid,source='original RGB + colored-only candidate predictions; provisional distinct-body identity',location_kind='native faint support centroid; not bead center',band_clearance_px=float(base.sample(data['clearance'],point[None])[0]),provisional=True,independent_detection=False,body_identity_confirmed=False))
            pixels.append(dict(id=oid,pixels_xy=xy.tolist()))
    return provisional,pixels,dict(sites=records,provisional_count=len(provisional),independently_new_beads=0,policy='Provisional observations compete with original no-addition candidates; no absence/expected-site-only promotion. Two overlapping windows are correlated, not independent confirmations.')
