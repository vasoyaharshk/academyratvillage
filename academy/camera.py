import cv2
import os
import numpy as np
import pandas as pd
from multiprocessing import Process, JoinableQueue, Value
from user import settings
from academy import time_utils


class FakeVideo:
    def __init__(self):
        self.connected = False
        self.tracking_inside = False

    def play(self):
        pass

    def put_state(self, something):
        pass

    def stop(self):
        pass


class Video(Process):
    def __init__(self, port='0', cam_number=0, name_video=None, path=None, width=None, height=None, fps=None,
                 codec_video='X264', cam_states=None, duration_video=1800, number_of_videos=50,
                 threshold=0, cage_zone=None, doors1_zone=None, doors2_zone=None,
                 floor1_zone=None, floor2_zone=None, tracking_position=False):

        Process.__init__(self)

        self.connected = True
        self.port = port
        self.cam_number = cam_number
        self.name_video = name_video
        self.width = width
        self.height = height
        self.fps = fps
        self.fourcc_out = cv2.VideoWriter_fourcc(*codec_video)
        self.cam_states = cam_states if cam_states is not None else {}
        self.duration_video = duration_video
        self.number_of_videos = number_of_videos
        self.threshold = threshold
        self.threshold2 = 0
        self.threshold3 = 0
        self.daily_threshold = False
        self.title = ''

        self.tracking_inside = doors1_zone is not None and doors2_zone is not None
        self.tracking_inside_floor = floor1_zone is not None and floor2_zone is not None
        self.tracking_position = tracking_position

        self.cage_zone = cage_zone if cage_zone is not None else [640, 0, 480, 0]
        self.doors1_zone = doors1_zone if doors1_zone is not None else [640, 0, 480, 0]
        self.doors2_zone = doors2_zone if doors2_zone is not None else [640, 0, 480, 0]
        self.floor1_zone = floor1_zone if floor1_zone is not None else [640, 0, 480, 0]
        self.floor2_zone = floor2_zone if floor2_zone is not None else [640, 0, 480, 0]


        self.image_queue = JoinableQueue(maxsize=1)
        self.recordV = ''
        self.frame = []
        self.frame_counter = 0
        self.timestamps = []
        self.frames = []
        self.states = []
        self.trials = []
        self.cxs = []
        self.cys = []

        self.cam_sync = {}
        self.list_states = []
        self.list_state_circle0 = []
        self.list_state_circle1 = []
        i = 0
        keys = sorted(self.cam_states)
        for key in keys:
            self.list_states.append(key)
            value = self.cam_states[key]
            self.list_state_circle0.append(value[0])
            self.list_state_circle1.append(value[1])

            self.cam_sync[key] = i
            i += 1

        self.command_queue = JoinableQueue()

        self.out_video = None
        self.ctime = None
        self.chrono = time_utils.Chrono()

        self.fps_now = 0
        self.fps_counter = 0
        self.last_sec = 0

        self.target = 10
        self.target_counter = 0

        self.state = ''
        self.previous_state = ''
        self.path = path
        self.path_video = os.path.join(path, name_video + '.avi')
        self.path_npz = os.path.join(path, name_video + '.npz')

        self.centers = {}

        self.area_cage = Value('i', 0)
        self.area_doors1 = Value('i', 0)
        self.area_doors2 = Value('i', 0)
        self.area_total = Value('i', 0)
        self.area_total_floor = Value('i', 0)

        self.next_time = time_utils.now_seconds() + self.duration_video

        self.video = None

        if self.cam_number == 1:
            self.active = True
        elif self.cam_number == 2:
            self.active = True
        else:
            self.active = False

        if not os.path.exists(self.port):
            raise

        self.trial_number = 0
        self.counter2 = [0, 0, 0, 0]
        self.cx = 0
        self.cy = 0

        self.create_mask_flag = True
        self.mask_mouse = None

    def put_state(self, state: str):
        self.command_queue.put(state)

    def play(self):
        self.start()

    def run(self):
        self.video = cv2.VideoCapture(self.port)

        if self.width is not None:
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height is not None:
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.fps is not None:
            self.video.set(cv2.CAP_PROP_FPS, self.fps)

        self.fps = int(self.video.get(cv2.CAP_PROP_FPS))
        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        self.out_video = cv2.VideoWriter(self.path_video, self.fourcc_out, self.fps, (self.width, self.height))

        self.chrono.reset()
        self.image_queue.put(self.frame)

        while True:
            if self.daily_threshold:

                begin_time = time_utils.hour_minute_to_time(settings.HOUR_DAY, settings.MINUTE_DAY)
                end_time = time_utils.hour_minute_to_time(settings.HOUR_NIGHT, settings.MINUTE_NIGHT)
                now = time_utils.now_time()

                if begin_time < end_time:
                    day = begin_time <= now <= end_time
                else:  # crosses midnight
                    day = now >= begin_time or now <= end_time
                if day:
                    self.threshold = settings.THRESHOLD_DAY_DOOR1
                    self.threshold2 = settings.THRESHOLD_DAY_CAGE
                    self.threshold3 = settings.THRESHOLD_DAY_DOOR2
                else:
                    self.threshold = settings.THRESHOLD_NIGHT_DOOR1
                    self.threshold2 = settings.THRESHOLD_NIGHT_CAGE
                    self.threshold3 = settings.THRESHOLD_NIGHT_DOOR2

            if not self.command_queue.empty():
                state = self.command_queue.get()
                try:
                    print(state)
                    self.trial_number = int(state)
                except:
                    pass
                if state == 'stop':
                    break
                elif state == 'day':
                    self.threshold = settings.THRESHOLD_DAY_DOOR1
                    self.threshold2 = settings.THRESHOLD_DAY_CAGE
                    self.threshold3 = settings.THRESHOLD_DAY_DOOR2
                    self.daily_threshold = False
                elif state == 'night':
                    self.threshold = settings.THRESHOLD_NIGHT_DOOR1
                    self.threshold2 = settings.THRESHOLD_NIGHT_CAGE
                    self.threshold3 = settings.THRESHOLD_NIGHT_DOOR2
                    self.daily_threshold = False
                elif state == 'daily':
                    self.daily_threshold = True
                elif state == 'black':
                    self.image_queue.put(np.zeros(self.frame.shape, np.uint8))
                elif state == 'active':
                    if not self.active:
                        self.frame_counter = 0
                        self.timestamps = []
                        self.frames = []
                        self.states = []
                        self.trials = []
                        self.cxs = []
                        self.cys = []
                        self.trial_number = 0
                        self.active = True
                        self.chrono.reset()
                        self.path_video = os.path.join(self.path, self.name_video + '.avi')
                        self.path_npz = os.path.join(self.path, self.name_video + '.npz')
                        self.path_csv = os.path.join(self.path, self.name_video + '.csv')
                        self.out_video = cv2.VideoWriter(self.path_video, self.fourcc_out,
                                                         self.fps, (self.width, self.height))
                elif state == 'inactive':
                    if self.active:
                        self.active = False
                        self.trial_number = 0
                        self.image_queue.put(np.zeros(self.frame.shape, np.uint8))
                        if self.cam_number == 1 or self.cam_number == 2:
                            self.save_video1or2()
                        elif self.cam_number == 3:
                            self.save_video3()
                elif state.startswith('File'):
                    if self.active:
                        if self.cam_number == 2:
                            self.save_video1or2()
                        elif self.cam_number == 3:
                            self.save_video3()
                    self.frame_counter = 0
                    self.timestamps = []
                    self.frames = []
                    self.states = []
                    self.trials = []
                    self.cxs = []
                    self.cys = []
                    self.trial_number = 0
                    self.active = True
                    self.chrono.reset()
                    name_video = state[4:]
                    path = os.path.join(self.path, name_video.split('_')[0])
                    if self.cam_number == 2:
                        self.path_video = os.path.join(path, name_video + '_tracking.avi')
                        self.path_npz = os.path.join(path, name_video + '_tracking.npz')
                        self.path_csv = os.path.join(path, name_video + '_tracking.csv')
                    else:
                        self.title = name_video
                        self.path_video = os.path.join(path, name_video + '.avi')
                        self.path_npz = os.path.join(path, name_video + '.npz')
                        self.path_csv = os.path.join(path, name_video + '.csv')
                    self.out_video = cv2.VideoWriter(self.path_video, self.fourcc_out, self.fps,
                                                     (self.width, self.height))
                elif state == "plus":
                    self.threshold += 1
                elif state == "minus":
                    self.threshold -= 1
                else:
                    self.state = state

            if self.cam_number == 1:
                if self.target_counter == self.target and self.active:
                    self.target_counter = 0
                    ret, self.frame = self.video.read()
                    if ret:
                        self.do_tracking_out()
                        self.add_info_tracking_out()
                        self.do_record1()
                        self.do_stream()
                        self.do_view()
                else:
                    ret = self.video.grab()
                    if ret:
                        self.target_counter += 1

            elif self.cam_number == 2:
                if self.target_counter == self.target and self.active:
                    self.target_counter = 0
                    ret, self.frame = self.video.read()
                    if ret:
                        # self.do_tracking_in()
                        self.do_record2()
                        # self.add_info_tracking_in()
                        self.do_stream()
                        self.do_view()
                elif self.active:
                    ret = self.video.grab()
                    if ret:
                        self.target_counter += 1

            elif self.cam_number == 3:
                if self.active:
                    (ret, self.frame), self.ctime = self.video.read(), time_utils.now_datetime()
                    if ret:
                        self.create_mask()
                        self.do_tracking_in()
                        self.do_tracking_position()
                        self.do_record3()
                        self.add_info_tracking_in()
                        self.add_info_tracking_position()
                        self.add_info_states()
                        self.add_info_trials()
                        self.do_stream()
                        self.target_counter += 1
                        if self.target_counter == self.target:
                            self.do_view()
                            self.target_counter = 0
        self.close()
        return

    def do_tracking_out(self):
        [zcxmin, zcxmax, zcymin, zcymax] = self.cage_zone
        [zdxmin1, zdxmax1, zdymin1, zdymax1] = self.doors1_zone
        [zdxmin2, zdxmax2, zdymin2, zdymax2] = self.doors2_zone

        cage_greyscale_frame = cv2.cvtColor(self.frame[zcymin:zcymax, zcxmin:zcxmax], cv2.COLOR_BGR2GRAY)
        doors1_greyscale_frame = cv2.cvtColor(self.frame[zdymin1:zdymax1, zdxmin1:zdxmax1], cv2.COLOR_BGR2GRAY)
        doors2_greyscale_frame = cv2.cvtColor(self.frame[zdymin2:zdymax2, zdxmin2:zdxmax2], cv2.COLOR_BGR2GRAY)

        cage_gaussian_frame = cv2.GaussianBlur(cage_greyscale_frame, (5, 5), 0)
        doors1_gaussian_frame = cv2.GaussianBlur(doors1_greyscale_frame, (5, 5), 0)
        doors2_gaussian_frame = cv2.GaussianBlur(doors2_greyscale_frame, (5, 5), 0)

        cage_thresh = cv2.threshold(cage_gaussian_frame, self.threshold2, 225, cv2.THRESH_BINARY_INV)[1]
        doors1_thresh = cv2.threshold(doors1_gaussian_frame, self.threshold, 225, cv2.THRESH_BINARY_INV)[1]
        doors2_thresh = cv2.threshold(doors2_gaussian_frame, self.threshold3, 225, cv2.THRESH_BINARY_INV)[1]

        area_cage = cv2.countNonZero(cage_thresh)
        area_doors1 = cv2.countNonZero(doors1_thresh)
        area_doors2 = cv2.countNonZero(doors2_thresh)

        area_total = area_cage + area_doors1 + area_doors2
        self.area_cage.value = int(area_cage)
        self.area_doors1.value = int(area_doors1)
        self.area_doors2.value = int(area_doors2)
        self.area_total.value = int(area_total)


    def do_tracking_in(self):

        if self.tracking_inside:
            [zdxmin1, zdxmax1, zdymin1, zdymax1] = self.doors1_zone
            [zdxmin2, zdxmax2, zdymin2, zdymax2] = self.doors2_zone

            doors1_greyscale_frame = cv2.cvtColor(self.frame[zdymin1:zdymax1, zdxmin1:zdxmax1], cv2.COLOR_BGR2GRAY)
            doors2_greyscale_frame = cv2.cvtColor(self.frame[zdymin2:zdymax2, zdxmin2:zdxmax2], cv2.COLOR_BGR2GRAY)

            doors1_gaussian_frame = cv2.GaussianBlur(doors1_greyscale_frame, (5, 5), 0)
            doors2_gaussian_frame = cv2.GaussianBlur(doors2_greyscale_frame, (5, 5), 0)

            doors1_thresh = cv2.threshold(doors1_gaussian_frame, self.threshold, 225, cv2.THRESH_BINARY_INV)[1]
            doors2_thresh = cv2.threshold(doors2_gaussian_frame, self.threshold, 225, cv2.THRESH_BINARY_INV)[1]

            area_doors1 = cv2.countNonZero(doors1_thresh)
            area_doors2 = cv2.countNonZero(doors2_thresh)

            area_total = area_doors1 + area_doors2
            self.area_doors1.value = int(area_doors1)
            self.area_doors2.value = int(area_doors2)
            self.area_total.value = int(area_total)


        if self.tracking_inside_floor:
            [zdxmin3, zdxmax3, zdymin3, zdymax3] = self.floor1_zone
            [zdxmin4, zdxmax4, zdymin4, zdymax4] = self.floor2_zone

            floor1_greyscale_frame = cv2.cvtColor(self.frame[zdymin3:zdymax3, zdxmin3:zdxmax3], cv2.COLOR_BGR2GRAY)
            floor2_greyscale_frame = cv2.cvtColor(self.frame[zdymin4:zdymax4, zdxmin4:zdxmax4], cv2.COLOR_BGR2GRAY)

            floor1_gaussian_frame = cv2.GaussianBlur(floor1_greyscale_frame, (5, 5), 0)
            floor2_gaussian_frame = cv2.GaussianBlur(floor2_greyscale_frame, (5, 5), 0)

            floor1_thresh = cv2.threshold(floor1_gaussian_frame, self.threshold, 225, cv2.THRESH_BINARY_INV)[1]
            floor2_thresh = cv2.threshold(floor2_gaussian_frame, self.threshold, 225, cv2.THRESH_BINARY_INV)[1]

            area_floor1 = cv2.countNonZero(floor1_thresh)
            area_floor2 = cv2.countNonZero(floor2_thresh)

            area_total_floor = area_floor1 + area_floor2
            self.area_total_floor.value = int(area_total_floor)

    def create_mask(self):
        if self.create_mask_flag:
            [zdxmin1, zdxmax1, zdymin1, zdymax1] = self.doors1_zone
            [zdxmin2, zdxmax2, zdymin2, zdymax2] = self.doors2_zone
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.mask_mouse = np.zeros_like(gray_frame)
            cv2.rectangle(self.mask_mouse, (zdxmin1, zdymin1), (zdxmax1, zdymax1), (255, 255, 255), -1)
            cv2.rectangle(self.mask_mouse, (zdxmin2, zdymin2), (zdxmax2, zdymax2), (255, 255, 255), -1)
            self.mask_mouse2 = cv2.bitwise_not(self.mask_mouse)

        self.create_mask_flag = False

    def do_tracking_position(self):
        if self.tracking_position:
            gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # Apply the mask to the grayscale image
            frame_mouse = cv2.bitwise_and(gray_frame, self.mask_mouse)
            frame_mouse = cv2.bitwise_or(frame_mouse, self.mask_mouse2)

            _, thresh = cv2.threshold(frame_mouse, self.threshold, 255,
                                      cv2.THRESH_BINARY_INV)  # Adjust threshold value as needed
            # Find contours which will detect the mouse
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for index, contour in enumerate(contours):

                # You can filter out small contours if needed
                if cv2.contourArea(contour) < 50:
                    continue

                # Add the origin offset to the contour (in this case origin = 0)
                self.contour2 = contour

                # Find the centroid of the mouse to get its position
                M = cv2.moments(self.contour2)
                if M['m00'] != 0:
                    self.cx = int(M['m10'] / M['m00'])
                    self.cy = int(M['m01'] / M['m00'])
                else:
                    self.cx, self.cy = 0, 0


    def do_record1(self):
        if time_utils.now_seconds() > self.next_time:
            self.next_time += self.duration_video
            self.get_output()
        self.out_video.write(self.frame)

    def do_record2(self):
        if time_utils.now_seconds() > self.next_time:
            self.next_time += self.duration_video
            self.get_output()
        self.out_video.write(self.frame)

    def do_record3(self):
        self.out_video.write(self.frame)
        self.timestamps += [self.ctime]

    def get_output(self):
        if self.out_video:
            self.out_video.release()
        date = time_utils.now_string_for_files()
        title = self.name_video[0:3] + '_' + date + '_' + self.name_video[-4:] + '.avi'
        path = os.path.join(self.path, title)
        self.delete_old_files()
        self.out_video = cv2.VideoWriter(path, self.fourcc_out, self.fps, (self.width, self.height))

    def add_info_trials(self):
        cv2.putText(self.frame, "trial: " + str(self.trial_number),
                    (50, 100), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

    def add_info_states(self):
        self.frame_counter += 1
        self.fps_counter += 1

        now_sec = int(self.chrono.get_seconds())
        if now_sec % 5 == 0 and now_sec != self.last_sec:  # reset the fps counter each 5 sec
            self.last_sec = int(now_sec)
            self.fps_now = int(self.fps_counter / 5)
            self.fps_counter = 0

        cv2.putText(self.frame, self.title,
                    (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(self.frame, 'fps: ' + str(self.fps_now) + ' time: ' + self.chrono.get_time_string(),
                    (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        try:
            circle = self.cam_states[self.state]
            cv2.circle(self.frame, circle, 12, (255, 255, 255), -1)
            cv2.putText(self.frame, f'{self.state}', (450, 35),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        except KeyError:
            pass


        self.frames += [self.frame_counter]
        self.states += [self.state]
        self.trials += [self.trial_number]
        self.cxs += [self.cx]
        self.cys += [self.cy]

    def add_info_tracking_out(self):
        try:
            [zcxmin, zcxmax, zcymin, zcymax] = self.cage_zone
            [zdxmin1, zdxmax1, zdymin1, zdymax1] = self.doors1_zone
            [zdxmin2, zdxmax2, zdymin2, zdymax2] = self.doors2_zone

            cv2.putText(self.frame, time_utils.now_string(), (350, 40), cv2.FONT_HERSHEY_DUPLEX,
                        0.35, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'{self.state[11:19]}', (350, 80), cv2.FONT_HERSHEY_DUPLEX,
                        0.35, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'{self.state[21:]}', (350, 100), cv2.FONT_HERSHEY_DUPLEX,
                        0.35, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'Area in the cage: {self.area_cage.value}',
                        (settings.CAM1_TEXT_X, settings.CAM1_TEXT_Y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'Area in door1:    {self.area_doors1.value}',
                        (settings.CAM1_TEXT_X, settings.CAM1_TEXT_Y + 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'Area in door2:    {self.area_doors2.value}',
                        (settings.CAM1_TEXT_X, settings.CAM1_TEXT_Y + 40),
                        cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, f'Area total:        {self.area_total.value}',
                        (settings.CAM1_TEXT_X, settings.CAM1_TEXT_Y + 60),
                        cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 0, 255), 1, cv2.LINE_AA)

            cv2.rectangle(self.frame, (zcxmin, zcymin), (zcxmax, zcymax), (0, 255, 0), 2)
            cv2.rectangle(self.frame, (zdxmin1, zdymin1), (zdxmax1, zdymax1), (0, 255, 255), 2)
            cv2.rectangle(self.frame, (zdxmin2, zdymin2), (zdxmax2, zdymax2), (255, 255, 0), 2)

            for key, value in self.centers.items():
                cv2.circle(self.frame, value, 7, (255, 255, 255), -1)
        except Exception:
            pass

    def add_info_tracking_in(self):
        if self.tracking_inside:
            try:
                [zdxmin1, zdxmax1, zdymin1, zdymax1] = self.doors1_zone
                [zdxmin2, zdxmax2, zdymin2, zdymax2] = self.doors2_zone
                cv2.putText(self.frame, f'Area in the box: {self.area_total.value}', (10, 450),
                            cv2.FONT_HERSHEY_DUPLEX, 0.4, (255, 0, 255), 1, cv2.LINE_AA)
                cv2.rectangle(self.frame, (zdxmin1, zdymin1), (zdxmax1, zdymax1), (255, 0, 255), 2)
                cv2.rectangle(self.frame, (zdxmin2, zdymin2), (zdxmax2, zdymax2), (255, 0, 255), 2)
                for key, value in self.centers.items():
                    cv2.circle(self.frame, value, 7, (255, 255, 255), -1)

            except Exception:
                pass

        if self.tracking_inside_floor:
            try:
                [zdxmin3, zdxmax3, zdymin3, zdymax3] = self.floor1_zone
                [zdxmin4, zdxmax4, zdymin4, zdymax4] = self.floor2_zone
                cv2.putText(self.frame, f'Area in the floor: {self.area_total_floor.value}', (10, 420),
                            cv2.FONT_HERSHEY_DUPLEX, 0.4, (100, 0, 255), 1, cv2.LINE_AA)
                cv2.rectangle(self.frame, (zdxmin3, zdymin3), (zdxmax3, zdymax3), (100, 0, 255), 2)
                cv2.rectangle(self.frame, (zdxmin4, zdymin4), (zdxmax4, zdymax4), (100, 0, 255), 2)

            except Exception:
                pass

    def add_info_tracking_position(self):
        if self.tracking_position:

            cv2.putText(self.frame, 'threshold mouse: ' + str(self.threshold), (10, 200),
                        cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
            try:
                # Draw the contour of the mouse
                cv2.drawContours(self.frame, [self.contour2], -1, (0, 255, 0), 1)
                # Draw the centroid of the mouse
                # cv2.circle(self.frame, (self.cx, self.cy), 5, (255, 255, 0), -1)
                # Draw the value of luminance of the LED
            except:
                pass

    def do_stream(self):
        pass

    def do_view(self):
        try:
            self.image_queue.put_nowait(self.frame)
        except Exception:
            pass

    def close(self):
        self.video.release()

    def stop(self):
        self.command_queue.put('stop')

    def save_video1or2(self):
        self.out_video.release()

    def save_video3(self):
        self.out_video.release()
        timestamps = np.array(self.timestamps, dtype='datetime64[ms]')
        frames = np.array(self.frames)
        states = np.array(self.states)

        arrays = [self.timestamps, self.frames, self.trials, self.states, self.cxs, self.cys]

        min_length = min(len(arr) for arr in arrays)

        self.timestamps = self.timestamps[:min_length]
        self.frames = self.frames[:min_length]
        self.trials = self.trials[:min_length]
        self.states = self.states[:min_length]
        self.cxs = self.cxs[:min_length]
        self.cys = self.cys[:min_length]

        # save timestamps, frames and states to a df
        df = pd.DataFrame({'timestamps': timestamps, 'frames': frames, 'trial': self.trials, 'states': states,
                           'x': self.cxs, 'y': self.cys})
        # save the df to a csv
        df.to_csv(self.path_csv, index=False)

    def delete_old_files(self):
        paths = []
        for file in os.listdir(self.path):
            if file.endswith('.avi'):
                paths.append(os.path.join(self.path, file))

        number_to_delete = len(paths) - self.number_of_videos
        paths = sorted(paths)
        for i in range(number_to_delete):
            try:  # the path can not be ready because it is being created or deleted
                os.remove(paths[i])
            except:
                pass

    @staticmethod
    def _decode_fourcc(v):
        v = int(v)
        return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])


try:
    cam1 = Video(port=settings.CAMERA1_PORT,
                 cam_number=settings.CAM1_NUMBER,
                 name_video=settings.CAM1_NAME_VIDEO + '_' + time_utils.now_string_for_files(),
                 path=settings.VIDEOS_DIRECTORY,
                 width=settings.CAM1_WIDTH,
                 height=settings.CAM1_HEIGHT,
                 fps=settings.CAM1_FPS,
                 codec_video=settings.CAM1_CODEC_VIDEO,
                 cam_states=settings.CAM1_STATES,
                 duration_video=settings.CAM1_DURATION_VIDEO,
                 number_of_videos=settings.CAM1_NUMBER_OF_VIDEOS,
                 threshold=settings.CAM1_THRESHOLD,
                 cage_zone=settings.CAM1_CAGE_ZONE,
                 doors1_zone=settings.CAM1_DOORS1_ZONE,
                 doors2_zone=settings.CAM1_DOORS2_ZONE,
                 floor1_zone=None,
                 floor2_zone=None)
    print('camera1 OK')
except:
    print('error in camera1')
    cam1 = FakeVideo()

try:
    cam2 = Video(port=settings.CAMERA2_PORT,
                 cam_number=settings.CAM2_NUMBER,
                 name_video=settings.CAM2_NAME_VIDEO + '_' + time_utils.now_string_for_files(),
                 path=settings.VIDEOS_DIRECTORY,
                 width=settings.CAM2_WIDTH,
                 height=settings.CAM2_HEIGHT,
                 fps=settings.CAM2_FPS,
                 codec_video=settings.CAM2_CODEC_VIDEO,
                 cam_states=settings.CAM2_STATES,
                 duration_video=settings.CAM2_DURATION_VIDEO,
                 number_of_videos=settings.CAM2_NUMBER_OF_VIDEOS,
                 threshold=settings.CAM2_THRESHOLD,
                 cage_zone=None,
                 doors1_zone=None,
                 doors2_zone=None,
                 floor1_zone=None,
                 floor2_zone=None)
    print('camera2 OK')
except:
    print('error in camera2')
    cam2 = FakeVideo()

try:
    cam3 = Video(port=settings.CAMERA3_PORT,
                 cam_number=settings.CAM3_NUMBER,
                 name_video=settings.CAM3_NAME_VIDEO,
                 path=settings.VIDEOS_DIRECTORY,
                 width=settings.CAM3_WIDTH,
                 height=settings.CAM3_HEIGHT,
                 fps=settings.CAM3_FPS,
                 codec_video=settings.CAM3_CODEC_VIDEO,
                 cam_states=settings.CAM3_STATES,
                 duration_video=settings.CAM3_DURATION_VIDEO,
                 number_of_videos=settings.CAM3_NUMBER_OF_VIDEOS,
                 threshold=settings.CAM3_THRESHOLD,
                 cage_zone=settings.CAM3_CAGE_ZONE,
                 doors1_zone=settings.CAM3_DOORS1_ZONE,
                 doors2_zone=settings.CAM3_DOORS2_ZONE,
                 floor1_zone=settings.CAM3_FLOOR1_ZONE,
                 floor2_zone=settings.CAM3_FLOOR2_ZONE,
                 tracking_position=settings.CAM3_TRACKING_POSITION)
    print('camera3 OK')

except:
    print('error in camera3')
    cam3 = FakeVideo()

cam1.play()
cam2.play()
cam3.play()
