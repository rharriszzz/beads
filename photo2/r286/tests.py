"""Scientific mechanism, independence, exact supports and failure-preservation tests."""
import unittest
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from .common import *
from .methods import marker_field,path_support,watershed_support
from photo2.r285.methods import component
from photo2.r285.mechanisms import field
from photo2.r285.run import local_mask

class Mechanisms(unittest.TestCase):
    def test_context_restores_excluded_peak_without_adding_pixel(self):
        y,x=np.indices((31,31));lum=.01+.5*np.exp(-((x-15)**2+(y-15)**2)/30);d=(x-15)**2+(y-15)**2<100;d[15,15]=False
        markers,target,ledger=marker_field(lum,d,d,np.zeros_like(d),[14,15]);r=next(r for r in ledger if r['raw_peak']==[15,15]);self.assertIsNotNone(r['placed']);self.assertNotEqual(r['placed'],[15,15]);self.assertTrue(d[r['placed'][1],r['placed'][0]]);self.assertEqual(markers[15,15],0)
    def test_paper_peak_is_not_projected(self):
        y,x=np.indices((31,31));lum=.01+.5*np.exp(-((x-15)**2+(y-15)**2)/30);d=(x-15)**2+(y-15)**2<100;d[15,15]=False;p=np.zeros_like(d);p[15,15]=True
        _,_,ledger=marker_field(lum,d,d,p,[14,15]);r=next(r for r in ledger if r['raw_peak']==[15,15]);self.assertIsNone(r['placed'])
    def test_bright_narrow_connection_not_pruned_by_M(self):
        lum,d=field(.29);m,*_=watershed_support(lum,d,d,~d,[24,32],False);self.assertTrue(m[32,46])
    def test_shallow_shading_retained_by_M(self):
        lum,d=field(.24);m,*_=watershed_support(lum,d,d,~d,[24,32],False);self.assertTrue(m[32,46])
    def test_dark_seam_stops_M(self):
        lum,d=field(.025);m,*_=watershed_support(lum,d,d,~d,[24,32],False);self.assertFalse(m[32,46]);self.assertTrue(m[32,24])
    def test_direct_barrier_cannot_be_bypassed(self):
        lum=np.ones((25,25));d=np.ones((25,25),bool);bar=np.zeros_like(d);bar[5:20,12]=True
        m,_=path_support(lum,d,[5,12],1,bar);self.assertFalse(m[12,20]);self.assertTrue(m[2,5])
    def test_seed_missing_is_not_substituted(self):
        m=np.zeros((10,10),bool);m[3:7,6:9]=True;self.assertFalse(component(m,[4,4]).any())
    def test_false_split_and_unobservable_ambiguity_preserved(self):
        rows=read(OUT/'mechanisms.json')['fields'];self.assertFalse(rows[1]['variants']['B']['right_feature_retained']);self.assertEqual(rows[0]['variants'],rows[3]['variants'])

class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev=read(OUT/'development.json.gz')['cases'];cls.conf=read(OUT/'confirmation.json.gz')['cases'];cls.obs=[o for c in cls.dev+cls.conf for o in c['observations']]
    def test_freeze_and_no_confirmation_retuning(self):
        f=read(OUT/'candidate-freeze.json');self.assertFalse(f['confirmation_results_exist']);self.assertEqual(f['method_sha256'],sha(Path(__file__).parent/'methods.py'));self.assertEqual(f['selection_sha256'],sha(OUT/'selection.json'))
    def test_independent_selection(self):
        old=[c['center'] for c in read(ROOT/'photo2/r284b/results/cases.json')]+[c['seed'] for c in read(OLD/'selection.json')['confirmation']];new=[]
        for c in read(OUT/'selection.json')['confirmation']:
            self.assertTrue(all(np.linalg.norm(np.array(c['seed'])-p)>145 for p in old+new));new.append(c['seed'])
        self.assertEqual(len(new),10);self.assertEqual(len(self.obs),57)
    def test_p2_preserved_exactly_p5_separated(self):
        p2=self.dev[1]['observations'][0]['variants'];p5=self.dev[4]['observations'][0]['variants']
        for m in ('M','A','B','C'):np.testing.assert_array_equal(pixels(p2[m]['measured_support']),pixels(p2['S']['measured_support']))
        self.assertEqual(p5['M']['metrics']['area'],664);self.assertEqual(p5['S']['metrics']['area'],1817)
    def test_record_geometry_and_uncertainty(self):
        for o in self.obs:
            for r in o['variants'].values():
                validate(r);p=pixels(r['measured_support']);self.assertEqual(len(p),r['metrics']['area']);self.assertIsNone(r['physical_body_center']);self.assertIsNone(r['physical_body_centerline_crossing']);self.assertIsNone(r['photographic_reliability']['calibrated_probability'])
                if len(p):np.testing.assert_allclose(p.mean(0),r['measured_photo_location'],atol=1e-12)
    def test_native_connectedness(self):
        for o in self.obs:
            for m in ('M','A','B','C'):
                mask=local_mask(o['variants'][m]['measured_support'],np.array(o['origin']),(97,97));self.assertLessEqual(ndi.label(mask)[1],1)
    def test_protected_interfaces_survive_all_mergers(self):
        count=0
        for o in self.obs:
            for e in o['variants']['B']['method_evidence'].get('interfaces',[]):
                if e['protected']:self.assertTrue(e['separate_after_merging']);count+=1
        self.assertGreater(count,10)
    def test_confirmation_failures_retained(self):
        c5=self.conf[4];o=min(c5['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-c5['seed']));self.assertIn('area ceiling',o['variants']['A']['abstention_reasons']);self.assertEqual(o['variants']['A']['metrics']['area'],1134)
    def test_black_exact_separate_unknown(self):
        r=read(OUT/'reflection-stability.json');self.assertEqual(r['comparisons'],144);self.assertTrue(all(c['exact_mask_contour_peak'] and c['physical_owner'] is None for c in r['checks']));self.assertEqual(set(r['upper_lower_overlap'].values()),{0})
    def test_synthetic_identity_after_inference(self):
        folders=list((OUT/'synthetic').glob('scene-*'));self.assertEqual(len(folders),4)
        for p in folders:
            t=read(p/'truth.json');self.assertTrue(t['certificate']['certified']);self.assertEqual(t['inference_sha256'],sha(p/'inference.json.gz'))

if __name__=='__main__':unittest.main()
