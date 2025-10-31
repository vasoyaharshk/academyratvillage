from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np

class Probability_WebersLaw_Pre(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This is the real weber's law file.
        This task displays the image of the jars which are touchable. This script is for Weber's law and the bias breaking is not active.
        ########   TASK INFO   ########
        Every 12 trials, the condition will change to a new one. 

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
        self.substage_bias = 0

        # Variables for the task:
        self.trials_max = 80
        self.duration_max = 3000
        self.duration_min = 2100
        self.duration_tired = 1800
        self.trials_tired = 5
        self.tired = False
        self.task_number = 3
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
        self.valve_factor_c = 1.0 # Normal water delivery of 25ul multiplied by this
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
        self.block = 12  # This is the number of trials one conditions will remain for
        self.conditions = []  # Takes the conditions from select task file.
        self.completed_conditions = []  # To store completed conditions
        self.current_condition = 0  # To track the current condition in progress
        self.repetition = 2  # To store how many times the conditions needs to repeat after the first initial run.
        self.current_repetition = 0  # To store how many times the condition has repeated.
        self.trial_counter = 0  # Track the number of trials for the current condition
        # Image output stims:
        self.stim_trial = 0
        self.stim_trials = []
        self.stim_trial_counter = 0

        self.running_window = self.block  # This is the number of trials the accuracy is measured by. It will take accuracy for every 12 trials.

        self.task_end = False

    def generate_alternating_conditions(self):
        # Define easy and hard conditions
        easy_conditions = [9, 10, 11, 12, 13, 14, 15, 16]
        hard_conditions = [1, 2, 3, 4, 5, 6, 7, 8]
        max_retries = 1000  # Limit retries to prevent excessive computation

        for attempt in range(max_retries):
            # Shuffle conditions for randomness
            random.shuffle(easy_conditions)
            random.shuffle(hard_conditions)
            total_conditions = len(easy_conditions) + len(hard_conditions)
            alternating_sequence = []

            def is_valid_candidate(sequence, candidate, is_easy):
                # Rule 1: No more than two hard or two easy in a row
                if len(sequence) >= 2 and (
                    all(c in hard_conditions for c in sequence[-2:]) and not is_easy or
                    all(c in easy_conditions for c in sequence[-2:]) and is_easy
                ):
                    return False
                # Rule 2: No more than two conditions in a row with same parity
                if len(sequence) >= 2 and sequence[-1] % 2 == sequence[-2] % 2 == candidate % 2:
                    return False
                # Rule 3: Always start with an easy condition
                if len(sequence) == 0 and not is_easy:
                    return False
                # Rule 4: Conditions 1 and 2 must be followed by an easy condition
                if len(sequence) > 0 and sequence[-1] in {1, 2} and not is_easy:
                    return False
                return True

            def backtrack(sequence, easy_idx, hard_idx):
                # If the sequence is complete, return it
                if len(sequence) == total_conditions:
                    return sequence
                # Try adding an easy condition if possible
                if easy_idx < len(easy_conditions):
                    candidate = easy_conditions[easy_idx]
                    if is_valid_candidate(sequence, candidate, True):
                        sequence.append(candidate)
                        result = backtrack(sequence, easy_idx + 1, hard_idx)
                        if result:
                            return result
                        sequence.pop()  # Backtrack
                # Try adding a hard condition if possible
                if hard_idx < len(hard_conditions):
                    candidate = hard_conditions[hard_idx]
                    if is_valid_candidate(sequence, candidate, False):
                        sequence.append(candidate)
                        result = backtrack(sequence, easy_idx, hard_idx + 1)
                        if result:
                            return result
                        sequence.pop()  # Backtrack
                return None  # No valid sequence found

            # Attempt to generate a sequence
            result = backtrack([], 0, 0)
            if result:
                return result  # Successfully generated a sequence

        # If all retries fail, raise an error
        raise RuntimeError("Unable to generate a valid sequence after multiple retries.")

    def validate_sequence(self, sequence):
        # Define easy and hard conditions
        easy_conditions = set([9, 10, 11, 12, 13, 14, 15, 16])
        hard_conditions = set([1, 2, 3, 4, 5, 6, 7, 8])

        # Dictionary to track rule violations
        rule_violations = {
            "no_more_than_two_hard_or_easy_in_a_row": False,
            "no_more_than_two_same_parity_in_a_row": False,
            "always_start_with_easy": False,
            "condition_1_2_followed_by_easy": False,
        }

        # Rule 3: Always start with an easy condition
        if len(sequence) == 0 or sequence[0] not in easy_conditions:
            rule_violations["always_start_with_easy"] = True

        for i in range(len(sequence)):
            # Rule 1: No more than two hard or two easy in a row
            if i >= 2 and (
                all(c in hard_conditions for c in sequence[i - 2:i + 1]) or
                all(c in easy_conditions for c in sequence[i - 2:i + 1])
            ):
                rule_violations["no_more_than_two_hard_or_easy_in_a_row"] = True
            # Rule 2: No more than two conditions in a row with same parity
            if i >= 2 and sequence[i] % 2 == sequence[i - 1] % 2 == sequence[i - 2] % 2:
                rule_violations["no_more_than_two_same_parity_in_a_row"] = True
            # Rule 4: Conditions 1 and 2 must be followed by an easy condition
            if sequence[i] in {1, 2} and i < len(sequence) - 1 and sequence[i + 1] not in easy_conditions:
                rule_violations["condition_1_2_followed_by_easy"] = True

        # Return rule violations
        return rule_violations

    def generate_random_trials(self, last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
        trials = []
        # Define a 50% probability for each stimulus (two stimuli)
        probabilities = [0.5, 0.5]  # Adjust this if you have more than two stimuli
        while len(trials) < self.block:
            # Use random.choices to select a candidate with 50% probability for each stimulus
            candidate = random.choices(self.stim, probabilities)[0]
            # Ensure no repetition more than twice in sequence
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                # Additionally, ensure the first trial doesn't repeat the last trial from the previous block
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue  # Skip if the first trial of new block matches last trial of previous block
                trials.append(candidate)
        return trials

    def generate_random_trials_ror1(self, last_trial=None):
        print(f"Starting generate_random_trials_ror1 with last_trial: {last_trial}")
        repetition_count = 3

        def generate_trials():
            all_trials = self.stim * repetition_count
            random.shuffle(all_trials)
            trials = []
            max_attempts = 1000
            attempts = 0

            def is_valid_candidate(candidate, trials):
                if len(trials) < 2:
                    return True
                return (
                        (candidate % 2 != trials[-1] % 2 or candidate % 2 != trials[-2] % 2)
                        and ((candidate <= 44) != (trials[-1] <= 44) or (candidate <= 44) != (trials[-2] <= 44))
                )

            while len(trials) < self.block:
                attempts += 1
                if attempts >= max_attempts:
                    print("Reached max_attempts in generate_trials.")
                    return None

                if not all_trials:
                    print("No candidates left in all_trials. Reinitializing.")
                    all_trials = self.stim * repetition_count
                    random.shuffle(all_trials)

                candidate = all_trials.pop(0)

                if len(trials) == 0 and last_trial is not None and candidate == last_trial:
                    continue

                if is_valid_candidate(candidate, trials):
                    trials.append(candidate)
                else:
                    all_trials.append(candidate)

            print("Generated trials:", trials)
            return trials

        try:
            result = generate_trials()
            if result is None:
                print("generate_trials returned None.")
            else:
                print(f"Generated trials successfully: {result}")
            return result
        except Exception as e:
            print(f"Error in generate_random_trials_ror1: {e}")
            return None

    def configure_gui(self):
        self.gui_input = ['duration_max', 'stage']

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Total Accuracy for session: ', self.accuracy)

        if not self.conditions and self.current_repetition == 0:
            while True:  # Retry until a valid sequence is generated
                self.conditions = self.generate_alternating_conditions()
                validation_results = self.validate_sequence(self.conditions)
                if not any(validation_results.values()):  # Ensure no rule violations
                    print("Conditions generated following the rules")
                    break  # Exit the loop if the sequence is valid
            self.current_condition = self.conditions[0]

        # Check if the current block of trials is complete
        if self.trial_counter >= self.block:
            # Move the completed condition to completed_conditions
            self.completed_conditions.append(self.current_condition)

            # Move to the next condition, if any are left
            if self.conditions:
                self.conditions.pop(0)  # Remove the completed condition
                if self.conditions:
                    self.current_condition = self.conditions[0]  # Set new current condition

            # If all conditions are completed, prepare for repetition
            if not self.conditions:
                self.current_repetition += 1
                if self.current_repetition <= self.repetition:
                    while True:  # Retry until a valid sequence is generated
                        self.conditions = self.generate_alternating_conditions()
                        validation_results = self.validate_sequence(self.conditions)
                        if not any(validation_results.values()):  # Ensure no rule violations
                            print("Conditions generated following the rules")
                            break  # Exit the loop if the sequence is valid
                    self.completed_conditions = []
                    self.current_condition = self.conditions[0]
                else:
                    self.stage = 5
                    self.tired = True
                    print("All repetitions completed. Task ending. Stage = 5")
                    self.sma.add_state(
                        state_name='Exit',
                        state_timer=0,
                        state_change_conditions={Bpod.Events.Tup: 'exit'},
                        output_actions=[])

            # Reset trial counter for the new condition or new repetition cycle
            self.trial_counter = 0
            self.stim_trial_counter = 0

        print(f"Block: {self.block}")
        print(f"Conditions: {self.conditions}")
        print(f"Completed Conditions: {self.completed_conditions}")
        print(f"Current Condition: {self.current_condition}")
        print(f"Repetition: {self.repetition}")
        print(f"Current Repetition: {self.current_repetition}")
        print(f"Trial Counter: {self.trial_counter}")

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        if self.current_condition in [1, 2]:
            self.stim = [43, 44, 45, 46]  # These are the functions being called. Odds are for the correct answer is on the left and Evens are when the correct answer is on the right
        else:
            self.stim = [41, 42]  # These are the functions being called. 41 is for the correct answer is on the left and 42 is when the correct answer is on the right

        # Stimulus generation logic: every 12 trials the stimulus location will be regenerated.
        if self.trial_counter % self.block == 0 and self.bias_breaking == 0:  # Re-randomize every 12 trials
            # If not the first block, pass the last stimulus of the previous block to avoid repetition
            self.stim_trial_counter = 0
            last_trial = self.stim_trials[self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None

            if self.current_condition in [1, 2]:
                print(f"Current condition is {self.current_condition}. Using generate_random_trials_ror1.")
                self.stim_trials = self.generate_random_trials_ror1(last_trial)
                print(f"Stimulus trials after first attempt: {self.stim_trials}")
                while self.stim_trials is None:
                    print("Retrying to generate stimulus trials...")
                    self.stim_trials = self.generate_random_trials_ror1(last_trial)
                    if self.stim_trials is None:
                        print("generate_random_trials_ror1 returned None. Retrying...")
                    else:
                        print(f"Successfully generated stimulus trials: {self.stim_trials}")
            else:
                self.stim_trials = self.generate_random_trials(last_trial)
                print('Stimulus List: ', self.stim_trials)

        if self.bias_breaking == 0:
            self.stim_trial = self.stim_trials[self.trial_counter % self.block]
        # else:
        #     self.stim_trial = self.last_stim_trial
        if self.stim_trial in [41, 43, 45]:
            self.x_correcth = self.x_correcth_pos[0]
            self.x_incorrecth = self.x_correcth_pos[1]
            print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)
        elif self.stim_trial in [42, 44, 46]:
            self.x_correcth = self.x_correcth_pos[1]
            self.x_incorrecth = self.x_correcth_pos[0]
            print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)

        print('Stimulus trial: ', self.stim_trial)
        print('Stimulus Trial Counter',self.stim_trial_counter)

        ############ STATE MACHINE ################
        if self.stage == 4:
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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 220)])
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
        if self.stage == 4:
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
            self.task_end = True


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
        self.register_value('task_number', self.task_number)
        self.register_value('stage', self.stage)
        self.register_value('substage', self.substage)
        self.register_value('substage_bias', self.substage_bias)
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