"""Session recorder controller; no audio dependencies in the Academy process."""
import atexit
import datetime
import logging
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


class VocalisationRecorder:
    def __init__(self):
        self.process = None
        self.log_file = None
        atexit.register(self.stop)

    def start(self, settings, task, subject_name):
        self.stop()
        if not getattr(settings, 'VOCALISATION_ENABLED', False):
            return
        try:
            # Snapshot metadata before task execution or stage progression.
            def safe(value):
                return re.sub(r'[^A-Za-z0-9_.-]+', '_', str(value))
            stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            name = '{}_{}-{}-{}_{}_Vocals'.format(
                safe(subject_name), safe(task.task), int(float(task.stage)),
                int(float(task.substage)), stamp)
            folder = Path(settings.VOCALISATION_DIRECTORY).expanduser()
            folder.mkdir(parents=True, exist_ok=True)
            # Never overwrite a previous recording, including very rapid restarts.
            base, suffix = name, 1
            while any((folder / (name + ext)).exists() for ext in
                      ('.flac', '.csv', '_bouts.csv', '.log')):
                name = '{}_{}'.format(base, suffix)
                suffix += 1
            self.log_file = open(folder / (name + '.log'), 'x', buffering=1)
            command = [sys.executable, str(Path(__file__).with_name('pettersson_recorder.py')),
                       '--output', str(folder), '--session-name', name, '--watch-parent',
                       '--device-name', getattr(settings, 'VOCALISATION_DEVICE_NAME', 'Pettersson'),
                       '--timezone', getattr(settings, 'VOCALISATION_TIMEZONE', 'Europe/Madrid')]
            device = getattr(settings, 'VOCALISATION_DEVICE', None)
            if device:
                command += ['--device', str(device)]
            # stdin ownership also stops capture if Academy crashes or is killed.
            # Execute the file directly: importing academy would run its startup code.
            self.process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                            stdout=self.log_file, stderr=self.log_file,
                                            start_new_session=True)
            logging.info('Vocalisations: %s', folder / name)
        except Exception:
            logging.exception('Could not start vocalisation recording')
            self.stop()

    def stop(self):
        proc, self.process = self.process, None
        try:
            if proc is not None:
                if proc.stdin:
                    proc.stdin.close()
                try:
                    code = proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        code = proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        code = proc.wait(timeout=2)
                if code:
                    logging.error('Vocalisation recorder exited with code %s; see session .log', code)
        except Exception:
            logging.exception('Could not stop vocalisation recorder')
        finally:
            if self.log_file:
                self.log_file.close()
                self.log_file = None


vocalisation = VocalisationRecorder()
