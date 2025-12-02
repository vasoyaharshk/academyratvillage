from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from scipy.signal import firwin, lfilter

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

class SoundR:
    def __init__(self):
        devices = sd.query_devices()
        self.device_index = None

        for idx, dev in enumerate(devices):
            if "babyface" in dev["name"].lower() and dev["max_output_channels"] >= N_BABYFACE_OUT:
                self.device_index = idx
                break

        if self.device_index is None:
            raise RuntimeError("Babyface Pro FS not found.")

        print(f"Using Babyface Pro FS device index {self.device_index}")

    def _blank(self, n_samples):
        return np.zeros((n_samples, N_BABYFACE_OUT), dtype=np.float32)

    def play(self, soundVec, FsOut=DEFAULT_FS, freq=None):
        # allow interface: detect freq based on tone length / ramp
        print("freq se: ", freq)
        n = len(soundVec)
        out = self._blank(n)

        if freq is not None and freq > CROSSOVER_HZ:        #Here is freq = None, then it will automatically go to normal speakers. Useful for punish sounds.
            out[:, ULTRA_CH_INDEX] = soundVec
        else:
            out[:, NORMAL_L_CH_INDEX] = soundVec
            out[:, NORMAL_R_CH_INDEX] = soundVec

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

soundVec2 = pureToneGen_dB(1368.5, 1, 70, FsOut=DEFAULT_FS)
soundVec3 = pureToneGen_dB(1368.5, 1, 70, FsOut=DEFAULT_FS)

# Frequency definitions (Hz) per subject
reward_frequency_map = {
    'chand': 250.0,
    'felix': 290.0,
    'fergus': 336.4,
    'geralt': 390.2,
    'joey': 452.7,
    'ross': 525.1,
    'innes': 609.1,
    'pol': 706.6,
    'm3': 200.0,
}

# Pre-generated tone vectors
rat_tones = {name: pureToneGen_dB(freq, 1800, db=70, FsOut=DEFAULT_FS) for name, freq in reward_frequency_map.items()}

#Sound Testing:
def play_any_frequency(frequency, duration=1, db=70, FsOut=DEFAULT_FS):
    tone = pureToneGen_dB(frequency, duration, db, FsOut)
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

# Pre-generate 2s tones with ramp
cb_tones = {}
for pair, freqs in cb_tones_hz.items():
    cb_tones[pair] = [pureToneGen_dB(f, 2.0, db=70, FsOut=CB_FS) for f in freqs]