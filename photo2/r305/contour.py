"""Existing B15 uncertain contour compared with native ownership, without fitting."""
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_erosion,distance_transform_edt
from scipy.spatial import cKDTree
from .model import *
from .diagnose import isolated
from photo2.r297.common import save
from photo2.r302.experiment import clean

def main():
    dim=source('primary')[1]['bead_dimensions'][0];polygon=np.array(dim['polygon']);lo=polygon.min(0)-25;hi=polygon.max(0)+25;shape=tuple((hi-lo+1)[::-1]);im=Image.new('1',shape[::-1]);ImageDraw.Draw(im).polygon([tuple(p-lo) for p in polygon],fill=1);mask=np.array(im,bool);yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.c_[xx.ravel(),yy.ravel()];out=[]
    for name in FAMILIES:
        scene=Extended(name);corr=read(BASE/f'results/{name}-correspondences.json');idx=next(q['index'] for q in corr['records'] if q['observation']=='C-1116-0328');single=isolated(scene,idx);tr=scene.camera(xy);owner=np.full(len(xy),-32768);ok=tr['owner']>=0;owner[ok]=scene.indices[tr['owner'][ok]];owner=owner.reshape(shape);sil=single.camera(xy)['owner'].reshape(shape)>=0
        assigned=owner==idx;distance=distance_transform_edt(~assigned);predboundary=assigned&~binary_erosion(assigned);observedboundary=mask&~binary_erosion(mask);d2=distance_transform_edt(~predboundary);d1=distance_transform_edt(~observedboundary)
        controls=[]
        for label,m in [('eroded3px',binary_erosion(mask,iterations=3)),('polygon',mask),('dilated3px',binary_dilation(mask,iterations=3))]:
            controls.append(dict(region=label,pixels=int(m.sum()),inside_assigned=float(np.mean(assigned[m])),inside_other=float(np.mean(((owner!=-32768)&~assigned)[m])),outside_union=float(np.mean((owner==-32768)[m])),occluded_by_neighbors=float(np.mean((sil&~assigned&(owner!=-32768))[m])),unknown_camera_fraction=float(np.mean(tr['unknown'].reshape(shape)[m])),outside_unobstructed=float(np.mean((~sil)[m])),uncovered_pixels=int(np.sum(m&~assigned)),uncovered_distance_max_px=float(distance[m].max())))
        out.append(dict(model=name,source=dim,index=idx,controls=controls,observed_to_visible_boundary_median_px=float(np.median(d2[observedboundary])),observed_to_visible_boundary_max_px=float(d2[observedboundary].max()),visible_to_observed_boundary_median_px=float(np.median(d1[predboundary])),meaning='Existing B15 analyst polygon; ±3px morphological controls are sensitivity, not confidence bounds or a full-bead certificate. Shape/pose/identity cannot be uniquely separated.'))
    save(BASE/'results/B15-contour-diagnosis.json',clean(out));print(json.dumps(clean(out),indent=2))
    p=REVIEW/'data.js';data=json.loads(p.read_text()[11:-2]);data['contour']=out;p.write_text('const DATA='+json.dumps(clean(data),separators=(',',':'))+';\n')
if __name__=='__main__':main()
