from academy.task_collection import Task
from pybpodapi.protocol import Bpod

class Test_Sound(Task):
    def __init__(self):
        super().__init__()

    def init_variables(self):
        self.trials_max = 10

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='RW_sound_on',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'Waiting'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 11)])

        self.sma.add_state(
            state_name='Waiting',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'PNSH_sound_on'},
            output_actions=[])

        self.sma.add_state(
            state_name='PNSH_sound_on',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'Waiting2'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 14)])

        self.sma.add_state(
            state_name='Waiting2',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):
        pass
