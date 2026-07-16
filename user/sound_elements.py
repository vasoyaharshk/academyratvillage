from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from scipy.signal import firwin, lfilter
import os
import json


DEFAULT_FS = 48000
CB_FS = 192000 # or 192000 if that’s your device limit. This is essential for the high tones. # high rate for ultrasonic part
DEFAULT_RAMP_DURATION = 0.01  # 10 ms
REFERENCE_DB = 97.7          # Measured SPL reference

# ------------------ Babyface Pro FS multichannel SoundR ------------------
N_BABYFACE_OUT = 12
ULTRA_CH_INDEX = 0      # CH1 ultrasonic
NORMAL_L_CH_INDEX = 2   # CH3 normal
NORMAL_R_CH_INDEX = 3   # CH4 normal
CROSSOVER_HZ = 10000    #

# -------------------------------------------------------------
# SPL calibration loading (from spl_calibration.json)
# -------------------------------------------------------------
CALIBRATION_FILE = "spl_calibration.json"

FREQ_GAIN = {}

calib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CALIBRATION_FILE)

try:
    with open(calib_path, "r", encoding="utf-8") as f:
        _calib_raw = json.load(f)
    # JSON structure: { "freq_str": { "measured_db": ..., "gain": ... }, ... }
    FREQ_GAIN = {
        str(k): float(v.get("gain", 1.0))
        for k, v in _calib_raw.items()
    }
    print(f"[sound_elements] Loaded SPL calibration for {len(FREQ_GAIN)} freqs from {calib_path}")
except FileNotFoundError:
    print(f"[sound_elements] No {CALIBRATION_FILE} found, using unity gain.")
except Exception as e:
    print(f"[sound_elements] Error loading {CALIBRATION_FILE}: {e}. Using unity gain.")

def apply_calibration_gain(tone: np.ndarray, freq: float) -> np.ndarray:
    """
    Multiply tone by precomputed gain for this frequency, if available.
    freq must match what was used in calibration_standalone (same float value).
    """
    key = str(float(freq))
    gain = FREQ_GAIN.get(key, 1.0)
    if gain != 1.0:
        tone = tone * gain
    return tone.astype(np.float32)


class SoundR:
    def __init__(self):
        devices = sd.query_devices()
        self.device_index = None
        self.n_out = None

        # first try Babyface Pro FS
        for idx, dev in enumerate(devices):
            if "babyface" in dev["name"].lower():
                self.device_index = idx
                self.n_out = dev["max_output_channels"]
                print(f"Using Babyface Pro FS, device index {idx}, channels {self.n_out}")
                break

        # if no Babyface, try UACDemoV1.0
        if self.device_index is None:
            for idx, dev in enumerate(devices):
                if "uacdemo" in dev["name"].lower():
                    self.device_index = idx
                    self.n_out = 2
                    print(f"Babyface not found. Using UACDemoV1.0, device index {idx}, channels 2")
                    break

        # if still nothing, error
        if self.device_index is None:
            raise RuntimeError("No Babyface Pro FS or UACDemoV1.0 audio device found.")

    def route_to_channels(self, soundVec, freq=None):
        """
        Take a 1-D mono vector and route it into a multichannel buffer
        according to freq and Babyface channel layout.
        """
        out = np.zeros((len(soundVec), self.n_out), dtype=np.float32)

        if self.n_out >= 4:
            if freq is not None and freq > CROSSOVER_HZ:
                out[:, ULTRA_CH_INDEX] = soundVec
            else:
                out[:, NORMAL_L_CH_INDEX] = soundVec
                out[:, NORMAL_R_CH_INDEX] = soundVec
        else:  # 2-channel fallback mode
            out[:, 0] = soundVec
            out[:, 1] = soundVec

        return out.astype(np.float32)

    def play(self, soundVec, FsOut=DEFAULT_FS, freq=None):
        """
        If soundVec is already multichannel with correct width, send it as-is.
        Otherwise, treat it as mono and route it.
        """
        # If soundVec is 2-D and already matches the output channel count,
        # avoid rebuilding the multichannel buffer.
        if isinstance(soundVec, np.ndarray) and soundVec.ndim == 2 and soundVec.shape[1] == self.n_out:
            out = soundVec
        else:
            # assume mono 1-D and route
            out = self.route_to_channels(soundVec, freq=freq)

        sd.play(out, samplerate=FsOut, device=self.device_index)

    def stop(self):
        sd.stop()

    # Function to set the reference db:
    def play_amp1(self, freq, duration=1.0, FsOut=DEFAULT_FS):
        tone = pureToneGen_amp1(freq, duration, FsOut=FsOut)
        self.play(tone, FsOut=FsOut, freq=freq)

    @staticmethod
    def _create_sound_vec(v1, v2):
        sound = np.array([v1, v2])
        return np.ascontiguousarray(sound.T, dtype=np.float32)


def pureToneGen(amp, freq, toneDuration, FsOut=DEFAULT_FS):
    if isinstance(amp, float) and isinstance(freq, (float, int)):
        tvec = np.linspace(0, toneDuration, int(toneDuration * FsOut), endpoint=False)
        return amp * np.sin(2 * np.pi * freq * tvec)
    else:
        raise ValueError('pureToneGen needs (float, float|int) as arguments')

def db_to_amplitude(db, reference_db=REFERENCE_DB):
    return 10 ** ((db - reference_db) / 20)

def apply_cosine_ramp(sound, ramp_duration=DEFAULT_RAMP_DURATION, FsOut=DEFAULT_FS):
    ramp_len = int(FsOut * ramp_duration)
    ramp = 0.5 * (1 - np.cos(np.pi * np.arange(ramp_len) / ramp_len))
    sound[:ramp_len] *= ramp
    sound[-ramp_len:] *= ramp[::-1]
    return sound

def pureToneGen_dB(freq, duration, db=70, FsOut=DEFAULT_FS):
    amp = db_to_amplitude(db)
    tvec = np.linspace(0, duration, int(duration * FsOut), endpoint=False)
    tone = amp * np.sin(2 * np.pi * freq * tvec)
    return apply_cosine_ramp(tone, FsOut=FsOut).astype(np.float32)

def whiteNoiseGen(amp, band_fs_bot, band_fs_top, duration, FsOut=DEFAULT_FS, Fn=10000, randgen=None):
    if randgen is None:
        randgen = np.random

    if isinstance(amp, float) and isinstance(band_fs_bot, int) and isinstance(band_fs_top, int) and band_fs_bot < band_fs_top:
        white_noise = amp * randgen.normal(0, 1, size=int(FsOut * (duration + 1)))
        band_pass = firwin(Fn, [band_fs_bot / (FsOut * 0.5), band_fs_top / (FsOut * 0.5)], pass_zero=False)
        band_noise = lfilter(band_pass, 1, white_noise)
        return band_noise[FsOut:int(FsOut * (duration + 1))]
    else:
        raise ValueError('whiteNoiseGen needs (float, int, int, num) as arguments')


class FakeSoundR:
    def __init__(self):
        self.name = 'fake'

    def playSound(self):
        pass

    def stopSound(self):
        pass

    def load(self, v1=None, v2=None):
        pass

    def finalStop(self):
        pass

    def play(self):
        pass


class FakeSoundVec:
    def __init__(self):
        self.name = 'fake'


soundStream = SoundR()
#soundVec1 = pureToneGen(0.4, 14000, 1800)
#soundVec2 = pureToneGen(0.4, 4000, 1)
#soundVec3 = pureToneGen(0.4, 4000, 1)

base_1368 = pureToneGen_dB(1368.5, 1, 70, FsOut=DEFAULT_FS)
soundVec2 = apply_calibration_gain(base_1368, 1368.5)
soundVec3 = apply_calibration_gain(base_1368, 1368.5)

# Frequency definitions (Hz) per subject
reward_frequency_map = {
    'astrid': 250.0,
    'boira': 290.0,
    'claire': 336.4,
    'elaanor': 390.2,
    'erza': 452.7,
    'jessie': 525.1,
    'kora': 609.1,
    'mona': 706.6,
    'nana': 819.6,
    'rebeca': 950.7,
    'sakura': 1102.9,
    'wendy': 250.0,
    'xata': 525.1,
    'xochil': 1102.9,
    'm2': 100.0,
}

# Pre-generated tone vectors
rat_tones = {}
for name, freq in reward_frequency_map.items():
    # 1) generate mono tone at target dB
    base_tone = pureToneGen_dB(freq, 180, db=70, FsOut=DEFAULT_FS)
    # 2) apply calibration gain for this frequency
    calibrated = apply_calibration_gain(base_tone, freq)
    # 3) expand to multichannel ONCE using the routing logic
    rat_tones[name] = soundStream.route_to_channels(calibrated, freq=freq)

#Sound Testing:
def play_any_frequency(frequency, duration=1, db=70, FsOut=DEFAULT_FS):
    tone = pureToneGen_dB(frequency, duration, db, FsOut)
    tone = apply_calibration_gain(tone, frequency)
    soundStream.play(tone, FsOut=FsOut, freq=frequency)

#Function to set the reference db:
def pureToneGen_amp1(freq, duration, FsOut=DEFAULT_FS):
    tvec = np.linspace(0, duration, int(duration * FsOut), endpoint=False)
    tone = np.sin(2 * np.pi * freq * tvec).astype(np.float32)
    return apply_cosine_ramp(tone, FsOut=FsOut)

#Cognitive Bias Script:
# 4 pairs × (low_ref, probe25, probe50, probe75, high_ref)
cb_tones_hz = {
    1: [2000.0, 2320.0, 2691.0, 3122.0, 3621.0],
    2: [4573.0, 5305.0, 6154.0, 7138.0, 8281.0],
    3: [10458.0, 12131.0, 14072.0, 16323.0, 18935.0],
    4: [23913.0, 27739.0, 32177.0, 37326.0, 43298.0]
}

# Pre-generate 2s tones with ramp, calibrated and routed to channels once
cb_tones = {}
for pair, freqs in cb_tones_hz.items():
    tones = []
    for f in freqs:
        base_tone = pureToneGen_dB(f, 2.0, db=70, FsOut=CB_FS)
        calibrated = apply_calibration_gain(base_tone, f)
        # pre-spread to multichannel using the same routing logic
        routed = soundStream.route_to_channels(calibrated, freq=f)
        tones.append(routed)
    cb_tones[pair] = tones