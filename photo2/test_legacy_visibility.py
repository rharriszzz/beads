"""Check unknown-slot accounting and instrumentation against original palette bodies."""
import tempfile
import subprocess
import unittest
from pathlib import Path

import numpy as np

from legacy_visibility import (ROOT, decode, instrument_source, measure, render, wrapper)


class LegacyVisibilityChecks(unittest.TestCase):
    def test_missing_indices_do_not_compress_repeat_slots(self):
        ids = np.array([[1,1,3,3,3,5,5,7,7,7]])  # Four slots, two occurrences.
        result = measure(ids, 4, 2)
        self.assertEqual(result['pixels_by_occurrence_and_slot'], [[2,0,3,0],[2,0,3,0]])
        self.assertEqual(result['coverage']['1']['unseen_slots'], [1,3])
        self.assertEqual(result['coverage']['1']['occurrences_per_slot'], [2,0,2,0])
        self.assertEqual(result['zero_pixel_bead_indices'], [1,3,5,7])
        self.assertIsNone(result['visible_centroids'][1])
        self.assertEqual(result['coverage']['12']['slots_seen'], 0)

    def test_id_decode_preserves_byte_boundaries_and_rejects_unknown_codes(self):
        rgb = np.array([[[0,0,0],[255,0,0],[0,1,0],[1,1,0]]], dtype=np.uint8)
        np.testing.assert_array_equal(decode(rgb, 257), [[0,255,256,257]])
        with self.assertRaises(ValueError):
            decode(rgb, 256)

    def test_instrumentation_rejects_unrecognized_scene(self):
        with self.assertRaises(ValueError):
            instrument_source((ROOT/'beads.pov').read_text().replace('0.8, 0.7, 1.0','0.9, 0.7, 1.0'))

    def test_real_legacy_ids_match_palette_silhouette_and_colors(self):
        # Original case-1 bodies and placement versus independently materialized ID bodies.
        pattern = {'colors':[0,1,2,0,2,1,0,1,1,2,0,2,2], 'groups':60}
        with tempfile.TemporaryDirectory(prefix='beads-legacy-visibility-') as tmp:
            out = Path(tmp)
            instrument = out/'instrument.pov'
            instrument.write_text(instrument_source((ROOT/'beads.pov').read_text()))
            scene = out/'wrapper.pov'
            for hand in (1, -1):
                with self.subTest(hand=hand):
                    scene.write_text(f'#declare Helicity={hand};\n'+wrapper(pattern, instrument.name))
                    ids = decode(render(out,f'ids-{hand}',scene,'0',[],width=480,height=360), 780)
                    palette = render(out,f'palette-{hand}',scene,'0',[],palette=True,width=480,height=360)
                    mask = ids > 0
                    self.assertGreater(int(mask.sum()), 1000)
                    np.testing.assert_array_equal(mask, np.any(palette != 0,axis=2))
                    colors = np.array([[255,0,0],[0,255,0],[0,0,255]], dtype=np.uint8)
                    slot_colors = np.array(pattern['colors'])[(ids[mask]-1)%13]
                    np.testing.assert_array_equal(palette[mask], colors[slot_colors])

    def test_legacy_rejects_invalid_helicity(self):
        with tempfile.TemporaryDirectory(prefix='beads-invalid-helicity-') as tmp:
            out = Path(tmp)
            scene = out/'invalid.pov'
            for hand in (0, 2, .5):
                with self.subTest(hand=hand):
                    scene.write_text(f'#declare Helicity={hand};\n#include "beads.pov"\n')
                    with self.assertRaises(subprocess.CalledProcessError):
                        render(out, 'invalid', scene, '0', [], beauty=True, width=80, height=60)
                    self.assertIn('Helicity must be +1 or -1', (out/'invalid.log').read_text())


if __name__ == '__main__':
    unittest.main()
