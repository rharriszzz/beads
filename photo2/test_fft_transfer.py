import copy,unittest
import numpy as np
from photo2.fft_transfer import qualify,match_triplets


class TransferChecks(unittest.TestCase):
    def triplet(self,mirror=1):
        return [dict(candidate=i+1,offset=[int(x*1000*mirror),int(y*1000)],frequency=float(np.hypot(x,y)),relative_angle=float(np.degrees(np.arctan2(y,x*mirror))),frequency_resolution=.001,boundary_clipped=False,weak=False) for i,(x,y) in enumerate([(.03,0),(0,.04),(.03,.04)])]

    def test_mirrors_closure_and_no_forced_result(self):
        for mirror in (-1,1):
            ps=self.triplet(mirror);r=dict(peaks=ps,n=1000,frequency_resolution=.001,tangent_deg=0)
            trios,_=qualify(r);self.assertEqual(len(trios),1);self.assertTrue(trios[0]['supported'])
            ps[2]['weak']=True;trios,_=qualify(r);self.assertFalse(trios[0]['supported']);self.assertIn('weak member',trios[0]['limitations'])
            ps[2]['weak']=False;ps[0]['boundary_clipped']=True;trios,_=qualify(r);self.assertFalse(trios[0]['supported'])
            r['peaks']=ps[:2];self.assertEqual(qualify(r)[0],[])

    def test_axial_one_to_one_match_and_missing_pair(self):
        ps=self.triplet();rev=copy.deepcopy(ps[::-1])
        for p in rev:p['relative_angle']+=180
        self.assertTrue(match_triplets(ps,rev));self.assertEqual(match_triplets(ps,rev[:2]),[])
        duplicated=[copy.deepcopy(ps[0]) for _ in range(3)];self.assertEqual(match_triplets(ps,duplicated),[])
        shifted=copy.deepcopy(ps)
        for p in shifted:p['frequency']*=2
        self.assertEqual(match_triplets(ps,shifted),[])

    def test_harmonic_collinear_peaks_are_not_three_directions(self):
        ps=self.triplet()
        for p,x in zip(ps,(10,20,30)):p.update(offset=[x,0],frequency=x/1000,relative_angle=0)
        r=dict(peaks=ps,n=1000,frequency_resolution=.001,tangent_deg=0)
        self.assertEqual(qualify(r)[0],[])


if __name__=='__main__':unittest.main()
