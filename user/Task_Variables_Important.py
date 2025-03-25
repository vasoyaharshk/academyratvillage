#Tracked Variables:
#Needed in Each Task:
self.stage = 0  # Current stage within the task
self.substage = 0  # Current substage within the stage
self.substage_bias = 0  # Side bias stage for substage behavior
self.wait_seconds = 0  # Time to wait before stimulus or response (in seconds)
self.task_number = 0  # Each task has a unique number. See RV script guide.

#Working Memory only:
self.stim_dur_ds = 0  # Stimulus duration for short duration for working memory
self.stim_dur_dm = 0  # Stimulus duration for medium duration for working memory
self.stim_dur_dl = 0  # Stimulus duration for long duration for working memory
self.choice = 0  # Choices subjects get in the working memory (for us its the same. Variable from IDIBAPs)

#Weber's Law Pre and Post Test:
self.block = 0  # Current block number for trials
self.conditions = []  # List of all Weber's law conditions
self.completed_conditions = []  # List of completed conditions
self.current_condition = 0  # Current condition for the trial
self.repetition = 0  # Number of repetitions for the Weber's Law
self.current_repetition = 0  # Current repetition number for the trial
self.trial_counter = 0  # Total number of trials run in the current block

#Weber's Law Training:
self.ror = 0  # Ratio of Ratios (ROR) for Weber's Law Training
self.completed_ror = []  # List of completed ROR levels
self.current_ror = 0  # Current ROR of the trial
self.trial_counter_ror = 0  # Counter for trials under current ROR
self.last_condition_trial = 0  #Condition of the last trial of the previous block. Used to ensure first trial of next block is different

#Needed to create blocks of 40 trials for criterion to be assessed on:
self.block_size = 0  # The number of trials in a block
self.block_trial_counter = 0  # Trial count within the current block
self.block_accuracy = 0.0  # Accuracy in the current block
self.block_number = 0  # Sequential block number
self.ror_change = 0  # If it is 1, ROR will change on the next trial.
self.block_change = 0  # If it is 1, a new block will start on the next trial
self.total_trials = 0  # Total trials across the task.
self.block_correct_count = 0  # Number of correct responses in the block
self.block_valid_count = 0  # Number of valid (non-missed) trials in the block
self.condition_trial_counter = 0  # Number of trials under the current condition
self.last_forward_stage = 0  # The stage moved forward from after a forward change
self.last_backward_stage = 0  # The stage moved backward to after the last backward change
self.moved_back_counter = 0  # Counter for how many times the subject moved back a stage
self.stage_forward_change = 0  # Whether stage move forward on the next trial
self.stage_backward_change = 0  # Whether stage move backward on the next trial
#Left Right Function Randomisation variables:
self.stim_trial = 0  # The function number of the correct stimulus in the current trial. This designates trial type, e.g. from Discrim. C: left is correct, big jar is correct, spacer in correct
self.stim_trials = []  # List of correct stimulus function randomised.
self.stim_trial_counter = 0  #It counts the number of trials within a randomization block. Doesnt change when Bias breaking is active.
self.last_stim_trial = 0  #the function of the last trial of the previous block. Used to ensure first trial of next block is different



#Untracked Variables:
self.duration_max = 3000
self.duration_min = 2100
self.duration_tired = 1800
self.trials_tired = 5 # if they do 5 trials of long duration, the door will open after 30 mins rather than 35
self.tired = False
self.response_duration = 60
self.image_display = 3        #Number of seconds the image will display after correct and incorrect

# pumps
self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions
self.valve_factor_c = 2.0  # Normal water delivery must be a multiple of 25ul. 2.0 is 2 x 25 = 50uL. E.g., if you set it to 1.8, this would be 1.8 x 25 = 45uL
#self.valve_factor_i = 0.6  # Water delivery for incorrects/punish - only if want to give water if they do an incorrect trial (only used for scripts that allow correction)

# counters for trials:
self.valid_counter = 0
self.tired_counter = 0
self.touch_outside = 0
self.reward_drunk = 0
#self.running_window = 10  # This is the number of trials the accuracy is measured by. It will take accuracy for every 10 trials.
self.accwindow = [0]
self.correct_count = 0
self.accuracy = 0

# Image output stims:
self.stim = [0]  # defines if correct side is left or right

# Correcth location and size:
self.x_correcth_pos = [95, 281]  #Screen Coordinates for left and right for
self.y_correcth = 110
self.width = 160    # Stimulus width in mm. Original size for peg is 120mm.
self.height = 235   # Stimulus height in mm. Original size for jar is 110mm.

#Bias breaking variables:
self.bias_breaking = 0        #If subject chooses same side for 5 trials in a row, bias breaking becomes active
self.response_x_array = []      #Stores responses for x till 3 values
self.sameside_counter = 0       #Counts number of times on same side
self.sameside = None             # To track which side is being triggered
self.side_bias_trigger = 5      #After how many trials does side_bias trigger
self.side_bias_trigger_acc = 0.8
self.status = None              #Stores the Touch_outside condition
self.biased_consecutive_corrects_counter = 0       #This is the counter for counting the number of corrects when bias breaking is active
self.biased_consecutive_corrects = 3                ##This is the number of corrrects the rat needs to do to end bias breaking

self.bias_accuracy_trials = []
self.bias_accuracy = 0
self.accuracy_criteria = 0.80  # move forward criteria. 80% success on block_size(32/40 trials correct)
self.trial_end_criteria = 320 # Move back criteria. Badly named - this is task end criteria.
self.max_move_backs = 5 # number of times they can be moved back (i.e., they've done 320 trials 5 times) before we review
self.success = 0  # tracks if trial is correct or incorrect (1 or 0)
