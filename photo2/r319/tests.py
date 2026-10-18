"""Contracts for scientific meaning and the R319 model extension."""
import unittest
from copy import deepcopy
import numpy as np
from photo2.r306.evidence import load
from photo2.r318 import optics
from photo2.r315.model import bump
from photo2.r295.geometry import AXES
from .common import *
from .experiment import GeneralChain
from .local_model import Chain
from .bound_controls import RelaxedCompact
from .evidence import Evidence,gate

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read(OLD/'epoch2/best.json.gz')['parameters'];cls.data=load()[0];cls.epoch=read(OLD/'epoch2/epoch.json')
    def test_narrow_zero_exact(self):
        p=deepcopy(self.p);p.update(patch_centers=[33.,40.],patch_halfwidth=10.,patch_phase=[0.,0.],patch_spacing=[0.,0.],patch_tilt=[0.,0.],patch_cant=[0.,0.]);a=GeneralChain(self.p,self.data);b=Chain(p,self.data);np.testing.assert_array_equal(a.centers,b.centers)
        for k in AXES:np.testing.assert_array_equal(a.g[k],b.g[k])
    def test_local_orientation_preserves_centers_and_rigid_frames(self):
        p=deepcopy(self.p);p.update(patch_centers=[33.,40.],patch_halfwidth=10.,patch_tilt=[.5,-.5],patch_cant=[.5,0]);a=GeneralChain(self.p,self.data);b=Chain(p,self.data);np.testing.assert_array_equal(a.centers,b.centers)
        for key in AXES:np.testing.assert_allclose(np.linalg.norm(b.g[key],axis=1),1,atol=1e-12)
        np.testing.assert_allclose(np.sum(b.g[AXES[0]]*b.g[AXES[1]],axis=1),0,atol=1e-12)
    def test_narrow_support_compact(self):
        p=deepcopy(self.p);p.update(patch_centers=[33.,40.],patch_halfwidth=10.,patch_phase=[.01,0]);a=GeneralChain(self.p,self.data);b=Chain(p,self.data);mask=np.abs(a.indices-33)>=10;np.testing.assert_array_equal(a.centers[mask],b.centers[mask]);self.assertGreater(np.max(np.linalg.norm(a.centers-b.centers,axis=1)),.001)
    def test_relaxed_rate_identical_geometry(self):
        a=GeneralChain(self.p,self.data);b=RelaxedCompact(self.p,self.data);np.testing.assert_array_equal(a.centers,b.centers);np.testing.assert_array_equal(a.pc,b.pc)
    def test_inactive_legacy_keys(self):
        a=GeneralChain(self.p,self.data)
        for key in ['pitch','yaw','local_metric','local_turn','phase_transport','local_phase_bias']:
            p=deepcopy(self.p);p[key]=p.get(key,0)+.1;b=GeneralChain(p,self.data);np.testing.assert_array_equal(a.centers,b.centers)
    def test_map_binding_rejects_mutation(self):
        e=deepcopy(self.epoch);e['mapping']['auto-0063']=52
        with self.assertRaises(ValueError):optics.Engine(e)
    def test_principal_half_lattice_scaling(self):
        from photo2.r314.bright import components
        from photo2.r318.detect import principal
        yy,xx=np.mgrid[0:5:.5,0:6:.5];xy=np.c_[xx.ravel(),yy.ravel()];v=np.exp(-((xy[:,0]-2.4)**2+(xy[:,1]-1.7)**2));a=principal(2*xy,v);b=max(components(xy,v,step=.5),key=lambda z:z['peak_intensity']);np.testing.assert_allclose(np.array(a['point'])/2,b['weighted_centroid'],atol=1e-12)
    def test_geometric_veto_independent_of_emax(self):
        b=read(OUT/'baseline.json.gz')['geometry'];m=deepcopy(b);m['dual_count']+=1;self.assertFalse(gate(m,b)['passed']);m=deepcopy(b);m['cores'][0]['modal_fraction']-=.04;self.assertFalse(gate(m,b)['passed'])
if __name__=='__main__':unittest.main()
