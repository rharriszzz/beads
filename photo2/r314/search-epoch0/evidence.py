"""R314-v1 independently supported transitions; old material/core arrays unchanged."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r297.common import ROOT,read,save,sha,photo,utc
from photo2.r290.detector import fields,shifted

OUT=ROOT/'photo2/r314'

def persistence(mask,axis):
    # Two independent tangent rows; no center sample can witness itself.
    normal=1 if axis==0 else 0
    nearby=ndi.maximum_filter1d(mask.astype(np.uint8),3,axis=normal,mode='constant')>0
    dy,dx=(1,0) if axis==0 else (0,1)
    return mask&shifted(nearby,dy,dx)&shifted(nearby,-dy,-dx)

def freeze():
    old=ROOT/'photo2/r313/evidence';m=dict(np.load(old/'maps.npz'));doc=read(old/'freeze.json')
    _,rgb,_=photo();x,y=m['origin'];h,w=m['shape'];_,ff=fields(rgb[y:y+h,x:x+w]);col=m['color'];roi=m['roi'];paper=m['paper']
    edges=[];seams=[];external=[];before=[];after=[]
    for axis,q in enumerate(ff):
        dy,dx=(0,1) if axis==0 else (1,0)
        ca=shifted(col,-3*dy,-3*dx);cb=shifted(col,3*dy,3*dx)
        dark=(q['drop']>=.35*1.15)&(q['coherence']>=.8)&(q['dark_context']>0)&(np.maximum(q['side_a'],q['side_b'])-q['center']>=.012*1.15)
        chrom=(q['color']>=.25*1.15)&(q['color_coherence']>=.8)&(ca>0)&(cb>0)&(ca!=cb)
        raw=((ca>0)|(cb>0))&(dark|chrom)&ndi.binary_erosion(roi,iterations=9)
        persistent=persistence(raw,axis)
        z=np.maximum(q['drop']*q['coherence'],q['color']*q['color_coherence']);ridge=z>=ndi.maximum_filter1d(z,3,axis=1 if axis==0 else 0)-1e-12
        supported=persistent&ridge;edges.append(supported);seams.append(supported&chrom)
        pa=np.zeros(roi.shape,bool);pb=pa.copy()
        for d in range(4,9):pa|=shifted(paper,-d*dy,-d*dx);pb|=shifted(paper,d*dy,d*dx)
        external.append(supported&(((ca>0)&pb)|((cb>0)&pa)))
        before.append(int((raw&ridge).sum()));after.append(int(supported.sum()))
    brackets=[]
    for axis in range(2):
        dy,dx=(0,1) if axis==0 else (1,0)
        for sign in [-1,1]:
            sy,sx=sign*dy,sign*dx;active=m['material']&~shifted(m['material'],sy,sx)&ndi.binary_erosion(roi,iterations=14)
            for gap in range(2,13):
                hit=active&shifted(paper,gap*sy,gap*sx)
                # Neighboring tangent lines independently support the material and paper sides.
                tdy,tdx=dx,dy
                endpoint_support=m['material']&shifted(paper,gap*sy,gap*sx)
                nearby=ndi.maximum_filter1d(endpoint_support.astype(np.uint8),3,axis=1 if axis==0 else 0)>0
                hit&=shifted(nearby,tdy,tdx)&shifted(nearby,-tdy,-tdx)
                for yy,xx in zip(*np.where(hit)):brackets.append([int(yy),int(xx),axis,sign,gap])
                active&=~shifted(paper,gap*sy,gap*sx)&~shifted(m['material'],gap*sy,gap*sx)
    m['external_brackets']=np.asarray(brackets,dtype=np.int32).reshape(-1,5)
    m['old_edges']=m['edges'];m['old_seams']=m['seams'];m['edges']=np.array(edges);m['seams']=np.array(seams);m['external']=np.array(external)
    dest=OUT/'evidence';dest.mkdir(parents=True,exist_ok=True);np.savez_compressed(dest/'maps.npz',**m)
    doc.update(version='R314-v1',utc=utc(),parent_maps_sha256=sha(old/'maps.npz'),maps_sha256=sha(dest/'maps.npz'),persistence_before=before,persistence_after=after,external_samples=int(np.sum(external)),external_brackets=len(brackets),external_policy='Conservative material-to-paper boundary brackets, 2..12px apart, independently supported on both tangent neighbors; all intervening locations allowed. Exact location and any intermediate black body remain unknown.',color_seam_samples=int(np.sum(seams)),dark_valleys='Retained in old_seams and edges; not asserted to be physical interfaces',sources_r314={str(p.relative_to(ROOT)):sha(p) for p in [__file__ and ROOT/'photo2/r314/evidence.py',ROOT/'beads-photo-2.jpg']})
    save(dest/'freeze.json',doc);print({k:doc[k] for k in ['persistence_before','persistence_after','external_samples','external_brackets','color_seam_samples']},flush=True)
    return m,doc
if __name__=='__main__':freeze()
