"""Graph controls independent of any rendered scene or evaluator index map."""
import unittest

from neighbor_graph import propagate, reciprocal


class NeighborGraphChecks(unittest.TestCase):
    def test_triangle_and_missing_edge_alternate_path(self):
        for edges in [[(10, 20, 1), (20, 30, 6), (10, 30, 7)],
                      [(10, 20, 1), (20, 30, 6)]]:
            result = propagate([10, 20, 30], reciprocal(edges))
            self.assertTrue(result['consistent'])
            self.assertEqual(result['labels'], {10: 0, 20: 1, 30: 7})

    def test_contradictory_triangle_and_duplicate_constraints(self):
        for edges in [[(0, 1, 1), (1, 2, 6), (0, 2, 6)],
                      [(0, 1, 1), (0, 1, 6)]]:
            result = propagate([0, 1, 2], reciprocal(edges))
            self.assertFalse(result['consistent'])
            self.assertTrue(result['conflicts'])

    def test_disconnected_offsets_and_isolated_vertex(self):
        result = propagate([9, 8, 7, 6, 5], reciprocal([(9, 8, 7), (7, 6, 6)]))
        self.assertTrue(result['consistent'])
        self.assertEqual([len(c['vertices']) for c in result['components']], [2, 2, 1])
        self.assertEqual([c['offset'] for c in result['components']], ['unknown']*3)

    def test_seam_winding_and_wrong_modulus(self):
        edges = reciprocal([(i, (i+1) % 20, 1) for i in range(20)])
        result = propagate(range(20), edges, modulus=20)
        self.assertTrue(result['consistent'])
        self.assertTrue(result['winding_edges'])
        self.assertEqual([result['labels'][i] % 20 for i in range(20)], list(range(20)))
        self.assertFalse(propagate(range(20), edges)['consistent'])
        self.assertFalse(propagate(range(20), edges, modulus=21)['consistent'])

    def test_wrong_bridge_is_consistent_but_does_not_certify_truth(self):
        # True indices 0,1,20,26; a falsely signed bridge 1->20 claims +6.
        result = propagate(['a', 'b', 'c', 'd'],
                           reciprocal([('a', 'b', 1), ('c', 'd', 6), ('b', 'c', 6)]))
        self.assertTrue(result['consistent'])
        self.assertEqual(result['labels']['c'], 7)
        self.assertNotEqual(result['labels']['c'], 20)

    def test_duplicate_indices_missing_reciprocals_and_bad_inputs(self):
        result = propagate([0, 1, 2], reciprocal([(0, 1, 1), (0, 2, 1)]))
        self.assertFalse(result['consistent'])
        self.assertEqual(result['duplicate_indices'], [[1, 2]])
        self.assertFalse(propagate([0, 1], [(0, 1, 1)])['consistent'])
        for vertices, edges in [([0, 0], []), ([0], [(0, 1, 1)]),
                                ([0, 1], [(0, 1, 2)])]:
            with self.assertRaises(ValueError):
                propagate(vertices, edges)

    def test_global_reversal_remains_consistent(self):
        edges = reciprocal([(4, 8, 1), (8, 3, 6), (4, 3, 7)])
        result = propagate([4, 8, 3], [(u, v, -d) for u, v, d in edges])
        self.assertTrue(result['consistent'])
        self.assertEqual(result['labels'], {4: 0, 8: -1, 3: -7})


if __name__ == '__main__':
    unittest.main()
