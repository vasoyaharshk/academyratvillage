from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time

from scipy.signal import firwin, lfilter  # filters


class SoundR:
    def __init__(self):
        try:
            device = self.getDevice()
        except:
            print("error in sound device detection")
            device = 1

        sd.default.device = device


    @staticmethod
    def getDevice():

        devi = sd.query_devices()
        result = 0
        idx = 0
        for dev in devi:
            if dev['name'].startswith('UACDemoV1.0') and dev['max_output_channels'] == 2:
                result = idx
                print(' External speaker found')
                break

            idx += 1
        return result



    def play(self, soundVec):
        #sd.play(soundVec, samplerate=44100)
        sd.play(soundVec, samplerate=44100)

    def stop(self):
        sd.stop()


def db_to_amplitude(db, reference_db=100):
    """Convert dB SPL to linear amplitude (RMS-based)"""
    return 10 ** ((db - reference_db) / 20)


def apply_cosine_ramp(sound, ramp_duration=0.01, FsOut=44100):
    """Apply 10 ms cosine on/off ramps to avoid clicks"""
    ramp_len = int(FsOut * ramp_duration)
    ramp = 0.5 * (1 - np.cos(np.pi * np.arange(ramp_len) / ramp_len))

    sound[:ramp_len] *= ramp
    sound[-ramp_len:] *= ramp[::-1]
    return sound


def pureToneGen(amp, freq, toneDuration, FsOut=44100):
    """Generate sine wave tone with cosine ramp gating"""
    if isinstance(amp, float) and isinstance(freq, (int, float)):
        tvec = np.linspace(0, toneDuration, int(toneDuration * FsOut), endpoint=False)
        s1 = amp * np.sin(2 * np.pi * freq * tvec)
        return apply_cosine_ramp(s1, ramp_duration=0.01, FsOut=FsOut).astype(np.float32)
    else:
        raise ValueError('pureToneGen needs (float, float, float) as arguments')


def generate_reward_sound(frequency=8000.0, duration=1.0, db=70, FsOut=44100):
    """Generate reward tone with specified frequency (Hz), duration (s), and volume (dB SPL)"""
    amp = db_to_amplitude(db)
    return pureToneGen(amp=amp, freq=frequency, toneDuration=duration, FsOut=FsOut)


def play_reward_sound(frequency=8000.0, duration=1.0, db=70):
    """Play a reward tone sound"""
    if isinstance(soundStream, SoundR):
        sound_vec = generate_reward_sound(frequency, duration, db)
        soundStream.play(sound_vec)


def whiteNoiseGen(db, band_fs_bot, band_fs_top, duration, FsOut=44100, Fn=1000, randgen=None):
    """Generate band-pass filtered white noise with 70 dB SPL and cosine ramp"""
    if randgen is None:
        randgen = np.random
    if not (isinstance(band_fs_bot, int) and isinstance(band_fs_top, int) and band_fs_bot < band_fs_top):
        raise ValueError('band_fs_bot must be < band_fs_top and both must be int')

    amp = db_to_amplitude(db)
    noise_len = int(FsOut * (duration + 1))
    raw_noise = randgen.normal(0, 1, size=noise_len)
    band = firwin(Fn, [band_fs_bot / (FsOut * 0.5), band_fs_top / (FsOut * 0.5)], pass_zero=False)
    band_noise = lfilter(band, 1, raw_noise)

    s1 = band_noise[FsOut:int(FsOut * (duration + 1))]  # Remove 1 sec ramp-up
    s1 *= amp / np.sqrt(np.mean(s1**2))  # Normalize to target RMS
    return apply_cosine_ramp(s1[:int(FsOut * duration)], ramp_duration=0.01, FsOut=FsOut).astype(np.float32)


class FakeSoundR:
    def __init__(self):
        self.name = 'fake'

    def play(self, *args, **kwargs):
        pass

    def stop(self):
        pass


class FakeSoundVec:
    def __init__(self):
        self.name = 'fake'


try:
    soundStream = SoundR()
except:
    print("______\nERROR SOUND\n_______")
    soundStream = FakeSoundR()
