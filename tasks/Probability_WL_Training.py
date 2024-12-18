from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Probability_WL_Training(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This is the real weber's law file.
        This task displays the image of the jars which are touchable. This script is for Weber's law and the bias breaking is not active.
        ########   TASK INFO   ########
        This is the Weber's law training task where: 
        1. Training starts with RoR 16, then 12, 8, 6 (conditions 16 to 9) consecutively, only progressing to the next RoR when they meet 
        criteria: ≥70% success on at least 36 trials within 2 consecutive sessions
        2. Then they get ROR 4 – 1 (conditions 9 to 1) interleaved with easier RoRs (conditions 16 to 9). No more than 2 easy or hard in a row
        3. End point: Cut-off of 1000 trials per RoR of conditions 16 to 9.

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        #Non-used variables so that working memory works:
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
        self.stage = 4
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
        self.accwindow = [0]
        self.correct_count = 0
        self.accuracy = 0

        # Correcth location and size:
        self.x_correcth_pos = [95, 281]  # Positions of the stim on the screen
        self.y_correcth = 110
        self.width = 110  # Stimulus width in mm. Original size for big jar is 80mm and small jar is 70mm.
        self.height = 225   # Stimulus height in mm. Original size for big jar is 125mm and small jar is 110mm.
        self.stim = [0]  # Calls functions to display Blue 1.png and function 26 to display Blue 2.png respectively.

        #Bias breaking variables, not used in Weber's Law:
        self.bias_breaking = 0        #If subject chooses same side for 5 trials in a row, bias breaking becomes active
        self.response_x_array = []      #Stores responses for x till 3 values
        self.sameside_counter = 0       #Counts number of times on same side
        self.sameside = None             # To track which side is being triggered
        self.side_bias_trigger = 5      #After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8            #Accuracy at which side bias will trigger
        self.status = None              #Stores the Touch_outside condition
        self.biased_consecutive_corrects_counter = 0       #This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3                ##This is the number of corrrects the rat needs to do to end bias breaking

        # Randomise blocks and trials for Weber's Law:
        self.block = 0  # This is the number of trials one conditions will remain for
        self.conditions = []  # Takes the conditions from select task file.
        self.completed_conditions = []  # To store completed conditions
        self.current_condition = 0  # To track the current condition in progress
        self.repetition = 0  # To store how many times the conditions needs to repeat.
        self.current_repetition = 0  # To store how many times the condition has repeated.
        self.trial_counter = 0  # Track the number of trials for the current condition
        # Image output stims:
        self.stim_trial = 0
        self.stim_trials = []
        self.stim_trial_counter = 0

        self.running_window = self.block  # This is the number of trials the accuracy is measured by. It will take accuracy for every 12 trials.

        #Weber's Law Training Variables:
        # Variables not tracked:
        self.start_task == 1        #This ensures that the first sessions is the start training task.
        self.ror_to_conditions = {
            16: [16, 15],
            12: [14, 13],
            8: [12, 11],
            6: [10, 9],
            4: [8, 7],
            2: [6, 5],
            1.5: [4, 3],
        }
        self.easy_conditions = [16, 15, 14, 13, 12, 11, 10, 9]
        self.easy_ror = [16, 12, 8, 6]
        self.hard_ror = [4, 2, 1.5]
        self.blocks = 20

        #Variables tracked:
        self.ror = [16, 12, 8, 6, 4, 2, 1.5]
        self.current_ror = 16
        self.completed_ror = []
        self.trial_conditions = []

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

    def generate_random_trial_conditions(self, current_ror, last_trial=None):
        """
        Generate a list of conditions for a session based on the given ROR.
        """
        if current_ror not in self.ror_to_conditions:
            raise ValueError("Invalid ROR value provided.")
        conditions = self.ror_to_conditions[current_ror]
        probabilities = [0.5, 0.5]  # 50% probability for each condition
        trials = []
        while len(trials) < 500:
            # Randomly select a candidate condition with 50-50 probability
            candidate = random.choices(conditions, probabilities)[0]
            # Ensure no more than 2 consecutive same conditions
            if len(trials) >= 2 and candidate == trials[-1] == trials[-2]:
                continue
            # Ensure the first trial doesn't repeat the last trial from the previous block
            if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                continue
            # Add the candidate to trials
            trials.append(candidate)
        return trials

    def configure_gui(self):
        self.gui_input = ['duration_max', 'stage']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Accuracy: ', self.accuracy)
        print('Stim_Trial: ', self.stim_trial)
        print('Bias Breaking: ', self.bias_breaking)
        #print('Stim_Trials: ', self.stim_trials)

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        self.stim = [61, 62]  # These are the functions being called. 31 is for the correct answer is on the left and 32 is when the correct answer is on the right

        # Stimulus generation logic
        if self.current_trial % 10 == 0 and self.bias_breaking == 0:  # Re-randomize every 10 trials
            # If not the first block, pass the last stimulus of the previous block to avoid repetition
            last_trial = self.stim_trials[self.current_trial - 1] if self.current_trial > 0 else None
            self.stim_trials = self.generate_random_trials(last_trial)
            print(f"Stimulus trials after first attempt: {self.stim_trials}")
            while self.stim_trials is None:
                print("Retrying to generate stimulus trials...")
                self.stim_trials = self.generate_random_trials(last_trial)
                if self.stim_trials is None:
                    print("generate_random_trials returned None. Retrying...")
                else:
                    print(f"Successfully generated stimulus trials: {self.stim_trials}")

            last_trial_conditions = self.trial_conditions[self.current_trial - 1] if self.current_trial > 0 else None
            self.trial_conditions = self.generate_random_trial_conditions(last_trial, self.current_ror)
            print(f"Trial conditions after first attempt: {self.trial_conditions}")
            while self.trial_conditions is None:
                print("Retrying to generate trial conditions...")
                self.trial_conditions = self.self.generate_random_trial_conditions(last_trial, self.current_ror)
                if self.trial_conditions is None:
                    print("generate_random_trial_conditions returned None. Retrying...")
                else:
                    print(f"Successfully generated stimulus trials: {self.trial_conditions}")

        self.stim_trial = self.stim_trials[self.current_trial]
        self.trial_condition = self.trial_conditions[self.current_trial]

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
        if self.stage != 5:
            #First trial:
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
                # Closes corridor door 2 and delivers initial 100ul water.

            #Other Trials:
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
                state_change_conditions={Bpod.Events.Port1In: 'Exit'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 40)])
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
        else:
            print("Stage is 5. All repetitions completed. Task Ended.")

    def after_trial(self):
        if self.stage != 6:
            self.trial_counter += 1
            self.stim_trial_counter += 1

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

                # # Check if side bias is active and if the current trial was correct
                # if self.bias_breaking == 1:  # Side bias active
                #     self.biased_consecutive_corrects_counter += 1  # Increment counter for consecutive corrects
                #     if self.biased_consecutive_corrects_counter >= self.biased_consecutive_corrects:   #If three corrects after bias breaking
                #         self.bias_breaking = 0  # End bias breaking
                #         self.biased_consecutive_corrects_counter = 0  # Reset the consecutive corrects counter


            # ##### COUNT Touches outside the jar areas :
            elif self.current_trial_states['Touch_Outside'][0][0] > 0:
                self.status = 'Touch_Outside'

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
            self.accuracy = self.correct_count / self.valid_counter if self.current_trial > 0 else 0

            # Measure accuracy for every 12 trials using running_window
            if self.trial_counter % self.running_window == 0:
                trials_in_window = self.accwindow[-self.running_window:]  # Last 12 trials
                window_accuracy = sum(trials_in_window) / len(trials_in_window)
                print(f"Running Accuracy (Last Block: {window_accuracy:.2f}")

            if self.accuracy>=0.7:
                # Move the completed condition to completed_conditions
                self.completed_conditions.append(self.current_condition)
                # Move to the next condition, if any are left
                if self.conditions:
                    self.conditions.pop(0)  # Remove the completed condition
                    if self.conditions:
                        self.current_condition = self.conditions[0]  # Set new current condition
                    # If all conditions are completed, end the task
                    if not self.conditions:
                        self.stage == 6

                    # Reset trial counter for the new condition or new repetition cycle
                    self.trial_counter = 0


            # # Side Bias Breaking formula:
            # self.last_stim_trial = self.stim_trial
            #
            # try:
            #     # Try converting response_x directly to a float
            #     self.response_x_bias = float(self.response_x)
            # except ValueError:
            #     print(f"No response_x value or response other: {self.response_x}")
            #
            #     # Split the string by commas and convert it to a list of floats
            #     try:
            #         # First, check if the response_x is a string and split it
            #         response_x_list = [float(x) for x in self.response_x.split(",")]
            #
            #         # Use the last element of the list as response_x_bias
            #         self.response_x_bias = response_x_list[-1]
            #         print(f"Using last value from response_x array: {self.response_x_bias}")
            #     except Exception as e:
            #         #print(f"Failed to process response_x as array. Error: {e}")
            #         return  # Handle this case if needed
            #
            # # Append the response to the array:
            # #if self.status != 'Touch_Outside':  #Do not append responses in case of touches outside the area
            # self.response_x_array.append(self.response_x_bias)
            # print(f"Responses so far: {self.response_x_array}")
            #
            # #if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy < self.side_bias_trigger_acc:
            # if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy is not None and self.accuracy < self.side_bias_trigger_acc:
            #     # Check if all responses fall into one of the two defined categories
            #     all_left_side = all(45 < x < 145 for x in self.response_x_array)            #Check if all the reponses fall on left
            #     all_right_side = all(231 < x < 331 for x in self.response_x_array)          #Check if all the reponses fall on right
            #
            #     if all_left_side:
            #         self.sameside = 'left'
            #         self.bias_breaking = 1
            #         print('Bias breaking active, side:', self.sameside)
            #         self.last_stim_trial = 32               #Ensure last_stim_trial is 32
            #     elif all_right_side:
            #         self.sameside = 'right'
            #         self.bias_breaking = 1
            #         self.last_stim_trial = 31                  #Ensure last_stim_trial is 31
            #         print('Bias breaking active, side:', self.sameside)
            #
            #     self.response_x_array = []      #Clearing the array
        else:
            print("Stage is 5. All repetitions completed. Task Ended.")
            self.trial_length = 0.1
            self.trial_result = None


        ############ REGISTER VALUES ################
        #Working Memory:
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)
        self.register_value('choices', self.choices)
        #PI:
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
        self.register_value('substage', self.substage)
        self.register_value('trial_result', self.trial_result)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('accuracy', self.accuracy)
        #Bias Breaking:
        self.register_value('bias_breaking', self.bias_breaking)
        self.register_value('sameside', self.sameside)
        self.register_value('side_bias_trigger_acc', self.side_bias_trigger_acc)
        self.register_value('side_bias_trigger_trial', self.side_bias_trigger)
        self.register_value('biased_consecutive_corrects_counter', self.biased_consecutive_corrects_counter)
        self.register_value('biased_consecutive_corrects', self.biased_consecutive_corrects)
        #Weber's Law:
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
        # Weber's Law Training:
        self.register_value('ror', self.ror)
        self.register_value('current_ror', self.current_ror)
        self.register_value('completed_ror', self.completed_ror)