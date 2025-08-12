from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
from academy import telegram_bot


class Cognitive_Bias_Auditory_Training(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task trains rats on 4 tone pairs for the cognitive bias tasks. 

        ########   TASK INFO   ########
        Goal: Train discrimination between tones within each of 4 frequency pairs.
        Procedure:
            Rats begin with Pair 1.
            Left/right responses (touchscreen) indicate tone identity (low/high); rewards differ in size (20 µL left vs 40 µL right sucrose water).
            Side and reward counterbalanced across rats.
            Partial reinforcement is introduced: 1 in 5 training trials is unrewarded.
            Rats proceed sequentially to Pairs 2, 3, and 4.
            Each pair uses a different shape to aid discrimination.
            Rats are split into 2 groups to counterbalance tone-reward mappings across pairs.
        Criterion: ≥85% correct for 2 consecutive sessions.
        Pairs:
        Pair 1:
            Low reference: 2000 Hz
            High reference: 3621 Hz
        Pair 2:
            Low reference: 4573 Hz
            High reference: 8281 Hz
        Pair 3:
            Low reference: 10458 Hz
            High reference: 18935 Hz
        Pair 4:
            Low reference: 23.913 Hz
            High reference: 43.298 Hz
        Training order: All rats follow Pair 1, Pair 2, Pair 3, Pair 4
        Randomization for Groups:
            8 rats:
            chandler, felix, fergus, geralt, joey, ross, innes, pol
            Stimulus sides:
                For each rat: randomly counterbalanced →
                Low tone = Left or Right
                High tone = Right or Left
            Reward mapping groups (between-subjects):
                Reward Group 1:
                    Pairs 1 & 3: High tone = Large reward
                    Pairs 2 & 4: Low tone = Large reward
                Reward Group 2 (opposite):
                    Pairs 1 & 3: Low tone = Large reward
                    Pairs 2 & 4: High tone = Large reward
            So in order to have a full factorial design:
            Summary of Reward Mapping per Group
                Group 1 (Pairs 1 & 3: High → large reward, left, triangle; Pairs 2 & 4: Low → large reward, right, triangle):
                    Rats: chandler, felix, joey, ross
                Group 2 (Pairs 1 & 3: Low → large reward, right, triangle; Pairs 2 & 4: High → large reward, right, triangle):
                
                    Rats: fergus, geralt, innes, pol
                
                ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED    
        """

        # Variables for the task:
        self.trials_max = 75
        self.duration_max = 3000
        self.duration_min = 2100
        self.duration_tired = 1800
        self.tired = False

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.reward_drunk = 0
        self.correct_count = 0
        self.accuracy = 0
        self.total_trials = 0  # Total number of trials in the current pair
        self.success = 0  # tracks if trial is correct or incorrect (1 or 0)

        # Tracked Variables - so that it is continuous within blocks (regardless of session)
        # self.block_accuracy = 0.0  # Accuracy for that 40 trial block
        # self.block_number = 1
        # self.block_change = 0
        # self.block_correct_count = 0  # Tracks the number of corrects in the block
        # self.block_valid_count = 0  ##Tracks the number of valid trials in the block
        # self.stage_forward_change = 0  # they've met criterion to move forward to next pair
        # self.stage_backward_change = 0  # they've met poor performance criterion to move back a pair
        # self.last_forward_stage = 0  # This is important for the moved_back_counter. Stores the last valaue for the forward pair change
        # self.last_backward_stage = 0  ##This is important for the moved_back_counter. Stores the last valaue for the backward pair change
        # self.moved_back_counter = 0  # number of times they have been moved back from one pair to another.

        # Variables for Cognitive_Bias_Auditory_Training Tracked:
        self.group = 0
        self.pair = 0

        #Untracked:
        self.side = None
        self.shape = None
        self.stim_trial = None  #probes 0 or 4 for training.
        self.last_stim_trial = 0  # It stores the correct side (L, R) of the last trial of the previous randomisation block
        self.stim = [0, 4]  # defines if correct side is left or right
        self.block_size = 75
        self.stim_trials = []
        self.stim_trial_counter = 0

        # --- Reward volumes (µL) ---
        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 5.6 #High reward, 140ul
        self.valve_factor_i = 2.8 #Low reward, 60 ul

        # --- Training parameters ---
        self.partial_reinforcement_ratio = 0.2

        # Correcth location and size:
        self.x_correcth_pos = [103, 308]  # Positions of the stim on the screen
        self.y_correcth = 150
        self.width = 100  # Stimulus width in mm. Original size for peg is 120mm.
        self.height = 100  # Stimulus height in mm. Original size for jar is 110mm.
        self.response_duration = 60


    def configure_gui(self):
        self.gui_input = ['group', 'pair', 'duration_max']

    def generate_random_trials(self,last_trial=None):  # Generates a series of stim outputs where none are repeated more than 2 times in sequence.
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

    #Function to map high, low sounds
    def derive_high_low(self, group: int, pair: int):
        """
        Return ((high_side, high_shape), (low_side, low_shape)) following the rule:
          group 1: pairs 1 & 3 → high=left/triangle; pairs 2 & 4 → high=right/circle
          group 2: inverse of group 1
        """
        if group == 1:
            if pair in (1, 3):  # high on left
                return ("left", "triangle"), ("right", "circle")
            if pair in (2, 4):  # high on right
                return ("right", "circle"), ("left", "triangle")
        elif group == 2:
            if pair in (1, 3):  # high on right
                return ("right", "circle"), ("left", "triangle")
            if pair in (2, 4):  # high on left
                return ("left", "triangle"), ("right", "circle")
        raise ValueError(f"Invalid group/pair: group={group}, pair={pair}")

    # --- Reward mapping lookup function ---
    # def get_reward_mapping(self, subject, pair):
    #     group = self.reward_group[subject]
    #     if group == 'A':
    #         if pair in [1, 3]:
    #             return {'low': self.reward_small, 'high': self.reward_large}
    #         else:  # pair in [2, 4]
    #             return {'low': self.reward_large, 'high': self.reward_small}
    #     elif group == 'B':
    #         if pair in [1, 3]:
    #             return {'low': self.reward_large, 'high': self.reward_small}
    #         else:  # pair in [2, 4]
    #             return {'low': self.reward_small, 'high': self.reward_large}

    def main_loop(self):
        print('subject', self.subject)
        print('task', self.task)
        print('block_size', self.block_size)
        print('stim_trial_counter', self.stim_trial_counter)

        if self.current_trial == 0:
            self.accuracy = 0
            self.stim_trial_counter = 0
            self.stim = [0, 4]

        # if self.block_change == 1:
        #     self.block_number += 1
        #     self.block_change = 0
        #     self.block_accuracy = 0.0
        #     self.block_trial_counter = 0  # Reset the counter after the block
        #     self.block_correct_count = 0
        #     self.block_valid_count = 0
        #     self.stim_trial_counter = 0

        # if self.stage_forward_change == 1:
        #     self.total_trials = 0
        #     self.stage_forward_change = 0
        #     self.last_forward_stage = self.pair  # Save current BEFORE increasing
        #     self.pair += 1
        #     message = f"Stage moved forward to {self.pair} for {self.subject} in {self.task}"
        #     try:
        #         telegram_bot.alarm_finish_session(message, self.subject)
        #     except Exception as e:
        #         print(f"Telegram message not sent. Error: {e}")
        #     if self.pair == 6:
        #         self.task_number = 2
        #         self.tired = True

        # if self.stage_backward_change == 1:
        #     self.total_trials = 0
        #     self.stage_backward_change = 0
        #     self.block_accuracy = 0.0
        #     self.block_trial_counter = 0  # Reset the counter after the block
        #     self.block_correct_count = 0
        #     self.block_valid_count = 0
        #     self.stim_trial_counter = 0
        #     new_stage = max(self.pair - 1, 1)
        #     if new_stage == self.last_forward_stage:
        #         if self.last_backward_stage == new_stage:
        #             self.moved_back_counter += 1
        #         else:
        #             self.moved_back_counter = 1
        #             self.last_backward_stage = new_stage
        #     else:
        #         self.moved_back_counter = 1
        #         self.last_backward_stage = new_stage
        #     self.pair = new_stage
        #     message = f"Stage moved backward to {self.pair} for {self.subject} in {self.task}"
        #     try:
        #         telegram_bot.alarm_finish_session(message, self.subject)
        #     except:
        #         print("Telegram message not sent")

        #Probe Generation:
        if self.stim_trial_counter % self.block_size == 0:  # Re-randomize every 75 trials
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

        # current probe for this trial (0 = low, 4 = high)
        self.stim_trial = self.stim_trials[self.stim_trial_counter]  # already 0 or 4

        # get mapping from your counterbalance
        (high_side, high_shape), (low_side, low_shape) = self.derive_high_low(int(self.group), int(self.pair))

        # pick correct side/shape for THIS trial based on probe
        if self.stim_trial == 4:  # HIGH probe
            self.side = high_side
            self.shape_correct = high_shape
            self.shape_incorrect = low_shape
        elif self.stim_trial == 0:  # LOW probe
            self.side = low_side
            self.shape_correct = low_shape
            self.shape_incorrect = high_shape
        else:
            raise ValueError(f"Unexpected probe (0 or 4 expected): {self.stim_trial}")

        self.side_incorrect = "right" if self.side == "left" else "left"

        # x positions
        if self.side == "left":
            self.x_correcth, self.x_incorrecth = self.x_correcth_pos[0], self.x_correcth_pos[1]
        else:
            self.x_correcth, self.x_incorrecth = self.x_correcth_pos[1], self.x_correcth_pos[0]

        print(
            f"group={self.group} pair={self.pair} probe={self.stim_trial} "
            f"correct_side={self.side} correct_shape={self.shape_correct} "
            f"incorrect_side={self.side_incorrect} incorrect_shape={self.shape_incorrect} "
            f"x_correcth={self.x_correcth} x_incorrecth={self.x_incorrecth} "
            f"width={self.width}, height={self.height}"
        )

        ############ STATE MACHINE ################
        # First trial:
        if self.task == "Cognitive_Bias_Auditory_Training":
            if self.current_trial == 0:
                self.sma.add_state(
                    state_name='Start_task',
                    state_timer=0,
                    state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, 234)])
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
                    state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                    output_actions=[])

            self.sma.add_state(
                state_name='Wait_for_fixation',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port4In: 'Fixation1'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 234)])
            # Does Nothing. Make it close door 3 later when Duncan has fixed it.

            self.sma.add_state(
                state_name='Fixation1',
                state_timer=2,
                state_change_conditions={Bpod.Events.Tup: 'Fixation2'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 230)])
            # Does Nothing. Make it close door 3 later when Duncan has fixed it.

            self.sma.add_state(
                state_name='Fixation2',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port6In: 'Response_window'},
                output_actions=[])
            # Changes the state to response window after photogate near the screen has been crossed. Here display the stimulus for trials after first trial.

            self.sma.add_state(
                state_name='Response_window',
                state_timer=self.response_duration,
                state_change_conditions={'SoftCode1': 'Correct', 'SoftCode3': 'Touch_Outside', 'SoftCode4': 'Punish',
                                         Bpod.Events.Tup: 'No_Touch'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 231)])
            # Starts to read the touchscreen with one touch processing

            self.sma.add_state(
                state_name='Correct',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Correct_image_display'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 232)])
            # Turns on Water port LED and plays correct sound

            self.sma.add_state(
                state_name='Correct_image_display',
                state_timer=0,
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
                state_timer=self.valve_time * self.valve_factor_i,
                state_change_conditions={Bpod.Events.Tup: 'Punish_image_display'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 233)])
            # Turns on Global LED and water port LED on

            self.sma.add_state(
                state_name='Punish_image_display',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port1In: 'After_punish', Bpod.Events.Tup: 'Flip_screen_no_reward'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6)])
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
            self.trial_length = None
            self.trial_result = None

    def after_trial(self):
        if self.task == "Cognitive_Bias_Auditory_Training":
            self.total_trials += 1  # remove this

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.trial_result = 'miss'

            ##### COUNT PUNISH
            elif self.current_trial_states['Punish'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.reward_drunk += self.valve_reward * self.valve_factor_i
                self.valid_counter += 1
                self.stim_trial_counter += 1
                self.success = 0
                print('Acc Valid_count: ', self.block_valid_count)

            ##### COUNT CORRECTS FIRST POKE
            elif self.current_trial_states['Correct'][0][0] > 0:
                self.trial_result = 'correct'
                self.valid_counter += 1
                self.stim_trial_counter += 1
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.correct_count += 1
                # print('Correct_count: ', self.correct_count)
                self.success = 1

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
            self.accuracy = self.correct_count / self.valid_counter if self.current_trial > 0 else 0
            print("Accuracy: ", self.accuracy)

            # if self.total_trials >= self.trial_end_criteria:
            #     self.stage_backward_change = 1
        else:
            print(
                "Task 2 ended because Extra training completed. Task is now 3 so will move to Urn training in next session.")

        ############ REGISTER VALUES ################
        # Task-related
        self.register_value('duration_max', self.duration_max)
        self.register_value('duration_min', self.duration_min)
        self.register_value('duration_tired', self.duration_tired)
        self.register_value('trials_tired', self.trials_tired)
        self.register_value('tired', self.tired)
        self.register_value('task_number', self.task_number)
        self.register_value('response_duration', self.response_duration)

        # Pumps
        self.register_value('valve_time', self.valve_time)
        self.register_value('valve_reward', self.valve_reward)
        self.register_value('valve_factor_c', self.valve_factor_c)
        self.register_value('valve_factor_i', self.valve_factor_i)

        # Counters
        self.register_value('valid_counter', self.valid_counter)
        self.register_value('tired_counter', self.tired_counter)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('correct_count', self.correct_count)
        self.register_value('accuracy', self.accuracy)
        self.register_value('success', self.success)

        # Stimulus-related
        self.register_value('stim', self.stim)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y_correcth', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)

        # Stage changes
        self.register_value('moved_back_counter', self.moved_back_counter)

        # Corecth location:
        self.register_value('correct_th', self.x_correcth)
        self.register_value('incorrect_th', self.x_incorrecth)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)

        # Trial Information:
        self.register_value('trial_length', self.trial_length)
        self.register_value('trial_result', self.trial_result)

        # Stimulus trial control
        self.register_value('group', self.group)
        self.register_value('pair', self.pair)
        self.register_value('side', self.side)
        self.register_value('shape', self.shape)
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)
        self.register_value('last_stim_trial', self.last_stim_trial)
        self.register_value('stim', self.stim)


