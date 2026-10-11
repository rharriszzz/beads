"""Transform fidelity and rejection tests; phantoms are signals, not bead renders."""
import unittest
import numpy as np
from photo2.fft_curvature import Curve, mapped_patch, analyze
from photo2 import fft_helicity as base

class Straight:
    def at(self,s):
        s=np.asarray(s);xy=np.stack([256+s,np.zeros_like(s)+256],axis=-1)
        t=np.broadcast_to([1.,0.],xy.shape);n=np.broadcast_to([0.,1.],xy.shape)
        return xy,t,n
    def metric(self,s,r,stretch=1):
        return dict(turn_rms_deg=0.,turn_range_deg=0.,jacobian_min_visible=1.,jacobian_min_3sigma=1.,max_abs_curvature=0.)

class CurvatureChecks(unittest.TestCase):
    def setUp(self):
        self.q=dict(id='test',s=0.,xy=[256,256],tangent=[1.,0.],tangent_deg=0.,radius=18.,diameter=16.)
        y,x=np.mgrid[:513,:513];self.rgb=np.repeat((.5+.2*np.cos(2*np.pi*(x/16+y/32)+.7))[:,:,None],3,axis=2).astype('float32')

    def test_straight_warp_equals_long_window_and_preserves_brightness(self):
        b,g,_=mapped_patch(self.rgb,self.q,Straight(),'B');c,h,_=mapped_patch(self.rgb,self.q,Straight(),'C')
        np.testing.assert_array_equal(b,c);np.testing.assert_array_equal(g,h)
        c,_,_=mapped_patch(np.full_like(self.rgb,.37),self.q,Straight(),'C')
        np.testing.assert_allclose(c,.37,atol=1e-7)

    def test_axis_aligned_adapter_matches_native_and_phase(self):
        a,x=analyze(self.rgb,self.q,Straight(),'A','V');b,y=base.analyze(self.rgb,self.q,'V')
        np.testing.assert_allclose(x['f'],y['f'],rtol=2e-5,atol=.0001)
        self.assertEqual(a['peaks'][0]['offset'],b['peaks'][0]['offset'])
        inv=base.inverse_pairs(x['f'],a['peaks'][:1]);direct=base.inverse_pairs(y['f'],b['peaks'][:1])
        np.testing.assert_allclose(inv,direct,atol=1e-6)

    def test_curved_phase_field_straightening_recovers_signed_frequency(self):
        y,x=np.mgrid[:769,:769];R=180.;cx=cy=384.
        u=R*np.arctan2(y-cy,x-cx);v=R-np.hypot(x-cx,y-cy)
        field=.5+.2*np.cos(2*np.pi*(u/20+v/32)+.61)
        rgb=np.repeat(field[:,:,None],3,axis=2).astype('float32')
        theta=np.linspace(0,2*np.pi,8001);curve=Curve(np.column_stack((cx+R*np.cos(theta),cy+R*np.sin(theta))))
        q=dict(self.q,xy=[cx+R,cy],radius=18.,diameter=20.)
        rec,a=analyze(rgb,q,curve,'C','V');p=rec['peaks'][0]
        k=np.array(p['offset'])/rec['n'];target=np.array([1/20,-1/32])
        self.assertLess(min(np.linalg.norm(k-target),np.linalg.norm(k+target)),1.5/rec['n'])
        half=len(a['patch'])//2;yy,xx=np.mgrid[-half:half+1,-half:half+1]
        ideal=.5+.2*np.cos(2*np.pi*(xx/20+yy/32)+.61)
        self.assertLess(np.sqrt(np.mean((a['patch'][:,:,0]-ideal)**2)),.004)
        self.assertGreater(rec['geometry']['jacobian_min_3sigma'],.69)

    def test_fold_and_outside_support_are_rejected(self):
        theta=np.linspace(0,2*np.pi,1001);curve=Curve(np.column_stack((256+40*np.cos(theta),256+40*np.sin(theta))))
        with self.assertRaisesRegex(ValueError,'Fold'):
            mapped_patch(self.rgb,self.q,curve,'C')
        with self.assertRaisesRegex(ValueError,'Outside'):
            mapped_patch(self.rgb,dict(self.q,s=255),Straight(),'A')

    def test_perturbation_matching_is_one_to_one_and_keeps_ambiguity(self):
        from photo2.fft_curvature_report import stable_pairs
        def peak(i,a):return dict(candidate=i,relative_angle=a,fd=1.)
        primary=dict(peaks=[peak(1,10),peak(2,12)])
        other=dict(peaks=[peak(1,11)])
        stability,_=stable_pairs(primary,[other])
        self.assertEqual(sum(p['fraction'] for p in stability),1.)
        _,ambiguous=stable_pairs(other,[primary])
        self.assertEqual(ambiguous,1)

    def test_circular_gaussian_weights_and_four_sigma_tail(self):
        _,g3,_=mapped_patch(self.rgb,self.q,Straight(),'A')
        _,g4,_=mapped_patch(self.rgb,self.q,Straight(),'A',dict(extent=4))
        c=len(g4)//2;r=int(self.q['radius'])
        self.assertAlmostEqual(float(g4[c+r,c]),float(g4[c,c+r]),places=7)
        self.assertAlmostEqual(float(g4[c+3*r,c+4*r]),float(g4[c-3*r,c-4*r]),places=7)
        h=len(g3)//2;np.testing.assert_array_equal(g4[c-h:c+h+1,c-h:c+h+1],g3)
        self.assertAlmostEqual(float(g4[c,-1]),np.exp(-8),places=8)

    def test_rotating_signal_and_elliptical_mask_rotates_fft(self):
        n=129;y,x=np.mgrid[-64:65,-64:65]
        a=np.cos(2*np.pi*(7*x+11*y)/n+.3)
        g=np.exp(-.5*((x/24)**2+(y/12)**2))
        mag=abs(np.fft.fftshift(np.fft.fft2(a*g)))
        turned=abs(np.fft.fftshift(np.fft.fft2(np.rot90(a)*np.rot90(g))))
        np.testing.assert_allclose(turned,np.rot90(mag),atol=1e-10)

    def test_zero_signal_has_no_manufactured_noncentral_pairs(self):
        r,_=analyze(np.zeros_like(self.rgb),self.q,Straight(),'B','Y')
        self.assertEqual(r['peaks'],[])

if __name__=='__main__':unittest.main()
