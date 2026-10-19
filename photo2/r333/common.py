"""Immutable R332 adapter; all locations are measured supports, never centers."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r333-mpl')
from collections import Counter,defaultdict
import numpy as np
from scipy.spatial import cKDTree
from photo2.r332.common import ROOT,read,save,sha,representative
COLORS=['red','yellow','black']
BASE='d726ef590e56bfaa29f54f8ba142a054ba88019e'

def artifact(path):
    return __import__('pathlib').Path(os.environ.get('R333_RUN_ROOT',ROOT/'photo2/r333'))/path

def dataset():
    g=read(ROOT/'photo2/r332/results/graph.json.gz');obs={o['id']:o for o in g['observations']};co={r['id']:tuple(r['ab']) for r in g['coordinates']};ids=sorted(co)
    old=read(ROOT/'photo2/r328/results/graph.json.gz');oldnames=sorted(old['stations_px']);xy=np.array([obs[o]['xy'] for o in oldnames]);tree=cKDTree(xy)
    period=old['period_px'];st=[]
    for o in ids:
        if o in old['stations_px']:st.append(old['stations_px'][o]%period);continue
        dd,jj=tree.query(obs[o]['xy'],k=3);values=np.array([old['stations_px'][oldnames[j]]%period for j in jj]);values-=np.rint((values-values[0])/period)*period
        st.append(float(np.average(values,weights=1/np.maximum(dd,1)))%period)
    st=np.array(st);b=np.minimum((st/period*12).astype(int),11);ab=np.array([co[o] for o in ids]);c=np.array([COLORS.index(obs[o]['color']) for o in ids]);w=np.where(c==2,.55,1.)
    for i,o in enumerate(ids):
        if 'provisional' in str(obs[o]).lower():w[i]=.25
    return g,obs,co,ids,ab,c,w,b,st

def fit_keys(keys,c,w,train,parent=None):
    keys=np.asarray(keys);size=int(keys.max())+1;cc=np.bincount(keys[train]*3+c[train],weights=w[train],minlength=size*3).reshape(size,3);base=np.bincount(c[train],weights=w[train],minlength=3)+1;base/=base.sum()
    prior=np.tile(base,(size,1)) if parent is None else parent
    theta=(cc+3*prior)/(cc.sum(1)[:,None]+3)
    return theta,base,cc

def cross_predict(keys,c,w,blocks,guard=0,parent_keys=None):
    n=len(c);pr=np.zeros((n,3));base=np.zeros_like(pr)
    for block in range(12):
        tr=~np.isin(blocks,[(block+d)%12 for d in range(-guard,guard+1)]);te=blocks==block
        if parent_keys is not None:
            par,_,_=fit_keys(parent_keys,c,w,tr)
            # Each fine key has a unique parent. Populate by observed key mapping.
            mapping=np.zeros(int(np.max(keys))+1,int)
            for f,p in zip(keys,parent_keys):mapping[f]=p
            th,ba,cc=fit_keys(keys,c,w,tr,par[mapping]);th=(cc+par[mapping])/(cc.sum(1)[:,None]+1)
        else:th,ba,_=fit_keys(keys,c,w,tr)
        pr[te]=th[keys[te]];base[te]=ba
    return pr,base

def score(pr,base,c,w,b):
    ll=np.log(pr[np.arange(len(c)),c])-np.log(base[np.arange(len(c)),c]);per=[float(np.average(ll[b==j],weights=w[b==j])) for j in range(12)]
    return dict(gain_nats=float(np.average(ll,weights=w)),agreement=float(np.mean(pr.argmax(1)==c)),per_section=per,section_se=float(np.std(per,ddof=1)/np.sqrt(12)))

def spatial_keys(ab,translation=(16,16)):
    # Quotient by ONE spatial translation, retaining the transverse coordinate.
    # A string period adds a second identification; this model does not.
    da,db=translation;t=np.floor_divide(ab[:,0],da);rep=ab-t[:,None]*np.array([da,db]);unique={v:j for j,v in enumerate(sorted(set(map(tuple,rep))))};return np.array([unique[tuple(v)] for v in rep]),rep
