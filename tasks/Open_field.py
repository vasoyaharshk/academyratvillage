from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils


class Open_field(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Homecage with laser stimulation
        """

    def init_variables(self):
        # general
        self.trials_max = 2

    def configure_gui(self):  # Variables that appear in the GUI
        self.gui_input = ['trials_max']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))


        self.sma.add_state(
            state_name='Light_off',
            state_timer=60*3,
            state_change_conditions={Bpod.Events.Tup: 'Light_on'},
            output_actions=[(Bpod.OutputChannels.BNC1, 0),(Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Light_on',
            state_timer=60*3,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 11), (Bpod.OutputChannels.BNC1, 3), (Bpod.OutputChannels.PWM4, 5)])

    def after_trial(self):
        pass
