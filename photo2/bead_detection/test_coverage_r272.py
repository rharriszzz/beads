"""Nonempty contracts and known failure witnesses for coverage, no review inputs."""
import unittest
from dataclasses import replace
import numpy as np
from scipy import ndimage as ndi
from .coverage_r272 import detect,Parameters,select_nonoverlap
from .evaluate_coverage_r272 import scenes,metric
from .inventory_r272 import component,CROSS

class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures={name:(rgb,truth,colors) for name,rgb,truth,colors,_ in scenes()}
        cls.cache={}
    def run_scene(self,name,p=None):
        rgb,truth,colors=self.fixtures[name]
        if p is not None:return detect(rgb,p=p),truth,colors
        if name not in self.cache:self.cache[name]=detect(rgb)
        return self.cache[name],truth,colors
    def test_black_bypasses_broad_illumination(self):
        d,t,c=self.run_scene('black-black-clear',replace(Parameters(),minimum_mean_y=.99,minimum_lit_fraction=1.01,minimum_core_pixels=1000));b=d[0]
        self.assertEqual(len(b),2);self.assertTrue(all(z['color']=='black' for z in b))
    def test_no_reflection_is_not_a_bead_detection(self):
        d,_,_=self.run_scene('black-black-no-black-reflection');self.assertEqual(len(d[0]),0)
    def test_black_stops_at_first_dark_shell(self):
        d,t,c=self.run_scene('black-black-clear')
        for b in d[0]:
            self.assertTrue(b['dark_perimeter']['closed']);self.assertLessEqual(b['dark_perimeter']['maximum_value'],b['dark_perimeter']['threshold']);self.assertLess(b['region']['pixel_count'],np.sum(t==1)/4)
    def test_colored_nonempty_and_classification(self):
        for name,color in [('red-red-clear','red'),('yellow-yellow-clear','yellow')]:
            d,t,c=self.run_scene(name);self.assertEqual(len(d[0]),2);self.assertTrue(all(b['color']==color for b in d[0]))
    def test_background_shadows_and_palette(self):
        for name in self.fixtures:
            if name.startswith('background-'):self.assertEqual(len(self.run_scene(name)[0][0]),0)
    def test_known_truth_ownership(self):
        for name in ['black-black-clear','red-red-clear','yellow-yellow-clear','black-red-touching','red-yellow-touching']:
            d,t,c=self.run_scene(name);m,_=metric(d[0],t,c)
            for v in m.values():self.assertEqual(v['background_pixels']+v['other_body_pixels'],0);self.assertEqual(v['duplicate_extras'],0)
    def test_measurements_and_connected_native_masks(self):
        d,_,_=self.run_scene('red-yellow-clear');rgb,_,_=self.fixtures['red-yellow-clear']
        from .brightness_r270 import linearize
        lum=linearize(rgb/255)@np.array([.2126,.7152,.0722])
        for b in d[0]:
            for key in ['region','bright_patch']:
                r=b[key];pts=np.array([(x,y) for y,a,z in r['runs'] for x in range(a,z+1)]);self.assertEqual(len(pts),r['pixel_count']);np.testing.assert_allclose(pts.mean(axis=0),r['centroid']);m=np.zeros(lum.shape,bool);m[pts[:,1],pts[:,0]]=True;self.assertEqual(ndi.label(m,CROSS)[1],1)
            pts=np.array([(x,y) for y,a,z in b['region']['runs'] for x in range(a,z+1)]);self.assertAlmostEqual(b['brightest']['luminance'],lum[pts[:,1],pts[:,0]].max());self.assertEqual(b['outline']['smooth'][0],b['outline']['smooth'][-1]);self.assertLessEqual(b['region']['pixel_count'],870)
    def test_multiple_glints_count_physical_body_once(self):
        d,t,c=self.run_scene('black-black-multiple-highlights');m,_=metric(d[0],t,c);self.assertEqual(m['black']['duplicate_extras'],0);self.assertEqual(m['black']['detected'],2)
    def test_deterministic(self):
        rgb,_,_=self.fixtures['black-red-clear'];a=detect(rgb)[0];b=detect(rgb)[0];self.assertEqual(a,b)
    def test_overlap_does_not_merge_distinct_peaks(self):
        def rec(id,x,a,b):return dict(id=id,accepted=True,color='yellow',reasons=[],brightest=dict(x=x,y=5,luminance=.8),region=dict(runs=[[5,a,b]]))
        rows=[rec('a',2,0,12),rec('b',20,10,22)];select_nonoverlap(rows,None)
        self.assertTrue(all(not r['accepted'] and 'ownership-conflict' in r['reasons'] for r in rows))
    def test_frozen_annotations_not_runtime_inputs(self):
        import inspect
        from . import coverage_r272
        src=inspect.getsource(coverage_r272);self.assertNotIn('photo-samples',src);self.assertNotIn('R00956',src);self.assertNotIn('R01284',src);self.assertNotIn('trusted-locations.json',src)

if __name__=='__main__':unittest.main()
