from academy.task_collection import Task
from pybpodapi.protocol import Bpod
from academy.utils import utils


class A_Test_PurgeValve(Task):

    def __init__(self):
        super().__init__()

        self.info = """
        Purge valve using calibrated water delivery time.
        """

    def init_variables(self):
        self.trials_max = 100

        #Load last calibration values for port 1
        self.valve_time = utils.water_calibration.read_last_value('port', 1).pulse_duration
        self.valve_reward = utils.water_calibration.read_last_value('port', 1).water
        self.valve_factor_c = 1 # 300ul for 1 trial.

        self.delivered_ul = 0
        self.delivered_ml = 0

        # Accumulate total across trials
        self.total_delivered_ul = 0
        self.total_delivered_ml = 0

    def configure_gui(self):
        self.gui_input = ['trials_max']

    def main_loop(self):
        self.sma.add_state(
            state_name='Valve_1',
            state_timer=self.valve_time * self.valve_factor_c,
            state_change_conditions={Bpod.Events.Tup: 'exit'},
            output_actions=[(Bpod.OutputChannels.Valve, 1), (Bpod.OutputChannels.LED, 1)])

    def after_trial(self):
        # Volume delivered in this trial
        self.delivered_ul = self.valve_reward * self.valve_factor_c
        self.delivered_ml = self.delivered_ul / 1000

        # Accumulate total across trials
        self.total_delivered_ul += self.delivered_ul
        self.total_delivered_ml = self.total_delivered_ul / 1000

        # Log to console
        print(f"Trial {self.current_trial + 1}/{self.trials_max}")
        print(f"Delivered this trial: {self.delivered_ul:.2f} µL ({self.delivered_ml:.3f} mL)")
        print(f"Total delivered so far: {self.total_delivered_ul:.2f} µL ({self.total_delivered_ml:.3f} mL)")


        # If this was the last trial, print final summary
        if (self.current_trial + 1) >= self.trials_max:
            print("\n=== Purge complete ===")
            print(f"Total delivered: {self.total_delivered_ul:.2f} µL ({self.total_delivered_ml:.3f} mL)")
            print("======================")

        # Optional: store the values for later access in your task logs
        self.register_value('delivered_ul', self.delivered_ul)
        self.register_value('delivered_ml', self.delivered_ml)
        self.register_value('total_delivered_ml', self.total_delivered_ml)
        self.register_value('total_delivered_ul', self.total_delivered_ul)
