# Edited March 2025 for General Touchscreen Training

from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random


class Test_Touch(Task):

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
        self.duration_max = 3000  # Maximum duration of the task. 50 mins
        self.duration_min = 2100  # Minimum duration of the task. 35 mins.
        self.duration_tired = 1800  # Duration for the door to open (30 mins) if the animal is inactive. Less than 5 trials.
        self.response_duration = 120  # 2 min
        self.stim_duration = self.response_duration

        # screen details
        self.x_correcth_pos = 0  # screen width is 401mmm. For Stage 2, x position is randomised, below
        self.y_correcth_pos = 0  # screen height is 250mmm (randomise this??)
        self.width = 0
        self.height = 0
        self.x_incorrecth = None  # Incorrecth coordinate
        self.contrast = 0.4  # contrast of the stim. 0 black, 1 gray, 2 white. Default 40%

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 3.0  # More reward for correct. 2.0 = 50uL
        # self.valve_factor_i = 0.0 #Less reward for misses

        # counters
        self.reward_drunk = 0  # how many uLs they have received in the session

        # Needed in Each Task:
        self.stage = 1  # Current stage within the task
        self.substage = 0  # Current substage within the stage
        # self.task_number = 0  # Each task has a unique number. See RV script guide.

        # Needed to create blocks of 40 trials for criterion to be assessed on:
        self.block_size = 40  # The number of trials in a block
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

        self.trial_length = 0

        # Sound Variables:
        self.reward_frequency = 0

        # Variables for x positions:
        self.min_x_mm = 112
        self.max_x_mm = settings.WIN_SIZE[0] - 112  # screen width in mm - 60 mm margin
        self.screen_third = (self.max_x_mm - self.min_x_mm) // 3  # 1/3rd of the screen
        self.x_zone_trials = []  # stores zone (1,2,3) for each trial in current block
        self.current_x_zone = None
        self.zone_min = None
        self.zone_max = None

        self.y_value_trials = []  # This is to randomise the y trials
        self.y_choices = [190, 202, 215]  # Y-correcth positions to randomise with

    # def generate_non_repeating_block(self, values, block_size=40):
    #     sequence = []
    #     while len(sequence) < block_size:
    #         candidate = random.choice(values)
    #         if len(sequence) >= 2 and sequence[-1] == sequence[-2] == candidate:
    #             continue  # Skip if would cause 3 in a row
    #         sequence.append(candidate)
    #     return sequence

    def generate_non_repeating_block(self, values, block_size=40):
        from collections import Counter

        # Calculate how many times each value should appear
        base_count = block_size // len(values)
        remainder = block_size % len(values)

        # Create balanced pool
        pool = []
        for i, v in enumerate(values):
            count = base_count + (1 if i < remainder else 0)
            pool.extend([v] * count)

        # Shuffle until valid (no >2 repeats)
        max_attempts = 1000
        for _ in range(max_attempts):
            random.shuffle(pool)
            valid = True
            for i in range(2, len(pool)):
                if pool[i] == pool[i - 1] == pool[i - 2]:
                    valid = False
                    break
            if valid:
                return pool

        raise ValueError("Unable to generate non-repeating block with balanced values")

    def configure_gui(self):  # Variables that appear in the GUI
        self.gui_input = ['stage']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        if self.stage == 1:
            self.stim = 201
            self.x_correcth_pos = settings.CENTRE_SCREEN[0]  # 640 = center of the screen. Screen width is 401mmm
            self.y_correcth_pos = settings.CENTRE_SCREEN[1]  # 640 = center of the screen. Screen height is 250mmm
            self.width = settings.WIN_RESOLUTION[0]
            self.height = settings.WIN_RESOLUTION[1]

        elif self.stage == 2:
            if self.block_trial_counter == 0 or len(self.x_zone_trials) < 1:
                self.x_zone_trials = self.generate_non_repeating_block([1, 2, 3])
                print("x_zone_trials:", self.x_zone_trials)

            # X: get current_x_zone and convert to x position
            self.current_x_zone = self.x_zone_trials[self.block_trial_counter]

            self.zone_min = self.min_x_mm + (self.current_x_zone - 1) * self.screen_third
            self.zone_max = self.zone_min + self.screen_third
            self.x_correcth_pos = random.randint(self.zone_min, self.zone_max)

            self.stim = 202

            # Y fixed: 20 cm (200 mm) from top → translate to coordinate system where Y=0 is top
            self.y_correcth_pos = 152  # in mm
            self.width = 75
            self.height = 75

        elif self.stage == 3:
            if self.block_trial_counter == 0 or len(self.x_zone_trials) < 1:
                self.x_zone_trials = self.generate_non_repeating_block([1, 2, 3])
                self.y_value_trials = self.generate_non_repeating_block(self.y_choices)
                print("x_zone_trials:", self.x_zone_trials)
                print("y value trials:", self.y_value_trials)

            # X: get current_x_zone and convert to x position
            self.current_x_zone = self.x_zone_trials[self.block_trial_counter]

            self.zone_min = self.min_x_mm + (self.current_x_zone - 1) * self.screen_third
            self.zone_max = self.zone_min + self.screen_third
            self.x_correcth_pos = random.randint(self.zone_min, self.zone_max)

            # Y: use predefined value directly
            self.y_correcth_pos = self.y_value_trials[self.block_trial_counter]

            self.stim = 202
            self.width = 60
            self.height = 60

            # # Screen margin limits in mm

            # # Random X position within margins
            # self.x_correcth_pos = random.randint(self.min_x_mm, self.max_x_mm)
            # # Y fixed: 20 cm (200 mm) from top → translate to coordinate system where Y=0 is top
            # self.y_correcth_pos = random.choice([140, 152, 165])

        print("Zone: ", self.current_x_zone)
        print("X: ", self.x_correcth_pos)
        print("Y: ", self.y_correcth_pos)
        print("Width: ", self.width)
        print("Height: ", self.height)
        print("stim: ", self.stim)

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.SoftCode, self.stim)])

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
            state_change_conditions={Bpod.Events.Tup: 'Stimulus_Display'},
            output_actions=[])

        self.sma.add_state(
            state_name='Stimulus_Display',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},  # starts the response window
            output_actions=[(Bpod.OutputChannels.SoftCode, self.stim)])  # shows the stimuli

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration,
            state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 204)])  # function 204 defines the active touch area of our stims

        self.sma.add_state(
            state_name='Correct',
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 220)])
        # waterLED and RWsound remain ON until poke

        self.sma.add_state(
            state_name='Correct_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 222)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 12)])
        # waterLED ON, global LED ON

        self.sma.add_state(
            state_name='Touch_Outside',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[])
        # Goes back to response window in case of touch outside the two jar areas

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):
        self.block_trial_counter = (self.block_trial_counter + 1) % 40

        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0:
            self.trial_result = 'miss'
        elif self.current_trial_states['Correct'][0][0] > 0:
            self.trial_result = 'correct'

        self.trial_length = self.current_trial_states['Exit'][0][0] - self.current_trial_states['Start_task'][0][0]
        # print('Trial length: ' + str(self.trial_length))

        ############ REGISTER VALUES ################
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y_correcth_pos', self.y_correcth_pos)
        self.register_value('current_x_zone', self.current_x_zone)
        self.register_value('zone_min', self.zone_min)
        self.register_value('zone_max', self.zone_max)
        self.register_value('x_zone_trials', self.x_zone_trials)
        self.register_value('valve_factor_c', self.valve_factor_c)

        # Trial Information:
        self.register_value('trial_length', self.trial_length)
        self.register_value('trial_result', self.trial_result)
