"""Compact original-pixel diagnostic figures, no external assets or viewer framework."""
from .common import *
import csv,json,html
from collections import defaultdict,Counter
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})

def main():
 g,b,p,ss=inputs();obs={o['id']:o for o in g['observations']};im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');led=read(OUT/'index-ledger.json.gz')['comparisons'];cases=read(OUT/'backward-cases.json.gz')['cases'];frozen=read(OUT/'frozen-ledger.json.gz')['models'];novel=read(OUT/'novel-windings.json.gz')['alternatives'];phys=read(OUT/'physical-summary.json');matched=read(OUT/'matched-physical.json.gz');novphys=read(OUT/'novel-physical.json.gz');traversals=read(OUT/'traversal-summary.json')['runs']+read(OUT/'extra-traversal-summary.json')['runs']
 # Distinguish coverage levels for every integer, including odd counts.
 coverage=[]
 for n in range(2000,3601):
  trials=[z for z in phys['trials'] if z['N']==n]+[z for z in matched['trials'] if z['N']==n]+[z for z in novphys['trials'] if z['N']==n]
  sparse=n in phys['counts_sparse_native'] or any('sparse_ownership' in z for z in matched['trials'] if z['N']==n)
  full=n in phys['counts_full_support_and_local_reflection'] or any(z['N']==n for z in matched['native']) or any(z['N']==n and 'full_native_ownership' in z for z in novphys['trials'])
  refl=n in phys['counts_full_support_and_local_reflection'];coverage.append(dict(N=n,algebraic=True,physical_trials=len(trials),sparse_native=sparse,full_native_support=full,local_native_reflections=refl,certified_trials=sum(z.get('contact',{}).get('certified',False) for z in trials),photo_witness=any(n in [abs(int(np.dot(s['H'],w))) for w in [(7,6),(6,7)]] for s in ss+[z['state'] for z in novel])))
 with open(OUT/'count-coverage.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
 save(OUT/'coverage-summary.json',dict(integer_counts=1601,constructed_counts=sum(z['physical_trials']>0 for z in coverage),constructed_trials=sum(z['physical_trials'] for z in coverage),sparse_native_counts=sum(z['sparse_native'] for z in coverage),full_native_support_counts=[z['N'] for z in coverage if z['full_native_support']],local_native_reflection_counts=[z['N'] for z in coverage if z['local_native_reflections']],photo_witness_counts=[z['N'] for z in coverage if z['photo_witness']],policy='Full-native support is every retained original support pixel, with all scene bodies; shaded native reflections cover only local declared targets. No whole-photo rendered fit.'))
 fig,ax=plt.subplots(3,1,figsize=(10,7),layout='constrained')
 for name,col in [('A','#0072b2'),('B','#d55e00')]:
  rr=next(z['rows'] for z in led if z['alternative']==1 and z['family']==name and z['direction']==1);ax[0].plot([r['k'] for r in rr],[r['delta'] for r in rr],'.',ms=2,label=name,color=col)
  for direction,style in [(1,'-'),(-1,'--')]:
   z=next(z for z in led if z['alternative']==1 and z['family']==name and z['direction']==direction);first=z['first'];rr=[r for r in z['rows'] if first['first']['k']-35<r['k']<first['first']['k']+35];ax[1].plot([r['k']-first['first']['k'] for r in rr],[r['delta'] for r in rr],style+'o',ms=3,label=f'{name} direction {direction}')
 ax[0].set(title='Closest winding: a local decision becomes a persistent ±1 index offset',ylabel='Alternative − primary index');ax[0].legend();ax[0].axvline(1739,color='k',ls=':',lw=1);ax[0].set_xlabel('Unwrapped relative index from C-1302-0316, forward')
 ax[1].set(title='First departure in each direction (zero aligned to first differing support)',xlabel='Relative index minus first-departure index',ylabel='Signed index difference');ax[1].axvline(0,color='k',ls=':');ax[1].legend(ncol=2)
 nz=next(z for z in novel if z['H']==[214,176]);rr=next(z['rows'] for z in nz['comparisons'] if z['family']=='B' and z['direction']==1);ax[2].plot([r['k'] for r in rr],[r['delta'] for r in rr],'.',ms=2,color='#009e73');ax[2].axvline(97,color='k',ls=':');ax[2].set(title='Unusual H=(214,176): first −7 at k=97, accumulated −175 later',xlabel='Forward relative index, family B',ylabel='Alternative − primary index')
 fig.savefig(OUT/'index-errors.png');plt.close(fig)
 # Frozen geometry: discrete addresses, visible region, reflection, and center proxy kept separate.
 fig,axs=plt.subplots(4,1,figsize=(10,9),layout='constrained')
 for model,col in zip(frozen,['#0072b2','#d55e00']):
  f=next(z for z in model['families'] if z['family']==model['selected_family']);rr=f['rows'];name=model['label'].replace('R321-','');valid=[r for r in rr if r['delta'] is not None and -50<=r['k']<=230]
  axs[0].plot([r['k'] for r in valid],[r['delta'] for r in valid],'.-',ms=3,label=name,color=col)
  for field,ax in [('center_to_support_proxy_px',axs[1]),('visible_region_distance_px',axs[2]),('reflection_error_px',axs[3])]:
   pp=[r for r in rr if -50<=r['k']<=230 and r[field] is not None];ax.plot([r['k'] for r in pp],[r[field] for r in pp],'.-',ms=3,label=name,color=col)
 for ax in axs:ax.axvline(31,color='#0072b2',ls=':',lw=.8);ax.axvline(20,color='#d55e00',ls=':',lw=.8);ax.grid(alpha=.15)
 axs[0].set(ylabel='Modal − assigned index',title='Frozen models: earliest modal ownership disagreement precedes large later drift');axs[0].legend();axs[1].set_ylabel('Center→support proxy px');axs[2].set_ylabel('Visible region distance px');axs[3].set(ylabel='Reflection error px',xlabel='Signed relative string index from C-1302-0316 (model-selected family)');fig.savefig(OUT/'frozen-errors.png');plt.close(fig)
 fig,axs=plt.subplots(2,1,figsize=(10,5),layout='constrained');axs[0].plot([2000,3600],[0,0],lw=7,color='#aaa',label='All integer counts: arithmetic')
 for y,key,label,col in [(1,'physical_trials','Constructed / contact checked','#0072b2'),(2,'sparse_native','Sparse native support','#56b4e9'),(3,'full_native_support','Full native support pixels','#009e73'),(4,'local_native_reflections','Local native reflections','#d55e00')]:
  nn=[r['N'] for r in coverage if r[key]];axs[0].scatter(nn,[y]*len(nn),marker='|',s=100,color=col,label=label)
 axs[0].set_yticks(range(5),['Arithmetic','Constructed','Sparse rays','Full support','Local reflections']);axs[0].set_xlim(1980,3620);axs[0].set_title('Count coverage; no count excluded by sparse screening alone')
 for label,col in [('certified-separation','#0072b2'),('demonstrated-interpenetration','#d55e00'),('unresolved','#999')]:
  rr=[r for r in phys['trials'] if r.get('contact',{}).get('classification')==label];axs[1].scatter([r['N'] for r in rr],[r.get('sparse_native',{}).get('assigned_fraction',0) for r in rr],s=15,alpha=.6,label=label,color=col)
 axs[1].set(xlabel='Total bead count N',ylabel='Sparse assigned ownership',title='Frozen shared-camera diagnostic extrapolation (topology-incompatible trials labeled in data)');axs[1].legend(fontsize=8);fig.savefig(OUT/'wide-count.png');plt.close(fig)
 # Native crops and SVG overlays keep the unmodified image directly available.
 crops=[];panels=[]
 def panel(name,box,states,focus=None):
  box=tuple(map(int,box));im.crop(box).save(OUT/f'{name}-native.png');crops.append(dict(name=name,box=box));w,h=box[2]-box[0],box[3]-box[1];cards=[]
  for label,state in [('Original photograph',None)]+states:
   shapes=[]
   if state:
    co=canonical(state);edges={}
    for r in state['path']:
     if r.get('skipped'):continue
     for a,bb,d in p['patches'][r['window']][r['patch']]['edges']:
      edges[(a,bb,tuple(d))]=(a,bb,d)
    for a,bb,d in edges.values():
     aa,cc=obs[a]['xy'],obs[bb]['xy']
     if all(box[0]<=q[0]<=box[2] and box[1]<=q[1]<=box[3] for q in [aa,cc]):
      col={(1,0):'#00cfff',(0,1):'#76ff57',(1,-1):'#ffba50'}[tuple(d)];shapes.append(f'<line x1="{aa[0]-box[0]}" y1="{aa[1]-box[1]}" x2="{cc[0]-box[0]}" y2="{cc[1]-box[1]}" stroke="{col}" stroke-width="1.3"><title>{a} → {bb}: {d}</title></line>')
    for oid in focus or []:
     if oid not in co:continue
     x,y=obs[oid]['xy'];k=int(np.dot(co[oid],[6,7]));shapes.append(f'<circle cx="{x-box[0]}" cy="{y-box[1]}" r="5" fill="none" stroke="white"/><text x="{x-box[0]+6}" y="{y-box[1]-5}" fill="white" font-size="9" stroke="#111" stroke-width=".3">{k}<title>{oid} at {x:.3f},{y:.3f}; family B index {k}</title></text>')
   cards.append(f'<figure><figcaption>{html.escape(label)}</figcaption><svg viewBox="0 0 {w} {h}" role="img" aria-label="{name} {html.escape(label)}"><image href="{name}-native.png" width="{w}" height="{h}"/><g class="overlay">{"".join(shapes)}</g></svg></figure>')
  panels.append('<div class="panels">'+''.join(cards)+'</div>')
 panel('closest-first',(1600,1500,1830,1670),[('H=(214,201)',ss[0]),('H=(215,200)',ss[1])],['C-1721-1566','K-1740-1575','MAT25-K-1719-1592'])
 panel('upper-first',(1510,215,1810,420),[('Primary',ss[0]),('H=(214,176)',nz['state'])],['NEW-1621-315','C-1559-0252'])
 lower=next((s for s in ss if s['H']==[213,201]));panel('lower-first',(1050,2820,1290,3030),[('Primary',ss[0]),('H=(213,201)',lower)],['NEW-1132-2925'])
 # Backward trace: downstream common offset -> transition -> agreeing predecessor.
 chosen=next(z for z in led if z['alternative']==1 and z['family']=='B' and z['direction']==1);r=next(r for r in chosen['rows'] if r['k']>2400 and r['delta']!=0);targets=[('late-offset',r),('first-branch',chosen['first']['first']),('last-agreement',chosen['first']['last_agreement'])];trace=[]
 for name,r in targets:
  x,y=r['xy'];box=[max(0,int(x)-100),max(0,int(y)-85),min(im.width,int(x)+100),min(im.height,int(y)+85)];im.crop(box).save(OUT/f'{name}-native.png');crops.append(dict(name=name,box=box));trace.append(f'<figure><figcaption>{name}: {r["id"]}<br>k={r["k"]}, Δ={r["delta"]}, ({x:.2f},{y:.2f})</figcaption><img src="{name}-native.png" alt="Original photo {name}"></figure>')
 # Model first and predecessor markers, with later target in a common original crop.
 box=(1260,215,1535,355);im.crop(box).save(OUT/'model-trace-native.png');crops.append(dict(name='model-trace',box=list(box)));model=next(z for z in frozen if z['label']=='R321-geometry-best');first=model['first_forward'];points=[('Last agreement',first['last_agreement']),('First +6',first['first'])];texts=[]
 for label,r in points:
  x,y=r['xy'];texts.append(f'<circle cx="{x-box[0]}" cy="{y-box[1]}" r="7" fill="none" stroke="white"/><text x="{x-box[0]-30}" y="{y-box[1]-10}" fill="white" font-size="9" stroke="#111" stroke-width=".3">{label}: k={r["k"]}</text>')
 model_svg=f'<svg viewBox="0 0 275 140" role="img" aria-label="Frozen model first disagreement on original pixels"><image href="model-trace-native.png" width="275" height="140"/><g class="overlay">{"".join(texts)}</g></svg>'
 # Whole-circuit positional overview colors changed supports, retaining original image.
 co=canonical(ss[0]);ca=canonical(ss[1]);dots=[]
 for oid in co.keys()&ca.keys():
  x,y=obs[oid]['xy'];col='#ff5353' if co[oid]!=ca[oid] else '#00d4dd';dots.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{col}"/>')
 overview=f'<svg class="overview" viewBox="0 0 {im.width} {im.height}" role="img" aria-label="Whole photograph closest alternative consequences"><image href="../../../beads-photo-2.jpg" width="{im.width}" height="{im.height}"/><g class="overlay">{"".join(dots)}</g></svg>'
 table=''.join(f'<tr><td>{r["label"]}</td><td>{r["seed"]}</td><td>{r["direction"]}</td><td>{r["normalized_H"]}</td><td>{"complete" if r["completed"] else "incomplete"}</td><td>{r.get("changed_coordinates")}</td><td>{r["seconds"]:.2f}</td></tr>' for r in traversals)
 cov=read(OUT/'coverage-summary.json');text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R329 — trace disagreement backward</title><style>body{{max-width:1150px;margin:24px auto;padding:0 16px;font:16px system-ui;background:#13151a;color:#eee}}a{{color:#88d8ff}}img,svg{{max-width:100%;height:auto}}figure{{margin:0}}figcaption{{margin:8px 0;font-size:14px}}.panels,.trace{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}button{{padding:10px;margin:8px 0}}table{{border-collapse:collapse;font-size:13px}}td,th{{padding:7px;border-bottom:1px solid #555;text-align:left}}.scroll{{overflow:auto}}.overview{{max-width:340px}}@media(max-width:700px){{.panels,.trace{{grid-template-columns:1fr}}}}</style><h1>Trace the disagreement backward</h1><p>R329: relative zero is C-1302-0316 at (1301.854,315.585). One connected photographic lattice; conditional alternatives retained. No final N or period adopted.</p><p><a href="../../R329_REPORT.md">Report</a> · <a href="../../R329_REPRODUCE.md">Reproduce</a> · <a href="index-ledger.json.gz">Index ledger</a> · <a href="backward-cases.json.gz">Counterfactual cases</a> · <a href="verification.json">Verification</a></p><button id="toggle">Toggle photograph overlays</button><h2>First branch, then persistent offset</h2><p>Closest H=(215,200) first differs at C-1721-1566, B k=1739 (A k=1745). Last B agreement: MAT25-K-1719-1592, k=1733. A single-patch change fails; windows124–126 together replay to closure in about0.012s. The cause of the alternative offset is localized; the physically correct branch remains unresolved.</p>{panels[0]}<img src="index-errors.png" alt="Index discrepancy versus explicit relative index, closest and unusual windings"><h2>Backward trace on original pixels</h2><div class="trace">{''.join(trace)}</div><p>These are repeated observations along two saved paths, not independent confirmations. Cyan/green/orange lines show the three primitive directions. Labels in crops are family B indices; original IDs are in tooltips and ledgers.</p><h2>Frozen physical model: the first +6 occurs much earlier</h2><p>N3000 first disagrees at K-1398-0248, A k=31; preceding agreement is C-1391-0312, k=26. A +6 suffix improves some ownership but breaks three photo links. Small global phase/station controls do not explain the whole failure. Uniform spacing interpenetrates and is not rendered.</p>{model_svg}<img src="frozen-errors.png" alt="Separate signed address, center proxy, visible region and reflection errors"><h2>Unusual complete winding retained</h2><p>H=(214,176), conditional N2554/2516, first differs at NEW-1621-315 (B k=97, −7), then accumulates −175. Replacing windows10–34 reproduces it from the original seed. It retains900 supports but has worse shared-shape penalties and only about3% whole-photo support ownership in the tested own-count models.</p>{panels[1]}<h2>Lower-bend alternative</h2>{panels[2]}<h2>Wide count coverage</h2><p>All1601 integers screened; {cov['constructed_counts']} distinct counts physically constructed in {cov['constructed_trials']} trials. {len(cov['full_native_support_counts'])} counts receive full original-support ownership; {len(cov['local_native_reflection_counts'])} receive local native reflection evaluation. These are limited shared-camera constructions, not optimized count exclusions. P252 has no inference weight.</p><img src="wide-count.png" alt="Arithmetic, physical and native count coverage"><p><a href="count-coverage.csv">Every count and evaluation level</a> · <a href="matched-physical.json.gz">Models with their own H-derived N</a> · <a href="periods.json.gz">Frozen color-period constraints</a></p><h2>Whole-circuit checks and ambiguity</h2><div class="scroll"><table><tr><th>Run</th><th>Seed</th><th>Direction</th><th>H</th><th>Return</th><th>Changed coordinates</th><th>Seconds</th></tr>{table}</table></div><p>Inward forward fails even at width128. Inward reverse width128 selects H=(213,202). Forced R328-path replay succeeds in both directions from that seed: beam pruning remains a real limitation. Alternate routes reuse photographed neighbors; return subsets reuse starting evidence.</p>{overview}<p>Red supports differ in the closest alternative; cyan supports retain the primary coordinates. The 900-support graph is a working hypothesis, not ground truth. <a href="alternative-routes.json">Alternate routes</a> · <a href="return-subsets.json">Return subsets</a> · <a href="novel-windings.json.gz">Unusual saved paths</a></p><script>document.querySelector('#toggle').onclick=()=>document.querySelectorAll('.overlay').forEach(e=>e.style.display=e.style.display==='none'?'':'none');</script></html>'''
 (OUT/'index.html').write_text(text);save(OUT/'native-crops.json',dict(image_sha256=sha(ROOT/'beads-photo-2.jpg'),crops=crops));print('REVIEW',cov,flush=True)
if __name__=='__main__':main()
