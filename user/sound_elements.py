from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from scipy.signal import firwin, lfilter

DEFAULT_FS = 44800
#DEFAULT_FS = 384000  # or 192000 if that’s your device limit. This is essential for the high tones.
DEFAULT_RAMP_DURATION = 0.01  # 10 ms
REFERENCE_DB = 85.8           # Measured SPL reference

class SoundR:
    def __init__(self):
        try:
            device = self.getDevice()
        except Exception as e:
            print(f"❌ Error in sound device detection: {e}")
            device = 1  # fallback device index

        #sd.default.device = 'dx3'
        sd.default.device = 'UACDemoV1.0'

    @staticmethod
    def list_devices():
        print("\n🔊 Available audio output devices:")
        for idx, dev in enumerate(sd.query_devices()):
            print(f"{idx}: {dev['name']} | max_output_channels = {dev['max_output_channels']}")

    @staticmethod
    # def getDevice():
        # SoundR.list_devices()
        # for idx, dev in enumerate(sd.query_devices()):
        #     name = dev.get('name', '').lower()
        #     max_out = dev.get('max_output_channels', 0)
        #     if "dx3" in name and "analog" in name and max_out >= 2:
        #         print(f"✅ External speaker found: {name} (index {idx})")
        #         return idx
        # raise RuntimeError("❌ DX3 Pro+ (Analog Output) not found in audio devices.")

    def getDevice():
        return 'dx3'

    def play(self, soundVec):
        sd.play(soundVec)

    def stop(self):
        sd.stop()

    @staticmethod
    def _create_sound_vec(v1, v2):
        sound = np.array([v1, v2])
        return np.ascontiguousarray(sound.T, dtype=np.float32)


def pureToneGen(amp, freq, toneDuration, FsOut=44800):
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

def whiteNoiseGen(amp, band_fs_bot, band_fs_top, duration, FsOut=44800, Fn=10000, randgen=None):
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

soundVec2 = pureToneGen_dB(1368.5, 1, 70)
soundVec3 = pureToneGen_dB(1368.5, 1, 70)

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
    'm3': 100.5,
}

# Pre-generated tone vectors
rat_tones = {name: pureToneGen_dB(freq, 1800, db=70) for name, freq in reward_frequency_map.items()}

#Sound Testing:
def play_any_frequency(frequency, duration=1, db=70, FsOut=DEFAULT_FS):
    tone = pureToneGen_dB(frequency, duration, db, FsOut)
    soundStream.play(tone)


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
    cb_tones[pair] = [pureToneGen_dB(f, 2.0, db=70, FsOut=DEFAULT_FS) for f in freqs]