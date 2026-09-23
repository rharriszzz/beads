import itertools
import unittest

from partial_word import canonical, completion_summary, fit_period, holdout, primitive, scan


class PartialWordTests(unittest.TestCase):
    def test_exhaustive_independent_residue_pair_oracle(self):
        # Independent pairwise definition, including holes between conflicts.
        for n in range(1, 6):
            for word in itertools.product((None, 0, 1, 2), repeat=n):
                for p in range(1, n + 1):
                    expected = all(word[i] == word[j] for i in range(n) for j in range(i + 1, n)
                                   if word[i] is not None and word[j] is not None and (j-i) % p == 0)
                    fit = fit_period(word, p)
                    self.assertEqual(fit['compatible'], expected)
                    if not expected:
                        a, b = fit['witness_positions']
                        self.assertEqual((b-a) % p, 0)
                        self.assertNotEqual(word[a], word[b])
                    else:
                        for slot, ids in enumerate(fit['support_positions']):
                            self.assertEqual(ids, [i for i in range(n) if i % p == slot and word[i] is not None])

    def test_tiny_controls_and_original_unknowns(self):
        self.assertFalse(fit_period([0, None, 1], 1)['compatible'])
        word = [0, None, 2, 0, 1, None]
        before = word.copy()
        self.assertEqual(fit_period(word, 3)['slot_colors'], [0, 1, 2])
        self.assertEqual(word, before)
        full = [0, 1, 2] * 2
        self.assertEqual([f['period'] for f in scan(full)['compatible']], [3])
        self.assertEqual(fit_period([0, None, 0, None], 2)['slot_colors'], [0, None])

    def test_closure_is_optional_and_does_not_remove_candidates(self):
        word = [None] * 10
        open_scan = scan(word)
        closed = scan(word, exact_count=10)
        self.assertEqual([x['period'] for x in closed['compatible']], [1, 2, 3, 4, 5])
        self.assertEqual([x['period'] for x in closed['compatible'] if x['whole_repeat_closure']], [1, 2, 5])
        self.assertTrue(all(x['whole_repeat_closure'] is None for x in open_scan['compatible']))

    def test_frozen_holdout_and_abstention(self):
        # Held-out disagreement must not delete a period that training accepts.
        result = holdout([0, 0, 1, 1], 2, 4)
        p1 = next(x for x in result['compatible'] if x['period'] == 1)
        self.assertEqual((p1['correct'], p1['wrong'], p1['abstained']), (0, 2, 0))
        abstain = holdout([None, None, 0, 1], 2, 4)
        self.assertTrue(all(x['abstained'] == 2 for x in abstain['compatible']))

    def test_rotation_reversal_and_color_identity(self):
        word = [0, 0, 1, 2, 1]
        key = canonical(word)['key']
        for base in (word, word[::-1]):
            for k in range(len(word)):
                self.assertEqual(canonical(base[k:] + base[:k])['key'], key)
        self.assertEqual(canonical(word * 3)['key'], key)
        self.assertNotEqual(canonical([0, 0, 1])['key'], canonical([0, 0, 2])['key'])
        self.assertEqual(canonical([0, None, 0, None])['block_length'], 4)
        with self.assertRaises(ValueError):
            primitive([0, None])

    def test_completion_alternatives_not_filled(self):
        slots = [0, None, 2]
        summary = completion_summary(slots)
        self.assertEqual(summary['raw_completion_count'], 3)
        self.assertEqual(len(summary['canonical_completions']), 3)
        self.assertEqual(slots, [0, None, 2])
        summary = completion_summary([None] * 13)
        self.assertEqual(summary['raw_completion_count'], 3**13)
        self.assertIsNone(summary['canonical_completions'])

    def test_invalid_inputs(self):
        for word in ([], [3], [False], [-1], ['unknown']):
            with self.assertRaises(ValueError):
                scan(word)
        for p in (0, 4, True, 1.5):
            with self.assertRaises(ValueError):
                fit_period([0, 1, 2], p)
        with self.assertRaises(ValueError):
            scan([0, 1], exact_count=1)


if __name__ == '__main__':
    unittest.main()
