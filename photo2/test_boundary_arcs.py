import copy,unittest
import numpy as np
from fit_boundary_arcs import arc_samples,support,losses


class BoundaryArcTests(unittest.TestCase):
    def setUp(self):
        self.arc=dict(id='L',body='C',points=[[8,5],[8,17]],interior_hint=[14,11])
        self.cfg=dict(crop=[0,0,25,25],held_out='G',observations={
            'C':[[8,5],[18,5],[18,18],[8,18]],'G':[[1,1],[5,1],[5,5],[1,5]]})

    def test_brackets_reject_growth_that_core_only_accepts(self):
        xy,cores,pairs,_=support(self.cfg,[self.arc],halfwidth=3)
        tight=np.where(xy[:,0]>8,0,-999)
        grown=np.zeros(len(xy),int)
        self.assertEqual(losses(tight,{'C':0},cores,pairs)['core_miss'],0)
        self.assertEqual(losses(grown,{'C':0},cores,pairs)['core_miss'],0)
        self.assertEqual(losses(tight,{'C':0},cores,pairs)['bracket_miss'],0)
        self.assertGreater(losses(grown,{'C':0},cores,pairs)['bracket_miss'],0)

    def test_unknown_pair_and_unassigned_arc_exclusion(self):
        pairs=arc_samples([self.arc],[8,11],6,3)
        for pair in pairs:
            for side in ['inside','outside']:
                self.assertGreater(np.linalg.norm(np.array(pair[side])-[8,11]),6)
        xy,cores,ranges,_=support(self.cfg,[self.arc])
        altered=copy.deepcopy(self.cfg);altered['observations']['G']=[[0,0],[24,0],[24,24],[0,24]]
        held=copy.deepcopy(self.arc);held['body']='G';held['points']=[[3,3],[9,9]]
        xy2,cores2,ranges2,_=support(altered,[self.arc,held])
        np.testing.assert_array_equal(xy,xy2)
        self.assertEqual(cores,cores2);self.assertEqual(ranges,ranges2)

    def test_brackets_cannot_cross_a_thin_body(self):
        region={'C':[[8,5],[11,5],[11,18],[8,18]]}
        candidates=arc_samples([self.arc],[100,100],1)
        self.assertGreater(len(candidates),0)
        valid=arc_samples([self.arc],[100,100],1,regions=region)
        self.assertEqual(valid,[])

    def test_interior_hint_reverses_paired_sides(self):
        a=arc_samples([self.arc],[100,100],1)
        flipped=copy.deepcopy(self.arc);flipped['interior_hint']=[2,11]
        b=arc_samples([flipped],[100,100],1)
        for p,q in zip(a,b):
            np.testing.assert_allclose(p['inside'],q['outside'])
            np.testing.assert_allclose(p['outside'],q['inside'])

if __name__=='__main__':unittest.main()
