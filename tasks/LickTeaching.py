from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils

class LickTeaching(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Reward association with lickport and correct sound.
        Starts with reward sound ON + water port LED ON + automatic delivery of water.
        Sound and LED stay on until poke or timeup. Global lights always ON.

        ########   PORTS INFO   ########
        Port 1 - WATER PORT: LED, photogates and pump
        Port 2 - BUZZER: valve (16kHz): correct
        Port 4 - PHOTOGATES 0: Photogates next to lickport & Global LED
        """

    def init_variables(self):
        # general
        self.duration_min = 1200  # 20 mins
        self.duration_max = 1260
        self.stage = 0
        self.substage = 0

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water

        # counters
        self.miss_acc_counter = 0
        self.reward_drunk = 0


    def configure_gui(self): # Variables that appear in the GUI
        pass

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))

        # FLOADING AVOIDANCE
        if self.miss_acc_counter > 5:
            floading = 'Wait_for_reward'
        else:
            floading = 'Automatic_reward'

        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port4In: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.PWM4, 5)])
                # global LED ON

            self.sma.add_state(
                state_name='Real_start',  # close corridor door 2 when subject enters to behavioral box
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Fixation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.PWM4, 5)])
        else:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Fixation'},
                output_actions=[(Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Fixation',  # if mouse licks during fixation, this is started again.
            state_timer=1,
            state_change_conditions={Bpod.Events.Port1In: 'Fixation_break', Bpod.Events.Tup: floading},
            output_actions=[(Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Fixation_break',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Fixation'},
            output_actions=[(Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Automatic_reward',
            state_timer=self.valve_time,
            state_change_conditions={Bpod.Events.Tup: 'Wait_for_reward'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.PWM4, 5),
                            (Bpod.OutputChannels.Valve, 2)])
            # Automatic water, lickportLED, and Reward sound

        self.sma.add_state(
            state_name='Wait_for_reward',
            state_timer=30,
            state_change_conditions={Bpod.Events.Tup: 'Miss', Bpod.Events.Port1In: 'Correct_first'},
            output_actions=[(Bpod.OutputChannels.PWM1, 5), (Bpod.OutputChannels.Valve, 2), (Bpod.OutputChannels.PWM4, 5)])
            # lickportLED and RWsound remain ON until poke o timeup

        self.sma.add_state(
            state_name='Correct_first',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 11), (Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Miss',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 12),(Bpod.OutputChannels.PWM4, 5)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=10,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.SoftCode, 15), (Bpod.OutputChannels.PWM4, 5)])
            # Wait 10 sec for the next automatic reward


    def after_trial(self):

        # Trial Counter
        if self.current_trial_states['Miss'][0][0] > 0: # Missed trial
            self.register_value('trial_result', 'miss')
            self.register_value('response_x', '')  # we add '' here to easily compare with other tasks
            self.register_value('response_y', '')  # we add '' here to easily compare with other tasks
            self.miss_acc_counter += 1
        else:
            self.register_value('trial_result', 'correct_first')  # Correct trial
            self.register_value('response_x', 0)  # we add a zero here to easily compare with other tasks
            self.register_value('response_y', 0)  # we add a zero here to easily compare with other tasks
            self.miss_acc_counter = 0

        if self.current_trial_states['Automatic_reward'][0][0] > 0:
            self.reward_drunk += self.valve_reward

        # Relevant prints
        self.register_value('reward_drunk', self.reward_drunk)

