"""Real-data and analytic geometry contracts; no synthetic scenes/images."""
import unittest
import numpy as np
from PIL import Image
from photo2.r279.geometry import SURFACE,sdf
from .common import *
from .geometry import Chain
from .fit import Objective

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=read(EVIDENCE/'inputs.json.gz')
        cls.models={k:read(OUT/(k+'.json'))['selected']['parameters'] for k in ('initial','revised')}

    def test_exact_source_observations(self):
        source={r['observation_id']:r for r in read(ROOT/'photo2/r293/results/phase1-observations.json.gz')['records']}
        for r in self.inputs['records']:self.assertEqual(r['source'],source[r['source']['observation_id']])
        for p,h in self.inputs['sources'].items():self.assertEqual(sha(ROOT/p),h)

    def test_rejections_and_unknowns_preserved(self):
        for r in self.inputs['completed_r293_reviews']:
            if r['answer']=='wrong-clear':self.assertIsNone(r['accepted_candidate'])
            self.assertFalse(r['rejected_centroid_used'])
        for r in self.inputs['records']:
            self.assertIsNone(r['source']['uncertainty']['physical_identity'])
            self.assertIsNone(r['source']['physical_material_color'])

    def test_anchor_native_crossing(self):
        native,_,_=photo();np.testing.assert_array_equal(np.array(Image.open(EVIDENCE/'anchor-native.png')),native[205:345,1400:1650])
        a=self.inputs['anchor_selection'];self.assertEqual(a['record_id'],'C-1497-0271')
        self.assertLess(a['signed_extent'][0],0);self.assertGreater(a['signed_extent'][1],0)

    def test_training_geographic_separation(self):
        obj=Objective(self.inputs)
        for r in obj.rows+obj.old:
            self.assertEqual(r['split'],'train')
            self.assertNotEqual(int(np.floor((r['along_px']+60)/120))%4,2)
        hold={r['source']['observation_id'] for r in self.inputs['records'] if r['split']=='holdout'}
        self.assertFalse(hold&{r['source']['observation_id'] for r in obj.rows})

    def test_literal_surface_and_fixed_minor_radius(self):
        np.testing.assert_allclose(sdf(SURFACE),0,atol=2e-12)
        for p in self.models.values():
            s=Chain(p,self.inputs);np.testing.assert_allclose(np.linalg.norm(s.centers-s.line,axis=1),4,atol=2e-12)
            np.testing.assert_allclose(s.line[:,2],0,atol=1e-12)
            np.testing.assert_allclose(np.linalg.norm(s.g['surface_tangent'],axis=1),1,atol=1e-12)

    def test_requested_sequence_and_uncertainty(self):
        for stage in self.models:
            d=read(OUT/(stage+'-positions.json.gz'));rows=d['records']
            self.assertEqual([r['index'] for r in rows],list(range(-20,201)))
            for r in rows:
                self.assertFalse(r['physical_identity_verified']);self.assertIsNone(r['color'])
                self.assertIsNone(r['uncertainty']['physical_identity_probability'])
                self.assertGreaterEqual(r['uncertainty']['local_parameter_sensitivity_radius_px'],0)

    def test_primary_physical_certificates(self):
        for stage,p in self.models.items():
            self.assertTrue(Chain(p,self.inputs).certify()['certified'],stage)
        rejected=read(OUT/'unconstrained-penetration.json')
        self.assertGreater(rejected['sampled_penetrating_pairs'],0)

    def test_no_end_occluder_truncation(self):
        xy=np.concatenate([pixels(r['source']['native_bright_patch']) for r in self.inputs['records'] if r['fit_eligible']])
        for p in self.models.values():
            a=Chain(p,self.inputs);b=Chain(p,self.inputs,np.arange(-65,271))
            x=a.trace(xy);y=b.trace(xy)
            def labels(s,d):
                o=np.full(len(xy),-999);ok=d['owner']>=0;o[ok]=s.indices[d['owner'][ok]];return o
            oa=labels(a,x);ob=labels(b,y);relevant=((oa>=-20)&(oa<=200))|((ob>=-20)&(ob<=200))
            np.testing.assert_array_equal(oa[relevant],ob[relevant]);np.testing.assert_array_equal(x['unknown'][relevant],y['unknown'][relevant])

    def test_review_native_crops(self):
        native,_,_=photo();m=read(REVIEW/'manifest.json')
        self.assertGreaterEqual(len(m['crops']),8)
        for c in m['crops']:
            x0,y0,x1,y1=c['box'];np.testing.assert_array_equal(np.array(Image.open(REVIEW/c['native'])),native[y0:y1,x0:x1])

if __name__=='__main__':unittest.main()
