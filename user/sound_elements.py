from multiprocessing import Process, Value
import sounddevice as sd
import numpy as np
import time
from threading import Thread
from timeit import default_timer as timer
from scipy.signal import firwin, lfilter  # filters


class SoundR:
    def __init__(self, sampleRate=44100, channelsOut=2, latency='low'):

        try:
            devices = self.getDevicesNamesAndNumbers()
            print(devices)
            device = devices["BPOD10"]
            print(device)
        except:
            device = 1
            print("1")

        sd.default.device = device
        sd.default.samplerate = sampleRate
        sd.default.latency = latency
        sd.default.channels = channelsOut

        self._Stream = sd.OutputStream(dtype='float32')
        self._Stream.close()
        self._sound = []
        self._playing = Value('i', 0)
        self._p = Process(target=self._play_sound_background)
        self._p.daemon = True

    @staticmethod
    def getDevices():
        return sd.query_devices()

    @staticmethod
    def getDevicesNamesAndNumbers():
        devi = sd.query_devices()

        idx = 0
        idxs = []

        for dev in devi:
            if dev['name'].startswith('Xonar DX: Multichannel'):
                idxs.append(idx)
            idx += 1

        idx = 0
        names = []

        with open('/proc/asound/cards') as file:
            line = file.readline()
            while line:
                if '[' in line and ']' in line:
                    try:
                        a = line.index('BPOD')
                        names.append(line[a:a+6])
                    except:
                        try:
                            a = line.index('bpod')
                            names.append(line[a:a + 6])
                        except:
                            pass
                    idx += 1
                line = file.readline()

        return dict(zip(names, idxs))

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

    def stopSound(self):
        try:
            if self._playing.value == 1:
                self._playing.value = 2
                self._Stream.close()
                self._p.terminate()
                print('SoundR: Stop.')
            elif self._playing.value == 0:
                self._playing.value = 2
        except AttributeError:
            print('SoundR: it is not possible to stop. No process is running.')

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

    if type(amp) is float and isinstance(band_fs_top, int) and isinstance(band_fs_bot,
                                                                          int) and band_fs_bot < band_fs_top:
        band_fs = [band_fs_bot, band_fs_top]
        white_noise = amp * randgen.normal(mean, std, size=int(FsOut * (duration + 1)))
        band_pass = firwin(Fn, [band_fs[0] / (FsOut * 0.5), band_fs[1] / (FsOut * 0.5)], pass_zero=False)
        band_noise = lfilter(band_pass, 1, white_noise)
        s1 = band_noise[FsOut:int(FsOut * (duration + 1))]
        return s1  # use np.zeros(s1.size) to get equal-size empty vec.
    else:
        raise ValueError('whiteNoiseGen needs (float, int, int, num,) as arguments')

def envelope(coh, whitenoise, dur, nframes, samplingR=192000, variance=0.015, randomized=False, paired=True, LAmp=1.0,
             RAmp=1.0, oldbug=True, randgen=None):
    """
    coh: coherence from 0(left only)to 1(right). ! var < coh < (1-var). Else this wont work
    whitenoise: vec containing sound (not necessarily whitenoise)
    dur: total duration of the stimulus (secs)
    nframes: total frames in the whole stimulus
    samplingR: soundcard sampling rate (ie 96000). Need to match with EVERYTHING
    variance: fixed var
    randomized: shuffles noise vec
    paired: each instantaneous evidence is paired with its counterpart so their sum = 1
    randgen: np.random.RandomState instance to sample from
    returns: left noise vec, right noise vec, left coh stairs, right coh stairs [being them all 1d-arrays]
    """
    if randgen is None:
        randgen = np.random
    totpoints = dur * samplingR  # should be an integer
    if len(whitenoise) < totpoints:
        raise ValueError('whitenoise is shorter than expected')

    if randomized == True:
        svec = whitenoise[:int(totpoints)]
        svec = svec.reshape(int(len(svec) / 10), 10)
        randgen.shuffle(svec)
        svec = svec.flatten()
    else:
        svec = whitenoise[:int(totpoints)]
    modfreq = nframes / dur
    if oldbug: # when freq was doubled, maintaining it because of compatibility issues. #envs = #stairs*2
        modwave = 1 * np.sin(2 * np.pi * (modfreq) * np.arange(0, dur, step=1 / samplingR) + np.pi)
    else: # bug fixed, stairs paired with envelopes (#envs = #stairs)
        modwave = 0.5 * (np.sin(2 * np.pi * (modfreq) * np.arange(0, dur, step=1 / samplingR) - np.pi/2)+1)

    if coh < 0 or coh > 1:
        raise ValueError(f'{coh} is an invalid coherence, it must fall w/i range 0 ~ 1')

    elif coh == 0 or coh == 1:
        staircaseR = np.repeat(coh, dur * samplingR)
        staircaseL = staircaseR - 1
        Lout = staircaseL * svec * modwave * LAmp
        Rout = staircaseR * svec * modwave * RAmp
        return Lout, Rout, np.repeat(coh - 1, nframes), np.repeat(coh, nframes)
    elif coh <= (variance * 1.1) or coh >= 1 - variance * 1.1:
        raise ValueError('invalid coherence for given variance or viceversa (if coh!=0|1, 1.1*var<coh<1-var*1.1)')
    else:
        alpha = ((1 - coh) / variance - 1 / coh) * coh ** 2
        beta = alpha * (1 / coh - 1)
        stairs_envelopeR = randgen.beta(alpha, beta, size=nframes)
        staircaseR = np.repeat(stairs_envelopeR, int(totpoints / nframes))
        staircaseL = staircaseR - 1
        Rout = staircaseR * svec * modwave * RAmp
        if paired == False:
            stairs_envelopeL = randgen.beta(alpha, beta, size=nframes) - 1
            staircaseL = np.repeat(stairs_envelopeL, int(totpoints / nframes))
            Lout = staircaseL * svec * modwave * LAmp
            return Lout, Rout, stairs_envelopeL, stairs_envelopeR
        Lout = staircaseL * svec * modwave * LAmp
        return Lout, Rout, stairs_envelopeR - 1, stairs_envelopeR


class FakeSoundR:
    def __init__(self):
        self.name = 'fake'

class FakeSoundVec:
    def __init__(self):
        self.name = 'fake'

try:
    soundStream = SoundR(sampleRate=192000)
    soundVec = whiteNoiseGen(1.0, 2000, 20000, 0.5, FsOut=192000, Fn=10000)
    soundStream.load(soundVec)
except:
    soundStream = FakeSoundR()
    soundVec = FakeSoundVec()




