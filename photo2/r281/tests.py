"""Scientific contracts, not accuracy guarantees."""
import ast,copy,unittest
from pathlib import Path
import numpy as np
from PIL import Image
from .common import OUT,ROOT,read,sha,mask_from_runs
from .geometry import R,counterfactual,warp,certify
from .detector import infer,pigment,residual,decide

class Contracts(unittest.TestCase):
 def setUp(self):
  self.p=dict(hand=1,phase=.15,pitch=1.2,inclination=15.,roll=0.,scale=8.,translation=[159.5,111.5])
 def test_intended_physical_dimensions(self):
  self.assertAlmostEqual(R,.96*4*np.sin(np.pi/6.5),14)
  for hand in (-1,1):self.assertTrue(certify({**self.p,'hand':hand})['certified'])
  self.assertFalse(certify({**self.p,'pitch':1.})['certified'])
 def test_h0_changes_only_target_rays(self):
  h=counterfactual(self.p,0,(224,320));outside=h['h1']!=0
  np.testing.assert_array_equal(h['h0'][outside],h['h1'][outside]);self.assertFalse((h['h0']==0).any())
 def test_counterfactual_matches_independent_absent_render(self):
  f=OUT/'dev/scene-00';k=read(f/'evaluation-targets.json')['targets'][0]['model_index'];maps=np.load(f/f'hyp-{k:+03}.npz');truth=np.asarray(Image.open(f/f'absent-{k:+03}'/'identity.png'))[:,:,0].astype(int)-1;expect=np.where(truth>=0,truth-14,-999);valid=~maps['unknown'];np.testing.assert_array_equal(maps['h0'][valid],expect[valid])
 def test_blank_and_shadowed_paper_not_supported(self):
  h=counterfactual(self.p,0,(224,320));rgb=np.full((224,320,3),[140,90,130],np.uint8)
  for shadow in (False,True):
   if shadow:rgb[90:140,130:185]//=4
   self.assertNotEqual(infer(rgb,h)['status'],'supported')
 def test_duplicate_claim_abstains(self):
  h=counterfactual(self.p,0,(224,320));h['competitors']=['alias'];rgb=np.full((224,320,3),[120,70,100],np.uint8);rgb[h['h1']==0]=[240,10,10];r=infer(rgb,h);self.assertEqual(r['status'],'ambiguous');self.assertEqual(r['competing_ids'],['alias'])
 def test_specular_residual_common_material_line(self):
  p=np.array([.8,.15,.05]);features=np.array([p*.7+np.ones(3)/3*.3,p*.2+np.ones(3)/3*.8]);np.testing.assert_allclose(residual(features,p),0,atol=1e-12);self.assertGreater(residual(np.array([[.05,.8,.15]]),p)[0],.3)
 def test_immutable_input_and_no_physical_center_claim(self):
  h=counterfactual(self.p,0,(224,320));old=copy.deepcopy(h);rgb=np.full((224,320,3),[120,70,100],np.uint8);before=rgb.copy();r=infer(rgb,h);self.assertIsNone(r['physical_center']);np.testing.assert_array_equal(rgb,before)
  for k in ('h1','h0','unknown'):np.testing.assert_array_equal(h[k],old[k])
 def test_no_wraparound_under_wrong_prediction(self):
  h=counterfactual(self.p,0,(224,320));q=warp(h,[1000,0]);self.assertFalse((q['h1']==0).any());self.assertFalse((q['h0']==0).any())
 def test_frozen_sources_and_explicit_generation_amendment(self):
  freeze=read(OUT/'freeze.json');amendment=read(OUT/'benchmark-amendment.json')
  for f,digest in freeze['source_hashes'].items():
   expected=amendment['new_hash'] if f=='synthetic.py' else digest;self.assertEqual(sha(ROOT/'photo2/r281'/f),expected,f)
 def test_runtime_has_no_truth_or_historical_file_io(self):
  for f in ('detector.py','geometry.py'):
   tree=ast.parse((ROOT/'photo2/r281'/f).read_text());calls=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)];self.assertFalse(set(calls)&{'open','read','load','save'})
   imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)];self.assertFalse(any(any(s in (m or '') for s in ('evaluate','synthetic','real_fit','inventory')) for m in imports))
 def test_real_prediction_freeze_and_anchor_integrity(self):
  f=OUT/'real';p=read(f/'prediction-freeze.json');m=read(f/'measurements.json');self.assertEqual(sha(f/'prediction-freeze.json'),m['prediction_freeze_sha256']);self.assertEqual(sha(f/'anchors.json'),p['anchor_sha256']);a=read(f/'anchors.json');self.assertEqual(sha(ROOT/'beads-photo-2.jpg'),a['photo_sha256']);self.assertEqual(sha(ROOT/'photo2/review/r278/phase1-inventory.json.gz'),a['phase1_sha256']);self.assertEqual(len(a['anchors']),4)
  source=(ROOT/'photo2/r281/real_fit.py').read_text();self.assertNotIn('photo-evidence',source);self.assertNotIn('raw.png',source)
  for model in p['models']:
   self.assertTrue(model['certificate']['certified']);self.assertTrue(set(model['targets']).isdisjoint(model['assignments']))
   self.assertTrue(all(any(abs(k-a) in (1,6,7) for a in model['assignments']) for k in model['targets']))
 def test_complete_benchmark_and_all_removed_controls(self):
  for split,scenes in [('dev',12),('heldout',40)]:
   generation=read(OUT/(split+'-generation.json'));self.assertEqual(len(generation['scenes']),scenes)
   for f in (OUT/split).glob('scene-*'):
    for t in read(f/'evaluation-targets.json')['targets']:
     self.assertTrue((f/f'absent-{t["model_index"]:+03}'/'photo.png').exists());self.assertGreaterEqual(t['area'],150)
 def test_confirmation_keeps_original_rules_and_frozen_sources(self):
  frozen=read(OUT/'confirmation-freeze.json');self.assertEqual(frozen['rules'],read(OUT/'freeze.json')['rules'])
  for name,digest in frozen['source_hashes'].items():self.assertEqual(sha(ROOT/'photo2/r281'/name),digest,name)
 def test_confirmation_has_distinct_scenes_and_paired_absence(self):
  fresh=read(OUT/'confirmation-generation.json');self.assertEqual(len(fresh['scenes']),24)
  for split in ('dev','heldout'):self.assertNotEqual(fresh['seed'],read(OUT/(split+'-generation.json'))['seed'])
  old={sha(f) for split in ('dev','heldout') for f in (OUT/split).glob('scene-*/photo.png')}
  for folder in (OUT/'confirmation').glob('scene-*'):
   self.assertNotIn(sha(folder/'photo.png'),old);self.assertTrue(read(folder/'truth.json')['certificate']['certified'])
   rows=read(folder/'inference.json.gz');targets=read(folder/'evaluation-targets.json')['targets'];self.assertEqual(len(rows),15*len(targets))
   for target in targets:
    k=target['model_index'];self.assertTrue((folder/f'absent-{k:+03}'/'photo.png').exists())
    pair=[r for r in rows if r['query_target']==k and r['kind'] in ('present','removed') and r['level']==0]
    self.assertEqual(len(pair),2);self.assertEqual(pair[0]['hypothesis'],pair[1]['hypothesis'])

if __name__=='__main__':unittest.main()
