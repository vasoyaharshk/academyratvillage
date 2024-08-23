import os
import time
from threading import Thread
import numpy as np
from numpy import linalg as ln
from academy.utils import utils
from user import settings
from academy.softcode import softcode
from academy import time_utils, queues, telegram_bot

try:
    import evdev
except:
    evdev = None


class Touch:

    def __init__(self, touch_device, only_x, first_touch, win_resolution, touch_resolution, pixels_per_mm):
        self.connected = True
        self.touch_device = touch_device
        self.win_resolution = win_resolution
        self.touch_resolution = touch_resolution
        self.pixels_per_mm = pixels_per_mm
        self.softcode = softcode
        self.only_x = None
        self.first_touch = first_touch
        self.timer = None
        self.time_between_responses = 0.5
        self.device = evdev.InputDevice(touch_device)
        self.device.grab()

    def close(self):
        self.device.ungrab()

    def start_reading(self, duration, x, y, correct_th, repoke_th):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run, args=(x, y, correct_th, repoke_th,), daemon=True)
        t.start()

    def resume_reading(self, x, y, correct_th, repoke_th):
        t = Thread(target=self.run, args=(x, y, correct_th, repoke_th,), daemon=True)
        t.start()

    def create_new_device(self):
        i = 0.001
        error_flag = True
        while i < 10:
            i *= 10
            try:
                os.system(settings.XINPUT)
                self.device.ungrab()
                self.device = evdev.InputDevice(self.touch_device)
                self.device.grab()
                i = 10
                utils.log('Academy', 'New device created', 'ACTION')
                error_flag = False
            except Exception:
                utils.log('Academy', 'touchscreen not found, waiting ' + str(i) + ' s', 'ERROR')
                time.sleep(i)
        if error_flag:
            telegram_bot.alarm_touchscreen(utils.subject_name)
            utils.task.tired = True
            utils.relaunch = True

    def run(self, x, y, correct_th, repoke_th):
        x_coord = None
        y_coord = None
        answer = None

        try:
            while self.device.read_one() is not None:  # clearing buffer of events
                pass
        except Exception:
            utils.log('Academy', 'lectureError in touchscreen clearing buffer, creating new device', 'ERROR')
            self.create_new_device()

        while self.timer.get_remaining_time() > 0:
            event = None
            try:
                event = self.device.read_one()
            except Exception:
                utils.log('Academy', 'lectureError in touchscreen, creating new device', 'ERROR')
                self.create_new_device()

            if event is not None:
                if event.type == evdev.ecodes.EV_ABS:  # if event is a coordinate
                    if event.code == 0 or event.code == 53:  # x coord
                        x_coord = event.value
                    if event.code == 1 or event.code == 54:  # y coord
                        y_coord = event.value
                    if self.first_touch and x_coord is not None and (y_coord is not None or self.only_x):
                        answer = [x_coord, y_coord]
                        break
                elif event.type == evdev.ecodes.EV_KEY and event.value != 1:  # BTN_TOUCH up
                    if not self.first_touch and x_coord is not None and (y_coord is not None or self.only_x):
                        answer = [x_coord, y_coord]
                        break

        if answer is None:
            self.softcode.send(3)
            response = []
        else:
            xpsy = abs(x)
            ypsy = 770  # y is now set to 770

            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            try:
                ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))
            except Exception:
                ytouch = None

            if self.only_x:
                if abs(xtouch - xpsy) < correct_th / 2:
                    self.softcode.send(1)
                elif abs(xtouch - xpsy) < repoke_th / 2:
                    self.softcode.send(2)
                else:
                    self.softcode.send(4)
            else:
                if ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))) < correct_th * 2:
                    self.softcode.send(1)
                elif ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))) < repoke_th * 2:
                    self.softcode.send(2)
                else:
                    self.softcode.send(4)

            if ytouch is None:
                ytouch = 0

            response = [xtouch / self.pixels_per_mm, ytouch / self.pixels_per_mm]

        queues.responses.put(response)


class FakeTouch:

    def __init__(self):
        self.connected = False

    def create_new_device(self):
        pass


try:
    touch = Touch(settings.TOUCHSCREEN_PORT, False, True, settings.WIN_RESOLUTION,
                 settings.TOUCH_RESOLUTION, settings.PIXELS_PER_MM)
except Exception:
    touch = FakeTouch()