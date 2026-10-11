"""Numerical, isolation, persistence and export contracts (no browser required)."""
import contextlib, hashlib, io, json, shutil, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.interpolate import splev
from .generate import ROOT, generate, detect, spline_from_photo, sha
from .store import ReviewStore, Conflict
from . import models

class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name)/'replay'
        generate(ROOT/'beads-photo-2.jpg',cls.out)
        cls.man=json.loads((cls.out/'manifest.json').read_text())
        cls.inv=json.loads((cls.out/'observations.json').read_text())
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_exact_historical_replay_and_periodic_curve_tolerance(self):
        spl=json.loads((self.out/'splines.json').read_text());ref=json.loads((ROOT/'photo2/review/r255/historical-splines.json').read_text())
        for key in ['outer_spline','inner_spline','centerline_spline','outer_spline_control','inner_spline_control']:
            np.testing.assert_array_equal(spl['raw'][key],ref[key])
        from tangent_circles import SplineRope,View
        seed=json.loads((ROOT/'photo2/spline-seed-r175.json').read_text());old=SplineRope(seed['points'],View(),smoothing=2)
        np.testing.assert_allclose(np.array(spl['centerline']),old.seed_image_curve[::4],atol=.001,rtol=0)
    def test_inventory_identity_and_no_dark_seam_assignment(self):
        rows=self.inv['observations'];ids=[r['id'] for r in rows];self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(g['color'] for g in self.inv['palette']['groups']),{'red','yellow'})
        rgb=np.asarray(Image.open(ROOT/'beads-photo-2.jpg'),float)/255
        for r in rows:
            self.assertIsNone(r['bead_index']);self.assertIsNone(r['physical_center']);self.assertNotIn('trusted',r['evidence_class'])
            if r['kind']=='colored-interior' and r['patch']:
                p=np.array(r['patch'],int);self.assertTrue(np.all(rgb[p[:,1],p[:,0]].max(axis=1)>.18))
            if r['kind']=='reflection-on-dark-body':self.assertGreaterEqual(r['dark_annulus_fraction'],.55)
        self.assertTrue(any(p['credible_split_evidence'] for p in self.inv['split_pairs']))
        self.assertTrue(any(not p['credible_split_evidence'] for p in self.inv['split_pairs']))
    def test_regeneration_in_isolated_copy_without_any_legacy_files(self):
        # Only detector code, vendor numerical functions and original JPEG exist here.
        # No archive, accepted observations, graph, model, spline seed or review files.
        isolated=Path(self.tmp.name)/'isolated';pkg=isolated/'photo2/bead_debugger';pkg.mkdir(parents=True)
        for name in ['__init__.py','generate.py']:shutil.copy2(Path(__file__).parent/name,pkg/name)
        shutil.copytree(Path(__file__).parent/'vendor',pkg/'vendor',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT/'beads-photo-2.jpg',isolated/'beads-photo-2.jpg')
        subprocess.run([sys.executable,'-m','photo2.bead_debugger.generate','--output','out'],cwd=isolated,check=True,stdout=subprocess.DEVNULL)
        for name in ['observations.json','splines.json','positive-patches.npz']:
            self.assertEqual(sha(self.out/name),sha(isolated/'out'/name),name)
    def test_brightness_valley_is_not_automatically_two_beads(self):
        # Negative split evidence is retained as ambiguous instead of certified topology.
        weak={p['a'] for p in self.inv['split_pairs'] if not p['credible_split_evidence']}|{p['b'] for p in self.inv['split_pairs'] if not p['credible_split_evidence']}
        for r in self.inv['observations']:
            if r['id'] in weak:self.assertIn(r['evidence_class'],['ambiguous-split','rejected'])

class StoreTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name);self.store=ReviewStore(self.path,'photo-hash')
    def tearDown(self):self.tmp.cleanup()
    def record(self):return dict(model_id='N2696_h+1_f0',model_version='m1',generation_id='d1',generator_index=2162,bead_index=0,origin_id='legacy',observation_id='I256-A',source_position=[1346.,273.],clicked_position=[1350.,275.],action='index-neighbor-incorrect',note='Test note')
    def test_save_restart_revisions_and_optimistic_conflict(self):
        r=self.store.update(0,'review',self.record());self.assertEqual(r['revision'],1)
        with self.assertRaises(Conflict):self.store.update(0,'review',self.record())
        r=self.store.update(1,'session',dict(gi=2163,view=dict(x=-30,y=20,scale=2)))
        restored=ReviewStore(self.path,'photo-hash');self.assertEqual(restored.read(),r);self.assertEqual(len(list(self.path.glob('revision-*.json'))),2)
        self.assertEqual(r['reviews'][0]['note'],'Test note')
    def test_import_merge_dedup_and_conflict_rejection(self):
        r=self.store.update(0,'review',self.record());s=self.store.update(1,'import',r);self.assertEqual(len(s['reviews']),1)
        r['reviews'][0]['note']='silently overwrite'
        with self.assertRaises(ValueError):self.store.update(2,'import',r)
        self.assertEqual(self.store.read()['revision'],2)
    def test_wrong_image_and_invalid_session_refused(self):
        with self.assertRaises(ValueError):self.store.update(0,'import',dict(schema=1,image_sha256='different'))
        with self.assertRaises(ValueError):self.store.update(0,'session',dict(view=dict(x=0,y=0,scale=float('nan'))))
        self.assertEqual(self.store.read()['revision'],0)
    def test_corrupt_latest_never_silently_erases_reviews(self):
        self.store.update(0,'review',self.record());(self.path/'latest.json').write_text('{incomplete')
        with self.assertRaises(json.JSONDecodeError):ReviewStore(self.path,'photo-hash')
        self.assertEqual(len(list(self.path.glob('revision-*.json'))),1)

class ModelTests(unittest.TestCase):
    def test_both_helicities_wrap_and_triples(self):
        for mid in models.IDS:
            c,m=models.load(mid);n=c['n'];g=m.geometry(np.array([0,n]))
            np.testing.assert_allclose(g['centers'][0],g['centers'][1],atol=1e-9)
            self.assertIn(c['h'],[-1,1])
            for k in range(n):
                a,b,d=models.triple(k,n);self.assertEqual((a+6*b+7*d)%n,k)
    def test_saved_adapter_contains_live_surfaces_and_unresolved(self):
        for mid in models.IDS:
            p=ROOT/f'photo2/output/debugger/models/{mid}.json'
            if not p.exists():self.skipTest('Run server --prepare-only to exercise prepared adapter')
            m=json.loads(p.read_text());self.assertEqual(len(m['beads']),m['n'])
            self.assertTrue(any(b['area_px2']==0 for b in m['beads']));self.assertTrue(any(b['area_px2']>100 for b in m['beads']))
            self.assertTrue(all(len(b['footprint'])*16==b['area_px2'] for b in m['beads']))
            self.assertTrue(any(c['owner_generator_index'] is None for c in m['correspondences'].values()))
            self.assertIn('LEGACY-ASSISTED',m['provenance'])

if __name__=='__main__':unittest.main()
