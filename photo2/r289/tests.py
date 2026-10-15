"""Scientific failure controls and saved evidence contracts."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from .landmark import patch,darkness
from .common import *
from .calibrate import predict,eligible
from .physics import R,sdf,local_normal,RADIUS

class LandmarkChecks(unittest.TestCase):
    def test_native_component_and_weighting(self):
        y,x=np.indices((81,81));f=.03+.8*np.exp(-((x-40)**2/8+(y-40)**2/18));q=patch(f,[40,40])
        np.testing.assert_allclose(q['centroid'],[40,40]);np.testing.assert_allclose(q['weighted'],[40,40]);self.assertGreater(q['shape']['sigma_major'],q['shape']['sigma_minor']);self.assertFalse(q['touches'])
    def test_no_borrowed_peak(self):
        f=np.zeros((81,81));f[40,40]=.5;f[40,41]=1.;q=patch(f,[40,40]);self.assertEqual(q['point'],[40,40]);self.assertTrue(q['contains_brighter'])
    def test_two_separate_highlights(self):
        f=np.full((81,81),.01);f[38:43,30:33]=.9;f[38:43,45:48]=.9
        a=patch(f,[31,40]);b=patch(f,[46,40]);self.assertFalse(set(map(tuple,pixels(a)))&set(map(tuple,pixels(b))))
    def test_dark_coherence(self):
        f=np.ones((81,81));f[38:43,30:33]=.1;f[38:43,48:51]=.1
        q=darkness(f,[40,40]);self.assertTrue(q['profiles'][0]['paired']);self.assertEqual(q['offset'][0],0.)
        # A route immediately outside these five tracks remains bright, and cannot
        # cancel their seam evidence.
        self.assertEqual(q['axes'],1)
    def test_single_dark_pixel_is_not_seam(self):
        f=np.ones((81,81));f[40,30:33]=.01;f[40,48:51]=.01
        self.assertEqual(darkness(f,[40,40])['axes'],0)
    def test_no_window_as_edge(self):
        f=np.ones((81,81));q=patch(f,[40,40]);self.assertTrue(q['touches']);self.assertEqual(darkness(f,[40,40])['axes'],0)
    def test_constant_is_not_a_physical_center(self):
        d=read(OUT/'phase2-observations.json.gz')
        self.assertFalse(d['production_adopted'])
        for r in d['records']:
            self.assertIsNone(r['physical_center']);self.assertIsNone(r['physical_identity']);self.assertEqual(r['specularity'],'unresolved: diffuse or specular')
    def test_frozen_source(self):
        f=read(OUT/'calibration-frozen.json')
        for p,h in f['source_hashes'].items():self.assertEqual(sha(Path(__file__).parent/p),h)
        self.assertEqual(sha(OUT/'photo-landmarks.json.gz'),f['detector_sha256'])
    def test_geographic_separation(self):
        rr=read(OUT/'associations.json.gz');a=np.array([r['centroid'] for r in rr if r['split']=='development']);b=np.array([r['centroid'] for r in rr if r['split']=='evaluation'])
        self.assertGreaterEqual(np.linalg.norm(a[:,None]-b[None,:],axis=2).min(),100)
    def test_matching_never_nearest_substitution(self):
        rr=read(OUT/'associations.json.gz')
        for r in rr:
            if r['match_status']=='unique':self.assertEqual(r['matches'],[r['landmark']['id']])
            if r['match_status']=='missing':self.assertFalse(r['matches']);self.assertNotIn('landmark',r)
    def test_historical_exact(self):
        r=read(OUT/'historical-replay.json');self.assertEqual(r['exact_observations'],810);self.assertEqual(r['exact_ledger'],807)
        for p,h in r['inputs'].items():self.assertEqual(sha(ROOT/p),h)
    def test_normal_matches_sdf(self):
        q=np.array([.31*R,.8*R,.2*R]);e=1e-6;grad=np.array([(sdf(q+np.eye(3)[i]*e)-sdf(q-np.eye(3)[i]*e))/(2*e) for i in range(3)]);grad/=np.linalg.norm(grad)
        np.testing.assert_allclose(local_normal(q*RADIUS/R),grad,atol=1e-8)
    def test_synthetic_projection_and_inference_provenance(self):
        for p in (OUT/'synthetic').glob('*/evaluation.json'):
            d=read(p);self.assertTrue(d['projection_check']['exact_resolved_agreement']);self.assertTrue(d['certificate']['certified'])
            for name,h in d['inference_hashes'].items():self.assertEqual(sha(p.parent/(name+'-inference.json.gz')),h)
    def test_named_review_anchors(self):
        cases=[q for stage in ('development','confirmation') for q in read(ROOT/f'photo2/r288/results/{stage}.json.gz')['cases']]
        for r in read(OUT/'review-manifest.json'):
            if r['name'] not in ('P2','P5','N11','Q14'):continue
            q=next(q for q in cases if q['name']==r['name']);o=next(o for o in q['observations'] if o['seed']==q['seed']);self.assertEqual(r['id'],o['id'])
    def test_saved_metrics_recompute(self):
        rows=read(OUT/'associations.json.gz');f=read(OUT/'calibration-frozen.json')['models'];ev=read(OUT/'photo-evaluation.json')
        for color in ('red','yellow'):
            rr=eligible(rows,'R275',color,'evaluation');m=f[f'R275/{color}/constant_patch'];e=[np.linalg.norm(predict(r,'constant_patch',m)-r['centroid']) for r in rr]
            self.assertEqual(stats(e),ev['scores'][f'R275/{color}/evaluation/constant_patch']['total'])
    def test_all_detector_peaks_remain_native_maxima(self):
        from photo2.bead_detection.brightness_r270 import linearize
        _,rgb,_=photo();lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);rr=read(OUT/'photo-landmarks.json.gz')['records']
        for r in rr:
            x,y=r['point'];self.assertGreaterEqual(lum[y,x],lum[max(0,y-1):y+2,max(0,x-1):x+2].max()-1e-12)
            if r['accepted']:
                pts=pixels(r);self.assertIn((x,y),set(map(tuple,pts)));self.assertFalse(r['contains_brighter']);self.assertFalse(r['touches'])
                np.testing.assert_allclose(pts.mean(0),r['centroid'],atol=1e-12)

if __name__=='__main__':unittest.main()
