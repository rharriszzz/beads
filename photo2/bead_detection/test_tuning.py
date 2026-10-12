"""Before-photo contracts for bounded native noise tolerance and peak gating."""
import unittest
from dataclasses import replace
import numpy as np
from matplotlib.colors import rgb_to_hsv
from . import monotone_detect as old
from . import tunable_detect as new
from .test_pixels import fixtures


def audit(t, budget):
    floor=255; seen=set();locked={}
    for s in t['stops']:locked.setdefault(tuple(s[:2]),s[8])
    for i,a in enumerate(t['accepted']):
        xy=tuple(a[:2]);assert xy not in seen;seen.add(xy)
        assert xy not in locked or i<locked[xy]
        assert a[3]<=floor+budget;floor=min(floor,a[3])
        if i:
            assert 0<=a[2]<i
            p=t['accepted'][a[2]]
            assert max(abs(a[0]-p[0]),abs(a[1]-p[1]))==1
        else:assert a[2]==-1
    for s in t['stops']:
        p=t['accepted'][s[2]]
        assert max(abs(s[0]-p[0]),abs(s[1]-p[1]))==1


class TuningTests(unittest.TestCase):
    def test_zero_budget_preserves_baseline(self):
        rng=np.random.default_rng(263)
        for _ in range(30):
            v=rng.integers(0,256,(12,15),dtype=np.uint8)
            y,x=np.unravel_index(v.argmax(),v.shape)
            hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
            a,ta=old.grow(v,hsv,(int(x),int(y)))
            b,tb=new.grow(v,hsv,(int(x),int(y)))
            np.testing.assert_array_equal(a,b);self.assertEqual(ta,tb)

    def test_noise_budget_never_accumulates_uphill(self):
        v=np.array([[210,200,201,202,203,204,220]],np.uint8)
        hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        for budget in range(5):
            _,t=new.grow(v,hsv,(0,0),replace(new.Parameters(),rise_budget_dn=budget))
            audit(t,budget)
            self.assertEqual([a[0] for a in t['accepted']],list(range(2+budget)))
            self.assertNotIn(6,[a[0] for a in t['accepted']])

    def test_six_scenes_all_tested_budgets_and_peak_filter(self):
        for name,rgb in fixtures().items():
            for budget in (0,1,2,4):
                p=replace(new.Parameters(),rise_budget_dn=budget)
                data,_,_=new.detect(rgb,p)
                for r in data['regions']+data['rejected']:audit(r['trace'],budget)
                if name=='dark_shadow':self.assertEqual(len(data['regions']),0)
                if name in ('two_adjacent','uneven_light','noise_and_equal'):
                    self.assertGreaterEqual(len(data['regions']),2)
                    for r in data['regions']:
                        x=r['bright_patch']['peak'][0]
                        if x<45:self.assertLess(r['bbox'][2],50)
                        if x>55:self.assertGreater(r['bbox'][0],45)
                # Peak gating is exactly filterable without rerunning growth.
                filtered,_,_=new.detect(rgb,replace(p,minimum_peak_dn=220))
                self.assertEqual([(r['id'],r['pixel_runs']) for r in filtered['regions']],
                                 [(r['id'],r['pixel_runs']) for r in data['regions'] if r['bright_patch']['value_dn']>=220])
                self.assertEqual(len(data['maxima']),len(filtered['maxima']))

    def test_destination_cannot_be_reopened_by_detour(self):
        rng=np.random.default_rng(264)
        for budget in (0,1,2,4):
            for _ in range(25):
                v=rng.integers(150,170,(12,15),dtype=np.uint8);v[5,6]=200
                hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
                _,t=new.grow(v,hsv,(6,5),replace(new.Parameters(),rise_budget_dn=budget))
                audit(t,budget)

if __name__=='__main__':unittest.main()
