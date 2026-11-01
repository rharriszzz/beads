"""Publication boundary, data extraction contract, and navigable local assets."""
import importlib.util
import json
import re
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts/build_site.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class StaticSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.candidate_data()
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / 'site'
        cls.count, cls.size = build.build(cls.output)
        cls.html = (cls.output / 'index.html').read_text()
        cls.doc = build.Document(cls.html)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_epochs_recount_their_actual_retained_labels(self):
        names = {'R': 'red', 'Y': 'yellow', 'B': 'black'}
        for key, epoch in self.data['epochs'].items():
            statuses = Counter()
            seen = set()
            agreements = total = 0
            for entry in epoch['entries']:
                counts, ids, blocks = entry['counts'], entry['ids'], entry['geographic_blocks']
                n = sum(counts.values())
                self.assertEqual(n, len(ids))
                self.assertFalse(seen.intersection(ids))
                seen.update(ids)
                state = ('conflicting' if len(counts) > 1 else
                         'supported' if n >= 3 and len(blocks) >= 3 else 'insufficient')
                self.assertEqual(state, entry['status'])
                statuses[state] += 1
                total += n
                agreements += counts.get(names[self.data['candidate'][entry['position']]], 0)
            self.assertEqual(dict(statuses), {k: v for k, v in epoch['statuses'].items() if v})
            self.assertEqual((agreements, total), (epoch['agreements'], epoch['observations']))
            if key == 'r347':
                self.assertNotIn('R332-R-0037-0040', seen)
                self.assertEqual([e['position'] for e in epoch['entries'] if e['status'] != 'supported'],
                                 [43, 75, 82, 89, 140, 147, 186])

    def test_candidate_primitivity_and_unknowns_remain_distinct(self):
        candidate = self.data['candidate']
        for divisor in [1, 2, 4, 8, 13, 16, 26, 52, 104]:
            self.assertTrue(any(candidate[i] != candidate[i % divisor] for i in range(208)))
        self.assertEqual(self.data['epochs']['r344']['strict'].count('?'), 9)
        self.assertEqual(self.data['epochs']['r347']['strict'].count('?'), 7)
        self.assertEqual(Counter(candidate), {'R': 62, 'Y': 62, 'B': 84})

    def test_exact_allowlist_and_bounded_size(self):
        actual = {p.relative_to(self.output).as_posix() for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(build.catalog()) | {'.nojekyll'})
        self.assertLess(self.size, 20 * 1024 * 1024)
        self.assertTrue(all(not p.startswith(('photo2/', '.git/')) for p in actual))

    def test_new_unselected_file_cannot_enter_publication(self):
        with tempfile.NamedTemporaryFile(dir=ROOT / 'site', suffix='.txt') as stray:
            stray.write(b'unselected research or private data'); stray.flush()
            files = build.expected_files()
            self.assertNotIn('site/' + Path(stray.name).name, files)

    def test_stray_or_corrupt_output_is_rejected(self):
        path = self.output / 'unexpected.txt'
        path.write_text('not public')
        try:
            with self.assertRaises(ValueError):
                build.check(self.output)
        finally:
            path.unlink()

    def test_copied_evidence_and_local_targets(self):
        build.provenance_check()
        build.check_links(self.output)
        self.assertNotIn('<!-- PATTERN_VIEWER -->', self.html)
        self.assertIn('id="pattern-data"', self.html)
        self.assertIn('lang="en"', self.html)
        self.assertIn('name="viewport"', self.html)

    def test_svg_membership_and_boundaries_are_explicit(self):
        beads = [attrs for _, attrs in self.doc.elements if attrs.get('class') == 'bead']
        self.assertEqual(len(beads), 984)
        selected = [b for b in beads if b['data-chosen'] == 'true']
        self.assertEqual(sorted(int(b['data-k']) for b in selected), list(range(208)))
        self.assertEqual(sum('tabindex' in b for b in beads), 208)
        sides = [a['data-boundary'] for _, a in self.doc.elements if 'data-boundary' in a]
        self.assertEqual(sides, ['left', 'right', 'START', 'END'])
        self.assertNotIn('fetch(', (ROOT / 'site/app.js').read_text())

    def test_historical_demo_and_missing_movie_notice(self):
        for name in ['beads.html', 'bead-links.html', 'beads.pov', 'ie.css', 'nn.js']:
            self.assertEqual((self.output / name).read_bytes(), (ROOT / name).read_bytes())
        old = (ROOT / 'simulated-beads.html').read_text()
        published = (self.output / 'simulated-beads.html').read_text()
        self.assertEqual(published, old.replace('href="beads.mp4"', 'href="legacy-movie.html"'))
        self.assertTrue((self.output / 'legacy-movie.html').is_file())

    def test_markdown_local_targets(self):
        for page in [ROOT / 'README.md', *ROOT.glob('docs/**/*.md')]:
            text = re.sub(r'```.*?```', '', page.read_text(), flags=re.S)
            for target in re.findall(r'\]\(([^\s)]+)\)', text):
                if re.match(r'\w+://|mailto:|#', target):
                    continue
                self.assertTrue((page.parent / target.split('#')[0]).exists(), (page, target))


if __name__ == '__main__':
    unittest.main()
