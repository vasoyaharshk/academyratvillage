from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from user import settings

class TouchTeaching(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Mice learn to touch the screen during the response window to obtain the reward.
        Animals crossing the end of the corridor trigger the stimulus presentation in all holes and response window onset. 
        Screen touches during response window deliver reward.
        Stimulus low contrast to not scare animals

        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - BUZZER: valve (16kHz): correct
        Port 3 - PHOTOGATES 4: Photogates end of corridor
        Port 4 - PHOTOGATES 0: Photogates next to lickport & Global LED
        """

    def init_variables(self):
        # general
        self.duration_min = 1800 # 30 mins
        self.duration_max = 2100 # 40 mins
        self.stage = 0
        self.substage = 0
        self.response_duration = 120 # 2 min
        self.stim_duration = self.response_duration

        # screen details
        self.x = [60, 200, 340]  # screen width is 401mmm
        self.y = 125  # screen height is 250mmm
        self.width = 30
        self.correct_th = settings.WIN_SIZE[0] * 2  # full screen
        self.repoke_th = settings.WIN_SIZE[0] * 2   # full screen
        self.contrast= 0.4 #0 black, 1 gray, 2 white. Default 20%


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

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port4In: 'Real_start'},
                output_actions=[])

            self.sma.add_state(
                state_name='Real_start',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20)])
                # close corridor door 2 when subject enter to the behav box

        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Wait_for_fixation'},
                output_actions=[])

        self.sma.add_state(
            state_name='Wait_for_fixation',
            state_timer=0,
            state_change_conditions={Bpod.Events.Port3In: 'Fixation'},
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
            state_change_conditions={Bpod.Events.Port1In: 'Correct_first_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.Valve, 2),
                            (Bpod.OutputChannels.SoftCode, 11)])
            # waterLED and RWsound remain ON until poke

        self.sma.add_state(
            state_name='Correct_first_reward',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Miss_reward'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.LED, 4), (Bpod.OutputChannels.SoftCode, 12)])
            # waterLED ON, global LED ON

        self.sma.add_state(
            state_name='Miss_reward',
            state_timer=self.valve_time * self.valve_factor_i,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.SoftCode, 15)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[])


    def after_trial(self):

        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0: # Missed trial
            self.register_value('trial_result', 'miss')
            self.reward_drunk += self.valve_reward * self.valve_factor_i
        else:
            self.register_value('trial_result', 'correct_first') # Correct trial
            self.reward_drunk += self.valve_reward * self.valve_factor_c

        # Relevant prints
        self.register_value('reward_drunk', self.reward_drunk)
        self.register_value('response_x', self.response_x)
        self.register_value('response_y', self.response_y)
