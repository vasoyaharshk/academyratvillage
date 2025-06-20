from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class Test_Global_LED(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Global LED.
        """

    def init_variables(self):
        self.trials_max = 1000

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='LED_ON',
            state_timer=1000,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.LED, 1), (Bpod.OutputChannels.LED, 2), (Bpod.OutputChannels.LED, 3), (Bpod.OutputChannels.LED, 4), (Bpod.OutputChannels.LED, 5), (Bpod.OutputChannels.LED, 6)]
        )

    def after_trial(self):
        pass
