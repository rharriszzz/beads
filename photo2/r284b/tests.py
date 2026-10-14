"""Scientific contracts and mathematical controls, independent of review coordinates."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from photo2.r282.common import read,pixels,validate
from .methods import colored,reflection,grow_barrier,metrics,contour
from .run import OUT

class Mathematics(unittest.TestCase):
    def setUp(self):
        self.y,self.x=np.indices((49,49));self.initial=(self.x-24)**2+(self.y-24)**2<100
        self.lum=.002+.4*np.exp(-((self.x-24)**2/18+(self.y-24)**2/40))
    def test_thickness_removes_branch_without_inventing_pixels(self):
        mask=self.initial.copy();mask[23:26,30:44]=True
        m,_,_=colored(self.lum,np.ones_like(mask),mask,variant='T')
        self.assertFalse((m&~mask).any());self.assertLess(m[:,38:].sum(),mask[:,38:].sum());self.assertGreater(m.sum(),.8*self.initial.sum())
    def test_barrier_stops_renewed_brightness_after_saddle(self):
        field=np.tile(np.array([.8,.5,.15,.3,.6]),(3,1));domain=np.ones_like(field,bool)
        m=grow_barrier(field,domain,[0,1],.08)
        self.assertTrue(m[:,:3].all());self.assertFalse(m[:,3:].any())
    def test_all_colored_results_connected(self):
        for method in ('A','T','E','W','L','I'):
            m,c,_=colored(self.lum,np.ones_like(self.initial),self.initial,variant=method)
            self.assertLessEqual(ndi.label(m)[1],1);self.assertTrue(np.isfinite(c).all())
    def test_two_highlights_are_not_two_certified_bodies(self):
        lum=self.lum+.32*np.exp(-((self.x-32)**2+(self.y-24)**2)/3)
        _,_,meta=colored(lum,np.ones_like(self.initial),self.initial,variant='W')
        self.assertGreater(meta['competing_feature_markers'],1);self.assertTrue(meta['possible_false_partition'])
    def test_reflections_have_native_positive_contrast(self):
        for method in ('R1','R2','R3','R4'):
            m,c,meta=reflection(self.lum,np.ones_like(self.initial),self.initial,variant=method)
            self.assertTrue(m.any());self.assertTrue((self.lum[m]>=meta['native_level']-1e-12).all())
            self.assertFalse(m[0,0]);self.assertTrue(np.isfinite(c).all())
    def test_translation_equivariance(self):
        a,c,_=reflection(self.lum,np.ones_like(self.initial),self.initial,variant='R1')
        b,d,_=reflection(np.roll(self.lum,2,axis=1),np.ones_like(self.initial),np.roll(self.initial,2,axis=1),seed=[26,24],variant='R1')
        np.testing.assert_array_equal(np.roll(a,2,axis=1),b);np.testing.assert_allclose(c+[2,0],d,atol=1e-10)
    def test_weak_secondary_survives(self):
        lum=.002+.07*np.exp(-((self.x-24)**2/10+(self.y-24)**2/4))
        for method in ('R1','R2','R3','R4'):
            m,_,meta=reflection(lum,np.ones_like(self.initial),self.initial,variant=method)
            self.assertTrue(m.any());self.assertEqual(meta['peak'],[24,24])
    def test_weak_bright_bridge_exposes_failure_and_basin_fix(self):
        lum=.002+.07*np.exp(-((self.x-24)**2+(self.y-26)**2)/8)+.4*np.exp(-((self.x-24)**2+(self.y-17)**2)/8)
        initial=(self.x-24)**2+(self.y-26)**2<49
        a,_,ma=reflection(lum,np.ones_like(initial),initial,seed=[24,26],variant='R1')
        b,_,mb=reflection(lum,np.ones_like(initial),initial,seed=[24,26],variant='R4')
        self.assertTrue(ma['brighter_neighbor_in_support']) # preserved failure
        self.assertFalse(mb['brighter_neighbor_in_support'])
        self.assertTrue(b[26,24]);self.assertFalse(b[17,24])
        self.assertEqual(mb['reflection_markers'],2)
    def test_native_subpixel_are_separate(self):
        m,c,_=reflection(self.lum,np.ones_like(self.initial),self.initial,variant='R1')
        self.assertTrue(np.any(np.abs(c-np.rint(c))>1e-3));self.assertEqual(m.dtype,bool)

class SavedEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=read(OUT/'cases.json');cls.data=[read(OUT/(c['name']+'.json.gz')) for c in cls.cases]
    def test_full_records_and_physical_independence(self):
        for data in self.data:
            for ob in data['observations']:
                for r in ob['variants'].values():
                    validate(r);self.assertEqual(r['importance'],'high');self.assertIsNone(r['physical_model_index']);self.assertEqual(r['physical_model_confidence'],0)
                    self.assertIsNone(r['physical_body_center']);self.assertIsNone(r['physical_body_centerline_crossing'])
    def test_black_contract_native_intensity_and_peak(self):
        for data in self.data:
            for ob in data['observations']:
                if ob['color']!='black':continue
                lum=np.array(ob['native_Y']);origin=np.array(ob['origin'])
                for method in ('R1','R2','R3','R4'):
                    r=ob['variants'][method];p=pixels(r['measured_support'])-origin
                    self.assertEqual(r['support_type'],'specular-reflection region')
                    if len(p):self.assertTrue((lum[p[:,1],p[:,0]]>=r['method_evidence']['native_level']-1e-12).all())
                    self.assertEqual(r['centerline']['measured_feature'],'reflection')
    def test_same_frozen_cues_for_alternatives(self):
        for data in self.data:
            for ob in data['observations']:
                for r in ob['variants'].values():self.assertEqual(r['seed'],ob['seed'])
    def test_native_metrics_and_contours(self):
        for data in self.data:
            for ob in data['observations']:
                for r in ob['variants'].values():
                    self.assertEqual(len(pixels(r['measured_support'])),r['metrics']['area'])
                    self.assertLessEqual(r['metrics']['components'],1)
                    self.assertTrue(np.isfinite(np.array(r['subpixel_contour'])).all())
    def test_complete_comparison_and_failed_pass_preserved(self):
        self.assertEqual(len(self.cases),10);self.assertTrue((OUT/'pass01/methods.py.txt').exists());self.assertTrue((OUT/'selection-control/cases.json').exists())
        for d in self.data:
            for o in d['observations']:
                required=('R1','R2','R3','R4','A') if o['color']=='black' else ('A','T','E','W','L','I')
                self.assertTrue(set(required)<=o['variants'].keys())

if __name__=='__main__':unittest.main()
