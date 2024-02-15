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
        self._Stream = sd.OutputStream(dtype='float32')
        self._Stream.close()
        self._sound = []
        self._playing = Value('i', 0)
        self._p = Process(target=self._play_sound_background)
        self._p.daemon = True

    @staticmethod
    def getDevice():

        devi = sd.query_devices()
        result = 0
        idx = 0
        for dev in devi:
            if dev['name'].startswith('front') and dev['max_output_channels'] == 2:
                result = idx
                print('found')
                break

            idx += 1
        print('found', devi[result])
        return result

    def load(self, v1, v2=None):

        """ Load audio """
        if v2 is None:
            v2 = v1
        if len(v1) != len(v2):
            raise ValueError('SoundR: The length of the vectors v1 and v2 has be the same.')
        try:
            self.stopSound()

        except AttributeError:
            pass

        sound = self._create_sound_vec(v1, v2)
        self._Stream.close()
        self._Stream = sd.OutputStream(dtype='float32')
        self._Stream.start()
        self._sound = sound
        self._playing.value = 0
        self._p = Process(target=self._play_sound_background)
        self._p.daemon = True
        self._p.start()
        print('SoundR: Loaded.')

    def playSound(self):
        if self._sound == []:
            raise ValueError('SoundR: No sound loaded. Please, use the method load().')
        self._playing.value = 1

    def play(self, soundVec):
        sd.play(soundVec)

    def stopSound(self):
        self._playing.value = 2
        try:
            self._Stream.close()
            self._p.terminate()
            print('SoundR: Stop.')
        except:
            print('stop without play')

    def finalStop(self):
        print("-----finalstop-----")
        self.playSound()
        time.sleep(0.5)
        self.stopSound()

    def _play_sound_background(self):
        while True:

            if self._playing.value == 1:
                print('SoundR: Play.')
                if self._sound == []:
                    print('Error: no sound is loaded.')
                    self._playing.value = 2
                    break
                else:
                    self._Stream.write(self._sound)
                    self._playing.value = 2
                    break
            elif self._playing.value == 2:
                break

    @staticmethod
    def _create_sound_vec(v1, v2):
        sound = np.array([v1, v2])  # left and right channel
        return np.ascontiguousarray(sound.T, dtype=np.float32)


def whiteNoiseGen(amp, band_fs_bot, band_fs_top, duration, FsOut=192000, Fn=10000, randgen=None):
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
    soundVec1 = whiteNoiseGen(1.0, 2000, 20000, 0.2, FsOut=44100, Fn=1000)
    soundVec2 = whiteNoiseGen(1.0, 2000, 20000, 1, FsOut=44100, Fn=1000)

except:
    print("______")
    print("ERROR SOUND")
    print("_______")
    soundStream = FakeSoundR()
    soundVec1 = FakeSoundVec()
    soundVec2 = FakeSoundVec()


