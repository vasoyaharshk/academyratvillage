from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
from collections import Counter


class StageTraining_8B_V2(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        --> Update: Opto TTLs included, states--> 0: corridor; 1: response; 2: reward; 3: all

        Stage 1: Stimulus categorization. 
        # Sb1: Repoking allowed; 
        # Sb2: Punish introduced; 
        # Sb3: Data collection.
        Stage 2: Data Collection opto. 

        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - BUZZER: valve (16kHz): correct; LED (4kHz):punish
        Port 3 - PHOTOGATES 4: Photogates end of corridor
        Port 4 - PHOTOGATES 0: Photogates next to lickport & Global LED
        PAm  1 - PHOTOGATES 1: Photogates start of corridor           
        PAm  2 - PHOTOGATES 2: Photogates midle-start of corridor
        PAm  3 - PHOTOGATES 3: Photogates midle-end of corridor     
        """

    def init_variables(self):
        # general
        self.duration_max = 4500    #  1:15 min finished the task
        self.duration_min = 2100    #  35 min door opens
        self.duration_tired = 1800  # 30 mins if animal sleeping last 10 mins, finishes task
        self.trials_tired = 5  # if animal does less than this number in the last 10 mins, finishes task
        self.tired = False  # Tired animal indicator
        self.silent_on = 0
        self.mask = 3
        self.choices = 3
        self.target = 1 #0:L, 1:C, 2:R
        self.block_size = 20
        self.prob = 0.8
        self.stage = 3
        self.substage = 2

        # task variables: by default easy parameters
        self.response_duration = 60
        self.correction_bias = 0
        self.punish_intro = 0.55

        # stimulus duration extra in each ttype
        self.stim_duration = 0
        self.stim_dur_ds = 0
        self.stim_dur_dm = 0
        self.stim_dur_dl = 0

        # accuracy limits for changing stim_dur
        self.acc_up = 0.6
        self.acc_down = 0.4

        # trial types probabilies
        self.pvg = 1
        self.pds = 0
        self.pdm = 0
        self.pdl = 0
        self.trial_type = 'VG'

        # screen details
        self.x = 0  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30  # stimulus width
        self.correct_th = 130  # 1/3 of the screen
        self.repoke_th = settings.WIN_SIZE[0] * 2  # full screen
        self.contrast = 1.2  # 0 black, 1 gray, 2 white. Default 60%

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water # 10ul per trial normal conditions
        self.valve_factor_c = 1
        self.valve_factor_i = 0.45

        # optogenetics parameters
        self.opto_state = 3  # 0: corridor, 1: response, 2: reward, 3: all
        self.opto_bool = 0
        self.opto_on = 0

        # counters
        self.valid_counter = 0
        self.tired_counter = 0
        self.reward_drunk = 0
        self.running_window = 10
        self.accwindow = [0] * self.running_window  # Vector to store accuracy, continuously updated eliminating previous trials.
        self.vg_accwindow = [0] * self.running_window
        self.ds_accwindow = [0] * self.running_window
        self.dm_accwindow = [0] * self.running_window
        self.dl_accwindow = [0] * self.running_window


    def configure_gui(self): # Variables appearing in the GUI
        self.gui_input = ['stage', 'substage', 'mask', 'duration_max', 'correction_bias',
                          'stim_dur_ds', 'stim_dur_dm', 'stim_dur_dl', 'choices',
                          'target', 'block_size', 'prob', 'opto_state', 'silent_on', 'opto_on']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # Register initial values
        if self.current_trial == 0:
            self.init_stim_dur_ds = self.stim_dur_ds
            self.init_stim_dur_dm = self.stim_dur_dm
            self.init_stim_dur_dl = self.stim_dur_dl

        # Acuracy by trial type
        self.accuracy = sum(self.accwindow) / len(self.accwindow)
        self.vg_accuracy = sum(self.vg_accwindow) / len(self.vg_accwindow)
        self.ds_accuracy = sum(self.ds_accwindow) / len(self.ds_accwindow)
        self.dm_accuracy = sum(self.dm_accwindow) / len(self.dm_accwindow)
        self.dl_accuracy = sum(self.dl_accwindow) / len(self.dl_accwindow)
        print("Global Accuracy: " + str(self.accuracy))
        print("VG Accuracy: " + str(self.vg_accuracy))
        print("DS Accuracy: " + str(self.ds_accuracy))
        print("DM Accuracy: " + str(self.dm_accuracy))
        print("DL Accuracy: " + str(self.dl_accuracy))

        ############ VARIABLES BY STAGE ################

        ####### STAGE 1: STIMULUS CATEGORIZATION ######
        if self.stage == 1:
            self.duration_tired = 1800  # 30 mins

            if self.substage == 1:  # SUBSTAGE 1: REPOKING ALLOWED, LONG RESP WIN, MORE WATER, HIGH PROB BLOCKS
                self.valve_factor_c = 1.2
                self.valve_factor_i = 0.6

            if self.substage == 2:  # SUBSTAGE 2: SHORTER RESPONSE WIN, LESS WATER, MED PROB BLOCKS
                self.response_duration = 30
                self.prob = 0.7

            elif self.substage == 3:  # SUBSTAGE 3: PUNISH INTRODUCTION, LOW PROB BLOCKS
                self.response_duration = 30
                self.prob = 0.5
                if self.current_trial >= 10:
                    self.repoke_th = self.correct_th

            elif self.substage == 4:  # SUBSTAGE 4: NO MORE BLOCKS
                self.prob = 0.33
                if self.current_trial >= 10:
                    self.repoke_th = self.correct_th
                    self.response_duration = 20

        else:
            self.prob = 0.33
            # Easy trials: All VG and repoking allowed
            if self.current_trial == 8:
                self.response_duration = 20
                self.repoke_th = self.correct_th  # no more repoking allowed
                self.stim_dur_ds = self.init_stim_dur_ds

            ####### STAGE 2: DELAY SHORT TEACHING  #######
            if self.stage == 2 and self.substage == 1 and self.current_trial > 8:  # SUBSTAGE 1: DS INTRODUCTION
                self.pvg = 0.7
                self.pds = 0.3
                self.correction_bias = 1 # Repeat prev stim position if punish
                self.stim_dur_ds = 0.5

            elif self.stage == 2 and self.substage == 2 and self.current_trial > 8: # SUBSTAGE 2: DS CONSOLIDATION
                self.pvg = 0.4
                self.pds = 0.6
                self.correction_bias = 0  # Repeat prev stim position if punish
                # from trial 20 start reducing stimulus duration of DS
                if self.current_trial >= 20 and self.current_trial % self.running_window == 0:
                    if self.accuracy >= self.acc_up and self.stim_dur_ds > 0.05:
                        self.stim_dur_ds -= 0.05
                        print('more difficult!')
                    elif self.accuracy <= self.acc_down and self.stim_dur_ds < self.init_stim_dur_ds:
                        self.stim_dur_ds += 0.075
                        print('easier!')

            ####### STAGE 3: DATA COLLECTION  #######
            elif self.stage == 3 and self.current_trial > 8:
                self.stim_dur_ds = 0
                self.stim_dur_dm = 0
                self.stim_dur_dl = 0
                self.correction_bias = 0
                self.response_duration = 15
                if self.substage==1:
                    self.pvg = 0.2
                    self.pds = 0.8
                elif self.substage ==2:
                    self.pvg = 0.2
                    self.pds = 0.4
                    self.pdm = 0.4
                elif self.substage ==3:
                    self.pvg = 0.2
                    self.pds = 0.4
                    self.pdl = 0.4



        ############ CHANGING VARIABLES ################

        ### STIMULUS POSITIONS
        # Possible positions (screen is 0-400 mm)
        self.x_positions = [60, 200, 340]

        # Choose x positions by blocks
        if self.current_trial == 0:  # Make a list with x values
            self.block_size = int(self.block_size)

            ## Create a pseudorandom serie with 3 choices (0:Left, 1:Centre, 2:Right)
            if self.choices == 3:
                if self.prob == 0.33:  # random
                    self.x_trials = random.choices(self.x_positions, k=1000)
                    print('random')
                else:  # blocks
                    other_prob = (1 - self.prob) / 2
                    p_list = [other_prob] * 3
                    block_combinations = ['012', '021', '102', '120', '210', '201']
                    block_serie = np.random.choice(block_combinations)
                    for i in range(10):
                        next_block = np.random.choice(block_combinations)
                        while block_serie[-1] == next_block[0]:
                            next_block = np.random.choice(block_combinations)
                            if block_serie[-1] != next_block[0]:
                                break
                        block_serie = block_serie + next_block
                    # create block of trials following the prev serie
                    for idx, i in enumerate(block_serie):
                        p = p_list.copy()
                        p[int(i)] = self.prob
                        if idx == 0:
                            self.x_trials = (np.random.choice(self.x_positions, size=self.block_size, p=p)).tolist()
                        else:
                            self.x_trials = self.x_trials + (np.random.choice(self.x_positions, size=self.block_size, p=p)).tolist()
                    print('x pobs: ' + str(p))
                print('x positions list: ' + str(self.x_trials))

            # Blocks of 2 choices #change
            elif self.choices == 2:
                start = np.random.choice(self.x_positions)
                end = np.random.choice(list(set(self.x_positions).difference(start)))
                order = [start, end]
                self.x_trials = [order[0]] * self.block_size + [order[1]] * self.block_size
                for i in range(20):
                    self.x_trials = self.x_trials + [order[0]] * self.block_size + [order[1]] * self.block_size
                print('x positions list: ' + str(self.x_trials))

            # 1 choice all the session
            elif self.choices == 1:
                try:
                    p = [0.1, 0.1, 0.1]
                    p[int(self.target)] = 0.8
                except:
                    p = [0.1, 0.8, 0.1]  # center choice by default
                self.x_trials = (np.random.choice(self.x_positions, size=1000, p=p)).tolist()
                print('x positions list: ' + str(self.x_trials))

            else:
                print('Incorrect number of choices')

        # Choose x
        self.x = self.x_trials[self.current_trial]
        # Correction bias extension
        if self.correction_bias == 1 and self.current_trial > 0:
            if self.trial_result == 'punish':
                self.x = self.last_x
                print('Correction trial, x position:' + str(self.x))
        print('x position:' + str(self.x))


        ### CHOOSE TRIAL TYPE
        sum_probs = self.pvg + self.pds + self.pdm + self.pdl
        probs_ttypes = [self.pvg / sum_probs, self.pds / sum_probs, self.pdm / sum_probs, self.pdl / sum_probs]
        self.trial_type = np.random.choice(['VG', 'DS', 'DM', 'DL'], p=probs_ttypes)
        print('Trial probs: ' + str(self.pvg) + str(self.pds))
        print('Trial type: ' + str(self.trial_type))
        print('Stim dur DS: ' + str(self.stim_dur_ds))

        # conditions depending on trial type:
        # 0 no function called; 1 show stim with timer; 2 show stim infinite time; 3 stop stim and clear cam tags
        if self.trial_type == 'VG':
            self.stim_duration = self.response_duration
            output_stim1 = 2  # show stimulus initially
            output_stim2 = 0
            output_stim3 = 0
            output_stim4 = 1  # turn off stim at the eng of Resp Win
        elif self.trial_type == 'DS':
            self.stim_duration = self.stim_dur_ds
            output_stim1 = 2  # show stimulus initially
            output_stim2 = 0
            output_stim3 = 0
            output_stim4 = 1  # turn off stim in the Resp Win
        elif self.trial_type == 'DM':
            self.stim_duration = self.stim_dur_dm
            output_stim1 = 2  # show stimulus initially
            output_stim2 = 0
            output_stim3 = 1  # turn off stim in fixation 3
            output_stim4 = 15
        elif self.trial_type == 'DL':
            self.stim_duration = self.stim_dur_dl
            output_stim1 = 2  # show stimulus initially
            output_stim2 = 1  # turn off stim in fixation 2
            output_stim3 = 15
            output_stim4 = 0

        # silent trials
        if self.silent_on == 1 and self.stage == 3 and self.current_trial > 8:
            self.y = np.random.choice([125, 1000], p=[0.95, 0.05])  # 5% trials stimulus doesn't appear
            if self.y == 1000:
                print('Silent trial')

        ### CHOOSE OPTO STIMULATION --> 0: stimulus, 1: response, 2: reward, 3: all
        output_laser_start = 0
        output_laser_corr = 0
        output_laser_resp = 0
        output_laser_rew = 0

        if self.current_trial > 8 and self.opto_on==1:
            self.laser = np.random.choice([0, 1], p=[0.8, 0.2])  # 20% trials laser ON
            if self.laser == 1:
                if self.opto_state == 0: # corridor state
                    output_laser_start = 3
                    output_laser_corr = 3
                elif self.opto_state == 1: # response state
                    output_laser_resp = 3
                elif self.opto_state == 2: # reward state
                    output_laser_rew = 3
                elif self.opto_state == 3: # all: corridor + response states
                    output_laser_start = 3
                    output_laser_corr = 3
                    output_laser_resp = 3
                self.opto_bool = 1
                print('LASER STIMULATION!')
            else:
                self.opto_bool =0


        ############ STATE MACHINE ################

        # Only the first trial
        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={'Port4In': 'Real_start'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 2)])
            # show stim inifite time

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 2,
                state_change_conditions={Bpod.Events.Tup: 'Fixation1'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # close corridor 2 door, and deliver water when animal enter to behav box

        # Other trials
        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={'PA1_Port1In': 'Fixation1'},
                output_actions=[(Bpod.OutputChannels.BNC1, output_laser_rew)])

        self.sma.add_state(
            state_name='Fixation1',
            state_timer=0,
            state_change_conditions={'PA1_Port2In': 'Fixation2'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim1), (Bpod.OutputChannels.BNC1, output_laser_start)])
        # show stimulus now

        self.sma.add_state(
            state_name='Fixation2',
            state_timer=0,
            state_change_conditions={'PA1_Port3In': 'Fixation3'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim2), (Bpod.OutputChannels.BNC1, output_laser_corr)])

        self.sma.add_state(
            state_name='Fixation3',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port3In: 'Pre_Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim3), (Bpod.OutputChannels.BNC1, output_laser_corr)])

        self.sma.add_state(
            state_name='Pre_Response_window',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim4)])
        # show stimulus with timer: VG until RW ends, WMI defined by stim_dur_ds

        self.sma.add_state(
            state_name='Response_window',
            state_timer= 3,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect', 'SoftCode3': 'Miss',
                                     'SoftCode4': 'Punish', Bpod.Events.Tup: 'Response_window_finish'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4),(Bpod.OutputChannels.BNC1, output_laser_resp)])
        # wait for subject response

        self.sma.add_state(
            state_name = 'Response_window_finish',
            state_timer = self.response_duration + 7,
            state_change_conditions = {'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect', 'SoftCode3': 'Miss',
                                   'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions = [(Bpod.OutputChannels.SoftCode, 4) , (Bpod.OutputChannels.BNC1, 0)])
        # wait for subject response

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.Valve, 2),
                            (Bpod.OutputChannels.SoftCode, 11)])
        # waterLED and correct sound remain ON until poke

        self.sma.add_state(
            state_name='Miss',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port4In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 4),
                            (Bpod.OutputChannels.SoftCode, 12)])
        # waterLED ON, global LEDs ON

        self.sma.add_state(
            state_name='Punish',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'After_punish'},
            output_actions=[(Bpod.OutputChannels.LED, 2), (Bpod.OutputChannels.LED, 4),
                            (Bpod.OutputChannels.SoftCode, 14)])
        # Incorrect sound, global LEDs on

        self.sma.add_state(
            state_name='After_punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port1Out: 'Miss_reward',
                                     Bpod.Events.Port4In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 4)])
        # waterLED ON & global LEDs ON

        self.sma.add_state(
            state_name='Incorrect',
            state_timer=0.25,
            state_change_conditions={Bpod.Events.Tup: 'Response_window2'},
            output_actions=[(Bpod.OutputChannels.LED, 2), (Bpod.OutputChannels.SoftCode, 13)])
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
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.Valve, 2),
                            (Bpod.OutputChannels.SoftCode, 11)])
        # waterLED and correct sound remain ON until poke

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15), (Bpod.OutputChannels.BNC1, output_laser_rew)])

        self.sma.add_state(
            state_name='Correct_other_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15), (Bpod.OutputChannels.BNC1, output_laser_rew)])

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15), (Bpod.OutputChannels.BNC1, output_laser_rew)])

        self.sma.add_state(
            state_name='Exit',  # Doors closure when trial ends
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.BNC1, 0), (Bpod.OutputChannels.BNC1, output_laser_rew)])

    def after_trial(self):
        ############ TRIAL COUNTER ################

        ##### COUNT MISSES
        if self.current_trial_states['Miss'][0][0] > 0:  # misses & incorrects modify the acc
            self.accwindow = self.accwindow[1:] + [0]
            if self.trial_type == 'VG':
                self.vg_accwindow = self.vg_accwindow[1:] + [0]
            elif self.trial_type == 'DS' or self.trial_type == 'DSc1' or self.trial_type == 'DSc2':
                self.ds_accwindow = self.ds_accwindow[1:] + [0]
            elif self.trial_type == 'DM' or self.trial_type == 'DMc1':
                self.dm_accwindow = self.dm_accwindow[1:] + [0]
            elif self.trial_type == 'DL':
                self.dl_accwindow = self.dl_accwindow[1:] + [0]
            if self.current_trial_states['Incorrect'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.valid_counter += 1
            else:
                self.trial_result = 'miss'

        ##### COUNT PUNISH
        elif self.current_trial_states['Punish'][0][0] > 0:
            self.trial_result = 'punish'
            self.valid_counter += 1
            self.accwindow = self.accwindow[1:] + [0]
            if self.trial_type == 'VG':
                self.vg_accwindow = self.vg_accwindow[1:] + [0]
            elif self.trial_type == 'DS' or self.trial_type == 'DSc1' or self.trial_type == 'DSc2':
                self.ds_accwindow = self.ds_accwindow[1:] + [0]
            elif self.trial_type == 'DM' or self.trial_type == 'DMc1':
                self.dm_accwindow = self.dm_accwindow[1:] + [0]
            elif self.trial_type == 'DL':
                self.dl_accwindow = self.dl_accwindow[1:] + [0]

        ##### COUNT CORRECTS FIRST POKE
        elif self.current_trial_states['Correct_first'][0][0] > 0:
            self.trial_result = 'correct_first'
            self.valid_counter += 1
            self.reward_drunk += self.valve_reward * self.valve_factor_c
            self.accwindow = self.accwindow[1:] + [1]
            if self.trial_type == 'VG':
                self.vg_accwindow = self.vg_accwindow[1:] + [1]
            elif self.trial_type == 'DS' or self.trial_type == 'DSc1' or self.trial_type == 'DSc2':
                self.ds_accwindow = self.ds_accwindow[1:] + [1]
            elif self.trial_type == 'DM' or self.trial_type == 'DMc1':
                self.dm_accwindow = self.dm_accwindow[1:] + [1]
            elif self.trial_type == 'DL':
                self.dl_accwindow = self.dl_accwindow[1:] + [1]

        ##### COUNT CORRECTS OTHER POKE
        else:
            self.trial_result = 'correct_other'
            self.valid_counter += 1
            self.reward_drunk += self.valve_reward * self.valve_factor_i
            self.accwindow = self.accwindow[1:] + [0]
            if self.trial_type == 'VG':
                self.vg_accwindow = self.vg_accwindow[1:] + [0]
            elif self.trial_type == 'DS' or self.trial_type == 'DSc1' or self.trial_type == 'DSc2':
                self.ds_accwindow = self.ds_accwindow[1:] + [0]
            elif self.trial_type == 'DM' or self.trial_type == 'DMc1':
                self.dm_accwindow = self.dm_accwindow[1:] + [0]
            elif self.trial_type == 'DL':
                self.dl_accwindow = self.dl_accwindow[1:] + [0]

        # End-trial calculations
        self.last_x = self.x
        self.trial_length = self.current_trial_states['Exit'][0][0] - self.current_trial_states['Start_task'][0][0]
        print('Trial lenght: ' + str(self.trial_length))

        ### Long trials
        if utils.chrono.get_seconds() >= self.duration_tired and self.trial_length > 45:
            self.tired_counter += 1
            if self.tired_counter > 2:
                self.tired = True
                print('Finishing task: subject tired')
        else:  # reset the counter
            self.tired_counter = 0

        ############ REGISTER VALUES ################
        self.register_value('x', self.x)
        self.register_value('y', self.y)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('mask', self.mask)
        self.register_value('choices', self.choices)
        self.register_value('width', self.width)
        self.register_value('correct_th', self.correct_th)
        self.register_value('repoke_th', self.repoke_th)
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)
        self.register_value('trial_type', self.trial_type)
        self.register_value('trial_result', self.trial_result)
        self.register_value('pvg', self.pvg)
        self.register_value('pds', self.pds)
        self.register_value('pdm', self.pdm)
        self.register_value('pdl', self.pdl)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('reponse_duration', self.response_duration)
        self.register_value('correction_bias', self.correction_bias)
        self.register_value('trial_length', self.trial_length)
        self.register_value('block_size', self.block_size)
        self.register_value('opto_bool', self.opto_bool)

