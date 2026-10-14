"""Security-relevant launcher boundaries; no browser or outside writes."""
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name('beads-chromium-review')
launch = runpy.run_path(str(SOURCE))['invocation']


class LauncherTests(unittest.TestCase):
    def test_rejects_extra_arguments_and_other_modules(self):
        bad = [[], ['-c'], ['os'], ['photo2.r282.phase2'], ['photo2.r282.browser_check', '--help'],
               ['photo2.r282.browser_check;id'], ['photo2/r282/browser_check.py'],
               ['photo2.r282.browser_check\n'], ['photo2.r../../browser_check'],
               ['photo2.r２８２.browser_check'], ['photo2.r28.browser_check']]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError): launch(args)

    @patch('pathlib.Path.is_dir', return_value=True)
    def test_fixed_interpreter_module_and_environment(self, _):
        with patch.dict(os.environ, {'PYTHONPATH':'/tmp/untrusted', 'R282_OUTPUT':'/tmp/untrusted',
                                    'PLAYWRIGHT_BROWSERS_PATH':'/tmp/untrusted', 'NODE_OPTIONS':'--inspect'}, clear=False):
            cmd, env = launch(['photo2.r282.browser_check'])
        self.assertEqual(cmd[:3], ['/home/rharris/git/beads/.venv/bin/python', '-I', '-c'])
        self.assertEqual(cmd[-1], 'photo2.r282.browser_check')
        self.assertEqual(env['PLAYWRIGHT_BROWSERS_PATH'], '/home/rharris/.cache/beads-playwright')
        for key in ('PYTHONPATH','R282_OUTPUT','NODE_OPTIONS'):self.assertNotIn(key, env)

    def test_missing_future_module_rejected(self):
        with self.assertRaises(ValueError): launch(['photo2.r999999999.browser_check'])

    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('pathlib.Path.resolve', return_value=Path('/tmp/other/browser_check.py'))
    def test_symlink_escape_rejected(self, *_):
        with self.assertRaises(ValueError): launch(['photo2.r282.browser_check'])

    @patch('pathlib.Path.is_dir', return_value=False)
    def test_missing_cache_fails_closed(self, _):
        with self.assertRaises(ValueError): launch(['photo2.r282.browser_check'])


if __name__ == '__main__':unittest.main()
