"""Numerical contracts with independent synthetic evidence, not photo ground truth."""
import unittest
import numpy as np
from reconstruct import ClosedPath, classify, layout, period_candidates


class ReconstructionTests(unittest.TestCase):
    def test_closed_curve_has_uniform_distance_and_continuous_frame(self):
        angle = np.linspace(0, 2 * np.pi, 81)
        path = ClosedPath(np.c_[500 * np.cos(angle), 500 * np.sin(angle)])
        self.assertAlmostEqual(path.length, 1000 * np.pi, delta=3)
        xy, tangent, normal = path.evaluate(np.linspace(0, path.length, 501))
        np.testing.assert_allclose(xy[0], xy[-1], atol=1e-9)
        np.testing.assert_allclose(tangent[0], tangent[-1], atol=1e-9)
        np.testing.assert_allclose((normal * tangent).sum(axis=1), 0, atol=1e-12)
        chord = np.linalg.norm(np.diff(xy, axis=0), axis=1)
        self.assertLess(np.std(chord) / np.mean(chord), .001)

    def test_handedness_mirrors_normal_displacement_not_path_or_height(self):
        angle = np.linspace(0, 2 * np.pi, 81)
        path = ClosedPath(np.c_[500 * np.cos(angle), 500 * np.sin(angle)])
        settings = dict(turn_pitch_px=22, beads_per_turn=6.5, rope_radius_px=30,
                        bead_radius_px=13, handedness=1, phase_degrees=0)
        plus = layout(path, settings, 1)
        minus = layout(path, settings, -1)
        center, _, _ = path.evaluate(np.arange(len(plus[0])) * path.length / len(plus[0]))
        np.testing.assert_allclose((plus[0] + minus[0]) / 2, center, atol=1e-10)
        np.testing.assert_allclose(plus[1], minus[1])
        self.assertGreaterEqual(float(plus[1].min()), 13)

    def test_period_recovery_with_hidden_beads_and_noise(self):
        rng = np.random.default_rng(71)
        pattern = rng.integers(0, 3, 271)
        sequence = np.tile(pattern, 12)
        noisy = rng.random(len(sequence)) < .06
        sequence[noisy] = rng.integers(0, 3, noisy.sum())
        hidden = rng.random(len(sequence)) < .55
        sequence[hidden] = -1
        weights = (~hidden).astype(float)
        candidates = period_candidates(sequence, weights)
        self.assertEqual(candidates[0]['period'], 271)
        self.assertGreater(candidates[0]['held_out_accuracy'], .9)
        # Arbitrarily renumbering categorical colors cannot change the ranking.
        relabelled = sequence.copy()
        relabelled[~hidden] = np.array([2, 0, 1])[sequence[~hidden]]
        other = period_candidates(relabelled, weights)
        self.assertEqual([c['period'] for c in candidates], [c['period'] for c in other])
        np.testing.assert_allclose([c['held_out_accuracy'] for c in candidates],
                                   [c['held_out_accuracy'] for c in other])

    def test_unknown_residues_remain_unknown(self):
        labels = np.tile([0, -1, 1, -1, 2, -1, 1], 20)
        weights = (labels >= 0).astype(float)
        candidate = period_candidates(labels, weights, 7, 7)[0]
        self.assertEqual(candidate['pattern'], [0, -1, 1, -1, 2, -1, 1])
        self.assertEqual(candidate['held_out_accuracy'], 1)
        self.assertEqual(period_candidates(np.full(100, -1), np.zeros(100)), [])

    def test_paper_and_shadow_are_not_red_or_black(self):
        rgb = np.array([[205, 90, 175], [105, 40, 85], [180, 25, 40], [245, 160, 12], [12, 8, 10]])
        np.testing.assert_array_equal(classify(rgb), [-1, -1, 1, 2, 0])


if __name__ == '__main__':
    unittest.main()
