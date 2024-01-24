import serial
from threading import Thread
from academy import queues
from user import settings
from academy.utils import utils


class Arduino:
    def __init__(self, address):
        self.t = None
        self.arduino = serial.Serial(address, 9600, timeout=0.1)
        self.connected = True
        self.t = Thread(target=self.read_tag, daemon=True)
        self.t.start()

    def open_door1(self):
        self.arduino.write(b'0')

    def close_door1(self):
        self.arduino.write(b'1')

    def open_door2(self):
        self.arduino.write(b'2')

    def close_door2(self):
        self.arduino.write(b'3')

    def move_doors_to_go_to_box(self):
        self.arduino.write(b'4')

    def move_doors_to_go_home(self):
        self.arduino.write(b'5')

    def turn_led_on(self):
        self.arduino.write(b'6')

    def turn_led_off(self):
        self.arduino.write(b'7')

    def temp_and_scale(self):
        self.arduino.write(b'8')

    def get_temperature(self):
        self.arduino.write(b'9')

    def tare_scale(self):
        utils.log('Academy', 'Taring the scale', 'ACTION')
        self.arduino.write(b'a')

    def get_weight(self):
        self.arduino.write(b'b')

    def noise_door2(self):
        self.arduino.write(b'c')

    def read_tag(self):

        while True:
            tag = self.arduino.readline()
            try:
                tag = tag.decode('utf-8')
            except UnicodeDecodeError:
                tag = None

            if tag:
                if ':' in tag:
                    try:
                        position = tag.index(':')
                        weight = str(float(tag[position + 1:]))
                        value = 'w', weight
                        queues.tags.put(value)
                    except:
                        pass

                elif '*' in tag:
                    try:
                        position = tag.index('*')
                        weight = str(float(tag[position + 1:]))
                        value = 'p', weight
                        queues.tags.put(value)
                    except:
                        pass

                elif ';' in tag:
                    try:
                        position = tag.index(';')
                        temperature = tag[position + 1:]
                        value = 't', temperature
                        queues.tags.put(value)
                    except:
                        pass

                else:
                    value = 's', tag
                    if utils.reading_tags > 0:
                        queues.tags.put(value)




class FakeArduino:
    def __init__(self):
        self.connected = False

    def open_door1(self):
        pass

    def close_door1(self):
        pass

    def open_door2(self):
        pass

    def close_door2(self):
        pass

    def move_doors_to_go_to_box(self):
        pass

    def move_doors_to_go_home(self):
        pass

    def turn_led_on(self):
        pass

    def turn_led_off(self):
        pass

    def temp_and_scale(self):
        pass

    def get_temperature(self):
        pass

    def tare_scale(self):
        pass

    def get_weight(self):
        pass

try:
    arduino = Arduino(address=settings.ARDUINO_SERIAL_PORT)
except:
    arduino = FakeArduino()
