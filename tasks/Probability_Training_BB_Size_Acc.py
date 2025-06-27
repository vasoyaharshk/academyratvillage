from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
import os
import re
from academy import telegram_bot

class Probability_Training_BB_Size_Acc(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task displays the image of the jars which are touchable. This script is the main script now with side bias breaking.
        This script is where the jars are a mix of small and big.
        ########   TASK INFO   ########
        Stage 1: Indication: Only blue jar of pegs stimulus appears Blue is rewarding and yellow unrewarding
        Stage 2: Discrimination a: Blue and yellow jar of pegs appears (100% each). Combination of small and big jars.
        Stage 3: Discrimination b: Blue and yellow jar of pegs appears (1 jar is 100% of unrewarded color yellow and the other is 50%). Combination of small and big jars.
        Stage 4: Discrimination c: Spacers: Blue and yellow jar of pegs appears (1 jar is 100% of unrewarded color yellow and the other is 50%). Combination of small and big jars with spacers.        
                
                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        # ==============================
        # Tracked Variables
        # ==============================
        # Needed in Each Task:
        self.stage = 1  # Current stage within the task
        self.substage = 0  # Current substage within the stage
        self.substage_bias = 0  # Side bias stage for substage behavior
        self.task_number = 2  # Each task has a unique number. See RV script guide.

        # Needed to create blocks of 40 trials for criterion to be assessed on:
        self.block_size = 40  # The number of trials in a block
        self.block_trial_counter = 0  # Trial count within the current block
        self.block_accuracy = 0.0  # Accuracy in the current block
        self.block_number = 0  # Sequential block number
        self.ror_change = 0  # If it is 1, ROR will change on the next trial.
        self.block_change = 0  # If it is 1, a new block will start on the next trial
        self.total_trials = 0  # Total trials across the task.
        self.block_correct_count = 0  # Number of correct responses in the block
        self.block_valid_count = 0  # Number of valid (non-missed) trials in the block
        self.condition_trial_counter = 0  # Counter for randomising conditions
        self.last_forward_stage = 0  # The stage moved forward from after a forward change
        self.last_backward_stage = 0  # The stage moved backward to after the last backward change
        self.moved_back_counter = 0  # Counter for how many times the subject moved back a stage
        self.stage_forward_change = 0  # Whether stage move forward on the next trial
        self.stage_backward_change = 0  # Whether stage move backward on the next trial

        # Left Right Function Randomisation variables:
        self.stim_trial = 0  # The function number of the correct stimulus in the current trial. This designates trial type, e.g. from Discrim. C: left is correct, big jar is correct, spacer in correct
        self.stim_trials = []  # List of correct stimulus function randomised.
        self.stim_trial_counter = 0  # It counts the number of trials within a randomization block. Doesnt change when Bias breaking is active.
        self.last_stim_trial = 0  # the function of the last trial of the previous block. Used to ensure first trial of next block is different

        # ==============================
        # Untracked Variables
        # ==============================
        # Task specific:
        self.accuracy_criteria = 0.80  # move forward criteria. 80% success on block_size(32/40 trials correct)
        self.trial_end_criteria = 320  # Move back criteria. Badly named - this is task end criteria.
        self.max_move_backs = 5  # number of times they can be moved back (i.e., they've done 320 trials 5 times) before we review
        self.probabilities_size = [0.5, 0.5]
        self.probabilities_side = [0.5, 0.5]
        self.probabilities_spacer = [0.5, 0.5]

        # Trial Specific:
        self.duration_max = 3000  # Maximum duration of the task. 50 mins
        self.duration_min = 2100  # Minimum duration of the task. 35 mins.
        self.duration_tired = 1800  # Duration for the door to open (30 mins) if the animal is inactive. Less than 5 trials.
        self.trials_tired = 5  # if they do 5 trials of long duration (more than 45 seconds), the door will open after 30 mins rather than 35
        self.tired = False  # The door 2 opens whenever this is true. Used to end the task.
        self.response_duration = 60  # The response time after the last photogate has been crossed in secs.
        self.image_display = 3        #Number of seconds the image will display after correct and incorrect

        # Pump:
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration  # The duration the water valve needs to be open for. Takes the value from the water_calibration.csv
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions. Takes the value from water_caliberation.csv
        self.valve_factor_c = 1.0  # Normal water delivery must be a multiple of 25ul. 2.0 is 2 x 25 = 50uL. E.g., if you set it to 1.8, this would be 1.8 x 25 = 45uL
        self.valve_factor_i = 0.6  # Water delivery for incorrects/punish - only if want to give water if they do an incorrect trial (only used for scripts that allow correction)

        # Counters for trials:
        self.valid_counter = 0  # Counter for valid counts in a session
        self.tired_counter = 0  # Counter for longer duration trials (more than 45 secs) in a session
        self.reward_drunk = 0  # Amount of water drunk in the session
        self.correct_count = 0  # Counter for correct counts in a session
        self.accuracy = 0  # Accuracy of the session
        self.success = 0  # tracks if trial is correct or incorrect (1 or 0)
        self.status = None  # Stores the Touch_outside condition

        # Image output stims:
        self.stim = [0]  # Lists which defines both the functions for left and right.

        # Correcth location and size:
        self.x_correcth_pos = [95, 281]  # Horizontal Coordinates for left and right for Jars
        self.y_correcth = 110  # Vertical Coordinates for left and right for Jars
        self.width = 100  # Stimulus width in mm. Original size for jar is 120mm.
        self.height = 190   # Stimulus height in mm. Original size for jar is 110mm.
        self.image_path_function = None  # Full Path for the image displayed
        self.image_displayed = None  # The image which is displayed
        self.image_directory = None  # The directory of the image displayed

        #Bias breaking variables:
        self.bias_breaking = 0  # If subject chooses same side for 5 trials in a row, bias breaking becomes 1
        self.response_x_array = []  # Stores responses for x till 5 values
        self.sameside_counter = 0       #Counts number of times on same side
        self.sameside = None  # To track which side is being triggered for bias breaking
        self.side_bias_trigger = 5      #After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8  # Side_bias triggers if accuracy is below this for the last 5 trials
        self.biased_consecutive_corrects_counter = 0       #This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3  # This is the number of corrects the rat needs to do to end bias breaking
        self.bias_accuracy_trials = []  # List that holds the last five success or failures.
        self.bias_accuracy = 0  # Accuracy of the last five trials.

        self.task_end = False


    def configure_gui(self):
        self.gui_input = ['stage', 'substage', 'duration_max', 'task_number', 'block_size']

    # def generate_random_trials_position_size(self, last_trial=None):
    #     """
    #     This function generates a sequence of trials ensuring the following constraints:
    #     1. No more than two consecutive trials should have the same size ('small' or 'big').
    #     2. No more than two consecutive trials should have the same position ('left' or 'right').
    #     3. The first trial of the new block must also follow these constraints relative to the last trial of the previous block.
    #     """
    #     print(f"Starting generate_random_trials_ror1 with last_trial: {last_trial}")
    #
    #     def generate_trials():
    #         all_trials = self.stim * 100  # Ensure enough trials to randomize from
    #         random.shuffle(all_trials)
    #         trials = []
    #         max_attempts = 10000
    #         attempts = 0
    #
    #         def get_size(trial):
    #             return 'small' if trial in [101, 102] else 'big'
    #
    #         def get_position(trial):
    #             return 'left' if trial in [101, 103] else 'right'
    #
    #         def is_valid_candidate(candidate, trials):
    #             if len(trials) < 2:
    #                 return True
    #             return (
    #                     get_size(candidate) != get_size(trials[-1]) or get_size(candidate) != get_size(trials[-2])
    #             ) and (
    #                     get_position(candidate) != get_position(trials[-1]) or get_position(candidate) != get_position(
    #                 trials[-2])
    #             )
    #
    #         first_trial_selected = False
    #         while len(trials) < self.block_size:
    #             attempts += 1
    #             if attempts >= max_attempts:
    #                 print("Reached max_attempts in generate_trials.")
    #                 return None
    #             if not all_trials:
    #                 print("No candidates left in all_trials. Reinitializing.")
    #                 all_trials = self.stim * 100
    #                 random.shuffle(all_trials)
    #             candidate = all_trials.pop(0)
    #             if len(trials) == 0 and last_trial is not None and not first_trial_selected:
    #                 if get_size(candidate) == get_size(last_trial) or get_position(candidate) == get_position(
    #                         last_trial):
    #                     continue
    #                 first_trial_selected = True
    #             if is_valid_candidate(candidate, trials):
    #                 trials.append(candidate)
    #             else:
    #                 all_trials.append(candidate)
    #         print("Generated trials:", trials)
    #         return trials
    #
    #     try:
    #         result = generate_trials()
    #         if result is None:
    #             print("generate_trials returned None.")
    #         else:
    #             print(f"Generated trials successfully: {result}")
    #         return result
    #     except Exception as e:
    #         print(f"Error in generate_random_trials_ror1: {e}")
    #         return None

    def generate_random_trials_position_size_weighted(self, last_trial=None):
        print(f"Starting generate_random_trials_ror1 with last_trial: {last_trial}")

        def generate_trials():
            tolerance = 0.05
            all_trials = self.stim * 100  # Ensure enough trials to randomize from
            random.shuffle(all_trials)
            trials = []
            max_attempts = 10000
            attempts = 0

            def get_size(trial):
                return 'small' if trial in [101, 102] else 'big'

            def get_position(trial):
                return 'left' if trial in [101, 103] else 'right'

            def current_counts(trials):
                count_small = sum(1 for t in trials if get_size(t) == 'small')
                count_big = len(trials) - count_small
                count_left = sum(1 for t in trials if get_position(t) == 'left')
                count_right = len(trials) - count_left
                return count_small, count_big, count_left, count_right

            def is_valid_candidate(candidate, trials):
                if len(trials) < 2:
                    return True
                same_size = get_size(candidate) == get_size(trials[-1]) == get_size(trials[-2])
                same_pos = get_position(candidate) == get_position(trials[-1]) == get_position(trials[-2])
                return not (same_size or same_pos)

            self.random_block = self.block_size
            max_small = round(self.probabilities_size[0] * self.random_block + tolerance * self.random_block)
            max_big = round(self.probabilities_size[1] * self.random_block + tolerance * self.random_block)
            max_left = round(self.probabilities_side[0] * self.random_block + tolerance * self.random_block)
            max_right = round(self.probabilities_side[1] * self.random_block + tolerance * self.random_block)

            first_trial_selected = False
            while len(trials) < self.random_block:
                attempts += 1
                if attempts >= max_attempts:
                    print("Reached max_attempts in generate_trials.")
                    return None
                if not all_trials:
                    print("No candidates left in all_trials. Reinitializing.")
                    all_trials = self.stim * 100
                    random.shuffle(all_trials)
                candidate = all_trials.pop(0)

                if len(trials) == 0 and last_trial is not None and not first_trial_selected:
                    if get_size(candidate) == get_size(last_trial) or get_position(candidate) == get_position(
                            last_trial):
                        continue
                    first_trial_selected = True

                count_small, count_big, count_left, count_right = current_counts(trials)
                if get_size(candidate) == 'small' and count_small >= max_small:
                    continue
                if get_size(candidate) == 'big' and count_big >= max_big:
                    continue
                if get_position(candidate) == 'left' and count_left >= max_left:
                    continue
                if get_position(candidate) == 'right' and count_right >= max_right:
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

    # def generate_random_trials_position_size_spacers(self, last_trial=None):
    #     """
    #     This function generates a sequence of trials ensuring the following constraints:
    #     1. No more than two consecutive trials should have the same size ('small' or 'big').
    #     2. No more than two consecutive trials should have the same position ('left' or 'right').
    #     3. No more than two consecutive trials should have the spacer.
    #     4. The first trial of the new block must also follow these three constraints relative to the last trial of the previous block.
    #     """
    #     print(f"Function failed to generate trials with last_trial: {last_trial}")
    #
    #     def generate_trials():
    #         all_trials = self.stim * 100
    #         random.shuffle(all_trials)
    #         trials = []
    #         max_attempts = 10000
    #         attempts = 0
    #
    #         def get_size(trial):
    #             return 'small' if trial in [101, 102, 105, 106] else 'big'
    #
    #         def get_position(trial):
    #             return 'left' if trial in [101, 103, 105, 107] else 'right'
    #
    #         def get_spacer(trial):
    #             return 'spacer' if trial in [105, 106, 107, 108] else 'no spacer'
    #
    #         def is_valid_candidate(candidate, trials):
    #             if len(trials) < 2:
    #                 return True
    #             return (
    #                     (get_size(candidate) != get_size(trials[-1]) or get_size(candidate) != get_size(trials[-2])) and
    #                     (get_position(candidate) != get_position(trials[-1]) or get_position(candidate) != get_position(
    #                         trials[-2])) and
    #                     (get_spacer(candidate) != get_spacer(trials[-1]) or get_spacer(candidate) != get_spacer(
    #                         trials[-2]))
    #             )
    #
    #         first_trial_selected = False
    #         while len(trials) < self.block_size:
    #             attempts += 1
    #             if attempts >= max_attempts:
    #                 print("Reached max_attempts in generate_trials.")
    #                 return None
    #             if not all_trials:
    #                 print("No candidates left in all_trials. Reinitializing.")
    #                 all_trials = self.stim * 100
    #                 random.shuffle(all_trials)
    #             candidate = all_trials.pop(0)
    #             if len(trials) == 0 and last_trial is not None and not first_trial_selected:
    #                 if (
    #                         get_size(candidate) == get_size(last_trial) or
    #                         get_position(candidate) == get_position(last_trial) or
    #                         get_spacer(candidate) == get_spacer(last_trial)
    #                 ):
    #                     continue
    #                 first_trial_selected = True
    #             if is_valid_candidate(candidate, trials):
    #                 trials.append(candidate)
    #             else:
    #                 all_trials.append(candidate)
    #         print("Generated trials:", trials)
    #         return trials
    #
    #     try:
    #         result = generate_trials()
    #         if result is None:
    #             print("generate_trials returned None.")
    #         else:
    #             print(f"Generated trials successfully: {result}")
    #         return result
    #     except Exception as e:
    #         print(f"Error in generating trial stims: {e}")
    #         return None

    def generate_random_trials_position_size_spacers_weighted(self, last_trial=None):
        print(f"Starting generate_random_trials_position_size_spacers_weighted with last_trial: {last_trial}")

        def generate_trials():
            tolerance = 0.05
            all_trials = self.stim * 100
            random.shuffle(all_trials)
            trials = []
            max_attempts = 10000
            attempts = 0

            def get_size(trial):
                return 'small' if trial in [101, 102, 105, 106] else 'big'

            def get_position(trial):
                return 'left' if trial in [101, 103, 105, 107] else 'right'

            def get_spacer(trial):
                return 'spacer' if trial in [105, 106, 107, 108] else 'no spacer'

            def current_counts(trials):
                count_small = sum(1 for t in trials if get_size(t) == 'small')
                count_big = len(trials) - count_small
                count_left = sum(1 for t in trials if get_position(t) == 'left')
                count_right = len(trials) - count_left
                count_spacer = sum(1 for t in trials if get_spacer(t) == 'spacer')
                count_no_spacer = len(trials) - count_spacer
                return count_small, count_big, count_left, count_right, count_spacer, count_no_spacer

            def is_valid_candidate(candidate, trials):
                if len(trials) < 2:
                    return True
                same_size = get_size(candidate) == get_size(trials[-1]) == get_size(trials[-2])
                same_pos = get_position(candidate) == get_position(trials[-1]) == get_position(trials[-2])
                same_spacer = get_spacer(candidate) == get_spacer(trials[-1]) == get_spacer(trials[-2])
                return not (same_size or same_pos or same_spacer)

            self.random_block = self.block_size
            max_small = round(self.probabilities_size[0] * self.random_block + tolerance * self.random_block)
            max_big = round(self.probabilities_size[1] * self.random_block + tolerance * self.random_block)
            max_left = round(self.probabilities_side[0] * self.random_block + tolerance * self.random_block)
            max_right = round(self.probabilities_side[1] * self.random_block + tolerance * self.random_block)
            max_spacer = round(self.probabilities_spacer[0] * self.random_block + tolerance * self.random_block)
            max_no_spacer = round(self.probabilities_spacer[1] * self.random_block + tolerance * self.random_block)

            first_trial_selected = False
            while len(trials) < self.random_block:
                attempts += 1
                if attempts >= max_attempts:
                    print("Reached max_attempts in generate_trials.")
                    return None
                if not all_trials:
                    print("No candidates left in all_trials. Reinitializing.")
                    all_trials = self.stim * 100
                    random.shuffle(all_trials)
                candidate = all_trials.pop(0)

                if len(trials) == 0 and last_trial is not None and not first_trial_selected:
                    if (
                        get_size(candidate) == get_size(last_trial) or
                        get_position(candidate) == get_position(last_trial) or
                        get_spacer(candidate) == get_spacer(last_trial)
                    ):
                        continue
                    first_trial_selected = True

                count_small, count_big, count_left, count_right, count_spacer, count_no_spacer = current_counts(trials)
                if get_size(candidate) == 'small' and count_small >= max_small:
                    continue
                if get_size(candidate) == 'big' and count_big >= max_big:
                    continue
                if get_position(candidate) == 'left' and count_left >= max_left:
                    continue
                if get_position(candidate) == 'right' and count_right >= max_right:
                    continue
                if get_spacer(candidate) == 'spacer' and count_spacer >= max_spacer:
                    continue
                if get_spacer(candidate) == 'no spacer' and count_no_spacer >= max_no_spacer:
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
            print(f"Error in generating trial stims: {e}")
            return None


    def get_stim_image_path(self, stim_trial, stage):
        image_path = None
        image_folder = None
        try:
            if stim_trial in [101, 105]:
                position = 'left'
                size = 'small'
            elif stim_trial in [102, 106]:
                position = 'right'
                size = 'small'
            elif stim_trial in [103, 107]:
                position = 'left'
                size = 'big'
            elif stim_trial in [104, 108]:
                position = 'right'
                size = 'big'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}.")

            spacer = 'spacer' if stim_trial in [105, 106, 107, 108] else ''

            if stage == 1:
                image_folder = '/home/harsh/academy/stimuli/urn_training/1_indication'
            elif stage == 2:
                image_folder = '/home/harsh/academy/stimuli/urn_training/2_discrimination_a'
            elif stage == 3:
                image_folder = '/home/harsh/academy/stimuli/urn_training/3_discrimination_b'
            elif stage == 4:
                image_folder = '/home/harsh/academy/stimuli/urn_training/4_discrimination_c'
            else:
                raise ValueError(f"Invalid stage value: {stage}.")

            images = [f for f in os.listdir(image_folder) if
                      os.path.isfile(os.path.join(image_folder, f)) and
                      (position in f.lower() and 'both' in f.lower() and size in f.lower() and (
                          spacer in f.lower() if spacer else True))]
            if not images:
                raise ValueError(
                    f"No images found in {image_folder} for stage {stage}, position {position}, size {size}, and spacer {spacer}.")

            image_path = os.path.join(image_folder, random.choice(images))
            print(f'Stage in function: {stage}')
            print(f'Correct answer on {position}, {size}, {spacer} jar: {image_path}')
        except Exception as e:
            print(f"Error occurred: {e}")
        return image_path

    def main_loop(self):
        print('')
        if self.current_trial == 0:
            self.bias_breaking = 0
            self.accuracy = 0
            # print("Move on to next ROR Accuracy Criteria: ", self.accuracy_criteria)

        print('Bias Breaking: ', self.bias_breaking)
        # print('stim_trials: ', self.stim_trials)

        if self.block_change == 1:
            self.block_number += 1
            self.block_change = 0
            self.block_accuracy = 0.0
            self.block_trial_counter = 0  # Reset the counter after the block
            self.block_correct_count = 0
            self.block_valid_count = 0
            self.stim_trial_counter = 0

        if self.stage_forward_change == 1:
            self.total_trials = 0
            self.stage_forward_change = 0
            self.last_forward_stage = self.stage  # Save current BEFORE increasing
            self.stage += 1
            message = f"Stage moved forward to {self.stage} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except Exception as e:
                print(f"Telegram message not sent. Error: {e}")
            if self.stage == 5:
                self.task_number = 3
                self.tired = True

        if self.stage_backward_change == 1:
            self.total_trials = 0
            self.stage_backward_change = 0
            self.block_accuracy = 0.0
            self.block_trial_counter = 0  # Reset the counter after the block
            self.block_correct_count = 0
            self.block_valid_count = 0
            self.stim_trial_counter = 0
            new_stage = max(self.stage - 1, 1)
            if new_stage == self.last_forward_stage:
                if self.last_backward_stage == new_stage:
                    self.moved_back_counter += 1
                else:
                    self.moved_back_counter = 1
                    self.last_backward_stage = new_stage
            else:
                self.moved_back_counter = 1
                self.last_backward_stage = new_stage
            self.stage = new_stage
            message = f"Stage moved backward to {self.stage} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except:
                print("Telegram message not sent")

        ### Randomizing the stimulus positions for both the images:
        # Choose x positions:
        if self.stage == 4:
            self.stim = [101, 102, 103, 104, 105, 106, 107, 108]  # Correct Answer 101-102: small (left/right), 103-104: big (left/right) without spacer; 105-106: small (left/right), 107-108: big (left/right) with spacer. All odd numbers are for left and even numbers for right
        else:
            self.stim = [101, 102, 103, 104]

        if self.task_number == 2:
            # Stimulus generation logic
            if self.stage == 4:
                if self.stim_trial_counter % self.block_size == 0 and self.bias_breaking == 0:  # Re-randomize every 20 trials
                    # If not the first block_size, pass the last stimulus of the previous block_size to avoid repetition
                    self.last_stim_trial = self.stim_trials[self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None
                    self.stim_trials = self.generate_random_trials_position_size_spacers_weighted(self.last_stim_trial)
                    print(f"Stimulus trials after first attempt: {self.stim_trials}")
                    while self.stim_trials is None:
                        print("Retrying to generate stimulus trials...")
                        self.stim_trials = self.generate_random_trials_position_size_spacers_weighted(self.last_stim_trial)
                        if self.stim_trials is None:
                            print("generate_random_trials returned None. Retrying...")
                        else:
                            print(f"Successfully generated stimulus trials: {self.stim_trials}")
                    self.stim_trial_counter = 0
            else:
                if self.stim_trial_counter % self.block_size == 0 and self.bias_breaking == 0:  # Re-randomize every 10 trials
                    # If not the first block_size, pass the last stimulus of the previous block_size to avoid repetition
                    self.last_stim_trial = self.stim_trials[self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None
                    self.stim_trials = self.generate_random_trials_position_size_weighted(self.last_stim_trial)
                    print(f"Stimulus trials after first attempt: {self.stim_trials}")
                    while self.stim_trials is None:
                        print("Retrying to generate stimulus trials...")
                        self.stim_trials = self.generate_random_trials_position_size_weighted(self.last_stim_trial)
                        if self.stim_trials is None:
                            print("generate_random_trials returned None. Retrying...")
                        else:
                            print(f"Successfully generated stimulus trials: {self.stim_trials}")
                    self.stim_trial_counter = 0

            if self.bias_breaking == 0:
                self.stim_trial = self.stim_trials[self.stim_trial_counter]
            else:
                self.stim_trial = self.last_stim_trial
                print('last_stim_trial', self.last_stim_trial)

            if self.stage == 1:  # We have only one stimuli in stage 1
                self.image_display = 0
                # Here, if we need to define the correcth_x position based on the stimulus. So function 101 displays stimulus with correct answer on the left (x=115) and 102 displays stimulus with correct answer on right (x=295)
                if self.stim_trial in [101, 103, 105, 107]:
                    self.x_correcth = self.x_correcth_pos[0]
                    self.x_incorrecth = None  # No incorrect area in stage 1
                    print('Correct Answer: Left, ', 'X position = ', self.x_correcth)
                elif self.stim_trial in [102, 104, 106, 108]:
                    self.x_correcth = self.x_correcth_pos[1]
                    self.x_incorrecth = None  # No incorrect area in stage 1
                    print('Correct Answer: Right, ', 'X position = ', self.x_correcth)
            else:  # We have two stimuli after stage 1 with correct and incorrect areas
                self.image_display = 3
                if self.stim_trial in [101, 103, 105, 107]:
                    self.x_correcth = self.x_correcth_pos[0]
                    self.x_incorrecth = self.x_correcth_pos[1]
                    print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)
                elif self.stim_trial in [102, 104, 106, 108]:
                    self.x_correcth = self.x_correcth_pos[1]
                    self.x_incorrecth = self.x_correcth_pos[0]
                    print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ', self.x_incorrecth)

            if self.task_number == 2:
                self.image_path_function = self.get_stim_image_path(self.stim_trial, self.stage)
                print("image_path_function: ", self.image_path_function)

                directory, filename = os.path.split(self.image_path_function)
                self.image_displayed = filename
                self.image_directory = directory

            print('Stimulus trial: ', self.stim_trial)
            print('Stimulus Trial Counter', self.stim_trial_counter)
            print('Stage before Bpod', self.stage)

        ############ STATE MACHINE ################
        #First trial:
        if self.task_number == 2:
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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 63)])
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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6), (Bpod.OutputChannels.SoftCode, 64)])
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
            print("Task 2 ended because Core training completed. Task is now 3 so will move to Weber's law in next session.")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.x_correcth = None
            self.x_incorrecth = None
            self.response_x = None
            self.response_y = None
            self.trial_length = None
            self.trial_result = None


    def after_trial(self):
        if self.task_number == 2:
                # self.block_trial_counter += 1  # For counting the blocks

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.trial_result = 'miss'

            ##### COUNT PUNISH
            elif self.current_trial_states['Punish'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.valid_counter += 1
                self.block_valid_count += 1
                self.success = 0
                self.block_trial_counter += 1
                self.total_trials += 1
                if self.bias_breaking == 0:
                    self.stim_trial_counter += 1
                print('Acc Valid_count: ', self.block_valid_count)

            ##### COUNT CORRECTS FIRST POKE
            elif self.current_trial_states['Correct'][0][0] > 0:
                self.trial_result = 'correct'
                self.valid_counter += 1
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.correct_count += 1
                #print('Correct_count: ', self.correct_count)
                self.block_correct_count += 1
                self.block_valid_count += 1
                self.block_trial_counter += 1
                self.success = 1
                self.total_trials += 1
                if self.bias_breaking == 0:
                    self.stim_trial_counter += 1
                print('Acc Correct_count: ', self.block_correct_count)
                print('Acc Valid_count: ', self.block_valid_count)

                # Check if side bias is active and if the current trial was correct
                if self.bias_breaking == 1:  # Side bias active
                    self.biased_consecutive_corrects_counter += 1  # Increment counter for consecutive corrects
                    if self.biased_consecutive_corrects_counter >= self.biased_consecutive_corrects:   #If three corrects after bias breaking
                        self.bias_breaking = 0  # End bias breaking
                        self.stim_trial_counter = 0
                        self.biased_consecutive_corrects_counter = 0  # Reset the consecutive corrects counter


            # ##### COUNT Touches outside the jar areas :
            elif self.current_trial_states['Touch_Outside'][0][0] > 0:
                self.status = 'Touch_Outside'

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

            # Check accuracy for every block of 40 trials
            self.block_accuracy = (self.block_correct_count / self.block_valid_count if self.block_valid_count > 0 else 0)
            print("Block Accuracy: ", self.block_accuracy)

            # Change block_trial_counter to block_trial_counter, and then block_counter should be the number of block.
            if self.block_trial_counter == self.block_size:
                self.block_change = 1
                if self.block_accuracy >= self.accuracy_criteria:
                    self.stage_forward_change = 1  # Indicate that a stage change is due
                else:
                    print("Accuracy criteria not met.")

            if self.total_trials >= self.trial_end_criteria:
                self.stage_backward_change = 1

            #Assign in pass what to do when the rat is moved back more than 5 times.
            if self.moved_back_counter > self.max_move_backs:
                message = f"URGENT: Moved back {self.moved_back_counter} for {self.subject}. CHECK DATA."
                try:
                    telegram_bot.alarm_finish_session(message, self.subject)
                except:
                    print('Telegram message not sent')
                    pass

            if self.stage > self.last_backward_stage + 1:
                self.moved_back_counter = 0

            print("After trial changes: ")
            print("Block Trial Counter: ", self.block_trial_counter)
            print("Block Accuracy: ", self.block_accuracy)
            print("Block Number: ", self.block_number)
            print("Block Size: ", self.block_size)
            print("Task Number: ", self.task_number)
            print("Stage Number after trial: ", self.stage)
            print("Block Change: ", self.block_change)
            print("Stage Change Forward: ", self.stage_forward_change)
            print("Stage Change Backward: ", self.stage_backward_change)
            print("Moved Back Counter: ", self.moved_back_counter)

            # Side Bias Breaking formula:

            # Calculate bias accuracy for the last five trials without using accuracy window
            self.bias_accuracy_trials.append(self.success)  # Append current trial success (0 or 1)
            if len(self.bias_accuracy_trials) > self.side_bias_trigger:
                self.bias_accuracy_trials.pop(0)  # Keep only the last 5 trials

            self.bias_accuracy = sum(self.bias_accuracy_trials) / len(self.bias_accuracy_trials) if self.bias_accuracy_trials else 0

            print(f"Bias Accuracy (last 5 trials): {self.bias_accuracy}")

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
                    #print(f"Failed to process response_x as array. Error: {e}")
                    return  # Handle this case if needed

            # Append the response to the array:
            self.response_x_array.append(self.response_x_bias)
                #print(f"Responses so far: {self.response_x_array}")

            #if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy < self.side_bias_trigger_acc:
            if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy is not None and self.accuracy < self.side_bias_trigger_acc:
                # Check if all responses fall into one of the two defined categories
                all_left_side = all(45 < x < 145 for x in self.response_x_array)            #Check if all the reponses fall on left
                all_right_side = all(231 < x < 331 for x in self.response_x_array)          #Check if all the reponses fall on right

                if self.stage == 4:
                    if all_left_side:
                        self.sameside = 'left'
                        self.bias_breaking = 1
                        print('Bias breaking active, side:', self.sameside)
                        self.last_stim_trial = random.choice([102, 104, 106, 108])  # Ensure the new stim is on the right
                    elif all_right_side:
                        self.sameside = 'right'
                        self.bias_breaking = 1
                        self.last_stim_trial = random.choice([101, 103, 105, 107])  # Ensure the new stim is on the left
                        print('Bias breaking active, side:', self.sameside)

                    self.response_x_array = []  # Clearing the array
                else:
                    if all_left_side:
                        self.sameside = 'left'
                        self.bias_breaking = 1
                        print('Bias breaking active, side:', self.sameside)
                        self.last_stim_trial = random.choice([102, 104])  # Ensure the new stim is on the right
                    elif all_right_side:
                        self.sameside = 'right'
                        self.bias_breaking = 1
                        self.last_stim_trial = random.choice([101, 103])  # Ensure the new stim is on the left
                        print('Bias breaking active, side:', self.sameside)

                    self.response_x_array = []      #Clearing the array
        else:
            print("Task 2 ended because Core training completed. Task is now 3 so will move to Weber's law in next session.")
            self.task_end = True

        ############ REGISTER VALUES ################
        self.register_value('stage', self.stage)
        self.register_value('substage', self.substage)
        self.register_value('substage_bias', self.substage_bias)
        self.register_value('task_number', self.task_number)
        self.register_value('block_size', self.block_size)
        self.register_value('block_trial_counter', self.block_trial_counter)
        self.register_value('block_accuracy', self.block_accuracy)
        self.register_value('block_number', self.block_number)
        self.register_value('ror_change', self.ror_change)
        self.register_value('block_change', self.block_change)
        self.register_value('total_trials', self.total_trials)
        self.register_value('block_correct_count', self.block_correct_count)
        self.register_value('block_valid_count', self.block_valid_count)
        self.register_value('condition_trial_counter', self.condition_trial_counter)
        self.register_value('last_forward_stage', self.last_forward_stage)
        self.register_value('last_backward_stage', self.last_backward_stage)
        self.register_value('moved_back_counter', self.moved_back_counter)
        self.register_value('stage_forward_change', self.stage_forward_change)
        self.register_value('stage_backward_change', self.stage_backward_change)
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)
        self.register_value('last_stim_trial', self.last_stim_trial)
        self.register_value('accuracy_criteria', self.accuracy_criteria)
        self.register_value('trial_end_criteria', self.trial_end_criteria)
        self.register_value('max_move_backs', self.max_move_backs)
        self.register_value('duration_max', self.duration_max)
        self.register_value('duration_min', self.duration_min)
        self.register_value('duration_tired', self.duration_tired)
        self.register_value('trials_tired', self.trials_tired)
        self.register_value('tired', self.tired)
        self.register_value('response_duration', self.response_duration)
        self.register_value('image_display', self.image_display)
        self.register_value('valve_time', self.valve_time)
        self.register_value('valve_reward', self.valve_reward)
        self.register_value('valve_factor_c', self.valve_factor_c)
        self.register_value('valve_factor_i', self.valve_factor_i)
        self.register_value('valid_counter', self.valid_counter)
        self.register_value('tired_counter', self.tired_counter)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('correct_count', self.correct_count)
        self.register_value('accuracy', self.accuracy)
        self.register_value('success', self.success)
        self.register_value('stim', self.stim)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)
        self.register_value('image_path_function', self.image_path_function)
        self.register_value('image_displayed', self.image_displayed)
        self.register_value('image_directory', self.image_directory)
        self.register_value('bias_breaking', self.bias_breaking)
        self.register_value('response_x_array', self.response_x_array)
        self.register_value('sameside_counter', self.sameside_counter)
        self.register_value('sameside', self.sameside)
        self.register_value('side_bias_trigger', self.side_bias_trigger)
        self.register_value('side_bias_trigger_acc', self.side_bias_trigger_acc)
        self.register_value('status', self.status)
        self.register_value('biased_consecutive_corrects_counter', self.biased_consecutive_corrects_counter)
        self.register_value('biased_consecutive_corrects', self.biased_consecutive_corrects)
        self.register_value('bias_accuracy_trials', self.bias_accuracy_trials)
        self.register_value('bias_accuracy', self.bias_accuracy)
        #Not Initialised but registered:
        self.register_value('correct_th', self.x_correcth)
        self.register_value('incorrect_th', self.x_incorrecth)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
        self.register_value('trial_length', self.trial_length)
        self.register_value('trial_result', self.trial_result)


