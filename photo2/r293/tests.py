"""Original-photo evidence, coverage semantics, provenance and review contracts."""
import gzip,tempfile,unittest
import numpy as np
from PIL import Image
from .common import *
from .run import hashes
from .serve import Store
from .geometry import Reference

class PhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native,cls.rgb,cls.meta=photo();cls.rows=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];cls.manifest=read(REVIEW/'manifest.json');cls.population=read(OUT/'feature-population.json.gz')['records'];cls.coverage=read(OUT/'coverage.json')
    def test_preservation(self):
        for p,h in dict(read(EVIDENCE/'historical-hashes.json.gz'),**read(EVIDENCE/'feedback-hashes.json')).items():self.assertEqual(sha(ROOT/p),h,p)
    def test_archived_review_and_exact_snapshot_provenance(self):
        d=read(EVIDENCE/'r292-review-analysis.json');self.assertEqual(d['final_answers'],{'A':4,'partial':3,'wrong-clear':4});raw=gzip.decompress((ROOT/d['archive']).read_bytes());self.assertEqual(raw,(ROOT/d['source']).read_bytes());self.assertEqual(len(d['history']),11)
        for q in d['records']:
            self.assertEqual(sha(ROOT/q['candidate_path']),q['candidate_digest']);self.assertEqual(sha(ROOT/q['crop_path']),q['crop_sha256'])
    def test_new_targets_frozen_before_reserved_and_unchanged_R292(self):
        d=read(EVIDENCE/'collection.json');freeze=read(OUT/'algorithm-frozen.json');self.assertEqual(freeze['source_hashes'],hashes());self.assertLess(d['frozen_utc'],freeze['frozen_utc']);self.assertEqual(len(self.rows),48);old=[q['feature']['point'] for q in read(ROOT/'photo2/r292/evidence/collection.json')['cases']];seen=[]
        for q in d['cases']:
            p=q['feature']['point'];self.assertGreaterEqual(min(np.linalg.norm(np.array(p)-v) for v in old),45)
            if seen:self.assertGreaterEqual(min(np.linalg.norm(np.array(p)-v) for v in seen),24)
            seen.append(p);self.assertLessEqual(q['priority_evidence']['centerline']['distance'],26)
        self.assertEqual(sum(r['split']=='reserved' for r in self.rows),24)
    def test_native_crops_full_image_and_station_crops(self):
        np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'original.png')),self.native)
        for e in self.manifest['cases']:
            d=read(REVIEW/'data'/(e['case_id']+'.json'));x0,y0,x1,y1=d['box'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'crops'/(e['case_id']+'.png'))),self.native[y0:y1,x0:x1]);self.assertEqual(sha(REVIEW/'data'/(e['case_id']+'.json')),e['candidate_digest'])
        for s in self.coverage['stations']:
            x,y=np.rint(s['point']).astype(int);np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'stations'/(s['station_id']+'.png'))),self.native[max(0,y-40):y+41,max(0,x-40):x+41])
    def test_every_historical_candidate_unchanged(self):
        for stage in ('development','reserved'):
            for old in read(ROOT/f'photo2/r292/results/{stage}.json.gz')['records']:
                new=read(REVIEW/'data'/(old['case_id']+'.json'));self.assertEqual(new['A'],old['A']);self.assertEqual(new['B'],old['B']);self.assertEqual(new['separator_arcs'],old['separator_arcs'])
    def test_all_evidence_preserved_without_physical_silhouette_claims(self):
        for r in self.rows:
            core=set(map(tuple,pixels(r['feature'])))
            for c in [r['A']]+([r['B']] if r['B'] else []):
                self.assertEqual(set(c['evidence']),{f'T{i}' for i in range(1,9)});self.assertTrue(core<=set(map(tuple,pixels(c['candidate_pixels']))));self.assertIsNone(c['visible_region_centroid']);self.assertFalse(c['evidence']['T8']['photographic_insufficiency_asserted'])
    def test_coverage_uses_actual_photographic_window_not_false_empty_arc_bin(self):
        points={r['feature_id']:np.array(r['point']) for r in self.population};s=next(s for s in self.coverage['stations'] if s['station_id']=='S083');self.assertIn('H-1275-2981',s['near_feature_ids']);self.assertLess(np.linalg.norm(points['H-1275-2981']-s['point']),26)
        for s in self.coverage['stations']:
            self.assertIsNone(s['physical_bead_count']);self.assertIsNone(s['completeness'])
            for fid in s['near_feature_ids']:self.assertLessEqual(np.linalg.norm(points[fid]-s['point']),26+1e-9)
    def test_signed_sides_are_not_bead_ownership_or_arrangement_edges(self):
        for q in self.coverage['opposite_side_pairs']:self.assertIsNone(q['physical_distinct_beads'])
        for q in self.coverage['near_feature_ambiguities']:self.assertIsNone(q['same_physical_bead'])
        for q in self.population:self.assertIn('Not inferred',q['arrangement_exterior'])
    def test_clear_central_failure_not_deferred_and_counter_not_truth(self):
        known={q['case_id']:q for q in read(EVIDENCE/'r292-review-analysis.json')['records']};pop={q['feature_id']:q for q in self.population};r=known['development-red-06'];self.assertEqual(r['answer'],'wrong-clear');self.assertTrue(pop[r['feature_id']]['priority'].startswith('High:'));self.assertEqual(known['red-multiple-1']['answer'],'A');self.assertGreater(known['red-multiple-1']['evidence']['T4']['remaining_separator_bank_connections'],0)
    def test_evidence_export_preserves_independent_pixels_positions_and_color(self):
        d=read(OUT/'phase1-observations.json.gz');self.assertFalse(d['production_adopted']);self.assertEqual(d['legacy_observation_sources'][0]['locations'],810);self.assertEqual(sha(ROOT/d['legacy_observation_sources'][0]['path']),d['legacy_observation_sources'][0]['sha256']);source={r['feature_id']:r['feature'] for r in self.population};self.assertEqual(len(d['records']),1545)
        for r in d['records']:
            f=source[r['observation_id']];self.assertEqual(r['original_peak'],f['point']);self.assertEqual(r['native_peak_rgb'],self.native[f['point'][1],f['point'][0]].tolist());self.assertEqual(r['representative_bright_patch_location'],f['centroid']);self.assertEqual(r['weighted_bright_patch_alternative'],f['weighted']);self.assertEqual(r['native_bright_patch']['runs'],f['runs']);self.assertEqual(r['source_context_color'],f['color']);self.assertIsNone(r['physical_material_color']);self.assertIsNone(r['uncertainty']['physical_identity']);self.assertIsNone(r['uncertainty']['physical_center']);self.assertIsNone(r['uncertainty']['calibrated_accuracy'])
            if r['accepted_visible_measurement']:
                m=r['accepted_visible_measurement'];old=read(ROOT/m['source'])[m['provenance']['answer']];self.assertEqual(m['native_pixels'],old['candidate_pixels']);self.assertIsNone(m['physical_center']);self.assertIsNone(m['physical_body_centerline_crossing'])
    def test_short_review_contains_only_new_high_priority_cases(self):
        cases={q['case_id']:q for q in self.manifest['cases']};self.assertGreaterEqual(len(self.manifest['start_here']),6);self.assertLessEqual(len(self.manifest['start_here']),10)
        for cid in self.manifest['start_here']:
            c=cases[cid];self.assertFalse(c['historical_review']);self.assertTrue(c['well_observed']);self.assertLessEqual(c['centerline_distance'],26)
    def test_separate_feedback_undo_reopen_and_historical_read_only(self):
        with tempfile.TemporaryDirectory(prefix='r293-test-') as folder:
            s=Store(folder);self.assertEqual(s.state()['cases'],{});cid=self.manifest['start_here'][0];entry=s.cases[cid];req=dict(case_id=cid,candidate_digest=entry['candidate_digest'],expected_revision=0,payload=dict(answer='A',diagnostics=[],ownership={}));s.record(req);req.update(expected_revision=1,payload=dict(answer='partial',diagnostics=['neighbor'],ownership={}));s.record(req);req.update(expected_revision=2,action='undo');s.record(req);self.assertEqual(Store(folder).state()['cases'][cid]['payload']['answer'],'A');self.assertEqual(s.events()[0]['schema'],'R293-review-v1');self.assertIn('measurement_question',s.events()[0]);old=next(c for c in self.manifest['cases'] if c['historical_review']);req.update(case_id=old['case_id'],candidate_digest=old['candidate_digest'],expected_revision=0,action='assessment')
            with self.assertRaises(ValueError):s.record(req)
if __name__=='__main__':unittest.main()
