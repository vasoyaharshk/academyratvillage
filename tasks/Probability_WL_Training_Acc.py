from academy.task_collection import Task
from academy import telegram_bot
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
import os
import re
from academy import telegram_bot

class Probability_WL_Training_Acc(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This is the real weber's law file.
        This task displays the image of the jars which are touchable. This script is for Weber's law and the bias breaking is not active.
        ########   TASK INFO   ########
        This is the Weber's law training task where: 
        1. Training starts with RoR 16, then 12, 8, 6 (conditions 16 to 9) consecutively, only progressing to the next RoR when they meet 
        criteria: ≥80% success on 40 trials.
        2. Then they get ROR 4 – 1 (conditions 9 to 1) interleaved with easier RoRs (conditions 16 to 9). No more than 2 motivational or target in a row
        3. End point: Cut-off of 1000 trials per RoR of conditions 16 to 9.

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        # Non-used variables so that working memory works:
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
        self.task_number = 3
        self.stage = 5
        self.substage = 0
        self.response_duration = 60
        self.image_display = 3  # Number of seconds the image will display after correct and incorrect

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 3.0  # Normal water delivery of 25ul multiplied by this

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
        self.height = 225  # Stimulus height in mm. Original size for big jar is 125mm and small jar is 110mm.
        self.stim = [0]  # Calls functions to display Blue 1.png and function 26 to display Blue 2.png respectively.
        self.image_path_function = None
        self.image_displayed = None
        self.image_directory = None

        # Bias breaking variables, not used in Weber's Law:
        self.bias_breaking = 0  # If subject chooses same side for 5 trials in a row, bias breaking becomes active
        self.response_x_array = []  # Stores responses for x till 3 values
        self.sameside_counter = 0  # Counts number of times on same side
        self.sameside = None  # To track which side is being triggered
        self.side_bias_trigger = 5  # After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8  # Accuracy at which side bias will trigger
        self.status = None  # Stores the Touch_outside condition
        self.biased_consecutive_corrects_counter = 0  # This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3  ##This is the number of corrrects the rat needs to do to end bias breaking
        # New variables for 40 trial blocks:
        self.bias_accuracy_trials = []
        self.bias_accuracy = 0

        # Weber's Law Training Variables:
        # Variables not tracked:
        self.ror_to_conditions = {
            16.0: [16, 15],
            12.0: [14, 13],
            8.0: [12, 11],
            6.0: [10, 9],
            4.0: [8, 7],
            2.0: [6, 5],
            1.5: [4, 3],
        }
        self.motivational_conditions = [16, 15, 14,
                                        13]  # These are the actual motivational conditions that will be interleaved with RoR 4 and below
        self.motivational_ror = [16.0, 12.0, 8.0,
                                 6.0]  # This is the list of easy rors but called motivational here to make it easy for us
        self.target_ror = [4.0, 2.0, 1.5]  # This is the list of hard rors but called target here to make it easy for us
        self.allowed_conditions = []

        self.accuracy_criteria = 0.80  # 80% success on block_size(32/40 trials correct)
        self.trial_end_criteria = 1500
        self.previous_ror = 0
        self.success = 0  # tracks if trial is correct or incorrect (1 or 0)
        self.block_wlt = self.block_size

        # Variables tracked:
        self.ror = [16.0, 12.0, 8.0, 6.0, 4.0, 2.0, 1.5]
        self.completed_ror = []
        self.current_ror = 16.0
        self.trial_counter_ror = 0  # Track the number of trials for the current ror for only valid conditions.

        self.block_size = 40  # Every 40 blocks the criteria will be tested.
        self.block_trial_counter = 0  # Counter for block
        self.block_accuracy = 0.0  # Accuracy for that 40 trial block
        self.block_number = 1
        self.ror_change = 0
        self.block_change = 0
        self.last_stim_trial = 0  # It stores the correct side (L, R) of the last trial of the previous randomisation block
        self.last_condition_trial = 0  # It stores the condition of the last trial of the previous randomisation block
        self.total_trials = 0  # Total number of trials in that ROR irrespective of conditions
        self.block_correct_count = 0  # Tracks the number of corrects in the block
        self.block_valid_count = 0  ##Tracks the number of valid trials in the block

        self.stim_trial = 0
        self.stim_trials = []
        self.stim_trial_counter = 0
        self.condition_trial_counter = 0
        self.conditions = []

        self.task_end = False

    def get_stim_image_path(self, stim_trial, condition):
        """
        Determines whether stim_trial is 71 or 72, retrieves the corresponding image path, and returns it.
        """
        image_path = None
        image_folder = f'/home/harsh/academy/stimuli/webers_law/5_webers_law_training/{condition}'

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

    def generate_random_trials(self,
                               last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
        if last_trial == 0:
            last_trial = None
        trials = []
        # Define a 50% probability for each stimulus (two stimuli)
        probabilities = [0.5, 0.5]  # Adjust this if you have more than two stimuli
        while len(trials) < self.block_wlt:
            # Use random.choices to select a candidate with 50% probability for each stimulus
            candidate = random.choices(self.stim, probabilities)[0]
            # Ensure no repetition more than twice in sequence
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                # Additionally, ensure the first trial doesn't repeat the last trial from the previous block_wlt
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue  # Skip if the first trial of new block_wlt matches last trial of previous block_wlt
                trials.append(candidate)
        return trials

    def generate_random_trial_conditions_motivational(self, current_ror, last_trial=None):
        """
        Generate a list of conditions for a session based on the given ROR.
        """
        if last_trial == 0:
            last_trial = None

        if current_ror not in self.ror_to_conditions:
            raise ValueError("Invalid ROR value provided.")

        conditions_list = self.ror_to_conditions[current_ror]
        probabilities = [0.5, 0.5]  # 50% probability for each condition
        trials = []
        while len(trials) < self.block_wlt:
            # Randomly select a candidate condition with 50-50 probability
            candidate = random.choices(conditions_list, probabilities)[0]
            # Ensure no more than 2 consecutive same conditions_list
            if len(trials) >= 2 and candidate == trials[-1] == trials[-2]:
                continue
            # Ensure the first trial doesn't repeat the last trial from the previous block_wlt
            if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                continue
            # Add the candidate to trials
            trials.append(candidate)
        return trials

    def generate_random_trial_conditions_target(self, current_ror, last_trial=None):
        # Rules enforced by this function:
        # 1. Trial Type Constraints:
        #    - No more than two consecutive trials of the same type (target or motivational).
        #
        # 2. Parity Constraints:
        #    - No more than two consecutive trials with the same parity (odd or even).
        #
        # 3. Initial Trial Rule:
        #    - If a previous trial (`last_trial`) is provided, the parity of the first trial in the new sequence
        #      must not match the parity of `last_trial`.
        #
        # 4. ROR Proportion Rule:
        #    - The proportion of target to motivational trials is determined by the ROR (Rate of Reinforcement) parameter.
        #    - Proportions:
        #      ROR = 4   -> Hard: 60%, Easy: 40%
        #      ROR = 2   -> Hard: 60%, Easy: 40%
        #      ROR = 1.5 -> Hard: 60%, Easy: 40%
        #    - Proportions and counts must fall within ±2% of the expected values.
        #
        # 5. Hard Condition Distribution Rule:
        #    - Hard conditions_list are evenly distributed among their respective values.
        #      Example: For ROR=4, "8" and "7" split the target trials equally (50% each).
        #    - Edge cases (e.g., uneven splits due to rounding) are handled by assigning
        #      remaining trials to the first conditions_list in the list.
        #
        # 6. Randomization within Constraints:
        #    - Hard and motivational trials are shuffled to ensure no fixed ordering.
        #    - Randomization respects all constraints (e.g., type, parity, proportion).
        #
        # 7. Failure Handling:
        #    - If a valid sequence cannot be generated within the maximum attempts, an exception is raised.
        if last_trial == 0:
            last_trial = None

        def check_max_consecutive_type(seq, target_conditions):
            last_type = None
            count = 0
            for t in seq:
                current_type = "target" if t in target_conditions else "motivational"
                if current_type == last_type:
                    count += 1
                    if count > 2:
                        return False
                else:
                    last_type = current_type
                    count = 1
            return True

        def check_max_consecutive_parity(seq):
            def get_parity(t):
                return "odd" if t % 2 != 0 else "even"

            last_parity = None
            count = 0
            for t in seq:
                current_parity = get_parity(t)
                if current_parity == last_parity:
                    count += 1
                    if count > 2:
                        return False
                else:
                    last_parity = current_parity
                    count = 1
            return True

        # Hard conditions mapping
        ror_to_target_conditions = {
            4: [8, 7],
            2: [6, 5],
            1.5: [4, 3]
        }
        if current_ror not in ror_to_target_conditions:
            raise ValueError("Invalid ROR. Must be 4 or 2 or 1.5.")
        target_conditions = ror_to_target_conditions[current_ror]

        # Easy conditions
        motivational_conditions = self.motivational_conditions

        # ROR proportions
        ror_to_proportion = {
            4: 0.6,
            2: 0.6,
            1.5: 0.6
        }

        target_prop = ror_to_proportion[current_ror]
        target_count_total = int(round(self.block_wlt * target_prop))
        motivational_count_total = self.block_wlt - target_count_total

        print(f"Expected proportions -> Hard: {target_prop * 100:.2f}%, Easy: {(1 - target_prop) * 100:.2f}%")
        print(f"Expected counts -> Hard: {target_count_total}, Easy: {motivational_count_total}")

        # Distribute target conditions evenly
        num_target_conditions = len(target_conditions)
        target_count_per_condition = {c: target_count_total // num_target_conditions for c in target_conditions}
        remainder = target_count_total % num_target_conditions
        for i in range(remainder):
            c = target_conditions[i]
            target_count_per_condition[c] += 1

        # Distribute motivational conditions evenly
        num_motivational_conditions = len(motivational_conditions)
        motivational_count_per_condition = {c: motivational_count_total // num_motivational_conditions for c in
                                            motivational_conditions}
        remainder = motivational_count_total % num_motivational_conditions
        for i in range(remainder):
            c = motivational_conditions[i]
            motivational_count_per_condition[c] += 1

        target_trials = []
        for c, cnt in target_count_per_condition.items():
            target_trials += [c] * cnt

        motivational_trials = []
        for c, cnt in motivational_count_per_condition.items():
            motivational_trials += [c] * cnt

        random.shuffle(target_trials)
        random.shuffle(motivational_trials)

        def get_parity(t):
            return "odd" if t % 2 != 0 else "even"

        def is_valid_addition(seq, trial):
            # Check max consecutive type
            if len(seq) >= 2:
                last_two_types = ["target" if x in target_conditions else "motivational" for x in seq[-2:]]
                current_type = "target" if trial in target_conditions else "motivational"
                if last_two_types[0] == last_two_types[1] == current_type:
                    return False

            # Check max consecutive parity
            if len(seq) >= 2:
                last_two_parities = [get_parity(x) for x in seq[-2:]]
                current_parity = get_parity(trial)
                if last_two_parities[0] == last_two_parities[1] == current_parity:
                    return False

            # Last trial repetition rule (only for first trial)
            if len(seq) == 0 and last_trial is not None:
                first_p = get_parity(trial)
                last_p = get_parity(last_trial)
                if first_p == last_p:
                    return False

            return True

        max_attempts = 100000
        for attempt in range(max_attempts):
            sequence = []
            temp_target = target_trials.copy()
            temp_motivational = motivational_trials.copy()

            while len(sequence) < self.block_wlt:
                if len(sequence) >= 2:
                    last_two_types = ["target" if x in target_conditions else "motivational" for x in sequence[-2:]]
                    if last_two_types[0] == last_two_types[1] == "target":
                        possible_types = ["motivational"]
                    elif last_two_types[0] == last_two_types[1] == "motivational":
                        possible_types = ["target"]
                    else:
                        possible_types = ["target", "motivational"]
                else:
                    possible_types = ["target", "motivational"]

                random.shuffle(possible_types)
                added = False
                for ttype in possible_types:
                    if ttype == "target" and len(temp_target) > 0:
                        candidates = temp_target.copy()
                        random.shuffle(candidates)
                        for c in candidates:
                            if is_valid_addition(sequence, c):
                                sequence.append(c)
                                temp_target.remove(c)
                                added = True
                                break
                        if added:
                            break
                    elif ttype == "motivational" and len(temp_motivational) > 0:
                        candidates = temp_motivational.copy()
                        random.shuffle(candidates)
                        for e in candidates:
                            if is_valid_addition(sequence, e):
                                sequence.append(e)
                                temp_motivational.remove(e)
                                added = True
                                break
                        if added:
                            break

                if not added:
                    # Couldn't add a valid trial now, try another attempt
                    break

            if len(sequence) == self.block_wlt:
                # Validate
                target_count = sum(1 for x in sequence if x in target_conditions)
                motivational_count = self.block_wlt - target_count
                actual_target_prop = target_count / self.block_wlt
                expected_target_prop = ror_to_proportion[current_ror]

                print(
                    f"Generated proportions -> Hard: {actual_target_prop * 100:.2f}%, Easy: {(1 - actual_target_prop) * 100:.2f}%")
                print(f"Generated counts -> Hard: {target_count}, Easy: {motivational_count}")

                # Proportion tolerance ±2%
                if abs(actual_target_prop - expected_target_prop) > 0.02:
                    continue

                if not check_max_consecutive_type(sequence, target_conditions):
                    continue
                if not check_max_consecutive_parity(sequence):
                    continue

                if last_trial is not None:
                    first_p = get_parity(sequence[0])
                    last_p = get_parity(last_trial)
                    if first_p == last_p:
                        continue

                return sequence
        raise ValueError("Could not generate a valid sequence for given ROR and constraints within max_attempts.")

    def configure_gui(self):
        self.gui_input = ['duration_max', 'stage']

    def main_loop(self):
        print('')
        print('ROR: ', self.current_ror)
        print("Block Trial Counter: ", self.block_trial_counter)
        print("Block Accuracy: ", self.block_accuracy)
        print("Block Number: ", self.block_number)
        print("Block Change: ", self.block_change)
        print("ROR Change: ", self.ror_change)

        # print('Trial: ' + str(self.current_trial))
        # print('Total Accuracy for the session: ', self.accuracy)
        # print('stim_trial: ', self.stim_trial)
        # print('stim_trial_counter: ', self.stim_trial_counter)

        if self.current_trial == 0:
            self.bias_breaking = 0
            self.accuracy = 0
            # print("Move on to next ROR Accuracy Criteria: ", self.accuracy_criteria)
            self.block_wlt = self.block_size  # This is for presenting equal number of trial types every x trials.

        print('Bias Breaking: ', self.bias_breaking)
        # print('stim_trials: ', self.stim_trials)

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        self.stim = [61, 62]  # These are the functions being called. 61 is for the correct answer is on the left and 62 is when the correct answer is on the right

        if self.block_change == 1:
            self.block_number += 1
            self.block_change = 0
            self.block_accuracy = 0.0
            self.block_trial_counter = 0  # Reset the counter after the block
            self.block_correct_count = 0
            self.block_valid_count = 0

        if self.ror_change == 1:
            self.trial_counter_ror = 0
            if self.current_ror in self.ror:  # Ensure the current ROR exists in self.ror list
                print("ROR before update:", self.ror)
                # Append current_ror to completed_ror before removing it
                self.completed_ror.append(self.current_ror)
                print("Completed ROR after update:", self.completed_ror)
                # Remove current_ror from ror
                self.ror.remove(self.current_ror)
                print("ROR after removal:", self.ror)
                print("Block_accuracy:", self.block_accuracy)
                if self.ror:
                    self.current_ror = self.ror[0]
                    print(f"Updated current_ror: {self.current_ror}")
                else:
                    print("All RORs are completed. Task ends.")
                    self.tired = True
                    self.current_ror = 0
                    self.ror = []
                    self.completed_ror = []
                    self.stage = 4
                    self.block = 12
                    self.conditions = []
                    self.completed_conditions = []
                    self.current_condition = 0
                    self.repetition = 2
                    self.current_repetition = 0
                    self.trial_counter = 0
                    self.stim_trial = 0
                    self.stim_trials = []
                    self.stim_trial_counter = 0
                    self.substage = 0
            self.ror_change = 0  # Reset the flag so it only triggers once

        if self.stage == 5:
            # Stimulus generation logic: every 20 trials the stimulus location will be regenerated.
            if self.stim_trial_counter % self.block_wlt == 0 and self.bias_breaking == 0:  # Re-randomize every 20 trials
                # If not the first block_wlt, pass the last stimulus of the previous block_wlt to avoid repetition
                self.last_stim_trial = self.stim_trials[
                    self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None
                self.stim_trials = self.generate_random_trials(self.last_stim_trial)
                # print(f"Stimulus trials after first attempt: {self.stim_trials}")
                while self.stim_trials is None:
                    # print("Retrying to generate stimulus trials...")
                    self.stim_trials = self.generate_random_trials(self.last_stim_trial)
                    if self.stim_trials is None:
                        print("generate_random_trials returned None. Retrying...")
                    else:
                        print(f"Successfully generated stimulus trials: {self.stim_trials}")

                self.stim_trial_counter = 0

            print("Current_ror", self.current_ror)
            print("Previous_ror", self.previous_ror)

            # Stimulus generation logic: every 40 trials the stimulus CONDITIONS will be regenerated
            if self.current_ror != self.previous_ror or not self.conditions or self.condition_trial_counter % self.block_wlt == 0:
                self.last_condition_trial = self.conditions[self.condition_trial_counter - 1] if self.condition_trial_counter > 0 else 0
                if self.current_ror in self.motivational_ror:
                    self.conditions = self.generate_random_trial_conditions_motivational(self.current_ror,
                                                                                         self.last_condition_trial)
                    print(f"Trial conditions after first attempt: {self.conditions}")
                    while self.conditions is None:
                        # print("Retrying to generate trial conditions...")
                        self.conditions = self.generate_random_trial_conditions_motivational(self.current_ror,
                                                                                             self.last_condition_trial)
                        if self.conditions is None:
                            print("generate_random_trial_conditions_motivational returned None. Retrying...")
                        else:
                            print(f"Successfully generated stimulus trials: {self.conditions}")
                elif self.current_ror in self.target_ror:
                    self.conditions = self.generate_random_trial_conditions_target(self.current_ror,
                                                                                   self.last_condition_trial)
                    print(f"Trial conditions after first attempt: {self.conditions}")
                    while self.conditions is None:
                        # print("Retrying to generate trial conditions...")
                        self.conditions = self.generate_random_trial_conditions_target(self.current_ror,
                                                                                       self.last_condition_trial)
                        if self.conditions is None:
                            print("generate_random_trial_conditions_target returned None. Retrying...")
                        else:
                            print(f"Successfully generated stimulus trials: {self.conditions}")

                # Update previous ROR so that conditions won't be regenerated again until it changes.
                self.previous_ror = self.current_ror
                self.condition_trial_counter = 0  # Optionally reset your counter if needed.

            # self.trial_condition = self.conditions[self.condition_trial_counter % len(self.conditions)]

            self.trial_condition = self.conditions[self.condition_trial_counter]

            if self.bias_breaking == 0:
                self.stim_trial = self.stim_trials[self.stim_trial_counter]
            else:
                self.stim_trial = self.last_stim_trial

            if self.stim_trial == 61:
                self.x_correcth = self.x_correcth_pos[0]
                self.x_incorrecth = self.x_correcth_pos[1]
                # print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)
            elif self.stim_trial == 62:
                self.x_correcth = self.x_correcth_pos[1]
                self.x_incorrecth = self.x_correcth_pos[0]
                # print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)

            self.image_path_function = self.get_stim_image_path(self.stim_trial, self.trial_condition)

            directory, filename = os.path.split(self.image_path_function)
            self.image_displayed = filename
            self.image_directory = directory

            print('Stimulus Conditions', self.conditions)
            print('Stimulus Condition', self.trial_condition)
            print('Stimulus trial: ', self.stim_trial)
            print('Stimulus Trial Counter', self.stim_trial_counter)
            print('Stimulus Condition Counter', self.condition_trial_counter)

        ############ STATE MACHINE ################
        if self.stage == 5:
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
                # Closes corridor door 2 and delivers initial 100ul water.

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
                state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', 'SoftCode4': 'Punish',
                                         Bpod.Events.Tup: 'No_Touch'},
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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 63)])
            # Turns on Water port LED and displays correct stimuli for image_display (3 seconds)

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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 39)])
            # Turns on Global LED and water port LED on

            self.sma.add_state(
                state_name='Punish_image_display',
                state_timer=self.image_display,
                state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 64)])
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
        else:
            print("Stage is 4. All repetitions completed. Task Ended.")

    def after_trial(self):
        if self.stage == 5:
            self.total_trials += 1
            self.condition_trial_counter += 1  # checks for condition randomisation

            if self.bias_breaking == 0:
                self.stim_trial_counter += 1

            # This means that only the trials of the target conditions are counted towards the block (40 trials). This makes sure that the motivational trials from ror 4 down are not included.
            # This means that only the trials of the target conditions are counted towards the block (40 trials). This makes sure that the motivational trials from ror 4 down are not included.
            self.allowed_conditions = self.ror_to_conditions.get(self.current_ror, [])
            print(f"Checking accuracy for ROR: {self.current_ror}, Allowed Conditions: {self.allowed_conditions}")

            if self.trial_condition in self.allowed_conditions:
                #self.block_trial_counter += 1  # For counting the blocks
                self.trial_counter_ror += 1  # for the total trials in that ROR

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.accwindow = self.accwindow[1:] + [0]
                self.trial_result = 'miss'

            ##### COUNT PUNISH
            elif self.current_trial_states['Punish'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.valid_counter += 1
                if self.trial_condition in self.allowed_conditions:
                    self.block_valid_count += 1
                    self.block_trial_counter += 1
                    self.success = 0
                    print('Acc Valid_count: ', self.block_valid_count)
                self.accwindow = self.accwindow[1:] + [0]

            ##### COUNT CORRECTS FIRST POKE
            elif self.current_trial_states['Correct'][0][0] > 0:
                self.trial_result = 'correct'
                self.valid_counter += 1
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.accwindow = self.accwindow[1:] + [1]
                self.correct_count += 1
                print('Correct_count: ', self.correct_count)
                if self.trial_condition in self.allowed_conditions:
                    self.block_correct_count += 1
                    self.block_valid_count += 1
                    self.block_trial_counter += 1
                    self.success = 1
                    print('Acc Correct_count: ', self.block_correct_count)
                    print('Acc Valid_count: ', self.block_valid_count)

                # Check if side bias is active and if the current trial was correct and display the unbiased side three times:
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
            #print('Trial length: ' + str(self.trial_length))

            ### Checks if the rat is tired (rate of trial is low) and opens the gate after 30 mins rather than 35:
            if utils.chrono.get_seconds() >= self.duration_tired and self.trial_length > 45:
                self.tired_counter += 1
                if self.tired_counter > 2:
                    self.tired = True
                    print('Finishing task: subject tired')
            else:  # reset the counter
                self.tired_counter = 0

            # Compute overall accuracy for the session:
            self.accuracy = self.correct_count / self.valid_counter if self.valid_counter > 0 else 0

            # Check accuracy for every block of 40 trials
            self.block_accuracy = (
                self.block_correct_count / self.block_valid_count if self.block_valid_count > 0 else 0)
            print("Block Accuracy: ", self.block_accuracy)

            # Change block_trial_counter to block_trial_counter, and then block_counter should be the number of block.
            if self.block_trial_counter == self.block_size:
                self.block_change = 1
                if self.block_accuracy >= self.accuracy_criteria:
                    self.ror_change = 1  # Indicate that a ROR change is due
                else:
                    print("Accuracy criteria not met.")

            if self.trial_counter_ror >= self.trial_end_criteria:
                self.stage = 4
                self.tired = True
                print("Stage is 4. All RORs completed. Task Ended.")


            if self.trial_counter_ror % 216 == 0:
                message = f"URGENT PI: {self.subject} has completed {self.trial_counter_ror} trials in ROR {self.current_ror} in {self.task}. CHECK DATA"
                print(f'{message}')
                try:
                    telegram_bot.alarm_finish_session(message, self.subject)
                except:
                    print('Telegram message not sent')
                    pass

            # SIDE BIAS BREAKING FORMULA FROM HERE:

            # Calculate bias accuracy for the last five trials without using accuracy window
            self.bias_accuracy_trials.append(self.success)  # Append current trial success (0 or 1)
            if len(self.bias_accuracy_trials) > self.side_bias_trigger:
                self.bias_accuracy_trials.pop(0)  # Keep only the last 5 trials

            self.bias_accuracy = sum(self.bias_accuracy_trials) / len(
                self.bias_accuracy_trials) if self.bias_accuracy_trials else 0

            print(f"Bias Accuracy (last 5 trials): {self.bias_accuracy}")

            self.last_stim_trial = self.stim_trial

            try:
                # Try converting response_x directly to a float
                self.response_x_bias = float(self.response_x)
            except ValueError:
                #print(f"No response_x value or response other: {self.response_x}")

                # Split the string by commas and convert it to a list of floats
                try:
                    # First, check if the response_x is a string and split it
                    response_x_list = [float(x) for x in self.response_x.split(",")]

                    # Use the last element of the list as response_x_bias
                    self.response_x_bias = response_x_list[-1]
                    #print(f"Using last value from response_x array: {self.response_x_bias}")
                except Exception as e:
                    # print(f"Failed to process response_x as array. Error: {e}")
                    return

            # Append the response to the array:
            self.response_x_array.append(self.response_x_bias)
            #print(f"Responses so far: {self.response_x_array}")

            # if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy < self.side_bias_trigger_acc:
            if len(self.response_x_array) >= self.side_bias_trigger and self.bias_accuracy is not None and self.bias_accuracy < self.side_bias_trigger_acc:
                # Check if all responses fall into one of the two defined categories
                all_left_side = all(
                    45 < x < 145 for x in self.response_x_array)  # Check if all the responses fall on left
                all_right_side = all(
                    231 < x < 331 for x in self.response_x_array)  # Check if all the responses fall on right

                if all_left_side:
                    self.sameside = 'left'
                    self.bias_breaking = 1
                    print('Bias breaking active, side:', self.sameside)
                    self.last_stim_trial = 62  # Ensure last_stim_trial is 62
                elif all_right_side:
                    self.sameside = 'right'
                    self.bias_breaking = 1
                    self.last_stim_trial = 61  # Ensure last_stim_trial is 61
                    print('Bias breaking active, side:', self.sameside)

                self.response_x_array = []  # Clearing the array
        else:
            print("Stage is 4. All RORs completed. Task Ended.")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.task_end = True

        ############ REGISTER VALUES ################
        # Working Memory:
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)
        self.register_value('choices', self.choices)
        # PI:
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
        # Bias Breaking:
        self.register_value('bias_breaking', self.bias_breaking)
        self.register_value('sameside', self.sameside)
        self.register_value('side_bias_trigger_acc', self.side_bias_trigger_acc)
        self.register_value('side_bias_trigger_trial', self.side_bias_trigger)
        self.register_value('biased_consecutive_corrects_counter', self.biased_consecutive_corrects_counter)
        self.register_value('biased_consecutive_corrects', self.biased_consecutive_corrects)
        self.register_value('bias_accuracy_trials', self.bias_accuracy_trials)
        self.register_value('bias_accuracy', self.bias_accuracy)
        self.register_value('response_x_array', self.response_x_array)
        self.register_value('valve_factor_c', self.valve_factor_c)
        # #Weber's Law:
        # self.register_value('block', self.block)
        # self.register_value('conditions', self.conditions)
        # self.register_value('completed_conditions', self.completed_conditions)
        # self.register_value('current_condition', self.current_condition)
        # self.register_value('repetition', self.repetition)
        # self.register_value('current_repetition', self.current_repetition)
        # self.register_value('trial_counter', self.trial_counter)
        # self.register_value('stim_trial', self.stim_trial)
        # self.register_value('stim_trials', self.stim_trials)
        # self.register_value('stim_trial_counter', self.stim_trial_counter)
        # Weber's Law Training Tracked:
        self.register_value('ror', self.ror)
        self.register_value('completed_ror', self.completed_ror)
        self.register_value('current_ror', self.current_ror)
        self.register_value('trial_counter_ror', self.trial_counter_ror)
        self.register_value('block_size', self.block_size)
        self.register_value('block_trial_counter', self.block_trial_counter)
        self.register_value('block_accuracy', self.block_accuracy)
        self.register_value('block_number', self.block_number)
        self.register_value('ror_change', self.ror_change)
        self.register_value('block_change', self.block_change)
        self.register_value('last_stim_trial', self.last_stim_trial)
        self.register_value('last_condition_trial', self.last_condition_trial)
        self.register_value('total_trials', self.total_trials)
        # Weber's Law Training unTracked:
        self.register_value('motivational_conditions', self.motivational_conditions)
        self.register_value('motivational_ror', self.motivational_ror)
        self.register_value('target_ror', self.target_ror)
        self.register_value('block_wlt', self.block_wlt)
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)
        self.register_value('condition_trial_counter', self.condition_trial_counter)
        self.register_value('conditions', self.conditions)
        self.register_value('trial_condition', self.trial_condition)
        self.register_value('image_displayed', self.image_displayed)
        self.register_value('image_directory', self.image_directory)
        self.register_value('accuracy_criteria', self.accuracy_criteria)
        self.register_value('allowed_conditions', self.allowed_conditions)
        self.register_value('block_correct_count', self.block_correct_count)
        self.register_value('block_valid_count', self.block_valid_count)
        self.register_value('trial_end_criteria', self.trial_end_criteria)
        self.register_value('success', self.success)
