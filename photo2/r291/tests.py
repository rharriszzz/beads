"""Focused contracts using original real-photo inputs and saved results only."""
import copy
import tempfile
import unittest
import numpy as np
from PIL import Image
from .common import *
from .run import hashes
from .detector import detect
from .serve import Store,pair_id

class PhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[r for s in ('development','retrospective','reserved') for r in read(OUT/(s+'.json.gz'))['records']];cls.native,cls.rgb,cls.meta=photo();cls.collection=read(EVIDENCE/'collection.json')
    def test_frozen_sources(self):self.assertEqual(hashes(),read(OUT/'algorithm-frozen.json')['source_hashes'])
    def test_preservation(self):
        for path,digest in dict(read(EVIDENCE/'historical-hashes.json.gz'),**read(EVIDENCE/'r290-feedback-hashes.json')).items():self.assertEqual(sha(ROOT/path),digest,path)
    def test_every_native_crop(self):
        for r in self.rows:
            x0,y0,x1,y1=r['box'];p=REVIEW/'crops'/(r['case_id']+'.png');np.testing.assert_array_equal(np.asarray(Image.open(p)),self.native[y0:y1,x0:x1]);self.assertEqual(sha(p),r['crop_sha256'])
    def test_all_old_cases_retained(self):
        old={c['case_id'] for c in read(ROOT/'photo2/r290/evidence/collection.json')['cases']};self.assertTrue(old<={r['case_id'] for r in self.rows});self.assertEqual(len(self.rows),68)
    def test_new_holdout_separation(self):
        old=[r['feature']['point'] for r in self.rows if r['split']!='reserved'];new=[r['feature']['point'] for r in self.rows if r['split']=='reserved'];self.assertEqual(len(new),10)
        for i,p in enumerate(new):self.assertGreaterEqual(min(np.linalg.norm(np.array(p)-q) for q in old+new[:i]),100)
    def test_complete_evidence_and_no_machine_insufficiency(self):
        for r in self.rows:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                self.assertEqual(set(c['evidence']),{f'T{i}' for i in range(1,9)});self.assertTrue(c['evidence']['T8']['all_complementary_methods_attempted']);self.assertFalse(c['evidence']['T8']['photographic_insufficiency_asserted'])
    def test_target_patch_preserved(self):
        for r in self.rows:
            patch=set(map(tuple,pixels(r['feature'])))
            for c in [r['A']]+([r['B']] if r['B'] else []):self.assertTrue(patch<=set(map(tuple,pixels(c['candidate_pixels']))))
    def test_supported_sides_have_complementary_justification(self):
        unstable_support=0
        for r in self.rows:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                for s in c['segments']:
                    if not s['supported']:continue
                    self.assertTrue(any(v.startswith(('A:','B:','C:')) for v in s['methods']));self.assertFalse(s['conflicted']);self.assertFalse(s['frame']);unstable_support+=int(not s['stable'])
        self.assertGreater(unstable_support,0,'Local photographic evidence must survive while stability is reported separately')
    def test_no_contour_gap_closed_by_arcs(self):
        for r in self.rows:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                ids=[i for arc in c['supported_arcs']+c['unresolved_arcs'] for i in arc];self.assertEqual(sorted(ids),list(range(len(c['segments']))))
                for arc in c['supported_arcs']:
                    for i in arc:self.assertTrue(c['segments'][i]['supported'])
    def test_protected_separator_not_bypassed(self):
        total=0
        for r in self.rows:
            owned=set(map(tuple,pixels(r['A']['candidate_pixels'])));core=set(map(tuple,pixels(r['feature'])))
            for p in r['separators']:
                if p['supported'] and tuple(p['point']) not in core:self.assertNotIn(tuple(p['point']),owned);total+=1
        self.assertGreater(total,0)
    def test_internal_edges_retained_and_centroids_not_certified(self):
        self.assertGreater(sum(len(r['internal_edges']) for r in self.rows),0)
        for r in self.rows:np.testing.assert_allclose(pixels(r['A']['candidate_pixels']).mean(0),r['A']['candidate_centroid']);self.assertIsNone(r['A']['visible_region_centroid'])
    def test_metadata_not_runtime_rules(self):
        r=next(r for r in self.rows if r['case_id']=='P2');f=copy.deepcopy(r['feature']);allf=[q for q in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if q['accepted']];p=np.array(f['point']);near=[q for q in allf if np.linalg.norm(np.array(q['point'])-p)<=170]
        one=detect(self.rgb,f,near)
        stripped={k:v for k,v in f.items() if k in ('id','point','runs')};two=detect(self.rgb,stripped,near);self.assertEqual(one['A'],two['A']);self.assertEqual(one['B'],two['B'])
    def test_start_here_short_and_diverse(self):
        s=read(OUT/'start-here.json');self.assertEqual(len(s['cases']),14);self.assertEqual(len({r['case_id'] for r in s['cases']}),14);self.assertFalse(s['unfilled'])
        for i,r in enumerate(s['cases']):
            for q in s['cases'][:i]:self.assertGreaterEqual(np.linalg.norm(np.array(r['point'])-q['point']),12)
    def test_feedback_optional_diagnostics_reopen_undo(self):
        with tempfile.TemporaryDirectory(prefix='r291-test-') as folder:
            store=Store(folder);c=store.manifest['cases'][0];req=dict(case_id=c['case_id'],candidate_digest=c['candidate_digest'],expected_revision=0,payload=dict(answer='partial',diagnostics=[],ownership={}))
            first=store.record(req);self.assertEqual(first['cases'][c['case_id']]['revision'],1)
            req['expected_revision']=1;req['payload']['answer']='wrong-clear';req['payload']['diagnostics']=['neighbor'];store.record(req)
            reopened=Store(folder);self.assertEqual(reopened.state()['cases'][c['case_id']]['payload']['answer'],'wrong-clear')
            req.update(expected_revision=2,action='undo');s=reopened.record(req);self.assertEqual(s['cases'][c['case_id']]['payload']['answer'],'partial');self.assertEqual(s['cases'][c['case_id']]['payload']['diagnostics'],[])
            self.assertEqual(len(reopened.events()),3);self.assertIn('displayed_candidates',reopened.events()[0]);self.assertTrue(reopened.events()[0]['previous_payload']['answer'] is None)
            with self.assertRaises(ValueError):reopened.record(req)
    def test_feedback_pair_deduplication(self):
        with tempfile.TemporaryDirectory(prefix='r291-test-') as folder:
            store=Store(folder);c=next(c for c in store.manifest['cases'] if c['case_id']=='red-multiple-1');r=read(REVIEW/'data'/(c['case_id']+'.json'));peer=next(q['feature_id'] for q in r['neighboring_features'] if q['feature_id']=='H-0656-0525')
            state=store.record(dict(case_id=c['case_id'],candidate_digest=c['candidate_digest'],expected_revision=0,payload=dict(answer='partial',diagnostics=[],ownership={peer:'same'})))
            key=pair_id(r['feature']['id'],peer);self.assertEqual(state['ownership'][key]['value'],'same')
            other=next(c for c in store.manifest['cases'] if c['case_id']=='red-multiple-2');state=store.record(dict(case_id=other['case_id'],candidate_digest=other['candidate_digest'],expected_revision=0,payload=dict(answer='not-sure',diagnostics=[],ownership={})))
            self.assertEqual(state['ownership'][key]['value'],'same');self.assertEqual(len(store.events()[1]['ownership_changes']),0)
    def test_feedback_version_guard(self):
        with tempfile.TemporaryDirectory(prefix='r291-test-') as folder:
            s=Store(folder)
            with self.assertRaises(ValueError):s.record(dict(case_id=s.manifest['cases'][0]['case_id'],candidate_digest='old-version'))

if __name__=='__main__':unittest.main()
