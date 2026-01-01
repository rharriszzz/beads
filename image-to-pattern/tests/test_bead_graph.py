import sys
from pathlib import Path
import unittest

from image_to_pattern import bead_graph, bead_detect

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class BeadGraphTests(unittest.TestCase):
    def test_order_beads_by_mst(self):
        beads = [
            bead_detect.DetectedBead(center=(0.0, 0.0), distance=1.0),
            bead_detect.DetectedBead(center=(1.0, 0.0), distance=1.0),
            bead_detect.DetectedBead(center=(2.0, 0.0), distance=1.0),
        ]
        ordered = bead_graph.order_beads_by_mst(beads)
        self.assertEqual(len(ordered.centers), 3)
        # Should preserve linear order along the chain
        self.assertEqual(ordered.centers[0], (0.0, 0.0))
        self.assertEqual(ordered.centers[-1], (2.0, 0.0))


if __name__ == "__main__":
    unittest.main()
