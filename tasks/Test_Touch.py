from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings

class Test_Touch(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        """

    def init_variables(self):
        # general
        self.duration_min = 1800 # 30 mins
        self.duration_max = 2100 # 40 mins
        self.stage = 0
        self.substage = 0
        self.response_duration = 20
        self.stim_duration = self.response_duration
        self.trials_max = 10

        # screen details
        self.x = [60, 200, 340]  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30
        self.correct_th = settings.WIN_SIZE[0] * 2  # full screen
        self.repoke_th = settings.WIN_SIZE[0] * 2   # full screen
        self.contrast= 2 #0 black, 1 gray, 2 white. Default 20%


        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 1.5
        self.valve_factor_i = 0.5

        # counters
        self.reward_drunk = 0


    def configure_gui(self): # Variables that appear in the GUI
        pass

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))


        self.sma.add_state(
            state_name='Start_task',
            state_timer=2,
            state_change_conditions={Bpod.Events.Tup: 'Fixation'},
            output_actions=[])

        self.sma.add_state(
            state_name='Fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Response_window'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 3)])
            # show 3 stimuli when crossing end of corridor

        self.sma.add_state(
            state_name='Response_window',
            state_timer=self.response_duration+10,
            state_change_conditions={'SoftCode1': 'Correct_first', 'SoftCode3': 'Miss', Bpod.Events.Tup: 'Miss'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 4)])

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 11)])

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=1,
            state_change_conditions={Bpod.Events.Tup: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 12)])

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=3,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])


    def after_trial(self):

        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0: # Missed trial
            self.register_value('trial_result', 'miss')
            self.reward_drunk += self.valve_reward * self.valve_factor_i
            print("_______ MISSED ________")
        else:
            self.register_value('trial_result', 'correct_first') # Correct trial
            self.reward_drunk += self.valve_reward * self.valve_factor_c

        print('Resp coord:' + str(self.response_x))

        # Relevant prints
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
