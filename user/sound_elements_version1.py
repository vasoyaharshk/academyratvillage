from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from user import settings
from scipy.signal import firwin, lfilter

# Constants
DEFAULT_FS = 48000               # Default audio sample rate (samples per second), standard for high-quality sound. Our speaker only works at 48000
DEFAULT_RAMP_DURATION = 0.01     # Duration (in seconds) of the cosine ramp used to avoid audio clicks (e.g. 10 ms fade-in/out)
REFERENCE_DB = 85.8               # Reference decibel level for converting dB SPL to linear amplitude. This was measured with Harsh's phone inside the box.
DEFAULT_FN = 1000                # Filter order (number of taps) for FIR band-pass filter used in white noise generation


# Core Sound Handling Class
class SoundR:
    def __init__(self):
        self.device_name = 'DX3 Pro+: USB Audio (hw:1,0)'
        self.device = self.get_device_by_name(self.device_name)
        self.fs = 48000  # USB DAC compatible sample rate
        if self.device is not None:
            sd.default.device = self.device
            sd.default.samplerate = self.fs
            print(f"✅ External speaker selected: {self.device_name}")
        else:
            raise RuntimeError(f"❌ Device '{self.device_name}' not found.")

    def get_device_by_name(self, name):
        for idx, dev in enumerate(sd.query_devices()):
            if dev['name'] == name and dev['max_output_channels'] > 0:
                print(f"✅ Found device: {dev['name']} (index {idx})")
                return idx
        print(f"❌ Device '{name}' not found in device list.")
        return None

    def play(self, sound_vec):
        sd.play(sound_vec, samplerate=self.fs, device=self.device)

    def stop(self):
        sd.stop()


# Safe Fallback
class FakeSoundR:
    def play(self, *args, **kwargs):
        pass

    def stop(self):
        pass


# Utilities
def db_to_amplitude(db, reference_db=REFERENCE_DB):
    pass
    # return 10 ** ((db - reference_db) / 20)


# def apply_cosine_ramp(sound, ramp_duration=DEFAULT_RAMP_DURATION, FsOut=DEFAULT_FS):
#     pass
#     # ramp_len = int(FsOut * ramp_duration)
#     # ramp = 0.5 * (1 - np.cos(np.pi * np.arange(ramp_len) / ramp_len))
#     # sound[:ramp_len] *= ramp
#     # sound[-ramp_len:] *= ramp[::-1]
#     # return sound


def pure_tone_gen(amp, freq, duration, FsOut=DEFAULT_FS):
    tvec = np.linspace(0, duration, int(duration * FsOut), endpoint=False)
    tone = amp * np.sin(2 * np.pi * freq * tvec)
    return tone.astype(np.float32)


def generate_reward_sound(frequency=10.0, duration=1.0, db=70, FsOut=DEFAULT_FS):
    #amp = db_to_amplitude(db)
    amp = 1
    return pure_tone_gen(amp, frequency, duration, FsOut)


def play_reward_sound(frequency=10.0, duration=1.0, db=70):
    print(sd.query_devices(1, 'output'))  # Optional: inspect device
    t = time.time()
    sound_vec = generate_reward_sound(frequency, duration, db, FsOut=soundStream.fs)
    # Print expected hardware+driver output latency
    # info = sd.query_devices(soundStream.device, 'output')
    # print("Expected latency (output):", info['default_high_output_latency'])
    # Measure time to call sd.play
    soundStream.play(sound_vec)
    print("Time to call soundStream.play():", time.time() - t)


def play_incorrect_sound(duration=1.0):
    freq = settings.INCORRECT_FREQ
    db = settings.INCORRECT_DB
    sound_vec = generate_reward_sound(freq, duration, db, FsOut=soundStream.fs)
    soundStream.play(sound_vec)


def white_noise_gen(db, band_fs_bot, band_fs_top, duration, FsOut=DEFAULT_FS, Fn=DEFAULT_FN, randgen=None):
    randgen = randgen or np.random
    if not (isinstance(band_fs_bot, int) and isinstance(band_fs_top, int) and band_fs_bot < band_fs_top):
        raise ValueError("band_fs_bot must be < band_fs_top and both must be int")

    amp = db_to_amplitude(db)
    noise_len = int(FsOut * (duration + 1))
    raw_noise = randgen.normal(0, 1, size=noise_len)
    band_filter = firwin(Fn, [band_fs_bot / (FsOut * 0.5), band_fs_top / (FsOut * 0.5)], pass_zero=False)
    filtered_noise = lfilter(band_filter, 1, raw_noise)

    signal = filtered_noise[FsOut:int(FsOut * (duration + 1))]
    signal *= amp / np.sqrt(np.mean(signal ** 2))
    return apply_cosine_ramp(signal[:int(FsOut * duration)], FsOut=FsOut).astype(np.float32)


# Initialization
try:
    soundStream = SoundR()
except Exception as e:
    print("ERROR: Failed to initialise SoundR. Falling back to FakeSoundR.")
    soundStream = FakeSoundR()
