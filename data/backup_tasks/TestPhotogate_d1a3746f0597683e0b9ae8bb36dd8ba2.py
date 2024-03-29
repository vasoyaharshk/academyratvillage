from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class Test_Photogates(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        Checking photogates.
        """

    def init_variables(self):
        self.trials_max = 100

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='Waiting',
            state_timer=500,
            state_change_conditions={'Port1In': 'Cross_corridor',
                                     Bpod.Events.Tup: 'exit'},
            output_actions=[])

        self.sma.add_state(
            state_name='Cross_corridor',
            state_timer=500,
            state_change_conditions={'Port1Out': 'Waiting',
                                    Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.LED, 1)])

    def after_trial(self):
        pass
