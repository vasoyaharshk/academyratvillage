import inspect
import importlib
import os
import pkgutil
import hashlib
from shutil import copyfile
from threading import Thread
from academy.utils import utils
from user import settings
from academy import bpod
from pybpodapi.protocol import Bpod, StateMachine
from academy.camera import cam2, cam3
from academy.touch import touch
from academy import time_utils, queues, telegram_bot


def softcode_handler(data):
    queues.softcodes.put(data)


class SuperSubject:
    def __init__(self, name, subject, task, all_in, min_time, index):
        self.name = name
        self.subject = subject
        self.task = task
        self.all_in = all_in
        self.min_time = min_time
        self.index = index


class Task(object):

    def __init__(self):
        self.task = 'UNKNOWN'
        self.p = None
        self.stage = 1
        self.substage = 1

        self.stim_dur_ds = 0  # by default
        self.stim_dur_dm = 0  # by default
        self.stim_dur_dl = 0.1  # by default

        self.checksum = None
        self.subject_class = None
        self.subject = None
        self.subject_weight = 0
        self.my_bpod = None
        self.sma = None
        self.current_trial_states = None
        self.box = settings.BOX_NAME
        self.date = None
        self.current_trial = 0
        self.trials_min = settings.DEFAULT_TRIALS_MIN
        self.duration_min = settings.DEFAULT_DURATION_MIN
        self.duration_tired = settings.DEFAULT_DURATION_TIRED
        self.trials_tired = settings.DEFAULT_TRIALS_TIRED
        self.trials_max = settings.DEFAULT_TRIALS_MAX
        self.duration_max = settings.DEFAULT_DURATION_MAX
        self.tired = False
        self.gui_input_fixed = ['subject_weight']
        self.gui_input = []
        self.gui_output = []
        self.info = None
        self.collection = None
        self.values_dict = {}
        self.response_x = []
        self.response_y = []
        self.loop = self.clear

    def clear(self):
        pass

    def init_variables(self):
        pass

    def set_and_run(self, subject, subject_name, subject_weight, task_manager):

        utils.control_softcodes = 0
        utils.control_serials = 0

        touch.create_new_device()

        self.subject_class = subject
        self.subject = subject_name
        self.subject_weight = subject_weight

        # empty response_queue (from previous task)
        while True:
            try:
                queues.responses.get_nowait()
            except:
                break

        # empty softcode_queue (from previous task)
        while True:
            try:
                queues.softcodes.get_nowait()
            except:
                break

        self.current_trial = 0
        trials = int(self.trials_max)

        if task_manager is not None:

            self.date = task_manager.start[:10]
            video_directory = os.path.join(settings.VIDEOS_DIRECTORY, subject_name)

            if not os.path.exists(video_directory):
                os.mkdir(video_directory)

            #cam2.put_state('File' + task_manager.filename)
            cam3.put_state('File' + task_manager.filename)

        else:
            #cam2.put_state('active')
            cam3.put_state('active')
            self.date = time_utils.now_string()[:10]

        self.p = Thread(target=self.run_thread, args=(trials,), daemon=True)
        self.p.start()


    def run_thread(self, trials):
        utils.chrono.reset()
        if self.my_bpod is None:

            self.my_bpod = bpod.create_Bpod()

            if self.my_bpod is None:
                telegram_bot.alarm_bpod("error starting task")

            self.my_bpod.softcode_handler_function = softcode_handler

            while True:

                #print(utils.current_trials, utils.control_serials, utils.control_softcodes)

                if settings.BOX_NAME == 4:
                    if utils.current_trials == utils.control_serials + 5:
                        print('alarm serial')
                        #telegram_bot.alarm_serials()
                        #utils.force_relaunch = True

                    if utils.current_trials == utils.control_softcodes + 5:
                        print('alarm softcode')
                        #telegram_bot.alarm_softcodes()
                        #utils.force_relaunch = True

                queues.trials.put(self.current_trial)
                utils.current_trials = self.current_trial
                self.sma = StateMachine(self.my_bpod)

                self.my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL,
                                             channel_number=1, value=16)

                if self.current_trial < trials:
                    self.main_loop()
                else:
                    self.sma.add_state(
                        state_name='End',
                        state_timer=100,
                        state_change_conditions={Bpod.Events.Tup: 'exit'},
                        output_actions=[]
                    )
                if len(self.sma.state_names) == 0:
                    self.sma.add_state(
                        state_name='End',
                        state_timer=0,
                        state_change_conditions={Bpod.Events.Tup: 'exit'},
                        output_actions=[]
                    )
                self.my_bpod.send_state_machine(self.sma)
                self.my_bpod.run_state_machine(self.sma)
                self.current_trial_states = self.my_bpod.session.current_trial.states_durations
                self.update_response()
                self.after_trial()
                self.register_values()
                self.current_trial += 1
                cam3.put_state(str(self.current_trial))

    def main_loop(self):
        raise NotImplementedError

    def after_trial(self):
        pass

    def configure_gui(self):
        pass

    def update_response(self):
        self.response_x = []
        self.response_y = []
        response_list = []
        while True:
            try:
                response_list.append(queues.responses.get_nowait())
            except:
                break
        for item in response_list:
            try:
                self.response_x.append(item[0])
                self.response_y.append(item[1])
            except IndexError:
                pass

        self.response_x = ','.join(str(e) for e in self.response_x)
        self.response_y = ','.join(str(e) for e in self.response_y)

    def register_value(self, key, value):
        self.my_bpod.register_value(key, value)

    def register_values(self):
        self.my_bpod.register_value('task', self.task)
        self.my_bpod.register_value('stage', self.stage)
        self.my_bpod.register_value('checksum', self.checksum)
        self.my_bpod.register_value('subject', self.subject)
        self.my_bpod.register_value('subject_weight', self.subject_weight)
        self.my_bpod.register_value('box', self.box)
        self.my_bpod.register_value('date', self.date)

        for i in range(len(utils.task.gui_input)):
            name = utils.task.gui_input[i]
            attribute = getattr(utils.task, name)
            self.my_bpod.register_value(name, attribute)

        self.my_bpod.register_value('TRIAL', None)


class TaskCollection(object):
    def __init__(self):
        self.tasks_package = 'tasks'
        self.tasks = []
        self.seen_paths = []
        self.reload_tasks()
        self.subjects_dict = self.create_subjects_dict()

    def reload_tasks(self):
        self.tasks = []
        self.seen_paths = []
        self.walk_package(self.tasks_package)
        for task in self.tasks:
            task.init_variables()
            task.configure_gui()


    def create_subjects_dict(self):
        subjects_dict = {}
        min_index = 100000000

        active = {subject.name for subject in utils.subjects.items}

        for name in active:
            try:
                subject = utils.subjects.read_last_value_excluding('name', name, 'task',
                                                                  ['manual_water',
                                                                   'control_weight', 'basal_weight'])

                index = utils.subjects.read_last_index_excluding('name', name, 'task',
                                                                ['manual_water',
                                                                 'control_weight', 'basal_weight'])

                min_index = min(index, min_index)

                tag = subject.tag
                all_in = False
                min_time = time_utils.string_to_datetime(subject.date, subject.wait_seconds)
                subject_task = None

                for task in self.tasks:
                    if task.task == subject.task:
                        subject_task = task
                        break

                super_subject = SuperSubject(name, subject, subject_task, all_in, min_time, index)

                subjects_dict[tag] = super_subject
            except:
                pass

        for super_subject in subjects_dict.values():
            if super_subject.index == min_index:
                super_subject.all_in = True
        return subjects_dict


    def walk_package(self, package):
        try:
            imported_package = __import__(package, fromlist=['blah'])
        except ModuleNotFoundError:
            return

        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:

                plugin_module = importlib.import_module(pluginname)
                importlib.reload(plugin_module)

                # plugin_module = __import__(pluginname, fromlist=['blah'])

                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, c) in clsmembers:
                    if issubclass(c, Task) & (c is not Task):
                        path = inspect.getmodule(c().__class__).__file__
                        name = c.__name__
                        new_task = c()
                        new_task.task = name
                        self.tasks.append(new_task)
                        self.create_checksum(name, path)

        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])

        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]

                for child_pkg in child_pkgs:
                    self.walk_package(package + '.' + child_pkg)

    def create_checksum(self, name, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        digester = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                digester.update(chunk)
        checksum = digester.hexdigest()
        new_path = os.path.join(settings.BACKUP_TASKS_DIRECTORY, filename + '_' + checksum + '.py')
        for task in self.tasks:
            if task.task == name:
                task.checksum = checksum
        if not os.path.exists(new_path):
            copyfile(path, new_path)

    @staticmethod
    def path_generator(path, pattern):
        paths = []
        for root, _, file in os.walk(path):
            for f in file:
                if f.endswith(pattern):
                    paths.append(os.path.join(root, f))
        return paths

task_collection = TaskCollection()
