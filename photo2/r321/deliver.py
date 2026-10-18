"""Compact photographic and actual-geometry contact review."""
import shutil,html
import numpy as np
from photo2.r297.common import ROOT,read,save,utc
from photo2.r306.evidence import load
from photo2.r320 import deliver as old_draw
from .model import Chain
from .packing import curvature
from .evaluate import Evidence,evaluate,errors
from .verify import verify
OUT=ROOT/'photo2/r321/results'

def select():
 rows=[read(f) for f in sorted((OUT/'trials').glob('*.gz'))]
 good=[r for r in rows if r['parameters'].get('packing_spacing')=='curvature-density' and r.get('optical',{}).get('emax_px') is not None and r['optical']['geometry']['dual_count']==0 and r['optical']['geometry']['material_omission']<.15]
 primary=min(good,key=lambda r:(r['optical']['geometry']['seam_conflict_fraction'],r['optical']['emax_px']))
 reflection=min(good,key=lambda r:r['optical']['emax_px']);rescue=rows[98]
 models=[dict(label=label,trial=r['id'],parameters=r['parameters'],optical=r['optical'],summary=r['construction']['summary']) for label,r in [('geometry-best',primary),('photo-sized-rescue',rescue),('reflection-tradeoff',reflection)]]
 save(OUT/'selection.json',dict(models=models,policy='Photo-sized certified density-law models, zero dual claims, omission<15%; primary minimizes confident separator conflicts then Emax. Reflection-minimax alternative retained. This ranking is a diagnostic, not acceptance or adoption.'))
 return models

def contact_figure(s,label):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 k=curvature(s);records=read(OUT/f'{label}-neighbor-gaps.json.gz');lookups={r['offset']:r['pairs'] for r in records};centers=[int(np.argmin(abs(k))),int(np.argmax(abs(k)))];fig=plt.figure(figsize=(12,5));tables=[]
 # Exact legacy rounded annular surface, revolved then rigidly transformed.
 gamma=np.linspace(0,2*np.pi,65);ang=np.linspace(0,2*np.pi,49)
 rho=s.radius*(.57+.086*np.sign(np.cos(gamma))+.344*np.cos(gamma));x=s.radius*(.7/.43*s.axial)*(.086*np.sign(np.sin(gamma))+.344*np.sin(gamma))
 local=np.stack([np.broadcast_to(x[:,None],(65,49)),rho[:,None]*np.cos(ang),rho[:,None]*np.sin(ang)],axis=-1)
 from photo2.r295.geometry import AXES
 for panel,i in enumerate(centers):
  ax=fig.add_subplot(1,2,panel+1,projection='3d');frame=np.stack([s.g[key][i] for key in AXES]);table=[]
  for off in [0,-7,-6,-1,1,6,7]:
   j=(i+off)%s.n;color='#ce5670' if off==0 else '#9aafbd'
   if off:
    rr=lookups[abs(off)][i if off>0 else j];near=rr['upper']<=.02*s.radius;color='#39a578' if near else '#e2ad46';table.append(dict(offset=off,physical_index=int(s.indices[j]),lower=rr['lower'],upper=rr['upper'],classification='near contact (upper <= .02r)' if near else 'positive gap'))
   world=s.centers[j]+sum(local[...,a,None]*s.g[key][j] for a,key in enumerate(AXES));q=(world-s.centers[i])@frame.T
   ax.plot_surface(q[...,0],q[...,1],q[...,2],color=color,alpha=.62,linewidth=.1,rstride=2,cstride=2,shade=True)
   pt=(s.centers[j]-s.centers[i])@frame.T;ax.text(*pt,str(off),fontsize=9)
  ax.set_title(('Least curved' if panel==0 else 'Most curved')+f' |k|={abs(k[i]):.5f}\nindex {s.indices[i]}');ax.set_xlabel('hole axis');ax.set_ylabel('body plane');ax.set_zlabel('body plane');ax.set_box_aspect((1,1,1));ax.view_init(elev=25,azim=35)
  tables.append(dict(center=int(s.indices[i]),curvature=float(k[i]),pairs=table))
 fig.suptitle('Actual rounded glass surfaces; green near contact, amber gap. No force model.');fig.tight_layout();fig.savefig(OUT/'contact-geometry.png',dpi=150);plt.close(fig)
 save(OUT/'contact-geometry.json',tables)
 # Measured gap versus local curvature/phase: no universal missing-contact loss.
 fig,axs=plt.subplots(1,3,figsize=(12,3.3));bins=[]
 for ax,row in zip(axs,records):
  lo=np.array([v['lower'] for v in row['pairs']]);hi=np.array([v['upper'] for v in row['pairs']]);crowding=k*s.p['minor']*np.sin(s.phase)
  ax.scatter(crowding,hi/s.radius,s=2,alpha=.4);ax.set_title(f'+{row["offset"]} measured upper gaps');ax.set_xlabel('signed inner-side metric R k sin(phase)');ax.set_ylabel('gap / radius')
  groups={}
  for name,mask in [('near_straight',abs(k)<=np.quantile(abs(k),.2)),('strong_bend_inner',(abs(k)>=np.quantile(abs(k),.8))&(crowding>0)),('strong_bend_outer',(abs(k)>=np.quantile(abs(k),.8))&(crowding<=0))]:groups[name]=dict(pairs=int(mask.sum()),lower_median=float(np.median(lo[mask])),upper_median=float(np.median(hi[mask])),near_contact_count=int(np.sum(hi[mask]<=.02*s.radius)))
  bins.append(dict(offset=row['offset'],groups=groups))
 fig.tight_layout();fig.savefig(OUT/'curvature-gaps.png',dpi=150);plt.close(fig);save(OUT/'curvature-gaps.json',bins)

def main():
 data=load()[0];ev=Evidence(data);models=select();old_draw.OUT=OUT;verification=[]
 for m in models:
  label=m['label'];p=m['parameters'];ep=read(OUT/f'epoch-N{p["count"]}-h{p["hand"]}.json.gz');o,cache,sh=evaluate(p,data,ev,'pilot',ev.obs,ep['mapping'],keep=True);s=cache['s']
  assert o['physical']['certified'];save(OUT/f'{label}-model.json.gz',dict(**m,optical_recomputed=o,positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),frames={k:v.tolist() for k,v in s.g.items()},projected=s.pc.tolist())))
  np.savez_compressed(OUT/f'{label}-raster.npz',xy=cache['xy'],owner=cache['tr']['owner'],boundary=cache['boundary'],intensity=sh['intensity'])
  old_draw.draw(label,o,cache['xy'],cache['boundary']);verification.append(verify(p,data,label))
  mapping=ev.assignment(s,ev.obs);pred={int(k):v for k,v in o['predictions'].items()};control=errors(ev.obs,mapping['mapping'],pred)
  save(OUT/f'{label}-assignment-control.json',dict(frozen_emax=o['emax_px'],same_geometry_new_support_map=control,new_mapping=mapping,geometric_gain=False,policy='Predictions outside the frozen-map target pool may be unavailable; missing remains infinite, never favorable.'))
 save(OUT/'verification.json',dict(models=verification,utc=utc()))
 contact_figure(Chain(models[1]['parameters'],data),'photo-sized-rescue')
 print('DELIVERY',[(m['label'],m['trial'],m['optical']['emax_px']) for m in models],flush=True)
if __name__=='__main__':main()
