from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
import os
import re


class Probability_Bastos_Taylor(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task is for Bastos and Taylor for Probabilistic Inference training and test.
        Stages:
        Stage 1 - Image of 2 open hands, 1 hand with peg and 1 hand empty. 
        Stage 2 - Starts from open hands and then closes as rat approaches.
        Stage 3 -

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        # Non-used variables so that stage training works:
        self.stim_dur_ds = 0
        self.stim_dur_dm = 0
        self.stim_dur_dl = 0
        self.choices = 0
        self.substage = 0
        self.substage_bias = 0

        # Variables for the task:
        self.duration_max = 3000
        self.duration_min = 2100
        self.duration_tired = 1800
        self.trials_tired = 5
        self.tired = False
        self.task_number = 5
        self.stage = 2
        self.response_duration = 60
        self.video_display = 0  # Number of seconds the video will display after correct and incorrect
        # self.punish_intro = 0.6     #If they do 60% correct trials prvious 10 trials, punish is introduced (40Khz tone, negatively associated) where they do not get any water

        # accuracy limits for changing something later on:
        # self.acc_up = 0.85
        # self.acc_down = 0.4

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 2  # Normal water delivery of 25ul multiplied by this
        # self.valve_factor_i = 0.6  # Water delivery for incorrects/punish

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.touch_outside = 0
        self.reward_drunk = 0
        # self.running_window = 10  # This is the number of trials the accuracy is measured by. It will take accuracy for every 10 trials.
        self.accwindow = [0]
        self.correct_count = 0
        self.accuracy = 0

        # video output stims:
        self.stim = [0]  # Calls function 25 to display Blue 1.png and function 26 to display Blue 2.png respectively.

        # Correcth location and size:
        self.x_correcth_pos = [95, 281]  # Positions of the stim on the screen
        self.y_correcth = 110
        self.width = 100  # Stimulus width in mm. Original size for jar is 70mm.
        self.height = 190  # Stimulus height in mm. Original size for jar is 110mm.
        self.video_path_function = None
        self.video_displayed = None
        self.video_directory = None
        self.random_block = 40
        self.random_counter = 0
        self.video_stim_play = 0
        self.video_length = 0

        self.moved_back_counter = 0  # TO TRACK HOW MANY TIMES DOES THE RAT MOVE FROM DISCRIMINATION A TO INDICATION.

        # Bias breaking variables:
        self.bias_breaking = 0  # If subject chooses same side for 5 trials in a row, bias breaking becomes active
        self.response_x_array = []  # Stores responses for x till 3 values
        self.sameside_counter = 0  # Counts number of times on same side
        self.sameside = None  # To track which side is being triggered
        self.side_bias_trigger = 5  # After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8
        self.status = None  # Stores the Touch_outside condition
        self.biased_consecutive_corrects_counter = 0  # This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3  ##This is the number of corrrects the rat needs to do to end bias breaking

        # Required for Weber's law:
        self.block = 0  # This is the number of trials at which randomisation will be given again.
        self.conditions = []  # Takes the conditions from select task file.
        self.completed_conditions = []  # To store completed conditions
        self.current_condition = 0  # To track the current condition in progress
        self.repetition = 0
        self.current_repetition = 0  # To store how many times the condition has repeated.
        self.trial_counter = 0  # Track the number of trials for the current condition
        # # video output stims:
        # self.stim_trial = 0
        # self.stim_trials = []
        self.stim_trial_counter = 0

    def configure_gui(self):
        self.gui_input = ['stage', 'substage', 'duration_max']

    def generate_random_trials(self, last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
        trials = []
        # Define a 50% probability for each stimulus (two stimuli)
        probabilities = [0.5, 0.5]  # Adjust this if you have more than two stimuli
        while len(trials) < self.random_block:
            # Use random.choices to select a candidate with 50% probability for each stimulus
            candidate = random.choices(self.stim, probabilities)[0]
            # Ensure no repetition more than twice in sequence
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                # Additionally, ensure the first trial doesn't repeat the last trial from the previous block
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue  # Skip if the first trial of new block matches last trial of previous block
                trials.append(candidate)
        return trials

    def get_stim_video_path(self, stim_trial, stage):
        """
        Determines whether stim_trial is 111, 112, retrieves the corresponding video path, and returns it.
        """
        video_path = None
        video_folder = None
        try:
            if stim_trial == 111:
                position = 'left'
            elif stim_trial == 112:
                position = 'right'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}. Expected 111, or 112.")
            # Define video folder based on stage
            if stage == 2:
                video_folder = '/home/ratvillage01/academy/stimuli/bastos_taylor/hand_tracking/stage_2_hand_tracking_video'
            elif stage == 3:
                video_folder = '/home/ratvillage01/academy/stimuli/bastos_taylor/hand_tracking/'
            else:
                raise ValueError(f"Invalid stage value: {stage}.")
            # Get relevant videos based on position and size
            videos = [f for f in os.listdir(video_folder) if
                      os.path.isfile(os.path.join(video_folder, f)) and
                      (position in f.lower() and 'both' in f.lower())]
            if not videos:
                raise ValueError(
                    f"No videos found in {video_folder} for stage {stage}, position {position}.")
            # Choose a random video
            video_path = os.path.join(video_folder, random.choice(videos))
            print(f'Stage: {utils.task.stage}')
            print(f'Correct answer on {position}, {size} jar: {video_path}')
        except Exception as e:
            print(f"Error occurred: {e}")

        return video_path

    def get_stim_image_path(self, stim_trial, condition):
        """
        Determines whether stim_trial is 71 or 72, retrieves the corresponding image path, and returns it.
        """
        image_path = None
        image_folder = f'/home/ratvillage01/academy/stimuli/webers_law/5_webers_law_training/{condition}'

        try:
            if stim_trial == 61:
                position = 'left'
            elif stim_trial == 62:
                position = 'right'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}. Expected 71 or 72.")

                # Get relevant images
            images = [f for f in os.listdir(image_folder) if
                      os.path.isfile(os.path.join(image_folder, f)) and
                      (position in f.lower() and 'both' in f.lower())]

            if not images:
                raise ValueError(
                    f"No images found in {image_folder} for condition {condition} and position {position}.")

            # Choose a random image
            image_path = os.path.join(image_folder, random.choice(images))

            print(f'Trial Condition: {condition}')
            print(f'Correct answer on {position}: {image_path}')

        except Exception as e:
            print(f"Error occurred: {e}")

        return image_path

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Stage:', self.stage)
        print('Accuracy: ', self.accuracy)
        print('Stim_Trial: ', self.stim_trial)
        print('random_counter: ', self.random_counter)

        if self.current_trial == 0:
            self.bias_breaking = 0
            self.accuracy = 0
            self.random_counter = 0

        print('Bias Breaking: ', self.bias_breaking)

        ### Randomizing the stimulus positions for both the videos:
        # Choose x positions:
        self.stim = [111, 112]

        if self.stage == 1:
            pass #Program for images here
        else:
            # Stimulus generation logic
            if self.random_counter % self.random_block == 0 and self.bias_breaking == 0:  # Re-randomize every 10 trials
                # If not the first random_block, pass the last stimulus of the previous random_block to avoid repetition
                last_trial = self.stim_trials[self.random_counter - 1] if self.random_counter > 0 else None
                self.stim_trials = self.generate_random_trials(last_trial)
                print(f"Stimulus trials after first attempt: {self.stim_trials}")
                while self.stim_trials is None:
                    print("Retrying to generate stimulus trials...")
                    self.stim_trials = self.generate_random_trials(last_trial)
                    if self.stim_trials is None:
                        print("generate_random_trials returned None. Retrying...")
                    else:
                        print(f"Successfully generated stimulus trials: {self.stim_trials}")
                self.random_counter = 0

        if self.bias_breaking == 0:
            self.stim_trial = self.stim_trials[self.random_counter]
        else:
            self.stim_trial = self.last_stim_trial
            print('last_stim_trial', self.last_stim_trial)

        if self.stage == 2:  # We have only one stimuli in stage 1
            # Here, if we need to define the correcth_x position based on the stimulus. So function 101 displays stimulus with correct answer on the left (x=115) and 102 displays stimulus with correct answer on right (x=295)
            if self.stim_trial in [111]:
                self.video_stim_play = 115
                self.x_correcth = self.x_correcth_pos[0]
                self.x_incorrecth = None  # No incorrect area in stage 1
                print('Correct Answer: Left, ', 'X position = ', self.x_correcth)
            elif self.stim_trial in [112]:
                self.video_stim_play = 116
                self.x_correcth = self.x_correcth_pos[1]
                self.x_incorrecth = None  # No incorrect area in stage 1
                print('Correct Answer: Right, ', 'X position = ', self.x_correcth)
        else:  # We have two stimuli after stage 1 with correct and incorrect areas
            if self.stim_trial in [111]:
                self.video_stim_play = 115
                self.x_correcth = self.x_correcth_pos[0]
                self.x_incorrecth = self.x_correcth_pos[1]
                print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ',
                      self.x_incorrecth)
            elif self.stim_trial in [112]:
                self.video_stim_play = 116
                self.x_correcth = self.x_correcth_pos[1]
                self.x_incorrecth = self.x_correcth_pos[0]
                print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ',
                      self.x_incorrecth)

        self.video_path_function = self.get_stim_video_path(self.stim_trial, self.stage)

        print("video_path_function", self.video_path_function)

        directory, filename = os.path.split(self.video_path_function)
        self.video_displayed = filename
        self.video_directory = directory

        print('random counter', self.random_counter)

        ############ STATE MACHINE ################
        # First trial:
        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
            # Starts task and displays stimuli instanly

            self.sma.add_state(
                state_name='Real_start',
                state_timer=self.valve_time * 2,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
            # Closes corridor door 2 and delivers initial 50ul water.

        # Other Trials:
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
            state_change_conditions={Bpod.Events.Port3In: 'Start_Video'},
            output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
        # Does Nothing. Make it close door 3 later when Duncan has fixed it.

        self.sma.add_state(
            state_name='Start_Video',
            state_timer=self.video_length,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, self.video_stim_play)])
        # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration,
            state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', 'SoftCode4': 'Punish',
                                     Bpod.Events.Tup: 'No_Touch'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 34)])
        # Starts to read the touchscreen with one touch processing

        self.sma.add_state(
            state_name='Correct',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Correct_video_display'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 38)])
        # Turns on Water port LED and plays correct sound

        self.sma.add_state(
            state_name='Correct_video_display',
            state_timer=self.video_display,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_reward', Bpod.Events.Tup: 'Flip_screen_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 63)])
        # Turns on Water port LED and plays correct sound and displays correct stimuli for video_display (3 seconds)

        self.sma.add_state(
            state_name='Correct_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 17)])
        # Delivers Water and stops the reward sound and flips the screen

        self.sma.add_state(
            state_name='Flip_screen_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Correct_reward'},
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
            state_change_conditions={Bpod.Events.Tup: 'Punish_video_display'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 39)])
        # Turns on Global LED and water port LED on

        self.sma.add_state(
            state_name='Punish_video_display',
            state_timer=self.video_display,
            state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 64)])
        # Turns on Global LED and water port LED on, and displays incorrect stimuli for video_display (3 seconds) nad plays punish sound for 1 second.

        self.sma.add_state(
            state_name='After_punish',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 40)])
        # Flips the screen after water port poked in.

        self.sma.add_state(
            state_name='Flip_screen_no_reward',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 40)])
        # Turns on Water port LED and plays correct sound and flips screen after 3 seconds

        self.sma.add_state(
            state_name='No_Touch',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port1In: 'Exit', Bpod.Events.Port2In: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                            (Bpod.OutputChannels.SoftCode, 37)])
        # Turns on Water port LED and Global LED and displays message on camera for miss and flips the screen to displays blank,

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])

    def after_trial(self):
        if self.bias_breaking == 0:
            self.random_counter += 1

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

            # Check if side bias is active and if the current trial was correct
            if self.bias_breaking == 1:  # Side bias active
                self.biased_consecutive_corrects_counter += 1  # Increment counter for consecutive corrects
                if self.biased_consecutive_corrects_counter >= self.biased_consecutive_corrects:  # If three corrects after bias breaking
                    self.bias_breaking = 0  # End bias breaking
                    self.biased_consecutive_corrects_counter = 0  # Reset the consecutive corrects counter


        # ##### COUNT Touches outside the jar areas :
        elif self.current_trial_states['Touch_Outside'][0][0] > 0:
            self.status = 'Touch_Outside'

        # End-trial calculations
        # self.last_x = self.x
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
        # self.accuracy = sum(self.accwindow) / len(self.accwindow)
        self.accuracy = self.correct_count / self.valid_counter if self.current_trial > 0 else 0

        # Side Bias Breaking formula:
        self.last_stim_trial = self.stim_trial

        try:
            # Try converting response_x directly to a float
            self.response_x_bias = float(self.response_x)
        except ValueError:
            print(f"No response_x value or response other: {self.response_x}")

            # Split the string by commas and convert it to a list of floats
            try:
                # First, check if the response_x is a string and split it
                response_x_list = [float(x) for x in self.response_x.split(",")]

                # Use the last element of the list as response_x_bias
                self.response_x_bias = response_x_list[-1]
                print(f"Using last value from response_x array: {self.response_x_bias}")
            except Exception as e:
                # print(f"Failed to process response_x as array. Error: {e}")
                return  # Handle this case if needed

        # Append the response to the array:
        # if self.status != 'Touch_Outside':  #Do not append responses in case of touches outside the area
        self.response_x_array.append(self.response_x_bias)
        print(f"Responses so far: {self.response_x_array}")
        print(f"Conditions: {self.conditions}")

        # if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy < self.side_bias_trigger_acc:
        if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy is not None and self.accuracy < self.side_bias_trigger_acc:
            # Check if all responses fall into one of the two defined categories
            all_left_side = all(45 < x < 145 for x in self.response_x_array)  # Check if all the reponses fall on left
            all_right_side = all(
                231 < x < 331 for x in self.response_x_array)  # Check if all the reponses fall on right


            if all_left_side:
                self.sameside = 'left'
                self.bias_breaking = 1
                print('Bias breaking active, side:', self.sameside)
                self.last_stim_trial = random.choice([112])  # Ensure the new stim is on the right
            elif all_right_side:
                self.sameside = 'right'
                self.bias_breaking = 1
                self.last_stim_trial = random.choice([111])  # Ensure the new stim is on the left
                print('Bias breaking active, side:', self.sameside)

            self.response_x_array = []  # Clearing the array


        ############ REGISTER VALUES ################
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)
        self.register_value('choices', self.choices)
        self.register_value('substage', self.substage)
        self.register_value('substage_bias', self.substage_bias)
        self.register_value('y', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)
        self.register_value('correct_th', self.x_correcth)
        self.register_value('incorrect_th', self.x_incorrecth)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('response_duration', self.response_duration)
        self.register_value('trial_length', self.trial_length)
        self.register_value('task_number', self.task_number)
        self.register_value('stage', self.stage)
        self.register_value('trial_result', self.trial_result)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('accuracy', self.accuracy)
        self.register_value('bias_breaking', self.bias_breaking)
        self.register_value('sameside', self.sameside)
        self.register_value('side_bias_trigger_acc', self.side_bias_trigger_acc)
        self.register_value('side_bias_trigger_trial', self.side_bias_trigger)
        self.register_value('biased_consecutive_corrects_counter', self.biased_consecutive_corrects_counter)
        self.register_value('biased_consecutive_corrects', self.biased_consecutive_corrects)
        self.register_value('random_counter', self.random_counter)
        self.register_value('random_block', self.random_block)
        self.register_value('moved_back_counter', self.moved_back_counter)
        # Weber's Law:
        self.register_value('block', self.block)
        self.register_value('conditions', self.conditions)
        self.register_value('completed_conditions', self.completed_conditions)
        self.register_value('current_condition', self.current_condition)
        self.register_value('repetition', self.repetition)
        self.register_value('current_repetition', self.current_repetition)
        self.register_value('trial_counter', self.trial_counter)
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)
        self.register_value('video_displayed', self.video_displayed)
        self.register_value('video_directory', self.video_directory)