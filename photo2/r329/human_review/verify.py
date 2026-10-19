"""Check paired-image identity, local numerical comparisons and preserved science."""
from .investigate import *
import hashlib,re,subprocess

def main():
 t=time.perf_counter();receipt={};base=read(HERE/'baseline.json');allowed={'photo2/r329/ILLUSTRATED_GUIDE.md','photo2/r329/photographic_diagnostics/README.md'}
 for name,sha in base.items():
  raw=(ROOT/name).read_bytes()
  if name in allowed:
   before=subprocess.check_output(['git','show','98251e67:'+name]);assert hashlib.sha256(before).hexdigest()==sha
   old=before.decode();new=raw.decode();insert='\n**Current review status:' if 'ILLUSTRATED' in name else '\n**For the current decision list,'
   start=new.index(insert);end=new.index('**\n',start+3)+3;rest=new[:start]+new[end:];assert rest==old
  else:assert hashlib.sha256(raw).hexdigest()==sha,name
 receipt['preserved_baseline_files']=len(base)-len(allowed);receipt['guide_changes_only_added_status_links']=2
 d=read(HERE/'investigation.json.gz');fitchecks=0;errors={}
 for name,c in d['cases'].items():
  alt=c['config']['alt'];states=['working',alt]
  for f in c['shared_anchor_fits']:
   assert set(f['train']).isdisjoint(f['targets']);assert all(OBS[o]['color']!='black' for o in f['train'])
   assert all(CO['working'][o]==CO[alt][o] for o in f['train'])
   mm={o:measure(OBS[o],f['radius'],f['threshold'])[0] for o in f['train']};ab=np.array([CO[f['state']][o] for o in f['train']]);origin=ab.mean(0);X=design(ab-origin,f['degree']);Y=np.array([mm[o] for o in f['train']]);coef=np.linalg.pinv(X)@Y
   for o,v in f['targets'].items():
    pred=design(np.array([CO[f['state']][o]])-origin,f['degree'])@coef;assert np.allclose(pred[0],v['prediction'],atol=1e-7);assert abs(np.linalg.norm(pred[0]-v['measured'])-v['error'])<1e-7;fitchecks+=1
  for r in c['transfer_controls']:
   a=r['results']['working']['errors'];b=r['results'][alt]['errors'];assert max(b)<min(a) if name=='G' else max(a)<min(b)
  fixed=c['stable_shared_anchors'];ab=np.array([CO['working'][o] for o in fixed]);rank=int(np.linalg.matrix_rank(design(ab-ab.mean(0),2)));errors[name]=dict(whole_row_controls=len(c['transfer_controls']),fits=len(c['shared_anchor_fits']),fixed_anchor_count=len(fixed),quadratic_rank=rank)
 assert errors['H']['quadratic_rank']==4
 assert sum(not r['shared'] for r in d['cases']['G']['reference_audit'])==0
 assert sum(not r['shared'] for r in d['cases']['H']['reference_audit'])==1
 receipt['prediction_rows_checked_with_pseudoinverse']=fitchecks;receipt['cases']=errors
 photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');figs=read(HERE/'figures.json');imagechecks=[]
 for f in figs:
  a,b=f['panels'];assert a['crop']==b['crop'] and a['scale']==b['scale'] and a['labels']==b['labels'];assert f['disputed_connections_per_panel']==1
  raw=np.array(Image.open(HERE/'images'/(f['case'].lower()+'-raw.png')));assert np.array_equal(raw,np.array(photo.crop(a['crop'])))
  for panel in [a,b]:
   co=CO[panel['state']]
   for key in ['source','target']:assert panel[key+'_index']==sum(co[panel[key]][j]*[6,7][j] for j in [0,1])
   assert panel['delta']==(np.array(co[panel['target']])-co[panel['source']]).tolist()
   for fam,seq,steps in f['rows']:
    for o,q,n in zip(seq,seq[1:],steps):
     delta=np.array(co[q])-co[o];expected=[0,0];expected[fam]=n;assert delta.tolist()==expected
  im=np.array(Image.open(HERE/'images'/f['file']));w,h=f['photo_dimensions'];panels=[im[p['origin'][1]:p['origin'][1]+h,p['origin'][0]:p['origin'][0]+w] for p in [a,b]];diff=np.any(panels[0]!=panels[1],axis=2)
  # All changed photograph pixels must be confined to the one highlighted edge.
  xy={l['id']:np.array(l['xy']) for l in a['labels']};q=np.array([xy[p[key]] for p in [a,b] for key in ['source','target']]);q=(q-np.array(a['crop'][:2]))*a['scale'];lo=np.floor(q.min(0)-30).astype(int);hi=np.ceil(q.max(0)+30).astype(int)
  yy,xx=np.nonzero(diff);assert len(xx)>0;assert (xx>=lo[0]).all() and (xx<=hi[0]).all() and (yy>=lo[1]).all() and (yy<=hi[1]).all()
  imagechecks.append(dict(case=f['case'],identical_photo_and_scale=True,identical_labels=True,changed_photo_pixels=int(diff.sum()),all_changes_within_highlight=True,sha256=hashlib.sha256((HERE/'images'/f['file']).read_bytes()).hexdigest()))
 receipt['paired_images']=imagechecks
 docs=[ROOT/'photo2/r329/HUMAN_DECISIONS_REQUIRED.md',HERE/'SUPPLEMENT.md',ROOT/'photo2/r329/ILLUSTRATED_GUIDE.md',ROOT/'photo2/r329/photographic_diagnostics/README.md'];links=0
 for doc in docs:
  for href in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',doc.read_text()):
   if href.startswith(('http:','https:')):continue
   path=href.partition('#')[0]
   if not path:continue
   assert (doc.parent/path).exists(),href;links+=1
 report=docs[0].read_text();assert report.startswith('# Questions for Human Review\n');assert '**No human decisions required yet.**' in report
 receipt.update(local_links=links,report_words=len(report.split()),visual_review='Both images separately inspected at reading size; one candidate connection changes, shared numbered references and raw pixels remain fixed. Not an independent human scientific certification.',passed=True,seconds=time.perf_counter()-t)
 (HERE/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
