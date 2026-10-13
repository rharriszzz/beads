"""Numerical correctness tests, not simulated bead positions or identity truth."""
import unittest
import numpy as np
from skimage.morphology import h_maxima
from .audit_r267 import averages,exact_prominence,rank,METRICS

class AuditTests(unittest.TestCase):
    def test_native_neighborhoods(self):
        v=np.zeros((11,11),np.uint8);v[5,5]=255
        a=averages(v,5,5)
        for key,n in zip(METRICS,[25,49,81,13,29,49]):self.assertAlmostEqual(a[key],255/n)
    def test_equal_rank_and_no_uint8_overflow(self):
        v=np.full((11,11),255,np.uint8);a=averages(v,5,5)
        self.assertEqual(set(a.values()),{255.})
        rows=[dict(a),dict(a),{k:100. for k in METRICS}];rank(rows)
        for k in METRICS:self.assertEqual([r['rank_'+k] for r in rows],[1,1,3])
    def test_prominence_against_hmax(self):
        v=np.array([[0,0,0,0,0,0,0],[0,9,7,5,6,8,0],[0,0,0,0,0,0,0]],np.uint8)
        pts=[(1,1),(5,1)];result=exact_prominence(v,pts,[0,0,7,3])
        self.assertEqual([p[0] for p in result],[9,3])
        for h in range(1,11):
            mask=h_maxima(v,h,footprint=np.ones((3,3)))
            self.assertEqual([bool(mask[y,x]) for x,y in pts],[p[0]>=h for p in result])
    def test_escape_certificate_expands(self):
        v=np.zeros((5,150),np.uint8);v[2,2:145]=8;v[2,3]=10;v[2,140]=12
        p=exact_prominence(v,[(3,2)],[1,1,5,4])[0]
        self.assertEqual(p[:2],(2,8));self.assertIn('256',p[2])

if __name__=='__main__':unittest.main()
