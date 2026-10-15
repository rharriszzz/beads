"""Scientific mechanisms, fixed controls, independence and preserved failures."""
import copy,unittest
from scipy import ndimage as ndi
from photo2.r285.run import local_mask
from .common import *
from .evidence import diffuse_routes
from .mechanisms import fields
from .selector import decide

class Mechanisms(unittest.TestCase):
    def test_shading_continuation_is_not_dark_seam(self):
        _,lum,pg,j,m=fields()[0];r=diffuse_routes(lum,pg,j,m,.25);self.assertEqual(r['supported_pixels'],r['eligible_pixels'])
    def test_deep_seam_blocks_bright_far_material(self):
        _,lum,pg,j,m=fields()[1];r=diffuse_routes(lum,pg,j,m,.25);self.assertFalse(any(x>25 for x,y in r['pixels']));self.assertTrue(any(x>25 for x,y in r['rejected_pixels']))
    def test_narrow_material_not_pruned_for_width(self):
        _,lum,pg,j,m=fields()[2];r=diffuse_routes(lum,pg,j,m,.25);self.assertEqual(r['supported_pixels'],r['eligible_pixels'])
    def test_same_pixels_cannot_certify_different_identity(self):
        rr=[]
        for i in (1,3):
            _,lum,pg,j,m=fields()[i];rr.append(diffuse_routes(lum,pg,j,m,.25))
        self.assertEqual(rr[0],rr[1])
    def test_material_continuation_requires_pigment(self):
        _,lum,pg,j,m=fields()[0];pg[:,22:]=False;r=diffuse_routes(lum,pg,j,m,.25);self.assertFalse(any(x>21 for x,y in r['pixels']))

class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev=read(OUT/'development.json.gz');cls.conf=read(OUT/'confirmation.json.gz');cls.obs=[o for d in (cls.dev,cls.conf) for c in d['cases'] for o in c['observations']]
    def test_freeze_unchanged(self):
        f=read(OUT/'freeze.json');self.assertFalse(f['confirmation_exists']);self.assertEqual(sha(OUT/'selection.json'),f['selection_sha256'])
        for name,h in f['source_hashes'].items():self.assertEqual(sha(Path(__file__).parent/name),h)
    def test_independent_selection(self):
        d=read(OUT/'selection.json');previous=[];self.assertEqual(len(d['confirmation']),16)
        for q in d['confirmation']:
            self.assertTrue(all(np.linalg.norm(np.array(q['seed'])-p)>100 for p in d['excluded_centers']));self.assertTrue(all(np.linalg.norm(np.array(q['seed'])-p)>80 for p in previous));previous.append(q['seed'])
        self.assertFalse(d['new_methods_evaluated'])
    def test_control_replay_count(self):self.assertEqual(self.dev['baseline_masks_replayed'],78)
    def test_four_way_outputs(self):
        self.assertEqual(set(o['selector']['status'] for o in self.obs),{'prefer J','prefer M','both comparably supported','neither reliable; abstain'})
    def test_p2_mechanism_and_p5_stability(self):
        d={q['name']:q['observations'][0] for q in self.dev['cases']};self.assertEqual(d['P2']['selector']['status'],'prefer M');self.assertEqual(d['P2']['evidence']['diffuse_routes']['supported_pixels'],295);self.assertEqual(d['P5']['selector']['status'],'prefer J');self.assertGreater(max(p['area'] for p in d['P5']['variants']['M']['perturbations']),1200)
    def test_no_color_or_id_decision_shortcut(self):
        e=copy.deepcopy(self.dev['cases'][1]['observations'][0]['evidence']);before=decide(e)
        for color in ('yellow','black','red'):
            e.update(color=color,id='unrelated',seed=[999,999]);self.assertEqual(before,decide(e))
    def test_records_preserve_unknowns_and_measured_centroids(self):
        for o in self.obs:
            for r in list(o['variants'].values())+[o['selector']]:
                validate(r);self.assertIsNone(r['physical_body_center']);self.assertIsNone(r['physical_body_centerline_crossing']);self.assertIsNone(r['photographic_reliability']['calibrated_probability']);self.assertEqual(r['importance'],'high')
                p=pixels(r['measured_support'])
                if len(p):np.testing.assert_allclose(p.mean(0),r['measured_photo_location'])
    def test_both_is_not_a_union(self):
        for o in self.obs:
            r=o['selector']
            if len(r['selection']['alternatives'])!=1:self.assertIsNone(r['measured_support']);self.assertIsNone(r['measured_photo_location'])
            else:self.assertEqual(r['measured_support'],o['variants'][r['selection']['alternatives'][0]]['measured_support'])
    def test_connected_supports(self):
        for o in self.obs:
            for r in o['variants'].values():self.assertLessEqual(ndi.label(local_mask(r['measured_support'],np.array(o['origin']),(97,97)))[1],1)
    def test_all_requested_perturbation_families(self):
        for o in self.obs:
            for m in ('J','M'):
                self.assertEqual(len(o['variants'][m]['perturbations']),14);self.assertEqual(set(o['evidence']['candidates'][m]['stability']['by_family']),{'gain','contrast','sigma','background','seed','domain'})
    def test_first_failure_and_confirmation_regression_preserved(self):
        first=read(OUT/'development-v1.json.gz');p2=next(q for q in first['cases'] if q['name']=='P2')['observations'][0];self.assertEqual(p2['selector']['status'],'neither reliable; abstain')
        n7=next(q for q in self.conf['cases'] if q['name']=='N07');o=min(n7['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-n7['seed']));self.assertEqual(o['selector']['status'],'prefer J');self.assertEqual(o['variants']['J']['metrics']['area'],288);self.assertEqual(o['evidence']['diffuse_routes']['supported_pixels'],227)
    def test_black_preservation(self):
        d=read(OUT/'black-preservation.json');self.assertEqual(d['sha256'],sha(ROOT/d['source']));self.assertIsNone(d['physical_owner']);self.assertEqual(d['retained_default'],'R2')

if __name__=='__main__':unittest.main()
