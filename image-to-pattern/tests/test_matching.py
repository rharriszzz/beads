import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import matching, pov_patterns


class MatchingTests(unittest.TestCase):
    def test_exact_match(self):
        pat = pov_patterns.get_pattern(1)
        indices = pat.color_pattern * 2  # two repeats
        res = matching.match_pattern(indices, pat)
        self.assertEqual(res.mismatches, 0)
        self.assertEqual(res.matched, len(indices))
        self.assertEqual(res.match_rate, 1.0)

    def test_shifted_match(self):
        pat = pov_patterns.get_pattern(2)
        shifted = pat.color_pattern[3:] + pat.color_pattern[:3]
        indices = shifted * 2
        res = matching.match_pattern(indices, pat)
        self.assertEqual(res.offset, 3)
        self.assertEqual(res.mismatches, 0)

    def test_best_pattern_match(self):
        pat = pov_patterns.get_pattern(7)
        indices = pat.color_pattern * 1
        res = matching.best_pattern_match(indices)
        self.assertEqual(res.pattern.case, 7)

    def test_no_indices(self):
        pat = pov_patterns.get_pattern(1)
        res = matching.match_pattern([], pat)
        self.assertEqual(res.mismatches, 0)
        self.assertEqual(res.match_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
