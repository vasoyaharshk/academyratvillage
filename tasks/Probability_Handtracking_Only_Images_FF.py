from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
import os
import re
from academy import telegram_bot


class Probability_Handtracking_Only_Images_FF(Task):
    def __init__(self):
        super().__init__()

        self.image_name = None  # Initialize image_name # NEW
        self.info = """
        This task is for Bastos and Taylor for Probabilistic Inference training and test. This task has the zoomed in stimuli and substages where the stages are
        mixed in.

        ALL ODD STAGES ARE IMAGE TRIALS AND EVEN STAGES ARE VIDEO TRIALS.
        
        Stage 3: Introduction of the yellow tokens:
        Here the stimuli is only images in substage 0.
        Substage 0: Only image trials, accuracy criteria 80%.
        Substage 1: This is actually stage 3.1 where we introduce the yellow token. The photogate that triggers the video is 5. Stage 1 and stage 2 trials interleaved. 87.5% stage 2 and 12.5% stage 1 , accuracy criteria 80%.

        if they hit 320 trials, move back one substage

        Stages:
        stage 1 - Image of 2 open hands, 1 hand with peg and 1 hand empty. 
        stage 2 - Videos - starts from open hands and then closes as rat approaches.

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump. 
        Port 2 - PHOTOGATES 2: Photogates next to lickport. STARTS TRIAL
        Port 3 - PHOTOGATES 3: Photogates. DOES NOTHING
        Port 4 - PHOTOGATES 4: Photogates. DOES NOTHING
        Port 5 - PHOTOGATES 5: Photogates. STARTS THE VIDEO 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED. STARTS THE RESPONSE WINDOW

        IMPORTANT NOTE: Condition trial counter here tracks the total number of trials in this task.

        Task Number = 6

        """

        # ==============================
        # Tracked Variables
        # ==============================
        # Needed in Each Task:
        self.stage = 0  # Current stage within the task
        self.substage = 0  # Current substage within the stage
        self.substage_bias = 0  # Side bias stage for substage behavior
        self.task_number = 6  # Each task has a unique number. See RV script guide.

        # Needed to create blocks of 40 trials for criterion to be assessed on:
        self.block_size = 40  # The number of trials in a block
        self.block_trial_counter = 0  # Trial count within the current block
        self.block_accuracy = 0.0  # Accuracy in the current block
        self.block_number = 1  # Sequential block number
        self.ror_change = 0  # If it is 1, ROR will change on the next trial.
        self.block_change = 0  # If it is 1, a new block will start on the next trial
        self.total_trials = 0  # Total trials across the task.
        self.block_correct_count = 0  # Number of correct responses in the block
        self.block_valid_count = 0  # Number of valid (non-missed) trials in the block
        self.condition_trial_counter = 0  # Counter for randomising conditions and for TOTAL TRIALS IN HANDTRACKING FOR TASK END CRITERIA.
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

        # to show an equal number of each image (left 1-5 and right 1-5)
        self.image_counter = 0  # NEW: Initialize the counter
        self.image_history = []  # Initialize the history list

        # ==============================
        # Untracked Variables
        # ==============================
        # Task specific:
        self.accuracy_criteria = None  # move forward criteria. 80% success on block_size(32/40 trials correct)
        self.trial_end_criteria = 320  # Move back criteria. Badly named - this is task end criteria.
        self.task_end_criteria = 1600  # Move back criteria. Badly named - this is task end criteria.
        self.max_move_backs = 8  # number of times they can be moved back (i.e., they've done 320 trials 5 times) before we review
        self.probabilities = []  # The probability for left and right in the randomization block. [0.1, 0.9] would mean 10% on left and 90% on right.

        # Trial Specific:
        self.duration_max = 3000  # Maximum duration of the task. 50 mins
        self.duration_min = 2100  # Minimum duration of the task. 35 mins.
        self.duration_tired = 1800  # Duration for the door to open (30 mins) if the animal is inactive. Less than 5 trials.
        self.trials_tired = 5  # if they do 5 trials of long duration (more than 45 seconds), the door will open after 30 mins rather than 35
        self.tired = False  # The door 2 opens whenever this is true. Used to end the task.
        self.response_duration = 60  # The response time after the last photogate has been crossed in secs.
        self.image_display = 0  # Number of seconds the image will display after correct and incorrect
        self.trial_length = 0  # time from when a trial starts until next trial starts
        self.trial_result = None  # Result of the trial, correct, incorrect or miss

        # Pump:
        self.valve_time = utils.water_calibration.read_last_value('port',1).pulse_duration  # The duration the water valve needs to be open for. Takes the value from the water_calibration.csv
        self.valve_reward = utils.water_calibration.read_last_value('port',1).water  # 25ul per trial normal conditions. Takes the value from water_caliberation.csv
        self.valve_factor_c = 1  # Normal water delivery must be a multiple of 25ul. 2.0 is 2 x 25 = 50uL. E.g., if you set it to 1.8, this would be 1.8 x 25 = 45uL
        # self.valve_factor_i = 0.6  # Water delivery for incorrects/punish - only if want to give water if they do an incorrect trial (only used for scripts that allow correction)

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
        self.x_correcth_pos = [130, 250]  # Horizontal Coordinates for left and right for Jars
        self.y_correcth = 110  # Vertical Coordinates for left and right for Jars
        self.width = 100  # Stimulus width in mm. Original size for jar is 120mm.
        self.height = 190  # Stimulus height in mm. Original size for jar is 110mm.
        self.image_path_function = None  # Full Path for the image displayed
        self.image_displayed = None  # The image which is displayed
        self.image_directory = None  # The directory of the image displayed

        # Bias breaking variables:
        self.bias_breaking = 0  # If subject chooses same side for 5 trials in a row, bias breaking becomes 1
        self.response_x_array = []  # Stores responses for x till 5 values
        self.sameside_counter = 0  # Counts number of times on same side
        self.sameside = None  # To track which side is being triggered for bias breaking
        self.side_bias_trigger = 5  # After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8  # Side_bias triggers if accuracy is below this for the last 5 trials
        self.biased_consecutive_corrects_counter = 0  # This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3  # This is the number of corrects the rat needs to do to end bias breaking
        self.bias_accuracy_trials = []  # List that holds the last five success or failures.
        self.bias_accuracy = 0  # Accuracy of the last five trials.

        # For Videos:
        # Video parameters:
        self.video_display = 3  # Number of seconds the video will display after correct and incorrect
        self.video_stim_play = 0  # The function that plays the video
        self.video_length = 0  # Length of the video till what it is played
        self.response_image = 0  # Not used yet. This was a function that can display the first frame of the video but it is not used now.

        # Video output paths:
        self.video_path_function = None
        self.video_displayed = None
        self.video_directory = None

        self.stage_sequence = []
        self.last_stage_trial = 0
        self.task_end = False

        self.alert_sent = False

        self.substage_stage_map = {
            1: {1: 1.0, 2: 0.0},
            2: {1: 0.125, 2: 0.875}
        }

        self.stage_sequence_counter = 0
        self.substage_counter_1 = 0
        self.substage_counter_2 = 0
        self.substage_counter_3 = 0
        self.substage_counter_4 = 0
        self.substage_counter_5 = 0
        self.substage_counter_6 = 0
        self.substage_counter_7 = 0
        self.substage_counter_8 = 0
        self.substage_counter_9 = 0
        self.substage_counter_10 = 0
        self.substage_counter_11 = 0
        self.substage_counter_12 = 0

        self.fixation_trigger_port = Bpod.Events.Port5In

        # Forced-choice logic
        self.forced_choice_actual_trial = 0 # type of the current trial, 0 for normal 1 for forced choice
        self.forced_choice_next_trial = 0  # type of the next trial, 0 for normal 1 for forced choice
        self.forced_choice_probe = None  # 0 or 4, probe to repeat on forced-choice trials

        self.touchoutside = 0

        self.consecutive_good_blocks = 0
        self.consecutive_good_blocks_criteria = 2

        self.session_first_stim = None
        self.last_two_stim = []

    def flip_side(self, stim_val: int) -> int:
        return stim_val + 1 if (stim_val % 2 == 1) else stim_val - 1

    def configure_gui(self):
        self.gui_input = ['stage', 'substage', 'duration_max']

    def get_stage_sequence(self, block_size=None, substage=None, last_stage_trial=None):
        """
        Returns a randomised stage sequence for the given block size and substage,
        using the correct proportions for image and video trials.
        For substages other than 3, just returns the correct shuffled sequence.
        This is only fo substage 1 and 2 and 3.
        """
        if block_size is None:
            block_size = self.block_size
        if substage is None:
            substage = self.substage

        # Special handling for substage 3
        if substage == 3:
            return self.generate_random_trials_stages(last_trial=last_stage_trial)

        # General handling for other substages
        if substage not in self.substage_stage_map:
            raise ValueError(f"Invalid substage: {substage}")
        stage_map = self.substage_stage_map[substage]

        sequence = []

        for stage, prop in stage_map.items():
            stage_n = int(round(block_size * prop))
            sequence.extend([stage] * stage_n)

        # Fix rounding issues
        while len(sequence) < block_size:
            sequence.append(random.choice(list(stage_map.keys())))
        sequence = sequence[:block_size]

        random.shuffle(sequence)

        # Avoid repeating the same stage as last trial
        if last_stage_trial is not None and sequence[0] == last_stage_trial:
            for i in range(1, len(sequence)):
                if sequence[i] != last_stage_trial:
                    sequence[0], sequence[i] = sequence[i], sequence[0]
                    break

        return sequence

    def get_stage_sequence_fixed_video(self, block_size=None, substage=None, last_stage_trial=None):
        """
        For substages 4+, creates a block with exactly block_size video (even) trials
        and a fixed number of image (odd) trials according to the map.
        """
        if block_size is None:
            block_size = self.block_size
        if substage is None:
            substage = self.substage

        if substage not in self.substage_stage_map:
            raise ValueError(f"Invalid substage: {substage}")
        stage_map = self.substage_stage_map[substage]

        # Identify image and video stages
        image_stages = [s for s in stage_map if s % 2 == 1]
        video_stages = [s for s in stage_map if s % 2 == 0]

        if not video_stages or not image_stages:
            raise ValueError("Expected both image and video stages for substage 4+")

        video_stage = video_stages[0]
        image_stage = image_stages[0]

        # Compute number of image trials to match the intended proportion
        prop_image = stage_map[image_stage]
        n_image = int(round(block_size * prop_image / (1 - prop_image)))
        # For example, if prop_image = 0.25, block_size = 40:
        # n_image = round(40 * 0.25 / 0.75) = round(13.33) = 13
        # For example, if prop_image = 0.125, block_size = 40:
        # n_image = round(40 * 0.125 / 0.875) = round(6.349) = 6

        sequence = [video_stage] * block_size + [image_stage] * n_image
        random.shuffle(sequence)

        # Avoid repeating the same stage as last trial
        if last_stage_trial is not None and sequence[0] == last_stage_trial:
            for i in range(1, len(sequence)):
                if sequence[i] != last_stage_trial:
                    sequence[0], sequence[i] = sequence[i], sequence[0]
                    break

        return sequence

    def generate_random_trials(self,
                               last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
        trials = []
        # Define a 50% probability for each stimulus (two stimuli)
        probabilities = [0.5, 0.5]  # Adjust this if you have more than two stimuli
        while len(trials) < self.block_size:
            # Use random.choices to select a candidate with 50% probability for each stimulus
            candidate = random.choices(self.stim, probabilities)[0]
            # Ensure no repetition more than twice in sequence
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                # Additionally, ensure the first trial doesn't repeat the last trial from the previous block
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue  # Skip if the first trial of new block matches last trial of previous block
                trials.append(candidate)
        return trials

    def generate_random_trials_stages(self, last_trial=None):
        """
        Special generator for substage 3: 50/50 interleaved stages (1 and 2)
        with no more than 2 repetitions in sequence.
        """
        trials = []
        choices = [1, 2]
        probabilities = [0.5, 0.5]

        while len(trials) < self.block_size:
            candidate = random.choices(choices, probabilities)[0]
            if len(trials) < 2 or not (candidate == trials[-1] == trials[-2]):
                if last_trial is not None and len(trials) == 0 and candidate == last_trial:
                    continue
                trials.append(candidate)

        return trials

    def get_stim_image_path(self, stim_trial, stage):
        """
        Determines whether stim_trial is 121 or 122, retrieves the corresponding image path based on the stage, and returns it.
        """
        image_path = None
        image_name = None  # NEW

        try:
            if stim_trial == 121:
                position = 'left'
            elif stim_trial == 122:
                position = 'right'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}. Expected 121 or 122.")

            # Define image folder based on stage
            if stage == 1:
                image_folder = '/home/harsh/academy/stimuli/bastos_taylor/hand_tracking/stage_1_only_Images'
            elif stage == 2:
                image_folder = '/home/harsh/academy/stimuli/bastos_taylor/hand_tracking/stage_2_video/images'
            else:
                raise ValueError(f"Invalid stage value: {stage}. Expected 1, 2, or 3.")

            # Get relevant images based on position
            mode_correction = (self.forced_choice_next_trial == 1)

            def is_valid_image(fname: str) -> bool:
                f = fname.lower()

                # Keep left right rule exactly as before
                if position not in f:
                    return False

                # Keep existing core filters
                if "both" not in f:
                    return False
                if "open" not in f:
                    return False

                # Split normal vs correction pools
                has_correction = ("correction" in f)

                if mode_correction:
                    return has_correction
                else:
                    return (not has_correction)

            images = [
                f for f in os.listdir(image_folder)
                if os.path.isfile(os.path.join(image_folder, f)) and is_valid_image(f)
            ]

            if not images:
                raise ValueError(f"No images found in {image_folder} for position {position}.")

            ### NEW Ensure no image is displayed more than twice in a row
            while True:
                image_path = os.path.join(image_folder, images[self.image_counter % len(images)])  # NEW
                image_name = os.path.splitext(os.path.basename(image_path))[0]
                if self.image_history.count(image_name) < 2:  # NEW
                    break
                self.image_counter += 1  # NEW

            self.image_counter += 1  # NEW
            self.image_history.append(image_name)  # NEW
            if len(self.image_history) > 2:  # NEW
                self.image_history.pop(0)  # NEW

            print(f'Stage: {stage}')
            print(f'Image Correct answer on {position}: {image_path}')

        except Exception as e:
            print(f"Error occurred: {e}")

        return image_path, image_name  # EDITED

        #     # Choose a random image
        #     image_path = os.path.join(image_folder, random.choice(images))
        #     image_name = os.path.splitext(os.path.basename(image_path))[0]
        #     print(f'XXXXX{image_name}')
        #     print(f'Stage: {stage}')
        #     print(f'Image Correct answer on {position}: {image_path}')
        #
        # except Exception as e:
        #     print(f"Error occurred: {e}")
        #
        # return image_path, image_name # EDITED

    def get_stim_video_path(self, stim_trial, stage, image_name):
        """
        Determines whether stim_trial is 111, 112, retrieves the corresponding video path, and returns it.
        """
        video_path = None

        try:
            if stim_trial == 111:
                position = 'left'
            elif stim_trial == 112:
                position = 'right'
            else:
                raise ValueError(f"Invalid stim_trial value: {stim_trial}. Expected 115, or 116.")
            # Define video folder based on stage
            if stage == 2:
                video_folder = '/home/harsh/academy/stimuli/bastos_taylor/hand_tracking/stage_3_hand_tracking_video_yellow_token/videos'
            else:
                raise ValueError(f"Invalid stage: {stage}")

            # Get relevant videos based on position
            videos = [f for f in os.listdir(video_folder) if
                      os.path.isfile(os.path.join(video_folder, f)) and
                      (position in f.lower() and 'both' in f.lower())]
            if not videos:
                raise ValueError(
                    f"No videos found in {video_folder} for stage {stage}, position {position}.")

            # Choose a video that matches with the image left or right, and 1-5
            def filter_videos(videos, keyword, number):
                return [video for video in videos if keyword in video and str(number) in video]

            if "left" in image_name:
                keyword = "left"
            elif "right" in image_name:
                keyword = "right"
            else:
                keyword = ""
            number = next((num for num in range(1, 7) if str(num) in image_name), None)

            # Filter videos based on keyword and number
            filtered_videos = filter_videos(videos, keyword, number)

            # Choose a random video from the filtered list
            if filtered_videos:
                video_path = os.path.join(video_folder, random.choice(filtered_videos))
            else:
                print("No matching video found.")
            ## to here

            # video_path = os.path.join(video_folder, random.choice(videos)) # here is where it picks a random video
            print(f'Video Correct answer on {position} {video_path}')
        except Exception as e:
            print(f"Error occurred: {e}")

        return video_path

    def main_loop(self):
        self.touchoutside = 0

        print('')
        ### Randomizing the stimulus positions for both the images:

        self.accuracy_criteria_substage = {
            1: 0.80,
            2: 0.80,
        }

        if self.current_trial == 0:
            self.bias_breaking = 0
            self.accuracy = 0
            self.forced_choice_next_trial = 0

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
            self.stage_sequence_counter = 0

        if self.stage_forward_change == 1:
            self.total_trials = 0
            self.stage_forward_change = 0
            self.consecutive_good_blocks = 0
            self.last_forward_stage = self.substage  # Save current BEFORE increasing
            self.substage += 1
            message = f"Substage moved forward to {self.substage} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except Exception as e:
                print(f"Telegram message not sent. Error: {e}")
            if self.substage == 2:
                self.task_number = 7
                self.tired = True

        if self.stage_backward_change == 1:
            self.total_trials = 0
            self.stage_backward_change = 0
            self.block_accuracy = 0.0
            self.block_trial_counter = 0  # Reset the counter after the block
            self.block_correct_count = 0
            self.block_valid_count = 0
            self.stim_trial_counter = 0
            new_stage = max(self.substage - 1, 0)
            if new_stage == self.last_forward_stage:
                if self.last_backward_stage == new_stage:
                    self.moved_back_counter += 1
                else:
                    self.moved_back_counter = 1
                    self.last_backward_stage = new_stage
            else:
                self.moved_back_counter = 1
                self.last_backward_stage = new_stage
            self.substage = new_stage
            message = f"Substage moved backward to {self.substage} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except:
                print("Telegram message not sent")

        print('Block_trial_counter= ', self.block_trial_counter)
        print('Stage_sequence_counter= ', self.stage_sequence_counter)
        print('Substage= ', self.substage)

        ### Randomizing the stimulus positions for image and the videos:
        # Stage Assignment:
        if self.task_number == 6:
            # Generate the sequence on the first block (or whenever you want),
            # but DO NOT regenerate later — we'll fall back to stage 2 instead.
            if self.stage_sequence_counter == 0:
                if self.substage <= 3:
                    self.stage_sequence = self.get_stage_sequence(
                        block_size=self.block_size,
                        substage=self.substage,
                        last_stage_trial=self.last_stage_trial
                    )
                else:
                    self.stage_sequence = self.get_stage_sequence_fixed_video(
                        block_size=self.block_size,
                        substage=self.substage,
                        last_stage_trial=self.last_stage_trial
                    )
                self.last_stage_trial = self.stage_sequence[-1]
                print("stage_sequence = ", self.stage_sequence)

            # Use planned sequence while available; once consumed, fill with stage 2
            if self.stage_sequence_counter < len(self.stage_sequence):
                self.stage = self.stage_sequence[self.stage_sequence_counter]
            else:
                self.stage = 2  # fallback: keep using stage 2 for all remaining trials

        # REMINDER: HERE THE LAST STAGE TRIAL IS THE STAGE IN THE LAST TRIAL OF BLOCK.

        ### IMAGE Randomisation
        self.stim = [121, 122]  # function 121 is image where the left hand is correct and 122 is where right is correct
        if self.task_number == 6:
            # Stimulus generation logic
            if self.stim_trial_counter % self.block_size == 0 and self.bias_breaking == 0:  # Re-randomize every 10 trials
                # If not the first block_size, pass the last stimulus of the previous block_size to avoid repetition
                last_trial = self.stim_trials[self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None
                self.stim_trials = self.generate_random_trials(last_trial)
                # print(f"Stimulus trials after first attempt: {self.stim_trials}")
                while self.stim_trials is None:
                    print("Retrying to generate stimulus trials...")
                    self.stim_trials = self.generate_random_trials(last_trial)
                    if self.stim_trials is None:
                        print("generate_random_trials returned None. Retrying...")
                    else:
                        print(f"Successfully generated stimulus trials: {self.stim_trials}")
                self.stim_trial_counter = 0

            # --- session-local logic for first two trials in this session ---
            if self.current_trial == 0:
                candidate = random.choice(self.stim)
                self.session_first_stim = candidate
            elif self.current_trial == 1:
                candidate = self.flip_side(self.session_first_stim)
            else:
                # from 3rd trial onwards: normal block / bias-breaking logic
                if self.bias_breaking == 0:
                    candidate = self.stim_trials[self.stim_trial_counter]
                else:
                    candidate = self.last_stim_trial

            # --- global guard: never allow 3 same-side stimuli in a row across sessions ---
            if len(self.last_two_stim) >= 2:
                if (candidate % 2 == self.last_two_stim[-1] % 2) and (candidate % 2 == self.last_two_stim[-2] % 2):
                    candidate = self.flip_side(candidate)

                # self.forced_choice_actual_trial = self.forced_choice_next_trial

            if self.forced_choice_next_trial == 0:
                self.stim_trial = candidate
            else:
                self.stim_trial = self.forced_choice_probe

            # keep stimulus schedule aligned with actual delivered probe
            if self.forced_choice_next_trial == 0 and 0 <= self.stim_trial_counter < len(self.stim_trials):
                self.stim_trials[self.stim_trial_counter] = self.stim_trial


            print("Stage: ", self.stage)
            print("Substage: ", self.substage)

            # Set accuracy criterion
            self.accuracy_criteria = self.accuracy_criteria_substage.get(self.substage, 0.8)
            print("Accuracy Criteria: ", self.accuracy_criteria)

            # self.stim_trial = 121  #Remove this if you need to randomise left and right. Cause the video for left is only ready, only left is done.

            ### VIDEOS
            if self.stage % 2 == 1:  # We have only one stimulus in stage 1
                # Here, if we need to define the correcth_x position based on the stimulus. So function 101 displays stimulus with correct answer on the left (x=115) and 102 displays stimulus with correct answer on right (x=295)
                if self.stim_trial in [121]:  # if image is left correct
                    self.video_stim_play = 111  # display videos with correct on left
                    self.response_image = 117
                    self.x_correcth = self.x_correcth_pos[0]
                    self.x_incorrecth = self.x_correcth_pos[1]  # No incorrect area in stage 1
                    # print('Correct Answer: Left, ', 'X position = ', self.x_correcth)
                elif self.stim_trial in [122]:  # if image is right correct
                    self.video_stim_play = 112
                    self.response_image = 118
                    self.x_correcth = self.x_correcth_pos[1]
                    self.x_incorrecth = self.x_correcth_pos[0]  # No incorrect area in stage 1
                    # print('Correct Answer: Right, ', 'X position = ', self.x_correcth)

            ### For stage 2 onwards
            else:  # We have two stimuli after stage 1 with correct and incorrect areas
                if self.stim_trial in [121]:  # if image is left correct
                    self.video_stim_play = 111  # display videos with correct on left
                    self.response_image = 117
                    self.x_correcth = self.x_correcth_pos[0]
                    self.x_incorrecth = self.x_correcth_pos[1]
                    # print('Correct Answer: Left, ', 'X position = ', self.x_correcth, 'Incorrect position: ',
                    # self.x_incorrecth)
                elif self.stim_trial in [122]:  # if image is right correct
                    self.video_stim_play = 112  # should display videos with correct on right
                    self.response_image = 118
                    self.x_correcth = self.x_correcth_pos[1]
                    self.x_incorrecth = self.x_correcth_pos[0]
                    # print('Correct Answer: Right, ', 'X position = ', self.x_correcth, 'Incorrect position: ',
                    # self.x_incorrecth)

            # print('randomisation counter: ', self.stim_trial_counter)
            # print('stim_trial: ', self.stim_trial)
            # print('video_stim_play: ', self.video_stim_play)
            # print('response_image: ', self.response_image)

            self.image_path_function, self.image_name = self.get_stim_image_path(self.stim_trial, self.stage)
            # self.image_path_function = self.get_stim_image_path(self.stim_trial, self.stage)

            if self.stage % 2 == 0:
                self.video_length = 1
                # Figure out the full path to the video we want to play.
                # This uses some kind of function (self.get_stim_video_path, probably defined earlier in your code) that takes in which video to play and what stage we're in.
                self.video_path_function = self.get_stim_video_path(self.video_stim_play, self.stage, self.image_name)
                # Split that full video path into two parts:
                # - 'directory' is where the video is stored on your computer.
                # - 'filename' is just the name of the video file itself (without the folder path).
                directory, filename = os.path.split(self.video_path_function)
                # Save the name of the video file for later use or reference.
                self.video_displayed = filename
                # Save the directory (location) where the video file lives.
                self.video_directory = directory

            # print("image_path_function: ", self.image_path_function)
            # print("video_path_function: ", self.video_path_function)

            # Decide which port triggers video for this trial
            self.fixation_trigger_port = Bpod.Events.Port5In

            if self.forced_choice_next_trial == 1:
                self.x_incorrecth = None

        ############ STATE MACHINE ################
        # First trial:
        if self.task_number == 6:
            if self.stage % 2 == 1:
                # First trial:
                if self.current_trial == 0:
                    self.sma.add_state(
                        state_name='Start_task',
                        state_timer=0,
                        # the timer is set to 0 meaning it will immediately proceed to the next state when photogate at port 2 has been crossed
                        state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                        output_actions=[(Bpod.OutputChannels.SoftCode,
                                         self.stim_trial)])  # displays the still image of the first frame of the video
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
                    state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside',
                                             'SoftCode4': 'Punish',
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
                    state_change_conditions={Bpod.Events.Port1In: 'Correct_reward',
                                             Bpod.Events.Tup: 'Flip_screen_reward'},
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
                    state_change_conditions={Bpod.Events.Tup: 'Punish_image_display'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 39)])
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
                    state_change_conditions={Bpod.Events.Port1In: 'After_punish',
                                             Bpod.Events.Tup: 'Flip_screen_no_reward'},
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

            ### STAGE 2 ONWARDS
            else:  # For stage 2 involving videos
                if self.current_trial == 0:  # This is a separate statement for the first trial as we need it to also close door 2
                    self.sma.add_state(
                        state_name='Start_task',
                        state_timer=0,
                        state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                        output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
                    # Starts task and displays stimuli instantly

                    self.sma.add_state(
                        state_name='Real_start',
                        state_timer=self.valve_time * 2,
                        state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                        output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.Valve, 1)])
                    # Closes corridor door 2 and delivers initial 50ul water.

                # Other Trials (trial 2 onwards):
                else:
                    self.sma.add_state(
                        state_name='Start_task',
                        state_timer=0,
                        state_change_conditions={Bpod.Events.Port2In: 'Wait_for_fixation'},
                        # This starts the trial when they cross photogate port 2 is crossed.
                        output_actions=[])

                self.sma.add_state(
                    state_name='Wait_for_fixation',
                    state_timer=0,
                    state_change_conditions={Bpod.Events.Tup: 'Fixation'},
                    output_actions=[])

                self.sma.add_state(
                    state_name='Fixation',  # displays image
                    state_timer=0,
                    state_change_conditions={self.fixation_trigger_port: 'Start_Video'},
                    # This starts the video when they cross photogate port 5 is crossed .
                    output_actions=[(Bpod.OutputChannels.SoftCode, self.stim_trial)])
                # Change the number in Port5In to select which photogate

                self.sma.add_state(
                    state_name='Start_Video',
                    state_timer=self.video_length,
                    state_change_conditions={Bpod.Events.Tup: 'Response_window_image'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, self.video_stim_play)])
                # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

                self.sma.add_state(
                    state_name='Response_window_image',
                    state_timer=0,
                    state_change_conditions={Bpod.Events.Tup: 'Response_window'},
                    output_actions=[])
                # output_actions=[(Bpod.OutputChannels.SoftCode, self.response_image)])

                self.sma.add_state(
                    state_name='Response_window',
                    state_timer=self.response_duration,
                    state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside',
                                             'SoftCode4': 'Punish',
                                             Bpod.Events.Tup: 'No_Touch'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, 34)])
                # Starts to read the touchscreen with one touch processing

                self.sma.add_state(
                    state_name='Correct',
                    state_timer=0,
                    state_change_conditions={Bpod.Events.Tup: 'Correct_video_display'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 220)])
                # Turns on Water port LED and plays correct sound

                self.sma.add_state(
                    state_name='Correct_video_display',
                    state_timer=self.video_display,
                    state_change_conditions={Bpod.Events.Port1In: 'Correct_reward',
                                             Bpod.Events.Tup: 'Flip_screen_reward'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 113)])
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
                    state_change_conditions={Bpod.Events.Tup: 'Punish_video_display'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 39)])
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
                    state_change_conditions={Bpod.Events.Port1In: 'After_punish',
                                             Bpod.Events.Tup: 'Flip_screen_no_reward'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 114)])
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
        else:
            print("Task 4 is completed. Task is now 5 which we will decide later")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.x_correcth = None
            self.x_incorrecth = None
            self.response_x = None
            self.response_y = None

    def after_trial(self):
        if self.task_number == 6:

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.trial_result = 'miss'

            ##### COUNT PUNISH
            elif self.current_trial_states['Punish'][0][0] > 0:
                self.trial_result = 'incorrect'
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.stage_sequence_counter += 1  # Always advance in the sequence if it was a valid trial
                    # Block trial counter logic
                    if (self.substage == 0) or (self.substage == 1 and self.stage % 2 == 0):
                        self.block_trial_counter += 1
                        self.total_trials += 1
                        self.block_valid_count += 1
                    self.success = 0
                    self.condition_trial_counter += 1
                    if self.bias_breaking == 0:
                        self.stim_trial_counter += 1
                    self.forced_choice_next_trial = 1
                    self.forced_choice_probe = self.stim_trial
                    print('Acc Valid_count: ', self.block_valid_count)

                ##### COUNT CORRECTS POKE
            elif self.current_trial_states['Correct'][0][0] > 0:
                self.trial_result = 'correct'
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.reward = self.valve_reward * self.valve_factor_c
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.stage_sequence_counter += 1  # Always advance in the sequence if it was a valid trial
                    self.reward_drunk += self.valve_reward * self.valve_factor_c
                    self.correct_count += 1
                    # Block trial counter logic
                    if (self.substage == 0) or (self.substage == 1 and self.stage % 2 == 0):
                        self.block_trial_counter += 1
                        self.total_trials += 1
                        self.block_valid_count += 1
                        self.block_correct_count += 1
                        self.success = 1
                    self.condition_trial_counter += 1
                    if self.bias_breaking == 0:
                        self.stim_trial_counter += 1
                self.forced_choice_next_trial = 0
                self.forced_choice_probe = None
                print('Acc Correct_count: ', self.block_correct_count)
                print('Acc Valid_count: ', self.block_valid_count)

                # Check if side bias is active and if the current trial was correct
                if self.bias_breaking == 1:  # Side bias active
                    self.biased_consecutive_corrects_counter += 1  # Increment counter for consecutive corrects
                    if self.biased_consecutive_corrects_counter >= self.biased_consecutive_corrects:  # If three corrects after bias breaking
                        self.bias_breaking = 0  # End bias breaking
                        self.stim_trial_counter = 0
                        self.biased_consecutive_corrects_counter = 0  # Reset the consecutive corrects counter


            # ##### COUNT Touches outside the jar areas :
            elif self.current_trial_states['Touch_Outside'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.touchoutside = 1
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.stage_sequence_counter += 1  # Always advance in the sequence if it was a valid trial
                    # Block trial counter logic
                    if (self.substage == 0) or (self.substage == 1 and self.stage % 2 == 0):
                        self.block_trial_counter += 1
                        self.total_trials += 1
                        self.block_valid_count += 1
                    self.success = 0
                    self.condition_trial_counter += 1
                    if self.bias_breaking == 0:
                        self.stim_trial_counter += 1
                    self.forced_choice_next_trial = 1
                    self.forced_choice_probe = self.stim_trial
                    print('Acc Valid_count: ', self.block_valid_count)

            # End-trial calculations
            # self.last_x = self.x
            self.trial_length = self.current_trial_states['Exit'][0][0] - self.current_trial_states['Start_task'][0][0]
            print('Trial length: ' + str(self.trial_length))

            # Actual forced choice flag. In this task, a forced choice trial disables the incorrect side
            if self.x_incorrecth is None:
                self.forced_choice_actual_trial = 1
            else:
                self.forced_choice_actual_trial = 0

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
                self.last_block_accuracy = self.block_accuracy

                # update consecutive good blocks
                if self.block_accuracy >= self.accuracy_criteria:
                    self.consecutive_good_blocks += 1
                else:
                    self.consecutive_good_blocks = 0

                # forward criterion: 3 consecutive good blocks
                if self.consecutive_good_blocks >= self.consecutive_good_blocks_criteria:
                    self.stage_forward_change = 1

                # backward rule if many trials and still no forward move
                if self.total_trials >= self.trial_end_criteria and self.stage_forward_change == 0:
                    self.stage_backward_change = 1

            # Assign in pass what to do when the rat is moved back more than 5 times.
            if self.moved_back_counter > self.max_move_backs:
                message = f"URGENT: Moved back {self.moved_back_counter} for {self.subject}. CHECK DATA."
                try:
                    print(message)
                    # telegram_bot.alarm_finish_session(message, self.subject)
                except:
                    print('Telegram message not sent')
                    pass

            if self.stage > self.last_backward_stage + 1:
                self.moved_back_counter = 0

            # Substage trial counters for only videos:
            if (self.substage == 0) or (self.substage == 1 and self.stage % 2 == 0):
                if self.substage == 0:
                    self.substage_counter_1 += 1
                elif self.substage == 1:
                    self.substage_counter_2 += 1

            # Side Bias Breaking formula:

            # Calculate bias accuracy for the last five trials without using accuracy window
            self.bias_accuracy_trials.append(self.success)  # Append current trial success (0 or 1)
            if len(self.bias_accuracy_trials) > self.side_bias_trigger:
                self.bias_accuracy_trials.pop(0)  # Keep only the last 5 trials

            self.bias_accuracy = sum(self.bias_accuracy_trials) / len(
                self.bias_accuracy_trials) if self.bias_accuracy_trials else 0

            print(f"Bias Accuracy (last 5 trials): {self.bias_accuracy}")

            self.last_stim_trial = self.stim_trial

            # Update short history used to prevent triples
            self.last_two_stim.append(self.stim_trial)
            if len(self.last_two_stim) > 2:
                self.last_two_stim.pop(0)

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
            self.response_x_array.append(self.response_x_bias)
            # print(f"Responses so far: {self.response_x_array}")

            # if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy < self.side_bias_trigger_acc:
            if len(self.response_x_array) >= self.side_bias_trigger and self.accuracy is not None and self.accuracy < self.side_bias_trigger_acc:
                # Check if all responses fall into one of the two defined categories
                all_left_side = all(
                    45 < x < 145 for x in self.response_x_array)  # Check if all the reponses fall on left
                all_right_side = all(
                    231 < x < 331 for x in self.response_x_array)  # Check if all the reponses fall on right

                if all_left_side:
                    self.sameside = 'left'
                    self.bias_breaking = 1
                    print('Bias breaking active, side:', self.sameside)
                    self.last_stim_trial = random.choice([122])  # Ensure the new stim is on the right
                elif all_right_side:
                    self.sameside = 'right'
                    self.bias_breaking = 1
                    self.last_stim_trial = random.choice([121])  # Ensure the new stim is on the left
                    print('Bias breaking active, side:', self.sameside)

                self.response_x_array = []  # Clearing the array

            print("Block Trial Counter: ", self.block_trial_counter)
            # print("Block Accuracy: ", self.block_accuracy)
            print("Block Number: ", self.block_number)
            print("Block Size: ", self.block_size)
            # print("Task Number: ", self.task_number)
            print("Block Change: ", self.block_change)
            print("Stage Change Forward: ", self.stage_forward_change)
            print("Stage Change Backward: ", self.stage_backward_change)
            print("Moved Back Counter: ", self.moved_back_counter)

            if self.substage == 5 and self.moved_back_counter == 2 and not self.alert_sent:
                try:
                    message = f"URGENT: {self.subject} has moved back from substage 5 twice in {self.task}"
                    # telegram_bot.alarm_finish_session(message, self.subject)
                    self.alert_sent = True
                except Exception as e:
                    print("Telegram message not sent. Error:", e)

            if self.substage != 5:
                self.alert_sent = False

            if self.substage == 6 and self.moved_back_counter == 2 and not self.alert_sent:
                try:
                    message = f"URGENT: {self.subject} has moved back from substage 5 twice in {self.task}"
                    # telegram_bot.alarm_finish_session(message, self.subject)
                    self.alert_sent = True
                except Exception as e:
                    print("Telegram message not sent. Error:", e)

            if (self.substage_counter_1 >= self.task_end_criteria) or (
                    self.substage_counter_2 >= self.task_end_criteria):
                try:
                    message = f"URGENT: {self.subject} has completed 1600 trials in this task."
                    telegram_bot.alarm_finish_session(message, self.subject)
                    self.task_end = True
                except Exception as e:
                    print("Telegram message not sent. Error:", e)


        else:
            print("Task 4 is completed. Task is now 5 which we will decide later")
            self.task_end = True

        ############ REGISTER VALUES ################
        # Task-related
        self.register_value('duration_max', self.duration_max)
        self.register_value('duration_min', self.duration_min)
        self.register_value('duration_tired', self.duration_tired)
        self.register_value('trials_tired', self.trials_tired)
        self.register_value('tired', self.tired)
        self.register_value('task_number', self.task_number)
        self.register_value('stage', self.stage)
        self.register_value('substage', self.substage)
        self.register_value('substage_bias', self.substage_bias)
        self.register_value('response_duration', self.response_duration)
        self.register_value('image_display', self.image_display)

        # Pumps
        self.register_value('valve_time', self.valve_time)
        self.register_value('valve_reward', self.valve_reward)
        self.register_value('valve_factor_c', self.valve_factor_c)
        # self.register_value('valve_factor_i', self.valve_factor_i)  # Uncomment if used

        # Counters
        self.register_value('valid_counter', self.valid_counter)
        self.register_value('tired_counter', self.tired_counter)
        self.register_value('reward_drunk', self.reward_drunk)
        # self.register_value('running_window', self.running_window)  # Uncomment if used
        self.register_value('correct_count', self.correct_count)
        self.register_value('accuracy', self.accuracy)

        # Stimulus-related
        self.register_value('stim', self.stim)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y_correcth', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)

        # Bias-breaking
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

        # Criteria
        self.register_value('accuracy_criteria', self.accuracy_criteria)
        self.register_value('trial_end_criteria', self.trial_end_criteria)
        self.register_value('task_end_criteria', self.task_end_criteria)
        self.register_value('max_move_backs', self.max_move_backs)

        # Trial/block tracking
        self.register_value('success', self.success)
        self.register_value('block_size', self.block_size)
        self.register_value('block_trial_counter', self.block_trial_counter)
        self.register_value('block_accuracy', self.block_accuracy)
        self.register_value('block_number', self.block_number)
        self.register_value('block_change', self.block_change)
        self.register_value('last_stim_trial', self.last_stim_trial)
        self.register_value('total_trials', self.total_trials)
        self.register_value('block_correct_count', self.block_correct_count)
        self.register_value('block_valid_count', self.block_valid_count)
        self.register_value('condition_trial_counter', self.condition_trial_counter)
        self.register_value('stage_sequence_counter', self.stage_sequence_counter)

        # Stimulus trial control
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)

        # Stage changes
        self.register_value('stage_forward_change', self.stage_forward_change)
        self.register_value('stage_backward_change', self.stage_backward_change)
        self.register_value('moved_back_counter', self.moved_back_counter)

        # Corecth location:
        self.register_value('correct_th', self.x_correcth)
        self.register_value('incorrect_th', self.x_incorrecth)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)

        # Trial Information:
        self.register_value('trial_length', self.trial_length)
        self.register_value('trial_result', self.trial_result)

        self.register_value('last_forward_stage', self.last_forward_stage)
        self.register_value('last_backward_stage', self.last_backward_stage)

        # Videos:
        self.register_value('video_display', self.video_display)
        self.register_value('video_stim_play', self.video_stim_play)
        self.register_value('video_length', self.video_length)
        self.register_value('response_image', self.response_image)
        self.register_value('video_path_function', self.video_path_function)
        self.register_value('video_displayed', self.video_displayed)
        self.register_value('video_directory', self.video_directory)
        self.register_value('image_name', self.image_name)
        self.register_value('stage_sequence', self.stage_sequence)
        self.register_value('last_stage_trial', self.last_stage_trial)
        self.register_value('substage_counter_1', self.substage_counter_1)
        self.register_value('substage_counter_2', self.substage_counter_2)
        self.register_value('substage_counter_3', self.substage_counter_3)
        self.register_value('substage_counter_4', self.substage_counter_4)
        self.register_value('substage_counter_5', self.substage_counter_5)
        self.register_value('substage_counter_6', self.substage_counter_6)
        self.register_value('substage_counter_7', self.substage_counter_7)
        self.register_value('substage_counter_8', self.substage_counter_8)
        self.register_value('substage_counter_9', self.substage_counter_9)
        self.register_value('substage_counter_10', self.substage_counter_10)
        self.register_value('substage_counter_11', self.substage_counter_11)
        self.register_value('substage_counter_12', self.substage_counter_12)

        self.register_value('touchoutside', self.touchoutside)

        self.register_value('session_first_stim', self.session_first_stim)
        self.register_value('forced_choice_actual_trial', self.forced_choice_actual_trial)
        self.register_value('forced_choice_next_trial', self.forced_choice_next_trial)
        self.register_value('forced_choice_probe', self.forced_choice_probe)

        self.register_value('last_two_stim', self.last_two_stim)
        self.register_value('consecutive_good_blocks', self.consecutive_good_blocks)
        self.register_value('consecutive_good_blocks_criteria', self.consecutive_good_blocks_criteria)
        self.register_value('last_block_accuracy', self.last_block_accuracy)

        self.register_value('fixation_trigger_port', str(self.fixation_trigger_port))


