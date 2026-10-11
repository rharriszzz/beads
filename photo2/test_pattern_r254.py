import itertools, unittest
from pattern_r254 import diagnostic, cut_scan, propagate

def row(k,c,i=None):return dict(k=k,color=c,observation_id=str(k) if i is None else str(i))

class ExactPatternTests(unittest.TestCase):
    def test_minimum_not_pairs(self):
        rr=[row(k,'red' if k<3 else 'yellow') for k in range(5)]
        d=diagnostic(rr,1);self.assertEqual(d['minimum_conflicting_assignments'],2)
        self.assertEqual(diagnostic(rr[::-1],1)['minimum_conflicting_assignments'],2)
    def test_unknown_not_black(self):
        self.assertEqual(diagnostic([row(0,'red'),row(1,'yellow')],4)['template'],'RY??')
    def test_incomplete_final_repeat(self):
        rr=[row(k,('red','yellow','black')[k%3]) for k in range(8)]
        self.assertTrue(diagnostic(rr,3)['exact']);self.assertNotEqual(8%3,0)
    def test_all_cuts_bruteforce(self):
        rr=[row(0,'red'),row(2,'yellow'),row(3,'red'),row(7,'black')]
        for P in range(1,10):
            a=cut_scan(rr,9,P);b=min(diagnostic(rr,P,9,c)['minimum_conflicting_assignments'] for c in range(10))
            self.assertEqual(a['minimum'],b)
    def test_known_pattern_rotation_seam(self):
        original=[('red','yellow','black')[k%3] for k in range(8)]
        rr=[row((k-3)%8,c) for k,c in enumerate(original)]
        self.assertFalse(diagnostic(rr,3)['exact']);self.assertEqual(cut_scan(rr,8,3)['minimum'],0)
    def test_shift_reversal(self):
        rr=[row(k,('red','yellow','black')[k%3]) for k in range(8)]
        for sign in (-1,1):self.assertTrue(diagnostic([dict(r,k=sign*r['k']+11) for r in rr],3)['exact'])
    def test_propagation_soundness_exhaustive(self):
        rr=[row(0,'red',0),row(1,'yellow',1),row(2,'red',2)]
        domains=[[0],[1],[2],[0,1],[1,2],[0,2]]
        for dd in itertools.product(domains,repeat=3):
            for P in (1,2,3):
                possible=any(len(set(kk))==3 and diagnostic([dict(r,k=k) for r,k in zip(rr,kk)],P)['exact'] for kk in itertools.product(*dd))
                if possible:self.assertNotEqual(propagate(rr,dd,P)['status'],'infeasible')
    def test_regression_preliminary(self):
        import json
        from pattern_r254 import OLD
        for mid,P,want in [('N2671_h+1_both',309,13),('N2679_h-1_twist',310,11)]:
            rr=json.loads((OLD/f'{mid}-assignments.json').read_text());rr=[r for r in rr if r['conditional_unique']]
            self.assertEqual(diagnostic(rr,P)['minimum_conflicting_assignments'],want)


class CameraAndAssignmentTests(unittest.TestCase):
    def test_divisibility_clarification(self):
        rr=[row(k,('red','yellow','black')[k%3]) for k in range(8)]
        d=diagnostic(rr,3,n=8)
        self.assertTrue(d['exact']);self.assertFalse(d['admissible_by_maker'])
        self.assertTrue(diagnostic(rr,3,n=9)['admissible_by_maker'])
    def test_milp_known_pattern_alternative(self):
        from alternatives_r254 import solve
        rr=[row(0,'red',0),row(2,'yellow',1),row(4,'red',2)]
        result=solve(rr,[[0],[2,3],[4]],2)
        self.assertEqual(result['status'],0);self.assertEqual(result['minimum_changes'],1)
        self.assertEqual(result['indices'],[0,3,4])
        self.assertEqual(solve(rr,[[0],[2],[4]],2)['status'],2)
    def test_known_pattern_partial_prediction(self):
        palette=['red','yellow','black','red','black','yellow','yellow']
        train=[row(k,palette[k%7]) for k in range(28) if palette[k%7]!='black']
        d=diagnostic(train,7,35);self.assertTrue(d['exact']);self.assertEqual(d['template'],'RY?R?YY')
        for k in range(28,35):
            if d['template'][k%7]!='?':self.assertEqual(d['template'][k%7],palette[k%7][0].upper())
    def test_camera_geometry_ray_controls(self):
        import numpy as np
        from camera_r254 import Model,rays
        from tangent_circles import first_hits
        p=np.array([.5,.2,2.,-1.,82.,35.]+[0.]*8)
        for focal in [0.,4799.175227618243,9598.350455236487]:
            m=Model(2670,1,p,focal);g=m.geometry(np.arange(2670))
            plane=np.c_[m.plane,np.zeros(len(m.plane))]
            np.testing.assert_allclose(m.view.project(plane),m.seed_image_curve+p[2:4],atol=1e-9)
            xyz=g['centers'][::17];xy=m.view.project(xyz);base=m.view.base(xy);direction=m.view.directions(xy);v=xyz-base
            np.testing.assert_allclose(np.cross(v,direction),0,atol=1e-10)
            gg=m.geometry([0,2670]);np.testing.assert_allclose(gg['centers'][0],gg['centers'][1],atol=1e-10)
            a=rays(m,xy,g)
            if not focal:
                b=first_hits(m,xy,g);np.testing.assert_array_equal(a[0],b[0]);np.testing.assert_array_equal(a[2],b[2])
            self.assertEqual(a[2].sum(),0)

if __name__=='__main__':unittest.main()
