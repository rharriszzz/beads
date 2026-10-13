import unittest
import numpy as np
from matplotlib.colors import hsv_to_rgb,rgb_to_hsv
from .climb_r268 import Surface,Guards,score_sums,edge_reasons,audit

class ClimbTests(unittest.TestCase):
    def surface(self):
        v=np.full((15,15),180,np.uint8);hsv=np.zeros((15,15,3));hsv[:]=[.1,.7,180/255]
        s=Surface(v,hsv,np.zeros(v.shape,bool),5);s.sums[:]=0;return s
    def test_exact_sums(self):
        rng=np.random.default_rng(268);v=rng.integers(0,256,(31,33),dtype=np.uint8)
        for n in (5,7,9):
            s=score_sums(v,n);r=n//2
            for y in range(r,v.shape[0]-r):
                for x in range(r,v.shape[1]-r):self.assertEqual(s[y,x],int(v[y-r:y+r+1,x-r:x+r+1].sum()))
            self.assertTrue(np.all(s[:r]==-1))
        self.assertEqual(score_sums(np.full((15,15),255,np.uint8),9)[7,7],255*81)
    def test_ties_deterministic(self):
        s=self.surface();s.sums[7,7]=1;s.sums[6,6]=s.sums[6,8]=2
        a=s.climb((7,7));b=s.climb((7,7));self.assertEqual(a,b);self.assertEqual(a['endpoint'],[6,6]);self.assertEqual(audit(s,a,Guards()),1)
    def test_equal_plateau_never_traversed(self):
        s=self.surface();s.sums[7,5:9]=10;s.sums[7,9]=11
        a=s.climb((5,7));self.assertEqual(a['endpoint'],[5,7]);self.assertEqual(a['stop'],'equal-plateau-with-unreachable-uphill-exit');self.assertEqual(a['plateau']['pixel_count'],4)
    def test_regional_plateau_canonical_is_not_movement(self):
        s=self.surface();s.sums[6:9,6:9]=10
        a=s.climb((7,7));self.assertEqual(a['endpoint'],[7,7]);self.assertEqual(a['plateau']['canonical'],[6,6]);self.assertEqual(len(a['steps']),1)
    def test_running_peak_valley(self):
        s=self.surface();s.sums[7,5:10]=np.arange(1,6);s.value[7,5:10]=[200,210,220,209,207]
        a=s.climb((5,7));self.assertEqual(a['endpoint'],[8,7]);self.assertIn('raw-running-peak-valley',a['blocked'][-1]['reasons']);audit(s,a,Guards())
    def test_diagonal_background_corner(self):
        s=self.surface();s.sums[7,7]=1;s.sums[8,8]=2;s.paper[7,8]=True
        a=s.climb((7,7));self.assertEqual(a['endpoint'],[7,7]);self.assertIn('diagonal-corner:confident-background',a['blocked'][0]['reasons'])
    def test_background_start(self):
        s=self.surface();s.paper[7,7]=True
        self.assertEqual(s.climb((7,7))['stop'],'start-confident-background')
    def test_circular_color_boundary(self):
        s=self.surface();s.sums[7,7:9]=[1,2];s.hsv[7,7,0]=355/360;s.hsv[7,8,0]=5/360
        self.assertEqual(s.climb((7,7))['endpoint'],[8,7]);s.hsv[7,8,0]=40/360
        a=s.climb((7,7));self.assertEqual(a['endpoint'],[7,7]);self.assertIn('abrupt-hue-boundary',a['blocked'][0]['reasons'])
    def test_best_admissible_neighbor(self):
        s=self.surface();s.sums[7,7]=1;s.sums[7,8]=3;s.sums[8,7]=2;s.paper[7,8]=True
        self.assertEqual(s.climb((7,7))['endpoint'],[7,8])

    def test_uncertainty_kept_distinct_from_confidence(self):
        s=self.surface();s.paper=s.paper.astype(np.uint8);s.paper[7,7]=2
        self.assertEqual(s.climb((7,7))['stop'],'start-existing-paper-context-uncertainty')
        self.assertNotEqual(s.climb((7,7),Guards(paper_uncertainty_stop=False))['stop'],'start-existing-paper-context-uncertainty')
    def test_nested_maximum_plateau_inventory(self):
        from .synthetic_r268 import start_points
        v=np.zeros((31,31),np.uint8);v[5,5:26]=v[25,5:26]=100;v[5:26,5]=v[5:26,25]=100;v[15,15]=200
        pts=start_points(v);self.assertEqual(len(pts),2);self.assertEqual(len(set(pts)),2);self.assertIn((15,15),pts)

    def test_uniform_dark_image_and_flat_score(self):
        from .climb_r268 import background
        rgb=np.zeros((21,21,3),np.uint8);hsv,paper,model=background(rgb)
        s=Surface(rgb.max(axis=2),hsv,paper,5);t=s.climb((10,10))
        self.assertEqual(len(t['steps']),1);self.assertEqual(t['steps'][0]['score_dn'],0)
        self.assertTrue(s.climb((10,10),Guards(enabled=False))['stop'].startswith('equal-plateau-regional-maximum'))

    def test_dark_neutral_to_bright_color_boundary(self):
        s=self.surface();s.sums[7,7:9]=[1,2];s.hsv[7,7]=[.1,.08,.12];s.hsv[7,8]=[.3,.8,.45];s.value[7,7:9]=[31,115]
        self.assertEqual(s.climb((7,7))['endpoint'],[7,7])
        self.assertEqual(s.climb((7,7),Guards(saturation_both_bright=True))['endpoint'],[8,7])

if __name__=='__main__':unittest.main()
