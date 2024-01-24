from academy.task_collection import Task
from pybpodapi.protocol import Bpod

from user import settings

class Test_Screen(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Checking psychopy.
        """

    def init_variables(self):
        self.trials_max = 10

        self.stim_duration = 3
        self.response_duration = 2

        self.x = 60  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30
        self.contrast= 1.2 #0 black, 1 gray, 2 white. Default 60%

        self.correct_th = 130  # 1/3 of the screen
        self.repoke_th = settings.WIN_SIZE[0] * 2  # full screen


    def configure_gui(self):
        self.gui_input = ['trials_max', 'width', 'stim_duration']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # Start the State Machine
        self.sma.add_state(
            state_name='Start_task',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'Stimulus_onset'},
            output_actions=[])

        self.sma.add_state(
            state_name='Stimulus_onset',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 2)])

        self.sma.add_state(
            state_name='Response_window',
            state_timer=10,
            state_change_conditions={'SoftCode1': 'Stimulus_offset', 'SoftCode2': 'Stimulus_offset',
                                     'SoftCode3': 'Stimulus_offset', 'SoftCode4': 'Stimulus_offset',
                                     Bpod.Events.Tup: 'Stimulus_offset'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4)])

        self.sma.add_state(
            state_name='Stimulus_offset',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15)])




def after_trial(self):
        pass

