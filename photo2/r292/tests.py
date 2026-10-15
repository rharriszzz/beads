"""Scientific contracts evaluated only on original photograph and saved outcomes."""
import copy,gzip,json,tempfile,unittest
import numpy as np
from PIL import Image
from .common import *
from .run import hashes
from .separators import crossing
from .detector import detect
from .serve import Store

class PhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];cls.byid={r['case_id']:r for r in cls.rows};cls.native,cls.rgb,cls.meta=photo();cls.collection=read(EVIDENCE/'collection.json');cls.comparison=read(OUT/'comparison.json')
    def test_sources_frozen_before_holdouts(self):
        f=read(OUT/'algorithm-frozen.json');self.assertEqual(f['source_hashes'],hashes());self.assertFalse(f['reserved_opened']);self.assertLess(self.collection['frozen_utc'],f['frozen_utc'])
    def test_historical_science_and_live_feedback_unchanged(self):
        for p,digest in dict(read(EVIDENCE/'historical-hashes.json.gz'),**read(EVIDENCE/'feedback-hashes.json')).items():self.assertEqual(sha(ROOT/p),digest,p)
    def test_collection_retains_old_and_frozen_new_targets(self):
        old=read(ROOT/'photo2/r291/evidence/collection.json')['cases'];self.assertEqual(len(self.rows),len(old)+self.collection['new_reserved_count']);self.assertTrue({c['case_id'] for c in old}<set(self.byid));anchors=[r['feature']['point'] for r in self.rows if r['split']=='development'];fresh=[]
        for r in self.rows:
            if r['split']!='reserved':continue
            p=r['feature']['point'];self.assertGreaterEqual(min(np.linalg.norm(np.array(p)-q) for q in anchors+fresh),100);fresh.append(p)
        self.assertEqual(len(fresh),9);self.assertEqual(self.collection['unfilled'],[['unknown',2]])
    def test_native_pixels_and_displayed_provenance(self):
        manifest=read(REVIEW/'manifest.json')
        for e in manifest['cases']:
            r=self.byid[e['case_id']];x0,y0,x1,y1=r['box'];np.testing.assert_array_equal(np.asarray(Image.open(REVIEW/'crops'/(e['case_id']+'.png'))),self.native[y0:y1,x0:x1]);self.assertEqual(sha(REVIEW/'data'/(e['case_id']+'.json')),e['candidate_digest'])
    def test_every_candidate_has_all_evidence_and_original_patch(self):
        for r in self.rows:
            core=set(map(tuple,pixels(r['feature'])))
            for c in [r['A']]+([r['B']] if r['B'] else []):
                self.assertEqual(set(c['evidence']),{f'T{i}' for i in range(1,9)});self.assertTrue(core<=set(map(tuple,pixels(c['candidate_pixels']))));self.assertIsNone(c['visible_region_centroid']);self.assertFalse(c['evidence']['T8']['photographic_insufficiency_asserted'])
                for s in c['segments']:
                    if s['supported']:self.assertFalse(s['frame']);self.assertFalse(s['conflicted']);self.assertTrue(any(x.startswith(('A:','B:','C:')) for x in s['methods']))
    def test_tracked_arcs_are_adjacent_observations_with_unresolved_ends(self):
        for r in self.rows:
            for a in r['separator_arcs']:
                p=np.asarray(a['path']);n=np.asarray(a['normal']);self.assertGreaterEqual(len(p),5);delta=np.diff(p,axis=0);self.assertTrue(np.all(np.linalg.norm(delta,axis=1)<=np.sqrt(5)+1e-8));self.assertTrue(np.all(np.abs(np.abs(delta@np.array([-n[1],n[0]]))-1)<1e-8));self.assertGreater(a['dark_samples'],0);self.assertEqual(len(a['endings']),2)
                if a['enforced']:self.assertFalse(a['core_conflict']);self.assertGreaterEqual(a['external_connection_fraction'],.6)
    def test_enforced_observed_valleys_remain_outside_target(self):
        for r in self.rows:
            owned=set(map(tuple,pixels(r['A']['candidate_pixels'])))
            for a in r['separator_arcs']:
                if not a['enforced']:continue
                for offset in (0,1):self.assertFalse(any(tuple(q) in owned for q in np.rint(np.asarray(a['path'])+offset*np.asarray(a['normal'])).astype(int)))
    def test_original_missed_separator_samples_now_excluded(self):
        r=self.byid['reserved-yellow-05'];old=read(ROOT/'photo2/review/r291/data/reserved-yellow-05.json');origin=np.array(old['box'][:2]);p=next(q for q in old['separators'] if q['feature_id']=='H-1727-1875');samples=np.rint(np.array(p['troughs'])+origin).astype(int);before=set(map(tuple,pixels(old['A']['candidate_pixels'])));after=set(map(tuple,pixels(r['A']['candidate_pixels'])));self.assertEqual(sum(tuple(q) in before for q in samples),3);self.assertEqual(sum(tuple(q) in after for q in samples),0)
    def test_end_around_connections_are_not_hidden_by_zero_center_crossings(self):
        r=self.byid['red-multiple-1'];self.assertEqual(sum(q['straddled_samples'] for q in r['separator_comparison']['after'] if q['enforced']),0);self.assertGreater(sum(q['routed_around_samples'] for q in r['separator_comparison']['after'] if q['enforced']),0)
    def test_accepted_reference_changes_are_explicit_without_auto_answers(self):
        manifest=read(REVIEW/'manifest.json');accepted=[q for q in manifest['cases'] if q['r291_accepted']];self.assertEqual(len(accepted),13)
        for q in accepted:
            self.assertEqual(q['materially_changed'],self.comparison[q['case_id']]['materially_changed'])
            if not q['materially_changed']:self.assertNotIn(q['case_id'],manifest['start_here'])
        for cid in ('Q14','development-yellow-03'):
            self.assertEqual(self.comparison[cid]['baseline_label'],'B');self.assertEqual(self.comparison[cid]['iou'],1.)
    def test_ablation_separates_the_two_B_factors(self):
        rows={r['case_id']:r for r in read(OUT/'r291-B-ablation.json.gz')['records']};self.assertEqual(len(rows),68)
        for cid in ('Q14','development-yellow-03'):
            v=rows[cid]['variants'];self.assertEqual(v['dark_only']['reference_iou'],1.);self.assertEqual(v['peer_only']['pixels'],v['A']['pixels'])
        self.assertLess(rows['red-worst']['variants']['dark_only']['reference_iou'],.7)
    def test_case_metadata_and_judgments_are_not_runtime_inputs(self):
        r=self.byid['reserved-yellow-05'];features=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']];p=np.array(r['feature']['point']);near=[q for q in features if np.linalg.norm(np.array(q['point'])-p)<=170];f={k:v for k,v in r['feature'].items() if k in ('id','point','runs')};out=detect(self.rgb,f,near);self.assertEqual(out['A'],r['A']);self.assertEqual(out['separator_arcs'],r['separator_arcs'])
    def test_feedback_is_separate_versioned_optional_revisable_and_reopenable(self):
        with tempfile.TemporaryDirectory(prefix='r292-test-') as folder:
            store=Store(folder);e=next(c for c in store.manifest['cases'] if c['case_id']=='reserved-yellow-05');self.assertEqual(store.state()['cases'],{});req=dict(case_id=e['case_id'],candidate_digest=e['candidate_digest'],expected_revision=0,payload=dict(answer='partial',diagnostics=[],ownership={}))
            store.record(req);req.update(expected_revision=1,payload=dict(answer='wrong-clear',diagnostics=['neighbor'],ownership={}));store.record(req);req.update(expected_revision=2,action='undo');store.record(req);reopened=Store(folder);self.assertEqual(reopened.state()['cases'][e['case_id']]['payload']['answer'],'partial');self.assertEqual(len(reopened.events()),3);self.assertIn('displayed_separator_arcs',reopened.events()[0]);self.assertEqual(reopened.events()[0]['schema'],'R292-review-v1')
            req['expected_revision']=3;req['candidate_digest']='stale'
            with self.assertRaises(ValueError):store.record(req)
if __name__=='__main__':unittest.main()
