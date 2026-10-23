#!/usr/bin/env python3
"""RatVillage - Pettersson M500-384 continuous FLAC recorder and live CSV analysis.

EDIT THE SETTINGS SECTION BELOW before running on Ubuntu.

Native microphone acquisition: 384,000 samples/s, mono, 16-bit signed PCM.
The program saves *all* captured audio, even when no call is detected.
CSV detections are acoustic activity candidates, NOT verified rat calls.
Measurements are dBFS (digital), NOT calibrated sound pressure (dB SPL).
The microphone has limited sensitivity below about 10 kHz; an additional
ordinary microphone is needed for comprehensive low-frequency audible calls.
"""

import argparse
import csv
import datetime as dt
import logging
import re
import shutil
import signal
import os
import select
import threading
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import soundfile as sf
from scipy.fft import rfft, rfftfreq

# ============================================================================
# USER SETTINGS - CHANGE THESE VALUES HERE (no command-line flags required)
# ============================================================================

# Main recording folder. Change this to any writable directory or mounted disk.
SAVE_DIRECTORY = Path("/home/ratvillage03/Important/Vocalisations")

# The ALSA card index may change after restarting Linux. Search by card name.
MICROPHONE_NAME = "Pettersson"
# Set to "hw:3,0" to use a fixed device, or None for automatic detection.
ALSA_DEVICE_OVERRIDE = None

TIMEZONE = "Europe/Madrid"
RECORDING_FILE_MINUTES = 60           # Each FLAC file covers this many minutes.
FREQUENCY_MIN_HZ = 1             # Pettersson's approximate lower usable end.
FREQUENCY_MAX_HZ = 160_000            # Pettersson's approximate upper usable end.
DETECTION_MIN_DBFS = -65.0            # Reduce (e.g. -75) for quieter signals.
DETECTION_MIN_PROMINENCE_DB = 18.0    # Peak relative to the frame spectral floor.
MINIMUM_ACTIVITY_MS = 10.0
MAXIMUM_SILENT_GAP_MS = 20.0
FFT_WINDOW_SAMPLES = 4096
FFT_HOP_SAMPLES = 2048
READ_BLOCK_MS = 100
RECONNECT_AFTER_SECONDS = 5.0

# Native acquisition format: DO NOT change unless using different hardware.
RATE = 384_000
BITS = 'S16_LE'
CHANNELS = 1
PCM_FULL_SCALE = 32768.0

# ============================================================================
# END OF USER SETTINGS
# ============================================================================


def get_devices():
    result = subprocess.run(['arecord', '-l'], capture_output=True, text=True, check=True)
    devices = []
    for ln in result.stdout.splitlines():
        m = re.search(r'^card\s+(\d+):.*?\[(.*?)\],\s+device\s+(\d+):', ln)
        if m:
            devices.append((f'hw:{m.group(1)},{m.group(3)}', m.group(2), ln.strip()))
    return devices


def resolve_device(name, explicit):
    if explicit:
        return explicit
    matches = [(d, label) for d, label, _ in get_devices() if name.casefold() in label.casefold()]
    if len(matches) != 1:
        description = '\n'.join(x[2] for x in get_devices()) or '(no devices listed)'
        raise RuntimeError(f'Expected exactly one ALSA recording device containing {name!r}; found {len(matches)}.\n{description}\n'
                           'Use --device hw:N,0 to specify a device explicitly.')
    logging.info('Selected %s (%s)', matches[0][0], matches[0][1])
    return matches[0][0]


class DailyCsv:
    def __init__(self, directory, name, header):
        self.directory, self.name, self.header = directory, name, header
        self.day, self.file, self.writer = None, None, None

    def write(self, when_local, row):
        date = when_local.strftime('%Y-%m-%d')
        if date != self.day:
            self.close()
            folder = self.directory / 'analysis' / date
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / self.name
            initial = not path.exists() or path.stat().st_size == 0
            self.file = open(path, 'a', newline='', buffering=1, encoding='utf-8')
            self.writer = csv.writer(self.file)
            if initial:
                self.writer.writerow(self.header)
            self.day = date
            logging.info('CSV: %s', path)
        self.writer.writerow(row)

    def close(self):
        if self.file:
            self.file.flush()
            self.file.close()
        self.day, self.file, self.writer = None, None, None


class SessionCsv:
    """Create even an empty session datasheet, including its header."""
    def __init__(self, directory, name, header):
        self.file = open(directory / name, 'x', newline='', buffering=1, encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(header)

    def write(self, when_local, row):
        self.writer.writerow(row)

    def close(self):
        self.file.close()


class Detector:
    def __init__(self, args, started_utc, peak_csv, bout_csv, tz):
        self.args, self.started, self.peak_csv, self.bout_csv, self.tz = args, started_utc, peak_csv, bout_csv, tz
        self.n = args.fft_size
        self.hop = args.hop_size
        self.window = np.hanning(self.n).astype(np.float32)
        self.scaling = self.window.sum() / 2 * PCM_FULL_SCALE
        hz = rfftfreq(self.n, 1 / RATE)
        self.indices = np.where((hz >= args.min_hz) & (hz <= args.max_hz))[0]
        if not len(self.indices):
            raise ValueError('Frequency band does not overlap the FFT bins')
        self.hz = hz
        self.pending = np.empty(0, dtype=np.int16)
        self.frame_sample = 0
        self.current_bout = None
        self.last_active_end = None
        self.chunk_best = None
        self.frames = 0
        self.bouts = 0

    def clock(self, sample):
        return self.started + dt.timedelta(seconds=sample / RATE)

    def time_strings(self, sample):
        utc = self.clock(sample)
        local = utc.astimezone(self.tz)
        return utc.isoformat(timespec='milliseconds'), local.isoformat(timespec='milliseconds'), local

    def analyse(self, pcm, chunk_index):
        self.pending = np.concatenate((self.pending, pcm))
        best = None
        while len(self.pending) >= self.n:
            sample = self.frame_sample
            frame = self.pending[:self.n].astype(np.float32)
            self.pending = self.pending[self.hop:]
            self.frame_sample += self.hop
            self.frames += 1
            spectrum = np.abs(rfft(frame * self.window)) / self.scaling
            band = spectrum[self.indices]
            imax = int(np.argmax(band))
            p = float(band[imax])
            floor = float(np.median(band))
            db = 20.0 * np.log10(max(p, 1e-12))
            snr = 20.0 * np.log10(max(p, 1e-12) / max(floor, 1e-12))
            bin_i = int(self.indices[imax])
            f = float(self.hz[bin_i])
            # Interpolate log-magnitude around strongest spectral bin.
            if 0 < bin_i < len(spectrum) - 1:
                a, b, c = np.log(np.maximum(spectrum[bin_i - 1:bin_i + 2], 1e-12))
                denom = a - 2 * b + c
                if abs(denom) > 1e-9:
                    delta = np.clip(0.5 * (a - c) / denom, -0.5, 0.5)
                    f += float(delta) * RATE / self.n
            active = db >= self.args.min_dbfs and snr >= self.args.min_snr_db
            if active:
                info = {'sample': sample, 'frequency': f, 'dbfs': db, 'snr': snr}
                if best is None or db > best['dbfs']:
                    best = info
                self.update_bout(info)
            else:
                self.maybe_end_bout(sample)
        if best is not None:
            utc_s, local_s, local = self.time_strings(best['sample'])
            self.peak_csv.write(local, [utc_s, local_s, chunk_index,
                                        f'{best["frequency"]:.1f}', f'{best["dbfs"]:.2f}',
                                        f'{best["snr"]:.2f}', 'candidate'])

    def update_bout(self, info):
        sample = info['sample']
        # A continuous bout can include brief gaps (default 20 ms).
        if self.current_bout and self.last_active_end is not None:
            if (sample - self.last_active_end) / RATE > self.args.max_gap_ms / 1000:
                self.finish_bout()
        if not self.current_bout:
            self.current_bout = {'first': sample, 'last': sample + self.n,
                                 'count': 0, 'max_dbfs': -999., 'freq_at_peak': 0.,
                                 'min_hz': float('inf'), 'max_hz': 0.}
        b = self.current_bout
        b['last'] = sample + self.n
        b['count'] += 1
        b['min_hz'] = min(b['min_hz'], info['frequency'])
        b['max_hz'] = max(b['max_hz'], info['frequency'])
        if info['dbfs'] > b['max_dbfs']:
            b['max_dbfs'] = info['dbfs']
            b['freq_at_peak'] = info['frequency']
        self.last_active_end = sample + self.n

    def maybe_end_bout(self, sample):
        if self.current_bout and self.last_active_end is not None:
            if (sample - self.last_active_end) / RATE > self.args.max_gap_ms / 1000:
                self.finish_bout()

    def finish_bout(self):
        b = self.current_bout
        if b:
            duration_ms = (b['last'] - b['first']) / RATE * 1000
            if duration_ms >= self.args.min_bout_ms:
                utc_start, local_start, local = self.time_strings(b['first'])
                utc_end, local_end, _ = self.time_strings(b['last'])
                self.bout_csv.write(local, [utc_start, local_start, utc_end, local_end,
                                            f'{duration_ms:.1f}', f'{b["freq_at_peak"]:.1f}',
                                            f'{b["min_hz"]:.1f}', f'{b["max_hz"]:.1f}',
                                            f'{b["max_dbfs"]:.2f}', b['count'], 'candidate'])
                self.bouts += 1
            self.current_bout = None
            self.last_active_end = None


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--session-name', help='Session basename; save one FLAC and session CSVs without rotation')
    p.add_argument('--watch-parent', action='store_true', help='Stop when parent closes stdin')
    p.add_argument('--list-devices', action='store_true', help='Show recording devices and exit')
    p.add_argument('--device-name', default=MICROPHONE_NAME, help='ALSA card label substring')
    p.add_argument('--device', default=ALSA_DEVICE_OVERRIDE, help='Override auto device detection, e.g. hw:3,0')
    p.add_argument('--output', type=Path, default=SAVE_DIRECTORY, help='Overrides SAVE_DIRECTORY in user settings')
    p.add_argument('--timezone', default=TIMEZONE)
    p.add_argument('--duration', type=float, default=0, help='Stop after this many seconds (0=continuous)')
    p.add_argument('--segment-seconds', type=int, default=RECORDING_FILE_MINUTES * 60, help='FLAC segment duration in seconds')
    p.add_argument('--min-hz', type=float, default=FREQUENCY_MIN_HZ)
    p.add_argument('--max-hz', type=float, default=FREQUENCY_MAX_HZ)
    p.add_argument('--min-dbfs', type=float, default=DETECTION_MIN_DBFS, help='Minimum FFT peak dBFS')
    p.add_argument('--min-snr-db', type=float, default=DETECTION_MIN_PROMINENCE_DB, help='Spectral peak above median bin noise level')
    p.add_argument('--min-bout-ms', type=float, default=MINIMUM_ACTIVITY_MS)
    p.add_argument('--max-gap-ms', type=float, default=MAXIMUM_SILENT_GAP_MS)
    p.add_argument('--fft-size', type=int, default=FFT_WINDOW_SAMPLES)
    p.add_argument('--hop-size', type=int, default=FFT_HOP_SAMPLES)
    p.add_argument('--chunk-ms', type=int, default=READ_BLOCK_MS)
    p.add_argument('--reconnect-seconds', type=float, default=RECONNECT_AFTER_SECONDS)
    p.add_argument('--simulate', action='store_true', help='Generate test ultrasonic tones instead of reading hardware')
    a = p.parse_args()
    if a.fft_size < 128 or a.hop_size <= 0 or a.hop_size > a.fft_size:
        p.error('Invalid FFT/window sizes')
    if not 0 <= a.min_hz < a.max_hz < RATE / 2:
        p.error('Choose a frequency band between 0 and 192000 Hz')
    if a.segment_seconds <= 0 or a.chunk_ms <= 0:
        p.error('Segment/chunk durations must be positive')
    return a


def read_exact(stream, count):
    pieces, left = [], count
    while left:
        data = stream.read(left)
        if not data:
            break
        pieces.append(data)
        left -= len(data)
    return b''.join(pieces)


def synthetic_blocks(samples_per_chunk, duration):
    count = int(duration * RATE) if duration else RATE * 2
    rng = np.random.default_rng(42)
    produced = 0
    while produced < count:
        n = min(samples_per_chunk, count - produced)
        t = (np.arange(n, dtype=np.float64) + produced) / RATE
        x = rng.normal(0, .00015, n)
        for start, end, freq in [(0.2, .35, 22_000), (.65, .82, 40_000), (1.25, 1.45, 50_000)]:
            mask = (t >= start) & (t < end)
            x[mask] += .045 * np.sin(2 * np.pi * freq * t[mask])
        yield np.round(np.clip(x, -1, 1 - 1 / 32768) * 32768).astype('<i2')
        produced += n


def capture(args, stop):
    tz = ZoneInfo(args.timezone)
    args.output.mkdir(parents=True, exist_ok=True)
    session = getattr(args, 'session_name', None)
    csv_type = SessionCsv if session else DailyCsv
    peak_csv = csv_type(args.output, session + '.csv' if session else 'frequency_peaks.csv',
                        ['timestamp_utc', 'timestamp_local', 'chunk_index', 'peak_frequency_hz',
                         'peak_amplitude_dbfs', 'spectral_prominence_db', 'classification'])
    bout_csv = csv_type(args.output, session + '_bouts.csv' if session else 'activity_bouts.csv',
                        ['start_utc', 'start_local', 'end_utc', 'end_local', 'duration_ms',
                         'peak_frequency_hz', 'min_peak_frequency_hz', 'max_peak_frequency_hz',
                         'peak_amplitude_dbfs', 'active_fft_frames', 'classification'])
    samples_per_chunk = int(round(RATE * args.chunk_ms / 1000))
    segment_samples = RATE * args.segment_seconds
    # Preserve real acquisition start time in file names; each segment is sample-accurate.
    started = dt.datetime.now(dt.timezone.utc)
    detector = Detector(args, started, peak_csv, bout_csv, tz)
    written = 0
    wav_file = None
    proc = None
    last_log = time.monotonic()
    segment_name = ''

    def open_segment(sample):
        nonlocal segment_name
        now = started + dt.timedelta(seconds=sample / RATE)
        local = now.astimezone(tz)
        folder = args.output if session else args.output / 'recordings' / local.strftime('%Y-%m-%d')
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f'Pettersson_{local.strftime("%Y-%m-%d_%H-%M-%S_%z")}_{sample // segment_samples:05d}.flac'
        if session:
            path = folder / (session + '.flac')
            if path.exists():
                raise FileExistsError(str(path))
        segment_name = str(path)
        logging.info('New FLAC: %s', path)
        return sf.SoundFile(str(path), mode='w', samplerate=RATE, channels=1,
                            format='FLAC', subtype='PCM_16')

    try:
        if args.simulate:
            duration = args.duration or 2
            blocks = synthetic_blocks(samples_per_chunk, duration)
        else:
            device = resolve_device(args.device_name, args.device)
            cmd = ['arecord', '-D', device, '-f', BITS, '-r', str(RATE), '-c', str(CHANNELS),
                   '-t', 'raw', '-q']
            logging.info('Recording with: %s', ' '.join(cmd))
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
            def live_blocks():
                pending = b''
                while not stop[0]:
                    if not select.select([proc.stdout], [], [], 0.1)[0]:
                        continue
                    data = os.read(proc.stdout.fileno(), samples_per_chunk * 2)
                    if not data:
                        break
                    pending += data
                    count = min(len(pending) // 2 * 2, samples_per_chunk * 2)
                    if count:
                        yield np.frombuffer(pending[:count], dtype='<i2')
                        pending = pending[count:]
            blocks = live_blocks()
        for pcm in blocks:
            if stop[0]:
                break
            if not len(pcm):
                continue
            offset = 0
            while offset < len(pcm):
                if wav_file is None:
                    wav_file = open_segment(written)
                room = len(pcm) if session else segment_samples - (written % segment_samples)
                part = pcm[offset: offset + room]
                wav_file.write(part)
                written += len(part)
                offset += len(part)
                if not session and written % segment_samples == 0:
                    wav_file.close()
                    wav_file = None
            detector.analyse(pcm, written // samples_per_chunk)
            if args.duration and written >= RATE * args.duration:
                break
            if time.monotonic() - last_log > 60:
                logging.info('Recorded %.1f min; candidates: %s; %s',
                             written / RATE / 60, detector.bouts, segment_name)
                last_log = time.monotonic()
        if proc is not None and proc.poll() is not None and not stop[0]:
            err = proc.stderr.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'Audio capture stopped unexpectedly: {err[-2000:]}')
    finally:
        if proc is not None:
            proc.terminate() if proc.poll() is None else None
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            proc.stdout.close()
            proc.stderr.close()
        detector.finish_bout()
        if wav_file is not None:
            wav_file.close()
        peak_csv.close()
        bout_csv.close()
        logging.info('Finished: %.2f seconds of recordings, %d activity bouts', written / RATE, detector.bouts)
    if not args.simulate and not stop[0] and args.duration == 0:
        raise RuntimeError('Capture ended unexpectedly; will attempt to reconnect')


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    if args.list_devices:
        for device, label, raw in get_devices():
            print(f'{device}: {label}\n  {raw}')
        return
    if not args.simulate and shutil.which('arecord') is None:
        raise RuntimeError('Install arecord: sudo apt install alsa-utils')
    stop = [False]
    def signal_handler(signum, frame):
        stop[0] = True
        logging.info('Shutting down at user request...')
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if args.watch_parent:
        def watch_parent():
            sys.stdin.buffer.read()
            stop[0] = True
        threading.Thread(target=watch_parent, daemon=True).start()
    while not stop[0]:
        try:
            capture(args, stop)
            return
        except (RuntimeError, OSError, sf.LibsndfileError) as e:
            logging.error('%s', e)
            if args.simulate or args.duration or args.session_name:
                raise
            logging.info('Trying again in %.1f seconds', args.reconnect_seconds)
            time.sleep(args.reconnect_seconds)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logging.error('Fatal error: %s', exc)
        sys.exit(1)
