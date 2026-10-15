"""Regression contracts evaluated only with original real photographic pixels."""
import copy
import tempfile
import unittest
import numpy as np
from PIL import Image
from .common import *
from .detector import detect
from .run import hashes
from .serve import Store

class PhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.collection=read(EVIDENCE/'collection.json');cls.native,cls.rgb,cls.meta=photo()
        cls.records=[q for s in ('development','reserved') for q in read(OUT/(s+'.json.gz'))['records']]

    def test_frozen_sources(self):self.assertEqual(hashes(),read(OUT/'algorithm-frozen.json')['source_hashes'])
    def test_historical_blobs_unchanged(self):
        old=read(EVIDENCE/'historical-hashes.json.gz')
        for path,digest in old.items():self.assertEqual(sha(ROOT/path),digest,path)
    def test_native_fidelity_every_crop(self):
        for r in self.records:
            x0,y0,x1,y1=r['box'];path=REVIEW/'crops'/(r['case_id']+'.png')
            np.testing.assert_array_equal(np.asarray(Image.open(path)),self.native[y0:y1,x0:x1]);self.assertEqual(sha(path),r['crop_sha256'])
    def test_reserved_spatial_separation(self):
        dev=[c for c in self.collection['cases'] if c['split']=='development'];reserved=[c for c in self.collection['cases'] if c['split']=='reserved']
        for c in reserved:
            self.assertGreaterEqual(min(np.linalg.norm(np.array(c['feature']['point'])-d['feature']['point']) for d in dev),110)
    def test_all_cases_all_tests(self):
        self.assertEqual({r['case_id'] for r in self.records},{c['case_id'] for c in self.collection['cases']})
        for r in self.records:
            for c in [r['A']]+([r['B']] if r['B'] else []):self.assertEqual(set(c['evidence']),{f'T{i}' for i in range(1,9)})
    def test_target_feature_enclosed(self):
        for r in self.records:
            for c in [r['A']]+([r['B']] if r['B'] else []):self.assertIn(r['feature']['point'],pixels(c['candidate_pixels']).tolist())
    def test_arcs_partition_without_invented_closure(self):
        for r in self.records:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                ids=[i for group in c['supported_arcs']+c['unresolved_arcs'] for i in group];self.assertEqual(sorted(ids),list(range(len(c['segments']))))
                for group in c['supported_arcs']:
                    for i in group:self.assertTrue(c['segments'][i]['supported']);self.assertTrue(c['segments'][i]['stable'])
    def test_segment_local_justification(self):
        for r in self.records:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                for s in c['segments']:
                    self.assertAlmostEqual(float(np.linalg.norm(np.array(s['endpoints'][0])-s['endpoints'][1])),1.)
                    if s['supported']:
                        self.assertTrue(any(v.startswith(('T1 ','T3/T6 ','T2/T6 ')) for v in s['reasons']))
                        self.assertFalse(any('frame' in v for v in s['reasons']))
    def test_no_unjustified_centroid_export(self):
        for r in self.records:
            for c in [r['A']]+([r['B']] if r['B'] else []):
                np.testing.assert_allclose(pixels(c['candidate_pixels']).mean(0),c['candidate_centroid'])
                if c['status']!='Reliable boundary':self.assertIsNone(c['visible_region_centroid']);self.assertIsNone(c['photographically_supported_visible_pixels'])
                else:self.assertTrue(all(s['supported'] for s in c['segments']));self.assertFalse(c['evidence']['T8']['reflection_edge_ambiguous'])
    def test_complete_status_vocabulary(self):
        allowed={'Reliable boundary','Partial boundary / unresolved','Insufficient measurement'}
        for r in self.records:self.assertIn(r['A']['status'],allowed)
    def test_detector_independent_of_evaluation_metadata(self):
        r=self.records[0];f=copy.deepcopy(r['feature']);near=[dict(id=q['feature_id'],point=q['point']) for q in r['neighboring_features']]
        baseline=detect(self.rgb,f,near)
        for k in list(f):
            if k not in ('id','point','runs'):f.pop(k)
        stripped=detect(self.rgb,f,near)
        self.assertEqual(baseline['A'],stripped['A']);self.assertEqual(baseline['B'],stripped['B'])
    def test_user_evidence_sources_preserved(self):
        d=read(EVIDENCE/'user-judgments.json');self.assertTrue(d['records'][0]['evaluation_only'])
        self.assertEqual(d['records'][0]['landmark_id'],'H-1288-2129')
        for entry in d['records'][0]['source_files']:self.assertEqual(sha(ROOT/entry['path']),entry['sha256'])
    def test_feedback_revisions_reopen_undo_and_conflict(self):
        with tempfile.TemporaryDirectory(prefix='r290-feedback-test-') as folder:
            store=Store(folder);entry=store.manifest['cases'][0];base=dict(case_id=entry['case_id'],candidate_digest=entry['candidate_digest'],expected_revision=0,payload=dict(answer='neither',ownership={}))
            one=store.record(base);self.assertEqual(one['revision'],1)
            base['expected_revision']=1;base['payload']['answer']='not-sure';store.record(base)
            reopened=Store(folder);self.assertEqual(reopened.state()[entry['case_id']]['payload']['answer'],'not-sure')
            base['expected_revision']=2;base['action']='undo';undo=reopened.record(base);self.assertEqual(undo['payload']['answer'],'neither')
            base['expected_revision']=3;undo=reopened.record(base);self.assertIsNone(undo['payload']['answer'])
            self.assertEqual(len(reopened.events()),4);self.assertEqual(reopened.events()[1]['previous_payload']['answer'],'neither')
            with self.assertRaises(ValueError):reopened.record(base)
            self.assertIn('displayed_candidates',reopened.events()[0])
    def test_feedback_rejects_candidate_mismatch(self):
        with tempfile.TemporaryDirectory(prefix='r290-feedback-test-') as folder:
            store=Store(folder)
            with self.assertRaises(ValueError):store.record(dict(case_id=store.manifest['cases'][0]['case_id'],candidate_digest='wrong'))

if __name__=='__main__':unittest.main()
