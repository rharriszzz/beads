import unittest
from copy import deepcopy
from .correspondence import track
from .bright import components,freeze_epoch
from .correspondence import evaluate_fixed as evaluate
from photo2.r297.common import ROOT,read
import numpy as np

class ExtraContracts(unittest.TestCase):
 def test_stored_assignment_and_cohort_cannot_change(self):
  o=[dict(id='a',peak=[1,2],centroid=[1,2],reliable_correspondence=True,reliably_localized=True,specular_status='supported')];e=freeze_epoch(o,{'a':[0,1]},'fixture');bad=deepcopy(e);bad['assignments']['a']=[0,2]
  with self.assertRaises(ValueError):evaluate(bad,[],geometry_passed=True)
  bad=deepcopy(e);bad['cohort']=[]
  with self.assertRaises(ValueError):evaluate(bad,[],geometry_passed=True)
 def test_faint_secondary_peak_is_not_dropped(self):
  from .local_lobes import maxima
  r=maxima([[0,0],[1,0],[2,0],[3,0],[4,0]],[1.,.8,.01,.2,.3]);self.assertEqual(len(r),2);self.assertAlmostEqual(r[1]['relative_to_global'],.3)
 def test_component_order_is_not_lobe_identity(self):
  refs=[dict(index=0,lobe=1,peak_local_radius=[0,1,0]),dict(index=0,lobe=2,peak_local_radius=[0,-1,0])]
  cur=[dict(index=0,component=1,peak_local_radius=[0,-1,0]),dict(index=0,component=2,peak_local_radius=[0,1,0])]
  r=track(refs,cur);self.assertEqual([p['component'] for p in r['predictions']],[2,1]);self.assertFalse(r['unresolved'])
 def test_merge_does_not_keep_easy_lobe(self):
  refs=[dict(index=0,lobe=i,peak_local_radius=[0,1,0]) for i in [1,2]];cur=[dict(index=0,component=1,peak_local_radius=[0,1,0])];self.assertEqual(track(refs,cur)['predictions'],[])
 def test_two_nearby_maxima_preserved(self):
  xy=np.array([[0,0],[1,0],[2,0],[3,0],[4,0]]);v=np.array([1,1,.1,.99,.99]);cs=components(xy,v);self.assertEqual(len(cs),2);self.assertEqual(len(cs[0]['peak_ties']),2);self.assertEqual(len(cs[1]['peak_ties']),2)
 def test_ambiguous_observation_not_confirmed_specular(self):
  o=[dict(id='yellow',peak=[1,2],centroid=[1,2],reliable_correspondence=True,reliably_localized=True,specular_status='ambiguous')];e=freeze_epoch(o,{},'fixture');r=evaluate(e,[],geometry_passed=True);self.assertEqual(r['cohort'],0);self.assertFalse(r['eligible_for_optimization']);self.assertIsNone(r['metrics']['peak']['maximum_px'])
 def test_expansion_cannot_buy_acceptance(self):
  cases={r['name']:r for r in read(ROOT/'photo2/r314/results/controls.json')['cases']};c=cases['expansion_3px'];self.assertFalse(c['acceptance']['passed']);self.assertIn('paper',c['acceptance']['failures']);self.assertIn('seam',c['acceptance']['failures']);self.assertLess(c['metrics']['vector']['omission'],cases['unchanged']['metrics']['vector']['omission'])
 def test_material_measurement_is_immutable(self):
  o=[dict(id='a',peak=[1,2],centroid=[1,2],reliable_correspondence=True,reliably_localized=True,specular_status='supported')];e=freeze_epoch(o,{'a':[0,1]},'fixture');e['observations'][0]['peak']=[1,3]
  with self.assertRaises(ValueError):evaluate(e,[],geometry_passed=True)
if __name__=='__main__':unittest.main()
