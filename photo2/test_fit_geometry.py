"""Numerical identifiability and observation-assignment checks."""
import unittest

import numpy as np

from fit_geometry import centers, match


class GeometryChecks(unittest.TestCase):
    def test_one_to_one_matching_prevents_reusing_center(self):
        errors, indices = match(np.array([[0., 0.], [.1, 0.]]),
                                np.array([[0., 0.], [10., 0.]]))
        self.assertEqual(len(set(indices)), 2)
        self.assertGreater(errors.sum(), 90)

    def test_unrestricted_projection_has_exact_hand_ambiguity(self):
        global_values = [24., 6.7, 34.]
        local = [.3, .45, -2.]
        positive, ip = centers(global_values, local, 1, front_only=False)
        negative, im = centers(global_values, [local[0], np.pi-local[1], local[2]],
                               -1, front_only=False)
        np.testing.assert_array_equal(ip, im)
        np.testing.assert_allclose(positive, negative, atol=1e-11)
        # Front-only visibility removes that specific symmetry.
        a, _ = centers(global_values, local, 1)
        b, _ = centers(global_values, [local[0], np.pi-local[1], local[2]], -1)
        self.assertGreater(np.sqrt(match(a, b)[0].mean()), 3)

    def test_pitch_count_twist_gauge_preserves_visible_centers(self):
        p, b, r = 24., 6.7, 34.
        local = np.array([.3, .45, -2.])
        hand = -1
        new_b = 7.2
        d = p/b
        twist = 160/d * (hand*2*np.pi/b - hand*2*np.pi/new_b)
        adjusted = local.copy()
        adjusted[1] -= twist*(local[0]*d-80)/160
        a, ia = centers([p,b,r], local, hand)
        z, iz = centers([d*new_b,new_b,r], adjusted, hand, twist=twist)
        np.testing.assert_array_equal(ia, iz)
        np.testing.assert_allclose(a, z, atol=1e-10)

    def test_known_front_lattice_fixed_geometry_distinguishes_hands(self):
        from fit_geometry import fit_local
        global_values = [24., 6.7, 34.]
        obs, _ = centers(global_values, [.3, .45, -2.], 1)
        obs = obs[(obs[:, 0] > 10) & (obs[:, 0] < 150)]
        # Synthetic centers, not an image round trip. Deterministic noise.
        obs = obs + np.random.default_rng(73).normal(0,.2,obs.shape)
        positive = min(fit_local(obs,global_values,1,s)[1] for s in [17,43])
        negative = min(fit_local(obs,global_values,-1,s)[1] for s in [17,43])
        self.assertLess(np.sqrt(positive), .5)
        self.assertGreater(np.sqrt(negative), 3.)


if __name__ == '__main__':
    unittest.main()
