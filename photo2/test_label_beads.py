import errno
import json
import subprocess
from io import BytesIO
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image
import label_beads
from label_beads import AnnotationError, LabelStore, SaveConflict, make_server, open_browser, start_server


class StartupTests(unittest.TestCase):
    def test_busy_default_uses_a_free_port_but_explicit_port_is_honored(self):
        occupied = make_server(None, port=0)
        self.addCleanup(occupied.server_close)
        with patch.object(label_beads, 'DEFAULT_PORT', occupied.server_port):
            server = start_server(None)
            self.addCleanup(server.server_close)
            self.assertNotEqual(server.server_port, occupied.server_port)
            with self.assertRaises(OSError) as error:
                start_server(None, occupied.server_port)
            self.assertEqual(error.exception.errno, errno.EADDRINUSE)
            automatic = start_server(None, 0)
            self.addCleanup(automatic.server_close)
            self.assertGreater(automatic.server_port, 0)

    def test_other_bind_errors_do_not_trigger_port_fallback(self):
        with patch.object(label_beads, 'make_server', side_effect=PermissionError(errno.EACCES, 'denied')) as bind:
            with self.assertRaises(PermissionError): start_server(None)
            self.assertEqual(bind.call_count, 1)

    def test_wsl_uses_windows_launcher_without_running_it_in_tests(self):
        url = 'http://127.0.0.1:4000/'
        find = lambda name: '/mock/powershell.exe' if name == 'powershell.exe' else None
        with patch.object(label_beads.sys, 'platform', 'linux'), \
             patch.object(label_beads.platform, 'release', return_value='6.18-microsoft-standard-WSL2'), \
             patch.object(label_beads.shutil, 'which', side_effect=find), \
             patch.object(label_beads.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as run, \
             patch.object(label_beads.webbrowser, 'open') as browser:
            self.assertTrue(open_browser(url))
            self.assertEqual(run.call_args.args[0], ['/mock/powershell.exe', '-NoProfile', '-NonInteractive', '-Command', 'Start-Process', url])
            browser.assert_not_called()
            run.return_value = SimpleNamespace(returncode=1)
            self.assertFalse(open_browser(url))
            run.side_effect = OSError('Windows interop unavailable')
            self.assertFalse(open_browser(url))

    def test_missing_launchers_return_manual_fallback_without_xdg_open(self):
        with patch.object(label_beads.sys, 'platform', 'linux'), \
             patch.object(label_beads.shutil, 'which', return_value=None), \
             patch.dict(label_beads.os.environ, {}, clear=True), \
             patch.object(label_beads.webbrowser, 'open') as browser, \
             patch.object(label_beads.subprocess, 'run') as run:
            for kernel in ['6.18-microsoft-standard-WSL2', '6.18-generic']:
                with patch.object(label_beads.platform, 'release', return_value=kernel):
                    self.assertFalse(open_browser('http://127.0.0.1:4000/'))
            browser.assert_not_called()
            run.assert_not_called()

    def test_wslview_failure_or_timeout_tries_windows_browser(self):
        with patch.object(label_beads.sys, 'platform', 'linux'), \
             patch.object(label_beads.platform, 'release', return_value='microsoft-WSL2'), \
             patch.object(label_beads.shutil, 'which', side_effect=lambda name: '/mock/' + name), \
             patch.object(label_beads.subprocess, 'run') as run:
            for failure in [SimpleNamespace(returncode=1), subprocess.TimeoutExpired('wslview', 5)]:
                run.reset_mock()
                run.side_effect = [failure, SimpleNamespace(returncode=0)]
                self.assertTrue(open_browser('http://127.0.0.1:4000/'))
                self.assertEqual(run.call_args_list[0].args[0][0], '/mock/wslview')
                self.assertEqual(run.call_args_list[1].args[0][0], '/mock/powershell.exe')


class LabelStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / 'photo.png'
        im = Image.new('RGB', (100, 80))
        im.putpixel((23, 34), (17, 91, 203)); im.save(self.image)
        self.path = self.root / 'annotations.json'
        self.store = LabelStore(self.image, (20, 30, 60, 70), self.path)
        self.marker = dict(id='stable-marker', x=23.5, y=34.25, number=11, label_dx=6, label_dy=-6)

    def test_raw_crop_and_original_coordinates_survive_reload(self):
        im = Image.open(BytesIO(self.store.png))
        self.assertEqual(im.size, (40, 40)); self.assertEqual(im.getpixel((3, 4)), (17, 91, 203))
        saved = self.store.save(dict(revision=0, annotations=[self.marker]))
        reopened = LabelStore(self.image, (0, 0, 100, 80), self.path)
        self.assertEqual(reopened.read()['annotations'], saved['annotations'])
        self.assertEqual(reopened.read()['source']['oriented_size'], [100, 80])

    def test_stale_tab_cannot_overwrite_or_erase_another_save(self):
        self.store.save(dict(revision=0, annotations=[self.marker]))
        before = self.path.read_bytes()
        with self.assertRaises(SaveConflict): self.store.save(dict(revision=0, annotations=[]))
        self.assertEqual(before, self.path.read_bytes())
        self.store.save(dict(revision=1, annotations=[]))
        previous = json.loads((self.root / 'annotations.previous.json').read_text())
        self.assertEqual(previous['annotations'][0]['id'], self.marker['id'])
        self.assertEqual(previous['annotations'][0]['number'], self.marker['number'])

    def test_invalid_annotations_and_changed_source_preserve_saved_file(self):
        self.store.save(dict(revision=0, annotations=[self.marker])); before = self.path.read_bytes()
        for bad in [[self.marker, self.marker], [dict(self.marker, x=float('nan'))],
                    [dict(self.marker, y=80)], [dict(self.marker, number='7')]]:
            with self.assertRaises(AnnotationError): self.store.save(dict(revision=1, annotations=bad))
            self.assertEqual(before, self.path.read_bytes())
        Image.new('RGB', (100, 80), 'white').save(self.image)
        with self.assertRaises(AnnotationError): LabelStore(self.image, None, self.path)
        self.assertEqual(before, self.path.read_bytes())

    def test_ordered_series_and_renumbering_survive_reload(self):
        second = dict(self.marker, id='second', number=27, x=40)
        active = dict(id='s1', direction='d3', status='active', bead_ids=[second['id'], self.marker['id']])
        saved = self.store.save(dict(revision=0, annotations=[self.marker, second], series=[active]))
        self.assertEqual(saved['series'][0]['bead_ids'], ['second', 'stable-marker'])
        changed = [dict(self.marker, number=-5), second]
        finished = dict(active, status='complete')
        self.store.save(dict(revision=1, annotations=changed, series=[finished]))
        reopened = LabelStore(self.image, None, self.path).read()
        self.assertEqual(reopened['series'], [finished])
        self.assertEqual(reopened['annotations'][0]['number'], -5)
        self.assertIn('counterclockwise', reopened['direction_definitions']['d3'])

    def test_invalid_series_and_duplicate_numbers_cannot_damage_saved_work(self):
        second = dict(self.marker, id='second', number=27)
        annotations = [self.marker, second]
        valid = dict(id='s1', direction='d2', status='complete', bead_ids=['stable-marker', 'second'])
        self.store.save(dict(revision=0, annotations=annotations, series=[valid]))
        before = self.path.read_bytes()
        bad_series = [[dict(valid, bead_ids=['stable-marker', 'missing'])],
                      [dict(valid, bead_ids=['stable-marker'])],
                      [dict(valid, bead_ids=['second', 'second'])],
                      [dict(valid, direction='d4')], [dict(valid, direction=[])],
                      [valid, valid],
                      [dict(valid, status='active'), dict(valid, id='s2', status='active')]]
        for series in bad_series:
            with self.assertRaises(AnnotationError):
                self.store.save(dict(revision=1, annotations=annotations, series=series))
            self.assertEqual(before, self.path.read_bytes())
        for number in [11, True, 1.5, 9007199254740992]:
            with self.assertRaises(AnnotationError):
                self.store.save(dict(revision=1, annotations=[self.marker, dict(second, number=number)]))
            self.assertEqual(before, self.path.read_bytes())
        with self.assertRaises(AnnotationError):
            self.store.save(dict(revision=1, annotations=[second], series=[valid]))
        self.assertEqual(before, self.path.read_bytes())

    def test_crop_uses_exif_oriented_dimensions_and_pixels(self):
        file = self.root / 'oriented.jpg'
        im = Image.new('RGB', (80, 40), 'red'); exif = Image.Exif(); exif[274] = 6
        im.save(file, exif=exif)
        store = LabelStore(file, (0, 0, 40, 80), self.path)
        self.assertEqual(store.size, (40, 80))
        with self.assertRaises(AnnotationError): LabelStore(file, (0, 0, 80, 40), self.path)

    def test_source_cannot_be_used_as_annotation_or_backup_file(self):
        source = self.root / 'annotations.previous.json'
        source.write_bytes(self.image.read_bytes())
        with self.assertRaises(AnnotationError): LabelStore(source, None, self.path)
        with self.assertRaises(AnnotationError): LabelStore(self.image, None, self.image)


class HTTPIntegrationTests(unittest.TestCase):
    def test_real_http_image_save_reload_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d); image = path / 'photo.png'; annotations = path / 'data.json'
            Image.new('RGB', (25, 20), 'red').save(image)
            store = LabelStore(image, (2, 3, 22, 18), annotations)
            server = make_server(store, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                base = f'http://127.0.0.1:{server.server_port}'
                with urlopen(base + '/') as response: self.assertIn(b'Bead labeler', response.read())
                with urlopen(base + '/api/config') as response: config = json.load(response)
                self.assertEqual(config['crop'], [2, 3, 22, 18])
                with urlopen(base + '/image.png') as response: raw = Image.open(BytesIO(response.read()))
                self.assertEqual(raw.size, (20, 15))
                payload=dict(revision=0, annotations=[dict(id='m1', x=4.5, y=7.25, number=7), dict(id='m2', x=9, y=8, number=12)],
                             series=[dict(id='series1', direction='d2', status='complete', bead_ids=['m2','m1'])])
                request=Request(base+'/api/annotations',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
                with urlopen(request) as response: self.assertEqual(json.load(response)['revision'],1)
                with self.assertRaises(HTTPError) as error: urlopen(request)
                self.assertEqual(error.exception.code,409)
                with urlopen(base+'/api/annotations') as response: doc=json.load(response)
                self.assertEqual(doc['annotations'][0]['x'],4.5);self.assertEqual(doc['annotations'][0]['number'],7)
                self.assertEqual(doc['series'][0]['bead_ids'], ['m2', 'm1'])
                foreign=Request(base+'/api/annotations',data=json.dumps(dict(payload,revision=1)).encode(),headers={'Content-Type':'application/json','Origin':'http://other.invalid'},method='POST')
                with self.assertRaises(HTTPError) as error: urlopen(foreign)
                self.assertEqual(error.exception.code,403)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)


if __name__ == '__main__': unittest.main()
