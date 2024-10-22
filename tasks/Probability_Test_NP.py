from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Probability_Test_NP(Task):
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
        self.duration_max = 3000
        self.duration_min = 2100
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
        self.y_correcth = 110
        self.width = 100  # Stimulus width in mm
        self.height = 190

        #Bias breaking variables:
        self.bias_breaking = 0        #If subject chooses same side for 5 trials in a row, bias breaking becomes active
        self.response_x_array = []      #Stores responses for x till 3 values
        self.sameside_counter = 0       #Counts number of times on same side
        self.sameside = None             # To track which side is being triggered
        self.side_bias_trigger = 3      #After how many trials does side_bias trigger

    def configure_gui(self):
        self.gui_input = ['stage', 'substage', 'duration_max']

    def generate_random_trials(self, last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
        trials = []
        # Define a 50% probability for each stimulus (two stimuli)
        probabilities = [0.5, 0.5]  # Adjust this if you have more than two stimuli
        while len(trials) < 1000:
            # Use random.choices to select a candidate with 50% probability for each stimulus
            candidate = random.choices(self.stim, probabilities)[0]
            # Ensure no repetition more than twice in sequence
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                # Additionally, ensure the first trial doesn't repeat the last trial from the previous block
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue  # Skip if the first trial of new block matches last trial of previous block
                trials.append(candidate)
        return trials

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Accuracy: ', self.accuracy)

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        self.stim = [31, 32]  # These are the functions being called. 31 is for the correct answer is on the left and 32 is when the correct answer is on the right

        # Stimulus generation logic
        if self.current_trial % 10 == 0 and self.bias_breaking == 0:  # Re-randomize every 10 trials
            # If not the first block, pass the last stimulus of the previous block to avoid repetition
            last_trial = self.stim_trials[self.current_trial - 1] if self.current_trial > 0 else None
            self.stim_trials = self.generate_random_trials(last_trial)
            print('x positions list: ' + str(self.stim_trials))

        self.stim_trial = self.stim_trials[self.current_trial]

        if self.bias_breaking == 0:
            self.stim_trial = self.stim_trials[self.current_trial]
        else:
            self.stim_trial = self.last_stim_trial

        if self.stage == 1:  # We have only one stimuli in stage 1
            # Here, if we need to define the correcth_x position based on the stimulus. So function 31 displays stimulus with correct answer on the left (x=115) and 32 displays stimulus with correct answer on right (x=295)
            if self.stim_trial == 31:
                self.x_correcth = self.x_correcth_pos[0]
                self.x_incorrecth = None  # No incorrect area in stage 1
                print('Correct Answer: Left, ', 'X position = ', self.x_correcth)
            elif self.stim_trial == 32:
                self.x_correcth = self.x_correcth_pos[1]
                self.x_incorrecth = None  # No incorrect area in stage 1
                print('Correct Answer: Right, ', 'X position = ', self.x_correcth)
        else:  # We have two stimuli after stage 1 with correct and incorrect areas
            if self.stim_trial == 31:
                self.x_correcth = self.x_correcth_pos[0]
                self.x_incorrecth = self.x_correcth_pos[1]
                print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)
            elif self.stim_trial == 32:
                self.x_correcth = self.x_correcth_pos[1]
                self.x_incorrecth = self.x_correcth_pos[0]
                print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)


        ############ STATE MACHINE ################
        #First trial:
        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
            # Starts task and displays stimuli instanly

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 2,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # Closes corridor door 2 and delivers initial 50ul water.

        #Other Trials:
        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
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
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
        # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration,
            state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', 'SoftCode4': 'Punish', Bpod.Events.Tup: 'No_Touch'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 34)])
        # Starts to read the touchscreen with one touch processing

        self.sma.add_state(
            state_name='Correct',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Correct_image_display'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 38)])
        # Turns on Water port LED and plays correct sound

        self.sma.add_state(
            state_name='Correct_image_display',
            state_timer=self.image_display,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_reward', Bpod.Events.Tup: 'Flip_screen_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 35)])
        # Turns on Water port LED and plays correct sound and displays correct stimuli for image_display (3 seconds)

        self.sma.add_state(
            state_name='Correct_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])
        # Delivers Water and stops the reward sound and flips the screen

        self.sma.add_state(
            state_name='Flip_screen_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Correct_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 40)])
        # Turns on Water port LED and plays correct sound and flips screen after 3 seconds

        self.sma.add_state(
            state_name='Touch_Outside',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[])
        # Goes back to response window in case of touch outside the two jar areas

        self.sma.add_state(
            state_name='Punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Punish_image_display'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 39)])
        # Turns on Global LED and water port LED on

        self.sma.add_state(
            state_name='Punish_image_display',
            state_timer=self.image_display,
            state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 36)])
        # Turns on Global LED and water port LED on, and displays incorrect stimuli for image_display (3 seconds) nad plays punish sound for 1 second.

        self.sma.add_state(
            state_name='After_punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 40)])
        # Flips the screen after water port poked in.

        self.sma.add_state(
            state_name='Flip_screen_no_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 40)])
        # Turns on Water port LED and plays correct sound and flips screen after 3 seconds

        self.sma.add_state(
            state_name='No_Touch',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit', Bpod.Events.Port2In: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 37)])
        # Turns on Water port LED and Global LED and displays message on camera for miss and flips the screen to displays blank,

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])


    def after_trial(self):
        ##### COUNT MISSES:
        if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
            self.accwindow = self.accwindow[1:] + [0]
            self.trial_result = 'miss'

        ##### COUNT PUNISH
        elif self.current_trial_states['Punish'][0][0] > 0:
            self.trial_result = 'incorrect'
            self.valid_counter += 1
            self.accwindow = self.accwindow[1:] + [0]

        ##### COUNT CORRECTS FIRST POKE
        elif self.current_trial_states['Correct'][0][0] > 0:
            self.trial_result = 'correct'
            self.valid_counter += 1
            self.reward_drunk += self.valve_reward * self.valve_factor_c
            self.accwindow = self.accwindow[1:] + [1]
            self.correct_count += 1
            print('Correct_count: ', self.correct_count)
            self.bias_breaking = 0

        # ##### COUNT Touches outside the jar areas :
        # elif self.current_trial_states['Touch_Outside'][0][0] > 0:
        #     self.touch_outside += 1
        #     print('Outside_count: ', self.touch_outside)

        # End-trial calculations
        #self.last_x = self.x
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

        # Accuracy for running trials:
        #self.accuracy = sum(self.accwindow) / len(self.accwindow)
        self.accuracy = self.correct_count / self.valid_counter if self.current_trial > 0 else None

        # # Stage progression based on conditions:
        # if self.stage == 1 and self.current_trial >= 40 and self.accuracy >= self.acc_up:
        #     print(f'Advancing from stage 1 to stage 2 with accuracy {self.accuracy}')
        #     self.stage = 2
        #     self.current_trial = 1
        #     self.acc_up = 0
        # elif self.stage == 2 and self.current_trial >= 40 and self.accuracy >= self.acc_up:
        #     print(f'Advancing from stage 2 to stage 3 with accuracy {self.accuracy}')
        #     self.stage = 3
        #     self.current_trial = 1
        #     self.acc_up = 0
        # elif self.stage == 3 and self.current_trial >= 40 and self.accuracy >= self.acc_up:
        #     print(f'Advancing from stage 2 to stage 3 with accuracy {self.accuracy}')
        #     self.stage = 4
        #     self.current_trial = 1
        #     self.acc_up = 0

        # Side Bias Breaking formula:

        self.last_stim_trial = self.stim_trial

        print('response X:', self.response_x)
        print(f"Type of response X: {type(response_x)}")

        # Append the response to the array:
        #if self.current_trial_states['miss'][0][0] > 0   #Do not append responses in case of touches outside the area
        self.response_x_array.append(self.response_x)
        print(f"Responses so far: {self.response_x_array}")

        if len(self.response_x_array) >= self.side_bias_trigger:
            self.response_x_array = []

            # Check if all responses fall into one of the two defined categories
            all_left_side = all(45 < x < 145 for x in self.response_x_array)            #Check if all the reponses fall on left
            all_right_side = all(231 < x < 331 for x in self.response_x_array)          #Check if all the reponses fall on right

            if all_left_side:
                self.sameside = 'left'
                self.bias_breaking = 1
                print('Bias breaking active, side:', self.sameside)
            elif all_right_side:
                self.sameside = 'right'
                self.bias_breaking = 1
                print('Bias breaking active, side:', self.sameside)


        # if 45 < self.response_x < 145:
        #     self.sameside = 'left'
        #     self.sameside_counter += 1
        # elif 231 < self.response_x < 331:
        #     #self.sameside = 'right'
        #     self.sameside_counter += 1
        #
        # if self.sameside_counter == 5:
        #     self.bias_breaking = 1
        #     print('Bias breaking active, side: ', self.sameside)
        #     if self.trial_result == 'punish':
        #         self.stim_trial = self.last_stim_trial
        #
        # # Correction bias extension
        # if self.bias_breaking == 1:
        #     if self.trial_result == 'punish':
        #         self.stim_trial = self.last_stim_trial
        # print('Stim Trial: ', self.stim_trial)

        ############ REGISTER VALUES ################
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)
        self.register_value('choices', self.choices)
        self.register_value('substage', self.substage)
        self.register_value('y', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)
        self.register_value('correct_th', self.x_correcth)
        self.register_value('incorrect_th', self.x_incorrecth)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('response_duration', self.response_duration)
        self.register_value('trial_length', self.trial_length)
        self.register_value('stage', self.stage)
        self.register_value('trial_result', self.trial_result)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('accuracy', self.accuracy)