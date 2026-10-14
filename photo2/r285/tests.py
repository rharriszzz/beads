"""Scientific mechanism, frozen evidence, provenance and measurement tests."""
import unittest
import numpy as np
from pathlib import Path
from scipy import ndimage as ndi
from photo2.r282.common import read,sha,pixels,validate
from .select import OUT
from .methods import component,basins
from .mechanisms import field
from .run import local_mask

class Mechanisms(unittest.TestCase):
    def test_strict_seed_no_substitution(self):
        mask=np.zeros((9,9),bool);mask[3:6,5:8]=True
        self.assertFalse(component(mask,[4,4]).any())
    def test_narrow_bright_continuation(self):
        lum,domain=field(.29);m,*_=basins(lum,domain,domain,[24,32]);self.assertTrue(m[32,46]);self.assertTrue(m[32,35])
    def test_dark_saddle(self):
        lum,domain=field(.025);m,*_=basins(lum,domain,domain,[24,32]);self.assertTrue(m[32,24]);self.assertFalse(m[32,46])
    def test_shading_is_not_split(self):
        lum,domain=field(.24);m,*_=basins(lum,domain,domain,[24,32]);self.assertTrue(m[32,46])
    def test_unobservable_body_ambiguity_preserved(self):
        results=read(OUT/'mechanisms.json');self.assertEqual(results[1]['support'],results[3]['support']);self.assertFalse(results[3]['right_feature_retained'])

class SavedEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev=read(OUT/'development.json.gz');cls.confirm=read(OUT/'confirmation.json.gz')
    def test_frozen_source_and_selection(self):
        freeze=read(OUT/'candidate-freeze.json');self.assertEqual(sha(Path(__file__).parent/'methods.py'),freeze['methods_sha256']);self.assertEqual(sha(OUT/'selection.json'),freeze['selection_sha256'])
    def test_control_bank_count(self):
        sel=read(OUT/'selection.json');self.assertEqual(sel['control_replayed_masks'],1421);self.assertEqual(len(sel['development']),16);self.assertEqual(len(self.dev['observations']),203)
    def test_confirmation_separation(self):
        from .select import OLD
        centers=[c['center'] for c in read(OLD/'cases.json')];prior=[]
        for r in read(OUT/'selection.json')['confirmation']:
            self.assertTrue(all(np.linalg.norm(np.array(r['seed'])-c)>180 for c in centers+prior));prior.append(r['seed'])
    def test_records_and_centroids(self):
        for o in self.dev['observations']+self.confirm['observations']:
            for m,r in o['variants'].items():
                validate(r);p=pixels(r['measured_support']);self.assertEqual(len(p),r['metrics']['area']);self.assertIsNone(r['physical_body_center']);self.assertIsNone(r['physical_body_centerline_crossing']);self.assertEqual(r['phase1_reliability'],0.)
                if len(p):np.testing.assert_allclose(p.mean(0),r['measured_photo_location'],atol=1e-12)
    def test_connected_new_supports(self):
        for o in self.dev['observations']+self.confirm['observations']:
            for m in ('D','S','G'):
                mask=local_mask(o['variants'][m]['measured_support'],np.array(o['origin']),(97,97));self.assertLessEqual(ndi.label(mask)[1],1)
    def test_false_confidence_not_assigned(self):
        for o in self.dev['observations']+self.confirm['observations']:
            for r in o['variants'].values():self.assertIsNone(r['photographic_reliability']['calibrated_probability'])
    def test_black_native_threshold_and_schema(self):
        data=read(OUT/'reflections.json.gz')
        for o in data['observations']:
            for m in ('R1','R2','R4'):
                r=o['variants'][m];p=pixels(r['measured_support'])-o['origin'];meta=r['method_evidence'];lum=np.array(o['native_Y']);self.assertEqual(r['support_type'],'specular-reflection region');self.assertIsNone(r['physical_body_center'])
                if len(p):self.assertTrue(np.all(lum[p[:,1],p[:,0]]>=meta['native_level']-1e-7))
                if o['id'] in data['confirmation_ids']:validate(r)
    def test_primary_and_secondary_remain_separate_features(self):
        d=read(OUT/'reflections.json.gz');selected=d['selected'];ids=[s['id'] for s in selected[:2]];obs={o['id']:o for o in d['observations']}
        a,b=[obs[i] for i in ids];self.assertNotEqual(ids[0],ids[1])
        for m in ('R1','R2','R4'):
            pa=set(map(tuple,pixels(a['variants'][m]['measured_support'])));pb=set(map(tuple,pixels(b['variants'][m]['measured_support'])));self.assertTrue(pa and pb);self.assertFalse(pa&pb)
    def test_synthetic_saved_before_truth(self):
        for folder in sorted((OUT/'synthetic').glob('scene-*')):
            truth=read(folder/'truth.json');self.assertEqual(truth['inference_sha256'],sha(folder/'inference.json.gz'));self.assertTrue(truth['certificate']['certified'])
    def test_clear_confirmation_failure_not_hidden(self):
        r=self.confirm['observations'][3]['variants']['S'];self.assertGreater(r['metrics']['area'],870);self.assertEqual(r['status'],'rejected-area-cap');self.assertTrue(r['method_evidence']['domain_sensitive'])

if __name__=='__main__':unittest.main()
