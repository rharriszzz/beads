"""Scientific invariants and a real POV-Ray visibility integration check."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from synthetic_benchmark import (Geometry, boundaries, candidates, center_rmse,
                                 decode, layout, render, write_include)


class SyntheticChecks(unittest.TestCase):
    def test_gauge_preserves_bodies_and_reflection_preserves_projection(self):
        for hand in [-1, 1]:
            variants = candidates(Geometry(hand=hand))
            truth, gauge, reflected = [layout(variants[n]) for n in
                                       ['truth', 'gauge_equivalent', 'depth_reflection']]
            np.testing.assert_array_equal(truth['k'], gauge['k'])
            for key in ['positions', 'axes']:
                np.testing.assert_allclose(truth[key], gauge[key], atol=1e-12)
                np.testing.assert_allclose(truth[key]*[1,1,-1], reflected[key], atol=1e-12)
            matrices = np.stack([truth['bx'], truth['axes'], truth['bz']], axis=2)
            np.testing.assert_allclose(np.linalg.det(matrices), 1., atol=1e-12)

    def test_unpenalized_superset_cannot_worsen_partial_center_match(self):
        variants = candidates(Geometry())
        a, b = layout(variants['truth']), layout(variants['double_density_stress'])
        truth = a['positions'][np.abs(a['positions'][:,0])<60,:2]
        dense = b['positions'][np.abs(b['positions'][:,0])<60,:2]
        obs = truth[::3]+np.random.default_rng(9).normal(0,2,truth[::3].shape)
        self.assertLessEqual(center_rmse(obs, dense), center_rmse(obs, truth)+1e-12)
        self.assertIsNone(center_rmse(obs, dense[:1]))

    def test_masks_reject_unknown_colors_and_boundaries_ignore_id_values(self):
        colors = np.array([[20,30,40], [60,70,80]], dtype=np.uint8)
        rgb = np.array([[[0,0,0], colors[0], colors[1]]], dtype=np.uint8)
        np.testing.assert_array_equal(decode(rgb, colors), [[0,1,2]])
        rgb[0,0,0] = 1
        with self.assertRaises(ValueError):
            decode(rgb, colors)
        ids = np.array([[0,1,1,2,0], [0,1,2,2,0]])
        np.testing.assert_array_equal(boundaries(ids), boundaries(np.choose(ids,[0,77,4])))

    def test_renderer_front_body_completely_hides_identical_back_body(self):
        g = Geometry()
        data = {k:v[:2].copy() for k,v in layout(g).items()}
        data['positions'][:] = [[0,0,10], [0,0,-10]]
        data['axes'][:] = [1,0,0]
        data['bx'][:] = [0,-1,0]
        data['bz'][:] = [0,0,1]
        with tempfile.TemporaryDirectory(prefix='beads-visibility-') as tmp:
            directory = Path(tmp)
            write_include(directory, g, data)
            commands = []
            full = decode(render(directory, 'full', commands), data['colors'])
            rear = decode(render(directory, 'rear', commands, only=1), data['colors'])
        self.assertGreater(np.count_nonzero(full==1), 100)
        self.assertFalse(np.any(full==2))
        np.testing.assert_array_equal(full>0, rear>0)


if __name__ == '__main__':
    unittest.main()
