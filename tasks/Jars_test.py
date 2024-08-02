from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Jars_test(Task):
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
        self.substage = 1
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
        self.x1 = 60
        self.x2 = 290
        self.x_positions = [60, 290]  #Positions of the stim on the screen

        self.run = []
        self.time_on = 10
        self.time_off = 10

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
        if self.current_trial == 0:  # Make a list with x values
            self.block_size = int(self.block_size)

            # Randomizing the probabilities for both images:
            self.x1_trials = random.choices(self.x_positions, k=1000)
            self.x2_trials = random.choices(self.x_positions, k=1000)

            # Ensure x2_trials is not identical to x1_trials
            while self.x2_trials == self.x1_trials:
                self.x2_trials = random.choices(self.x_positions, k=1000)

            print('x1 positions list: ' + str(self.x1_trials))
            print('x2 positions list: ' + str(self.x2_trials))

        # Choose x1 and x2 for the function:
        #self.x1 = self.x1_trials[self.current_trial]
        self.x1 = 60
        #self.x2 = self.x2_trials[self.current_trial]
        self.x2 = 290

        # Correction bias:
        if self.correction_bias == 1:
            if self.trial_result == 'punish':
                self.x1 = self.last_x1
                self.x2 = self.last_x2
                print('Correction trial, x1 position:' + str(self.x1))
                print('Correction trial, x2 position:' + str(self.x2))
        print('x1 position:' + str(self.x1))
        print('x2 position:' + str(self.x2))

        self.sma.set_global_timer(timer_id=1, timer_duration=self.time_on)

        self.sma.add_state(
            state_name='Display_1',
            state_timer=self.time_on,
            state_change_conditions={Bpod.Events.Tup: 'Display_off1'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 6)]
        )

        self.sma.add_state(
            state_name='Display_off1',
            state_timer=self.time_off,
            state_change_conditions={Bpod.Events.Tup: 'Display_2'},
            output_actions=[]
        )

        self.sma.add_state(
            state_name='Display_2',
            state_timer=self.time_on,
            state_change_conditions={Bpod.Events.Tup: 'Display_off2'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 7)]
        )

        self.sma.add_state(
            state_name='Display_off2',
            state_timer=self.time_off,
            state_change_conditions={Bpod.Events.Tup: 'Display_3'},
            output_actions=[]
        )

        self.sma.add_state(
            state_name='Display_3',
            state_timer=self.time_on,
            state_change_conditions={Bpod.Events.Tup: 'Display_off3'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 9)]
        )

        self.sma.add_state(
            state_name='Display_off3',
            state_timer=self.time_off,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[]
        )

    def after_trial(self):
        self.runs.append(self.current_trial)
        self.register_value('time_on', self.time_on)
        self.register_value('time_off', self.time_off)
        self.register_value('runs', self.runs[self.current_trial])
