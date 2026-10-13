"""R273 nonempty image fixtures, ownership conflicts and honest mask contracts."""
import unittest
from dataclasses import replace
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import hsv_to_rgb
from .interiors_r273 import detect,refine,black_ownership,Parameters,pixels,mask_local
from .coverage_r272 import detect as baseline
from .evaluate_coverage_r272 import scenes,metric

def reflections(kind='weak'):
    yy,xx=np.mgrid[:110,:140];rgb=np.full((110,140,3),hsv_to_rgb([.83,.45,.8]));truth=np.zeros((110,140),int)
    centers=[(57,55),(83 if kind=='separate' else 67 if kind=='close' else 66,55)];amps=[.86,.53 if kind=='weak' else .84]
    if kind in ('weak','equal'):
        body=((xx-61)/16)**2+((yy-55)/18)**2<=1;rgb[body]=.035;truth[body]=1
    else:
        for i,(cx,cy) in enumerate(centers,1):
            body=((xx-cx)/4.2)**2+((yy-cy)/9)**2<=1;rgb[body]=.035;truth[body]=i
    for (cx,cy),amp in zip(centers,amps):
        g=amp*np.exp(-((xx-cx)**2+(yy-cy)**2)/3.0);rgb[truth>0]+=g[truth>0,None]
    return np.rint(np.clip(rgb,0,1)*255).astype(np.uint8),truth

class R273Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.scenes={n:(rgb,t,c) for n,rgb,t,c,_ in scenes()}
    def test_weak_secondary_suppressed(self):
        rgb,t=reflections();old=baseline(rgb)[0];self.assertEqual(len(old),2);new,rows,edges,_=refine(rgb,rgb,old);self.assertEqual(len(new),1);self.assertEqual(sum('black-secondary' in r['reasons'] for r in rows),1);self.assertEqual(new[0]['brightest']['luminance'],max(r['brightest']['luminance'] for r in old));self.assertEqual(new[0]['region'],next(r['region'] for r in old if r['id']==new[0]['id']))
    def test_similar_glints_defer_whole_group(self):
        rgb,_=reflections('equal');old=baseline(rgb)[0];self.assertEqual(len(old),2);new,rows,_,_=refine(rgb,rgb,old);self.assertEqual(new,[]);self.assertTrue(all('black-ambiguous' in r['reasons'] for r in rows))
    def test_distinct_reflections_remain_separate(self):
        rgb,_=reflections('separate');old=baseline(rgb)[0];self.assertEqual(len(old),2);self.assertEqual(len(refine(rgb,rgb,old)[0]),2)
    def test_close_background_separated_reflections_not_merged(self):
        rgb,_=reflections('close');old=baseline(rgb)[0];self.assertEqual(len(old),2);new,rows,edges,_=refine(rgb,rgb,old);self.assertFalse(any(e['dark_bridge'] for e in edges));self.assertEqual(new,[])
    def test_all_colors_and_exact_native_measurements(self):
        for name in ('red-red-clear','yellow-yellow-clear','black-black-clear'):
            rgb,t,c=self.scenes[name]
            # Original 16x19-radius synthetic bodies exceed the historical 870px
            # safety ceiling when grown to their edges. Test smaller native bodies.
            from PIL import Image
            rgb=np.array(Image.fromarray(rgb).resize((126,99),Image.Resampling.NEAREST));t=np.array(Image.fromarray(t).resize((126,99),Image.Resampling.NEAREST))
            new,rows,_,_=detect(rgb);self.assertEqual(len(new),2)
            for r in new:
                self.assertEqual(ndi.label(mask_local(r['region']))[1],1);pts=pixels(r);a=np.array(sorted(pts));self.assertEqual(len(pts),r['region']['pixel_count']);np.testing.assert_allclose(a.mean(axis=0),r['region']['centroid']);self.assertTrue(pixels(r,'bright_patch')<=pts);self.assertTrue(all(t[y,x]>0 for x,y in pts))
                if r['color']!='black':self.assertTrue(pts<=pixels(r,'supported_region'));self.assertGreaterEqual(r['shape']['solidity'],.88)
    def test_oversized_yellow_body_is_not_globally_brightened(self):
        rgb,_,_=self.scenes['yellow-yellow-clear'];new,rows,_,_=detect(rgb);self.assertFalse(new);self.assertTrue(all('interior-open' in r['reasons'] for r in rows));self.assertTrue(all(len(r['interior_attempts'])==1 for r in rows))
    def test_same_color_touching_native_pixels_stay_owned(self):
        rgb,t,c=self.scenes['red-red-touching'];new,*_=detect(rgb);self.assertEqual(len(new),2);m,_=metric(new,t,c);self.assertEqual(sum(v['other_body_pixels'] for v in m.values()),0)
    def test_background_bridge_preserves_confident_paper_and_distance(self):
        from .interiors_r273 import background_allowance
        yy,xx=np.mgrid[:21,:21];hs=np.zeros((21,21,3));hs[:,:,1]=.8;hs[:,:,2]=.8;l=np.full((21,21),.15);v=(xx%3)*30.;pp=np.full((21,21),2);pp[8:13,8:13]=0;pp[10,13]=1;highlight=np.zeros((21,21),bool)
        allowed=background_allowance(pp,hs,l,v,0,highlight,.008,True)
        self.assertTrue(allowed[10,14]);self.assertFalse(allowed[10,13]);self.assertFalse(allowed[10,17]);self.assertFalse(allowed[0,0]);self.assertTrue(np.all(allowed[pp==1]==False))
        self.assertFalse(background_allowance(pp,hs,l,np.zeros_like(v),0,highlight,.008,True)[10,14])
        hs[10,14,0]=.25;self.assertFalse(background_allowance(pp,hs,l,v,0,highlight,.008,True)[10,14])
    def test_historical_touching_boundary_retreat(self):
        from .experiment_r273 import ROOT
        from .historical_coverage_r272 import colors_for
        rgb=np.load(ROOT/'photo2/review/r270/synthetic-inputs.npz')['stress-000'];truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz')['stress-000'];new,*_=detect(rgb);self.assertTrue(new);m,_=metric(new,truth,colors_for('stress-000'));self.assertEqual(sum(v['other_body_pixels']+v['background_pixels'] for v in m.values()),0)
    def test_cleanup_never_invents_pixels(self):
        rgb,_,_=self.scenes['red-yellow-touching'];_,rows,_,_=detect(rgb)
        for r in rows:
            if r['color']!='black' and 'region' in r:self.assertTrue(pixels(r)<=pixels(r,'supported_region'))
    def test_adjacent_regions_do_not_overlap(self):
        rgb,t,c=self.scenes['red-yellow-touching'];new,*_=detect(rgb);seen=set()
        for r in new:self.assertFalse(seen&pixels(r));seen|=pixels(r)
        metrics,_=metric(new,t,c)
        self.assertEqual(sum(v['background_pixels']+v['other_body_pixels'] for v in metrics.values()),0)
    def test_no_photo_review_coordinates_in_runtime(self):
        import inspect
        from . import interiors_r273
        source=inspect.getsource(interiors_r273)
        for token in ('R00956','R01284','photo-samples','inventory.json'):self.assertNotIn(token,source)
    def test_deterministic(self):
        rgb,_=reflections();base=baseline(rgb)[0];self.assertEqual(refine(rgb,rgb,base),refine(rgb,rgb,base))
if __name__=='__main__':unittest.main()
