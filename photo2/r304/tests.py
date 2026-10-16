"""Construction and data contracts, independent of photographic fit quality."""
import unittest
import numpy as np
from .model import *
from .forward import segments

class Contracts(unittest.TestCase):
    def test_one_phase_and_immutable_guards(self):
        for name in FAMILIES:
            a,b=Extended(name,64),Extended(name,96);i=np.searchsorted(b.indices,a.indices)
            np.testing.assert_array_equal(a.centers,b.centers[i]);np.testing.assert_array_equal(a.phase,b.phase[i]);np.testing.assert_allclose(np.diff(a.phase),a.hand*2*np.pi/a.p['turn'],atol=1e-12)
            self.assertEqual(len(a.indices[(a.indices>=FIRST)&(a.indices<=LAST)]),350)
    def test_s1_registration(self):
        for name in FAMILIES:
            c=Extended(name);self.assertLess(c.registration['maximum_S1_center_change_px'],.0002)
            k=np.searchsorted(c.indices,0);np.testing.assert_allclose(c.axis_xy[k],c.offset,atol=1e-9)
    def test_visible_boundary_hole(self):
        mask=np.ones((3,3),bool);mask[1,1]=False;s=segments(mask,10,20)
        length=sum(abs(x2-x1)+abs(y2-y1) for x1,y1,x2,y2 in s)
        self.assertEqual(length,16);self.assertEqual(len(s),8)
        self.assertEqual(segments(np.ones((1,1),bool),0,0),[[-.5,-.5,.5,-.5],[-.5,.5,.5,.5],[-.5,-.5,-.5,.5],[.5,-.5,.5,.5]])
    def test_no_hidden_assignment_replacement(self):
        for name in FAMILIES:
            d=read(BASE/f'results/{name}-correspondences.json');matched=[r for r in d['records'] if r['index'] is not None];self.assertEqual(len(matched),len({r['index'] for r in matched}))
            self.assertTrue(all(r['index']==r['penalty_owners']['24'] for r in d['records']))
            old=read(ROOT/f'photo2/r303/results/native-{FAMILIES[name]}.json.gz')['result'];anchor={r['id']:r['index'] for r in old['train']['records']+old['withheld']['records']};current={r['observation']:r['index'] for r in d['records']}
            for ident,k in anchor.items():self.assertEqual(current[ident],k)
            for key,path in d['paths'].items():
                post=[p['index'] for p in path if p['operation']=='pair' and p['index']>max(anchor.values())];self.assertEqual(post,sorted(post))
    def test_original_observations_and_feasible_alternative(self):
        rows=read(BASE/'evidence/observations.json')['observations'];source={r['id']:r for r in read(ROOT/'photo2/r299/evidence/measurements.json.gz')['observations']}
        for r in rows:
            if r['id'] in source:self.assertEqual(r['point'],source[r['id']].get('centroid') or source[r['id']]['historical_peak'])
        d=read(BASE/'results/hand-minus.json.gz');self.assertTrue(d['physical']['certified']);self.assertEqual([r['index'] for r in d['positions'] if r['displayed']],list(range(-20,330)))

if __name__=='__main__':unittest.main()
