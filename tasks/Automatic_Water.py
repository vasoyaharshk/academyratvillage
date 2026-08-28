from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from academy import telegram_bot


class Automatic_Water(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Reward association with lickport and correct sound.
        Starts with reward sound ON + water port LED ON + automatic delivery of water.
        Sound and LED stay on until poke or timeup. Global lights always ON.

        ########   PORTS INFO   OLD   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - BUZZER: valve (16kHz): correct
        Port 4 - PHOTOGATES 0: Photogates next to lickport & Global LED


        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen , global LED
        """





    def init_variables(self):
        # general
        self.duration_max = 3000
        self.duration_min = 2100
        #self.trials_max = 300
        self.stage = 0
        self.substage = 0

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 1.5

        # counters
        self.miss_acc_counter = 0
        self.reward_drunk = 0

        # ==============================
        # Tracked Variables
        # ==============================
        # Needed in Each Task:
        self.stage = 0  # Current stage within the task
        self.substage = 0  # Current substage within the stage
        self.substage_bias = 0  # Side bias stage for substage behavior
        self.task_number = 0  # Each task has a unique number. See RV script guide.

        # Working Memory only:
        self.stim_dur_ds = 0  # Stimulus duration for short duration for working memory
        self.stim_dur_dm = 0  # Stimulus duration for medium duration for working memory
        self.stim_dur_dl = 0  # Stimulus duration for long duration for working memory
        self.choice = 0  # Choices subjects get in the working memory (for us its the same. Variable from IDIBAPs)

        # Weber's Law Pre and Post Test:
        self.block = 0  # Current block number for trials
        self.conditions = []  # List of all Weber's law conditions
        self.completed_conditions = []  # List of completed conditions
        self.current_condition = 0  # Current condition for the trial
        self.repetition = 0  # Number of repetitions for the Weber's Law
        self.current_repetition = 0  # Current repetition number for the trial
        self.trial_counter = 0  # Total number of trials run in the current block

        # Weber's Law Training:
        self.ror = []  # Ratio of Ratios (ROR) for Weber's Law Training
        self.completed_ror = []  # List of completed ROR levels
        self.current_ror = 0  # Current ROR of the trial
        self.trial_counter_ror = 0  # Counter for trials under current ROR
        self.last_condition_trial = 0  # Condition of the last trial of the previous block. Used to ensure first trial of next block is different

        # Needed to create blocks of 40 trials for criterion to be assessed on:
        self.block_size = 0  # The number of trials in a block
        self.block_trial_counter = 0  # Trial count within the current block
        self.block_accuracy = 0.0  # Accuracy in the current block
        self.block_number = 0  # Sequential block number
        self.ror_change = 0  # If it is 1, ROR will change on the next trial.
        self.block_change = 0  # If it is 1, a new block will start on the next trial
        self.total_trials = 0  # Total trials across the task.
        self.block_correct_count = 0  # Number of correct responses in the block
        self.block_valid_count = 0  # Number of valid (non-missed) trials in the block
        self.block_stim_correct_count_1 = 0
        self.block_stim_valid_count_1 = 0
        self.block_stim_accuracy_1 = 0.0
        self.block_stim_correct_count_2 = 0
        self.block_stim_valid_count_2 = 0
        self.block_stim_accuracy_2 = 0.0
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
        self.max_move_backs = 0
        self.stage_sequence = []

        # Stage and Cognitive Bias continuity
        self.last_stage_trial = 0
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
        self.group = 0
        self.pair = 0
        self.prev_block_accuracy = -1.0
        self.last_block_accuracy = 0.0
        self.last_two_stim = []
        self.unrewarded_list = []
        self.pr_carry_tone = ""
        self.pr_carry_pending = 0
        self.consecutive_good_blocks = 0

        self.intertrial_interval = 60
        self.trial_result = None

    def configure_gui(self): # Variables that appear in the GUI
        pass

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # flooding AVOIDANCE
        if self.miss_acc_counter > 300:
            flooding = 'Wait_for_reward'
        else:
            flooding = 'Automatic_reward'

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                output_actions = [(Bpod.OutputChannels.SoftCode, 234), (Bpod.OutputChannels.LED, 3)])  # Draws black screen
                # global LED ON

            self.sma.add_state(
                state_name='Real_start',  # close corridor door 2 when subject enters to behavioral box
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.LED, 3)])
        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Fixation'},
                output_actions=[(Bpod.OutputChannels.LED, 3)])

        self.sma.add_state(
            state_name='Fixation',  # if animal licks during fixation, this is started again.
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Fixation_break', Bpod.Events.Tup: flooding},
            output_actions=[(Bpod.OutputChannels.LED, 3)])

        self.sma.add_state(
            state_name='Fixation_break',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Fixation'},
            output_actions=[(Bpod.OutputChannels.LED, 3)])

        self.sma.add_state(
            state_name='Automatic_reward',
            state_timer=self.valve_time*self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Wait_for_reward'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.PWM1, 1), (Bpod.OutputChannels.PWM3, 1),
                            (Bpod.OutputChannels.SoftCode, 220)])
            # Automatic water, lickportLED, and Reward sound

        self.sma.add_state(
            state_name='Wait_for_reward',
            state_timer=30,
            state_change_conditions={Bpod.Events.Tup: 'Miss', Bpod.Events.Port1In: 'Correct_first'},
            output_actions=[(Bpod.OutputChannels.PWM1, 1), (Bpod.OutputChannels.PWM3, 1)])
            # lickportLED and RWsound remain ON until poke o timeup

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.LED, 3)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 12),(Bpod.OutputChannels.LED, 3)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=10,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 222), (Bpod.OutputChannels.LED, 3)])
            # Wait 10 sec for the next automatic reward


    def after_trial(self):
        # Frequency verification
        # expected = self.reward_frequency_map.get(self.subject, None)
        # actual = self.reward_frequency
        #
        # if expected is None:
        #     message = f"URGENT: No expected frequency set for '{self.subject}'"
        #     try:
        #         telegram_bot.alarm_finish_session(message, self.subject)
        #     except:
        #         print('Telegram message not sent')
        # elif round(expected, 2) != round(actual, 2):
        #     message = f"🚨 URGENT: Frequency mismatch for {self.subject} — expected {expected} Hz, got {actual} Hz"
        #     try:
        #         telegram_bot.alarm_finish_session(message, self.subject)
        #     except:
        #         print('Telegram message not sent')


        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0:  # Missed trial
            self.trial_result = 'miss'
            self.miss_acc_counter += 1
        else:
            self.trial_result = 'correct_first'
            self.miss_acc_counter = 0

        if self.current_trial_states['Automatic_reward'][0][0] > 0:
            self.reward_drunk += self.valve_reward * self.valve_factor_c


        # General counters
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('miss_acc_counter', self.miss_acc_counter)

        # Task structure
        self.register_value('task_number', self.task_number)
        self.register_value('stage', self.stage)
        self.register_value('substage', self.substage)
        self.register_value('substage_bias', self.substage_bias)
        self.register_value('choice', self.choice)

        # Working Memory durations
        self.register_value('stim_dur_ds', self.stim_dur_ds)
        self.register_value('stim_dur_dm', self.stim_dur_dm)
        self.register_value('stim_dur_dl', self.stim_dur_dl)

        # Weber’s Law Pre/Post
        self.register_value('block', self.block)
        self.register_value('conditions', self.conditions)
        self.register_value('completed_conditions', self.completed_conditions)
        self.register_value('current_condition', self.current_condition)
        self.register_value('repetition', self.repetition)
        self.register_value('current_repetition', self.current_repetition)
        self.register_value('trial_counter', self.trial_counter)

        # Weber’s Law Training
        self.register_value('ror', self.ror)
        self.register_value('completed_ror', self.completed_ror)
        self.register_value('current_ror', self.current_ror)
        self.register_value('trial_counter_ror', self.trial_counter_ror)
        self.register_value('last_condition_trial', self.last_condition_trial)

        # Block tracking
        self.register_value('block_size', self.block_size)
        self.register_value('block_trial_counter', self.block_trial_counter)
        self.register_value('block_accuracy', self.block_accuracy)
        self.register_value('block_number', self.block_number)
        self.register_value('ror_change', self.ror_change)
        self.register_value('block_change', self.block_change)
        self.register_value('total_trials', self.total_trials)
        self.register_value('block_correct_count', self.block_correct_count)
        self.register_value('block_valid_count', self.block_valid_count)
        self.register_value('block_stim_correct_count_1', self.block_stim_correct_count_1)
        self.register_value('block_stim_valid_count_1', self.block_stim_valid_count_1)
        self.register_value('block_stim_accuracy_1', self.block_stim_accuracy_1)
        self.register_value('block_stim_correct_count_2', self.block_stim_correct_count_2)
        self.register_value('block_stim_valid_count_2', self.block_stim_valid_count_2)
        self.register_value('block_stim_accuracy_2', self.block_stim_accuracy_2)

        # Condition and stage tracking
        self.register_value('condition_trial_counter', self.condition_trial_counter)
        self.register_value('last_forward_stage', self.last_forward_stage)
        self.register_value('last_backward_stage', self.last_backward_stage)
        self.register_value('moved_back_counter', self.moved_back_counter)
        self.register_value('stage_forward_change', self.stage_forward_change)
        self.register_value('stage_backward_change', self.stage_backward_change)
        self.register_value('max_move_backs', self.max_move_backs)
        self.register_value('stage_sequence', self.stage_sequence)
        self.register_value('last_stage_trial', self.last_stage_trial)
        self.register_value('stage_sequence_counter', self.stage_sequence_counter)
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

        # Cognitive Bias state
        self.register_value('group', self.group)
        self.register_value('pair', self.pair)
        self.register_value('prev_block_accuracy', self.prev_block_accuracy)
        self.register_value('last_block_accuracy', self.last_block_accuracy)
        self.register_value('last_two_stim', self.last_two_stim)
        self.register_value('unrewarded_list', self.unrewarded_list)
        self.register_value('pr_carry_tone', self.pr_carry_tone)
        self.register_value('pr_carry_pending', self.pr_carry_pending)
        self.register_value('consecutive_good_blocks', self.consecutive_good_blocks)

        # Reward sound settings
        self.register_value('reward_frequency', self.reward_frequency)
        self.register_value('reward_db', self.reward_db)
        self.register_value('reward_duration', self.reward_duration)

        # Stimulus randomisation
        self.register_value('stim_trial', self.stim_trial)
        self.register_value('stim_trials', self.stim_trials)
        self.register_value('stim_trial_counter', self.stim_trial_counter)
        self.register_value('last_stim_trial', self.last_stim_trial)

        # Trial outcome placeholder
        self.register_value('trial_result', self.trial_result)
        self.register_value('response_x', 0)  # we add a zero here to easily compare with other tasks
        self.register_value('response_y', 0)  # we add a zero here to easily compare with other tasks


