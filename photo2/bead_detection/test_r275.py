"""R275 band selection, preservation, honest fallback measurements and ownership."""
import unittest
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from .centerline_r275 import Band
from .recover_r275 import Recovery,resolve
from .coverage_r272 import detect
from .hue_r274 import refine
from .synthetic_r274 import scenes
from .interiors_r273 import pixels,mask_local

class RecoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rgb,cls.truth,cls.colors=next((rgb,t,c) for n,rgb,t,c in scenes() if n=='h18-h42-equal-Y')
  cls.band=Band(np.array([[69.,0.],[69.,127.]]));cls.base=detect(cls.rgb)[0];beads,loc,*_=refine(cls.rgb,cls.rgb,cls.base);cls.old=dict(beads=beads,locations=loc);cls.engine=Recovery(cls.rgb,cls.rgb,cls.base,cls.band)
 def test_band_fixed_not_detection_dependent(self):
  b=Band(np.array([[50.,0.],[50.,100.]]));self.assertTrue(b.qualifies([76,50])['in_band']);self.assertFalse(b.qualifies([76.2,50])['in_band']);self.assertTrue(b.qualifies([80,50],{'runs':[[50,60,65]]})['in_band']);self.assertFalse(b.qualifies([80,50],{'runs':[[50,65,70]]})['in_band'])
 def test_preserves_all_successes(self):
  b,l,r=resolve([],self.old,self.band);self.assertEqual(b,self.old['beads']);self.assertEqual(l,self.old['locations'])
 def test_same_highlight_not_extra_bead(self):
  r=deepcopy(self.old['beads'][0]);r['id']='new-alias';b,l,rows=resolve([r],self.old,self.band);self.assertEqual(len(l),len(self.old['locations']));self.assertEqual(rows[0]['status'],'duplicate removed')
 def test_different_color_overlap_is_unresolved(self):
  r=deepcopy(self.old['beads'][0]);r['id']='conflict';r['color']='yellow' if r['color']=='red' else 'red';b,l,rows=resolve([r],self.old,self.band);self.assertEqual(b,self.old['beads']);self.assertEqual(rows[0]['status'],'still unresolved')
 def test_new_support_measured_and_separate(self):
  rows=[self.engine.interior(r,layered=True) for r in self.base];b,l,dec=resolve(rows,dict(beads=[],locations=[]),self.band);self.assertEqual(len(b),2)
  seen=set()
  for r in b:
   pts=pixels(r);self.assertFalse(pts&seen);seen|=pts;self.assertEqual(len(pts),r['region']['pixel_count']);self.assertEqual(ndi.label(mask_local(r['region']))[1],1);self.assertTrue(pixels(r,'bright_patch')<=pts);np.testing.assert_allclose(np.array(list(pts)).mean(axis=0),r['region']['centroid']);self.assertTrue(all(self.truth[y,x]>0 for x,y in pts))
 def test_all_windows_raw_scan_and_stable_ids(self):
  peaks=self.engine.peaks();self.assertEqual({r['window'] for r in peaks},{5,7,9});self.assertEqual(len({r['id'] for r in peaks}),len(peaks));self.assertTrue(self.engine.peaks(black=True));self.assertEqual(peaks,self.engine.peaks())
 def test_shaded_same_color_retreat_keeps_automatic_anchor(self):
  for name,rgb,t,c in scenes():
   if name not in ('h18-h18-shading','h42-h42-shading'):continue
   e=Recovery(rgb,rgb,detect(rgb)[0],self.band);r=e.new_colored([66,64],'E5',True);r=e.interior(r,layered=True);self.assertTrue(r['accepted']);self.assertGreater(r['region']['pixel_count'],400);body=t[r['brightest']['y'],r['brightest']['x']];self.assertTrue(all(t[y,x]==body for x,y in pixels(r)));self.assertEqual(r['interior_seed'],[66,64])
 def test_empty_upstream_palette_learned_from_image(self):
  e=Recovery(self.rgb,self.rgb,[],self.band,pale=True);self.assertEqual(set(e.palette),{'red','yellow'})
 def test_arclength_wrap_and_individual_steps(self):
  from .spacing_r275 import projection,circular_intervals
  angles=np.linspace(0,2*np.pi,721)[:-1];curve=100*np.c_[np.cos(angles),np.sin(angles)];p,length=projection([[100,0],[0,100],[-100,0],[0,-100]],curve)
  np.testing.assert_allclose([r['angle_degrees'] for r in p],[0,90,180,270],atol=1e-8);rr=[dict(id=str(i),**r) for i,r in enumerate(p)];g=circular_intervals(rr,length);np.testing.assert_allclose([r['step_degrees'] for r in g],90,atol=1e-8);self.assertAlmostEqual(sum(r['step_degrees'] for r in g),360)
 def test_single_double_groups_do_not_insert_beads(self):
  from .groups_r275 import stations
  rows=[dict(id=str(i),arc_px=s,angle_degrees=s/100*360,signed_distance=d) for i,(s,d) in enumerate([(0,-9),(2,9),(25,0),(49,-9),(51,9),(75,0)])];g=stations(rows,100,5,2);self.assertEqual(sorted(z['members'] for z in g),[1,1,2,2]);self.assertEqual(sum(z['members'] for z in g),len(rows));self.assertEqual({id for z in g for id in z['ids']},{r['id'] for r in rows});self.assertAlmostEqual(sum(z['step_degrees'] for z in g),360)
 def test_dominance_keeps_separate_dark_bodies(self):
  from .dominance_r275 import suppress
  from .coverage_r272 import black_region,Parameters
  from matplotlib.colors import hsv_to_rgb
  from .climb_r268 import background
  yy,xx=np.mgrid[:128,:128]
  for separate in (False,True):
   rgb=np.full((128,128,3),hsv_to_rgb([.83,.42,.78]));centers=[(58,55),(61,68)] if not separate else [(50,60),(64,60)]
   bodies=((xx-60)**2+(yy-61)**2<=22**2) if not separate else (((xx-50)**2+(yy-60)**2<=5**2)|((xx-64)**2+(yy-60)**2<=5**2))
   value=np.full(xx.shape,.055)
   for (cx,cy),strength,width in zip(centers,(.85,.33),(5,3)):value+=strength*np.exp(-((xx-cx)**2+(yy-cy)**2)/width)
   rgb[bodies]=np.repeat(value[:,:,None],3,axis=2)[bodies];rgb=np.rint(rgb*255).astype(np.uint8);e=Recovery(rgb,rgb,[],self.band);rows=[]
   for i,(x,y) in enumerate(centers):
    r=dict(id='test-'+str(i),anchor=[x,y],reasons=[],accepted=False,confidence={});black_region(r,rgb,rgb,e.hsv,e.nhsv,e.lum,e.paper,Parameters());self.assertTrue(r['accepted']);r['inventory_number']=i+1;rows.append(r)
   loc=[dict(id=r['id'],point=r['brightest'],color='black',inventory_number=i+1,bright_patch=r['bright_patch'],source='automatic fixture') for i,r in enumerate(rows)];result,dec=suppress(dict(beads=rows,locations=loc),rgb,rgb,self.band);self.assertEqual(len(result['beads']),2 if separate else 1)
 def test_superseded_color_fragment_cannot_reappear(self):
  prior=deepcopy(self.old['beads'][0]);current=deepcopy(prior);current['color']='black';current['brightest']['luminance']=4*prior['brightest']['luminance'];current['region']['runs']=[]
  location=deepcopy(self.old['locations'][0]);location['color']='black';location['point']=current['brightest'];old=dict(beads=[current],locations=[location],superseded_beads=[prior]);alias=deepcopy(prior);alias['id']='different-window-alias';b,l,rows=resolve([alias],old,self.band);self.assertEqual(rows[0]['status'],'duplicate removed');self.assertIn('superseded-colored-reflection-alias',rows[0]['reasons']);self.assertEqual(len(l),1)
 def test_colored_secondary_patch_requires_continuous_body(self):
  from types import SimpleNamespace
  from .homogeneous_r275 import guard_ownership
  e=SimpleNamespace(paper=np.zeros((40,40),int),lum=np.full((40,40),.3),hsv=np.zeros((40,40,3)));e.hsv[:,:,1]=.6
  old=dict(locations=[dict(id='main',color='red',point=dict(x=10,y=20,luminance=.6))]);candidate=dict(accepted=True,color='red',brightest=dict(x=22,y=20,luminance=.3),color_evidence=dict(hue=0),reasons=[])
  result=guard_ownership(deepcopy(candidate),old,e);self.assertFalse(result['accepted']);self.assertEqual(result['competing_ids'],['main'])
  e.lum[20,16]=.02;self.assertTrue(guard_ownership(deepcopy(candidate),old,e)['accepted'])
  e.lum[:]=.3;e.hsv[20,16,0]=60/360;self.assertTrue(guard_ownership(deepcopy(candidate),old,e)['accepted'])
 def test_reflection_control_reproduces_original_at_point_six(self):
  from .coverage_r272 import black_region,Parameters
  from .reflection_r275 import reflection_region
  from dataclasses import replace
  e=self.engine;p=replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25)
  for peak in e.peaks(black=True)[:20]:
   a=dict(id='control',anchor=peak['anchor'],reasons=[],accepted=False,confidence={});b=deepcopy(a)
   black_region(a,e.native,e.srgb,e.hsv,e.nhsv,e.lum,e.paper,p);reflection_region(b,e.native,e.srgb,e.hsv,e.nhsv,e.lum,e.paper,p,.60)
   for k in ('kind','dark_fraction'):b.get('dark_perimeter',{}).pop(k,None)
   b['confidence'].pop('tinted_shell_exception',None)
   self.assertEqual(a,b)
 def test_suppressed_black_reflection_cannot_reappear(self):
  prior=deepcopy(self.old['beads'][0]);prior['color']='black';main=deepcopy(prior);main['id']='strong';main['brightest']['luminance']=4*prior['brightest']['luminance'];main['region']['runs']=[]
  l=deepcopy(self.old['locations'][0]);l.update(id='strong',color='black',point=main['brightest']);old=dict(beads=[main],locations=[l],suppressed_beads=[prior],dominance_decisions=[dict(strong='strong',weak=prior['id'],suppress=True)])
  alias=deepcopy(prior);alias['id']='new-window';b,loc,rows=resolve([alias],old,self.band);self.assertEqual(rows[0]['status'],'duplicate removed');self.assertIn('suppressed-secondary-reflection-alias',rows[0]['reasons']);self.assertEqual(len(loc),1)
 def test_no_review_ids_or_model_inputs(self):
  import inspect
  from . import recover_r275
  src=inspect.getsource(recover_r275.Recovery)
  for token in ('R00956','R01284','truth','registered-centerline','N2696','audit_number'):self.assertNotIn(token,src)
if __name__=='__main__':unittest.main()
