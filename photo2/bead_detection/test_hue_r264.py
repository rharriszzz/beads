"""Independent example proving a leaf-control coordinate can move."""
import unittest
from .analyze_r264 import leaf_control
from .bounded_detect import Parameters
from dataclasses import asdict


class LeafControlTests(unittest.TestCase):
    def test_bright_terminal_leaf_can_change_supported_coordinate(self):
        # root -> branch, with bright lateral leaf and dark downward leaf.
        # Production keeps root/branch; bright leaf has its own value as floor.
        t={'accepted':[[0,0,-1,245,0,0,1,True],
                       [1,0,0,230,0,0,1,True],
                       [2,0,1,225,0,0,1,False],
                       [1,1,1,100,0,0,1,False]],
           'stops':[], 'retreat_floor_dn':[100,100,225,100]}
        result,restored=leaf_control(t,asdict(Parameters()))
        self.assertEqual(restored,[2])
        self.assertEqual(result['location'],[1,0])
        self.assertEqual(t['accepted'][2][7],False) # immutable production evidence
        # Original two-pixel support chooses [0,0] by the native row-major tie.
        self.assertEqual(result['pixel_count'],3)

    def test_dark_frontier_leaf_is_not_restored(self):
        t={'accepted':[[0,0,-1,245,0,0,1,True],[1,0,0,225,0,0,1,False]],
           'stops':[[2,0,1,80,0,0,0,'dark-frontier',2]],'retreat_floor_dn':[80,80]}
        result,restored=leaf_control(t,asdict(Parameters()))
        self.assertEqual(restored,[])
        self.assertEqual(result['location'],[0,0])


if __name__=='__main__':unittest.main()
