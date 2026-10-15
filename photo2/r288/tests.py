"""Scientific contracts: causal defects, preserved failures, independence and records."""
import copy
import unittest
from scipy import ndimage as ndi
from photo2.r285.run import local_mask
from photo2.r285.mechanisms import field
from photo2.r286.methods import watershed_support
from .methods import positive_watershed
from .methods_v1 import positive_watershed as first
from .selector import decide
from .common import *

class Mechanisms(unittest.TestCase):
    def get(self,level):
        lum,domain=field(level);return dict(smooth=lum,pigment=domain,domain=domain,paper=~domain,seed=[24,32])
    def test_deep_valley_remains_separate(self):
        mask,_=positive_watershed(self.get(.025));self.assertFalse(mask[32,46]);self.assertTrue(mask[32,24])
    def test_shallow_shading_survives(self):
        mask,_=positive_watershed(self.get(.24));self.assertTrue(mask[32,46])
    def test_narrow_bright_material_survives(self):
        mask,_=positive_watershed(self.get(.29));self.assertTrue(mask[32,46])
    def test_first_corridor_failure_is_preserved(self):
        for level in (.24,.29):
            mask,info=first(self.get(level));self.assertFalse(mask[32,46]);self.assertTrue(info['interfaces'][0]['corridor']['coherent'])
    def test_identical_pixels_cannot_establish_different_physical_identity(self):
        a=self.get(.025);b=copy.deepcopy(a);b['hypothetical_identity']='one-body-with-dark-texture';np.testing.assert_array_equal(positive_watershed(a)[0],positive_watershed(b)[0])

class PhotographicContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev=read(OUT/'development.json.gz');cls.conf=read(OUT/'confirmation.json.gz');cls.obs=[o for d in (cls.dev,cls.conf) for q in d['cases'] for o in q['observations']]
    def anchor(self,name):
        q=next(q for q in self.dev['cases'] if q['name']==name);return min(q['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-q['seed']))
    def test_explanation_precedes_algorithm_and_is_preserved(self):
        e=read(OUT/'explanation-checkpoint.json');self.assertFalse(e['segmentation_changes_exist']);self.assertGreater(e['words'],1500);self.assertEqual(e['explanation_sha256'],sha(ROOT/'photo2/J_AND_M_EXPLAINED.md'))
    def test_freeze_and_selection_unchanged(self):
        f=read(OUT/'freeze.json');self.assertFalse(f['confirmation_exists']);self.assertEqual(f['selection_sha256'],sha(OUT/'selection.json'))
        for name,h in f['source_hashes'].items():self.assertEqual(sha(ROOT/'photo2/r288'/name),h)
    def test_new_regions_spatially_selected_without_new_outputs(self):
        d=read(OUT/'selection.json');self.assertFalse(d['new_methods_evaluated']);self.assertTrue(12<=len(d['confirmation'])<=20);previous=[]
        for q in d['confirmation']:
            self.assertTrue(all(np.linalg.norm(np.array(q['seed'])-p)>100 for p in d['excluded_centers']));self.assertTrue(all(np.linalg.norm(np.array(q['seed'])-p)>80 for p in previous));previous.append(q['seed'])
    def test_all_original_controls_replayed(self):self.assertEqual(self.dev['baseline_masks_replayed'],63)
    def test_n07_retains_diffuse_interior_without_old_instability(self):
        o=self.anchor('N07');self.assertEqual(o['variants']['W']['metrics']['area'],515);self.assertGreater(o['evidence']['candidates']['W']['stability']['minimum_iou'],.95);self.assertTrue(o['selector']['selection']['J_inadequacy']);self.assertNotEqual(o['selector']['selection']['alternatives'],['J'])
    def test_p2_success_unchanged(self):
        o=self.anchor('P2');self.assertEqual(o['variants']['W']['measured_support'],o['variants']['M']['measured_support']);self.assertEqual(o['variants']['W']['metrics']['area'],495)
    def test_n06_dark_two_pair_connector_is_not_merged(self):
        o=self.anchor('N06');self.assertLess(o['variants']['W']['metrics']['area'],o['variants']['M']['metrics']['area']);edges=o['variants']['W']['method_evidence']['interfaces'];self.assertTrue(any(e['short_interface'] and e['dark_interface'] and e['separate_after_merging'] for e in edges))
    def test_n11_upper_extension_not_misreported_as_removed(self):
        o=self.anchor('N11');self.assertEqual(o['variants']['W']['measured_support'],o['variants']['M']['measured_support']);self.assertGreater(o['evidence']['candidates']['W']['stability']['minimum_iou'],.95)
    def test_failed_chromatic_alternative_kept(self):
        for name in ('N07','N11'):self.assertIsNone(self.anchor(name)['variants']['H']['measured_support'])
    def test_ensemble_failure_kept(self):
        for name in ('N11','P5'):self.assertLess(self.anchor(name)['evidence']['candidates']['E']['stability']['minimum_iou'],.7)
    def test_full_conditional_perturbations(self):
        for o in self.obs:
            for m in ('J','M','E','W','H'):
                self.assertEqual(len(o['variants'][m]['perturbations']),14);self.assertEqual(set(o['evidence']['candidates'][m]['stability']['by_family']),{'gain','contrast','sigma','background','seed','domain'})
    def test_records_and_unknown_physical_ownership(self):
        for o in self.obs:
            for r in list(o['variants'].values())+[o['selector']]:
                validate(r);self.assertEqual(r['importance'],'high');self.assertIsNone(r['physical_body_center']);self.assertIsNone(r['physical_body_centerline_crossing']);self.assertIsNone(r['photographic_reliability']['calibrated_probability'])
    def test_native_connected_supports(self):
        for o in self.obs:
            for r in o['variants'].values():self.assertLessEqual(ndi.label(local_mask(r['measured_support'],np.array(o['origin']),(97,97)))[1],1)
    def test_decision_not_color_or_review_identity(self):
        o=self.anchor('N07');e=copy.deepcopy(o['evidence']);before=decide(e);e.update(color='yellow',id='unreviewed',seed=[1,1]);self.assertEqual(before,decide(e))
    def test_alternatives_never_union(self):
        for o in self.obs:
            r=o['selector'];names=r['selection']['alternatives']
            if len(names)==1:self.assertEqual(r['measured_support'],o['variants'][names[0]]['measured_support'])
            else:self.assertIsNone(r['measured_support']);self.assertIsNone(r['measured_photo_location'])

if __name__=='__main__':unittest.main()
