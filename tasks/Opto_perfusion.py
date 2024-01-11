from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils


class Opto_perfusion(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Homecage with laser stimulation
        """

    def init_variables(self):
        # general
        self.trials_max = 10

    def configure_gui(self):  # Variables that appear in the GUI
        self.gui_input = ['trials_max']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))


        self.sma.add_state(
            state_name='Light_off',
            state_timer=60*3,
            state_change_conditions={Bpod.Events.Tup: 'Light_on'},
            output_actions=[(Bpod.OutputChannels.BNC1, 0)])

        self.sma.add_state(
            state_name='Light_on',
            state_timer=60*3,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.BNC1, 3), (Bpod.OutputChannels.PWM4, 5)])
        # close corridor door 2 when subject enters to behavioral box

        (Bpod.OutputChannels.SoftCode, 15)

    def after_trial(self):
        pass
