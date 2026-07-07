from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils
from academy import telegram_bot

class Habituation_LickTeaching(Task):

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
        self.duration_max = 86401  #24 hours
        self.duration_min = 86400  #24 hours
        self.stage = 0
        self.substage = 0

        # pumps
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 3

        self.reward_interval = 3600  # 1 hour
        self.max_rewards = 24
        self.trial_counter = 0


    def configure_gui(self): # Variables that appear in the GUI
        pass

    def main_loop(self):
        print('')
        print('Trial: ' + str(self.current_trial))
        print('Trial Counter: ' + str(self.trial_counter))

        if self.trial_counter < self.max_rewards:
            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'Automatic_reward'},
                output_actions=[])

            self.sma.add_state(
                state_name='Automatic_reward',
                state_timer=self.valve_time * self.valve_factor_c,
                state_change_conditions={Bpod.Events.Tup: 'Wait_one_hour'},
                output_actions=[(Bpod.OutputChannels.Valve, 1)])

            self.sma.add_state(
                state_name='Wait_one_hour',
                state_timer=self.reward_interval,
                state_change_conditions={Bpod.Events.Tup: 'exit'},
                output_actions=[])
        else:
            print("Task has Ended.")
            self.task_end = True

            self.sma.add_state(
                state_name='Start_task',
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: 'exit'},
                output_actions=[])

    def after_trial(self):
        if self.trial_counter < self.max_rewards:
            self.trial_counter += 1

            self.register_value('trial_result', 'automatic_water')
            self.register_value('response_x', '')
            self.register_value('response_y', '')

            print('Finished water delivery number: ' + str(self.trial_counter))

            if self.trial_counter >= self.max_rewards:
                print("24 hourly water deliveries completed.")
                self.task_end = True