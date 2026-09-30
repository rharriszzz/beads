"""Slider transport matches frozen geometry; choices preserve independent files."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from tangent_viewer import ViewerStore, validate_selection, validate_guides, width_guides, ROOT
from tangent_circles import load_model, tangent_circles


class ViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.store = ViewerStore(Path(cls.temp.name) / 'choice.json')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_both_hands_and_counts_match_frozen_circle_locations_and_exposure(self):
        frozen = json.loads((ROOT / 'photo2/review/r179/summary.json').read_text())
        for variant in frozen['variants']:
            frame = self.store.frame(variant['count'], variant['hand'])
            self.assertEqual(frame['parameters'], variant['config'])
            self.assertEqual(frame['visible_anchors'], variant['overlay']['visible_anchors'])
            self.assertEqual(frame['unfinished_rays'], variant['overlay']['unfinished_rays'])
            centers = np.array(frame['circles'])[:, :2]
            for bead in variant['overlay']['local_checks']:
                if bead['exposed']:
                    self.assertLess(np.min(np.linalg.norm(centers - bead['outward_xy'], axis=1)), 1e-8)
            json.dumps(frame, allow_nan=False)

    def test_compact_ellipses_reproduce_full_projected_tangent_circles(self):
        # Transport uses six numbers per ellipse rather than all49 vertices.
        frame = self.store.frame(2833, 1)
        model = load_model(frame['parameters'], frame['parameters']['parameters'])
        all_geometry = model.geometry(np.arange(2833))
        full_circles, _ = tangent_circles(all_geometry, frame['parameters']['circle_radius'])
        projected = model.view.project(full_circles.reshape(-1, 3)).reshape(2833, 49, 2)
        packet = np.array(frame['circles'])
        angles = np.linspace(0, 2*np.pi, 49)
        reconstructed = packet[:, None, :2] + packet[:, None, 2:4]*np.cos(angles)[None, :, None] + packet[:, None, 4:6]*np.sin(angles)[None, :, None]
        # Match exposed anchors to the full generator array independently.
        from scipy.spatial import cKDTree
        # The true circle center projects independently of vertex sampling.
        _, indices = cKDTree(model.view.project(all_geometry['outward'])).query(packet[:, :2])
        np.testing.assert_allclose(reconstructed, projected[indices], atol=1e-10)

    def test_save_reload_backups_and_refuses_to_replace_other_documents(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'saved.json'
            store = ViewerStore(path)
            view = dict(x=-315., y=88., scale=3.5)
            guides = dict(width_percent=107.5, show_edges=True, show_centerline=False)
            first = store.save(dict(count=2742, hand=1, view=view, guides=guides))['document']
            resumed = ViewerStore(path)
            self.assertEqual((resumed.initial_count, resumed.initial_hand), (2742, 1))
            self.assertEqual(resumed.initial_view, view)
            self.assertEqual(resumed.initial_guides, guides)
            self.assertEqual(first['parameters'], store.configuration(2742, 1)['parameters'])
            store.save(dict(count=2600, hand=-1, view=view))
            self.assertEqual(json.loads(path.with_name('saved.previous.json').read_text()), first)
            unrelated = Path(folder) / 'annotations.json'
            unrelated.write_text('{"annotations": ["preserve me"]}\n')
            before = unrelated.read_bytes()
            with self.assertRaises(ValueError):
                ViewerStore(unrelated)
            self.assertEqual(unrelated.read_bytes(), before)

    def test_guides_are_closed_and_follow_count_scale_without_moving_centerline(self):
        reference = None
        for count in [2698, 2833]:
            frame = self.store.frame(count, -1)
            guide = frame['guides']
            centers = np.array(guide['centerline']); normals = np.array(guide['normals'])
            np.testing.assert_allclose(centers[0], centers[-1], atol=1e-10)
            np.testing.assert_allclose(normals[0], normals[-1], atol=1e-10)
            np.testing.assert_allclose(np.linalg.norm(normals, axis=1), 1, atol=1e-12)
            if reference is not None:
                np.testing.assert_allclose(centers, reference, atol=1e-10)
            reference = centers
            self.assertAlmostEqual(guide['radius_pixels'], guide['radius_model_units']*frame['scale_pixels_per_unit'])

    def test_image_normal_radius_is_the_projected_cross_section_support(self):
        for elevation in [65., 89.]:
            config = self.store.configuration(2698, 1)
            config['parameters']['elevation'] = elevation
            model = load_model(config, config['parameters'])
            guide = width_guides(model)
            g = model.geometry([0]); center = np.array(guide['centerline'][0])
            screen_normal = np.array(guide['normals'][0])
            phi = np.linspace(0, 2*np.pi, 4097)
            radial = np.sin(phi)[:, None]*g['normal'][0] + np.cos(phi)[:, None]*[0,0,1]
            surface = g['line'][0]+guide['radius_model_units']*radial
            support = (model.view.project(surface)-center)@screen_normal
            self.assertAlmostEqual(float(support.max()), guide['radius_pixels'], delta=1e-4)
            self.assertAlmostEqual(float(support.min()), -guide['radius_pixels'], delta=1e-4)

    def test_older_choices_restore_default_guides_and_invalid_width_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'choice.json'; store = ViewerStore(path)
            old = store.save(dict(count=2698, hand=-1, view=dict(x=0, y=0, scale=1)))['document']
            del old['viewer_choice']['guides']; path.write_text(json.dumps(old))
            resumed = ViewerStore(path)
            self.assertEqual(resumed.initial_guides, dict(width_percent=107., show_edges=True, show_centerline=True))
        for value in [dict(width_percent=float('nan')), dict(width_percent=200), dict(show_edges=1)]:
            with self.assertRaises(ValueError):
                validate_guides(value)

    def test_invalid_inputs_cannot_choose_a_different_model_or_write_a_choice(self):
        for count, hand in [(True,1), (2698.5,1), (0,1), (10001,1), (2698,0), (2698,True)]:
            with self.assertRaises(ValueError):
                validate_selection(count, hand)
        with self.assertRaises(ValueError):
            self.store.save(dict(count=2698, hand=-1, view=dict(x=0, y=0, scale=float('nan'))))


if __name__ == '__main__':
    unittest.main()
