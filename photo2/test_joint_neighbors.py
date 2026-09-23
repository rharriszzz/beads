"""Independent controls for local lattice constraints and anonymous tracing."""
import unittest

import numpy as np

from inference_audit import evaluate
from inference_controls import brick_ring
from joint_neighbors import infer_joint, motifs, trace_families


def canonical(edges, mapping):
    return sorted((min(mapping[u], mapping[v]), max(mapping[u], mapping[v]),
                   d if mapping[u] < mapping[v] else -d) for u, v, d in edges)


class JointNeighborsChecks(unittest.TestCase):
    def test_ideal_lattice_all_edges_and_relative_indices(self):
        xy, cov, truth, n = brick_ring()
        for moments in (None, cov):
            output = infer_joint(xy, moments)
            s = evaluate(truth, n, output['variants'][0])['summary']
            self.assertEqual(s['proposed_edges'], 520)
            self.assertEqual(s['true_neighbor_pairs'], 520)
            self.assertEqual(s['signed_correct_by_global_reversal'][1], 520)
            self.assertEqual(s['consistent_wrong_nonseed_up_to_reversal'], 0)
            self.assertEqual(s['consistent_nontrivial_components'], 1)
            self.assertEqual(s['consistent_nonseed'], 199)

    def test_triangle_checks_sum_and_noncollinearity(self):
        xy = np.array([[0., 0.], [0., 1.], [1., 1.]])
        self.assertEqual(len(motifs(xy, [(0, 1, 1), (0, 2, 7), (1, 2, 6)])[0]), 1)
        self.assertEqual(motifs(xy, [(0, 1, 1), (0, 2, 6), (1, 2, 7)])[0], [])
        xy[2] = [0., 2.]
        self.assertEqual(motifs(xy, [(0, 1, 1), (0, 2, 7), (1, 2, 6)])[0], [])

    def test_continuations_require_same_sign_smoothness_and_spacing(self):
        edges = [(0, 1, 6), (1, 2, 6)]
        self.assertEqual(motifs(np.array([[0., 0.], [1., 0.], [2., 0.]]), edges)[1], [[0, 1, 1]])
        for end in ([1., 1.], [-1., 0.], [4., 0.]):
            self.assertEqual(motifs(np.array([[0., 0.], [1., 0.], end]), edges)[1], [])
        self.assertEqual(motifs(np.array([[0., 0.], [1., 0.], [2., 0.]]),
                                [(0, 1, 6), (1, 2, 7)])[1], [])

    def test_permutation_rotation_translation_scale(self):
        xy, cov, _, _ = brick_ring()
        # Include the deliberate holes and crossing where candidate ties matter.
        xy = np.vstack((xy, xy+[1.1*np.max(xy[:, 0]), 13.]))
        cov = np.concatenate((cov, cov))
        keep = np.ones(len(xy), bool)
        keep[[47, 52, 57]] = False
        xy, cov = xy[keep], cov[keep]
        reference = infer_joint(xy, cov)
        order = np.random.Generator(np.random.PCG64(43)).permutation(len(xy))
        angle = .731
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        moved = infer_joint(2.3*xy[order]@rotation.T+[723, -40],
                            2.3**2*rotation@cov[order]@rotation.T)
        for a, b in zip(reference['variants'], moved['variants']):
            self.assertEqual(canonical(a['edges'], np.arange(len(xy))), canonical(b['edges'], order))

    def test_every_selected_edge_has_retained_triangle_and_continuation(self):
        xy, cov, _, _ = brick_ring()
        keep = np.ones(len(xy), bool)
        keep[[47, 52, 57]] = False
        result = infer_joint(xy[keep], cov[keep])
        selected = set(result['selected_candidate_ids'])
        self.assertTrue(selected)
        triangle_support = {e for tri in result['triangles'] if set(tri) <= selected for e in tri}
        trace_support = {e for a, b, _ in result['continuations']
                         if a in selected and b in selected for e in (a, b)}
        self.assertEqual(selected, triangle_support)
        self.assertEqual(selected, trace_support)
        for variant in result['variants']:
            slots = [(u, d) for u, v, d in variant['edges']]+[(v, -d) for u, v, d in variant['edges']]
            self.assertEqual(len(slots), len(set(slots)))

    def test_traces_cover_edges_once_and_keep_family_and_offsets(self):
        edges = [(0, 1, 1), (1, 2, 1), (3, 4, 6), (4, 5, 6), (3, 5, -6)]
        traces = trace_families(edges)
        self.assertEqual(sum(len(t['vertices'])-1 for t in traces), len(edges))
        self.assertEqual(sum(t['closed'] for t in traces), 1)
        self.assertTrue(all(t['offset'] == 'unknown' for t in traces))
        self.assertEqual({t['family'] for t in traces}, {1, 6})

    def test_bad_inputs_and_convention_symmetry(self):
        for xy in ([], [[0, 0]]*4, [[0, 0], [1, 0], [2, 0], [3, 0]],
                   [[0, 0], [1, 0], [0, 1], [np.nan, 1]]):
            with self.assertRaises(ValueError):
                infer_joint(xy)
        xy, cov, _, _ = brick_ring()
        a, b = infer_joint(xy, cov)['variants']
        transformed = [[u, v, -d if abs(d) == 1 else (1 if d > 0 else -1)*(13-abs(d))]
                       for u, v, d in a['edges']]
        self.assertEqual(transformed, b['edges'])

    def test_indistinguishable_duplicates_abstain_instead_of_breaking_ties(self):
        xy, cov, _, _ = brick_ring()
        result = infer_joint(np.repeat(xy, 2, axis=0), np.repeat(cov, 2, axis=0))
        for variant in result['variants']:
            self.assertGreater(len(variant['ambiguous']), 0)
            self.assertEqual(variant['edges'], [])


if __name__ == '__main__':
    unittest.main()
