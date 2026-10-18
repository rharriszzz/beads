"""Conservative visible-surface tests on frozen R314 photographic evidence.

Different pigment cores support distinct beads. Same-color disconnected cores
alone are NOT proof of separate beads; dark valleys are never hard separators.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r315.model import refined_trace
from .common import *

class Evidence:
    def __init__(self,epoch):
        m=dict(np.load(ROOT/'photo2/r314/evidence/maps.npz'));doc=read(ROOT/'photo2/r314/evidence/freeze.json')
        pts=np.array([o['point'] for o in epoch['observations']]);lo=np.floor(pts.min(0)-28).astype(int);hi=np.ceil(pts.max(0)+28).astype(int)
        self.origin=lo;self.shape=tuple((hi-lo+1)[::-1]);yy,xx=np.indices(self.shape);self.xy=np.c_[xx.ravel()+lo[0],yy.ravel()+lo[1]]
        x,y=lo-m['origin'];h,w=self.shape;sl=np.s_[y:y+h,x:x+w]
        self.m={k:m[k][sl] for k in ['core','material','paper','color','roi']};self.seams=m['seams'][:,y:y+h,x:x+w]
        self.cores=[r for r in doc['regions'] if np.sum(self.m['core']==r['label'])>=20]
        self.brackets=[]
        for row in m['external_brackets']:
            by,bx,axis,sign,gap=map(int,row);bx+=int(m['origin'][0]-lo[0]);by+=int(m['origin'][1]-lo[1])
            if 3<=bx<w-3 and 3<=by<h-3:self.brackets.append([by,bx,axis,sign,gap])
        save(OUT/'evidence-policy.json',dict(origin=lo.tolist(),shape=[int(v) for v in self.shape],cores=self.cores,brackets=self.brackets,source_sha256=sha(ROOT/'photo2/r314/evidence/maps.npz'),policy='Frozen positive pigment interiors, red/yellow chromatic seams and material-to-paper uncertainty brackets only. No complete outlines or dark-valley separators. Distinct-color cores support distinct beads; same-color pairs remain unresolved. 20 pixels and 25% of each core for substantial dual ownership; core crossing uses 2px eroded interiors. Thresholds are conservative engineering diagnostics, not calibrated confidence intervals.'))
    def measure(self,s,detail=False,owner=None,unknown=None):
        if owner is None:
            tr=refined_trace(s,self.xy);owner=tr['owner'].reshape(self.shape);unknown=tr['unknown'].reshape(self.shape)
        known=~unknown;valid=known&self.m['roi'];core=self.m['core'];rows=[];claims={};cross=[]
        bd=np.zeros(self.shape,bool)
        for ax in [0,1]:
            sl=[slice(None)]*2;ss=sl.copy();sl[ax]=slice(None,-1);ss[ax]=slice(1,None);sl,ss=tuple(sl),tuple(ss)
            hit=(owner[sl]!=owner[ss])&known[sl]&known[ss]&((owner[sl]>=0)|(owner[ss]>=0));bd[sl]|=hit;bd[ss]|=hit
        for c in self.cores:
            mask=(core==c['label']);total=int(mask.sum());js,nn=np.unique(owner[mask&known&(owner>=0)],return_counts=True);order=np.argsort(-nn)
            rr=[dict(index=int(s.indices[j]),pixels=int(n),fraction=float(n/total)) for j,n in zip(js[order],nn[order])]
            for r in rr:
                if r['pixels']>=20 and r['fraction']>=.25:claims.setdefault(r['index'],[]).append(dict(id=c['id'],color=c['color'],**r))
            deep=ndi.binary_erosion(mask,iterations=2);crossing=int((bd&deep).sum());den=int(deep.sum())
            rows.append(dict(id=c['id'],color=c['color'],pixels=total,owners=rr,modal_fraction=rr[0]['fraction'] if rr else 0,crossing_pixels=crossing,deep_pixels=den,crossing_fraction=crossing/max(1,den)))
        dual=[]
        for idx,rs in claims.items():
            for i,a in enumerate(rs):
                for b in rs[i+1:]:
                    if a['color']!=b['color']:dual.append(dict(index=idx,a=a,b=b))
        seam=[]
        for ax in [0,1]:
            dy,dx=(0,1) if ax==0 else (1,0)
            for y,x in zip(*np.where(self.seams[ax])):
                ya,yb,xa,xb=y-3*dy,y+3*dy,x-3*dx,x+3*dx
                if min(ya,yb,xa,xb)<0 or max(ya,yb)>=self.shape[0] or max(xa,xb)>=self.shape[1]:continue
                a,b=owner[ya,xa],owner[yb,xb]
                if known[ya,xa] and known[yb,xb]:seam.append(dict(xy=(self.origin+[x,y]).tolist(),conflict=bool(a>=0 and a==b),owners=[int(s.indices[a]) if a>=0 else None,int(s.indices[b]) if b>=0 else None]))
        brackets=[]
        for y,x,ax,sign,gap in self.brackets:
            dy,dx=(0,sign) if ax==0 else (sign,0);ts=np.arange(-24,gap+25);yy=y+ts*dy;xx=x+ts*dx
            v=(yy>=0)&(yy+dy>=0)&(yy<self.shape[0])&(yy+dy<self.shape[0])&(xx>=0)&(xx+dx>=0)&(xx<self.shape[1])&(xx+dx<self.shape[1]);ts,yy,xx=ts[v],yy[v],xx[v]
            good=(owner[yy,xx]>=0)&(owner[yy+dy,xx+dx]<0)&known[yy,xx]&known[yy+dy,xx+dx];dist=np.maximum(np.maximum(-ts,ts-(gap-1)),0);ix=np.flatnonzero(good)
            brackets.append(dict(material=(self.origin+[x,y]).tolist(),paper=(self.origin+[x+gap*dx,y+gap*dy]).tolist(),uncertainty_px=gap,excess_px=float(dist[ix].min()) if len(ix) else None))
        ds=[r['excess_px'] for r in brackets if r['excess_px'] is not None]
        result=dict(cores=rows,dual_claims=dual,dual_count=len(dual),seam_conflict_fraction=float(np.mean([r['conflict'] for r in seam])) if seam else 0.,seam_samples=len(seam),paper_fraction=float(np.mean(owner[self.m['paper']&valid]>=0)),material_omission=float(np.mean(owner[self.m['material']&valid]<0)),core_crossing_fraction=sum(r['crossing_pixels'] for r in rows)/max(1,sum(r['deep_pixels'] for r in rows)),bracket_p95=float(np.percentile(ds,95)) if ds else None,bracket_missing=sum(r['excess_px'] is None for r in brackets),unknown_evidence=int((unknown&(self.m['material']|self.m['paper']|(core>0))).sum()))
        if detail:result.update(seams=seam,brackets=brackets);return result,dict(owner=owner,unknown=unknown,boundary=bd,xy=self.xy,origin=self.origin)
        return result

def gate(m,b):
    fail=[]
    # Every strong contradiction remains visible, even when already in baseline.
    for k,t in [('paper_fraction',.002),('seam_conflict_fraction',.02),('core_crossing_fraction',.02)]:
        if m[k]>b[k]+t:fail.append(k)
    if m['dual_count']>b['dual_count']:fail.append('dual_core_claims')
    if m['bracket_missing']>b['bracket_missing']:fail.append('missing_boundary')
    if m['bracket_p95'] is not None and b['bracket_p95'] is not None and m['bracket_p95']>b['bracket_p95']+.5:fail.append('external_boundary')
    if m['unknown_evidence']:fail.append('unknown_evidence')
    for a,z in zip(m['cores'],b['cores']):
        if a['modal_fraction']<z['modal_fraction']-.03:fail.append('core_loss:'+a['id'])
    return dict(passed=not fail,failures=fail,absolute_clear=(m['dual_count']==0 and m['seam_conflict_fraction']<=.1 and m['paper_fraction']<=.005 and m['core_crossing_fraction']<=.03),policy='Baseline non-regression screen; passing does not erase inherited contradictions or establish accurate geometry.')
