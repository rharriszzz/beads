"""Geometry and failure controls for width-constrained shadow correction."""
import unittest
import numpy as np

from width_correction import normal_hits, fit_width, constrain, shadow_extent


class WidthCorrectionTests(unittest.TestCase):
    def test_normal_intersections_measure_annulus_width(self):
        angle=np.linspace(0,2*np.pi,721)
        inner=90*np.column_stack([np.cos(angle),np.sin(angle)])
        outer=110*np.column_stack([np.cos(angle),np.sin(angle)])
        normal=np.array([[1.,0.],[0.,1.],[-1.,0.],[0.,-1.]])
        xy=normal*100
        a=normal_hits(xy,normal,inner);b=normal_hits(xy,normal,outer)
        np.testing.assert_allclose(b-a,20,atol=1e-8)
        self.assertTrue((a*b<0).all())

    def test_robust_fit_recovers_increasing_width_with_contamination(self):
        y=np.linspace(0,1000,100);w=80+.02*y;w[::10]+=40
        expected,report=fit_width(y,w,np.ones(100,bool),1000)
        np.testing.assert_allclose(expected,80+.02*y,atol=1.)
        self.assertGreater(report['coefficients'][1],0)

    def test_nonnegative_model_does_not_invent_positive_slope(self):
        y=np.linspace(0,1000,100);w=100-.01*y
        _,report=fit_width(y,w,np.ones(100,bool),1000)
        self.assertLess(abs(report['coefficients'][1]),1e-5)
        self.assertLess(report['free_coefficients'][1],0)

    def test_missing_vertical_coverage_rejected(self):
        y=np.linspace(400,500,100)
        with self.assertRaises(ValueError):fit_width(y,np.full(100,95.),np.ones(100,bool),1000)

    def fixture(self):
        y=np.arange(40,dtype=float)
        xy=np.column_stack([np.full(40,10.),y]);inner=np.column_stack([np.full(40,70.),y]);outer=np.column_stack([np.full(40,-50.),y])
        return xy,inner,outer,np.full(40,120.),np.full(40,100.)

    def test_clear_edge_anchored_and_center_moves_half_width_excess(self):
        xy,inner,outer,w,e=self.fixture();yes=np.ones(40,bool);no=~yes
        ni,no_,nc,g,strong,_,_=constrain(xy,inner,outer,w,e,5,no,yes,yes,no)
        np.testing.assert_array_equal(no_,outer)
        np.testing.assert_allclose(ni[:,0],50)
        np.testing.assert_allclose(nc[:,0],0,atol=1e-12)
        self.assertTrue(strong.all())
        self.assertTrue((g==1).all())

    def test_swapping_inner_outer_keeps_geometry(self):
        xy,inner,outer,w,e=self.fixture();yes=np.ones(40,bool);no=~yes
        a=constrain(xy,inner,outer,w,e,5,no,yes,yes,no)
        b=constrain(xy,outer,inner,w,e,5,yes,no,no,yes)
        np.testing.assert_allclose(a[0],b[1]);np.testing.assert_allclose(a[1],b[0]);np.testing.assert_allclose(a[2],b[2])

    def test_both_or_neither_clear_abstains(self):
        xy,inner,outer,w,e=self.fixture();yes=np.ones(40,bool);no=~yes
        for flags in [yes,no]:
            ni,no_,nc,g,_,_,_=constrain(xy,inner,outer,w,e,5,flags,flags,yes,yes)
            np.testing.assert_array_equal(ni,inner);np.testing.assert_array_equal(no_,outer);np.testing.assert_array_equal(nc,xy)
            self.assertFalse(g.any())

    def test_no_excess_width_abstains(self):
        xy,inner,outer,w,e=self.fixture();yes=np.ones(40,bool);no=~yes
        result=constrain(xy,inner,outer,w,w+10,5,no,yes,yes,no)
        np.testing.assert_array_equal(result[2],xy)

    def test_shadow_extent_and_out_of_frame_reference(self):
        hsv=np.zeros((300,500,3));hsv[:]=[.9,.5,.8];hsv[:,50:110,2]=.4
        edge=np.array([[50.,150.],[490.,150.]])
        result=shadow_extent(hsv,edge,np.array([[1.,0.],[1.,0.]]),np.array([[0.,1.],[0.,1.]]))
        self.assertTrue(56<=result[0]['extent_px']<=64)
        self.assertFalse(result[0]['censored'])
        self.assertIsNone(result[1]['extent_px'])


if __name__=='__main__':unittest.main()
