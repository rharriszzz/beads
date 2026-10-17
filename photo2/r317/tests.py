import unittest
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r316.model import Chain
from photo2.r316.renderer import RayLayers
from photo2.r315.model import refined_trace
from .search import check,vals
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read(ROOT/'photo2/r316/results/joint-recovery-model.json.gz')['parameters'];cls.data=load()[0]
    def test_extended_zero_preserves_geometry(self):
        q=deepcopy(self.p);q['compact_centers']+=[-26,26]
        for key in ['compact_phase','compact_spacing','compact_tilt']:q[key]+=[0.,0.]
        a,b=Chain(self.p,self.data),Chain(q,self.data)
        np.testing.assert_array_equal(a.centers,b.centers)
        for k in a.g:np.testing.assert_array_equal(a.g[k],b.g[k])
    def test_hypotheses_never_merge_aliases(self):
        from photo2.r314.diagnostics import EARLY
        r=dict(early=[dict(id=k,best_visible=.7,visible={'-14':.7,'-15':.03}) for k in EARLY])
        self.assertEqual(vals(r,'A')[2],.7);self.assertEqual(vals(r,'B')[2],.03)
    def test_orientation_derivative_bound(self):
        q=deepcopy(self.p);q['orientation_halfwidth']=1
        with self.assertRaises(ValueError):check(q)
    def test_new_basis_cached_layers_match_oracle(self):
        q=deepcopy(self.p);q['compact_centers']+=[-26,26]
        for key in ['compact_phase','compact_spacing','compact_tilt']:q[key]+=[0.,0.]
        e=engine();xy=e.xy[::91];cache=RayLayers();cache.trace(Chain(q,self.data),xy);q['compact_tilt'][3]=2
        s=Chain(q,self.data);a=cache.trace(s,xy);b=refined_trace(s,xy)
        np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown'])
    def test_radial_cant_zero_is_identical(self):
        from .model import Chain as New
        a,b=Chain(self.p,self.data),New(self.p,self.data)
        np.testing.assert_array_equal(a.centers,b.centers)
        for k in a.g:np.testing.assert_array_equal(a.g[k],b.g[k])
    def test_radial_cant_rigid_and_centers_fixed(self):
        from .model import Chain as New
        from photo2.r295.geometry import AXES
        q=deepcopy(self.p);q['radial_cant']=5
        a,b=Chain(self.p,self.data),New(q,self.data)
        np.testing.assert_array_equal(a.centers,b.centers)
        frames=np.stack([b.g[k] for k in AXES],axis=1)
        np.testing.assert_allclose(frames@np.swapaxes(frames,1,2),np.tile(np.eye(3),(b.n,1,1)),atol=1e-12)
        np.testing.assert_allclose(np.sum(b.g[AXES[0]]*b.g['radial'],axis=1),-np.sin(np.radians(5)),atol=1e-12)
    def test_canted_layers_match_python_reference(self):
        from .model import Chain as New
        from photo2.r316.verify import original
        q=deepcopy(self.p);q['compact_cant']=[-4,0,4];s=New(q,self.data);e=engine();xy=e.xy[::101];a=RayLayers().trace(s,xy);b=original(s,xy);known=~b['unknown']
        np.testing.assert_array_equal(a['owner'][known],b['owner'][known])
if __name__=='__main__':unittest.main()
