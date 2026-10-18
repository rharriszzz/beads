"""Compact offline review: original-photo overlays and six task views."""
import html
from PIL import Image,ImageDraw,ImageFont
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .coupled import *
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)

def main():
 g=read(OUT/'graph.json');a=read(OUT/'analysis.json');im=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB');op={o['id']:o for o in g['observations']};ns={n['id']:n for n in g['intersections']};pal={'F0':'#00e9ff','F1':'#55ff40','difference':'#e8c260'}
 def whole(name,draw):
  v=im.copy();d=ImageDraw.Draw(v);draw(d);v.resize((1270,1591),Image.Resampling.LANCZOS).save(OUT/name)
 def tracks(d):
  for e in g['graph']['edges']:
   if e['family']=='difference':continue
   d.line([tuple(op[e[k]]['xy']) for k in ['source','target']],fill=pal[e['family']],width=3)
  for b in a['chart_breaks']:
   x,y=b['xy'];d.ellipse((x-20,y-20,x+20,y+20),outline='orange',width=4)
 whole('A-diagonals.png',tracks)
 def indices(d):
  for i,n in enumerate(g['intersections']):
   x,y=n['xy'];color={'black':'#333333','red':'#ff3d50','yellow':'#ffe300'}[n['color']];d.ellipse((x-5,y-5,x+5,y+5),fill=color,outline='white',width=1)
   if n['component'] is not None and i%7==0:
    label=f"{n['component']}:{n['conditional_indices']['A']}";d.text((x+8,y-15),label,font=SMALL,fill='white',stroke_width=2,stroke_fill='black')
 whole('B-indexed.png',indices)
 validated={r['node'] for r in read(OUT/'validation.json')['associations'] if r['status']=='unambiguous proximity association'}
 def coverage(d):
  for n in ns.values():
   x,y=n['xy'];c='#00eaff' if n['id'] in validated else '#3dff79' if n['component'] is not None else '#ff9e28';d.ellipse((x-7,y-7,x+7,y+7),outline=c,width=3)
  for b in a['chart_breaks']:
   x,y=b['xy'];d.rectangle((x-17,y-17,x+17,y+17),outline='#ff9e28',width=4)
  for w in g['windows']:
   if not w['hypotheses']:
    x,y=w['center'];d.rectangle((x-90,y-90,x+90,y+90),outline='white',width=5)
 whole('C-coverage.png',coverage)
 m=read(OUT/'R321-photo-sized-rescue-frozen.json.gz');idx={k:j for j,k in enumerate(m['positions']['indices'])};pc=np.array(m['positions']['projected']);wrong={o for e in m['edge_comparison'] if e['status']=='disagrees' for o in [e['source'],e['target']]}
 def frozen(d):
  for c in m['components']:
   for i,(oid,k) in enumerate(c['best']['mapping'].items()):
    if i%2:continue
    p=np.array(op[oid]['xy']);q=pc[idx[k]];color='#ff4c58' if oid in wrong else '#20e6ff'
    if np.linalg.norm(q-p)<100:d.line([tuple(p),tuple(q)],fill=color,width=2)
    d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),outline=color,width=2)
    if np.linalg.norm(q-p)<100:d.line([(q[0]-4,q[1]),(q[0]+4,q[1])],fill='white',width=2)
 whole('D-frozen-model.png',frozen)
 # Important bridge: untouched original above an annotated primary graph.
 box=(1470,180,1840,410);crop=im.crop(box);annot=crop.copy();d=ImageDraw.Draw(annot)
 for e in g['graph']['edges']+g['graph']['unresolved_edges']:
  p,q=[np.array(op[e[k]]['xy'])-box[:2] for k in ['source','target']]
  if all(0<=p[j]<crop.size[j] and 0<=q[j]<crop.size[j] for j in range(2)):d.line([tuple(p),tuple(q)],fill=pal[e['family']] if e['status']=='accepted conditional' else 'orange',width=1)
 for pair in read(OUT/'bridge.json')['summary']:
  for oid in pair['pair']:
   x,y=np.array(op[oid]['xy'])-box[:2];d.ellipse((x-5,y-5,x+5,y+5),outline='white',width=1)
 out=Image.new('RGB',(1110,1420),'#181818');out.paste(crop.resize((1110,690),Image.Resampling.NEAREST),(0,0));out.paste(annot.resize((1110,690),Image.Resampling.NEAREST),(0,730));out.save(OUT/'bridge-original-and-graph.png');crop.save(OUT/'bridge-raw.png')
 fs=read(OUT/'fit-summary.json');before=read(OUT/f'fit-trials/{fs["baseline100"]:04}.json.gz');after=read(OUT/f'fit-trials/{fs["final100"]:04}.json.gz')
 box=(1100,195,1535,390);panels=[]
 for label,r,file in [('Before',before,'baseline100-raster.npz'),('After',after,'final100-raster.npz')]:
  view=im.crop(box);d=ImageDraw.Draw(view);ra=dict(np.load(OUT/file));xy=ra['xy'];owner=ra['owner'];key=xy[:,1].astype(int)*2540+xy[:,0].astype(int);bd=np.zeros(len(key),bool)
  for off in [1,2540]:
   j=np.searchsorted(key,key+off);ii=np.flatnonzero(j<len(key));jj=j[ii];eq=key[jj]==key[ii]+off;ii,jj=ii[eq],jj[eq];hit=owner[ii]!=owner[jj];bd[ii[hit]]=True
  for x,y in xy[bd]-box[:2]:
   if 0<=x<view.width and 0<=y<view.height:d.point((x,y),fill='#00ffff')
  for row in r['native']['rows']:
   x,y=np.array(row['observed'])-box[:2];d.ellipse((x-2,y-2,x+2,y+2),outline='yellow')
   if row['predicted'] is not None:
    q=np.array(row['predicted'])-box[:2];d.line([(x,y),tuple(q)],fill='#ff44dd',width=1)
  view=view.resize((870,390),Image.Resampling.NEAREST);panel=Image.new('RGB',(870,430),'#181818');panel.paste(view,(0,40));ImageDraw.Draw(panel).text((12,8),f'{label}: max {r["native"]["emax_px"]:.3f}px',font=FONT,fill='white');panels.append(panel)
 out=Image.new('RGB',(1740,430));out.paste(panels[0],(0,0));out.paste(panels[1],(870,0));out.save(OUT/'E-coupled-before-after.png')
 es=read(OUT/'expand-summary.json');b200=read(OUT/f'fit-trials/{fs["baseline200"]:04}.json.gz');best200=read(OUT/f'expand-trials/{es["best"]:04}.json.gz') if es['best'] is not None else b200
 fig,axs=plt.subplots(1,2,figsize=(12,3.5))
 for ax,bb,aa,title in [(axs[0],before,after,'100 consecutive modeled addresses'),(axs[1],b200,best200,'200 addresses; bridge excluded from fitting')]:
  for r,label,col in [(bb,'before','#666666'),(aa,'after','#c62858')]:
   rr=sorted(r['native']['rows'],key=lambda z:z['index']);ax.plot([z['index'] for z in rr],[z['error_px'] for z in rr],'.-',label=label,color=col,lw=1)
  ax.set_title(title);ax.set_xlabel('conditional physical index');ax.set_ylabel('reflection displacement (px)');ax.legend();ax.grid(alpha=.2)
 fig.tight_layout();fig.savefig(OUT/'E-error-versus-index.png',dpi=150);plt.close(fig)
 perf=read(OUT/'performance-control.json');keys=['decode_preprocess','observations','spectral','joint_candidates','beam_transport','row_switch_skip_and_photographic_checks'];fig,axs=plt.subplots(1,2,figsize=(12,4));x=np.arange(len(keys));axs[0].barh(x-.18,[perf['original']['stages'][k] for k in keys],height=.35,label='original');axs[0].barh(x+.18,[perf['optimized']['stages'][k] for k in keys],height=.35,label='cached');axs[0].set_yticks(x,labels=['preprocess','support extraction','local FFT','joint hypotheses','beam + transport','link photo checks']);axs[0].set_xlabel('seconds, full circuit');axs[0].legend();plan=read(OUT/'runtime-plan.json');axs[1].bar([r['name'] for r in plan['scenarios']],[r['total_hours'] for r in plan['scenarios']],color='#357e99');axs[1].set_ylabel('serial hours');axs[1].set_title('Planning workloads, not convergence forecasts');fig.tight_layout();fig.savefig(OUT/'F-performance.png',dpi=150);plt.close(fig)
 captions=[('A-diagonals.png','A. Both photographic diagonal families around the full circuit. Orange rings mark incompatible chart overlaps; gaps remain.'),('B-indexed.png','B. Observed colors and sparse component:A labels. Each component has its own origin. Full inventory and B/reversal alternatives are in graph.json.'),('C-coverage.png','C. Cyan: associated R161 reference; green: conditional index; orange: unresolved support or chart boundary; white window: no retained lattice. None of the green observations has new external accuracy validation.'),('D-frozen-model.png','D. Frozen N2800 comparison, every second observation shown. Dots are observed supports; white ticks are projected model centers, not measured centers. Red marks endpoints of model/photo index disagreements. Each disconnected component has a separately fitted discrete origin.'),('bridge-original-and-graph.png','Bridge: untouched native RGB above, primary graph below. Additional 160/240/280px contexts retain alternatives for both circled pairs. The primary acceptance at the first pair is contested; fitting stops at x1510.'),('E-coupled-before-after.png','E. Before/after 100-address native visibility boundaries and reflection vectors. Cyan includes modeled hole/occlusion edges; only supported photographic brackets are scored. All 2800 bodies remain present.'),('E-error-versus-index.png','E. Fixed-map errors remain large. The 200-address fit excludes ambiguous bridge correspondences and retains unlabelled surface guards beyond it.'),('F-performance.png','F. Matched photographic cache optimization and serial runtime scenarios. Evaluation costs are measured; iteration budgets and overhead allowances are assumptions.')]
 links=[('../../R324_REPORT.md','Report'),('../../R324_REPRODUCE.md','Reproduce'),('graph.json','Full graph'),('bridge.json','Bridge alternatives'),('analysis.json','Coverage / drift / feedback'),('frozen-summary.json','Frozen models'),('fit-summary.json','100-address fit'),('expand-summary.json','200-address fit'),('runtime-plan.json','Runtime model'),('verification.json','Photo verification'),('physical-verification.json','Physical verification')]
 page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R324 full circuit</title><style>body{font:16px system-ui;background:#181818;color:#eee;max-width:1350px;margin:20px auto;padding:0 14px}img{max-width:100%;height:auto}figure{margin:24px 0}a{color:#7de3ff}p{max-width:1000px}</style><h1>R324 — full photographic circuit, conditional sections</h1><p>187 windows cover the whole circuit; 886 conditionally indexed supports, 1,722 conditional links, 25 components. N and full-loop closure remain unknown. R161: 25/25 interior beads, 45/45 interior links, zero wrong interior links. Both requested bridge continuations remain ambiguous. Small physical fit gains do not establish a reconstruction.</p><p>'+' · '.join(f'<a href="{p}">{html.escape(t)}</a>' for p,t in links)+'</p>'
 for file,text in captions:page+=f'<figure><figcaption>{html.escape(text)}</figcaption><a href="{file}"><img src="{file}" alt="{html.escape(text)}"></a></figure>'
 (OUT/'index.html').write_text(page+'</html>');print('REVIEW',len(captions),flush=True)
if __name__=='__main__':main()
