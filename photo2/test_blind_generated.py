"""Controls for the blind JPEG pipeline; no renderer pattern fixtures."""
import unittest
from unittest.mock import patch
import numpy as np

from blind_generated import detect, color_name
from blind_generated_index import periods, attempt


class BlindGeneratedTests(unittest.TestCase):
    def test_empty_white_floor_has_no_beads(self):
        labels, xy, mask, _ = detect(np.full((80, 100, 3), 255, np.uint8))
        self.assertEqual(len(xy), 0)
        self.assertFalse(labels.any())
        self.assertFalse(mask.any())

    def test_touching_same_color_bodies_are_separated(self):
        y, x = np.indices((80, 100))
        image = np.full((80, 100, 3), 255, np.uint8)
        for cx in [40, 57]:
            radius = np.hypot(x-cx, y-40)
            body = radius <= 10
            brightness = np.clip(230 - 9*radius, 0, 255)
            image[body] = np.column_stack([brightness[body], brightness[body]*.08, brightness[body]*.08]).astype(np.uint8)
        labels, xy, _, _ = detect(image)
        self.assertEqual(len(xy), 2)
        self.assertNotEqual(labels[40, 40], labels[40, 57])
        self.assertGreater(labels[40, 40], 0)
        self.assertGreater(labels[40, 57], 0)

    def test_red_hue_wrap_does_not_become_cyan(self):
        hsv = np.array([[.99,.9,.8],[.01,.9,.8],[.995,.8,.8],[.005,.8,.8]])
        self.assertEqual(color_name(hsv, 1)[0], 'red')

    def test_five_color_period_and_missing_positions(self):
        colors = ['red','green','blue','white','black']
        fits = periods({i: colors[i % 5] for i in range(15) if i % 5 != 2})
        fit = next(f for f in fits if f['period'] == 5)
        self.assertEqual(fit['slot_colors'], ['red','green',None,'white','black'])
        self.assertEqual(fit['missing_slots'], [2])
        self.assertFalse(any(f['period'] < 5 for f in fits))

    def test_conflicting_index_graph_never_reaches_period_scan(self):
        rows = [dict(observation_id=i+1, flags=[], marker_xy=[i, 0], color='red') for i in range(13)]
        edges = [[i,i+1,1] for i in range(12)] + [[0,2,6]]
        proposal = dict(parameters={}, variants=[dict(convention=1, edges=edges, ambiguous=[], nonreciprocal=[])])
        with patch('blind_generated_index.infer', return_value=proposal), patch('blind_generated_index.periods') as scan:
            result = attempt(rows, 'marker_xy')
            scan.assert_not_called()
        self.assertFalse(result['variants'][0]['consistent'])
        self.assertGreater(result['variants'][0]['conflicting_directed_edges'], 0)


if __name__ == '__main__':
    unittest.main()
