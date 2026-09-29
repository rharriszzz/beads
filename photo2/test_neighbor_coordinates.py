import unittest
from neighbor_coordinates import DirectionCoordinates as D, resolve_local


class DirectionCoordinateTests(unittest.TestCase):
    def test_alternate_routes_to_same_body(self):
        direct=D().step(7)
        via=D().step(1).step(6)
        self.assertNotEqual(direct,via)
        self.assertEqual(direct.bead_index(23),via.bead_index(23))
        graph=resolve_local(['a','b','c'],[('a','c',7),('a','b',1),('b','c',6)],'a')
        self.assertFalse(graph['conflicts'])
        self.assertEqual(len(graph['consistent_alternate_paths']),1)

    def test_signed_backtracking_and_skipped_indices(self):
        for d in [-7,-6,-1,1,6,7]:
            self.assertEqual(D().step(d).step(-d),D())
        graph=resolve_local(['a','b','c','unknown'],[('a','b',6),('b','c',7)],'b',origin=100)
        self.assertEqual(graph['derived_component_indices'],{'b':100,'a':94,'c':107})
        self.assertEqual(graph['unresolved'],['unknown'])

    def test_wrong_cycle_and_distinct_body_collision(self):
        graph=resolve_local(['a','b','c'],[('a','b',1),('b','c',6),('a','c',6)],'a')
        self.assertTrue(graph['conflicts'])
        collision=resolve_local(['a','b','c'],[('a','b',6),('a','c',6)],'a')
        self.assertEqual(collision['distinct_observation_index_collisions'],[('b','c')])

    def test_no_invented_immediate_neighbor(self):
        with self.assertRaises(ValueError):D().step(2)
        with self.assertRaises(ValueError):resolve_local(['a'],[('a','missing',1)],'a')


if __name__=='__main__':unittest.main()
