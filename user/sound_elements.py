from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from scipy.signal import firwin, lfilter


class SoundR:
    def __init__(self):
        try:
            device = self.getDevice()
        except Exception as e:
            print(f"❌ Error in sound device detection: {e}")
            device = 1  # fallback device index

        sd.default.device = 'dx3'

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
soundVec1 = pureToneGen(0.4, 14000, 1800)
soundVec2 = pureToneGen(0.4, 4000, 1)
soundVec3 = pureToneGen(0.4, 4000, 1)

soundVec4 = pureToneGen(1.0, 250.0, 1)
soundVec5 = pureToneGen(0.4, 500.0, 1)
