"""Check registry repair preservation, idempotence, and refusal of unsafe inputs."""
from pathlib import Path
import os
import runpy
import subprocess
import sys
import tempfile
import unittest

MODULE = runpy.run_path(str(Path(__file__).with_name('repair-launcher-fonts.py')))
repair, FONTS, SECTION = (MODULE[name] for name in ('repair', 'FONTS', 'SECTION'))


class FontRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='eso-font-repair-test-')
        self.prefix = Path(self.temp.name)
        fonts = self.prefix / 'drive_c/windows/Fonts'
        fonts.mkdir(parents=True)
        for filename in FONTS.values():
            (fonts / filename).write_bytes(b'fixture-font-data')
        self.original = ('WINE REGISTRY Version 2\n#arch=win64\n\n' + SECTION + ' 123\n#time=abc\n"Existing"="keep.ttf"\n\n[Unrelated] 456\n"Value"="unchanged"\n').encode()
        (self.prefix / 'system.reg').write_bytes(self.original)

    def tearDown(self):
        self.temp.cleanup()

    def test_backup_preservation_and_idempotence(self):
        result = repair(self.prefix)
        self.assertEqual(Path(result['backup']).read_bytes(), self.original)
        after = (self.prefix / 'system.reg').read_text()
        self.assertIn('[Unrelated] 456\n"Value"="unchanged"', after)
        self.assertIn('"Existing"="keep.ttf"', after)
        for name, filename in FONTS.items():
            self.assertEqual(after.count('"' + name + '"="' + filename + '"'), 1)
        self.assertFalse(repair(self.prefix)['changed'])
        self.assertEqual(len(list(self.prefix.glob('system.reg.before-*'))), 1)

    def test_missing_font_leaves_registry_untouched(self):
        (self.prefix / 'drive_c/windows/Fonts/tahoma.ttf').unlink()
        with self.assertRaises(ValueError):
            repair(self.prefix)
        self.assertEqual((self.prefix / 'system.reg').read_bytes(), self.original)
        self.assertFalse(list(self.prefix.glob('system.reg.before-*')))

    def test_duplicate_section_is_rejected(self):
        data = self.original + (SECTION + '\n').encode()
        (self.prefix / 'system.reg').write_bytes(data)
        with self.assertRaises(ValueError):
            repair(self.prefix)
        self.assertEqual((self.prefix / 'system.reg').read_bytes(), data)

    def test_active_prefix_is_rejected(self):
        env = os.environ.copy()
        env['WINEPREFIX'] = str(self.prefix)
        child = subprocess.Popen([sys.executable, '-c', 'import time; print("ready", flush=True); time.sleep(15)'], env=env, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), 'ready')
            with self.assertRaises(ValueError):
                repair(self.prefix)
            self.assertEqual((self.prefix / 'system.reg').read_bytes(), self.original)
        finally:
            child.terminate()
            child.wait(timeout=5)
            child.stdout.close()


if __name__ == '__main__':
    unittest.main()
