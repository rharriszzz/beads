import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import geometry, segmentation


class GeometryTests(unittest.TestCase):
    def test_project_points_and_angles(self):
        cl = segmentation.Centerline(xs=[0, 10, 20], ys=[0, 0, 0])
        pts = [(0, 0), (10, 0), (20, 0)]
        arcs, projs, tangents = geometry.project_points_onto_centerline(pts, cl)
        self.assertEqual(arcs, [0.0, 10.0, 20.0])
        angles = geometry.neighbor_angles(projs, tangents)
        self.assertTrue(all(abs(a) < 1e-6 for a in angles))

    def test_angles_on_curve(self):
        cl = segmentation.Centerline(xs=[0, 10, 20], ys=[0, 5, 10])
        pts = [(0, 0), (10, 5), (20, 10)]
        _, projs, tangents = geometry.project_points_onto_centerline(pts, cl)
        angles = geometry.neighbor_angles(projs, tangents)
        self.assertEqual(len(angles), 2)


if __name__ == "__main__":
    unittest.main()
