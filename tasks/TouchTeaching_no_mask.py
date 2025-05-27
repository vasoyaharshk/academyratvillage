# Edited March 2025 for General Touchscreen Training

from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random


class TouchTeaching_no_mask(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Mice learn to touch the screen during the response window to obtain the reward.
        Animals crossing the end of the corridor trigger the stimulus presentation in all holes and response window onset. 
        Screen touches during response window deliver reward.
        Stimulus low contrast to not scare animals
        
        Stages:
        Stage 1: A big white rectangle covering the whole screen
        Stage 2: A smaller rectangle at the bottom half of the screen.
        Stage 3: 

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED

        """

    def init_variables(self):
        # general
        self.duration_min = 1800  # 30 mins   # minimum session duration
        self.duration_max = 2100  # 35 mins   # max
        self.stage = 1
        self.substage = 0
        self.response_duration = 120  # 2 min
        self.stim_duration = self.response_duration

        # screen details
        self.x_correcth_pos = 0  # screen width is 401mmm. For Stage 2, x position is randomised, below
        self.y_correcth_pos = 0  # screen height is 250mmm (randomise this??)
        self.width = 0
        self.height = 0
        self.x_incorrecth = 0  # Incorrecth coordinate
        self.contrast = 0.4  # contrast of the stim. 0 black, 1 gray, 2 white. Default 40%

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 2.0  # More reward for correct. 2.0 = 50uL
        #self.valve_factor_i = 0.0 #Less reward for misses

        # counters
        self.reward_drunk = 0  # how many uLs they have received in the session

        # Needed in Each Task:
        self.stage = 0  # Current stage within the task
        self.substage = 0  # Current substage within the stage
        # self.task_number = 0  # Each task has a unique number. See RV script guide.

        # Needed to create blocks of 40 trials for criterion to be assessed on:
        self.block_size = 0  # The number of trials in a block
        self.block_trial_counter = 0  # Trial count within the current block
        self.block_accuracy = 0.0  # Accuracy in the current block
        self.block_number = 0  # Sequential block number
        self.block_change = 0  # If it is 1, a new block will start on the next trial
        self.total_trials = 0  # Total trials across the task.
        self.block_correct_count = 0  # Number of correct responses in the block
        self.block_valid_count = 0  # Number of valid (non-missed) trials in the block
        self.last_forward_stage = 0  # The stage moved forward from after a forward change
        self.last_backward_stage = 0  # The stage moved backward to after the last backward change
        self.moved_back_counter = 0  # Counter for how many times the subject moved back a stage
        self.stage_forward_change = 0  # Whether stage move forward on the next trial
        self.stage_backward_change = 0  # Whether stage move backward on the next trial

        # Left Right Function Randomisation variables:
        self.stim_trial = 0  # The function number of the correct stimulus in the current trial. This designates trial type, e.g. from Discrim. C: left is correct, big jar is correct, spacer in correct
        self.stim_trials = []  # List of correct stimulus function randomised.
        self.stim_trial_counter = 0  # It counts the number of trials within a randomization block. Doesnt change when Bias breaking is active.
        self.last_stim_trial = 0  # the function of the last trial of the previous block. Used to ensure first trial of next block is different
        self.stim = [0]

    def configure_gui(self):  # Variables that appear in the GUI
        self.gui_input = ['stage']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        if self.stage == 1:
            self.stim = 201
            self.x_correcth_pos = 640  # 640 = center of the screen. Screen width is 401mmm
            self.y_correcth_pos = 512  # 640 = center of the screen. Screen height is 250mmm
            self.width = settings.WIN_SIZE[0] * 2
        elif self.stage == 2:
            self.stim = 202
            self.x_correcth_pos = random.randint(65, 325)  # Screen width is 401mmm
            self.y_correcth_pos = 110  # 640 = center of the screen. Screen height is 250mmm
            self.width = 125
            self.height = 125
        elif self.stage == 3:
            self.stim = 203
            self.x_correcth_pos = random.randint(33,357)  # Screen width is 410mmm. We minus 10 on each end to account for mask
            self.y_correcth_pos = random.randint(43,82)  # 640 = center of the screen. Screen height is 250mmm. We minus 10 on each end to account for mask
            self.width = 65
            self.height = 65

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                output_actions=[])

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 2,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # close corridor door 2 when subject enter to the behav box

        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[])  # because there's nothing in the brackets, this does nothing

        self.sma.add_state(
            state_name='Wait_for_fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port6In: 'Stimulus_Display'},
            # when the last photogate is crossed, the stimulus is displayed
            output_actions=[])

        self.sma.add_state(
            state_name='Stimulus_Display',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},  # starts the response window
            output_actions=[(Bpod.OutputChannels.SoftCode, self.stim)])  #
        # show 3 stimuli when crossing end of corridor

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode3': 'Miss', Bpod.Events.Tup: 'Miss'},
            output_actions=[
                (Bpod.OutputChannels.SoftCode, 204)])  # function 204 defines the active touch area of our stims

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
        # waterLED and RWsound remain ON until poke

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 12)])
        # waterLED ON, global LED ON

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):
        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0:  # Missed trial
            self.register_value('trial_result', 'miss')
        else:
            self.register_value('trial_result', 'correct')  # Correct trial
            self.reward_drunk += self.valve_reward * self.valve_factor_c


        ############ REGISTER VALUES ################
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y_correcth_pos', self.y_correcth_pos)

        #Trial Information:
        self.register_value('trial_length', self.trial_length)
        self.register_value('trial_result', self.trial_result)
