"""Direct visible-owner objective on immutable native photographic evidence."""
import time
import numpy as np
from scipy import ndimage as ndi
from photo2.r312.fast import Chain
from photo2.r311.model import Legacy

D=36.878  # historical remote dimension, normalization only, not exact local diameter

def scene(parameters,data,implementation='R306'):
    return Legacy(parameters,data) if implementation=='R297' else Chain(parameters,data)

def boundaries(owner,unknown):
    out=np.zeros((2,*owner.shape),bool)
    out[0,:,:-1]=(owner[:,:-1]!=owner[:,1:])&((owner[:,:-1]>=0)|(owner[:,1:]>=0))
    out[1,:-1,:]=(owner[:-1,:]!=owner[1:,:])&((owner[:-1,:]>=0)|(owner[1:,:]>=0))
    out&=~ndi.binary_dilation(unknown,iterations=1)[None]
    out[:,:3]=False;out[:,-3:]=False;out[:,:,:3]=False;out[:,:,-3:]=False
    return out

def distances(mask):
    return ndi.distance_transform_edt(~mask) if mask.any() else np.full(mask.shape,100.)

def stats(values):
    a=np.asarray(values,float)
    return dict(n=len(a),rms_px=float(np.sqrt(np.mean(a*a))) if len(a) else None,p95_px=float(np.percentile(a,95)) if len(a) else None,max_px=float(a.max()) if len(a) else None)

class Objective:
    def __init__(self,maps,document):
        self.m=maps;self.doc=document;self.shape=tuple(maps['shape']);self.xy=maps['xy']
        self.photo_dist=np.array([distances(e) for e in maps['edges']])
        self.regions=[]
        for r in document['regions']:
            self.regions.append((r,np.flatnonzero(maps['core'].ravel()==r['label'])))
        self.tiles=[];h,w=self.shape
        for y in range(0,h,40):
            for x in range(0,w,40):
                mask=np.zeros(self.shape,bool);mask[y:y+40,x:x+40]=True;mask&=maps['roi']
                if np.sum(mask&maps['material'])<12 and np.sum(mask&maps['edges'].any(0))<5:continue
                self.tiles.append((x,y,mask))

    def measure(self,owner,unknown,indices,split=0,detail=False):
        m=self.m;own=np.asarray(owner).reshape(self.shape);un=np.asarray(unknown).reshape(self.shape)
        valid=m['roi']&(m['split']==split);mat=m['material']&valid;paper=m['paper']&valid
        # Unknown rays cannot receive either foreground or background credit.
        missing=(own<0)|un;intrusion=(own>=0)|un
        omission=float(missing[mat].mean()) if mat.any() else 0.
        background=float(intrusion[paper].mean()) if paper.any() else 0.
        edge=boundaries(own,un);dd=np.array([distances(e) for e in edge])
        observed=m['edges']&valid[None];seams=m['seams']&valid[None]
        forward=dd[observed];separation=dd[seams]
        # Reverse evidence is conditional on nearby supported photographic transitions.
        # Missing unsupported contours carry no fabricated distance-to-contour loss.
        reverse_mask=edge&valid[None]&(self.photo_dist<=8)
        reverse=self.photo_dist[reverse_mask]
        # Incorrect new cuts through confident colored material have independent evidence.
        cut=edge.any(0)&ndi.binary_erosion(mat)&(self.photo_dist.min(0)>3)
        core_rows=[];frag=[];outside=0
        for r,ix in self.regions:
            if r['split']!=split:continue
            oo=own.ravel()[ix];uu=un.ravel()[ix];ids,c=np.unique(oo[(oo>=0)&~uu],return_counts=True)
            j=int(ids[c.argmax()]) if len(c) else -1;n=len(ix)
            modal=float(c.max()/n) if len(c) else 0.;fragmented=float((c.sum()-c.max())/n) if len(c) else 0.
            # A hole/missing core and split ownership both fail one-body material explanation.
            frag.append(1-modal)
            index=int(indices[j]) if j>=0 else None
            yy,xx=np.unravel_index(ix,self.shape);near=np.zeros(self.shape,bool)
            near[max(0,yy.min()-8):yy.max()+9,max(0,xx.min()-8):xx.max()+9]=True
            d=dd[m['edges']&near[None]&valid[None]]
            core_rows.append(dict(id=r['id'],point=r['point'],pixels=n,index=index,modal_fraction=modal,
                unexplained_fraction=float(np.mean((oo<0)|uu)),fragmented_fraction=fragmented,
                substantial_owners=int(np.sum(c>=.10*n)),outside_200=index is not None and not -100<=index<=99,
                boundary=stats(d),error=1-modal+(float(np.percentile(d,95))/D if len(d) else 0)))
        # Same body on both sides of a supported seam is an ownership conflict.
        crossing=[]
        for axis in range(2):
            dy,dx=(0,1) if axis==0 else (1,0)
            a=ndi.shift(own,(3*dy,3*dx),order=0,mode='constant',cval=-1)
            b=ndi.shift(own,(-3*dy,-3*dx),order=0,mode='constant',cval=-1)
            cross=(a==b)&(a>=0)
            crossing.extend(cross[seams[axis]].tolist())
        cross=float(np.mean(crossing)) if crossing else 0.
        f=np.array(frag);meanfrag=float(f.mean()) if len(f) else 0.;worstfrag=float(np.percentile(f,90)) if len(f) else 0.
        # Distance has a 3px deadband reflecting native profile uncertainty, not hard truth.
        fd=float(np.mean(np.maximum(forward-3,0))/D) if len(forward) else 0.
        rd=float(np.mean(np.maximum(reverse-3,0))/D) if len(reverse) else 0.
        tail=float(np.mean(np.sort(np.maximum(forward-3,0))[-max(1,len(forward)//10):])/D) if len(forward) else 0.
        cutfrac=float(cut.sum()/max(1,mat.sum()))
        score=2*omission+2*background+meanfrag+worstfrag+fd+rd+tail+.5*cross+2*cutfrac
        mapped=np.full(own.shape,-100000,int);good=own>=0;mapped[good]=indices[own[good]]
        result=dict(score=score,material_pixels=int(mat.sum()),material_explained_pixels=int((~missing&mat).sum()),
            material_unexplained_pixels=int((missing&mat).sum()),material_unexplained_percent=100*omission,
            background_pixels=int(paper.sum()),background_intrusion_pixels=int((paper&intrusion).sum()),background_intrusion_percent=100*background,
            modal_ownership_percent=100*(1-meanfrag),fragmentation_p90_percent=100*worstfrag,
            supported_transition_alignment=stats(forward),supported_separation_alignment=stats(separation),
            reverse_supported_boundary=stats(reverse),seam_same_owner_percent=100*cross,
            unsupported_predicted_edge_samples=int((edge&valid[None]&~reverse_mask).sum()),
            predicted_cuts_through_material_pixels=int(cut.sum()),unknown_rays=int(un[valid].sum()),
            material_explained_by_200_pixels=int((mat&~missing&(mapped>=-100)&(mapped<=99)).sum()),
            material_explained_by_context_pixels=int((mat&~missing&((mapped<-100)|(mapped>99))).sum()),
            score_terms=dict(omission=2*omission,paper=2*background,mean_core_loss=meanfrag,tail_core_loss=worstfrag,forward=fd,reverse=rd,tail_distance=tail,seam=.5*cross,material_cut=2*cutfrac))
        if detail:
            tiles=[]
            for x,y,mask in self.tiles:
                mask=mask&valid;mm=mask&mat;pp=mask&paper;ee=m['edges']&mask[None]
                if mm.sum()<12 and ee.sum()<5:continue
                e=dd[ee];merr=float(missing[mm].mean()) if mm.any() else 0.;perr=float(intrusion[pp].mean()) if pp.any() else 0.
                loc=(m['origin']+np.array([x+20,y+20])).tolist()
                tiles.append(dict(point=loc,box=[int(m['origin'][0]+x),int(m['origin'][1]+y),int(m['origin'][0]+x+40),int(m['origin'][1]+y+40)],material_pixels=int(mm.sum()),unexplained_percent=100*merr,background_intrusion_percent=100*perr,transition=stats(e),severity=merr+perr+(float(np.percentile(e,95))/D if len(e) else 0)))
            result.update(cores=core_rows,regions=sorted(tiles,key=lambda r:-r['severity']),worst_cores=sorted(core_rows,key=lambda r:-r['error'])[:20])
        return result

    def evaluate(self,p,data,implementation='R306',detail=False):
        began=time.monotonic();s=scene(p,data,implementation);placed=time.monotonic()
        cert=s.certify(iterations=150,witnesses=detail);checked=time.monotonic()
        r=dict(feasible=cert['certified'],physical=cert,parameters=p,implementation=implementation)
        if cert['certified']:
            tr=s.trace(self.xy);rendered=time.monotonic()
            r['development']=self.measure(tr['owner'],tr['unknown'],s.indices,0,detail)
            if detail:r['comparison']=self.measure(tr['owner'],tr['unknown'],s.indices,1,True)
            r['profile']=dict(geometry=placed-began,contact=checked-placed,render=rendered-checked,measure=time.monotonic()-rendered)
        else:tr=None
        r['seconds']=time.monotonic()-began
        return r,s,tr
