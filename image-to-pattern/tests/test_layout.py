import sys
from pathlib import Path
import unittest

# Ensure the package inside this workspace is importable when running tests directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import layout


class LayoutTests(unittest.TestCase):
    def test_case1_row_counts(self):
        # case 1 from beads.pov: pattern_length=24, ngroups=28 -> nbeads=672
        nbeads = 24 * 28
        lengths = layout.row_lengths_for_beads(nbeads)
        self.assertEqual(len(lengths), 103)
        self.assertEqual(sum(lengths), nbeads)
        self.assertEqual(lengths.count(7), 54)
        self.assertEqual(lengths.count(6), 49)

    def test_case7_row_counts(self):
        # case 7: pattern_length=24, ngroups=28 -> same nbeads as case1
        nbeads = 24 * 28
        nrows = layout.compute_nrows(nbeads)
        self.assertEqual(nrows, 103)
        lengths = layout.row_lengths_for_beads(nbeads)
        self.assertEqual(lengths.count(7) + lengths.count(6), nrows)

    def test_case2_row_counts(self):
        # case 2: pattern_length=35, ngroups=20 -> nbeads=700
        nbeads = 35 * 20
        lengths = layout.row_lengths_for_beads(nbeads)
        self.assertEqual(len(lengths), 108)
        self.assertEqual(sum(lengths), nbeads)
        self.assertEqual(lengths.count(7), 52)
        self.assertEqual(lengths.count(6), 56)

    def test_bead_index_mapping_length(self):
        nbeads = 35 * 20
        mapping = layout.bead_index_to_row_col(nbeads)
        self.assertEqual(len(mapping), nbeads)
        # Ensure mapping rows respect computed row lengths
        lengths = layout.row_lengths_for_beads(nbeads)
        offset = 0
        for row_idx, length in enumerate(lengths):
            row_slice = mapping[offset : offset + length]
            self.assertTrue(all(r == row_idx for r, _ in row_slice))
            self.assertEqual([c for _, c in row_slice], list(range(length)))
            offset += length


if __name__ == "__main__":
    unittest.main()
