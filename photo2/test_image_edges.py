"""Numerical controls and known-edge synthetic image checks."""
import unittest
import numpy as np
from image_edges import chromaticity, interpolate, objective, optimize, transition_scores


class ImageEdgeTests(unittest.TestCase):
    def test_chromaticity_invariant_to_scalar_shade(self):
        colors=np.array([[.8,.25,.65],[.2,.04,.05],[.1,.08,.09]])
        np.testing.assert_allclose(chromaticity(colors),chromaticity(colors*.17),atol=1e-14)

    def test_interpolated_force_continuous_and_correct(self):
        grid=np.broadcast_to(np.arange(-5.,6),(3,2,11)).copy()
        values=np.sin(grid/3)
        for coordinate in [-2.,-.3,1.4]:
            x=np.full((3,2),coordinate)
            val,der=interpolate(grid,values,x)
            plus=interpolate(grid,values,x+1e-6)[0];minus=interpolate(grid,values,x-1e-6)[0]
            np.testing.assert_allclose(der,(plus-minus)/2e-6,atol=2e-7)
        left=interpolate(grid,values,np.full((3,2),-2.-1e-8))[1]
        right=interpolate(grid,values,np.full((3,2),-2.+1e-8))[1]
        np.testing.assert_allclose(left,right,atol=1e-8)

    def test_full_objective_gradient_includes_cyclic_smoothing(self):
        base=np.tile([-50.,50.],(6,1))
        grid=base[:,:,None]+np.arange(-24.,25)
        score=np.sin(grid/7)*.4
        x=base+np.array([[1.3,-2.2],[2.1,-1.1],[-1.5,2.7],[.4,-3.3],[1.7,4.8],[-2.6,1.9]])
        args=(grid,score,base,np.full(6,99.),np.full((6,2),8.),8.,4.)
        exact=objective(x.ravel(),*args)[1]
        flat=x.ravel();numeric=np.empty_like(flat)
        for j in range(len(flat)):
            step=np.zeros_like(flat);step[j]=1e-5
            numeric[j]=(objective(flat+step,*args)[0]-objective(flat-step,*args)[0])/2e-5
        np.testing.assert_allclose(exact,numeric,atol=1e-7,rtol=1e-6)

    def synthetic(self,shadow=False,flat=False):
        rgb=np.zeros((460,500,3),float);rgb[:]=[.8,.3,.65]
        if not flat:rgb[:,200:301]=[.7,.08,.06]
        if shadow:
            shade=np.where(np.arange(500)<=300,1.,.35+.65*np.minimum((np.arange(500)-300)/90,1))
            rgb*=shade[None,:,None]
        rgb=np.rint(rgb*255).astype('uint8')
        xy=np.column_stack([np.full(16,250.),np.linspace(60,400,16)])
        n=np.tile([1.,0.],(16,1));t=np.tile([0.,1.],(16,1))
        base=np.tile([-54.,54.],(16,1))
        grid,score,_=transition_scores(rgb,xy,n,t,base,base)
        return grid,score,base

    def test_known_red_band_edges_with_cast_shadow(self):
        for shadow in [False,True]:
            grid,score,base=self.synthetic(shadow=shadow)
            x,result=optimize(grid,score,base,np.full(16,101.),np.ones((16,2),bool))
            self.assertTrue(result['success'])
            # Pixel centers 200..300 imply half-pixel silhouette edges.
            np.testing.assert_allclose(x,np.tile([-50.5,50.5],(16,1)),atol=2.)

    def test_flat_paper_does_not_invent_image_force(self):
        grid,score,base=self.synthetic(flat=True)
        self.assertLess(np.max(np.abs(score)),1e-12)
        clear=np.ones((16,2),bool);expected=np.full(16,100.)
        x,_=optimize(grid,score,base,expected,clear,image_weight=4.)
        zero,_=optimize(grid,score,base,expected,clear,image_weight=0.)
        np.testing.assert_allclose(x,zero,atol=1e-9)


if __name__=='__main__':unittest.main()
