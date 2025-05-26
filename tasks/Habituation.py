from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils


class Habituation(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        ########   TASK INFO   ########
        Habituation to empty behavioral box with lights ON.
    
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
        self.duration_min = 600
        self.duration_max = 660
        self.tired = False
        self.stage = 0
        self.substage = 0

        # pumps
        self.reward_drunk = 100  # deliver 100 ul water initially
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_time = self.reward_drunk * self.valve_time / self.valve_reward

    def configure_gui(self): # Variables that appear in the GUI
        pass

    def main_loop(self):
        if self.current_trial == 0:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=self.valve_time,
                state_change_conditions={Bpod.Events.Tup: 'Start_task2'},
                output_actions=[(Bpod.OutputChannels.Valve, 1),
                                (Bpod.OutputChannels.PWM6, 5)])
                # deliver 100 ul reward, and global LED ON

            self.sma.add_state(
                state_name='Start_task2',
                state_timer=0,
                state_change_conditions={Bpod.Events.Port2In: 'Real_start'},
                output_actions=[(Bpod.OutputChannels.PWM6, 5)])

            self.sma.add_state(
                state_name='Real_start',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Habituation'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 20), (Bpod.OutputChannels.PWM6, 5)])
                # close corridor door 2 when subject enters to behavioral box

        self.sma.add_state(
            state_name='Habituation',
            state_timer=self.duration_min/4,
            state_change_conditions={Bpod.Events.Tup: 'Exit'},
            output_actions=[(Bpod.OutputChannels.PWM6, 5)])

        self.sma.add_state(
            state_name='Exit',
            state_timer=0,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.PWM6, 5)])


    def after_trial(self):
        self.register_value('reward_drunk', self.reward_drunk)

