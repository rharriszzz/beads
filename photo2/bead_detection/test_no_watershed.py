"""R262: removing the ownership veto must leave other growth rules unchanged."""
import unittest
from dataclasses import replace
import numpy as np
from matplotlib.colors import rgb_to_hsv
from . import pixel_detect as archived
from . import monotone_detect as current
from .test_pixels import fixtures

def audit_trace(region):
    t=region['trace'];a=t['accepted'];seen=set();blocked={}
    assert a
    for s in t['stops']:blocked.setdefault((s[0],s[1]),s[8])
    for i,row in enumerate(a):
        x,y,prev,v,*_=row
        assert (x,y) not in seen;seen.add((x,y))
        assert (x,y) not in blocked or i<blocked[x,y]
        if i:
            assert 0<=prev<i
            q=a[prev];assert max(abs(x-q[0]),abs(y-q[1]))==1
            assert v<=q[3] and v<=a[i-1][3]
            if row[7]:assert q[7]
        else:assert prev==-1
    points=[(r[0],r[1]) for r in a if r[7]]
    expected={(x,y) for y,x1,x2 in region['pixel_runs'] for x in range(x1,x2+1)}
    assert set(points)==expected
    assert len(points)==region['pixel_count']
    assert np.allclose(np.mean(points,axis=0),region['centroid'],rtol=0,atol=1e-12)
    assert tuple(region['location']) in expected
    for c in region['contours']:assert c[0]==c[-1]
    for s in t['stops']:
        q=a[s[2]];assert max(abs(s[0]-q[0]),abs(s[1]-q[1]))==1
    return len(a),len(t['stops'])


class NoPartitionTests(unittest.TestCase):
    def test_exact_equivalence_to_old_growth_without_ownership_veto(self):
        rng=np.random.default_rng(262)
        inputs=[np.array([[245,241,245]],np.uint8),np.full((9,9),160,np.uint8)]
        inputs += [rng.integers(50,245,(13,17),dtype=np.uint8) for _ in range(50)]
        for value in inputs:
            y,x=np.unravel_index(np.argmax(value),value.shape)
            hsv=rgb_to_hsv(np.repeat(value[:,:,None],3,axis=2)/255)
            old_mask,old_trace=archived.grow(value,hsv,np.ones_like(value),1,(int(x),int(y)))
            mask,trace=current.grow(value,hsv,(int(x),int(y)))
            mx,my=trace.pop('mask_offset');expected=np.zeros(value.shape,bool)
            expected[my:my+mask.shape[0],mx:mx+mask.shape[1]]=mask
            np.testing.assert_array_equal(expected,old_mask)
            self.assertEqual(trace,old_trace)

    def test_six_scenes_keep_pixel_contracts(self):
        for name,rgb in fixtures().items():
            with self.subTest(name=name):
                data,labels,count=current.detect(rgb)
                for r in data['regions']+data['rejected']:
                    audit_trace(r)
                    self.assertNotIn('competing-maximum-catchment',[s[7] for s in r['trace']['stops']])
                self.assertTrue(np.array_equal(labels==-1,count>1))
                if name=='dark_shadow':self.assertEqual(len(data['regions']),0)
                if name in ('two_adjacent','uneven_light','noise_and_equal'):
                    self.assertGreaterEqual(len(data['regions']),2)
                    for r in data['regions']:
                        x=r['bright_patch']['peak'][0]
                        if x<45:self.assertLess(r['bbox'][2],50)
                        if x>55:self.assertGreater(r['bbox'][0],45)
                if name=='black_reflection':self.assertTrue(any(r['dark_enclosure'] for r in data['regions']))

    def test_245_241_245_peaks_can_overlap_without_crossing_the_rise(self):
        v=np.array([[245,241,245]],np.uint8);hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        for seed in [(0,0),(2,0)]:
            _,trace=current.grow(v,hsv,seed)
            accepted={(a[0],a[1]) for a in trace['accepted']}
            self.assertIn((1,0),accepted)
            self.assertNotIn((2-seed[0],0),accepted)
            self.assertTrue(any(s[7]=='brightness-rise' for s in trace['stops']))

    def test_bright_leaf_retreat_is_unchanged_not_fixed_in_this_step(self):
        v=np.array([[245,240]],np.uint8);hsv=rgb_to_hsv(np.repeat(v[:,:,None],3,axis=2)/255)
        _,trace=current.grow(v,hsv,(0,0))
        self.assertFalse(trace['accepted'][1][7])
        self.assertEqual(trace['retreat_floor_dn'][1],240)

if __name__=='__main__':unittest.main()
