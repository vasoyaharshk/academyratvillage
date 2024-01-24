from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np


class StageTraining_9B_V2(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        --> Update: Stimulus control trials as 7B
        --> Update: possibility to have trial blocks with same stimulus in stage 1


        Stage 1: Stimulus categorization. 
        # Sb1: 70%VG 30%DS Repoking allowed; 
        # Sb2: 70%VG 30%DS Punish introduced; 
        # Sb3: 40%VG 60%WMI Consolidation.
        Stage 2: Delay elongation
        # Sb1: 20%VG 80%DS Reduce stim duration after PH4 from 0.45 to 0  
        # Sb2: 10%VG 45%DS 45%DM Reduce stim duration after PH3 from 0.4 to 0  
        # Sb1: 10%VG 30%DS 30%DM Reduce stim duration after PH2 from 0.35 to 0  
        Stage 3: Data collection (silent trials can appear)

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
        self.duration_max = 3000  # 50 min finished the task
        self.duration_min = 2100  # 35 min door opens
        self.duration_tired = 1800  # 30 mins if animal sleeping last 10 mins, finishes task
        self.trials_tired = 5  # if animal does less than this number in the last 10 mins, finishes task
        self.tired = False  # Tired animal indicator
        self.silent = False
        self.mask = 3
        self.choices = 3
        self.blocks= True
        self.block_size = 20
        self.prob = 0.33 # random by default
        self.stage = 1
        self.substage = 1

        # task variables: by default easy parameters
        self.response_duration = 60
        self.correction_bias = 0
        self.punish_intro = 0.6

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
        self.pdsc1 = 0
        self.pdsc2 = 0
        self.pdmc1 = 0
        self.trial_type = 'VG'

        # screen details
        self.x = 0  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30  # stimulus width
        self.correct_th = 130  # 1/3 of the screen
        self.repoke_th = settings.WIN_SIZE[0] * 2  # full screen
        self.contrast= 1.2 #0 black, 1 gray, 2 white. Default 60%

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water # 10ul per trial normal conditions
        self.valve_factor_c = 1
        self.valve_factor_i = 0.45

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
                          'stim_dur_ds', 'stim_dur_dm', 'stim_dur_dl', 'silent', 'choices']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # Register initial values
        if self.current_trial == 0:
            self.init_stim_dur_ds = self.stim_dur_ds
            self.init_stim_dur_dm = self.stim_dur_dm
            self.init_stim_dur_dl = self.stim_dur_dl
            print('init DL:'+ str(self.init_stim_dur_dl))

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

            if self.blocks == True:  # Repeat if blocks allowed
                if self.substage==1:
                    self.prob = 0.75
                elif self.substage ==2:
                    self.prob = 0.55
                else:
                    self.prob = 0.33

            # SUBSTAGE 1: STIMULUS REPOKING ALLOWED, LONG RESP WIN, MORE WATER
            if self.substage == 1:
                self.valve_factor_c = 1.2
                self.valve_factor_i = 0.6
                # 10 initial easy trials: all VG
                if self.current_trial >= 10:
                    self.pvg = 0.8
                    self.pds = 0.2
                    self.stim_dur_ds = 0.45

            # SUBSTAGE 2: PUNISH INTRODUCTION
            if self.substage == 2 and self.current_trial >= 10:
                self.response_duration = 30
                self.stim_dur_ds = 0.4
                self.pvg = 0.7
                self.pds = 0.3

                if self.blocks==True: # Repeat 50% if block allowed, punish incorrects
                    self.repoke_th = self.correct_th

                else: # no blocks repoke will depend on the accuracy
                    self.correction_bias = 1  # Repeat prev stim position if punish
                    # repoking allowed: No punish
                    if self.accuracy <= (self.punish_intro - 0.20) and self.current_trial % self.running_window == 0:
                        self.repoke_th = settings.WIN_SIZE[0] * 2
                        print('repoking allowed again')
                    # repoking not allowed: Punish trials
                    elif self.accuracy >= self.punish_intro and self.current_trial % self.running_window == 0:
                        self.repoke_th = self.correct_th
                        print('repoking not allowed')

            elif self.substage == 3 and self.current_trial >= 10:  # SUBSTAGE 3: CONSOLIDATING
                self.pvg = 0.5
                self.pds = 0.5
                self.response_duration = 30
                self.stim_dur_ds = 0.4
                self.correction_bias = 1
                self.repoke_th = self.correct_th


        ####### Other stages #######
        else:  # Easy trials
            # 4 initial easy trials: all VG, repoking allowed
            if self.current_trial > 4 and self.current_trial <9:  # 4 following intermediate trials
                self.pvg = 0.4
                self.pds = 0.6
                self.response_duration = 20
                self.stim_dur_ds = (0.6 + self.init_stim_dur_ds) / 2
            elif self.current_trial == 9:
                self.repoke_th = self.correct_th  # no more repoking allowed
                self.stim_dur_ds = self.init_stim_dur_ds

            ####### STAGE 2: DELAYS LEARNING #######
            elif self.stage == 2 and self.current_trial >= 10:
                if self.substage == 1:  # SUBSTAGE 1: DS CONSOLIDATION
                    self.pvg = 0.2
                    self.pds = 0.8
                    self.correction_bias = 1  # Repeat prev stim position if punish
                    # from trial 20 start reducing stimulus duration of DS
                    if self.current_trial >= 20 and self.current_trial % self.running_window == 0:
                        if self.accuracy >= self.acc_up and self.stim_dur_ds > 0.05:
                            self.stim_dur_ds -= 0.05
                            print('more difficult!')
                        elif self.accuracy <= self.acc_down and self.stim_dur_ds < self.init_stim_dur_ds:
                            self.stim_dur_ds += 0.075
                            print('easier!')

                elif self.substage == 2 and self.current_trial >= 10:  # SUBSTAGE 2: DM CONSOLIDATION
                    self.response_duration = 15
                    self.stim_dur_ds = 0
                    self.pvg = 0.1
                    self.pds = 0.45
                    self.pdm = 0.45

                    # from trial 20 start reducing stimulus duration of DM
                    if self.current_trial >= 20 and self.current_trial % self.running_window == 0:
                        if self.dm_accuracy >= self.acc_up - 0.1 and self.stim_dur_dm > 0.05:
                            self.stim_dur_dm -= 0.05
                            print('more difficult!')
                        elif self.dm_accuracy <= self.acc_down - 0.05 and self.stim_dur_dm < self.init_stim_dur_dm:
                            self.stim_dur_dm += 0.075
                            print('easier!')

                elif self.substage == 3 and self.current_trial >= 10:  # SUBSTAGE 3: DL CONSOLIDATION
                    self.response_duration = 15
                    self.stim_dur_ds = 0
                    self.stim_dur_dm = 0
                    self.pvg = 0.1
                    self.pds = 0.3
                    self.pdm = 0.3
                    self.pdl = 0.3
                    print('Current DL:' + str(self.stim_dur_dl))

                    # from trial 20 start reducing stimulus duration of DL
                    if self.current_trial >= 20 and self.current_trial % self.running_window == 0:
                        if self.dm_accuracy >= self.acc_up - 0.1 and self.stim_dur_dl > 0.05:
                            self.stim_dur_dl -= 0.05
                            print('more difficult!')
                        elif self.dm_accuracy < self.acc_down - 0.05 and self.stim_dur_dl < self.init_stim_dur_dl:
                            self.stim_dur_dl += 0.075
                            print('easier!')

            ####### STAGE 3: DATA COLLECTION  #######
            elif self.stage == 3 and self.current_trial >= 10:
                self.response_duration = 15
                self.stim_dur_ds = 0
                self.stim_dur_dm = 0
                self.stim_dur_dl = 0
                self.pvg = 0.1
                self.pds = 0.1
                self.pdsc1 = 0.1
                self.pdsc2 = 0.1
                self.pdm = 0.15
                self.pdmc1 = 0.15
                self.pdl = 0.3


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
                    print('Blocks prob: '+str(self.prob))
                    other_prob = (1 - self.prob) / 2 # calculate non fav probs
                    p_list = [other_prob] * 3 # create a list of 3 non-fav probs
                    block_combinations = ['012', '021', '102', '120', '210', '201']
                    block_serie = np.random.choice(block_combinations) #choose randomly a block serie
                    for i in range(10): # take 10 pseudirandom block combinations and create a single string
                        next_block = np.random.choice(block_combinations)
                        while block_serie[-1] == next_block[0]:
                            next_block = np.random.choice(block_combinations)
                            if block_serie[-1] != next_block[0]:
                                break
                        block_serie = block_serie + next_block
                    print('blocks serie values: '+str( block_serie))
                    # create block of trials (n= block size value) following the prev serie
                    for idx, i in enumerate(block_serie):
                        p = p_list.copy()
                        p[int(i)] = self.prob
                        if idx == 0:
                            self.x_trials = (np.random.choice(self.x_positions, size=self.block_size, p=p)).tolist()
                            print('x pobs: ' + str(p))
                        else:
                            self.x_trials = self.x_trials + (np.random.choice(self.x_positions, size=self.block_size, p=p)).tolist()
                print('x positions list: ' + str(self.x_trials))


        # Choose x
        self.x = self.x_trials[self.current_trial]
        # Correction bias extension
        if self.correction_bias == 1 and self.current_trial > 0:
            if self.trial_result == 'punish':
                self.x = self.last_x
                print('Correction trial, x position:' + str(self.x))
        print('x position:' + str(self.x))


        ### CHOOSE TRIAL TYPE
        sum_probs = self.pvg + self.pds+ self.pdm + self.pdl + self.pdsc1 +self.pdsc2 + self.pdmc1
        probs_ttypes =  [self.pvg / sum_probs, self.pds / sum_probs, self.pdm / sum_probs, self.pdl / sum_probs,
                         self.pdsc1 / sum_probs, self.pdsc2 / sum_probs,  self.pdmc1 / sum_probs]
        self.trial_type = np.random.choice(['VG', 'DS', 'DM', 'DL', 'DSc1', 'DSc2', 'DMc1'], p=probs_ttypes)
        print('Trial type: ' + str(self.trial_type))

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
        elif self.trial_type == 'DSc1':
            self.stim_duration = self.stim_dur_ds
            output_stim1 = 0
            output_stim2 = 2  # show stimulus fixation 2
            output_stim3 = 0
            output_stim4 = 1  # turn off stim in the Resp Win
        elif self.trial_type == 'DSc2':
            self.stim_duration = self.stim_dur_ds
            output_stim1 = 0
            output_stim2 = 0
            output_stim3 = 2   # show stimulus fixation 2
            output_stim4 = 1   # turn off stim in the Resp Win
        elif self.trial_type == 'DMc1':
            self.stim_duration = self.stim_dur_dm
            output_stim1 = 0
            output_stim2 = 2  # show stimulus fixation 2
            output_stim3 = 1  # turn off stim in the fixation 3
            output_stim4 = 15

        # silent trials
        if self.silent == True and self.stage==3 and self.current_trial >10:
            self.y = np.random.choice([125, 1000], p=[0.95, 0.05])  # 5% trials stimulus doesn't appear
            print('Silent trial')


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
                output_actions=[])

        self.sma.add_state(
            state_name='Fixation1',
            state_timer=0,
            state_change_conditions={'PA1_Port2In': 'Fixation2'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim1)])
            # show stimulus now

        self.sma.add_state(
            state_name='Fixation2',
            state_timer=0,
            state_change_conditions={'PA1_Port3In': 'Fixation3'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim2)])

        self.sma.add_state(
            state_name='Fixation3',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port3In: 'Pre_Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim3)])

        self.sma.add_state(
            state_name='Pre_Response_window',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, output_stim4)])
            #show stimulus with timer: VG until RW ends, WMI defined by stim_dur_ds

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
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Correct_other_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Exit',  # Doors closure when trial ends
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])



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
        self.register_value('pdsc1', self.pdsc1)
        self.register_value('pdsc2', self.pdsc2)
        self.register_value('pdmc1', self.pdmc1)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('reponse_duration', self.response_duration)
        self.register_value('correction_bias', self.correction_bias)
        self.register_value('trial_length', self.trial_length)
        self.register_value('block_size', self.block_size)

