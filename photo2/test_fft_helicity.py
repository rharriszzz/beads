"""Meaningful source-parity, transform, tracking and geometry checks for R243."""
import ast, copy, unittest
from pathlib import Path
import numpy as np
from photo2 import fft_explorer_core as core
from photo2.fft_helicity import analyze, inverse_pairs, predicted, score, track, wrap, ROOT

class FFTChecks(unittest.TestCase):
    def test_source_excerpts_unchanged(self):
        source=ROOT.parent/'fft-image-explorer/fft_image_explorer.py'
        if not source.exists(): self.skipTest('optional pinned sibling source unavailable')
        original={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        actual={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(Path(core.__file__).read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        for name,node in actual.items():self.assertEqual(node,original[name],name)

    def test_source_gaussian_and_channels(self):
        n=101; sigma=15.; g=core.make_mask((n,n),'Rectangle','Gaussian',50,50,100,100,0,.3)
        y,x=np.mgrid[:n,:n];np.testing.assert_allclose(g,np.exp(-((x-50)**2+(y-50)**2)/(2*sigma**2)),atol=5e-8)
        rgb=np.array([[[1.,0,0],[1,1,0],[0,0,0]]],np.float32);b=core.make_channel_bank(rgb)
        np.testing.assert_allclose(b.arrays['HSV V'],[[1,1,0]])
        np.testing.assert_allclose(b.arrays['Y luminance'],[[.299,.886,0]],atol=1e-6)

    def test_even_odd_complex_pair_reconstruction(self):
        for n in (64,65):
            yy,xx=np.mgrid[:n,:n];x=np.cos(2*np.pi*(5*xx-7*yy)/n+.7)
            f=np.fft.fftshift(np.fft.fft2(x));a=inverse_pairs(f,[{'offset':[5,7]}])
            np.testing.assert_allclose(a,x,atol=1e-12)
            p=core.find_top_fft_peaks(np.log1p(abs(f)),top_k=2,min_distance=2)
            self.assertEqual(p[0]['distance'],0)
            self.assertAlmostEqual(p[1]['distance'],np.hypot(5,7))

    def test_no_forced_peaks_and_gain_invariance(self):
        q=dict(id='test',xy=[128,128],radius=20.,diameter=16.,tangent=[1,0],tangent_deg=0)
        rgb=np.zeros((257,257,3),np.float32);r,_=analyze(rgb,q,'V');self.assertFalse(r['peaks'])
        yy,xx=np.mgrid[:257,:257];a=.4+.1*np.cos(2*np.pi*(xx/16+yy/32))
        rgb=np.repeat(a[:,:,None],3,axis=2).astype('float32')
        r,_=analyze(rgb,q,'V');s,_=analyze(rgb*.5,q,'V')
        self.assertGreater(len(r['peaks']),0)
        self.assertEqual(r['peaks'][0]['offset'],s['peaks'][0]['offset'])
        self.assertAlmostEqual(r['peaks'][0]['band_fraction'],s['peaks'][0]['band_fraction'],places=6)
        self.assertAlmostEqual(r['peaks'][0]['pair_power']/s['peaks'][0]['pair_power'],4,places=5)

    def test_reciprocal_normals_and_tangent_reversal(self):
        # At a top-down limit, true geometric normals to rows agree with model.
        for h in (-1,1):
            p=predicted(0,h,89.999,0)
            rev=predicted(180,h,89.999,0)
            for a,b in zip(p,rev):
                self.assertAlmostEqual(float(wrap(a['relative_angle']-b['relative_angle'])),0,places=7)
                self.assertAlmostEqual(a['fd'],b['fd'],places=7)
        p=predicted(0,1,89.999,0);m=predicted(0,-1,89.999,0)
        for a,b in zip(p,m):self.assertAlmostEqual(float(wrap(a['relative_angle']+b['relative_angle'])),0,places=7)
        expected=np.degrees(np.arctan(.443292307273487/(6.1109157489*2*np.pi/6.5)))
        self.assertAlmostEqual(abs(p[0]['relative_angle']),expected,places=6)

    def test_image_roll_is_not_world_azimuth_gauge(self):
        base=predicted(20,1,45,0)
        rotated=predicted(65,1,45,45)
        changed=predicted(20,1,45,45)
        for a,b in zip(base,rotated):
            self.assertAlmostEqual(float(wrap(a['relative_angle']-b['relative_angle'])),0,places=7)
            self.assertAlmostEqual(a['fd'],b['fd'],places=7)
        self.assertGreater(max(abs(float(wrap(a['relative_angle']-b['relative_angle']))) for a,b in zip(base,changed)),.1)

    def test_track_gap_and_competing_links(self):
        def peak(a):return dict(candidate=1,relative_angle=a,fd=1.,angle_uncertainty=5.)
        rs=[dict(window='a',peaks=[peak(10)]),dict(window='b',peaks=[]),dict(window='c',peaks=[peak(11),dict(peak(12),candidate=2)])]
        links=track(rs);self.assertEqual(links[0]['gap'],2)
        self.assertEqual(rs[0]['peaks'][0]['track'],rs[2]['peaks'][0]['track'])
        self.assertNotEqual(rs[2]['peaks'][0]['track'],rs[2]['peaks'][1]['track'])

if __name__=='__main__':unittest.main()
