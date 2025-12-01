from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
from academy import telegram_bot


class A_TouchTeaching_blob(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task displays the image of the jars which are touchable. This script is for the extra training if rats are struggling to discriminate between stimuli.

        ########   TASK INFO   ########
        Rats learn to touch the screen during the response window to obtain the reward.
        
        Stages:
        Stage 3: A white irregular blob the same size as the screen.
        Stage 1: A white irregular blob the same size and same location as the pegs. Rat has to touch the white blob but also can touch anywhere else.
        Stage 2: A white irregular blob the same size and same location as the pegs. Rat has to touch the white blob but if touches anywhere else is incorrect.

                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED

        NOTE: FOR NEW SOUNDS, FUNCTION38 NEEDS TO BE REPLACED WITH 220 EVERYWHERE.
        """

        # Variables for the task:
        self.duration_max = 3000
        self.duration_min = 2100
        self.duration_tired = 1800
        self.trials_tired = 5  # if they do 5 trials of long duration, the door will open after 30 mins rather than 35
        self.tired = False
        self.task_number = 1
        self.stage = 1
        self.substage = 0
        self.substage_bias = 0  # 1 = 90:10, 2 = 75:25, 3 = 50:50
        self.response_duration = 60
        self.image_display = 0  # Number of seconds the image will display after correct and incorrect

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 1.0  # Normal water delivery must be a multiple of 25ul. 2.0 is 2 x 25 = 50uL. E.g., if you set it to 1.8, this would be 1.8 x 25 = 45uL
        # self.valve_factor_i = 0.6  # Water delivery for incorrects/punish - only if want to give water if they do an incorrect trial (only used for scripts that allow correction)

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.reward_drunk = 0
        self.correct_count = 0
        self.accuracy = 0

        # Image output stims:
        self.stim = [0]  # defines if correct side is left or right

        # Correcth location and size:
        # self.x_correcth_pos = [75, 315]  # Positions of the stim on the screen
        # self.y_correcth = 110
        # self.width = 160  # Stimulus width in mm. Original size for peg is 120mm.
        # self.height = 235  # Stimulus height in mm. Original size for jar is 110mm.
        self.x_correcth_pos = [90, 320]  # Horizontal Coordinates for left and right for Jars
        self.y_correcth = 155  # Vertical Coordinates for left and right for Jars
        self.x_incorrecth = None
        self.width = 100  # Stimulus width in mm. Original size for jar is 120mm.
        self.height = 100  # Stimulus height in mm. Original size for jar is 110mm.
        self.contrast = 0.4  # contrast of the stim. 0 black, 1 gray, 2 white. Default 40%

        # Bias breaking variables:
        self.bias_breaking = 0  # If subject chooses same side for 5 trials in a row, bias breaking becomes active
        self.response_x_array = []  # Stores responses for x till 3 values
        self.sameside_counter = 0  # Counts number of times on same side
        self.sameside = None  # To track which side is being triggered
        self.side_bias_trigger = 5  # After how many trials does side_bias trigger
        self.side_bias_trigger_acc = 0.8
        self.status = None  # Stores the Touch outside condition
        self.biased_consecutive_corrects_counter = 0  # This is the counter for counting the number of corrects when bias breaking is active
        self.biased_consecutive_corrects = 3  ##This is the number of corrrects the rat needs to do to end bias breaking

        self.bias_accuracy_trials = []
        self.bias_accuracy = 0
        self.accuracy_criteria = 0.80  # move forward criteria. 80% success on block_size(32/40 trials correct)
        self.trial_end_criteria = 320  # Move back criteria. Badly named - this is task end criteria.
        self.max_move_backs = 5  # number of times they can be moved back (i.e., they've done 320 trials 5 times) before we review
        self.success = 0  # tracks if trial is correct or incorrect (1 or 0)

        # Tracked Variables - so that it is continuous within blocks (regardless of session)
        self.block_size = 40  # Every 40 blocks the criteria will be tested.
        self.block_trial_counter = 0  # Counter for block
        self.block_accuracy = 0.0  # Accuracy for that 40 trial block
        self.block_number = 1
        self.block_change = 0
        self.last_stim_trial = 0  # It stores the correct side (L, R) of the last trial of the previous randomisation block
        self.total_trials = 0  # Total number of trials in that ROR irrespective of conditions
        self.block_correct_count = 0  # Tracks the number of corrects in the block
        self.block_valid_count = 0  ##Tracks the number of valid trials in the block

        self.prev_block_accuracy = -1.0  #Stores the block_accuracy for previous block, Set to -1 because cannot use None. #This stores the last block accuracy only if criteria met otherwise it is -1.
        self.last_block_accuracy = 0.0 #This stores the accuracy of the last complete block

        self.stim_trial = 0
        self.stim_trials = []
        self.stim_trial_counter = 0

        self.stage_forward_change = 0  # they've met criterion to move forward to next stage
        self.stage_backward_change = 0  # they've met poor performance criterion to move back a stage
        self.last_forward_stage = 0  # This is important for the moved_back_counter. Stores the last valaue for the forward stage change
        self.last_backward_stage = 0  ##This is important for the moved_back_counter. Stores the last valaue for the backward stage change
        self.moved_back_counter = 0  # number of times they have been moved back from one stage to another. It needs to

        self.task_end = False

        self.session_first_stim = None  # first stim of this session (left or right)
        self.last_two_stim = []         # history of last two stim_trial values across sessions

    def configure_gui(self):
        self.gui_input = ['stage', 'substage', 'duration_max', 'block_size']

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
        ### Randomizing the stimulus positions for both the images:
        print('')
        self.bias_breaking = 0
        ### Randomizing the stimulus positions for both the images:

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
            self.prev_block_accuracy = -1.0
            self.last_forward_stage = self.stage  # Save current BEFORE increasing
            if self.stage == 0:
                self.stage += 2
            else:
                self.stage += 1
            message = f"Stage moved forward to {self.stage} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except Exception as e:
                print(f"Telegram message not sent. Error: {e}")
            if self.stage == 3:
                self.task_number = 2
                self.tired = True
                message = f"URGENT: Stage moved forward to {self.stage} for {self.subject} in {self.task}. Email ALEX."
                try:
                    telegram_bot.alarm_finish_session(message, self.subject)
                except Exception as e:
                    print(f"Telegram message not sent. Error: {e}")

        if self.stage_backward_change == 1:
            self.total_trials = 0
            self.stage_backward_change = 0
            self.block_accuracy = 0.0
            self.prev_block_accuracy = -1.0
            self.block_trial_counter = 0  # Reset the counter after the block
            self.block_correct_count = 0
            self.block_valid_count = 0
            self.stim_trial_counter = 0
            new_stage = max(self.stage - 1, 0)
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
        self.stim = [213, 214]  # These are teh axis for the functions 211 for sqaure on the left and 212 for sqaure on the right

        if self.stage == 0:
            self.stim_trial = 215
            self.x_correcth = settings.CENTRE_SCREEN[0]  # 640 = center of the screen. Screen width is 401mmm
            self.y_correcth = settings.CENTRE_SCREEN[1]  # 640 = center of the screen. Screen height is 250mmm
            self.width = settings.WIN_RESOLUTION[0]
            self.height = settings.WIN_RESOLUTION[1]
        else:
            if self.stim_trial_counter % self.block_size == 0 and self.bias_breaking == 0:  # Re-randomize every 20 trials
                # If not the first block_size, pass the last stimulus of the previous block_size to avoid repetition
                self.last_stim_trial = self.stim_trials[self.stim_trial_counter - 1] if self.stim_trial_counter > 0 else None
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

            # --- session-local logic for first two trials in this session ---
            if self.current_trial == 0:
                # first trial in this session: random left/right
                candidate = random.choice(self.stim)  # 213 or 214
                self.session_first_stim = candidate
            elif self.current_trial == 1:
                # second trial in this session: forced opposite of first
                if self.session_first_stim == 213:
                    candidate = 214
                else:
                    candidate = 213
            else:
                # from 3rd trial onwards: normal block / bias-breaking logic
                if self.bias_breaking == 0:
                    candidate = self.stim_trials[self.stim_trial_counter]
                else:
                    candidate = self.last_stim_trial

            # --- global guard: never allow 3 same-side stimuli in a row across sessions ---
            if len(self.last_two_stim) >= 2 and candidate == self.last_two_stim[-1] == self.last_two_stim[-2]:
                # flip side
                candidate = 213 if candidate == 214 else 214

            self.stim_trial = candidate


            # Here, if we need to define the correcth_x position based on the stimulus. So function 31 displays stimulus with correct answer on the left (x=115) and 32 displays stimulus with correct answer on right (x=295)
        if self.stim_trial == 213:
            self.x_correcth = self.x_correcth_pos[0]
            self.x_incorrecth = None  # No incorrect area in stage 1
            # print('Correct Answer: Left, ', 'X position = ', self.x_correcth)
        elif self.stim_trial == 214:
            self.x_correcth = self.x_correcth_pos[1]
            self.x_incorrecth = None  # No incorrect area in stage 1
            # print('Correct Answer: Right, ', 'X position = ', self.x_correcth)

        print('Stage: ', self.stage)
        print('Stimulus trial: ', self.stim_trial)
        print('Stimulus Trial Counter', self.stim_trial_counter)
        print('prev_block_accuracy', self.prev_block_accuracy)
        print('last_block_accuracy', self.last_block_accuracy)

        ############ STATE MACHINE ################
        # First trial:
        if self.task_number == 1:
            if self.stage == 1:  #Stage 1 has only correct, if they touch outside, they can retry
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
                    state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', 'SoftCode4': 'Punish',
                                             Bpod.Events.Tup: 'No_Touch'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, 204)])
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
                    output_actions=[(Bpod.OutputChannels.PWM1, 5)])
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
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 39)])
                # Turns on Global LED and water port LED on

                self.sma.add_state(
                    state_name='Punish_image_display',
                    state_timer=self.image_display,
                    state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 57)])
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
            else: #Stage 2 has only correct, if they touch outside, it is incorrect
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
                    state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Punish', 'SoftCode4': 'Punish',
                                             Bpod.Events.Tup: 'No_Touch'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, 204)])
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
                    output_actions=[(Bpod.OutputChannels.PWM1, 5)])
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
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 39)])
                # Turns on Global LED and water port LED on

                self.sma.add_state(
                    state_name='Punish_image_display',
                    state_timer=self.image_display,
                    state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
                    output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                    (Bpod.OutputChannels.SoftCode, 57)])
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
            print(
                "Task 1 ended because Extra training completed. Task is now 3 so will move to Urn training in next session.")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.x_correcth = None
            self.x_incorrecth = None
            self.response_x = None
            self.response_y = None
            self.trial_result = None

    def after_trial(self):
        if self.task_number == 1:
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
                # print('Correct_count: ', self.correct_count)
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
                    if self.biased_consecutive_corrects_counter >= self.biased_consecutive_corrects:  # If three corrects after bias breaking
                        self.bias_breaking = 0  # End bias breaking
                        self.stim_trial_counter = 0
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

            # Check accuracy for every block of 40 trials
            self.block_accuracy = (self.block_correct_count / self.block_valid_count if self.block_valid_count > 0 else 0)
            print("Block Accuracy: ", self.block_accuracy)

            # Change block_trial_counter to block_trial_counter, and then block_counter should be the number of block.
            if self.block_trial_counter == self.block_size:
                self.block_change = 1
                self.last_block_accuracy = self.block_accuracy

                if self.block_accuracy >= self.accuracy_criteria:
                    if self.prev_block_accuracy >= self.accuracy_criteria:
                        self.stage_forward_change = 1
                        print("Two consecutive blocks >= criterion. Advancing stage.")
                    else:
                        self.prev_block_accuracy = self.block_accuracy
                        print("Good block. One more needed.")
                else:
                    print("Block failed. Resetting previous block.")
                    self.prev_block_accuracy = -1.0

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
                    self.last_stim_trial = 212  # Ensure last_stim_trial is 212
                elif all_right_side:
                    self.sameside = 'right'
                    self.bias_breaking = 1
                    self.last_stim_trial = 211  # Ensure last_stim_trial is 211
                    print('Bias breaking active, side:', self.sameside)

                self.response_x_array = []  # Clearing the array

            print("Block Trial Counter: ", self.block_trial_counter)
            print("Block Accuracy: ", self.block_accuracy)
            print("Block Number: ", self.block_number)
            print("Block Size: ", self.block_size)
            print("Task Number: ", self.task_number)
            print("Stage Number: ", self.stage)
            print("Block Change: ", self.block_change)
            print("Stage Change Forward: ", self.stage_forward_change)
            print("Stage Change Backward: ", self.stage_backward_change)
            print("Moved Back Counter: ", self.moved_back_counter)

        else:
            print(
                "Task 2 ended because Extra training completed. Task is now 3 so will move to Urn training in next session.")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.x_correcth = None
            self.x_incorrecth = None
            self.response_x = None
            self.response_y = None
            self.trial_result = None
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

        self.register_value('prev_block_accuracy', self.prev_block_accuracy)
        self.register_value('last_block_accuracy', self.last_block_accuracy)

        self.register_value('session_first_stim', self.session_first_stim)
        self.register_value('last_two_stim', self.last_two_stim)
