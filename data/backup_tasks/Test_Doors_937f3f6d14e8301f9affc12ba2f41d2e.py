from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class Test_Doors(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Open and close doors.
        """

    def init_variables(self):
        self.trials_max = 10

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
                state_name='CloseDoors',
                state_timer=2,
                state_change_conditions={Bpod.Events.Tup: 'Delay'},
                output_actions=[(Bpod.OutputChannels.Serial1, 11)])

        self.sma.add_state(
            state_name='Delay',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'OpenDoors'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 16)])  # super important that the softcode is in every trial)

        self.sma.add_state(
            state_name='OpenDoors',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.Serial1, 12)])

    def after_trial(self):
        pass
