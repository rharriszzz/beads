import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import layout, pov_patterns


class PovPatternsTests(unittest.TestCase):
    def test_lengths_match_declared(self):
        for pattern in pov_patterns.PATTERNS:
            self.assertEqual(len(pattern.color_pattern), pattern.pattern_length)
            self.assertEqual(pattern.pattern_length * pattern.ngroups, pattern.nbeads)

    def test_case3_length(self):
        p3 = pov_patterns.get_pattern(3)
        self.assertEqual(p3.pattern_length, 372)
        self.assertEqual(p3.nbeads, 744)

    def test_nrows_alignment(self):
        # Ensure row distribution sums correctly for all patterns
        for pattern in pov_patterns.PATTERNS:
            rows = layout.row_lengths_for_beads(pattern.nbeads)
            self.assertEqual(sum(rows), pattern.nbeads)

    def test_row_counts_known_cases(self):
        p1 = pov_patterns.get_pattern(1)
        rows1 = layout.row_lengths_for_beads(p1.nbeads)
        self.assertEqual(len(rows1), 103)
        self.assertEqual(rows1.count(7), 54)
        self.assertEqual(rows1.count(6), 49)

        p2 = pov_patterns.get_pattern(2)
        rows2 = layout.row_lengths_for_beads(p2.nbeads)
        self.assertEqual(len(rows2), 108)
        self.assertEqual(rows2.count(7), 52)
        self.assertEqual(rows2.count(6), 56)


if __name__ == "__main__":
    unittest.main()
