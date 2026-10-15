"""Real-data/analytic contracts; no generated photographic truth scenes."""
import unittest
from copy import deepcopy
import numpy as np
from photo2.r294.geometry import Chain as R294
from photo2.r279.geometry import R,SURFACE
from .common import *
from .geometry import Chain,extend,AXES
from .physical_audit import independent_support
from .contact_fallback import audit_pair
from .fit import Objective

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read(EVIDENCE/'inputs.json.gz');cls.inputs=cls.data['r294'];cls.p=extend(read(ROOT/'photo2/r294/results/revised.json')['selected']['parameters'])
    def test_baseline_geometry_and_first_hit(self):
        a=R294(self.p,self.inputs);b=Chain(self.p,self.inputs);np.testing.assert_allclose(a.pc,b.pc,atol=1e-8)
        xy=np.concatenate([pixels(r['pixels']) for r in self.data['rows'] if r['kind']=='patch']);np.testing.assert_array_equal(a.trace(xy)['owner'],b.trace(xy)['owner'])
    def test_transformed_literal_surface_zero(self):
        for radius,axial in [(R,.8),(2.1109157489,1.1),(R,1.)]:
            p=dict(self.p,radius=radius,axial=axial);s=Chain(p,self.inputs);self.assertLess(np.max(abs(s.local_sdf(SURFACE*s.dims))),1e-10)
    def test_independent_analytic_support_contains_surface(self):
        s=Chain(dict(self.p,axial=.83),self.inputs);rng=np.random.default_rng(295);n=rng.normal(size=(150,3));n/=np.linalg.norm(n,axis=1)[:,None];t=np.tile([1.,0.,0.],(len(n),1))
        np.testing.assert_allclose(s.support(n,t),independent_support(n,t,s.radius,s.axial),atol=1e-12)
        surface=SURFACE*s.dims;self.assertTrue(np.all((n@surface.T).max(1)<=s.support(n,t)+1e-10))
    def test_geographic_training_excludes_whole_holdout_support(self):
        o=Objective();self.assertTrue(all(r['split']=='train' for r in o.rows))
        for r in o.rows:
            lo,hi=r['station_extent']
            for a,b in self.data['intervals']['validation']+self.data['intervals']['reserved']:
                self.assertTrue(hi<a-15 or lo>b+15,(r['id'],lo,hi))
        self.assertFalse(read(EVIDENCE/'freeze.json')['accepted_in_requested_window'])
    def test_source_rows_exact(self):
        old=self.inputs
        patches={r['source']['observation_id']:r['source'] for r in old['records']};regions={r['source']['record_id']:r['source'] for r in old['legacy_colored']}
        for r in self.data['rows']:self.assertEqual(r['original'],(patches if r['kind']=='patch' else regions)[r['id']])
    def test_contact_classification_and_fallback(self):
        rows=read(OUT/'inconclusive-volume-audit.json')['records'];self.assertEqual(rows[0]['audit']['state'],'demonstrated-interpenetration')
        p=read(OUT/'screen.json')['candidates'][rows[0]['candidate']]['parameters'];s=Chain(p,self.inputs);a,b=[k-int(s.indices[0]) for k in rows[0]['pair']]
        self.assertEqual(audit_pair(s,a,b),rows[0]['audit'])
        self.assertEqual(audit_pair(s,0,100)['state'],'certified-nonintersection')
    def test_pinhole_projection_ray_roundtrip(self):
        s=Chain(dict(self.p,perspective=.001,yaw=9.),self.inputs);xy=np.array([r['point'] for r in self.data['rows']]);d=s.trace(xy,True);ok=d['owner']>=0
        self.assertGreater(ok.sum(),50);np.testing.assert_allclose(s.project(d['points'][ok]),xy[ok],atol=1e-7)
        np.testing.assert_allclose(np.linalg.norm(d['normal'][ok],axis=1),1,atol=1e-10)
    def test_export_complete_and_uncertainty_same_hand(self):
        for path in OUT.glob('*-positions.json.gz'):
            rows=read(path)['records'];self.assertEqual([r['index'] for r in rows],list(range(-20,201)));self.assertTrue(all(not r['physical_identity_verified'] for r in rows))
        if (OUT/'R295-positions.json.gz').exists():
            hand=read(OUT/'R295-positions.json.gz')['parameters']['hand'];self.assertTrue(all(r['parameters']['hand']==hand for r in read(OUT/'final-sensitivity.json')['records']))
    def test_extended_occlusion_guards(self):
        p=read(EVIDENCE/'final-freeze.json')['models']['R295'];a=Chain(p,self.inputs);b=Chain(p,self.inputs,indices=np.arange(-65,271))
        xy=np.concatenate([pixels(r['pixels'])[::3] for r in self.data['rows']])
        def owners(s):
            o=s.trace(xy)['owner'];return np.where(o>=0,s.indices[np.maximum(o,0)],-999)
        np.testing.assert_array_equal(owners(a),owners(b))
    def test_preservation(self):
        d=read(EVIDENCE/'preservation.json.gz')
        for name,h in {**d['science'],**d['feedback']}.items():self.assertEqual(sha(ROOT/name),h,name)
if __name__=='__main__':unittest.main()
