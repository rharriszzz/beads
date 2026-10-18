"""Exact appearance extraction with scalar minimum-channel linearization.
The monotonic sRGB transfer commutes with channel minimum; there is no need to
allocate a full RGB linear image merely to immediately reduce it to one channel.
"""
import json
import numpy as np
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from photo2.r322 import tracker as base
ROOT=base.ROOT;sample=base.sample
def observations(data):
    # Reuse measured pigment/reflection evidence instead of inventing segmentation.
    # Deliberately ignore historical centerline groups, graph/physical identities,
    # region outlines and black-body collars. Only bright native supports are read.
    path=ROOT/'photo2/review/r275/inventory.json';catalog=json.loads(path.read_text());catalog_sha=base.sha(path)
    obs=[];support=[]
    for record in catalog['locations']:
        patch=record['bright_patch'];point=np.array(patch['centroid'])
        if not(base.CROP[0]<=point[0]<base.CROP[2] and base.CROP[1]<=point[1]<base.CROP[3]):continue
        pixels=np.array([[x,y] for y,xa,xb in patch['runs'] for x in range(xa,xb+1)])
        if not len(pixels):continue
        oid=record['id'];local=point-np.array(base.CROP[:2])
        clearance=float(sample(data['clearance'],local[None])[0])
        obs.append(dict(id=oid,kind='specular-reflection' if record['color']=='black' else 'pigment-bright-patch',
            color=record['color'],xy=point.tolist(),allowance_px=18,area=len(pixels),source_pixel_count=len(pixels),
            location_kind='observed bright support centroid; not bead center',pixel_support=oid,
            source='photo2/review/r275/inventory.json:locations:'+oid,source_sha256=catalog_sha,
            historical_interior_status=record['interior_status'],band_clearance_px=clearance,
            note='Historical image-only color cue; no bead index, centerline grouping or full outline reused.'))
        support.append(dict(id=oid,pixels_xy=pixels.tolist()))
    # Supplemental local white reflections, using only the original RGB. These
    # are not predictions at lattice sites. Existing observations retain priority;
    # nearby new components are not counted as separate beads.
    rgb=data['rgb'];minimum=rgb.min(2)
    white=np.where(minimum<=.04045,minimum/12.92,((minimum+.055)/1.055)**2.4);smooth=ndi.gaussian_filter(white,.65);contrast=smooth-ndi.gaussian_filter(white,5)
    loc=peak_local_max(smooth,min_distance=9,threshold_abs=.07,labels=data['fg'])
    for yy,xx in loc:
        if contrast[yy,xx]<.025 or data['clearance'][yy,xx]<11:continue
        y0=max(0,yy-10);x0=max(0,xx-10);patch=white[y0:yy+11,x0:xx+11]
        lab,_=ndi.label(patch>=.5*white[yy,xx],np.ones((3,3)))
        label=lab[yy-y0,xx-x0]
        if not label:continue
        py,px=np.where(lab==label)
        if len(px)<2:continue
        pixels=np.column_stack([px+x0,py+y0]);point=np.average(pixels,axis=0,weights=white[pixels[:,1],pixels[:,0]])+np.array(base.CROP[:2])
        nearby=[o for o in obs if np.linalg.norm(np.array(o['xy'])-point)<12]
        if nearby:continue  # location-level deduplication; not an identity proof
        clipped=bool(np.any((px==0)|(py==0)|(px==patch.shape[1]-1)|(py==patch.shape[0]-1)))
        if clipped:continue
        surround=rgb[max(0,yy-8):yy+9,max(0,xx-8):xx+9];med=np.median(surround.reshape(-1,3),axis=0)
        color='black' if med.max()<90/255 else ('yellow' if med[1]>.5*med[0] and med[2]<.6*med[0] else 'red')
        oid=f'NEW-{xx+base.CROP[0]}-{yy+base.CROP[1]}'
        obs.append(dict(id=oid,kind='fresh-bright-component',color=color,xy=point.tolist(),allowance_px=18,
            area=len(px),source_pixel_count=len(px),pixel_support=oid,source='original RGB, linear minimum-channel half-maximum component',
            location_kind='bright component; not bead center',band_clearance_px=float(data['clearance'][yy,xx]),
            color_status='automatic local pigment/darkness cue'))
        support.append(dict(id=oid,pixels_xy=(pixels+np.array(base.CROP[:2])).tolist()))
    return obs,support
