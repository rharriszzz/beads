"""Independent image-basin support assignment; unchanged-geometry controls."""
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from skimage.segmentation import watershed
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,digest,utc
from photo2.r306.evidence import load
from photo2.r315.model import refined_trace
from .detect import OUT,linear
from .optics import Engine,Chain

def main():
    original=read(OUT/'epoch.json');epoch=deepcopy(original);doc=read(OUT/'observations.json.gz');allobs=doc['observations']
    im=np.array(Image.open(ROOT/'beads-photo-2.jpg'));mask=np.load(OUT/'photo-mask.npz')['mask'];markers=np.zeros(mask.shape,np.int32)
    for i,o in enumerate(allobs):x,y=o['detected_peak'];markers[y,x]=i+1
    lum=linear(im)@np.array([.2126,.7152,.0722]);labels=watershed(-ndi.gaussian_filter(lum,1.2),markers,mask=mask)
    s=Chain(original['parameters'],load()[0]);owners=sorted({j for z in s.tree.query_ball_point([o['point'] for o in epoch['observations']],35) for j in z})
    cost=np.full((len(epoch['observations']),len(owners)),1e6);records=[]
    for a,o in enumerate(epoch['observations']):
        label=next(i+1 for i,r in enumerate(allobs) if r['id']==o['id']);yy,xx=np.where(labels==label);xy=np.c_[xx,yy]
        tr=refined_trace(s,xy);alternatives=[]
        for b,j in enumerate(owners):
            fraction=float(np.mean(tr['owner']==j));distance=float(np.linalg.norm(s.pc[j]-o['point']))
            if fraction>.015 and distance<35:
                cost[a,b]=1-fraction+distance*.0001;alternatives.append(dict(index=int(s.indices[j]),visible_photo_basin_fraction=fraction,center_distance_px=distance))
        alternatives.sort(key=lambda r:-r['visible_photo_basin_fraction']);records.append(dict(id=o['id'],alternatives=alternatives,photo_basin_pixels=len(xy)))
    ii,jj=linear_sum_assignment(cost);assert len(ii)==len(epoch['observations']) and np.max(cost[ii,jj])<1e6
    mapping={epoch['observations'][i]['id']:int(s.indices[owners[j]]) for i,j in zip(ii,jj)}
    changes=[]
    for o,record in zip(epoch['observations'],records):
        idx=mapping[o['id']]
        if idx!=original['mapping'][o['id']]:changes.append(dict(id=o['id'],before=original['mapping'][o['id']],after=idx))
        o.update(index=idx,geometry_alternatives=record['alternatives'],correspondence_confidence='provisional-basin-support',
                 correspondence_basis='one-to-one maximum summed native overlap of image-only luminance watershed basins; no predicted reflection distances in assignment')
    epoch.update(id='stage1-epoch2-basin',utc=utc(),mapping=mapping,assignment_changes=changes,scope=[min(mapping.values()),max(mapping.values())],
                 policy='Same 22 observations/localization; map selected by full photographic basin support, before optical control. All identity remains provisional.')
    epoch['binding']=digest(dict(observations=epoch['observations'],mapping=mapping,method=epoch['method']))
    out=OUT/'epoch2';out.mkdir(exist_ok=True);save(out/'epoch.json',epoch);save(out/'assignment-evidence.json',dict(records=records,changes=changes))
    # The two objectives are explicitly compared with identical original geometry.
    before=read(OUT/'baseline.json.gz');after=Engine(epoch).evaluate(original['parameters'])
    save(out/'baseline.json.gz',dict(parameters=original['parameters'],**after));save(out/'assignment-control.json',dict(geometry_held_fixed=True,parameter_hash=digest(original['parameters']),before_emax=before['emax_px'],after_emax=after['emax_px'],changes=changes,geometric_gain=False))
    print('ALTERNATIVE',len(changes),'Emax',before['emax_px'],'->',after['emax_px'],'assignment only',flush=True)

if __name__=='__main__':main()
