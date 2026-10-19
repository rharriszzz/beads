"""Reproject frozen glass bodies on a complete local grid; no light or fitting."""
from pathlib import Path
import json,time,hashlib
import numpy as np
from photo2.r329.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r321.model import Chain
from photo2.r315.model import refined_trace,subset
OUT=Path(__file__).resolve().parent

def main():
 t=time.perf_counter();source=ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz';f=read(source);s=Chain(f['parameters'],load()[0]);error=float(np.max(abs(s.pc-np.array(f['positions']['projected']))));assert error<1e-8
 bbox=[1230,208,1510,365];step=.5;xx=np.arange(bbox[0],bbox[2],step);yy=np.arange(bbox[1],bbox[3],step);x,y=np.meshgrid(xx,yy);xy=np.c_[x.ravel(),y.ravel()];tr=refined_trace(s,xy);assert not tr['unknown'].any()
 arrays=dict(xy=xy,owner=tr['owner'],shape=np.array(x.shape),bbox=np.array(bbox),step=np.array(step),indices=s.indices,projected=s.pc)
 for addr in [-33,-27]:
  j=int(np.flatnonzero(s.indices==addr)[0]);iso=refined_trace(subset(s,[j]),xy);assert not iso['unknown'].any();arrays['isolated_'+str(addr)]=iso['owner']>=0
 np.savez_compressed(OUT/'model-geometry.npz',**arrays)
 record={'model':'frozen R321 geometry-best N3000','parameters':f['parameters'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'all_bodies':s.n,'full_crop_xyxy':bbox,'sample_spacing_px':step,'camera_rays':len(xy),'unknown_rays':int(tr['unknown'].sum()),'projected_center_max_delta_from_saved_px':error,'seconds':time.perf_counter()-t,'scope':'Full local geometry grid; all 3000 bodies occlude. Separate isolated footprints for M−33/M−27. No brightness, light, observed black pixels, fitting or registration changes.'}
 (OUT/'model-geometry.json').write_text(json.dumps(record,indent=2)+'\n');print(record['seconds'],len(xy),error)
if __name__=='__main__':main()
