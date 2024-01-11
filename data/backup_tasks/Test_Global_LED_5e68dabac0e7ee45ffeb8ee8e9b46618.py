from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class Test_Global_LED(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Global LED.
        """

    def init_variables(self):
        self.trials_max = 10

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='LED_ON',
            state_timer=60,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.LED, 4)])

    def after_trial(self):
        pass
