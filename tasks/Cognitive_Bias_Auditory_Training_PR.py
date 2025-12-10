from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings
import random
import numpy as np
from academy import telegram_bot


class Cognitive_Bias_Auditory_Training_PR(Task):
    def __init__(self):
        super().__init__()

        self.info = """
        This task trains rats on 4 tone pairs for the cognitive bias tasks. 

        ########   TASK INFO   ########
        Goal:
            Train discrimination between tones within each of 4 frequency pairs.

        Procedure:
            • Rats are pre-assigned to a Group (1–4) and a starting Pair (1–4) in subjects.csv.
            • Each Pair is defined by a Low and a High reference frequency.
            • On each trial, the rat touches left or right to indicate the tone (low or high).
            • Correct touches are rewarded with sucrose water. Reward magnitude depends on:
                – Which tone is designated the “high-reward” tone for that Group × Pair.
                – High-reward = 5.6× water, Low-reward = 2.8× water.
            • For each Group, Table 1 defines:
                – Whether the High or Low tone is the high-reward tone (HF→HR or LF→HR).
                – Which side the High tone appears on (left or right).
                – The High-reward side then follows automatically from those two.
            • Shapes (triangle, circle, square, star) are also counterbalanced across Groups/Pairs to aid discrimination.
            • Rats are presented with variably reinforced trials, where approximately 1 in every 10 trials will randomly not be rewarded from the start of training.
            The non-reinforced trials are pseudorandomised so that no more than two consecutive trials of the same tone type (high or low) are unrewarded.


        Criterion: ≥80% correct across 3 consecutive blocks (per Pair).

        Pairs (reference tones):
            Pair 1:  Low 2000 Hz,   High 3621 Hz
            Pair 2:  Low 4573 Hz,   High 8281 Hz
            Pair 3:  Low 10458 Hz,  High 18935 Hz
            Pair 4:  Low 23913 Hz,  High 43298 Hz

        Group structure:
            • 4 Groups total (Groups 1–4).
            • Each Group implements a different counterbalancing of:
                – Which tone is high-reward (HF vs LF).
                – Which side is correct for the High tone (Left vs Right).
                – Thus across all 4 Groups, high-reward side, tone–reward mapping,
                  and side assignment are fully counterbalanced.
            • Each rat is assigned to one Group and progresses through all 4 Pairs.

        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - PHOTOGATES 2: Photogates next to lickport 
        Port 3 - PHOTOGATES 3: Photogates 
        Port 4 - PHOTOGATES 4: Photogates 
        Port 5 - PHOTOGATES 5: Photogates 
        Port 6 - PHOTOGATES 6: Photogates next to screen, global LED

        Task Number = 2
        """

        # Variables for the task:
        self.task_number = 1
        self.trials_max = 80
        self.duration_max = 3000
        self.duration_min = 2100
        self.duration_tired = 1800
        self.tired = False

        # counters for trials:
        self.valid_counter = 0
        self.tired_counter = 0
        self.reward_drunk = 0
        self.reward = 0
        self.correct_count = 0
        self.success = 0  # tracks if trial is correct or incorrect (1 or 0)
        self.trial_end_criteria = 320
        self.accuracy_criteria = 0.80
        self.consecutive_good_blocks_criteria = 3
        self.consecutive_good_blocks = 0
        self.max_move_backs = 5

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

        self.prev_block_accuracy = -1.0  # Stores the block_accuracy for previous block, Set to -1 because cannot use None. #This stores the last block accuracy only if criteria met otherwise it is -1.
        self.last_block_accuracy = 0.0  # This stores the accuracy of the last complete block

        self.stim_trial = None
        self.stim_trials = []
        self.stim_trial_counter = 0

        self.stage_forward_change = 0  # they've met criterion to move forward to next stage
        self.stage_backward_change = 0  # they've met poor performance criterion to move back a stage
        self.last_forward_stage = 0  # This is important for the moved_back_counter. Stores the last valaue for the forward stage change
        self.last_backward_stage = 0  ##This is important for the moved_back_counter. Stores the last valaue for the backward stage change
        self.moved_back_counter = 0  # number of times they have been moved back from one stage to another. It needs to

        self.last_two_stim = []  # history of last two stim_trial values across sessions. Tracked.

        # Variables for Cognitive_Bias_Auditory_Training Tracked:
        self.group = 0
        self.pair = 0

        # Untracked:
        self.session_first_stim = None  # first stim of this session (left or right)
        self.task_end = False

        self.side = None
        self.shape = None
        self.stim = [0, 4]  # defines if correct side is left or right

        # --- Reward volumes (µL) ---
        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
        self.valve_factor_c = 0  # High reward, 140ul
        # self.valve_factor_i = 2.8 #Low reward, 60 ul

        # Correcth location and size:
        self.x_correcth_pos = [75, 345]  # Positions of the stim on the screen
        self.y_correcth = 155
        self.width = 100  # Stimulus width in mm. Original size for peg is 120mm.
        self.height = 100  # Stimulus height in mm. Original size for jar is 110mm.
        self.response_duration = 60

        # === New Table 1 mapping (group 1..4; pair 1..4) ===
        # Keys per pair:
        #   'hr_tone'         → which tone gets LARGE reward ('high' or 'low')
        #   'high_tone_side'  → correct side for the HIGH tone ('left' or 'right')
        self.table1 = {
            1: {  # Group 1 → HR side = RIGHT
                1: {'hr_tone': 'high', 'high_tone_side': 'right'},
                2: {'hr_tone': 'low', 'high_tone_side': 'left'},
                3: {'hr_tone': 'high', 'high_tone_side': 'right'},
                4: {'hr_tone': 'low', 'high_tone_side': 'left'},
            },
            2: {  # Group 2 → HR side = LEFT
                1: {'hr_tone': 'low', 'high_tone_side': 'right'},
                2: {'hr_tone': 'high', 'high_tone_side': 'left'},
                3: {'hr_tone': 'low', 'high_tone_side': 'right'},
                4: {'hr_tone': 'high', 'high_tone_side': 'left'},
            },
            3: {  # Group 3 → HR side = RIGHT
                1: {'hr_tone': 'high', 'high_tone_side': 'right'},
                2: {'hr_tone': 'low', 'high_tone_side': 'left'},
                3: {'hr_tone': 'high', 'high_tone_side': 'right'},
                4: {'hr_tone': 'low', 'high_tone_side': 'left'},
            },
            4: {  # Group 4 → HR side = LEFT
                1: {'hr_tone': 'low', 'high_tone_side': 'right'},
                2: {'hr_tone': 'high', 'high_tone_side': 'left'},
                3: {'hr_tone': 'low', 'high_tone_side': 'right'},
                4: {'hr_tone': 'high', 'high_tone_side': 'left'},
            },
        }

        # --- Partial reinforcement (PR) control ---
        self.partial_reinforcement_active = 1  # turn PR on/off
        self.partial_reinforcement_ratio = 0.2  # 1-in-10
        self.unrewarded_list = []  # filled per block; 1 = skip reward on correct
        self.unrewarded_trial = 0  # store in after_trial
        self.tone_played = None

        self.pr_carry_pending = 0  # owe an unreward from a missed (incorrect) scheduled index
        self.pr_carry_tone = ""  # 'high' or 'low' we owe
        self.pr_carry_deadline = -1  # absolute trial index by which we must pay even if tone doesn't match
        # you can tweak how long we wait to keep the tone exactly:
        self.pr_carry_max_windows = 1  # wait up to 1 extra window to match tone before falling back
        self.unrewarded_tone = None
        self.unrewarded_list_planned = []

        # Forced-choice logic
        self.forced_choice_actual_trial = 0
        self.forced_choice_next_trial = 0  # type of the current trial, 0 for normal 1 for forced choice
        self.forced_choice_probe = None  # 0 or 4, probe to repeat on forced-choice trials

        self.touchoutside = 0

    def configure_gui(self):
        self.gui_input = ['group', 'pair', 'duration_max', 'block_size']

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

    # Function to map high, low sounds
    def derive_high_low(self, group: int, pair: int):
        """
        Return (high_side, low_side) from Table 1.
        """
        group = int(group);
        pair = int(pair)
        try:
            high_side = self.table1[group][pair]['high_tone_side']
        except KeyError:
            raise ValueError(f"Invalid (group, pair) in Table1: ({group}, {pair})")
        low_side = 'left' if high_side == 'right' else 'right'
        return high_side, low_side

    # --- NEW: per-rat/per-group counterbalanced shapes (all four pairs different) ---
    def shape_for_pair(self, subject: str, pair: int) -> str:
        """
        Return the shape for the given subject and pair, using the Shapes table.
        Pair is 1..4. No dependency on tone group.
        """
        name = (subject or "").strip().lower()

        # Shapes table (subject : rotation for pairs 1..4)
        rotations = {
            "chand": ["triangle", "circle", "square", "star"],
            "felix": ["circle", "square", "star", "triangle"],
            "joey": ["square", "star", "triangle", "circle"],
            "ross": ["star", "triangle", "circle", "square"],
            "fergus": ["triangle", "circle", "square", "star"],
            "geralt": ["circle", "square", "star", "triangle"],
            "innes": ["square", "star", "triangle", "circle"],
            "pol": ["star", "triangle", "circle", "square"],
            "m3": ["triangle", "circle", "square", "star"],  # fallback subject used in your code
        }

        seq = rotations.get(name)
        if seq is None:
            # deterministic fallback rotation for unknown names
            base = ["triangle", "circle", "square", "star"]
            shift = (hash(name) % 4)
            seq = base[shift:] + base[:shift]

        if pair not in (1, 2, 3, 4):
            raise ValueError(f"Invalid pair: {pair}")
        return seq[pair - 1]

    def partial_reinforcement_list(self, stim_seq, ratio=0.1):
        """
        Random, balanced partial reinforcement list (no forced alternation).
          • Exactly one unrewarded per window (window = round(1/ratio))
          • Exactly 50–50 high vs low among unrewarded across the whole block
          • No >=3 consecutive unrewarded of the same tone (in unrewarded-tone stream)
        Returns a 0/1 list aligned to stim_seq.
        """
        n = len(stim_seq)
        block = max(1, int(round(1.0 / float(ratio))))  # 0.1→10, 0.2→5
        num_blocks = n // block
        lst = [0] * n
        # Collect candidate indices by window, split by tone
        windows = [(b * block, (b + 1) * block) for b in range(num_blocks)]
        by_win = []
        for s, e in windows:
            highs = [i for i in range(s, e) if stim_seq[i] == 4]
            lows = [i for i in range(s, e) if stim_seq[i] == 0]
            by_win.append((highs, lows))

        # Quotas: exactly half high, half low (when num_blocks even, which it is for 80 trials)
        target_high = num_blocks // 2
        target_low = num_blocks - target_high
        # Build a random target tone sequence of length num_blocks with exact quotas
        # and reject sequences with any run >=3; if needed, repair.
        target = ['high'] * target_high + ['low'] * target_low

        def has_triple(seq):
            run = 1
            for i in range(1, len(seq)):
                run = run + 1 if seq[i] == seq[i - 1] else 1
                if run >= 3:
                    return True
            return False

        # Try a few random shuffles; if unlucky, repair by local swaps
        for _ in range(200):
            random.shuffle(target)
            if not has_triple(target):
                break
        else:
            # Repair pass: scan and swap with a later different-tone position
            i = 2
            while i < len(target):
                if target[i] == target[i - 1] == target[i - 2]:
                    # find a later j to swap that breaks the triple
                    j = i + 1
                    swapped = False
                    while j < len(target):
                        if target[j] != target[i]:
                            target[i], target[j] = target[j], target[i]
                            swapped = True
                            break
                        j += 1
                    # if we couldn't swap (extremely unlikely with balanced quotas), leave as-is
                    i += 1
                    continue
                i += 1
        # Now, for each window, pick an index that matches the target tone
        for b, tone in enumerate(target):
            s, e = windows[b]
            highs, lows = by_win[b]
            if tone == 'high' and highs:
                idx = random.choice(highs)
            elif tone == 'low' and lows:
                idx = random.choice(lows)
            else:
                # Fallback if window lacks desired tone (rare); pick any in window
                idx = random.randrange(s, e)
            lst[idx] = 1
        return lst

    # This gives alternating sequeunce:
    # def partial_reinforcement_list_balanced(stim_seq, ratio=0.1):
    #     """
    #     Exactly 1 unrewarded per window (window = round(1/ratio)),
    #     exact 50–50 high/low among unrewarded across the whole block,
    #     and no runs ≥3 of same unrewarded tone (achieved by alternating pattern).
    #     """
    #     import random
    #
    #     n = len(stim_seq)
    #     block = max(1, int(round(1.0 / float(ratio))))  # 0.1→10, 0.2→5
    #     num_blocks = n // block
    #     lst = [0] * n
    #
    #     # Build an alternating target sequence of tones for the num_blocks windows.
    #     # Randomly choose whether to start with 'high' or 'low' so it doesn't always align the same way.
    #     start_high = bool(random.getrandbits(1))
    #     target_seq = [('high' if ((i % 2 == 0) == start_high) else 'low') for i in range(num_blocks)]
    #
    #     # Ensure exact 50–50 by flipping the last element if needed (only matters when num_blocks is even; here it is).
    #     if target_seq.count('high') != num_blocks // 2:
    #         target_seq[-1] = 'high' if target_seq[-1] == 'low' else 'low'
    #
    #     # For each window, pick an index matching the target tone.
    #     for b in range(num_blocks):
    #         s, e = b * block, (b + 1) * block
    #         tone = target_seq[b]
    #         candidates = [i for i in range(s, e) if (stim_seq[i] == 4 if tone == 'high' else stim_seq[i] == 0)]
    #
    #         if not candidates:
    #             # Extremely unlikely with your stim generator; fallback to the opposite tone
    #             alt = [i for i in range(s, e) if (stim_seq[i] == 0 if tone == 'high' else stim_seq[i] == 4)]
    #             candidates = alt if alt else list(range(s, e))
    #
    #         lst[random.choice(candidates)] = 1
    #
    #     return lst

    def main_loop(self):
        self.touchoutside = 0

        # Reset all tracked variables as session needs to be independent of the previous session:
        if self.current_trial == 0:
            # session counters
            # stimulus scheduling
            self.stim = [0, 4]
            # self.block_size = 40
            self.forced_choice_next_trial = 0

        print('')
        print('Stimulus Trial Counter', self.stim_trial_counter)
        print('block_size', self.block_size)

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
            self.task_number = 3
            self.tired = True
            message = f"Stage moved forward to {self.pair} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except Exception as e:
                print(f"Telegram message not sent. Error: {e}")

        if self.stage_backward_change == 1:
            self.stage_backward_change = 0
            message = f"URGENT Stage moved backward to {self.pair} for {self.subject} in {self.task}"
            try:
                telegram_bot.alarm_finish_session(message, self.subject)
            except:
                print("Telegram message not sent")

        # Probe Generation:
        if self.stim_trial_counter % self.block_size == 0:  # Re-randomize every 75 trials
            # If not the first block_size, pass the last stimulus of the previous block_size to avoid repetition
            last_trial = self.last_stim_trial if len(self.stim_trials) > 0 else None
            self.stim_trials = self.generate_random_trials(last_trial)

            # print(f"Stimulus trials after first attempt: {self.stim_trials}")
            while self.stim_trials is None:
                # print("Retrying to generate stimulus trials...")
                self.stim_trials = self.generate_random_trials(last_trial)
                if self.stim_trials is None:
                    print("generate_random_trials returned None. Retrying...")
                else:
                    print(f"Successfully generated stimulus trials: {self.stim_trials}")
            self.stim_trial_counter = 0

            print(f"Successfully generated stimulus trials: {self.stim_trials}")
            self.unrewarded_list = self.partial_reinforcement_list(self.stim_trials,
                                                                   ratio=self.partial_reinforcement_ratio)
            self.unrewarded_list_planned = self.unrewarded_list.copy()
            print(f"Successfully generated unrewarded trials: {self.unrewarded_list}")

            # Reset carry when a new block starts
            self.pr_carry_pending = 0
            self.pr_carry_tone = ""
            self.pr_carry_deadline = -1

        # --- session-local logic for first two trials in this session ---
        if self.current_trial == 0:
            # first trial in this session: random left/right
            candidate = random.choice(self.stim)  # 0 or 4
            self.session_first_stim = candidate
        elif self.current_trial == 1:
            # second trial in this session: forced opposite of first
            if self.session_first_stim == 0:
                candidate = 4
            else:
                candidate = 0
        else:
            # from 3rd trial onwards: normal block / bias-breaking logic
            candidate = self.stim_trials[self.stim_trial_counter]

        # --- global guard: never allow 3 same-side stimuli in a row across sessions ---
        if len(self.last_two_stim) >= 2 and candidate == self.last_two_stim[-1] == self.last_two_stim[-2]:
            # flip side
            candidate = 0 if candidate == 4 else 4

        if self.forced_choice_next_trial == 0:
            self.stim_trial = candidate
        else:
            self.stim_trial = self.forced_choice_probe

        # keep stimulus schedule aligned with actual delivered probe
        if self.forced_choice_next_trial == 0 and 0 <= self.stim_trial_counter < len(self.stim_trials):
            self.stim_trials[self.stim_trial_counter] = self.stim_trial

        # get sides from existing mapping, but override shape per subject/group/pair
        (high_side), (low_side) = self.derive_high_low(int(self.group), int(self.pair))
        self.shape = self.shape_for_pair(self.subject, int(self.pair))

        # pick correct side based on probe
        if self.stim_trial == 4:  # HIGH probe
            self.side = high_side
            self.tone_played = "High"
        elif self.stim_trial == 0:  # LOW probe
            self.side = low_side
            self.tone_played = "Low"
        else:
            raise ValueError(f"Unexpected probe (0 or 4 expected): {self.stim_trial}")

        # shape is fixed by pair → same for both sides
        self.side_incorrect = "right" if self.side == "left" else "left"

        # x positions
        if self.side == "left":
            self.x_correcth, self.x_incorrecth = self.x_correcth_pos[0], self.x_correcth_pos[1]
        else:
            self.x_correcth, self.x_incorrecth = self.x_correcth_pos[1], self.x_correcth_pos[0]

        # In forced-choice trials, disable the incorrect side completely
        if self.forced_choice_next_trial == 1:
            self.x_incorrecth = None

        # --- Per-trial reward size from Table 1 (ONLY valve_factor_c) ---
        # Large reward = 1.4, Small reward = 0.7
        mapping = self.table1[int(self.group)][int(self.pair)]
        hr_tone = mapping['hr_tone']  # 'high' or 'low'
        is_high_probe = (self.stim_trial == 4)  # 4 = high, 0 = low

        large_now = (is_high_probe and hr_tone == 'high') or ((not is_high_probe) and hr_tone == 'low')
        self.valve_factor_c = 1.4 if large_now else 0.7

        # --- Partial reinforcement: propose skip (applied ONLY if correct) ---
        self.skip_proposed = 0
        self.unrewarded_tone = None

        if self.partial_reinforcement_active and self.forced_choice_next_trial == 0:
            # Window size from ratio (e.g., 0.1→10, 0.2→5)
            block = max(1, int(round(1.0 / float(self.partial_reinforcement_ratio))))
            i = self.stim_trial_counter
            w = i // block
            tone_now = 'high' if (self.stim_trial == 4) else 'low'

            # A) planned skip at this index?
            planned_skip = (0 <= i < len(self.unrewarded_list)) and (self.unrewarded_list[i] == 1)

            # B) tone-carry skip? (we owe an unreward of a specific tone)
            carry_ok = 0
            if self.pr_carry_pending:
                # allow if tone matches, OR we've passed the deadline (must pay to keep 1-in-N correct)
                if (tone_now == self.pr_carry_tone) or (i >= self.pr_carry_deadline):
                    carry_ok = 1

            # Propose skip if either applies
            if planned_skip or carry_ok:
                self.skip_proposed = 1
                self.valve_factor_c = 0  # only matters if this trial ends up CORRECT

        print(
            f"Group={self.group} Pair={self.pair}  Probe={self.stim_trial} Tone Played={self.tone_played} "
            f" Shape={self.shape} "
            f"valve_factor_c={self.valve_factor_c} "
            f"unrewarded_trial={self.unrewarded_trial} "
        )
        print(f"Correct_side={self.side}")
        print(f"forced_choice_next_trial={self.forced_choice_next_trial}")
        print(f"forced_choice_probe={self.forced_choice_probe}")

        ############ STATE MACHINE ################
        # First trial:
        if self.task_number == 1:
            if self.current_trial == 0:
                self.sma.add_state(
                    state_name='Start_task',
                    state_timer=0,
                    state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                    output_actions=[(Bpod.OutputChannels.SoftCode, 234)])  # Draws black screen
                # Starts task and displays stimuli instanly

                self.sma.add_state(
                    state_name='Real_start',
                    state_timer=self.valve_time * 0.5,
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
                state_change_conditions={Bpod.Events.Port4In: 'Fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 234)])  # Draws black screen

            self.sma.add_state(
                state_name='Fixation',
                state_timer=2,
                state_change_conditions={Bpod.Events.Tup: 'Response_window'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 230)])  # PLayes sound and displays stims

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
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.SoftCode, 220)])
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
                state_change_conditions={Bpod.Events.Tup: 'Punish_image_display'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 232)])
            # Goes back to response window in case of touch outside the two jar areas

            self.sma.add_state(
                state_name='Punish',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Punish_image_display'},
                output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 6),
                                (Bpod.OutputChannels.SoftCode, 232)])
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
                output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 40)])
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
            print("Task 1 ended because training completed. Task is now 2 so will move to Pr in next session.")
            self.trial_length = 0.1
            self.trial_result = None
            self.last_stim_trial = 0
            self.x_correcth = None
            self.x_incorrecth = None
            self.response_x = None
            self.response_y = None

    def after_trial(self):
        if self.task_number == 1:

            ##### COUNT MISSES:
            if self.current_trial_states['No_Touch'][0][0] > 0:  # misses modify the acc
                self.trial_result = 'miss'

            ##### COUNT PUNISH
            elif self.current_trial_states['Punish'][0][0] > 0:
                self.trial_result = 'incorrect'
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.block_valid_count += 1
                    self.success = 0
                    self.block_trial_counter += 1
                    self.total_trials += 1
                    self.stim_trial_counter += 1
                self.forced_choice_next_trial = 1
                self.forced_choice_probe = self.stim_trial

            ##### COUNT CORRECTS FIRST POKE
            elif self.current_trial_states['Correct'][0][0] > 0:
                self.trial_result = 'correct'
                self.reward_drunk += self.valve_reward * self.valve_factor_c
                self.reward = self.valve_reward * self.valve_factor_c
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.stim_trial_counter += 1
                    self.correct_count += 1
                    # print('Correct_count: ', self.correct_count)
                    self.block_correct_count += 1
                    self.block_valid_count += 1
                    self.block_trial_counter += 1
                    self.success = 1
                    self.total_trials += 1
                self.forced_choice_next_trial = 0
                self.forced_choice_probe = None

            # ##### COUNT Touches outside the shape areas :
            elif self.current_trial_states['Touch_Outside'][0][0] > 0:
                self.trial_result = 'incorrect'
                self.touchoutside = 1
                if self.forced_choice_next_trial == 0:
                    self.valid_counter += 1
                    self.block_valid_count += 1
                    self.success = 0
                    self.block_trial_counter += 1
                    self.total_trials += 1
                    self.stim_trial_counter += 1
                self.forced_choice_next_trial = 1
                self.forced_choice_probe = self.stim_trial

            # End-trial calculations
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

            # Check accuracy for every block of 40 trials
            self.block_accuracy = (
                self.block_correct_count / self.block_valid_count if self.block_valid_count > 0 else 0)
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

            self.last_stim_trial = self.stim_trial

            # Update short history used to prevent triples
            self.last_two_stim.append(self.stim_trial)
            if len(self.last_two_stim) > 2:
                self.last_two_stim.pop(0)

            # ---- Partial reinforcement bookkeeping (AFTER trial outcome) ----
            if self.partial_reinforcement_active:
                block = max(1, int(round(1.0 / float(self.partial_reinforcement_ratio))))

                # Use current index for miss/no-touch; (counter-1) for correct/incorrect
                if self.trial_result in ('correct', 'incorrect'):
                    i = self.stim_trial_counter - 1
                else:
                    i = self.stim_trial_counter

                # Clamp just in case
                i = max(0, min(i, len(self.stim_trials) - 1))

                w = i // block
                was_correct = (self.trial_result == 'correct')
                tone_this = 'high' if (self.stim_trials[i] == 4) else 'low'

                if was_correct and self.skip_proposed:
                    if 0 <= i < len(self.unrewarded_list) and self.unrewarded_list[i] == 1:
                        self.unrewarded_list[i] = 0
                    self.pr_carry_pending = 0
                    self.pr_carry_tone = ""
                    self.unrewarded_trial = 1
                    self.unrewarded_tone = tone_this

                elif (not was_correct) and self.skip_proposed:
                    if 0 <= i < len(self.unrewarded_list) and self.unrewarded_list[i] == 1:
                        self.unrewarded_list[i] = 0
                    self.pr_carry_pending = 1
                    self.pr_carry_tone = tone_this
                    end_next = min(len(self.stim_trials) - 1, ((w + 1 + self.pr_carry_max_windows) * block) - 1)
                    self.pr_carry_deadline = end_next
                    self.unrewarded_trial = 0

                else:
                    self.unrewarded_trial = 0

        else:
            print("Task 1 ended because training completed. Task is now 2 so will move to Pr in next session.")

        ############ REGISTER VALUES ################
        # Task-related
        self.register_value('duration_max', self.duration_max)
        self.register_value('duration_min', self.duration_min)
        self.register_value('duration_tired', self.duration_tired)
        self.register_value('tired', self.tired)
        self.register_value('task_number', self.task_number)
        self.register_value('response_duration', self.response_duration)

        # Pumps
        self.register_value('valve_time', self.valve_time)
        self.register_value('valve_reward', self.valve_reward)
        self.register_value('valve_factor_c', self.valve_factor_c)

        # Counters
        self.register_value('valid_counter', self.valid_counter)
        self.register_value('tired_counter', self.tired_counter)
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('reward', self.reward)
        self.register_value('correct_count', self.correct_count)
        self.register_value('success', self.success)

        # Stimulus-related
        self.register_value('stim', self.stim)
        self.register_value('x_correcth_pos', self.x_correcth_pos)
        self.register_value('y_correcth', self.y_correcth)
        self.register_value('width', self.width)
        self.register_value('height', self.height)

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
        self.register_value('touchoutside', self.touchoutside)

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

        self.register_value('last_forward_stage', self.last_forward_stage)
        self.register_value('last_backward_stage', self.last_backward_stage)

        self.register_value('prev_block_accuracy', self.prev_block_accuracy)
        self.register_value('last_block_accuracy', self.last_block_accuracy)

        self.register_value('session_first_stim', self.session_first_stim)
        self.register_value('forced_choice_actual_trial', self.forced_choice_actual_trial)
        self.register_value('forced_choice_next_trial', self.forced_choice_next_trial)
        self.register_value('forced_choice_probe', self.forced_choice_probe)

        self.register_value('last_two_stim', self.last_two_stim)
        self.register_value('consecutive_good_blocks', self.consecutive_good_blocks)
        self.register_value('consecutive_good_blocks_criteria', self.consecutive_good_blocks_criteria)

        # Partial Reinforcement:
        self.register_value('partial_reinforcement_active', self.partial_reinforcement_active)
        self.register_value('partial_reinforcement_ratio', self.partial_reinforcement_ratio)
        self.register_value('unrewarded_list', self.unrewarded_list)
        self.register_value('unrewarded_trial', self.unrewarded_trial)
        self.register_value('unrewarded_tone', self.unrewarded_tone)
        self.register_value('tone_played', self.tone_played)
        self.register_value('unrewarded_list_planned', self.unrewarded_list_planned)

        self.register_value('pr_carry_pending', self.pr_carry_pending)
        self.register_value('pr_carry_tone', self.pr_carry_tone)
        self.register_value('pr_carry_deadline', self.pr_carry_deadline)
        self.register_value('pr_carry_max_windows', self.pr_carry_max_windows)
