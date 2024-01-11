import serial
import os
from threading import Thread
from user import settings
from academy import time_utils
from academy.utils import utils


class Arduino:
    def __init__(self, address):
        self.t = None
        self.arduino = serial.Serial(address, 9600, timeout=0.5)
        self.connected = True
        self.t = Thread(target=self.read_tag, daemon=True)
        self.t.start()

    def read_tag(self):

        filepath = os.path.join(settings.DATA_DIRECTORY, 'arduino_inside_log.txt')
        filepath2 = os.path.join(settings.DATA_DIRECTORY, 'arduino_inside_log2.txt')

        with open(filepath) as f:
            for i, l in enumerate(f):
                pass

        if i > 50000:
            try:
                os.remove(filepath2)
            except:
                pass
            try:
                os.rename(filepath, filepath2)
            except:
                pass


        while True:
            tag = self.arduino.readline()
            try:
                tag = tag.decode('utf-8')
            except UnicodeDecodeError:
                tag = None

            try:
                if tag[0:2] == '16':
                    utils.control_serials += 1
                    with open(filepath, 'a') as f:
                        f.write(time_utils.now_string())
                        f.write(',')
                        f.write(str(tag))
            except:
                pass



class FakeArduino:
    def __init__(self):
        self.connected = False

try:
    arduino_inside = Arduino(address=settings.ARDUINO_INSIDE_SERIAL_PORT)
except:
    arduino_inside = FakeArduino()
