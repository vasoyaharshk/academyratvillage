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
        sd.play(soundVec)

    def stop(self, soundVec):
       sd.stop()

    @staticmethod
    def _create_sound_vec(v1, v2):
        sound = np.array([v1, v2])  # left and right channel
        return np.ascontiguousarray(sound.T, dtype=np.float32)



def pureToneGen(amp, freq, toneDuration, FsOut=44800):
    """generates a given parameters pure tone vector. Gen counterpart using np.empty(s1.shape[?])
    pureToneGen(amp, freq, toneDuration, FsOut=192000):
    """
    if type(amp) is float and type(freq) is int:
        tvec = np.linspace(0, toneDuration, toneDuration * FsOut)
        s1 = amp * np.sin(2 * np.pi * freq * tvec)
        return s1
    else:
        raise ValueError('pureToneGen needs (float, int) as arguments')



def whiteNoiseGen(amp, band_fs_bot, band_fs_top, duration, FsOut=44800, Fn=10000, randgen=None):
    """whiteNoiseGen(amp, band_fs_bot, band_fs_top):
    beware this is not actually whitenoise
    amp: float, amplitude
    band_fs_bot: int, bottom freq of the band
    band_fs_top: int, top freq
    duration: secs
    FsOut: SoundCard samplingrate to use (192k, 96k, 48k...)
    Fn: filter len, def 10k
    *** if this takes too long try shortening Fn or using a lower FsOut ***
    adding some values here. Not meant to change them usually.
    randgen: np.random.RandomState instance to sample from

    returns: sound vector (np.array)
    """

    mean = 0
    std = 1
    if randgen is None:
        randgen = np.random

    if type(amp) is float and isinstance(band_fs_top, int) and isinstance(band_fs_bot, int) and band_fs_bot < band_fs_top:

        band_fs = [band_fs_bot, band_fs_top]
        white_noise = amp * randgen.normal(mean, std, size=int(FsOut * (duration + 1)))
        band_pass = firwin(Fn, [band_fs[0] / (FsOut * 0.5), band_fs[1] / (FsOut * 0.5)], pass_zero=False)
        band_noise = lfilter(band_pass, 1, white_noise)
        s1 = band_noise[FsOut:int(FsOut * (duration + 1))]
        return s1  # use np.zeros(s1.size) to get equal-size empty vec.
    else:
        raise ValueError('whiteNoiseGen needs (float, int, int, num,) as arguments')




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


try:
    soundStream = SoundR()
    #soundVec1 = whiteNoiseGen(1.0, 2000, 20000, 0.2, FsOut=44800, Fn=1000)
    #soundVec2 = whiteNoiseGen(1.0, 2000, 20000, 1, FsOut=44800, Fn=1000)

    soundVec1 = pureToneGen(0.4, 14000, 1800) #16000
    soundVec2 = pureToneGen(0.4, 4000, 1) #4000  #Incorrect sound
    soundVec3 = pureToneGen(0.4, 4000, 1)  # 4000  #Punish sound plays only for 1 second

except:
    print("______")
    print("ERROR SOUND")
    print("_______")
    soundStream = FakeSoundR()
    soundVec1 = FakeSoundVec()
    soundVec2 = FakeSoundVec()
    soundVec3 = FakeSoundVec()


