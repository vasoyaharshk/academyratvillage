from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
import os
import re

class Probability_Turtle_Training(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task is the Relative Quantity Discrimination task based on the Turtle experiment by Sun et al. 2023. The discrimination is between blue and yellow colours.
        In this task, the animals are allowed to correct their mistakes
        ########   TASK INFO   ########
        Substage 0: Pre training: 5Y0B VS 0Y5B (100%Y VS 0%Y)
        Substage 1: Training 1: 4Y1B VS 1Y4B (80%Y VS 20%Y)
        Substage 2: Training 2: 4Y1B VS 2Y3B (80%Y VS 40%Y)
        Substage 3: Training 3: 2Y3B VS 1Y4B (40%Y VS 20%Y)

        Stage = 6
        
                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        # Variables for the task:
        self.duration_max = 3000                    #50 mins
        self.duration_min = 2100                    #35 mins
        self.duration_tired = 1800                  #30 mins
        self.trials_tired = 5
        self.tired = False
        self.task = 4                               #Task 4 is for Turtle Style.
        self.stage = 0
        self.substage = 0
        self.response_duration = 60
        self.repoking = 1               #This means that repoking is allowed where animals can correct their choices.

        # pump:
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 2.0  # Normal water delivery of 25ul multiplied by this
        self.valve_factor_i = 0.9  # Water delivery for corrections

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.touch_outside = 0
        self.reward_drunk = 0
        self.accwindow = [0]
        self.correct_count = 0
        self.correction_count = 0
        self.accuracy = 0
        self.trial_counter = 0
        self.random_counter = 0
        self.random_block = 4

        # Image output stims:
        self.stim = [0]

        # Correcth location and size:
        self.x_correcth_pos = [95, 281]  # Positions of the stim on the screen
        self.y_correcth = 110
        self.width = 110  # Stimulus width in mm. Original size for jar is 70mm.
        self.height = 160  # Stimulus height in mm. Original size for jar is 110mm.

        # Image output stims:
        self.stim_trial = 0
        self.stim_trials = []
        self.image_path_function = None
        self.image_displayed = None
        self.image_directory = None

    def configure_gui(self):
        self.gui_input = ['substage', 'duration_max']

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

    def get_stim_image_path(self, stim_trial, substage):
        """
        Determines whether stim_trial is 71 or 72, retrieves the corresponding image path, and returns it.
        """
        image_path = None
        image_folder = None

        try:
            if stim_trial == 71:
                position = 'left'
            elif stim_trial == 72:
                position = 'right'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}. Expected 71 or 72.")

            # Define image folder based on substage
            if substage == 0:
                image_folder = '/home/ratvillage02/academy/stimuli/turtle_style/6_turtle_style/0_pre_training'
            elif substage == 1:
                image_folder = '/home/ratvillage02/academy/stimuli/turtle_style/6_turtle_style/1_training'
            elif substage == 2:
                image_folder = '/home/ratvillage02/academy/stimuli/turtle_style/6_turtle_style/2_training'
            elif substage == 3:
                image_folder = '/home/ratvillage02/academy/stimuli/turtle_style/6_turtle_style/3_training'
            else:
                raise ValueError(f"Invalid substage value: {substage}.")

            # Get relevant images
            images = [f for f in os.listdir(image_folder) if
                      os.path.isfile(os.path.join(image_folder, f)) and
                      (position in f.lower() and 'both' in f.lower())]

            if not images:
                raise ValueError(f"No images found in {image_folder} for substage {substage} and position {position}.")

            # Choose a random image
            image_path = os.path.join(image_folder, random.choice(images))

            print(f'Stage: {utils.task.stage}')
            print(f'Correct answer on {position}: {image_path}')

        except Exception as e:
            print(f"Error occurred: {e}")

        return image_path

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Random Counter: ' + str(self.random_counter))
        print('Accuracy: ', self.accuracy)
        print('Stim_Trial: ', self.stim_trial)

        if self.current_trial == 0:
            self.accuracy = 0
            self.random_counter = 0

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        self.stim = [71, 72]  # These are the functions being called. 31 is for the correct answer is on the left and 32 is when the correct answer is on the right

        # Stimulus generation logic
        if self.random_counter % self.random_block == 0:  # Re-randomize every 10 trials
            # If not the first block, pass the last stimulus of the previous block to avoid repetition
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

        self.stim_trial = self.stim_trials[self.random_counter]


        # Decide where the correct position is depending on the function generated randomly, 71 for left and 72 for right:
        if self.stim_trial == 71:
            self.x_correcth = self.x_correcth_pos[0]
            self.x_incorrecth = self.x_correcth_pos[1]
            print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)
        elif self.stim_trial == 72:
            self.x_correcth = self.x_correcth_pos[1]
            self.x_incorrecth = self.x_correcth_pos[0]
            print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)

        self.image_path_function = self.get_stim_image_path(self.stim_trial, self.substage)

        directory, filename = os.path.split(self.image_path_function)
        self.image_displayed = filename
        self.image_directory = directory


        ############ STATE MACHINE ################
        # First trial:
        if self.stage != 7:
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
                state_change_conditions={Bpod.Events.Port6In: 'Response_window'},
                output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
            # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

            self.sma.add_state(
                state_name='Response_window',
                state_timer=self.response_duration,
                state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode2': 'Incorrect',
                                         'SoftCode3': 'Touch_Outside', Bpod.Events.Tup: 'No_Touch'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 73)])
            # wait for subject response

            self.sma.add_state(
                state_name='Correct_first',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 11)])
            # waterLED and correct sound remain ON until poke and flips the screen

            self.sma.add_state(
                state_name='No_Touch',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port1In: 'Exit', Bpod.Events.Port2In: 'Exit'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 37)])
            # waterLED ON, global LEDs ON and flips the screen

            self.sma.add_state(
                state_name='No_Touch2',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port1In: 'Exit', Bpod.Events.Port2In: 'Exit'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 37)])
            # waterLED ON, global LEDs ON and flips the screen

            self.sma.add_state(
                state_name='Incorrect',
                state_timer=0.25,  # After incorrect, the state remains for 1 second.
                state_change_conditions={Bpod.Events.Tup: 'Response_window2'},
                output_actions=[(Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 13)])
            # Incorrect sound and global LED.

            self.sma.add_state(
                state_name='Response_window2',
                state_timer=self.response_duration,
                state_change_conditions={'SoftCode1': 'Correct_other', 'SoftCode2': 'Incorrect',
                                         'SoftCode3': 'Touch_Outside2', Bpod.Events.Tup: 'No_Touch2'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 74)])

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
                state_name='Touch_Outside',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Response_window'},
                output_actions=[])
            # Goes back to response window in case of touch outside the three regions

            self.sma.add_state(
                state_name='Touch_Outside2',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Response_window2'},
                output_actions=[])
            # Goes back to response window in case of touch outside the three regions

            self.sma.add_state(
                state_name='Exit',  # Doors closure when trial ends
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'exit'},
                output_actions=[])
        else:
            print("Stage is 7. Task Ended.")


    def after_trial(self):
        if self.stage != 7:
            self.trial_counter += 1
            self.random_counter += 1

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.accwindow = self.accwindow[1:] + [0]
                self.trial_result = 'miss'

            if self.current_trial_states['No_Touch2'][0][0] > 0:  # miss after a touch is considered as an incorrect
                self.accwindow = self.accwindow[1:] + [0]
                self.trial_result = 'incorrect'

            ##### COUNT CORRECTS:
            elif self.current_trial_states['Correct_first'][0][0] > 0:
                self.trial_result = 'correct_first'
                self.valid_counter += 1
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.accwindow = self.accwindow[1:] + [1]
                self.correct_count += 1
                print('Correct_count: ', self.correct_count)

            ##### COUNT CORRECTIONS:
            elif self.current_trial_states['Correct_other'][0][0] > 0:
                self.trial_result = 'correction'
                self.valid_counter += 1
                self.reward_drunk += self.valve_reward * self.valve_factor_i
                self.accwindow = self.accwindow[1:] + [1]
                self.correction_count += 1
                print('Correction_count: ', self.correction_count)

            # ##### COUNT Touches outside the jar areas :
            elif self.current_trial_states['Touch_Outside'][0][0] > 0 or self.current_trial_states['Touch_Outside2'][0][
                0] > 0:
                self.status = 'Touch_Outside'
                self.touch_outside += 1

            # End-trial calculations
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
            self.accuracy = self.correct_count / self.valid_counter if self.current_trial > 0 else 0
        else:
            print("Stage is 7. Task End")
            self.trial_length = 0.1
            self.trial_result = None

        ############ REGISTER VALUES ################
        self.register_value('stage', self.stage)
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
        self.register_value('trial_result', self.trial_result)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('accuracy', self.accuracy)
        self.register_value('trial_counter', self.trial_counter)
        self.register_value('correct_count', self.correct_count)
        self.register_value('touch_outside', self.touch_outside)
        self.register_value('correction_count', self.correction_count)
        self.register_value('image_displayed', self.image_displayed)
        self.register_value('image_directory', self.image_directory)

