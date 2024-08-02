from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Probability_1(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task displays the image of the jars which are touchable.
        ########   TASK INFO   ########

        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - BUZZER: valve (16kHz): correct; LED (4kHz):punish
        Port 3 - PHOTOGATES 4: Photogates end of corridor
        Port 4 - PHOTOGATES 0: Photogates next to lickport & Global LED
        PAm  1 - PHOTOGATES 1: Photogates start of corridor           
        PAm  2 - PHOTOGATES 2: Photogates midle-start of corridor
        PAm  3 - PHOTOGATES 3: Photogates midle-end of corridor     

        """

        #Variables for the task:
        self.duration_max = 3000  # 50 min finished the task
        self.duration_min = 2100  # 35 min door opens
        self.duration_tired = 1800  # 30 mins if animal sleeping last 10 mins, finishes task
        self.trials_tired = 5  # if animal does less than this number in the last 10 mins, finishes task
        self.tired = False  # Tired animal indicator
        self.trials_max = 10
        self.mask = 3
        self.choices = self.mask
        self.block_size = 10
        self.stage = 1
        self.response_duration = 60
        self.correction_bias = 0
        self.punish_intro = 0.6

        # accuracy limits for changing something later on:
        self.acc_up = 0.6
        self.acc_down = 0.4

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water # 25ul per trial normal conditions
        self.valve_factor_c = 1    #Normal water delivery of 25ul.
        self.valve_factor_i = 0.6  #Water delivery for incorrects/punish

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.reward_drunk = 0
        self.running_window = 10
        self.accwindow = [0] * self.running_window  #Accuracy changes every 10 trials and is stored in this variable.

        #Screen details:
        self.y = 50 #height of the stimulus
        self.width = 120 #width of the stimulus
        self.correct_th = 200 #portion of the screen correct.
        self.repoke_th = settings.WIN_SIZE[0] * 2
        self.x = 0
        self.x_positions = [60, 290]  #Positions of the stim on the screen

        self.run = []
        self.time_on = 2
        self.time_off = 2

    def configure_gui(self):
        self.gui_input = ['trials_max', 'y', 'width']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # Accuracy for running trials:
        self.accuracy = sum(self.accwindow) / len(self.accwindow)
        print("Accuracy: " + str(self.accuracy))


        ### Randomizing the stimulus positions for both the images:
        # Choose x positions by blocks
        if self.stage == 1:
            if self.current_trial == 0:  # Make a list with x values
                self.block_size = int(self.block_size)

                # Randomizing the probabilities for both images:
                self.x_trials = random.choices(self.x_positions, k=1000)
                print('x positions list: ' + str(self.x_trials))

            self.x = self.x_trials[self.current_trial]

        else:
            if self.current_trial == 0:  # Make a list with x values
                self.block_size = int(self.block_size)

                # Randomizing the probabilities for both images:
                self.x_correct = random.choices(self.x_positions, k=1000)
                self.x_incorrect = random.choices(self.x_positions, k=1000)

                # Ensure x_correct and x_incorrect are not identical in the same trial
                while self.x2_trials == self.x_trials:
                    self.x2_trials = random.choices(self.x_positions, k=1000)

            print('x2 positions list: ' + str(self.x2_trials))

    # Choose x and x for the function:

    #self.x2 = self.x2_trials[self.current_trial]

        # Correction bias:
        if self.correction_bias == 1:
            if self.trial_result == 'punish':
                self.x = self.last_x
                print('Correction trial, x position:' + str(self.x))
        print('x position:' + str(self.x))

        self.sma.set_global_timer(timer_id=1, timer_duration=self.time_on)

        self.sma.add_state(
            state_name='Display_1',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 6)]
        )

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect', 'SoftCode3': 'Miss',
                                     'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4)])
        # wait for subject response

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect', 'SoftCode3': 'Miss',
                                     'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4)])
        # wait for subject response

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
        # waterLED and correct sound remain ON until poke

        self.sma.add_state(
            state_name='Miss',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port2In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 12)])
        # waterLED ON, global LEDs ON

        self.sma.add_state(
            state_name='Punish',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'After_punish'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 14)])
        # Incorrect sound, global LEDs on. Note: In the rat village, there is only one LED

        self.sma.add_state(
            state_name='After_punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port1Out: 'Miss_reward',
                                     Bpod.Events.Port2In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6)])
        # waterLED ON & global LEDs ON

        self.sma.add_state(
            state_name='Incorrect',
            state_timer=0.25,
            state_change_conditions={Bpod.Events.Tup: 'Response_window2'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 13)])
        # Incorrect sound

        self.sma.add_state(
            state_name='Response_window2',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_other', 'SoftCode2': 'Incorrect',
                                     'SoftCode3': 'Miss', 'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 5)])

        self.sma.add_state(
            state_name='Correct_other',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_other_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
        # waterLED and correct sound remain ON until poke

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])

        self.sma.add_state(
            state_name='Correct_other_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 17)])

        self.sma.add_state(
            state_name='Exit',  # Doors closure when trial ends
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

def after_trial(self):
    self.runs.append(self.current_trial)
    self.register_value('time_on', self.time_on)
    self.register_value('time_off', self.time_off)
    self.register_value('runs', self.runs[self.current_trial])
