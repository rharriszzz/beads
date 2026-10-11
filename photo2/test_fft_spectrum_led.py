"""R248: phase/geometry, source-mask parity and cutoff-artifact checks."""
import unittest
import numpy as np
from photo2.fft_spectrum_led import core,products,filter_fft,extract,inverse_pairs,reciprocal_alternatives,sample


class SpectrumChecks(unittest.TestCase):
    def scene(self,sigma=20,constant=False,mirror=1):
        y,x=np.mgrid[:601,:601]
        z=np.full(x.shape,.4)
        if not constant:
            for kx,ky,phase in [(.03,0,.7),(.01,.04,-.4),(.04,.04,1.2)]:
                z+=.1*np.cos(2*np.pi*(mirror*kx*x-ky*y)+phase)
        rgb=np.repeat(z[...,None],3,axis=2).astype('float32')
        return products(rgb,{'xy':[300,300]},sigma,'V')

    def test_source_filter_parity(self):
        for sigma in (20,30,55):
            a=self.scene(sigma)
            for lo,hi in [(.01,.08),(.025,.05),(0,np.sqrt(.5))]:
                reference=core.compute_fft_products(a['x'],a['g'],False,square_fft=False,fft_highpass_percent=lo*100*np.sqrt(2),fft_lowpass_percent=hi*100*np.sqrt(2))[6]
                np.testing.assert_array_equal(filter_fft(a,lo,hi),reference)

    def test_native_circle_five_sigma(self):
        a=self.scene(20);n=a['n'];c=n//2;y,x=np.mgrid[:n,:n];r=np.hypot(x-c,y-c)
        expected=np.where(r<=100,np.exp(-r*r/800),0)
        np.testing.assert_allclose(a['g'],expected,atol=7e-8)
        np.testing.assert_array_equal(a['g'],np.rot90(a['g']))
        self.assertEqual(a['origin'],[200,200]);self.assertEqual(n,201)

    def test_cutoff_cannot_manufacture_gaussian_ring_peaks(self):
        a=self.scene(40,constant=True);r=extract(a,.008,.025)
        self.assertEqual(r['peaks'],[])
        self.assertTrue(any('cutoff-created' in p['reason'] for p in r['rejected']))

    def test_zero_input_has_no_forced_noncentral_peaks(self):
        rgb=np.zeros((601,601,3),np.float32)
        a=products(rgb,{'xy':[300,300]},20,'Y')
        self.assertEqual(extract(a,.01,.1)['peaks'],[])

    def test_phase_and_both_mirror_reciprocal_bases(self):
        for mirror in (-1,1):
            a=self.scene(55,mirror=mirror);r=extract(a,.01,.08)
            exact=np.array([[.03,0],[.01,.04],[.04,.04]])*[mirror,1]
            for k in exact:
                self.assertLess(min(min(np.linalg.norm(np.array(p['offset'])/a['n']-k),np.linalg.norm(np.array(p['offset'])/a['n']+k)) for p in r['peaks']),1/a['n'])
            # A single-bin conjugate inverse agrees with its complex phase,
            # including the odd native crop's origin and negative image y.
            p=r['peaks'][0];dx,dy=p['offset'];n=a['n'];c=n//2;y,x=np.mgrid[:n,:n]
            coeff=a['f'][c-dy,c+dx]
            expected=2*np.real(coeff*np.exp(2j*np.pi*(dx*x-dy*y)/n))/n**2
            np.testing.assert_allclose(inverse_pairs(a['f'],[p]),expected,atol=1e-12)
            alts=reciprocal_alternatives(r['peaks'],n,r['frequency_resolution'])
            self.assertTrue(alts)
            for alt in alts:
                B=np.column_stack([np.array(r['peaks'][i-1]['offset'])/n*s for i,s in zip(alt['basis_candidates'],alt['basis_signs'])])
                np.testing.assert_allclose(B.T@np.array(alt['direct_columns']).T,np.eye(2),atol=1e-12)


if __name__=='__main__':unittest.main()
