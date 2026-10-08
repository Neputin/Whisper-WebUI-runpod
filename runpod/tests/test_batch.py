import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
from batch import transcribe_batch

class Model:
    def transcribe(self, source, **kwargs):
        def segments():
            yield SimpleNamespace(text=' Zażółć gęślą jaźń. ')
            if 'broken' in source:
                raise ValueError('bad audio')
            yield SimpleNamespace(text=' Second line. ')
        return segments(), None

class ExportTests(unittest.TestCase):
    def test_duplicate_names_unicode_and_partial_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            archive, files, status = transcribe_batch(
                ['/one/audio.mp3', '/two/audio.wav', '/broken.mp3'], Model(), folder)
            self.assertEqual(len(files), 2)
            self.assertIn('2/3', status)
            self.assertFalse(list(Path(folder).rglob('*.partial')))
            with ZipFile(archive) as bundle:
                self.assertEqual(bundle.namelist(), ['0001_audio.txt', '0002_audio.txt', 'ERRORS.txt'])
                self.assertEqual(bundle.read('0001_audio.txt').decode(), 'Zażółć gęślą jaźń.\nSecond line.\n')
    def test_separate_jobs_and_empty_input(self):
        with tempfile.TemporaryDirectory() as folder:
            a, _, _ = transcribe_batch(['/same.mp3'], Model(), folder)
            b, _, _ = transcribe_batch(['/same.mp3'], Model(), folder)
            self.assertNotEqual(a, b)
            self.assertTrue(Path(a).exists())
            with self.assertRaises(ValueError):
                transcribe_batch([], Model(), folder)

if __name__ == '__main__':
    unittest.main()
