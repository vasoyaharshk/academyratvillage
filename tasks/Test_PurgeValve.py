from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class Test_PurgeValve(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Purge valve.
        """

    def init_variables(self):
        self.trials_max = 1

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='Valve_1',
            state_timer=5,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.LED, 1)])

    def after_trial(self):
        pass
