from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Water_Filler(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task displays the image of the jars which are touchable. This script includes repoketh, the ability to make correct choices.
        ########   TASK INFO   ########
        Stage 1: Indication: Only blue jar of pegs stimulus appears Blue is rewarding and yellow unrewarding
        Stage 2: Discrimination 1: Blue and yellow jar of pegs appears (100% each)
        Stage 3: Discrimination 2: Blue and yellow jar of pegs appears (1 jar is 100% of unrewarded color yellow and the other is 50%)

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        #Non-used variables so that stage training works:
        self.stim_dur_ds = 0
        self.stim_dur_dm = 0
        self.stim_dur_dl = 0
        self.choices = 0
        self.substage = 0

        # Variables for the task:
        self.duration_max = 300
        self.duration_min = 180
        self.duration_tired = 1800
        self.trials_tired = 5
        self.tired = False
        self.stage = 1
        self.substage = 0
        self.response_duration = 60
        self.image_display = 3        #Number of seconds the image will display after correct and incorrect
        # self.punish_intro = 0.6     #If they do 60% correct trials prvious 10 trials, punish is introduced (40Khz tone, negatively associated) where they do not get any water

        # accuracy limits for changing something later on:
        #self.acc_up = 0.85
        #self.acc_down = 0.4

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 2  # Normal water delivery of 25ul.
        #self.valve_factor_i = 0.6  # Water delivery for incorrects/punish

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.touch_outside = 0
        self.reward_drunk = 0
        #self.running_window = 10  # This is the number of trials the accuracy is measured by. It will take accuracy for every 10 trials.
        self.accwindow = [0]
        self.correct_count = 0
        self.accuracy = 0

        # Image output stims:
        self.stim = [0]  # Calls function 25 to display Blue 1.png and function 26 to display Blue 2.png respectively.

        # Correcth location and size:
        self.x_correcth_pos = [95, 281]  # Positions of the stim on the screen
        self.x_correcth = 0
        self.x_incorrecth = 0
        self.y_correcth = 110
        self.width = 100  # Stimulus width in mm
        self.height = 190

        #Required for Weber's law:
        self.block = 0  # This is the number of trials one conditions will remain for
        self.conditions = []  # Takes the conditions from select task file.
        self.completed_conditions = []  # To store completed conditions
        self.current_condition = 0  # To track the current condition in progress
        self.repetition = 0  # To store how many times the conditions needs to repeat.
        self.current_repetition = 0  # To store how many times the condition has repeated.
        self.trial_counter = 0  # Track the number of trials for the current condition
        # Image output stims:
        self.stim_trial = 0
        self.stim_trials = []
        self.stim_trial_counter = 0

    def configure_gui(self):
        self.gui_input = ['duration_max']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))


        ############ STATE MACHINE ################
        #First trial:
        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={'Port2In': 'Real_start'},
                output_actions=[])

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 4,
                state_change_conditions={Bpod.Events.Tup: 'Blank1'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # close corridor 2 door, and deliver water when animal enter to behav box

            self.sma.add_state(
                state_name='Blank1',
                state_timer=1,
                state_change_conditions={Bpod.Events.Port1In: 'Reward1'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5)])

            self.sma.add_state(
                state_name='Reward1',
                state_timer=self.valve_time * 4,
                state_change_conditions={Bpod.Events.Tup: 'Blank2'},
                output_actions=[(Bpod.OutputChannels.Valve, 1)])

            self.sma.add_state(
                state_name='Blank2',
                state_timer=1,
                state_change_conditions={Bpod.Events.Port1In: 'Reward2'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5)])

            self.sma.add_state(
                state_name='Reward2',
                state_timer=self.valve_time * 4,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.Valve, 1)])

        #Other Trials:
        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Wait_for_fixation'},
                output_actions=[])

        self.sma.add_state(
            state_name='Wait_for_fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Fixation'},
            output_actions=[])
        # Does Nothing. Make it close door 3 later when Duncan has fixed it.

        self.sma.add_state(
            state_name='Fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[])
        # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):

        ############ REGISTER VALUES ################
        self.register_value('reward_drunk', self.reward_drunk)