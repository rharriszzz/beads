"""Independent lattice enumeration and geometric boundary tests; no photo inputs."""
import math
import unittest
from collections import Counter, defaultdict

from beadwork.graph_paper import boundary, layout, pattern_layout, representative


def enumerate_site(k, x0):
    # Independent integer search, not the producer's modular representative.
    sites = [(x, y) for y in range(k // 7 - abs(k) - abs(x0) - 20,
                                   k // 6 + abs(k) + abs(x0) + 21)
             for x in range(x0, x0 + 13)
             if x + 13 * y == 2 * k and (x + y) % 2 == 0]
    assert len(sites) == 1
    return sites[0]


def above(x, y, cut):
    for (a, b), (c, d) in zip(cut, cut[1:]):
        if b == d and min(a, c) <= x <= max(a, c):
            return y > b
    raise AssertionError((x, y, cut))


def ellipse_clear(point, p, q):
    # Independent distance from segment to the unit-circle-normalized ellipse.
    ax, ay = (p[0] - point['x']) * 24 / 18, (p[1] - point['y']) * 32 / 14
    bx, by = (q[0] - point['x']) * 24 / 18, (q[1] - point['y']) * 32 / 14
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy))) if dx or dy else 0
    return math.hypot(ax + t * dx, ay + t * dy) > 1


class GraphPaperTests(unittest.TestCase):
    def test_independent_representatives_and_directions(self):
        for x0 in [-13, -1, 0, 7]:
            for k in range(-100, 101):
                x, y = representative(k, x0)
                self.assertEqual((x, y), enumerate_site(k, x0))
                a, b = (x + y) // 2, (y - x) // 2
                self.assertEqual(7 * a + 6 * b, k)
                for dx, dy, dk in [(2, 0, 1), (-1, 1, 6), (1, 1, 7)]:
                    self.assertEqual(x + dx + 13 * (y + dy), 2 * (k + dk))

    def test_arbitrary_lengths_origins_and_strips(self):
        for length in [1, 2, 7, 13, 17, 52, 104, 207, 208, 209, 299, 338]:
            for start in [-23, 0, 5, 111]:
                for x0 in [-13, -1, 0, 7]:
                    with self.subTest(length=length, start=start, x0=x0):
                        paper = layout(length, start, x0)
                        rows = defaultdict(list)
                        chosen = []
                        for r in paper['points']:
                            rows[r['y']].append(r)
                            cx, cy = representative(r['k'], x0)
                            m = r['lateral_copy']
                            self.assertEqual((r['x'], r['y']), (cx + 13 * m, cy - m))
                            self.assertEqual(r['position'], (r['k'] - start) % length)
                            geometric = (x0 <= r['x'] < x0 + 13
                                         and above(r['x'], r['y'], paper['start_boundary'])
                                         and not above(r['x'], r['y'], paper['end_boundary']))
                            self.assertEqual(geometric, r['in_chosen_interval'])
                            if geometric:
                                chosen.append(r['k'])
                            for cut in [paper['start_boundary'], paper['end_boundary']]:
                                if abs(r['y'] - cut[0][1]) < 2:
                                    for p, q in zip(cut, cut[1:]):
                                        self.assertTrue(ellipse_clear(r, p, q))
                        self.assertEqual(sorted(chosen), list(range(start, start + length)))
                        for i, (y, row) in enumerate(sorted(rows.items())):
                            self.assertEqual(Counter(r['side'] for r in row),
                                             {'left': 7, 'basic': len(row) - 14, 'right': 7})
                            self.assertIn(len(row), [20, 21])
                            for left, right in zip(row, row[1:]):
                                self.assertEqual(right['k'] - left['k'], 1)
                                self.assertEqual(right['x'] - left['x'], 2)
                            basic = [r for r in row if r['side'] == 'basic']
                            for name, x in [('left', basic[0]['x'] - 1), ('right', basic[-1]['x'] + 1)]:
                                self.assertEqual(paper['side_boundaries'][name][2*i:2*i+2],
                                                 [[x, y-.5], [x, y+.5]])
                                for r in row:
                                    self.assertTrue(ellipse_clear(r, [x, y-.5], [x, y+.5]))

    def test_double_seams_and_current_membership(self):
        paper = layout(208)
        row = [r for r in paper['points'] if r['y'] == 1]
        self.assertEqual((row[0]['x'], row[0]['k'], row[0]['lateral_copy']), (-15, -1, -2))
        self.assertEqual((row[-1]['x'], row[-1]['k'], row[-1]['lateral_copy']), (25, 19, 2))
        self.assertEqual(len(paper['points']), 984)
        self.assertEqual(sum(p['in_chosen_interval'] for p in paper['points']), 208)
        self.assertEqual(paper['start_boundary'], [[-2, -.5], [12, -.5]])
        self.assertEqual(paper['end_boundary'], [[-2, 31.5], [12, 31.5]])
        self.assertEqual(boundary(5), [[-2, .5], [9, .5], [9, -.5], [12, -.5]])
        self.assertEqual(boundary(22), [[-2, 3.5], [4, 3.5], [4, 2.5], [12, 2.5]])

    def test_sequence_only_unknowns_and_alias_colors(self):
        strict, provisional = 'BRYBRYBRYBRYBRYB?', 'BRYBRYBRYBRYBRYBY'
        codes = dict(B='black', R='red', Y='yellow', **{'?': '?'})
        paper = pattern_layout(strict, provisional, start=5, x0=7)
        identities = defaultdict(set)
        for r in paper['points']:
            i = (r['k'] - 5) % 17
            self.assertEqual(r['strict_color'], codes[strict[i]])
            self.assertEqual(r['provisional_color'], codes[provisional[i]])
            self.assertEqual(r['tentative'], i == 16)
            identities[r['k']].add((tuple(r['canonical_xy']), r['strict_color'], r['provisional_color']))
        self.assertTrue(all(len(v) == 1 for v in identities.values()))
        self.assertEqual(pattern_layout(['red', '?'])['points'],
                         pattern_layout('R ?')['points'])

    def test_public_inputs_fail_explicitly(self):
        for kwargs in [dict(length=0), dict(length=-2), dict(length=1.5), dict(length=True),
                       dict(length=17, start=.5), dict(length=17, x0=1.1),
                       dict(length=17, extension_rows=-1), dict(length=17, side_beads=-1),
                       dict(length=17, minimum_rows=-1)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                layout(**kwargs)
        for strict, provisional in [('', None), ('RX', None), ('RB', 'R'), ([42], None)]:
            with self.assertRaises(ValueError):
                pattern_layout(strict, provisional)


if __name__ == '__main__':
    unittest.main()
