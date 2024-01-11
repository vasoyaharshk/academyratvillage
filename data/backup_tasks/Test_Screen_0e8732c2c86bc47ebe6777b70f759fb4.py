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
        self.response_duration = 5

        self.x = [60, 200, 340]  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30

    def configure_gui(self):
        self.gui_input = ['trials_max', 'width', 'stim_duration']

    def main_loop(self):
        # Start the State Machine
        self.sma.add_state(
            state_name='Start_task',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'Stimulus_onset'},
            output_actions=[])

        self.sma.add_state(
            state_name='Stimulus_onset',
            state_timer=self.response_duration,
            state_change_conditions={Bpod.Events.Tup: 'Stimulus_offset'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 3)])

        self.sma.add_state(
            state_name='Stimulus_offset',
            state_timer=self.response_duration,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15)])


def after_trial(self):
        pass

