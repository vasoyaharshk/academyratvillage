from academy.collection import Collection
from academy import time_utils
import user.collections as collections
from academy.camera import cam1, cam2


class Utils:
    def __init__(self):
        self.state = 0
        self.old_state = 0
        self.change_to_state = 0
        self.change_gui = False
        self.change_gui7 = False
        self.relaunch = False
        self.force_relaunch = False
        self.state_after_relaunch = 0

        self.alarms = None
        self.events = None
        self.subjects = None
        self.subject = None

        self.chrono = time_utils.Chrono()
        self.reading_tags = 0

        self.gui_name = 'TASKS'

        self.current_trials = 0

        self.list_of_trial_timings = []

        self.task = None
        self.touch = None

        self.x_max = 3
        self.subject_name = ''
        self.day = True
        self.threshold = 0

        self.alarm_mice_time = 0  # 2 mice in the box
        self.alarm_mice_repetition = 0
        self.alarm_trapped_time = 0  # 2 mice in the box
        self.alarm_trapped_repetition = 0
        self.alarm_mouse_time = 1000000000  # too much time in box
        self.alarm_mouse_time2 = 1000000000  # too much time in box

        self.task_real_duration = 0

        self.looping = False

        self.add_collections()
        self.super_subject = None
        self.task_manager = None

        self.control_softcodes = 0
        self.control_serials = 0

        self.subject_trapped = False

    def log(self, subject, description, action_type):
        date = time_utils.now_string()
        print(date + '  ' + subject + '  ' + description + '  ' + action_type)
        event_dict = {'subject': subject, 'description': description, 'type': action_type}
        self.events.add_new_item(event_dict)

    def log_cam(self, subject, description, action_type):
        date = time_utils.now_string()
        print(date + '  ' + subject + '  ' + description + '  ' + action_type)
        event_dict = {'subject': subject, 'description': description, 'type': action_type}
        self.events.add_new_item(event_dict)
        if action_type == 'END':
            cam1.put_state(date + '  ' + subject + '  ' + description + '  END')
            cam2.put_state(date + '  ' + subject + '  ' + description + '  END')
        else:
            cam1.put_state(date + '  ' + subject + '  ' + description)
            cam2.put_state(date + '  ' + subject + '  ' + description)

    def add_collections(self):
        names = [item for item in dir(collections) if not item.startswith("__")]
        for name in names:
            attribute = getattr(collections, name)
            collection = Collection(name, attribute)
            setattr(self, name, collection)

utils = Utils()
