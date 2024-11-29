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
        self.duration_max = 300 # 5 mins

        self.stage = 0
        self.substage = 0
        self.reward_drunk = 500 # deliver 1000 ul water

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        print(self.valve_time)

        # #Non-used variables so that stage training works:
        # self.stim_dur_ds = 0
        # self.stim_dur_dm = 0
        # self.stim_dur_dl = 0
        # self.choice = 0
        # self.substage = 0
        # self.block = 0  # This is the number of trials one conditions will remain for
        # self.conditions = []  # Takes the conditions from select task file.
        # self.completed_conditions = []  # To store completed conditions
        # self.current_condition = 0  # To track the current condition in progress
        # self.repetition = 0  # To store how many times the conditions needs to repeat.
        # self.current_repetition = 0  # To store how many times the condition has repeated.
        # self.trial_counter = 0  # Track the number of trials for the current condition


    def configure_gui(self):
        self.gui_input = ['reward_drunk']


    def main_loop(self):

        if self.current_trial == 0:
            self.valve_time = self.reward_drunk * self.valve_time / self.valve_reward
            self.sma.add_state(
                state_name='Close_door',  # deliver reward
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Automatic_water'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20)])

            self.sma.add_state(
                state_name='Automatic_water',  # deliver reward
                state_timer=self.valve_time,
                state_change_conditions={Bpod.Events.Tup: 'Waiting'},
                output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.LED, 1)])

        self.sma.add_state(
            state_name='Waiting',
            state_timer=self.duration_min/4,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):
        self.register_value('reward_drunk', self.reward_drunk)

