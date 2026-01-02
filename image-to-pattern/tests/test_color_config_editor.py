import json
import os
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_TMP_CACHE = tempfile.mkdtemp()
os.environ.setdefault("MPLCONFIGDIR", _TMP_CACHE)
os.environ.setdefault("XDG_CACHE_HOME", _TMP_CACHE)

import color_config_editor as editor


class ColorConfigEditorTests(unittest.TestCase):
    def test_load_config_default(self):
        cfg = editor.load_config(Path("nonexistent.json"), "img.jpg")
        self.assertEqual(cfg["image_filename"], "img.jpg")
        self.assertEqual(cfg["colors"], [])

    def test_add_edit_delete_color(self):
        cfg = {"image_filename": "img.jpg", "colors": []}
        editor.add_color(cfg, "red", False)
        self.assertEqual(len(cfg["colors"]), 1)
        self.assertEqual(cfg["colors"][0]["name"], "red")
        self.assertFalse(cfg["colors"][0]["background"])

        editor.edit_color(cfg, 0, new_name="bg", new_bg=True)
        self.assertEqual(cfg["colors"][0]["name"], "bg")
        self.assertTrue(cfg["colors"][0]["background"])

        editor.delete_color(cfg, 0)
        self.assertEqual(cfg["colors"], [])

    def test_save_config_roundtrip(self):
        cfg = {"image_filename": "img.jpg", "colors": [{"name": "c1", "background": False, "rectangles": []}]}
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ.setdefault("MPLCONFIGDIR", tmpdir)
            os.environ.setdefault("XDG_CACHE_HOME", tmpdir)
            path = Path(tmpdir) / "cfg.json"
            editor.save_config(cfg, path)
            self.assertTrue(path.exists())
            with open(path, "r") as f:
                loaded = json.load(f)
            self.assertEqual(loaded, cfg)


if __name__ == "__main__":
    unittest.main()
