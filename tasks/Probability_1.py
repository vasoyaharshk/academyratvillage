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
        Stage 1 - Only blue jar of pegs stimulus appears Blue is rewarding and yellow unrewarding
        Stage 2: Blue and yellow jar of pegs appears (100% each)
        Stage 3:   Blue and yellow jar of pegs appears (1 jar is 100% of unrewarded color yellow and the other is 50%)
        
                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        #Variables for the task:
        #self.duration_max = 3000  # 50 min finished the task
        self.duration_max = 125  # 50 min finished the task
        #self.duration_min = 2100  # 35 min door opens
        self.duration_min = 120  # 35 min door opens
        self.duration_tired = 10  # 30 mins if animal sleeping last 10 mins, finishes task
        self.trials_tired = 5  # if animal does less than this number in the last 10 mins, finishes task
        self.tired = False  # Tired animal indicator
        self.mask = 2
        self.choices = self.mask
        self.block_size = 10    #Used for randomisation
        self.stage = 1
        self.substage = 1
        self.response_duration = 60
        self.correction_bias = 0    # if 1, The same stimulus position is repeated if they get it wrong in the previous trial until they get it correct.
        #self.punish_intro = 0.6     #If they do 60% correct trials prvious 10 trials, punish is introduced (40Khz tone, negatively associated) where they do not get any water

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
        self.running_window = 10        #This is the number of trials the accuracy is measured by. It will take accuracy for every 10 trials.
        self.accwindow = [0] * self.running_window  #Accuracy changes every 10 trials and is stored in this variable.

        #Screen details:
        self.y = 100 #height of the stimulus
        self.width = 120 #width of the stimulus
        self.correct_th = 130 #portion of the screen correct.
        self.repoke_th = self.correct_th                #This is the condition when repoking is now allowed and the incorrects get punished.

        self.x = 0
        self.x_positions = [60, 290]  #Positions of the stim on the screen

    def configure_gui(self):
        self.gui_input = ['x', 'y', 'width', 'stage', 'substage', 'duration_max']

    def generate_random_trials(self):
        trials = []
        while len(trials) < 1000:
            candidate = random.choice(self.x_positions)
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                trials.append(candidate)
        return trials

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # Accuracy for running trials:
        self.accuracy = sum(self.accwindow) / len(self.accwindow)
        print("Accuracy: " + str(self.accuracy))

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions by blocks
        if self.stage == 1:
            if self.current_trial % 10 == 0:  # Re-randomize every 10 trials

                # Randomizing the probabilities for both images:
                #self.x_trials = random.choices(self.x_positions, k=1000)
                # Generate initial random x positions where no two positions are repeated more than twice:
                self.x_trials = self.generate_random_trials()
                print('x positions list: ' + str(self.x_trials))

                #Substage 1: The individuals can correct their responses only in this substage
            if self.substage == 1:
                self.repoke_th = settings.WIN_SIZE[0] * 2  # This is the condition when repoking is allowed

        elif stage == 2 or stage== 3:
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
        self.x = self.x_trials[self.current_trial]
        #self.x2 = self.x2_trials[self.current_trial]

        # Correction bias:
        #if self.correction_bias == 1:
         #   if self.trial_result == 'punish':
          #      self.x = self.last_x
           #     print('Correction trial, x position:' + str(self.x))
        print('x position:' + str(self.x))

        ############ STATE MACHINE ################

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 6)])
                #Starts task and displays stimuli instanly

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 2,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # Closes corridor door 2 and delivers initial 50ul water.

        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 6)])
                # Starts task and displays stimuli instanly

        self.sma.add_state(
            state_name='Wait_for_fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port6In: 'Fixation'},
            output_actions=[])
            #Does Nothing

        self.sma.add_state(
            state_name='Fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[])
            # Does Nothing

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect', 'SoftCode3': 'Miss',
                                     'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4)])
            #Starts to read the touchscreen

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
            #Turns on Water port LED and plays correct sound

        self.sma.add_state(
            state_name='Miss',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port2In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 10)])
            #Turns on Water port LED and Global LED and displays message on camera for miss

        self.sma.add_state(
            state_name='Punish',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'After_punish'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 14)])
            #Turns on Global LED and plays punish sound

        self.sma.add_state(
            state_name='After_punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward', Bpod.Events.Port1Out: 'Miss_reward',
                                     Bpod.Events.Port2In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6)])
            #Turns on water port LED and Global LED

        self.sma.add_state(
            state_name='Incorrect',
            state_timer=0.25,
            state_change_conditions={Bpod.Events.Tup: 'Response_window2'},
            output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 13)])
            #Turns on Global LED and plays incorrect sound

        self.sma.add_state(
            state_name='Response_window2',
            state_timer=self.response_duration + 10,
            state_change_conditions={'SoftCode1': 'Correct_other', 'SoftCode2': 'Incorrect',
                                     'SoftCode3': 'Miss', 'SoftCode4': 'Punish', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 5)])
            #Touchscreen in reading mode again

        self.sma.add_state(
            state_name='Correct_other',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_other_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
            #Turns on Water port LED and plays correct sound

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])
            #Delivers Water and stops the reward sound

        self.sma.add_state(
            state_name='Correct_other_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])
            #Delivers Water and stops the reward sound

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 17)])
            #Stops the reward sound

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])


def after_trial(self):
    ############ TRIAL COUNTER ################

    ##### COUNT MISSES
    if self.current_trial_states['Miss'][0][0] > 0:  # misses & incorrects modify the acc
        self.accwindow = self.accwindow[1:] + [0]
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

    ##### COUNT CORRECTS FIRST POKE
    elif self.current_trial_states['Correct_first'][0][0] > 0:
        self.trial_result = 'correct_first'
        self.valid_counter += 1
        self.reward_drunk += self.valve_reward * self.valve_factor_c
        self.accwindow = self.accwindow[1:] + [1]

    ##### COUNT CORRECTS OTHER POKE
    else:
        self.trial_result = 'correct_other'
        self.valid_counter += 1
        self.reward_drunk += self.valve_reward * self.valve_factor_i
        self.accwindow = self.accwindow[1:] + [0]

    # End-trial calculations
    self.last_x = self.x
    self.trial_length = self.current_trial_states['Exit'][0][0] - self.current_trial_states['Start_task'][0][0]
    print('Trial length: ' + str(self.trial_length))

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
    self.register_value('trial_result', self.trial_result)
    self.register_value('reward_drunk', self.reward_drunk)
    self.register_value('reponse_duration', self.response_duration)
    self.register_value('correction_bias', self.correction_bias)
    self.register_value('trial_length', self.trial_length)
    self.register_value('block_size', self.block_size)
