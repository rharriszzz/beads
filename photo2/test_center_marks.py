"""Independent persistence, optimal assignment and known-count synthetic checks."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

import numpy as np
from center_marks import CenterStore, validate_marks, match_centers, score_counts
from tangent_viewer import ViewerStore


class CenterTests(unittest.TestCase):
    def test_persistence_revision_conflict_backups_and_document_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'centers.json'
            source = dict(sha256='test', oriented_size=[100, 200])
            store = CenterStore(path, source)
            point = dict(id='stable', number=10, x=30.5, y=180.)
            first = store.save(dict(points=[point], revision=0), dict(parameters=dict(nbeads=2698)), {})['document']
            self.assertEqual(CenterStore(path, source).read(), first)
            changed = dict(point, x=35.)
            store.save(dict(points=[changed], revision=1), dict(parameters=dict(nbeads=2833)), {})
            self.assertEqual(json.loads(path.with_name('centers.previous.json').read_text()), first)
            self.assertEqual(store.read()['points'][0]['id'], 'stable')
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                store.save(dict(points=[], revision=1), {}, {})
            self.assertEqual(path.read_bytes(), before)
            with self.assertRaises(ValueError): CenterStore(path, dict(source, sha256='different'))
            other = Path(folder)/'annotations.json'; other.write_text('{"keep": true}')
            with self.assertRaises(ValueError): CenterStore(other, source)
            self.assertEqual(other.read_text(), '{"keep": true}')
            with self.assertRaises(ValueError): CenterStore(path, source, forbidden=[path])
            backup=path.with_name('centers.previous.json');backup.write_text('{"unrelated":true}')
            before=path.read_bytes()
            with self.assertRaises(ValueError): store.save(dict(points=[],revision=2),{}, {})
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(backup.read_text(),'{"unrelated":true}')

    def test_duplicate_numbers_ids_and_outside_or_nonfinite_points_rejected(self):
        p = dict(id='a', number=1, x=10., y=20.)
        for points in [[p,p], [p,dict(p,id='b')], [dict(p,x=100)], [dict(p,y=-1)],
                       [dict(p,x=float('nan'))], [dict(p,number=True)], [dict(p,x=True)]]:
            with self.assertRaises(ValueError): validate_marks(points, [100,100])

    def test_distinct_nearest_matching_is_optimal_and_squared_not_unsquared(self):
        points = [dict(id=str(i), number=i+1, x=x, y=y) for i,(x,y) in enumerate([(0,0),(0,0),(9,1)])]
        predictions = [(0,0),(4,0),(10,0),(20,0)]
        frame = dict(count=100,hand=1,circles=[[*xy,1,0,0,1] for xy in predictions],generator_indices=[20,30,40,50])
        result = match_centers(points, frame)
        independent = min(sum((p['x']-predictions[j][0])**2+(p['y']-predictions[j][1])**2
                              for p,j in zip(points,indices)) for indices in itertools.permutations(range(4),3))
        self.assertEqual(result['sse'], independent)
        self.assertEqual(result['sse'],18.)
        self.assertAlmostEqual(result['rms_pixels'],np.sqrt(6))
        self.assertEqual(len(set(m['tentative_generator_index'] for m in result['matches'])),3)

    def test_exact_model_synthetic_marks_select_true_count_for_both_hands(self):
        # This is a correctness test of the proxy score, not a claim that photo
        # visible-area centroids coincide with these outward points.
        with tempfile.TemporaryDirectory() as folder:
            viewer = ViewerStore(Path(folder)/'choice.json')
            for hand in [-1,1]:
                true = viewer.frame(2698,hand)
                xy = np.array(true['circles'])[np.linspace(0,len(true['circles'])-1,12,dtype=int),:2]
                points = [dict(id=str(i),number=i+1,x=float(x),y=float(y)) for i,(x,y) in enumerate(xy)]
                document = dict(source=viewer.source,points=points,revision=1)
                progress = []
                result = score_counts(document,[2688,2698,2708],hand,viewer.frame,lambda n,total:progress.append((n,total)))
                self.assertEqual(result['best']['count'],2698)
                self.assertEqual(result['best']['sse'],0.)
                self.assertTrue(all(row['sse']>0 for row in result['rows'] if row['count']!=2698))
                self.assertEqual(progress,[(1,3),(2,3),(3,3)])
                self.assertEqual(document['points'],points)
                json.dumps(result,allow_nan=False)
                # Counts/hand do not mutate or assign indices to observations.
                self.assertTrue(all(set(p)=={'id','number','x','y'} for p in points))

    def test_saved_score_preserves_snapshot_and_refuses_unrelated_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source=dict(sha256='test',oriented_size=[100,100]); store=CenterStore(Path(folder)/'centers.json',source)
            doc=dict(schema_version=1,kind='center_count_score',source=source,centers=dict(points=[dict(id='a',x=20)]))
            store.save_score(doc); newer=deepcopy(doc);newer['centers']['points'][0]['x']=30;store.save_score(newer)
            self.assertEqual(json.loads(store.score_path.with_name('centers-score.previous.json').read_text()),doc)
            store.score_path.write_text('{"keep":true}')
            before=store.score_path.read_bytes()
            with self.assertRaises(ValueError): store.save_score(newer)
            self.assertEqual(store.score_path.read_bytes(),before)

    def test_background_scan_completes_with_saved_snapshot_without_a_server(self):
        with tempfile.TemporaryDirectory() as folder:
            viewer=ViewerStore(Path(folder)/'choice.json')
            frame=viewer.frame(2698,-1)
            points=[dict(id=str(i),number=i+1,x=row[0],y=row[1]) for i,row in enumerate(frame['circles'][::300][:4])]
            saved=viewer.save_centers(dict(count=2698,hand=-1,revision=0,points=points))['document']
            complete=threading.Event();original=viewer.centers.save_score
            def finish(doc): original(doc);complete.set()
            viewer.centers.save_score=finish
            payload=dict(low=2697,high=2699,step=1,hand=-1,revision=saved['revision'])
            with self.assertRaises(ValueError): viewer.start_score(dict(payload,revision=0))
            with self.assertRaises(ValueError): viewer.start_score(dict(payload,low=100,high=10000,step=1))
            job=viewer.start_score(payload)
            self.assertTrue(complete.wait(timeout=5))
            for _ in range(100):
                state=viewer.score_status(job['id'])
                if state['state']!='running':break
                time.sleep(.01)
            self.assertEqual(state['state'],'complete')
            self.assertEqual(state['result']['best']['count'],2698)
            self.assertEqual(state['done'],3)
            self.assertEqual(viewer.centers.read_score()['centers'],saved)
            self.assertEqual(viewer.centers.read()['points'],points)

    def test_restores_saved_points_and_matching_scores_without_writing_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'choice.json'; viewer=ViewerStore(path)
            points=[dict(id='one',number=1,x=100.,y=200.)]
            first=viewer.save_centers(dict(count=2646,hand=-1,revision=0,points=points))['document']
            result=dict(schema_version=1,kind='center_count_score',source=viewer.source,centers=first,hand=-1,
                        counts=[2697,2698],rows=[dict(count=2697,sse=4,rms_pixels=2),dict(count=2698,sse=1,rms_pixels=1)],
                        best=dict(count=2698,sse=1,rms_pixels=1))
            viewer.centers.save_score(result)
            # A new save of identical marks changes revision/reference, not the
            # scored positions. It should still restore the same score curve.
            second=viewer.save_centers(dict(count=2600,hand=-1,revision=1,points=points))['document']
            before={p:p.read_bytes() for p in Path(folder).glob('*.json')}
            reopened=ViewerStore(path); config=reopened.config()
            self.assertEqual(config['centers'],second)
            self.assertEqual(config['saved_score'],result)
            self.assertEqual(config['initial_count'],2600)
            self.assertEqual({p:p.read_bytes() for p in Path(folder).glob('*.json')},before)
            changed=[dict(points[0],x=101.)]
            reopened.save_centers(dict(count=2600,hand=-1,revision=2,points=changed))
            self.assertIsNone(reopened.config()['saved_score'])
            self.assertIn('different centers',reopened.config()['score_restore_message'])


if __name__=='__main__': unittest.main()
