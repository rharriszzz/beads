"""Hard area ceiling: stop before pixel871 and preserve overflow diagnostics."""
import unittest
import numpy as np
from matplotlib.colors import rgb_to_hsv
from . import bounded_detect as bounded
from . import tunable_detect as old
from .test_tuning import audit


class BoundTests(unittest.TestCase):
    def test_exact_limit_and_overflow(self):
        for width,limited in [(869,False),(870,False),(871,True)]:
            v=np.full((1,width),200,np.uint8);hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
            mask,t=bounded.grow(v,hsv,(0,0));audit(t,0)
            self.assertEqual(len(t['accepted']),min(width,870));self.assertEqual(int(mask.sum()),min(width,870))
            self.assertEqual(t['size_limited'],limited)
            if limited:
                self.assertEqual(t['stops'][-1][:4],[870,0,869,200])
                self.assertEqual(t['stops'][-1][7],'maximum-region-pixels')

    def test_uncapped_trace_is_identical(self):
        rng=np.random.default_rng(870)
        for _ in range(20):
            v=rng.integers(80,250,(15,17),dtype=np.uint8);hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
            m,a=old.grow(v,hsv,(8,7));n,b=bounded.grow(v,hsv,(8,7))
            self.assertFalse(b.pop('size_limited'));self.assertEqual(b.pop('max_region_pixels'),870)
            self.assertEqual(a,b);np.testing.assert_array_equal(m,n)

    def test_all_eight_frontier_approaches_are_recorded_on_overflow(self):
        v=np.full((35,35),200,np.uint8);hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,t=bounded.grow(v,hsv,(17,17));audit(t,0)
        accepted={tuple(a[:2]) for a in t['accepted']};stops={(s[2],s[0],s[1]) for s in t['stops']}
        self.assertTrue(t['size_limited']);self.assertEqual(len(accepted),870)
        for i,a in enumerate(t['accepted']):
            for dy,dx in bounded.N8:
                x,y=a[0]+dx,a[1]+dy
                if 0<=x<35 and 0<=y<35 and (x,y) not in accepted:self.assertIn((i,x,y),stops)

    def test_ceiling_cannot_be_silently_raised(self):
        for n in (0,871):
            with self.assertRaises(ValueError):bounded.Parameters(max_region_pixels=n)

    def test_ten_degree_default_uses_path_anchor_and_circular_hue(self):
        self.assertEqual(bounded.Parameters().hue_stop_deg,10)
        # Two7-degree changes: the second exceeds10 degrees from the anchor.
        for hues in ([0,7,14],[350,357,4]):
            hsv=np.array([[[h/360,.8,v/255] for h,v in zip(hues,[200,190,180])]])
            _,trace=bounded.grow(np.array([[200,190,180]],np.uint8),hsv,(0,0))
            self.assertEqual([a[0] for a in trace['accepted']],[0,1])
            self.assertTrue(any(s[0]==2 and s[7]=='relative-hue-change' for s in trace['stops']))

if __name__=='__main__':unittest.main()
