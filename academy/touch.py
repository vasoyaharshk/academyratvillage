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
            ypsy = 750  # y set to 750

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

# #Commented sections:
# # Draw boundaries for the correct area:
# top_boundary_line = (110 * self.pixels_per_mm + height / 2)
# bottom_boundary_line = (110 * self.pixels_per_mm - height / 2)
#
# left_line_correct = Line(win=window, start=(left_boundary_correct, bottom_boundary_line),
#                          end=(left_boundary_correct, top_boundary_line), lineColor="green",
#                          lineWidth=2 * self.pixels_per_mm)
# right_line_correct = Line(win=window, start=(right_boundary_correct, bottom_boundary_line),
#                           end=(right_boundary_correct, top_boundary_line), lineColor="green",
#                           lineWidth=2 * self.pixels_per_mm)
# top_line_correct = Line(win=window, start=(left_boundary_correct, bottom_boundary_line),
#                         end=(right_boundary_correct, top_boundary_line), lineColor="green",
#                         lineWidth=2 * self.pixels_per_mm)
# bottom_line_correct = Line(win=window, start=(left_boundary_correct, bottom_boundary_line),
#                            end=(right_boundary_correct, top_boundary_line), lineColor="green",
#                            lineWidth=2 * self.pixels_per_mm)
#
# # Draw the correct area lines
# left_line_correct.draw()
# right_line_correct.draw()
# top_line_correct.draw()
# bottom_line_correct.draw()
#
#
# # Draw boundaries for the incorrect area
# left_line_incorrect = Line(win=window, start=(left_boundary_incorrect, bottom_boundary_line),
#                            end=(left_boundary_incorrect, top_boundary_line), lineColor="red",
#                            lineWidth=2 * self.pixels_per_mm)
# right_line_incorrect = Line(win=window, start=(right_boundary_incorrect, bottom_boundary_line),
#                             end=(right_boundary_incorrect, top_boundary_line), lineColor="red",
#                             lineWidth=2 * self.pixels_per_mm)
# top_line_incorrect = Line(win=window, start=(left_boundary_incorrect, bottom_boundary_line),
#                           end=(right_boundary_incorrect, top_boundary_line), lineColor="red",
#                           lineWidth=2 * self.pixels_per_mm)
# bottom_line_incorrect = Line(win=window, start=(left_boundary_incorrect, bottom_boundary_line),
#                              end=(right_boundary_incorrect, top_boundary_line), lineColor="red",
#                              lineWidth=2 * self.pixels_per_mm)
#
# # Draw the incorrect area lines
# left_line_incorrect.draw()
# right_line_incorrect.draw()
# top_line_incorrect.draw()
# bottom_line_incorrect.draw()
#
# window.flip()


# def start_reading_probability(self, duration, x_correct, x_incorrect, y, width, height):
#     self.timer = time_utils.Timer(duration)
#     t = Thread(target=self.run_probability, args=(x_correct, x_incorrect, y, width, height), daemon=True)
#     t.start()

# def resume_reading_probability(self, x_correct, x_incorrect, y, width, height):
#     t = Thread(target=self.run_probability, args=(x_correct, x_incorrect, y, width, height), daemon=True)
#     t.start()
#
# def run_probability(self, x_correct, x_incorrect, y, width, height):
#     x_coord = None
#     y_coord = None
#     answer = None
#     last_answer = None
#     #last_time = time.time()
#     debounce_threshold = 100   #Value of 9.9 is 1 mm vertically and 16.384 is 1 mm horizontally
#     #throttle_time = 0.5
#     print('x_correct in touch.py 1: ', x_correct)
#     print('x_incorrect in touch.py 1: ', x_incorrect)
#     print('y in touch.py1: ', y)
#     print('width in touch.py1: ', width)
#     print('height in touch.py1: ', height)
#
#     # Ensure to clear old events
#     try:
#         while self.device.read_one() is not None:
#             pass
#     except Exception:
#         utils.log('Academy', 'Error in touchscreen clearing buffer, creating new device', 'ERROR')
#         self.create_new_device()
#
#     while self.timer.get_remaining_time() > 0:
#         event = None
#         try:
#             event = self.device.read_one()
#         except Exception:
#             utils.log('Academy', 'Error in touchscreen, creating new device', 'ERROR')
#             self.create_new_device()
    #
#         if event is not None:
#             # print(f"Event received: type={event.type}, code={event.code}, value={event.value}")
#
#             # Handle the touch start event (EV_KEY, BTN_TOUCH down)
#             if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_TOUCH and event.value == 1:
#                 # print("Touch started")
#                 self.touch_active = True  # Mark the touch as active
#                 continue  # Skip to the next event
#
#             # Handle touch coordinates when active
#             if event.type == evdev.ecodes.EV_ABS and self.touch_active:
#                 # print("Processing coordinate event (EV_ABS)")
#                 if event.code == 0 or event.code == 53:  # x coord
#                     x_coord = event.value
#                     # print(f"x_coord updated: {x_coord}")
#                 if event.code == 1 or event.code == 54:  # y coord
#                     y_coord = event.value
#                     # print(f"y_coord updated: {y_coord}")
#
#                 # Process coordinates when both x and y are available
#                 if x_coord is not None and y_coord is not None:
#                     answer = [x_coord, y_coord]
#                     # print(f"Touch detected - Answer: {answer}")
#
#                     # Debounce and throttle
#                     if last_answer is None or (
#                             abs(answer[0] - last_answer[0]) > debounce_threshold or
#                             abs(answer[1] - last_answer[1]) > debounce_threshold
#                     ):
#                         self.process_touch_probability(answer, x_correct, x_incorrect, y, width, height)
#                         last_answer = answer
#                     #     if time.time() - last_time > throttle_time:
#                     #         # print("Throttle passed - processing touch.")
#                     #         self.process_touch_probability(answer, x_correct, x_incorrect, y, width, height)
#                     #         last_answer = answer
#                     #         last_time = time.time()
#                     #     else:
#                     #         # print("Throttle blocked - not enough time since last event.")
#                     #         pass
    #     else:
#                         print("Debounce blocked - insignificant movement")
#                         pass
#
#             # Handle touch release (EV_KEY, BTN_TOUCH up)
#             elif event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_TOUCH and event.value == 0:
#                 # print("Touch released")
#                 self.touch_active = False  # Reset the touch state
#
#     queues.responses.put([])  # Default empty response at the end