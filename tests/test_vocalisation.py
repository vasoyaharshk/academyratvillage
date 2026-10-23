"""Run with: python -m unittest discover -s tests -p test_vocalisation.py"""
import csv
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest

import soundfile as sf

ACADEMY = Path(__file__).resolve().parents[1] / 'academy'
spec = importlib.util.spec_from_file_location('vocalisation_test_module', ACADEMY / 'vocalisation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VocalisationTests(unittest.TestCase):
    def test_simulated_audio_and_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            name = 'astrid_Touch_Demotivation-2-0_20261023-050950_Vocals'
            command = [sys.executable, str(ACADEMY / 'pettersson_recorder.py'),
                       '--simulate', '--duration', '2', '--segment-seconds', '1',
                       '--output', directory, '--session-name', name]
            subprocess.run(command, check=True, capture_output=True)
            info = sf.info(str(Path(directory) / (name + '.flac')))
            self.assertEqual((info.samplerate, info.channels, info.frames), (384000, 1, 768000))
            self.assertEqual(info.subtype, 'PCM_16')
            with open(Path(directory) / (name + '_bouts.csv')) as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 3)
            for row, hz in zip(rows, [22000, 40000, 50000]):
                self.assertLess(abs(float(row['peak_frequency_hz']) - hz), 100)
            with open(Path(directory) / (name + '.csv')) as stream:
                self.assertTrue(list(csv.DictReader(stream)))
            self.assertEqual(len(list(Path(directory).glob('*.flac'))), 1)
            original = (Path(directory) / (name + '.flac')).read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(original, (Path(directory) / (name + '.flac')).read_bytes())

    def test_disabled_does_not_touch_filesystem(self):
        recorder = module.VocalisationRecorder()
        recorder.start(SimpleNamespace(), None, None)
        self.assertIsNone(recorder.process)

    def test_stalled_microphone_stops_and_closes_flac(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            fake = folder / 'arecord'
            fake.write_text('#!' + sys.executable + '\nimport os, sys, time\n'
                            'if "-l" in sys.argv:\n'
                            ' print("card 2: Ultr [Pettersson M500], device 0: USB Audio")\n'
                            'else:\n'
                            ' os.write(1, b"\\x00\\x00" * 38400)\n'
                            ' time.sleep(30)\n')
            fake.chmod(0o755)
            old_path = os.environ['PATH']
            os.environ['PATH'] = directory + os.pathsep + old_path
            recorder = module.VocalisationRecorder()
            try:
                settings = SimpleNamespace(VOCALISATION_ENABLED=True,
                                           VOCALISATION_DIRECTORY=folder / 'output')
                task = SimpleNamespace(task='Touch_Demotivation', stage=2.0, substage=0)
                recorder.start(settings, task, 'astrid')
                process = recorder.process
                deadline = time.monotonic() + 10
                while not list((folder / 'output').glob('*.flac')):
                    self.assertIsNone(process.poll())
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(.05)
                time.sleep(.2)
                start = time.monotonic()
                recorder.stop()
                self.assertLess(time.monotonic() - start, 3)
                self.assertEqual(process.returncode, 0)
                audio = next((folder / 'output').glob('*.flac'))
                self.assertEqual(sf.info(str(audio)).frames, 38400)
                self.assertTrue(audio.name.startswith('astrid_Touch_Demotivation-2-0_'))
                # Restart immediately: both sessions must survive.
                recorder.start(settings, task, 'astrid')
                time.sleep(1)
                recorder.stop()
                self.assertEqual(len(list((folder / 'output').glob('*.flac'))), 2)
            finally:
                recorder.stop()
                os.environ['PATH'] = old_path


if __name__ == '__main__':
    unittest.main()
