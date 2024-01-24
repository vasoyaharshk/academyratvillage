from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils


class Automatic_Water(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Gives water to animals in the behavioral box

        # PORTS INFO
        Port 1 - WATER PORT: LED, photogates and pump
        """

    def init_variables(self):
        self.duration_min = 120 # 2 mins
        self.duration_max = 180

        self.stage = 0
        self.substage = 0
        self.reward_drunk = 600 # deliver 600 ul water

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        print(self.valve_time)

    def configure_gui(self):
        self.gui_input = ['reward_drunk']


    def main_loop(self):

        if self.current_trial == 0:
            self.valve_time = self.reward_drunk * self.valve_time / self.valve_reward
            self.sma.add_state(
                state_name='Automatic_water',  # deliver reward
                state_timer=self.valve_time,
                state_change_conditions={Bpod.Events.Tup: 'Waiting'},
                output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Waiting',
            state_timer=self.duration_min/4,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.PWM4, 5)])


    def after_trial(self):
        self.register_value('reward_drunk', self.reward_drunk)

