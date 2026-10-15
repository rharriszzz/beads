"""R291 binary target objective with independently controllable evidence costs."""
import numpy as np
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow,breadth_first_order
from photo2.r291.detector import PARAMETERS

def solve(m,core,access,peers,*,strength=1.,stop_penalty=4.5,peer_capacity=10**8,local_relax=None,seam_background=None):
    lum=m['lum'];h,w=lum.shape;n=h*w;idx=np.arange(n).reshape(h,w);source=n;sink=n+1
    match=m['match'];rel=m['reliability'];floor=m['model']['floor_Y'];diffuse=max(m['model']['diffuse_Y'],.008)
    illuminated=np.clip((lum-floor)/max(diffuse-floor,.005),0,1)
    dark=np.clip((floor-lum)/max(floor,.004),0,1)
    logit=3*match*rel*illuminated*m['model']['continuation_exposure']-3*(1-match)*rel-2*dark
    stop=stop_penalty
    if local_relax is not None:stop=np.where(local_relax,2.7,stop_penalty)
    logit-=stop*(~access)
    weight=PARAMETERS['unary_weight']*strength
    cost_fg=weight*np.logaddexp(0,-logit);cost_bg=weight*np.logaddexp(0,logit)
    row=[];col=[];values=[]
    for i,(a,b) in enumerate([(idx[:,:-1],idx[:,1:]),(idx[:-1,:],idx[1:,:])]):
        f=m['fields'][i];continuity=f['D_continuity']*(1-np.clip(f['A_dark_seam']*2,0,1))
        cap=PARAMETERS['pairwise_weight']*(.015+np.exp(-PARAMETERS['conductance_gain']*f['combined'])+.5*continuity)
        cap=cap[:,:-1] if i==0 else cap[:-1,:];v=np.maximum(1,np.rint(cap*10000)).astype(np.int64).ravel()
        row.extend([a.ravel(),b.ravel()]);col.extend([b.ravel(),a.ravel()]);values.extend([v,v])
    source_cap=np.maximum(0,np.rint(cost_bg*10000)).astype(np.int64).ravel();sink_cap=np.maximum(0,np.rint(cost_fg*10000)).astype(np.int64).ravel()
    source_cap[core.ravel()]=10**8
    frame=np.unique(np.r_[idx[0],idx[-1],idx[:,0],idx[:,-1]]);sink_cap[frame]=10**8
    for p in peers:
        if not p['supported']:continue
        x,y=np.rint(p['local_point']).astype(int)
        if 0<=x<w and 0<=y<h and not core[y,x]:sink_cap[idx[y,x]]=peer_capacity
    if seam_background is not None:
        protected=seam_background & ~core
        sink_cap[protected.ravel()]=10**8
    row.extend([np.full(n,source),idx.ravel()]);col.extend([idx.ravel(),np.full(n,sink)]);values.extend([source_cap,sink_cap])
    graph=coo_matrix((np.concatenate(values),(np.concatenate(row),np.concatenate(col))),shape=(n+2,n+2),dtype=np.int64).tocsr()
    flow=maximum_flow(graph,source,sink);residual=graph-flow.flow;residual.data=(residual.data>0).astype(np.int8);residual.eliminate_zeros()
    reached=breadth_first_order(residual,source,directed=True,return_predecessors=False);owned=np.zeros(n+2,bool);owned[reached]=True;mask=owned[:n].reshape(h,w)
    # Only source-connected visible material is this invocation's candidate.
    labels,_=ndi.label(mask,np.ones((3,3)));ids=np.unique(labels[core]);mask=np.isin(labels,ids[ids>0])
    return mask

