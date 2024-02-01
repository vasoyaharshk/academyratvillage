# IMPORTS: The 2 first imports (Task and BPod) are necessary for all tasks
#
#
# CLASS DEFINITION: Use the same name for the class and the file
#                   For example the class: Example(Task) is inside the file Example.py
#
#
# CLASS STRUCTURE: def __init__(self): Initialization of the task
#                                      It is done for all the task when academy is launched
#                                      NECESSARY
#
#                  def init_variables(self): To init the values of the variables each time the task is run
#                                            OPTIONAL
#
#                  def configure_gui(self): To select which values are created in the gui when the tasks is directly run
#                                           and read those values before each run of the task
#                                           OPTIONAL
#
#                  def main_loop(self): To change the values of the variables before running each trial and
#                                       then add all the states of each trial
#                                       NECESSARY
#
#                  def after_trial(self): To calculate values that depend on the performace of the trial
#                                         OPTIONAL
#
#
# VARIABLES: Add all the relevant variables for the task in the __init__ function
#            All the variables created in __init__ will be stored in the csv trial by trial
#            There are 10 extra pre-created variables for every task:
#
#                  self.sma: The state machine, where you add the states
#
#                  self.trials_min: The minimum number of trials
#                                   The door will not open if trials performed < trials_min
#                                   Default value in settings.py
#
#                  self.trials_max: The maximum number of trials.
#                                   If this value is reached the task will end
#                                   Default value in settings.py
#
#                  self.duration_min: The minimum duration of the task in seconds
#                                     The door will not open if real duration < duration_min
#                                     Default value in settings.py
#
#                  self.duration_max: The maximum duration of the task in seconds
#                                     If this value is reached the task will end
#                                     Default in settings.py
#
#                  self.tired = when is made True (usually in after trial) the task ends in the next state
#                               Default is False
#
#                  self.stage: To set the value of other variables depending on which stage you are
#                              Default value in settings.py
#
#                  self.gui_input: List with the names of the variables which values can be modified in the gui
#                                  when the task is run manually
#
#                  self.gui_input: List with the names of the variables that return values in the gui
#                                  when the task is run manually (for callibration tasks)
#
#                  self.current_trial: The number of trial the subject is, starting at 0
#
#                  self.current_trial_states: A dictionary of states and times for each trial
#                         keys: states.
#                         values: a list of (start, end) for each occurence of the state in the current trial.
#                                 if the state does not occur in the current trial, value is [(nan, nan)].
#
#                  self.response: Is generated each trial by the touch plugin that reads the touches in the screen
#
#


from academy.task_collection import Task
from pybpodapi.protocol import Bpod


class _ExampleTaskWithDocumentation(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        This tasks only lights the first led for time1, and then waits for time2 before going to the next trial.
        """

    def init_variables(self):
        self.stage = 0
        self.trials_max = 20

        self.time_on = 0.2
        self.time_off = 0.2
        self.runs = []

    def configure_gui(self):
        self.gui_input = ['stage', 'trials_max']

    def main_loop(self):
        if self.stage == 1:
            self.time_on = 0.2
            self.time_off = 0.2
        else:
            self.time_on = 0.2
            self.time_off = 0.2

        self.sma.set_global_timer(timer_id=1, timer_duration=self.time_on)

        self.sma.add_state(
            state_name='Light_on',
            state_timer=self.time_on,
            state_change_conditions={Bpod.Events.GlobalTimer1_End: 'Light_off'},
            output_actions=[(Bpod.OutputChannels.GlobalTimerTrig, 1), (Bpod.OutputChannels.PWM1, 100)]
        )

        self.sma.add_state(
            state_name='Light_off',
            state_timer=self.time_off,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[]
        )

    def after_trial(self):
        self.runs.append(self.current_trial)
        self.register_value('time_on', self.time_on)
        self.register_value('time_off', self.time_off)
        self.register_value('runs', self.runs[self.current_trial])
