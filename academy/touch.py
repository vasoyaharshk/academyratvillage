import os
import time
from threading import Thread
import numpy as np
from numpy import linalg as ln
from academy.utils import utils
from user import settings
from academy.softcode import softcode
from academy import time_utils, queues, telegram_bot
from psychopy.visual import Line
from user.psychopy_elements import window  # Use the pre-defined window from psychopy_elements

try:
    import evdev
except:
    evdev = None


class Touch:

    def __init__(self, touch_device, only_x, first_touch, win_resolution, touch_resolution, pixels_per_mm, pixels_per_mm_x, pixels_per_mm_y):
        self.connected = True
        self.touch_device = touch_device
        self.win_resolution = win_resolution
        self.touch_resolution = touch_resolution
        self.pixels_per_mm = pixels_per_mm
        self.pixels_per_mm_x = pixels_per_mm_x
        self.pixels_per_mm_y = pixels_per_mm_y
        self.softcode = softcode
        self.only_x = None
        self.first_touch = first_touch
        self.timer = None
        self.time_between_responses = 0.5
        self.device = evdev.InputDevice(touch_device)
        self.device.grab()

        #self.touch_active = False

    def close(self):
        self.device.ungrab()

    def start_reading(self, duration, x, y, correct_th, repoke_th):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run, args=(x, y, correct_th, repoke_th,), daemon=True)
        t.start()

    def resume_reading(self, x, y, correct_th, repoke_th):
        t = Thread(target=self.run, args=(x, y, correct_th, repoke_th,), daemon=True)
        t.start()

    def start_reading_wm_no_mask(self, duration, x, y, correct_th, repoke_th, x_incorrect1, x_incorrect2, width, height):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run_wm_no_mask, args=(x, y, correct_th, repoke_th, x_incorrect1, x_incorrect2, width, height), daemon=True)
        t.start()

    def resume_reading_wm_no_mask(self, x, y, correct_th, repoke_th, x_incorrect1, x_incorrect2, width, height):
        t = Thread(target=self.run_wm_no_mask, args=(x, y, correct_th, repoke_th, x_incorrect1, x_incorrect2, width, height), daemon=True)
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
            ypsy = 750  # y is now set to 770
            #ypsy = abs(y)  # y is now set to 770

            #print('Touch: ', answer)
            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            try:
                ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))
            except Exception:
                ytouch = None

            #print('X2: ', xtouch, 'Y2: ', ytouch)
            #print(correct_th)

            if self.only_x:
                if abs(xtouch - xpsy) < correct_th / 2:
                    self.softcode.send(1)
                elif abs(xtouch - xpsy) < repoke_th / 2:
                    self.softcode.send(2)
                else:
                    self.softcode.send(4)
            else:
                if ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))) < correct_th * 1:
                    #print('Formula Correct: ', ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))))
                    self.softcode.send(1)
                elif ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))) < repoke_th * 1:
                    #print('Formula Incorrect: ', ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))))
                    self.softcode.send(2)
                else:
                    self.softcode.send(4)

            if ytouch is None:
                ytouch = 0

            response = [xtouch / self.pixels_per_mm, ytouch / self.pixels_per_mm]

        queues.responses.put(response)

    def run_wm_no_mask(self, x, y, correct_th, repoke_th, x_incorrect1, x_incorrect2, width, height):
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
            xpsy_incorrect1 = abs(x_incorrect1)
            xpsy_incorrect2 = abs(x_incorrect2)

            ypsy = 750  # y is now set to 770
            #ypsy = abs(y)  # y is now set to 770

            #print('Touch: ', answer)
            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))
            #ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1])) - yz
            #print('X2: ', xtouch, 'Y2: ', ytouch)
            #print('Touch: Correct: ', xpsy, 'Incorrect1: ', xpsy_incorrect1, 'Incorrect2: ', xpsy_incorrect2, 'Correcth: ', correct_th, 'Repoketh: ', repoke_th)

            # Define boundaries for the correct rectangular area:
            top_boundary = (ypsy + height / 2)
            bottom_boundary = (ypsy - height / 2)

            # Define boundaries for the incorrect rectangular areas:
            left_boundary_incorrect1 = (xpsy_incorrect1 - width / 2)
            right_boundary_incorrect1 = (xpsy_incorrect1 + width / 2)
            left_boundary_incorrect2 = (xpsy_incorrect2 - width / 2)
            right_boundary_incorrect2 = (xpsy_incorrect2 + width / 2)

            #print('Correcth: ', correct_th, 'Repoketh: ', repoke_th)

            # Condition 1: Check if touch is in the correct area
            if ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))) < correct_th:
                #print('Formula Correct: ', ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))))
                self.softcode.send(1)
            # Condition 2: Repoke area in incorrect locations (only if correct_th != repoke_th and outside correct area)
            elif correct_th != repoke_th and (
                    (left_boundary_incorrect1 <= xtouch <= right_boundary_incorrect1 and bottom_boundary <= ytouch <= top_boundary) or
                    (left_boundary_incorrect2 <= xtouch <= right_boundary_incorrect2 and bottom_boundary <= ytouch <= top_boundary)
            ):
                #print('Touch is in the repoketh area')
                self.softcode.send(2)
            # Condition 3: Check if touch is in the incorrect areas (punish area)
            elif correct_th == repoke_th and (
                    (ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy_incorrect1, ypsy))) < correct_th) or
                     (ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy_incorrect2, ypsy))) < correct_th)
            ):
                #print('Formula Punish: ', ln.norm(np.array((xtouch, ytouch)) - np.array((xpsy, ypsy))))
                self.softcode.send(4)
            # Condition 4: If touch is outside the correct and incorrect areas
            else:
                #print('Formula Outside: ')
                self.softcode.send(5)


            if ytouch is None:
                ytouch = 0

            response = [xtouch / self.pixels_per_mm, ytouch / self.pixels_per_mm]

        queues.responses.put(response)


    def start_reading_probability_first_touch(self, duration, x_correct, x_incorrect, y, width, height):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run_probability_first_touch, args=(x_correct, x_incorrect, y, width, height), daemon=True)
        t.start()

    def run_probability_first_touch(self, x_correct, x_incorrect, y, width, height):
        x_coord = None
        y_coord = None
        answer = None
        #print("x_correct in touch.py 1: ", x_correct)
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
                        self.process_touch_probability(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break
                elif event.type == evdev.ecodes.EV_KEY and event.value != 1:  # BTN_TOUCH up
                    if not self.first_touch and x_coord is not None and (y_coord is not None or self.only_x):
                        answer = [x_coord, y_coord]
                        self.process_touch_probability(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break

    def process_touch_probability(self, answer, x_correct, x_incorrect, y, width, height):
        if answer is None:
            self.softcode.send(3)
            response = []
            print('No touch found')  # Debugging incorrect area touch
        else:
            #print('x_correct in touch.py 2: ', x_correct)
            #print('x_incorrect in touch.py 2: ', x_incorrect)
            #print('y in touch.py2: ', y)
            #print('width in touch.py2: ', width)
            #print('height in touch.py2: ', height)

            xpsy_correct = abs(x_correct)
            ypsy = 400  # y set to 750

            # Convert touch coordinates to the window coordinates
            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))

            #print(f'Touch Coordinates: {answer}')  # Debugging raw touch coordinates
            #print(f'Converted Touch (xtouch, ytouch): {xtouch}, {ytouch}')  # Debugging touch conversion

            # Define boundaries for the correct rectangular area:
            left_boundary_correct = (xpsy_correct - width / 2)
            right_boundary_correct = (xpsy_correct + width / 2)
            top_boundary = (ypsy + height / 2)
            bottom_boundary = (ypsy - height / 2)

            #print(f'Correct Area (x_correct, ypsy): {xpsy_correct}, {ypsy}')  # Debugging correct area
            #print(f'Correct Boundaries (left, right, top, bottom): {left_boundary_correct}, {right_boundary_correct}, {top_boundary}, {bottom_boundary}')  # Debugging correct area boundaries

            # Check if the touch is within the correct area
            if left_boundary_correct <= xtouch <= right_boundary_correct and bottom_boundary <= ytouch <= top_boundary:
                #print('Touch is in the correct area.')  # Debugging correct area touch
                self.softcode.send(1)
            elif x_incorrect is not None:
                xpsy_incorrect = abs(x_incorrect)
                left_boundary_incorrect = (xpsy_incorrect - width / 2)
                right_boundary_incorrect = (xpsy_incorrect + width / 2)

                #print(f'Incorrect Area (x_incorrect): {xpsy_incorrect}')  # Debugging incorrect area
                #print(f'Incorrect Boundaries (left, right): {left_boundary_incorrect}, {right_boundary_incorrect}')  # Debugging incorrect area boundaries

                # Check if the touch is in the incorrect area:
                if left_boundary_incorrect <= xtouch <= right_boundary_incorrect and bottom_boundary <= ytouch <= top_boundary:
                    #print('Touch is in the incorrect area.')  # Debugging incorrect area touch
                    self.softcode.send(4)
                else:
                    #print('Touch is outside both areas. Waiting for valid touch...')  # Debugging outside area touch
                    self.softcode.send(3)
            else:
                #print('Touch is outside both areas. Waiting for valid touch...')
                self.softcode.send(3)

            response = [xtouch / self.pixels_per_mm, ytouch / self.pixels_per_mm]
            # print(f'Response (xtouch, ytouch in mm): {response}')  # Debugging response
        queues.responses.put(response)


    def start_reading_probability_correction(self, duration, x_correct, x_incorrect, y, width, height):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run_probability_correction, args=(x_correct, x_incorrect, y, width, height), daemon=True)
        t.start()

    def run_probability_correction(self, x_correct, x_incorrect, y, width, height):
        x_coord = None
        y_coord = None
        answer = None
        #print("x_correct in touch.py 1: ", x_correct)
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
                        self.process_touch_probability_correction(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break
                elif event.type == evdev.ecodes.EV_KEY and event.value != 1:  # BTN_TOUCH up
                    if not self.first_touch and x_coord is not None and (y_coord is not None or self.only_x):
                        answer = [x_coord, y_coord]
                        self.process_touch_probability_correction(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break

    def process_touch_probability_correction(self, answer, x_correct, x_incorrect, y, width, height):
        if answer is None:
            self.softcode.send(3)
            response = []
            #print('No touch found')  # Debugging incorrect area touch
        else:
            #print('x_correct in touch.py 2: ', x_correct)
            #print('x_incorrect in touch.py 2: ', x_incorrect)
            #print('y in touch.py2: ', y)
            #print('width in touch.py2: ', width)
            #print('height in touch.py2: ', height)

            xpsy_correct = abs(x_correct)
            ypsy = 720  # y set to 750

            # Convert touch coordinates to the window coordinates
            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))

            #print(f'Touch Coordinates: {answer}')  # Debugging raw touch coordinates
            #print(f'Converted Touch (xtouch, ytouch): {xtouch}, {ytouch}')  # Debugging touch conversion

            # Define boundaries for the correct rectangular area:
            left_boundary_correct = (xpsy_correct - width / 2)
            right_boundary_correct = (xpsy_correct + width / 2)
            top_boundary = (ypsy + height / 2)
            bottom_boundary = (ypsy - height / 2)

            #print(f'Correct Area (x_correct, ypsy): {xpsy_correct}, {ypsy}')  # Debugging correct area
            #print(f'Correct Boundaries (left, right, top, bottom): {left_boundary_correct}, {right_boundary_correct}, {top_boundary}, {bottom_boundary}')  # Debugging correct area boundaries

            # Check if the touch is within the correct area
            if left_boundary_correct <= xtouch <= right_boundary_correct and bottom_boundary <= ytouch <= top_boundary:
                #print('Touch is in the correct area.')  # Debugging correct area touch
                self.softcode.send(1)
            elif x_incorrect is not None:
                xpsy_incorrect = abs(x_incorrect)
                left_boundary_incorrect = (xpsy_incorrect - width / 2)
                right_boundary_incorrect = (xpsy_incorrect + width / 2)

                #print(f'Incorrect Area (x_incorrect): {xpsy_incorrect}')  # Debugging incorrect area
                #print(f'Incorrect Boundaries (left, right): {left_boundary_incorrect}, {right_boundary_incorrect}')  # Debugging incorrect area boundaries

                # Check if the touch is in the incorrect area
                if left_boundary_incorrect <= xtouch <= right_boundary_incorrect and bottom_boundary <= ytouch <= top_boundary:
                    #print('Touch is in the incorrect area.')  # Debugging incorrect area touch
                    self.softcode.send(2)
                else:
                    #print('Touch is outside both areas. Waiting for valid touch...')  # Debugging outside area touch
                    self.softcode.send(3)
            else:
                #print('Touch is outside both areas. Waiting for valid touch...')
                self.softcode.send(3)

            response = [xtouch / self.pixels_per_mm, ytouch / self.pixels_per_mm]
            # print(f'Response (xtouch, ytouch in mm): {response}')  # Debugging response
        queues.responses.put(response)


#New function for Touchteaching and accurate touch positions on x and y axis:
    def start_reading_probability_touch_accurate(self, duration, x_correct, x_incorrect, y, width, height):
        self.timer = time_utils.Timer(duration)
        t = Thread(target=self.run_probability_touch_accurate, args=(x_correct, x_incorrect, y, width, height), daemon=True)
        t.start()

    def run_probability_touch_accurate(self, x_correct, x_incorrect, y, width, height):
        x_coord = None
        y_coord = None
        answer = None
        #print("x_correct in touch.py 1: ", x_correct)
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
                        self.process_touch_probability_accurate(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break
                elif event.type == evdev.ecodes.EV_KEY and event.value != 1:  # BTN_TOUCH up
                    if not self.first_touch and x_coord is not None and (y_coord is not None or self.only_x):
                        answer = [x_coord, y_coord]
                        self.process_touch_probability_accurate(answer, x_correct, x_incorrect, y, width,
                                                       height)  # Process touch event
                        break

    def process_touch_probability_accurate(self, answer, x_correct, x_incorrect, y, width, height):
        if answer is None:
            self.softcode.send(3)
            response = []
            print('No touch found')  # Debugging incorrect area touch
        else:
            # print('x_correct in touch.py 2: ', x_correct)
            # print('x_incorrect in touch.py 2: ', x_incorrect)
            # print('y in touch.py2: ', y)
            # print('width in touch.py2: ', width)
            # print('height in touch.py2: ', height)

            xpsy_correct = abs(x_correct)
            # ypsy = 750  # y is now set to 770
            ypsy = abs(y)  # y is now set to 770

            # Convert touch coordinates to the window coordinates
            # print('Touch: ', answer)
            xtouch = abs(answer[0] * (self.win_resolution[0] / self.touch_resolution[0]))
            ytouch = abs(answer[1] * (self.win_resolution[1] / self.touch_resolution[1]))

            # print(f'Touch Coordinates: {answer}')  # Debugging raw touch coordinates
            # print(f'Converted Touch (xtouch, ytouch): {xtouch}, {ytouch}')  # Debugging touch conversion

            # Define boundaries for the correct rectangular area:
            left_boundary_correct = (xpsy_correct - width / 2)
            right_boundary_correct = (xpsy_correct + width / 2)
            top_boundary = (ypsy + height / 2)
            bottom_boundary = (ypsy - height / 2)

            # print(f'Correct Area (x_correct, ypsy): {xpsy_correct}, {ypsy}')  # Debugging correct area
            # print(f'Correct Boundaries (left, right, top, bottom): {left_boundary_correct}, {right_boundary_correct}, {top_boundary}, {bottom_boundary}')  # Debugging correct area boundaries

            # Check if the touch is within the correct area
            if left_boundary_correct <= xtouch <= right_boundary_correct and bottom_boundary <= ytouch <= top_boundary:
                # print('Touch is in the correct area.')  # Debugging correct area touch
                self.softcode.send(1)
            elif x_incorrect is not None:
                xpsy_incorrect = abs(x_incorrect)
                left_boundary_incorrect = (xpsy_incorrect - width / 2)
                right_boundary_incorrect = (xpsy_incorrect + width / 2)

                # print(f'Incorrect Area (x_incorrect): {xpsy_incorrect}')  # Debugging incorrect area
                # print(f'Incorrect Boundaries (left, right): {left_boundary_incorrect}, {right_boundary_incorrect}')  # Debugging incorrect area boundaries

                # Check if the touch is in the incorrect area:
                if left_boundary_incorrect <= xtouch <= right_boundary_incorrect and bottom_boundary <= ytouch <= top_boundary:
                    # print('Touch is in the incorrect area.')  # Debugging incorrect area touch
                    self.softcode.send(4)
                else:
                    # print('Touch is outside both areas. Waiting for valid touch...')  # Debugging outside area touch
                    self.softcode.send(3)
            else:
                # print('Touch is outside both areas. Waiting for valid touch...')
                self.softcode.send(3)

            response = [xtouch / self.pixels_per_mm_x, ytouch / self.pixels_per_mm_y]
            # print(f'Response (xtouch, ytouch in mm): {response}')  # Debugging response
        queues.responses.put(response)


class FakeTouch:

    def __init__(self):
        self.connected = False

    def create_new_device(self):
        pass


try:
    touch = Touch(settings.TOUCHSCREEN_PORT, False, True, settings.WIN_RESOLUTION,
                 settings.TOUCH_RESOLUTION, settings.PIXELS_PER_MM, settings.PIXELS_PER_MM_X, settings.PIXELS_PER_MM_Y)
except Exception:
    touch = FakeTouch()