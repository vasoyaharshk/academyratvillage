# ==============================
# Tracked Variables
# ==============================
#Needed in Each Task:
self.stage = 0  # Current stage within the task
self.substage = 0  # Current substage within the stage
self.substage_bias = 0  # Side bias stage for substage behavior
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
self.condition_trial_counter = 0  # Counter for randomising conditions
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
self.max_move_backs = 0
self.stage_sequence = []

#Only defined in select_task:
self.wait_seconds = 0  # Time between two sessions.
# ==============================
# Untracked Variables
# ==============================
#Task specific:
self.accuracy_criteria = 0.80  # move forward criteria. 80% success on block_size(32/40 trials correct)
self.trial_end_criteria = 320 # Move back criteria. Badly named - this is task end criteria.
self.max_move_backs = 5 # number of times they can be moved back (i.e., they've done 320 trials 5 times) before we review

#Trial Specific:
self.duration_max = 3000  #Maximum duration of the task. 50 mins
self.duration_min = 2100  #Minimum duration of the task. 35 mins.
self.duration_tired = 1800  #Duration for the door to open (30 mins) if the animal is inactive. Less than 5 trials.
self.trials_tired = 5  # if they do 5 trials of long duration (more than 45 seconds), the door will open after 30 mins rather than 35
self.tired = False  #The door 2 opens whenever this is true. Used to end the task.
self.response_duration = 60  #The response time after the last photogate has been crossed in secs.
self.image_display = 3        #Number of seconds the image will display after correct and incorrect

#Pump:
self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration  #The duration the water valve needs to be open for. Takes the value from the water_calibration.csv
self.valve_reward = utils.water_calibration.read_last_value('port', 1).water  # 25ul per trial normal conditions. Takes the value from water_caliberation.csv
self.valve_factor_c = 2.0  # Normal water delivery must be a multiple of 25ul. 2.0 is 2 x 25 = 50uL. E.g., if you set it to 1.8, this would be 1.8 x 25 = 45uL
self.valve_factor_i = 0.6  # Water delivery for incorrects/punish - only if want to give water if they do an incorrect trial (only used for scripts that allow correction)

# Counters for trials:
self.valid_counter = 0  #Counter for valid counts in a session
self.tired_counter = 0  #Counter for longer duration trials (more than 45 secs) in a session
self.reward_drunk = 0   #Amount of water drunk in the session
self.correct_count = 0  #Counter for correct counts in a session
self.accuracy = 0   #Accuracy of the session
self.success = 0  # tracks if trial is correct or incorrect (1 or 0)
self.status = None  #Stores the Touch_outside condition

# Image output stims:
self.stim = [0]  # Lists which defines both the functions for left and right.

# Correcth location and size:
self.x_correcth_pos = [95, 281] #x-axis Coordinates for left and right for Jars
self.y_correcth = 110   #y-axis Coordinates for left and right for Jars
self.width = 160    # Stimulus width in mm. Original size for jar is 120mm.
self.height = 235   # Stimulus height in mm. Original size for jar is 110mm.
self.image_path_function = None #Full Path for the image displayed
self.image_displayed = None #The image which is displayed
self.image_directory = None #The directory of the image displayed
#Not necesarry to have in initialisation but important when registering at the end of the trial
self.x_correcth = 0     #Correcth coordinate
self.x_incorrecth = 0   #Incorrecth coordinate
self.response_x = 0 #Coordinate of the response on x axis
self.response_y = 0 #Coordinate of the response on y axis
self.trial_length = 0   #length of the trial
self.trial_result = None   #Result of the trial, correct, incorrect or miss

#Bias breaking variables:
self.bias_breaking = 0  #If subject chooses same side for 5 trials in a row, bias breaking becomes 1
self.response_x_array = []  #Stores responses for x till 5 values
self.sameside_counter = 0   #Counts number of times on same side
self.sameside = None    # To track which side is being triggered for bias breaking
self.side_bias_trigger = 5  #After how many trials does side_bias trigger
self.side_bias_trigger_acc = 0.8    #Side_bias triggers if accuracy is below this for the last 5 trials
self.biased_consecutive_corrects_counter = 0    #This is the counter for counting the number of corrects when bias breaking is active
self.biased_consecutive_corrects = 3    #This is the number of corrects the rat needs to do to end bias breaking
self.bias_accuracy_trials = []  #List that holds the last five success or failures.
self.bias_accuracy = 0  #Accuracy of the last five trials.

# ===============================================
# Untracked Variables used for Side Bias Scripts:
# ===============================================
self.probabilities = [] #The probability for left and right in extra training in the randomization block. [0.1, 0.9] would mean 10% on left and 90% on right.
self.probabilities_size = [] #The probability for left and right in the randomization block. [0.1, 0.9] would mean 10% on left and 90% on right.
self.probabilities_side  = [] #The probability for left and right in the randomization block. [0.1, 0.9] would mean 10% on left and 90% on right.
