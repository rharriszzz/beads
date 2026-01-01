import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from image_to_pattern import periodicity


class PeriodicityTests(unittest.TestCase):
    def test_normalized_autocorrelation_constant(self):
        corrs = periodicity.normalized_autocorrelation([1, 1, 1])
        self.assertTrue((corrs == 1.0).all())

    def test_estimate_period_simple(self):
        seq = [0, 1, 0, 1, 0, 1]
        period = periodicity.estimate_period(seq, max_period=4, min_period=1)
        self.assertEqual(period, 2)

    def test_estimate_period_noise(self):
        seq = [0, 1, 0, 1, 0, 1, 0, 1]
        # Flip a couple entries to simulate noise
        seq_noisy = seq.copy()
        seq_noisy[3] = 0
        seq_noisy[5] = 0
        period = periodicity.estimate_period(seq_noisy, max_period=4, min_period=1)
        self.assertEqual(period, 2)

    def test_extract_pattern(self):
        seq = [0, 1, 2, 0, 1, 2, 0]
        pat = periodicity.extract_pattern(seq, period=3)
        self.assertEqual(pat, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
