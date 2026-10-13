import unittest
import numpy as np
from matplotlib.colors import rgb_to_hsv
from .brightness_r270 import *
from .search_r269 import Policy

class BrightnessTests(unittest.TestCase):
    def test_srgb_luminance_reference_primaries(self):
        colors=np.array([[255,0,0],[0,255,0],[0,0,255],[255,255,255],[0,0,0]],np.uint8)
        np.testing.assert_allclose(scores(colors)['Y']/255,[.2126,.7152,.0722,1,0],atol=1e-14)
    def test_correct_linearization_at_dark_and_middle_values(self):
        self.assertAlmostEqual(float(linearize(.02)),.02/12.92,places=14)
        self.assertAlmostEqual(float(linearize(128/255)),.21586050011389926,places=14)
    def test_oklab_published_linear_srgb_examples(self):
        colors=np.array([[255,0,0],[0,255,0],[0,0,255],[255,255,255]])
        np.testing.assert_allclose(scores(colors)['OKL']/255,[.6279553606145516,.8664396115356694,.4520137183853429,.9999999934735462],atol=2e-9)
    def test_vs_equals_v_times_one_minus_half_s(self):
        rng=np.random.default_rng(270);rgb=rng.integers(0,256,(10,11,3),dtype=np.uint8);h=rgb_to_hsv(rgb/255.)
        np.testing.assert_allclose(scores(rgb)['VS'],255*h[:,:,2]*(1-h[:,:,1]/2),atol=6e-14)
    def test_transform_before_averaging(self):
        rgb=np.array([[0,0,0],[255,255,255]],np.uint8)
        self.assertAlmostEqual(scores(rgb)['Y'].mean()/255,.5)
        self.assertLess(float(scores(rgb.mean(axis=0))['Y']/255),.22)
    def test_neutral_roundtrip_and_threshold_conversion(self):
        for m in MEASURES:
            for v in (0,4,32,128,192,255):
                self.assertAlmostEqual(float(gray_equivalent(neutral(v,m),m)),v,places=9)
                self.assertAlmostEqual(floor_for(float(neutral(v,m)),12,m),float(neutral(max(0,v-12),m)),places=9)
    def test_v_quantization_and_all_sums_exact(self):
        rng=np.random.default_rng(2701);rgb=rng.integers(0,256,(17,19,3),dtype=np.uint8);q=quantized(rgb)
        np.testing.assert_array_equal(q['V'],rgb.max(axis=2).astype(np.int64)*SCALE)
        for m in MEASURES:
            self.assertLessEqual(np.max(np.abs(q[m]/SCALE-scores(rgb)[m])),.5001/SCALE)
            for n in (5,7,9):
                a=sums(q[m],n);r=n//2
                for y in range(r,17-r):
                    for x in range(r,19-r):self.assertEqual(int(a[y,x]),int(q[m][y-r:y+r+1,x-r:x+r+1].sum()))
    def test_maximum_plateau_crossing_crop_preserved(self):
        q=np.zeros((15,15),np.int64);q[7,5:10]=200*SCALE;pts,_=maxima_inventory(q,[7,6,8,9]);self.assertEqual({(x,y) for x,y,_ in pts},{(x,7) for x in range(5,10)})
    def test_prominence_saddle_and_censoring(self):
        q=np.zeros((15,15),np.int64);q[7,4]=200*SCALE;q[7,5:10]=160*SCALE;q[7,10]=220*SCALE
        p=prominences(q,[(4,7),(10,7)]);self.assertEqual(p[0]['prominence'],40);self.assertFalse(p[0]['prominence_censored']);self.assertTrue(p[1]['prominence_censored'])
    def test_perceived_pale_peak_beats_orange_for_alternatives(self):
        rgb=np.array([[248,219,125],[245,174,66]],np.uint8);a=scores(rgb)
        for m in MEASURES:self.assertGreater(a[m][0],a[m][1])
        self.assertGreater(a['Y'][0]-a['Y'][1],30)
    def graph(self):
        rgb=np.full((21,21,3),[200,160,70],np.uint8);q=quantized(rgb)['Y'];hs=rgb_to_hsv(rgb/255.);p=np.zeros((21,21),np.uint8);s=sums(q,5)
        return q,hs,p,s
    def test_float_score_search_keeps_small_differences(self):
        q,h,p,s=self.graph();s[:]=100*SCALE*25;s[10,11]=int(100.01*SCALE*25)
        g=Search(q,h,p,s,5,(10,10),'Y');r=g.search(3,Policy(256,256,False));self.assertEqual(g.xy[r['end']].tolist(),[11,10]);self.assertAlmostEqual(g.mean[r['end']],100.01)
    def test_plateau_is_diagnosed_without_equal_climb_moves(self):
        q,h,p,s=self.graph();c=Climber(q,h,p,5,'Y');c.sumq[:]=0;c.sumq[10,7:11]=100*SCALE*25;c.sumq[10,11]=101*SCALE*25
        t=c.climb((7,10),False);self.assertEqual(len(t['steps']),1);self.assertEqual(t['stop'],'equal-plateau-with-uphill-exit')
    def test_background_and_diagonal_guards_remain_fixed(self):
        q,h,p,s=self.graph();s[:]=0;s[10,10]=100*SCALE;s[11,11]=101*SCALE;p[10,11]=1;p[11,10]=2
        g=Search(q,h,p,s,5,(10,10),'Y');r=g.search(3,Policy(256,2));self.assertFalse(r['reachable'][g.index((11,11))])
    def test_broader_search_crosses_shallow_fluctuations(self):
        q,h,p,s=self.graph();s[:]=50*SCALE*25;s[10,7:12]=np.array([100,100,99.9,100.2,101])*SCALE*25
        g=Search(q,h,p,s,5,(7,10),'Y');r=g.search(6,Policy(24,2));self.assertEqual(g.xy[r['end']].tolist(),[11,10]);g.audit_path(g.path(r['pred'],r['end']),6,Policy(24,2))

    def test_profile_pairing_keeps_native_v_and_vs(self):
        native=np.array([[248,219,125]],np.uint8);standard=np.array([[240,216,146]],np.uint8)
        result=paired_scores(native,standard)
        for m in ('V','VS'):np.testing.assert_equal(result[m],scores(native)[m])
        for m in ('Y','OKL'):np.testing.assert_equal(result[m],scores(standard)[m])
    def test_converted_raw_floor_blocks_substantial_valley(self):
        q,h,p,s=self.graph();q[10,11]=int(neutral(90,'Y')*SCALE);q[10,10]=int(neutral(140,'Y')*SCALE);s[:]=0;s[10,10]=100*SCALE*25;s[10,11]=101*SCALE*25
        g=Search(q,h,p,s,5,(10,10),'Y');r=g.search(3,Policy(24,2));self.assertFalse(r['reachable'][g.index((11,10))])
    def test_constant_background_start_does_not_move(self):
        q,h,p,s=self.graph();p[10,10]=1;c=Climber(q,h,p,5,'Y');t=c.climb((10,10));self.assertEqual(t['endpoint'],[10,10]);self.assertEqual(t['stop'],'start-background')
    def test_strict_climb_keeps_sub_dn_improvement(self):
        q,h,p,s=self.graph();c=Climber(q,h,p,5,'Y');c.sumq[:]=0;c.sumq[10,10]=100*SCALE*25;c.sumq[10,11]=int(100.000001*SCALE*25)
        t=c.climb((10,10),False);self.assertEqual(t['endpoint'],[11,10]);c.audit(t,False)

if __name__=='__main__':unittest.main()
